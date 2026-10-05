"""Generated software fixtures only; no participant accuracy/readiness claims."""

from dataclasses import asdict, replace
import time

import numpy as np
import pytest

from gestureforge import pose_repair
from gestureforge.dataset import file_sha256, load_dataset, save_dataset
from gestureforge.enrolment import EnrolmentSession
from gestureforge.contracts import Observation
from gestureforge.fixtures import synthetic_dataset
from gestureforge.pose_repair import PoseRepair, RepairCandidate
from gestureforge.profiles import ProfileSettings, ProfileStore
from gestureforge.vocabulary import GestureVocabulary


@pytest.fixture
def workflow(tmp_path):
    generated = synthetic_dataset(trials_per_label_per_split=2)
    vocabulary = GestureVocabulary(('G1', 'G2', 'G3'))
    mapping = dict(zip(generated.vocabulary.labels, vocabulary.labels, strict=True))
    records = tuple(replace(r, participant_id='SOFTWARE_TEST', hand='Right', provenance='human',
                            intended_label=mapping.get(r.intended_label, r.intended_label))
                    for r in generated.records)
    source = save_dataset(tmp_path / 'original', records, generated.features,
                          {'chosen_hand': 'Right', 'warning': 'GENERATED SOFTWARE TEST ONLY'},
                          vocabulary=vocabulary)
    assert source.manifest_path is not None
    store = ProfileStore(tmp_path / 'profiles')
    original = store.create('Original', source.manifest_path, 'Right', consent=True,
                            settings=ProfileSettings('knn', 1.5, 1.5))
    repair = PoseRepair(original.record, 'NEUTRAL', 'Reviewed diagnostic: neutral rejection')
    plan = repair.plan(2, 'GENERATED SOFTWARE TEST ONLY')
    # New selected-class session, with five slots in each of two trials.
    chosen = tuple(r for r in source.records if r.split == 'train' and r.intended_label == 'NEUTRAL')
    replacement = tuple(replace(r, session_id='repair-session', trial_id='repair-' + r.trial_id)
                        for r in chosen)
    features = np.array([source.features[r.feature_index] for r in chosen], dtype=np.float32) + .02
    replacement = tuple(replace(r, feature_index=i) for i, r in enumerate(replacement))
    samples = save_dataset(tmp_path / 'samples', replacement, features,
                           {'chosen_hand': 'Right', 'collection_complete': True, 'planned_trials': 2,
                            'warning': 'GENERATED SOFTWARE TEST ONLY'}, vocabulary=vocabulary)
    return store, original, source, repair, plan, samples


def test_candidate_retains_other_classes_excludes_heldout_and_rolls_back(workflow, tmp_path):
    store, original, source, repair, _, samples = workflow
    paths = [source.manifest_path, samples.manifest_path,
             store.root / (original.record.profile_id + '.json')]
    hashes = [file_sha256(path) for path in paths]
    candidate = repair.build_candidate(samples.manifest_path, tmp_path / 'candidates', reviewed=True)
    combined = load_dataset(candidate.manifest)
    assert set(r.split for r in combined.records) == {'train'}
    assert set(r.intended_label for r in combined.records) == set(source.vocabulary.labels)
    for label in ('G1', 'G2', 'G3'):
        before = [r for r in source.records if r.split == 'train' and r.intended_label == label]
        after = [r for r in combined.records if r.intended_label == label]
        assert [dict(asdict(r), feature_index=None) for r in after] == [
            dict(asdict(r), feature_index=None) for r in before]
        for old, new in zip(before, after, strict=True):
            np.testing.assert_array_equal(source.features[old.feature_index], combined.features[new.feature_index])
    assert all(r.session_id == 'repair-session' for r in combined.records if r.intended_label == 'NEUTRAL')
    new = store.create('Candidate', candidate.manifest, candidate.hand, consent=True,
                       settings=candidate.settings, gesture_names=dict(candidate.gesture_names))
    assert new.record.profile_id != original.record.profile_id
    assert new.record.model_version != original.record.model_version
    assert new.record.settings == original.record.settings
    assert new.selection.readiness_revision == ''
    assert store.load(candidate.rollback_profile_id).record == original.record
    assert [file_sha256(path) for path in paths] == hashes
    again = repair.build_candidate(samples.manifest_path, tmp_path / 'candidates', reviewed=True)
    assert again.manifest != candidate.manifest


