"""Strict, offline contracts for the bounded M9-I2 identity checkpoint."""

from __future__ import annotations

import copy
import json
import re
from collections.abc import Mapping, Sequence
from datetime import datetime
from pathlib import Path
from types import MappingProxyType
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker

from .canonical import CANONICALIZATION_VERSION, canonical_sha256


ROOT = Path(__file__).resolve().parents[2]
SCHEMA_DIR = ROOT / "schemas"
SCHEMA_VERSION = "0.1.0"

SCHEMA_FILES = {
    "identity_catalog": "issuer-identity-catalog.schema.json",
    "identity_policy": "identity-resolution-policy.schema.json",
    "scope_registry": "issuer-structural-scope-registry.schema.json",
    "candidate_set": "issuer-candidate-set.schema.json",
    "selection": "issuer-selection.schema.json",
    "verified_identity": "verified-issuer-identity.schema.json",
    "scope_decision": "issuer-structural-scope-decision.schema.json",
    "validation_result": "issuer-resolution-validation-result.schema.json",
}

HASH_FIELDS = {
    "identity_catalog": "catalog_hash",
    "identity_policy": "identity_policy_hash",
    "scope_registry": "scope_registry_hash",
    "candidate_set": "candidate_set_hash",
    "selection": "selection_hash",
    "verified_identity": "verified_identity_hash",
    "scope_decision": "scope_decision_hash",
    "validation_result": "validation_result_hash",
}

_KEBAB = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")

_LOCKED_MATCH_RANKS = (
    ("cik_exact", 0, 0),
    ("ticker_current_exact", 0, 1),
    ("legal_name_exact", 0, 2),
    ("ticker_historical_exact", 10, 3),
    ("declared_alias_exact", 10, 4),
)

_LOCKED_SCOPE_RULES = (
    ("unsupported-financial", 10, (("regulated_capital_model_required", "equals", True),), "unsupported", "SCOPE-UNSUPPORTED-FINANCIAL"),
    ("unsupported-reit", 20, (("issuer_class", "equals", "reit"),), "unsupported", "SCOPE-UNSUPPORTED-REIT"),
    ("unsupported-fund", 30, (("issuer_class", "equals", "fund"),), "unsupported", "SCOPE-UNSUPPORTED-FUND"),
    ("unsupported-etf", 31, (("issuer_class", "equals", "etf"),), "unsupported", "SCOPE-UNSUPPORTED-FUND"),
    ("unsupported-investment-company", 32, (("issuer_class", "equals", "investment_company"),), "unsupported", "SCOPE-UNSUPPORTED-FUND"),
    ("unsupported-non-operating-vehicle", 33, (("issuer_class", "equals", "non_operating_holding_vehicle"),), "unsupported", "SCOPE-UNSUPPORTED-FUND"),
    ("unsupported-spac", 40, (("issuer_class", "equals", "spac_blank_check"),), "unsupported", "SCOPE-UNSUPPORTED-SPAC"),
    ("unsupported-natural-resource", 50, (("reserve_real_option_required", "equals", True),), "unsupported", "SCOPE-UNSUPPORTED-NATURAL-RESOURCE"),
    ("unsupported-non-us", 60, (("primary_listing_country", "not_equals", "US"),), "unsupported", "SCOPE-UNSUPPORTED-NON-US"),
    ("unsupported-private", 61, (("public_company_status", "equals", "private"),), "unsupported", "SCOPE-UNSUPPORTED-PRIVATE"),
    ("unsupported-non-usd", 70, (("primary_reporting_currency", "not_equals", "USD"),), "unsupported", "SCOPE-UNSUPPORTED-NON-USD"),
    (
        "in-scope-pending-review",
        100,
        (
            ("public_company_status", "equals", "active"),
            ("primary_listing_country", "equals", "US"),
            ("primary_reporting_currency", "equals", "USD"),
            ("issuer_class", "equals", "operating_non_financial"),
            ("regulated_capital_model_required", "equals", False),
            ("reserve_real_option_required", "equals", False),
        ),
        "eligible_for_data_review",
        "SCOPE-IN-SCOPE-PENDING-REVIEW",
    ),
)

