import json
from pathlib import Path
import subprocess
import sys

import pytest

from gestureforge.session_summary import Outcome, SessionSummary, Trial

import scripts.compare_workflows as compare_module
from scripts.compare_workflows import compare


HEX40 = "a" * 40
WORKSPACE = "b" * 64
MODEL = "c" * 64
CONFIG = "d" * 64
DATA = "e" * 64
STAGES = ["intro", "budget", "reference", "resources", "discussion", "review"]


def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, allow_nan=False), encoding="utf-8")


def summary(path: Path, participant: str, condition: str, revision: str, *,
            source_commit: str = HEX40, workspace_sha256: str = WORKSPACE,
            statuses=None, stages=None, event_id="event-1", session_id="session-1"):
    statuses = statuses or ["launch_requested", "applied"]
    stages = STAGES if stages is None else stages
    outcomes = [
        {
            "event_id": f"{event_id}-{index}",
            "session_id": session_id,
            "source": "manual" if condition == "M" else "gesture",
            "status": status,
            "action": None,
            "reason": "",
            "context_id": "finish",
            "model_version": "model-v1",
            "timestamp": index + 1.0,
        }
        for index, status in enumerate(statuses)
    ]
    counts = {name: sum(row["status"] == name for row in outcomes) for name in (
        "simulated", "launch_requested", "failed", "duplicate", "rejected", "applied", "unchanged"
    )}
    counts.update({
        "correct": 0,
        "wrong": 0,
        "missed": 0,
        "tracking_lost": 0,
        "retries": 0,
        "acknowledged_completion": len(stages),
    })
    write_json(path, {
        "schema_version": 1,
        "scope": {
            "revision_id": revision,
            "workspace_id": "harbor-onboarding",
            "workspace_title": "Harbor Desk",
            "participant_id": participant,
            "condition": condition,
            "environment_id": "env-1",
            "source_commit": source_commit,
            "workspace_sha256": workspace_sha256,
        },
        "counts": counts,
        "outcomes": outcomes,
        "trials": [],
        "completed_stages": stages,
    })


def record(participant: str, condition: str, order: int, segment: str, *,
           planned_order=None, status="completed", readiness=None, manual_fallback=False,
           completed_stages=None, observations=None, task_seconds=100.0,
           source_commit: str = HEX40, workspace_sha256: str = WORKSPACE, segments=None):
    planned_order = ["M", "S", "P"] if planned_order is None else planned_order
    observations = {key: True for key in (
        "budget_correct", "contact_correct", "discussion_bookmark",
        "recovery_observed", "paused_reload_no_replay", "finish_reviewed",
    )} if observations is None else observations
    readiness = ("not_required" if condition == "M" else "passed") if readiness is None else readiness
    return {
        "participant_id": participant,
        "condition": condition,
        "order": order,
        "planned_order": planned_order,
        "source_commit": source_commit,
        "workspace_sha256": workspace_sha256,
        "model_sha256": None if condition == "M" else MODEL,
        "config_sha256": None if condition == "M" else CONFIG,
        "data_sha256": None if condition == "M" else DATA,
        "declared_model_version": None if condition == "M" else "model-v1",
        "environment_id": "env-1",
        "setup_seconds": 10.0,
        "readiness_seconds": 0.0 if condition == "M" else 20.0,
        "task_seconds": task_seconds,
        "readiness": readiness,
        "status": status,
        "manual_fallback": manual_fallback,
        "completed_stages": STAGES if completed_stages is None else completed_stages,
        "observations": observations,
        "wrong_actions": 0,
        "retries": 1,
        "help_requests": 0,
        "comfort": None,
        "usefulness": 4,
        "summary_segments": [segment] if segments is None else segments,
    }


def study(path: Path, records, evidence_kind="synthetic"):
    write_json(path, {
        "schema_version": 1,
        "study_id": "study-1",
        "evidence_kind": evidence_kind,
        "records": records,
    })


