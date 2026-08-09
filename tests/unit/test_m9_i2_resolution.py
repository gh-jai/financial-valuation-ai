import copy
from datetime import datetime, timezone
from pathlib import Path

import pytest

from tools.retail_data.canonical import canonical_sha256
from tools.retail_data.identity_contracts import IdentityContractError, attach_hash, strict_load
from tools.retail_data.resolution import (
    ResolutionStop,
    create_selection,
    load_synthetic_catalog,
    normalize_query,
    resolve_issuer,
    verify_selected_identity,
)
from tools.retail_data.structural_scope import evaluate_structural_scope


ROOT = Path(__file__).resolve().parents[2]
AT = "2026-08-09T00:00:00Z"
AT_DT = datetime(2026, 8, 9, tzinfo=timezone.utc)


def request(query: dict, suffix: str = "1") -> dict:
    return {
        "schema_version": "0.1.0",
        "request_id": f"REQ-SYNTH-{suffix}",
        "requested_at": AT,
        "market_scope": "us-listed-non-financial-operating-company",
        "query": query,
        "locale": "en",
        "jurisdiction": {"country_code": "US"},
        "acknowledgements": {
            "research_not_advice": True,
            "no_trade_instruction": True,
            "scenario_uncertainty": True,
        },
    }


@pytest.fixture
def artifacts() -> tuple[dict, dict, dict]:
    catalog = load_synthetic_catalog("m9-i2-synthetic-catalog", AT_DT)
    policy = strict_load(ROOT / "registries/m9-identity-resolution-policy.yaml")
    scope = strict_load(ROOT / "registries/m9-issuer-structural-scope.yaml")
    return catalog, policy, scope


def rehash_catalog(catalog: dict) -> dict:
    value = copy.deepcopy(catalog)
    for evidence in value["evidence_records"]:
        updated = attach_hash(
            {key: item for key, item in evidence.items() if key != "evidence_record_hash"},
            "evidence_record_hash",
        )
        evidence.clear()
        evidence.update(updated)
    for record in value["records"]:
        for listing in record["listing_history"]:
            updated = attach_hash(
                {key: item for key, item in listing.items() if key != "listing_entry_hash"},
                "listing_entry_hash",
            )
            listing.clear()
            listing.update(updated)
        updated_record = attach_hash(
            {key: item for key, item in record.items() if key != "catalog_record_hash"},
            "catalog_record_hash",
        )
        record.clear()
        record.update(updated_record)
    return attach_hash(
        {key: item for key, item in value.items() if key != "catalog_hash"}, "catalog_hash"
    )


def full_path(query: dict, artifacts: tuple[dict, dict, dict], suffix: str = "1") -> tuple:
    catalog, policy, scope = artifacts
    candidate_set = resolve_issuer(
        request(query, suffix), catalog, policy, resolution_at=AT,
        candidate_set_id=f"ICS-SYNTH-{suffix}",
    )
    selection = create_selection(
        candidate_set,
        selection_id=f"ISL-SYNTH-{suffix}",
        selected_at=AT,
        selected_candidate_id=candidate_set["candidates"][0]["candidate_id"],
        actor_id="synthetic-human-reviewer",
    )
    identity = verify_selected_identity(
        candidate_set, selection, policy,
        verified_identity_id=f"VID-SYNTH-{suffix}", verified_at=AT,
    )
    decision = evaluate_structural_scope(
        identity, scope, policy, scope_decision_id=f"ISD-SYNTH-{suffix}", evaluated_at=AT,
    )
    return candidate_set, selection, identity, decision


@pytest.mark.parametrize(
    ("query", "kind"),
    [
        ({"kind": "ticker", "ticker": "ZXQA"}, "ticker_current_exact"),
        ({"kind": "cik", "cik": "9000000001"}, "cik_exact"),
        ({"kind": "company_name", "company_name": "Northstar Synthetic Operating Company"}, "legal_name_exact"),
        ({"kind": "company_name", "company_name": " Northstar   Synthetic "}, "declared_alias_exact"),
    ],
)
def test_exact_resolution_vectors_are_deterministic(query: dict, kind: str, artifacts) -> None:
    first = resolve_issuer(request(query), artifacts[0], artifacts[1], resolution_at=AT, candidate_set_id="ICS-SYNTH-1")
    second = resolve_issuer(request(query), artifacts[0], artifacts[1], resolution_at=AT, candidate_set_id="ICS-SYNTH-1")
    assert first == second
    assert first["status"] == "unique_candidate"
    assert first["candidates"][0]["primary_match_kind"] == kind


