"""Strict M9-I4 policy, fixture, result, and safe-error contracts."""

from __future__ import annotations

import copy
import json
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from .canonical import CANONICALIZATION_VERSION, canonical_sha256
from .errors import ErrorSeverity, NextAction, RetailDataError
from .identity_contracts import strict_load
from .sec_endpoints import MAX_DECODED_BODY_BYTES, endpoint_specs


ROOT = Path(__file__).resolve().parents[2]
SCHEMAS = ROOT / "schemas"
SCHEMA_VERSION = "0.1.0"
_UTC = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
LOCKED_SYNTHETIC_FIXTURE_HASHES = frozenset(
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
_SAFE_ERROR = {
    "SEC-ADAPTER-DISABLED": ("SEC adapter is disabled", ErrorSeverity.BLOCKING, False, NextAction.STOP),
    "SEC-PROVIDER-DENIED": ("Provider authority is denied", ErrorSeverity.BLOCKING, False, NextAction.UPDATE_REGISTRY),
    "SEC-USER-AGENT-DENIED": ("Operator identity policy is not satisfied", ErrorSeverity.BLOCKING, False, NextAction.CONTACT_SUPPORT),
    "SEC-ENDPOINT-DENIED": ("Endpoint construction is denied", ErrorSeverity.BLOCKING, False, NextAction.STOP),
    "SEC-REDIRECT-DENIED": ("Redirect response is denied", ErrorSeverity.BLOCKING, False, NextAction.STOP),
    "SEC-RATE-LIMITED": ("Global request budget is unavailable", ErrorSeverity.REVIEW, True, NextAction.RETRY_LATER),
    "SEC-CIRCUIT-OPEN": ("Circuit breaker denies the attempt", ErrorSeverity.REVIEW, True, NextAction.RETRY_LATER),
    "SEC-TRANSPORT-TIMEOUT": ("Synthetic transport timed out", ErrorSeverity.REVIEW, True, NextAction.RETRY_LATER),
    "SEC-TRANSPORT-RESET": ("Synthetic transport reset before response", ErrorSeverity.REVIEW, True, NextAction.RETRY_LATER),
    "SEC-UPSTREAM-RETRYABLE": ("Synthetic upstream response is retryable", ErrorSeverity.REVIEW, True, NextAction.RETRY_LATER),
    "SEC-UPSTREAM-REJECTED": ("Synthetic upstream response was rejected", ErrorSeverity.BLOCKING, False, NextAction.CONTACT_SUPPORT),
    "SEC-RESPONSE-OVERSIZE": ("Response exceeds the locked resource limit", ErrorSeverity.BLOCKING, False, NextAction.STOP),
    "SEC-RESPONSE-INTEGRITY": ("Response integrity validation failed", ErrorSeverity.BLOCKING, False, NextAction.STOP),
    "SEC-CACHE-TAMPER": ("Cache integrity validation failed", ErrorSeverity.BLOCKING, False, NextAction.STOP),
    "SEC-HASH-MISMATCH": ("Artifact hash validation failed", ErrorSeverity.BLOCKING, False, NextAction.STOP),
}


class SecContractError(ValueError):
    """An M9-I4 artifact violated its strict contract."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def _schema(name: str, value: Mapping[str, Any]) -> None:
    schema = json.loads((SCHEMAS / name).read_text(encoding="utf-8"))
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(dict(value)),
        key=lambda item: list(item.absolute_path),
    )
    if errors:
        raise SecContractError("SEC-SCHEMA-INVALID", f"{name} validation failed")


def self_hash(value: Mapping[str, Any], field: str) -> str:
    """Hash an artifact without its self-hash field."""

    return canonical_sha256({key: copy.deepcopy(item) for key, item in value.items() if key != field})


def attach_self_hash(value: Mapping[str, Any], field: str) -> dict[str, Any]:
    result = copy.deepcopy(dict(value))
    result[field] = self_hash(result, field)
    return result


def require_self_hash(value: Mapping[str, Any], field: str) -> None:
    if value.get(field) != self_hash(value, field):
        raise SecContractError("SEC-HASH-MISMATCH", f"{field} does not match")


def provider_registry_subject(path: Path) -> tuple[dict[str, Any], str]:
    """Return strict registry content and its canonical artifact hash."""

    value = strict_load(path)
    return value, canonical_sha256(value)


def build_disabled_policy(provider_registry_hash: str) -> dict[str, Any]:
    """Build the exact disabled policy; there is no activation parameter."""

    capabilities = [
        {
            "order": spec.order,
            "capability": spec.capability,
            "provider_id": spec.provider_id,
            "endpoint_id": spec.endpoint_id,
            "endpoint_template": spec.endpoint_template,
            "host": spec.host,
            "redirect_policy": "deny_all",
            "accept_media": list(spec.accept_media),
            "max_decoded_body_bytes": MAX_DECODED_BODY_BYTES,
            "kill_switch": "disabled",
        }
        for spec in endpoint_specs()
    ]
    value = {
        "schema_version": SCHEMA_VERSION,
        "canonicalization_version": CANONICALIZATION_VERSION,
        "policy_id": "m9-i4-sec-adapter-policy",
        "policy_version": "0.1.0",
        "status": "candidate",
        "activation_state": "disabled",
        "network_state": "denied",
        "provider_registry_id": "m9-provider-license",
        "provider_registry_hash": provider_registry_hash,
        "capabilities": capabilities,
        "header_policy": {
            "allowed_headers": ["Accept", "Host", "User-Agent"],
            "authentication_class": "user_agent",
            "user_agent_policy": "operator_configured_not_stored",
            "store_user_agent_value": False,
            "caller_headers_allowed": False,
        },
        "global_rate_limit": {
            "algorithm": "deterministic_token_bucket_v1",
            "window_seconds": 1,
            "max_requests": 1,
            "burst_capacity": 1,
            "clock": "injected_monotonic",
            "scheduler": "injected",
            "queue_limit": 32,
            "queue_order": "eligible_at_then_request_sequence",
        },
        "retry_policy": {
            "max_attempts": 3,
            "backoff_seconds": [1, 2],
            "jitter": "none",
            "retryable_http_statuses": [429, 500, 502, 503, 504],
            "retryable_transport_events": ["connection_reset_before_response", "timeout"],
        },
        "timeout_policy": {
            "clock": "injected_monotonic",
            "connect_seconds": 5,
            "read_idle_seconds": 20,
            "total_seconds": 30,
            "outer_deadline_resets": False,
        },
        "circuit_breaker": {
            "scope": "provider_id_and_capability",
            "states": ["closed", "half_open", "open"],
            "failure_threshold": 5,
            "open_seconds": 60,
            "half_open_probe_limit": 1,
            "clock": "injected_monotonic",
            "persists_across_restart": False,
        },
        "cache_policy": {
            "store_contract": "m9-i3-content-addressed-store-v1",
            "write_once": True,
            "index_canonicalization": CANONICALIZATION_VERSION,
            "rehash_on_read": True,
            "rights_recheck": True,
            "kill_switch_recheck": True,
            "fallback_on_tamper": False,
        },
        "global_kill_switch": "disabled",
    }
    result = attach_self_hash(value, "policy_hash")
    _schema("sec-adapter-policy.schema.json", result)
    return result


def require_disabled_policy(
    value: Mapping[str, Any], provider_registry_hash: str
) -> None:
    """Require exact policy bytes for the referenced default-deny registry subject."""

    _schema("sec-adapter-policy.schema.json", value)
    require_self_hash(value, "policy_hash")
    if dict(value) != build_disabled_policy(provider_registry_hash):
        raise SecContractError("SEC-POLICY-DENIED", "policy differs from the locked disabled form")


def load_fixture(path: Path) -> dict[str, Any]:
    value = strict_load(path)
    _schema("sec-synthetic-transport-fixture.schema.json", value)
    require_self_hash(value, "fixture_hash")
    if value["fixture_hash"] not in LOCKED_SYNTHETIC_FIXTURE_HASHES:
        raise SecContractError("SEC-FIXTURE-DENIED", "fixture hash is not implementation locked")
    return value


def require_locked_fixture(value: Mapping[str, Any]) -> None:
    """Require strict provenance, self-hash, and the implementation allowlist."""

    require_self_hash(value, "fixture_hash")
    if (
        value.get("fixture_hash") not in LOCKED_SYNTHETIC_FIXTURE_HASHES
        or value.get("synthetic") is not True
        or value.get("network_state") != "denied"
        or value.get("capture_provenance") != "original_fixture"
    ):
        raise SecContractError("SEC-FIXTURE-DENIED", "fixture is not original and locked")


def validate_created_at(value: str) -> None:
    if not isinstance(value, str) or not _UTC.fullmatch(value):
        raise SecContractError("SEC-TIME-INVALID", "created_at must be canonical UTC seconds")


def safe_error(code: str, *artifact_refs: str) -> dict[str, Any]:
    """Create only fixed messages; no untrusted material enters the error."""

    try:
        message, severity, retryable, next_action = _SAFE_ERROR[code]
    except KeyError as exc:
        raise SecContractError("SEC-ERROR-CODE-INVALID", "error code is not locked") from exc
    return RetailDataError(
        code=code,
        message=message,
        severity=severity,
        retryable=retryable,
        artifact_refs=artifact_refs,
        next_action=next_action,
    ).to_dict()


def finalize_result(value: Mapping[str, Any]) -> dict[str, Any]:
    result = attach_self_hash(value, "result_hash")
    _schema("sec-adapter-result.schema.json", result)
    return result


def request_fingerprint(
    policy: Mapping[str, Any],
    *,
    provider_id: str,
    capability: str,
    endpoint_id: str,
    identifiers: Mapping[str, str],
    accept_media: tuple[str, ...],
    user_agent_policy_valid: bool,
) -> str:
    """Bind request semantics without an actual User-Agent or wall-clock value."""

    subject = {
        "policy_version": policy["policy_version"],
        "policy_hash": policy["policy_hash"],
        "provider_id": provider_id,
        "capability": capability,
        "endpoint_id": endpoint_id,
        "identifiers": dict(sorted(identifiers.items())),
        "accept_media": list(accept_media),
        "header_presence": {
            "accept": True,
            "host": True,
            "user_agent": user_agent_policy_valid,
        },
    }
    return canonical_sha256(subject)
