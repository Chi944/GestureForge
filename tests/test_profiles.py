"""Generated numeric fixtures test software only, never participant readiness."""

from dataclasses import replace
import json
import os
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import numpy as np
import pytest

from gestureforge import profiles, storage
from gestureforge.dataset import save_dataset
from gestureforge.fixtures import synthetic_dataset
from gestureforge.profiles import ProfileSettings, ProfileStore
from gestureforge.vocabulary import GestureVocabulary


@pytest.fixture
def numeric_fixture(tmp_path):
    def make(name='dataset', hand='Right', custom=False, seed=304):
        bundle = synthetic_dataset(trials_per_label_per_split=2, seed=seed)
        vocabulary = GestureVocabulary(('G1', 'G2', 'G3')) if custom else bundle.vocabulary
        mapping = dict(zip(bundle.vocabulary.labels, vocabulary.labels, strict=True))
        records = tuple(replace(r, participant_id='TEST_PERSON', hand=hand, provenance='human',
                                intended_label=mapping[r.intended_label]) for r in bundle.records)
        return save_dataset(tmp_path / name, records, bundle.features,
                            {'chosen_hand': hand, 'warning': 'GENERATED SOFTWARE TEST ONLY'},
                            vocabulary=vocabulary if custom else None)
    return make


def test_profile_retains_invalid_detections_without_fitting_them(numeric_fixture, tmp_path):
    bundle = numeric_fixture()
    invalid = tuple(replace(bundle.records[0], trial_id=f'invalid-trial-{index}',
                            valid=False, feature_index=None, hand=hand)
                    for index, hand in enumerate(('Left', None)))
    bundle = save_dataset(tmp_path / 'with-invalid', (*bundle.records, *invalid),
                          bundle.features, bundle.metadata)
    assert bundle.manifest_path is not None
    store = ProfileStore(tmp_path / 'profiles')

    created = store.create('Invalid observations retained', bundle.manifest_path, 'Right', consent=True)
    loaded = store.load(created.record.profile_id)

    assert created.model.model_version == loaded.model.model_version
    assert len(loaded.model.train_features_scaled) == len(bundle.valid_records('train'))
    assert profiles.load_dataset(bundle.manifest_path).records == bundle.records


@pytest.mark.parametrize('hand,selected_hand', [('Left', 'Right'), ('Right', 'Left')])
def test_profile_rejects_valid_wrong_hand_before_fitting(numeric_fixture, tmp_path, monkeypatch,
                                                       hand, selected_hand):
    bundle = numeric_fixture(hand=hand)
    train = Mock(side_effect=AssertionError('Wrong-hand valid rows must not reach model fitting'))
    monkeypatch.setattr(profiles, 'train_model', train)

    with pytest.raises(ValueError, match='dataset hand does not match the selected hand'):
        ProfileStore(tmp_path / 'profiles').create(
            'Wrong hand', bundle.manifest_path, selected_hand, consent=True)

    train.assert_not_called()


@pytest.mark.parametrize('algorithm', ['knn', 'svm'])
@pytest.mark.parametrize('custom,hand', [(False, 'Right'), (True, 'Left')])
def test_round_trip_rebuild_and_cosmetic_rename(numeric_fixture, tmp_path, algorithm, custom, hand):
    bundle = numeric_fixture(custom=custom, hand=hand)
    store = ProfileStore(tmp_path / 'profiles')
    names = {label: 'Pose ' + label for label in bundle.vocabulary.labels}
    created = store.create('个人 profile', bundle.manifest_path, hand, consent=True,
                           settings=ProfileSettings(algorithm, 1.5, 1.2), gesture_names=names)
    profile_id = created.record.profile_id
    names[bundle.vocabulary.labels[0]] = 'External mutation'
    loaded = ProfileStore(store.root).load(profile_id)
    assert loaded.record == created.record
    assert dict(loaded.record.gesture_names) != names
    assert loaded.model.model_version == loaded.model.config.model_version == created.record.model_version
    for row in bundle.features[:5]:
        assert loaded.model.predict(row) == created.model.predict(row)
    assert loaded.selection.readiness_revision == ''
    assert loaded.selection.readiness_reason
    assert loaded.selection.selected_hand == hand
    renamed = store.rename(profile_id, 'New name')
    assert renamed.model_version == created.record.model_version
    assert store.load(profile_id).record.display_name == 'New name'
    assert store.list_ids() == (profile_id,)


