# M9-I3 Immutable Snapshot Store and Manual Import Contract

Status: `IMPLEMENTATION_AUTHORIZED_LOCAL_CANDIDATE`
Contract version: `0.1.0`
Implementation authorization: Project owner, 2026-08-11
Implementation base: `3ea93c8751bfaa558d3597a91b978f986dac6412`
Network state: `DENIED`
Data boundary: compact synthetic UTF-8 JSON and CSV fixtures only

## Decision

M9-I3 implements the offline storage boundary between the verified M9-I2 issuer decision and the
later M9-I5 normalization slice. It accepts caller-supplied bytes, validates a narrowly bounded
manual JSON or CSV representation, stores the exact bytes once under their SHA-256 digest, builds
an M8 `source-snapshot` plus a reference-closing M9-I3 manifest, and independently validates the
result.

It does not collect a browser upload, open a caller-selected path, retrieve a URL, select an issuer,
create a license approval, normalize a financial fact, value a company, or expose an API, CLI, LLM,
or UI capability.

```text
verified M9-I2 identity + eligible structural-scope decision
-> bounded local JSON/CSV bytes
-> parse and hostile-input checks
-> content-addressed write-once record
-> M8 source-snapshot
-> exact-reference M9-I3 manifest
-> implementation-separated validation
```

## Locked limits

| Limit | Value |
|---|---:|
| Maximum raw input and stored record | 1,048,576 bytes |
| Maximum JSON records | 2,000 |
| Maximum CSV data rows | 2,000 |
| Maximum CSV columns | 128 |
| Maximum decoded CSV cell | 16,384 Unicode code points |
| Maximum source label | 128 Unicode code points |

The limits are constants in both the production and independent-validator implementations. A
change requires a versioned contract and new boundary tests.

## Store contract

- The configured root must already exist, be a real directory, and not be a symlink.
- The public store API accepts bytes and a supported media type. It never accepts an output path or
  record identifier from untrusted input.
- Record paths are generated as `records/sha256/<first-two-hex>/<64-hex-digest>` beneath the
  configured root. Digest syntax is checked before every read.
- Writes use a same-root temporary file and an atomic create-if-absent link. Existing content is
  never replaced. A matching existing record is a deduplication success; a mismatching existing
  record is a blocking tamper finding.
- Every read rejects symlinks and non-regular files, enforces the size limit, and recomputes the
  digest. A changed record cannot be returned as valid.
- Generated directories are checked after creation. A symlinked root, `records`, algorithm, or
  shard component is rejected.
- Raw bytes are authoritative. Parsed JSON objects and CSV cells are not substituted for the raw
  record and are not copied into the manifest.

## Manual import contract

- The importer accepts only `bytes`; `str`, `Path`, file objects, URLs, archives, and compressed
  streams are rejected.
- Supported media types are exactly `application/json` and `text/csv`.
- Input must be non-empty UTF-8 without a BOM or NUL. ZIP, gzip, bzip2, 7z, RAR, PDF, ELF, and PE
  signatures are rejected before parsing.
- JSON uses duplicate-key rejection and finite-number rejection. Its root is one object or an array
  of objects; an array is non-empty, contains at most 2,000 records, and every record is an object.
- CSV uses the standard-library parser in strict mode. It requires a non-blank unique header, at
  least one data row, at most 2,000 rows and 128 columns, and an exact field count on every row.
- CSV cells beginning, after whitespace, with `=`, `+`, or `@` are rejected. A leading
  `-` is accepted only for a bounded finite decimal literal; other leading-minus content is rejected as a
  spreadsheet-formula vector. No formula is escaped or rewritten.
- Validation completes before the first store write. Failed imports leave no raw record behind.
- The import result contains only bounded metadata, byte and record counts, the raw digest, the
  deterministic record identifier, and a canonical self-hash. It never contains raw cells,
  credentials, formulas, or an arbitrary path.

## Snapshot and authority contract

