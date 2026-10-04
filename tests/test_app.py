import os
import json
import subprocess
import sys
import time
from dataclasses import replace
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import Mock

import numpy as np
import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QEvent, QPoint, Qt
from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import QApplication, QGridLayout, QPushButton

from gestureforge.app import STUDIO_ACTIONS, Window
from gestureforge.contracts import Action, ActionType, Prediction, RoutingMode
from gestureforge.shortcuts import Target, TargetKind
from gestureforge.vocabulary import GestureVocabulary
from gestureforge.viewer import load_deck
from gestureforge.workspace import Binding, Stage, Workspace, workspace_json


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture(autouse=True)
def isolated_studio_state(tmp_path, monkeypatch):
    import gestureforge.app as app_module
    monkeypatch.setattr(app_module, "DEFAULT_STUDIO_STATE_FOLDER", tmp_path / "studio-default")


def test_studio_keyboard_hint_matches_native_shortcuts(qapp):
    window = Window(studio=True)
    try:
        for shortcut in window.shortcuts[-2:]:
            assert shortcut.key().toString(QKeySequence.SequenceFormat.NativeText) in window.camera_status.text()
    finally:
        window.close()


def test_opt_in_trace_ends_at_pause_and_ignores_old_packets(tmp_path, monkeypatch, qapp):
    import gestureforge.app as app_module
    window = Window(model=object(), studio=True)
    _disable_logging(window)
    window.trace_folder = tmp_path
    worker = FakeWorker()
    monkeypatch.setattr(app_module, "CaptureWorker", lambda *a: worker)
    monkeypatch.setattr(app_module.time, "monotonic", lambda: 100.0)
    try:
        assert not window.record_trace.isChecked()
        window.record_trace.setChecked(True)
        window.start_camera()
        assert not window.record_trace.isEnabled()
        prediction = _studio_prediction(window, 0, 99.95, "NEUTRAL")
        worker.packets = [(_frame(), prediction)]
        window.poll()
        assert not list(tmp_path.glob("*.json"))
        window.pause()
        files = list(tmp_path.glob("*.json"))
        assert len(files) == 1
        saved = json.loads(files[0].read_text(encoding="utf-8"))
        assert saved["frames"][0]["frame_id"] == 0
        assert saved["frames"][0]["received_at"] == 100.0
        assert saved["annotation_complete"] is False and saved["expected_holds"] == []
        assert "landmarks" not in saved and "features" not in saved
        worker.packets = [(_frame(), replace(prediction, frame_id=1, timestamp=99.98))]
        window.poll()
        assert json.loads(files[0].read_text(encoding="utf-8")) == saved
        worker.finished = True
        window.poll()
        assert window.record_trace.isEnabled()
    finally:
        window.close()


def test_unsaved_trace_blocks_close_and_restart_until_retry(tmp_path, monkeypatch, qapp):
    import gestureforge.app as app_module
    window = Window(model=object(), studio=True)
    _disable_logging(window)
    window.trace_folder = tmp_path
    worker = FakeWorker()
    factory = Mock(return_value=worker)
    monkeypatch.setattr(app_module, "CaptureWorker", factory)
    monkeypatch.setattr(app_module.time, "monotonic", lambda: 100.0)
    try:
        window.record_trace.setChecked(True)
        window.start_camera()
        worker.packets = [(_frame(), _studio_prediction(window, 0, 99.95, "NEUTRAL"))]
        window.poll()
        trace = window.evaluation_trace
        assert trace is not None
        save = trace.save
        monkeypatch.setattr(trace, "save", Mock(side_effect=OSError("disk full")))
        close = FakeCloseEvent()
        window.closeEvent(close)
        assert close.ignored and not window._closing
        assert window.evaluation_trace is trace and worker.interrupted
        assert "disk full" in window.trace_status.text()
        worker.finished = True
        window.poll()
        window.start_camera()
        assert factory.call_count == 1 and window.evaluation_trace is trace
        routing, model, viewer = window.routing, window.model, window.viewer
        assert routing is not None
        snapshot = routing.snapshot
        camera_index = window.camera_index
        viewer.next_keyboard()
        window.restart_deck()
        assert window.viewer is viewer and viewer.position == 1
        assert not window.configure_studio(context_id="new-context")
        assert not window.set_studio_camera(camera_index + 1)
        assert not window.load_studio_dataset(tmp_path / "unused.json")
        vocabulary = GestureVocabulary(("G1", "G2", "G3"))
        with pytest.raises(ValueError, match="Save the current evaluation trace"):
            window.use_studio_model(_candidate_model(vocabulary), "Left", "P02", vocabulary)
        assert window.model_loader is None and window.model is model
        assert window.routing is routing and routing.snapshot == snapshot
        assert window.camera_index == camera_index and routing.state == "PAUSED"
        assert window.evaluation_trace is trace and "disk full" in window.trace_status.text()
        monkeypatch.setattr(trace, "save", save)
        assert window.pause()
        assert window.evaluation_trace is None and len(list(tmp_path.glob("*.json"))) == 1
        assert window.configure_studio(context_id="new-context")
        window.restart_deck()
        assert window.viewer.position == 0
    finally:
        window.close()


class FakeWorker:
    def __init__(self, packets=(), wait_result=True):
        self.packets = list(packets)
        self.error = ""
        self.interrupted = False
        self.finished = False
        self.wait_result = wait_result
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


def _frame():
    return np.zeros((8, 8, 3), dtype=np.uint8)


def _prediction(
    window: Window,
    frame_id: int,
    timestamp: float,
    label: str,
    *,
    accepted: bool = True,
    reason: str = "",
) -> Prediction:
    return Prediction(
        window.controller.session_id,
        "pilot",
        frame_id,
        timestamp,
        label,
        accepted,
        rejection_reason=reason,
    )


def _disable_logging(window: Window) -> None:
    window._log_failed = True
    window._auto_archive_summary_on_close = False


def _set_live_manual(window: Window) -> None:
    assert window.configure_studio(mode=RoutingMode.LIVE)


def _deck_file(path: Path, *, deck_id: str = "deck-test", title: str = "Demo <b>Deck</b>") -> Path:
    path.write_text(json.dumps({
        "schema_version": 1,
        "deck_id": deck_id,
        "title": title,
        "cards": [
            {"id": "intro", "title": "Card <b>Intro</b>", "body": "Body <i>one</i>"},
            {"id": "detail", "title": "Detail & proof", "body": "Body two"},
            {"id": "close", "title": "Close", "body": "Body three"},
        ],
    }), encoding="utf-8")
    return path


def _workspace_file(path: Path, workspace: Workspace) -> Path:
    path.write_text(json.dumps(workspace_json(workspace)), encoding="utf-8")
    return path


def _studio_prediction(
    window: Window,
    frame_id: int,
    timestamp: float,
    label: str,
    *,
    accepted: bool = True,
) -> Prediction:
    assert window.routing is not None
    snapshot = window.routing.snapshot
    return Prediction(
        snapshot.session_id,
        snapshot.profile_id,
        frame_id,
        timestamp,
        label,
        accepted,
        model_version=snapshot.model_version,
    )


def test_window_starts_keyboard_only_and_deck_controls_work(qapp) -> None:
    window = Window(model=None, data_note="keyboard only")
    _disable_logging(window)

    try:
        assert window.start_button.isEnabled() is False
        assert "no gesture dataset loaded" in window.prediction.text()
        assert "--dataset" in window.detail.text()
        assert window.viewer.position == 0
        assert window.card_badge.text() == "1"
        assert "GESTUREFORGE ASSIGNMENT DEMO" in window.deck_label.text()
        assert "Card 1 of 10" in window.position.text()
        assert "card-01" not in window.position.text()
        assert window.deck_progress.value() == 1
        assert window.card_topic.text() == "Topic: Start"
        assert window.card_title.text() == "Start"

        window.next_card()
        assert window.viewer.position == 1
        assert window.card_badge.text() == "2"
        assert "Card 2 of 10" in window.position.text()
        assert window.deck_progress.value() == 2
        assert window.card_topic.text() == "Topic: Personal Setup"
        assert window.card_title.text() == "Personal Setup"
        assert "Now showing Personal Setup (from Start)." in window.feedback.text()
        assert window.card_badge.styleSheet()
        assert window.card_frame.styleSheet()

        window.restart_deck()
        assert window.viewer.position == 0
        assert window.card_badge.text() == "1"
        assert "Card 1 of 10" in window.position.text()
        assert window.deck_progress.value() == 1
    finally:
        window.close()


def test_studio_no_dataset_starts_as_simulated_shell(qapp) -> None:
    window = Window(model=None, data_note="studio no data", studio=True)
    _disable_logging(window)

    try:
        assert window.start_button.isEnabled() is False
        assert "starter/personal recogniser" in window.studio_status.text()
        assert "Studio Preview" in window.boundary.text()
        assert "NEXT: would show next card" in window.boundary.text()
        assert "PREVIOUS: would show previous card" in window.boundary.text()
        assert "BOOKMARK: would bookmark this card" in window.boundary.text()
        assert window.viewer.position == 0
    finally:
        window.close()


def test_studio_manual_viewer_browses_bookmarks_and_resyncs_after_restart(qapp) -> None:
    window = Window(model=None, data_note="studio no data", studio=True)
    _disable_logging(window)

    try:
        widget = window.manual_viewer
        assert widget is not None
        assert widget.viewer is window.viewer
        assert window.start_button.isEnabled() is False
        _set_live_manual(window)

        widget.buttons[ActionType.PREVIOUS].click()
        assert window.viewer.position == 0
        assert widget.buttons[ActionType.PREVIOUS].isEnabled() is False

        widget.buttons[ActionType.NEXT].click()
        assert window.viewer.position == 1
        assert "Card 2 of 10" in window.position.text()
        assert widget.viewer is window.viewer
        assert widget.buttons[ActionType.PREVIOUS].isEnabled() is True

        widget.buttons[ActionType.BOOKMARK].click()
        widget.buttons[ActionType.BOOKMARK].click()
        assert [card.id for card in window.viewer.bookmarks] == ["card-02"]
        assert widget.bookmarks.count() == 1
        assert widget.buttons[ActionType.BOOKMARK].isEnabled() is False

        widget.buttons[ActionType.NEXT].click()
        widget.buttons[ActionType.NEXT].click()
        assert window.viewer.position == 3
        window.deck_tabs.setCurrentIndex(1)
        widget.bookmarks.setCurrentRow(0)
        widget.bookmarks.itemActivated.emit(widget.bookmarks.currentItem())
        window.deck_tabs.setCurrentIndex(0)
        assert window.viewer.position == 1
        assert "Card 2 of 10" in window.position.text()

        window.deck_tabs.setCurrentIndex(1)
        widget.bookmarks.setCurrentRow(0)
        remove = next(button for button in widget.findChildren(QPushButton) if button.text() == "Remove selected bookmark")
        remove.click()
        window.deck_tabs.setCurrentIndex(0)
        assert window.viewer.bookmarks == ()
        assert widget.bookmarks.count() == 0
        assert widget.buttons[ActionType.BOOKMARK].isEnabled() is True

        widget.buttons[ActionType.PREVIOUS].click()
        assert window.viewer.position == 0
        old = window.viewer
        window.restart_deck()
        assert window.viewer is not old
        assert widget.viewer is window.viewer
        assert window.viewer.position == 0
        assert "Card 1 of 10" in window.position.text()
    finally:
        window.close()


def test_studio_manual_viewer_rejects_non_viewer_actions_without_mutating(qapp) -> None:
    window = Window(model=None, data_note="studio no data", studio=True)
    _disable_logging(window)

    try:
        window.manual_viewer_action(Action(ActionType.ADVANCE_STAGE))
        assert window.viewer.position == 0
        assert window.viewer.bookmarks == ()
        assert "Use NEXT or the button to advance." in window.feedback.text()
    finally:
        window.close()


