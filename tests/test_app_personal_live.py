from dataclasses import replace
from types import SimpleNamespace
from typing import cast
from unittest.mock import Mock

import pytest

from gestureforge.app import HistoricalPracticeReview, Window
from gestureforge.contracts import Action, ActionType, RoutingMode, RoutingResult
from gestureforge.practice import PROTOCOL_VERSION, PersonalRehearsal, PracticeResult, PracticeTrial
from gestureforge.practice_widget import PersonalRehearsalWidget
from gestureforge.session_summary import Outcome
from gestureforge.shortcuts import Target, TargetKind
from gestureforge.vocabulary import GestureVocabulary
from gestureforge.workspace import Binding, Stage, Workspace


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


def model(vocabulary=None):
    vocabulary = vocabulary or GestureVocabulary(("G1", "G2", "G3"))
    return SimpleNamespace(
        predict=lambda _: (vocabulary.action_ids[0], True, ""),
        train_labels=vocabulary.labels,
        model_version="personal-live-model",
        config=SimpleNamespace(algorithm="knn", multiplier=2.0, margin=1.5),
    )


def passed_result(window: Window, *, status="passed") -> PracticeResult:
    revision = window._practice_current_revision()
    trials = tuple(
        PracticeTrial(
            expected,
            repetition,
            f"Hold {expected}",
            f"practice-session-{index}",
            0.0,
            5.0,
            "correct",
            (),
            (),
            expected == "NEUTRAL",
            50,
            (),
            True,
            "unit fixture",
        )
        for index, (expected, repetition) in enumerate(
            [(pose, rep) for rep in range(1, 11) for pose in ("G1", "G2", "G3", "NEUTRAL")]
            + [("NEGATIVE", rep) for rep in range(1, 11)]
        )
    )
    return PracticeResult(
        "attempt-live",
        revision,
        PROTOCOL_VERSION,
        window.profile,
        window._model_version(),
        status,
        "unit full pass",
        trials,
        (("G1", 10), ("G2", 10), ("G3", 10), ("NEUTRAL", 10)),
        0,
        (),
    )


def review_for(window: Window, result: PracticeResult, tmp_path, *, dirty=False) -> HistoricalPracticeReview:
    assert window.routing is not None
    path = tmp_path / f"practice-{result.attempt_id}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("{}", encoding="utf-8")
    outcomes: tuple[Outcome, ...] = ()
    if dirty:
        outcomes = (
            Outcome(
                "unexpected-event",
                "unexpected-session",
                "gesture",
                "simulated",
                Action(ActionType.NEXT),
                "",
                window.routing.snapshot.context_id,
                result.model_version,
            ),
        )
    return HistoricalPracticeReview(
        result,
        outcomes,
        window.routing.snapshot.context_id,
        tuple(window.routing.snapshot.bindings),
        tuple(sorted(window.session_summary.scope.items())),
        path,
    )


class Attempt:
    def __init__(self, result: PracticeResult, *, passed=True):
        self.attempt_id = result.attempt_id
        self._result = result
        self._passed = passed

    def result(self):
        return self._result

    def passed_for(self, revision):
        return self._passed and revision == self._result.behavior_revision


class Widget:
    def __init__(self, result: PracticeResult | None, *, save_error=False):
        self.last_saved_result = result
        self.save_error = save_error


def grant(window: Window, result: PracticeResult, tmp_path, *, review=None) -> bool:
    return window._maybe_grant_personal_live(
        attempt=cast(PersonalRehearsal, Attempt(result)),
        widget=cast(PersonalRehearsalWidget, Widget(result)),
        result=result,
        review=review or review_for(window, result, tmp_path),
    )


