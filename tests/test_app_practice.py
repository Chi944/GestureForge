import os
from types import SimpleNamespace
from unittest.mock import Mock

import numpy as np
import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from gestureforge.app import Window
from gestureforge.contracts import Action, ActionType, Prediction, RoutingMode
from gestureforge.practice_widget import PersonalRehearsalWidget
from gestureforge.vocabulary import GestureVocabulary


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture(autouse=True)
def isolated_state(tmp_path, monkeypatch):
    import gestureforge.app as app_module

    monkeypatch.setattr(app_module, "DEFAULT_STUDIO_STATE_FOLDER", tmp_path / "studio")
    monkeypatch.setattr(app_module, "DEFAULT_ENROLMENT_FOLDER", tmp_path / "enrolment")
    monkeypatch.setattr(app_module.Window, "log", lambda self, record: None)


class FakeWorker:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.packets = []
        self.error = ""
        self.finished = False
        self.interrupted = False
        self.start = Mock()

    def take_latest(self):
        return self.packets.pop(0) if self.packets else None

    def isFinished(self):
        return self.finished

    def wait(self, timeout=None):
        return True

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


class Clock:
    def __init__(self):
        self.value = 200.0
        self.frame_id = 0

    def advance(self, amount=0.10):
        self.value += amount
        self.frame_id += 1
        return self.value


def frame():
    return np.zeros((4, 4, 3), dtype=np.uint8)


def model(vocabulary=None):
    vocabulary = vocabulary or GestureVocabulary(("G1", "G2", "G3"))
    return SimpleNamespace(
        predict=lambda _: (vocabulary.action_ids[0], True, ""),
        train_labels=vocabulary.labels,
        model_version="practice-revision",
        config=SimpleNamespace(algorithm="knn", multiplier=2.0, margin=1.5),
    )


def prediction(window, clock, label, *, accepted=True, rejection_reason=""):
    assert window.routing is not None
    snapshot = window.routing.snapshot
    return Prediction(
        snapshot.session_id,
        snapshot.profile_id,
        clock.frame_id,
        clock.value,
        label,
        accepted,
        snapshot.model_version,
        rejection_reason,
    )


def make_worker_factory(workers: list[FakeWorker]):
    def factory(*args, **kwargs):
        worker = FakeWorker(*args, **kwargs)
        workers.append(worker)
        return worker

    return factory


def enqueue(window, worker, clock, label, *, accepted=True, rejection_reason=""):
    worker.packets.append((
        frame(),
        prediction(window, clock, label, accepted=accepted, rejection_reason=rejection_reason),
    ))
    window.poll()
    clock.advance()


def finish_worker(window, worker):
    worker.finished = True
    window.poll()


def feed_until_armed(window, worker, clock):
    for _ in range(6):
        enqueue(window, worker, clock, "NEUTRAL")
        if window.practice_attempt is not None and window.practice_attempt.status == "armed":
            return
    raise AssertionError("practice did not arm from NEUTRAL")


def feed_window(window, worker, clock, label, *, seconds=5.8, accepted=True, rejection_reason=""):
    steps = int(seconds / 0.10)
    for _ in range(steps):
        enqueue(window, worker, clock, label, accepted=accepted, rejection_reason=rejection_reason)
    if window.practice_widget is not None:
        window.practice_widget.tick()


def start_practice(window) -> PersonalRehearsalWidget:
    window.practice_consent.setChecked(True)
    assert window.start_practice_rehearsal()
    assert window.practice_widget is not None
    return window.practice_widget


def test_practice_tab_starts_rehearsal_context_with_local_consent(qapp):
    vocabulary = GestureVocabulary(("G1", "G2", "G3"))
    window = Window(model=model(vocabulary), studio=True, vocabulary=vocabulary)
    try:
        assert not window.start_practice_rehearsal()
        assert "consent" in window.practice_status.text().lower()

        widget = start_practice(window)

        assert window.practice_attempt is not None
        assert window.routing is not None
        assert window.routing.snapshot.mode.value == "REHEARSAL"
        assert window.routing.snapshot.context_id.startswith("practice:")
        assert widget.attempt.gesture_ids == ("G1", "G2", "G3")
    finally:
        window.close()


