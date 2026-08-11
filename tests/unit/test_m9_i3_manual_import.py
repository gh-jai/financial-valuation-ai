import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker

from tools.retail_data.manual_import import ManualImportError, import_manual_bytes
from tools.retail_data.storage import MAX_RECORD_BYTES, ContentAddressedStore


AT = "2026-08-11T00:00:00Z"
ROOT = Path(__file__).resolve().parents[2]


def _store(tmp_path: Path) -> ContentAddressedStore:
    root = tmp_path / "store"
    root.mkdir()
    return ContentAddressedStore(root)


def _stored_files(store: ContentAddressedStore) -> list[Path]:
    return [path for path in store.root.rglob("*") if path.is_file()]


def _validate(result: dict) -> None:
    schema = json.loads((ROOT / "schemas/manual-import-result.schema.json").read_text())
    errors = list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(result))
    assert not errors


def test_json_import_preserves_exact_bytes_and_is_deterministic(tmp_path: Path) -> None:
    store = _store(tmp_path)
    raw = b'[{"period":"2025","revenue":100},{"period":"2024","revenue":90}]\n'
    first = import_manual_bytes(
        store, raw, media_type="application/json", source_label="synthetic-json", created_at=AT
    )
    second = import_manual_bytes(
        store, raw, media_type="application/json", source_label="synthetic-json", created_at=AT
    )
    assert first == second
    assert first["record_count"] == 2 and first["columns"] == []
    assert store.read_bytes(first["record_hash"]) == raw
    assert len(_stored_files(store)) == 1
    _validate(first)


@pytest.mark.parametrize(
    ("raw", "code"),
    [
        (b'{"a":1,"a":2}', "IMPORT-JSON-DUPLICATE-KEY"),
        (b'{"value":NaN}', "IMPORT-JSON-NONFINITE"),
        ((b'{"value":' + b"9" * 129 + b"}"), "IMPORT-JSON-NUMBER-LIMIT"),
        (b'{"value":1e999}', "IMPORT-JSON-NONFINITE"),
        (b'[]', "IMPORT-JSON-SHAPE-DENIED"),
        (b'[1,2]', "IMPORT-JSON-SHAPE-DENIED"),
        (b'{broken', "IMPORT-JSON-MALFORMED"),
    ],
)
def test_invalid_json_is_rejected_before_store_write(tmp_path: Path, raw: bytes, code: str) -> None:
    store = _store(tmp_path)
    with pytest.raises(ManualImportError) as caught:
        import_manual_bytes(
            store, raw, media_type="application/json", source_label="synthetic", created_at=AT
        )
    assert caught.value.code == code
    assert _stored_files(store) == []


def test_csv_import_preserves_columns_rows_and_negative_numbers(tmp_path: Path) -> None:
    store = _store(tmp_path)
    raw = b"concept,value\nrevenue,100\ncapex,-12.5\n"
    result = import_manual_bytes(
        store, raw, media_type="text/csv", source_label="synthetic-csv", created_at=AT
    )
    assert result["columns"] == ["concept", "value"]
    assert result["record_count"] == 2
    assert store.read_bytes(result["record_hash"]) == raw
    _validate(result)


@pytest.mark.parametrize(
    "cell", ["=1+1", "+SUM(A1)", "@cmd", "-cmd|calc", "  =hidden", "\n=hidden"]
)
def test_csv_formula_vectors_are_rejected_before_write(tmp_path: Path, cell: str) -> None:
    store = _store(tmp_path)
    raw = f'concept,value\nrevenue,"{cell}"\n'.encode()
    with pytest.raises(ManualImportError) as caught:
        import_manual_bytes(
            store, raw, media_type="text/csv", source_label="synthetic", created_at=AT
        )
    assert caught.value.code == "IMPORT-CSV-FORMULA-DENIED"
    assert _stored_files(store) == []


@pytest.mark.parametrize(
    ("raw", "code"),
    [
        (b"a,a\n1,2\n", "IMPORT-CSV-HEADER-INVALID"),
        (b"a,b\n1\n", "IMPORT-CSV-WIDTH-INVALID"),
        (b"a,b\n", "IMPORT-CSV-EMPTY"),
        (b" a,b\n1,2\n", "IMPORT-CSV-HEADER-INVALID"),
    ],
)
def test_csv_structure_is_strict(tmp_path: Path, raw: bytes, code: str) -> None:
    store = _store(tmp_path)
    with pytest.raises(ManualImportError) as caught:
        import_manual_bytes(
            store, raw, media_type="text/csv", source_label="synthetic", created_at=AT
        )
    assert caught.value.code == code
    assert _stored_files(store) == []


@pytest.mark.parametrize(
    ("raw", "media_type", "code"),
    [
        (b"\xef\xbb\xbf{}", "application/json", "IMPORT-ENCODING-DENIED"),
        (b"\xff", "application/json", "IMPORT-ENCODING-DENIED"),
        (b"{}\x00", "application/json", "IMPORT-ENCODING-DENIED"),
        (b"PK\x03\x04payload", "application/json", "IMPORT-ARCHIVE-DENIED"),
        (b"%PDF-payload", "application/json", "IMPORT-ARCHIVE-DENIED"),
        (b"{}", "application/zip", "IMPORT-MEDIA-TYPE-DENIED"),
    ],
)
def test_encoding_archive_and_media_boundaries_fail_closed(
    tmp_path: Path, raw: bytes, media_type: str, code: str
) -> None:
    store = _store(tmp_path)
    with pytest.raises(ManualImportError) as caught:
        import_manual_bytes(
            store, raw, media_type=media_type, source_label="synthetic", created_at=AT
        )
    assert caught.value.code == code
    assert _stored_files(store) == []


def test_import_rejects_oversize_input_and_unsafe_metadata(tmp_path: Path) -> None:
    store = _store(tmp_path)
    with pytest.raises(ManualImportError) as caught:
        import_manual_bytes(
            store,
            b"x" * (MAX_RECORD_BYTES + 1),
            media_type="text/csv",
            source_label="synthetic",
            created_at=AT,
        )
    assert caught.value.code == "IMPORT-SIZE-DENIED"
    for label in ("", " leading", "line\nbreak", "x" * 129):
        with pytest.raises(ManualImportError):
            import_manual_bytes(
                store, b"a\n1\n", media_type="text/csv", source_label=label, created_at=AT
            )
    with pytest.raises(ManualImportError, match="created_at"):
        import_manual_bytes(
            store,
            b"a\n1\n",
            media_type="text/csv",
            source_label="synthetic",
            created_at="2026-08-11T00:00:00+00:00",
        )
    assert _stored_files(store) == []
