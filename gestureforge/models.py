"""Prototype classifiers and training-only rejection rules."""

from __future__ import annotations

from dataclasses import dataclass
from importlib.metadata import version
from time import perf_counter
from typing import Literal

import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from .contracts import LABELS

Algorithm = Literal["knn", "svm"]
MODEL_VERSION = "prototype-v1"


@dataclass(frozen=True)
class ModelConfig:
    algorithm: Algorithm = "knn"
    multiplier: float = 1.5
    model_version: str = MODEL_VERSION


@dataclass(frozen=True)
class PredictionResult:
    label: str
    accepted: bool
    reason: str = ""
    distance: float | None = None
    threshold: float | None = None

    def as_tuple(self) -> tuple[str, bool, str]:
        return (self.label, self.accepted, self.reason)


class PrototypeGestureModel:
    def __init__(
        self,
        estimator: KNeighborsClassifier | SVC,
        scaler: StandardScaler,
        train_features_scaled: np.ndarray,
        train_labels: np.ndarray,
        thresholds: dict[str, float],
        config: ModelConfig,
        fit_seconds: float,
        estimator_fit_seconds: float,
        threshold_seconds: float,
    ) -> None:
        self.estimator = estimator
        self.scaler = scaler
        self.train_features_scaled = train_features_scaled
        self.train_labels = train_labels
        self.thresholds = thresholds
        self.config = config
        self.fit_seconds = fit_seconds
        self.estimator_fit_seconds = estimator_fit_seconds
        self.threshold_seconds = threshold_seconds
        self.model_version = config.model_version

    def predict(self, feature: np.ndarray) -> tuple[str, bool, str]:
        result = self.predict_one(feature)
        return result.as_tuple()

    def predict_one(self, feature: np.ndarray) -> PredictionResult:
        row = _coerce_feature_row(feature)
        scaled = self.scaler.transform(row.reshape(1, -1))
        label = str(self.estimator.predict(scaled)[0])
        class_rows = self.train_features_scaled[self.train_labels == label]
        if len(class_rows) == 0:
            return PredictionResult(label=label, accepted=False, reason="no_training_examples")
        distance = float(np.min(np.linalg.norm(class_rows - scaled, axis=1)))
        threshold = float(self.thresholds.get(label, np.inf))
        if distance > threshold:
            return PredictionResult(
                label=label,
                accepted=False,
                reason="distance_rejection",
                distance=distance,
                threshold=threshold,
            )
        return PredictionResult(label=label, accepted=True, distance=distance, threshold=threshold)

    def to_config(self) -> dict[str, object]:
        return {
            "algorithm": self.config.algorithm,
            "multiplier": self.config.multiplier,
            "model_version": self.model_version,
            "labels": sorted(set(str(label) for label in self.train_labels)),
            "thresholds": self.thresholds,
            "fit_seconds": self.fit_seconds,
            "timing": {
                "fit_seconds": self.fit_seconds,
                "estimator_fit_seconds": self.estimator_fit_seconds,
                "threshold_seconds": self.threshold_seconds,
            },
            "estimator_params": self.estimator.get_params(deep=False),
            "library_versions": _library_versions(),
        }


