import hashlib
import json
import re
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "docs/milestones/M9-I2-issuer-resolution-contract-lock.md"
APPROVAL = ROOT / "docs/milestones/M9-I2-contract-lock-review-approval-record.md"
CLOSURE = ROOT / "docs/milestones/M9-I2-post-owner-approval-snapshot-closure.md"
OWNER_ATTESTATION = ROOT / "docs/milestones/M9-I2-contract-owner-attestation.md"
SNAPSHOT_ATTESTATION = ROOT / "docs/milestones/M9-I2-snapshot-closure-attestation.md"
CURRENT_SNAPSHOT_ATTESTATION = (
    ROOT / "docs/milestones/M9-I2-current-snapshot-closure-attestation.md"
)
M9_I4_STATUS_SNAPSHOT_ATTESTATION = (
    ROOT / "docs/milestones/M9-I4-status-snapshot-closure-attestation.md"
)
CONTRACT_SHA256 = "9326b6c76dcfe3061c5e356b5141d9f458d57694cb4e6b01b6470b0bf044d84e"
SUBJECT_COMMIT_SHA = "743159d08ab05541a8d4fe25859bc9f9a49c5287"
ATTESTATION_COMMIT_SHA = "a406b5fc5cfded19f116cc42309da13cea42c713"
ATTESTATION_BLOB_SHA = "0011df140cfb44af244526b0feb3d71a8c40cdd6"
ATTESTATION_SHA256 = "daba23aa09e9c6e3e13ed983518ecf44d4698160e38693c72357ed19b14f1a75"
ATTESTATION_EVENT_HASH = "1c0a77e77fd3ecc755d86c0d0db3c229d5194be63eb87af5bd4984520506df83"
HISTORICAL_SNAPSHOT_ID = "1c3754e724f98ff8324c567237070b68fe20514e678de3d1787e51d47f9da918"
CURRENT_SNAPSHOT_ID = "eb726009ac6afeebd5b15618ff03796c73790175f6360a3823f7c411dafde705"
SNAPSHOT_COMMIT_SHA = "01b5d95bc990242321cfea3e6b7ddcde7b8a1f4f"
SNAPSHOT_CARRIER_SHA256 = "335ff417785d6e97b23e395c2341910499d1661cc65c1a881219ef22576bc772"
SNAPSHOT_ATTESTATION_COMMIT_SHA = "1f1f0fd65e067015a17b016536f04ca9435493c3"
SNAPSHOT_ATTESTATION_BLOB_SHA = "955fae32f148385b4eb09f72d3775d8898fbf8ef"
SNAPSHOT_ATTESTATION_SHA256 = "16984ab5492114d111b1ba2c9c56e6a1c433a7fc6db3ace79d6dc2344bf7c12c"
SNAPSHOT_ATTESTATION_EVENT_HASH = (
    "288270085de0794ed954ef10ab41746a85fe357e6c02d5ff1a43adb949aabcea"
)
CURRENT_MAIN_SUBJECT_COMMIT_SHA = "3b2a7adec3fb2c9c8d4d9ce2eb9aa61e75f5379c"
CURRENT_MAIN_SUBJECT_TREE_SHA = "444938a913197824d2556193a4b3b1c812694210"
CURRENT_PRE_ATTESTATION_CARRIER_SHA256 = (
    "d7cd3e309505a0bd2168b22f2689a508847bbe354a26d526ab326c92f1d4cb73"
)
CURRENT_ATTESTATION_COMMIT_SHA = "1a3a33646e963525c952f7af735d8806369f6a70"
CURRENT_ATTESTATION_BLOB_SHA = "15b4654d22450665a1e5fd16c465e55a19837b27"
CURRENT_ATTESTATION_SHA256 = "36d24d8ed7a58adaf62e5d25426bbc891f9129e365f6224cc9dfa51ac2b248c3"
CURRENT_ATTESTATION_EVENT_HASH = (
    "d203f487fd9a6c1623f71d5ed0a68828c586956ebdb739c1cf5aa6e6569117c1"
)
CURRENT_ATTESTATION_CI_RUN_ID = "31524034663"
M9_I4_STATUS_SNAPSHOT_ID = "8996b5c370576a09b556823ed61e5f025f8640aa2c9d061e29895e9384886f9d"
M9_I4_STATUS_SUBJECT_COMMIT_SHA = "82c26f8b4872d849837b774bcbed2d9229a4ce96"
M9_I4_STATUS_SUBJECT_TREE_SHA = "7c4feeb48bf9a4088a72d53a45d618677a7208ae"
M9_I4_PRE_ATTESTATION_CARRIER_SHA256 = (
    "5b94dc1fb7c2f430a4f547a6dd39fcb753c7ea1224e5995c1b937068deaad06b"
)
M9_I4_STATUS_ATTESTATION_EVENT_HASH = (
    "a2ab8b45dcd40605eba3a680322be3da5318fccac97424356ca94364bfca17d1"
)
M9_I4_STATUS_ATTESTATION_COMMIT_SHA = "35d36fd74f0850b55fd833699f39cd091509fa72"
M9_I4_STATUS_ATTESTATION_TREE_SHA = "b8ed657d9f573ec332fac703cdd31a43980a0383"
M9_I4_STATUS_ATTESTATION_BLOB_SHA = "fab592fa6ac54f8f02f16985c0702f444442eca7"
M9_I4_STATUS_ATTESTATION_SHA256 = (
    "60e97e1eb35fdd303a5b6e705e5fe9c3b0ac67771a4a7bff626b77b3efdb0918"
)
M9_I4_STATUS_ATTESTATION_CI_RUN_ID = "31704722307"
STATUS_SUMMARY_PATHS = ("PROJECT_STATUS.md", "ROADMAP.md", "README.md")
HASH_RE = re.compile(r"^[0-9a-f]{64}$")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def closure_text() -> str:
    return CLOSURE.read_text(encoding="utf-8")


