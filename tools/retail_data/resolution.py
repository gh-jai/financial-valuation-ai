"""Deterministic, synthetic-only issuer resolution for the M9-I2 checkpoint."""

from __future__ import annotations

import copy
from collections.abc import Mapping, Sequence
from datetime import datetime
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from .canonical import CANONICALIZATION_VERSION, canonical_sha256
from .errors import ErrorSeverity, NextAction, RetailDataError
from .identity_contracts import (
    ROOT,
    IdentityContractError,
    attach_hash,
    normalize_company_name,
    parse_utc,
    require_artifact_hash,
    strict_load,
    validate_identity_catalog,
    validate_identity_policy,
    validate_schema,
)


RESOLVER_VERSION = "0.1.0"
FIXTURE_ROOT = ROOT / "benchmarks" / "fixtures" / "m9_i2"
_CATALOG_ALLOWLIST = {
    "m9-i2-synthetic-catalog": "synthetic-identity-catalog.yaml",
}

_MESSAGES = {
    "IDENTITY-NOT-FOUND": "No exact synthetic identity candidate was found.",
    "IDENTITY-AMBIGUOUS": "Multiple exact synthetic candidates require human selection.",
    "IDENTITY-SELECTION-REQUIRED": "A hash-bound human identity selection is required.",
    "IDENTITY-SELECTION-MISMATCH": "The human selection does not close to the candidate set.",
    "IDENTITY-TICKER-REUSED": "The ticker is reused across catalog identity history.",
    "IDENTITY-CIK-NAME-MISMATCH": "Catalog CIK and legal-name evidence do not agree.",
    "IDENTITY-CATALOG-CONFLICT": "The synthetic identity catalog contains conflicting records.",
    "IDENTITY-CATALOG-DENIED": "The synthetic identity catalog is unavailable or denied.",
    "IDENTITY-POLICY-DENIED": "The identity-resolution policy is unavailable or denied.",
    "IDENTITY-HASH-COLLISION": "A deterministic identity hash collision was detected.",
    "IDENTITY-STALE": "Identity evidence exceeds the approved freshness limit.",
    "IDENTITY-EVIDENCE-FUTURE": "Identity evidence post-dates the controlled evaluation time.",
    "IDENTITY-DELISTED": "The selected identity has no active listing at evaluation time.",
    "IDENTITY-HASH-MISMATCH": "An identity artifact hash or reference does not close.",
}

_NEXT_ACTION = {
    "IDENTITY-NOT-FOUND": NextAction.VERIFY_IDENTITY,
    "IDENTITY-AMBIGUOUS": NextAction.VERIFY_IDENTITY,
    "IDENTITY-SELECTION-REQUIRED": NextAction.VERIFY_IDENTITY,
    "IDENTITY-SELECTION-MISMATCH": NextAction.VERIFY_IDENTITY,
    "IDENTITY-TICKER-REUSED": NextAction.UPDATE_REGISTRY,
    "IDENTITY-CIK-NAME-MISMATCH": NextAction.UPDATE_REGISTRY,
    "IDENTITY-CATALOG-CONFLICT": NextAction.UPDATE_REGISTRY,
    "IDENTITY-CATALOG-DENIED": NextAction.UPDATE_REGISTRY,
    "IDENTITY-POLICY-DENIED": NextAction.UPDATE_REGISTRY,
    "IDENTITY-HASH-COLLISION": NextAction.STOP,
    "IDENTITY-STALE": NextAction.UPDATE_REGISTRY,
    "IDENTITY-EVIDENCE-FUTURE": NextAction.UPDATE_REGISTRY,
    "IDENTITY-DELISTED": NextAction.STOP,
    "IDENTITY-HASH-MISMATCH": NextAction.STOP,
}


class ResolutionStop(ValueError):
    """A fail-closed stop carrying only the stable M9-I1 safe-error shape."""

    def __init__(self, error: RetailDataError):
        super().__init__(error.code)
        self.error = error


def _plain(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _plain(item) for key, item in value.items()}
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return [_plain(item) for item in value]
    return copy.deepcopy(value)


