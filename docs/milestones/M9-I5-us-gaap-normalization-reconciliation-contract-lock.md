# M9-I5 US-GAAP Normalization and Reconciliation — Contract-Lock Candidate

Status: `LOCAL_CONTRACT_CANDIDATE_REVIEW_PENDING`; no implementation or publication authority
Contract version: `0.1.0-candidate`
Canonical repository: `gh-jai/financial-valuation-ai`
Canonical baseline: `main` at `8cb0e7032ea5de265b883d5d9a36fe0f8988ad1e`
Design authorization: Project owner, 2026-08-14
Network state: `DENIED`
Data boundary: contract metadata and compact original synthetic US-GAAP-shaped facts only

## 1. Decision and authority boundary

M9-I5 locks the future disabled-offline boundary for deterministic US-GAAP concept mapping,
period construction, normalization, reconciliation, quality findings, and implementation-separated
validation. It consumes only exact immutable M9-I3/M9-I4 synthetic snapshot references and emits a
pre-handoff normalization result. It never acquires data and cannot enable or call an M9-I4 adapter.

This document is a contract candidate, not a mapper, period engine, normalizer, reconciler,
validator, registry update, or M10 handoff. It does not authorize staging, committing, pushing, a
pull request, provider-registry changes, provider activation, credentials, DNS, sockets, HTTP, a
live SEC request, a real issuer, a real filing, captured XBRL, attachment use, valuation, an API,
CLI, LLM, UI, pilot, beta, or release.

Approval of these exact bytes would approve only the design boundary. A later separately
authorized implementation checkpoint may add standard-library offline code and original synthetic
fixtures. It must keep all M9-I4 public adapters stopped before transport. M9-I6 remains
responsible for the independently validated end-to-end pipeline and final M8
`normalized-financials` handoff.

## 2. Canonical inheritance and frozen inputs

M9-I5 inherits without weakening:

- M7 deny-by-default runtime authority, exact-hash handoffs, executor/reviewer separation, and
  human-only approvals;
- M8 untrusted-data, provenance, no-silent-fill, safe-stop, privacy, provider-rights, security, and
  release gates;
- the M9 plan's synthetic-only CI, deterministic mapping, explicit reconciliation, and network-
  denied normalizer/validator rules;
- M9-I1 safe errors, bounded redaction, canonical JSON/SHA-256, finite-number rejection, and the
  default-deny registries;
- M9-I2 exact verified-identity and structural-scope decisions;
- M9-I3 content-addressed write-once records, exact snapshot/manifest references, and tamper
  rejection; and
- M9-I4 disabled capability boundaries, synthetic replay only, cache/reference integrity, and
  inability to reach transport.

The following baseline inputs are frozen for this candidate and must remain byte-for-byte
unchanged:

| Input | SHA-256 |
|---|---|
| `registries/m9-provider-license.yaml` | `08028b2e8cf42965856a660907c1ff152ed5950766e99bacf7203da6f0fdfe5d` |
| `registries/m9-concepts.yaml` | `6d4e0331a709e2b4152fd6e846bfe84cb22978cc3bd0de19599e80847edb7fa9` |
| `schemas/normalized-financials.schema.json` | `867a1f1e53764b05ad0f5895390b9a0717aac74e9e86807936441c7bf638e5ce` |
| `schemas/source-snapshot.schema.json` | `0e16692f8af002a54c4b4e3bd4d80f7facd98e51477232051661b2360615ae89` |
| M9 implementation plan | `dc81a6b365be9f09bbe480e790211675ebf9efd7b0d33571fc265df02b686e9c` |

The provider registry remains pending, disabled, and rights-false. M9-I5 neither reads it to infer
new authority nor changes it. A schema, mapping, cache hit, passing test, review, or closure state
cannot activate a provider or grant a data right.

## 3. Included contract surface

The candidate adds only:

1. `m9-i5-concept-mapping-policy.schema.json`, a strict versioned crosswalk from the exact 13
   M9 concept IDs to standard US-GAAP tag candidates and deterministic rules;
