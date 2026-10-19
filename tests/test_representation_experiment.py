from dataclasses import replace
import json

import numpy as np
import pytest

from gestureforge import evaluate
from gestureforge.dataset import dataset_hashes
from gestureforge.evaluate import evaluate_algorithm
from gestureforge.fixtures import synthetic_dataset
from gestureforge.representation_experiment import compare_representations, main, palm_local
from gestureforge.vocabulary import GestureVocabulary


def development_bundle(participant="P67"):
    bundle = synthetic_dataset(trials_per_label_per_split=2)
    return replace(bundle, records=tuple(replace(r, participant_id=participant) for r in bundle.records))


def hand():
    points = np.random.default_rng(304).normal(size=(21, 3))
    points[0] = 0
    points[9] = [0, 1, 0]
    points[5] = [0.5, 0.8, 0.1]
    points[17] = [-0.5, 0.8, 0.1]
    return points[1:].ravel()


def test_rotation_invariance_and_no_mutation():
    row = hand()
    before = row.copy()
    rotation, _ = np.linalg.qr(np.random.default_rng(19).normal(size=(3, 3)))
    assert np.linalg.det(rotation) > 0
    actual = palm_local(row)
    assert actual.dtype == np.float32 and actual.shape == (60,)
    assert np.isfinite(actual).all()
    np.testing.assert_allclose(actual, palm_local((row.reshape(20, 3) @ rotation).ravel()), atol=1e-6)
    np.testing.assert_array_equal(row, before)


@pytest.mark.parametrize("row", [np.zeros(59), np.zeros((20, 3)), np.full(60, np.nan),
                                 np.full(60, np.inf)])
def test_invalid_input_shape_or_finiteness(row):
    with pytest.raises(ValueError, match="finite 60-value"):
        palm_local(row)


@pytest.mark.parametrize("axis", ["y", "x"])
def test_degenerate_palm(axis):
    row = hand().reshape(20, 3)
    if axis == "y":
        row[8] = [0, 1e-6, 0]
    else:
        row[4] = row[16] + [0, 0.5, 0]
    with pytest.raises(ValueError, match="degenerate_palm"):
        palm_local(row.ravel())


@pytest.mark.parametrize("participant,algorithm,margin", [("P67", "knn", 1.75), ("P1543", "svm", 1.25)])
def test_unchanged_baseline_and_source(participant, algorithm, margin):
    bundle = development_bundle(participant)
    before = bundle.features.copy()
    hashes = dataset_hashes(bundle)
    report = compare_representations(bundle)
    expected = evaluate_algorithm(bundle, algorithm, 2.5, margin)
    assert report["conditions"][0]["metrics"] == expected["metrics"]
    assert report["input_hashes"] == hashes == dataset_hashes(bundle)
    np.testing.assert_array_equal(before, bundle.features)
    encoded = json.dumps(report, allow_nan=False)
    assert '"trial_id"' not in encoded and '"model_version"' not in encoded
    assert report["conditions"][1]["representation"] == "palm-local-experiment-v1"


@pytest.mark.parametrize("bad", ["test", "left", "custom", "participant", "labels"])
def test_refuse_out_of_scope_before_fit(monkeypatch, bad):
    bundle = development_bundle()
    if bad == "test":
        bundle = replace(bundle, records=(*bundle.records, replace(bundle.records[0], split="test")))
    elif bad == "left":
        bundle = replace(bundle, records=(replace(bundle.records[0], hand="Left"), *bundle.records[1:]))
    elif bad == "custom":
        bundle = replace(bundle, vocabulary=GestureVocabulary(("G1", "G2", "G3")))
    elif bad == "labels":
        bundle = replace(bundle, records=(replace(bundle.records[0], intended_label="G1"), *bundle.records[1:]))
    else:
        bundle = replace(bundle, records=tuple(replace(r, participant_id="P69") for r in bundle.records))
    monkeypatch.setattr(evaluate, "train_model", lambda *a, **k: pytest.fail("fit occurred"))
    with pytest.raises(ValueError):
        compare_representations(bundle)


