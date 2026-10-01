"""Session outcomes and measured rehearsal records; no invented completion."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import time

from .contracts import Action, validate_gesture_id, validate_identifier
from .storage import atomic_write_json, text
from .workspace import action_json


@dataclass(frozen=True)
class Outcome:
    event_id: str
    session_id: str
    source: str
    status: str
    action: Action | None = None
    reason: str = ''
    context_id: str = ''
    model_version: str = ''
    timestamp: float = field(default_factory=time.monotonic)


@dataclass(frozen=True)
class Trial:
    id: str
    expected: str
    observed: str | None
    tracking_lost: bool = False


class SessionSummary:
    def __init__(self) -> None:
        self.outcomes: list[Outcome] = []
        self.trials: list[Trial] = []
        self.completed_stages: set[str] = set()
        self.retries = 0

    def ensure_capacity(self) -> None:
        if len(self.outcomes) >= 10000:
            raise ValueError('session record limit reached; export and start a new review')

    def record(self, outcome: Outcome) -> None:
        self.ensure_capacity()
        validate_identifier(outcome.event_id)
        validate_identifier(outcome.session_id)
        text(outcome.reason, 240, empty=True)
        if outcome.source not in {'gesture', 'manual'} or outcome.status not in {
            'simulated', 'launch_requested', 'failed', 'duplicate', 'rejected', 'applied', 'unchanged'
        } or (outcome.action is not None and not isinstance(outcome.action, Action)):
            raise ValueError('invalid measured outcome')
        self.outcomes.append(outcome)

    def record_trial(self, trial: Trial) -> None:
        validate_identifier(trial.id)
        if trial.expected != 'NEUTRAL':
            validate_gesture_id(trial.expected)
        if trial.observed not in {None, 'NEUTRAL', 'UNKNOWN'}:
            validate_gesture_id(trial.observed)  # type: ignore[arg-type]
        if type(trial.tracking_lost) is not bool:
            raise ValueError('tracking_lost must be boolean')
        if any(item.id == trial.id for item in self.trials):
            raise ValueError('duplicate measured trial ID')
        if len(self.trials) >= 10000:
            raise ValueError('trial limit reached')
        self.trials.append(trial)

    def acknowledge_completion(self, stage_id: str) -> None:
        validate_identifier(stage_id)
        self.completed_stages.add(stage_id)

    def retry(self) -> None:
        self.retries += 1

    def counts(self) -> dict[str, int]:
        result = {status: sum(item.status == status for item in self.outcomes) for status in (
            'simulated', 'launch_requested', 'failed', 'duplicate', 'rejected', 'applied', 'unchanged')}
        result.update(correct=sum(t.observed == t.expected for t in self.trials),
                      wrong=sum(t.observed not in {None, 'UNKNOWN'} and t.observed != t.expected for t in self.trials),
                      missed=sum(t.observed in {None, 'UNKNOWN'} for t in self.trials),
                      tracking_lost=sum(t.tracking_lost for t in self.trials),
                      retries=self.retries, acknowledged_completion=len(self.completed_stages))
        return result

    def export(self, path: Path) -> None:
        atomic_write_json(path, {'schema_version': 1, 'counts': self.counts(),
                                'outcomes': [{'event_id': o.event_id, 'session_id': o.session_id,
                                              'source': o.source, 'status': o.status,
                                              'action': action_json(o.action) if o.action else None,
                                              'reason': o.reason, 'context_id': o.context_id,
                                              'model_version': o.model_version, 'timestamp': o.timestamp} for o in self.outcomes],
                                'trials': [vars(t) for t in self.trials],
                                'completed_stages': sorted(self.completed_stages)}, limit=16 * 1024 * 1024)
