import json
import os
from unittest.mock import Mock

import pytest

from scripts.monitor_studio import Monitor, ReportFile


@pytest.fixture(autouse=True)
def available_memory(monkeypatch):
    monkeypatch.setattr("scripts.monitor_studio.current_process_peak_memory", lambda: {
        "peak_bytes": 123456, "method": "test_fixture", "scope": "process_lifetime_peak",
    })


def worker():
    value = Mock()
    value.isFinished.return_value = False
    value.isInterruptionRequested.return_value = False
    value.error = ""
    return value


def finish(monitor, camera, now):
    camera.isFinished.return_value = True
    camera.isInterruptionRequested.return_value = True
    monitor.event("normal_close", None, now)
    return monitor.report(now, finalized=True, qt_exit_code=0)


def test_normal_close_requires_active_duration_and_observations():
    monitor = Monitor(0, 1)
    camera = worker()
    monitor.event("worker_started", camera, 0)
    monitor.event("observation", camera, .1)
    monitor.event("observation", camera, .6)
    monitor.event("observation", camera, 1.1)
    report = finish(monitor, camera, 1.2)
    assert report["measurement_criteria_met"]
    assert report["delivered_observations"] == 3
    assert report["exit_outcome"] == "observed_normal_window_close"
    assert report["requested_seconds"] != 1800


def test_zero_frames_early_close_and_unknown_checkpoint():
    monitor = Monitor(0, 1800)
    assert monitor.report(1900)["exit_outcome"] == "unknown"
    monitor.event("normal_close", None, 1)
    report = monitor.report(1, finalized=True, qt_exit_code=0)
    assert report["early_close"]
    assert not report["measurement_criteria_met"]
    assert "no_delivered_observations" in report["unmet_measurement_criteria"]


def test_gui_gap_and_frame_gap_fail_even_when_duration_reached():
    monitor = Monitor(0, 1)
    camera = worker()
    monitor.event("observation", camera, 0)
    monitor.tick(3)
    report = finish(monitor, camera, 3.1)
    assert "gui_gap_over_2_seconds" in report["unmet_measurement_criteria"]
    assert "delivered_observation_gap_over_2_seconds" in report["unmet_measurement_criteria"]


def test_restart_does_not_count_paused_time_as_frame_gap():
    monitor = Monitor(0, 1)
    first, second = worker(), worker()
    monitor.event("observation", first, 0)
    monitor.tick(.5)
    first.isFinished.return_value = True
    first.isInterruptionRequested.return_value = True
    monitor.tick(.5)
    for now in range(1, 10):
        monitor.tick(now)
    monitor.event("observation", second, 10)
    monitor.tick(10.6)
    report = finish(monitor, second, 10.6)
    assert report["generation_observation_counts"] == [1, 1]
    assert report["camera_active_seconds_estimate"] == pytest.approx(1.1)
    assert report["delivered_max_gap_seconds_within_generation"] == pytest.approx(.6)
    assert not report["measurement_criteria_met"]


def test_worker_failure_and_release_are_explicit_without_private_errors():
    monitor = Monitor(0, 1)
    camera = worker()
    monitor.event("observation", camera, 0)
    camera.error = "private profile path and participant label"
    report = monitor.report(2, finalized=True, qt_exit_code=0)
    assert report["worker_error_count"] == 1
    assert not report["all_workers_released"]
    assert "private" not in json.dumps(report)
    assert "landmark" not in json.dumps(report)


def test_unique_output_and_external_changes_preserved(tmp_path):
    path = tmp_path / "monitor.json"
    output = ReportFile(path, {"status": "incomplete"})
    with pytest.raises(ValueError):
        ReportFile(path, {})
    output.save({"status": "final"})
    assert json.loads(path.read_text())["status"] == "final"
    path.write_text("external")
    with pytest.raises(ValueError):
        output.save({})
    assert path.read_text() == "external"


def test_write_failure_preserves_checkpoint(tmp_path, monkeypatch):
    path = tmp_path / "monitor.json"
    output = ReportFile(path, {"status": "incomplete"})
    def fail(*args):
        raise OSError("disk unavailable")
    monkeypatch.setattr(os, "replace", fail)
    with pytest.raises(OSError):
        output.save({"status": "final"})
    assert json.loads(path.read_text())["status"] == "incomplete"
    assert list(tmp_path.iterdir()) == [path]


