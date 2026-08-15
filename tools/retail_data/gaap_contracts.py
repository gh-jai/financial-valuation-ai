"""Strict, synthetic-only contracts for the M9-I5 normalization runtime."""

from __future__ import annotations

import copy
import re
from collections.abc import Mapping
from decimal import Decimal, InvalidOperation, localcontext
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from .canonical import CANONICALIZATION_VERSION, canonical_sha256
from .identity_contracts import strict_load

ROOT = Path(__file__).resolve().parents[2]
SCHEMAS = ROOT / "schemas"
SCHEMA_VERSION = "0.1.0"
CONCEPT_REGISTRY_HASH = "6d4e0331a709e2b4152fd6e846bfe84cb22978cc3bd0de19599e80847edb7fa9"
CONTRACT_HASH = "99ee481383eece5d21f45e22dc2ced16f3e04f3bd8ae169ac7c58279c8121949"
MAX_DECIMAL_CHARACTERS = 256
MAX_ABS_EXPONENT = 128

CONCEPT_IDS = (
    "revenue",
    "operating-income",
    "statutory-tax-rate",
    "cash-taxes",
    "depreciation-amortization",
    "capital-expenditure",
    "noncash-working-capital",
    "debt",
    "cash",
    "nonoperating-assets",
    "minority-interest",
    "other-claims",
    "diluted-shares",
)

RECONCILIATION_FAMILIES = (
    "balance-sheet",
    "cash-flow",
    "annual-quarterly",
    "unit-scale",
    "currency",
    "shares-split",
    "amendment",
    "duplicate-fact",
    "custom-tag",
    "fcff-completeness",
)

_DECIMAL = re.compile(r"^(?:0|-?(?:[1-9][0-9]*)(?:\.[0-9]*[1-9])?|0\.[0-9]*[1-9]|-0\.[0-9]*[1-9])$")
_SAFE_REF = re.compile(r"^[A-Z][A-Z0-9-]{1,127}$")
_ACCESSION = re.compile(r"^[0-9]{10}-[0-9]{2}-[0-9]{6}$")
_UTC_SECONDS = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$")
_RAW_FACT_FIELDS = frozenset(
    {
        "source_fact_id",
        "source_fact_hash",
        "namespace",
        "local_name",
        "value_decimal",
        "unit",
        "currency",
        "start",
        "end",
        "filing_record_ref",
        "accession",
        "filed_at",
        "form",
        "fiscal_year",
        "fiscal_period",
        "scale",
        "decimals",
        "context_id",
        "dimensions",
        "amendment_of_accession",
        "material",
        "synthetic",
    }
)


