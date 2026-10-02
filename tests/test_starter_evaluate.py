"""Synthetic evaluator checks, not evidence of participant performance."""

from dataclasses import replace

import numpy as np
import pytest

from gestureforge import starter_evaluate as starter
from gestureforge.dataset import SampleRecord, save_dataset
from gestureforge.vocabulary import LEGACY_VOCABULARY


@pytest.fixture
def starter_tree(tmp_path):
    rng = np.random.default_rng(304)
    for person in ('P01', 'P02', 'P03'):
        for folder, split in (('session-1', 'train'), ('session-2', 'validation'),
                              ('negatives', 'validation_negative')):
            labels = ('UNKNOWN',) if folder == 'negatives' else LEGACY_VOCABULARY.labels
            records: list[SampleRecord] = []
            features: list[np.ndarray] = []
            for label_index, label in enumerate(labels):
                for trial in range(8):
                    for slot in range(5):
                        valid = not (person == 'P01' and trial == 0 and slot == 0)
                        if valid:
                            row = rng.normal(0, .02, 60)
                            row[label_index * 12:label_index * 12 + 12] += 2
                            if folder == 'negatives':
                                row += 100
                            features.append(row)
                        records.append(SampleRecord(
                            participant_id=person, session_id=f'{person}-{folder}',
                            trial_id=f'{person}-{folder}-{label}-{trial}',
                            intended_label=label, split=split, sample_index=slot,
                            timestamp=float(len(records)), valid=valid,
                            feature_index=len(features)-1 if valid else None,
                            validity_reason='' if valid else 'no_hand', hand='Right',
                            # Exercise production provenance validation using generated test data.
                            provenance='human'))
            save_dataset(tmp_path / person / folder, records, np.asarray(features),
                         {'warning': 'SYNTHETIC SOFTWARE TEST ONLY'})
    return tmp_path


def test_person_separation_invalid_accounting_and_reproduction(starter_tree, monkeypatch):
    original = starter.train_model
    calls = []

    def checked_train(x, labels, **kwargs):
        groups = kwargs['groups']
        people = {g.split('-')[0] for g in groups}
        assert len(people) == 2
        assert 'UNKNOWN' not in labels
        model = original(x, labels, **kwargs)
        np.testing.assert_allclose(model.scaler.mean_, x.mean(axis=0, dtype=np.float64))
        calls.append(people)
        return model

    monkeypatch.setattr(starter, 'train_model', checked_train)
    first = starter.run(starter_tree)
    second = starter.run(starter_tree)
    from gestureforge.starter_diagnose import diagnose
    diagnostic = diagnose(first)
    assert len(diagnostic['folds']) == 6
    assert diagnostic['folds'][0]['negative_sample_outcomes']['invalid_detection'] == 1
    assert len(first['folds']) == 6
    assert first['data_audit']['P01']['negatives']['invalid'] == 1
    for index, (a, b) in enumerate(zip(first['folds'], second['folds'], strict=True)):
        assert a['held_out'] not in calls[index]
        assert a['total_trials'] == 64
        assert a['trial_predictions'] == b['trial_predictions']
        assert a['model']['model_version'] == b['model']['model_version']
        if a['held_out'] == 'P01':
            assert a['negative_metrics']['valid_feature_samples'] == 39
            assert a['negative_metrics']['invalid_detection_samples'] == 1
            invalid = [p for p in a['sample_predictions'] if p['reason'] == 'no_hand']
            assert invalid and all(p['scored_label'] == 'UNKNOWN' for p in invalid)


@pytest.mark.parametrize('field,value', [('participant_id', 'P99'), ('hand', 'Left'),
                                        ('provenance', 'synthetic'), ('split', 'train')])
def test_reject_wrong_identity_hand_provenance_split(starter_tree, monkeypatch, field, value):
    original = starter.load_dataset

    def changed(path):
        bundle = original(path)
        if path.parent.name == 'negatives':
            return replace(bundle, records=tuple(replace(r, **{field: value}) for r in bundle.records))
        return bundle

    monkeypatch.setattr(starter, 'load_dataset', changed)
    with pytest.raises(ValueError, match='mismatch'):
        starter.run(starter_tree)


def test_reject_missing_scheduled_slot(starter_tree, monkeypatch):
    original = starter.load_dataset

    def changed(path):
        bundle = original(path)
        return replace(bundle, records=bundle.records[1:])

    monkeypatch.setattr(starter, 'load_dataset', changed)
    with pytest.raises(ValueError, match='five scheduled'):
        starter.run(starter_tree)


def test_existing_output_untouched(tmp_path, monkeypatch):
    output = tmp_path / 'report.json'
    output.write_text('previous evidence', encoding='utf-8')
    monkeypatch.setattr('sys.argv', ['starter', '--root', str(tmp_path), '--output', str(output)])
    with pytest.raises(FileExistsError):
        starter.main()
    assert output.read_text(encoding='utf-8') == 'previous evidence'


def test_held_out_changes_do_not_affect_its_fitted_model(starter_tree, monkeypatch):
    baseline = starter.run(starter_tree)
    original = starter.load_dataset

    def changed(path):
        bundle = original(path)
        if path.parent.parent.name == 'P01':
            return replace(bundle, features=bundle.features + 50)
        return bundle

    monkeypatch.setattr(starter, 'load_dataset', changed)
    modified = starter.run(starter_tree)
    for a, b in zip(baseline['folds'][:2], modified['folds'][:2], strict=True):
        assert a['held_out'] == b['held_out'] == 'P01'
        assert a['model']['model_version'] == b['model']['model_version']
        assert a['model']['thresholds'] == b['model']['thresholds']
        assert a['scaler_mean'] == b['scaler_mean']
        assert a['scaler_scale'] == b['scaler_scale']
        assert a['trial_predictions'] != b['trial_predictions']


def test_reject_reused_session(starter_tree, monkeypatch):
    original = starter.load_dataset

    def changed(path):
        bundle = original(path)
        return replace(bundle, records=tuple(replace(r, session_id='reused') for r in bundle.records))

    monkeypatch.setattr(starter, 'load_dataset', changed)
    with pytest.raises(ValueError, match='Session overlap'):
        starter.run(starter_tree)


def test_reject_exact_features_copied_between_sessions(starter_tree, monkeypatch):
    original = starter.load_dataset

    def changed(path):
        bundle = original(path)
        features = bundle.features.copy()
        features[0] = np.ones(60)
        return replace(bundle, features=features)

    monkeypatch.setattr(starter, 'load_dataset', changed)
    with pytest.raises(ValueError, match='Exact feature duplicate'):
        starter.run(starter_tree)