@pytest.mark.parametrize("seconds", [0, -1, float("nan"), float("inf")])
def test_bad_duration(seconds):
    with pytest.raises(ValueError):
        Monitor(0, seconds)


def test_actual_studio_normal_close_offscreen(tmp_path, monkeypatch):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication
    import gestureforge.app as app_module
    app = QApplication.instance() or QApplication([])
    monkeypatch.setattr(app_module, "DEFAULT_STUDIO_STATE_FOLDER", tmp_path / "state")
    monkeypatch.setattr(app_module.Window, "log", lambda *args: None)
    window = app_module.Window(studio=True)
    monitor = Monitor(0, 1800)
    window.measurement.connect(lambda kind, camera: monitor.event(kind, camera, 1))
    window.show()
    app.processEvents()
    assert window.worker is None
    window.close()
    app.processEvents()
    assert monitor.normal_close
    assert not monitor.report(1, finalized=True, qt_exit_code=0)["measurement_criteria_met"]

def test_only_current_generation_packets_count_and_one_consumer(tmp_path, monkeypatch):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    import time
    import numpy as np
    from PySide6.QtWidgets import QApplication
    import gestureforge.app as app_module
    from gestureforge.contracts import Prediction
    app = QApplication.instance() or QApplication([])
    monkeypatch.setattr(app_module, "DEFAULT_STUDIO_STATE_FOLDER", tmp_path / "state")
    monkeypatch.setattr(app_module.Window, "log", lambda *args: None)
    window = app_module.Window(studio=True)
    camera = worker()
    camera.observation_only = False
    camera.wait.return_value = True
    window.worker = camera
    monitor = Monitor(time.monotonic(), 1800)
    window.measurement.connect(lambda kind, value: monitor.event(kind, value, time.monotonic()))
    assert window.routing is not None
    snapshot = window.routing.snapshot
    frame = np.zeros((20, 20, 3), dtype=np.uint8)
    def packet(session):
        return frame, Prediction(session, snapshot.profile_id, 1, time.monotonic(),
                                 "NEUTRAL", True, model_version=snapshot.model_version)
    camera.take_latest.return_value = packet("old-generation")
    window.poll()
    assert sum(monitor.frames) == 0
    camera.take_latest.return_value = packet(snapshot.session_id)
    window.poll()
    assert sum(monitor.frames) == 1
    assert camera.take_latest.call_count == 2
    camera.isFinished.return_value = True
    camera.isInterruptionRequested.return_value = True
    window.close()
    app.processEvents()


def test_two_900_second_generations_do_not_pass_1800_second_continuity():
    monitor = Monitor(0, 1800)
    first, second = worker(), worker()
    monitor.event("worker_started", first, 0)
    for now in range(901):
        monitor.event("observation", first, now)
    # Even an overlapping restart with no heartbeat gap breaks continuity.
    monitor.event("worker_started", second, 900)
    first.isFinished.return_value = True
    first.isInterruptionRequested.return_value = True
    for now in range(900, 1801):
        monitor.event("observation", second, now)
    report = finish(monitor, second, 1800)
    assert report["camera_active_seconds_estimate"] == 1800
    assert report["longest_contiguous_delivered_seconds"] == 900
    assert not report["measurement_criteria_met"]


def test_startup_time_and_final_pending_gap_cannot_inflate_continuity():
    monitor = Monitor(0, 10)
    camera = worker()
    monitor.event("worker_started", camera, 0)
    for now in range(10):
        monitor.tick(now)
    monitor.event("observation", camera, 10)
    monitor.event("observation", camera, 11)
    monitor.tick(14)
    report = finish(monitor, camera, 14)
    assert report["longest_contiguous_delivered_seconds"] == 1
    assert report["delivered_max_gap_seconds_within_generation"] == 3
    assert not report["measurement_criteria_met"]


def test_memory_unavailable_prevents_measurement_pass(monkeypatch):
    monkeypatch.setattr("scripts.monitor_studio.current_process_peak_memory", lambda: {
        "peak_bytes": None, "unavailable": True,
    })
    monitor = Monitor(0, 1)
    camera = worker()
    monitor.event("observation", camera, 0)
    monitor.event("observation", camera, 1)
    report = finish(monitor, camera, 1)
    assert "peak_process_memory_unavailable" in report["unmet_measurement_criteria"]
    assert not report["measurement_criteria_met"]


