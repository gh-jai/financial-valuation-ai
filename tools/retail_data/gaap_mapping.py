"""Versioned, exact-tag US-GAAP mapping for the synthetic M9-I5 runtime."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from .canonical import CANONICALIZATION_VERSION
from .gaap_contracts import (
    CONCEPT_IDS,
    CONCEPT_REGISTRY_HASH,
    SCHEMA_VERSION,
    NormalizationError,
    deterministic_id,
    finalize_artifact,
    require_self_hash,
    validate_schema,
)

_MAPPING_ROWS = (
    (
        "revenue",
        "monetary",
        "USD",
        "duration",
        1,
        "direct",
        ("RevenueFromContractWithCustomerExcludingAssessedTax",),
    ),
    ("operating-income", "monetary", "USD", "duration", 1, "direct", ("OperatingIncomeLoss",)),
    (
        "statutory-tax-rate",
        "rate",
        "ratio",
        "duration",
        1,
        "direct",
        ("EffectiveIncomeTaxRateReconciliationAtFederalStatutoryIncomeTaxRate",),
    ),
    ("cash-taxes", "monetary", "USD", "duration", 1, "direct", ("IncomeTaxesPaidNet",)),
    (
        "depreciation-amortization",
        "monetary",
        "USD",
        "duration",
        1,
        "direct",
        ("DepreciationDepletionAndAmortization",),
    ),
    (
        "capital-expenditure",
        "monetary",
        "USD",
        "duration",
        -1,
        "direct",
        ("PaymentsToAcquirePropertyPlantAndEquipment",),
    ),
    (
        "noncash-working-capital",
        "monetary",
        "USD",
        "instant",
        1,
        "direct",
        ("WorkingCapital",),
    ),
    (
        "debt",
        "monetary",
        "USD",
        "instant",
        1,
        "direct",
        ("LongTermDebtAndFinanceLeaseObligations",),
    ),
    ("cash", "monetary", "USD", "instant", 1, "direct", ("CashAndCashEquivalentsAtCarryingValue",)),
    ("nonoperating-assets", "monetary", "USD", "instant", 1, "direct", ("ShortTermInvestments",)),
    (
        "minority-interest",
        "monetary",
        "USD",
        "instant",
        1,
        "direct",
        ("NoncontrollingInterestInConsolidatedEntity",),
    ),
    (
        "other-claims",
        "monetary",
        "USD",
        "instant",
        1,
        "direct",
        ("OperatingLeaseLiabilityNoncurrent",),
    ),
    (
        "diluted-shares",
        "shares",
        "shares",
        "duration",
        1,
        "direct",
        ("WeightedAverageNumberOfDilutedSharesOutstanding",),
    ),
)


def build_mapping_policy(
    *, taxonomy_version: str, review_decision_ref: str, review_decision_hash: str
) -> dict[str, Any]:
    """Build the only approved standard-tag policy for this runtime version."""

    if (
        not isinstance(review_decision_ref, str)
        or not review_decision_ref.startswith("MREV-")
        or not isinstance(review_decision_hash, str)
        or len(review_decision_hash) != 64
    ):
        raise NormalizationError("NORM-AUTHORITY-DENIED", "mapping review evidence is missing")
    mappings = []
    for concept_id, kind, unit, period_type, polarity, aggregation, tags in _MAPPING_ROWS:
        mappings.append(
            {
                "concept_id": concept_id,
                "kind": kind,
                "allowed_unit": unit,
                "period_type": period_type,
                "polarity": polarity,
                "aggregation_rule": aggregation,
                "source_tags": {
                    f"{index:02d}": {"namespace": "us-gaap", "local_name": tag}
                    for index, tag in enumerate(tags, start=1)
                },
                "mapping_status": "approved",
            }
        )
    identity = {
        "mapping_version": "0.1.0",
        "taxonomy_version": taxonomy_version,
        "concept_registry_hash": CONCEPT_REGISTRY_HASH,
        "mappings": mappings,
        "review_decision_ref": review_decision_ref,
        "review_decision_hash": review_decision_hash,
    }
    value = {
        "schema_version": SCHEMA_VERSION,
        "canonicalization_version": CANONICALIZATION_VERSION,
        "mapping_id": deterministic_id("MAP", identity),
        "mapping_version": "0.1.0",
        "concept_registry_id": "m9-concepts",
        "concept_registry_hash": CONCEPT_REGISTRY_HASH,
        "taxonomy_namespace": "us-gaap",
        "taxonomy_version": taxonomy_version,
        "network_state": "denied",
        "synthetic_only": True,
        "mappings": mappings,
        "review_decision_ref": review_decision_ref,
        "review_decision_hash": review_decision_hash,
    }
    return finalize_artifact(
        value,
        hash_field="mapping_hash",
        schema_filename="m9-i5-concept-mapping-policy.schema.json",
    )


def require_mapping_policy(value: Mapping[str, Any]) -> None:
    """Reject coherent retyping, reordering, or alternate tag priority authority."""

    require_self_hash(value, "mapping_hash")
    expected = build_mapping_policy(
        taxonomy_version=value.get("taxonomy_version", ""),
        review_decision_ref=value.get("review_decision_ref", ""),
        review_decision_hash=value.get("review_decision_hash", ""),
    )
    if dict(value) != expected:
        raise NormalizationError("NORM-CONCEPT-UNMAPPED", "mapping policy differs from lock")


def standard_authority(value: Mapping[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    """Return exact namespace/local-name authorities after policy verification."""

    require_mapping_policy(value)
    authority: dict[tuple[str, str], dict[str, Any]] = {}
    concepts = []
    for mapping in value["mappings"]:
        concepts.append(mapping["concept_id"])
        for source_tag in mapping["source_tags"].values():
            key = (source_tag["namespace"], source_tag["local_name"])
            if key in authority:
                raise NormalizationError("NORM-CONCEPT-DUPLICATE", "tag authority is duplicate")
            authority[key] = dict(mapping)
    if tuple(concepts) != CONCEPT_IDS:
        raise NormalizationError("NORM-CONCEPT-UNMAPPED", "concept order differs from lock")
    return authority


def custom_authority(
    decisions: Sequence[Mapping[str, Any]],
    *,
    mapping_hash: str,
    company_cik: str,
    taxonomy_version: str,
) -> dict[tuple[str, str, str], dict[str, Any]]:
    """Build exact-company/fact custom authorities; never generalize a human decision."""

    authority: dict[tuple[str, str, str], dict[str, Any]] = {}
    for decision in decisions:
        validate_schema(decision, "m9-i5-custom-tag-decision.schema.json")
        require_self_hash(decision, "decision_hash")
        if (
            decision.get("mapping_hash") != mapping_hash
            or decision.get("company_cik") != company_cik
            or decision.get("taxonomy_version") != taxonomy_version
            or decision.get("reviewer_actor_type") != "human"
            or decision.get("decision") != "approved"
            or decision.get("network_state") != "denied"
            or decision.get("synthetic_only") is not True
        ):
            continue
        key = (
            decision["custom_namespace"],
            decision["custom_local_name"],
            decision["source_fact_hash"],
        )
        if key in authority:
            raise NormalizationError("NORM-CONCEPT-DUPLICATE", "custom authority is duplicate")
        authority[key] = dict(decision)
    return authority


__all__ = [
    "build_mapping_policy",
    "custom_authority",
    "require_mapping_policy",
    "standard_authority",
]
