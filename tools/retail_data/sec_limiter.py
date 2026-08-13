"""Injected-clock deterministic global limiter for synthetic M9-I4 replay."""

from __future__ import annotations

from dataclasses import dataclass, field
from threading import RLock
from typing import Protocol


class MonotonicClock(Protocol):
    def now(self) -> float: ...


class Scheduler(Protocol):
    def wait(self, seconds: float) -> None: ...


class RateLimitError(ValueError):
    """The bounded global limiter could not admit an attempt."""

    code = "SEC-RATE-LIMITED"


@dataclass(slots=True)
class ManualClock:
    """A deterministic monotonic clock used only by injected offline execution."""

    value: float = 0.0

    def now(self) -> float:
        return self.value

    def advance(self, seconds: float) -> None:
        if isinstance(seconds, bool) or not isinstance(seconds, (int, float)) or seconds < 0:
            raise ValueError("clock advance must be a non-negative number")
        self.value += float(seconds)


@dataclass(slots=True)
class AdvancingScheduler:
    """Advance an injected clock; never invoke real sleep."""

    clock: ManualClock
    waits: list[float] = field(default_factory=list)

    def wait(self, seconds: float) -> None:
        if isinstance(seconds, bool) or not isinstance(seconds, (int, float)) or seconds < 0:
            raise ValueError("scheduled wait must be a non-negative number")
        value = float(seconds)
        self.waits.append(value)
        self.clock.advance(value)


class GlobalRateLimiter:
    """One-token, one-second process-shared budget with a bounded wait set."""

    WINDOW_SECONDS = 1.0
    MAX_REQUESTS = 1
    BURST_CAPACITY = 1
    QUEUE_LIMIT = 32

    def __init__(self, clock: MonotonicClock, scheduler: Scheduler) -> None:
        self._clock = clock
        self._scheduler = scheduler
        self._next_eligible = clock.now()
        self._token_sequence = 0
        self._pending = 0
        self._next_request_sequence = 1
        self._lock = RLock()

    @property
    def token_sequence(self) -> int:
        return self._token_sequence

    def acquire(self, *, request_sequence: int, deadline: float) -> int:
        """Admit in request order or fail without unbounded waiting."""

        if (
            isinstance(request_sequence, bool)
            or not isinstance(request_sequence, int)
            or request_sequence < 1
        ):
            raise TypeError("request_sequence must be a positive integer")
        if isinstance(deadline, bool) or not isinstance(deadline, (int, float)):
            raise TypeError("deadline must be numeric")
        with self._lock:
            # A later sequence may reach this lock before an earlier caller.  It must never
            # reserve the earlier caller's token/window.  Missing or reordered sequences stop
            # immediately instead of creating an unbounded wait for a caller that may not exist.
            if request_sequence != self._next_request_sequence:
                raise RateLimitError("request sequence is not the next eligible sequence")
            if self._pending >= self.QUEUE_LIMIT:
                raise RateLimitError("global limiter queue is full")
            now = self._clock.now()
            eligible = max(now, self._next_eligible)
            if eligible > float(deadline):
                raise RateLimitError("global limiter would exceed the operation deadline")
            self._pending += 1
            self._token_sequence += 1
            token_sequence = self._token_sequence
            self._next_request_sequence += 1
            self._next_eligible = eligible + self.WINDOW_SECONDS
        try:
            if eligible > now:
                self._scheduler.wait(eligible - now)
            return token_sequence
        finally:
            with self._lock:
                self._pending -= 1
