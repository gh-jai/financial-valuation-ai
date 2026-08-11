import ast
import copy
import inspect
from datetime import datetime, timezone
from pathlib import Path

from tools.retail_data.canonical import canonical_sha256
from tools.retail_data.identity_contracts import strict_load
from tools.retail_data.manual_import import import_manual_bytes
from tools.retail_data.resolution import (
    create_selection,
    load_synthetic_catalog,
    resolve_issuer,
    verify_selected_identity,
)
from tools.retail_data.snapshots import build_manual_snapshot
from tools.retail_data.storage import ContentAddressedStore
from tools.retail_data.structural_scope import evaluate_structural_scope
from tools.validate_m9_i3_storage import validate_m9_i3_storage


ROOT = Path(__file__).resolve().parents[2]
AT = "2026-08-11T00:00:00Z"


def _request() -> dict:
    return {
        "schema_version": "0.1.0",
        "request_id": "REQ-SYNTH-I3",
        "requested_at": AT,
        "market_scope": "us-listed-non-financial-operating-company",
        "query": {"kind": "ticker", "ticker": "ZXQA"},
        "locale": "en",
        "jurisdiction": {"country_code": "US"},
        "acknowledgements": {
            "research_not_advice": True,
            "no_trade_instruction": True,
            "scenario_uncertainty": True,
        },
    }


def _identity_and_scope() -> tuple[dict, dict]:
    at = datetime(2026, 8, 11, tzinfo=timezone.utc)
    request = _request()
    catalog = load_synthetic_catalog("m9-i2-synthetic-catalog", at)
    policy = strict_load(ROOT / "registries/m9-identity-resolution-policy.yaml")
    registry = strict_load(ROOT / "registries/m9-issuer-structural-scope.yaml")
    candidates = resolve_issuer(
        request,
        catalog,
        policy,
        resolution_at=AT,
        candidate_set_id="ICS-SYNTH-I3",
    )
    selection = create_selection(
        candidates,
        selection_id="ISL-SYNTH-I3",
        selected_at=AT,
        selected_candidate_id=candidates["candidates"][0]["candidate_id"],
        actor_id="synthetic-human-reviewer",
    )
    identity = verify_selected_identity(
        candidates,
        selection,
        policy,
        verified_identity_id="VID-SYNTH-I3",
        verified_at=AT,
    )
    decision = evaluate_structural_scope(
        identity,
        registry,
        policy,
        scope_decision_id="ISD-SYNTH-I3",
        evaluated_at=AT,
    )
    return identity, decision


def _graph(tmp_path: Path) -> tuple:
    store_root = tmp_path / "store"
    store_root.mkdir()
    store = ContentAddressedStore(store_root)
    raw = (ROOT / "benchmarks/fixtures/m9_i3/synthetic-manual-financials.csv").read_bytes()
    imported = import_manual_bytes(
        store,
        raw,
        media_type="text/csv",
        source_label="synthetic-financials",
        created_at=AT,
    )
    identity, decision = _identity_and_scope()
    snapshot, manifest = build_manual_snapshot(
        request_id="REQ-SYNTH-I3",
        verified_identity=identity,
        scope_decision=decision,
        import_result=imported,
        created_at=AT,
        record_metadata={
            "as_of": AT,
            "period_start": "2025-01-01",
            "period_end": "2025-12-31",
            "currency": "USD",
            "unit_basis": "reported-unscaled",
            "license_ref": "synthetic-local-data-review-v1",
        },
        freshness={
            "evaluated_at": AT,
            "financials_as_of": "2025-12-31",
            "market_data_as_of": None,
            "policy_id": "m9-i3-synthetic-freshness-v1",
            "stale": False,
        },
        license_review={
            "status": "approved",
            "reviewer": "synthetic-license-reviewer",
            "reviewed_at": AT,
            "storage_allowed": True,
            "display_allowed": False,
            "export_allowed": False,
            "redistribution_allowed": False,
        },
        status="complete",
    )
    return store, identity, decision, imported, snapshot, manifest


def _validate(graph: tuple, suffix: str = "GRAPH") -> dict:
    store, identity, decision, imported, snapshot, manifest = graph
    return validate_m9_i3_storage(
        store_root=store.root,
        verified_identity=identity,
        scope_decision=decision,
        import_result=imported,
        source_snapshot=snapshot,
        snapshot_manifest=manifest,
        validation_result_id=f"SVR-SYNTH-{suffix}",
        created_at=AT,
    )


