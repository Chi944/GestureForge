"""GF-P12 measured rehearsal using the shared router and persistent dispatcher.

No camera, model fitting, external launcher, or shell attachment is created here.
The host supplies its real router/dispatcher and current behavior-revision getter.
"""
from __future__ import annotations

from collections import Counter
from collections.abc import Callable
from dataclasses import asdict, dataclass
import math
from pathlib import Path
from typing import Any
from uuid import uuid4

from .contracts import Prediction, RoutingMode, RoutingSnapshot, validate_gesture_id
from .controller import MAX_FRAME_GAP_SECONDS, MAX_PREDICTION_AGE_SECONDS
from .dispatcher import Dispatcher
from .routing import RoutingSession
from .storage import atomic_write_json

PROTOCOL_VERSION = 'gf-p12-v1'
DIAGNOSTIC_PROTOCOL_VERSION = 'gf-p12-single-pose-diagnostic-v1'
TRIALS_PER_POSE = 10
WINDOW_SECONDS = 5.0
NEGATIVE_CUES = (
    'Keep both hands out of view.',
    'Keep both hands out of view while moving your head normally.',
    'Show one index finger only; do not use an enrolled action pose.',
    'Show a relaxed half-open hand; avoid enrolled action poses.',
    'Show all five fingers together; avoid enrolled action poses.',
    'Slowly move an open palm left and right.',
    'Slowly rotate an open palm away from the camera.',
    'Move an open palm into and out of view.',
    'Move between a relaxed hand and an open palm without holding an action pose.',
    'Rest your hand, then return to an open palm without holding an action pose.',
)


@dataclass(frozen=True)
class PracticePrompt:
    expected: str
    repetition: int
    instruction: str


@dataclass(frozen=True)
class PracticeTrial:
    expected: str
    repetition: int
    instruction: str
    session_id: str
    started_at: float
    ended_at: float
    outcome: str
    actions: tuple[str, ...]
    event_ids: tuple[str, ...]
    neutral_ready: bool
    frames: int
    rejections: tuple[tuple[str, int], ...]
    coverage_ok: bool
    reason: str


@dataclass(frozen=True)
class PracticeResult:
    attempt_id: str
    behavior_revision: str
    protocol_version: str
    profile_id: str
    model_version: str
    status: str
    reason: str
    trials: tuple[PracticeTrial, ...]
    correct_per_pose: tuple[tuple[str, int], ...]
    negative_actions: int
    guidance: tuple[str, ...]


