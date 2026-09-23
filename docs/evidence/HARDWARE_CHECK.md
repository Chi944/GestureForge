# Local environment and camera check

Date: 23 September 2026. This is same-computer evidence, not a second-device test.

Initially no webcam was connected. The user then connected a Logitech QuickCam for Notebooks Deluxe, which produced black or very slow frames during investigation. Those early failures are not attributed to one cause: wrong device selection, backend behaviour, and possible Windows Camera app contention were all confounding factors.

The webcam has since been replaced. Windows now lists two camera devices: `Slim1322AF` and `USB2.0 HD UVC WebCam`. The user provided a clear Windows Camera screenshot with a hand visible. MediaPipe IMAGE-mode inference on that supplied screenshot detected one hand, so the downloaded model asset can recognise a hand in a clear still image. This is screenshot evidence, not live webcam hand-detection evidence.

## Current connected camera check

The key OpenCV finding is device-index selection. Camera index 0 fails in current checks. Camera index 1 with the default OpenCV backend (`CAP_ANY`) produces usable, non-black video. Device indexes can change after unplugging or replugging hardware, so the selected index must be confirmed before collection or demonstration.

| Check | Observed result |
| --- | --- |
| Windows camera list | `Slim1322AF`; `USB2.0 HD UVC WebCam` |
| Windows Camera app | User supplied a clear hand screenshot |
| Screenshot MediaPipe inference | One hand detected in IMAGE mode; not a live camera result |
| OpenCV camera index 0, default backend | No usable capture in current checks |
| OpenCV camera index 1, default backend | Usable non-black capture |
| 60-frame capture run on index 1 | 60 frames processed; post-warmup mean 31.24 ms, about 32 fps; max 63 ms; clean close; zero hands detected |
| Earlier 20-second interactive preview on index 1 | 304 frames processed; zero hands detected; later found to be confounded because the user did not see the preview window |
| Visible/topmost 60-second preview on index 1 | 1,145 frames processed; one hand detected in 338 frames; handedness labels included Left and Right; clean close |
| Pilot consent and hand choice | User consented to local numeric P01 data collection using the right hand; no raw frames; GitHub exclusion remains required |
| Pilot TRAIN collection | Completed 32 trials, eight each for NEXT, PREVIOUS, BOOKMARK, and NEUTRAL; 160 of 160 scheduled samples valid; right hand |
| Pilot VALIDATION collection | Completed 32 trials, eight each for NEXT, PREVIOUS, BOOKMARK, and NEUTRAL; 160 of 160 scheduled samples valid; right hand |
| Pilot validation-negative collection | Completed 8 trials and 40 valid samples from unenrolled poses |
| Live personal gesture to NEXT | Verified for assignment path: genuine webcam gesture events advanced the viewer to positions 1, 2, and 3 |
| Participant-observed hold smoke check | Two deliberate fist holds advanced exactly once each, with open-palm rearm between holds; not the formal final-project twenty-hold run |

Production capture now preserves the negotiated camera format, uses the default OpenCV backend, and retries at most five missing-frame reads 30 ms apart without reusing an old image. It does not force DirectShow. The environment checker now accepts `--camera-index` so the working index can be tested directly.

No images or video were saved. Diagnostic numeric results are in ignored `experiments/local/`. The user-confirmed clear lens and lighting narrow the issue to the capture/driver/device path, but do not identify its exact cause.

The visible preview verifies live hand-tracking activity from camera index 1. The 338 detections out of 1,145 frames are detector-activity counts from an interactive preview, not recognition accuracy or classifier performance. The user then consented to local numeric P01 data collection using the right hand. TRAIN, VALIDATION, and validation-negative sessions completed. Aggregate pilot metrics are summarised in `docs/evidence/PILOT_RESULTS.md`. Two live application instances closed cleanly with exit code 0, the second instance opened the camera, and no raw frames were saved. No individual feature vectors, trial IDs, model thresholds, raw images, raw video, or raw event logs are published in this evidence file.

## Initial checks before a camera was connected

| Check | Observed result |
| --- | --- |
| Python environment | Python 3.11.16 installed under the project; dependencies pinned in requirements.lock |
| Qt | QApplication initializes; assignment window renders and closes in smoke test |
| Model retrieval | Official float16/1 Hand Landmarker asset downloaded and verified against assets/model_manifest.json |
| Model inference smoke | Real MediaPipe detector initialized and returned zero hands for a generated blank 640x480 RGB image |
| Default camera backend, device 0 | No usable capture in current checks |
| Default camera backend, device 1 | Usable non-black capture at about 32 fps; later visible preview verified live hand detection |
| Forced DirectShow backend | Interim investigation was confounded; current production capture no longer forces DirectShow |
| Pilot data collection | Completed P01 right-hand TRAIN and VALIDATION with 160 valid scheduled samples each; validation-negative has 40 valid samples |
| Live personal gesture to NEXT | Verified for assignment NEXT path; two participant-observed holds advanced exactly once each |
| Second Windows computer | Not yet tested |

No video or audio was recorded. The blank-image smoke check proves asset loading and a model inference call, not hand recognition or webcam operation. Automated capture/GUI tests use injected data and must not be labelled as participant results.

Next evidence gate: complete the formal final-project twenty-hold run, live false-action and latency measurements if time allows, and preserve the local pilot/event evidence for the submission package. The window can close cleanly after preview or capture.
