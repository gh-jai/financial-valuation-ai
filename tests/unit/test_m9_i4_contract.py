import json
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "docs/milestones/M9-I4-disabled-sec-adapters-contract-lock.md"
CHECKLIST = ROOT / "templates/m9-i4-disabled-sec-adapters-contract-review-checklist.md"
SCHEMAS = (
    ROOT / "schemas/sec-adapter-policy.schema.json",
    ROOT / "schemas/sec-adapter-result.schema.json",
    ROOT / "schemas/sec-synthetic-transport-fixture.schema.json",
    ROOT / "schemas/sec-adapter-validation-result.schema.json",
)
PROVIDER_REGISTRY = ROOT / "registries/m9-provider-license.yaml"


def _contract() -> str:
    return CONTRACT.read_text(encoding="utf-8")


def test_m9_i4_contract_is_design_only_and_network_denied() -> None:
    text = _contract()
    normalized = " ".join(text.split())
    for requirement in (
        "LOCAL_CONTRACT_CANDIDATE_REVIEW_PENDING",
        "Canonical baseline: `main` at `cd804db1126a45d8082f081f086b463d382566ba`",
        "Network state: `DENIED`",
        "This document is a contract candidate, not an adapter implementation",
        "does not authorize staging, committing, pushing, a pull request",
        "live transport unreachable",
        "No stage, commit, push, Draft PR",
    ):
        assert requirement in normalized


def test_m9_i4_contract_separates_all_four_capabilities_and_fixed_endpoints() -> None:
    text = _contract()
    for expected in (
        "`identity` | `sec-identity` | `sec-company-tickers-v1`",
        "`submissions` | `sec-submissions` | `sec-submissions-by-cik-v1`",
        "`filings` | `sec-filings` | `sec-filing-document-v1`",
        "`companyfacts` | `sec-xbrl` | `sec-companyfacts-by-cik-v1`",
        "https://www.sec.gov/files/company_tickers.json",
        "https://data.sec.gov/submissions/CIK{cik}.json",
        "https://www.sec.gov/Archives/edgar/data/{cik}/{accession_compact}/{document}",
        "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json",
    ):
        assert expected in text
    assert "Permission for one capability\nnever grants another" in text


def test_m9_i4_contract_locks_network_resilience_and_resource_limits() -> None:
    normalized = " ".join(_contract().split())
    for requirement in (
        "Redirect policy is `deny_all`",
        "operator_configured_not_stored",
        "One process-wide limiter covers all four SEC capabilities",
        "Maximum requests per window | 1",
        "Burst capacity | 1",
        "Queue bound | 32",
        "`max_attempts` is 3 total attempts",
        "exactly 1 and 2 seconds",
        "Connect timeout is 5 seconds",
        "read-idle timeout is 20 seconds",
        "total request deadline is 30 seconds",
        "five consecutive countable failures open the circuit for 60 seconds",
        "identity | 8,388,608 bytes",
        "companyfacts | 33,554,432 bytes",
    ):
        assert requirement in normalized


def test_m9_i4_contract_preserves_write_once_cache_and_independent_validation() -> None:
    normalized = " ".join(_contract().split())
    for requirement in (
        "M9-I3 content-addressed write-once store",
        "no stale or network fallback is allowed",
        "Fixtures are compact, original, and conspicuously synthetic",
        "must not import production adapter, endpoint, limiter, retry, timeout, breaker, cache",
        "replay the synthetic event script with its own limiter, retry, timeout, breaker",
        "coordinated mutation",
    ):
        assert requirement in normalized


def test_m9_i4_contract_excludes_live_real_private_and_later_scope() -> None:
    text = _contract()
    for excluded in (
        "No adapter, network transport, DNS, socket, HTTP client",
        "No provider activation, credential, actual User-Agent",
        "No real company, ticker, filing, accession, XBRL fact, provider response",
        "PDF",
        "private extract",
        "`project_sources/` use",
        "M9-I5/M9-I6",
        "valuation",
        "LLM",
        "UI",
    ):
        assert excluded in text


