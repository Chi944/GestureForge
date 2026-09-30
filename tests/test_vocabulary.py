"""Software regression fixtures only; these are not participant measurements."""

from dataclasses import replace
import json
from types import SimpleNamespace

import numpy as np
import pytest

from gestureforge.contracts import LABELS
from gestureforge.dataset import load_dataset, merge_datasets, save_dataset
from gestureforge.evaluate import classification_metrics, evaluate_config, validation_negative_metrics
from gestureforge.fixtures import synthetic_dataset
from gestureforge.models import train_model
from gestureforge.vocabulary import GestureVocabulary, LEGACY_VOCABULARY


VOCABULARY = GestureVocabulary(("G1", "CUSTOM_2", "POSE3"))


def custom_bundle():
    baseline = synthetic_dataset(trials_per_label_per_split=2)
    mapping = dict(zip(LEGACY_VOCABULARY.action_ids, VOCABULARY.action_ids, strict=True))
    return replace(baseline, vocabulary=VOCABULARY, records=tuple(
        replace(record, intended_label=mapping.get(record.intended_label, record.intended_label))
        for record in baseline.records
    ))


@pytest.mark.parametrize("ids", [(), ("G1", "G2"), ("G1", "G1", "G3"),
                                ("UNKNOWN", "G2", "G3"), ("NEUTRAL", "G2", "G3"),
                                ("lower", "G2", "G3"), ("1A", "G2", "G3"),
                                ("A" * 65, "G2", "G3")])
def test_bad_vocabulary_rejected(ids):
    with pytest.raises(ValueError):
        GestureVocabulary(ids)


@pytest.mark.parametrize("version", [True, 2, "1"])
def test_unknown_vocabulary_version_rejected(version):
    with pytest.raises(ValueError):
        GestureVocabulary.from_mapping({"version": version, "action_ids": ["G1", "G2", "G3"]})


def test_legacy_manifest_round_trip_remains_version_one(tmp_path):
    bundle = synthetic_dataset(trials_per_label_per_split=2)
    saved = save_dataset(tmp_path, bundle.records, bundle.features, bundle.metadata)
    assert saved.manifest_path is not None
    manifest = json.loads(saved.manifest_path.read_text())
    assert manifest["schema_version"] == 1
    assert manifest["labels"] == list(LABELS)
    assert "vocabulary" not in manifest
    loaded = load_dataset(tmp_path)
    assert loaded.vocabulary == LEGACY_VOCABULARY
    assert loaded.records == bundle.records
    result = evaluate_config({"dataset_path": str(tmp_path), "algorithms": ["knn", "svm"]})
    assert all(set(row["metrics"]["per_class"]) == set(LABELS) for row in result["results"])


@pytest.mark.parametrize("algorithm", ["knn", "svm"])
def test_custom_labels_survive_save_train_predict_and_evaluate(tmp_path, algorithm):
    bundle = custom_bundle()
    saved = save_dataset(tmp_path, bundle.records, bundle.features, bundle.metadata,
                         vocabulary=VOCABULARY)
    loaded = load_dataset(tmp_path)
    assert loaded.vocabulary == VOCABULARY
    assert loaded.records == saved.records
    features, labels, records = loaded.training_data()
    model = train_model(features, labels, algorithm=algorithm, vocabulary=VOCABULARY,
                        groups=[r.trial_id for r in records])
    assert {model.predict(row)[0] for row in features} == set(VOCABULARY.labels)
    result = evaluate_config({"dataset_path": str(tmp_path), "algorithm": algorithm})["results"][0]
    assert set(result["metrics"]["per_class"]) == set(VOCABULARY.labels)
    assert {p["true_label"] for p in result["trial_predictions"]} == set(VOCABULARY.labels)
    assert result["metrics"]["macro_f1"] == 1.0


def test_unknown_never_trained_and_undeclared_labels_fail(tmp_path):
    bundle = custom_bundle()
    features, labels, _ = bundle.training_data()
    labels[0] = "UNKNOWN"
    with pytest.raises(ValueError, match="unknown labels"):
        train_model(features, labels, vocabulary=VOCABULARY)
    records = list(bundle.records)
    records[0] = replace(records[0], intended_label="UNKNOWN")
    with pytest.raises(ValueError, match="unknown intended label"):
        save_dataset(tmp_path, records, bundle.features, vocabulary=VOCABULARY)


