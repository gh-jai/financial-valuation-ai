# M9-I2 Issuer Resolution — Contract-Lock Candidate

Status: Revised frozen candidate; independent review and project-owner approval pending; no implementation authority
Contract version: 0.1.1-candidate
Canonical repository: `gh-jai/financial-valuation-ai`
Canonical baseline: `main` at `3945e90559ec2e10771489078c9e8f52036209b7`
Design authorization: Project owner, 2026-08-09
Network state: Denied
Data boundary: Synthetic offline identity fixtures only

## 1. Decision

M9-I2 is a bounded, offline issuer-resolution checkpoint. If separately authorized for
implementation, it may validate an existing `company-request`, produce deterministic issuer
candidates from a frozen synthetic catalog, require an exact-hash-bound human selection, construct
a verified issuer identity, and evaluate whether that identity is eligible to proceed to later M9
data review under a versioned support policy.

This contract does not authorize implementation, staging, committing, pushing, a pull request,
live SEC or provider access, provider activation, real-company fixtures, user uploads, storage,
normalization, valuation, a route decision, an API, a CLI, an LLM, a UI, or a report.

M9-I2 must not advance the current operational implementation state beyond M7. Approval of this
contract candidate would authorize neither M9-I2 implementation nor M9-I3 through M9-I6. The
authoritative review and approval state is external to this frozen document and follows section 16.

## 2. Canonical inheritance

M9-I2 inherits without weakening:

- the M8 retail scope: US-listed, USD-reporting, non-financial operating companies;
- M8 safe-stop behavior and the `IDENTITY-*` / `SCOPE-*` error families;
- M9-I1 safe structured errors, bounded redaction, canonical JSON/SHA-256, implementation-separated
  hash recomputation, and default-deny registry behavior;
- M7 deny-by-default authority, append-only evidence, exact-hash artifact handoffs,
  executor/reviewer separation, stale-approval invalidation, and human-only approval boundaries;
- the existing M1-M7 workflow composition and deterministic valuation engines.

M9-I2 does not create a `case_lock` or `output_approval`. Its human selection is a narrower identity
choice and must not be treated as valuation approval, route approval, distribution approval, or
provider/license approval.

## 3. Included and excluded scope

### Included if implementation is separately authorized

- strict validation of `company-request.schema.json` version `0.1.0`;
- deterministic normalization of ticker, ten-digit CIK, or company-name queries;
- a synthetic, injected, offline identity-catalog adapter;
- deterministic candidate construction and ordering;
- explicit, hash-bound human candidate selection, including the one-candidate case;
- verified identity construction from one unchanged selected candidate;
- deterministic structural scope pre-screening against a versioned structural-scope registry;
- stable safe errors, reference closure, canonical hashes, independent validation, and synthetic
  regression fixtures.

### Excluded

- live HTTP, DNS, socket, browser, SEC, exchange, or market-data access;
- provider SDKs, credentials, request headers, rate limiting, retry, cache, redirect, or transport;
- real issuers, real tickers, real filings, provider payloads, PDFs, ebooks, or private extracts;
- fuzzy matching, probabilistic ranking, confidence scores, learned entity resolution, or LLM use;
- filing acquisition, snapshot storage, manual JSON/CSV import, XBRL mapping, normalization,
  reconciliation, or pipeline orchestration;
- lifecycle classification as mature, growth, young, declining, distressed, or cyclical;
- selection of `WFL-VAL-001`, `WFL-YNG-001`, `WFL-GRW-001`, `WFL-DST-001`, or `WFL-CYC-001`;
- assumptions, scenarios, valuation arithmetic, report language, advice, territory approval, or any
  M7 approval.

## 4. Locked artifact graph

```text
schema-valid company-request
-> canonical company_request_hash
-> frozen synthetic identity catalog + identity policy
-> issuer-candidate-set
-> human issuer-selection bound to candidate_set_hash and candidate_hash
-> verified-issuer-identity
-> versioned issuer-structural-scope registry
-> issuer-structural-scope-decision
-> issuer-resolution-validation-result from the independent validator
```

No arrow grants network, provider, valuation, approval, or publication authority. Each downstream
artifact refers to exact upstream hashes. A missing, mutated, stale, unsupported, or unresolved
reference stops all downstream handoffs. Ambiguity stops automatic identity/scope evaluation but
permits only the dedicated human-selection transition to consume the frozen candidate-set hash.

## 5. Proposed strict interfaces

The following are proposed M9-I2-owned schemas. Every object is Draft 2020-12, rejects unknown
fields, uses schema version `0.1.0`, requires `canonicalization_version` fixed to
`fvi-canonical-json-v1`, permits only finite JSON values, and rejects duplicate keys during YAML
or JSON loading before schema validation.

| Proposed schema | Purpose | Hash subject |
|---|---|---|
| `issuer-identity-catalog.schema.json` | Strictly governs the frozen synthetic identity catalog, record history, aliases, classification, evidence, status, and expiry. | Entire catalog excluding `catalog_hash`; each record excluding only `catalog_record_hash`. |
| `identity-resolution-policy.schema.json` | Governs normalization, ranks, precedence, freshness, taxonomy, adapter, and authority rules. | Entire policy excluding `identity_policy_hash`. |
| `issuer-structural-scope-registry.schema.json` | Governs only M9-I2 structural exclusions and the in-scope-pending-review result. | Entire registry excluding `scope_registry_hash`. |
| `issuer-candidate-set.schema.json` | Binds the request, normalized query, catalog/policy versions, deterministic candidate list, status, and safe errors. | Entire object excluding `candidate_set_hash`. |
| `issuer-selection.schema.json` | Records one human selection against an exact candidate set and exact candidate. | Entire object excluding `selection_hash`. |
| `verified-issuer-identity.schema.json` | Copies the selected identity without mutation and binds dated verification evidence. | Entire object excluding `verified_identity_hash`. |
| `issuer-structural-scope-decision.schema.json` | Applies structural v1 scope pre-screening without selecting a lifecycle route. | Entire object excluding `scope_decision_hash`. |
| `issuer-resolution-validation-result.schema.json` | Records the implementation-separated verdict over exact M9-I2 subject hashes. | Entire object excluding `validation_result_hash`. |

