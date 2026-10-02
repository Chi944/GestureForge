import os
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import Mock

import numpy as np
import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QEvent
from PySide6.QtWidgets import QApplication

from gestureforge.contracts import Observation, RoutingMode
from gestureforge.vocabulary import GestureVocabulary


@pytest.fixture(autouse=True)
def isolated_app_state(tmp_path, monkeypatch):
    import gestureforge.app as app_module

    monkeypatch.setattr(app_module, "DEFAULT_STUDIO_STATE_FOLDER", tmp_path / "studio")
    monkeypatch.setattr(app_module.Window, "log", lambda self, record: None)


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


def frame():
    return np.zeros((4, 4, 3), dtype=np.uint8)


def observation(session="enrol-capture", profile="TEST", frame_id=1, timestamp=0.1):
    points = np.arange(63, dtype=float).reshape(21, 3) / 100
    return Observation(session, profile, frame_id, timestamp, 1, "Right", points)


def model(vocabulary=None):
    vocabulary = vocabulary or GestureVocabulary(("G1", "G2", "G3"))
    return SimpleNamespace(
        predict=lambda _: (vocabulary.action_ids[0], True, ""),
        train_labels=vocabulary.labels,
        model_version="gesture-test-revision-2",
        config=SimpleNamespace(algorithm="knn", multiplier=2.0, margin=1.5),
    )


