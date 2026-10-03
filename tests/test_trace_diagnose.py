import json

import pytest

from gestureforge.contracts import Action, ActionType, Prediction, RoutingMode, RoutingSnapshot
from gestureforge.trace_diagnose import diagnose_trace
from gestureforge.traces import EvaluationTrace


def test_unannotated_trace_distinguishes_rejected_neutral_and_recovery(tmp_path):
    snap = RoutingSnapshot('session1', 'P-test', 'model-test', 'preview',
                           (('G1', Action(ActionType.NEXT)),), RoutingMode.PREVIEW)
    trace = EvaluationTrace(snap)
    labels = ['NEUTRAL'] * 6 + ['G1'] * 7 + ['NEUTRAL'] * 6 + ['NEUTRAL'] * 6
    for i, label in enumerate(labels):
        rejected = 13 <= i < 19
        trace.append(Prediction('session1', 'P-test', i, i / 10, label, not rejected,
                                'model-test', 'margin_rejection' if rejected else ''), i / 10 + .01)
    path = tmp_path / 'trace.json'
    trace.save(path)
    original = path.read_bytes()
    result = diagnose_trace(path)
    assert result['counts']['rejected_neutral'] == 6
    assert result['frames'][14]['reconstructed_after'] == 'LATCHED'
    assert result['frames'][-1]['reconstructed_after'] == 'READY'
    assert result['counts']['simulated_command_events'] == 1
    assert path.read_bytes() == original
    assert not json.loads(original)['annotation_complete']


def test_trace_diagnosis_requires_recorded_receipt_time(tmp_path):
    path = tmp_path / 'trace.json'
    path.write_text(json.dumps({'schema_version': 1, 'session_id': 's', 'profile_id': 'p',
        'model_version': 'm', 'context_id': 'c', 'bindings': {'G1': {'kind': 'NEXT'}},
        'frames': [{'frame_id': 1, 'timestamp': 0., 'label': 'NEUTRAL', 'accepted': True}]}))
    with pytest.raises(ValueError, match='receipt timing'):
        diagnose_trace(path)
