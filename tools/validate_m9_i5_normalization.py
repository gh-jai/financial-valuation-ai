"""Independent validator for exact M9-I5 synthetic normalization bundles."""

from __future__ import annotations

import argparse
import ast
import copy
import hashlib
import json
import re
from datetime import date
from decimal import Decimal, localcontext
from itertools import pairwise
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"
CANONICALIZATION_VERSION = "fvi-canonical-json-v1"
CONCEPT_REGISTRY_HASH = "6d4e0331a709e2b4152fd6e846bfe84cb22978cc3bd0de19599e80847edb7fa9"
CONTRACT_HASH = "99ee481383eece5d21f45e22dc2ced16f3e04f3bd8ae169ac7c58279c8121949"
CONCEPTS = (
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
FAMILIES = (
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
EXPECTED = {
    "revenue": ("monetary", "USD", "duration", 1),
    "operating-income": ("monetary", "USD", "duration", 1),
    "statutory-tax-rate": ("rate", "ratio", "duration", 1),
    "cash-taxes": ("monetary", "USD", "duration", 1),
    "depreciation-amortization": ("monetary", "USD", "duration", 1),
    "capital-expenditure": ("monetary", "USD", "duration", -1),
    "noncash-working-capital": ("monetary", "USD", "instant", 1),
    "debt": ("monetary", "USD", "instant", 1),
    "cash": ("monetary", "USD", "instant", 1),
    "nonoperating-assets": ("monetary", "USD", "instant", 1),
    "minority-interest": ("monetary", "USD", "instant", 1),
    "other-claims": ("monetary", "USD", "instant", 1),
    "diluted-shares": ("shares", "shares", "duration", 1),
}
EXPECTED_TAGS = {
    "revenue": ("RevenueFromContractWithCustomerExcludingAssessedTax",),
    "operating-income": ("OperatingIncomeLoss",),
    "statutory-tax-rate": ("EffectiveIncomeTaxRateReconciliationAtFederalStatutoryIncomeTaxRate",),
    "cash-taxes": ("IncomeTaxesPaidNet",),
    "depreciation-amortization": ("DepreciationDepletionAndAmortization",),
    "capital-expenditure": ("PaymentsToAcquirePropertyPlantAndEquipment",),
    "noncash-working-capital": ("WorkingCapital",),
    "debt": ("LongTermDebtAndFinanceLeaseObligations",),
    "cash": ("CashAndCashEquivalentsAtCarryingValue",),
    "nonoperating-assets": ("ShortTermInvestments",),
    "minority-interest": ("NoncontrollingInterestInConsolidatedEntity",),
    "other-claims": ("OperatingLeaseLiabilityNoncurrent",),
    "diluted-shares": ("WeightedAverageNumberOfDilutedSharesOutstanding",),
}
DECIMAL_PATTERN = re.compile(
    r"^(?:0|-?(?:[1-9][0-9]*)(?:\.[0-9]*[1-9])?|0\.[0-9]*[1-9]|-0\.[0-9]*[1-9])$"
)
IMPLEMENTATION_FILES = (
    "gaap_contracts.py",
    "gaap_mapping.py",
    "period_graph.py",
    "normalization.py",
    "reconciliation.py",
)
BANNED_IMPORTS = {
    "aiohttp",
    "httpx",
    "requests",
    "socket",
    "subprocess",
    "urllib",
    "sec_adapters",
    "sec_endpoints",
}
BANNED_CALLS = {"eval", "exec", "compile", "__import__"}


class DuplicateKey(ValueError):
    pass


def _unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKey(key)
        result[key] = value
    return result


def strict_json(path: Path) -> dict[str, Any]:
    value = json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=_unique,
        parse_constant=lambda token: (_ for _ in ()).throw(ValueError(token)),
    )
    if not isinstance(value, dict):
        raise TypeError("root must be object")
    return value


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def digest(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def deterministic_id(prefix: str, subject: Any) -> str:
    return f"{prefix}-{digest(subject)[:24].upper()}"


def self_hash(value: dict[str, Any], field: str) -> str:
    return digest({key: copy.deepcopy(item) for key, item in value.items() if key != field})


def decimal_text(value: Decimal) -> str:
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return "0" if text in {"", "-0"} else text


def parsed_date(value: Any) -> date | None:
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        return None


def finding(code: str, message: str, *refs: str) -> dict[str, Any]:
    return {
        "code": code,
        "severity": "blocking",
        "message": message,
        "subject_refs": sorted(set(refs)) or ["BUNDLE-M9-I5"],
    }


def _schema_errors(value: dict[str, Any], filename: str) -> list[dict[str, Any]]:
    schema = strict_json(SCHEMAS / filename)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    if next(validator.iter_errors(value), None) is None:
        return []
    return [finding("NORM-AUTHORITY-DENIED", f"{filename} schema validation failed")]


def _fixture_errors(fixture: dict[str, Any]) -> list[dict[str, Any]]:
    errors = []
    if (
        fixture.get("contract_hash") != CONTRACT_HASH
        or fixture.get("network_state") != "denied"
        or fixture.get("synthetic_only") is not True
    ):
        errors.append(finding("NORM-AUTHORITY-DENIED", "fixture authority mismatch"))
    snapshot = fixture.get("source_snapshot", {})
    if snapshot.get("network_state") != "denied" or snapshot.get("synthetic_only") is not True:
        errors.append(finding("NORM-AUTHORITY-DENIED", "snapshot authority mismatch"))
    record_refs = snapshot.get("record_refs", [])
    if record_refs != sorted(set(record_refs)):
        errors.append(finding("NORM-REFERENCE-MISSING", "snapshot records are noncanonical"))
    facts = fixture.get("facts", [])
    fact_ids = [raw.get("source_fact_id") for raw in facts]
    if len(fact_ids) != len(set(fact_ids)):
        errors.append(finding("NORM-CONCEPT-DUPLICATE", "source fact IDs are duplicate"))
    for raw in facts:
        if raw.get("synthetic") is not True or raw.get("filing_record_ref") not in record_refs:
            errors.append(
                finding(
                    "NORM-REFERENCE-MISSING",
                    "source fact authority does not close",
                    raw.get("source_fact_id", "RAW-INVALID"),
                )
            )
        lexical = raw.get("value_decimal")
        if not isinstance(lexical, str) or not DECIMAL_PATTERN.fullmatch(lexical):
            errors.append(
                finding(
                    "NORM-UNIT-SCALE",
                    "source decimal is noncanonical",
                    raw.get("source_fact_id", "RAW-INVALID"),
                )
            )
    return errors


def _hash_errors(fixture: dict[str, Any], bundle: dict[str, Any]) -> list[dict[str, Any]]:
    errors = []
    subjects = (
        (fixture, "fixture_hash", "FIXTURE-M9-I5"),
        (bundle["mapping"], "mapping_hash", bundle["mapping"]["mapping_id"]),
        (bundle["period_graph"], "period_graph_hash", bundle["period_graph"]["period_graph_id"]),
        (
            bundle["normalization_result"],
            "normalization_hash",
            bundle["normalization_result"]["normalization_id"],
        ),
    )
    for subject, field, reference in subjects:
        if subject.get(field) != self_hash(subject, field):
            errors.append(finding("NORM-HASH-MISMATCH", f"{field} mismatch", reference))
    if fixture.get("source_snapshot_hash") != digest(fixture.get("source_snapshot")):
        errors.append(finding("NORM-HASH-MISMATCH", "source snapshot hash mismatch"))
    review = fixture.get("mapping_review", {})
    if review.get("review_hash") != self_hash(review, "review_hash"):
        errors.append(finding("NORM-HASH-MISMATCH", "mapping review hash mismatch"))
    for raw in fixture.get("facts", []):
        if raw.get("source_fact_hash") != self_hash(raw, "source_fact_hash"):
            errors.append(
                finding(
                    "NORM-HASH-MISMATCH",
                    "source fact hash mismatch",
                    raw.get("source_fact_id", "RAW-INVALID"),
                )
            )
    return errors


def _mapping_errors(fixture: dict[str, Any], mapping: dict[str, Any]) -> list[dict[str, Any]]:
    errors = []
    if mapping.get("concept_registry_hash") != CONCEPT_REGISTRY_HASH:
        errors.append(finding("NORM-HASH-MISMATCH", "concept registry hash mismatch"))
    review = fixture.get("mapping_review", {})
    if (
        mapping.get("review_decision_ref") != review.get("review_decision_ref")
        or mapping.get("review_decision_hash") != review.get("review_hash")
        or review.get("reviewer_actor_type") != "human"
        or review.get("decision") != "approved"
    ):
        errors.append(finding("NORM-AUTHORITY-DENIED", "mapping review evidence mismatch"))
    rows = mapping.get("mappings", [])
    if tuple(row.get("concept_id") for row in rows) != CONCEPTS:
        errors.append(finding("NORM-CONCEPT-UNMAPPED", "concept order mismatch"))
        return errors
    seen_tags = set()
    for row in rows:
        concept = row["concept_id"]
        expected_kind, expected_unit, expected_period, expected_polarity = EXPECTED[concept]
        actual = (row["kind"], row["allowed_unit"], row["period_type"], row["polarity"])
        if actual != (expected_kind, expected_unit, expected_period, expected_polarity):
            errors.append(finding("NORM-CONCEPT-UNMAPPED", "mapping semantics mismatch"))
        if row.get("mapping_status") != "approved":
            errors.append(finding("NORM-AUTHORITY-DENIED", "mapping is not approved"))
        priorities = list(row.get("source_tags", {}))
        if priorities != [f"{index:02d}" for index in range(1, len(priorities) + 1)]:
            errors.append(finding("NORM-CONCEPT-DUPLICATE", "tag priorities are noncanonical"))
        local_names = tuple(tag.get("local_name") for tag in row.get("source_tags", {}).values())
        if local_names != EXPECTED_TAGS[concept]:
            errors.append(finding("NORM-CONCEPT-UNMAPPED", "source tag authority mismatch"))
        for tag in row.get("source_tags", {}).values():
            authority = (tag.get("namespace"), tag.get("local_name"))
            if authority in seen_tags:
                errors.append(finding("NORM-CONCEPT-DUPLICATE", "tag authority is duplicate"))
            seen_tags.add(authority)
    identity = {
        "mapping_version": mapping.get("mapping_version"),
        "taxonomy_version": mapping.get("taxonomy_version"),
        "concept_registry_hash": mapping.get("concept_registry_hash"),
        "mappings": rows,
        "review_decision_ref": mapping.get("review_decision_ref"),
        "review_decision_hash": mapping.get("review_decision_hash"),
    }
    if mapping.get("mapping_id") != deterministic_id("MAP", identity):
        errors.append(finding("NORM-HASH-MISMATCH", "mapping ID is nondeterministic"))
    return errors


def _graph_errors(fixture: dict[str, Any], graph: dict[str, Any]) -> list[dict[str, Any]]:
    errors = []
    nodes = graph.get("nodes", [])
    if nodes != sorted(
        nodes,
        key=lambda item: (
            item.get("end", ""),
            item.get("start") or "",
            item.get("accession", ""),
            item.get("period_id", ""),
        ),
    ):
        errors.append(finding("NORM-PERIOD-AMBIGUOUS", "period node order is noncanonical"))
    if graph.get("edges", []) != sorted(
        graph.get("edges", []), key=lambda item: item.get("edge_id", "")
    ):
        errors.append(finding("NORM-PERIOD-AMBIGUOUS", "period edge order is noncanonical"))
    by_id = {node.get("period_id"): node for node in nodes}
    forms_by_id: dict[str, set[Any]] = {}
    if len(by_id) != len(nodes):
        errors.append(finding("NORM-PERIOD-AMBIGUOUS", "period IDs are duplicate"))
    for node in nodes:
        node_subject = {
            "start": node.get("start"),
            "end": node.get("end"),
            "fiscal_year": node.get("fiscal_year"),
            "fiscal_period": node.get("fiscal_period"),
            "filing_record_ref": node.get("filing_record_ref"),
            "accession": node.get("accession"),
            "filed_at": node.get("filed_at"),
            "amendment_of_accession": node.get("amendment_of_accession"),
        }
        if node.get("period_id") != deterministic_id("PER", node_subject):
            errors.append(finding("NORM-HASH-MISMATCH", "period ID is nondeterministic"))
        raw_forms = {
            raw.get("form")
            for raw in fixture.get("facts", [])
            if all(
                raw.get(field) == node.get(field)
                for field in (
                    "start",
                    "end",
                    "fiscal_year",
                    "fiscal_period",
                    "filing_record_ref",
                    "accession",
                    "filed_at",
                    "amendment_of_accession",
                )
            )
        }
        forms_by_id[node.get("period_id", "PER-INVALID")] = raw_forms
        if len(raw_forms) != 1:
            errors.append(finding("NORM-PERIOD-AMBIGUOUS", "period form family mismatch"))
        if node.get("basis") == "instant":
            if node.get("start") is not None or node.get("duration_days") is not None:
                errors.append(finding("NORM-PERIOD-AMBIGUOUS", "instant duration mismatch"))
        else:
            try:
                start = date.fromisoformat(node["start"])
                end = date.fromisoformat(node["end"])
                days = (end - start).days + 1
            except (KeyError, TypeError, ValueError):
                days = -1
            if days <= 1 or node.get("duration_days") != days:
                errors.append(finding("NORM-PERIOD-AMBIGUOUS", "duration day count mismatch"))
    adjacency = {node_id: [] for node_id in by_id}
    amendment_sources: list[str] = []
    for edge in graph.get("edges", []):
        targets = [*edge.get("from_period_ids", []), edge.get("to_period_id")]
        if any(target not in by_id for target in targets):
            errors.append(finding("NORM-REFERENCE-MISSING", "period edge is orphaned"))
            continue
        for source in edge["from_period_ids"]:
            adjacency[source].append(edge["to_period_id"])
        if edge.get("relationship") == "amendment-supersedes":
            amendment_sources.extend(edge.get("from_period_ids", []))
            edge_subject = {"from": edge["from_period_ids"][0], "to": edge["to_period_id"]}
        else:
            edge_subject = {
                "relationship": edge.get("relationship"),
                "from": edge.get("from_period_ids"),
                "to": edge.get("to_period_id"),
            }
        if edge.get("edge_id") != deterministic_id("PEDGE", edge_subject):
            errors.append(finding("NORM-HASH-MISMATCH", "period edge ID is nondeterministic"))
        if not _edge_semantics(edge, by_id, forms_by_id):
            errors.append(finding("NORM-PERIOD-AMBIGUOUS", "period edge semantics mismatch"))
    if len(amendment_sources) != len(set(amendment_sources)):
        errors.append(finding("NORM-AMENDMENT-CONFLICT", "amendment lineage forks"))
    state: dict[str, int] = {}

    def visit(node_id: str) -> bool:
        if state.get(node_id) == 1:
            return False
        if state.get(node_id) == 2:
            return True
        state[node_id] = 1
        if not all(visit(target) for target in adjacency[node_id]):
            return False
        state[node_id] = 2
        return True

    if not all(visit(node_id) for node_id in adjacency):
        errors.append(finding("NORM-PERIOD-AMBIGUOUS", "period graph contains a cycle"))
    identity = {
        "source_snapshot_hash": graph.get("source_snapshot_hash"),
        "mapping_hash": graph.get("mapping_hash"),
        "nodes": nodes,
        "edges": graph.get("edges", []),
    }
    if graph.get("period_graph_id") != deterministic_id("PGR", identity):
        errors.append(finding("NORM-HASH-MISMATCH", "period graph ID is nondeterministic"))
    return errors


def _edge_semantics(
    edge: dict[str, Any], nodes: dict[str, dict[str, Any]], forms: dict[str, set[Any]]
) -> bool:
    try:
        sources = [nodes[source_id] for source_id in edge["from_period_ids"]]
        target = nodes[edge["to_period_id"]]
    except KeyError:
        return False
    relationship = edge.get("relationship")
    if relationship == "amendment-supersedes":
        return (
            len(sources) == 1
            and sources[0].get("selection_status") == "superseded"
            and target.get("selection_status") == "selected"
            and target.get("amendment_of_accession") == sources[0].get("accession")
            and sources[0].get("start") == target.get("start")
            and sources[0].get("end") == target.get("end")
            and forms.get(sources[0].get("period_id")) == forms.get(target.get("period_id"))
        )
    if relationship == "prior-instant-to-current":
        source_end = parsed_date(sources[0].get("end")) if len(sources) == 1 else None
        target_end = parsed_date(target.get("end"))
        return (
            len(sources) == 1
            and sources[0].get("basis") == target.get("basis") == "instant"
            and source_end is not None
            and target_end is not None
            and source_end < target_end
        )
    if relationship == "quarter-to-ytd":
        return (
            len(sources) == 1
            and sources[0].get("basis") == "quarterly"
            and target.get("basis") == "year-to-date"
            and sources[0].get("end") == target.get("end")
        )
    if relationship == "ytd-to-annual":
        return (
            len(sources) == 1
            and sources[0].get("basis") == "year-to-date"
            and target.get("basis") == "annual"
            and sources[0].get("end") == target.get("end")
        )
    if relationship in {"annual-rollup", "ttm-composition"}:
        ordered = sorted(sources, key=lambda item: item.get("start") or "")
        boundaries = [
            (parsed_date(left.get("end")), parsed_date(right.get("start")))
            for left, right in pairwise(ordered)
        ]
        return (
            len(ordered) == 4
            and all(node.get("basis") == "quarterly" for node in ordered)
            and target.get("basis") == ("annual" if relationship == "annual-rollup" else "ttm")
            and ordered[0].get("start") == target.get("start")
            and ordered[-1].get("end") == target.get("end")
            and all(
                left_end is not None
                and right_start is not None
                and (right_start - left_end).days == 1
                for left_end, right_start in boundaries
            )
        )
    return False


def _fact_errors(
    fixture: dict[str, Any], mapping: dict[str, Any], graph: dict[str, Any], result: dict[str, Any]
) -> list[dict[str, Any]]:
    errors = []
    raw_by_id = {fact["source_fact_id"]: fact for fact in fixture.get("facts", [])}
    nodes = {node["period_id"]: node for node in graph.get("nodes", [])}
    authority = {}
    for row in mapping.get("mappings", []):
        for tag in row.get("source_tags", {}).values():
            authority[(tag["namespace"], tag["local_name"])] = row
    selected_lineages: dict[tuple[Any, ...], set[str]] = {}
    for raw in fixture.get("facts", []):
        row = authority.get((raw.get("namespace"), raw.get("local_name")))
        if row is None:
            continue
        matching = [
            node
            for node in graph.get("nodes", [])
            if node.get("accession") == raw.get("accession")
            and node.get("start") == raw.get("start")
            and node.get("end") == raw.get("end")
            and node.get("selection_status") == "selected"
        ]
        if len(matching) == 1:
            lineage_key = (
                row.get("concept_id"),
                raw.get("start"),
                raw.get("end"),
                raw.get("unit"),
                tuple(sorted(raw.get("dimensions", {}).items())),
            )
            selected_lineages.setdefault(lineage_key, set()).add(raw.get("accession"))
    if any(len(accessions) > 1 for accessions in selected_lineages.values()):
        errors.append(finding("NORM-AMENDMENT-CONFLICT", "selected filing lineages conflict"))
    decisions = {
        decision.get("decision_id"): decision
        for decision in fixture.get("custom_tag_decisions", [])
    }
    seen = set()
    consumed: set[str] = set()
    emitted_facts = result.get("facts", [])
    if emitted_facts != sorted(
        emitted_facts, key=lambda item: (item.get("concept_id", ""), item.get("period_id", ""))
    ):
        errors.append(finding("NORM-AUTHORITY-DENIED", "normalized fact order is noncanonical"))
    for fact in result.get("facts", []):
        key = (fact.get("concept_id"), fact.get("period_id"))
        if key in seen:
            errors.append(
                finding("NORM-CONCEPT-DUPLICATE", "normalized concept/period is duplicate")
            )
        seen.add(key)
        if fact.get("period_id") not in nodes:
            errors.append(finding("NORM-REFERENCE-MISSING", "normalized period is missing"))
        source_refs = fact.get("source_fact_refs", [])
        if source_refs != sorted(set(source_refs)):
            errors.append(finding("NORM-CONCEPT-DUPLICATE", "source references are noncanonical"))
        if not source_refs or any(reference not in raw_by_id for reference in source_refs):
            errors.append(finding("NORM-REFERENCE-MISSING", "source fact reference is missing"))
            continue
        consumed.update(source_refs)
        expected_values = set()
        for source_ref in source_refs:
            raw = raw_by_id[source_ref]
            row = authority.get((raw["namespace"], raw["local_name"]))
            if fact.get("provenance_kind") == "custom_tag":
                decision = decisions.get(fact.get("custom_mapping_decision_ref"))
                decision_valid = (
                    isinstance(decision, dict)
                    and decision.get("decision_hash") == self_hash(decision, "decision_hash")
                    and decision.get("source_fact_hash") == raw.get("source_fact_hash")
                    and decision.get("mapping_hash") == mapping.get("mapping_hash")
                    and decision.get("company_cik")
                    == fixture.get("source_snapshot", {}).get("company_cik")
                    and decision.get("taxonomy_version") == fixture.get("taxonomy_version")
                    and decision.get("custom_namespace") == raw.get("namespace")
                    and decision.get("custom_local_name") == raw.get("local_name")
                    and decision.get("concept_id") == fact.get("concept_id")
                    and decision.get("reviewer_actor_type") == "human"
                    and decision.get("decision") == "approved"
                )
                if not decision_valid:
                    errors.append(
                        finding("NORM-CUSTOM-TAG-REVIEW", "custom decision mismatch", source_ref)
                    )
                    continue
                row = {
                    "concept_id": decision["concept_id"],
                    "allowed_unit": decision["unit"],
                    "period_type": decision["period_type"],
                    "polarity": decision["polarity"],
                }
            elif row is None:
                errors.append(
                    finding("NORM-CONCEPT-UNMAPPED", "standard source has no mapping", source_ref)
                )
                continue
            if row.get("concept_id") != fact.get("concept_id"):
                errors.append(
                    finding("NORM-CONCEPT-UNMAPPED", "source concept mismatch", source_ref)
                )
            lexical = raw["value_decimal"]
            if not isinstance(lexical, str) or not DECIMAL_PATTERN.fullmatch(lexical):
                errors.append(finding("NORM-UNIT-SCALE", "raw decimal is noncanonical", source_ref))
                continue
            with localcontext() as context:
                context.prec = 384
                expected = Decimal(lexical) * (Decimal(10) ** raw["scale"]) * row["polarity"]
            expected_values.add(decimal_text(expected))
            if fact.get("unit") != row["allowed_unit"]:
                errors.append(finding("NORM-UNIT-SCALE", "normalized unit mismatch", source_ref))
            node = nodes.get(fact.get("period_id"), {})
            if any(
                raw.get(field) != node.get(field)
                for field in (
                    "start",
                    "end",
                    "fiscal_year",
                    "fiscal_period",
                    "filing_record_ref",
                    "accession",
                    "filed_at",
                    "amendment_of_accession",
                )
            ):
                errors.append(
                    finding("NORM-PERIOD-AMBIGUOUS", "source period mismatch", source_ref)
                )
        if len(expected_values) != 1 or fact.get("value_decimal") not in expected_values:
            errors.append(finding("NORM-UNIT-SCALE", "normalized arithmetic mismatch"))
        fact_subject = {
            "concept_id": fact.get("concept_id"),
            "value_decimal": fact.get("value_decimal"),
            "period_id": fact.get("period_id"),
            "source_fact_refs": source_refs,
        }
        if fact.get("fact_id") != deterministic_id("FACT", fact_subject):
            errors.append(finding("NORM-HASH-MISMATCH", "fact ID is nondeterministic"))
    finding_refs = {
        reference
        for item in result.get("findings", [])
        for reference in item.get("subject_refs", [])
    }
    for source_ref, raw in raw_by_id.items():
        matching_nodes = [
            node
            for node in graph.get("nodes", [])
            if all(
                raw.get(field) == node.get(field)
                for field in (
                    "start",
                    "end",
                    "fiscal_year",
                    "fiscal_period",
                    "filing_record_ref",
                    "accession",
                    "filed_at",
                    "amendment_of_accession",
                )
            )
        ]
        superseded = (
            len(matching_nodes) == 1 and matching_nodes[0].get("selection_status") == "superseded"
        )
        if source_ref not in consumed and source_ref not in finding_refs and not superseded:
            errors.append(
                finding("NORM-REFERENCE-MISSING", "source fact has no disposition", source_ref)
            )
    return errors


def _quality_errors(result: dict[str, Any]) -> list[dict[str, Any]]:
    errors = []
    checks = result.get("reconciliations", [])
    expected_findings = sorted(
        result.get("findings", []),
        key=lambda item: (item.get("code", ""), item.get("subject_refs", [])),
    )
    if result.get("findings", []) != expected_findings:
        errors.append(finding("NORM-AUTHORITY-DENIED", "finding order is noncanonical"))
    if tuple(check.get("check_type") for check in checks) != FAMILIES:
        errors.append(
            finding("NORM-RECONCILIATION-FAILED", "reconciliation coverage/order mismatch")
        )
    for check in checks:
        if check.get("applicability") == "not_applicable":
            exact = (
                check.get("status") == "not_applicable"
                and check.get("difference_decimal") is None
                and check.get("tolerance_decimal") == "0"
                and check.get("fact_refs") == []
                and isinstance(check.get("exclusion_reason_code"), str)
            )
        else:
            try:
                difference = abs(Decimal(check.get("difference_decimal")))
                tolerance = Decimal(check.get("tolerance_decimal"))
            except (TypeError, ArithmeticError):
                exact = False
            else:
                exact = (
                    tolerance >= 0
                    and check.get("exclusion_reason_code") is None
                    and bool(check.get("fact_refs"))
                    and (
                        (check.get("status") == "passed" and difference <= tolerance)
                        or (check.get("status") == "failed" and difference > tolerance)
                        or check.get("status") == "review"
                    )
                )
        if not exact:
            errors.append(
                finding("NORM-RECONCILIATION-FAILED", "reconciliation arithmetic mismatch")
            )
    quality = result.get("quality", {})
    concepts = {fact.get("concept_id") for fact in result.get("facts", [])}
    missing = [concept for concept in CONCEPTS if concept not in concepts]
    blocking = sorted(
        {
            item.get("code")
            for item in result.get("findings", [])
            if item.get("severity") == "blocking"
        }
    )
    review = sorted(
        {
            item.get("code")
            for item in result.get("findings", [])
            if item.get("severity") == "review"
        }
    )
    if quality.get("material_missing_concepts") != missing:
        errors.append(finding("NORM-MATERIAL-MISSING", "missing concept list mismatch"))
    if quality.get("blocking_codes") != blocking or quality.get("review_codes") != review:
        errors.append(finding("NORM-AUTHORITY-DENIED", "quality finding codes mismatch"))
    complete = (
        concepts == set(CONCEPTS)
        and all(fact.get("review_status") == "approved" for fact in result.get("facts", []))
        and all(check.get("status") in {"passed", "not_applicable"} for check in checks)
        and not result.get("findings")
        and not quality.get("material_missing_concepts")
        and not quality.get("blocking_codes")
        and not quality.get("review_codes")
    )
    if (quality.get("status") == "complete") != complete:
        errors.append(finding("NORM-RECONCILIATION-FAILED", "quality completeness mismatch"))
    if quality.get("status") == "unsupported" and not quality.get("blocking_codes"):
        errors.append(finding("NORM-AUTHORITY-DENIED", "unsupported state lacks blocking code"))
    identity = {
        "source_snapshot_hash": result.get("source_snapshot_hash"),
        "mapping_hash": result.get("mapping_hash"),
        "period_graph_hash": result.get("period_graph_hash"),
        "facts": result.get("facts"),
        "reconciliations": checks,
        "findings": result.get("findings"),
        "quality": quality,
    }
    if result.get("normalization_id") != deterministic_id("NRM", identity):
        errors.append(finding("NORM-HASH-MISMATCH", "normalization ID is nondeterministic"))
    return errors


def _ast_errors() -> list[dict[str, Any]]:
    errors = []
    package = ROOT / "tools" / "retail_data"
    for filename in IMPLEMENTATION_FILES:
        path = package / filename
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = {alias.name.split(".")[0] for alias in node.names}
                if names & BANNED_IMPORTS:
                    errors.append(finding("NORM-AUTHORITY-DENIED", "banned runtime import"))
            elif isinstance(node, ast.ImportFrom):
                module = (node.module or "").split(".")[-1]
                if module in BANNED_IMPORTS:
                    errors.append(finding("NORM-AUTHORITY-DENIED", "banned runtime import"))
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in BANNED_CALLS:
                    errors.append(finding("NORM-AUTHORITY-DENIED", "dynamic execution is denied"))
            elif isinstance(node, ast.Constant) and isinstance(node.value, float):
                errors.append(finding("NORM-UNIT-SCALE", "runtime float literal is denied"))
    return errors


def validate_bundle(fixture: dict[str, Any], bundle: dict[str, Any]) -> dict[str, Any]:
    """Independently recompute hashes, mappings, graph, facts, checks, and authority."""

    mapping = bundle["mapping"]
    graph = bundle["period_graph"]
    result = bundle["normalization_result"]
    errors = []
    errors.extend(_schema_errors(mapping, "m9-i5-concept-mapping-policy.schema.json"))
    errors.extend(_schema_errors(graph, "m9-i5-period-graph.schema.json"))
    errors.extend(_schema_errors(result, "m9-i5-normalization-result.schema.json"))
    for decision in fixture.get("custom_tag_decisions", []):
        errors.extend(_schema_errors(decision, "m9-i5-custom-tag-decision.schema.json"))
    errors.extend(_hash_errors(fixture, bundle))
    errors.extend(_fixture_errors(fixture))
    if bundle.get("fixture_hash") != fixture.get("fixture_hash"):
        errors.append(finding("NORM-HASH-MISMATCH", "bundle fixture hash mismatch"))
    if result.get("mapping_hash") != mapping.get("mapping_hash"):
        errors.append(finding("NORM-HASH-MISMATCH", "result mapping hash mismatch"))
    if result.get("period_graph_hash") != graph.get("period_graph_hash"):
        errors.append(finding("NORM-HASH-MISMATCH", "result period graph hash mismatch"))
    if result.get("source_snapshot_hash") != fixture.get("source_snapshot_hash"):
        errors.append(finding("NORM-HASH-MISMATCH", "result snapshot hash mismatch"))
    if graph.get("source_snapshot_hash") != fixture.get("source_snapshot_hash"):
        errors.append(finding("NORM-HASH-MISMATCH", "graph snapshot hash mismatch"))
    if graph.get("mapping_hash") != mapping.get("mapping_hash"):
        errors.append(finding("NORM-HASH-MISMATCH", "graph mapping hash mismatch"))
    errors.extend(_mapping_errors(fixture, mapping))
    errors.extend(_graph_errors(fixture, graph))
    errors.extend(_fact_errors(fixture, mapping, graph, result))
    errors.extend(_quality_errors(result))
    errors.extend(_ast_errors())
    unique_errors = {canonical_json(item): item for item in errors}
    errors = sorted(
        unique_errors.values(),
        key=lambda item: (item["code"], item["message"], item["subject_refs"]),
    )
    identity = {
        "normalization_hash": result["normalization_hash"],
        "mapping_hash": mapping["mapping_hash"],
        "period_graph_hash": graph["period_graph_hash"],
        "source_snapshot_hash": fixture["source_snapshot_hash"],
        "findings": errors,
    }
    validation = {
        "schema_version": "0.1.0",
        "canonicalization_version": CANONICALIZATION_VERSION,
        "validation_id": f"NVAL-{digest(identity)[:24].upper()}",
        "normalization_id": result["normalization_id"],
        "normalization_hash": result["normalization_hash"],
        "mapping_hash": mapping["mapping_hash"],
        "period_graph_hash": graph["period_graph_hash"],
        "source_snapshot_hash": fixture["source_snapshot_hash"],
        "implementation_separation": "independent",
        "network_state": "denied",
        "synthetic_only": True,
        "findings": errors,
        "passed": not errors,
    }
    validation["validation_hash"] = self_hash(validation, "validation_hash")
    schema_errors = _schema_errors(validation, "m9-i5-normalization-validation-result.schema.json")
    if schema_errors:
        raise ValueError("independent validation result violates its schema")
    return validation


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("fixture", type=Path)
    parser.add_argument("bundle", type=Path)
    args = parser.parse_args()
    validation = validate_bundle(strict_json(args.fixture), strict_json(args.bundle))
    print(canonical_json(validation))
    return 0 if validation["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
