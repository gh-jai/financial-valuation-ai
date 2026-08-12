# M9-I4 Disabled SEC Adapters — Contract-Lock Candidate

Status: `LOCAL_CONTRACT_CANDIDATE_REVIEW_PENDING`; no implementation or network authority
Contract version: `0.1.0-candidate`
Canonical repository: `gh-jai/financial-valuation-ai`
Canonical baseline: `main` at `cd804db1126a45d8082f081f086b463d382566ba`
Design authorization: Project owner, 2026-08-12
Network state: `DENIED`
Data boundary: contract metadata and compact original synthetic transport fixtures only

## 1. Decision and authority boundary

M9-I4 defines a future, disabled-by-default transport boundary for four separately governed SEC
capabilities: issuer identity, submissions metadata, filing documents, and companyfacts. This
candidate locks strict interfaces, fixed endpoint construction, host and redirect policy, a shared
global limiter, deterministic bounded retries, timeouts, circuit breaking, tamper-evident caching,
safe errors, synthetic fixtures, and implementation-separated validation.

This document is a contract candidate, not an adapter implementation. It does not authorize
staging, committing, pushing, a pull request, provider activation, credentials, a User-Agent value,
DNS, sockets, HTTP, a live SEC request, a real issuer, a real filing, a captured provider payload,
normalization, valuation, an API, CLI, LLM, UI, pilot, beta, or release.

Approval of these bytes would approve only the design boundary. A later, separately authorized
offline implementation checkpoint may implement injected-transport behavior using synthetic
fixtures, but must still keep live transport unreachable. Live readiness is a later decision that
must recheck official policy and name the exact endpoints, environment, operator-owned User-Agent,
rate budget, logging, rollback, and test window.

## 2. Canonical inheritance

M9-I4 inherits without weakening:

- M7 deny-by-default runtime authority, exact-hash handoffs, executor/reviewer separation, and
  human-only approvals;
- M8 untrusted-provider-data, safe-stop, provider-rights, privacy, security, and release gates;
- the M9 planning rule that only the data gateway may ever receive allowlisted outbound access;
- M9-I1 safe errors, bounded redaction, canonical JSON/SHA-256, and default-deny provider registry;
- M9-I2 exact verified-identity and structural-scope handoffs; and
- M9-I3 content-addressed write-once storage, raw-byte authority, symlink/tamper rejection, and
  implementation-separated validation.

The existing `registries/m9-provider-license.yaml` remains authoritative and unchanged. All four
SEC entries are `pending`, `live_activation: disabled`, have no redirect hosts, and grant no
storage, display, export, or redistribution right. A contract, schema, fixture, passing test, or
cache hit cannot change those facts.

## 3. Included contract surface

The candidate defines only:

1. `sec-adapter-policy.schema.json`, the exact disabled transport policy and four capability
   records;
2. `sec-adapter-result.schema.json`, bounded metadata for one future injected-transport execution;
3. `sec-synthetic-transport-fixture.schema.json`, compact original request/response scripts with
   no provider capture or real-company data;
4. `sec-adapter-validation-result.schema.json`, an implementation-separated verdict over exact
   policy, fixture, result, registry, stored-record, and cache subjects; and
5. a review checklist and governance regressions for these exact contract bytes.

No production module, transport client, fixture payload, provider registry mutation, cache entry,
credential, operator identity, or User-Agent string is included.

## 4. Locked capability separation

The future policy artifact must contain exactly four unique capability records in this canonical
order:

| Order | Capability | Provider registry ID | Endpoint ID | Fixed HTTPS template | Host |
|---:|---|---|---|---|---|
| 0 | `identity` | `sec-identity` | `sec-company-tickers-v1` | `https://www.sec.gov/files/company_tickers.json` | `www.sec.gov` |
| 1 | `submissions` | `sec-submissions` | `sec-submissions-by-cik-v1` | `https://data.sec.gov/submissions/CIK{cik}.json` | `data.sec.gov` |
| 2 | `filings` | `sec-filings` | `sec-filing-document-v1` | `https://www.sec.gov/Archives/edgar/data/{cik}/{accession_compact}/{document}` | `www.sec.gov` |
| 3 | `companyfacts` | `sec-xbrl` | `sec-companyfacts-by-cik-v1` | `https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json` | `data.sec.gov` |

