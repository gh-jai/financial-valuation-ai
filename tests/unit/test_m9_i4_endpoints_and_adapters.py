import ast
from pathlib import Path

import pytest

from tools.retail_data.registries import load_provider_registry
from tools.retail_data.sec_adapters import (
    SecCompanyFactsAdapter,
    SecFilingsAdapter,
    SecIdentityAdapter,
    SecSubmissionsAdapter,
)
from tools.retail_data.sec_contracts import build_disabled_policy, provider_registry_subject
from tools.retail_data.sec_endpoints import EndpointError, construct_endpoint, endpoint_specs
from tools.retail_data.sec_fixture_transport import SyntheticFixtureTransport
from tools.retail_data.sec_limiter import ManualClock


ROOT = Path(__file__).resolve().parents[2]
REGISTRY_PATH = ROOT / "registries/m9-provider-license.yaml"
AT = "2026-08-12T00:00:00Z"


def _policy_and_registry():
    _, registry_hash = provider_registry_subject(REGISTRY_PATH)
    return build_disabled_policy(registry_hash), load_provider_registry(REGISTRY_PATH), registry_hash


@pytest.mark.parametrize(
    ("capability", "identifiers", "expected"),
    [
        ("identity", {}, "https://www.sec.gov/files/company_tickers.json"),
        (
            "submissions",
            {"cik": "9000000001"},
            "https://data.sec.gov/submissions/CIK9000000001.json",
        ),
        (
            "filings",
            {
                "cik": "0000000042",
                "accession": "0000000042-26-000001",
                "document": "synthetic-report.txt",
            },
            "https://www.sec.gov/Archives/edgar/data/42/000000004226000001/synthetic-report.txt",
        ),
        (
            "companyfacts",
            {"cik": "9000000003"},
            "https://data.sec.gov/api/xbrl/companyfacts/CIK9000000003.json",
        ),
    ],
)
def test_fixed_endpoint_construction(capability: str, identifiers: dict, expected: str) -> None:
    assert construct_endpoint(capability, identifiers) == expected


@pytest.mark.parametrize(
    "identifiers",
    [
        {"cik": "1"},
        {"cik": "９00000001"},
        {"cik": "9000000001", "url": "https://example.invalid"},
        {"cik": "9000000001", "accession": "9000000001-26-000001", "document": "../x"},
        {"cik": "9000000001", "accession": "9000000001-26-000001", "document": "%2e%2e"},
        {"cik": "9000000001", "accession": "9000000001-26-000001", "document": ".hidden"},
        {"cik": "9000000001", "accession": "bad", "document": "x.txt"},
    ],
)
def test_endpoint_rejects_identifier_and_traversal_surfaces(identifiers: dict) -> None:
    capability = "filings" if "accession" in identifiers else "submissions"
    with pytest.raises(EndpointError):
        construct_endpoint(capability, identifiers)


class _DispatchTrap:
    dispatches = 0

    def dispatch(self, **kwargs):  # pragma: no cover - a call is a test failure
        self.dispatches += 1
        raise AssertionError("disabled adapter reached transport")


@pytest.mark.parametrize(
    ("adapter_type", "identifiers", "provider_id"),
    [
        (SecIdentityAdapter, {}, "sec-identity"),
        (SecSubmissionsAdapter, {"cik": "9000000001"}, "sec-submissions"),
        (
            SecFilingsAdapter,
            {
                "cik": "9000000002",
                "accession": "9000000002-26-000001",
                "document": "synthetic-report.txt",
            },
            "sec-filings",
        ),
        (SecCompanyFactsAdapter, {"cik": "9000000003"}, "sec-xbrl"),
    ],
)
def test_all_public_adapters_stop_before_injected_transport(
    adapter_type, identifiers: dict, provider_id: str
) -> None:
    policy, registry, registry_hash = _policy_and_registry()
    trap = _DispatchTrap()
    adapter = adapter_type(
        policy=policy,
        registry=registry,
        provider_registry_hash=registry_hash,
        transport=trap,
    )
    result = adapter.execute(
        identifiers=identifiers,
        user_agent_policy_valid=True,
        created_at=AT,
    )
    assert result["status"] == "failed"
    assert result["provider_id"] == provider_id
    assert result["errors"][0]["code"] == "SEC-ADAPTER-DISABLED"
    assert result["attempts"] == [] and result["raw_record"] is None
    assert trap.dispatches == 0


def test_missing_user_agent_presence_fails_without_storing_a_value() -> None:
    policy, registry, registry_hash = _policy_and_registry()
    result = SecIdentityAdapter(
        policy=policy,
        registry=registry,
        provider_registry_hash=registry_hash,
    ).execute(identifiers={}, user_agent_policy_valid=False, created_at=AT)
    assert result["errors"][0]["code"] == "SEC-USER-AGENT-DENIED"
    assert result["user_agent_policy_valid"] is False
    serialized = str(result).lower()
    assert "@" not in serialized and "contact=" not in serialized


def test_endpoint_modules_have_no_network_shell_or_dynamic_execution() -> None:
    files = [
        ROOT / "tools/retail_data/sec_endpoints.py",
        ROOT / "tools/retail_data/sec_adapters.py",
        ROOT / "tools/retail_data/sec_fixture_transport.py",
        ROOT / "tools/retail_data/sec_limiter.py",
        ROOT / "tools/retail_data/sec_resilience.py",
        ROOT / "tools/retail_data/sec_cache.py",
    ]
    forbidden = {
        "socket",
        "subprocess",
        "requests",
        "httpx",
        "aiohttp",
        "urllib.request",
        "http.client",
    }
    imports: set[str] = set()
    calls: set[str] = set()
    for path in files:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module)
            elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                calls.add(node.func.id)
    assert not imports.intersection(forbidden)
    assert not calls.intersection({"eval", "exec", "compile", "__import__"})
    assert tuple(item.capability for item in endpoint_specs()) == (
        "identity",
        "submissions",
        "filings",
        "companyfacts",
    )


def test_fixture_transport_constructor_cannot_enable_network() -> None:
    with pytest.raises(ValueError, match="network state"):
        SyntheticFixtureTransport(
            {
                "synthetic": True,
                "network_state": "enabled",
                "capture_provenance": "original_fixture",
                "events": [],
            },
            ManualClock(),
        )
