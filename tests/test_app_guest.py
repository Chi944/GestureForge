import os
from dataclasses import replace
import json
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import Mock

import numpy as np
import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from gestureforge.contracts import Action, ActionType, Observation, Prediction
from gestureforge.dataset import save_dataset
from gestureforge.fixtures import synthetic_dataset
from gestureforge.profiles import ProfileStore
from gestureforge.vocabulary import LEGACY_VOCABULARY


@pytest.fixture(autouse=True)
def isolated_app_state(tmp_path, monkeypatch):
    import gestureforge.app as app_module

    monkeypatch.setattr(app_module, "DEFAULT_STUDIO_STATE_FOLDER", tmp_path / "studio")
    monkeypatch.setattr(app_module, "DEFAULT_ENROLMENT_FOLDER", tmp_path / "enrolment")
    monkeypatch.setattr(app_module.Window, "log", lambda self, record: None)


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


def candidate_model(vocabulary=LEGACY_VOCABULARY, *, version="guest-model-v1"):
    return SimpleNamespace(
        predict=lambda _: (vocabulary.action_ids[0], True, ""),
        train_labels=vocabulary.labels,
        model_version=version,
        config=SimpleNamespace(algorithm="knn", multiplier=2.0, margin=1.5),
    )


def frame():
    return np.zeros((4, 4, 3), dtype=np.uint8)


def observation(session: str, profile: str, frame_id: int = 1, timestamp: float = 0.1):
    points = np.arange(63, dtype=float).reshape(21, 3) / 100
    return Observation(session, profile, frame_id, timestamp, 1, "Right", points)


