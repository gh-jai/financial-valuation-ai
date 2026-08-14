# M9-I2 Post-Owner-Approval Exact-Snapshot Closure

Status: `NOT_CLOSED`; M9-I5 contract-lock status-snapshot attestation/carrier candidate
Last closed snapshot status: `CLOSED_WITH_SINGLE_MAINTAINER_EXCEPTION` for exact M9-I4 snapshot
`8996b5c370576a09b556823ed61e5f025f8640aa2c9d061e29895e9384886f9d`
Current M9-I5 status snapshot: `NOT_CLOSED` for exact snapshot
`126ad4fc548b897546ebe9c09832b3e79283bab5fae860be3a264b6c30055980`
Historical snapshot status: `CLOSED_WITH_SINGLE_MAINTAINER_EXCEPTION`; both ordered immutable
exception events remain verified for snapshot `1c3754e7…a918`
Carrier update state: `m9_i5_status_attestation_local_candidate`
Evidence assessment date: 2026-08-15
Review baseline: `3945e90559ec2e10771489078c9e8f52036209b7`
Status synchronization baseline: `c4dcf9ef4780249f7a9a3a12a515cf4e07ce64b3`
Current operational implementation milestone: M7
Contract authority: `owner_approved_with_exception`; first-stage immutable attestation verified
Publication authority: `DENIED`; separate explicit authorization required
Runtime and data authority: bounded synthetic offline M9-I2 through M9-I4 only; live/provider
access, real-company data, attachment use, M9-I4 live readiness, M9-I5 through M9-I6, and release
authority remain `DENIED`

## Closure model

This record preserves the first two distinct exact documentation snapshots. The historical manifest records
the five immutable subject hashes closed by the published 2026-08-09 attestation. The current
manifest records the same five paths after the 2026-08-12 post-merge status synchronization. The
contract and review/approval bytes are unchanged; only `PROJECT_STATUS.md`, `ROADMAP.md`, and
`README.md` change. This carrier remains outside both manifests to avoid a self-referential hash.

No review, approval, event, or closure transfers between snapshot IDs. The historical attestation
continues to close only historical snapshot
`1c3754e724f98ff8324c567237070b68fe20514e678de3d1787e51d47f9da918`. The current snapshot is
separately closed as `CLOSED_WITH_SINGLE_MAINTAINER_EXCEPTION`: its immutable subject commit,
exact-subject remote CI, `COMMENTED_PASS` disposition with the only finding resolved, ordered
immutable `snapshot_closure_attestation`, and successful exact-attestation-commit CI are all
verified below. This carrier-only candidate performs the final transition without changing a
subject byte or immutable event.

The M9-I4 implementation post-merge synchronization later changed the same three status subjects
again and was squash-merged through PR #33 as immutable main subject commit
`82c26f8b4872d849837b774bcbed2d9229a4ce96`. The new manifest below starts a third lineage and does
not alter or inherit either prior closure verdict. Its attestation was separately reviewed,
published, and verified in immutable main commit
`35d36fd74f0850b55fd833699f39cd091509fa72`; exact-main Validate #100 succeeded. This
out-of-manifest carrier-only candidate verifies the immutable object and complete event chain and
records only that exact third-lineage snapshot as `CLOSED_WITH_SINGLE_MAINTAINER_EXCEPTION`.

The M9-I5 contract-lock post-merge synchronization changed the same three status subjects once
more and was merge-committed through PR #37 as immutable main subject commit
`fe2131721ea20c89ca3b452c0a7ef80dac37b236`. The fourth manifest below starts a new lineage and
does not alter or inherit any prior closure verdict. Its new attestation is only an unstaged local
candidate. Until that attestation is separately reviewed, published, verified by exact-main CI,
and referenced by a later carrier-only transition, this exact M9-I5 status snapshot remains
`NOT_CLOSED`.

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

## Historical closed subject manifest

The following block is historical evidence and must remain byte-for-byte stable. Its snapshot ID
is SHA-256 over the block bytes using the same newline rules as the current manifest.

```text
BEGIN HISTORICAL SUBJECT MANIFEST
9326b6c76dcfe3061c5e356b5141d9f458d57694cb4e6b01b6470b0bf044d84e docs/milestones/M9-I2-issuer-resolution-contract-lock.md
4734260f5946f57d08bb502919091025c49c7368d683d4334997e132d48ce969 docs/milestones/M9-I2-contract-lock-review-approval-record.md
c181c387c98bc77fbb6d9c7ff4face0c6bd7edb41e4c71d3c505f064e6030c45 PROJECT_STATUS.md
d1cc6d6f3a63fef58b50ef3b83131f36de56fa6af1b01023936b4200cb8538ab ROADMAP.md
6057359a14a20a8945a471d6fe527e7baab4481ee765d7d45bdae6b013c74f6d README.md
END HISTORICAL SUBJECT MANIFEST
```

