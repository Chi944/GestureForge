import numpy as np
import pytest
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


@pytest.mark.parametrize("first_split, second_split, pose_set_id", [
    ("train", "validation", None),
    ("test", "test", "standard-v1"),
])
def test_collector_saves_complete_trials_and_appends_distinct_sessions(
    monkeypatch, tmp_path, first_split, second_split, pose_set_id,
):
    import gestureforge.collect as collection
    from gestureforge.dataset import load_dataset

    clock = [100.0]
    capture_times = []

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
            captured_at = monotonic()
            capture_times.append(captured_at)
            return np.zeros((8, 8, 3), dtype=np.uint8), _valid_observation(captured_at)

    monkeypatch.setattr(collection, "HandCamera", Camera)
    monkeypatch.setattr(collection.time, "monotonic", monotonic)
    monkeypatch.setattr(collection, "show", lambda *args: None)
    monkeypatch.setattr(collection.cv2, "waitKey", lambda _: 32)
    monkeypatch.setattr(collection.cv2, "destroyAllWindows", lambda: None)
    args = SimpleNamespace(output=str(tmp_path / "pilot"), participant="P01", hand="Right",
                           split=first_split, setup="software test", asset="unused", camera=0,
                           trials=1, pose_set_id=pose_set_id)
    collection.collect_trials(args)
    original = load_dataset(tmp_path / "pilot")
    assert len(original.records) == 20
    assert all(record.valid for record in original.records)
    assert all(record.timestamp in capture_times for record in original.records)
    for record in original.records:
        due = original.metadata["trial_start_times"][record.trial_id] + collection.SAMPLE_OFFSETS[record.sample_index]
        assert 0 <= record.timestamp - due <= 0.2
    assert original.metadata.get("pose_set_id") == pose_set_id
    args.split = second_split
    # Omission on append inherits an existing declared pose set; it never drops it.
    args.pose_set_id = None
    collection.collect_trials(args)
    combined = load_dataset(tmp_path / "pilot")
    assert len(combined.records) == 40
    assert len({record.session_id for record in combined.records}) == 2
    assert combined.records[:20] == original.records
    assert len({record.feature_index for record in combined.records}) == 40
    assert {record.split for record in combined.records} == {first_split, second_split}
    assert combined.metadata.get("pose_set_id") == pose_set_id


def test_collection_cli_accepts_test_and_pose_set(monkeypatch, tmp_path):
    import gestureforge.collect as collection
    observed: list[SimpleNamespace] = []
    monkeypatch.setattr("sys.argv", [
        "collect", "--split", "test", "--pose-set-id", "standard-v1", "--participant", "P04",
        "--output", str(tmp_path / "test"), "--setup", "generated test only", "--consent",
    ])
    monkeypatch.setattr(collection, "collect_trials", observed.append)
    collection.main()
    assert len(observed) == 1
    assert observed[0].split == "test" and observed[0].pose_set_id == "standard-v1"


@pytest.mark.parametrize("existing_split, existing_pose, new_split, new_pose, error", [
    (None, None, "test", None, "pose-set-id"),
    (None, None, "test", "bad/path", "IDs must"),
    ("train", "standard-v1", "test", "standard-v1", "separate TEST"),
    ("test", "standard-v1", "train", "standard-v1", "separate TEST"),
    ("test", "standard-v1", "test", "custom-v2", "pose set"),
    ("train", None, "train", "standard-v1", "pose set"),
])
def test_collection_rejects_unsafe_test_append_before_camera(
    monkeypatch, tmp_path, existing_split, existing_pose, new_split, new_pose, error,
):
    import gestureforge.collect as collection
    from gestureforge.dataset import SampleRecord, save_dataset
    output = tmp_path / "data"
    if existing_split is not None:
        record = SampleRecord("P04", "old-session", "old-trial", "NEUTRAL", existing_split,
                              0, 0.0, True, 0, hand="Right")
        metadata = {"chosen_hand": "Right"}
        if existing_pose:
            metadata["pose_set_id"] = existing_pose
        save_dataset(output, [record], np.zeros((1, 60)), metadata)
    before = {p.name: p.read_bytes() for p in output.glob("*")} if output.exists() else {}
    def forbidden_camera(*args):
        raise AssertionError("Invalid TEST setup must fail before camera acquisition")
    monkeypatch.setattr(collection, "HandCamera", forbidden_camera)
    args = SimpleNamespace(output=str(output), participant="P04", hand="Right", split=new_split,
                           pose_set_id=new_pose, setup="generated test only", camera=0, trials=1, asset="unused")
    with pytest.raises(ValueError, match=error):
        collection.collect_trials(args)
    after = {p.name: p.read_bytes() for p in output.glob("*")} if output.exists() else {}
    assert after == before
