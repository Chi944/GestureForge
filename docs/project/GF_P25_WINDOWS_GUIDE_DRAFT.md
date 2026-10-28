# GestureForge Studio Windows guide

Current delivery owner: Deston (transferred 26 October 2026). Original draft prepared by Javier on 19 October 2026; preserve his contribution.
Reviewed 28 October 2026 against source `976467c`. Instructions and the local
Word demo guide are prepared now under Revision 6; final package reconciliation
follows GF-P23. The current presentation uses 14 core slides and a 60-second
highlight within its ten-minute speaking plan; the live demonstration is separate.
This review does not certify a fresh installation or change historical device evidence.

## What this helps you do

A trainer must keep explaining while moving between material, applications and
audience questions. GestureForge keeps a prepared sequence and its available
actions visible, with personal gestures, manual controls and a saved return
point. Use it to follow a runbook, open local resources, bookmark a discussion
and restore your place. The supplied Harbor Desk content is fictional.

GestureForge does not control Microsoft PowerPoint or perform tasks inside
another application. You still calculate, read and confirm completion yourself.
The intended benefit is less difficulty choosing resources and recovering your
place; measured speed or customer-demand improvements are not established.

## Install and open Studio

Use the Studio source ZIP and its matching JSON receipt. The participant browser
collection kit and the preserved assignment package are different tools.
Compare the downloaded ZIP's checksum with the receipt:

```powershell
Get-FileHash .\gestureforge-studio-source.zip -Algorithm SHA256
```

If the download filename has a suffix such as `(1)`, use that actual filename.
Extract into a fresh writable local folder and open its `gestureforge` folder.
Keep the previous installation and private data until the new copy is verified.
Use 64-bit Python 3.11 and run `setup.cmd` while online. Wait for setup success;
preserve an error if setup fails. Create this laptop's environment through setup;
do not copy another computer's `.venv`. Do not move the installed folder.
See the [Windows setup guide](../WINDOWS_LAPTOP.md) for Python and recovery steps.

Double-click `run-studio.cmd`, or use PowerShell inside that project folder:

```powershell
.\run-studio.cmd
```

`run.cmd` without `--studio` opens the earlier viewer. A terminal
running Studio remains occupied until Studio exits. For additional commands,
open another PowerShell and change to the project folder first. A prompt such as
`PS C:\...\gestureforge>` means the shell is ready for a command. A message saying
the folder is not a Git repository means Git was run outside the checkout;
change directory before retrying. ZIP-only users do not need Git to run Studio.

## Brief offline check after installation

Finish setup and the model download while online first. Save work in other apps,
then use Windows network settings to turn **Wi-Fi off**, not just disconnect one
network; unplug Ethernet and disable any hotspot/tethering connection for this
check. This avoids automatic Wi-Fi reconnection. Keep the network off until
Studio has closed. Internet reference links are outside this local-only check.

Launch Studio, load the supplied workspace, navigate and bookmark a card, and
use explicit Live manual controls to open this laptop's configured Calculator,
local reference file and folder. Save and restore the session; confirm Preview,
paused state and no automatic target reopening. Export the session summary and
close normally. Record the build, actual results and network state throughout.
The check needs no webcam, new profile or thirty-minute wait. Reconnect afterward.
An assisted installation remains labelled assisted; it does not establish that
a new user installed successfully using only this guide.

## Choose manual or gesture operation

| Mode | Typed/manual requests | Gesture requests |
| --- | --- | --- |
| Preview | Simulated; the requested card or external app does not change through typed dispatch | Simulated when a personal recogniser is loaded and capture is started |
| Rehearsal / Practice | Simulated | Simulated; measured windows save local evidence |
| Explicit Live | Manual typed actions can execute without a profile or webcam | Personal gestures need a current-session full-Practice grant or the explicitly labelled manually approved demo route below |

