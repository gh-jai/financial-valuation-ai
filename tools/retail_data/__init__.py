"""Offline, default-deny primitives for the M9 retail-data boundary."""

from .canonical import CANONICALIZATION_VERSION, canonical_json, canonical_sha256
from .errors import ErrorSeverity, NextAction, RetailDataError
from .independent import independent_canonical_json, independent_sha256
from .identity_contracts import (
    IdentityContractError,
    load_identity_catalog,
    load_identity_policy,
    load_scope_registry,
)
from .registries import (
    ConceptRegistry,
    ProviderRegistry,
    load_concept_registry,
    load_provider_registry,
)
from .resolution import (
    ResolutionStop,
    create_selection,
    load_synthetic_catalog,
    normalize_query,
    resolve_issuer,
    verify_selected_identity,
)
from .structural_scope import evaluate_structural_scope
from .manual_import import ManualImportError, import_manual_bytes
from .snapshots import SnapshotError, build_manual_snapshot
from .storage import ContentAddressedStore, StorageError, StoredRecord

__all__ = [
    "CANONICALIZATION_VERSION",
    "ConceptRegistry",
    "ErrorSeverity",
    "IdentityContractError",
    "NextAction",
    "ManualImportError",
    "ProviderRegistry",
    "RetailDataError",
    "ResolutionStop",
    "SnapshotError",
    "StorageError",
    "StoredRecord",
    "ContentAddressedStore",
    "build_manual_snapshot",
    "canonical_json",
    "canonical_sha256",
    "create_selection",
    "evaluate_structural_scope",
    "independent_canonical_json",
    "independent_sha256",
    "import_manual_bytes",
    "load_concept_registry",
    "load_identity_catalog",
    "load_identity_policy",
    "load_provider_registry",
    "load_scope_registry",
    "load_synthetic_catalog",
    "normalize_query",
    "resolve_issuer",
    "verify_selected_identity",
]
