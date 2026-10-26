"""Generated clock/UI checks, never evidence of physical hold performance."""
from collections import Counter
from dataclasses import replace
import json
import os
from unittest.mock import Mock
from zipfile import ZipFile

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
import numpy as np
import cv2
from PySide6.QtWidgets import QApplication

from gestureforge.dataset import save_dataset
from gestureforge.contracts import Prediction
from gestureforge.fixtures import synthetic_dataset
from gestureforge.profiles import ProfileStore
from gestureforge.vocabulary import GestureVocabulary
from scripts.run_p20 import GuidedWindow, HoldSequence, LatencyFrames, NEGATIVE_CUES, main


def test_twenty_cues_are_five_seconds_with_neutral_and_no_inferred_pass():
    sequence = HoldSequence(("G1", "G2", "G3"), 10)
    now = 10.0
    for index in range(20):
        sequence.advance(now + 2.9, ready=True, capture_ok=True)
        assert sequence.phase == "neutral"
        now += 3
        sequence.advance(now, ready=True, capture_ok=True)
        assert sequence.phase == "form"
        now += 1
        sequence.advance(now, ready=False, capture_ok=True)
        assert sequence.phase == "hold"
        sequence.advance(now + 4.9, ready=False, capture_ok=True)
        assert sequence.completed == index
        now += 5
        sequence.advance(now, ready=False, capture_ok=True)
        assert sequence.completed == index + 1
    assert sequence.phase == "complete"
    holds = [c for c in sequence.cues if c["kind"] == "hold"]
    assert Counter(c["command"] for c in holds) == {"G1": 7, "G2": 7, "G3": 6}
    releases = [c for c in sequence.cues if c["kind"] == "release"]
    assert all(b["timestamp"] - a["timestamp"] == 5 for a, b in zip(holds, releases))
    assert sequence.report()["capture_passed"] is None
    assert sequence.report()["annotation_complete"] is False
    assert sequence.report()["latency_measured"] is False


def test_no_hold_before_ready_and_timeout_is_incomplete():
    sequence = HoldSequence(("G1", "G2", "G3"), 0)
    sequence.advance(29, ready=False, capture_ok=True)
    assert sequence.completed == 0 and sequence.phase == "neutral"
    sequence.advance(30, ready=False, capture_ok=True)
    assert sequence.phase == "interrupted"
    assert "READY" in sequence.reason
    sequence.advance(31, ready=True, capture_ok=True)
    assert sequence.completed == 0


@pytest.mark.parametrize("in_hold", [False, True])
def test_capture_loss_stops_without_counting_incomplete_hold(in_hold):
    sequence = HoldSequence(("G1", "G2", "G3"), 0)
    if in_hold:
        sequence.advance(3, ready=True, capture_ok=True)
        sequence.advance(4, ready=False, capture_ok=True)
    sequence.advance(4.5, ready=True, capture_ok=False)
    assert sequence.phase == "interrupted" and sequence.completed == 0
    assert sequence.cues[-1]["kind"] == "interrupted"


def test_close_interrupt_does_not_rewrite_completed_sequence():
    sequence = HoldSequence(("G1", "G2", "G3"), 0)
    sequence.phase = "complete"
    sequence.completed = 20
    sequence.interrupt("closing", 200)
    assert sequence.phase == "complete" and not sequence.reason


def test_negative_timer_requires_neutral_then_runs_full_ten_minutes_without_ready():
    sequence = HoldSequence(("G1", "G2", "G3"), 10, negative=True)
    sequence.advance(13, ready=False, capture_ok=True)
    assert sequence.phase == "neutral"
    sequence.advance(14, ready=True, capture_ok=True)
    assert sequence.phase == "negative"
    for minute in range(1, 10):
        sequence.advance(14 + minute * 60, ready=False, capture_ok=True)
        assert sequence.phase == "negative" and sequence.completed == minute
    sequence.advance(613.9, ready=False, capture_ok=True)
    assert sequence.phase == "negative"
    sequence.advance(614, ready=False, capture_ok=True)
    assert sequence.phase == "complete"
    report = sequence.report()
    assert report["protocol"] == "GF-P20-ten-minute-negatives-v1"
    assert report["requested_duration_seconds"] == report["elapsed_negative_seconds"] == 600
    assert report["completed_minutes"] == 10
    assert "requested_holds" not in report
    assert report["capture_passed"] is None and not report["annotation_complete"]
    assert [c["instruction"] for c in sequence.cues if c["kind"] == "negative"] == list(NEGATIVE_CUES)


def test_negative_interruption_retains_elapsed_time_without_pass():
    sequence = HoldSequence(("G1", "G2", "G3"), 0, negative=True)
    sequence.advance(3, ready=True, capture_ok=True)
    sequence.advance(63, ready=False, capture_ok=True)
    sequence.advance(93, ready=False, capture_ok=False)
    report = sequence.report()
    assert report["status"] == "interrupted"
    assert report["elapsed_negative_seconds"] == 90
    assert report["completed_minutes"] == 1
    assert report["capture_passed"] is None
    sequence.advance(1000, ready=True, capture_ok=True)
    assert sequence.phase == "interrupted" and sequence.negative_elapsed == 90


