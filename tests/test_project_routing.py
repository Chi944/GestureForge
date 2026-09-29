from dataclasses import FrozenInstanceError, replace
import math

import pytest

from gestureforge.contracts import (
    Action, ActionType, CommandEvent, FEATURE_VERSION, Prediction, PROJECT_CONTRACT_VERSION,
    RoutingMode, RoutingSnapshot, SCHEMA_VERSION,
)
from gestureforge.routing import RoutingSession


BINDINGS = {
    "G1": Action(ActionType.NEXT),
    "G2": Action(ActionType.OPEN_SHORTCUT, "calculator"),
    "G3": Action(ActionType.ADVANCE_STAGE),
}


def prediction(session: RoutingSession, label: str, frame: int, time: float) -> Prediction:
    snapshot = session.snapshot
    return Prediction(snapshot.session_id, snapshot.profile_id, frame, time, label, True,
                      snapshot.model_version)


def emit(session: RoutingSession, gesture: str = "G1") -> CommandEvent:
    session.resume()
    for frame, time in enumerate((0.0, 0.15, 0.31), 1):
        assert session.process(prediction(session, "NEUTRAL", frame, time), time) is None
    for frame, time in enumerate((0.45, 0.60, 0.75), 4):
        assert session.process(prediction(session, gesture, frame, time), time) is None
    event = session.process(prediction(session, gesture, 7, 0.90), 0.90)
    assert event is not None
    return event


@pytest.mark.parametrize("action", [
    Action(ActionType.NEXT), Action(ActionType.PREVIOUS), Action(ActionType.BOOKMARK),
    Action(ActionType.ADVANCE_STAGE), Action(ActionType.OPEN_SHORTCUT, "calculator"),
])
def test_single_typed_action_routes_once(action: Action) -> None:
    session = RoutingSession("trainer", "model-v2", "stage-1", {"CUSTOM_POSE": action},
                             RoutingMode.LIVE)
    event = emit(session, "CUSTOM_POSE")
    result = session.route(event, 0.91)
    assert result.action == action
    assert result.simulated_action is None
    assert not result.rejection_reason
    assert session.route(event, 0.92).rejection_reason == "duplicate_event"
    for frame, time in enumerate((1.0, 1.15, 1.30, 1.45), 8):
        assert session.process(prediction(session, "CUSTOM_POSE", frame, time), time) is None


@pytest.mark.parametrize("mode", [RoutingMode.PREVIEW, RoutingMode.REHEARSAL])
def test_practice_records_would_be_shortcut_without_executable_result(mode: RoutingMode) -> None:
    session = RoutingSession("trainer", "model-v2", "quick-actions", BINDINGS, mode)
    event = emit(session, "G2")
    result = session.route(event, 0.91)
    assert result.action is None
    assert result.simulated_action == BINDINGS["G2"]
    assert not result.rejection_reason
    assert session.route(event, 0.92).rejection_reason == "duplicate_event"


@pytest.mark.parametrize("change", ["profile", "model", "context", "mapping", "mode"])
def test_switch_invalidates_queued_work_and_requires_neutral(change: str) -> None:
    session = RoutingSession("trainer", "model-v2", "stage-1", BINDINGS)
    event = emit(session)
    old = session.snapshot
    queued_prediction = prediction(session, "G1", 8, 1.0)
    mapping = {**BINDINGS, "G1": Action(ActionType.BOOKMARK)} if change == "mapping" else BINDINGS
    session.configure(
        "other" if change == "profile" else "trainer",
        "model-v3" if change == "model" else "model-v2",
        "stage-2" if change == "context" else "stage-1", mapping,
        RoutingMode.LIVE if change == "mode" else RoutingMode.PREVIEW,
    )
    assert session.state == "PAUSED"
    assert session.snapshot.session_id != old.session_id
    assert session.route(event, 0.91).action is None
    session.resume()
    assert session.route(event, 0.91).rejection_reason == "identity_mismatch"
    assert session.process(queued_prediction, 1.0) is None
    for frame, time in enumerate((1.0, 1.15, 1.30, 1.45), 1):
        assert session.process(prediction(session, "G1", frame, time), time) is None
    assert session.state == "WAIT_NEUTRAL"
    fresh = emit(session)
    result = session.route(fresh, 0.91)
    assert (result.action or result.simulated_action) == mapping["G1"]


