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
