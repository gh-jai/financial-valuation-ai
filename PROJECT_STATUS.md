# Financial Valuation Intelligence — Project Status

Last updated: 2026-08-12

Repository: `gh-jai/financial-valuation-ai`

## Current state

**Current operational implementation milestone: M7 — Governed agentization.**

M7 remains the latest complete end-to-end implementation milestone.

The repository has merged eight implementation milestones through delivery PR #16:

- M0 — Repository foundation
- M1 — Basic FCFF DCF vertical slice
- M2 — Narrative-to-Numbers vertical slice
- M3 — Young-company survival-adjusted valuation vertical slice
- M4 — Growth-company scaling-and-fade vertical slice
- M5 — Decline, distress, and contingent-survival vertical slice
- M6 — Cycle-aware judgment layer
- M7 — Governed agentization and human-gated orchestration

The M4 contract and repository-wide implementation were delivered through PR #10. The implementation includes the locked source boundary and 30 claims, seven Knowledge artifacts, nine Skills, `WFL-GRW-001`, a strict schema, deterministic engine, independent recomputation validator, two synthetic benchmarks, adversarial controls, and CI/pre-commit integration. Final review hardened registered bidirectional traceability and independent recomputation of market scale, capacity utilization, calculation trails, sensitivity points, and supported break-even values.

The M5 contract was approved and merged through PR #12, and the repository-wide implementation was delivered through PR #13. Its locked boundary is Chapter 12, printed pages 397-436 / PDF pages 445-484, with 32 reviewed atomic claims. Final review hardened partial-liquidation routing, bidirectional divestiture support, turnaround probability dating, and the one-bridge rule. The full suite reports 179 passing tests, and the Python 3.10/3.12 matrix passes.

M6 contract-first planning, source-fidelity/financial review, repository-wide implementation, and publication are complete. The implementation preserves the dual-source boundary and 36 reviewed claims, adds eight Knowledge artifacts, ten Skills, `WFL-CYC-001`, a strict schema, deterministic engine, independent validator, two synthetic benchmarks, 54 focused tests, and CI/pre-commit integration. PR #14 passed the Python 3.10/3.12 matrix and merged as `f4175ee`; the post-merge Actions run also passed. The complete merged suite reports 242 passing tests.

M7 governed agentization is complete and merged through PR #16. It adds 20 reviewed claims, four Knowledge artifacts, five Skills, five agents, five prompts, `WFL-AGT-001`, five strict schemas, a deny-by-default registry, exact-hash handoffs, two human-only approvals, append-only events, executor/reviewer separation, offline adapters, independent validation, and three synthetic governance benchmarks. PR #16 Actions run #48 passed on Python 3.10 and 3.12 and merged as `75503192255053bffa42f2a2debe9a2668fe6f96`. The merged suite reports 275 passing tests.

P0 publication-state synchronization and the M8 cross-functional design review are complete. These
are post-M7 product and governance checkpoints, not a new complete end-to-end operational
milestone. The M9 planning baseline was merged through PR #19 as `d129d3e`; M9-I1 was merged through
PR #20 as `7b2b2d2`. M9-I2's bounded synthetic offline issuer-resolution implementation was merged
through PR #24 as `3ea93c8`, and its completion carrier was merged through PR #25 as `58a6031`.
M9-I3's bounded offline immutable store and safe manual JSON/CSV import were merged through PR #26
as `c4dcf9e`. The complete merged suite at the M9-I3 exact head reports 425 passing tests, and
Validate run #81 passed on Python 3.10 and 3.12. These slices still do not form the complete M9
ingestion/normalization handoff, so the project current operational state remains M7.

The revised M9-I2 contract defines a narrowly scoped single-maintainer documentation-governance
exception without weakening runtime separation or later qualified-review gates. Its immutable
events close only the historical exact documentation snapshot
`1c3754e724f98ff8324c567237070b68fe20514e678de3d1787e51d47f9da918`. Synchronizing the current
post-merge state changes three files in that historical subject set, so the new status snapshot is
fail-closed as `NOT_CLOSED` until it receives its own immutable subject commit, exact-head CI,
findings disposition, and closure attestation. Both manifests and the current evidence assessment
are preserved in `docs/milestones/M9-I2-post-owner-approval-snapshot-closure.md`. Qualified
legal/compliance, provider-license, privacy, security, accessibility, live-provider, and
real-company evidence remain later gates.

