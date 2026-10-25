import json
from typing import Any, cast

import pytest

from gestureforge.contracts import Action, ActionType, Prediction, RoutingMode, RoutingSnapshot
from gestureforge.traces import MAX_TRACE_FRAMES, EvaluationTrace


def snapshot() -> RoutingSnapshot:
    return RoutingSnapshot(
        "session-1",
        "P01",
        "model-v1",
        "stage-1",
        (("NEXT", Action(ActionType.NEXT)), ("LAUNCH_CAMERA", Action(ActionType.OPEN_SHORTCUT, "camera"))),
        RoutingMode.REHEARSAL,
    )


def prediction(frame_id=0, timestamp=10.0, label="NEUTRAL", *, accepted=True, reason="") -> Prediction:
    return Prediction("session-1", "P01", frame_id, timestamp, label, accepted, "model-v1", reason)


def test_save_round_trips_replay_schema_without_raw_capture_data(tmp_path):
    trace = EvaluationTrace(snapshot())
    trace.append(prediction(0, 10.0), 10.02)
    trace.append(prediction(1, 10.2, "UNKNOWN", accepted=False, reason="stale"), 10.25)

    path = tmp_path / "nested" / "trace.json"
    trace.save(path)
    saved = json.loads(path.read_text(encoding="utf-8"))

    assert trace.frame_count == 2
    assert saved["schema_version"] == 1
    assert saved["session_id"] == "session-1"
    assert saved["profile_id"] == "P01"
    assert saved["model_version"] == "model-v1"
    assert saved["context_id"] == "stage-1"
    assert saved["bindings"]["NEXT"] == {"kind": "NEXT", "shortcut_id": None}
    assert saved["bindings"]["LAUNCH_CAMERA"] == {"kind": "OPEN_SHORTCUT", "shortcut_id": "camera"}
    assert saved["frames"][0]["frame_id"] == 0
    assert saved["frames"][1]["rejection_reason"] == "stale"
    assert saved["expected_holds"] == []
    assert saved["annotation_complete"] is False
    assert "landmarks" not in json.dumps(saved)
    assert "features" not in json.dumps(saved)


def test_rejects_identity_timing_and_reason_errors():
    trace = EvaluationTrace(snapshot())

    with pytest.raises(ValueError, match="session"):
        trace.append(Prediction("other", "P01", 0, 10.0, "NEUTRAL", True, "model-v1"), 10.0)
    with pytest.raises(ValueError, match="profile"):
        trace.append(Prediction("session-1", "P02", 0, 10.0, "NEUTRAL", True, "model-v1"), 10.0)
    with pytest.raises(ValueError, match="model"):
        trace.append(Prediction("session-1", "P01", 0, 10.0, "NEUTRAL", True, "other"), 10.0)
    with pytest.raises(ValueError, match="finite"):
        trace.append(prediction(0, float("nan")), 10.0)
    with pytest.raises(ValueError, match="frame_id"):
        trace.append(prediction(True, 10.0), 10.0)
    with pytest.raises(ValueError, match="label"):
        trace.append(prediction(0, 10.0, ""), 10.0)
    with pytest.raises(ValueError, match="accepted"):
        trace.append(Prediction("session-1", "P01", 0, 10.0, "NEUTRAL", cast(Any, "yes"), "model-v1"), 10.0)
    with pytest.raises(ValueError, match="rejection_reason"):
        trace.append(Prediction("session-1", "P01", 0, 10.0, "NEUTRAL", False, "model-v1", cast(Any, None)), 10.0)
    with pytest.raises(ValueError, match="greater than or equal"):
        trace.append(prediction(0, 10.0), 9.99)
    with pytest.raises(ValueError, match="rejection_reason"):
        trace.append(prediction(0, 10.0, accepted=False), 10.0)
    with pytest.raises(ValueError, match="must not include"):
        trace.append(prediction(0, 10.0, reason="bad"), 10.0)

    trace.append(prediction(0, 10.0), 10.0)
    with pytest.raises(ValueError, match="frame IDs"):
        trace.append(prediction(0, 10.1), 10.1)
    with pytest.raises(ValueError, match="timestamps"):
        trace.append(prediction(1, 9.9), 10.2)
    with pytest.raises(ValueError, match="received_at"):
        trace.append(prediction(1, 10.2), 10.0)


def test_frame_bound_and_empty_existing_or_failed_save_preserve_buffer(tmp_path, monkeypatch):
    trace = EvaluationTrace(snapshot(), max_frames=1)
    with pytest.raises(ValueError, match="empty"):
        trace.save(tmp_path / "empty.json")

    trace.append(prediction(0, 10.0), 10.0)
    with pytest.raises(OverflowError, match="limit"):
        trace.append(prediction(1, 10.2), 10.2)

    existing = tmp_path / "existing.json"
    existing.write_text("keep", encoding="utf-8")
    with pytest.raises(ValueError, match="already exists"):
        trace.save(existing)
    assert existing.read_text(encoding="utf-8") == "keep"
    assert trace.frame_count == 1

    import gestureforge.traces as traces_module

    def fail_link(source, destination):
        raise OSError("disk full")

    monkeypatch.setattr(traces_module.os, "link", fail_link)
    with pytest.raises(OSError, match="disk full"):
        trace.save(tmp_path / "failed.json")
    assert trace.frame_count == 1
    assert not (tmp_path / "failed.json").exists()
    assert {path.name for path in tmp_path.iterdir()} == {"existing.json"}

    def fail_write_text(*args, **kwargs):
        raise OSError("write failed")

    monkeypatch.setattr(traces_module.Path, "write_text", fail_write_text)
    with pytest.raises(OSError, match="write failed"):
        trace.save(tmp_path / "write-failed.json")
    assert {path.name for path in tmp_path.iterdir()} == {"existing.json"}

