# M9-I2 Post-Owner-Approval Exact-Snapshot Closure

Status: `NOT_CLOSED`; durable review/approval provenance is incomplete
Evidence assessment date: 2026-08-09
Review baseline: `3945e90559ec2e10771489078c9e8f52036209b7`
Current operational implementation milestone: M7
Contract authority: `candidate`; frozen exact-SHA contract bytes only
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
- the event chain proves independent contract review before exact-SHA owner approval, followed by
  remediation, validation, and independent exact-snapshot review;
- reviewer/remediator identity separation is mechanically checkable; and
- the exact-snapshot attestation returns `PASS` with no blocking, high, or medium findings.

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
4c596e806896a9693dd95766b7f5d3207c7f0969ee69e4aeeed05ab5e1e016ad docs/milestones/M9-I2-issuer-resolution-contract-lock.md
604b8535309e56bcd1115d465c48ac02d8de1f7e1a40662b838aec0c6b801d27 docs/milestones/M9-I2-contract-lock-review-approval-record.md
5604b685e4dab6d94be1059f89061143d48b4878a1e82a38ae936553dc818941 PROJECT_STATUS.md
9daeb38c2dff58af1681a3df8053ecf9239814d00cfd49d77417a60b46fdc931 ROADMAP.md
d45d0195ce45a0d982e9a595a0e4747590e2fcbeddbbbb58d2a24bc440078715 README.md
END SUBJECT MANIFEST
```

Subject snapshot ID: `0dee9d0aa63672b29e95ad9d4d51add36484197fae8662f18dbe0735f939536c`

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

## Historical validation and attestation assertions

The prior carrier recorded 325 passing tests and all 16 configured pre-commit hooks for the earlier
snapshot. The configuration consists of six upstream hooks plus all 10 local hooks, including
repository policy. That wording replaces the earlier imprecise statement that counted repository
policy separately from the 10 local hooks.

Those test results are useful historical execution evidence but cannot repair missing review or
approval provenance. Changes made during remediation also require fresh validation against the new
subject snapshot.

Fresh remediation validation for subject snapshot
`0dee9d0aa63672b29e95ad9d4d51add36484197fae8662f18dbe0735f939536c` completed in the local
workspace on Python 3.12.13 with pytest 8.4.2:

- all-candidate pre-commit: `PASS`; all 16 configured hooks passed without rewriting files;
- hook composition: six upstream hooks and 10 local hooks, including repository policy;
- full pytest suite: `PASS`; 331 tests passed;
- focused governance regressions: `PASS`; six tests passed; and
- `git diff --check`: `PASS`.

These results demonstrate reproducibility of the remediated bytes. They are not a substitute for a
durable validation event or for the missing independent review and project-owner approval events,
so the closure state remains `NOT_CLOSED`.

The prior exact-snapshot `PASS` is retained only as a historical assertion. It has no actor ID, UTC
timestamp, immutable evidence reference, or event-chain link and therefore grants no closure state.
It must not be silently upgraded by adding invented metadata after the fact.

## Required path to closure

1. Record a fresh independent contract review for the unchanged contract SHA-256 with durable event
   evidence and an identified reviewer separate from contract authoring/remediation.
2. After that `PASS`, record a fresh project-owner decision that names the review event and exact
   contract SHA-256.
3. Recompute the post-approval subject manifest and record remediation/validation events with exact
   hashes and immutable references.
4. Obtain a separate exact-snapshot review, durably record its verdict, and verify the full event
   hash chain.

Until every step is satisfied, the exact subject snapshot is `NOT_CLOSED`. This state does not
authorize publication, implementation, network/provider use, real-company data, attachments, or a
later milestone.

## Source boundary

No attached PDF, original extract, continuous source text, long quotation, private-source content,
real issuer data, or live provider response was read or used to produce this record.
