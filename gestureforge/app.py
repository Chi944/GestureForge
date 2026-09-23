"""Assignment desktop shell: one real action, with future scope clearly labelled."""

from dataclasses import asdict, replace
import json
from pathlib import Path
from threading import Event, Lock, Thread
import time
from uuid import uuid4

import cv2
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap, QShortcut, QKeySequence
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QProgressBar, QFrame,
)

from .capture import HandCamera
from .contracts import Prediction
from .controller import Controller
from .viewer import Viewer


class CaptureWorker(Thread):
    """One bounded mailbox prevents a slow interface accumulating old frames."""

    def __init__(self, model, feature_function, chosen_hand, camera_index, asset, session, profile):
        # No Qt objects live in this thread. A broken native camera driver must
        # not prevent process exit; normal shutdown still releases its handles.
        super().__init__(daemon=True, name="gestureforge-camera")
        self._interruption = Event()
        self.model = model
        self.feature_function = feature_function
        self.chosen_hand = chosen_hand
        self.camera_index = camera_index
        self.asset = asset
        self.session = session
        self.profile = profile
        self._lock = Lock()
        self._latest = None
        self.error = ""

    def requestInterruption(self):
        self._interruption.set()

    def isInterruptionRequested(self):
        return self._interruption.is_set()

    def isFinished(self):
        return not self.is_alive()

    def wait(self, milliseconds=None):
        self.join(None if milliseconds is None else milliseconds / 1000)
        return not self.is_alive()

    def take_latest(self):
        with self._lock:
            latest, self._latest = self._latest, None
        return latest

    def run(self):
        try:
            with HandCamera(self.asset, self.camera_index, self.session, self.profile) as camera:
                while not self.isInterruptionRequested():
                    frame, observation = camera.read()
                    try:
                        if self.feature_function is None:
                            raise ValueError("Feature extractor unavailable")
                        features = self.feature_function(observation, self.chosen_hand)
                        label, accepted, reason = self.model.predict(features)
                    except ValueError as exc:
                        label, accepted, reason = "UNKNOWN", False, str(exc)
                    prediction = Prediction(
                        observation.session_id, observation.profile_id, observation.frame_id,
                        observation.timestamp, label, accepted, rejection_reason=reason,
                    )
                    with self._lock:
                        self._latest = (frame, prediction)
        except Exception as exc:
            self.error = f"{type(exc).__name__}: {exc}"


