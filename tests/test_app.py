import os
import json
import subprocess
import sys
import time
from hashlib import sha256

import numpy as np
import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from gestureforge.app import Window
from gestureforge.contracts import Prediction


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
