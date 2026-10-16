"""Private profile metadata and validated numeric-model reconstruction (GF-P06).

No camera, active UI selection, readiness certification or OS actions live here.
The caller pauses before loading and installs a returned candidate only on success.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from hashlib import sha256
import json
import math
from pathlib import Path
import re
from uuid import uuid4

import numpy as np

from .contracts import FEATURE_VERSION, validate_identifier
from .dataset import DatasetBundle, dataset_hashes, file_sha256, load_dataset
from .models import Algorithm, PrototypeGestureModel, train_model
from .storage import atomic_write_json, fields, read_json, text, version
from .vocabulary import GestureVocabulary


def _profile_id(value: str) -> str:
    # Generated storage IDs, not display names or participant identities.
    if not isinstance(value, str) or re.fullmatch(r'[0-9a-f]{32}', value) is None:
        raise ValueError('profile ID must be a generated 32-character lowercase hex ID')
    return value


def _digest(value: str) -> str:
    if not isinstance(value, str) or re.fullmatch(r'[0-9a-f]{64}', value) is None:
        raise ValueError('invalid SHA-256 reference')
    return value


@dataclass(frozen=True)
class ProfileSettings:
    algorithm: Algorithm = 'knn'
    multiplier: float = 1.5
    margin: float = 1.0

    def __post_init__(self) -> None:
        if self.algorithm not in ('knn', 'svm'):
            raise ValueError('profile algorithm must be knn or svm')
        for value, minimum, inclusive in ((self.multiplier, 0, False), (self.margin, 1, True)):
            if (type(value) not in (int, float) or not math.isfinite(value)
                    or (value < minimum if inclusive else value <= minimum)):
                raise ValueError('invalid finite rejection settings')
        # Hash the same numeric representation before and after JSON persistence.
        object.__setattr__(self, 'multiplier', float(self.multiplier))
        object.__setattr__(self, 'margin', float(self.margin))

    def to_dict(self) -> dict:
        return {'preset': 'prototype-default-v1', 'algorithm': self.algorithm,
                'multiplier': float(self.multiplier), 'margin': float(self.margin)}

    @classmethod
    def from_mapping(cls, raw: object) -> ProfileSettings:
        data = fields(raw, {'preset', 'algorithm', 'multiplier', 'margin'})
        if data['preset'] != 'prototype-default-v1':
            raise ValueError('unsupported estimator preset')
        return cls(data['algorithm'], data['multiplier'], data['margin'])


@dataclass(frozen=True)
class ProfileRecord:
    profile_id: str
    display_name: str
    selected_hand: str
    vocabulary: GestureVocabulary
    gesture_names: tuple[tuple[str, str], ...]
    dataset_path: str
    manifest_sha256: str
    features_sha256: str
    model_version: str
    settings: ProfileSettings
    schema_version: int = 1
    feature_version: int = FEATURE_VERSION

    def __post_init__(self) -> None:
        version(self.schema_version)
        if type(self.feature_version) is not int or self.feature_version != FEATURE_VERSION:
            raise ValueError('unsupported profile feature version')
        _profile_id(self.profile_id)
        text(self.display_name, 80)
        if self.selected_hand not in ('Left', 'Right'):
            raise ValueError('selected_hand must be Left or Right')
        if not isinstance(self.vocabulary, GestureVocabulary):
            raise ValueError('invalid vocabulary')
        if not isinstance(self.settings, ProfileSettings):
            raise ValueError('invalid settings')
        if (not isinstance(self.gesture_names, tuple)
                or any(not isinstance(p, tuple) or len(p) != 2 for p in self.gesture_names)
                or len(self.gesture_names) != 4
                or {p[0] for p in self.gesture_names} != set(self.vocabulary.labels)):
            raise ValueError('gesture names must cover the four vocabulary labels exactly')
        for _, name in self.gesture_names:
            text(name, 80)
        text(self.dataset_path, 4096)
        if not Path(self.dataset_path).is_absolute() or Path(self.dataset_path).suffix != '.json':
            raise ValueError('dataset reference must be an absolute local JSON manifest path')
        if self.dataset_path.startswith(('\\\\', '//')):
            raise ValueError('network dataset paths are not supported')
        _digest(self.manifest_sha256)
        _digest(self.features_sha256)
        if not isinstance(self.model_version, str) or re.fullmatch(
                r'profile-v1-[0-9a-f]{32}', self.model_version) is None:
            raise ValueError('invalid profile model revision')

    def to_dict(self) -> dict:
        return {
            'schema_version': self.schema_version, 'feature_version': self.feature_version,
            'profile_id': self.profile_id, 'display_name': self.display_name,
            'selected_hand': self.selected_hand, 'vocabulary': self.vocabulary.to_dict(),
            'gesture_names': dict(self.gesture_names), 'dataset_path': self.dataset_path,
            'manifest_sha256': self.manifest_sha256, 'features_sha256': self.features_sha256,
            'model_version': self.model_version, 'settings': self.settings.to_dict(),
        }

    @classmethod
    def from_mapping(cls, raw: object) -> ProfileRecord:
        data = fields(raw, {'schema_version', 'feature_version', 'profile_id', 'display_name',
                            'selected_hand', 'vocabulary', 'gesture_names', 'dataset_path',
                            'manifest_sha256', 'features_sha256', 'model_version', 'settings'})
        vocabulary = GestureVocabulary.from_mapping(data['vocabulary'])
        names = fields(data['gesture_names'], set(vocabulary.labels))
        return cls(
            data['profile_id'], data['display_name'], data['selected_hand'], vocabulary,
            tuple((label, names[label]) for label in vocabulary.labels), data['dataset_path'],
            data['manifest_sha256'], data['features_sha256'], data['model_version'],
            ProfileSettings.from_mapping(data['settings']), data['schema_version'],
            data['feature_version'])


@dataclass(frozen=True)
class ProfileSelection:
    profile_id: str
    display_name: str
    selected_hand: str
    vocabulary: GestureVocabulary
    model_version: str
    readiness_revision: str = ''
    readiness_reason: str = 'Personal rehearsal has not been verified for this selection.'


@dataclass(frozen=True)
class LoadedProfile:
    record: ProfileRecord
    model: PrototypeGestureModel

    @property
    def selection(self) -> ProfileSelection:
        p = self.record
        return ProfileSelection(p.profile_id, p.display_name, p.selected_hand,
                                p.vocabulary, p.model_version)


def _read_training(path: Path, hand: str) -> tuple[DatasetBundle, dict[str, str]]:
    if hand not in ('Left', 'Right'):
        raise ValueError('selected_hand must be Left or Right')
    # Reject ambiguous JSON before using the legacy dataset loader.
    read_json(path)
    before = file_sha256(path)
    bundle = load_dataset(path)
    hashes = dataset_hashes(bundle)
    if before != hashes['manifest_sha256']:
        raise ValueError('dataset changed during loading; retry with a stable dataset')
    participants = {r.participant_id for r in bundle.records}
    if len(participants) != 1:
        raise ValueError('a personal profile requires exactly one participant')
    validate_identifier(next(iter(participants)))
    if any(r.provenance != 'human' for r in bundle.records):
        raise ValueError('synthetic data cannot create a personal profile')
    # Invalid detections retain the observed hand for diagnostics and are never fitted.
    if any(r.valid and r.hand != hand for r in bundle.records):
        raise ValueError('dataset hand does not match the selected hand')
    if bundle.metadata.get('chosen_hand', hand) != hand:
        raise ValueError('dataset chosen_hand conflicts with selection')
    if np.any(np.linalg.norm(bundle.features, axis=1) <= 1e-8):
        raise ValueError('degenerate feature vectors cannot create a personal profile')
    return bundle, hashes


def _rebuild(bundle: DatasetBundle, hashes: dict[str, str], hand: str,
             settings: ProfileSettings) -> PrototypeGestureModel:
    features, labels, records = bundle.training_data()
    model = train_model(features, labels, settings.algorithm, settings.multiplier, settings.margin,
                        groups=[r.trial_id for r in records], vocabulary=bundle.vocabulary)
    # Bind hand and exact persisted input to the already data/settings/library-bound model.
    payload = {'model': model.model_version, 'hand': hand, 'hashes': hashes,
               'feature_version': FEATURE_VERSION}
    revision = 'profile-v1-' + sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:32]
    model.config = replace(model.config, model_version=revision)
    model.model_version = revision
    return model


class ProfileStore:
    """Single-owner local metadata store; references datasets but never deletes them.

    Serialize create/rename/delete on the owning thread. Loading/training can run
    in a worker, but its result is only a candidate until the shell installs it.
    """

    def __init__(self, root: str | Path):
        self.root = Path(root).resolve()

    def _path(self, profile_id: str) -> Path:
        path = self.root / f'{_profile_id(profile_id)}.json'
        if path.is_symlink() or path.resolve().parent != self.root:
            raise ValueError('profile path must stay inside its private store')
        return path

    def list_ids(self) -> tuple[str, ...]:
        # Listing is not successful model validation; read/load reports corrupt entries.
        return tuple(sorted(p.stem for p in self.root.glob('*.json')
                            if re.fullmatch(r'[0-9a-f]{32}', p.stem)))

    def read(self, profile_id: str) -> ProfileRecord:
        record = ProfileRecord.from_mapping(read_json(self._path(profile_id), limit=16384))
        if record.profile_id != profile_id:
            raise ValueError('profile identity differs from its filename')
        return record

    def create(self, display_name: str, dataset_path: str | Path, selected_hand: str,
               *, consent: bool, settings: ProfileSettings = ProfileSettings(),
               gesture_names: dict[str, str] | None = None) -> LoadedProfile:
        if consent is not True:
            raise ValueError('explicit internal-use consent is required')
        text(display_name, 80)
        if not isinstance(settings, ProfileSettings):
            raise ValueError('invalid settings')
        source = Path(dataset_path).resolve()
        if source.is_dir():
            source = source / 'manifest.json'
        if str(source).startswith(('\\\\', '//')) or source.suffix != '.json':
            raise ValueError('choose a local JSON dataset manifest')
        bundle, hashes = _read_training(source, selected_hand)
        names = fields(gesture_names if gesture_names is not None else
                       {label: label for label in bundle.vocabulary.labels},
                       set(bundle.vocabulary.labels))
        model = _rebuild(bundle, hashes, selected_hand, settings)
        record = ProfileRecord(
            uuid4().hex, display_name, selected_hand, bundle.vocabulary,
            tuple((label, names[label]) for label in bundle.vocabulary.labels), str(source),
            hashes['manifest_sha256'], hashes['features_sha256'], model.model_version, settings)
        path = self._path(record.profile_id)
        if path.exists():
            raise FileExistsError('generated profile ID already exists')
        atomic_write_json(path, record.to_dict(), limit=16384)
        return LoadedProfile(record, model)

    def load(self, profile_id: str) -> LoadedProfile:
        record = self.read(profile_id)
        bundle, hashes = _read_training(Path(record.dataset_path), record.selected_hand)
        if hashes != {'manifest_sha256': record.manifest_sha256,
                      'features_sha256': record.features_sha256}:
            raise ValueError('profile dataset changed; create a new reviewed revision')
        if bundle.vocabulary != record.vocabulary:
            raise ValueError('profile vocabulary does not match its dataset')
        model = _rebuild(bundle, hashes, record.selected_hand, record.settings)
        if model.model_version != record.model_version:
            raise ValueError('model revision changed; review data, settings and library versions')
        return LoadedProfile(record, model)

    def rename(self, profile_id: str, display_name: str) -> ProfileRecord:
        updated = replace(self.read(profile_id), display_name=display_name)
        atomic_write_json(self._path(profile_id), updated.to_dict(), limit=16384)
        return updated

    def delete(self, profile_id: str) -> None:
        # Deliberately not recursive; original numeric datasets may be shared by profiles.
        self._path(profile_id).unlink()
