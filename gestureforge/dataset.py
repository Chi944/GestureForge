"""Dataset manifest and numeric feature persistence for GestureForge.

The persisted assignment format deliberately stores JSON records and numeric
NumPy arrays, not pickle/joblib model objects. This keeps collection data
reviewable and avoids executable model files in the submitted prototype.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Iterable
from uuid import uuid4

import numpy as np

from .contracts import FEATURE_VERSION, LABELS, SCHEMA_VERSION

UNKNOWN_LABEL = "UNKNOWN"
TRAIN_SPLIT = "train"
VALIDATION_SPLIT = "validation"
VALIDATION_NEGATIVE_SPLIT = "validation_negative"


@dataclass(frozen=True)
class SampleRecord:
    participant_id: str
    session_id: str
    trial_id: str
    intended_label: str
    split: str
    sample_index: int
    timestamp: float
    valid: bool
    feature_index: int | None = None
    validity_reason: str = ""
    hand: str | None = None
    provenance: str = "human"

    @classmethod
    def from_mapping(cls, value: dict[str, Any]) -> "SampleRecord":
        return cls(
            participant_id=_strict_str(value, "participant_id"),
            session_id=_strict_str(value, "session_id"),
            trial_id=_strict_str(value, "trial_id"),
            intended_label=_strict_str(value, "intended_label"),
            split=_strict_str(value, "split"),
            sample_index=_strict_int(value, "sample_index"),
            timestamp=_strict_number(value, "timestamp"),
            valid=_strict_bool(value, "valid"),
            feature_index=_optional_strict_int(value, "feature_index"),
            validity_reason=_optional_strict_str(value, "validity_reason", "") or "",
            hand=_optional_strict_str(value, "hand", None),
            provenance=_optional_strict_str(value, "provenance", "human") or "human",
        )


@dataclass(frozen=True)
class DatasetBundle:
    manifest_path: Path | None
    records: tuple[SampleRecord, ...]
    features: np.ndarray
    metadata: dict[str, Any]

    @property
    def labels(self) -> np.ndarray:
        return np.asarray([record.intended_label for record in self.valid_records()], dtype=object)

    def valid_records(self, split: str | None = None) -> tuple[SampleRecord, ...]:
        return tuple(
            record
            for record in self.records
            if record.valid and record.feature_index is not None and (split is None or record.split == split)
        )

    def split_data(self, split: str) -> tuple[np.ndarray, np.ndarray, tuple[SampleRecord, ...]]:
        records = self.valid_records(split)
        indices = [record.feature_index for record in records]
        features = self.features[np.asarray(indices, dtype=int)] if indices else np.empty((0, 60))
        labels = np.asarray([record.intended_label for record in records], dtype=object)
        return features, labels, records

    def training_data(self) -> tuple[np.ndarray, np.ndarray, tuple[SampleRecord, ...]]:
        return self.split_data(TRAIN_SPLIT)

    def validation_data(self) -> tuple[np.ndarray, np.ndarray, tuple[SampleRecord, ...]]:
        return self.split_data(VALIDATION_SPLIT)


def append_dataset(
    path: str | Path,
    records: Iterable[SampleRecord | dict[str, Any]],
    features: np.ndarray,
    metadata: dict[str, Any] | None = None,
) -> DatasetBundle:
    """Append a separately collected session to an existing manifest."""

    manifest_path = _manifest_path(path)
    if not manifest_path.exists():
        return save_dataset(manifest_path, records, features, metadata)
    existing = load_dataset(manifest_path)
    incoming = _assign_feature_indices(records, len(_coerce_feature_matrix(features)))
    merged_records, merged_features = _merge_records_and_features(
        [existing.records, incoming], [existing.features, _coerce_feature_matrix(features)]
    )
    merged_metadata = {**existing.metadata, **(metadata or {})}
    return save_dataset(manifest_path, merged_records, merged_features, merged_metadata)


def save_dataset(
    path: str | Path,
    records: Iterable[SampleRecord | dict[str, Any]],
    features: np.ndarray,
    metadata: dict[str, Any] | None = None,
) -> DatasetBundle:
    """Save a JSON manifest and sidecar NPZ feature matrix."""

    manifest_path = _manifest_path(path)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    feature_matrix = _coerce_feature_matrix(features)
    normalised_records = _assign_feature_indices(records, len(feature_matrix))
    _validate_records(normalised_records, len(feature_matrix))

    temp_feature_path = manifest_path.with_name(f".{manifest_path.stem}.{uuid4().hex}.npz")
    np.savez_compressed(temp_feature_path, features=feature_matrix)
    feature_hash = file_sha256(temp_feature_path)
    feature_path = manifest_path.with_name(f"{manifest_path.stem}.features.{feature_hash[:16]}.npz")
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "feature_version": FEATURE_VERSION,
        "labels": list(LABELS),
        "feature_file": feature_path.name,
        "feature_sha256": feature_hash,
        "metadata": metadata or {},
        "records": [asdict(record) for record in normalised_records],
    }
    temp_manifest_path = manifest_path.with_name(f".{manifest_path.name}.{uuid4().hex}.tmp")
    try:
        if feature_path.exists():
            temp_feature_path.unlink()
        else:
            temp_feature_path.replace(feature_path)
        temp_manifest_path.write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        temp_manifest_path.replace(manifest_path)
    finally:
        if temp_feature_path.exists():
            temp_feature_path.unlink()
        if temp_manifest_path.exists():
            temp_manifest_path.unlink()
    return DatasetBundle(
        manifest_path=manifest_path,
        records=tuple(normalised_records),
        features=feature_matrix,
        metadata=metadata or {},
    )


def merge_datasets(bundles: Iterable[DatasetBundle]) -> DatasetBundle:
    bundle_list = list(bundles)
    if not bundle_list:
        raise ValueError("at least one dataset is required")
    merged_records, merged_features = _merge_records_and_features(
        [bundle.records for bundle in bundle_list], [bundle.features for bundle in bundle_list]
    )
    metadata = {
        "sources": [
            None if bundle.manifest_path is None else str(bundle.manifest_path) for bundle in bundle_list
        ],
        "provenance": ",".join(
            sorted({str(bundle.metadata.get("provenance", "unknown")) for bundle in bundle_list})
        ),
    }
    return DatasetBundle(
        manifest_path=None,
        records=merged_records,
        features=merged_features,
        metadata=metadata,
    )


def load_dataset(path: str | Path) -> DatasetBundle:
    """Load a saved GestureForge dataset manifest and feature sidecar."""

    manifest_path = _manifest_path(path)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(f"unsupported dataset schema version {manifest.get('schema_version')}")
    if manifest.get("feature_version") != FEATURE_VERSION:
        raise ValueError(f"unsupported feature version {manifest.get('feature_version')}")

    feature_path = manifest_path.with_name(str(manifest["feature_file"]))
    expected_hash = str(manifest["feature_sha256"])
    actual_hash = file_sha256(feature_path)
    if actual_hash != expected_hash:
        raise ValueError("feature sidecar hash mismatch")

    with np.load(feature_path) as loaded:
        features = _coerce_feature_matrix(loaded["features"])
    records = tuple(SampleRecord.from_mapping(record) for record in manifest["records"])
    _validate_records(records, len(features))
    return DatasetBundle(
        manifest_path=manifest_path,
        records=records,
        features=features,
        metadata=dict(manifest.get("metadata", {})),
    )


def dataset_hashes(bundle: DatasetBundle) -> dict[str, str]:
    if bundle.manifest_path is None:
        payload = json.dumps([asdict(record) for record in bundle.records], sort_keys=True).encode("utf-8")
        return {
            "manifest_sha256": sha256(payload).hexdigest(),
            "features_sha256": sha256(bundle.features.tobytes()).hexdigest(),
        }
    manifest = json.loads(bundle.manifest_path.read_text(encoding="utf-8"))
    feature_file = bundle.manifest_path.with_name(str(manifest["feature_file"]))
    return {
        "manifest_sha256": file_sha256(bundle.manifest_path),
        "features_sha256": file_sha256(feature_file),
    }


def file_sha256(path: str | Path) -> str:
    digest = sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _manifest_path(path: str | Path) -> Path:
    result = Path(path)
    if result.suffix.lower() != ".json":
        result = result / "manifest.json"
    return result


def _coerce_feature_matrix(features: np.ndarray) -> np.ndarray:
    matrix = np.asarray(features, dtype=np.float32)
    if matrix.ndim != 2 or matrix.shape[1] != 60:
        raise ValueError(f"expected feature matrix shape (n, 60), got {matrix.shape}")
    if not np.all(np.isfinite(matrix)):
        raise ValueError("feature matrix contains non-finite values")
    return matrix


def _assign_feature_indices(
    records: Iterable[SampleRecord | dict[str, Any]], feature_count: int
) -> tuple[SampleRecord, ...]:
    next_feature_index = 0
    assigned: list[SampleRecord] = []
    for value in records:
        record = value if isinstance(value, SampleRecord) else SampleRecord.from_mapping(value)
        if record.valid and record.feature_index is None:
            if next_feature_index >= feature_count:
                raise ValueError("more valid records than feature rows")
            record = SampleRecord(**{**asdict(record), "feature_index": next_feature_index})
            next_feature_index += 1
        elif record.valid and record.feature_index is not None:
            next_feature_index = max(next_feature_index, record.feature_index + 1)
        assigned.append(record)
    return tuple(assigned)


def _validate_records(records: Iterable[SampleRecord], feature_count: int) -> None:
    feature_indices: set[int] = set()
    feature_split_by_index: dict[int, str] = {}
    session_splits: dict[str, str] = {}
    seen_trial_splits: dict[str, str] = {}
    trial_identity: dict[str, tuple[str, str, str, str]] = {}
    trial_slots: dict[str, set[int]] = {}
    hands: set[str] = set()
    for record in records:
        if record.intended_label not in LABELS and not (
            record.split == VALIDATION_NEGATIVE_SPLIT and record.intended_label == UNKNOWN_LABEL
        ):
            raise ValueError(f"unknown intended label {record.intended_label}")
        if record.split not in {TRAIN_SPLIT, VALIDATION_SPLIT, VALIDATION_NEGATIVE_SPLIT, "test"}:
            raise ValueError(f"unknown split {record.split}")
        previous_session_split = session_splits.setdefault(record.session_id, record.split)
        if previous_session_split != record.split:
            raise ValueError(f"session {record.session_id} appears in multiple splits")
        previous_split = seen_trial_splits.setdefault(record.trial_id, record.split)
        if previous_split != record.split:
            raise ValueError(f"trial {record.trial_id} appears in multiple splits")
        identity = (
            record.participant_id,
            record.session_id,
            record.intended_label,
            record.split,
        )
        previous_identity = trial_identity.setdefault(record.trial_id, identity)
        if previous_identity != identity:
            raise ValueError(f"trial {record.trial_id} has inconsistent participant/session/label/split")
        if record.valid:
            if not record.hand:
                raise ValueError("valid records must include the chosen hand")
            if type(record.hand) is not str:
                raise ValueError("record hand must be a string")
            hands.add(record.hand)
            if record.feature_index is None:
                raise ValueError("valid record missing feature_index")
            if record.feature_index < 0 or record.feature_index >= feature_count:
                raise ValueError("feature_index outside feature matrix")
            if record.feature_index in feature_indices:
                raise ValueError(f"feature_index {record.feature_index} is used by multiple records")
            feature_indices.add(record.feature_index)
            previous_feature_split = feature_split_by_index.setdefault(record.feature_index, record.split)
            if previous_feature_split != record.split:
                raise ValueError(f"feature_index {record.feature_index} appears in multiple splits")
        elif record.feature_index is not None:
            raise ValueError("invalid record must not point at a feature row")
        if record.sample_index < 0 or record.sample_index > 4:
            raise ValueError(f"sample_index must be in the planned 0..4 slots, got {record.sample_index}")
        slots = trial_slots.setdefault(record.trial_id, set())
        if record.sample_index in slots:
            raise ValueError(f"duplicate sample_index {record.sample_index} in trial {record.trial_id}")
        slots.add(record.sample_index)
    if len(hands) > 1:
        raise ValueError(f"dataset must contain one chosen hand, got {sorted(hands)}")


def _merge_records_and_features(
    record_groups: list[tuple[SampleRecord, ...]],
    feature_groups: list[np.ndarray],
) -> tuple[tuple[SampleRecord, ...], np.ndarray]:
    merged_features: list[np.ndarray] = []
    merged_records: list[SampleRecord] = []
    feature_offset = 0
    seen_trials: set[str] = set()
    for records, features in zip(record_groups, feature_groups, strict=True):
        features = _coerce_feature_matrix(features)
        for record in records:
            if record.trial_id in seen_trials:
                raise ValueError(f"trial {record.trial_id} would be overwritten by merge")
            if record.valid and record.feature_index is not None:
                values = asdict(record)
                values["feature_index"] = record.feature_index + feature_offset
                merged_records.append(SampleRecord(**values))
            else:
                merged_records.append(record)
        seen_trials.update(record.trial_id for record in records)
        merged_features.append(features)
        feature_offset += len(features)
    feature_matrix = (
        np.vstack(merged_features).astype(np.float32)
        if merged_features
        else np.empty((0, 60), dtype=np.float32)
    )
    _validate_records(merged_records, len(feature_matrix))
    return tuple(merged_records), feature_matrix


def _strict_str(value: dict[str, Any], key: str) -> str:
    item = value[key]
    if type(item) is not str:
        raise ValueError(f"{key} must be a string")
    return item


def _optional_strict_str(value: dict[str, Any], key: str, default: str | None) -> str | None:
    item = value.get(key, default)
    if item is None:
        return None
    if type(item) is not str:
        raise ValueError(f"{key} must be a string or null")
    return item


def _strict_int(value: dict[str, Any], key: str) -> int:
    item = value[key]
    if type(item) is not int:
        raise ValueError(f"{key} must be an integer")
    return item


def _optional_strict_int(value: dict[str, Any], key: str) -> int | None:
    item = value.get(key)
    if item is None:
        return None
    if type(item) is not int:
        raise ValueError(f"{key} must be an integer or null")
    return item


def _strict_bool(value: dict[str, Any], key: str) -> bool:
    item = value[key]
    if type(item) is not bool:
        raise ValueError(f"{key} must be a boolean")
    return item


def _strict_number(value: dict[str, Any], key: str) -> float:
    item = value[key]
    if type(item) not in {int, float}:
        raise ValueError(f"{key} must be a number")
    return float(item)
