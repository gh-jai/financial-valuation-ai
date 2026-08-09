# M8 Retail Product Contract and Safety Boundary

Status: Cross-functional design review complete; M9 planning merged; I1 primitives approved
Contract version: 0.1.0
Baseline: P0+M8 contract merged at `9099a287caf7c8e363d99586db1173f76d63956a`
Target release: FVI v1.0 after M9-M14 launch gates

## Decision

M8 defines the product and safety boundary required to turn FVI from a developer framework into a retail-facing research and valuation tool. It does not ingest live data, normalize a real filing, call a model provider, expose an API, render a Web interface, or authorize a production release.

The v1.0 target is a non-personalized research tool for US-listed, USD-reporting, non-financial operating companies. A user may inspect and approve the exact company data, route, assumptions, scenarios, and output. The system may explain a valuation range but must not recommend buying, selling, holding, sizing, timing, or executing a transaction.

## Included v1.0 scope

- US-listed operating issuers identified by verified ticker, exchange, legal name, and ten-digit CIK.
- USD financial statements derived primarily from Forms 10-K, 10-Q, 8-K, SEC submissions JSON, and US-GAAP XBRL facts.
- Manual CSV or JSON input as an explicit, provenance-preserving fallback.
- Existing M1, M3, M4, M5, and M6 routes, using FCFF DCF as the primary method.
- Bear, base, and bull scenarios without hidden or automatically invented probabilities.
- Traditional Chinese user experience with English source names, filing identifiers, and technical fields preserved.
- Server-side, default-deny territory decisions; a request-supplied country code never grants distribution authority.
- Human `case_lock` and `output_approval` bound to exact artifact hashes.
- Human-readable and machine-readable report contracts with source, date, unit, calculation, uncertainty, and limitation disclosures.

## Excluded v1.0 scope

- Banks, insurers, REITs, funds, SPACs, regulated-capital models, and natural-resource real-option cases.
- Issuers without sufficient, reconcilable FCFF inputs or with unresolved material corporate actions.
- Non-USD primary reporting, non-US primary listings, private companies, cryptoassets, derivatives, and portfolios.
- Relative-value rankings, screeners, backtests, price targets presented as predictions, and performance claims.
- Personalized suitability, investor profiling, risk-tolerance capture, portfolio holdings, brokerage connections, and orders.
- Buy, sell, hold, position-size, leverage, hedge, timing, alert, or trade-execution instructions.
- Autonomous approval of issuer identity, support status, route, assumptions, case, valuation output, or publication.

## Required user journey

1. Resolve a ticker, CIK, or company name without silently selecting an ambiguous issuer.
2. Show identity, support decision, filing period, data dates, providers, and license status.
3. Acquire or import an immutable source snapshot; never modify a raw fact in place.
4. Normalize statements and expose period, unit, amendment, split, duplicate, custom-tag, and reconciliation findings.
5. Propose a lifecycle route and bear/base/bull assumptions with dated provenance.
6. Require a human to approve the exact `valuation-case` hash at `case_lock`.
7. Run only the existing deterministic valuation engines and an independent validator.
8. Require a different human approval of the exact validated output hash.
9. Render the approved range, sensitivity, drivers, counterevidence, data gaps, and limitations without action language.
10. Export a content-addressed report and version manifest that can reproduce the run.

## Five interface contracts

The following schemas are draft interfaces. Schema validation does not imply that their runtime exists.

| Schema | Authority boundary |
|---|---|
| `company-request.schema.json` | Captures only company lookup, requested country, and acknowledgements; it must not collect portfolio or suitability data or self-approve a territory. |
| `source-snapshot.schema.json` | Binds issuer identity, each provider record, dates, units, license review, warnings, and immutable hashes. |
| `normalized-financials.schema.json` | Preserves filing/derived/override provenance and explicit reconciliation results; no silent fill is allowed. |
| `valuation-case.schema.json` | Binds route, scenarios, assumptions, evidence, overrides, and human `case_lock` to one exact hash. |
| `retail-report.schema.json` | Requires range, scenarios, sensitivity, sources, counterevidence, gaps, limitations, a server-approved distribution decision, approval, and null action fields. |

All five use schema version `0.1.0`. They remain unstable until M13 pilots and must not be frozen before M14.

## Data trust boundary

```text
Allowlisted public or licensed provider
-> networked data gateway
-> immutable hashed snapshot
-> offline deterministic normalization
-> reviewed valuation case
-> human case_lock
-> network-denied M1-M6 runtime
-> independent recomputation
-> human output_approval
-> immutable retail report
```

- The data gateway is the only component allowed to retrieve external issuer data.
- The valuation runtime retains M7's deny-by-default network and arbitrary-path boundary.
- A provider response, filing, CSV cell, XBRL label, or LLM output is untrusted data and cannot grant authority.
- A browser-supplied country code, acknowledgement, or other request field is also untrusted and cannot approve distribution, licensing, a route, or an artifact.
- Every material model input must resolve to a filing fact, licensed market snapshot, deterministic calculation, or recorded user override.
- A user override preserves the original value, new value, reason, actor, timestamp, and prior case hash. Any change invalidates existing approvals.
- CI uses fixed, redistributable or appropriately licensed offline fixtures and never depends on a live provider.

## Hash and approval semantics

