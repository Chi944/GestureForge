# GestureForge User Guide

For Apple Silicon macOS installation, camera permissions and equivalent Terminal commands,
use the [Mac setup guide](MACOS.md). The `.cmd` and PowerShell commands below are for Windows.

Status: assignment guide aligned to implemented entry points. Software verification is recorded in `docs/evidence/verification.json`; measured pilot results, setup/package checks, P02 qualitative feedback and limitations are consolidated in `docs/evidence/RESULTS.md`. The user confirmed second-laptop pause/restart and offline use on 29 September. Exact device, package and guide-only setup details are not recorded.

## Purpose

GestureForge is a local desktop prototype for recognising a small personal set of static hand gestures from a webcam and controlling a card viewer. The assignment release executes NEXT only. PREVIOUS and BOOKMARK may appear as recognised labels but are preview-only until the final project release.

GestureForge controls its own fixed ten-card deck. It is not connected to Microsoft PowerPoint; PowerPoint/OS control is outside the agreed scope.

## Requirements

### Project Studio preview

Launch `.\run.cmd --studio` for the current project build. Click **Load personal dataset...** and select an existing personal `manifest.json`; no restart is required. Loading pauses control and trains locally in the background. After success, check the reset Preview mappings, click **Start camera control** and hold NEUTRAL until READY. Switching datasets requires another explicit start and neutral hold. If loading fails, the previous model stays selected and paused.

The loader uses your launch settings, for example `.\run.cmd --studio --algorithm knn --multiplier 2 --margin 1.5 --camera 1`. It accepts one participant's numeric collection data, including custom gesture vocabularies, and rejects synthetic fixtures. It does not create or save profiles yet. All Studio gesture actions are simulations; the manual card buttons still work. See the [project progress](project/PROGRESS.md) for remaining functionality.

In Studio, choose **Camera index** (usually 0 or 1), then **Use camera and pause**. Editing the number alone does not change capture. Applying a different index stops the old worker and clears its predictions; wait for release before Start becomes available. Start explicitly and hold NEUTRAL again. Camera changes preserve your active mappings and simulation mode. The selection is not saved across launches; use `--camera` for a launch default.

**Ctrl+O** loads a dataset, **Ctrl+Enter** starts capture when ready, and **Esc** pauses. The indeterminate loading bar means local training is still running, not a completion percentage. Camera selection is disabled during loading. If the preview stalls or the camera disconnects, follow the recovery message: close other camera apps, check the cable and permissions, then retry Start or another camera index. On a small window, scroll through setup and card content. Start/Pause, manual controls, controller state, hold progress and the active context/gesture legend stay visible in the bottom bar. Draft settings do not replace that active legend until applied.

### Assignment environment

- Windows computer with a working webcam.
- Python 3.11. The local development environment currently reports Python 3.11.16.
- Access to this `code` folder.
- Internet access for initial dependency installation.

The final submitted package should also work offline after dependencies and model assets are installed, but this must be verified before it is claimed.

## Setup

Open the extracted `gestureforge` folder or your cloned repository in File Explorer. You can double-click:

```text
setup.cmd
run.cmd
```

For terminal setup, open PowerShell in that folder, wherever you saved it. The developer's original directory layout is not required. Follow the [Windows laptop guide](WINDOWS_LAPTOP.md) for installation and personal enrolment on another computer.

Then run:

```powershell
.\setup.cmd
.\run.cmd
```

`setup.cmd` uses process-scoped PowerShell execution bypass for this project script only. It does not change the computer's execution policy.

