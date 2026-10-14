"""Frozen paired positive TEST evaluation for starter and personal recognisers."""

from __future__ import annotations

import argparse
from dataclasses import asdict
from hashlib import sha256
import json
import os
from pathlib import Path
import re
from time import perf_counter
from typing import Any
from uuid import uuid4

import numpy as np

from .contracts import validate_identifier
from .dataset import DatasetBundle, SampleRecord, dataset_hashes, file_sha256, load_dataset, merge_datasets
from .evaluate import UNKNOWN, _predict_records, classification_metrics, trial_majority_predictions
from .models import train_model
from .vocabulary import GestureVocabulary, LEGACY_VOCABULARY

SCHEMA_VERSION = 1
PROTOCOL_VERSION = "gf-p18-positive-test-v1"
MODEL_NAMES = ("starter", "personal")
DEV_SPLITS = {"train", "validation", "validation_negative"}
TEST_SPLIT = "test"
BROWSER_TEST_PROTOCOL = "gestureforge-browser-test-v1"
SETTING_KEYS = {
    "algorithm",
    "multiplier",
    "margin",
    "knn_k",
    "knn_weights",
    "svm_c",
    "svm_gamma",
}


def freeze_config(config_path: str | Path, output_path: str | Path) -> dict[str, Any]:
    """Freeze development inputs and settings without reading final TEST data."""

    base = Path(config_path).resolve().parent
    output_base = Path(output_path).resolve().parent
    config = _read_json(Path(config_path))
    target = _text(config, "target_participant")
    validate_identifier(target)
    hand = _hand(config.get("hand"), "hand")
    pose_set = _pose_set(config)
    frozen_models: dict[str, Any] = {}
    seen_dev_sessions: set[str] = set()
    seen_dev_trials: set[str] = set()
    seen_dev_features: set[str] = set()
    vocabulary: GestureVocabulary | None = None
    provenance: str | None = None

    for name in MODEL_NAMES:
        section = _mapping(config.get(name), name)
        manifests = _manifest_paths(section.get("manifests"), base, f"{name}.manifests")
        if not manifests:
            raise ValueError(f"{name}.manifests must contain at least one development manifest")
        bundles = [load_dataset(path) for path in manifests]
        vocabulary = bundles[0].vocabulary if vocabulary is None else vocabulary
        if any(bundle.vocabulary != vocabulary for bundle in bundles):
            raise ValueError(f"{name} manifests use a different vocabulary")
        for bundle, path in zip(bundles, manifests, strict=True):
            provenance = _merge_provenance(provenance, _dataset_provenance(bundle))
            _validate_development_bundle(
                bundle, path, name, target, hand, pose_set["id"], require_target=(name == "personal")
            )
        bundle = merge_datasets(bundles)
        _register_role_records(
            bundle, f"{name} development", seen_dev_sessions, seen_dev_trials, seen_dev_features
        )
        _require_training_coverage(bundle, name)
        frozen_models[name] = {
            "manifests": [_manifest_fingerprint(path, output_base) for path in manifests],
            "settings": _model_settings(section.get("settings", {}), f"{name}.settings"),
        }

    assert vocabulary is not None
    pose_descriptions = pose_set["descriptions"]
    _require_pose_descriptions(vocabulary, pose_descriptions)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "protocol_version": PROTOCOL_VERSION,
        "purpose": (
            "Frozen reproducibility record for paired offline positive TEST scoring; "
            "not proof of chronology, consent, or live readiness."
        ),
        "target_participant": target,
        "hand": hand,
        "pose_set": pose_set,
        "vocabulary": vocabulary.to_dict(),
        "models": frozen_models,
        "provenance": provenance,
        "limitations": [
            "Scores positive TEST gesture trials only; validation_negative data are not final TEST negatives.",
            "UNKNOWN predictions, rejected samples, invalid samples, and missing scheduled sample slots are misses.",
            "Entirely absent trials cannot be inferred from the manifest.",
            "Declared pose-set metadata does not prove physical equivalence of recorded poses.",
            "This does not certify new-user readiness or live-controller performance.",
        ],
    }
    payload["config_fingerprint"] = _stable_hash(_without_keys(payload, {"integrity_sha256"}))
    payload["integrity_sha256"] = _stable_hash(_without_keys(payload, {"integrity_sha256"}))
    _write_json_exclusive(Path(output_path), payload)
    return payload


