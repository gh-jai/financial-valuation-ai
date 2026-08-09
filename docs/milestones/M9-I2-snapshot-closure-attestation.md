# M9-I2 Snapshot Closure Attestation

Artifact state: `local_candidate_not_yet_immutable`
Governance path: `single-maintainer exception`
Contract state: `owner_approved_with_exception`
Package closure before immutable publication: `NOT_CLOSED`

## Decision boundary

This is the second-stage `snapshot_closure_attestation` candidate for exact documentation snapshot
`1c3754e724f98ff8324c567237070b68fe20514e678de3d1787e51d47f9da918`. The owner chooses
`CLOSED_WITH_SINGLE_MAINTAINER_EXCEPTION` for that exact snapshot while explicitly disclosing that
the owner is also the author/remediator and that no independent review occurred.

This local file is not yet an immutable public attestation. It cannot close the package until a
separately authorized commit and publication preserve these exact bytes in an immutable Git object
and the out-of-manifest closure carrier is later updated to reference that object. Until then, the
authoritative package state remains `NOT_CLOSED`.

## Canonical event

`event_hash` is lowercase SHA-256 over UTF-8 canonical JSON of the complete `event` mapping below,
using lexicographically sorted object keys, no insignificant whitespace, JSON booleans/null, and
no ASCII escaping. The hash excludes the top-level `event_hash` field itself.

```yaml
event:
  schema_version: m9_i2_exception_attestation/v1
  event_id: m9-i2-snapshot-closure-attestation-20260809T133331Z
  exception_id: m9-i2-single-maintainer-9326b6c7-1c3754e7
  decision_kind: snapshot_closure_attestation
  occurred_at: "2026-08-09T13:33:31Z"
  actor_id: "github:gh-jai"
  actor_role: project_owner
  actor_type: human
  repository: gh-jai/financial-valuation-ai
  baseline_sha: 3945e90559ec2e10771489078c9e8f52036209b7
  subject_kind: exact_snapshot
  subject_id: 1c3754e724f98ff8324c567237070b68fe20514e678de3d1787e51d47f9da918
  subject_commit_sha: 01b5d95bc990242321cfea3e6b7ddcde7b8a1f4f
  contract_path: docs/milestones/M9-I2-issuer-resolution-contract-lock.md
  contract_sha256: 9326b6c76dcfe3061c5e356b5141d9f458d57694cb4e6b01b6470b0bf044d84e
  snapshot_id: 1c3754e724f98ff8324c567237070b68fe20514e678de3d1787e51d47f9da918
  decision: CLOSED_WITH_SINGLE_MAINTAINER_EXCEPTION
  eligibility_reason: >-
    The canonical repository is operated through the single project-owner identity github:gh-jai.
    That identity authored or remediated the subject bytes, GitHub cannot accept its self-approval
    as an independent review, and no second eligible reviewer was reasonably available after the
    separation-of-duties requirement was evaluated.
  shared_actor_disclosure: >-
    github:gh-jai is simultaneously the project owner and the author/remediator of the exact
    subject commit; reviewer/author separation did not occur and this event is not independent
    review.
  separation_waiver_scope: >-
    M9-I2 contract and documentation governance only. The waiver does not apply to M1-M7 runtime
    composition, human-only approvals, implementation, or any qualified-review gate.
  ci_evidence:
    workflow_name: Validate
    workflow_run_id: 31315947577
    workflow_run_number: 68
    workflow_url: https://github.com/gh-jai/financial-valuation-ai/actions/runs/31315947577
    trigger: pull_request
    head_sha: 01b5d95bc990242321cfea3e6b7ddcde7b8a1f4f
    status: completed
    conclusion: success
    governance_regressions: 14 passed
    matrix_jobs:
      - python_version: "3.10"
        job_id: 93251090338
        job_url: https://github.com/gh-jai/financial-valuation-ai/actions/runs/31315947577/job/93251090338
        conclusion: success
        full_suite: 339 passed
      - python_version: "3.12"
        job_id: 93251090352
        job_url: https://github.com/gh-jai/financial-valuation-ai/actions/runs/31315947577/job/93251090352
        conclusion: success
        full_suite: 339 passed
  local_validation_evidence:
    environment:
      python: 3.12.13
      pytest: 8.4.2
      jsonschema: 4.26.0
    commands:
      - command: python -m pytest tests/unit/test_m9_i2_governance.py -q
        result: 14 passed
      - command: pre-commit run --all-files
        result: 16 of 16 configured hooks passed without rewrites
      - command: python -m pytest -q
        result: 339 passed
      - command: git diff --check
        result: passed
    hook_composition: six upstream hooks and 10 local hooks, including repository policy
    evidence_scope: exact subject commit before this attestation candidate was added
  finding_disposition: >-
    No unresolved blocking, high, or medium code or governance finding remains against exact
    subject commit 01b5d95bc990242321cfea3e6b7ddcde7b8a1f4f.
  residual_risk_acceptance: >-
    The owner accepts the loss of independent challenge and the increased risk of undetected bias
    or governance error. Proceeding is proportionate only because the exception is transparent,
    exact-hash and CI bound, limited to documentation governance, grants no runtime, publication,
    data, or release authority, and any later subject-file change fails closed.
  authority_boundary: >-
    This decision closes only exact documentation snapshot
    1c3754e724f98ff8324c567237070b68fe20514e678de3d1787e51d47f9da918 under the
    single-maintainer exception after immutable publication. It does not authorize implementation,
    staging, committing, pushing, PR state changes, publication, live or provider access,
    real-company data, M9-I3 or later work, release, or any legal, privacy, security,
    accessibility, or provider-license approval.
  evidence_ref: https://github.com/gh-jai/financial-valuation-ai/blob/01b5d95bc990242321cfea3e6b7ddcde7b8a1f4f/docs/milestones/M9-I2-post-owner-approval-snapshot-closure.md
  evidence_sha256: 335ff417785d6e97b23e395c2341910499d1661cc65c1a881219ef22576bc772
  previous_event_hash: 1c0a77e77fd3ecc755d86c0d0db3c229d5194be63eb87af5bd4984520506df83
event_hash: 288270085de0794ed954ef10ab41746a85fe357e6c02d5ff1a43adb949aabcea
```

## Publication and carrier-update rule

The future immutable Git object containing these exact attestation bytes is the durable second
event. Only after its object identity, public URL, file SHA-256, and event hash are independently
verified may the out-of-manifest closure carrier reference it and record
`CLOSED_WITH_SINGLE_MAINTAINER_EXCEPTION`. That carrier-only update must not alter any file in the
five-file subject manifest.

No attached PDF, original extract, continuous source text, long quotation, private-source content,
real issuer data, or live provider response was read or used to produce this attestation candidate.