def _error(code: str, *refs: str) -> RetailDataError:
    return RetailDataError(
        code=code,
        message=_MESSAGES[code],
        severity=ErrorSeverity.BLOCKING,
        retryable=False,
        artifact_refs=tuple(sorted(set(refs))),
        next_action=_NEXT_ACTION[code],
    )


def _catalog_error_code(error: IdentityContractError) -> str:
    message = str(error).lower()
    if "cik and legal-name" in message:
        return "IDENTITY-CIK-NAME-MISMATCH"
    if "future" in message:
        return "IDENTITY-EVIDENCE-FUTURE"
    if "hash" in message:
        return "IDENTITY-HASH-MISMATCH"
    if any(
        marker in message
        for marker in (
            "duplicate",
            "conflict",
            "interval",
            "listing",
            "source reference",
            "evidence reference",
            "identity_observed_at",
        )
    ):
        return "IDENTITY-CATALOG-CONFLICT"
    return "IDENTITY-CATALOG-DENIED"


def _candidate_set(
    *,
    request: Mapping[str, Any],
    request_hash: str,
    catalog: Mapping[str, Any],
    policy: Mapping[str, Any],
    candidate_set_id: str,
    at_text: str,
    query_kind: str,
    normalized_query: str,
    status: str,
    candidates: list[dict[str, Any]],
    errors: list[dict[str, Any]],
) -> dict[str, Any]:
    value = {
        "schema_version": "0.1.0",
        "candidate_set_id": candidate_set_id,
        "created_at": at_text,
        "resolution_at": at_text,
        "canonicalization_version": CANONICALIZATION_VERSION,
        "request_id": request["request_id"],
        "company_request_hash": request_hash,
        "resolver_version": RESOLVER_VERSION,
        "normalization_version": policy["normalization_version"],
        "catalog_id": catalog["catalog_id"],
        "catalog_version": catalog["catalog_version"],
        "catalog_hash": catalog["catalog_hash"],
        "identity_policy_id": policy["identity_policy_id"],
        "identity_policy_version": policy["identity_policy_version"],
        "identity_policy_hash": policy["identity_policy_hash"],
        "query_kind": query_kind,
        "normalized_query": normalized_query,
        "status": status,
        "candidates": candidates,
        "errors": errors,
    }
    result = attach_hash(value, "candidate_set_hash")
    validate_schema(result, "candidate_set")
    return result


def load_synthetic_catalog(catalog_id: str, at: datetime) -> Mapping[str, Any]:
    """Load one allowlisted fixture; callers can never provide a path or environment override."""

    if not isinstance(catalog_id, str) or catalog_id not in _CATALOG_ALLOWLIST:
        raise ResolutionStop(_error("IDENTITY-CATALOG-DENIED", f"catalog:{catalog_id}"))
    filename = _CATALOG_ALLOWLIST[catalog_id]
    candidate = FIXTURE_ROOT / filename
    try:
        root = FIXTURE_ROOT.resolve(strict=True)
        resolved = candidate.resolve(strict=True)
    except OSError as exc:
        raise ResolutionStop(_error("IDENTITY-CATALOG-DENIED", f"catalog:{catalog_id}")) from exc
    if resolved.parent != root or resolved.is_symlink() or resolved.suffix not in {".yaml", ".json"}:
        raise ResolutionStop(_error("IDENTITY-CATALOG-DENIED", f"catalog:{catalog_id}"))
    value = strict_load(resolved)
    try:
        validate_identity_catalog(value, at)
    except IdentityContractError as exc:
        raise ResolutionStop(_error("IDENTITY-CATALOG-DENIED", f"catalog:{catalog_id}")) from exc
    return value


def _validate_company_request(request: Mapping[str, Any]) -> None:
    schema = strict_load(ROOT / "schemas" / "company-request.schema.json")
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    if next(validator.iter_errors(dict(request)), None) is not None:
        raise ResolutionStop(_error("IDENTITY-NOT-FOUND", "request:invalid"))


