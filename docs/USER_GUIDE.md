# GestureForge User Guide

For Apple Silicon macOS installation, camera permissions and equivalent Terminal commands,
use the [Mac setup guide](MACOS.md). The `.cmd` and PowerShell commands below are for Windows.

Status: assignment guide aligned to implemented entry points. Software verification is recorded in `docs/evidence/verification.json`; measured pilot results, setup/package checks, P02 qualitative feedback and limitations are consolidated in `docs/evidence/RESULTS.md`. The user confirmed second-laptop pause/restart and offline use on 29 September. Exact device, package and guide-only setup details are not recorded.

## Purpose

GestureForge is a local desktop prototype for recognising a small personal set of static hand gestures from a webcam and controlling a card viewer. The assignment release executes NEXT only; PREVIOUS and BOOKMARK are recognition preview only there. Studio's manual viewer supports all three actions in explicitly selected LIVE mode; Preview/Rehearsal simulate typed actions, and live gestures remain blocked.

The assignment controls its supplied ten-card deck and does not connect to Microsoft PowerPoint. Studio supports custom content and manual Windows shortcut requests in explicit LIVE mode. macOS supports the manual viewer but reports external launches unsupported.

## Requirements

### Project Studio preview

Launch `.\run.cmd --studio` for the current project build. Click **Load personal dataset...** and select an existing personal `manifest.json`; no restart is required. Loading pauses control and trains locally in the background. After success, check the Preview mappings. A compatible active stage keeps its authored mappings; an empty or incompatible stage stays manual-only. When Start is enabled, click **Start camera control** and hold NEUTRAL until READY. Switching datasets requires another explicit start and neutral hold. If loading fails, the previous model stays selected and paused.

The dataset loader uses your launch settings, for example `.\run.cmd --studio --algorithm knn --multiplier 2 --margin 1.5 --camera 1`. It accepts one participant's numeric collection data, including custom gesture vocabularies, and rejects synthetic fixtures. Studio gesture actions can run as simulations only. Manual typed action buttons also simulate in Preview/Rehearsal; explicitly selecting LIVE allows manual actions without a model or readiness pass. See the [project progress](project/PROGRESS.md) for remaining functionality.

Open **Profiles** to manage saved personal profiles. To create one, enter a name, browse to an existing numeric `manifest.json`, select its hand and classifier, confirm that internal-use permission has been obtained, then click **Create and load personal profile**. Fitting runs in the background. To return to a saved profile, select it and click **Load selected**. Both paths install only a valid completed model and leave control paused in Preview. A failed load keeps the previous selection with an error; a corrupt entry does not hide the other profiles. Competing load, camera and mapping controls are unavailable while creation/loading is busy.

Check the active mappings, then click **Request Preview start** after the previous camera has released. This request must match the loaded profile/model and Preview mode; hold NEUTRAL before simulated actions can occur. Creating/loading a profile never starts capture automatically or passes readiness. **Rename selected profile** changes only its display name. **Delete selected** asks for confirmation, deletes only that profile's settings and clears it if active; its numeric dataset and other profiles remain. **Use Guest (manual only)** returns to manual controls without deleting any profile or dataset, so either profile can be loaded again. **Try standard gestures** is disabled with the unavailable-starter reason.

You can also launch `.\run.cmd --studio --profile-id YOUR_PROFILE_ID --camera 1`. The ID is the saved profile JSON filename without `.json`, usually under `.local/profiles`; `--profile-store PATH` selects a different private store for both startup and the Profiles tab. Keep the original numeric dataset at its recorded path. Saved classifier settings are authoritative: do not combine `--profile-id` with `--dataset`, `--algorithm`, `--multiplier` or `--margin`; intentional retraining requires a new profile. Loading displays the profile name/ID and stays paused. A successful load is not a readiness pass.

With a personal recogniser loaded, click **Start/retry readiness** after the previous camera has released. This starts a preliminary simulated check: follow the prompts for two activations of each of the three enrolled action gestures, using NEUTRAL between activations. All six must pass through the protected controller with zero wrong activations. UNKNOWN does not count toward completion; **Finish readiness** fails an incomplete check. Guest has no standard recogniser and cannot run this check. A pass applies only to this session's behaviour revision; model, camera or active behaviour changes expire it, while cosmetic profile renaming and navigation through existing stages retain it. It does not enable live gestures. The separate **Practice** tab provides the longer fifty-window protocol below. A measured result still needs review and does not automatically enable LIVE gestures. Manual LIVE controls do not depend on either gesture check.

