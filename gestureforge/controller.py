"""Prototype activation controller for converting predictions into commands."""

from __future__ import annotations

import math
import uuid
from dataclasses import dataclass

from .contracts import CommandEvent, Prediction, validate_gesture_id, validate_identifier


NEUTRAL_HOLD_SECONDS = 0.300
COMMAND_HOLD_SECONDS = 0.400
MAX_PREDICTION_AGE_SECONDS = 0.200
MAX_FRAME_GAP_SECONDS = 0.200
CLASSIFIER_REJECTION_GRACE_SECONDS = 0.500

EXECUTABLE_COMMANDS = frozenset({"NEXT"})
CLASSIFIER_REJECTION_REASONS = {"distance_rejection", "margin_rejection"}


@dataclass
class _Candidate:
    label: str
    started_at: float


class Controller:
    """State machine that protects the viewer from accidental repeat actions."""

    def __init__(
        self, session_id: str, profile_id: str = "pilot", *,
        executable_gesture_ids: frozenset[str] | None = None,
        model_version: str | None = None,
    ) -> None:
        self._legacy_labels = executable_gesture_ids is None
        gesture_ids = EXECUTABLE_COMMANDS if executable_gesture_ids is None else executable_gesture_ids
        if isinstance(gesture_ids, str) or not 1 <= len(gesture_ids) <= 3:
            raise ValueError("one to three executable gesture IDs are required")
        for gesture_id in gesture_ids:
            validate_gesture_id(gesture_id)
        self._executable_gesture_ids = frozenset(gesture_ids)
        if model_version is not None:
            validate_identifier(model_version)
        self._model_version = model_version
        self.session_id = session_id
        self.profile_id = profile_id
        self.state = "PAUSED"
        self.progress = 0.0
        self.last_error = ""
        self._last_timestamp: float | None = None
        self._last_frame_id: int | None = None
        self._neutral_started_at: float | None = None
        self._candidate: _Candidate | None = None
        self._classifier_reject_started_at: float | None = None
        self._event_counter = 0

    @property
    def executable_gesture_ids(self) -> frozenset[str]:
        return self._executable_gesture_ids

    @property
    def model_version(self) -> str | None:
        return self._model_version

    def resume(self, session_id: str | None = None) -> None:
        """Begin accepting predictions after a fresh neutral hold."""

        self.session_id = session_id or f"session-{uuid.uuid4()}"
        self.state = "WAIT_NEUTRAL"
        self.progress = 0.0
        self.last_error = ""
        self._last_timestamp = None
        self._last_frame_id = None
        self._neutral_started_at = None
        self._candidate = None
        self._classifier_reject_started_at = None

    def pause(self) -> None:
        self.state = "PAUSED"
        self.progress = 0.0
        self.last_error = ""
        self._neutral_started_at = None
        self._candidate = None
        self._classifier_reject_started_at = None

    def fault(self, reason: str = "fault") -> None:
        self.pause()
        self.last_error = reason

    def process(self, prediction: Prediction, now: float) -> CommandEvent | None:
        """Consume a prediction and optionally emit one command event."""

        if self.state == "PAUSED":
            return None
        if not self._matches_active_identity(prediction):
            return None
        if self.model_version is not None and prediction.model_version != self.model_version:
            self._require_neutral("model version mismatch")
            return None
        if not self._prediction_is_fresh_and_ordered(prediction, now):
            self._require_neutral("stale, future, or out-of-order prediction", reset_clock=True)
            return None

        self._last_timestamp = prediction.timestamp
        self._last_frame_id = prediction.frame_id

        if not prediction.accepted:
            self._handle_rejected_prediction(prediction)
            return None

        label = prediction.label.upper() if self._legacy_labels else prediction.label
        if label == "NEUTRAL":
            self._classifier_reject_started_at = None
            self._observe_neutral(prediction.timestamp)
            return None

        if self.state == "LATCHED":
            self._classifier_reject_started_at = None
            self.progress = 1.0
            return None

        if self._classifier_rejection_expired(prediction.timestamp):
            self._require_neutral("classifier rejection grace expired")
            return None
        self._classifier_reject_started_at = None

        self._neutral_started_at = None
        if label not in self.executable_gesture_ids:
            self._cancel_candidate()
            if self.state != "WAIT_NEUTRAL":
                self.state = "READY"
            self.progress = 0.0
            return None

        if self.state == "WAIT_NEUTRAL":
            self.progress = 0.0
            self.last_error = "Show NEUTRAL until READY, then hold an enabled gesture."
            return None

        if self._candidate is None or self._candidate.label != label:
            self._candidate = _Candidate(label=label, started_at=prediction.timestamp)
            self._classifier_reject_started_at = None
            self.state = "CANDIDATE"
            self.progress = 0.0
            return None

        elapsed = prediction.timestamp - self._candidate.started_at
        self.state = "CANDIDATE"
        self.progress = min(1.0, max(0.0, elapsed / COMMAND_HOLD_SECONDS))
        if elapsed < COMMAND_HOLD_SECONDS:
            return None

        self.state = "LATCHED"
        self.progress = 1.0
        self._event_counter += 1
        return CommandEvent(
            event_id=f"{self.session_id}:{self.profile_id}:{self._event_counter}",
            session_id=self.session_id,
            profile_id=self.profile_id,
            frame_id=prediction.frame_id,
            command=label,
            timestamp=now,
            model_version=prediction.model_version,
        )

    def _matches_active_identity(self, prediction: Prediction) -> bool:
        return prediction.session_id == self.session_id and prediction.profile_id == self.profile_id

    def _prediction_is_fresh_and_ordered(self, prediction: Prediction, now: float) -> bool:
        if not math.isfinite(now) or not math.isfinite(prediction.timestamp):
            return False
        if prediction.timestamp > now:
            return False
        if now - prediction.timestamp > MAX_PREDICTION_AGE_SECONDS:
            return False
        if self._last_timestamp is not None:
            if prediction.timestamp <= self._last_timestamp:
                return False
            if prediction.timestamp - self._last_timestamp > MAX_FRAME_GAP_SECONDS:
                return False
        if self._last_frame_id is not None and prediction.frame_id <= self._last_frame_id:
            return False
        return True

    def _observe_neutral(self, timestamp: float) -> None:
        self._candidate = None
        if self._neutral_started_at is None:
            self._neutral_started_at = timestamp
        elapsed = timestamp - self._neutral_started_at
        self.progress = min(1.0, max(0.0, elapsed / NEUTRAL_HOLD_SECONDS))
        if elapsed >= NEUTRAL_HOLD_SECONDS:
            self.state = "READY"
            self.progress = 1.0
        else:
            self.state = "WAIT_NEUTRAL"

    def _cancel_candidate(self) -> None:
        self._candidate = None

    def _handle_rejected_prediction(self, prediction: Prediction) -> None:
        reason = prediction.rejection_reason or "prediction rejected"
        if reason not in CLASSIFIER_REJECTION_REASONS:
            self._require_neutral(reason)
            return
        if self.state == "LATCHED":
            self.progress = 1.0
            self.last_error = reason
            return
        if self.state not in {"READY", "CANDIDATE"}:
            self._require_neutral(reason)
            return
        if self._classifier_reject_started_at is None:
            self._classifier_reject_started_at = prediction.timestamp
        if prediction.timestamp - self._classifier_reject_started_at > CLASSIFIER_REJECTION_GRACE_SECONDS:
            self._require_neutral(reason)
            return
        self._cancel_candidate()
        self.state = "READY"
        self.progress = 0.0
        self.last_error = reason

    def _classifier_rejection_expired(self, timestamp: float) -> bool:
        return (
            self._classifier_reject_started_at is not None
            and timestamp - self._classifier_reject_started_at > CLASSIFIER_REJECTION_GRACE_SECONDS
        )

    def _require_neutral(self, reason: str, *, reset_clock: bool = False) -> None:
        self.state = "WAIT_NEUTRAL"
        self.progress = 0.0
        self.last_error = reason
        self._neutral_started_at = None
        self._candidate = None
        self._classifier_reject_started_at = None
        if reset_clock:
            self._last_timestamp = None
            self._last_frame_id = None
