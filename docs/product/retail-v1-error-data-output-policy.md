# Retail v1 Error, Data, and Output Policy

Status: M8 reviewed contract; M9-I1 safe errors approved; data and output runtime unauthorized

## Error taxonomy

| Code family | Example condition | Severity | Required behavior |
|---|---|---|---|
| `IDENTITY-*` | ambiguous ticker/CIK or delisted identity mismatch | Blocking | Ask the user to select a verified issuer or stop |
| `SCOPE-*` | bank, insurer, REIT, fund, SPAC, non-US/non-USD | Blocking | Explain unsupported scope; do not run another method |
| `TERRITORY-*` | requested country has no current server-side distribution approval | Blocking | Explain unavailable territory; request data cannot override the registry |
| `PROVIDER-*` | outage, timeout, rate limit, malformed response | Retry or blocking | Bounded retry; offer explicit manual import; never reuse stale data silently |
| `LICENSE-*` | display/redistribution right pending or rejected | Blocking for affected output | Suppress affected data/export and stop if it is material |
| `DATA-*` | missing fact, duplicate, amendment, custom tag, mixed unit/currency | Review or blocking | Preserve raw facts, show finding, require reconciliation |
| `STALE-*` | filing or market snapshot exceeds policy | Blocking | Refresh or stop; show the applicable as-of date |
| `ROUTE-*` | unsupported lifecycle or low-confidence route | Blocking | Human review or stop; no LLM approval |
| `ASSUMPTION-*` | missing provenance, failed bound, inconsistent terminal state | Blocking | Correct and re-lock the case; no default hidden from the user |
| `APPROVAL-*` | missing, non-human, stale, or hash mismatch | Blocking | Invalidate and request a new exact-hash approval |
| `VALIDATION-*` | arithmetic, schema, traceability, or independent review failure | Blocking | No retail report; preserve audit finding |
| `ADVICE-*` | buy/sell/hold, sizing, timing, suitability, persuasion | Blocking | Refuse or remove prohibited field before approval; log policy finding |
| `EXPORT-*` | report hash/version/source index mismatch | Blocking | Do not create or distribute the export |
| `SECURITY-*` | injection, unauthorized access, malware, secret exposure | Blocking | Terminate request, contain, redact, and follow incident runbook |

Every error object in M9 must include a stable code, user-safe message, severity, retryability, affected artifact references, and an allowed next action. Stack traces, raw provider bodies, secrets, and hidden prompts are not user-visible messages.

## Data provenance policy

- Raw provider records are append-only, content-addressed snapshots.
- Normalization never overwrites a filing fact. It creates a new derived fact with source references and a calculation rule.
- Material inputs require provider, accession when applicable, period, unit, currency, as-of time, and content hash.
- Manual inputs are labeled `manual-upload`; user overrides never masquerade as filing facts.
- Amendments, stock splits, acquisitions, disposals, discontinued operations, leases, minority claims, and share dilution require explicit reconciliation.
- Missing material data cannot be replaced with zero, peer medians, stale values, or LLM estimates without a visible approved assumption and permitted route.

## Provider and license register fields

Before a provider adapter is enabled, M9 must record: owner, endpoint, data categories, authentication, terms URL and version/date, allowed storage, display, export, redistribution, attribution, retention, rate limits, territorial restrictions, fallback, reviewer, review date, and approval status. Rights are evaluated per provider and requested output; one aggregate boolean cannot expand narrower record-level rights.

SEC public access does not automatically authorize every downstream market-data field or export. Each provider is reviewed independently.

## Output policy

- An approved report contains a conditional valuation range, not a single action target.
- Current price, if licensed and shown, is a dated observation and cannot produce an upside/downside recommendation label.
- Bear/base/bull labels describe assumption sets; their probabilities remain null unless a later reviewed contract adds an evidenced deterministic method.
- Report prose cannot change numbers or omit blocking findings from the approved artifacts.
- PDF/JSON exports carry the same report hash, version manifest, data dates, sources, and limitations.
- A superseded or stale report is visibly expired and must not be silently refreshed under the old approval.
- The server-side territory registry is default deny. A request's country code and acknowledgements are context only and cannot create a distribution approval.
- `case_lock.approved_hash` equals the recomputed canonical `case_hash`; `output_approval.approved_hash` equals the independently validated `valuation_output_hash`; `report_hash` protects the final export and is not substituted for either approval target.
