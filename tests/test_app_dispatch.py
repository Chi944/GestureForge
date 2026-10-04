import os
import json
from pathlib import Path
from unittest.mock import Mock

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from gestureforge.app import Window
from gestureforge.contracts import Action, ActionType, RoutingMode
from gestureforge.shortcuts import Target, TargetKind
from gestureforge.workspace import Stage, Workspace


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


class FakeLauncher:
    def __init__(self):
        self.calls = []
        self.error = None

    def open(self, target, resolved):
        if self.error is not None:
            raise self.error
        self.calls.append((target.id, target.value, resolved))


class StuckWorker:
    def __init__(self):
        self.interrupted = False

    def requestInterruption(self):
        self.interrupted = True

    def wait(self, milliseconds=None):
        return False

    def isFinished(self):
        return False

    def isInterruptionRequested(self):
        return self.interrupted


def window_with_dispatcher():
    window = Window(model=object(), studio=True)
    launcher = FakeLauncher()
    window.dispatcher.launcher = launcher
    return window, launcher


def bind_builtin(window, target_id="calculator", value="calculator"):
    window.quick_registry.configure(Target(target_id, target_id.title(), TargetKind.BUILTIN, value))
    window.quick_registry.bind_quick((target_id, None, None))
    return Action(ActionType.OPEN_SHORTCUT, target_id)


def set_live(window):
    assert window.configure_studio(
        context_id=window.workspace.id,
        mode=RoutingMode.LIVE,
        bindings={"NEXT": Action(ActionType.NEXT), "PREVIOUS": Action(ActionType.PREVIOUS)},
    )


def test_preview_manual_requests_simulate_without_moving_or_launching(qapp):
    window, launcher = window_with_dispatcher()
    try:
        before = window.viewer.position
        window.manual_viewer_action(Action(ActionType.NEXT))
        assert window.viewer.position == before
        assert window.session_summary.counts()["simulated"] == 1
        assert "would show next card" in window.feedback.text()

        action = bind_builtin(window)
        window.manual_quick_action(action)
        assert launcher.calls == []
        assert window.session_summary.counts()["simulated"] == 2
    finally:
        window.close()


def test_studio_footer_next_uses_dispatcher_preview_and_live(qapp):
    window, _ = window_with_dispatcher()
    try:
        window.next_card()
        assert window.viewer.position == 0
        assert window.session_summary.counts()["simulated"] == 1

        set_live(window)
        window.next_card()
        assert window.viewer.position == 1
        assert window.session_summary.counts()["applied"] == 1
    finally:
        window.close()


def test_explicit_live_manual_viewer_and_quick_action_use_shared_dispatcher(qapp):
    window, launcher = window_with_dispatcher()
    try:
        set_live(window)
        window.manual_viewer_action(Action(ActionType.NEXT))
        assert window.viewer.position == 1
        assert window.session_summary.counts()["applied"] == 1

        action = bind_builtin(window)
        window.manual_quick_action(action)
        assert launcher.calls == [("calculator", "calculator", "calculator")]
        assert window.session_summary.counts()["launch_requested"] == 1
    finally:
        window.close()


def test_dispatcher_duplicate_gate_persists_across_summary_reset(qapp):
    window, _ = window_with_dispatcher()
    try:
        set_live(window)
        assert window._dispatch_action(Action(ActionType.NEXT), event_id="same", source="Manual viewer").status == "applied"
        assert window.viewer.position == 1
        window._reset_session_summary()

        outcome = window._dispatch_action(Action(ActionType.NEXT), event_id="same", source="Manual viewer")
        assert outcome.status == "duplicate"
        assert window.viewer.position == 1
        assert window.session_summary.counts()["duplicate"] == 1
    finally:
        window.close()


