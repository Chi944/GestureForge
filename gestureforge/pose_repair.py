"""Selected-label TRAIN candidates; never overwrites data or installs a model."""

from dataclasses import dataclass, replace
from pathlib import Path
from uuid import uuid4

import numpy as np

from .dataset import DatasetBundle, SampleRecord, dataset_hashes, load_dataset, save_dataset
from .enrolment import EnrolmentPlan
from .profiles import ProfileRecord, ProfileSettings
from .storage import text


@dataclass(frozen=True)
class RepairCandidate:
    manifest: Path
    manifest_sha256: str
    hand: str
    settings: ProfileSettings
    gesture_names: tuple[tuple[str, str], ...]
    rollback_profile_id: str
    rollback_manifest: str
    label: str
    valid_per_label: tuple[tuple[str, int], ...]


class PoseRepair:
    """Snapshot a saved profile's data, collect one label, review a separate candidate.

    Collection uses EnrolmentSession. A candidate is data only; explicit profile
    creation/loading must use the existing ProfileStore/selector/host lifecycle.
    """

    def __init__(self, source: ProfileRecord, label: str, diagnosis: str):
        text(diagnosis, 500)
        self.source = source
        self.label = label
        self.diagnosis = diagnosis
        self.bundle = load_dataset(source.dataset_path)
        self.hashes = dataset_hashes(self.bundle)
        if self.hashes != {'manifest_sha256': source.manifest_sha256,
                           'features_sha256': source.features_sha256}:
            raise ValueError('Original profile data changed; review before repair')
        if self.bundle.vocabulary != source.vocabulary or label not in source.vocabulary.labels:
            raise ValueError('Choose one positive label from the original vocabulary')
        self.participant = self._validate_personal(self.bundle)
        train_labels = {r.intended_label for r in self.bundle.valid_records('train')}
        if train_labels != set(source.vocabulary.labels):
            raise ValueError('Original TRAIN data must cover all four labels')

    def _validate_personal(self, bundle: DatasetBundle) -> str:
        participants = {r.participant_id for r in bundle.records}
        if len(participants) != 1 or not bundle.records:
            raise ValueError('Repair requires exactly one participant')
        if any(r.provenance != 'human' for r in bundle.records):
            raise ValueError('Repair requires consented personal records')
        if (bundle.metadata.get('chosen_hand', self.source.selected_hand) != self.source.selected_hand
                or any((r.valid and r.hand != self.source.selected_hand)
                       or (r.hand is not None and r.hand != self.source.selected_hand)
                       for r in bundle.records)):
            raise ValueError('Repair hand must match the original profile')
        if np.any(np.linalg.norm(bundle.features, axis=1) <= 1e-8):
            raise ValueError('Degenerate features cannot train a repair candidate')
        return next(iter(participants))

    def plan(self, trials: int, setup: str) -> EnrolmentPlan:
        descriptions = self.bundle.metadata.get('pose_instructions', {})
        if not isinstance(descriptions, dict):
            raise ValueError('Original pose instructions must be a label-description mapping')
        names = dict(self.source.gesture_names)
        return EnrolmentPlan(
            self.participant, self.source.selected_hand, self.source.vocabulary,
            tuple((label, descriptions.get(label, names[label])) for label in self.source.vocabulary.labels),
            trials=trials, setup=setup, collection_labels=(self.label,))

    def build_candidate(self, repair_path: Path, output_root: Path, *, reviewed: bool,
                        expected_repair_hashes: dict[str, str] | None = None) -> RepairCandidate:
        if reviewed is not True:
            raise ValueError('Review the collected counts before building a candidate')
        # Reload both sources: a changed file cannot silently replace reviewed input.
        original = load_dataset(self.source.dataset_path)
        if dataset_hashes(original) != self.hashes:
            raise ValueError('Original data changed during repair')
        repair = load_dataset(repair_path)
        if expected_repair_hashes is not None and dataset_hashes(repair) != expected_repair_hashes:
            raise ValueError('Collected data changed after review')
        if repair.vocabulary != original.vocabulary or self._validate_personal(repair) != self.participant:
            raise ValueError('Repair participant/vocabulary must match the original')
        if any(r.split != 'train' or r.intended_label != self.label for r in repair.records):
            raise ValueError('Only the selected positive TRAIN label can repair the profile')
        if repair.metadata.get('collection_complete') is not True:
            raise ValueError('Cancelled or incomplete collection cannot create a candidate')
        trials: dict[str, list[SampleRecord]] = {}
        for record in repair.records:
            trials.setdefault(record.trial_id, []).append(record)
        planned = repair.metadata.get('planned_trials')
        if (type(planned) is not int or not 2 <= planned <= 12 or len(trials) != planned
                or any(len(slots) != 5 or not all(r.valid for r in slots) for slots in trials.values())):
            raise ValueError('Repair needs complete five-valid-slot trials; invalid evidence is retained')
        old_ids = {r.trial_id for r in original.records}
        old_sessions = {r.session_id for r in original.records}
        if any(r.trial_id in old_ids or r.session_id in old_sessions for r in repair.records):
            raise ValueError('Repair must use a new collection session and trial identities')
        records: list[SampleRecord] = []
        rows: list[np.ndarray] = []
        # Replace only this label's TRAIN records; never promote held-out data.
        retained = tuple(r for r in original.records if r.split == 'train' and r.intended_label != self.label)
        for bundle, selected in ((original, retained), (repair, repair.records)):
            for record in selected:
                index = None
                if record.valid and record.feature_index is not None:
                    index = len(rows)
                    rows.append(bundle.features[record.feature_index].copy())
                records.append(replace(record, feature_index=index))
        folder = Path(output_root).resolve() / ('repair-' + uuid4().hex)
        folder.mkdir(parents=True, exist_ok=False)
        metadata = {
            'chosen_hand': self.source.selected_hand, 'provenance': 'human',
            'raw_video_recorded': False, 'pose_instructions': dict(self.plan(2, 'review').instructions),
            'repair': {'label': self.label, 'strategy': 'replace-selected-train-only',
                       'diagnosis': self.diagnosis, 'source_hashes': self.hashes,
                       'repair_hashes': dataset_hashes(repair),
                       'rollback_profile_id': self.source.profile_id,
                       'rollback_manifest': self.source.dataset_path,
                       'held_out_records_copied': False},
        }
        candidate = save_dataset(folder / 'manifest.json', records, np.asarray(rows, dtype=np.float32),
                                 metadata, vocabulary=original.vocabulary)
        assert candidate.manifest_path is not None
        counts = tuple((label, sum(r.intended_label == label for r in candidate.valid_records('train')))
                       for label in original.vocabulary.labels)
        return RepairCandidate(candidate.manifest_path, dataset_hashes(candidate)['manifest_sha256'],
                               self.source.selected_hand, self.source.settings, self.source.gesture_names,
                               self.source.profile_id, self.source.dataset_path, self.label, counts)