@pytest.mark.parametrize('multiplier,margin', [(2, 1.5), (2.0, 1), (2, 1)])
def test_integer_settings_reload_the_same_model(numeric_fixture, tmp_path, multiplier, margin):
    bundle = numeric_fixture()
    store = ProfileStore(tmp_path / 'profiles')
    created = store.create('Integer settings', bundle.manifest_path, 'Right', consent=True,
                           settings=ProfileSettings(multiplier=multiplier, margin=margin))
    loaded = store.load(created.record.profile_id)
    assert loaded.record == created.record
    assert loaded.model.model_version == created.model.model_version
    assert loaded.model.predict(bundle.features[0]) == created.model.predict(bundle.features[0])


def test_two_profiles_delete_independently_without_deleting_data(numeric_fixture, tmp_path):
    bundle = numeric_fixture()
    source = bundle.manifest_path
    before = source.read_bytes()
    store = ProfileStore(tmp_path / 'profiles')
    first = store.create('Same name', source, 'Right', consent=True)
    second = store.create('Same name', source, 'Right', consent=True)
    assert first.record.profile_id != second.record.profile_id
    store.delete(first.record.profile_id)
    assert store.list_ids() == (second.record.profile_id,)
    assert store.load(second.record.profile_id).model.model_version == second.model.model_version
    assert source.read_bytes() == before


@pytest.mark.parametrize('operation', ['create', 'rename'])
def test_failed_atomic_replace_preserves_previous_file(numeric_fixture, tmp_path, monkeypatch, operation):
    bundle = numeric_fixture()
    store = ProfileStore(tmp_path / 'profiles')
    created = store.create('Original', bundle.manifest_path, 'Right', consent=True)
    path = store.root / f'{created.record.profile_id}.json'
    before = path.read_bytes()

    def fail(*args):
        raise OSError('simulated disk failure')

    monkeypatch.setattr(storage.os, 'replace', fail)
    with pytest.raises(OSError, match='disk failure'):
        if operation == 'create':
            store.create('Another', bundle.manifest_path, 'Right', consent=True)
        else:
            store.rename(created.record.profile_id, 'Changed')
    assert path.read_bytes() == before
    assert store.list_ids() == (created.record.profile_id,)
    assert list(store.root.iterdir()) == [path]


@pytest.mark.parametrize('field,value', [
    ('schema_version', 2), ('schema_version', True), ('feature_version', 999),
    ('model_version', 'old-model'), ('selected_hand', 'Both'), ('display_name', ''),
    ('manifest_sha256', 'not-a-hash'), ('dataset_path', 'relative.json'),
    ('vocabulary', {'version': 1, 'action_ids': ['NEXT']}),
    ('gesture_names', {'NEXT': 'one'}), ('unexpected', 'reject me'),
    ('settings', {'preset': 'pickle', 'algorithm': 'knn', 'multiplier': 1.5, 'margin': 1}),
])
def test_corrupt_profile_rejected_without_changing_candidate(numeric_fixture, tmp_path, field, value):
    bundle = numeric_fixture()
    store = ProfileStore(tmp_path / 'profiles')
    active = store.create('Previous working candidate', bundle.manifest_path, 'Right', consent=True)
    path = store.root / f'{active.record.profile_id}.json'
    raw = json.loads(path.read_text())
    raw[field] = value
    path.write_text(json.dumps(raw), encoding='utf-8')
    with pytest.raises(ValueError):
        store.load(active.record.profile_id)
    assert active.record.display_name == 'Previous working candidate'
    assert active.model.predict(bundle.features[0])
    assert json.loads(path.read_text()) == raw  # loading never repairs/writes over evidence


def test_duplicate_json_and_oversized_files_rejected(numeric_fixture, tmp_path):
    bundle = numeric_fixture()
    store = ProfileStore(tmp_path / 'profiles')
    active = store.create('Original', bundle.manifest_path, 'Right', consent=True)
    path = store.root / f'{active.record.profile_id}.json'
    path.write_text('{"schema_version":1,"schema_version":2}', encoding='utf-8')
    with pytest.raises(ValueError, match='duplicate'):
        store.load(active.record.profile_id)
    path.write_text(' ' * 16385, encoding='utf-8')
    with pytest.raises(ValueError, match='size limit'):
        store.load(active.record.profile_id)


