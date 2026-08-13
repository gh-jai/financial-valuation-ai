"""Disabled SEC adapters plus an isolated synthetic replay implementation."""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from datetime import datetime, timedelta, timezone
from typing import Any

from .canonical import canonical_sha256
from .registries import ProviderRegistry
from .sec_contracts import (
    finalize_result,
    request_fingerprint,
    require_disabled_policy,
    require_locked_fixture,
    safe_error,
    validate_created_at,
)
from .sec_endpoints import ENDPOINTS, EndpointError, construct_endpoint, normalize_identifiers
from .sec_fixture_transport import SyntheticFixtureTransport, SyntheticTransportError
from .sec_limiter import AdvancingScheduler, GlobalRateLimiter, ManualClock, RateLimitError
from .sec_resilience import (
    BACKOFF_SECONDS,
    MAX_ATTEMPTS,
    TOTAL_TIMEOUT_SECONDS,
    CircuitBreaker,
    CircuitOpenError,
)
from .storage import ContentAddressedStore, StorageError


class _DuplicateKey(ValueError):
    pass


def _reject_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateKey(key)
        result[key] = value
    return result


def _parse_json(content: bytes) -> None:
    try:
        json.loads(
            content.decode("utf-8"),
            object_pairs_hook=_reject_duplicates,
            parse_constant=lambda token: (_ for _ in ()).throw(ValueError(token)),
        )
    except (UnicodeError, json.JSONDecodeError, ValueError) as exc:
        raise SyntheticTransportError("SEC-RESPONSE-INTEGRITY", "json_parse") from exc


def _timestamp(created_at: str, elapsed: float) -> str:
    base = datetime.fromisoformat(created_at[:-1] + "+00:00")
    value = base + timedelta(seconds=elapsed)
    return value.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _result_id(capability: str, created_at: str, suffix: str) -> str:
    subject = {"capability": capability, "created_at": created_at, "suffix": suffix}
    return "SAR-" + canonical_sha256(subject)[:24].upper()


def _base_result(
    *,
    policy: Mapping[str, Any],
    provider_registry_hash: str,
    capability: str,
    request_fingerprint_value: str,
    user_agent_policy_valid: bool,
    created_at: str,
    suffix: str,
) -> dict[str, Any]:
    spec = ENDPOINTS[capability]
    return {
        "schema_version": "0.1.0",
        "canonicalization_version": "fvi-canonical-json-v1",
        "result_id": _result_id(capability, created_at, suffix),
        "created_at": created_at,
        "policy_hash": policy["policy_hash"],
        "provider_registry_hash": provider_registry_hash,
        "provider_id": spec.provider_id,
        "capability": capability,
        "endpoint_id": spec.endpoint_id,
        "request_fingerprint": request_fingerprint_value,
        "activation_state": "disabled",
        "network_state": "denied",
        "user_agent_policy_valid": user_agent_policy_valid,
        "attempts": [],
        "cache": {"disposition": "bypassed", "index_hash": None, "published": False},
        "raw_record": None,
        "status": "failed",
        "errors": [],
    }


class DisabledSecAdapter:
    """A capability-isolated adapter whose live/public path cannot dispatch."""

    capability: str

    def __init__(
        self,
        *,
        policy: Mapping[str, Any],
        registry: ProviderRegistry,
        provider_registry_hash: str,
        transport: SyntheticFixtureTransport | None = None,
    ) -> None:
        require_disabled_policy(policy, provider_registry_hash)
        self._policy = policy
        self._registry = registry
        self._provider_registry_hash = provider_registry_hash
        self._transport = transport

    def execute(
        self,
        *,
        identifiers: Mapping[str, str],
        user_agent_policy_valid: bool,
        created_at: str,
    ) -> dict[str, Any]:
        """Validate caller inputs, then stop before any injected transport dispatch."""

        validate_created_at(created_at)
        spec = ENDPOINTS[self.capability]
        try:
            normalized = normalize_identifiers(self.capability, identifiers)
            construct_endpoint(self.capability, normalized)
            fingerprint = request_fingerprint(
                self._policy,
                provider_id=spec.provider_id,
                capability=self.capability,
                endpoint_id=spec.endpoint_id,
                identifiers=normalized,
                accept_media=spec.accept_media,
                user_agent_policy_valid=user_agent_policy_valid,
            )
        except EndpointError:
            normalized = {}
            fingerprint = canonical_sha256(
                {"capability": self.capability, "denied": True, "policy_hash": self._policy["policy_hash"]}
            )
            error_code = "SEC-ENDPOINT-DENIED"
        else:
            error_code = "SEC-ADAPTER-DISABLED"
            if user_agent_policy_valid is not True:
                error_code = "SEC-USER-AGENT-DENIED"
            else:
                record = self._registry.by_id.get(spec.provider_id)
                if record is None or record.status != "pending" or record.live_activation != "disabled":
                    error_code = "SEC-PROVIDER-DENIED"
                elif (
                    self._policy.get("activation_state") != "disabled"
                    or self._policy.get("network_state") != "denied"
                    or self._policy.get("global_kill_switch") != "disabled"
                ):
                    error_code = "SEC-HASH-MISMATCH"
        result = _base_result(
            policy=self._policy,
            provider_registry_hash=self._provider_registry_hash,
            capability=self.capability,
            request_fingerprint_value=fingerprint,
            user_agent_policy_valid=user_agent_policy_valid,
            created_at=created_at,
            suffix="DISABLED",
        )
        result["errors"] = [safe_error(error_code, self._policy["policy_id"], spec.endpoint_id)]
        return finalize_result(result)


