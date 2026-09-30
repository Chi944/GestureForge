import os
import json
import subprocess
import sys
import time
from dataclasses import replace
from hashlib import sha256
from types import SimpleNamespace
from unittest.mock import Mock

import numpy as np
import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QEvent
from PySide6.QtWidgets import QApplication

from gestureforge.app import Window
from gestureforge.contracts import Action, ActionType, Prediction, RoutingMode
from gestureforge.vocabulary import GestureVocabulary


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance() or QApplication([])
    yield app


class FakeWorker:
    def __init__(self, packets=(), wait_result=True):
        self.packets = list(packets)
        self.error = ""
        self.interrupted = False
        self.finished = False
        self.wait_result = wait_result

    def take_latest(self):
        if self.packets:
            return self.packets.pop(0)
        return None

    def isFinished(self):
        return self.finished

    def wait(self, timeout=None):
        return self.wait_result

    def requestInterruption(self):
        self.interrupted = True

    def isInterruptionRequested(self):
        return self.interrupted


class FakeCloseEvent:
    def __init__(self):
        self.accepted = False
        self.ignored = False

    def accept(self):
        self.accepted = True

    def ignore(self):
        self.ignored = True


def _frame():
    return np.zeros((8, 8, 3), dtype=np.uint8)


def _prediction(
    window: Window,
    frame_id: int,
    timestamp: float,
    label: str,
    *,
    accepted: bool = True,
    reason: str = "",
) -> Prediction:
    return Prediction(
        window.controller.session_id,
        "pilot",
        frame_id,
        timestamp,
        label,
        accepted,
        rejection_reason=reason,
    )


def _disable_logging(window: Window) -> None:
    window._log_failed = True


def _studio_prediction(
    window: Window,
    frame_id: int,
    timestamp: float,
    label: str,
    *,
    accepted: bool = True,
) -> Prediction:
    assert window.routing is not None
    snapshot = window.routing.snapshot
    return Prediction(
        snapshot.session_id,
        snapshot.profile_id,
        frame_id,
        timestamp,
        label,
        accepted,
        model_version=snapshot.model_version,
    )


def test_window_starts_keyboard_only_and_deck_controls_work(qapp) -> None:
    window = Window(model=None, data_note="keyboard only")
    _disable_logging(window)

    try:
        assert window.start_button.isEnabled() is False
        assert "no gesture dataset loaded" in window.prediction.text()
        assert "--dataset" in window.detail.text()
        assert window.viewer.position == 0
        assert window.card_badge.text() == "1"
        assert "GESTUREFORGE ASSIGNMENT DEMO" in window.deck_label.text()
        assert "Card 1 of 10" in window.position.text()
        assert "card-01" not in window.position.text()
        assert window.deck_progress.value() == 1
        assert window.card_topic.text() == "Topic: Start"
        assert window.card_title.text() == "Start"

        window.next_card()
        assert window.viewer.position == 1
        assert window.card_badge.text() == "2"
        assert "Card 2 of 10" in window.position.text()
        assert window.deck_progress.value() == 2
        assert window.card_topic.text() == "Topic: Personal Setup"
        assert window.card_title.text() == "Personal Setup"
        assert "Now showing Personal Setup (from Start)." in window.feedback.text()
        assert window.card_badge.styleSheet()
        assert window.card_frame.styleSheet()

        window.restart_deck()
        assert window.viewer.position == 0
        assert window.card_badge.text() == "1"
        assert "Card 1 of 10" in window.position.text()
        assert window.deck_progress.value() == 1
    finally:
        window.close()


def test_studio_no_dataset_starts_as_simulated_shell(qapp) -> None:
    window = Window(model=None, data_note="studio no data", studio=True)
    _disable_logging(window)

    try:
        assert window.start_button.isEnabled() is False
        assert "starter/personal recogniser" in window.studio_status.text()
        assert "Studio Preview" in window.boundary.text()
        assert "NEXT: would show next card" in window.boundary.text()
        assert "PREVIOUS: would show previous card" in window.boundary.text()
        assert "BOOKMARK: would bookmark this card" in window.boundary.text()
        assert window.viewer.position == 0
    finally:
        window.close()