def _rehash(value: dict, field: str) -> dict:
    updated = {key: item for key, item in value.items() if key != field}
    updated[field] = canonical_sha256(updated)
    return updated


def test_i3_graph_closes_six_subjects_and_is_deterministic(tmp_path: Path) -> None:
    graph = _graph(tmp_path)
    result = _validate(graph)
    assert result["status"] == "passed" and result["findings"] == []
    assert len(result["subjects"]) == 6
    assert result["implementation_separation"] == "independent"
    assert _validate(graph) == result


def test_validator_kills_coordinated_rehash_of_snapshot_identity_copy(tmp_path: Path) -> None:
    graph = list(_graph(tmp_path))
    snapshot = copy.deepcopy(graph[4])
    snapshot["company_identity"]["ticker"] = "ZXQZ"
    snapshot = _rehash(snapshot, "snapshot_hash")
    manifest = copy.deepcopy(graph[5])
    manifest["snapshot_hash"] = snapshot["snapshot_hash"]
    subject = {
        "created_at": manifest["created_at"],
        "import_hash": manifest["import_hash"],
        "request_id": manifest["request_id"],
        "snapshot_hash": manifest["snapshot_hash"],
        "verified_identity_hash": manifest["verified_identity_hash"],
    }
    manifest["manifest_id"] = "MNF-" + canonical_sha256(subject)[:24].upper()
    manifest = _rehash(manifest, "manifest_hash")
    graph[4], graph[5] = snapshot, manifest
    result = _validate(tuple(graph), "IDENTITY-MUTATION")
    assert result["status"] == "failed"
    assert any(item["code"] == "M9I3-SNAPSHOT-IDENTITY" for item in result["findings"])


def test_validator_detects_raw_store_tamper_even_if_metadata_is_unchanged(tmp_path: Path) -> None:
    graph = _graph(tmp_path)
    store, _, _, imported, _, _ = graph
    digest = imported["record_hash"]
    path = store.root / "records" / "sha256" / digest[:2] / digest
    path.chmod(0o600)
    path.write_bytes(b"concept,value\nrevenue,999\n")
    result = _validate(graph, "RAW-TAMPER")
    assert result["status"] == "failed"
    assert any(item["code"] == "M9I3-STORE-TAMPER" for item in result["findings"])


def test_validator_rejects_scope_or_import_reference_drift(tmp_path: Path) -> None:
    graph = list(_graph(tmp_path))
    manifest = copy.deepcopy(graph[5])
    manifest["scope_decision_hash"] = "0" * 64
    graph[5] = _rehash(manifest, "manifest_hash")
    result = _validate(tuple(graph), "REFERENCE-DRIFT")
    assert result["status"] == "failed"
    assert any(item["code"] == "M9I3-MANIFEST-CLOSURE" for item in result["findings"])


def test_validator_does_not_import_production_i3_or_hash_helpers() -> None:
    import tools.validate_m9_i3_storage as validator

    source = inspect.getsource(validator)
    for prohibited in (
        "retail_data.storage",
        "retail_data.manual_import",
        "retail_data.snapshots",
        "retail_data.canonical",
        "retail_data.identity_contracts",
    ):
        assert prohibited not in source


def test_i3_runtime_has_no_network_shell_provider_or_dynamic_execution() -> None:
    files = [
        ROOT / "tools/retail_data/storage.py",
        ROOT / "tools/retail_data/manual_import.py",
        ROOT / "tools/retail_data/snapshots.py",
        ROOT / "tools/validate_m9_i3_storage.py",
    ]
    forbidden = {
        "socket",
        "subprocess",
        "requests",
        "httpx",
        "aiohttp",
        "urllib.request",
        "http.client",
        "boto3",
        "selenium",
    }
    imports: set[str] = set()
    calls: set[str] = set()
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


def test_i3_graph_contains_no_later_slice_or_product_authority(tmp_path: Path) -> None:
    graph = _graph(tmp_path)
    keys: set[str] = set()

    def collect(value) -> None:
        if isinstance(value, dict):
            keys.update(value)
            for item in value.values():
                collect(item)
        elif isinstance(value, (list, tuple)):
            for item in value:
                collect(item)

    collect(graph[1:])
    for prohibited in (
        "provider_payload",
        "normalized_financials",
        "valuation_output",
        "case_lock",
        "output_approval",
        "trade_instruction",
        "transport",
    ):
        assert prohibited not in keys