def train_model(
    features: np.ndarray,
    labels: np.ndarray | list[str],
    algorithm: Algorithm = "knn",
    multiplier: float = 1.5,
) -> PrototypeGestureModel:
    """Train the assignment's default kNN or SVM model.

    The scaler is fitted on training data only. The distance rejection thresholds
    are class-conditional 95th-percentile nearest-neighbour distances from the
    same scaled training data, multiplied by the configured prototype multiplier.
    """

    feature_matrix = _coerce_feature_matrix(features)
    label_vector = np.asarray(labels, dtype=object)
    if label_vector.ndim != 1:
        raise ValueError(f"labels must be one-dimensional, got shape {label_vector.shape}")
    if len(feature_matrix) != len(label_vector):
        raise ValueError("features and labels must have the same length")
    if len(feature_matrix) == 0:
        raise ValueError("cannot train a model with no samples")
    if algorithm == "knn" and len(feature_matrix) < 5:
        raise ValueError("kNN training requires at least 5 samples")
    if not np.isfinite(multiplier) or multiplier <= 0:
        raise ValueError("rejection multiplier must be finite and positive")
    unknown_labels = sorted(set(str(label) for label in label_vector) - set(LABELS))
    if unknown_labels:
        raise ValueError(f"unknown labels in training data: {unknown_labels}")
    label_counts = {label: int(np.sum(label_vector == label)) for label in LABELS}
    missing_labels = [label for label, count in label_counts.items() if count == 0]
    if missing_labels:
        raise ValueError(f"training data must include all four labels; missing {missing_labels}")
    sparse_labels = [label for label, count in label_counts.items() if count < 2]
    if sparse_labels:
        raise ValueError(f"training data needs at least 2 samples per label; sparse {sparse_labels}")

    scaler = StandardScaler()
    total_start = perf_counter()
    fit_start = perf_counter()
    scaled = scaler.fit_transform(feature_matrix)
    estimator = _make_estimator(algorithm)
    estimator.fit(scaled, label_vector)
    estimator_fit_seconds = perf_counter() - fit_start
    threshold_start = perf_counter()
    thresholds = class_distance_thresholds(scaled, label_vector, multiplier)
    threshold_seconds = perf_counter() - threshold_start
    fit_seconds = perf_counter() - total_start
    return PrototypeGestureModel(
        estimator=estimator,
        scaler=scaler,
        train_features_scaled=scaled,
        train_labels=label_vector,
        thresholds=thresholds,
        config=ModelConfig(algorithm=algorithm, multiplier=multiplier),
        fit_seconds=fit_seconds,
        estimator_fit_seconds=estimator_fit_seconds,
        threshold_seconds=threshold_seconds,
    )


def class_distance_thresholds(
    scaled_features: np.ndarray, labels: np.ndarray, multiplier: float = 1.5
) -> dict[str, float]:
    if not np.isfinite(multiplier) or multiplier <= 0:
        raise ValueError("rejection multiplier must be finite and positive")
    thresholds: dict[str, float] = {}
    for label in sorted(set(str(value) for value in labels)):
        class_rows = scaled_features[labels == label]
        if len(class_rows) <= 1:
            raise ValueError(f"cannot derive rejection threshold for {label} with fewer than 2 samples")
        distances: list[float] = []
        for index, row in enumerate(class_rows):
            others = np.delete(class_rows, index, axis=0)
            distances.append(float(np.min(np.linalg.norm(others - row, axis=1))))
        thresholds[label] = float(np.quantile(distances, 0.95) * multiplier)
    return thresholds


def _make_estimator(algorithm: Algorithm) -> KNeighborsClassifier | SVC:
    if algorithm == "knn":
        return KNeighborsClassifier(n_neighbors=5, weights="distance")
    if algorithm == "svm":
        return SVC(C=1, gamma="scale", kernel="rbf")
    raise ValueError(f"unknown algorithm {algorithm}")


def _coerce_feature_matrix(features: np.ndarray) -> np.ndarray:
    matrix = np.asarray(features, dtype=np.float32)
    if matrix.ndim != 2 or matrix.shape[1] != 60:
        raise ValueError(f"expected feature matrix shape (n, 60), got {matrix.shape}")
    if not np.all(np.isfinite(matrix)):
        raise ValueError("feature matrix contains non-finite values")
    return matrix


def _coerce_feature_row(feature: np.ndarray) -> np.ndarray:
    row = np.asarray(feature, dtype=np.float32)
    if row.shape != (60,):
        raise ValueError(f"expected one feature vector of shape (60,), got {row.shape}")
    if not np.all(np.isfinite(row)):
        raise ValueError("feature contains non-finite values")
    return row


def _library_versions() -> dict[str, str]:
    return {
        "numpy": np.__version__,
        "scikit-learn": version("scikit-learn"),
    }