Each capability has an independent kill switch fixed to `disabled`. Permission for one capability
never grants another. Provider/license approval is necessary but insufficient; the policy's global
kill switch, capability switch, live-readiness decision, exact environment, and endpoint must also
permit a request. Under this contract candidate every such decision remains denied.

## 5. Fixed request construction and SSRF boundary

- Callers select only a capability plus strict typed identifiers; they never provide a URL,
  scheme, host, port, path, query string, header name, proxy, or redirect target.
- CIK is exactly ten ASCII digits. For path construction it is normalized only to its decimal
  no-leading-zero form where the fixed endpoint requires it; the canonical identity remains the
  ten-digit value.
- Accession is exactly `##########-##-######`; `accession_compact` is those 18 digits with hyphens
  removed. The filing `document` is an allowlisted basename matching
  `[A-Za-z0-9][A-Za-z0-9._-]{0,127}` with no slash, backslash, percent escape, dot segment, control
  character, Unicode normalization, or empty extension trick.
- Schemes are fixed to `https`; ports, fragments, userinfo, arbitrary queries, proxies, environment
  proxy inheritance, and caller headers are forbidden.
- Hosts are exact lowercase ASCII matches after parsing. Subdomains, trailing dots, alternate IP
  spellings, DNS rebinding results outside the future approved public-address policy, loopback,
  link-local, private, multicast, reserved, unspecified, and IPv4-mapped IPv6 addresses stop.
- Redirect policy is `deny_all`: every 3xx response stops before following `Location`, even when the
  target host appears allowlisted. A later contract revision is required to permit any redirect.
- The future transport must disable automatic decompression unless the exact bounded content-
  encoding policy is separately locked. Archives and nested containers are not accepted.

## 6. Header, identity, and credential boundary

- The only permitted outbound request headers are `Accept`, `Host`, and `User-Agent`, constructed
  internally. Capability-specific `Accept` values are fixed by policy.
- `User-Agent` policy is `operator_configured_not_stored`. It must be a non-empty, bounded,
  contact-identifying value supplied only by a later approved runtime environment.
- The repository, fixtures, artifacts, cache metadata, logs, safe errors, and review evidence must
  never contain the actual User-Agent or its contact component. Validation records only whether a
  value was present and policy-valid.
- Authentication class is `user_agent`; cookies, authorization headers, API keys, bearer/basic
  credentials, client certificates, query credentials, and session state are forbidden.
- Missing or invalid User-Agent stops before transport with `SEC-USER-AGENT-DENIED` and never falls
  back to a default library identity.

## 7. Global rate limit and deterministic scheduling

One process-wide limiter covers all four SEC capabilities and both SEC hosts:

| Parameter | Locked value |
|---|---:|
| Algorithm | `deterministic_token_bucket_v1` |
| Window | 1 second |
| Maximum requests per window | 1 |
| Burst capacity | 1 |
| Clock | injected monotonic clock |
| Sleep | injected scheduler only |
| Queue bound | 32 pending acquisitions |
| Queue order | `(eligible_at, request_sequence)` |
| Exhaustion behavior | fail closed; no unbounded wait |

Every network attempt, including a retry, consumes a token before dispatch. Cache hits and
pre-transport policy failures consume no token. No capability, thread, async task, process-local
adapter instance, response code, or caller priority receives a separate burst budget. Multi-process
coordination is outside this slice and therefore live activation remains forbidden.

## 8. Bounded retry, backoff, and timeout contract

- `max_attempts` is 3 total attempts, including the first.
- Only synthetic transport timeout, connection reset before response bytes, HTTP 429, and HTTP
  500/502/503/504 are retryable.
- DNS/policy/SSRF/redirect/User-Agent/license/kill-switch failures, other 4xx responses, malformed
  status or headers, partial body, oversize body, content-type mismatch, digest mismatch, and parse
  failure are never retried.
- Deterministic delays before attempts 2 and 3 are exactly 1 and 2 seconds. Jitter is fixed to
  `none`; `Retry-After` is recorded only as bounded untrusted metadata and cannot shorten, extend,
  or bypass the locked schedule in M9-I4.
