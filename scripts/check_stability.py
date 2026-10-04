"""GF-P23 bounded local capture stability diagnostic.

Run explicitly with a camera index, for example:
python -m scripts.check_stability --camera 1 --seconds 60 --output experiments/local/stability.json

The report is a timing and resource diagnostic only. It does not persist images,
landmarks, feature vectors, labels, or per-frame rows, and it does not certify
recognition accuracy, participant evidence, native-device behavior, or launcher
readiness.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import math
from pathlib import Path
import platform
import re
import subprocess
import sys
import time
from typing import Any, Callable, Protocol

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gestureforge.app import CaptureWorker, load_personal_model, validate_camera_index  # noqa: E402
from gestureforge.capture import DEFAULT_ASSET  # noqa: E402
from gestureforge.features import extract_feature_vector  # noqa: E402
from gestureforge.traces import _write_json_exclusive  # noqa: E402

SCHEMA_VERSION = 1
POLL_INTERVAL_SECONDS = 0.030
STARTUP_TIMEOUT_SECONDS = 20.0
NO_FRAME_GAP_SECONDS = 2.0
STALE_FRAME_SECONDS = 0.200
SHUTDOWN_WAIT_MS = 3000
MIN_DURATION_SECONDS = 1
MAX_DURATION_SECONDS = 1800


class Clock(Protocol):
    def monotonic(self) -> float:
        ...


@dataclass(frozen=True)
class DiagnosticConfig:
    camera: int
    seconds: int
    output: Path
    dataset: Path | None
    algorithm: str
    multiplier: float
    margin: float
    asset: Path


@dataclass
class StabilityStats:
    started_at: float
    requested_seconds: int
    delivered_frames: int = 0
    first_frame_latency_seconds: float | None = None
    last_frame_received_at: float | None = None
    last_frame_id: int | None = None
    stale_frames_over_200ms: int = 0
    max_frame_age_seconds: float | None = None
    max_receive_gap_seconds: float | None = None
    frame_id_gap_events: int = 0
    frame_id_missing_count: int = 0
    out_of_order_frames: int = 0
    invalid_timestamp_frames: int = 0
    negative_frame_id_frames: int = 0
    future_timestamp_frames: int = 0

    def record(self, payload: Any, received_at: float) -> None:
        frame_id = getattr(payload, "frame_id", None)
        timestamp = getattr(payload, "timestamp", None)
        if self.delivered_frames == 0:
            self.first_frame_latency_seconds = _rounded(received_at - self.started_at)
        if self.last_frame_received_at is not None:
            gap = received_at - self.last_frame_received_at
            self.max_receive_gap_seconds = _max_rounded(self.max_receive_gap_seconds, gap)
        self.last_frame_received_at = received_at
        self.delivered_frames += 1

        if isinstance(frame_id, int) and not isinstance(frame_id, bool):
            update_last_frame_id = True
            if frame_id < 0:
                self.negative_frame_id_frames += 1
                update_last_frame_id = False
            if self.last_frame_id is not None:
                if frame_id <= self.last_frame_id:
                    self.out_of_order_frames += 1
                    update_last_frame_id = False
                elif frame_id > self.last_frame_id + 1:
                    self.frame_id_gap_events += 1
                    self.frame_id_missing_count += frame_id - self.last_frame_id - 1
            if update_last_frame_id:
                self.last_frame_id = frame_id
        if isinstance(timestamp, (int, float)) and not isinstance(timestamp, bool) and math.isfinite(timestamp):
            age = received_at - float(timestamp)
            if age < 0:
                self.future_timestamp_frames += 1
            self.max_frame_age_seconds = _max_rounded(self.max_frame_age_seconds, age)
            if age > STALE_FRAME_SECONDS:
                self.stale_frames_over_200ms += 1
        else:
            self.invalid_timestamp_frames += 1

    def as_report(self, finished_at: float) -> dict[str, Any]:
        elapsed = max(0.0, finished_at - self.started_at)
        return {
            "delivered_frames": self.delivered_frames,
            "first_frame_latency_seconds": self.first_frame_latency_seconds,
            "last_frame_age_seconds": None
            if self.last_frame_received_at is None
            else _rounded(finished_at - self.last_frame_received_at),
            "max_frame_age_seconds": self.max_frame_age_seconds,
            "stale_frames_over_200ms": self.stale_frames_over_200ms,
            "max_receive_gap_seconds": self.max_receive_gap_seconds,
            "frame_id_gap_events": self.frame_id_gap_events,
            "frame_id_missing_count": self.frame_id_missing_count,
            "out_of_order_frames": self.out_of_order_frames,
            "invalid_timestamp_frames": self.invalid_timestamp_frames,
            "negative_frame_id_frames": self.negative_frame_id_frames,
            "future_timestamp_frames": self.future_timestamp_frames,
            "observation_rate_hz": _rounded(self.delivered_frames / elapsed) if elapsed > 0 else None,
            "elapsed_seconds": _rounded(elapsed),
        }


def parse_args(argv: list[str] | None = None) -> DiagnosticConfig:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--camera", type=_camera_index, required=True)
    parser.add_argument("--seconds", type=_duration, default=60)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dataset", type=Path)
    parser.add_argument("--algorithm", choices=("knn", "svm"), default="knn")
    parser.add_argument("--multiplier", type=_positive_float, default=1.5)
    parser.add_argument("--margin", type=_margin, default=1.5)
    parser.add_argument("--asset", type=Path, default=DEFAULT_ASSET)
    args = parser.parse_args(argv)
    return DiagnosticConfig(
        camera=args.camera,
        seconds=args.seconds,
        output=args.output,
        dataset=args.dataset,
        algorithm=args.algorithm,
        multiplier=args.multiplier,
        margin=args.margin,
        asset=args.asset,
    )


def run_diagnostic(
    config: DiagnosticConfig,
    *,
    clock: Clock = time,
    sleep: Callable[[float], None] = time.sleep,
    worker_factory: Callable[..., Any] = CaptureWorker,
    model_loader: Callable[..., Any] = load_personal_model,
    feature_function: Callable[..., Any] = extract_feature_vector,
    memory_reader: Callable[[], dict[str, Any]] = lambda: current_process_peak_memory(),
    versions_reader: Callable[[], dict[str, str | None]] = lambda: dependency_versions(),
    write_report: Callable[[Path, dict[str, Any]], None] = _write_json_exclusive,
) -> dict[str, Any]:
    validate_config(config)
    if config.output.exists():
        raise ValueError("output already exists; choose a new diagnostic filename")
    if config.dataset is not None and _same_path(config.output, config.dataset):
        raise ValueError("output must not overwrite dataset input")

    environment = {
        "platform": platform.platform(),
        "python": platform.python_version(),
        "utc_started": datetime.now(timezone.utc).isoformat(),
        "dependencies": versions_reader(),
    }
    provenance = _provenance(config)
    model: Any = None
    chosen_hand = "Right"
    profile = "stability"
    observation_only = config.dataset is None
    if config.dataset is not None:
        loaded = model_loader(
            config.dataset,
            config.algorithm,
            config.multiplier,
            config.margin,
            studio=True,
        )
        model, chosen_hand, profile, _vocabulary = loaded
        provenance["recognizer_settings_sha256"] = _json_sha256(
            {
                "algorithm": config.algorithm,
                "multiplier": config.multiplier,
                "margin": config.margin,
                "model_version": str(getattr(model, "model_version", "unversioned")),
            }
        )
        provenance["model_version_sha256"] = _text_sha256(str(getattr(model, "model_version", "unversioned")))

    worker = worker_factory(
        model,
        None if observation_only else feature_function,
        chosen_hand,
        config.camera,
        config.asset,
        "stability",
        profile,
        observation_only=observation_only,
    )
    started_at = clock.monotonic()
    stats = StabilityStats(started_at=started_at, requested_seconds=config.seconds)
    status = "completed"
    failure_reason: str | None = None
    interrupted = False
    clean_shutdown = False
    worker_started = False
    worker_error = ""

    try:
        worker_started = True
        worker.start()
        deadline = started_at + config.seconds
        while clock.monotonic() < deadline:
            packet = worker.take_latest()
            now = clock.monotonic()
            if packet is not None:
                _frame, payload = packet
                stats.record(payload, now)
            error = getattr(worker, "error", "")
            if error:
                status = "failed"
                failure_reason = "capture_worker_error"
                worker_error = error
                break
            if bool(getattr(worker, "isFinished", lambda: False)()):
                status = "failed"
                failure_reason = "capture_worker_finished_unexpectedly"
                break
            if stats.delivered_frames == 0 and now - started_at >= STARTUP_TIMEOUT_SECONDS:
                status = "failed"
                failure_reason = "startup_timeout_no_frame"
                break
            if (
                stats.delivered_frames > 0
                and stats.last_frame_received_at is not None
                and now - stats.last_frame_received_at >= NO_FRAME_GAP_SECONDS
            ):
                status = "failed"
                failure_reason = "no_frame_gap_timeout"
                break
            sleep(POLL_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        status = "interrupted"
        failure_reason = "keyboard_interrupt"
        interrupted = True
    except Exception as exc:
        status = "failed"
        failure_reason = f"{type(exc).__name__}_during_capture"
        worker_error = type(exc).__name__
    finally:
        finished_at = clock.monotonic()
        if status == "completed":
            worker_error = worker_error or getattr(worker, "error", "")
            if worker_error:
                status = "failed"
                failure_reason = "capture_worker_error"
            elif bool(getattr(worker, "isFinished", lambda: False)()):
                status = "failed"
                failure_reason = "capture_worker_finished_unexpectedly"
            elif stats.delivered_frames == 0:
                status = "failed"
                failure_reason = "no_frames_delivered"
            elif (
                stats.last_frame_received_at is not None
                and finished_at - stats.last_frame_received_at >= NO_FRAME_GAP_SECONDS
            ):
                status = "failed"
                failure_reason = "no_frame_gap_timeout"
        if worker_started:
            try:
                worker.requestInterruption()
                clean_shutdown = bool(worker.wait(SHUTDOWN_WAIT_MS))
            except Exception:
                clean_shutdown = False
        worker_error = worker_error or getattr(worker, "error", "")
        if status == "completed":
            if worker_error:
                status = "failed"
                failure_reason = "capture_worker_error"
            elif not clean_shutdown:
                status = "failed"
                failure_reason = "shutdown_timeout"
        report = _build_report(
            config,
            environment,
            provenance,
            stats,
            finished_at,
            status=status,
            failure_reason=failure_reason,
            interrupted=interrupted,
            clean_shutdown=clean_shutdown,
            worker_error=_safe_error(worker_error),
            memory=memory_reader(),
        )
        write_report(config.output, report)
    return report


def _build_report(
    config: DiagnosticConfig,
    environment: dict[str, Any],
    provenance: dict[str, Any],
    stats: StabilityStats,
    finished_at: float,
    *,
    status: str,
    failure_reason: str | None,
    interrupted: bool,
    clean_shutdown: bool,
    worker_error: str,
    memory: dict[str, Any],
) -> dict[str, Any]:
    metrics = stats.as_report(finished_at)
    timing_flags = {
        "startup_timeout_no_frame": failure_reason == "startup_timeout_no_frame",
        "no_frame_gap_timeout": failure_reason == "no_frame_gap_timeout",
        "stale_frames_observed": stats.stale_frames_over_200ms > 0,
            "frame_gaps_observed": stats.frame_id_gap_events > 0,
            "out_of_order_observed": stats.out_of_order_frames > 0,
            "invalid_frame_metadata_observed": (
                stats.invalid_timestamp_frames > 0
                or stats.negative_frame_id_frames > 0
                or stats.future_timestamp_frames > 0
            ),
        }
    return {
        "schema_version": SCHEMA_VERSION,
        "diagnostic": "GF-P23 local capture stability",
        "status": {
            "completed_diagnostic": status == "completed",
            "state": status,
            "failure_reason": failure_reason,
            "interrupted": interrupted,
            "clean_shutdown": clean_shutdown,
            "worker_error": worker_error or None,
        },
        "scope_limits": {
            "timing_diagnostic_only": True,
            "not_recognition_validation": True,
            "not_live_action_or_dispatch_test": True,
            "not_gui_or_rendering_soak": True,
            "no_media_landmarks_features_labels_or_frame_rows": True,
        },
        "config": {
            "camera_index": config.camera,
            "requested_seconds": config.seconds,
            "poll_interval_seconds": POLL_INTERVAL_SECONDS,
            "startup_timeout_seconds": STARTUP_TIMEOUT_SECONDS,
            "no_frame_gap_seconds": NO_FRAME_GAP_SECONDS,
            "stale_frame_threshold_seconds": STALE_FRAME_SECONDS,
            "observation_only": config.dataset is None,
            "dataset_backed_recognizer": config.dataset is not None,
            "algorithm": config.algorithm if config.dataset is not None else None,
            "multiplier": config.multiplier if config.dataset is not None else None,
            "margin": config.margin if config.dataset is not None else None,
        },
        "metrics": metrics,
        "timing_flags": timing_flags,
        "memory": memory,
        "environment": environment,
        "provenance": provenance,
    }


def validate_config(config: DiagnosticConfig) -> None:
    validate_camera_index(config.camera)
    if not isinstance(config.seconds, int) or isinstance(config.seconds, bool):
        raise ValueError("seconds must be an integer")
    if not MIN_DURATION_SECONDS <= config.seconds <= MAX_DURATION_SECONDS:
        raise ValueError("seconds must be between 1 and 1800")
    if config.algorithm not in {"knn", "svm"}:
        raise ValueError("algorithm must be knn or svm")
    if not math.isfinite(config.multiplier) or config.multiplier <= 0:
        raise ValueError("multiplier must be finite and positive")
    if not math.isfinite(config.margin) or config.margin < 1.0:
        raise ValueError("margin must be finite and at least 1.0")


def current_process_peak_memory() -> dict[str, Any]:
    if sys.platform == "win32":
        return _windows_peak_memory()
    try:
        import resource

        usage = resource.getrusage(resource.RUSAGE_SELF)
        # getrusage ru_maxrss is bytes on Darwin/XNU and KiB on Linux.
        multiplier = 1 if sys.platform == "darwin" else 1024
        return {
            "peak_bytes": int(usage.ru_maxrss * multiplier),
            "method": "resource.ru_maxrss",
            "scope": "process_lifetime_peak",
        }
    except Exception:
        return {"peak_bytes": None, "method": None, "scope": "process_lifetime_peak", "unavailable": True}


def dependency_versions() -> dict[str, str | None]:
    versions: dict[str, str | None] = {}
    for name in ("gestureforge", "PySide6", "opencv-contrib-python", "mediapipe", "numpy", "scikit-learn"):
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = None
    return versions


def _provenance(config: DiagnosticConfig) -> dict[str, Any]:
    return {
        "source_commit": _git_output("rev-parse", "HEAD"),
        "source_dirty": _source_dirty(),
        "source_sha256": {
            "check_stability.py": _file_sha256(ROOT / "scripts" / "check_stability.py"),
            "app.py": _file_sha256(ROOT / "gestureforge" / "app.py"),
            "capture.py": _file_sha256(ROOT / "gestureforge" / "capture.py"),
            "features.py": _file_sha256(ROOT / "gestureforge" / "features.py"),
            "models.py": _file_sha256(ROOT / "gestureforge" / "models.py"),
        },
        "asset_sha256": _file_sha256(config.asset),
        "dataset_sha256": None if config.dataset is None else _file_sha256(config.dataset),
    }


def _windows_peak_memory() -> dict[str, Any]:
    try:
        import ctypes
        from ctypes import wintypes

        # GetProcessMemoryInfo returns process-lifetime peak working set size.
        # https://learn.microsoft.com/en-us/windows/win32/api/psapi/nf-psapi-getprocessmemoryinfo
        class ProcessMemoryCounters(ctypes.Structure):
            _fields_ = [
                ("cb", wintypes.DWORD),
                ("PageFaultCount", wintypes.DWORD),
                ("PeakWorkingSetSize", ctypes.c_size_t),
                ("WorkingSetSize", ctypes.c_size_t),
                ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPagedPoolUsage", ctypes.c_size_t),
                ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                ("PagefileUsage", ctypes.c_size_t),
                ("PeakPagefileUsage", ctypes.c_size_t),
            ]

        counters = ProcessMemoryCounters()
        counters.cb = ctypes.sizeof(ProcessMemoryCounters)
        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        psapi = ctypes.WinDLL("psapi", use_last_error=True)
        kernel32.GetCurrentProcess.argtypes = []
        kernel32.GetCurrentProcess.restype = wintypes.HANDLE
        psapi.GetProcessMemoryInfo.argtypes = [
            wintypes.HANDLE,
            ctypes.POINTER(ProcessMemoryCounters),
            wintypes.DWORD,
        ]
        psapi.GetProcessMemoryInfo.restype = wintypes.BOOL
        process = kernel32.GetCurrentProcess()
        ok = psapi.GetProcessMemoryInfo(
            process,
            ctypes.byref(counters),
            counters.cb,
        )
        if not ok:
            return {
                "peak_bytes": None,
                "method": "GetProcessMemoryInfo",
                "scope": "process_lifetime_peak",
                "unavailable": True,
            }
        return {
            "peak_bytes": int(counters.PeakWorkingSetSize),
            "method": "GetProcessMemoryInfo",
            "scope": "process_lifetime_peak",
        }
    except Exception:
        return {
            "peak_bytes": None,
            "method": "GetProcessMemoryInfo",
            "scope": "process_lifetime_peak",
            "unavailable": True,
        }


def _camera_index(value: str) -> int:
    try:
        index = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("camera must be a non-negative integer") from exc
    try:
        validate_camera_index(index)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc
    return index


def _duration(value: str) -> int:
    try:
        seconds = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("seconds must be an integer") from exc
    if seconds < MIN_DURATION_SECONDS or seconds > MAX_DURATION_SECONDS:
        raise argparse.ArgumentTypeError("seconds must be between 1 and 1800")
    return seconds


def _positive_float(value: str) -> float:
    try:
        number = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("value must be a finite positive number") from exc
    if not math.isfinite(number) or number <= 0:
        raise argparse.ArgumentTypeError("value must be a finite positive number")
    return number


def _margin(value: str) -> float:
    number = _positive_float(value)
    if number < 1.0:
        raise argparse.ArgumentTypeError("margin must be finite and at least 1.0")
    return number


def _same_path(left: Path, right: Path) -> bool:
    try:
        return left.resolve() == right.resolve()
    except OSError:
        return left.absolute() == right.absolute()


def _file_sha256(path: Path) -> str | None:
    try:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()
    except OSError:
        return None


def _json_sha256(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, default=str).encode("utf-8")).hexdigest()


def _text_sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _git_output(*args: str) -> str | None:
    try:
        completed = subprocess.run(
            ["git", *args],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if completed.returncode != 0:
        return None
    return completed.stdout.strip()


def _source_dirty() -> bool | None:
    status = _git_output("status", "--porcelain")
    if status is None:
        return None
    return bool(status)


def _safe_error(value: str) -> str:
    if not value:
        return ""
    head = value.split(":", 1)[0].strip()
    if re.fullmatch(r"[A-Za-z]+Error", head):
        return head
    return "capture_error"


def _rounded(value: float) -> float:
    return round(float(value), 6)


def _max_rounded(current: float | None, candidate: float) -> float:
    rounded = _rounded(candidate)
    return rounded if current is None else max(current, rounded)


def main(argv: list[str] | None = None) -> int:
    try:
        config = parse_args(argv)
        report = run_diagnostic(config)
    except (OSError, ValueError) as exc:
        raise SystemExit(f"check_stability: {exc}") from exc
    return 0 if report["status"]["completed_diagnostic"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
