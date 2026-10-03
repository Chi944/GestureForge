"""Host-attached personal rehearsal controls; no capture or dispatcher creation."""
from pathlib import Path
import time

from PySide6.QtCore import QTimer, Signal, Qt
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from .contracts import Prediction
from .practice import PersonalRehearsal


class PersonalRehearsalWidget(QWidget):
    """Host creates a fresh attempt and attaches this widget after interface review.

    snapshot_requested asks the shell to supply correctly stamped shared-camera
    predictions. capture_release_requested means release practice capture and
    remain paused. result_ready is a measured result, never permission to go LIVE.
    """

    snapshot_requested = Signal(object)
    capture_release_requested = Signal()
    result_ready = Signal(object)

    def __init__(self, attempt: PersonalRehearsal, output_root: Path, parent=None,
                 *, clock=time.monotonic):
        super().__init__(parent)
        self.attempt, self.output_root, self.clock = attempt, Path(output_root), clock
        self._released = True
        self._announced = False
        self._terminal_autosave_attempted = False
        self.save_error = False
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel('Personal rehearsal — simulated actions only'))
        self.prompt = QLabel()
        self.prompt.setWordWrap(True)
        self.prompt.setTextFormat(Qt.TextFormat.PlainText)
        layout.addWidget(self.prompt)
        self.feedback = QLabel('Confirm the ten negative instructions fit your enrolled poses with the host.')
        self.feedback.setWordWrap(True)
        self.feedback.setTextFormat(Qt.TextFormat.PlainText)
        layout.addWidget(self.feedback)
        self.prepare_button = QPushButton('Prepare next trial')
        self.begin_button = QPushButton('Begin five-second window')
        self.stop_button = QPushButton('Stop rehearsal')
        self.save_button = QPushButton('Save / retry local results')
        for button in (self.prepare_button, self.begin_button, self.stop_button, self.save_button):
            layout.addWidget(button)
        self.prepare_button.clicked.connect(self.prepare)
        self.begin_button.clicked.connect(self.begin)
        self.stop_button.clicked.connect(self.stop)
        self.save_button.clicked.connect(self.save)
        self.timer = QTimer(self)
        self.timer.setInterval(40)
        self.timer.timeout.connect(self.tick)
        self.refresh()

    def prepare(self):
        if self.save_error:
            return
        try:
            snapshot = self.attempt.prepare(self.clock())
        except ValueError as exc:
            self.feedback.setText(str(exc))
            return
        self._released = False
        self.timer.start()
        self.snapshot_requested.emit(snapshot)
        self.refresh()

    def begin(self):
        try:
            self.attempt.begin_window(self.clock())
        except ValueError as exc:
            self.feedback.setText(str(exc))
            return
        self.refresh()

    def receive_prediction(self, prediction: Prediction, received_at: float):
        self.attempt.receive(prediction, received_at)
        self.refresh()

    def tick(self):
        self.attempt.tick(self.clock())
        self.refresh()

    def stop(self):
        if self.attempt.status not in {'passed', 'failed', 'cancelled', 'expired'}:
            self.attempt.cancel('Rehearsal stopped or capture/focus interrupted.')
        self.refresh()

    def capture_failed(self, reason: str):
        self.attempt.cancel(reason)
        self.refresh()

    def save(self):
        try:
            path = self.attempt.save(self.output_root)
        except (OSError, ValueError) as exc:
            self.save_error = True
            self.feedback.setText(f'Results remain in memory. Fix storage and retry: {exc}')
        else:
            self.save_error = False
            self.feedback.setText(f'Local rehearsal results saved: {path}')
        self.prepare_button.setEnabled(self.attempt.status == 'idle' and not self.save_error)

    def refresh(self):
        attempt = self.attempt
        prompt = attempt.expected
        next_text = (f'{prompt.expected} {prompt.repetition}/10: {prompt.instruction}'
                     if prompt else 'All prompted windows recorded.')
        self.prompt.setText(f'{attempt.completed}/50 completed | {attempt.status}\n{next_text}\n{attempt.reason}')
        self.prepare_button.setEnabled(attempt.status == 'idle' and not self.save_error)
        self.begin_button.setEnabled(attempt.status == 'armed' or (
            attempt.status == 'preparing' and prompt is not None and prompt.expected == 'NEUTRAL'))
        terminal = attempt.status in {'passed', 'failed', 'cancelled', 'expired'}
        self.stop_button.setEnabled(not terminal)
        should_autosave = False
        if attempt.status == 'idle' or terminal:
            self.timer.stop()
            if not self._released:
                self._released = True
                self.capture_release_requested.emit()
                should_autosave = True
        if terminal and not self._terminal_autosave_attempted:
            self._terminal_autosave_attempted = True
            should_autosave = True
        if should_autosave:
            self.save()
        if terminal and not self._announced:
            self._announced = True
            self.result_ready.emit(attempt.result())

    def hideEvent(self, event):
        if self.attempt.status in {'preparing', 'armed', 'measuring'}:
            self.stop()
        super().hideEvent(event)

    def closeEvent(self, event):
        self.stop()
        if self.save_error:
            event.ignore()
        else:
            super().closeEvent(event)
