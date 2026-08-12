# Financial Valuation Intelligence

Financial Valuation Intelligence (FVI) is an open, software-style framework for turning privately held financial valuation source materials into traceable claims, reusable knowledge, executable skills, repeatable workflows, prompts, and benchmarks. The repository contains original metadata, abstractions, and tooling—not source books or copied chapters.

## Repository philosophy

- Treat financial knowledge as versioned, testable artifacts.
- Preserve provenance from each claim to a precise private-source location.
- Separate sourced statements, derived rules, and model inferences.
- Prefer small Markdown and YAML artifacts governed by JSON Schema.
- Require human review for judgment-heavy valuation conclusions.
- Keep examples synthetic, minimal, and safe to redistribute.

## Legal and copyright boundary

Raw PDFs, ebooks, scans, and copyrighted extracts must never be committed. Private source files may be placed locally under `sources/private/`, which Git ignores. Only source metadata, compact factual citations, original paraphrases, and independently authored framework artifacts belong in the repository. See [CITATION_POLICY.md](CITATION_POLICY.md) and [NOTICE.md](NOTICE.md).

## Knowledge pipeline

```text
Source -> Claim -> Knowledge -> Skill -> Workflow -> Agent -> Prompt -> Test -> Release
```

Here, **Source** means the redistributable metadata record. A private local input may inform that record but remains outside version control. Every transformation should retain `source_refs`, declare dependencies, pass schema validation, and expose human-review checkpoints.

## Folder structure

| Path | Purpose |
|---|---|
| `sources/` | Redistributable source metadata; private inputs remain ignored |
| `schemas/` | JSON Schemas for governed artifacts |
| `ontology/` | Concepts, relationships, and aliases |
| `extraction/` | Manifests, maps, and staged original notes |
| `knowledge/` | Reviewed domain knowledge units |
| `skills/` | Bounded, reusable valuation capabilities |
| `workflows/` | Ordered combinations of skills and review gates |
| `agents/` | Governed agent role, authority, and handoff definitions |
| `prompts/` | System, task, and evaluator prompts |
| `agentization/` | Agent registry, tool allowlists, evaluator policy, and separation-of-duties controls |
| `registries/` | Versioned, default-deny M9 provider/license and bounded concept metadata |
| `templates/` | Authoring templates for consistent contributions |
| `benchmarks/` | Synthetic fixtures, expected results, and scoring rules |
| `tests/` | Schema, unit, integration, regression, and adversarial tests |
| `tools/` | Lightweight validation utilities |
| `docs/` | Extended project documentation |

## Milestone model

M0 established repository governance and provenance. M1-M6 added bounded deterministic valuation
and judgment vertical slices. M7 completes the governed `Workflow -> Agent -> Prompt -> Test` path
without granting agents autonomous approval, private-source, network, shell, or trading authority.
M8's cross-functional design review and the M9 planning baseline are merged. M9-I1 provides the
offline error, hashing, and default-deny registry foundation. M9-I2's bounded synthetic offline
issuer-resolution implementation and completion carrier are merged through PRs #24 and #25;
M9-I3's immutable store and safe manual JSON/CSV import are merged through PR #26. M9-I4's
disabled SEC adapter contract lock is merged through PR #30 as
`e26f55ef3e9b8babecb42f41f25be20dd918ea1e`; exact-head formal review recorded
`COMMENTED_PASS`, and main Validate run #92 passed on Python 3.10 and 3.12. M9-I4 remains
contract-only: no adapter, transport, fixture payload, cache runtime, provider activation, or live
request is implemented or authorized. These checkpoints do not advance the latest complete
end-to-end operational milestone beyond M7. The revised M9-I2 contract remains
`owner_approved_with_exception`, without weakening runtime separation or later qualified-review
gates. The previously attested synchronized documentation snapshot
`eb726009ac6afeebd5b15618ff03796c73790175f6360a3823f7c411dafde705` remains closed exact-snapshot
evidence; changing these three summary files for M9-I4 creates a new recomputable snapshot that is
`NOT_CLOSED` until separately committed, validated, reviewed, and attested. M9-I4 implementation,
M9-I5 through M9-I6, and every live-data capability remain separately gated. The authoritative
snapshot history and closure evidence are recorded in
`docs/milestones/M9-I2-post-owner-approval-snapshot-closure.md`, not by this summary. M9-M14 are the
retail-product delivery path; no live issuer ingestion or user interface exists. See
[ROADMAP.md](ROADMAP.md) and [PROJECT_STATUS.md](PROJECT_STATUS.md).

