import hashlib
import re
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "docs/milestones/M9-I2-issuer-resolution-contract-lock.md"
APPROVAL = ROOT / "docs/milestones/M9-I2-contract-lock-review-approval-record.md"
CLOSURE = ROOT / "docs/milestones/M9-I2-post-owner-approval-snapshot-closure.md"
CONTRACT_SHA256 = "9326b6c76dcfe3061c5e356b5141d9f458d57694cb4e6b01b6470b0bf044d84e"
HASH_RE = re.compile(r"^[0-9a-f]{64}$")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def closure_text() -> str:
    return CLOSURE.read_text(encoding="utf-8")


def manifest_block(text: str) -> str:
    start = "BEGIN SUBJECT MANIFEST\n"
    end = "END SUBJECT MANIFEST\n"
    assert text.count(start) == 1
    assert text.count(end) == 1
    return text.split(start, 1)[1].split(end, 1)[0]


def manifest_entries(text: str) -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    for line in manifest_block(text).splitlines():
        digest, path = line.split(" ", 1)
        assert HASH_RE.fullmatch(digest)
        entries.append((digest, path))
    return entries


def test_frozen_contract_hash_is_unchanged() -> None:
    assert sha256(CONTRACT) == CONTRACT_SHA256
    approval = APPROVAL.read_text(encoding="utf-8")
    assert f"Contract SHA-256: `{CONTRACT_SHA256}`" in approval


def test_subject_manifest_and_snapshot_id_recompute() -> None:
    text = closure_text()
    entries = manifest_entries(text)
    assert [path for _, path in entries] == [
        "docs/milestones/M9-I2-issuer-resolution-contract-lock.md",
        "docs/milestones/M9-I2-contract-lock-review-approval-record.md",
        "PROJECT_STATUS.md",
        "ROADMAP.md",
        "README.md",
    ]
    for expected_digest, relative_path in entries:
        assert sha256(ROOT / relative_path) == expected_digest

    expected_snapshot = hashlib.sha256(manifest_block(text).encode("utf-8")).hexdigest()
    match = re.search(r"^Subject snapshot ID: `([0-9a-f]{64})`$", text, re.MULTILINE)
    assert match
    assert match.group(1) == expected_snapshot


def test_missing_durable_events_fail_closed() -> None:
    approval = APPROVAL.read_text(encoding="utf-8")
    closure = closure_text()

    assert "Status: `candidate`" in approval
    assert "Post-owner-approval package closure: `NOT_CLOSED`" in approval
    assert "Status: `NOT_CLOSED`" in closure
    assert "the exact subject snapshot is `NOT_CLOSED`" in closure
    assert "The exact subject snapshot is `CLOSED`" not in closure

    for required_field in (
        "`event_id`",
        "`occurred_at`",
        "`actor_id`",
        "`actor_role`",
        "`actor_type`",
        "`repository`",
        "`baseline_sha`",
        "`subject_kind`",
        "`subject_id`",
        "`decision`",
        "`evidence_ref`",
        "`evidence_sha256`",
        "`previous_event_hash`",
        "`event_hash`",
    ):
        assert required_field in closure

    evidence_rows = [
        line
        for line in closure.splitlines()
        if line.startswith("|") and line.endswith("| Not auditable |")
    ]
    assert len(evidence_rows) == 6
    assert all(row.count("| Missing") == 4 for row in evidence_rows)


def test_historical_assertions_cannot_satisfy_actor_separation_or_ordering() -> None:
    approval = APPROVAL.read_text(encoding="utf-8")
    closure = closure_text()
    normalized_approval = " ".join(approval.split())
    normalized_closure = " ".join(closure.split())

    assert "role labels without actor identifiers" in normalized_approval
    assert "The alternative single-maintainer path does not claim independence" in normalized_approval
    assert (
        "An owner-approval event must name the exact earlier independent-review `event_id`"
        in normalized_closure
    )
    assert "different from every actor that changed the reviewed subject bytes" in normalized_closure
    assert "single commit" in closure
    assert "does not prove that the claimed review preceded approval" in closure