class PersonalRehearsal:
    """Fifty prompted windows, scored only from protected simulated events.

Each window uses a new router generation. Host must attach shared capture to the
returned snapshot before delivering predictions (never relabel old packets).
Action/negative windows first wait for real NEUTRAL -> READY, then an explicit
Begin window. NEUTRAL windows measure that transition themselves. The component
feeds the supplied router exactly once; the shell must not process packets again.
"""

    def __init__(self, router: RoutingSession, dispatcher: Dispatcher,
                 revision: str, current_revision: Callable[[], str],
                 gesture_ids: tuple[str, ...], *,
                 negative_cues: tuple[str, ...] = NEGATIVE_CUES) -> None:
        if (not isinstance(revision, str) or not revision.strip()
                or len(revision) > 128):
            raise ValueError('a bounded behavior revision is required')
        if len(gesture_ids) != 3 or len(set(gesture_ids)) != 3:
            raise ValueError('three distinct enrolled action poses are required')
        for gesture in gesture_ids:
            validate_gesture_id(gesture)
        if len(negative_cues) != 10 or any(
                not isinstance(cue, str) or not cue.strip() or len(cue) > 240
                for cue in negative_cues):
            raise ValueError('ten explicit negative/transition instructions are required')
        snapshot = router.snapshot
        if snapshot.mode != RoutingMode.REHEARSAL or set(dict(snapshot.bindings)) != set(gesture_ids):
            raise ValueError('REHEARSAL routing with all three enrolled poses is required')
        if router.state != 'PAUSED' or dispatcher.current() != snapshot:
            raise ValueError('attach a paused shared router and matching persistent dispatcher')
        self.router, self.dispatcher = router, dispatcher
        self.revision, self.current_revision = revision, current_revision
        self.gesture_ids = gesture_ids
        self._base = snapshot
        self._snapshot = snapshot
        self.attempt_id = uuid4().hex
        self.sequence = tuple(
            PracticePrompt(label, repetition, 'Hold ' + label + ' for the full window.')
            for repetition in range(1, 11)
            for label in (*gesture_ids, 'NEUTRAL')
        ) + tuple(PracticePrompt('NEGATIVE', i + 1, cue) for i, cue in enumerate(negative_cues))
        self._full_sequence = self.sequence
        self.diagnostic_pose: str | None = None
        self.status = 'idle'
        self.reason = 'Prepare the next trial. Actions remain simulated.'
        self._trials: list[PracticeTrial] = []
        self._clock: float | None = None
        self._started: float | None = None
        self._prepared_at: float | None = None
        self._last_packet: float | None = None
        self._last_frame = -1
        self._actions: list[str] = []
        self._events: list[str] = []
        self._frames = 0
        self._rejections: Counter[str] = Counter()
        self._neutral_ready = False
        self._coverage = True
        self._window_first: float | None = None
        self._window_last: float | None = None
        self.last_begin_attempt: dict[str, Any] | None = None
        self.boundary_prediction: dict[str, Any] | None = None
        self.last_capture_validation: dict[str, Any] | None = None

    @property
    def expected(self) -> PracticePrompt | None:
        return self.sequence[len(self._trials)] if len(self._trials) < len(self.sequence) else None

    @property
    def completed(self) -> int:
        return len(self._trials)

    def select_diagnostic_pose(self, pose: str | None) -> None:
        """Select a separate one-window probe before any capture is prepared."""
        if self.status != 'idle' or self._prepared_at is not None or self._trials:
            raise ValueError('choose the test before preparing the first trial')
        if pose is not None and pose not in (*self.gesture_ids, 'NEUTRAL'):
            raise ValueError('choose an enrolled pose or NEUTRAL')
        self.diagnostic_pose = pose
        self.sequence = (self._full_sequence if pose is None else
                         (PracticePrompt(pose, 1, 'Hold ' + pose + ' for the full window.'),))
        self.reason = ('Prepare the next trial. Actions remain simulated.' if pose is None else
                       'Single-pose diagnostic only. This cannot pass the full rehearsal.')

    def remaining_window_seconds(self, now: float) -> float | None:
        """Display-only countdown; reading it does not advance or score a trial."""
        if self.status != 'measuring' or self._started is None:
            return None
        return max(0.0, self._window_end - now)

    def _check(self, now: float) -> bool:
        if (isinstance(now, bool) or not isinstance(now, (int, float))
                or not math.isfinite(now) or (self._clock is not None and now < self._clock)):
            raise ValueError('finite nondecreasing monotonic time is required')
        self._clock = now
        if self.status in {'passed', 'failed', 'cancelled', 'expired'}:
            return False
        current = self.router.snapshot
        if (self.current_revision() != self.revision
                or current != self._snapshot
                or self.dispatcher.current() != current
                or current.mode != RoutingMode.REHEARSAL):
            self.cancel('Behavior or routing generation changed; start a new attempt.', expired=True)
            return False
        return self.status not in {'passed', 'failed', 'cancelled', 'expired'}

    def prepare(self, now: float) -> RoutingSnapshot:
        if not self._check(now) or self.status != 'idle' or self.expected is None:
            raise ValueError('the next trial cannot be prepared in the current state')
        self.router.pause()
        self._snapshot = self.router.resume()
        self._started = None
        self._prepared_at = now
        self._last_packet, self._last_frame = None, -1
        self._actions, self._events = [], []
        self._frames, self._rejections = 0, Counter()
        self._coverage, self._neutral_ready = True, False
        self._window_first, self._window_last = None, None
        self.last_begin_attempt = None
        self.boundary_prediction = None
        self.last_capture_validation = None
        self.status = 'preparing'
        self.reason = 'Wait for capture, then show NEUTRAL until READY.'
        if self.expected.expected == 'NEUTRAL':
            self.reason = 'Wait for capture, then Begin window and show NEUTRAL.'
        return self._snapshot

    def begin_window(self, now: float) -> None:
        # Diagnostic evidence is local only; it does not contribute trial credit.
        self.last_begin_attempt = {
            'requested_at': (now if type(now) in (int, float) and math.isfinite(now) else None),
            'status_before': self.status,
            'controller_state': self.router.state,
            'last_capture_at': self._last_packet, 'accepted': False,
        }
        try:
            self._begin_window(now)
        except ValueError as exc:
            self.last_begin_attempt['error'] = str(exc)
            raise
        self.last_begin_attempt['accepted'] = True

    def _begin_window(self, now: float) -> None:
        if not self._check(now) or self.status not in {'preparing', 'armed'}:
            raise ValueError('prepare and arm the trial before beginning')
        prompt = self.expected
        assert prompt is not None
        if self._last_packet is None or now - self._last_packet > MAX_FRAME_GAP_SECONDS:
            raise ValueError('fresh capture is required before the timed window')
        if prompt.expected != 'NEUTRAL' and self.router.state != 'READY':
            raise ValueError('show accepted NEUTRAL until the controller is READY')
        self._started = now
        self._window_first, self._window_last = None, None
        self._neutral_ready, self._coverage = False, True
        self.status = 'measuring'
        self.reason = prompt.instruction

    def receive(self, prediction: Prediction, now: float) -> None:
        if not self._check(now) or self.status not in {'preparing', 'armed', 'measuring'}:
            return
        snapshot = self._snapshot
        # Wrong-generation inputs are ignored rather than relabelled; they cannot
        # supply coverage or score. Host cancels on an actual setup/capture change.
        if (prediction.session_id != snapshot.session_id
                or prediction.profile_id != snapshot.profile_id
                or prediction.model_version != snapshot.model_version):
            return
        invalid_reason = self._prediction_invalid_reason(prediction, now)
        if invalid_reason is not None:
            if self._recover_stale_preparation_packet(prediction, now, invalid_reason):
                return
            self._record_capture_validation(prediction, now, invalid_reason, recovered=False)
            self.cancel('Invalid or stale capture packet; preserve evidence and retry.')
            return
        scoreable_drain_packet = (
            self.status == 'measuring'
            and self._started is not None
            and self._started <= prediction.timestamp <= self._window_end
            and now <= self._window_drain_deadline
        )
        if not scoreable_drain_packet:
            self.tick(now)
        if self.status not in {'preparing', 'armed', 'measuring'}:
            return
        measuring = self.status == 'measuring'
        pre_window = bool(measuring and self._started is not None and prediction.timestamp < self._started)
        if measuring and self._started is not None and prediction.timestamp > self._window_end:
            return  # post-window frames are outside the scored capture-time interval
        if measuring and not pre_window:
            if self._window_first is None:
                self._window_first = prediction.timestamp
            if self._window_last is not None and prediction.timestamp - self._window_last > MAX_FRAME_GAP_SECONDS:
                self._coverage = False
            self._window_last = prediction.timestamp
            self._frames += 1
            if not prediction.accepted:
                self._rejections[prediction.rejection_reason] += 1
        self._last_frame, self._last_packet = prediction.frame_id, prediction.timestamp
        if not measuring and self.expected is not None and self.expected.expected == 'NEUTRAL':
            # The neutral trial must earn READY inside its measurement window,
            # rather than inherit a preparation-phase neutral hold.
            return
        event = self.router.process(prediction, now)
        if pre_window and prediction.accepted and prediction.label != 'NEUTRAL' and event is None:
            self.boundary_prediction = {
                'captured_at': prediction.timestamp, 'received_at': now,
                'begin_at': self._started, 'label': prediction.label,
                'command_emitted': False,
            }
            self.cancel('A non-NEUTRAL prediction captured before Begin arrived after Begin; '
                        'no command was emitted. Keep NEUTRAL until measurement starts.')
            return
        if prediction.accepted and prediction.label == 'NEUTRAL' and self.router.state == 'READY':
            if pre_window:
                pass
            elif measuring:
                self._neutral_ready = True
            else:
                self.status = 'armed'
                self.reason = 'READY. Begin the five-second window when prepared.'
        if event is None:
            return
        result = self.router.route(event, now)
        if result.action is not None or result.simulated_action is None or result.rejection_reason:
            self.cancel('Practice routing did not produce a simulation.')
            return
        try:
            outcome = self.dispatcher.dispatch(result, snapshot, source='gesture')
        except Exception:
            self.cancel('Simulation recording failed; preserve evidence before retrying.')
            return
        if (outcome.status != 'simulated' or outcome.event_id != event.event_id
                or outcome.source != 'gesture' or outcome.session_id != snapshot.session_id
                or outcome.action != result.simulated_action):
            self.cancel('Simulation was not recorded successfully.')
            return
        self._actions.append(event.command)
        self._events.append(event.event_id)
        if not measuring or pre_window:
            self.boundary_prediction = {
                'captured_at': prediction.timestamp, 'received_at': now,
                'begin_at': self._started, 'label': prediction.label,
                'command_emitted': True,
            }
            self.cancel('A simulated command was emitted from a pre-Begin prediction; '
                        'review Begin timing and recognition before retrying.')
        if measuring:
            self.tick(now)

    def tick(self, now: float) -> None:
        if not self._check(now):
            return
        if self.status in {'preparing', 'armed'} and self._prepared_at is not None and now - self._prepared_at >= 30:
            self.cancel('Preparation timed out; review capture and NEUTRAL evidence.')
            return
        if self.status != 'measuring' or self._started is None:
            return
        if now > self._window_drain_deadline:
            self._finish_window(self._window_end)

    @property
    def _window_end(self) -> float:
        assert self._started is not None
        return self._started + WINDOW_SECONDS

    @property
    def _window_drain_deadline(self) -> float:
        return self._window_end + MAX_PREDICTION_AGE_SECONDS

    def _finish_window(self, ended_at: float) -> None:
        assert self._started is not None and self.expected is not None
        prompt = self.expected
        coverage = (self._coverage and self._window_first is not None
                    and self._window_first - self._started <= MAX_FRAME_GAP_SECONDS
                    and self._window_last is not None
                    and ended_at - self._window_last <= MAX_FRAME_GAP_SECONDS)
        if not coverage:
            outcome, reason = 'inconclusive', 'Capture did not cover the full five-second window.'
        elif prompt.expected == 'NEGATIVE':
            outcome = 'correct' if not self._actions else 'wrong'
            reason = 'No simulated action.' if not self._actions else 'Action during a negative/transition interval.'
        elif prompt.expected == 'NEUTRAL':
            outcome = 'correct' if self._neutral_ready and not self._actions else ('wrong' if self._actions else 'missed')
            reason = 'NEUTRAL reached READY.' if outcome == 'correct' else 'NEUTRAL did not safely rearm.'
        else:
            outcome = ('correct' if self._actions == [prompt.expected]
                       else 'wrong' if self._actions else 'missed')
            reason = 'Exactly one intended simulated action.' if outcome == 'correct' else 'Missing, wrong or repeated simulated action.'
        self._trials.append(PracticeTrial(
            prompt.expected, prompt.repetition, prompt.instruction, self._snapshot.session_id,
            self._started, ended_at, outcome, tuple(self._actions), tuple(self._events),
            self._neutral_ready, self._frames, tuple(sorted(self._rejections.items())),
            bool(coverage), reason,
        ))
        self.router.pause()
        self._started = None
        self.status, self.reason = 'idle', reason
        if self.diagnostic_pose is not None:
            # Close the host's temporary practice context using its existing
            # terminal lifecycle; a diagnostic can never certify readiness.
            self.cancel('Single-pose diagnostic complete. Full 50-window rehearsal not performed.')
            return
        if self.completed == len(self.sequence):
            counts = self._counts()
            good = (all(value >= 9 for value in counts.values())
                    and all(t.coverage_ok and t.outcome != 'wrong' for t in self._trials)
                    and all(t.outcome == 'correct' for t in self._trials if t.expected == 'NEGATIVE'))
            self.status = 'passed' if good else 'failed'
            self.reason = ('Measured rehearsal met the proposed target; await host acceptance.' if good
                           else 'Rehearsal target not met; review per-pose and rejection evidence.')

    def cancel(self, reason: str, *, expired: bool = False) -> None:
        if self.status in {'passed', 'failed', 'cancelled', 'expired'}:
            return
        if self.status in {'preparing', 'armed', 'measuring'} and self.expected is not None:
            prompt = self.expected
            start = self._started if self._started is not None else self._prepared_at
            assert start is not None
            self._trials.append(PracticeTrial(
                prompt.expected, prompt.repetition, prompt.instruction, self._snapshot.session_id,
                start, self._clock if self._clock is not None else start,
                'interrupted', tuple(self._actions), tuple(self._events), self._neutral_ready,
                self._frames, tuple(sorted(self._rejections.items())), False, reason,
            ))
        self.router.pause()
        self.status = 'expired' if expired else 'cancelled'
        self.reason = reason
        self._started = None

    def _counts(self) -> dict[str, int]:
        return {label: sum(t.expected == label and t.outcome == 'correct' for t in self._trials)
                for label in (*self.gesture_ids, 'NEUTRAL')}

    def result(self) -> PracticeResult:
        counts = self._counts()
        guidance = []
        for label, count in counts.items():
            if sum(t.expected == label for t in self._trials) == 10 and count < 9:
                guidance.append(f'{label}: review accepted labels, rejection reasons and pose notes before targeted repair collection.')
        negatives = sum(len(t.actions) for t in self._trials if t.expected == 'NEGATIVE')
        if negatives:
            guidance.append('Negative actions occurred. Inspect transition evidence before changing thresholds.')
        if any(not t.coverage_ok for t in self._trials):
            guidance.append('Incomplete capture: resolve timing/interruption before repeating the attempt.')
        protocol = DIAGNOSTIC_PROTOCOL_VERSION if self.diagnostic_pose is not None else PROTOCOL_VERSION
        return PracticeResult(self.attempt_id, self.revision, protocol,
                              self._base.profile_id, self._base.model_version,
                              self.status, self.reason, tuple(self._trials),
                              tuple(counts.items()), negatives, tuple(guidance))

    def passed_for(self, revision: str) -> bool:
        result = self.result()
        return (
            result.status == 'passed'
            and result.protocol_version == PROTOCOL_VERSION
            and len(result.trials) == 50
            and revision == result.behavior_revision
            and self.current_revision() == result.behavior_revision
        )

    def save(self, directory: Path) -> Path:
        """Save local numeric outcomes; failed writes leave all evidence in memory."""
        path = Path(directory) / f'practice-{self.attempt_id}.json'
        payload: dict[str, Any] = asdict(self.result())
        payload['schema_version'] = 1
        payload['simulation_only'] = True
        payload['timing_diagnostics'] = {
            'scope': 'latest prepared trial only; timestamps use the monotonic clock',
            'last_begin_attempt': self.last_begin_attempt,
            'boundary_prediction': self.boundary_prediction,
            'last_capture_validation': self.last_capture_validation,
        }
        atomic_write_json(path, payload)
        return path

    def _prediction_invalid_reason(self, prediction: Prediction, now: float) -> str | None:
        if (not isinstance(prediction.timestamp, (float, int))
                or isinstance(prediction.timestamp, bool) or not math.isfinite(prediction.timestamp)):
            return 'invalid_timestamp'
        if prediction.timestamp > now:
            return 'future_timestamp'
        if type(prediction.frame_id) is not int:
            return 'invalid_frame_id'
        if prediction.frame_id <= self._last_frame:
            return 'out_of_order_frame'
        if self._last_packet is not None and prediction.timestamp <= self._last_packet:
            return 'out_of_order_timestamp'
        if type(prediction.accepted) is not bool:
            return 'invalid_accepted_flag'
        if not isinstance(prediction.label, str):
            return 'invalid_label'
        if not isinstance(prediction.rejection_reason, str):
            return 'invalid_rejection_reason'
        if prediction.accepted and prediction.rejection_reason:
            return 'accepted_with_rejection_reason'
        if not prediction.accepted and not prediction.rejection_reason:
            return 'rejected_without_reason'
        if now - prediction.timestamp > MAX_PREDICTION_AGE_SECONDS:
            return 'stale_prediction'
        return None

    def _recover_stale_preparation_packet(self, prediction: Prediction, now: float, reason: str) -> bool:
        if reason != 'stale_prediction' or self.status != 'preparing':
            return False
        self.tick(now)
        if self.status != 'preparing':
            self._record_capture_validation(prediction, now, reason, recovered=False)
            return False
        event = self.router.process(prediction, now)
        recovered = event is None
        self._record_capture_validation(prediction, now, reason, recovered=recovered)
        self._last_frame, self._last_packet = prediction.frame_id, prediction.timestamp
        self.reason = 'Stale startup capture dropped; show fresh NEUTRAL until READY.'
        return recovered

    def _record_capture_validation(self, prediction: Prediction, now: float, reason: str, *,
                                   recovered: bool) -> None:
        captured = prediction.timestamp
        captured_at = captured if type(captured) in (int, float) and math.isfinite(captured) else None
        self.last_capture_validation = {
            'reason': reason,
            'phase': self.status,
            'received_at': now,
            'captured_at': captured_at,
            'age_seconds': (now - captured_at if captured_at is not None else None),
            'frame_id': prediction.frame_id if type(prediction.frame_id) is int else None,
            'last_capture_at': self._last_packet,
            'last_frame_id': self._last_frame,
            'recovered': recovered,
            'decision': 'dropped_and_rearmed' if recovered else 'terminal_cancel',
        }