- Connect timeout is 5 seconds, read-idle timeout is 20 seconds, and total request deadline is 30
  seconds, all measured by injected monotonic time. The earliest limit wins.
- A retry receives the remaining total operation budget; it never resets an outer deadline.
- No retry may occur after cancellation, kill-switch transition, open circuit, exhausted global
  rate budget, or any response byte integrity failure.

## 9. Circuit breaker and kill switches

The circuit breaker is shared by `(provider_id, capability)` and uses injected monotonic time:

- states are `closed`, `open`, and `half_open`;
- five consecutive countable failures open the circuit for 60 seconds;
- countable failures are retryable transport failures and HTTP 429/500/502/503/504 only;
- policy denials, cache findings, caller validation errors, and cancellations do not train the
  breaker;
- success resets the consecutive count to zero;
- after 60 seconds exactly one deterministic probe may enter `half_open`; concurrent probes stop;
- probe success closes and resets; probe failure reopens for another 60 seconds; and
- process restart persistence is not claimed, so live activation remains forbidden.

The global and four capability kill switches are evaluated before cache read, limiter acquisition,
every attempt, and cache publication. Any switch not exactly enabled by a later live-readiness
artifact stops with `SEC-ADAPTER-DISABLED`. A fixture cannot alter a switch or breaker.

## 10. Response and resource limits

The future injected transport must stream into a bounded sink and stop before accepting excess:

| Capability | Maximum decoded body | Required media family |
|---|---:|---|
| identity | 8,388,608 bytes | JSON |
| submissions | 16,777,216 bytes | JSON |
| filings | 25,165,824 bytes | HTML, text, or XBRL/XML selected by fixed policy |
| companyfacts | 33,554,432 bytes | JSON |

Header bytes are capped at 65,536, header count at 128, one header value at 8,192 bytes, and status
lines at 1,024 bytes. Transfer/content-length disagreement, unsupported encoding, truncation,
multiple conflicting content lengths, or body beyond the capability limit is blocking. Raw error
bodies never enter safe errors or logs.

## 11. Tamper-evident cache contract

- M9-I4 does not create a second mutable cache. Accepted raw bytes are stored only through the
  M9-I3 content-addressed write-once store after provider/license storage authority is positively
  established. In this candidate that authority is absent.
- A cache index is a canonical, self-hashed immutable artifact mapping a strict request fingerprint
  to raw record digest, byte count, retrieval instant, endpoint ID, capability, provider policy
  hash, fixture hash for tests, media type, and expiry instant.
- The fingerprint covers policy version/hash, provider/capability/endpoint, strict identifiers,
  accepted media family, and canonical request-header-presence flags; it never includes the actual
  User-Agent, contact data, a secret, or wall-clock state.
- Cache publication occurs only after complete-body hashing, M9-I3 write-once storage, schema
  validation, and final kill-switch recheck. Interrupted or failed responses create no valid index.
- Reads revalidate schema, self-hash, request fingerprint, referenced raw digest, byte count,
  symlink/path safety, media type, expiry, current policy hash, and provider rights. Any mismatch is
  `SEC-CACHE-TAMPER` and no stale or network fallback is allowed.
- Synthetic fixture cache tests may use an isolated temporary M9-I3 store. Repository fixtures
  contain no captured SEC bytes and never prove production cache freshness or rights.
- Cache reuse does not bypass license, territory, freshness, kill switch, or circuit policy.

## 12. Synthetic transport fixture contract

Fixtures are compact, original, and conspicuously synthetic. They contain only invented CIK-shaped
IDs, accessions, document basenames, headers, and small response bodies authored for tests. They
must declare `synthetic: true`, `network_state: denied`, and `capture_provenance: original_fixture`.

Fixtures select an endpoint ID and strict identifiers, never a caller URL. Scripted events are
limited to response metadata/body, timeout, connection reset, or monotonic-time advance. Bodies are
UTF-8 fixture strings or bounded base64 test bytes and are inside the fixture hash subject. No
recording tool, HAR, packet capture, real hostname response, SEC content, real issuer, credential,
actual User-Agent, PDF, ebook, private extract, or attached source is permitted.