### 5.1 Common identifiers and hashes

- `company_request_hash`, `catalog_hash`, `catalog_record_hash`, `evidence_record_hash`,
  `listing_entry_hash`,
  `identity_policy_hash`,
  `candidate_hash`, `candidate_set_hash`, `selection_hash`, `verified_identity_hash`,
  `scope_registry_hash`, `scope_decision_hash`, and `validation_result_hash` are lowercase
  64-character SHA-256 values.
- Candidate-set IDs use `ICS-[A-Z0-9-]+`; selection IDs use `ISL-[A-Z0-9-]+`; verified-identity
  IDs use `VID-[A-Z0-9-]+`; structural-scope-decision IDs use `ISD-[A-Z0-9-]+`;
  validation-result IDs use `IVR-[A-Z0-9-]+`.
- IDs are labels only. Trust derives from recomputed content hashes and closed references, never
  from an ID alone.
- Every catalog, policy, registry, and output artifact contains
  `canonicalization_version: fvi-canonical-json-v1` inside its hash subject.
- `company_request_hash` is SHA-256 over the entire schema-valid `company-request` object. That
  draft schema has no self-hash field, so nothing is excluded.
- `catalog_record_hash` is SHA-256 over the complete strict catalog record excluding only
  `catalog_record_hash`; `candidate_hash` is SHA-256 over the complete candidate excluding only
  `candidate_hash`.
- Every output artifact records `created_at` from an injected UTC test clock. Stage-specific
  timestamps are additional fields and must equal that artifact's `created_at`. The resolver must
  not read the wall clock implicitly.
- All effective, expiry, observed, created, selected, verified, and evaluated times use RFC 3339
  UTC with a terminal `Z`.

### 5.2 Strict catalog, policy, and scope-registry contracts

The synthetic identity catalog requires exactly:

- `schema_version`, `canonicalization_version`, `catalog_id`, `catalog_version`;
- `status`: `pending`, `approved`, or `rejected`;
- `effective_at`, `expires_at`, `reviewed_at`, `reviewed_by`, `review_evidence`;
- `adapter_id`, `network_state` fixed to `denied`, `evidence_records`, `records`, `catalog_hash`.

Pending/rejected catalogs require no affirmative review authority and cannot resolve. An approved
catalog requires a human reviewer, non-empty bounded review evidence, `effective_at < expires_at`,
and evaluation time within `[effective_at, expires_at)`. Synthetic evidence records require
exactly `source_record_id`, `source_kind` fixed to `synthetic_identity`, `observed_at`, `fact_as_of`,
`assertion_kind`, `cik`, `legal_name`, `ticker`, `exchange_code`, `asserted_effective_from`, nullable
`asserted_effective_to`, and `evidence_record_hash`. `assertion_kind` is exactly `active_as_of` or
`closed_interval`. Their hash excludes only
`evidence_record_hash`. Catalog identity records require exactly:

- `record_id`, ten-digit `cik`, `legal_name`, `aliases`;
- `listing_history`, `primary_listing_country`, `primary_reporting_currency`;
- `issuer_class`, `regulated_capital_model_required`,
  `reserve_real_option_required`, `public_company_status`;
- `identity_observed_at`, `source_record_refs`, `catalog_record_hash`.

Each listing-history entry requires exact `ticker`, `exchange_code`, `effective_from`, nullable
`effective_to`, canonically ordered `evidence_record_refs`, and `listing_entry_hash`;
the entry hash excludes only itself and intervals use `[effective_from, effective_to)`. The catalog rejects
duplicate `record_id`, duplicate record hash, duplicate CIK, duplicate normalized alias within a
record, duplicate listing-history tuple, overlapping current intervals for one record, and any
non-identical records with a colliding content hash. Every source ref must resolve exactly once.
Every listing entry requires evidence whose CIK, legal name, ticker, and exchange code equal the
entry. An open current interval requires at least one `active_as_of` record with
`asserted_effective_from = effective_from`, null `asserted_effective_to`,
`effective_from <= fact_as_of <= observed_at`, and `observed_at <= resolution_at`. It proves only
that the listing was active at `fact_as_of`; it does not predict an end.

A closed historical interval requires at least one retrospective `closed_interval` record with
asserted start/end exactly equal to the listing entry, `fact_as_of = effective_to`, and
`effective_to <= observed_at <= resolution_at`. It proves the completed interval only after its
end. Optional contemporaneous `active_as_of` evidence may also be retained but cannot prove the
end. Source evidence never labels an interval current or historical; the resolver derives that
classification at `resolution_at`.

Any CIK/name difference blocks as `IDENTITY-CIK-NAME-MISMATCH`; ticker, exchange, assertion,
interval, `fact_as_of`, or observation-time differences block as `IDENTITY-CATALOG-CONFLICT`.
For the one listing active at resolution, the record's `identity_observed_at` equals the earliest
`observed_at` among the evidence records required to substantiate its CIK/name and active listing;
historical-match evidence is validated against its historical interval but does not replace or
artificially stale the current identity evidence.
Aliases are sorted by
`(normalized_alias, original_alias)`, listing history by
`(effective_from, effective_to-or-max, ticker, exchange_code, listing_entry_hash)`, and source refs
lexicographically. Array order is part of the canonical contract; non-canonical order is rejected.

For every catalog/policy/registry envelope, IDs are lower-kebab-case, versions are semantic
`MAJOR.MINOR.PATCH`, hashes are lowercase SHA-256, review evidence is a unique canonically ordered
array of bounded artifact references, and effective/expiry times are UTC instants. `pending`
requires null `reviewed_at`/`reviewed_by` and grants no use. `approved` and `rejected` require a
human reviewer, review timestamp, and non-empty evidence; only `approved` within its half-open
effective interval is usable. Status, reviewer, evidence, and interval fields are inside the hash
subject.

The identity-resolution policy requires exactly:

- identity, schema, canonicalization, status, effective, expiry, review, and hash fields;
- `normalization_version`, allowed query/match kinds, exact rank and precedence tables;
- `max_identity_age_seconds`, timestamp and interval rules;
- exact issuer-class taxonomy and required classification fields;
- exact evidence-assertion enum `active_as_of`, `closed_interval`, a separate derived
  temporal-classification enum `current`, `historical`, `future`, exact public-company-status
  values, and the section 7.1 rules;