def test_diagnostics_are_separate_opt_in_bounded_and_replay_compatible(tmp_path):
    from dataclasses import replace
    from scripts.replay_controller import load_trace

    config = {"algorithm": "knn", "multiplier": 1.5, "margin": 1.0}
    detail: dict[str, float | None] = {"distance": 2.0, "threshold": 3.0, "competitor_distance": 4.0, "competitor_ratio": 2.0}
    with pytest.raises(ValueError, match="Preview or Rehearsal"):
        EvaluationTrace(replace(snapshot(), mode=RoutingMode.LIVE), recognition_config=config)
    plain = EvaluationTrace(snapshot())
    with pytest.raises(ValueError, match="not enabled"):
        plain.append(prediction(), 10.1, detail)
    assert plain.frame_count == 0
    trace = EvaluationTrace(snapshot(), recognition_config=config, max_frames=2)
    trace.append(prediction(), 10.1, detail)
    trace.append(prediction(1, 11.0, "UNKNOWN", accepted=False, reason="no_hand"), 11.1)
    with pytest.raises(OverflowError):
        trace.append(prediction(2, 12.0), 12.1, detail)
    path = tmp_path / "trace.json"
    trace.save(path)
    data = json.loads(path.read_text())
    assert data["recognition_diagnostics"]["frames"] == [
        {"frame_id": 0, "decision": detail}, {"frame_id": 1, "decision": None}]
    assert not any(key in path.read_text() for key in ("landmarks", "features", "train_features", "video"))
    data["annotation_complete"] = True
    path.write_text(json.dumps(data))
    assert len(load_trace(path)["frames"]) == 2


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), -1, True, "raw"])
def test_diagnostics_reject_invalid_values_without_retaining_row(bad):
    trace = EvaluationTrace(snapshot(), recognition_config={"algorithm": "knn", "multiplier": 1.5, "margin": 1})
    with pytest.raises(ValueError, match="finite"):
        trace.append(prediction(), 10.1, {"distance": bad, "threshold": None,
                                        "competitor_distance": None, "competitor_ratio": None})
    assert trace.frame_count == 0
    with pytest.raises(ValueError, match="fields"):
        trace.append(prediction(), 10.1, {"features": None})
    assert trace.frame_count == 0

@pytest.mark.parametrize("config", [
    {"algorithm": "knn", "multiplier": 0, "margin": 1},
    {"algorithm": "knn", "multiplier": 1, "margin": float("nan")},
    {"algorithm": "knn", "multiplier": True, "margin": 1},
    {"algorithm": "other", "multiplier": 1, "margin": 1},
    {"algorithm": "knn", "multiplier": 1, "margin": 1, "training": []},
])
def test_diagnostic_configuration_rejects_non_numeric_and_extra_data(config):
    with pytest.raises(ValueError, match="configuration"):
        EvaluationTrace(snapshot(), recognition_config=config)


def test_full_diagnostic_trace_fits_reader_size_bound_and_survives_failed_save(tmp_path, monkeypatch):
    import gestureforge.traces as traces_module
    trace = EvaluationTrace(snapshot(), recognition_config={"algorithm": "knn", "multiplier": 1.5, "margin": 1})
    detail: dict[str, float | None] = {"distance": 1.23456789, "threshold": 2.3456789,
              "competitor_distance": 3.456789, "competitor_ratio": 2.800000002}
    for index in range(MAX_TRACE_FRAMES):
        trace.append(prediction(index, 10.0 + index * 0.1), 10.01 + index * 0.1, detail)
    original_link = traces_module.os.link
    def fail(*args):
        raise OSError("disk full")
    monkeypatch.setattr(traces_module.os, "link", fail)
    with pytest.raises(OSError, match="disk full"):
        trace.save(tmp_path / "failed.json")
    assert trace.frame_count == MAX_TRACE_FRAMES
    assert not list(tmp_path.iterdir())
    monkeypatch.setattr(traces_module.os, "link", original_link)
    destination = tmp_path / "saved.json"
    trace.save(destination)
    assert destination.stat().st_size < 16 * 1024 * 1024
    assert len(json.loads(destination.read_text())["recognition_diagnostics"]["frames"]) == MAX_TRACE_FRAMES

@pytest.mark.parametrize("camera,hand", [(True, "Right"), (-1, "Right"), (0, "Other"), (None, "Right"), (0, None)])
def test_diagnostic_capture_context_validated(camera, hand):
    with pytest.raises(ValueError, match="capture context"):
        EvaluationTrace(snapshot(), recognition_config={"algorithm": "knn", "multiplier": 1, "margin": 1},
                        camera_index=camera, chosen_hand=hand)


def test_default_trace_covers_ten_minutes_at_studio_poll_rate(tmp_path):
    trace = EvaluationTrace(snapshot())
    # 30 ms polling plus one minute of setup must fit without stopping capture.
    for index in range(22001):
        trace.append(prediction(index, 10.0 + index * 0.03), 10.01 + index * 0.03)
    trace.save(tmp_path / "ten-minute.json")
    assert trace.frame_count == 22001