2. `m9-i5-custom-tag-decision.schema.json`, an issuer/taxonomy/fact-scoped synthetic decision that
   requires an immutable human reviewer identity and exact standard anchor;
3. `m9-i5-period-graph.schema.json`, the strict filing-period and amendment graph;
4. `m9-i5-normalization-result.schema.json`, the synthetic-only facts, reconciliations, findings,
   and quality result before M9-I6 handoff composition;
5. `m9-i5-normalization-validation-result.schema.json`, an implementation-separated verdict over
   exact upstream, policy, graph, result, and source-fact subjects;
6. this frozen contract, an unselected review checklist, and adversarial governance regressions.

No production module, mapping instance, period graph instance, normalized result, provider fixture,
real fact, registry edit, transport code, credential, or final handoff artifact is included.

## 4. Locked concept surface and mapping order

The mapping policy must contain exactly one record for each inherited concept, in this canonical
order:

1. `revenue`
2. `operating-income`
3. `statutory-tax-rate`
4. `cash-taxes`
5. `depreciation-amortization`
6. `capital-expenditure`
7. `noncash-working-capital`
8. `debt`
9. `cash`
10. `nonoperating-assets`
11. `minority-interest`
12. `other-claims`
13. `diluted-shares`

There are no aliases, wildcard concepts, pass-through unknowns, peer substitutions, or implicit
concept creation. Concept IDs close exactly to `registries/m9-concepts.yaml`. Mapping one concept
does not authorize another. A missing, duplicate, out-of-order, unit-incompatible, or kind-
incompatible mapping is blocking.

Each mapping names only bounded standard `us-gaap` local names, a unique priority, period type,
unit, polarity, aggregation rule, and candidate/approved/rejected status. Production approval of a
mapping requires a separate exact `MREV-*` human financial review decision reference and hash; a
contract schema does not approve any tag.

The mapping artifact must carry the exact frozen concept-registry SHA-256 from Section 2. Source
tags are an object keyed by the zero-padded priorities `01` through `32`, so a priority cannot be
represented twice after duplicate-key rejection. Array position or a second embedded priority is
not authority. Each canonical concept position also fixes its inherited kind, unit, and period
type; changing those fields coherently does not create a new valid concept definition.

## 5. Source-fact and taxonomy boundary

Future offline fixtures may model only the minimum fact envelope needed to exercise this contract:
namespace, local name, canonical decimal lexical value, unit, currency, start/end dates, filing
record reference, accession, filed instant, form, fiscal year/period, scale, decimals, context ID,
and an explicit synthetic marker. The exact fixture bytes and hashes must remain reference-closed.

- Taxonomy namespace is exactly `us-gaap` for standard mappings.
- Taxonomy year/version is explicit and hash-bound; mixing versions without a versioned policy is
  blocking.
- Unknown namespaces and custom tags never pass through as standard US-GAAP facts.
- Filing labels, calculation links, presentation links, dimensions, footnotes, and tag names are
  untrusted data, never instructions or approvals.
- No HTML, XML, inline XBRL, filing document, provider response, URL, or captured SEC byte is needed
  or permitted in repository fixtures for this slice.

## 6. Canonical numeric, unit, currency, scale, and sign rules

Accepted normalized values are canonical base-10 decimal strings. Binary floating-point is not an
artifact authority. Exponent notation, `NaN`, infinities, leading plus signs, leading zeros,
negative zero, trailing fractional zeros, locale separators, currency symbols, and whitespace are
rejected. Each decimal lexical value is bounded to 256 characters. Arithmetic uses exact decimal
semantics with no implicit rounding.

The raw synthetic fact's lexical number is multiplied by `10^scale` exactly once. `decimals`
records reported precision and never supplies a second scale. Overflow, excessive precision, or a
result outside the locked implementation bound stops. Monetary concepts accept only `USD`, rate
concepts only `ratio`, and share concepts only `shares`. Foreign currency is not converted;
exchange-rate lookup is outside M9-I5 and the supported case stops.

