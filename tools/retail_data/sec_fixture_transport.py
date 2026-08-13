"""Original-fixture-only injected transport; this module has no network capability."""

from __future__ import annotations

import base64
from dataclasses import dataclass
from typing import Any, Mapping

from .sec_endpoints import MAX_DECODED_BODY_BYTES
from .sec_limiter import ManualClock
from .sec_resilience import CONNECT_TIMEOUT_SECONDS, READ_IDLE_TIMEOUT_SECONDS


MAX_HEADER_BYTES = 65_536
MAX_HEADER_COUNT = 128
MAX_HEADER_VALUE_BYTES = 8_192
MAX_STATUS_LINE_BYTES = 1_024


class SyntheticTransportError(ValueError):
    def __init__(self, code: str, kind: str) -> None:
        super().__init__(kind)
        self.code = code
        self.kind = kind


@dataclass(frozen=True, slots=True)
class SyntheticResponse:
    status: int
    headers: Mapping[str, str]
    body: bytes
    media_type: str


class SyntheticFixtureTransport:
    """Consume a strict fixture script without accepting a URL or header value."""

    def __init__(self, fixture: Mapping[str, Any], clock: ManualClock) -> None:
        if fixture.get("synthetic") is not True:
            raise ValueError("transport requires a synthetic fixture")
        if fixture.get("network_state") != "denied":
            raise ValueError("synthetic transport network state must be denied")
        if fixture.get("capture_provenance") != "original_fixture":
            raise ValueError("captured provider material is forbidden")
        self._fixture = fixture
        self._events = list(fixture["events"])
        self._cursor = 0
        self._clock = clock
        self.dispatches = 0

    def dispatch(
        self,
        *,
        capability: str,
        endpoint_id: str,
        operation_deadline: float,
    ) -> SyntheticResponse:
        if capability != self._fixture["capability"] or endpoint_id != self._fixture["endpoint_id"]:
            raise SyntheticTransportError("SEC-ENDPOINT-DENIED", "fixture_endpoint_mismatch")
        self.dispatches += 1
        attempt_started = self._clock.now()
        response_metadata: tuple[int, dict[str, str], str] | None = None
        body_parts: list[bytes] = []
        body_size = 0
        last_progress = attempt_started
        while self._cursor < len(self._events):
            event = self._events[self._cursor]
            self._cursor += 1
            kind = event["kind"]
            if kind == "advance_time":
                self._clock.advance(event["seconds"])
                continue
            if kind == "timeout":
                raise SyntheticTransportError("SEC-TRANSPORT-TIMEOUT", kind)
            if kind == "connection_reset_before_response":
                if response_metadata is not None:
                    raise SyntheticTransportError("SEC-RESPONSE-INTEGRITY", "partial_body")
                raise SyntheticTransportError("SEC-TRANSPORT-RESET", kind)
            if kind == "response":
                if response_metadata is not None:
                    raise SyntheticTransportError("SEC-RESPONSE-INTEGRITY", "response_overlap")
                self._raise_timeout_if_due(
                    attempt_started=attempt_started,
                    last_progress=last_progress,
                    reading=False,
                    body_started=False,
                    operation_deadline=operation_deadline,
                )
                return self._response(event)
            if kind == "response_headers":
                if response_metadata is not None:
                    raise SyntheticTransportError("SEC-RESPONSE-INTEGRITY", "response_overlap")
                self._raise_timeout_if_due(
                    attempt_started=attempt_started,
                    last_progress=last_progress,
                    reading=False,
                    body_started=False,
                    operation_deadline=operation_deadline,
                )
                response_metadata = self._metadata(event)
                last_progress = self._clock.now()
                continue
            if kind == "body_chunk":
                if response_metadata is None:
                    raise SyntheticTransportError("SEC-RESPONSE-INTEGRITY", "body_before_headers")
                self._raise_timeout_if_due(
                    attempt_started=attempt_started,
                    last_progress=last_progress,
                    reading=True,
                    body_started=bool(body_parts),
                    operation_deadline=operation_deadline,
                )
                chunk = self._body(event)
                body_size += len(chunk)
                if body_size > MAX_DECODED_BODY_BYTES:
                    raise SyntheticTransportError("SEC-RESPONSE-OVERSIZE", "body")
                body_parts.append(chunk)
                last_progress = self._clock.now()
                continue
            if kind == "response_end":
                if response_metadata is None:
                    raise SyntheticTransportError("SEC-RESPONSE-INTEGRITY", "end_before_headers")
                self._raise_timeout_if_due(
                    attempt_started=attempt_started,
                    last_progress=last_progress,
                    reading=True,
                    body_started=bool(body_parts),
                    operation_deadline=operation_deadline,
                )
                status, headers, media_type = response_metadata
                body = b"".join(body_parts)
                self._validate_body_headers(headers, body)
                return SyntheticResponse(status, headers, body, media_type)
            raise SyntheticTransportError("SEC-RESPONSE-INTEGRITY", "unknown_event")
        self._raise_timeout_if_due(
            attempt_started=attempt_started,
            last_progress=last_progress,
            reading=response_metadata is not None,
            body_started=bool(body_parts),
            operation_deadline=operation_deadline,
        )
        if response_metadata is not None:
            raise SyntheticTransportError("SEC-RESPONSE-INTEGRITY", "partial_body")
        raise SyntheticTransportError("SEC-RESPONSE-INTEGRITY", "fixture_exhausted")

    def _response(self, event: Mapping[str, Any]) -> SyntheticResponse:
        status, headers, media_type = self._metadata(event)
        body = self._body(event)
        if len(body) > MAX_DECODED_BODY_BYTES:
            raise SyntheticTransportError("SEC-RESPONSE-OVERSIZE", "body")
        self._validate_body_headers(headers, body)
        return SyntheticResponse(status, headers, body, media_type)

    def _metadata(self, event: Mapping[str, Any]) -> tuple[int, dict[str, str], str]:
        status = event["status"]
        if not isinstance(status, int) or not 100 <= status <= 599:
            raise SyntheticTransportError("SEC-UPSTREAM-REJECTED", "malformed_status")
        if len(f"HTTP/1.1 {status}") > MAX_STATUS_LINE_BYTES:
            raise SyntheticTransportError("SEC-RESPONSE-OVERSIZE", "status_line")
        headers = event["headers"]
        if len(headers) > MAX_HEADER_COUNT:
            raise SyntheticTransportError("SEC-RESPONSE-OVERSIZE", "header_count")
        header_bytes = 0
        for name, value in headers.items():
            value_bytes = value.encode("utf-8")
            if len(value_bytes) > MAX_HEADER_VALUE_BYTES:
                raise SyntheticTransportError("SEC-RESPONSE-OVERSIZE", "header_value")
            header_bytes += len(name.encode("ascii")) + len(value_bytes) + 4
        if header_bytes > MAX_HEADER_BYTES:
            raise SyntheticTransportError("SEC-RESPONSE-OVERSIZE", "headers")
        encoding = headers.get("Content-Encoding")
        if encoding not in (None, "identity"):
            raise SyntheticTransportError("SEC-RESPONSE-INTEGRITY", "content_encoding")
        media_type = headers.get("Content-Type", "").split(";", 1)[0].strip().lower()
        return status, dict(headers), media_type

    def _body(self, event: Mapping[str, Any]) -> bytes:
        try:
            if event["body_encoding"] == "utf-8":
                return event["body"].encode("utf-8")
            return base64.b64decode(event["body"], validate=True)
        except (UnicodeError, ValueError) as exc:
            raise SyntheticTransportError("SEC-RESPONSE-INTEGRITY", "body_encoding") from exc

    def _validate_body_headers(self, headers: Mapping[str, str], body: bytes) -> None:
        lengths = [value.strip() for name, value in headers.items() if name == "Content-Length"]
        if lengths:
            if len(set(lengths)) != 1 or not lengths[0].isdigit() or int(lengths[0]) != len(body):
                raise SyntheticTransportError("SEC-RESPONSE-INTEGRITY", "content_length")

    def _raise_timeout_if_due(
        self,
        *,
        attempt_started: float,
        last_progress: float,
        reading: bool,
        body_started: bool,
        operation_deadline: float,
    ) -> None:
        now = self._clock.now()
        if now >= operation_deadline:
            if body_started:
                raise SyntheticTransportError("SEC-RESPONSE-INTEGRITY", "partial_body")
            raise SyntheticTransportError("SEC-TRANSPORT-TIMEOUT", "total_timeout")
        if reading:
            if now - last_progress >= READ_IDLE_TIMEOUT_SECONDS:
                if body_started:
                    raise SyntheticTransportError("SEC-RESPONSE-INTEGRITY", "partial_body")
                raise SyntheticTransportError("SEC-TRANSPORT-TIMEOUT", "read_idle_timeout")
        elif now - attempt_started >= CONNECT_TIMEOUT_SECONDS:
            raise SyntheticTransportError("SEC-TRANSPORT-TIMEOUT", "connect_timeout")