def test_nfkc_casefold_and_whitespace_do_not_enable_fuzzy_matching(artifacts) -> None:
    kind, value = normalize_query(request({"kind": "company_name", "company_name": "  Ａｍｂｉｇｕｏｕｓ   SYNTHETIC industries  "}))
    assert (kind, value) == ("company_name", "ambiguous synthetic industries")
    no_match = resolve_issuer(request({"kind": "company_name", "company_name": "Northstar"}), artifacts[0], artifacts[1], resolution_at=AT, candidate_set_id="ICS-SYNTH-2")
    assert no_match["status"] == "not_found" and not no_match["candidates"]


def test_ambiguity_requires_explicit_hash_bound_human_selection(artifacts) -> None:
    candidate_set = resolve_issuer(request({"kind": "company_name", "company_name": "Ambiguous Synthetic Industries"}), artifacts[0], artifacts[1], resolution_at=AT, candidate_set_id="ICS-SYNTH-3")
    assert candidate_set["status"] == "selection_required"
    assert len(candidate_set["candidates"]) == 2
    assert candidate_set["errors"][0]["code"] == "IDENTITY-AMBIGUOUS"
    selection = create_selection(candidate_set, selection_id="ISL-SYNTH-3", selected_at=AT, selected_candidate_id=candidate_set["candidates"][1]["candidate_id"], actor_id="synthetic-human-reviewer")
    assert selection["selection_reason"] == "resolved_ambiguity"
    assert selection["candidate_set_hash"] == candidate_set["candidate_set_hash"]


@pytest.mark.parametrize(
    ("mutation", "code"),
    [
        ("cik-name", "IDENTITY-CIK-NAME-MISMATCH"),
        ("future", "IDENTITY-EVIDENCE-FUTURE"),
        ("hash", "IDENTITY-HASH-MISMATCH"),
    ],
)
def test_catalog_failures_preserve_stable_error_taxonomy(artifacts, mutation: str, code: str) -> None:
    catalog = copy.deepcopy(artifacts[0])
    if mutation == "cik-name":
        catalog["evidence_records"][0]["legal_name"] = "Conflicting Synthetic Name"
        catalog = rehash_catalog(catalog)
    elif mutation == "future":
        catalog["evidence_records"][0]["observed_at"] = "2026-08-10T00:00:00Z"
        catalog["evidence_records"][0]["fact_as_of"] = "2026-08-10T00:00:00Z"
        catalog = rehash_catalog(catalog)
    else:
        catalog["records"][0]["legal_name"] = "Hash Mutated Synthetic Name"
    with pytest.raises(ResolutionStop) as stopped:
        resolve_issuer(
            request({"kind": "ticker", "ticker": "ZXQA"}), catalog, artifacts[1],
            resolution_at=AT, candidate_set_id="ICS-CATALOG-STOP",
        )
    assert stopped.value.error.code == code


def test_temporal_ticker_reuse_is_non_overridable(artifacts) -> None:
    catalog = copy.deepcopy(artifacts[0])
    catalog["records"][1]["listing_history"][0]["ticker"] = "ZXQA"
    catalog["evidence_records"][1]["ticker"] = "ZXQA"
    catalog = rehash_catalog(catalog)
    candidate_set = resolve_issuer(
        request({"kind": "ticker", "ticker": "ZXQA"}, "REUSE"), catalog, artifacts[1],
        resolution_at=AT, candidate_set_id="ICS-TICKER-REUSE",
    )
    assert candidate_set["status"] == "blocked"
    assert candidate_set["errors"][0]["code"] == "IDENTITY-TICKER-REUSED"
    with pytest.raises(ResolutionStop):
        create_selection(
            candidate_set, selection_id="ISL-REUSE", selected_at=AT,
            selected_candidate_id="ICD-" + "A" * 64, actor_id="synthetic-human-reviewer",
        )