class SecIdentityAdapter(DisabledSecAdapter):
    capability = "identity"


class SecSubmissionsAdapter(DisabledSecAdapter):
    capability = "submissions"


class SecFilingsAdapter(DisabledSecAdapter):
    capability = "filings"


class SecCompanyFactsAdapter(DisabledSecAdapter):
    capability = "companyfacts"


def replay_synthetic_fixture(
    *,
    fixture: Mapping[str, Any],
    policy: Mapping[str, Any],
    provider_registry_hash: str,
    store: ContentAddressedStore,
    created_at: str,
    clock: ManualClock | None = None,
    scheduler: AdvancingScheduler | None = None,
    limiter: GlobalRateLimiter | None = None,
    breaker: CircuitBreaker | None = None,
    cancelled: Callable[[], bool] | None = None,
) -> dict[str, Any]:
    """Exercise bounded mechanics in a test-only, network-denied harness.

    This does not call ``DisabledSecAdapter.execute`` and cannot change provider or kill-switch
    authority. It produces synthetic evidence only.
    """

    validate_created_at(created_at)
    require_disabled_policy(policy, provider_registry_hash)
    require_locked_fixture(fixture)
    capability = fixture["capability"]
    spec = ENDPOINTS[capability]
    identifiers = normalize_identifiers(capability, fixture["identifiers"])
    construct_endpoint(capability, identifiers)
    ua_valid = fixture["user_agent_policy_valid"] is True
    fingerprint = request_fingerprint(
        policy,
        provider_id=spec.provider_id,
        capability=capability,
        endpoint_id=spec.endpoint_id,
        identifiers=identifiers,
        accept_media=spec.accept_media,
        user_agent_policy_valid=ua_valid,
    )
    result = _base_result(
        policy=policy,
        provider_registry_hash=provider_registry_hash,
        capability=capability,
        request_fingerprint_value=fingerprint,
        user_agent_policy_valid=ua_valid,
        created_at=created_at,
        suffix=str(fixture["fixture_id"]),
    )
    if not ua_valid:
        result["errors"] = [safe_error("SEC-USER-AGENT-DENIED", fixture["fixture_id"])]
        return finalize_result(result)

    actual_clock = clock or ManualClock()
    actual_scheduler = scheduler or AdvancingScheduler(actual_clock)
    actual_limiter = limiter or GlobalRateLimiter(actual_clock, actual_scheduler)
    actual_breaker = breaker or CircuitBreaker(actual_clock)
    transport = SyntheticFixtureTransport(fixture, actual_clock)
    started = actual_clock.now()
    deadline = started + TOTAL_TIMEOUT_SECONDS
    request_sequence = actual_limiter.token_sequence + 1
    final_code = "SEC-RESPONSE-INTEGRITY"

    def offline_locked() -> bool:
        capability_policy = next(
            (
                item
                for item in policy.get("capabilities", [])
                if item.get("capability") == capability
            ),
            {},
        )
        return (
            policy.get("activation_state") == "disabled"
            and policy.get("network_state") == "denied"
            and policy.get("global_kill_switch") == "disabled"
            and capability_policy.get("kill_switch") == "disabled"
        )

    for attempt_number in range(1, MAX_ATTEMPTS + 1):
        if (cancelled is not None and cancelled()) or not offline_locked():
            final_code = "SEC-ADAPTER-DISABLED"
            break
        if attempt_number > 1:
            actual_scheduler.wait(BACKOFF_SECONDS[attempt_number - 2])
            if (cancelled is not None and cancelled()) or not offline_locked():
                final_code = "SEC-ADAPTER-DISABLED"
                break
        if actual_clock.now() >= deadline:
            final_code = "SEC-TRANSPORT-TIMEOUT"
            break
        try:
            permit = actual_breaker.before_attempt(spec.provider_id, capability)
        except CircuitOpenError:
            final_code = "SEC-CIRCUIT-OPEN"
            break
        try:
            token = actual_limiter.acquire(request_sequence=request_sequence, deadline=deadline)
        except RateLimitError:
            actual_breaker.failure(permit, countable=False)
            final_code = "SEC-RATE-LIMITED"
            break
        request_sequence += 1
        attempt_started = actual_clock.now()
        try:
            response = transport.dispatch(
                capability=capability,
                endpoint_id=spec.endpoint_id,
                operation_deadline=deadline,
            )
        except SyntheticTransportError as exc:
            if exc.code == "SEC-TRANSPORT-TIMEOUT":
                attempt_outcome = "timeout"
            elif exc.code == "SEC-TRANSPORT-RESET":
                attempt_outcome = "connection_reset_before_response"
            else:
                attempt_outcome = "response_accepted"
            actual_breaker.failure(
                permit,
                countable=exc.code in {"SEC-TRANSPORT-TIMEOUT", "SEC-TRANSPORT-RESET"},
            )
            result["attempts"].append(
                {
                    "attempt": attempt_number,
                    "token_sequence": token,
                    "started_at": _timestamp(created_at, attempt_started - started),
                    "ended_at": _timestamp(created_at, actual_clock.now() - started),
                    "outcome": attempt_outcome,
                }
            )
            final_code = exc.code
            if (
                exc.code in {"SEC-TRANSPORT-TIMEOUT", "SEC-TRANSPORT-RESET"}
                and attempt_number < MAX_ATTEMPTS
                and actual_clock.now() < deadline
            ):
                continue
            break

        if actual_clock.now() >= deadline:
            actual_breaker.failure(permit, countable=True)
            result["attempts"].append(
                {
                    "attempt": attempt_number,
                    "token_sequence": token,
                    "started_at": _timestamp(created_at, attempt_started - started),
                    "ended_at": _timestamp(created_at, actual_clock.now() - started),
                    "outcome": "timeout",
                }
            )
            final_code = "SEC-TRANSPORT-TIMEOUT"
            break
        status = response.status
        if status in {429, 500, 502, 503, 504}:
            actual_breaker.failure(permit, countable=True)
            result["attempts"].append(
                {
                    "attempt": attempt_number,
                    "token_sequence": token,
                    "started_at": _timestamp(created_at, attempt_started - started),
                    "ended_at": _timestamp(created_at, actual_clock.now() - started),
                    "outcome": f"http_{status}",
                }
            )
            final_code = "SEC-UPSTREAM-RETRYABLE"
            if attempt_number < MAX_ATTEMPTS:
                continue
            break
        result["attempts"].append(
            {
                "attempt": attempt_number,
                "token_sequence": token,
                "started_at": _timestamp(created_at, attempt_started - started),
                "ended_at": _timestamp(created_at, actual_clock.now() - started),
                "outcome": "response_accepted",
            }
        )
        if 300 <= status <= 399:
            actual_breaker.failure(permit, countable=False)
            final_code = "SEC-REDIRECT-DENIED"
            break
        if not 200 <= status <= 299:
            actual_breaker.failure(permit, countable=False)
            final_code = "SEC-UPSTREAM-REJECTED"
            break
        if response.media_type not in spec.accept_media:
            actual_breaker.failure(permit, countable=False)
            final_code = "SEC-RESPONSE-INTEGRITY"
            break
        if (cancelled is not None and cancelled()) or not offline_locked():
            actual_breaker.failure(permit, countable=False)
            final_code = "SEC-ADAPTER-DISABLED"
            break
        try:
            if response.media_type == "application/json":
                _parse_json(response.body)
            # Preserve the exact M9-I3 store implementation. Response media is bound by the M9-I4
            # result while the underlying content-addressed store persists only exact bytes.
            stored = store.put_bytes(response.body, media_type="application/json")
        except (SyntheticTransportError, StorageError) as exc:
            actual_breaker.failure(permit, countable=False)
            final_code = getattr(exc, "code", "SEC-RESPONSE-INTEGRITY")
            if not str(final_code).startswith("SEC-"):
                final_code = "SEC-RESPONSE-INTEGRITY"
            break
        actual_breaker.success(permit)
        result["raw_record"] = {
            "record_id": "REC-" + stored.record_hash[:24].upper(),
            "content_hash": stored.record_hash,
            "byte_count": stored.byte_length,
            "media_type": response.media_type,
        }
        result["status"] = "succeeded"
        result["errors"] = []
        return finalize_result(result)

    result["errors"] = [safe_error(final_code, fixture["fixture_id"], spec.endpoint_id)]
    return finalize_result(result)
