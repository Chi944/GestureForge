from types import SimpleNamespace
from typing import Any, cast

import numpy as np
import pytest

from gestureforge.contracts import Observation, Prediction


def _landmarks():
    return [SimpleNamespace(x=float(index), y=float(index + 1), z=float(index + 2)) for index in range(21)]


def test_hand_camera_reads_unmirrored_frame_and_releases_resources(monkeypatch, tmp_path) -> None:
    from gestureforge import capture

    asset = tmp_path / "hand_landmarker.task"
    asset.write_bytes(b"model")
    bgr_frame: np.ndarray = np.zeros((3, 4, 3), dtype=np.uint8)

    class FakeCapture:
        def __init__(self, index):
            self.index = index
            self.released = False
            self.settings = []
            self.reads = 0

        def isOpened(self):
            return True

        def set(self, key, value):
            self.settings.append((key, value))
            return True

        def read(self):
            self.reads += 1
            if self.reads == 1:
                return False, None
            return True, bgr_frame

        def release(self):
            self.released = True

    fake_cap = FakeCapture(0)

    class FakeDetector:
        def __init__(self):
            self.stamps = []
            self.closed = False

        def detect_for_video(self, image, stamp_ms):
            self.stamps.append(stamp_ms)
            return SimpleNamespace(
                hand_world_landmarks=[_landmarks()],
                handedness=[[SimpleNamespace(category_name="Right")]],
            )

        def close(self):
            self.closed = True

    fake_detector = FakeDetector()

    class FakeHandLandmarker:
        @staticmethod
        def create_from_options(options):
            assert str(asset.resolve()) in str(options.base_options.model_asset_path)
            return fake_detector

    fake_mp = SimpleNamespace(
        tasks=SimpleNamespace(
            BaseOptions=lambda model_asset_path: SimpleNamespace(model_asset_path=model_asset_path),
            vision=SimpleNamespace(
                HandLandmarkerOptions=lambda **kwargs: SimpleNamespace(**kwargs),
                RunningMode=SimpleNamespace(VIDEO="VIDEO"),
                HandLandmarker=FakeHandLandmarker,
            ),
        ),
        ImageFormat=SimpleNamespace(SRGB="SRGB"),
        Image=lambda image_format, data: SimpleNamespace(image_format=image_format, data=data),
    )
    monkeypatch.setitem(__import__("sys").modules, "mediapipe", fake_mp)
    def open_camera(index, backend):
        assert backend == capture.cv2.CAP_ANY
        return fake_cap

    monkeypatch.setattr(capture.cv2, "VideoCapture", open_camera)
    monkeypatch.setattr(capture.cv2, "cvtColor", lambda frame, code: frame)

    ticks = iter([1.000, 1.000])
    monkeypatch.setattr(capture.time, "monotonic", lambda: next(ticks))

    camera = capture.HandCamera(asset=asset, camera=0, session_id="session", profile_id="pilot")
    frame, first = camera.read()
    _, second = camera.read()
    camera.close()

    assert frame is bgr_frame
    assert first == Observation(
        session_id="session",
        profile_id="pilot",
        frame_id=0,
        timestamp=1.0,
        hand_count=1,
        handedness="Right",
        landmarks=first.landmarks,
        validity_reason="",
    )
    assert first.landmarks.shape == (21, 3)
    assert second.frame_id == 1
    assert fake_detector.stamps == [1000, 1001]
    assert fake_detector.closed is True
    assert fake_cap.released is True
    assert fake_cap.settings == []
    assert fake_cap.reads == 3


def test_camera_stops_after_bounded_missing_frame_retries(monkeypatch):
    from gestureforge import capture

    reads = []
    camera = capture.HandCamera.__new__(capture.HandCamera)
    def read_missing_frame():
        reads.append(1)
        return False, None

    camera.cap = cast(Any, SimpleNamespace(read=read_missing_frame))
    camera.detector = object()
    monkeypatch.setattr(capture.time, "sleep", lambda _: None)
    with pytest.raises(capture.CameraError, match="returned no frame"):
        camera.read()
    assert len(reads) == 5


