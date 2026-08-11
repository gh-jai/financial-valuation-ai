"""Write-once content-addressed storage for bounded M9-I3 raw records."""

from __future__ import annotations

import hashlib
import os
import re
import stat
import tempfile
from dataclasses import dataclass
from pathlib import Path


MAX_RECORD_BYTES = 1_048_576
STORE_LAYOUT = "sha256-sharded-v1"
_DIGEST = re.compile(r"^[a-f0-9]{64}$")
_MEDIA_TYPES = frozenset({"application/json", "text/csv"})


class StorageError(ValueError):
    """A stable fail-closed storage error without raw record material."""

    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True, slots=True)
class StoredRecord:
    record_hash: str
    byte_length: int
    media_type: str
    deduplicated: bool


def _checked_directory(path: Path, *, create: bool = False) -> None:
    try:
        if create:
            path.mkdir(mode=0o700)
        metadata = path.lstat()
    except FileExistsError:
        metadata = path.lstat()
    except OSError as exc:
        raise StorageError(
            "STORE-ROOT-INVALID", "configured store directory is unavailable"
        ) from exc
    if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
        raise StorageError("STORE-SYMLINK-DENIED", "store path component must be a real directory")


class ContentAddressedStore:
    """Persist exact bytes under generated SHA-256 paths without replacement."""

    def __init__(self, root: Path, *, max_record_bytes: int = MAX_RECORD_BYTES) -> None:
        if not isinstance(root, Path):
            raise TypeError("store root must be a pathlib.Path")
        if not root.is_absolute():
            raise StorageError("STORE-ROOT-INVALID", "configured store root must be absolute")
        if isinstance(max_record_bytes, bool) or not isinstance(max_record_bytes, int):
            raise TypeError("max_record_bytes must be an integer")
        if max_record_bytes != MAX_RECORD_BYTES:
            raise StorageError("STORE-LIMIT-UNSUPPORTED", "store size limit is contract locked")
        _checked_directory(root)
        self._root = root
        self._records = root / "records"
        self._algorithm = self._records / "sha256"
        _checked_directory(self._records, create=True)
        _checked_directory(self._algorithm, create=True)

    @property
    def root(self) -> Path:
        return self._root

    def _record_path(self, digest: str, *, create_shard: bool) -> Path:
        if not isinstance(digest, str) or not _DIGEST.fullmatch(digest):
            raise StorageError("STORE-DIGEST-INVALID", "record digest is not canonical SHA-256")
        _checked_directory(self._root)
        _checked_directory(self._records)
        _checked_directory(self._algorithm)
        shard = self._algorithm / digest[:2]
        if create_shard:
            _checked_directory(shard, create=True)
        else:
            try:
                metadata = shard.lstat()
            except FileNotFoundError:
                return shard / digest
            except OSError as exc:
                raise StorageError(
                    "STORE-READ-FAILED", "record shard could not be inspected safely"
                ) from exc
            if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
                raise StorageError(
                    "STORE-SYMLINK-DENIED", "record shard must be a real directory"
                )
        return shard / digest

    def put_bytes(self, content: bytes, *, media_type: str) -> StoredRecord:
        if type(content) is not bytes:
            raise TypeError("record content must be bytes")
        if media_type not in _MEDIA_TYPES:
            raise StorageError("STORE-MEDIA-TYPE-DENIED", "record media type is not allowed")
        if not content or len(content) > MAX_RECORD_BYTES:
            raise StorageError("STORE-SIZE-DENIED", "record size is outside the locked limit")
        digest = hashlib.sha256(content).hexdigest()
        target = self._record_path(digest, create_shard=True)
        if target.exists() or target.is_symlink():
            existing = self.read_bytes(digest)
            if existing != content:
                raise StorageError("STORE-TAMPER-DETECTED", "existing record content differs")
            return StoredRecord(digest, len(content), media_type, True)

        descriptor, temporary_name = tempfile.mkstemp(prefix=".pending-", dir=target.parent)
        temporary = Path(temporary_name)
        try:
            with os.fdopen(descriptor, "wb", closefd=True) as stream:
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
            try:
                os.link(temporary, target, follow_symlinks=False)
            except FileExistsError:
                existing = self.read_bytes(digest)
                if existing != content:
                    raise StorageError("STORE-TAMPER-DETECTED", "existing record content differs")
                return StoredRecord(digest, len(content), media_type, True)
            os.chmod(target, 0o400, follow_symlinks=False)
            return StoredRecord(digest, len(content), media_type, False)
        except OSError as exc:
            raise StorageError("STORE-WRITE-FAILED", "record could not be stored safely") from exc
        finally:
            try:
                temporary.unlink()
            except FileNotFoundError:
                pass

    def read_bytes(self, digest: str) -> bytes:
        path = self._record_path(digest, create_shard=False)
        try:
            metadata = path.lstat()
        except OSError as exc:
            raise StorageError("STORE-RECORD-MISSING", "stored record is unavailable") from exc
        if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISREG(metadata.st_mode):
            raise StorageError(
                "STORE-SYMLINK-DENIED", "stored record must be a regular file"
            )
        if metadata.st_size < 1 or metadata.st_size > MAX_RECORD_BYTES:
            raise StorageError(
                "STORE-SIZE-DENIED", "stored record size is outside the locked limit"
            )
        try:
            content = path.read_bytes()
        except OSError as exc:
            raise StorageError(
                "STORE-READ-FAILED", "stored record could not be read safely"
            ) from exc
        if hashlib.sha256(content).hexdigest() != digest:
            raise StorageError(
                "STORE-TAMPER-DETECTED", "stored record digest does not match its path"
            )
        return content
