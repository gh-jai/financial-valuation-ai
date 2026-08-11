# M9-I2 Current Snapshot Closure Attestation

Artifact state: `local_candidate_not_yet_immutable`
Governance path: `single-maintainer exception`
Contract state: `owner_approved_with_exception`
Current snapshot state before immutable publication: `NOT_CLOSED`

## Decision boundary

This is the next append-only `snapshot_closure_attestation` candidate for current documentation
snapshot `eb726009ac6afeebd5b15618ff03796c73790175f6360a3823f7c411dafde705`. The owner chooses
`CLOSED_WITH_SINGLE_MAINTAINER_EXCEPTION` for that exact snapshot while explicitly disclosing that
the owner is also the author/remediator and that no independent review occurred.

This local file is not yet an immutable public attestation. Its existence does not close the
current snapshot. Closure remains `NOT_CLOSED` until a separately authorized commit and publication
preserve these exact bytes in an immutable Git object, exact-head CI verifies that object, and the
out-of-manifest closure carrier is later updated to verify the object identity, file SHA-256, event
hash, and event-chain link. That later carrier-only transition requires separate authorization.

## Canonical event

`event_hash` is lowercase SHA-256 over UTF-8 canonical JSON of the complete `event` mapping below,
using lexicographically sorted object keys, no insignificant whitespace, JSON booleans/null, and
no ASCII escaping. The hash excludes the top-level `event_hash` field itself.

