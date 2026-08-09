import ast
from datetime import date
from pathlib import Path

import yaml

from tools.retail_data import canonical_sha256, independent_sha256
from tools.retail_data.registries import load_concept_registry, load_provider_registry


ROOT = Path(__file__).resolve().parents[2]
PACKAGE = ROOT / "tools/retail_data"
REVIEW = ROOT / "docs/milestones/M9-I1-implementation-review.md"


def test_i1_package_has_no_transport_or_provider_sdk_imports() -> None:
    forbidden = {"httpx", "requests", "socket", "urllib.request", "aiohttp", "boto3"}
    imports: set[str] = set()
    for path in PACKAGE.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module)
    assert not any(name in forbidden for name in imports)


def test_registry_artifacts_resolve_and_remain_disabled() -> None:
    providers = load_provider_registry(ROOT / "registries/m9-provider-license.yaml")
    concepts = load_concept_registry(ROOT / "registries/m9-concepts.yaml")
    assert providers.registry_id == "m9-provider-license"
    assert concepts.registry_id == "m9-concepts"
    for provider in providers.records:
        assert not providers.authorize(
            provider.provider_id,
            category=provider.data_categories[0],
            right="storage",
            territory="US",
            as_of=date(2026, 8, 8),
        ).allowed


def test_hash_cross_implementation_for_registry_metadata() -> None:
    for name in ("m9-provider-license.yaml", "m9-concepts.yaml"):
        value = yaml.safe_load((ROOT / "registries" / name).read_text(encoding="utf-8"))
        assert canonical_sha256(value) == independent_sha256(value)


def test_registry_files_contain_no_payload_or_credentials() -> None:
    combined = "\n".join(
        path.read_text(encoding="utf-8") for path in (ROOT / "registries").glob("m9-*.yaml")
    ).lower()
    for prohibited in ("authorization:", "bearer ", "api_key:", "provider_payload"):
        assert prohibited not in combined


def test_review_record_binds_approved_baseline_and_separate_publication() -> None:
    text = REVIEW.read_text(encoding="utf-8")
    assert "Status: Implementation baseline approved; publication authorized" in text
    assert "[x] Human implementation review complete" in text
    assert "[x] Stage, commit, push, and Draft PR authorized" in text
    assert "does not authorize `M9-I2`" in text


def test_i1_package_exports_only_offline_primitives() -> None:
    import tools.retail_data as package

    assert "canonical_sha256" in package.__all__
    assert "load_provider_registry" in package.__all__
    assert all("adapter" not in name and "transport" not in name for name in package.__all__)
