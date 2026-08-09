# M9-I2 Post-Owner-Approval Exact-Snapshot Closure

Status: `NOT_CLOSED`; neither the default nor single-maintainer evidence path is complete
Evidence assessment date: 2026-08-09
Review baseline: `3945e90559ec2e10771489078c9e8f52036209b7`
Current operational implementation milestone: M7
Contract authority: `candidate`; single-maintainer exception policy defined, attestation pending
Publication authority: `DENIED`; separate explicit authorization required
Runtime and data authority: `DENIED`; no M9-I2 implementation, live/provider access, real-company
data, attachment use, or M9-I3 through M9-I6 authority

## Closure model

This record assesses only an exact documentation snapshot. It does not alter the contract bytes or
transfer a review or approval to another SHA-256. The subject snapshot consists of the five files
in the ordered manifest below. This carrier is outside the subject snapshot so that evidence and a
future verdict can be appended without creating a self-referential file hash.

Closure is valid only when:

- every subject-file SHA-256 matches;
- the snapshot ID recomputes from the exact UTF-8 manifest block;
- every relied-on governance event has an actor identifier, RFC 3339 UTC timestamp, exact subject,
  immutable evidence reference and evidence hash, prior-event link, and recomputable event hash;
- one complete governance path is mechanically verifiable: either independent contract review
  before exact-SHA owner approval followed by remediation, validation, and independent
  exact-snapshot review; or the bounded single-maintainer exception described below;
- reviewer/remediator identity separation is mechanically checkable on the default path, while
  the exception path explicitly discloses the shared identity and narrow separation waiver; and
- the exact-snapshot decision returns `PASS` with no blocking, high, or medium findings and uses
  the state name required by the selected path.

Any mismatch or missing event evidence fails closed to `NOT_CLOSED`. The carrier SHA-256 must be
reported with any handoff. Changing this carrier does not change the subject snapshot ID, but it
invalidates a prior carrier handoff until the new bytes are independently checked.

## Ordered subject manifest

The snapshot ID is SHA-256 over the bytes between `BEGIN SUBJECT MANIFEST` and
`END SUBJECT MANIFEST`, excluding both delimiter lines and including the final newline after the
last manifest row. Paths are repository-relative, ordered exactly as shown, and separated from
lowercase SHA-256 values by one ASCII space.

```text
BEGIN SUBJECT MANIFEST
9326b6c76dcfe3061c5e356b5141d9f458d57694cb4e6b01b6470b0bf044d84e docs/milestones/M9-I2-issuer-resolution-contract-lock.md
47141591752ac078c9aafea377f4e04c99baa4b0c7786faa80e5706127bc4448 docs/milestones/M9-I2-contract-lock-review-approval-record.md
093c12abd3b65f895c27e32faabbb584ca0214a695a438e514351431a1686200 PROJECT_STATUS.md
13ab4e5a354932ba771857a33a381eeb64d1b4c44180cb8f1c03c25684833e67 ROADMAP.md
544b88549d29e6712d683df5d225ba213766eb8247be335e27bdfe387056f2ec README.md
END SUBJECT MANIFEST
```

Subject snapshot ID: `c2f3abc9ee6e1ce08938467c654ae65b86bfdf143ade244b7bb4688c077377d6`

Recompute from the repository root:

```bash
sha256sum \
  docs/milestones/M9-I2-issuer-resolution-contract-lock.md \
  docs/milestones/M9-I2-contract-lock-review-approval-record.md \
  PROJECT_STATUS.md ROADMAP.md README.md
sed -n '/^BEGIN SUBJECT MANIFEST$/,/^END SUBJECT MANIFEST$/p' \
  docs/milestones/M9-I2-post-owner-approval-snapshot-closure.md \
  | sed '1d;$d' | sha256sum
```

## Required durable event record

Every event relied on for closure must be preserved in an append-only artifact with these fields:

| Field | Requirement |
|---|---|
| `event_id` | Unique bounded identifier. |
| `occurred_at` | RFC 3339 UTC timestamp ending in `Z`; strict ordering uses the instant, not a date label. |
| `actor_id` | Stable bounded actor identifier; role-only labels are insufficient. |
| `actor_role` | One of contract author, independent reviewer, project owner, remediator, validator, or exact-snapshot reviewer. |
| `actor_type` | Human or agent, without implying authority from the type alone. |
| `repository` | Exact canonical repository. |
| `baseline_sha` | Exact review baseline commit. |
| `subject_kind` | Contract, owner decision, remediation snapshot, validation result, or exact snapshot. |
| `subject_id` | Exact contract SHA-256, snapshot ID, or decision/event ID as applicable. |
| `decision` | Bounded verdict/decision plus its authority boundary. |
| `evidence_ref` | Independently retrievable immutable artifact reference, not prose in this carrier. |
| `evidence_sha256` | SHA-256 of the referenced evidence bytes. |
| `previous_event_hash` | Prior event hash or an explicit genesis marker. |
| `event_hash` | SHA-256 over every event field except `event_hash`. |

An owner-approval event must name the exact earlier independent-review `event_id` and event hash.
An exact-snapshot review must name the remediation and validation events and use an `actor_id`
different from every actor that changed the reviewed subject bytes. A single commit containing the
claims and their supposed proof does not independently establish occurrence, separation, or order.

## Single-maintainer exception evidence

The alternative path exists only for M9-I2 documentation/contract governance when no eligible
independent reviewer is reasonably available. It must never be represented as independent review
and cannot waive M1-M7 runtime separation, human approval, or any later qualified legal, privacy,
security, accessibility, provider-license, or real-company gate.

Each of the two ordered public owner attestations must include and bind:

| Field | Requirement |
|---|---|
| `exception_id` | Unique identifier scoped to this contract SHA and, for closure, snapshot. |
| `decision_kind` | First `contract_owner_attestation`, then `snapshot_closure_attestation`. |
| `eligibility_reason` | Why the repository is single-maintainer and no eligible independent reviewer was reasonably available. |
| `shared_actor_disclosure` | Exact owner/author/remediator actor ID and an explicit statement that separation did not occur. |
| `separation_waiver_scope` | M9-I2 documentation governance only; no runtime or qualified-review waiver. |
| `subject_commit_sha` | Immutable commit containing the exact contract or subject-snapshot bytes. |
| `contract_sha256` and `snapshot_id` | Exact recomputable subjects of the decision. |
| `ci_evidence` | Successful exact-subject-commit workflow run IDs and immutable URLs. |
| `local_validation_evidence` | Full command/result, runtime versions, focused regressions, hook composition, and `git diff --check`. |
| `finding_disposition` | Explicitly no unresolved blocking, high, or medium finding against the exact subject commit. |
| `residual_risk_acceptance` | Owner accepts the loss of independent challenge and records why proceeding is proportionate. |
| `authority_boundary` | Contract/documentation decision only; all implementation, publication, data, and release actions remain separately gated. |
| `evidence_ref` and `evidence_sha256` | Immutable Git object and supporting-evidence hash; mutable PR prose or an ordinary comment is insufficient. |
| `previous_event_hash` and `event_hash` | Genesis/prior link and recomputable hash over the complete attestation. |

Only the first event may advance the contract to `owner_approved_with_exception`. After the
approval record is updated and the subject manifest is recomputed, only the second event may
advance that exact snapshot to `CLOSED_WITH_SINGLE_MAINTAINER_EXCEPTION`. The unqualified states
`independently_reviewed`, `owner_approved`, and `CLOSED` are forbidden on this path. Any subject-file
change invalidates the snapshot attestation and returns the changed package to `NOT_CLOSED`. A
later carrier-only update may reference the second immutable event because the carrier is outside
the subject manifest; it must not alter any subject file.

## Current evidence assessment

The prior carrier asserted six events using only one date and role labels. It did not preserve the
minimum durable fields:

| Claimed event | Actor ID | UTC timestamp | Immutable evidence ref/hash | Event-chain link | Result |
|---|---|---|---|---|---|
| Contract review `PASS` | Missing | Missing | Missing | Missing | Not auditable |
| Exact-SHA project-owner approval | Missing | Missing | Missing | Missing | Not auditable |
| Package review with required changes | Missing | Missing | Missing | Missing | Not auditable |
| Documentation remediation | Missing | Missing | Missing | Missing | Not auditable |
| Local validation | Missing | Missing | Missing | Missing | Not auditable |
| Exact-snapshot review `PASS` | Missing | Missing | Missing | Missing | Not auditable |

The branch commit `5a7e5cb2a09806b6545e9837078ed60374c5187b` is immutable evidence of the
published documentation bytes and Git identity only. Because all six files were introduced in that
single commit, it does not prove that the claimed review preceded approval, that reviewers were
separate from authors/remediators, or that a pre-attestation carrier existed.

