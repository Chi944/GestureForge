import numpy as np
import pytest

from gestureforge.contracts import LABELS
from gestureforge.fixtures import synthetic_dataset
from gestureforge.models import train_model


def test_train_model_knn_predicts_synthetic_validation_samples() -> None:
    bundle = synthetic_dataset(trials_per_label_per_split=2)
    train_features, train_labels, _ = bundle.training_data()
    validation_features, validation_labels, _ = bundle.validation_data()

    model = train_model(train_features, train_labels, algorithm="knn")
    predictions = [model.predict(feature) for feature in validation_features]

    assert model.model_version == "prototype-v1"
    assert [label for label, _, _ in predictions] == validation_labels.tolist()
    assert sum(accepted for _, accepted, _ in predictions) >= int(len(predictions) * 0.8)


def test_train_model_svm_uses_supported_labels() -> None:
    bundle = synthetic_dataset(trials_per_label_per_split=2)
    train_features, train_labels, _ = bundle.training_data()

    model = train_model(train_features, train_labels, algorithm="svm")

    config = model.to_config()
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
