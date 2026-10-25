# Harbor Desk demonstration and evaluation protocol

Owner: Deston · GF-P32 · Authored 30 September 2026 · Release protocol revised 24 October 2026

This is fictional product content and a test protocol, not measured results. The ten-card deck is `assets/corporate_demo_deck.json`; the local reference is `assets/corporate_reference.txt`. Load the supplied `assets/harbor_workspace.json` in Studio to use the custom-gesture six-stage runbook, or `assets/harbor_standard_workspace.json` when the loaded recogniser uses the legacy `NEXT`, `PREVIOUS` and `BOOKMARK` action IDs. Explicit **Live** supports manual stage/deck actions, bookmarks, saved sessions and validated Windows resource requests. Preview/Rehearsal simulates typed requests. Personal LIVE gestures require the user's own genuine full Practice pass in the current app session, saved and reconciled before paused restoration, then explicit Live selection, Apply, Start and fresh NEUTRAL. Loading a profile, the short check and historical/imported results cannot grant eligibility; see the [personal LIVE steps](../USER_GUIDE.md#personal-live-after-practice).

## New-user enrolment showcase

Include a **60–90 second edited onboarding segment** in the ten-minute presentation,
then demonstrate the six-stage product workflow below and explain results and
limitations. The demo video can include the same segment. This is a recording plan,
not evidence that a new user or the marker has already passed.

| Shot | What to show and explain |
| --- | --- |
| First launch | Guest/manual controls work immediately. **Open Enrolment** starts personal collection without an existing recogniser; the main camera-control Start button is for a loaded recogniser. |
| Personal choices | Enter a pseudonym, chosen hand, actual conditions and four distinct poses. Show consent before collection. Defaults are G1 = fist, G2 = thumb up, G3 = index/middle fingers raised, NEUTRAL = open palm. These are gesture IDs; the workspace determines their actions. |
| Real collection | Show **Request collection**, the correct camera preview and **Begin trial**. Include one genuine trial for each pose, with its countdown and hold. Keep the full hand visible and release between trials. |
| Clearly marked time cuts | Caption: “Time cut: full TRAIN session = 48 trials, 12 per pose.” After a real break, show the separate VALIDATION session and caption: “Separate VALIDATION = 48 trials, 12 per pose.” Show the saved session locations without exposing private paths. Do not imply four filmed trials replace all 96, or that validation was training data. |
| Save the user's profile | In **Profiles**, enter a profile name, **Browse dataset…** to the TRAIN manifest, review hand/classifier/rejection settings, confirm **Dataset permission confirmed**, then **Create and load personal profile**. Show the actual separate validation result if available; never substitute another user's result. |
| Qualify and use | Configure the intended workspace/camera before **Open Practice**. Show a real window, then a labelled time cut to the actual saved outcome. Only a complete current-session pass can be followed by explicit Live, Apply, Start and fresh NEUTRAL. Demonstrate one action per hold and neutral rearming. If Practice fails, show the limitation and manual fallback instead of implying a pass. |

The complete Practice protocol remains **22 five-second windows**: three trials of
each of G1/G2/G3/NEUTRAL (12), plus ten negative/transition windows. Preparation
adds time. All windows need full coverage and correct outcomes: each pose 3/3,
zero wrong/repeated actions, and no action in negative windows. Separate failed
attempts cannot be edited together into a pass. The default controller requires
300 ms NEUTRAL and 400 ms command holds; a five-second command hold must produce
only one action. A standard fresh launch uses kNN, distance multiplier 1.5 and
ambiguity margin 1.5, but saved profiles retain their own settings: show the actual
values and do not loosen them to make the recording pass.

Configure the screen recording separately and obtain permission from anyone
shown. Studio's normal numeric collection does not record video. Keep unedited
numeric outcomes and the reported limitations; an edited showcase is not a
continuous verification record. The presentation should explain the problem:
trainers move between explanatory cards and local demonstration resources, and
GestureForge offers deliberate hands-free requests while preserving manual
control and explicit confirmation of external outcomes.

### Marker's own profile

