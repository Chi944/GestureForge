"""Assignment desktop shell: one real action, with future scope clearly labelled."""

from collections.abc import Mapping
from dataclasses import asdict, replace
import json
from pathlib import Path
from threading import Event, Lock, Thread
import time
from uuid import uuid4

import cv2
from PySide6.QtCore import Qt, QEvent, QTimer
from PySide6.QtGui import QImage, QPixmap, QShortcut, QKeySequence
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout,
    QProgressBar, QFrame, QComboBox, QGridLayout, QScrollArea, QFileDialog, QSpinBox, QCheckBox,
    QSizePolicy, QTabWidget,
)

from .capture import HandCamera
from .contracts import Action, ActionType, Prediction, RoutingMode, validate_identifier
from .controller import Controller
from .routing import RoutingSession
from .storage import read_json
from .viewer import Viewer, load_deck
from .javier_widgets import (
    RunbookEditorWidget,
    RunbookWidget,
    SessionSummaryWidget,
    ViewerWidget,
    WorkspaceWidget,
)
from .runbook import Runbook
from .session_summary import Outcome, SessionSummary
from .vocabulary import LEGACY_VOCABULARY
from .workspace import Workspace, parse_workspace
from .traces import EvaluationTrace

CARD_STYLES = (
    ("#f2f1e9", "#ab5e45"),
    ("#edf4ef", "#387f65"),
    ("#eef3f8", "#4473b2"),
    ("#f5efdc", "#916d29"),
    ("#f4ecef", "#ad5775"),
    ("#eceff7", "#686bb3"),
    ("#edf5f3", "#367c7e"),
    ("#f5eee6", "#a76037"),
    ("#eff2e5", "#64793b"),
    ("#f0edf6", "#7d62aa"),
)

REJECTION_MESSAGES = {
    "distance_rejection": "Pose does not match yet. Hold the enrolled pose steady, or return to neutral if it persists.",
    "margin_rejection": "Pose is ambiguous. Hold the enrolled pose steady, or return to neutral if it persists.",
    "multiple_hands": "Only show your enrolled hand.",
    "no_hand": "No hand detected. Keep your enrolled hand in view.",
    "observation has no landmarks": "No usable hand landmarks were found. Keep your hand in view.",
}

STUDIO_ACTIONS = (Action(ActionType.NEXT), Action(ActionType.PREVIOUS), Action(ActionType.BOOKMARK))


def validate_camera_index(index):
    if type(index) is not int or not 0 <= index <= 2147483647:
        raise ValueError("Camera index must be a non-negative 32-bit integer")


def load_personal_model(path, algorithm="knn", multiplier=1.5, margin=1.5, *, studio=False):
    """Shared CLI/UI loader; numeric participant data only, never saved model objects."""
    from .dataset import load_dataset
    from .models import train_model

    bundle = load_dataset(path)
    if not studio and bundle.vocabulary != LEGACY_VOCABULARY:
        raise ValueError("Custom gesture datasets require --studio.")
    if any(record.provenance != "human" for record in bundle.records):
        raise ValueError("Synthetic fixtures cannot enable live control. Collect personal gestures.")
    participants = {record.participant_id for record in bundle.records}
    if len(participants) != 1:
        raise ValueError("Live control requires exactly one participant's dataset.")
    profile = next(iter(participants))
    if studio:
        validate_identifier(profile)
    hand = bundle.metadata.get("chosen_hand", "Right")
    if hand not in ("Left", "Right"):
        raise ValueError("Dataset chosen_hand must be Left or Right")
    features, labels, records = bundle.training_data()
    model = train_model(features, labels, algorithm, multiplier, margin,
                        groups=[record.trial_id for record in records],
                        vocabulary=bundle.vocabulary if studio else None)
    return model, hand, profile, bundle.vocabulary


class ModelLoadWorker(Thread):
    """One pending load; no widgets or camera access on this thread."""

    def __init__(self, path, settings):
        super().__init__(daemon=True, name="gestureforge-model-load")
        self.path, self.settings = path, settings
        self.result = None
        self.error = ""

    def run(self):
        try:
            self.result = load_personal_model(self.path, *self.settings, studio=True)
        except Exception as exc:
            self.error = f"{type(exc).__name__}: {exc}"


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
                        model_version=getattr(self.model, "model_version", "unversioned"),
                    )
                    with self._lock:
                        self._latest = (frame, prediction)
        except Exception as exc:
            self.error = f"{type(exc).__name__}: {exc}"