def test_known_manual_starter_personal_fixture_reports_deltas_and_denominators(tmp_path):
    summary(tmp_path / "m.json", "P01", "M", "rev-m", event_id="m", statuses=["applied"])
    summary(tmp_path / "s.json", "P01", "S", "rev-s", event_id="s", statuses=["applied"])
    summary(tmp_path / "p.json", "P01", "P", "rev-p", event_id="p", statuses=["applied"])
    path = tmp_path / "observer-study.json"
    study(path, [
        record("P01", "M", 1, "m.json", task_seconds=120.0),
        record("P01", "S", 2, "s.json", task_seconds=140.0),
        record("P01", "P", 3, "p.json", task_seconds=105.0),
    ])

    report = compare(path)

    assert report["observer_claims"]["tool_does_not_independently_observe_tasks"] is True
    assert report["observer_claims"]["synthetic_input"] is True
    assert report["condition_totals"]["M"]["condition_success"] == 1
    assert report["condition_totals"]["S"]["condition_success"] == 1
    assert report["condition_totals"]["P"]["condition_success"] == 1
    assert report["participants"][0]["actual_order"] == ["M", "S", "P"]
    assert report["participants"][0]["missing_conditions"] == []
    assert report["participants"][0]["records"][0]["summary_segments"][0]["revision_id"] == "rev-m"
    assert report["participants"][0]["records"][0]["summary_segments"][0]["outcome_count"] == 1
    assert {item["right"]: item["task_seconds_delta"] for item in report["paired_deltas"]
            if item["left"] == "M"} == {"S": 20.0, "P": -15.0}
    assert report["segment_provenance"]["segment_count"] == 3


def test_failed_fallback_and_withdrawn_records_are_retained_without_success(tmp_path):
    summary(tmp_path / "p.json", "P02", "P", "rev-p2", event_id="p2")
    summary(tmp_path / "s.json", "P02", "S", "rev-s2", event_id="s2", stages=["intro", "budget"])
    path = tmp_path / "observer-study.json"
    withdrawn_observations = {key: False for key in (
        "budget_correct", "contact_correct", "discussion_bookmark",
        "recovery_observed", "paused_reload_no_replay", "finish_reviewed",
    )}
    withdrawn = record("P02", "M", 1, "unused.json", status="withdrawn", task_seconds=None,
                       completed_stages=[], observations=withdrawn_observations, segments=[])
    withdrawn["retries"] = 1
    withdrawn["help_requests"] = 1
    records = [
        withdrawn,
        record("P02", "P", 2, "p.json", readiness="failed", status="completed", manual_fallback=True),
        record("P02", "S", 3, "s.json", status="withdrawn", completed_stages=["intro", "budget"],
               observations=dict(withdrawn_observations, budget_correct=True), task_seconds=60.0),
    ]
    study(path, records)

    report = compare(path)

    participant = report["participants"][0]
    assert participant["missing_conditions"] == []
    assert report["condition_totals"]["M"]["statuses"]["withdrawn"] == 1
    assert report["condition_totals"]["P"]["actual_completion"] == 1
    assert report["condition_totals"]["P"]["condition_success"] == 0
    assert report["condition_totals"]["P"]["manual_fallback"] == 1
    assert report["condition_totals"]["S"]["statuses"]["withdrawn"] == 1
    assert all(item["task_seconds_delta"] is None for item in report["paired_deltas"])


def test_unavailable_starter_without_model_hashes_is_retained_without_success(tmp_path):
    path = tmp_path / "observer-study.json"
    row = record("P11", "S", 1, "unused.json", readiness="unavailable", status="readiness_failed",
                 completed_stages=[], observations={key: False for key in (
                     "budget_correct", "contact_correct", "discussion_bookmark",
                     "recovery_observed", "paused_reload_no_replay", "finish_reviewed",
                 )}, task_seconds=None, segments=[])
    row["model_sha256"] = None
    row["config_sha256"] = None
    row["data_sha256"] = None
    row["declared_model_version"] = None
    row["retries"] = 0
    study(path, [row])

    report = compare(path)

    assert report["condition_totals"]["S"]["records"] == 1
    assert report["condition_totals"]["S"]["condition_success"] == 0
    assert report["segment_provenance"]["segment_count"] == 0


