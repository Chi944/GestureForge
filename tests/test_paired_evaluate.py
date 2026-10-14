import json
import shutil
import subprocess
import sys
from dataclasses import replace
from pathlib import Path
from zipfile import ZipFile

import numpy as np
import pytest

from gestureforge.contracts import LABELS
from gestureforge.dataset import SampleRecord, load_dataset, save_dataset
from gestureforge.paired_evaluate import freeze_config, score_frozen
from gestureforge.paired_evaluate import browser_test_ticket, _stable_hash, _without_keys
from gestureforge.import_participant import import_browser_zip, MODEL_SHA256, RETENTION


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


@pytest.fixture
def browser_test_fixture(tmp_path):
    """Fabricated data exercise the human import route; no participant data are used."""
    config, starter, personal, _ = paired_fixture(tmp_path)
    for path in (starter, personal):
        bundle = load_dataset(path)
        save_dataset(path, [replace(row, provenance="human") for row in bundle.records],
                     bundle.features, dict(bundle.metadata, provenance="human"))
    frozen = tmp_path / "frozen.json"
    freeze_config(config, frozen)
    ticket = browser_test_ticket(frozen)
    session = f"P02-test-{ticket['config_fingerprint'][:32]}"
    records: list[dict[str, object]] = []
    for label in LABELS:
        for trial in range(1, 13):
            for sample in range(5):
                records.append({
                    "session_id": session, "trial_id": f"test-{label}-{trial:02d}",
                    "split": "test", "intended_label": label, "sample_index": sample,
                    "timestamp": float(len(records)), "frame_id": None, "hand_count": 0,
                    "hand": None, "landmarks": None, "validity_reason": "paused_before_sample",
                })
    payload = {
        "schema_version": 1, "protocol": ticket["protocol"], "test_ticket": ticket,
        "participant_id": "P02", "hand": "Right",
        "source": {"runtime": "mediapipe-tasks-vision-web", "version": "1.1.0", "model_sha256": MODEL_SHA256},
        "consent": {"numeric_data": True, "team_and_marker_access": True, "retention": RETENTION,
                    "recorded_at": "2026-10-14T00:00:00Z"},
        "sessions": [{"session_id": session, "split": "test", "started_at": "2026-10-14T00:00:01Z",
                      "conditions": "software fixture"}], "records": records,
    }
    return frozen, payload


def write_browser_zip(tmp_path, payload):
    zip_path = tmp_path / "return.zip"
    with ZipFile(zip_path, "w") as archive:
        archive.writestr("collection.json", json.dumps(payload))
    return zip_path


def test_browser_partial_import_retains_invalid_slots_but_cannot_be_scored(browser_test_fixture, tmp_path):
    frozen, payload = browser_test_fixture
    payload["records"] = payload["records"][:5]
    bundle = import_browser_zip(write_browser_zip(tmp_path, payload), tmp_path / "partial", frozen=frozen)
    assert len(bundle.records) == 5 and len(bundle.features) == 0
    assert bundle.metadata["browser_collection"]["import_status"] == "partial"
    assert {row.validity_reason for row in bundle.records} == {"paused_before_sample"}
    with pytest.raises(ValueError, match="48 planned trials"):
        score_frozen(frozen, [bundle.manifest_path], tmp_path / "report.json")


@pytest.mark.parametrize("change", ["missing-freeze", "wrong-person", "wrong-fingerprint", "wrong-integrity",
                                    "wrong-protocol", "mixed-splits", "development-relabel", "wrong-session", "dev-with-freeze"])
def test_browser_test_import_rejects_mismatches(browser_test_fixture, tmp_path, change):
    frozen, payload = browser_test_fixture
    if change == "wrong-person":
        payload["participant_id"] = "P03"
    elif change == "wrong-fingerprint":
        payload["test_ticket"]["config_fingerprint"] = "0" * 64
    elif change == "wrong-integrity":
        payload["test_ticket"]["frozen_integrity_sha256"] = "0" * 64
    elif change == "wrong-protocol":
        payload["test_ticket"]["paired_protocol"] = "other"
    elif change == "mixed-splits":
        payload["records"][0]["split"] = "train"
    elif change == "development-relabel":
        payload["records"][0]["trial_id"] = "train-NEXT-01"
    elif change == "wrong-session":
        payload["sessions"][0]["session_id"] = "P02-test"
    elif change == "dev-with-freeze":
        payload["protocol"] = "gestureforge-browser-development-v1"
        del payload["test_ticket"]
    with pytest.raises(ValueError):
        import_browser_zip(write_browser_zip(tmp_path, payload), tmp_path / "bad",
                           frozen=None if change == "missing-freeze" else frozen)
    assert not (tmp_path / "bad" / "manifest.json").exists()


