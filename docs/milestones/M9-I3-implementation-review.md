# M9-I3 Bounded Offline Implementation Review

Status: `LOCAL_CANDIDATE_VALIDATED_REVIEW_PENDING`
Review date: 2026-08-11
Canonical repository: `gh-jai/financial-valuation-ai`
Exact implementation base: `3ea93c8751bfaa558d3597a91b978f986dac6412`
Local branch: `feat/m9-i3-immutable-snapshot-store`
Network state: `DENIED`
Data boundary: compact synthetic UTF-8 JSON/CSV only

## Local conclusion

The current unstaged local candidate implements the separately authorized M9-I3 slice:

```text
M9-I2 verified identity and eligible scope
-> hostile-input-safe local JSON/CSV bytes interface
-> atomic write-once SHA-256 store
-> M8 source-snapshot
-> exact-reference M9-I3 manifest
-> implementation-separated validation result
```

The candidate is locally green on Python 3.12. It is not yet committed, pushed, published, or
reviewed through GitHub. Python 3.10 and remote matrix evidence remain pending until a separately
authorized publication workflow exists.

## Delivered boundary

- strict contract and three Draft 2020-12 schemas for import result, snapshot manifest, and
  independent validation result;
- configured-root, generated-path-only, content-addressed raw-byte storage;
- atomic create-if-absent writes, exact-byte deduplication, read-time rehashing, and symlink/tamper
  rejection;
- bounded JSON and CSV import with duplicate-key/header, finite-number, formula, archive, size,
  row, column, cell, NUL, BOM, and UTF-8 controls;
- deterministic M8 source-snapshot and M9-I3 manifest construction bound to exact M9-I2 identity
  and scope hashes;
- independent schema, hash, raw-byte, path, ID, upstream-copy, and reference-closure validation;
  and
- one compact original synthetic CSV fixture with unit, integration, adversarial, mutation,
  authority-boundary, and repository-regression tests.

## Validation evidence

- focused M9-I3 suite: `PASS`; 42 tests;
- complete repository suite: `PASS`; 424 tests;
- schema/governed-document validator: `PASS`; 32 schemas and 121 governed documents;
- source, claim, narrative, M3-M7 domain, and agent validators: `PASS`;
- repository content policy: `PASS`; 377 candidate files and no prohibited source;
- `git diff --check`: `PASS`;
- Python 3.10 grammar compatibility: `PASS`; eight changed Python files;
- Python 3.10 runtime and GitHub Actions matrix: not yet run; and
- staged index: empty; commit, push, and Draft PR not authorized.

## Threat-control disposition

| Threat | Local evidence | Result |
|---|---|---|
| overwrite or digest collision path | create-if-absent link, dedup rehash, mismatch stop | Pass |
| traversal or caller-selected output | digest-only generated path; invalid digest tests | Pass |
| symlink/root escape | root, layout, shard, and record `lstat` checks | Pass |
| archive/executable input | magic-signature deny before parsing | Pass |
| encoding/parser ambiguity | strict UTF-8, no BOM/NUL, duplicate JSON/header rejection | Pass |
| spreadsheet formula injection | prefix checks including whitespace/newline concealment | Pass |
| resource exhaustion | locked byte, number, row, column, and cell limits | Pass |
| raw-byte tamper | production read rehash plus separate validator rehash | Pass |
| coordinated downstream rehash | upstream identity copy and manifest closure mutation tests | Pass |
| network/provider authority creep | AST import/call denial and no transport surface | Pass |

## Explicitly not claimed

- no independent human or GitHub platform review;
- no Python 3.10 or remote Actions evidence yet;
- no user-upload collection, malware scanner, retention service, backup system, or privacy approval;
- no live/provider access, SEC adapter, normalization, reconciliation, pipeline, valuation, API,
  CLI, LLM, UI, pilot, beta, or release capability; and
- no commit, push, Draft PR, Mark Ready, approval, merge, or branch deletion authority.

## Reviewed local file manifest

The hashes below bind the final local candidate bytes. This review file is intentionally excluded
from its own manifest to avoid self-reference.

```text
d14c098bf2c660b180debb5614d897052d1d35b34c81987dc30a861b14b362a7 benchmarks/fixtures/m9_i3/synthetic-manual-financials.csv
49b19fc6fede17064718b0f4c205bb062c7f107e68dd1afe1ac4d93e2e50d843 docs/milestones/M9-I3-immutable-snapshot-store-contract.md
a3bd2423c4c26b64592d891cea7ef581eca42e72580c8717a1b4b2c67d25ab23 schemas/manual-import-result.schema.json
8f1148f9e5e2463d59c0f1cb3b678fd3374f38f827c7befc7b9636236882e127 schemas/m9-snapshot-manifest.schema.json
dafd86469626d20ab1dd87c06fe93dc0c7c8e8fbf4bf4d0ba1007b9ba9dc15cd schemas/m9-storage-validation-result.schema.json
c5d9ca8b321cfe573b8411fa78d0aea0c8d2a9efc7e54f39d5505a81fc9e3a87 tools/retail_data/__init__.py
96060ad64c04d4886d5363f2c233d978406f6914ac57aeb64e73003b0f803a00 tools/retail_data/storage.py
4af1abe6ce24586b7c78f063aeef6321c152b56117921da9bbabbb8028294eb2 tools/retail_data/manual_import.py
66096a947617a3a8d135fed3879c4530d5623c14a7e302d92a0447dbeb244adb tools/retail_data/snapshots.py
295fb7d3a05cd0b2fd6480fae547413a585182c345ae1f47d908b704cc509849 tools/validate_m9_i3_storage.py
2bdfb55b2208e8cbf9a7f50c9a534e91ecf497b35eec76f848009af57bbc40cd tests/unit/test_m9_i3_contract.py
e294f605f99eeca7128a65dbb557139d3bb8aa242872d2fc418a052617452190 tests/unit/test_m9_i3_storage.py
65ff29f6eb71b650a69cfa4c579aaf90fca12bd9905ddf2747676e6cd69244f6 tests/unit/test_m9_i3_manual_import.py
59e0637ca981e1405313b0725cb8e134bd7175ff62b0aeee1aa446638eb94357 tests/integration/test_m9_i3_storage_graph.py
```
