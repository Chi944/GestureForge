import pytest

from gestureforge.app import Window
from gestureforge.contracts import Action, ActionType
from gestureforge.vocabulary import GestureVocabulary
from test_app_personal_live import grant, model, passed_result
from test_app_readiness import FakeWorker, FailingTrace, pass_readiness
from test_app_starter import release_fake_worker, standard_window


@pytest.fixture(scope="module")
def qapp():
    from PySide6.QtWidgets import QApplication

    yield QApplication.instance() or QApplication([])


@pytest.fixture(params=["personal", "standard"])
def granted_window(request, qapp, tmp_path, monkeypatch):
    import gestureforge.app as app_module

    monkeypatch.setattr(app_module, "DEFAULT_STUDIO_STATE_FOLDER", tmp_path / "studio")
    monkeypatch.setattr(Window, "log", lambda self, record: None)
    if request.param == "standard":
        window = standard_window(qapp)
        pass_readiness(window, monkeypatch)
        release_fake_worker(window)
    else:
        window = Window(model=model(), studio=True, vocabulary=GestureVocabulary(("G1", "G2", "G3")))
        assert grant(window, passed_result(window), tmp_path)
    try:
        yield window, f"_{request.param}_live_grant"
    finally:
        if window.evaluation_trace is not None:
            window.evaluation_trace.fail = False
        window.close()


def test_same_camera_apply_pauses_and_retries_trace_without_revoking_grant(granted_window, tmp_path):
    window, grant_name = granted_window
    accepted = getattr(window, grant_name)
    assert accepted is not None
    window.routing.resume()
    worker = FakeWorker()
    window.worker = worker
    trace = FailingTrace()
    window.evaluation_trace = trace
    window.trace_path = tmp_path / "trace.json"

    assert not window.set_studio_camera(window.camera_index)
    assert worker.interrupted and window.routing.state == "PAUSED"
    assert window.evaluation_trace is trace
    assert "disk full" in window.trace_status.text()
    assert getattr(window, grant_name) is accepted

    trace.fail = False
    assert window.set_studio_camera(window.camera_index)
    assert window.evaluation_trace is None and trace.saved == 1
    assert getattr(window, grant_name) is accepted


def test_binding_change_preserves_grant_on_failed_trace_save_then_revokes_on_retry(granted_window, tmp_path):
    window, grant_name = granted_window
    accepted = getattr(window, grant_name)
    assert accepted is not None
    original = window.routing.snapshot
    trace = FailingTrace()
    window.evaluation_trace = trace
    window.trace_path = tmp_path / "trace.json"
    bindings = {window.vocabulary.action_ids[0]: Action(ActionType.PREVIOUS)}

    assert not window.configure_studio(bindings=bindings)
    assert window.routing.snapshot == original
    assert window.evaluation_trace is trace
    assert getattr(window, grant_name) is accepted

    trace.fail = False
    assert window.configure_studio(bindings=bindings)
    assert dict(window.routing.snapshot.bindings) == bindings
    assert window.evaluation_trace is None and trace.saved == 1
    assert getattr(window, grant_name) is None