State terms used below are intentionally distinct:

- **Current operational state:** M7 is the latest complete end-to-end implementation milestone.
- **Merged post-M7 checkpoints:** M8's contract/review, the M9 planning baseline, M9-I1's bounded
  offline foundation, M9-I2's synthetic offline issuer resolution, and M9-I3's immutable local
  storage/manual import are on `main`; they do not yet form the complete M9 handoff or advance the
  current operational state.
- **Frozen M9-I2 contract:** the revised issuer-resolution contract defines a bounded
  single-maintainer documentation-governance exception. Its exact SHA-256 is authoritative in the
  review/approval record. Its governance state is `owner_approved_with_exception`; the bounded
  offline implementation is merged without granting any live-data authority.
- **Historical package closure:** exact snapshot `1c3754e7…a918` remains
  `CLOSED_WITH_SINGLE_MAINTAINER_EXCEPTION`; its immutable events and subject hashes are historical
  evidence and are not rewritten.
- **Current status-snapshot reclosure:** `NOT_CLOSED`. The authoritative current manifest and
  evidence assessment are in
  `docs/milestones/M9-I2-post-owner-approval-snapshot-closure.md`.
- **Unauthorized:** M9-I4 through M9-I6, live SEC/provider access, provider activation,
  real-company acquisition, normalization, and every later product or release capability.

Current mainline architecture:

```text
Evidence
→ Narrative
→ 3P Review
→ Value Drivers
→ Life-cycle Routing / Scaling / Decline / Reinvestment / Risk Fade
→ FCFF Inputs
→ Going-concern DCF
→ Optional Survival / Distress-sale Adjustment
→ Equity and Claim Bridge
→ Per-share Value
→ Optional Dated Cycle Judgment Overlay
→ Feedback Revision
→ Exact-hash Human-Gated Agent Review and Memo
```

The merged M9-I1 through M9-I3 slices add this bounded offline path before any provider adapter or
accounting normalization:

```text
Safe structured errors and bounded redaction
→ Versioned canonical JSON/SHA-256
↔ Implementation-separated canonical hash recomputation
→ Immutable default-deny provider/license and concept registries
→ Synthetic issuer candidates and exact-hash human selection
→ Verified issuer identity and structural data-review eligibility
→ Safe local JSON/CSV import and content-addressed write-once storage
→ Source snapshot and exact-reference manifest
↔ Implementation-separated storage-graph validation
```

The project remains pre-v1.0 and is not investment advice.

## Milestone summary

### M0 — Repository foundation

Status: Complete and merged

Merge commit: `327fd2b84d83d4838084123c0ed42ba070204fee`

Delivered:

- Repository governance and contribution conventions
- Provenance-aware schemas and templates
- Source catalog and source-map structure
- Knowledge, Skill, Workflow, benchmark, and test conventions
- Repository content and copyright policy
- Validation tooling
- Pre-commit integration
- GitHub Actions CI
- Synthetic sample artifacts

### M1 — Basic FCFF DCF

Status: Complete and merged

Merge commit: `3d795efd3a35f8576496ec539bc21713ab03dfd8`

Primary source:

- `SRC-DAMODARAN-LBV-2024`

Delivered:

- Reviewed FCFF valuation claims
- Sourced Knowledge artifacts
- Bounded valuation Skills
- `WFL-VAL-001` standard-company valuation workflow
- Deterministic FCFF forecasting and DCF engine
- Period-specific and cumulative discounting
- Terminal-value controls
- Enterprise-to-equity bridge
- Sensitivity and calculation-trail requirements
- Synthetic benchmarks and regression tests

### M2 — Narrative-to-Numbers

Status: Complete and merged

Merge commit: `c2c5f5e34f1b9b04e484f03b8bb88d5b2e185197`

Primary source:

- `SRC-DAMODARAN-NARRATIVE-NUMBERS-2017`

Source boundary:

- Chapters 6–10
- Printed pages approximately 70–166
- Break, change, and shift taxonomy extends into printed pages 167–183

Delivered:

- 24 reviewed atomic claims
- Six Knowledge artifacts
- Eight bounded Skills
- `WFL-NAR-001` narrative-to-numbers workflow
- Evidence-backed narrative assertions
- Possibility, plausibility, and probability review
- Value-driver mapping
- Separate alternative narratives and valuations
- Feedback revision history
- Two deterministic synthetic benchmarks
- Narrative validators and regression coverage

