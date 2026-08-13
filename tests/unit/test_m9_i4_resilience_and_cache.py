import copy
import os
import threading
from pathlib import Path

import pytest

from tools.retail_data.sec_cache import CacheError, TamperEvidentCache, synthetic_cache_context
from tools.retail_data.sec_contracts import (
    build_disabled_policy,
    load_fixture,
    provider_registry_subject,
)
from tools.retail_data.sec_fixture_transport import SyntheticFixtureTransport, SyntheticTransportError
from tools.retail_data.sec_limiter import (
    AdvancingScheduler,
    GlobalRateLimiter,
    ManualClock,
    RateLimitError,
)
from tools.retail_data.sec_resilience import CircuitBreaker, CircuitOpenError
from tools.retail_data.storage import ContentAddressedStore, StorageError


ROOT = Path(__file__).resolve().parents[2]


def _sec_store(tmp_path: Path) -> ContentAddressedStore:
    root = tmp_path / "store"
    root.mkdir()
    return ContentAddressedStore(root)


def _context(name: str = "synthetic-identity-success.json"):
    fixture = load_fixture(ROOT / "benchmarks/fixtures/m9_i4" / name)
    registry, registry_hash = provider_registry_subject(ROOT / "registries/m9-provider-license.yaml")
    policy = build_disabled_policy(registry_hash)
    return synthetic_cache_context(fixture), policy, registry


def test_global_limiter_is_one_shared_token_per_second_without_real_sleep() -> None:
    clock = ManualClock()
    scheduler = AdvancingScheduler(clock)
    limiter = GlobalRateLimiter(clock, scheduler)
    assert limiter.acquire(request_sequence=1, deadline=5) == 1
    assert limiter.acquire(request_sequence=2, deadline=5) == 2
    assert limiter.acquire(request_sequence=3, deadline=5) == 3
    assert scheduler.waits == [1.0, 1.0]
    assert clock.now() == 2.0


def test_global_limiter_fails_closed_on_deadline_and_sequence_reuse() -> None:
    clock = ManualClock()
    scheduler = AdvancingScheduler(clock)
    limiter = GlobalRateLimiter(clock, scheduler)
    limiter.acquire(request_sequence=1, deadline=0)
    with pytest.raises(RateLimitError, match="deadline"):
        limiter.acquire(request_sequence=2, deadline=0.5)
    with pytest.raises(RateLimitError, match="sequence"):
        limiter.acquire(request_sequence=1, deadline=5)


def test_global_limiter_rejects_later_sequence_without_consuming_earlier_token() -> None:
    clock = ManualClock()
    limiter = GlobalRateLimiter(clock, AdvancingScheduler(clock))
    assert limiter.acquire(request_sequence=1, deadline=5) == 1
    observed: list[Exception] = []

    def arrive_out_of_order() -> None:
        try:
            limiter.acquire(request_sequence=3, deadline=5)
        except Exception as exc:  # captured for an assertion in the owning thread
            observed.append(exc)

    later = threading.Thread(target=arrive_out_of_order)
    later.start()
    later.join(timeout=5)
    assert not later.is_alive()
    assert len(observed) == 1 and isinstance(observed[0], RateLimitError)
    assert limiter.token_sequence == 1
    assert limiter.acquire(request_sequence=2, deadline=5) == 2


def test_global_limiter_enforces_exact_queue_bound() -> None:
    class BlockingScheduler:
        def __init__(self) -> None:
            self.condition = threading.Condition()
            self.entered = 0
            self.release = threading.Event()

        def wait(self, seconds: float) -> None:
            with self.condition:
                self.entered += 1
                self.condition.notify_all()
            assert self.release.wait(timeout=5)

    clock = ManualClock()
    scheduler = BlockingScheduler()
    limiter = GlobalRateLimiter(clock, scheduler)
    assert limiter.acquire(request_sequence=1, deadline=0) == 1
    tokens: list[int] = []
    threads = [
        threading.Thread(
            target=lambda sequence=sequence: tokens.append(
                limiter.acquire(request_sequence=sequence, deadline=100)
            )
        )
        for sequence in range(2, 34)
    ]
    for expected, thread in enumerate(threads, start=1):
        thread.start()
        with scheduler.condition:
            assert scheduler.condition.wait_for(
                lambda expected=expected: scheduler.entered == expected, timeout=5
            )
    with pytest.raises(RateLimitError, match="queue is full"):
        limiter.acquire(request_sequence=34, deadline=100)
    scheduler.release.set()
    for thread in threads:
        thread.join(timeout=5)
        assert not thread.is_alive()
    assert sorted(tokens) == list(range(2, 34))


