import copy
from pathlib import Path

import pytest

from tools.retail_data.canonical import canonical_sha256
from tools.retail_data.gaap_contracts import (
    CONCEPT_IDS,
    CONTRACT_HASH,
    NormalizationError,
    attach_self_hash,
    canonical_decimal,
    load_synthetic_fixture,
    require_self_hash,
    scale_and_apply_polarity,
)
from tools.retail_data.gaap_mapping import build_mapping_policy, require_mapping_policy
from tools.retail_data.normalization import normalize_fixture

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "benchmarks/fixtures/m9_i5/synthetic-gaap-golden.json"


def _fixture() -> dict:
    return load_synthetic_fixture(FIXTURE)


def _rehash(value: dict) -> dict:
    value = copy.deepcopy(value)
    value["source_snapshot_hash"] = canonical_sha256(value["source_snapshot"])
    value["mapping_review"] = attach_self_hash(value["mapping_review"], "review_hash")
    value["facts"] = [attach_self_hash(fact, "source_fact_hash") for fact in value["facts"]]
    return attach_self_hash(value, "fixture_hash")


def test_golden_fixture_is_exact_synthetic_offline_and_contract_bound() -> None:
    fixture = _fixture()
    assert fixture["contract_hash"] == CONTRACT_HASH
    assert fixture["network_state"] == "denied"
    assert fixture["synthetic_only"] is True
    assert all(fact["synthetic"] is True for fact in fixture["facts"])
    require_self_hash(fixture, "fixture_hash")


def test_mapping_policy_is_exact_ordered_reviewed_and_hash_bound() -> None:
    fixture = _fixture()
    review = fixture["mapping_review"]
    policy = build_mapping_policy(
        taxonomy_version=fixture["taxonomy_version"],
        review_decision_ref=review["review_decision_ref"],
        review_decision_hash=review["review_hash"],
    )
    require_mapping_policy(policy)
    assert tuple(row["concept_id"] for row in policy["mappings"]) == CONCEPT_IDS
    assert all(row["mapping_status"] == "approved" for row in policy["mappings"])


def test_coherent_mapping_retyping_is_still_rejected() -> None:
    fixture = _fixture()
    review = fixture["mapping_review"]
    policy = build_mapping_policy(
        taxonomy_version="2026",
        review_decision_ref=review["review_decision_ref"],
        review_decision_hash=review["review_hash"],
    )
    policy["mappings"][0].update(
        {"kind": "shares", "allowed_unit": "shares", "period_type": "instant"}
    )
    policy = attach_self_hash(policy, "mapping_hash")
    with pytest.raises(NormalizationError, match="differs from lock"):
        require_mapping_policy(policy)


@pytest.mark.parametrize(
    "lexical",
    ["+1", "01", "-0", "1.0", "1e3", " 1", "1,000", "NaN", "Infinity", "0.0"],
)
def test_noncanonical_decimal_lexical_forms_are_rejected(lexical: str) -> None:
    with pytest.raises(NormalizationError) as error:
        canonical_decimal(lexical)
    assert error.value.code == "NORM-UNIT-SCALE"


def test_scale_and_polarity_are_exact_and_applied_once() -> None:
    assert scale_and_apply_polarity("12.5", 2, 1) == "1250"
    assert scale_and_apply_polarity("-60", 0, -1) == "60"
    assert scale_and_apply_polarity("0.21", 0, 1) == "0.21"


def test_golden_runtime_is_deterministic_complete_and_reference_closed() -> None:
    fixture = _fixture()
    first = normalize_fixture(fixture)
    second = normalize_fixture(copy.deepcopy(fixture))
    assert first == second
    result = first["normalization_result"]
    assert result["quality"] == {
        "status": "complete",
        "material_missing_concepts": [],
        "blocking_codes": [],
        "review_codes": [],
    }
    assert len(result["facts"]) == 13
    assert {fact["concept_id"] for fact in result["facts"]} == set(CONCEPT_IDS)
    assert result["mapping_hash"] == first["mapping"]["mapping_hash"]
    assert result["period_graph_hash"] == first["period_graph"]["period_graph_hash"]
    require_self_hash(result, "normalization_hash")