def test_m9_i4_schemas_are_strict_valid_draft_2020_12_contracts() -> None:
    assert len(SCHEMAS) == 4
    for path in SCHEMAS:
        schema = json.loads(path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
        assert schema["additionalProperties"] is False


def test_policy_schema_locks_disabled_state_and_numeric_controls() -> None:
    schema = json.loads(SCHEMAS[0].read_text(encoding="utf-8"))
    properties = schema["properties"]
    assert properties["activation_state"] == {"const": "disabled"}
    assert properties["network_state"] == {"const": "denied"}
    assert properties["global_kill_switch"] == {"const": "disabled"}
    assert properties["header_policy"]["properties"]["store_user_agent_value"] == {"const": False}
    assert properties["global_rate_limit"]["properties"]["max_requests"] == {"const": 1}
    assert properties["global_rate_limit"]["properties"]["burst_capacity"] == {"const": 1}
    assert properties["retry_policy"]["properties"]["max_attempts"] == {"const": 3}
    assert properties["retry_policy"]["properties"]["backoff_seconds"] == {"const": [1, 2]}
    assert properties["timeout_policy"]["properties"]["total_seconds"] == {"const": 30}
    assert properties["circuit_breaker"]["properties"]["failure_threshold"] == {"const": 5}
    assert properties["circuit_breaker"]["properties"]["open_seconds"] == {"const": 60}
    capability_rules = schema["$defs"]["capability"]["allOf"]
    assert len(capability_rules) == 4
    mappings = {
        rule["if"]["properties"]["capability"]["const"]: (
            rule["then"]["properties"]["provider_id"]["const"],
            rule["then"]["properties"]["endpoint_id"]["const"],
        )
        for rule in capability_rules
    }
    assert mappings == {
        "identity": ("sec-identity", "sec-company-tickers-v1"),
        "submissions": ("sec-submissions", "sec-submissions-by-cik-v1"),
        "filings": ("sec-filings", "sec-filing-document-v1"),
        "companyfacts": ("sec-xbrl", "sec-companyfacts-by-cik-v1"),
    }


def test_result_fixture_and_validation_schemas_preserve_offline_boundary() -> None:
    result = json.loads(SCHEMAS[1].read_text(encoding="utf-8"))
    fixture = json.loads(SCHEMAS[2].read_text(encoding="utf-8"))
    validation = json.loads(SCHEMAS[3].read_text(encoding="utf-8"))
    assert result["properties"]["activation_state"] == {"const": "disabled"}
    assert result["properties"]["network_state"] == {"const": "denied"}
    assert fixture["properties"]["synthetic"] == {"const": True}
    assert fixture["properties"]["network_state"] == {"const": "denied"}
    assert fixture["properties"]["capture_provenance"] == {"const": "original_fixture"}
    assert "url" not in fixture["properties"]
    assert validation["properties"]["implementation_separation"] == {"const": "independent"}
    assert validation["properties"]["network_state"] == {"const": "denied"}
    assert len(result["allOf"]) == 6
    assert len(fixture["allOf"]) == 4


def test_review_checklist_has_no_preselected_verdict() -> None:
    text = CHECKLIST.read_text(encoding="utf-8")
    assert text.count("- [ ]") >= 25
    assert "`[ ] PASS  [ ] COMMENTED_BLOCKING  [ ] request changes`" in text
    assert "No box is preselected" in text


def test_existing_provider_registry_remains_default_deny_contract_input() -> None:
    text = PROVIDER_REGISTRY.read_text(encoding="utf-8")
    assert text.count("status: pending") == 4
    assert text.count("live_activation: disabled") == 4
    for right in ("storage", "display", "export", "redistribution"):
        assert text.count(f"{right}: false") == 4