def score_frozen(
    frozen_path: str | Path,
    test_manifests: list[str | Path],
    output_path: str | Path,
) -> dict[str, Any]:
    """Score frozen starter and personal recognisers on identical positive TEST records."""

    frozen = _read_json(Path(frozen_path))
    _validate_frozen(frozen)
    base = Path(frozen_path).resolve().parent
    vocabulary = GestureVocabulary.from_mapping(frozen["vocabulary"])
    target = str(frozen["target_participant"])
    hand = str(frozen["hand"])
    pose_id = str(frozen["pose_set"]["id"])
    dev_bundles: dict[str, DatasetBundle] = {}
    train_sessions: set[str] = set()
    train_trials: set[str] = set()
    train_features: set[str] = set()

    for name in MODEL_NAMES:
        manifests = frozen["models"][name]["manifests"]
        bundles = []
        for pinned in manifests:
            path = _resolve_pinned_path(pinned, base)
            _check_manifest_fingerprint(path, pinned)
            bundle = load_dataset(path)
            _validate_development_bundle(
                bundle, path, name, target, hand, pose_id, require_target=(name == "personal")
            )
            bundles.append(bundle)
        dev_bundle = merge_datasets(bundles)
        _require_training_coverage(dev_bundle, name)
        _register_role_records(dev_bundle, f"{name} development", train_sessions, train_trials, train_features)
        dev_bundles[name] = dev_bundle

    test_paths = [Path(path).resolve() for path in test_manifests]
    if not test_paths:
        raise ValueError("at least one TEST manifest is required")
    test_bundles = [load_dataset(path) for path in test_paths]
    for bundle, path in zip(test_bundles, test_paths, strict=True):
        _validate_test_bundle(bundle, path, target, hand, pose_id, vocabulary, frozen)
    test_bundle = merge_datasets(test_bundles)
    _require_test_coverage(test_bundle, vocabulary)
    _reject_overlap(test_bundle, "TEST", train_sessions, train_trials, train_features)
    provenance = _report_provenance([*dev_bundles.values(), test_bundle])

    sample_order = [(record.trial_id, record.sample_index) for record in test_bundle.records]
    results = []
    for name in MODEL_NAMES:
        results.append(_score_model(name, frozen, dev_bundles[name], test_bundle, sample_order))

    by_name = {item["model_name"]: item for item in results}
    report = {
        "schema_version": SCHEMA_VERSION,
        "protocol_version": PROTOCOL_VERSION,
        "frozen": {
            "path": str(Path(frozen_path).resolve()),
            "sha256": file_sha256(frozen_path),
            "config_fingerprint": frozen["config_fingerprint"],
            "integrity_verified": True,
        },
        "test_inputs": [_manifest_fingerprint(path, base) for path in test_paths],
        "target_participant": target,
        "hand": hand,
        "pose_set": frozen["pose_set"],
        "vocabulary": frozen["vocabulary"],
        "provenance": provenance,
        "claims": {
            "paired_positive_test_only": True,
            "unknown_predictions_are_misses": True,
            "no_new_user_readiness_certification": True,
            "freeze_is_not_chronology_or_consent_proof": True,
        },
        "limitations": frozen["limitations"],
        "results": results,
        "paired": {
            "same_test_record_order": (
                by_name["starter"]["sample_identity"] == by_name["personal"]["sample_identity"]
            ),
            "personal_minus_starter_macro_f1": (
                by_name["personal"]["metrics"]["macro_f1"] - by_name["starter"]["metrics"]["macro_f1"]
            ),
            "trial_outcomes": _paired_trial_outcomes(
                by_name["starter"]["trial_predictions"], by_name["personal"]["trial_predictions"]
            ),
        },
    }
    _write_json_exclusive(Path(output_path), report)
    return report


