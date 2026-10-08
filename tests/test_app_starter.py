from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from gestureforge.app import Window
from gestureforge.contracts import Action, ActionType, RoutingMode, RoutingResult
from gestureforge.shortcuts import Target, TargetKind
from gestureforge.vocabulary import LEGACY_VOCABULARY
from gestureforge.workspace import Binding, Stage, Workspace, WorkspaceStore
from test_app_readiness import Clock, FakeWorker, FailingTrace, frame, pass_readiness, perform_activation, prediction, start_check


@pytest.fixture(scope="module")
def qapp():
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance() or QApplication([])
    yield app


@pytest.fixture(autouse=True)
def isolated_state(tmp_path, monkeypatch):
    import gestureforge.app as app_module

    monkeypatch.setattr(app_module, "DEFAULT_STUDIO_STATE_FOLDER", tmp_path / "studio")
    monkeypatch.setattr(app_module, "DEFAULT_ENROLMENT_FOLDER", tmp_path / "enrolment")
    monkeypatch.setattr(app_module.Window, "log", lambda self, record: None)


def standard_model(vocabulary=None):
    vocabulary = vocabulary or LEGACY_VOCABULARY
    return SimpleNamespace(
        predict=lambda _: (vocabulary.action_ids[0], True, ""),
        train_labels=vocabulary.labels,
        model_version="standard-starter-revision",
        config=SimpleNamespace(algorithm="svm", multiplier=1.7, margin=1.2),
    )


class FinishedModelLoader:
    def __init__(self, load, *, kind="dataset", profile_id=None, error=""):
        self.kind = kind
        self.profile_id = profile_id
        self.error = error
        self.result = None if error else load()
        self.started = False

    def start(self):
        self.started = True

    def is_alive(self):
        return False

    def join(self):
        return None


def patch_approved_starter(monkeypatch, result, *, error=""):
    import gestureforge.app as app_module

    monkeypatch.setattr(app_module.starter, "unavailable_reason", lambda: None)
    monkeypatch.setattr(app_module.starter, "load_starter", lambda: result)
    monkeypatch.setattr(
        app_module,
        "ModelLoadWorker",
        lambda load, *, kind="dataset", profile_id=None: FinishedModelLoader(
            load, kind=kind, profile_id=profile_id, error=error
        ),
    )


def standard_window(qapp):
    vocabulary = LEGACY_VOCABULARY
    model = standard_model(vocabulary)
    window = Window(model=model, studio=True, vocabulary=vocabulary, profile="standard-guest")
    window._standard_model = model
    return window


def release_fake_worker(window):
    if window.worker is None:
        return
    window.worker.finished = True
    window.poll()


def poll_live_label(window, worker, clock, label, *, accepted=True):
    worker.packets.append((frame(), prediction(window, clock, label, accepted=accepted)))
    window.poll()
    clock.tick()


def harbor_workspace(name):
    root = Path(__file__).resolve().parent.parent
    return WorkspaceStore(Workspace("empty", "Empty")).import_file(root / "assets" / name)


def test_starter_load_completes_in_preview_without_starting_camera(monkeypatch, qapp):
    vocabulary = LEGACY_VOCABULARY
    model = standard_model(vocabulary)
    patch_approved_starter(monkeypatch, (model, "Right", "standard-guest", vocabulary))
    window = Window(model=None, studio=True, vocabulary=vocabulary)
    try:
        assert window.load_studio_starter()
        assert window.model is None
        assert window.worker is None

        window.poll_model_load()

        assert window.model is model
        assert window._standard_model is model
        assert window.routing is not None
        assert window.routing.snapshot.mode == RoutingMode.PREVIEW
        assert window.routing.state == "PAUSED"
        assert window.worker is None
        assert window._standard_live_grant is None
    finally:
        window.close()


@pytest.mark.parametrize("failure", ["loader-error", "closing"])
def test_starter_load_failure_retains_existing_model_without_live_grant(monkeypatch, qapp, failure):
    vocabulary = LEGACY_VOCABULARY
    existing = standard_model(vocabulary)
    starter_candidate = standard_model(vocabulary)
    patch_approved_starter(
        monkeypatch,
        (starter_candidate, "Right", "standard-guest", vocabulary),
        error="ValueError: generated fixture rejected" if failure == "loader-error" else "",
    )
    window = Window(model=existing, studio=True, vocabulary=vocabulary, profile="personal")
    try:
        assert window.load_studio_starter()
        if failure == "closing":
            window._closing = True

        window.poll_model_load()

        assert window.model is existing
        assert window._standard_model is None
        assert window._standard_live_grant is None
        assert window.routing is not None
        assert window.routing.state == "PAUSED"
    finally:
        window.close()