def test_custom_unknown_misses_and_negative_acceptances_are_counted():
    metrics = classification_metrics([
        {"true_label": "G1", "predicted_label": "UNKNOWN"},
        {"true_label": "G1", "predicted_label": "G1"},
    ], VOCABULARY)
    assert metrics["per_class"]["G1"]["recall"] == 0.5
    negative = validation_negative_metrics([
        {"accepted": True, "raw_label": "CUSTOM_2"},
        {"accepted": True, "raw_label": "NEUTRAL"},
    ], VOCABULARY)
    assert negative["accepted_command_predictions"] == 1
    with pytest.raises(ValueError, match="outside selected vocabulary"):
        classification_metrics([{"true_label": "G1", "predicted_label": "OTHER"}], VOCABULARY)


def test_merge_rejects_different_vocabularies():
    with pytest.raises(ValueError, match="different gesture vocabularies"):
        merge_datasets([custom_bundle(), synthetic_dataset()])


def test_manifest_labels_cannot_disagree_with_vocabulary(tmp_path):
    bundle = custom_bundle()
    saved = save_dataset(tmp_path, bundle.records, bundle.features, vocabulary=VOCABULARY)
    assert saved.manifest_path is not None
    manifest = json.loads(saved.manifest_path.read_text())
    manifest["labels"] = list(LABELS)
    saved.manifest_path.write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="do not match"):
        load_dataset(tmp_path)


def test_project_model_revision_is_reproducible_and_sensitive_to_changes():
    features, labels, records = custom_bundle().training_data()
    groups = [r.trial_id for r in records]
    baseline = train_model(features, labels, vocabulary=VOCABULARY, groups=groups).model_version
    assert baseline == train_model(features.copy(), labels.copy(), vocabulary=VOCABULARY,
                                   groups=groups).model_version
    changed = features.copy()
    changed[0, 0] += 0.01
    assert baseline != train_model(changed, labels, vocabulary=VOCABULARY, groups=groups).model_version
    assert baseline != train_model(features, labels, multiplier=2, vocabulary=VOCABULARY,
                                   groups=groups).model_version
    assert baseline != train_model(features, labels, algorithm="svm", vocabulary=VOCABULARY,
                                   groups=groups).model_version


def test_custom_split_leakage_and_nonfinite_data_rejected(tmp_path):
    bundle = custom_bundle()
    records = list(bundle.records)
    records[1] = replace(records[1], split="validation")
    with pytest.raises(ValueError, match="multiple splits"):
        save_dataset(tmp_path, records, bundle.features, vocabulary=VOCABULARY)
    features = bundle.features.copy()
    features[0, 0] = np.nan
    with pytest.raises(ValueError, match="non-finite"):
        save_dataset(tmp_path, bundle.records, features, vocabulary=VOCABULARY)


def test_collector_uses_custom_ids_without_opening_real_camera(tmp_path, monkeypatch):
    from gestureforge import collect

    vocabulary_path = tmp_path / "vocabulary.json"
    vocabulary_path.write_text(json.dumps(VOCABULARY.to_dict()))
    args = SimpleNamespace(output=tmp_path / "data", vocabulary=vocabulary_path,
                           participant="P02", hand="Right", split="train", setup="synthetic",
                           camera=0, asset=None, trials=1)
    titles = []

    class FakeCamera:
        def __init__(self, *args):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def read(self):
            return None, None

    monkeypatch.setattr(collect, "HandCamera", FakeCamera)
    monkeypatch.setattr(collect, "show", lambda frame, title, instruction: titles.append(title))
    monkeypatch.setattr(collect.cv2, "waitKey", lambda _: ord("q"))
    monkeypatch.setattr(collect.cv2, "destroyAllWindows", lambda: None)
    collect.collect_trials(args)
    assert titles == ["G1 | trial 1/1"]
    assert not (tmp_path / "data" / "manifest.json").exists()


def test_invalid_custom_validation_slots_are_unknown_misses(tmp_path):
    bundle = custom_bundle()
    # Keep feature rows in place, but mark one complete validation trial invalid.
    target = next(r.trial_id for r in bundle.records
                  if r.split == "validation" and r.intended_label == "G1")
    records = tuple(replace(r, valid=False, feature_index=None, validity_reason="no_hand")
                    if r.trial_id == target else r for r in bundle.records)
    save_dataset(tmp_path, records, bundle.features, vocabulary=VOCABULARY)
    result = evaluate_config({"dataset_path": str(tmp_path)})["results"][0]
    assert result["metrics"]["confusion"]["G1"]["UNKNOWN"] == 1
    assert result["metrics"]["per_class"]["G1"]["recall"] == 0.5
