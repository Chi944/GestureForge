"""Local webcam adapter. Frames are not recorded or uploaded."""

from pathlib import Path
import time

import cv2
import numpy as np

from .contracts import Observation

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ASSET = ROOT / "assets" / "hand_landmarker.task"


class CameraError(RuntimeError):
    pass


class HandCamera:
    """Capture unmirrored RGB input; mirror only the application's preview."""

    def __init__(self, asset=DEFAULT_ASSET, camera=0, session_id="capture", profile_id="pilot"):
        import mediapipe as mp

        asset = Path(asset)
        if not asset.is_file():
            raise CameraError("Missing hand model. Run: python scripts/download_model.py")
        self.mp = mp
        self.session_id = session_id
        self.profile_id = profile_id
        self.frame_id = 0
        self.last_ms = -1
        self.detector = None
        self.cap = None
        try:
            options = mp.tasks.vision.HandLandmarkerOptions(
                base_options=mp.tasks.BaseOptions(model_asset_path=str(asset.resolve())),
                running_mode=mp.tasks.vision.RunningMode.VIDEO,
                num_hands=2,
            )
            self.detector = mp.tasks.vision.HandLandmarker.create_from_options(options)
            # Preserve the device's negotiated format. Forcing even its current
            # resolution can break legacy drivers. The operator selects the
            # camera index; backend device ordering is not interchangeable.
            self.cap = cv2.VideoCapture(camera, cv2.CAP_ANY)
            if not self.cap.isOpened():
                raise CameraError("Camera unavailable. Close other camera apps and check permissions.")
        except Exception:
            self.close()
            raise

    def read(self):
        if self.cap is None or self.detector is None:
            raise CameraError("Camera is closed.")
        # Some USB cameras drop a startup or occasional frame. Retry briefly;
        # never reuse the previous image or hide a sustained disconnection.
        for attempt in range(5):
            ok, frame = self.cap.read()
            if ok and frame is not None:
                break
            if attempt < 4:
                time.sleep(0.03)
        else:
            raise CameraError("Camera disconnected or returned no frame. Pause and reconnect.")
        timestamp = time.monotonic()
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        stamp_ms = max(self.last_ms + 1, int(timestamp * 1000))
        self.last_ms = stamp_ms
        result = self.detector.detect_for_video(
            self.mp.Image(image_format=self.mp.ImageFormat.SRGB, data=rgb), stamp_ms
        )
        count = len(result.hand_world_landmarks)
        reason = "" if count == 1 else ("no_hand" if count == 0 else "multiple_hands")
        landmarks = None
        handedness = None
        if count == 1:
            landmarks = np.array(
                [[point.x, point.y, point.z] for point in result.hand_world_landmarks[0]],
                dtype=np.float32,
            )
            # Tasks already uses Right/Left labels in the opposite order to
            # legacy solutions.hands. Do not apply the legacy selfie swap here.
            handedness = result.handedness[0][0].category_name
        observation = Observation(
            self.session_id, self.profile_id, self.frame_id, timestamp,
            count, handedness, landmarks, reason,
        )
        self.frame_id += 1
        return frame, observation

    def close(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        if self.detector is not None:
            self.detector.close()
            self.detector = None

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
