from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace

import pytest

from gestureforge.contracts import Observation, Prediction
from scripts import check_stability


@dataclass
class FakeClock:
    now: float = 100.0

    def monotonic(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.now += seconds


class FakeWorker:
    def __init__(self, packets=None, *, error="", stuck=False, on_start=None, finished=False):
        self.packets = list(packets or [])
        self.error = error
        self.stuck = stuck
        self.on_start = on_start
        self.finished = finished
        self.started = False
        self.interrupted = False
        self.waited_ms = None

    def start(self):
        self.started = True
        if self.on_start is not None:
            self.on_start()

    def take_latest(self):
        if not self.packets:
            return None
        return self.packets.pop(0)

    def requestInterruption(self):
        self.interrupted = True

    def wait(self, milliseconds):
        self.waited_ms = milliseconds
        return not self.stuck

    def isFinished(self):
        return self.finished


def packet(payload):
    return object(), payload


def observation(frame_id: int, timestamp: float) -> Observation:
    return Observation("stability", "profile", frame_id, timestamp, 1, "Right", None, "")


def prediction(frame_id: int, timestamp: float) -> Prediction:
    return Prediction("stability", "profile", frame_id, timestamp, "NEXT", True, "model")


def config(tmp_path, *, seconds=1, dataset=None, output_name="stability.json"):
    return check_stability.DiagnosticConfig(
        camera=1,
        seconds=seconds,
        output=tmp_path / output_name,
        dataset=dataset,
        algorithm="knn",
        multiplier=1.5,
        margin=1.5,
        asset=tmp_path / "asset.task",
    )


def run_with_worker(tmp_path, worker, *, clock=None, cfg=None, **kwargs):
    clock = clock or FakeClock()
    cfg = cfg or config(tmp_path)
    writes = []

    def write_report(path: Path, report: dict):
        writes.append((path, report))

    report = check_stability.run_diagnostic(
        cfg,
        clock=clock,
        sleep=clock.sleep,
        worker_factory=lambda *args, **worker_kwargs: worker,
        memory_reader=lambda: {"peak_bytes": 1234, "method": "fake", "scope": "process_lifetime_peak"},
        versions_reader=lambda: {"gestureforge": "0.1-test"},
        write_report=write_report,
        **kwargs,
    )
    assert writes == [(cfg.output, report)]
    return report, worker


def test_completed_observation_only_report_is_fixed_size_and_has_no_frame_rows(tmp_path):
    clock = FakeClock()
    worker = FakeWorker(
        [
            packet(observation(0, 99.99)),
            packet(observation(1, 100.02)),
            packet(observation(2, 100.05)),
        ]
    )

    report, worker = run_with_worker(tmp_path, worker, clock=clock)

    assert report["status"]["completed_diagnostic"] is True
    assert report["status"]["state"] == "completed"
    assert report["status"]["clean_shutdown"] is True
    assert report["config"]["observation_only"] is True
    assert report["config"]["dataset_backed_recognizer"] is False
    assert report["metrics"]["delivered_frames"] == 3
    assert report["metrics"]["first_frame_latency_seconds"] == 0.0
    assert report["scope_limits"]["no_media_landmarks_features_labels_or_frame_rows"] is True
    assert "frames" not in report
    assert "NEXT" not in str(report)
    assert worker.interrupted is True
    assert worker.waited_ms == check_stability.SHUTDOWN_WAIT_MS


def test_dataset_mode_uses_model_loader_and_feature_extractor_without_persisting_names(tmp_path):
    dataset = tmp_path / "manifest.json"
    dataset.write_text("{}", encoding="utf-8")
    cfg = config(tmp_path, dataset=dataset)
    worker_args = []
    model = SimpleNamespace(model_version="model-for-person-name")

    def model_loader(path, algorithm, multiplier, margin, *, studio):
        assert path == dataset
        assert (algorithm, multiplier, margin, studio) == ("knn", 1.5, 1.5, True)
        return model, "Left", "PersonName", object()

    def worker_factory(*args, **kwargs):
        worker_args.append((args, kwargs))
        return FakeWorker([packet(prediction(0, 99.99))])

    clock = FakeClock()
    report = check_stability.run_diagnostic(
        cfg,
        clock=clock,
        sleep=clock.sleep,
        worker_factory=worker_factory,
        model_loader=model_loader,
        feature_function=lambda observation, hand: [1],
        memory_reader=lambda: {
            "peak_bytes": None,
            "method": None,
            "scope": "process_lifetime_peak",
            "unavailable": True,
        },
        versions_reader=lambda: {},
        write_report=lambda path, data: None,
    )

    args, kwargs = worker_args[0]
    assert args[0] is model
    assert args[1] is not None
    assert args[2] == "Left"
    assert kwargs == {"observation_only": False}
    assert report["config"]["dataset_backed_recognizer"] is True
    assert report["provenance"]["dataset_sha256"] is not None
    assert report["provenance"]["recognizer_settings_sha256"] is not None
    assert "PersonName" not in str(report)
    assert "model-for-person-name" not in str(report)


def test_no_frames_fails_after_startup_timeout_and_shutdown_is_bounded(tmp_path):
    clock = FakeClock()
    report, worker = run_with_worker(
        tmp_path,
        FakeWorker(stuck=True),
        clock=clock,
        cfg=config(tmp_path, seconds=21),
    )

    assert report["status"]["completed_diagnostic"] is False
    assert report["status"]["state"] == "failed"
    assert report["status"]["failure_reason"] == "startup_timeout_no_frame"
    assert report["timing_flags"]["startup_timeout_no_frame"] is True
    assert report["status"]["clean_shutdown"] is False
    assert worker.waited_ms == check_stability.SHUTDOWN_WAIT_MS


def test_camera_worker_failure_is_reported(tmp_path):
    report, _worker = run_with_worker(tmp_path, FakeWorker(error="CameraError: unavailable"))

    assert report["status"]["state"] == "failed"
    assert report["status"]["failure_reason"] == "capture_worker_error"
    assert report["status"]["worker_error"] == "CameraError"


def test_worker_error_redaction_does_not_persist_paths(tmp_path):
    report, _worker = run_with_worker(tmp_path, FakeWorker(error="C:\\private\\camera failed"))

    assert report["status"]["worker_error"] == "capture_error"
    assert "private" not in str(report)


def test_lag_drop_and_order_counters_are_aggregated(tmp_path):
    clock = FakeClock()
    worker = FakeWorker(
        [
            packet(observation(1, 99.0)),
            packet(observation(4, 100.0)),
            packet(observation(3, 100.01)),
            packet(observation(5, 100.02)),
        ]
    )

    report, _worker = run_with_worker(tmp_path, worker, clock=clock)

    assert report["metrics"]["delivered_frames"] == 4
    assert report["metrics"]["stale_frames_over_200ms"] == 1
    assert report["metrics"]["frame_id_gap_events"] == 1
    assert report["metrics"]["frame_id_missing_count"] == 2
    assert report["metrics"]["out_of_order_frames"] == 1
    assert report["timing_flags"]["stale_frames_observed"] is True
    assert report["timing_flags"]["frame_gaps_observed"] is True
    assert report["timing_flags"]["out_of_order_observed"] is True


def test_invalid_frame_metadata_is_flagged_without_raw_payload(tmp_path):
    clock = FakeClock()
    worker = FakeWorker(
        [
            packet(observation(-1, 101.0)),
            packet(Observation("stability", "profile", 1, float("nan"), 1, "Right", None, "")),
        ]
    )

    report, _worker = run_with_worker(tmp_path, worker, clock=clock)

    assert report["metrics"]["negative_frame_id_frames"] == 1
    assert report["metrics"]["future_timestamp_frames"] == 1
    assert report["metrics"]["invalid_timestamp_frames"] == 1
    assert report["timing_flags"]["invalid_frame_metadata_observed"] is True


def test_receive_time_is_sampled_after_mailbox_take(tmp_path):
    clock = FakeClock()

    class AdvancingWorker(FakeWorker):
        def take_latest(self):
            clock.now += 0.25
            return packet(observation(0, clock.now))

    report, _worker = run_with_worker(tmp_path, AdvancingWorker(), clock=clock)

    assert report["metrics"]["future_timestamp_frames"] == 0
    assert report["metrics"]["max_frame_age_seconds"] == 0.0


def test_worker_finished_unexpectedly_fails(tmp_path):
    report, _worker = run_with_worker(tmp_path, FakeWorker(finished=True))

    assert report["status"]["state"] == "failed"
    assert report["status"]["failure_reason"] == "capture_worker_finished_unexpectedly"


def test_no_frame_gap_timeout_after_first_frame(tmp_path):
    clock = FakeClock()
    report, _worker = run_with_worker(
        tmp_path,
        FakeWorker([packet(observation(0, 100.0))]),
        clock=clock,
        cfg=config(tmp_path, seconds=10),
    )

    assert report["status"]["state"] == "failed"
    assert report["status"]["failure_reason"] == "no_frame_gap_timeout"
    assert report["timing_flags"]["no_frame_gap_timeout"] is True


def test_terminal_no_frame_gap_is_checked_after_duration_sleep(tmp_path):
    clock = FakeClock()

    class OneFrameWorker(FakeWorker):
        def take_latest(self):
            if self.packets:
                clock.now = 100.99
            return super().take_latest()

    def sleep_to_deadline(_seconds):
        clock.now = 103.0

    worker = OneFrameWorker([packet(observation(0, 100.99))])
    writes = []
    cfg = config(tmp_path, seconds=3)

    report = check_stability.run_diagnostic(
        cfg,
        clock=clock,
        sleep=sleep_to_deadline,
        worker_factory=lambda *args, **worker_kwargs: worker,
        memory_reader=lambda: {"peak_bytes": 1234, "method": "fake", "scope": "process_lifetime_peak"},
        versions_reader=lambda: {},
        write_report=lambda path, data: writes.append((path, data)),
    )

    assert report["status"]["state"] == "failed"
    assert report["status"]["failure_reason"] == "no_frame_gap_timeout"
    assert report["timing_flags"]["no_frame_gap_timeout"] is True


def test_terminal_worker_finished_is_checked_after_duration_sleep(tmp_path):
    clock = FakeClock()
    worker = FakeWorker([packet(observation(0, 100.0))])

    def sleep_and_finish(_seconds):
        clock.now = 101.0
        worker.finished = True

    report = check_stability.run_diagnostic(
        config(tmp_path, seconds=1),
        clock=clock,
        sleep=sleep_and_finish,
        worker_factory=lambda *args, **worker_kwargs: worker,
        memory_reader=lambda: {"peak_bytes": 1234, "method": "fake", "scope": "process_lifetime_peak"},
        versions_reader=lambda: {},
        write_report=lambda path, data: None,
    )

    assert report["status"]["state"] == "failed"
    assert report["status"]["failure_reason"] == "capture_worker_finished_unexpectedly"


def test_keyboard_interrupt_saves_interrupted_report_and_requests_shutdown(tmp_path):
    def interrupt():
        raise KeyboardInterrupt

    report, worker = run_with_worker(tmp_path, FakeWorker(on_start=interrupt))

    assert report["status"]["state"] == "interrupted"
    assert report["status"]["interrupted"] is True
    assert report["status"]["failure_reason"] == "keyboard_interrupt"
    assert worker.interrupted is True


def test_output_exists_refuses_before_worker_starts(tmp_path):
    output = tmp_path / "exists.json"
    output.write_text("{}", encoding="utf-8")
    worker = FakeWorker()
    cfg = config(tmp_path, output_name="exists.json")

    with pytest.raises(ValueError, match="output already exists"):
        check_stability.run_diagnostic(cfg, worker_factory=lambda *args, **kwargs: worker)

    assert worker.started is False


def test_output_must_not_overwrite_dataset(tmp_path):
    dataset = tmp_path / "same.json"
    dataset.write_text("{}", encoding="utf-8")
    cfg = config(tmp_path, dataset=dataset, output_name="same.json")

    with pytest.raises(ValueError, match="output already exists|overwrite dataset"):
        check_stability.run_diagnostic(cfg, worker_factory=lambda *args, **kwargs: FakeWorker())


def test_parse_args_requires_camera_and_validates_duration(tmp_path):
    with pytest.raises(SystemExit):
        check_stability.parse_args(["--seconds", "1", "--output", str(tmp_path / "o.json")])
    with pytest.raises(SystemExit):
        check_stability.parse_args(
            ["--camera", "0", "--seconds", "0", "--output", str(tmp_path / "o.json")]
        )
    with pytest.raises(SystemExit):
        check_stability.parse_args(
            ["--camera", "-1", "--seconds", "1", "--output", str(tmp_path / "o.json")]
        )
    parsed = check_stability.parse_args(
        [
            "--camera",
            "1",
            "--seconds",
            "1",
            "--output",
            str(tmp_path / "o.json"),
            "--multiplier",
            "2",
            "--margin",
            "1.5",
        ]
    )
    assert parsed.multiplier == 2.0
    assert parsed.margin == 1.5


def test_main_returns_nonzero_for_failed_report(tmp_path, monkeypatch):
    cfg = config(tmp_path)
    monkeypatch.setattr(check_stability, "parse_args", lambda argv=None: cfg)
    monkeypatch.setattr(
        check_stability,
        "run_diagnostic",
        lambda _config: {"status": {"completed_diagnostic": False}},
    )

    assert check_stability.main([]) == 1


def test_camera_index_validation_rejects_bool(tmp_path):
    cfg = config(tmp_path)
    cfg = check_stability.DiagnosticConfig(
        camera=True,
        seconds=1,
        output=cfg.output,
        dataset=None,
        algorithm="knn",
        multiplier=1.5,
        margin=1.5,
        asset=cfg.asset,
    )
    with pytest.raises(ValueError, match="Camera index"):
        check_stability.validate_config(cfg)
