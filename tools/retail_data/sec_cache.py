"""Tamper-evident M9-I4 cache references over the M9-I3 write-once store."""

from __future__ import annotations

import copy
import base64
import hashlib
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any

from .canonical import CANONICALIZATION_VERSION, canonical_sha256
from .sec_contracts import (
    LOCKED_SYNTHETIC_FIXTURE_HASHES,
    require_disabled_policy,
    require_self_hash,
)
from .storage import ContentAddressedStore, StorageError


SEC_CACHE_MEDIA_TYPES = frozenset(
    {"application/json", "application/xml", "text/html", "text/plain"}
)
PROVIDER_REGISTRY_HASH = "78a1c561aaf0baa199e698e053789ab47f4e0f1840c04c9962a5ad57d6ab4295"
_DATA_CATEGORY = {
    "identity": "issuer-identity",
    "submissions": "issuer-submissions",
    "filings": "filing-document",
    "companyfacts": "xbrl-facts",
}
_CACHEABLE_FIXTURE_HASHES = frozenset(
    {
        "437f3cb589a4867728604346a183d8dc3633ce8a62d963b8d800215d12a58544",
        "4d9e9c7728d0240eab7b8e509f296ff0f53294bbc2d721157903adea1b5c1086",
        "b7a41f43f4fd48da1378ac332262636854889dbb965d241a44c7144d13a40a2c",
        "e5b1441fc32d091d2ffe65ef12a57ca83889b18e134d845666b1c71bbb70c3ad",
    }
)
_FIELDS = frozenset(
    {
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
    }
)


class CacheError(ValueError):
    code = "SEC-CACHE-TAMPER"


@dataclass(frozen=True, slots=True)
class SyntheticCacheContext:
    """Locked original-fixture evidence; never provider or live authority."""

    fixture_hash: str
    provider_id: str
    capability: str
    endpoint_id: str
    accepted_bodies: frozenset[tuple[str, str]]


def synthetic_cache_context(fixture: Mapping[str, Any]) -> SyntheticCacheContext:
    """Bind cache tests to exact original response bytes in one locked fixture."""

    try:
        require_self_hash(fixture, "fixture_hash")
    except ValueError as exc:
        raise CacheError("synthetic fixture self-hash does not match") from exc
    if (
        fixture.get("fixture_hash") not in LOCKED_SYNTHETIC_FIXTURE_HASHES
        or fixture.get("fixture_hash") not in _CACHEABLE_FIXTURE_HASHES
        or fixture.get("synthetic") is not True
        or fixture.get("network_state") != "denied"
        or fixture.get("capture_provenance") != "original_fixture"
    ):
        raise CacheError("synthetic fixture provenance is denied")
    accepted_bodies: set[tuple[str, str]] = set()
    try:
        for event in fixture["events"]:
            if event["kind"] != "response" or not 200 <= event["status"] <= 299:
                continue
            if event["body_encoding"] == "utf-8":
                content = event["body"].encode("utf-8")
            else:
                content = base64.b64decode(event["body"], validate=True)
            media_type = event["headers"].get("Content-Type", "").split(";", 1)[0].strip().lower()
            accepted_bodies.add((hashlib.sha256(content).hexdigest(), media_type))
    except (KeyError, TypeError, UnicodeError, ValueError) as exc:
        raise CacheError("synthetic fixture body is invalid") from exc
    if not accepted_bodies:
        raise CacheError("synthetic fixture contains no accepted response body")
    return SyntheticCacheContext(
        str(fixture["fixture_hash"]),
        str(fixture["provider_id"]),
        str(fixture["capability"]),
        str(fixture["endpoint_id"]),
        frozenset(accepted_bodies),
    )


def _offline_policy(policy: Mapping[str, Any]) -> None:
    try:
        require_disabled_policy(policy, str(policy.get("provider_registry_hash", "")))
    except ValueError as exc:
        raise CacheError("cache test policy self-hash does not match") from exc
    if (
        policy.get("policy_id") != "m9-i4-sec-adapter-policy"
        or policy.get("status") != "candidate"
        or policy.get("activation_state") != "disabled"
        or policy.get("network_state") != "denied"
        or policy.get("global_kill_switch") != "disabled"
    ):
        raise CacheError("cache test policy is not exact offline default deny")