_LOCKED_DEFERRED_ROWS = (
    "M8-LIFECYCLE-CYCLICAL",
    "M8-LIFECYCLE-DECLINING",
    "M8-LIFECYCLE-DISTRESSED",
    "M8-LIFECYCLE-GROWTH",
    "M8-LIFECYCLE-MATURE",
    "M8-LIFECYCLE-YOUNG",
)


class IdentityContractError(ValueError):
    """Raised when an M9-I2 artifact fails its strict, default-deny contract."""


class _UniqueKeyLoader(yaml.SafeLoader):
    pass


def _construct_mapping(
    loader: _UniqueKeyLoader, node: yaml.MappingNode, deep: bool = False
) -> dict[Any, Any]:
    result: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in result:
            raise IdentityContractError(f"duplicate mapping key: {key!r}")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


_UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_mapping
)


def strict_load(path: Path) -> dict[str, Any]:
    """Load one JSON/YAML object while rejecting duplicate keys before validation."""

    if not isinstance(path, Path):
        raise TypeError("artifact path must be a pathlib.Path")
    try:
        text = path.read_text(encoding="utf-8")
        if path.suffix == ".json":
            value = json.loads(
                text,
                object_pairs_hook=lambda pairs: _unique_json_object(pairs),
                parse_constant=lambda token: _reject_constant(token),
            )
        else:
            value = yaml.load(text, Loader=_UniqueKeyLoader)
    except (OSError, UnicodeError, json.JSONDecodeError, yaml.YAMLError) as exc:
        raise IdentityContractError(f"cannot load strict artifact {path.name}") from exc
    if not isinstance(value, dict) or any(not isinstance(key, str) for key in value):
        raise IdentityContractError("artifact root must be an object with string keys")
    return value


def _unique_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise IdentityContractError(f"duplicate mapping key: {key!r}")
        result[key] = value
    return result


def _reject_constant(token: str) -> None:
    raise IdentityContractError(f"non-finite JSON number: {token}")


def _schema(kind: str) -> dict[str, Any]:
    try:
        filename = SCHEMA_FILES[kind]
    except KeyError as exc:
        raise IdentityContractError(f"unknown M9-I2 artifact kind: {kind}") from exc
    return strict_load(SCHEMA_DIR / filename)


def validate_schema(value: Mapping[str, Any], kind: str) -> None:
    """Validate one in-memory artifact against its named strict Draft 2020-12 schema."""

    validator = Draft202012Validator(_schema(kind), format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(dict(value)), key=lambda item: list(item.path))
    if errors:
        first = errors[0]
        location = ".".join(str(part) for part in first.path) or "<root>"
        raise IdentityContractError(f"{kind} [{location}]: {first.message}")


def hash_subject(value: Mapping[str, Any], hash_field: str) -> dict[str, Any]:
    subject = copy.deepcopy(dict(value))
    if hash_field not in subject:
        raise IdentityContractError(f"missing hash field: {hash_field}")
    del subject[hash_field]
    return subject


def artifact_hash(value: Mapping[str, Any], hash_field: str) -> str:
    return canonical_sha256(hash_subject(value, hash_field))


def attach_hash(value: Mapping[str, Any], hash_field: str) -> dict[str, Any]:
    result = copy.deepcopy(dict(value))
    result[hash_field] = canonical_sha256(result)
    return result


def require_artifact_hash(value: Mapping[str, Any], hash_field: str) -> None:
    if value.get(hash_field) != artifact_hash(value, hash_field):
        raise IdentityContractError(f"{hash_field} does not match canonical content")


def parse_utc(value: str, label: str) -> datetime:
    if not isinstance(value, str) or not value.endswith("Z"):
        raise IdentityContractError(f"{label} must be RFC 3339 UTC ending in Z")
    try:
        parsed = datetime.fromisoformat(value[:-1] + "+00:00")
    except ValueError as exc:
        raise IdentityContractError(f"{label} must be RFC 3339 UTC ending in Z") from exc
    if parsed.isoformat().replace("+00:00", "Z") != value:
        raise IdentityContractError(f"{label} must use canonical RFC 3339 UTC")
    return parsed


