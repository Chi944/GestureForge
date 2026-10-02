import os
from dataclasses import replace
from types import SimpleNamespace
from unittest.mock import Mock

import numpy as np
import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from gestureforge.app import Window
from gestureforge.contracts import Action, ActionType, Prediction, RoutingMode
from gestureforge.shortcuts import Target, TargetKind
from gestureforge.vocabulary import GestureVocabulary
from gestureforge.workspace import Binding, Stage


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
    def __init__(self):
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


def model(vocabulary=None):
    vocabulary = vocabulary or GestureVocabulary(("G1", "G2", "G3"))
    return SimpleNamespace(
        predict=lambda _: (vocabulary.action_ids[0], True, ""),
        train_labels=vocabulary.labels,
        model_version="readiness-revision",
        config=SimpleNamespace(algorithm="knn", multiplier=2.0, margin=1.5),
    )


def frame():
    return np.zeros((4, 4, 3), dtype=np.uint8)


class Clock:
    def __init__(self):
        self.value = 100.0
        self.frame_id = 0

    def tick(self, amount=0.16):
        self.value += amount
        self.frame_id += 1
        return self.value


def prediction(window, clock, label, *, accepted=True):
    assert window.routing is not None
    snapshot = window.routing.snapshot
    return Prediction(
        snapshot.session_id,
        snapshot.profile_id,
        clock.frame_id,
        clock.value,
        label,
        accepted,
        model_version=snapshot.model_version,
    )


def poll_label(window, worker, clock, label, *, accepted=True):
    worker.packets.append((frame(), prediction(window, clock, label, accepted=accepted)))
    window.poll()
    clock.tick()


def perform_activation(window, worker, clock, label):
    for _ in range(3):
        poll_label(window, worker, clock, "NEUTRAL")
    for _ in range(4):
        poll_label(window, worker, clock, label)


def start_check(window, monkeypatch):
    import gestureforge.app as app_module

    worker = FakeWorker()
    monkeypatch.setattr(app_module, "CaptureWorker", lambda *args, **kwargs: worker)
    clock = Clock()
    monkeypatch.setattr(app_module.time, "monotonic", lambda: clock.value + 0.01)
    assert window.start_readiness_check()
    assert worker.start.called
    return worker, clock


def test_readiness_passes_six_simulated_events_and_restores_manual_context(monkeypatch, qapp):
    vocabulary = GestureVocabulary(("G1", "G2", "G3"))
    window = Window(model=model(vocabulary), studio=True, vocabulary=vocabulary)
    try:
        assert window.configure_studio(context_id="manual", bindings={})
        previous_session = window.manual_session_id
        worker, clock = start_check(window, monkeypatch)
        assert not window.routing_manual_only
        assert window.routing is not None and window.routing.snapshot.context_id.startswith("readiness:")

        for label in (*vocabulary.action_ids, *vocabulary.action_ids):
            perform_activation(window, worker, clock, label)

        assert window.readiness_check is not None
        assert window.readiness_check.status == "passed"
        assert window.readiness_progress.value() == 6
        assert window.finish_readiness_check()
        assert window.readiness_check is None
        assert window.readiness_pass_revision
        assert window.routing_manual_only
        assert window.manual_context_id == "manual"
        assert window.manual_session_id != previous_session
        assert window.routing is not None and window.routing.state == "PAUSED"
        assert "passed" in window.readiness_status.text().lower()
    finally:
        window.close()


def test_readiness_wrong_action_fails_and_finish_restores(monkeypatch, qapp):
    vocabulary = GestureVocabulary(("G1", "G2", "G3"))
    window = Window(model=model(vocabulary), studio=True, vocabulary=vocabulary)
    try:
        assert window.configure_studio(context_id="partial", bindings={"G1": window._readiness_bindings()["G1"]})
        worker, clock = start_check(window, monkeypatch)
        perform_activation(window, worker, clock, "G2")

        assert window.readiness_check is not None
        assert window.readiness_check.status == "failed"
        assert "Expected G1" in window.readiness_check.reason
        assert not window.finish_readiness_check()
        assert window.readiness_pass_revision == ""
        assert window.routing is not None and window.routing.snapshot.context_id == "partial"
    finally:
        window.close()


def test_readiness_unknown_only_finish_fails_without_routed_events(monkeypatch, qapp):
    vocabulary = GestureVocabulary(("G1", "G2", "G3"))
    window = Window(model=model(vocabulary), studio=True, vocabulary=vocabulary)
    try:
        worker, clock = start_check(window, monkeypatch)
        for _ in range(8):
            poll_label(window, worker, clock, "UNKNOWN")

        assert window.readiness_check is not None
        assert window.readiness_check.completed == 0
        assert not window.finish_readiness_check()
        assert window.readiness_pass_revision == ""
        assert "incomplete" in window.feedback.text().lower()
    finally:
        window.close()



