import numpy as np
from types import SimpleNamespace

from gestureforge.collect import scheduled_sample
from gestureforge.contracts import Observation


def _valid_observation(timestamp: float, handedness: str = "Right") -> Observation:
    landmarks: np.ndarray = np.zeros((21, 3), dtype=np.float32)
    landmarks[9] = [0.0, 1.0, 0.0]
    return Observation(
        session_id="session",
        profile_id="pilot",
        frame_id=1,
        timestamp=timestamp,
        hand_count=1,
        handedness=handedness,
        landmarks=landmarks,
        validity_reason="",
    )


def test_scheduled_sample_accepts_due_frame_and_preserves_feature_slot() -> None:
    feature, reason = scheduled_sample(_valid_observation(10.19), due=10.0, chosen_hand="Right")

    assert reason == ""
    assert feature is not None
    assert feature.shape == (60,)


def test_scheduled_sample_rejects_early_or_late_frame_without_substitution() -> None:
    early_feature, early_reason = scheduled_sample(
        _valid_observation(9.99), due=10.0, chosen_hand="Right"
    )
    late_feature, late_reason = scheduled_sample(
        _valid_observation(10.21), due=10.0, chosen_hand="Right"
    )

    assert early_feature is None
    assert early_reason == "missed scheduled timestamp"
    assert late_feature is None
    assert late_reason == "missed scheduled timestamp"


def test_scheduled_sample_records_feature_rejection_reason() -> None:
    observation = _valid_observation(10.05, handedness="Left")

    feature, reason = scheduled_sample(observation, due=10.0, chosen_hand="Right")

    assert feature is None
    assert reason == "expected Right hand, got Left"


def test_collector_saves_complete_trials_and_appends_distinct_sessions(monkeypatch, tmp_path):
    import gestureforge.collect as collection
    from gestureforge.dataset import load_dataset

    clock = [100.0]

    def monotonic():
        clock[0] += 0.02
        return clock[0]

    class Camera:
        def __init__(self, *args):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *_):
            pass

        def read(self):
            return np.zeros((8, 8, 3), dtype=np.uint8), _valid_observation(monotonic())

    monkeypatch.setattr(collection, "HandCamera", Camera)
    monkeypatch.setattr(collection.time, "monotonic", monotonic)
    monkeypatch.setattr(collection, "show", lambda *args: None)
    monkeypatch.setattr(collection.cv2, "waitKey", lambda _: 32)
    monkeypatch.setattr(collection.cv2, "destroyAllWindows", lambda: None)
    args = SimpleNamespace(output=str(tmp_path / "pilot"), participant="P01", hand="Right",
                           split="train", setup="software test", asset="unused", camera=0, trials=1)
    collection.collect_trials(args)
    original = load_dataset(tmp_path / "pilot")
    assert len(original.records) == 20
    assert all(record.valid for record in original.records)
    args.split = "validation"
    collection.collect_trials(args)
    combined = load_dataset(tmp_path / "pilot")
    assert len(combined.records) == 40
    assert len({record.session_id for record in combined.records}) == 2
    assert combined.records[:20] == original.records
    assert len({record.feature_index for record in combined.records}) == 40
    assert {record.split for record in combined.records} == {"train", "validation"}
