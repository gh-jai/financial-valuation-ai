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
adapter contract lock was subsequently merged through PR #30; it is contract-only and grants no
implementation or live-data authority. These post-M7 checkpoints do not advance the current
operational implementation milestone beyond M7.

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
and 3.12 job at the exact main commit. This is contract evidence only: M9-I4 adapters, injected
transport, limiter, retry, circuit-breaker, cache, fixtures, and independent validator have not
been implemented. The frozen M9-I2 contract remains
`owner_approved_with_exception`; the disclosed single-maintainer path does not claim independent
human or GitHub platform approval and does not weaken M1-M7 runtime separation or later qualified
review gates.

The previously attested synchronized M9-I2 documentation snapshot `eb726009…de705` remains exact
`CLOSED_WITH_SINGLE_MAINTAINER_EXCEPTION` evidence. Synchronizing the M9-I4 post-merge facts changes
three files in that subject set, so the resulting current snapshot is fail-closed as `NOT_CLOSED`
pending its own immutable subject commit, exact-head CI, findings disposition, and new
snapshot-closure attestation. The preserved manifests and attestation evidence remain in
`docs/milestones/M9-I2-post-owner-approval-snapshot-closure.md`. M9-I4 implementation, M9-I5 through
M9-I6, live SEC or provider access, provider activation, real-company fixtures, normalization, API,
LLM, UI, and release work remain separately unauthorized. The next bounded checkpoint is a
separately authorized M9-I4 disabled offline implementation; it must use only original synthetic
fixtures and an injected network-denied transport and must not perform a live request.

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