def test_retains_newly_degenerate_and_existing_invalid_slots_and_negatives():
    bundle = development_bundle()
    trial = next(r.trial_id for r in bundle.records if r.split == "validation")
    features = bundle.features.copy()
    records = list(bundle.records)
    for i, record in enumerate(records):
        if record.trial_id == trial:
            features[record.feature_index] = 0
            if record.sample_index == 0:
                records[i] = replace(record, valid=False, feature_index=None, validity_reason="no_hand")
    negative = replace(records[0], split="validation_negative", session_id="negative", trial_id="negative",
                       intended_label="UNKNOWN", feature_index=len(features))
    bundle = replace(bundle, records=(*records, negative), features=np.vstack((features, np.zeros(60))))
    baseline, transformed = compare_representations(bundle)["conditions"]
    assert baseline["splits"]["validation"]["invalid_slots"] == 1
    assert transformed["splits"]["validation"]["invalid_slots"] == 5
    assert baseline["splits"]["validation"]["scheduled_slots"] == transformed["splits"]["validation"]["scheduled_slots"] == 40
    label = next(r.intended_label for r in records if r.trial_id == trial)
    assert transformed["metrics"]["confusion"][label]["UNKNOWN"] >= 1
    assert transformed["metrics"]["validation_negative"]["samples"] == 1
    assert transformed["splits"]["validation_negative"]["invalid_slots"] == 1
    assert transformed["metrics"]["validation_negative"]["accepted_command_predictions"] == 0


def test_sparse_transformed_training_condition_unavailable():
    bundle = development_bundle()
    features = bundle.features.copy()
    trial = bundle.records[0].trial_id
    for record in bundle.records:
        if record.trial_id == trial:
            features[record.feature_index] = 0
    baseline, transformed = compare_representations(replace(bundle, features=features))["conditions"]
    assert baseline["status"] == "available"
    assert transformed["status"] == "unavailable"
    assert transformed["classes"] == [bundle.records[0].intended_label]
    assert transformed["splits"]["train"]["invalid_slots"] == 5
    assert "metrics" not in transformed


def test_training_only_and_whole_trial_calibration(monkeypatch):
    bundle = development_bundle()
    original = evaluate.train_model
    captured = []

    def tracked(features, labels, **kwargs):
        model = original(features, labels, **kwargs)
        groups = np.asarray(kwargs["groups"])
        assert set(groups) == {r.trial_id for r in bundle.records if r.split == "train"}
        np.testing.assert_allclose(model.scaler.mean_, np.mean(features.astype(np.float64), axis=0))
        for label in bundle.vocabulary.labels:
            rows = model.train_features_scaled[labels == label]
            trial_groups = groups[labels == label]
            distances = [np.min(np.linalg.norm(rows[trial_groups != trial_groups[i]] - row, axis=1))
                         for i, row in enumerate(rows)]
            assert model.thresholds[label] == pytest.approx(float(np.quantile(distances, .95)) * 2.5)
        captured.append(model)
        return model

    monkeypatch.setattr(evaluate, "train_model", tracked)
    compare_representations(bundle)
    assert len(captured) == 2


def test_output_preservation_before_load(tmp_path):
    target = tmp_path / "keep.json"
    target.write_text("keep", encoding="utf-8")
    with pytest.raises(SystemExit):
        main([str(tmp_path / "missing.json"), "--output", str(target)])
    assert target.read_text(encoding="utf-8") == "keep"


def test_output_race_cannot_overwrite(tmp_path, monkeypatch):
    from gestureforge import representation_experiment

    target = tmp_path / "fresh.json"
    monkeypatch.setattr(representation_experiment, "load_dataset", lambda _: development_bundle())

    def competing_writer(bundle):
        target.write_text("another result", encoding="utf-8")
        return {"status": "test"}

    monkeypatch.setattr(representation_experiment, "compare_representations", competing_writer)
    with pytest.raises(FileExistsError):
        main(["unused.json", "--output", str(target)])
    assert target.read_text(encoding="utf-8") == "another result"
