# M9-I4 Disabled SEC Adapters Contract Review

Contract: `docs/milestones/M9-I4-disabled-sec-adapters-contract-lock.md`
Status: `LOCAL_REVIEW_CHECKLIST_CANDIDATE`; no verdict or approval recorded
Review baseline: `main@cd804db1126a45d8082f081f086b463d382566ba`

## Authority and scope

- [ ] Review is bound to the exact contract SHA-256 and baseline.
- [ ] Contract design is not represented as adapter implementation or live-network authority.
- [ ] Identity, submissions, filings, and companyfacts are four separately gated capabilities.
- [ ] Provider activation, credentials, actual User-Agent, live SEC requests, and real data remain denied.
- [ ] M9-I5, M9-I6, normalization, valuation, API/CLI, LLM, UI, pilot, beta, and release remain excluded.

## Endpoint and network policy

- [ ] Callers cannot supply URL, scheme, host, port, path, query, fragment, headers, proxy, or redirect target.
- [ ] Four exact HTTPS templates, endpoint IDs, registry IDs, and hosts are locked.
- [ ] CIK, accession, compact accession, and document-basename transformations are unambiguous.
- [ ] Redirects are denied without following `Location`.
- [ ] Host parsing, public-address checks, DNS-rebinding, private/link-local/loopback/reserved ranges, and proxy inheritance fail closed.
- [ ] Only internally constructed `Accept`, `Host`, and `User-Agent` headers are permitted.
- [ ] Actual User-Agent/contact content is operator-owned and forbidden from repository artifacts.

## Resilience and resource controls

- [ ] One global 1 request/second, burst-1 limiter covers all capabilities and attempts.
- [ ] Queue bound/order, injected monotonic clock, and injected scheduler are deterministic.
- [ ] Three total attempts, exact retry classes, 1s/2s backoff, and no jitter are locked.
- [ ] Connect/read/total timeouts are 5s/20s/30s and outer deadlines never reset.
- [ ] Circuit states, five-failure threshold, 60s open interval, and one half-open probe are locked.
- [ ] Global and capability kill switches are checked at every authority-sensitive transition.
- [ ] Header and capability-specific body limits, media, encoding, length, and truncation rules stop safely.

## Cache, fixtures, and errors

- [ ] Cache bytes use only M9-I3 write-once storage; no mutable secondary cache is introduced.
- [ ] Cache fingerprint/index/hash/reference/rights/expiry/tamper checks are complete and no fallback hides a finding.
- [ ] Fixtures are original, compact, synthetic, network-denied, and never captured provider data.
- [ ] Fixtures contain no real issuer, credential, actual User-Agent, PDF, ebook, private extract, or attachment material.
- [ ] Stable error codes, retryability, next action, bounded redaction, and no raw error body/header/URL invariants are locked.

## Independent validation and evidence

- [ ] Validator does not import production adapter, endpoint, limiter, resilience, cache, fixture-runner, or hash helpers.
- [ ] Validator independently replays time, rate, retry, breaker, cache, hash, reference, and authority state.
- [ ] Coordinated downstream rehash mutations cannot conceal upstream or state-machine tamper.
- [ ] Schemas are Draft 2020-12, strict, versioned, finite, and reject unknown fields.
- [ ] Existing provider registry remains byte-for-byte unchanged and default deny.
- [ ] Focused tests, full suite, workflow validators/policy, Python 3.10/3.12 CI, and `git diff --check` are required before publication.

Review recommendation:
`[ ] PASS  [ ] COMMENTED_BLOCKING  [ ] request changes`

No box is preselected. A later review must record findings and a verdict outside the frozen
contract payload and must not claim independence when reviewer/author separation did not occur.
