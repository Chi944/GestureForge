# GestureForge User Guide

For Apple Silicon macOS installation, camera permissions and equivalent Terminal commands,
use the [Mac setup guide](MACOS.md). The `.cmd` and PowerShell commands below are for Windows.

Status: assignment guide aligned to implemented entry points. Software verification is recorded in `docs/evidence/verification.json`; measured pilot results, setup/package checks, P02 qualitative feedback and limitations are consolidated in `docs/evidence/RESULTS.md`. The user confirmed second-laptop pause/restart and offline use on 29 September. Exact device, package and guide-only setup details are not recorded.

## Purpose

GestureForge is a local desktop prototype for recognising a small personal set of static hand gestures from a webcam and controlling a card viewer. The assignment release executes NEXT only; PREVIOUS and BOOKMARK are recognition preview only there. Studio's manual viewer supports all three actions in explicitly selected LIVE mode; Preview/Rehearsal simulate typed actions. Personal LIVE gestures require the current full-Practice grant and explicit activation described below.

The assignment controls its supplied ten-card deck and does not connect to Microsoft PowerPoint. Studio supports custom content and manual Windows shortcut requests in explicit LIVE mode. macOS supports the manual viewer but reports external launches unsupported.

## Requirements

### Project Studio preview

Launch `.\run.cmd --studio` for the current project build. For manual control, click **Open Setup**, select **Live** in **Studio action mode** at the top of Setup, then click **Apply and pause**. These controls appear before dataset, camera and readiness settings; no dataset or webcam is needed for the manual walkthrough.

For gesture simulation, use Preview or Rehearsal, click **Load personal dataset...** and select an existing personal TRAIN `manifest.json`; no restart is required. Loading pauses control and trains locally in the background. After success, check the Preview mappings. A compatible active stage keeps its authored mappings; an empty or incompatible stage stays manual-only. When Start is enabled, click **Start camera control** and hold NEUTRAL until READY. Switching datasets requires another explicit start and neutral hold. If loading fails, the previous model stays selected and paused.

The loader distinguishes the wrong file type from missing training samples. A workspace or deck JSON produces guidance to use **Load workspace...** or **Load deck...**. **Dataset has no valid TRAIN samples** means the selected dataset cannot train a model, including validation/negative-only data; locate the existing personal TRAIN manifest first. Selecting the wrong JSON file does not require new gesture recordings.

The dataset loader uses your launch settings, for example `.\run.cmd --studio --algorithm knn --multiplier 2 --margin 1.5 --camera 1`. It accepts one participant's numeric collection data, including custom gesture vocabularies, and rejects synthetic fixtures. Studio gesture actions simulate in Preview/Rehearsal; personal LIVE control becomes eligible only after the full Practice gate below. Manual typed action buttons also simulate in Preview/Rehearsal; explicitly selecting LIVE allows manual actions without a model or readiness pass. See the [project progress](project/PROGRESS.md) for remaining functionality.

Open **Profiles** to manage saved personal profiles. To create one, enter a name, browse to an existing numeric `manifest.json`, select its hand and classifier, confirm that internal-use permission has been obtained, then click **Create and load personal profile**. Fitting runs in the background. To return to a saved profile, select it and click **Load selected**. Both paths install only a valid completed model and leave control paused in Preview. A failed load keeps the previous selection with an error; a corrupt entry does not hide the other profiles. Competing load, camera and mapping controls are unavailable while creation/loading is busy.

Check the active mappings, then click **Request Preview start** after the previous camera has released. This request must match the loaded profile/model and Preview mode; hold NEUTRAL before simulated actions can occur. Creating/loading a profile never starts capture automatically or passes readiness. **Rename selected profile** changes only its display name. **Delete selected** asks for confirmation, deletes only that profile's settings and clears it if active; its numeric dataset and other profiles remain. **Use Guest (manual only)** returns to manual controls without deleting any profile or dataset, so either profile can be loaded again. **Try standard gestures** remains disabled because no approved starter is supplied. In a future reviewed release it loads the standard right-hand model in paused Preview and opens Setup. Complete the six prompted activations, then select LIVE, Apply and pause, Start, and show NEUTRAL. Changing camera, model or action meanings requires a fresh check. This shorter standard-model check never replaces full Practice for a personal model.