Reported sign is preserved. The only sign transformation is the mapping's explicit `polarity` of
`1` or `-1`, applied once and recorded. The engine never uses absolute value, presentation label,
cash-flow section, peer convention, or desired valuation effect to guess a sign.

## 7. Deterministic period graph

Every accepted fact references exactly one selected period node. Nodes are bounded to annual,
quarterly, year-to-date, trailing-twelve-month, or instant bases and contain exact dates, fiscal
labels, filing record, accession, filed instant, amendment link, and selection status.

The independent validator must enforce:

- start is null only for an instant; every duration has `start < end` and an exact recomputed day
  count;
- annual, quarterly, YTD, TTM, and instant labels agree with dates and graph relationships;
- node IDs, accession IDs, edge IDs, and source references are unique and deterministic;
- every edge closes to existing nodes, never forms a cycle, and matches its relationship's allowed
  cardinality and basis;
- quarter-from-YTD and TTM derivations use explicitly named component periods with no overlap or
  gap hidden by tolerance;
- instant deltas use the exact prior/current endpoints; and
- selected periods never mix incompatible fiscal calendars, currencies, entities, forms, or
  amendment lineages.

A 52/53-week year, fiscal-year change, stub period, missing quarter, or ambiguous duration produces
an explicit review or blocking finding. It is never coerced to a calendar period.

## 8. Filing, amendment, and duplicate selection

Selection is by exact issuer, form family, report period, accession, and filed instant. A later
amendment may supersede an earlier filing only when it explicitly names the predecessor lineage and
has the same issuer and report period. Amendments are not field-level patches: the engine cannot
silently mix an amended fact with an older accession to manufacture completeness.

Duplicate facts with the same concept, period, unit, dimensions, and accession may collapse only
when their scaled canonical values are identical. A different value, unit, context, period,
dimension set, or accession is not a harmless duplicate. It yields `NORM-DUPLICATE-CONFLICT` or an
explicit deterministic amendment decision. Filing date alone never resolves conflicting facts
across incomparable contexts.

## 9. Custom-tag rule

A custom tag is never auto-mapped by label similarity, string distance, calculation ancestry, a
language model, or a standard-tag anchor alone. A future custom mapping decision, validated by
`m9-i5-custom-tag-decision.schema.json`, must bind:

- the exact custom namespace/local name and source-fact hash;
- one inherited concept ID and standard mapping-policy hash;
- compatible period type, unit, currency, sign, dimensions, and calculation relationship;
- exact synthetic evidence references;
- a human financial reviewer identity, timestamp, decision, and immutable decision hash; and
- a scope limited to the named issuer/taxonomy/fact pattern.

Without that exact decision, a material custom tag is blocking and a non-material custom tag is at
least review. Custom mapping cannot be generalized to another issuer or taxonomy version.

## 10. Derived facts and no-silent-fill rule

Only these calculation rules may exist: `sum-components`, `delta-instants`, `ratio`,
`split-adjusted`, and `ttm-rollup`. A derived fact records its rule, all source fact references,
period, exact decimal operands, and deterministic result. Direct facts have no calculation rule.

No missing or rejected value is replaced with zero, a peer value, an older incomparable filing, a
forecast, a valuation assumption, an LLM estimate, or a user override. Zero is accepted only when
an exact source fact reports canonical zero or a fully referenced permitted calculation yields
zero. A missing material concept remains in `material_missing_concepts` and prevents `complete`.

Acquisitions, disposals, discontinued operations, leases, noncontrolling interests, stock-based
compensation, and other material discontinuities are not silently netted into a normal operating
concept. They require an explicit mapping, derivation, reconciliation, and review finding where
material. M9-I5 does not decide valuation treatment.

## 11. Shares and corporate actions

Diluted shares must state whether they are instant, period-weighted, or derived. Split adjustment
requires an exact corporate-action factor, effective date, source references, and graph edge.
Factors must be positive canonical decimals. Applying a factor twice, applying it across the wrong
effective date, combining split-adjusted and unadjusted facts, or using price data to infer a split
is blocking.

