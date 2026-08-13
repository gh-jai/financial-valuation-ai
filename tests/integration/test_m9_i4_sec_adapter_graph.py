import ast
import copy
import inspect
from pathlib import Path

import pytest

from tools.retail_data.canonical import canonical_sha256
from tools.retail_data.sec_adapters import replay_synthetic_fixture
from tools.retail_data.sec_cache import TamperEvidentCache, synthetic_cache_context
from tools.retail_data.sec_contracts import (
    attach_self_hash,
    build_disabled_policy,
    load_fixture,
    provider_registry_subject,
)
from tools.retail_data.sec_fixture_transport import SyntheticFixtureTransport, SyntheticTransportError
from tools.retail_data.sec_limiter import AdvancingScheduler, GlobalRateLimiter, ManualClock
from tools.retail_data.storage import ContentAddressedStore
from tools.validate_m9_i4_sec_adapters import validate_m9_i4_sec_adapters


ROOT = Path(__file__).resolve().parents[2]
REGISTRY = ROOT / "registries/m9-provider-license.yaml"
FIXTURES = sorted((ROOT / "benchmarks/fixtures/m9_i4").glob("*.json"))
SUCCESS_FIXTURES = [
    path
    for path in FIXTURES
    if path.name
    in {
        "synthetic-identity-success.json",
        "synthetic-submissions-success.json",
        "synthetic-filing-success.json",
        "synthetic-companyfacts-retry-success.json",
    }
]
AT = "2026-08-12T00:00:00Z"
VALIDATED_AT = "2026-08-12T00:20:00Z"


def _store(tmp_path: Path) -> ContentAddressedStore:
    root = tmp_path / "store"
    root.mkdir(parents=True)
    return ContentAddressedStore(root)


def _graph(tmp_path: Path, fixture_path: Path):
    _, registry_hash = provider_registry_subject(REGISTRY)
    policy = build_disabled_policy(registry_hash)
    fixture = load_fixture(fixture_path)
    store = _store(tmp_path)
    result = replay_synthetic_fixture(
        fixture=fixture,
        policy=policy,
        provider_registry_hash=registry_hash,
        store=store,
        created_at=AT,
    )
    return policy, fixture, result, store


def _validate(graph: tuple, suffix: str = "GRAPH", cache_index=None):
    policy, fixture, result, store = graph
    return validate_m9_i4_sec_adapters(
        policy=policy,
        fixture=fixture,
        result=result,
        provider_registry_path=REGISTRY,
        store_root=store.root,
        validation_result_id=f"SAV-SYNTH-{suffix}",
        created_at=VALIDATED_AT,
        cache_index=cache_index,
    )


@pytest.mark.parametrize("fixture_path", SUCCESS_FIXTURES, ids=lambda path: path.stem)
def test_all_four_capabilities_replay_and_independently_validate(
    tmp_path: Path, fixture_path: Path
) -> None:
    graph = _graph(tmp_path, fixture_path)
    policy, fixture, result, _ = graph
    validation = _validate(graph, fixture_path.stem.upper())
    assert result["status"] == "succeeded"
    assert result["result_hash"] == fixture["expected_result_hash"]
    assert result["activation_state"] == "disabled" and result["network_state"] == "denied"
    assert policy["global_kill_switch"] == "disabled"
    assert validation["status"] == "passed" and validation["findings"] == []
    assert validation["implementation_separation"] == "independent"


def test_independent_validator_accepts_later_process_wide_limiter_token(tmp_path: Path) -> None:
    registry, registry_hash = provider_registry_subject(REGISTRY)
    del registry
    policy = build_disabled_policy(registry_hash)
    clock = ManualClock()
    scheduler = AdvancingScheduler(clock)
    limiter = GlobalRateLimiter(clock, scheduler)
    first = load_fixture(ROOT / "benchmarks/fixtures/m9_i4/synthetic-identity-success.json")
    second = load_fixture(ROOT / "benchmarks/fixtures/m9_i4/synthetic-submissions-success.json")
    first_store = _store(tmp_path / "first")
    second_store = _store(tmp_path / "second")
    replay_synthetic_fixture(
        fixture=first,
        policy=policy,
        provider_registry_hash=registry_hash,
        store=first_store,
        created_at=AT,
        clock=clock,
        scheduler=scheduler,
        limiter=limiter,
    )
    second_result = replay_synthetic_fixture(
        fixture=second,
        policy=policy,
        provider_registry_hash=registry_hash,
        store=second_store,
        created_at=AT,
        clock=clock,
        scheduler=scheduler,
        limiter=limiter,
    )
    graph = (policy, second, second_result, second_store)
    validation = _validate(graph, "SHARED-LIMITER")
    assert second_result["attempts"][0]["token_sequence"] == 2
    assert validation["status"] == "passed", validation["findings"]


@pytest.mark.parametrize("fixture_path", FIXTURES, ids=lambda path: path.stem)
def test_every_locked_fixture_binds_expected_result_and_independent_replay(
    tmp_path: Path, fixture_path: Path
) -> None:
    graph = _graph(tmp_path, fixture_path)
    _, fixture, result, _ = graph
    validation = _validate(graph, "ALL-" + fixture_path.stem.upper())
    assert result["result_hash"] == fixture["expected_result_hash"]
    assert validation["status"] == "passed", validation["findings"]