@pytest.fixture
def window(tmp_path, monkeypatch, request):
    import gestureforge.app as app_module
    app = QApplication.instance() or QApplication([])
    monkeypatch.setattr(app_module, "DEFAULT_STUDIO_STATE_FOLDER", tmp_path / "state")
    monkeypatch.setattr(app_module.Window, "log", lambda *args: None)
    bundle = synthetic_dataset(trials_per_label_per_split=2)
    vocabulary = GestureVocabulary(("G1", "G2", "G3"))
    mapping = dict(zip(bundle.vocabulary.labels, vocabulary.labels, strict=True))
    records = tuple(replace(r, participant_id="TEST_PERSON", hand="Right", provenance="human",
                            intended_label=mapping[r.intended_label]) for r in bundle.records)
    data = save_dataset(tmp_path / "data", records, bundle.features,
                        {"chosen_hand": "Right", "warning": "GENERATED SOFTWARE TEST ONLY"},
                        vocabulary=vocabulary)
    store = ProfileStore(tmp_path / "profiles")
    assert data.manifest_path is not None
    loaded = store.create("Software fixture", data.manifest_path, "Right", consent=True)
    output = tmp_path / "run"
    output.mkdir()
    value = GuidedWindow(loaded, store, 1, output, negative=getattr(request, "param", False))
    yield value
    value.close()
    app.processEvents()


def test_window_starts_no_camera_and_close_retains_not_started(window):
    assert window.worker is None
    assert window.hold_sequence is None
    assert window.routing.snapshot.mode.value == "REHEARSAL"
    assert {a.kind.value for _, a in window.routing.snapshot.bindings} == {"NEXT", "PREVIOUS", "BOOKMARK"}
    assert window.names["G1"]
    window.close()
    assert json.loads((window.output / "run.json").read_text())["status"] == "not_started"
    assert window.latency_frames is None
    assert not window.record_latency_video
    assert not list(window.output.glob("private-latency*"))


@pytest.mark.parametrize("window", [True], indirect=True)
def test_negative_ui_and_incomplete_report_are_distinct(window, monkeypatch):
    assert window.worker is None
    assert window.begin_holds.text() == "Start guided ten-minute negative test"
    assert "Avoid fist, thumb up and V sign" in window.cue.text()
    monkeypatch.setattr(window, "start_camera", lambda: None)
    window.start_holds()
    report = json.loads((window.output / "run.json").read_text())
    assert report["protocol"] == "GF-P20-ten-minute-negatives-v1"
    assert report["status"] == "interrupted"
    assert report["elapsed_negative_seconds"] == 0
    assert report["capture_passed"] is None
    window.hold_sequence = HoldSequence(("G1", "G2", "G3"), 0, negative=True)
    window.hold_sequence.advance(3, ready=True, capture_ok=True)
    window.render_cue(3)
    assert "10:00 remaining" in window.cue.text()
    assert NEGATIVE_CUES[0] in window.cue.text()


def test_failed_camera_start_saves_incomplete_not_pass(window, monkeypatch):
    monkeypatch.setattr(window, "start_camera", lambda: None)
    window.start_holds()
    report = json.loads((window.output / "run.json").read_text())
    assert report["status"] == "interrupted" and report["completed_cue_windows"] == 0
    assert report["capture_passed"] is None
    assert (window.output / "session-summary.json").exists()


def test_changed_configuration_refuses_capture(window, monkeypatch):
    start = Mock()
    monkeypatch.setattr(window, "start_camera", start)
    window.camera_index = 2
    window.start_holds()
    start.assert_not_called()
    assert window.hold_sequence is None
    assert "changed" in window.cue.text()


def test_save_failure_offers_retry_without_repeating_holds(window, monkeypatch):
    window.hold_sequence = HoldSequence(("G1", "G2", "G3"), 0)
    window.hold_sequence.interrupt("Operator stopped", 1)
    outcomes = iter([False, True])
    pause = Mock(side_effect=lambda: next(outcomes, True))
    monkeypatch.setattr(window, "pause", pause)
    window.finish_holds()
    assert not window.finished_evidence
    assert window.begin_holds.isEnabled()
    assert "Retry saving" in window.begin_holds.text()
    window.start_holds()
    assert window.finished_evidence
    assert window.hold_sequence.completed == 0
    assert json.loads((window.output / "run.json").read_text())["status"] == "interrupted"


def test_focus_loss_stops_and_preserves_cues(window, monkeypatch):
    now = 100.0
    monkeypatch.setattr("scripts.run_p20.time.monotonic", lambda: now)
    window.hold_sequence = HoldSequence(("G1", "G2", "G3"), 95)
    window.hold_sequence.advance(98, ready=True, capture_ok=True)
    window.hold_sequence.advance(99, ready=False, capture_ok=True)
    window.capture_snapshot = window.routing.snapshot
    window.capture_worker = Mock()
    window.worker = window.capture_worker
    window.worker.isFinished.return_value = False
    window.worker.isInterruptionRequested.return_value = False
    window.evaluation_trace = Mock()
    window.last_tick = 99.9
    monkeypatch.setattr(window, "isActiveWindow", lambda: False)
    def pause():
        window.worker = None
        window.evaluation_trace = None
        return True
    monkeypatch.setattr(window, "pause", pause)
    window.tick_holds()
    report = json.loads((window.output / "run.json").read_text())
    assert report["status"] == "interrupted"
    assert report["completed_cue_windows"] == 0
    assert any(c["kind"] == "hold" for c in report["cues"])