The marker can first inspect Guest/manual features without a camera or dataset.
For personal gestures, use their own consented enrolment, saved profile and
current-session Practice workflow above; another person's qualifying profile or
old Practice export does not qualify the marker. Follow the
[collection guide](../USER_GUIDE.md#collect-in-studio),
[Practice guide](../USER_GUIDE.md#personal-practice) and
[Mac setup guide](../MACOS.md) rather than relying on time-cut video instructions.

On Mac, earlier browser-collector recordings support browser collection only;
they do not establish native Studio installation, enrolment or Live operation.
Native Apple Silicon Studio still needs destination-machine verification.
External desktop resource launches are Windows-only; on Mac demonstrate internal
cards, bookmarks and runbook state, with external requests simulated in Preview.
Do not present the Windows six-stage resource-launch recording as a Mac run.

## Six-stage runbook

The custom workspace implements the mappings below with literal `G1`, `G2` and `G3` pose IDs. The standard variant keeps the same columns but uses literal `NEXT`, `PREVIOUS` and `BOOKMARK` pose IDs; those IDs are still independent of the mapped stage action. A vocabulary mismatch leaves gestures unavailable while the manual stage buttons remain usable; Studio does not remap arbitrary imports. Stage changes show the linked card and stay paused; gesture control requires an explicit Start and fresh NEUTRAL. Selecting an existing authored stage preserves a valid personal LIVE grant; editing its action map expires it. Stages never open a resource automatically. Previous-stage and Continue/Finish buttons are always present.

| Stage / linked card | Presenter instruction | G1 | G2 | G3 | Completion evidence |
|---|---|---|---|---|---|
| 1 / `welcome` | Explain the fictional purpose; browse outcomes/team cards | NEXT | PREVIOUS | ADVANCE_STAGE | Presenter acknowledges the purpose, then continues |
| 2 / `budget` | Open Calculator, calculate 240 credits, return and resume | ADVANCE_STAGE | OPEN_SHORTCUT `calculator` | BOOKMARK | Correct answer acknowledged separately from launch request |
| 3 / `reference` | Open the reference; identify the training coordinator | ADVANCE_STAGE | OPEN_SHORTCUT `product-reference` | BOOKMARK | Correct contact acknowledged after return/resume |
| 4 / `resources` | Open the resource folder and locate the reference file | ADVANCE_STAGE | OPEN_SHORTCUT `resource-folder` | BOOKMARK | File located and acknowledged |
| 5 / `discussion` | Bookmark this point, recover from a missing dedicated test reference, then pause/save/reload | ADVANCE_STAGE | OPEN_SHORTCUT `recovery-reference` | BOOKMARK | One bookmark; useful error; successful retry; paused reload with no launch replay |
| 6 / `finish` | Review stage outcomes and one recognition limitation | ADVANCE_STAGE (Finish) | PREVIOUS | BOOKMARK | Summary distinguishes launches, actual acknowledgements and failures |

Cards `outcomes`, `team`, `recovery` and `resume` supply supporting instructions; all ten cards remain reachable through the viewer. ADVANCE_STAGE on the last stage finishes once and does not wrap or replay actions.

## Local resource binding

- `calculator`: built-in Windows Calculator adapter.
- `product-reference`: this machine's copy of `assets/corporate_reference.txt`.
- `resource-folder`: the local folder containing that reference.
- `recovery-reference`: a disposable copy of the reference created specifically for the test. Configure and test it, move only that copy aside, demonstrate the missing-target error, then restore/rebind it. Never manipulate another user's genuine files.
- Optional `product-help`: explicitly bind `https://example.com` as a clearly labelled placeholder website; it is not real Harbor Desk help. Test HTTPS separately; omit from offline core timing.
- Camera is a separate handoff check: pause, confirm capture-worker shutdown, request Windows Camera launch, return, close the other camera consumer as necessary, and resume manually. Do not make this a prerequisite for the six-stage product task.

Portable workspaces export only semantic shortcut IDs and labels. Paths, URLs, personal profiles and target bindings stay on each machine. Test each binding using a button before enabling its gesture. Record `launch requested`, failure or explicit task acknowledgement separately.

## Manual walkthrough available now

This is a development acceptance run, separate from the later participant comparison. No webcam, profile or new gesture samples are needed.

Javier executes this walkthrough after the software checkpoint is reviewed and supplies the observed outcomes to Deston for integration and final acceptance review. Camera/recognition evidence is a separate follow-up, not a prerequisite for this manual run. Javier may run personal LIVE cases only after his own qualifying current-session full Practice pass; those observations remain separate from manual Harbor and participant acceptance.

1. Run `.\run.cmd --studio`, click **Open Setup**, then scroll inside the right-hand panel to **Load workspace...** and select `assets/harbor_workspace.json` for the custom manual walkthrough. Use `assets/harbor_standard_workspace.json` when the loaded recogniser uses the legacy `NEXT`, `PREVIOUS` and `BOOKMARK` action IDs. Return to the top of Setup, where **Studio action mode** and **Apply and pause** appear before dataset, camera and readiness controls. Select **Live**, then click **Apply and pause**. Confirm the status says **Manual LIVE ready**. Disabled camera/readiness buttons do not prevent this manual walkthrough.
2. In **Quick Actions**, create the four required targets above using their exact opaque IDs. Save each target. Local target edits pause Studio and preserve the active runbook stage. **Use Quick Actions** explicitly switches to standalone slots; it is unnecessary for this runbook walkthrough.
3. Return to **Runbook**. Perform stages 1–4 using their labelled action buttons and **Continue**. Observe each opened application/resource yourself; use **I completed this stage's task** only after the requested task succeeds. A launch request alone is not completion. No camera restart is needed for manual buttons.
4. At **discussion**, bookmark once. Move only the disposable recovery reference aside and request it. Confirm a useful failure and an increased **Failed** count. Restore/rebind that test file, verify the context still says `discussion`, then explicitly retry once. Repairing or returning to Studio must not open it automatically. In a personal gesture run, rebinding/editing the target expires its LIVE grant; record manual fallback or a new full Practice pass separately before further gesture use.
5. Export the current results from **Session summary** before **Save session...** and **Restore session...**. Reload must preserve the discussion stage and bookmark, return Live mode to paused Preview and replay no launch. For this development walkthrough only, verify that a typed action simulates, then explicitly select Live and Apply and pause again before continuing real manual actions. Restoration archives the previous results locally and starts a new summary; keep both segments for the walkthrough record. The simulation probe stays in these exports and disqualifies them as successful measured-study conditions; do not reuse this walkthrough as participant-study evidence.
6. Continue to **finish**, review the results, acknowledge actual completion and select **Finish**. Export the final segment. Record the source commit, Windows version, device, actual failures/retries and observed outcomes under ignored `experiments/local/`. Do not label this manual run as gesture or participant-study success.

`tests/test_app_dispatch.py` also runs the six-stage Guest/manual flow with a fake launcher and disposable files, including repair, context attribution, save/reload and no replay. That regression checks software integration; it does not prove that an external application appeared or a person completed its task.

## Evaluation procedure fixed before collection

Revision 5 replaces the planned three-condition unfamiliar-presenter study with a manual-versus-personal engineering case study using at least one consenting available team operator. No new external recruitment or starter qualification is required. Preserve existing frozen TEST results and historical M/S/P evidence unchanged; do not tune against TEST. Freeze the release profile, rejection and hold settings before this comparison, and keep pseudonymous records and permissions locally. Record the operator's team role and prior familiarity privately so the report can disclose the lack of independent usability validation.

1. Record OS, camera, lighting/framing, selected hand, source commit, workspace revision and model/data/config hashes. Use the same equipment, content and task sequence for paired comparisons.
2. Provide the same scripted introduction and untimed familiarisation for each condition. Record training/readiness time separately from task time. Manual control requires no recognition check. A personal gesture condition requires that participant's own genuine current-session full Practice pass, terminal save, exact event reconciliation and paused restoration before explicit Live selection, Apply, Start and fresh NEUTRAL. The supplied starter is deferred; do not manufacture an S attempt for this M/P protocol. The existing full Practice protocol remains 22 windows with its unchanged pass conditions.
3. Compare manual buttons/keyboard (M) and personal gestures (P). Declare M–P or P–M before starting and record the actual order and prior practice. If a second operator is readily available, reverse the order; do not delay the release to recruit one. A single-operator case study cannot separate order, familiarity or learning effects or establish general user benefit.
4. Run the six-stage task with the prescribed safe missing-reference failure. Start the task timer on the participant's first task instruction; stop after Finish and summary review. Count help, retries, wrong actions and actual acknowledgements. Save/reload and focus-loss recovery are part of the task.
5. If recognition/readiness fails, record failure and elapsed time. Allow manual completion for usability, but report it as fallback rather than gesture success. Stop an individual condition after 15 minutes, participant withdrawal, or unrecoverable fault; report incomplete tasks instead of discarding them.
6. Optional comfort/usefulness ratings may be recorded from 1 (poor) to 5 (good); leave uncollected ratings null. Record observed limitations, assistance and errors. Report the individual result and small-sample limits, without significance or commercial-demand claims.

**Keep preparation separate from the measured task.** Practice and familiarisation
can add simulated outcomes to the current Session summary; exporting alone does
not clear it. After setup/readiness finishes, export those preparation results,
then use **Restart deck** before the first task instruction. This archives the
previous summary, starts a fresh one and returns Harbor to its first stage.
Confirm the summary is empty and the appropriate current-session readiness is
still valid before starting the measured condition; a reset cannot grant readiness.
Keep preparation exports alongside the study as separate evidence, outside that
condition's task `summary_segments`.

**Measured reload differs from the development simulation probe.** During the
timed task, export before restoring, observe the restored stage/bookmark, paused
Preview and absence of automatic replay, then explicitly select **Live** and
**Apply and pause** before the next real action. For gestures, retain valid
current-session readiness, then Start and show fresh NEUTRAL. Do not request the
development-only simulated action. Keep both task segments. If any simulation
does occur after the task starts, preserve it and report the execution mismatch;
do not remove rows, discard a segment or reset the summary to manufacture success.

## Measures and success criteria

| Measure | Definition / target |
|---|---|
| Recognition | Trial majority across five scheduled samples; no majority/invalid/rejected genuine poses count UNKNOWN. Per-person macro-F1: personal ≥0.90. Preserve the historical held-out starter target ≥0.85 and its results, but starter delivery is deferred |
| Setup cost | Record personal enrolment/readiness separately from task time. The historical ≤120-second standard first-action promise is deferred with starter delivery |
| Workflow completion | Six stages and required acknowledgements, correct budget/contact, one discussion bookmark, paused reload, visible recovery; report actual completion and fallback |
| Duplicate protection | Twenty five-second command holds per profile across enabled actions; target zero duplicates; neutral between trials |
| Negative activity | Ten minutes per profile; target ≤1 unintended viewer action and zero unintended external launches; prescribed non-command movements/poses recorded |
| Latency | Annotated stable-pose onset to controller action request; p95 <1 second including hold. External app opening delay measured separately |
| Efficiency | Task time, action errors, retries, help requests and completed stages per condition; present all participants, no cherry-picked fastest run |
| Stability | Thirty-minute run, observation rate, peak process memory, faults and clean camera shutdown; independent Windows installation and offline local workflow |

Targets are prospective, not passed checks. Use a simulated dispatcher for the paired controller-protection on/off replay of identical predictions. Live tests retain protection. Do not run an unprotected external launcher for comparison.

### Controller replay tool (GF-P20 preparation)

Run the same annotated prediction trace through the actual rehearsal routing/controller and a naive baseline that emits one simulated action for every accepted mapped frame:

```powershell
.\.venv\Scripts\python.exe scripts/replay_controller.py --trace experiments/local/annotated-trace.json --output experiments/local/replay-report.json
```

This tool never calls the viewer or an operating-system launcher. The baseline deliberately removes activation protection; it is not a competing recognition algorithm. Both conditions receive identical classifier outputs, so this experiment isolates controller behaviour rather than comparing classifiers.

Use a new output filename for each run. Existing traces and reports are never overwritten. The completed report is published atomically using a local filesystem hard link; if the destination filesystem does not support that operation, the command fails without publishing a partial report. Use the project's local NTFS workspace on Windows.

| Trace field | Required meaning |
|---|---|
| `schema_version` | Integer 1 |
| `session_id`, `profile_id`, `model_version`, `context_id` | Identifiers for one uninterrupted capture session and fixed context/model |
| `bindings` | One to three gesture IDs mapped to typed action objects, such as `{"NEXT": {"kind": "NEXT"}}`; shortcut actions contain only a semantic `shortcut_id` |
| `frames` | Ordered rows containing `frame_id`, monotonic capture `timestamp`, `label`, boolean `accepted`, and a nonempty `rejection_reason` for rejected frames |
| `received_at` (per frame) | Monotonic processing time, including capture/processing delay. If omitted, the tool assumes it equals capture time and explicitly reports that limitation |
| `expected_holds` | Observer annotations with stable-pose `start`, release `end`, and intended `command`. Windows must not overlap and must lie inside recorded coverage. An empty list means a deliberately annotated negative-activity trace |

Include neutral/release frames, invalid detections and negative activity; do not export only successful poses. Keep annotations independent of predicted labels. Normal command-only application logs are insufficient because they omit predictions that did not trigger an action. This tool consumes supplied traces; Studio can now record these controller inputs with the opt-in procedure below; participant collection and independent annotation still require people. Split recordings at pause, profile/model/context changes and capture restarts.

**Record a new trace:** open Studio, load your personal dataset, select Preview or Rehearsal and check **Record evaluation trace (labels and timing only)** before Start. Confirm participant permission for this evaluation. Start, perform the planned neutral/hold/negative sequence, then Pause. A local `experiments/local/controller-traces/trace-*.json` is saved and the UI shows its path. Pause, focus loss, camera failure or reconfiguration ends that segment; a new Start records a new file. No camera images, landmarks or feature vectors are included. Recording is off by default, applies only to Studio and does not turn simulation into desktop control.

The recorder saves the predictions actually consumed by the controller, including rejected inputs, with their original capture and processing timestamps. The latest-frame mailbox can discard intermediate camera frames, so this is a controller-input trace, not every sensor frame. Frame IDs can start at zero and have gaps. At 18,000 inputs, recording pauses before processing another input; the saved trace covers only its recorded interval. Saving never overwrites existing files. If storage fails, keep the app open, fix the storage problem and press Pause to retry; buffered evidence is retained. Capture restart, closing, deck reset, camera/configuration changes and dataset/model replacement wait until it is saved.

**Before scoring:** preserve the original and make an annotated copy. Record source commit, actual collection conditions, annotator, annotation method and timing uncertainty alongside it. Use an independent observer or separately consented, synchronised recording to identify stable-pose onsets/releases; never derive the intended pose from the classifier output. Fill `expected_holds` using the same monotonic seconds as `frames[*].timestamp`, then set `annotation_complete` to `true` in the copy. For a deliberate negative-only session, explicitly confirm the empty hold list. New recordings default to `false` and the replay tool refuses to score them. Legacy hand-authored traces without this field remain supported. Without reliable independent timing, do not claim the latency target from these traces.

The report records the input checksum, controller timing settings, simulated event traces, correct/missed holds, duplicate and unintended actions, and latency from annotated onset to the first matching request. Events outside their matching hold window count as unintended; late arrivals can therefore count as both a missed intended hold and an unintended request. Nearest-rank p95 uses only successful first actions and is null if none succeed; always interpret it beside misses. Keep real recordings and reports under ignored `experiments/local/` with the source commit and actual annotation method/uncertainty. Synthetic traces verify this tool, not the project's participant or live-performance targets.

## Minimal local records and reviewer handoff

Store under ignored `experiments/local/`: one session record per participant/condition with `participant_id`, condition/order, source/model/config/workspace revisions, setup/readiness/task durations, completed stages, errors/retries/help/fallbacks, comfort/usefulness, actual environment and limitations. Event rows need monotonic time, source (`manual`/`gesture`), session/context/event IDs, typed action, simulated flag and outcome. Avoid raw video, document contents and full target paths in ordinary logs.

Timing annotations require explicit participant permission if an optional recording is used; otherwise use observer timestamps and report timing uncertainty. Never convert launch acceptance into success automatically. Deston reviews complete event traces against outcomes, Hau Jie provides recognition results, and Javier checks dispatcher/recovery evidence. This document completes scenario/protocol authoring; execution and final evidence remain GF-P16/P18/P19/P20/P23.


### Workflow comparison tool (GF-P20 preparation)

Use the [workflow comparison guide](WORKFLOW_COMPARISON.md) to combine explicit
observer records with the existing exported SessionSummary segments. The CLI
retains readiness failures, incomplete tasks, withdrawals and manual fallback;
it never infers task completion from a launch request or substitutes action
timestamps for the observer's task timer. It reports individual condition results,
missing conditions and comparable paired times without statistical significance
or commercial-demand claims.

This is preparation for the protocol above. Software fixtures do not establish
participant performance, and the tool cannot verify an observer's assertions or
enable LIVE gestures. Keep actual records, exports and results local.