def normalize_query(request: Mapping[str, Any]) -> tuple[str, str]:
    """Return only the locked exact-match query representation."""

    _validate_company_request(request)
    query = request["query"]
    kind = query["kind"]
    if kind == "ticker":
        return kind, query["ticker"]
    if kind == "cik":
        return kind, query["cik"]
    if kind == "company_name":
        return kind, normalize_company_name(query["company_name"])
    raise ResolutionStop(_error("IDENTITY-NOT-FOUND", "request:invalid"))


def _listing_state(
    record: Mapping[str, Any], evidence_by_id: Mapping[str, Mapping[str, Any]], at: datetime
) -> tuple[Mapping[str, Any], list[Mapping[str, Any]]]:
    current: list[Mapping[str, Any]] = []
    historical: list[Mapping[str, Any]] = []
    for listing in record["listing_history"]:
        start = parse_utc(listing["effective_from"], "effective_from")
        end = parse_utc(listing["effective_to"], "effective_to") if listing["effective_to"] else None
        refs = [evidence_by_id[item] for item in listing["evidence_record_refs"]]
        if start > at or (end is not None and end > at):
            raise ResolutionStop(_error("IDENTITY-EVIDENCE-FUTURE", record["record_id"]))
        if any(parse_utc(item["observed_at"], "observed_at") > at for item in refs):
            raise ResolutionStop(_error("IDENTITY-EVIDENCE-FUTURE", record["record_id"]))
        if end is None:
            active = [
                item
                for item in refs
                if item["assertion_kind"] == "active_as_of"
                and item["asserted_effective_from"] == listing["effective_from"]
                and item["asserted_effective_to"] is None
            ]
            if not active:
                raise ResolutionStop(_error("IDENTITY-CATALOG-CONFLICT", record["record_id"]))
            current.append(listing)
        elif end <= at:
            closed = [
                item
                for item in refs
                if item["assertion_kind"] == "closed_interval"
                and item["asserted_effective_from"] == listing["effective_from"]
                and item["asserted_effective_to"] == listing["effective_to"]
                and item["fact_as_of"] == listing["effective_to"]
            ]
            if not closed:
                raise ResolutionStop(_error("IDENTITY-CATALOG-CONFLICT", record["record_id"]))
            historical.append(listing)
    if record["public_company_status"] == "active" and len(current) != 1:
        raise ResolutionStop(_error("IDENTITY-DELISTED", record["record_id"]))
    if len(current) != 1:
        raise ResolutionStop(_error("IDENTITY-DELISTED", record["record_id"]))
    return current[0], historical


def _matched_kinds(
    record: Mapping[str, Any], current: Mapping[str, Any], historical: Sequence[Mapping[str, Any]],
    query_kind: str, normalized_query: str,
) -> tuple[list[str], list[Mapping[str, Any]]]:
    kinds: list[str] = []
    matched_listings: list[Mapping[str, Any]] = []
    if query_kind == "cik" and record["cik"] == normalized_query:
        kinds.append("cik_exact")
    elif query_kind == "ticker":
        if current["ticker"] == normalized_query:
            kinds.append("ticker_current_exact")
            matched_listings.append(current)
        for listing in historical:
            if listing["ticker"] == normalized_query:
                kinds.append("ticker_historical_exact")
                matched_listings.append(listing)
    elif query_kind == "company_name":
        if normalize_company_name(record["legal_name"]) == normalized_query:
            kinds.append("legal_name_exact")
        if any(normalize_company_name(alias) == normalized_query for alias in record["aliases"]):
            kinds.append("declared_alias_exact")
    return kinds, matched_listings


def _matched_listing_ref(
    listing: Mapping[str, Any], evidence_by_id: Mapping[str, Mapping[str, Any]], at: datetime
) -> dict[str, Any]:
    end = parse_utc(listing["effective_to"], "effective_to") if listing["effective_to"] else None
    classification = "current" if end is None else "historical"
    if parse_utc(listing["effective_from"], "effective_from") > at:
        classification = "future"
    return {
        "listing_entry_hash": listing["listing_entry_hash"],
        "ticker": listing["ticker"],
        "exchange_code": listing["exchange_code"],
        "derived_temporal_classification": classification,
        "effective_from": listing["effective_from"],
        "effective_to": listing["effective_to"],
        "evidence_record_hashes": sorted(
            evidence_by_id[item]["evidence_record_hash"]
            for item in listing["evidence_record_refs"]
        ),
    }


