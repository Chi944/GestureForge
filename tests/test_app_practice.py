import json
import os
from dataclasses import replace
from types import SimpleNamespace
from typing import cast
from unittest.mock import Mock

import numpy as np
import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from gestureforge.app import HistoricalPracticeReview, Window
from gestureforge.contracts import Action, ActionType, Prediction, RoutingMode
from gestureforge.practice import DIAGNOSTIC_PROTOCOL_VERSION, PracticeResult, PracticeTrial
from gestureforge.practice_widget import PersonalRehearsalWidget
from gestureforge.profiles import ProfileStore
from gestureforge.session_summary import Outcome
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


class FinishedModelLoader:
    def __init__(self, *, kind="profile", profile_id=None, error="", result=None):
        self.kind = kind
        self.profile_id = profile_id
        self.error = error
        self.result = result
        self.joined = False

    def is_alive(self):
        return False

    def join(self):
        self.joined = True


class AliveModelLoader(FinishedModelLoader):
    def __init__(self, load, *, kind="profile", profile_id=None):
        super().__init__(kind=kind, profile_id=profile_id)
        self.load = load
        self.started = False
        self.alive = True

    def start(self):
        self.started = True

    def is_alive(self):
        return self.alive

    def finish(self, *, error="", result=None):
        self.error = error
        self.result = result
        self.alive = False


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


def diagnostic_trial(expected="G1", outcome="correct", *, actions=None, coverage=True):
    if actions is None:
        actions = (expected,) if expected not in {"NEUTRAL", "NEGATIVE"} and outcome == "correct" else ()
    return PracticeTrial(
        expected, 1, "Recorded diagnostic cue", "diagnostic-session", 0.0, 5.0, outcome,
        actions, tuple(f"diagnostic-event-{index}" for index in range(len(actions))),
        expected == "NEUTRAL" and outcome == "correct", 50, (), coverage, "Recorded diagnostic reason",
    )


def diagnostic_result(trials, *, status="cancelled"):
    poses = ("G1", "G2", "G3", "NEUTRAL")
    return PracticeResult(
        "diagnostic-attempt", "behavior-v1", DIAGNOSTIC_PROTOCOL_VERSION, "profile", "model",
        status, "Single-pose diagnostic complete. Full 50-window rehearsal not performed.",
        tuple(trials),
        tuple((pose, sum(row.expected == pose and row.outcome == "correct" for row in trials)) for pose in poses),
        sum(len(row.actions) for row in trials if row.expected == "NEGATIVE"), (),
    )


def diagnostic_review(window, result, tmp_path):
    saved_path = tmp_path / "practice-diagnostic.json"
    saved_path.write_text("{}", encoding="utf-8")
    assert window.routing is not None
    return HistoricalPracticeReview(
        result,
        tuple(window.session_summary.outcomes),
        window.routing.snapshot.context_id,
        tuple(window.routing.snapshot.bindings),
        tuple(sorted(window.session_summary.scope.items())),
        saved_path,
    )


@pytest.mark.parametrize(("outcome", "expected_status", "expected_correct"), [
    ("correct", "diagnostic completed", "correct 1/1"),
    ("missed", "diagnostic completed", "correct 0/1"),
    ("interrupted", "diagnostic interrupted", "correct 0/1"),
])
def test_single_pose_diagnostic_review_uses_one_window_scope(qapp, tmp_path, outcome, expected_status, expected_correct):
    vocabulary = GestureVocabulary(("G1", "G2", "G3"))
    window = Window(model=model(vocabulary), studio=True, vocabulary=vocabulary)
    try:
        result = diagnostic_result([diagnostic_trial("G1", outcome, coverage=outcome != "interrupted")])
        review = diagnostic_review(window, result, tmp_path)

        text = window._practice_review_text(review).lower()

        assert expected_status in text
        assert "serialized status: cancelled" in text
        assert f"window outcome: g1 {outcome}" in text
        assert expected_correct in text
        assert "windows recorded: 1/1" in text
        assert "completed five-second windows: 1/1" in text if outcome != "interrupted" else "completed five-second windows: 0/1" in text
        assert "g2: not assessed" in text
        assert "g3: not assessed" in text
        assert "neutral: not assessed" in text
        assert "negative windows: not assessed" in text
        assert "full 50-window rehearsal not performed" in text
        assert "recorded 0/10" not in text
        assert "unattempted 49" not in text
        assert "correct 0/10" not in text
    finally:
        window.close()


