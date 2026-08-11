"""Bounded offline JSON/CSV import into the M9-I3 content-addressed store."""

from __future__ import annotations

import csv
import json
import math
import re
from collections.abc import Sequence
from datetime import datetime
from io import StringIO
from typing import Any

from .canonical import CANONICALIZATION_VERSION, canonical_sha256
from .storage import MAX_RECORD_BYTES, ContentAddressedStore


MAX_RECORDS = 2_000
MAX_CSV_COLUMNS = 128
MAX_CELL_CHARACTERS = 16_384
MAX_SOURCE_LABEL_CHARACTERS = 128
_DECIMAL = re.compile(r"^-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?$")
_ARCHIVE_SIGNATURES = (
    b"PK\x03\x04",
    b"\x1f\x8b",
    b"BZh",
    b"7z\xbc\xaf\x27\x1c",
    b"Rar!",
    b"%PDF-",
    b"\x7fELF",
    b"MZ",
)
_MAX_NUMBER_CHARACTERS = 128


class ManualImportError(ValueError):
    """A stable import rejection that never includes raw cells or input bytes."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def _utc(value: str) -> str:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ManualImportError("IMPORT-TIME-INVALID", "created_at must be canonical UTC")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise ManualImportError("IMPORT-TIME-INVALID", "created_at must be canonical UTC") from exc
    if parsed.utcoffset() is None or parsed.microsecond:
        raise ManualImportError("IMPORT-TIME-INVALID", "created_at must use whole UTC seconds")
    return parsed.strftime("%Y-%m-%dT%H:%M:%SZ")


def _source_label(value: str) -> str:
    if not isinstance(value, str):
        raise TypeError("source_label must be a string")
    if (
        not value
        or value != value.strip()
        or len(value) > MAX_SOURCE_LABEL_CHARACTERS
        or any(ord(character) < 32 or ord(character) == 127 for character in value)
    ):
        raise ManualImportError("IMPORT-LABEL-INVALID", "source label is not bounded safe text")
    return value


def _decode(content: bytes) -> str:
    if type(content) is not bytes:
        raise TypeError("manual import content must be bytes")
    if not content or len(content) > MAX_RECORD_BYTES:
        raise ManualImportError(
            "IMPORT-SIZE-DENIED", "manual input size is outside the locked limit"
        )
    if content.startswith(b"\xef\xbb\xbf"):
        raise ManualImportError("IMPORT-ENCODING-DENIED", "UTF-8 BOM is not accepted")
    if any(content.startswith(signature) for signature in _ARCHIVE_SIGNATURES):
        raise ManualImportError(
            "IMPORT-ARCHIVE-DENIED", "archive or executable input is not accepted"
        )
    if b"\x00" in content:
        raise ManualImportError("IMPORT-ENCODING-DENIED", "NUL is not accepted")
    try:
        return content.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise ManualImportError(
            "IMPORT-ENCODING-DENIED", "manual input must be UTF-8"
        ) from exc


def _reject_duplicate_pairs(pairs: Sequence[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ManualImportError(
                "IMPORT-JSON-DUPLICATE-KEY", "JSON object keys must be unique"
            )
        result[key] = value
    return result


def _reject_constant(_: str) -> None:
    raise ManualImportError("IMPORT-JSON-NONFINITE", "JSON numbers must be finite")


def _integer(value: str) -> int:
    if len(value) > _MAX_NUMBER_CHARACTERS:
        raise ManualImportError("IMPORT-JSON-NUMBER-LIMIT", "JSON number exceeds the limit")
    return int(value)


def _floating(value: str) -> float:
    if len(value) > _MAX_NUMBER_CHARACTERS:
        raise ManualImportError("IMPORT-JSON-NUMBER-LIMIT", "JSON number exceeds the limit")
    parsed = float(value)
    if not math.isfinite(parsed):
        raise ManualImportError("IMPORT-JSON-NONFINITE", "JSON numbers must be finite")
    return parsed


def _json_shape(text: str) -> tuple[int, tuple[str, ...]]:
    try:
        value = json.loads(
            text,
            object_pairs_hook=_reject_duplicate_pairs,
            parse_constant=_reject_constant,
            parse_int=_integer,
            parse_float=_floating,
        )
    except ManualImportError:
        raise
    except (json.JSONDecodeError, RecursionError) as exc:
        raise ManualImportError(
            "IMPORT-JSON-MALFORMED", "manual JSON is malformed"
        ) from exc
    records = value if isinstance(value, list) else [value]
    if (
        not records
        or len(records) > MAX_RECORDS
        or any(not isinstance(item, dict) for item in records)
    ):
        raise ManualImportError(
            "IMPORT-JSON-SHAPE-DENIED",
            "manual JSON must contain one object or a bounded non-empty array of objects",
        )
    return len(records), ()


def _formula(cell: str) -> bool:
    candidate = cell.lstrip()
    if not candidate:
        return False
    if candidate[0] in "=+@":
        return True
    return candidate.startswith("-") and _DECIMAL.fullmatch(candidate) is None


def _csv_shape(text: str) -> tuple[int, tuple[str, ...]]:
    previous_limit = csv.field_size_limit()
    csv.field_size_limit(MAX_CELL_CHARACTERS)
    try:
        reader = csv.reader(StringIO(text, newline=""), strict=True)
        try:
            header = next(reader)
        except StopIteration as exc:
            raise ManualImportError(
                "IMPORT-CSV-EMPTY", "manual CSV requires a header"
            ) from exc
        if (
            not header
            or len(header) > MAX_CSV_COLUMNS
            or any(not item or item != item.strip() for item in header)
            or len(set(header)) != len(header)
        ):
            raise ManualImportError(
                "IMPORT-CSV-HEADER-INVALID", "manual CSV header is invalid"
            )
        if any(len(item) > MAX_CELL_CHARACTERS or _formula(item) for item in header):
            raise ManualImportError(
                "IMPORT-CSV-FORMULA-DENIED", "spreadsheet formulas are not accepted"
            )
        count = 0
        for row in reader:
            count += 1
            if count > MAX_RECORDS:
                raise ManualImportError("IMPORT-ROW-LIMIT", "manual CSV exceeds the row limit")
            if len(row) != len(header):
                raise ManualImportError(
                    "IMPORT-CSV-WIDTH-INVALID", "manual CSV row width is inconsistent"
                )
            for cell in row:
                if len(cell) > MAX_CELL_CHARACTERS:
                    raise ManualImportError(
                        "IMPORT-CELL-LIMIT", "manual CSV cell exceeds the limit"
                    )
                if _formula(cell):
                    raise ManualImportError(
                        "IMPORT-CSV-FORMULA-DENIED", "spreadsheet formulas are not accepted"
                    )
        if count == 0:
            raise ManualImportError("IMPORT-CSV-EMPTY", "manual CSV requires a data row")
        return count, tuple(header)
    except csv.Error as exc:
        raise ManualImportError("IMPORT-CSV-MALFORMED", "manual CSV is malformed") from exc
    finally:
        csv.field_size_limit(previous_limit)


def import_manual_bytes(
    store: ContentAddressedStore,
    content: bytes,
    *,
    media_type: str,
    source_label: str,
    created_at: str,
) -> dict[str, Any]:
    """Validate complete input before atomically storing its exact bytes."""

    if not isinstance(store, ContentAddressedStore):
        raise TypeError("store must be a ContentAddressedStore")
    text = _decode(content)
    label = _source_label(source_label)
    timestamp = _utc(created_at)
    if media_type == "application/json":
        count, columns = _json_shape(text)
        source_kind = "manual-json"
    elif media_type == "text/csv":
        count, columns = _csv_shape(text)
        source_kind = "manual-csv"
    else:
        raise ManualImportError(
            "IMPORT-MEDIA-TYPE-DENIED", "manual input media type is not allowed"
        )

    stored = store.put_bytes(content, media_type=media_type)
    identity_subject = {
        "created_at": timestamp,
        "media_type": media_type,
        "record_hash": stored.record_hash,
        "source_label": label,
    }
    import_id = "IMP-" + canonical_sha256(identity_subject)[:24].upper()
    result: dict[str, Any] = {
        "schema_version": "0.1.0",
        "canonicalization_version": CANONICALIZATION_VERSION,
        "import_id": import_id,
        "created_at": timestamp,
        "source_kind": source_kind,
        "media_type": media_type,
        "source_label": label,
        "record_id": "REC-" + stored.record_hash[:24].upper(),
        "record_hash": stored.record_hash,
        "byte_length": stored.byte_length,
        "record_count": count,
        "columns": list(columns),
    }
    result["import_hash"] = canonical_sha256(result)
    return result
