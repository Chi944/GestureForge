from typing import Any, cast

import numpy as np
import pytest

from gestureforge.contracts import LABELS
from gestureforge.fixtures import synthetic_dataset
from gestureforge.models import class_distance_thresholds, train_model


def test_candidate_hyperparameters_change_revision() -> None:
    from gestureforge.vocabulary import LEGACY_VOCABULARY

    bundle = synthetic_dataset(trials_per_label_per_split=2)
    train_features, train_labels, _ = bundle.training_data()
    base = train_model(train_features, train_labels, vocabulary=LEGACY_VOCABULARY)
    tuned = train_model(train_features, train_labels, vocabulary=LEGACY_VOCABULARY,
                        knn_k=3, knn_weights='uniform')
    assert base.model_version != tuned.model_version
    assert tuned.estimator.get_params()['n_neighbors'] == 3
    assert tuned.estimator.get_params()['weights'] == 'uniform'
    assert train_model(train_features, train_labels, knn_k=3).model_version != 'prototype-v2'


def test_reject_invalid_candidate_hyperparameters() -> None:
    bundle = synthetic_dataset(trials_per_label_per_split=2)
    train_features, train_labels, _ = bundle.training_data()
    with pytest.raises(ValueError, match='knn_k'):
        train_model(train_features, train_labels, knn_k=0)
    with pytest.raises(ValueError, match='svm_c'):
        train_model(train_features, train_labels, svm_c=0)
    with pytest.raises(ValueError, match='svm_gamma'):
        train_model(train_features, train_labels, svm_gamma=-0.1)


def test_default_svm_keeps_existing_saved_profile_revision(monkeypatch) -> None:
    from sklearn.svm import SVC
    from gestureforge import models
    from gestureforge.vocabulary import LEGACY_VOCABULARY

    bundle = synthetic_dataset(trials_per_label_per_split=2)
    features, labels, records = bundle.training_data()
    groups = [r.trial_id for r in records]
    current = train_model(features, labels, algorithm='svm', vocabulary=LEGACY_VOCABULARY, groups=groups)
    # The pre-search implementation used an integer C; JSON hashes distinguish 1.0.
    monkeypatch.setattr(models, '_make_estimator', lambda *args: SVC(C=1, gamma='scale', kernel='rbf'))
    previous = train_model(features, labels, algorithm='svm', vocabulary=LEGACY_VOCABULARY, groups=groups)
    assert current.model_version == previous.model_version


def test_train_model_knn_predicts_synthetic_validation_samples() -> None:
    bundle = synthetic_dataset(trials_per_label_per_split=2)
    train_features, train_labels, _ = bundle.training_data()
    validation_features, validation_labels, _ = bundle.validation_data()

    model = train_model(train_features, train_labels, algorithm="knn")
    predictions = [model.predict(feature) for feature in validation_features]

    assert model.model_version == "prototype-v2"
    assert [label for label, _, _ in predictions] == validation_labels.tolist()
    assert sum(accepted for _, accepted, _ in predictions) >= int(len(predictions) * 0.8)


def test_train_model_svm_uses_supported_labels() -> None:
    bundle = synthetic_dataset(trials_per_label_per_split=2)
    train_features, train_labels, _ = bundle.training_data()

    model = train_model(train_features, train_labels, algorithm="svm")

    config = cast(dict[str, Any], model.to_config())
    assert config["algorithm"] == "svm"
    assert set(config["labels"]) == set(LABELS)
    assert config["estimator_params"]["C"] == 1
    assert config["estimator_params"]["gamma"] == "scale"
    assert "scikit-learn" in config["library_versions"]
    assert config["timing"]["fit_seconds"] >= config["timing"]["estimator_fit_seconds"]


def test_model_rejects_far_pose_by_distance() -> None:
    bundle = synthetic_dataset(trials_per_label_per_split=2)
    train_features, train_labels, _ = bundle.training_data()
    model = train_model(train_features, train_labels, algorithm="knn", multiplier=1.0)

    label, accepted, reason = model.predict(np.full(60, 99.0, dtype=np.float32))

    assert label in LABELS
    assert not accepted
    assert reason == "distance_rejection"


def test_model_rejects_ambiguous_pose_by_margin() -> None:
    features = []
    labels = []
    for label, base in (("NEXT", 0.0), ("PREVIOUS", 10.0), ("BOOKMARK", 0.3), ("NEUTRAL", 20.0)):
        for offset in (0.0, 0.03, 0.06):
            row = np.zeros(60, dtype=np.float32)
            row[0] = base + offset
            features.append(row)
            labels.append(label)
    model = train_model(
        np.asarray(features),
        np.asarray(labels, dtype=object),
        multiplier=10.0,
        margin=1.2,
    )
    ambiguous = np.zeros(60, dtype=np.float32)
    ambiguous[0] = 0.18

    label, accepted, reason = model.predict(ambiguous)

    assert model.model_version == "prototype-v3"
    assert label in {"NEXT", "BOOKMARK"}
    assert not accepted
    assert reason == "margin_rejection"