def _score_model(
    name: str,
    frozen: dict[str, Any],
    development: DatasetBundle,
    test_bundle: DatasetBundle,
    sample_order: list[tuple[str, int]],
) -> dict[str, Any]:
    settings = frozen["models"][name]["settings"]
    train_features, train_labels, train_records = development.training_data()
    revision = _fitted_revision(frozen, name)
    fit_start = perf_counter()
    model = train_model(
        train_features,
        train_labels,
        algorithm=settings["algorithm"],
        multiplier=settings["multiplier"],
        margin=settings["margin"],
        vocabulary=development.vocabulary,
        groups=[record.trial_id for record in train_records],
        knn_k=settings["knn_k"],
        knn_weights=settings["knn_weights"],
        svm_c=settings["svm_c"],
        svm_gamma=settings["svm_gamma"],
    )
    fit_seconds = perf_counter() - fit_start
    predict_start = perf_counter()
    sample_predictions = _predict_records(model, test_bundle, test_bundle.records)
    predict_seconds = perf_counter() - predict_start
    trial_predictions = trial_majority_predictions(test_bundle.records, sample_predictions)
    metrics = classification_metrics(trial_predictions, test_bundle.vocabulary)
    counts = _prediction_counts(test_bundle.records, sample_predictions, trial_predictions)
    config = model.to_config()
    config["fitted_revision"] = revision
    return {
        "model_name": name,
        "settings": settings,
        "model": config,
        "train_samples": len(train_records),
        "test_samples": len(test_bundle.records),
        "test_trials": len(trial_predictions),
        "timing": {
            "fit_seconds": fit_seconds,
            "predict_seconds": predict_seconds,
            "predict_seconds_per_sample": predict_seconds / max(1, len(test_bundle.records)),
        },
        "metrics": metrics,
        "counts": counts,
        "sample_identity": sample_order,
        "sample_predictions": sample_predictions,
        "trial_predictions": trial_predictions,
    }


def _validate_development_bundle(
    bundle: DatasetBundle,
    path: Path,
    name: str,
    target: str,
    hand: str,
    pose_set_id: str,
    *,
    require_target: bool,
) -> None:
    _validate_dataset_pose(bundle, path, pose_set_id, development=True)
    splits = {record.split for record in bundle.records}
    if TEST_SPLIT in splits:
        raise ValueError(f"{name} development manifest must not contain TEST records: {path}")
    unexpected = sorted(splits - DEV_SPLITS)
    if unexpected:
        raise ValueError(f"{name} development contains unsupported splits {unexpected}")
    participants = {record.participant_id for record in bundle.records}
    if require_target:
        if participants != {target}:
            raise ValueError("personal development must contain only the target participant")
    elif target in participants:
        raise ValueError("starter development must exclude the target participant")
    _validate_hand(bundle, hand, f"{name} development")
    _reject_mixed_provenance(bundle)


def _validate_test_bundle(
    bundle: DatasetBundle,
    path: Path,
    target: str,
    hand: str,
    pose_set_id: str,
    vocabulary: GestureVocabulary,
    frozen: dict[str, Any],
) -> None:
    _validate_dataset_pose(bundle, path, pose_set_id, development=False)
    if bundle.vocabulary != vocabulary:
        raise ValueError("TEST vocabulary does not match frozen vocabulary")
    splits = {record.split for record in bundle.records}
    if splits != {TEST_SPLIT}:
        raise ValueError("final scoring accepts positive TEST manifests only")
    participants = {record.participant_id for record in bundle.records}
    if participants != {target}:
        raise ValueError("TEST manifest must contain only the frozen target participant")
    labels = {record.intended_label for record in bundle.records}
    if UNKNOWN in labels:
        raise ValueError("UNKNOWN records are excluded from this positive TEST evaluator")
    _validate_hand(bundle, hand, "TEST")
    _reject_mixed_provenance(bundle)
    if bundle.metadata.get("import_source") == "browser-participant-kit" or "browser_collection" in bundle.metadata:
        browser = _mapping(bundle.metadata.get("browser_collection"), "browser_collection")
        ticket = _browser_test_ticket(frozen)
        found_ticket = browser.get("test_ticket")
        if (
            bundle.metadata.get("import_source") != "browser-participant-kit"
            or browser.get("protocol") != BROWSER_TEST_PROTOCOL or not isinstance(found_ticket, dict)
            or type(found_ticket.get("schema_version")) is not int or found_ticket != ticket
        ):
            raise ValueError("browser TEST ticket does not match the frozen configuration")
        from .import_participant import _trial_identity_hash

        session = f"{target}-test-{ticket['config_fingerprint'][:32]}"
        expected_slots = {
            (session, _trial_identity_hash(target, session, f"test-{label}-{index:02d}"), label, sample)
            for label in vocabulary.labels for index in range(1, 13) for sample in range(5)
        }
        actual_slots = {(row.session_id, row.trial_id, row.intended_label, row.sample_index) for row in bundle.records}
        if actual_slots != expected_slots or len(bundle.records) != 240:
            raise ValueError("browser TEST scoring requires all 48 planned trials and 240 sample slots; partial returns may be imported for recovery")


