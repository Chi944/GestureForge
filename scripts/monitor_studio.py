"""Opt-in real Studio aggregate monitor; run with python -m scripts.monitor_studio.

Open/select a profile and operate Studio normally, then close it normally. No camera
is started by this script. Checkpoints describe incomplete/unknown exits until an
accepted window close. This is measurement evidence, not workflow acceptance.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass, field
import json
import math
import os
from pathlib import Path
import sys
import time
from typing import Any

from gestureforge.traces import _write_json_exclusive
from scripts.check_stability import current_process_peak_memory


@dataclass
class Monitor:
    started: float
    requested_seconds: float
    workers: list[Any] = field(default_factory=list, repr=False)
    frames: list[int] = field(default_factory=list)
    last_frames: list[float | None] = field(default_factory=list)
    max_frame_gap: float = 0.0
    heartbeat_count: int = 0
    max_heartbeat_gap: float = 0.0
    active_max_heartbeat_gap: float = 0.0
    active_seconds: float = 0.0
    normal_close: bool = False
    last_tick: float | None = None
    capacity_exceeded: bool = False
    longest_contiguous_seconds: float = 0.0
    segment_generation: int | None = None
    segment_started: float | None = None
    running_generations: set[int] = field(default_factory=set)

    def __post_init__(self) -> None:
        if not math.isfinite(self.requested_seconds) or self.requested_seconds <= 0:
            raise ValueError("seconds must be finite and positive")
        self.last_tick = self.started

    def tick(self, now: float) -> None:
        assert self.last_tick is not None
        gap = max(0.0, now - self.last_tick)
        self.max_heartbeat_gap = max(self.max_heartbeat_gap, gap)
        running = {index for index, worker in enumerate(self.workers) if not worker.isFinished()}
        still_running = running & self.running_generations
        if still_running:
            self.active_seconds += gap
        if any(self.last_frames[index] is not None for index in still_running):
            self.active_max_heartbeat_gap = max(self.active_max_heartbeat_gap, gap)
        for index, (worker, previous) in enumerate(zip(self.workers, self.last_frames, strict=True)):
            if previous is not None and index in running:
                self.max_frame_gap = max(self.max_frame_gap, now - previous)
            if self.segment_generation == index and (
                index not in running or (previous is not None and now - previous > 2.0)
            ):
                self.segment_generation = None
                self.segment_started = None
        self.running_generations = running
        self.last_tick = now
        self.heartbeat_count += 1

    def event(self, kind: str, worker: Any, now: float) -> None:
        self.tick(now)
        if kind == "normal_close":
            self.normal_close = True
            return
        index = next((i for i, known in enumerate(self.workers) if known is worker), None)
        if index is None:
            if len(self.workers) >= 256:
                self.capacity_exceeded = True
                return
            self.workers.append(worker)
            self.frames.append(0)
            self.last_frames.append(None)
            index = len(self.workers) - 1
        if not worker.isFinished():
            self.running_generations.add(index)
        if kind == "worker_started":
            # A restart ends continuity, even if generations overlap.
            self.segment_generation = None
            self.segment_started = None
        if kind == "observation":
            if self.segment_generation != index:
                self.segment_generation = index
                self.segment_started = now
            assert self.segment_started is not None
            self.longest_contiguous_seconds = max(
                self.longest_contiguous_seconds, now - self.segment_started,
            )
            previous = self.last_frames[index]
            if previous is not None:
                self.max_frame_gap = max(self.max_frame_gap, now - previous)
            self.last_frames[index] = now
            self.frames[index] += 1

    def progress_text(self) -> str:
        continuous = 0.0
        if self.segment_generation is not None and self.segment_started is not None:
            last = self.last_frames[self.segment_generation]
            if last is not None:
                continuous = max(0.0, last - self.segment_started)
        state = "Receiving frames" if self.segment_generation is not None else "Waiting / paused"
        remaining = max(0.0, self.requested_seconds - continuous)
        return (f"Stability: {state} | continuous {continuous:.1f}s / {self.requested_seconds:g}s"
                f" | remaining {remaining:.1f}s | received {sum(self.frames)} frames"
                " | close normally when finished; no automatic stop")

    def report(self, now: float, *, finalized: bool = False,
               qt_exit_code: int | None = None) -> dict[str, Any]:
        elapsed = max(0.0, now - self.started)
        total = sum(self.frames)
        released = all(worker.isFinished() for worker in self.workers)
        errors = sum(bool(worker.error) for worker in self.workers)
        unexpected = sum(worker.isFinished() and not worker.isInterruptionRequested()
                         for worker in self.workers)
        memory = current_process_peak_memory()
        problems = []
        if finalized and qt_exit_code != 0:
            problems.append("qt_event_loop_exit_not_successful")
        if memory.get("peak_bytes") is None or memory.get("unavailable", False):
            problems.append("peak_process_memory_unavailable")
        if not finalized or not self.normal_close:
            problems.append("normal_window_close_not_confirmed")
        if self.longest_contiguous_seconds < self.requested_seconds:
            problems.append("requested_contiguous_capture_duration_not_reached")
        if not total:
            problems.append("no_delivered_observations")
        if self.active_max_heartbeat_gap > 2.0:
            problems.append("gui_gap_over_2_seconds")
        if self.max_frame_gap > 2.0:
            problems.append("delivered_observation_gap_over_2_seconds")
        if errors or unexpected:
            problems.append("worker_error_or_unexpected_stop")
        if not released:
            problems.append("worker_release_not_confirmed")
        if self.capacity_exceeded:
            problems.append("generation_capacity_exceeded")
        return {
            "schema_version": 1,
            "kind": "real_studio_aggregate_monitor",
            "status": "final" if finalized else "incomplete_checkpoint",
            "exit_outcome": "observed_normal_window_close" if self.normal_close else "unknown",
            "qt_event_loop_exit_code": qt_exit_code if finalized else None,
            "requested_seconds": self.requested_seconds,
            "elapsed_seconds": elapsed,
            "camera_active_seconds_estimate": self.active_seconds,
            "longest_contiguous_delivered_seconds": self.longest_contiguous_seconds,
            "camera_paused_seconds_estimate": max(0.0, elapsed - self.active_seconds),
            "activity_sampling_seconds": 0.1,
            "delivered_observations": total,
            "delivered_rate_per_camera_active_second": total / self.active_seconds if self.active_seconds else None,
            "generation_observation_counts": self.frames.copy(),
            "gui_heartbeat_count": self.heartbeat_count,
            "gui_max_gap_seconds": self.max_heartbeat_gap,
            "active_gui_max_gap_seconds": self.active_max_heartbeat_gap,
            "delivered_max_gap_seconds_within_generation": self.max_frame_gap,
            "worker_error_count": errors,
            "unexpected_worker_stop_count": unexpected,
            "all_workers_released": released,
            "early_close": self.normal_close and self.longest_contiguous_seconds < self.requested_seconds,
            "measurement_criteria_met": not problems,
            "unmet_measurement_criteria": problems,
            "memory": memory,
            "limitations": ["Not recognition accuracy or full workflow acceptance.",
                            "Delivered frames only; no raw camera frame-rate claim.",
                            "Active time is sampled; an interval ending with worker release is unmeasured, not an active gap.",
                            "A checkpoint cannot establish subsequent process exit or camera release.",
                            "Camera reopen after close requires a separate native check."],
        }


class ReportFile:
    """Reserve once; replace only our own report, keeping one bounded checkpoint."""

    def __init__(self, path: Path, initial: dict[str, Any]):
        self.path = path
        self.previous = json.dumps(initial, indent=2, sort_keys=True) + "\n"
        _write_json_exclusive(path, initial)

    def save(self, report: dict[str, Any]) -> None:
        if self.path.read_text(encoding="utf-8") != self.previous:
            raise ValueError("monitor output changed externally; refusing replacement")
        text = json.dumps(report, indent=2, sort_keys=True) + "\n"
        temporary = self.path.with_name(self.path.name + ".tmp")
        # Exclusive creation also refuses unrelated temporary files.
        with temporary.open("x", encoding="utf-8") as handle:
            handle.write(text)
        try:
            os.replace(temporary, self.path)
        finally:
            temporary.unlink(missing_ok=True)
        self.previous = text


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seconds", type=float, default=1800)
    parser.add_argument("--camera", type=int, default=0)
    args = parser.parse_args(argv)
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication
    from gestureforge.app import Window, validate_camera_index
    from gestureforge.capture import DEFAULT_ASSET
    from gestureforge.features import extract_feature_vector
    from gestureforge.profiles import ProfileStore

    validate_camera_index(args.camera)
    monitor = Monitor(time.monotonic(), args.seconds)
    output = ReportFile(args.output, monitor.report(time.monotonic()))
    app = QApplication(sys.argv[:1])
    window = Window(feature_function=extract_feature_vector, camera_index=args.camera,
                    asset=DEFAULT_ASSET, studio=True, profile_store=ProfileStore(Path(".local/profiles")))
    window.measurement.connect(lambda kind, worker: monitor.event(kind, worker, time.monotonic()))
    window.statusBar().showMessage(monitor.progress_text())
    failed = False
    last_saved = monitor.started

    def tick() -> None:
        nonlocal failed, last_saved
        now = time.monotonic()
        monitor.tick(now)
        window.statusBar().showMessage(
            "Stability: output failed; no measurement pass." if failed else monitor.progress_text()
        )
        if now - last_saved >= 5 and not failed:
            try:
                output.save(monitor.report(now))
                last_saved = now
            except (OSError, ValueError):
                failed = True
                print("Monitor output failed; no measurement pass can be claimed. Studio is unchanged.", file=sys.stderr)

    timer = QTimer()
    timer.timeout.connect(tick)
    timer.start(100)
    window.show()
    print("Monitor running. Operate Studio normally, then close it. No camera starts automatically.")
    code = app.exec()
    timer.stop()
    monitor.tick(time.monotonic())
    if failed:
        return 1
    report = monitor.report(time.monotonic(), finalized=True, qt_exit_code=code)
    try:
        output.save(report)
    except (OSError, ValueError):
        print("Final report could not be saved; retained checkpoint is incomplete.", file=sys.stderr)
        return 1
    return code if report["measurement_criteria_met"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
