"""Host-attached personal rehearsal controls; no capture or dispatcher creation."""
from pathlib import Path
import time

from PySide6.QtCore import QTimer, Signal, Qt
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from .contracts import Prediction
from .practice import PersonalRehearsal, PracticeResult


class PersonalRehearsalWidget(QWidget):
    """Host creates a fresh attempt and attaches this widget after interface review.

    snapshot_requested asks the shell to supply correctly stamped shared-camera
    predictions. capture_release_requested means release practice capture and
    remain paused. result_ready is a measured result, never permission to go LIVE.
    """

    snapshot_requested = Signal(object)
    capture_release_requested = Signal()
    result_ready = Signal(object)
    controls_changed = Signal()

    def __init__(self, attempt: PersonalRehearsal, output_root: Path, parent=None,
                 *, clock=time.monotonic):
        super().__init__(parent)
        self.attempt, self.output_root, self.clock = attempt, Path(output_root), clock
        self._released = True
        self._announced = False
        self._terminal_autosave_attempted = False
        self.save_error = False
        self.last_saved_result: PracticeResult | None = None
        self._last_status: str | None = None
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        self.test_selection = QComboBox()
        self.test_selection.addItem('Full rehearsal — 50 windows', None)
        for pose in (*attempt.gesture_ids, 'NEUTRAL'):
            self.test_selection.addItem(f'Test only {pose} — one diagnostic window', pose)
        self.test_selection.setAccessibleName('Practice test selection')
        self.test_selection.currentIndexChanged.connect(self.select_test)
        layout.addWidget(self.test_selection)
        self.prompt = QLabel()
        self.prompt.setWordWrap(True)
        self.prompt.setTextFormat(Qt.TextFormat.PlainText)
        layout.addWidget(self.prompt)
        self.prepare_button = QPushButton('Prepare next trial')
        self.begin_button = QPushButton('Begin five-second window')
        actions = QHBoxLayout()
        for button in (self.prepare_button, self.begin_button):
            actions.addWidget(button)
        layout.addLayout(actions)
        self.countdown = QLabel()
        self.countdown.setWordWrap(True)
        self.countdown.setTextFormat(Qt.TextFormat.PlainText)
        self.countdown.setAccessibleName('Practice countdown and next step')
        layout.addWidget(self.countdown)
        self.feedback = QLabel('Simulated actions only. Results save locally after each trial.')
        self.feedback.setWordWrap(True)
        self.feedback.setTextFormat(Qt.TextFormat.PlainText)
        layout.addWidget(self.feedback)
        self.stop_button = QPushButton('Stop rehearsal')
        self.save_button = QPushButton('Save / retry local results')
        secondary = QHBoxLayout()
        for button in (self.stop_button, self.save_button):
            secondary.addWidget(button)
        layout.addLayout(secondary)
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
        self.test_selection.setEnabled(False)
        self.timer.start()
        self.snapshot_requested.emit(snapshot)
        self.refresh()

    def select_test(self):
        try:
            self.attempt.select_diagnostic_pose(self.test_selection.currentData())
        except ValueError as exc:
            self.feedback.setText(str(exc))
            return
        self.refresh()

    def begin(self):
        try:
            started = self.attempt.request_begin(self.clock())
        except ValueError as exc:
            self.feedback.setText(f'Window not started: {exc}. Keep NEUTRAL and retry Begin.')
            return
        self.feedback.setText(
            'Measurement started. Now show the prompted pose for five seconds.' if started else
            'Waiting for fresh capture / READY. Keep NEUTRAL until the countdown starts.'
        )
        self.refresh()

    def receive_prediction(self, prediction: Prediction, received_at: float):
        was_pending = self.attempt.begin_pending
        self.attempt.receive(prediction, received_at)
        if was_pending and self.attempt.status == 'measuring':
            self.feedback.setText('Measurement started. Now show the prompted pose for five seconds.')
        self.refresh()

    def tick(self):
        self.attempt.tick(self.clock())
        self.refresh()

    def stop(self):
        if self.attempt.status not in {'passed', 'failed', 'cancelled', 'expired'}:
            self.attempt.cancel('Stop rehearsal selected.')
        self.refresh()

    def capture_failed(self, reason: str):
        self.attempt.cancel(reason)
        self.refresh()

    def save(self):
        try:
            path = self.attempt.save(self.output_root)
        except (OSError, ValueError) as exc:
            self.save_error = True
            self.last_saved_result = None
            self.feedback.setText(f'Results remain in memory. Fix storage and retry: {exc}')
        else:
            self.save_error = False
            self.last_saved_result = self.attempt.result()
            self.feedback.setText('Local rehearsal results saved. Full details are in Session summary.')
            self.feedback.setToolTip(str(path))
        self.prepare_button.setEnabled(self.attempt.status == 'idle' and not self.save_error)

    def refresh(self):
        attempt = self.attempt
        prompt = attempt.expected
        diagnostic = attempt.diagnostic_pose is not None
        repetitions = 1 if diagnostic else 10
        total = len(attempt.sequence)
        next_text = (f'{prompt.expected} {prompt.repetition}/{repetitions}: {prompt.instruction}'
                     if prompt else 'All prompted windows recorded.')
        status_text = ('diagnostic complete' if diagnostic and attempt.completed == total
                       and attempt.result().trials[-1].outcome != 'interrupted' else attempt.status)
        scope = 'Diagnostic only | ' if diagnostic else ''
        self.prompt.setText(f'{scope}{attempt.completed}/{total} completed | {status_text}\n{next_text}')
        self.prompt.setToolTip(attempt.reason)
        retry_setup = attempt.reason.startswith('Setup paused')
        remaining = attempt.remaining_window_seconds(self.clock())
        if remaining is not None:
            self.countdown.setText(
                f'{remaining:.1f} seconds remaining — keep the prompted pose.'
                if remaining > 0 else 'Five seconds complete — finishing the trial.'
            )
        elif attempt.begin_pending:
            self.countdown.setText('Waiting for fresh capture / READY — keep NEUTRAL. Timing has not started.')
        elif 'Begin wait expired' in attempt.reason:
            self.countdown.setText(attempt.reason)
        elif attempt.status == 'armed':
            self.countdown.setText('READY — keep NEUTRAL. Click Begin before showing the prompted pose.')
        elif attempt.status == 'preparing':
            self.countdown.setText('Timing has not started. Follow the preparation instructions above.')
        elif attempt.status == 'idle':
            if retry_setup:
                self.countdown.setText(attempt.reason)
            elif attempt.completed:
                self.countdown.setText('Trial finished. Click Prepare next trial to continue.')
            else:
                self.countdown.setText('Click Prepare next trial to open the camera.')
        else:
            self.countdown.setText('Rehearsal ended. Review the result above.')
        self.prepare_button.setEnabled(attempt.status == 'idle' and not self.save_error)
        self.prepare_button.setText('Retry setup' if retry_setup else 'Prepare next trial')
        self.begin_button.setText('Waiting for capture…' if attempt.begin_pending else 'Begin five-second window')
        self.begin_button.setEnabled(not attempt.begin_pending and (attempt.status == 'armed' or (
            attempt.status == 'preparing' and prompt is not None and prompt.expected == 'NEUTRAL')))
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
        if attempt.status != self._last_status:
            self._last_status = attempt.status
            self.controls_changed.emit()
        if terminal and not self._announced:
            self._announced = True
            self.result_ready.emit(attempt.result())

    def hideEvent(self, event):
        if self.attempt.status in {'preparing', 'armed', 'measuring'}:
            self.attempt.cancel('Practice tab hidden.')
            self.stop()
        super().hideEvent(event)

    def closeEvent(self, event):
        self.attempt.cancel('Practice window closed.')
        self.stop()
        if self.save_error:
            event.ignore()
        else:
            super().closeEvent(event)
