import ast
import copy
import inspect
from datetime import datetime, timezone
from pathlib import Path

from tools.retail_data.identity_contracts import strict_load
from tools.retail_data.resolution import load_synthetic_catalog, resolve_issuer, create_selection, verify_selected_identity
from tools.retail_data.structural_scope import evaluate_structural_scope
from tools.validate_issuer_resolution import validate_issuer_resolution


ROOT = Path(__file__).resolve().parents[2]
AT = "2026-08-09T00:00:00Z"


def _request() -> dict:
    return {"schema_version": "0.1.0", "request_id": "REQ-SYNTH-GRAPH", "requested_at": AT, "market_scope": "us-listed-non-financial-operating-company", "query": {"kind": "ticker", "ticker": "ZXQA"}, "locale": "en", "jurisdiction": {"country_code": "US"}, "acknowledgements": {"research_not_advice": True, "no_trade_instruction": True, "scenario_uncertainty": True}}


def _graph() -> tuple:
    at = datetime(2026, 8, 9, tzinfo=timezone.utc)
    request = _request()
    catalog = load_synthetic_catalog("m9-i2-synthetic-catalog", at)
    policy = strict_load(ROOT / "registries/m9-identity-resolution-policy.yaml")
    registry = strict_load(ROOT / "registries/m9-issuer-structural-scope.yaml")
    candidates = resolve_issuer(request, catalog, policy, resolution_at=AT, candidate_set_id="ICS-SYNTH-GRAPH")
    selection = create_selection(candidates, selection_id="ISL-SYNTH-GRAPH", selected_at=AT, selected_candidate_id=candidates["candidates"][0]["candidate_id"], actor_id="synthetic-human-reviewer")
    identity = verify_selected_identity(candidates, selection, policy, verified_identity_id="VID-SYNTH-GRAPH", verified_at=AT)
    decision = evaluate_structural_scope(identity, registry, policy, scope_decision_id="ISD-SYNTH-GRAPH", evaluated_at=AT)
    return request, catalog, policy, registry, candidates, selection, identity, decision


def test_independent_validator_closes_all_eight_subjects() -> None:
    request, catalog, policy, registry, candidates, selection, identity, decision = _graph()
    result = validate_issuer_resolution(company_request=request, identity_catalog=catalog, identity_policy=policy, candidate_set=candidates, selection=selection, verified_identity=identity, scope_registry=registry, scope_decision=decision, validation_result_id="IVR-SYNTH-GRAPH", created_at=AT)
    assert result["status"] == "passed" and result["findings"] == []
    assert len(result["subjects"]) == 8
    assert result["implementation_separation"] == "independent"


def test_independent_validator_kills_nested_production_mutation() -> None:
    request, catalog, policy, registry, candidates, selection, identity, decision = _graph()
    mutated = copy.deepcopy(identity)
    mutated["ticker"] = "ZXQZ"
    result = validate_issuer_resolution(company_request=request, identity_catalog=catalog, identity_policy=policy, candidate_set=candidates, selection=selection, verified_identity=mutated, scope_registry=registry, scope_decision=decision, validation_result_id="IVR-SYNTH-MUTATION", created_at=AT)
    assert result["status"] == "failed"
    assert any("mutates selected candidate" in item["message"] for item in result["findings"])


def test_validator_import_graph_is_implementation_separated() -> None:
    import tools.validate_issuer_resolution as validator

    source = inspect.getsource(validator)
    for prohibited in ("retail_data.resolution", "retail_data.structural_scope", "identity_contracts"):
        assert prohibited not in source


def test_m9_i2_runtime_has_no_network_shell_dynamic_or_provider_imports() -> None:
    files = [ROOT / "tools/retail_data/identity_contracts.py", ROOT / "tools/retail_data/resolution.py", ROOT / "tools/retail_data/structural_scope.py", ROOT / "tools/validate_issuer_resolution.py"]
    forbidden = {"socket", "subprocess", "requests", "httpx", "aiohttp", "urllib.request", "http.client", "boto3", "selenium"}
    imports = set()
    calls = set()
    for path in files:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module)
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                calls.add(node.func.id)
    assert not imports.intersection(forbidden)
    assert not calls.intersection({"eval", "exec", "compile", "__import__"})


def test_artifact_graph_contains_no_valuation_approval_route_or_provider_payload() -> None:
    graph = _graph()
    keys = set()

    def collect(value) -> None:
        if isinstance(value, dict):
            keys.update(value)
            for item in value.values():
                collect(item)
        elif isinstance(value, (list, tuple)):
            for item in value:
                collect(item)

    collect(graph)
    for prohibited in (
        "case_lock",
        "output_approval",
        "provider_payload",
        "lifecycle_route_id",
        "trade_instruction",
    ):
        assert prohibited not in keys