def delimited_block(text: str, start_label: str, end_label: str) -> str:
    start = f"{start_label}\n"
    end = f"{end_label}\n"
    assert text.count(start) == 1
    assert text.count(end) == 1
    return text.split(start, 1)[1].split(end, 1)[0]


def manifest_block(text: str) -> str:
    return delimited_block(text, "BEGIN SUBJECT MANIFEST", "END SUBJECT MANIFEST")


def historical_manifest_block(text: str) -> str:
    return delimited_block(
        text,
        "BEGIN HISTORICAL SUBJECT MANIFEST",
        "END HISTORICAL SUBJECT MANIFEST",
    )


def m9_i4_status_manifest_block(text: str) -> str:
    return delimited_block(
        text,
        "BEGIN M9-I4 STATUS SUBJECT MANIFEST",
        "END M9-I4 STATUS SUBJECT MANIFEST",
    )


def manifest_entries(text: str) -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    for line in manifest_block(text).splitlines():
        digest, path = line.split(" ", 1)
        assert HASH_RE.fullmatch(digest)
        entries.append((digest, path))
    return entries


def historical_manifest_entries(text: str) -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    for line in historical_manifest_block(text).splitlines():
        digest, path = line.split(" ", 1)
        assert HASH_RE.fullmatch(digest)
        entries.append((digest, path))
    return entries


def m9_i4_status_manifest_entries(text: str) -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    for line in m9_i4_status_manifest_block(text).splitlines():
        digest, path = line.split(" ", 1)
        assert HASH_RE.fullmatch(digest)
        entries.append((digest, path))
    return entries


def owner_attestation() -> dict[str, object]:
    text = OWNER_ATTESTATION.read_text(encoding="utf-8")
    match = re.search(r"```yaml\n(.*?)\n```", text, re.DOTALL)
    assert match
    parsed = yaml.safe_load(match.group(1))
    assert isinstance(parsed, dict)
    return parsed


def snapshot_attestation() -> dict[str, object]:
    text = SNAPSHOT_ATTESTATION.read_text(encoding="utf-8")
    match = re.search(r"```yaml\n(.*?)\n```", text, re.DOTALL)
    assert match
    parsed = yaml.safe_load(match.group(1))
    assert isinstance(parsed, dict)
    return parsed


def current_snapshot_attestation() -> dict[str, object]:
    text = CURRENT_SNAPSHOT_ATTESTATION.read_text(encoding="utf-8")
    match = re.search(r"```yaml\n(.*?)\n```", text, re.DOTALL)
    assert match
    parsed = yaml.safe_load(match.group(1))
    assert isinstance(parsed, dict)
    return parsed


def m9_i4_status_snapshot_attestation() -> dict[str, object]:
    text = M9_I4_STATUS_SNAPSHOT_ATTESTATION.read_text(encoding="utf-8")
    match = re.search(r"```yaml\n(.*?)\n```", text, re.DOTALL)
    assert match
    parsed = yaml.safe_load(match.group(1))
    assert isinstance(parsed, dict)
    return parsed


def test_frozen_contract_hash_is_unchanged() -> None:
    assert sha256(CONTRACT) == CONTRACT_SHA256
    approval = APPROVAL.read_text(encoding="utf-8")
    assert f"Contract SHA-256: `{CONTRACT_SHA256}`" in approval


def test_last_attested_subject_manifest_is_preserved_and_new_status_bytes_fail_closed() -> None:
    text = closure_text()
    entries = manifest_entries(text)
    assert [path for _, path in entries] == [
        "docs/milestones/M9-I2-issuer-resolution-contract-lock.md",
        "docs/milestones/M9-I2-contract-lock-review-approval-record.md",
        "PROJECT_STATUS.md",
        "ROADMAP.md",
        "README.md",
    ]
    manifest = {relative_path: digest for digest, relative_path in entries}
    for relative_path in (
        "docs/milestones/M9-I2-issuer-resolution-contract-lock.md",
        "docs/milestones/M9-I2-contract-lock-review-approval-record.md",
    ):
        assert sha256(ROOT / relative_path) == manifest[relative_path]
    for relative_path in STATUS_SUMMARY_PATHS:
        assert sha256(ROOT / relative_path) != manifest[relative_path]

    expected_snapshot = hashlib.sha256(manifest_block(text).encode("utf-8")).hexdigest()
    match = re.search(r"^Current subject snapshot ID: `([0-9a-f]{64})`$", text, re.MULTILINE)
    assert match
    assert match.group(1) == expected_snapshot
    assert match.group(1) == CURRENT_SNAPSHOT_ID


