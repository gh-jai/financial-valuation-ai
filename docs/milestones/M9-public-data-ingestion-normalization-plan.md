# M9 Public Data Ingestion and Accounting Normalization — Implementation Plan

Status: Planning merged; M9-I1 baseline approved for publication; M9-I2+ not authorized
Plan version: 0.1.0
Planning authorization: Project owner, 2026-08-08
Planning baseline approval: Project owner, 2026-08-08
Planning baseline: M8 review merge `e6a791a827a2a37457494ae0b184d3a37f3040a3`
Target contract: `docs/milestones/M8-retail-product-safety-contract.md`

## Decision

M9 will turn the M8 `company-request`, `source-snapshot`, and
`normalized-financials` interfaces into a deterministic, independently validated data path for
supported US-listed, USD-reporting non-financial operating companies. It will not implement
valuation-case construction, assumptions, lifecycle routing, report rendering, a stable API, a
CLI, a Web interface, model calls, user-file collection, external beta, or release.

The planning decision authorized design and sequencing only; it did not itself authorize code
implementation, live SEC retrieval, a market-data subscription or adapter, provider credentials,
real-company fixtures, user uploads, staging, committing, pushing, or publication. M9-I1 later
received separate implementation, review, and publication authorizations. M9-I2 through M9-I6,
live SEC or provider access, and every release action remain unauthorized.

## M9 outcome

An approved M9 implementation must be able to take an explicit company request through issuer
resolution, an immutable source snapshot, deterministic US-GAAP normalization, reconciliation,
data-quality findings, and an independently recomputed validation result. Every test must run
offline from synthetic fixtures. Unsupported or uncertain cases stop with a stable error and no
valuation output.

```text
Company request
-> deterministic issuer candidates
-> explicit verified identity and support decision
-> provider/license policy check
-> immutable raw snapshot
-> deterministic concept and period mapping
-> reconciliations and data-quality findings
-> normalized-financials artifact
-> implementation-separated validation
-> approved handoff candidate for M10
```

M9 ends at a validated normalized-financials handoff. M10 owns route and assumption construction;
M11 owns stable Python, CLI, and service interfaces; M12 owns uploads and the retail experience.

## Locked planning decisions

### 1. Authority and network boundary

- The data gateway is the only M9 component that may ever receive allowlisted outbound network
  authority. Resolver, store, normalizer, reconciler, validator, and CI remain network denied.
- All adapters start disabled. Registry approval is necessary but not sufficient for live
  activation; the project owner must separately authorize the exact provider, endpoint set,
  credential class, environment, and test window.
- Provider responses, SEC documents, XBRL labels, CSV cells, filenames, redirects, and error bodies
  are untrusted data. They cannot alter policy, select an issuer silently, approve a license,
  suppress a finding, or expand an allowlist.
- CI and the default local suite use only compact synthetic fixtures created for the repository.
  They do not call SEC, a market-data provider, or a model provider.

### 2. Package and dependency boundary

The implementation should introduce a small `tools/retail_data/` package with explicit modules
for contracts, errors, canonical JSON and hashing, registries, resolution, adapters, snapshot
storage, manual import, normalization, reconciliation, pipeline orchestration, and independent
validation. Provider-specific parsing stays behind adapters; provider payload shapes must not leak
into the normalized domain model.

The default implementation uses the Python standard library plus the repository's existing
`jsonschema` and `PyYAML` dependencies. Any additional runtime dependency requires a documented
need, bounded version range, license review, security review, and separate approval in the
implementation checkpoint.

### 3. Storage and canonicalization boundary

- Raw records are written once under a content hash. A logical snapshot is a manifest that refers
  to exact record hashes; it never rewrites a provider response in place.
- Canonical JSON uses UTF-8, sorted keys, compact separators, finite JSON numbers, and an explicit
  canonicalization version. The independent validator reserializes and rehashes every artifact.
- The store accepts only configured roots and generated identifiers. Absolute paths, traversal,
  symlink escape, archive extraction, and user-selected output paths are rejected.
- Secrets, authentication headers, cookies, query credentials, raw stack traces, and unrestricted
  response bodies never enter manifests, logs, fixtures, or user-safe errors.

### 4. Identity and support boundary

- Ticker, company name, or CIK resolution returns candidates; ambiguity is a terminal
  `IDENTITY-*` stop until a human explicitly selects a candidate.