def test_retry_fixture_uses_three_boundaries_without_jitter_or_real_sleep(tmp_path: Path) -> None:
    fixture = ROOT / "benchmarks/fixtures/m9_i4/synthetic-companyfacts-retry-success.json"
    _, _, result, _ = _graph(tmp_path, fixture)
    assert [item["outcome"] for item in result["attempts"]] == ["http_500", "response_accepted"]
    assert [item["token_sequence"] for item in result["attempts"]] == [1, 2]
    assert result["attempts"][1]["started_at"] == "2026-08-12T00:00:01Z"


def test_three_timeouts_stop_at_exact_attempt_cap(tmp_path: Path) -> None:
    graph = _graph(
        tmp_path, ROOT / "benchmarks/fixtures/m9_i4/synthetic-identity-timeout-exhausted.json"
    )
    result = graph[2]
    assert result["status"] == "failed"
    assert [item["outcome"] for item in result["attempts"]] == ["timeout"] * 3
    assert [item["started_at"] for item in result["attempts"]] == [
        "2026-08-12T00:00:00Z",
        "2026-08-12T00:00:01Z",
        "2026-08-12T00:00:03Z",
    ]
    assert result["errors"][0]["code"] == "SEC-TRANSPORT-TIMEOUT"


def test_total_deadline_wins_over_a_late_response(tmp_path: Path) -> None:
    result = _graph(
        tmp_path, ROOT / "benchmarks/fixtures/m9_i4/synthetic-identity-total-timeout.json"
    )[2]
    assert result["status"] == "failed"
    assert result["attempts"][0]["outcome"] == "timeout"
    assert result["errors"][0]["code"] == "SEC-TRANSPORT-TIMEOUT"
    assert result["raw_record"] is None


def test_connect_timeout_precedes_total_deadline_and_retry_uses_remaining_budget(
    tmp_path: Path,
) -> None:
    result = _graph(
        tmp_path,
        ROOT
        / "benchmarks/fixtures/m9_i4/synthetic-identity-connect-timeout-retry-success.json",
    )[2]
    assert result["status"] == "succeeded"
    assert [item["outcome"] for item in result["attempts"]] == [
        "timeout",
        "response_accepted",
    ]
    assert result["attempts"][1]["started_at"] == "2026-08-12T00:00:06Z"


def test_cancellation_stops_before_retry(tmp_path: Path) -> None:
    calls = 0

    def cancelled() -> bool:
        nonlocal calls
        calls += 1
        return calls > 1

    path = ROOT / "benchmarks/fixtures/m9_i4/synthetic-identity-timeout-exhausted.json"
    fixture = load_fixture(path)
    _, registry_hash = provider_registry_subject(REGISTRY)
    result = replay_synthetic_fixture(
        fixture=fixture,
        policy=build_disabled_policy(registry_hash),
        provider_registry_hash=registry_hash,
        store=_store(tmp_path),
        created_at=AT,
        cancelled=cancelled,
    )
    assert len(result["attempts"]) == 1
    assert result["errors"][0]["code"] == "SEC-ADAPTER-DISABLED"


def test_redirect_and_non_retryable_status_are_never_retried(tmp_path: Path) -> None:
    cases = (
        ("synthetic-identity-redirect-denied.json", "SEC-REDIRECT-DENIED"),
        ("synthetic-identity-upstream-rejected.json", "SEC-UPSTREAM-REJECTED"),
    )
    for filename, code in cases:
        result = _graph(tmp_path / filename, ROOT / "benchmarks/fixtures/m9_i4" / filename)[2]
        assert len(result["attempts"]) == 1
        assert result["errors"][0]["code"] == code


def test_oversize_media_mismatch_and_duplicate_json_fail_without_retry(tmp_path: Path) -> None:
    for filename in (
        "synthetic-identity-media-mismatch.json",
        "synthetic-identity-duplicate-json.json",
    ):
        result = _graph(tmp_path / filename, ROOT / "benchmarks/fixtures/m9_i4" / filename)[2]
        assert result["status"] == "failed"
        assert len(result["attempts"]) == 1
        assert result["errors"][0]["code"] == "SEC-RESPONSE-INTEGRITY"

    oversize_fixture = {
        "synthetic": True,
        "network_state": "denied",
        "capture_provenance": "original_fixture",
        "capability": "identity",
        "endpoint_id": "sec-company-tickers-v1",
        "events": [
            {
                "kind": "response",
                "status": 200,
                "headers": {"Content-Type": "application/json"},
                "body_encoding": "utf-8",
                "body": "x" * 1_048_577,
            }
        ],
    }
    with pytest.raises(SyntheticTransportError) as error:
        SyntheticFixtureTransport(oversize_fixture, ManualClock()).dispatch(
            capability="identity",
            endpoint_id="sec-company-tickers-v1",
            operation_deadline=30,
        )
    assert error.value.code == "SEC-RESPONSE-OVERSIZE"


