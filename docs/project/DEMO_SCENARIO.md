# Harbor Desk demonstration and evaluation protocol

Owner: Deston · GF-P32 · Authored 30 September 2026

This is fictional product content and a test protocol, not measured results. The ten-card deck is `assets/corporate_demo_deck.json`; the local reference is `assets/corporate_reference.txt`. Javier integrates these through the validated workspace/runbook importer. The current Studio preview does not yet execute this runbook, persist bookmarks or open resources.

## Six-stage runbook

These are authoring instructions for the agreed stage editor, not a second executable workspace schema. G1/G2/G3 mean the selected profile's three action IDs; display the actual gesture names and current action meanings. Map every slot explicitly. Stage changes show the linked card and require neutral; they never open a resource automatically. Previous-stage and Continue/Finish buttons are always present.

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

## Evaluation procedure fixed before collection

Recruit at least two consenting participants who did not contribute to starter training/tuning and are unfamiliar with this scenario. Hau Jie collects their personal TRAIN/VALIDATION/TEST sessions with whole-trial separation. Freeze starter/personal configurations, rejection and hold settings before opening TEST outcomes. Availability and consent are not assumed. Keep pseudonymous records and actual permissions locally.

1. Record OS, camera, lighting/framing, selected hand, source commit, workspace revision and model/data/config hashes. Use the same equipment, content and task sequence for paired comparisons.
2. Provide the same scripted introduction and untimed familiarisation for each condition. Record training/readiness time separately from task time. Manual control requires no recognition check; gesture conditions must pass their specified simulated check before LIVE.
3. Compare manual buttons/keyboard (M), starter gestures (S) and personal gestures (P). With two participants use M–S–P and P–S–M; this balances endpoints only, not all order effects. Report that limitation. With six participants use all six permutations. Record the actual order and prior practice.
4. Run the six-stage task with the prescribed safe missing-reference failure. Start the task timer on the participant's first task instruction; stop after Finish and summary review. Count help, retries, wrong actions and actual acknowledgements. Save/reload and focus-loss recovery are part of the task.
5. If recognition/readiness fails, record failure and elapsed time. Allow manual completion for usability, but report it as fallback rather than gesture success. Stop an individual condition after 15 minutes, participant withdrawal, or unrecoverable fault; report incomplete tasks instead of discarding them.
6. Ask each participant to rate comfort and usefulness from 1 (poor) to 5 (good), then give one limitation and one improvement. Report individual values and small-sample limits, without significance or commercial-demand claims.

## Measures and success criteria

| Measure | Definition / target |
|---|---|
| Recognition | Trial majority across five scheduled samples; no majority/invalid/rejected genuine poses count UNKNOWN. Per-person macro-F1: personal ≥0.90, held-out starter ≥0.85 |
| First-use time | Camera ready to first successful standard action, including readiness check; target ≤120 seconds; installation time reported separately |
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

The recorder saves the predictions actually consumed by the controller, including rejected inputs, with their original capture and processing timestamps. The latest-frame mailbox can discard intermediate camera frames, so this is a controller-input trace, not every sensor frame. Frame IDs can start at zero and have gaps. At 18,000 inputs, recording pauses before processing another input; the saved trace covers only its recorded interval. Saving never overwrites existing files. If storage fails, keep the app open, fix the storage problem and press Pause to retry; buffered evidence is retained and capture restart/close is blocked until it is saved.

**Before scoring:** preserve the original and make an annotated copy. Record source commit, actual collection conditions, annotator, annotation method and timing uncertainty alongside it. Use an independent observer or separately consented, synchronised recording to identify stable-pose onsets/releases; never derive the intended pose from the classifier output. Fill `expected_holds` using the same monotonic seconds as `frames[*].timestamp`, then set `annotation_complete` to `true` in the copy. For a deliberate negative-only session, explicitly confirm the empty hold list. New recordings default to `false` and the replay tool refuses to score them. Legacy hand-authored traces without this field remain supported. Without reliable independent timing, do not claim the latency target from these traces.

The report records the input checksum, controller timing settings, simulated event traces, correct/missed holds, duplicate and unintended actions, and latency from annotated onset to the first matching request. Events outside their matching hold window count as unintended; late arrivals can therefore count as both a missed intended hold and an unintended request. Nearest-rank p95 uses only successful first actions and is null if none succeed; always interpret it beside misses. Keep real recordings and reports under ignored `experiments/local/` with the source commit and actual annotation method/uncertainty. Synthetic traces verify this tool, not the project's participant or live-performance targets.

## Minimal local records and reviewer handoff

Store under ignored `experiments/local/`: one session record per participant/condition with `participant_id`, condition/order, source/model/config/workspace revisions, setup/readiness/task durations, completed stages, errors/retries/help/fallbacks, comfort/usefulness, actual environment and limitations. Event rows need monotonic time, source (`manual`/`gesture`), session/context/event IDs, typed action, simulated flag and outcome. Avoid raw video, document contents and full target paths in ordinary logs.

Timing annotations require explicit participant permission if an optional recording is used; otherwise use observer timestamps and report timing uncertainty. Never convert launch acceptance into success automatically. Deston reviews complete event traces against outcomes, Hau Jie provides recognition results, and Javier checks dispatcher/recovery evidence. This document completes scenario/protocol authoring; execution and final evidence remain GF-P16/P18/P19/P20/P23.
