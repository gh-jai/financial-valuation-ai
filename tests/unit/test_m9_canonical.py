import inspect
import json
import math

import pytest

from tools.retail_data.canonical import (
    CANONICALIZATION_VERSION,
    CanonicalizationError,
    canonical_bytes,
    canonical_json,
    canonical_sha256,
)
from tools.retail_data.independent import (
    IndependentValidationError,
    independent_canonical_json,
    independent_sha256,
)


def test_canonical_json_is_sorted_compact_and_unicode_preserving() -> None:
    value = {"z": [2, 1], "é": "東京", "a": {"b": True}}
    assert canonical_json(value) == '{"a":{"b":true},"z":[2,1],"é":"東京"}'
    assert canonical_bytes(value).decode("utf-8") == canonical_json(value)


def test_hash_changes_after_nested_mutation() -> None:
    value = {"facts": [{"value": 10}]}
    before = canonical_sha256(value)
    value["facts"][0]["value"] = 11
    assert canonical_sha256(value) != before


def test_canonical_json_rejects_non_json_types_and_cycles() -> None:
    for value in [(1, 2), {1: "bad"}, b"bytes"]:
        with pytest.raises(CanonicalizationError):
            canonical_json(value)
    cyclic: list[object] = []
    cyclic.append(cyclic)
    with pytest.raises(CanonicalizationError, match="cyclic"):
        canonical_json(cyclic)


def test_canonical_json_rejects_every_nonfinite_number() -> None:
    for value in (math.nan, math.inf, -math.inf):
        with pytest.raises(CanonicalizationError, match="non-finite"):
            canonical_json({"value": value})
        with pytest.raises(IndependentValidationError, match="non-finite"):
            independent_canonical_json({"value": value})


def test_unknown_canonicalization_versions_fail_closed() -> None:
    assert CANONICALIZATION_VERSION == "fvi-canonical-json-v1"
    with pytest.raises(CanonicalizationError, match="unsupported"):
        canonical_json({}, "future-version")
    with pytest.raises(IndependentValidationError, match="unsupported"):
        independent_canonical_json({}, "future-version")


def test_independent_implementation_matches_vectors_without_production_import() -> None:
    vectors = [None, True, 3, 2.5, "é", [1, {"z": 0}], {"b": 2, "a": 1}]
    for value in vectors:
        assert independent_canonical_json(value) == canonical_json(value)
        assert independent_sha256(value) == canonical_sha256(value)
        json.loads(independent_canonical_json(value))
    source = inspect.getsource(inspect.getmodule(independent_sha256))
    assert "retail_data.canonical" not in source
