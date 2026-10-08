"""Import browser participant collections into the standard dataset format."""

from __future__ import annotations

import argparse
from datetime import datetime
import json
import math
from pathlib import Path
from typing import Any
import zipfile

import numpy as np

from .contracts import LABELS, Observation, validate_identifier
from .dataset import (
    UNKNOWN_LABEL,
    VALIDATION_NEGATIVE_SPLIT,
    VALIDATION_SPLIT,
    TRAIN_SPLIT,
    SampleRecord,
    save_dataset,
)
from .features import LANDMARK_COUNT, extract_feature_result

PROTOCOL = "gestureforge-browser-development-v1"
RUNTIME = "mediapipe-tasks-vision-web"
RUNTIME_VERSION = "1.1.0"
MODEL_SHA256 = "fbc2a30080c3c557093b5ddfc334698132eb341044ccee322ccf8bcf3607cde1"
RETENTION = "Delete after marking and appeals finish; team and private marker access only"
MAX_ZIP_BYTES = 10 * 1024 * 1024
MAX_RECORDS = 520
COLLECTION_ENTRY = "collection.json"
POSITIVE_SPLITS = {TRAIN_SPLIT, VALIDATION_SPLIT}
ALLOWED_SPLITS = {*POSITIVE_SPLITS, VALIDATION_NEGATIVE_SPLIT}
EXPECTED_COUNTS = {
    TRAIN_SPLIT: {label: 12 for label in LABELS},
    VALIDATION_SPLIT: {label: 12 for label in LABELS},
    VALIDATION_NEGATIVE_SPLIT: {UNKNOWN_LABEL: 8},
}


def import_browser_zip(zip_path: str | Path, output: str | Path):
    output_path = _manifest_path(output)
    if output_path.exists():
        raise ValueError(f"output already exists: {output_path}")
    payload = _load_collection(zip_path)
    records, features, metadata = _convert_collection(payload, Path(zip_path))
    return save_dataset(output_path, records, np.asarray(features, dtype=np.float32).reshape(-1, 60), metadata)