def test_live_grant_requires_current_saved_pass_and_clean_review(qapp, tmp_path):
    window = Window(model=model(), studio=True, vocabulary=GestureVocabulary(("G1", "G2", "G3")))
    try:
        result = passed_result(window)
        review = review_for(window, result, tmp_path)

        assert not window._maybe_grant_personal_live(
            attempt=cast(PersonalRehearsal, Attempt(result)),
            widget=cast(PersonalRehearsalWidget, Widget(None)),
            result=result,
            review=review,
        )
        assert not window._maybe_grant_personal_live(
            attempt=cast(PersonalRehearsal, Attempt(result, passed=False)),
            widget=cast(PersonalRehearsalWidget, Widget(result)),
            result=result,
            review=review,
        )
        failed_result = passed_result(window, status="failed")
        assert not window._maybe_grant_personal_live(
            attempt=cast(PersonalRehearsal, Attempt(failed_result, passed=False)),
            widget=cast(PersonalRehearsalWidget, Widget(failed_result)),
            result=failed_result,
            review=review,
        )
        assert not window._maybe_grant_personal_live(
            attempt=cast(PersonalRehearsal, Attempt(result)),
            widget=cast(PersonalRehearsalWidget, Widget(result)),
            result=result,
            review=review_for(window, result, tmp_path, dirty=True),
        )

        assert grant(window, result, tmp_path)
        assert window._personal_live_grant is not None
        accepted = window._personal_live_grant
        assert not window._finish_practice_rehearsal(result)
        assert window._personal_live_grant is accepted
        assert "No current Practice attempt" in window.practice_status.text()
    finally:
        window.close()


def test_live_start_requires_live_selection_and_revokes_on_camera_change(qapp, tmp_path):
    window = Window(model=model(), studio=True, vocabulary=GestureVocabulary(("G1", "G2", "G3")))
    try:
        result = passed_result(window)
        assert grant(window, result, tmp_path)
        assert window.routing is not None
        assert "select LIVE" in window._live_gate_reason(window.routing.snapshot)

        assert window.configure_studio(mode=RoutingMode.LIVE)
        assert window._live_gate_reason(window.routing.snapshot) == ""
        assert window._can_start_studio_camera()

        assert window.set_studio_camera(1)
        assert window._personal_live_grant is None
        assert "complete and save" in window._live_gate_reason(window.routing.snapshot)
        assert not window._can_start_studio_camera()
    finally:
        window.close()


def test_live_context_must_be_approved_current_stage_or_active_quick_actions(qapp, tmp_path):
    window = Window(model=model(), studio=True, vocabulary=GestureVocabulary(("G1", "G2", "G3")))
    try:
        stage = Stage(
            "stage-one",
            "Stage One",
            "Do the stage",
            window.viewer.current_card.id,
            (Binding("G1", Action(ActionType.NEXT)),),
        )
        window.workspace = Workspace(window.workspace.id, window.workspace.title, window.workspace.deck, stages=(stage,))
        window.runbook = window._make_runbook(window.workspace)
        assert window.runbook.activate()
        result = passed_result(window)
        assert grant(window, result, tmp_path)

        assert window.configure_studio(context_id=stage.id, mode=RoutingMode.LIVE, bindings={"G1": Action(ActionType.NEXT)})
        assert window.routing is not None
        assert window._live_gate_reason(window.routing.snapshot) == ""

        window.runbook.position = 0
        window.runbook.finished = True
        assert "approved stage" in window._live_gate_reason(window.routing.snapshot)

        assert window.configure_studio(context_id=window.quick_actions_context_id, mode=RoutingMode.LIVE, bindings={"G1": Action(ActionType.NEXT)})
        assert window.routing is not None
        assert "approved stage" in window._live_gate_reason(window.routing.snapshot)

        window.quick_registry.configure(Target("calc", "Calculator", TargetKind.BUILTIN, "calculator", True))
        window.quick_registry.bind_quick(("calc", None, None))
        assert window.use_quick_actions_context()
        result = passed_result(window)
        assert grant(window, result, tmp_path)
        assert window.configure_studio(
            context_id=window.quick_actions_context_id,
            mode=RoutingMode.LIVE,
            bindings={"G1": Action(ActionType.OPEN_SHORTCUT, "calc")},
        )
        assert window.routing is not None
        assert window._live_gate_reason(window.routing.snapshot) == ""
        assert window._can_start_studio_camera()
    finally:
        window.close()