@pytest.mark.parametrize('change', ['cancelled', 'invalid', 'validation', 'test', 'wrong_label',
                                    'participant', 'hand', 'incomplete', 'collision'])
def test_invalid_or_cancelled_repair_never_publishes_candidate(workflow, tmp_path, change):
    _, original, _, repair, _, samples = workflow
    records = list(samples.records)
    metadata = dict(samples.metadata)
    features = samples.features
    if change == 'cancelled':
        metadata['collection_complete'] = False
    elif change == 'invalid':
        records[0] = replace(records[0], valid=False, feature_index=None, validity_reason='no_hand')
    elif change in ('validation', 'test'):
        records = [replace(r, split=change) for r in records]
    elif change == 'wrong_label':
        records = [replace(r, intended_label='G1') for r in records]
    elif change == 'participant':
        records = [replace(r, participant_id='OTHER') for r in records]
    elif change == 'hand':
        records = [replace(r, hand='Left') for r in records]
    elif change == 'incomplete':
        records = records[:-1]
    else:
        records = [replace(r, session_id=repair.bundle.records[0].session_id) for r in records]
    bad = save_dataset(tmp_path / 'bad', records, features, metadata, vocabulary=samples.vocabulary)
    with pytest.raises(ValueError):
        repair.build_candidate(bad.manifest_path, tmp_path / 'candidates', reviewed=True)
    assert not (tmp_path / 'candidates').exists()
    assert load_dataset(original.record.dataset_path).records == repair.bundle.records


def test_candidate_builder_checks_reviewed_collection_snapshot(workflow, tmp_path):
    _, _, _, repair, _, samples = workflow
    from gestureforge.dataset import dataset_hashes

    reviewed_hashes = dataset_hashes(samples)
    changed = save_dataset(samples.manifest_path, samples.records, samples.features + 0.01,
                           samples.metadata, vocabulary=samples.vocabulary)
    with pytest.raises(ValueError, match='changed after review'):
        repair.build_candidate(changed.manifest_path, tmp_path / 'candidates', reviewed=True,
                               expected_repair_hashes=reviewed_hashes)
    assert not (tmp_path / 'candidates').exists()


def test_review_and_unchanged_source_required(workflow, tmp_path):
    _, _, source, repair, _, samples = workflow
    with pytest.raises(ValueError, match='Review'):
        repair.build_candidate(samples.manifest_path, tmp_path / 'candidates', reviewed=False)
    save_dataset(source.manifest_path, source.records, source.features,
                 {**source.metadata, 'changed': True}, vocabulary=source.vocabulary)
    with pytest.raises(ValueError, match='changed'):
        repair.build_candidate(samples.manifest_path, tmp_path / 'candidates', reviewed=True)


def test_candidate_save_failure_preserves_original_and_retry(workflow, tmp_path, monkeypatch):
    store, original, _, repair, _, samples = workflow
    save = pose_repair.save_dataset
    def fail(*args, **kwargs):
        raise OSError('disk full')
    monkeypatch.setattr(pose_repair, 'save_dataset', fail)
    with pytest.raises(OSError, match='disk full'):
        repair.build_candidate(samples.manifest_path, tmp_path / 'candidates', reviewed=True)
    assert not list((tmp_path / 'candidates').glob('*/manifest.json'))
    assert store.load(original.record.profile_id).record == original.record
    monkeypatch.setattr(pose_repair, 'save_dataset', save)
    assert repair.build_candidate(samples.manifest_path, tmp_path / 'candidates', reviewed=True).manifest.exists()


