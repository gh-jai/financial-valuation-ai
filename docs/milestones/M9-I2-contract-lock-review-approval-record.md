# M9-I2 Contract Lock — Review and Approval Record

Status: `owner_approved_with_exception`; first-stage immutable owner attestation verified
Post-owner-approval package closure: `NOT_CLOSED`
Contract path: `docs/milestones/M9-I2-issuer-resolution-contract-lock.md`
Contract SHA-256: `9326b6c76dcfe3061c5e356b5141d9f458d57694cb4e6b01b6470b0bf044d84e`
Review baseline: `3945e90559ec2e10771489078c9e8f52036209b7`
Record date: 2026-08-09
Current operational implementation milestone: M7
Network and data state: Denied; synthetic offline design only

## Purpose and authority

This record carries the mutable governance state for the frozen M9-I2 contract payload. A review or
approval applies only when the contract path and recomputed SHA-256 exactly match the values above
and the event evidence satisfies the durable-evidence requirements below. This record does not
authorize M9-I2 runtime implementation, staging, committing, pushing, creating or changing a pull
request, live SEC/provider access, provider activation, real-company data, attachments, or M9-I3
through M9-I6.

Repository status summaries are informational. If they conflict with this record, if the contract
hash does not match, or if required event evidence is absent, the contract fails closed to
`candidate`. Contract approval and post-owner-approval package closure are separate decisions. The
latter is authoritative only in
`docs/milestones/M9-I2-post-owner-approval-snapshot-closure.md`.

## Exact-SHA lineage

| Contract SHA-256 | Historical assertion | Auditable governance state | Repository-use state |
|---|---|---|---|
| `4bb47ef11c645f8f38f1112c433d63e8670ae5fe48a7896bb325d86d122f7d7b` | Five review rounds, 16 findings resolved, and owner approval were recorded on 2026-08-09. | Historical only; superseded bytes and no durable event references. | Superseded for repository publication after documentation/governance findings. |
| `4c596e806896a9693dd95766b7f5d3207c7f0969ee69e4aeeed05ab5e1e016ad` | A contract review `PASS` and exact-SHA owner approval were recorded on 2026-08-09. | Historical only; actor identifiers, UTC event timestamps, immutable evidence references, and a verifiable event chain were not preserved. | Superseded by the contract that defines the single-maintainer exception. |
| `9326b6c76dcfe3061c5e356b5141d9f458d57694cb4e6b01b6470b0bf044d84e` | A narrow two-stage single-maintainer documentation-governance exception is defined. | `owner_approved_with_exception`; the first-stage immutable attestation and its exact-subject-commit CI evidence are verified below. | Frozen contract approved only under the disclosed exception. Publication, implementation, and package closure remain separately unauthorized. |

The historical assertions explain the document's provenance but grant no current authority. They
must not be promoted to `independently_reviewed` or `owner_approved` without fresh durable evidence.

## Durable event evidence requirements

Every review or approval event used by the external state machine must preserve all of the
following in an append-only, independently retrievable artifact:

- a unique `event_id` and the prior event's hash or an explicit genesis marker;
- an RFC 3339 UTC `occurred_at` timestamp with a terminal `Z`;
- a bounded `actor_id`, `actor_role`, and human/agent boundary;
- the exact repository, baseline, subject path, and subject SHA-256;
- the verdict or decision and its authority boundary;
- an immutable artifact reference plus the SHA-256 of the referenced evidence bytes; and
- an event hash computed over all event fields other than the event hash itself.

For the default path, the independent reviewer `actor_id` must differ from every authoring or
remediation actor for the reviewed bytes, and owner approval must reference that earlier `PASS` for
the same exact contract SHA-256. Dates without times, role labels without actor identifiers, and
prose in the same commit as a claimed independent decision are not sufficient evidence.

The alternative single-maintainer path does not claim independence. It requires two ordered public
attestations containing the exception fields in contract section 16.1: a
`contract_owner_attestation`, then a `snapshot_closure_attestation` after this record is updated.
Both must disclose the shared author/remediator identity, explicit separation waiver,
exact-subject-commit CI evidence, complete-suite result, finding disposition, residual-risk
acceptance, and narrow authority boundary. The evidence reference must be an immutable Git object;
a mutable PR body or ordinary comment is insufficient. Missing any required field fails closed.

## Historical pre-owner-review assertion

- Asserted reviewed contract SHA-256, now superseded:
  `4c596e806896a9693dd95766b7f5d3207c7f0969ee69e4aeeed05ab5e1e016ad`
- Asserted verdict/date: `PASS`, 2026-08-09
- Asserted reviewer boundary: independent documentation/governance reviewer
- Preserved actor identifier: **missing**
- Preserved UTC event timestamp: **missing**
- Immutable review artifact reference and evidence hash: **missing**
- Verifiable event ID/hash-chain link: **missing**
- Governance result: does not advance the exact SHA beyond `candidate`

Any future independent review must be a new event. It must not backfill an invented identity,
timestamp, or evidence reference for the historical assertion.

## Historical project-owner approval assertion

