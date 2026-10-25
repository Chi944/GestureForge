"""Guide twenty five-second holds using Studio's real simulated controller path.

Cue times are instructions, not observed stable-pose onsets. This tool does not
qualify a profile or score latency; original traces need independent annotation.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass, field
import hashlib
from pathlib import Path
import sys
import time
from typing import Any

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget

from gestureforge.app import Window, validate_camera_index
from gestureforge.capture import DEFAULT_ASSET
from gestureforge.contracts import RoutingMode, RoutingSnapshot
from gestureforge.features import extract_feature_vector
from gestureforge.profiles import ProfileStore
from gestureforge.storage import atomic_write_json


@dataclass
class HoldSequence:
    """Instruction clock only: never substitutes cues for observed hand motion."""

    actions: tuple[str, ...]
    started: float
    phase_started: float = field(init=False)
    phase: str = "neutral"
    completed: int = 0
    reason: str = ""
    cues: list[dict] = field(default_factory=list)

    def __post_init__(self) -> None:
        if len(self.actions) != 3 or len(set(self.actions)) != 3:
            raise ValueError("three distinct action poses are required")
        self.phase_started = self.started
        self.cues.append({"kind": "neutral", "timestamp": self.started, "before_hold": 1})

    def advance(self, now: float, *, ready: bool, capture_ok: bool) -> None:
        if self.phase in {"complete", "interrupted"}:
            return
        if not capture_ok:
            self.interrupt("Capture, focus or configuration interrupted", now)
            return
        elapsed = now - self.phase_started
        if self.phase == "neutral":
            if elapsed >= 3 and ready:
                self.phase = "form"
                self.phase_started = now
                self.cues.append({"kind": "form", "timestamp": now,
                                  "hold": self.completed + 1,
                                  "command": self.actions[self.completed % 3]})
            elif elapsed >= 30:
                self.interrupt("NEUTRAL did not reach READY within 30 seconds", now)
        elif self.phase == "form" and elapsed >= 1:
            self.phase = "hold"
            self.phase_started = now
            self.cues.append({"kind": "hold", "timestamp": now,
                              "hold": self.completed + 1,
                              "command": self.actions[self.completed % 3], "requested_seconds": 5})
        elif self.phase == "hold" and elapsed >= 5:
            self.cues.append({"kind": "release", "timestamp": now, "hold": self.completed + 1})
            self.completed += 1
            self.phase = "complete" if self.completed == 20 else "neutral"
            self.phase_started = now
            if self.phase == "neutral":
                self.cues.append({"kind": "neutral", "timestamp": now,
                                  "before_hold": self.completed + 1})

    def interrupt(self, reason: str, now: float) -> None:
        if self.phase not in {"complete", "interrupted"}:
            self.phase = "interrupted"
            self.reason = reason
            self.cues.append({"kind": "interrupted", "timestamp": now, "reason": reason})

    def report(self) -> dict:
        return {"schema_version": 1, "protocol": "GF-P20-twenty-holds-v1",
                "status": self.phase, "reason": self.reason,
                "requested_holds": 20, "completed_cue_windows": self.completed,
                "capture_passed": None, "annotation_complete": False,
                "latency_measured": False, "cues": self.cues,
                "limitations": ["Cue timestamps are not observed stable-pose onsets.",
                                "All controller actions are simulated; no external launches.",
                                "Completed cues do not establish correct physical holds or a pass."]}


class GuidedWindow(Window):
    def __init__(self, loaded, store: ProfileStore, camera: int, output: Path):
        record = loaded.record
        settings = record.settings
        super().__init__(
            loaded.model, extract_feature_vector, record.selected_hand, camera,
            DEFAULT_ASSET, record.profile_id, "GF-P20 controller evaluation: simulated actions only",
            studio=True, studio_mode=RoutingMode.REHEARSAL, vocabulary=record.vocabulary,
            model_settings=(settings.algorithm, settings.multiplier, settings.margin),
            profile_display_name=record.display_name, profile_store=store, loaded_profile=loaded,
        )
        self.setWindowTitle("GestureForge | GF-P20 guided holds")
        self.output = output
        self.trace_folder = output
        self.hold_sequence: HoldSequence | None = None
        self.capture_worker: Any = None
        self.capture_snapshot: RoutingSnapshot | None = None
        self.last_cue_count = 0
        self.last_tick = 0.0
        self.names = dict(record.gesture_names)
        assert self.routing is not None
        self.expected_snapshot = self.routing.snapshot
        self.finished_evidence = False
        self.metadata = {"profile_id": record.profile_id,
                         "model_version": record.model_version,
                         "manifest_sha256": record.manifest_sha256,
                         "features_sha256": record.features_sha256,
                         "camera": camera, "hand": record.selected_hand,
                         "source_sha256": {str(p.name): hashlib.sha256(p.read_bytes()).hexdigest()
                                           for p in (Path(__file__), Path(__file__).resolve().parents[1]
                                                     / "gestureforge" / "app.py")},
                         "settings": {"algorithm": settings.algorithm,
                                      "multiplier": settings.multiplier, "margin": settings.margin}}
        panel = QWidget()
        layout = QVBoxLayout(panel)
        self.cue = QLabel("20 holds · 5 seconds each · about 3–5 minutes\n"
                          "Start when ready. Keep this window focused; Esc stops and saves an incomplete run.")
        self.cue.setWordWrap(True)
        self.cue.setStyleSheet("background:#173548;color:#ffffff;font-size:20px;padding:12px;")
        self.begin_holds = QPushButton("Start guided 20-hold test")
        self.begin_holds.clicked.connect(self.start_holds)
        layout.addWidget(self.cue)
        layout.addWidget(self.begin_holds)
        central = self.centralWidget()
        assert central is not None
        shell_layout = central.layout()
        assert isinstance(shell_layout, QVBoxLayout)
        shell_layout.insertWidget(0, panel)
        self.hold_timer = QTimer(self)
        self.hold_timer.timeout.connect(self.tick_holds)
        self.start_button.setEnabled(False)
        atomic_write_json(output / "run.json", {**self.metadata, "status": "not_started",
                                                "capture_passed": None})

    def start_holds(self) -> None:
        if self.hold_sequence is not None:
            if self.hold_sequence.phase in {"complete", "interrupted"}:
                self.finish_holds()
            return
        if self.worker is not None:
            return
        assert self.routing is not None
        if (self.routing.snapshot != self.expected_snapshot or self.runbook is not None
                or self.camera_index != self.metadata["camera"]
                or self.chosen_hand != self.metadata["hand"]):
            self.cue.setText("Restart this dedicated runner; its fixed simulated context was changed.")
            return
        self.record_trace.setChecked(True)
        self.record_diagnostics.setChecked(False)
        self.start_camera()
        now = time.monotonic()
        self.hold_sequence = HoldSequence(tuple(self.vocabulary.action_ids), now)
        self.capture_worker = self.worker
        self.capture_snapshot = self.routing.snapshot
        self.last_tick = now
        self.begin_holds.setEnabled(False)
        self.deck_tabs.setEnabled(False)
        self.next_button.setEnabled(False)
        self.reset_button.setEnabled(False)
        self.record_trace.setEnabled(False)
        if self.worker is None or self.evaluation_trace is None:
            self.hold_sequence.interrupt("Camera did not start; no trial was performed", now)
            self.finish_holds()
            return
        if not self.save_cues():
            return
        self.hold_timer.start(50)
        self.render_cue(now)

    def tick_holds(self) -> None:
        sequence = self.hold_sequence
        if sequence is None:
            return
        now = time.monotonic()
        assert self.routing is not None
        worker: Any = self.worker
        capture_ok = bool(worker is not None and worker is self.capture_worker
                          and not worker.isFinished() and not worker.isInterruptionRequested()
                          and self.routing.snapshot == self.capture_snapshot
                          and self.isActiveWindow() and now - self.last_tick <= 1.0
                          and self.evaluation_trace is not None
                          and not any(o.source == "manual" for o in self.session_summary.outcomes))
        self.last_tick = now
        sequence.advance(now, ready=self.received_first_frame and self.routing.state == "READY",
                         capture_ok=capture_ok)
        if sequence.phase in {"complete", "interrupted"}:
            self.finish_holds()
            return
        if len(sequence.cues) != self.last_cue_count and not self.save_cues():
            return
        self.render_cue(now)

    def render_cue(self, now: float) -> None:
        sequence = self.hold_sequence
        assert sequence is not None
        if sequence.phase == "hold":
            action = sequence.actions[sequence.completed % 3]
            remaining = max(0.0, 5 - (now - sequence.phase_started))
            self.cue.setText(f"Hold {sequence.completed + 1}/20: {action} — {self.names[action]}\n"
                             f"Keep it steady for {remaining:.1f} s. Do not return to NEUTRAL yet.")
        elif sequence.phase == "form":
            action = sequence.actions[sequence.completed % 3]
            self.cue.setText(f"Hold {sequence.completed + 1}/20: form {action} — {self.names[action]} NOW\n"
                             "The five-second steady hold starts next. Early actions remain in the trace.")
        else:
            action = sequence.actions[sequence.completed % 3]
            self.cue.setText(f"Prepare hold {sequence.completed + 1}/20: NEUTRAL — {self.names['NEUTRAL']}\n"
                             f"Keep your open palm steady. Next: {action} — {self.names[action]}.")

    def offer_save_retry(self) -> None:
        self.begin_holds.setText("Retry saving this test (does not repeat holds)")
        self.begin_holds.setEnabled(True)

    def save_cues(self) -> bool:
        assert self.hold_sequence is not None
        try:
            atomic_write_json(self.output / "run.json", {**self.metadata, **self.hold_sequence.report()})
            self.last_cue_count = len(self.hold_sequence.cues)
            return True
        except (OSError, ValueError) as exc:
            self.hold_timer.stop()
            self.hold_sequence.interrupt("Cue recording failed", time.monotonic())
            self.pause()
            self.cue.setText(f"Recording stopped: {exc}. Keep this window open; no pass is claimed.")
            self.offer_save_retry()
            return False

    def finish_holds(self) -> None:
        if self.finished_evidence:
            return
        self.hold_timer.stop()
        assert self.hold_sequence is not None
        if not self.pause():
            self.cue.setText("Trace could not be saved. Keep Studio open and use Pause to retry; review required.")
            self.offer_save_retry()
            return
        if not self.save_cues():
            return
        try:
            self.session_summary.export(self.output / "session-summary.json")
        except (OSError, ValueError) as exc:
            self.cue.setText(f"Summary export failed: {exc}. Keep this window open; no pass is claimed.")
            self.offer_save_retry()
            return
        self.finished_evidence = True
        self.begin_holds.setEnabled(False)
        status = "Captured all 20 cue windows" if self.hold_sequence.phase == "complete" else "Test interrupted"
        self.cue.setText(f"{status}. Review needed — no automatic pass.\n"
                         f"{self.hold_sequence.reason}\nSaved in {self.output}")

    def closeEvent(self, event) -> None:
        if self.hold_sequence is not None and not self.finished_evidence:
            self.hold_sequence.interrupt("Window closed before test completion", time.monotonic())
            self.finish_holds()
            if not self.finished_evidence:
                event.ignore()
                return
        super().closeEvent(event)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile-id", required=True)
    parser.add_argument("--camera", type=int, default=1)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--smoke-test", action="store_true")
    args = parser.parse_args(argv)
    validate_camera_index(args.camera)
    store = ProfileStore(Path(".local/profiles"))
    loaded = store.load(args.profile_id)
    args.output_dir.mkdir(parents=True, exist_ok=False)
    app = QApplication(sys.argv[:1])
    window = GuidedWindow(loaded, store, args.camera, args.output_dir.resolve())
    window.show()
    window.raise_()
    window.activateWindow()
    if args.smoke_test:
        QTimer.singleShot(500, window.close)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
