"""Bounded redaction for untrusted M9 error material."""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any


REDACTED = "[REDACTED]"
DEFAULT_MESSAGE_LIMIT = 512
_SECRET_KEY = re.compile(
    r"(?:authorization|cookie|credential|password|passwd|secret|session|token|api[_-]?key)",
    re.IGNORECASE,
)
_AUTHORIZATION = re.compile(
    r"(?i)\b(authorization\s*[:=]\s*)(?:bearer|basic)?\s*[^\s,;]+"
)
_COOKIE_HEADER = re.compile(r"(?im)\b((?:set-)?cookie\s*[:=]\s*)[^\r\n]*")
_NAMED_SECRET = re.compile(
    r"(?i)\b(api[_-]?key|access[_-]?token|refresh[_-]?token|password|passwd|"
    r"credential|session(?:id)?|token|secret)"
    r"(\s*[:=]\s*)[^\s&,;]+"
)
_QUERY_SECRET = re.compile(
    r"(?i)([?&](?:api[_-]?key|access[_-]?token|refresh[_-]?token|password|passwd|"
    r"credential|session(?:id)?|token|secret)=)[^&#\s]+"
)


def redact_text(value: object, limit: int = DEFAULT_MESSAGE_LIMIT) -> str:
    """Remove common credentials, flatten lines, and bound an untrusted message."""

    if isinstance(limit, bool) or not isinstance(limit, int) or limit < 1:
        raise ValueError("redaction limit must be a positive integer")
    text = str(value).replace("\x00", " ")
    text = _COOKIE_HEADER.sub(r"\1" + REDACTED, text)
    text = " ".join(text.splitlines())
    text = _AUTHORIZATION.sub(r"\1" + REDACTED, text)
    text = _NAMED_SECRET.sub(r"\1\2" + REDACTED, text)
    text = _QUERY_SECRET.sub(r"\1" + REDACTED, text)
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 1)] + "…"


def redact_structure(value: Any) -> Any:
    """Return a recursively redacted JSON-like copy."""

    if isinstance(value, Mapping):
        return {
            str(key): REDACTED if _SECRET_KEY.search(str(key)) else redact_structure(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact_structure(item) for item in value]
    if isinstance(value, tuple):
        return tuple(redact_structure(item) for item in value)
    if isinstance(value, str):
        return redact_text(value)
    return value
