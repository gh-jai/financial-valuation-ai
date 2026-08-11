# M9-I2 Bounded Offline Implementation Review

Status: `LOCAL_REMEDIATION_VALIDATED_REVIEW_PENDING`
Review date: 2026-08-11
Canonical repository: `gh-jai/financial-valuation-ai`
Exact implementation base: `8dc7e45a623571e856ccdc4e10ddc62db1c3cdef`
Remediation parent: `126b7baa8f6a2fcb1d31e88e546402445cc0ea07`
Local branch: `feat/m9-i2-issuer-resolution-offline`
Contract snapshot: `1c3754e724f98ff8324c567237070b68fe20514e678de3d1787e51d47f9da918`
Contract package state: `CLOSED_WITH_SINGLE_MAINTAINER_EXCEPTION`
Network state: `DENIED`
Data boundary: synthetic offline identity fixtures only

## Review conclusion

The bounded local remediation candidate passes focused and complete repository tests for code,
contract, artifact-graph, authority-boundary, and regression behavior. It implements only:

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

This carrier binds the current unstaged local remediation bytes. The six GitHub review threads
remain unresolved, and a second-round PASS, platform approval, Mark Ready, or merge is not claimed.

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

## GitHub review findings remediated locally

1. Verified-identity upstream references and evaluation-time structural-scope semantics are now
   independently recomputed, including freshness, exact rules, reason/error pairs, and deferred
   M8 rows.
2. Identity rank/precedence and structural-scope rule/deferred-row semantics are contract-locked,
   and the resolver rejects a catalog adapter outside the policy allowlist.
3. Every policy list is now independently pinned to its exact contract tuple. A coordinated,
   schema-valid policy/catalog adapter substitution that rehashes the complete downstream graph is
   rejected by both the production loader and the implementation-separated validator.
4. This out-of-manifest carrier now binds all 19 current implementation subjects and the current
   39-test focused / 382-test complete-suite evidence.

No reviewed blocking vector remains locally reproducible. The six GitHub threads remain open until
a separately authorized re-review and thread-resolution action.

## Validation evidence

Environment:

- Python 3.12.13;
- pytest 8.4.2;
- jsonschema 4.26.0;
- PyYAML 6.0.3; and
- package-index access disabled during test execution with `PIP_NO_INDEX=1`.

Results:

- focused M9-I2 suite: `PASS`; 39 tests;
- complete repository suite: `PASS`; 382 tests;
- `git diff --check`: `PASS`;
- staged index: empty;
- local remediation state: unstaged and uncommitted; and
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
8d9f7c1cc712b36292c64065f453acf5fd9a7382e53c7dbea526c54d46f7f190 tests/integration/test_m9_i2_artifact_graph.py
cf3b74e4ea26409f9490cac7cdea65564095284bf9441dbe13f5229cb2786546 tests/unit/test_m9_i2_identity_contracts.py
f3692edb84d0e4c9b554cc4cdc97e2707a973997fe2f4eed3520f5a6857b3ba6 tests/unit/test_m9_i2_resolution.py
f6008e473696e31ee2cba39c4884399b91818477d42883f220db2b16bc6ce819 tools/retail_data/__init__.py
0ec4bc40492f86986640be5ae0bfddd6d87d69370cb3847fadbb7cb02e3fe935 tools/retail_data/identity_contracts.py
c80e0d3c6ea0fa695f2217137948aaa0c0c1f16e362d4aa01ef4f5a071f3cc2b tools/retail_data/resolution.py
97a5399e297f91c5a35c06d8e05e86d7da8f978a26fc026beedd8ad075f75c27 tools/retail_data/structural_scope.py
60aff9e4eb7b85537ec42d1a77daab5c5003835acfe9b332290d1d153875d7a9 tools/validate_issuer_resolution.py
```

## Authority boundary

This local `PASS` authorizes nothing beyond reporting the reviewed local result. Stage, commit,
push, Draft PR creation, Mark Ready, platform approval, merge, publication, live/provider access,
real-company data, attachments, M9-I3 through M9-I6, M10, release, and any legal, privacy,
security, accessibility, or provider-license approval remain separately gated.