def test_circuit_breaker_opens_at_five_and_allows_one_probe_after_sixty() -> None:
    clock = ManualClock()
    breaker = CircuitBreaker(clock)
    for _ in range(5):
        permit = breaker.before_attempt("sec-xbrl", "companyfacts")
        breaker.failure(permit, countable=True)
    assert breaker.state("sec-xbrl", "companyfacts") == "open"
    with pytest.raises(CircuitOpenError):
        breaker.before_attempt("sec-xbrl", "companyfacts")
    clock.advance(60)
    probe = breaker.before_attempt("sec-xbrl", "companyfacts")
    assert probe.probe and breaker.state("sec-xbrl", "companyfacts") == "half_open"
    with pytest.raises(CircuitOpenError, match="probe"):
        breaker.before_attempt("sec-xbrl", "companyfacts")
    breaker.success(probe)
    assert breaker.state("sec-xbrl", "companyfacts") == "closed"


def test_non_countable_failure_does_not_train_breaker() -> None:
    clock = ManualClock()
    breaker = CircuitBreaker(clock)
    for _ in range(10):
        permit = breaker.before_attempt("sec-identity", "identity")
        breaker.failure(permit, countable=False)
    assert breaker.state("sec-identity", "identity") == "closed"


def _stream_fixture(events: list[dict]) -> dict:
    return {
        "synthetic": True,
        "network_state": "denied",
        "capture_provenance": "original_fixture",
        "capability": "identity",
        "endpoint_id": "sec-company-tickers-v1",
        "events": events,
    }


def test_streaming_transport_enforces_read_idle_after_headers() -> None:
    clock = ManualClock()
    transport = SyntheticFixtureTransport(
        _stream_fixture(
            [
                {
                    "kind": "response_headers",
                    "status": 200,
                    "headers": {"Content-Type": "application/json"},
                },
                {"kind": "advance_time", "seconds": 20},
                {"kind": "body_chunk", "body_encoding": "utf-8", "body": "{}"},
                {"kind": "response_end"},
            ]
        ),
        clock,
    )
    with pytest.raises(SyntheticTransportError) as error:
        transport.dispatch(
            capability="identity",
            endpoint_id="sec-company-tickers-v1",
            operation_deadline=30,
        )
    assert error.value.code == "SEC-TRANSPORT-TIMEOUT"
    assert error.value.kind == "read_idle_timeout"


def test_streaming_transport_rejects_truncation_and_bounds_chunks() -> None:
    truncated = SyntheticFixtureTransport(
        _stream_fixture(
            [
                {
                    "kind": "response_headers",
                    "status": 200,
                    "headers": {"Content-Type": "application/json"},
                },
                {"kind": "body_chunk", "body_encoding": "utf-8", "body": "{"},
            ]
        ),
        ManualClock(),
    )
    with pytest.raises(SyntheticTransportError) as truncated_error:
        truncated.dispatch(
            capability="identity",
            endpoint_id="sec-company-tickers-v1",
            operation_deadline=30,
        )
    assert truncated_error.value.kind == "partial_body"

    oversized = SyntheticFixtureTransport(
        _stream_fixture(
            [
                {
                    "kind": "response_headers",
                    "status": 200,
                    "headers": {"Content-Type": "application/json"},
                },
                {"kind": "body_chunk", "body_encoding": "utf-8", "body": "x" * 600_000},
                {"kind": "body_chunk", "body_encoding": "utf-8", "body": "y" * 500_000},
                {"kind": "response_end"},
            ]
        ),
        ManualClock(),
    )
    with pytest.raises(SyntheticTransportError) as oversize_error:
        oversized.dispatch(
            capability="identity",
            endpoint_id="sec-company-tickers-v1",
            operation_deadline=30,
        )
    assert oversize_error.value.code == "SEC-RESPONSE-OVERSIZE"