The earlier pre-attestation SHA-256
`770929fe7a7b2bfcfa7710fa38bd60733f62e5ff553c9abbf7cf8e929bff12ee` is retained as a historical
assertion. No independently retrievable artifact containing those exact bytes was preserved, so
the value cannot serve as closure evidence.

The current single-maintainer policy change has not yet been committed, pushed, validated by
exact-subject-commit remote CI, or covered by an immutable `contract_owner_attestation`.
Eligibility to use the exception is not evidence that the exception was exercised. The later
`snapshot_closure_attestation` is necessarily absent as well. The current package therefore
remains `NOT_CLOSED`.

## Historical validation and attestation assertions

The prior carrier recorded 325 passing tests and all 16 configured pre-commit hooks for the earlier
snapshot. The configuration consists of six upstream hooks plus all 10 local hooks, including
repository policy. That wording replaces the earlier imprecise statement that counted repository
policy separately from the 10 local hooks.

Those test results are useful historical execution evidence but cannot repair missing review or
approval provenance. Changes made during remediation also require fresh validation against the new
subject snapshot.

Remediation validation for the now-superseded subject snapshot
`0dee9d0aa63672b29e95ad9d4d51add36484197fae8662f18dbe0735f939536c` completed in the local
workspace on Python 3.12.13 with pytest 8.4.2:

- all-candidate pre-commit: `PASS`; all 16 configured hooks passed without rewriting files;
- hook composition: six upstream hooks and 10 local hooks, including repository policy;
- full pytest suite: `PASS`; 331 tests passed;
- focused governance regressions: `PASS`; six tests passed; and
- `git diff --check`: `PASS`.

These results demonstrate reproducibility of the earlier remediated bytes. The single-maintainer
policy changes alter the contract and documentation snapshot, so fresh validation is required and
will be recorded only after the final local bytes pass. The earlier results cannot close the new
snapshot.

Current local validation for subject snapshot
`c2f3abc9ee6e1ce08938467c654ae65b86bfdf143ade244b7bb4688c077377d6` completed in the local
workspace on Python 3.12.13 with pytest 8.4.2:

- focused M9-I2 governance regressions: `PASS`; nine tests passed;
- all-candidate pre-commit: `PASS`; all 16 configured hooks passed without rewriting files;
- hook composition: six upstream hooks and 10 local hooks, including repository policy;
- full pytest suite: `PASS`; 334 tests passed; and
- `git diff --check`: `PASS`.

This is reproducibility evidence for the current uncommitted bytes, not exact-subject-commit remote
CI or either immutable owner attestation. It does not advance the contract beyond `candidate` or
the package beyond `NOT_CLOSED`.

The prior exact-snapshot `PASS` is retained only as a historical assertion. It has no actor ID, UTC
timestamp, immutable evidence reference, or event-chain link and therefore grants no closure state.
It must not be silently upgraded by adding invented metadata after the fact.

## Required path to closure

The preferred default path remains:

1. record a fresh independent contract review for the exact contract SHA-256;
2. record a later project-owner decision naming that review;
3. recompute and validate the exact post-approval snapshot; and
4. obtain a separate exact-snapshot `PASS` and verify the complete event chain.

When no eligible independent reviewer is reasonably available, the alternative path is:

1. commit and publish the exact contract/documentation candidate without declaring it approved;
2. obtain successful remote CI and complete validation for that immutable subject commit, then
   publish an immutable `contract_owner_attestation` satisfying every exception field and advance
   only the contract state to `owner_approved_with_exception` in the approval record;
3. publish that approval-record update, recompute the subject manifest, obtain successful remote CI
   for the new immutable subject commit, and confirm no unresolved blocking/high/medium finding;
4. publish a separate immutable `snapshot_closure_attestation` bound to that exact subject commit
   and snapshot ID; and
5. update only this out-of-manifest carrier to reference the second event and record
   `CLOSED_WITH_SINGLE_MAINTAINER_EXCEPTION`, without altering a subject file.

Until every selected-path step is satisfied, the exact subject snapshot is `NOT_CLOSED`. No closure
state authorizes publication, implementation, network/provider use, real-company data,
attachments, or a later milestone.

## Source boundary

No attached PDF, original extract, continuous source text, long quotation, private-source content,
real issuer data, or live provider response was read or used to produce this record.
