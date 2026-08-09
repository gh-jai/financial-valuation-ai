"""Strict immutable provider/license and concept registries for M9-I1."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from types import MappingProxyType
from typing import Any
from urllib.parse import urlsplit

import yaml


_IDENTIFIER = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
_VERSION = re.compile(r"^\d+\.\d+\.\d+$")
_HOSTNAME = re.compile(
    r"^(?=.{1,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+"
    r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$"
)
_RIGHTS = frozenset({"storage", "display", "export", "redistribution"})
_PROVIDER_STATUS = frozenset({"pending", "approved", "rejected"})
_AUTH_CLASSES = frozenset({"none", "api_key", "oauth2", "user_agent"})
_CONCEPT_KINDS = frozenset({"monetary", "rate", "shares"})
_PROVIDER_REGISTRY_ID = "m9-provider-license"
_CONCEPT_REGISTRY_ID = "m9-concepts"
_SUPPORTED_SCHEMA_VERSION = "0.1.0"


class RegistryError(ValueError):
    """Raised when a registry violates its strict fail-closed contract."""


def _mapping(value: Any, label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise RegistryError(f"{label} must be an object")
    if any(not isinstance(key, str) for key in value):
        raise RegistryError(f"{label} keys must be strings")
    return value


def _exact_fields(
    value: Mapping[str, Any], required: frozenset[str], label: str
) -> None:
    missing = required - value.keys()
    unknown = value.keys() - required
    if missing:
        raise RegistryError(f"{label} missing fields: {', '.join(sorted(missing))}")
    if unknown:
        raise RegistryError(f"{label} unknown fields: {', '.join(sorted(unknown))}")


def _text(value: Any, label: str, *, pattern: re.Pattern[str] | None = None) -> str:
    if not isinstance(value, str) or not value or value != value.strip():
        raise RegistryError(f"{label} must be a non-empty trimmed string")
    if pattern is not None and not pattern.fullmatch(value):
        raise RegistryError(f"{label} has an invalid format")
    return value


def _string_tuple(value: Any, label: str, *, identifier: bool = False) -> tuple[str, ...]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise RegistryError(f"{label} must be an array")
    pattern = _IDENTIFIER if identifier else None
    items = tuple(_text(item, f"{label} item", pattern=pattern) for item in value)
    if len(set(items)) != len(items):
        raise RegistryError(f"{label} contains duplicates")
    return items


def _date(value: Any, label: str) -> date:
    text = _text(value, label)
    try:
        parsed = date.fromisoformat(text)
    except ValueError as exc:
        raise RegistryError(f"{label} must be an ISO date") from exc
    if parsed.isoformat() != text:
        raise RegistryError(f"{label} must use YYYY-MM-DD")
    return parsed


def _url_tuple(value: Any, label: str) -> tuple[str, ...]:
    urls = _string_tuple(value, label)
    for url in urls:
        parsed = urlsplit(url)
        if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
            raise RegistryError(f"{label} entries must be credential-free HTTPS URLs")
    return urls


def _host_tuple(value: Any, label: str) -> tuple[str, ...]:
    hosts = _string_tuple(value, label)
    for host in hosts:
        if not _HOSTNAME.fullmatch(host):
            raise RegistryError(f"{label} entries must be canonical hostnames")
    return hosts


def _require_registry_identity(
    root: Mapping[str, Any], *, registry_id: str, label: str
) -> tuple[str, str]:
    actual_id = _text(root["registry_id"], "registry_id", pattern=_IDENTIFIER)
    if actual_id != registry_id:
        raise RegistryError(f"{label} registry_id is not supported")
    schema_version = _text(root["schema_version"], "schema_version", pattern=_VERSION)
    if schema_version != _SUPPORTED_SCHEMA_VERSION:
        raise RegistryError(f"{label} schema_version is not supported")
    return actual_id, schema_version


def _load(path: Path) -> Mapping[str, Any]:
    if not isinstance(path, Path):
        raise TypeError("registry path must be a pathlib.Path")
    try:
        content = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise RegistryError(f"cannot load registry {path.name}") from exc
    return _mapping(content, "registry")


@dataclass(frozen=True, slots=True)
class ProviderPolicy:
    provider_id: str
    provider_name: str
    version: str
    status: str
    live_activation: str
    endpoint_templates: tuple[str, ...]
    host_allowlist: tuple[str, ...]
    redirect_host_allowlist: tuple[str, ...]
    data_categories: tuple[str, ...]
    authentication_class: str
    retention_days: int
    rights: Mapping[str, bool]
    territories: tuple[str, ...]
    attribution: str
    review_date: date
    expires_on: date
    review_evidence: tuple[str, ...]
    rate_window_seconds: int
    rate_max_requests: int


@dataclass(frozen=True, slots=True)
class ProviderDecision:
    allowed: bool
    reason: str
    provider_id: str
    registry_version: str


@dataclass(frozen=True, slots=True)
class ProviderRegistry:
    registry_id: str
    schema_version: str
    records: tuple[ProviderPolicy, ...]
    by_id: Mapping[str, ProviderPolicy]

    def authorize(
        self,
        provider_id: str,
        *,
        category: str,
        right: str,
        territory: str,
        as_of: date,
    ) -> ProviderDecision:
        """Evaluate one bounded use; every absent or incompatible fact denies."""

        record = self.by_id.get(provider_id)
        reason = "provider_unknown"
        if record is not None:
            if record.status != "approved":
                reason = "provider_not_approved"
            elif record.live_activation != "disabled":
                reason = "invalid_live_activation"
            elif as_of > record.expires_on:
                reason = "approval_expired"
            elif category not in record.data_categories:
                reason = "category_denied"
            elif right not in _RIGHTS or record.rights.get(right) is not True:
                reason = "right_denied"
            elif territory not in record.territories:
                reason = "territory_denied"
            else:
                return ProviderDecision(True, "approved", provider_id, self.schema_version)
        return ProviderDecision(False, reason, provider_id, self.schema_version)


@dataclass(frozen=True, slots=True)
class ConceptDefinition:
    concept_id: str
    label: str
    kind: str
    allowed_units: tuple[str, ...]
    required_for: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ConceptRegistry:
    registry_id: str
    schema_version: str
    records: tuple[ConceptDefinition, ...]
    by_id: Mapping[str, ConceptDefinition]


_PROVIDER_ROOT_FIELDS = frozenset({"registry_id", "schema_version", "providers"})
_PROVIDER_FIELDS = frozenset(
    {
        "provider_id",
        "provider_name",
        "version",
        "status",
        "live_activation",
        "endpoint_templates",
        "host_allowlist",
        "redirect_host_allowlist",
        "data_categories",
        "authentication_class",
        "retention_days",
        "rights",
        "territories",
        "attribution",
        "review_date",
        "expires_on",
        "review_evidence",
        "rate_limit",
    }
)


def _provider_record(value: Any, index: int) -> ProviderPolicy:
    record = _mapping(value, f"provider {index}")
    _exact_fields(record, _PROVIDER_FIELDS, f"provider {index}")
    status = _text(record["status"], "status")
    if status not in _PROVIDER_STATUS:
        raise RegistryError("provider status is not recognized")
    if record["live_activation"] != "disabled":
        raise RegistryError("M9-I1 live_activation must be disabled")
    auth_class = _text(record["authentication_class"], "authentication_class")
    if auth_class not in _AUTH_CLASSES:
        raise RegistryError("authentication_class is not recognized")
    retention = record["retention_days"]
    if isinstance(retention, bool) or not isinstance(retention, int) or retention < 0:
        raise RegistryError("retention_days must be a non-negative integer")
    rights = _mapping(record["rights"], "rights")
    _exact_fields(rights, _RIGHTS, "rights")
    if any(type(rights[name]) is not bool for name in _RIGHTS):
        raise RegistryError("rights values must be booleans")
    review_date = _date(record["review_date"], "review_date")
    expires_on = _date(record["expires_on"], "expires_on")
    if expires_on < review_date:
        raise RegistryError("expires_on cannot precede review_date")
    rate = _mapping(record["rate_limit"], "rate_limit")
    _exact_fields(rate, frozenset({"window_seconds", "max_requests"}), "rate_limit")
    rate_values = (rate["window_seconds"], rate["max_requests"])
    if any(isinstance(item, bool) or not isinstance(item, int) or item < 1 for item in rate_values):
        raise RegistryError("rate_limit values must be positive integers")
    endpoints = _url_tuple(record["endpoint_templates"], "endpoint_templates")
    hosts = _host_tuple(record["host_allowlist"], "host_allowlist")
    redirects = _host_tuple(record["redirect_host_allowlist"], "redirect_host_allowlist")
    if any(urlsplit(endpoint).hostname not in hosts for endpoint in endpoints):
        raise RegistryError("endpoint_templates host is not in host_allowlist")
    return ProviderPolicy(
        provider_id=_text(record["provider_id"], "provider_id", pattern=_IDENTIFIER),
        provider_name=_text(record["provider_name"], "provider_name"),
        version=_text(record["version"], "version", pattern=_VERSION),
        status=status,
        live_activation="disabled",
        endpoint_templates=endpoints,
        host_allowlist=hosts,
        redirect_host_allowlist=redirects,
        data_categories=_string_tuple(
            record["data_categories"], "data_categories", identifier=True
        ),
        authentication_class=auth_class,
        retention_days=retention,
        rights=MappingProxyType(dict(rights)),
        territories=_string_tuple(record["territories"], "territories"),
        attribution=_text(record["attribution"], "attribution"),
        review_date=review_date,
        expires_on=expires_on,
        review_evidence=_string_tuple(record["review_evidence"], "review_evidence"),
        rate_window_seconds=rate_values[0],
        rate_max_requests=rate_values[1],
    )


def load_provider_registry(path: Path) -> ProviderRegistry:
    """Load a strict provider/license registry into immutable records."""

    root = _load(path)
    _exact_fields(root, _PROVIDER_ROOT_FIELDS, "provider registry")
    registry_id, schema_version = _require_registry_identity(
        root, registry_id=_PROVIDER_REGISTRY_ID, label="provider registry"
    )
    values = root["providers"]
    if not isinstance(values, list) or not values:
        raise RegistryError("providers must be a non-empty array")
    records = tuple(_provider_record(value, index) for index, value in enumerate(values))
    by_id = {record.provider_id: record for record in records}
    if len(by_id) != len(records):
        raise RegistryError("provider_id values must be unique")
    return ProviderRegistry(
        registry_id=registry_id,
        schema_version=schema_version,
        records=records,
        by_id=MappingProxyType(by_id),
    )


_CONCEPT_ROOT_FIELDS = frozenset({"registry_id", "schema_version", "concepts"})
_CONCEPT_FIELDS = frozenset(
    {"concept_id", "label", "kind", "allowed_units", "required_for"}
)


def _concept_record(value: Any, index: int) -> ConceptDefinition:
    record = _mapping(value, f"concept {index}")
    _exact_fields(record, _CONCEPT_FIELDS, f"concept {index}")
    kind = _text(record["kind"], "kind")
    if kind not in _CONCEPT_KINDS:
        raise RegistryError("concept kind is not recognized")
    return ConceptDefinition(
        concept_id=_text(record["concept_id"], "concept_id", pattern=_IDENTIFIER),
        label=_text(record["label"], "label"),
        kind=kind,
        allowed_units=_string_tuple(record["allowed_units"], "allowed_units"),
        required_for=_string_tuple(record["required_for"], "required_for", identifier=True),
    )


def load_concept_registry(path: Path) -> ConceptRegistry:
    """Load the bounded M1-M6 input vocabulary without provider mappings."""

    root = _load(path)
    _exact_fields(root, _CONCEPT_ROOT_FIELDS, "concept registry")
    registry_id, schema_version = _require_registry_identity(
        root, registry_id=_CONCEPT_REGISTRY_ID, label="concept registry"
    )
    values = root["concepts"]
    if not isinstance(values, list) or not values:
        raise RegistryError("concepts must be a non-empty array")
    records = tuple(_concept_record(value, index) for index, value in enumerate(values))
    by_id = {record.concept_id: record for record in records}
    if len(by_id) != len(records):
        raise RegistryError("concept_id values must be unique")
    return ConceptRegistry(
        registry_id=registry_id,
        schema_version=schema_version,
        records=records,
        by_id=MappingProxyType(by_id),
    )
