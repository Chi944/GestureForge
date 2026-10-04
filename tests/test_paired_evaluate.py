import json
import subprocess
import sys
from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest

from gestureforge.contracts import LABELS
from gestureforge.dataset import SampleRecord, load_dataset, save_dataset
from gestureforge.paired_evaluate import freeze_config, score_frozen


POSE_DESCRIPTIONS = {
    "NEXT": "Closed fist facing the camera.",
    "PREVIOUS": "Thumb-up pose facing the camera.",
    "BOOKMARK": "Index and middle fingers extended.",
    "NEUTRAL": "Open palm with all fingers visible.",
}


def write_json(path: Path, data):
    path.write_text(json.dumps(data, allow_nan=False), encoding="utf-8")


def make_dataset(
    path: Path,
    participant: str,
    split: str,
    *,
    pose_set_id: str | None = "standard-v1",
    hand: str = "Right",
    provenance: str = "synthetic",
    seed: int = 1,
    offset: float = 0.0,
    trials_per_label: int = 2,
    invalid_tail: bool = False,
):
    rng = np.random.default_rng(seed)
    features: list[np.ndarray] = []
    records = []
    timestamp = 0.0
    for label_index, label in enumerate(LABELS):
        center = np.zeros(60, dtype=np.float32)
        center[label_index * 12 : label_index * 12 + 12] = 1.0 + label_index + offset
        for trial_index in range(trials_per_label):
            trial_id = f"{participant}-{split}-{label}-{trial_index}"
            for sample_index in range(5):
                valid = not (invalid_tail and label == "NEXT" and trial_index == 0 and sample_index >= 2)
                feature_index = len(features) if valid else None
                if valid:
                    features.append(center + rng.normal(0.0, 0.015, 60).astype(np.float32))
                records.append(SampleRecord(
                    participant_id=participant,
                    session_id=f"{participant}-{split}",
                    trial_id=trial_id,
                    intended_label=label,
                    split=split,
                    sample_index=sample_index,
                    timestamp=timestamp,
                    valid=valid,
                    feature_index=feature_index,
                    validity_reason="" if valid else "missed scheduled timestamp",
                    hand=hand if valid else None,
                    provenance=provenance,
                ))
                timestamp += 0.2
    metadata = {"provenance": provenance.upper(), "chosen_hand": hand}
    if pose_set_id is not None:
        metadata["pose_set_id"] = pose_set_id
    return save_dataset(path, records, np.asarray(features, dtype=np.float32).reshape(-1, 60), metadata)


def paired_fixture(tmp_path: Path, *, algorithm: str = "knn") -> tuple[Path, Path, Path, Path]:
    starter = make_dataset(tmp_path / "starter" / "manifest.json", "P_STARTER", "train", seed=10, offset=0.08)
    personal = make_dataset(tmp_path / "personal" / "manifest.json", "P02", "train", seed=20)
    test = make_dataset(tmp_path / "test" / "manifest.json", "P02", "test", seed=30, invalid_tail=True, trials_per_label=1)
    config = tmp_path / "paired-config.json"
    write_json(config, {
        "target_participant": "P02",
        "hand": "Right",
        "pose_set": {"id": "standard-v1", "descriptions": POSE_DESCRIPTIONS},
        "starter": {
            "manifests": [str(starter.manifest_path.relative_to(tmp_path))],
            "settings": {"algorithm": algorithm, "multiplier": 2.0, "margin": 1.0},
        },
        "personal": {
            "manifests": [str(personal.manifest_path.relative_to(tmp_path))],
            "settings": {"algorithm": algorithm, "multiplier": 2.0, "margin": 1.0},
        },
    })
    return config, starter.manifest_path, personal.manifest_path, test.manifest_path


def rewrite_with_validation_manifest(path: Path, participant: str, *, leak: bool = False, validation_offset: float = 0.25):
    train = make_dataset(path.parent / "train-source" / "manifest.json", participant, "train", seed=101)
    validation = make_dataset(
        path.parent / "validation-source" / "manifest.json",
        participant,
        "validation",
        seed=202,
        offset=validation_offset,
    )
    records = list(train.records)
    offset = len(train.features)
    for record in validation.records:
        records.append(replace(
            record,
            feature_index=None if record.feature_index is None else record.feature_index + offset,
        ))
    features = np.vstack([train.features, validation.features]).astype(np.float32)
    if leak:
        features[offset] = features[0]
    metadata = {"provenance": "SYNTHETIC", "chosen_hand": "Right", "pose_set_id": "standard-v1"}
    return save_dataset(path, records, features, metadata)


