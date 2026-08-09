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


def _walk(value: Any, ancestors: frozenset[int]) -> None:
    if value is None or isinstance(value, (str, bool, int)):
        return
    if isinstance(value, float):
        if not math.isfinite(value):
            raise IndependentValidationError("non-finite number")
        return
    if isinstance(value, Mapping):
        identity = id(value)
        if identity in ancestors:
            raise IndependentValidationError("cyclic value")
        next_ancestors = ancestors | {identity}
        for key in value:
            if not isinstance(key, str):
                raise IndependentValidationError("non-string object key")
            _walk(value[key], next_ancestors)
        return
    if isinstance(value, list):
        identity = id(value)
        if identity in ancestors:
            raise IndependentValidationError("cyclic value")
        next_ancestors = ancestors | {identity}
        for item in value:
            _walk(item, next_ancestors)
        return
    raise IndependentValidationError(f"unsupported type: {type(value).__name__}")


def independent_canonical_json(value: Any, version: str = _SUPPORTED_VERSION) -> str:
    """Reserialize without importing the production canonicalization implementation."""

    if version != _SUPPORTED_VERSION:
        raise IndependentValidationError(f"unsupported version: {version!r}")
    _walk(value, frozenset())
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


def independent_sha256(value: Any, version: str = _SUPPORTED_VERSION) -> str:
    """Independently recompute the canonical UTF-8 SHA-256 digest."""

    payload = independent_canonical_json(value, version).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()