def test_every_reconciliation_family_is_explicit_and_exact() -> None:
    result = normalize_fixture(_fixture())["normalization_result"]
    assert [check["check_type"] for check in result["reconciliations"]] == [
        "balance-sheet",
        "cash-flow",
        "annual-quarterly",
        "unit-scale",
        "currency",
        "shares-split",
        "amendment",
        "duplicate-fact",
        "custom-tag",
        "fcff-completeness",
    ]
    for check in result["reconciliations"]:
        if check["applicability"] == "not_applicable":
            assert check["status"] == "not_applicable"
            assert check["difference_decimal"] is None
            assert check["tolerance_decimal"] == "0"
            assert check["fact_refs"] == []
            assert check["exclusion_reason_code"].startswith("NORM-")
        else:
            assert check["status"] == "passed"
            assert check["difference_decimal"] == "0"
            assert check["fact_refs"]


def test_capex_sign_is_mapping_driven_without_absolute_value_guessing() -> None:
    result = normalize_fixture(_fixture())["normalization_result"]
    capex = next(fact for fact in result["facts"] if fact["concept_id"] == "capital-expenditure")
    assert capex["value_decimal"] == "60"


def test_missing_concept_is_never_silently_filled() -> None:
    fixture = _fixture()
    fixture["facts"] = [
        fact for fact in fixture["facts"] if fact["local_name"] != "OperatingIncomeLoss"
    ]
    result = normalize_fixture(_rehash(fixture))["normalization_result"]
    assert result["quality"]["status"] == "unsupported"
    assert result["quality"]["material_missing_concepts"] == ["operating-income"]
    assert "NORM-MATERIAL-MISSING" in result["quality"]["blocking_codes"]
    assert all(fact["concept_id"] != "operating-income" for fact in result["facts"])


def test_identical_duplicate_collapses_with_both_exact_source_refs() -> None:
    fixture = _fixture()
    duplicate = copy.deepcopy(fixture["facts"][0])
    duplicate["source_fact_id"] = "RAW-SYNTHETIC-REVENUE-DUPLICATE"
    duplicate = attach_self_hash(duplicate, "source_fact_hash")
    fixture["facts"].append(duplicate)
    result = normalize_fixture(_rehash(fixture))["normalization_result"]
    revenue = next(fact for fact in result["facts"] if fact["concept_id"] == "revenue")
    assert revenue["source_fact_refs"] == [
        "RAW-SYNTHETIC-REVENUE",
        "RAW-SYNTHETIC-REVENUE-DUPLICATE",
    ]
    assert result["quality"]["status"] == "complete"


def test_conflicting_duplicate_fails_closed() -> None:
    fixture = _fixture()
    duplicate = copy.deepcopy(fixture["facts"][0])
    duplicate["source_fact_id"] = "RAW-SYNTHETIC-REVENUE-CONFLICT"
    duplicate["value_decimal"] = "1001"
    duplicate = attach_self_hash(duplicate, "source_fact_hash")
    fixture["facts"].append(duplicate)
    result = normalize_fixture(_rehash(fixture))["normalization_result"]
    assert result["quality"]["status"] == "unsupported"
    assert "NORM-DUPLICATE-CONFLICT" in result["quality"]["blocking_codes"]
    assert "revenue" in result["quality"]["material_missing_concepts"]


def test_selected_cross_accession_fact_cannot_silently_mix_lineages() -> None:
    fixture = _fixture()
    competing = copy.deepcopy(fixture["facts"][0])
    competing["source_fact_id"] = "RAW-SYNTHETIC-REVENUE-OTHER-ACCESSION"
    competing["accession"] = "0000000001-26-000002"
    competing["filed_at"] = "2026-02-15T00:00:00Z"
    competing = attach_self_hash(competing, "source_fact_hash")
    fixture["facts"].append(competing)
    result = normalize_fixture(_rehash(fixture))["normalization_result"]
    assert result["quality"]["status"] == "unsupported"
    assert "NORM-AMENDMENT-CONFLICT" in result["quality"]["blocking_codes"]
    assert "revenue" in result["quality"]["material_missing_concepts"]


