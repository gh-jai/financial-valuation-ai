# M9-I5 Contract-Lock Status Snapshot Closure Attestation

Artifact state: `local_candidate_not_yet_immutable`
Governance path: `single-maintainer exception`
Contract state: `owner_approved_with_exception`
Attested predecessor snapshot: `8996b5c370576a09b556823ed61e5f025f8640aa2c9d061e29895e9384886f9d`
Current snapshot state before immutable publication: `NOT_CLOSED`

## Decision boundary

This is the next append-only `snapshot_closure_attestation` candidate for the M9-I5 contract-lock
post-merge status snapshot `126ad4fc548b897546ebe9c09832b3e79283bab5fae860be3a264b6c30055980`.
The owner chooses `CLOSED_WITH_SINGLE_MAINTAINER_EXCEPTION` for those exact subject bytes while
explicitly disclosing that the owner is also the author/remediator and that no independent review
occurred.

This local file is not yet an immutable public attestation. Its existence does not close the
current snapshot. Closure remains `NOT_CLOSED` until separately authorized publication preserves
these exact bytes in an immutable Git object, exact-head CI verifies that object, and a later
out-of-manifest carrier-only update verifies the object identity, file SHA-256, canonical event
hash, event-chain link, and authority boundary. Each later state transition requires separate
authorization.

## Canonical event

`event_hash` is lowercase SHA-256 over UTF-8 canonical JSON of the complete `event` mapping below,
using lexicographically sorted object keys, no insignificant whitespace, JSON booleans/null, and
no ASCII escaping. The hash excludes the top-level `event_hash` field itself.

