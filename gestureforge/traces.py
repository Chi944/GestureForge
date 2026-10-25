"""Local prediction traces for controller replay evidence."""

from __future__ import annotations

import json
import math
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

from .contracts import Prediction, RoutingMode, RoutingSnapshot

SCHEMA_VERSION = 1
# Ten minutes at the 30 ms UI poll interval plus preparation headroom.
MAX_TRACE_FRAMES = 24000


class EvaluationTrace:
    """Bounded label/timing recorder; never stores frames, landmarks or features."""

    def __init__(self, snapshot: RoutingSnapshot, *, max_frames: int = MAX_TRACE_FRAMES,
                 recognition_config: dict[str, Any] | None = None,
                 camera_index: int | None = None, chosen_hand: str | None = None) -> None:
        if not isinstance(max_frames, int) or isinstance(max_frames, bool) or max_frames <= 0:
            raise ValueError("max_frames must be positive")
        self._recognition: dict[str, Any] | None = None
        if recognition_config is not None:
            if snapshot.mode not in (RoutingMode.PREVIEW, RoutingMode.REHEARSAL):
                raise ValueError("recognition diagnostics require Preview or Rehearsal")
            if set(recognition_config) != {"algorithm", "multiplier", "margin"}:
                raise ValueError("invalid recognition configuration fields")
            if recognition_config["algorithm"] not in ("knn", "svm") or any(
                not _finite(recognition_config[key]) for key in ("multiplier", "margin")
            ) or recognition_config["multiplier"] <= 0 or recognition_config["margin"] < 1:
                raise ValueError("invalid recognition configuration values")
            self._recognition = {"schema_version": 1, "config": dict(recognition_config),
                                 "mode": snapshot.mode.value, "frames": []}
            if camera_index is not None or chosen_hand is not None:
                if (not isinstance(camera_index, int) or isinstance(camera_index, bool)
                        or camera_index < 0 or chosen_hand not in ("Right", "Left")):
                    raise ValueError("invalid recognition capture context")
                self._recognition["capture"] = {"camera_index": camera_index, "chosen_hand": chosen_hand}
        self._snapshot = snapshot
        self._max_frames = max_frames
        self._frames: list[dict[str, Any]] = []
        self._previous_frame = -1
        self._previous_timestamp: float | None = None
        self._previous_received: float | None = None

    @property
    def frame_count(self) -> int:
        return len(self._frames)

    def append(self, prediction: Prediction, received_at: float,
               diagnostics: dict[str, float | None] | None = None) -> None:
        if prediction.session_id != self._snapshot.session_id:
            raise ValueError("prediction session does not match trace session")
        if prediction.profile_id != self._snapshot.profile_id:
            raise ValueError("prediction profile does not match trace profile")
        if prediction.model_version != self._snapshot.model_version:
            raise ValueError("prediction model does not match trace model")
        if len(self._frames) >= self._max_frames:
            raise OverflowError("evaluation trace frame limit reached")
        if not _finite(prediction.timestamp) or not _finite(received_at):
            raise ValueError("timestamps must be finite")
        if not isinstance(prediction.frame_id, int) or isinstance(prediction.frame_id, bool):
            raise ValueError("frame_id must be an int")
        if prediction.frame_id <= self._previous_frame:
            raise ValueError("frame IDs must strictly increase")
        if self._previous_timestamp is not None and prediction.timestamp <= self._previous_timestamp:
            raise ValueError("prediction timestamps must strictly increase")
        if received_at < prediction.timestamp:
            raise ValueError("received_at must be greater than or equal to timestamp")
        if self._previous_received is not None and received_at <= self._previous_received:
            raise ValueError("received_at values must strictly increase")
        if not isinstance(prediction.label, str) or not prediction.label:
            raise ValueError("label is required")
        if not isinstance(prediction.accepted, bool):
            raise ValueError("accepted must be true or false")
        if not isinstance(prediction.rejection_reason, str):
            raise ValueError("rejection_reason must be a string")
        if prediction.accepted and prediction.rejection_reason:
            raise ValueError("accepted predictions must not include rejection_reason")
        if not prediction.accepted and not prediction.rejection_reason:
            raise ValueError("rejected predictions require rejection_reason")

        row: dict[str, Any] = {
            "frame_id": prediction.frame_id,
            "timestamp": prediction.timestamp,
            "received_at": received_at,
            "label": prediction.label,
            "accepted": prediction.accepted,
        }
        if prediction.rejection_reason:
            row["rejection_reason"] = prediction.rejection_reason
        if diagnostics is not None:
            if self._recognition is None:
                raise ValueError("recognition diagnostics were not enabled")
            if set(diagnostics) != {"distance", "threshold", "competitor_distance", "competitor_ratio"}:
                raise ValueError("invalid recognition diagnostic fields")
            if any(value is not None and (not _finite(value) or value < 0)
                   for value in diagnostics.values()):
                raise ValueError("recognition diagnostics must be finite nonnegative values or null")
        if self._recognition is not None:
            self._recognition["frames"].append({"frame_id": prediction.frame_id,
                                                "decision": None if diagnostics is None else dict(diagnostics)})
        self._frames.append(row)
        self._previous_frame = prediction.frame_id
        self._previous_timestamp = prediction.timestamp
        self._previous_received = received_at

    def save(self, path: Path) -> None:
        if not self._frames:
            raise ValueError("cannot save an empty evaluation trace")
        _write_json_exclusive(path, {
            "schema_version": SCHEMA_VERSION,
            "session_id": self._snapshot.session_id,
            "profile_id": self._snapshot.profile_id,
            "model_version": self._snapshot.model_version,
            "context_id": self._snapshot.context_id,
            "bindings": {
                gesture: {"kind": action.kind.value, "shortcut_id": action.shortcut_id}
                for gesture, action in self._snapshot.bindings
            },
            "frames": self._frames,
            "expected_holds": [],
            "annotation_complete": False,
            **({"recognition_diagnostics": self._recognition} if self._recognition is not None else {}),
            "metadata": {
                "source": "GestureForge Studio UI/controller-consumed predictions",
                "contents": "labels, acceptance state and monotonic timing"
                + ("; opted-in numeric decision diagnostics" if self._recognition is not None else ""),
            },
        })


def _write_json_exclusive(path: Path, data: dict[str, Any]) -> None:
    if path.exists():
        raise ValueError("output already exists; choose a new trace filename")
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(data, indent=2, sort_keys=True) + "\n"
    with NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        temp = Path(handle.name)
    try:
        temp.write_text(text, encoding="utf-8")
        os.link(temp, path)
    finally:
        temp.unlink(missing_ok=True)


def _finite(value: float) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)
