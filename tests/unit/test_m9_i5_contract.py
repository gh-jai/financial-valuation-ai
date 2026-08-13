import copy
import hashlib
import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "docs/milestones/M9-I5-us-gaap-normalization-reconciliation-contract-lock.md"
CHECKLIST = (
    ROOT
    / "templates/m9-i5-us-gaap-normalization-reconciliation-contract-review-checklist.md"
)
SCHEMAS = (
    ROOT / "schemas/m9-i5-concept-mapping-policy.schema.json",
    ROOT / "schemas/m9-i5-period-graph.schema.json",
    ROOT / "schemas/m9-i5-normalization-result.schema.json",
    ROOT / "schemas/m9-i5-normalization-validation-result.schema.json",
    ROOT / "schemas/m9-i5-custom-tag-decision.schema.json",
)
CONCEPT_REGISTRY = ROOT / "registries/m9-concepts.yaml"
PROVIDER_REGISTRY = ROOT / "registries/m9-provider-license.yaml"
NORMALIZED_FINANCIALS = ROOT / "schemas/normalized-financials.schema.json"
SOURCE_SNAPSHOT = ROOT / "schemas/source-snapshot.schema.json"
M9_PLAN = ROOT / "docs/milestones/M9-public-data-ingestion-normalization-plan.md"

BASELINE_SHA = "8cb0e7032ea5de265b883d5d9a36fe0f8988ad1e"
CONCEPT_IDS = (
    "revenue",
    "operating-income",
    "statutory-tax-rate",
    "cash-taxes",
    "depreciation-amortization",
    "capital-expenditure",
    "noncash-working-capital",
    "debt",
    "cash",
    "nonoperating-assets",
    "minority-interest",
    "other-claims",
    "diluted-shares",
)
FROZEN_SHA256 = {
    PROVIDER_REGISTRY: "08028b2e8cf42965856a660907c1ff152ed5950766e99bacf7203da6f0fdfe5d",
    CONCEPT_REGISTRY: "6d4e0331a709e2b4152fd6e846bfe84cb22978cc3bd0de19599e80847edb7fa9",
    NORMALIZED_FINANCIALS: "867a1f1e53764b05ad0f5895390b9a0717aac74e9e86807936441c7bf638e5ce",
    SOURCE_SNAPSHOT: "0e16692f8af002a54c4b4e3bd4d80f7facd98e51477232051661b2360615ae89",
    M9_PLAN: "dc81a6b365be9f09bbe480e790211675ebf9efd7b0d33571fc265df02b686e9c",
}


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _contract() -> str:
    return CONTRACT.read_text(encoding="utf-8")


def _schema(index: int) -> dict:
    return json.loads(SCHEMAS[index].read_text(encoding="utf-8"))


def _errors(schema: dict, document: dict) -> list:
    return list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(document))


def _mapping_document() -> dict:
    monetary = set(CONCEPT_IDS) - {"statutory-tax-rate", "diluted-shares"}
    mappings = []
    for index, concept_id in enumerate(CONCEPT_IDS, start=1):
        if concept_id == "statutory-tax-rate":
            kind, unit, period_type, aggregation = "rate", "ratio", "duration", "ratio"
        elif concept_id == "diluted-shares":
            kind, unit, period_type, aggregation = "shares", "shares", "duration", "direct"
        else:
            assert concept_id in monetary
            kind, unit = "monetary", "USD"
            period_type = "instant" if concept_id in {
                "noncash-working-capital",
                "debt",
                "cash",
                "nonoperating-assets",
                "minority-interest",
                "other-claims",
            } else "duration"
            aggregation = "direct"
        mappings.append(
            {
                "concept_id": concept_id,
                "kind": kind,
                "allowed_unit": unit,
                "period_type": period_type,
                "polarity": 1,
                "aggregation_rule": aggregation,
                "source_tags": {
                    "01": {"namespace": "us-gaap", "local_name": f"SyntheticTag{index}"}
                },
                "mapping_status": "candidate",
            }
        )
    return {
        "schema_version": "0.1.0",
        "canonicalization_version": "fvi-canonical-json-v1",
        "mapping_id": "MAP-" + "A" * 24,
        "mapping_version": "0.1.0",
        "concept_registry_id": "m9-concepts",
        "concept_registry_hash": FROZEN_SHA256[CONCEPT_REGISTRY],
        "taxonomy_namespace": "us-gaap",
        "taxonomy_version": "2026",
        "network_state": "denied",
        "synthetic_only": True,
        "mappings": mappings,
        "review_decision_ref": None,
        "review_decision_hash": None,
        "mapping_hash": "b" * 64,
    }