def test_practice_prepare_uses_exact_generation_and_routes_once(monkeypatch, qapp):
    import gestureforge.app as app_module

    workers: list[FakeWorker] = []
    monkeypatch.setattr(app_module, "CaptureWorker", make_worker_factory(workers))
    clock = Clock()
    monkeypatch.setattr(app_module.time, "monotonic", lambda: clock.value + 0.01)
    vocabulary = GestureVocabulary(("G1", "G2", "G3"))
    window = Window(model=model(vocabulary), studio=True, vocabulary=vocabulary)
    try:
        widget = start_practice(window)
        widget.prepare()
        assert len(workers) == 1
        worker = workers[0]
        assert window.routing is not None
        routing = window.routing
        snapshot = routing.snapshot
        assert worker.args[5:7] == (snapshot.session_id, snapshot.profile_id)

        route = Mock(wraps=routing.route)
        routing.route = route  # type: ignore[method-assign]
        for _ in range(5):
            enqueue(window, worker, clock, "NEUTRAL")
        widget.begin()
        clock.advance(0.05)
        for _ in range(8):
            enqueue(window, worker, clock, "G1")

        assert route.call_count == 1
        assert window.session_summary.counts()["simulated"] == 1
    finally:
        window.close()


def test_practice_stop_saves_and_restores_prior_context(monkeypatch, qapp, tmp_path):
    import gestureforge.app as app_module

    monkeypatch.setattr(app_module, "DEFAULT_STUDIO_STATE_FOLDER", tmp_path / "studio")
    vocabulary = GestureVocabulary(("G1", "G2", "G3"))
    window = Window(model=model(vocabulary), studio=True, vocabulary=vocabulary)
    try:
        assert window.routing is not None
        assert window.routing is not None
        previous = window.routing.snapshot
        widget = start_practice(window)
        widget.stop()

        assert window.practice_attempt is None
        assert window.practice_widget is None
        assert window.routing is not None
        assert window.routing.snapshot.context_id == previous.context_id
        assert window.routing.snapshot.mode == previous.mode
        assert "practice cancelled" in window.practice_status.text().lower()
        assert "local rehearsal results saved" in window.practice_status.text().lower()
        assert list((tmp_path / "studio" / "practice").glob("practice-*.json"))
    finally:
        window.close()


def test_practice_can_run_from_manual_only_context_and_restore_it(qapp):
    vocabulary = GestureVocabulary(("G1", "G2", "G3"))
    window = Window(model=model(vocabulary), studio=True, vocabulary=vocabulary)
    try:
        assert window.configure_studio(context_id="manual-stage", bindings={})
        assert window.routing_manual_only

        widget = start_practice(window)
        assert window.practice_attempt is not None
        assert window.routing is not None
        assert window.routing.snapshot.mode.value == "REHEARSAL"
        assert not window.routing_manual_only

        widget.stop()
        assert window.practice_attempt is None
        assert window.routing_manual_only
        assert window.manual_context_id == "manual-stage"
        assert "practice cancelled" in window.practice_status.text().lower()
    finally:
        window.close()


def test_practice_save_failure_blocks_restore_close_and_retry_unblocks(monkeypatch, qapp):
    vocabulary = GestureVocabulary(("G1", "G2", "G3"))
    window = Window(model=model(vocabulary), studio=True, vocabulary=vocabulary)
    try:
        widget = start_practice(window)

        def fail_save(_directory):
            raise OSError("disk full")

        assert window.practice_attempt is not None
        original_save = type(window.practice_attempt).save.__get__(window.practice_attempt, type(window.practice_attempt))
        monkeypatch.setattr(window.practice_attempt, "save", fail_save)
        widget.stop()

        assert window.practice_attempt is not None
        assert window.practice_widget is widget
        assert widget.save_error
        close_event = FakeCloseEvent()
        window.closeEvent(close_event)
        assert close_event.ignored

        monkeypatch.setattr(window.practice_attempt, "save", original_save)
        widget.save()
        assert window._finish_practice_rehearsal()
        assert window.practice_attempt is None
        assert "practice cancelled" in window.practice_status.text().lower()
    finally:
        window._auto_archive_summary_on_close = False
        window._closing = False
        window.practice_attempt = None
        window.practice_widget = None
        window.close()



