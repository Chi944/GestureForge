import json
from typing import Any, cast

import pytest

from gestureforge.contracts import Action, ActionType, Prediction, RoutingMode, RoutingSnapshot
from gestureforge.traces import EvaluationTrace


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