def _offline_authority(
    *,
    provider_registry: Mapping[str, Any],
    policy: Mapping[str, Any],
    fixture_context: SyntheticCacheContext,
    territory: str,
    evaluated_at: str,
) -> None:
    """Recheck the exact denied provider subject for synthetic-test cache use.

    This is deliberately not production storage authority.  It permits only original synthetic
    fixture bytes while proving that the current registry still grants no storage right and has
    not drifted into a live/approved state.
    """

    _offline_policy(policy)
    if (
        not isinstance(provider_registry, Mapping)
        or provider_registry.get("registry_id") != "m9-provider-license"
        or provider_registry.get("schema_version") != "0.1.0"
        or canonical_sha256(provider_registry) != PROVIDER_REGISTRY_HASH
        or policy.get("provider_registry_hash") != PROVIDER_REGISTRY_HASH
        or territory != "US"
    ):
        raise CacheError("synthetic cache provider authority does not close")
    providers = provider_registry.get("providers")
    if not isinstance(providers, list):
        raise CacheError("synthetic cache provider authority does not close")
    matching = [
        item
        for item in providers
        if isinstance(item, Mapping) and item.get("provider_id") == fixture_context.provider_id
    ]
    if len(matching) != 1:
        raise CacheError("synthetic cache provider authority does not close")
    record = matching[0]
    capability_policy = [
        item
        for item in policy.get("capabilities", [])
        if isinstance(item, Mapping) and item.get("capability") == fixture_context.capability
    ]
    try:
        expiry = date.fromisoformat(str(record["expires_on"]))
        evaluated_date = _utc(evaluated_at).date()
    except (KeyError, ValueError) as exc:
        raise CacheError("synthetic cache provider expiry is invalid") from exc
    if (
        len(capability_policy) != 1
        or capability_policy[0].get("provider_id") != fixture_context.provider_id
        or capability_policy[0].get("endpoint_id") != fixture_context.endpoint_id
        or capability_policy[0].get("kill_switch") != "disabled"
        or record.get("status") != "pending"
        or record.get("live_activation") != "disabled"
        or record.get("rights", {}).get("storage") is not False
        or record.get("retention_days") != 0
        or record.get("territories") != [territory]
        or record.get("data_categories") != [_DATA_CATEGORY[fixture_context.capability]]
        or expiry < evaluated_date
    ):
        raise CacheError("synthetic cache provider right, territory, or expiry is denied")