def test_live_shortcut_honors_pause_failure_before_os_side_effect(monkeypatch, qapp):
    window, launcher = window_with_dispatcher()
    try:
        set_live(window)
        action = bind_builtin(window)
        monkeypatch.setattr(window, "pause", Mock(return_value=False))

        window.manual_quick_action(action)

        assert launcher.calls == []
        assert window.session_summary.counts()["failed"] == 1
        assert "Save the current trace" in window.feedback.text()
    finally:
        window.close()


def test_camera_release_failure_consumes_request_and_requires_fresh_retry(qapp):
    window, launcher = window_with_dispatcher()
    try:
        set_live(window)
        action = bind_builtin(window, "camera", "camera")
        worker = StuckWorker()
        window.worker = worker

        outcome = window._dispatch_action(action, event_id="camera-request", source="Quick Action")
        assert outcome.status == "failed"
        assert worker.interrupted
        assert launcher.calls == []

        window.worker = None
        duplicate = window._dispatch_action(action, event_id="camera-request", source="Quick Action")
        assert duplicate.status == "duplicate"
        fresh = window._dispatch_action(action, event_id="camera-request-2", source="Quick Action")
        assert fresh.status == "launch_requested"
        assert launcher.calls == [("camera", "camera", "camera")]
    finally:
        window.close()


def test_dispatch_rejects_profile_busy_enrolment_tab_and_closing(monkeypatch, qapp):
    window, _ = window_with_dispatcher()
    try:
        set_live(window)
        monkeypatch.setattr(window, "_profile_selector_change_blocked", lambda: True)
        assert window._dispatch_action(Action(ActionType.NEXT), event_id="busy") is None
        assert window.viewer.position == 0
        monkeypatch.setattr(window, "_profile_selector_change_blocked", lambda: False)

        window.deck_tabs.setCurrentWidget(window.enrolment_widget)
        assert window._dispatch_action(Action(ActionType.NEXT), event_id="enrol") is None
        assert window.viewer.position == 0

        window.deck_tabs.setCurrentWidget(window.manual_viewer)
        window._closing = True
        assert window._dispatch_action(Action(ActionType.NEXT), event_id="closing") is None
        assert window.viewer.position == 0
        window._closing = False
    finally:
        window.close()


def test_dispatcher_uses_replaced_workspace_viewer_and_summary(qapp):
    window, _ = window_with_dispatcher()
    try:
        replacement = Workspace("replacement", "Replacement", window.viewer.deck)
        assert window.use_studio_workspace(replacement, reason="Workspace replaced")
        set_live(window)

        window.manual_viewer_action(Action(ActionType.NEXT))

        assert window.workspace.id == "replacement"
        assert window.viewer.position == 1
        assert window.dispatcher.viewer is window.viewer
        assert window.dispatcher.summary is window.session_summary
        assert window.session_summary.counts()["applied"] == 1
    finally:
        window.close()


def test_short_readiness_pass_does_not_unlock_live_gesture_start(qapp, monkeypatch):
    window, _ = window_with_dispatcher()
    try:
        monkeypatch.setattr(window, "isActiveWindow", lambda: True)
        window.selected_profile_id = window.profile
        window.selected_profile_name = "Profile"
        window.readiness_pass_revision = window._readiness_behavior_revision()
        set_live(window)

        assert not window._can_start_studio_camera()
        window.start_camera()

        assert window.worker is None
        assert "full personal Practice pass" in window.notice.text()
        assert "full personal Practice pass" in window.studio_status.text()
    finally:
        window.close()


@pytest.mark.parametrize("finished", [False, True])
def test_camera_launch_requires_completed_worker_acknowledgement(qapp, finished):
    window, launcher = window_with_dispatcher()
    try:
        set_live(window)
        action = bind_builtin(window, "camera", "camera")
        worker = Mock()
        worker.wait.return_value = True
        worker.isFinished.return_value = finished
        window.worker = worker
        window.manual_quick_action(action)
        worker.wait.assert_called_once_with(750)
        if finished:
            assert window.worker is None
            assert launcher.calls == [("camera", "camera", "camera")]
        else:
            assert window.worker is worker
            assert launcher.calls == []
            assert window.session_summary.counts()["failed"] == 1
    finally:
        window.worker = None
        window.close()