def test_snapshot_copies_caller_bindings_and_rejects_invalid_configuration_atomically() -> None:
    bindings = dict(BINDINGS)
    session = RoutingSession("trainer", "model-v2", "stage-1", bindings)
    before = session.snapshot
    bindings["G1"] = Action(ActionType.BOOKMARK)
    assert dict(before.bindings)["G1"] == Action(ActionType.NEXT)
    with pytest.raises(FrozenInstanceError):
        setattr(before, "context_id", "stage-2")
    with pytest.raises(ValueError):
        session.configure("trainer", "model-v2", "stage-2", {"NEUTRAL": BINDINGS["G1"]})
    assert session.snapshot is before
    with pytest.raises(ValueError):
        RoutingSnapshot("s1", "p1", "v1", "c1", (("G1", BINDINGS["G1"]),) * 2)


@pytest.mark.parametrize("bad_id", ["", "g1", "NEUTRAL", "UNKNOWN", "G-1", "A" * 65, "Ｇ1"])
def test_invalid_gesture_ids_are_rejected(bad_id: str) -> None:
    with pytest.raises(ValueError):
        RoutingSession("trainer", "v1", "c1", {bad_id: Action(ActionType.NEXT)})


def test_invalid_actions_and_snapshot_fields_are_rejected() -> None:
    with pytest.raises(ValueError):
        Action("NEXT")  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        Action(ActionType.NEXT, "calculator")
    for bad_id in (None, "", "../../evil.exe", "https://example.com"):
        with pytest.raises(ValueError):
            Action(ActionType.OPEN_SHORTCUT, bad_id)
    with pytest.raises(ValueError):
        RoutingSession("trainer", "", "c1", BINDINGS)
    with pytest.raises(ValueError):
        RoutingSession("trainer", "v1", "c1", {})
    with pytest.raises(ValueError):
        RoutingSession("trainer", "v1", "c1", {f"G{i}": BINDINGS["G1"] for i in range(4)})
    with pytest.raises(ValueError):
        RoutingSession("trainer", "v1", "c1", {"G1": "NEXT"})  # type: ignore[dict-item]
    with pytest.raises(ValueError):
        RoutingSession("trainer", "v1", "c1", BINDINGS, "LIVE")  # type: ignore[arg-type]


@pytest.mark.parametrize("now", [0.89, 1.11, math.nan, math.inf])
def test_expired_or_invalid_time_consumes_event(now: float) -> None:
    session = RoutingSession("trainer", "model-v2", "stage-1", BINDINGS, RoutingMode.LIVE)
    event = emit(session)
    assert session.route(event, now).rejection_reason == "stale_event"
    assert session.route(event, 0.91).rejection_reason == "duplicate_event"


def test_unissued_altered_and_old_model_events_cannot_bypass_controller() -> None:
    session = RoutingSession("trainer", "model-v2", "stage-1", BINDINGS, RoutingMode.LIVE)
    event = emit(session)
    assert session.route(replace(event, event_id="forged"), 0.91).rejection_reason == "unissued_event"
    assert session.route(replace(event, model_version="old"), 0.91).rejection_reason == "altered_event"
    assert session.route(event, 0.91).rejection_reason == "duplicate_event"
    event = emit(session)
    assert session.route(replace(event, command="G2"), 0.91).rejection_reason == "altered_event"
    assert session.route(event, 0.91).rejection_reason == "duplicate_event"
    event = emit(session)
    assert session.route(replace(event, profile_id="other"), 0.91).rejection_reason == "altered_event"
    assert session.route(event, 0.91).rejection_reason == "duplicate_event"


def test_pause_and_tracking_loss_cancel_pending_events() -> None:
    session = RoutingSession("trainer", "model-v2", "stage-1", BINDINGS, RoutingMode.LIVE)
    event = emit(session)
    session.pause()
    assert session.route(event, 0.91).rejection_reason == "paused"
    session.resume()
    assert session.route(event, 0.91).rejection_reason == "identity_mismatch"
    event = emit(session)
    loss = replace(prediction(session, "UNKNOWN", 8, 1.0), accepted=False,
                   rejection_reason="tracking lost")
    session.process(loss, 1.0)
    assert session.route(event, 1.01).rejection_reason == "unissued_event"


def test_project_contract_does_not_change_legacy_versions() -> None:
    assert FEATURE_VERSION == SCHEMA_VERSION == 1
    assert PROJECT_CONTRACT_VERSION == 1