def _validate_dataset_pose(bundle: DatasetBundle, path: Path, pose_set_id: str, *, development: bool) -> None:
    found = bundle.metadata.get("pose_set_id")
    if found is None and development:
        return
    if found != pose_set_id:
        raise ValueError(f"pose set mismatch for {path}")


def _validate_hand(bundle: DatasetBundle, hand: str, role: str) -> None:
    hands = {record.hand for record in bundle.records if record.valid and record.hand is not None}
    if hands and hands != {hand}:
        raise ValueError(f"{role} must contain only {hand} hand records")
    declared = bundle.metadata.get("chosen_hand")
    if declared is not None and declared not in {"Left", "Right"}:
        raise ValueError(f"{role} declared chosen hand must be Left or Right")
    if declared is not None and declared != hand:
        raise ValueError(f"{role} declared chosen hand must be {hand}")
    if not hands and declared != hand:
        raise ValueError(f"{role} with no valid detections must declare chosen_hand as {hand}")


def _reject_mixed_provenance(bundle: DatasetBundle) -> None:
    provenances = {record.provenance for record in bundle.records}
    if "synthetic" in provenances and len(provenances) > 1:
        raise ValueError("evaluation cannot mix synthetic and human records")


def _merge_provenance(current: str | None, incoming: str) -> str:
    if current is None:
        return incoming
    if current != incoming:
        raise ValueError("evaluation cannot mix synthetic and human records")
    return current


def _dataset_provenance(bundle: DatasetBundle) -> str:
    provenances = {record.provenance for record in bundle.records}
    if provenances == {"synthetic"}:
        return "synthetic"
    if "synthetic" in provenances:
        raise ValueError("evaluation cannot mix synthetic and human records")
    return "human"


def _report_provenance(bundles: list[DatasetBundle]) -> dict[str, Any]:
    provenances = {_dataset_provenance(bundle) for bundle in bundles}
    if len(provenances) != 1:
        raise ValueError("evaluation cannot mix synthetic and human records")
    value = next(iter(provenances))
    return {
        "kind": value,
        "synthetic_input": value == "synthetic",
        "note": (
            "Synthetic fixtures are software-test evidence only."
            if value == "synthetic"
            else "Human numeric features; no raw video or images are required by this report."
        ),
    }


def _require_training_coverage(bundle: DatasetBundle, name: str) -> None:
    _, labels, records = bundle.training_data()
    if len(records) == 0:
        raise ValueError(f"{name} development has no valid TRAIN records")
    missing = sorted(set(bundle.vocabulary.labels) - set(str(label) for label in labels))
    if missing:
        raise ValueError(f"{name} TRAIN records must include all labels; missing {missing}")


def _require_test_coverage(bundle: DatasetBundle, vocabulary: GestureVocabulary) -> None:
    if not bundle.records:
        raise ValueError("TEST manifests contain no records")
    participants = sorted({record.participant_id for record in bundle.records})
    for participant in participants:
        labels = {record.intended_label for record in bundle.records if record.participant_id == participant}
        missing = sorted(set(vocabulary.labels) - labels)
        if missing:
            raise ValueError(f"TEST records for {participant} must include all labels; missing {missing}")


def _register_role_records(
    bundle: DatasetBundle,
    role: str,
    sessions: set[str],
    trials: set[str],
    feature_hashes: set[str],
) -> None:
    local_sessions = {record.session_id for record in bundle.records}
    local_trials = {record.trial_id for record in bundle.records}
    local_feature_roles: dict[str, set[tuple[str, str]]] = {}
    for record in bundle.records:
        if record.valid and record.feature_index is not None:
            feature_hash = _feature_hash(bundle.features[record.feature_index])
            local_feature_roles.setdefault(feature_hash, set()).add((record.participant_id, record.split))
    if any(len(roles) > 1 for roles in local_feature_roles.values()):
        raise ValueError(f"{role} contains exact feature leakage across participant/split roles")
    if sessions.intersection(local_sessions):
        raise ValueError(f"{role} reuses a session identity from another role")
    if trials.intersection(local_trials):
        raise ValueError(f"{role} reuses a trial identity from another role")
    local_features = set(local_feature_roles)
    if feature_hashes.intersection(local_features):
        raise ValueError(f"{role} contains exact duplicate feature vectors across roles")
    sessions.update(local_sessions)
    trials.update(local_trials)
    feature_hashes.update(local_features)