def test_single_pose_diagnostic_finish_banner_does_not_look_like_full_pass(qapp):
    vocabulary = GestureVocabulary(("G1", "G2", "G3"))
    window = Window(model=model(vocabulary), studio=True, vocabulary=vocabulary)
    try:
        result = diagnostic_result([diagnostic_trial("NEUTRAL", "missed")])

        assert window._finish_practice_rehearsal(result)

        text = window.practice_status.text().lower()
        assert "practice diagnostic completed" in text
        assert "neutral missed (0/1 correct)" in text
        assert "full 50-window rehearsal not performed" in text
        assert "other poses and negative windows were not assessed" in text
        assert "no readiness credit" in text
        assert "neutral 0/10" not in text
        assert "practice passed" not in text
    finally:
        window.close()


def test_practice_status_matches_initial_model_availability(qapp):
    vocabulary = GestureVocabulary(("G1", "G2", "G3"))
    ready_window = Window(model=model(vocabulary), studio=True, vocabulary=vocabulary)
    guest_window = Window(studio=True)
    try:
        assert "practice ready" in ready_window.practice_status.text().lower()
        assert "consent" in ready_window.practice_status.text().lower()
        assert "unavailable" in guest_window.practice_status.text().lower()
    finally:
        ready_window.close()
        guest_window.close()


def test_open_practice_entrypoint_selects_practice_without_starting(qapp):
    vocabulary = GestureVocabulary(("G1", "G2", "G3"))
    window = Window(model=model(vocabulary), studio=True, vocabulary=vocabulary)
    try:
        window.deck_tabs.setCurrentWidget(window.profile_selector)
        window.practice_consent.setChecked(False)

        window.open_practice_button.click()
        qapp.processEvents()

        assert window.deck_tabs.currentWidget() is window.practice_page
        assert window.practice_attempt is None
        assert not window.practice_consent.isChecked()
        assert "practice ready" in window.practice_status.text().lower()
    finally:
        window.close()


def test_practice_status_pauses_during_actual_dataset_and_profile_loads(monkeypatch, qapp):
    import gestureforge.app as app_module

    loaders: list[AliveModelLoader] = []

    def loader_factory(*args, **kwargs):
        loader = AliveModelLoader(*args, **kwargs)
        loaders.append(loader)
        return loader

    class Store:
        def load(self, profile_id):
            raise AssertionError("alive fake loader should not run the profile load")

    monkeypatch.setattr(app_module, "ModelLoadWorker", loader_factory)
    vocabulary = GestureVocabulary(("G1", "G2", "G3"))
    window = Window(model=model(vocabulary), studio=True, vocabulary=vocabulary)
    try:
        assert "practice ready" in window.practice_status.text().lower()

        assert window.load_studio_dataset("personal.json")
        assert loaders[-1].kind == "dataset"
        assert loaders[-1].started
        assert "paused while" in window.practice_status.text().lower()
        window.model_loader = None

        profile_id = "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
        assert window.load_studio_profile(cast(ProfileStore, Store()), profile_id)
        assert loaders[-1].kind == "profile"
        assert loaders[-1].profile_id == profile_id
        assert loaders[-1].started
        assert "paused while" in window.practice_status.text().lower()
    finally:
        window.model_loader = None
        window.close()