def _require_sorted_unique(values: Sequence[Any], key: Any, label: str) -> None:
    if len(values) != len({repr(item) for item in values}):
        raise IdentityContractError(f"{label} must be unique")
    if list(values) != sorted(values, key=key):
        raise IdentityContractError(f"{label} is not in canonical order")


def _validate_envelope(value: Mapping[str, Any], hash_field: str, at: datetime) -> None:
    if value.get("schema_version") != SCHEMA_VERSION:
        raise IdentityContractError("unsupported schema version")
    if value.get("canonicalization_version") != CANONICALIZATION_VERSION:
        raise IdentityContractError("unsupported canonicalization version")
    status = value.get("status")
    effective = parse_utc(value["effective_at"], "effective_at")
    expires = parse_utc(value["expires_at"], "expires_at")
    if effective >= expires:
        raise IdentityContractError("effective_at must precede expires_at")
    reviewed_at = value.get("reviewed_at")
    reviewed_by = value.get("reviewed_by")
    evidence = value.get("review_evidence")
    if status == "pending":
        if reviewed_at is not None or reviewed_by is not None or evidence:
            raise IdentityContractError("pending artifact cannot carry affirmative review")
    elif status in {"approved", "rejected"}:
        if not isinstance(reviewed_by, str) or not reviewed_by:
            raise IdentityContractError("reviewed artifact requires a human reviewer")
        if reviewed_at is None or not evidence:
            raise IdentityContractError("reviewed artifact requires time and evidence")
        review_time = parse_utc(reviewed_at, "reviewed_at")
        if review_time > at:
            raise IdentityContractError("review timestamp cannot post-date use")
    else:
        raise IdentityContractError("unknown governed status")
    if status != "approved" or not effective <= at < expires:
        raise IdentityContractError("governed artifact is denied at the evaluation instant")
    _require_sorted_unique(evidence, lambda item: item, "review_evidence")
    require_artifact_hash(value, hash_field)


def _listing_key(item: Mapping[str, Any]) -> tuple[str, str, str, str, str]:
    return (
        item["effective_from"],
        item["effective_to"] or "9999-12-31T23:59:59Z",
        item["ticker"],
        item["exchange_code"],
        item["listing_entry_hash"],
    )