def test_unmapped_standard_and_custom_tags_fail_closed() -> None:
    for namespace, expected in (
        ("us-gaap", "NORM-CONCEPT-UNMAPPED"),
        ("synthetic:issuer", "NORM-CUSTOM-TAG-REVIEW"),
    ):
        fixture = _fixture()
        fixture["facts"][0]["namespace"] = namespace
        fixture["facts"][0]["local_name"] = "UntrustedRevenueLabel"
        result = normalize_fixture(_rehash(fixture))["normalization_result"]
        assert result["quality"]["status"] == "unsupported"
        assert expected in result["quality"]["blocking_codes"]


def test_exact_human_custom_tag_decision_is_scoped_to_one_source_fact() -> None:
    fixture = _fixture()
    raw = fixture["facts"][0]
    raw["namespace"] = "synthetic:issuer"
    raw["local_name"] = "SyntheticCustomerRevenue"
    fixture = _rehash(fixture)
    review = fixture["mapping_review"]
    mapping = build_mapping_policy(
        taxonomy_version=fixture["taxonomy_version"],
        review_decision_ref=review["review_decision_ref"],
        review_decision_hash=review["review_hash"],
    )
    decision = {
        "schema_version": "0.1.0",
        "canonicalization_version": "fvi-canonical-json-v1",
        "decision_id": "CMD-M9-I5-SYNTHETIC-REVENUE-001",
        "company_cik": "0000000001",
        "taxonomy_version": "2026",
        "custom_namespace": "synthetic:issuer",
        "custom_local_name": "SyntheticCustomerRevenue",
        "source_fact_hash": fixture["facts"][0]["source_fact_hash"],
        "mapping_hash": mapping["mapping_hash"],
        "concept_id": "revenue",
        "standard_anchor_local_name": "RevenueFromContractWithCustomerExcludingAssessedTax",
        "period_type": "duration",
        "unit": "USD",
        "currency": "USD",
        "polarity": 1,
        "calculation_relationship_ref": "CALC-SYNTHETIC-REVENUE",
        "scope": "exact-company-taxonomy-source-fact",
        "reviewer_actor_id": "HUMAN-SYNTHETIC-FINANCIAL-REVIEWER",
        "reviewer_actor_type": "human",
        "reviewed_at": "2026-08-15T00:00:00Z",
        "decision": "approved",
        "network_state": "denied",
        "synthetic_only": True,
    }
    fixture["custom_tag_decisions"] = [attach_self_hash(decision, "decision_hash")]
    result = normalize_fixture(_rehash(fixture))["normalization_result"]
    revenue = next(fact for fact in result["facts"] if fact["concept_id"] == "revenue")
    assert revenue["provenance_kind"] == "custom_tag"
    assert revenue["custom_mapping_decision_ref"] == decision["decision_id"]
    assert result["quality"]["status"] == "complete"

    fixture["custom_tag_decisions"][0]["company_cik"] = "0000000002"
    fixture["custom_tag_decisions"][0] = attach_self_hash(
        fixture["custom_tag_decisions"][0], "decision_hash"
    )
    denied = normalize_fixture(_rehash(fixture))["normalization_result"]
    assert denied["quality"]["status"] == "unsupported"
    assert "NORM-CUSTOM-TAG-REVIEW" in denied["quality"]["blocking_codes"]


@pytest.mark.parametrize(
    ("field", "value", "code"),
    [
        ("value_decimal", "1e3", "NORM-UNIT-SCALE"),
        ("currency", "EUR", "NORM-UNIT-SCALE"),
        ("scale", 19, "NORM-UNIT-SCALE"),
        ("synthetic", False, "NORM-AUTHORITY-DENIED"),
    ],
)
def test_invalid_source_fact_authority_is_rejected(field: str, value: object, code: str) -> None:
    fixture = _fixture()
    fixture["facts"][0][field] = value
    with pytest.raises(NormalizationError) as error:
        normalize_fixture(_rehash(fixture))
    assert error.value.code == code


def test_provider_network_and_corporate_action_authority_are_absent() -> None:
    fixture = _fixture()
    fixture["network_state"] = "allowed"
    with pytest.raises(NormalizationError) as error:
        normalize_fixture(_rehash(fixture))
    assert error.value.code == "NORM-AUTHORITY-DENIED"

    fixture = _fixture()
    fixture["corporate_actions"] = [{"factor": "2", "source": "price"}]
    with pytest.raises(NormalizationError) as error:
        normalize_fixture(_rehash(fixture))
    assert error.value.code == "NORM-SPLIT-AMBIGUOUS"
