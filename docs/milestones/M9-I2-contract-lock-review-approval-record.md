# M9-I2 Contract Lock — Review and Approval Record

Status: `candidate`; historical review/approval assertions are not independently auditable
Post-owner-approval package closure: `NOT_CLOSED`
Contract path: `docs/milestones/M9-I2-issuer-resolution-contract-lock.md`
Contract SHA-256: `4c596e806896a9693dd95766b7f5d3207c7f0969ee69e4aeeed05ab5e1e016ad`
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
| `4c596e806896a9693dd95766b7f5d3207c7f0969ee69e4aeeed05ab5e1e016ad` | A contract review `PASS` and exact-SHA owner approval were recorded on 2026-08-09. | `candidate`; actor identifiers, UTC event timestamps, immutable evidence references, and a verifiable event chain were not preserved. | Frozen contract candidate only. Publication and implementation remain separately unauthorized. |

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

For an independent review, the reviewer `actor_id` must differ from every authoring or remediation
actor for the reviewed bytes. Owner approval must reference a qualifying earlier independent
`PASS` event for the same exact contract SHA-256. Dates without times, role labels without actor
identifiers, and prose in the same commit as the claimed decision are not sufficient evidence.

## Historical pre-owner-review assertion

- Asserted reviewed contract SHA-256:
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

A fresh project-owner decision may occur only after a fresh, durably evidenced independent `PASS`
for the same exact SHA. Such approval would cover the frozen contract boundary only and would not
authorize publication or implementation.

## Post-owner-approval exact-snapshot closure

The authoritative closure assessment is
`docs/milestones/M9-I2-post-owner-approval-snapshot-closure.md`. Package closure remains
`NOT_CLOSED` unless all subject hashes and the snapshot ID recompute and the durable event chain
proves, in order:

1. independent contract review;
2. exact-SHA project-owner approval referencing that review;
3. post-approval remediation and validation; and
4. an independent exact-snapshot `PASS` by an actor separate from remediation.

Any change to a subject file invalidates an earlier snapshot closure. Neither a closed snapshot nor
contract approval would authorize publication or implementation.

## Current verification state

- [x] Contract SHA-256 recomputes to the frozen candidate value.
- [x] No M9-I2 runtime, live provider access, real-company material, or attachment content is added.
- [ ] A durable independent-review event exists for the exact contract SHA-256.
- [ ] A later durable project-owner approval event references that exact review event.
- [ ] The post-owner-approval package has a complete, independently verifiable event chain.
- [ ] Package closure is established.

## Source boundary

No attached PDF, original extract, continuous source text, long quotation, private-source content,
real issuer data, or live provider response was read or used to produce this record.
