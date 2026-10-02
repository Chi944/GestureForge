"""Synthetic observations verify collection mechanics, never human pose accuracy."""

from dataclasses import replace
import os

import numpy as np
import pytest

from gestureforge import enrolment
from gestureforge.contracts import Observation
from gestureforge.dataset import load_dataset
from gestureforge.enrolment import EnrolmentPlan, EnrolmentSession, OFFSETS
from gestureforge.vocabulary import GestureVocabulary


@pytest.fixture
def plan():
    vocabulary = GestureVocabulary(('G1', 'G2', 'G3'))
    return EnrolmentPlan('TEST', 'Right', vocabulary,
                         tuple((label, 'Show ' + label) for label in vocabulary.labels),
                         trials=2, setup='SYNTHETIC SOFTWARE TEST ONLY')


def observation(timestamp, frame):
    points = np.arange(63, dtype=float).reshape(21, 3) / 100
    return Observation('capture1', 'TEST', frame, timestamp, 1, 'Right', points)


def finish_trial(session, start, frame=0):
    session.begin(start)
    for index, offset in enumerate(OFFSETS):
        at = start + 2. + offset + .01
        session.advance(at, observation(at, frame + index))
    session.advance(start + 4.1)


def test_complete_custom_session_roundtrip_and_separate_validation(plan, tmp_path):
    session = EnrolmentSession(plan, tmp_path, 'capture1', 'TEST', consent=True)
    for trial in range(8):
        at = trial * 6.
        session.advance(at)
        finish_trial(session, at, trial * 10)
    bundle = load_dataset(session.manifest)
    assert session.state == 'complete'
    assert len(bundle.records) == 40
    assert len(bundle.valid_records()) == 40
    assert bundle.vocabulary == plan.vocabulary
    assert set(r.intended_label for r in bundle.records) == set(plan.vocabulary.labels)
    assert bundle.metadata['raw_video_recorded'] is False
    other = EnrolmentSession(replace(plan, split='validation'), tmp_path,
                              'capture2', 'TEST', consent=True)
    assert other.manifest != session.manifest
    assert other.session_id != session.session_id
    assert not other.manifest.exists()


@pytest.mark.parametrize('change', [dict(hand_count=0), dict(hand_count=2),
                                    dict(handedness='Left'), dict(landmarks=None),
                                    dict(landmarks=np.zeros((21, 3))),
                                    dict(landmarks=np.full((21, 3), np.nan))])
def test_invalid_detections_are_retained(plan, tmp_path, change):
    session = EnrolmentSession(plan, tmp_path, 'capture1', 'TEST', consent=True)
    session.begin(0.)
    for i, offset in enumerate(OFFSETS):
        at = 2. + offset + .01
        session.advance(at, replace(observation(at, i), **change))
    session.advance(4.1)
    bundle = load_dataset(session.manifest)
    assert len(bundle.records) == 5 and not bundle.valid_records()
    assert all(r.validity_reason for r in bundle.records)


def test_absent_camera_preserves_five_slots(plan, tmp_path):
    session = EnrolmentSession(plan, tmp_path, 'capture1', 'TEST', consent=True)
    session.begin(0.)
    session.advance(5.)
    bundle = load_dataset(session.manifest)
    assert len(bundle.records) == 5
    assert not bundle.valid_records()


def test_timer_waits_for_latest_eligible_delivery_before_expiring_slot(plan, tmp_path):
    session = EnrolmentSession(plan, tmp_path, 'capture1', 'TEST', consent=True)
    session.begin(0.)
    session.advance(2.41)
    session.advance(2.50, observation(2.39, 1))
    session.advance(5.)
    records = load_dataset(session.manifest).records
    assert records[0].valid
    assert records[0].timestamp == 2.39


def test_final_slot_waits_for_delivery_window_before_save(plan, tmp_path):
    session = EnrolmentSession(plan, tmp_path, 'capture1', 'TEST', consent=True)
    session.begin(0.)
    for index, offset in enumerate(OFFSETS[:-1]):
        at = 2. + offset + .01
        session.advance(at, observation(at, index))
    session.advance(4.01)
    assert session.state == 'hold'
    assert not session.manifest.exists()
    session.advance(4.10, observation(3.99, 10))
    bundle = load_dataset(session.manifest)
    assert session.state == 'release'
    assert len(bundle.valid_records()) == 5


