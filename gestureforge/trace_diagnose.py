"""Replay controller states without inventing intended poses or scoring accuracy."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
from pathlib import Path
from uuid import uuid4

from .contracts import Action, ActionType, Prediction, RoutingMode, RoutingSnapshot
from .controller import (
    Controller, NEUTRAL_HOLD_SECONDS, MAX_FRAME_GAP_SECONDS, MAX_PREDICTION_AGE_SECONDS,
)
from .storage import atomic_write_json, read_json
from .traces import EvaluationTrace


def diagnose_trace(path: Path) -> dict:
    """Validate using the recorder's rules, then replay the current controller.

    Physical pose annotations are deliberately separate. This accepts original
    unannotated UI traces for diagnosis, not the scored replay/accuracy workflow.
    """
    data = read_json(path, limit=16 * 1024 * 1024)
    if not isinstance(data, dict) or type(data.get('schema_version')) is not int or data['schema_version'] != 1:
        raise ValueError('trace schema version 1 is required')
    try:
        bindings = tuple((key, Action(ActionType(value['kind']), value.get('shortcut_id')))
                         for key, value in data['bindings'].items())
        snapshot = RoutingSnapshot(data['session_id'], data['profile_id'], data['model_version'],
                                   data['context_id'], bindings, RoutingMode.REHEARSAL)
        frames = data['frames']
    except (KeyError, TypeError, AttributeError) as exc:
        raise ValueError('trace identity/bindings are incomplete') from exc
    if not isinstance(frames, list) or not 1 <= len(frames) <= 18000:
        raise ValueError('trace must contain 1–18000 recorded frames')
    validator = EvaluationTrace(snapshot)
    controller = Controller(snapshot.session_id, snapshot.profile_id,
                            executable_gesture_ids=frozenset(dict(bindings)),
                            model_version=snapshot.model_version)
    controller.resume(session_id=snapshot.session_id)
    rows = []
    counts: Counter[str] = Counter()
    previous: float | None = None
    start: float | None = None
    for frame in frames:
        try:
            prediction = Prediction(snapshot.session_id, snapshot.profile_id, frame['frame_id'],
                                    frame['timestamp'], frame['label'], frame['accepted'],
                                    snapshot.model_version, frame.get('rejection_reason', ''))
            received = frame['received_at']
        except (TypeError, KeyError) as exc:
            raise ValueError('each frame requires recorded label, acceptance and receipt timing') from exc
        validator.append(prediction, received)
        if start is None:
            start = received
        before = controller.state
        event = controller.process(prediction, received)
        gap = None if previous is None else prediction.timestamp - previous
        age = received - prediction.timestamp
        row = {
            'frame_id': prediction.frame_id, 'timestamp': prediction.timestamp,
            'received_at': received, 'seconds_from_first_receipt': received - start,
            'label': prediction.label, 'accepted': prediction.accepted,
            'rejection_reason': prediction.rejection_reason,
            'reconstructed_before': before, 'reconstructed_after': controller.state,
            'controller_reason': controller.last_error, 'prediction_age': age,
            'gap': gap, 'would_emit': event.command if event else None,
        }
        rows.append(row)
        if prediction.label == 'NEUTRAL':
            counts['accepted_neutral' if prediction.accepted else 'rejected_neutral'] += 1
            if prediction.accepted and controller.state == 'READY':
                counts['accepted_neutral_ready'] += 1
        if gap is not None and gap > MAX_FRAME_GAP_SECONDS:
            counts['excessive_gaps'] += 1
        if age > MAX_PREDICTION_AGE_SECONDS:
            counts['stale_packets'] += 1
        if event:
            counts['simulated_command_events'] += 1
        previous = prediction.timestamp
    return {
        'schema_version': 1, 'trace_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
        'model_version': snapshot.model_version,
        'policy': {'neutral_hold_seconds': NEUTRAL_HOLD_SECONDS,
                   'max_gap_seconds': MAX_FRAME_GAP_SECONDS,
                   'max_prediction_age_seconds': MAX_PREDICTION_AGE_SECONDS},
        'scope': 'Current-controller reconstruction; no physical pose or observed UI state inferred.',
        'limits': 'Compare code revision and separately recorded intended-pose/display notes. No accuracy or readiness score.',
        'counts': dict(counts), 'frames': rows,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('trace', type=Path)
    parser.add_argument('--output-dir', type=Path, default=Path('experiments/local/controller-diagnostics'))
    args = parser.parse_args()
    result = diagnose_trace(args.trace)
    output = args.output_dir / f'diagnosis-{uuid4().hex}.json'
    atomic_write_json(output, result, limit=16 * 1024 * 1024)
    print(output)
    print(result['counts'])


if __name__ == '__main__':
    main()
