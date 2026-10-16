"""Generated software fixtures only; no participant data or camera access."""

from dataclasses import replace
import os
from pathlib import Path
from threading import Event, get_ident
from time import monotonic

import pytest
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication, QMessageBox

from gestureforge.dataset import load_dataset, save_dataset
from gestureforge.app import Window, load_personal_model
from gestureforge.fixtures import synthetic_dataset
from gestureforge.profile_widget import ProfileSelectorWidget
from gestureforge.profiles import LoadedProfile, ProfileRecord, ProfileSelection, ProfileSettings, ProfileStore


@pytest.fixture(scope='module')
def qt_app():
    return QApplication.instance() or QApplication([])


@pytest.fixture
def studio(qt_app, tmp_path, monkeypatch):
    import gestureforge.app as app_module

    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(app_module, "DEFAULT_STUDIO_STATE_FOLDER", tmp_path / "studio")
    monkeypatch.setattr(app_module, "DEFAULT_ENROLMENT_FOLDER", tmp_path / "enrolment")
    window = Window(studio=True)
    window._log_failed = True
    window._auto_archive_summary_on_close = False
    yield window
    window.close()


@pytest.fixture
def local_store(tmp_path):
    bundle = synthetic_dataset(trials_per_label_per_split=2)
    records = tuple(replace(r, participant_id='GENERATED_TEST', hand='Right', provenance='human')
                    for r in bundle.records)
    source = save_dataset(tmp_path / 'generated', records, bundle.features,
                          {'chosen_hand': 'Right', 'warning': 'GENERATED SOFTWARE TEST ONLY'})
    return ProfileStore(tmp_path / 'profiles'), source.manifest_path


def select(widget, profile_id):
    for index in range(widget.profiles.count()):
        item = widget.profiles.item(index)
        if item.data(Qt.ItemDataRole.UserRole) == profile_id:
            widget.profiles.setCurrentItem(item)
            return
    raise AssertionError('profile missing from list')


def finish(widget):
    deadline = monotonic() + 15
    while widget.busy and monotonic() < deadline:
        QApplication.processEvents()
        QTest.qWait(10)
    assert not widget.busy, 'profile worker did not finish'


def create(widget, source) -> LoadedProfile:
    widget.name.setText('Generated profile')
    widget.manifest.setText(str(source))
    widget.consent.setChecked(True)
    widget.create_button.click()
    finish(widget)
    assert widget.loaded is not None, widget.status.text()
    return widget.loaded


def test_empty_guest_and_unavailable_starter(qt_app, tmp_path):
    store = ProfileStore(tmp_path / 'unused')
    widget = ProfileSelectorWidget(store)
    assert widget.profiles.count() == 0
    assert not store.root.exists()
    assert not widget.start_button.isEnabled()
    assert not widget.starter_button.isEnabled()
    assert 'no approved starter' in widget.starter_notice.text()
    guests = []
    widget.guest_selected.connect(lambda: guests.append(True))
    widget.guest_button.click()
    assert guests == [True]
    assert widget.loaded is None
    assert 'Manual controls only' in widget.status.text()
    widget.close()


def test_create_consent_background_fit_and_host_install(studio, local_store, monkeypatch):
    store, source = local_store
    events = []
    main_thread = get_ident()
    original = store.create
    original_install = studio.use_studio_profile

    def fit(*args, **kwargs):
        assert get_ident() != main_thread
        events.append('fit')
        return original(*args, **kwargs)

    def install(candidate):
        assert get_ident() == main_thread
        events.append('install')
        original_install(candidate)

    monkeypatch.setattr(store, 'create', fit)
    def pause():
        events.append('pause')
        return True

    monkeypatch.setattr(studio, 'pause', pause)
    monkeypatch.setattr(studio, 'use_studio_profile', install)
    widget = ProfileSelectorWidget(store, host=studio)
    widget.create_button.click()
    assert not events and not widget.busy
    assert 'permission' in widget.status.text()
    selected: list[ProfileSelection] = []
    starts: list[ProfileSelection] = []
    widget.profile_selected.connect(selected.append)
    widget.start_requested.connect(starts.append)
    created = create(widget, source)
    assert events == ['pause', 'fit', 'install', 'pause']
    assert selected == [created.selection]
    assert not created.selection.readiness_revision
    assert widget.start_button.isEnabled()
    widget.start_button.click()
    assert starts == [created.selection]
    assert store.load(created.record.profile_id).record == created.record
    widget.close()