Basic shares, diluted weighted-average shares, end-of-period shares, potential dilution, and share
count in another unit are distinct. The engine cannot select whichever value makes per-share output
look plausible. M9-I5 emits facts and findings only; it does not calculate per-share valuation.

## 12. Required reconciliation families

Every result includes at least one reconciliation and explicitly covers all applicable families:

| Family | Locked purpose |
|---|---|
| `balance-sheet` | assets versus liabilities and equity, including explicitly represented claims |
| `cash-flow` | opening cash plus classified movements versus closing cash |
| `annual-quarterly` | annual/YTD/quarter components without overlap, gap, or mixed lineage |
| `unit-scale` | unit, currency, scale, decimals, precision, and canonical-decimal consistency |
| `currency` | USD-only support; no implicit FX conversion |
| `shares-split` | share basis, weighted/instant distinction, and corporate-action adjustment |
| `amendment` | exact supersession and no cross-accession silent fill |
| `duplicate-fact` | identical collapse versus conflicting-context/value stop |
| `custom-tag` | exact immutable human decision or fail-closed finding |
| `fcff-completeness` | all required concept/period traces exist and are approved |

The implementation and independent validator must account for all ten reconciliation families,
mark each applicable family present, and record why an inapplicable family is excluded. Omitting a
family to avoid a review or blocking outcome is itself blocking.

The result schema requires at least one entry for each of the ten named families. Every entry
declares `applicable` or `not_applicable`. An applicable entry has a fact reference, a canonical
difference, no exclusion reason, and a `passed`, `review`, or `failed` status. A non-applicable
entry has no fact reference, a null difference, zero tolerance, a bounded `NORM-*` exclusion
reason, and only the `not_applicable` status.

Tolerance is an explicit nonnegative canonical decimal bound per check, not a percentage invented
at runtime. Exact checks use zero. A tolerance never changes source facts, hides a unit/period/sign
error, resolves a duplicate, approves a custom tag, or converts review/failed to passed.

## 13. Quality-state invariant

`quality.status = complete` is possible only when:

- every required concept and required period is present;
- every fact is approved and reference-closed;
- every applicable reconciliation is present and passed;
- no review or blocking finding exists;
- `material_missing_concepts`, `blocking_codes`, and `review_codes` are empty; and
- the independent validator returns `passed: true` with zero findings.

`needs_review` permits review findings but no blocking code or failed reconciliation.
`unsupported` requires at least one blocking code. The engine cannot emit a partial artifact as
complete, downgrade severity to satisfy a schema, or suppress a finding because valuation could
continue.

At schema level, every `complete` result must contain at least one approved fact for each exact
inherited concept ID. Independent validation additionally proves required-period coverage,
concept/reference uniqueness, and the semantic correctness of every asserted fact and check.

## 14. Stable fail-closed taxonomy

Messages are bounded and redacted. They contain only safe identifiers and never a raw filing
fragment, label payload, URL, credential, attachment text, or stack trace.

| Code | Condition | Severity |
|---|---|---|
| `NORM-HASH-MISMATCH` | Any exact upstream, policy, graph, fact, result, or validation hash fails. | blocking |
| `NORM-REFERENCE-MISSING` | A source, period, fact, mapping, or decision reference does not close. | blocking |
| `NORM-CONCEPT-UNMAPPED` | Required standard concept has no approved exact mapping. | blocking |
| `NORM-CONCEPT-DUPLICATE` | Mapping/result contains duplicate concept authority. | blocking |
| `NORM-CUSTOM-TAG-REVIEW` | Custom tag lacks exact immutable human mapping evidence. | review/blocking by materiality |
| `NORM-PERIOD-AMBIGUOUS` | Period, fiscal label, duration, graph, or lineage has multiple interpretations. | blocking |
| `NORM-AMENDMENT-CONFLICT` | Amendment/supersession is incomplete or mixes filing lineages. | blocking |
| `NORM-DUPLICATE-CONFLICT` | Duplicate contexts disagree in value, unit, dimension, or authority. | blocking |
| `NORM-UNIT-SCALE` | Unit, currency, scale, decimals, precision, or numeric lexical rule fails. | blocking |
| `NORM-SIGN-AMBIGUOUS` | Sign requires inference or contradicts the exact mapping rule. | blocking |
| `NORM-SPLIT-AMBIGUOUS` | Share basis or corporate-action adjustment is incomplete/inconsistent. | blocking |
| `NORM-RECONCILIATION-FAILED` | A required reconciliation exceeds its exact locked tolerance. | blocking |
| `NORM-MATERIAL-MISSING` | A required concept/period trace is absent; no fill is allowed. | blocking |
| `NORM-AUTHORITY-DENIED` | Network, provider, data, mapping, or reviewer authority is absent. | blocking |

