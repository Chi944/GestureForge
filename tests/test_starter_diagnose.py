"""Generated prediction records exercise diagnostics, not real recognition."""

from collections import Counter
from copy import deepcopy
from hashlib import sha256
import json
import math
from typing import Any

import pytest

from gestureforge.evaluate import classification_metrics
from gestureforge import starter_diagnose as diagnosis


def votes(rows):
    trials: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        trials.setdefault(row['trial_id'], []).append(row)
    result = []
    for trial, samples in sorted(trials.items()):
        label, count = Counter(r['scored_label'] for r in samples).most_common(1)[0]
        result.append({'trial_id': trial, 'true_label': samples[0]['true_label'],
                       'predicted_label': label if count >= 3 else 'UNKNOWN'})
    return result


@pytest.fixture
def saved_report():
    positives = []
    for label in diagnosis.LABELS:
        for trial in range(16):
            for slot in range(5):
                raw = 'PREVIOUS' if label == 'NEUTRAL' and trial == 0 else label
                positives.append({'trial_id': f'{label}-{trial}', 'sample_index': slot,
                                  'true_label': label, 'raw_label': raw, 'scored_label': raw,
                                  'accepted': True, 'reason': '', 'distance': 0.5, 'threshold': 1.0})
    negatives = []
    for trial in range(8):
        for slot in range(5):
            raw = ('NEXT', 'NEUTRAL', 'NEXT', 'UNKNOWN', 'UNKNOWN')[slot]
            row = {'trial_id': f'negative-{trial}', 'sample_index': slot,
                   'true_label': 'UNKNOWN', 'raw_label': raw,
                   'scored_label': raw if slot < 2 else 'UNKNOWN', 'accepted': slot < 2,
                   'reason': '' if slot < 2 else ('distance_rejection' if slot == 2 else 'no_hand')}
            if slot < 3:
                row.update(distance=0.5 if slot < 2 else 2.0, threshold=1.0)
            negatives.append(row)
    trials = votes(positives)
    return {'protocol': diagnosis.PROTOCOL, 'folds': [
        {'held_out': person, 'algorithm': algorithm,
         'training_people': sorted(set(diagnosis.PEOPLE) - {person}),
         'model': {'model_version': 'generated-test-v1'},
         'sample_predictions': deepcopy(positives), 'negative_predictions': deepcopy(negatives),
         'trial_predictions': deepcopy(trials), 'total_trials': 64, 'correct_trials': 63,
         'metrics': classification_metrics(trials),
         'negative_metrics': {'trial_predictions': votes(negatives), 'valid_feature_samples': 24,
                              'invalid_detection_samples': 16, 'valid_feature_rejections': 8,
                              'accepted_neutral_predictions': 8, 'accepted_command_predictions': 8}}
        for person in diagnosis.PEOPLE for algorithm in ('knn', 'svm')]}


def test_separates_invalid_rejection_neutral_and_actions_without_mutation(saved_report):
    original = deepcopy(saved_report)
    first = diagnosis.diagnose(saved_report)
    assert first == diagnosis.diagnose(saved_report)
    assert saved_report == original
    assert len(first['folds']) == 6
    for fold in first['folds']:
        assert fold['neutral_trial_outcomes']['NEUTRAL'] == 15
        assert fold['neutral_trial_outcomes']['PREVIOUS'] == 1
        assert fold['positive_sample_outcomes']['NEUTRAL'] == {
            'accepted_correct': 75, 'accepted_wrong': 5}
        assert fold['negative_sample_outcomes'] == {
            'accepted_action': 8, 'accepted_neutral': 8, 'classifier_rejection': 8,
            'invalid_detection': 16}
        assert fold['negative_rates_among_valid_features']['classifier_rejection'] == 1 / 3
        assert fold['negative_trial_votes'] == {'UNKNOWN': 8}
        assert fold['negative_distance_threshold_ratios']['UNKNOWN:classifier_rejection']['mean'] == 2
        assert 'trial_id' not in json.dumps(fold)  # aggregate output omits trial/sample identities