def pass_readiness(window, monkeypatch):
    worker, clock = start_check(window, monkeypatch)
    for label in (*window.vocabulary.action_ids, *window.vocabulary.action_ids):
        perform_activation(window, worker, clock, label)
    assert window.readiness_check is not None
    assert window.readiness_check.status == "passed"
    assert window.finish_readiness_check()
    assert window.readiness_pass_revision
    return window.readiness_pass_revision


def test_readiness_cancel_records_missed_trials_and_restores_after_focus_pause(monkeypatch, qapp):
    vocabulary = GestureVocabulary(("G1", "G2", "G3"))
    window = Window(model=model(vocabulary), studio=True, vocabulary=vocabulary)
    try:
        worker, clock = start_check(window, monkeypatch)
        perform_activation(window, worker, clock, "G1")
        assert window.readiness_check is not None
        assert window.readiness_check.completed == 1

        assert window.pause()

        assert worker.interrupted
        assert window.readiness_check is None
        assert window.readiness_pass_revision == ""
        assert window.routing is not None
        assert not window.routing.snapshot.context_id.startswith("readiness:")
        counts = window.session_summary.counts()
        assert counts["correct"] == 1
        assert counts["missed"] == 5
    finally:
        window.close()


def test_readiness_camera_fault_cancels_partial_check_and_restores(monkeypatch, qapp):
    vocabulary = GestureVocabulary(("G1", "G2", "G3"))
    window = Window(model=model(vocabulary), studio=True, vocabulary=vocabulary)
    try:
        worker, clock = start_check(window, monkeypatch)
        perform_activation(window, worker, clock, "G1")
        worker.error = "Camera disconnected"
        worker.finished = True

        window.poll()

        assert window.worker is None
        assert window.readiness_check is None
        assert window.readiness_pass_revision == ""
        assert window.routing is not None
        assert not window.routing.snapshot.context_id.startswith("readiness:")
        assert window.session_summary.counts()["missed"] == 5
    finally:
        window.close()


def test_readiness_pass_expires_on_direct_authored_binding_change_but_not_stage_navigation(monkeypatch, qapp):
    vocabulary = GestureVocabulary(("G1", "G2", "G3"))
    window = Window(model=model(vocabulary), studio=True, vocabulary=vocabulary)
    try:
        stage = Stage(
            "practice",
            "Practice",
            "Keep rehearsing",
            None,
            (Binding("G1", Action(ActionType.NEXT)),),
        )
        window.workspace = replace(window.workspace, stages=(stage,))
        passed_revision = pass_readiness(window, monkeypatch)

        assert window.reset_runbook_stage(stage, resume=False)
        assert window.readiness_pass_revision == passed_revision
        assert "passed" in window.readiness_status.text().lower()

        assert window.configure_studio(
            context_id=window.workspace.id,
            mode=RoutingMode.PREVIEW,
            bindings={"G1": Action(ActionType.PREVIOUS)},
        )
        assert window.readiness_pass_revision == ""
        assert "not checked" in window.readiness_status.text().lower()
    finally:
        window.close()


def test_readiness_restores_quick_actions_context_after_terminal_result(monkeypatch, qapp):
    vocabulary = GestureVocabulary(("G1", "G2", "G3"))
    window = Window(model=model(vocabulary), studio=True, vocabulary=vocabulary)
    try:
        window.quick_registry.configure(Target("site", "Site", TargetKind.WEBSITE, "https://example.com"))
        window.quick_registry.bind_quick(("site", None, None))
        assert window.use_quick_actions_context()
        quick_context = window.quick_actions_context_id

        worker, clock = start_check(window, monkeypatch)
        perform_activation(window, worker, clock, "G2")

        assert window.readiness_check is not None
        assert window.readiness_check.status == "failed"
        assert window.routing is not None
        assert window.routing.snapshot.context_id == quick_context
        assert window.quick_actions_active
        assert not window.finish_readiness_check()
    finally:
        window.close()


class FailingTrace:
    frame_count = 1

    def __init__(self):
        self.fail = True
        self.saved = 0

    def append(self, prediction, processed_at):
        self.frame_count += 1

    def save(self, path):
        if self.fail:
            raise OSError("disk full")
        self.saved += 1


