"""Offscreen widget requests, persistence and empty-content regressions."""
from pathlib import Path
from typing import Any

import pytest
from PySide6.QtCore import QEvent
from PySide6.QtWidgets import QApplication, QPushButton

from gestureforge.contracts import Action, ActionType, RoutingMode
from gestureforge.javier_preview import PreviewWindow
from gestureforge.javier_widgets import QuickActionsWidget, RunbookEditorWidget, RunbookWidget, ViewerWidget
from gestureforge.runbook import Runbook
from gestureforge.shortcuts import Target, TargetKind, TargetRegistry
from gestureforge.viewer import Viewer
from gestureforge.workspace import Stage, Workspace, WorkspaceStore


@pytest.fixture(scope='module')
def qt_app():
    app = QApplication.instance() or QApplication([])
    yield app


def click(widget, text: str) -> None:
    for button in widget.findChildren(QPushButton):
        if button.text() == text:
            button.click()
            return
    raise AssertionError(f'button missing: {text}')


def test_quick_empty_content_three_slots_no_launch_and_paused_reload(qt_app, tmp_path: Path) -> None:
    registry = TargetRegistry()
    state = tmp_path / 'targets.json'
    widget = QuickActionsWidget(registry, state)
    requests: list[Action] = []
    widget.action_requested.connect(requests.append)
    assert len(widget.slots) == 3
    assert all(not button.isEnabled() for button in widget.launch_buttons)
    registry.save(state)
    restored = QuickActionsWidget(TargetRegistry(), state)
    assert restored.registry.targets == ()
    assert restored.registry.quick_slots == (None, None, None)
    assert requests == []
    widget.close()
    restored.close()


def test_quick_target_editor_and_slot_only_emit_requests(qt_app, tmp_path: Path) -> None:
    widget = QuickActionsWidget(TargetRegistry(), tmp_path / 'targets.json')
    requests: list[Action] = []
    changes: list[Any] = []
    widget.action_requested.connect(requests.append)
    widget.bindings_changed.connect(changes.append)
    widget.target_id.setText('calculator')
    widget.label.setText('My calculator')
    widget.kind.setCurrentIndex(widget.kind.findData(TargetKind.BUILTIN))
    widget.value.setText('calculator')
    click(widget, 'Save target')
    assert len(widget.registry.targets) == 1
    assert requests == []
    widget.slots[0].setCurrentIndex(widget.slots[0].findData('calculator'))
    assert widget.launch_buttons[0].isEnabled() and changes
    widget.launch_buttons[0].click()
    assert requests == [Action(ActionType.OPEN_SHORTCUT, 'calculator')]
    other = TargetRegistry()
    other.restore(tmp_path / 'targets.json')
    assert other.quick_slots == ('calculator', None, None)
    widget.close()


def test_quick_save_failure_does_not_publish_registry_or_callbacks(qt_app, tmp_path: Path) -> None:
    state = tmp_path / 'state-as-dir'
    state.mkdir()
    registry = TargetRegistry()
    widget = QuickActionsWidget(registry, state)
    changes: list[Any] = []
    widget.bindings_changed.connect(changes.append)
    widget.target_id.setText('calculator')
    widget.label.setText('Calculator')
    widget.kind.setCurrentIndex(widget.kind.findData(TargetKind.BUILTIN))
    widget.value.setText('calculator')
    click(widget, 'Save target')
    assert registry.targets == ()
    assert changes == []
    assert 'Cannot save target' in widget.status.text()
    registry.configure(Target('calculator', 'Calculator', TargetKind.BUILTIN, 'calculator'))
    widget.refresh()
    widget.slots[0].setCurrentIndex(widget.slots[0].findData('calculator'))
    assert registry.quick_slots == (None, None, None) and changes == []
    click(widget, 'Delete target')
    assert len(registry.targets) == 1 and changes == []
    assert widget.registry is registry
    widget.close()


def test_quick_closed_widget_no_longer_emits_focus_lost(qt_app) -> None:
    widget = QuickActionsWidget(TargetRegistry())
    pauses: list[bool] = []
    widget.focus_lost.connect(lambda: pauses.append(True))
    widget.close()
    QApplication.sendEvent(qt_app, QEvent(QEvent.Type.ApplicationDeactivate))
    assert pauses == []
    widget.show()
    QApplication.sendEvent(qt_app, QEvent(QEvent.Type.ApplicationDeactivate))
    assert pauses
    widget.close()


def test_quick_invalid_target_and_lost_focus_signal(qt_app) -> None:
    widget = QuickActionsWidget(TargetRegistry())
    widget.target_id.setText('site')
    widget.label.setText('Website')
    widget.kind.setCurrentIndex(widget.kind.findData(TargetKind.WEBSITE))
    widget.value.setText('javascript:alert(1)')
    click(widget, 'Save target')
    assert not widget.registry.targets
    assert 'Cannot save' in widget.status.text()
    pauses = []
    widget.focus_lost.connect(lambda: pauses.append(True))
    QApplication.sendEvent(qt_app, QEvent(QEvent.Type.ApplicationDeactivate))
    assert pauses
    widget.close()


def test_quick_missing_target_visible_and_launch_disabled(qt_app, tmp_path: Path) -> None:
    path = tmp_path / 'reference.txt'
    path.write_text('fixture')
    registry = TargetRegistry()
    registry.configure(Target('reference', 'Reference', TargetKind.FILE, str(path)))
    registry.bind_quick(('reference', None, None))
    path.unlink()
    widget = QuickActionsWidget(registry)
    assert not widget.launch_buttons[0].isEnabled()
    assert 'unavailable' in widget.launch_buttons[0].text()
    assert 'Unavailable' in widget.library.item(0).text()
    widget.close()