def test_standard_readiness_pass_requires_live_and_explicit_start_before_real_action(monkeypatch, qapp):
    import gestureforge.app as app_module

    window = standard_window(qapp)
    launcher = Mock()
    window.dispatcher.launcher = launcher
    try:
        pass_readiness(window, monkeypatch)
        release_fake_worker(window)
        assert window._standard_live_grant is not None
        assert window.worker is None
        assert "select LIVE" in window._live_gate_reason(window.routing.snapshot)

        assert window.configure_studio(mode=RoutingMode.LIVE)
        assert window.worker is None
        worker = FakeWorker()
        clock = Clock()
        monkeypatch.setattr(app_module, "CaptureWorker", lambda *args, **kwargs: worker)
        monkeypatch.setattr(app_module.time, "monotonic", lambda: clock.value + 0.01)
        monkeypatch.setattr(window, "isActiveWindow", lambda: True)
        start_position = window.viewer.position

        window.start_camera()
        assert worker.start.called
        for _ in range(3):
            poll_live_label(window, worker, clock, "NEUTRAL")
        for _ in range(4):
            poll_live_label(window, worker, clock, window.vocabulary.action_ids[0])

        assert window.viewer.position == start_position + 1
        assert launcher.open.call_count == 0
        outcome = window.dispatcher.dispatch(
            RoutingResult(window.session_summary.outcomes[-1].event_id, action=Action(ActionType.NEXT)),
            window.routing.snapshot,
        )
        assert outcome.status == "duplicate"
        assert window.viewer.position == start_position + 1
    finally:
        window.close()


@pytest.mark.parametrize("labels", [(LEGACY_VOCABULARY.action_ids[1],), ("UNKNOWN",) * 8])
def test_failed_or_incomplete_standard_readiness_blocks_live_start(monkeypatch, qapp, labels):
    window = standard_window(qapp)
    try:
        worker, clock = start_check(window, monkeypatch)
        for label in labels:
            perform_activation(window, worker, clock, label) if label != "UNKNOWN" else poll_live_label(window, worker, clock, label)

        assert not window.finish_readiness_check()
        assert window._standard_live_grant is None
        assert window.configure_studio(mode=RoutingMode.LIVE)
        assert "six-action standard readiness check" in window._live_gate_reason(window.routing.snapshot)
        assert not window._can_start_studio_camera()
    finally:
        window.close()


def test_retained_failed_readiness_restore_cannot_be_retried_or_grant_live(monkeypatch, qapp, tmp_path):
    window = standard_window(qapp)
    try:
        assert window.configure_studio(context_id="manual", bindings={})
        worker, clock = start_check(window, monkeypatch)
        trace = FailingTrace()
        window.evaluation_trace = trace
        window.trace_path = tmp_path / "trace.json"
        perform_activation(window, worker, clock, window.vocabulary.action_ids[1])

        assert not window.finish_readiness_check()
        assert window._readiness_previous is not None
        assert window._standard_live_grant is None
        assert not window.start_readiness_check()
        assert window._standard_live_grant is None
        assert "six-action standard readiness check" in window._live_gate_reason(window.routing.snapshot)
    finally:
        window.close()


def test_standard_grant_is_revoked_by_camera_mapping_and_guest_but_not_navigation(monkeypatch, qapp):
    window = standard_window(qapp)
    first_gesture = window.vocabulary.action_ids[0]
    try:
        stage = Stage(
            "stage-one",
            "Stage One",
            "Do the stage",
            window.viewer.current_card.id,
            (Binding(first_gesture, Action(ActionType.NEXT)),),
        )
        window.workspace = Workspace(window.workspace.id, window.workspace.title, window.workspace.deck, stages=(stage,))
        window.runbook = window._make_runbook(window.workspace)
        assert window.runbook.activate()
        pass_readiness(window, monkeypatch)
        release_fake_worker(window)
        grant = window._standard_live_grant
        assert grant is not None

        assert window.reset_runbook_stage(stage, resume=False)
        assert window._standard_live_grant is grant
        assert window.set_studio_camera(1)
        assert window._standard_live_grant is None

        pass_readiness(window, monkeypatch)
        release_fake_worker(window)
        assert window._standard_live_grant is not None
        assert window.configure_studio(context_id=window.workspace.id, bindings={first_gesture: Action(ActionType.PREVIOUS)})
        assert window._standard_live_grant is None

        pass_readiness(window, monkeypatch)
        release_fake_worker(window)
        assert window._standard_live_grant is not None
        assert window.use_studio_guest()
        assert window._standard_live_grant is None
        assert window.model is None
    finally:
        window.close()