## 13. Strict result interfaces

`sec-adapter-result` records one deterministic execution without raw response bytes. It binds the
exact policy, provider registry, request fingerprint, endpoint/capability, controlled timestamps,
attempt records, cache disposition, optional M9-I3 raw record reference, stable errors, and its
canonical self-hash.

Successful results require one accepted raw-record digest and no blocking errors. Failed results
require at least one stable error and no newly published cache entry. `activation_state` and
`network_state` remain `disabled` and `denied` in offline implementation evidence. A result is not
a `source-snapshot`, license approval, normalized fact, or M10 handoff.

## 14. Stable safe-stop taxonomy

All messages are fixed, bounded, and passed through M9-I1 redaction. Artifact references are safe
identifiers only. Raw URL, headers, body, stack trace, DNS answer, User-Agent, contact data, and
credentials are forbidden.

| Code | Condition | Retryable | Next action |
|---|---|---:|---|
| `SEC-ADAPTER-DISABLED` | Global/capability/live-readiness gate is not enabled. | false | `stop` |
| `SEC-PROVIDER-DENIED` | Registry status, expiry, right, territory, or policy hash denies use. | false | `update_registry` |
| `SEC-USER-AGENT-DENIED` | Required operator identity is absent or invalid. | false | `contact_support` |
| `SEC-ENDPOINT-DENIED` | Endpoint, identifier, scheme, host, port, path, DNS, or SSRF rule fails. | false | `stop` |
| `SEC-REDIRECT-DENIED` | Any redirect is returned. | false | `stop` |
| `SEC-RATE-LIMITED` | Bounded limiter queue/budget cannot admit the attempt. | true | `retry_later` |
| `SEC-CIRCUIT-OPEN` | Circuit is open or half-open probe is occupied. | true | `retry_later` |
| `SEC-TRANSPORT-TIMEOUT` | Synthetic/live-readiness transport hits a locked timeout. | true | `retry_later` |
| `SEC-TRANSPORT-RESET` | Connection resets before response bytes. | true | `retry_later` |
| `SEC-UPSTREAM-RETRYABLE` | HTTP 429/500/502/503/504 before accepted body. | true | `retry_later` |
| `SEC-UPSTREAM-REJECTED` | Other non-success status or malformed response metadata. | false | `contact_support` |
| `SEC-RESPONSE-OVERSIZE` | Header/body resource limit is exceeded. | false | `stop` |
| `SEC-RESPONSE-INTEGRITY` | Length, encoding, media, truncation, digest, or parse boundary fails. | false | `stop` |
| `SEC-CACHE-TAMPER` | Cache index or referenced raw bytes fail validation. | false | `stop` |
| `SEC-HASH-MISMATCH` | Canonical hash or exact reference closure fails. | false | `stop` |

## 15. Implementation-separated validation

The future `tools/validate_m9_i4_sec_adapters.py` must not import production adapter, endpoint,
limiter, retry, timeout, breaker, cache, fixture-runner, or canonical-hash helpers. It may use JSON
Schema and standard-library primitives and must independently:

1. reject duplicate JSON keys, non-finite numbers, unknown fields, non-canonical arrays, and
   unsupported versions;
2. recompute policy, fixture, result, cache-index, and validation-result hashes;
3. prove the exact four-capability registry/policy/endpoint closure and disabled state;
4. reconstruct fixed paths from strict identifiers and reject every alternate URL surface;
5. replay the synthetic event script with its own limiter, retry, timeout, breaker, and monotonic
   clock state machines;
6. recompute request fingerprints without production helpers or actual User-Agent content;
7. independently read and rehash any M9-I3 raw record and validate immutable cache reference
   closure;
8. enforce safe-error taxonomy, redaction, attempt/token accounting, deterministic order, and
   result state invariants; and
9. return a strict validation result whose `passed` state is impossible with any finding.

A coordinated mutation that rehashes downstream artifacts must still fail when it changes a
capability, endpoint, identifier, clock event, attempt, token, breaker transition, fixture byte,
stored byte, cache reference, error, or authority state.

## 16. Required offline implementation tests