- allowlisted synthetic adapter IDs and `network_state: denied`;
- exact allowlists for supported primary-listing country, reporting currency, and synthetic test
  exchange codes;
- `identity_policy_hash`.

The structural-scope registry requires the same identity/status/effective/expiry/review/hash
envelope, `m8_support_matrix_ref`, SHA-256 over the exact checked-in UTF-8 bytes of that M8 matrix
with no newline normalization, and unique,
canonically ordered structural rule records. Each rule declares exact predicates, one outcome, one
stable reason code, and `evaluation_stage: m9-i2-structural`. It also lists M8
lifecycle-dependent matrix rows as `deferred_to_m10` metadata with no executable M9-I2 predicate.
Unknown, overlapping contradictory, pending, rejected, expired, unmapped, or non-canonical rules
fail closed.

All three contracts reject unknown fields and duplicate YAML/JSON keys. Their loaders must
normalize neither keys nor values before duplicate detection.

### 5.3 `issuer-candidate-set`

Required top-level fields:

- `schema_version`, `candidate_set_id`, `created_at`, `resolution_at`;
- `canonicalization_version`;
- `request_id`, `company_request_hash`;
- `resolver_version`, `normalization_version`;
- `catalog_id`, `catalog_version`, `catalog_hash`;
- `identity_policy_id`, `identity_policy_version`, `identity_policy_hash`;
- `query_kind`, `normalized_query`;
- `status`, `candidates`, `errors`, `candidate_set_hash`.

Allowed statuses and invariants:

| Status | Candidate count | Meaning and permitted transition |
|---|---:|---|
| `unique_candidate` | exactly 1 | Resolution found one candidate; human confirmation is still mandatory. |
| `selection_required` | at least 2 | Current invocation stops with `IDENTITY-AMBIGUOUS`; a new human-selection step may continue. |
| `not_found` | 0 | Terminal `IDENTITY-NOT-FOUND`; only a new request or corrected catalog may continue. |
| `blocked` | any | Terminal integrity, reuse, freshness, or catalog error; human selection cannot override it. |

Status/error invariants are enforced both in schema conditionals and by the independent validator:

- `unique_candidate`: exactly one candidate and an empty `errors` array;
- `selection_required`: at least two candidates and exactly one blocking, non-retryable
  `IDENTITY-AMBIGUOUS` error using `verify_identity`;
- `not_found`: zero candidates and exactly one blocking, non-retryable `IDENTITY-NOT-FOUND` error
  using `verify_identity`;
- `blocked`: at least one blocking error other than `IDENTITY-AMBIGUOUS` or
  `IDENTITY-NOT-FOUND`; no selection is permitted.

Every error must contain exactly the M9-I1 fields `code`, `message`, `severity`, `retryable`,
`artifact_refs`, and `next_action`, and must satisfy the M9-I1 retry/action consistency rules.

Every candidate requires:

- `candidate_id` and `candidate_hash`;
- `primary_match_kind` and `match_kinds`, using only `cik_exact`, `ticker_current_exact`,
  `ticker_historical_exact`, `legal_name_exact`, or `declared_alias_exact`;
- integer `match_rank` from the locked rank table;
- ten-digit `cik`, `legal_name`, current `ticker`, current `exchange_code`;
- `listing_status`, `listing_effective_from`, nullable `listing_effective_to`;
- `active_listing_evidence_hashes`, `matched_listing_refs`;
- `primary_listing_country`, `primary_reporting_currency`, `issuer_class`,
  `regulated_capital_model_required`, `reserve_real_option_required`, `public_company_status`;
- `identity_observed_at`, `source_record_refs`;
- `catalog_record_hash`.

`candidate_id` is `ICD-` followed by the uppercase 64-character SHA-256 of the canonical identity
key payload `(catalog_id, catalog_version, record_id, catalog_record_hash)`. It is never random or
position-derived. A non-identical payload/hash collision blocks as `IDENTITY-HASH-COLLISION`.

When one record matches through multiple fields, the resolver emits one candidate. `match_kinds`
contains every distinct match kind sorted by the locked precedence
`cik_exact`, `ticker_current_exact`, `legal_name_exact`, `ticker_historical_exact`,
`declared_alias_exact`; `primary_match_kind` is the first item and `match_rank` is its locked rank.
Candidates are then sorted by section 7.4.

Candidate objects reject user-visible confidence or probability fields. Candidate facts are data,
not authority. Candidate hashes exclude only their own `candidate_hash` field.

`created_at` must equal `resolution_at`; that instant is the sole temporal anchor used to classify
listing history and construct the candidate set. `matched_listing_refs` is empty for CIK/name
matches and contains the exact matched listing-history/evidence hashes for ticker matches. The
candidate's top-level ticker, exchange, status, and interval always describe the one active listing
at `resolution_at`, even when the query matched a historical ticker.

Each `matched_listing_refs` item contains exactly `listing_entry_hash`, `ticker`, `exchange_code`,
`derived_temporal_classification`, `effective_from`, nullable `effective_to`, and
`evidence_record_hashes`; source fields must equal the referenced catalog listing entry and its
closed assertion evidence, while the derived classification is independently recomputed at
`resolution_at`. Items are sorted by
`(effective_from, effective_to-or-max, ticker, exchange_code, listing_entry_hash)`.

### 5.4 `issuer-selection`

Required fields:

- `schema_version`, `canonicalization_version`, `selection_id`, `created_at`, `selected_at`;
- `candidate_set_id`, `candidate_set_hash`;
- `selected_candidate_id`, `selected_candidate_hash`;
- `actor_type` fixed to `human`, bounded `actor_id`;
- `selection_reason` enum: `confirmed_unique`, `resolved_ambiguity`;
- `selection_hash`.

Locked rules:

- A selection is valid only for `unique_candidate` or `selection_required`.
- `confirmed_unique` requires exactly one candidate; `resolved_ambiguity` requires at least two.
- The selected ID and hash must identify the same candidate in the exact candidate set.
- The actor must be human. An agent, service, validator, resolver, fixture, or provider cannot select.
- A selection cannot edit a ticker, CIK, name, exchange code, issuer class, classification flag,
  date, or scope field.
- A changed request, catalog, policy, candidate, order, or candidate set invalidates the selection.
- Authentication and object authorization are later runtime concerns; synthetic tests use bounded
  fictitious actor IDs and grant no production identity authority.
- `created_at` must equal `selected_at` and must be no earlier than the candidate set's
  `created_at`.

### 5.5 `verified-issuer-identity`

Required fields:

- `schema_version`, `canonicalization_version`, `verified_identity_id`, `created_at`, `verified_at`;
- `selection_id`, `selection_hash`, `candidate_set_hash`, `selected_candidate_hash`;
- `cik`, `legal_name`, `ticker`, `exchange_code`;
- `listing_status` fixed to `active`;
- `listing_effective_from`, nullable `listing_effective_to`,
  `active_listing_evidence_hashes`;
- `primary_listing_country`, `primary_reporting_currency`, `issuer_class`,
  `regulated_capital_model_required`, `reserve_real_option_required`, `public_company_status`;
- `identity_observed_at`, `identity_age_seconds`, `freshness_evaluated_at`,
  `freshness_policy_ref`;
- `catalog_record_hash`, `source_record_refs`;
- `identity_status` fixed to `verified`;
- `verified_identity_hash`.

The identity fields must exactly equal the selected candidate. Unicode-equivalent but byte-different
names are not silently substituted after selection. Normalization is used for matching only; the
catalog's canonical legal name is preserved in the artifact.

The listing effective interval and `active_listing_evidence_hashes` must exactly equal the selected
candidate's active listing and must close to catalog evidence whose CIK, legal name, ticker,
exchange code, status, interval, and observed time all pass section 5.2. Historical matched-listing
evidence remains in the selected candidate hash; it cannot replace evidence for the current
verified identity.

Failed attempts do not emit a partially verified identity. They emit a safe blocking error and no
downstream identity handoff.

`created_at`, `verified_at`, and `freshness_evaluated_at` must be equal. Verification must occur no
earlier than `selected_at`. Listing status and interval, catalog/policy effectiveness, evidence
freshness, and every referenced hash are rechecked at `verified_at`.

### 5.6 `issuer-structural-scope-decision`

Required fields:

- `schema_version`, `canonicalization_version`, `scope_decision_id`, `created_at`, `evaluated_at`;
- `verified_identity_id`, `verified_identity_hash`;
- `scope_registry_id`, `scope_registry_version`, `scope_registry_hash`;
- `structural_rule_ids`, `deferred_matrix_row_ids`, `reason_codes`, `blocking_errors`;
- `outcome`, `eligible_for_m9_data_review`;
- `lifecycle_route_status` fixed to `not_evaluated`;
- `scope_decision_hash`.

Allowed outcomes:

| Outcome | Eligibility | Required behavior |
|---|---:|---|
| `eligible_for_data_review` | `true` | Identity is structurally within M8 scope; later evidence may still stop. |
| `unsupported` | `false` | At least one stable `SCOPE-*` reason; no alternative method, issuer, or route. |
| `insufficient_evidence` | `false` | Required structural classification is absent or contradictory; stop for review. |

Conditional invariants are enforced in schema and independently recomputed:

- `eligible_for_data_review`: eligibility is true, blocking errors are empty, exactly the
  in-scope-pending-review structural reason is present, and lifecycle rows remain deferred;
- `unsupported`: eligibility is false, at least one blocking `SCOPE-*` error is present, and every
  reason/error pair maps exactly to each matched structural rule;
- `insufficient_evidence`: eligibility is false and contains exactly the required default-deny
  missing/contradictory-classification errors for the absent predicates;
- no outcome may contain an error, reason, or rule ID that is not closed by the exact scope
  registry; all arrays are unique and canonically ordered.

Every `blocking_errors` item uses exactly the M9-I1 safe error shape and retry/action consistency
rules. Structural decision artifacts never embed raw catalog rows or provider-style payloads.

`created_at` must equal `evaluated_at` and must be no earlier than `verified_at`. Scope evaluation
rechecks the verified identity hash, listing interval, identity freshness, and catalog/policy/scope
registry effectiveness at `evaluated_at`; an identity that became stale or inactive cannot remain
eligible.

`eligible_for_data_review` is only a structural pre-screen. It is not the
`valuation-case.support_decision` defined by the M8 `valuation-case` schema and cannot satisfy,
replace, pre-approve, or populate that object. It is not a provider authorization, data-quality
conclusion, lifecycle route, or valuation authorization. M10 retains lifecycle routing and the
later human-reviewed valuation-case support decision.

### 5.7 `issuer-resolution-validation-result`

Required fields:

- `schema_version`, `canonicalization_version`, `validation_result_id`, `created_at`;
- `validator_id`, `validator_version`, `implementation_separation` fixed to `independent`;
- `subjects`, `findings`, `status`, `validation_result_hash`.

Each subject contains exactly an allowed M9-I2 artifact kind, artifact ID, and artifact hash.
Subjects are unique and sorted by `(artifact_kind, artifact_id, artifact_hash)`. Findings use the
M9-I1 safe error shape with `severity` fixed to `blocking`, are unique, and use the canonical
safe-error ordering from section 7.4. Review/warning observations belong in a separate human review
record and are not validation-result findings.

Allowed statuses and invariants:

- `passed`: all artifacts required by the actual path are present, hashes and references close,
  findings are empty, and no prohibited downstream artifact exists;
- `failed`: at least one blocking validation finding exists and no later handoff is permitted.

For a successful eligible path, subjects must close the company request, catalog, identity policy,
candidate set, selection, verified identity, structural-scope registry, and scope decision. For a
valid terminal path, subjects include only artifacts legitimately emitted before the stop. The
validation result is an integrity verdict, not a human approval, valuation output, provider
authorization, or permission to continue into M9-I3.

## 6. Versioned policy artifacts

If M9-I2 implementation is later authorized, it may introduce three strict, immutable,
default-deny data/policy artifacts governed by section 5.2:

