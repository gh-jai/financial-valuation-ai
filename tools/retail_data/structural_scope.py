"""Default-deny structural scope pre-screening for M9-I2 verified identities."""

from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from typing import Any

from .canonical import CANONICALIZATION_VERSION
from .errors import ErrorSeverity, NextAction, RetailDataError
from .identity_contracts import (
    IdentityContractError,
    attach_hash,
    parse_utc,
    require_artifact_hash,
    validate_identity_policy,
    validate_schema,
    validate_scope_registry,
)
from .resolution import ResolutionStop, _plain


SCOPE_EVALUATOR_VERSION = "0.1.0"

_MESSAGES = {
    "SCOPE-REGISTRY-DENIED": "The structural-scope registry is unavailable or denied.",
    "SCOPE-UNSUPPORTED-FINANCIAL": "The issuer requires an unsupported financial valuation model.",
    "SCOPE-UNSUPPORTED-REIT": "REIT issuers are outside the approved structural scope.",
    "SCOPE-UNSUPPORTED-FUND": "Fund and non-operating vehicles are outside structural scope.",
    "SCOPE-UNSUPPORTED-SPAC": "SPAC and blank-check issuers are outside structural scope.",
    "SCOPE-UNSUPPORTED-NATURAL-RESOURCE": "Reserve real-option cases are outside scope.",
    "SCOPE-UNSUPPORTED-NON-US": "Non-US primary listings are outside structural scope.",
    "SCOPE-UNSUPPORTED-NON-USD": "Non-USD reporting issuers are outside structural scope.",
    "SCOPE-UNSUPPORTED-PRIVATE": "Private companies are outside structural scope.",
    "SCOPE-INSUFFICIENT-EVIDENCE": "Structural identity evidence is missing or contradictory.",
}


def _scope_error(code: str, *refs: str) -> dict[str, Any]:
    action = NextAction.UPDATE_REGISTRY if code == "SCOPE-REGISTRY-DENIED" else NextAction.STOP
    if code == "SCOPE-INSUFFICIENT-EVIDENCE":
        action = NextAction.VERIFY_IDENTITY
    return RetailDataError(
        code=code,
        message=_MESSAGES[code],
        severity=ErrorSeverity.BLOCKING,
        retryable=False,
        artifact_refs=tuple(sorted(set(refs))),
        next_action=action,
    ).to_dict()


def _matches(identity: Mapping[str, Any], predicates: list[Mapping[str, Any]]) -> bool:
    for predicate in predicates:
        field = predicate["field"]
        if field not in identity:
            return False
        if predicate["operator"] == "equals" and identity[field] != predicate["value"]:
            return False
        if predicate["operator"] == "not_equals" and identity[field] == predicate["value"]:
            return False
    return True


