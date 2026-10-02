"""GF-P11 descriptive audit of saved GF-P28 baseline predictions; no fitting/tuning."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from hashlib import sha256
import json
import math
from pathlib import Path
from typing import Any

from .evaluate import classification_metrics
from .storage import decode_json
from .vocabulary import LEGACY_VOCABULARY

LABELS = LEGACY_VOCABULARY.labels
PEOPLE = ('P01', 'P02', 'P03')
PROTOCOL = 'GF-P28 leave-one-person-out development baseline; not final independent testing'
LIMIT = 16 * 1024 * 1024


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _samples(rows: list[dict[str, Any]], negative: bool) -> dict[str, Any]:
    """The baseline encodes invalid detection as raw UNKNOWN without distances."""
    expected = ('UNKNOWN',) if negative else LABELS
    _require(isinstance(rows, list) and len(rows) == (40 if negative else 320),
             'Expected all scheduled baseline samples (320 positive / 40 negative)')
    by_trial: dict[str, dict[int, str]] = defaultdict(dict)
    true_labels: dict[str, str] = {}
    outcomes: dict[str, Counter] = {label: Counter() for label in expected}
    raw_confusion = {label: {column: 0 for column in (*LABELS, 'UNKNOWN')}
                     for label in expected}
    ratios: dict[str, list[float]] = defaultdict(list)
    reasons: Counter = Counter()
    for row in rows:
        label, raw, scored = row['true_label'], row['raw_label'], row['scored_label']
        accepted, trial, slot = row['accepted'], row['trial_id'], row['sample_index']
        _require(label in expected and raw in (*LABELS, 'UNKNOWN'), 'Unexpected prediction label')
        _require(type(accepted) is bool and scored == (raw if accepted else 'UNKNOWN'),
                 'Inconsistent accepted/scored label')
        _require(isinstance(trial, str) and bool(trial) and type(slot) is int and 0 <= slot < 5,
                 'Invalid trial/slot identity')
        _require(slot not in by_trial[trial], 'Duplicate scheduled sample')
        _require(trial not in true_labels or true_labels[trial] == label,
                 'Mixed intended labels in one trial')
        by_trial[trial][slot] = scored
        true_labels[trial] = label
        raw_confusion[label][raw] += 1
        if raw == 'UNKNOWN':
            _require(not accepted and 'distance' not in row and 'threshold' not in row,
                     'Invalid-detection encoding conflicts with classifier output')
            outcome = 'invalid_detection'
        else:
            distance, threshold = row['distance'], row['threshold']
            _require(all(type(value) in (int, float) and math.isfinite(value) and value >= 0
                         for value in (distance, threshold)), 'Invalid distance/threshold')
            if not accepted:
                outcome = 'classifier_rejection'
            elif negative:
                outcome = 'accepted_neutral' if raw == 'NEUTRAL' else 'accepted_action'
            else:
                outcome = 'accepted_correct' if raw == label else 'accepted_wrong'
            if threshold > 0:
                ratio = distance / threshold
                _require(math.isfinite(ratio), 'Distance/threshold ratio is not finite')
                ratios[f'{label}:{outcome}'].append(ratio)
        outcomes[label][outcome] += 1
        if not accepted:
            _require(isinstance(row['reason'], str) and bool(row['reason']),
                     'Rejected/invalid sample needs a reason')
            reasons[row['reason']] += 1
    trials = []
    for trial, slots in sorted(by_trial.items()):
        _require(set(slots) == set(range(5)), 'Missing scheduled slot')
        predicted, votes = Counter(slots.values()).most_common(1)[0]
        trials.append({'trial_id': trial, 'true_label': true_labels[trial],
                       'predicted_label': predicted if votes >= 3 else 'UNKNOWN'})
    counts = Counter(row['true_label'] for row in trials)
    _require(all(counts[label] == (8 if negative else 16) for label in expected),
             'Unexpected number of trials per label')
    ratio_summary = {key: {'count': len(values), 'minimum': min(values),
                           'mean': sum(values) / len(values), 'maximum': max(values)}
                     for key, values in sorted(ratios.items())}
    return {'trials': trials, 'outcomes': {k: dict(v) for k, v in outcomes.items()},
            'raw_confusion': raw_confusion, 'reasons': dict(reasons),
            'distance_threshold_ratios': ratio_summary}


def diagnose(report: dict[str, Any]) -> dict[str, Any]:
    """Recompute summaries; reject incomplete folds or conflicting saved counts."""
    try:
        _require(report['protocol'] == PROTOCOL, 'Expected the saved GF-P28 baseline protocol')
        folds = report['folds']
        _require(isinstance(folds, list) and len(folds) == 6, 'Expected six person/model folds')
        seen = set()
        summaries = []
        for fold in folds:
            person, algorithm = fold['held_out'], fold['algorithm']
            _require(person in PEOPLE and algorithm in ('knn', 'svm'), 'Unknown person/model')
            key = (person, algorithm)
            _require(key not in seen, 'Duplicate person/model fold')
            seen.add(key)
            _require(sorted(fold['training_people']) == sorted(set(PEOPLE) - {person}),
                     'Held-out person must not occur in training people')
            positive = _samples(fold['sample_predictions'], False)
            negative = _samples(fold['negative_predictions'], True)
            def sort_trials(rows):
                return sorted(rows, key=lambda row: row['trial_id'])

            _require(not {row['trial_id'] for row in positive['trials']}.intersection(
                row['trial_id'] for row in negative['trials']), 'Positive/negative trial overlap')
            _require(positive['trials'] == sort_trials(fold['trial_predictions']),
                     'Saved positive trials conflict with sample votes')
            _require(negative['trials'] == sort_trials(fold['negative_metrics']['trial_predictions']),
                     'Saved negative trials conflict with sample votes')
            correct = sum(t['true_label'] == t['predicted_label'] for t in positive['trials'])
            _require(fold['total_trials'] == 64 and fold['correct_trials'] == correct,
                     'Saved positive counts conflict with sample votes')
            metrics = classification_metrics(positive['trials'])
            _require(fold['metrics']['confusion'] == metrics['confusion'] and
                     math.isclose(fold['metrics']['macro_f1'], metrics['macro_f1'], abs_tol=1e-12),
                     'Saved positive metrics conflict with sample votes')
            counts = Counter(negative['outcomes']['UNKNOWN'])
            valid = 40 - counts['invalid_detection']
            expected_metrics = {
                'valid_feature_samples': valid,
                'invalid_detection_samples': counts['invalid_detection'],
                'valid_feature_rejections': counts['classifier_rejection'],
                'accepted_neutral_predictions': counts['accepted_neutral'],
                'accepted_command_predictions': counts['accepted_action'],
            }
            _require(all(fold['negative_metrics'][k] == value for k, value in expected_metrics.items()),
                     'Saved negative metrics conflict with sample outcomes')
            negative_rates = {key: counts[key] / valid if valid else None for key in
                              ('classifier_rejection', 'accepted_neutral', 'accepted_action')}
            summaries.append({
                'held_out': person, 'algorithm': algorithm,
                'training_people': fold['training_people'],
                'model_version': fold['model']['model_version'],
                'positive_trial_metrics': metrics,
                'neutral_trial_outcomes': metrics['confusion']['NEUTRAL'],
                'positive_sample_outcomes': positive['outcomes'],
                'positive_raw_confusion': positive['raw_confusion'],
                'positive_rejection_reasons': positive['reasons'],
                'negative_sample_outcomes': dict(counts),
                'negative_rates_among_valid_features': negative_rates,
                'negative_trial_votes': dict(Counter(t['predicted_label'] for t in negative['trials'])),
                'negative_rejection_reasons': negative['reasons'],
                'positive_distance_threshold_ratios': positive['distance_threshold_ratios'],
                'negative_distance_threshold_ratios': negative['distance_threshold_ratios'],
            })
        return {'schema_version': 1, 'analysis': 'GF-P11 descriptive baseline diagnosis',
                'folds': summaries,
                'limits': ['No model fitting, parameter selection or threshold changes',
                           'Invalid detections are separate from classifier rejections',
                           'Accepted NEUTRAL is not UNKNOWN rejection',
                           'Sample/trial votes do not measure executed controller actions',
                           'Distance ratios do not prove physical causes or calibrated confidence',
                           'Contains participant results: keep private; no release readiness claim']}
    except (KeyError, TypeError, AttributeError) as exc:
        raise ValueError(f'Malformed baseline report: {exc}') from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    if args.output.exists():
        raise FileExistsError('Refusing to replace existing evidence')
    with args.report.open('rb') as stream:
        source = stream.read(LIMIT + 1)
    _require(len(source) <= LIMIT, 'Baseline report exceeds size limit')
    result = diagnose(decode_json(source))
    result['source_report_sha256'] = sha256(source).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=2, sort_keys=True, allow_nan=False)
    print('Saved descriptive diagnosis. Keep it private; no model was fitted or selected.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