def test_event_loop_error_and_unknown_code_prevent_measurement_pass():
    monitor = Monitor(0, 1)
    camera = worker()
    monitor.event("observation", camera, 0)
    monitor.event("observation", camera, 1)
    assert finish(monitor, camera, 1)["measurement_criteria_met"]
    for code in (None, 2):
        report = monitor.report(1, finalized=True, qt_exit_code=code)
        assert report["qt_event_loop_exit_code"] == code
        assert "qt_event_loop_exit_not_successful" in report["unmet_measurement_criteria"]
        assert not report["measurement_criteria_met"]
    assert monitor.report(1)["qt_event_loop_exit_code"] is None


def test_preflight_gui_gap_is_descriptive_not_active_capture_failure():
    monitor = Monitor(0, 1)
    # Slow construction or native profile selection happens before capture starts.
    monitor.tick(20)
    camera = worker()
    monitor.event("worker_started", camera, 30)
    monitor.event("observation", camera, 30)
    monitor.event("observation", camera, 31)
    report = finish(monitor, camera, 31)
    assert report["gui_max_gap_seconds"] == 20
    assert report["active_gui_max_gap_seconds"] == 1
    assert report["first_active_gui_gap_elapsed_seconds"] is None
    assert report["first_delivered_gap_elapsed_seconds"] is None
    assert report["measurement_criteria_met"]


def test_finished_camera_then_paused_native_dialog_does_not_invent_active_gap():
    monitor = Monitor(0, 1)
    camera = worker()
    monitor.event("observation", camera, 0)
    monitor.event("observation", camera, 1)
    # Thread stops between timer samples, then a native dialog delays polling.
    report = finish(monitor, camera, 11)
    assert report["longest_contiguous_delivered_seconds"] == 1
    assert report["gui_max_gap_seconds"] == 10
    assert report["active_gui_max_gap_seconds"] == 1
    assert report["delivered_max_gap_seconds_within_generation"] == 1
    assert report["camera_active_seconds_estimate"] == 1
    assert report["first_active_gui_gap_elapsed_seconds"] is None
    assert report["first_delivered_gap_elapsed_seconds"] is None
    assert report["measurement_criteria_met"]


def test_progress_counts_received_continuity_not_waiting_time():
    monitor = Monitor(0, 10)
    assert "Waiting / paused" in monitor.progress_text()
    camera = worker()
    monitor.event("observation", camera, 0)
    monitor.event("observation", camera, 1)
    monitor.tick(2)
    assert "continuous 1.0s / 10s" in monitor.progress_text()
    assert "remaining 9.0s" in monitor.progress_text()
    assert "received 2 frames" in monitor.progress_text()
    monitor.tick(4)
    assert "Waiting / paused" in monitor.progress_text()
    assert "remaining 10.0s" in monitor.progress_text()
    monitor.event("observation", camera, 5)
    assert "continuous 0.0s" in monitor.progress_text()
    assert "no automatic stop" in monitor.progress_text()


def test_gap_warning_and_first_detection_survive_recovered_duration():
    monitor = Monitor(10, 1)
    camera = worker()
    monitor.event("observation", camera, 10)
    monitor.event("observation", camera, 13)
    monitor.event("observation", camera, 14)
    assert "remaining 0.0s" in monitor.progress_text()
    assert "GAP RECORDED (>2s): this run cannot pass" in monitor.progress_text()
    # A later, larger gap must not overwrite when the first gap was detected.
    monitor.event("observation", camera, 18)
    monitor.event("observation", camera, 19)
    report = finish(monitor, camera, 19)
    assert report["first_active_gui_gap_elapsed_seconds"] == 3
    assert report["first_delivered_gap_elapsed_seconds"] == 3
    assert report["active_gui_max_gap_seconds"] == 4
    assert report["delivered_max_gap_seconds_within_generation"] == 4
    assert report["longest_contiguous_delivered_seconds"] == 1
    assert not report["measurement_criteria_met"]
    assert "GAP RECORDED (>2s): this run cannot pass" in monitor.progress_text()


def test_frame_gap_records_detection_without_inventing_gui_gap():
    monitor = Monitor(10, 1)
    camera = worker()
    monitor.event("observation", camera, 10)
    for now in (11, 12, 13, 14):
        monitor.tick(now)
    report = finish(monitor, camera, 14)
    assert report["first_delivered_gap_elapsed_seconds"] == 3
    assert report["first_active_gui_gap_elapsed_seconds"] is None
    assert "GAP RECORDED (>2s): this run cannot pass" in monitor.progress_text()
