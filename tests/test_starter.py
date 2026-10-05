from __future__ import annotations

from dataclasses import replace
from hashlib import sha256
import json

import numpy as np
import pytest

from gestureforge import starter
from gestureforge.contracts import LABELS
from gestureforge.dataset import DatasetBundle, SampleRecord, save_dataset
from gestureforge.models import train_model
from gestureforge.vocabulary import LEGACY_VOCABULARY


SETTINGS = {
    "algorithm": "svm",
    "knn_k": 3,
    "knn_weights": "uniform",
    "svm_c": 2.0,
    "svm_gamma": 0.2,
    "multiplier": 1.7,
    "margin": 1.2,
}


def test_default_starter_is_disabled(monkeypatch, tmp_path):
    monkeypatch.setattr(starter, "APPROVED_RELEASE_SHA256", "")
    monkeypatch.setattr(starter, "RELEASE_PATH", tmp_path / "release.json")

    reason = starter.unavailable_reason()
    assert reason is not None and "no approved starter" in reason
    with pytest.raises(ValueError, match="no approved"):
        starter.load_starter()


def test_real_release_rebuilds_from_reviewed_train_rows(monkeypatch, tmp_path):
    release = write_release(tmp_path, SETTINGS)
    patch_release(monkeypatch, release)

    model, hand, profile, vocabulary = starter.load_starter()

    assert hand == "Right"
    assert profile == "standard-guest"
    assert vocabulary == LEGACY_VOCABULARY
    assert model.config.algorithm == "svm"
    assert model.config.multiplier == 1.7
    assert model.config.margin == 1.2
    assert model.config.rejection_reference == "leave_one_trial_out"
    assert model.model_version == release["model_version"]


def test_descriptor_parses_the_exact_approved_bytes(monkeypatch, tmp_path):
    release = write_release(tmp_path, SETTINGS)
    descriptor_bytes = release["descriptor"].read_bytes()
    monkeypatch.setattr(starter, "RELEASE_PATH", release["descriptor"])
    monkeypatch.setattr(starter, "APPROVED_RELEASE_SHA256", sha256(descriptor_bytes).hexdigest())

    def read_then_mutate(path, limit, label):
        raw = json.loads(release["descriptor"].read_text())
        raw["hand"] = "Left"
        release["descriptor"].write_text(json.dumps(raw, sort_keys=True), encoding="utf-8")
        return descriptor_bytes

    monkeypatch.setattr(starter, "_read_bytes", read_then_mutate)

    assert starter.load_starter()[1] == "Right"


@pytest.mark.parametrize("field", ["schema_version", "feature_version"])
def test_descriptor_rejects_bool_versions(monkeypatch, tmp_path, field):
    release = write_release(tmp_path, SETTINGS)
    raw = json.loads(release["descriptor"].read_text())
    raw[field] = True
    release["descriptor"].write_text(json.dumps(raw, sort_keys=True), encoding="utf-8")
    patch_release(monkeypatch, release)

    with pytest.raises(ValueError, match="unsupported .* version"):
        starter.load_starter()


def test_invalid_train_detections_can_remain_outside_training(monkeypatch, tmp_path):
    def retain_invalid(records):
        failed = replace(
            records[0],
            trial_id="P01-NEXT-invalid",
            valid=False,
            feature_index=None,
            hand=None,
            validity_reason="no_hand",
        )
        return records + (failed,)

    release = write_release(tmp_path, SETTINGS, mutate_records=retain_invalid)
    patch_release(monkeypatch, release)

    assert starter.load_starter()[2] == "standard-guest"


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (lambda paths: paths["descriptor"].write_text(paths["descriptor"].read_text() + "\n"), "hash mismatch"),
        (lambda paths: paths["manifest"].write_text(paths["manifest"].read_text() + "\n"), "manifest hash"),
        (lambda paths: paths["sidecar"].write_bytes(paths["sidecar"].read_bytes() + b"x"), "sidecar hash"),
    ],
)
def test_tampering_is_rejected(monkeypatch, tmp_path, mutate, message):
    release = write_release(tmp_path, SETTINGS)
    patch_release(monkeypatch, release)
    mutate(release)

    with pytest.raises(ValueError, match=message):
        starter.load_starter()


def test_json_approved_flag_does_not_enable_unpinned_release(monkeypatch, tmp_path):
    release = write_release(tmp_path, SETTINGS)
    raw = json.loads(release["descriptor"].read_text())
    raw["approved"] = True
    release["descriptor"].write_text(json.dumps(raw, sort_keys=True), encoding="utf-8")
    monkeypatch.setattr(starter, "RELEASE_PATH", release["descriptor"])
    monkeypatch.setattr(starter, "APPROVED_RELEASE_SHA256", "")

    reason = starter.unavailable_reason()
    assert reason is not None and "no approved starter" in reason
    with pytest.raises(ValueError, match="no approved"):
        starter.load_starter()


