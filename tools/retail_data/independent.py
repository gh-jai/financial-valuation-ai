"""Implementation-separated canonicalization used to cross-check M9 hashes."""

from __future__ import annotations

import hashlib
import json
import math
from collections.abc import Mapping
from typing import Any


_SUPPORTED_VERSION = "fvi-canonical-json-v1"


class IndependentValidationError(ValueError):
    """Raised when independently recomputed input is not canonicalizable."""


def _normalize(value: Any, ancestors: frozenset[int]) -> Any:
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise IndependentValidationError("non-finite number")
        return value
    if isinstance(value, Mapping):
        identity = id(value)
        if identity in ancestors:
            raise IndependentValidationError("cyclic value")
        next_ancestors = ancestors | {identity}
        normalized = {}
        for key in value:
            if not isinstance(key, str):
                raise IndependentValidationError("non-string object key")
            normalized[key] = _normalize(value[key], next_ancestors)
        return normalized
    if isinstance(value, list):
        identity = id(value)
        if identity in ancestors:
            raise IndependentValidationError("cyclic value")
        next_ancestors = ancestors | {identity}
        return [_normalize(item, next_ancestors) for item in value]
    raise IndependentValidationError(f"unsupported type: {type(value).__name__}")


def independent_canonical_json(value: Any, version: str = _SUPPORTED_VERSION) -> str:
    """Reserialize without importing the production canonicalization implementation."""

    if version != _SUPPORTED_VERSION:
        raise IndependentValidationError(f"unsupported version: {version!r}")
    normalized = _normalize(value, frozenset())
    return json.dumps(
        normalized,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def independent_sha256(value: Any, version: str = _SUPPORTED_VERSION) -> str:
    """Independently recompute the canonical UTF-8 SHA-256 digest."""

    payload = independent_canonical_json(value, version).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()