def test_runbook_continue_obeys_mode_and_stage_changes_stay_paused(qapp, monkeypatch):
    window, _ = window_with_dispatcher()
    try:
        workspace = Workspace("stages", "Stages", stages=(
            Stage("first", "First", "First step", None, ()),
            Stage("second", "Second", "Second step", None, ()),
        ))
        assert window.use_studio_workspace(workspace, reason="Test stages")
        start = Mock()
        monkeypatch.setattr(window, "start_camera", start)
        window.manual_runbook_action(Action(ActionType.ADVANCE_STAGE))
        assert window.runbook.position == 0
        assert window.session_summary.counts()["simulated"] == 1
        assert window.configure_studio(mode=RoutingMode.LIVE)
        window.runbook.paused = False
        window.manual_runbook_action(Action(ActionType.ADVANCE_STAGE))
        assert window.runbook.position == 1
        assert window.runbook.paused
        assert window.routing.state == "PAUSED"
        window.runbook.paused = False
        window.previous_runbook_stage()
        assert window.runbook.position == 0
        assert window.runbook.paused
        start.assert_not_called()
    finally:
        window.close()


def test_full_summary_stops_manual_request_before_effect(qapp, monkeypatch):
    window, launcher = window_with_dispatcher()
    try:
        set_live(window)
        action = bind_builtin(window)
        monkeypatch.setattr(window.session_summary, "ensure_capacity", Mock(side_effect=ValueError("record limit reached")))
        window.manual_quick_action(action)
        assert launcher.calls == []
        assert "record limit" in window.feedback.text().lower()
    finally:
        window.close()


@pytest.mark.parametrize("mode", [RoutingMode.PREVIEW, RoutingMode.LIVE])
def test_quick_actions_activation_text_and_rebinding_match_mode(qapp, mode):
    window, launcher = window_with_dispatcher()
    try:
        bind_builtin(window)
        assert window.configure_studio(mode=mode)
        assert window.use_quick_actions_context()
        if mode == RoutingMode.LIVE:
            assert "LIVE manual" in window.feedback.text()
            assert "Start camera" not in window.quick_actions_widget.status.text()
        else:
            assert "simulate" in window.feedback.text()
        previous = window.routing.snapshot
        window.quick_actions_widget._publish(window.quick_registry.copy())
        assert window.routing_manual_only
        assert window.manual_context_id == window.quick_actions_context_id
        assert window.routing.snapshot.session_id != previous.session_id
        assert not window.quick_actions_active
        assert window.routing.state == "PAUSED"
        assert launcher.calls == []
    finally:
        window.close()


def test_invalid_target_test_records_bounded_failure_and_honors_host_guards(qapp, monkeypatch):
    window, launcher = window_with_dispatcher()
    try:
        widget = window.quick_actions_widget
        widget.target_id.setText("C:/private/unbound-reference.txt")
        widget._test()
        outcome = window.session_summary.outcomes[-1]
        assert outcome.status == "failed"
        assert outcome.source == "manual"
        assert outcome.action is None
        assert "private" not in outcome.reason
        assert launcher.calls == []
        with monkeypatch.context() as patch:
            patch.setattr(window.session_summary, "ensure_capacity", Mock(side_effect=ValueError("record limit reached")))
            widget._test()
            assert len(window.session_summary.outcomes) == 1
            assert "record limit" in window.feedback.text()
            window._closing = True
            widget._test()
            assert len(window.session_summary.outcomes) == 1
            assert "finish Studio work" in window.feedback.text()
            window._closing = False
    finally:
        window.close()