class FakeWorker:
    def __init__(self, *args, observation_only=False, wait_result=True, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.observation_only = observation_only
        self.wait_result = wait_result
        self.packets = []
        self.error = ""
        self.finished = False
        self.interrupted = False
        self.start = Mock()

    def take_latest(self):
        if self.packets:
            return self.packets.pop(0)
        return None

    def isFinished(self):
        return self.finished

    def wait(self, timeout=None):
        return self.wait_result

    def requestInterruption(self):
        self.interrupted = True

    def isInterruptionRequested(self):
        return self.interrupted


class FakeCloseEvent:
    def __init__(self):
        self.accepted = False
        self.ignored = False

    def accept(self):
        self.accepted = True

    def ignore(self):
        self.ignored = True


def fill_enrolment_form(window, participant="TEST"):
    widget = window.enrolment_widget
    window.deck_tabs.setCurrentWidget(widget)
    widget.participant.setText(participant)
    widget.setup.setText("Synthetic host test only")
    widget.consent.setChecked(True)
    return widget


def capture_factory(workers):
    def factory(*args, **kwargs):
        worker = FakeWorker(*args, **kwargs)
        workers.append(worker)
        return worker
    return factory


@pytest.mark.parametrize("interruption", [None, "cancel", "tab", "close"])
def test_enrolment_queued_scroll_stays_with_current_request(interruption, monkeypatch, qapp):
    import gestureforge.app as app_module

    window = app_module.Window(studio=True)
    callbacks = []
    monkeypatch.setattr(app_module.QTimer, "singleShot", lambda _delay, callback: callbacks.append(callback))
    try:
        window.deck_tabs.setCurrentWidget(window.enrolment_widget)
        window.enrolment_request_id = "current-collection"
        bar = window.studio_scroll.verticalScrollBar()
        bar.setRange(0, 100)
        bar.setValue(20)
        window._scroll_enrolment_controls_into_view()
        if interruption == "cancel":
            window.release_enrolment_capture("current-collection")
        elif interruption == "tab":
            window.deck_tabs.setCurrentWidget(window.card_frame)
        elif interruption == "close":
            window._closing = True
        callbacks[0]()
        assert bar.value() == (100 if interruption is None else 20)
    finally:
        window._closing = False
        window.enrolment_request_id = ""
        window.close()


def test_enrolment_request_hands_off_single_worker_and_attaches_on_first_matching_frame(tmp_path, monkeypatch, qapp):
    import gestureforge.app as app_module
    from gestureforge.app import Window

    monkeypatch.setattr(app_module, "DEFAULT_ENROLMENT_FOLDER", tmp_path / "enrolment")
    workers: list[FakeWorker] = []

    def factory(*args, **kwargs):
        worker = FakeWorker(*args, **kwargs)
        workers.append(worker)
        return worker

    monkeypatch.setattr(app_module, "CaptureWorker", factory)
    selected = model()
    window = Window(model=selected, studio=True, studio_mode=RoutingMode.PREVIEW)
    old_worker = FakeWorker(observation_only=False)
    window.worker = old_worker
    try:
        widget = fill_enrolment_form(window)
        assert widget.output_root == tmp_path / "enrolment"
        widget.request_collection()
        assert old_worker.interrupted
        assert len(workers) == 0
        assert widget.pending_plan is not None
        assert window.pending_enrolment_request_id
        old_worker.finished = True
        window.poll()
        assert len(workers) == 1
        capture = workers[0]
        assert capture.observation_only is True
        assert window.worker is capture
        assert widget.session is None
        assert widget.pending_plan is not None
        wrong = observation("old-session", "TEST", 1, 0.1)
        capture.packets.append((frame(), wrong))
        window.poll()
        assert widget.session is None
        matching = observation(window.enrolment_capture_session, window.enrolment_capture_profile, 2, 0.2)
        capture.packets.append((frame(), matching))
        assert window.routing is not None
        routing_process = Mock()
        controller_process = Mock()
        monkeypatch.setattr(window.routing, "process", routing_process)
        monkeypatch.setattr(window.controller, "process", controller_process)
        trace = SimpleNamespace(append=Mock())
        window.evaluation_trace = cast(Any, trace)
        window.poll()
        assert widget.session is not None
        assert widget.session.capture_session == matching.session_id
        routing_process.assert_not_called()
        controller_process.assert_not_called()
        trace.append.assert_not_called()
        window.evaluation_trace = None
        assert window.model is selected
        assert window.routing is not None and window.routing.state == "PAUSED"
        assert window.selected_profile_id is None
        assert not window.start_button.isEnabled()
    finally:
        window.evaluation_trace = None
        window.close()


def test_enrolment_tab_entry_pauses_recognition_and_disables_start(tmp_path, monkeypatch, qapp):
    import gestureforge.app as app_module
    from gestureforge.app import Window

    monkeypatch.setattr(app_module, "DEFAULT_ENROLMENT_FOLDER", tmp_path)
    window = Window(model=model(), studio=True)
    recognition = FakeWorker(observation_only=False)
    window.worker = recognition
    try:
        window.deck_tabs.setCurrentWidget(window.enrolment_widget)
        assert recognition.interrupted
        assert not window.start_button.isEnabled()
        window.start_camera()
        assert window.worker is recognition
    finally:
        window.close()


def test_enrolment_capture_can_start_without_loaded_model(tmp_path, monkeypatch, qapp):
    import gestureforge.app as app_module
    from gestureforge.app import Window

    monkeypatch.setattr(app_module, "DEFAULT_ENROLMENT_FOLDER", tmp_path)
    workers: list[FakeWorker] = []
    monkeypatch.setattr(app_module, "CaptureWorker", capture_factory(workers))
    window = Window(model=None, studio=True)
    try:
        widget = fill_enrolment_form(window)
        widget.request_collection()
        assert len(workers) == 1
        assert workers[0].observation_only is True
        assert window.model is None
        assert "Enrolment mode" in window.prediction.text()
    finally:
        window.close()


def test_leaving_enrolment_tab_cancels_pending_collection(tmp_path, monkeypatch, qapp):
    import gestureforge.app as app_module
    from gestureforge.app import Window

    monkeypatch.setattr(app_module, "DEFAULT_ENROLMENT_FOLDER", tmp_path)
    workers: list[FakeWorker] = []
    monkeypatch.setattr(app_module, "CaptureWorker", capture_factory(workers))
    window = Window(model=model(), studio=True)
    old_worker = FakeWorker(observation_only=False)
    window.worker = old_worker
    try:
        widget = fill_enrolment_form(window)
        widget.request_collection()
        assert window.pending_enrolment_request_id
        assert widget.pending_plan is not None

        window.deck_tabs.setCurrentWidget(window.card_frame)

        assert widget.pending_plan is None
        assert widget.request_id == ""
        assert window.pending_enrolment_request_id == ""
        assert len(workers) == 0
    finally:
        window.close()


def test_focus_loss_cancels_active_enrolment_capture(tmp_path, monkeypatch, qapp):
    import gestureforge.app as app_module
    from gestureforge.app import Window

    monkeypatch.setattr(app_module, "DEFAULT_ENROLMENT_FOLDER", tmp_path)
    workers: list[FakeWorker] = []
    monkeypatch.setattr(app_module, "CaptureWorker", capture_factory(workers))
    window = Window(model=model(), studio=True)
    try:
        widget = fill_enrolment_form(window)
        widget.request_collection()
        capture = workers[0]
        assert window.enrolment_request_id

        window.changeEvent(QEvent(QEvent.Type.ActivationChange))

        assert capture.interrupted
        assert widget.session is None
        assert window.enrolment_request_id == ""
        assert "Paused after focus loss" in window.state.text()
    finally:
        window.close()


def test_enrolment_cancel_uses_stale_token_guard_and_does_not_auto_resume(tmp_path, monkeypatch, qapp):
    import gestureforge.app as app_module
    from gestureforge.app import Window

    monkeypatch.setattr(app_module, "DEFAULT_ENROLMENT_FOLDER", tmp_path)
    workers: list[FakeWorker] = []
    monkeypatch.setattr(app_module, "CaptureWorker", capture_factory(workers))
    window = Window(model=model(), studio=True)
    try:
        widget = fill_enrolment_form(window)
        widget.request_collection()
        capture = workers[0]
        token = window.enrolment_request_id
        window.release_enrolment_capture("stale-token")
        assert window.enrolment_request_id == token
        assert not capture.interrupted
        widget.stop_collection()
        assert capture.interrupted
        assert window.enrolment_request_id == ""
        capture.packets.append((frame(), observation(window.enrolment_capture_session, "TEST", 3, 0.3)))
        window.poll()
        assert widget.session is None
        assert window.worker is capture
        assert capture.start.call_count == 1
    finally:
        window.close()


def test_stale_enrolment_request_cannot_interrupt_active_capture(tmp_path, monkeypatch, qapp):
    import gestureforge.app as app_module
    from gestureforge.app import Window

    monkeypatch.setattr(app_module, "DEFAULT_ENROLMENT_FOLDER", tmp_path)
    workers: list[FakeWorker] = []
    monkeypatch.setattr(app_module, "CaptureWorker", capture_factory(workers))
    window = Window(model=model(), studio=True)
    try:
        widget = fill_enrolment_form(window)
        widget.request_collection()
        capture = workers[0]
        token = window.enrolment_request_id
        plan = widget.pending_plan
        assert plan is not None

        window.start_enrolment_capture(plan, "")
        window.start_enrolment_capture(plan, "stale-token")
        replacement_plan = SimpleNamespace(participant=plan.participant, hand=plan.hand)
        window.start_enrolment_capture(replacement_plan, token)

        assert window.worker is capture
        assert window.enrolment_request_id == token
        assert not capture.interrupted
        assert len(workers) == 1
    finally:
        window.close()


def test_enrolment_new_request_waits_for_interrupted_observation_worker_release(tmp_path, monkeypatch, qapp):
    import gestureforge.app as app_module
    from gestureforge.app import Window

    monkeypatch.setattr(app_module, "DEFAULT_ENROLMENT_FOLDER", tmp_path)
    workers: list[FakeWorker] = []
    monkeypatch.setattr(app_module, "CaptureWorker", capture_factory(workers))
    window = Window(model=model(), studio=True)
    try:
        widget = fill_enrolment_form(window)
        widget.request_collection()
        first = workers[0]
        widget.stop_collection()
        assert first.interrupted
        widget.request_collection()
        assert len(workers) == 1
        assert window.pending_enrolment_request_id
        first.finished = True
        window.poll()
        assert len(workers) == 2
        assert window.worker is workers[1]
        assert workers[1].start.call_count == 1
        assert widget.pending_plan is not None
    finally:
        window.close()


@pytest.mark.parametrize("phase", ["startup", "after_frame", "fault"])
def test_enrolment_capture_timeout_and_fault_paths(phase, tmp_path, monkeypatch, qapp):
    import gestureforge.app as app_module
    from gestureforge.app import Window

    current = [0.0]
    monkeypatch.setattr(app_module.time, "monotonic", lambda: current[0])
    monkeypatch.setattr(app_module, "DEFAULT_ENROLMENT_FOLDER", tmp_path)
    workers: list[FakeWorker] = []
    monkeypatch.setattr(app_module, "CaptureWorker", capture_factory(workers))
    window = Window(model=model(), studio=True)
    try:
        widget = fill_enrolment_form(window)
        widget.request_collection()
        capture = workers[0]
        if phase == "startup":
            current[0] = 21.0
            window.poll()
            assert "stalled" in widget.feedback.text()
            assert capture.interrupted
        elif phase == "after_frame":
            capture.packets.append((frame(), observation(window.enrolment_capture_session, "TEST", 1, 0.1)))
            current[0] = 0.1
            window.poll()
            current[0] = 2.2
            window.poll()
            assert "stalled" in widget.feedback.text()
            assert capture.interrupted
        else:
            capture.error = "camera boom"
            capture.finished = True
            window.poll()
            assert "camera boom" in widget.feedback.text()
            assert window.enrolment_request_id == ""
    finally:
        window.close()


def test_enrolment_save_error_blocks_pause_close_and_model_replacement_until_retry(tmp_path, monkeypatch, qapp):
    import gestureforge.app as app_module
    import gestureforge.enrolment as enrolment_module
    from gestureforge.enrolment import OFFSETS
    from gestureforge.app import Window

    monkeypatch.setattr(app_module, "DEFAULT_ENROLMENT_FOLDER", tmp_path)
    workers: list[FakeWorker] = []
    monkeypatch.setattr(app_module, "CaptureWorker", capture_factory(workers))
    selected = model()
    window = Window(model=selected, studio=True)
    try:
        widget = fill_enrolment_form(window)
        widget.request_collection()
        capture = workers[0]
        capture.packets.append((frame(), observation(window.enrolment_capture_session, "TEST", 1, 0.1)))
        window.poll()
        assert widget.session is not None
        current = [widget.session.last_now + 1.0]
        widget.clock = lambda: current[0]
        original_save = enrolment_module.save_dataset

        def fail_save(*args, **kwargs):
            raise OSError("disk full")

        monkeypatch.setattr(enrolment_module, "save_dataset", fail_save)
        start = current[0]
        widget.session.begin(start)
        for index, offset in enumerate(OFFSETS):
            at = start + 2.0 + offset + 0.01
            widget.session.advance(
                at,
                observation(widget.session.capture_session, widget.session.capture_profile, index + 2, at),
            )
        widget.session.advance(start + 4.1)
        current[0] = start + 4.2
        assert widget.session.state == "save_error"
        assert len(widget.session.pending_records) == 5
        widget.refresh()
        assert not window.pause()
        assert capture.interrupted
        assert widget.session.state == "save_error"
        assert widget.session.after_save == "cancelled"
        assert widget.retry_button.isEnabled()
        with pytest.raises(ValueError, match="Save the current evaluation trace|Studio must be open"):
            window.use_studio_model(model(), "Right", "P02", GestureVocabulary(("G1", "G2", "G3")))
        close = FakeCloseEvent()
        window.closeEvent(close)
        assert close.ignored
        assert window.model is selected
        monkeypatch.setattr(enrolment_module, "save_dataset", original_save)
        current[0] = start + 4.3
        widget.retry_save()
        assert widget.session.state == "cancelled"
        assert not widget.session.pending_records
        assert widget.session.manifest.exists()
    finally:
        if widget.session is not None:
            widget.session.state = "cancelled"
        window.close()
