"""Deterministic period and amendment graph construction for M9-I5."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import date, datetime
from itertools import pairwise
from typing import Any

from .canonical import CANONICALIZATION_VERSION
from .gaap_contracts import (
    SCHEMA_VERSION,
    NormalizationError,
    deterministic_id,
    finalize_artifact,
)


def _date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise NormalizationError("NORM-PERIOD-AMBIGUOUS", "period date is invalid") from exc


def _filed_at(value: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (AttributeError, ValueError) as exc:
        raise NormalizationError("NORM-PERIOD-AMBIGUOUS", "filed instant is invalid") from exc
    if not value.endswith("Z") or parsed.microsecond:
        raise NormalizationError("NORM-PERIOD-AMBIGUOUS", "filed instant is not canonical UTC")
    return parsed


def _basis(fact: Mapping[str, Any]) -> str:
    start = fact["start"]
    fiscal_period = fact["fiscal_period"]
    if start is None:
        if fiscal_period != "INSTANT":
            raise NormalizationError("NORM-PERIOD-AMBIGUOUS", "instant fiscal label disagrees")
        return "instant"
    if fiscal_period == "FY":
        return "annual"
    if fiscal_period in {"Q1", "Q2", "Q3", "Q4"}:
        days = (_date(fact["end"]) - _date(start)).days + 1
        if 75 <= days <= 105:
            return "quarterly"
        ytd_bounds = {"Q2": (150, 205), "Q3": (235, 300), "Q4": (330, 380)}
        if (
            fiscal_period in ytd_bounds
            and ytd_bounds[fiscal_period][0] <= days <= ytd_bounds[fiscal_period][1]
        ):
            return "year-to-date"
    if fiscal_period == "TTM":
        return "ttm"
    raise NormalizationError("NORM-PERIOD-AMBIGUOUS", "duration basis is ambiguous")


def _period_subject(fact: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "start": fact["start"],
        "end": fact["end"],
        "fiscal_year": fact["fiscal_year"],
        "fiscal_period": fact["fiscal_period"],
        "filing_record_ref": fact["filing_record_ref"],
        "accession": fact["accession"],
        "filed_at": fact["filed_at"],
        "amendment_of_accession": fact["amendment_of_accession"],
    }


def _node(fact: Mapping[str, Any]) -> dict[str, Any]:
    basis = _basis(fact)
    end = _date(fact["end"])
    _filed_at(fact["filed_at"])
    if fact["start"] is None:
        duration_days = None
    else:
        start = _date(fact["start"])
        if start >= end:
            raise NormalizationError("NORM-PERIOD-AMBIGUOUS", "duration is not positive")
        duration_days = (end - start).days + 1
        if basis in {"annual", "ttm"} and duration_days not in {365, 366}:
            raise NormalizationError("NORM-PERIOD-AMBIGUOUS", "annualized duration needs review")
    subject = _period_subject(fact)
    return {
        "period_id": deterministic_id("PER", subject),
        "basis": basis,
        "start": fact["start"],
        "end": fact["end"],
        "fiscal_year": fact["fiscal_year"],
        "fiscal_period": fact["fiscal_period"],
        "duration_days": duration_days,
        "filing_record_ref": fact["filing_record_ref"],
        "accession": fact["accession"],
        "filed_at": fact["filed_at"],
        "amendment_of_accession": fact["amendment_of_accession"],
        "selection_status": "selected",
    }


def build_period_graph(
    facts: Sequence[Mapping[str, Any]],
    *,
    source_snapshot_id: str,
    source_snapshot_hash: str,
    mapping_id: str,
    mapping_hash: str,
    requested_edges: Sequence[Mapping[str, Any]] = (),
) -> dict[str, Any]:
    """Build a stable, acyclic graph and make amendment selection explicit."""

    unique: dict[tuple[Any, ...], dict[str, Any]] = {}
    node_forms: dict[str, str] = {}
    for fact in facts:
        subject = _period_subject(fact)
        key = tuple(subject.values())
        node = unique.setdefault(key, _node(fact))
        prior_form = node_forms.setdefault(node["period_id"], fact["form"])
        if prior_form != fact["form"]:
            raise NormalizationError("NORM-PERIOD-AMBIGUOUS", "period mixes form families")

    nodes = list(unique.values())
    nodes.sort(
        key=lambda item: (item["end"], item["start"] or "", item["accession"], item["period_id"])
    )
    accession_nodes: dict[str, list[dict[str, Any]]] = {}
    for node in nodes:
        accession_nodes.setdefault(node["accession"], []).append(node)
    edges: list[dict[str, Any]] = []
    for node in nodes:
        predecessor = node["amendment_of_accession"]
        if predecessor is None:
            continue
        candidates = accession_nodes.get(predecessor, [])
        matching = [
            item
            for item in candidates
            if item["start"] == node["start"]
            and item["end"] == node["end"]
            and item["fiscal_period"] == node["fiscal_period"]
        ]
        if (
            len(matching) != 1
            or matching[0]["selection_status"] != "selected"
            or node_forms[matching[0]["period_id"]] != node_forms[node["period_id"]]
            or _filed_at(node["filed_at"]) <= _filed_at(matching[0]["filed_at"])
        ):
            raise NormalizationError("NORM-AMENDMENT-CONFLICT", "amendment lineage is invalid")
        matching[0]["selection_status"] = "superseded"
        subject = {"from": matching[0]["period_id"], "to": node["period_id"]}
        edges.append(
            {
                "edge_id": deterministic_id("PEDGE", subject),
                "relationship": "amendment-supersedes",
                "from_period_ids": [matching[0]["period_id"]],
                "to_period_id": node["period_id"],
            }
        )

    known_ids = {node["period_id"] for node in nodes}
    nodes_by_id = {node["period_id"]: node for node in nodes}
    for requested in requested_edges:
        relationship = requested.get("relationship")
        from_ids = requested.get("from_period_ids")
        to_id = requested.get("to_period_id")
        if (
            relationship == "amendment-supersedes"
            or not isinstance(from_ids, list)
            or not from_ids
            or not isinstance(to_id, str)
            or any(period_id not in known_ids for period_id in [*from_ids, to_id])
        ):
            raise NormalizationError("NORM-PERIOD-AMBIGUOUS", "period edge is not reference-closed")
        _require_relationship(relationship, from_ids, to_id, nodes_by_id)
        edge_subject = {"relationship": relationship, "from": from_ids, "to": to_id}
        edges.append(
            {
                "edge_id": deterministic_id("PEDGE", edge_subject),
                "relationship": relationship,
                "from_period_ids": list(from_ids),
                "to_period_id": to_id,
            }
        )
    _require_acyclic(nodes, edges)
    edges.sort(key=lambda item: item["edge_id"])
    identity = {
        "source_snapshot_hash": source_snapshot_hash,
        "mapping_hash": mapping_hash,
        "nodes": nodes,
        "edges": edges,
    }
    value = {
        "schema_version": SCHEMA_VERSION,
        "canonicalization_version": CANONICALIZATION_VERSION,
        "period_graph_id": deterministic_id("PGR", identity),
        "source_snapshot_id": source_snapshot_id,
        "source_snapshot_hash": source_snapshot_hash,
        "mapping_id": mapping_id,
        "mapping_hash": mapping_hash,
        "network_state": "denied",
        "synthetic_only": True,
        "nodes": nodes,
        "edges": edges,
    }
    return finalize_artifact(
        value,
        hash_field="period_graph_hash",
        schema_filename="m9-i5-period-graph.schema.json",
    )


def _require_acyclic(
    nodes: Sequence[Mapping[str, Any]], edges: Sequence[Mapping[str, Any]]
) -> None:
    adjacency = {node["period_id"]: [] for node in nodes}
    for edge in edges:
        for source in edge["from_period_ids"]:
            adjacency[source].append(edge["to_period_id"])
    state: dict[str, int] = {}

    def visit(node_id: str) -> None:
        if state.get(node_id) == 1:
            raise NormalizationError("NORM-PERIOD-AMBIGUOUS", "period graph contains a cycle")
        if state.get(node_id) == 2:
            return
        state[node_id] = 1
        for target in adjacency[node_id]:
            visit(target)
        state[node_id] = 2

    for node_id in adjacency:
        visit(node_id)


def _require_relationship(
    relationship: str,
    from_ids: Sequence[str],
    to_id: str,
    nodes: Mapping[str, Mapping[str, Any]],
) -> None:
    sources = [nodes[source_id] for source_id in from_ids]
    target = nodes[to_id]
    if relationship == "prior-instant-to-current":
        valid = (
            len(sources) == 1
            and sources[0]["basis"] == target["basis"] == "instant"
            and _date(sources[0]["end"]) < _date(target["end"])
        )
    elif relationship == "quarter-to-ytd":
        valid = (
            len(sources) == 1
            and sources[0]["basis"] == "quarterly"
            and target["basis"] == "year-to-date"
            and sources[0]["end"] == target["end"]
            and _date(sources[0]["start"]) >= _date(target["start"])
        )
    elif relationship == "ytd-to-annual":
        valid = (
            len(sources) == 1
            and sources[0]["basis"] == "year-to-date"
            and target["basis"] == "annual"
            and sources[0]["end"] == target["end"]
        )
    elif relationship in {"annual-rollup", "ttm-composition"}:
        ordered = sorted(sources, key=lambda item: item["start"] or "")
        contiguous = all(
            (_date(right["start"]) - _date(left["end"])).days == 1
            for left, right in pairwise(ordered)
        )
        valid = (
            len(ordered) == 4
            and all(node["basis"] == "quarterly" for node in ordered)
            and target["basis"] == ("annual" if relationship == "annual-rollup" else "ttm")
            and ordered[0]["start"] == target["start"]
            and ordered[-1]["end"] == target["end"]
            and contiguous
        )
    else:
        valid = False
    if not valid:
        raise NormalizationError("NORM-PERIOD-AMBIGUOUS", "period relationship is invalid")


__all__ = ["build_period_graph"]
