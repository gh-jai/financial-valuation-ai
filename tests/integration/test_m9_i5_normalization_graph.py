import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from tools.retail_data.canonical import canonical_json
from tools.retail_data.gaap_contracts import load_synthetic_fixture
from tools.retail_data.normalization import normalize_fixture
from tools.validate_m9_i5_normalization import strict_json, validate_bundle

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "benchmarks/fixtures/m9_i5/synthetic-gaap-golden.json"


def _schema(name: str) -> dict:
    return json.loads((ROOT / "schemas" / name).read_text(encoding="utf-8"))


def test_exact_fixture_to_normalization_to_independent_validation_graph(tmp_path: Path) -> None:
    fixture = load_synthetic_fixture(FIXTURE)
    bundle = normalize_fixture(fixture)
    subjects = (
        ("m9-i5-concept-mapping-policy.schema.json", bundle["mapping"]),
        ("m9-i5-period-graph.schema.json", bundle["period_graph"]),
        ("m9-i5-normalization-result.schema.json", bundle["normalization_result"]),
    )
    for schema_name, subject in subjects:
        validator = Draft202012Validator(_schema(schema_name), format_checker=FormatChecker())
        assert list(validator.iter_errors(subject)) == []

    bundle_path = tmp_path / "exact-bundle.json"
    bundle_path.write_text(canonical_json(bundle) + "\n", encoding="utf-8")
    reloaded = strict_json(bundle_path)
    validation = validate_bundle(fixture, reloaded)
    validator = Draft202012Validator(
        _schema("m9-i5-normalization-validation-result.schema.json"),
        format_checker=FormatChecker(),
    )
    assert list(validator.iter_errors(validation)) == []
    assert validation["passed"] is True


def test_fixture_contains_no_live_provider_or_real_company_surface() -> None:
    text = FIXTURE.read_text(encoding="utf-8")
    for prohibited in (
        "https://",
        "http://",
        "www.sec.gov",
        "data.sec.gov",
        "provider_response",
        "ticker",
        "credential",
        "authorization",
    ):
        assert prohibited not in text.lower()
    fixture = load_synthetic_fixture(FIXTURE)
    assert fixture["source_snapshot"]["company_cik"] == "0000000001"
    assert fixture["source_snapshot"]["synthetic_only"] is True
