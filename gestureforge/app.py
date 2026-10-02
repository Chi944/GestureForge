"""Assignment desktop shell: one real action, with future scope clearly labelled."""

from collections.abc import Callable, Mapping
import os
from dataclasses import asdict, replace
import json
from pathlib import Path
from threading import Event, Lock, Thread
import time
from typing import cast
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
from .contracts import Action, ActionType, Observation, Prediction, RoutingMode, validate_identifier
from .controller import Controller
from .dispatcher import DispatchFailure, Dispatcher
from .enrolment import EnrolmentPlan
from .routing import RoutingSession
from .readiness import ReadinessCheck, behavior_revision
from .storage import read_json
from .viewer import Viewer, load_deck
from .javier_widgets import (
    QuickActionsWidget,
    RunbookEditorWidget,
    RunbookWidget,
    SessionSummaryWidget,
    ViewerWidget,
    WorkspaceWidget,
)
from .enrolment_widget import EnrolmentWidget
from .profile_widget import ProfileSelectorWidget
from .profiles import LoadedProfile, ProfileStore
from .runbook import Runbook
from .session_summary import Outcome, SessionSummary
from .shortcuts import Target, TargetRegistry, WindowsLauncher
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
DEFAULT_STUDIO_STATE_FOLDER = Path(__file__).resolve().parent.parent / ".local/studio"
DEFAULT_ENROLMENT_FOLDER = Path(__file__).resolve().parent.parent / "data/local/enrolment"


class UnsupportedLauncher:
    def open(self, target: Target, resolved: str) -> None:
        raise DispatchFailure("LIVE desktop launch is available on Windows only; use manual controls on this platform.")


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

    def __init__(self, load: Callable[[], object], *, kind="dataset", profile_id=None):
        super().__init__(daemon=True, name="gestureforge-model-load")
        self.load = load
        self.kind = kind
        self.profile_id = profile_id
        self.result: object | None = None
        self.error = ""

    def run(self):
        try:
            self.result = self.load()
        except Exception as exc:
            self.error = f"{type(exc).__name__}: {exc}"