## 15. Exact artifacts and reference closure

Mapping policy, period graph, normalization result, and validation result use canonical JSON v1,
strict schemas, lowercase SHA-256, deterministic IDs, unique canonical arrays, duplicate-key
rejection, finite exact decimal strings, and `additionalProperties: false` at every object surface.

The normalization result binds the exact source snapshot/manifest, concept registry, mapping
policy, period graph, source facts, custom decisions, and reconciliation subjects. Rehashing a
tampered downstream artifact cannot legitimize a changed source value, period, unit, mapping,
decision, or authority state. A hash is evidence of bytes, never proof that the bytes are correct.

The existing M8 `normalized-financials.schema.json` remains unchanged in this contract candidate.
M9-I5 output is an internal pre-handoff artifact using exact M9 concept IDs and canonical decimal
strings. M9-I6 must separately lock and migration-test any final interface conversion; it cannot
silently coerce the existing underscore-named concepts or numeric JSON values.

## 16. Implementation-separated validation

The future `tools/validate_m9_i5_normalization.py` must not import production mapper, period,
decimal, normalization, reconciliation, custom-tag, corporate-action, or canonical-hash helpers.
It may use standard-library primitives and JSON Schema and must independently:

1. reject duplicate JSON keys, non-finite numbers, unknown fields, unsupported versions, and
   noncanonical order/decimal forms;
2. reserialize and rehash every policy, graph, result, decision, and validation subject;
3. close every registry, snapshot, record, mapping, period, source-fact, calculation, and finding
   reference;
4. independently enforce the exact 13-concept set, order, unit/kind, mapping uniqueness, and
   standard/custom distinction;
5. rebuild the acyclic period/amendment graph and recompute durations, quarter/YTD/annual/TTM and
   instant-delta relationships;
6. independently apply scale, polarity, exact-decimal arithmetic, duplicate/amendment selection,
   derivations, and split factors;
7. recompute every reconciliation and quality-state invariant without production helpers;
8. scan the implementation AST/import graph to deny network, provider SDK, subprocess, shell,
   dynamic execution, unsafe decimal/float shortcuts, and M9-I4 activation paths; and
9. return a strict validation result whose `passed: true` is impossible with any finding.

A coordinated mutation that updates downstream hashes must still fail when it changes a registry
hash, tag, concept, value, unit, scale, sign, context, period, edge, accession, decision, source
reference, calculation, tolerance, finding, quality state, or network/authority marker.

## 17. Required adversarial offline implementation tests

A later implementation candidate must include:

- exact concept count/order/registry-hash and duplicate/missing/unknown mapping tests;
- coherent kind/unit/period retyping and duplicate-priority representation tests;
- unknown namespace, taxonomy-version mix, custom-tag auto-map, label injection, calculation-link
  spoofing, and cross-issuer decision-reuse tests;
- exponent/locale/leading-zero/negative-zero/trailing-zero, non-finite, overflow, excessive-
  precision, scale-twice, wrong-unit, foreign-currency, and sign-flip tests;
- instant/duration, date order, day-count, fiscal-calendar, 52/53-week, stub, missing-quarter,
  overlap/gap, cycle, orphan edge, and TTM/YTD mutation tests;
