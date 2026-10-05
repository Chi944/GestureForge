"""Reviewed starter release loader.

The checked-in default is disabled until code review pins a licensed descriptor
hash in APPROVED_RELEASE_SHA256. The release stores JSON and NPZ arrays only;
models are always reconstructed locally from reviewed TRAIN rows.
"""

from __future__ import annotations

from hashlib import sha256
import math
from pathlib import Path
from typing import Any
import zipfile

import numpy as np

from .contracts import FEATURE_VERSION, LABELS, validate_identifier
from .dataset import TRAIN_SPLIT, file_sha256, load_dataset
from .models import train_model
from .storage import decode_json, fields, read_json, version
from .vocabulary import LEGACY_VOCABULARY

RELEASE_PATH = Path(__file__).resolve().parent.parent / "assets" / "starter" / "release.json"
APPROVED_RELEASE_SHA256 = ""
MAX_DESCRIPTOR_BYTES = 16 * 1024
MAX_MANIFEST_BYTES = 512 * 1024
MAX_NPZ_EXPANDED_BYTES = 8 * 1024 * 1024


def unavailable_reason() -> str | None:
    if not APPROVED_RELEASE_SHA256:
        return "Standard gestures are unavailable: no approved starter model is supplied."
    if not RELEASE_PATH.exists():
        return "Standard gestures are unavailable: starter model files are missing."
    return None


def load_starter():
    if not APPROVED_RELEASE_SHA256:
        raise ValueError("starter release has no approved pinned descriptor hash")
    descriptor_bytes = _read_bytes(RELEASE_PATH, MAX_DESCRIPTOR_BYTES, "starter descriptor")
    if sha256(descriptor_bytes).hexdigest() != APPROVED_RELEASE_SHA256:
        raise ValueError("approved starter descriptor hash mismatch")

    descriptor = fields(
        decode_json(descriptor_bytes),
        {"schema_version", "feature_version", "manifest_file", "manifest_sha256",
         "hand", "settings", "model_version"},
    )
    version(descriptor["schema_version"])
    if type(descriptor["feature_version"]) is not int or descriptor["feature_version"] != FEATURE_VERSION:
        raise ValueError("unsupported starter feature version")
    if descriptor["hand"] != "Right":
        raise ValueError("starter release is approved for Right hand only")

    settings = _settings(descriptor["settings"])
    manifest_path = _local_file(RELEASE_PATH.parent, descriptor["manifest_file"], ".json")
    expected_manifest_hash = _digest(descriptor["manifest_sha256"], "manifest_sha256")
    before_manifest = _stable_hash(manifest_path, expected_manifest_hash, "manifest")
    manifest = read_json(manifest_path, limit=MAX_MANIFEST_BYTES)
    after_manifest = _stable_hash(manifest_path, expected_manifest_hash, "manifest")
    if before_manifest != after_manifest:
        raise ValueError("starter manifest changed during loading")
    manifest_data = fields(
        manifest,
        {"schema_version", "feature_version", "labels", "feature_file", "feature_sha256", "records"},
        {"metadata", "vocabulary"},
    )
    sidecar = _local_file(manifest_path.parent, manifest_data["feature_file"], ".npz")
    expected_sidecar_hash = _digest(manifest_data["feature_sha256"], "feature_sha256")
    before_sidecar = _stable_hash(sidecar, expected_sidecar_hash, "feature sidecar")
    _inspect_npz(sidecar)

    bundle = load_dataset(manifest_path)
    if file_sha256(manifest_path) != expected_manifest_hash:
        raise ValueError("starter manifest changed during dataset loading")
    if file_sha256(sidecar) != before_sidecar:
        raise ValueError("starter feature sidecar changed during dataset loading")
    _validate_bundle(bundle)

    features, labels, records = bundle.training_data()
    model = train_model(
        features,
        labels,
        settings["algorithm"],
        settings["multiplier"],
        settings["margin"],
        groups=[record.trial_id for record in records],
        vocabulary=bundle.vocabulary,
        knn_k=settings["knn_k"],
        knn_weights=settings["knn_weights"],
        svm_c=settings["svm_c"],
        svm_gamma=settings["svm_gamma"],
    )
    if model.model_version != descriptor["model_version"]:
        raise ValueError("starter model revision changed; review descriptor and data")
    return model, "Right", "standard-guest", bundle.vocabulary


def _read_bytes(path: Path, limit: int, label: str) -> bytes:
    if path.is_symlink():
        raise ValueError(f"{label} must not be a symlink")
    with path.open("rb") as stream:
        data = stream.read(limit + 1)
    if len(data) > limit:
        raise ValueError(f"{label} exceeds the size limit")
    return data