def test_historical_ticker_returns_current_identity_and_retains_closed_evidence(artifacts) -> None:
    catalog = copy.deepcopy(artifacts[0])
    historical_evidence = {
        "source_record_id": "EVD-HIST-0001",
        "source_kind": "synthetic_identity",
        "observed_at": "2019-01-02T00:00:00Z",
        "fact_as_of": "2019-01-01T00:00:00Z",
        "assertion_kind": "closed_interval",
        "cik": "9000000001",
        "legal_name": "Northstar Synthetic Operating Company",
        "ticker": "ZXQH",
        "exchange_code": "XTEST",
        "asserted_effective_from": "2018-01-01T00:00:00Z",
        "asserted_effective_to": "2019-01-01T00:00:00Z",
        "evidence_record_hash": "0" * 64,
    }
    historical_listing = {
        "ticker": "ZXQH",
        "exchange_code": "XTEST",
        "effective_from": "2018-01-01T00:00:00Z",
        "effective_to": "2019-01-01T00:00:00Z",
        "evidence_record_refs": ["EVD-HIST-0001"],
        "listing_entry_hash": "0" * 64,
    }
    catalog["evidence_records"].insert(0, historical_evidence)
    catalog["records"][0]["listing_history"].insert(0, historical_listing)
    catalog["records"][0]["source_record_refs"].insert(0, "EVD-HIST-0001")
    catalog = rehash_catalog(catalog)
    candidate_set = resolve_issuer(
        request({"kind": "ticker", "ticker": "ZXQH"}, "HIST"), catalog, artifacts[1],
        resolution_at=AT, candidate_set_id="ICS-HISTORICAL",
    )
    candidate = candidate_set["candidates"][0]
    assert candidate["primary_match_kind"] == "ticker_historical_exact"
    assert candidate["ticker"] == "ZXQA"
    assert candidate["matched_listing_refs"][0]["ticker"] == "ZXQH"
    assert candidate["matched_listing_refs"][0]["derived_temporal_classification"] == "historical"


def test_nonhuman_or_replayed_selection_fails_closed(artifacts) -> None:
    candidate_set, selection, _, _ = full_path({"kind": "ticker", "ticker": "ZXQA"}, artifacts)
    with pytest.raises(ResolutionStop):
        create_selection(candidate_set, selection_id="ISL-BAD", selected_at=AT, selected_candidate_id=candidate_set["candidates"][0]["candidate_id"], actor_id="service", actor_type="service")
    mutated = copy.deepcopy(candidate_set)
    mutated["candidates"][0]["ticker"] = "ZXQZ"
    mutated["candidate_set_hash"] = canonical_sha256({key: value for key, value in mutated.items() if key != "candidate_set_hash"})
    with pytest.raises(IdentityContractError, match="candidate_hash"):
        verify_selected_identity(mutated, selection, artifacts[1], verified_identity_id="VID-BAD", verified_at=AT)


def test_inner_candidate_hash_and_selection_reason_are_rechecked(artifacts) -> None:
    candidate_set, selection, _, _ = full_path(
        {"kind": "ticker", "ticker": "ZXQA"}, artifacts, "INNER"
    )
    mutated = copy.deepcopy(candidate_set)
    mutated["candidates"][0]["ticker"] = "ZXQZ"
    mutated = attach_hash(
        {key: value for key, value in mutated.items() if key != "candidate_set_hash"},
        "candidate_set_hash",
    )
    with pytest.raises(IdentityContractError, match="candidate_hash"):
        verify_selected_identity(
            mutated, selection, artifacts[1],
            verified_identity_id="VID-INNER-HASH", verified_at=AT,
        )
    wrong_reason = copy.deepcopy(selection)
    wrong_reason["selection_reason"] = "resolved_ambiguity"
    wrong_reason = attach_hash(
        {key: value for key, value in wrong_reason.items() if key != "selection_hash"},
        "selection_hash",
    )
    with pytest.raises(ResolutionStop) as stopped:
        verify_selected_identity(
            candidate_set, wrong_reason, artifacts[1],
            verified_identity_id="VID-WRONG-REASON", verified_at=AT,
        )
    assert stopped.value.error.code == "IDENTITY-SELECTION-MISMATCH"


def test_supported_and_bank_paths_never_choose_lifecycle_route(artifacts) -> None:
    _, _, _, eligible = full_path({"kind": "ticker", "ticker": "ZXQA"}, artifacts, "4")
    _, _, _, bank = full_path({"kind": "ticker", "ticker": "ZXQD"}, artifacts, "5")
    assert eligible["outcome"] == "eligible_for_data_review"
    assert eligible["eligible_for_m9_data_review"] is True
    assert bank["outcome"] == "unsupported"
    assert bank["blocking_errors"][0]["code"] == "SCOPE-UNSUPPORTED-FINANCIAL"
    assert eligible["lifecycle_route_status"] == bank["lifecycle_route_status"] == "not_evaluated"