def test_validation_rows_are_refused(monkeypatch, tmp_path):
    release = write_release(tmp_path, SETTINGS, split="validation")
    patch_release(monkeypatch, release)

    with pytest.raises(ValueError, match="TRAIN-only"):
        starter.load_starter()


@pytest.mark.parametrize(
    ("change", "message"),
    [
        (lambda records: tuple(replace(r, participant_id="../P01") if r.participant_id == "P01" else r for r in records), "IDs"),
        (lambda records: tuple(r for r in records if not (r.participant_id == "P03" and r.intended_label == "NEXT")), "every standard label"),
        (lambda records: tuple(replace(r, provenance="synthetic") for r in records), "human provenance"),
        (lambda records: tuple(replace(r, hand="Left") for r in records), "Right hand"),
    ],
)
def test_release_record_errors_are_rejected(monkeypatch, tmp_path, change, message):
    release = write_release(tmp_path, SETTINGS, mutate_records=change)
    patch_release(monkeypatch, release)

    with pytest.raises(ValueError, match=message):
        starter.load_starter()


def test_missing_descriptor_reports_unavailable(monkeypatch, tmp_path):
    descriptor = tmp_path / "release.json"
    monkeypatch.setattr(starter, "RELEASE_PATH", descriptor)
    monkeypatch.setattr(starter, "APPROVED_RELEASE_SHA256", "0" * 64)

    reason = starter.unavailable_reason()
    assert reason is not None and "missing" in reason


def write_release(tmp_path, settings, *, split="train", mutate_records=None):
    bundle = release_bundle(split=split)
    records = mutate_records(bundle.records) if mutate_records else bundle.records
    saved = save_dataset(
        tmp_path / "manifest.json",
        records,
        bundle.features,
        {"chosen_hand": "Right", "warning": "GENERATED SOFTWARE TEST ONLY"},
    )
    assert saved.manifest_path is not None
    features, labels, training_records = saved.training_data()
    try:
        model_version = train_model(
            features,
            labels,
            settings["algorithm"],
            settings["multiplier"],
            settings["margin"],
            groups=[record.trial_id for record in training_records],
            vocabulary=LEGACY_VOCABULARY,
            knn_k=settings["knn_k"],
            knn_weights=settings["knn_weights"],
            svm_c=settings["svm_c"],
            svm_gamma=settings["svm_gamma"],
        ).model_version
    except ValueError:
        model_version = "gesture-v1-" + "0" * 32
    manifest = saved.manifest_path
    raw_manifest = json.loads(manifest.read_text())
    sidecar = manifest.with_name(raw_manifest["feature_file"])
    descriptor = tmp_path / "release.json"
    descriptor.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "feature_version": 1,
                "manifest_file": manifest.name,
                "manifest_sha256": sha256(manifest.read_bytes()).hexdigest(),
                "hand": "Right",
                "settings": settings,
                "model_version": model_version,
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    return {
        "descriptor": descriptor,
        "manifest": manifest,
        "sidecar": sidecar,
        "model_version": model_version,
    }


def patch_release(monkeypatch, release):
    monkeypatch.setattr(starter, "RELEASE_PATH", release["descriptor"])
    monkeypatch.setattr(
        starter,
        "APPROVED_RELEASE_SHA256",
        sha256(release["descriptor"].read_bytes()).hexdigest(),
    )


def release_bundle(*, split="train"):
    rng = np.random.default_rng(304)
    features = []
    records = []
    timestamp = 0.0
    for participant_index, participant in enumerate(("P01", "P02", "P03")):
        for label_index, label in enumerate(LABELS):
            center = np.zeros(60, dtype=np.float32)
            center[label_index * 12: label_index * 12 + 12] = 1 + label_index
            center[48 + participant_index] = participant_index + 1
            trial_id = f"{participant}-{label}"
            for sample_index in range(5):
                features.append(center + rng.normal(0, 0.01, 60).astype(np.float32))
                records.append(
                    {
                        "participant_id": participant,
                        "session_id": f"{participant}-{split}",
                        "trial_id": trial_id,
                        "intended_label": label,
                        "split": split,
                        "sample_index": sample_index,
                        "timestamp": timestamp,
                        "valid": True,
                        "feature_index": len(features) - 1,
                        "validity_reason": "",
                        "hand": "Right",
                        "provenance": "human",
                    }
                )
                timestamp += 0.1
    return DatasetBundle(
        manifest_path=None,
        records=tuple(SampleRecord.from_mapping(record) for record in records),
        features=np.asarray(features, dtype=np.float32),
        metadata={"chosen_hand": "Right"},
    )