def test_practice_restore_failure_can_retry_after_terminal_save(monkeypatch, qapp, tmp_path):
    import gestureforge.app as app_module

    monkeypatch.setattr(app_module, "DEFAULT_STUDIO_STATE_FOLDER", tmp_path / "studio")
    vocabulary = GestureVocabulary(("G1", "G2", "G3"))
    window = Window(model=model(vocabulary), studio=True, vocabulary=vocabulary)
    try:
        assert window.routing is not None
        previous = window.routing.snapshot
        widget = start_practice(window)
        finish_trace = Mock(side_effect=[False, True, True, True])
        monkeypatch.setattr(window, "finish_evaluation_trace", finish_trace)

        widget.stop()

        assert window.practice_attempt is not None
        assert window.practice_widget is widget
        assert window._practice_previous is not None
        assert "prior studio context was not restored" in window.practice_status.text().lower()
        assert list((tmp_path / "studio" / "practice").glob("practice-*.json"))

        assert window.pause()

        assert window.practice_attempt is None
        assert window.practice_widget is None
        assert window.routing is not None
        assert window.routing.snapshot.context_id == previous.context_id
        assert window.routing.snapshot.mode == previous.mode
        assert "practice cancelled" in window.practice_status.text().lower()
        assert "local rehearsal results saved" in window.practice_status.text().lower()
    finally:
        window.close()


def test_practice_wrong_generation_packet_is_ignored(monkeypatch, qapp):
    import gestureforge.app as app_module

    workers: list[FakeWorker] = []
    monkeypatch.setattr(app_module, "CaptureWorker", make_worker_factory(workers))
    clock = Clock()
    monkeypatch.setattr(app_module.time, "monotonic", lambda: clock.value + 0.01)
    vocabulary = GestureVocabulary(("G1", "G2", "G3"))
    window = Window(model=model(vocabulary), studio=True, vocabulary=vocabulary)
    try:
        widget = start_practice(window)
        widget.prepare()
        worker = workers[0]
        stale = prediction(window, clock, "NEUTRAL")
        stale = Prediction(
            "other-session", stale.profile_id, stale.frame_id, stale.timestamp,
            stale.label, stale.accepted, stale.model_version, stale.rejection_reason,
        )
        worker.packets.append((frame(), stale))
        window.poll()

        assert window.practice_attempt is not None
        assert window.practice_attempt.status == "preparing"
        assert window.session_summary.counts()["simulated"] == 0
    finally:
        window.close()


def test_practice_save_button_during_active_attempt_does_not_restore(qapp):
    vocabulary = GestureVocabulary(("G1", "G2", "G3"))
    window = Window(model=model(vocabulary), studio=True, vocabulary=vocabulary)
    try:
        widget = start_practice(window)
        widget.save_button.click()
        assert window.practice_attempt is not None
        assert window.practice_widget is widget
        assert window.routing is not None
        assert window.routing.snapshot.context_id.startswith("practice:")
        assert "finish or stop" in window.practice_status.text().lower()
    finally:
        window.close()


def test_readiness_api_refuses_during_practice(qapp):
    vocabulary = GestureVocabulary(("G1", "G2", "G3"))
    window = Window(model=model(vocabulary), studio=True, vocabulary=vocabulary)
    try:
        start_practice(window)

        assert not window.start_readiness_check()
        assert window.practice_attempt is not None
        assert window.routing is not None
        assert window.routing.snapshot.context_id.startswith("practice:")
        assert "practice" in window.readiness_status.text().lower()
    finally:
        window.close()