def test_historical_manifest_and_snapshot_evidence_are_preserved() -> None:
    text = closure_text()
    assert historical_manifest_entries(text) == [
        (CONTRACT_SHA256, "docs/milestones/M9-I2-issuer-resolution-contract-lock.md"),
        (
            "4734260f5946f57d08bb502919091025c49c7368d683d4334997e132d48ce969",
            "docs/milestones/M9-I2-contract-lock-review-approval-record.md",
        ),
        ("c181c387c98bc77fbb6d9c7ff4face0c6bd7edb41e4c71d3c505f064e6030c45", "PROJECT_STATUS.md"),
        ("d1cc6d6f3a63fef58b50ef3b83131f36de56fa6af1b01023936b4200cb8538ab", "ROADMAP.md"),
        ("6057359a14a20a8945a471d6fe527e7baab4481ee765d7d45bdae6b013c74f6d", "README.md"),
    ]
    historical_snapshot = hashlib.sha256(
        historical_manifest_block(text).encode("utf-8")
    ).hexdigest()
    assert historical_snapshot == HISTORICAL_SNAPSHOT_ID
    assert f"`{HISTORICAL_SNAPSHOT_ID}`" in text
    assert CURRENT_SNAPSHOT_ID != HISTORICAL_SNAPSHOT_ID


def test_completed_snapshot_closure_preserves_fail_closed_schema() -> None:
    approval = APPROVAL.read_text(encoding="utf-8")
    closure = closure_text()

    assert "Status: `owner_approved_with_exception`" in approval
    assert "Post-owner-approval package closure: `NOT_CLOSED`" in approval
    assert "Status: `CLOSED_WITH_SINGLE_MAINTAINER_EXCEPTION`; M9-I4 implementation" in closure
    assert "Last attested snapshot status: `CLOSED_WITH_SINGLE_MAINTAINER_EXCEPTION`" in closure
    assert "Historical snapshot status: `CLOSED_WITH_SINGLE_MAINTAINER_EXCEPTION`" in closure
    assert "both ordered immutable\nexception events remain verified" in closure
    assert "Any later mismatch in a\nsubject hash, event-chain link, immutable object" in closure
    assert "evidence fails closed to `NOT_CLOSED`" in closure

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


def test_status_summaries_advance_without_transferring_historical_closure() -> None:
    summaries = {
        path: (ROOT / path).read_text(encoding="utf-8")
        for path in STATUS_SUMMARY_PATHS
    }
    for text in summaries.values():
        assert "`owner_approved_with_exception`" in text
        assert "`NOT_CLOSED`" in text
        assert "M9-I3" in text

    closure = closure_text()
    normalized = " ".join(closure.split())
    assert "preserves the old immutable evidence without transferring its verdict" in normalized
    assert "current manifest is preserved in immutable subject commit" in normalized
    assert "out-of-manifest carrier is the authoritative closure record" in normalized
    assert (
        "No hash match, prior attestation, merged implementation, review remediation, or status prose alone"
        in normalized
    )

    combined = "\n".join(summaries.values())
    assert "M9-I2 runtime and M9-I3 through M9-I6 remain unauthorized" not in combined
    assert "M9-I2 implementation has not started" not in combined
    assert "does not yet provide M9-I2 issuer resolution" not in combined
    assert "M9-I4 implementation" in combined
    assert "M9-I5 through M9-I6" in combined
    assert "Validate run #81" in combined
    assert "PR #30" in combined
    assert "e26f55ef3e9b8babecb42f41f25be20dd918ea1e" in combined
    assert "Validate run #92" in combined
    assert "COMMENTED_PASS" in combined
    assert "587fa892cefb1397c7854c93698799fa88e18f8e" in combined
    assert "M9-I4 disabled offline implementation" in combined
    assert "PR #32" in combined
    assert "e5055afe312f7d83341eda2a172300a6a0f5bddb" in combined
    assert "c8c1b7bb5b8f63a77ea933e4c68c800e1fa0cbb1" in combined
    assert "Validate run #96" in combined
    assert "31700614399" in combined
    assert "505 tests per job" in combined
    assert "M9-I5 contract lock" in combined
    assert "live request" in combined
    assert "M9-I4 is contract-only" not in combined
    assert "No M9-I4 runtime implementation" not in combined


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


def test_exception_evidence_schema_is_complete_and_first_stage_is_immutable() -> None:
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
    assert f"immutable attestation commit: `{ATTESTATION_COMMIT_SHA}`" in approval
    assert f"attestation Git blob: `{ATTESTATION_BLOB_SHA}`" in approval
    assert f"attestation SHA-256: `{ATTESTATION_SHA256}`" in approval
    assert f"event hash: `{ATTESTATION_EVENT_HASH}`" in approval
    assert "The contract state is therefore\n`owner_approved_with_exception`" in approval
    assert "focused M9-I2 governance regressions: `PASS`; nine tests passed" in closure
    assert "full pytest suite: `PASS`; 334 tests passed" in closure
    assert "The ordered second-stage `snapshot_closure_attestation` is now immutable" in closure
    assert "focused M9-I2 governance regressions: `PASS`; 14 tests passed" in closure
    assert "full pytest suite: `PASS`; 339 tests passed" in closure
    assert "Exact-subject-commit remote\nCI and the immutable `snapshot_closure_attestation`" in closure