Historical subject snapshot ID:
`1c3754e724f98ff8324c567237070b68fe20514e678de3d1787e51d47f9da918`

## Current reclosure subject manifest

The snapshot ID is SHA-256 over the bytes between `BEGIN SUBJECT MANIFEST` and
`END SUBJECT MANIFEST`, excluding both delimiter lines and including the final newline after the
last manifest row. Paths are repository-relative, ordered exactly as shown, and separated from
lowercase SHA-256 values by one ASCII space.

```text
BEGIN SUBJECT MANIFEST
9326b6c76dcfe3061c5e356b5141d9f458d57694cb4e6b01b6470b0bf044d84e docs/milestones/M9-I2-issuer-resolution-contract-lock.md
4734260f5946f57d08bb502919091025c49c7368d683d4334997e132d48ce969 docs/milestones/M9-I2-contract-lock-review-approval-record.md
ef05898cb6a8bdda0d52eeb7ac53e95862ca6065aa1253b28b3ed6ff2969c2db PROJECT_STATUS.md
c657a35c37b1b9e6424e39cf56d6b595c1e2c70bad2e3f37a79ce9d8cab3d2d8 ROADMAP.md
e5cc613c4a593c5cb99b61d168602f72179e61465ef9a348c1ab60eabdff2c13 README.md
END SUBJECT MANIFEST
```

Current subject snapshot ID: `eb726009ac6afeebd5b15618ff03796c73790175f6360a3823f7c411dafde705`

## M9-I4 implementation status-snapshot candidate manifest

This third manifest uses the same canonical hashing rule and preserves the two prior manifests
unchanged. Its five subject files are exact bytes from main commit
`82c26f8b4872d849837b774bcbed2d9229a4ce96`; this carrier and the new attestation candidate remain
outside the manifest.

```text
BEGIN M9-I4 STATUS SUBJECT MANIFEST
9326b6c76dcfe3061c5e356b5141d9f458d57694cb4e6b01b6470b0bf044d84e docs/milestones/M9-I2-issuer-resolution-contract-lock.md
4734260f5946f57d08bb502919091025c49c7368d683d4334997e132d48ce969 docs/milestones/M9-I2-contract-lock-review-approval-record.md
853e5ce1915befc3ce9bf7f4d9c35b544576be8d5168882d6329c779b8a7fd92 PROJECT_STATUS.md
f08296b18c87004e0b29f390255614dcb3fcc95a1f6a10e0575a197c6b86e82c ROADMAP.md
6aa4385cf7909ad5515e483d3bf1106c1cc344e4fcf023c0f43c44f286d12516 README.md
END M9-I4 STATUS SUBJECT MANIFEST
```

M9-I4 implementation status subject snapshot ID:
`8996b5c370576a09b556823ed61e5f025f8640aa2c9d061e29895e9384886f9d`

All five recorded hashes and the M9-I4 snapshot ID recompute exactly for its immutable historical
subject bytes. The append-only attestation is
`docs/milestones/M9-I4-status-snapshot-closure-attestation.md`; its exact bytes are immutable,
validated on the reviewed head and exact main commit, and verified by the published carrier
transition. The closure verdict applies only to snapshot
`8996b5c370576a09b556823ed61e5f025f8640aa2c9d061e29895e9384886f9d`. The three status hashes no
longer match the current repository because the later M9-I5 synchronization starts a new lineage;
that expected difference does not transfer or invalidate the historical M9-I4 verdict.

## M9-I5 contract-lock status-snapshot candidate manifest

This fourth manifest uses the same canonical hashing rule and preserves all three prior manifests
unchanged. Its five subject files are exact bytes from main commit
`fe2131721ea20c89ca3b452c0a7ef80dac37b236`; this carrier and the new attestation candidate remain
outside the manifest.

```text
BEGIN M9-I5 STATUS SUBJECT MANIFEST
9326b6c76dcfe3061c5e356b5141d9f458d57694cb4e6b01b6470b0bf044d84e docs/milestones/M9-I2-issuer-resolution-contract-lock.md
4734260f5946f57d08bb502919091025c49c7368d683d4334997e132d48ce969 docs/milestones/M9-I2-contract-lock-review-approval-record.md
874a16e7dcc5ea8364b60f840245cdfd52036679c106d1b5185add9ec0bd0460 PROJECT_STATUS.md
646c11664a2f6246165655eaf86cb130604c0725e0fd5e1cfaff1dbdb03453b2 ROADMAP.md
2222ce4054c090b5fafcb04ceb19b8d2f7978ed956c67da4aee3827c82476b62 README.md
END M9-I5 STATUS SUBJECT MANIFEST
```

M9-I5 contract-lock status subject snapshot ID:
`126ad4fc548b897546ebe9c09832b3e79283bab5fae860be3a264b6c30055980`