Manual setup commands, if needed:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.lock
python -m pip install --no-deps -e .
python scripts/download_model.py
```

If Python 3.11 is installed without the Windows launcher, run `.\setup.cmd -PythonExe "C:\path\to\python.exe"`. The script checks that the interpreter is 64-bit Python 3.11 before installing dependencies.

If PowerShell blocks activation, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

## Launch the Prototype

Keyboard-only viewer:

```powershell
.\run.cmd
```

Smoke-test startup with screenshot:

```powershell
.\run.cmd --smoke-test --screenshot docs\evidence\app-smoke.png
```

Live gesture control after collecting a human dataset:

```powershell
.\run.cmd --dataset data\local\pilot\manifest.json --algorithm knn --multiplier 2 --margin 1.5 --camera 1
```

Supported algorithm choices are `knn` and `svm`. The shown kNN multiplier 2 and margin 1.5 configuration is the revised P01 development setting. The margin rejects predictions too similar to another enrolled class; it does not eliminate all unknown-pose errors. Other participants need their own collection and validation. Synthetic fixtures cannot enable live control. Version 2 calibration requires at least two valid training trials per label; the planned pilot uses eight.

If **Start camera control** is disabled immediately after launch, no personal gesture dataset was loaded. Double-clicking `run.cmd` opens the keyboard-only viewer even when a webcam is connected. Close that window and use the live command above with your saved dataset. Existing P01 users do not need to collect more data just to enable the button.

### Select the working camera

Close Windows Camera, video-call apps and other camera previews before using GestureForge. Device indices can change after reconnecting cameras. On the development computer, index 1 returned usable video; index 0 did not. Verify the selected device on each computer:

```powershell
python scripts/check_environment.py --camera --camera-index 1
.\run.cmd --dataset data/local/pilot/manifest.json --algorithm knn --multiplier 2 --margin 1.5 --camera 1
```

Use `--camera 1` on each collection command below when that is the working device. The camera check reports hand counts without saving images. A successful image read alone does not establish hand recognition or a working gesture command.

Expected assignment window:

- Webcam preview.
- Current prediction.
- Controller state.
- Current card.
- Start/Pause controls.
- Manual Next control.
- Clear preview-only marking for PREVIOUS and BOOKMARK.

## Collect Assignment Data

The submitted P01 pilot already exists. Preserve it unchanged. For another person or a new experiment, use a new pseudonym and separate output folder, following [Windows enrolment instructions](WINDOWS_LAPTOP.md). The commands below document the original P01 protocol; do not rerun them into the retained submission dataset. Commands using `python` require the activated project environment from Manual setup above.

Human collection commands:

```powershell
python -m gestureforge.collect --camera 1 --split train --participant P01 --hand Right --setup "desk lighting, plain background" --consent --output data/local/pilot
python -m gestureforge.collect --camera 1 --split validation --participant P01 --hand Right --setup "desk lighting, plain background" --consent --output data/local/pilot
python -m gestureforge.collect --camera 1 --split validation_negative --participant P01 --hand Right --setup "desk lighting, plain background" --consent --output data/local/pilot
```

The command arguments set the participant pseudonym, hand and session type. The window prompts each label in sequence. Press Space for each trial, wait for the two-second countdown, hold the pose steadily, then relax during the release interval. Press Q to stop; completed trials remain saved. Only collect data after participant consent has been recorded.

Assignment labels:

- NEXT
- PREVIOUS
- BOOKMARK
- NEUTRAL

Assignment collection target:

- One participant.
- Separate train and validation sessions.
- Eight trials per label per session.
- Five scheduled samples per trial.

## Run Evaluation

Reproduce the recorded human pilot using the private marker package or the retained local P01 dataset:

```powershell
.\.venv\Scripts\python.exe -m gestureforge.evaluate --config experiments/pilot.json --output experiments/local/reproduced-pilot.json
```

The source ZIP alone excludes P01 data. For a synthetic software check without participant data, use `experiments/prototype.json` instead; its scores are not human recognition evidence.

Expected assignment output:

- kNN results.
- SVM results.
- Rejection setting used.
- Macro-F1 over the four labels.
- Per-class precision and recall.
- Confusion matrix including UNKNOWN.
- Notes on invalid detections.

To create a saved synthetic fixture manifest before testing `dataset_path` loading:

```powershell
python -m gestureforge.fixtures data\local\synthetic
```

Example config using a collected human manifest:

```json
{
  "dataset_path": "data/local/pilot/manifest.json",
  "algorithms": ["knn", "svm"],
  "rejection_multiplier": 2.0
}
```

## Environment and Model Checks

After setup, run:

```powershell
python scripts\check_environment.py
python scripts\download_model.py
```

For a live camera check, run:

```powershell
python scripts\check_environment.py --camera
```

Save the output as release evidence when preparing a submission. Summarise accepted release evidence in `docs\evidence\RESULTS.md`.

## Agile Board

The live sprint board is [GestureForge Assignment and Project on Trello](https://trello.com/b/wDb978u6/gestureforge-assignment-and-project). Move cards according to actual evidence and keep their acceptance criteria and release target visible. `docs/backlog.csv` is the submission snapshot; `docs/sprint_events.jsonl` preserves development status events. See [the Agile record](AGILE.md) for the sprint schedule and definition of done.

## Source Package

Create a source archive:

```powershell
python scripts\package_release.py
```

The archive includes tracked source files and excludes private local data and environments. It is not the complete assignment submission until the report, permitted participant evidence, declaration, and upload verification are complete.

## Run Tests

Run the automated tests:

```powershell
python -m pytest
```

The current software verification summary is recorded in `docs\evidence\verification.json`. Consolidated measured results and limitations are recorded in `docs\evidence\RESULTS.md`. Re-run tests before packaging each release and refresh those evidence files when results change.

## Assignment Demo Script

1. Launch with the human dataset path, selected algorithm, rejection multiplier and working camera index shown above.
2. Confirm the notice identifies the intended participant and hand.
3. Click **Start camera control**.
4. Confirm the webcam preview appears.
5. Hold NEUTRAL until the controller is ready.
6. Hold NEXT until one card advance occurs.
7. Continue holding NEXT and show that no duplicate action occurs.
8. Return to NEUTRAL.
9. Show PREVIOUS and BOOKMARK predictions, if available, marked as preview-only.
10. Pause recognition and show that no command fires.

## Known Assignment Limits

- NEXT is the only executed gesture command.
- PREVIOUS and BOOKMARK are recognition preview only.
- Only one fixed deck is supported.
- Profile management is not part of the assignment release.
- Recognition results are preliminary until held-out final project testing.

## Troubleshooting

| Symptom | Action |
| --- | --- |
| Python version is wrong | Run `py -3.11 --version` and recreate `.venv` with Python 3.11 |
| Camera does not open | Close other camera apps and restart GestureForge |
| No hand detected or pose repeatedly rejected | Keep the full enrolled hand in frame, face the camera as during training, use similar distance and lighting, settle the pose, then hold NEUTRAL until READY. Removing the hand is not required by the controller. |
| Many rejections | Recheck distance, lighting, hand choice, and enrolment consistency |
| Action repeats | Stop using the prototype and record a controller defect; the state machine must prevent repeats |
| Import error | Re-run `python -m pip install -r requirements.lock` and `python -m pip install --no-deps -e .` in the active `.venv` |

## Final Project Preview

The final project guide will add profile creation, in-app practice, PREVIOUS and BOOKMARK execution, custom JSON deck loading, saved state, and recovery from corrupted files.

## Rejection settings and historical results

The live app defaults to ambiguity margin 1.5. For the revised P01 setting, pass both `--multiplier 2 --margin 1.5`. Accepted unfamiliar poses are recognition errors, not default PREVIOUS/BOOKMARK behaviour. Rejected poses display Unrecognised and cannot dispatch actions.

The new `experiments/pilot-rejection.json` reproduces prototype-v3 macro-F1 0.9667 for both classifiers on P01 development validation. Historical `experiments/pilot.json` intentionally retains distance-only prototype-v2 (margin 1.0), macro-F1 0.9686. For exact historical live configuration pass `--margin 1`. The balanced update reduces unfamiliar command-label accepts from 25/40 to 5/40 and the user confirmed the corrected NEUTRAL-to-NEXT transition twice. This remains smoke evidence, not formal live evaluation. See the [result comparison](evidence/RESULTS.md).


## Transition recovery and BOOKMARK

After a 300 ms NEUTRAL hold reaches READY, move directly into NEXT and hold it steadily for 400 ms. A classifier-only rejection during the transition cancels any partial NEXT hold but preserves readiness for up to 500 ms; the stable NEXT hold must start again from zero. Longer rejection, lost/wrong/multiple hands, stale observations or a camera fault require NEUTRAL again. Rejection while LATCHED cannot trigger a second action. If NEXT appears with WAIT NEUTRAL, show NEUTRAL until READY before retrying; removing the hand is unnecessary. Restart the app after installing this controller update.

BOOKMARK is recognition preview only in the assignment. In the final project it will mark the current card for later review and persist that mark with saved deck state. Repeating it will keep one bookmark, without moving the card. It does not control PowerPoint.
