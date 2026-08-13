# M9-I4 Disabled SEC Adapters — Local Implementation Candidate Review

Status: `COMMENTED_PASS`; same-maintainer local formal review, not independent approval

Canonical baseline: `main` at `46b938c2709faeef374f36684bfe69dee3df9a4e`

Authority: local unstaged candidate only; no commit, push, pull request, provider activation, or
live-readiness decision

Network state: `DENIED`

Data boundary: four positive and seven negative locked fixture artifacts plus small original
in-memory adversarial stream scripts; no real-company or captured provider data

## 1. Candidate decision

This candidate implements the separately authorized M9-I4 offline checkpoint against the merged
contract. It does not amend the contract, provider/license registry, prior snapshot evidence, or
M9-I5/M9-I6 authority. It is not a claim that the current status-synchronization snapshot is closed.

The public adapter surface remains fail-closed. Each adapter accepts only a capability-specific
typed identifier mapping and a User-Agent-policy-presence boolean. Because the merged policy is
`disabled`/`denied`, each public execution stops before its injected transport. No actual User-Agent
value, contact component, credential, caller URL, header, proxy, socket, DNS resolver, HTTP client,
or fallback identity is accepted or stored.

## 2. Implementation topology

| Surface | Candidate path | Locked role |
|---|---|---|
| Contracts | `tools/retail_data/sec_contracts.py` | Exact disabled policy, strict fixture/result hashes, fixed safe errors |
| Endpoints | `tools/retail_data/sec_endpoints.py` | Four typed constructors; no caller-addressable URL surface |
| Limiter | `tools/retail_data/sec_limiter.py` | Shared 1 request/second token budget, 32-request queue, injected scheduling |
| Resilience | `tools/retail_data/sec_resilience.py` | Three attempts, 1s/2s backoff, 30s outer deadline, five-failure breaker |
| Transport | `tools/retail_data/sec_fixture_transport.py` | Original-fixture event replay only; no network imports |
| Cache | `tools/retail_data/sec_cache.py` | Exact-byte M9-I3 storage references and self-hashed immutable index |
| Adapters | `tools/retail_data/sec_adapters.py` | Four disabled public adapters plus isolated synthetic replay harness |
| Independent validation | `tools/validate_m9_i4_sec_adapters.py` | Separate schemas, hashing, replay, registry, store, cache, and redaction checks |

The M9-I3 `ContentAddressedStore` remains byte-for-byte unchanged. M9-I4 passes accepted synthetic
bytes through that existing store and binds the independently checked response media type in its
own strict result/cache metadata. It does not create a second raw-byte store or widen the M9-I3
manual-import media contract.

## 3. Authority separation

The two execution surfaces are intentionally non-interchangeable:

1. `SecIdentityAdapter`, `SecSubmissionsAdapter`, `SecFilingsAdapter`, and
   `SecCompanyFactsAdapter` validate strict identifiers and policy references, then stop before
   dispatch because global/capability switches are disabled and the registry remains pending.
2. `replay_synthetic_fixture` exercises limiter, retry, timeout, breaker, response, and store
   behavior only with injected time and a `SyntheticFixtureTransport`. It cannot call a live
   transport or change provider authority. Its results retain `activation_state: disabled` and
   `network_state: denied` and are synthetic validation evidence, not a source snapshot.

Cache tests require a `SyntheticCacheContext` derived from one of the four exact locked fixture
hashes plus the exact current provider-registry subject and explicit `US` territory. Publication
and every read recheck registry hash, pending/disabled state, absent storage right, zero retention,
territory, provider expiry, capability kill switch, and fixture/body closure. This is synthetic-test
authority only: it proves that provider storage authority remains absent and cannot grant live use.
A generic boolean cannot grant cache publication, and arbitrary bytes are rejected.

## 4. Locked synthetic fixtures

Positive capability fixtures:

- `STF-SYNTH-IDENTITY-SUCCESS`
- `STF-SYNTH-SUBMISSIONS-SUCCESS`
- `STF-SYNTH-FILING-SUCCESS`
- `STF-SYNTH-COMPANYFACTS-RETRY-SUCCESS`

Negative resilience/integrity fixtures:

- `STF-SYNTH-IDENTITY-TIMEOUT-EXHAUSTED`
- `STF-SYNTH-IDENTITY-TOTAL-TIMEOUT`
- `STF-SYNTH-IDENTITY-CONNECT-TIMEOUT-RETRY-SUCCESS`
- `STF-SYNTH-IDENTITY-REDIRECT-DENIED`
- `STF-SYNTH-IDENTITY-UPSTREAM-REJECTED`
- `STF-SYNTH-IDENTITY-MEDIA-MISMATCH`
- `STF-SYNTH-IDENTITY-DUPLICATE-JSON`