def test_private_frames_preserve_timestamp_identity_gaps_and_unmirrored_image(tmp_path):
    recording = LatencyFrames(tmp_path)
    frame = np.zeros((480, 800, 3), dtype=np.uint8)
    frame[:, :400] = (0, 0, 255)
    first = Prediction("session", "profile", 4, 100.125, "G1", True)
    recording.append(frame, first)
    recording.append(frame, replace(first, frame_id=7, timestamp=100.325))
    report = recording.close()
    assert report["frame_count"] == 2 and report["skipped_capture_frames"] == 2
    assert report["max_capture_gap_seconds"] == pytest.approx(0.2)
    index = [json.loads(line) for line in (tmp_path / "private-latency-frames.jsonl").read_text().splitlines()]
    assert [r["capture_timestamp"] for r in index] == [100.125, 100.325]
    assert [r["frame_id"] for r in index] == [4, 7]
    assert all(r["session_id"] == "session" for r in index)
    with ZipFile(tmp_path / "private-latency-frames.zip") as archive:
        decoded = cv2.imdecode(np.frombuffer(archive.read("000000.jpg"), np.uint8), cv2.IMREAD_COLOR)
    assert decoded.shape == (384, 640, 3)
    assert decoded[100, 100, 2] > 240 and decoded[100, 500, 2] < 10
    assert recording.close() == report
    with pytest.raises(ValueError, match="closed"):
        recording.append(frame, first)


@pytest.mark.parametrize("limit,value,match", [("MAX_BYTES", 1, "storage"),
                                               ("MAX_FRAMES", 0, "frame limit")])
def test_private_recording_caps_before_writing(tmp_path, monkeypatch, limit, value, match):
    recording = LatencyFrames(tmp_path)
    monkeypatch.setattr(recording, limit, value)
    with pytest.raises(ValueError, match=match):
        recording.append(np.zeros((8, 8, 3), np.uint8), Prediction("s", "p", 0, 1, "G1", True))
    assert recording.close()["frame_count"] == 0


def test_private_recording_rejects_out_of_order_and_excessive_duration(tmp_path):
    recording = LatencyFrames(tmp_path)
    frame = np.zeros((8, 8, 3), np.uint8)
    first = Prediction("s", "p", 3, 1, "G1", True)
    recording.append(frame, first)
    with pytest.raises(ValueError, match="identity/time"):
        recording.append(frame, first)
    with pytest.raises(ValueError, match="six-minute"):
        recording.append(frame, replace(first, frame_id=4, timestamp=362))
    assert recording.close()["frame_count"] == 1


def test_recording_failure_stops_packet_dispatch_and_marks_incomplete(window, monkeypatch):
    window.latency_frames = Mock()
    window.latency_frames.append.side_effect = OSError("disk full")
    window.latency_frames.close.return_value = {"frame_count": 0}
    window.hold_sequence = HoldSequence(("G1", "G2", "G3"), 0)
    packet = (np.zeros((8, 8, 3), np.uint8), Prediction("s", "p", 0, 1, "G1", True))
    monkeypatch.setattr("scripts.run_p20.QTimer.singleShot", lambda delay, callback: None)
    assert window.record_packet(packet) is None
    assert window.hold_sequence.phase == "interrupted"
    assert "disk full" in window.hold_sequence.reason
    window.finish_holds()
    report = json.loads((window.output / "run.json").read_text())
    assert report["status"] == "interrupted" and report["capture_passed"] is None
    assert report["private_visual_recording_error"] == "disk full"
    window.latency_frames.close.assert_called_once()


def test_recording_opt_in_wraps_existing_mailbox_without_second_camera(window, monkeypatch):
    window.record_latency_video = True
    worker = Mock()
    packet = (np.zeros((8, 8, 3), np.uint8), Prediction("s", "p", 0, 1, "G1", True))
    worker.take_latest.return_value = packet
    def start_camera():
        window.worker = worker
        window.evaluation_trace = Mock()
    monkeypatch.setattr(window, "start_camera", start_camera)
    monkeypatch.setattr(window, "pause", lambda: True)
    window.start_holds()
    original = worker.take_latest
    assert original() is packet
    assert window.latency_frames.count == 1
    window.hold_sequence.interrupt("test finished", 2)
    window.finish_holds()
    window.worker = None
    window.evaluation_trace = None
    assert window.latency_frames.closed


def test_private_video_cli_refuses_public_output_before_profile_or_camera(tmp_path):
    with pytest.raises(SystemExit) as exc:
        main(["--profile-id", "unused", "--output-dir", str(tmp_path), "--record-latency-video"])
    assert exc.value.code == 2