def test_read_idle_after_partial_body_is_integrity_failure_not_retryable_timeout() -> None:
    transport = SyntheticFixtureTransport(
        _stream_fixture(
            [
                {
                    "kind": "response_headers",
                    "status": 200,
                    "headers": {"Content-Type": "application/json"},
                },
                {"kind": "body_chunk", "body_encoding": "utf-8", "body": "{"},
                {"kind": "advance_time", "seconds": 20},
                {"kind": "body_chunk", "body_encoding": "utf-8", "body": "}"},
                {"kind": "response_end"},
            ]
        ),
        ManualClock(),
    )
    with pytest.raises(SyntheticTransportError) as error:
        transport.dispatch(
            capability="identity",
            endpoint_id="sec-company-tickers-v1",
            operation_deadline=30,
        )
    assert error.value.code == "SEC-RESPONSE-INTEGRITY"
    assert error.value.kind == "partial_body"


def test_m9_i3_store_media_surface_remains_narrow(tmp_path: Path) -> None:
    default_root = tmp_path / "default"
    default_root.mkdir()
    default = ContentAddressedStore(default_root)
    with pytest.raises(StorageError):
        default.put_bytes(b"synthetic", media_type="text/plain")
    cache = TamperEvidentCache(_sec_store(tmp_path))
    context, policy, registry = _context("synthetic-filing-success.json")
    index, raw = cache.publish(
        b"SYNTHETIC TEST PAYLOAD - NO PROVIDER DATA",
        media_type="text/plain",
        request_fingerprint="1" * 64,
        provider_id="sec-filings",
        capability="filings",
        endpoint_id="sec-filing-document-v1",
        policy_hash=policy["policy_hash"],
        fixture_context=context,
        policy=policy,
        provider_registry=registry,
        territory="US",
        retrieved_at="2026-08-12T00:00:00Z",
        expires_at="2026-08-12T00:10:00Z",
    )
    assert index["media_type"] == "text/plain"
    assert raw["media_type"] == "text/plain"


def _publish(cache: TamperEvidentCache):
    context, policy, registry = _context()
    return cache.publish(
        b'{"synthetic":true,"entities":[]}',
        media_type="application/json",
        request_fingerprint="1" * 64,
        provider_id="sec-identity",
        capability="identity",
        endpoint_id="sec-company-tickers-v1",
        policy_hash=policy["policy_hash"],
        fixture_context=context,
        policy=policy,
        provider_registry=registry,
        territory="US",
        retrieved_at="2026-08-12T00:00:00Z",
        expires_at="2026-08-12T00:10:00Z",
    )


def test_cache_publishes_write_once_and_rehashes_every_read(tmp_path: Path) -> None:
    store = _sec_store(tmp_path)
    cache = TamperEvidentCache(store)
    index, raw = _publish(cache)
    context, policy, registry = _context()
    assert cache.read(
        index,
        request_fingerprint="1" * 64,
        policy_hash=policy["policy_hash"],
        fixture_context=context,
        policy=policy,
        provider_registry=registry,
        territory="US",
        evaluated_at="2026-08-12T00:05:00Z",
    ) == b'{"synthetic":true,"entities":[]}'
    assert raw["content_hash"] == index["record_hash"]


def test_cache_rejects_bytes_not_bound_to_locked_fixture(tmp_path: Path) -> None:
    cache = TamperEvidentCache(_sec_store(tmp_path))
    context, policy, registry = _context()
    with pytest.raises(CacheError, match="not bound"):
        cache.publish(
            b'{"not":"a locked fixture body"}',
            media_type="application/json",
            request_fingerprint="1" * 64,
            provider_id="sec-identity",
            capability="identity",
            endpoint_id="sec-company-tickers-v1",
            policy_hash=policy["policy_hash"],
            fixture_context=context,
            policy=policy,
            provider_registry=registry,
            territory="US",
            retrieved_at="2026-08-12T00:00:00Z",
            expires_at="2026-08-12T00:10:00Z",
        )