@pytest.mark.parametrize('kind', ['metadata', 'numeric', 'settings', 'missing'])
def test_changed_dataset_or_settings_rejected(numeric_fixture, tmp_path, kind):
    bundle = numeric_fixture()
    store = ProfileStore(tmp_path / 'profiles')
    created = store.create('Original', bundle.manifest_path, 'Right', consent=True)
    if kind == 'missing':
        bundle.manifest_path.unlink()
    elif kind in ('metadata', 'numeric'):
        save_dataset(bundle.manifest_path, bundle.records,
                     bundle.features + .1 if kind == 'numeric' else bundle.features,
                     {'chosen_hand': 'Right', 'new_note': 'modified'})
    else:
        path = store.root / f'{created.record.profile_id}.json'
        raw = json.loads(path.read_text())
        raw['settings']['multiplier'] = 2
        path.write_text(json.dumps(raw), encoding='utf-8')
    with pytest.raises((ValueError, FileNotFoundError)):
        store.load(created.record.profile_id)


@pytest.mark.parametrize('changes', [dict(algorithm='invalid'), dict(multiplier=True),
                                    dict(multiplier=0), dict(multiplier=float('nan')),
                                    dict(margin=.9), dict(margin=float('inf'))])
def test_settings_strict_validation(changes):
    with pytest.raises(ValueError):
        ProfileSettings(**changes)


@pytest.mark.parametrize('bad_id', ['../outside', 'CON', 'a:b', 'A'*32, 'a'*33, ''])
def test_invalid_ids_cannot_escape_store(tmp_path, bad_id):
    store = ProfileStore(tmp_path / 'profiles')
    for operation in (store.load, store.delete):
        with pytest.raises(ValueError):
            operation(bad_id)
    assert not store.root.exists()


def test_hand_provenance_identity_and_consent_rejected(numeric_fixture, tmp_path):
    bundle = numeric_fixture()
    store = ProfileStore(tmp_path / 'profiles')
    with pytest.raises(ValueError, match='consent'):
        store.create('Missing consent', bundle.manifest_path, 'Right', consent=False)
    with pytest.raises(ValueError, match='hand'):
        store.create('Wrong hand', bundle.manifest_path, 'Left', consent=True)
    for field, value, message in [('participant_id', 'OTHER', 'one participant'),
                                  ('provenance', 'synthetic', 'synthetic'), ('hand', 'Both', 'hand')]:
        records = tuple(replace(r, **{field: value})
                        if field == 'hand' or r.split == 'validation' else r
                        for r in bundle.records)
        bad = save_dataset(tmp_path / field, records, bundle.features)
        assert bad.manifest_path is not None
        with pytest.raises(ValueError, match=message):
            store.create('Bad data', bad.manifest_path, 'Right', consent=True)
    assert not store.root.exists()


def test_only_training_rows_fit_scaler_and_revision_changes(numeric_fixture, tmp_path):
    bundle = numeric_fixture()
    store = ProfileStore(tmp_path / 'profiles')
    candidate = store.create('Default', bundle.manifest_path, 'Right', consent=True)
    training, _, _ = bundle.training_data()
    np.testing.assert_allclose(candidate.model.scaler.mean_, training.mean(axis=0, dtype=np.float64))
    different = store.create('Different rejection', bundle.manifest_path, 'Right', consent=True,
                             settings=ProfileSettings(multiplier=2))
    assert candidate.model.model_version != different.model.model_version


def test_empty_store_and_missing_profile(tmp_path):
    store = ProfileStore(tmp_path / 'profiles')
    assert store.list_ids() == ()
    with pytest.raises(FileNotFoundError):
        store.load('0'*32)
    assert not store.root.exists()


def test_profile_identity_must_match_filename(numeric_fixture, tmp_path):
    bundle = numeric_fixture()
    store = ProfileStore(tmp_path / 'profiles')
    candidate = store.create('Original', bundle.manifest_path, 'Right', consent=True)
    path = store.root / f'{candidate.record.profile_id}.json'
    raw = json.loads(path.read_text())
    raw['profile_id'] = '0'*32
    path.write_text(json.dumps(raw), encoding='utf-8')
    with pytest.raises(ValueError, match='filename'):
        store.read(candidate.record.profile_id)