def test_studio_custom_deck_and_progress_round_trip(tmp_path, qapp) -> None:
    deck_path = _deck_file(tmp_path / "deck.json")
    progress = tmp_path / "progress.json"
    window = Window(model=None, data_note="studio no data", studio=True)
    _disable_logging(window)

    try:
        assert window.load_studio_deck(deck_path)
        assert window.viewer.deck.deck_id == "deck-test"
        assert window.deck_progress.maximum() == 3
        assert window.deck_label.text() == "DEMO <B>DECK</B>"
        assert window.card_title.text() == "Card <b>Intro</b>"
        assert window.card_body.text() == "Body <i>one</i>"
        assert window.card_title.textFormat() == Qt.TextFormat.PlainText
        assert window.card_body.textFormat() == Qt.TextFormat.PlainText
        _set_live_manual(window)

        window.manual_viewer_action(Action(ActionType.NEXT))
        window.manual_viewer_action(Action(ActionType.BOOKMARK))
        assert window.save_studio_progress(progress)

        restored = Window(model=None, data_note="studio no data", studio=True)
        _disable_logging(restored)
        try:
            assert restored.load_studio_deck(deck_path)
            assert restored.restore_studio_progress(progress)
            assert restored.viewer.position == 1
            assert [card.id for card in restored.viewer.bookmarks] == ["detail"]

            restored.restart_deck()
            assert restored.viewer.deck.deck_id == "deck-test"
            assert restored.viewer.position == 0
            assert restored.viewer.bookmarks == ()
            assert "Card 1 of 3" in restored.position.text()
        finally:
            restored.close()
    finally:
        window.close()


def test_studio_bad_deck_or_progress_preserves_current_selection(tmp_path, qapp) -> None:
    good = _deck_file(tmp_path / "good.json")
    wrong = _deck_file(tmp_path / "wrong.json", deck_id="other-deck")
    bad = tmp_path / "bad.json"
    bad.write_text("{", encoding="utf-8")
    wrong_progress = tmp_path / "wrong-progress.json"
    window = Window(model=None, data_note="studio no data", studio=True)
    _disable_logging(window)

    try:
        assert window.load_studio_deck(good)
        _set_live_manual(window)
        window.manual_viewer_action(Action(ActionType.NEXT))
        assert window.viewer.position == 1
        assert not window.load_studio_deck(bad)
        assert window.viewer.deck.deck_id == "deck-test"
        assert window.viewer.position == 1
        assert "Deck not loaded" in window.feedback.text()

        other = Window(model=None, data_note="studio no data", studio=True)
        _disable_logging(other)
        try:
            assert other.load_studio_deck(wrong)
            _set_live_manual(other)
            other.manual_viewer_action(Action(ActionType.NEXT))
            assert other.save_studio_progress(wrong_progress)
        finally:
            other.close()

        assert not window.restore_studio_progress(wrong_progress)
        assert window.viewer.deck.deck_id == "deck-test"
        assert window.viewer.position == 1
        assert "Progress not restored" in window.feedback.text()
    finally:
        window.close()


def test_studio_restore_pauses_and_ignores_stale_worker_packet(tmp_path, qapp) -> None:
    deck_path = _deck_file(tmp_path / "deck.json")
    progress = tmp_path / "progress.json"
    window = Window(model=object(), feature_function=lambda observation, hand: np.zeros(60), studio=True)
    _disable_logging(window)
    assert window.routing is not None
    old_snapshot = window.routing.resume()
    stale = Prediction(old_snapshot.session_id, old_snapshot.profile_id, 1, time.monotonic(), "NEXT", True,
                       model_version=old_snapshot.model_version)
    worker = FakeWorker([(_frame(), stale)])
    window.worker = worker

    try:
        assert window.load_studio_deck(deck_path)
        _set_live_manual(window)
        window.manual_viewer_action(Action(ActionType.NEXT))
        assert window.save_studio_progress(progress)
        window.manual_viewer_action(Action(ActionType.NEXT))
        assert window.viewer.position == 2

        assert window.restore_studio_progress(progress)
        assert worker.interrupted
        assert window.routing.state == "PAUSED"
        window.poll()
        assert window.viewer.position == 1
        assert "Studio simulation" not in window.feedback.text()
    finally:
        window.close()


def test_studio_workspace_runbook_loads_stage_routes_and_session(tmp_path, qapp) -> None:
    deck_path = _deck_file(tmp_path / "deck.json")
    deck = load_deck(deck_path)
    workspace = Workspace(
        "training", "Training Workspace", deck,
        stages=(
            Stage("intro", "Intro", "Read the first instruction.", "detail",
                  (Binding("NEXT", Action(ActionType.NEXT)),), "Continue"),
            Stage("finish", "Finish", "Manual review only.", "close", (), "Finish"),
        ),
    )
    workspace_path = _workspace_file(tmp_path / "workspace.json", workspace)
    session_path = tmp_path / "session.json"
    window = Window(model=object(), feature_function=lambda observation, hand: np.zeros(60), studio=True)
    _disable_logging(window)
    assert window.routing is not None
    old_snapshot = window.routing.resume()
    window.worker = FakeWorker([(
        _frame(),
        Prediction(old_snapshot.session_id, old_snapshot.profile_id, 1, time.monotonic(), "NEXT", True,
                   model_version=old_snapshot.model_version),
    )])

    try:
        assert window.load_studio_workspace(workspace_path)
        _set_live_manual(window)
        assert window.runbook is not None
        assert window.viewer is window.runbook.viewer
        assert window.viewer.current_card.id == "detail"
        assert window.runbook_widget.title.text() == "1: Intro"
        assert "Read the first instruction." in window.runbook_widget.instructions.text()
        assert not window.runbook_widget.complete.isHidden()
        assert window.session_summary.counts()["acknowledged_completion"] == 0
        assert "NEXT" in window.boundary.text() and "Context: intro" in window.boundary.text()
        assert window.routing.state == "PAUSED"
        assert window.worker.interrupted
        window.poll()
        assert window.viewer.current_card.id == "detail"
        assert "Studio simulation" not in window.feedback.text()

        window.manual_runbook_action(Action(ActionType.ADVANCE_STAGE))
        assert window.runbook.position == 1
        assert window.viewer.current_card.id == "close"
        assert window.routing_manual_only
        assert not window.start_button.isEnabled()
        assert "Live manual controls active" in window.boundary.text()

        assert window.save_studio_session(session_path)
        window.previous_runbook_stage()
        assert window.runbook is not None
        assert window.runbook.position == 0 and not window.routing_manual_only
        assert window.restore_studio_session(session_path)
        assert window.runbook is not None
        assert window.runbook.position == 1 and window.routing_manual_only
        assert window.viewer.current_card.id == "close"

        window.restart_deck()
        assert window.runbook is not None
        assert window.runbook.position == 0
        assert not window.routing_manual_only
        assert window.viewer.current_card.id == "detail"
        assert "Context: intro" in window.boundary.text()
    finally:
        window.close()


def test_studio_runbook_editor_applies_with_archive_scope_and_preserves_review(tmp_path, qapp) -> None:
    deck_path = _deck_file(tmp_path / "deck.json")
    deck = load_deck(deck_path)
    workspace = Workspace(
        "training", "Training Workspace", deck,
        stages=(
            Stage("intro", "Intro", "Read the first instruction.", "intro",
                  (Binding("NEXT", Action(ActionType.NEXT)),), "Continue"),
            Stage("finish", "Finish", "Manual review only.", "close", (), "Finish"),
        ),
    )
    window = Window(model=object(), studio=True)
    _disable_logging(window)
    window.studio_state_folder = tmp_path / "studio"

    try:
        assert window.use_studio_workspace(workspace)
        _set_live_manual(window)
        window.manual_viewer_action(Action(ActionType.BOOKMARK))
        assert window.session_summary.counts()["applied"] == 1
        assert tuple(card.id for card in window.viewer.bookmarks) == ("intro",)

        window.runbook_editor.stages.setCurrentRow(1)
        window.runbook_editor.title.setText("Wrap up")
        window.runbook_editor.instructions.setPlainText("Confirm the last manual step.")
        window.runbook_editor._save()

        assert window.workspace.stages[1].title == "Wrap up"
        assert window.runbook is not None and window.runbook.current_stage is not None
        assert window.runbook.current_stage.id == "intro"
        assert tuple(card.id for card in window.viewer.bookmarks) == ("intro",)
        assert window.session_summary.counts()["applied"] == 0
        archived = list(window.studio_state_folder.glob("studio-session-summary-*.json"))
        assert len(archived) == 1
        payload = json.loads(archived[0].read_text(encoding="utf-8"))
        assert payload["scope"]["workspace_id"] == "training"
        assert payload["scope"]["revision_id"].startswith("revision-")
        assert payload["counts"]["applied"] == 1
        assert "Shell rejected" not in window.runbook_editor.status.text()
    finally:
        window.close()


def test_studio_runbook_editor_rejection_preserves_shell_and_widget_state(tmp_path, qapp) -> None:
    workspace = Workspace(
        "training", "Training Workspace",
        stages=(Stage("intro", "Intro", "Read.", None, (), "Continue"),),
    )
    window = Window(model=object(), studio=True)
    _disable_logging(window)

    try:
        assert window.use_studio_workspace(workspace)
        trace = SimpleNamespace(frame_count=1, save=Mock(side_effect=OSError("disk full")))
        window.evaluation_trace = cast(Any, trace)
        window.trace_path = tmp_path / "trace.json"

        window.runbook_editor.stages.setCurrentRow(0)
        window.runbook_editor.title.setText("Rejected")
        window.runbook_editor.instructions.setPlainText("Keep this draft.")
        window.runbook_editor.continue_label.setText("Retry later")
        window.runbook_editor._save()

        assert window.workspace.stages[0].title == "Intro"
        assert window.runbook_editor.editor.workspace.stages[0].title == "Intro"
        assert window.runbook_editor.title.text() == "Rejected"
        assert window.runbook_editor.instructions.toPlainText() == "Keep this draft."
        assert window.runbook_editor.continue_label.text() == "Retry later"
        assert "Shell rejected runbook change" in window.runbook_editor.status.text()
        assert "disk full" in window.trace_status.text()

        window.evaluation_trace = cast(Any, trace)
        window.runbook_editor._new()
        window.runbook_editor.title.setText("Draft new stage")
        window.runbook_editor.instructions.setPlainText("Still typing.")
        window.runbook_editor._save()
        assert len(window.workspace.stages) == 1
        assert window.runbook_editor.stages.currentRow() == -1
        assert window.runbook_editor.title.text() == "Draft new stage"
        assert window.runbook_editor.instructions.toPlainText() == "Still typing."
        window.evaluation_trace = None
    finally:
        window.close()


@pytest.mark.parametrize("operation", ["move", "delete"])
def test_rejected_editor_reorder_retains_selection_and_retry_target(operation, monkeypatch, qapp):
    window = Window(studio=True)
    _disable_logging(window)
    workspace = Workspace("review", "Review", stages=(
        Stage("first", "First", "Read.", None, ()),
        Stage("second", "Second", "Continue.", None, ()),
    ))
    try:
        assert window.use_studio_workspace(workspace)
        editor = window.runbook_editor
        editor.stages.setCurrentRow(0)
        editor.instructions.setPlainText("Draft retained")
        monkeypatch.setattr(window, "_archive_session_summary", lambda reason: False)
        editor._move(1) if operation == "move" else editor._delete()
        assert editor.editor.workspace == workspace
        assert editor.stages.currentRow() == 0
        assert editor.stage_id.text() == "first"
        assert editor.instructions.toPlainText() == "Draft retained"
        monkeypatch.setattr(window, "_archive_session_summary", lambda reason: True)
        editor._save()
        assert window.workspace.stages[0].instructions == "Draft retained"
        assert window.workspace.stages[1] == workspace.stages[1]
    finally:
        window.close()