1. a frozen synthetic catalog under the M9-I2 benchmark fixture root;
2. `registries/m9-identity-resolution-policy.yaml`;
3. `registries/m9-issuer-structural-scope.yaml`.

The identity-resolution policy must declare:

- registry and schema versions;
- query-normalization version;
- allowed match kinds and exact rank values;
- freshness calculation unit and maximum age;
- required candidate and catalog fields;
- allowed evidence assertions, public-company statuses, and derived temporal classifications;
- the synthetic adapter ID and `network_state: denied`;
- effective timestamp, expiry timestamp, reviewer evidence, status, canonicalization version, and
  exact policy hash subject.

The structural-scope registry implements only predicates determinable from M9-I2 verified identity:
public/active status, primary-listing country, reporting currency, issuer class, regulated-capital
requirement, and explicit reserve-real-option requirement. It records stable references to all M8
matrix rows, but lifecycle-dependent supported rows are marked `deferred_to_m10` and cannot be
emitted as matched M9-I2 structural rules. The registry must fail closed for unknown issuer types,
missing predicates, overlapping contradictory rules, unknown versions, pending/rejected/expired
status, or an unrecognized structural row.

The Markdown M8 support matrix remains the human contract. A machine registry cannot silently
broaden it. Review must prove closure for every structural exclusion and prove that every
lifecycle-dependent row remains explicitly deferred rather than selected.

Catalog, policy, and scope-registry collection ordering is canonical:

- catalog records: `(cik, record_id, catalog_record_hash)`;
- evidence records: `(cik, source_record_id, evidence_record_hash)`;
- review/source evidence refs: lexicographic by the complete string;
- policy match/rank entries: numeric rank then locked precedence then match-kind ID;
- scope rules: `(priority, rule_id)`, with contradictory overlapping rules rejected;
- allowed codes, countries, currencies, exchange codes, and adapter IDs: lexicographic.

Duplicate values or non-canonical order are rejected instead of silently sorted during load.

## 7. Deterministic query normalization and matching

### 7.1 Ticker

- The input must already satisfy the strict company-request ticker schema.
- Matching uses uppercase ASCII exactly; punctuation is preserved.
- No punctuation deletion, exchange inference, prefix, substring, phonetic, or fuzzy matching.
- Current and declared historical ticker fields are searched separately.
- `resolution_at = candidate_set.created_at` is the only classification instant.
- A listing is current only when `public_company_status = active`, it has qualifying
  `active_as_of` evidence, `effective_from <= resolution_at`, and `effective_to` is null. A
  non-null end after `resolution_at` is an unsupported future assertion and blocks rather than
  becoming a current interval.
- A listing is historical only when it has qualifying `closed_interval` evidence,
  `effective_to` is non-null, and `effective_to <= resolution_at`; `historical` is
  resolver-derived, never a source assertion.
- `effective_from == resolution_at` is current; `effective_to == resolution_at` is no longer
  current and is derived as historical when the closed-interval evidence rules pass.
- A future entry with `effective_from > resolution_at` cannot match, rank, or affect ticker-reuse
  calculation; its presence, or a non-null end after `resolution_at`, blocks the candidate set as
  `IDENTITY-EVIDENCE-FUTURE` so it cannot be silently ignored.
- Exactly one active listing must exist for a selectable record at `resolution_at`. A historical
  ticker match returns that record's current ticker/exchange as candidate identity and preserves
  the historical matched entry separately in `matched_listing_refs`.
- Every evidence record used by an active or matched entry, and the resulting
  `identity_observed_at`, must satisfy `observed_at <= resolution_at`; equality is allowed. A mix of
  past and future evidence blocks the whole candidate set and the future item is never ignored.

### 7.2 CIK

- Matching uses the exact ten-digit string, including leading zeros.
- Integer conversion is prohibited at the artifact boundary.
- More than one catalog identity for the same CIK is a catalog conflict, not ambiguity.

### 7.3 Company name

- Matching normalization is Unicode NFKC, trim, collapse consecutive Unicode whitespace to one
  ASCII space, then Unicode `casefold`.
- Punctuation, word order, and legal suffixes are preserved.
- Exact normalized comparison is allowed against only `legal_name` and explicitly declared aliases.
- No suffix stripping, token similarity, substring, edit distance, transliteration, web search,
  model inference, or hidden confidence score.

### 7.4 Match ranks and ordering

Locked rank values:

| Match kind | Rank |
|---|---:|
| `cik_exact` | 0 |
| `ticker_current_exact` | 0 |
| `legal_name_exact` | 0 |
| `ticker_historical_exact` | 10 |
| `declared_alias_exact` | 10 |

Candidates are deduplicated by exact `(cik, catalog_record_hash)`. Conflicting records for one CIK
block instead of deduplicating. Final ordering is ascending by:

`(match_rank, cik, exchange_code, ticker, legal_name, candidate_id)`.

After canonical catalog-array order is validated, YAML mapping order, locale, hash-map order, and
operating-system behavior must not change the result. A permuted catalog array is rejected rather
than silently reordered.

For an exact ticker query, reuse is evaluated before candidate emission across every current or
historical non-future entry matching that ticker. More than one distinct CIK blocks as
`IDENTITY-TICKER-REUSED`, even when only one match is current. Future entries never participate
because their presence already blocks under section 7.1.

Every hash-bearing collection has a locked unique order:

- `match_kinds`: locked match-kind precedence;
- candidates: the tuple above;
- artifact/source/reference arrays: lexicographic full-string order;
- safe errors: `(code, message, joined artifact_refs, next_action)`;
- structural rule IDs and deferred matrix-row IDs: validated registry order;
- reason codes: `(matched rule priority, reason_code)`;
- blocking errors: the safe-error order above.

An executor must construct these arrays directly in canonical order. A schema-valid but
non-canonically ordered artifact is rejected by the independent validator.

## 8. Identity freshness and integrity rules

- Freshness is evaluated against an injected evaluator-controlled UTC timestamp, never the
  request's untrusted `requested_at` and never an implicit wall clock.