M2 composition:

```text
Evidence
→ Narrative
→ 3P Review
→ Value Drivers
→ FCFF Inputs
→ WFL-VAL-001
→ Alternative Values
→ Feedback Revision
```

### M3 — Young-company survival-adjusted valuation

Status: Complete and merged

Merge commit: `d9f85c917b4729caf81a4171c249f52e3c194411`

Primary source:

- `SRC-DAMODARAN-DARK-SIDE-2018`

Source boundary:

- Chapter 9, “Baby Steps: Young and Start-Up Companies”
- Printed pages 259–321
- Chapter 10 begins on printed page 323 and is outside M3

Delivered:

- 30 reviewed atomic claims
- Seven Knowledge artifacts
- Nine bounded Skills
- `WFL-YNG-001` young-company workflow
- Young-company classification
- Top-down and bottom-up revenue forecasting
- Margin convergence
- Net operating loss carryforward
- Reinvestment and reinvestment-lag handling
- Time-varying discount-rate paths
- M1-composed going-concern FCFF valuation
- Deterministic survival/failure adjustment
- Key-person separate-scenario control
- Controlled pre-money and post-money equity bridge
- Employee-option and other-claim deductions
- Financing authorization, retention, and share-count controls
- Negative-FCFF dilution double-counting prevention
- Two deterministic synthetic benchmarks
- Full cross-field recomputation validator
- M1 and M2 regression tests

M3 composition:

```text
WFL-NAR-001
→ Young-company Classification
→ Forecast-method Selection
→ Revenue Forecast
→ Margin / NOL / Reinvestment
→ Time-varying Discount Rates
→ WFL-VAL-001 Going-concern DCF
→ Failure Scenario
→ Survival Adjustment
→ Equity and Claim Bridge
→ Per-share Value
→ M2 Feedback Revision
```

Core survival formula:

```text
Adjusted operating value
= Survival probability × Going-concern operating value
+ Failure probability × Failure value
```

Core risk separation:

- Operating and going-concern risk belongs in forecast cash flows and period-specific discount rates.
- Discrete failure risk belongs in failure probability, survival probability, and failure value.
- Key-person risk requires a separately valued operating scenario.
- The same failure exposure must not be embedded in both discount rates or FCFF and the survival adjustment.

Human review strengthened M3 so that the validator recomputes:

- FCFF
- Cumulative discount factors
- Terminal value
- Going-concern operating value
- Survival and failure components
- Failure-adjustment delta
- Pre-money common equity
- Post-money common equity
- Per-share value

The equity contract also requires that financing proceeds be authorized and retained, and that any post-money per-share denominator include shares issued in the financing round.

### M4 — Growth-company scaling and fade

Status: Complete and merged

Merge commit: `d8fec65ce1b1edbde733d74fc42b6bdb3837a64d`

Primary source:

- `SRC-DAMODARAN-DARK-SIDE-2018`

Approved source boundary:

- Chapter 10, “Shooting Stars: Valuing Growth Companies”
- Printed pages 323–357
- PDF pages 371–405 in the reviewed private edition

Approved contract artifacts:

- `docs/milestones/M4-growth-company-scaling-and-fade-contract.md`
- `extraction/manifests/M4-growth-company-scaling-and-fade.yaml`
- `extraction/reviewed/M4-growth-company-scaling-and-fade-claims.yaml`
- `templates/m4-growth-company-review-checklist.md`

Completed implementation review:

- `docs/milestones/M4-implementation-human-review.md`

Delivered through PR #10:

- Seven `GRW-*` Knowledge artifacts covering all 30 reviewed claims
- Nine `SKL-GRW-*` Skills
- `WFL-GRW-001` growth-company scaling-and-fade workflow
- `schemas/growth-company-valuation.schema.json` with strict governed objects
- `tools/growth_company.py` for scale, margin, taxes, reinvestment, invested capital, implied ROC, FCFF, stable-state rebuild, M1 discounting, and optional M3 failure handoff
- `tools/validate_growth_company_valuations.py` for independent numeric and cross-field recomputation
- Asset-light platform and capacity-led expansion deterministic benchmarks
- Adversarial coverage for boundary, stale base, scale, reinvestment, capacity, margin, risk, terminal state, failure, dilution, and market-price controls
- M1–M3 composition regressions and local/CI validation integration