def test_studio_summary_records_manual_runbook_prechange_context_and_completion(qapp) -> None:
    workspace = Workspace(
        "training", "Training Workspace",
        stages=(
            Stage("intro", "Intro", "Read.", None, (), "Continue"),
            Stage("finish", "Finish", "Done.", None, (), "Finish"),
        ),
    )
    window = Window(model=object(), studio=True)
    _disable_logging(window)

    try:
        assert window.use_studio_workspace(workspace)
        _set_live_manual(window)
        assert window.routing is not None
        first_session = window.routing.snapshot.session_id
        window.manual_runbook_action(Action(ActionType.ADVANCE_STAGE))

        assert window.runbook is not None and window.runbook.current_stage is not None
        assert window.runbook.current_stage.id == "finish"
        assert window.session_summary.counts()["applied"] == 1
        outcome = window.session_summary.outcomes[-1]
        assert outcome.action == Action(ActionType.ADVANCE_STAGE)
        assert outcome.context_id == "intro"
        assert outcome.session_id == first_session
        assert window.session_summary.counts()["acknowledged_completion"] == 0

        window.runbook_widget.complete.click()
        assert window.session_summary.counts()["acknowledged_completion"] == 1
        assert window.session_summary.completed_stages == {"finish"}
    finally:
        window.close()


def test_studio_restore_and_restart_archive_then_reset_summary(tmp_path, qapp) -> None:
    deck_path = _deck_file(tmp_path / "deck.json")
    deck = load_deck(deck_path)
    workspace = Workspace(
        "training", "Training Workspace", deck,
        stages=(
            Stage("intro", "Intro", "Read.", "intro", (), "Continue"),
            Stage("finish", "Finish", "Done.", "close", (), "Finish"),
        ),
    )
    window = Window(model=object(), studio=True)
    _disable_logging(window)
    window.studio_state_folder = tmp_path / "studio"

    try:
        assert window.use_studio_workspace(workspace)
        _set_live_manual(window)
        session_path = tmp_path / "session.json"
        assert window.save_studio_session(session_path)
        window.manual_viewer_action(Action(ActionType.BOOKMARK))
        window.manual_runbook_action(Action(ActionType.ADVANCE_STAGE))
        assert window.session_summary.counts()["applied"] == 2

        assert window.restore_studio_session(session_path)
        assert window.session_summary.counts()["applied"] == 0
        assert window.runbook is not None and window.runbook.position == 0
        archived = list(window.studio_state_folder.glob("studio-session-summary-*.json"))
        assert len(archived) == 1
        assert json.loads(archived[0].read_text(encoding="utf-8"))["counts"]["applied"] == 2

        window.manual_viewer_action(Action(ActionType.BOOKMARK))
        assert window.session_summary.counts()["applied"] == 1
        window.restart_deck()
        assert window.session_summary.counts()["applied"] == 0
        assert window.runbook is not None and window.runbook.position == 0
        assert len(list(window.studio_state_folder.glob("studio-session-summary-*.json"))) == 2
    finally:
        window.close()


@pytest.mark.parametrize("operation", ["restart", "restore", "close"])
def test_studio_summary_archive_failure_blocks_reset_or_close(operation, tmp_path, monkeypatch, qapp) -> None:
    deck_path = _deck_file(tmp_path / "deck.json")
    deck = load_deck(deck_path)
    workspace = Workspace(
        "training", "Training Workspace", deck,
        stages=(Stage("intro", "Intro", "Read.", "intro", (), "Continue"),),
    )
    window = Window(model=object(), studio=True)
    window._log_failed = True
    window.studio_state_folder = tmp_path / "studio"

    try:
        assert window.use_studio_workspace(workspace)
        _set_live_manual(window)
        window.manual_viewer_action(Action(ActionType.BOOKMARK))
        assert window.session_summary.counts()["applied"] == 1
        monkeypatch.setattr(window.session_summary, "export", Mock(side_effect=OSError("disk full")))

        if operation == "restart":
            before = (window.viewer, window.runbook, window.session_summary)
            window.restart_deck()
            assert (window.viewer, window.runbook, window.session_summary) == before
            assert "disk full" in window.feedback.text()
        elif operation == "restore":
            session_path = tmp_path / "session.json"
            assert window.save_studio_session(session_path)
            assert not window.restore_studio_session(session_path)
            assert window.session_summary.counts()["applied"] == 1
            assert "disk full" in window.feedback.text()
        else:
            event = FakeCloseEvent()
            window.closeEvent(event)
            assert event.ignored and not event.accepted and not window._closing
            assert "disk full" in window.feedback.text()
            window._auto_archive_summary_on_close = False
    finally:
        window._auto_archive_summary_on_close = False
        window.close()


def test_studio_deckless_workspace_is_honest_manual_only(tmp_path, qapp) -> None:
    workspace = Workspace(
        "quick-only", "Quick Only",
        stages=(Stage("manual", "Manual", "Use the button; no deck is included.", None, ()),),
    )
    window = Window(model=object(), studio=True)
    _disable_logging(window)

    try:
        assert window.use_studio_workspace(workspace)
        _set_live_manual(window)
        assert not window.deck_available
        assert not window.card_frame.isEnabled()
        assert window.card_title.text() == "Quick Only"
        assert "no deck" in window.card_body.text().lower() or "button" in window.card_body.text().lower()
        assert window.routing_manual_only
        assert not window.start_button.isEnabled()
        assert isinstance(window.deck_tools, QGridLayout)
        assert all(button.isEnabled() for button in window.file_tool_buttons)
        window.start_camera()
        assert window.worker is None
        window.manual_viewer_action(Action(ActionType.NEXT))
        assert "No deck is loaded" in window.feedback.text()
        window.next_card()
        assert "No deck is loaded" in window.feedback.text()
        assert not window.save_studio_progress(tmp_path / "progress.json")
        window.manual_runbook_action(Action(ActionType.ADVANCE_STAGE))
        assert window.runbook is not None
        assert window.runbook.finished
    finally:
        window.close()


def test_studio_quick_actions_activate_explicitly_and_simulate_with_custom_vocabulary(tmp_path, qapp) -> None:
    window = Window(model=object(), studio=True)
    _disable_logging(window)
    window.studio_state_folder = tmp_path / "studio"
    window.quick_actions_widget.state_path = window.studio_state_folder / "quick-actions-targets.json"

    try:
        assert window.routing is not None
        previous = window.routing.snapshot
        candidate = window.quick_registry.copy()
        candidate.configure(Target("calculator", "Calculator", TargetKind.BUILTIN, "calculator"))
        candidate.bind_quick(("calculator", None, None))
        window.quick_actions_widget._publish(candidate)

        assert window.quick_actions_widget.state_path.exists()
        assert window.routing.snapshot.context_id == previous.context_id
        assert window.routing.snapshot.bindings == previous.bindings
        assert not window.quick_actions_active
        assert "Use Quick Actions" in window.quick_actions_widget.status.text()

        assert window.use_quick_actions_context()
        assert window.routing is not None
        assert not window.routing_manual_only
        assert window.routing.snapshot.context_id == window.quick_actions_context_id
        assert dict(window.routing.snapshot.bindings) == {
            "NEXT": Action(ActionType.OPEN_SHORTCUT, "calculator"),
        }

        vocabulary = GestureVocabulary(("G1", "G2", "G3"))
        window.use_studio_model(_candidate_model(vocabulary), "Right", "P02", vocabulary)

        assert window.routing is not None
        assert window.routing.snapshot.context_id == window.quick_actions_context_id
        assert dict(window.routing.snapshot.bindings) == {
            "G1": Action(ActionType.OPEN_SHORTCUT, "calculator"),
        }
        assert window.quick_actions_widget.launch_buttons[0].text().startswith("G1:")
        window.quick_actions_widget.launch_buttons[0].click()
        assert window.session_summary.counts()["simulated"] == 1
        assert window.session_summary.counts()["launch_requested"] == 0
        assert "would open Calculator" in window.feedback.text()
    finally:
        window.close()


def test_studio_quick_actions_change_failure_preserves_routing_and_registry(tmp_path, monkeypatch, qapp) -> None:
    window = Window(model=object(), studio=True)
    _disable_logging(window)
    window.quick_actions_widget.state_path = tmp_path / "targets.json"
    assert window.routing is not None
    before = window.routing.snapshot
    monkeypatch.setattr(window, "pause", Mock(return_value=False))

    try:
        window.quick_actions_widget.target_id.setText("calculator")
        window.quick_actions_widget.label.setText("Calculator")
        window.quick_actions_widget.kind.setCurrentIndex(window.quick_actions_widget.kind.findData(TargetKind.BUILTIN))
        window.quick_actions_widget.value.setText("calculator")
        window.quick_actions_widget._save_target()

        assert window.quick_registry.targets == ()
        assert not window.quick_actions_widget.state_path.exists()
        assert window.routing.snapshot == before
        assert window.manual_context_id == "demo-studio"
        assert "Cannot save target" in window.quick_actions_widget.status.text()
    finally:
        window.close()


def test_studio_quick_actions_busy_shell_rejects_before_private_write(tmp_path, qapp) -> None:
    window = Window(model=object(), studio=True)
    _disable_logging(window)
    window.quick_actions_widget.state_path = tmp_path / "targets.json"
    window.model_loader = object()

    try:
        window.quick_actions_widget.target_id.setText("calculator")
        window.quick_actions_widget.label.setText("Calculator")
        window.quick_actions_widget.kind.setCurrentIndex(window.quick_actions_widget.kind.findData(TargetKind.BUILTIN))
        window.quick_actions_widget.value.setText("calculator")
        window.quick_actions_widget._save_target()

        assert window.quick_registry.targets == ()
        assert not window.quick_actions_widget.state_path.exists()
        assert "Cannot save target" in window.quick_actions_widget.status.text()
        assert not window.use_quick_actions_context()
        window.manual_quick_action(Action(ActionType.OPEN_SHORTCUT, "calculator"))
        assert window.session_summary.outcomes == []
    finally:
        window.model_loader = None
        window.close()


def test_studio_quick_actions_storage_failure_does_not_commit_or_rebind(tmp_path, qapp) -> None:
    window = Window(model=object(), studio=True)
    _disable_logging(window)
    state = tmp_path / "state-as-dir"
    state.mkdir()
    window.quick_actions_widget.state_path = state
    assert window.routing is not None
    before = window.routing.snapshot

    try:
        window.quick_actions_widget.target_id.setText("calculator")
        window.quick_actions_widget.label.setText("Calculator")
        window.quick_actions_widget.kind.setCurrentIndex(window.quick_actions_widget.kind.findData(TargetKind.BUILTIN))
        window.quick_actions_widget.value.setText("calculator")
        window.quick_actions_widget._save_target()

        assert window.quick_registry.targets == ()
        assert window.routing.snapshot == before
        assert window.manual_context_id == "demo-studio"
        assert "Cannot save target" in window.quick_actions_widget.status.text()
    finally:
        window.close()


