# M9-I5 Runtime Status Snapshot Closure Attestation

Artifact state: `local_candidate_not_yet_immutable`
Governance path: `single-maintainer exception`
Contract state: `owner_approved_with_exception`
Attested predecessor snapshot: `126ad4fc548b897546ebe9c09832b3e79283bab5fae860be3a264b6c30055980`
Current snapshot state before immutable publication: `NOT_CLOSED`

## Decision boundary

This is the next append-only `snapshot_closure_attestation` candidate for the M9-I5
disabled-offline runtime post-merge status snapshot
`5162b931381dd88149efc2c02aebf787ef6bf02e2d33910d086428f94f410a40`. The owner chooses
`CLOSED_WITH_SINGLE_MAINTAINER_EXCEPTION` for those exact subject bytes while explicitly
disclosing that the owner is also the author/remediator and that no independent review occurred.

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
  event_id: m9-i5-runtime-status-snapshot-closure-attestation-20260820T185719Z
  exception_id: m9-i2-single-maintainer-9326b6c7-5162b931
  decision_kind: snapshot_closure_attestation
  occurred_at: "2026-08-20T18:57:19Z"
  actor_id: "github:gh-jai"
  actor_role: project_owner
  actor_type: human
  repository: gh-jai/financial-valuation-ai
  baseline_sha: 1bfe3707b0b0fd6302f9f212894c9a0afa8254e2
  subject_kind: exact_snapshot
  subject_id: 5162b931381dd88149efc2c02aebf787ef6bf02e2d33910d086428f94f410a40
  subject_commit_sha: 5db235d4e5a6046613f023b032a816da4229a351
  contract_path: docs/milestones/M9-I2-issuer-resolution-contract-lock.md
  contract_sha256: 9326b6c76dcfe3061c5e356b5141d9f458d57694cb4e6b01b6470b0bf044d84e
  snapshot_id: 5162b931381dd88149efc2c02aebf787ef6bf02e2d33910d086428f94f410a40
  decision: CLOSED_WITH_SINGLE_MAINTAINER_EXCEPTION
  eligibility_reason: >-
    The canonical repository is operated through the single project-owner identity github:gh-jai.
    That identity authored or remediated the subject bytes, GitHub cannot accept its self-approval
    as independent review, and no second eligible reviewer was reasonably available after the
    separation-of-duties requirement was evaluated.
  shared_actor_disclosure: >-
    github:gh-jai is simultaneously the project owner and the author/remediator of the exact
    subject bytes; reviewer/author separation did not occur, formal review 4986157642 is a
    disclosed same-maintainer COMMENTED_PASS, and this event is not independent review.
  separation_waiver_scope: >-
    M9-I2 exact-snapshot documentation governance for the M9-I5 disabled-offline runtime
    post-merge status synchronization only. The waiver does not apply to provider or network
    activation, live requests, real-company data, M9-I6, release, or any qualified-review gate.
  ci_evidence:
    workflow_name: Validate
    workflow_run_id: 32405264670
    workflow_run_number: 114
    workflow_url: https://github.com/gh-jai/financial-valuation-ai/actions/runs/32405264670
    trigger: push
    head_sha: 5db235d4e5a6046613f023b032a816da4229a351
    status: completed
    conclusion: success
    matrix_jobs:
      - python_version: "3.10"
        job_id: 96542747245
        job_url: https://github.com/gh-jai/financial-valuation-ai/actions/runs/32405264670/job/96542747245
        conclusion: success
        full_suite: 586 passed
      - python_version: "3.12"
        job_id: 96542746796
        job_url: https://github.com/gh-jai/financial-valuation-ai/actions/runs/32405264670/job/96542746796
        conclusion: success
        full_suite: 586 passed
  exact_head_ci_evidence:
    workflow_name: Validate
    workflow_run_id: 32403641346
    workflow_run_number: 113
    workflow_url: https://github.com/gh-jai/financial-valuation-ai/actions/runs/32403641346
    trigger: pull_request
    head_sha: da7b1fe603fc4de07689534584685f71c4685383
    status: completed
    conclusion: success
    matrix_jobs:
      - python_version: "3.10"
        job_id: 96537467386
        job_url: https://github.com/gh-jai/financial-valuation-ai/actions/runs/32403641346/job/96537467386
        conclusion: success
        full_suite: 586 passed
      - python_version: "3.12"
        job_id: 96537467797
        job_url: https://github.com/gh-jai/financial-valuation-ai/actions/runs/32403641346/job/96537467797
        conclusion: success
        full_suite: 586 passed
  local_validation_evidence:
    environment:
      python: 3.12.13
      pytest: 8.4.2
      jsonschema: 4.26.0
      pyyaml: 6.0.3
    commands:
      - command: python -m pytest tests/unit/test_m9_i2_governance.py -q
        result: 39 passed
      - command: run all Validate workflow artifact validators and repository policy
        result: passed; 41 schemas and 121 governed documents; 430 repository candidate files
      - command: python -m pytest -q
        result: 590 passed
      - command: pre-commit run --all-files
        result: passed; all 16 configured hooks
      - command: git diff --check
        result: passed
    evidence_scope: >-
      Reviewed head da7b1fe603fc4de07689534584685f71c4685383 and byte-identical main subject
      tree 7321bab34145e34aaac382bc7f216791e0f00798 at subject commit
      5db235d4e5a6046613f023b032a816da4229a351 before this attestation candidate was added.
  review_evidence:
    pull_request_number: 41
    pull_request_url: https://github.com/gh-jai/financial-valuation-ai/pull/41
    base_sha: 1bfe3707b0b0fd6302f9f212894c9a0afa8254e2
    reviewed_head_sha: da7b1fe603fc4de07689534584685f71c4685383
    reviewed_tree_sha: 7321bab34145e34aaac382bc7f216791e0f00798
    main_subject_tree_sha: 7321bab34145e34aaac382bc7f216791e0f00798
    review_id: 4986157642
    review_node_id: PRR_kwDOTqKoFc8AAAABKTK6Sg
    github_state: COMMENTED
    disposition: COMMENTED_PASS
    finding_resolution: no_findings
  milestone_contract_evidence:
    path: docs/milestones/M9-I5-us-gaap-normalization-reconciliation-contract-lock.md
    sha256: 99ee481383eece5d21f45e22dc2ced16f3e04f3bd8ae169ac7c58279c8121949
    runtime_pull_request_number: 40
    runtime_reviewed_head_sha: 8a864a71b28ee67d579fc946ec82abc07db0e125
    runtime_merge_commit_sha: 1bfe3707b0b0fd6302f9f212894c9a0afa8254e2
    runtime_reviewed_and_merged_tree_sha: c709b3231a740c9815e9e24b5dca27b1b6bb8fa0
  finding_disposition: >-
    PR #41 formal same-maintainer exact-head review 4986157642 recorded COMMENTED_PASS with no
    findings against reviewed head da7b1fe603fc4de07689534584685f71c4685383. Its tree is
    byte-identical to main subject commit 5db235d4e5a6046613f023b032a816da4229a351. Validate #113
    passed at the reviewed head and post-merge Validate #114 passed at the exact main subject
    commit. No unresolved blocking, high, or medium code or governance finding remains against the
    exact subject bytes.
  residual_risk_acceptance: >-
    The owner accepts the loss of independent challenge and the increased risk of undetected bias
    or governance error. Proceeding is proportionate only because the exception is transparent,
    exact-snapshot, immutable-main-commit, CI, review, finding-disposition, and event-chain bound;
    limited to documentation governance; grants no provider, network, live-data, M9-I6, release,
    or qualified-review authority; and remains fail-closed until later immutable publication and
    carrier verification.
  authority_boundary: >-
    This decision concerns only exact documentation snapshot
    5162b931381dd88149efc2c02aebf787ef6bf02e2d33910d086428f94f410a40 under the
    single-maintainer exception after immutable publication and later carrier verification. This
    local candidate does not close the snapshot. It records only the already-merged M9-I5
    disabled-offline, repository-synthetic, network-denied runtime state. It does not authorize
    staging, committing, pushing, PR creation or state changes, publication, provider or network
    activation, live requests, credentials, real-company data, attachment use, frozen registry,
    schema or immutable-contract changes, M9-I6, release, or any legal, privacy, security,
    accessibility, provider-license, or qualified-review approval.
  evidence_ref: https://github.com/gh-jai/financial-valuation-ai/blob/5db235d4e5a6046613f023b032a816da4229a351/docs/milestones/M9-I2-post-owner-approval-snapshot-closure.md
  evidence_sha256: e2da7ce99a500e449d2a2f9ec54351d936bf5dd0823f41879fba56f8b45c26a9
  previous_event_hash: 0f46b14d8143af829df356c0b81ee20c449739a9c8e9219d5fdbb9c699aa99e8
event_hash: b94532a148372195f3aed05937460aef699fd44531714cd79ff537c9ac48861c
```

## Publication and carrier-update rule

The future immutable Git object containing these exact attestation bytes is the durable next event
in the existing chain. Only after its object identity, public URL, file SHA-256, canonical event
hash, previous-event link, and exact-head CI are verified may a separately authorized carrier-only
update reference it and transition snapshot
`5162b931381dd88149efc2c02aebf787ef6bf02e2d33910d086428f94f410a40` to
`CLOSED_WITH_SINGLE_MAINTAINER_EXCEPTION`. That update must not alter any file in the five-file
subject manifest or any existing immutable event.

No attached PDF, original extract, continuous source text, long quotation, private-source content,
real issuer data, or live provider response was read or used to produce this attestation candidate.