def test_rename_reload_duplicate_names_and_local_preview(qt_app, local_store):
    store, source = local_store
    widget = ProfileSelectorWidget(store)
    first = create(widget, source)
    second = create(widget, source)
    assert first.record.profile_id != second.record.profile_id
    assert widget.profiles.count() == 2
    assert not widget.start_button.isEnabled()
    select(widget, second.record.profile_id)
    widget.name.setText('<b>个人</b>')
    renamed: list[ProfileRecord] = []
    widget.profile_renamed.connect(renamed.append)
    widget.rename_button.click()
    assert widget.loaded is not None
    assert widget.loaded.record.display_name == '<b>个人</b>'
    assert widget.current.textFormat() == Qt.TextFormat.PlainText
    assert widget.loaded.record.model_version == second.record.model_version
    assert len(renamed) == 1
    widget.close()
    restored = ProfileSelectorWidget(store)
    assert restored.loaded is None
    select(restored, second.record.profile_id)
    restored.load_button.click()
    finish(restored)
    loaded = restored.loaded
    assert isinstance(loaded, LoadedProfile)
    assert loaded.record.display_name == '<b>个人</b>'
    restored.close()


def test_failed_load_and_install_keep_previous_selection(studio, local_store, monkeypatch):
    store, source = local_store
    widget = ProfileSelectorWidget(store, host=studio)
    previous = create(widget, source)
    select(widget, previous.record.profile_id)
    def fail_install(candidate):
        raise ValueError('installation refused')

    monkeypatch.setattr(studio, 'use_studio_profile', fail_install)
    widget.load_button.click()
    finish(widget)
    assert widget.loaded is previous
    assert 'installation refused' in widget.status.text()
    assert widget.guest_button.isEnabled()

    def fail(profile_id):
        raise FileNotFoundError('referenced numeric dataset is missing')

    monkeypatch.setattr(store, 'load', fail)
    widget.load_button.click()
    finish(widget)
    assert widget.loaded is previous
    assert 'dataset is missing' in widget.status.text()
    widget.close()


def test_pause_failure_prevents_storage_work(studio, local_store, monkeypatch):
    store, source = local_store
    monkeypatch.setattr(studio, 'pause', lambda: False)
    widget = ProfileSelectorWidget(store, host=studio)
    widget.name.setText('Blocked')
    widget.manifest.setText(str(source))
    widget.consent.setChecked(True)
    widget.create_button.click()
    assert not widget.busy and store.list_ids() == ()
    assert 'could not pause' in widget.status.text()
    widget.close()


def test_delete_confirmation_preserves_source_and_clears_active(studio, local_store, monkeypatch):
    store, source = local_store
    widget = ProfileSelectorWidget(store, host=studio)
    created = create(widget, source)
    other = create(widget, source)
    select(widget, other.record.profile_id)
    assert widget.delete_button.isEnabled()
    monkeypatch.setattr(QMessageBox, 'question', lambda *a: QMessageBox.StandardButton.No)
    widget.delete_button.click()
    assert len(store.list_ids()) == 2
    monkeypatch.setattr(QMessageBox, 'question', lambda *a: QMessageBox.StandardButton.Yes)
    deleted: list[str] = []
    widget.profile_deleted.connect(deleted.append)
    widget.delete_button.click()
    assert deleted == [other.record.profile_id]
    assert studio.model is None and widget.loaded is None
    assert not studio.start_button.isEnabled()
    assert store.list_ids() == (created.record.profile_id,)
    assert source.exists()
    assert store.load(created.record.profile_id).record == created.record
    widget.close()