Acceptance evidence:

- Maintainer-approved implementation and human-review checklist
- Full local repository validators and regression suite
- Remote Python 3.10 and Python 3.12 CI on PR #10
- Final adversarial review fixes for traceability, market/capacity series, calculation trail, sensitivity, and break-even recomputation

### M5 — Decline, distress, and contingent survival

Status: Complete; final review approved for merge

Primary source:

- `SRC-DAMODARAN-DARK-SIDE-2018`

Approved source boundary:

- Chapter 12, “Winding Down: Declining Companies”
- Printed pages 397-436
- PDF pages 445-484 in the reviewed private edition
- Chapter 11 mature-company methods are outside the M5 boundary
- Chapter 13 begins on printed page 438 / PDF page 486

Approved contract artifacts:

- `docs/milestones/M5-decline-distress-contingent-survival-contract.md`
- `extraction/manifests/M5-decline-distress-contingent-survival.yaml`
- `extraction/reviewed/M5-decline-distress-contingent-survival-claims.yaml`
- `templates/m5-decline-distress-review-checklist.md`

Approved contract decisions:

- Classify decline reversibility independently from financial distress
- Route one of four reversible/irreversible and low/high-distress combinations
- Keep status-quo, turnaround, orderly-liquidation, and forced-sale alternatives separate
- Permit evidence-backed negative growth and negative reinvestment
- Reconcile divestiture proceeds with capital and operating contribution removed
- Apply deterministic distress probability once on a common declared valuation basis
- Require probability event, horizon, as-of date, and default-to-cessation mapping
- Reuse M1 DCF, M4 forecast consistency, and M3 survival arithmetic without changing their public contracts
- Exclude live data, statistical probability estimation, relative valuation, simulation, APV, and equity-as-option methods

Implementation delivered:

- Eight `DST-*` Knowledge artifacts covering all 32 reviewed claims
- Ten `SKL-DST-*` Skills and `WFL-DST-001`
- Strict `decline-distress-valuation.schema.json`
- Deterministic decline/distress engine and independent recomputation validator
- Negative-growth, negative-reinvestment, divestiture, financing, loss-limited tax-benefit, WACC, and closure controls
- Separate turnaround, orderly-liquidation, distress-sale, contingent-survival, and current-claim bridge calculations
- Irreversible/low-distress and reversible/high-distress deterministic benchmarks
- Adversarial mutation coverage and M1-M4 composition regressions
- Pre-commit and Python 3.10/3.12 CI integration

Acceptance evidence:

- 10 schemas, 10 sources, and 128 claims validate
- Two M5 valuation documents independently recompute
- Repository copyright policy passes with no private source content
- Full local suite: 179 passed
- Maintainer final review approved on 2026-08-02
- PR #13 final-head Actions run #42 passed on Python 3.10 and Python 3.12

### M6 — Cycle-aware judgment layer

Status: Merged through PR #14; local and remote validation complete

Primary sources:

- `SRC-DAMODARAN-DARK-SIDE-2018` for cycle-aware valuation-input methods
- `SRC-MARKS-MASTERING-MARKET-CYCLE-2018` for the non-numeric judgment overlay

Approved source boundary:

- Damodaran Chapter 13, printed pages 438-458 / PDF pages 486-506
- Marks Chapters I-III, VI-IX, and XII-XV, with Chapter XVIII used only as a summary cross-check
- Damodaran simulation, relative valuation, and natural-resource real-options sections are excluded
- Marks macro/policy forecasting, distressed-debt, real-estate, allocation, and trade instructions are excluded

Approved contract artifacts:

- `docs/milestones/M6-cycle-aware-judgment-layer-contract.md`
- `extraction/manifests/M6-cycle-aware-judgment-layer.yaml`
- `extraction/reviewed/M6-cycle-aware-judgment-layer-claims.yaml`
- `templates/m6-cycle-aware-judgment-review-checklist.md`

Implemented artifacts:

- Eight `CYC-*` Knowledge artifacts split across lifecycle, valuation, risk, and market-pricing domains
- Ten bounded `SKL-CYC-*` Skills
- `WFL-CYC-001-cycle-aware-judgment-layer.md`
- `schemas/cycle-aware-judgment.schema.json`
- `tools/cycle_aware.py`
- `tools/validate_cycle_aware_judgments.py`
- Established-cycle industrial and structural-break commodity synthetic fixtures
- Two expected benchmark outputs
- Engine, validator, benchmark, artifact-graph, adversarial, mutation, and composition tests
- CI and pre-commit validator integration
- `docs/milestones/M6-implementation-human-review.md`