@pytest.mark.parametrize("algorithm", ["knn", "svm"])
def test_freeze_and_score_report_paired_positive_test_metrics(tmp_path: Path, algorithm: str) -> None:
    config, _, _, test = paired_fixture(tmp_path, algorithm=algorithm)
    frozen = tmp_path / "frozen.json"
    report_path = tmp_path / "report.json"

    freeze = freeze_config(config, frozen)
    report = score_frozen(frozen, [test], report_path)

    assert freeze["protocol_version"] == "gf-p18-positive-test-v1"
    assert freeze["purpose"].startswith("Frozen reproducibility record")
    assert freeze["pose_set"]["descriptions"] == POSE_DESCRIPTIONS
    assert "not proof of chronology" in freeze["purpose"]
    assert report["claims"]["no_new_user_readiness_certification"] is True
    assert report["provenance"]["synthetic_input"] is True
    assert {item["model_name"] for item in report["results"]} == {"starter", "personal"}
    assert report["paired"]["same_test_record_order"] is True
    assert isinstance(report["paired"]["personal_minus_starter_macro_f1"], float)
    assert report["results"][0]["counts"]["invalid_or_missing_scheduled_slots"] >= 3
    assert report["results"][0]["counts"]["unknown_trial_predictions"] >= 1
    assert report["results"][0]["model"]["fitted_revision"].startswith("paired-v1-")
    assert json.loads(report_path.read_text(encoding="utf-8"))["paired"]["same_test_record_order"] is True


def test_frozen_paths_are_relative_to_frozen_file_not_config_file(tmp_path: Path) -> None:
    config, _, _, test = paired_fixture(tmp_path / "config-root")
    output_dir = tmp_path / "frozen-root"
    output_dir.mkdir()
    frozen = output_dir / "frozen.json"

    freeze_config(config, frozen)
    report = score_frozen(frozen, [test], output_dir / "report.json")

    pinned_path = json.loads(frozen.read_text(encoding="utf-8"))["models"]["starter"]["manifests"][0]["path"]
    assert pinned_path.startswith("..")
    assert report["paired"]["same_test_record_order"] is True


def test_test_features_cannot_change_frozen_fit_thresholds_or_revisions(tmp_path: Path) -> None:
    config, _, _, test = paired_fixture(tmp_path)
    frozen = tmp_path / "frozen.json"
    freeze_config(config, frozen)
    first = score_frozen(frozen, [test], tmp_path / "first.json")

    bundle = load_dataset(test)
    changed = bundle.features.copy()
    changed += 20.0
    save_dataset(test, bundle.records, changed, bundle.metadata)
    second = score_frozen(frozen, [test], tmp_path / "second.json")

    for index in range(2):
        assert first["results"][index]["model"]["thresholds"] == second["results"][index]["model"]["thresholds"]
        assert first["results"][index]["model"]["fitted_revision"] == second["results"][index]["model"]["fitted_revision"]
    assert first["results"][0]["metrics"] != second["results"][0]["metrics"]


def test_validation_feature_leakage_is_rejected_but_fresh_tuning_does_not_change_fit(tmp_path: Path) -> None:
    config, _, personal, test = paired_fixture(tmp_path)
    rewrite_with_validation_manifest(personal, "P02")
    frozen = tmp_path / "frozen.json"
    freeze_config(config, frozen)
    first = score_frozen(frozen, [test], tmp_path / "first.json")

    rewrite_with_validation_manifest(personal, "P02", validation_offset=0.75)
    second_frozen = tmp_path / "second-frozen.json"
    freeze_config(config, second_frozen)
    second = score_frozen(second_frozen, [test], tmp_path / "second.json")
    first_personal = next(item for item in first["results"] if item["model_name"] == "personal")
    second_personal = next(item for item in second["results"] if item["model_name"] == "personal")
    assert first_personal["model"]["thresholds"] == second_personal["model"]["thresholds"]

    rewrite_with_validation_manifest(personal, "P02", leak=True)
    with pytest.raises(ValueError, match="feature leakage"):
        freeze_config(config, tmp_path / "leaky-frozen.json")


def test_freeze_rejects_target_in_starter_and_test_in_development(tmp_path: Path) -> None:
    config, starter, _, _ = paired_fixture(tmp_path)
    bundle = load_dataset(starter)
    records = [replace(record, participant_id="P02") for record in bundle.records]
    save_dataset(starter, records, bundle.features, bundle.metadata)

    with pytest.raises(ValueError, match="starter development must exclude"):
        freeze_config(config, tmp_path / "frozen.json")

    config, starter, _, _ = paired_fixture(tmp_path / "next")
    bundle = load_dataset(starter)
    records = [replace(record, split="test", session_id="bad-test", trial_id=f"bad-{index}")
               for index, record in enumerate(bundle.records)]
    save_dataset(starter, records, bundle.features, bundle.metadata)
    with pytest.raises(ValueError, match="must not contain TEST"):
        freeze_config(config, tmp_path / "next" / "frozen.json")