def test_viewer_widget_plain_text_boundary_buttons_and_explicit_remove(qt_app) -> None:
    viewer = Viewer(project_actions=True)
    widget = ViewerWidget(viewer)
    requests: list[Action] = []
    widget.action_requested.connect(requests.append)
    assert not widget.buttons[ActionType.PREVIOUS].isEnabled()
    widget.buttons[ActionType.NEXT].click()
    assert requests == [Action(ActionType.NEXT)] and viewer.position == 0
    viewer.bookmark()
    widget.refresh()
    assert widget.bookmarks.count() == 1
    assert not widget.buttons[ActionType.BOOKMARK].isEnabled()
    widget.bookmarks.setCurrentRow(0)
    click(widget, 'Remove selected bookmark')
    assert viewer.bookmarks == ()
    widget.close()


def test_stage_editor_create_update_reorder_delete_and_reject(qt_app) -> None:
    workspace = Workspace('empty', 'Runbook editor')
    widget = RunbookEditorWidget(workspace)
    changes: list[Workspace] = []
    widget.workspace_changed.connect(changes.append)
    widget.stage_id.setText('first')
    widget.title.setText('First')
    widget.instructions.setPlainText('Read this, then continue.')
    click(widget, 'Save stage')
    assert changes and len(widget.editor.workspace.stages) == 1
    click(widget, 'New')
    widget.stage_id.setText('second')
    widget.title.setText('Second')
    widget.instructions.setPlainText('Finish this.')
    click(widget, 'Save stage')
    assert len(widget.editor.workspace.stages) == 2
    click(widget, 'Move up')
    assert widget.editor.workspace.stages[0].id == 'second'
    widget.continue_label.setText('')
    click(widget, 'Save stage')
    assert 'Invalid stage' in widget.status.text()
    assert widget.editor.workspace.stages[0].continue_label == 'Continue'
    click(widget, 'Delete')
    assert len(widget.editor.workspace.stages) == 1
    widget.close()


def test_runbook_widget_manual_navigation_and_ack_never_automatic(qt_app) -> None:
    workspace = Workspace('manual', 'Manual', stages=(Stage('one', 'One', 'Read and finish.', None, ()),))
    runbook = Runbook(workspace, lambda stage, resume: True)
    widget = RunbookWidget(runbook)
    requests: list[Action] = []
    completions: list[str] = []
    widget.action_requested.connect(requests.append)
    widget.completion_acknowledged.connect(completions.append)
    assert widget.continue_button.text() == 'Finish'
    assert completions == [] and not runbook.finished
    widget.continue_button.click()
    assert requests == [Action(ActionType.ADVANCE_STAGE)] and not runbook.finished
    widget.complete.click()
    assert completions == ['one']
    runbook.advance()
    widget.refresh()
    assert not widget.continue_button.isEnabled() and widget.previous.isEnabled()
    widget.close()


@pytest.mark.parametrize('quick_only', [True, False])
def test_review_harness_opens_without_data_or_model_and_never_launches(qt_app, tmp_path: Path, quick_only: bool) -> None:
    window = PreviewWindow(quick_only=quick_only, state_dir=tmp_path)
    window.request(Action(ActionType.OPEN_SHORTCUT, 'missing'))
    assert window.session.snapshot.mode == RoutingMode.PREVIEW
    assert window.gate.summary.counts()['simulated'] == 1
    assert window.gate.summary.counts()['launch_requested'] == 0
    if not quick_only:
        window.inspect_viewer(Action(ActionType.BOOKMARK))
        window.inspect_viewer(Action(ActionType.NEXT))
        window.save()
        assert window.viewer is not None
        before = window.viewer.state_json()
        window.inspect_viewer(Action(ActionType.NEXT))
        window.restore()
        assert window.viewer.state_json() == before and window.runbook.paused
        assert window.session.state == 'PAUSED'
    window.close()


def test_supplied_six_stage_workspace_loads_and_exports_semantics_only() -> None:
    root = Path(__file__).resolve().parent.parent
    workspace = WorkspaceStore(Workspace('empty', 'Empty')).import_file(root / 'assets' / 'harbor_workspace.json')
    assert workspace.deck is not None
    assert len(workspace.stages) == 6 and len(workspace.deck.cards) == 10
    assert all(len(stage.bindings) == 3 for stage in workspace.stages)
    assert workspace.stages[-1].continue_label == 'Finish'


def test_workspace_widget_rejects_partial_import_without_emitting_or_rebinding(qt_app, tmp_path: Path) -> None:
    from gestureforge.javier_widgets import WorkspaceWidget
    widget = WorkspaceWidget(Workspace('empty', 'Empty'))
    changes: list[Workspace] = []
    widget.workspace_changed.connect(changes.append)
    bad = tmp_path / 'bad.json'
    bad.write_text('{"schema_version": 1, "password": "secret"}')
    assert not widget.import_path(bad)
    assert changes == [] and widget.store.active.id == 'empty'
    source = Path(__file__).resolve().parent.parent / 'assets' / 'harbor_workspace.json'
    assert widget.import_path(source)
    assert changes and widget.store.active.id == 'harbor-onboarding'
    widget.close()
