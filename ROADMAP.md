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
only the separately approved M9-I1 offline primitives are now a publication candidate.

## M9 Public data ingestion and accounting normalization

Implement ticker/CIK resolution, SEC and licensed market-data adapters, immutable snapshots, manual import, US-GAAP normalization, reconciliation, data-quality findings, and offline provider fixtures.

Planning status: Reviewed, approved, and merged through PR #19. The planning baseline divides
implementation into six separately approved offline-first slices, keeps every adapter disabled by
default, and requires a separate live-readiness approval.

Implementation status: M9-I1 implementation baseline approved for publication. It adds errors,
redaction, canonical JSON/SHA-256, independent recomputation, and strict provider/license and
concept registries without transport or provider payloads. M9-I2 through M9-I6 remain unauthorized,
and live SEC or provider access remains unauthorized.

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
