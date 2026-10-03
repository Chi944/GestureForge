"""Generated predictions test mechanics, never participant recognition readiness."""
from dataclasses import replace
import json

import pytest

from gestureforge.contracts import Action, ActionType, Prediction, RoutingMode, RoutingSnapshot
from gestureforge.controller import MAX_PREDICTION_AGE_SECONDS
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

    def feed_at(self, label, *, captured, received, accepted=True, reason=''):
        self.now = received
        self.frame += 1
        snap = self.router.snapshot
        prediction = Prediction(snap.session_id, snap.profile_id, self.frame, captured,
                                label, accepted, snap.model_version, reason)
        self.attempt.receive(prediction, received)
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
        self.now = round(started + 5 + MAX_PREDICTION_AGE_SECONDS + 0.000001, 6)
        self.attempt.tick(self.now)


def prepare_fixed_latency_window(h):
    h.attempt.prepare(h.now)
    latency = 0.15625
    for captured in (10.125, 10.25, 10.375, 10.5, 10.625, 10.75):
        h.feed_at('NEUTRAL', captured=captured, received=captured + latency)
    assert h.attempt.status == 'armed'
    h.attempt.begin_window(h.now)
    return h.now, latency


@pytest.mark.parametrize('pose', ['G2', 'NEUTRAL'])
def test_single_pose_diagnostic_saves_only_selected_window_and_never_passes(pose, tmp_path):
    h = Harness()
    h.attempt.select_diagnostic_pose(pose)
    h.window(pose)
    result = h.attempt.result()
    assert len(result.trials) == 1
    assert result.trials[0].expected == pose
    assert result.trials[0].outcome == 'correct'
    assert result.status == 'cancelled'
    assert result.protocol_version == 'gf-p12-single-pose-diagnostic-v1'
    assert 'diagnostic complete' in result.reason
    assert not h.attempt.passed_for(h.revision)
    assert h.router.state == 'PAUSED'
    saved = json.loads(h.attempt.save(tmp_path).read_text())
    assert saved['simulation_only'] is True
    assert len(saved['trials']) == 1
    assert saved['protocol_version'] != 'gf-p12-v1'


def test_diagnostic_cannot_skip_or_replace_an_already_prepared_attempt():
    h = Harness()
    with pytest.raises(ValueError, match='enrolled pose'):
        h.attempt.select_diagnostic_pose('UNKNOWN')
    h.attempt.select_diagnostic_pose('NEUTRAL')
    h.attempt.select_diagnostic_pose(None)
    assert len(h.attempt.sequence) == 50
    h.attempt.prepare(h.now)
    with pytest.raises(ValueError, match='before preparing'):
        h.attempt.select_diagnostic_pose('NEUTRAL')


def test_single_pose_widget_uses_existing_capture_and_saves_once(tmp_path):
    from PySide6.QtWidgets import QApplication
    from gestureforge.practice_widget import PersonalRehearsalWidget
    app = QApplication.instance() or QApplication([])
    h = Harness()
    widget = PersonalRehearsalWidget(h.attempt, tmp_path, clock=lambda: h.now)
    results: list[PracticeResult] = []
    releases = []
    widget.result_ready.connect(results.append)
    widget.capture_release_requested.connect(lambda: releases.append(True))
    widget.test_selection.setCurrentIndex(4)
    assert h.attempt.expected is not None
    assert h.attempt.expected.expected == 'NEUTRAL'
    assert 'Diagnostic only | 0/1' in widget.prompt.text()
    widget.prepare()
    assert not widget.test_selection.isEnabled()
    for _ in range(6):
        h.feed('NEUTRAL')
    widget.refresh()
    widget.begin_button.click()
    start = h.now
    while h.now < start + 4.89:
        h.feed('NEUTRAL')
    h.now = start + 5.21
    widget.tick()
    assert '1/1 completed | diagnostic complete' in widget.prompt.text()
    assert len(results) == len(releases) == 1
    assert len(list(tmp_path.glob('practice-*.json'))) == 1
    assert results[0].trials[0].outcome == 'correct'
    widget.close()
    app.processEvents()
    assert len(results) == len(releases) == 1


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
    h.router.configure('P-test', 'model-test', 'restored-live', h.bindings, RoutingMode.LIVE)
    h.router.resume()
    restored_state = h.router.state
    assert h.attempt.result().status == 'passed'
    assert h.attempt.save(tmp_path).exists()
    h.attempt.tick(h.now + .1)
    h.attempt.cancel('late host cleanup')
    assert h.router.state == restored_state
    h.revision = 'new-behavior'
    assert not h.attempt.passed_for('behavior-test')
    assert h.attempt.result().status == 'passed'


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
    h.attempt.tick(start + 5 + MAX_PREDICTION_AGE_SECONDS + 0.000001)
    trial = h.attempt.result().trials[0]
    assert trial.actions == ('G1', 'G1') and trial.outcome == 'wrong'