def _candidate(
    record: Mapping[str, Any], current: Mapping[str, Any], matched_kinds: list[str],
    matched_listings: list[Mapping[str, Any]], catalog: Mapping[str, Any],
    policy: Mapping[str, Any], evidence_by_id: Mapping[str, Mapping[str, Any]], at: datetime,
) -> dict[str, Any]:
    rank_by_kind = {item["match_kind"]: item for item in policy["match_ranks"]}
    precedence = {item["match_kind"]: item["precedence"] for item in policy["match_ranks"]}
    kinds = sorted(set(matched_kinds), key=lambda item: precedence[item])
    identity_key = {
        "catalog_id": catalog["catalog_id"],
        "catalog_version": catalog["catalog_version"],
        "record_id": record["record_id"],
        "catalog_record_hash": record["catalog_record_hash"],
    }
    candidate_id = "ICD-" + canonical_sha256(identity_key).upper()
    active_evidence = sorted(
        evidence_by_id[item]["evidence_record_hash"] for item in current["evidence_record_refs"]
    )
    refs = [
        _matched_listing_ref(item, evidence_by_id, at)
        for item in sorted(
            matched_listings,
            key=lambda item: (
                item["effective_from"],
                item["effective_to"] or "9999-12-31T23:59:59Z",
                item["ticker"],
                item["exchange_code"],
                item["listing_entry_hash"],
            ),
        )
    ]
    value = {
        "candidate_id": candidate_id,
        "primary_match_kind": kinds[0],
        "match_kinds": kinds,
        "match_rank": rank_by_kind[kinds[0]]["rank"],
        "cik": record["cik"],
        "legal_name": record["legal_name"],
        "ticker": current["ticker"],
        "exchange_code": current["exchange_code"],
        "listing_status": "active",
        "listing_effective_from": current["effective_from"],
        "listing_effective_to": current["effective_to"],
        "active_listing_evidence_hashes": active_evidence,
        "matched_listing_refs": refs,
        "primary_listing_country": record["primary_listing_country"],
        "primary_reporting_currency": record["primary_reporting_currency"],
        "issuer_class": record["issuer_class"],
        "regulated_capital_model_required": record["regulated_capital_model_required"],
        "reserve_real_option_required": record["reserve_real_option_required"],
        "public_company_status": record["public_company_status"],
        "identity_observed_at": record["identity_observed_at"],
        "source_record_refs": list(record["source_record_refs"]),
        "catalog_record_hash": record["catalog_record_hash"],
    }
    return attach_hash(value, "candidate_hash")