Approved decisions:

- Keep the `valuation_input_handoff` separate from the `judgment_overlay`
- Route exactly one of normalized inputs, transition to normal, current expectations, or stop
- Require dated five-dimension evidence, counterevidence, staleness controls, and an indeterminate result
- Normalize the complete cycle-sensitive input vector rather than one earnings line
- Use deterministic scenario ranges without invented probabilities or Monte Carlo simulation
- Treat price relative to intrinsic value as an observation, never as an intrinsic-value input
- Keep discrete distress and forced-sale treatment exclusively in `WFL-DST-001`
- Produce only bounded human-review posture labels, never timing, trading, leverage, or sizing instructions

Implementation remains within the approved source boundary, all 36 reviewed claims, financial and evidence controls, schema invariants, benchmark designs, and review checklist. PR #14 validated the exact implementation tree on Python 3.10 and Python 3.12 before merge.

Acceptance and publication evidence:

- 11 schemas and 101 governed documents validate
- 10 source records, 10 source mappings, 164 atomic claims, and 172 Knowledge references validate
- Two M6 documents independently recompute
- Full local suite: 242 passed
- Maintainer checklist approved on 2026-08-02 after separating market-wide credit evidence from issuer-specific refinancing risk in Benchmark B
- Repository copyright policy and all-candidate pre-commit pass with no private source content
- PR #14 exact-head Actions run #44 passed on Python 3.10 and Python 3.12
- PR #14 merged to `main` as `f4175ee64212288862e37eba74c43b570f6d598a`
- Post-merge Actions run `31252836713` passed

### M7 — Governed agentization

Status: Complete and merged through PR #16

Merge commit: `75503192255053bffa42f2a2debe9a2668fe6f96`

Delivered:

- 20 reviewed atomic claims and four cross-domain Knowledge artifacts
- Five bounded agent Skills, five deny-by-default agents, and five versioned prompts
- `WFL-AGT-001` and `REG-AGT-001`
- Exact-hash artifacts, handoffs, and human-only `case_lock` / `output_approval`
- Append-only events, independently derived state, and stale-approval invalidation
- Executor/reviewer separation, per-agent and global action budgets, and offline allowlisted adapters
- Independent validation of schemas, hashes, state, traceability, budgets, tool authority, separation of duties, and prohibited output
- Happy-path, adversarial-stop, and approval-tampering synthetic benchmarks

Acceptance and publication evidence:

- 16 schemas, 121 governed documents, 184 reviewed claims, and three M7 run fixtures validated
- Full local suite: 275 passed
- All 16 pre-commit hooks passed without rewriting files
- PR #16 exact-head Actions run #48 passed on Python 3.10 and 3.12
- PR #16 merged to `main` as `75503192255053bffa42f2a2debe9a2668fe6f96`
- No private PDF, ebook, extract, secret, or live external call is a release dependency

### M8 — Retail product contract and cross-functional review

Status: Complete and merged through PR #18

Merge commit: `e6a791a827a2a37457494ae0b184d3a37f3040a3`

Delivered:

- Narrow retail user, issuer, territory, method, data, output, and advice boundaries
- Five strict draft interface schemas with safe-stop invariants
- Error/data/output policy, issuer support matrix, threat model, and pilot/holdout design
- Product, financial, data-governance, security, internal legal/data-perimeter, accessibility, engineering, and operations review
- Five closed contract defects and seven mandatory M9-M14 conditions

The review recommended M9 implementation planning with conditions. The project owner separately
authorized that planning on 2026-08-08; the decision did not authorize implementation or live data.

### M9 — Public data ingestion and accounting normalization

Status: Planning baseline and bounded offline M9-I1, M9-I2, and M9-I3 slices merged; revised M9-I2
exact-SHA contract is `owner_approved_with_exception`; operational state remains M7

M9-I1 merge commit: `7b2b2d2481a6a95e76156fedf39975381811fdea`
M9-I2 implementation merge commit: `3ea93c8751bfaa558d3597a91b978f986dac6412`
M9-I2 completion-carrier merge commit: `58a6031427ace8ce61b48884753ca732943ea2ca`
M9-I3 implementation merge commit: `c4dcf9ef4780249f7a9a3a12a515cf4e07ce64b3`