- At verification, `identity_age_seconds = verified_at - identity_observed_at` using UTC instants.
- At structural scope evaluation, freshness is recomputed as
  `evaluated_at - identity_observed_at`; the stored verification age is not reused.
- An age equal to the policy maximum passes; an age one second greater stops.
- Candidate construction rejects any active or matched evidence with
  `observed_at > resolution_at`, including mixed past/future reference sets, as
  `IDENTITY-EVIDENCE-FUTURE`; equality passes. Verification and scope evaluation independently
  recheck that constraint as well as their own later stage times.
- Pending, rejected, expired, unknown, or hash-mismatched identity policy stops by default.
- Missing legal name, ticker, exchange code, listing dates, country, currency, issuer class,
  classification flag, public-company status, or source-record closure stops; no field is inferred.
- A CIK attached to inconsistent legal-name evidence stops as `IDENTITY-CIK-NAME-MISMATCH`.
- Multiple catalog identities using one CIK stop as `IDENTITY-CATALOG-CONFLICT`.
- Any exact ticker query matching more than one CIK across current or declared historical records
  stops as `IDENTITY-TICKER-REUSED`. Human selection cannot override ticker reuse.
- Delisted, suspended, inactive, or date-inconsistent listing evidence stops before verified
  identity handoff. The resolver cannot substitute a former or successor issuer.
- Artifact-chain order is
  `candidate_set.created_at <= selection.selected_at <= verified_identity.verified_at <=
  scope_decision.evaluated_at`. Equality is permitted for an injected fixed-clock test.
- Catalog, identity policy, and structural-scope registry intervals use
  `[effective_at, expires_at)` and must be active at every stage that consumes them.
- Listing intervals use `[effective_from, effective_to)`; a null end is open. Active status must
  hold at verification and be rechecked at structural scope evaluation.
- The untrusted company-request `requested_at` is retained and hashed but grants no freshness,
  listing, catalog, policy, or scope authority.

## 9. Structural support evaluation

M9-I2 evaluates only facts available in the verified identity and versioned structural-scope
registry.

An identity is eligible for later M9 data review only when all of the following are explicit and
consistent:

- active public listing;
- US primary listing;
- USD primary reporting currency;
- `issuer_class = operating_non_financial`;
- `regulated_capital_model_required = false`;
- `reserve_real_option_required = false`;
- no structural exclusion in the M8 matrix.

The following are unsupported and blocking when positively identified:

- bank or deposit-taking institution;
- insurer;
- broker-dealer, diversified financial intermediary, or another issuer requiring a
  regulated-capital model outside the approved FCFF framework;
- REIT;
- fund, ETF, investment company, or non-operating holding vehicle;
- SPAC or blank-check company;
- natural-resource case explicitly requiring reserve real-option valuation;
- non-US primary listing;
- non-USD primary reporting;
- private company.

An identity that cannot satisfy the verified-identity minimum—such as an explicitly private,
delisted, or inactive entity—stops in the candidate/verification stage with the applicable stable
code and emits no verified identity or scope-decision artifact. Active listed financial, foreign,
non-USD, REIT, fund, SPAC, or explicitly reserve-real-option cases may be structurally verified and
then receive an `unsupported` scope decision. This distinction never turns verification into
support approval.

The default-deny issuer taxonomy is exactly:

- `operating_non_financial`;
- `bank`, `deposit_taking`, `insurer`, `broker_dealer`,
  `other_regulated_capital_financial`;
- `reit`, `fund`, `etf`, `investment_company`, `non_operating_holding_vehicle`;
- `spac_blank_check`, `private_company`, `unknown`.

Country, currency, and exchange support are never inferred from display text. They must match exact
codes in the active policy. An exchange code not in the policy, an unknown issuer class, missing
regulated-capital or reserve-real-option flags, or contradictory classification produces
`insufficient_evidence`, not eligibility and not an invented classification. Mature, growth,
young, distressed, declining, and cyclical routing is not evaluated in M9-I2.

## 10. Stable safe-stop taxonomy

The implementation checkpoint must lock exact messages separately; messages remain bounded,
redacted, and free of raw catalog/provider content. Codes and next actions are:

| Code | Condition | Severity | Retryable | Next action |
|---|---|---|---:|---|
| `IDENTITY-NOT-FOUND` | No exact candidate. | blocking | false | `verify_identity` |
| `IDENTITY-AMBIGUOUS` | Multiple permissible candidates require a human choice. | blocking | false | `verify_identity` |
| `IDENTITY-SELECTION-REQUIRED` | No valid human selection, including a unique candidate. | blocking | false | `verify_identity` |
| `IDENTITY-SELECTION-MISMATCH` | Selection does not close to the exact candidate set/candidate. | blocking | false | `verify_identity` |
| `IDENTITY-TICKER-REUSED` | One ticker maps to more than one CIK in catalog history. | blocking | false | `update_registry` |
| `IDENTITY-CIK-NAME-MISMATCH` | CIK and legal-name evidence conflict. | blocking | false | `update_registry` |
| `IDENTITY-CATALOG-CONFLICT` | Duplicate or contradictory catalog identity. | blocking | false | `update_registry` |
| `IDENTITY-CATALOG-DENIED` | Catalog is unknown, pending, rejected, expired, or invalid. | blocking | false | `update_registry` |
| `IDENTITY-POLICY-DENIED` | Identity policy is unknown, pending, rejected, expired, or invalid. | blocking | false | `update_registry` |
| `IDENTITY-HASH-COLLISION` | Non-identical identity-key payloads produce the same derived ID/hash. | blocking | false | `stop` |
| `IDENTITY-STALE` | Identity evidence exceeds policy. | blocking | false | `update_registry` |
| `IDENTITY-EVIDENCE-FUTURE` | Evidence post-dates controlled evaluation time. | blocking | false | `update_registry` |
| `IDENTITY-DELISTED` | Listing is not active at evaluation time. | blocking | false | `stop` |
| `IDENTITY-HASH-MISMATCH` | Canonical hash or reference closure fails. | blocking | false | `stop` |
| `SCOPE-REGISTRY-DENIED` | Structural-scope registry is unknown, pending, rejected, expired, or invalid. | blocking | false | `update_registry` |
| `SCOPE-UNSUPPORTED-FINANCIAL` | Financial intermediary or regulated-capital model required. | blocking | false | `stop` |
| `SCOPE-UNSUPPORTED-REIT` | REIT. | blocking | false | `stop` |
| `SCOPE-UNSUPPORTED-FUND` | Fund/investment company/non-operating vehicle. | blocking | false | `stop` |
| `SCOPE-UNSUPPORTED-SPAC` | SPAC or blank-check company. | blocking | false | `stop` |
| `SCOPE-UNSUPPORTED-NATURAL-RESOURCE` | Reserve real-option method required. | blocking | false | `stop` |
| `SCOPE-UNSUPPORTED-NON-US` | Non-US primary listing. | blocking | false | `stop` |
| `SCOPE-UNSUPPORTED-NON-USD` | Non-USD primary reporting. | blocking | false | `stop` |
| `SCOPE-UNSUPPORTED-PRIVATE` | Private company. | blocking | false | `stop` |
| `SCOPE-INSUFFICIENT-EVIDENCE` | Structural scope facts missing or contradictory. | blocking | false | `verify_identity` |