For manual work, Guest/manual is sufficient. Click **Open Setup**, choose **Live**
under **Studio action mode**, then **Apply and pause**. Read the footer to confirm
the applied mode and context before requesting an action. A disabled camera Start
in Guest/manual does not prevent Live manual actions. Separate browse/navigation
controls are not gesture recognition results.

For gesture simulation, load your existing permitted saved profile in **Profiles**
using **Load selected**. Confirm the loaded profile name, ID and enrolled hand in
the banner. Loading stays paused; click **Start camera control** explicitly and
show the enrolled NEUTRAL pose until READY. The new-profile creation form can
show a different hand/default settings from the loaded profile. Those draft
fields do not replace its saved settings. Do not recreate a profile merely to
diagnose an existing one. See the [user guide](../USER_GUIDE.md) for dataset loading.

Pose names are labels, not universal hand shapes. Follow the mapping recorded
for that person's dataset. Javier's P03 mapping is right open palm = NEUTRAL,
closed fist = NEXT, thumb up = PREVIOUS, and index plus middle fingers = BOOKMARK.
Do not apply this mapping to a different person's profile without checking it.

## Enrol a new user

Guest/manual works immediately; another person's profile is not a model trained
for your hand. No approved standard starter is supplied.

1. Choose **Open Enrolment**, enter a pseudonym, selected hand, actual recording
   conditions and permission. For the supplied right-hand mapping use **open
   palm = NEUTRAL, fist = G1, thumb up = G2, index/middle fingers raised = G3**.
   Custom poses must remain distinct and match that profile's recorded mapping.
2. Select TRAIN and **12 trials per pose**. Click **Request collection**, wait
   for the correct preview, then **Begin trial**. This starts collection without
   an existing recogniser; the main camera-control Start is for loaded models.
   Follow countdown, hold and release cues with the full hand visible.
3. Complete 48 TRAIN trials, take a real break, then collect a separate 48-trial
   VALIDATION session. Wait for the saved confirmation for each. Do not train on
   VALIDATION or treat partial collection as complete.
4. In **Profiles**, enter a name, **Browse dataset…** to TRAIN's manifest, review
   hand/classifier/settings, confirm **Dataset permission confirmed**, then
   **Create and load personal profile**. Wait for fitting; loading stays paused
   in Preview. This fits TRAIN; profile creation does not automatically score
   the separate VALIDATION session or display a validation report.
5. To return later, use **Load selected**. **Use Guest (manual only)** preserves
   the profile and dataset. Rename changes its display name; Delete confirms
   removal of profile settings without deleting its numeric data or other profiles.

Validation scoring is a separate, team-assisted offline step using the existing
`gestureforge.evaluate` tool with both saved manifests and the profile's actual
algorithm, distance multiplier and ambiguity margin. Preserve its report in a
new local output file. Keep this evidence separate from **Practice**, which is
the in-app behaviour check; a profile load is neither of these evaluations.
If no matching negative-validation samples are supplied, rejection performance
is unmeasured, not passed.

