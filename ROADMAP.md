# Roadmap

## M0 Repository Foundation

Establish governance, legal boundaries, directory conventions, core schemas, ontology seeds, templates, validators, tests, and a synthetic vertical slice.

## M1 One-book vertical slice

Process one lawfully accessed private source end to end: metadata, scoped claims, reviewed knowledge, one skill, one workflow, and benchmark coverage. No source text is distributed.

## M2 Narrative-to-numbers integration

Connect business narratives, accounting signals, operating drivers, forecast assumptions, and valuation mechanics with explicit uncertainty and evidence trails.

## M3 Young-company survival-adjusted valuation

Add young-company classification, top-down and bottom-up forecasting, NOL and reinvestment controls, time-varying rates, discrete survival adjustment, and controlled equity bridges.

## M4 Growth-company scaling and fade

Add current-base normalization, revenue scale and fade, margin convergence, segment-specific reinvestment, implied-return checks, risk convergence, stable-state terminal rebuild, and bounded failure and equity handoffs.

## M5 Distress decline and contingent survival

Extend life-cycle routing to declining and distressed operating paths while keeping default, recovery, financing, and claim effects separate.

## M6 Cycle-aware judgment layer

Add bounded cycle evidence, scenario implications, price-versus-value review, contradiction handling, and decision-audit benchmarks without creating a market-timing signal.

## M7 Agentization

Define constrained agent roles, tool contracts, prompt suites, evaluator policies, handoffs, and human approval controls.

## M8 Retail product contract and safety boundary

Define the supported retail user and issuer scope, five real-data interface schemas, safe-stop behavior, data and output policies, threat model, provider/legal/security review gates, and the pilot/holdout design. M8 is contract-only and does not add live data, LLM, API, CLI, or Web implementation.

Status: Cross-functional design review complete. The project owner authorized M9 implementation
planning with the seven recorded conditions on 2026-08-08. The M9 planning baseline is merged;
the separately approved M9-I1 offline foundation was subsequently reviewed, hardened, validated,
and merged through PR #20. The bounded synthetic offline M9-I2 issuer resolver and M9-I3 immutable
storage/manual-import slice were subsequently merged through PRs #24-#26. The M9-I4 disabled SEC
adapter contract lock was merged through PR #30, followed by the disabled offline implementation
through PR #32. It remains network-denied and grants no live-data authority. The M9-I5
disabled-offline US-GAAP normalization and reconciliation contract lock was merged through PR #36
as `98536ff27a80bd8ddb4dd9e651ca7217c1c0d582`; it adds no normalization runtime. These post-M7
checkpoints do not advance the current operational implementation milestone beyond M7.

## M9 Public data ingestion and accounting normalization

Implement ticker/CIK resolution, SEC and licensed market-data adapters, immutable snapshots, manual import, US-GAAP normalization, reconciliation, data-quality findings, and offline provider fixtures.

Planning status: Reviewed, approved, and merged through PR #19. The planning baseline divides
implementation into six separately approved offline-first slices, keeps every adapter disabled by
default, and requires a separate live-readiness approval.

Implementation status: The bounded M9-I1 offline foundation is merged through PR #20 as
`7b2b2d2481a6a95e76156fedf39975381811fdea`. M9-I2's bounded synthetic offline issuer-resolution
implementation was reviewed, remediated, validated, and merged through PR #24 as
`3ea93c8751bfaa558d3597a91b978f986dac6412`; PR #25 then merged its completion carrier as
`58a6031427ace8ce61b48884753ca732943ea2ca`. M9-I3's bounded offline immutable store and safe manual
JSON/CSV import were reviewed, remediated, validated, and merged through PR #26 as
`c4dcf9ef4780249f7a9a3a12a515cf4e07ce64b3`. Validate run #81 passed every Python 3.10 and 3.12
job at the exact M9-I3 head. M9-I4's disabled SEC adapter contract lock was reviewed, remediated,
and merged through PR #30 as `e26f55ef3e9b8babecb42f41f25be20dd918ea1e`. Formal same-maintainer
review recorded `COMMENTED_PASS` at exact head
`587fa892cefb1397c7854c93698799fa88e18f8e`; post-merge Validate run #92 passed every Python 3.10
and 3.12 job at the exact main commit. M9-I4's disabled offline implementation was then formally
reviewed, remediated, and merged through PR #32 as
`c8c1b7bb5b8f63a77ea933e4c68c800e1fa0cbb1`. Same-maintainer review recorded
`COMMENTED_PASS` at exact head `e5055afe312f7d83341eda2a172300a6a0f5bddb`; post-merge Validate
run #96 (`31700614399`) passed every Python 3.10 and 3.12 step with 505 tests per job. Four disabled
adapters, injected network-denied synthetic replay, limiter/retry/timeouts/breaker, tamper-evident
cache references, locked original fixtures, and an independent validator are implemented. Public
adapters still stop before transport. The frozen M9-I2 contract remains
`owner_approved_with_exception`; the disclosed single-maintainer path does not claim independent
human or GitHub platform approval and does not weaken M1-M7 runtime separation or later qualified
review gates.