def test_all_invalid_negatives_have_no_rejection_rate(saved_report):
    for fold in saved_report['folds']:
        for row in fold['negative_predictions']:
            row.update(raw_label='UNKNOWN', scored_label='UNKNOWN', accepted=False, reason='no_hand')
            row.pop('distance', None)
            row.pop('threshold', None)
        fold['negative_metrics'].update(valid_feature_samples=0, invalid_detection_samples=40,
                                         valid_feature_rejections=0, accepted_neutral_predictions=0,
                                         accepted_command_predictions=0)
    output = diagnosis.diagnose(saved_report)
    assert all(value is None for value in
               output['folds'][0]['negative_rates_among_valid_features'].values())


def test_large_finite_ratios_keep_finite_mean(saved_report):
    fold = saved_report['folds'][0]
    for row in (*fold['sample_predictions'], *fold['negative_predictions']):
        if 'distance' in row:
            row['distance'] = 1e308
            row['threshold'] = 1.0
    output = diagnosis.diagnose(saved_report)
    positive = output['folds'][0]['positive_distance_threshold_ratios']
    negative = output['folds'][0]['negative_distance_threshold_ratios']
    assert math.isfinite(positive['NEUTRAL:accepted_wrong']['mean'])
    assert math.isfinite(positive['NEXT:accepted_correct']['mean'])
    assert math.isfinite(negative['UNKNOWN:classifier_rejection']['mean'])


@pytest.mark.parametrize('defect', ['missing_fold', 'leakage', 'duplicate_fold', 'duplicate_slot',
                                   'bad_votes', 'bad_counts', 'nonfinite', 'accepted_invalid'])
def test_inconsistent_or_incomplete_evidence_rejected(saved_report, defect):
    fold = saved_report['folds'][0]
    if defect == 'missing_fold':
        saved_report['folds'].pop()
    elif defect == 'leakage':
        fold['training_people'][0] = fold['held_out']
    elif defect == 'duplicate_fold':
        saved_report['folds'][1] = deepcopy(fold)
    elif defect == 'duplicate_slot':
        fold['sample_predictions'][1] = deepcopy(fold['sample_predictions'][0])
    elif defect == 'bad_votes':
        fold['trial_predictions'][0]['predicted_label'] = 'UNKNOWN'
    elif defect == 'bad_counts':
        fold['negative_metrics']['valid_feature_rejections'] += 1
    elif defect == 'nonfinite':
        fold['sample_predictions'][0]['distance'] = float('nan')
    else:
        fold['negative_predictions'][-1]['accepted'] = True
    with pytest.raises(ValueError):
        diagnosis.diagnose(saved_report)


def test_cli_records_source_hash_and_never_overwrites(tmp_path, saved_report):
    source, target = tmp_path / 'baseline.json', tmp_path / 'diagnosis.json'
    source.write_text(json.dumps(saved_report), encoding='utf-8')
    before = source.read_bytes()
    assert diagnosis.main(['--report', str(source), '--output', str(target)]) == 0
    output = json.loads(target.read_text(encoding='utf-8'))
    assert output['source_report_sha256'] == sha256(before).hexdigest()
    previous_output = target.read_bytes()
    with pytest.raises(FileExistsError):
        diagnosis.main(['--report', str(source), '--output', str(target)])
    with pytest.raises(FileExistsError):
        diagnosis.main(['--report', str(source), '--output', str(source)])
    assert source.read_bytes() == before
    assert target.read_bytes() == previous_output


def test_cli_rejects_duplicate_json_keys_without_output(tmp_path):
    source, target = tmp_path / 'bad.json', tmp_path / 'diagnosis.json'
    source.write_text('{"folds": [], "folds": []}', encoding='utf-8')
    with pytest.raises(ValueError, match='duplicate JSON key'):
        diagnosis.main(['--report', str(source), '--output', str(target)])
    assert not target.exists()


def test_cli_serialization_failure_leaves_no_partial_output(tmp_path, saved_report, monkeypatch):
    source, target = tmp_path / 'baseline.json', tmp_path / 'diagnosis.json'
    source.write_text(json.dumps(saved_report), encoding='utf-8')
    monkeypatch.setattr(diagnosis, 'diagnose', lambda report: {'bad': float('nan')})
    with pytest.raises(ValueError, match='Out of range float values'):
        diagnosis.main(['--report', str(source), '--output', str(target)])
    assert not target.exists()