def _reject_overlap(
    bundle: DatasetBundle,
    role: str,
    sessions: set[str],
    trials: set[str],
    feature_hashes: set[str],
) -> None:
    for record in bundle.records:
        if record.session_id in sessions:
            raise ValueError(f"{role} reuses development session identity")
        if record.trial_id in trials:
            raise ValueError(f"{role} reuses development trial identity")
        if record.valid and record.feature_index is not None:
            feature_hash = _feature_hash(bundle.features[record.feature_index])
            if feature_hash in feature_hashes:
                raise ValueError(f"{role} contains exact feature overlap with development data")


def _feature_hash(feature: np.ndarray) -> str:
    return sha256(np.asarray(feature, dtype=np.float32).tobytes()).hexdigest()


def _prediction_counts(
    records: tuple[SampleRecord, ...],
    sample_predictions: list[dict[str, Any]],
    trial_predictions: list[dict[str, str]],
) -> dict[str, int]:
    present_slots = {(record.trial_id, record.sample_index) for record in records}
    absent_slots = sum(
        1
        for trial_id in {record.trial_id for record in records}
        for sample_index in range(5)
        if (trial_id, sample_index) not in present_slots
    )
    invalid_slots = sum(1 for record in records if not record.valid or record.feature_index is None)
    classifier_rejections = sum(
        1
        for record, prediction in zip(records, sample_predictions, strict=True)
        if record.valid and record.feature_index is not None and not prediction["accepted"]
    )
    return {
        "samples": len(sample_predictions),
        "absent_scheduled_slots": absent_slots,
        "invalid_or_missing_scheduled_slots": invalid_slots + absent_slots,
        "classifier_rejected_samples": classifier_rejections,
        "unknown_sample_scores": (
            sum(1 for row in sample_predictions if row["scored_label"] == UNKNOWN) + absent_slots
        ),
        "unknown_trial_predictions": sum(1 for row in trial_predictions if row["predicted_label"] == UNKNOWN),
    }


def _paired_trial_outcomes(
    starter: list[dict[str, str]],
    personal: list[dict[str, str]],
) -> list[dict[str, Any]]:
    personal_by_trial = {row["trial_id"]: row for row in personal}
    outcomes = []
    for row in starter:
        other = personal_by_trial[row["trial_id"]]
        outcomes.append({
            "trial_id": row["trial_id"],
            "true_label": row["true_label"],
            "starter_prediction": row["predicted_label"],
            "personal_prediction": other["predicted_label"],
            "starter_correct": row["predicted_label"] == row["true_label"],
            "personal_correct": other["predicted_label"] == other["true_label"],
        })
    return outcomes


def _model_settings(value: Any, field: str) -> dict[str, Any]:
    raw = _mapping(value, field)
    unexpected = sorted(set(raw) - SETTING_KEYS)
    if unexpected:
        raise ValueError(f"{field} contains unsupported settings {unexpected}")
    algorithm = raw.get("algorithm", "knn")
    if algorithm not in {"knn", "svm"}:
        raise ValueError(f"{field}.algorithm must be knn or svm")
    settings = {
        "algorithm": algorithm,
        "multiplier": _finite_positive(raw.get("multiplier", 1.5), f"{field}.multiplier"),
        "margin": _finite_minimum(raw.get("margin", 1.0), 1.0, f"{field}.margin"),
        "knn_k": _positive_int(raw.get("knn_k", 5), f"{field}.knn_k"),
        "knn_weights": raw.get("knn_weights", "distance"),
        "svm_c": _finite_positive(raw.get("svm_c", 1.0), f"{field}.svm_c"),
        "svm_gamma": raw.get("svm_gamma", "scale"),
    }
    if settings["knn_weights"] not in {"uniform", "distance"}:
        raise ValueError(f"{field}.knn_weights must be uniform or distance")
    if settings["svm_gamma"] != "scale":
        settings["svm_gamma"] = _finite_positive(settings["svm_gamma"], f"{field}.svm_gamma")
    return settings


