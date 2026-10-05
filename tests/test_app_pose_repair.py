"""Generated software host tests for selected-pose repair; no participant readiness claims."""

import os
from dataclasses import replace
from time import monotonic
from typing import Any, cast
from unittest.mock import Mock

import numpy as np
import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QEvent
from PySide6.QtWidgets import QApplication

from gestureforge.contracts import Observation, RoutingMode
from gestureforge.dataset import file_sha256, save_dataset
from gestureforge.enrolment import OFFSETS
from gestureforge.fixtures import synthetic_dataset
from gestureforge.pose_repair import PoseRepair
from gestureforge.profiles import LoadedProfile, ProfileSettings, ProfileStore
from gestureforge.vocabulary import GestureVocabulary

from test_app_enrolment import FakeCloseEvent, FakeWorker, capture_factory, frame, model


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


def observation(session="repair-capture", profile="SOFTWARE_TEST", frame_id=1, timestamp=0.1):
    points = np.arange(63, dtype=float).reshape(21, 3) / 100
    return Observation(session, profile, frame_id, timestamp, 1, "Right", points)


def generated_profile(tmp_path) -> tuple[ProfileStore, LoadedProfile]:
    generated = synthetic_dataset(trials_per_label_per_split=2, seed=304)
    vocabulary = GestureVocabulary(("G1", "G2", "G3"))
    mapping = dict(zip(generated.vocabulary.labels, vocabulary.labels, strict=True))
    records = tuple(
        replace(
            record,
            participant_id="SOFTWARE_TEST",
            hand="Right",
            provenance="human",
            intended_label=mapping[record.intended_label],
        )
        for record in generated.records
    )
    source = save_dataset(
        tmp_path / "generated",
        records,
        generated.features,
        {"chosen_hand": "Right", "warning": "GENERATED SOFTWARE TEST ONLY"},
        vocabulary=vocabulary,
    )
    assert source.manifest_path is not None
    store = ProfileStore(tmp_path / "profiles")
    original = store.create(
        "Generated repair source",
        source.manifest_path,
        "Right",
        consent=True,
        settings=ProfileSettings("knn", 1.5, 1.5),
    )
    return store, original


def fill_repair_form(window, source: LoadedProfile):
    widget = window.pose_repair_widget
    window.deck_tabs.setCurrentWidget(widget)
    widget.set_source(source.record)
    widget.repair_pose.setCurrentText("NEUTRAL")
    widget.diagnosis.setText("Reviewed generated diagnostic for neutral rejection")
    widget.setup.setText("GENERATED SOFTWARE TEST ONLY")
    widget.consent.setChecked(True)
    widget.diagnostic_reviewed.setChecked(True)
    return widget


def repair_candidate(tmp_path, original: LoadedProfile):
    repair = PoseRepair(original.record, "NEUTRAL", "Reviewed generated diagnostic")
    selected = tuple(r for r in repair.bundle.records if r.split == "train" and r.intended_label == "NEUTRAL")
    records = tuple(
        replace(r, session_id="repair-session", trial_id="repair-" + r.trial_id, feature_index=i)
        for i, r in enumerate(selected)
    )
    features = np.array([repair.bundle.features[r.feature_index] for r in selected], dtype=np.float32) + 0.02
    samples = save_dataset(
        tmp_path / "samples",
        records,
        features,
        {
            "chosen_hand": "Right",
            "collection_complete": True,
            "planned_trials": 2,
            "warning": "GENERATED SOFTWARE TEST ONLY",
        },
        vocabulary=original.record.vocabulary,
    )
    assert samples.manifest_path is not None
    return repair.build_candidate(samples.manifest_path, tmp_path / "candidate", reviewed=True)


def complete_repair_session(widget, monkeypatch, tmp_path, *, fail_save=False):
    import gestureforge.enrolment as enrolment_module

    session = widget.session
    assert session is not None
    current = [session.last_now + 1.0]
    widget.clock = lambda: current[0]
    real_save = enrolment_module.save_dataset

    def boom(*_args, **_kwargs):
        raise OSError("disk full")

    if fail_save:
        monkeypatch.setattr(enrolment_module, "save_dataset", boom)
    start = current[0]
    session.begin(start)
    for index, offset in enumerate(OFFSETS):
        at = start + 2.0 + offset + 0.01
        session.advance(at, observation(session.capture_session, session.capture_profile, index + 2, at))
    session.advance(start + 4.1)
    current[0] = start + 4.2
    if fail_save:
        monkeypatch.setattr(enrolment_module, "save_dataset", real_save)
    return tmp_path


def finish_profile_work(window, selector):
    deadline = monotonic() + 15
    while (selector.busy or window.model_loader is not None) and monotonic() < deadline:
        QApplication.processEvents()
        selector._poll()
        window.poll_model_load()
    assert not selector.busy, selector.status.text()
    assert window.model_loader is None, window.notice.text()


