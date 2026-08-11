import os
from pathlib import Path

import pytest

from tools.retail_data.storage import MAX_RECORD_BYTES, ContentAddressedStore, StorageError


def _store(tmp_path: Path) -> ContentAddressedStore:
    root = tmp_path / "store"
    root.mkdir(parents=True)
    return ContentAddressedStore(root)


def _record_path(store: ContentAddressedStore, digest: str) -> Path:
    return store.root / "records" / "sha256" / digest[:2] / digest


def test_store_is_write_once_and_deduplicates_exact_bytes(tmp_path: Path) -> None:
    store = _store(tmp_path)
    first = store.put_bytes(b'{"value":1}', media_type="application/json")
    second = store.put_bytes(b'{"value":1}', media_type="application/json")
    assert not first.deduplicated and second.deduplicated
    assert first.record_hash == second.record_hash
    assert store.read_bytes(first.record_hash) == b'{"value":1}'
    assert _record_path(store, first.record_hash).stat().st_mode & 0o222 == 0


def test_store_rejects_invalid_digest_media_type_and_size(tmp_path: Path) -> None:
    store = _store(tmp_path)
    for digest in ("../escape", "A" * 64, "0" * 63):
        with pytest.raises(StorageError, match="digest"):
            store.read_bytes(digest)
    with pytest.raises(StorageError) as caught:
        store.read_bytes("0" * 64)
    assert caught.value.code == "STORE-RECORD-MISSING"
    with pytest.raises(StorageError, match="media type"):
        store.put_bytes(b"value", media_type="application/zip")
    for value in (b"", b"x" * (MAX_RECORD_BYTES + 1)):
        with pytest.raises(StorageError, match="size"):
            store.put_bytes(value, media_type="text/csv")
    with pytest.raises(TypeError):
        store.put_bytes(bytearray(b"value"), media_type="text/csv")  # type: ignore[arg-type]


def test_store_detects_changed_content_under_existing_digest(tmp_path: Path) -> None:
    store = _store(tmp_path)
    stored = store.put_bytes(b'{"value":1}', media_type="application/json")
    path = _record_path(store, stored.record_hash)
    path.chmod(0o600)
    path.write_bytes(b'{"value":2}')
    with pytest.raises(StorageError, match="digest") as caught:
        store.read_bytes(stored.record_hash)
    assert caught.value.code == "STORE-TAMPER-DETECTED"


@pytest.mark.skipif(not hasattr(os, "symlink"), reason="symlink support required")
def test_store_rejects_symlinked_root_component_and_record(tmp_path: Path) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    linked_root = tmp_path / "linked-root"
    linked_root.symlink_to(outside, target_is_directory=True)
    with pytest.raises(StorageError) as caught:
        ContentAddressedStore(linked_root)
    assert caught.value.code == "STORE-SYMLINK-DENIED"

    root = tmp_path / "store"
    root.mkdir()
    (root / "records").symlink_to(outside, target_is_directory=True)
    with pytest.raises(StorageError) as caught:
        ContentAddressedStore(root)
    assert caught.value.code == "STORE-SYMLINK-DENIED"

    safe = _store(tmp_path / "safe")
    stored = safe.put_bytes(b'{"value":1}', media_type="application/json")
    path = _record_path(safe, stored.record_hash)
    path.unlink()
    path.symlink_to(outside / "missing")
    with pytest.raises(StorageError) as caught:
        safe.read_bytes(stored.record_hash)
    assert caught.value.code == "STORE-SYMLINK-DENIED"


def test_store_rejects_relative_or_changed_size_configuration(tmp_path: Path) -> None:
    with pytest.raises(StorageError, match="absolute"):
        ContentAddressedStore(Path("relative"))
    root = tmp_path / "store"
    root.mkdir()
    with pytest.raises(StorageError) as caught:
        ContentAddressedStore(root, max_record_bytes=10)
    assert caught.value.code == "STORE-LIMIT-UNSUPPORTED"