class CaptureWorker(Thread):
    """One bounded mailbox prevents a slow interface accumulating old frames."""

    def __init__(
        self, model, feature_function, chosen_hand, camera_index, asset, session, profile, *,
        observation_only=False,
    ):
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
        self.observation_only = observation_only
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
                    if self.observation_only:
                        with self._lock:
                            self._latest = (frame, observation)
                        continue
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
                 vocabulary=LEGACY_VOCABULARY, model_settings=("knn", 1.5, 1.5),
                 profile_display_name=None, profile_store=None, loaded_profile=None):
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
        self.studio_authored_bindings = dict(zip(vocabulary.action_ids, STUDIO_ACTIONS, strict=True))
        self.selected_profile_id = profile if model is not None and profile_display_name is not None else None
        self.selected_profile_name = profile_display_name or ""
        self.pending_profile_id = None
        self._deleted_profile_ids: set[str] = set()
        self._profile_selector_installing = False
        self.readiness_check: ReadinessCheck | None = None
        self.readiness_revision = ""
        self.readiness_pass_revision = ""
        self._readiness_previous: tuple[bool, str, RoutingMode, dict[str, Action], bool] | None = None
        self._readiness_switching = False
        self._closing = False
        self.last_result_at = 0.0
        self.received_first_frame = False
        self._log_path = None
        self._log_failed = False
        self._auto_archive_summary_on_close = True
        self.evaluation_trace: EvaluationTrace | None = None
        self.trace_path: Path | None = None
        self.trace_folder = Path(__file__).resolve().parent.parent / "experiments/local/controller-traces"
        self.studio_state_folder = DEFAULT_STUDIO_STATE_FOLDER
        self.profile_store = profile_store or ProfileStore(self.studio_state_folder.parent / "profiles")
        self.enrolment_root = DEFAULT_ENROLMENT_FOLDER
        self.pending_enrolment_plan = None
        self.pending_enrolment_request_id = ""
        self.enrolment_request_id = ""
        self.enrolment_capture_session = ""
        self.enrolment_capture_profile = ""
        self.enrolment_capture_attached = False
        self.enrolment_capture_started_at = 0.0
        self.enrolment_received_first_frame = False
        self.quick_actions_context_id = f"quick-actions:{uuid4().hex[:8]}"
        self.quick_actions_active = False
        self.quick_registry = TargetRegistry()
        launcher = WindowsLauncher() if os.name == "nt" else UnsupportedLauncher()
        self.dispatcher = Dispatcher(
            self.quick_registry,
            launcher,
            self._dispatcher_snapshot,
            self._dispatcher_active,
            self._gesture_live_ready,
            self._dispatcher_pause,
            self._release_capture_for_dispatch,
            self.viewer,
            self.runbook,
            self.session_summary,
        )
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
            readiness_row = QHBoxLayout()
            self.readiness_start_button = QPushButton("Start/retry readiness")
            self.readiness_start_button.setAccessibleName("Start or retry guided readiness check")
            self.readiness_start_button.setToolTip(
                "Runs a simulated readiness check: two correct activations for each enrolled action gesture."
            )
            self.readiness_start_button.clicked.connect(self.start_readiness_check)
            readiness_row.addWidget(self.readiness_start_button)
            self.readiness_finish_button = QPushButton("Finish readiness")
            self.readiness_finish_button.setAccessibleName("Finish guided readiness check")
            self.readiness_finish_button.setToolTip("Incomplete checks fail; passed checks remain tied to this profile revision.")
            self.readiness_finish_button.clicked.connect(self.finish_readiness_check)
            readiness_row.addWidget(self.readiness_finish_button)
            page.addLayout(readiness_row)
            self.readiness_progress = QProgressBar()
            self.readiness_progress.setRange(0, 6)
            self.readiness_progress.setValue(0)
            self.readiness_progress.setAccessibleName("Readiness check progress")
            page.addWidget(self.readiness_progress)
            self.readiness_status = QLabel("Readiness check unavailable until a personal recogniser is loaded.")
            self.readiness_status.setWordWrap(True)
            self.readiness_status.setObjectName("muted")
            self.readiness_status.setTextFormat(Qt.TextFormat.PlainText)
            page.addWidget(self.readiness_status)
            self.load_progress = QProgressBar()
            self.load_progress.setRange(0, 0)
            self.load_progress.setAccessibleName("Loading and training personal dataset")
            self.load_progress.hide()
            page.addWidget(self.load_progress)
            page.addWidget(self.studio_status)
            settings = QGridLayout()
            page.addLayout(settings)
            self.mode_picker = QComboBox()
            self.mode_picker.setAccessibleName("Studio action mode")
            for mode in (RoutingMode.PREVIEW, RoutingMode.REHEARSAL, RoutingMode.LIVE):
                label = "Live (manual controls)" if mode == RoutingMode.LIVE else mode.value.title()
                self.mode_picker.addItem(label, mode.value)
            mode_label = QLabel("Studio action mode")
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
                "Apply these action settings, stop the camera and require neutral on resume."
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
                    "Counts cover Studio manual card/runbook/Quick Actions, live manual launch requests, "
                    "and gesture simulation/rejection events. "
                    "Bookmark list review/removal and OS completion are outside this summary. "
                    "Only explicit acknowledgement records task completion."
                ),
            )
            self.summary_widget.setObjectName("manualViewer")
            self.summary_widget.setMinimumWidth(0)
            self.summary_widget.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Expanding)
            self.deck_tabs.addTab(self.summary_widget, "Session summary")
            self.profile_selector = ProfileSelectorWidget(self.profile_store, host=self)
            self.profile_selector.setObjectName("manualViewer")
            self.profile_selector.setMinimumWidth(0)
            self.profile_selector.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Expanding)
            self.profile_selector.busy_changed.connect(self.set_profile_selector_busy)
            self.profile_selector.profile_selected.connect(lambda _selection: self.sync_profile_selector())
            self.profile_selector.guest_selected.connect(lambda: self.sync_profile_selector())
            self.profile_selector.profile_renamed.connect(self.rename_studio_profile)
            self.profile_selector.profile_deleted.connect(lambda _profile_id: self.sync_profile_selector())
            self.profile_selector.start_requested.connect(self.request_profile_preview_start)
            self.deck_tabs.addTab(self.profile_selector, "Profiles")
            self.enrolment_widget = EnrolmentWidget(self.enrolment_root)
            self.enrolment_widget.setObjectName("manualViewer")
            self.enrolment_widget.setMinimumWidth(0)
            self.enrolment_widget.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Expanding)
            self.enrolment_widget.capture_requested.connect(self.start_enrolment_capture)
            self.enrolment_widget.capture_release_requested.connect(self.release_enrolment_capture)
            self.enrolment_widget.dataset_saved.connect(self.enrolment_dataset_saved)
            self.deck_tabs.addTab(self.enrolment_widget, "Enrolment")
            self.quick_actions_page = QWidget()
            self.quick_actions_page.setObjectName("manualViewer")
            self.quick_actions_page.setMinimumWidth(0)
            self.quick_actions_page.setSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Expanding)
            quick_layout = QVBoxLayout(self.quick_actions_page)
            self.use_quick_actions_button = QPushButton("Use Quick Actions")
            self.use_quick_actions_button.clicked.connect(self.use_quick_actions_context)
            quick_layout.addWidget(self.use_quick_actions_button)
            self.quick_actions_widget = QuickActionsWidget(
                self.quick_registry,
                self.studio_state_folder / "quick-actions-targets.json",
                before_publish=self.prepare_quick_action_change,
            )
            self.quick_actions_widget.set_gesture_ids(tuple(self.vocabulary.action_ids))
            self.quick_actions_widget.action_requested.connect(self.manual_quick_action)
            self.quick_actions_widget.bindings_changed.connect(self.accept_quick_bindings_change)
            self.quick_actions_widget.focus_lost.connect(self.pause)
            quick_layout.addWidget(self.quick_actions_widget)
            self.deck_tabs.addTab(self.quick_actions_page, "Quick Actions")
            self.deck_tabs.currentChanged.connect(self.on_studio_tab_changed)
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
            self.render_readiness_status()
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
        self.sync_profile_selector(loaded_profile)

    def _model_version(self) -> str:
        return getattr(self.model, "model_version", "unversioned")

    def _can_start_studio_camera(self) -> bool:
        mode = None
        if self.routing is not None:
            mode = self.manual_mode if self.routing_manual_only else self.routing.snapshot.mode
        return (
            self.model is not None and self.worker is None and self.model_loader is None
            and not self._closing and not self.routing_manual_only and not self._enrolment_blocks_recognition()
            and not self._profile_selector_busy() and mode != RoutingMode.LIVE
        )

    def _profile_selector_busy(self) -> bool:
        return bool(self.studio and hasattr(self, "profile_selector") and self.profile_selector.busy)

    def _profile_selector_change_blocked(self) -> bool:
        return self._profile_selector_busy() and not self._profile_selector_installing

    def _readiness_bindings(self) -> dict[str, Action]:
        defaults = dict(zip(self.vocabulary.action_ids, STUDIO_ACTIONS, strict=True))
        authored: Mapping[str, Action] = self.studio_authored_bindings
        return {gesture: authored.get(gesture, defaults[gesture]) for gesture in self.vocabulary.action_ids}

    def _readiness_behavior_revision(self) -> str:
        return behavior_revision(
            self.profile, self._model_version(), self.chosen_hand,
            self.workspace, self.quick_registry, self._readiness_bindings(),
        )

    def _readiness_status_value(self) -> str:
        check = self.readiness_check
        return check.status if check is not None else "idle"

    def _readiness_completed_value(self) -> int:
        check = self.readiness_check
        return check.completed if check is not None else 0

    def render_readiness_status(self) -> None:
        if not self.studio or not hasattr(self, "readiness_status"):
            return
        revision = self._readiness_behavior_revision() if self.model is not None else ""
        if self.readiness_check is not None and revision:
            self.readiness_check.invalidate(revision)
        self.readiness_progress.setValue(self._readiness_completed_value())
        if self.model is None or self.routing is None:
            text = "Readiness unavailable: load a personal recogniser before checking gestures."
        elif self.readiness_check is not None:
            check = self.readiness_check
            status = self._readiness_status_value()
            expected = check.expected
            reason = check.reason
            if status == "running" and expected:
                text = f"Readiness running: perform {expected}. {self._readiness_completed_value()}/6 complete."
            elif status == "passed":
                text = "Readiness passed for this local session revision. Gesture actions still simulate only."
            elif status in {"failed", "expired"}:
                text = f"Readiness {status}: {reason or 'retry the guided check'}."
            else:
                text = f"Readiness {status}: {self._readiness_completed_value()}/6 complete."
        elif revision and self.readiness_pass_revision == revision:
            text = "Readiness passed for this local session revision. Gesture actions still simulate only."
        else:
            text = "Readiness not checked: Start/retry requires two correct activations for each action gesture."
        self.readiness_status.setText(text)
        self.readiness_start_button.setEnabled(
            self.model is not None and self.routing is not None
            and not self._closing and self.model_loader is None
            and not self._profile_selector_busy() and not self._enrolment_blocks_recognition()
        )
        self.readiness_finish_button.setEnabled(self.readiness_check is not None)

    def _invalidate_readiness(self, reason: str) -> bool:
        if not self.studio or self._readiness_switching:
            return True
        check = self.readiness_check
        if check is not None:
            check.cancel(reason)
            if not self._restore_readiness_routing():
                self.render_readiness_status()
                return False
            self.readiness_check = None
        self._readiness_previous = None
        self.readiness_revision = ""
        self.readiness_pass_revision = ""
        if hasattr(self, "readiness_status"):
            self.readiness_status.setText(f"Readiness reset: {reason}.")
            self.readiness_progress.setValue(0)
            self.render_readiness_status()
        return True

    def _invalidate_readiness_if_revision_changed(self, reason: str) -> bool:
        if not self.studio or self.model is None:
            return self._invalidate_readiness(reason)
        revision = self._readiness_behavior_revision()
        check = self.readiness_check
        if check is not None:
            check.invalidate(revision)
            if check.status != "expired":
                self.render_readiness_status()
                return True
        if self.readiness_pass_revision and self.readiness_pass_revision == revision:
            self.render_readiness_status()
            return True
        return self._invalidate_readiness(reason)

    def _record_readiness_trials(self, check: ReadinessCheck) -> None:
        existing = {trial.id for trial in self.session_summary.trials}
        for trial in check.trials:
            if trial.id not in existing:
                self.session_summary.record_trial(trial)
                existing.add(trial.id)
        if hasattr(self, "summary_widget"):
            self.summary_widget.refresh()

    def _restore_readiness_routing(self) -> bool:
        previous = self._readiness_previous
        if previous is None or self.routing is None:
            return True
        manual_only, context_id, mode, bindings, quick_actions_active = previous
        self._readiness_switching = True
        try:
            restored = self.configure_studio(context_id=context_id, mode=mode, bindings={} if manual_only else bindings)
        finally:
            self._readiness_switching = False
        if restored:
            self.quick_actions_active = bool(
                quick_actions_active and not manual_only and context_id == self.quick_actions_context_id and bindings
            )
            self._readiness_previous = None
            return True
        self.readiness_status.setText("Readiness finished but prior context was not restored; fix trace storage, then Finish again.")
        return False

    def _cancel_readiness_check(self, reason: str) -> bool:
        check = self.readiness_check
        if check is None or self._readiness_switching:
            return True
        check.cancel(reason)
        self._record_readiness_trials(check)
        restored = self._restore_readiness_routing()
        if restored:
            if check.status == "passed":
                self.readiness_pass_revision = check.revision
            else:
                self.readiness_pass_revision = ""
            self.readiness_check = None
            self.readiness_revision = ""
            self.readiness_progress.setValue(0)
            self.render_readiness_status()
        return restored

    def start_readiness_check(self) -> bool:
        if not self.studio or self._closing or self.model_loader is not None:
            return False
        if self.model is None or self.routing is None:
            self.readiness_status.setText("Readiness unavailable: load a personal recogniser first.")
            return False
        if self.readiness_check is not None and not self._cancel_readiness_check("Readiness cancelled before retry."):
            self.readiness_status.setText("Readiness retry not started: save the current trace first.")
            return False
        if self._profile_selector_change_blocked() or self._enrolment_blocks_recognition():
            self.readiness_status.setText("Readiness not started: finish profile or enrolment work first.")
            return False
        if self.worker is not None:
            if not self.pause():
                self.readiness_status.setText("Readiness not started: save the current trace or collection first.")
                return False
            self.readiness_status.setText("Readiness waiting for camera release; retry once the camera is off.")
            return False
        revision = self._readiness_behavior_revision()
        if not revision:
            self.readiness_status.setText("Readiness revision unavailable; retry after the engine is ready.")
            return False
        snapshot = self.routing.snapshot
        previous_bindings = dict(snapshot.bindings)
        self._readiness_previous = (self.routing_manual_only, self.manual_context_id if self.routing_manual_only else snapshot.context_id,
                                    self.manual_mode if self.routing_manual_only else snapshot.mode, previous_bindings,
                                    self.quick_actions_active)
        self._readiness_switching = True
        try:
            if not self.configure_studio(
                context_id="readiness:" + uuid4().hex[:24],
                mode=RoutingMode.PREVIEW,
                bindings=self._readiness_bindings(),
            ):
                self._readiness_previous = None
                return False
        finally:
            self._readiness_switching = False
        self.readiness_check = ReadinessCheck(revision, tuple(self.vocabulary.action_ids))
        self.readiness_revision = revision
        self.readiness_pass_revision = ""
        self.readiness_progress.setValue(0)
        self.feedback.setText("Readiness check started. Actions are simulated only; no OS launch can occur.")
        self.render_studio_status()
        self.start_camera()
        return True

    def finish_readiness_check(self) -> bool:
        check = self.readiness_check
        if check is None:
            self.render_readiness_status()
            return False
        check.finish()
        self._record_readiness_trials(check)
        status = self._readiness_status_value()
        revision = self.readiness_revision
        restored = self._restore_readiness_routing()
        if not restored:
            self.feedback.setText("Readiness finished but prior context is retained for recovery; save the trace and press Finish again.")
            self.render_readiness_status()
            return False
        if status == "passed":
            self.readiness_pass_revision = revision
            self.feedback.setText("Readiness passed for this local session revision; Studio remains simulation-only.")
        else:
            self.readiness_pass_revision = ""
            self.feedback.setText("Readiness incomplete or failed; retry before relying on rehearsal evidence.")
        self.readiness_check = None
        self.readiness_revision = ""
        self.render_studio_status()
        return status == "passed"

    def _record_readiness_result(self, event, result) -> None:
        check = self.readiness_check
        if check is None or result.simulated_action is None:
            return
        revision = self._readiness_behavior_revision()
        check.record(event, result, revision)
        status = self._readiness_status_value()
        if status == "passed":
            self._record_readiness_trials(check)
            if self._restore_readiness_routing():
                self.readiness_pass_revision = revision
        elif status in {"failed", "expired"}:
            self._record_readiness_trials(check)
            self.readiness_pass_revision = ""
            self._restore_readiness_routing()
        self.render_studio_status()

    def _enrolment_state(self) -> str:
        if not self.studio or not hasattr(self, "enrolment_widget"):
            return "idle"
        session = self.enrolment_widget.session
        return session.state if session is not None else "idle"

    def _enrolment_tab_selected(self) -> bool:
        if not self.studio or not hasattr(self, "enrolment_widget"):
            return False
        return self.deck_tabs.currentWidget() is self.enrolment_widget

    def _enrolment_blocks_recognition(self) -> bool:
        if not self.studio or not hasattr(self, "enrolment_widget"):
            return False
        if self._enrolment_tab_selected():
            return True
        state = self._enrolment_state()
        return bool(
            self.pending_enrolment_request_id
            or self.enrolment_request_id
            or self.enrolment_widget.pending_plan is not None
            or state not in ("idle", "complete", "cancelled")
        )

    def _display_capture_frame(self, frame) -> None:
        rgb = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB)
        height, width, channels = rgb.shape
        image = QImage(rgb.data, width, height, width * channels,
                       QImage.Format.Format_RGB888).copy()
        self.preview.setPixmap(QPixmap.fromImage(image).scaled(
            self.preview.size(), Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        ))

    def _pause_capture_only(self) -> bool:
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

    def _clear_enrolment_capture(self) -> None:
        self.enrolment_request_id = ""
        self.enrolment_capture_session = ""
        self.enrolment_capture_profile = ""
        self.enrolment_capture_attached = False
        self.enrolment_capture_started_at = 0.0
        self.enrolment_received_first_frame = False

    def _retire_enrolment_capture(self, request_id: str) -> bool:
        if request_id == self.pending_enrolment_request_id:
            self.pending_enrolment_plan = None
            self.pending_enrolment_request_id = ""
            self.start_button.setEnabled(self._can_start_studio_camera() and not self._enrolment_blocks_recognition())
            return True
        if request_id != self.enrolment_request_id:
            return False
        if self.worker is not None and getattr(self.worker, "observation_only", False):
            self.worker.requestInterruption()
        self._clear_enrolment_capture()
        self.start_button.setEnabled(self._can_start_studio_camera() and not self._enrolment_blocks_recognition())
        return True

    def _fail_enrolment_capture(self, reason: str) -> None:
        request_id = self.enrolment_request_id
        if request_id and hasattr(self, "enrolment_widget"):
            self.enrolment_widget.capture_failed(request_id, reason)
        if request_id == self.enrolment_request_id:
            self._retire_enrolment_capture(request_id)
        self.detail.setText(reason)

    def start_enrolment_capture(self, plan, request_id: str) -> None:
        if (
            not request_id
            or not hasattr(self, "enrolment_widget")
            or self.enrolment_widget.request_id != request_id
            or self.enrolment_widget.pending_plan is not plan
        ):
            return
        if (
            not self.studio or self._closing or self.model_loader is not None
            or self._profile_selector_change_blocked()
        ):
            self.enrolment_widget.capture_failed(request_id, "Studio is busy; retry enrolment when the shell is idle.")
            return
        if self._enrolment_state() == "save_error":
            self.enrolment_widget.capture_failed(request_id, "Retry the unsaved enrolment trial before starting another capture.")
            return
        if not self._pause_capture_only():
            self.enrolment_widget.capture_failed(request_id, "Save the current evaluation trace before enrolment.")
            return
        self.pending_enrolment_plan = plan
        self.pending_enrolment_request_id = request_id
        if self.worker is not None:
            self.state.setText("Waiting for previous camera release before enrolment.")
            self.preview.setText("Camera stopping...\n\nEnrolment will start after release.")
            self.start_button.setEnabled(False)
            return
        self._start_pending_enrolment_if_ready()

    def _start_pending_enrolment_if_ready(self) -> bool:
        plan = self.pending_enrolment_plan
        if self.worker is not None or not self.pending_enrolment_request_id or plan is None:
            return False
        request_id = self.pending_enrolment_request_id
        if (
            self._closing
            or not hasattr(self, "enrolment_widget")
            or self.enrolment_widget.pending_plan is not plan
            or self.enrolment_widget.request_id != request_id
            or self.deck_tabs.currentWidget() is not self.enrolment_widget
        ):
            self.pending_enrolment_plan = None
            self.pending_enrolment_request_id = ""
            return False
        if self._profile_selector_change_blocked():
            self.enrolment_widget.capture_failed(
                request_id, "Studio is busy; retry enrolment when the shell is idle."
            )
            if request_id == self.pending_enrolment_request_id:
                self.pending_enrolment_plan = None
                self.pending_enrolment_request_id = ""
            self.detail.setText("Studio is busy; retry enrolment when the shell is idle.")
            return False
        plan = cast(EnrolmentPlan, plan)
        capture_profile = plan.participant
        capture_hand = plan.hand
        self.pending_enrolment_plan = None
        self.pending_enrolment_request_id = ""
        capture_session = "enrol-" + uuid4().hex
        self.enrolment_request_id = request_id
        self.enrolment_capture_session = capture_session
        self.enrolment_capture_profile = capture_profile
        self.enrolment_capture_attached = False
        self.enrolment_capture_started_at = time.monotonic()
        self.enrolment_received_first_frame = False
        self.last_result_at = self.enrolment_capture_started_at
        self.received_first_frame = False
        self.worker = CaptureWorker(
            None, None, capture_hand, self.camera_index, self.asset, capture_session, capture_profile,
            observation_only=True,
        )
        self.worker.start()
        self.start_button.setEnabled(False)
        self.state.setText("Opening camera for enrolment • gesture routing paused")
        self.preview.setText(f"Opening camera {self.camera_index} for enrolment...")
        return True

    def release_enrolment_capture(self, request_id: str) -> None:
        self._retire_enrolment_capture(request_id)

    def enrolment_dataset_saved(self, manifest) -> None:
        message = f"Enrolment session saved: {manifest}"
        self.feedback.setText(message)
        self.enrolment_widget.feedback.setText(message)
        self.enrolment_widget.cue.setText("Session saved. Review the manifest path below before training separately.")

    def _show_enrolment_retry_required(self) -> None:
        if not self.studio or not hasattr(self, "enrolment_widget"):
            return
        self.deck_tabs.setCurrentWidget(self.enrolment_widget)
        self.enrolment_widget.feedback.setText("Retry saving the unsaved enrolment trial before leaving or changing context.")
        self.detail.setText("Retry save in Enrolment, or keep this window open until the trial is saved.")
        self.state.setText("Enrolment save pending")

    def _scroll_enrolment_controls_into_view(self) -> None:
        if not self.studio or not hasattr(self, "studio_scroll"):
            return
        request_id = self.enrolment_request_id

        def scroll_to_bottom() -> None:
            if (
                self._closing or not self._enrolment_tab_selected()
                or not request_id or request_id != self.enrolment_request_id
            ):
                return
            bar = self.studio_scroll.verticalScrollBar()
            bar.setValue(bar.maximum())

        QTimer.singleShot(0, scroll_to_bottom)

    def _stop_enrolment_for_pause(self) -> bool:
        if not self.studio or not hasattr(self, "enrolment_widget"):
            return True
        state = self._enrolment_state()
        if state == "save_error":
            self.enrolment_widget.stop_collection()
            if self.enrolment_request_id:
                self._retire_enrolment_capture(self.enrolment_request_id)
            self._show_enrolment_retry_required()
            return False
        if (
            self.pending_enrolment_request_id or self.enrolment_request_id
            or self.enrolment_widget.pending_plan is not None
            or state not in ("idle", "complete", "cancelled")
        ):
            self.enrolment_widget.stop_collection()
            if self._enrolment_state() == "save_error":
                if self.enrolment_request_id:
                    self._retire_enrolment_capture(self.enrolment_request_id)
                self._show_enrolment_retry_required()
                return False
        return True

    def on_studio_tab_changed(self, _index: int) -> None:
        self.render_card()
        if not self.studio:
            return
        if self._enrolment_tab_selected():
            self.preview.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom)
            if self.worker is not None or self.readiness_check is not None:
                if not self.pause():
                    self.detail.setText("Enrolment not opened: save the current trace or collection first.")
                    return
            self.prediction.setText("Enrolment mode: camera observations only")
            self.detail.setText(
                "Request collection, wait for camera preview, then Begin trial. "
                "No gestures are routed and no model is trained here."
            )
            self.studio_status.setText("Personal enrolment saves a local manifest only; readiness remains unverified.")
        else:
            self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
            if not self._stop_enrolment_for_pause():
                return
        if not self._enrolment_tab_selected() and self.worker is None:
            self.prediction.setText(
                "Prediction: awaiting new camera session"
                if self.model is not None else
                "Camera control unavailable: no gesture dataset loaded"
            )
            self.detail.setText("Start -> neutral pose -> hold a bound gesture -> return to neutral")
            self.render_studio_status()
        self.start_button.setEnabled(self._can_start_studio_camera() and not self._enrolment_blocks_recognition())

    def action_text(self, action: Action) -> str:
        if action.kind == ActionType.OPEN_SHORTCUT:
            if action.shortcut_id:
                for target in self.quick_registry.targets:
                    if target.id == action.shortcut_id:
                        return f"open {target.label}"
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
        if hasattr(self, "dispatcher"):
            self.dispatcher.summary = self.session_summary
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

    def _dispatcher_snapshot(self):
        assert self.routing is not None
        return self.routing.snapshot

    def _dispatcher_active(self) -> bool:
        return bool(
            self.routing is not None
            and not self.routing_manual_only
            and self.routing.state != "PAUSED"
            and not self._closing
        )

    def _gesture_live_ready(self, _snapshot) -> bool:
        # GF-P10's six-gesture check is a short simulation check only. GF-P12
        # owns longer LIVE personal readiness, so routed gestures cannot launch.
        return False

    def _dispatcher_pause(self) -> None:
        if not self.pause():
            raise DispatchFailure("Save the current trace or enrolment trial before dispatching.")

    def _release_capture_for_dispatch(self, snapshot) -> bool:
        if self.routing is None or snapshot != self.routing.snapshot:
            return False
        worker = self.worker
        if worker is None:
            return True
        worker.requestInterruption()
        if not worker.wait(750) or not worker.isFinished() or self.worker is not worker:
            return False
        if self.routing is None or snapshot != self.routing.snapshot:
            return False
        self.worker = None
        self.received_first_frame = False
        self.record_trace.setEnabled(self.evaluation_trace is None)
        self.preview.clear()
        self.preview.setText("Camera off\n\nManual request released capture")
        self.start_button.setEnabled(self._can_start_studio_camera())
        return True

    def _sync_dispatcher_refs(self) -> None:
        self.dispatcher.viewer = self.viewer if self.deck_available else None
        self.dispatcher.runbook = self.runbook
        self.dispatcher.summary = self.session_summary

    def _dispatch_action(self, action: Action, *, event_id: str | None = None,
                         source: str = "manual"):
        if (
            not self.studio or self.routing is None or self._closing
            or self.model_loader is not None or self._profile_selector_change_blocked()
            or self._enrolment_blocks_recognition()
            or (self.isVisible() and not self.isActiveWindow())
        ):
            self.feedback.setText("Action not requested: finish Studio work before dispatch.")
            return None
        if not self._reserve_session_record():
            return None
        mode = self.manual_mode if self.routing_manual_only else self.routing.snapshot.mode
        if mode == RoutingMode.LIVE and not self.finish_evaluation_trace():
            self.feedback.setText("Action not requested: save the current evaluation trace first.")
            return None
        self._sync_dispatcher_refs()
        outcome = self.dispatcher.manual(event_id or f"manual-{uuid4()}", action)
        if hasattr(self, "summary_widget"):
            self.summary_widget.refresh()
        self._handle_dispatch_outcome(outcome, action, source=source)
        return outcome

    def _handle_dispatch_outcome(self, outcome: Outcome, action: Action, *, source: str) -> None:
        if outcome.status == "simulated":
            self.feedback.setText(f"Studio simulation: {source} would {self.action_text(action)}.")
        elif outcome.status == "launch_requested":
            self.feedback.setText("LIVE manual request sent to Windows. Acknowledge completion separately.")
        elif outcome.status in {"applied", "unchanged"}:
            if action.kind == ActionType.ADVANCE_STAGE and self.runbook is not None:
                self.runbook.paused = True
            self._refresh_workspace_widgets()
            self.render_card()
            if action.kind == ActionType.ADVANCE_STAGE:
                self.feedback.setText("Runbook advanced." if outcome.status == "applied" else "Runbook did not change.")
            else:
                self.feedback.setText(
                    f"Manual {action.kind.value}: now showing {self.card_topic_text()}."
                    if outcome.status == "applied" and action.kind != ActionType.BOOKMARK
                    else f"Manual {action.kind.value}: {self.action_text(action)}."
                    if outcome.status == "applied"
                    else f"Manual {action.kind.value}: no change."
                )
        elif outcome.status == "duplicate":
            self.feedback.setText("Action already consumed; request a fresh manual action.")
        elif outcome.status == "rejected":
            self.feedback.setText(f"Action rejected: {outcome.reason}")
        else:
            self.feedback.setText(f"Action failed: {outcome.reason}")

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
        if hasattr(self, "dispatcher"):
            self._sync_dispatcher_refs()

    def _quick_action_bindings(self) -> dict[str, Action]:
        if not self.studio:
            return {}
        bindings = {}
        for gesture, slot in zip(self.vocabulary.action_ids, self.quick_registry.quick_slots, strict=True):
            if slot is None:
                continue
            self.quick_registry.resolve(slot)
            bindings[gesture] = Action(ActionType.OPEN_SHORTCUT, slot)
        return bindings

    def prepare_quick_action_change(self) -> bool:
        if not self.studio:
            return True
        if self.model_loader is not None or self._closing or self._profile_selector_change_blocked():
            self.set_deck_file_status("Quick Actions not changed: wait for Studio to be idle.")
            return False
        if not self.pause():
            self.set_deck_file_status("Quick Actions not changed: save the current evaluation trace first.")
            return False
        return True

    def accept_quick_bindings_change(self, _bindings) -> None:
        if not self.studio:
            return
        if self.configure_studio(context_id=self.quick_actions_context_id, bindings={}):
            self.quick_actions_active = False
            self._invalidate_readiness_if_revision_changed("Quick Actions bindings changed")
            self.quick_actions_widget.status.setText(
                "Quick Actions changed and Studio paused. Click Use Quick Actions to activate valid slots."
            )

    def use_quick_actions_context(self) -> bool:
        if not self.studio or self.model_loader is not None or self._closing or self._profile_selector_change_blocked():
            return False
        try:
            bindings = self._quick_action_bindings()
        except (ValueError, OSError) as exc:
            self.configure_studio(context_id=self.quick_actions_context_id, bindings={})
            self.quick_actions_active = False
            self.quick_actions_widget.status.setText(f"Quick Actions paused: repair target before activation: {exc}")
            return False
        if not self.configure_studio(context_id=self.quick_actions_context_id, bindings=bindings):
            return False
        if bindings:
            self.quick_actions_active = True
            self.feedback.setText("Quick Actions active for gesture simulation. Manual target tests also simulate.")
            self.quick_actions_widget.status.setText("Quick Actions active. Start camera explicitly and show NEUTRAL.")
            return True
        self.quick_actions_active = False
        self.feedback.setText("Quick Actions has no valid slots; manual target tests still simulate.")
        self.quick_actions_widget.status.setText("Quick Actions paused: bind at least one valid local target.")
        return False

    def manual_quick_action(self, action: Action) -> None:
        if (
            not self.studio or action.kind != ActionType.OPEN_SHORTCUT
            or action.shortcut_id is None or self.model_loader is not None or self._closing
        ):
            return
        try:
            self.quick_registry.resolve(action.shortcut_id)
        except (ValueError, OSError):
            pass
        self._dispatch_action(action, source="Quick Action")

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
        if self.runbook is not None:
            self.runbook.paused = True
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
        profile_text = "Guest/manual"
        if self.model is not None:
            profile_text = self.profile
            if self.selected_profile_id == self.profile and self.selected_profile_name:
                profile_text = f"{self.selected_profile_name} ({self.profile})"
        self.camera_status.setText(
            f"Selected camera: {self.camera_index} | Enrolled hand: {self.chosen_hand} | "
            f"Profile: {profile_text} | "
            f"{self.studio_key_hint}"
        )
        active_bindings = self._active_studio_bindings()
        bindings = "  |  ".join(
            f"{gesture}: would {self.action_text(action)}"
            for gesture, action in active_bindings
        )
        mode_text = "Live (manual controls)" if mode == RoutingMode.LIVE else mode.value.title()
        if bindings:
            behavior_text = (
                "Gestures blocked pending longer readiness; Live manual controls active."
                if mode == RoutingMode.LIVE
                else "All typed manual and gesture requests simulate."
            )
            boundary_text = (
                f"Studio {mode_text} | Context: {context_id} | {behavior_text}\n"
                f"{bindings}"
            )
        else:
            manual_text = (
                "Live manual controls active; no gesture actions are active."
                if mode == RoutingMode.LIVE
                else "Manual-only stage; typed requests simulate and no gesture actions are active."
            )
            boundary_text = f"Studio {mode_text} | Context: {context_id} | {manual_text}"
        if self.readiness_check is not None and self.readiness_check.status == "running":
            expected = self.readiness_check.expected or "the prompted pose"
            boundary_text += f"\nReadiness running: perform {expected}. {self.readiness_check.completed}/6 complete."
        self.boundary.setText(boundary_text)
        missing = []
        if self.model is None:
            missing.append("starter/personal recogniser")
        revision = self._readiness_behavior_revision() if self.model is not None else ""
        if self.selected_profile_id and self.readiness_pass_revision == revision:
            missing.append("longer LIVE gesture readiness")
        else:
            missing.append("profile readiness verification" if self.selected_profile_id else "profile enrolment")
        if mode == RoutingMode.LIVE:
            self.studio_status.setText(
                "Manual LIVE controls available. Gesture control unavailable: " + ", ".join(missing) + "."
            )
        else:
            self.studio_status.setText(
                "Studio preview is running without: " + ", ".join(missing) + "."
            )
        self.mode_picker.setCurrentIndex(self.mode_picker.findData(mode.value))
        self.render_readiness_status()
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
        if self._profile_selector_change_blocked():
            raise ValueError("Wait for the profile selector to finish before changing settings")
        if self.model_loader is not None:
            raise ValueError("Wait for the dataset load to finish before changing settings")
        if mode is not None and mode not in (RoutingMode.PREVIEW, RoutingMode.REHEARSAL, RoutingMode.LIVE):
            raise ValueError("Studio supports Preview, Rehearsal or explicit Live manual mode only")
        if self.readiness_check is not None and not self._readiness_switching:
            if not self._cancel_readiness_check("Readiness cancelled before Studio settings changed."):
                return False
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
        authored_bindings = None
        previous_readiness_revision = self._readiness_behavior_revision() if self.model is not None else ""
        if (
            bindings is not None and new_bindings and not self._readiness_switching
            and new_context_id == self.workspace.id
        ):
            defaults = dict(zip(self.vocabulary.action_ids, STUDIO_ACTIONS, strict=True))
            drafted = dict(new_bindings)
            authored_bindings = {
                gesture: drafted.get(gesture, self.studio_authored_bindings.get(gesture, defaults[gesture]))
                for gesture in self.vocabulary.action_ids
            }
        if not self.pause():
            return False
        self.manual_context_id = new_context_id
        self.manual_session_id = str(uuid4())
        self.manual_mode = new_mode
        self.routing_manual_only = len(new_bindings) == 0
        if self.routing_manual_only:
            if self.worker is not None:
                self.worker.requestInterruption()
        routing_bindings = dict(new_bindings) or self._readiness_bindings()
        self.routing.configure(
            self.profile, self._model_version(), new_context_id, routing_bindings, new_mode,
        )
        self.state.setText(
            "Manual LIVE ready; gesture control remains unavailable."
            if new_mode == RoutingMode.LIVE
            else "Paused after Studio context change. Resume and show NEUTRAL."
        )
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
        if new_context_id != self.quick_actions_context_id:
            self.quick_actions_active = False
        if authored_bindings is not None:
            self.studio_authored_bindings = authored_bindings
            if previous_readiness_revision != self._readiness_behavior_revision():
                self._invalidate_readiness("simulation settings changed")
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
        if not self.studio or self.model_loader is not None or self._closing or self._profile_selector_change_blocked():
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
        self._invalidate_readiness("deck changed")
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
        if not self.studio or self.model_loader is not None or self._closing or self._profile_selector_change_blocked():
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
        if not self.studio or self.model_loader is not None or self._closing or self._profile_selector_change_blocked():
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
        self._invalidate_readiness_if_revision_changed("workspace changed")
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
        if self.model_loader is not None or self._closing or self._profile_selector_change_blocked():
            if self._profile_selector_change_blocked():
                self.notice.setText("Dataset not loaded: wait for the profile selector to finish.")
            return False
        if not self.pause():
            return False
        self.start_button.setEnabled(False)
        self.load_dataset_button.setEnabled(False)
        self.apply_bindings_button.setEnabled(False)
        self.apply_camera_button.setEnabled(False)
        self.load_progress.show()
        self.notice.setText("Loading and training locally. Camera control is paused; existing data is unchanged.")
        self.pending_profile_id = None
        self.model_loader = ModelLoadWorker(
            lambda: load_personal_model(path, *self.model_settings, studio=True),
            kind="dataset",
        )
        self.model_loader.start()
        return True

    def load_studio_profile(self, store: ProfileStore, profile_id: str):
        if not self.studio:
            raise ValueError("In-app profile loading requires Studio")
        if self.model_loader is not None or self._closing or self._profile_selector_change_blocked():
            if self._profile_selector_change_blocked():
                self.notice.setText("Profile not loaded: wait for the profile selector to finish.")
            return False
        if not self.pause():
            return False
        if profile_id in self._deleted_profile_ids:
            self.notice.setText("Profile not loaded: profile was deleted. Previous selection retained; control is paused.")
            return False
        self.start_button.setEnabled(False)
        self.load_dataset_button.setEnabled(False)
        self.apply_bindings_button.setEnabled(False)
        self.apply_camera_button.setEnabled(False)
        self.load_progress.show()
        self.pending_profile_id = profile_id
        self.notice.setText("Loading saved profile locally. Camera control is paused; existing data is unchanged.")
        self.model_loader = ModelLoadWorker(
            lambda: store.load(profile_id),
            kind="profile",
            profile_id=profile_id,
        )
        self.model_loader.start()
        return True

    def set_studio_camera(self, index):
        if not self.studio or self._closing:
            raise ValueError("Camera selection requires an open Studio window")
        validate_camera_index(index)
        if self._profile_selector_change_blocked():
            raise ValueError("Wait for the profile selector to finish before changing camera")
        if self.model_loader is not None:
            raise ValueError("Wait for the dataset load to finish before changing camera")
        if index == self.camera_index:
            return False
        if not self.configure_studio():
            return False
        self._invalidate_readiness("camera selection changed")
        self.camera_index = index
        self.camera_picker.setValue(index)
        self.start_button.setEnabled(self._can_start_studio_camera())
        self.detail.setText(f"Camera {index} selected. Wait for camera release, then Start and show NEUTRAL.")
        self.render_studio_status()
        self.log({"type": "camera_selection", "camera_index": index,
                  "timestamp": time.monotonic()})
        return True

    def use_studio_model(self, model, hand, profile, vocabulary, *, profile_display_name=None):
        """Install an already trained candidate atomically; capture resumes only on request."""
        if not self.studio or self.model_loader is not None or self._closing:
            raise ValueError("Studio must be open and idle before changing the model")
        if self._profile_selector_change_blocked():
            raise ValueError("Wait for the profile selector to finish before changing the model")
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
        self._invalidate_readiness("model or profile changed")
        was_manual_only = self.routing_manual_only
        was_quick_actions = self.quick_actions_active
        self.model, self.chosen_hand, self.profile, self.vocabulary = model, hand, profile, vocabulary
        self.studio_authored_bindings = dict(zip(self.vocabulary.action_ids, STUDIO_ACTIONS, strict=True))
        saved_profile = profile_display_name is not None
        self.selected_profile_id = profile if saved_profile else None
        self.selected_profile_name = profile_display_name or ""
        self.routing = candidate
        self.routing_manual_only = False
        self.manual_context_id = candidate.snapshot.context_id
        self.manual_session_id = str(uuid4())
        self.manual_mode = candidate.snapshot.mode
        self.received_first_frame = False
        self.preview.clear()
        self.preview.setText("Camera off\n\nProfile loaded; start and show NEUTRAL"
                             if saved_profile else
                             "Camera off\n\nDataset loaded; start and show NEUTRAL")
        self.prediction.setText("Prediction: awaiting new camera session")
        self.state.setText("Paused after model change. Start and show NEUTRAL.")
        self.detail.setText("Mappings reset to Preview. Check the actions before starting camera simulation.")
        self.notice.setText(
            f"Saved profile: {profile_display_name} | ID {profile} | {hand} hand | readiness unverified | local processing"
            if saved_profile else note
        )
        self.feedback.setText("Profile loaded. Gesture actions remain simulations; start explicitly."
                              if saved_profile else
                              "Dataset loaded. Gesture actions remain simulations; start explicitly.")
        self.start_button.setToolTip("Start camera simulation using the loaded personal dataset.")
        self.start_button.setEnabled(self._can_start_studio_camera())
        self._profile_selector_installing = True
        try:
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
            if hasattr(self, "quick_actions_widget"):
                self.quick_actions_widget.set_gesture_ids(tuple(self.vocabulary.action_ids))
            if was_quick_actions:
                self.use_quick_actions_context()
        finally:
            self._profile_selector_installing = False
        self.render_studio_status()
        self.log({"type": "studio_profile" if saved_profile else "studio_dataset",
                  "profile": profile, "model_version": model.model_version,
                  "session": candidate.snapshot.session_id, "timestamp": time.monotonic()})
        self.sync_profile_selector()

    def use_studio_profile(self, candidate: LoadedProfile):
        record = candidate.record
        if record.profile_id in self._deleted_profile_ids:
            raise ValueError("Profile was deleted before it could be loaded")
        self.use_studio_model(
            candidate.model,
            record.selected_hand,
            record.profile_id,
            record.vocabulary,
            profile_display_name=record.display_name,
        )
        settings = record.settings
        self.model_settings = (settings.algorithm, settings.multiplier, settings.margin)
        self.sync_profile_selector(candidate)

    def sync_profile_selector(self, loaded: LoadedProfile | None = None) -> None:
        if not self.studio or not hasattr(self, "profile_selector"):
            return
        selector = self.profile_selector
        if loaded is not None:
            selector.loaded = loaded
            selector._current_label()
        elif self.selected_profile_id is None:
            selector.loaded = None
            selector._current_label()
            if self.model is not None:
                selector.current.setText("Ad-hoc dataset loaded in Studio; saved profiles unchanged.")
        else:
            if (
                selector.loaded is not None
                and selector.loaded.record.profile_id == self.selected_profile_id
                and self.model is selector.loaded.model
            ):
                selector._current_label()
            else:
                selector.loaded = None
                selector.current.setText(
                    f"Loaded: {self.selected_profile_name or self.selected_profile_id} · {self.chosen_hand} hand"
                )
        selector.refresh()
        selector._controls()

    def rename_studio_profile(self, record) -> None:
        if self.selected_profile_id != record.profile_id:
            self.sync_profile_selector()
            return
        self.selected_profile_name = record.display_name
        self.notice.setText("Profile renamed. Active model and readiness state were not changed.")
        self.render_studio_status()
        self.sync_profile_selector()

    def set_profile_selector_busy(self, busy: bool) -> None:
        if not self.studio:
            return
        self.load_dataset_button.setEnabled(not busy and self.model_loader is None and not self._closing)
        self.apply_bindings_button.setEnabled(not busy and self.model_loader is None and not self._closing)
        self.apply_camera_button.setEnabled(not busy and self.model_loader is None and not self._closing)
        self.start_button.setEnabled(False if busy else self._can_start_studio_camera())

    def request_profile_preview_start(self, selection) -> None:
        if not self.studio or self._closing:
            return
        if self.model_loader is not None or self.worker is not None:
            self.notice.setText("Preview not started: wait for the current load or camera release.")
            return
        if self.routing is None or self.routing_manual_only or self.model is None:
            self.notice.setText("Preview not started: load the selected profile first.")
            return
        snapshot = self.routing.snapshot
        if (
            selection.profile_id != self.selected_profile_id
            or selection.profile_id != self.profile
            or selection.model_version != self._model_version()
            or snapshot.mode != RoutingMode.PREVIEW
        ):
            self.notice.setText("Preview not started: selected profile, model, or mode no longer matches.")
            return
        if self._profile_selector_busy() or self._enrolment_blocks_recognition():
            self.notice.setText("Preview not started: finish profile or enrolment work first.")
            return
        self.raise_()
        self.activateWindow()
        self.start_camera()

    def _clear_studio_model_to_manual(
        self, *, context_id: str, mode: RoutingMode, bindings: Mapping[str, Action],
    ) -> None:
        preserved_bindings = dict(bindings) or dict(zip(self.vocabulary.action_ids, STUDIO_ACTIONS, strict=True))
        self.model = None
        self.profile = "pilot"
        self.selected_profile_id = None
        self.selected_profile_name = ""
        self.routing = RoutingSession(
            "pilot", "unversioned", context_id,
            preserved_bindings, mode,
        )
        self.routing_manual_only = True
        self.manual_context_id = context_id
        self.manual_session_id = str(uuid4())
        self.manual_mode = mode
        self.received_first_frame = False
        self.preview.clear()
        self.prediction.setText("Prediction: awaiting new camera session")
        self.start_button.setEnabled(False)
        self.render_studio_status()

    def use_studio_guest(self) -> bool:
        """Unload the active Studio model/profile and keep manual-only project state."""
        if not self.studio or self._closing:
            return False
        if self._profile_selector_change_blocked():
            self.notice.setText("Guest mode not changed: wait for the profile selector to finish.")
            return False
        if self.model_loader is not None:
            self.notice.setText("Guest mode not changed: wait for the current model/profile load to finish.")
            return False
        if self.routing is None:
            return False
        context_id = self.manual_context_id if self.routing_manual_only else self.routing.snapshot.context_id
        mode = self.manual_mode if self.routing_manual_only else self.routing.snapshot.mode
        bindings = {} if self.routing_manual_only else dict(self.routing.snapshot.bindings)
        previous_profile = self.selected_profile_id or self.profile
        if not self.pause():
            self.notice.setText("Guest mode not changed: save the current trace or enrolment trial first.")
            return False
        self._invalidate_readiness("Guest mode selected")
        self._clear_studio_model_to_manual(
            context_id=context_id,
            mode=mode,
            bindings=bindings,
        )
        self.preview.setText("Camera off\n\nGuest mode active; load a profile or dataset to use gestures")
        self.state.setText("Paused in Guest mode. Manual controls remain available.")
        self.detail.setText("Guest mode unloads the active recogniser. Deck, workspace, runbook, summary and target settings remain available.")
        self.notice.setText("Guest mode active. Active model cleared; saved files were not deleted.")
        self.feedback.setText("Guest mode active. Manual viewer remains available.")
        assert self.routing is not None
        self.log({"type": "studio_guest", "profile": previous_profile,
                  "session": self.routing.snapshot.session_id, "timestamp": time.monotonic()})
        self.sync_profile_selector()
        return True

    def prepare_studio_profile_delete(self, profile_id: str) -> bool:
        if not self.studio or self._closing:
            return False
        if self.model_loader is not None and self.pending_profile_id != profile_id:
            return False
        if self.selected_profile_id == profile_id and not self.pause():
            return False
        return True

    def clear_studio_profile(self, profile_id: str) -> bool:
        if not self.prepare_studio_profile_delete(profile_id):
            return False
        active = self.selected_profile_id == profile_id
        if active:
            self._invalidate_readiness("active profile deleted")
        self._deleted_profile_ids.add(profile_id)
        if self.pending_profile_id == profile_id:
            self.pending_profile_id = None
        if not active:
            return True
        assert self.routing is not None
        context_id = self.manual_context_id if self.routing_manual_only else self.routing.snapshot.context_id
        mode = self.manual_mode if self.routing_manual_only else self.routing.snapshot.mode
        bindings = {} if self.routing_manual_only else dict(self.routing.snapshot.bindings)
        self._clear_studio_model_to_manual(
            context_id=context_id,
            mode=mode,
            bindings=bindings,
        )
        self.preview.setText("Camera off\n\nSaved profile deleted; load another profile or dataset")
        self.state.setText("Paused after profile deletion. Manual controls remain available.")
        self.detail.setText("Active profile was removed. Load another saved profile or personal dataset before camera simulation.")
        self.notice.setText("Saved profile deleted. Active model cleared; previous camera packets are invalid.")
        self.feedback.setText("Profile cleared. Manual viewer remains available.")
        assert self.routing is not None
        self.log({"type": "studio_profile_cleared", "profile": profile_id,
                  "session": self.routing.snapshot.session_id, "timestamp": time.monotonic()})
        self.sync_profile_selector()
        return True

    def poll_model_load(self):
        loader = self.model_loader
        if loader is None or loader.is_alive():
            return
        loader.join()
        self.model_loader = None
        if self._closing:
            return
        try:
            if loader.error:
                raise ValueError(loader.error)
            if loader.result is None:
                raise ValueError("Profile loading returned no model" if loader.kind == "profile"
                                 else "Dataset training returned no model")
            if loader.kind == "profile":
                if loader.profile_id != self.pending_profile_id or loader.profile_id in self._deleted_profile_ids:
                    self.notice.setText("Profile load ignored: selection changed or profile was deleted.")
                    return
                self.pending_profile_id = None
                self._profile_selector_installing = True
                try:
                    self.use_studio_profile(loader.result)
                finally:
                    self._profile_selector_installing = False
            else:
                self.pending_profile_id = None
                self.use_studio_model(*loader.result)
        except (ValueError, AttributeError, TypeError) as exc:
            if loader.kind == "profile":
                self.pending_profile_id = None
            self.notice.setText(
                f"{'Profile' if loader.kind == 'profile' else 'Dataset'} not loaded: "
                f"{exc}. Previous selection retained; control is paused."
            )
        finally:
            self.load_dataset_button.setEnabled(True)
            self.apply_bindings_button.setEnabled(True)
            self.apply_camera_button.setEnabled(True)
            self.load_progress.hide()
            self.start_button.setEnabled(self._can_start_studio_camera())
            self.render_readiness_status()

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
        if self.studio and self.routing is not None:
            mode = self.manual_mode if self.routing_manual_only else self.routing.snapshot.mode
            if mode == RoutingMode.LIVE:
                self.notice.setText("Live gesture launch is unavailable until longer personal readiness is completed.")
                self.detail.setText("Use manual controls in Live mode, or switch back to Preview/Rehearsal for camera simulation.")
                self.start_button.setEnabled(False)
                return
        if (
            self.model is None or self.worker is not None or self.model_loader is not None
            or self._closing or (self.studio and (
                self.routing_manual_only or self._enrolment_blocks_recognition() or self._profile_selector_busy()
            ))
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
        readiness_restored = True
        if self.studio and self.readiness_check is not None and not self._readiness_switching:
            readiness_restored = self._cancel_readiness_check("Readiness cancelled; camera paused.")
        enrolment_saved = self._stop_enrolment_for_pause()
        return readiness_restored and self._pause_capture_only() and enrolment_saved

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
        if self.studio:
            self.manual_viewer_action(Action(ActionType.NEXT))
            return
        old_topic = self.card_topic_text()
        moved = self.viewer.next_keyboard()
        self.render_card()
        self.feedback.setText(
            f"Now showing {self.card_topic_text()} (from {old_topic})."
            if moved else f"Still showing {old_topic}; the assignment deck does not wrap."
        )
        self.log({"type": "command", "source": "keyboard_or_mouse", "command": "NEXT",
                  "position": self.viewer.position, "timestamp": time.monotonic()})

    def manual_viewer_action(self, action):
        if not self.studio or action.kind not in {ActionType.NEXT, ActionType.PREVIOUS, ActionType.BOOKMARK}:
            return
        if not self.deck_available:
            self.feedback.setText("No deck is loaded for this workspace.")
            return
        outcome = self._dispatch_action(action, source="Manual viewer")
        if outcome is not None:
            self.log({"type": "manual_dispatch", "source": "manual_viewer", "command": action.kind.value,
                      "status": outcome.status, "position": self.viewer.position, "timestamp": time.monotonic()})

    def manual_runbook_action(self, action):
        if not self.studio or self.runbook is None:
            return
        if action.kind == ActionType.ADVANCE_STAGE:
            outcome = self._dispatch_action(action, source="Runbook")
            if outcome is not None:
                self.log({"type": "manual_dispatch", "source": "runbook", "command": action.kind.value,
                          "status": outcome.status, "stage": self.runbook.current_stage.id
                          if self.runbook.current_stage else None, "timestamp": time.monotonic()})
            return
        if action.kind in {ActionType.NEXT, ActionType.PREVIOUS, ActionType.BOOKMARK} and self.deck_available:
            self.manual_viewer_action(action)
            return
        outcome = self._dispatch_action(action, source="Runbook")
        if outcome is not None:
            self.log({"type": "manual_dispatch", "source": "runbook", "command": action.kind.value,
                      "status": outcome.status, "timestamp": time.monotonic()})

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
            self.runbook.paused = True
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
            self._start_pending_enrolment_if_ready()
            return
        if getattr(self.worker, "observation_only", False):
            self.poll_enrolment_capture()
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
            self._display_capture_frame(frame)
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
                    if not self._reserve_session_record():
                        self.pause()
                        return
                    snapshot = self.routing.snapshot
                    result = self.routing.route(event, time.monotonic())
                    self._sync_dispatcher_refs()
                    outcome = self.dispatcher.dispatch(result, snapshot, source="gesture")
                    if hasattr(self, "summary_widget"):
                        self.summary_widget.refresh()
                    action = result.simulated_action or result.action
                    if outcome.status == "simulated" and result.simulated_action is not None:
                        self.feedback.setText(
                            f"Studio simulation: {event.command} would {self.action_text(result.simulated_action)}."
                        )
                        self._record_readiness_result(event, result)
                        self.log({
                            "type": "studio_simulation", "source": "gesture",
                            "event_id": event.event_id, "command": event.command,
                            "action": result.simulated_action.kind.value,
                            "timestamp": time.monotonic(),
                        })
                    elif outcome.status == "launch_requested":
                        self.feedback.setText("LIVE gesture launch requested.")
                    elif outcome.status in {"applied", "unchanged"} and action is not None:
                        self._handle_dispatch_outcome(outcome, action, source="gesture")
                    elif outcome.status == "rejected":
                        self.feedback.setText(f"Studio routing rejected {event.command}: {outcome.reason}.")
                    elif outcome.status in {"failed", "duplicate"}:
                        self.feedback.setText(f"Studio routing {outcome.status}: {outcome.reason}.")
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
        worker = self.worker
        if worker is not None and worker.isFinished():
            error = worker.error
            worker.wait()
            self.worker = None
            self.finish_evaluation_trace()
            if self.studio and self.readiness_check is not None:
                self._cancel_readiness_check(error or "Readiness cancelled; camera stopped.")
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
            self.start_button.setEnabled(self._can_start_studio_camera())
            self._start_pending_enrolment_if_ready()

    def poll_enrolment_capture(self):
        worker = self.worker
        if worker is None:
            return
        now = time.monotonic()
        request_id = self.enrolment_request_id
        packet = worker.take_latest()
        if packet is not None and request_id:
            frame, observation = packet
            if not isinstance(observation, Observation):
                self._fail_enrolment_capture("Camera returned an invalid enrolment observation.")
                return
            if (
                not worker.isInterruptionRequested()
                and observation.session_id == self.enrolment_capture_session
                and observation.profile_id == self.enrolment_capture_profile
            ):
                self._display_capture_frame(frame)
                self.last_result_at = now
                self.enrolment_received_first_frame = True
                if not self.enrolment_capture_attached:
                    if not self.enrolment_widget.attach_capture(
                        request_id, self.enrolment_capture_session, self.enrolment_capture_profile,
                    ):
                        self._retire_enrolment_capture(request_id)
                        return
                    self.enrolment_capture_attached = True
                    self._scroll_enrolment_controls_into_view()
                self.enrolment_widget.receive_observation(observation)
        if request_id and not worker.isInterruptionRequested():
            elapsed = now - (self.last_result_at if self.enrolment_received_first_frame else self.enrolment_capture_started_at)
            limit = 2 if self.enrolment_received_first_frame else 20
            if elapsed > limit:
                self._fail_enrolment_capture("Enrolment camera stalled. Check the camera and retry collection.")
                return
        if worker.isFinished():
            error = worker.error
            worker.wait()
            self.worker = None
            if request_id == self.enrolment_request_id:
                if error:
                    self.enrolment_widget.capture_failed(request_id, error)
                elif not worker.isInterruptionRequested():
                    self.enrolment_widget.capture_failed(request_id, "Camera stopped")
                self._clear_enrolment_capture()
            self.preview.clear()
            self.preview.setText("Camera off\n\nStart explicitly to reconnect")
            self.state.setText(error or "Paused • camera released")
            self.start_button.setEnabled(self._can_start_studio_camera())
            self._start_pending_enrolment_if_ready()

    def changeEvent(self, event):
        if self.studio and event.type() == QEvent.Type.ActivationChange and not self.isActiveWindow():
            self.pause()
            self.state.setText("Paused after focus loss. Resume Studio before gestures.")
        super().changeEvent(event)

    def closeEvent(self, event):
        self._closing = True
        if not self.pause():
            self._closing = False
            event.ignore()
            return
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
        if self.studio and hasattr(self, "quick_actions_widget"):
            self.quick_actions_widget.close()
        if self.studio and hasattr(self, "profile_selector"):
            self.profile_selector.close()
        if self.studio and hasattr(self, "enrolment_widget"):
            self.enrolment_widget.close()
        self.timer.stop()
        event.accept()
