"""Embeddable GF-P06 selector; no camera, routing or readiness certification."""

from __future__ import annotations

from collections.abc import Callable
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import replace
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QFileDialog, QFormLayout, QHBoxLayout, QLabel,
    QLineEdit, QListWidget, QListWidgetItem, QMessageBox, QPushButton, QVBoxLayout, QWidget,
)

from .profiles import LoadedProfile, ProfileSettings, ProfileStore
from . import starter
from .pose_repair import RepairCandidate
from .dataset import file_sha256

if TYPE_CHECKING:
    from .app import ModelLoadWorker, Window


class ProfileSelectorWidget(QWidget):
    """Optional Studio host uses Deston's existing load/prepare-delete/clear APIs.

    Without a host, candidates are local previews and Start stays disabled.
    Creation fits in one worker; attached saved loads use the shell's own worker.
    """

    profile_selected = Signal(object)  # ProfileSelection, after successful installation
    guest_selected = Signal()
    profile_renamed = Signal(object)  # ProfileRecord; cosmetic only
    profile_deleted = Signal(str)
    start_requested = Signal(object)  # ProfileSelection; Preview only, host checks lifecycle
    busy_changed = Signal(bool)  # host serializes other load/start/edit controls

    def __init__(self, store: ProfileStore, parent=None, *, host: Window | None = None):
        super().__init__(parent)
        self.store = store
        self.host = host
        self._host_load_id: str | None = None
        self._host_loader: ModelLoadWorker | None = None
        self.loaded: LoadedProfile | None = None
        self._repair_candidate: RepairCandidate | None = None
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix='profile-loader')
        self._future: Future[LoadedProfile] | None = None
        self._discard = False
        self._closed = False
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel('Choose a personal profile'))
        self.current = self._label('Guest — manual controls only. No recogniser loaded.')
        layout.addWidget(self.current)
        self.starter_notice = self._label(
            'Standard gestures are unavailable: no approved starter model is supplied. '
            'Use Guest for manual controls, or load a personal profile. '
            'Loading a profile does not verify recognition readiness.')
        layout.addWidget(self.starter_notice)
        self.starter_button = QPushButton('Try standard gestures (unavailable)')
        self.starter_button.setEnabled(False)
        self.starter_button.setToolTip(self.starter_notice.text())
        self.starter_button.clicked.connect(self.try_standard)
        layout.addWidget(self.starter_button)
        self.profiles = QListWidget()
        self.profiles.setAccessibleName('Saved personal profiles')
        layout.addWidget(self.profiles)
        self.details = self._label('Select a saved profile, or create one below.')
        layout.addWidget(self.details)
        row = QHBoxLayout()
        self.load_button = QPushButton('Load selected')
        self.delete_button = QPushButton('Delete selected')
        self.refresh_button = QPushButton('Refresh')
        for button in (self.load_button, self.delete_button, self.refresh_button):
            row.addWidget(button)
        layout.addLayout(row)
        self.form = QWidget()
        form = QFormLayout(self.form)
        form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)
        self.name = QLineEdit()
        self.name.setMaxLength(80)
        form.addRow('Profile &name', self.name)
        self.rename_button = QPushButton('Rename selected profile')
        form.addRow(self.rename_button)
        self.manifest = QLineEdit()
        self.manifest.setPlaceholderText('Choose an existing local manifest.json')
        form.addRow('&Dataset manifest', self.manifest)
        self.browse_button = QPushButton('Browse dataset…')
        form.addRow(self.browse_button)
        self.hand = QComboBox()
        self.hand.addItems(['Right', 'Left'])
        form.addRow('&Hand', self.hand)
        self.algorithm = QComboBox()
        self.algorithm.addItems(['knn', 'svm'])
        form.addRow('&Classifier', self.algorithm)
        self.consent = QCheckBox('Dataset permission confirmed')
        self.manifest.textChanged.connect(self._manifest_changed)
        form.addRow(self.consent)
        form.addRow(self._label('Confirm you have permission to use this dataset internally. '
                                'Numeric data stays on this computer.'))
        self.create_button = QPushButton('Create and load personal profile')
        form.addRow(self.create_button)
        layout.addWidget(self.form)
        row = QHBoxLayout()
        self.guest_button = QPushButton('Use Guest (manual only)')
        self.start_button = QPushButton('Request Preview start')
        row.addWidget(self.guest_button)
        row.addWidget(self.start_button)
        layout.addLayout(row)
        self.guest_notice = self._label('')
        layout.addWidget(self.guest_notice)
        self.status = self._label('Local component preview; camera and shell are not attached.'
                                  if host is None else 'Choose a profile to begin.')
        layout.addWidget(self.status)
        self.timer = QTimer(self)
        self.timer.setInterval(30)
        self.timer.timeout.connect(self._poll)
        self.profiles.currentItemChanged.connect(self._selection_changed)
        self.load_button.clicked.connect(self.load_selected)
        self.create_button.clicked.connect(self.create_profile)
        self.rename_button.clicked.connect(self.rename_selected)
        self.delete_button.clicked.connect(self.delete_selected)
        self.refresh_button.clicked.connect(self.refresh)
        self.browse_button.clicked.connect(self.browse)
        self.guest_button.clicked.connect(self.use_guest)
        self.start_button.clicked.connect(self.request_start)
        self.refresh()

    @staticmethod
    def _label(value: str) -> QLabel:
        label = QLabel(value)
        label.setTextFormat(Qt.TextFormat.PlainText)
        label.setWordWrap(True)
        return label

    @property
    def busy(self) -> bool:
        return self._future is not None or self._host_load_id is not None

    def selected_id(self) -> str | None:
        item = self.profiles.currentItem()
        return item.data(Qt.ItemDataRole.UserRole) if item else None

    def refresh(self):
        if self.busy or self._closed:
            return
        selected = self.selected_id()
        self.profiles.clear()
        try:
            for profile_id in self.store.list_ids():
                try:
                    record = self.store.read(profile_id)
                    title = f'{record.display_name} · {record.selected_hand} · {profile_id[:8]}'
                    detail = (f'{record.settings.algorithm.upper()} · '
                              f'Poses: {", ".join(record.vocabulary.labels)}. '
                              'Model availability is checked when you load.')
                    valid = True
                except (OSError, ValueError) as exc:
                    title = f'Unavailable profile · {profile_id[:8]}'
                    detail, valid = str(exc), False
                item = QListWidgetItem(title)
                item.setData(Qt.ItemDataRole.UserRole, profile_id)
                item.setData(Qt.ItemDataRole.UserRole + 1, valid)
                item.setToolTip(detail)
                self.profiles.addItem(item)
                if profile_id == selected:
                    self.profiles.setCurrentItem(item)
        except OSError as exc:
            self.status.setText(f'Cannot list profiles: {exc}')
        self._selection_changed()

    def _selection_changed(self, *args):
        item = self.profiles.currentItem()
        self.details.setText(item.toolTip() if item else
                             'Select a saved profile, or create one below.')
        self._controls()

    def _controls(self):
        idle = not self.busy and not self._closed
        item = self.profiles.currentItem()
        valid = bool(item and item.data(Qt.ItemDataRole.UserRole + 1))
        self.profiles.setEnabled(idle)
        self.form.setEnabled(idle)
        self.refresh_button.setEnabled(idle)
        self.load_button.setEnabled(idle and valid)
        self.rename_button.setEnabled(idle and valid)
        self.delete_button.setEnabled(idle and item is not None)
        self.delete_button.setToolTip('Deletes profile settings only; numeric data is kept.')
        self.guest_button.setEnabled(idle)
        unavailable = starter.unavailable_reason()
        self.starter_button.setEnabled(idle and self.host is not None
                                       and self.host.model_loader is None and not unavailable)
        self.starter_button.setText('Try standard gestures' if not unavailable
                                    else 'Try standard gestures (unavailable)')
        self.starter_notice.setText(unavailable or
                                    'Standard poses: open palm = NEUTRAL, fist = NEXT, '
                                    'thumb up = PREVIOUS, two fingers = BOOKMARK. '
                                    'Load in Preview, then pass the six-action check in Setup.')
        self.starter_button.setToolTip(self.starter_notice.text())
        self.guest_notice.setText('Guest uses manual controls and keeps saved profiles and data.')
        self.guest_button.setToolTip('Unload the recogniser without deleting your saved profile.')
        self.start_button.setEnabled(idle and self.loaded is not None
                                     and self.host is not None)
        self.start_button.setToolTip('Requires an installed personal model and shell connection. '
                                    'The shell checks camera state and requires NEUTRAL.')

    def _prepare(self) -> bool:
        if self.busy or self._closed:
            return False
        try:
            if self.host is not None and (self.host.model_loader is not None or
                                          not self.host.pause()):
                self.status.setText('Operation stopped: the application could not pause safely.')
                return False
        except Exception as exc:
            self.status.setText(f'Cannot prepare profile change: {exc}')
            return False
        return True

    def browse(self):
        if self.busy or self._closed:
            return
        path, _ = QFileDialog.getOpenFileName(self, 'Choose local gesture dataset', '',
                                            'Dataset manifest (*.json)')
        if path:
            self.manifest.setText(path)

    def _manifest_changed(self):
        self.consent.setChecked(False)
        self._repair_candidate = None
        self.algorithm.setEnabled(True)
        self.hand.setEnabled(True)

    def offer_repair_candidate(self, candidate: RepairCandidate):
        """Populate review fields only. Training/loading requires the Create click."""
        if self.busy or self._closed:
            raise ValueError('Finish the current profile operation before reviewing a repair')
        if file_sha256(candidate.manifest) != candidate.manifest_sha256:
            raise ValueError('Candidate data changed before review')
        self.manifest.setText(str(candidate.manifest))
        self._repair_candidate = candidate
        self.name.setText('Repaired ' + candidate.label)
        self.hand.setCurrentText(candidate.hand)
        self.algorithm.setCurrentText(candidate.settings.algorithm)
        self.algorithm.setEnabled(False)
        self.hand.setEnabled(False)
        self.status.setText(f'Review separate TRAIN candidate: {candidate.valid_per_label}. '
                            f'Settings retained: {candidate.settings}. '
                            f'Rollback profile: {candidate.rollback_profile_id}. '
                            'Confirm permission and click Create to train/load explicitly.')

    def _submit(self, operation: Callable[[], LoadedProfile]):
        self._discard = False
        self._future = self._executor.submit(operation)
        self.status.setText('Validating data and rebuilding the model. Please wait…')
        self._controls()
        self.busy_changed.emit(True)
        self.timer.start()

    def create_profile(self):
        if not self.consent.isChecked():
            self.status.setText('Confirm internal-use permission before creating a profile.')
            return
        name, path = self.name.text().strip(), self.manifest.text().strip()
        if not name or not path:
            self.status.setText('Enter a profile name and choose a dataset manifest.')
            return
        if not self._prepare():
            return
        hand = self.hand.currentText()
        candidate = self._repair_candidate
        settings = (candidate.settings if candidate else
                    ProfileSettings('svm' if self.algorithm.currentText() == 'svm' else 'knn'))
        names = dict(candidate.gesture_names) if candidate else None

        def create():
            if candidate and file_sha256(candidate.manifest) != candidate.manifest_sha256:
                raise ValueError('Candidate changed after review; review it again')
            return self.store.create(name, path, hand, consent=True, settings=settings, gesture_names=names)

        self._submit(create)

    def load_selected(self):
        profile_id = self.selected_id()
        if profile_id and self._prepare():
            if self.host is None:
                self._submit(lambda: self.store.load(profile_id))
            else:
                try:
                    if not self.host.load_studio_profile(self.store, profile_id):
                        self.status.setText('Profile load was refused. See the Studio status.')
                        return
                    self._host_load_id = profile_id
                    self._host_loader = self.host.model_loader
                    self.status.setText('Studio is loading the saved profile. Please wait…')
                    self._controls()
                    self.busy_changed.emit(True)
                    self.timer.start()
                except Exception as exc:
                    self.status.setText(f'Cannot request profile load: {exc}')

    def _poll(self):
        if self._closed:
            return
        if self._host_load_id is not None:
            self._poll_host()
            return
        future = self._future
        if self._closed or future is None or not future.done():
            return
        self.timer.stop()
        self._future = None
        try:
            candidate = future.result()
            if self._discard:
                self.status.setText('Selection cancelled when this screen was hidden. '
                                    'Any completed profile save is retained; load it explicitly.')
            else:
                if self.host is not None:
                    self.host.use_studio_profile(candidate)
                self.loaded = candidate
                self._current_label()
                self.status.setText('Profile loaded and paused. Personal rehearsal is not verified.'
                                    if self.host is not None else
                                    'Profile loaded locally. Attach the shell before starting Preview.')
                self.profile_selected.emit(candidate.selection)
        except Exception as exc:
            self.status.setText(f'Cannot load profile: {exc}. Previous selection retained.')
        self.refresh()
        self.busy_changed.emit(False)

    def _poll_host(self):
        host, profile_id = self.host, self._host_load_id
        if host is None or profile_id is None or host.model_loader is not None:
            return
        self._host_load_id = None
        loader = self._host_loader
        self._host_loader = None
        self.timer.stop()
        # Host polling owns completion/installation. This only reflects its result.
        if (loader is not None and not loader.error and isinstance(loader.result, LoadedProfile)
                and host.selected_profile_id == profile_id and host.model is loader.result.model):
            try:
                self.loaded = loader.result
                self._current_label()
                self.status.setText(host.notice.text())
                self.profile_selected.emit(self.loaded.selection)
            except (OSError, ValueError) as exc:
                self.status.setText(f'Cannot display loaded profile: {exc}')
        else:
            self.status.setText(host.notice.text())
        self.refresh()
        self.busy_changed.emit(False)

    def _current_label(self):
        self.current.setText(
            f'Loaded: {self.loaded.record.display_name} · {self.loaded.record.selected_hand} hand'
            if self.loaded else 'Guest — manual controls only. No recogniser loaded.')

    def rename_selected(self):
        profile_id = self.selected_id()
        if not profile_id or not self._prepare():
            return
        try:
            record = self.store.rename(profile_id, self.name.text().strip())
            if self.loaded and self.loaded.record.profile_id == profile_id:
                self.loaded = replace(self.loaded, record=record)
                self._current_label()
            # The shell has no cosmetic-rename entry point; its owner connects the
            # notification to label refresh, without rebuilding model/readiness.
            self.status.setText('Profile renamed. Model revision is unchanged.')
            self.profile_renamed.emit(record)
        except (OSError, ValueError) as exc:
            self.status.setText(f'Cannot rename profile: {exc}')
        self.refresh()

    def delete_selected(self):
        profile_id = self.selected_id()
        if self.busy or self._closed or not profile_id:
            return
        answer = QMessageBox.question(
            self, 'Delete profile settings?',
            'Permanently delete the selected profile settings? Original numeric data will be kept.',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No)
        if answer != QMessageBox.StandardButton.Yes:
            return
        try:
            if self.host is not None and not self.host.prepare_studio_profile_delete(profile_id):
                self.status.setText('Cannot delete profile: Studio could not preserve its state.')
                return
            self.store.delete(profile_id)
            if self.host is not None and not self.host.clear_studio_profile(profile_id):
                self.status.setText('Settings were deleted, but Studio could not clear the model. '
                                    'Keep control paused and restart Studio.')
                return
            if self.loaded and self.loaded.record.profile_id == profile_id:
                self.loaded = None
                self._current_label()
            self.status.setText('Profile settings deleted. Original numeric data was kept.')
            self.profile_deleted.emit(profile_id)
        except (OSError, ValueError) as exc:
            self.status.setText(f'Cannot delete profile: {exc}')
        self.refresh()

    def use_guest(self):
        if not self._prepare():
            return
        try:
            if self.host is not None and not self.host.use_studio_guest():
                self.status.setText('Cannot switch to Guest yet. Studio must finish loading or '
                                    'preserve its current trace/collection; previous selection retained.')
                return
            self.loaded = None
            self._current_label()
            self.status.setText('Guest selected. Manual controls only; starter recognition unavailable.')
            self.guest_selected.emit()
        except Exception as exc:
            self.status.setText(f'Cannot switch to Guest: {exc}')
        self._controls()

    def try_standard(self):
        if self.host is not None and self._prepare():
            self.host.load_studio_starter()
            self.status.setText(self.host.notice.text())
            self._controls()

    def request_start(self):
        if (not self._closed and not self.busy and self.loaded is not None
                and self.host is not None):
            self.status.setText('Preview start requested. The application must check the camera '
                                'and require NEUTRAL; LIVE readiness is not established.')
            self.start_requested.emit(self.loaded.selection)

    def hideEvent(self, event):
        self._discard = True
        super().hideEvent(event)

    def closeEvent(self, event):
        self._closed = True
        self._discard = True
        self.timer.stop()
        self._executor.shutdown(wait=False, cancel_futures=True)
        self._controls()
        super().closeEvent(event)