Planning artifact:

- `docs/milestones/M9-public-data-ingestion-normalization-plan.md`
- `templates/m9-implementation-planning-review-checklist.md`

Revised M9-I2 contract lock and governance record:

- `docs/milestones/M9-I2-issuer-resolution-contract-lock.md`
- `docs/milestones/M9-I2-contract-lock-review-approval-record.md`
- `docs/milestones/M9-I2-post-owner-approval-snapshot-closure.md`
- Contract SHA-256: `9326b6c76dcfe3061c5e356b5141d9f458d57694cb4e6b01b6470b0bf044d84e`
- Historical review/approval assertions: recorded on 2026-08-09 but not independently auditable
- Current exact-SHA contract governance state: `owner_approved_with_exception`
- Historical snapshot `1c3754e7…a918`: `CLOSED_WITH_SINGLE_MAINTAINER_EXCEPTION`
- Current synchronized status snapshot: `NOT_CLOSED` pending new immutable reclosure evidence;
  recompute and inspect both manifests in the exact-snapshot evidence assessment

The approved baseline ends M9 at an independently validated normalized-financials handoff. It divides
implementation into six separately approved slices covering primitives and registries, issuer
resolution, immutable storage/manual import, disabled SEC adapters, US-GAAP normalization and
reconciliation, and an offline end-to-end validator. All adapters remain disabled by default; live
readiness and each implementation slice require separate authorization.

M9-I1 delivers immutable safe errors, bounded redaction, canonical JSON/SHA-256,
implementation-separated hash recomputation, a strict provider/license registry, and the bounded
FCFF/equity-bridge concept vocabulary. M9-I2 adds deterministic synthetic issuer resolution,
exact-hash human selection, structural scope pre-screening, and an implementation-separated
validator. M9-I3 adds hostile-input-safe local JSON/CSV import, atomic content-addressed write-once
storage, deterministic snapshots/manifests, and independent graph validation. SEC entries remain
pending, all storage/display/export/redistribution rights are false, and `live_activation` remains
`disabled`. There is still no provider transport or payload, credential use, live request,
real-company fixture, accounting normalization, API, CLI, LLM, UI, or valuation behavior. M9-I4
through M9-I6 remain unauthorized.

## Current governed artifact graph

```text
Sources
→ Extraction Manifests
→ Reviewed Atomic Claims
→ Knowledge
→ Skills
→ Workflows
→ Schemas
→ Engines and Validators
→ Synthetic Fixtures
→ Expected Benchmark Outputs
→ Unit and Integration Tests
→ Governed Agents, Prompts, Handoffs, and Human Approvals
→ CI
```

Important workflow dependencies:

```text
WFL-NAR-001 → WFL-VAL-001
WFL-NAR-001 + WFL-VAL-001 → WFL-YNG-001
WFL-NAR-001 + WFL-VAL-001 + bounded WFL-YNG-001 handoff → WFL-GRW-001
WFL-NAR-001 + WFL-VAL-001 + bounded WFL-GRW-001/WFL-YNG-001 reuse → WFL-DST-001
WFL-NAR-001 + WFL-VAL-001 + bounded WFL-GRW-001/WFL-DST-001 reuse → WFL-CYC-001 treatment handoff → intrinsic valuation → separate judgment overlay
Approved M1-M6 route → WFL-AGT-001 exact-hash orchestration → independent review → human-approved memo
```

## Validation and CI

Latest merged change CI:

- GitHub Actions Validate run #62 for the PR #22 handoff-document synchronization
- Python 3.10: Passed
- Python 3.12: Passed

PR #22 merged the handoff-document synchronization as
`3945e90559ec2e10771489078c9e8f52036209b7`. It did not alter the operational implementation,
authorize M9-I2 runtime or later slices, or add live-data capability.

M9-I1 passed local validation, independent code/governance review, and PR #20 remote matrix
validation on Python 3.10 and Python 3.12 before merge commit `7b2b2d2`. This bounded offline
foundation does not change M7's status as the latest complete operational implementation milestone.

Validated controls include:

- Schema validity
- Source metadata integrity
- Atomic-claim and Knowledge references
- Narrative cross-references
- Probability reconciliation
- Failure-value basis consistency
- Survival-risk double-counting prevention
- FCFF and DCF recomputation
- Terminal growth and discount-rate constraints
- Reinvestment support for growth
- Revenue scale and market-share reconciliation
- Margin convergence and current-base normalization
- Invested-capital and implied-return recomputation
- Stable-state reinvestment and terminal-FCFF rebuild
- Capacity-holiday limits and resumption
- Negative-FCFF dilution controls
- Financing authorization and retention
- Post-money share-count consistency
- Explicit option and claim valuation
- Alternative narrative and claim-structure isolation
- Decline boundary and four-quadrant routing
- Negative reinvestment and divestiture reconciliation
- Face-debt, market-weight, interest-tax-benefit, after-tax debt-cost, and WACC recomputation
- Finite-life, stabilized-smaller-company, and negative-perpetuity closure controls
- Turnaround and orderly-liquidation alternative separation
- Distress event, horizon, recovery, common-basis, and one-bridge controls
- Cycle exposure, life-cycle, recurrence, structural-break, and treatment routing
- Evidence dating, staleness, availability, bidirectional references, and counterevidence
- Complete normalization, single-transition, driver-curve, carry, and scenario-isolation controls
- Scenario range and reviewed-probability controls
- Five-dimension alignment, confidence, extreme, and posture recomputation
- Intrinsic-value immutability, price-value ordering, and M5 distress separation
- Hidden-score, market-timing, trade-instruction, and excluded-method rejection
- Repository copyright policy
- Unit, integration, benchmark, and regression tests

At M3 completion, the full suite reported 88 passing tests. M4 and its final review fixes brought
the suite to 125. M5 brought the merged suite to 179 passing tests. M6 brought the merged suite to
242 passing tests, and M7 brought it to 275. The merged P0+M8 contract checkpoint added 10 contract
tests for 285; the cross-functional review added two conditional-schema regressions for 287. The
merged M9 planning baseline adds five planning-contract tests for 292. The merged M9-I1
implementation and review remediation add 33 offline primitive and governance tests for a total of
325. M9-I2's bounded issuer-resolution implementation and governance regressions bring the merged
suite to 382 tests. M9-I3's immutable storage/manual-import implementation, including the
time-closure regression, brings the exact-head suite to 425 tests without changing M1-M8 valuation
behavior. PR #19 planning CI, PR #20 Validate run #58, PR #24 Validate run #74, and PR #26 Validate
run #81 passed all validators, policy checks, and tests on Python 3.10 and 3.12.

## Source and copyright policy

Private PDFs must remain under:

```text
sources/private/
```

They must never be committed.

The repository must not contain:

- Source PDFs
- Raw source extracts
- Sequential source text
- Copied tables or figures
- Long quotations
- Private source material

Public artifacts must use original paraphrases, precise source locations, and explicit claim references.

## Current limitations

The repository does not yet provide:

- Live company or market-data ingestion
- Accounting normalization for real SEC filings
- Stable retail Python API, CLI, or service API
- Retail Web UI or PDF/JSON report renderer
- General real-case M7 routing beyond its allowlisted synthetic fixture
- Qualified legal/compliance approval for retail distribution
- Market-data display and redistribution approvals
- Autonomous investment recommendations
- Preferred-stock liquidation waterfalls
- Venture-capital ownership negotiation
- Monte Carlo simulation
- Decision-tree valuation
- Generalized real-options valuation
- Full relative-valuation implementation
- Statistical failure-probability estimation
- Automated extraction from private source PDFs

It also does not yet provide live issuer/data retrieval, M9-I4 disabled SEC adapter
implementations, M9-I5 normalization/reconciliation, or the M9-I6 end-to-end validator. M9-I2
issuer resolution and M9-I3 storage/manual import are bounded offline implementations using only
synthetic fixtures; they are not live ingestion capability.

M3 failure probabilities and recovery values are deterministic reviewed assumptions rather than statistical forecasts.

## Recommended next milestone

M8's internal review, the M9 planning merge, and the bounded M9-I1 through M9-I3 offline slices are
complete. The project current state remains M7 because no provider adapter, accounting
normalization, or end-to-end M9 data handoff exists. M9-I2 and M9-I3 are merged only for synthetic
offline operation; they authorize no live data, provider enablement, real issuer acquisition,
pilot, or report distribution. The frozen M9-I2 contract remains
`owner_approved_with_exception`. Its prior exact documentation snapshot remains historical
`CLOSED_WITH_SINGLE_MAINTAINER_EXCEPTION` evidence, while this post-merge status synchronization
creates a distinct current snapshot that remains `NOT_CLOSED` pending its own immutable reclosure
evidence.

