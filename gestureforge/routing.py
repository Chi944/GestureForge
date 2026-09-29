"""Single-owner routing foundation: no UI, callbacks, storage or OS side effects.

Call process/route/configure on the same owner thread. LIVE routing does not
establish readiness: the integrating UI must enforce the future readiness gate.
"""

from collections.abc import Mapping
from dataclasses import replace
import math
from uuid import uuid4

from .contracts import (
    Action, CommandEvent, Prediction, RoutingMode, RoutingResult, RoutingSnapshot,
)
from .controller import Controller, MAX_PREDICTION_AGE_SECONDS


class RoutingSession:
    """Own the controller and snapshot so configuration changes cannot skip reset.

    Construction and configure leave the session paused. Explicit resume creates
    another generation and requires neutral. A result consumes its issued event
    before the caller handles it, including failed downstream actions.
    """

    def __init__(
        self, profile_id: str, model_version: str, context_id: str,
        bindings: Mapping[str, Action], mode: RoutingMode = RoutingMode.PREVIEW,
    ) -> None:
        self.configure(profile_id, model_version, context_id, bindings, mode)

    @property
    def snapshot(self) -> RoutingSnapshot:
        return self._snapshot

    @property
    def state(self) -> str:
        return self._controller.state

    @property
    def progress(self) -> float:
        return self._controller.progress

    @property
    def last_error(self) -> str:
        return self._controller.last_error

    @property
    def controller(self) -> Controller:
        return self._controller

    def configure(
        self, profile_id: str, model_version: str, context_id: str,
        bindings: Mapping[str, Action], mode: RoutingMode = RoutingMode.PREVIEW,
    ) -> RoutingSnapshot:
        """Atomically validate/replace configuration and pause; old work is invalid."""
        snapshot = RoutingSnapshot(
            str(uuid4()), profile_id, model_version, context_id, tuple(bindings.items()), mode,
        )
        controller = Controller(
            snapshot.session_id, profile_id,
            executable_gesture_ids=frozenset(key for key, _ in snapshot.bindings),
            model_version=model_version,
        )
        self._snapshot = snapshot
        self._controller = controller
        self._issued: dict[str, CommandEvent] = {}
        self._consumed: set[str] = set()
        return snapshot

    def resume(self) -> RoutingSnapshot:
        self._controller.resume()
        self._snapshot = replace(self.snapshot, session_id=self._controller.session_id)
        self._issued.clear()
        self._consumed.clear()
        return self.snapshot

    def pause(self) -> None:
        self._controller.pause()
        self._issued.clear()

    def process(self, prediction: Prediction, now: float) -> CommandEvent | None:
        event = self._controller.process(prediction, now)
        if self.state == "WAIT_NEUTRAL":
            self._issued.clear()
        if event is not None:
            self._issued[event.event_id] = event
        return event

    def route(self, event: CommandEvent, now: float) -> RoutingResult:
        """Consume a controller-issued event once; practice only yields simulation."""
        def reject(reason: str) -> RoutingResult:
            return RoutingResult(event.event_id, rejection_reason=reason)

        snapshot = self.snapshot
        if self.state == "PAUSED":
            return reject("paused")
        if event.event_id in self._consumed:
            return reject("duplicate_event")
        issued = self._issued.pop(event.event_id, None)
        if issued is not None:
            self._consumed.add(event.event_id)
            if event != issued:
                return reject("altered_event")
        if event.session_id != snapshot.session_id or event.profile_id != snapshot.profile_id:
            return reject("identity_mismatch")
        if issued is None:
            return reject("unissued_event")
        if event.model_version != snapshot.model_version:
            return reject("model_mismatch")
        if (
            not math.isfinite(now) or not math.isfinite(event.timestamp)
            or not 0 <= now - event.timestamp <= MAX_PREDICTION_AGE_SECONDS
        ):
            return reject("stale_event")
        action = dict(snapshot.bindings).get(event.command)
        if action is None:
            return reject("unmapped_gesture")
        if snapshot.mode != RoutingMode.LIVE:
            return RoutingResult(event.event_id, simulated_action=action)
        return RoutingResult(event.event_id, action=action)