def test_live_grant_revocation_distinguishes_cosmetic_and_behavior_changes(qapp, tmp_path):
    window = Window(model=model(), studio=True, vocabulary=GestureVocabulary(("G1", "G2", "G3")))
    try:
        stage = Stage(
            "stage-one",
            "Stage One",
            "Do the stage",
            window.viewer.current_card.id,
            (Binding("G1", Action(ActionType.NEXT)),),
        )
        window.workspace = replace(window.workspace, stages=(stage,))
        window.runbook = window._make_runbook(window.workspace)
        assert window.runbook.activate()
        result = passed_result(window)
        assert grant(window, result, tmp_path)

        window.workspace = replace(window.workspace, title="Renamed workspace")
        assert window._invalidate_readiness_if_revision_changed("workspace renamed")
        assert window._personal_live_grant is not None

        window.quick_registry.configure(Target("calc", "Calculator", TargetKind.BUILTIN, "calculator", True))
        window.quick_registry.bind_quick(("calc", None, None))
        assert window.use_quick_actions_context()
        result = passed_result(window)
        assert grant(window, result, tmp_path)
        candidate = window.quick_registry.copy()
        candidate.configure(Target("calc", "Renamed Calculator", TargetKind.BUILTIN, "calculator", True))
        window.quick_registry.replace_with(candidate)
        window.accept_quick_bindings_change(None)
        assert window._personal_live_grant is not None
        assert not window.quick_actions_active
        assert window.use_quick_actions_context()
        assert window.configure_studio(mode=RoutingMode.LIVE)
        assert window.routing is not None
        assert window._live_gate_reason(window.routing.snapshot) == ""
        assert window.start_button.isEnabled()

        candidate = window.quick_registry.copy()
        candidate.configure(Target("calc", "Calculator", TargetKind.BUILTIN, "camera", True))
        window.quick_registry.replace_with(candidate)
        window.accept_quick_bindings_change(None)
        assert window._personal_live_grant is None

        result = passed_result(window)
        assert grant(window, result, tmp_path)
        assert window.configure_studio(context_id=stage.id, bindings={"G1": Action(ActionType.NEXT)})
        assert window.configure_studio(
            context_id=window.workspace.id,
            bindings={
                "G1": Action(ActionType.PREVIOUS),
                "G2": Action(ActionType.PREVIOUS),
                "G3": Action(ActionType.BOOKMARK),
            },
        )
        assert window._personal_live_grant is None
        assert window.configure_studio(context_id=stage.id, bindings={"G1": Action(ActionType.NEXT)})
        assert window.configure_studio(context_id=window.workspace.id, bindings={
            "G1": Action(ActionType.NEXT), "G2": Action(ActionType.PREVIOUS), "G3": Action(ActionType.BOOKMARK),
        })
        assert window._personal_live_grant is None
    finally:
        window.close()


def test_live_ready_refuses_focus_loss_during_dispatch_handoff(qapp, tmp_path, monkeypatch):
    window = Window(model=model(), studio=True, vocabulary=GestureVocabulary(("G1", "G2", "G3")))
    try:
        result = passed_result(window)
        assert grant(window, result, tmp_path)
        assert window.configure_studio(mode=RoutingMode.LIVE)
        assert window.routing is not None
        snapshot = window.routing.snapshot

        monkeypatch.setattr(window, "isVisible", lambda: True)
        monkeypatch.setattr(window, "isActiveWindow", lambda: True)
        assert window._gesture_live_ready(snapshot)

        window._focus_epoch += 1
        assert not window._gesture_live_ready(snapshot)

        monkeypatch.setattr(window, "isActiveWindow", lambda: False)
        assert not window._dispatcher_active()
        window.start_camera()
        assert window.worker is None
    finally:
        window.close()