def test_selected_plan_and_partial_stop_keep_evidence(workflow, tmp_path):
    _, _, _, repair, plan, _ = workflow
    assert plan.labels == ('NEUTRAL',) and plan.split == 'train'
    session = EnrolmentSession(plan, tmp_path / 'capture', 'capture', 'SOFTWARE_TEST', consent=True)
    assert session.total == 2 and session.label == 'NEUTRAL'
    session.begin(0.)
    session.advance(2.3)
    session.stop(2.4)
    assert session.state == 'cancelled'
    partial = load_dataset(session.manifest)
    assert len(partial.records) == 5 and not partial.metadata['collection_complete']
    with pytest.raises(ValueError, match='Cancelled'):
        repair.build_candidate(session.manifest, tmp_path / 'candidates', reviewed=True)
    with pytest.raises(ValueError, match='positive TRAIN'):
        replace(plan, split='validation')
    with pytest.raises(ValueError, match='positive TRAIN'):
        replace(plan, collection_labels=('UNKNOWN',))


def test_selected_collection_save_retry_completes_only_chosen_label(workflow, tmp_path, monkeypatch):
    from gestureforge import enrolment
    _, _, _, _, plan, _ = workflow
    session = EnrolmentSession(plan, tmp_path / 'capture', 'capture', 'SOFTWARE_TEST', consent=True)
    real_save = enrolment.save_dataset
    def fail(*args, **kwargs):
        raise OSError('disk full')
    for trial in range(2):
        now = trial * 6.
        session.advance(now)
        session.begin(now)
        for slot, offset in enumerate(enrolment.OFFSETS):
            stamp = now + 2. + offset + .01
            points = np.arange(63, dtype=float).reshape(21, 3) / 100
            session.advance(stamp, Observation('capture', 'SOFTWARE_TEST', trial * 10 + slot,
                                                stamp, 1, 'Right', points))
        if trial == 1:
            monkeypatch.setattr(enrolment, 'save_dataset', fail)
        session.advance(now + 4.1)
    assert session.state == 'save_error' and session.completed == 1
    assert len(session.pending_records) == 5
    monkeypatch.setattr(enrolment, 'save_dataset', real_save)
    session.retry_save(10.2)
    assert session.state == 'complete' and session.completed == 2
    bundle = load_dataset(session.manifest)
    assert len(bundle.records) == 10 and len(bundle.valid_records()) == 10
    assert {r.intended_label for r in bundle.records} == {'NEUTRAL'}
    assert bundle.metadata['collection_complete'] is True


def test_source_unknown_synthetic_or_missing_train_class_is_rejected(workflow, tmp_path):
    _, original, source, _, _, _ = workflow
    with pytest.raises(ValueError, match='positive label'):
        PoseRepair(original.record, 'UNKNOWN', 'Reviewed diagnostic')
    records = tuple(replace(r, provenance='synthetic') for r in source.records)
    bad = save_dataset(tmp_path / 'synthetic', records, source.features,
                       source.metadata, vocabulary=source.vocabulary)
    from gestureforge.dataset import dataset_hashes
    hashes = dataset_hashes(bad)
    record = replace(original.record, dataset_path=str(bad.manifest_path),
                     manifest_sha256=hashes['manifest_sha256'], features_sha256=hashes['features_sha256'])
    with pytest.raises(ValueError, match='personal records'):
        PoseRepair(record, 'NEUTRAL', 'Reviewed diagnostic')


@pytest.mark.parametrize('label', ['G1', 'G2', 'G3', 'NEUTRAL'])
def test_each_positive_label_can_be_repaired_without_other_class_changes(workflow, tmp_path, label):
    _, original, source, _, _, _ = workflow
    repair = PoseRepair(original.record, label, 'Reviewed targeted diagnostic')
    selected = tuple(r for r in source.records if r.split == 'train' and r.intended_label == label)
    records = tuple(replace(r, session_id='new-session', trial_id='new-' + r.trial_id, feature_index=i)
                    for i, r in enumerate(selected))
    rows = np.array([source.features[r.feature_index] for r in selected]) + .01
    samples = save_dataset(tmp_path / 'replacement', records, rows,
                           {'collection_complete': True, 'planned_trials': 2}, vocabulary=source.vocabulary)
    assert samples.manifest_path is not None
    candidate = repair.build_candidate(samples.manifest_path, tmp_path / 'candidate', reviewed=True)
    bundle = load_dataset(candidate.manifest)
    assert len(bundle.records) == 40
    assert {r.intended_label for r in bundle.records if r.session_id == 'new-session'} == {label}
    assert dict(candidate.valid_per_label) == dict.fromkeys(source.vocabulary.labels, 10)


