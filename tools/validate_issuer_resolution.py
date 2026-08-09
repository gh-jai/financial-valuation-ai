"""Implementation-separated validator for the bounded M9-I2 artifact graph."""

from __future__ import annotations

import copy
import hashlib
import json
import unicodedata
from collections.abc import Mapping, Sequence
from datetime import datetime
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from tools.retail_data.independent import independent_sha256


ROOT = Path(__file__).resolve().parents[1]
SCHEMAS = {
    "candidate_set": "issuer-candidate-set.schema.json",
    "selection": "issuer-selection.schema.json",
    "verified_identity": "verified-issuer-identity.schema.json",
    "scope_decision": "issuer-structural-scope-decision.schema.json",
    "validation_result": "issuer-resolution-validation-result.schema.json",
    "identity_catalog": "issuer-identity-catalog.schema.json",
    "identity_policy": "identity-resolution-policy.schema.json",
    "scope_registry": "issuer-structural-scope-registry.schema.json",
    "company_request": "company-request.schema.json",
}
VALIDATOR_ID = "m9-i2-independent-validator"
VALIDATOR_VERSION = "0.1.0"


def _plain(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _plain(item) for key, item in value.items()}
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return [_plain(item) for item in value]
    return copy.deepcopy(value)


def _utc(text: str) -> datetime:
    if not isinstance(text, str) or not text.endswith("Z"):
        raise ValueError("timestamp is not canonical UTC")
    parsed = datetime.fromisoformat(text[:-1] + "+00:00")
    if parsed.isoformat().replace("+00:00", "Z") != text:
        raise ValueError("timestamp is not canonical UTC")
    return parsed