def test_train_model_requires_all_four_labels() -> None:
    features = np.ones((5, 60), dtype=np.float32)
    labels = np.asarray(["NEXT", "NEXT", "PREVIOUS", "PREVIOUS", "BOOKMARK"], dtype=object)

    with pytest.raises(ValueError, match="all four labels"):
        train_model(features, labels, algorithm="knn")


def test_train_model_requires_two_samples_per_label() -> None:
    features = np.ones((7, 60), dtype=np.float32)
    labels = np.asarray(
        ["NEXT", "NEXT", "PREVIOUS", "PREVIOUS", "BOOKMARK", "BOOKMARK", "NEUTRAL"],
        dtype=object,
    )

    with pytest.raises(ValueError, match="at least 2 samples per label"):
        train_model(features, labels, algorithm="svm")


def test_train_model_rejects_non_1d_labels() -> None:
    features = np.ones((8, 60), dtype=np.float32)
    labels = np.asarray(
        [["NEXT"], ["NEXT"], ["PREVIOUS"], ["PREVIOUS"], ["BOOKMARK"], ["BOOKMARK"], ["NEUTRAL"], ["NEUTRAL"]]
    )

    with pytest.raises(ValueError, match="one-dimensional"):
        train_model(features, labels)


def test_train_model_rejects_invalid_multiplier() -> None:
    bundle = synthetic_dataset(trials_per_label_per_split=2)
    train_features, train_labels, _ = bundle.training_data()

    with pytest.raises(ValueError, match="finite and positive"):
        train_model(train_features, train_labels, multiplier=0)


def test_train_model_rejects_invalid_margin() -> None:
    bundle = synthetic_dataset(trials_per_label_per_split=2)
    train_features, train_labels, _ = bundle.training_data()

    with pytest.raises(ValueError, match="at least 1.0"):
        train_model(train_features, train_labels, margin=0.99)


def test_rejection_reference_excludes_all_frames_from_the_same_hold():
    rows = np.asarray([[0.0], [0.01], [10.0], [10.01]])
    labels = np.asarray(["NEXT"] * 4)
    groups = ["hold-a", "hold-a", "hold-b", "hold-b"]
    thresholds = class_distance_thresholds(rows, labels, 1.0, groups=groups)
    assert thresholds["NEXT"] == pytest.approx(10.0)


def test_grouped_training_requires_independent_trials_for_each_label():
    bundle = synthetic_dataset(trials_per_label_per_split=1)
    features, labels, records = bundle.training_data()
    with pytest.raises(ValueError, match="at least 2 training trials"):
        train_model(features, labels, groups=[r.trial_id for r in records])


def test_training_rejects_misaligned_trial_ids():
    bundle = synthetic_dataset(trials_per_label_per_split=2)
    features, labels, _ = bundle.training_data()
    with pytest.raises(ValueError, match="groups must have one trial ID per sample"):
        train_model(features, labels, groups=["one-id"])

@pytest.mark.parametrize("algorithm", ["knn", "svm"])
@pytest.mark.parametrize("margin", [1.0, 1.5])
def test_opt_in_diagnostics_preserve_decisions_and_revision(algorithm, margin):
    bundle = synthetic_dataset(trials_per_label_per_split=2)
    features, labels, _ = bundle.training_data()
    model = train_model(features, labels, algorithm=algorithm, margin=margin)
    revision = model.model_version
    for feature in (features[0], features[0] + 100):
        plain = model.predict_one(feature)
        detail = model.predict_one(feature, diagnostics=True)
        assert plain.as_tuple() == detail.as_tuple()
        assert plain.distance == detail.distance and plain.threshold == detail.threshold
        assert plain.diagnostics is None
        assert detail.diagnostics is not None
        assert set(detail.diagnostics) == {"distance", "threshold", "competitor_distance", "competitor_ratio"}
        assert all(value is None or np.isfinite(value) for value in detail.diagnostics.values())
    assert model.model_version == revision

def test_diagnostic_nulls_and_default_avoid_extra_competitor_work(monkeypatch):
    import gestureforge.models as models_module
    bundle = synthetic_dataset(trials_per_label_per_split=2)
    features, labels, _ = bundle.training_data()
    model = train_model(features, labels, margin=1.0)
    original = models_module.np.linalg.norm
    calls = []
    def norm(*args, **kwargs):
        calls.append(True)
        return original(*args, **kwargs)
    monkeypatch.setattr(models_module.np.linalg, "norm", norm)
    model.predict_one(features[0])
    assert len(calls) == 1
    calls.clear()
    model.thresholds[str(labels[0])] = float("inf")
    diagnostic = model.predict_one(features[0], diagnostics=True)
    assert len(calls) == 2
    assert diagnostic.diagnostics is not None
    assert diagnostic.diagnostics["threshold"] is None