def test_studio_preview_simulates_without_moving_deck(monkeypatch, qapp) -> None:
    import gestureforge.app as app_module

    window = Window(model=object(), feature_function=lambda observation, hand: np.zeros(60), studio=True)
    _disable_logging(window)
    current = [100.0]
    monkeypatch.setattr(app_module.time, "monotonic", lambda: current[0])
    assert window.routing is not None
    window.routing.resume()
    packets = []
    for frame_id, timestamp, label in [
        (1, 100.00, "NEUTRAL"),
        (2, 100.15, "NEUTRAL"),
        (3, 100.31, "NEUTRAL"),
        (4, 100.45, "NEXT"),
        (5, 100.62, "NEXT"),
        (6, 100.78, "NEXT"),
        (7, 100.91, "NEXT"),
    ]:
        packets.append((_frame(), _studio_prediction(window, frame_id, timestamp, label)))
    window.worker = FakeWorker(packets)

    try:
        for _, prediction in list(packets):
            current[0] = prediction.timestamp
            window.poll()

        assert window.viewer.position == 0
        assert "Studio simulation: NEXT would show next card." in window.feedback.text()
        assert "Card 1 of 10" in window.position.text()
    finally:
        window.close()


def test_studio_context_change_drops_old_identity(monkeypatch, qapp) -> None:
    import gestureforge.app as app_module

    window = Window(model=object(), feature_function=lambda observation, hand: np.zeros(60), studio=True)
    _disable_logging(window)
    current = [200.0]
    monkeypatch.setattr(app_module.time, "monotonic", lambda: current[0])
    assert window.routing is not None
    old_snapshot = window.routing.resume()
    stale = Prediction(
        old_snapshot.session_id,
        old_snapshot.profile_id,
        1,
        200.0,
        "NEXT",
        True,
        model_version=old_snapshot.model_version,
    )
    worker = FakeWorker([(_frame(), stale)])
    window.worker = worker

    try:
        window.configure_studio(context_id="stage-2", mode=RoutingMode.REHEARSAL)
        current[0] = 200.0
        window.poll()

        assert worker.interrupted is True
        assert window.viewer.position == 0
        assert "Studio simulation" not in window.feedback.text()
        assert window.routing.snapshot.context_id == "stage-2"
        assert window.routing.snapshot.mode == RoutingMode.REHEARSAL
        assert window.prediction.text() == "Prediction: awaiting new camera session"
    finally:
        window.close()


def test_studio_focus_loss_pauses_and_invalidates_worker(monkeypatch, qapp) -> None:
    window = Window(model=object(), feature_function=lambda observation, hand: np.zeros(60), studio=True)
    _disable_logging(window)
    assert window.routing is not None
    window.routing.resume()
    worker = FakeWorker()
    window.worker = worker
    monkeypatch.setattr(window, "isActiveWindow", lambda: False)

    try:
        window.changeEvent(QEvent(QEvent.Type.ActivationChange))

        assert worker.interrupted is True
        assert window.routing.state == "PAUSED"
        assert "focus loss" in window.state.text()
    finally:
        window.close()


def test_window_poll_executes_next_only_after_neutral_and_hold(monkeypatch, qapp) -> None:
    import gestureforge.app as app_module

    window = Window(model=object(), feature_function=lambda observation, hand: np.zeros(60))
    _disable_logging(window)
    current = [100.0]
    monkeypatch.setattr(app_module.time, "monotonic", lambda: current[0])
    window.controller.resume("live-session")

    packets = []
    for frame_id, timestamp, label, accepted, reason in [
        (1, 100.00, "NEUTRAL", True, ""),
        (2, 100.15, "NEUTRAL", True, ""),
        (3, 100.31, "NEUTRAL", True, ""),
        (4, 100.45, "PREVIOUS", True, ""),
        (5, 100.55, "BOOKMARK", True, ""),
        (6, 100.60, "NEXT", False, "margin_rejection"),
        (7, 100.65, "NEXT", True, ""),
        (8, 100.83, "NEXT", True, ""),
        (9, 101.00, "NEXT", True, ""),
        (10, 101.06, "NEXT", True, ""),
    ]:
        packets.append(
            (_frame(), _prediction(window, frame_id, timestamp, label, accepted=accepted, reason=reason))
        )
    window.worker = FakeWorker(packets)

    try:
        for _, prediction in list(packets):
            current[0] = prediction.timestamp
            window.poll()

        assert window.viewer.position == 1
        assert "NEXT accepted" in window.feedback.text()
        assert "Personal Setup" in window.feedback.text()
        assert "Start" in window.feedback.text()
        assert window.card_badge.text() == "2"
        assert "Card 2 of 10" in window.position.text()
    finally:
        window.close()


def test_window_pause_blocks_pending_worker_prediction_from_moving_deck(qapp) -> None:
    window = Window(model=object(), feature_function=lambda observation, hand: np.zeros(60))
    _disable_logging(window)
    window.controller.resume("live-session")
    worker = FakeWorker([(_frame(), _prediction(window, 1, time.monotonic(), "NEXT"))])
    window.worker = worker

    try:
        window.pause()
        window.poll()

        assert worker.interrupted is True
        assert window.viewer.position == 0
        assert "Card 1 of 10" in window.position.text()
    finally:
        window.close()