def test_status_summaries_preserve_candidate_and_not_closed_state() -> None:
    summaries = {
        path: (ROOT / path).read_text(encoding="utf-8")
        for path in ("PROJECT_STATUS.md", "ROADMAP.md", "README.md")
    }
    for text in summaries.values():
        assert "`candidate`" in text
        assert "`NOT_CLOSED`" in text
        assert "single-maintainer" in text

    combined = "\n".join(summaries.values())
    for stale_claim in (
        "M9-I2 owner-approved contract lock",
        "revised M9-I2 exact-SHA contract independently reviewed and owner-approved",
        "has an independent `PASS` and exact-SHA project-owner approval",
    ):
        assert stale_claim not in combined


def test_single_maintainer_exception_is_explicit_and_narrow() -> None:
    contract = CONTRACT.read_text(encoding="utf-8")
    approval = APPROVAL.read_text(encoding="utf-8")
    closure = closure_text()
    normalized = " ".join((contract + approval + closure).split())

    assert "### 16.1 Single-maintainer documentation-governance exception" in contract
    assert "owner_approved_with_exception" in contract
    assert "This state never means `independently_reviewed`" in contract
    assert "M1-M7 runtime composition" in contract
    assert "cannot satisfy or waive those runtime controls" in contract
    assert "does not claim independence" in approval
    assert "M9-I2 documentation/contract governance" in closure
    assert "must never be represented as independent review" in normalized
    for protected_gate in (
        "legal",
        "privacy",
        "security",
        "accessibility",
        "provider-license",
    ):
        assert protected_gate in normalized


def test_exception_evidence_schema_is_complete_and_currently_pending() -> None:
    approval = APPROVAL.read_text(encoding="utf-8")
    closure = closure_text()

    required_exception_fields = (
        "`exception_id`",
        "`decision_kind`",
        "`eligibility_reason`",
        "`shared_actor_disclosure`",
        "`separation_waiver_scope`",
        "`subject_commit_sha`",
        "`contract_sha256` and `snapshot_id`",
        "`ci_evidence`",
        "`local_validation_evidence`",
        "`finding_disposition`",
        "`residual_risk_acceptance`",
        "`authority_boundary`",
        "`evidence_ref` and `evidence_sha256`",
        "`previous_event_hash` and `event_hash`",
    )
    assert all(field in closure for field in required_exception_fields)
    assert "immutable subject commit containing these bytes: pending" in approval
    assert (
        "successful exact-subject-commit remote CI run identifiers and URLs: pending" in approval
    )
    assert "immutable `contract_owner_attestation`" in approval
    assert "Consequently the current state remains `candidate`" in approval
    assert (
        "Eligibility to use the exception is not evidence that the exception was exercised"
        in " ".join(closure.split())
    )
    assert "focused M9-I2 governance regressions: `PASS`; nine tests passed" in closure
    assert "full pytest suite: `PASS`; 334 tests passed" in closure
    assert "not exact-subject-commit remote\nCI or either immutable owner attestation" in closure


def test_exception_states_are_distinct_and_fail_closed_on_change() -> None:
    contract = CONTRACT.read_text(encoding="utf-8")
    closure = closure_text()
    normalized = " ".join(closure.split())

    assert "`owner_approved_with_exception`" in contract
    assert "`CLOSED_WITH_SINGLE_MAINTAINER_EXCEPTION`" in closure
    assert (
        "The unqualified states `independently_reviewed`, `owner_approved`, and `CLOSED` are forbidden"
        in normalized
    )
    assert "`contract_owner_attestation`" in closure
    assert "`snapshot_closure_attestation`" in closure
    assert "mutable PR prose or an ordinary comment is insufficient" in closure
    assert "Any subject-file change invalidates the snapshot attestation" in normalized
    assert "returns the changed package to `NOT_CLOSED`" in normalized
    assert "later carrier-only update may reference the second immutable event" in normalized


def test_hook_count_includes_repository_policy_once() -> None:
    config = yaml.safe_load((ROOT / ".pre-commit-config.yaml").read_text(encoding="utf-8"))
    hooks = [hook for repository in config["repos"] for hook in repository["hooks"]]
    local = next(repository for repository in config["repos"] if repository["repo"] == "local")

    assert len(hooks) == 16
    assert len(local["hooks"]) == 10
    assert [hook["id"] for hook in local["hooks"]].count("fvi-repository-policy") == 1
    assert (
        "six upstream hooks plus all 10 local hooks, including\nrepository policy"
        in closure_text()
    )