You can also launch `.\run.cmd --studio --profile-id YOUR_PROFILE_ID --camera 1`. The ID is the saved profile JSON filename without `.json`, usually under `.local/profiles`; `--profile-store PATH` selects a different private store for both startup and the Profiles tab. Keep the original numeric dataset at its recorded path. Saved classifier settings are authoritative: do not combine `--profile-id` with `--dataset`, `--algorithm`, `--multiplier` or `--margin`; intentional retraining requires a new profile. Loading displays the profile name/ID and stays paused. A successful load is not a readiness pass.

With a personal recogniser loaded, click **Start/retry readiness** after the previous camera has released. This starts a preliminary simulated check: follow the prompts for two activations of each of the three enrolled action gestures, using NEUTRAL between activations. All six must pass through the protected controller with zero wrong activations. UNKNOWN does not count toward completion; **Finish readiness** fails an incomplete check. Guest has no standard recogniser and cannot run this check. A pass applies only to this session's behaviour revision; model, camera or active behaviour changes expire it, while cosmetic profile renaming and navigation through existing stages retain it. For personal models it does not enable live gestures. The separate **Practice** tab provides the longer measured protocol below. Only a saved, reconciled full Practice pass from the current app session can grant personal LIVE eligibility; it never starts capture or actions automatically. Manual LIVE controls do not depend on either gesture check.

In Studio, choose **Camera index** (usually 0 or 1), then **Use camera and pause**. Editing the number alone does not change capture. Applying a different index stops the old worker and clears its predictions. An applied camera change expires personal LIVE eligibility even if you later select the old index. To resume simulation, select Preview or Rehearsal in **Studio action mode** and click **Apply and pause**; LIVE Start requires a new qualifying full Practice pass. With a personal recogniser loaded, wait for the old camera to release, Start explicitly and hold NEUTRAL again. Camera changes preserve your active mappings and mode. The selection is not saved across launches; use `--camera` for a launch default.

**Ctrl+O** loads a dataset, **Ctrl+Enter** starts capture when ready, and **Esc** pauses. The indeterminate loading bar means local training is still running, not a completion percentage. Camera selection is disabled during loading. If the preview stalls or the camera disconnects, follow the recovery message: close other camera apps, check the cable and permissions, then retry Start or another camera index. Studio keeps the camera outside the scrolling workflow pane. **Setup** contains the camera, mapping, readiness and file controls; **Open Practice** goes directly to the trial workflow. Start/Pause, manual controls, prediction, rejection/rearm guidance and hold progress stay visible while the right pane scrolls. Resizing fits the entire camera image without cropping; narrow borders can remain to preserve its aspect ratio. Draft settings do not replace the active context/gesture legend until applied.

### Personal Practice

Use **Open Practice** to reveal the Practice tab
and recording-consent box. A personal recogniser must be loaded. The camera
intentionally switches off after each measured window; click **Prepare next
trial** only when ready to continue. Preparation has a 30-second timeout.

For a brief check, choose **Test only NEXT**, **Test only NEUTRAL**, or another
enrolled pose after **Start personal practice**, before preparing. This records
one five-second diagnostic and finishes automatically. Read the actual trial
outcome: completing a diagnostic is not a full rehearsal pass. Other poses and
negative activity are not assessed by that diagnostic. The default full rehearsal
still requires all 22 windows; separate attempts cannot be combined into a pass.