- Asserted approval subject:
  `4c596e806896a9693dd95766b7f5d3207c7f0969ee69e4aeeed05ab5e1e016ad`
- Asserted decision/date: `APPROVED`, 2026-08-09
- Preserved owner actor identifier: **missing**
- Preserved UTC event timestamp: **missing**
- Immutable approval artifact reference and evidence hash: **missing**
- Verifiable reference to a qualifying earlier review event: **missing**
- Governance result: does not advance the exact SHA to `owner_approved`

A fresh project-owner decision for the current SHA may follow either the default independent path
or the explicit single-maintainer path. The latter must be recorded as
`owner_approved_with_exception`, not `independently_reviewed` or unqualified `owner_approved`.
Either decision would cover only the frozen contract boundary and would not authorize publication
or implementation.

## Current single-maintainer exception decision

The canonical repository and PR are operated through project-owner identity `github:gh-jai`, which
is also the author/remediator identity for the frozen contract bytes. No eligible independent
reviewer was reasonably available. The owner therefore exercised the narrow exception without
claiming reviewer/author separation or independent review.

The qualifying first-stage evidence is:

- immutable subject commit: `743159d08ab05541a8d4fe25859bc9f9a49c5287`;
- successful exact-subject-commit CI: `Validate` run
  [#66](https://github.com/gh-jai/financial-valuation-ai/actions/runs/31313816548), with Python 3.10
  and 3.12 each passing 334 tests and all nine focused M9-I2 governance regressions;
- immutable attestation commit: `a406b5fc5cfded19f116cc42309da13cea42c713`;
- immutable attestation reference:
  `https://github.com/gh-jai/financial-valuation-ai/blob/a406b5fc5cfded19f116cc42309da13cea42c713/docs/milestones/M9-I2-contract-owner-attestation.md`;
- attestation Git blob: `0011df140cfb44af244526b0feb3d71a8c40cdd6`;
- attestation SHA-256: `daba23aa09e9c6e3e13ed983518ecf44d4698160e38693c72357ed19b14f1a75`;
- event ID: `m9-i2-contract-owner-attestation-20260809T124450Z`;
- event hash: `1c0a77e77fd3ecc755d86c0d0db3c229d5194be63eb87af5bd4984520506df83`;
- immutable-attestation validation: `Validate` run
  [#67](https://github.com/gh-jai/financial-valuation-ai/actions/runs/31314762621), with Python 3.10
  and 3.12 each passing 337 tests, all 12 focused M9-I2 governance regressions, and repository
  policy over 343 candidate files; and
- finding disposition: no unresolved blocking, high, or medium finding remained against the exact
  contract subject commit.

The attestation's canonical event discloses the shared owner/author/remediator identity, explicitly
waives separation only for M9-I2 contract/documentation governance, accepts the residual risk from
loss of independent challenge, and denies implementation, publication, data, release, and later
qualified-review authority. Its event hash, evidence hash, contract SHA-256, and immutable Git
objects were independently recomputed after publication. The contract state is therefore
`owner_approved_with_exception`, never `independently_reviewed` or unqualified `owner_approved`.

This record update creates a new subject snapshot. That snapshot still requires its own immutable
subject commit, successful exact-subject-commit CI, complete validation, zero unresolved
blocking/high/medium findings, and a later immutable `snapshot_closure_attestation`. The first-stage
event cannot close the later snapshot, so package closure remains `NOT_CLOSED`.

## Post-owner-approval exact-snapshot closure

The authoritative closure assessment is
`docs/milestones/M9-I2-post-owner-approval-snapshot-closure.md`. Package closure remains
`NOT_CLOSED` unless all subject hashes and the snapshot ID recompute and one complete durable path
is established. The default path requires independent contract review, later exact-SHA owner
approval, post-approval remediation/validation, and an independent exact-snapshot `PASS`. The
alternative path requires the two ordered immutable attestations in section 16.1, successful
exact-subject-commit CI at each stage, complete validation, no unresolved blocking/high/medium
findings, and an exact-snapshot decision explicitly named
`CLOSED_WITH_SINGLE_MAINTAINER_EXCEPTION`.

Any change to a subject file invalidates an earlier snapshot closure. Neither a closed snapshot nor
contract approval would authorize publication or implementation.

## Current verification state

- [x] Contract SHA-256 recomputes to the frozen approved-with-exception value.
- [x] No M9-I2 runtime, live provider access, real-company material, or attachment content is added.
- [x] A bounded single-maintainer documentation-governance exception is defined without weakening
      M1-M7 runtime separation or later qualified-review gates.
- [x] A qualifying immutable `contract_owner_attestation` exists for
      the exact contract SHA-256 and immutable subject commit.
- [x] First-stage exact-subject-commit remote CI and complete validation evidence are durably
      referenced.
- [x] No unresolved blocking, high, or medium finding remains against the first-stage subject
      commit.
- [ ] A later `snapshot_closure_attestation` binds the final subject snapshot.
- [ ] Package closure is established.

## Source boundary

No attached PDF, original extract, continuous source text, long quotation, private-source content,
real issuer data, or live provider response was read or used to produce this record.
