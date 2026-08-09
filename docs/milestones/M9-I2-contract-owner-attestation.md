# M9-I2 Contract Owner Attestation

Artifact state: `local_candidate_not_yet_immutable`
Governance path: `single-maintainer exception`
Contract state before immutable publication: `candidate`
Package closure: `NOT_CLOSED`

## Decision boundary

This is the first-stage `contract_owner_attestation` candidate for the frozen M9-I2 contract. The
owner chooses `owner_approved_with_exception` for that exact contract, while explicitly disclosing
that the owner is also the author/remediator and that no independent review occurred. The decision
is limited to the contract/documentation boundary.

This local file is not yet an immutable public attestation. It cannot advance the approval record
until a separately authorized commit and publication preserve these exact bytes in an immutable
Git object and the approval record is later updated to reference that object. It cannot close the
subject snapshot; the ordered `snapshot_closure_attestation` remains separately required.

## Canonical event

`event_hash` is lowercase SHA-256 over UTF-8 canonical JSON of the complete `event` mapping below,
using lexicographically sorted object keys, no insignificant whitespace, JSON booleans/null, and
no ASCII escaping. The hash excludes the top-level `event_hash` field itself.

```yaml
event:
  schema_version: m9_i2_exception_attestation/v1
  event_id: m9-i2-contract-owner-attestation-20260809T124450Z
  exception_id: m9-i2-single-maintainer-9326b6c7
  decision_kind: contract_owner_attestation
  occurred_at: "2026-08-09T12:44:50Z"
  actor_id: "github:gh-jai"
  actor_role: project_owner
  actor_type: human
  repository: gh-jai/financial-valuation-ai
  baseline_sha: 3945e90559ec2e10771489078c9e8f52036209b7
  subject_kind: contract
  subject_id: 9326b6c76dcfe3061c5e356b5141d9f458d57694cb4e6b01b6470b0bf044d84e
  subject_commit_sha: 743159d08ab05541a8d4fe25859bc9f9a49c5287
  contract_path: docs/milestones/M9-I2-issuer-resolution-contract-lock.md
  contract_sha256: 9326b6c76dcfe3061c5e356b5141d9f458d57694cb4e6b01b6470b0bf044d84e
  snapshot_id: not_applicable_for_contract_owner_attestation
  decision: owner_approved_with_exception
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
    workflow_run_id: 31313816548
    workflow_run_number: 66
    workflow_url: https://github.com/gh-jai/financial-valuation-ai/actions/runs/31313816548
    trigger: pull_request
    head_sha: 743159d08ab05541a8d4fe25859bc9f9a49c5287
    status: completed
    conclusion: success
    governance_regressions: 9 passed
    matrix_jobs:
      - python_version: "3.10"
        job_id: 93245702435
        job_url: https://github.com/gh-jai/financial-valuation-ai/actions/runs/31313816548/job/93245702435
        conclusion: success
        full_suite: 334 passed
      - python_version: "3.12"
        job_id: 93245702418
        job_url: https://github.com/gh-jai/financial-valuation-ai/actions/runs/31313816548/job/93245702418
        conclusion: success
        full_suite: 334 passed
  local_validation_evidence:
    environment:
      python: 3.12.13
      pytest: 8.4.2
    commands:
      - command: python -m pytest tests/unit/test_m9_i2_governance.py -q
        result: 9 passed
      - command: pre-commit run --all-files
        result: 16 of 16 configured hooks passed without rewrites
      - command: python -m pytest -q
        result: 334 passed
      - command: git diff --check
        result: passed
    hook_composition: six upstream hooks and 10 local hooks, including repository policy
    evidence_scope: exact subject commit before this attestation candidate was added
  finding_disposition: >-
    No unresolved blocking, high, or medium code or governance finding remains against exact
    subject commit 743159d08ab05541a8d4fe25859bc9f9a49c5287.
  residual_risk_acceptance: >-
    The owner accepts the loss of independent challenge and the increased risk of undetected bias
    or governance error. Proceeding is proportionate only because the exception is transparent,
    exact-hash and CI bound, limited to documentation governance, followed by a separately
    attested snapshot, and grants no runtime, publication, data, or release authority.
  authority_boundary: >-
    This decision approves only the frozen M9-I2 contract boundary under the single-maintainer
    exception after immutable publication. It does not authorize implementation, staging,
    committing, pushing, PR state changes, publication, live or provider access, real-company
    data, M9-I3 or later work, release, or any legal, privacy, security, accessibility, or
    provider-license approval.
  evidence_ref: https://github.com/gh-jai/financial-valuation-ai/blob/743159d08ab05541a8d4fe25859bc9f9a49c5287/docs/milestones/M9-I2-issuer-resolution-contract-lock.md
  evidence_sha256: 9326b6c76dcfe3061c5e356b5141d9f458d57694cb4e6b01b6470b0bf044d84e
  previous_event_hash: GENESIS
event_hash: 1c0a77e77fd3ecc755d86c0d0db3c229d5194be63eb87af5bd4984520506df83
```

## Publication and next-stage rule

The future immutable Git object containing these exact attestation bytes is the durable event
artifact. The approval record may reference it only after its object identity and public URL are
known and the event hash above recomputes. Updating the approval record creates a new subject
snapshot that must receive its own exact-subject-commit remote CI and later immutable
`snapshot_closure_attestation` before any
`CLOSED_WITH_SINGLE_MAINTAINER_EXCEPTION` claim.

No attached PDF, original extract, continuous source text, long quotation, private-source content,
real issuer data, or live provider response was read or used to produce this attestation candidate.