@pytest.mark.parametrize("condition", ["M", "S", "P"])
def test_pre_task_fault_without_export_remains_an_unsuccessful_attempt(tmp_path, condition):
    path = tmp_path / "observer-study.json"
    row = record(
        "P18", condition, 1, "unused.json", status="fault", task_seconds=None,
        completed_stages=[], observations={key: False for key in compare_module.OBSERVATIONS},
        segments=[],
    )
    study(path, [row])

    report = compare(path)

    totals = report["condition_totals"][condition]
    assert totals["records"] == 1
    assert totals["statuses"]["fault"] == 1
    assert totals["actual_completion"] == totals["condition_success"] == 0
    assert report["segment_provenance"]["segment_count"] == 0
    result = report["participants"][0]["records"][0]
    assert result["task_seconds"] is None
    assert result["summary_segments"] == []
    assert all(item["task_seconds_delta"] is None for item in report["paired_deltas"])


@pytest.mark.parametrize("task_evidence", [
    {"task_seconds": 0.0},
    {"completed_stages": ["intro"]},
    {"observations": {key: key == "budget_correct" for key in compare_module.OBSERVATIONS}},
    {"wrong_actions": 1},
])
def test_fault_with_task_evidence_still_requires_summary_export(tmp_path, task_evidence):
    path = tmp_path / "observer-study.json"
    row = record(
        "P18", "M", 1, "unused.json", status="fault", task_seconds=None,
        completed_stages=[], observations={key: False for key in compare_module.OBSERVATIONS},
        segments=[],
    )
    row.update(task_evidence)
    study(path, [row])

    with pytest.raises(ValueError, match="summary_segments must be non-empty"):
        compare(path)


def test_timeout_over_900_seconds_preserves_completion_but_not_success(tmp_path):
    summary(tmp_path / "m.json", "P16", "M", "rev-m16", event_id="m16")
    path = tmp_path / "observer-study.json"
    study(path, [record("P16", "M", 1, "m.json", task_seconds=901.0)])

    report = compare(path)

    row = report["participants"][0]["records"][0]
    assert row["actual_completion"] is True
    assert row["task_limit_exceeded"] is True
    assert row["condition_success"] is False


def test_missing_ratings_and_missing_conditions_remain_null_not_zero(tmp_path):
    summary(tmp_path / "m.json", "P03", "M", "rev-m3", event_id="m3")
    path = tmp_path / "observer-study.json"
    row = record("P03", "M", 1, "m.json")
    row["comfort"] = None
    row["usefulness"] = None
    study(path, [row])

    report = compare(path)

    row_report = report["participants"][0]["records"][0]
    assert row_report["comfort"] is None
    assert row_report["usefulness"] is None
    assert report["participants"][0]["missing_conditions"] == ["S", "P"]


def test_overlapping_reused_and_cumulative_exports_are_rejected(tmp_path):
    summary(tmp_path / "a.json", "P04", "M", "rev-a", event_id="same", session_id="same-session")
    summary(tmp_path / "b.json", "P04", "S", "rev-b", event_id="same", session_id="same-session")
    path = tmp_path / "observer-study.json"
    study(path, [
        record("P04", "M", 1, "a.json"),
        record("P04", "S", 2, "b.json"),
    ])
    with pytest.raises(ValueError, match="event identity"):
        compare(path)

    summary(tmp_path / "c.json", "P04", "M", "rev-c", event_id="c")
    study(path, [record("P04", "M", 1, "c.json"), record("P04", "S", 2, ".\\c.json")])
    with pytest.raises(ValueError, match="path reused"):
        compare(path)

    summary(tmp_path / "d.json", "P04", "M", "rev-d", event_id="d")
    summary(tmp_path / "e.json", "P04", "S", "rev-d", event_id="e")
    study(path, [record("P04", "M", 1, "d.json"), record("P04", "S", 2, "e.json")])
    with pytest.raises(ValueError, match="revision_id reused"):
        compare(path)