def test_independent_validator_rejects_fixture_coordinated_rehash(tmp_path: Path) -> None:
    graph = list(
        _graph(tmp_path, ROOT / "benchmarks/fixtures/m9_i4/synthetic-identity-success.json")
    )
    fixture = copy.deepcopy(graph[1])
    fixture["events"][0]["body"] = '{"synthetic":true,"entities":["changed"]}'
    fixture = attach_self_hash(fixture, "fixture_hash")
    graph[1] = fixture
    validation = _validate(tuple(graph), "MUTATED")
    assert validation["status"] == "failed"
    assert any(item["code"] == "M9I4-FIXTURE-NOT-LOCKED" for item in validation["findings"])


def test_independent_validator_rejects_stored_byte_tamper(tmp_path: Path) -> None:
    graph = _graph(tmp_path, ROOT / "benchmarks/fixtures/m9_i4/synthetic-filing-success.json")
    _, _, result, store = graph
    digest = result["raw_record"]["content_hash"]
    path = store.root / "records" / "sha256" / digest[:2] / digest
    path.chmod(0o600)
    path.write_bytes(b"SYNTHETIC TAMPER")
    validation = _validate(graph, "RAW-TAMPER")
    assert validation["status"] == "failed"
    assert any(item["code"] == "M9I4-RAW-TAMPER" for item in validation["findings"])


def test_cache_index_closes_against_same_raw_record(tmp_path: Path) -> None:
    graph = _graph(tmp_path, ROOT / "benchmarks/fixtures/m9_i4/synthetic-identity-success.json")
    policy, fixture, result, store = graph
    registry, _ = provider_registry_subject(REGISTRY)
    content = store.read_bytes(result["raw_record"]["content_hash"])
    index, raw = TamperEvidentCache(store).publish(
        content,
        media_type=result["raw_record"]["media_type"],
        request_fingerprint=result["request_fingerprint"],
        provider_id=result["provider_id"],
        capability=result["capability"],
        endpoint_id=result["endpoint_id"],
        policy_hash=policy["policy_hash"],
        fixture_context=synthetic_cache_context(fixture),
        policy=policy,
        provider_registry=registry,
        territory="US",
        retrieved_at=AT,
        expires_at="2026-08-12T00:30:00Z",
    )
    assert raw == result["raw_record"]
    validation = _validate(graph, "CACHE", cache_index=index)
    assert validation["status"] == "passed"


def test_validator_rejects_rehashed_expired_cache_index_with_unknown_field(
    tmp_path: Path,
) -> None:
    graph = _graph(tmp_path, ROOT / "benchmarks/fixtures/m9_i4/synthetic-identity-success.json")
    policy, fixture, result, store = graph
    registry, _ = provider_registry_subject(REGISTRY)
    content = store.read_bytes(result["raw_record"]["content_hash"])
    index, _ = TamperEvidentCache(store).publish(
        content,
        media_type=result["raw_record"]["media_type"],
        request_fingerprint=result["request_fingerprint"],
        provider_id=result["provider_id"],
        capability=result["capability"],
        endpoint_id=result["endpoint_id"],
        policy_hash=policy["policy_hash"],
        fixture_context=synthetic_cache_context(fixture),
        policy=policy,
        provider_registry=registry,
        territory="US",
        retrieved_at=AT,
        expires_at="2026-08-12T00:30:00Z",
    )
    changed = copy.deepcopy(index)
    changed["expires_at"] = "2000-01-01T00:00:00Z"
    changed["unknown_authority"] = "synthetic"
    changed["cache_index_hash"] = canonical_sha256(
        {key: value for key, value in changed.items() if key != "cache_index_hash"}
    )
    validation = _validate(graph, "CACHE-ADVERSARIAL", cache_index=changed)
    assert validation["status"] == "failed"
    codes = {item["code"] for item in validation["findings"]}
    assert {"M9I4-CACHE-SCHEMA", "M9I4-CACHE-CLOSURE"}.issubset(codes)


def test_validator_does_not_import_any_production_m9_i4_or_hash_helper() -> None:
    import tools.validate_m9_i4_sec_adapters as validator

    source = inspect.getsource(validator)
    for prohibited in (
        "retail_data.sec_adapters",
        "retail_data.sec_endpoints",
        "retail_data.sec_limiter",
        "retail_data.sec_resilience",
        "retail_data.sec_cache",
        "retail_data.sec_fixture_transport",
        "retail_data.canonical",
    ):
        assert prohibited not in source
    tree = ast.parse(source)
    calls = {
        node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
    }
    assert not calls.intersection({"eval", "exec", "compile", "__import__"})


def test_provider_registry_bytes_are_not_part_of_candidate_scope() -> None:
    baseline = (
        "78a1c561aaf0baa199e698e053789ab47f4e0f1840c04c9962a5ad57d6ab4295"
    )
    registry, digest = provider_registry_subject(REGISTRY)
    assert digest == baseline
    assert all(item["status"] == "pending" for item in registry["providers"])
    assert all(item["live_activation"] == "disabled" for item in registry["providers"])
    assert canonical_sha256(registry) == baseline
