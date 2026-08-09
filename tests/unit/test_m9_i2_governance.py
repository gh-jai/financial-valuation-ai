import hashlib
import re
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "docs/milestones/M9-I2-issuer-resolution-contract-lock.md"
APPROVAL = ROOT / "docs/milestones/M9-I2-contract-lock-review-approval-record.md"
CLOSURE = ROOT / "docs/milestones/M9-I2-post-owner-approval-snapshot-closure.md"
CONTRACT_SHA256 = "4c596e806896a9693dd95766b7f5d3207c7f0969ee69e4aeeed05ab5e1e016ad"
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
    assert "A fresh project-owner decision may occur only after a fresh" in normalized_approval
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

    combined = "\n".join(summaries.values())
    for stale_claim in (
        "M9-I2 owner-approved contract lock",
        "revised M9-I2 exact-SHA contract independently reviewed and owner-approved",
        "has an independent `PASS` and exact-SHA project-owner approval",
    ):
        assert stale_claim not in combined


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