class Window(QMainWindow):
    def __init__(self, model=None, feature_function=None, chosen_hand="Right", camera_index=0,
                 asset=None, profile="pilot", data_note="No enrolled dataset loaded",
                 studio=False, studio_mode=RoutingMode.PREVIEW,
                 vocabulary=LEGACY_VOCABULARY, model_settings=("knn", 1.5, 1.5)):
        if studio and studio_mode not in (RoutingMode.PREVIEW, RoutingMode.REHEARSAL):
            raise ValueError("Studio currently supports simulation modes only")
        if studio:
            validate_camera_index(camera_index)
        super().__init__()
        self.studio = studio
        self.setWindowTitle("GestureForge Studio" if studio else "GestureForge | Assignment prototype")
        self.resize(1150, 740)
        self.setMinimumSize(900, 620)
        self.model, self.feature_function = model, feature_function
        self.chosen_hand, self.camera_index, self.asset = chosen_hand, camera_index, asset
        self.profile = profile
        self.vocabulary = vocabulary
        self.routing = (
            RoutingSession(profile, self._model_version(), "demo-studio",
                           dict(zip(vocabulary.action_ids, STUDIO_ACTIONS, strict=True)), studio_mode)
            if studio
            else None
        )
        self.controller = Controller(str(uuid4()), profile)
        self.viewer = Viewer()
        self.deck_available = True
        self.workspace = Workspace("demo-studio", "Demo Studio", self.viewer.deck)
        self.runbook = None
        self.session_summary = SessionSummary()
        self.routing_manual_only = False
        self.manual_context_id = "demo-studio"
        self.manual_session_id = str(uuid4())
        self.manual_mode = studio_mode
        self.worker = None
        self.model_loader = None
        self.model_settings = model_settings
        self._closing = False
        self.last_result_at = 0.0
        self.received_first_frame = False
        self._log_path = None
        self._log_failed = False
        self._auto_archive_summary_on_close = True
        self.evaluation_trace: EvaluationTrace | None = None
        self.trace_path: Path | None = None
        self.trace_folder = Path(__file__).resolve().parent.parent / "experiments/local/controller-traces"
        self.studio_state_folder = Path(__file__).resolve().parent.parent / ".local/studio"
        self._set_session_summary_scope()
        self.studio_key_hint = "Ctrl+O: load dataset | Ctrl+Enter: start | Esc: pause"
        container = QWidget()
        container.setObjectName("page")
        if studio:
            container.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred)
        if studio:
            shell = QWidget()
            shell.setObjectName("page")
            shell_layout = QVBoxLayout(shell)
            shell_layout.setContentsMargins(0, 0, 0, 0)
            self.studio_scroll = QScrollArea()
            self.studio_scroll.setWidgetResizable(True)
            self.studio_scroll.setWidget(container)
            shell_layout.addWidget(self.studio_scroll, 1)
            self.setCentralWidget(shell)
        else:
            self.setCentralWidget(container)
        page = QVBoxLayout(container)
        page.setContentsMargins(28, 22, 28, 22)
        header = QLabel("GestureForge")
        header.setObjectName("title")
        page.addWidget(header)
        subtitle_text = (
            "Training demo workspace preview   /   project integration build"
            if studio
            else "Personal gestures. Deliberate actions.   /   Assignment release 0.1"
        )
        subtitle = QLabel(subtitle_text)
        subtitle.setObjectName("muted")
        page.addWidget(subtitle)
        self.notice = QLabel(data_note)
        self.notice.setWordWrap(True)
        self.notice.setObjectName("notice")
        page.addWidget(self.notice)
        self.studio_status = QLabel("")
        self.studio_status.setWordWrap(True)
        self.studio_status.setObjectName("notice")
        if studio:
            self.load_dataset_button = QPushButton("Load personal dataset...")
            self.load_dataset_button.setToolTip(
                "Choose an existing manifest.json. Pauses control, trains locally and resets mappings."
            )
            self.load_dataset_button.clicked.connect(self.choose_studio_dataset)
            camera_controls = QHBoxLayout()
            page.addLayout(camera_controls)
            camera_controls.addWidget(self.load_dataset_button, 1)
            camera_label = QLabel("Camera index")
            camera_controls.addWidget(camera_label)
            self.camera_picker = QSpinBox()
            self.camera_picker.setRange(0, 2147483647)
            self.camera_picker.setValue(camera_index)
            self.camera_picker.setAccessibleName("Camera device index")
            self.camera_picker.setToolTip("Usually 0 for the first webcam, 1 for the second. Apply, then Start to test.")
            camera_label.setBuddy(self.camera_picker)
            camera_controls.addWidget(self.camera_picker)
            self.apply_camera_button = QPushButton("Use camera and pause")
            self.apply_camera_button.clicked.connect(lambda: self.set_studio_camera(self.camera_picker.value()))
            camera_controls.addWidget(self.apply_camera_button)
            self.camera_status = QLabel()
            self.camera_status.setObjectName("muted")
            self.camera_status.setWordWrap(True)
            page.addWidget(self.camera_status)
            self.record_trace = QCheckBox("Record evaluation trace (labels and timing only)")
            self.record_trace.setToolTip(
                "Opt in before Start. Saves locally on pause; no images, video or landmarks. "
                "Intended gestures must be annotated separately before scoring."
            )
            page.addWidget(self.record_trace)
            self.trace_status = QLabel("Trace recording off; no evaluation samples are being saved.")
            self.trace_status.setWordWrap(True)
            self.trace_status.setObjectName("muted")
            page.addWidget(self.trace_status)
            self.load_progress = QProgressBar()
            self.load_progress.setRange(0, 0)
            self.load_progress.setAccessibleName("Loading and training personal dataset")
            self.load_progress.hide()
            page.addWidget(self.load_progress)
            page.addWidget(self.studio_status)
            settings = QGridLayout()
            page.addLayout(settings)
            self.mode_picker = QComboBox()
            self.mode_picker.setAccessibleName("Simulation mode")
            for mode in (RoutingMode.PREVIEW, RoutingMode.REHEARSAL):
                self.mode_picker.addItem(mode.value.title(), mode.value)
            mode_label = QLabel("Simulation mode")
            mode_label.setBuddy(self.mode_picker)
            settings.addWidget(mode_label, 0, 0)
            settings.addWidget(self.mode_picker, 1, 0)
            self.binding_labels = []
            self.binding_pickers = []
            for index in range(3):
                label = QLabel()
                picker = QComboBox()
                label.setBuddy(picker)
                settings.addWidget(label, 0, index + 1)
                settings.addWidget(picker, 1, index + 1)
                self.binding_labels.append(label)
                self.binding_pickers.append(picker)
            self.apply_bindings_button = QPushButton("Apply and pause")
            self.apply_bindings_button.clicked.connect(self.apply_studio_settings)
            self.apply_bindings_button.setToolTip(
                "Apply these simulation settings, stop the camera and require neutral on resume."
            )
            settings.addWidget(self.apply_bindings_button, 1, 4)
            settings_note = QLabel("Draft settings apply only when you click Apply and pause. Nothing is saved yet.")
            settings_note.setObjectName("muted")
            settings_note.setWordWrap(True)
            settings.addWidget(settings_note, 2, 0, 1, 5)
        columns = QHBoxLayout()
        page.addLayout(columns, 1)
        left = QVBoxLayout()
        columns.addLayout(left, 1)
        self.preview = QLabel("Camera off\n\nFrames stay on this computer")
        self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview.setMinimumSize(320 if studio else 390, 180 if studio else 270)
        if studio:
            self.preview.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Expanding)
        self.preview.setObjectName("preview")
        left.addWidget(self.preview, 1)
        self.prediction = QLabel("Prediction: awaiting camera")
        self.prediction.setObjectName("prediction")
        self.prediction.setWordWrap(studio)
        left.addWidget(self.prediction)
        self.state = QLabel("Paused • keyboard controls remain available")
        self.state.setWordWrap(True)
        left.addWidget(self.state)
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        self.progress.setTextVisible(False)
        left.addWidget(self.progress)
        self.detail = QLabel(
            "Start -> neutral pose -> hold a bound gesture -> return to neutral"
            if studio
            else "Start → neutral pose → hold NEXT → return to neutral"
        )
        self.detail.setWordWrap(True)
        self.detail.setObjectName("muted")
        left.addWidget(self.detail)
        self.card_frame = QFrame()
        self.card_frame.setObjectName("card")
        self.card_frame.setMinimumWidth(0)
        self.card_frame.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Expanding)
        right = QVBoxLayout(self.card_frame)
        right.setContentsMargins(28, 28, 28, 28)
        self.manual_viewer = None
        if studio:
            self.deck_tabs = QTabWidget()
            self.deck_tabs.setObjectName("deckTabs")
            self.deck_tabs.addTab(self.card_frame, "Card")
            self.manual_viewer = ViewerWidget(self.viewer)
            self.manual_viewer.setObjectName("manualViewer")
            self.manual_viewer.setMinimumWidth(0)
            self.manual_viewer.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Expanding)
            self.manual_viewer.action_requested.connect(self.manual_viewer_action)
            self.deck_tabs.addTab(self.manual_viewer, "Manual browse / bookmarks")
            self.workspace_widget = WorkspaceWidget(self.workspace)
            self.workspace_widget.setObjectName("manualViewer")
            self.workspace_widget.setMinimumWidth(0)
            self.workspace_widget.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Expanding)
            self.workspace_widget.workspace_changed.connect(self.accept_workspace_widget_change)
            self.deck_tabs.addTab(self.workspace_widget, "Workspace")
            self.runbook_editor = RunbookEditorWidget(self.workspace)
            self.runbook_editor.setObjectName("manualViewer")
            self.runbook_editor.setMinimumWidth(0)
            self.runbook_editor.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Expanding)
            self.runbook_editor.workspace_changed.connect(self.accept_runbook_editor_change)
            self.deck_tabs.addTab(self.runbook_editor, "Edit runbook")
            self.runbook_widget = RunbookWidget(self._make_runbook(self.workspace))
            self.runbook_widget.setObjectName("manualViewer")
            self.runbook_widget.setMinimumWidth(0)
            self.runbook_widget.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Expanding)
            self.runbook_widget.action_requested.connect(self.manual_runbook_action)
            self.runbook_widget.previous_stage_requested.connect(self.previous_runbook_stage)
            self.runbook_widget.completion_acknowledged.connect(self.acknowledge_runbook_completion)
            self.deck_tabs.addTab(self.runbook_widget, "Runbook")
            self.summary_widget = SessionSummaryWidget(
                self.session_summary,
                default_folder=self.studio_state_folder,
                scope_text=(
                    "Counts cover Studio manual card/runbook actions plus gesture simulation/rejection events. "
                    "Bookmark list review/removal and live OS dispatch are outside this summary. "
                    "Only explicit acknowledgement records task completion."
                ),
            )
            self.summary_widget.setObjectName("manualViewer")
            self.summary_widget.setMinimumWidth(0)
            self.summary_widget.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Expanding)
            self.deck_tabs.addTab(self.summary_widget, "Session summary")
            self.deck_tabs.currentChanged.connect(lambda _index: self.render_card())
            self.deck_tabs.setMinimumWidth(0)
            self.deck_tabs.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Expanding)
            columns.addWidget(self.deck_tabs, 1)
        else:
            columns.addWidget(self.card_frame, 1)
        card_header = QHBoxLayout()
        right.addLayout(card_header)
        self.card_badge = QLabel()
        self.card_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.card_badge.setObjectName("cardBadge")
        card_header.addWidget(self.card_badge)
        card_meta = QVBoxLayout()
        card_header.addLayout(card_meta, 1)
        self.deck_label = QLabel()
        self.deck_label.setObjectName("deckLabel")
        card_meta.addWidget(self.deck_label)
        self.position = QLabel()
        self.position.setObjectName("cardPosition")
        card_meta.addWidget(self.position)
        self.card_topic = QLabel()
        self.card_topic.setObjectName("cardTopic")
        card_meta.addWidget(self.card_topic)
        self.deck_progress = QProgressBar()
        self.deck_progress.setRange(0, len(self.viewer.deck.cards))
        self.deck_progress.setTextVisible(False)
        self.deck_progress.setObjectName("deckProgress")
        right.addWidget(self.deck_progress)
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
        self.feedback.setObjectName("feedback")
        right.addWidget(self.feedback)
        for label in (
            self.notice, self.studio_status,
            self.deck_label, self.position, self.card_topic, self.card_title,
            self.card_body, self.feedback, self.state, self.detail,
        ):
            label.setTextFormat(Qt.TextFormat.PlainText)
        if studio:
            self.camera_status.setTextFormat(Qt.TextFormat.PlainText)
        controls = QHBoxLayout()
        if studio:
            footer = QWidget()
            footer_layout = QVBoxLayout(footer)
            footer_layout.setContentsMargins(28, 10, 28, 14)
            shell_layout.addWidget(footer)
            left.removeWidget(self.state)
            footer_layout.addWidget(self.state)
            left.removeWidget(self.progress)
            footer_layout.addWidget(self.progress)
            footer_layout.addLayout(controls)
        else:
            page.addLayout(controls)
        self.start_button = QPushButton("Start camera control")
        self.start_button.setEnabled(model is not None)
        if model is None:
            self.prediction.setText("Camera control unavailable: no gesture dataset loaded")
            self.detail.setText(
                "Connecting a webcam is not enough. Relaunch with --dataset pointing to your "
                "saved manifest.json; see the User Guide's live gesture control command."
            )
            self.start_button.setToolTip("Load a personal gesture dataset when launching the app.")
            if studio:
                self.detail.setText("Choose Load personal dataset and select your collected manifest.json.")
                self.start_button.setToolTip("Load a personal dataset using the button above.")
        self.start_button.clicked.connect(self.start_camera)
        controls.addWidget(self.start_button)
        self.pause_button = QPushButton("Pause / camera off")
        self.pause_button.clicked.connect(self.pause)
        controls.addWidget(self.pause_button)
        self.next_button = QPushButton("Next card  →")
        self.next_button.clicked.connect(self.next_card)
        controls.addWidget(self.next_button)
        self.reset_button = QPushButton("Restart deck")
        self.reset_button.clicked.connect(self.restart_deck)
        controls.addWidget(self.reset_button)
        self.boundary = QLabel()
        self.boundary.setObjectName("muted")
        self.boundary.setWordWrap(True)
        self.boundary.setTextFormat(Qt.TextFormat.PlainText)
        if studio:
            footer_layout.addWidget(self.boundary)
        else:
            page.addWidget(self.boundary)
        self.shortcuts = []
        for key, slot in [("Right", self.next_card), ("Escape", self.pause)]:
            shortcut = QShortcut(QKeySequence(key), self)
            shortcut.activated.connect(slot)
            self.shortcuts.append(shortcut)
        if studio:
            for key, slot in [("Ctrl+O", self.choose_studio_dataset), ("Ctrl+Return", self.start_camera)]:
                shortcut = QShortcut(QKeySequence(key), self)
                shortcut.activated.connect(slot)
                self.shortcuts.append(shortcut)
            self.deck_tools = QGridLayout()
            self.file_tool_buttons = []
            for index, (text, slot) in enumerate((
                ("Load deck...", self.choose_studio_deck),
                ("Save progress...", self.choose_save_studio_progress),
                ("Restore progress...", self.choose_restore_studio_progress),
                ("Load workspace...", self.choose_studio_workspace),
                ("Save session...", self.choose_save_studio_session),
                ("Restore session...", self.choose_restore_studio_session),
            )):
                button = QPushButton(text)
                button.clicked.connect(slot)
                button.setAccessibleName(text.replace("...", ""))
                button.setMinimumWidth(0)
                button.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Fixed)
                self.deck_tools.addWidget(button, index // 3, index % 3)
                self.file_tool_buttons.append(button)
            self.deck_file_status = QLabel("Load a deck, or save and restore your place and bookmarks.")
            self.deck_file_status.setWordWrap(True)
            self.deck_file_status.setTextFormat(Qt.TextFormat.PlainText)
            self.deck_file_status.setObjectName("muted")
            file_tools_index = max(0, page.count() - 1)
            page.insertLayout(file_tools_index, self.deck_tools)
            page.insertWidget(file_tools_index + 1, self.deck_file_status)
            self.studio_key_hint = " | ".join(
                f"{shortcut.key().toString(QKeySequence.SequenceFormat.NativeText)}: {label}"
                for shortcut, label in zip(self.shortcuts[-2:], ("load dataset", "start"))
            ) + " | Esc: pause"
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.poll)
        self.timer.start(30)
        self.setStyleSheet("""
            QMainWindow { background: #101923; }
            QWidget#page { background: #101923; }
            QScrollArea { background: #101923; border: none; }
            QWidget { color: #e8eef4; font-family: 'Segoe UI'; font-size: 14px; }
            QLabel#title { font-size: 32px; font-weight: 700; }
            QLabel#muted { color: #a9bacb; font-size: 12px; }
            QLabel#notice { background: #223247; padding: 12px; border-radius: 7px; }
            QLabel#preview { background: #080e15; border-radius: 10px; color: #9cafc2; }
            QLabel#prediction { font-size: 19px; font-weight: 600; }
            QFrame#card { background: #f2f1e9; border-radius: 12px; }
            QFrame#card QLabel { color: #172b38; background: transparent; }
            QFrame#card QLabel#muted { color: #516777; }
            QLabel#deckLabel { color: #516777; font-size: 12px; font-weight: 700; }
            QLabel#cardPosition { color: #516777; font-size: 13px; }
            QLabel#cardTopic { color: #172b38; font-size: 16px; font-weight: 700; }
            QLabel#cardBadge { background: #172b38; color: #f7f1da; border-radius: 8px;
                               font-size: 30px; font-weight: 800; min-width: 76px;
                               min-height: 68px; }
            QLabel#cardTitle { font-size: 28px; font-weight: 600; }
            QFrame#card QLabel#feedback { background: #dbeadf; color: #15301d;
                                          padding: 12px; border-radius: 7px;
                                          font-weight: 600; }
            QPushButton { background: #264459; border: 1px solid #486478;
                          padding: 12px; border-radius: 7px; }
            QPushButton:hover { background: #355b72; }
            QPushButton:disabled { color: #738392; background: #1c2a35; }
            QComboBox { background: #223247; border: 1px solid #486478;
                        padding: 7px; border-radius: 5px; }
            QComboBox QAbstractItemView { background: #223247; color: #e8eef4;
                                         selection-background-color: #355b72; }
            QSpinBox { background: #223247; border: 1px solid #486478; padding: 7px; }
            QPushButton:focus, QComboBox:focus, QSpinBox:focus { border: 2px solid #62d6ad; }
            QTabWidget#deckTabs::pane { background: #101923; border: 1px solid #486478; border-radius: 7px; }
            QTabWidget#deckTabs QTabBar::tab { background: #223247; color: #e8eef4;
                                               border: 1px solid #486478; padding: 8px 12px; }
            QTabWidget#deckTabs QTabBar::tab:focus { border: 2px solid #62d6ad; }
            QTabWidget#deckTabs QTabBar::tab:selected { background: #355b72; color: #ffffff; }
            QWidget#manualViewer { background: #101923; }
            QWidget#manualViewer QLabel { color: #e8eef4; background: transparent; }
            QWidget#manualViewer QTextEdit, QWidget#manualViewer QListWidget, QWidget#manualViewer QLineEdit {
                background: #0c1620; color: #e8eef4; border: 1px solid #486478; border-radius: 6px;
                selection-background-color: #355b72; selection-color: #ffffff;
            }
            QWidget#manualViewer QTextEdit:focus, QWidget#manualViewer QListWidget:focus,
            QWidget#manualViewer QLineEdit:focus {
                border: 2px solid #62d6ad;
            }
            QProgressBar { background: #253542; border: none; height: 8px; border-radius: 4px; }
            QProgressBar::chunk { background: #62d6ad; border-radius: 4px; }
            QProgressBar#deckProgress { background: #d5d1bf; height: 10px; }
            QProgressBar#deckProgress::chunk { background: #d97757; }
        """)
        self.render_studio_status()
        self.render_card()

    def _model_version(self) -> str:
        return getattr(self.model, "model_version", "unversioned")

    def _can_start_studio_camera(self) -> bool:
        return self.model is not None and self.worker is None and not self.routing_manual_only

    def action_text(self, action: Action) -> str:
        if action.kind == ActionType.OPEN_SHORTCUT:
            return f"open shortcut {action.shortcut_id}"
        return {
            ActionType.NEXT: "show next card",
            ActionType.PREVIOUS: "show previous card",
            ActionType.BOOKMARK: "bookmark this card",
            ActionType.ADVANCE_STAGE: "advance stage",
        }[action.kind]

    def _active_studio_bindings(self) -> tuple[tuple[str, Action], ...]:
        if self.routing_manual_only:
            return ()
        assert self.routing is not None
        return self.routing.snapshot.bindings

    def _make_runbook(self, workspace: Workspace) -> Runbook:
        viewer = self.viewer if workspace.deck is not None else None
        return Runbook(workspace, self.reset_runbook_stage, viewer)

    def _summary_has_records(self) -> bool:
        return bool(
            self.session_summary.outcomes
            or self.session_summary.trials
            or self.session_summary.completed_stages
            or self.session_summary.retries
        )

    def _archive_session_summary(self, reason: str) -> bool:
        if not self._summary_has_records():
            return True
        try:
            self.studio_state_folder.mkdir(parents=True, exist_ok=True)
            path = self.studio_state_folder / f"studio-session-summary-{uuid4()}.json"
            self.session_summary.export(path)
        except (OSError, ValueError) as exc:
            self.set_deck_file_status(f"{reason}: session summary not archived: {exc}. Prior state retained.")
            return False
        self.set_deck_file_status(f"Previous session summary archived: {path}")
        return True

    def _set_session_summary_scope(self) -> None:
        self.session_summary.set_scope(
            workspace_id=self.workspace.id,
            workspace_title=self.workspace.title,
            revision_id=f"revision-{uuid4()}",
        )

    def _reset_session_summary(self) -> None:
        self.session_summary = SessionSummary()
        self._set_session_summary_scope()
        if hasattr(self, "summary_widget"):
            self.summary_widget.summary = self.session_summary
            self.summary_widget.refresh()

    def _record_session_outcome(
        self,
        *,
        source: str,
        status: str,
        action: Action | None,
        reason: str = "",
        event_id: str | None = None,
        identity: tuple[str, str, str] | None = None,
    ) -> bool:
        try:
            self.session_summary.ensure_capacity()
            session_id, context_id, model_version = identity or self._session_outcome_identity()
            self.session_summary.record(Outcome(
                event_id or f"manual-{uuid4()}",
                session_id,
                source,
                status,
                action,
                reason,
                context_id,
                model_version,
            ))
        except ValueError as exc:
            self.feedback.setText(f"Session summary full; export results before continuing: {exc}")
            return False
        if hasattr(self, "summary_widget"):
            self.summary_widget.refresh()
        return True

    def _reserve_session_record(self) -> bool:
        try:
            self.session_summary.ensure_capacity()
        except ValueError as exc:
            self.feedback.setText(f"Session summary full; export results before continuing: {exc}")
            return False
        return True

    def _session_outcome_identity(self) -> tuple[str, str, str]:
        if self.routing_manual_only:
            return self.manual_session_id, self.manual_context_id, self._model_version()
        assert self.routing is not None
        snapshot = self.routing.snapshot
        return snapshot.session_id, snapshot.context_id, snapshot.model_version

    def _refresh_workspace_widgets(self, *, refresh_editor: bool = False) -> None:
        if not self.studio:
            return
        if hasattr(self, "workspace_widget"):
            self.workspace_widget.set_workspace(self.workspace)
        if refresh_editor and hasattr(self, "runbook_editor"):
            self.runbook_editor.set_workspace(self.workspace)
        if hasattr(self, "runbook_widget"):
            self.runbook_widget.runbook = self.runbook or self._make_runbook(self.workspace)
            self.runbook_widget.refresh()
        if hasattr(self, "summary_widget"):
            self.summary_widget.summary = self.session_summary
            self.summary_widget.refresh()

    def accept_workspace_widget_change(self, workspace: Workspace) -> None:
        if not self.use_studio_workspace(workspace):
            self.workspace_widget.import_accepted = False
            self._refresh_workspace_widgets()
            if hasattr(self, "workspace_widget"):
                self.workspace_widget.status.setText("Shell rejected activation; prior workspace retained.")
            return
        self.workspace_widget.import_accepted = True

    def accept_runbook_editor_change(self, workspace: Workspace) -> None:
        if not self.use_studio_workspace(workspace, preserve_deck_review=True, reason="Runbook change not applied"):
            self.runbook_editor.change_accepted = False
            self._refresh_workspace_widgets()
            return
        self.runbook_editor.change_accepted = True

    def acknowledge_runbook_completion(self, stage_id: str) -> None:
        try:
            self.session_summary.acknowledge_completion(stage_id)
        except ValueError as exc:
            self.feedback.setText(f"Completion not recorded: {exc}")
            return
        if hasattr(self, "summary_widget"):
            self.summary_widget.refresh()
        self.feedback.setText(f"Completion acknowledged for stage {stage_id}.")

    def _set_deck_available(self, available: bool) -> None:
        self.deck_available = available
        for widget in (self.card_frame, self.manual_viewer, self.next_button, self.reset_button):
            if widget is not None:
                widget.setEnabled(available)

    def reset_runbook_stage(self, stage, resume: bool) -> bool:
        bindings = {binding.gesture_id: binding.action for binding in stage.bindings} if stage else {}
        mismatch = [gesture for gesture in bindings if gesture not in self.vocabulary.action_ids]
        if mismatch:
            if not self.configure_studio(context_id=stage.id if stage else self.workspace.id, bindings={}):
                return False
            self.feedback.setText(
                f"Stage gestures {', '.join(mismatch)} are not in the loaded vocabulary; use manual buttons."
            )
            return True
        if not self.configure_studio(context_id=stage.id if stage else self.workspace.id, bindings=bindings):
            return False
        if resume and not self.routing_manual_only:
            self.start_camera()
        return True

    def render_studio_status(self):
        if not self.studio:
            self.boundary.setText(
                "NEXT: active  •  PREVIOUS / BOOKMARK: recognition preview only\n"
                "November extension: guided enrolment, profiles, all three actions and saved decks."
            )
            return
        assert self.routing is not None
        snapshot = self.routing.snapshot
        context_id = self.manual_context_id if self.routing_manual_only else snapshot.context_id
        mode = self.manual_mode if self.routing_manual_only else snapshot.mode
        self.camera_status.setText(
            f"Selected camera: {self.camera_index} | Enrolled hand: {self.chosen_hand} | "
            f"Profile: {self.profile if self.model is not None else 'none'} | "
            f"{self.studio_key_hint}"
        )
        active_bindings = self._active_studio_bindings()
        bindings = "  |  ".join(
            f"{gesture}: would {self.action_text(action)}"
            for gesture, action in active_bindings
        )
        mode_text = mode.value.title()
        if bindings:
            self.boundary.setText(
                f"Studio {mode_text} | Context: {context_id} | Gesture actions simulated; manual deck active.\n"
                f"{bindings}"
            )
        else:
            self.boundary.setText(
                f"Studio {mode_text} | Context: {context_id} | Manual-only stage; no gesture actions are active."
            )
        missing = []
        if self.model is None:
            missing.append("starter/personal recogniser")
        missing.extend(["profile enrolment", "validated shortcut dispatcher"])
        self.studio_status.setText(
            "Studio preview is running without: " + ", ".join(missing) + "."
        )
        self.mode_picker.setCurrentIndex(self.mode_picker.findData(mode.value))
        for index, (label, picker) in enumerate(zip(self.binding_labels, self.binding_pickers)):
            active = index < len(active_bindings)
            label.setVisible(active)
            picker.setVisible(active)
            if not active:
                continue
            gesture, action = active_bindings[index]
            label.setText(f"{gesture} gesture")
            picker.setAccessibleName(f"Simulated action for {gesture}")
            picker.clear()
            choices = [Action(kind) for kind in (
                ActionType.NEXT, ActionType.PREVIOUS, ActionType.BOOKMARK, ActionType.ADVANCE_STAGE,
            )]
            if action not in choices:
                choices.append(action)
            for choice in choices:
                picker.addItem(self.action_text(choice).capitalize(), choice)
            picker.setCurrentIndex(choices.index(action))

    def apply_studio_settings(self):
        assert self.routing is not None
        bindings = {
            gesture: self.binding_pickers[index].currentData()
            for index, (gesture, _) in enumerate(self._active_studio_bindings())
        }
        self.configure_studio(mode=RoutingMode(self.mode_picker.currentData()), bindings=bindings)

    def configure_studio(self, *, context_id: str | None = None,
                         mode: RoutingMode | None = None,
                         bindings: Mapping[str, Action] | None = None) -> bool:
        if self.routing is None:
            return False
        if self.model_loader is not None:
            raise ValueError("Wait for the dataset load to finish before changing settings")
        if mode is not None and mode not in (RoutingMode.PREVIEW, RoutingMode.REHEARSAL):
            raise ValueError("Studio currently supports simulation modes only")
        old = self.routing.snapshot
        new_context_id = (self.manual_context_id if self.routing_manual_only else old.context_id) if context_id is None else context_id
        validate_identifier(new_context_id)
        new_mode = (self.manual_mode if self.routing_manual_only else old.mode) if mode is None else mode
        new_bindings = () if self.routing_manual_only and bindings is None else old.bindings if bindings is None else tuple(bindings.items())
        # Validate the complete draft before stopping capture or replacing active state.
        if not 0 <= len(new_bindings) <= 3:
            raise ValueError("Bindings must contain zero to three gestures")
        if any(gesture not in self.vocabulary.action_ids for gesture, _ in new_bindings):
            raise ValueError("Bindings must use gestures from the selected dataset vocabulary")
        if new_bindings:
            replace(old, context_id=new_context_id, mode=new_mode, bindings=new_bindings)
        if not self.pause():
            return False
        self.manual_context_id = new_context_id
        self.manual_session_id = str(uuid4())
        self.manual_mode = new_mode
        self.routing_manual_only = len(new_bindings) == 0
        if self.routing_manual_only:
            if self.worker is not None:
                self.worker.requestInterruption()
        else:
            self.routing.configure(
                self.profile, self._model_version(), new_context_id, dict(new_bindings), new_mode,
            )
        self.state.setText("Paused after Studio context change. Resume and show NEUTRAL.")
        self.prediction.setText("Prediction: awaiting new camera session")
        self.feedback.setText(
            "Manual-only stage active; use the buttons."
            if self.routing_manual_only
            else "Simulation settings applied. Resume and show NEUTRAL before a gesture."
        )
        self.start_button.setEnabled(self._can_start_studio_camera())
        self.log({"type": "studio_configuration", "session": self.routing.snapshot.session_id,
                  "context": new_context_id, "mode": new_mode.value,
                  "bindings": {gesture: asdict(action) for gesture, action in new_bindings},
                  "timestamp": time.monotonic()})
        self.render_studio_status()
        return True

    def choose_studio_dataset(self):
        if self.model_loader is not None or self._closing:
            return
        path, _ = QFileDialog.getOpenFileName(
            self, "Load a personal gesture dataset", "", "Gesture dataset (manifest.json *.json)",
        )
        if path:
            self.load_studio_dataset(Path(path))

    def set_deck_file_status(self, message: str) -> None:
        self.feedback.setText(message)
        if self.studio and hasattr(self, "deck_file_status"):
            self.deck_file_status.setText(message)

    def choose_studio_deck(self):
        if not self.studio or self.model_loader is not None or self._closing:
            return
        if not self.pause():
            self.set_deck_file_status("Deck not loaded: save the current evaluation trace first.")
            return
        path, _ = QFileDialog.getOpenFileName(
            self, "Load a Studio deck", "", "GestureForge deck (*.json)",
        )
        if path:
            self.load_studio_deck(Path(path))

    def choose_save_studio_progress(self):
        if not self.studio or self.model_loader is not None or self._closing:
            return
        if not self.pause():
            self.set_deck_file_status("Progress not saved: save the current evaluation trace first.")
            return
        suggested = str(self.studio_state_folder / "viewer-progress.json")
        try:
            self.studio_state_folder.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            suggested = ""
            self.set_deck_file_status(f"Default save folder unavailable: {exc}. Choose a writable JSON file.")
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Studio progress", suggested, "JSON (*.json)",
        )
        if path:
            self.save_studio_progress(Path(path))

    def choose_restore_studio_progress(self):
        if not self.studio or self.model_loader is not None or self._closing:
            return
        if not self.pause():
            self.set_deck_file_status("Progress not restored: save the current evaluation trace first.")
            return
        path, _ = QFileDialog.getOpenFileName(
            self, "Restore Studio progress", str(self.studio_state_folder), "JSON (*.json)",
        )
        if path:
            self.restore_studio_progress(Path(path))

    def choose_studio_workspace(self):
        if not self.studio or self.model_loader is not None or self._closing:
            return
        if not self.pause():
            self.set_deck_file_status("Workspace not loaded: save the current evaluation trace first.")
            return
        path, _ = QFileDialog.getOpenFileName(
            self, "Load a Studio workspace", str(self.studio_state_folder), "JSON (*.json)",
        )
        if path:
            self.load_studio_workspace(Path(path))

    def choose_save_studio_session(self):
        if not self.studio or self.model_loader is not None or self._closing:
            return
        if not self.pause():
            self.set_deck_file_status("Session not saved: save the current evaluation trace first.")
            return
        suggested = str(self.studio_state_folder / "studio-session.json")
        try:
            self.studio_state_folder.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            suggested = ""
            self.set_deck_file_status(f"Default save folder unavailable: {exc}. Choose a writable JSON file.")
        path, _ = QFileDialog.getSaveFileName(self, "Save Studio session", suggested, "JSON (*.json)")
        if path:
            self.save_studio_session(Path(path))

    def choose_restore_studio_session(self):
        if not self.studio or self.model_loader is not None or self._closing:
            return
        if not self.pause():
            self.set_deck_file_status("Session not restored: save the current evaluation trace first.")
            return
        path, _ = QFileDialog.getOpenFileName(
            self, "Restore Studio session", str(self.studio_state_folder), "JSON (*.json)",
        )
        if path:
            self.restore_studio_session(Path(path))

    def load_studio_deck(self, path: Path) -> bool:
        if not self.studio or self.model_loader is not None or self._closing:
            return False
        if not self.pause():
            self.set_deck_file_status("Deck not loaded: save the current evaluation trace first.")
            return False
        try:
            deck = load_deck(path)
        except (OSError, ValueError) as exc:
            self.set_deck_file_status(f"Deck not loaded: {exc}. Choose a valid GestureForge deck JSON.")
            return False
        if not self._archive_session_summary("Deck not loaded"):
            return False
        self.viewer = Viewer(deck, project_actions=True)
        self.workspace = Workspace("manual-deck", deck.title, deck)
        self.runbook = self._make_runbook(self.workspace)
        self._reset_session_summary()
        self._set_deck_available(True)
        self._refresh_workspace_widgets(refresh_editor=True)
        self.configure_studio(
            context_id=self.workspace.id,
            bindings=dict(zip(self.vocabulary.action_ids, STUDIO_ACTIONS, strict=True)),
        )
        self.set_deck_file_status(f"Loaded deck: {deck.title}.")
        self.render_card()
        return True

    def save_studio_progress(self, path: Path) -> bool:
        if not self.studio or self.model_loader is not None or self._closing:
            return False
        if not self.deck_available:
            self.set_deck_file_status("Progress not saved: this workspace has no deck.")
            return False
        if not self.pause():
            self.set_deck_file_status("Progress not saved: save the current evaluation trace first.")
            return False
        try:
            self.viewer.save(path)
        except (OSError, ValueError) as exc:
            self.set_deck_file_status(f"Progress not saved: {exc}. Choose a writable JSON file.")
            return False
        self.set_deck_file_status(f"Progress saved: {path}")
        return True

    def restore_studio_progress(self, path: Path) -> bool:
        if not self.studio or self.model_loader is not None or self._closing:
            return False
        if not self.deck_available:
            self.set_deck_file_status("Progress not restored: this workspace has no deck.")
            return False
        if not self.pause():
            self.set_deck_file_status("Progress not restored: save the current evaluation trace first.")
            return False
        try:
            raw = read_json(path)
            self.viewer.restore_state(raw)
        except (OSError, ValueError) as exc:
            self.set_deck_file_status(f"Progress not restored: {exc}. Use progress saved for this deck.")
            return False
        self.set_deck_file_status(f"Progress restored: {path}")
        self.render_card()
        return True

    def load_studio_workspace(self, path: Path) -> bool:
        if not self.studio or self.model_loader is not None or self._closing:
            return False
        if not self.pause():
            self.set_deck_file_status("Workspace not loaded: save the current evaluation trace first.")
            return False
        try:
            workspace = parse_workspace(read_json(path))
        except (OSError, ValueError) as exc:
            self.set_deck_file_status(f"Workspace not loaded: {exc}. Prior workspace retained.")
            return False
        return self.use_studio_workspace(workspace)

    def use_studio_workspace(
        self,
        workspace: Workspace,
        *,
        preserve_deck_review: bool = False,
        reason: str = "Workspace not loaded",
    ) -> bool:
        if not self.studio or self.model_loader is not None or self._closing:
            return False
        if not self.pause():
            self.set_deck_file_status(f"{reason}: save the current evaluation trace first.")
            return False
        if not self._archive_session_summary(reason):
            return False
        previous = (
            self.workspace, self.viewer, self.runbook, self.deck_available, self.session_summary,
            self.routing_manual_only, self.manual_context_id, self.manual_session_id, self.manual_mode,
        )
        same_deck = workspace.deck is not None and workspace.deck == self.workspace.deck
        candidate_viewer = (
            self.viewer
            if preserve_deck_review and same_deck
            else Viewer(workspace.deck, project_actions=True)
            if workspace.deck is not None
            else self.viewer
        )
        candidate_runbook = Runbook(workspace, self.reset_runbook_stage,
                                    candidate_viewer if workspace.deck is not None else None)
        previous_stage_id = self.runbook.current_stage.id if self.runbook and self.runbook.current_stage else None
        self.workspace = workspace
        self.viewer = candidate_viewer
        self.runbook = candidate_runbook
        if preserve_deck_review and previous_stage_id:
            ids = [stage.id for stage in workspace.stages]
            if previous_stage_id in ids:
                self.runbook.position = ids.index(previous_stage_id)
        self._reset_session_summary()
        self._set_deck_available(workspace.deck is not None)
        self._refresh_workspace_widgets(refresh_editor=True)
        if workspace.stages:
            try:
                self.runbook.activate()
            except ValueError as exc:
                (
                    self.workspace, self.viewer, self.runbook, self.deck_available, self.session_summary,
                    self.routing_manual_only, self.manual_context_id, self.manual_session_id, self.manual_mode,
                ) = previous
                self._set_deck_available(self.deck_available)
                self._refresh_workspace_widgets(refresh_editor=True)
                self.set_deck_file_status(f"{reason}: {exc}. Prior workspace retained.")
                return False
        else:
            if not self.configure_studio(context_id=workspace.id, bindings={}):
                (
                    self.workspace, self.viewer, self.runbook, self.deck_available, self.session_summary,
                    self.routing_manual_only, self.manual_context_id, self.manual_session_id, self.manual_mode,
                ) = previous
                self._set_deck_available(self.deck_available)
                self._refresh_workspace_widgets(refresh_editor=True)
                return False
        stage = self.runbook.current_stage if self.runbook else None
        mismatch = [
            binding.gesture_id for binding in stage.bindings
            if binding.gesture_id not in self.vocabulary.action_ids
        ] if stage else []
        if mismatch:
            self.set_deck_file_status(
                f"Workspace loaded: {workspace.title}. Stage gestures {', '.join(mismatch)} "
                "are not in the loaded vocabulary; use manual buttons."
            )
        else:
            self.set_deck_file_status(f"Workspace loaded: {workspace.title}.")
        self.render_card()
        return True

    def save_studio_session(self, path: Path) -> bool:
        if not self.studio or self.model_loader is not None or self._closing or self.runbook is None:
            return False
        if not self.pause():
            self.set_deck_file_status("Session not saved: save the current evaluation trace first.")
            return False
        try:
            self.runbook.save(path)
        except (OSError, ValueError) as exc:
            self.set_deck_file_status(f"Session not saved: {exc}. Choose a writable JSON file.")
            return False
        self.set_deck_file_status(f"Session saved: {path}")
        return True

    def restore_studio_session(self, path: Path) -> bool:
        if not self.studio or self.model_loader is not None or self._closing or self.runbook is None:
            return False
        if not self.pause():
            self.set_deck_file_status("Session not restored: save the current evaluation trace first.")
            return False
        if not self._archive_session_summary("Session not restored"):
            return False
        try:
            self.runbook.restore(path)
        except (OSError, ValueError) as exc:
            self.set_deck_file_status(f"Session not restored: {exc}. Prior session retained.")
            return False
        self._reset_session_summary()
        self._refresh_workspace_widgets()
        self.set_deck_file_status(f"Session restored: {path}")
        self.render_card()
        return True

    def load_studio_dataset(self, path):
        if not self.studio:
            raise ValueError("In-app dataset loading requires Studio")
        if self.model_loader is not None or self._closing:
            return False
        if not self.pause():
            return False
        self.start_button.setEnabled(False)
        self.load_dataset_button.setEnabled(False)
        self.apply_bindings_button.setEnabled(False)
        self.apply_camera_button.setEnabled(False)
        self.load_progress.show()
        self.notice.setText("Loading and training locally. Camera control is paused; existing data is unchanged.")
        self.model_loader = ModelLoadWorker(path, self.model_settings)
        self.model_loader.start()
        return True

    def set_studio_camera(self, index):
        if not self.studio or self._closing:
            raise ValueError("Camera selection requires an open Studio window")
        validate_camera_index(index)
        if self.model_loader is not None:
            raise ValueError("Wait for the dataset load to finish before changing camera")
        if index == self.camera_index:
            return False
        if not self.configure_studio():
            return False
        self.camera_index = index
        self.camera_picker.setValue(index)
        self.start_button.setEnabled(self._can_start_studio_camera())
        self.detail.setText(f"Camera {index} selected. Wait for camera release, then Start and show NEUTRAL.")
        self.render_studio_status()
        self.log({"type": "camera_selection", "camera_index": index,
                  "timestamp": time.monotonic()})
        return True

    def use_studio_model(self, model, hand, profile, vocabulary):
        """Install an already trained candidate atomically; capture resumes only on request."""
        if not self.studio or self.model_loader is not None or self._closing:
            raise ValueError("Studio must be open and idle before changing the model")
        if hand not in ("Left", "Right") or not callable(getattr(model, "predict", None)):
            raise ValueError("A trained model and Left/Right hand are required")
        if set(model.train_labels) != set(vocabulary.labels):
            raise ValueError("Model labels must match the selected vocabulary")
        candidate = RoutingSession(profile, model.model_version, "demo-studio",
                                   dict(zip(vocabulary.action_ids, STUDIO_ACTIONS, strict=True)))
        note = (f"Personal dataset: {profile} | {hand} hand | "
                f"{model.config.algorithm.upper()} | rejection {model.config.multiplier:g} | "
                f"margin {model.config.margin:g} | local processing")
        if not self.pause():
            raise ValueError("Save the current evaluation trace before changing the model")
        was_manual_only = self.routing_manual_only
        self.model, self.chosen_hand, self.profile, self.vocabulary = model, hand, profile, vocabulary
        self.routing = candidate
        self.routing_manual_only = False
        self.manual_context_id = candidate.snapshot.context_id
        self.manual_session_id = str(uuid4())
        self.manual_mode = candidate.snapshot.mode
        self.received_first_frame = False
        self.preview.clear()
        self.preview.setText("Camera off\n\nDataset loaded; start and show NEUTRAL")
        self.prediction.setText("Prediction: awaiting new camera session")
        self.state.setText("Paused after dataset change. Start and show NEUTRAL.")
        self.detail.setText("Mappings reset to Preview. Check the actions before starting camera simulation.")
        self.notice.setText(note)
        self.feedback.setText("Dataset loaded. Gesture actions remain simulations; start explicitly.")
        self.start_button.setToolTip("Start camera simulation using the loaded personal dataset.")
        self.start_button.setEnabled(self._can_start_studio_camera())
        if self.runbook is not None:
            if self.runbook.current_stage is not None:
                self.reset_runbook_stage(self.runbook.current_stage, False)
            elif was_manual_only:
                self.configure_studio(context_id=self.workspace.id, bindings={})
            else:
                self.configure_studio(
                    context_id=self.workspace.id,
                    bindings=dict(zip(self.vocabulary.action_ids, STUDIO_ACTIONS, strict=True)),
                )
        self.render_studio_status()
        self.log({"type": "studio_dataset", "profile": profile, "model_version": model.model_version,
                  "session": candidate.snapshot.session_id, "timestamp": time.monotonic()})

    def poll_model_load(self):
        loader = self.model_loader
        if loader is None or loader.is_alive():
            return
        loader.join()
        self.model_loader = None
        try:
            if loader.error:
                raise ValueError(loader.error)
            if loader.result is None:
                raise ValueError("Dataset training returned no model")
            self.use_studio_model(*loader.result)
        except (ValueError, AttributeError, TypeError) as exc:
            self.notice.setText(f"Dataset not loaded: {exc}. Previous selection retained; control is paused.")
        finally:
            self.load_dataset_button.setEnabled(True)
            self.apply_bindings_button.setEnabled(True)
            self.apply_camera_button.setEnabled(True)
            self.load_progress.hide()
            self.start_button.setEnabled(self._can_start_studio_camera())

    def card_topic_text(self) -> str:
        title = self.viewer.current_card.title
        if self.studio:
            return title
        return title.split(": ", 1)[1] if title.startswith("Card ") and ": " in title else title

    def rejection_message(self, reason: str) -> str:
        if reason in REJECTION_MESSAGES:
            return REJECTION_MESSAGES[reason]
        if reason.startswith("expected one hand"):
            return "Show one enrolled hand only."
        if reason.startswith("expected ") and " hand, got " in reason:
            return "Wrong hand detected. Use your enrolled hand."
        return reason

    def render_card(self):
        if self.manual_viewer is not None:
            self.manual_viewer.viewer = self.viewer
            self.manual_viewer.refresh()
        if self.runbook is not None and hasattr(self, "runbook_widget"):
            self.runbook_widget.refresh()
        if not self.deck_available:
            self.deck_progress.setRange(0, 1)
            self.deck_progress.setValue(0)
            self.card_badge.setText("-")
            self.deck_label.setText("NO DECK")
            self.position.setText("No card loaded")
            self.card_topic.setText("Topic: manual-only workspace")
            self.card_title.setText(self.workspace.title)
            stage = self.runbook.current_stage if self.runbook else None
            self.card_body.setText(stage.instructions if stage else "Use the runbook controls for this workspace.")
            self.feedback.setText("Deck controls are disabled for this workspace.")
            self.card_frame.setStyleSheet("QFrame#card { background: #eef3f8; border-radius: 12px; }")
            return
        card = self.viewer.current_card
        count = len(self.viewer.deck.cards)
        number = self.viewer.position + 1
        background, accent = CARD_STYLES[self.viewer.position % len(CARD_STYLES)]
        self.deck_progress.setRange(0, count)
        self.card_badge.setText(f"{number}")
        self.deck_label.setText(self.viewer.deck.title.upper())
        self.position.setText(f"Card {number} of {count}")
        self.card_topic.setText(f"Topic: {self.card_topic_text()}")
        self.deck_progress.setValue(number)
        self.card_title.setText(self.card_topic_text())
        self.card_body.setText(card.body)
        self.card_frame.setStyleSheet(f"QFrame#card {{ background: {background}; border-radius: 12px; }}")
        self.card_badge.setStyleSheet(
            f"background: {accent}; color: #fffaf0; border-radius: 8px; "
            "font-size: 30px; font-weight: 800; min-width: 76px; min-height: 68px;"
        )
        self.deck_progress.setStyleSheet(
            "QProgressBar#deckProgress { background: rgba(23, 43, 56, 35); "
            "height: 10px; border-radius: 4px; } "
            f"QProgressBar#deckProgress::chunk {{ background: {accent}; border-radius: 4px; }}"
        )
        self.feedback.setStyleSheet(
            f"background: {accent}; color: #fffaf0; padding: 12px; "
            "border-radius: 7px; font-weight: 700;"
        )

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
        if (
            self.model is None or self.worker is not None or self.model_loader is not None
            or self._closing or (self.studio and self.routing_manual_only)
        ):
            return
        if not self.finish_evaluation_trace():
            return
        if self.routing is not None:
            snapshot = self.routing.resume()
            session = snapshot.session_id
            profile = snapshot.profile_id
            self.record_trace.setEnabled(False)
            if self.record_trace.isChecked():
                self.evaluation_trace = EvaluationTrace(snapshot)
                self.trace_path = self.trace_folder / f"trace-{uuid4()}.json"
                self.trace_status.setText("Recording controller inputs locally; Pause to save for annotation.")
        else:
            session = str(uuid4())
            profile = self.profile
            self.controller.resume(session)
        self.last_result_at = time.monotonic()
        self.received_first_frame = False
        self.worker = CaptureWorker(self.model, self.feature_function, self.chosen_hand,
                                    self.camera_index, self.asset, session, profile)
        self.worker.start()
        self.start_button.setEnabled(False)
        self.state.setText("Opening camera • show your enrolled neutral pose")
        if self.studio:
            self.preview.setText(f"Opening camera {self.camera_index}...")
        self.log({"type": "start", "session": session, "timestamp": time.monotonic(),
                  "camera_index": self.camera_index, "chosen_hand": self.chosen_hand,
                  "mode": self.routing.snapshot.mode.value if self.routing else "ASSIGNMENT",
                  "model": self.model.to_config() if hasattr(self.model, "to_config") else None})

    def pause(self):
        if self.routing is not None:
            self.routing.pause()
        else:
            self.controller.pause()
        if self.worker is not None:
            self.worker.requestInterruption()
        saved = self.finish_evaluation_trace()
        if self.studio:
            self.record_trace.setEnabled(self.worker is None and self.evaluation_trace is None)
            self.preview.clear()
            self.preview.setText("Camera stopping..." if self.worker else "Camera off")
        self.progress.setValue(0)
        self.state.setText("Paused • camera stopping" if self.worker else "Paused")
        self.log({"type": "pause", "timestamp": time.monotonic()})
        return saved

    def finish_evaluation_trace(self):
        trace = self.evaluation_trace
        if trace is None:
            return True
        if trace.frame_count == 0:
            self.evaluation_trace = None
            self.trace_status.setText("No controller inputs received; no trace saved.")
            return True
        assert self.trace_path is not None
        try:
            trace.save(self.trace_path)
        except (OSError, ValueError) as exc:
            self.trace_status.setText(f"Trace not saved: {exc}. Fix storage, then press Pause to retry; keep this window open.")
            return False
        self.evaluation_trace = None
        self.trace_status.setText(f"Saved {trace.frame_count} inputs for annotation: {self.trace_path}")
        return True

    def next_card(self):
        if self.studio and not self.deck_available:
            self.feedback.setText("No deck is loaded for this workspace.")
            return
        if self.studio and not self._reserve_session_record():
            return
        old_topic = self.card_topic_text()
        moved = self.viewer.next_keyboard()
        self.render_card()
        self.feedback.setText(
            f"Now showing {self.card_topic_text()} (from {old_topic})."
            if moved else f"Still showing {old_topic}; the assignment deck does not wrap."
        )
        if self.studio:
            self._record_session_outcome(
                source="manual",
                status="applied" if moved else "unchanged",
                action=Action(ActionType.NEXT),
                reason="keyboard_or_mouse",
            )
        self.log({"type": "command", "source": "keyboard_or_mouse", "command": "NEXT",
                  "position": self.viewer.position, "timestamp": time.monotonic()})

    def manual_viewer_action(self, action):
        if not self.studio or action.kind not in {ActionType.NEXT, ActionType.PREVIOUS, ActionType.BOOKMARK}:
            return
        if not self.deck_available:
            self.feedback.setText("No deck is loaded for this workspace.")
            return
        if not self._reserve_session_record():
            return
        old_topic = self.card_topic_text()
        moved = self.viewer.apply_action(action)
        self.render_card()
        self.feedback.setText(
            f"Manual {action.kind.value}: now showing {self.card_topic_text()} (from {old_topic})."
            if moved and action.kind != ActionType.BOOKMARK
            else f"Manual {action.kind.value}: {self.action_text(action)}."
            if moved
            else f"Manual {action.kind.value}: no change."
        )
        self._record_session_outcome(
            source="manual",
            status="applied" if moved else "unchanged",
            action=action,
            reason="manual_viewer",
        )
        self.log({"type": "command", "source": "manual_viewer", "command": action.kind.value,
                  "position": self.viewer.position, "timestamp": time.monotonic()})

    def manual_runbook_action(self, action):
        if not self.studio or self.runbook is None:
            return
        if action.kind == ActionType.ADVANCE_STAGE:
            if not self._reserve_session_record():
                return
            identity = self._session_outcome_identity()
            try:
                changed = self.runbook.advance()
            except ValueError as exc:
                self.feedback.setText(f"Runbook not advanced: {exc}")
                self._record_session_outcome(
                    source="manual", status="failed", action=action,
                    reason=f"runbook_advance: {exc}", identity=identity,
                )
                return
            self._refresh_workspace_widgets()
            self.render_card()
            self.feedback.setText("Runbook finished." if self.runbook.finished else "Runbook advanced.")
            self._record_session_outcome(
                source="manual",
                status="applied" if changed else "unchanged",
                action=action,
                reason="runbook_continue_or_finish",
                identity=identity,
            )
            self.log({"type": "runbook_advance", "stage": self.runbook.current_stage.id
                      if self.runbook.current_stage else None, "timestamp": time.monotonic()})
            return
        if action.kind in {ActionType.NEXT, ActionType.PREVIOUS, ActionType.BOOKMARK} and self.deck_available:
            self.manual_viewer_action(action)
            return
        if not self._reserve_session_record():
            return
        self.feedback.setText(f"Manual {self.action_text(action)} is simulated; no OS action is launched.")
        self._record_session_outcome(
            source="manual", status="simulated", action=action, reason="manual_runbook_action",
        )
        self.log({"type": "manual_simulation", "action": action.kind.value, "timestamp": time.monotonic()})

    def previous_runbook_stage(self):
        if not self.studio or self.runbook is None:
            return
        if not self._reserve_session_record():
            return
        identity = self._session_outcome_identity()
        try:
            changed = self.runbook.previous()
        except ValueError as exc:
            self.feedback.setText(f"Runbook not moved: {exc}")
            self._record_session_outcome(
                source="manual", status="failed", action=None, reason=f"previous_stage: {exc}", identity=identity,
            )
            return
        if changed:
            self._refresh_workspace_widgets()
            self.render_card()
            self.feedback.setText("Previous runbook stage restored.")
        self._record_session_outcome(
            source="manual",
            status="applied" if changed else "unchanged",
            action=None,
            reason="previous_runbook_stage" if changed else "no_previous_runbook_stage",
            identity=identity,
        )

    def restart_deck(self):
        if not self.pause():
            return
        if not self.deck_available:
            self.feedback.setText("No deck is loaded for this workspace.")
            return
        if not self._archive_session_summary("Deck not restarted"):
            return
        previous = (
            self.viewer, self.runbook, self.routing_manual_only,
            self.manual_context_id, self.manual_session_id, self.manual_mode,
        )
        self.viewer = Viewer(self.viewer.deck, project_actions=self.studio)
        if self.workspace.deck is not None:
            self.runbook = self._make_runbook(self.workspace)
            self._refresh_workspace_widgets()
            try:
                if self.runbook.current_stage is not None:
                    self.runbook.activate()
            except ValueError as exc:
                (
                    self.viewer, self.runbook, self.routing_manual_only,
                    self.manual_context_id, self.manual_session_id, self.manual_mode,
                ) = previous
                self._refresh_workspace_widgets()
                self.feedback.setText(f"Deck not restarted: {exc}")
                return
        self._reset_session_summary()
        self.feedback.setText("Deck restarted. Resume and show neutral before another gesture.")
        self.render_card()

    def poll(self):
        if self._closing:
            return
        self.poll_model_load()
        if self.worker is None:
            return
        control = self.routing or self.controller
        packet = self.worker.take_latest()
        if packet is not None and self.routing is not None:
            prediction = packet[1]
            snapshot = self.routing.snapshot
            if self.worker.isInterruptionRequested() or (
                prediction.session_id, prediction.profile_id, prediction.model_version
            ) != (snapshot.session_id, snapshot.profile_id, snapshot.model_version):
                packet = None
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
            if not self.studio and prediction.label in {"PREVIOUS", "BOOKMARK"} and prediction.accepted:
                display += " (preview only)"
            self.prediction.setText(f"Prediction: {display}")
            processed_at = time.monotonic()
            if self.evaluation_trace is not None:
                try:
                    self.evaluation_trace.append(prediction, processed_at)
                    self.trace_status.setText(
                        f"Recording {self.evaluation_trace.frame_count} inputs | "
                        f"Capture time {prediction.timestamp:.3f} s | Pause to save for annotation."
                    )
                except (ValueError, OverflowError) as exc:
                    self.pause()
                    self.state.setText(f"Evaluation capture stopped: {exc}. Saved trace covers earlier inputs only.")
                    return
            event = (
                self.routing.process(prediction, processed_at)
                if self.routing is not None
                else self.controller.process(prediction, processed_at)
            )
            self.state.setText(control.state.replace("_", " "))
            self.progress.setValue(round(control.progress * 100))
            if control.state == "WAIT_NEUTRAL" and prediction.rejection_reason in {
                "distance_rejection", "margin_rejection",
            }:
                guidance = "Show NEUTRAL until READY, then retry."
            else:
                guidance = (
                    self.rejection_message(prediction.rejection_reason)
                    if prediction.rejection_reason
                    else ""
                )
            self.detail.setText(guidance or control.last_error or
                                "Return to neutral between commands. Esc pauses immediately.")
            if event:
                if self.routing is not None:
                    identity = self._session_outcome_identity()
                    if not self._reserve_session_record():
                        self.pause()
                        return
                    result = self.routing.route(event, time.monotonic())
                    if result.simulated_action is not None:
                        action = self.action_text(result.simulated_action)
                        self.feedback.setText(
                            f"Studio simulation: {event.command} would {action}."
                        )
                        self._record_session_outcome(
                            source="gesture",
                            status="simulated",
                            action=result.simulated_action,
                            reason=f"gesture {event.command}",
                            event_id=event.event_id,
                            identity=identity,
                        )
                        self.log({
                            "type": "studio_simulation", "source": "gesture",
                            "event_id": event.event_id, "command": event.command,
                            "action": result.simulated_action.kind.value,
                            "timestamp": time.monotonic(),
                        })
                    elif result.rejection_reason:
                        self.feedback.setText(
                            f"Studio routing rejected {event.command}: {result.rejection_reason}."
                        )
                        self._record_session_outcome(
                            source="gesture",
                            status="rejected",
                            action=None,
                            reason=result.rejection_reason,
                            event_id=event.event_id,
                            identity=identity,
                        )
                else:
                    old_topic = self.card_topic_text()
                    moved = self.viewer.apply(event)
                    event = replace(event, resulting_position=self.viewer.position)
                    self.render_card()
                    self.log({"type": "command", "source": "gesture", **asdict(event)})
                    self.feedback.setText(
                        f"NEXT accepted: now showing {self.card_topic_text()} (from {old_topic})."
                        if moved else f"NEXT accepted, still showing {old_topic}; this is the final card."
                    )
        elif (control.state != "PAUSED" and time.monotonic() - self.last_result_at
              > (2 if self.received_first_frame else 20)):
            self.pause()
            self.state.setText("Camera stalled. Wait for shutdown, then restart.")
            if self.studio:
                self.detail.setText("Close other camera apps and check the cable/permissions. "
                                    "Wait for release, then retry Start or select another camera index.")
        if self.worker.isFinished():
            error = self.worker.error
            self.worker.wait()
            self.worker = None
            self.finish_evaluation_trace()
            control.fault(error or "Camera stopped")
            self.state.setText(error or "Paused • camera released")
            if self.studio:
                self.record_trace.setEnabled(self.evaluation_trace is None)
                self.preview.clear()
                self.preview.setText("Camera off\n\nStart explicitly to reconnect")
                if error:
                    self.detail.setText(f"Capture stopped: {error}\n"
                                        "Check the hand model, camera connection and permissions; close other "
                                        "camera apps. Retry Start or choose another camera index.")
            self.start_button.setEnabled(self.model is not None and self.model_loader is None and not self.routing_manual_only)

    def changeEvent(self, event):
        if self.studio and event.type() == QEvent.Type.ActivationChange and not self.isActiveWindow():
            self.pause()
            self.state.setText("Paused after focus loss. Resume Studio before gestures.")
        super().changeEvent(event)

    def closeEvent(self, event):
        self._closing = True
        self.pause()
        if self.evaluation_trace is not None:
            self._closing = False
            event.ignore()
            return
        if (
            self.studio and self._auto_archive_summary_on_close
            and not self._archive_session_summary("Window not closed")
        ):
            self._closing = False
            event.ignore()
            return
        if self.worker is not None and not self.worker.wait(3000):
            self.log({"type": "camera_shutdown_timeout", "timestamp": time.monotonic(),
                      "note": "Native driver stalled; daemon worker will end with process exit."})
        self.timer.stop()
        event.accept()