def test_studio_quick_actions_deckless_reload_and_exports_keep_targets_private(tmp_path, qapp) -> None:
    workspace = Workspace(
        "quick-only", "Quick Only",
        stages=(Stage("manual", "Manual", "Use the target test button.", None, ()),),
    )
    window = Window(model=object(), studio=True)
    _disable_logging(window)
    window.studio_state_folder = tmp_path / "studio"
    window.quick_actions_widget.state_path = window.studio_state_folder / "quick-actions-targets.json"

    try:
        assert window.use_studio_workspace(workspace)
        candidate = window.quick_registry.copy()
        candidate.configure(Target("site", "Private Site", TargetKind.WEBSITE, "https://example.com/private"))
        candidate.bind_quick(("site", None, None))
        window.quick_actions_widget._publish(candidate)
        assert window.use_quick_actions_context()
        window.manual_quick_action(Action(ActionType.OPEN_SHORTCUT, "site"))

        session_path = tmp_path / "session.json"
        summary_path = tmp_path / "summary.json"
        assert window.save_studio_session(session_path)
        window.session_summary.export(summary_path)
        exported = session_path.read_text(encoding="utf-8") + summary_path.read_text(encoding="utf-8")

        assert "https://example.com/private" not in exported
        assert "site" in exported
        assert window.quick_actions_widget.state_path.exists()

        assert window.restore_studio_session(session_path)
        assert window.deck_available is False
        assert window.use_quick_actions_context()
        assert window.routing is not None
        assert window.routing.snapshot.context_id == window.quick_actions_context_id
        assert dict(window.routing.snapshot.bindings) == {
            "NEXT": Action(ActionType.OPEN_SHORTCUT, "site"),
        }
    finally:
        window.close()


def test_studio_empty_workspace_stays_manual_only_after_model_reload(qapp) -> None:
    window = Window(model=object(), studio=True)
    _disable_logging(window)

    try:
        assert window.use_studio_workspace(Workspace("empty", "Empty"))
        assert window.routing_manual_only
        assert not window.start_button.isEnabled()
        vocabulary = GestureVocabulary(("G1", "G2", "G3"))
        window.use_studio_model(_candidate_model(vocabulary), "Right", "P02", vocabulary)
        assert window.workspace.id == "empty"
        assert window.runbook is not None and window.runbook.current_stage is None
        assert window.routing_manual_only
        assert not window.start_button.isEnabled()
        assert "Context: empty" in window.boundary.text()
    finally:
        window.close()


def test_stage_named_quick_actions_does_not_reactivate_shortcuts_on_model_reload(qapp) -> None:
    window = Window(model=object(), studio=True)
    _disable_logging(window)
    workspace = Workspace(
        "training", "Training", window.viewer.deck,
        stages=(Stage("quick-actions", "Coincidental ID", "Read manually.", "card-01",
                      (Binding("NEXT", Action(ActionType.NEXT)),)),),
    )

    try:
        candidate = window.quick_registry.copy()
        candidate.configure(Target("calculator", "Calculator", TargetKind.BUILTIN, "calculator"))
        candidate.bind_quick(("calculator", None, None))
        window.quick_actions_widget._publish(candidate)
        assert not window.quick_actions_active
        assert window.use_studio_workspace(workspace)
        assert window.routing is not None
        assert window.routing.snapshot.context_id == "quick-actions"
        assert window.routing.snapshot.context_id != window.quick_actions_context_id

        vocabulary = GestureVocabulary(("G1", "G2", "G3"))
        window.use_studio_model(_candidate_model(vocabulary), "Right", "P02", vocabulary)

        assert not window.quick_actions_active
        assert window.routing_manual_only
        assert window.manual_context_id == "quick-actions"
        assert window.manual_context_id != window.quick_actions_context_id
    finally:
        window.close()


def test_custom_deck_model_reload_keeps_default_deck_bindings(tmp_path, qapp) -> None:
    deck_path = _deck_file(tmp_path / "deck.json")
    window = Window(model=object(), studio=True)
    _disable_logging(window)

    try:
        assert window.load_studio_deck(deck_path)
        assert not window.routing_manual_only
        vocabulary = GestureVocabulary(("G1", "G2", "G3"))
        window.use_studio_model(_candidate_model(vocabulary), "Right", "P02", vocabulary)
        assert window.workspace.id == "manual-deck"
        assert window.runbook is not None and window.runbook.current_stage is None
        assert not window.routing_manual_only
        assert window.routing is not None
        assert window.routing.snapshot.context_id == "manual-deck"
        assert dict(window.routing.snapshot.bindings) == dict(zip(vocabulary.action_ids, STUDIO_ACTIONS, strict=True))
        assert window.start_button.isEnabled()
    finally:
        window.close()


def test_studio_supplied_workspace_loads_manual_until_matching_vocabulary(qapp) -> None:
    path = Path(__file__).resolve().parent.parent / "assets" / "harbor_workspace.json"
    window = Window(model=None, studio=True)
    _disable_logging(window)

    try:
        assert window.load_studio_workspace(path)
        assert window.workspace.id == "harbor-onboarding"
        assert window.runbook is not None
        assert window.viewer is window.runbook.viewer
        assert window.runbook.position == 0
        assert window.routing_manual_only
        assert "Manual-only stage" in window.boundary.text()
        assert "G1" in window.feedback.text() and "manual buttons" in window.feedback.text()
        assert not window.runbook_widget.manual_actions[0].isHidden()
        assert window.runbook_widget.manual_actions[0].isEnabled()

        vocabulary = GestureVocabulary(("G1", "G2", "G3"))
        model = _candidate_model(vocabulary)
        window.use_studio_model(model, "Right", "P02", vocabulary)
        assert not window.routing_manual_only
        assert window.runbook.position == 0
        assert window.routing is not None
        assert window.runbook.current_stage is not None
        assert window.routing.snapshot.context_id == window.runbook.current_stage.id
        assert dict(window.routing.snapshot.bindings) == {
            binding.gesture_id: binding.action for binding in window.runbook.current_stage.bindings
        }
        assert "G1" in window.boundary.text()
    finally:
        window.close()


def test_studio_workspace_failures_preserve_existing_state(tmp_path, qapp) -> None:
    good = Workspace("good", "Good", stages=(Stage("one", "One", "Ready.", None, ()),))
    bad_path = tmp_path / "bad-workspace.json"
    bad_path.write_text('{"schema_version": 1, "id": "bad", "title": "Bad", "password": "secret"}')
    window = Window(model=object(), studio=True)
    _disable_logging(window)

    try:
        assert window.use_studio_workspace(good)
        before = (window.workspace, window.viewer, window.runbook, window.routing_manual_only, window.manual_context_id)
        assert not window.load_studio_workspace(bad_path)
        assert (window.workspace, window.viewer, window.runbook,
                window.routing_manual_only, window.manual_context_id) == before
        assert "Prior workspace retained" in window.feedback.text()

        trace = SimpleNamespace(frame_count=1, save=Mock(side_effect=OSError("disk full")))
        window.evaluation_trace = cast(Any, trace)
        window.trace_path = tmp_path / "trace.json"
        assert not window.use_studio_workspace(Workspace("other", "Other"))
        assert (window.workspace, window.viewer, window.runbook,
                window.routing_manual_only, window.manual_context_id) == before
        assert "disk full" in window.trace_status.text()
        window.evaluation_trace = None
    finally:
        window.close()


def test_workspace_widget_import_rejection_reconciles_to_shell_state(tmp_path, qapp) -> None:
    current = Workspace("current", "Current", stages=(Stage("one", "One", "Ready.", None, ()),))
    candidate = Workspace("candidate", "Candidate", stages=(Stage("two", "Two", "Blocked.", None, ()),))
    path = _workspace_file(tmp_path / "candidate.json", candidate)
    window = Window(model=object(), studio=True)
    _disable_logging(window)

    try:
        assert window.use_studio_workspace(current)
        trace = SimpleNamespace(frame_count=1, save=Mock(side_effect=OSError("disk full")))
        window.evaluation_trace = cast(Any, trace)
        window.trace_path = tmp_path / "trace.json"

        assert not window.workspace_widget.import_path(path)

        assert window.workspace.id == "current"
        assert window.workspace_widget.store.active.id == "current"
        assert "Shell rejected activation" in window.workspace_widget.status.text()
        assert "disk full" in window.trace_status.text()
        window.evaluation_trace = None
    finally:
        window.close()


def test_workspace_widget_same_workspace_rejection_is_explicit(tmp_path, qapp) -> None:
    current = Workspace("current", "Current", stages=(Stage("one", "One", "Ready.", None, ()),))
    path = _workspace_file(tmp_path / "current.json", current)
    window = Window(model=object(), studio=True)
    _disable_logging(window)

    try:
        assert window.use_studio_workspace(current)
        trace = SimpleNamespace(frame_count=1, save=Mock(side_effect=OSError("disk full")))
        window.evaluation_trace = cast(Any, trace)
        window.trace_path = tmp_path / "trace.json"

        assert not window.workspace_widget.import_path(path)

        assert window.workspace.id == "current"
        assert window.workspace_widget.store.active.id == "current"
        assert "Shell rejected activation" in window.workspace_widget.status.text()
        assert "disk full" in window.trace_status.text()
        window.evaluation_trace = None
    finally:
        window.close()


def test_studio_progress_save_honors_trace_and_atomic_failures(tmp_path, monkeypatch, qapp) -> None:
    import gestureforge.storage as storage

    progress = tmp_path / "progress.json"
    progress.write_text('{"kept": true}\n', encoding="utf-8")
    window = Window(model=object(), studio=True)
    _disable_logging(window)

    try:
        _set_live_manual(window)
        window.record_trace.setChecked(True)
        assert window.routing is not None
        window.routing.resume()
        window.evaluation_trace = cast(Any, SimpleNamespace(frame_count=1, save=Mock(side_effect=OSError("disk full"))))
        window.trace_path = tmp_path / "trace.json"
        window.manual_viewer_action(Action(ActionType.NEXT))
        assert not window.save_studio_progress(progress)
        assert progress.read_text(encoding="utf-8") == '{"kept": true}\n'
        assert window.viewer.position == 0
        assert "Progress not saved" in window.feedback.text()

        window.evaluation_trace = None
        monkeypatch.setattr(storage.os, "replace", Mock(side_effect=OSError("replace failed")))
        assert not window.save_studio_progress(progress)
        assert progress.read_text(encoding="utf-8") == '{"kept": true}\n'
    finally:
        window.close()


@pytest.mark.parametrize("operation", ["load", "restore"])
def test_studio_load_or_restore_does_not_mutate_when_pause_fails(operation, tmp_path, monkeypatch, qapp) -> None:
    deck_path = _deck_file(tmp_path / "deck.json")
    window = Window(model=object(), studio=True)
    _disable_logging(window)

    try:
        window.manual_viewer_action(Action(ActionType.NEXT))
        progress = tmp_path / "progress.json"
        assert window.save_studio_progress(progress)
        window.manual_viewer_action(Action(ActionType.NEXT))
        before = (window.viewer.deck.deck_id, window.viewer.position, tuple(card.id for card in window.viewer.bookmarks))
        monkeypatch.setattr(window, "pause", Mock(return_value=False))

        ok = window.load_studio_deck(deck_path) if operation == "load" else window.restore_studio_progress(progress)

        assert not ok
        assert (window.viewer.deck.deck_id, window.viewer.position,
                tuple(card.id for card in window.viewer.bookmarks)) == before
    finally:
        window.close()


