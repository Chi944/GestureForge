# Run GestureForge on Apple Silicon

Target: **Apple Silicon, macOS 13 Ventura or newer, native Python 3.11**.
The pinned dependencies have compatible wheels and passed a cross-platform pip
resolution check. Actual Mac installation, camera permission, live operation and
performance still need verification on the destination Mac. Intel Macs and Rosetta
are outside this setup path.

## Install and launch

Use a fresh clone or source ZIP, extracted into a writable folder. Do not copy a
Windows `.venv`; virtual environments must be created on the destination computer.
Open Terminal in the folder containing `pyproject.toml`.

Check the Mac and Python:

```bash
sw_vers -productVersion
python3.11 -c 'import platform; print(platform.machine())'
```

The Python command must print `arm64`. If Python 3.11 is missing, install native
Python 3.11; with [Homebrew](https://formulae.brew.sh/formula/python@3.11) already
installed, use `brew install python@3.11`. Do not launch Terminal using Rosetta.

```bash
python3.11 scripts/setup_macos.py
bash run.sh
```

Setup needs internet. It installs the existing pinned dependencies into `.venv`,
verifies their consistency, downloads the checksum-verified hand model and runs
blank-image landmark inference. It does not open the camera or collect samples.
If setup fails, resolve the reported error and rerun; it does not delete an existing
environment. Use `bash run.sh` rather than double-clicking the script so errors
remain visible. The launcher handles project folders containing spaces.

The initial viewer supports keyboard/mouse control. **Start camera control remains
disabled until a personal dataset is supplied.** A connected webcam alone is not enough.

## Camera permission and personal gestures

First check the camera from the same Terminal you will use to run the app:

```bash
.venv/bin/python scripts/check_environment.py --camera --camera-index 0
```

Allow camera access when macOS asks. If denied, open **System Settings → Privacy &
Security → Camera** and enable the listed launching application (Terminal, your
editor, or Python as shown). Quit and reopen that application after changing its
permission. Close FaceTime, Zoom and other camera applications before retrying.
The check processes five frames without saving images. Its hand counts can be zero
if no hand was in view; this is not a successful recognition test.

Start with camera index 0. If it selects the wrong camera or is unavailable, repeat
with index 1. Use the successful index consistently for collection and live control;
do not assume the Windows development computer's index applies to a Mac.

Use your existing personal dataset if you already have one. The GitHub/source ZIP
does not contain private P01 data. To enrol a new consenting user, follow the
[collection protocol](DATA_COLLECTION.md), using a new folder and participant ID.
For example, after consent, collect a right-hand TRAIN session:

```bash
.venv/bin/python -m gestureforge.collect --output data/local/mac-pilot --participant MAC01 --split train --hand Right --trials 8 --camera 0 --setup "Record your actual lighting, camera position and four poses here" --consent
```

Replace the setup text with actual conditions. Use the same folder, participant,
hand and pose mapping in a separate recording session with `--split validation`.
Collection shows the camera in an OpenCV window; focus it and use Space/Q as prompted.
Only numeric features and metadata are saved. Do not overwrite P01 or reuse someone
else's classifier as evidence of your own recognition accuracy.

```bash
bash run.sh --dataset data/local/mac-pilot/manifest.json --algorithm knn --multiplier 2 --margin 1.5 --camera 0
```

These are the prototype's provisional live settings, not a guarantee for a new
person or camera. Keep the enrolled hand fully visible, steady and similarly
oriented to training. Wait for NEUTRAL → READY, then hold NEXT. Return to NEUTRAL
before repeating. PREVIOUS and BOOKMARK remain recognition previews.

## Verify the destination Mac

```bash
.venv/bin/python -m pip check
.venv/bin/python scripts/check_environment.py --model
.venv/bin/python scripts/verify.py
```

The verification script saves actual results in `docs/evidence/verification.json`.
It runs offscreen software checks; it does not prove camera or live performance.
Keep the Mac's evidence separately from the Windows record when sharing results.

Then run the app normally and confirm:

- The window responds while the camera preview moves, and different cards are visible.
- NEUTRAL arms, a five-second NEXT hold advances once, and another NEXT needs NEUTRAL.
- Pause releases the camera; restarting and closing/reopening work.
- After successful setup, the viewer and camera still work with Wi-Fi disconnected.
- A sustained session remains responsive; record duration, Mac model, macOS version,
  camera, dataset and any errors. Do not report Windows timings as Mac measurements.

Camera inference already runs outside the UI thread with only the latest result
retained. If transitions remain slow, compare the displayed prediction and controller
state, improve lighting/framing and close other camera/compute-heavy apps. Do not
shorten the deliberate hold or disable rejection to conceal recognition problems.

Sources: [Qt macOS requirements](https://doc.qt.io/qt-6/macos.html),
[MediaPipe Python setup](https://developers.google.com/edge/mediapipe/solutions/setup_python),
[Apple camera permissions](https://support.apple.com/guide/mac-help/control-access-to-your-camera-mchlf6d108da/mac).