def test_exception_states_are_distinct_and_fail_closed_on_change() -> None:
    contract = CONTRACT.read_text(encoding="utf-8")
    closure = closure_text()
    normalized = " ".join(closure.split())

    assert "`owner_approved_with_exception`" in contract
    assert "`CLOSED_WITH_SINGLE_MAINTAINER_EXCEPTION`" in closure
    assert closure.startswith(
        "# M9-I2 Post-Owner-Approval Exact-Snapshot Closure\n\n"
        "Status: `CLOSED_WITH_SINGLE_MAINTAINER_EXCEPTION`"
    )
    assert "Last attested snapshot status: `CLOSED_WITH_SINGLE_MAINTAINER_EXCEPTION`" in closure
    assert (
        "The unqualified states `independently_reviewed`, `owner_approved`, and `CLOSED` are forbidden"
        in normalized
    )
    assert "`contract_owner_attestation`" in closure
    assert "`snapshot_closure_attestation`" in closure
    assert "mutable PR prose or an ordinary comment is insufficient" in closure
    assert "Any subject-file change invalidates that attestation for the changed bytes" in normalized
    assert "returns the new package to `NOT_CLOSED`" in normalized
    assert "later carrier-only update may reference the second immutable event" in normalized


def test_contract_owner_attestation_binds_complete_exception_evidence() -> None:
    attestation = owner_attestation()
    event = attestation["event"]
    assert isinstance(event, dict)

    required_fields = {
        "schema_version",
        "event_id",
        "exception_id",
        "decision_kind",
        "occurred_at",
        "actor_id",
        "actor_role",
        "actor_type",
        "repository",
        "baseline_sha",
        "subject_kind",
        "subject_id",
        "subject_commit_sha",
        "contract_path",
        "contract_sha256",
        "snapshot_id",
        "decision",
        "eligibility_reason",
        "shared_actor_disclosure",
        "separation_waiver_scope",
        "ci_evidence",
        "local_validation_evidence",
        "finding_disposition",
        "residual_risk_acceptance",
        "authority_boundary",
        "evidence_ref",
        "evidence_sha256",
        "previous_event_hash",
    }
    assert set(event) == required_fields
    assert all(value not in (None, "", "pending", "PENDING") for value in event.values())
    assert event["decision_kind"] == "contract_owner_attestation"
    assert event["decision"] == "owner_approved_with_exception"
    assert event["subject_commit_sha"] == SUBJECT_COMMIT_SHA
    assert event["contract_sha256"] == CONTRACT_SHA256
    assert event["subject_id"] == CONTRACT_SHA256
    assert event["evidence_sha256"] == CONTRACT_SHA256
    assert event["snapshot_id"] == "not_applicable_for_contract_owner_attestation"
    assert event["previous_event_hash"] == "GENESIS"
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", event["occurred_at"])

    ci = event["ci_evidence"]
    assert ci["workflow_run_id"] == 31313816548
    assert ci["workflow_run_number"] == 66
    assert ci["head_sha"] == SUBJECT_COMMIT_SHA
    assert ci["status"] == "completed"
    assert ci["conclusion"] == "success"
    assert {job["python_version"] for job in ci["matrix_jobs"]} == {"3.10", "3.12"}
    assert all(job["conclusion"] == "success" for job in ci["matrix_jobs"])