def resolve_issuer(
    request: Mapping[str, Any], catalog: Mapping[str, Any], policy: Mapping[str, Any], *,
    resolution_at: str, candidate_set_id: str,
) -> dict[str, Any]:
    """Resolve exact synthetic candidates without selecting or verifying any candidate."""

    at = parse_utc(resolution_at, "resolution_at")
    request_plain = _plain(request)
    catalog_plain = _plain(catalog)
    policy_plain = _plain(policy)
    query_kind, normalized_query = normalize_query(request_plain)
    try:
        validate_identity_catalog(catalog_plain, at)
    except IdentityContractError as exc:
        raise ResolutionStop(_error(_catalog_error_code(exc), "catalog:denied")) from exc
    try:
        validate_identity_policy(policy_plain, at)
    except IdentityContractError as exc:
        raise ResolutionStop(_error("IDENTITY-POLICY-DENIED", "policy:denied")) from exc
    if query_kind not in policy_plain["allowed_query_kinds"]:
        raise ResolutionStop(_error("IDENTITY-POLICY-DENIED", "policy:query-kind"))
    request_hash = canonical_sha256(request_plain)
    evidence_by_id = {
        item["source_record_id"]: item for item in catalog_plain["evidence_records"]
    }
    matches: list[dict[str, Any]] = []
    ticker_ciks: set[str] = set()
    for record in catalog_plain["records"]:
        current, historical = _listing_state(record, evidence_by_id, at)
        kinds, matched_listings = _matched_kinds(
            record, current, historical, query_kind, normalized_query
        )
        if kinds:
            if query_kind == "ticker":
                ticker_ciks.add(record["cik"])
            matches.append(
                _candidate(
                    record, current, kinds, matched_listings, catalog_plain, policy_plain,
                    evidence_by_id, at,
                )
            )
    if query_kind == "ticker" and len(ticker_ciks) > 1:
        error = _error("IDENTITY-TICKER-REUSED", f"request:{request_plain['request_id']}")
        return _candidate_set(
            request=request_plain, request_hash=request_hash, catalog=catalog_plain,
            policy=policy_plain, candidate_set_id=candidate_set_id, at_text=resolution_at,
            query_kind=query_kind, normalized_query=normalized_query, status="blocked",
            candidates=[], errors=[error.to_dict()],
        )
    matches.sort(
        key=lambda item: (
            item["match_rank"], item["cik"], item["exchange_code"], item["ticker"],
            item["legal_name"], item["candidate_id"],
        )
    )
    if not matches:
        status = "not_found"
        errors = [_error("IDENTITY-NOT-FOUND", f"request:{request_plain['request_id']}").to_dict()]
    elif len(matches) == 1:
        status = "unique_candidate"
        errors = []
    else:
        status = "selection_required"
        errors = [_error("IDENTITY-AMBIGUOUS", f"request:{request_plain['request_id']}").to_dict()]
    return _candidate_set(
        request=request_plain, request_hash=request_hash, catalog=catalog_plain,
        policy=policy_plain, candidate_set_id=candidate_set_id, at_text=resolution_at,
        query_kind=query_kind, normalized_query=normalized_query, status=status,
        candidates=matches, errors=errors,
    )


def create_selection(
    candidate_set: Mapping[str, Any], *, selection_id: str, selected_at: str,
    selected_candidate_id: str, actor_id: str, actor_type: str = "human",
) -> dict[str, Any]:
    value = _plain(candidate_set)
    validate_schema(value, "candidate_set")
    require_artifact_hash(value, "candidate_set_hash")
    if value["status"] not in {"unique_candidate", "selection_required"}:
        raise ResolutionStop(_error("IDENTITY-SELECTION-MISMATCH", value["candidate_set_id"]))
    if actor_type != "human":
        raise ResolutionStop(_error("IDENTITY-SELECTION-MISMATCH", value["candidate_set_id"]))
    selected = [item for item in value["candidates"] if item["candidate_id"] == selected_candidate_id]
    if len(selected) != 1:
        raise ResolutionStop(_error("IDENTITY-SELECTION-MISMATCH", value["candidate_set_id"]))
    if parse_utc(selected_at, "selected_at") < parse_utc(value["created_at"], "created_at"):
        raise ResolutionStop(_error("IDENTITY-SELECTION-MISMATCH", value["candidate_set_id"]))
    reason = "confirmed_unique" if len(value["candidates"]) == 1 else "resolved_ambiguity"
    selection = {
        "schema_version": "0.1.0",
        "canonicalization_version": CANONICALIZATION_VERSION,
        "selection_id": selection_id,
        "created_at": selected_at,
        "selected_at": selected_at,
        "candidate_set_id": value["candidate_set_id"],
        "candidate_set_hash": value["candidate_set_hash"],
        "selected_candidate_id": selected[0]["candidate_id"],
        "selected_candidate_hash": selected[0]["candidate_hash"],
        "actor_type": "human",
        "actor_id": actor_id,
        "selection_reason": reason,
    }
    result = attach_hash(selection, "selection_hash")
    validate_schema(result, "selection")
    return result


