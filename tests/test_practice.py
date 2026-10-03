"""Generated predictions test mechanics, never participant recognition readiness."""
from dataclasses import replace
import json

import pytest

from gestureforge.contracts import Action, ActionType, Prediction, RoutingMode, RoutingSnapshot
from gestureforge.dispatcher import Dispatcher
from gestureforge.practice import PersonalRehearsal, PracticeResult
from gestureforge.routing import RoutingSession
from gestureforge.shortcuts import TargetRegistry


class ForbiddenLauncher:
    def open(self, *args):
        raise AssertionError('Rehearsal must never call an external launcher')


class Harness:
    def __init__(self):
        self.bindings = {'G1': Action(ActionType.NEXT), 'G2': Action(ActionType.PREVIOUS),
                         'G3': Action(ActionType.OPEN_SHORTCUT, 'unbound')}
        self.router = RoutingSession('P-test', 'model-test', 'practice', self.bindings, RoutingMode.REHEARSAL)
        self.dispatcher = Dispatcher(TargetRegistry(), ForbiddenLauncher(), lambda: self.router.snapshot,
                                     lambda: True, lambda _: False, self.router.pause, lambda _: False)
        self.revision = 'behavior-test'
        self.attempt = PersonalRehearsal(self.router, self.dispatcher, self.revision,
                                        lambda: self.revision, tuple(self.bindings))
        self.now = 10.0
        self.frame = 0

    def feed(self, label, *, accepted=True, reason='', gap=.1):
        self.now = round(self.now + gap, 6)
        self.frame += 1
        snap = self.router.snapshot
        prediction = Prediction(snap.session_id, snap.profile_id, self.frame, self.now,
                                label, accepted, snap.model_version, reason)
        self.attempt.receive(prediction, self.now)
        return prediction

    def prepare(self):
        self.attempt.prepare(self.now)
        for _ in range(6):
            self.feed('NEUTRAL')
        self.attempt.begin_window(self.now)

    def window(self, label, *, accepted=True, reason='', gap=.1):
        self.prepare()
        started = self.now
        while self.now < started + 4.89:
            self.feed(label, accepted=accepted, reason=reason, gap=gap)
        self.now = round(started + 5, 6)
        self.attempt.tick(self.now)


def test_full_protocol_uses_real_router_and_persistent_simulated_dispatcher(tmp_path):
    h = Harness()
    for prompt in h.attempt.sequence:
        label = prompt.expected if prompt.expected != 'NEGATIVE' else 'UNKNOWN'
        h.window(label, accepted=label != 'UNKNOWN', reason='margin_rejection' if label == 'UNKNOWN' else '')
    result = h.attempt.result()
    assert result.status == 'passed'
    assert len(result.trials) == 50
    assert dict(result.correct_per_pose) == {'G1': 10, 'G2': 10, 'G3': 10, 'NEUTRAL': 10}
    assert result.negative_actions == 0
    assert len(h.dispatcher.summary.outcomes) == 30
    assert all(o.status == 'simulated' for o in h.dispatcher.summary.outcomes)
    assert all(len(t.event_ids) == 1 for t in result.trials if t.expected in h.bindings)
    path = h.attempt.save(tmp_path)
    saved = json.loads(path.read_text())
    assert saved['simulation_only'] and saved['behavior_revision'] == 'behavior-test'
    assert 'features' not in saved and 'frames' not in saved  # only per-trial counts
    assert h.attempt.passed_for('behavior-test')
    assert not h.attempt.passed_for('different')
    h.revision = 'new-behavior'
    assert not h.attempt.passed_for('behavior-test')
    assert h.attempt.result().status == 'expired'


def test_missing_neutral_never_arms_and_unknown_only_never_passes():
    h = Harness()
    h.attempt.prepare(h.now)
    for _ in range(50):
        h.feed('G1')
    with pytest.raises(ValueError, match='NEUTRAL'):
        h.attempt.begin_window(h.now)
    assert not h.dispatcher.summary.outcomes
    h = Harness()
    h.window('UNKNOWN', accepted=False, reason='margin_rejection')
    trial = h.attempt.result().trials[0]
    assert trial.outcome == 'missed' and trial.coverage_ok
    assert dict(trial.rejections)['margin_rejection'] > 0
    assert not h.attempt.passed_for(h.revision)


def test_wrong_pose_and_repeat_after_rearm_do_not_earn_credit():
    h = Harness()
    h.window('G2')
    assert h.attempt.result().trials[0].outcome == 'wrong'
    h = Harness()
    h.prepare()
    start = h.now
    for label, frames in [('G1', 10), ('NEUTRAL', 6), ('G1', 33)]:
        for _ in range(frames):
            h.feed(label)
    h.attempt.tick(start + 5)
    trial = h.attempt.result().trials[0]
    assert trial.actions == ('G1', 'G1') and trial.outcome == 'wrong'