All five hashes and the snapshot ID recompute exactly. A match identifies only the new candidate
subject and does not close it. The append-only attestation candidate is
`docs/milestones/M9-I5-status-snapshot-closure-attestation.md`. Its local existence grants no
closure state. The M9-I4 verdict remains bound only to snapshot
`8996b5c370576a09b556823ed61e5f025f8640aa2c9d061e29895e9384886f9d`.

Recompute from the repository root:

```bash
sha256sum \
  docs/milestones/M9-I2-issuer-resolution-contract-lock.md \
  docs/milestones/M9-I2-contract-lock-review-approval-record.md \
  PROJECT_STATUS.md ROADMAP.md README.md
sed -n '/^BEGIN M9-I5 STATUS SUBJECT MANIFEST$/,/^END M9-I5 STATUS SUBJECT MANIFEST$/p' \
  docs/milestones/M9-I2-post-owner-approval-snapshot-closure.md \
  | sed '1d;$d' | sha256sum
```

The two contract-governance subjects intentionally retain their historical hashes. The three
M9-I5 status subjects must match the current repository bytes. A mismatch in either M9-I5 hashes
or its snapshot ID fails closed to `NOT_CLOSED`; matching hashes establish only the candidate
identity, not closure.

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
change invalidates that attestation for the changed bytes and returns the new package to
`NOT_CLOSED`. A later carrier-only update may reference the second immutable event because the
carrier is outside the subject manifest; it must not alter a subject file within the same
snapshot. An intentionally changed subject set starts a new snapshot lineage and must preserve the
prior manifest and attestation as historical evidence.

## Historical closure evidence assessment

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

