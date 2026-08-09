from datetime import date
from pathlib import Path
from types import MappingProxyType

import pytest
import yaml

from tools.retail_data.registries import (
    RegistryError,
    load_concept_registry,
    load_provider_registry,
)


ROOT = Path(__file__).resolve().parents[2]
PROVIDERS = ROOT / "registries/m9-provider-license.yaml"
CONCEPTS = ROOT / "registries/m9-concepts.yaml"


def _provider_data() -> dict:
    return yaml.safe_load(PROVIDERS.read_text(encoding="utf-8"))


def _write(tmp_path: Path, value: dict, name: str = "registry.yaml") -> Path:
    path = tmp_path / name
    path.write_text(yaml.safe_dump(value, sort_keys=False), encoding="utf-8")
    return path


def _approved(tmp_path: Path):
    data = _provider_data()
    record = data["providers"][0]
    record["status"] = "approved"
    record["rights"]["storage"] = True
    return load_provider_registry(_write(tmp_path, data))


def test_committed_registries_load_as_bounded_immutable_records() -> None:
    providers = load_provider_registry(PROVIDERS)
    concepts = load_concept_registry(CONCEPTS)
    assert len(providers.records) == 4
    assert len(concepts.records) == 13
    assert isinstance(providers.by_id, MappingProxyType)
    assert isinstance(providers.records[0].rights, MappingProxyType)
    assert set(concepts.by_id) >= {"revenue", "operating-income", "diluted-shares"}


def test_committed_provider_registry_is_default_deny() -> None:
    registry = load_provider_registry(PROVIDERS)
    for record in registry.records:
        assert record.status == "pending"
        assert record.live_activation == "disabled"
        assert not any(record.rights.values())
        decision = registry.authorize(
            record.provider_id,
            category=record.data_categories[0],
            right="storage",
            territory="US",
            as_of=date(2026, 8, 8),
        )
        assert not decision.allowed and decision.reason == "provider_not_approved"


def test_unknown_expired_and_mismatched_uses_fail_closed(tmp_path: Path) -> None:
    registry = _approved(tmp_path)
    checks = [
        ("unknown", "issuer-identity", "storage", "US", date(2026, 8, 8)),
        ("sec-identity", "other", "storage", "US", date(2026, 8, 8)),
        ("sec-identity", "issuer-identity", "display", "US", date(2026, 8, 8)),
        ("sec-identity", "issuer-identity", "storage", "GB", date(2026, 8, 8)),
        ("sec-identity", "issuer-identity", "storage", "US", date(2027, 1, 1)),
    ]
    for provider, category, right, territory, as_of in checks:
        assert not registry.authorize(
            provider,
            category=category,
            right=right,
            territory=territory,
            as_of=as_of,
        ).allowed


def test_exact_approved_right_is_still_network_disabled(tmp_path: Path) -> None:
    registry = _approved(tmp_path)
    decision = registry.authorize(
        "sec-identity",
        category="issuer-identity",
        right="storage",
        territory="US",
        as_of=date(2026, 8, 8),
    )
    assert decision.allowed and decision.reason == "approved"
    assert registry.by_id["sec-identity"].live_activation == "disabled"


def test_unknown_fields_and_duplicate_identifiers_are_rejected(tmp_path: Path) -> None:
    unknown = _provider_data()
    unknown["providers"][0]["surprise"] = True
    with pytest.raises(RegistryError, match="unknown fields"):
        load_provider_registry(_write(tmp_path, unknown, "unknown.yaml"))
    duplicate = _provider_data()
    duplicate["providers"][1]["provider_id"] = duplicate["providers"][0]["provider_id"]
    with pytest.raises(RegistryError, match="unique"):
        load_provider_registry(_write(tmp_path, duplicate, "duplicate.yaml"))


def test_invalid_types_dates_urls_and_activation_are_rejected(tmp_path: Path) -> None:
    mutations = [
        ("rights", "storage", "yes"),
        ("rate_limit", "max_requests", True),
        (None, "review_date", "08/08/2026"),
        (None, "endpoint_templates", ["http://example.test/data"]),
        (None, "live_activation", "enabled"),
    ]
    for index, (parent, field, value) in enumerate(mutations):
        data = _provider_data()
        target = data["providers"][0]
        if parent is None:
            target[field] = value
        else:
            target[parent][field] = value
        with pytest.raises(RegistryError):
            load_provider_registry(_write(tmp_path, data, f"invalid-{index}.yaml"))


def test_post_load_source_mutation_cannot_change_registry(tmp_path: Path) -> None:
    data = _provider_data()
    registry = load_provider_registry(_write(tmp_path, data))
    data["providers"][0]["status"] = "approved"
    data["providers"][0]["rights"]["storage"] = True
    assert registry.by_id["sec-identity"].status == "pending"
    assert registry.by_id["sec-identity"].rights["storage"] is False


def test_concept_registry_rejects_provider_mapping_and_unknown_kind(tmp_path: Path) -> None:
    data = yaml.safe_load(CONCEPTS.read_text(encoding="utf-8"))
    data["concepts"][0]["provider_mapping"] = "Revenue"
    with pytest.raises(RegistryError, match="unknown fields"):
        load_concept_registry(_write(tmp_path, data, "mapping.yaml"))
    data = yaml.safe_load(CONCEPTS.read_text(encoding="utf-8"))
    data["concepts"][0]["kind"] = "guess"
    with pytest.raises(RegistryError, match="kind"):
        load_concept_registry(_write(tmp_path, data, "kind.yaml"))
