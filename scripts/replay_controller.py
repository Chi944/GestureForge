"""Replay saved predictions through GestureForge controller protection.

Input schema version 1:
{
  "schema_version": 1,
  "session_id": "session-1",
  "profile_id": "P01",
  "model_version": "model-v1",
  "context_id": "stage-1",
  "bindings": {"NEXT": {"kind": "NEXT"}},
  "frames": [
    {"frame_id": 1, "timestamp": 0.00, "label": "NEUTRAL", "accepted": true},
    {"frame_id": 2, "timestamp": 0.15, "label": "NEUTRAL", "accepted": true},
    {"frame_id": 3, "timestamp": 0.31, "label": "NEUTRAL", "accepted": true},
    {"frame_id": 4, "timestamp": 0.45, "label": "NEXT", "accepted": true},
    {"frame_id": 5, "timestamp": 0.60, "label": "NEXT", "accepted": true},
    {"frame_id": 6, "timestamp": 0.75, "label": "NEXT", "accepted": true},
    {"frame_id": 7, "timestamp": 0.90, "label": "NEXT", "accepted": true}
  ],
  "expected_holds": [
    {"start": 0.45, "end": 0.90, "command": "NEXT"}
  ]
}
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import sys
from tempfile import NamedTemporaryFile
from typing import Any, cast

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gestureforge.contracts import (  # noqa: E402
    Action,
    ActionType,
    Prediction,
    validate_identifier,
    validate_gesture_id,
)
from gestureforge.controller import (  # noqa: E402
    CLASSIFIER_REJECTION_GRACE_SECONDS,
    COMMAND_HOLD_SECONDS,
    MAX_FRAME_GAP_SECONDS,
    MAX_PREDICTION_AGE_SECONDS,
    NEUTRAL_HOLD_SECONDS,
)
from gestureforge.routing import RoutingMode, RoutingSession  # noqa: E402

SCHEMA_VERSION = 1


def load_trace(path: Path) -> dict[str, Any]:
    raw_bytes = path.read_bytes()
    raw_text = raw_bytes.decode("utf-8")
    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("trace must be a JSON object")
    if "annotation_complete" in data and data["annotation_complete"] is not True:
        raise ValueError("Annotate expected_holds and set annotation_complete to true before scoring")
    schema_version = data.get("schema_version")
    _require(
        isinstance(schema_version, int) and not isinstance(schema_version, bool)
        and schema_version == SCHEMA_VERSION,
        "schema_version must be 1",
    )
    for key in ("session_id", "profile_id", "model_version", "context_id"):
        value = data.get(key)
        _require(isinstance(value, str), f"{key} is required")
        value = cast(str, value)
        validate_identifier(value)
    frames = data.get("frames")
    holds = data.get("expected_holds")
    _require(isinstance(frames, list) and len(frames) > 0, "frames must be a non-empty list")
    _require(isinstance(holds, list), "expected_holds must be a list")
    bindings = _parse_bindings(data.get("bindings"))
    data["bindings"] = bindings
    data["frames"], data["received_at_assumed"] = _parse_frames(cast(list[Any], frames), data)
    data["expected_holds"] = _parse_holds(cast(list[Any], holds), bindings, data["frames"])
    data["trace_sha256"] = hashlib.sha256(raw_bytes).hexdigest()
    return data


def replay(trace: dict[str, Any]) -> dict[str, Any]:
    frames: list[tuple[Prediction, float]] = trace["frames"]
    holds: list[dict[str, Any]] = trace["expected_holds"]
    bindings: dict[str, Action] = trace["bindings"]
    protected = _protected_events(trace, frames, bindings)
    baseline = _baseline_events(frames, bindings)
    conditions = {
        "protected": _summarise(protected, holds),
        "baseline": _summarise(baseline, holds),
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "input": {
            "session_id": trace["session_id"],
            "profile_id": trace["profile_id"],
            "model_version": trace["model_version"],
            "context_id": trace["context_id"],
            "frame_count": len(frames),
            "expected_hold_count": len(holds),
            "received_at_assumed_from_timestamp": trace["received_at_assumed"],
            "trace_sha256": trace["trace_sha256"],
            "controller_timing_seconds": {
                "neutral_hold": NEUTRAL_HOLD_SECONDS,
                "command_hold": COMMAND_HOLD_SECONDS,
                "max_prediction_age": MAX_PREDICTION_AGE_SECONDS,
                "max_frame_gap": MAX_FRAME_GAP_SECONDS,
                "classifier_rejection_grace": CLASSIFIER_REJECTION_GRACE_SECONDS,
            },
        },
        "conditions": conditions,
        "limitations": [
            "Replay uses saved prediction labels only; it does not claim live participant performance.",
            "Baseline is a naive per-frame ablation: one would-be action per accepted mapped frame.",
            "Latency is annotated hold start to simulated action request, not camera-to-OS end-to-end time.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--trace", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        _require(not _same_path_or_file(args.trace, args.output), "output must not overwrite input trace")
        trace = load_trace(args.trace)
        result = replay(trace)
        _write_json_atomic(args.output, result)
    except (ValueError, OSError) as exc:
        raise SystemExit(f"replay_controller: {exc}") from exc
    return 0


def _parse_bindings(raw: Any) -> dict[str, Action]:
    _require(isinstance(raw, dict) and len(raw) > 0, "bindings must be a non-empty object")
    raw = cast(dict[Any, Any], raw)
    _require(len(raw) <= 3, "bindings may contain at most three gestures")
    bindings: dict[str, Action] = {}
    for gesture, value in raw.items():
        validate_gesture_id(gesture)
        _require(isinstance(value, dict), f"binding {gesture} must be an object")
        _require(set(value) <= {"kind", "shortcut_id"}, f"binding {gesture} has unknown fields")
        kind = value.get("kind")
        _require(isinstance(kind, str), f"binding {gesture} requires kind")
        try:
            action_type = ActionType(kind)
        except ValueError as exc:
            raise ValueError(f"binding {gesture} has unsupported action kind") from exc
        shortcut_id = value.get("shortcut_id")
        _require(shortcut_id is None or isinstance(shortcut_id, str), "shortcut_id must be a string")
        bindings[gesture] = Action(action_type, shortcut_id)
    return bindings


def _parse_frames(raw_frames: list[Any], trace: dict[str, Any]) -> tuple[list[tuple[Prediction, float]], bool]:
    predictions: list[tuple[Prediction, float]] = []
    previous_frame = -1
    previous_time: float | None = None
    previous_received: float | None = None
    received_at_assumed = False
    for index, raw in enumerate(raw_frames):
        _require(isinstance(raw, dict), f"frame {index} must be an object")
        _require(
            set(raw) <= {"frame_id", "timestamp", "received_at", "label", "accepted", "rejection_reason"},
            f"frame {index} has unknown fields",
        )
        frame_id = raw.get("frame_id")
        timestamp = raw.get("timestamp")
        received_at = raw.get("received_at", timestamp)
        label = raw.get("label")
        accepted = raw.get("accepted")
        reason = raw.get("rejection_reason", "")
        _require(isinstance(frame_id, int) and not isinstance(frame_id, bool), "frame_id must be an int")
        _require(frame_id > previous_frame, "frame_id values must strictly increase")
        _require(_finite_number(timestamp), "timestamp must be finite")
        timestamp = float(timestamp)
        _require(_finite_number(received_at), "received_at must be finite")
        received_at = float(received_at)
        _require(previous_time is None or timestamp > previous_time, "timestamps must strictly increase")
        _require(received_at >= timestamp, "received_at must be greater than or equal to timestamp")
        _require(
            previous_received is None or received_at > previous_received,
            "received_at values must strictly increase",
        )
        _require(isinstance(label, str) and len(label) > 0, "label is required")
        _require(isinstance(accepted, bool), "accepted must be true or false")
        _require(isinstance(reason, str), "rejection_reason must be a string")
        if accepted:
            _require(reason == "", "accepted frames must not include rejection_reason")
        else:
            _require(reason != "", "rejected frames require rejection_reason")
        predictions.append((
            Prediction(
                trace["session_id"], trace["profile_id"], frame_id, timestamp, label, accepted,
                trace["model_version"], reason,
            ),
            received_at,
        ))
        received_at_assumed = received_at_assumed or "received_at" not in raw
        previous_frame = frame_id
        previous_time = timestamp
        previous_received = received_at
    return predictions, received_at_assumed


def _parse_holds(
    raw_holds: list[Any], bindings: dict[str, Action], frames: list[tuple[Prediction, float]],
) -> list[dict[str, Any]]:
    holds: list[dict[str, Any]] = []
    previous_end: float | None = None
    first_time = frames[0][0].timestamp
    last_time = frames[-1][0].timestamp
    for index, raw in enumerate(raw_holds):
        _require(isinstance(raw, dict), f"expected hold {index} must be an object")
        _require(set(raw) == {"start", "end", "command"}, f"expected hold {index} fields are start/end/command")
        start = raw["start"]
        end = raw["end"]
        command = raw["command"]
        _require(_finite_number(start) and _finite_number(end), "hold times must be finite")
        start = float(start)
        end = float(end)
        _require(start < end, "hold start must be before end")
        _require(first_time <= start and end <= last_time, "expected holds must lie within trace timestamps")
        _require(
            any(start <= prediction.timestamp <= end for prediction, _ in frames),
            "expected holds must contain at least one frame",
        )
        _require(previous_end is None or start > previous_end, "expected holds must not overlap")
        _require(isinstance(command, str), "hold command must be a string")
        _require(command in bindings, "hold command must be a configured binding")
        holds.append({"start": start, "end": end, "command": command})
        previous_end = end
    return holds


def _protected_events(
    trace: dict[str, Any], frames: list[tuple[Prediction, float]], bindings: dict[str, Action],
) -> list[dict[str, Any]]:
    session = RoutingSession(
        trace["profile_id"], trace["model_version"], trace["context_id"], bindings, RoutingMode.REHEARSAL,
    )
    snapshot = session.resume()
    events: list[dict[str, Any]] = []
    for frame, received_at in frames:
        prediction = Prediction(
            snapshot.session_id, snapshot.profile_id, frame.frame_id, frame.timestamp, frame.label,
            frame.accepted, snapshot.model_version, frame.rejection_reason,
        )
        event = session.process(prediction, received_at)
        if event is None:
            continue
        result = session.route(event, received_at)
        if result.simulated_action is not None:
            event_id = f"protected:{len(events) + 1}"
            events.append(_event_row(event_id, event.frame_id, event.timestamp, event.command,
                                     result.simulated_action))
    return events


def _baseline_events(frames: list[tuple[Prediction, float]], bindings: dict[str, Action]) -> list[dict[str, Any]]:
    return [
        _event_row(f"baseline:{frame.frame_id}", frame.frame_id, received_at, frame.label,
                   bindings[frame.label])
        for frame, received_at in frames
        if frame.accepted and frame.label in bindings
    ]


def _event_row(event_id: str, frame_id: int, timestamp: float, command: str, action: Action) -> dict[str, Any]:
    return {
        "event_id": event_id,
        "frame_id": frame_id,
        "timestamp": timestamp,
        "command": command,
        "action": {"kind": action.kind.value, "shortcut_id": action.shortcut_id},
    }


def _summarise(events: list[dict[str, Any]], holds: list[dict[str, Any]]) -> dict[str, Any]:
    matched: set[int] = set()
    duplicate = 0
    unintended = 0
    latencies = []
    hold_hits = [0 for _ in holds]
    for event in events:
        hit = _matching_hold(event, holds)
        if hit is None:
            unintended += 1
            continue
        hold_hits[hit] += 1
        if hold_hits[hit] == 1:
            matched.add(hit)
            latencies.append(round(event["timestamp"] - holds[hit]["start"], 6))
        else:
            duplicate += 1
    return {
        "actions": len(events),
        "correct": len(matched),
        "missed": len(holds) - len(matched),
        "duplicate": duplicate,
        "unintended": unintended,
        "latencies_seconds": latencies,
        "latency_p95_seconds": _percentile95(latencies) if latencies else None,
        "events": events,
    }


def _matching_hold(event: dict[str, Any], holds: list[dict[str, Any]]) -> int | None:
    for index, hold in enumerate(holds):
        if hold["command"] == event["command"] and hold["start"] <= event["timestamp"] <= hold["end"]:
            return index
    return None


def _percentile95(values: list[float]) -> float:
    ordered = sorted(values)
    rank = math.ceil(0.95 * len(ordered)) - 1
    return ordered[max(0, min(rank, len(ordered) - 1))]


def _write_json_atomic(path: Path, data: dict[str, Any]) -> None:
    _require(not path.exists(), "output already exists; choose a new report filename")
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(data, indent=2, sort_keys=True) + "\n"
    with NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        temp = Path(handle.name)
        handle.write(text)
    try:
        # Publish the completed file exclusively, including if another writer raced us.
        os.link(temp, path)
    finally:
        temp.unlink(missing_ok=True)


def _finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _same_path_or_file(left: Path, right: Path) -> bool:
    if left.resolve() == right.resolve():
        return True
    try:
        return left.samefile(right)
    except FileNotFoundError:
        return False


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


if __name__ == "__main__":
    raise SystemExit(main())