def test_window_shows_rejection_guidance_without_moving_deck(monkeypatch, qapp) -> None:
    import gestureforge.app as app_module

    window = Window(model=object(), feature_function=lambda observation, hand: np.zeros(60))
    _disable_logging(window)
    current = [100.0]
    monkeypatch.setattr(app_module.time, "monotonic", lambda: current[0])
    window.controller.resume("live-session")
    arm_session = window.controller.session_id
    for frame_id, timestamp in ((1, 100.00), (2, 100.15), (3, 100.31)):
        window.controller.process(
            Prediction(arm_session, "pilot", frame_id, timestamp, "NEUTRAL", True),
            timestamp,
        )
    window.worker = FakeWorker([
        (_frame(), _prediction(
            window,
            4,
            100.45,
            "BOOKMARK",
            accepted=False,
            reason="margin_rejection",
        )),
        *[
            (
                _frame(),
                _prediction(
                    window,
                    frame_id,
                    timestamp,
                    "BOOKMARK",
                    accepted=False,
                    reason="margin_rejection",
                ),
            )
            for frame_id, timestamp in ((5, 100.63), (6, 100.81), (7, 100.99))
        ],
    ])

    try:
        current[0] = 100.45
        window.poll()

        assert window.viewer.position == 0
        assert window.prediction.text() == "Prediction: Unrecognised"
        assert "Pose is ambiguous" in window.detail.text()
        assert "margin_rejection" not in window.detail.text()

        for timestamp in (100.63, 100.81, 100.99):
            current[0] = timestamp
            window.poll()

        assert window.viewer.position == 0
        assert window.controller.state == "WAIT_NEUTRAL"
        assert "Show NEUTRAL" in window.detail.text()
        assert "Pose is ambiguous" not in window.detail.text()
    finally:
        window.close()


def test_close_event_does_not_trap_window_when_worker_wait_times_out(qapp) -> None:
    window = Window(model=object(), feature_function=lambda observation, hand: np.zeros(60))
    _disable_logging(window)
    worker = FakeWorker(wait_result=False)
    window.worker = worker
    event = FakeCloseEvent()

    window.closeEvent(event)

    assert worker.interrupted is True
    assert event.accepted is True
    assert event.ignored is False
    assert window.timer.isActive() is False


def test_poll_allows_longer_cold_start_before_first_worker_result(monkeypatch, qapp) -> None:
    import gestureforge.app as app_module

    window = Window(model=object(), feature_function=lambda observation, hand: np.zeros(60))
    _disable_logging(window)
    worker = FakeWorker()
    window.worker = worker
    window.controller.resume("live-session")
    window.last_result_at = 100.0
    monkeypatch.setattr(app_module.time, "monotonic", lambda: 103.0)

    try:
        window.poll()

        assert worker.interrupted is False
        assert window.controller.state != "PAUSED"
    finally:
        window.close()


def test_main_rejects_synthetic_dataset_for_live_control(tmp_path) -> None:
    manifest = tmp_path / "manifest.json"
    feature_file = tmp_path / "features.npz"
    np.savez_compressed(feature_file, features=np.ones((1, 60), dtype=np.float32))
    digest = sha256(feature_file.read_bytes()).hexdigest()
    manifest.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "feature_version": 1,
                "labels": ["NEXT", "PREVIOUS", "BOOKMARK", "NEUTRAL"],
                "feature_file": feature_file.name,
                "feature_sha256": digest,
                "metadata": {"provenance": "SYNTHETIC", "chosen_hand": "Right"},
                "records": [
                    {
                        "participant_id": "SYNTHETIC_SOFTWARE_TEST_ONLY",
                        "session_id": "SYN-train",
                        "trial_id": "SYN-train-NEXT-00",
                        "intended_label": "NEXT",
                        "split": "train",
                        "sample_index": 0,
                        "timestamp": 0.0,
                        "valid": True,
                        "feature_index": 0,
                        "validity_reason": "",
                        "hand": "Right",
                        "provenance": "synthetic",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    completed = subprocess.run(
        [sys.executable, "-m", "gestureforge", "--dataset", str(manifest), "--smoke-test"],
        check=False,
        capture_output=True,
        text=True,
        env={**os.environ, "QT_QPA_PLATFORM": "offscreen"},
    )

    assert completed.returncode == 1
    assert "Synthetic fixtures cannot enable live control" in completed.stderr


def test_main_studio_smoke_starts_without_dataset() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "gestureforge", "--studio", "--smoke-test"],
        check=False,
        capture_output=True,
        text=True,
        env={**os.environ, "QT_QPA_PLATFORM": "offscreen"},
        timeout=20,
    )

    assert completed.returncode == 0