In Studio, choose **Camera index** (usually 0 or 1), then **Use camera and pause**. Editing the number alone does not change capture. Applying a different index stops the old worker and clears its predictions. To resume gesture simulation from LIVE, select Preview or Rehearsal in **Studio action mode** and click **Apply and pause**; camera Start remains disabled in LIVE. With a personal recogniser loaded, wait for the old camera to release, Start explicitly and hold NEUTRAL again. Camera changes preserve your active mappings and mode. The selection is not saved across launches; use `--camera` for a launch default.

**Ctrl+O** loads a dataset, **Ctrl+Enter** starts capture when ready, and **Esc** pauses. The indeterminate loading bar means local training is still running, not a completion percentage. Camera selection is disabled during loading. If the preview stalls or the camera disconnects, follow the recovery message: close other camera apps, check the cable and permissions, then retry Start or another camera index. On a small window, scroll through setup and card content. Start/Pause, manual controls, current prediction, rejection/rearm guidance, controller state, hold progress and the active context/gesture legend stay visible in the bottom bar. Draft settings do not replace that active legend until applied.

### Personal Practice

Keep NEUTRAL while clicking **Begin five-second window**. The fixed footer and
Practice countdown now distinguish preparation from measurement: only change to
the prompted pose after **Measurement started**. At zero, wait while the last
in-window frames finish processing. For a NEUTRAL window, establish READY inside
the measurement window itself; for a negative window, follow its displayed cue.

After saving, **Session summary** offers measured next steps for that recorded
attempt. Incomplete capture is separated from recognition misses, and unattempted
poses are not diagnosed. Wrong or repeated commands and rejection-frame counts
help identify what evidence to inspect before targeted recollection. Event
reconciliation differences must be resolved first. These recommendations do not
change thresholds, collect data, retrain a model or enable LIVE gestures.

New results distinguish Stop rehearsal, camera Pause, loss of Studio focus,
hiding the Practice tab, closing Studio and configuration changes. Older generic
interruption messages cannot be retrospectively assigned a cause. Local timing
diagnostics retain only the latest prepared trial's Begin attempt and any
pre-Begin boundary prediction; they are not a full timeline of physical poses.

Practice is the longer GF-P12 measurement workflow, separate from **Start/retry readiness**. It uses the loaded recogniser, shared camera, hold/rearm controller and existing dispatcher; every action is simulated. A passed result does not enable LIVE gestures.

1. Load a personal dataset or profile and select the correct camera. Finish/cancel the short readiness check, pause any existing capture and wait for camera release.
2. Open **Practice**. Review the ten negative/transition instructions and edit any that overlap your enrolled action poses; keep exactly ten nonempty lines. Select **Save local numeric rehearsal outcomes for this profile** only if you consent to local outcome recording. Cue text is also saved, so keep it free of personal details.
3. Click **Start personal practice**, then **Prepare next trial**. Wait for the matching camera preview. For action and negative trials, show accepted NEUTRAL until READY; for a NEUTRAL trial, the rearm transition must occur inside its measured window.
4. Click **Begin five-second window** when ready and follow the displayed pose/instruction for the full window. Use **Prepare next trial** after the preceding capture releases. Ten rounds of the three action poses and NEUTRAL provide forty windows, followed by ten negative/transition windows: fifty five-second measurements, with preparation time in addition.
5. Review the per-pose result and saved path. Local JSON files under `.local/studio/practice/practice-<attempt-id>.json` record trial outcomes, simulated event IDs, rejection counts, capture coverage and the profile/model/behaviour revision. They contain no images, video, landmarks or feature vectors. Keep these files private and preserve the code revision plus separate intended-pose notes with any reported issue.

The proposed pass target is at least nine correct trials per pose and zero negative actions; interrupted or incomplete capture cannot be accepted as a successful window. NEUTRAL and negative windows should not emit an action, so fifty windows do not mean fifty actions. The dedicated Practice JSON holds per-trial measurements; the session summary records dispatcher outcomes. Do not interpret a simulation count as a real launch or task completion.