The first-stage single-maintainer exception is now exercised by immutable
`contract_owner_attestation` commit `a406b5fc5cfded19f116cc42309da13cea42c713`. Its fixed blob is
`0011df140cfb44af244526b0feb3d71a8c40cdd6`, its file SHA-256 is
`daba23aa09e9c6e3e13ed983518ecf44d4698160e38693c72357ed19b14f1a75`, and canonical event hash
`1c0a77e77fd3ecc755d86c0d0db3c229d5194be63eb87af5bd4984520506df83` recomputes. The event binds
contract subject commit `743159d08ab05541a8d4fe25859bc9f9a49c5287`, successful `Validate` run
[#66](https://github.com/gh-jai/financial-valuation-ai/actions/runs/31313816548), complete validation,
zero unresolved blocking/high/medium findings, explicit shared-actor disclosure, a narrow separation
waiver, and residual-risk acceptance. `Validate` run
[#67](https://github.com/gh-jai/financial-valuation-ai/actions/runs/31314762621) also verified the
immutable attestation commit on Python 3.10 and 3.12 with 337 tests per job.

That event advances only the contract to `owner_approved_with_exception`. The subsequent
approval-record and status-summary update created exact subject snapshot
`1c3754e724f98ff8324c567237070b68fe20514e678de3d1787e51d47f9da918`, preserved in subject commit
`01b5d95bc990242321cfea3e6b7ddcde7b8a1f4f`. `Validate` run
[#68](https://github.com/gh-jai/financial-valuation-ai/actions/runs/31315947577) completed
successfully for that exact head, with Python 3.10 and 3.12 each passing 339 tests.

The ordered second-stage `snapshot_closure_attestation` is now immutable in commit
`1f1f0fd65e067015a17b016536f04ca9435493c3`. Its fixed blob is
`955fae32f148385b4eb09f72d3775d8898fbf8ef`, its file SHA-256 is
`16984ab5492114d111b1ba2c9c56e6a1c433a7fc6db3ace79d6dc2344bf7c12c`, and canonical event hash
`288270085de0794ed954ef10ab41746a85fe357e6c02d5ff1a43adb949aabcea` recomputes. The immutable
reference is
`https://github.com/gh-jai/financial-valuation-ai/blob/1f1f0fd65e067015a17b016536f04ca9435493c3/docs/milestones/M9-I2-snapshot-closure-attestation.md`.
Its event links to first-stage event hash
`1c0a77e77fd3ecc755d86c0d0db3c229d5194be63eb87af5bd4984520506df83`, binds the unchanged subject
snapshot and commit, records the successful exact-subject `Validate` run #68, discloses the shared
owner/author/remediator identity, accepts the bounded residual risk, and reports no unresolved
blocking, high, or medium finding.

`Validate` run [#69](https://github.com/gh-jai/financial-valuation-ai/actions/runs/31316921540)
independently verified the immutable attestation commit. Job
[`93253567690`](https://github.com/gh-jai/financial-valuation-ai/actions/runs/31316921540/job/93253567690)
on Python 3.12 and job
[`93253567722`](https://github.com/gh-jai/financial-valuation-ai/actions/runs/31316921540/job/93253567722)
on Python 3.10 completed successfully; each passed all validation and repository-policy steps and
341 tests. The complete ordered exception path is therefore mechanically verifiable, and this
out-of-manifest carrier records the exact subject snapshot as
`CLOSED_WITH_SINGLE_MAINTAINER_EXCEPTION`.

The historical manifest above preserves those five exact subject hashes and the attested snapshot
ID. The current repository no longer pretends that its three high-level status files still have
those bytes. This explicit separation preserves the old immutable evidence without transferring
its verdict to the new snapshot.

## Current reclosure evidence assessment

PR #24 merged the bounded synthetic offline M9-I2 issuer-resolution implementation as
`3ea93c8751bfaa558d3597a91b978f986dac6412`. PR #25 merged its out-of-manifest completion carrier as
`58a6031427ace8ce61b48884753ca732943ea2ca`. PR #26 merged the bounded offline M9-I3 immutable store
and safe manual-import implementation as `c4dcf9ef4780249f7a9a3a12a515cf4e07ce64b3`; exact-head
Validate run #81 succeeded on Python 3.10 and 3.12 with 425 tests per job.

Those facts require `README.md`, `ROADMAP.md`, and `PROJECT_STATUS.md` to move beyond their attested
2026-08-09 status. Their changed bytes produce the current manifest and snapshot ID above. The
contract and approval-record hashes remain unchanged, and the historical attestation files and
events are not modified.

The current manifest is preserved in immutable subject commit
`f571c1426181107d50f84e59fed051fb11c9c94e`. Validate run
[#83](https://github.com/gh-jai/financial-valuation-ai/actions/runs/31518237790) succeeded for that
exact head on Python 3.10 and 3.12; each job passed all 10 workflow validators/repository-policy
steps and 426 tests. Formal exact-head review recorded `COMMENTED_BLOCKING` against that commit and
identified one current-evidence inconsistency in this out-of-manifest carrier. This carrier-only
follow-up corrects the inconsistency without changing any subject byte or the current snapshot ID.

PR #27's carrier remediation was subsequently published in main subject commit
`3b2a7adec3fb2c9c8d4d9ce2eb9aa61e75f5379c`. Its Git tree is byte-identical to the reviewed
`ff0767f145867f08a4386d1d8e5d7342663fed7c` head. Validate run #85 (`31519855793`) succeeded for
that exact main commit, the formal disposition is `COMMENTED_PASS`, and the only authoritative
finding thread `PRRT_kwDOTqKoFc6YUcz-` is resolved. No unresolved blocking, high, or medium finding
remains against the current subject bytes.

The ordered current `snapshot_closure_attestation` is now immutable in main commit
`1a3a33646e963525c952f7af735d8806369f6a70`. Its fixed Git blob is
`15b4654d22450665a1e5fd16c465e55a19837b27`, its file SHA-256 is
`36d24d8ed7a58adaf62e5d25426bbc891f9129e365f6224cc9dfa51ac2b248c3`, and canonical event hash
`d203f487fd9a6c1623f71d5ed0a68828c586956ebdb739c1cf5aa6e6569117c1` recomputes. The immutable
reference is
`https://github.com/gh-jai/financial-valuation-ai/blob/1a3a33646e963525c952f7af735d8806369f6a70/docs/milestones/M9-I2-current-snapshot-closure-attestation.md`.
The event links to prior event hash
`288270085de0794ed954ef10ab41746a85fe357e6c02d5ff1a43adb949aabcea`, binds current snapshot
`eb726009ac6afeebd5b15618ff03796c73790175f6360a3823f7c411dafde705` and main subject commit
`3b2a7adec3fb2c9c8d4d9ce2eb9aa61e75f5379c`, preserves the shared-actor disclosure and bounded
separation waiver, accepts the residual risk, and grants no additional runtime, data, provider,
publication, release, or qualified-review authority.

Main Validate run [#87](https://github.com/gh-jai/financial-valuation-ai/actions/runs/31524034663)
verified the exact immutable-attestation commit. Job
[`93887825384`](https://github.com/gh-jai/financial-valuation-ai/actions/runs/31524034663/job/93887825384)
on Python 3.10.20 and job
[`93887825359`](https://github.com/gh-jai/financial-valuation-ai/actions/runs/31524034663/job/93887825359)
on Python 3.12.13 completed successfully; each passed all 10 validation and repository-policy
steps and 429 tests. The complete current exception path is therefore mechanically verifiable,
and this out-of-manifest carrier-only candidate records the current snapshot as
`CLOSED_WITH_SINGLE_MAINTAINER_EXCEPTION`.

The `NOT_CLOSED` wording inside the five-file subject snapshot is retained as immutable subject
history; modifying those bytes would create a different snapshot and invalidate this attestation.
The out-of-manifest carrier is the authoritative closure record for the exact attested snapshot.
No hash match, prior attestation, merged implementation, review remediation, or status prose alone
may advance a snapshot; closure here depends on the complete ordered evidence chain above.

## M9-I4 implementation status-snapshot closure evidence

PR #34 published the append-only M9-I4 status `snapshot_closure_attestation` as reviewed head
`561b5631b98942be47a1c177f23b4a187d6fae69`. Validate #99
([`31703633945`](https://github.com/gh-jai/financial-valuation-ai/actions/runs/31703633945))
succeeded at that exact head on Python 3.10 and 3.12 with 509 tests per job. Formal same-maintainer
review `4927430704` recorded `COMMENTED_PASS` with no findings against that exact head and did not
claim independent approval. The reviewed tree
`b8ed657d9f573ec332fac703cdd31a43980a0383` is byte-identical to the squash-merged main tree.

The ordered M9-I4 status `snapshot_closure_attestation` is now immutable in main commit
`35d36fd74f0850b55fd833699f39cd091509fa72`. Its fixed Git blob is
`fab592fa6ac54f8f02f16985c0702f444442eca7`, its file SHA-256 is
`60e97e1eb35fdd303a5b6e705e5fe9c3b0ac67771a4a7bff626b77b3efdb0918`, and canonical event hash
`a2ab8b45dcd40605eba3a680322be3da5318fccac97424356ca94364bfca17d1` recomputes. The immutable
reference is
`https://github.com/gh-jai/financial-valuation-ai/blob/35d36fd74f0850b55fd833699f39cd091509fa72/docs/milestones/M9-I4-status-snapshot-closure-attestation.md`.
The event links to predecessor event hash
`d203f487fd9a6c1623f71d5ed0a68828c586956ebdb739c1cf5aa6e6569117c1`, binds snapshot
`8996b5c370576a09b556823ed61e5f025f8640aa2c9d061e29895e9384886f9d` and subject commit
`82c26f8b4872d849837b774bcbed2d9229a4ce96`, preserves the shared-actor disclosure and narrow
separation waiver, accepts the residual risk, and grants no runtime, provider, data, publication,
release, or qualified-review authority.

Main Validate #100
([`31704722307`](https://github.com/gh-jai/financial-valuation-ai/actions/runs/31704722307))
verified the exact immutable-attestation commit. Job
[`94462271822`](https://github.com/gh-jai/financial-valuation-ai/actions/runs/31704722307/job/94462271822)
on Python 3.10 and job
[`94462271743`](https://github.com/gh-jai/financial-valuation-ai/actions/runs/31704722307/job/94462271743)
on Python 3.12 completed successfully; each passed every validation, repository-policy, and test
step with 509 tests. The complete selected exception path is therefore mechanically verifiable,
and this out-of-manifest carrier-only candidate records the exact M9-I4 implementation status
snapshot as `CLOSED_WITH_SINGLE_MAINTAINER_EXCEPTION`.

The `NOT_CLOSED` wording inside the five-file subject snapshot and immutable attestation remains
historical subject/event context. Modifying those bytes would create a different snapshot or event
and invalidate this verdict. This out-of-manifest carrier is the authoritative closure record only
after its own separately authorized publication; until then these local carrier bytes are a
validated closure-transition candidate.

## M9-I5 contract-lock status-snapshot attestation candidate evidence

PR #37 synchronized the M9-I5 contract-lock post-merge status through reviewed exact head
`f44905584c88a1476a05c07e3e01adb46457b6f0`. Validate #105
([`31803048721`](https://github.com/gh-jai/financial-valuation-ai/actions/runs/31803048721))
succeeded at that exact head. Python 3.10 job `94775314595` and Python 3.12 job `94775314423`
each passed every validation, repository-policy, and test step with 526 tests. Formal
same-maintainer review `4937392887`, node `PRR_kwDOTqKoFc8AAAABJkqi9w`, recorded
`COMMENTED_PASS` with no findings and did not claim independent approval.

PR #37 was merge-committed as exact main subject commit
`fe2131721ea20c89ca3b452c0a7ef80dac37b236`, whose parent list is exactly
`98536ff27a80bd8ddb4dd9e651ca7217c1c0d582` followed by
`f44905584c88a1476a05c07e3e01adb46457b6f0`. The reviewed and merged subject tree is
byte-identical at `914cdbc87b8e5eea07a1bffe21a492d51a018d3f`. Post-merge Validate #106
([`31830905746`](https://github.com/gh-jai/financial-valuation-ai/actions/runs/31830905746))
succeeded at that exact main commit. Python 3.10 job `94866073988` and Python 3.12 job
`94866074048` each passed every validation, repository-policy, and test step with 526 tests.

The append-only M9-I5 status `snapshot_closure_attestation` exists only as an unstaged local
candidate at `docs/milestones/M9-I5-status-snapshot-closure-attestation.md`. Its canonical event
links to predecessor event hash `a2ab8b45dcd40605eba3a680322be3da5318fccac97424356ca94364bfca17d1`,
binds exact snapshot `126ad4fc548b897546ebe9c09832b3e79283bab5fae860be3a264b6c30055980`
and subject commit `fe2131721ea20c89ca3b452c0a7ef80dac37b236`, discloses the shared
owner/author/remediator identity, accepts the bounded residual risk, and grants no runtime,
provider, data, publication, release, or qualified-review authority.

Because this attestation is not yet an immutable Git object and has no exact-attestation-main CI,
the event cannot yet advance the new snapshot. The current M9-I5 status snapshot remains
`NOT_CLOSED`. A separately authorized publication and a later separately authorized carrier-only
verification are both still required. Neither the closed M9-I4 snapshot nor any earlier closure
verdict transfers to these changed summary bytes.

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

This is historical reproducibility evidence for the pre-approval snapshot. Exact-subject-commit
remote CI and the first immutable owner attestation later advanced only the contract to
`owner_approved_with_exception`; they did not close the package.

Current local validation for the post-owner-approval subject snapshot
`1c3754e724f98ff8324c567237070b68fe20514e678de3d1787e51d47f9da918` completed in the local
workspace on Python 3.12.13 with pytest 8.4.2 and jsonschema 4.26.0:

- focused M9-I2 governance regressions: `PASS`; 14 tests passed;
- all-candidate pre-commit: `PASS`; all 16 configured hooks passed without rewriting files;
- hook composition: six upstream hooks and 10 local hooks, including repository policy;
- full pytest suite: `PASS`; 339 tests passed; and
- `git diff --check`: `PASS`.

This was local validation of the recomputable subject candidate bytes. Exact-subject-commit remote
CI and the immutable `snapshot_closure_attestation` were subsequently published and verified as
recorded in the current evidence assessment above.

Immutable second-stage publication verification for attestation commit
`1f1f0fd65e067015a17b016536f04ca9435493c3` completed in `Validate` run #69:

- Python 3.10.20: `PASS`; 341 tests passed;
- Python 3.12.13: `PASS`; 341 tests passed;
- pytest 8.4.2 and jsonschema 4.26.0;
- all validation and repository-policy steps: `PASS`; and
- the workflow's pull-request head is the exact attestation commit.

Historical local validation for the final 2026-08-09 carrier-only transition completed in the local workspace on
Python 3.12.13 with pytest 8.4.2 and jsonschema 4.26.0:

- focused M9-I2 governance regressions: `PASS`; 18 tests passed;
- all-candidate pre-commit: `PASS`; all 16 configured hooks passed without rewriting files;
- hook composition: six upstream hooks and 10 local hooks, including repository policy;
- full pytest suite: `PASS`; 343 tests passed; and
- `git diff --check`: `PASS`.

These results validate the final local candidate bytes. The carrier transition becomes the
published authoritative repository state only after separately authorized staging, commit, push,
and exact-head remote verification.

Current local validation for the 2026-08-12 post-merge status-snapshot reclosure candidate completed
on Python 3.12.13 with pytest 8.4.2, jsonschema 4.26.0, and PyYAML 6.0.3:

- focused M9-I2 governance regressions: `PASS`; 19 tests passed;
- current subject manifest: `PASS`; all five current repository hashes and the current snapshot ID
  recomputed exactly;
- historical subject manifest: `PASS`; all five recorded hashes and historical snapshot ID
  remained byte-for-byte stable;
- complete repository suite: `PASS`; 426 tests passed;
- all 10 workflow validators and repository-policy steps: `PASS`;
- schema/governed-document validation: `PASS`; 32 schemas and 121 governed documents;
- repository content policy: `PASS`; no prohibited source detected;
- `git diff --check`: `PASS`; and
- staged index: empty; no commit, push, PR, attestation publication, or closure transition claimed.

These results first validated the unstaged local candidate. Commit
`f571c1426181107d50f84e59fed051fb11c9c94e` subsequently published the exact current subject bytes,
and exact-head Validate run #83 (`31518237790`) supplied successful remote CI. The carrier-only
finding was remediated, exact-head run #84 passed, and formal re-review returned `COMMENTED_PASS`.
Main subject run #85 then verified the reviewed subject tree. The immutable current attestation was
published in commit `1a3a33646e963525c952f7af735d8806369f6a70`, and main run #87
(`31524034663`) verified that exact commit on Python 3.10.20 and 3.12.13 with 429 tests per job.

Current local validation for this carrier-only reclosure candidate completed on Python 3.12.13
with pytest 8.4.2, jsonschema 4.26.0, and PyYAML 6.0.3:

- focused M9-I2 governance regressions: `PASS`; 23 tests passed;
- complete repository suite: `PASS`; 430 tests passed;
- all 10 workflow validators and repository-policy steps: `PASS`;
- schema/governed-document validation: `PASS`; 32 schemas and 121 governed documents;
- immutable current-attestation SHA-256 and canonical event hash: `PASS`;
- current and historical subject manifests and the complete three-event chain: `PASS`;
- `git diff --check`: `PASS`; and
- staged index: empty; no staging, commit, push, PR, or publication is claimed.

These results validate only the unstaged local carrier candidate. The transition becomes the
published repository state only after separately authorized publication and exact-head remote
verification; those future actions do not alter the already immutable attestation event.

The prior exact-snapshot `PASS` is retained only as a historical assertion. It has no actor ID, UTC
timestamp, immutable evidence reference, or event-chain link and therefore grants no closure state.
It must not be silently upgraded by adding invented metadata after the fact.

## Historical path to closure

The preferred default path remains:

1. record a fresh independent contract review for the exact contract SHA-256;
2. record a later project-owner decision naming that review;
3. recompute and validate the exact post-approval snapshot; and
4. obtain a separate exact-snapshot `PASS` and verify the complete event chain.

When no eligible independent reviewer is reasonably available, the alternative path is:

1. [complete] commit and publish the exact contract/documentation candidate without declaring it
   approved;
2. [complete] obtain successful remote CI and complete validation for that immutable subject
   commit, then publish an immutable `contract_owner_attestation` satisfying every exception field
   and advance only the contract state to `owner_approved_with_exception` in the approval record;
3. [complete] publish that approval-record update, recompute the subject manifest, obtain successful
   remote CI for the new immutable subject commit, and confirm no unresolved
   blocking/high/medium finding;
4. [complete] publish a separate immutable `snapshot_closure_attestation` bound to that exact subject commit
   and snapshot ID; and
5. [complete in this local candidate] update only this out-of-manifest carrier to reference the second event and record
   `CLOSED_WITH_SINGLE_MAINTAINER_EXCEPTION`, without altering a subject file.

Every selected-path evidence step remains satisfied for historical snapshot `1c3754e7…a918`, so
that exact historical package remains `CLOSED_WITH_SINGLE_MAINTAINER_EXCEPTION`. It does not close
the current snapshot or authorize publication, implementation, network/provider use, real-company
data, attachments, or a later milestone.

## Required path for current reclosure

1. [complete] synchronize only the three high-level status subjects,
   preserve both contract-governance subjects, record the new manifest/snapshot ID, and add
   recomputation and history-preservation regressions;
2. [complete] publish exact subject commit `f571c1426181107d50f84e59fed051fb11c9c94e` and retain the
   current manifest and snapshot ID without declaring closure;
3. [complete] obtain successful exact-subject Python 3.10/3.12 CI in Validate run #83
   (`31518237790`);
4. [complete] correct the carrier-only current-evidence finding,
   obtain successful exact-head CI for the correction, and complete formal re-review with no
   unresolved blocking, high, or medium finding;
5. [complete] publish a new immutable `snapshot_closure_attestation` bound to
   the current snapshot ID, subject commit, CI, validation, finding disposition, shared-actor
   disclosure, residual-risk acceptance, prior event chain, and authority boundary; and
6. [complete in this local candidate] update only this out-of-manifest carrier to verify the new Git
   object and transition the current snapshot to `CLOSED_WITH_SINGLE_MAINTAINER_EXCEPTION`.

All six selected-path steps are satisfied for the exact current snapshot. Any later mismatch in a
subject hash, event-chain link, immutable object, CI, finding disposition, or authority boundary
fails closed to `NOT_CLOSED`; any subject-file change starts a new snapshot lineage.

## Required path for M9-I4 implementation status-snapshot closure

1. [complete] preserve the three synchronized status subjects and two unchanged contract-governance
   subjects in immutable main commit `82c26f8b4872d849837b774bcbed2d9229a4ce96`;
2. [complete] recompute all five subject hashes and candidate snapshot
   `8996b5c370576a09b556823ed61e5f025f8640aa2c9d061e29895e9384886f9d` while preserving both prior
   manifests and attestations;
3. [complete] obtain successful exact-main-subject Python 3.10/3.12 CI in Validate #98
   (`31702191834`) and retain same-maintainer exact-head `COMMENTED_PASS` review `4927207917` with
   no findings;
4. [complete] create a new append-only `snapshot_closure_attestation`
   bound to the new snapshot ID, main subject commit, CI, review, finding disposition, shared-actor
   disclosure, residual-risk acceptance, prior event hash, and narrow authority boundary;
5. [complete] publish the exact attestation candidate as immutable main commit
   `35d36fd74f0850b55fd833699f39cd091509fa72` and obtain successful exact-attestation-main Validate
   #100 (`31704722307`); and
6. [complete in this local candidate] update only this out-of-manifest carrier to verify the immutable
   attestation object, file SHA-256, event hash, chain link, and CI before transitioning only the
   exact new snapshot to `CLOSED_WITH_SINGLE_MAINTAINER_EXCEPTION`.

All six selected-path steps are satisfied for the exact M9-I4 implementation status snapshot. This
carrier-only candidate records `CLOSED_WITH_SINGLE_MAINTAINER_EXCEPTION` without altering any
subject or attestation byte. Its later publication remains separately gated. Neither this closure
verdict nor the prior closure states authorize provider/network activation, live SEC access,
real-company data, M9-I5 implementation, or release activity.

## Required path for M9-I5 contract-lock status-snapshot closure

1. [complete] preserve the three synchronized status subjects and two unchanged contract-governance
   subjects in immutable main commit `fe2131721ea20c89ca3b452c0a7ef80dac37b236`;
2. [complete] recompute all five subject hashes and candidate snapshot
   `126ad4fc548b897546ebe9c09832b3e79283bab5fae860be3a264b6c30055980` while preserving all prior
   manifests and attestations;
3. [complete] obtain successful exact-reviewed-head Validate #105 (`31803048721`), exact-main
   Validate #106 (`31830905746`), and same-maintainer exact-head `COMMENTED_PASS` review
   `4937392887` with no findings;
4. [complete in this local candidate] create a new append-only `snapshot_closure_attestation`
   bound to the new snapshot ID, main subject commit, CI, review, finding disposition, shared-actor
   disclosure, residual-risk acceptance, prior event hash, and narrow authority boundary;
5. [pending separate authorization] publish the exact attestation candidate as an immutable main
   commit and obtain successful exact-attestation-main Validate; and
6. [pending separate authorization] update only this out-of-manifest carrier to verify the immutable
   attestation object, file SHA-256, event hash, chain link, and CI before transitioning only the
   exact M9-I5 status snapshot to `CLOSED_WITH_SINGLE_MAINTAINER_EXCEPTION`.

The first four selected-path steps identify and validate only a local attestation candidate. They
do not close the snapshot. Any later mismatch in a subject hash, event-chain link, immutable
object, CI, finding disposition, or authority boundary fails closed to `NOT_CLOSED`; any
subject-file change starts another snapshot lineage.

Local validation for this 2026-08-13 closure-attestation candidate completed on Python 3.12.13
with pytest 8.4.2, jsonschema 4.26.0, and PyYAML 6.0.3:

- focused M9-I2/M9-I4 governance regressions: `PASS`; 27 tests passed;
- all nine artifact validators plus repository policy: `PASS`;
- repository policy: `PASS`; 409 candidate files and no prohibited sources;
- full pytest suite: `PASS`; 509 tests passed;
- new subject manifest, snapshot ID, attestation event hash, and prior-event link recomputation:
  `PASS`; and
- `git diff --check`: `PASS`.

These local results validate only the unstaged candidate bytes. They do not substitute for the
pending immutable attestation commit, its exact-head remote CI, or the later carrier-only
verification and closure transition.

Local validation for this 2026-08-14 carrier-only closure-transition candidate completed on
Python 3.12.13 with pytest 8.4.2, jsonschema 4.26.0, and PyYAML 6.0.3:

- focused M9-I2/M9-I4 governance regressions: `PASS`; 29 tests passed;
- all nine artifact validators plus repository policy: `PASS`;
- repository policy: `PASS`; 409 candidate files and no prohibited sources;
- full pytest suite: `PASS`; 511 tests passed;
- immutable attestation blob, file SHA-256, canonical event hash, previous-event link, reviewed/main
  tree identity, and Validate #100 matrix evidence: `PASS`; and
- `git diff --check`: `PASS`.

These results validate only the unstaged carrier-transition candidate bytes. They do not authorize
staging, committing, pushing, PR creation, merge, or any capability outside the narrow closure
record. The carrier becomes the authoritative published transition only after those later actions
are separately authorized and exact-head evidence is verified.

Local validation for this 2026-08-15 M9-I5 status-snapshot attestation/carrier candidate completed
on Python 3.12.13 with pytest 8.4.2, jsonschema 4.26.0, and PyYAML 6.0.3:

- focused M9-I2/M9-I4/M9-I5 governance regressions: `PASS`; 33 tests passed;
- all nine artifact validators plus repository policy: `PASS`;
- schema/governed-document validation: `PASS`; 41 schemas and 121 governed documents;
- repository policy: `PASS`; 418 candidate files and no prohibited sources;
- full pytest suite: `PASS`; 530 tests passed;
- all-candidate pre-commit: `PASS`; all 16 configured hooks passed without rewriting files;
- new subject manifest, snapshot ID, attestation event hash, prior-event link, exact head/main tree
  identity, Validate #105/#106 evidence, and M9-I5 contract SHA-256: `PASS`; and
- `git diff --check`: `PASS`.

These results validate only the unstaged local attestation/carrier candidate bytes. They do not
authorize staging, committing, pushing, PR creation, publication, closure transition, runtime,
provider/network activation, real-company data, M9-I5 runtime, M9-I6, or release activity.

## Source boundary

No attached PDF, original extract, continuous source text, long quotation, private-source content,
real issuer data, or live provider response was read or used to produce this record.
