"""Implementation-separated validation for the M9-I3 storage and snapshot graph."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
import stat
from collections.abc import Mapping, Sequence
from io import StringIO
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = ROOT / "schemas"
MAX_RECORD_BYTES = 1_048_576
MAX_RECORDS = 2_000
MAX_CSV_COLUMNS = 128
MAX_CELL_CHARACTERS = 16_384
CANONICALIZATION_VERSION = "fvi-canonical-json-v1"
_HASH = re.compile(r"^[a-f0-9]{64}$")
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


class _DuplicateKey(ValueError):
    pass


def _normalize(value: Any, ancestors: frozenset[int] = frozenset()) -> Any:
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite number")
        return value
    if isinstance(value, Mapping):
        identity = id(value)
        if identity in ancestors:
            raise ValueError("cyclic value")
        next_ancestors = ancestors | {identity}
        result: dict[str, Any] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueError("non-string key")
            result[key] = _normalize(item, next_ancestors)
        return result
    if isinstance(value, list):
        identity = id(value)
        if identity in ancestors:
            raise ValueError("cyclic value")
        next_ancestors = ancestors | {identity}
        return [_normalize(item, next_ancestors) for item in value]
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
    return {key: item for key, item in value.items() if key != field}


def _schema_errors(name: str, value: Any) -> list[str]:
    try:
        schema = json.loads((SCHEMAS / name).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return ["validator schema is unavailable"]
    return [
        error.message
        for error in sorted(
            Draft202012Validator(
                schema, format_checker=FormatChecker()
            ).iter_errors(value),
            key=lambda item: list(item.absolute_path),
        )
    ]


def _pairs(pairs: Sequence[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateKey
        result[key] = value
    return result


def _constant(_: str) -> None:
    raise ValueError("non-finite number")


def _integer(value: str) -> int:
    if len(value) > _MAX_NUMBER_CHARACTERS:
        raise ValueError("integer too large")
    return int(value)


def _floating(value: str) -> float:
    if len(value) > _MAX_NUMBER_CHARACTERS:
        raise ValueError("float too large")
    parsed = float(value)
    if not math.isfinite(parsed):
        raise ValueError("non-finite number")
    return parsed


def _formula(value: str) -> bool:
    candidate = value.lstrip()
    if not candidate:
        return False
    if candidate[0] in "=+@":
        return True
    return candidate.startswith("-") and _DECIMAL.fullmatch(candidate) is None


def _parse_raw(content: bytes, media_type: Any) -> tuple[int, list[str]]:
    if not content or len(content) > MAX_RECORD_BYTES or content.startswith(b"\xef\xbb\xbf"):
        raise ValueError("raw record violates size or encoding limits")
    if any(content.startswith(signature) for signature in _ARCHIVE_SIGNATURES):
        raise ValueError("raw record has a denied archive or executable signature")
    if b"\x00" in content:
        raise ValueError("raw record contains NUL")
    text = content.decode("utf-8", errors="strict")
    if media_type == "application/json":
        value = json.loads(
            text,
            object_pairs_hook=_pairs,
            parse_constant=_constant,
            parse_int=_integer,
            parse_float=_floating,
        )
        records = value if isinstance(value, list) else [value]
        if (
            not records
            or len(records) > MAX_RECORDS
            or any(not isinstance(item, dict) for item in records)
        ):
            raise ValueError("JSON shape is outside the locked contract")
        return len(records), []
    if media_type != "text/csv":
        raise ValueError("media type is outside the locked contract")
    previous_limit = csv.field_size_limit()
    csv.field_size_limit(MAX_CELL_CHARACTERS)
    try:
        reader = csv.reader(StringIO(text, newline=""), strict=True)
        header = next(reader)
        if (
            not header
            or len(header) > MAX_CSV_COLUMNS
            or any(not item or item != item.strip() for item in header)
            or len(set(header)) != len(header)
            or any(len(item) > MAX_CELL_CHARACTERS or _formula(item) for item in header)
        ):
            raise ValueError("CSV header is outside the locked contract")
        count = 0
        for row in reader:
            count += 1
            if (
                count > MAX_RECORDS
                or len(row) != len(header)
                or any(len(item) > MAX_CELL_CHARACTERS or _formula(item) for item in row)
            ):
                raise ValueError("CSV row is outside the locked contract")
        if not count:
            raise ValueError("CSV requires a data row")
        return count, header
    finally:
        csv.field_size_limit(previous_limit)


def _subject_hash(value: Any, field: str | None = None) -> str:
    try:
        if field is not None and isinstance(value, Mapping):
            return _sha(_without(value, field))
        return _sha(value)
    except (TypeError, ValueError):
        return "0" * 64


def validate_m9_i3_storage(
    *,
    store_root: Path,
    verified_identity: Mapping[str, Any],
    scope_decision: Mapping[str, Any],
    import_result: Mapping[str, Any],
    source_snapshot: Mapping[str, Any],
    snapshot_manifest: Mapping[str, Any],
    validation_result_id: str,
    created_at: str,
) -> dict[str, Any]:
    """Independently close schemas, hashes, references, raw bytes, and generated IDs."""

    findings: list[dict[str, str]] = []

    def finding(code: str, message: str, subject: str) -> None:
        item = {"code": code, "message": message, "subject": subject}
        if item not in findings:
            findings.append(item)

    graph = (
        ("verified-issuer-identity.schema.json", verified_identity, "identity"),
        ("issuer-structural-scope-decision.schema.json", scope_decision, "scope"),
        ("manual-import-result.schema.json", import_result, "import"),
        ("source-snapshot.schema.json", source_snapshot, "snapshot"),
        ("m9-snapshot-manifest.schema.json", snapshot_manifest, "manifest"),
    )
    for schema_name, value, label in graph:
        if _schema_errors(schema_name, value):
            finding("M9I3-SCHEMA-INVALID", f"{label} schema validation failed", label)

    hashed = (
        (verified_identity, "verified_identity_hash", "identity"),
        (scope_decision, "scope_decision_hash", "scope"),
        (import_result, "import_hash", "import"),
        (source_snapshot, "snapshot_hash", "snapshot"),
        (snapshot_manifest, "manifest_hash", "manifest"),
    )
    for value, field, label in hashed:
        try:
            expected = _sha(_without(value, field))
            if value.get(field) != expected:
                finding("M9I3-HASH-MISMATCH", f"{label} self-hash does not match", label)
        except (TypeError, ValueError):
            finding("M9I3-HASH-MISMATCH", f"{label} cannot be independently hashed", label)

    content = b""
    record_hash = import_result.get("record_hash")
    if not isinstance(store_root, Path) or not store_root.is_absolute():
        finding("M9I3-STORE-ROOT-INVALID", "configured store root is invalid", "raw_record")
    elif not isinstance(record_hash, str) or not _HASH.fullmatch(record_hash):
        finding("M9I3-RECORD-HASH-INVALID", "raw record hash is invalid", "raw_record")
    else:
        components = [store_root, store_root / "records", store_root / "records/sha256"]
        record_path = components[-1] / record_hash[:2] / record_hash
        components.append(record_path.parent)
        try:
            for component in components:
                metadata = component.lstat()
                if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
                    raise ValueError("unsafe store component")
            metadata = record_path.lstat()
            if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode):
                raise ValueError("unsafe raw record")
            if metadata.st_size < 1 or metadata.st_size > MAX_RECORD_BYTES:
                raise ValueError("raw record size is outside the locked contract")
            content = record_path.read_bytes()
            if hashlib.sha256(content).hexdigest() != record_hash:
                raise ValueError("raw record digest mismatch")
        except (OSError, ValueError):
            finding("M9I3-STORE-TAMPER", "raw record path or content is invalid", "raw_record")

    if content:
        try:
            count, columns = _parse_raw(content, import_result.get("media_type"))
            if import_result.get("byte_length") != len(content):
                finding(
                    "M9I3-IMPORT-METADATA",
                    "raw byte count does not match import",
                    "import",
                )
            if (
                import_result.get("record_count") != count
                or import_result.get("columns") != columns
            ):
                finding(
                    "M9I3-IMPORT-METADATA",
                    "parsed shape does not match import",
                    "import",
                )
            expected_record_id = "REC-" + hashlib.sha256(content).hexdigest()[:24].upper()
            if import_result.get("record_id") != expected_record_id:
                finding(
                    "M9I3-IMPORT-ID",
                    "record identifier is not derived from raw bytes",
                    "import",
                )
            import_subject = {
                "created_at": import_result.get("created_at"),
                "media_type": import_result.get("media_type"),
                "record_hash": record_hash,
                "source_label": import_result.get("source_label"),
            }
            expected_import_id = "IMP-" + _sha(import_subject)[:24].upper()
            if import_result.get("import_id") != expected_import_id:
                finding(
                    "M9I3-IMPORT-ID", "import identifier is not deterministic", "import"
                )
            expected_kind = {
                "application/json": "manual-json",
                "text/csv": "manual-csv",
            }.get(import_result.get("media_type"))
            if import_result.get("source_kind") != expected_kind:
                finding(
                    "M9I3-IMPORT-METADATA",
                    "import kind and media type differ",
                    "import",
                )
        except (
            csv.Error,
            json.JSONDecodeError,
            UnicodeError,
            ValueError,
            StopIteration,
            _DuplicateKey,
        ):
            finding(
                "M9I3-RAW-INVALID",
                "raw record violates the manual-input contract",
                "raw_record",
            )

    try:
        if verified_identity.get("identity_status") != "verified":
            raise ValueError
        if (
            scope_decision.get("outcome") != "eligible_for_data_review"
            or scope_decision.get("eligible_for_m9_data_review") is not True
            or scope_decision.get("verified_identity_id")
            != verified_identity.get("verified_identity_id")
            or scope_decision.get("verified_identity_hash")
            != verified_identity.get("verified_identity_hash")
        ):
            raise ValueError
    except (AttributeError, ValueError):
        finding(
            "M9I3-UPSTREAM-DENIED",
            "identity and scope authority do not close",
            "scope",
        )

    try:
        expected_identity = {
            "cik": verified_identity["cik"],
            "legal_name": verified_identity["legal_name"],
            "ticker": verified_identity["ticker"],
            "exchange": verified_identity["exchange_code"],
            "identity_status": "verified",
        }
        if source_snapshot.get("company_identity") != expected_identity:
            finding(
                "M9I3-SNAPSHOT-IDENTITY",
                "snapshot identity is not an exact upstream copy",
                "snapshot",
            )
        snapshot_subject = {
            "created_at": source_snapshot.get("created_at"),
            "import_hash": import_result.get("import_hash"),
            "request_id": source_snapshot.get("request_id"),
            "scope_decision_hash": scope_decision.get("scope_decision_hash"),
            "verified_identity_hash": verified_identity.get("verified_identity_hash"),
        }
        expected_snapshot_id = "SNP-" + _sha(snapshot_subject)[:24].upper()
        if source_snapshot.get("snapshot_id") != expected_snapshot_id:
            finding("M9I3-SNAPSHOT-ID", "snapshot identifier is not deterministic", "snapshot")
        records = source_snapshot.get("records")
        if not isinstance(records, list) or len(records) != 1:
            raise ValueError
        record = records[0]
        if (
            record.get("record_id") != import_result.get("record_id")
            or record.get("content_hash") != record_hash
            or record.get("provider") != "manual-upload"
            or record.get("record_type") != "manual-financials"
            or record.get("retrieved_at") != source_snapshot.get("created_at")
            or record.get("source_url")
            != f"urn:fvi:manual-import:{str(import_result.get('import_id')).lower()}"
        ):
            finding("M9I3-SNAPSHOT-RECORD", "snapshot record does not close to import", "snapshot")
    except (KeyError, TypeError, ValueError):
        finding("M9I3-SNAPSHOT-RECORD", "snapshot record graph is invalid", "snapshot")

    try:
        manifest_subject = {
            "created_at": snapshot_manifest.get("created_at"),
            "import_hash": import_result.get("import_hash"),
            "request_id": source_snapshot.get("request_id"),
            "snapshot_hash": source_snapshot.get("snapshot_hash"),
            "verified_identity_hash": verified_identity.get("verified_identity_hash"),
        }
        expected_manifest_id = "MNF-" + _sha(manifest_subject)[:24].upper()
        expected_manifest = {
            "manifest_id": expected_manifest_id,
            "created_at": source_snapshot.get("created_at"),
            "request_id": source_snapshot.get("request_id"),
            "verified_identity_id": verified_identity.get("verified_identity_id"),
            "verified_identity_hash": verified_identity.get("verified_identity_hash"),
            "scope_decision_id": scope_decision.get("scope_decision_id"),
            "scope_decision_hash": scope_decision.get("scope_decision_hash"),
            "import_id": import_result.get("import_id"),
            "import_hash": import_result.get("import_hash"),
            "snapshot_id": source_snapshot.get("snapshot_id"),
            "snapshot_hash": source_snapshot.get("snapshot_hash"),
            "record_hashes": [record_hash],
            "store_layout": "sha256-sharded-v1",
            "network_state": "denied",
        }
        if any(snapshot_manifest.get(key) != value for key, value in expected_manifest.items()):
            finding("M9I3-MANIFEST-CLOSURE", "manifest references do not close", "manifest")
        if import_result.get("created_at") != source_snapshot.get("created_at"):
            finding("M9I3-TIME-CLOSURE", "import and snapshot times do not close", "manifest")
    except (AttributeError, TypeError, ValueError):
        finding("M9I3-MANIFEST-CLOSURE", "manifest references do not close", "manifest")

    subjects = [
        {
            "kind": "verified_identity",
            "identifier": str(verified_identity.get("verified_identity_id", "identity"))[:128],
            "hash": _subject_hash(verified_identity, "verified_identity_hash"),
        },
        {
            "kind": "scope_decision",
            "identifier": str(scope_decision.get("scope_decision_id", "scope"))[:128],
            "hash": _subject_hash(scope_decision, "scope_decision_hash"),
        },
        {
            "kind": "manual_import",
            "identifier": str(import_result.get("import_id", "import"))[:128],
            "hash": _subject_hash(import_result, "import_hash"),
        },
        {
            "kind": "raw_record",
            "identifier": str(import_result.get("record_id", "raw-record"))[:128],
            "hash": hashlib.sha256(content).hexdigest() if content else "0" * 64,
        },
        {
            "kind": "source_snapshot",
            "identifier": str(source_snapshot.get("snapshot_id", "snapshot"))[:128],
            "hash": _subject_hash(source_snapshot, "snapshot_hash"),
        },
        {
            "kind": "snapshot_manifest",
            "identifier": str(snapshot_manifest.get("manifest_id", "manifest"))[:128],
            "hash": _subject_hash(snapshot_manifest, "manifest_hash"),
        },
    ]
    result: dict[str, Any] = {
        "schema_version": "0.1.0",
        "canonicalization_version": CANONICALIZATION_VERSION,
        "validation_result_id": validation_result_id,
        "created_at": created_at,
        "implementation_separation": "independent",
        "subjects": subjects,
        "status": "failed" if findings else "passed",
        "findings": sorted(
            findings,
            key=lambda item: (item["code"], item["subject"], item["message"]),
        ),
    }
    result["validation_result_hash"] = _sha(result)
    result_errors = _schema_errors("m9-storage-validation-result.schema.json", result)
    if result_errors:
        raise ValueError("independent validation result is not schema-valid")
    return result