@pytest.mark.parametrize("change", ["ticket", "source", "partial", "trial-identity"])
def test_browser_scoring_rechecks_binding_and_actual_coverage(browser_test_fixture, tmp_path, change):
    frozen, payload = browser_test_fixture
    bundle = import_browser_zip(write_browser_zip(tmp_path, payload), tmp_path / "imported", frozen=frozen)
    rows = list(bundle.records)
    metadata = bundle.metadata
    if change == "ticket":
        metadata["browser_collection"]["test_ticket"]["config_fingerprint"] = "0" * 64
    elif change == "source":
        metadata["import_source"] = "native"
    elif change == "partial":
        rows = rows[:-5]
    else:
        rows = [replace(row, trial_id="relabelled-trial") if row.trial_id == rows[0].trial_id else row for row in rows]
    save_dataset(bundle.manifest_path, rows, bundle.features, metadata)
    with pytest.raises(ValueError, match="browser TEST"):
        score_frozen(frozen, [bundle.manifest_path], tmp_path / "report.json")


def test_browser_ticket_checks_both_frozen_hashes_and_supported_contract(browser_test_fixture):
    frozen, _ = browser_test_fixture
    original = json.loads(frozen.read_text(encoding="utf-8"))
    changed = dict(original, config_fingerprint="0" * 64)
    changed["integrity_sha256"] = _stable_hash(_without_keys(changed, {"integrity_sha256"}))
    write_json(frozen, changed)
    with pytest.raises(ValueError, match="fingerprint"):
        browser_test_ticket(frozen)
    for field, value in [("target_participant", "P" * 25), ("hand", "Left"),
                         ("pose_set", {**original["pose_set"], "id": "other"})]:
        changed = dict(original, **{field: value})
        changed["config_fingerprint"] = _stable_hash(_without_keys(changed, {"config_fingerprint", "integrity_sha256"}))
        changed["integrity_sha256"] = _stable_hash(_without_keys(changed, {"integrity_sha256"}))
        write_json(frozen, changed)
        with pytest.raises(ValueError, match="browser TEST"):
            browser_test_ticket(frozen)
    changed = dict(original, pose_set={**original["pose_set"], "descriptions": {
        label: f"Operator description for {label}" for label in LABELS
    }})
    changed["config_fingerprint"] = _stable_hash(_without_keys(changed, {"config_fingerprint", "integrity_sha256"}))
    changed["integrity_sha256"] = _stable_hash(_without_keys(changed, {"integrity_sha256"}))
    write_json(frozen, changed)
    assert browser_test_ticket(frozen)["target_participant"] == "P02"


def test_actual_browser_test_export_imports_and_scores_same_freeze(browser_test_fixture, tmp_path):
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node.js is required for the browser interoperability check")
    frozen, payload = browser_test_fixture
    ticket_file = tmp_path / "ticket.json"
    write_json(ticket_file, payload["test_ticket"])
    script = tmp_path / "export.mjs"
    collector = (Path(__file__).resolve().parents[1] / "participant" / "collector.mjs").as_uri()
    script.write_text(f"""
import {{ makeCollection, makeTrialPlan, makeStoredZip, stampRecords, SampleScheduler, readOwnCollectionZip }} from {json.dumps(collector)};
import {{ readFileSync, writeFileSync }} from 'node:fs';
const testTicket = JSON.parse(readFileSync(process.argv[2], 'utf8'));
const participantId = testTicket.target_participant;
const records = makeTrialPlan(testTicket).flatMap((trial, index) => {{
  const scheduler = new SampleScheduler(trial, index * 3);
  if (index) for (let sample = 0; sample < 5; sample++) {{
    const timestamp = index * 3 + 0.2 + sample * 0.4 + 0.001;
    scheduler.due(timestamp, {{ timestamp, frame_id: index * 5 + sample, hand_count: 1, hand: 'Right',
      landmarks: Array.from({{ length: 21 }}, (_, point) => point === 9 ? [0, 1, 0] : [point / 100, point / 50, point / 25]) }});
  }}
  return stampRecords(scheduler.finalize('paused_before_sample'), participantId, testTicket);
}});
const collection = makeCollection({{ participantId, testTicket, trainConditions: 'software fixture',
  recordedAt: '2026-10-14T00:00:00Z', sessionStartedAt: {{ test: '2026-10-14T00:00:01Z' }}, records }});
const zip = makeStoredZip({{ 'collection.json': JSON.stringify(collection) }});
readOwnCollectionZip(zip, testTicket);
writeFileSync(process.argv[3], zip);
""", encoding="utf-8")
    zip_path = tmp_path / "EMAIL_THIS_P02_test.zip"
    subprocess.run([node, str(script), str(ticket_file), str(zip_path)], check=True)
    manifest = tmp_path / "imported" / "manifest.json"
    result = subprocess.run([sys.executable, "-m", "gestureforge.import_participant", str(zip_path),
                             "--output", str(manifest), "--frozen", str(frozen)],
                            check=True, capture_output=True, text=True)
    assert "Imported 240 records (235 valid features), status=complete" in result.stdout
    report = score_frozen(frozen, [manifest], tmp_path / "report.json")
    assert report["frozen"]["config_fingerprint"] == payload["test_ticket"]["config_fingerprint"]
    assert report["paired"]["same_test_record_order"] is True
    for result in report["results"]:
        assert result["test_trials"] == 48
        assert result["counts"]["invalid_or_missing_scheduled_slots"] == 5