def test_studio_deck_dialogs_cancel_and_busy_without_side_effects(tmp_path, monkeypatch, qapp) -> None:
    import gestureforge.app as app_module

    window = Window(model=object(), studio=True)
    _disable_logging(window)
    window.studio_state_folder = tmp_path / "state"
    load_dialog = Mock(return_value=("", ""))
    save_dialog = Mock(return_value=("", ""))
    monkeypatch.setattr(app_module.QFileDialog, "getOpenFileName", load_dialog)
    monkeypatch.setattr(app_module.QFileDialog, "getSaveFileName", save_dialog)
    pause = Mock(return_value=True)
    monkeypatch.setattr(window, "pause", pause)

    try:
        window.choose_studio_deck()
        window.choose_save_studio_progress()
        window.choose_restore_studio_progress()
        assert load_dialog.call_count == 2 and save_dialog.call_count == 1
        assert pause.call_count == 3
        assert window.viewer.position == 0

        window.model_loader = object()
        window.choose_studio_deck()
        window.choose_save_studio_progress()
        window.choose_restore_studio_progress()
        assert load_dialog.call_count == 2 and save_dialog.call_count == 1
        assert pause.call_count == 3
    finally:
        window.model_loader = None
        window.close()


def test_studio_save_dialog_falls_back_when_default_folder_is_unwritable(tmp_path, monkeypatch, qapp) -> None:
    import gestureforge.app as app_module

    destination = tmp_path / "chosen.json"
    window = Window(model=object(), studio=True)
    _disable_logging(window)
    blocked = window.studio_state_folder
    original_mkdir = Path.mkdir

    def mkdir(path: Path, mode: int = 0o777, parents: bool = False, exist_ok: bool = False) -> None:
        if path == blocked:
            raise OSError("locked")
        original_mkdir(path, mode=mode, parents=parents, exist_ok=exist_ok)

    monkeypatch.setattr(Path, "mkdir", mkdir)
    save_dialog = Mock(return_value=(str(destination), ""))
    monkeypatch.setattr(app_module.QFileDialog, "getSaveFileName", save_dialog)

    try:
        window.choose_save_studio_progress()

        assert save_dialog.call_args.args[2] == ""
        assert destination.exists()
        assert "Progress saved" in window.deck_file_status.text()
    finally:
        window.close()


def test_assignment_window_keeps_existing_card_controls_only(qapp) -> None:
    window = Window(model=None, data_note="keyboard only")
    _disable_logging(window)

    try:
        assert window.manual_viewer is None
        assert not hasattr(window, "deck_tabs")
        window.manual_viewer_action(Action(ActionType.BOOKMARK))
        assert window.viewer.bookmarks == ()
        window.next_card()
        assert window.viewer.position == 1
        assert "Card 2 of 10" in window.position.text()
    finally:
        window.close()


def test_studio_preview_simulates_without_moving_deck(monkeypatch, qapp) -> None:
    import gestureforge.app as app_module

    window = Window(model=object(), feature_function=lambda observation, hand: np.zeros(60), studio=True)
    _disable_logging(window)
    current = [100.0]
    monkeypatch.setattr(app_module.time, "monotonic", lambda: current[0])
    assert window.routing is not None
    window.routing.resume()
    packets = []
    for frame_id, timestamp, label in [
        (1, 100.00, "NEUTRAL"),
        (2, 100.15, "NEUTRAL"),
        (3, 100.31, "NEUTRAL"),
        (4, 100.45, "NEXT"),
        (5, 100.62, "NEXT"),
        (6, 100.78, "NEXT"),
        (7, 100.91, "NEXT"),
    ]:
        packets.append((_frame(), _studio_prediction(window, frame_id, timestamp, label)))
    window.worker = FakeWorker(packets)

    try:
        for _, prediction in list(packets):
            current[0] = prediction.timestamp
            window.poll()

        assert window.viewer.position == 0
        assert "Studio simulation: NEXT would show next card." in window.feedback.text()
        assert "Card 1 of 10" in window.position.text()
        assert window.session_summary.counts()["simulated"] == 1
        assert window.session_summary.outcomes[-1].source == "gesture"
    finally:
        window.close()


def test_studio_full_summary_pauses_before_consuming_gesture(monkeypatch, qapp) -> None:
    import gestureforge.app as app_module

    window = Window(model=object(), feature_function=lambda observation, hand: np.zeros(60), studio=True)
    _disable_logging(window)
    current = [100.0]
    monkeypatch.setattr(app_module.time, "monotonic", lambda: current[0])
    assert window.routing is not None
    window.routing.resume()
    route = Mock(wraps=window.routing.route)
    cast(Any, window.routing).route = route
    monkeypatch.setattr(window.session_summary, "ensure_capacity", Mock(side_effect=ValueError("full")))
    packets = [(_frame(), _studio_prediction(window, i, t, label)) for i, t, label in (
        (1, 100.0, "NEUTRAL"), (2, 100.15, "NEUTRAL"), (3, 100.31, "NEUTRAL"),
        (4, 100.45, "NEXT"), (5, 100.60, "NEXT"), (6, 100.75, "NEXT"), (7, 100.90, "NEXT"),
    )]
    window.worker = FakeWorker(packets)

    try:
        for _, prediction in packets:
            current[0] = prediction.timestamp
            window.poll()

        route.assert_not_called()
        assert window.routing.state == "PAUSED"
        assert window.viewer.position == 0
        assert window.session_summary.outcomes == []
        assert "summary full" in window.feedback.text().lower()
    finally:
        window.close()


def test_studio_context_change_drops_old_identity(monkeypatch, qapp) -> None:
    import gestureforge.app as app_module

    window = Window(model=object(), feature_function=lambda observation, hand: np.zeros(60), studio=True)
    _disable_logging(window)
    current = [200.0]
    monkeypatch.setattr(app_module.time, "monotonic", lambda: current[0])
    assert window.routing is not None
    old_snapshot = window.routing.resume()
    stale = Prediction(
        old_snapshot.session_id,
        old_snapshot.profile_id,
        1,
        200.0,
        "NEXT",
        True,
        model_version=old_snapshot.model_version,
    )
    worker = FakeWorker([(_frame(), stale)])
    window.worker = worker

    try:
        window.configure_studio(context_id="stage-2", mode=RoutingMode.REHEARSAL)
        current[0] = 200.0
        window.poll()

        assert worker.interrupted is True
        assert window.viewer.position == 0
        assert "Studio simulation" not in window.feedback.text()
        assert window.routing.snapshot.context_id == "stage-2"
        assert window.routing.snapshot.mode == RoutingMode.REHEARSAL
        assert window.prediction.text() == "Prediction: awaiting new camera session"
    finally:
        window.close()


def test_studio_focus_loss_pauses_and_invalidates_worker(monkeypatch, qapp) -> None:
    window = Window(model=object(), feature_function=lambda observation, hand: np.zeros(60), studio=True)
    _disable_logging(window)
    assert window.routing is not None
    window.routing.resume()
    worker = FakeWorker()
    window.worker = worker
    monkeypatch.setattr(window, "isActiveWindow", lambda: False)

    try:
        window.changeEvent(QEvent(QEvent.Type.ActivationChange))

        assert worker.interrupted is True
        assert window.routing.state == "PAUSED"
        assert "focus loss" in window.state.text()
    finally:
        window.close()


def test_studio_successful_close_detaches_quick_actions_focus_filter(monkeypatch, qapp) -> None:
    window = Window(model=object(), studio=True)
    _disable_logging(window)
    focus_lost = Mock()
    window.quick_actions_widget.focus_lost.connect(focus_lost)
    pause = Mock(wraps=window.pause)
    monkeypatch.setattr(window, "pause", pause)
    event = FakeCloseEvent()

    window.closeEvent(event)
    QApplication.sendEvent(qapp, QEvent(QEvent.Type.ApplicationDeactivate))

    assert event.accepted
    assert pause.call_count == 1
    focus_lost.assert_not_called()


def test_window_poll_executes_next_only_after_neutral_and_hold(monkeypatch, qapp) -> None:
    import gestureforge.app as app_module

    window = Window(model=object(), feature_function=lambda observation, hand: np.zeros(60))
    _disable_logging(window)
    current = [100.0]
    monkeypatch.setattr(app_module.time, "monotonic", lambda: current[0])
    window.controller.resume("live-session")

    packets = []
    for frame_id, timestamp, label, accepted, reason in [
        (1, 100.00, "NEUTRAL", True, ""),
        (2, 100.15, "NEUTRAL", True, ""),
        (3, 100.31, "NEUTRAL", True, ""),
        (4, 100.45, "PREVIOUS", True, ""),
        (5, 100.55, "BOOKMARK", True, ""),
        (6, 100.60, "NEXT", False, "margin_rejection"),
        (7, 100.65, "NEXT", True, ""),
        (8, 100.83, "NEXT", True, ""),
        (9, 101.00, "NEXT", True, ""),
        (10, 101.06, "NEXT", True, ""),
    ]:
        packets.append(
            (_frame(), _prediction(window, frame_id, timestamp, label, accepted=accepted, reason=reason))
        )
    window.worker = FakeWorker(packets)

    try:
        for _, prediction in list(packets):
            current[0] = prediction.timestamp
            window.poll()

        assert window.viewer.position == 1
        assert "NEXT accepted" in window.feedback.text()
        assert "Personal Setup" in window.feedback.text()
        assert "Start" in window.feedback.text()
        assert window.card_badge.text() == "2"
        assert "Card 2 of 10" in window.position.text()
    finally:
        window.close()


def test_window_pause_blocks_pending_worker_prediction_from_moving_deck(qapp) -> None:
    window = Window(model=object(), feature_function=lambda observation, hand: np.zeros(60))
    _disable_logging(window)
    window.controller.resume("live-session")
    worker = FakeWorker([(_frame(), _prediction(window, 1, time.monotonic(), "NEXT"))])
    window.worker = worker

    try:
        window.pause()
        window.poll()

        assert worker.interrupted is True
        assert window.viewer.position == 0
        assert "Card 1 of 10" in window.position.text()
    finally:
        window.close()


def test_window_shows_rejection_guidance_without_moving_deck(monkeypatch, qapp) -> None:
    import gestureforge.app as app_module

    window = Window(model=object(), feature_function=lambda observation, hand: np.zeros(60))
    _disable_logging(window)
    current = [100.0]
    monkeypatch.setattr(app_module.time, "monotonic", lambda: current[0])
    window.controller.resume("live-session")
    arm_session = window.controller.session_id
    for frame_id, timestamp in ((1, 100.00), (2, 100.15), (3, 100.31)):
        window.controller.process(
            Prediction(arm_session, "pilot", frame_id, timestamp, "NEUTRAL", True),
            timestamp,
        )
    window.worker = FakeWorker([
        (_frame(), _prediction(
            window,
            4,
            100.45,
            "BOOKMARK",
            accepted=False,
            reason="margin_rejection",
        )),
        *[
            (
                _frame(),
                _prediction(
                    window,
                    frame_id,
                    timestamp,
                    "BOOKMARK",
                    accepted=False,
                    reason="margin_rejection",
                ),
            )
            for frame_id, timestamp in ((5, 100.63), (6, 100.81), (7, 100.99))
        ],
    ])

    try:
        current[0] = 100.45
        window.poll()

        assert window.viewer.position == 0
        assert window.prediction.text() == "Prediction: Unrecognised"
        assert "Pose is ambiguous" in window.detail.text()
        assert "margin_rejection" not in window.detail.text()

        for timestamp in (100.63, 100.81, 100.99):
            current[0] = timestamp
            window.poll()

        assert window.viewer.position == 0
        assert window.controller.state == "WAIT_NEUTRAL"
        assert "Show NEUTRAL" in window.detail.text()
        assert "Pose is ambiguous" not in window.detail.text()
    finally:
        window.close()


def test_close_event_does_not_trap_window_when_worker_wait_times_out(qapp) -> None:
    window = Window(model=object(), feature_function=lambda observation, hand: np.zeros(60))
    _disable_logging(window)
    worker = FakeWorker(wait_result=False)
    window.worker = worker
    event = FakeCloseEvent()

    window.closeEvent(event)

    assert worker.interrupted is True
    assert event.accepted is True
    assert event.ignored is False
    assert window.timer.isActive() is False


