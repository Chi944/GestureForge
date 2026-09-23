# Local environment and camera check

Date: 23 September 2026. This is same-computer evidence, not a second-device test.

The user subsequently confirmed: "No webcam connected yet." The live check is therefore blocked by unavailable hardware; the backend observations below do not establish a fault with a physical camera.

| Check | Observed result |
| --- | --- |
| Python environment | Python 3.11.16 installed under the project; dependencies pinned in requirements.lock |
| Qt | QApplication initializes; assignment window renders and closes in smoke test |
| Model retrieval | Official float16/1 Hand Landmarker asset downloaded and verified against assets/model_manifest.json |
| Model inference smoke | Real MediaPipe detector initialized and returned zero hands for a generated blank 640x480 RGB image |
| Default camera backend, device 0 | Device opened but did not return a frame; CameraError reported |
| DirectShow backend, device 0 | Open call did not complete in the bounded investigation; process was stopped |
| Live personal gesture to NEXT | Not verified; requires a working camera and consented personal dataset |
| Second Windows computer | Not yet tested |

No video or audio was recorded. The blank-image smoke check proves asset loading and a model inference call, not hand recognition or webcam operation. Automated capture/GUI tests use injected data and must not be labelled as participant results.

Next hardware step: connect a webcam or use the planned demo laptop, then run the User Guide camera check. Collect separate training and validation sessions before enabling live gesture control. If a native driver stalls with a connected device, close the application and resolve the device/driver before retrying; the window can close even when the daemon camera worker has not returned.