def test_late_timestamp_stays_invalid_after_delivery_window(plan, tmp_path):
    session = EnrolmentSession(plan, tmp_path, 'capture1', 'TEST', consent=True)
    session.begin(0.)
    session.advance(2.61, observation(2.41, 1))
    session.advance(5.)
    records = load_dataset(session.manifest).records
    assert not records[0].valid
    assert records[0].validity_reason == 'missed scheduled timestamp'


@pytest.mark.parametrize('change', [dict(session_id='old'), dict(profile_id='old'),
                                    dict(timestamp=0.), dict(timestamp=999.)])
def test_stale_and_wrong_generation_rejected(plan, tmp_path, change):
    session = EnrolmentSession(plan, tmp_path, 'capture1', 'TEST', consent=True)
    session.begin(0.)
    session.advance(2.21, replace(observation(2.21, 1), **change))
    session.advance(5.)
    assert not load_dataset(session.manifest).valid_records()


def test_duplicate_frame_cannot_fill_another_slot(plan, tmp_path):
    session = EnrolmentSession(plan, tmp_path, 'capture1', 'TEST', consent=True)
    session.begin(0.)
    session.advance(2.21, observation(2.21, 7))
    session.advance(2.61, observation(2.61, 7))
    session.advance(5.)
    assert len(load_dataset(session.manifest).valid_records()) == 1


def test_fault_retains_partial_trial_and_previous_trials(plan, tmp_path):
    session = EnrolmentSession(plan, tmp_path, 'capture1', 'TEST', consent=True)
    finish_trial(session, 0.)
    session.advance(6.)
    session.begin(6.)
    session.advance(8.21, observation(8.21, 20))
    session.stop(8.3, 'Camera interrupted')
    bundle = load_dataset(session.manifest)
    assert session.state == 'cancelled'
    assert len(bundle.records) == 10
    assert len(bundle.valid_records()) == 6
    assert all(r.validity_reason == 'Camera interrupted' for r in bundle.records[-4:])


def test_failed_save_retries_same_trial_without_duplicates(plan, tmp_path, monkeypatch):
    session = EnrolmentSession(plan, tmp_path, 'capture1', 'TEST', consent=True)
    finish_trial(session, 0.)
    original = session.manifest.read_bytes()
    save = enrolment.save_dataset
    def fail(*args, **kwargs):
        raise OSError('disk full')
    monkeypatch.setattr(enrolment, 'save_dataset', fail)
    session.advance(6.)
    finish_trial(session, 6., 10)
    assert session.state == 'save_error'
    assert session.completed == 1
    assert session.manifest.read_bytes() == original
    with pytest.raises(ValueError):
        session.begin(11.)
    session.stop(11.1)
    assert len(session.pending_records) == 5
    monkeypatch.setattr(enrolment, 'save_dataset', save)
    session.retry_save(11.2)
    assert session.state == 'cancelled'
    assert len(load_dataset(session.manifest).records) == 10


def test_no_consent_no_directory(plan, tmp_path):
    with pytest.raises(ValueError, match='consent'):
        EnrolmentSession(plan, tmp_path / 'private', 'capture1', 'TEST', consent=False)
    assert not (tmp_path / 'private').exists()


def test_widget_host_handshake_cancel_and_no_camera(tmp_path):
    os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
    from PySide6.QtWidgets import QApplication
    from gestureforge.enrolment_widget import EnrolmentWidget
    app = QApplication.instance() or QApplication([])
    assert app is not None
    widget = EnrolmentWidget(tmp_path, clock=lambda: 0.)
    requests = []
    releases: list[str] = []
    widget.capture_requested.connect(lambda plan, token: requests.append((plan, token)))
    widget.capture_release_requested.connect(releases.append)
    try:
        widget.participant.setText('TEST')
        widget.setup.setText('Software fixture')
        widget.request_collection()
        assert not requests  # consent not yet checked
        widget.consent.setChecked(True)
        widget.request_collection()
        token = requests[0][1]
        assert not widget.begin_button.isEnabled()
        widget.stop_collection()
        assert not widget.attach_capture(token, 'old', 'TEST')
        widget.request_collection()
        assert widget.attach_capture(requests[-1][1], 'capture1', 'TEST')
        assert widget.begin_button.isEnabled()
        widget.begin_trial()
        assert not widget.begin_button.isEnabled()
        assert not widget.form.isEnabled()
        widget.stop_collection()
        assert widget.session is not None
        assert widget.session.state == 'cancelled'
        assert widget.form.isEnabled()
        assert not list(tmp_path.rglob('*.json'))
    finally:
        widget.close()


