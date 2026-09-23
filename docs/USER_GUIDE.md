# GestureForge User Guide

Status: assignment guide aligned to implemented entry points. Software verification is recorded in `docs/evidence/verification.json`; measured pilot results and limitations are in `docs/evidence/PILOT_RESULTS.md`. Second-computer verification remains open.

## Purpose

GestureForge is a local desktop prototype for recognising a small personal set of static hand gestures from a webcam and controlling a card viewer. The assignment release executes NEXT only. PREVIOUS and BOOKMARK may appear as recognised labels but are preview-only until the final project release.

## Requirements

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
.\run.cmd --dataset data\local\pilot\manifest.json --algorithm knn --multiplier 2 --camera 1
```

Supported algorithm choices are `knn` and `svm`. The shown kNN multiplier 2 configuration is the provisional P01 pilot setting; other participants need their own collection and validation. Synthetic fixtures cannot enable live control. Version 2 calibration requires at least two valid training trials per label; the planned pilot uses eight.

### Select the working camera

Close Windows Camera, video-call apps and other camera previews before using GestureForge. Device indices can change after reconnecting cameras. On the development computer, index 1 returned usable video; index 0 did not. Verify the selected device on each computer:

```powershell
python scripts/check_environment.py --camera --camera-index 1
.\run.cmd --dataset data/local/pilot/manifest.json --algorithm knn --multiplier 2 --camera 1
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

Run evaluation with a JSON config:

```powershell
python -m gestureforge.evaluate --config experiments\prototype.json --output experiments\local\prototype-results.json
```

Expected assignment output:

- kNN results.
- SVM results.
- Rejection setting used.
- Macro-F1 over the four labels.
- Per-class precision and recall.
- Confusion matrix including UNKNOWN.
- Notes on invalid detections.

The repository also includes `experiments/prototype.json`, a synthetic software-test fixture configuration. It can help verify the evaluation path, but it is not participant evidence.

To create a saved synthetic fixture manifest before testing `dataset_path` loading:

```powershell
python -m gestureforge.fixtures data\local\synthetic
```

Example config using a collected human manifest:

```json
{
  "dataset_path": "data/local/pilot/manifest.json",
  "algorithms": ["knn", "svm"],
  "rejection_multiplier": 1.5
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

Save the output as release evidence when preparing a submission.

## Agile Board

Generate the local sprint board:

```powershell
python scripts\board.py
```

This writes `docs\SPRINT_BOARD.html` from `docs\backlog.csv`. Status updates should be evidence-based and can be recorded by the implementation lead with:

```powershell
python scripts\board.py --id GF-A1-002 --status "Done" --note "Evidence path or command result summary"
```

The update also appends an event to `docs\sprint_events.jsonl`.

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

The current software verification summary is recorded in `docs\evidence\verification.json`. Re-run tests before packaging each release and refresh that evidence file when results change.

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
| No hand detected | Improve lighting, keep hand in frame, use selected hand |
| Many rejections | Recheck distance, lighting, hand choice, and enrolment consistency |
| Action repeats | Stop using the prototype and record a controller defect; the state machine must prevent repeats |
| Import error | Re-run `python -m pip install -r requirements.lock` and `python -m pip install --no-deps -e .` in the active `.venv` |

## Final Project Preview

The final project guide will add profile creation, in-app practice, PREVIOUS and BOOKMARK execution, custom JSON deck loading, saved state, and recovery from corrupted files.