def test_score_rejects_hash_tampering_pose_mismatch_and_non_test_records(tmp_path: Path) -> None:
    config, starter, _, test = paired_fixture(tmp_path)
    frozen = tmp_path / "frozen.json"
    freeze_config(config, frozen)
    manifest = json.loads(starter.read_text(encoding="utf-8"))
    manifest["metadata"]["note"] = "tampered"
    starter.write_text(json.dumps(manifest, allow_nan=False), encoding="utf-8")
    with pytest.raises(ValueError, match="checksum changed"):
        score_frozen(frozen, [test], tmp_path / "report.json")

    config, _, _, test = paired_fixture(tmp_path / "pose")
    frozen = tmp_path / "pose" / "frozen.json"
    freeze_config(config, frozen)
    bundle = load_dataset(test)
    metadata = dict(bundle.metadata, pose_set_id="other-pose")
    save_dataset(test, bundle.records, bundle.features, metadata)
    with pytest.raises(ValueError, match="pose set mismatch"):
        score_frozen(frozen, [test], tmp_path / "pose" / "report.json")

    config, _, _, test = paired_fixture(tmp_path / "split")
    frozen = tmp_path / "split" / "frozen.json"
    freeze_config(config, frozen)
    bundle = load_dataset(test)
    records = [replace(record, split="validation", session_id="not-test", trial_id=f"not-test-{index}")
               for index, record in enumerate(bundle.records)]
    save_dataset(test, records, bundle.features, bundle.metadata)
    with pytest.raises(ValueError, match="positive TEST"):
        score_frozen(frozen, [test], tmp_path / "split" / "report.json")


def test_overlap_mixed_provenance_hand_vocab_and_pose_declarations_are_rejected(tmp_path: Path) -> None:
    config, _, personal, test = paired_fixture(tmp_path)
    personal_bundle = load_dataset(personal)
    test_bundle = load_dataset(test)
    save_dataset(test, test_bundle.records, personal_bundle.features[:len(test_bundle.features)], test_bundle.metadata)
    frozen = tmp_path / "frozen.json"
    freeze_config(config, frozen)
    with pytest.raises(ValueError, match="exact feature overlap"):
        score_frozen(frozen, [test], tmp_path / "report.json")

    config, _, _, test = paired_fixture(tmp_path / "shared-session")
    frozen = tmp_path / "shared-session" / "frozen.json"
    freeze_config(config, frozen)
    bundle = load_dataset(test)
    records = [replace(record, session_id="P02-train", trial_id=f"fresh-{index}")
               for index, record in enumerate(bundle.records)]
    save_dataset(test, records, bundle.features, bundle.metadata)
    with pytest.raises(ValueError, match="session identity"):
        score_frozen(frozen, [test], tmp_path / "shared-session" / "report.json")

    config, _, personal, _ = paired_fixture(tmp_path / "mixed")
    bundle = load_dataset(personal)
    records = list(bundle.records)
    records[0] = replace(records[0], provenance="human")
    save_dataset(personal, records, bundle.features, bundle.metadata)
    with pytest.raises(ValueError, match="cannot mix synthetic and human"):
        freeze_config(config, tmp_path / "mixed" / "frozen.json")

    config, _, _, test = paired_fixture(tmp_path / "mixed-test")
    frozen = tmp_path / "mixed-test" / "frozen.json"
    freeze_config(config, frozen)
    bundle = load_dataset(test)
    records = [replace(record, provenance="human") for record in bundle.records]
    save_dataset(test, records, bundle.features, dict(bundle.metadata, provenance="HUMAN"))
    with pytest.raises(ValueError, match="cannot mix synthetic and human"):
        score_frozen(frozen, [test], tmp_path / "mixed-test" / "report.json")

    config, _, personal, _ = paired_fixture(tmp_path / "hand")
    bundle = load_dataset(personal)
    records = [replace(record, hand="Left") if record.valid else record for record in bundle.records]
    save_dataset(personal, records, bundle.features, dict(bundle.metadata, chosen_hand="Left"))
    with pytest.raises(ValueError, match="Right hand"):
        freeze_config(config, tmp_path / "hand" / "frozen.json")

    config, _, personal, _ = paired_fixture(tmp_path / "same-role-duplicates")
    bundle = load_dataset(personal)
    features = bundle.features.copy()
    features[1] = features[0]
    save_dataset(personal, bundle.records, features, bundle.metadata)
    freeze_config(config, tmp_path / "same-role-duplicates" / "frozen.json")

    config, _, personal, _ = paired_fixture(tmp_path / "legacy")
    bundle = load_dataset(personal)
    metadata = dict(bundle.metadata)
    metadata.pop("pose_set_id")
    save_dataset(personal, bundle.records, bundle.features, metadata)
    frozen_payload = freeze_config(config, tmp_path / "legacy" / "frozen.json")
    assert "operator assertion" in frozen_payload["pose_set"]["operator_declaration"]

    config, _, personal, _ = paired_fixture(tmp_path / "custom")
    payload = json.loads(config.read_text(encoding="utf-8"))
    del payload["pose_set"]["descriptions"]["BOOKMARK"]
    write_json(config, payload)
    with pytest.raises(ValueError, match="pose descriptions"):
        freeze_config(config, tmp_path / "custom" / "frozen.json")

    config, _, _, _ = paired_fixture(tmp_path / "bad-pose-id")
    payload = json.loads(config.read_text(encoding="utf-8"))
    payload["pose_set"]["id"] = "bad/path"
    write_json(config, payload)
    with pytest.raises(ValueError, match="IDs must"):
        freeze_config(config, tmp_path / "bad-pose-id" / "frozen.json")