def test_corrupt_entries_visible_and_independently_deletable(qt_app, local_store, monkeypatch):
    store, source = local_store
    good = store.create('Good', source, 'Right', consent=True)
    corrupt_id = 'f' * 32
    (store.root / f'{corrupt_id}.json').write_text('{"schema_version":999}', encoding='utf-8')
    widget = ProfileSelectorWidget(store)
    assert widget.profiles.count() == 2
    select(widget, corrupt_id)
    assert not widget.load_button.isEnabled()
    assert widget.delete_button.isEnabled()
    monkeypatch.setattr(QMessageBox, 'question', lambda *a: QMessageBox.StandardButton.Yes)
    widget.delete_button.click()
    assert store.list_ids() == (good.record.profile_id,)
    select(widget, good.record.profile_id)
    assert widget.load_button.isEnabled()
    widget.close()


@pytest.mark.parametrize('operation', ['rename', 'delete'])
def test_write_failure_keeps_saved_profile(studio, local_store, monkeypatch, operation):
    store, source = local_store
    widget = ProfileSelectorWidget(store, host=studio)
    created = create(widget, source)
    select(widget, created.record.profile_id)

    def fail(*args):
        raise OSError('disk unavailable')

    monkeypatch.setattr(store, operation, fail)
    monkeypatch.setattr(QMessageBox, 'question', lambda *a: QMessageBox.StandardButton.Yes)
    if operation == 'rename':
        widget.name.setText('Changed')
        widget.rename_button.click()
    else:
        widget.delete_button.click()
    assert 'disk unavailable' in widget.status.text()
    assert store.read(created.record.profile_id) == created.record
    assert studio.model is created.model
    assert widget.loaded is created
    widget.close()


@pytest.mark.parametrize('stop', ['hide', 'close'])
def test_late_worker_cannot_install_after_hide_or_close(qt_app, local_store, monkeypatch, stop):
    store, source = local_store
    candidate = store.create('Generated', source, 'Right', consent=True)
    entered, release = Event(), Event()

    def delayed(profile_id):
        entered.set()
        assert release.wait(10)
        return candidate

    monkeypatch.setattr(store, 'load', delayed)
    widget = ProfileSelectorWidget(store)
    widget.show()
    select(widget, candidate.record.profile_id)
    try:
        widget.load_button.click()
        assert entered.wait(3)
        assert not widget.create_button.isEnabled()
        assert not widget.guest_button.isEnabled()
        widget.load_selected()  # duplicate requests are ignored
        future = widget._future
        assert future is not None
        getattr(widget, stop)()
        release.set()
        assert future.result(timeout=5) == candidate
        if stop == 'hide':
            finish(widget)
        else:
            widget._poll()
        assert widget.loaded is None
    finally:
        release.set()
        widget.close()


def test_saved_load_uses_existing_shell_worker(studio, local_store, monkeypatch):
    store, source = local_store
    saved_settings = ProfileSettings('knn', 2.0, 1.25)
    candidate = store.create('Saved', source, 'Right', consent=True, settings=saved_settings)
    studio.model_settings = ('svm', 3.0, 1.75)
    widget = ProfileSelectorWidget(store, host=studio)
    selected: list[ProfileSelection] = []
    widget.profile_selected.connect(selected.append)
    select(widget, candidate.record.profile_id)
    widget.load_button.click()
    assert widget._future is None  # no duplicate component reconstruction worker
    assert studio.model_loader is not None
    finish(widget)
    assert studio.selected_profile_id == candidate.record.profile_id
    assert widget.loaded is not None and widget.loaded.model is studio.model
    assert selected == [candidate.selection]
    assert studio.worker is None  # selection never opens a camera
    assert studio.routing.state == 'PAUSED'
    assert widget.loaded.record.settings == saved_settings
    assert studio.model_settings == ('knn', 2.0, 1.25)
    assert widget.guest_button.isEnabled()
    widget.close()


@pytest.mark.parametrize('settings', [('knn', 1.5, 1.5), ('svm', 2.0, 1.25)])
def test_profile_creation_matches_direct_dataset_rejection_settings(studio, local_store, settings):
    store, source = local_store
    studio.model_settings = settings
    direct, *_ = load_personal_model(source, *settings, studio=True)
    widget = ProfileSelectorWidget(store, host=studio)
    widget.algorithm.setCurrentText(settings[0])
    try:
        created = create(widget, source)
        assert created.record.settings == ProfileSettings(*settings)
        assert replace(created.model.config, model_version=direct.model_version) == direct.config
        assert created.model.thresholds == direct.thresholds
        for feature in load_dataset(source).features:
            assert created.model.predict(feature) == direct.predict(feature)
        assert str(settings[1]) in widget.creation_settings.text()
        assert str(settings[2]) in widget.creation_settings.text()
    finally:
        widget.close()


