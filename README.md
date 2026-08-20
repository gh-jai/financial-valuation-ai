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
contract lock was merged through PR #30, and its disabled offline implementation was subsequently
reviewed, remediated, and merged through PR #32 as
`c8c1b7bb5b8f63a77ea933e4c68c800e1fa0cbb1`. Exact-head formal review recorded
`COMMENTED_PASS`; post-merge Validate run #96 passed on Python 3.10 and 3.12 with 505 tests per job.
The implementation provides four capability-isolated adapters, an injected network-denied
synthetic replay harness, bounded resilience controls, tamper-evident cache references, and an
implementation-separated validator. Public adapters remain stopped before transport, and no
provider activation or live request is authorized. M9-I5's disabled-offline US-GAAP normalization
and reconciliation contract lock was then merged through PR #36 as
`98536ff27a80bd8ddb4dd9e651ca7217c1c0d582`. Its reviewed exact head
`c4715930a59b6e2f79000cffdb7c0ebbec7cf217` and merge commit have the byte-identical tree
`a10327d7057c3478a38c9230667bc0529ceb6c21`. Same-maintainer review #4930291093, node
`PRR_kwDOTqKoFc8AAAABJd5FlQ`, recorded `COMMENTED_PASS` with no findings; it is not independent
approval. Validate #103 (`31728378287`) passed jobs `94542365764` (Python 3.10) and `94542365886`
(Python 3.12), and post-merge Validate #104 (`31730656034`) passed jobs `94550030252` (Python 3.10)
and `94550030257` (Python 3.12), with 526 tests per job. The exact contract SHA-256 is
`99ee481383eece5d21f45e22dc2ced16f3e04f3bd8ae169ac7c58279c8121949`.
The separately authorized disabled-offline runtime was then reviewed and merged through PR #40 as
`1bfe3707b0b0fd6302f9f212894c9a0afa8254e2`. Reviewed exact head
`8a864a71b28ee67d579fc946ec82abc07db0e125` and the merge commit share tree
`c709b3231a740c9815e9e24b5dca27b1b6bb8fa0`. Same-maintainer review #4942961896, node
`PRR_kwDOTqKoFc8AAAABJp-c6A`, recorded `COMMENTED_PASS` with no findings and is not independent
approval. Validate #111 (`31867065910`) passed jobs `94969739732` (Python 3.10) and `94969739789`
(Python 3.12); post-merge Validate #112 (`31867408735`) passed jobs `94970557404` (Python 3.10) and
`94970557341` (Python 3.12) at the exact merge commit. Each job completed 585 tests. The runtime is
limited to repository synthetic fixtures and remains network-denied. These checkpoints do not
advance the latest complete end-to-end operational milestone beyond M7. The revised M9-I2 contract
remains `owner_approved_with_exception`, without weakening runtime separation or later qualified
review gates. The M9-I4 implementation status snapshot
`8996b5c370576a09b556823ed61e5f025f8640aa2c9d061e29895e9384886f9d` remains
`CLOSED_WITH_SINGLE_MAINTAINER_EXCEPTION` evidence only for its exact original bytes. The later
M9-I5 contract-lock status snapshot
`126ad4fc548b897546ebe9c09832b3e79283bab5fae860be3a264b6c30055980` is likewise closed only for
its original exact bytes. Changing the three summary files for this M9-I5 runtime post-merge
synchronization creates a distinct recomputable snapshot that is `NOT_CLOSED` until separately
committed, validated, reviewed, and attested. M9-I4 live readiness, M9-I6, provider/network
activation, real-company data, and every live-data capability remain separately gated. The
authoritative snapshot history and closure evidence are recorded in
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
- M9-I4 merged disabled offline implementation: four separately disabled SEC adapter capabilities,
  fixed
  endpoint/network policy, limiter/retry/timeout/breaker contracts, M9-I3-compatible 1 MiB storage
  closure, tamper-evident cache references, locked original synthetic fixtures, safe errors, and
  implementation-separated validation. PR #32 merged the remediated implementation as
  `c8c1b7bb5b8f63a77ea933e4c68c800e1fa0cbb1` after exact-head `COMMENTED_PASS`; main Validate run
  #96 passed on Python 3.10 and 3.12. Public adapters remain disabled and network-denied; no live
  authority is included.
- M9-I5 merged disabled-offline contract lock: PR #36 merged reviewed head
  `c4715930a59b6e2f79000cffdb7c0ebbec7cf217` as
  `98536ff27a80bd8ddb4dd9e651ca7217c1c0d582` after same-maintainer `COMMENTED_PASS`; Validate #103
  and post-merge Validate #104 passed all four Python 3.10/3.12 jobs with 526 tests per job. The
  exact contract SHA-256 is `99ee481383eece5d21f45e22dc2ced16f3e04f3bd8ae169ac7c58279c8121949`.
  That merge locked the contract only; runtime authority was granted separately.
- M9-I5 merged disabled-offline runtime: PR #40 merged reviewed exact head
  `8a864a71b28ee67d579fc946ec82abc07db0e125` as
  `1bfe3707b0b0fd6302f9f212894c9a0afa8254e2`, with byte-identical tree
  `c709b3231a740c9815e9e24b5dca27b1b6bb8fa0`. Same-maintainer review #4942961896, node
  `PRR_kwDOTqKoFc8AAAABJp-c6A`, recorded `COMMENTED_PASS` with no findings. Validate #111 and
  post-merge Validate #112 passed all four Python 3.10/3.12 jobs with 585 tests per job. Runtime
  scope is repository synthetic fixtures only and network-denied.
- M9-I5 status snapshot: exact contract-lock snapshot
  `126ad4fc548b897546ebe9c09832b3e79283bab5fae860be3a264b6c30055980` remains
  `CLOSED_WITH_SINGLE_MAINTAINER_EXCEPTION` evidence only for its original exact bytes. This
  runtime post-merge synchronization changes three subject files and therefore creates a distinct
  current snapshot that is `NOT_CLOSED` pending an immutable subject commit, exact-head CI,
  findings disposition, and closure attestation.

M9-I6, live access, provider/network activation, and real-company data remain unauthorized. The
M9-I5 runtime is authorized only in its merged disabled-offline, synthetic-only form.

FVI remains pre-v1.0 and is not investment advice. Interfaces and schemas may change before release.