```yaml
event:
  schema_version: m9_i2_exception_attestation/v1
  event_id: m9-i2-current-snapshot-closure-attestation-20260811T180235Z
  exception_id: m9-i2-single-maintainer-9326b6c7-eb726009
  decision_kind: snapshot_closure_attestation
  occurred_at: "2026-08-11T18:02:35Z"
  actor_id: "github:gh-jai"
  actor_role: project_owner
  actor_type: human
  repository: gh-jai/financial-valuation-ai
  baseline_sha: c4dcf9ef4780249f7a9a3a12a515cf4e07ce64b3
  subject_kind: exact_snapshot
  subject_id: eb726009ac6afeebd5b15618ff03796c73790175f6360a3823f7c411dafde705
  subject_commit_sha: 3b2a7adec3fb2c9c8d4d9ce2eb9aa61e75f5379c
  contract_path: docs/milestones/M9-I2-issuer-resolution-contract-lock.md
  contract_sha256: 9326b6c76dcfe3061c5e356b5141d9f458d57694cb4e6b01b6470b0bf044d84e
  snapshot_id: eb726009ac6afeebd5b15618ff03796c73790175f6360a3823f7c411dafde705
  decision: CLOSED_WITH_SINGLE_MAINTAINER_EXCEPTION
  eligibility_reason: >-
    The canonical repository is operated through the single project-owner identity github:gh-jai.
    That identity authored or remediated the subject bytes, GitHub cannot accept its self-approval
    as an independent review, and no second eligible reviewer was reasonably available after the
    separation-of-duties requirement was evaluated.
  shared_actor_disclosure: >-
    github:gh-jai is simultaneously the project owner and the author/remediator of the exact
    subject commit; reviewer/author separation did not occur, the formal COMMENTED_PASS is a
    disclosed same-actor review disposition, and this event is not independent review.
  separation_waiver_scope: >-
    M9-I2 contract and documentation governance only. The waiver does not apply to M1-M7 runtime
    composition, human-only approvals, M9-I2/M9-I3 runtime controls, M9-I4 through M9-I6, or any
    qualified-review gate.
  ci_evidence:
    workflow_name: Validate
    workflow_run_id: 31519855793
    workflow_run_number: 85
    workflow_url: https://github.com/gh-jai/financial-valuation-ai/actions/runs/31519855793
    trigger: push
    head_sha: 3b2a7adec3fb2c9c8d4d9ce2eb9aa61e75f5379c
    status: completed
    conclusion: success
    governance_regressions: 19 passed
    matrix_jobs:
      - python_version: "3.10"
        python_runtime: 3.10.20
        job_id: 93873946343
        job_url: https://github.com/gh-jai/financial-valuation-ai/actions/runs/31519855793/job/93873946343
        conclusion: success
        full_suite: 426 passed
      - python_version: "3.12"
        python_runtime: 3.12.13
        job_id: 93873946509
        job_url: https://github.com/gh-jai/financial-valuation-ai/actions/runs/31519855793/job/93873946509
        conclusion: success
        full_suite: 426 passed
  local_validation_evidence:
    environment:
      python: 3.12.13
      pytest: 8.4.2
      jsonschema: 4.26.0
      pyyaml: 6.0.3
    commands:
      - command: python -m pytest tests/unit/test_m9_i2_governance.py -q
        result: 19 passed
      - command: run the 10 Validate workflow validators and repository-policy steps
        result: 10 of 10 passed; 32 schemas and 121 governed documents validated
      - command: python -m pytest -q
        result: 426 passed
      - command: git diff --check
        result: passed
    evidence_scope: exact main subject commit before this attestation candidate was added
  review_evidence:
    pull_request_number: 27
    pull_request_url: https://github.com/gh-jai/financial-valuation-ai/pull/27
    base_sha: c4dcf9ef4780249f7a9a3a12a515cf4e07ce64b3
    reviewed_head_sha: ff0767f145867f08a4386d1d8e5d7342663fed7c
    reviewed_tree_sha: 444938a913197824d2556193a4b3b1c812694210
    main_subject_tree_sha: 444938a913197824d2556193a4b3b1c812694210
    review_id: 4909174183
    review_node_id: PRR_kwDOTqKoFc8AAAABJJwNpw
    review_url: https://github.com/gh-jai/financial-valuation-ai/pull/27#pullrequestreview-4909174183
    submitted_at: "2026-08-11T17:48:00Z"
    disposition: COMMENTED_PASS
    remediation_ci_run_id: 31519188629
    finding_thread_id: PRRT_kwDOTqKoFc6YUcz-
    finding_comment_id: PRRC_kwDOTqKoFc7gIYkI
    finding_resolution: resolved
    resolved_by: "github:gh-jai"
  finding_disposition: >-
    PR #27 formal exact-head re-review recorded COMMENTED_PASS against
    ff0767f145867f08a4386d1d8e5d7342663fed7c after successful remediation CI run #84. Its tree is
    byte-identical to main subject commit 3b2a7adec3fb2c9c8d4d9ce2eb9aa61e75f5379c. The PR's only
    blocking thread, PRRT_kwDOTqKoFc6YUcz-, is resolved, and no unresolved blocking, high, or medium
    code or governance finding remains against the exact subject bytes.
  residual_risk_acceptance: >-
    The owner accepts the loss of independent challenge and the increased risk of undetected bias
    or governance error. Proceeding is proportionate only because the exception is transparent,
    exact-snapshot, immutable-main-commit, CI, review, finding-disposition, and event-chain bound;
    limited to documentation governance; grants no runtime, publication, data, provider, or release
    authority; and remains fail-closed until later carrier verification.
  authority_boundary: >-
    This decision concerns only exact documentation snapshot
    eb726009ac6afeebd5b15618ff03796c73790175f6360a3823f7c411dafde705 under the
    single-maintainer exception after immutable publication and later carrier verification. This
    local candidate does not close the snapshot. It does not authorize staging, committing,
    pushing, PR creation or state changes, publication, runtime changes, live or provider access,
    real-company data, attachment use, M9-I4 through M9-I6, release, or any legal, privacy,
    security, accessibility, or provider-license approval.
  evidence_ref: https://github.com/gh-jai/financial-valuation-ai/blob/3b2a7adec3fb2c9c8d4d9ce2eb9aa61e75f5379c/docs/milestones/M9-I2-post-owner-approval-snapshot-closure.md
  evidence_sha256: d7cd3e309505a0bd2168b22f2689a508847bbe354a26d526ab326c92f1d4cb73
  previous_event_hash: 288270085de0794ed954ef10ab41746a85fe357e6c02d5ff1a43adb949aabcea
event_hash: d203f487fd9a6c1623f71d5ed0a68828c586956ebdb739c1cf5aa6e6569117c1
```

## Publication and carrier-update rule

The future immutable Git object containing these exact attestation bytes is the durable next event
in the existing chain. Only after its object identity, public URL, file SHA-256, canonical event
hash, previous-event link, and exact-head CI are independently verified may a separately authorized
carrier-only update reference it and transition the current snapshot to
`CLOSED_WITH_SINGLE_MAINTAINER_EXCEPTION`. That update must not alter any file in the five-file
current subject manifest or any existing immutable event.

No attached PDF, original extract, continuous source text, long quotation, private-source content,
real issuer data, or live provider response was read or used to produce this attestation candidate.