Every identifier and body is invented for testing. The fixtures contain no provider capture,
official response, real issuer, real ticker, credential, actual User-Agent, PDF, archive, private
extract, or attached source material. Each fixture self-hash and expected deterministic result hash
is implementation locked in both the production contract loader and the independent validator.
The headers/body-chunk/read-idle adversarial scripts are constructed only inside unit tests against
the transport parser; they are not repository fixture artifacts, cannot enter the allowlisted replay
or cache surfaces, and do not amend the merged fixture schema.

## 5. Required review matrix

- [x] exact base, unstaged state, and candidate-only authority confirmed;
- [x] provider registry byte identity confirmed unchanged;
- [x] all four capability/provider/endpoint mappings and canonical order confirmed;
- [x] traversal, percent escape, Unicode digit, extra identifier, and caller URL surfaces denied;
- [x] public adapters proven unable to dispatch injected transport;
- [x] missing User-Agent presence stops without retaining a value;
- [x] one-process limiter token order, one-second spacing, deadline, and 32-request bound confirmed;
- [x] retry classification, exact attempt cap, 1s/2s backoff, cancellation, and total deadline confirmed;
- [x] breaker threshold, open interval, single half-open probe, and non-countable failures confirmed;
- [x] response status, redirect, media, size, encoding, length, and duplicate-JSON boundaries confirmed;
- [x] exact-byte write-once storage, immutable cache index, stale/tamper/symlink/no-fallback behavior confirmed;
- [x] fixture provenance and arbitrary-byte cache denial confirmed;
- [x] safe errors contain no URL, raw header/body, User-Agent, contact data, secret, or stack trace;
- [x] independent validator imports none of the production M9-I4 or canonical-hash helpers;
- [x] coordinated fixture rehash and stored-byte tamper fail independent validation;
- [x] repository policy, governed validators, `git diff --check`, focused tests, and full suite pass;
- [x] no staging, commit, push, PR, Mark Ready, merge, or status-snapshot closure claim occurred.

No box is preselected. Formal findings and disposition must be recorded only after review of the
exact local candidate bytes.

## 6. Validation record

Local validation on Python 3.12.13 after blocker remediation stabilized:

- focused M9-I4 unit/integration suite: 65 passed;
- complete repository suite: 505 passed;
- all 10 workflow validation/repository-policy steps passed;
- schema/governed-document validation: 36 schemas and 121 governed documents;
- repository policy: 408 candidate files and no prohibited source;
- `git diff --check`: passed;
- provider registry and M9-I3 storage implementation: byte-for-byte unchanged from the exact base;
- index contains no staged path; no commit, push, or pull request exists for this candidate.

Remote Python 3.10/3.12 CI and an exact-head formal review remain unavailable until separately
authorized staging, commit, push, and Draft PR steps. These local results and the same-maintainer
`COMMENTED_PASS` do not constitute independent approval or authorize publication.

## 7. Blocking-review remediation and disposition

The formal re-review reproduced and then closed all five prior blockers:

1. the global limiter now rejects a later request sequence before it can consume the earlier
   sequence's token/window; the earlier sequence remains admissible;
2. the synthetic transport now has explicit headers, body-chunk, and response-end phases, enforces
   5-second connect, 20-second read-idle, and 30-second total limits, bounds streamed bytes before
   acceptance, and treats timeout after response bytes as non-retryable partial-body integrity;
3. the independent validator accepts a positive consecutive offset from the process-wide limiter,
   independently normalizes that offset and its bounded initial wait to the locked standalone
   fixture result, and still rejects non-consecutive/token mutations;
4. cache validation now applies a strict exact-field/type/time schema, rejects unknown fields and
   expired entries, and closes capability/provider/endpoint/media/raw-record references; and
5. cache publication/read APIs now require and recheck exact registry, storage-right, territory,
   provider-expiry, policy, capability-switch, and fixture authority, including a final gate after
   raw storage and immediately before index publication.

Adversarial regression tests cover each condition, including the prior coordinated cache-index
self-rehash attack. No blocking finding remains in the exact 23-path local candidate. Formal local
disposition: `COMMENTED_PASS` by the same maintainer; independent review remains a later gate.

## 8. Explicit exclusions

- No provider registry, right, retention, territory, expiry, endpoint, or activation change.
- No credentials, actual User-Agent/contact string, environment proxy, DNS, socket, or HTTP client.
- No live SEC request, captured response, real-company identifier, real filing, or real XBRL fact.
- No M9-I5 normalization/reconciliation, M9-I6 handoff, valuation, LLM, API, CLI, or UI behavior.
- No `project_sources/` access or attached-source use.
- No status-summary change and no transfer of any prior snapshot closure verdict to these bytes.
- No stage, commit, push, pull request, Mark Ready, or merge.