- amendment lineage, mixed accession, duplicate context/value, stale filing, and coordinated-rehash
  tests;
- missing-as-zero, older-period fill, peer/forecast/LLM fill, unauthorized override, partial-
  completeness, and severity-downgrade tests;
- acquisition/disposal/discontinued-operation/lease/minority/other-claim separation tests;
- split effective-date, factor positivity, double adjustment, weighted-versus-instant shares, and
  inferred-price-split denial tests;
- every reconciliation/tolerance/quality invariant and absent-check tests;
- negative/overlong tolerance, non-applicable-check, and partial-`complete` bypass tests;
- safe-error redaction, raw-label/URL/body/stack/credential leakage tests;
- independent arithmetic, graph, reconciliation, reference closure, AST/import, and subprocess/
  shell/dynamic-execution denial tests; and
- complete M1-M9-I4 regressions with network denied, no credentials, no real data, and Python
  3.10/3.12 CI.

## 18. Proposed implementation footprint — separately authorized later

A future disabled-offline implementation review may consider:

```text
tools/retail_data/gaap_contracts.py
tools/retail_data/gaap_mapping.py
tools/retail_data/period_graph.py
tools/retail_data/normalization.py
tools/retail_data/reconciliation.py
tools/validate_m9_i5_normalization.py
benchmarks/fixtures/m9_i5/*.json
tests/unit/test_m9_i5_*.py
tests/integration/test_m9_i5_*.py
```

These paths are informative, not authorized. No third-party runtime dependency is approved. No
implementation may import or call `sec_adapters`, modify a registry, use a network package, or
accept a provider response outside an exact synthetic snapshot fixture.

## 19. Contract acceptance gates

The contract may be recommended for exact-SHA review only when:

- all five schemas are valid Draft 2020-12, strict, versioned, bounded, and network denied;
- the exact 13 concepts, mapping/custom-tag rules, decimal/unit/sign semantics, period/amendment
  graph, derivations, corporate actions, reconciliations, findings, and quality states are locked;
- frozen provider/concept registries and M8/M9 input schemas remain unchanged;
- no runtime module, registry instance, fixture payload, real-company material, network/provider
  capability, or final handoff is added;
- focused adversarial contract regressions, all repository validators/policy, `git diff --check`,
  and the complete test suite pass; and
- the candidate remains unstaged, uncommitted, unpushed, and unpublished pending separate
  authorization.

## 20. Governance and later decisions

This document contains no mutable reviewer verdict or owner approval. Review applies only to the
SHA-256 of these exact UTF-8 bytes and the named exact baseline. Any byte change supersedes review.
Contract review, owner approval, staging, commit, push, Draft PR, implementation authorization,
M9-I6 authorization, live readiness, provider/license approval, and release are distinct decisions.

Missing, contradictory, unqualified, hash-mismatched, or wrong-baseline review evidence leaves the
contract a candidate. Same-maintainer commentary must not be described as independent approval.
No contract state can waive later qualified financial, legal, privacy, security, accessibility,
provider-license, operational, or release review.

## 21. Explicit exclusions

- No mapper, period engine, normalizer, reconciler, independent validator, runtime dependency, or
  final `normalized-financials` handoff implementation.
- No adapter, transport, DNS, socket, HTTP client, provider SDK, credential, actual User-Agent,
  provider activation, live request, or provider-registry/right change.
- No real company, ticker, CIK, filing, accession, XBRL fact, provider response, captured fixture,
  PDF, ebook, private extract, attachment, or `project_sources/` use.
- No silent zero/peer/older-period/forecast/LLM fill, valuation assumption, user override, M9-I6,
  M10+, valuation, approval creation, stable API/CLI, LLM, UI, pilot, beta, or release.
- No stage, commit, push, Draft PR, Mark Ready, merge, branch deletion, or other publication action.

## Source boundary

No attached PDF, original extract, continuous source text, private-source content, real issuer
data, captured provider response, credential, or live external request was read or used to prepare
this candidate.
