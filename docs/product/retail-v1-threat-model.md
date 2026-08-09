# Retail v1 Threat Model

Status: M8 reviewed contract; M9-I1 offline primitives approved; transport remains unauthorized
Security baselines: OWASP ASVS 5.0.0 and OWASP LLMSVS v2.0, revalidated before release

## Assets

- provider credentials and application secrets;
- immutable public-data snapshots and user uploads;
- normalized financials, assumptions, approvals, valuation outputs, reports, and audit events;
- issuer identity and source provenance;
- deterministic engine, validator, schemas, prompts, registry, and policy versions;
- service availability and provider fair-access reputation.

## Trust zones

| Zone | Network | Authority |
|---|---|---|
| Browser/client | Untrusted | Submit requests and human approvals only after authentication |
| Data gateway | Allowlisted outbound | Fetch, cache, hash, and label provider records; cannot value or approve |
| Upload quarantine | No valuation access | Type/size/malware checks before an immutable snapshot is admitted |
| Normalization service | No arbitrary outbound | Deterministic mapping and reconciliation; cannot approve |
| M7 valuation runtime | Network denied | Execute approved exact-hash case through allowlisted engines only |
| Independent validator | Network denied and implementation-separated | Recompute and issue findings; cannot modify or approve output |
| Report renderer | Network denied | Render approved artifact without changing facts or numbers |
| Operations/admin | Least privilege and audited | Manage service health; cannot silently rewrite artifacts or approvals |

## Threats and required controls

| Threat | Example | Required M9-M13 control |
|---|---|---|
| Issuer confusion | ticker reuse or ambiguous name | CIK/exchange/legal-name verification and explicit user selection |
| Provider tampering | malformed JSON, unit changes, replayed stale response | TLS, allowlist, schema checks, content hashes, dates, cache provenance, no silent fallback |
| SSRF and redirect escape | crafted URL, DNS rebinding, redirect to private or metadata service | fixed provider adapters, scheme/host/port allowlist, redirect revalidation, private-address denial, egress proxy and tests |
| Fair-access abuse | runaway SEC requests | declared User-Agent, global limiter at or below current policy, cache, bounded retry/backoff, circuit breaker |
| Filing injection | hostile text or XBRL label instructs an agent | treat content as data, structured extraction, no authority from evidence, output schema/policy checks |
| CSV attack | formulas, oversized archives, traversal, mixed encoding | size/type limits, archive/path rejection, formula neutralization, malware scan, strict parser |
| Unit/period corruption | thousands vs millions, quarter vs YTD | explicit units/contexts, period graph, cross-statement and annual/quarter reconciliation |
| Corporate-action error | amendment, split, acquisition, disposal | accession ordering, amendment and split controls, human review for material discontinuity |
| LLM fabrication | invented financial fact or arithmetic | evidence-required structured output, deterministic facts/calculation, independent validation, fail closed |
| Prompt injection | filing or user text requests tools/secrets | separated instructions/data, fixed allowlists, no shell/browser in runtime, redaction and adversarial tests |
| Approval tampering | reuse approval after assumption edit | canonical hashes, append-only events, automatic invalidation, human-only actor type |
| Browser approval forgery | CSRF, session theft, replay, or request field claims approval | authenticated object authorization, CSRF protection, step-up/recent authentication, nonce/idempotency, server-side territory and approval registries |
| Role collapse | executor reviews own output | executor/reviewer identity and implementation separation inherited from M7 |
| Advice leakage | report says buy/hold or position size | null schema fields, lexical/semantic policy validator, mutation tests, legal wording review |
| Unauthorized export | licensed price included in public PDF | provider-specific display/export flags and report source filtering |
| Secret leakage | API key in logs, prompts, reports, fixture | secret manager, structured redaction, repository scan, negative tests |
| Broken access control | read another user's run or approval | authenticated object-level authorization, tenant isolation, audit logging |
| Availability attack | expensive repeated valuations or provider outage | quotas, idempotency, queues, timeouts, cached snapshots, manual import fallback |
| Supply-chain compromise | malicious dependency/build | lockfiles, provenance, dependency/license scan, SBOM, signed release process |

Provider payloads, filings, uploads, browser request fields, user text, and model output are untrusted data and cannot authorize actions, approve a territory, expand an allowlist, create an approval, or suppress a finding.
The M7 valuation zone remains a network-denied M1-M6 runtime; only the separately governed data gateway may retrieve external issuer data.

## Security acceptance boundary

- M8 defines threats; it does not claim that controls are implemented.
- M13 requires no unresolved critical/high finding and documented disposition of lower findings.
- Security tests cover SSRF, injection, traversal, malicious uploads, broken access control, secret/log leakage, approval tampering, rate limiting, and export filtering.
- Incident response, backup/restore, deletion, provider disablement, and rollback are rehearsed before M14.
