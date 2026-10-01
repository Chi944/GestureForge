import json
from pathlib import Path
import subprocess
import sys

import pytest

from scripts.replay_controller import load_trace, replay


def trace(frames, holds=None):
    default_holds = [{"start": 0.45, "end": frames[-1]["timestamp"], "command": "NEXT"}]
    return {
        "schema_version": 1,
        "session_id": "saved-session",
        "profile_id": "P01",
        "model_version": "model-v1",
        "context_id": "stage-1",
        "bindings": {
            "NEXT": {"kind": "NEXT"},
            "BOOKMARK": {"kind": "BOOKMARK"},
        },
        "frames": frames,
        "expected_holds": default_holds if holds is None else holds,
    }


def frame(frame_id, timestamp, label, accepted=True, rejection_reason=""):
    row = {"frame_id": frame_id, "timestamp": timestamp, "label": label, "accepted": accepted}
    if rejection_reason:
        row["rejection_reason"] = rejection_reason
    return row


def test_camera_frame_zero_is_valid_but_unannotated_recordings_cannot_be_scored(tmp_path):
    path = tmp_path / "recorded.json"
    data = trace([frame(0, 100.0, "NEUTRAL")], [])
    data["annotation_complete"] = False
    path.write_text(json.dumps(data), encoding="utf-8")
    with pytest.raises(ValueError, match="Annotate expected_holds"):
        load_trace(path)
    data["annotation_complete"] = True
    path.write_text(json.dumps(data), encoding="utf-8")
    assert replay(load_trace(path))["input"]["frame_count"] == 1


def test_long_hold_duplicates_baseline_but_protected_routes_once(tmp_path):
    path = tmp_path / "trace.json"
    path.write_text(json.dumps(trace([
        frame(1, 0.00, "NEUTRAL"),
        frame(2, 0.15, "NEUTRAL"),
        frame(3, 0.31, "NEUTRAL"),
        frame(4, 0.45, "NEXT"),
        frame(5, 0.60, "NEXT"),
        frame(6, 0.75, "NEXT"),
        frame(7, 0.90, "NEXT"),
        frame(8, 1.05, "NEXT"),
        frame(9, 1.20, "NEXT"),
    ])), encoding="utf-8")

    result = replay(load_trace(path))

    assert result["input"]["frame_count"] == 9
    assert result["conditions"]["protected"]["actions"] == 1
    assert result["conditions"]["protected"]["correct"] == 1
    assert result["conditions"]["protected"]["duplicate"] == 0
    assert result["conditions"]["baseline"]["actions"] == 6
    assert result["conditions"]["baseline"]["correct"] == 1
    assert result["conditions"]["baseline"]["duplicate"] == 5


def test_neutral_rearm_allows_second_protected_action(tmp_path):
    path = tmp_path / "trace.json"
    path.write_text(json.dumps(trace([
        frame(1, 0.00, "NEUTRAL"),
        frame(2, 0.15, "NEUTRAL"),
        frame(3, 0.31, "NEUTRAL"),
        frame(4, 0.45, "NEXT"),
        frame(5, 0.60, "NEXT"),
        frame(6, 0.75, "NEXT"),
        frame(7, 0.90, "NEXT"),
        frame(8, 1.00, "NEUTRAL"),
        frame(9, 1.15, "NEUTRAL"),
        frame(10, 1.31, "NEUTRAL"),
        frame(11, 1.45, "NEXT"),
        frame(12, 1.60, "NEXT"),
        frame(13, 1.75, "NEXT"),
        frame(14, 1.90, "NEXT"),
    ], [
        {"start": 0.45, "end": 0.95, "command": "NEXT"},
        {"start": 1.45, "end": 1.90, "command": "NEXT"},
    ])), encoding="utf-8")

    result = replay(load_trace(path))

    assert result["conditions"]["protected"]["actions"] == 2
    assert result["conditions"]["protected"]["correct"] == 2
    assert result["conditions"]["protected"]["missed"] == 0


def test_unknown_tracking_loss_resets_candidate_and_blocks_short_hold(tmp_path):
    path = tmp_path / "trace.json"
    path.write_text(json.dumps(trace([
        frame(1, 0.00, "NEUTRAL"),
        frame(2, 0.15, "NEUTRAL"),
        frame(3, 0.31, "NEUTRAL"),
        frame(4, 0.45, "NEXT"),
        frame(5, 0.60, "UNKNOWN", False, "tracking lost"),
        frame(6, 0.75, "NEXT"),
        frame(7, 0.90, "NEXT"),
        frame(8, 1.05, "NEXT"),
    ])), encoding="utf-8")

    result = replay(load_trace(path))

    assert result["conditions"]["protected"]["actions"] == 0
    assert result["conditions"]["protected"]["missed"] == 1
    assert result["conditions"]["baseline"]["actions"] == 4
    assert result["conditions"]["baseline"]["duplicate"] == 3