After saving, open **Session summary** for **Latest saved practice — historical**.
It shows completed versus recorded windows, per-pose outcomes, unattempted
windows, coverage failures and negative actions. The event comparison checks each
recorded action against its original dispatcher event, including the session,
model, context and typed action. Missing, duplicate, mismatched or unexpected
events need investigation; they are not hidden by an aggregate total. A generated
perfect run has fifty windows and thirty simulated command actions.

This historical view survives summary reset and later profile changes within the
open app. Its revision labels show whether it refers to the current behavior and
summary segment. **Export session results** continues to export the current
SessionSummary format; keep the separate Practice JSON and original summary
exports together for review. Reopening the app does not import an old Practice
review automatically, and this view cannot enable LIVE gestures.

**Stop rehearsal**, Pause/Esc, focus loss or leaving Practice ends the attempt, releases capture and restores the previous context paused after saving. It does not continue an interrupted attempt automatically. If a write fails, leave the app open, fix folder access and click **Save / retry local results**. Evidence stays in memory and replacement/close is blocked until saved; it is not protected against process termination or power loss. Changing the profile, model, camera, bindings or workspace must finish this preservation flow before the new setup takes effect.

### Studio stays LATCHED with an open palm

LATCHED prevents repeat actions after a command hold. The controller needs **accepted NEUTRAL predictions continuously for 0.3 seconds**, with fresh observations and gaps no longer than 0.2 seconds, to reach READY again. A visible open palm alone does not prove the classifier accepted NEUTRAL. Removing your hand is not required.

| Visible feedback | Meaning and next step |
| :--- | :--- |
| Unrecognised + LATCHED | The pose is rejected; read the distance/ambiguity guidance and match your enrolled neutral pose. No new command is allowed. |
| Another gesture label + LATCHED | The classifier accepts another label, so it has not begun neutral rearming. Record the mismatch for diagnosis. |
| NEUTRAL + WAIT_NEUTRAL | Neutral is being accepted; hold steadily until READY. Rejection or tracking/timing loss restarts the hold. |
| READY | Rearming is complete; hold the next mapped gesture. |

While LATCHED the Studio bar shows zero, then fills during the accepted neutral hold. This display change does not weaken command hold, neutral rearm or rejection rules. Fresh accepted predictions clear old error text; Pause and Start also clear the previous displayed prediction.

For Hau Jie's intermittent report, record a short **Preview/Rehearsal** reproduction with **Record evaluation trace** selected before Start, then Pause to save under `experiments/local/controller-traces/`. Keep local notes of the code revision, profile/settings, intended open-palm intervals and visible prediction/state. The trace contains consumed labels, acceptance/rejection, timing and routing identity; it does not infer physical pose or store controller state, camera images or feature vectors. Preserve the original unannotated trace; independently annotate a copy before scored replay. Do not lower rejection thresholds or recollect the whole dataset before the trace identifies the failure. The screenshot alone does not establish a controller or recognition defect.

To inspect a saved trace with the current controller, run from the repository root:

```powershell
.\.venv\Scripts\python.exe -m gestureforge.trace_diagnose experiments/local/controller-traces/trace-YOUR_ID.json
```

Replace the example path with your saved trace. This writes a separate diagnostic JSON under ignored `experiments/local/controller-diagnostics/`; the input trace is preserved. It reconstructs controller states from recorded labels, acceptance and timing using the current controller policy. It does not infer the physical pose or observed UI state, and it does not score accuracy or readiness. Compare the output with separately recorded intended-pose/display notes and the code revision before proposing a fix.

### Collect in Studio

1. Launch `.\run.cmd --studio`. Choose **Camera index**, then **Use camera and pause** before opening the **Enrolment** tab. A trained model is not required for collection.
2. Enter your participant pseudonym, selected hand, TRAIN or VALIDATION session, trials per pose and collection conditions. Describe three distinct poses plus NEUTRAL. The default descriptions are fist, thumb up, two fingers and open palm; the stored action IDs are G1/G2/G3. Select the consent checkbox only if you agree to local numeric collection and internal evaluation.
3. Click **Request collection**. Studio pauses gesture control, waits for any previous camera to release, then opens the selected camera. **Begin trial** becomes available after the first matching camera observation. Check the preview and keep the whole selected hand visible.
4. Prepare the prompted pose and click **Begin trial**. Follow the two-second countdown and two-second hold. Five timestamps are sampled; invalid detections remain recorded with their reasons. Release between trials, then begin the next prompted trial. Use the default twelve trials per pose for the planned personal sessions.
5. After all trials, use the displayed manifest path under `data/local/enrolment/enrol-.../`. Start a separate request for VALIDATION; each request creates a new session folder. Do not merge neighbouring samples randomly into different splits.
6. To try the completed TRAIN data, leave Enrolment and explicitly choose its `manifest.json` with **Load personal dataset...**, or create a saved profile from it in **Profiles**. Check the active mappings, then Start and NEUTRAL. Collection never creates a profile or passes readiness automatically; an all-invalid collection cannot train a usable model.

