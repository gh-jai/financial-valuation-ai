"""Disabled-offline US-GAAP normalization runtime for the M9-I5 checkpoint."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any

from .canonical import CANONICALIZATION_VERSION, canonical_sha256
from .gaap_contracts import (
    CONCEPT_IDS,
    CONTRACT_HASH,
    SCHEMA_VERSION,
    NormalizationError,
    deterministic_id,
    finalize_artifact,
    require_raw_fact,
    require_self_hash,
    safe_finding,
    scale_and_apply_polarity,
)
from .gaap_mapping import build_mapping_policy, custom_authority, standard_authority
from .period_graph import build_period_graph
from .reconciliation import reconcile

_FIXTURE_FIELDS = frozenset(
    {
        "fixture_version",
        "fixture_id",
        "contract_hash",
        "network_state",
        "synthetic_only",
        "taxonomy_version",
        "source_snapshot",
        "source_snapshot_hash",
        "mapping_review",
        "facts",
        "requested_period_edges",
        "custom_tag_decisions",
        "corporate_actions",
        "fixture_hash",
    }
)
_SNAPSHOT_FIELDS = frozenset(
    {"snapshot_id", "company_cik", "record_refs", "network_state", "synthetic_only"}
)
_REVIEW_FIELDS = frozenset(
    {
        "review_decision_ref",
        "reviewer_actor_id",
        "reviewer_actor_type",
        "reviewed_at",
        "decision",
        "synthetic_only",
        "review_hash",
    }
)


def _require_fixture_surface(value: Mapping[str, Any]) -> None:
    if set(value) != _FIXTURE_FIELDS:
        raise NormalizationError("NORM-AUTHORITY-DENIED", "fixture surface is not locked")
    if (
        value.get("fixture_version") != "0.1.0"
        or value.get("contract_hash") != CONTRACT_HASH
        or value.get("network_state") != "denied"
        or value.get("synthetic_only") is not True
    ):
        raise NormalizationError("NORM-AUTHORITY-DENIED", "fixture authority is denied")
    if not isinstance(value.get("taxonomy_version"), str) or not re.fullmatch(
        r"[0-9]{4}", value["taxonomy_version"]
    ):
        raise NormalizationError("NORM-AUTHORITY-DENIED", "taxonomy version is invalid")
    require_self_hash(value, "fixture_hash")
    snapshot = value.get("source_snapshot")
    if not isinstance(snapshot, dict) or set(snapshot) != _SNAPSHOT_FIELDS:
        raise NormalizationError("NORM-REFERENCE-MISSING", "source snapshot is invalid")
    if (
        snapshot.get("network_state") != "denied"
        or snapshot.get("synthetic_only") is not True
        or value.get("source_snapshot_hash") != canonical_sha256(snapshot)
    ):
        raise NormalizationError("NORM-HASH-MISMATCH", "source snapshot authority does not close")
    if not isinstance(snapshot.get("snapshot_id"), str) or not re.fullmatch(
        r"SNP-[A-Z0-9-]+", snapshot["snapshot_id"]
    ):
        raise NormalizationError("NORM-REFERENCE-MISSING", "snapshot ID is invalid")
    if not isinstance(snapshot.get("company_cik"), str) or not re.fullmatch(
        r"[0-9]{10}", snapshot["company_cik"]
    ):
        raise NormalizationError("NORM-REFERENCE-MISSING", "synthetic CIK is invalid")
    review = value.get("mapping_review")
    if not isinstance(review, dict) or set(review) != _REVIEW_FIELDS:
        raise NormalizationError("NORM-AUTHORITY-DENIED", "mapping review is invalid")
    require_self_hash(review, "review_hash")
    if (
        review.get("reviewer_actor_type") != "human"
        or review.get("decision") != "approved"
        or review.get("synthetic_only") is not True
        or not isinstance(review.get("review_decision_ref"), str)
        or not re.fullmatch(r"MREV-[A-Z0-9-]+", review["review_decision_ref"])
        or not isinstance(review.get("reviewer_actor_id"), str)
        or not re.fullmatch(r"HUMAN-[A-Z0-9-]+", review["reviewer_actor_id"])
        or not isinstance(review.get("reviewed_at"), str)
        or not re.fullmatch(
            r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z",
            review["reviewed_at"],
        )
    ):
        raise NormalizationError("NORM-AUTHORITY-DENIED", "mapping review is not approved")
    if not isinstance(value.get("facts"), list) or not value["facts"]:
        raise NormalizationError("NORM-MATERIAL-MISSING", "source facts are missing")
    for fact in value["facts"]:
        require_raw_fact(fact)
    if not isinstance(value.get("requested_period_edges"), list):
        raise NormalizationError("NORM-PERIOD-AMBIGUOUS", "period edges are invalid")
    if not isinstance(value.get("custom_tag_decisions"), list):
        raise NormalizationError("NORM-AUTHORITY-DENIED", "custom decisions are invalid")
    if value.get("corporate_actions") != []:
        raise NormalizationError("NORM-SPLIT-AMBIGUOUS", "corporate actions are not approved")
    record_refs = snapshot.get("record_refs")
    if not isinstance(record_refs, list) or sorted(set(record_refs)) != record_refs:
        raise NormalizationError("NORM-REFERENCE-MISSING", "snapshot record references are invalid")
    if any(fact["filing_record_ref"] not in record_refs for fact in value["facts"]):
        raise NormalizationError("NORM-REFERENCE-MISSING", "source record reference does not close")


def _period_for_fact(fact: Mapping[str, Any], graph: Mapping[str, Any]) -> Mapping[str, Any]:
    matches = [
        node
        for node in graph["nodes"]
        if node["start"] == fact["start"]
        and node["end"] == fact["end"]
        and node["fiscal_year"] == fact["fiscal_year"]
        and node["fiscal_period"] == fact["fiscal_period"]
        and node["filing_record_ref"] == fact["filing_record_ref"]
        and node["accession"] == fact["accession"]
        and node["filed_at"] == fact["filed_at"]
        and node["amendment_of_accession"] == fact["amendment_of_accession"]
    ]
    if len(matches) != 1:
        raise NormalizationError("NORM-PERIOD-AMBIGUOUS", "fact period is ambiguous")
    return matches[0]


def _fact_candidate(
    raw: Mapping[str, Any],
    period: Mapping[str, Any],
    mapping: Mapping[str, Any],
    custom_decision: Mapping[str, Any] | None,
) -> dict[str, Any]:
    expected_duration = mapping["period_type"] == "duration"
    if expected_duration != (period["basis"] != "instant"):
        raise NormalizationError("NORM-PERIOD-AMBIGUOUS", "concept period type disagrees")
    if raw["unit"] != mapping["allowed_unit"]:
        raise NormalizationError("NORM-UNIT-SCALE", "concept unit disagrees with mapping")
    value = scale_and_apply_polarity(raw["value_decimal"], raw["scale"], mapping["polarity"])
    provenance = "custom_tag" if custom_decision is not None else "filing_fact"
    subject = {
        "concept_id": mapping["concept_id"],
        "value_decimal": value,
        "period_id": period["period_id"],
        "source_fact_refs": [raw["source_fact_id"]],
    }
    return {
        "fact_id": deterministic_id("FACT", subject),
        "concept_id": mapping["concept_id"],
        "value_decimal": value,
        "unit": raw["unit"],
        "currency": raw["currency"],
        "period_id": period["period_id"],
        "provenance_kind": provenance,
        "source_fact_refs": [raw["source_fact_id"]],
        "calculation_rule": None,
        "custom_mapping_decision_ref": (
            custom_decision["decision_id"] if custom_decision is not None else None
        ),
        "review_status": "approved",
    }


def _normalize_facts(
    raw_facts: Sequence[Mapping[str, Any]],
    mapping_policy: Mapping[str, Any],
    graph: Mapping[str, Any],
    custom_decisions: Sequence[Mapping[str, Any]],
    *,
    company_cik: str,
    taxonomy_version: str,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], bool]:
    standard = standard_authority(mapping_policy)
    custom = custom_authority(
        custom_decisions,
        mapping_hash=mapping_policy["mapping_hash"],
        company_cik=company_cik,
        taxonomy_version=taxonomy_version,
    )
    candidates: dict[tuple[Any, ...], dict[str, Any]] = {}
    authority_index: dict[tuple[Any, ...], tuple[Any, ...]] = {}
    conflicted_authorities: set[tuple[Any, ...]] = set()
    findings: list[dict[str, Any]] = []
    duplicate_conflict = False
    for raw in sorted(raw_facts, key=lambda item: item["source_fact_id"]):
        period = _period_for_fact(raw, graph)
        if period["selection_status"] == "superseded":
            continue
        custom_decision = None
        mapping = standard.get((raw["namespace"], raw["local_name"]))
        if mapping is None and raw["namespace"].startswith("synthetic:"):
            custom_decision = custom.get(
                (raw["namespace"], raw["local_name"], raw["source_fact_hash"])
            )
            if custom_decision is not None:
                mapping = {
                    "concept_id": custom_decision["concept_id"],
                    "allowed_unit": custom_decision["unit"],
                    "period_type": custom_decision["period_type"],
                    "polarity": custom_decision["polarity"],
                }
        if mapping is None:
            code = (
                "NORM-CUSTOM-TAG-REVIEW"
                if raw["namespace"].startswith("synthetic:")
                else "NORM-CONCEPT-UNMAPPED"
            )
            severity = "blocking" if raw["material"] else "review"
            findings.append(
                safe_finding(
                    code, severity, "Exact concept authority is unavailable", raw["source_fact_id"]
                )
            )
            continue
        try:
            candidate = _fact_candidate(raw, period, mapping, custom_decision)
        except NormalizationError as exc:
            findings.append(
                safe_finding(
                    exc.code,
                    "blocking",
                    "Source fact violates normalization rules",
                    raw["source_fact_id"],
                )
            )
            continue
        authority_key = (
            candidate["concept_id"],
            raw["start"],
            raw["end"],
            raw["fiscal_year"],
            raw["fiscal_period"],
            candidate["unit"],
            tuple(sorted(raw["dimensions"].items())),
        )
        key = (
            candidate["concept_id"],
            candidate["period_id"],
            candidate["unit"],
            tuple(sorted(raw["dimensions"].items())),
            raw["accession"],
        )
        if authority_key in conflicted_authorities:
            findings.append(
                safe_finding(
                    "NORM-AMENDMENT-CONFLICT",
                    "blocking",
                    "Selected filing lineages conflict",
                    raw["source_fact_id"],
                )
            )
            continue
        prior_key = authority_index.get(authority_key)
        if prior_key is not None and prior_key[-1] != raw["accession"]:
            prior = candidates.pop(prior_key)
            authority_index.pop(authority_key)
            conflicted_authorities.add(authority_key)
            findings.append(
                safe_finding(
                    "NORM-AMENDMENT-CONFLICT",
                    "blocking",
                    "Selected filing lineages conflict",
                    *prior["source_fact_refs"],
                    raw["source_fact_id"],
                )
            )
            continue
        prior = candidates.get(key)
        if prior is None:
            candidates[key] = candidate
            authority_index[authority_key] = key
        elif (
            prior["value_decimal"] == candidate["value_decimal"]
            and prior["custom_mapping_decision_ref"] == candidate["custom_mapping_decision_ref"]
        ):
            refs = sorted([*prior["source_fact_refs"], *candidate["source_fact_refs"]])
            prior["source_fact_refs"] = refs
            prior["fact_id"] = deterministic_id(
                "FACT",
                {
                    "concept_id": prior["concept_id"],
                    "value_decimal": prior["value_decimal"],
                    "period_id": prior["period_id"],
                    "source_fact_refs": refs,
                },
            )
        else:
            duplicate_conflict = True
            findings.append(
                safe_finding(
                    "NORM-DUPLICATE-CONFLICT",
                    "blocking",
                    "Duplicate source facts disagree",
                    *prior["source_fact_refs"],
                    *candidate["source_fact_refs"],
                )
            )
            del candidates[key]
            authority_index.pop(authority_key, None)
            conflicted_authorities.add(authority_key)
    facts = sorted(candidates.values(), key=lambda item: (item["concept_id"], item["period_id"]))
    return (
        facts,
        sorted(findings, key=lambda item: (item["code"], item["subject_refs"])),
        duplicate_conflict,
    )


def normalize_fixture(value: Mapping[str, Any]) -> dict[str, Any]:
    """Normalize one exact synthetic fixture without touching an adapter or network surface."""

    _require_fixture_surface(value)
    review = value["mapping_review"]
    mapping = build_mapping_policy(
        taxonomy_version=value["taxonomy_version"],
        review_decision_ref=review["review_decision_ref"],
        review_decision_hash=review["review_hash"],
    )
    graph = build_period_graph(
        value["facts"],
        source_snapshot_id=value["source_snapshot"]["snapshot_id"],
        source_snapshot_hash=value["source_snapshot_hash"],
        mapping_id=mapping["mapping_id"],
        mapping_hash=mapping["mapping_hash"],
        requested_edges=value["requested_period_edges"],
    )
    facts, findings, duplicate_conflict = _normalize_facts(
        value["facts"],
        mapping,
        graph,
        value["custom_tag_decisions"],
        company_cik=value["source_snapshot"]["company_cik"],
        taxonomy_version=value["taxonomy_version"],
    )
    if not facts:
        raise NormalizationError("NORM-MATERIAL-MISSING", "no normalized fact can be emitted")
    represented = {fact["concept_id"] for fact in facts}
    for concept_id in CONCEPT_IDS:
        if concept_id not in represented:
            findings.append(
                safe_finding(
                    "NORM-MATERIAL-MISSING",
                    "blocking",
                    "Required concept is missing",
                    f"CONCEPT-{concept_id.upper()}",
                )
            )
    findings = sorted(findings, key=lambda item: (item["code"], item["subject_refs"]))
    reconciliations, quality = reconcile(
        facts, findings, graph, duplicate_conflict=duplicate_conflict
    )
    identity = {
        "source_snapshot_hash": value["source_snapshot_hash"],
        "mapping_hash": mapping["mapping_hash"],
        "period_graph_hash": graph["period_graph_hash"],
        "facts": facts,
        "reconciliations": reconciliations,
        "findings": findings,
        "quality": quality,
    }
    result = {
        "schema_version": SCHEMA_VERSION,
        "canonicalization_version": CANONICALIZATION_VERSION,
        "normalization_id": deterministic_id("NRM", identity),
        "source_snapshot_id": value["source_snapshot"]["snapshot_id"],
        "source_snapshot_hash": value["source_snapshot_hash"],
        "mapping_id": mapping["mapping_id"],
        "mapping_hash": mapping["mapping_hash"],
        "period_graph_id": graph["period_graph_id"],
        "period_graph_hash": graph["period_graph_hash"],
        "company_cik": value["source_snapshot"]["company_cik"],
        "network_state": "denied",
        "synthetic_only": True,
        "facts": facts,
        "reconciliations": reconciliations,
        "findings": findings,
        "quality": quality,
    }
    result = finalize_artifact(
        result,
        hash_field="normalization_hash",
        schema_filename="m9-i5-normalization-result.schema.json",
    )
    return {
        "fixture_hash": value["fixture_hash"],
        "mapping": mapping,
        "period_graph": graph,
        "normalization_result": result,
    }


__all__ = ["normalize_fixture"]
