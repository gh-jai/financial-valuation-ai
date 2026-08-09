"""Versioned canonical JSON and SHA-256 helpers for M9 artifacts."""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Mapping
from typing import Any


CANONICALIZATION_VERSION = "fvi-canonical-json-v1"


class CanonicalizationError(ValueError):
    """Raised when a value is not valid for the locked canonical representation."""


def _normalize(value: Any, active: set[int]) -> Any:
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise CanonicalizationError("canonical JSON rejects non-finite numbers")
        return value
    if isinstance(value, Mapping):
        identity = id(value)
        if identity in active:
            raise CanonicalizationError("canonical JSON rejects cyclic values")
        active.add(identity)
        try:
            normalized = {}
            for key, item in value.items():
                if not isinstance(key, str):
                    raise CanonicalizationError("canonical JSON object keys must be strings")
                normalized[key] = _normalize(item, active)
        finally:
            active.remove(identity)
        return normalized
    if isinstance(value, list):
        identity = id(value)
        if identity in active:
            raise CanonicalizationError("canonical JSON rejects cyclic values")
        active.add(identity)
        try:
            normalized_list = [_normalize(item, active) for item in value]
        finally:
            active.remove(identity)
        return normalized_list
    raise CanonicalizationError(f"unsupported canonical JSON type: {type(value).__name__}")


def _require_version(version: str) -> None:
    if version != CANONICALIZATION_VERSION:
        raise CanonicalizationError(f"unsupported canonicalization version: {version!r}")


def canonical_json(value: Any, version: str = CANONICALIZATION_VERSION) -> str:
    """Return the locked compact, Unicode-preserving canonical JSON representation."""

    _require_version(version)
    normalized = _normalize(value, set())
    return json.dumps(
        normalized,
        ensure_ascii=False,
        allow_nan=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def canonical_bytes(value: Any, version: str = CANONICALIZATION_VERSION) -> bytes:
    """Encode canonical JSON as UTF-8 bytes."""

    return canonical_json(value, version).encode("utf-8")


def canonical_sha256(value: Any, version: str = CANONICALIZATION_VERSION) -> str:
    """Return the lowercase SHA-256 digest of the canonical UTF-8 bytes."""

    return hashlib.sha256(canonical_bytes(value, version)).hexdigest()