def test_no_camera_frames_cannot_pass_as_safe_negative_or_correct_positive():
    h = Harness()
    h.prepare()
    h.attempt.tick(h.now + 5)
    assert h.attempt.result().trials == ()
    h.attempt.tick(h.now + 5 + MAX_PREDICTION_AGE_SECONDS + 0.000001)
    trial = h.attempt.result().trials[0]
    assert trial.outcome == 'inconclusive' and not trial.coverage_ok
    h = Harness()
    h.prepare()
    start = h.now
    h.feed('G1', gap=.25)
    while h.now < start + 4.89:
        h.feed('G1')
    h.attempt.tick(start + 5 + MAX_PREDICTION_AGE_SECONDS + 0.000001)
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


def test_late_fresh_in_window_action_is_scored_before_drain_finishes():
    h = Harness()
    for prompt in h.attempt.sequence[:40]:
        h.window(prompt.expected)
    h.prepare()
    start = h.now
    previous_outcomes = len(h.dispatcher.summary.outcomes)
    offset = 0.1
    while offset < 4.376:
        h.feed('NEUTRAL', gap=round(start + offset - h.now, 6))
        offset = round(offset + 0.125, 6)
    for offset in (4.5, 4.625, 4.75, 4.875):
        h.feed('G1', gap=round(start + offset - h.now, 6))
    h.attempt.tick(start + 5.0)
    assert h.attempt.status == 'measuring'
    h.frame += 1
    snap = h.router.snapshot
    final = Prediction(snap.session_id, snap.profile_id, h.frame, start + 4.9375,
                       'G1', True, snap.model_version)
    h.now = start + 5.05
    h.attempt.receive(final, h.now)
    new_outcomes = h.dispatcher.summary.outcomes[previous_outcomes:]
    assert len(new_outcomes) == 1
    assert new_outcomes[0].action is not None
    assert new_outcomes[0].action.kind is ActionType.NEXT
    h.attempt.tick(start + 5.2 + 0.000001)
    trial = h.attempt.result().trials[-1]
    assert trial.expected == 'NEGATIVE'
    assert trial.outcome == 'wrong'
    assert trial.actions == ('G1',)


def test_pre_begin_neutral_preserves_controller_continuity_for_fixed_latency_stream():
    h = Harness()
    started, latency = prepare_fixed_latency_window(h)
    h.feed_at('NEUTRAL', captured=10.875, received=10.875 + latency)
    assert h.attempt.status == 'measuring'
    assert h.router.state == 'READY'
    captured = 11.0
    while captured < started + 4.98:
        h.feed_at('G1', captured=captured, received=captured + latency)
        captured = round(captured + 0.125, 6)
    h.attempt.tick(started + 5.0 + MAX_PREDICTION_AGE_SECONDS + 0.000001)
    trial = h.attempt.result().trials[0]
    assert trial.outcome == 'correct'
    assert trial.actions == ('G1',)
    assert trial.coverage_ok


def test_pre_begin_command_after_begin_cancels_without_trial_credit(tmp_path):
    h = Harness()
    _started, latency = prepare_fixed_latency_window(h)
    h.feed_at('G1', captured=10.875, received=10.875 + latency)
    result = h.attempt.result()
    assert result.status == 'cancelled'
    assert result.trials[0].outcome == 'interrupted'
    assert result.trials[0].actions == ()
    assert 'no command was emitted' in result.reason
    saved = json.loads(h.attempt.save(tmp_path).read_text())
    timing = saved['timing_diagnostics']
    assert timing['last_begin_attempt']['accepted'] is True
    assert timing['boundary_prediction']['captured_at'] < timing['last_begin_attempt']['requested_at']
    assert timing['boundary_prediction']['received_at'] > timing['last_begin_attempt']['requested_at']
    assert timing['boundary_prediction']['command_emitted'] is False