def _schema_errors(value: Mapping[str, Any], kind: str) -> list[str]:
    schema = json.loads((ROOT / "schemas" / SCHEMAS[kind]).read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return [
        f"{kind} schema violation at "
        f"{'.'.join(str(part) for part in error.path) or '<root>'}"
        for error in sorted(validator.iter_errors(dict(value)), key=lambda item: list(item.path))
    ]


def _without(value: Mapping[str, Any], field: str) -> dict[str, Any]:
    result = _plain(value)
    if field not in result:
        raise ValueError(f"missing hash field {field}")
    del result[field]
    return result


def _hash_matches(value: Mapping[str, Any], field: str) -> bool:
    try:
        return value[field] == independent_sha256(_without(value, field))
    except (KeyError, TypeError, ValueError):
        return False


def _normalized_name(text: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", text).strip().split()).casefold()


def _query(request: Mapping[str, Any]) -> tuple[str, str]:
    query = request["query"]
    if query["kind"] == "company_name":
        return "company_name", _normalized_name(query["company_name"])
    if query["kind"] == "ticker":
        return "ticker", query["ticker"]
    return "cik", query["cik"]


def _independent_matches(
    catalog: Mapping[str, Any], policy: Mapping[str, Any], request: Mapping[str, Any], at: datetime
) -> list[tuple[int, str, str, str, str, list[str]]]:
    kind, query = _query(request)
    rank = {item["match_kind"]: item["rank"] for item in policy["match_ranks"]}
    precedence = {item["match_kind"]: item["precedence"] for item in policy["match_ranks"]}
    result: list[tuple[int, str, str, str, str, list[str]]] = []
    ticker_ciks: set[str] = set()
    for record in catalog["records"]:
        current = []
        historical = []
        for listing in record["listing_history"]:
            start = _utc(listing["effective_from"])
            end = _utc(listing["effective_to"]) if listing["effective_to"] else None
            if start > at or (end is not None and end > at):
                raise ValueError("future listing evidence")
            (current if end is None else historical).append(listing)
        if len(current) != 1:
            raise ValueError("record does not have exactly one current listing")
        active = current[0]
        kinds: list[str] = []
        if kind == "cik" and record["cik"] == query:
            kinds.append("cik_exact")
        elif kind == "ticker":
            if active["ticker"] == query:
                kinds.append("ticker_current_exact")
            if any(item["ticker"] == query for item in historical):
                kinds.append("ticker_historical_exact")
            if kinds:
                ticker_ciks.add(record["cik"])
        elif kind == "company_name":
            if _normalized_name(record["legal_name"]) == query:
                kinds.append("legal_name_exact")
            if any(_normalized_name(item) == query for item in record["aliases"]):
                kinds.append("declared_alias_exact")
        if kinds:
            ordered = sorted(set(kinds), key=lambda item: precedence[item])
            result.append(
                (
                    rank[ordered[0]],
                    record["cik"],
                    active["exchange_code"],
                    active["ticker"],
                    record["legal_name"],
                    ordered,
                )
            )
    if kind == "ticker" and len(ticker_ciks) > 1:
        raise ValueError("ticker reuse")
    return sorted(result, key=lambda item: item[:5])


def _finding(message: str, ref: str) -> dict[str, Any]:
    return {
        "code": "IDENTITY-VALIDATION-FAILED",
        "message": message[:240],
        "severity": "blocking",
        "retryable": False,
        "artifact_refs": [ref],
        "next_action": "stop",
    }


def _envelope_active(value: Mapping[str, Any], at: datetime) -> bool:
    try:
        return (
            value["status"] == "approved"
            and _utc(value["effective_at"]) <= at < _utc(value["expires_at"])
            and value["reviewed_at"] is not None
            and _utc(value["reviewed_at"]) <= at
            and bool(value["reviewed_by"])
            and bool(value["review_evidence"])
        )
    except (KeyError, TypeError, ValueError):
        return False


def _subject(kind: str, identifier: str, digest: str) -> dict[str, str]:
    return {"artifact_kind": kind, "artifact_id": identifier, "artifact_hash": digest}


def validate_issuer_resolution(
    *,
    company_request: Mapping[str, Any],
    identity_catalog: Mapping[str, Any],
    identity_policy: Mapping[str, Any],
    candidate_set: Mapping[str, Any],
    validation_result_id: str,
    created_at: str,
    selection: Mapping[str, Any] | None = None,
    verified_identity: Mapping[str, Any] | None = None,
    scope_registry: Mapping[str, Any] | None = None,
    scope_decision: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Independently recompute one emitted path without production resolver imports."""

    request = _plain(company_request)
    catalog = _plain(identity_catalog)
    policy = _plain(identity_policy)
    candidates = _plain(candidate_set)
    optional = {
        "selection": _plain(selection) if selection is not None else None,
        "verified_identity": _plain(verified_identity) if verified_identity is not None else None,
        "scope_registry": _plain(scope_registry) if scope_registry is not None else None,
        "scope_decision": _plain(scope_decision) if scope_decision is not None else None,
    }
    findings: list[dict[str, Any]] = []

    for kind, value in (
        ("company_request", request),
        ("identity_catalog", catalog),
        ("identity_policy", policy),
        ("candidate_set", candidates),
    ):
        findings.extend(_finding(message, kind) for message in _schema_errors(value, kind))
    for kind, value in optional.items():
        if value is not None:
            findings.extend(_finding(message, kind) for message in _schema_errors(value, kind))

    hash_fields = {
        "identity_catalog": (catalog, "catalog_hash"),
        "identity_policy": (policy, "identity_policy_hash"),
        "candidate_set": (candidates, "candidate_set_hash"),
        "selection": (optional["selection"], "selection_hash"),
        "verified_identity": (optional["verified_identity"], "verified_identity_hash"),
        "scope_registry": (optional["scope_registry"], "scope_registry_hash"),
        "scope_decision": (optional["scope_decision"], "scope_decision_hash"),
    }
    for kind, (value, field) in hash_fields.items():
        if value is not None and not _hash_matches(value, field):
            findings.append(_finding(f"{field} does not match canonical content", kind))
    for evidence in catalog.get("evidence_records", []):
        if not _hash_matches(evidence, "evidence_record_hash"):
            findings.append(_finding("evidence record hash mismatch", "identity_catalog"))
    for record in catalog.get("records", []):
        if not _hash_matches(record, "catalog_record_hash"):
            findings.append(_finding("catalog record hash mismatch", "identity_catalog"))
        for listing in record.get("listing_history", []):
            if not _hash_matches(listing, "listing_entry_hash"):
                findings.append(_finding("listing entry hash mismatch", "identity_catalog"))
    for candidate in candidates.get("candidates", []):
        if not _hash_matches(candidate, "candidate_hash"):
            findings.append(_finding("candidate hash mismatch", "candidate_set"))

    if candidates.get("company_request_hash") != independent_sha256(request):
        findings.append(_finding("company-request hash does not close", "candidate_set"))
    refs = (
        ("catalog_hash", catalog.get("catalog_hash")),
        ("identity_policy_hash", policy.get("identity_policy_hash")),
    )
    for field, expected in refs:
        if candidates.get(field) != expected:
            findings.append(_finding(f"{field} reference does not close", "candidate_set"))

    try:
        at = _utc(candidates["resolution_at"])
        if candidates.get("created_at") != candidates.get("resolution_at"):
            findings.append(_finding("candidate-set timestamps do not match", "candidate_set"))
        if not _envelope_active(catalog, at):
            findings.append(_finding("identity catalog is denied at resolution", "identity_catalog"))
        if not _envelope_active(policy, at):
            findings.append(_finding("identity policy is denied at resolution", "identity_policy"))
        records = catalog["records"]
        evidence = catalog["evidence_records"]
        if records != sorted(
            records,
            key=lambda item: (item["cik"], item["record_id"], item["catalog_record_hash"]),
        ):
            findings.append(_finding("catalog record order is not canonical", "identity_catalog"))
        if evidence != sorted(
            evidence,
            key=lambda item: (item["cik"], item["source_record_id"], item["evidence_record_hash"]),
        ):
            findings.append(_finding("catalog evidence order is not canonical", "identity_catalog"))
        expected_ranks = sorted(
            policy["match_ranks"],
            key=lambda item: (item["rank"], item["precedence"], item["match_kind"]),
        )
        if policy["match_ranks"] != expected_ranks:
            findings.append(_finding("identity-policy rank order is not canonical", "identity_policy"))
        expected = _independent_matches(catalog, policy, request, at)
        actual = [
            (
                item["match_rank"], item["cik"], item["exchange_code"], item["ticker"],
                item["legal_name"], item["match_kinds"],
            )
            for item in candidates["candidates"]
        ]
        if candidates.get("status") not in {"blocked", "not_found"} and actual != expected:
            findings.append(_finding("independent candidate set differs", "candidate_set"))
        evidence_by_id = {item["source_record_id"]: item for item in evidence}
        record_by_hash = {item["catalog_record_hash"]: item for item in records}
        for candidate in candidates.get("candidates", []):
            record = record_by_hash.get(candidate.get("catalog_record_hash"))
            if record is None or record.get("cik") != candidate.get("cik"):
                findings.append(_finding("candidate does not close to one catalog record", "candidate_set"))
                continue
            current = [item for item in record["listing_history"] if item["effective_to"] is None]
            if len(current) != 1:
                findings.append(_finding("candidate catalog record lacks one current listing", "candidate_set"))
                continue
            listing = current[0]
            identity_key = {
                "catalog_id": catalog["catalog_id"],
                "catalog_version": catalog["catalog_version"],
                "record_id": record["record_id"],
                "catalog_record_hash": record["catalog_record_hash"],
            }
            expected_id = "ICD-" + independent_sha256(identity_key).upper()
            active_evidence = sorted(
                evidence_by_id[item]["evidence_record_hash"]
                for item in listing["evidence_record_refs"]
            )
            expected_fields = {
                "candidate_id": expected_id,
                "cik": record["cik"],
                "legal_name": record["legal_name"],
                "ticker": listing["ticker"],
                "exchange_code": listing["exchange_code"],
                "listing_status": "active",
                "listing_effective_from": listing["effective_from"],
                "listing_effective_to": listing["effective_to"],
                "active_listing_evidence_hashes": active_evidence,
                "primary_listing_country": record["primary_listing_country"],
                "primary_reporting_currency": record["primary_reporting_currency"],
                "issuer_class": record["issuer_class"],
                "regulated_capital_model_required": record["regulated_capital_model_required"],
                "reserve_real_option_required": record["reserve_real_option_required"],
                "public_company_status": record["public_company_status"],
                "identity_observed_at": record["identity_observed_at"],
                "source_record_refs": record["source_record_refs"],
            }
            if any(candidate.get(field) != value for field, value in expected_fields.items()):
                findings.append(_finding("candidate mutates catalog identity", "candidate_set"))
    except (KeyError, TypeError, ValueError):
        if candidates.get("status") != "blocked":
            findings.append(_finding("independent resolution stopped", "candidate_set"))

    selected = optional["selection"]
    identity = optional["verified_identity"]
    registry = optional["scope_registry"]
    decision = optional["scope_decision"]
    selectable = candidates.get("status") in {"unique_candidate", "selection_required"}
    if not selectable and any(item is not None for item in (selected, identity, decision)):
        findings.append(_finding("downstream artifact exists after blocking stop", "candidate_set"))
    if selected is not None:
        matching = [
            item for item in candidates.get("candidates", [])
            if item.get("candidate_id") == selected.get("selected_candidate_id")
            and item.get("candidate_hash") == selected.get("selected_candidate_hash")
        ]
        if (
            selected.get("actor_type") != "human"
            or selected.get("candidate_set_hash") != candidates.get("candidate_set_hash")
            or len(matching) != 1
        ):
            findings.append(_finding("human selection does not close", "selection"))
        expected_reason = (
            "confirmed_unique"
            if len(candidates.get("candidates", [])) == 1
            else "resolved_ambiguity"
        )
        try:
            selection_time_valid = (
                selected["created_at"] == selected["selected_at"]
                and _utc(selected["selected_at"]) >= _utc(candidates["created_at"])
            )
        except (KeyError, TypeError, ValueError):
            selection_time_valid = False
        if selected.get("selection_reason") != expected_reason or not selection_time_valid:
            findings.append(_finding("selection reason or timestamp chain is invalid", "selection"))
    if identity is not None:
        if selected is None:
            findings.append(_finding("verified identity lacks selection", "verified_identity"))
        else:
            candidate = next(
                (item for item in candidates.get("candidates", []) if item.get("candidate_hash") == selected.get("selected_candidate_hash")),
                None,
            )
            copied = (
                "cik", "legal_name", "ticker", "exchange_code", "listing_status",
                "listing_effective_from", "listing_effective_to", "active_listing_evidence_hashes",
                "primary_listing_country", "primary_reporting_currency", "issuer_class",
                "regulated_capital_model_required", "reserve_real_option_required",
                "public_company_status", "identity_observed_at", "catalog_record_hash",
                "source_record_refs",
            )
            if candidate is None or any(identity.get(field) != candidate.get(field) for field in copied):
                findings.append(_finding("verified identity mutates selected candidate", "verified_identity"))
            else:
                age = int((_utc(identity["verified_at"]) - _utc(identity["identity_observed_at"])).total_seconds())
                identity_times_valid = (
                    identity.get("created_at") == identity.get("verified_at")
                    == identity.get("freshness_evaluated_at")
                    and _utc(identity["verified_at"]) >= _utc(selected["selected_at"])
                )
                if (
                    identity.get("identity_age_seconds") != age
                    or age > policy["max_identity_age_seconds"]
                    or not identity_times_valid
                    or not _envelope_active(policy, _utc(identity["verified_at"]))
                ):
                    findings.append(_finding("verified identity freshness mismatch", "verified_identity"))
    if decision is not None:
        if identity is None or registry is None:
            findings.append(_finding("scope decision lacks identity or registry", "scope_decision"))
        else:
            try:
                decision_at = _utc(decision["evaluated_at"])
                decision_times_valid = (
                    decision["created_at"] == decision["evaluated_at"]
                    and decision_at >= _utc(identity["verified_at"])
                    and _envelope_active(registry, decision_at)
                    and _envelope_active(policy, decision_at)
                )
            except (KeyError, TypeError, ValueError):
                decision_times_valid = False
            try:
                matrix_path = ROOT / registry["m8_support_matrix_ref"]
                matrix_valid = (
                    hashlib.sha256(matrix_path.read_bytes()).hexdigest()
                    == registry["m8_support_matrix_sha256"]
                )
            except (KeyError, OSError, TypeError):
                matrix_valid = False
            supported = (
                identity.get("listing_status") == "active"
                and identity.get("primary_listing_country") == "US"
                and identity.get("primary_reporting_currency") == "USD"
                and identity.get("issuer_class") == "operating_non_financial"
                and identity.get("regulated_capital_model_required") is False
                and identity.get("reserve_real_option_required") is False
            )
            expected_outcome = "eligible_for_data_review" if supported else "unsupported"
            if (
                decision.get("verified_identity_hash") != identity.get("verified_identity_hash")
                or decision.get("scope_registry_hash") != registry.get("scope_registry_hash")
                or decision.get("outcome") != expected_outcome
                or decision.get("eligible_for_m9_data_review") is not supported
                or decision.get("lifecycle_route_status") != "not_evaluated"
                or not decision_times_valid
                or not matrix_valid
            ):
                findings.append(_finding("structural scope decision differs", "scope_decision"))

    deduped = {
        (item["message"], tuple(item["artifact_refs"])): item for item in findings
    }
    findings = sorted(
        deduped.values(),
        key=lambda item: (item["code"], item["message"], "|".join(item["artifact_refs"]), item["next_action"]),
    )
    subjects = [
        _subject("company_request", request["request_id"], independent_sha256(request)),
        _subject("identity_catalog", catalog["catalog_id"], catalog["catalog_hash"]),
        _subject("identity_policy", policy["identity_policy_id"], policy["identity_policy_hash"]),
        _subject("candidate_set", candidates["candidate_set_id"], candidates["candidate_set_hash"]),
    ]
    optional_subjects = (
        ("selection", selected, "selection_id", "selection_hash"),
        ("verified_identity", identity, "verified_identity_id", "verified_identity_hash"),
        ("scope_registry", registry, "scope_registry_id", "scope_registry_hash"),
        ("scope_decision", decision, "scope_decision_id", "scope_decision_hash"),
    )
    for kind, value, id_field, hash_field in optional_subjects:
        if value is not None:
            subjects.append(_subject(kind, value[id_field], value[hash_field]))
    subjects.sort(key=lambda item: (item["artifact_kind"], item["artifact_id"], item["artifact_hash"]))
    result = {
        "schema_version": "0.1.0",
        "canonicalization_version": "fvi-canonical-json-v1",
        "validation_result_id": validation_result_id,
        "created_at": created_at,
        "validator_id": VALIDATOR_ID,
        "validator_version": VALIDATOR_VERSION,
        "implementation_separation": "independent",
        "subjects": subjects,
        "findings": findings,
        "status": "failed" if findings else "passed",
    }
    result["validation_result_hash"] = independent_sha256(result)
    validation_errors = _schema_errors(result, "validation_result")
    if validation_errors:
        raise ValueError(validation_errors[0])
    return result