def test_practice_camera_error_cancels_once_and_saves(monkeypatch, qapp, tmp_path):
    import gestureforge.app as app_module

    monkeypatch.setattr(app_module, "DEFAULT_STUDIO_STATE_FOLDER", tmp_path / "studio")
    workers: list[FakeWorker] = []
    monkeypatch.setattr(app_module, "CaptureWorker", make_worker_factory(workers))
    clock = Clock()
    monkeypatch.setattr(app_module.time, "monotonic", lambda: clock.value + 0.01)
    vocabulary = GestureVocabulary(("G1", "G2", "G3"))
    window = Window(model=model(vocabulary), studio=True, vocabulary=vocabulary)
    try:
        widget = start_practice(window)
        widget.prepare()
        worker = workers[0]
        worker.error = "Camera disconnected"
        worker.finished = True

        window.poll()

        assert window.practice_attempt is None
        assert "practice cancelled" in window.practice_status.text().lower()
        assert len(list((tmp_path / "studio" / "practice").glob("practice-*.json"))) == 1
    finally:
        window.close()


def test_practice_pause_saves_and_restores(monkeypatch, qapp, tmp_path):
    import gestureforge.app as app_module

    monkeypatch.setattr(app_module, "DEFAULT_STUDIO_STATE_FOLDER", tmp_path / "studio")
    vocabulary = GestureVocabulary(("G1", "G2", "G3"))
    window = Window(model=model(vocabulary), studio=True, vocabulary=vocabulary)
    try:
        start_practice(window)

        assert window.pause()

        assert window.practice_attempt is None
        assert window.routing is not None
        assert window.routing.snapshot.context_id == "demo-studio"
        assert list((tmp_path / "studio" / "practice").glob("practice-*.json"))
    finally:
        window.close()


def test_practice_waits_for_old_camera_release_without_scoring_failure(monkeypatch, qapp):
    import gestureforge.app as app_module

    workers: list[FakeWorker] = []
    monkeypatch.setattr(app_module, "CaptureWorker", make_worker_factory(workers))
    clock = Clock()
    monkeypatch.setattr(app_module.time, "monotonic", lambda: clock.value + 0.01)
    vocabulary = GestureVocabulary(("G1", "G2", "G3"))
    window = Window(model=model(vocabulary), studio=True, vocabulary=vocabulary)
    try:
        widget = start_practice(window)
        old_worker = FakeWorker()
        window.worker = old_worker
        widget.prepare()

        assert old_worker.interrupted
        assert window.routing is not None
        assert window._practice_pending_snapshot == window.routing.snapshot
        assert window.practice_attempt is not None
        assert window.practice_attempt.completed == 0
        assert not workers

        old_worker.finished = True
        window.poll()
        assert len(workers) == 1
        assert not window._practice_pending_snapshot
        worker = workers[0]
        for _ in range(5):
            enqueue(window, worker, clock, "NEUTRAL")
        widget.begin()
        clock.advance(0.05)
        for _ in range(8):
            enqueue(window, worker, clock, "G1")
        assert window.session_summary.counts()["simulated"] == 1
    finally:
        window.close()




def test_guest_mode_during_practice_preserves_restored_prior_context(qapp):
    vocabulary = GestureVocabulary(("G1", "G2", "G3"))
    window = Window(model=model(vocabulary), studio=True, vocabulary=vocabulary)
    try:
        assert window.configure_studio(
            context_id="original",
            mode=RoutingMode.LIVE,
            bindings={"G1": Action(ActionType.NEXT)},
        )
        assert window.routing is not None
        original = window.routing.snapshot
        start_practice(window)
        assert window.routing.snapshot.context_id.startswith("practice:")

        assert window.use_studio_guest()

        assert window.practice_attempt is None
        assert window.model is None
        assert window.routing is not None
        assert window.routing_manual_only
        assert window.manual_context_id == "original"
        assert window.manual_mode == RoutingMode.LIVE
        assert window.routing.snapshot.context_id == original.context_id
        assert window.routing.snapshot.mode == original.mode
        assert dict(window.routing.snapshot.bindings) == {"G1": Action(ActionType.NEXT)}
    finally:
        window.close()