def test_profile_creation_uses_selected_algorithm_and_current_host_thresholds(studio, local_store):
    store, source = local_store
    widget = ProfileSelectorWidget(store, host=studio)
    studio.model_settings = ('knn', 2.0, 1.25)
    widget.algorithm.setCurrentText('svm')
    try:
        assert create(widget, source).record.settings == ProfileSettings('svm', 2.0, 1.25)
    finally:
        widget.close()


def test_standalone_creation_keeps_defaults(qt_app, local_store):
    store, source = local_store
    widget = ProfileSelectorWidget(store)
    try:
        assert create(widget, source).record.settings == ProfileSettings()
    finally:
        widget.close()


def test_repair_creation_keeps_candidate_settings(studio, local_store):
    from gestureforge.dataset import file_sha256
    from gestureforge.pose_repair import RepairCandidate

    store, source = local_store
    original = store.create('Original', source, 'Right', consent=True,
                            settings=ProfileSettings('knn', 2.0, 1.25))
    candidate = RepairCandidate(source, file_sha256(source), 'Right', original.record.settings,
                                original.record.gesture_names, original.record.profile_id,
                                str(source), 'PREVIOUS', ())
    studio.model_settings = ('svm', 3.0, 1.75)
    widget = ProfileSelectorWidget(store, host=studio)
    try:
        widget.offer_repair_candidate(candidate)
        widget.consent.setChecked(True)
        widget.create_button.click()
        finish(widget)
        assert widget.loaded is not None, widget.status.text()
        assert widget.loaded.record.settings == candidate.settings
        assert store.read(original.record.profile_id) == original.record
    finally:
        widget.close()


def test_guest_switch_preserves_profile_and_can_reload(studio, local_store):
    store, source = local_store
    widget = ProfileSelectorWidget(store, host=studio)
    candidate = create(widget, source)
    before = source.read_bytes()
    guests = []
    widget.guest_selected.connect(lambda: guests.append(True))
    widget.guest_button.click()
    assert guests == [True]
    assert widget.loaded is None and studio.model is None
    assert not widget.start_button.isEnabled() and not studio.start_button.isEnabled()
    assert store.read(candidate.record.profile_id) == candidate.record
    assert source.read_bytes() == before
    select(widget, candidate.record.profile_id)
    widget.load_button.click()
    finish(widget)
    assert studio.selected_profile_id == candidate.record.profile_id
    assert widget.loaded is not None and widget.loaded.model is studio.model
    assert studio.worker is None
    widget.close()


@pytest.mark.parametrize('failure', ['refused', 'exception'])
def test_guest_failure_keeps_previous_selection(studio, local_store, monkeypatch, failure):
    store, source = local_store
    widget = ProfileSelectorWidget(store, host=studio)
    candidate = create(widget, source)
    guests = []
    widget.guest_selected.connect(lambda: guests.append(True))

    def blocked():
        if failure == 'exception':
            raise ValueError('trace save failed')
        return False

    monkeypatch.setattr(studio, 'use_studio_guest', blocked)
    widget.guest_button.click()
    assert not guests
    assert widget.loaded is candidate and studio.model is candidate.model
    assert 'Cannot switch to Guest' in widget.status.text()
    assert store.read(candidate.record.profile_id) == candidate.record
    widget.close()


def test_visible_component_evidence(qt_app, local_store):
    store, source = local_store
    widget = ProfileSelectorWidget(store)
    widget.resize(760, 760)
    widget.show()
    create(widget, source)
    QApplication.processEvents()
    evidence = os.environ.get('GF_PROFILE_SCREENSHOT')
    if evidence:
        path = Path(evidence)
        path.parent.mkdir(parents=True, exist_ok=True)
        assert widget.grab().save(str(path))
    assert widget.current.isVisible() and widget.guest_button.isVisible()
    widget.close()