class NormalizationError(ValueError):
    """An input or artifact violated the fail-closed M9-I5 contract."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def self_hash(value: Mapping[str, Any], field: str) -> str:
    """Hash a canonical artifact while excluding its self-hash field."""

    subject = {key: copy.deepcopy(item) for key, item in value.items() if key != field}
    return canonical_sha256(subject)


def attach_self_hash(value: Mapping[str, Any], field: str) -> dict[str, Any]:
    """Return a detached artifact with its recomputed self-hash."""

    result = copy.deepcopy(dict(value))
    result[field] = self_hash(result, field)
    return result


def require_self_hash(value: Mapping[str, Any], field: str) -> None:
    if value.get(field) != self_hash(value, field):
        raise NormalizationError("NORM-HASH-MISMATCH", f"{field} does not match")


def deterministic_id(prefix: str, subject: Mapping[str, Any]) -> str:
    """Build a schema-compatible deterministic identifier from canonical content."""

    return f"{prefix}-{canonical_sha256(subject)[:24].upper()}"


def validate_schema(value: Mapping[str, Any], filename: str) -> None:
    schema = strict_load(SCHEMAS / filename)
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(dict(value)),
        key=lambda item: list(item.absolute_path),
    )
    if errors:
        location = ".".join(str(part) for part in errors[0].absolute_path) or "<root>"
        raise NormalizationError(
            "NORM-AUTHORITY-DENIED", f"{filename} validation failed at {location}"
        )


def load_synthetic_fixture(path: Path) -> dict[str, Any]:
    """Load a strict JSON fixture and enforce its offline/synthetic authority markers."""

    value = strict_load(path)
    if value.get("network_state") != "denied" or value.get("synthetic_only") is not True:
        raise NormalizationError("NORM-AUTHORITY-DENIED", "fixture authority is denied")
    require_self_hash(value, "fixture_hash")
    snapshot = value.get("source_snapshot")
    if not isinstance(snapshot, dict):
        raise NormalizationError("NORM-REFERENCE-MISSING", "source snapshot is missing")
    if value.get("source_snapshot_hash") != canonical_sha256(snapshot):
        raise NormalizationError("NORM-HASH-MISMATCH", "source snapshot hash does not match")
    facts = value.get("facts")
    if not isinstance(facts, list) or not facts:
        raise NormalizationError("NORM-MATERIAL-MISSING", "fixture facts are missing")
    for fact in facts:
        require_raw_fact(fact)
    return value


def require_raw_fact(value: Any) -> None:
    """Validate the exact bounded source-fact envelope without accepting provider payloads."""

    if not isinstance(value, dict) or set(value) != _RAW_FACT_FIELDS:
        raise NormalizationError("NORM-AUTHORITY-DENIED", "raw fact surface is not locked")
    if value["synthetic"] is not True:
        raise NormalizationError("NORM-AUTHORITY-DENIED", "non-synthetic fact is denied")
    if type(value["material"]) is not bool:
        raise NormalizationError("NORM-AUTHORITY-DENIED", "materiality marker is invalid")
    if not isinstance(value["source_fact_id"], str) or not _SAFE_REF.fullmatch(
        value["source_fact_id"]
    ):
        raise NormalizationError("NORM-REFERENCE-MISSING", "source fact ID is invalid")
    require_self_hash(value, "source_fact_hash")
    if value["namespace"] != "us-gaap" and not (
        isinstance(value["namespace"], str) and value["namespace"].startswith("synthetic:")
    ):
        raise NormalizationError("NORM-AUTHORITY-DENIED", "taxonomy namespace is denied")
    if not isinstance(value["local_name"], str) or not re.fullmatch(
        r"[A-Za-z][A-Za-z0-9]{0,127}", value["local_name"]
    ):
        raise NormalizationError("NORM-CONCEPT-UNMAPPED", "local name is invalid")
    if value["unit"] not in {"USD", "ratio", "shares"}:
        raise NormalizationError("NORM-UNIT-SCALE", "unit is unsupported")
    if value["currency"] not in {"USD", None}:
        raise NormalizationError("NORM-UNIT-SCALE", "currency is unsupported")
    if value["unit"] == "USD" and value["currency"] != "USD":
        raise NormalizationError("NORM-UNIT-SCALE", "USD fact requires USD currency")
    if value["unit"] != "USD" and value["currency"] is not None:
        raise NormalizationError("NORM-UNIT-SCALE", "non-monetary fact cannot carry currency")
    if value["form"] not in {
        "SYNTHETIC-ANNUAL",
        "SYNTHETIC-QUARTERLY",
        "SYNTHETIC-AMENDMENT",
    }:
        raise NormalizationError("NORM-AUTHORITY-DENIED", "non-synthetic form is denied")
    if not isinstance(value["fiscal_year"], int) or not 1900 <= value["fiscal_year"] <= 9999:
        raise NormalizationError("NORM-PERIOD-AMBIGUOUS", "fiscal year is invalid")
    if value["fiscal_period"] not in {"FY", "Q1", "Q2", "Q3", "Q4", "TTM", "INSTANT"}:
        raise NormalizationError("NORM-PERIOD-AMBIGUOUS", "fiscal period is invalid")
    if not isinstance(value["end"], str) or not re.fullmatch(
        r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value["end"]
    ):
        raise NormalizationError("NORM-PERIOD-AMBIGUOUS", "end date is invalid")
    if value["start"] is not None and (
        not isinstance(value["start"], str)
        or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value["start"])
    ):
        raise NormalizationError("NORM-PERIOD-AMBIGUOUS", "start date is invalid")
    if not isinstance(value["accession"], str) or not _ACCESSION.fullmatch(value["accession"]):
        raise NormalizationError("NORM-AMENDMENT-CONFLICT", "accession is invalid")
    predecessor = value["amendment_of_accession"]
    if predecessor is not None and (
        not isinstance(predecessor, str) or not _ACCESSION.fullmatch(predecessor)
    ):
        raise NormalizationError("NORM-AMENDMENT-CONFLICT", "amendment accession is invalid")
    if not isinstance(value["filed_at"], str) or not _UTC_SECONDS.fullmatch(value["filed_at"]):
        raise NormalizationError("NORM-PERIOD-AMBIGUOUS", "filed instant is invalid")
    if not isinstance(value["filing_record_ref"], str) or not _SAFE_REF.fullmatch(
        value["filing_record_ref"]
    ):
        raise NormalizationError("NORM-REFERENCE-MISSING", "filing record reference is invalid")
    if not isinstance(value["context_id"], str) or not _SAFE_REF.fullmatch(value["context_id"]):
        raise NormalizationError("NORM-REFERENCE-MISSING", "context reference is invalid")
    if type(value["scale"]) is not int or not -18 <= value["scale"] <= 18:
        raise NormalizationError("NORM-UNIT-SCALE", "scale is outside the locked bound")
    if type(value["decimals"]) is not int or not -18 <= value["decimals"] <= 18:
        raise NormalizationError("NORM-UNIT-SCALE", "decimals is outside the locked bound")
    if not isinstance(value["dimensions"], dict) or any(
        not isinstance(key, str) or not isinstance(item, str)
        for key, item in value["dimensions"].items()
    ):
        raise NormalizationError("NORM-AUTHORITY-DENIED", "dimensions are invalid")
    canonical_decimal(value["value_decimal"])


def canonical_decimal(value: str) -> str:
    """Require the locked canonical base-10 lexical form."""

    if (
        not isinstance(value, str)
        or len(value) > MAX_DECIMAL_CHARACTERS
        or not _DECIMAL.fullmatch(value)
    ):
        raise NormalizationError("NORM-UNIT-SCALE", "decimal lexical form is invalid")
    return value


def decimal_value(value: str) -> Decimal:
    canonical_decimal(value)
    try:
        with localcontext() as context:
            context.prec = MAX_DECIMAL_CHARACTERS + MAX_ABS_EXPONENT
            return Decimal(value)
    except InvalidOperation as exc:
        raise NormalizationError("NORM-UNIT-SCALE", "decimal value is invalid") from exc


def decimal_text(value: Decimal) -> str:
    """Serialize an exact Decimal into the one canonical lexical representation."""

    if not value.is_finite() or value.adjusted() > MAX_ABS_EXPONENT:
        raise NormalizationError("NORM-UNIT-SCALE", "decimal result exceeds the locked bound")
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    if text in {"", "-0"}:
        text = "0"
    return canonical_decimal(text)


def scale_and_apply_polarity(value: str, scale: int, polarity: int) -> str:
    if polarity not in {-1, 1} or type(scale) is not int or not -18 <= scale <= 18:
        raise NormalizationError("NORM-SIGN-AMBIGUOUS", "scale or polarity is invalid")
    with localcontext() as context:
        context.prec = MAX_DECIMAL_CHARACTERS + MAX_ABS_EXPONENT
        result = decimal_value(value) * (Decimal(10) ** scale) * polarity
    return decimal_text(result)


def safe_finding(code: str, severity: str, message: str, *subject_refs: str) -> dict[str, Any]:
    if not re.fullmatch(r"NORM-[A-Z0-9-]+", code):
        raise NormalizationError("NORM-AUTHORITY-DENIED", "finding code is not locked")
    if severity not in {"info", "review", "blocking"}:
        raise NormalizationError("NORM-AUTHORITY-DENIED", "finding severity is invalid")
    refs = sorted(set(subject_refs))
    if not refs or any(not _SAFE_REF.fullmatch(ref) for ref in refs):
        raise NormalizationError("NORM-REFERENCE-MISSING", "finding reference is invalid")
    return {"code": code, "severity": severity, "message": message[:256], "subject_refs": refs}


def finalize_artifact(
    value: Mapping[str, Any], *, hash_field: str, schema_filename: str
) -> dict[str, Any]:
    result = attach_self_hash(value, hash_field)
    validate_schema(result, schema_filename)
    return result


__all__ = [
    "CANONICALIZATION_VERSION",
    "CONCEPT_IDS",
    "CONCEPT_REGISTRY_HASH",
    "CONTRACT_HASH",
    "RECONCILIATION_FAMILIES",
    "SCHEMA_VERSION",
    "NormalizationError",
    "attach_self_hash",
    "canonical_decimal",
    "decimal_text",
    "decimal_value",
    "deterministic_id",
    "finalize_artifact",
    "load_synthetic_fixture",
    "require_raw_fact",
    "require_self_hash",
    "safe_finding",
    "scale_and_apply_polarity",
    "self_hash",
    "validate_schema",
]