```yaml
event:
  schema_version: m9_i2_exception_attestation/v1
  event_id: m9-i5-status-snapshot-closure-attestation-20260814T190051Z
  exception_id: m9-i2-single-maintainer-9326b6c7-126ad4fc
  decision_kind: snapshot_closure_attestation
  occurred_at: "2026-08-14T19:00:51Z"
  actor_id: "github:gh-jai"
  actor_role: project_owner
  actor_type: human
  repository: gh-jai/financial-valuation-ai
  baseline_sha: 98536ff27a80bd8ddb4dd9e651ca7217c1c0d582
  subject_kind: exact_snapshot
  subject_id: 126ad4fc548b897546ebe9c09832b3e79283bab5fae860be3a264b6c30055980
  subject_commit_sha: fe2131721ea20c89ca3b452c0a7ef80dac37b236
  contract_path: docs/milestones/M9-I2-issuer-resolution-contract-lock.md
  contract_sha256: 9326b6c76dcfe3061c5e356b5141d9f458d57694cb4e6b01b6470b0bf044d84e
  snapshot_id: 126ad4fc548b897546ebe9c09832b3e79283bab5fae860be3a264b6c30055980
  decision: CLOSED_WITH_SINGLE_MAINTAINER_EXCEPTION
  eligibility_reason: >-
    The canonical repository is operated through the single project-owner identity github:gh-jai.
    That identity authored or remediated the subject bytes, GitHub cannot accept its self-approval
    as independent review, and no second eligible reviewer was reasonably available after the
    separation-of-duties requirement was evaluated.
  shared_actor_disclosure: >-
    github:gh-jai is simultaneously the project owner and the author/remediator of the exact
    subject bytes; reviewer/author separation did not occur, formal review 4937392887 is a
    disclosed same-maintainer COMMENTED_PASS, and this event is not independent review.
  separation_waiver_scope: >-
    M9-I2 exact-snapshot documentation governance for the M9-I5 contract-lock status
    synchronization only. The waiver does not apply to M1-M7 runtime composition, human-only
    approvals, M9-I2 through M9-I4 runtime controls, M9-I4 live readiness, M9-I5 runtime, M9-I6,
    or any qualified-review gate.
  ci_evidence:
    workflow_name: Validate
    workflow_run_id: 31830905746
    workflow_run_number: 106
    workflow_url: https://github.com/gh-jai/financial-valuation-ai/actions/runs/31830905746
    trigger: push
    head_sha: fe2131721ea20c89ca3b452c0a7ef80dac37b236
    status: completed
    conclusion: success
    governance_regressions: 44 passed
    matrix_jobs:
      - python_version: "3.10"
        job_id: 94866073988
        job_url: https://github.com/gh-jai/financial-valuation-ai/actions/runs/31830905746/job/94866073988
        conclusion: success
        full_suite: 526 passed
      - python_version: "3.12"
        job_id: 94866074048
        job_url: https://github.com/gh-jai/financial-valuation-ai/actions/runs/31830905746/job/94866074048
        conclusion: success
        full_suite: 526 passed
  exact_head_ci_evidence:
    workflow_name: Validate
    workflow_run_id: 31803048721
    workflow_run_number: 105
    workflow_url: https://github.com/gh-jai/financial-valuation-ai/actions/runs/31803048721
    trigger: pull_request
    head_sha: f44905584c88a1476a05c07e3e01adb46457b6f0
    status: completed
    conclusion: success
    matrix_jobs:
      - python_version: "3.10"
        job_id: 94775314595
        job_url: https://github.com/gh-jai/financial-valuation-ai/actions/runs/31803048721/job/94775314595
        conclusion: success
        full_suite: 526 passed
      - python_version: "3.12"
        job_id: 94775314423
        job_url: https://github.com/gh-jai/financial-valuation-ai/actions/runs/31803048721/job/94775314423
        conclusion: success
        full_suite: 526 passed
  local_validation_evidence:
    environment:
      python: 3.12.13
      pytest: 8.4.2
      jsonschema: 4.26.0
      pyyaml: 6.0.3
    commands:
      - command: python -m pytest tests/unit/test_m9_i2_governance.py -q
        result: 33 passed
      - command: run all Validate workflow artifact validators and repository policy
        result: passed; 41 schemas and 121 governed documents; 418 repository candidate files
      - command: python -m pytest -q
        result: 530 passed
      - command: pre-commit run --all-files
        result: passed; all 16 configured hooks
      - command: git diff --check
        result: passed
    evidence_scope: >-
      Reviewed head f44905584c88a1476a05c07e3e01adb46457b6f0 and byte-identical main subject
      tree 914cdbc87b8e5eea07a1bffe21a492d51a018d3f at subject commit
      fe2131721ea20c89ca3b452c0a7ef80dac37b236 before this attestation candidate was added.
  review_evidence:
    pull_request_number: 37
    pull_request_url: https://github.com/gh-jai/financial-valuation-ai/pull/37
    base_sha: 98536ff27a80bd8ddb4dd9e651ca7217c1c0d582
    reviewed_head_sha: f44905584c88a1476a05c07e3e01adb46457b6f0
    reviewed_tree_sha: 914cdbc87b8e5eea07a1bffe21a492d51a018d3f
    main_subject_tree_sha: 914cdbc87b8e5eea07a1bffe21a492d51a018d3f
    review_id: 4937392887
    review_node_id: PRR_kwDOTqKoFc8AAAABJkqi9w
    disposition: COMMENTED_PASS
    finding_resolution: no_findings
  milestone_contract_evidence:
    path: docs/milestones/M9-I5-us-gaap-normalization-reconciliation-contract-lock.md
    sha256: 99ee481383eece5d21f45e22dc2ced16f3e04f3bd8ae169ac7c58279c8121949
    pull_request_number: 36
    reviewed_head_sha: c4715930a59b6e2f79000cffdb7c0ebbec7cf217
    merge_commit_sha: 98536ff27a80bd8ddb4dd9e651ca7217c1c0d582
    reviewed_and_merged_tree_sha: a10327d7057c3478a38c9230667bc0529ceb6c21
  finding_disposition: >-
    PR #37 formal same-maintainer exact-head review 4937392887 recorded COMMENTED_PASS with no
    findings against reviewed head f44905584c88a1476a05c07e3e01adb46457b6f0. Its tree is
    byte-identical to main subject commit fe2131721ea20c89ca3b452c0a7ef80dac37b236. Validate #105
    passed at the reviewed head and post-merge Validate #106 passed at the exact main subject
    commit. No unresolved blocking, high, or medium code or governance finding remains against the
    exact subject bytes.
  residual_risk_acceptance: >-
    The owner accepts the loss of independent challenge and the increased risk of undetected bias
    or governance error. Proceeding is proportionate only because the exception is transparent,
    exact-snapshot, immutable-main-commit, CI, review, finding-disposition, and event-chain bound;
    limited to documentation governance; grants no runtime, publication, data, provider, or release
    authority; and remains fail-closed until later immutable publication and carrier verification.
  authority_boundary: >-
    This decision concerns only exact documentation snapshot
    126ad4fc548b897546ebe9c09832b3e79283bab5fae860be3a264b6c30055980 under the
    single-maintainer exception after immutable publication and later carrier verification. This
    local candidate does not close the snapshot. It does not authorize staging, committing,
    pushing, PR creation or state changes, publication, runtime changes, network/provider
    activation, live SEC access, credentials, actual User-Agent values, real-company data,
    attachment use, M9-I5 runtime, M9-I6, release, or any legal, privacy, security, accessibility,
    or provider-license approval.
  evidence_ref: https://github.com/gh-jai/financial-valuation-ai/blob/fe2131721ea20c89ca3b452c0a7ef80dac37b236/docs/milestones/M9-I2-post-owner-approval-snapshot-closure.md
  evidence_sha256: 13d0e784b7b64de0c5979303f789194201c5fb76154649d9936cb0fe41dce4b9
  previous_event_hash: a2ab8b45dcd40605eba3a680322be3da5318fccac97424356ca94364bfca17d1
event_hash: 0f46b14d8143af829df356c0b81ee20c449739a9c8e9219d5fdbb9c699aa99e8
```

## Publication and carrier-update rule

The future immutable Git object containing these exact attestation bytes is the durable next event
in the existing chain. Only after its object identity, public URL, file SHA-256, canonical event
hash, previous-event link, and exact-head CI are independently verified may a separately authorized
carrier-only update reference it and transition snapshot
`126ad4fc548b897546ebe9c09832b3e79283bab5fae860be3a264b6c30055980` to
`CLOSED_WITH_SINGLE_MAINTAINER_EXCEPTION`. That update must not alter any file in the five-file
subject manifest or any existing immutable event.

No attached PDF, original extract, continuous source text, long quotation, private-source content,
real issuer data, or live provider response was read or used to produce this attestation candidate.