def test_poll_allows_longer_cold_start_before_first_worker_result(monkeypatch, qapp) -> None:
    import gestureforge.app as app_module

    window = Window(model=object(), feature_function=lambda observation, hand: np.zeros(60))
    _disable_logging(window)
    worker = FakeWorker()
    window.worker = worker
    window.controller.resume("live-session")
    window.last_result_at = 100.0
    monkeypatch.setattr(app_module.time, "monotonic", lambda: 103.0)

    try:
        window.poll()

        assert worker.interrupted is False
        assert window.controller.state != "PAUSED"
    finally:
        window.close()


def test_main_rejects_synthetic_dataset_for_live_control(tmp_path) -> None:
    manifest = tmp_path / "manifest.json"
    feature_file = tmp_path / "features.npz"
    np.savez_compressed(feature_file, features=np.ones((1, 60), dtype=np.float32))
    digest = sha256(feature_file.read_bytes()).hexdigest()
    manifest.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "feature_version": 1,
                "labels": ["NEXT", "PREVIOUS", "BOOKMARK", "NEUTRAL"],
                "feature_file": feature_file.name,
                "feature_sha256": digest,
                "metadata": {"provenance": "SYNTHETIC", "chosen_hand": "Right"},
                "records": [
                    {
                        "participant_id": "SYNTHETIC_SOFTWARE_TEST_ONLY",
                        "session_id": "SYN-train",
                        "trial_id": "SYN-train-NEXT-00",
                        "intended_label": "NEXT",
                        "split": "train",
                        "sample_index": 0,
                        "timestamp": 0.0,
                        "valid": True,
                        "feature_index": 0,
                        "validity_reason": "",
                        "hand": "Right",
                        "provenance": "synthetic",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    completed = subprocess.run(
        [sys.executable, "-m", "gestureforge", "--dataset", str(manifest), "--smoke-test"],
        check=False,
        capture_output=True,
        text=True,
        env={**os.environ, "QT_QPA_PLATFORM": "offscreen"},
    )

    assert completed.returncode == 1
    assert "Synthetic fixtures cannot enable live control" in completed.stderr


def test_main_studio_smoke_starts_without_dataset() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "gestureforge", "--studio", "--smoke-test"],
        check=False,
        capture_output=True,
        text=True,
        env={**os.environ, "QT_QPA_PLATFORM": "offscreen"},
        timeout=20,
    )

    assert completed.returncode == 0


@pytest.mark.parametrize("studio", [False, True])
@pytest.mark.parametrize("custom", [False, True])
def test_main_selects_dataset_vocabulary_without_changing_assignment(studio, custom, monkeypatch) -> None:
    from gestureforge import __main__ as launcher
    from gestureforge.fixtures import synthetic_dataset
    from gestureforge.vocabulary import LEGACY_VOCABULARY

    vocabulary = GestureVocabulary(("G1", "G2", "G3")) if custom else LEGACY_VOCABULARY
    bundle = synthetic_dataset(trials_per_label_per_split=2)
    features, labels, records = bundle.training_data()
    mapping = dict(zip(LEGACY_VOCABULARY.labels, vocabulary.labels, strict=True))
    # Mock only the human-data gate; synthetic arrays never become participant files.
    dataset = SimpleNamespace(
        vocabulary=vocabulary, metadata={"chosen_hand": "Right"},
        records=[SimpleNamespace(provenance="human", participant_id="MOCK_GATE_ONLY")],
        training_data=lambda: (features, np.array([mapping[label] for label in labels]), records),
    )
    monkeypatch.setattr("gestureforge.dataset.load_dataset", lambda _: dataset)
    application = Mock()
    application.exec.return_value = 0
    monkeypatch.setattr("PySide6.QtWidgets.QApplication", Mock(return_value=application))
    window = Mock()
    monkeypatch.setattr("gestureforge.app.Window", window)
    monkeypatch.setattr(sys, "argv", ["gestureforge", "--dataset", "mock-manifest.json"]
                        + (["--studio"] if studio else []))
    if custom and not studio:
        with pytest.raises(SystemExit) as exc:
            launcher.main()
        assert exc.value.code == 1
        window.assert_not_called()
        return
    assert launcher.main() == 0
    model = window.call_args.args[0]
    assert set(model.train_labels) == set(vocabulary.labels)
    assert model.model_version.startswith("gesture-v1-" if studio else "prototype-v3")
    assert window.call_args.kwargs["vocabulary"] == vocabulary


@pytest.mark.parametrize(
    "argv, message, code",
    [
        (["gestureforge", "--profile-id", "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"], "--profile-id is available only", 1),
        (
            [
                "gestureforge", "--studio", "--profile-id", "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
                "--dataset", "manifest.json",
            ],
            "--profile-id cannot be used with --dataset",
            1,
        ),
        (
            ["gestureforge", "--studio", "--profile-id", "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", "--algorithm", "svm"],
            "Saved profiles use their stored model settings",
            1,
        ),
        (
            ["gestureforge", "--studio", "--profile-id", "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", "--mult=2"],
            "unrecognized arguments",
            2,
        ),
    ],
)
def test_main_profile_cli_rejects_conflicts(argv, message, code, monkeypatch, capsys) -> None:
    from gestureforge import __main__ as launcher

    monkeypatch.setattr(sys, "argv", argv)
    with pytest.raises(SystemExit) as exc:
        launcher.main()
    assert exc.value.code == code
    assert message in capsys.readouterr().err


def test_main_profile_cli_loads_saved_profile_settings(monkeypatch) -> None:
    from gestureforge import __main__ as launcher
    import gestureforge.app as app_module

    loaded = _loaded_profile("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", "Desk profile")
    application = Mock()
    application.exec.return_value = 0
    monkeypatch.setattr("PySide6.QtWidgets.QApplication", Mock(return_value=application))
    window = Mock()
    monkeypatch.setattr(app_module, "Window", window)
    monkeypatch.setattr("gestureforge.profiles.ProfileStore.load", Mock(return_value=loaded))
    monkeypatch.setattr(sys, "argv", [
        "gestureforge", "--studio", "--profile-id", loaded.record.profile_id,
        "--profile-store", "private-profiles",
    ])

    assert launcher.main() == 0
    assert window.call_args.args[0] is loaded.model
    assert window.call_args.args[5] == loaded.record.profile_id
    assert window.call_args.kwargs["profile_display_name"] == "Desk profile"
    assert window.call_args.kwargs["model_settings"] == ("knn", 2.0, 1.5)
    assert window.call_args.kwargs["profile_store"].root.name == "private-profiles"
    assert window.call_args.kwargs["loaded_profile"] is loaded
    assert "readiness unverified" in window.call_args.args[6]


def test_custom_classifier_labels_reach_studio_simulation(monkeypatch, qapp) -> None:
    from gestureforge.fixtures import synthetic_dataset
    from gestureforge.models import train_model
    from gestureforge.vocabulary import LEGACY_VOCABULARY

    vocabulary = GestureVocabulary(("G1", "G2", "G3"))
    features, labels, records = synthetic_dataset(trials_per_label_per_split=2).training_data()
    mapping = dict(zip(LEGACY_VOCABULARY.labels, vocabulary.labels, strict=True))
    labels = np.array([mapping[label] for label in labels])
    model = train_model(features, labels, vocabulary=vocabulary,
                        groups=[record.trial_id for record in records])
    window = Window(model=model, studio=True, vocabulary=vocabulary)
    _disable_logging(window)
    assert window.routing is not None
    current = [100.0]
    monkeypatch.setattr("gestureforge.app.time.monotonic", lambda: current[0])
    try:
        assert [label.text() for label in window.binding_labels] == [f"{g} gesture" for g in vocabulary.action_ids]
        assert window.routing.snapshot.model_version == model.model_version
        window.routing.resume()
        packets = []
        for i, timestamp, gesture in (
            (1, 100.0, "NEUTRAL"), (2, 100.15, "NEUTRAL"), (3, 100.31, "NEUTRAL"),
            (4, 100.45, "G1"), (5, 100.60, "G1"), (6, 100.75, "G1"), (7, 100.90, "G1"),
            (8, 101.05, "G1"),
        ):
            label, accepted, _ = model.predict(features[np.flatnonzero(labels == gesture)[0]])
            assert accepted and label == gesture
            packets.append((_frame(), _studio_prediction(window, i, timestamp, label)))
        window.worker = FakeWorker(packets)
        for _, prediction in packets:
            current[0] = prediction.timestamp
            window.poll()
        assert "G1 would show next card" in window.feedback.text()
        assert window.routing.state == "LATCHED"
        assert window.viewer.position == 0
    finally:
        window.close()


def test_studio_capture_controls_and_active_legend_stay_visible_when_scrolling(qapp) -> None:
    window = Window(model=object(), studio=True)
    _disable_logging(window)
    window.resize(900, 620)
    content = window.studio_scroll.widget()
    assert content is not None
    content.setMinimumHeight(1500)
    window.show()
    qapp.processEvents()
    try:
        window.configure_studio(context_id="training-stage")
        assert "Context: training-stage" in window.boundary.text()
        assert {"Profiles", "Enrolment", "Practice", "Quick Actions"} <= {
            window.deck_tabs.tabText(index) for index in range(window.deck_tabs.count())
        }
        assert isinstance(window.deck_tools, QGridLayout)
        assert window.deck_tools.count() == len(window.file_tool_buttons) == 6
        assert window.studio_scroll.horizontalScrollBar().maximum() == 0
        widgets = (window.start_button, window.pause_button, window.state, window.progress,
                   window.boundary, window.prediction, window.detail)
        before = [widget.mapTo(window, QPoint(0, 0)).y() for widget in widgets]
        scrollbar = window.studio_scroll.verticalScrollBar()
        assert scrollbar.maximum() > 0
        scrollbar.setValue(scrollbar.maximum())
        qapp.processEvents()
        assert before == [widget.mapTo(window, QPoint(0, 0)).y() for widget in widgets]
        assert all(widget.isVisible() and window.rect().contains(
            widget.rect().translated(widget.mapTo(window, QPoint(0, 0)))
        ) for widget in widgets)
        assert window.routing is not None
        window.routing.resume()
        window.pause_button.click()
        assert window.routing.state == "PAUSED"
        assert window.viewer.position == 0
    finally:
        window.close()


def test_studio_rearm_feedback_distinguishes_rejection_and_neutral_hold(monkeypatch, qapp):
    import gestureforge.app as app_module

    window = Window(model=object(), studio=True)
    _disable_logging(window)
    worker = FakeWorker()
    current = [100.0]
    monkeypatch.setattr(app_module, "CaptureWorker", lambda *a: worker)
    monkeypatch.setattr(app_module.time, "monotonic", lambda: current[0])
    window.start_camera()
    assert window.routing is not None
    frame_id = 0

    def feed(timestamp, label, reason=""):
        nonlocal frame_id
        frame_id += 1
        current[0] = timestamp
        prediction = replace(_studio_prediction(window, frame_id, timestamp, label),
                             accepted=not reason, rejection_reason=reason)
        worker.packets = [(_frame(), prediction)]
        window.poll()

    try:
        for timestamp in (100.0, 100.15, 100.31):
            feed(timestamp, "NEUTRAL")
        for timestamp in (100.45, 100.60, 100.75, 100.86):
            feed(timestamp, "NEXT")
        assert window.routing.state == "LATCHED"
        feed(101.00, "UNKNOWN", "margin_rejection")
        assert window.prediction.text() == "Prediction: Unrecognised"
        assert "Pose is ambiguous" in window.detail.text()
        assert "NEUTRAL" in window.detail.text()
        assert window.progress.value() == 0  # Waiting to rearm, not a completed neutral hold.
        feed(101.15, "NEUTRAL")
        assert window.routing.state == "WAIT_NEUTRAL"
        assert "Keep holding NEUTRAL" in window.detail.text()
        assert "margin_rejection" not in window.detail.text()
        feed(101.30, "NEUTRAL")
        assert 0 < window.progress.value() < 100
        feed(101.46, "NEUTRAL")
        assert window.routing.state == "READY"
        assert "READY" in window.detail.text()
        assert window.viewer.position == 0  # Preview never changes the actual deck.
        window.pause()
        assert window.prediction.text() == "Prediction: camera paused"
        worker.finished = True
        window.poll()
        worker = FakeWorker()
        window.start_camera()
        assert window.prediction.text() == "Prediction: awaiting camera"
        assert window.progress.value() == 0
    finally:
        window.close()