def _period_graph_document() -> dict:
    return {
        "schema_version": "0.1.0",
        "canonicalization_version": "fvi-canonical-json-v1",
        "period_graph_id": "PGR-" + "A" * 24,
        "source_snapshot_id": "SNP-SYNTHETIC",
        "source_snapshot_hash": "a" * 64,
        "mapping_id": "MAP-" + "A" * 24,
        "mapping_hash": "b" * 64,
        "network_state": "denied",
        "synthetic_only": True,
        "nodes": [
            {
                "period_id": "PER-SYNTHETIC-INSTANT",
                "basis": "instant",
                "start": None,
                "end": "2025-12-31",
                "fiscal_year": 2025,
                "fiscal_period": "INSTANT",
                "duration_days": None,
                "filing_record_ref": "REC-SYNTHETIC",
                "accession": "0000000001-26-000001",
                "filed_at": "2026-01-31T00:00:00Z",
                "amendment_of_accession": None,
                "selection_status": "selected",
            }
        ],
        "edges": [],
        "period_graph_hash": "c" * 64,
    }


def _normalization_document() -> dict:
    instant_concepts = {
        "noncash-working-capital",
        "debt",
        "cash",
        "nonoperating-assets",
        "minority-interest",
        "other-claims",
    }
    facts = []
    for concept_id in CONCEPT_IDS:
        if concept_id == "statutory-tax-rate":
            value, unit, currency = "0.2", "ratio", None
        elif concept_id == "diluted-shares":
            value, unit, currency = "10", "shares", None
        else:
            value, unit, currency = "100", "USD", "USD"
        token = concept_id.upper()
        facts.append(
            {
                "fact_id": f"FACT-SYNTHETIC-{token}",
                "concept_id": concept_id,
                "value_decimal": value,
                "unit": unit,
                "currency": currency,
                "period_id": (
                    "PER-SYNTHETIC-INSTANT"
                    if concept_id in instant_concepts
                    else "PER-SYNTHETIC-FY"
                ),
                "provenance_kind": "filing_fact",
                "source_fact_refs": [f"RAW-SYNTHETIC-{token}"],
                "calculation_rule": None,
                "custom_mapping_decision_ref": None,
                "review_status": "approved",
            }
        )
    check_types = (
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
    )
    reconciliations = []
    for check_type in check_types:
        token = check_type.upper()
        not_applicable = check_type == "custom-tag"
        reconciliations.append(
            {
                "check_id": f"RECCHK-SYNTHETIC-{token}",
                "check_type": check_type,
                "applicability": "not_applicable" if not_applicable else "applicable",
                "status": "not_applicable" if not_applicable else "passed",
                "difference_decimal": None if not_applicable else "0",
                "tolerance_decimal": "0",
                "fact_refs": [] if not_applicable else ["FACT-SYNTHETIC-REVENUE"],
                "message_code": (
                    "NORM-CUSTOM-TAG-NOT-APPLICABLE"
                    if not_applicable
                    else f"NORM-{token}-PASS"
                ),
                "exclusion_reason_code": (
                    "NORM-NO-CUSTOM-TAGS" if not_applicable else None
                ),
            }
        )
    return {
        "schema_version": "0.1.0",
        "canonicalization_version": "fvi-canonical-json-v1",
        "normalization_id": "NRM-" + "A" * 24,
        "source_snapshot_id": "SNP-SYNTHETIC",
        "source_snapshot_hash": "a" * 64,
        "mapping_id": "MAP-" + "A" * 24,
        "mapping_hash": "b" * 64,
        "period_graph_id": "PGR-" + "A" * 24,
        "period_graph_hash": "c" * 64,
        "company_cik": "0000000001",
        "network_state": "denied",
        "synthetic_only": True,
        "facts": facts,
        "reconciliations": reconciliations,
        "findings": [],
        "quality": {
            "status": "complete",
            "material_missing_concepts": [],
            "blocking_codes": [],
            "review_codes": [],
        },
        "normalization_hash": "d" * 64,
    }


