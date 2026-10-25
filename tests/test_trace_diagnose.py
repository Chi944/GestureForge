import json

import pytest

from gestureforge.contracts import Action, ActionType, Prediction, RoutingMode, RoutingSnapshot
from gestureforge.trace_diagnose import diagnose_trace
from gestureforge.traces import MAX_TRACE_FRAMES, EvaluationTrace


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
    assert 'recognition_diagnostics' not in result
    assert all('recognition_decision' not in row for row in result['frames'])


def test_trace_diagnosis_requires_recorded_receipt_time(tmp_path):
    path = tmp_path / 'trace.json'
    path.write_text(json.dumps({'schema_version': 1, 'session_id': 's', 'profile_id': 'p',
        'model_version': 'm', 'context_id': 'c', 'bindings': {'G1': {'kind': 'NEXT'}},
        'frames': [{'frame_id': 1, 'timestamp': 0., 'label': 'NEUTRAL', 'accepted': True}]}))
    with pytest.raises(ValueError, match='receipt timing'):
        diagnose_trace(path)


@pytest.fixture
def diagnostic_path(tmp_path):
    snapshot = RoutingSnapshot('s', 'p', 'm', 'c', (('G1', Action(ActionType.NEXT)),), RoutingMode.PREVIEW)
    trace = EvaluationTrace(snapshot, recognition_config={
        'algorithm': 'knn', 'multiplier': 1.5, 'margin': 1.0}, camera_index=0, chosen_hand='Right')
    trace.append(Prediction('s', 'p', 0, 0., 'NEUTRAL', True, 'm'), .01,
                 {'distance': .1, 'threshold': 1., 'competitor_distance': None,
                  'competitor_ratio': None})
    trace.append(Prediction('s', 'p', 1, .1, 'UNKNOWN', False, 'm', 'no_hand'), .11)
    path = tmp_path / 'trace.json'
    trace.save(path)
    return path


@pytest.mark.parametrize('mode', [RoutingMode.PREVIEW.value, RoutingMode.REHEARSAL.value])
@pytest.mark.parametrize('with_capture', [True, False])
def test_recognition_diagnostics_roundtrip(diagnostic_path, mode, with_capture):
    data = json.loads(diagnostic_path.read_text())
    extension = data['recognition_diagnostics']
    extension['mode'] = mode
    if not with_capture:
        extension.pop('capture')
    diagnostic_path.write_text(json.dumps(data))
    original = diagnostic_path.read_bytes()
    result = diagnose_trace(diagnostic_path)
    assert result['recognition_diagnostics'] == {
        key: value for key, value in extension.items() if key != 'frames'}
    assert [row['recognition_decision'] for row in result['frames']] == [
        row['decision'] for row in extension['frames']]
    assert result['frames'][0]['label'] == 'NEUTRAL'
    assert result['frames'][1]['rejection_reason'] == 'no_hand'
    assert diagnostic_path.read_bytes() == original


@pytest.mark.parametrize('keys,value', [
    ((), None), ((), []),
    (('schema_version',), True), (('schema_version',), 1.0), (('schema_version',), 2),
    (('extra',), 'unexpected'), (('mode',), 'live'), (('mode',), None),
    (('config',), None), (('config',), []), (('config',), {}),
    (('config', 'algorithm'), 'other'), (('config', 'multiplier'), 0),
    (('config', 'multiplier'), True), (('config', 'margin'), .5),
    (('config', 'margin'), '1'), (('config', 'extra'), 'unexpected'),
    (('capture',), None), (('capture',), []), (('capture',), {}),
    (('capture', 'camera_index'), None), (('capture', 'camera_index'), True),
    (('capture', 'camera_index'), -1), (('capture', 'chosen_hand'), None),
    (('capture', 'chosen_hand'), 'other'), (('capture', 'extra'), 'unexpected'),
    (('frames',), None), (('frames',), []),
    (('frames', 0), None), (('frames', 0), {'frame_id': 0}),
    (('frames', 0, 'frame_id'), True), (('frames', 0, 'frame_id'), 1),
    (('frames', 1, 'frame_id'), 0), (('frames', 0, 'extra'), 'unexpected'),
    (('frames', 0, 'decision'), []), (('frames', 0, 'decision'), {}),
    (('frames', 0, 'decision', 'extra'), 0),
    (('frames', 0, 'decision', 'distance'), -1),
    (('frames', 0, 'decision', 'threshold'), True),
    (('frames', 0, 'decision', 'competitor_distance'), '1'),
    (('frames', 0, 'decision', 'competitor_ratio'), float('inf')),
])
def test_rejects_malformed_recognition_extension(diagnostic_path, keys, value):
    data = json.loads(diagnostic_path.read_text())
    if not keys:
        data['recognition_diagnostics'] = value
    else:
        target = data['recognition_diagnostics']
        for key in keys[:-1]:
            target = target[key]
        target[keys[-1]] = value
    diagnostic_path.write_text(json.dumps(data))
    with pytest.raises(ValueError):
        diagnose_trace(diagnostic_path)


def test_full_diagnostic_trace_cli_fits_output_limit(tmp_path, monkeypatch):
    from gestureforge.trace_diagnose import main
    snapshot = RoutingSnapshot('s', 'p', 'm', 'c', (('G1', Action(ActionType.NEXT)),), RoutingMode.PREVIEW)
    trace = EvaluationTrace(snapshot, recognition_config={
        'algorithm': 'knn', 'multiplier': 1.5, 'margin': 1.0})
    detail: dict[str, float | None] = {
        'distance': 1.2345678901234567, 'threshold': 2.345678901234567,
        'competitor_distance': 3.456789012345678, 'competitor_ratio': 2.800000000000002}
    for index in range(MAX_TRACE_FRAMES):
        trace.append(Prediction('s', 'p', index, 10. + index * .1, 'NEUTRAL', True, 'm'),
                     10.01 + index * .1, detail)
    source = tmp_path / 'trace.json'
    trace.save(source)
    output = tmp_path / 'diagnoses'
    monkeypatch.setattr('sys.argv', ['trace_diagnose', str(source), '--output-dir', str(output)])
    main()
    files = list(output.glob('diagnosis-*.json'))
    assert len(files) == 1
    assert files[0].stat().st_size < 16 * 1024 * 1024
    result = json.loads(files[0].read_text())
    assert len(result['frames']) == MAX_TRACE_FRAMES
    assert result['frames'][-1]['recognition_decision'] == detail