def test_manual_actions_blocked_during_practice(qapp):
    vocabulary = GestureVocabulary(("G1", "G2", "G3"))
    window = Window(model=model(vocabulary), studio=True, vocabulary=vocabulary)
    try:
        start_practice(window)
        assert window.practice_attempt is not None

        window.manual_viewer_action(Action(ActionType.NEXT))

        assert window.session_summary.counts()["simulated"] == 0
        assert "finish studio work" in window.feedback.text().lower()
        assert window.practice_attempt is not None
    finally:
        window.close()


def test_terminal_practice_release_does_not_fault_restored_context(monkeypatch, qapp):
    import gestureforge.app as app_module

    workers: list[FakeWorker] = []
    monkeypatch.setattr(app_module, "CaptureWorker", make_worker_factory(workers))
    clock = Clock()
    monkeypatch.setattr(app_module.time, "monotonic", lambda: clock.value + 0.01)
    vocabulary = GestureVocabulary(("G1", "G2", "G3"))
    window = Window(model=model(vocabulary), studio=True, vocabulary=vocabulary)
    try:
        assert window.routing is not None
        previous_context = window.routing.snapshot.context_id
        widget = start_practice(window)
        widget.prepare()
        worker = workers[0]
        widget.stop()

        assert window.practice_attempt is None
        assert window.routing is not None
        assert window.routing.snapshot.context_id == previous_context
        restored_generation = window.routing.snapshot.session_id
        assert worker.interrupted

        worker.finished = True
        window.poll()

        assert window.worker is None
        assert window.routing.snapshot.session_id == restored_generation
        assert window.routing.state == "PAUSED"
        assert not window.routing.last_error
    finally:
        window.close()


def test_practice_completes_full_50_window_host_regression(monkeypatch, qapp, tmp_path):
    import gestureforge.app as app_module

    monkeypatch.setattr(app_module, "DEFAULT_STUDIO_STATE_FOLDER", tmp_path / "studio")
    workers: list[FakeWorker] = []
    monkeypatch.setattr(app_module, "CaptureWorker", make_worker_factory(workers))
    clock = Clock()
    monkeypatch.setattr(app_module.time, "monotonic", lambda: clock.value + 0.01)
    vocabulary = GestureVocabulary(("G1", "G2", "G3"))
    window = Window(model=model(vocabulary), studio=True, vocabulary=vocabulary)
    try:
        assert window.routing is not None
        previous = window.routing.snapshot
        start_practice(window)

        for expected in [*(label for _ in range(10) for label in ("G1", "G2", "G3", "NEUTRAL")), *("NEGATIVE" for _ in range(10))]:
            widget = window.practice_widget
            assert widget is not None
            widget.prepare()
            worker = workers[-1]
            if expected == "NEUTRAL":
                enqueue(window, worker, clock, "NEUTRAL")
                widget.begin()
                clock.advance(0.05)
                feed_window(window, worker, clock, "NEUTRAL")
            elif expected == "NEGATIVE":
                feed_until_armed(window, worker, clock)
                widget.begin()
                clock.advance(0.05)
                feed_window(window, worker, clock, "UNKNOWN", accepted=False, rejection_reason="distance_rejection")
            else:
                feed_until_armed(window, worker, clock)
                widget.begin()
                clock.advance(0.05)
                feed_window(window, worker, clock, expected)
            finish_worker(window, worker)

        assert window.practice_attempt is None
        assert window.routing is not None
        assert window.routing.snapshot.context_id == previous.context_id
        assert window.routing.snapshot.mode == previous.mode
        assert window.routing.state == "PAUSED"
        assert window.readiness_check is None
        assert window.readiness_pass_revision == ""
        assert window.session_summary.counts()["simulated"] == 30
        assert "practice passed" in window.practice_status.text().lower()
        saved = list((tmp_path / "studio" / "practice").glob("practice-*.json"))
        assert len(saved) == 1
    finally:
        window.close()