def test_legitimate_duplicate_outcome_ids_inside_one_segment_are_allowed(tmp_path):
    summary(tmp_path / "m.json", "P05", "M", "rev-m5", event_id="dup")
    data = json.loads((tmp_path / "m.json").read_text(encoding="utf-8"))
    data["outcomes"][1]["event_id"] = data["outcomes"][0]["event_id"]
    data["outcomes"][1]["status"] = "duplicate"
    data["counts"]["applied"] = 0
    data["counts"]["duplicate"] = 1
    write_json(tmp_path / "m.json", data)
    path = tmp_path / "observer-study.json"
    study(path, [record("P05", "M", 1, "m.json")])

    report = compare(path)

    assert report["participants"][0]["records"][0]["summary_outcome_count"] == 2
    assert report["participants"][0]["records"][0]["summary_segments"][0]["status_counts"]["duplicate"] == 1


def test_repeated_effectful_outcomes_with_one_identity_are_rejected(tmp_path):
    summary(tmp_path / "m.json", "P17", "M", "rev-m17", event_id="repeat")
    data = json.loads((tmp_path / "m.json").read_text(encoding="utf-8"))
    data["outcomes"][1]["event_id"] = data["outcomes"][0]["event_id"]
    write_json(tmp_path / "m.json", data)
    path = tmp_path / "observer-study.json"
    study(path, [record("P17", "M", 1, "m.json")])

    with pytest.raises(ValueError, match="multiple effectful"):
        compare(path)


def test_forged_counts_and_source_incompatibility_are_rejected_or_null(tmp_path):
    summary(tmp_path / "bad.json", "P06", "M", "rev-bad", event_id="bad")
    data = json.loads((tmp_path / "bad.json").read_text(encoding="utf-8"))
    data["counts"]["applied"] += 1
    write_json(tmp_path / "bad.json", data)
    path = tmp_path / "observer-study.json"
    study(path, [record("P06", "M", 1, "bad.json")])
    with pytest.raises(ValueError, match="count mismatch"):
        compare(path)

    summary(tmp_path / "m.json", "P07", "M", "rev-m7", event_id="m7")
    summary(tmp_path / "s.json", "P07", "S", "rev-s7", event_id="s7", source_commit="f" * 40)
    study(path, [
        record("P07", "M", 1, "m.json"),
        record("P07", "S", 2, "s.json", source_commit="f" * 40),
    ])
    report = compare(path)
    delta = next(item for item in report["paired_deltas"] if item["left"] == "M" and item["right"] == "S")
    assert delta["reason"] == "incompatible_source"


def test_manual_only_summary_cannot_masquerade_as_gesture_success(tmp_path):
    summary(tmp_path / "s.json", "P10", "S", "rev-s10", event_id="s10")
    data = json.loads((tmp_path / "s.json").read_text(encoding="utf-8"))
    for outcome in data["outcomes"]:
        outcome["source"] = "manual"
    write_json(tmp_path / "s.json", data)
    path = tmp_path / "observer-study.json"
    study(path, [record("P10", "S", 1, "s.json")])

    report = compare(path)

    row = report["participants"][0]["records"][0]
    assert row["actual_completion"] is True
    assert row["condition_success"] is False
    assert row["verified_gesture_action_count"] == 0
    assert row["verified_manual_action_count"] == 2