def _utc(value: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise CacheError("cache time is not canonical UTC")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise CacheError("cache time is not canonical UTC") from exc
    if parsed.isoformat().replace("+00:00", "Z") != value:
        raise CacheError("cache time is not canonical UTC")
    return parsed


class TamperEvidentCache:
    """Publish and revalidate immutable raw-record references; no fallback exists."""

    def __init__(self, store: ContentAddressedStore) -> None:
        self._store = store

    def publish(
        self,
        content: bytes,
        *,
        media_type: str,
        request_fingerprint: str,
        provider_id: str,
        capability: str,
        endpoint_id: str,
        policy_hash: str,
        fixture_context: SyntheticCacheContext,
        policy: Mapping[str, Any],
        provider_registry: Mapping[str, Any],
        territory: str,
        retrieved_at: str,
        expires_at: str,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        """Publish only synthetic bytes after an explicit final offline gate."""

        _offline_authority(
            provider_registry=provider_registry,
            policy=policy,
            fixture_context=fixture_context,
            territory=territory,
            evaluated_at=retrieved_at,
        )
        content_hash = hashlib.sha256(content).hexdigest()
        if (content_hash, media_type) not in fixture_context.accepted_bodies:
            raise CacheError("bytes are not bound to the locked synthetic fixture")
        if (
            provider_id != fixture_context.provider_id
            or capability != fixture_context.capability
            or endpoint_id != fixture_context.endpoint_id
        ):
            raise CacheError("cache endpoint is not bound to the locked synthetic fixture")
        if policy_hash != policy.get("policy_hash"):
            raise CacheError("cache policy hash does not match")
        if media_type not in SEC_CACHE_MEDIA_TYPES:
            raise CacheError("cache media type is denied")
        if _utc(expires_at) <= _utc(retrieved_at):
            raise CacheError("cache expiry must follow retrieval")
        try:
            # M9-I3 stores exact bytes and does not persist a media label. M9-I4 keeps the
            # independently validated response media type in this index instead of widening the
            # immutable M9-I3 implementation surface.
            stored = self._store.put_bytes(content, media_type="application/json")
        except StorageError as exc:
            raise CacheError("raw record publication failed") from exc
        # Re-evaluate the exact current authority after storage and immediately before emitting
        # the immutable index.  A concurrent registry/policy drift cannot inherit the first gate.
        _offline_authority(
            provider_registry=provider_registry,
            policy=policy,
            fixture_context=fixture_context,
            territory=territory,
            evaluated_at=retrieved_at,
        )
        subject = {
            "schema_version": "0.1.0",
            "canonicalization_version": CANONICALIZATION_VERSION,
            "cache_index_id": "SCI-" + request_fingerprint[:24].upper(),
            "request_fingerprint": request_fingerprint,
            "record_hash": stored.record_hash,
            "byte_count": stored.byte_length,
            "retrieved_at": retrieved_at,
            "endpoint_id": endpoint_id,
            "capability": capability,
            "provider_id": provider_id,
            "policy_hash": policy_hash,
            "fixture_hash": fixture_context.fixture_hash,
            "media_type": media_type,
            "expires_at": expires_at,
            "network_state": "denied",
        }
        index = copy.deepcopy(subject)
        index["cache_index_hash"] = canonical_sha256(subject)
        raw_record = {
            "record_id": "REC-" + stored.record_hash[:24].upper(),
            "content_hash": stored.record_hash,
            "byte_count": stored.byte_length,
            "media_type": media_type,
        }
        return index, raw_record

    def read(
        self,
        index: Mapping[str, Any],
        *,
        request_fingerprint: str,
        policy_hash: str,
        fixture_context: SyntheticCacheContext,
        policy: Mapping[str, Any],
        provider_registry: Mapping[str, Any],
        territory: str,
        evaluated_at: str,
    ) -> bytes:
        """Rehash every subject and stop on stale/tampered data without fallback."""

        _offline_authority(
            provider_registry=provider_registry,
            policy=policy,
            fixture_context=fixture_context,
            territory=territory,
            evaluated_at=evaluated_at,
        )
        if not isinstance(index, Mapping) or index.keys() != _FIELDS:
            raise CacheError("cache index fields are invalid")
        subject = {key: copy.deepcopy(value) for key, value in index.items() if key != "cache_index_hash"}
        if index.get("cache_index_hash") != canonical_sha256(subject):
            raise CacheError("cache index self-hash does not match")
        if (
            index.get("request_fingerprint") != request_fingerprint
            or index.get("policy_hash") != policy_hash
            or index.get("fixture_hash") != fixture_context.fixture_hash
            or index.get("network_state") != "denied"
            or index.get("media_type") not in SEC_CACHE_MEDIA_TYPES
            or index.get("provider_id") != fixture_context.provider_id
            or index.get("capability") != fixture_context.capability
            or index.get("endpoint_id") != fixture_context.endpoint_id
        ):
            raise CacheError("cache reference closure does not match")
        if _utc(evaluated_at) >= _utc(str(index["expires_at"])):
            raise CacheError("cache entry is stale")
        try:
            content = self._store.read_bytes(str(index["record_hash"]))
        except StorageError as exc:
            raise CacheError("cached raw record failed integrity validation") from exc
        if len(content) != index.get("byte_count"):
            raise CacheError("cached raw record byte count does not match")
        if (
            hashlib.sha256(content).hexdigest(),
            str(index["media_type"]),
        ) not in fixture_context.accepted_bodies:
            raise CacheError("cached bytes are not bound to the locked synthetic fixture")
        return content