A recorded action can still have an **inconclusive** outcome if camera capture
does not cover the whole measurement window. This is not, by itself, a recognition
failure. New diagnostic results show the first-frame gap, largest frame gap and
end gap in **Session summary**, alongside the allowed gap. These values explain
capture coverage; they do not change its 200 ms requirement. Older results may
lack this timing detail and are not backfilled with invented values.

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
diagnostics retain the latest prepared trial's Begin attempt, any pre-Begin
boundary prediction, and its latest invalid/late capture condition. They are
not a full timeline of physical poses. An otherwise valid late frame during
preparation, including READY while waiting for Begin, is discarded and resets
neutral arming. The camera stays open and completed windows remain in the same
attempt. Hold NEUTRAL again until READY before clicking Begin; the original
30-second preparation deadline still applies. In protocol `gf-p12-v3`, an
otherwise valid late frame during measurement is dropped without an action.
The current window finishes on its original five-second timer as **inconclusive**;
click **Prepare next trial** to continue the same session. Previous windows are
retained, but any inconclusive window prevents a full pass. Its saved coverage
diagnostics retain the late-frame count and largest observed age. This policy
also applies to the v3 single-pose diagnostic. Malformed/out-of-order packets,
camera faults, focus loss and configuration changes still interrupt and preserve
the result. A previously cancelled attempt cannot be resumed or combined with
a new attempt for a full-protocol pass. Older v1/v2/v3 results remain unchanged
and cannot be reused as a current `gf-p12-v4` personal LIVE grant.

If setup reaches 30 seconds before measurement starts, capture pauses and
**Retry setup** repeats the same prompt. Completed windows remain saved in the
same attempt; setup retries are recorded separately and earn no trial credit.
After **Begin**, a brief **Waiting for fresh capture / READY** message means
timing has not started: keep NEUTRAL until the countdown appears. This wait lasts
at most two seconds; if it expires, keep NEUTRAL and click Begin again. Do not
change poses until **Measurement started** appears. The 200 ms frame limit and
five-second measured window are unchanged.

Practice is the longer GF-P12 measurement workflow, separate from **Start/retry readiness**. It uses the loaded recogniser, shared camera, hold/rearm controller and existing dispatcher; every action during measurement is simulated. Only a genuine qualifying full attempt completed in the current app session can grant personal LIVE eligibility after saving, event reconciliation and paused context restoration.

1. Load a personal dataset or profile and select the correct camera. Finish/cancel the short readiness check, pause any existing capture and wait for camera release.
2. Open **Practice**, then **Review negative cues**. Edit any of the ten instructions that overlap your enrolled action poses; keep exactly ten nonempty lines, then close the dialog. Select the local numeric outcome consent checkbox only if you consent to recording. Cue text is also saved, so keep it free of personal details. The instructions are fixed once practice starts.
3. Click **Start personal practice**, then **Prepare next trial**. Wait for the matching camera preview. For action and negative trials, show accepted NEUTRAL until READY; for a NEUTRAL trial, the rearm transition must occur inside its measured window.
4. Click **Begin five-second window** when ready and follow the displayed pose/instruction for the full window. Use **Prepare next trial** after the preceding capture releases. Protocol `gf-p12-v4` uses three rounds of the three action poses and NEUTRAL, followed by ten negative/transition windows: twenty-two five-second measurements, with preparation time in addition.
5. Review the per-pose result and saved path. Local JSON files under `.local/studio/practice/practice-<attempt-id>.json` record trial outcomes, simulated event IDs, rejection counts, capture coverage and the profile/model/behaviour revision. They contain no images, video, landmarks or feature vectors. Keep these files private and preserve the code revision plus separate intended-pose notes with any reported issue.

The personal LIVE pass requires all 22 windows with complete capture coverage, all three trials correct for each action pose and NEUTRAL, zero wrong or repeated activations and all ten negative windows correct. An interrupted or inconclusive attempt cannot pass; separate diagnostics or attempts cannot be combined. NEUTRAL and negative windows should not emit an action, so twenty-two windows do not mean twenty-two actions. The dedicated Practice JSON holds per-trial measurements; the session summary records dispatcher outcomes. Do not interpret a simulation count as a real launch or task completion.

