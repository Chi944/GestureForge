"""Report dependency versions; optional live camera check never saves frames."""

import argparse
import hashlib
import importlib.metadata
import json
from pathlib import Path
import platform


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--camera", action="store_true", help="Open camera for five frames")
    parser.add_argument("--camera-index", type=int, default=0, help="Camera index for --camera")
    parser.add_argument("--model", action="store_true", help="Verify model and run blank-image inference without opening a camera")
    args = parser.parse_args()
    report: dict[str, object] = {"python": platform.python_version(), "platform": platform.platform(),
                                 "architecture": platform.machine()}
    for name in ["numpy", "scikit-learn", "mediapipe", "opencv-contrib-python", "PySide6"]:
        report[name] = importlib.metadata.version(name)
    if args.model:
        import mediapipe as mp
        import numpy as np

        assets = Path(__file__).resolve().parent.parent / "assets"
        asset = assets / "hand_landmarker.task"
        expected = json.loads((assets / "model_manifest.json").read_text(encoding="utf-8"))
        if not asset.is_file():
            raise SystemExit("Missing model. Run: python scripts/download_model.py while online.")
        model_bytes = asset.read_bytes()
        digest = hashlib.sha256(model_bytes).hexdigest()
        if digest != expected["sha256"]:
            raise SystemExit("Model checksum mismatch. Replace the model through verified setup.")
        options = mp.tasks.vision.HandLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(model_asset_buffer=model_bytes),
            running_mode=mp.tasks.vision.RunningMode.VIDEO,
            num_hands=2,
        )
        with mp.tasks.vision.HandLandmarker.create_from_options(options) as detector:
            result = detector.detect_for_video(
                mp.Image(image_format=mp.ImageFormat.SRGB,
                         data=np.zeros((256, 256, 3), dtype=np.uint8)), 1
            )
        if result.hand_landmarks:
            raise SystemExit("Unexpected hand detection in blank-image model check.")
        report["model"] = {"sha256": digest, "blank_image_hands": 0, "camera_opened": False}
    if args.camera:
        from gestureforge.capture import HandCamera
        with HandCamera(camera=args.camera_index) as camera:
            counts = [camera.read()[1].hand_count for _ in range(5)]
        report["camera"] = {"index": args.camera_index, "frames": 5, "hand_counts": counts, "recorded": False}
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