def validate_identity_catalog(value: Mapping[str, Any], at: datetime) -> None:
    validate_schema(value, "identity_catalog")
    _validate_envelope(value, "catalog_hash", at)
    if value["network_state"] != "denied":
        raise IdentityContractError("identity catalog network state must remain denied")
    records = value["records"]
    evidence_records = value["evidence_records"]
    _require_sorted_unique(
        records,
        lambda item: (item["cik"], item["record_id"], item["catalog_record_hash"]),
        "catalog records",
    )
    _require_sorted_unique(
        evidence_records,
        lambda item: (item["cik"], item["source_record_id"], item["evidence_record_hash"]),
        "catalog evidence records",
    )
    evidence_by_id: dict[str, Mapping[str, Any]] = {}
    for evidence in evidence_records:
        require_artifact_hash(evidence, "evidence_record_hash")
        if evidence["source_record_id"] in evidence_by_id:
            raise IdentityContractError("duplicate source_record_id")
        evidence_by_id[evidence["source_record_id"]] = evidence
        observed = parse_utc(evidence["observed_at"], "observed_at")
        fact_as_of = parse_utc(evidence["fact_as_of"], "fact_as_of")
        if fact_as_of > observed:
            raise IdentityContractError("fact_as_of cannot follow observed_at")
        if observed > at:
            raise IdentityContractError("future evidence post-dates evaluation")
        asserted_from = parse_utc(evidence["asserted_effective_from"], "asserted_effective_from")
        asserted_to = (
            parse_utc(evidence["asserted_effective_to"], "asserted_effective_to")
            if evidence["asserted_effective_to"] is not None
            else None
        )
        if evidence["assertion_kind"] == "active_as_of":
            if asserted_to is not None or not asserted_from <= fact_as_of <= observed:
                raise IdentityContractError("active evidence assertion interval is invalid")
        elif (
            asserted_to is None
            or asserted_from >= asserted_to
            or fact_as_of != asserted_to
            or asserted_to > observed
        ):
            raise IdentityContractError("closed evidence assertion interval is invalid")
    ciks: set[str] = set()
    record_hashes: set[str] = set()
    for record in records:
        require_artifact_hash(record, "catalog_record_hash")
        if record["cik"] in ciks:
            raise IdentityContractError("catalog CIK values must be unique")
        if record["catalog_record_hash"] in record_hashes:
            raise IdentityContractError("catalog record hashes must be unique")
        ciks.add(record["cik"])
        record_hashes.add(record["catalog_record_hash"])
        aliases = record["aliases"]
        _require_sorted_unique(
            aliases,
            lambda item: (normalize_company_name(item), item),
            "record aliases",
        )
        listings = record["listing_history"]
        _require_sorted_unique(listings, _listing_key, "listing history")
        _require_sorted_unique(record["source_record_refs"], lambda item: item, "source refs")
        for source_ref in record["source_record_refs"]:
            if source_ref not in evidence_by_id:
                raise IdentityContractError("catalog source reference does not close")
        active_listings: list[tuple[Mapping[str, Any], list[Mapping[str, Any]]]] = []
        for listing in listings:
            require_artifact_hash(listing, "listing_entry_hash")
            _require_sorted_unique(
                listing["evidence_record_refs"], lambda item: item, "listing evidence refs"
            )
            start = parse_utc(listing["effective_from"], "effective_from")
            end = (
                parse_utc(listing["effective_to"], "effective_to")
                if listing["effective_to"] is not None
                else None
            )
            if end is not None and start >= end:
                raise IdentityContractError("listing effective interval is invalid")
            if start > at or (end is not None and end > at):
                raise IdentityContractError("future listing evidence post-dates evaluation")
            referenced_evidence: list[Mapping[str, Any]] = []
            for source_ref in listing["evidence_record_refs"]:
                evidence = evidence_by_id.get(source_ref)
                if evidence is None:
                    raise IdentityContractError("listing evidence reference does not close")
                identity = (
                    evidence["cik"],
                    evidence["legal_name"],
                    evidence["ticker"],
                    evidence["exchange_code"],
                )
                expected = (
                    record["cik"],
                    record["legal_name"],
                    listing["ticker"],
                    listing["exchange_code"],
                )
                if identity != expected:
                    if identity[:2] != expected[:2]:
                        raise IdentityContractError("CIK and legal-name evidence conflict")
                    raise IdentityContractError("listing evidence conflicts with catalog")
                referenced_evidence.append(evidence)
            if end is None:
                qualifying = [
                    item
                    for item in referenced_evidence
                    if item["assertion_kind"] == "active_as_of"
                    and item["asserted_effective_from"] == listing["effective_from"]
                    and item["asserted_effective_to"] is None
                ]
                if not qualifying:
                    raise IdentityContractError("open listing lacks active evidence")
                active_listings.append((listing, qualifying))
            else:
                qualifying = [
                    item
                    for item in referenced_evidence
                    if item["assertion_kind"] == "closed_interval"
                    and item["asserted_effective_from"] == listing["effective_from"]
                    and item["asserted_effective_to"] == listing["effective_to"]
                    and item["fact_as_of"] == listing["effective_to"]
                ]
                if not qualifying:
                    raise IdentityContractError("closed listing lacks retrospective evidence")
        if record["public_company_status"] == "active":
            if len(active_listings) != 1:
                raise IdentityContractError("active record requires exactly one active listing")
            expected_observed = min(
                item["observed_at"] for item in active_listings[0][1]
            )
            if record["identity_observed_at"] != expected_observed:
                raise IdentityContractError("identity_observed_at does not close to active evidence")