@pytest.mark.parametrize('action', ['stop', 'hide', 'close'])
def test_widget_cancels_save_error_capture_once_and_retries(action, tmp_path, monkeypatch):
    os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
    from PySide6.QtGui import QCloseEvent, QHideEvent
    from PySide6.QtWidgets import QApplication
    from gestureforge.enrolment_widget import EnrolmentWidget
    app = QApplication.instance() or QApplication([])
    assert app is not None
    now = 0.
    widget = EnrolmentWidget(tmp_path, clock=lambda: now)
    requests = []
    releases: list[str] = []
    widget.capture_requested.connect(lambda plan, token: requests.append((plan, token)))
    widget.capture_release_requested.connect(releases.append)
    save = enrolment.save_dataset
    def fail(*args, **kwargs):
        raise OSError('disk full')
    try:
        widget.participant.setText('TEST')
        widget.setup.setText('Software fixture')
        widget.consent.setChecked(True)
        widget.request_collection()
        token = requests[0][1]
        assert widget.attach_capture(token, 'capture1', 'TEST')
        widget.begin_trial()
        monkeypatch.setattr(enrolment, 'save_dataset', fail)
        for index, offset in enumerate(OFFSETS):
            now = 2. + offset + .01
            widget.receive_observation(observation(now, index))
        now = 4.1
        widget.tick()
        assert widget.session is not None
        assert widget.session.state == 'save_error'
        assert not releases
        if action == 'stop':
            widget.stop_collection()
        elif action == 'hide':
            widget.hideEvent(QHideEvent())
        else:
            event = QCloseEvent()
            widget.closeEvent(event)
            assert not event.isAccepted()
        assert widget.session.state == 'save_error'
        assert releases == [token]
        assert widget.retry_button.isEnabled()
        widget.stop_collection()
        assert releases == [token]
        monkeypatch.setattr(enrolment, 'save_dataset', save)
        now = 4.2
        widget.retry_save()
        assert widget.session.state == 'cancelled'
        assert releases == [token]
        assert len(load_dataset(widget.session.manifest).records) == 5
    finally:
        monkeypatch.setattr(enrolment, 'save_dataset', save)
        widget.session = None
        widget.close()


@pytest.mark.parametrize('action', ['stop', 'hide', 'close'])
def test_widget_stop_induced_save_failure_releases_capture_once(action, tmp_path, monkeypatch):
    os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
    from PySide6.QtGui import QCloseEvent, QHideEvent
    from PySide6.QtWidgets import QApplication
    from gestureforge.enrolment_widget import EnrolmentWidget
    app = QApplication.instance() or QApplication([])
    assert app is not None
    now = 0.
    widget = EnrolmentWidget(tmp_path, clock=lambda: now)
    requests = []
    releases: list[str] = []
    widget.capture_requested.connect(lambda plan, token: requests.append((plan, token)))
    widget.capture_release_requested.connect(releases.append)
    save = enrolment.save_dataset
    def fail(*args, **kwargs):
        raise OSError('disk full')
    try:
        widget.participant.setText('TEST')
        widget.setup.setText('Software fixture')
        widget.consent.setChecked(True)
        widget.request_collection()
        token = requests[0][1]
        assert widget.attach_capture(token, 'capture1', 'TEST')
        widget.begin_trial()
        now = 2.21
        widget.receive_observation(observation(now, 1))
        monkeypatch.setattr(enrolment, 'save_dataset', fail)
        now = 2.3
        if action == 'stop':
            widget.stop_collection()
        elif action == 'hide':
            widget.hideEvent(QHideEvent())
        else:
            event = QCloseEvent()
            widget.closeEvent(event)
            assert not event.isAccepted()
        assert widget.session is not None
        assert widget.session.state == 'save_error'
        assert len(widget.session.pending_records) == 5
        assert releases == [token]
        widget.stop_collection()
        assert releases == [token]
        monkeypatch.setattr(enrolment, 'save_dataset', save)
        now = 2.4
        widget.retry_save()
        assert widget.session.state == 'cancelled'
        bundle = load_dataset(widget.session.manifest)
        assert len(bundle.records) == 5
        assert len(bundle.valid_records()) == 1
        assert releases == [token]
    finally:
        monkeypatch.setattr(enrolment, 'save_dataset', save)
        widget.session = None
        widget.close()