def test_contract_owner_attestation_event_hash_recomputes() -> None:
    attestation = owner_attestation()
    canonical = json.dumps(
        attestation["event"], sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    assert HASH_RE.fullmatch(attestation["event_hash"])
    assert hashlib.sha256(canonical).hexdigest() == attestation["event_hash"]


def test_published_attestation_advances_only_contract_state() -> None:
    attestation_text = OWNER_ATTESTATION.read_text(encoding="utf-8")
    approval = APPROVAL.read_text(encoding="utf-8")
    closure = closure_text()

    assert "Artifact state: `local_candidate_not_yet_immutable`" in attestation_text
    assert "This local file is not yet an immutable public attestation" in attestation_text
    assert "Status: `owner_approved_with_exception`" in approval
    assert ATTESTATION_COMMIT_SHA in approval
    assert sha256(OWNER_ATTESTATION) == ATTESTATION_SHA256
    assert "Historical snapshot status: `CLOSED_WITH_SINGLE_MAINTAINER_EXCEPTION`" in closure
    assert SNAPSHOT_ATTESTATION_COMMIT_SHA in closure
    assert "CLOSED_WITH_SINGLE_MAINTAINER_EXCEPTION` claim" in attestation_text


def test_approval_record_references_exact_immutable_attestation_objects() -> None:
    approval = APPROVAL.read_text(encoding="utf-8")
    normalized = " ".join(approval.split())

    assert ATTESTATION_COMMIT_SHA in approval
    assert ATTESTATION_BLOB_SHA in approval
    assert ATTESTATION_SHA256 in approval
    assert ATTESTATION_EVENT_HASH in approval
    assert (
        f"blob/{ATTESTATION_COMMIT_SHA}/docs/milestones/M9-I2-contract-owner-attestation.md"
        in normalized
    )
    assert "never `independently_reviewed` or unqualified `owner_approved`" in normalized


def test_second_stage_immutable_objects_close_only_exact_snapshot() -> None:
    approval = " ".join(APPROVAL.read_text(encoding="utf-8").split())
    closure = " ".join(closure_text().split())

    assert "This record update creates a new subject snapshot" in approval
    assert "snapshot_closure_attestation" in approval
    assert "package closure remains `NOT_CLOSED`" in approval
    assert SNAPSHOT_ATTESTATION_COMMIT_SHA in closure
    assert SNAPSHOT_ATTESTATION_BLOB_SHA in closure
    assert SNAPSHOT_ATTESTATION_SHA256 in closure
    assert SNAPSHOT_ATTESTATION_EVENT_HASH in closure
    assert f"blob/{SNAPSHOT_ATTESTATION_COMMIT_SHA}/docs/milestones/M9-I2-snapshot-closure-attestation.md" in closure
    assert "historical package remains `CLOSED_WITH_SINGLE_MAINTAINER_EXCEPTION`" in closure
    assert "or authorize publication, implementation" in closure


def test_snapshot_closure_attestation_binds_exact_subject_and_ci() -> None:
    attestation = snapshot_attestation()
    event = attestation["event"]
    assert isinstance(event, dict)

    assert event["decision_kind"] == "snapshot_closure_attestation"
    assert event["decision"] == "CLOSED_WITH_SINGLE_MAINTAINER_EXCEPTION"
    assert event["subject_kind"] == "exact_snapshot"
    assert event["subject_id"] == HISTORICAL_SNAPSHOT_ID
    assert event["snapshot_id"] == HISTORICAL_SNAPSHOT_ID
    assert event["subject_commit_sha"] == SNAPSHOT_COMMIT_SHA
    assert event["contract_sha256"] == CONTRACT_SHA256
    assert event["evidence_sha256"] == SNAPSHOT_CARRIER_SHA256
    assert event["previous_event_hash"] == ATTESTATION_EVENT_HASH
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", event["occurred_at"])

    ci = event["ci_evidence"]
    assert ci["workflow_run_id"] == 31315947577
    assert ci["workflow_run_number"] == 68
    assert ci["head_sha"] == SNAPSHOT_COMMIT_SHA
    assert ci["status"] == "completed"
    assert ci["conclusion"] == "success"
    assert {job["python_version"] for job in ci["matrix_jobs"]} == {"3.10", "3.12"}
    assert all(job["conclusion"] == "success" for job in ci["matrix_jobs"])
    assert all(job["full_suite"] == "339 passed" for job in ci["matrix_jobs"])

    text = SNAPSHOT_ATTESTATION.read_text(encoding="utf-8")
    assert "Artifact state: `local_candidate_not_yet_immutable`" in text
    assert "authoritative package state remains `NOT_CLOSED`" in text
    assert "It does not authorize implementation" in " ".join(text.split())


def test_snapshot_closure_attestation_event_hash_recomputes() -> None:
    attestation = snapshot_attestation()
    canonical = json.dumps(
        attestation["event"], sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    assert HASH_RE.fullmatch(attestation["event_hash"])
    assert hashlib.sha256(canonical).hexdigest() == attestation["event_hash"]


def test_snapshot_attestation_immutable_bytes_and_validation_run_are_bound() -> None:
    closure = " ".join(closure_text().split())

    assert sha256(SNAPSHOT_ATTESTATION) == SNAPSHOT_ATTESTATION_SHA256
    assert snapshot_attestation()["event_hash"] == SNAPSHOT_ATTESTATION_EVENT_HASH
    assert "Validate` run #69" in closure
    assert "31316921540" in closure
    assert "93253567690" in closure
    assert "93253567722" in closure
    assert "each passed all validation and repository-policy steps and 341 tests" in closure


def test_current_snapshot_attestation_binds_main_ci_review_and_resolved_finding() -> None:
    attestation = current_snapshot_attestation()
    event = attestation["event"]
    assert isinstance(event, dict)

    required_fields = {
        "schema_version",
        "event_id",
        "exception_id",
        "decision_kind",
        "occurred_at",
        "actor_id",
        "actor_role",
        "actor_type",
        "repository",
        "baseline_sha",
        "subject_kind",
        "subject_id",
        "subject_commit_sha",
        "contract_path",
        "contract_sha256",
        "snapshot_id",
        "decision",
        "eligibility_reason",
        "shared_actor_disclosure",
        "separation_waiver_scope",
        "ci_evidence",
        "local_validation_evidence",
        "review_evidence",
        "finding_disposition",
        "residual_risk_acceptance",
        "authority_boundary",
        "evidence_ref",
        "evidence_sha256",
        "previous_event_hash",
    }
    assert set(event) == required_fields
    assert all(value not in (None, "", "pending", "PENDING") for value in event.values())
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", event["occurred_at"])

    assert event["decision_kind"] == "snapshot_closure_attestation"
    assert event["decision"] == "CLOSED_WITH_SINGLE_MAINTAINER_EXCEPTION"
    assert event["subject_kind"] == "exact_snapshot"
    assert event["subject_id"] == CURRENT_SNAPSHOT_ID
    assert event["snapshot_id"] == CURRENT_SNAPSHOT_ID
    assert event["subject_commit_sha"] == CURRENT_MAIN_SUBJECT_COMMIT_SHA
    assert event["contract_sha256"] == CONTRACT_SHA256
    assert event["evidence_sha256"] == CURRENT_PRE_ATTESTATION_CARRIER_SHA256
    assert sha256(CLOSURE) != CURRENT_PRE_ATTESTATION_CARRIER_SHA256
    assert event["previous_event_hash"] == SNAPSHOT_ATTESTATION_EVENT_HASH

    ci = event["ci_evidence"]
    assert ci["workflow_run_id"] == 31519855793
    assert ci["workflow_run_number"] == 85
    assert ci["trigger"] == "push"
    assert ci["head_sha"] == CURRENT_MAIN_SUBJECT_COMMIT_SHA
    assert ci["status"] == "completed"
    assert ci["conclusion"] == "success"
    assert {job["python_version"] for job in ci["matrix_jobs"]} == {"3.10", "3.12"}
    assert all(job["conclusion"] == "success" for job in ci["matrix_jobs"])
    assert all(job["full_suite"] == "426 passed" for job in ci["matrix_jobs"])

    review = event["review_evidence"]
    assert review["pull_request_number"] == 27
    assert review["reviewed_head_sha"] == "ff0767f145867f08a4386d1d8e5d7342663fed7c"
    assert review["reviewed_tree_sha"] == CURRENT_MAIN_SUBJECT_TREE_SHA
    assert review["main_subject_tree_sha"] == CURRENT_MAIN_SUBJECT_TREE_SHA
    assert review["review_id"] == 4909174183
    assert review["review_node_id"] == "PRR_kwDOTqKoFc8AAAABJJwNpw"
    assert review["disposition"] == "COMMENTED_PASS"
    assert review["finding_thread_id"] == "PRRT_kwDOTqKoFc6YUcz-"
    assert review["finding_comment_id"] == "PRRC_kwDOTqKoFc7gIYkI"
    assert review["finding_resolution"] == "resolved"


def test_current_snapshot_attestation_event_hash_recomputes_and_chains() -> None:
    attestation = current_snapshot_attestation()
    canonical = json.dumps(
        attestation["event"], sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    assert HASH_RE.fullmatch(attestation["event_hash"])
    assert hashlib.sha256(canonical).hexdigest() == attestation["event_hash"]
    assert (
        attestation["event"]["previous_event_hash"]
        == snapshot_attestation()["event_hash"]
    )


def test_current_snapshot_attestation_preserves_narrow_authority_after_publication() -> None:
    text = CURRENT_SNAPSHOT_ATTESTATION.read_text(encoding="utf-8")
    normalized = " ".join(text.split())

    assert "Artifact state: `local_candidate_not_yet_immutable`" in text
    assert "Current snapshot state before immutable publication: `NOT_CLOSED`" in text
    assert "This local file is not yet an immutable public attestation" in text
    assert "Its existence does not close the current snapshot" in normalized
    assert "later carrier-only transition requires separate authorization" in normalized
    assert "shared_actor_disclosure" in text
    assert "residual_risk_acceptance" in text
    assert "authority_boundary" in text
    assert "this event is not independent review" in normalized
    assert "does not authorize staging, committing, pushing, PR creation or state changes" in normalized
    assert "live or provider access" in normalized
    assert "real-company data" in normalized
    assert "attachment use" in normalized
    assert closure_text().startswith(
        "# M9-I2 Post-Owner-Approval Exact-Snapshot Closure\n\n"
        "Status: `CLOSED_WITH_SINGLE_MAINTAINER_EXCEPTION`"
    )


def test_current_attestation_immutable_object_and_main_ci_are_bound() -> None:
    closure = " ".join(closure_text().split())

    assert sha256(CURRENT_SNAPSHOT_ATTESTATION) == CURRENT_ATTESTATION_SHA256
    assert current_snapshot_attestation()["event_hash"] == CURRENT_ATTESTATION_EVENT_HASH
    assert CURRENT_ATTESTATION_COMMIT_SHA in closure
    assert CURRENT_ATTESTATION_BLOB_SHA in closure
    assert CURRENT_ATTESTATION_SHA256 in closure
    assert CURRENT_ATTESTATION_EVENT_HASH in closure
    assert (
        f"blob/{CURRENT_ATTESTATION_COMMIT_SHA}/docs/milestones/"
        "M9-I2-current-snapshot-closure-attestation.md"
    ) in closure
    assert "Validate run [#87]" in closure
    assert CURRENT_ATTESTATION_CI_RUN_ID in closure
    assert "93887825384" in closure
    assert "93887825359" in closure
    assert "each passed all 10 validation and repository-policy steps and 429 tests" in closure


def test_current_reclosure_is_hash_bound_and_closes_only_the_attested_snapshot() -> None:
    closure = closure_text()
    normalized = " ".join(closure.split())

    assert "Carrier update state: `immutable_m9_i4_status_attestation_verified`" in closure
    assert "Last attested snapshot status: `CLOSED_WITH_SINGLE_MAINTAINER_EXCEPTION`" in closure
    manifest = {relative_path: digest for digest, relative_path in manifest_entries(closure)}
    for relative_path in (
        "docs/milestones/M9-I2-issuer-resolution-contract-lock.md",
        "docs/milestones/M9-I2-contract-lock-review-approval-record.md",
    ):
        assert sha256(ROOT / relative_path) == manifest[relative_path]
    for relative_path in STATUS_SUMMARY_PATHS:
        assert sha256(ROOT / relative_path) != manifest[relative_path]
    assert snapshot_attestation()["event"]["subject_commit_sha"] == SNAPSHOT_COMMIT_SHA
    assert snapshot_attestation()["event"]["snapshot_id"] == HISTORICAL_SNAPSHOT_ID
    assert CURRENT_SNAPSHOT_ID != HISTORICAL_SNAPSHOT_ID
    assert "f571c1426181107d50f84e59fed051fb11c9c94e" in closure
    assert "Validate run\n[#83]" in closure
    assert "31518237790" in closure
    assert "formal re-review returned `COMMENTED_PASS`" in closure
    assert CURRENT_ATTESTATION_COMMIT_SHA in closure
    assert "records the current snapshot as `CLOSED_WITH_SINGLE_MAINTAINER_EXCEPTION`" in normalized
    assert "All six selected-path steps are satisfied for the exact current snapshot" in normalized
    assert "any subject-file change starts a new snapshot lineage" in normalized
    assert "grants no additional runtime, data, provider, publication, release" in normalized
    summaries = " ".join(
        (ROOT / relative_path).read_text(encoding="utf-8")
        for relative_path in STATUS_SUMMARY_PATHS
    )
    assert "eb726009ac6afeebd5b15618ff03796c73790175f6360a3823f7c411dafde705" in summaries
    assert "distinct current snapshot" in summaries
    assert "`NOT_CLOSED`" in summaries


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


def test_m9_i4_status_manifest_matches_exact_main_subject_bytes() -> None:
    closure = closure_text()
    entries = m9_i4_status_manifest_entries(closure)
    expected_paths = [
        "docs/milestones/M9-I2-issuer-resolution-contract-lock.md",
        "docs/milestones/M9-I2-contract-lock-review-approval-record.md",
        "PROJECT_STATUS.md",
        "ROADMAP.md",
        "README.md",
    ]
    assert [path for _, path in entries] == expected_paths
    assert all(sha256(ROOT / path) == digest for digest, path in entries)
    snapshot_id = hashlib.sha256(
        m9_i4_status_manifest_block(closure).encode("utf-8")
    ).hexdigest()
    assert snapshot_id == M9_I4_STATUS_SNAPSHOT_ID
    assert (
        "M9-I4 implementation status subject snapshot ID:\n"
        f"`{M9_I4_STATUS_SNAPSHOT_ID}`"
    ) in closure


def test_m9_i4_status_attestation_recomputes_and_extends_event_chain() -> None:
    attestation = m9_i4_status_snapshot_attestation()
    event = attestation["event"]
    assert isinstance(event, dict)
    canonical = json.dumps(
        event, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    assert attestation["event_hash"] == M9_I4_STATUS_ATTESTATION_EVENT_HASH
    assert hashlib.sha256(canonical).hexdigest() == M9_I4_STATUS_ATTESTATION_EVENT_HASH
    assert event["previous_event_hash"] == CURRENT_ATTESTATION_EVENT_HASH
    assert event["subject_id"] == M9_I4_STATUS_SNAPSHOT_ID
    assert event["snapshot_id"] == M9_I4_STATUS_SNAPSHOT_ID
    assert event["subject_commit_sha"] == M9_I4_STATUS_SUBJECT_COMMIT_SHA
    assert event["evidence_sha256"] == M9_I4_PRE_ATTESTATION_CARRIER_SHA256
    assert sha256(CLOSURE) != M9_I4_PRE_ATTESTATION_CARRIER_SHA256


def test_m9_i4_status_attestation_binds_exact_ci_review_and_tree_identity() -> None:
    event = m9_i4_status_snapshot_attestation()["event"]
    ci = event["ci_evidence"]
    assert ci["workflow_run_id"] == 31702191834
    assert ci["workflow_run_number"] == 98
    assert ci["trigger"] == "push"
    assert ci["head_sha"] == M9_I4_STATUS_SUBJECT_COMMIT_SHA
    assert ci["status"] == "completed"
    assert ci["conclusion"] == "success"
    assert {job["python_version"] for job in ci["matrix_jobs"]} == {"3.10", "3.12"}
    assert {job["job_id"] for job in ci["matrix_jobs"]} == {94453784919, 94453784987}
    assert all(job["conclusion"] == "success" for job in ci["matrix_jobs"])
    assert all(job["full_suite"] == "505 passed" for job in ci["matrix_jobs"])

    review = event["review_evidence"]
    assert review["pull_request_number"] == 33
    assert review["reviewed_head_sha"] == "51b2b946a8c20a78ac7a6a1ff9f230f2acfe568e"
    assert review["reviewed_tree_sha"] == M9_I4_STATUS_SUBJECT_TREE_SHA
    assert review["main_subject_tree_sha"] == M9_I4_STATUS_SUBJECT_TREE_SHA
    assert review["review_id"] == 4927207917
    assert review["review_node_id"] == "PRR_kwDOTqKoFc8AAAABJa857Q"
    assert review["disposition"] == "COMMENTED_PASS"
    assert review["finding_resolution"] == "no_findings"


def test_m9_i4_status_attestation_candidate_remains_fail_closed_and_narrow() -> None:
    text = M9_I4_STATUS_SNAPSHOT_ATTESTATION.read_text(encoding="utf-8")
    normalized = " ".join(text.split())
    closure = closure_text()
    assert "Artifact state: `local_candidate_not_yet_immutable`" in text
    assert "Current snapshot state before immutable publication: `NOT_CLOSED`" in text
    assert "This local file is not yet an immutable public attestation" in text
    assert "Its existence does not close the current snapshot" in normalized
    assert "Each later state transition requires separate authorization" in normalized
    assert "this event is not independent review" in normalized
    assert "does not authorize staging, committing, pushing, PR creation or state changes" in normalized
    assert "network/provider activation" in normalized
    assert "real-company data" in normalized
    assert "M9-I5 through M9-I6" in normalized
    assert closure.startswith(
        "# M9-I2 Post-Owner-Approval Exact-Snapshot Closure\n\n"
        "Status: `CLOSED_WITH_SINGLE_MAINTAINER_EXCEPTION`"
    )
    assert "All six selected-path steps are satisfied" in closure
    assert HISTORICAL_SNAPSHOT_ID in closure
    assert CURRENT_SNAPSHOT_ID in closure


def test_m9_i4_status_immutable_attestation_object_and_main_ci_are_bound() -> None:
    closure = closure_text()
    normalized = " ".join(closure.split())
    assert sha256(M9_I4_STATUS_SNAPSHOT_ATTESTATION) == M9_I4_STATUS_ATTESTATION_SHA256
    assert m9_i4_status_snapshot_attestation()["event_hash"] == M9_I4_STATUS_ATTESTATION_EVENT_HASH
    for required in (
        M9_I4_STATUS_ATTESTATION_COMMIT_SHA,
        M9_I4_STATUS_ATTESTATION_TREE_SHA,
        M9_I4_STATUS_ATTESTATION_BLOB_SHA,
        M9_I4_STATUS_ATTESTATION_SHA256,
        M9_I4_STATUS_ATTESTATION_EVENT_HASH,
        M9_I4_STATUS_ATTESTATION_CI_RUN_ID,
        "94462271822",
        "94462271743",
        "4927430704",
    ):
        assert required in closure
    assert (
        f"blob/{M9_I4_STATUS_ATTESTATION_COMMIT_SHA}/docs/milestones/"
        "M9-I4-status-snapshot-closure-attestation.md"
    ) in closure
    assert "Main Validate #100" in closure
    assert "each passed every validation, repository-policy, and test step with 509 tests" in normalized


def test_m9_i4_status_carrier_transition_closes_only_exact_attested_snapshot() -> None:
    closure = closure_text()
    normalized = " ".join(closure.split())
    assert closure.startswith(
        "# M9-I2 Post-Owner-Approval Exact-Snapshot Closure\n\n"
        "Status: `CLOSED_WITH_SINGLE_MAINTAINER_EXCEPTION`"
    )
    assert "Carrier update state: `immutable_m9_i4_status_attestation_verified`" in closure
    assert f"Last attested snapshot status: `CLOSED_WITH_SINGLE_MAINTAINER_EXCEPTION` for exact snapshot\n`{M9_I4_STATUS_SNAPSHOT_ID}`" in closure
    assert "records the exact M9-I4 implementation status snapshot as `CLOSED_WITH_SINGLE_MAINTAINER_EXCEPTION`" in normalized
    assert "All six selected-path steps are satisfied for the exact M9-I4 implementation status snapshot" in normalized
    assert "without altering any subject or attestation byte" in normalized
    assert "authoritative closure record only after its own separately authorized publication" in normalized
    assert "grants no runtime, provider, data, publication, release" in normalized
    summaries = " ".join(
        (ROOT / relative_path).read_text(encoding="utf-8")
        for relative_path in STATUS_SUMMARY_PATHS
    )
    assert M9_I4_STATUS_SNAPSHOT_ID not in summaries
    assert "`NOT_CLOSED`" in summaries
