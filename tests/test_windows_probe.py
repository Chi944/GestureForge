"""Probe shutdown must not destroy a still-running capture worker."""
import os
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import Mock

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')

from PySide6.QtWidgets import QApplication

from scripts.windows_launch_probe import ProbeWindow


def test_probe_close_waits_for_capture(tmp_path):
    app = QApplication.instance() or QApplication([])
    window = ProbeWindow('test-laptop', tmp_path / 'probe.json', 0, tmp_path / 'unused.task')
    worker = SimpleNamespace(isFinished=lambda: False, requestInterruption=Mock(),
                             wait=Mock(side_effect=[False, True]))
    window.worker = cast(Any, worker)
    try:
        assert not window.close()
        assert window.timer.isActive()
        assert not any(row['kind'] == 'probe_closed' for row in window.rows)
        assert window.close()
        assert not window.timer.isActive()
        assert worker.requestInterruption.call_count == 2
        assert window.rows[-1]['kind'] == 'probe_closed'
        assert app is not None
    finally:
        window.worker = None
        window.close()


def test_probe_confirmation_requires_pending_accepted_launch(tmp_path):
    app = QApplication.instance() or QApplication([])
    window = ProbeWindow('test-laptop', tmp_path / 'probe.json', 0, tmp_path / 'unused.task')
    try:
        window.confirm(True)
        assert window.rows[-1]['kind'] == 'observer_confirmation_refused'
        assert not any(row['kind'] == 'observer_confirmation' for row in window.rows)

        window.pending_confirmation_event_id = 'accepted-event'
        window.confirm(True)
        assert window.rows[-1] == {
            'kind': 'observer_confirmation',
            'monotonic': window.rows[-1]['monotonic'],
            'event_id': 'accepted-event',
            'visible': True,
        }
        window.confirm(False)
        assert window.rows[-1]['kind'] == 'observer_confirmation_refused'
        assert app is not None
    finally:
        window.close()


def test_probe_records_pre_dispatch_validation_failure(tmp_path):
    app = QApplication.instance() or QApplication([])
    window = ProbeWindow('test-laptop', tmp_path / 'probe.json', 0, tmp_path / 'unused.task')
    try:
        window.pending_confirmation_event_id = 'older-launch'
        window.validation_failed('reference', 'file does not exist')
        assert window.pending_confirmation_event_id is None
        assert window.rows[-1]['kind'] == 'target_validation_failed'
        assert window.rows[-1]['target_id'] == 'reference'
        assert window.rows[-1]['reason'] == 'file does not exist'
        assert app is not None
    finally:
        window.close()