- A verified identity binds ten-digit CIK, legal name, exchange, ticker, and the dated source used
  to verify them. Ticker reuse, delisting, and mismatched CIK/name pairs stop.
- The issuer-support matrix is evaluated deterministically before data acquisition. A supported
  class may still stop when evidence is missing or inconsistent; an unsupported issuer is never
  routed to another method or company.

### 5. Provider and license boundary

- A versioned provider registry contains every field required by the M8 policy, including
  endpoint templates, host and redirect allowlists, data categories, authentication class,
  retention, display/export/redistribution rights, rate limits, territories, review evidence, and
  status.
- The registry is default deny. Unknown, pending, rejected, expired, or field-incompatible rights
  prevent acquisition or downstream use as applicable.
- SEC identity, submissions, filing, and XBRL adapters are separate capabilities so that one
  approval cannot silently authorize all SEC endpoints. Market-data adapters remain interface-only
  until `M8-C02` is satisfied for the exact provider and fields.
- Manual JSON/CSV import is an explicit offline source type, not a fallback disguised as provider
  data. It preserves original cells/records and never executes formulas or archives.

### 6. Normalization and reconciliation boundary

Normalization is deterministic and mapping-versioned. Every normalized fact records its concept,
value, unit, currency, period, provenance kind, source fact references, calculation rule when
derived, and review status. No material missing value is silently replaced by zero, a peer value,
an older filing, or an LLM estimate.

The first M9 concept set covers only inputs needed by the existing FCFF routes and their equity
bridges: revenue, operating income, tax inputs, depreciation and amortization, capital expenditure,
working capital, debt, cash and non-operating assets, minority and other claims, diluted shares,
and the source fields needed to derive them. A proposed concept outside this set requires a mapping
decision and test before use.

Required reconciliation families are:

- duplicate and amendment selection by accession and filing date;
- instant, duration, fiscal period, quarter, year-to-date, and trailing-period alignment;
- currency, unit, scale, decimals, and sign consistency;
- annual versus quarterly roll-forward and cross-statement checks;
- split-adjusted shares and diluted-share consistency;
- cash-flow derivation and FCFF-input completeness;
- acquisitions, disposals, discontinued operations, leases, minority interests, custom tags, and
  other material discontinuities as explicit review or blocking findings.

`quality.status = complete` remains impossible while any fact is unapproved, any required
reconciliation is not passed, or any material blocking/review code remains.

## Implementation slices and checkpoints

Each slice is a separate reviewable checkpoint. Approval of one slice does not authorize the next.

| Slice | Deliverable | Network state | Exit evidence |
|---|---|---|---|
| `M9-I1` | Core error model, canonical JSON/hash helpers, provider/license and concept registries, independent primitives | Denied | Unit, mutation, registry-expiry, secret-redaction, and hash cross-implementation tests |
| `M9-I2` | Deterministic issuer resolver, candidate selection contract, support-matrix evaluator | Denied; synthetic adapter only | Ambiguity, ticker reuse, CIK/name mismatch, unsupported-sector, and stale-identity tests |
| `M9-I3` | Immutable content-addressed store, snapshot builder, safe manual JSON/CSV importer | Denied | Write-once, deduplication, traversal/symlink, formula, size, encoding, and tamper tests |
| `M9-I4` | Disabled SEC adapter implementations plus recorded synthetic response fixtures, limiter/backoff/circuit-breaker logic | Live calls denied by default | Host/redirect/SSRF, User-Agent, global-rate, retry, timeout, cache, and provider-kill-switch tests |
| `M9-I5` | Versioned US-GAAP concept mapper, period graph, normalizer, reconciliation engine, quality findings | Denied | Golden synthetic filings, custom-tag, amendment, unit/period, corporate-action, and no-silent-fill tests |
| `M9-I6` | Offline end-to-end pipeline, independent M9 validator, M10 handoff manifest, adversarial benchmark suite | Denied | Exact-hash recomputation, reference closure, executor/validator separation, deterministic rerun, and full regression suite |

`M9-I4` may implement and test transport policy without performing a live request. A later,
separately approved live-readiness checkpoint must name the exact endpoint allowlist, registry
version, official-policy recheck, User-Agent ownership, rate budget, cache, kill switch, credential
handling, logging/redaction plan, and rollback procedure.

## Required artifacts for an implemented M9