def test_practice_status_follows_guest_and_failed_profile_load_without_losing_active_model(monkeypatch, qapp):
    import gestureforge.app as app_module

    loaders: list[AliveModelLoader] = []

    def loader_factory(*args, **kwargs):
        loader = AliveModelLoader(*args, **kwargs)
        loaders.append(loader)
        return loader

    class Store:
        def load(self, profile_id):
            raise AssertionError("alive fake loader should not run the profile load")

    monkeypatch.setattr(app_module, "ModelLoadWorker", loader_factory)
    vocabulary = GestureVocabulary(("G1", "G2", "G3"))
    window = Window(model=model(vocabulary), studio=True, vocabulary=vocabulary)
    try:
        assert "practice ready" in window.practice_status.text().lower()

        profile_id = "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
        assert window.load_studio_profile(cast(ProfileStore, Store()), profile_id)
        failed = loaders[-1]
        assert "paused while" in window.practice_status.text().lower()
        failed.finish(error="ValueError: profile checksum mismatch")
        window.poll_model_load()

        assert failed.joined
        assert window.model is not None
        assert "practice ready" in window.practice_status.text().lower()
        assert "profile not loaded" in window.notice.text().lower()

        assert window.use_studio_guest()
        assert window.model is None
        assert "unavailable" in window.practice_status.text().lower()
    finally:
        window.close()


def test_practice_availability_refresh_does_not_overwrite_diagnostic_status(qapp):
    vocabulary = GestureVocabulary(("G1", "G2", "G3"))
    window = Window(model=model(vocabulary), studio=True, vocabulary=vocabulary)
    try:
        diagnostic = "Practice results remain in memory. Fix storage and retry Save before changing Studio context."
        window._set_practice_status(diagnostic)

        window.render_studio_status()

        assert window.practice_status.text() == diagnostic
    finally:
        window.close()


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
        assert window._practice_review is not None
        assert "interrupted 0" in window.practice_review_label.text().lower()
        assert "latest saved practice" in window.practice_review_label.text().lower()
        assert window.routing is not None
        assert window.routing.snapshot.context_id == previous.context_id
        assert window.routing.snapshot.mode == previous.mode
        assert window._practice_review is not None
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
        assert "practice ready" in window.practice_status.text().lower()

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
        assert window._practice_review is None
        close_event = FakeCloseEvent()
        window.closeEvent(close_event)
        assert close_event.ignored

        monkeypatch.setattr(window.practice_attempt, "save", original_save)
        widget.save()
        assert window._finish_practice_rehearsal()
        assert window.practice_attempt is None
        assert window._practice_review is not None
        assert "latest saved practice" in window.practice_review_label.text().lower()
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
        assert window._practice_review is None
        retained_previous = window._practice_previous
        assert "prior studio context was not restored" in window.practice_status.text().lower()
        assert list((tmp_path / "studio" / "practice").glob("practice-*.json"))

        window.manual_context_id = "partial-restore-noise"
        assert window.pause()

        assert window._practice_previous is None
        assert window.practice_attempt is None
        assert window.practice_widget is None
        assert window.routing is not None
        assert retained_previous[1] == previous.context_id
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



def test_practice_review_preserves_interrupted_preparation(monkeypatch, qapp, tmp_path):
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
        widget.stop()

        assert window._practice_review is not None
        assert window._practice_review.result.trials[0].outcome == "interrupted"
        assert "interrupted 1" in window.practice_review_label.text().lower()
        assert list((tmp_path / "studio" / "practice").glob("practice-*.json"))
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


def test_practice_footer_keeps_neutral_until_begin_then_follows_window(monkeypatch, qapp):
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
        feed_until_armed(window, worker, clock)
        assert "keep NEUTRAL" in window.detail.text()
        assert "Begin" in window.detail.text()
        assert "hold a mapped gesture" not in window.detail.text()

        widget.begin_button.click()
        window.poll()  # Phase guidance updates even without a new camera packet.
        assert "Hold G1" in window.detail.text()
        assert "remaining" in window.detail.text()
        assert "keep NEUTRAL" not in window.detail.text()
        clock.advance(0.05)
        feed_window(window, worker, clock, "G1")
        assert "Prepare next trial" in window.detail.text()
    finally:
        window.close()