After saving, open **Session summary** for **Latest saved practice — historical**.
It shows completed versus recorded windows, per-pose outcomes, unattempted
windows, coverage failures and negative actions. The event comparison checks each
recorded action against its original dispatcher event, including the session,
model, context and typed action. Missing, duplicate, mismatched or unexpected
events need investigation; they are not hidden by an aggregate total. A generated
perfect `gf-p12-v4` run has twenty-two windows and nine simulated command
actions. Older v1-v3 examples with fifty windows remain historical records.

This historical view survives summary reset and later profile changes within the
open app. Its revision labels show whether it refers to the current behavior and
summary segment. **Export session results** continues to export the current
SessionSummary format; keep the separate Practice JSON and original summary
exports together for review. Reopening the app does not import an old Practice
review automatically, and this view cannot enable LIVE gestures.

**Stop rehearsal**, Pause/Esc, focus loss or leaving Practice ends the attempt, releases capture and restores the previous context paused after saving. It does not continue an interrupted attempt automatically. If a write fails, leave the app open, fix folder access and click **Save / retry local results**. Evidence stays in memory and replacement/close is blocked until saved; it is not protected against process termination or power loss. Changing the profile, model, camera, bindings or workspace must finish this preservation flow before the new setup takes effect.

### Personal LIVE after Practice

A qualifying full Practice attempt grants eligibility only in the app session
that actually ran it. The host must finish the 22-window protocol, save the
terminal result, reconcile every simulated event with its original dispatcher
outcome, and restore the previous context paused. A pending save, interruption,
inconclusive window or reconciliation failure cannot grant eligibility. The
short six-activation check, a single-pose diagnostic, historical review and
imported/saved JSON cannot grant or restore it. Practice itself always simulates.

To use an eligible personal profile:

1. Confirm the full result satisfies all 22 covered windows, all 3/3 trials
   correct for each of the three action poses and NEUTRAL, zero wrong or repeated activations
   and all ten negative windows correct.
2. In **Open Setup**, select **Live** in **Studio action mode**, then click
   **Apply and pause**. Check the active context and gesture meanings.
3. Wait for the previous camera worker to release, click **Start camera control**
   and show fresh NEUTRAL until READY. A pass, mode selection or focus return
   never starts capture or executes an action automatically.

Eligibility exists only in memory. It is pinned to the profile, model, hand,
camera, behavior revision and exact authored maps for the workspace, its stages
and Quick Actions. A behavior, mapping, target or applied camera change expires
it permanently for that pass, even if the previous values are restored. Reloading
a model, switching to Guest or restarting Studio clears it; loading saved state
or JSON cannot recover it. Complete a new full Practice pass for the new setup.

Ordinary pause, cosmetic renaming and selecting an already configured stage or
Quick Actions context retain eligibility. Those context changes still pause and
clear pending holds; resume explicitly with Start and fresh NEUTRAL. An empty or
incompatible map remains manual-only. Configure intended routes and targets
before Practice to avoid expiring the grant during the walkthrough.

An external launch uses the existing target validation, once-only dispatch and
camera-release handshake. If capture cannot release, nothing opens; retry
explicitly after release. Returning focus never replays the request or resumes
control. Windows launch requests remain distinct from visible application
readiness and human task completion; macOS external launches remain unsupported.
Manual LIVE controls still need no profile or Practice pass. Standard starter
gestures remain unavailable. This software gate does not establish new participant
results, repair need, candidate quality or native-device acceptance.

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

### Repair One Pose

Use **Repair pose** only after a diagnostic or reviewed trace points to one weak label in your own saved profile. Load that saved profile first in **Profiles**. Guest/manual mode, ad-hoc manifests and unsaved datasets are disabled for repair; save an ad-hoc TRAIN manifest as a profile before repairing it.