def test_empty_annotations_and_wrong_commands_are_not_scored_as_correct(tmp_path):
    frames = [
        frame(1, 0.00, "NEUTRAL"),
        frame(2, 0.15, "NEUTRAL"),
        frame(3, 0.31, "NEUTRAL"),
        frame(4, 0.45, "BOOKMARK"),
        frame(5, 0.60, "BOOKMARK"),
        frame(6, 0.75, "BOOKMARK"),
        frame(7, 0.90, "BOOKMARK"),
    ]
    negative_path = tmp_path / "negative.json"
    negative_path.write_text(json.dumps(trace(frames, [])), encoding="utf-8")
    negative = replay(load_trace(negative_path))

    assert negative["conditions"]["protected"]["actions"] == 1
    assert negative["conditions"]["protected"]["unintended"] == 1
    assert negative["conditions"]["protected"]["missed"] == 0
    assert negative["conditions"]["protected"]["latency_p95_seconds"] is None

    wrong_path = tmp_path / "wrong.json"
    wrong_path.write_text(json.dumps(trace(
        frames, [{"start": 0.45, "end": 0.90, "command": "NEXT"}],
    )), encoding="utf-8")
    wrong = replay(load_trace(wrong_path))

    assert wrong["conditions"]["protected"]["actions"] == 1
    assert wrong["conditions"]["protected"]["correct"] == 0
    assert wrong["conditions"]["protected"]["missed"] == 1
    assert wrong["conditions"]["protected"]["unintended"] == 1
    assert wrong["conditions"]["protected"]["latency_p95_seconds"] is None


@pytest.mark.parametrize("patch", [
    {"expected_holds": [{"start": 1.0, "end": 0.9, "command": "NEXT"}]},
    {"expected_holds": [{"start": 0.0, "end": 1.0, "command": "PREVIOUS"}]},
    {"expected_holds": [
        {"start": 0.0, "end": 0.5, "command": "NEXT"},
        {"start": 0.5, "end": 1.0, "command": "NEXT"},
    ]},
    {"frames": [frame(1, 0.0, "NEUTRAL"), frame(1, 0.1, "NEUTRAL")]},
    {"frames": [frame(1, 0.0, "NEUTRAL"), frame(2, float("nan"), "NEUTRAL")]},
    {"frames": [frame(1, 0.0, "UNKNOWN", False)]},
])
def test_malformed_trace_errors_before_metrics(tmp_path, patch):
    data = trace([frame(1, 0.0, "NEUTRAL")])
    data.update(patch)
    path = tmp_path / "trace.json"
    path.write_text(json.dumps(data), encoding="utf-8")

    with pytest.raises(ValueError):
        load_trace(path)


def test_cli_writes_atomic_report_with_same_predictions_for_both_conditions(tmp_path):
    trace_path = tmp_path / "trace.json"
    output_path = tmp_path / "report.json"
    trace_path.write_text(json.dumps(trace([
        frame(1, 0.00, "NEUTRAL"),
        frame(2, 0.15, "NEUTRAL"),
        frame(3, 0.31, "NEUTRAL"),
        frame(4, 0.45, "NEXT"),
        frame(5, 0.60, "NEXT"),
        frame(6, 0.75, "NEXT"),
        frame(7, 0.90, "NEXT"),
    ])), encoding="utf-8")

    completed = subprocess.run(
        [sys.executable, "scripts/replay_controller.py", "--trace", str(trace_path), "--output", str(output_path)],
        capture_output=True,
        cwd=Path(__file__).resolve().parent.parent,
        text=True,
        check=False,
    )

    assert completed.returncode == 0, completed.stderr
    report = json.loads(output_path.read_text(encoding="utf-8"))
    assert report["input"]["frame_count"] == 7
    assert report["input"]["trace_sha256"]
    assert report["input"]["controller_timing_seconds"]["command_hold"] == 0.4
    assert report["conditions"]["protected"]["events"][0]["event_id"] == "protected:1"
    assert report["conditions"]["protected"]["events"][0]["frame_id"] == 7
    assert [event["frame_id"] for event in report["conditions"]["baseline"]["events"]] == [4, 5, 6, 7]
    original = output_path.read_bytes()
    repeated = subprocess.run(completed.args, capture_output=True, text=True,
                              cwd=Path(__file__).resolve().parent.parent, check=False)
    assert repeated.returncode != 0 and "output already exists" in repeated.stderr
    assert output_path.read_bytes() == original


def test_cli_rejects_overwriting_input(tmp_path):
    trace_path = tmp_path / "trace.json"
    trace_path.write_text(json.dumps(trace([frame(1, 0.00, "NEUTRAL")])), encoding="utf-8")

    completed = subprocess.run(
        [sys.executable, "scripts/replay_controller.py", "--trace", str(trace_path), "--output", str(trace_path)],
        capture_output=True,
        cwd=Path(__file__).resolve().parent.parent,
        text=True,
        check=False,
    )

    assert completed.returncode != 0
    assert "output must not overwrite input trace" in completed.stderr


def test_report_preserves_existing_evidence_and_cleans_up_if_destination_races(tmp_path, monkeypatch):
    import scripts.replay_controller as replay_module

    path = tmp_path / "report.json"
    path.write_text("keep-me", encoding="utf-8")
    with pytest.raises(ValueError, match="output already exists"):
        replay_module._write_json_atomic(path, {"new": True})
    assert path.read_text(encoding="utf-8") == "keep-me"

    output = tmp_path / "new-report.json"
    original_link = replay_module.os.link

    def competing_writer(source, destination):
        destination.write_text("other-evidence", encoding="utf-8")
        original_link(source, destination)

    monkeypatch.setattr(replay_module.os, "link", competing_writer)
    with pytest.raises(FileExistsError):
        replay_module._write_json_atomic(output, {"new": True})
    assert output.read_text(encoding="utf-8") == "other-evidence"
    assert {p.name for p in tmp_path.iterdir()} == {"report.json", "new-report.json"}
