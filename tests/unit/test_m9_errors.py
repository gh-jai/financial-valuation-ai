import json
from dataclasses import FrozenInstanceError

import pytest

from tools.retail_data.errors import ErrorSeverity, NextAction, RetailDataError
from tools.retail_data.redaction import REDACTED, redact_structure, redact_text


def test_error_has_stable_json_serializable_shape() -> None:
    error = RetailDataError(
        "REGISTRY-PENDING",
        "Provider approval is pending",
        ErrorSeverity.BLOCKING,
        False,
        ("snapshot:synthetic-1",),
        NextAction.UPDATE_REGISTRY,
    )
    payload = error.to_dict()
    assert list(payload) == [
        "code",
        "message",
        "severity",
        "retryable",
        "artifact_refs",
        "next_action",
    ]
    assert json.loads(json.dumps(payload))["code"] == "REGISTRY-PENDING"


def test_nested_secret_fields_are_redacted_without_mutating_input() -> None:
    source = {"headers": {"Authorization": "Bearer abc"}, "items": [{"api_key": "xyz"}]}
    redacted = redact_structure(source)
    assert redacted["headers"]["Authorization"] == REDACTED
    assert redacted["items"][0]["api_key"] == REDACTED
    assert source["headers"]["Authorization"] == "Bearer abc"


def test_authorization_and_query_credentials_are_redacted() -> None:
    text = "Authorization: Bearer abc123 https://e.test/?token=xyz&ok=1 password=hunter2"
    safe = redact_text(text)
    for secret in ("abc123", "xyz", "hunter2"):
        assert secret not in safe
    assert safe.count(REDACTED) == 3


def test_messages_are_flattened_and_bounded() -> None:
    safe = redact_text("first\r\nsecond " + "x" * 100, limit=24)
    assert "\n" not in safe and "\r" not in safe
    assert len(safe) == 24 and safe.endswith("…")
    with pytest.raises(ValueError):
        redact_text("message", limit=True)


def test_error_invariants_reject_unsafe_or_inconsistent_values() -> None:
    invalid = [
        ("bad", False, NextAction.STOP, ()),
        ("DATA-BAD", True, NextAction.STOP, ()),
        ("DATA-BAD", False, NextAction.RETRY_LATER, ()),
        ("DATA-BAD", False, NextAction.STOP, ("duplicate", "duplicate")),
        ("DATA-BAD", False, NextAction.STOP, ("unsafe ref",)),
    ]
    for code, retryable, action, refs in invalid:
        with pytest.raises((TypeError, ValueError)):
            RetailDataError(
                code, "safe", ErrorSeverity.BLOCKING, retryable, refs, action
            )


def test_error_is_frozen_and_redacts_message_on_construction() -> None:
    error = RetailDataError(
        "PROVIDER-ERROR",
        "api_key=do-not-log",
        ErrorSeverity.REVIEW,
        False,
        next_action=NextAction.CONTACT_SUPPORT,
    )
    assert "do-not-log" not in error.message
    with pytest.raises(FrozenInstanceError):
        error.message = "changed"  # type: ignore[misc]