## Validate

Python 3.10 or newer is required.

```bash
python -m pip install -e ".[dev]"
python tools/validate_schemas.py
python tools/validate_sources.py
python tools/validate_claims.py
python tools/validate_narratives.py
python tools/validate_young_company_valuations.py
python tools/validate_growth_company_valuations.py
python tools/validate_decline_distress_valuations.py
python tools/validate_cycle_aware_judgments.py
python tools/validate_agent_runs.py
python tools/check_repository_policy.py
pytest
```

Run `pre-commit install` once to enable local checks. See [CONTRIBUTING.md](CONTRIBUTING.md) before adding artifacts.

## Implemented vertical slices

- M1: traceable basic FCFF DCF, enterprise-to-equity bridge, sensitivity review, structured output, and synthetic benchmarks.
- M2: evidence-backed narrative construction, 3P review, assertion-to-value-driver mapping, separate alternative valuations, and feedback revision composed with the M1 workflow.
- M3: young-company top-down and bottom-up forecasts, NOL and reinvestment handling, time-varying rates, discrete survival adjustment, and controlled pre/post-money equity bridges composed with M1 and M2.
- M4: growth-company revenue scaling and fade, margin convergence, segment-specific reinvestment, implied returns, risk convergence, stable-state terminal rebuild, and bounded M3 failure handoff composed with M1–M3.
- M5: declining-company routing, negative reinvestment and divestitures, financing and tax-benefit paths, closure alternatives, deterministic distress-sale adjustment, and one current-claim bridge composed with M1–M4.
- M6: company-specific cycle routing, complete-input normalization or current-expectations scenarios, dated five-dimension evidence, immutable intrinsic-value references, and bounded non-numeric review posture composed with M1–M5.
- M7: deny-by-default agent roles and prompts, exact-hash artifact handoffs, two human-only approval gates, executor-reviewer separation, offline allowlisted adapters, independent run validation, and three adversarial synthetic benchmarks composed with M1–M6.
- M8 reviewed contract: retail product scope, five real-data interface contracts, safe-stop policy, threat model, pilot/holdout gates, and seven mandatory later-stage conditions.
- M9 planning: reviewed and merged baseline for six separately approved public-data and
  normalization slices.
- M9-I1 merged foundation: immutable safe errors, bounded secret redaction, versioned canonical JSON
  and SHA-256, implementation-separated recomputation, strict provider/license policy, and a
  bounded concept vocabulary. Network transport, provider activation, real-company fixtures,
  normalization, API, LLM, and UI remain absent or unauthorized.
- M9-I2 merged bounded offline issuer resolution: deterministic synthetic candidate resolution,
  exact-hash human selection, structural scope pre-screening, implementation-separated validation,
  strict schemas, and adversarial regressions. The frozen contract remains
  `owner_approved_with_exception`; no independent-human or GitHub `APPROVED` review is claimed.
- M9-I3 merged bounded offline storage/manual import: hostile-input-safe local JSON/CSV parsing,
  atomic content-addressed write-once storage, deterministic source snapshots/manifests, strict
  time closure, and implementation-separated validation using synthetic fixtures only.
- M9-I4 merged contract-only checkpoint: four separately disabled SEC adapter capabilities, fixed
  endpoint/network policy, limiter/retry/timeout/breaker contracts, M9-I3-compatible 1 MiB storage
  closure, tamper-evident cache rules, synthetic fixture interfaces, safe errors, and
  implementation-separated validation requirements. PR #30 merged as
  `e26f55ef3e9b8babecb42f41f25be20dd918ea1e` after exact-head `COMMENTED_PASS`; main Validate run
  #92 passed. No M9-I4 runtime implementation or live authority is included.
- M9-I2 status snapshot: attested exact snapshot `eb726009…de705` remains
  `CLOSED_WITH_SINGLE_MAINTAINER_EXCEPTION` evidence. This M9-I4 status synchronization changes
  three subject files and therefore creates a distinct current snapshot that is `NOT_CLOSED`
  pending an immutable subject commit, exact-head CI, findings disposition, and closure attestation.

M9-I4 implementation, M9-I5 through M9-I6, live access, provider activation, and real-company data
remain unauthorized.

FVI remains pre-v1.0 and is not investment advice. Interfaces and schemas may change before release.