@pytest.mark.parametrize("cause", ["pause", "focus", "stop", "close", "hidden", "settings"])
def test_practice_saved_interruption_reason_identifies_trigger(monkeypatch, qapp, tmp_path, cause):
    from PySide6.QtCore import QEvent
    from PySide6.QtGui import QHideEvent
    import gestureforge.app as app_module

    monkeypatch.setattr(app_module, "DEFAULT_STUDIO_STATE_FOLDER", tmp_path / "studio")
    monkeypatch.setattr(app_module, "CaptureWorker", make_worker_factory([]))
    vocabulary = GestureVocabulary(("G1", "G2", "G3"))
    window = Window(model=model(vocabulary), studio=True, vocabulary=vocabulary)
    try:
        widget = start_practice(window)
        if cause == "pause":
            window.pause()
            expected = "camera paused"
        elif cause == "focus":
            monkeypatch.setattr(window, "isActiveWindow", lambda: False)
            window.changeEvent(QEvent(QEvent.Type.ActivationChange))
            expected = "focus lost"
        elif cause == "stop":
            widget.stop_button.click()
            expected = "Stop rehearsal"
        elif cause == "close":
            window.closeEvent(FakeCloseEvent())
            expected = "Studio closed"
        elif cause == "hidden":
            widget.prepare()
            widget.hideEvent(QHideEvent())
            expected = "Practice tab hidden"
        else:
            window.configure_studio(mode=RoutingMode.PREVIEW)
            expected = "settings changed"
        saved = list((tmp_path / "studio" / "practice").glob("practice-*.json"))
        assert len(saved) == 1
        payload = json.loads(saved[0].read_text())
        assert expected in payload["reason"]
        assert payload["status"] == "cancelled"
        assert window.routing is not None
        assert window._gesture_live_ready(window.routing.snapshot) is False
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
        counts = window.session_summary.counts()
        assert counts["simulated"] == 30
        assert counts["launch_requested"] == 0
        assert counts["acknowledged_completion"] == 0
        assert "practice passed" in window.practice_status.text().lower()
        assert "Open Session summary" in window.practice_status.text()
        saved = list((tmp_path / "studio" / "practice").glob("practice-*.json"))
        assert len(saved) == 1
        review = window._practice_review
        assert review is not None
        assert review.saved_path == saved[0]
        assert len(review.result.trials) == 50
        review_text = window.practice_review_label.text().lower()
        assert "latest saved practice" in review_text
        assert "windows recorded: 50/50" in review_text
        assert "completed five-second windows: 50/50" in review_text
        assert "unattempted 0" in review_text
        assert "coverage failures 0" in review_text
        assert "scope revision: revision-" in review_text
        assert "demo studio" not in review_text
        assert "matched simulated 30" in review_text
        assert "missing 0" in review_text
        assert "duplicate 0" in review_text
        assert "mismatch 0" in review_text
        assert "unexpected 0" in review_text
        assert "launch requests 0" in review_text
        assert "saved full trial export" in review_text
        assert "next steps for this recorded attempt" in review_text
        assert "does not enable live gestures" in review_text
        export_path = tmp_path / "summary-export.json"
        window.session_summary.export(export_path)
        exported = json.loads(export_path.read_text(encoding="utf-8"))
        assert set(exported) == {"schema_version", "scope", "counts", "outcomes", "trials", "completed_stages"}
        assert "practice" not in exported

        base = window._practice_review_reconciliation(review)
        assert base["matched"] == 30
        unrelated = Outcome("unrelated-event", "unrelated-session", "gesture", "simulated", Action(ActionType.NEXT), "", "other-context", review.result.model_version)
        unrelated_review = app_module.HistoricalPracticeReview(review.result, review.outcomes + (unrelated,), review.context_id, review.bindings, review.scope, review.saved_path)
        assert window._practice_review_reconciliation(unrelated_review)["unexpected"] == 0
        expected_trial = next(trial for trial in review.result.trials if trial.event_ids)
        expected_event = expected_trial.event_ids[0]
        expected_session = expected_trial.session_id
        matching = [outcome for outcome in review.outcomes if outcome.event_id == expected_event and outcome.session_id == expected_session]
        assert len(matching) == 1
        without_match = app_module.HistoricalPracticeReview(
            review.result,
            tuple(outcome for outcome in review.outcomes if outcome not in matching),
            review.context_id, review.bindings, review.scope, review.saved_path,
        )
        assert window._practice_review_reconciliation(without_match)["missing"] == 1
        assert "Resolve the event reconciliation differences" in window._practice_review_guidance(without_match)[0]
        duplicate_review = app_module.HistoricalPracticeReview(review.result, review.outcomes + (matching[0],), review.context_id, review.bindings, review.scope, review.saved_path)
        assert window._practice_review_reconciliation(duplicate_review)["duplicate"] == 1
        wrong_status = replace(matching[0], status="failed")
        wrong_review = app_module.HistoricalPracticeReview(review.result, tuple(
            wrong_status if outcome is matching[0] else outcome for outcome in review.outcomes
        ), review.context_id, review.bindings, review.scope, review.saved_path)
        assert window._practice_review_reconciliation(wrong_review)["mismatch"] == 1
        assert "Resolve the event reconciliation differences" in window._practice_review_guidance(wrong_review)[0]
        wrong_source = replace(matching[0], source="manual")
        wrong_source_review = app_module.HistoricalPracticeReview(review.result, tuple(
            wrong_source if outcome is matching[0] else outcome for outcome in review.outcomes
        ), review.context_id, review.bindings, review.scope, review.saved_path)
        assert window._practice_review_reconciliation(wrong_source_review)["mismatch"] == 1
        wrong_action = replace(matching[0], action=Action(ActionType.PREVIOUS))
        wrong_action_review = app_module.HistoricalPracticeReview(review.result, tuple(
            wrong_action if outcome is matching[0] else outcome for outcome in review.outcomes
        ), review.context_id, review.bindings, review.scope, review.saved_path)
        assert window._practice_review_reconciliation(wrong_action_review)["mismatch"] == 1
        wrong_model = replace(matching[0], model_version="other-model")
        wrong_model_review = app_module.HistoricalPracticeReview(review.result, tuple(
            wrong_model if outcome is matching[0] else outcome for outcome in review.outcomes
        ), review.context_id, review.bindings, review.scope, review.saved_path)
        assert window._practice_review_reconciliation(wrong_model_review)["mismatch"] == 1
        duplicate_expected_trials = list(review.result.trials)
        duplicate_expected_trials[0] = replace(duplicate_expected_trials[0], event_ids=(expected_event, expected_event), actions=(expected_trial.actions[0], expected_trial.actions[0]))
        duplicate_expected_result = replace(review.result, trials=tuple(duplicate_expected_trials))
        duplicate_expected_review = app_module.HistoricalPracticeReview(duplicate_expected_result, review.outcomes, review.context_id, review.bindings, review.scope, review.saved_path)
        duplicate_expected_counts = window._practice_review_reconciliation(duplicate_expected_review)
        assert duplicate_expected_counts["duplicate"] >= 1
        assert duplicate_expected_counts["matched"] == 29
        unexpected = Outcome("unexpected-event", expected_session, "gesture", "simulated", Action(ActionType.NEXT), "", review.context_id, review.result.model_version)
        unexpected_review = app_module.HistoricalPracticeReview(review.result, review.outcomes + (unexpected,), review.context_id, review.bindings, review.scope, review.saved_path)
        assert window._practice_review_reconciliation(unexpected_review)["unexpected"] == 1
        window._reset_session_summary()
        assert window._practice_review is review
        assert "historical scope differs" in window.practice_review_label.text().lower()
        window.profile = "changed-profile"
        window.model.model_version = "changed-version"
        window.render_studio_status()
        changed_text = window.practice_review_label.text().lower()
        assert "historical behavior differs" in changed_text
        assert review.result.profile_id in changed_text
        assert window.practice_review_label.wordWrap()
        assert window.practice_review_label.parent() is window.summary_widget
        window.show()
        window.deck_tabs.setCurrentWidget(window.summary_widget)
        qapp.processEvents()
        for width, height in ((900, 620), (1100, 850)):
            window.resize(width, height)
            qapp.processEvents()
            label = window.practice_review_label
            assert window.studio_scroll.horizontalScrollBar().maximum() == 0
            assert (
                label.height() >= label.heightForWidth(label.width())
                or window.studio_scroll.verticalScrollBar().maximum() > 0
            )
    finally:
        window.close()