- versioned provider/license, concept-mapping, freshness, and error-code registries;
- resolver candidate and verified-identity domain objects;
- immutable snapshot store and manifest builder;
- disabled SEC identity/submissions/filing/XBRL adapters and a manual import adapter;
- deterministic normalizer, period graph, reconciliation engine, and quality report;
- independent validator that does not import production hashing, normalization, or reconciliation
  helpers;
- synthetic provider and filing fixtures with expected snapshots and normalized outputs;
- unit, schema, integration, adversarial, mutation, and M1-M8 regression tests;
- implementation review record, dependency/license evidence, threat-control traceability, and
  operator notes for provider disablement and artifact recovery.

## Acceptance gates

M9 implementation can be recommended complete only when all of the following are true:

1. The three M9-owned M8 interface schemas validate every accepted artifact and reject unknown
   fields; any schema change is versioned and migration-tested.
2. Resolver, support policy, snapshot, normalization, and validation outputs are deterministic for
   identical inputs and registry versions.
3. The independent validator recomputes canonical hashes, reference closure, status invariants,
   period/unit/currency relationships, reconciliations, and completeness without importing the
   executor implementations under test.
4. All network tests use injected transports or synthetic recordings. The default test command
   succeeds with network disabled and without credentials.
5. Adversarial tests cover ambiguity, stale/replayed responses, malformed provider data, redirects,
   private addresses, traversal, symlinks, CSV formulas, oversized input, custom tags, amendments,
   unit and period corruption, duplicate facts, secret leakage, rate exhaustion, and cache tamper.
6. Provider and field rights fail closed; no market-data adapter or user upload is enabled without
   the corresponding later gate.
7. No M9 component values a company, chooses assumptions, creates an approval, renders a retail
   report, emits action advice, or broadens M8 issuer scope.
8. M1-M8 validators, repository policy, pre-commit, and the complete Python 3.10/3.12 suite pass.
9. No PDF, ebook, private extract, credential, real issuer snapshot, or unapproved provider payload
   is committed.
10. A human financial reviewer approves the concept mappings and reconciliation outcomes, and an
    implementation-separated reviewer approves security, licensing, and validator evidence.

## Conditions and risk register

All `M8-C01` through `M8-C07` remain active. M9 planning does not satisfy them. In particular:

- `M8-C02` blocks enabling any market-data provider or field without exact rights approval.
- `M8-C03` keeps user-file collection disabled; M9 manual import is a local/offline interface until
  privacy and upload handling are approved in the later product runtime.
- `M8-C04` requires implementation evidence and later penetration testing; planning is not a
  security certification.
- `M8-C06` pilots and holdouts remain M13 evidence and must not be used to tune M9 fixtures after
  viewing valuation outcomes.
- `M8-C07` requires official-source and provider-term rechecks at implementation review and release.

| Risk | Planning control | Escalation trigger |
|---|---|---|
| XBRL taxonomy and custom-tag variability | versioned mappings, explicit unmapped findings, holdout cases | material concept cannot be mapped without judgment |
| Period/unit/amendment error | period graph and independent reconciliations | identical facts yield multiple plausible periods or scales |
| Provider terms or API policy change | dated registry evidence and default-deny expiry | terms, endpoint, rate, or allowed use changes |
| Network or SSRF exposure | fixed adapters, injected transport, allowlists, redirect revalidation | any user-controlled URL reaches transport code |
| False completeness | schema invariants plus independent completeness recomputation | material FCFF input lacks an approved trace |
| Architecture coupling | provider/domain separation and executor/validator separation | normalized output requires provider-specific fields |
| Scope creep into M10-M12 | explicit end-state and prohibited capabilities | code proposes assumptions, valuation, approval, API, upload, or UI behavior |

## Review and authorization sequence

```text
Approve this planning baseline
-> separately authorize M9-I1 implementation
-> review, test, and publish M9-I1
-> repeat authorization per slice through M9-I6
-> complete cross-functional M9 implementation review
-> separately authorize any live-readiness test
-> accept or request changes to M9
-> authorize M10 planning
```

Project-owner decision for this plan:
`[x] M9 implementation planning authorized  [ ] request further M8 changes`

Planning baseline decision:
`[x] approve baseline  [ ] request changes  [ ] reject`

Implementation decision:
`[x] authorize M9-I1 implementation  [ ] request plan changes`

Current implementation record: M9-I1 implementation baseline approved. M9-I2 through M9-I6
remain unauthorized, and live SEC or provider access remains unauthorized. See
`docs/milestones/M9-I1-implementation-review.md`.
