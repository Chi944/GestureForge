"""Feature extraction for the assignment prototype.

The assignment uses MediaPipe's 21 three-dimensional hand landmarks as input,
then applies the plan's fixed policy: translate by the wrist, divide by the
wrist-to-middle-knuckle distance, remove the wrist triplet, and flatten the
remaining 20 landmarks to 60 numeric features.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

import numpy as np

from .contracts import FEATURE_VERSION, Observation

LANDMARK_COUNT = 21
FEATURE_SIZE = 60
WRIST_INDEX = 0
MIDDLE_KNUCKLE_INDEX = 9
MIN_SCALE = 1e-6


class FeatureExtractionError(ValueError):
    """Raised when an observation cannot produce a valid feature vector."""


@dataclass(frozen=True)
class FeatureResult:
    feature: np.ndarray | None
    valid: bool
    reason: str = ""
    feature_version: int = FEATURE_VERSION


def extract_feature_vector(
    observation_or_landmarks: Observation | Any, chosen_hand: str | None = None
) -> np.ndarray:
    """Return the normalised 60-element feature vector for one hand observation."""

    landmarks = _landmarks_from_input(observation_or_landmarks, chosen_hand=chosen_hand)
    points = landmarks_to_array(landmarks)
    return normalise_world_landmarks(points)


def extract_feature_result(
    observation_or_landmarks: Observation | Any, chosen_hand: str | None = None
) -> FeatureResult:
    """Return a feature result instead of raising for invalid observations."""

    try:
        feature = extract_feature_vector(observation_or_landmarks, chosen_hand=chosen_hand)
    except FeatureExtractionError as exc:
        return FeatureResult(feature=None, valid=False, reason=str(exc))
    return FeatureResult(feature=feature, valid=True)


def landmarks_to_array(landmarks: Any) -> np.ndarray:
    """Convert MediaPipe-style objects, dictionaries, or triples to a 21x3 array."""

    values = list(_iter_landmark_triples(landmarks))
    points = np.asarray(values, dtype=np.float64)
    if points.shape != (LANDMARK_COUNT, 3):
        raise FeatureExtractionError(
            f"expected {LANDMARK_COUNT} landmarks with xyz values, got shape {points.shape}"
        )
    if not np.all(np.isfinite(points)):
        raise FeatureExtractionError("landmarks contain non-finite values")
    return points


def normalise_world_landmarks(points: np.ndarray) -> np.ndarray:
    """Normalise 21 world landmarks and return a 60-element vector."""

    points = np.asarray(points, dtype=np.float64)
    if points.shape != (LANDMARK_COUNT, 3):
        raise FeatureExtractionError(
            f"expected landmark array shape {(LANDMARK_COUNT, 3)}, got {points.shape}"
        )
    if not np.all(np.isfinite(points)):
        raise FeatureExtractionError("landmarks contain non-finite values")

    wrist = points[WRIST_INDEX]
    scale = float(np.linalg.norm(points[MIDDLE_KNUCKLE_INDEX] - wrist))
    if not np.isfinite(scale) or scale <= MIN_SCALE:
        raise FeatureExtractionError("degenerate wrist-to-middle-knuckle scale")

    normalised = (points - wrist) / scale
    without_wrist = np.delete(normalised, WRIST_INDEX, axis=0)
    feature = without_wrist.reshape(FEATURE_SIZE)
    if not np.all(np.isfinite(feature)):
        raise FeatureExtractionError("normalised feature contains non-finite values")
    return feature.astype(np.float32)


def _landmarks_from_input(observation_or_landmarks: Observation | Any, chosen_hand: str | None) -> Any:
    if isinstance(observation_or_landmarks, Observation):
        if observation_or_landmarks.validity_reason:
            raise FeatureExtractionError(observation_or_landmarks.validity_reason)
        if observation_or_landmarks.hand_count != 1:
            raise FeatureExtractionError(f"expected one hand, got {observation_or_landmarks.hand_count}")
        if chosen_hand is not None and observation_or_landmarks.handedness != chosen_hand:
            raise FeatureExtractionError(
                f"expected {chosen_hand} hand, got {observation_or_landmarks.handedness}"
            )
        if observation_or_landmarks.landmarks is None:
            raise FeatureExtractionError("observation has no landmarks")
        return observation_or_landmarks.landmarks
    return observation_or_landmarks


def _iter_landmark_triples(landmarks: Any) -> Iterable[tuple[float, float, float]]:
    if hasattr(landmarks, "landmark"):
        landmarks = landmarks.landmark
    if hasattr(landmarks, "hand_world_landmarks"):
        landmarks = landmarks.hand_world_landmarks

    for item in landmarks:
        if isinstance(item, dict):
            yield (float(item["x"]), float(item["y"]), float(item["z"]))
        elif hasattr(item, "x") and hasattr(item, "y") and hasattr(item, "z"):
            yield (float(item.x), float(item.y), float(item.z))
        else:
            x, y, z = item
            yield (float(x), float(y), float(z))