@pytest.mark.parametrize("studio", [False, True])
@pytest.mark.parametrize("custom", [False, True])
def test_main_selects_dataset_vocabulary_without_changing_assignment(studio, custom, monkeypatch) -> None:
    from gestureforge import __main__ as launcher
    from gestureforge.fixtures import synthetic_dataset
    from gestureforge.vocabulary import LEGACY_VOCABULARY

    vocabulary = GestureVocabulary(("G1", "G2", "G3")) if custom else LEGACY_VOCABULARY
    bundle = synthetic_dataset(trials_per_label_per_split=2)
    features, labels, records = bundle.training_data()
    mapping = dict(zip(LEGACY_VOCABULARY.labels, vocabulary.labels, strict=True))
    # Mock only the human-data gate; synthetic arrays never become participant files.
    dataset = SimpleNamespace(
        vocabulary=vocabulary, metadata={"chosen_hand": "Right"},
        records=[SimpleNamespace(provenance="human", participant_id="MOCK_GATE_ONLY")],
        training_data=lambda: (features, np.array([mapping[label] for label in labels]), records),
    )
    monkeypatch.setattr("gestureforge.dataset.load_dataset", lambda _: dataset)
    application = Mock()
    application.exec.return_value = 0
    monkeypatch.setattr("PySide6.QtWidgets.QApplication", Mock(return_value=application))
    window = Mock()
    monkeypatch.setattr("gestureforge.app.Window", window)
    monkeypatch.setattr(sys, "argv", ["gestureforge", "--dataset", "mock-manifest.json"]
                        + (["--studio"] if studio else []))
    if custom and not studio:
        with pytest.raises(SystemExit) as exc:
            launcher.main()
        assert exc.value.code == 1
        window.assert_not_called()
        return
    assert launcher.main() == 0
    model = window.call_args.args[0]
    assert set(model.train_labels) == set(vocabulary.labels)
    assert model.model_version.startswith("gesture-v1-" if studio else "prototype-v3")
    assert window.call_args.kwargs["vocabulary"] == vocabulary


def test_custom_classifier_labels_reach_studio_simulation(monkeypatch, qapp) -> None:
    from gestureforge.fixtures import synthetic_dataset
    from gestureforge.models import train_model
    from gestureforge.vocabulary import LEGACY_VOCABULARY

    vocabulary = GestureVocabulary(("G1", "G2", "G3"))
    features, labels, records = synthetic_dataset(trials_per_label_per_split=2).training_data()
    mapping = dict(zip(LEGACY_VOCABULARY.labels, vocabulary.labels, strict=True))
    labels = np.array([mapping[label] for label in labels])
    model = train_model(features, labels, vocabulary=vocabulary,
                        groups=[record.trial_id for record in records])
    window = Window(model=model, studio=True, vocabulary=vocabulary)
    _disable_logging(window)
    assert window.routing is not None
    current = [100.0]
    monkeypatch.setattr("gestureforge.app.time.monotonic", lambda: current[0])
    try:
        assert [label.text() for label in window.binding_labels] == [f"{g} gesture" for g in vocabulary.action_ids]
        assert window.routing.snapshot.model_version == model.model_version
        window.routing.resume()
        packets = []
        for i, timestamp, gesture in (
            (1, 100.0, "NEUTRAL"), (2, 100.15, "NEUTRAL"), (3, 100.31, "NEUTRAL"),
            (4, 100.45, "G1"), (5, 100.60, "G1"), (6, 100.75, "G1"), (7, 100.90, "G1"),
            (8, 101.05, "G1"),
        ):
            label, accepted, _ = model.predict(features[np.flatnonzero(labels == gesture)[0]])
            assert accepted and label == gesture
            packets.append((_frame(), _studio_prediction(window, i, timestamp, label)))
        window.worker = FakeWorker(packets)
        for _, prediction in packets:
            current[0] = prediction.timestamp
            window.poll()
        assert "G1 would show next card" in window.feedback.text()
        assert window.routing.state == "LATCHED"
        assert window.viewer.position == 0
    finally:
        window.close()


def test_studio_rejects_live_mode_at_both_entry_points(qapp) -> None:
    with pytest.raises(ValueError, match="simulation modes only"):
        Window(studio=True, studio_mode=RoutingMode.LIVE)
    window = Window(studio=True)
    _disable_logging(window)
    try:
        assert window.routing is not None
        original = window.routing.snapshot
        with pytest.raises(ValueError, match="simulation modes only"):
            window.configure_studio(mode=RoutingMode.LIVE)
        assert window.routing.snapshot == original
    finally:
        window.close()