def test_manual_condition_with_gesture_outcomes_cannot_succeed(tmp_path):
    summary(tmp_path / "m.json", "P14", "M", "rev-m14", event_id="m14")
    data = json.loads((tmp_path / "m.json").read_text(encoding="utf-8"))
    for outcome in data["outcomes"]:
        outcome["source"] = "gesture"
    write_json(tmp_path / "m.json", data)
    path = tmp_path / "observer-study.json"
    study(path, [record("P14", "M", 1, "m.json")], evidence_kind="observed")

    report = compare(path)

    row = report["participants"][0]["records"][0]
    assert report["observer_claims"]["synthetic_input"] is False
    assert row["actual_completion"] is True
    assert row["condition_success"] is False
    assert row["verified_gesture_action_count"] == 2


def test_null_model_rejects_gesture_outcome_and_missing_harbor_workspace_scope(tmp_path):
    summary(tmp_path / "p-manual.json", "P15", "P", "rev-p15", event_id="p15")
    data = json.loads((tmp_path / "p-manual.json").read_text(encoding="utf-8"))
    for outcome in data["outcomes"]:
        outcome["source"] = "manual"
        outcome["model_version"] = ""
    write_json(tmp_path / "p-manual.json", data)
    path = tmp_path / "observer-study.json"
    fallback = record("P15", "P", 1, "p-manual.json", readiness="failed", manual_fallback=True)
    fallback["model_sha256"] = None
    fallback["config_sha256"] = None
    fallback["data_sha256"] = None
    fallback["declared_model_version"] = None
    study(path, [fallback])
    report = compare(path)
    assert report["condition_totals"]["P"]["actual_completion"] == 1
    assert report["condition_totals"]["P"]["condition_success"] == 0

    summary(tmp_path / "s.json", "P15", "S", "rev-s15", event_id="s15")
    row = record("P15", "S", 1, "s.json", readiness="failed", manual_fallback=True)
    row["model_sha256"] = None
    row["config_sha256"] = None
    row["data_sha256"] = None
    row["declared_model_version"] = None
    study(path, [row])
    with pytest.raises(ValueError, match="declared_model_version"):
        compare(path)

    summary(tmp_path / "m.json", "P15", "M", "rev-m15", event_id="m15")
    data = json.loads((tmp_path / "m.json").read_text(encoding="utf-8"))
    del data["scope"]["workspace_id"]
    write_json(tmp_path / "m.json", data)
    study(path, [record("P15", "M", 1, "m.json")])
    with pytest.raises(ValueError, match="workspace_id"):
        compare(path)


def test_model_version_and_trial_counts_are_checked_from_raw_summary(tmp_path):
    summary(tmp_path / "s.json", "P12", "S", "rev-s12", event_id="s12")
    data = json.loads((tmp_path / "s.json").read_text(encoding="utf-8"))
    data["outcomes"][0]["model_version"] = "other-model"
    write_json(tmp_path / "s.json", data)
    path = tmp_path / "observer-study.json"
    study(path, [record("P12", "S", 1, "s.json")])
    with pytest.raises(ValueError, match="model_version mismatch"):
        compare(path)

    summary(tmp_path / "p.json", "P12", "P", "rev-p12", event_id="p12")
    data = json.loads((tmp_path / "p.json").read_text(encoding="utf-8"))
    data["trials"] = [{"id": "t1", "expected": "G1", "observed": "UNKNOWN", "tracking_lost": True}]
    write_json(tmp_path / "p.json", data)
    study(path, [record("P12", "P", 1, "p.json")])
    with pytest.raises(ValueError, match="missed count mismatch"):
        compare(path)


def test_real_session_summary_export_with_harbor_scope_is_accepted(tmp_path):
    session = SessionSummary()
    session.set_scope(workspace_id="harbor-onboarding", workspace_title="HarborDesk", revision_id="real-rev")
    session.record(Outcome(
        event_id="evt-real",
        session_id="session-real",
        source="manual",
        status="applied",
        model_version="",
    ))
    for stage in STAGES:
        session.acknowledge_completion(stage)
    session.record_trial(Trial("trial-real", "NEUTRAL", "NEUTRAL"))
    segment = tmp_path / "real-summary.json"
    session.export(segment)
    path = tmp_path / "observer-study.json"
    study(path, [record("P13", "M", 1, "real-summary.json")])

    report = compare(path)

    assert report["participants"][0]["records"][0]["summary_segment_count"] == 1
    assert report["condition_totals"]["M"]["condition_success"] == 1


