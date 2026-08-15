import copy
from pathlib import Path

import pytest

from tools.retail_data.gaap_contracts import NormalizationError, load_synthetic_fixture
from tools.retail_data.gaap_mapping import build_mapping_policy
from tools.retail_data.period_graph import build_period_graph

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "benchmarks/fixtures/m9_i5/synthetic-gaap-golden.json"


def _inputs() -> tuple[dict, dict]:
    fixture = load_synthetic_fixture(FIXTURE)
    review = fixture["mapping_review"]
    mapping = build_mapping_policy(
        taxonomy_version=fixture["taxonomy_version"],
        review_decision_ref=review["review_decision_ref"],
        review_decision_hash=review["review_hash"],
    )
    return fixture, mapping


def _graph(fixture: dict, mapping: dict, edges: list | None = None) -> dict:
    return build_period_graph(
        fixture["facts"],
        source_snapshot_id=fixture["source_snapshot"]["snapshot_id"],
        source_snapshot_hash=fixture["source_snapshot_hash"],
        mapping_id=mapping["mapping_id"],
        mapping_hash=mapping["mapping_hash"],
        requested_edges=edges or [],
    )


def test_period_graph_deduplicates_exact_period_authority() -> None:
    fixture, mapping = _inputs()
    graph = _graph(fixture, mapping)
    assert len(graph["nodes"]) == 2
    assert {node["basis"] for node in graph["nodes"]} == {"annual", "instant"}
    annual = next(node for node in graph["nodes"] if node["basis"] == "annual")
    assert annual["duration_days"] == 365
    assert annual["selection_status"] == "selected"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("start", "2025-12-31"),
        ("end", "not-a-date"),
        ("fiscal_period", "Q2"),
        ("filed_at", "2026-01-31T00:00:00.100Z"),
    ],
)
def test_ambiguous_period_mutations_are_rejected(field: str, value: object) -> None:
    fixture, mapping = _inputs()
    fixture["facts"][0][field] = value
    with pytest.raises(NormalizationError) as error:
        _graph(fixture, mapping)
    assert error.value.code == "NORM-PERIOD-AMBIGUOUS"


def test_orphan_edge_is_rejected_before_graph_emission() -> None:
    fixture, mapping = _inputs()
    with pytest.raises(NormalizationError) as error:
        _graph(
            fixture,
            mapping,
            [
                {
                    "relationship": "annual-rollup",
                    "from_period_ids": ["PER-NOT-PRESENT"],
                    "to_period_id": "PER-NOT-PRESENT-EITHER",
                }
            ],
        )
    assert error.value.code == "NORM-PERIOD-AMBIGUOUS"


def test_52_week_annual_period_is_not_coerced_to_calendar_year() -> None:
    fixture, mapping = _inputs()
    fixture["facts"][0]["start"] = "2025-01-02"
    with pytest.raises(NormalizationError) as error:
        _graph(fixture, mapping)
    assert error.value.code == "NORM-PERIOD-AMBIGUOUS"


def test_cyclic_or_semantically_invalid_edges_are_rejected() -> None:
    fixture, mapping = _inputs()
    graph = _graph(fixture, mapping)
    ids = [node["period_id"] for node in graph["nodes"]]
    with pytest.raises(NormalizationError) as error:
        _graph(
            fixture,
            mapping,
            [
                {
                    "relationship": "prior-instant-to-current",
                    "from_period_ids": [ids[0]],
                    "to_period_id": ids[1],
                },
                {
                    "relationship": "prior-instant-to-current",
                    "from_period_ids": [ids[1]],
                    "to_period_id": ids[0],
                },
            ],
        )
    assert error.value.code == "NORM-PERIOD-AMBIGUOUS"


def test_valid_amendment_supersedes_the_complete_predecessor_period() -> None:
    fixture, mapping = _inputs()
    predecessors = copy.deepcopy(fixture["facts"][:2])
    amended = copy.deepcopy(fixture["facts"][:2])
    for fact in predecessors:
        fact["accession"] = "0000000001-26-000000"
        fact["filed_at"] = "2026-01-15T00:00:00Z"
    for fact in amended:
        fact["amendment_of_accession"] = "0000000001-26-000000"
    fixture["facts"] = [*predecessors, *amended]
    graph = _graph(fixture, mapping)
    assert [node["selection_status"] for node in graph["nodes"]] == [
        "superseded",
        "selected",
    ]
    assert graph["edges"][0]["relationship"] == "amendment-supersedes"


def test_amendment_without_exact_predecessor_is_rejected() -> None:
    fixture, mapping = _inputs()
    fixture["facts"][0]["amendment_of_accession"] = "0000000001-26-999999"
    with pytest.raises(NormalizationError) as error:
        _graph(fixture, mapping)
    assert error.value.code == "NORM-AMENDMENT-CONFLICT"


def test_forked_amendment_lineage_is_rejected() -> None:
    fixture, mapping = _inputs()
    predecessor = copy.deepcopy(fixture["facts"][0])
    predecessor["accession"] = "0000000001-26-000000"
    predecessor["filed_at"] = "2026-01-15T00:00:00Z"
    first = copy.deepcopy(fixture["facts"][0])
    first["amendment_of_accession"] = predecessor["accession"]
    second = copy.deepcopy(first)
    second["accession"] = "0000000001-26-000002"
    second["filed_at"] = "2026-02-15T00:00:00Z"
    fixture["facts"] = [predecessor, first, second]
    with pytest.raises(NormalizationError) as error:
        _graph(fixture, mapping)
    assert error.value.code == "NORM-AMENDMENT-CONFLICT"


def test_period_node_cannot_mix_form_families() -> None:
    fixture, mapping = _inputs()
    duplicate = copy.deepcopy(fixture["facts"][0])
    duplicate["form"] = "SYNTHETIC-QUARTERLY"
    fixture["facts"] = [fixture["facts"][0], duplicate]
    with pytest.raises(NormalizationError) as error:
        _graph(fixture, mapping)
    assert error.value.code == "NORM-PERIOD-AMBIGUOUS"