def _local_file(root: Path, value: object, suffix: str) -> Path:
    if not isinstance(value, str):
        raise ValueError("release file reference must be a filename")
    path = Path(value)
    if path.name != value or path.suffix.lower() != suffix:
        raise ValueError("release file reference must be a local filename")
    candidate = root / path
    if candidate.is_symlink():
        raise ValueError("release file reference must stay inside the starter folder")
    resolved = candidate.resolve()
    if resolved.parent != root.resolve():
        raise ValueError("release file reference must stay inside the starter folder")
    return resolved


def _digest(value: object, name: str) -> str:
    if not isinstance(value, str) or len(value) != 64 or any(c not in "0123456789abcdef" for c in value):
        raise ValueError(f"invalid {name}")
    return value


def _stable_hash(path: Path, expected: str, label: str) -> str:
    actual = file_sha256(path)
    if actual != expected:
        raise ValueError(f"starter {label} hash mismatch")
    return actual


def _inspect_npz(path: Path) -> None:
    if path.is_symlink():
        raise ValueError("starter feature sidecar must not be a symlink")
    try:
        with zipfile.ZipFile(path) as archive:
            expanded = sum(info.file_size for info in archive.infolist())
    except zipfile.BadZipFile as exc:
        raise ValueError("starter feature sidecar must be a bounded NPZ archive") from exc
    if expanded > MAX_NPZ_EXPANDED_BYTES:
        raise ValueError("starter feature sidecar expands beyond the size limit")


def _settings(raw: object) -> dict[str, Any]:
    data = fields(raw, {"algorithm", "knn_k", "knn_weights", "svm_c", "svm_gamma",
                        "multiplier", "margin"})
    algorithm = data["algorithm"]
    if algorithm not in ("knn", "svm"):
        raise ValueError("starter algorithm must be knn or svm")
    knn_k = data["knn_k"]
    if isinstance(knn_k, bool) or type(knn_k) is not int:
        raise ValueError("starter knn_k must be an integer")
    knn_weights = data["knn_weights"]
    if knn_weights not in ("uniform", "distance"):
        raise ValueError("starter knn_weights must be uniform or distance")
    return {
        "algorithm": algorithm,
        "knn_k": knn_k,
        "knn_weights": knn_weights,
        "svm_c": _number(data["svm_c"], "svm_c"),
        "svm_gamma": "scale" if data["svm_gamma"] == "scale" else _number(data["svm_gamma"], "svm_gamma"),
        "multiplier": _number(data["multiplier"], "multiplier"),
        "margin": _number(data["margin"], "margin"),
    }


def _number(value: object, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
        raise ValueError(f"starter {name} must be a finite number")
    return float(value)


def _validate_bundle(bundle) -> None:
    if bundle.vocabulary != LEGACY_VOCABULARY:
        raise ValueError("starter release must use the standard vocabulary")
    if bundle.metadata.get("chosen_hand") != "Right":
        raise ValueError("starter release metadata must choose Right hand")
    if not bundle.records:
        raise ValueError("starter release must contain TRAIN records")
    if any(record.split != TRAIN_SPLIT for record in bundle.records):
        raise ValueError("starter release must contain TRAIN-only records")
    if any(record.intended_label not in LABELS for record in bundle.records):
        raise ValueError("starter release contains a non-standard label")
    if any(record.provenance != "human" for record in bundle.records):
        raise ValueError("starter release requires human provenance")
    if any(record.hand not in (None, "Right") for record in bundle.records):
        raise ValueError("starter release is approved for Right hand records only")
    if any(record.hand != "Right" for record in bundle.valid_records(TRAIN_SPLIT)):
        raise ValueError("starter release is approved for Right hand records only")
    for participant in {record.participant_id for record in bundle.records}:
        validate_identifier(participant)
    participants = sorted({record.participant_id for record in bundle.valid_records(TRAIN_SPLIT)})
    if len(participants) < 3:
        raise ValueError("starter release requires at least three contributors")
    for participant in participants:
        labels = {
            record.intended_label
            for record in bundle.valid_records(TRAIN_SPLIT)
            if record.participant_id == participant
        }
        if labels != set(LABELS):
            raise ValueError("each starter contributor must provide every standard label")
    if np.any(np.linalg.norm(bundle.features, axis=1) <= 1e-8) or np.max(np.ptp(bundle.features, axis=0)) <= 1e-8:
        raise ValueError("starter release contains degenerate features")