def validate_identity_policy(value: Mapping[str, Any], at: datetime) -> None:
    validate_schema(value, "identity_policy")
    _validate_envelope(value, "identity_policy_hash", at)
    if value["network_state"] != "denied":
        raise IdentityContractError("identity policy network state must remain denied")
    _require_sorted_unique(
        value["match_ranks"],
        lambda item: (item["rank"], item["precedence"], item["match_kind"]),
        "match ranks",
    )
    actual_ranks = tuple(
        (item["match_kind"], item["rank"], item["precedence"])
        for item in value["match_ranks"]
    )
    if actual_ranks != _LOCKED_MATCH_RANKS:
        raise IdentityContractError("identity policy rank and precedence table is not contract-locked")
    for field in (
        "allowed_query_kinds",
        "allowed_match_kinds",
        "issuer_classes",
        "public_company_statuses",
        "evidence_assertion_kinds",
        "derived_temporal_classifications",
        "synthetic_adapter_ids",
        "supported_primary_listing_countries",
        "supported_reporting_currencies",
        "synthetic_exchange_codes",
    ):
        _require_sorted_unique(value[field], lambda item: item, field)


def validate_scope_registry(value: Mapping[str, Any], at: datetime) -> None:
    validate_schema(value, "scope_registry")
    _validate_envelope(value, "scope_registry_hash", at)
    _require_sorted_unique(
        value["rules"], lambda item: (item["priority"], item["rule_id"]), "scope rules"
    )
    _require_sorted_unique(
        value["deferred_matrix_rows"], lambda item: item["row_id"], "deferred rows"
    )
    actual_rules = tuple(
        (
            rule["rule_id"],
            rule["priority"],
            tuple(
                (predicate["field"], predicate["operator"], predicate["value"])
                for predicate in rule["predicates"]
            ),
            rule["outcome"],
            rule["reason_code"],
        )
        for rule in value["rules"]
    )
    if actual_rules != _LOCKED_SCOPE_RULES:
        raise IdentityContractError(
            "scope registry rule semantics are not contract-locked or are contradictory"
        )
    if tuple(item["row_id"] for item in value["deferred_matrix_rows"]) != _LOCKED_DEFERRED_ROWS:
        raise IdentityContractError("scope registry deferred M8 rows are not contract-locked")
    required_reasons = {
        "SCOPE-IN-SCOPE-PENDING-REVIEW",
        "SCOPE-UNSUPPORTED-FINANCIAL",
        "SCOPE-UNSUPPORTED-REIT",
        "SCOPE-UNSUPPORTED-FUND",
        "SCOPE-UNSUPPORTED-SPAC",
        "SCOPE-UNSUPPORTED-NATURAL-RESOURCE",
        "SCOPE-UNSUPPORTED-NON-US",
        "SCOPE-UNSUPPORTED-NON-USD",
        "SCOPE-UNSUPPORTED-PRIVATE",
    }
    if {item["reason_code"] for item in value["rules"]} != required_reasons:
        raise IdentityContractError("scope registry does not close the M8 structural reasons")
    matrix_path = ROOT / value["m8_support_matrix_ref"]
    try:
        import hashlib

        matrix_hash = hashlib.sha256(matrix_path.read_bytes()).hexdigest()
    except OSError as exc:
        raise IdentityContractError("M8 support matrix reference does not close") from exc
    if matrix_hash != value["m8_support_matrix_sha256"]:
        raise IdentityContractError("M8 support matrix hash does not close")


def normalize_company_name(value: str) -> str:
    import unicodedata

    return " ".join(unicodedata.normalize("NFKC", value).strip().split()).casefold()


def freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({key: freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(freeze(item) for item in value)
    return value


def load_identity_catalog(path: Path, at: datetime) -> Mapping[str, Any]:
    value = strict_load(path)
    validate_identity_catalog(value, at)
    return freeze(value)


def load_identity_policy(path: Path, at: datetime) -> Mapping[str, Any]:
    value = strict_load(path)
    validate_identity_policy(value, at)
    return freeze(value)


def load_scope_registry(path: Path, at: datetime) -> Mapping[str, Any]:
    value = strict_load(path)
    validate_scope_registry(value, at)
    return freeze(value)
