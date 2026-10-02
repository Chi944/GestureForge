"""Timed enrolment using observations supplied by the shared capture owner."""

from dataclasses import dataclass
from datetime import datetime, timezone
import math
from pathlib import Path
from uuid import uuid4

import numpy as np

from .contracts import Observation, validate_identifier
from .dataset import SampleRecord, save_dataset
from .features import extract_feature_vector
from .storage import text
from .vocabulary import GestureVocabulary

OFFSETS = (.2, .6, 1., 1.4, 1.8)
DELIVERY_TOLERANCE = .2
SLOT_TOLERANCE = .2


@dataclass(frozen=True)
class EnrolmentPlan:
    participant: str
    hand: str
    vocabulary: GestureVocabulary
    instructions: tuple[tuple[str, str], ...]
    split: str = 'train'
    trials: int = 12
    setup: str = ''

    def __post_init__(self):
        validate_identifier(self.participant)
        if self.hand not in ('Left', 'Right'):
            raise ValueError('Choose Left or Right hand')
        if not isinstance(self.vocabulary, GestureVocabulary):
            raise ValueError('A versioned vocabulary is required')
        if self.split not in ('train', 'validation'):
            raise ValueError('Choose a separate TRAIN or VALIDATION session')
        if type(self.trials) is not int or not 2 <= self.trials <= 12:
            raise ValueError('Choose 2–12 trials per pose')
        if (not isinstance(self.instructions, tuple) or len(self.instructions) != 4
                or any(not isinstance(pair, tuple) or len(pair) != 2 for pair in self.instructions)
                or {pair[0] for pair in self.instructions} != set(self.vocabulary.labels)):
            raise ValueError('Provide instructions for three poses and NEUTRAL')
        for _, instruction in self.instructions:
            text(instruction, 200)
        text(self.setup, 500)