See the [collection procedure](../USER_GUIDE.md#collect-in-studio). Collection or
a high validation score does not guarantee live qualification. For camera
selection, index **0** usually means the first device and **1** another, not a
quality setting. Set the number and click **Use camera and pause**; editing alone
does not apply it. Close other camera applications before starting capture.

## Cards, Harbor and local shortcuts

Load Harbor through **Load workspace...** using `assets/harbor_workspace.json`.
For recognisers with NEXT/PREVIOUS/BOOKMARK labels, the separately supplied
`assets/harbor_standard_workspace.json` uses that vocabulary. Its filename does
not mean a standard starter is approved. Follow the existing six-stage
[Harbor scenario](DEMO_SCENARIO.md); do not invent task answers or acknowledge
completion until the operator actually performs the requested task.

Portable workspaces carry content, semantic slots and action meanings, not
machine-specific paths, URLs or personal datasets. Bind and test local targets
on each laptop. The library supports up to twelve targets and Quick Actions has
three gesture slots. Quick Actions can be used without a deck or runbook.
After choosing the slots, click **Use Quick Actions**; selecting its tab alone
does not activate that routing context. Check the context and action legend in
the footer. Stage selection likewise does not automatically launch a target.

Supported Windows targets are built-in Calculator/Camera, a selected existing
trusted `.exe`, permitted local TXT/PDF/PNG/JPEG files, local folders and
credential-free HTTPS. Scripts, interpreters, `.lnk`/`.url`, network/device paths
and unsupported schemes are refused. Use the actual local target rather than
guessing a path. Native macOS external shortcuts remain unsupported.

An action count, a Windows launch request, a visibly opened application and a
completed human task are different observations. Record each separately.

## Pause, failure and restore

Focus loss pauses capture. Returning to Studio does not resume or replay actions.
After any necessary release, Start explicitly and show fresh NEUTRAL. LATCHED
after an action is expected: keeping the same pose must not repeat it. Return
to NEUTRAL until READY before the next intended hold.

For a missing-target check, bind a disposable permitted TXT copy and move or
rename only that copy. Record the visible failure and unchanged stage. Restore
or rebind the target, then make a new explicit request. A request is not retried
automatically. Do not change existing Windows associations simply to manufacture
a missing-association test; mark the case NOT RUN if an isolated setup is absent.

Save progress/session explicitly before restoring. Export the Session summary
before restore, inspect the restored card/stage/bookmark and confirm paused
Preview with no automatic launch, then export the later summary as well. Saved
progress is not an event replay. Before the next real manual request, explicitly
select Live and **Apply and pause**. Review both revisions and event IDs: later
exports may include earlier rows. Use disjoint segments or a documented event-ID
union; never add overlapping snapshot totals.

If Camera opens while Studio capture was already off, record that limited case.
An active-capture handoff separately requires current personal Live eligibility
from a full Practice pass or the explicit manually approved demo route below,
and evidence that capture shut down before the real Camera request. Close Windows Camera
before explicit Studio reacquisition. A release refusal/timeout must open nothing
and require a fresh request after recovery. Record naturally observed faults;
do not label an unrun refusal case passed.

## Diagnose recognition before another full rehearsal

Keep the same saved profile, model/settings, hand, camera and source identity.
In Preview, tick **Record evaluation trace (labels and timing only)** before
Start. Show NEUTRAL to READY, perform the planned pose/negative sequence, then
Pause. Stay in Studio throughout. The saved trace records consumed labels,
acceptance/rejection and timing, not camera video or independently observed poses.
Record intended poses, repetitions and visible prediction/rejection messages
separately. Do not infer physical-pose timing from classifier labels.

Export Session summary and compare actions with that trace's session/model/context.
Preview may record a simulated NEXT even though the visible card did not move.
Keep the original unannotated trace. The existing diagnostic reconstructs the
controller; it does not score accuracy, latency or readiness without the required
independent annotations. Share private traces/settings with the assigned reviewers.
Do not lower thresholds or recollect the full dataset just to obtain a better run.

If repeated timing gaps occur, use the existing 60-second capture diagnostic in
the [user guide](../USER_GUIDE.md#capture-stability-diagnostic), with the camera
paused elsewhere and a new output filename. A pipeline check does not replace a
Studio workflow or a thirty-minute stability run.

## Personal Practice and conditional Live gestures

Configure all intended workspace/stage/Quick Actions targets and maps first.
The current `gf-p12-v4` full rehearsal has **22 five-second windows**: three each
for NEXT/PREVIOUS/BOOKMARK/NEUTRAL and ten negatives. Use the enrolled vocabulary
if its action labels differ. Choose the full rehearsal in **Practice**.

For each prompt, click **Prepare next trial** and wait for fresh camera capture.
For an action or negative window, hold NEUTRAL until READY and keep NEUTRAL while
clicking **Begin five-second window**. Change pose only after **Measurement
started**, following the displayed action or negative cue. For a NEUTRAL window,
click **Begin five-second window** after capture starts, then hold NEUTRAL during
measurement; READY is measured inside this window, not during preparation.
Camera off between windows is intentional. Avoid tab/focus changes during the attempt.

A qualifying pass needs all three trials correct for every pose, every window
fully covered, all ten negatives correct and zero wrong/repeated actions. A
capture gap or inconclusive result is not a pass. Successful separate attempts
and single-pose diagnostics cannot be combined or imported to grant eligibility.
Historical v1-v3 fifty-window evidence remains historical.

Wait for terminal save, exact dispatcher-event reconciliation and paused context
restoration. Only then explicitly select Live, **Apply and pause**, Start and
show fresh NEUTRAL. A grant is memory-only and tied to the exact profile/model,
hand, camera, behavior and authored maps. Target/map/camera/behavior edits expire
it even if reverted; restart, Guest and model reload clear it. Ordinary pause,
cosmetic renaming and existing context selection retain eligibility but never
resume automatically. If neither a full-Practice grant nor the explicit manually
approved demo route below is currently valid, active-capture Camera remains
NOT RUN; camera-off manual checks remain possible. Demo approval does not prove
automated qualification. No approved standard starter is supplied.

### Manually approved demonstration

With a personal recogniser loaded and capture/checks stopped, use **Practice →
Enable manually approved demo** for supervised demonstration. Choose Live,
**Apply and pause**, then **Start camera control** and fresh NEUTRAL. Keep
**Manually approved demo active** visible and Pause available. This session-only
approval retains hold/rearm and target protections; it does not create an
automated Practice pass. Camera, recogniser or action-map changes invalidate it.

The selected P01 demonstration has operator review acceptance with a saved
automated **19/22** result. Do not present that approval as an automated 22/22 or
as qualification for a new user. Recognition may still miss or misclassify;
use the labelled manual controls when needed.

## Evidence and next recording boundary

Preserve the accepted laptop-A PR24/26/28/29 records with their original build
identities. They do not establish new-build or active-capture acceptance.
Hau Jie operates laptop B; Javier coordinates and consolidates. Both use the
identified Studio handoff and [Windows case procedure](../evidence/WINDOWS_LAUNCH_PROCEDURE.md).
Fresh setup, offline core operation, the full thirty-minute Studio workflow,
measured rates/memory where available, faults and clean shutdown require actual
per-device observations. HTTPS online features are separate from offline core.
Mark unavailable or unmeasured cases explicitly; Deston retains final acceptance.

The [26 October evaluation](P20_EVALUATION_2026_10_26.md) contains the current
walkthrough, hold, negative-activity and latency evidence. It reports recognition
misses separately from completed operator-confirmed workflows; no controlled
speed advantage is claimed. Original traces/profiles/exports stay private.

The [endurance review](GF_P23_ENDURANCE_REVIEW_2026_10_26.md) records a completed
continuous-duration interval, normal close and camera reopening, alongside a
five-second responsiveness gap. The monitor now retains a visible gap warning;
zero remaining time does not mean every stability criterion passed. The original
laptop-B packet has been received and checked. Use the [current team guide](TEAM_GUIDE.md)
for remaining device work rather than repeating unchanged passed checks.

Use the [presentation and demo storyboard](GF_P25_DEMO_STORYBOARD.md) for the
pain-point-led sequence and genuine enrolment excerpt. Label manual footage,
simulation, time cuts and the actual demonstration mode. Obtain permission for
people/screens recorded. Final footage follows the identified release checks.
A script is not filmed evidence: GF-P25 stays open until the completed guide and
demo receive review. The ten-minute presentation is a separate deliverable.

AI assistance prepared this draft from repository instructions and supplied
observations. Javier operates the Windows device; Deston reviews acceptance.