def test_rejected_begin_records_reason_and_successful_retry(tmp_path):
    h = Harness()
    h.attempt.prepare(h.now)
    with pytest.raises(ValueError, match='fresh capture'):
        h.attempt.begin_window(h.now)
    failed = json.loads(h.attempt.save(tmp_path).read_text())['timing_diagnostics']
    assert failed['last_begin_attempt']['accepted'] is False
    assert 'fresh capture' in failed['last_begin_attempt']['error']
    for _ in range(6):
        h.feed('NEUTRAL')
    h.attempt.begin_window(h.now)
    assert h.attempt.status == 'measuring'
    assert h.attempt.last_begin_attempt is not None
    assert h.attempt.last_begin_attempt['accepted'] is True
    assert 'error' not in h.attempt.last_begin_attempt


@pytest.mark.parametrize('invalid_time', [float('nan'), float('inf'), -float('inf'), True, 'bad'])
def test_invalid_begin_time_cannot_prevent_saving_evidence(tmp_path, invalid_time):
    h = Harness()
    h.attempt.prepare(h.now)
    with pytest.raises(ValueError, match='monotonic time'):
        h.attempt.begin_window(invalid_time)
    payload = json.loads(h.attempt.save(tmp_path).read_text())
    assert payload['timing_diagnostics']['last_begin_attempt']['requested_at'] is None
    assert payload['timing_diagnostics']['last_begin_attempt']['accepted'] is False
    assert payload['trials'] == []


def test_widget_confirms_begin_success_and_distinguishes_rejected_click(tmp_path):
    from PySide6.QtWidgets import QApplication
    from gestureforge.practice_widget import PersonalRehearsalWidget
    app = QApplication.instance() or QApplication([])
    h = Harness()
    widget = PersonalRehearsalWidget(h.attempt, tmp_path, clock=lambda: h.now)
    widget.prepare()
    widget.begin()
    assert 'Window not started' in widget.feedback.text()
    for _ in range(6):
        h.feed('NEUTRAL')
    widget.refresh()
    widget.begin_button.click()
    assert h.attempt.status == 'measuring'
    assert 'Measurement started' in widget.feedback.text()
    assert '5.0 seconds remaining' in widget.countdown.text()
    h.now += 2.5
    widget.refresh()
    assert '2.5 seconds remaining' in widget.countdown.text()
    assert h.attempt.completed == 0
    h.now += 2.5
    widget.refresh()
    assert 'finishing the trial' in widget.countdown.text()
    assert h.attempt.status == 'measuring'
    widget.close()
    app.processEvents()


def test_in_window_packet_delivered_at_drain_boundary_is_scored():
    h = Harness()
    h.prepare()
    start = h.now
    previous_outcomes = len(h.dispatcher.summary.outcomes)
    offset = 0.1
    while offset < 4.51:
        h.feed('NEUTRAL', gap=round(start + offset - h.now, 6))
        offset = round(offset + 0.1, 6)
    for offset in (4.6, 4.75, 4.875):
        h.feed('G1', gap=round(start + offset - h.now, 6))
    h.frame += 1
    snap = h.router.snapshot
    boundary = Prediction(snap.session_id, snap.profile_id, h.frame, start + 5.0,
                          'G1', True, snap.model_version)
    h.now = start + 5.0 + MAX_PREDICTION_AGE_SECONDS
    h.attempt.receive(boundary, h.now)
    new_outcomes = h.dispatcher.summary.outcomes[previous_outcomes:]
    assert len(new_outcomes) == 1
    assert h.attempt.result().trials == ()
    h.attempt.tick(h.now + 0.000001)
    trial = h.attempt.result().trials[0]
    assert trial.outcome == 'correct'
    assert trial.actions == ('G1',)


def test_timer_first_at_drain_boundary_still_allows_boundary_packet():
    h = Harness()
    h.prepare()
    start = h.now
    previous_outcomes = len(h.dispatcher.summary.outcomes)
    offset = 0.1
    while offset < 4.51:
        h.feed('NEUTRAL', gap=round(start + offset - h.now, 6))
        offset = round(offset + 0.1, 6)
    for offset in (4.6, 4.75, 4.875):
        h.feed('G1', gap=round(start + offset - h.now, 6))
    deadline = start + 5.0 + MAX_PREDICTION_AGE_SECONDS
    h.attempt.tick(deadline)
    assert h.attempt.status == 'measuring'
    h.frame += 1
    snap = h.router.snapshot
    boundary = Prediction(snap.session_id, snap.profile_id, h.frame, start + 5.0,
                          'G1', True, snap.model_version)
    h.attempt.receive(boundary, deadline)
    new_outcomes = h.dispatcher.summary.outcomes[previous_outcomes:]
    assert len(new_outcomes) == 1
    assert h.attempt.result().trials == ()
    h.attempt.tick(deadline + 0.000001)
    trial = h.attempt.result().trials[0]
    assert trial.outcome == 'correct'
    assert trial.actions == ('G1',)