def _pose_set(config: dict[str, Any]) -> dict[str, Any]:
    if "pose_set" in config:
        pose = _mapping(config["pose_set"], "pose_set")
        pose_id = _text(pose, "id")
        descriptions = _mapping(pose.get("descriptions"), "pose_set.descriptions")
    else:
        pose_id = _text(config, "pose_set_id")
        descriptions = _mapping(config.get("pose_descriptions"), "pose_descriptions")
    validate_identifier(pose_id)
    return {
        "id": pose_id,
        "descriptions": {str(key): _nonempty_text(value, f"pose description {key}") for key, value in descriptions.items()},
        "operator_declaration": (
            "Development manifests without pose_set_id are accepted only as an operator assertion "
            "that the frozen pose-set declaration matches those recordings."
        ),
    }


def _require_pose_descriptions(vocabulary: GestureVocabulary, descriptions: dict[str, str]) -> None:
    missing = sorted(set(vocabulary.labels) - set(descriptions))
    if missing:
        raise ValueError(f"pose descriptions must cover all labels; missing {missing}")


def _manifest_paths(value: Any, base: Path, field: str) -> list[Path]:
    if not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value):
        raise ValueError(f"{field} must be a non-empty array of paths")
    return [(base / item).resolve() if not Path(item).is_absolute() else Path(item).resolve() for item in value]


def _manifest_fingerprint(path: Path, base: Path) -> dict[str, Any]:
    bundle = load_dataset(path)
    hashes = dataset_hashes(bundle)
    return {
        "path": os.path.relpath(path.resolve(), base.resolve()),
        "manifest_sha256": hashes["manifest_sha256"],
        "features_sha256": hashes["features_sha256"],
    }


def _check_manifest_fingerprint(path: Path, pinned: dict[str, Any]) -> None:
    current = _manifest_fingerprint(path, path.resolve().parent)
    if current["manifest_sha256"] != pinned["manifest_sha256"]:
        raise ValueError(f"manifest checksum changed: {path}")
    if current["features_sha256"] != pinned["features_sha256"]:
        raise ValueError(f"feature sidecar checksum changed: {path}")


def _resolve_pinned_path(pinned: dict[str, Any], base: Path) -> Path:
    raw = _text(pinned, "path")
    path = Path(raw)
    return path.resolve() if path.is_absolute() else (base / path).resolve()


def _validate_frozen(frozen: dict[str, Any]) -> None:
    if (
        type(frozen.get("schema_version")) is not int or frozen.get("schema_version") != SCHEMA_VERSION
        or frozen.get("protocol_version") != PROTOCOL_VERSION
    ):
        raise ValueError("unsupported frozen paired evaluation file")
    expected = frozen.get("integrity_sha256")
    if expected != _stable_hash(_without_keys(frozen, {"integrity_sha256"})):
        raise ValueError("frozen file integrity check failed")
    if frozen.get("config_fingerprint") != _stable_hash(_without_keys(frozen, {"integrity_sha256", "config_fingerprint"})):
        raise ValueError("frozen configuration fingerprint check failed")
    validate_identifier(_text(frozen, "target_participant"))
    _hand(frozen.get("hand"), "hand")
    pose = _pose_set(frozen)
    vocabulary = GestureVocabulary.from_mapping(frozen.get("vocabulary"))
    _require_pose_descriptions(vocabulary, pose["descriptions"])
    if set(_mapping(frozen.get("models"), "models")) != set(MODEL_NAMES):
        raise ValueError("frozen file must define starter and personal models")
    for name in MODEL_NAMES:
        model = _mapping(frozen["models"][name], name)
        settings = _mapping(model.get("settings"), f"{name}.settings")
        if set(settings) != SETTING_KEYS:
            raise ValueError(f"{name}.settings must contain every frozen setting")
        _model_settings(settings, f"{name}.settings")
        pins = model.get("manifests")
        if not isinstance(pins, list) or not pins:
            raise ValueError(f"{name}.manifests must contain development fingerprints")
        for value in pins:
            pin = _mapping(value, "manifest fingerprint")
            _text(pin, "path")
            for key in ("manifest_sha256", "features_sha256"):
                if re.fullmatch(r"[0-9a-f]{64}", _text(pin, key)) is None:
                    raise ValueError(f"invalid {key}")


def browser_test_ticket(frozen_path: str | Path) -> dict[str, Any]:
    """Return only the public collection binding, never development paths or data."""
    frozen = _read_json(Path(frozen_path))
    _validate_frozen(frozen)
    return _browser_test_ticket(frozen)


