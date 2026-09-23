import math

from gestureforge.contracts import Prediction
from gestureforge.controller import Controller


def pred(
    label: str,
    frame_id: int,
    timestamp: float,
    *,
    accepted: bool = True,
    session: str = "s1",
) -> Prediction:
    return Prediction(
        session_id=session,
        profile_id="pilot",
        frame_id=frame_id,
        timestamp=timestamp,
        label=label,
        accepted=accepted,
        rejection_reason="" if accepted else "tracking lost",
    )


def arm(controller: Controller, start: float = 0.0, frame: int = 1) -> int:
    session = controller.session_id
    controller.process(pred("NEUTRAL", frame, start, session=session), start)
    controller.process(pred("NEUTRAL", frame + 1, start + 0.15, session=session), start + 0.15)
    controller.process(pred("NEUTRAL", frame + 2, start + 0.31, session=session), start + 0.31)
    assert controller.state == "READY"
    return frame + 3


def hold_next(controller: Controller, frame: int, start: float):
    session = controller.session_id
    assert controller.process(pred("NEXT", frame, start, session=session), start) is None
    assert (
        controller.process(pred("NEXT", frame + 1, start + 0.18, session=session), start + 0.18)
        is None
    )
    assert (
        controller.process(pred("NEXT", frame + 2, start + 0.35, session=session), start + 0.35)
        is None
    )
    return controller.process(
        pred("NEXT", frame + 3, start + 0.41, session=session), start + 0.41
    )


def test_next_hold_executes_once_until_neutral_rearms() -> None:
    controller = Controller("s1")
    controller.resume()
    frame = arm(controller)

    event = hold_next(controller, frame, 0.45)
    assert event is not None
    assert event.command == "NEXT"
    assert event.timestamp == 0.86
    assert controller.state == "LATCHED"

    session = controller.session_id
    assert controller.process(pred("NEXT", frame + 4, 1.00, session=session), 1.00) is None
    assert controller.state == "LATCHED"

    controller.process(pred("NEUTRAL", frame + 5, 1.05, session=session), 1.05)
    controller.process(pred("NEUTRAL", frame + 6, 1.20, session=session), 1.20)
    controller.process(pred("NEUTRAL", frame + 7, 1.36, session=session), 1.36)
    assert controller.state == "READY"

    second = hold_next(controller, frame + 8, 1.45)
    assert second is not None
    assert second.event_id != event.event_id


def test_preview_labels_do_not_execute_or_latch() -> None:
    controller = Controller("s1")
    controller.resume()
    frame = arm(controller)
    session = controller.session_id

    assert controller.process(pred("PREVIOUS", frame, 0.45, session=session), 0.45) is None
    assert controller.state == "READY"
    assert controller.process(pred("BOOKMARK", frame + 1, 0.55, session=session), 0.55) is None
    assert controller.state == "READY"


def test_changed_candidate_cancels_hold() -> None:
    controller = Controller("s1")
    controller.resume()
    frame = arm(controller)
    session = controller.session_id

    controller.process(pred("NEXT", frame, 0.45, session=session), 0.45)
    controller.process(pred("BOOKMARK", frame + 1, 0.60, session=session), 0.60)
    assert controller.process(pred("NEXT", frame + 2, 0.75, session=session), 0.75) is None
    assert controller.state == "CANDIDATE"


def test_preview_labels_do_not_unlatch() -> None:
    controller = Controller("s1")
    controller.resume()
    frame = arm(controller)
    session = controller.session_id

    assert hold_next(controller, frame, 0.45) is not None
    assert controller.process(pred("BOOKMARK", frame + 4, 1.00, session=session), 1.00) is None
    assert controller.state == "LATCHED"


def test_tracking_loss_and_gap_require_neutral_again() -> None:
    controller = Controller("s1")
    controller.resume()
    frame = arm(controller)
    session = controller.session_id

    controller.process(pred("NEXT", frame, 0.45, session=session), 0.45)
    controller.process(pred("NEXT", frame + 1, 0.50, accepted=False, session=session), 0.50)
    assert controller.state == "WAIT_NEUTRAL"

    assert controller.process(pred("NEXT", frame + 2, 0.60, session=session), 0.60) is None
    assert controller.state == "WAIT_NEUTRAL"

    controller.process(pred("NEUTRAL", frame + 3, 0.70, session=session), 0.70)
    controller.process(pred("NEUTRAL", frame + 4, 1.01, session=session), 1.01)
    assert controller.state == "WAIT_NEUTRAL"
    assert controller.last_error

    controller.process(pred("NEUTRAL", frame + 5, 1.20, session=session), 1.20)
    controller.process(pred("NEUTRAL", frame + 6, 1.36, session=session), 1.36)
    controller.process(pred("NEUTRAL", frame + 7, 1.52, session=session), 1.52)
    assert controller.state == "READY"


def test_stale_future_out_of_order_and_old_session_do_not_execute() -> None:
    controller = Controller("s1")
    controller.resume()
    frame = arm(controller)
    session = controller.session_id

    assert controller.process(pred("NEXT", frame, 0.45, session=session), 0.70) is None
    assert controller.state == "WAIT_NEUTRAL"

    controller.resume()
    frame = arm(controller, start=1.00, frame=10)
    session = controller.session_id
    assert controller.process(pred("NEXT", frame, 1.45, session=session), 1.40) is None
    assert controller.state == "WAIT_NEUTRAL"

    controller.resume()
    frame = arm(controller, start=2.00, frame=20)
    session = controller.session_id
    controller.process(pred("NEXT", frame, 2.45, session=session), 2.45)
    assert controller.process(pred("NEXT", frame, 2.50, session=session), 2.50) is None
    assert controller.state == "WAIT_NEUTRAL"

    controller.resume(session_id="s2")
    assert controller.process(pred("NEXT", 1, 3.00, session="s1"), 3.00) is None
    assert controller.state == "WAIT_NEUTRAL"


def test_resume_without_session_invalidates_queued_predictions() -> None:
    controller = Controller("s1")
    controller.resume(session_id="s1")
    frame = arm(controller)
    queued = pred("NEXT", frame, 0.45, session="s1")

    controller.pause()
    controller.resume()

    assert controller.session_id != "s1"
    assert controller.process(queued, 0.45) is None
    assert controller.state == "WAIT_NEUTRAL"


def test_non_finite_times_are_rejected_and_neutral_can_recover() -> None:
    controller = Controller("s1")
    controller.resume()
    session = controller.session_id

    assert controller.process(pred("NEUTRAL", 1, math.nan, session=session), 0.0) is None
    assert controller.state == "WAIT_NEUTRAL"

    controller.process(pred("NEUTRAL", 2, 1.00, session=session), 1.00)
    controller.process(pred("NEUTRAL", 3, 1.16, session=session), 1.16)
    controller.process(pred("NEUTRAL", 4, 1.31, session=session), 1.31)
    assert controller.state == "READY"