def test_readiness_trace_save_failure_retains_recoverable_prior_context(monkeypatch, qapp, tmp_path):
    vocabulary = GestureVocabulary(("G1", "G2", "G3"))
    window = Window(model=model(vocabulary), studio=True, vocabulary=vocabulary)
    try:
        assert window.configure_studio(context_id="manual", bindings={})
        worker, clock = start_check(window, monkeypatch)
        trace = FailingTrace()
        window.evaluation_trace = trace  # type: ignore[assignment]
        window.trace_path = tmp_path / "trace.json"

        perform_activation(window, worker, clock, "G2")

        assert window.readiness_check is not None
        assert window.readiness_check.status == "failed"
        assert window._readiness_previous is not None
        assert window.routing is not None
        assert window.routing.snapshot.context_id.startswith("readiness:")
        assert not window.finish_readiness_check()
        assert window._readiness_previous is not None
        assert window.readiness_check is not None

        trace.fail = False
        assert not window.finish_readiness_check()
        assert trace.saved == 1
        assert window.readiness_check is None
        assert window._readiness_previous is None
        assert window.routing_manual_only
        assert window.manual_context_id == "manual"
        assert window.readiness_pass_revision == ""
    finally:
        window.close()



def test_enrolment_tab_cancels_active_readiness_and_restores_manual_context(monkeypatch, qapp):
    vocabulary = GestureVocabulary(("G1", "G2", "G3"))
    window = Window(model=model(vocabulary), studio=True, vocabulary=vocabulary)
    try:
        assert window.configure_studio(context_id="manual", bindings={})
        worker, clock = start_check(window, monkeypatch)
        perform_activation(window, worker, clock, "G1")

        window.deck_tabs.setCurrentWidget(window.enrolment_widget)
        window.on_studio_tab_changed(window.deck_tabs.currentIndex())

        assert worker.interrupted
        assert window.readiness_check is None
        assert window.readiness_pass_revision == ""
        assert window.routing_manual_only
        assert window.manual_context_id == "manual"
        assert window.routing is not None and window.routing.state == "PAUSED"
    finally:
        window.close()


def test_readiness_retry_refuses_when_previous_context_cannot_restore(monkeypatch, qapp, tmp_path):
    vocabulary = GestureVocabulary(("G1", "G2", "G3"))
    window = Window(model=model(vocabulary), studio=True, vocabulary=vocabulary)
    try:
        assert window.configure_studio(context_id="manual", bindings={})
        worker, clock = start_check(window, monkeypatch)
        trace = FailingTrace()
        window.evaluation_trace = trace  # type: ignore[assignment]
        window.trace_path = tmp_path / "trace.json"
        perform_activation(window, worker, clock, "G2")
        previous = window._readiness_previous
        assert previous is not None
        assert not window.finish_readiness_check()

        assert not window.start_readiness_check()

        assert window._readiness_previous == previous
        assert window.readiness_check is not None
        assert window.routing is not None
        assert window.routing.snapshot.context_id.startswith("readiness:")
    finally:
        window.close()


def test_configure_studio_implicit_mode_change_restores_manual_before_apply(monkeypatch, qapp):
    vocabulary = GestureVocabulary(("G1", "G2", "G3"))
    window = Window(model=model(vocabulary), studio=True, vocabulary=vocabulary)
    try:
        assert window.configure_studio(context_id="manual", bindings={})
        worker, clock = start_check(window, monkeypatch)
        perform_activation(window, worker, clock, "G1")

        assert window.configure_studio(mode=RoutingMode.REHEARSAL)

        assert worker.interrupted
        assert window.readiness_check is None
        assert window.routing_manual_only
        assert window.manual_context_id == "manual"
        assert window.manual_mode == RoutingMode.REHEARSAL
        assert window.routing is not None and not window.routing.snapshot.context_id.startswith("readiness:")
    finally:
        window.close()


def test_cosmetic_workspace_and_target_label_changes_preserve_completed_pass(monkeypatch, qapp):
    vocabulary = GestureVocabulary(("G1", "G2", "G3"))
    workspace = None
    window = Window(model=model(vocabulary), studio=True, vocabulary=vocabulary)
    try:
        window.quick_registry.configure(Target("site", "Site", TargetKind.WEBSITE, "https://example.com"))
        window.quick_registry.bind_quick(("site", None, None))
        passed_revision = pass_readiness(window, monkeypatch)
        workspace = replace(window.workspace, title="Renamed Workspace")

        assert window.use_studio_workspace(workspace, reason="Workspace renamed")
        assert window.readiness_pass_revision == passed_revision

        candidate = window.quick_registry.copy()
        candidate.configure(Target("site", "Renamed Site", TargetKind.WEBSITE, "https://example.com"))
        window.quick_registry.replace_with(candidate)
        window.accept_quick_bindings_change(tuple())
        assert window.readiness_pass_revision == passed_revision
    finally:
        window.close()