def test_all_invalid_positive_test_scores_unknown_without_hand_detection(tmp_path: Path) -> None:
    config, _, _, test = paired_fixture(tmp_path)
    frozen = tmp_path / "frozen.json"
    freeze_config(config, frozen)
    bundle = load_dataset(test)
    records = [
        replace(record, valid=False, feature_index=None, validity_reason="no hand", hand=None)
        for record in bundle.records
    ]
    save_dataset(test, records, np.empty((0, 60), dtype=np.float32), bundle.metadata)

    report = score_frozen(frozen, [test], tmp_path / "report.json")

    assert report["results"][0]["counts"]["invalid_or_missing_scheduled_slots"] == len(records)
    assert report["results"][0]["counts"]["classifier_rejected_samples"] == 0
    assert all(row["predicted_label"] == "UNKNOWN" for row in report["results"][0]["trial_predictions"])

    config, _, _, test = paired_fixture(tmp_path / "bad-hand")
    frozen = tmp_path / "bad-hand" / "frozen.json"
    freeze_config(config, frozen)
    bundle = load_dataset(test)
    save_dataset(test, bundle.records, bundle.features, dict(bundle.metadata, chosen_hand="Middle"))
    with pytest.raises(ValueError, match="Left or Right"):
        score_frozen(frozen, [test], tmp_path / "bad-hand" / "report.json")


def test_score_rejects_changed_frozen_integrity_and_preserves_existing_output(tmp_path: Path) -> None:
    config, _, _, test = paired_fixture(tmp_path)
    frozen = tmp_path / "frozen.json"
    output = tmp_path / "report.json"
    freeze_config(config, frozen)
    data = json.loads(frozen.read_text(encoding="utf-8"))
    data["target_participant"] = "P03"
    frozen.write_text(json.dumps(data, allow_nan=False), encoding="utf-8")
    with pytest.raises(ValueError, match="integrity"):
        score_frozen(frozen, [test], output)
    assert not output.exists()

    frozen.unlink()
    freeze_config(config, frozen)
    output.write_text("keep me", encoding="utf-8")
    with pytest.raises(FileExistsError):
        score_frozen(frozen, [test], output)
    assert output.read_text(encoding="utf-8") == "keep me"


def test_cli_freeze_and_score_write_json_without_overwrite(tmp_path: Path) -> None:
    config, _, _, test = paired_fixture(tmp_path)
    frozen = tmp_path / "frozen.json"
    report = tmp_path / "report.json"
    freeze_cmd = [sys.executable, "-m", "gestureforge.paired_evaluate", "freeze",
                  "--config", str(config), "--output", str(frozen)]
    score_cmd = [sys.executable, "-m", "gestureforge.paired_evaluate", "score",
                 "--frozen", str(frozen), "--test", str(test), "--output", str(report)]

    assert subprocess.run(freeze_cmd, capture_output=True, text=True, check=False).returncode == 0
    assert subprocess.run(score_cmd, capture_output=True, text=True, check=False).returncode == 0
    repeated = subprocess.run(score_cmd, capture_output=True, text=True, check=False)

    assert repeated.returncode != 0
    assert "output already exists" in repeated.stderr
    assert json.loads(report.read_text(encoding="utf-8"))["claims"]["paired_positive_test_only"] is True


