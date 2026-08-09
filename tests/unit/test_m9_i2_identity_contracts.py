import copy
from datetime import datetime, timezone
from pathlib import Path

import pytest

from tools.retail_data.identity_contracts import (
    IdentityContractError,
    attach_hash,
    strict_load,
    validate_identity_catalog,
    validate_identity_policy,
    validate_schema,
    validate_scope_registry,
)
from tools.retail_data.resolution import ResolutionStop, load_synthetic_catalog


ROOT = Path(__file__).resolve().parents[2]
AT = datetime(2026, 8, 9, tzinfo=timezone.utc)
CATALOG = ROOT / "benchmarks/fixtures/m9_i2/synthetic-identity-catalog.yaml"
POLICY = ROOT / "registries/m9-identity-resolution-policy.yaml"
SCOPE = ROOT / "registries/m9-issuer-structural-scope.yaml"


def test_committed_governed_artifacts_are_strict_hash_closed_and_offline() -> None:
    catalog = strict_load(CATALOG)
    policy = strict_load(POLICY)
    scope = strict_load(SCOPE)
    validate_identity_catalog(catalog, AT)
    validate_identity_policy(policy, AT)
    validate_scope_registry(scope, AT)
    assert catalog["network_state"] == policy["network_state"] == "denied"


def test_nested_catalog_mutation_and_unknown_fields_fail_closed() -> None:
    catalog = strict_load(CATALOG)
    catalog["records"][0]["legal_name"] = "Mutated Synthetic Name"
    with pytest.raises(IdentityContractError, match="catalog_hash|catalog_record_hash"):
        validate_identity_catalog(catalog, AT)
    policy = strict_load(POLICY)
    policy["unexpected"] = True
    with pytest.raises(IdentityContractError, match="unexpected"):
        validate_identity_policy(policy, AT)


def test_duplicate_yaml_keys_are_rejected_before_schema_validation(tmp_path: Path) -> None:
    path = tmp_path / "duplicate.yaml"
    path.write_text("schema_version: 0.1.0\nschema_version: 0.1.0\n", encoding="utf-8")
    with pytest.raises(IdentityContractError, match="duplicate mapping key"):
        strict_load(path)


def test_all_eight_m9_i2_schemas_reject_unknown_fields() -> None:
    valid = {
        "candidate_set": strict_load(CATALOG),
        "selection": strict_load(POLICY),
        "verified_identity": strict_load(SCOPE),
    }
    for kind, wrong_shape in valid.items():
        value = copy.deepcopy(wrong_shape)
        value["unexpected"] = True
        with pytest.raises(IdentityContractError):
            validate_schema(value, kind)


def test_fixture_adapter_rejects_paths_unknown_ids_and_environment_shape() -> None:
    assert load_synthetic_catalog("m9-i2-synthetic-catalog", AT)["catalog_id"] == (
        "m9-i2-synthetic-catalog"
    )
    for value in ("../synthetic-identity-catalog", "/tmp/catalog", "unknown", "archive.zip"):
        with pytest.raises(ResolutionStop) as stopped:
            load_synthetic_catalog(value, AT)
        assert stopped.value.error.code == "IDENTITY-CATALOG-DENIED"


def test_policy_rejects_schema_valid_rehashed_rank_semantic_drift() -> None:
    policy = strict_load(POLICY)
    policy["match_ranks"][1]["precedence"] = 2
    policy["match_ranks"][2]["precedence"] = 1
    policy["match_ranks"].sort(
        key=lambda item: (item["rank"], item["precedence"], item["match_kind"])
    )
    mutated = attach_hash(
        {key: value for key, value in policy.items() if key != "identity_policy_hash"},
        "identity_policy_hash",
    )
    with pytest.raises(IdentityContractError, match="rank and precedence table"):
        validate_identity_policy(mutated, AT)


def test_scope_registry_rejects_rehashed_contradictory_rule_semantics() -> None:
    registry = strict_load(SCOPE)
    registry["rules"][8]["outcome"] = "eligible_for_data_review"
    mutated = attach_hash(
        {key: value for key, value in registry.items() if key != "scope_registry_hash"},
        "scope_registry_hash",
    )
    with pytest.raises(IdentityContractError, match="contract-locked or are contradictory"):
        validate_scope_registry(mutated, AT)


def test_scope_registry_rejects_rehashed_deferred_row_substitution() -> None:
    registry = strict_load(SCOPE)
    registry["deferred_matrix_rows"][0]["row_id"] = "M8-LIFECYCLE-FICTIONAL"
    registry["deferred_matrix_rows"].sort(key=lambda item: item["row_id"])
    mutated = attach_hash(
        {key: value for key, value in registry.items() if key != "scope_registry_hash"},
        "scope_registry_hash",
    )
    with pytest.raises(IdentityContractError, match="deferred M8 rows"):
        validate_scope_registry(mutated, AT)
