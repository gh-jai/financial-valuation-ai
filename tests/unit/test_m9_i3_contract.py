import hashlib
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "docs/milestones/M9-I3-immutable-snapshot-store-contract.md"
REVIEW = ROOT / "docs/milestones/M9-I3-implementation-review.md"


def test_m9_i3_contract_records_authority_limits_and_exit_matrix() -> None:
    text = CONTRACT.read_text(encoding="utf-8")
    normalized = " ".join(text.split())
    for requirement in (
        "IMPLEMENTATION_AUTHORIZED_LOCAL_CANDIDATE",
        "Network state: `DENIED`",
        "1,048,576 bytes",
        "2,000",
        "write-once",
        "implementation-separated validation",
        "No live SEC or provider access",
        "No user-file collection",
        "No commit, push, Draft PR",
    ):
        assert requirement in normalized


def test_m9_i3_contract_excludes_sources_and_later_slices() -> None:
    text = CONTRACT.read_text(encoding="utf-8")
    for excluded in (
        "No real issuer",
        "PDF",
        "private extract",
        "M9-I4",
        "M9-I5",
        "M9-I6",
        "valuation",
        "LLM",
        "UI",
    ):
        assert excluded in text


def test_m9_i3_review_reports_local_evidence_without_publication_claim() -> None:
    text = REVIEW.read_text(encoding="utf-8")
    assert "LOCAL_CANDIDATE_VALIDATED_REVIEW_PENDING" in text
    assert "focused M9-I3 suite: `PASS`; 42 tests" in text
    assert "complete repository suite: `PASS`; 424 tests" in text
    assert "Python 3.10 runtime and GitHub Actions matrix: not yet run" in text
    assert "commit, push, and Draft PR not authorized" in text


def test_m9_i3_review_manifest_binds_every_local_subject() -> None:
    text = REVIEW.read_text(encoding="utf-8")
    entries = re.findall(r"^([a-f0-9]{64}) (.+)$", text, flags=re.MULTILINE)
    assert len(entries) == 14
    assert str(REVIEW.relative_to(ROOT)) not in {path for _, path in entries}
    for expected, relative in entries:
        content = (ROOT / relative).read_bytes()
        assert hashlib.sha256(content).hexdigest() == expected
