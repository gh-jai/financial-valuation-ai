"""M8 source-snapshot and exact-reference M9-I3 manifest construction."""

from __future__ import annotations

import copy
import json
import re
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from .canonical import CANONICALIZATION_VERSION, canonical_sha256


ROOT = Path(__file__).resolve().parents[2]
SCHEMAS = ROOT / "schemas"
_REQUEST_ID = re.compile(r"^REQ-[A-Z0-9-]+$")
_RECORD_METADATA_FIELDS = frozenset(
    {"as_of", "period_start", "period_end", "currency", "unit_basis", "license_ref"}
)


class SnapshotError(ValueError):
    """Raised when the M9-I3 snapshot graph does not close."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def _plain(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(item) for item in value]
    return copy.deepcopy(value)


def _schema(name: str, value: Mapping[str, Any]) -> None:
    schema = json.loads((SCHEMAS / name).read_text(encoding="utf-8"))
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(value),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        raise SnapshotError("SNAPSHOT-SCHEMA-INVALID", f"{name} validation failed")


def _self_hash(value: Mapping[str, Any], field: str) -> None:
    subject = {key: item for key, item in value.items() if key != field}
    if value.get(field) != canonical_sha256(subject):
        raise SnapshotError(
            "SNAPSHOT-HASH-INVALID", f"{field} does not match its subject"
        )


def build_manual_snapshot(
    *,
    request_id: str,
    verified_identity: Mapping[str, Any],
    scope_decision: Mapping[str, Any],
    import_result: Mapping[str, Any],
    created_at: str,
    record_metadata: Mapping[str, Any],
    freshness: Mapping[str, Any],
    license_review: Mapping[str, Any],
    status: str,
    warnings: Sequence[Mapping[str, Any]] = (),
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Build one deterministic manual source snapshot and closure manifest."""

    if not isinstance(request_id, str) or not _REQUEST_ID.fullmatch(request_id):
        raise SnapshotError("SNAPSHOT-REQUEST-INVALID", "request_id is invalid")
    identity = _plain(verified_identity)
    decision = _plain(scope_decision)
    imported = _plain(import_result)
    _schema("verified-issuer-identity.schema.json", identity)
    _schema("issuer-structural-scope-decision.schema.json", decision)
    _schema("manual-import-result.schema.json", imported)
    _self_hash(identity, "verified_identity_hash")
    _self_hash(decision, "scope_decision_hash")
    _self_hash(imported, "import_hash")
    if created_at != imported["created_at"]:
        raise SnapshotError(
            "SNAPSHOT-TIME-MISMATCH",
            "snapshot creation time must match the manual import time",
        )
    expected_source_kind = {
        "application/json": "manual-json",
        "text/csv": "manual-csv",
    }.get(imported.get("media_type"))
    if imported.get("source_kind") != expected_source_kind:
        raise SnapshotError("SNAPSHOT-IMPORT-MISMATCH", "manual import kind and media type differ")
    if identity["identity_status"] != "verified":
        raise SnapshotError("SNAPSHOT-IDENTITY-DENIED", "issuer identity is not verified")
    if (
        decision["outcome"] != "eligible_for_data_review"
        or decision["eligible_for_m9_data_review"] is not True
    ):
        raise SnapshotError("SNAPSHOT-SCOPE-DENIED", "issuer is not eligible for M9 data review")
    if (
        decision["verified_identity_id"] != identity["verified_identity_id"]
        or decision["verified_identity_hash"] != identity["verified_identity_hash"]
    ):
        raise SnapshotError("SNAPSHOT-UPSTREAM-MISMATCH", "scope decision does not bind identity")
    metadata = _plain(record_metadata)
    if not isinstance(metadata, dict) or set(metadata) != _RECORD_METADATA_FIELDS:
        raise SnapshotError("SNAPSHOT-METADATA-INVALID", "record metadata fields are invalid")

    snapshot_subject = {
        "created_at": created_at,
        "import_hash": imported["import_hash"],
        "request_id": request_id,
        "scope_decision_hash": decision["scope_decision_hash"],
        "verified_identity_hash": identity["verified_identity_hash"],
    }
    snapshot_id = "SNP-" + canonical_sha256(snapshot_subject)[:24].upper()
    record = {
        "record_id": imported["record_id"],
        "provider": "manual-upload",
        "record_type": "manual-financials",
        "accession": None,
        "retrieved_at": created_at,
        "as_of": metadata["as_of"],
        "period_start": metadata["period_start"],
        "period_end": metadata["period_end"],
        "currency": metadata["currency"],
        "unit_basis": metadata["unit_basis"],
        "source_url": f"urn:fvi:manual-import:{imported['import_id'].lower()}",
        "content_hash": imported["record_hash"],
        "license_ref": metadata["license_ref"],
    }
    if not isinstance(warnings, Sequence) or isinstance(warnings, (str, bytes)):
        raise SnapshotError("SNAPSHOT-WARNINGS-INVALID", "warnings must be an array")
    warning_values = [_plain(item) for item in warnings]
    if any(not isinstance(item, dict) for item in warning_values):
        raise SnapshotError("SNAPSHOT-WARNINGS-INVALID", "warnings must contain objects")
    snapshot: dict[str, Any] = {
        "schema_version": "0.1.0",
        "snapshot_id": snapshot_id,
        "request_id": request_id,
        "created_at": created_at,
        "company_identity": {
            "cik": identity["cik"],
            "legal_name": identity["legal_name"],
            "ticker": identity["ticker"],
            "exchange": identity["exchange_code"],
            "identity_status": "verified",
        },
        "records": [record],
        "freshness": _plain(freshness),
        "license_review": _plain(license_review),
        "status": status,
        "warnings": sorted(
            warning_values,
            key=lambda item: (
                str(item.get("code", "")),
                str(item.get("severity", "")),
                str(item.get("message", "")),
            ),
        ),
    }
    snapshot["snapshot_hash"] = canonical_sha256(snapshot)
    _schema("source-snapshot.schema.json", snapshot)

    manifest_subject = {
        "created_at": created_at,
        "import_hash": imported["import_hash"],
        "request_id": request_id,
        "snapshot_hash": snapshot["snapshot_hash"],
        "verified_identity_hash": identity["verified_identity_hash"],
    }
    manifest: dict[str, Any] = {
        "schema_version": "0.1.0",
        "canonicalization_version": CANONICALIZATION_VERSION,
        "manifest_id": "MNF-" + canonical_sha256(manifest_subject)[:24].upper(),
        "created_at": created_at,
        "request_id": request_id,
        "verified_identity_id": identity["verified_identity_id"],
        "verified_identity_hash": identity["verified_identity_hash"],
        "scope_decision_id": decision["scope_decision_id"],
        "scope_decision_hash": decision["scope_decision_hash"],
        "import_id": imported["import_id"],
        "import_hash": imported["import_hash"],
        "snapshot_id": snapshot["snapshot_id"],
        "snapshot_hash": snapshot["snapshot_hash"],
        "record_hashes": [imported["record_hash"]],
        "store_layout": "sha256-sharded-v1",
        "network_state": "denied",
    }
    manifest["manifest_hash"] = canonical_sha256(manifest)
    _schema("m9-snapshot-manifest.schema.json", manifest)
    return snapshot, manifest
