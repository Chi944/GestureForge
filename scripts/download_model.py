"""Download the official pretrained asset, pinning its checksum on first setup."""

import hashlib
import json
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parent.parent
URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"


def main():
    target = ROOT / "assets" / "hand_landmarker.task"
    manifest = ROOT / "assets" / "model_manifest.json"
    expected = json.loads(manifest.read_text()) if manifest.exists() else {}
    if target.exists():
        payload = target.read_bytes()
    else:
        with urlopen(URL, timeout=60) as response:
            payload = response.read(20_000_000)
    digest = hashlib.sha256(payload).hexdigest()
    if expected.get("sha256") and digest != expected["sha256"]:
        raise SystemExit("Asset checksum mismatch. Do not use this download.")
    if len(payload) < 1_000_000:
        raise SystemExit("Downloaded asset is unexpectedly small.")
    temporary = target.with_suffix(".download")
    temporary.write_bytes(payload)
    temporary.replace(target)
    if not manifest.exists():
        manifest.write_text(json.dumps({
            "name": "MediaPipe Hand Landmarker", "asset_version": "float16/1",
            "url": URL, "sha256": digest, "bytes": len(payload),
            "source": "https://developers.google.com/edge/mediapipe/solutions/vision/hand_landmarker",
            "distribution": "Retrieved from upstream during setup; not tracked in Git.",
        }, indent=2) + "\n", encoding="utf-8")
    print(f"Verified {target.name}: SHA256 {digest}")


if __name__ == "__main__":
    main()