def test_harbor_guest_manual_workflow_recovers_without_context_loss_or_replay(qapp, tmp_path):
    window = Window(model=None, studio=True)
    launcher = FakeLauncher()
    window.dispatcher.launcher = launcher
    reference = tmp_path / "private-reference.txt"
    reference.write_text("Fictional reference", encoding="utf-8")
    try:
        assert window.load_studio_workspace(Path(__file__).resolve().parents[1] / "assets/harbor_workspace.json")
        assert window.runbook is not None and window.routing is not None
        assert window.configure_studio(mode=RoutingMode.LIVE)
        candidate = window.quick_registry.copy()
        for target in (
            Target("calculator", "Calculator", TargetKind.BUILTIN, "calculator"),
            Target("product-reference", "Reference", TargetKind.FILE, str(reference)),
            Target("resource-folder", "Resources", TargetKind.FOLDER, str(tmp_path)),
            Target("recovery-reference", "Recovery", TargetKind.FILE, str(reference)),
        ):
            candidate.configure(target)
        window.quick_actions_widget._publish(candidate)
        assert window.manual_context_id == "intro"
        assert launcher.calls == []

        for stage_id in ("intro", "budget", "reference", "resources"):
            assert window.runbook.current_stage.id == stage_id
            if stage_id != "intro":
                window.runbook_widget.manual_actions[1].click()
                assert window.session_summary.outcomes[-1].context_id == stage_id
                assert window.session_summary.outcomes[-1].status == "launch_requested"
            window.runbook_widget.complete.click()
            window.runbook_widget.continue_button.click()
            assert window.runbook.paused and window.routing.state == "PAUSED"
        assert len(launcher.calls) == 3
        assert window.session_summary.counts()["acknowledged_completion"] == 4

        window.runbook_widget.manual_actions[2].click()
        assert [card.id for card in window.viewer.bookmarks] == ["discussion"]
        reference.unlink()  # Only the disposable fixture is moved/missing.
        window.quick_actions_widget.target_id.setText("recovery-reference")
        window.quick_actions_widget._test()
        failure = window.session_summary.outcomes[-1]
        assert failure.status == "failed" and failure.context_id == "discussion"
        assert failure.action == Action(ActionType.OPEN_SHORTCUT, "recovery-reference")
        assert len(launcher.calls) == 3

        reference.write_text("Restored fictional reference", encoding="utf-8")
        previous_session = window.routing.snapshot.session_id
        window.quick_actions_widget._publish(window.quick_registry.copy())
        assert window.manual_context_id == "discussion"
        assert window.routing.snapshot.session_id != previous_session
        assert window.manual_mode == RoutingMode.LIVE
        assert len(launcher.calls) == 3
        window.runbook_widget.manual_actions[1].click()
        assert window.session_summary.outcomes[-1].context_id == "discussion"
        assert len(launcher.calls) == 4
        window.runbook_widget.complete.click()

        before_reload = tmp_path / "before-reload.json"
        window.session_summary.export(before_reload)
        payload = before_reload.read_text(encoding="utf-8")
        assert str(reference) not in payload and "private-reference" not in payload
        assert json.loads(payload)["counts"]["failed"] == 1
        saved = tmp_path / "session.json"
        assert window.save_studio_session(saved)
        assert window.restore_studio_session(saved)
        assert window.runbook.current_stage.id == "discussion"
        assert [card.id for card in window.viewer.bookmarks] == ["discussion"]
        assert window.runbook.paused and window.routing.state == "PAUSED"
        assert len(launcher.calls) == 4
        assert window.session_summary.outcomes == []
        window.runbook_widget.continue_button.click()
        window.runbook_widget.complete.click()
        window.runbook_widget.continue_button.click()
        assert window.runbook.finished
        window.manual_runbook_action(Action(ActionType.ADVANCE_STAGE))
        assert window.session_summary.outcomes[-1].status == "unchanged"
        assert len(launcher.calls) == 4
        assert window.worker is None
    finally:
        window.close()