def test_repair_tab_binds_saved_profile_and_is_unavailable_for_guest_or_adhoc(tmp_path, qapp):
    from gestureforge.app import Window

    store, original = generated_profile(tmp_path)
    window = Window(studio=True, profile_store=store)
    try:
        labels = [window.deck_tabs.tabText(index) for index in range(window.deck_tabs.count())]
        assert "Repair pose" in labels

        window.use_studio_profile(original)
        assert window.pose_repair_widget.source == original.record

        assert window.use_studio_guest()
        assert window.pose_repair_widget.source is None

        window.use_studio_model(original.model, "Right", "ad-hoc", original.record.vocabulary)
        assert window.pose_repair_widget.source is None
        window.pose_repair_widget.consent.setChecked(True)
        window.pose_repair_widget.diagnostic_reviewed.setChecked(True)
        window.pose_repair_widget.request_collection()
        assert window.pose_repair_widget.pending_plan is None
        assert "existing saved profile" in window.pose_repair_widget.feedback.text()
    finally:
        window.close()


def test_repair_capture_receives_only_matching_observations_and_does_not_route_gestures(tmp_path, monkeypatch, qapp):
    import gestureforge.app as app_module
    from gestureforge.app import Window

    store, original = generated_profile(tmp_path)
    workers: list[FakeWorker] = []
    monkeypatch.setattr(app_module, "CaptureWorker", capture_factory(workers))
    window = Window(model=original.model, studio=True, studio_mode=RoutingMode.PREVIEW, profile_store=store)
    try:
        window.use_studio_profile(original)
        widget = fill_repair_form(window, original)
        widget.request_collection()
        capture = workers[0]
        assert capture.observation_only is True
        assert window.worker is capture
        assert widget.session is None

        capture.packets.append((frame(), observation("wrong-session", "SOFTWARE_TEST", 1, 0.1)))
        window.poll()
        assert widget.session is None

        matching = observation(capture.args[5], capture.args[6], 2, 0.2)
        capture.packets.append((frame(), matching))
        routing_process = Mock()
        controller_process = Mock()
        monkeypatch.setattr(window.routing, "process", routing_process)
        monkeypatch.setattr(window.controller, "process", controller_process)
        trace = Mock()
        window.evaluation_trace = cast(Any, trace)
        window.poll()

        assert widget.session is not None
        assert widget.session.capture_session == matching.session_id
        assert window.enrolment_widget.session is None
        routing_process.assert_not_called()
        controller_process.assert_not_called()
        trace.append.assert_not_called()
    finally:
        window.evaluation_trace = None
        window.close()


def test_leaving_repair_tab_cancels_pending_collection(tmp_path, monkeypatch, qapp):
    import gestureforge.app as app_module
    from gestureforge.app import Window

    store, original = generated_profile(tmp_path)
    workers: list[FakeWorker] = []
    monkeypatch.setattr(app_module, "CaptureWorker", capture_factory(workers))
    window = Window(model=original.model, studio=True, profile_store=store)
    old_worker = FakeWorker(observation_only=False)
    window.worker = old_worker
    try:
        window.use_studio_profile(original)
        widget = fill_repair_form(window, original)
        widget.request_collection()
        assert widget.request_id
        assert widget.pending_plan is not None

        window.deck_tabs.setCurrentWidget(window.card_frame)

        assert widget.pending_plan is None
        assert widget.request_id == ""
        assert workers == []
    finally:
        window.worker = None
        window.close()


def test_regular_enrolment_request_cannot_steal_queued_repair_capture(tmp_path, monkeypatch, qapp):
    import gestureforge.app as app_module
    from gestureforge.app import Window

    store, original = generated_profile(tmp_path)
    workers: list[FakeWorker] = []
    monkeypatch.setattr(app_module, "CaptureWorker", capture_factory(workers))
    window = Window(model=original.model, studio=True, profile_store=store)
    old_worker = FakeWorker(observation_only=False)
    window.worker = old_worker
    try:
        window.use_studio_profile(original)
        repair = fill_repair_form(window, original)
        repair.request_collection()
        repair_request = repair.request_id
        repair_plan = repair.pending_plan
        assert repair_request and repair_plan is not None

        enrolment = window.enrolment_widget
        enrolment.participant.setText("SOFTWARE_TEST")
        enrolment.setup.setText("GENERATED SOFTWARE TEST ONLY")
        enrolment.consent.setChecked(True)
        enrolment.request_collection()

        assert enrolment.pending_plan is None
        assert "other collection" in enrolment.feedback.text()
        assert repair.request_id == repair_request
        assert repair.pending_plan is repair_plan
        assert workers == []

        old_worker.finished = True
        window.poll()
        assert len(workers) == 1
        capture = workers[0]
        capture.packets.append((frame(), observation(capture.args[5], capture.args[6], 1, 0.1)))
        window.poll()
        assert repair.session is not None
        assert enrolment.session is None
    finally:
        window.worker = None
        window.close()