def test_post_window_capture_is_excluded_from_scoring_interval():
    h = Harness()
    h.prepare()
    start = h.now
    offset = 0.1
    while offset < 4.91:
        h.feed('UNKNOWN', accepted=False, reason='distance_rejection',
               gap=round(start + offset - h.now, 6))
        offset = round(offset + 0.1, 6)
    h.frame += 1
    snap = h.router.snapshot
    after = Prediction(snap.session_id, snap.profile_id, h.frame, start + 5.05,
                       'G1', True, snap.model_version)
    h.attempt.receive(after, start + 5.06)
    h.attempt.tick(start + 5.2)
    trial = h.attempt.result().trials[0]
    assert trial.outcome == 'missed'
    assert trial.actions == ()


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


def test_preparation_startup_stale_packet_recovers_and_requires_fresh_neutral(tmp_path):
    h = Harness()
    snap = h.attempt.prepare(h.now)
    h.frame += 1
    stale = Prediction(snap.session_id, snap.profile_id, h.frame, h.now - 0.25,
                       'G1', True, snap.model_version)
    h.attempt.receive(stale, h.now)
    assert h.attempt.status == 'preparing'
    assert h.router.snapshot == snap
    assert h.router.state == 'WAIT_NEUTRAL'
    assert h.dispatcher.summary.outcomes == []
    assert h.attempt.result().trials == ()
    with pytest.raises(ValueError, match='fresh capture'):
        h.attempt.begin_window(h.now)
    payload = json.loads(h.attempt.save(tmp_path).read_text())
    diagnostic = payload['timing_diagnostics']['last_capture_validation']
    assert diagnostic['reason'] == 'stale_prediction'
    assert diagnostic['decision'] == 'dropped_and_rearmed'
    assert diagnostic['recovered'] is True
    for _ in range(4):
        h.feed('NEUTRAL')
    assert h.attempt.status == 'armed'
    h.attempt.begin_window(h.now)
    assert h.attempt.status == 'measuring'


def test_stale_preparation_packet_after_partial_hold_requires_full_new_hold():
    h = Harness()
    snap = h.attempt.prepare(h.now)
    h.feed('NEUTRAL')
    assert h.attempt.status == 'preparing'
    h.frame += 1
    h.now = 10.5
    stale = Prediction(snap.session_id, snap.profile_id, h.frame, 10.2,
                       'NEUTRAL', True, snap.model_version)
    h.attempt.receive(stale, h.now)
    assert h.attempt.status == 'preparing'
    assert h.router.state == 'WAIT_NEUTRAL'
    h.feed('NEUTRAL')
    with pytest.raises(ValueError, match='READY'):
        h.attempt.begin_window(h.now)
    for _ in range(3):
        h.feed('NEUTRAL')
    assert h.attempt.status == 'armed'


def test_stale_preparation_packet_at_timeout_preserves_timeout_cancel():
    h = Harness()
    snap = h.attempt.prepare(h.now)
    h.frame += 1
    stale = Prediction(snap.session_id, snap.profile_id, h.frame, h.now + 29.7,
                       'NEUTRAL', True, snap.model_version)
    h.attempt.receive(stale, h.now + 30.0)
    result = h.attempt.result()
    assert result.status == 'cancelled'
    assert result.reason == 'Preparation timed out; review capture and NEUTRAL evidence.'
    assert result.trials[0].outcome == 'interrupted'


def test_stale_packet_only_recovers_while_preparing():
    h = Harness()
    h.attempt.prepare(h.now)
    for _ in range(6):
        h.feed('NEUTRAL')
    assert h.attempt.status == 'armed'
    snap = h.router.snapshot
    stale = Prediction(snap.session_id, snap.profile_id, h.frame + 1, h.now + 0.1,
                       'NEUTRAL', True, snap.model_version)
    h.attempt.receive(stale, h.now + 0.35)
    assert h.attempt.result().status == 'cancelled'
    h = Harness()
    h.prepare()
    snap = h.router.snapshot
    stale = Prediction(snap.session_id, snap.profile_id, h.frame + 1, h.now + 0.1,
                       'NEUTRAL', True, snap.model_version)
    h.attempt.receive(stale, h.now + 0.35)
    assert h.attempt.result().status == 'cancelled'