def test_studio_rejects_startup_live_mode_but_allows_explicit_manual_live(qapp) -> None:
    with pytest.raises(ValueError, match="simulation modes only"):
        Window(studio=True, studio_mode=RoutingMode.LIVE)
    window = Window(studio=True)
    _disable_logging(window)
    try:
        assert window.routing is not None
        assert window.configure_studio(mode=RoutingMode.LIVE)
        assert window.routing.snapshot.mode == RoutingMode.LIVE
        assert "Studio Live" in window.boundary.text()
        assert "Live manual controls active" in window.boundary.text()
        assert "Gesture launch blocked" in window.boundary.text()
    finally:
        window.close()


def test_studio_binding_editor_applies_once_then_new_hold_simulates_new_action(monkeypatch, qapp) -> None:
    import gestureforge.app as app_module

    window = Window(model=object(), studio=True)
    _disable_logging(window)
    assert window.routing is not None
    old = window.routing.resume()
    worker = FakeWorker([(_frame(), _studio_prediction(window, 1, 100.0, "NEXT"))])
    window.worker = worker
    current = [100.0]
    monkeypatch.setattr(app_module.time, "monotonic", lambda: current[0])
    try:
        # Editing is a draft: no implicit remapping or restart during a hold.
        window.binding_pickers[0].setCurrentIndex(1)  # NEXT gesture -> PREVIOUS action
        window.mode_picker.setCurrentIndex(1)
        assert window.routing.snapshot == old
        window.apply_bindings_button.click()
        assert worker.interrupted
        assert window.routing.state == "PAUSED"
        assert window.routing.snapshot.session_id != old.session_id
        assert window.routing.snapshot.mode == RoutingMode.REHEARSAL
        assert dict(window.routing.snapshot.bindings)["NEXT"] == Action(ActionType.PREVIOUS)
        window.poll()
        assert window.prediction.text() == "Prediction: awaiting new camera session"
        assert window.viewer.position == 0
        assert "NEXT: would show previous card" in window.boundary.text()

        window.routing.resume()
        packets = [(_frame(), _studio_prediction(window, i, t, label)) for i, t, label in (
            (1, 101.0, "NEUTRAL"), (2, 101.15, "NEUTRAL"), (3, 101.31, "NEUTRAL"),
            (4, 101.45, "NEXT"), (5, 101.60, "NEXT"), (6, 101.75, "NEXT"), (7, 101.90, "NEXT"),
        )]
        window.worker = FakeWorker(packets)
        for _, prediction in packets:
            current[0] = prediction.timestamp
            window.poll()
        assert "NEXT would show previous card" in window.feedback.text()
        assert window.viewer.position == 0
    finally:
        window.close()


def test_studio_invalid_draft_preserves_active_session_and_custom_mapping_survives_mode_change(qapp) -> None:
    window = Window(studio=True, vocabulary=GestureVocabulary(("G1", "G2", "G3")))
    _disable_logging(window)
    assert window.routing is not None
    try:
        window.configure_studio(context_id="stage-2", bindings={"G1": Action(ActionType.BOOKMARK)})
        old = window.routing.resume()
        worker = FakeWorker()
        window.worker = worker
        with pytest.raises(ValueError):
            window.configure_studio(bindings={"NEUTRAL": Action(ActionType.NEXT)})
        with pytest.raises(ValueError, match="selected dataset vocabulary"):
            window.configure_studio(bindings={"NOT_ENROLLED": Action(ActionType.NEXT)})
        assert window.routing.snapshot == old
        assert not worker.interrupted
        assert window.routing.state == "WAIT_NEUTRAL"
        window.mode_picker.setCurrentIndex(1)
        window.apply_bindings_button.click()
        assert window.routing.snapshot.context_id == "stage-2"
        assert dict(window.routing.snapshot.bindings) == {"G1": Action(ActionType.BOOKMARK)}
        assert window.binding_labels[0].text() == "G1 gesture"
        assert window.binding_pickers[1].isHidden()
        assert worker.interrupted
    finally:
        window.close()


@pytest.mark.parametrize("change", ["pause", "session", "profile", "model"])
def test_studio_discards_interrupted_or_wrong_identity_packet_before_display(change, monkeypatch, qapp) -> None:
    import gestureforge.app as app_module

    window = Window(model=object(), studio=True)
    _disable_logging(window)
    assert window.routing is not None
    window.routing.resume()
    packet = _studio_prediction(window, 1, 100.0, "NEXT")
    packet = replace(
        packet,
        session_id="other" if change == "session" else packet.session_id,
        profile_id="other" if change == "profile" else packet.profile_id,
        model_version="other" if change == "model" else packet.model_version,
    )
    window.worker = FakeWorker([(_frame(), packet)])
    window.last_result_at = 100.0
    monkeypatch.setattr(app_module.time, "monotonic", lambda: 100.0)
    try:
        before = window.prediction.text()
        if change == "pause":
            window.pause()
            assert window.prediction.text() == "Prediction: camera paused"
            before = window.prediction.text()
        window.poll()
        assert window.prediction.text() == before
        assert "Studio simulation" not in window.feedback.text()
        assert window.viewer.position == 0
    finally:
        window.close()


def _candidate_model(vocabulary):
    # Lightweight adapter test double; classifier correctness has its own numeric tests.
    return SimpleNamespace(
        predict=lambda _: (vocabulary.action_ids[0], True, ""),
        train_labels=vocabulary.labels, model_version="gesture-test-revision-2",
        config=SimpleNamespace(algorithm="knn", multiplier=2.0, margin=1.5),
    )


def _loaded_profile(profile_id: str, name: str, vocabulary=None, *, hand="Right"):
    from gestureforge.profiles import ProfileSettings
    from gestureforge.vocabulary import LEGACY_VOCABULARY

    vocabulary = vocabulary or LEGACY_VOCABULARY
    return SimpleNamespace(
        record=SimpleNamespace(
            profile_id=profile_id,
            display_name=name,
            selected_hand=hand,
            vocabulary=vocabulary,
            settings=ProfileSettings("knn", 2.0, 1.5),
        ),
        model=_candidate_model(vocabulary),
    )


def test_studio_background_load_switches_once_and_waits_for_camera_release(monkeypatch, qapp) -> None:
    from threading import Event
    import gestureforge.app as app_module

    vocabulary = GestureVocabulary(("G1", "G2", "G3"))
    candidate = _candidate_model(vocabulary)
    release = Event()
    entered = Event()
    calls = []

    def load(path, *settings, studio):
        calls.append((path, settings, studio))
        entered.set()
        assert release.wait(5)
        return candidate, "Left", "P02", vocabulary

    monkeypatch.setattr(app_module, "load_personal_model", load)
    window = Window(model=object(), studio=True, model_settings=("knn", 2.0, 1.5))
    _disable_logging(window)
    assert window.routing is not None
    old = window.routing.resume()
    packet = (_frame(), _studio_prediction(window, 1, 100.0, "NEXT"))
    camera = FakeWorker([packet])
    window.worker = camera
    try:
        assert window.load_studio_dataset("personal.json")
        loader = window.model_loader
        assert loader is not None
        assert entered.wait(5)
        assert camera.interrupted
        assert not window.start_button.isEnabled()
        assert not window.load_dataset_button.isEnabled()
        assert not window.apply_camera_button.isEnabled()
        assert not window.load_progress.isHidden()
        with pytest.raises(ValueError, match="Wait for the dataset load"):
            window.set_studio_camera(1)
        assert not window.load_studio_dataset("another.json")
        window.start_camera()
        assert window.worker is camera
        with pytest.raises(ValueError, match="Wait for the dataset load"):
            window.configure_studio(context_id="stage-2")
        release.set()
        loader.join(5)
        assert not loader.is_alive()
        window.poll()
        assert calls == [("personal.json", ("knn", 2.0, 1.5), True)]
        assert window.model is candidate and window.chosen_hand == "Left" and window.profile == "P02"
        assert window.routing.snapshot.session_id != old.session_id
        assert window.routing.snapshot.model_version == candidate.model_version
        assert window.routing.snapshot.mode == RoutingMode.PREVIEW
        assert window.routing.state == "PAUSED"
        assert window.binding_labels[0].text() == "G1 gesture"
        assert window.prediction.text() == "Prediction: awaiting new camera session"
        assert window.viewer.position == 0
        assert not window.start_button.isEnabled()
        camera.finished = True
        window.poll()
        assert window.worker is None and window.start_button.isEnabled()
        assert window.load_dataset_button.isEnabled()
        assert window.apply_camera_button.isEnabled()
        assert window.load_progress.isHidden()
        window.routing.resume()
        assert window.routing.state == "WAIT_NEUTRAL"
    finally:
        release.set()
        if window.model_loader is not None:
            window.model_loader.join(5)
        window.close()


def test_saved_profile_switch_keeps_name_separate_and_raw_dataset_clears_it(qapp) -> None:
    from gestureforge.vocabulary import LEGACY_VOCABULARY

    first = _loaded_profile("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", "Desk profile", LEGACY_VOCABULARY)
    custom_vocabulary = GestureVocabulary(("G1", "G2", "G3"))
    second = _loaded_profile("bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb", "Custom profile", custom_vocabulary, hand="Left")
    dataset_model = _candidate_model(LEGACY_VOCABULARY)
    window = Window(studio=True)
    _disable_logging(window)
    try:
        window.use_studio_profile(first)
        assert window.profile == first.record.profile_id
        assert window.selected_profile_id == first.record.profile_id
        assert window.selected_profile_name == "Desk profile"
        assert "Desk profile" in window.camera_status.text()
        assert "readiness unverified" in window.notice.text()

        window.use_studio_profile(second)
        assert window.profile == second.record.profile_id
        assert window.selected_profile_id == second.record.profile_id
        assert window.chosen_hand == "Left"
        assert [label.text() for label in window.binding_labels] == ["G1 gesture", "G2 gesture", "G3 gesture"]

        window.use_studio_model(dataset_model, "Right", "P02", LEGACY_VOCABULARY)
        assert window.profile == "P02"
        assert window.selected_profile_id is None
        assert window.selected_profile_name == ""
        assert "Profile: P02" in window.camera_status.text()
    finally:
        window.close()


def test_saved_profile_background_load_failure_retains_active_profile(qapp) -> None:
    active = _loaded_profile("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", "Active profile")
    window = Window(studio=True)
    _disable_logging(window)

    class Store:
        def load(self, profile_id):
            raise ValueError("profile checksum mismatch")

    try:
        window.use_studio_profile(active)
        assert window.routing is not None
        old = window.routing.resume()
        assert window.load_studio_profile(cast(Any, Store()), "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb")
        assert window.model_loader is not None
        window.model_loader.join(5)
        window.poll()
        assert window.selected_profile_id == active.record.profile_id
        assert window.routing is not None
        assert window.routing.snapshot == old
        assert "Profile not loaded" in window.notice.text()
        assert window.model_loader is None
        assert window.load_dataset_button.isEnabled()
    finally:
        window.close()