def test_capture_worker_mailbox_keeps_only_latest_packet() -> None:
    from gestureforge.app import CaptureWorker

    worker = CaptureWorker(
        model=None,
        feature_function=None,
        chosen_hand="Right",
        camera_index=0,
        asset=None,
        session="session",
        profile="pilot",
    )
    old_packet = ("old-frame", Prediction("session", "pilot", 1, 1.0, "NEUTRAL", True))
    new_packet = ("new-frame", Prediction("session", "pilot", 2, 1.1, "NEXT", True))

    with worker._lock:
        worker._latest = old_packet
        worker._latest = new_packet

    assert worker.take_latest() == new_packet
    assert worker.take_latest() is None


def test_capture_worker_observation_only_bypasses_model_and_releases_camera(monkeypatch) -> None:
    import gestureforge.app as app_module
    from gestureforge.app import CaptureWorker

    frame: np.ndarray = np.zeros((4, 4, 3), dtype=np.uint8)
    observation = Observation(
        session_id="session",
        profile_id="pilot",
        frame_id=7,
        timestamp=12.5,
        hand_count=0,
        handedness=None,
        landmarks=None,
        validity_reason="no_hand",
    )
    released = []
    worker_box: list[CaptureWorker] = []

    class FakeCamera:
        def __init__(self, *args):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *_):
            released.append(True)

        def read(self):
            worker_box[0].requestInterruption()
            return frame, observation

    class ModelShouldNotRun:
        def predict(self, features):
            raise AssertionError("model should not run in observation-only mode")

    def extract_should_not_run(observation, hand):
        raise AssertionError("extractor should not run in observation-only mode")

    monkeypatch.setattr(app_module, "HandCamera", FakeCamera)
    worker = CaptureWorker(
        model=ModelShouldNotRun(),
        feature_function=extract_should_not_run,
        chosen_hand="Right",
        camera_index=0,
        asset=None,
        session="session",
        profile="pilot",
        observation_only=True,
    )
    worker_box.append(worker)

    worker.run()
    packet = worker.take_latest()

    assert worker.error == ""
    assert released == [True]
    assert packet == (frame, observation)
    assert packet[1] is observation
    assert packet[1].timestamp == 12.5
    assert packet[1].validity_reason == "no_hand"
    assert worker.take_latest() is None


def test_capture_worker_observation_only_allows_no_model_or_extractor(monkeypatch) -> None:
    import gestureforge.app as app_module
    from gestureforge.app import CaptureWorker

    frame: np.ndarray = np.zeros((4, 4, 3), dtype=np.uint8)
    observation = Observation("session", "pilot", 1, 1.0, 1, "Right", np.ones((21, 3)), "")
    worker_box: list[CaptureWorker] = []

    class FakeCamera:
        def __init__(self, *args):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *_):
            pass

        def read(self):
            worker_box[0].requestInterruption()
            return frame, observation

    monkeypatch.setattr(app_module, "HandCamera", FakeCamera)
    worker = CaptureWorker(
        model=None,
        feature_function=None,
        chosen_hand="Right",
        camera_index=0,
        asset=None,
        session="session",
        profile="pilot",
        observation_only=True,
    )
    worker_box.append(worker)

    worker.run()

    assert worker.error == ""
    assert worker.take_latest() == (frame, observation)


def test_capture_worker_without_feature_function_yields_rejected_prediction(monkeypatch) -> None:
    import gestureforge.app as app_module
    from gestureforge.app import CaptureWorker

    frame: np.ndarray = np.zeros((4, 4, 3), dtype=np.uint8)
    observation = Observation(
        session_id="session",
        profile_id="pilot",
        frame_id=1,
        timestamp=1.0,
        hand_count=1,
        handedness="Right",
        landmarks=np.ones((21, 3), dtype=np.float32),
        validity_reason="",
    )
    worker_box: list[CaptureWorker] = []

    class FakeCamera:
        def __init__(self, *args):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *_):
            pass

        def read(self):
            worker_box[0].requestInterruption()
            return frame, observation

    class ModelShouldNotRun:
        def predict(self, features):
            raise AssertionError("model should not run without a feature function")

    monkeypatch.setattr(app_module, "HandCamera", FakeCamera)
    worker = CaptureWorker(
        model=ModelShouldNotRun(),
        feature_function=None,
        chosen_hand="Right",
        camera_index=0,
        asset=None,
        session="session",
        profile="pilot",
    )
    worker_box.append(worker)

    worker.run()
    packet = worker.take_latest()

    assert worker.error == ""
    assert packet is not None
    _, prediction = packet
    assert prediction.label == "UNKNOWN"
    assert prediction.accepted is False