`IDENTITY-AMBIGUOUS` is terminal for the current resolver invocation. A subsequent, explicit human
selection may continue only by binding the exact candidate-set and candidate hashes. All other
integrity, ticker-reuse, freshness, delisting, and scope stops remain non-overridable within M9-I2.

## 11. Synthetic offline adapter contract

- The resolver accepts only an already loaded, immutable, schema-valid in-memory catalog selected
  by a fixed catalog ID. It accepts no caller-supplied filesystem path.
- The test harness may map a named catalog ID to one allowlisted relative fixture beneath one fixed
  M9-I2 fixture root. It rejects absolute paths, traversal, symlinks, realpath escape, unknown IDs,
  archives, dynamic imports, and environment-variable path overrides before loading.
- It exposes no URL, hostname, credential, request, response, retry, or transport field.
- Resolver and adapter modules must not import or invoke `socket`, `urllib.request`, `http.client`,
  `requests`, `httpx`, `aiohttp`, browser/provider clients, `subprocess`, shell helpers,
  `os.system`, dynamic import/exec/eval, or any provider SDK.
- The default test suite must pass with network disabled and with no credentials.
- Fixtures use conspicuously fictitious names, tickers, exchanges, actors, and records. Ten-digit
  synthetic CIK-shaped identifiers are test data only and are not copied from a real issuer.
- Fixture payloads are compact, original, redistributable, and contain no filing facts, provider
  response, PDF, ebook, private extract, or user file.
- The adapter returns data only. It cannot select, verify, approve, suppress an error, alter a
  policy, or expand an allowlist.

## 12. Independent validation boundary

The M9-I2 independent validator must not import production resolver, normalization, candidate
ordering, selection, identity-construction, or scope-evaluator helpers. It may use the existing
M9-I1 implementation-separated canonical hash module.

It independently recomputes:

- company-request hash and schema validity;
- query normalization, exact match set, match kinds, rank values, deduplication, and stable order;
- resolution instant, half-open current/historical/future classification, active-listing uniqueness,
  historical-match/current-identity separation, and temporal ticker-reuse result;
- candidate record hashes and candidate-set hash;
- catalog/policy/scope-registry schemas, duplicate-key rejection, canonical collection order,
  identity, status, effective interval, expiry, review closure, and content hashes;
- evidence-to-listing CIK/name/ticker/exchange/assertion/start/end/`fact_as_of`/`observed_at`
  closure, including retrospective closed-interval evidence;
- evidence causality at `resolution_at`, including equality, mixed-time sets, and independently
  derived current/historical/future classification;
- ambiguity, ticker reuse, CIK/name mismatch, delisting, future evidence, and freshness boundaries;
- human actor type, selected membership, selected hash, and selection hash;
- exact copying of selected identity fields and verified-identity hash;
- structural-scope predicates, deferred M10 rows, outcome, eligibility boolean, and scope-decision
  hash;
- full reference closure and absence of unknown/cyclic/non-finite content;
- absence of downstream artifacts after any blocking stop;
- validation-result subject closure, conditional status/findings, canonical order, and result hash.

Tests must demonstrate implementation separation through import-graph inspection and mutation
kill tests. A validator that merely calls the production resolver or scope evaluator does not
satisfy this contract.

## 13. Required regression and adversarial tests

### Schema and canonicalization

- accept each minimal valid artifact and reject every unknown field;
- reject invalid IDs, CIKs, tickers, hashes, timestamps, enums, duplicate keys/refs, non-canonical
  arrays, and non-human actor;
- reject missing hash subjects, cyclic/non-finite values, unknown canonicalization versions, and
  mismatch between production and independent hashes;
- prove nested mutation invalidates every affected downstream artifact;
- validate passed/failed independent-result subjects, findings, ordering, reference closure, and
  result-hash mutation; reject review/warning validation findings.

### Resolution

- exact CIK, exact current ticker, exact legal name, historical ticker, and declared alias;
- resolution at exact `effective_from` and exact `effective_to` boundaries, null-ended current
  listing, future-start/future-end rejection, and no-active/multiple-active listing rejection;
- historical ticker returns the current identity while retaining exact historical match evidence;
- temporal ticker reuse across current/current, current/historical, and historical/historical
  records, with future entries excluded only through the required blocking stop;
- evidence mutation tests for ticker mismatch, exchange mismatch, assertion-kind mismatch,
  start/end mismatch, invalid `fact_as_of`, `observed_at < fact_as_of`, active evidence after
  `resolution_at`, historical matched evidence after `resolution_at`, mixed past/future refs,
  missing current evidence, and substitution of historical evidence for current identity;
- NFKC, whitespace collapse, and casefold vectors without punctuation/suffix stripping;
- no match for prefix, substring, spelling distance, transliteration, or undeclared alias;
- deterministic output on repeated canonical input; a permuted non-canonical catalog is rejected
  instead of normalized silently;
- listing-history canonical ordering uses the actual `listing_entry_hash` tie-breaker; mutated hash
  or non-canonical order is rejected;