def test_clear_saved_profile_blocks_pending_load_and_invalidates_active_packets(monkeypatch, qapp) -> None:
    from threading import Event
    import gestureforge.app as app_module

    active = _loaded_profile("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", "Active profile")
    pending = _loaded_profile("bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb", "Deleted profile")
    release = Event()
    entered = Event()

    class Store:
        def load(self, profile_id):
            entered.set()
            assert release.wait(5)
            return pending

    window = Window(studio=True)
    _disable_logging(window)
    try:
        window.use_studio_profile(active)
        assert window.routing is not None
        old = window.routing.resume()
        stale_packet = replace(
            _studio_prediction(window, 1, 100.0, "NEXT"),
            session_id=old.session_id,
            profile_id=old.profile_id,
            model_version=old.model_version,
        )
        assert window.load_studio_profile(cast(Any, Store()), pending.record.profile_id)
        assert entered.wait(5)
        assert window.prepare_studio_profile_delete(pending.record.profile_id)
        assert window.clear_studio_profile(pending.record.profile_id)
        release.set()
        assert window.model_loader is not None
        window.model_loader.join(5)
        window.poll()
        assert window.selected_profile_id == active.record.profile_id
        assert window.model is active.model
        assert "ignored" in window.notice.text()

        assert window.prepare_studio_profile_delete(active.record.profile_id)
        assert window.clear_studio_profile(active.record.profile_id)
        assert window.model is None
        assert window.selected_profile_id is None
        assert window.routing_manual_only
        assert window.routing is not None
        assert window.routing.snapshot.session_id != old.session_id
        window.worker = FakeWorker([(_frame(), stale_packet)])
        monkeypatch.setattr(app_module.time, "monotonic", lambda: 100.0)
        window.poll()
        assert "Studio simulation" not in window.feedback.text()
        assert "Manual viewer remains" in window.feedback.text()
        assert not window.start_button.isEnabled()
    finally:
        release.set()
        if window.model_loader is not None:
            window.model_loader.join(5)
        window.close()


def test_deleted_profile_retry_pauses_active_capture_and_honors_trace_failure(tmp_path, qapp) -> None:
    active = _loaded_profile("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", "Active profile")
    deleted_id = "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
    window = Window(studio=True)
    _disable_logging(window)

    class Store:
        def load(self, profile_id):
            raise AssertionError("Deleted profiles must be rejected before storage load.")

    try:
        window.use_studio_profile(active)
        assert window.routing is not None
        window.routing.resume()
        worker = FakeWorker()
        window.worker = worker
        window._deleted_profile_ids.add(deleted_id)

        assert not window.load_studio_profile(cast(Any, Store()), deleted_id)
        assert worker.interrupted
        assert window.routing.state == "PAUSED"
        assert window.model is active.model
        assert window.selected_profile_id == active.record.profile_id
        assert window.model_loader is None
        assert "profile was deleted" in window.notice.text()

        trace = SimpleNamespace(frame_count=1, save=Mock(side_effect=OSError("disk full")))
        window.evaluation_trace = cast(Any, trace)
        window.trace_path = tmp_path / "trace.json"
        assert not window.load_studio_profile(cast(Any, Store()), deleted_id)
        assert window.evaluation_trace is trace
        assert "disk full" in window.trace_status.text()
        assert "profile was deleted" in window.notice.text()
    finally:
        window.evaluation_trace = None
        window.close()


@pytest.mark.parametrize("failure", ["file", "labels", "identity"])
def test_failed_studio_load_retains_selection_and_allows_retry(failure, monkeypatch, qapp) -> None:
    import gestureforge.app as app_module
    from gestureforge.vocabulary import LEGACY_VOCABULARY

    old_model = _candidate_model(LEGACY_VOCABULARY)
    candidate = _candidate_model(LEGACY_VOCABULARY)
    if failure == "labels":
        candidate.train_labels = ("UNTRAINED",)

    def load(*args, **kwargs):
        if failure == "file":
            raise ValueError("Feature checksum mismatch")
        return candidate, "Right", "invalid/profile" if failure == "identity" else "P02", LEGACY_VOCABULARY

    monkeypatch.setattr(app_module, "load_personal_model", load)
    window = Window(model=old_model, studio=True)
    _disable_logging(window)
    assert window.routing is not None
    old = window.routing.resume()
    try:
        assert window.load_studio_dataset("broken.json")
        assert window.model_loader is not None
        window.model_loader.join(5)
        window.poll()
        assert window.model is old_model
        assert window.routing.snapshot == old
        assert window.routing.state == "PAUSED"
        assert "Dataset not loaded" in window.notice.text()
        assert "Manual controls remain available" in window.notice.text()
        assert "personal TRAIN manifest" in window.notice.text()
        assert "Guest/manual" in window.notice.text()
        assert window.start_button.isEnabled() and window.load_dataset_button.isEnabled()
        assert window.model_loader is None
        error_notice = window.notice.text()
        assert window.configure_studio(mode=RoutingMode.LIVE)
        assert window.notice.text() == error_notice
        monkeypatch.setattr(
            app_module, "load_personal_model",
            lambda *args, **kwargs: (old_model, "Right", "P02", LEGACY_VOCABULARY),
        )
        assert window.load_studio_dataset("fixed.json")
        assert window.model_loader is not None
        window.model_loader.join(5)
        window.poll()
        assert window.profile == "P02"
        assert "Dataset not loaded" not in window.notice.text()
    finally:
        window.close()


def test_closing_during_training_never_installs_finished_model(monkeypatch, qapp) -> None:
    from threading import Event
    import gestureforge.app as app_module
    from gestureforge.vocabulary import LEGACY_VOCABULARY

    release = Event()
    candidate = _candidate_model(LEGACY_VOCABULARY)

    def load(*args, **kwargs):
        assert release.wait(5)
        return candidate, "Right", "P02", LEGACY_VOCABULARY

    monkeypatch.setattr(app_module, "load_personal_model", load)
    window = Window(studio=True)
    _disable_logging(window)
    try:
        window.load_studio_dataset("personal.json")
        loader = window.model_loader
        assert loader is not None
        window.close()
        release.set()
        loader.join(5)
        window.poll()
        assert window.model is None
        assert not window.timer.isActive()
        window.start_camera()
        assert window.worker is None
        assert not window.load_studio_dataset("second.json")
    finally:
        release.set()
        window.close()


def test_in_app_loader_rejects_real_synthetic_manifest(tmp_path, qapp) -> None:
    from gestureforge.fixtures import save_synthetic_dataset

    dataset = save_synthetic_dataset(tmp_path)
    window = Window(studio=True)
    _disable_logging(window)
    try:
        window.load_studio_dataset(dataset.manifest_path)
        assert window.model_loader is not None
        window.model_loader.join(5)
        window.poll()
        assert window.model is None and window.worker is None
        assert "Synthetic fixtures cannot enable live control" in window.notice.text()
        assert window.load_dataset_button.isEnabled()
        assert not window.start_button.isEnabled()
    finally:
        window.close()


@pytest.mark.parametrize("split", ["validation", "validation_negative"])
def test_personal_loader_explains_evaluation_only_manifest(split, tmp_path, monkeypatch) -> None:
    import gestureforge.models as models_module
    from gestureforge.app import load_personal_model
    from gestureforge.dataset import SampleRecord, save_dataset

    # Generated software regression data; this does not represent participant evidence.
    record = SampleRecord(
        participant_id="TEST_PERSON", session_id="test-evaluation", trial_id="trial-1",
        intended_label="UNKNOWN" if split == "validation_negative" else "NEXT",
        split=split, sample_index=0, timestamp=0.0, valid=True, feature_index=0,
        hand="Right", provenance="human",
    )
    bundle = save_dataset(tmp_path, [record], np.zeros((1, 60)), {"chosen_hand": "Right"})
    train = Mock(side_effect=AssertionError("Evaluation-only rows must not be used for training"))
    monkeypatch.setattr(models_module, "train_model", train)

    with pytest.raises(ValueError, match="no valid TRAIN samples.*personal TRAIN manifest"):
        load_personal_model(bundle.manifest_path, studio=True)
    train.assert_not_called()


def test_camera_change_waits_for_release_and_restarts_with_fresh_identity(monkeypatch, qapp) -> None:
    import gestureforge.app as app_module

    window = Window(model=object(), studio=True)
    _disable_logging(window)
    assert window.routing is not None
    window.configure_studio(context_id="stage-2", mode=RoutingMode.REHEARSAL)
    old = window.routing.resume()
    previous = FakeWorker([(_frame(), _studio_prediction(window, 1, 100.0, "NEXT"))])
    window.worker = previous
    factory = Mock()
    replacement = FakeWorker()
    factory.return_value = replacement
    monkeypatch.setattr(app_module, "CaptureWorker", factory)
    try:
        window.camera_picker.setValue(1)
        assert window.camera_index == 0 and window.routing.snapshot == old
        window.apply_camera_button.click()
        changed = window.routing.snapshot
        assert window.camera_index == 1 and previous.interrupted
        assert changed.session_id != old.session_id
        assert changed.context_id == old.context_id and changed.bindings == old.bindings
        assert changed.mode == RoutingMode.REHEARSAL and window.routing.state == "PAUSED"
        window.start_camera()
        factory.assert_not_called()
        window.poll()
        assert window.prediction.text() == "Prediction: awaiting new camera session"
        assert window.preview.pixmap().isNull()
        previous.finished = True
        window.poll()
        assert window.worker is None and window.start_button.isEnabled()
        window.start_camera()
        assert factory.call_args.args[3] == 1
        assert factory.call_args.args[5] == window.routing.snapshot.session_id
        assert window.routing.snapshot.session_id != changed.session_id
        replacement.start.assert_called_once()
        assert window.routing.state == "WAIT_NEUTRAL"
        active = window.routing.snapshot
        assert not window.set_studio_camera(1)
        assert window.routing.snapshot == active and not replacement.interrupted
    finally:
        window.close()


@pytest.mark.parametrize("index", [-1, True, 1.5, "1", 2**31])
def test_invalid_camera_index_preserves_active_studio(index, qapp) -> None:
    window = Window(model=object(), studio=True)
    _disable_logging(window)
    assert window.routing is not None
    old = window.routing.resume()
    worker = FakeWorker()
    window.worker = worker
    try:
        with pytest.raises(ValueError):
            window.set_studio_camera(index)
        assert window.camera_index == 0 and window.routing.snapshot == old
        assert not worker.interrupted
    finally:
        window.close()


def test_studio_camera_failure_clears_preview_and_preserves_manual_controls(monkeypatch, qapp) -> None:
    import gestureforge.app as app_module

    window = Window(model=object(), studio=True)
    _disable_logging(window)
    assert window.routing is not None
    window.routing.resume()
    worker = FakeWorker([(_frame(), _studio_prediction(window, 1, 100.0, "NEUTRAL"))])
    window.worker = worker
    monkeypatch.setattr(app_module.time, "monotonic", lambda: 100.0)
    try:
        window.poll()
        assert not window.preview.pixmap().isNull()
        worker.error = "Camera disconnected"
        worker.finished = True
        window.poll()
        assert window.worker is None and window.routing.state == "PAUSED"
        assert window.preview.pixmap().isNull()
        assert "Camera disconnected" in window.detail.text()
        assert "permissions" in window.detail.text()
        assert window.start_button.isEnabled()
        _set_live_manual(window)
        window.next_card()
        assert window.viewer.position == 1
    finally:
        window.close()