def test_multiple_train_manifests_allow_same_role_repeated_vectors(tmp_path: Path) -> None:
    config, _, personal, _ = paired_fixture(tmp_path)
    first = load_dataset(personal)
    second = make_dataset(tmp_path / "second-train", "P02", "train", seed=32)
    rows = [replace(row, session_id="second-session", trial_id="second-" + row.trial_id)
            for row in second.records]
    features = second.features.copy()
    features[0] = first.features[0]
    save_dataset(second.manifest_path, rows, features, second.metadata)
    data = json.loads(config.read_text(encoding="utf-8"))
    data["personal"]["manifests"].append(str(second.manifest_path))
    write_json(config, data)
    freeze_config(config, tmp_path / "frozen.json")


def test_all_invalid_negative_development_retained_without_training(tmp_path: Path) -> None:
    config, _, _, test = paired_fixture(tmp_path)
    records = [SampleRecord("P02", "negative-session", "negative-trial", "UNKNOWN",
                            "validation_negative", i, i * .2, False,
                            validity_reason="no hand", hand=None, provenance="synthetic")
               for i in range(5)]
    negative = save_dataset(tmp_path / "negative", records, np.empty((0, 60)),
                            {"chosen_hand": "Right", "pose_set_id": "standard-v1"})
    data = json.loads(config.read_text(encoding="utf-8"))
    data["personal"]["manifests"].append(str(negative.manifest_path))
    write_json(config, data)
    frozen = tmp_path / "frozen.json"
    pinned = freeze_config(config, frozen)
    result = score_frozen(frozen, [test], tmp_path / "results.json")
    assert len(pinned["models"]["personal"]["manifests"]) == 2
    assert result["results"][1]["train_samples"] == 40


def test_custom_vocabulary_and_absent_slots_are_scored_without_label_remapping(tmp_path: Path) -> None:
    from gestureforge.vocabulary import GestureVocabulary
    config, starter, personal, test = paired_fixture(tmp_path)
    vocabulary = GestureVocabulary(("G1", "G2", "G3"))
    labels = dict(zip(LABELS, vocabulary.labels, strict=True))
    for path in (starter, personal, test):
        bundle = load_dataset(path)
        rows = [replace(row, intended_label=labels[row.intended_label]) for row in bundle.records
                if not (path == test and row.intended_label == "BOOKMARK" and row.sample_index >= 2)]
        save_dataset(path, rows, bundle.features, bundle.metadata, vocabulary=vocabulary)
    data = json.loads(config.read_text(encoding="utf-8"))
    data["pose_set"]["descriptions"] = {labels[key]: value for key, value in POSE_DESCRIPTIONS.items()}
    write_json(config, data)
    frozen = tmp_path / "frozen.json"
    freeze_config(config, frozen)
    result = score_frozen(frozen, [test], tmp_path / "results.json")
    assert result["vocabulary"] == vocabulary.to_dict()
    for model in result["results"]:
        assert model["counts"]["absent_scheduled_slots"] == 3
        assert model["counts"]["invalid_or_missing_scheduled_slots"] == 6
        trial = next(row for row in model["trial_predictions"] if row["true_label"] == "G3")
        assert trial["predicted_label"] == "UNKNOWN"


def test_exclusive_publication_failure_cleans_temp_and_preserves_competing_report(tmp_path: Path, monkeypatch):
    import gestureforge.paired_evaluate as paired
    output = tmp_path / "report.json"
    def failed_link(source, target):
        raise OSError("disk refusal")
    monkeypatch.setattr(paired.os, "link", failed_link)
    with pytest.raises(OSError, match="disk refusal"):
        paired._write_json_exclusive(output, {"result": "test"})
    assert list(tmp_path.iterdir()) == []
    with pytest.raises(ValueError):
        paired._write_json_exclusive(output, {"non_finite": float("nan")})
    assert list(tmp_path.iterdir()) == []
    def competing_link(source, target):
        Path(target).write_text("other writer", encoding="utf-8")
        raise FileExistsError("competing writer")
    monkeypatch.setattr(paired.os, "link", competing_link)
    with pytest.raises(FileExistsError):
        paired._write_json_exclusive(output, {"result": "test"})
    assert output.read_text(encoding="utf-8") == "other writer"
    assert list(tmp_path.iterdir()) == [output]
