# M9-I5 US-GAAP Normalization and Reconciliation Contract Review

Contract: `docs/milestones/M9-I5-us-gaap-normalization-reconciliation-contract-lock.md`
Status: `LOCAL_REVIEW_CHECKLIST_CANDIDATE`; no verdict or approval recorded
Review baseline: `main@8cb0e7032ea5de265b883d5d9a36fe0f8988ad1e`

## Authority and frozen boundaries

- [ ] Review is bound to the exact contract SHA-256 and exact main baseline.
- [ ] Contract design is not represented as implementation, normalized handoff, or live authority.
- [ ] Network state is denied and all M9-I4 public adapters remain stopped before transport.
- [ ] Provider/concept registries and inherited M8/M9 schemas remain byte-for-byte unchanged.
- [ ] Provider activation, credentials, real-company data, attachments, M9-I6, M10+, and release remain excluded.

## Concept and source-fact controls

- [ ] Exactly 13 inherited concept IDs are present once, in canonical order, with exact registry closure.
- [ ] The mapping artifact requires the exact frozen concept-registry SHA-256, not any shaped hash.
- [ ] Unknown concepts, aliases, wildcard mappings, implicit creation, and cross-concept authority fail closed.
- [ ] Mapping records lock kind, unit, period type, polarity, aggregation, source tags, and review status.
- [ ] Zero-padded source-tag priority keys make duplicate priority authority unrepresentable after duplicate-key rejection.
- [ ] Approved standard mappings require an exact human-review decision reference and hash.
- [ ] Taxonomy namespace/version and synthetic source-fact envelopes are exact and hash-bound.
- [ ] Filing labels, calculation links, dimensions, and custom tags are treated as untrusted data.
- [ ] Custom tags require exact issuer/taxonomy/fact-scoped immutable human mapping evidence.
- [ ] Custom-tag decision artifacts require a human actor, exact scope copies, standard anchor, and self-hash.

## Numeric, unit, scale, and sign controls

- [ ] Canonical decimal strings reject float authority, exponent notation, non-finite values, locale forms, and negative zero.
- [ ] Decimal strings are bounded and reconciliation tolerances are canonical and nonnegative.
- [ ] Scale is applied exactly once; decimals records precision and cannot rescale a fact.
- [ ] USD, ratio, and shares are the only supported units and foreign currency is not converted.
- [ ] Reported sign is preserved and only explicit polarity may transform it once.
- [ ] Missing/rejected values are never filled with zero, peer, old filing, forecast, LLM estimate, or override.

## Period, amendment, and duplicate controls

- [ ] Instant/duration dates, fiscal labels, duration days, graph IDs, and edges are deterministic.
- [ ] Period graph reference closure, basis/cardinality, acyclicity, no overlap/gap, and no mixed calendar/lineage are enforced.
- [ ] 52/53-week years, stubs, calendar changes, and missing quarters remain explicit findings.
- [ ] Amendments supersede only an exact compatible lineage and cannot field-level patch older accessions.
- [ ] Duplicate collapse requires identical scaled value, unit, context, dimensions, period, and accession.

## Derived facts, shares, and reconciliations

- [ ] Only the five locked calculation rules are permitted and every operand/source is explicit.
- [ ] Material discontinuities are separated and never silently netted into normal operations.
- [ ] Share basis and split factors/effective dates are explicit; double or inferred adjustments stop.
- [ ] All ten reconciliation families are present when applicable with explicit canonical tolerances.
- [ ] Every result accounts for all ten families; non-applicable checks carry only a bounded reason and no fact/difference.
- [ ] Tolerances cannot hide unit, period, sign, duplicate, custom-tag, or authority defects.
- [ ] Complete/needs-review/unsupported quality states enforce their exact fail-closed invariants.
- [ ] `complete` cannot omit any of the 13 concepts or any required reconciliation family.

## Independent validation and evidence

- [ ] Validator imports no production mapper, period, decimal, normalization, reconciliation, custom-tag, split, or hash helper.
- [ ] Validator independently recomputes hashes, references, graph, decimals, mappings, derivations, reconciliations, and quality.
- [ ] Coordinated downstream rehashing cannot conceal upstream, arithmetic, period, mapping, or authority tamper.
- [ ] AST/import controls deny network, provider SDK, subprocess, shell, dynamic execution, and M9-I4 activation.
- [ ] Schemas are Draft 2020-12, strict at every object, bounded, finite, and reject unknown fields.
- [ ] Adversarial contract tests cover unknown fields, wrong authority, schema weakening, concept drift, custom-tag bypass, and silent fill.
- [ ] Stable finding codes and bounded safe messages cannot leak raw labels, URLs, bodies, credentials, or stack traces.
- [ ] Focused tests, full suite, workflow validators/policy, Python 3.10/3.12 CI, and `git diff --check` are required before publication.

Review recommendation:
`[ ] PASS  [ ] COMMENTED_BLOCKING  [ ] request changes`

No box is preselected. A later review must record findings and a disposition outside the frozen
contract payload and must not claim independence when reviewer/author separation did not occur.