The next bounded checkpoint is M9-I4 contract lock: define disabled-by-default SEC identity,
submissions, filings, and companyfacts adapters; synthetic transport fixtures; fixed endpoint and
network policy; deterministic limiting, bounded retry/backoff, timeouts, and circuit breaking;
tamper-evident caching; safe errors/redaction; and an implementation-separated validator. Contract
work must not activate a provider or perform a live SEC request. M9-I4 implementation requires a
later, separate authorization after contract review and owner approval.

Recommended sequencing:

```text
M7: Merged implementation and remote Python 3.10/3.12 validation complete
→ M8: Retail product and safety contract review complete
→ Conditional recommendation for M9 planning
→ Project-owner planning authorization complete
→ M9: Public-data ingestion and accounting-normalization planning baseline
→ Planning review and approval complete
→ M9-I1 bounded offline primitives reviewed, validated, and merged through PR #20
→ M9-I2 bounded synthetic offline issuer resolution merged through PR #24
→ M9-I2 completion carrier merged through PR #25
→ M9-I3 immutable storage/manual import merged through PR #26
→ Historical M9-I2 status snapshot remains closed evidence
→ Current post-merge status snapshot reclosure pending; current snapshot NOT_CLOSED
→ Current operational implementation state remains M7
→ Next: separately authorize and review the M9-I4 contract lock; no live request
```

M8 has locked:

- Supported and unsupported issuers and territories
- Five input/output interface schemas
- Data provenance, freshness, normalization, and error contracts
- Advice, privacy, retention, copyright, and provider-license boundaries
- Data/LLM/upload/report threat model
- Eight pilot and two holdout acceptance designs
- Product, financial, security, and internal legal/data-perimeter decisions

The seven conditions in `docs/milestones/M8-cross-functional-review.md` remain mandatory. In particular, M8 does not represent qualified legal advice, provider permission, privacy approval, implemented security controls, accessibility evidence, or successful real-company pilots.

## Working model

Recommended division of work:

```text
ChatGPT and maintainer review
→ Approved source boundary, claims, financial rules, schema contract, and review gates

Codex local implementation
→ Knowledge, Skills, Workflow, schema, engine, validator, benchmarks, tests, and CI integration

Publication review
→ Commit and PR authorization, exact-head remote CI, review-thread resolution, Ready, and merge
```

Codex should be used after the method, source, and financial-control contracts are locked.

## New-conversation handoff

Use this file as the canonical project handoff for a new ChatGPT or Codex session.

Minimum startup instruction:

```text
Read PROJECT_STATUS.md, README.md, ROADMAP.md,
docs/milestones/M8-retail-product-safety-contract.md,
docs/milestones/M9-public-data-ingestion-normalization-plan.md,
docs/milestones/M9-I2-issuer-resolution-contract-lock.md,
docs/milestones/M9-I2-contract-lock-review-approval-record.md,
docs/milestones/M9-I2-post-owner-approval-snapshot-closure.md,
and the existing M1-M7 workflows before proposing or implementing M9.

Do not alter completed milestone contracts without identifying a concrete defect.
Do not commit private source material.
Preserve composition with WFL-NAR-001, WFL-VAL-001, WFL-YNG-001,
WFL-GRW-001, WFL-DST-001, WFL-CYC-001, and WFL-AGT-001.
Do not treat draft M8 schemas as implemented ingestion or a retail-ready release.
Treat M9-I1 through M9-I3 only as merged bounded offline slices. The current operational
implementation state remains M7. Treat the revised M9-I2 contract lock at the exact SHA recorded in
its review/approval record as frozen and `owner_approved_with_exception`; never describe its
single-maintainer path as independent review. Preserve historical snapshot
`1c3754e724f98ff8324c567237070b68fe20514e678de3d1787e51d47f9da918` and its immutable events as
closed historical evidence. Treat the current post-merge status snapshot as `NOT_CLOSED` until its
own immutable reclosure evidence is complete; verify both manifests in the exact-snapshot closure
record. The next bounded checkpoint is M9-I4 contract lock. Do not infer M9-I4 implementation,
provider activation, live-network authority, normalization, or release authority from any contract
or closure state.
```