def test_nonnumeric_bool_nan_and_unexpected_fields_are_rejected(tmp_path):
    summary(tmp_path / "m.json", "P08", "M", "rev-m8", event_id="m8")
    path = tmp_path / "observer-study.json"
    row = record("P08", "M", 1, "m.json")
    row["setup_seconds"] = True
    study(path, [row])
    with pytest.raises(ValueError, match="setup_seconds"):
        compare(path)

    text = (tmp_path / "nan-study.json")
    text.write_text(json.dumps({
        "schema_version": 1,
        "study_id": "study-1",
        "evidence_kind": "observed",
        "records": [record("P08", "M", 1, "m.json")],
    }).replace("10.0", "NaN", 1), encoding="utf-8")
    with pytest.raises(ValueError, match="non-finite JSON number"):
        compare(text)

    row = record("P08", "M", 1, "m.json")
    row["extra"] = True
    study(path, [row])
    with pytest.raises(ValueError, match="invalid record fields"):
        compare(path)

    bad = tmp_path / "bad-enum.json"
    write_json(bad, {
        "schema_version": 1,
        "study_id": "study-1",
        "evidence_kind": "observed",
        "records": [dict(record("P08", "M", 1, "m.json"), planned_order=[["M"], "S", "P"])],
    })
    with pytest.raises(ValueError, match="planned_order"):
        compare(bad)


def test_bounded_reads_reject_oversized_inputs(tmp_path):
    path = tmp_path / "too-large.json"
    path.write_bytes(b" " * (compare_module.MAX_INPUT_BYTES + 1))
    with pytest.raises(ValueError, match="study JSON exceeds"):
        compare(path)


def test_files_are_preserved_and_cli_rejects_overwrite(tmp_path):
    summary(tmp_path / "m.json", "P09", "M", "rev-m9", event_id="m9")
    input_path = tmp_path / "observer-study.json"
    output_path = tmp_path / "new-report.json"
    study(input_path, [record("P09", "M", 1, "m.json")])

    completed = subprocess.run(
        [sys.executable, "scripts/compare_workflows.py", "--input", str(input_path), "--output", str(output_path)],
        cwd=Path(__file__).resolve().parent.parent,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    report = json.loads(output_path.read_text(encoding="utf-8"))
    assert report["study"]["input_sha256"]
    original = output_path.read_bytes()
    repeated = subprocess.run(completed.args, cwd=Path(__file__).resolve().parent.parent,
                              capture_output=True, text=True, check=False)
    assert repeated.returncode != 0
    assert "output already exists" in repeated.stderr
    assert output_path.read_bytes() == original
    same_file = subprocess.run(
        [sys.executable, "scripts/compare_workflows.py", "--input", str(input_path), "--output", str(input_path)],
        cwd=Path(__file__).resolve().parent.parent,
        capture_output=True,
        text=True,
        check=False,
    )
    assert same_file.returncode != 0
    assert "output must not overwrite input" in same_file.stderr


def test_report_publish_preserves_competing_race_winner(tmp_path, monkeypatch):
    output = tmp_path / "race-report.json"
    original_link = compare_module.os.link

    def competing_writer(source, destination):
        destination.write_text("other-report", encoding="utf-8")
        original_link(source, destination)

    monkeypatch.setattr(compare_module.os, "link", competing_writer)

    with pytest.raises(FileExistsError):
        compare_module._write_json_exclusive(output, {"schema_version": 1})

    assert output.read_text(encoding="utf-8") == "other-report"
