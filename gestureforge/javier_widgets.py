"""Embeddable lane widgets. Signals request work; widgets never launch the OS."""
from __future__ import annotations

from pathlib import Path
from typing import Any
from uuid import uuid4

from PySide6.QtCore import QEvent, QObject, Qt, Signal
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QFileDialog, QFormLayout, QHBoxLayout,
    QLabel, QLineEdit, QListWidget, QPushButton, QTextEdit, QVBoxLayout, QWidget,
)

from .contracts import Action, ActionType, validate_gesture_id
from .runbook import Runbook, RunbookEditor
from .session_summary import SessionSummary
from .shortcuts import Target, TargetKind, TargetRegistry
from .viewer import Viewer
from .workspace import Binding, Stage, Workspace


def plain_label(value: str = '') -> QLabel:
    label = QLabel(value)
    label.setTextFormat(Qt.TextFormat.PlainText)
    label.setWordWrap(True)
    return label


def action_label(action: Action) -> str:
    return action.kind.value.replace('_', ' ').title() + (f': {action.shortcut_id}' if action.shortcut_id else '')


class ViewerWidget(QWidget):
    action_requested = Signal(object)

    def __init__(self, viewer: Viewer, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.viewer = viewer
        layout = QVBoxLayout(self)
        self.title = plain_label()
        self.body = QTextEdit()
        self.body.setReadOnly(True)
        layout.addWidget(self.title)
        layout.addWidget(self.body)
        controls = QHBoxLayout()
        self.buttons: dict[ActionType, QPushButton] = {}
        for kind in (ActionType.PREVIOUS, ActionType.NEXT, ActionType.BOOKMARK):
            button = QPushButton(kind.value.title())
            button.clicked.connect(lambda checked=False, kind=kind: self.action_requested.emit(Action(kind)))
            controls.addWidget(button)
            self.buttons[kind] = button
        layout.addLayout(controls)
        layout.addWidget(plain_label('Bookmarks — select one to review it. Removal is explicit.'))
        self.bookmarks = QListWidget()
        self.bookmarks.itemActivated.connect(self._review)
        layout.addWidget(self.bookmarks)
        remove = QPushButton('Remove selected bookmark')
        remove.clicked.connect(self._remove)
        layout.addWidget(remove)
        self.refresh()

    def _review(self, item: Any) -> None:
        self.viewer.select_card(item.data(Qt.ItemDataRole.UserRole))
        self.refresh()

    def _remove(self) -> None:
        item = self.bookmarks.currentItem()
        if item is not None:
            self.viewer.remove_bookmark(item.data(Qt.ItemDataRole.UserRole))
            self.refresh()

    def refresh(self) -> None:
        self.title.setText(f'{self.viewer.position + 1}/{len(self.viewer.deck.cards)} · {self.viewer.current_card.title}')
        self.body.setPlainText(self.viewer.current_card.body)
        self.buttons[ActionType.PREVIOUS].setEnabled(self.viewer.position > 0)
        self.buttons[ActionType.NEXT].setEnabled(self.viewer.position < len(self.viewer.deck.cards) - 1)
        self.buttons[ActionType.BOOKMARK].setEnabled(self.viewer.current_card not in self.viewer.bookmarks)
        self.bookmarks.clear()
        for card in self.viewer.bookmarks:
            self.bookmarks.addItem(f'{card.title} ({card.id})')
            self.bookmarks.item(self.bookmarks.count() - 1).setData(Qt.ItemDataRole.UserRole, card.id)


class QuickActionsWidget(QWidget):
    action_requested = Signal(object)
    bindings_changed = Signal(object)
    focus_lost = Signal()

    def __init__(self, registry: TargetRegistry, state_path: Path | None = None,
                 parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.registry, self.state_path = registry, state_path
        self.gesture_ids = ('G1', 'G2', 'G3')
        layout = QVBoxLayout(self)
        layout.addWidget(plain_label('Quick Actions · up to twelve local targets · three gesture slots'))
        self.status = plain_label('Paused — bind and test targets; resume explicitly in the shell.')
        layout.addWidget(self.status)
        self.slots: list[QComboBox] = []
        self.launch_buttons: list[QPushButton] = []
        for index in range(3):
            row = QHBoxLayout()
            combo = QComboBox()
            combo.setAccessibleName(f'Gesture slot {index + 1} target')
            button = QPushButton(f'{self.gesture_ids[index]}: Unbound')
            button.clicked.connect(lambda checked=False, index=index: self._request(index))
            combo.currentIndexChanged.connect(self._bind)
            self.slots.append(combo)
            self.launch_buttons.append(button)
            row.addWidget(combo)
            row.addWidget(button)
            layout.addLayout(row)
        self.library = QListWidget()
        self.library.currentRowChanged.connect(self._load_selected)
        layout.addWidget(self.library)
        form = QFormLayout()
        self.target_id, self.label, self.value = QLineEdit(), QLineEdit(), QLineEdit()
        self.target_id.setMaxLength(64)
        self.label.setMaxLength(80)
        self.value.setMaxLength(4096)
        self.kind = QComboBox()
        for kind in TargetKind:
            self.kind.addItem(kind.value.title(), kind)
        self.trusted = QCheckBox('I selected and trust this installed application')
        form.addRow('Opaque shortcut ID', self.target_id)
        form.addRow('Display label', self.label)
        form.addRow('Target type', self.kind)
        form.addRow('Local path / HTTPS / calculator / camera', self.value)
        form.addRow(self.trusted)
        layout.addLayout(form)
        row = QHBoxLayout()
        for label, callback in [('Browse', self._browse), ('New', self._new),
                                ('Save target', self._save_target), ('Delete target', self._delete),
                                ('Test selected target', self._test)]:
            button = QPushButton(label)
            button.clicked.connect(callback)
            row.addWidget(button)
        layout.addLayout(row)
        app = QApplication.instance()
        if app is not None:
            app.installEventFilter(self)
        if state_path is not None and state_path.exists():
            try:
                self.registry.restore(state_path)
            except (ValueError, OSError) as exc:
                self.status.setText(f'Could not restore local targets: {exc}. Rebind or select a valid file.')
        self.refresh()

    def showEvent(self, event: Any) -> None:
        app = QApplication.instance()
        if app is not None:
            app.installEventFilter(self)
        super().showEvent(event)

    def closeEvent(self, event: Any) -> None:
        app = QApplication.instance()
        if app is not None:
            app.removeEventFilter(self)
        super().closeEvent(event)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if event.type() == QEvent.Type.ApplicationDeactivate or (
            event.type() == QEvent.Type.WindowDeactivate and watched is self.window()
        ):
            self.focus_lost.emit()
        return super().eventFilter(watched, event)

    def set_gesture_ids(self, ids: tuple[str, str, str]) -> None:
        if len(ids) != 3 or len(set(ids)) != 3:
            raise ValueError('three unique gesture IDs required')
        for value in ids:
            validate_gesture_id(value)
        self.gesture_ids = ids
        self.refresh()

    def refresh(self) -> None:
        selected = self.target_id.text()
        self.library.clear()
        for target in self.registry.targets:
            try:
                self.registry.resolve(target.id)
                state = 'Configured; test locally'
            except (ValueError, OSError):
                state = 'Unavailable — repair binding'
            self.library.addItem(f'{target.label} · {target.id} · {state}')
            self.library.item(self.library.count() - 1).setData(Qt.ItemDataRole.UserRole, target.id)
        for index, combo in enumerate(self.slots):
            combo.blockSignals(True)
            combo.clear()
            combo.addItem('Unbound — choose a local target', None)
            for target in self.registry.targets:
                combo.addItem(f'{target.label} ({target.id})', target.id)
            combo.setCurrentIndex(max(0, combo.findData(self.registry.quick_slots[index])))
            combo.blockSignals(False)
            self._refresh_button(index)
        self.target_id.setText(selected)

    def _refresh_button(self, index: int) -> None:
        slot = self.registry.quick_slots[index]
        button = self.launch_buttons[index]
        enabled = False
        label = 'Unbound'
        if slot:
            try:
                target, _ = self.registry.resolve(slot)
                label, enabled = target.label, True
            except (ValueError, OSError):
                label = f'{slot} unavailable; repair local target'
        button.setText(f'{self.gesture_ids[index]}: {label}')
        button.setEnabled(enabled)
        button.setToolTip('Request one action through the shell dispatcher' if enabled else label)

    def _publish(self, candidate: TargetRegistry) -> None:
        if self.state_path:
            candidate.save(self.state_path)
        self.registry.replace_with(candidate)
        self.bindings_changed.emit(tuple(zip(self.gesture_ids, self.registry.quick_slots, strict=True)))

    def _bind(self) -> None:
        slots = tuple(combo.currentData() for combo in self.slots)
        try:
            candidate = self.registry.copy()
            candidate.bind_quick((slots[0], slots[1], slots[2]))
            self._publish(candidate)
            self.status.setText('Bindings changed — routing reset and readiness review required in the shell.')
        except (ValueError, OSError) as exc:
            self.status.setText(f'Cannot bind target: {exc}')
        self.refresh()

    def _request(self, index: int) -> None:
        slot = self.registry.quick_slots[index]
        if slot:
            self.action_requested.emit(Action(ActionType.OPEN_SHORTCUT, slot))

    def _load_selected(self, row: int) -> None:
        item = self.library.item(row)
        if item is None:
            return
        target = self.registry.get(item.data(Qt.ItemDataRole.UserRole))
        self.target_id.setText(target.id)
        self.label.setText(target.label)
        self.kind.setCurrentIndex(self.kind.findData(target.kind))
        self.value.setText(target.value)
        self.trusted.setChecked(target.trusted)

    def _new(self) -> None:
        self.library.clearSelection()
        self.target_id.setText(f'target-{uuid4().hex[:8]}')
        self.label.clear()
        self.value.clear()
        self.trusted.setChecked(False)

    def _browse(self) -> None:
        kind = self.kind.currentData()
        if kind == TargetKind.FOLDER:
            path = QFileDialog.getExistingDirectory(self, 'Select a local resource folder')
        elif kind in {TargetKind.FILE, TargetKind.APP}:
            pattern = 'Applications (*.exe)' if kind == TargetKind.APP else 'Reference files (*.pdf *.txt *.png *.jpg *.jpeg)'
            path, _ = QFileDialog.getOpenFileName(self, 'Select a local target', '', pattern)
        else:
            self.status.setText('Enter calculator/camera for Builtin, or a full HTTPS URL for Website.')
            return
        if path:
            self.value.setText(path)

    def _save_target(self) -> None:
        try:
            target = Target(self.target_id.text(), self.label.text(), TargetKind(self.kind.currentData()),
                            self.value.text(), self.trusted.isChecked())
            candidate = self.registry.copy()
            candidate.configure(target)
            self._publish(candidate)
            self.status.setText('Target configured. Test it explicitly; returning requires Resume.')
            self.refresh()
        except (ValueError, OSError) as exc:
            self.status.setText(f'Cannot save target: {exc}')

    def _delete(self) -> None:
        try:
            candidate = self.registry.copy()
            candidate.remove(self.target_id.text())
            self._publish(candidate)
        except (ValueError, OSError) as exc:
            self.status.setText(f'Cannot save removal: {exc}')
        self.refresh()

    def _test(self) -> None:
        try:
            target, resolved = self.registry.resolve(self.target_id.text())
            self.status.setText(f'Test requested for {target.label}: {resolved}. This does not confirm completion.')
            self.action_requested.emit(Action(ActionType.OPEN_SHORTCUT, target.id))
        except (ValueError, OSError) as exc:
            self.status.setText(f'Cannot test target: {exc}')


class RunbookEditorWidget(QWidget):
    workspace_changed = Signal(object)

    def __init__(self, workspace: Workspace, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.editor = RunbookEditor(workspace)
        layout = QVBoxLayout(self)
        self.stages = QListWidget()
        self.stages.currentRowChanged.connect(self._select)
        layout.addWidget(self.stages)
        form = QFormLayout()
        self.stage_id, self.title, self.continue_label = QLineEdit(), QLineEdit(), QLineEdit('Continue')
        self.instructions = QTextEdit()
        self.card = QComboBox()
        self.card.addItem('No card', None)
        if workspace.deck:
            for card in workspace.deck.cards:
                self.card.addItem(f'{card.title} ({card.id})', card.id)
        self.action_fields: list[tuple[QLineEdit, QComboBox]] = []
        form.addRow('Stage ID', self.stage_id)
        form.addRow('Stage title', self.title)
        form.addRow('Authored instructions', self.instructions)
        form.addRow('Linked card', self.card)
        form.addRow('Visible Continue / Finish label', self.continue_label)
        for index in range(3):
            gesture = QLineEdit(f'G{index + 1}')
            combo = QComboBox()
            combo.addItem('Unbound', None)
            for kind in ActionType:
                if kind != ActionType.OPEN_SHORTCUT:
                    if workspace.deck is None and kind in {ActionType.NEXT, ActionType.PREVIOUS, ActionType.BOOKMARK}:
                        continue
                    combo.addItem(action_label(Action(kind)), Action(kind))
            for slot in workspace.shortcuts:
                combo.addItem(f'Open {slot.label}', Action(ActionType.OPEN_SHORTCUT, slot.id))
            row = QHBoxLayout()
            row.addWidget(gesture)
            row.addWidget(combo)
            form.addRow(f'Single action {index + 1}', row)
            self.action_fields.append((gesture, combo))
        layout.addLayout(form)
        row = QHBoxLayout()
        for label, callback in [('New', self._new), ('Save stage', self._save), ('Delete', self._delete),
                                ('Move up', lambda: self._move(-1)), ('Move down', lambda: self._move(1))]:
            button = QPushButton(label)
            button.clicked.connect(callback)
            row.addWidget(button)
        layout.addLayout(row)
        self.status = plain_label('Editing never executes actions. Apply changes through the shell routing reset.')
        layout.addWidget(self.status)
        self._refresh()
        self._new()

    def _refresh(self) -> None:
        self.stages.clear()
        for stage in self.editor.workspace.stages:
            self.stages.addItem(f'{stage.title} ({stage.id})')

    def _new(self) -> None:
        self.stages.setCurrentRow(-1)
        self.stage_id.setText(f'stage-{uuid4().hex[:8]}')
        self.title.clear()
        self.instructions.clear()
        self.card.setCurrentIndex(0)
        self.continue_label.setText('Continue')
        for index, (gesture, combo) in enumerate(self.action_fields):
            gesture.setText(f'G{index + 1}')
            combo.setCurrentIndex(0)

    def _select(self, row: int) -> None:
        if not 0 <= row < len(self.editor.workspace.stages):
            return
        stage = self.editor.workspace.stages[row]
        self.stage_id.setText(stage.id)
        self.title.setText(stage.title)
        self.instructions.setPlainText(stage.instructions)
        self.card.setCurrentIndex(self.card.findData(stage.card_id))
        self.continue_label.setText(stage.continue_label)
        for index, (gesture, combo) in enumerate(self.action_fields):
            if index < len(stage.bindings):
                binding = stage.bindings[index]
                gesture.setText(binding.gesture_id)
                combo.setCurrentIndex(combo.findData(binding.action))
            else:
                gesture.setText(f'G{index + 1}')
                combo.setCurrentIndex(0)

    def _changed(self, row: int = -1) -> None:
        self.workspace_changed.emit(self.editor.workspace)
        self._refresh()
        self.stages.setCurrentRow(row)
        self.status.setText('Validated workspace changed. Shell must reset routing before activation.')

    def _save(self) -> None:
        try:
            stage = Stage(self.stage_id.text(), self.title.text(), self.instructions.toPlainText(),
                          self.card.currentData(), tuple(Binding(gesture.text(), combo.currentData())
                          for gesture, combo in self.action_fields if combo.currentData() is not None),
                          self.continue_label.text())
            row = self.stages.currentRow()
            if row < 0:
                self.editor.add(stage)
                row = len(self.editor.workspace.stages) - 1
            else:
                self.editor.update(row, stage)
            self._changed(row)
        except ValueError as exc:
            self.status.setText(f'Invalid stage: {exc}')

    def _delete(self) -> None:
        try:
            self.editor.delete(self.stages.currentRow())
            self._changed()
        except ValueError as exc:
            self.status.setText(str(exc))

    def _move(self, offset: int) -> None:
        try:
            row = self.stages.currentRow()
            self.editor.move(row, row + offset)
            self._changed(row + offset)
        except ValueError as exc:
            self.status.setText(str(exc))


class RunbookWidget(QWidget):
    action_requested = Signal(object)
    previous_stage_requested = Signal()
    completion_acknowledged = Signal(str)

    def __init__(self, runbook: Runbook, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.runbook = runbook
        layout = QVBoxLayout(self)
        self.title, self.instructions, self.legend = plain_label(), plain_label(), plain_label()
        for widget in (self.title, self.instructions, self.legend):
            layout.addWidget(widget)
        self.previous = QPushButton('Previous stage')
        self.previous.clicked.connect(self.previous_stage_requested.emit)
        self.continue_button = QPushButton('Continue')
        self.continue_button.clicked.connect(lambda: self.action_requested.emit(Action(ActionType.ADVANCE_STAGE)))
        self.complete = QPushButton('I completed this stage’s task')
        self.complete.clicked.connect(self._acknowledge)
        for button in (self.previous, self.continue_button, self.complete):
            layout.addWidget(button)
        self.manual_actions: list[QPushButton] = []
        for index in range(3):
            button = QPushButton()
            button.clicked.connect(lambda checked=False, index=index: self._request(index))
            layout.addWidget(button)
            self.manual_actions.append(button)
        self.refresh()

    def _request(self, index: int) -> None:
        stage = self.runbook.current_stage
        if stage and index < len(stage.bindings):
            self.action_requested.emit(stage.bindings[index].action)

    def _acknowledge(self) -> None:
        stage = self.runbook.current_stage
        if stage:
            self.completion_acknowledged.emit(stage.id)

    def refresh(self) -> None:
        stage = self.runbook.current_stage
        self.title.setText(f'{self.runbook.position + 1}: {stage.title}' if stage else 'No runbook — Quick Actions remains available')
        self.instructions.setText(stage.instructions if stage else '')
        self.legend.setText('\n'.join(f'{b.gesture_id} → {action_label(b.action)}' for b in stage.bindings) if stage else '')
        self.previous.setEnabled(bool(stage and (self.runbook.position > 0 or self.runbook.finished)))
        self.continue_button.setEnabled(stage is not None and not self.runbook.finished)
        self.continue_button.setText('Finish' if stage and self.runbook.position == len(self.runbook.workspace.stages) - 1 else stage.continue_label if stage else 'Continue')
        self.complete.setEnabled(stage is not None)
        for index, button in enumerate(self.manual_actions):
            bound = bool(stage and index < len(stage.bindings))
            button.setEnabled(bound)
            button.setVisible(bound)
            if bound and stage:
                button.setText(action_label(stage.bindings[index].action))


class SessionSummaryWidget(QWidget):
    def __init__(self, summary: SessionSummary, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.summary = summary
        layout = QVBoxLayout(self)
        self.counts = plain_label()
        layout.addWidget(self.counts)
        layout.addWidget(plain_label('Launch requested means Windows accepted an open request. Only explicit acknowledgement records task completion.'))
        refresh = QPushButton('Refresh measured results')
        refresh.clicked.connect(self.refresh)
        layout.addWidget(refresh)
        export = QPushButton('Export session results')
        export.clicked.connect(self._export)
        layout.addWidget(export)
        self.refresh()

    def refresh(self) -> None:
        self.counts.setText('\n'.join(f'{key.replace("_", " ").title()}: {value}' for key, value in self.summary.counts().items()))

    def _export(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, 'Export measured session', '', 'JSON (*.json)')
        if path:
            try:
                self.summary.export(Path(path))
            except (OSError, ValueError) as exc:
                self.counts.setText(f'Export failed: {exc}')


class WorkspaceWidget(QWidget):
    """Stage a validated import for the shell; never imports local targets."""
    workspace_changed = Signal(object)

    def __init__(self, workspace: Workspace, parent: QWidget | None = None) -> None:
        from .workspace import WorkspaceStore
        super().__init__(parent)
        self.store = WorkspaceStore(workspace)
        layout = QVBoxLayout(self)
        self.details = plain_label()
        layout.addWidget(self.details)
        layout.addWidget(plain_label('Portable workspaces carry cards, authored stages and semantic shortcut IDs. Each computer must rebind and test its own local targets. Applying content must reset routing.'))
        self.status = plain_label()
        layout.addWidget(self.status)
        row = QHBoxLayout()
        load = QPushButton('Import workspace JSON')
        load.clicked.connect(self._import)
        export = QPushButton('Export portable workspace')
        export.clicked.connect(self._export)
        row.addWidget(load)
        row.addWidget(export)
        layout.addLayout(row)
        self.refresh()

    def set_workspace(self, workspace: Workspace) -> None:
        from .workspace import validate_workspace
        self.store.active = validate_workspace(workspace)
        self.refresh()

    def import_path(self, path: Path) -> bool:
        try:
            candidate = self.store.import_file(path)
            self.workspace_changed.emit(candidate)
            self.refresh()
            self.status.setText('Validated content staged. Local targets are unbound until configured on this machine. Shell activation must reset routing and stay paused.')
            return True
        except (ValueError, OSError) as exc:
            self.status.setText(f'Import rejected; prior workspace retained: {exc}')
            return False

    def _import(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, 'Import a portable workspace', '', 'JSON (*.json)')
        if path:
            self.import_path(Path(path))

    def _export(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, 'Export portable workspace', '', 'JSON (*.json)')
        if path:
            try:
                self.store.export_file(Path(path))
                self.status.setText('Portable content exported. No local target bindings or personal profiles included.')
            except (ValueError, OSError) as exc:
                self.status.setText(f'Export failed: {exc}')

    def refresh(self) -> None:
        workspace = self.store.active
        cards = len(workspace.deck.cards) if workspace.deck else 0
        self.details.setText(f'{workspace.title}\n{cards} cards · {len(workspace.stages)} stages · {len(workspace.shortcuts)} semantic shortcuts\n' +
                             '\n'.join(f'{slot.id}: {slot.label} — bind locally' for slot in workspace.shortcuts))
