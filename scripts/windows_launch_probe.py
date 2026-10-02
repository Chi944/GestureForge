"""GF-P05/P19 isolated Windows probe; no gestures launch anything.

Run: python -m scripts.windows_launch_probe --laptop-id laptop-A
This uses the existing CaptureWorker and actual HandCamera, without recognition.
Only explicit button requests open targets. Evidence needs observer confirmation.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import importlib.metadata
from pathlib import Path
import platform
import sys
import time
from typing import Any
from uuid import uuid4

from PySide6.QtCore import QEvent, QTimer
from PySide6.QtWidgets import QApplication, QHBoxLayout, QMainWindow, QPushButton, QVBoxLayout, QWidget

from gestureforge.app import CaptureWorker
from gestureforge.capture import DEFAULT_ASSET
from gestureforge.contracts import Action, ActionType, RoutingMode, RoutingSnapshot, validate_identifier
from gestureforge.dispatcher import Dispatcher
from gestureforge.javier_widgets import QuickActionsWidget, plain_label
from gestureforge.routing import RoutingSession
from gestureforge.shortcuts import Target, TargetKind, TargetRegistry, WindowsLauncher
from gestureforge.storage import atomic_write_json


class NoRecognition:
    model_version = 'isolated-probe'

    def predict(self, features: Any) -> tuple[str, bool, str]:
        return 'UNKNOWN', False, 'manual_probe_only'


class ProbeWindow(QMainWindow):
    def __init__(self, laptop_id: str, output: Path, camera: int, asset: Path) -> None:
        super().__init__()
        self.setWindowTitle('GestureForge — isolated Windows launch and capture probe')
        self.resize(1100, 880)
        self.output, self.camera, self.asset = output, camera, asset
        self.worker: CaptureWorker | None = None
        self.captured_frames = 0
        self.rows: list[dict[str, object]] = []
        self.pending_confirmation_event_id: str | None = None
        self.environment = {
            'laptop_id': laptop_id, 'platform': platform.platform(), 'python': platform.python_version(),
            'utc': datetime.now(timezone.utc).isoformat(), 'camera_index': camera,
            'versions': {name: importlib.metadata.version(name) for name in ['PySide6', 'opencv-contrib-python', 'mediapipe']},
            'limitations': ['Observer confirmations are self-reported.',
                            'Probe is separate from the assignment/Studio shell.',
                            'No gesture launches or recognition performance are tested.'],
        }
        self.session = RoutingSession('probe', 'isolated-probe', 'targets',
                                      {'G1': Action(ActionType.NEXT)}, RoutingMode.LIVE)
        registry = TargetRegistry()
        registry.configure(Target('calculator', 'Calculator', TargetKind.BUILTIN, 'calculator'))
        registry.configure(Target('camera', 'Camera — start capture before testing', TargetKind.BUILTIN, 'camera'))
        self.gate = Dispatcher(registry, WindowsLauncher(), lambda: self.session.snapshot,
                               lambda: self.session.state != 'PAUSED', lambda snapshot: False,
                               self.pause, self.release_capture)
        body = QWidget()
        layout = QVBoxLayout(body)
        self.message = plain_label('MANUAL PROBE ONLY. Start capture, then test Camera. Local target buttons request one OS launch.')
        layout.addWidget(self.message)
        controls = QHBoxLayout()
        for label, callback in [('Start / resume capture explicitly', self.start_capture),
                                ('Pause', self.pause), ('Confirm visible opening', lambda: self.confirm(True)),
                                ('Confirm failed / not visible', lambda: self.confirm(False)),
                                ('Record manual recovery / return', lambda: self.record('manual_return_recovery'))]:
            button = QPushButton(label)
            button.clicked.connect(callback)
            controls.addWidget(button)
        layout.addLayout(controls)
        self.quick = QuickActionsWidget(registry)
        self.quick.action_requested.connect(self.launch)
        self.quick.target_validation_failed.connect(self.validation_failed)
        self.quick.focus_lost.connect(self.pause)
        layout.addWidget(self.quick)
        self.setCentralWidget(body)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.poll_capture)
        self.timer.start(80)
        self.record('probe_started')

    def record(self, kind: str, **values: object) -> None:
        self.rows.append({'kind': kind, 'monotonic': time.monotonic(), **values})
        try:
            atomic_write_json(self.output, {'schema_version': 1, 'environment': self.environment,
                                            'events': self.rows})
        except (OSError, ValueError) as exc:
            self.message.setText(f'Could not save evidence: {exc}. Choose a writable output directory.')

    def start_capture(self) -> None:
        if self.worker is not None and not self.worker.isFinished():
            self.message.setText('Capture already running. Pause and return manually after launching another application.')
            return
        self.session.resume()
        self.captured_frames = 0
        self.worker = CaptureWorker(NoRecognition(), None, 'Right', self.camera, self.asset,
                                    self.session.snapshot.session_id, 'probe')
        self.worker.start()
        self.record('capture_start_requested')
        self.message.setText('Waiting for actual capture frames; Camera opening is blocked until a frame arrives.')

    def poll_capture(self) -> None:
        if self.worker is None:
            return
        if self.worker.take_latest() is not None:
            self.captured_frames += 1
            if self.captured_frames == 1:
                self.record('capture_frame_received')
                self.message.setText('Actual GestureForge capture frame received. Camera handoff may now be tested.')
        if self.worker.error:
            self.message.setText(f'Capture error: {self.worker.error}. Check permissions, asset and competing camera consumers.')
            self.record('capture_error', reason=self.worker.error)
            self.worker.error = ''
            self.pause()

    def pause(self) -> None:
        was_active = self.session.state != 'PAUSED'
        self.session.pause()
        if was_active:
            self.record('paused')
        self.message.setText('Paused. Return manually, close competing Camera if needed, then explicitly resume capture.')

    def release_capture(self, snapshot: RoutingSnapshot) -> bool:
        worker = self.worker
        if worker is None or worker.isFinished() or self.captured_frames == 0:
            self.record('camera_handoff_refused', reason='start capture and verify a real frame first')
            return False
        worker.requestInterruption()
        acknowledged = worker.wait(5000)
        self.record('capture_shutdown_acknowledged' if acknowledged else 'capture_shutdown_timeout',
                    captured_frames=self.captured_frames)
        return bool(acknowledged and not worker.error and snapshot == self.session.snapshot)

    def launch(self, action: Action) -> None:
        result = self.gate.manual(str(uuid4()), action)
        self.record('dispatch', target_id=action.shortcut_id, status=result.status, reason=result.reason,
                    event_id=result.event_id)
        self.pending_confirmation_event_id = result.event_id if result.status == 'launch_requested' else None
        self.message.setText(f'{result.status}: {result.reason or "OS request accepted; observe the actual application and confirm its visible result."}')

    def validation_failed(self, target_id: str, reason: str) -> None:
        self.pending_confirmation_event_id = None
        self.record('target_validation_failed', target_id=target_id, reason=reason)

    def confirm(self, visible: bool) -> None:
        if self.pending_confirmation_event_id is None:
            reason = 'no accepted launch is awaiting observer confirmation'
            self.record('observer_confirmation_refused', reason=reason)
            self.message.setText(f'Cannot record observer result: {reason}. Test the target again.')
            return
        event_id = self.pending_confirmation_event_id
        self.pending_confirmation_event_id = None
        self.record('observer_confirmation', event_id=event_id, visible=visible)
        self.message.setText('Observer result recorded. Returning never resumes capture automatically.')

    def changeEvent(self, event: QEvent) -> None:
        if event.type() == QEvent.Type.ActivationChange and not self.isActiveWindow():
            self.pause()
        super().changeEvent(event)

    def closeEvent(self, event: Any) -> None:
        if self.worker and not self.worker.isFinished():
            self.worker.requestInterruption()
            acknowledged = self.worker.wait(5000)
            self.record('probe_close_shutdown', acknowledged=acknowledged)
            if not acknowledged:
                self.message.setText('Camera shutdown is still in progress. Keep this window open and retry closing after capture stops.')
                event.ignore()
                return
        self.timer.stop()
        self.record('probe_closed')
        super().closeEvent(event)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--laptop-id', required=True)
    parser.add_argument('--output', type=Path, default=Path('.local/windows-probe.json'))
    parser.add_argument('--camera', type=int, default=0)
    parser.add_argument('--asset', type=Path, default=DEFAULT_ASSET)
    args = parser.parse_args()
    validate_identifier(args.laptop_id)
    if sys.platform != 'win32':
        parser.error('this probe requires an actual Windows machine; no Windows evidence was recorded')
    app = QApplication(sys.argv[:1])
    window = ProbeWindow(args.laptop_id, args.output, args.camera, args.asset)
    window.show()
    return app.exec()


if __name__ == '__main__':
    raise SystemExit(main())
