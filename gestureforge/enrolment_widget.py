"""Embeddable guided collection; the host owns capture and suspends action routing."""

from pathlib import Path
import time
from uuid import uuid4

from PySide6.QtCore import QTimer, Signal, Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLabel, QLineEdit, QComboBox,
    QSpinBox, QCheckBox, QPushButton, QProgressBar, QGridLayout,
)

from .contracts import Observation
from .enrolment import EnrolmentPlan, EnrolmentSession
from .vocabulary import GestureVocabulary


class EnrolmentWidget(QWidget):
    capture_requested = Signal(object, str)  # validated plan, request generation
    capture_release_requested = Signal(str)  # request generation
    dataset_saved = Signal(object)  # Path to completed session manifest; no automatic training

    def __init__(self, output_root: Path, parent=None, *, clock=time.monotonic):
        super().__init__(parent)
        self.output_root = Path(output_root)
        self.clock = clock
        self.session: EnrolmentSession | None = None
        self.pending_plan: EnrolmentPlan | None = None
        self.request_id = ''
        self.announced = False
        self.vocabulary = GestureVocabulary(('G1', 'G2', 'G3'))
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel('Personal gesture enrolment'))
        self.notice = QLabel('Gesture actions will pause before collection begins.')
        self.notice.setWordWrap(True)
        layout.addWidget(self.notice)
        self.form = QWidget()
        form = QFormLayout(self.form)
        form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)
        self.participant = QLineEdit()
        self.participant.setPlaceholderText('P02 — use a participant ID')
        form.addRow('&Participant ID', self.participant)
        self.hand = QComboBox()
        self.hand.addItems(['Right', 'Left'])
        form.addRow('&Hand', self.hand)
        self.split = QComboBox()
        self.split.addItems(['train', 'validation'])
        form.addRow('&Session', self.split)
        self.trials = QSpinBox()
        self.trials.setRange(2, 12)
        self.trials.setValue(12)
        form.addRow('&Trials per pose', self.trials)
        self.pose_fields: dict[str, QLineEdit] = {}
        for label, default in zip(self.vocabulary.labels,
                                  ('Closed fist', 'Thumb up', 'Index and middle fingers raised',
                                   'Open palm'), strict=True):
            field = QLineEdit(default)
            field.setMaxLength(200)
            self.pose_fields[label] = field
            form.addRow(label + ' pose', field)
        self.setup = QLineEdit()
        self.setup.setMaxLength(500)
        self.setup.setPlaceholderText('Describe lighting, background and camera position')
        form.addRow('Collection &conditions', self.setup)
        self.consent = QCheckBox('I agree to this collection and evaluation.')
        form.addRow(self.consent)
        consent_scope = QLabel('Consent covers local numeric gesture features for internal evaluation. No photos or video.')
        consent_scope.setWordWrap(True)
        form.addRow(consent_scope)
        layout.addWidget(self.form)
        self.cue = QLabel('Describe three distinct poses and NEUTRAL, then request collection.')
        self.cue.setTextFormat(Qt.TextFormat.PlainText)
        self.cue.setWordWrap(True)
        layout.addWidget(self.cue)
        self.progress = QProgressBar()
        self.progress.setRange(0, 48)
        self.progress.setValue(0)
        layout.addWidget(self.progress)
        self.feedback = QLabel('Features and trial records are saved locally. Raw video is not saved.')
        self.feedback.setTextFormat(Qt.TextFormat.PlainText)
        self.feedback.setWordWrap(True)
        layout.addWidget(self.feedback)
        buttons = QGridLayout()
        self.request_button = QPushButton('Request collection')
        self.begin_button = QPushButton('Begin trial')
        self.retry_button = QPushButton('Retry save')
        self.cancel_button = QPushButton('Stop collection')
        for index, button in enumerate((self.request_button, self.begin_button, self.retry_button, self.cancel_button)):
            buttons.addWidget(button, index // 2, index % 2)
        layout.addLayout(buttons)
        self.request_button.clicked.connect(self.request_collection)
        self.begin_button.clicked.connect(self.begin_trial)
        self.retry_button.clicked.connect(self.retry_save)
        self.cancel_button.clicked.connect(self.stop_collection)
        self.timer = QTimer(self)
        self.timer.setInterval(40)
        self.timer.timeout.connect(self.tick)
        self.refresh()

    def request_collection(self):
        if self.pending_plan is not None or (self.session is not None and
                self.session.state not in ('complete', 'cancelled')):
            return
        try:
            if not self.consent.isChecked():
                raise ValueError('Confirm consent before requesting collection.')
            plan = EnrolmentPlan(self.participant.text().strip(), self.hand.currentText(),
                                 self.vocabulary,
                                 tuple((label, field.text().strip())
                                       for label, field in self.pose_fields.items()),
                                 self.split.currentText(), self.trials.value(), self.setup.text().strip())
        except ValueError as exc:
            self.feedback.setText(str(exc))
            return
        self.pending_plan = plan
        self.session = None
        self.request_id = uuid4().hex
        self.announced = False
        self.feedback.setText('Waiting for camera setup. Gesture actions must pause before collection.')
        self.refresh()
        self.capture_requested.emit(plan, self.request_id)

    def attach_capture(self, request_id: str, capture_session: str, capture_profile: str):
        """Host acknowledgement: actions suspended; this generation supplies observations."""
        if request_id != self.request_id or self.pending_plan is None:
            return False
        try:
            session = EnrolmentSession(self.pending_plan, self.output_root, capture_session,
                                       capture_profile, consent=True)
        except (OSError, ValueError) as exc:
            self.capture_failed(request_id, str(exc))
            return False
        self.session = session
        self.pending_plan = None
        self.timer.start()
        self.refresh()
        return True

    def capture_failed(self, request_id: str, reason: str):
        if request_id != self.request_id:
            return
        if self.session is not None:
            self.session.stop(self.clock(), 'Capture stopped: ' + reason[:450])
        self.pending_plan = None
        self.feedback.setText(reason)
        self._release_capture_once()
        self.refresh()

    def _release_capture_once(self):
        if self.request_id and not self.announced:
            self.announced = True
            self.timer.stop()
            self.capture_release_requested.emit(self.request_id)

    def receive_observation(self, observation: Observation):
        if self.session is not None:
            self.session.advance(self.clock(), observation)
            self.refresh()

    def tick(self):
        if self.session is not None:
            self.session.advance(self.clock())
            self.refresh()

    def begin_trial(self):
        if self.session is not None and self.session.state == 'prepare':
            self.session.begin(self.clock())
            self.refresh()

    def retry_save(self):
        if self.session is not None and self.session.state == 'save_error':
            self.session.retry_save(self.clock())
            self.refresh()

    def stop_collection(self):
        if self.session is not None:
            was_terminal = self.session.state in ('complete', 'cancelled')
            self.session.stop(self.clock())
            if not was_terminal:
                self._release_capture_once()
        elif self.pending_plan is not None:
            self.pending_plan = None
            self._release_capture_once()
            self.request_id = ''  # stale capture acknowledgements cannot start collection
            self.feedback.setText('Collection request cancelled.')
        self.refresh()

    def refresh(self):
        session = self.session
        state = session.state if session else 'idle'
        busy = self.pending_plan is not None or state not in ('idle', 'complete', 'cancelled')
        self.form.setEnabled(not busy)
        self.form.setVisible(not busy)
        self.request_button.setEnabled(not busy)
        self.begin_button.setEnabled(state == 'prepare')
        self.retry_button.setEnabled(state == 'save_error')
        self.cancel_button.setEnabled(busy)
        self.begin_button.setToolTip('Available after the host enables collection and between trials.')
        if session is None:
            return
        self.progress.setMaximum(session.total)
        self.progress.setValue(session.completed)
        cue = (f'{session.label}: {dict(session.plan.instructions)[session.label]}\n'
               f'Trial {session.completed % session.plan.trials + 1}/{session.plan.trials}')
        if state == 'countdown':
            cue += f' · Get ready: {max(0., session.start - self.clock()):.1f}s'
        elif state == 'hold':
            cue += f' · Hold still: {max(0., session.start + 2. - self.clock()):.1f}s'
        elif state == 'release':
            cue = 'Release your pose and relax. Wait for Begin trial.'
        elif state == 'complete':
            cue = ('Session saved. Review the valid sample counts before training.\n'
                   'Take a break before a separate validation session.')
        elif state == 'cancelled':
            cue = 'Collection stopped. Previously saved trials are retained.'
        self.cue.setText(cue)
        self.feedback.setText(session.feedback)
        if state in ('complete', 'cancelled') and not self.announced:
            self._release_capture_once()
            if state == 'complete':
                self.dataset_saved.emit(session.manifest)

    def closeEvent(self, event):
        self.stop_collection()
        if self.session is not None and self.session.state == 'save_error':
            event.ignore()
            return
        self.timer.stop()
        super().closeEvent(event)

    def hideEvent(self, event):
        # Switching away cannot silently continue collection of a no-longer-visible cue.
        self.stop_collection()
        super().hideEvent(event)
