"""Implementation-separated validation for M9-I4 synthetic SEC adapter evidence."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import math
import re
import stat
from collections.abc import Mapping, Sequence
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"
CANONICALIZATION_VERSION = "fvi-canonical-json-v1"
MAX_RECORD_BYTES = 1_048_576
RETRYABLE = frozenset({429, 500, 502, 503, 504})
FIXTURE_HASHES = frozenset(
    {
        "437f3cb589a4867728604346a183d8dc3633ce8a62d963b8d800215d12a58544",
        "4d9e9c7728d0240eab7b8e509f296ff0f53294bbc2d721157903adea1b5c1086",
        "b7a41f43f4fd48da1378ac332262636854889dbb965d241a44c7144d13a40a2c",
        "e5b1441fc32d091d2ffe65ef12a57ca83889b18e134d845666b1c71bbb70c3ad",
        "d6f9a2bf3119d5823bcb911e891a781d0099bc712a6428ffa90fba110b0a563d",
        "33b2cef8affffa25b1e50dcb9f85c267e49a2dc11aa4826e567b01f847415efd",
        "ec9d2e8df6e9f6284f4c7d4de636f69a97c404f302ad432d6eea6af62c29af65",
        "4538d0080bd66ec5971ea0b2ef0b6e713ff09ed9534722c133c99a32773fec6b",
        "dd4331f82ca608f06d3fe1ffadf4f769459cc975fc33cb9a7657260fdca1f4f8",
        "cc0564bc4824c2c22aaabdc8828c097dc2366a373e0638631ffd217984c9e85a",
        "25a4b779dfa394d2ba76a20107d59acfcdc73282186440ee2970afb6c331d871",
    }
)
CAPABILITIES = (
    (
        "identity",
        "sec-identity",
        "sec-company-tickers-v1",
        "https://www.sec.gov/files/company_tickers.json",
        "www.sec.gov",
        ("application/json",),
    ),
    (
        "submissions",
        "sec-submissions",
        "sec-submissions-by-cik-v1",
        "https://data.sec.gov/submissions/CIK{cik}.json",
        "data.sec.gov",
        ("application/json",),
    ),
    (
        "filings",
        "sec-filings",
        "sec-filing-document-v1",
        "https://www.sec.gov/Archives/edgar/data/{cik}/{accession}/{document}",
        "www.sec.gov",
        ("application/xml", "text/html", "text/plain"),
    ),
    (
        "companyfacts",
        "sec-xbrl",
        "sec-companyfacts-by-cik-v1",
        "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json",
        "data.sec.gov",
        ("application/json",),
    ),
)
SAFE_ERRORS = {
    "SEC-ADAPTER-DISABLED",
    "SEC-CACHE-TAMPER",
    "SEC-CIRCUIT-OPEN",
    "SEC-ENDPOINT-DENIED",
    "SEC-HASH-MISMATCH",
    "SEC-PROVIDER-DENIED",
    "SEC-RATE-LIMITED",
    "SEC-REDIRECT-DENIED",
    "SEC-RESPONSE-INTEGRITY",
    "SEC-RESPONSE-OVERSIZE",
    "SEC-TRANSPORT-RESET",
    "SEC-TRANSPORT-TIMEOUT",
    "SEC-UPSTREAM-REJECTED",
    "SEC-UPSTREAM-RETRYABLE",
    "SEC-USER-AGENT-DENIED",
}
SUSPICIOUS = re.compile(
    r"(?i)(https?://|authorization|cookie|bearer|basic|password|secret|token|api[_-]?key|traceback|@)"
)
CACHE_INDEX_SCHEMA = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "type": "object",
    "additionalProperties": False,
    "required": [
        "schema_version",
        "canonicalization_version",
        "cache_index_id",
        "request_fingerprint",
        "record_hash",
        "byte_count",
        "retrieved_at",
        "endpoint_id",
        "capability",
        "provider_id",
        "policy_hash",
        "fixture_hash",
        "media_type",
        "expires_at",
        "network_state",
        "cache_index_hash",
    ],
    "properties": {
        "schema_version": {"const": "0.1.0"},
        "canonicalization_version": {"const": CANONICALIZATION_VERSION},
        "cache_index_id": {"type": "string", "pattern": "^SCI-[A-F0-9]{24}$"},
        "request_fingerprint": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
        "record_hash": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
        "byte_count": {"type": "integer", "minimum": 1, "maximum": MAX_RECORD_BYTES},
        "retrieved_at": {
            "type": "string",
            "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$",
        },
        "endpoint_id": {"type": "string", "minLength": 1, "maxLength": 128},
        "capability": {"enum": ["identity", "submissions", "filings", "companyfacts"]},
        "provider_id": {"enum": ["sec-identity", "sec-submissions", "sec-filings", "sec-xbrl"]},
        "policy_hash": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
        "fixture_hash": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
        "media_type": {
            "enum": ["application/json", "application/xml", "text/html", "text/plain"]
        },
        "expires_at": {
            "type": "string",
            "pattern": "^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$",
        },
        "network_state": {"const": "denied"},
        "cache_index_hash": {"type": "string", "pattern": "^[a-f0-9]{64}$"},
    },
}


class _UniqueLoader(yaml.SafeLoader):
    pass


def _yaml_mapping(loader: _UniqueLoader, node: yaml.MappingNode, deep: bool = False) -> dict:
    result: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in result:
            raise ValueError("duplicate YAML key")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


_UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _yaml_mapping)


def _json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def strict_json(path: Path) -> dict[str, Any]:
    value = json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=_json_object,
        parse_constant=lambda token: (_ for _ in ()).throw(ValueError(token)),
    )
    if not isinstance(value, dict):
        raise ValueError("artifact root must be an object")
    return value


def _normalize(value: Any, active: set[int] | None = None) -> Any:
    active = set() if active is None else active
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite number")
        return value
    if isinstance(value, Mapping):
        marker = id(value)
        if marker in active:
            raise ValueError("cyclic object")
        active.add(marker)
        try:
            return {str(key): _normalize(item, active) for key, item in value.items()}
        finally:
            active.remove(marker)
    if isinstance(value, list):
        marker = id(value)
        if marker in active:
            raise ValueError("cyclic array")
        active.add(marker)
        try:
            return [_normalize(item, active) for item in value]
        finally:
            active.remove(marker)
    raise ValueError("unsupported canonical type")


def _canonical(value: Any) -> bytes:
    return json.dumps(
        _normalize(value),
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def _sha(value: Any) -> str:
    return hashlib.sha256(_canonical(value)).hexdigest()


def _without(value: Mapping[str, Any], field: str) -> dict[str, Any]:
    return {key: copy.deepcopy(item) for key, item in value.items() if key != field}


def _schema_errors(name: str, value: Mapping[str, Any]) -> list[Any]:
    schema = json.loads((SCHEMAS / name).read_text(encoding="utf-8"))
    return sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(dict(value)),
        key=lambda item: list(item.absolute_path),
    )


def _cache_schema_errors(value: Mapping[str, Any]) -> list[Any]:
    return sorted(
        Draft202012Validator(CACHE_INDEX_SCHEMA).iter_errors(dict(value)),
        key=lambda item: list(item.absolute_path),
    )


def _utc(value: Any) -> datetime:
    if not isinstance(value, str) or not re.fullmatch(
        r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z", value
    ):
        raise ValueError("non-canonical UTC timestamp")
    parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    if parsed.isoformat(timespec="seconds").replace("+00:00", "Z") != value:
        raise ValueError("non-canonical UTC timestamp")
    return parsed


def _timestamp(created_at: str, seconds: float) -> str:
    base = datetime.fromisoformat(created_at[:-1] + "+00:00")
    value = base + timedelta(seconds=seconds)
    return value.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _fixture_body(event: Mapping[str, Any]) -> bytes:
    if event["body_encoding"] != "utf-8":
        import base64

        return base64.b64decode(event["body"], validate=True)
    return event["body"].encode("utf-8")


def _expected_attempts(
    fixture: Mapping[str, Any], created_at: str, token_start: int, initial_delay: float
) -> tuple[list[dict], bytes | None]:
    events = list(fixture["events"])
    cursor = 0
    elapsed = initial_delay
    attempts: list[dict] = []
    accepted: bytes | None = None
    for attempt_number in range(1, 4):
        if attempt_number > 1:
            elapsed += float((1, 2)[attempt_number - 2])
        started = elapsed
        terminal: Mapping[str, Any] | None = None
        while cursor < len(events):
            event = events[cursor]
            cursor += 1
            if event["kind"] == "advance_time":
                elapsed += float(event["seconds"])
                continue
            terminal = event
            break
        if terminal is None:
            break
        kind = terminal["kind"]
        if elapsed >= 30:
            attempts.append(
                {
                    "attempt": attempt_number,
                    "token_sequence": token_start + attempt_number - 1,
                    "started_at": _timestamp(created_at, started),
                    "ended_at": _timestamp(created_at, elapsed),
                    "outcome": "timeout",
                }
            )
            break
        if kind == "response" and elapsed - started >= 5:
            attempts.append(
                {
                    "attempt": attempt_number,
                    "token_sequence": token_start + attempt_number - 1,
                    "started_at": _timestamp(created_at, started),
                    "ended_at": _timestamp(created_at, elapsed),
                    "outcome": "timeout",
                }
            )
            if attempt_number < 3:
                continue
            break
        if kind in {"timeout", "connection_reset_before_response"}:
            attempts.append(
                {
                    "attempt": attempt_number,
                    "token_sequence": token_start + attempt_number - 1,
                    "started_at": _timestamp(created_at, started),
                    "ended_at": _timestamp(created_at, elapsed),
                    "outcome": kind,
                }
            )
            if attempt_number < 3:
                continue
            break
        status = terminal["status"]
        if status in RETRYABLE:
            attempts.append(
                {
                    "attempt": attempt_number,
                    "token_sequence": token_start + attempt_number - 1,
                    "started_at": _timestamp(created_at, started),
                    "ended_at": _timestamp(created_at, elapsed),
                    "outcome": f"http_{status}",
                }
            )
            if attempt_number < 3:
                continue
            break
        attempts.append(
            {
                "attempt": attempt_number,
                "token_sequence": token_start + attempt_number - 1,
                "started_at": _timestamp(created_at, started),
                "ended_at": _timestamp(created_at, elapsed),
                "outcome": "response_accepted",
            }
        )
        if 200 <= status <= 299:
            accepted = _fixture_body(terminal)
        break
    return attempts, accepted


def _standalone_result_hash(
    result: Mapping[str, Any], token_start: int, initial_delay: float
) -> str:
    """Normalize a shared global-limiter offset back to the locked standalone replay."""

    subject = _without(result, "result_hash")
    attempts = subject.get("attempts")
    if not isinstance(attempts, list):
        raise ValueError("attempts are not an array")
    offset = token_start - 1
    for attempt in attempts:
        if not isinstance(attempt, Mapping):
            raise ValueError("attempt is not an object")
        token = attempt.get("token_sequence")
        if isinstance(token, bool) or not isinstance(token, int) or token <= offset:
            raise ValueError("token sequence is invalid")
        attempt["token_sequence"] = token - offset
        for field in ("started_at", "ended_at"):
            timestamp = _utc(attempt.get(field)) - timedelta(seconds=initial_delay)
            attempt[field] = timestamp.isoformat(timespec="seconds").replace("+00:00", "Z")
    return _sha(subject)


def _raw_path(store_root: Path, digest: str) -> Path:
    components = [store_root, store_root / "records", store_root / "records/sha256"]
    target = components[-1] / digest[:2] / digest
    components.append(target.parent)
    for component in components:
        metadata = component.lstat()
        if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
            raise ValueError("unsafe store component")
    metadata = target.lstat()
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode):
        raise ValueError("unsafe raw record")
    return target


def validate_m9_i4_sec_adapters(
    *,
    policy: Mapping[str, Any],
    fixture: Mapping[str, Any],
    result: Mapping[str, Any],
    provider_registry_path: Path,
    store_root: Path,
    validation_result_id: str,
    created_at: str,
    cache_index: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Independently validate exact offline policy, replay, hashes, and raw closure."""

    findings: list[dict[str, str]] = []

    def finding(code: str, message: str, subject: str) -> None:
        item = {"code": code, "message": message, "subject": subject}
        if item not in findings:
            findings.append(item)

    for schema_name, value, label in (
        ("sec-adapter-policy.schema.json", policy, "policy"),
        ("sec-synthetic-transport-fixture.schema.json", fixture, "fixture"),
        ("sec-adapter-result.schema.json", result, "result"),
    ):
        if _schema_errors(schema_name, value):
            finding("M9I4-SCHEMA-INVALID", f"{label} schema validation failed", label)
    for value, field, label in (
        (policy, "policy_hash", "policy"),
        (fixture, "fixture_hash", "fixture"),
        (result, "result_hash", "result"),
    ):
        try:
            if value.get(field) != _sha(_without(value, field)):
                finding("M9I4-HASH-MISMATCH", f"{label} self-hash does not match", label)
        except (TypeError, ValueError):
            finding("M9I4-HASH-MISMATCH", f"{label} cannot be independently hashed", label)
    if fixture.get("fixture_hash") not in FIXTURE_HASHES:
        finding("M9I4-FIXTURE-NOT-LOCKED", "fixture hash is not in the original set", "fixture")

    try:
        registry = yaml.load(provider_registry_path.read_text(encoding="utf-8"), Loader=_UniqueLoader)
        registry_hash = _sha(registry)
    except (OSError, UnicodeError, yaml.YAMLError, TypeError, ValueError):
        registry, registry_hash = {}, "0" * 64
        finding("M9I4-REGISTRY-INVALID", "provider registry cannot be loaded strictly", "registry")
    providers = registry.get("providers", []) if isinstance(registry, Mapping) else []
    provider_map = {
        item.get("provider_id"): item for item in providers if isinstance(item, Mapping)
    }
    if registry.get("registry_id") != "m9-provider-license" or len(provider_map) != 4:
        finding("M9I4-REGISTRY-CLOSURE", "provider registry identity or cardinality differs", "registry")
    for _, provider_id, _, template, host, _ in CAPABILITIES:
        item = provider_map.get(provider_id, {})
        if (
            item.get("status") != "pending"
            or item.get("live_activation") != "disabled"
            or item.get("endpoint_templates") != [template]
            or item.get("host_allowlist") != [host]
            or item.get("redirect_host_allowlist") != []
            or any(item.get("rights", {}).get(right) is not False for right in ("storage", "display", "export", "redistribution"))
        ):
            finding("M9I4-AUTHORITY-DRIFT", f"{provider_id} is not exact default deny", "registry")
    if policy.get("provider_registry_hash") != registry_hash or result.get("provider_registry_hash") != registry_hash:
        finding("M9I4-REGISTRY-HASH", "registry hash reference does not close", "registry")

    expected_capabilities = []
    for order, (capability, provider_id, endpoint_id, template, host, media) in enumerate(CAPABILITIES):
        expected_capabilities.append(
            {
                "order": order,
                "capability": capability,
                "provider_id": provider_id,
                "endpoint_id": endpoint_id,
                "endpoint_template": template,
                "host": host,
                "redirect_policy": "deny_all",
                "accept_media": list(media),
                "max_decoded_body_bytes": MAX_RECORD_BYTES,
                "kill_switch": "disabled",
            }
        )
    if policy.get("capabilities") != expected_capabilities:
        finding("M9I4-CAPABILITY-CLOSURE", "capability endpoint closure differs", "policy")
    if (
        policy.get("activation_state") != "disabled"
        or policy.get("network_state") != "denied"
        or policy.get("global_kill_switch") != "disabled"
        or result.get("activation_state") != "disabled"
        or result.get("network_state") != "denied"
    ):
        finding("M9I4-AUTHORITY-DRIFT", "offline authority state differs", "policy")
    controls = (
        policy.get("global_rate_limit", {}).get("max_requests") == 1,
        policy.get("global_rate_limit", {}).get("queue_limit") == 32,
        policy.get("retry_policy", {}).get("max_attempts") == 3,
        policy.get("retry_policy", {}).get("backoff_seconds") == [1, 2],
        policy.get("timeout_policy", {}).get("total_seconds") == 30,
        policy.get("circuit_breaker", {}).get("failure_threshold") == 5,
        policy.get("circuit_breaker", {}).get("open_seconds") == 60,
    )
    if not all(controls):
        finding("M9I4-STATE-MACHINE-DRIFT", "limiter/retry/timeout/breaker controls differ", "policy")

    capability_map = {row[0]: row for row in CAPABILITIES}
    capability = fixture.get("capability")
    if capability not in capability_map:
        finding("M9I4-ENDPOINT-INVALID", "fixture capability is invalid", "fixture")
        spec = CAPABILITIES[0]
    else:
        spec = capability_map[capability]
    _, provider_id, endpoint_id, _, _, media = spec
    identifiers = fixture.get("identifiers", {})
    cik = identifiers.get("cik") if isinstance(identifiers, Mapping) else None
    expected_keys = {
        "identity": set(),
        "submissions": {"cik"},
        "filings": {"cik", "accession", "document"},
        "companyfacts": {"cik"},
    }.get(capability, set())
    valid_identifiers = isinstance(identifiers, Mapping) and set(identifiers) == expected_keys
    if cik is not None and (not isinstance(cik, str) or not re.fullmatch(r"[0-9]{10}", cik, re.ASCII)):
        valid_identifiers = False
    if capability == "filings":
        accession = identifiers.get("accession")
        document = identifiers.get("document")
        valid_identifiers = valid_identifiers and bool(
            isinstance(accession, str)
            and re.fullmatch(r"[0-9]{10}-[0-9]{2}-[0-9]{6}", accession, re.ASCII)
            and isinstance(document, str)
            and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", document, re.ASCII)
            and ".." not in document
            and "%" not in document
            and not document.startswith(".")
            and not document.endswith(".")
        )
    if not valid_identifiers:
        finding("M9I4-ENDPOINT-INVALID", "strict identifiers are invalid", "fixture")
    fingerprint_subject = {
        "policy_version": policy.get("policy_version"),
        "policy_hash": policy.get("policy_hash"),
        "provider_id": provider_id,
        "capability": capability,
        "endpoint_id": endpoint_id,
        "identifiers": dict(sorted(identifiers.items())) if isinstance(identifiers, Mapping) else {},
        "accept_media": list(media),
        "header_presence": {
            "accept": True,
            "host": True,
            "user_agent": fixture.get("user_agent_policy_valid") is True,
        },
    }
    expected_fingerprint = _sha(fingerprint_subject)
    if result.get("request_fingerprint") != expected_fingerprint:
        finding("M9I4-FINGERPRINT-MISMATCH", "request fingerprint does not match", "result")
    if (
        result.get("provider_id") != provider_id
        or result.get("capability") != capability
        or result.get("endpoint_id") != endpoint_id
        or result.get("policy_hash") != policy.get("policy_hash")
    ):
        finding("M9I4-RESULT-CLOSURE", "result references do not close", "result")

    result_attempts = result.get("attempts")
    token_start = 1
    initial_delay = 0.0
    if isinstance(result_attempts, list) and result_attempts:
        first_token = result_attempts[0].get("token_sequence") if isinstance(result_attempts[0], Mapping) else None
        if isinstance(first_token, bool) or not isinstance(first_token, int) or first_token < 1:
            finding("M9I4-ATTEMPT-MISMATCH", "first global token sequence is invalid", "result")
        else:
            token_start = first_token
        try:
            initial_delay = (
                _utc(result_attempts[0].get("started_at")) - _utc(result.get("created_at"))
            ).total_seconds()
            if not 0 <= initial_delay <= 1:
                raise ValueError("initial limiter delay exceeds one window")
        except (TypeError, ValueError):
            initial_delay = 0.0
            finding("M9I4-ATTEMPT-MISMATCH", "initial limiter delay is invalid", "result")
    try:
        expected_attempts, accepted = _expected_attempts(
            fixture, result.get("created_at", ""), token_start, initial_delay
        )
    except (KeyError, TypeError, ValueError, UnicodeError):
        expected_attempts, accepted = [], None
        finding("M9I4-REPLAY-INVALID", "fixture replay failed", "fixture")
    if result.get("attempts") != expected_attempts:
        finding("M9I4-ATTEMPT-MISMATCH", "attempt/token/retry replay differs", "result")
    try:
        standalone_hash = _standalone_result_hash(result, token_start, initial_delay)
    except (TypeError, ValueError):
        standalone_hash = None
    if fixture.get("expected_result_hash") != standalone_hash:
        finding("M9I4-EXPECTED-RESULT", "fixture does not bind the result hash", "result")

    raw = result.get("raw_record")
    raw_content = b""
    if result.get("status") == "succeeded":
        if not isinstance(raw, Mapping):
            finding("M9I4-RAW-MISSING", "successful result has no raw record", "raw_record")
        else:
            try:
                target = _raw_path(store_root, str(raw.get("content_hash")))
                raw_content = target.read_bytes()
                if (
                    not raw_content
                    or len(raw_content) > MAX_RECORD_BYTES
                    or hashlib.sha256(raw_content).hexdigest() != raw.get("content_hash")
                    or len(raw_content) != raw.get("byte_count")
                    or accepted != raw_content
                    or raw.get("record_id") != "REC-" + str(raw.get("content_hash"))[:24].upper()
                ):
                    raise ValueError("raw closure mismatch")
            except (OSError, ValueError):
                finding("M9I4-RAW-TAMPER", "raw record failed independent rehash", "raw_record")
    elif raw is not None:
        finding("M9I4-RAW-STATE", "failed result must not reference raw bytes", "result")

    errors = result.get("errors", [])
    if not isinstance(errors, Sequence) or isinstance(errors, (str, bytes)):
        finding("M9I4-ERROR-SHAPE", "safe errors must be an array", "result")
    else:
        for item in errors:
            if (
                not isinstance(item, Mapping)
                or item.get("code") not in SAFE_ERRORS
                or SUSPICIOUS.search(str(item.get("message", "")))
                or len(str(item.get("message", ""))) > 240
            ):
                finding("M9I4-ERROR-UNSAFE", "safe error taxonomy or redaction failed", "result")

    if cache_index is not None:
        if not isinstance(cache_index, Mapping) or _cache_schema_errors(cache_index):
            finding("M9I4-CACHE-SCHEMA", "cache index schema validation failed", "cache_index")
        try:
            retrieved_at = _utc(cache_index.get("retrieved_at"))
            expires_at = _utc(cache_index.get("expires_at"))
            validated_at = _utc(created_at)
            provider_expiry = datetime.fromisoformat(
                str(provider_map.get(provider_id, {}).get("expires_on"))
            ).date()
            time_valid = (
                retrieved_at < expires_at
                and retrieved_at <= validated_at < expires_at
                and validated_at.date() <= provider_expiry
            )
        except (TypeError, ValueError):
            time_valid = False
        provider = provider_map.get(provider_id, {})
        authority_valid = (
            provider.get("status") == "pending"
            and provider.get("live_activation") == "disabled"
            and provider.get("rights", {}).get("storage") is False
            and provider.get("retention_days") == 0
            and provider.get("territories") == ["US"]
        )
        cache_subject = _without(cache_index, "cache_index_hash")
        if (
            cache_index.get("cache_index_hash") != _sha(cache_subject)
            or cache_index.get("cache_index_id")
            != "SCI-" + expected_fingerprint[:24].upper()
            or cache_index.get("request_fingerprint") != expected_fingerprint
            or cache_index.get("policy_hash") != policy.get("policy_hash")
            or cache_index.get("fixture_hash") != fixture.get("fixture_hash")
            or cache_index.get("record_hash") != (raw or {}).get("content_hash")
            or cache_index.get("byte_count") != len(raw_content)
            or cache_index.get("media_type") != (raw or {}).get("media_type")
            or cache_index.get("media_type") not in media
            or cache_index.get("provider_id") != provider_id
            or cache_index.get("capability") != capability
            or cache_index.get("endpoint_id") != endpoint_id
            or cache_index.get("network_state") != "denied"
            or not time_valid
            or not authority_valid
        ):
            finding("M9I4-CACHE-CLOSURE", "cache index reference closure failed", "cache_index")

    subjects = [
        {"kind": "adapter_policy", "identifier": str(policy.get("policy_id", "policy")), "hash": str(policy.get("policy_hash", "0" * 64))},
        {"kind": "synthetic_fixture", "identifier": str(fixture.get("fixture_id", "fixture")), "hash": str(fixture.get("fixture_hash", "0" * 64))},
        {"kind": "adapter_result", "identifier": str(result.get("result_id", "result")), "hash": str(result.get("result_hash", "0" * 64))},
        {"kind": "provider_registry", "identifier": "m9-provider-license", "hash": registry_hash},
    ]
    if isinstance(raw, Mapping):
        subjects.append({"kind": "raw_record", "identifier": str(raw.get("record_id", "raw")), "hash": str(raw.get("content_hash", "0" * 64))})
    if cache_index is not None:
        subjects.append({"kind": "cache_index", "identifier": str(cache_index.get("cache_index_id", "cache")), "hash": str(cache_index.get("cache_index_hash", "0" * 64))})
    subjects.sort(key=lambda item: (item["kind"], item["identifier"]))
    checks = sorted(
        [
            "authority_and_registry",
            "cache_reference_closure",
            "capability_endpoint_closure",
            "circuit_breaker_replay",
            "fixture_provenance",
            "hash_and_reference_closure",
            "limiter_and_attempt_accounting",
            "request_fingerprint",
            "retry_timeout_replay",
            "safe_error_redaction",
            "stored_record_rehash",
        ]
    )
    findings.sort(key=lambda item: (item["code"], item["subject"], item["message"]))
    validation = {
        "schema_version": "0.1.0",
        "canonicalization_version": CANONICALIZATION_VERSION,
        "validation_result_id": validation_result_id,
        "created_at": created_at,
        "implementation_separation": "independent",
        "network_state": "denied",
        "subjects": subjects,
        "checks": checks,
        "status": "failed" if findings else "passed",
        "findings": findings,
    }
    validation["validation_result_hash"] = _sha(validation)
    if _schema_errors("sec-adapter-validation-result.schema.json", validation):
        raise ValueError("constructed validation result violates its schema")
    return validation


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--store-root", type=Path, required=True)
    parser.add_argument("--cache-index", type=Path)
    parser.add_argument("--validation-result-id", required=True)
    parser.add_argument("--created-at", required=True)
    arguments = parser.parse_args()
    value = validate_m9_i4_sec_adapters(
        policy=strict_json(arguments.policy),
        fixture=strict_json(arguments.fixture),
        result=strict_json(arguments.result),
        provider_registry_path=arguments.registry,
        store_root=arguments.store_root.resolve(),
        cache_index=strict_json(arguments.cache_index) if arguments.cache_index else None,
        validation_result_id=arguments.validation_result_id,
        created_at=arguments.created_at,
    )
    print(json.dumps(value, indent=2, sort_keys=True))
    return 0 if value["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