def test_studio_binding_editor_applies_once_then_new_hold_simulates_new_action(monkeypatch, qapp) -> None:
    import gestureforge.app as app_module

    window = Window(model=object(), studio=True)
    _disable_logging(window)
    assert window.routing is not None
    old = window.routing.resume()
    worker = FakeWorker([(_frame(), _studio_prediction(window, 1, 100.0, "NEXT"))])
    window.worker = worker
    current = [100.0]
    monkeypatch.setattr(app_module.time, "monotonic", lambda: current[0])
    try:
        # Editing is a draft: no implicit remapping or restart during a hold.
        window.binding_pickers[0].setCurrentIndex(1)  # NEXT gesture -> PREVIOUS action
        window.mode_picker.setCurrentIndex(1)
        assert window.routing.snapshot == old
        window.apply_bindings_button.click()
        assert worker.interrupted
        assert window.routing.state == "PAUSED"
        assert window.routing.snapshot.session_id != old.session_id
        assert window.routing.snapshot.mode == RoutingMode.REHEARSAL
        assert dict(window.routing.snapshot.bindings)["NEXT"] == Action(ActionType.PREVIOUS)
        window.poll()
        assert window.prediction.text() == "Prediction: awaiting new camera session"
        assert window.viewer.position == 0
        assert "NEXT: would show previous card" in window.boundary.text()

        window.routing.resume()
        packets = [(_frame(), _studio_prediction(window, i, t, label)) for i, t, label in (
            (1, 101.0, "NEUTRAL"), (2, 101.15, "NEUTRAL"), (3, 101.31, "NEUTRAL"),
            (4, 101.45, "NEXT"), (5, 101.60, "NEXT"), (6, 101.75, "NEXT"), (7, 101.90, "NEXT"),
        )]
        window.worker = FakeWorker(packets)
        for _, prediction in packets:
            current[0] = prediction.timestamp
            window.poll()
        assert "NEXT would show previous card" in window.feedback.text()
        assert window.viewer.position == 0
    finally:
        window.close()


def test_studio_invalid_draft_preserves_active_session_and_custom_mapping_survives_mode_change(qapp) -> None:
    window = Window(studio=True, vocabulary=GestureVocabulary(("G1", "G2", "G3")))
    _disable_logging(window)
    assert window.routing is not None
    try:
        window.configure_studio(context_id="stage-2", bindings={"G1": Action(ActionType.BOOKMARK)})
        old = window.routing.resume()
        worker = FakeWorker()
        window.worker = worker
        with pytest.raises(ValueError):
            window.configure_studio(bindings={"NEUTRAL": Action(ActionType.NEXT)})
        with pytest.raises(ValueError, match="selected dataset vocabulary"):
            window.configure_studio(bindings={"NOT_ENROLLED": Action(ActionType.NEXT)})
        assert window.routing.snapshot == old
        assert not worker.interrupted
        assert window.routing.state == "WAIT_NEUTRAL"
        window.mode_picker.setCurrentIndex(1)
        window.apply_bindings_button.click()
        assert window.routing.snapshot.context_id == "stage-2"
        assert dict(window.routing.snapshot.bindings) == {"G1": Action(ActionType.BOOKMARK)}
        assert window.binding_labels[0].text() == "G1 gesture"
        assert window.binding_pickers[1].isHidden()
        assert worker.interrupted
    finally:
        window.close()


@pytest.mark.parametrize("change", ["pause", "session", "profile", "model"])
def test_studio_discards_interrupted_or_wrong_identity_packet_before_display(change, monkeypatch, qapp) -> None:
    import gestureforge.app as app_module

    window = Window(model=object(), studio=True)
    _disable_logging(window)
    assert window.routing is not None
    window.routing.resume()
    packet = _studio_prediction(window, 1, 100.0, "NEXT")
    packet = replace(
        packet,
        session_id="other" if change == "session" else packet.session_id,
        profile_id="other" if change == "profile" else packet.profile_id,
        model_version="other" if change == "model" else packet.model_version,
    )
    window.worker = FakeWorker([(_frame(), packet)])
    window.last_result_at = 100.0
    monkeypatch.setattr(app_module.time, "monotonic", lambda: 100.0)
    try:
        before = window.prediction.text()
        if change == "pause":
            window.pause()
        window.poll()
        assert window.prediction.text() == before
        assert "Studio simulation" not in window.feedback.text()
        assert window.viewer.position == 0
    finally:
        window.close()
