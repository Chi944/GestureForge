"""Review harness for Javier's widgets. Simulation only; no OS/camera access.

python -m gestureforge.javier_preview [--quick-only] [--smoke-test]
The assignment entry point remains unchanged. This is not Deston's integrated shell.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys
from uuid import uuid4

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QHBoxLayout, QMainWindow, QPushButton, QTabWidget, QVBoxLayout, QWidget

from .contracts import Action, ActionType, RoutingMode
from .dispatcher import Dispatcher
from .javier_widgets import (
    QuickActionsWidget, RunbookEditorWidget, RunbookWidget, SessionSummaryWidget,
    ViewerWidget, WorkspaceWidget, plain_label,
)
from .routing import RoutingSession
from .runbook import Runbook
from .shortcuts import TargetRegistry
from .viewer import Viewer
from .workspace import Stage, Workspace, WorkspaceStore, validate_workspace

ROOT = Path(__file__).resolve().parent.parent


class NeverLaunch:
    def open(self, target, resolved) -> None:
        raise RuntimeError('the review harness has no real launcher')


class PreviewWindow(QMainWindow):
    def __init__(self, *, quick_only: bool = False, state_dir: Path | None = None) -> None:
        super().__init__()
        self.setWindowTitle('GestureForge — Javier component review (simulation only)')
        self.resize(1120, 850)
        self.state_dir = state_dir or ROOT / '.local' / 'javier-preview'
        store = WorkspaceStore(Workspace('quick-only', 'Quick Actions review'))
        if not quick_only:
            store.import_file(ROOT / 'assets' / 'harbor_workspace.json')
        self.workspace = store.active
        self.session = RoutingSession('review', 'untrained', 'quick-actions',
                                      {'G1': Action(ActionType.NEXT)}, RoutingMode.PREVIEW)
        self.viewer = Viewer(self.workspace.deck, project_actions=True) if self.workspace.deck else None
        self.registry = TargetRegistry()
        self.runbook = Runbook(self.workspace, self.reset_stage, self.viewer)
        self.gate = Dispatcher(self.registry, NeverLaunch(), lambda: self.session.snapshot,
                               lambda: self.session.state != 'PAUSED', lambda snapshot: False,
                               self.session.pause, lambda snapshot: False,
                               self.viewer, self.runbook)
        body = QWidget()
        layout = QVBoxLayout(body)
        self.status = plain_label('SIMULATION ONLY. No recognition model, camera worker or real launch is attached. Manual viewer/stage inspection below; action requests are recorded as simulated.')
        layout.addWidget(self.status)
        controls = QHBoxLayout()
        for label, callback in [('Resume simulation', self.resume), ('Pause', self.pause),
                                ('Save progress', self.save), ('Restore paused', self.restore)]:
            button = QPushButton(label)
            button.clicked.connect(callback)
            controls.addWidget(button)
        layout.addLayout(controls)
        self.tabs = QTabWidget()
        self.workspace_widget = WorkspaceWidget(self.workspace)
        self.workspace_widget.workspace_changed.connect(self.replace_workspace)
        self.tabs.addTab(self.workspace_widget, 'Workspace')
        self.quick_widget = QuickActionsWidget(self.registry, self.state_dir / 'targets.json')
        self.quick_widget.action_requested.connect(self.request)
        self.quick_widget.focus_lost.connect(self.pause)
        self.quick_widget.bindings_changed.connect(self.reset_quick)
        self.tabs.addTab(self.quick_widget, 'Quick Actions')
        self.viewer_widget = ViewerWidget(self.viewer) if self.viewer else None
        if self.viewer_widget:
            # Review harness allows explicit button browsing. Real routed Studio
            # actions must use Dispatcher; this is just a content inspector.
            self.viewer_widget.action_requested.connect(self.inspect_viewer)
            self.tabs.addTab(self.viewer_widget, 'Viewer inspection')
        self.runbook_widget = RunbookWidget(self.runbook)
        self.runbook_widget.action_requested.connect(self.inspect_runbook)
        self.runbook_widget.previous_stage_requested.connect(self.previous_stage)
        self.runbook_widget.completion_acknowledged.connect(self.gate.summary.acknowledge_completion)
        self.tabs.addTab(self.runbook_widget, 'Runbook inspection')
        self.editor_widget = RunbookEditorWidget(self.workspace)
        self.editor_widget.workspace_changed.connect(self.replace_workspace)
        self.tabs.addTab(self.editor_widget, 'Stage editor')
        self.summary_widget = SessionSummaryWidget(self.gate.summary)
        self.tabs.addTab(self.summary_widget, 'Session review')
        self.tabs.currentChanged.connect(self.context_changed)
        layout.addWidget(self.tabs)
        self.setCentralWidget(body)

    def resume(self) -> None:
        self.session.resume()
        self.status.setText('Simulation resumed. The integrated shell must require NEUTRAL before gesture holds. This harness has no recogniser.')

    def pause(self) -> None:
        self.session.pause()
        self.runbook.paused = True
        self.status.setText('Paused. Returning requires explicit Resume. Simulation only.')

    def context_changed(self, index: int) -> None:
        widget = self.tabs.widget(index)
        if widget is self.runbook_widget:
            self.runbook.activate(resume=False)
        else:
            self.reset_quick()
        self.refresh()

    def reset_quick(self, bindings=None) -> None:
        mapping = {gesture: Action(ActionType.OPEN_SHORTCUT, slot) for gesture, slot in
                   zip(self.quick_widget.gesture_ids, self.registry.quick_slots, strict=True) if slot}
        if not mapping:
            # Coordinator requires a nonempty map. Keep it paused and label the
            # fallback as inspection-only, never pretend unbound poses are enabled.
            mapping = {'G1': Action(ActionType.NEXT)}
        self.session.configure('review', 'untrained', 'quick-actions', mapping, RoutingMode.PREVIEW)
        self.runbook.paused = True
        self.status.setText('Configuration changed; simulation paused. No targets opened.')

    def reset_stage(self, stage: Stage | None, resume: bool) -> bool:
        bindings = {b.gesture_id: b.action for b in stage.bindings} if stage else {}
        self.session.configure('review', 'untrained', stage.id if stage else 'empty-runbook',
                               bindings or {'G1': Action(ActionType.ADVANCE_STAGE)}, RoutingMode.PREVIEW)
        if resume:
            self.session.resume()
        return True

    def request(self, action: Action) -> None:
        outcome = self.gate.manual(str(uuid4()), action)
        self.status.setText(f'{outcome.status}: {outcome.reason or action.kind.value}. No real application opens in this harness.')
        self.refresh()

    def inspect_viewer(self, action: Action) -> None:
        self.request(action)
        if self.viewer:
            self.viewer.apply_action(action)
        self.refresh()

    def inspect_runbook(self, action: Action) -> None:
        self.request(action)
        if action.kind == ActionType.ADVANCE_STAGE:
            self.runbook.advance()
        elif action.kind != ActionType.OPEN_SHORTCUT and self.viewer:
            self.viewer.apply_action(action)
        self.refresh()

    def previous_stage(self) -> None:
        self.runbook.previous()
        self.refresh()

    def replace_workspace(self, workspace: Workspace) -> None:
        workspace = validate_workspace(workspace)
        viewer = (self.viewer if self.viewer and self.viewer.deck == workspace.deck
                  else Viewer(workspace.deck, project_actions=True) if workspace.deck else None)
        runbook = Runbook(workspace, self.reset_stage, viewer)
        self.pause()
        runbook.activate(resume=False)
        self.tabs.blockSignals(True)
        try:
            if self.viewer_widget and viewer is None:
                self.tabs.removeTab(self.tabs.indexOf(self.viewer_widget))
                self.viewer_widget.deleteLater()
                self.viewer_widget = None
            elif self.viewer_widget and viewer:
                self.viewer_widget.viewer = viewer
            elif viewer:
                self.viewer_widget = ViewerWidget(viewer)
                self.viewer_widget.action_requested.connect(self.inspect_viewer)
                self.tabs.insertTab(self.tabs.indexOf(self.runbook_widget), self.viewer_widget, 'Viewer inspection')
        finally:
            self.tabs.blockSignals(False)
        self.workspace = workspace
        self.viewer, self.runbook = viewer, runbook
        self.gate.viewer = self.viewer
        self.gate.runbook = self.runbook
        self.runbook_widget.runbook = self.runbook
        self.workspace_widget.set_workspace(workspace)
        # Stage editor edits already own this exact candidate; retain their
        # selected row/form while synchronising external imports.
        if self.editor_widget.editor.workspace != workspace:
            self.editor_widget.set_workspace(workspace)
        self.status.setText('Workspace applied; simulation paused. Local targets stay on this machine; imports never open them.')
        self.refresh()

    def refresh(self) -> None:
        if self.viewer_widget:
            self.viewer_widget.refresh()
        self.runbook_widget.refresh()
        self.summary_widget.refresh()

    def save(self) -> None:
        try:
            self.runbook.save(self.state_dir / 'session.json')
            WorkspaceStore(self.workspace).export_file(self.state_dir / 'workspace.json')
            self.status.setText('Progress saved. Local targets are in a separate private file; the workspace export has no targets.')
        except (ValueError, OSError) as exc:
            self.status.setText(f'Save failed: {exc}')

    def restore(self) -> None:
        try:
            self.runbook.restore(self.state_dir / 'session.json')
            self.status.setText('Progress restored, paused. No launch was replayed.')
            self.refresh()
        except (ValueError, OSError) as exc:
            self.status.setText(f'Restore failed; prior progress preserved: {exc}')


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--quick-only', action='store_true')
    parser.add_argument('--smoke-test', action='store_true')
    args = parser.parse_args()
    app = QApplication(sys.argv[:1])
    window = PreviewWindow(quick_only=args.quick_only)
    window.show()
    if args.smoke_test:
        QTimer.singleShot(150, app.quit)
    return app.exec()


if __name__ == '__main__':
    raise SystemExit(main())