@pytest.mark.parametrize(
    ("field", "value", "code", "suffix"),
    [
        ("primary_listing_country", "JP", "SCOPE-UNSUPPORTED-NON-US", "NONUS"),
        ("primary_reporting_currency", "JPY", "SCOPE-UNSUPPORTED-NON-USD", "NONUSD"),
    ],
)
def test_any_non_us_or_non_usd_identity_is_structurally_unsupported(
    artifacts, field: str, value: str, code: str, suffix: str
) -> None:
    _, _, identity, _ = full_path(
        {"kind": "ticker", "ticker": "ZXQA"}, artifacts, suffix
    )
    changed = copy.deepcopy(identity)
    changed[field] = value
    changed = attach_hash(
        {key: item for key, item in changed.items() if key != "verified_identity_hash"},
        "verified_identity_hash",
    )
    decision = evaluate_structural_scope(
        changed, artifacts[2], artifacts[1],
        scope_decision_id="ISD-NON-SUPPORTED", evaluated_at=AT,
    )
    assert decision["outcome"] == "unsupported"
    assert decision["blocking_errors"][0]["code"] == code


def test_contradictory_classification_is_insufficient_not_unsupported(artifacts) -> None:
    _, _, identity, _ = full_path(
        {"kind": "ticker", "ticker": "ZXQA"}, artifacts, "CONTRADICT"
    )
    changed = copy.deepcopy(identity)
    changed["regulated_capital_model_required"] = True
    changed = attach_hash(
        {key: item for key, item in changed.items() if key != "verified_identity_hash"},
        "verified_identity_hash",
    )
    decision = evaluate_structural_scope(
        changed, artifacts[2], artifacts[1],
        scope_decision_id="ISD-CONTRADICT", evaluated_at=AT,
    )
    assert decision["outcome"] == "insufficient_evidence"
    assert decision["blocking_errors"][0]["code"] == "SCOPE-INSUFFICIENT-EVIDENCE"


def test_private_identity_stops_before_verified_handoff(artifacts) -> None:
    candidate_set, selection, _, _ = full_path(
        {"kind": "ticker", "ticker": "ZXQA"}, artifacts, "PRIVATE"
    )
    changed_set = copy.deepcopy(candidate_set)
    changed_candidate = changed_set["candidates"][0]
    changed_candidate["public_company_status"] = "private"
    changed_candidate = attach_hash(
        {key: value for key, value in changed_candidate.items() if key != "candidate_hash"},
        "candidate_hash",
    )
    changed_set["candidates"][0] = changed_candidate
    changed_set = attach_hash(
        {key: value for key, value in changed_set.items() if key != "candidate_set_hash"},
        "candidate_set_hash",
    )
    changed_selection = copy.deepcopy(selection)
    changed_selection["candidate_set_hash"] = changed_set["candidate_set_hash"]
    changed_selection["selected_candidate_hash"] = changed_candidate["candidate_hash"]
    changed_selection = attach_hash(
        {key: value for key, value in changed_selection.items() if key != "selection_hash"},
        "selection_hash",
    )
    with pytest.raises(ResolutionStop) as stopped:
        verify_selected_identity(
            changed_set, changed_selection, artifacts[1],
            verified_identity_id="VID-PRIVATE", verified_at=AT,
        )
    assert stopped.value.error.code == "IDENTITY-DELISTED"


def test_stale_identity_one_second_beyond_policy_stops(artifacts) -> None:
    candidate_set = resolve_issuer(request({"kind": "ticker", "ticker": "ZXQA"}), artifacts[0], artifacts[1], resolution_at=AT, candidate_set_id="ICS-STale-1".upper())
    selection = create_selection(candidate_set, selection_id="ISL-STALE-1", selected_at=AT, selected_candidate_id=candidate_set["candidates"][0]["candidate_id"], actor_id="synthetic-human-reviewer")
    with pytest.raises(ResolutionStop) as stopped:
        verify_selected_identity(candidate_set, selection, artifacts[1], verified_identity_id="VID-STALE-1", verified_at="2027-08-02T00:00:01Z")
    assert stopped.value.error.code == "IDENTITY-STALE"
