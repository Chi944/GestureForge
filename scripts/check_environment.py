"""Report dependency versions; optional live camera check never saves frames."""

import argparse
import importlib.metadata
import json
import platform


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--camera", action="store_true", help="Open camera for five frames")
    parser.add_argument("--camera-index", type=int, default=0, help="Camera index for --camera")
    args = parser.parse_args()
    report: dict[str, object] = {"python": platform.python_version(), "platform": platform.platform()}
    for name in ["numpy", "scikit-learn", "mediapipe", "opencv-contrib-python", "PySide6"]:
        report[name] = importlib.metadata.version(name)
    if args.camera:
        from gestureforge.capture import HandCamera
        with HandCamera(camera=args.camera_index) as camera:
            counts = [camera.read()[1].hand_count for _ in range(5)]
        report["camera"] = {"index": args.camera_index, "frames": 5, "hand_counts": counts, "recorded": False}
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
