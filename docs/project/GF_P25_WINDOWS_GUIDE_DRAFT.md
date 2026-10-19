# GF-P25: Windows Studio user-guide draft

Owner: Javier. Prepared 19 October 2026 for Deston's review.
Status: documentation draft, not a completed demo or release acceptance.
Runtime reference: the identified 16 October Studio package, clean source
`d200947692253ede0c264755152e4419530147a3`.
ZIP SHA256: `4c4f4fbc0223229c50fb5a2e7abf9b1fb00057be1c95f9df443236aaaa42839a`.
Documentation reviewed against `97a05a0cace85a309966ba74ee04198fb41496ec`.
Later documentation does not change the runtime identity of the native checks.

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

`run.cmd` without `--studio` opens the earlier assignment viewer. A terminal
running Studio remains occupied until Studio exits. For additional commands,
open another PowerShell and change to the project folder first. A prompt such as
`PS C:\...\gestureforge>` means the shell is ready for a command. A message saying
the folder is not a Git repository means Git was run outside the checkout;
change directory before retrying. ZIP-only users do not need Git to run Studio.

## Choose manual or gesture operation

| Mode | Typed/manual requests | Gesture requests |
| --- | --- | --- |
| Preview | Simulated; the requested card or external app does not change through typed dispatch | Simulated when a personal recogniser is loaded and capture is started |
| Rehearsal / Practice | Simulated | Simulated; measured windows save local evidence |
| Explicit Live | Manual typed actions can execute without a profile or webcam | Personal capture and dispatch need a genuine current-session full-Practice grant |

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
An active-capture handoff separately requires a valid personal grant and evidence
that capture shut down before the real Camera request. Close Windows Camera
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
resume automatically. An unavailable grant leaves active-capture Camera NOT RUN;
manual checks remain possible. No approved standard starter is supplied.

## Evidence and next recording boundary

Preserve the accepted laptop-A PR24/26/28/29 records with their original build
identities. They do not establish new-build or active-capture acceptance.
Hau Jie operates laptop B; Javier coordinates and consolidates. Both use the
identified Studio handoff and [Windows case procedure](../evidence/WINDOWS_LAUNCH_PROCEDURE.md).
Fresh setup, offline core operation, the full thirty-minute Studio workflow,
measured rates/memory where available, faults and clean shutdown require actual
per-device observations. HTTPS online features are separate from offline core.
Mark unavailable or unmeasured cases explicitly; Deston retains final acceptance.

Javier's supplied short Preview traces on `d200947` show four recorded PREVIOUS
simulations matching four reported thumb-up holds, and two NEXT simulations in
an intended index-finger-only check. These are guided observations with no
independent physical-pose annotation. Earlier Practice misses, negative actions
and timing failures remain unresolved; no new full pass or active handoff is
claimed. Raw traces/profiles/exports stay private.

The separate storyboard remains a private draft. Record the manual workflow as
manual footage, show one real limitation/recovery and add a gesture segment only
after the actual gate and native observations. A script is not filmed evidence.
GF-P25 stays open until the guide and completed demo receive review. The project
presentation is a separate deliverable.

AI assistance prepared this draft from repository instructions and supplied
observations. Javier operates the Windows device; Deston reviews acceptance.