**Stop collection**, Pause, Esc, leaving the tab or losing application focus stops collection and releases capture. Interrupted holds retain collected slots and mark remaining slots invalid. No gesture commands execute during collection; the selected model and mappings are retained. Returning to the tab does not resume recording.

If saving fails, keep the application open, restore access to the output folder and click **Retry save**. The pending trial stays in memory and closing/replacing the active setup is blocked until it can be saved. Successful earlier trials remain on disk; crash/power-loss recovery of the unsaved trial is not available. No images or video are saved, and numeric data remains excluded from GitHub. This in-app path has software lifecycle tests; a real recording walkthrough still needs acceptance.

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
| MediaPipe reports `get_runfiles_dir_helper.cc` or an inaccessible non-ASCII runtime path | Keep the original folder and private files intact. Extract a fresh source copy to an ASCII-only writable path such as `C:\GestureForge` and rerun `setup.cmd`; never reuse a copied `.venv` |
| No hand detected or pose repeatedly rejected | Keep the full enrolled hand in frame, face the camera as during training, use similar distance and lighting, settle the pose, then hold NEUTRAL until READY. Removing the hand is not required by the controller. |
| Many rejections | Recheck distance, lighting, hand choice, and enrolment consistency |
| Action repeats | Stop using the prototype and record a controller defect; the state machine must prevent repeats |
| Import error | Re-run `python -m pip install -r requirements.lock` and `python -m pip install --no-deps -e .` in the active `.venv` |

## Final Project Preview

Run `.\run.cmd --studio` for the project preview. The shared file-control grid above the content tabs provides **Load deck...**, **Save progress...**, **Restore progress...**, **Load workspace...**, **Save session...** and **Restore session...**. The **Manual browse / bookmarks** tab provides Previous, Next, Bookmark and bookmark review/removal. Typed actions simulate in Preview/Rehearsal; in **Studio action mode**, select **Live (manual controls)** and click **Apply and pause** to perform manual deck/stage actions or request validated Windows targets. No model is required for manual control. Previous-stage navigation, bookmark review/removal, restart and restore remain explicit navigation operations; stage transitions stay paused. Try `assets/corporate_demo_deck.json` for deck-only browsing or `assets/harbor_workspace.json` for a workspace with runbook stages. An invalid deck, workspace or incompatible progress/session file leaves the current content intact and displays an error.

**Save progress...** writes only the loaded deck's card identifiers, current position and bookmarks; restore requires the same deck to be loaded and leaves camera control paused. A custom deck load creates a manual deck workspace and detaches any previous runbook. Restart keeps the loaded deck but returns to the first card, clears bookmarks in memory and resets the current stage context. Changes are not saved automatically; save again when needed.

The **Runbook** tab shows the current stage instructions and manual buttons for Previous, Continue/Finish and any stage actions. Typed stage actions follow the selected mode: simulated in Preview/Rehearsal, performed manually in explicit LIVE. Entering a stage never launches a target automatically. **Save session...** stores the current workspace plus runbook stage/finished state and matching deck position/bookmarks. Before **Restore session...**, load the same workspace first; restore validates that match, stays paused and does not auto-detect a workspace from the session file. A workspace whose stage gestures do not match the loaded vocabulary stays manual-only; loading a compatible model reapplies the current stage bindings. Loading or restoring never replays launches. Live gestures remain blocked while measured personal Practice evidence and gate acceptance remain; the six-activation check alone is insufficient.

Use **Edit runbook** to create, save, delete or reorder authored stages. Accepted edits reset the active workspace/runbook and keep deck review state when the deck did not change. Use **Session summary** to refresh counts and **Export session results** to save a local JSON measurement archive. Counts distinguish simulated actions, manual outcomes, Windows launch requests/failures and gesture rejections; bookmark list review/removal is outside this summary. A launch request does not establish visible application readiness or task completion. Zero correct/wrong/missed counts mean no measured trials were recorded in that summary. Before deck/workspace replacement, session restore, restart or close would leave a non-empty summary behind, Studio archives it under ignored `.local/studio`; if archiving fails, the change or close is blocked and counts remain visible. Successful restore/restart starts a fresh review summary. Session summary exports are separate from **Save session...** / **Restore session...**, which explicitly save and restore runbook navigation state; position is not autosaved.