@pytest.mark.parametrize("lose_focus", [False, True])
def test_live_shortcut_dispatch_pauses_and_rechecks_focus_before_launch(qapp, tmp_path, monkeypatch, lose_focus):
    from PySide6.QtCore import QEvent

    window = Window(model=model(), studio=True, vocabulary=GestureVocabulary(("G1", "G2", "G3")))
    launcher = Mock()
    window.dispatcher.launcher = launcher
    try:
        monkeypatch.setattr(window, "isActiveWindow", lambda: True)
        window.quick_registry.configure(Target("camera", "Camera", TargetKind.BUILTIN, "camera", True))
        window.quick_registry.bind_quick(("camera", None, None))
        assert window.use_quick_actions_context()
        assert grant(window, passed_result(window), tmp_path)
        assert window.configure_studio(mode=RoutingMode.LIVE)
        assert window.routing is not None
        snapshot = window.routing.resume()

        def release_capture(_snapshot):
            assert window.routing is not None
            assert window.routing.state == "PAUSED"
            if lose_focus:
                monkeypatch.setattr(window, "isActiveWindow", lambda: False)
                window.changeEvent(QEvent(QEvent.Type.ActivationChange))
                monkeypatch.setattr(window, "isActiveWindow", lambda: True)
            return True

        window.dispatcher.release_capture = release_capture
        request = RoutingResult("camera-request", action=Action(ActionType.OPEN_SHORTCUT, "camera"))
        outcome = window.dispatcher.dispatch(request, snapshot)
        assert outcome.status == ("rejected" if lose_focus else "launch_requested")
        assert launcher.open.call_count == (0 if lose_focus else 1)
        assert window.routing.state == "PAUSED"
        assert window.dispatcher.dispatch(request, snapshot).status == "duplicate"
        assert launcher.open.call_count == (0 if lose_focus else 1)
    finally:
        window.close()


@pytest.mark.parametrize("already_active", [False, True])
def test_missing_quick_target_does_not_change_practice_authorization(qapp, tmp_path, already_active):
    window = Window(model=model(), studio=True, vocabulary=GestureVocabulary(("G1", "G2", "G3")))
    try:
        target = tmp_path / "reference.txt"
        target.write_text("Demo reference", encoding="utf-8")
        window.quick_registry.configure(Target("reference", "Reference", TargetKind.FILE, str(target), True))
        window.quick_registry.bind_quick(("reference", None, None))
        if already_active:
            assert window.use_quick_actions_context()
        target.unlink()  # Own temporary fixture, never a user's resource.
        assert grant(window, passed_result(window), tmp_path)
        accepted = window._personal_live_grant
        assert window.configure_studio(mode=RoutingMode.LIVE)
        assert not window.use_quick_actions_context()
        assert window.routing is not None
        assert window.routing.state == "PAUSED"
        assert not window._can_start_studio_camera()
        assert not window.quick_actions_active
        assert window._personal_live_grant is accepted
        target.write_text("Demo reference", encoding="utf-8")
        assert window.use_quick_actions_context()
        assert window.configure_studio(mode=RoutingMode.LIVE)
        assert window.routing is not None
        assert window._personal_live_grant is accepted
        assert window._live_gate_reason(window.routing.snapshot) == ""
    finally:
        window.close()


def test_same_workspace_title_reload_preserves_personal_live_grant(qapp, tmp_path):
    window = Window(model=model(), studio=True, vocabulary=GestureVocabulary(("G1", "G2", "G3")))
    try:
        assert not window.workspace.stages
        assert grant(window, passed_result(window), tmp_path)
        accepted = window._personal_live_grant
        assert window.configure_studio(mode=RoutingMode.LIVE)
        assert window.routing is not None
        bindings = window.routing.snapshot.bindings
        assert window.use_studio_workspace(replace(window.workspace, title="Renamed workspace"))
        assert window._personal_live_grant is accepted
        assert window.routing.state == "PAUSED"
        assert window.routing.snapshot.bindings == bindings
        assert window._live_gate_reason(window.routing.snapshot) == ""
        assert window._can_start_studio_camera()
    finally:
        window.close()
