import ast

from tools.retail_data.gaap_contracts import attach_self_hash, load_synthetic_fixture
from tools.retail_data.normalization import normalize_fixture
from tools.validate_m9_i5_normalization import IMPLEMENTATION_FILES, ROOT, validate_bundle

FIXTURE = ROOT / "benchmarks/fixtures/m9_i5/synthetic-gaap-golden.json"


def _subjects() -> tuple[dict, dict]:
    fixture = load_synthetic_fixture(FIXTURE)
    return fixture, normalize_fixture(fixture)


def test_independent_validator_passes_exact_golden_bundle() -> None:
    fixture, bundle = _subjects()
    validation = validate_bundle(fixture, bundle)
    assert validation["passed"] is True
    assert validation["findings"] == []
    assert validation["implementation_separation"] == "independent"
    assert validation["network_state"] == "denied"


def test_coordinated_rehash_cannot_legitimize_changed_normalized_arithmetic() -> None:
    fixture, bundle = _subjects()
    result = bundle["normalization_result"]
    result["facts"][0]["value_decimal"] = "999"
    bundle["normalization_result"] = attach_self_hash(result, "normalization_hash")
    validation = validate_bundle(fixture, bundle)
    assert validation["passed"] is False
    assert "NORM-UNIT-SCALE" in {finding["code"] for finding in validation["findings"]}


def test_coordinated_rehash_cannot_hide_missing_concept_with_complete_quality() -> None:
    fixture, bundle = _subjects()
    result = bundle["normalization_result"]
    result["facts"] = [fact for fact in result["facts"] if fact["concept_id"] != "operating-income"]
    bundle["normalization_result"] = attach_self_hash(result, "normalization_hash")
    validation = validate_bundle(fixture, bundle)
    assert validation["passed"] is False
    assert "NORM-RECONCILIATION-FAILED" in {finding["code"] for finding in validation["findings"]}


def test_coordinated_rehash_cannot_remove_a_reconciliation_family() -> None:
    fixture, bundle = _subjects()
    result = bundle["normalization_result"]
    result["reconciliations"] = result["reconciliations"][:-1]
    result["quality"]["status"] = "needs_review"
    bundle["normalization_result"] = attach_self_hash(result, "normalization_hash")
    validation = validate_bundle(fixture, bundle)
    assert validation["passed"] is False
    assert "NORM-RECONCILIATION-FAILED" in {finding["code"] for finding in validation["findings"]}


def test_result_reference_hash_mutation_is_detected() -> None:
    fixture, bundle = _subjects()
    bundle["normalization_result"]["mapping_hash"] = "0" * 64
    bundle["normalization_result"] = attach_self_hash(
        bundle["normalization_result"], "normalization_hash"
    )
    validation = validate_bundle(fixture, bundle)
    assert validation["passed"] is False
    assert "NORM-HASH-MISMATCH" in {finding["code"] for finding in validation["findings"]}


def test_coordinated_rehash_cannot_expand_tolerance_to_turn_failure_into_pass() -> None:
    fixture, bundle = _subjects()
    result = bundle["normalization_result"]
    check = next(item for item in result["reconciliations"] if item["check_type"] == "unit-scale")
    check["difference_decimal"] = "1"
    check["tolerance_decimal"] = "2"
    check["status"] = "failed"
    result["quality"]["status"] = "unsupported"
    result["quality"]["blocking_codes"] = ["NORM-RECONCILIATION-FAILED"]
    bundle["normalization_result"] = attach_self_hash(result, "normalization_hash")
    validation = validate_bundle(fixture, bundle)
    assert validation["passed"] is False
    assert "NORM-RECONCILIATION-FAILED" in {finding["code"] for finding in validation["findings"]}


def test_coordinated_rehash_cannot_add_incompatible_duplicate_source_reference() -> None:
    fixture, bundle = _subjects()
    result = bundle["normalization_result"]
    revenue = next(fact for fact in result["facts"] if fact["concept_id"] == "revenue")
    revenue["source_fact_refs"].append("RAW-SYNTHETIC-OPERATING-INCOME")
    revenue["source_fact_refs"].sort()
    revenue["fact_id"] = "FACT-000000000000000000000000"
    bundle["normalization_result"] = attach_self_hash(result, "normalization_hash")
    validation = validate_bundle(fixture, bundle)
    assert validation["passed"] is False
    assert {"NORM-CONCEPT-UNMAPPED", "NORM-UNIT-SCALE"} & {
        finding["code"] for finding in validation["findings"]
    }


def test_deterministic_identifier_mutation_fails_after_coordinated_rehash() -> None:
    fixture, bundle = _subjects()
    bundle["mapping"]["mapping_id"] = "MAP-000000000000000000000000"
    bundle["mapping"] = attach_self_hash(bundle["mapping"], "mapping_hash")
    validation = validate_bundle(fixture, bundle)
    assert validation["passed"] is False
    assert "NORM-HASH-MISMATCH" in {finding["code"] for finding in validation["findings"]}


def test_coordinated_rehash_cannot_replace_locked_standard_tag_authority() -> None:
    fixture, bundle = _subjects()
    bundle["mapping"]["mappings"][0]["source_tags"]["01"]["local_name"] = "AlternateRevenue"
    bundle["mapping"] = attach_self_hash(bundle["mapping"], "mapping_hash")
    validation = validate_bundle(fixture, bundle)
    assert validation["passed"] is False
    assert "NORM-CONCEPT-UNMAPPED" in {finding["code"] for finding in validation["findings"]}


def test_unconsumed_source_fact_requires_an_explicit_disposition() -> None:
    fixture, bundle = _subjects()
    extra = dict(fixture["facts"][0])
    extra["source_fact_id"] = "RAW-SYNTHETIC-UNDISPOSED"
    extra = attach_self_hash(extra, "source_fact_hash")
    fixture["facts"].append(extra)
    fixture = attach_self_hash(fixture, "fixture_hash")
    bundle["fixture_hash"] = fixture["fixture_hash"]
    validation = validate_bundle(fixture, bundle)
    assert validation["passed"] is False
    assert "NORM-REFERENCE-MISSING" in {finding["code"] for finding in validation["findings"]}


def test_runtime_import_graph_has_no_network_provider_shell_or_dynamic_execution() -> None:
    package = ROOT / "tools/retail_data"
    forbidden = {
        "aiohttp",
        "httpx",
        "requests",
        "socket",
        "subprocess",
        "urllib",
        "sec_adapters",
    }
    for filename in IMPLEMENTATION_FILES:
        tree = ast.parse((package / filename).read_text(encoding="utf-8"))
        imports = {
            alias.name.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        imports.update(
            (node.module or "").split(".")[-1]
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom)
        )
        assert not imports & forbidden
        assert not any(
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id in {"eval", "exec", "compile", "__import__"}
            for node in ast.walk(tree)
        )
        assert not any(
            isinstance(node, ast.Constant) and isinstance(node.value, float)
            for node in ast.walk(tree)
        )


def test_validator_does_not_import_production_normalization_helpers() -> None:
    path = ROOT / "tools/validate_m9_i5_normalization.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports = {(node.module or "") for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
    assert not any(name.startswith(("tools.retail_data", "retail_data")) for name in imports)