def test_changed_review_candidate_does_not_replace_selected_profile(workflow, tmp_path):
    from PySide6.QtWidgets import QApplication
    from gestureforge.profile_widget import ProfileSelectorWidget
    app = QApplication.instance() or QApplication([])
    store, original, _, repair, _, samples = workflow
    candidate = repair.build_candidate(samples.manifest_path, tmp_path / 'candidate', reviewed=True)
    selector = ProfileSelectorWidget(store)
    selector.loaded = original
    selector.offer_repair_candidate(candidate)
    bundle = load_dataset(candidate.manifest)
    save_dataset(candidate.manifest, bundle.records, bundle.features,
                 {**bundle.metadata, 'changed_after_review': True}, vocabulary=bundle.vocabulary)
    selector.consent.setChecked(True)
    selector.create_profile()
    deadline = time.monotonic() + 10
    while selector.busy and time.monotonic() < deadline:
        selector._poll()
        app.processEvents()
        time.sleep(.01)
    assert not selector.busy and selector.loaded is original
    assert 'changed after review' in selector.status.text()
    assert store.list_ids() == (original.record.profile_id,)
    selector.close()


def test_failed_candidate_profile_save_keeps_original(workflow, tmp_path, monkeypatch):
    from gestureforge import profiles
    store, original, _, repair, _, samples = workflow
    candidate = repair.build_candidate(samples.manifest_path, tmp_path / 'candidate', reviewed=True)
    def fail(*args, **kwargs):
        raise OSError('profile save failed')
    monkeypatch.setattr(profiles, 'atomic_write_json', fail)
    with pytest.raises(OSError, match='profile save failed'):
        store.create('Candidate', candidate.manifest, candidate.hand, consent=True, settings=candidate.settings)
    assert store.list_ids() == (original.record.profile_id,)
    assert store.load(original.record.profile_id).record == original.record


def test_widget_review_does_not_train_and_selector_preserves_settings(workflow, tmp_path):
    from PySide6.QtWidgets import QApplication
    from gestureforge.pose_repair_widget import PoseRepairWidget
    from gestureforge.profile_widget import ProfileSelectorWidget
    app = QApplication.instance() or QApplication([])
    store, original, _, repair, plan, samples = workflow
    widget = PoseRepairWidget(tmp_path / 'captures', clock=lambda: 0.)
    selector = ProfileSelectorWidget(store)
    widget.set_source(original.record)
    widget.repair_pose.setCurrentText('NEUTRAL')
    widget.diagnosis.setText('Reviewed neutral miss')
    widget.setup.setText('GENERATED SOFTWARE TEST ONLY')
    widget.diagnostic_reviewed.setChecked(True)
    widget.consent.setChecked(True)
    requested = []
    widget.capture_requested.connect(lambda p, rid: requested.append((p, rid)))
    widget.request_collection()
    assert requested, widget.feedback.text()
    assert requested[0][0].labels == ('NEUTRAL',)
    widget.stop_collection()
    assert widget.pending_plan is None and not widget.candidate_button.isEnabled()
    # Generated completed fixture exercises review without collecting physical data.
    widget.repair = repair
    widget.session = EnrolmentSession(plan, tmp_path / 'session', 'capture', 'SOFTWARE_TEST', consent=True)
    widget.session.records = list(samples.records)
    widget.session.features = list(samples.features)
    widget.session.state = 'complete'
    widget._collection_complete(samples.manifest_path)
    results: list[RepairCandidate] = []
    widget.candidate_ready.connect(results.append)
    widget.candidate_ready.connect(selector.offer_repair_candidate)
    widget.build_candidate()
    assert not results  # review checkbox is mandatory
    widget.count_review.setChecked(True)
    widget.build_candidate()
    assert len(results) == 1 and selector._future is None
    assert not selector.consent.isChecked()
    assert selector._repair_candidate is not None
    assert selector._repair_candidate.settings == original.record.settings
    assert store.list_ids() == (original.record.profile_id,)
    widget.close()
    selector.close()
    app.processEvents()
