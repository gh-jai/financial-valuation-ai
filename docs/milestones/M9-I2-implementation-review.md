# M9-I2 Bounded Offline Implementation Review

Status: `LOCAL_REVIEW_PASS_NOT_PUBLISHED`
Review date: 2026-08-09
Canonical repository: `gh-jai/financial-valuation-ai`
Exact implementation base: `8dc7e45a623571e856ccdc4e10ddc62db1c3cdef`
Local branch: `feat/m9-i2-issuer-resolution-offline`
Contract snapshot: `1c3754e724f98ff8324c567237070b68fe20514e678de3d1787e51d47f9da918`
Contract package state: `CLOSED_WITH_SINGLE_MAINTAINER_EXCEPTION`
Network state: `DENIED`
Data boundary: synthetic offline identity fixtures only

## Review conclusion

The bounded local implementation passes code, contract, artifact-graph, authority-boundary, and
regression review with no unresolved blocking, high, medium, or low finding. It implements only:

```text
strict company-request
-> deterministic synthetic issuer candidates
-> exact-hash-bound human selection
-> verified issuer identity
-> structural M9 data-review eligibility pre-screen
-> implementation-separated validation result
```

The independent validator does not import the production resolver, normalization, candidate
ordering, selection, identity construction, or structural-scope evaluator. AST/import tests also
deny transport, socket, HTTP client, provider SDK, subprocess, shell, and dynamic-execution paths.

This review was performed as a role-separated local review in the same Codex execution context
that authored and remediated the candidate. It is not an external-human or GitHub platform
approval and must not be represented as reviewer/author identity separation. The mechanically
independent validator boundary is satisfied; any later governance rule requiring a distinct human
or external reviewer remains unsatisfied until separately evidenced.

## Scope reviewed

- eight strict Draft 2020-12 M9-I2 schemas, all rejecting unknown fields;
- duplicate-key-safe JSON/YAML loading, finite canonical JSON, SHA-256 self-hashes, canonical
  collection order, governed status/effective/expiry intervals, and reference closure;
- frozen allowlisted synthetic catalog, identity policy, and structural-scope registry;
- exact CIK, current ticker, legal name, declared alias, and historical ticker matching;
- ambiguity, ticker reuse, future evidence, CIK/name mismatch, stale evidence, private identity,
  non-US/non-USD scope, unsupported taxonomy, and contradictory classification stops;
- mandatory human selection for unique and ambiguous candidate sets, with replay invalidation;
- exact selected-candidate copying, freshness recomputation, and lifecycle-route non-evaluation;
- independent candidate/catalog reconstruction, derived IDs, nested hashes, timestamp chain,
  policy/registry effectiveness, exact M8 matrix byte hash, subjects, findings, and result hash;
- no M9-I3 storage/import, filing acquisition, normalization, valuation, API, CLI, LLM, UI,
  provider activation, live access, real-company material, attachment use, or M1-M7 contract edit.

## Findings remediated during review

1. Structural country/currency rules initially recognized only synthetic sentinel codes. They now
   use strict `not_equals` predicates so every non-US and non-USD value is unsupported.
2. A private public-company status could initially reach verified identity. Verification and the
   verified-identity schema now stop it before handoff.
3. Verification initially relied on the outer candidate-set hash without rechecking each candidate
   self-hash or selection reason/count. Both checks are now mandatory.
4. Fund-family taxonomy and catalog semantic failures were initially incomplete. ETF, investment
   company, and non-operating vehicle rules now close to the M8 matrix, while CIK/name conflict,
   future evidence, content-hash failure, ticker reuse, and catalog conflict retain their exact
   stable error codes.
5. The independent validator initially checked the graph but not every candidate/catalog copy,
   governed timestamp, or M8 matrix byte hash. These are now independently recomputed and covered
   by mutation-kill regressions.

No finding remains open.

## Validation evidence

Environment:

- Python 3.12.13;
- pytest 8.4.2;
- jsonschema 4.26.0;
- PyYAML 6.0.3; and
- dependency installation and network access disabled during validation.

Results:

- focused M9-I2 suite: `PASS`; 29 tests;
- complete repository suite: `PASS`; 372 tests;
- schema/document validation: `PASS`; 29 schemas and 121 governed documents;
- repository content policy: `PASS`; 498 candidate files, no prohibited source;
- all-file pre-commit: `PASS`; all 16 configured hooks;
- explicit new-file pre-commit: `PASS`; all 16 configured hooks;
- `git diff --check`: `PASS`;
- staged index: empty; and
- five attested subject hashes and snapshot ID: unchanged and exactly recomputable.

## Reviewed local file manifest

The hashes below bind the reviewed implementation bytes but do not grant publication authority.
This review record is intentionally outside the manifest to avoid self-reference.

```text
795d105a85a68f4606c1888d4fcd9565a4d900af6034b7ee468eeff11ab1837b benchmarks/fixtures/m9_i2/synthetic-identity-catalog.yaml
b2ae5dd8e52c1548810cfb339ae7480cdcd357de8fa9bb0e20043558b84aa1a2 registries/m9-identity-resolution-policy.yaml
49f3377e075b3a353829b6085072f38af389c7d694b50d26615aef3eff81aa0b registries/m9-issuer-structural-scope.yaml
ecd2751e4ba847f3daa76c43660e3546793bb9531b69f6adbae2de16532cc641 schemas/identity-resolution-policy.schema.json
eee87feb1813ee1b445110333a2185144eb9c08f972cad239c3552f55cbf773c schemas/issuer-candidate-set.schema.json
f093779316f5c6c56025d8bbc7225c993ac020f66eff03afe78ae95937f50653 schemas/issuer-identity-catalog.schema.json
f4116f97086d532d701c6e9ebf1c5776b6bba986e4c9ed1a538347d592a44549 schemas/issuer-resolution-validation-result.schema.json
17d3d5834bfaca5414aca5f430f7c1825ff15e9a654f22402f1bbf0c60a21ab5 schemas/issuer-selection.schema.json
6d2b6e0e7efdd8bf6dd2b64679dcb917e2a770277e5406f42b13af3afb0dbab9 schemas/issuer-structural-scope-decision.schema.json
df3c7a22f75c91048e1ca4afeb7d7d6e72d250fa03921841e30e6601de49e67d schemas/issuer-structural-scope-registry.schema.json
2d6c78769b21b2cf1c59600e5cea1dd5339a277d7fb5f12d5e61e5c0698eff2f schemas/verified-issuer-identity.schema.json
bd09cac8470ee89fd1f4262c8442f03f85ee1d7751b391bd6b8ea7498898c676 tests/integration/test_m9_i2_artifact_graph.py
f92c63c3ee51b6dc7d1c5cb217a4a73d318b77880a17f580cd8cfb3f74ed2df2 tests/unit/test_m9_i2_identity_contracts.py
7087b34faa9861f3e16ba3f89ee0b508797470ff3bc4434df66ae369ba1dccc0 tests/unit/test_m9_i2_resolution.py
f6008e473696e31ee2cba39c4884399b91818477d42883f220db2b16bc6ce819 tools/retail_data/__init__.py
03f4f2ba7810c25c8ea803343f2f058789ac0860351245398041d3e89d46e351 tools/retail_data/identity_contracts.py
ebdbe458216395af00ccc2766fed65f53230fd6b42cc32639cac2a0094f4b61e tools/retail_data/resolution.py
97a5399e297f91c5a35c06d8e05e86d7da8f978a26fc026beedd8ad075f75c27 tools/retail_data/structural_scope.py
a5774d922ba27a7156077d966f1a5f30b6fba28813b1f5fab94d55b2d0119bcc tools/validate_issuer_resolution.py
```

## Authority boundary

This local `PASS` authorizes nothing beyond reporting the reviewed local result. Stage, commit,
push, Draft PR creation, Mark Ready, platform approval, merge, publication, live/provider access,
real-company data, attachments, M9-I3 through M9-I6, M10, release, and any legal, privacy,
security, accessibility, or provider-license approval remain separately gated.
