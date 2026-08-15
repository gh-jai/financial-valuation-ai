"""Fail-closed reconciliation and quality-state construction for M9-I5."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from .gaap_contracts import CONCEPT_IDS, RECONCILIATION_FAMILIES


def _not_applicable(check_type: str, reason: str) -> dict[str, Any]:
    token = check_type.upper()
    return {
        "check_id": f"RECCHK-{token}-NOT-APPLICABLE",
        "check_type": check_type,
        "applicability": "not_applicable",
        "status": "not_applicable",
        "difference_decimal": None,
        "tolerance_decimal": "0",
        "fact_refs": [],
        "message_code": f"NORM-{token}-NOT-APPLICABLE",
        "exclusion_reason_code": reason,
    }


def _applicable(
    check_type: str, fact_refs: Sequence[str], *, passed: bool, message_code: str
) -> dict[str, Any]:
    return {
        "check_id": f"RECCHK-{check_type.upper()}-EXACT",
        "check_type": check_type,
        "applicability": "applicable",
        "status": "passed" if passed else "failed",
        "difference_decimal": "0" if passed else "1",
        "tolerance_decimal": "0",
        "fact_refs": sorted(set(fact_refs)),
        "message_code": message_code,
        "exclusion_reason_code": None,
    }


def reconcile(
    facts: Sequence[Mapping[str, Any]],
    findings: Sequence[Mapping[str, Any]],
    graph: Mapping[str, Any],
    *,
    duplicate_conflict: bool,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Cover every locked family and derive the only valid quality state."""

    fact_refs = [fact["fact_id"] for fact in facts]
    by_concept = {fact["concept_id"]: fact for fact in facts}
    blocking_codes = sorted(
        {finding["code"] for finding in findings if finding["severity"] == "blocking"}
    )
    review_codes = sorted(
        {finding["code"] for finding in findings if finding["severity"] == "review"}
    )
    missing = [concept for concept in CONCEPT_IDS if concept not in by_concept]
    all_approved = all(fact["review_status"] == "approved" for fact in facts)
    unit_passed = all(
        (fact["unit"] == "USD" and fact["currency"] == "USD")
        or (fact["unit"] in {"ratio", "shares"} and fact["currency"] is None)
        for fact in facts
    )
    currency_refs = [fact["fact_id"] for fact in facts if fact["unit"] == "USD"]
    custom_refs = [fact["fact_id"] for fact in facts if fact["provenance_kind"] == "custom_tag"]
    amendment_edges = [
        edge for edge in graph["edges"] if edge["relationship"] == "amendment-supersedes"
    ]
    split_edges = [edge for edge in graph["edges"] if edge["relationship"] == "split-adjustment"]
    rollup_edges = [
        edge
        for edge in graph["edges"]
        if edge["relationship"]
        in {"quarter-to-ytd", "ytd-to-annual", "annual-rollup", "ttm-composition"}
    ]

    entries = [
        _not_applicable("balance-sheet", "NORM-NO-BALANCE-SHEET-EQUATION-INPUT"),
        _not_applicable("cash-flow", "NORM-NO-CASH-FLOW-EQUATION-INPUT"),
        (
            _applicable(
                "annual-quarterly",
                fact_refs,
                passed=True,
                message_code="NORM-ANNUAL-QUARTERLY-PASS",
            )
            if rollup_edges
            else _not_applicable("annual-quarterly", "NORM-NO-PERIOD-ROLLUP")
        ),
        _applicable(
            "unit-scale",
            fact_refs,
            passed=unit_passed,
            message_code=("NORM-UNIT-SCALE-PASS" if unit_passed else "NORM-UNIT-SCALE"),
        ),
        _applicable(
            "currency",
            currency_refs or fact_refs,
            passed=unit_passed,
            message_code=("NORM-CURRENCY-PASS" if unit_passed else "NORM-UNIT-SCALE"),
        ),
        (
            _applicable(
                "shares-split",
                fact_refs,
                passed=False,
                message_code="NORM-SPLIT-AMBIGUOUS",
            )
            if split_edges
            else _not_applicable("shares-split", "NORM-NO-CORPORATE-ACTION")
        ),
        (
            _applicable(
                "amendment",
                fact_refs,
                passed=True,
                message_code="NORM-AMENDMENT-PASS",
            )
            if amendment_edges
            else _not_applicable("amendment", "NORM-NO-AMENDMENT")
        ),
        _applicable(
            "duplicate-fact",
            fact_refs,
            passed=not duplicate_conflict,
            message_code=(
                "NORM-DUPLICATE-FACT-PASS" if not duplicate_conflict else "NORM-DUPLICATE-CONFLICT"
            ),
        ),
        (
            _applicable(
                "custom-tag",
                custom_refs,
                passed=all(
                    by_concept[fact["concept_id"]]["review_status"] == "approved"
                    for fact in facts
                    if fact["fact_id"] in custom_refs
                ),
                message_code="NORM-CUSTOM-TAG-PASS",
            )
            if custom_refs
            else _not_applicable("custom-tag", "NORM-NO-CUSTOM-TAGS")
        ),
        _applicable(
            "fcff-completeness",
            fact_refs,
            passed=not missing and all_approved and not blocking_codes and not review_codes,
            message_code=(
                "NORM-FCFF-COMPLETENESS-PASS"
                if not missing and all_approved and not blocking_codes and not review_codes
                else "NORM-MATERIAL-MISSING"
            ),
        ),
    ]
    assert tuple(entry["check_type"] for entry in entries) == RECONCILIATION_FAMILIES
    failed = any(entry["status"] == "failed" for entry in entries)
    if blocking_codes or failed:
        status = "unsupported"
    elif review_codes or not all_approved:
        status = "needs_review"
    else:
        status = "complete"
    quality = {
        "status": status,
        "material_missing_concepts": missing,
        "blocking_codes": blocking_codes,
        "review_codes": review_codes,
    }
    return entries, quality


__all__ = ["reconcile"]
