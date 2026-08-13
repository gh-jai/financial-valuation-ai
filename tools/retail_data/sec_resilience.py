"""Bounded retry, timeout, and circuit-breaker state for M9-I4."""

from __future__ import annotations

from dataclasses import dataclass
from threading import RLock
from typing import Protocol


RETRYABLE_HTTP = frozenset({429, 500, 502, 503, 504})
MAX_ATTEMPTS = 3
BACKOFF_SECONDS = (1.0, 2.0)
CONNECT_TIMEOUT_SECONDS = 5.0
READ_IDLE_TIMEOUT_SECONDS = 20.0
TOTAL_TIMEOUT_SECONDS = 30.0


class Clock(Protocol):
    def now(self) -> float: ...


class CircuitOpenError(ValueError):
    code = "SEC-CIRCUIT-OPEN"


@dataclass(frozen=True, slots=True)
class CircuitPermit:
    key: tuple[str, str]
    probe: bool


@dataclass(slots=True)
class _CircuitState:
    consecutive_failures: int = 0
    opened_at: float | None = None
    probe_active: bool = False


class CircuitBreaker:
    """Shared provider/capability breaker with one deterministic half-open probe."""

    FAILURE_THRESHOLD = 5
    OPEN_SECONDS = 60.0

    def __init__(self, clock: Clock) -> None:
        self._clock = clock
        self._states: dict[tuple[str, str], _CircuitState] = {}
        self._lock = RLock()

    def state(self, provider_id: str, capability: str) -> str:
        with self._lock:
            current = self._states.setdefault((provider_id, capability), _CircuitState())
            if current.opened_at is None:
                return "closed"
            if self._clock.now() - current.opened_at >= self.OPEN_SECONDS:
                return "half_open"
            return "open"

    def before_attempt(self, provider_id: str, capability: str) -> CircuitPermit:
        key = (provider_id, capability)
        with self._lock:
            current = self._states.setdefault(key, _CircuitState())
            state = self.state(provider_id, capability)
            if state == "open":
                raise CircuitOpenError("circuit is open")
            if state == "half_open":
                if current.probe_active:
                    raise CircuitOpenError("half-open probe is already active")
                current.probe_active = True
                return CircuitPermit(key, True)
            return CircuitPermit(key, False)

    def success(self, permit: CircuitPermit) -> None:
        with self._lock:
            current = self._states.setdefault(permit.key, _CircuitState())
            current.consecutive_failures = 0
            current.opened_at = None
            current.probe_active = False

    def failure(self, permit: CircuitPermit, *, countable: bool) -> None:
        with self._lock:
            current = self._states.setdefault(permit.key, _CircuitState())
            current.probe_active = False
            if not countable:
                return
            if permit.probe:
                current.consecutive_failures = self.FAILURE_THRESHOLD
                current.opened_at = self._clock.now()
                return
            current.consecutive_failures += 1
            if current.consecutive_failures >= self.FAILURE_THRESHOLD:
                current.opened_at = self._clock.now()


def retryable_outcome(kind: str, status: int | None = None) -> bool:
    if kind in {"timeout", "connection_reset_before_response"}:
        return True
    return kind == "response" and status in RETRYABLE_HTTP


def outcome_name(kind: str, status: int | None = None) -> str:
    if kind == "response":
        if status == 429 or status in {500, 502, 503, 504}:
            return f"http_{status}"
        return "response_accepted"
    return kind
