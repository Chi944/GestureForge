from types import SimpleNamespace

import numpy as np
import pytest

from gestureforge.contracts import Observation
from gestureforge.features import FeatureExtractionError, extract_feature_result, extract_feature_vector


def test_extract_feature_vector_normalises_world_landmarks() -> None:
    landmarks = [(float(index), 0.0, 0.0) for index in range(21)]

    feature = extract_feature_vector(landmarks)

    assert feature.shape == (60,)
    reshaped = feature.reshape(20, 3)
    assert np.allclose(reshaped[0], [1 / 9, 0, 0])
    assert np.allclose(reshaped[8], [1, 0, 0])


def test_extract_feature_vector_accepts_mediapipe_style_objects() -> None:
    landmarks = [SimpleNamespace(x=float(index), y=1.0, z=-1.0) for index in range(21)]
    observation = Observation(
        session_id="s1",
        profile_id="p1",
        frame_id=1,
        timestamp=1.0,
        hand_count=1,
        handedness="Right",
        landmarks=landmarks,
    )

    feature = extract_feature_vector(observation)

    assert feature.shape == (60,)


def test_extract_feature_vector_rejects_wrong_chosen_hand() -> None:
    landmarks = [SimpleNamespace(x=float(index), y=1.0, z=-1.0) for index in range(21)]
    observation = Observation(
        session_id="s1",
        profile_id="p1",
        frame_id=1,
        timestamp=1.0,
        hand_count=1,
        handedness="Left",
        landmarks=landmarks,
    )

    result = extract_feature_result(observation, chosen_hand="Right")

    assert not result.valid
    assert "expected Right hand" in result.reason


def test_extract_feature_vector_rejects_invalid_observation() -> None:
    observation = Observation(
        session_id="s1",
        profile_id="p1",
        frame_id=1,
        timestamp=1.0,
        hand_count=2,
        handedness=None,
        landmarks=None,
    )

    result = extract_feature_result(observation)

    assert not result.valid
    assert result.feature is None
    assert "expected one hand" in result.reason


def test_extract_feature_vector_rejects_degenerate_scale() -> None:
    landmarks = np.zeros((21, 3), dtype=float)

    with pytest.raises(FeatureExtractionError, match="degenerate"):
        extract_feature_vector(landmarks)