- The builder requires a schema-valid verified identity whose status is `verified` and a
  schema-valid structural-scope decision whose outcome is `eligible_for_data_review` and whose
  `eligible_for_m9_data_review` flag is true.
- The scope decision must bind the exact verified-identity ID and hash. The manifest records both
  upstream hashes, the manual-import hash, the raw record hash, and the M8 snapshot hash.
- Snapshot identity fields are exact copies of the verified identity. `request_id` remains an
  explicit caller input because M9-I2's verified-identity interface does not carry it.
- The builder receives an explicit, already-reviewed M8 `license_review`; it validates and copies
  that decision but cannot approve, alter, or infer it. A synthetic approved decision may be used
  only in repository fixtures.
- `complete` requires the existing M8 invariants. Otherwise the caller must select a non-complete
  status consistent with freshness, license, and warnings.
- `source_url` is a generated `urn:fvi:manual-import:<import-id>` and cannot contain a filename or
  caller-controlled URL.
- Snapshot records are sorted by record ID. Snapshot and manifest identifiers are deterministically
  derived from their pre-hash subjects; neither uses randomness, a filesystem name, or process
  state.

## Independent validation

`tools/validate_m9_i3_storage.py` must not import production storage, manual-import, snapshot, or
canonical-hash helpers. It independently:

1. validates the verified identity, scope decision, import result, source snapshot, and manifest;
2. reserializes and rehashes every self-hashed JSON artifact;
3. checks upstream identity/scope and import/snapshot/manifest reference closure;
4. reconstructs the only permitted record path from the raw digest;
5. rejects symlinks, non-regular files, oversize content, and digest or byte-count mismatch;
6. recomputes snapshot identity copies, record metadata, generated IDs, deterministic order, and
   state invariants; and
7. returns a strict validation-result artifact with stable findings and its own hash.

A mutation that changes an artifact and coordinately rehashes downstream artifacts must still fail
when it changes an upstream copy, generated identifier, stored bytes, path semantics, or locked
limit.

## Exit evidence

- focused unit tests for store, importer, builder, schemas, and independent validation;
- write-once, deduplication, traversal/digest, root/component symlink, formula, archive, size,
  encoding, duplicate-key/header, malformed-row, and tamper tests;
- deterministic rerun and coordinated-rehash mutation tests;
- AST/import tests denying network, provider SDK, subprocess, shell, and dynamic execution;
- schema and reference-closure integration tests from M9-I2 identity to M9-I3 manifest;
- repository policy, complete regression suite, and Python 3.10/3.12 CI evidence; and
- an implementation review carrier that records exact subject hashes without changing the frozen
  M9-I2 snapshot subjects.

## Operator recovery notes

- Any `STORE-TAMPER-DETECTED`, unsafe component, or independent-validator raw-record finding is a
  terminal stop for that configured root. Do not rewrite the affected digest path.
- Preserve the root for incident evidence, move runtime use to a newly configured empty root, and
  rebuild only from an independently trusted original byte source whose digest is rechecked.
- A `.pending-*` file can exist only after an interrupted write. It is never a valid record and is
  ignored by manifests. Cleanup requires an operator to confirm that no writer is active and must
  never rename a pending file into a digest path.
- Deduplication is not backup. Backup, retention, deletion ownership, access control, malware
  scanning, and user-upload incident handling remain M8-C03/later-runtime gates.

## Explicit exclusions

- No live SEC or provider access and no transport implementation.
- No user-file collection, browser upload, arbitrary input/output path, archive extraction, or
  malware-scanning service claim.
- No real issuer, provider response, filing, PDF, ebook, private extract, or attached source use.
- No M9-I4 adapter, M9-I5 normalization/reconciliation, M9-I6 pipeline, M10+ behavior, valuation,
  approval creation, stable API/CLI, LLM, UI, pilot, beta, or release work.
- No commit, push, Draft PR, Mark Ready, approval, merge, or feature-branch deletion authority is
  implied by this local implementation authorization.