def test_standard_live_allows_approved_quick_action_manual_navigation_without_grant_injection(monkeypatch, qapp):
    window = standard_window(qapp)
    launcher = Mock()
    window.dispatcher.launcher = launcher
    try:
        window.quick_registry.configure(Target("calc", "Calculator", TargetKind.BUILTIN, "calculator", True))
        window.quick_registry.bind_quick(("calc", None, None))
        assert window.use_quick_actions_context()
        pass_readiness(window, monkeypatch)
        release_fake_worker(window)
        assert window._standard_live_grant is not None
        assert window._personal_live_grant is None
        assert window.use_quick_actions_context()
        assert window.configure_studio(mode=RoutingMode.LIVE)
        assert window._live_gate_reason(window.routing.snapshot) == ""

        outcome = window._dispatch_action(Action(ActionType.OPEN_SHORTCUT, "calc"))

        assert outcome.status == "launch_requested"
        assert launcher.open.call_count == 1
        assert window._personal_live_grant is None
        assert window._standard_live_grant is not None
    finally:
        window.close()


def test_standard_harbor_asset_preserves_scenario_with_legacy_gesture_ids():
    custom = harbor_workspace("harbor_workspace.json")
    standard = harbor_workspace("harbor_standard_workspace.json")

    assert custom.id == "harbor-onboarding"
    assert standard.id == "harbor-onboarding-standard"
    assert custom.deck is not None and standard.deck is not None
    assert custom.deck.deck_id != standard.deck.deck_id
    assert [(card.id, card.title, card.body) for card in standard.deck.cards] == [
        (card.id, card.title, card.body) for card in custom.deck.cards
    ]
    assert [stage.id for stage in standard.stages] == [stage.id for stage in custom.stages]

    legacy_ids = set(LEGACY_VOCABULARY.action_ids)
    assert all({binding.gesture_id for binding in stage.bindings} == legacy_ids for stage in standard.stages)
    assert {binding.gesture_id for stage in custom.stages for binding in stage.bindings} == {"G1", "G2", "G3"}
    assert [
        [binding.action for binding in stage.bindings] for stage in standard.stages
    ] == [
        [binding.action for binding in stage.bindings] for stage in custom.stages
    ]


def test_standard_harbor_workspace_routes_all_stages_once_after_readiness(monkeypatch, qapp):
    import gestureforge.app as app_module

    window = standard_window(qapp)
    launcher = Mock()
    window.dispatcher.launcher = launcher
    monkeypatch.setattr(window, "isActiveWindow", lambda: True)
    try:
        assert window.use_studio_workspace(harbor_workspace("harbor_workspace.json"))
        assert window.routing_manual_only
        assert "not in the loaded vocabulary" in window.feedback.text()

        assert window.use_studio_workspace(harbor_workspace("harbor_standard_workspace.json"))
        assert not window.routing_manual_only
        assert window.runbook is not None
        assert window.runbook.current_stage is not None
        assert window.runbook.current_stage.id == "intro"

        pass_readiness(window, monkeypatch)
        release_fake_worker(window)
        assert window.configure_studio(mode=RoutingMode.LIVE)
        assert window._live_gate_reason(window.routing.snapshot) == ""

        worker = FakeWorker()
        clock = Clock()
        monkeypatch.setattr(app_module, "CaptureWorker", lambda *args, **kwargs: worker)
        monkeypatch.setattr(app_module.time, "monotonic", lambda: clock.value + 0.01)

        window.start_camera()
        assert worker.start.called
        for index, label in enumerate(("BOOKMARK", "NEXT", "NEXT", "NEXT", "NEXT", "NEXT")):
            perform_activation(window, worker, clock, label)
            if index < 5:
                worker.finished = True
                window.poll()
                worker = FakeWorker()
                window.start_camera()
                assert worker.start.called

        advances = [
            outcome for outcome in window.session_summary.outcomes
            if outcome.action == Action(ActionType.ADVANCE_STAGE)
        ]
        assert [outcome.status for outcome in advances] == ["applied"] * 6
        assert window.runbook.finished
        assert window.runbook.current_stage is not None
        assert window.runbook.current_stage.id == "review"
        assert launcher.open.call_count == 0
    finally:
        window.close()
