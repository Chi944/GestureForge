"""GF-P28 fixed-configuration, participant-separated development evaluation."""

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
from typing import Any

import numpy as np

from gestureforge.dataset import dataset_hashes, load_dataset, merge_datasets
from gestureforge.evaluate import (
    _predict_records, classification_metrics, trial_majority_predictions,
    validation_negative_metrics,
)
from gestureforge.models import Algorithm, train_model
from gestureforge.vocabulary import LEGACY_VOCABULARY


def require(condition, message):
    if not condition:
        raise ValueError(message)


def load_validated_people(root):
    participants = {}
    audit: dict[str, Any] = {}
    hashes: dict[str, Any] = {}
    seen_sessions: set[str] = set()
    seen_trials: set[str] = set()
    row_owners: dict[str, tuple[str, str]] = {}
    for person in ('P01', 'P02', 'P03'):
        bundles = []
        audit[person] = {}
        hashes[person] = {}
        for folder, split in (('session-1', 'train'), ('session-2', 'validation'),
                              ('negatives', 'validation_negative')):
            bundle = load_dataset(root / person / folder / 'manifest.json')
            require(bundle.vocabulary == LEGACY_VOCABULARY, 'Unexpected vocabulary')
            require(all(r.participant_id == person and r.hand == 'Right'
                       and r.provenance == 'human' and r.split == split
                       for r in bundle.records), 'Participant/hand/provenance/split mismatch')
            sessions = {r.session_id for r in bundle.records}
            require(len(sessions) == 1 and not seen_sessions.intersection(sessions), 'Session overlap')
            seen_sessions.update(sessions)
            trial_ids = {r.trial_id for r in bundle.records}
            require(not seen_trials.intersection(trial_ids), 'Trial overlap across datasets')
            seen_trials.update(trial_ids)
            expected_labels = ('UNKNOWN',) if folder == 'negatives' else bundle.vocabulary.labels
            require({r.intended_label for r in bundle.records} == set(expected_labels), 'Wrong labels')
            for label in expected_labels:
                require(len({r.trial_id for r in bundle.records if r.intended_label == label}) == 8,
                        'Expected eight trials per label')
            for trial in trial_ids:
                require({r.sample_index for r in bundle.records if r.trial_id == trial} == set(range(5)),
                        'Expected five scheduled slots per trial')
            for record in bundle.valid_records():
                row = bundle.features[record.feature_index]
                digest = sha256(row.tobytes()).hexdigest()
                require(digest not in row_owners or row_owners[digest] == (person, folder),
                        'Exact feature duplicate across sessions or people')
                row_owners[digest] = (person, folder)
            audit[person][folder] = {
                'trials': len(trial_ids), 'scheduled': len(bundle.records),
                'valid': sum(r.valid for r in bundle.records),
                'invalid': sum(not r.valid for r in bundle.records),
                'invalid_reasons': dict(Counter(r.validity_reason for r in bundle.records if not r.valid)),
            }
            hashes[person][folder] = dataset_hashes(bundle)
            bundles.append(bundle)
        participants[person] = merge_datasets(bundles)
    return participants, audit, hashes


def evaluate_people(participants, audit, hashes):
    algorithms: tuple[Algorithm, ...] = ("knn", "svm")
    folds = []
    for held_out in participants:
        training_people = sorted(set(participants) - {held_out})
        matrices, labels, groups = [], [], []
        for person in training_people:
            bundle = participants[person]
            for record in bundle.valid_records():
                if record.split in ('train', 'validation'):
                    matrices.append(bundle.features[record.feature_index])
                    labels.append(record.intended_label)
                    groups.append(record.trial_id)
        x = np.asarray(matrices, dtype=np.float32)
        held_bundle = participants[held_out]
        positives = tuple(r for r in held_bundle.records if r.split in ('train', 'validation'))
        negatives = tuple(r for r in held_bundle.records if r.split == 'validation_negative')
        require(not set(groups).intersection(r.trial_id for r in held_bundle.records),
                'Trial overlap between fitting and scoring')
        for algorithm in algorithms:
            model = train_model(x, labels, algorithm=algorithm, multiplier=1.5, margin=1.0,
                                groups=groups, vocabulary=held_bundle.vocabulary)
            np.testing.assert_allclose(model.scaler.mean_, x.mean(axis=0, dtype=np.float64))
            predictions = _predict_records(model, held_bundle, positives)
            negative_predictions = _predict_records(model, held_bundle, negatives)
            trials = trial_majority_predictions(positives, predictions)
            negative_metrics = validation_negative_metrics(negative_predictions, held_bundle.vocabulary)
            valid_negative_count = sum(r.valid for r in negatives)
            accepted = negative_metrics['accepted_command_predictions']
            valid_predictions = [p for r, p in zip(negatives, negative_predictions, strict=True)
                                 if r.valid]
            negative_metrics['valid_feature_rejections'] = sum(
                not p['accepted'] for p in valid_predictions)
            negative_metrics['accepted_neutral_predictions'] = sum(
                p['accepted'] and p['raw_label'] == 'NEUTRAL' for p in valid_predictions)
            negative_metrics['trial_predictions'] = trial_majority_predictions(
                negatives, negative_predictions)
            negative_metrics.update({
                'valid_feature_samples': valid_negative_count,
                'invalid_detection_samples': len(negatives) - valid_negative_count,
                'accepted_fraction_among_valid_features': accepted / valid_negative_count
                if valid_negative_count else None,
            })
            folds.append({
                'held_out': held_out, 'training_people': training_people,
                'algorithm': algorithm, 'training_samples': len(x),
                'model': model.to_config(),
                'scaler_mean': model.scaler.mean_.tolist(),
                'scaler_scale': model.scaler.scale_.tolist(),
                'metrics': classification_metrics(trials, held_bundle.vocabulary),
                'correct_trials': sum(t['true_label'] == t['predicted_label'] for t in trials),
                'total_trials': len(trials), 'negative_metrics': negative_metrics,
                'trial_predictions': trials,
                'sample_predictions': predictions, 'negative_predictions': negative_predictions,
            })
    return {
        'protocol': 'GF-P28 leave-one-person-out development baseline; not final independent testing',
        'fixed_settings': {'knn_k': 5, 'knn_weights': 'distance', 'svm_C': 1,
                           'svm_gamma': 'scale', 'rejection_multiplier': 1.5, 'margin': 1.0},
        'selection_policy': 'Fixed defaults before reading fold outputs; no parameter search or selection',
        'training_policy': 'Both positive sessions of the other two participants; no negatives in training',
        'limits': ['Three team members only', 'Classifier predictions are not controller actions',
                   'Invalid negative detections are not successful classifier rejections',
                   'No distribution permission or readiness is established by this evaluation'],
        'data_audit': audit, 'input_hashes': hashes, 'folds': folds,
    }


def run(root):
    return evaluate_people(*load_validated_people(root))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError('Refusing to replace existing evaluation evidence')
    report = run(args.root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', encoding='utf-8') as handle:
        json.dump(report, handle, indent=2, sort_keys=True)
    for fold in report['folds']:
        print(f"{fold['held_out']} {fold['algorithm']}: "
              f"{fold['correct_trials']}/{fold['total_trials']} correct trials, "
              f"macro-F1={fold['metrics']['macro_f1']:.4f}, "
              f"negative accepted={fold['negative_metrics']['accepted_command_predictions']}/"
              f"{fold['negative_metrics']['valid_feature_samples']} valid features")
if __name__ == '__main__':
    main()
