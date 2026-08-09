from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PLAN = ROOT / "docs/milestones/M9-public-data-ingestion-normalization-plan.md"
CHECKLIST = ROOT / "templates/m9-implementation-planning-review-checklist.md"


def test_m9_plan_records_planning_but_not_implementation_authority() -> None:
    text = PLAN.read_text(encoding="utf-8")
    normalized = " ".join(text.split())
    assert "Status: Planning merged; M9-I1 baseline approved for publication" in text
    assert "[x] M9 implementation planning authorized" in text
    assert "[x] authorize M9-I1 implementation" in text
    for excluded in [
        "live SEC retrieval",
        "provider credentials",
        "real-company fixtures",
        "user uploads",
        "staging, committing, pushing",
    ]:
        assert excluded in normalized


def test_m9_plan_has_six_separately_approved_slices() -> None:
    text = PLAN.read_text(encoding="utf-8")
    for index in range(1, 7):
        assert f"`M9-I{index}`" in text
    assert "Approval of one slice does not authorize the next" in text
    assert "separately authorize M9-I1 implementation" in text


def test_m9_plan_preserves_offline_default_deny_boundary() -> None:
    text = PLAN.read_text(encoding="utf-8")
    normalized = " ".join(text.split())
    for requirement in [
        "All adapters start disabled",
        "CI and the default local suite use only compact synthetic fixtures",
        "The registry is default deny",
        "default test command succeeds with network disabled and without credentials",
        "independent validator",
    ]:
        assert requirement in normalized


def test_m9_plan_carries_every_m8_condition() -> None:
    text = PLAN.read_text(encoding="utf-8")
    assert "All `M8-C01` through `M8-C07` remain active" in text
    for condition in ["M8-C02", "M8-C03", "M8-C04", "M8-C06", "M8-C07"]:
        assert condition in text


def test_m9_planning_checklist_is_approved_and_keeps_implementation_separate() -> None:
    text = CHECKLIST.read_text(encoding="utf-8")
    assert "Status: Planning baseline merged; M9-I1 separately authorized and approved" in text
    assert "[x] approve baseline" in text
    assert "[x] authorize M9-I1 implementation" in text
    assert text.count("- [x]") >= 20
    assert "does not authorize `M9-I1`" in text


def test_i1_approval_does_not_authorize_later_or_live_capability() -> None:
    text = PLAN.read_text(encoding="utf-8")
    normalized = " ".join(text.split())
    assert "M9-I1 implementation baseline approved" in normalized
    assert "M9-I2 through M9-I6 remain unauthorized" in normalized
    assert "live SEC or provider access remains unauthorized" in normalized