@pytest.mark.parametrize("field", ["policy_hash", "request_fingerprint", "byte_count"])
def test_cache_rejects_coordinated_reference_tamper(tmp_path: Path, field: str) -> None:
    cache = TamperEvidentCache(_sec_store(tmp_path))
    index, _ = _publish(cache)
    context, policy, registry = _context()
    changed = copy.deepcopy(index)
    changed[field] = 99 if field == "byte_count" else "9" * 64
    with pytest.raises(CacheError):
        cache.read(
            changed,
            request_fingerprint="1" * 64,
            policy_hash=policy["policy_hash"],
            fixture_context=context,
            policy=policy,
            provider_registry=registry,
            territory="US",
            evaluated_at="2026-08-12T00:05:00Z",
        )


def test_cache_rejects_stale_and_denied_gates_without_fallback(tmp_path: Path) -> None:
    cache = TamperEvidentCache(_sec_store(tmp_path))
    index, _ = _publish(cache)
    context, policy, registry = _context()
    with pytest.raises(CacheError):
        cache.read(
            index,
            request_fingerprint="1" * 64,
            policy_hash=policy["policy_hash"],
            fixture_context=context,
            policy=policy,
            provider_registry=registry,
            territory="US",
            evaluated_at="2026-08-12T00:10:00Z",
        )
    changed_policy = copy.deepcopy(policy)
    changed_policy["global_kill_switch"] = "enabled"
    with pytest.raises(CacheError):
        cache.read(
            index,
            request_fingerprint="1" * 64,
            policy_hash=policy["policy_hash"],
            fixture_context=context,
            policy=changed_policy,
            provider_registry=registry,
            territory="US",
            evaluated_at="2026-08-12T00:05:00Z",
        )


def test_cache_rechecks_registry_right_territory_and_expiry_on_every_operation(
    tmp_path: Path,
) -> None:
    cache = TamperEvidentCache(_sec_store(tmp_path))
    index, _ = _publish(cache)
    context, policy, registry = _context()

    with pytest.raises(CacheError, match="authority"):
        cache.read(
            index,
            request_fingerprint="1" * 64,
            policy_hash=policy["policy_hash"],
            fixture_context=context,
            policy=policy,
            provider_registry=registry,
            territory="GB",
            evaluated_at="2026-08-12T00:05:00Z",
        )

    for field, value in (("rights", {"storage": True}), ("expires_on", "2000-01-01")):
        changed_registry = copy.deepcopy(registry)
        provider = next(
            item for item in changed_registry["providers"] if item["provider_id"] == "sec-identity"
        )
        if field == "rights":
            provider["rights"]["storage"] = value["storage"]
        else:
            provider[field] = value
        with pytest.raises(CacheError, match="authority"):
            cache.read(
                index,
                request_fingerprint="1" * 64,
                policy_hash=policy["policy_hash"],
                fixture_context=context,
                policy=policy,
                provider_registry=changed_registry,
                territory="US",
                evaluated_at="2026-08-12T00:05:00Z",
            )


@pytest.mark.skipif(not hasattr(os, "symlink"), reason="symlink support required")
def test_cache_rejects_symlinked_raw_reference(tmp_path: Path) -> None:
    store = _sec_store(tmp_path)
    cache = TamperEvidentCache(store)
    index, raw = _publish(cache)
    context, policy, registry = _context()
    path = store.root / "records" / "sha256" / raw["content_hash"][:2] / raw["content_hash"]
    outside = tmp_path / "outside"
    outside.write_bytes(b'{"synthetic":true}')
    path.unlink()
    path.symlink_to(outside)
    with pytest.raises(CacheError):
        cache.read(
            index,
            request_fingerprint="1" * 64,
            policy_hash=policy["policy_hash"],
            fixture_context=context,
            policy=policy,
            provider_registry=registry,
            territory="US",
            evaluated_at="2026-08-12T00:05:00Z",
        )