def test_focus_loss_cancels_active_repair_capture(tmp_path, monkeypatch, qapp):
    import gestureforge.app as app_module
    from gestureforge.app import Window

    store, original = generated_profile(tmp_path)
    workers: list[FakeWorker] = []
    monkeypatch.setattr(app_module, "CaptureWorker", capture_factory(workers))
    window = Window(model=original.model, studio=True, profile_store=store)
    try:
        window.use_studio_profile(original)
        widget = fill_repair_form(window, original)
        widget.request_collection()
        capture = workers[0]
        assert widget.request_id

        window.changeEvent(QEvent(QEvent.Type.ActivationChange))

        assert capture.interrupted
        repair_widget = window.pose_repair_widget
        assert repair_widget.session is None
        assert repair_widget.request_id == ""
        assert "Paused after focus loss" in window.state.text()
    finally:
        window.close()


def test_repair_save_error_blocks_close_model_change_and_returns_to_repair_tab(tmp_path, monkeypatch, qapp):
    import gestureforge.app as app_module
    from gestureforge.app import Window

    store, original = generated_profile(tmp_path)
    workers: list[FakeWorker] = []
    monkeypatch.setattr(app_module, "CaptureWorker", capture_factory(workers))
    window = Window(model=original.model, studio=True, profile_store=store)
    try:
        window.use_studio_profile(original)
        widget = fill_repair_form(window, original)
        widget.request_collection()
        capture = workers[0]
        capture.packets.append((frame(), observation(capture.args[5], capture.args[6], 1, 0.1)))
        window.poll()

        complete_repair_session(widget, monkeypatch, tmp_path, fail_save=True)
        widget.refresh()
        assert widget.session is not None and widget.session.state == "save_error"
        assert not window.pause()
        assert capture.interrupted
        assert window.deck_tabs.currentWidget() is widget

        with pytest.raises(ValueError, match="Save the current evaluation trace|Studio must be open"):
            window.use_studio_model(model(), "Right", "P02", GestureVocabulary(("G1", "G2", "G3")))
        close = FakeCloseEvent()
        window.closeEvent(close)
        assert close.ignored
        assert window.model is original.model
    finally:
        repair_widget = window.pose_repair_widget
        if repair_widget.session is not None:
            repair_widget.session.state = "cancelled"
        window.close()


def test_repair_candidate_is_offered_for_profile_review_without_training_or_loading(tmp_path, qapp):
    from gestureforge.app import Window

    store, original = generated_profile(tmp_path)
    window = Window(model=original.model, studio=True, profile_store=store)
    try:
        window.use_studio_profile(original)
        source_hash = file_sha256(original.record.dataset_path)
        candidate = repair_candidate(tmp_path, original)

        window.offer_pose_repair_candidate(candidate)

        assert window.deck_tabs.currentWidget() is window.profile_selector
        assert window.profile_selector._repair_candidate == candidate
        assert window.profile_selector._future is None
        assert window.selected_profile_id == original.record.profile_id
        assert store.list_ids() == (original.record.profile_id,)
        assert file_sha256(original.record.dataset_path) == source_hash
    finally:
        window.close()


def test_explicit_repair_profile_creation_preserves_original_and_expires_readiness(tmp_path, monkeypatch, qapp):
    from gestureforge.app import LiveGrant, Window

    store, original = generated_profile(tmp_path)
    window = Window(model=original.model, studio=True, profile_store=store)

    def seed_live_grants():
        grant = LiveGrant("generated-attempt", 0, "stale-revision", frozenset())
        window._personal_live_grant = grant
        window._standard_live_grant = grant

    try:
        window.use_studio_profile(original)
        source_hash = file_sha256(original.record.dataset_path)
        candidate = repair_candidate(tmp_path, original)
        dispatch = Mock(wraps=window.dispatcher.dispatch)
        monkeypatch.setattr(window.dispatcher, "dispatch", dispatch)

        seed_live_grants()
        window.offer_pose_repair_candidate(candidate)
        window.profile_selector.consent.setChecked(True)
        window.profile_selector.create_button.click()
        finish_profile_work(window, window.profile_selector)

        candidate_profile_id = window.selected_profile_id
        assert candidate_profile_id is not None and candidate_profile_id != original.record.profile_id
        assert len(store.list_ids()) == 2
        assert store.load(original.record.profile_id).record == original.record
        assert file_sha256(original.record.dataset_path) == source_hash
        assert window.profile_selector.loaded is not None
        assert window.profile_selector.loaded.selection.readiness_revision == ""
        assert window.profile_selector.loaded.selection.readiness_reason
        assert window.routing is not None
        assert window.routing.snapshot.mode == RoutingMode.PREVIEW
        assert window.routing.state == "PAUSED"
        assert window.worker is None
        assert window._personal_live_grant is None
        assert window._standard_live_grant is None

        seed_live_grants()
        assert window.load_studio_profile(store, original.record.profile_id)
        finish_profile_work(window, window.profile_selector)
        assert window.selected_profile_id == original.record.profile_id
        assert window.profile_selector.loaded is not None
        assert window.profile_selector.loaded.record == original.record
        assert window.routing is not None
        assert window.routing.snapshot.mode == RoutingMode.PREVIEW
        assert window.routing.state == "PAUSED"
        assert window.worker is None
        assert window._personal_live_grant is None
        assert window._standard_live_grant is None
        dispatch.assert_not_called()
    finally:
        window.close()
