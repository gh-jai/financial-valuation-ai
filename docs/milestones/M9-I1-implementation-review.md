# M9-I1 Offline Primitives — Implementation Review

Status: Implementation baseline approved; publication authorized
Implementation authorization: Project owner, 2026-08-08
Implementation baseline approval: Project owner, 2026-08-08
Publication authorization: Project owner, 2026-08-09
Planning baseline merge: `d129d3edd44e991194c5db2e291b56fb813851d5`
Network state: Denied; no transport implementation exists

## Delivered boundary

- `tools/retail_data/errors.py` defines immutable errors with a stable code, user-safe message,
  severity, retryability, artifact references, and one enumerated next action.
- `tools/retail_data/redaction.py` redacts structured secret-bearing fields and common credential
  forms, removes line breaks, and bounds untrusted messages.
- `tools/retail_data/canonical.py` locks UTF-8, sorted keys, compact separators, finite JSON
  numbers, SHA-256, and canonicalization version `fvi-canonical-json-v1`.
- `tools/retail_data/independent.py` independently walks, serializes, and hashes artifacts without
  importing the production canonicalization module.
- `tools/retail_data/registries.py` strictly loads immutable provider/license and concept
  registries, rejects unknown fields, and fails closed for unknown, non-approved, expired,
  field-incompatible, right-incompatible, or territory-incompatible use.
- `registries/m9-provider-license.yaml` keeps SEC public-data rights pending and every right false.
  `live_activation` is locked to `disabled`; no adapter, transport, credential, or request exists.
- `registries/m9-concepts.yaml` defines only the bounded FCFF and equity-bridge concept vocabulary.
  It does not map provider or XBRL facts; mapping remains `M9-I5`.

## Scope exclusions

- No issuer resolution or support routing (`M9-I2`).
- No store, snapshot builder, or manual importer (`M9-I3`).
- No SEC adapter, URL handling, limiter, retry, cache, or network call (`M9-I4`).
- No XBRL mapping, normalization, period graph, or reconciliation (`M9-I5`).
- No pipeline, M10 handoff, or complete M9 validator (`M9-I6`).
- No live provider data, real issuer fixture, PDF, ebook, credential, API, CLI, LLM, UI, valuation,
  report, or approval authority.

## Exit-evidence checklist

- [x] Canonical JSON unit vectors cover ordering, Unicode, compact encoding, mutation, invalid
  types, unknown versions, and non-finite numbers.
- [x] Production and implementation-separated SHA-256 implementations match the same vectors.
- [x] Error tests cover stable shape, retry/action consistency, identifier safety, duplicate
  references, bounded messages, nested secret fields, authorization headers, and query secrets.
- [x] Registry tests cover exact rights, default deny, status, expiry, territory, category,
  unknown fields, duplicate identifiers, disabled live activation, and post-load mutation.
- [x] Committed registries contain only synthetic/governance metadata and no provider payload.
- [x] Reconstructed candidate passes 319 tests, including all M1-M8 regressions.
- [x] Human implementation review complete.
- [x] Stage, commit, push, and Draft PR authorized.

## Review decision

`[x] approve M9-I1 implementation  [ ] request changes  [ ] reject`

Review conclusion: Approved by the project owner on 2026-08-08. Publication actions were
separately authorized on 2026-08-09 for the reconstructed, revalidated baseline. This decision
does not authorize `M9-I2`, any later implementation slice, live readiness, provider access, Mark
Ready, approval, merge, or release.
