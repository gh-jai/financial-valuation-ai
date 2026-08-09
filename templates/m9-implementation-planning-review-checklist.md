# M9 Implementation Planning Review

Plan: `docs/milestones/M9-public-data-ingestion-normalization-plan.md`
Status: Planning baseline merged; M9-I1 separately authorized and approved
Planning authorization: Project owner, 2026-08-08
Planning baseline approval: Project owner, 2026-08-08
Baseline: `e6a791a827a2a37457494ae0b184d3a37f3040a3`

## Scope and milestone boundary

- [x] M9 ends at an independently validated normalized-financials handoff to M10.
- [x] Valuation, assumptions, routing, API, CLI, Web, report rendering, LLM calls, beta, and release remain excluded.
- [x] Planning authorization is not represented as implementation or live-network authority.
- [x] The six slices `M9-I1` through `M9-I6` each have a deliverable, network state, and exit evidence.

## Product and financial data

- [x] Issuer ambiguity requires explicit human selection; no silent ticker/CIK choice is allowed.
- [x] The M8 issuer-support matrix is applied before acquisition and cannot route unsupported cases to another method.
- [x] The initial concept set is limited to existing M1-M6 FCFF and equity-bridge inputs.
- [x] Period, unit, currency, amendment, split, custom-tag, corporate-action, and completeness reconciliations are explicit.
- [x] Missing material inputs never become zero, stale values, peer values, or model estimates silently.

## Data governance and licensing

- [x] Provider, license, concept, freshness, and error registries are versioned and default deny.
- [x] Storage, display, export, redistribution, attribution, retention, territory, and field rights are evaluated separately.
- [x] Raw records are immutable and content addressed; canonicalization is versioned and independently recomputed.
- [x] Real provider data, private sources, credentials, and user uploads are absent from repository fixtures.
- [x] All `M8-C01` through `M8-C07` remain visible with their original blocking actions.

## Security and operations

- [x] Only the disabled data-gateway adapter boundary may ever receive allowlisted outbound access.
- [x] CI and default local tests remain offline and credential-free.
- [x] SSRF/redirect/private-address, traversal/symlink, CSV formula, size, malformed-data, secret-redaction, rate, cache, and replay tests are planned.
- [x] Provider activation requires an exact, separately approved live-readiness checkpoint and kill switch.
- [x] Executor and validator implementations remain separate.

## Engineering and verification

- [x] Package boundaries prevent provider payload shapes from leaking into normalized domain objects.
- [x] Added dependencies require documented need, bounded versions, license/security review, and approval.
- [x] Every accepted output is deterministic for identical inputs and registry versions.
- [x] Schema, unit, integration, adversarial, mutation, regression, and Python 3.10/3.12 CI gates are defined.
- [x] An implementation review record and cross-functional sign-off are required before M9 completion.

Planning recommendation:
`[x] approve baseline  [ ] request changes  [ ] reject`

Review conclusion: Approved on 2026-08-08. This planning approval accepts the planning baseline for
publication; it does not authorize `M9-I1`, any later implementation slice, or live-network access.
M9-I1 subsequently received separate implementation and publication decisions recorded in
`docs/milestones/M9-I1-implementation-review.md`.

Separate implementation decision:
`[x] authorize M9-I1 implementation  [ ] request further planning`