def _browser_test_ticket(frozen: dict[str, Any]) -> dict[str, Any]:
    target = frozen["target_participant"]
    if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,23}", target) is None:
        raise ValueError("browser TEST target must be a 1-24 character participant pseudonym")
    if (
        frozen["hand"] != "Right"
        or frozen["pose_set"]["id"] != "standard-v1"
        or GestureVocabulary.from_mapping(frozen["vocabulary"]) != LEGACY_VOCABULARY
    ):
        raise ValueError("browser TEST requires Right hand and the standard-v1 legacy vocabulary")
    return {
        "schema_version": 1,
        "protocol": BROWSER_TEST_PROTOCOL,
        "paired_protocol": PROTOCOL_VERSION,
        "target_participant": target,
        "config_fingerprint": frozen["config_fingerprint"],
        "frozen_integrity_sha256": frozen["integrity_sha256"],
        "pose_set_id": "standard-v1",
        "hand": "Right",
    }


def _fitted_revision(frozen: dict[str, Any], name: str) -> str:
    return "paired-v1-" + _stable_hash({
        "protocol_version": frozen["protocol_version"],
        "config_fingerprint": frozen["config_fingerprint"],
        "model_name": name,
        "model": frozen["models"][name],
    })[:32]


def _read_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("JSON input must be an object")
    return payload


def _write_json_exclusive(path: Path, data: dict[str, Any]) -> None:
    target = path.resolve()
    if target.exists():
        raise FileExistsError(f"output already exists: {target}")
    encoded = json.dumps(data, ensure_ascii=False, allow_nan=False, indent=2, sort_keys=True) + "\n"
    target.parent.mkdir(parents=True, exist_ok=True)
    temp = target.with_name(f".{target.name}.{uuid4().hex}.tmp")
    try:
        temp.write_text(encoded, encoding="utf-8")
        os.link(temp, target)
    finally:
        if temp.exists():
            temp.unlink()


def _stable_hash(value: Any) -> str:
    return sha256(
        json.dumps(value, ensure_ascii=False, allow_nan=False, sort_keys=True, default=_json_default).encode("utf-8")
    ).hexdigest()


def _without_keys(value: dict[str, Any], keys: set[str]) -> dict[str, Any]:
    return {key: item for key, item in value.items() if key not in keys}


def _json_default(value: Any) -> Any:
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, SampleRecord):
        return asdict(value)
    raise TypeError(f"object of type {type(value).__name__} is not JSON serialisable")


def _mapping(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{field} must be an object")
    return value


def _text(value: dict[str, Any], key: str) -> str:
    return _nonempty_text(value.get(key), key)


def _nonempty_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value


def _hand(value: Any, field: str) -> str:
    if value not in {"Left", "Right"}:
        raise ValueError(f"{field} must be Left or Right")
    return str(value)


def _finite_positive(value: Any, field: str) -> float:
    number = _number(value, field)
    if number <= 0:
        raise ValueError(f"{field} must be positive")
    return number


def _finite_minimum(value: Any, minimum: float, field: str) -> float:
    number = _number(value, field)
    if number < minimum:
        raise ValueError(f"{field} must be at least {minimum}")
    return number


def _number(value: Any, field: str) -> float:
    if type(value) not in {int, float} or not np.isfinite(value):
        raise ValueError(f"{field} must be a finite number")
    return float(value)


def _positive_int(value: Any, field: str) -> int:
    if type(value) is not int or value < 1:
        raise ValueError(f"{field} must be a positive integer")
    return value


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    freeze_parser = subparsers.add_parser("freeze", help="Pin development inputs and settings.")
    freeze_parser.add_argument("--config", required=True, type=Path)
    freeze_parser.add_argument("--output", required=True, type=Path)
    score_parser = subparsers.add_parser("score", help="Score frozen settings on positive TEST manifests.")
    score_parser.add_argument("--frozen", required=True, type=Path)
    score_parser.add_argument("--test", required=True, type=Path, nargs="+")
    score_parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "freeze":
            freeze_config(args.config, args.output)
        else:
            score_frozen(args.frozen, args.test, args.output)
    except (FileExistsError, OSError, ValueError) as exc:
        parser.exit(1, f"paired_evaluate: {exc}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