class EnrolmentSession:
    """One owner thread; never opens capture, classifies poses or dispatches actions.

    The host must suspend routing before supplying the capture generation. The
    monotonic clock used here must match Observation.timestamp.
    """

    def __init__(self, plan: EnrolmentPlan, root: Path, capture_session: str,
                 capture_profile: str, *, consent: bool):
        if consent is not True:
            raise ValueError('Confirm consent before collection')
        validate_identifier(capture_session)
        validate_identifier(capture_profile)
        self.plan = plan
        self.capture_session = capture_session
        self.capture_profile = capture_profile
        self.session_id = 'enrol-' + uuid4().hex
        folder = Path(root).resolve() / self.session_id
        folder.mkdir(parents=True, exist_ok=False)
        self.manifest = folder / 'manifest.json'
        self.records: list[SampleRecord] = []
        self.features: list[np.ndarray] = []
        self.pending_records: list[SampleRecord] = []
        self.pending_features: list[np.ndarray] = []
        self.completed = 0
        self.state = 'prepare'
        self.feedback = 'Prepare the displayed pose, then press Begin trial.'
        self.last_now = -math.inf
        self.last_frame = -1
        self.last_timestamp = -math.inf
        self.start = 0.
        self.release_until = 0.
        self.after_save = 'release'
        self.starts: dict[str, float] = {}
        self.created_at = datetime.now(timezone.utc).isoformat()

    @property
    def total(self):
        return 4 * self.plan.trials

    @property
    def label(self):
        return self.plan.vocabulary.labels[min(self.completed // self.plan.trials, 3)]

    @property
    def trial_id(self):
        return f'{self.session_id}-{self.completed:03d}'

    def _clock(self, now):
        if type(now) not in (int, float) or not math.isfinite(now) or now < self.last_now:
            raise ValueError('Use a finite monotonic clock')
        self.last_now = now

    def begin(self, now: float):
        self._clock(now)
        if self.state != 'prepare':
            raise ValueError('Finish or save the current trial first')
        self.start = now + 2.
        self.starts[self.trial_id] = self.start
        self.state = 'countdown'
        self.feedback = 'Get ready. Hold still after the countdown.'

    def _slot(self, feature, reason, timestamp):
        index = len(self.features) + len(self.pending_features) if feature is not None else None
        if feature is not None:
            self.pending_features.append(feature.copy())
        self.pending_records.append(SampleRecord(
            self.plan.participant, self.session_id, self.trial_id, self.label, self.plan.split,
            len(self.pending_records), timestamp, feature is not None, index, reason,
            self.plan.hand, 'human'))

    def advance(self, now: float, observation: Observation | None = None):
        self._clock(now)
        if self.state == 'release' and now >= self.release_until:
            self.state = 'prepare'
        usable = False
        if observation is not None:
            usable = (
                observation.session_id == self.capture_session
                and observation.profile_id == self.capture_profile
                and type(observation.frame_id) is int and observation.frame_id > self.last_frame
                and math.isfinite(observation.timestamp)
                and self.last_timestamp < observation.timestamp <= now
                and now - observation.timestamp <= DELIVERY_TOLERANCE)
            if usable:
                self.last_frame = observation.frame_id
                self.last_timestamp = observation.timestamp
        if self.state not in ('countdown', 'hold'):
            return
        if now < self.start:
            return
        self.state = 'hold'
        while len(self.pending_records) < 5:
            due = self.start + OFFSETS[len(self.pending_records)]
            if (usable and observation is not None
                    and due <= observation.timestamp <= due + SLOT_TOLERANCE):
                try:
                    feature = extract_feature_vector(observation, self.plan.hand)
                    reason = ''
                except (ValueError, TypeError, OverflowError, KeyError, IndexError) as exc:
                    feature, reason = None, str(exc)
                self._slot(feature, reason, observation.timestamp)
                self.feedback = 'Valid sample' if feature is not None else 'Invalid: ' + reason
                usable = False  # a frame can fill only one scheduled slot
            elif now > due + SLOT_TOLERANCE + DELIVERY_TOLERANCE:
                self._slot(None, 'missed scheduled timestamp', due)
                self.feedback = 'Invalid: no fresh sample at the scheduled time'
            else:
                break
        if len(self.pending_records) == 5 and now >= self.start + 2.:
            self._save(now)

    def _save(self, now):
        records = [*self.records, *self.pending_records]
        features = [*self.features, *self.pending_features]
        metadata = {
            'provenance': 'human', 'chosen_hand': self.plan.hand,
            'raw_video_recorded': False, 'sampling_offsets_seconds': list(OFFSETS),
            'trial_start_times': self.starts,
            'pose_instructions': dict(self.plan.instructions),
            'sessions': [{'session_id': self.session_id, 'split': self.plan.split,
                          'collected_at': self.created_at, 'setup': self.plan.setup,
                          'consent_confirmed_by_operator': True}],
        }
        try:
            save_dataset(self.manifest, records, np.asarray(features, dtype=np.float32).reshape(-1, 60),
                         metadata, vocabulary=self.plan.vocabulary)
        except (OSError, ValueError) as exc:
            self.state = 'save_error'
            self.feedback = f'Save failed: {exc}. Retry saving before continuing.'
            return
        valid = len(self.pending_features)
        self.records, self.features = records, features
        self.pending_records, self.pending_features = [], []
        self.completed += 1
        self.state = self.after_save
        if self.state == 'release' and self.completed == self.total:
            self.state = 'complete'
        self.release_until = now + 1.
        self.feedback = f'Saved {valid}/5 valid samples. Relax your hand.'

    def retry_save(self, now: float):
        self._clock(now)
        if self.state != 'save_error':
            raise ValueError('There is no pending save')
        self._save(now)

    def stop(self, now: float, reason: str = 'Collection cancelled'):
        self._clock(now)
        text(reason, 500)
        if self.state in ('complete', 'cancelled'):
            return
        self.after_save = 'cancelled'
        if self.state == 'save_error':
            self.feedback = 'Unsaved trial retained. Retry saving before closing.'
            return
        if self.state == 'hold' or (self.state == 'countdown' and now >= self.start):
            while len(self.pending_records) < 5:
                self._slot(None, reason, self.start + OFFSETS[len(self.pending_records)])
            self._save(now)
        else:
            self.state = 'cancelled'
        if self.state != 'save_error':
            self.feedback = reason + '. Saved trials remain available.'