M9-I5 contract-lock evidence is anchored to PR #36: reviewed exact head
`c4715930a59b6e2f79000cffdb7c0ebbec7cf217`, merge commit
`98536ff27a80bd8ddb4dd9e651ca7217c1c0d582`, and byte-identical reviewed/merged tree
`a10327d7057c3478a38c9230667bc0529ceb6c21`. Same-maintainer review #4930291093, node
`PRR_kwDOTqKoFc8AAAABJd5FlQ`, recorded `COMMENTED_PASS` with no findings and is not independent
approval. Validate #103 (`31728378287`) passed jobs `94542365764` (Python 3.10) and `94542365886`
(Python 3.12); post-merge Validate #104 (`31730656034`) passed jobs `94550030252` (Python 3.10) and
`94550030257` (Python 3.12). Each job completed the 526-test suite. The exact contract SHA-256 is
`99ee481383eece5d21f45e22dc2ced16f3e04f3bd8ae169ac7c58279c8121949`.

The separately authorized M9-I5 disabled-offline runtime was reviewed and merged through PR #40.
Reviewed exact head `8a864a71b28ee67d579fc946ec82abc07db0e125` and merge commit
`1bfe3707b0b0fd6302f9f212894c9a0afa8254e2` share tree
`c709b3231a740c9815e9e24b5dca27b1b6bb8fa0`. Same-maintainer review #4942961896, node
`PRR_kwDOTqKoFc8AAAABJp-c6A`, recorded `COMMENTED_PASS` with no findings and is not independent
approval. Validate #111 (`31867065910`) passed jobs `94969739732` (Python 3.10) and `94969739789`
(Python 3.12); post-merge Validate #112 (`31867408735`) passed jobs `94970557404` (Python 3.10) and
`94970557341` (Python 3.12) at the exact merge commit. Each job completed the 585-test suite.

The exact M9-I5 contract-lock status snapshot
`126ad4fc548b897546ebe9c09832b3e79283bab5fae860be3a264b6c30055980` remains
`CLOSED_WITH_SINGLE_MAINTAINER_EXCEPTION` evidence only for its original exact bytes. Synchronizing
the M9-I5 runtime post-merge facts changes the three summary subjects, so these new bytes form a
distinct current snapshot that is fail-closed as `NOT_CLOSED` pending its own immutable subject
commit, exact-head CI, findings disposition, and closure attestation. The preserved manifests and
attestation evidence remain in `docs/milestones/M9-I2-post-owner-approval-snapshot-closure.md`.
The merged runtime is limited to repository synthetic fixtures and remains network-denied. M9-I6,
live SEC or provider access, provider/network activation, real-company data, API, LLM, UI, and
release work remain separately unauthorized. The next separately gated implementation slice is
M9-I6's offline end-to-end validator; it remains unauthorized and cannot weaken those boundaries.
The earlier M9-I4 implementation status snapshot
`8996b5c370576a09b556823ed61e5f025f8640aa2c9d061e29895e9384886f9d` likewise remains closed
evidence only for its original exact bytes.

## M10 Assumption, routing, and scenario engine

Implement transparent WACC and operating assumptions, lifecycle routing, stable-state controls, bear/base/bull scenarios, provenance-preserving overrides, and deterministic stop rules.

## M11 Governed real-case runtime and stable interfaces

Expose one domain service through a stable Python API, CLI, and service API. Extend M7 from one synthetic allowlisted fixture to schema-valid, content-addressed, human-approved real cases without weakening exact-hash gates or role separation.

## M12 Retail Web experience and explainable reports

Build the Traditional Chinese-first Web journey, source/formula inspection, assumption editing, approvals, range/sensitivity explanations, and share-safe PDF/JSON exports to WCAG 2.2 AA.

## M13 Real-company pilots and product hardening

Validate eight development pilots and at least two holdouts, independently reconcile identical-assumption values, test data and advice mutations, complete accessibility/usability review, and close security, privacy, and licensing findings.

## M14 v1.0 release and operations

Freeze schemas and stable interfaces only after all launch gates pass. Complete documentation, migrations, SBOM, incident/rollback/restore drills, closed beta, go/no-go review, and then tag `v1.0.0`. A failed gate permits beta only, not a retail-ready claim.