def evaluate_structural_scope(
    verified_identity: Mapping[str, Any], scope_registry: Mapping[str, Any],
    identity_policy: Mapping[str, Any], *, scope_decision_id: str, evaluated_at: str,
) -> dict[str, Any]:
    """Evaluate only M8 structural predicates; lifecycle routing stays not evaluated."""

    identity = _plain(verified_identity)
    registry = _plain(scope_registry)
    policy = _plain(identity_policy)
    validate_schema(identity, "verified_identity")
    require_artifact_hash(identity, "verified_identity_hash")
    at = parse_utc(evaluated_at, "evaluated_at")
    if at < parse_utc(identity["verified_at"], "verified_at"):
        raise ResolutionStop(
            RetailDataError(
                "IDENTITY-HASH-MISMATCH",
                "The scope evaluation timestamp precedes identity verification.",
                ErrorSeverity.BLOCKING,
                False,
                (identity["verified_identity_id"],),
                NextAction.STOP,
            )
        )
    try:
        validate_identity_policy(policy, at)
    except IdentityContractError as exc:
        raise ResolutionStop(
            RetailDataError(
                "IDENTITY-POLICY-DENIED",
                "The identity-resolution policy is unavailable or denied.",
                ErrorSeverity.BLOCKING,
                False,
                ("policy:denied",),
                NextAction.UPDATE_REGISTRY,
            )
        ) from exc
    try:
        validate_scope_registry(registry, at)
    except IdentityContractError as exc:
        raise ResolutionStop(
            RetailDataError(
                "SCOPE-REGISTRY-DENIED",
                _MESSAGES["SCOPE-REGISTRY-DENIED"],
                ErrorSeverity.BLOCKING,
                False,
                ("scope-registry:denied",),
                NextAction.UPDATE_REGISTRY,
            )
        ) from exc
    observed = parse_utc(identity["identity_observed_at"], "identity_observed_at")
    age = int((at - observed).total_seconds())
    if age < 0 or age > policy["max_identity_age_seconds"]:
        code = "IDENTITY-EVIDENCE-FUTURE" if age < 0 else "IDENTITY-STALE"
        message = (
            "Identity evidence post-dates the controlled evaluation time."
            if age < 0
            else "Identity evidence exceeds the approved freshness limit."
        )
        raise ResolutionStop(
            RetailDataError(
                code,
                message,
                ErrorSeverity.BLOCKING,
                False,
                (identity["verified_identity_id"],),
                NextAction.UPDATE_REGISTRY,
            )
        )
    if identity["listing_status"] != "active" or identity["listing_effective_to"] is not None:
        raise ResolutionStop(
            RetailDataError(
                "IDENTITY-DELISTED",
                "The selected identity has no active listing at evaluation time.",
                ErrorSeverity.BLOCKING,
                False,
                (identity["verified_identity_id"],),
                NextAction.STOP,
            )
        )

    required = {
        "public_company_status",
        "primary_listing_country",
        "primary_reporting_currency",
        "issuer_class",
        "regulated_capital_model_required",
        "reserve_real_option_required",
        "exchange_code",
    }
    missing = required - identity.keys()
    recognized = (
        identity.get("issuer_class") in policy["issuer_classes"]
        and identity.get("public_company_status") in policy["public_company_statuses"]
        and identity.get("exchange_code") in policy["synthetic_exchange_codes"]
    )
    financial_classes = {
        "bank",
        "deposit_taking",
        "insurer",
        "broker_dealer",
        "other_regulated_capital_financial",
    }
    classification_consistent = not (
        (
            identity.get("issuer_class") == "operating_non_financial"
            and identity.get("regulated_capital_model_required") is not False
        )
        or (
            identity.get("issuer_class") in financial_classes
            and identity.get("regulated_capital_model_required") is not True
        )
    )
    matched = [rule for rule in registry["rules"] if _matches(identity, rule["predicates"])]
    unsupported = [rule for rule in matched if rule["outcome"] == "unsupported"]
    eligible = [rule for rule in matched if rule["outcome"] == "eligible_for_data_review"]
    if missing or not recognized or not classification_consistent or (unsupported and eligible):
        outcome = "insufficient_evidence"
        rule_ids: list[str] = []
        reason_codes = ["SCOPE-INSUFFICIENT-EVIDENCE"]
        errors = [_scope_error("SCOPE-INSUFFICIENT-EVIDENCE", identity["verified_identity_id"])]
        is_eligible = False
    elif unsupported:
        outcome = "unsupported"
        rule_ids = [rule["rule_id"] for rule in unsupported]
        reason_codes = [rule["reason_code"] for rule in unsupported]
        errors = [
            _scope_error(rule["reason_code"], identity["verified_identity_id"])
            for rule in unsupported
        ]
        errors.sort(
            key=lambda item: (
                item["code"], item["message"], "|".join(item["artifact_refs"]),
                item["next_action"],
            )
        )
        is_eligible = False
    elif len(eligible) == 1:
        outcome = "eligible_for_data_review"
        rule_ids = [eligible[0]["rule_id"]]
        reason_codes = [eligible[0]["reason_code"]]
        errors = []
        is_eligible = True
    else:
        outcome = "insufficient_evidence"
        rule_ids = []
        reason_codes = ["SCOPE-INSUFFICIENT-EVIDENCE"]
        errors = [_scope_error("SCOPE-INSUFFICIENT-EVIDENCE", identity["verified_identity_id"])]
        is_eligible = False

    decision = {
        "schema_version": "0.1.0",
        "canonicalization_version": CANONICALIZATION_VERSION,
        "scope_decision_id": scope_decision_id,
        "created_at": evaluated_at,
        "evaluated_at": evaluated_at,
        "verified_identity_id": identity["verified_identity_id"],
        "verified_identity_hash": identity["verified_identity_hash"],
        "scope_registry_id": registry["scope_registry_id"],
        "scope_registry_version": registry["scope_registry_version"],
        "scope_registry_hash": registry["scope_registry_hash"],
        "structural_rule_ids": rule_ids,
        "deferred_matrix_row_ids": [item["row_id"] for item in registry["deferred_matrix_rows"]],
        "reason_codes": reason_codes,
        "blocking_errors": errors,
        "outcome": outcome,
        "eligible_for_m9_data_review": is_eligible,
        "lifecycle_route_status": "not_evaluated",
    }
    result = attach_hash(decision, "scope_decision_hash")
    validate_schema(result, "scope_decision")
    return result