class Window(QMainWindow):
    def __init__(self, model=None, feature_function=None, chosen_hand="Right", camera_index=0,
                 asset=None, profile="pilot", data_note="No enrolled dataset loaded"):
        super().__init__()
        self.setWindowTitle("GestureForge | Assignment prototype")
        self.resize(1150, 740)
        self.setMinimumSize(900, 620)
        self.model, self.feature_function = model, feature_function
        self.chosen_hand, self.camera_index, self.asset = chosen_hand, camera_index, asset
        self.profile = profile
        self.controller = Controller(str(uuid4()), profile)
        self.viewer = Viewer()
        self.worker = None
        self.last_result_at = 0.0
        self.received_first_frame = False
        self._log_path = None
        self._log_failed = False
        container = QWidget()
        self.setCentralWidget(container)
        page = QVBoxLayout(container)
        page.setContentsMargins(28, 22, 28, 22)
        header = QLabel("GestureForge")
        header.setObjectName("title")
        page.addWidget(header)
        subtitle = QLabel("Personal gestures. Deliberate actions.   /   Assignment release 0.1")
        subtitle.setObjectName("muted")
        page.addWidget(subtitle)
        self.notice = QLabel(data_note)
        self.notice.setWordWrap(True)
        self.notice.setObjectName("notice")
        page.addWidget(self.notice)
        columns = QHBoxLayout()
        page.addLayout(columns, 1)
        left = QVBoxLayout()
        columns.addLayout(left, 1)
        self.preview = QLabel("Camera off\n\nFrames stay on this computer")
        self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview.setMinimumSize(390, 270)
        self.preview.setObjectName("preview")
        left.addWidget(self.preview, 1)
        self.prediction = QLabel("Prediction: awaiting camera")
        self.prediction.setObjectName("prediction")
        left.addWidget(self.prediction)
        self.state = QLabel("Paused • keyboard controls remain available")
        self.state.setWordWrap(True)
        left.addWidget(self.state)
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        left.addWidget(self.progress)
        self.detail = QLabel("Start → neutral pose → hold NEXT → return to neutral")
        self.detail.setWordWrap(True)
        self.detail.setObjectName("muted")
        left.addWidget(self.detail)
        card_frame = QFrame()
        card_frame.setObjectName("card")
        right = QVBoxLayout(card_frame)
        right.setContentsMargins(28, 28, 28, 28)
        columns.addWidget(card_frame, 1)
        self.position = QLabel()
        self.position.setObjectName("muted")
        right.addWidget(self.position)
        self.card_title = QLabel()
        self.card_title.setWordWrap(True)
        self.card_title.setObjectName("cardTitle")
        right.addWidget(self.card_title)
        self.card_body = QLabel()
        self.card_body.setWordWrap(True)
        self.card_body.setAlignment(Qt.AlignmentFlag.AlignTop)
        right.addWidget(self.card_body, 1)
        self.feedback = QLabel("Use NEXT or the button to advance.")
        self.feedback.setWordWrap(True)
        right.addWidget(self.feedback)
        controls = QHBoxLayout()
        page.addLayout(controls)
        self.start_button = QPushButton("Start camera control")
        self.start_button.setEnabled(model is not None)
        self.start_button.clicked.connect(self.start_camera)
        controls.addWidget(self.start_button)
        self.pause_button = QPushButton("Pause / camera off")
        self.pause_button.clicked.connect(self.pause)
        controls.addWidget(self.pause_button)
        next_button = QPushButton("Next card  →")
        next_button.clicked.connect(self.next_card)
        controls.addWidget(next_button)
        reset_button = QPushButton("Restart deck")
        reset_button.clicked.connect(self.restart_deck)
        controls.addWidget(reset_button)
        boundary = QLabel(
            "NEXT: active  •  PREVIOUS / BOOKMARK: recognition preview only\n"
            "November extension: guided enrolment, profiles, all three actions and saved decks."
        )
        boundary.setObjectName("muted")
        page.addWidget(boundary)
        self.shortcuts = []
        for key, slot in [("Right", self.next_card), ("Escape", self.pause)]:
            shortcut = QShortcut(QKeySequence(key), self)
            shortcut.activated.connect(slot)
            self.shortcuts.append(shortcut)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.poll)
        self.timer.start(30)
        self.setStyleSheet("""
            QMainWindow { background: #101923; }
            QWidget { color: #e8eef4; font-family: 'Segoe UI'; font-size: 14px; }
            QLabel#title { font-size: 32px; font-weight: 700; }
            QLabel#muted { color: #a9bacb; font-size: 12px; }
            QLabel#notice { background: #223247; padding: 12px; border-radius: 7px; }
            QLabel#preview { background: #080e15; border-radius: 10px; color: #9cafc2; }
            QLabel#prediction { font-size: 19px; font-weight: 600; }
            QFrame#card { background: #f2f1e9; border-radius: 12px; }
            QFrame#card QLabel { color: #172b38; background: transparent; }
            QFrame#card QLabel#muted { color: #516777; }
            QLabel#cardTitle { font-size: 28px; font-weight: 600; }
            QPushButton { background: #264459; border: 1px solid #486478;
                          padding: 12px; border-radius: 7px; }
            QPushButton:hover { background: #355b72; }
            QPushButton:disabled { color: #738392; background: #1c2a35; }
            QProgressBar { background: #253542; border: none; height: 8px; border-radius: 4px; }
            QProgressBar::chunk { background: #62d6ad; border-radius: 4px; }
        """)
        self.render_card()

    def render_card(self):
        card = self.viewer.current_card
        self.position.setText(f"FIXED DEMO DECK  /  {self.viewer.position + 1} OF 10")
        self.card_title.setText(card.title)
        self.card_body.setText(card.body)

    def log(self, record):
        if self._log_failed:
            return
        if self._log_path is None:
            folder = Path(__file__).resolve().parent.parent / "experiments" / "local"
            try:
                folder.mkdir(parents=True, exist_ok=True)
            except OSError:
                self._log_failed = True
                self.notice.setText("Cannot create event log. Check folder write permissions.")
                return
            self._log_path = folder / f"session-{uuid4()}.jsonl"
        try:
            with self._log_path.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps(record) + "\n")
        except OSError:
            self._log_failed = True
            self.notice.setText("Event logging failed. Check disk space and folder permissions.")

    def start_camera(self):
        if self.model is None or self.worker is not None:
            return
        session = str(uuid4())
        self.controller.resume(session)
        self.last_result_at = time.monotonic()
        self.received_first_frame = False
        self.worker = CaptureWorker(self.model, self.feature_function, self.chosen_hand,
                                    self.camera_index, self.asset, session, self.profile)
        self.worker.start()
        self.start_button.setEnabled(False)
        self.state.setText("Opening camera • show your enrolled neutral pose")
        self.log({"type": "start", "session": session, "timestamp": time.monotonic()})

    def pause(self):
        self.controller.pause()
        if self.worker is not None:
            self.worker.requestInterruption()
        self.progress.setValue(0)
        self.state.setText("Paused • camera stopping" if self.worker else "Paused")
        self.log({"type": "pause", "timestamp": time.monotonic()})

    def next_card(self):
        moved = self.viewer.next_keyboard()
        self.feedback.setText("Advanced by keyboard/button." if moved else "Last card; no wrap.")
        self.log({"type": "command", "source": "keyboard_or_mouse", "command": "NEXT",
                  "position": self.viewer.position, "timestamp": time.monotonic()})
        self.render_card()

    def restart_deck(self):
        self.pause()
        self.viewer = Viewer()
        self.feedback.setText("Deck restarted. Resume and show neutral before another gesture.")
        self.render_card()

    def poll(self):
        if self.worker is None:
            return
        packet = self.worker.take_latest()
        if packet is not None:
            frame, prediction = packet
            self.last_result_at = time.monotonic()
            self.received_first_frame = True
            rgb = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)
            height, width, channels = rgb.shape
            image = QImage(rgb.data, width, height, width * channels,
                           QImage.Format.Format_RGB888).copy()
            self.preview.setPixmap(QPixmap.fromImage(image).scaled(
                self.preview.size(), Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            ))
            display = prediction.label if prediction.accepted else "Unrecognised"
            if prediction.label in {"PREVIOUS", "BOOKMARK"} and prediction.accepted:
                display += " (preview only)"
            self.prediction.setText(f"Prediction: {display}")
            event = self.controller.process(prediction, time.monotonic())
            self.state.setText(self.controller.state.replace("_", " "))
            self.progress.setValue(round(self.controller.progress * 100))
            self.detail.setText(prediction.rejection_reason or self.controller.last_error or
                                "Return to neutral between commands. Esc pauses immediately.")
            if event:
                moved = self.viewer.apply(event)
                event = replace(event, resulting_position=self.viewer.position)
                self.log({"type": "command", "source": "gesture", **asdict(event)})
                self.feedback.setText("NEXT gesture accepted." if moved else "Last card; no wrap.")
                self.render_card()
        elif (self.controller.state != "PAUSED" and time.monotonic() - self.last_result_at
              > (2 if self.received_first_frame else 20)):
            self.pause()
            self.state.setText("Camera stalled. Wait for shutdown, then restart.")
        if self.worker.isFinished():
            error = self.worker.error
            self.worker.wait()
            self.worker = None
            self.controller.fault(error or "Camera stopped")
            self.state.setText(error or "Paused • camera released")
            self.start_button.setEnabled(self.model is not None)

    def closeEvent(self, event):
        self.pause()
        if self.worker is not None and not self.worker.wait(3000):
            self.log({"type": "camera_shutdown_timeout", "timestamp": time.monotonic(),
                      "note": "Native driver stalled; daemon worker will end with process exit."})
        self.timer.stop()
        event.accept()