def test_generated_id_collision_does_not_overwrite(numeric_fixture, tmp_path, monkeypatch):
    bundle = numeric_fixture()
    store = ProfileStore(tmp_path / 'profiles')
    monkeypatch.setattr(profiles, 'uuid4', lambda: SimpleNamespace(hex='a'*32))
    store.create('Original', bundle.manifest_path, 'Right', consent=True)
    before = (store.root / ('a'*32 + '.json')).read_bytes()
    with pytest.raises(FileExistsError):
        store.create('Collision', bundle.manifest_path, 'Right', consent=True)
    assert (store.root / ('a'*32 + '.json')).read_bytes() == before


def test_failed_delete_retains_profile(numeric_fixture, tmp_path, monkeypatch):
    bundle = numeric_fixture()
    store = ProfileStore(tmp_path / 'profiles')
    candidate = store.create('Original', bundle.manifest_path, 'Right', consent=True)
    def fail(*args):
        raise PermissionError('simulated access denied')
    monkeypatch.setattr(Path, 'unlink', fail)
    with pytest.raises(PermissionError):
        store.delete(candidate.record.profile_id)
    assert store.read(candidate.record.profile_id) == candidate.record


def test_zero_features_and_no_training_are_rejected(numeric_fixture, tmp_path):
    bundle = numeric_fixture()
    store = ProfileStore(tmp_path / 'profiles')
    zero = save_dataset(tmp_path / 'zero', bundle.records, np.zeros_like(bundle.features))
    assert zero.manifest_path is not None
    with pytest.raises(ValueError, match='degenerate'):
        store.create('Zero', zero.manifest_path, 'Right', consent=True)
    x, _, records = bundle.validation_data()
    no_train = save_dataset(tmp_path / 'no-train',
                            tuple(replace(r, feature_index=None) for r in records), x)
    assert no_train.manifest_path is not None
    with pytest.raises(ValueError, match='no samples|at least 5'):
        store.create('No training', no_train.manifest_path, 'Right', consent=True)


def test_sidecar_damage_rejected(numeric_fixture, tmp_path):
    bundle = numeric_fixture()
    store = ProfileStore(tmp_path / 'profiles')
    candidate = store.create('Original', bundle.manifest_path, 'Right', consent=True)
    manifest = json.loads(bundle.manifest_path.read_text())
    sidecar = bundle.manifest_path.with_name(manifest['feature_file'])
    sidecar.write_bytes(b'corrupt numeric archive')
    with pytest.raises(ValueError, match='hash mismatch'):
        store.load(candidate.record.profile_id)


def test_rejects_executable_model_file(tmp_path):
    model_file = tmp_path / 'unsafe.pkl'
    model_file.write_bytes(b'not deserialized')
    with pytest.raises(ValueError, match='JSON dataset'):
        ProfileStore(tmp_path / 'profiles').create('Bad', model_file, 'Right', consent=True)


def test_existing_shell_accepts_candidate_and_failed_load_preserves_it(numeric_fixture, tmp_path):
    os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
    from PySide6.QtWidgets import QApplication
    from gestureforge.app import Window
    from gestureforge.contracts import RoutingMode

    app = QApplication.instance() or QApplication([])
    assert app is not None
    bundle = numeric_fixture(custom=True)
    store = ProfileStore(tmp_path / 'profiles')
    candidate = store.create('Demo', bundle.manifest_path, 'Right', consent=True)
    window = Window(studio=True)
    window._log_failed = True
    try:
        selection = candidate.selection
        window.use_studio_model(candidate.model, selection.selected_hand,
                                selection.profile_id, selection.vocabulary)
        assert window.model is candidate.model
        assert window.worker is None
        assert window.routing is not None
        assert window.routing.snapshot.mode == RoutingMode.PREVIEW
        assert window.pause()
        profile_path = store.root / f'{selection.profile_id}.json'
        profile_path.write_text('{}', encoding='utf-8')
        with pytest.raises(ValueError):
            store.load(selection.profile_id)
        assert window.model is candidate.model
        assert window.profile == selection.profile_id
        assert window.worker is None
        assert 'PAUSED' in str(window.routing.state).upper()
    finally:
        window.close()