1. Open **Repair pose**, confirm the source profile, choose the label to repair and enter the diagnostic reason, collection conditions and 2-12 trials.
2. Select the numeric collection consent checkbox, then request collection. Studio pauses routing and uses the shared observation-only camera path; no gesture actions dispatch during repair.
3. Capture only the prompted label. Invalid or missing slots stay recorded as evidence, but an incomplete repair cannot create a candidate.
4. Review valid-slot and retained-class counts, then click **Save separate TRAIN candidate**. The candidate replaces the chosen label's TRAIN records only, preserves the other TRAIN classes, excludes VALIDATION, TEST and UNKNOWN rows from fitting, and verifies original dataset and reviewed collection hashes. If saving fails, leave the app open and retry; SaveError handling retains the original profile and collected evidence.
5. When the candidate opens in **Profiles**, review it there. Only explicit permission plus **Create and load personal profile** trains and loads the new profile. The app stays paused in Preview, expires readiness and requires a fresh NEUTRAL hold before any later control.
6. To roll back, load the original saved profile from **Profiles**. Rollback also stays paused and does not restore an old LIVE grant.

Repair is targeted collection, not a full rehearsal pass. Do not repeat a full dataset or change thresholds until the diagnostic evidence says repair is needed.


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

**Navigation:** click **Open Setup** above the camera area. **Studio action mode** and **Apply and pause** are at the top of Setup, before dataset, camera and readiness controls. If the panel is scrolled, return to its top, select **Live**, then click **Apply and pause**. Confirm **Manual LIVE ready** before the manual walkthrough; a dataset or readiness pass is not required.

