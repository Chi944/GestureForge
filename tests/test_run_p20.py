"""Generated clock/UI checks, never evidence of physical hold performance."""
from collections import Counter
from dataclasses import replace
import json
import os
from unittest.mock import Mock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import pytest
from PySide6.QtWidgets import QApplication

from gestureforge.dataset import save_dataset
from gestureforge.fixtures import synthetic_dataset
from gestureforge.profiles import ProfileStore
from gestureforge.vocabulary import GestureVocabulary
from scripts.run_p20 import GuidedWindow, HoldSequence


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


@pytest.fixture
def window(tmp_path, monkeypatch):
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
    value = GuidedWindow(loaded, store, 1, output)
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
