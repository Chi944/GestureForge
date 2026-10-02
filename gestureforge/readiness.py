"""Session-local guided checks scored from protected, simulated command events."""
from collections.abc import Mapping
import hashlib
import json
from uuid import uuid4

from .contracts import Action, CommandEvent, FEATURE_VERSION, RoutingResult, validate_gesture_id
from .controller import (
    CLASSIFIER_REJECTION_GRACE_SECONDS, COMMAND_HOLD_SECONDS, MAX_FRAME_GAP_SECONDS,
    MAX_PREDICTION_AGE_SECONDS, NEUTRAL_HOLD_SECONDS,
)
from .session_summary import Trial
from .shortcuts import TargetRegistry
from .workspace import Workspace, action_json, binding_json


def behavior_revision(profile_id: str, model_version: str, chosen_hand: str,
                      workspace: Workspace, registry: TargetRegistry,
                      bindings: Mapping[str, Action]) -> str:
    """Hash authored behavior, excluding display names and current stage position."""
    payload = {
        'profile': profile_id, 'model': model_version, 'hand': chosen_hand,
        'feature_version': FEATURE_VERSION,
        'policy': [NEUTRAL_HOLD_SECONDS, COMMAND_HOLD_SECONDS, MAX_PREDICTION_AGE_SECONDS,
                   MAX_FRAME_GAP_SECONDS, CLASSIFIER_REJECTION_GRACE_SECONDS],
        'bindings': {key: action_json(value) for key, value in bindings.items()},
        'quick': [binding_json(binding) for binding in workspace.quick_bindings],
        'stages': [{'id': stage.id, 'card': stage.card_id,
                    'bindings': [binding_json(binding) for binding in stage.bindings]}
                   for stage in workspace.stages],
        'targets': sorted((t.id, t.kind.value, t.value, t.trusted) for t in registry.targets),
        'quick_slots': registry.quick_slots,
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()


class ReadinessCheck:
    """Six prompted activations, with rearming enforced by the existing router.

    The host supplies results from its real simulation router, never manual
    outcomes. This check is evidence of this short attempt, not recognition
    accuracy, participant identity, or permission to launch applications.
    """

    def __init__(self, revision: str, gesture_ids: tuple[str, ...]) -> None:
        if not revision or len(gesture_ids) != 3 or len(set(gesture_ids)) != 3:
            raise ValueError('a readiness check requires a revision and three distinct poses')
        for gesture_id in gesture_ids:
            validate_gesture_id(gesture_id)
        self.revision = revision
        self.sequence = gesture_ids * 2
        self.status = 'running'
        self.reason = 'Show NEUTRAL, then hold the prompted pose.'
        self.trials: list[Trial] = []
        self._seen: set[str] = set()

    @property
    def completed(self) -> int:
        return sum(trial.expected == trial.observed for trial in self.trials)

    @property
    def expected(self) -> str | None:
        return self.sequence[len(self.trials)] if self.status == 'running' else None

    def invalidate(self, revision: str) -> None:
        if revision != self.revision:
            self.status = 'expired'
            self.reason = 'Setup changed. Run a new readiness check.'

    def passed_for(self, revision: str) -> bool:
        self.invalidate(revision)
        return self.status == 'passed'

    def record(self, event: CommandEvent, result: RoutingResult, revision: str) -> bool:
        self.invalidate(revision)
        if (self.status != 'running' or event.event_id in self._seen
                or result.event_id != event.event_id or result.simulated_action is None
                or result.action is not None or result.rejection_reason):
            return False
        self._seen.add(event.event_id)
        expected = self.expected
        assert expected is not None
        self.trials.append(Trial(str(uuid4()), expected, event.command))
        if event.command != expected:
            self.status = 'failed'
            self.reason = f'Expected {expected}; {event.command} would have activated. Retry or personalise.'
        elif self.completed == len(self.sequence):
            self.status = 'passed'
            self.reason = 'Six correct simulated activations; no wrong actions. Control remains paused.'
        return True

    def finish(self) -> None:
        if self.status == 'running':
            for expected in self.sequence[len(self.trials):]:
                self.trials.append(Trial(str(uuid4()), expected, None))
            self.status = 'failed'
            self.reason = 'Check incomplete. Retry, personalise your gestures, or use manual controls.'

    def cancel(self, reason: str) -> None:
        if self.status == 'running':
            self.finish()
            self.reason = reason