def test_no_camera_frames_cannot_pass_as_safe_negative_or_correct_positive():
    h = Harness()
    h.prepare()
    h.attempt.tick(h.now + 5)
    trial = h.attempt.result().trials[0]
    assert trial.outcome == 'inconclusive' and not trial.coverage_ok
    h = Harness()
    h.prepare()
    start = h.now
    h.feed('G1', gap=.25)
    while h.now < start + 4.89:
        h.feed('G1')
    h.attempt.tick(h.now + .2)
    assert h.attempt.result().trials[0].outcome == 'inconclusive'


def test_neutral_trial_cannot_inherit_preparation_ready():
    h = Harness()
    for label in h.bindings:
        h.window(label)
    assert h.attempt.expected is not None and h.attempt.expected.expected == 'NEUTRAL'
    h.window('UNKNOWN', accepted=False, reason='margin_rejection')
    assert h.attempt.result().trials[-1].outcome == 'missed'


def test_negative_activation_fails_after_otherwise_successful_pose_trials():
    h = Harness()
    for prompt in h.attempt.sequence[:40]:
        h.window(prompt.expected)
    h.window('G1')
    for _ in range(9):
        h.window('UNKNOWN', accepted=False, reason='distance_rejection')
    result = h.attempt.result()
    assert result.status == 'failed' and result.negative_actions == 1
    assert result.trials[40].outcome == 'wrong'


@pytest.mark.parametrize('change', ['revision', 'mode', 'generation'])
def test_behavior_or_mode_change_expires_partial_results(change):
    h = Harness()
    h.prepare()
    h.feed('G1')
    if change == 'revision':
        h.revision = 'different'
    elif change == 'mode':
        h.router.configure('P-test', 'model-test', 'practice', h.bindings, RoutingMode.LIVE)
    else:
        h.router.resume()
    h.attempt.tick(h.now)
    result = h.attempt.result()
    assert result.status == 'expired' and result.trials[0].outcome == 'interrupted'
    assert not h.dispatcher.summary.outcomes


def test_stale_packet_cancels_and_old_generation_cannot_count():
    h = Harness()
    h.prepare()
    snap = h.router.snapshot
    p = Prediction('old', snap.profile_id, 100, h.now, 'G1', True, snap.model_version)
    h.attempt.receive(p, h.now)
    assert h.attempt.status == 'measuring'
    h.attempt.receive(replace(p, session_id=snap.session_id, timestamp=h.now - 1), h.now)
    assert h.attempt.result().status == 'cancelled'


def test_recording_failure_and_user_stop_preserve_evidence(tmp_path, monkeypatch):
    h = Harness()
    h.prepare()
    h.feed('G1')
    h.attempt.cancel('user stopped')
    assert h.attempt.result().trials[0].outcome == 'interrupted'
    import gestureforge.practice as practice
    with monkeypatch.context() as patch:
        patch.setattr(practice, 'atomic_write_json', lambda *a, **k: (_ for _ in ()).throw(OSError('disk full')))
        with pytest.raises(OSError):
            h.attempt.save(tmp_path)
    assert len(h.attempt.result().trials) == 1
    assert h.attempt.save(tmp_path).exists()
    h = Harness()
    monkeypatch.setattr(h.dispatcher, 'dispatch', lambda *a, **k: (_ for _ in ()).throw(ValueError('full')))
    h.prepare()
    for _ in range(8):
        h.feed('G1')
    assert h.attempt.status == 'cancelled'


def test_preparation_action_is_recorded_as_interruption_not_silently_ignored():
    h = Harness()
    h.attempt.prepare(h.now)
    for _ in range(6):
        h.feed('NEUTRAL')
    for _ in range(8):
        h.feed('G1')
    result = h.attempt.result()
    assert result.status == 'cancelled'
    assert result.trials[0].actions == ('G1',)


def test_initial_live_and_invalid_negative_protocol_are_rejected():
    h = Harness()
    h.router.configure('P-test', 'model-test', 'practice', h.bindings, RoutingMode.LIVE)
    with pytest.raises(ValueError, match='REHEARSAL'):
        PersonalRehearsal(h.router, h.dispatcher, h.revision, lambda: h.revision, tuple(h.bindings))
    h = Harness()
    with pytest.raises(ValueError, match='ten explicit'):
        PersonalRehearsal(h.router, h.dispatcher, h.revision, lambda: h.revision,
                         tuple(h.bindings), negative_cues=('unknown',))


def test_widget_uses_host_capture_signals_and_saves_on_stop(tmp_path):
    from PySide6.QtWidgets import QApplication
    from gestureforge.practice_widget import PersonalRehearsalWidget
    app = QApplication.instance() or QApplication([])
    h = Harness()
    widget = PersonalRehearsalWidget(h.attempt, tmp_path, clock=lambda: h.now)
    snapshots: list[RoutingSnapshot] = []
    releases: list[bool] = []
    results: list[PracticeResult] = []
    widget.snapshot_requested.connect(snapshots.append)
    widget.capture_release_requested.connect(lambda: releases.append(True))
    widget.result_ready.connect(results.append)
    widget.prepare()
    assert snapshots == [h.router.snapshot]
    widget.stop()
    assert len(releases) == 1 and len(results) == 1
    assert list(tmp_path.glob('practice-*.json'))
    assert results[0].status == 'cancelled'
    widget.close()
    app.processEvents()