def _validation_document() -> dict:
    return {
        "schema_version": "0.1.0",
        "canonicalization_version": "fvi-canonical-json-v1",
        "validation_id": "NVAL-" + "A" * 24,
        "normalization_id": "NRM-" + "A" * 24,
        "normalization_hash": "d" * 64,
        "mapping_hash": "b" * 64,
        "period_graph_hash": "c" * 64,
        "source_snapshot_hash": "a" * 64,
        "implementation_separation": "independent",
        "network_state": "denied",
        "synthetic_only": True,
        "findings": [],
        "passed": True,
        "validation_hash": "e" * 64,
    }


def _custom_tag_decision_document() -> dict:
    return {
        "schema_version": "0.1.0",
        "canonicalization_version": "fvi-canonical-json-v1",
        "decision_id": "CMD-SYNTHETIC-REVENUE",
        "company_cik": "0000000001",
        "taxonomy_version": "2026",
        "custom_namespace": "synthetic:example",
        "custom_local_name": "SyntheticRevenue",
        "source_fact_hash": "f" * 64,
        "mapping_hash": "b" * 64,
        "concept_id": "revenue",
        "standard_anchor_local_name": "RevenueFromContractWithCustomerExcludingAssessedTax",
        "period_type": "duration",
        "unit": "USD",
        "currency": "USD",
        "polarity": 1,
        "calculation_relationship_ref": "CALC-SYNTHETIC-REVENUE",
        "scope": "exact-company-taxonomy-source-fact",
        "reviewer_actor_id": "HUMAN-FINANCIAL-REVIEWER",
        "reviewer_actor_type": "human",
        "reviewed_at": "2026-08-14T00:00:00Z",
        "decision": "approved",
        "network_state": "denied",
        "synthetic_only": True,
        "decision_hash": "1" * 64,
    }


def test_m9_i5_contract_is_design_only_exact_baseline_and_network_denied() -> None:
    normalized = " ".join(_contract().split())
    for requirement in (
        "LOCAL_CONTRACT_CANDIDATE_REVIEW_PENDING",
        f"Canonical baseline: `main` at `{BASELINE_SHA}`",
        "Network state: `DENIED`",
        "contract candidate, not a mapper, period engine, normalizer, reconciler",
        "does not authorize staging, committing, pushing, a pull request",
        "keep all M9-I4 public adapters stopped before transport",
        "No stage, commit, push, Draft PR",
    ):
        assert requirement in normalized


def test_frozen_registries_and_inherited_interfaces_are_byte_exact() -> None:
    for path, expected_hash in FROZEN_SHA256.items():
        assert _sha256(path) == expected_hash
        assert expected_hash in _contract()
    provider = PROVIDER_REGISTRY.read_text(encoding="utf-8")
    assert provider.count("status: pending") == 4
    assert provider.count("live_activation: disabled") == 4


def test_contract_locks_exact_concept_registry_surface_and_order() -> None:
    registry = yaml.safe_load(CONCEPT_REGISTRY.read_text(encoding="utf-8"))
    assert tuple(item["concept_id"] for item in registry["concepts"]) == CONCEPT_IDS
    text = _contract()
    positions = [text.index(f"{index}. `{concept_id}`") for index, concept_id in enumerate(CONCEPT_IDS, 1)]
    assert positions == sorted(positions)
    for rule in (
        "There are no aliases, wildcard concepts, pass-through unknowns",
        "A missing, duplicate, out-of-order, unit-incompatible",
        "Mapping one concept\ndoes not authorize another",
    ):
        assert rule in text