**Quick Actions** works without a deck/runbook or dataset. Manual target buttons simulate in Preview/Rehearsal and request real Windows launches only in explicit LIVE mode. Set it up as follows:

1. Open **Quick Actions**, click **New**, enter a display label, choose the target type and enter its value. For **Builtin**, use `calculator` or `camera`; websites require a full HTTPS URL. **Browse** selects supported local files, folders or applications; confirm the trust checkbox for an application you selected. Click **Save target**.
2. Choose targets in up to three gesture slots, then click **Use Quick Actions**. Target/slot edits pause control. If standalone Quick Actions is active, its gesture bindings clear until you activate again; otherwise the current deck/runbook context and mappings are retained. A missing bound target or no bound slots leaves gesture control paused; repair the target or bind a valid slot.
3. In Preview/Rehearsal, click a slot button or **Test selected target** to record a simulated request without opening anything. In explicitly selected LIVE mode, the same buttons validate the target and request its Windows launch. Camera first pauses and waits for capture shutdown; if it cannot release yet, retry after release. Return and resume manually. Unsupported external launches, including on macOS, report a reason. For gesture simulation, return to Preview/Rehearsal, load a valid personal dataset, activate Quick Actions, then explicitly Start and show NEUTRAL. Loading a different dataset updates the three gesture labels and leaves capture paused.

The library holds up to twelve targets and saves its private target values and slot choices locally in `.local/studio/quick-actions-targets.json`. Reopening Studio restores that library without activating or launching it. Workspace exports and saved runbook sessions do not contain these target values. **Test selected target** records a failed validation in the session results, including in Preview, without logging raw target paths or form text. Repair requires an explicit retry. Failed validation/save keeps the previous library; if a recorded evaluation trace cannot be saved, repair that before changing targets. Preview/Rehearsal does not prove that a native Windows launch succeeds.

For a complete camera-free Windows acceptance run, follow the [six-stage manual walkthrough](project/DEMO_SCENARIO.md#manual-walkthrough-available-now). A separate [Studio source ZIP](../releases/README.md#studio-development-handoff) supports teammate setup without replacing the submitted assignment archives.

## Rejection settings and historical results

The live app defaults to ambiguity margin 1.5. For the revised P01 setting, pass both `--multiplier 2 --margin 1.5`. Accepted unfamiliar poses are recognition errors, not default PREVIOUS/BOOKMARK behaviour. Rejected poses display Unrecognised and cannot dispatch actions.

The new `experiments/pilot-rejection.json` reproduces prototype-v3 macro-F1 0.9667 for both classifiers on P01 development validation. Historical `experiments/pilot.json` intentionally retains distance-only prototype-v2 (margin 1.0), macro-F1 0.9686. For exact historical live configuration pass `--margin 1`. The balanced update reduces unfamiliar command-label accepts from 25/40 to 5/40 and the user confirmed the corrected NEUTRAL-to-NEXT transition twice. This remains smoke evidence, not formal live evaluation. See the [result comparison](evidence/RESULTS.md).


## Transition recovery and BOOKMARK

After a 300 ms NEUTRAL hold reaches READY, move directly into NEXT and hold it steadily for 400 ms. A classifier-only rejection during the transition cancels any partial NEXT hold but preserves readiness for up to 500 ms; the stable NEXT hold must start again from zero. Longer rejection, lost/wrong/multiple hands, stale observations or a camera fault require NEUTRAL again. Rejection while LATCHED cannot trigger a second action. If NEXT appears with WAIT NEUTRAL, show NEUTRAL until READY before retrying; removing the hand is unnecessary. Restart the app after installing this controller update.

BOOKMARK is recognition preview only in the assignment. In explicit LIVE mode, Studio's manual Bookmark control marks the current card for later review and includes it in saved deck progress. Repeating it keeps one bookmark without moving the card. Preview/Rehearsal simulate that request; Studio gesture BOOKMARK remains simulated. It does not control PowerPoint.