def verify_selected_identity(
    candidate_set: Mapping[str, Any], selection: Mapping[str, Any], policy: Mapping[str, Any], *,
    verified_identity_id: str, verified_at: str,
) -> dict[str, Any]:
    candidates = _plain(candidate_set)
    selected = _plain(selection)
    policy_plain = _plain(policy)
    validate_schema(candidates, "candidate_set")
    validate_schema(selected, "selection")
    require_artifact_hash(candidates, "candidate_set_hash")
    require_artifact_hash(selected, "selection_hash")
    for candidate in candidates["candidates"]:
        require_artifact_hash(candidate, "candidate_hash")
    if selected["candidate_set_hash"] != candidates["candidate_set_hash"]:
        raise ResolutionStop(_error("IDENTITY-SELECTION-MISMATCH", selected["selection_id"]))
    matches = [
        item for item in candidates["candidates"]
        if item["candidate_id"] == selected["selected_candidate_id"]
        and item["candidate_hash"] == selected["selected_candidate_hash"]
    ]
    if len(matches) != 1:
        raise ResolutionStop(_error("IDENTITY-SELECTION-MISMATCH", selected["selection_id"]))
    candidate = matches[0]
    expected_reason = (
        "confirmed_unique" if len(candidates["candidates"]) == 1 else "resolved_ambiguity"
    )
    if selected["selection_reason"] != expected_reason:
        raise ResolutionStop(_error("IDENTITY-SELECTION-MISMATCH", selected["selection_id"]))
    at = parse_utc(verified_at, "verified_at")
    if at < parse_utc(selected["selected_at"], "selected_at"):
        raise ResolutionStop(_error("IDENTITY-SELECTION-MISMATCH", selected["selection_id"]))
    try:
        validate_identity_policy(policy_plain, at)
    except IdentityContractError as exc:
        raise ResolutionStop(_error("IDENTITY-POLICY-DENIED", "policy:denied")) from exc
    observed = parse_utc(candidate["identity_observed_at"], "identity_observed_at")
    age = int((at - observed).total_seconds())
    if age < 0:
        raise ResolutionStop(_error("IDENTITY-EVIDENCE-FUTURE", candidate["candidate_id"]))
    if age > policy_plain["max_identity_age_seconds"]:
        raise ResolutionStop(_error("IDENTITY-STALE", candidate["candidate_id"]))
    if (
        candidate["listing_status"] != "active"
        or candidate["listing_effective_to"] is not None
        or candidate["public_company_status"] != "active"
    ):
        raise ResolutionStop(_error("IDENTITY-DELISTED", candidate["candidate_id"]))
    identity = {
        "schema_version": "0.1.0",
        "canonicalization_version": CANONICALIZATION_VERSION,
        "verified_identity_id": verified_identity_id,
        "created_at": verified_at,
        "verified_at": verified_at,
        "selection_id": selected["selection_id"],
        "selection_hash": selected["selection_hash"],
        "candidate_set_hash": candidates["candidate_set_hash"],
        "selected_candidate_hash": candidate["candidate_hash"],
        "cik": candidate["cik"],
        "legal_name": candidate["legal_name"],
        "ticker": candidate["ticker"],
        "exchange_code": candidate["exchange_code"],
        "listing_status": "active",
        "listing_effective_from": candidate["listing_effective_from"],
        "listing_effective_to": candidate["listing_effective_to"],
        "active_listing_evidence_hashes": candidate["active_listing_evidence_hashes"],
        "primary_listing_country": candidate["primary_listing_country"],
        "primary_reporting_currency": candidate["primary_reporting_currency"],
        "issuer_class": candidate["issuer_class"],
        "regulated_capital_model_required": candidate["regulated_capital_model_required"],
        "reserve_real_option_required": candidate["reserve_real_option_required"],
        "public_company_status": candidate["public_company_status"],
        "identity_observed_at": candidate["identity_observed_at"],
        "identity_age_seconds": age,
        "freshness_evaluated_at": verified_at,
        "freshness_policy_ref": policy_plain["identity_policy_hash"],
        "catalog_record_hash": candidate["catalog_record_hash"],
        "source_record_refs": candidate["source_record_refs"],
        "identity_status": "verified",
    }
    result = attach_hash(identity, "verified_identity_hash")
    validate_schema(result, "verified_identity")
    return result