def test_contract_locks_period_amendment_duplicate_custom_and_no_fill_rules() -> None:
    normalized = " ".join(_contract().split())
    for requirement in (
        "never forms a cycle",
        "52/53-week year",
        "Amendments are not field-level patches",
        "collapse only when their scaled canonical values are identical",
        "never auto-mapped by label similarity",
        "No missing or rejected value is replaced with zero, a peer value",
        "Applying a factor twice",
        "all ten reconciliation families",
    ):
        assert requirement in normalized


def test_contract_excludes_live_real_private_registry_and_later_scope() -> None:
    text = _contract()
    for excluded in (
        "No adapter, transport, DNS, socket, HTTP client",
        "provider-registry/right change",
        "No real company, ticker, CIK, filing, accession, XBRL fact, provider response",
        "PDF",
        "attachment",
        "`project_sources/` use",
        "No silent zero/peer/older-period/forecast/LLM fill",
        "M9-I6",
        "valuation",
        "LLM",
        "UI",
    ):
        assert excluded in text


def test_m9_i5_schemas_are_strict_valid_draft_2020_12_contracts() -> None:
    def assert_object_surfaces_closed(value: object) -> None:
        if isinstance(value, dict):
            if value.get("type") == "object":
                assert value.get("additionalProperties") is False
            for child in value.values():
                assert_object_surfaces_closed(child)
        elif isinstance(value, list):
            for child in value:
                assert_object_surfaces_closed(child)

    assert len(SCHEMAS) == 5
    for path in SCHEMAS:
        schema = json.loads(path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
        assert_object_surfaces_closed(schema)


def test_valid_reference_closed_contract_artifacts_pass_schema_validation() -> None:
    documents = (
        _mapping_document(),
        _period_graph_document(),
        _normalization_document(),
        _validation_document(),
        _custom_tag_decision_document(),
    )
    for schema, document in zip((_schema(i) for i in range(len(SCHEMAS))), documents):
        assert _errors(schema, document) == []


def test_schemas_reject_unknown_fields_and_authority_escalation() -> None:
    documents = (
        _mapping_document(),
        _period_graph_document(),
        _normalization_document(),
        _validation_document(),
        _custom_tag_decision_document(),
    )
    for index, document in enumerate(documents):
        unknown = copy.deepcopy(document)
        unknown["provider_activation"] = True
        assert _errors(_schema(index), unknown)
        network = copy.deepcopy(document)
        network["network_state"] = "enabled"
        assert _errors(_schema(index), network)
        synthetic = copy.deepcopy(document)
        synthetic["synthetic_only"] = False
        assert _errors(_schema(index), synthetic)


def test_mapping_schema_rejects_concept_drift_wrong_count_kind_and_unit() -> None:
    schema = _schema(0)
    document = _mapping_document()
    assert schema["properties"]["mappings"]["minItems"] == 13
    assert schema["properties"]["mappings"]["maxItems"] == 13
    assert tuple(schema["$defs"]["conceptId"]["enum"]) == CONCEPT_IDS
    assert (
        schema["properties"]["concept_registry_hash"]["const"]
        == FROZEN_SHA256[CONCEPT_REGISTRY]
    )

    for mutation in (
        lambda item: item.update(concept_id="invented-concept"),
        lambda item: item.update(kind="rate", allowed_unit="USD"),
        lambda item: item.update(period_type="unknown"),
        lambda item: item.update(polarity=0),
    ):
        changed = copy.deepcopy(document)
        mutation(changed["mappings"][0])
        assert _errors(schema, changed)
    missing = copy.deepcopy(document)
    missing["mappings"].pop()
    assert _errors(schema, missing)
    reordered = copy.deepcopy(document)
    reordered["mappings"][0], reordered["mappings"][1] = (
        reordered["mappings"][1],
        reordered["mappings"][0],
    )
    assert _errors(schema, reordered)
    duplicate_concept = copy.deepcopy(document)
    duplicate_concept["mappings"][1]["concept_id"] = "revenue"
    assert _errors(schema, duplicate_concept)

    coherent_retype = copy.deepcopy(document)
    coherent_retype["mappings"][0].update(kind="rate", allowed_unit="ratio")
    assert _errors(schema, coherent_retype)
    wrong_period = copy.deepcopy(document)
    wrong_period["mappings"][0]["period_type"] = "instant"
    assert _errors(schema, wrong_period)
    wrong_registry_hash = copy.deepcopy(document)
    wrong_registry_hash["concept_registry_hash"] = "f" * 64
    assert _errors(schema, wrong_registry_hash)
    positional_priority_bypass = copy.deepcopy(document)
    positional_priority_bypass["mappings"][0]["source_tags"] = [
        {"namespace": "us-gaap", "local_name": "SyntheticTag1", "priority": 1},
        {"namespace": "us-gaap", "local_name": "SyntheticTagX", "priority": 1},
    ]
    assert _errors(schema, positional_priority_bypass)
    malformed_priority_key = copy.deepcopy(document)
    malformed_priority_key["mappings"][0]["source_tags"] = {
        "1": {"namespace": "us-gaap", "local_name": "SyntheticTag1"}
    }
    assert _errors(schema, malformed_priority_key)

    approved_without_review = copy.deepcopy(document)
    approved_without_review["mappings"][0]["mapping_status"] = "approved"
    assert _errors(schema, approved_without_review)
    approved_with_review = copy.deepcopy(approved_without_review)
    approved_with_review["review_decision_ref"] = "MREV-SYNTHETIC"
    approved_with_review["review_decision_hash"] = "9" * 64
    assert _errors(schema, approved_with_review) == []


def test_period_schema_rejects_instant_duration_and_reference_shape_attacks() -> None:
    schema = _schema(1)
    document = _period_graph_document()
    instant_with_start = copy.deepcopy(document)
    instant_with_start["nodes"][0]["start"] = "2025-01-01"
    assert _errors(schema, instant_with_start)
    instant_with_duration = copy.deepcopy(document)
    instant_with_duration["nodes"][0]["duration_days"] = 365
    assert _errors(schema, instant_with_duration)
    bad_accession = copy.deepcopy(document)
    bad_accession["nodes"][0]["accession"] = "../real-filing"
    assert _errors(schema, bad_accession)


def test_normalization_schema_rejects_numeric_unit_custom_tag_and_quality_bypasses() -> None:
    schema = _schema(2)
    document = _normalization_document()
    for lexical in ("1e3", "01", "-0", "1.0", "+1", "NaN", "1,000"):
        changed = copy.deepcopy(document)
        changed["facts"][0]["value_decimal"] = lexical
        assert _errors(schema, changed), lexical

    wrong_currency = copy.deepcopy(document)
    wrong_currency["facts"][0]["currency"] = None
    assert _errors(schema, wrong_currency)

    coherent_unit_retype = copy.deepcopy(document)
    coherent_unit_retype["facts"][0].update(unit="ratio", currency=None)
    assert _errors(schema, coherent_unit_retype)

    negative_tolerance = copy.deepcopy(document)
    negative_tolerance["reconciliations"][0]["tolerance_decimal"] = "-1"
    assert _errors(schema, negative_tolerance)

    excessive_precision = copy.deepcopy(document)
    excessive_precision["facts"][0]["value_decimal"] = "1" * 257
    assert _errors(schema, excessive_precision)

    incomplete_concepts = copy.deepcopy(document)
    incomplete_concepts["facts"] = incomplete_concepts["facts"][:-1]
    assert _errors(schema, incomplete_concepts)

    omitted_reconciliation_family = copy.deepcopy(document)
    omitted_reconciliation_family["reconciliations"] = [
        item
        for item in omitted_reconciliation_family["reconciliations"]
        if item["check_type"] != "cash-flow"
    ]
    assert _errors(schema, omitted_reconciliation_family)

    invalid_exclusion = copy.deepcopy(document)
    custom_check = next(
        item for item in invalid_exclusion["reconciliations"] if item["check_type"] == "custom-tag"
    )
    custom_check["status"] = "passed"
    assert _errors(schema, invalid_exclusion)

    custom_without_decision = copy.deepcopy(document)
    custom_without_decision["facts"][0]["provenance_kind"] = "custom_tag"
    assert _errors(schema, custom_without_decision)

    derived_without_rule = copy.deepcopy(document)
    derived_without_rule["facts"][0]["provenance_kind"] = "derived_calculation"
    assert _errors(schema, derived_without_rule)

    direct_with_rule = copy.deepcopy(document)
    direct_with_rule["facts"][0]["calculation_rule"] = "ratio"
    assert _errors(schema, direct_with_rule)

    silent_review = copy.deepcopy(document)
    silent_review["findings"] = [
        {
            "code": "NORM-CUSTOM-TAG-REVIEW",
            "severity": "review",
            "message": "Synthetic review finding.",
            "subject_refs": ["FACT-SYNTHETIC-REVENUE"],
        }
    ]
    assert _errors(schema, silent_review)

    failed_reconciliation = copy.deepcopy(document)
    failed_reconciliation["reconciliations"][0]["status"] = "failed"
    assert _errors(schema, failed_reconciliation)


def test_validation_schema_makes_pass_impossible_with_any_finding() -> None:
    schema = _schema(3)
    passed = _validation_document()
    passed["findings"] = [
        {
            "code": "NORM-HASH-MISMATCH",
            "severity": "blocking",
            "message": "Synthetic hash mismatch.",
            "subject_refs": ["NRM-SYNTHETIC"],
        }
    ]
    assert _errors(schema, passed)
    failed_without_finding = _validation_document()
    failed_without_finding["passed"] = False
    assert _errors(schema, failed_without_finding)


def test_custom_tag_decision_schema_rejects_nonhuman_scope_and_authority_bypass() -> None:
    schema = _schema(4)
    document = _custom_tag_decision_document()
    assert _errors(schema, document) == []

    nonhuman = copy.deepcopy(document)
    nonhuman["reviewer_actor_type"] = "agent"
    assert _errors(schema, nonhuman)

    wrong_namespace = copy.deepcopy(document)
    wrong_namespace["custom_namespace"] = "https://real.example/taxonomy"
    assert _errors(schema, wrong_namespace)

    wrong_unit = copy.deepcopy(document)
    wrong_unit["currency"] = None
    assert _errors(schema, wrong_unit)

    coherent_semantic_retype = copy.deepcopy(document)
    coherent_semantic_retype.update(period_type="instant", unit="ratio", currency=None)
    assert _errors(schema, coherent_semantic_retype)

    unknown_concept = copy.deepcopy(document)
    unknown_concept["concept_id"] = "invented-concept"
    assert _errors(schema, unknown_concept)

    broad_scope = copy.deepcopy(document)
    broad_scope["scope"] = "all-issuers"
    assert _errors(schema, broad_scope)
    assert "scope limited to the named issuer/taxonomy/fact pattern" in " ".join(
        _contract().split()
    )


def test_independent_validator_and_coordinated_mutation_requirements_are_locked() -> None:
    normalized = " ".join(_contract().split())
    for requirement in (
        "must not import production mapper, period, decimal, normalization, reconciliation",
        "rebuild the acyclic period/amendment graph",
        "independently apply scale, polarity, exact-decimal arithmetic",
        "AST/import graph to deny network, provider SDK, subprocess, shell, dynamic execution",
        "A coordinated mutation that updates downstream hashes must still fail",
    ):
        assert requirement in normalized


def test_review_checklist_has_no_preselected_verdict() -> None:
    text = CHECKLIST.read_text(encoding="utf-8")
    assert text.count("- [ ]") >= 35
    assert "`[ ] PASS  [ ] COMMENTED_BLOCKING  [ ] request changes`" in text
    assert "No box is preselected" in text