- `case_hash` is SHA-256 over the canonical approvable valuation-case payload, excluding `case_hash` and `case_lock`. An active `case_lock.approved_hash` must equal that `case_hash`.
- `valuation_output_hash` is SHA-256 over the independently validated deterministic valuation output. `output_approval.approval_subject` is `valuation-output`, and its `approved_hash` must equal `artifact_refs.valuation_output_hash`.
- `report_hash` is SHA-256 over the canonical report payload after the output approval is attached, excluding only `report_hash`. It is an export-integrity hash, not the object approved by `output_approval`.
- Draft 2020-12 cannot express equality, ordering, uniqueness across selected fields, or deterministic arithmetic between instance fields. M9 validators must recompute these hashes, enforce the equalities above, and reject cyclic, ambiguous, or unknown canonicalization versions.
- The independent retail validator must also require finite numeric values, `bear <= base <= bull`, `valuation_range.low <= valuation_range.high`, exact agreement between the stored range and approved scenario outputs, unique sensitivity coordinate pairs, complete reference resolution, and a different human for `case_lock` and `output_approval`.

## LLM boundary

LLMs may draft evidence summaries, narrative assertions, plain-language explanations, and report prose through versioned structured-output adapters. They may not be the authoritative source of a financial fact, perform valuation arithmetic, approve a route or assumption, suppress a data-quality finding, create an approval, or modify numeric output.

The core path must still complete when the LLM provider is unavailable. Model input and output are subject to schema validation, evidence-reference validation, prompt-injection defenses, budget controls, redaction, retention policy, and independent review.

## Safe-stop invariants

The product must stop before valuation or report publication when any of the following applies:

- issuer identity is ambiguous or unverified;
- issuer or sector is unsupported;
- a material input is missing or lacks provenance;
- filing or market data is stale under the approved policy;
- periods, currency, units, amendments, splits, or shares cannot be reconciled;
- provider display or redistribution rights are pending or rejected for the requested output;
- lifecycle route or scenario assumptions are rejected or not human-approved;
- `case_lock` or `output_approval` is missing, stale, non-human, or bound to another hash;
- deterministic validation, independent review, policy validation, or report integrity fails;
- the requested jurisdiction is not approved for distribution;
- prohibited advice or trade language is detected.

No stop may silently fall back to a point estimate, another issuer, an older filing, an invented assumption, or an LLM-derived number.

## Output wording policy

The retail output must:

- describe bear/base/bull values and sensitivities as conditional valuation scenarios, not forecasts of the future market price;
- display the financial period end, valuation date, market-data timestamp, and material limitations prominently;
- distinguish filing facts, derived values, assumptions, overrides, and narrative judgments;
- present counterevidence and missing evidence next to supporting drivers;
- avoid urgency, gamification, ranking, persuasion, and artificial confidence scores;
- keep `buy_signal`, `sell_signal`, `hold_signal`, `position_size`, `trade_timing`, and `personal_suitability` null at the schema layer;
- refuse user requests to transform valuation differences into an action recommendation.

This is a product control, not a substitute for qualified legal advice. Release territory and wording require written legal/compliance approval at M14.

## Data retention and privacy minimum

- v1.0 does not collect portfolio positions, net worth, investment objectives, risk tolerance, or brokerage credentials.
- Public-source snapshots, derived artifacts, approvals, and audit events have documented retention periods and deletion owners before beta.
- Authentication secrets and provider keys never enter artifacts, logs, reports, prompts, or repository fixtures.
- User-uploaded financial files are isolated, malware-scanned, size/type-limited, content-addressed, access-controlled, and deleted according to a published policy.
- Reports expose only share-safe fields; private notes, raw prompts, secrets, and hidden reasoning are excluded.

## External design baselines

The following were rechecked on 2026-08-08 during the cross-functional design review and must be rechecked before implementation review and again before M14 release:

- SEC EDGAR Data APIs: <https://www.sec.gov/search-filings/edgar-application-programming-interfaces>
- SEC fair-access policy, including the current 10 requests/second ceiling: <https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data>
- FCA PERG 8 advice/information and personal-recommendation guidance: <https://handbook.fca.org.uk/handbook/perg8>
- WCAG 2.2 Recommendation: <https://www.w3.org/TR/WCAG22/>
- OWASP ASVS 5.0.0: <https://owasp.org/www-project-application-security-verification-standard/>
- OWASP LLM Verification Standard v2.0: <https://owasp.org/www-project-llm-verification-standard/LLMSVS-v2.0-en.html>

## M8 acceptance gate

M8 is accepted only when all of the following are true:

- the five schemas pass Draft 2020-12 validation and contract tests;
- support/stop routing covers every class in the issuer matrix;
- error taxonomy maps every blocking condition to a user-visible recovery or terminal stop;
- threat model covers public data, uploads, LLMs, approvals, exports, and operations;
- pilot matrix contains eight development pilots and at least two holdouts without selecting issuers to flatter model output;
- product, financial, security, and internal legal/data-perimeter reviewers complete the M8 checklist;
- qualified legal/compliance counsel and every provider-license owner remain named, blocking M13/M14 launch gates; M8 approval is not their sign-off;
- repository validators, policy checks, pre-commit, and the full existing suite remain green;
- no PDF, ebook, private extract, real issuer snapshot, provider credential, or network runtime is committed.

The completed cross-functional review recommended M9 implementation planning subject to the recorded conditions in `M8-cross-functional-review.md`, and the project owner authorized that planning on 2026-08-08. Accepting or publishing the planning baseline, stage, commit, push, PR creation, every implementation slice, live access, release, qualified legal approval, provider approval, and any private-source extraction remain separate actions.

The planning baseline was later merged through PR #19. M9-I1 then received its own implementation,
review, and publication authorizations. That bounded candidate implements only safe errors,
canonical hashing, independent recomputation, and default-deny registry primitives. It does not
satisfy `M8-C01` through `M8-C07`, select an issuer, acquire data, enable a provider, implement a
later M9 slice, or authorize any live or release action.