def _load_collection(zip_path: str | Path) -> dict[str, Any]:
    path = Path(zip_path)
    if path.stat().st_size > MAX_ZIP_BYTES:
        raise ValueError("participant zip is larger than 10 MB")
    with zipfile.ZipFile(path) as archive:
        infos = archive.infolist()
        names = [info.filename for info in infos]
        if names != [COLLECTION_ENTRY]:
            raise ValueError("participant zip must contain only collection.json")
        info = infos[0]
        if info.flag_bits & 0x1:
            raise ValueError("encrypted participant zips are not accepted")
        if info.file_size > MAX_ZIP_BYTES or info.compress_size > MAX_ZIP_BYTES:
            raise ValueError("collection.json is larger than 10 MB")
        with archive.open(info) as handle:
            data = handle.read(MAX_ZIP_BYTES + 1)
    if len(data) > MAX_ZIP_BYTES:
        raise ValueError("collection.json is larger than 10 MB")
    payload = json.loads(data.decode("utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("collection.json must contain an object")
    return payload


def _convert_collection(payload: dict[str, Any], zip_path: Path) -> tuple[list[SampleRecord], list[np.ndarray], dict[str, Any]]:
    _require_exact_keys(payload, {
        "schema_version", "protocol", "participant_id", "hand", "source", "consent", "sessions", "records",
    }, "collection")
    if type(payload["schema_version"]) is not int or payload["schema_version"] != 1:
        raise ValueError("unsupported collection schema_version")
    if payload["protocol"] != PROTOCOL:
        raise ValueError("unsupported collection protocol")
    participant_id = _strict_str(payload, "participant_id")
    validate_identifier(participant_id)
    hand = _strict_str(payload, "hand")
    if hand != "Right":
        raise ValueError("participant kit currently imports Right-hand collections only")
    _validate_source(payload["source"])
    _validate_consent(payload["consent"])
    session_splits, sessions = _validate_sessions(payload["sessions"])
    if not isinstance(payload["records"], list) or not 1 <= len(payload["records"]) <= MAX_RECORDS:
        raise ValueError("records must be a non-empty array with at most 520 samples")

    records: list[SampleRecord] = []
    features: list[np.ndarray] = []
    trial_slots: dict[str, set[int]] = {}
    trial_identity: dict[str, tuple[str, str, str]] = {}
    session_last_timestamp: dict[str, float] = {}
    session_frames: dict[str, set[int]] = {}
    counts: dict[str, dict[str, int]] = {split: {} for split in ALLOWED_SPLITS}

    for item in payload["records"]:
        record, feature = _convert_record(item, participant_id, hand, session_splits)
        previous_timestamp = session_last_timestamp.get(record.session_id)
        if previous_timestamp is not None and record.timestamp < previous_timestamp:
            raise ValueError(f"timestamps decrease in session {record.session_id}")
        session_last_timestamp[record.session_id] = record.timestamp
        frame_id = _optional_int(item, "frame_id")
        if frame_id is not None:
            frames = session_frames.setdefault(record.session_id, set())
            if frame_id in frames:
                raise ValueError(f"frame_id {frame_id} is reused in session {record.session_id}")
            frames.add(frame_id)
        identity = (record.session_id, record.intended_label, record.split)
        previous_identity = trial_identity.setdefault(record.trial_id, identity)
        if previous_identity != identity:
            raise ValueError(f"trial {record.trial_id} has inconsistent session, label or split")
        slots = trial_slots.setdefault(record.trial_id, set())
        if record.sample_index in slots:
            raise ValueError(f"duplicate sample_index {record.sample_index} in trial {record.trial_id}")
        slots.add(record.sample_index)
        records.append(record)
        if feature is not None:
            features.append(feature)

    for trial_id, slots in trial_slots.items():
        if slots != {0, 1, 2, 3, 4}:
            raise ValueError(f"trial {trial_id} must contain exactly five scheduled samples")
    for trial_id, (session_id, label, split) in trial_identity.items():
        counts[split][label] = counts[split].get(label, 0) + 1
        if session_splits[session_id] != split:
            raise ValueError(f"trial {trial_id} split does not match its session")
    _validate_split_shape(counts, session_splits)
    completeness = _completeness(counts)
    metadata = {
        "provenance": "human",
        "chosen_hand": hand,
        "pose_set_id": "standard-v1",
        "import_source": "browser-participant-kit",
        "source_zip": str(zip_path),
        "source_sha256": _file_sha256(zip_path),
        "browser_collection": {
            "protocol": PROTOCOL,
            "source": payload["source"],
            "consent": payload["consent"],
            "sessions": sessions,
            "complete": completeness["complete"],
            "counts": completeness["counts"],
            "expected_counts": EXPECTED_COUNTS,
            "import_status": "complete" if completeness["complete"] else "partial",
            "feature_note": (
                "Browser MediaPipe world landmarks were normalised with the native GestureForge "
                "feature extractor; no browser/native equivalence claim is made."
            ),
        },
    }
    return records, features, metadata


def _convert_record(
    item: Any, participant_id: str, chosen_hand: str, session_splits: dict[str, str]
) -> tuple[SampleRecord, np.ndarray | None]:
    if not isinstance(item, dict):
        raise ValueError("each record must be an object")
    _require_exact_keys(item, {
        "session_id", "trial_id", "intended_label", "split", "sample_index", "timestamp", "frame_id",
        "hand_count", "hand", "landmarks", "validity_reason",
    }, "record")
    session_id = _strict_str(item, "session_id")
    validate_identifier(session_id)
    if session_id not in session_splits:
        raise ValueError(f"record references unknown session {session_id}")
    split = _strict_str(item, "split")
    if split != session_splits[session_id]:
        raise ValueError(f"record split does not match session {session_id}")
    trial_id = _strict_str(item, "trial_id")
    validate_identifier(trial_id)
    label = _strict_str(item, "intended_label")
    if split in POSITIVE_SPLITS and label not in LABELS:
        raise ValueError(f"unknown intended label {label}")
    if split == VALIDATION_NEGATIVE_SPLIT and label != UNKNOWN_LABEL:
        raise ValueError("validation_negative records must use UNKNOWN")
    sample_index = _strict_int(item, "sample_index")
    if sample_index not in {0, 1, 2, 3, 4}:
        raise ValueError("sample_index must be 0..4")
    timestamp = _strict_number(item, "timestamp")
    if timestamp < 0:
        raise ValueError("timestamp must be non-negative")
    hand_count = _strict_int(item, "hand_count")
    if hand_count < 0 or hand_count > 2:
        raise ValueError("hand_count must be between 0 and 2")
    detected_hand = _optional_str(item, "hand")
    landmarks = item["landmarks"]
    if landmarks is not None:
        _validate_landmarks(landmarks)
    frame_id = _optional_int(item, "frame_id")
    if frame_id is not None and frame_id < 0:
        raise ValueError("frame_id must be non-negative when present")
    observation = Observation(
        session_id=session_id,
        profile_id=participant_id,
        frame_id=-1 if frame_id is None else frame_id,
        timestamp=timestamp,
        hand_count=hand_count,
        handedness=detected_hand,
        landmarks=landmarks,
        validity_reason=_strict_str(item, "validity_reason"),
    )
    result = extract_feature_result(observation, chosen_hand)
    valid = result.valid
    if valid and frame_id is None:
        raise ValueError("valid observations must include a frame_id")
    reason = "" if valid else (result.reason or observation.validity_reason or "invalid observation")
    feature = result.feature if valid else None
    return (
        SampleRecord(
            participant_id=participant_id,
            session_id=session_id,
            trial_id=trial_id,
            intended_label=label,
            split=split,
            sample_index=sample_index,
            timestamp=timestamp,
            valid=valid,
            validity_reason=reason,
            hand=chosen_hand if valid else detected_hand,
            provenance="human",
        ),
        feature,
    )


def _manifest_path(path: str | Path) -> Path:
    output_path = Path(path)
    if output_path.suffix.lower() != ".json":
        output_path = output_path / "manifest.json"
    return output_path


def _validate_split_shape(counts: dict[str, dict[str, int]], session_splits: dict[str, str]) -> None:
    present_splits = {split for split, labels in counts.items() if labels}
    if TRAIN_SPLIT in present_splits and VALIDATION_SPLIT in present_splits:
        train_sessions = {session for session, split in session_splits.items() if split == TRAIN_SPLIT}
        val_sessions = {session for session, split in session_splits.items() if split == VALIDATION_SPLIT}
        if not train_sessions.isdisjoint(val_sessions) or not train_sessions or not val_sessions:
            raise ValueError("train and validation must use distinct positive sessions")
    for split in POSITIVE_SPLITS:
        if counts[split] and set(counts[split]) - set(LABELS):
            raise ValueError(f"{split} contains labels outside the legacy vocabulary")
    if counts[VALIDATION_NEGATIVE_SPLIT] and set(counts[VALIDATION_NEGATIVE_SPLIT]) != {UNKNOWN_LABEL}:
        raise ValueError("validation_negative can contain only UNKNOWN trials")
    for split, labels in counts.items():
        expected = EXPECTED_COUNTS[split]
        for label, count in labels.items():
            if count > expected[label]:
                raise ValueError(f"{split} has too many {label} trials")


def _completeness(counts: dict[str, dict[str, int]]) -> dict[str, Any]:
    normalised = {split: dict(sorted(labels.items())) for split, labels in sorted(counts.items()) if labels}
    complete = all(normalised.get(split, {}) == expected for split, expected in EXPECTED_COUNTS.items())
    return {"complete": complete, "counts": normalised}


def _validate_source(value: Any) -> None:
    if not isinstance(value, dict):
        raise ValueError("source must be an object")
    expected = {"runtime": RUNTIME, "version": RUNTIME_VERSION, "model_sha256": MODEL_SHA256}
    if value != expected:
        raise ValueError("collection source does not match the approved browser runtime")


def _validate_consent(value: Any) -> None:
    if not isinstance(value, dict):
        raise ValueError("consent must be an object")
    _require_exact_keys(value, {"numeric_data", "team_and_marker_access", "retention", "recorded_at"}, "consent")
    if value["numeric_data"] is not True or value["team_and_marker_access"] is not True:
        raise ValueError("participant consent must permit numeric data and team/marker access")
    if _strict_str(value, "retention") != RETENTION:
        raise ValueError("consent retention does not match the approved participant-kit wording")
    _parse_iso(_strict_str(value, "recorded_at"), "consent.recorded_at")


def _validate_sessions(value: Any) -> tuple[dict[str, str], list[dict[str, Any]]]:
    if not isinstance(value, list) or not value:
        raise ValueError("sessions must be a non-empty array")
    session_splits: dict[str, str] = {}
    sessions: list[dict[str, Any]] = []
    for item in value:
        if not isinstance(item, dict):
            raise ValueError("each session must be an object")
        _require_exact_keys(item, {"session_id", "split", "started_at", "conditions"}, "session")
        session_id = _strict_str(item, "session_id")
        validate_identifier(session_id)
        if session_id in session_splits:
            raise ValueError(f"duplicate session {session_id}")
        split = _strict_str(item, "split")
        if split not in ALLOWED_SPLITS:
            raise ValueError(f"unsupported session split {split}")
        _parse_iso(_strict_str(item, "started_at"), "session.started_at")
        if not _strict_str(item, "conditions").strip():
            raise ValueError("session conditions must be recorded")
        session_splits[session_id] = split
        sessions.append(dict(item))
    return session_splits, sessions


def _validate_landmarks(value: Any) -> None:
    if not isinstance(value, list) or len(value) != LANDMARK_COUNT:
        raise ValueError("landmarks must be a 21x3 numeric array or null")
    for point in value:
        if not isinstance(point, list) or len(point) != 3:
            raise ValueError("landmarks must be a 21x3 numeric array or null")
        for axis in point:
            if type(axis) not in {int, float} or not math.isfinite(float(axis)):
                raise ValueError("landmarks must contain finite numeric xyz values")


def _require_exact_keys(value: dict[str, Any], keys: set[str], label: str) -> None:
    if set(value) != keys:
        raise ValueError(f"{label} must contain exactly {sorted(keys)}")


def _strict_str(value: dict[str, Any], key: str) -> str:
    item = value[key]
    if type(item) is not str:
        raise ValueError(f"{key} must be a string")
    return item


def _optional_str(value: dict[str, Any], key: str) -> str | None:
    item = value[key]
    if item is None:
        return None
    if type(item) is not str:
        raise ValueError(f"{key} must be Right, Left or null")
    if item not in {"Right", "Left"}:
        raise ValueError(f"{key} must be Right, Left or null")
    return item


def _strict_int(value: dict[str, Any], key: str) -> int:
    item = value[key]
    if type(item) is not int:
        raise ValueError(f"{key} must be an integer")
    return item


def _optional_int(value: dict[str, Any], key: str) -> int | None:
    item = value[key]
    if item is None:
        return None
    if type(item) is not int:
        raise ValueError(f"{key} must be an integer or null")
    return item


def _strict_number(value: dict[str, Any], key: str) -> float:
    item = value[key]
    if type(item) not in {int, float}:
        raise ValueError(f"{key} must be a number")
    number = float(item)
    if not math.isfinite(number):
        raise ValueError(f"{key} must be finite")
    return number


def _parse_iso(value: str, label: str) -> None:
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"{label} must be ISO datetime text") from exc


def _file_sha256(path: Path) -> str:
    from .dataset import file_sha256

    return file_sha256(path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("zip_path", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        bundle = import_browser_zip(args.zip_path, args.output)
    except (OSError, ValueError, zipfile.BadZipFile, json.JSONDecodeError) as exc:
        parser.exit(1, f"Import failed: {exc}\n")
    status = bundle.metadata["browser_collection"]["import_status"]
    print(f"Imported {len(bundle.records)} records ({len(bundle.features)} valid features), status={status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