Contract approval would not authorize these tests to be implemented, but a later implementation
candidate must include:

- exact capability/order/registry/endpoint and strict schema tests;
- caller URL, scheme, port, userinfo, query, fragment, proxy, header, traversal, percent-escape,
  Unicode, host-confusion, private-address, DNS-rebinding, and every-redirect denial tests;
- missing/invalid User-Agent presence tests without storing its value;
- cross-capability global limiter, queue bound/order, retry-token accounting, injected-clock, and
  no-real-sleep tests;
- exact retry classification, attempt cap, 1s/2s backoff, timeout precedence, cancellation, and
  remaining-budget tests;
- breaker threshold, reset, open interval, one-probe half-open, concurrency, and non-countable
  failure tests;
- header/body/media/length/encoding/truncation and resource-exhaustion tests;
- write-once cache publication, policy/rights/expiry recheck, symlink/tamper, partial-response,
  stale, and no-fallback tests;
- synthetic fixture provenance, real-data markers, secret/contact, PDF/archive, and capture-tool
  rejection tests;
- safe-error redaction and no raw body/header/URL/stack trace tests;
- independent replay, reference closure, coordinated-rehash mutation, AST/import, and subprocess/
  shell/dynamic-execution denial tests; and
- complete M1-M9-I3 regressions with network denied, no credentials, and Python 3.10/3.12 CI.

## 17. Proposed implementation footprint — separately authorized later

A future offline implementation review may consider:

```text
tools/retail_data/sec_contracts.py
tools/retail_data/sec_endpoints.py
tools/retail_data/sec_limiter.py
tools/retail_data/sec_resilience.py
tools/retail_data/sec_cache.py
tools/retail_data/sec_adapters.py
tools/retail_data/sec_fixture_transport.py
tools/validate_m9_i4_sec_adapters.py
benchmarks/fixtures/m9_i4/*.json
tests/unit/test_m9_i4_*.py
tests/integration/test_m9_i4_*.py
```

These paths are informative, not authorized. No third-party runtime dependency is approved. The
default candidate must remain standard-library plus existing repository dependencies.

## 18. Contract acceptance gates

The contract may be recommended for exact-SHA review only when:

- the four strict schemas validate and reject unknown fields;
- capability separation, endpoint construction, network denial, limits, state machines, cache,
  fixtures, errors, validation separation, and exclusions are numerically locked;
- the existing pending/disabled/rights-false registry is not modified;
- no runtime adapter, transport, cache, credential, fixture payload, or real-company material is
  added;
- focused contract tests, all repository validators/policy, `git diff --check`, and the complete
  suite pass; and
- the candidate remains unstaged and unpublished pending separate authorization.

## 19. Governance and later decisions

This document contains no mutable reviewer verdict or owner approval. A review applies only to the
SHA-256 of these exact UTF-8 bytes and the named baseline. Any byte change supersedes that review.
Contract review, owner approval, staging, commit, push, Draft PR, implementation authorization,
live-readiness testing, provider/license approval, production activation, and release are distinct
decisions.

The contract must fail closed to `candidate` when review evidence is missing, contradictory,
unqualified, hash-mismatched, or bound to another baseline. Same-maintainer commentary must not be
represented as independent review. No contract state may waive later qualified legal, privacy,
security, accessibility, provider-license, or operational review.

## 20. Explicit exclusions

- No adapter, network transport, DNS, socket, HTTP client, retry loop, limiter, circuit breaker, or
  cache implementation.
- No provider activation, credential, actual User-Agent, proxy, live SEC request, or official-
  policy claim based on live access.
- No real company, ticker, filing, accession, XBRL fact, provider response, captured fixture, PDF,
  ebook, private extract, attachment, or `project_sources/` use.
- No provider registry/right change, source snapshot, normalization/reconciliation, M9-I5/M9-I6,
  valuation, approval creation, stable API/CLI, LLM, UI, pilot, beta, or release.
- No stage, commit, push, Draft PR, Mark Ready, approval, merge, or branch deletion.

## Source boundary

No attached PDF, original extract, continuous source text, private-source content, real issuer
data, captured provider response, credential, or live external request was read or used to prepare
this candidate.
