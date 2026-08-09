"""Immutable, user-safe error records for the M9 retail-data boundary."""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass
from enum import Enum
from typing import Any

from .redaction import redact_text


_CODE = re.compile(r"^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+$")
_REFERENCE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/-]{0,127}$")


class ErrorSeverity(str, Enum):
    BLOCKING = "blocking"
    REVIEW = "review"
    WARNING = "warning"


class NextAction(str, Enum):
    VERIFY_IDENTITY = "verify_identity"
    UPDATE_REGISTRY = "update_registry"
    RETRY_LATER = "retry_later"
    CONTACT_SUPPORT = "contact_support"
    STOP = "stop"


@dataclass(frozen=True, slots=True)
class RetailDataError:
    """A stable error shape that never carries raw provider material."""

    code: str
    message: str
    severity: ErrorSeverity
    retryable: bool
    artifact_refs: tuple[str, ...] = ()
    next_action: NextAction = NextAction.STOP

    def __post_init__(self) -> None:
        if not isinstance(self.code, str) or not _CODE.fullmatch(self.code):
            raise ValueError("error code must be a stable uppercase namespaced identifier")
        if not isinstance(self.severity, ErrorSeverity):
            raise TypeError("severity must be an ErrorSeverity")
        if type(self.retryable) is not bool:
            raise TypeError("retryable must be a boolean")
        if not isinstance(self.next_action, NextAction):
            raise TypeError("next_action must be a NextAction")
        if self.retryable != (self.next_action is NextAction.RETRY_LATER):
            raise ValueError("retryable errors must use retry_later, and vice versa")
        safe_message = redact_text(self.message)
        if not safe_message:
            raise ValueError("message must not be empty")
        object.__setattr__(self, "message", safe_message)
        if not isinstance(self.artifact_refs, Sequence) or isinstance(
            self.artifact_refs, (str, bytes)
        ):
            raise TypeError("artifact_refs must be a non-string sequence")
        refs = tuple(self.artifact_refs)
        if len(set(refs)) != len(refs):
            raise ValueError("artifact references must be unique")
        if any(not isinstance(ref, str) or not _REFERENCE.fullmatch(ref) for ref in refs):
            raise ValueError("artifact reference is not a bounded safe identifier")
        object.__setattr__(self, "artifact_refs", refs)

    def to_dict(self) -> dict[str, Any]:
        """Return a serialization-ready copy of the stable representation."""

        return {
            "code": self.code,
            "message": self.message,
            "severity": self.severity.value,
            "retryable": self.retryable,
            "artifact_refs": list(self.artifact_refs),
            "next_action": self.next_action.value,
        }