class FakeWorker:
    def __init__(self, *args, observation_only=False, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.observation_only = observation_only
        self.packets = []
        self.error = ""
        self.finished = False
        self.interrupted = False
        self.start = Mock()

    def take_latest(self):
        if self.packets:
            return self.packets.pop(0)
        return None

    def isFinished(self):
        return self.finished

    def wait(self, timeout=None):
        return True

    def requestInterruption(self):
        self.interrupted = True

    def isInterruptionRequested(self):
        return self.interrupted


def capture_factory(workers):
    def factory(*args, **kwargs):
        worker = FakeWorker(*args, **kwargs)
        workers.append(worker)
        return worker
    return factory


def fill_enrolment_form(window, participant="GUESTTEST"):
    widget = window.enrolment_widget
    window.deck_tabs.setCurrentWidget(widget)
    widget.participant.setText(participant)
    widget.setup.setText("Synthetic guest-switch host regression")
    widget.consent.setChecked(True)
    return widget


def generated_profile_store(tmp_path):
    bundle = synthetic_dataset(trials_per_label_per_split=2, seed=304)
    records = tuple(
        replace(record, participant_id="TEST_PERSON", hand="Right", provenance="human")
        for record in bundle.records
    )
    generated = save_dataset(
        tmp_path / "generated-profile-dataset",
        records,
        bundle.features,
        {"chosen_hand": "Right", "warning": "GENERATED SOFTWARE TEST ONLY"},
    )
    assert generated.manifest_path is not None
    store = ProfileStore(tmp_path / "profiles")
    first = store.create("Generated guest profile A", generated.manifest_path, "Right", consent=True)
    second = store.create("Generated guest profile B", generated.manifest_path, "Right", consent=True)
    assert first.record.profile_id != second.record.profile_id
    return store, generated, first, second


def stored_bytes(store: ProfileStore, profile_id: str, manifest_path):
    profile_path = store.root / f"{profile_id}.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    sidecar = manifest_path.with_name(str(manifest["feature_file"]))
    return profile_path.read_bytes(), manifest_path.read_bytes(), sidecar.read_bytes()


def test_guest_switch_preserves_real_profile_files_and_background_reload(tmp_path, qapp):
    from gestureforge.app import Window

    store, generated, first, second = generated_profile_store(tmp_path)
    assert generated.manifest_path is not None
    before_first = stored_bytes(store, first.record.profile_id, generated.manifest_path)
    before_second = stored_bytes(store, second.record.profile_id, generated.manifest_path)
    window = Window(studio=True)
    try:
        window.use_studio_profile(first)

        assert window.use_studio_guest()

        assert window.model is None
        assert first.record.profile_id not in window._deleted_profile_ids
        assert second.record.profile_id not in window._deleted_profile_ids
        assert stored_bytes(store, first.record.profile_id, generated.manifest_path) == before_first
        assert stored_bytes(store, second.record.profile_id, generated.manifest_path) == before_second

        assert window.load_studio_profile(store, first.record.profile_id)
        assert window.model_loader is not None
        window.model_loader.join(5)
        window.poll_model_load()

        assert window.selected_profile_id == first.record.profile_id
        assert window.selected_profile_name == first.record.display_name
        assert window.model is not None
        assert stored_bytes(store, first.record.profile_id, generated.manifest_path) == before_first
        assert stored_bytes(store, second.record.profile_id, generated.manifest_path) == before_second
        assert store.list_ids() == tuple(sorted((first.record.profile_id, second.record.profile_id)))
    finally:
        if window.model_loader is not None:
            window.model_loader.join(5)
        window.close()


def test_guest_switch_unloads_saved_profile_without_deleting_and_discards_stale_packets(monkeypatch, qapp):
    import gestureforge.app as app_module
    from gestureforge.app import Window

    workers: list[FakeWorker] = []
    monkeypatch.setattr(app_module, "CaptureWorker", capture_factory(workers))
    profile_id = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
    loaded_model = candidate_model()
    window = Window(studio=True)
    try:
        window.use_studio_model(
            loaded_model, "Right", profile_id, LEGACY_VOCABULARY,
            profile_display_name="Desk profile",
        )
        window.manual_viewer_action(Action(ActionType.BOOKMARK))
        window.manual_viewer_action(Action(ActionType.NEXT))
        assert window.start_camera() is None
        assert window.routing is not None
        old_snapshot = window.routing.snapshot
        worker = workers[0]
        before_position = window.viewer.position
        before_bookmarks = tuple(card.id for card in window.viewer.bookmarks)
        before_workspace = window.workspace
        before_summary_count = len(window.session_summary.outcomes)

        assert window.use_studio_guest()

        assert window.model is None
        assert window.selected_profile_id is None
        assert window.selected_profile_name == ""
        assert window.routing_manual_only
        assert profile_id not in window._deleted_profile_ids
        assert window.viewer.position == before_position
        assert tuple(card.id for card in window.viewer.bookmarks) == before_bookmarks
        assert window.workspace is before_workspace
        assert len(window.session_summary.outcomes) == before_summary_count
        assert "Guest/manual" in window.camera_status.text()
        assert not window.start_button.isEnabled()
        assert worker.interrupted

        stale = Prediction(
            old_snapshot.session_id, old_snapshot.profile_id, 1, 0.2,
            LEGACY_VOCABULARY.action_ids[0], True, old_snapshot.model_version,
        )
        worker.packets.append((frame(), stale))
        window.poll()
        assert window.viewer.position == before_position
        assert len(window.session_summary.outcomes) == before_summary_count

        worker.finished = True
        window.poll()
        assert not window.start_button.isEnabled()

        replacement = candidate_model(version="guest-model-v2")
        window.use_studio_model(
            replacement, "Right", profile_id, LEGACY_VOCABULARY,
            profile_display_name="Desk profile",
        )
        assert window.selected_profile_id == profile_id
        assert window.model is replacement
    finally:
        window.close()


def test_guest_switch_unloads_ad_hoc_dataset(qapp):
    from gestureforge.app import Window

    dataset_model = candidate_model()
    window = Window(model=dataset_model, studio=True, profile="P02")
    try:
        assert window.selected_profile_id is None
        assert window.model is dataset_model

        assert window.use_studio_guest()

        assert window.model is None
        assert window.profile == "pilot"
        assert window.selected_profile_id is None
        assert window.routing_manual_only
        assert "saved files were not deleted" in window.notice.text()
        assert not window.start_button.isEnabled()
    finally:
        window.close()


@pytest.mark.parametrize("failure", ["trace", "enrolment"])
def test_guest_switch_save_failures_retain_previous_model(failure, tmp_path, monkeypatch, qapp):
    import gestureforge.app as app_module
    from gestureforge.app import Window

    workers: list[FakeWorker] = []
    monkeypatch.setattr(app_module, "CaptureWorker", capture_factory(workers))
    active_model = candidate_model()
    window = Window(model=active_model, studio=True, profile="P02")
    try:
        if failure == "trace":
            trace = SimpleNamespace(frame_count=1, save=Mock(side_effect=OSError("disk full")))
            window.evaluation_trace = cast(Any, trace)
            window.trace_path = tmp_path / "trace.json"
        else:
            widget = fill_enrolment_form(window)
            widget.request_collection()
            capture = workers[0]
            capture.packets.append((
                frame(), observation(window.enrolment_capture_session, window.enrolment_capture_profile),
            ))
            window.poll()
            assert widget.session is not None
            widget.session.state = "save_error"

        assert not window.use_studio_guest()

        assert window.model is active_model
        assert window.profile == "P02"
        assert not window.routing_manual_only
        assert "Guest mode not changed" in window.notice.text() or "Retry saving" in window.notice.text()
    finally:
        window.evaluation_trace = None
        if hasattr(window, "enrolment_widget") and window.enrolment_widget.session is not None:
            window.enrolment_widget.session.state = "cancelled"
        window.close()


def test_guest_switch_refuses_busy_and_closing_without_mutation(qapp):
    from gestureforge.app import Window

    active_model = candidate_model()
    window = Window(model=active_model, studio=True, profile="P02")
    try:
        window.model_loader = object()
        assert not window.use_studio_guest()
        assert window.model is active_model
        assert not window.routing_manual_only
        assert "wait for the current model/profile load" in window.notice.text()

        window.model_loader = None
        window._closing = True
        assert not window.use_studio_guest()
        assert window.model is active_model
        assert not window.routing_manual_only
        window._closing = False
    finally:
        window.model_loader = None
        window._closing = False
        window.close()