@pytest.mark.parametrize(
    ('packet_change', 'reason'),
    [
        ({'timestamp': float('nan')}, 'invalid_timestamp'),
        ({'timestamp': 10.5}, 'future_timestamp'),
        ({'frame_id': 'bad'}, 'invalid_frame_id'),
        ({'accepted': 'yes'}, 'invalid_accepted_flag'),
        ({'label': None}, 'invalid_label'),
        ({'rejection_reason': None}, 'invalid_rejection_reason'),
        ({'rejection_reason': 'margin_rejection'}, 'accepted_with_rejection_reason'),
        ({'accepted': False}, 'rejected_without_reason'),
    ],
)
def test_malformed_preparation_packets_do_not_recover_and_serialize(tmp_path, packet_change, reason):
    h = Harness()
    snap = h.attempt.prepare(h.now)
    prediction = Prediction(snap.session_id, snap.profile_id, 1, h.now,
                            'NEUTRAL', True, snap.model_version, '')
    h.attempt.receive(replace(prediction, **packet_change), h.now)
    assert h.attempt.result().status == 'cancelled'
    payload = json.loads(h.attempt.save(tmp_path).read_text())
    diagnostic = payload['timing_diagnostics']['last_capture_validation']
    assert diagnostic['reason'] == reason
    assert diagnostic['decision'] == 'terminal_cancel'
    assert diagnostic['recovered'] is False
    assert 'NaN' not in json.dumps(payload, allow_nan=False)


def test_out_of_order_preparation_packet_does_not_recover():
    h = Harness()
    snap = h.attempt.prepare(h.now)
    h.feed('NEUTRAL')
    stale_but_out_of_order = Prediction(snap.session_id, snap.profile_id, h.frame + 1, h.now - 0.3,
                                        'NEUTRAL', True, snap.model_version)
    h.attempt.receive(stale_but_out_of_order, h.now)
    assert h.attempt.result().status == 'cancelled'
    assert h.attempt.last_capture_validation is not None
    assert h.attempt.last_capture_validation['reason'] == 'out_of_order_timestamp'


@pytest.mark.parametrize(
    ('frame_offset', 'captured', 'reason'),
    [
        (0, 10.3, 'out_of_order_frame'),
        (1, 10.0, 'out_of_order_timestamp'),
    ],
)
def test_packet_after_stale_recovery_must_still_advance_monotonic_watermark(frame_offset, captured, reason):
    h = Harness()
    snap = h.attempt.prepare(h.now)
    h.frame += 1
    stale = Prediction(snap.session_id, snap.profile_id, h.frame, 10.2,
                       'NEUTRAL', True, snap.model_version)
    h.attempt.receive(stale, 10.5)
    assert h.attempt.status == 'preparing'
    followup = Prediction(snap.session_id, snap.profile_id, h.frame + frame_offset, captured,
                          'NEUTRAL', True, snap.model_version)
    h.attempt.receive(followup, 10.5)
    assert h.attempt.result().status == 'cancelled'
    assert h.attempt.last_capture_validation is not None
    assert h.attempt.last_capture_validation['reason'] == reason


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


def test_widget_uses_host_capture_signals_and_saves_on_stop(tmp_path, monkeypatch):
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
    saves = []
    original_save = h.attempt.save

    def counted_save(directory):
        path = original_save(directory)
        saves.append(path)
        return path

    monkeypatch.setattr(h.attempt, 'save', counted_save)
    widget.prepare()
    assert snapshots == [h.router.snapshot]
    widget.stop()
    assert len(releases) == 1 and len(results) == 1
    assert list(tmp_path.glob('practice-*.json'))
    assert len(saves) == 1
    assert results[0].status == 'cancelled'
    widget.close()
    app.processEvents()
    assert len(saves) == 1


def test_widget_save_failure_retains_retry_without_extra_terminal_rewrite(tmp_path, monkeypatch):
    from PySide6.QtWidgets import QApplication
    from gestureforge.practice_widget import PersonalRehearsalWidget
    app = QApplication.instance() or QApplication([])
    h = Harness()
    widget = PersonalRehearsalWidget(h.attempt, tmp_path, clock=lambda: h.now)
    attempts = 0
    original_save = h.attempt.save

    def flaky_save(directory):
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise OSError('disk full')
        return original_save(directory)

    monkeypatch.setattr(h.attempt, 'save', flaky_save)
    widget.prepare()
    widget.capture_failed('camera lost')
    assert attempts == 1
    assert widget.save_error
    widget.close()
    app.processEvents()
    assert attempts == 1
    widget.save()
    assert attempts == 2
    assert not widget.save_error