**Camera index** is the capture device number, normally `0` for the first camera and `1` for the second; connected devices can change the numbering. Editing the number is a draft until you click **Use camera and pause**; the header shows the applied selection. This button selects a device and pauses, rather than starting capture. Leave the camera off for a manual walkthrough. For a dataset/vocabulary error, check the selected file and existing personal TRAIN manifest or saved profile. Workspace/deck JSON uses **Load workspace...**/**Load deck...**; the personal loader now identifies that file-type mistake separately from a dataset with no valid TRAIN samples. Neither message alone justifies blanket recollection.

Choose the Harbor workspace that matches the loaded gesture IDs: `assets/harbor_standard_workspace.json` uses **NEXT / PREVIOUS / BOOKMARK** for the standard starter and legacy personal profiles; `assets/harbor_workspace.json` uses **G1 / G2 / G3**. Both contain the same six-stage task. Gesture IDs identify poses; the stage shows the action currently assigned to each pose. Other custom vocabularies need explicitly authored bindings. Loading a workspace never renames gestures or grants LIVE eligibility. The standard starter itself remains unavailable until a qualifying release is approved.

Run `.\run.cmd --studio` for the project preview. The file-control grid near the bottom of the **Setup** tab provides **Load deck...**, **Save progress...**, **Restore progress...**, **Load workspace...**, **Save session...** and **Restore session...**. The **Manual browse / bookmarks** tab provides Previous, Next, Bookmark and bookmark review/removal. Typed actions simulate in Preview/Rehearsal; in **Studio action mode**, select **Live** and click **Apply and pause** to perform manual deck/stage actions or request validated Windows targets. No model is required for manual control. Previous-stage navigation, bookmark review/removal, restart and restore remain explicit navigation operations; stage transitions stay paused. Try `assets/corporate_demo_deck.json` for deck-only browsing or `assets/harbor_workspace.json` for a workspace with runbook stages. An invalid deck, workspace or incompatible progress/session file leaves the current content intact and displays an error.

**Save progress...** writes only the loaded deck's card identifiers, current position and bookmarks; restore requires the same deck to be loaded and leaves camera control paused. A custom deck load creates a manual deck workspace and detaches any previous runbook. Restart keeps the loaded deck but returns to the first card, clears bookmarks in memory and resets the current stage context. Changes are not saved automatically; save again when needed.

The **Runbook** tab shows the current stage instructions and manual buttons for Previous, Continue/Finish and any stage actions. Typed stage actions follow the selected mode: simulated in Preview/Rehearsal, performed manually in explicit LIVE. Entering a stage never launches a target automatically. **Save session...** stores the current workspace plus runbook stage/finished state and matching deck position/bookmarks. Restoring either session or deck progress returns LIVE mode to paused Preview; typed actions simulate until you explicitly select Live and Apply and pause again. Before **Restore session...**, load the same workspace first; restore validates that match, stays paused and does not auto-detect a workspace from the session file. A workspace whose stage gestures do not match the loaded vocabulary stays manual-only; loading a compatible model reapplies the current stage bindings. Loading or restoring never replays launches. A current personal full-Practice grant permits LIVE gestures only for the exact authored workspace, stage and Quick Actions maps covered by that grant. Selecting an existing configured stage keeps eligibility but pauses capture and requires explicit Start plus fresh NEUTRAL; an empty or incompatible map stays manual-only. The six-activation check alone is insufficient.

Use **Edit runbook** to create, save, delete or reorder authored stages. Accepted edits reset the active workspace/runbook and keep deck review state when the deck did not change. Use **Session summary** to refresh counts and **Export session results** to save a local JSON measurement archive. Counts distinguish simulated actions, manual and eligible LIVE gesture outcomes, Windows launch requests/failures and gesture rejections; bookmark list review/removal is outside this summary. A launch request does not establish visible application readiness or task completion. Zero correct/wrong/missed counts mean no measured trials were recorded in that summary. Before deck/workspace replacement, session restore, restart or close would leave a non-empty summary behind, Studio archives it under ignored `.local/studio`; if archiving fails, the change or close is blocked and counts remain visible. Successful restore/restart starts a fresh review summary. Session summary exports are separate from **Save session...** / **Restore session...**, which explicitly save and restore runbook navigation state; position is not autosaved.

**Quick Actions** works without a deck/runbook or dataset. Manual target buttons simulate in Preview/Rehearsal and request real Windows launches only in explicit LIVE mode. Set it up as follows:

1. Open **Quick Actions**, click **New**, enter a display label, choose the target type and enter its value. For **Builtin**, use `calculator` or `camera`; websites require a full HTTPS URL. **Browse** selects supported local files, folders or applications; confirm the trust checkbox for an application you selected. Click **Save target**.
2. Choose targets in up to three gesture slots, then click **Use Quick Actions**. Target/slot edits pause control and permanently expire any personal LIVE grant, even if the old values are restored. If standalone Quick Actions is active, its gesture bindings clear until you activate again; otherwise the current deck/runbook context and mappings are retained. A missing bound target or no bound slots leaves gesture control paused; repair the target or bind a valid slot.
3. In Preview/Rehearsal, click a slot button or **Test selected target** to record a simulated request without opening anything. In explicitly selected LIVE mode, the same buttons validate the target and request its Windows launch. Camera first pauses and waits for capture shutdown; if it cannot release yet, retry after release. Return and resume manually. Unsupported external launches, including on macOS, report a reason. For gesture simulation, return to Preview/Rehearsal, load a valid personal dataset, activate Quick Actions, then explicitly Start and show NEUTRAL. Personal LIVE use needs a qualifying full Practice pass for the configured targets and maps; activating an already configured Quick Actions context preserves that grant but still requires explicit Start and fresh NEUTRAL. Loading a different dataset updates the three gesture labels and leaves capture paused.

The library holds up to twelve targets and saves its private target values and slot choices locally in `.local/studio/quick-actions-targets.json`. Reopening Studio restores that library without activating or launching it. Workspace exports and saved runbook sessions do not contain these target values. **Test selected target** records a failed validation in the session results, including in Preview, without logging raw target paths or form text. Repair requires an explicit retry. Failed validation/save keeps the previous library; if a recorded evaluation trace cannot be saved, repair that before changing targets. Preview/Rehearsal does not prove that a native Windows launch succeeds.

For a complete camera-free Windows acceptance run, follow the [six-stage manual walkthrough](project/DEMO_SCENARIO.md#manual-walkthrough-available-now). A separate [Studio source ZIP](../releases/README.md#studio-development-handoff) supports teammate setup without replacing the submitted assignment archives.

## Capture stability diagnostic

Before another long Practice attempt, a short capture check can separate camera
timing problems from gesture recognition and Practice controls. It uses the same
camera worker and optional classifier as Studio, but does not display the camera,
run the controller, or open applications. No pose sequence is required.

Pause Studio and close other programs using the webcam first. From the repository
root, use the working camera index and a **new** output filename:

```powershell
.\.venv\Scripts\python.exe -m scripts.check_stability --camera 1 --seconds 60 --output experiments/local/capture-check-01.json
```

To include the existing personal classifier in the timing check:

```powershell
.\.venv\Scripts\python.exe -m scripts.check_stability --camera 1 --seconds 60 --dataset data/local/pilot/manifest.json --algorithm knn --multiplier 2 --margin 1.5 --output experiments/local/capture-model-check-01.json
```

The camera index and P01 path above are development-machine examples. On another
computer, use that computer's working index and locally permitted dataset. On
macOS, use `.venv/bin/python`; native Mac operation still needs device testing.

The report contains aggregate duration, delivered observation rate, frame delay,
gaps, skipped frame IDs, memory and camera shutdown results. It saves no photos,
video, landmarks, feature vectors or predicted labels. Reports remain local under
`experiments/local/`; existing output files cannot be overwritten. It uses the
installed environment and model asset, with no additional download or dependency.

Read timing warnings as well as completion: a completed diagnostic does not mean
gesture recognition passed. Missing frames, a camera fault, an interrupted run
or a worker that fails to shut down must remain visible. Ctrl+C requests a stop
and retains the interrupted report. After the check finishes and releases the
camera, return to Studio and start capture explicitly.

For the later release test, use `--seconds 1800` and another new filename. This
measures the capture/landmark pipeline and optional classifier; it does **not**
replace the full Studio UI/controller stability run, thirty-minute human workflow
observation, or independent second-laptop checks. A 60-second run cannot be
reported as thirty-minute acceptance.

## Rejection settings and historical results

The live app defaults to ambiguity margin 1.5. For the revised P01 setting, pass both `--multiplier 2 --margin 1.5`. Accepted unfamiliar poses are recognition errors, not default PREVIOUS/BOOKMARK behaviour. Rejected poses display Unrecognised and cannot dispatch actions.

The new `experiments/pilot-rejection.json` reproduces prototype-v3 macro-F1 0.9667 for both classifiers on P01 development validation. Historical `experiments/pilot.json` intentionally retains distance-only prototype-v2 (margin 1.0), macro-F1 0.9686. For exact historical live configuration pass `--margin 1`. The balanced update reduces unfamiliar command-label accepts from 25/40 to 5/40 and the user confirmed the corrected NEUTRAL-to-NEXT transition twice. This remains smoke evidence, not formal live evaluation. See the [result comparison](evidence/RESULTS.md).


## Transition recovery and BOOKMARK

After a 300 ms NEUTRAL hold reaches READY, move directly into NEXT and hold it steadily for 400 ms. A classifier-only rejection during the transition cancels any partial NEXT hold but preserves readiness for up to 500 ms; the stable NEXT hold must start again from zero. Longer rejection, lost/wrong/multiple hands, stale observations or a camera fault require NEUTRAL again. Rejection while LATCHED cannot trigger a second action. If NEXT appears with WAIT NEUTRAL, show NEUTRAL until READY before retrying; removing the hand is unnecessary. Restart the app after installing this controller update.

BOOKMARK is recognition preview only in the assignment. In explicit LIVE mode, Studio's manual Bookmark control marks the current card for later review and includes it in saved deck progress. Repeating it keeps one bookmark without moving the card. Preview/Rehearsal simulate that request; eligible personal Studio gestures perform it only after explicit LIVE activation. It does not control PowerPoint.