- stable deterministic candidate IDs, multi-match precedence, tie ordering, duplicate-candidate
  suppression, and synthetic hash-collision rejection;
- no candidate for empty or schema-invalid queries.

### Required M9-I2 stop cases

- ambiguous name with two candidates: blocking stop, no automatic selection;
- explicit human selection resolves permissible ambiguity and closes exact hashes;
- unique candidate still blocks until a human confirmation exists;
- ticker reuse across two CIKs: non-overridable blocking stop;
- duplicate CIK or CIK/name mismatch: blocking catalog error;
- stale identity exactly at boundary passes; one second beyond stops;
- future-dated identity, delisted identity, invalid effective interval, and hash mutation stop;
- reversed chain timestamps, expired policy/catalog/registry at each consuming stage, and replayed
  identity that becomes stale between verification and scope evaluation stop;
- unsupported bank, insurer, REIT, fund, SPAC, reserve real-option case, non-US primary listing,
  non-USD primary reporting, and private company all produce stable `SCOPE-*` stops; the private
  case emits no verified identity while active listed excluded classes may emit an unsupported
  scope decision;
- unknown/contradictory issuer class, regulated-capital flag, reserve-real-option flag, exchange
  code, country, or currency produces insufficient evidence, never eligibility;
- supported synthetic non-financial US/USD issuer produces only `eligible_for_data_review`, never a
  lifecycle route or valuation output.

### Authority and scope

- socket/DNS/network monkeypatch proves zero direct or indirect calls;
- AST/import scan proves no transport, shell, subprocess, dynamic-execution, browser, or provider
  SDK imports/calls;
- fixture tests reject caller paths, absolute paths, traversal, symlinks, realpath escape,
  environment overrides, unknown catalog IDs, and archives;
- resolver/adapter attempts to set human selection are rejected;
- selection of a candidate outside the bound set, changed order, changed catalog, or changed policy
  is rejected;
- blocked identity produces no verified identity; unsupported identity produces no later M9
  acquisition handoff;
- artifacts contain no advice, trading action, valuation, route approval, provider approval,
  territory approval, `case_lock`, or `output_approval`;
- repository policy scan finds no PDF, ebook, private extract, credential, real issuer fixture, or
  provider payload.

### Regression

- all M1-M8 validators and tests remain green;
- all M9-I1 tests remain green without changing canonicalization, errors, or registry semantics;
- complete suite passes on Python 3.10 and 3.12;
- all-candidate pre-commit checks pass without rewriting files.

## 14. Proposed implementation footprint — not authorized

If and only if later authorized, the expected bounded footprint is:

- eight schemas listed in section 5;
- `registries/m9-identity-resolution-policy.yaml`;
- `registries/m9-issuer-structural-scope.yaml`;
- `tools/retail_data/identity_contracts.py`;
- `tools/retail_data/resolution.py`;
- `tools/retail_data/structural_scope.py`;
- a separate `tools/validate_issuer_resolution.py`;
- compact synthetic fixtures and expected artifacts under an M9-I2 benchmark directory;
- focused unit, integration, adversarial, mutation, and composition tests;
- a later M9-I2 implementation-review record.

This list is an architecture estimate, not permission to create or edit any repository path.
Implementation must not modify M1-M7 public contracts or place resolution behavior in M9-I1
modules merely to avoid the separate M9-I2 authorization gate.

## 15. Contract acceptance gates

The contract may be recommended for approval only if independent review confirms:

1. all eight catalog, policy, registry, output, and validation-result boundaries are strict,
   deterministic, and hash-closed;
2. every issuer selection is human and bound to the exact candidate set and candidate;
3. ambiguity can continue only through an explicit later selection step, while ticker reuse,
   integrity, freshness, delisting, and scope failures cannot be overridden;
4. structural scope pre-screening cannot choose a lifecycle route, satisfy the M8
   `valuation-case.support_decision`, or value a company;
5. the structural-scope registry cannot broaden the M8 issuer matrix and explicitly defers every
   lifecycle-dependent row to M10;
6. the independent validator recomputes rather than delegates production behavior;
7. all tests are offline and synthetic and no real/private/provider material is required;
8. M9-I3 through M9-I6, live access, provider activation, and product interfaces remain excluded;
9. M1-M7 composition, exact-hash handoffs, human approvals, and separation of duties remain intact;
10. M8-C01 through M8-C07 remain active and unsatisfied unless separately evidenced later.

## 16. External review and approval state

This document is a frozen contract payload. It must not contain mutable checkboxes, reviewer
decisions, or project-owner approval claims because any such edit changes its SHA-256. Its
authoritative governance state is recorded separately in
`docs/milestones/M9-I2-contract-lock-review-approval-record.md` and is valid only when that record
names this repository-relative path and the SHA-256 of these exact UTF-8 bytes.

The external state machine is:

1. `candidate`: the contract bytes are frozen, but no independent-review verdict applies to their
   exact SHA-256; implementation and publication are not authorized;
2. `independently_reviewed`: an independent reviewer records `PASS` against the exact contract
   SHA-256 and review baseline; project-owner approval is still absent, and implementation and
   publication remain unauthorized;
3. `owner_approved`: the project owner explicitly approves that same exact SHA-256 after the
   independent `PASS`; this approves only the contract boundary;
4. `superseded`: any byte change, replacement candidate, later owner decision, or incompatible
   baseline invalidates reliance on the earlier state for the changed artifact. Prior review and
   approval remain historical evidence but never transfer to a new SHA-256.

The review/approval record must preserve the prior SHA lineage, the independent verdict and date,
the project-owner decision and date, and any publication blocker. Missing, contradictory, pending,
or hash-mismatched fields fail closed to `candidate`. Status prose elsewhere in the repository is
informational and cannot replace the exact-SHA-bound record.

Project-owner approval of an exact SHA-256 would approve only the M9-I2 contract boundary.
Separate, explicit authorization would still be required for implementation, staging, committing,
pushing, creating a Draft PR, Mark Ready, approval, merge, M9-I3 or later work, any live-readiness
test, provider use, real-company data, and release.

No attached PDF, original extract, continuous source text, long quotation, private-source content,
real issuer data, or live provider response was read or used to prepare this candidate.
