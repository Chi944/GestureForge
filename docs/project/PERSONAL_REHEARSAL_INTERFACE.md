# GF-P12 personal rehearsal: component and Studio interface

Owner: Hau Jie. Host integration/reviewer: Deston. Updated 5 October 2026.
Status: the measurement component, current-session personal LIVE gate and Repair
pose host flow are implemented in the integration branch. A real qualifying saved
attempt is still required for each session's eligibility. Repair creates only a
reviewed TRAIN candidate from a diagnosed selected label; software verification
does not establish a new human pass.

## Implemented measurement protocol

`PersonalRehearsal` uses the actual supplied `RoutingSession` in REHEARSAL mode
and the host's persistent `Dispatcher`. It processes each prediction once and
dispatches only protected simulated events. Raw labels, manual actions and a
passed preliminary six-activation check cannot earn action-trial credit.

The sequence is ten repetitions of each of the three action IDs **and NEUTRAL**,
then ten five-second negative/transition intervals: 50 measured windows. This
explicitly includes NEUTRAL in "ten trials per pose". Each window lasts five
seconds. Each action trial requires
exactly one intended simulated action; wrong or repeated actions fail that trial.
NEUTRAL trials require accepted controller READY inside the window and no action.
Negative intervals require no action and full prediction-stream coverage.

Current pass rule: all 50 windows completed, at least 9/10 correct for
each of the four poses, all ten negative windows covered with zero actions,
no wrong/repeated action trial and no incomplete capture window. One missed
trial per pose can be tolerated; wrong actions are not tolerated. These extra
conditions prevent a nine-correct/one-wrong classifier from being certified.
The host also requires successful saving, exact event reconciliation and paused
context restoration before granting personal LIVE eligibility.

Negative cues cover absent hands, unfamiliar poses, open-palm movement and
transitions without sustained enrolled action poses. The host/operator must
review the ten instructions against the actual custom vocabulary and supply ten
appropriate replacement cues when defaults overlap a trained pose. The component
stores intended instructions, not proof that a participant physically followed
them. Record operator confirmation separately. No blanket recollection or
threshold change is requested from a failing practice attempt.

## Attach using existing resources

1. Preserve the existing context/trace, pause, obtain consent for local outcome
   recording, and temporarily configure the shared router for REHEARSAL with all
   three action bindings. Keep the persistent dispatcher; do not recreate it or
   clear its consumed IDs. Save the exact intended behavior revision using the
   existing `behavior_revision(...)`, not a newly invented hash.
2. Construct `PersonalRehearsal(router, dispatcher, revision, current_revision,
   gesture_ids, negative_cues=...)`. `current_revision` must reflect changes to
   the intended profile/model/hand/policy/bindings/workspace/targets throughout
   the attempt. Preserve the intended context revision while temporary practice
   bindings are installed. The revision is an opaque host-supplied value; this
   component cannot establish that a host supplied the correct value.
3. Embed `PersonalRehearsalWidget(attempt, private_output_root)`. The widget owns
   no camera, model trainer, launcher or second dispatcher.
4. `prepare(now)` / **Prepare next trial** resets through `router.resume()` and
   emits `snapshot_requested(snapshot)`. Attach the existing capture worker to
   that new routing generation, respecting its shutdown/identity rules. Never
   restamp queued old observations. Use the shell's existing generation change
   path; a worker restart may be needed with the current immutable capture IDs.
5. Forward controller-consumed predictions to `receive_prediction(prediction,
   received_at)` on the UI owner thread. **Do not also call the shell's ordinary
   router process/dispatch path for the same packet.** Trace recording may still
   append the packet separately. The supplied router and dispatcher remain the
   authoritative controller and recording mechanism.
6. Action/negative windows require observed NEUTRAL -> READY during preparation;
   then **Begin five-second window** starts scoring. NEUTRAL windows require a
   fresh capture packet, but acquire their READY transition inside measurement.
   The scored interval is based on capture timestamps from Begin through exactly
   five seconds. The component then drains still-fresh packets for up to the
   existing 0.2-second prediction age limit, so a packet captured inside the
   window and delivered just after five seconds can still record a late action.
   Packets captured after the five-second interval are excluded from scoring.
   The entire five seconds is observed, so rearming and emitting again records
   a duplicate rather than finishing on the first correct event. A preparation
   action cancels and preserves its event. In v3, 30 seconds without beginning
   pauses capture and returns to idle for an explicit retry of the same prompt;
   completed trial records remain unchanged. `setup_retries` records the prompt,
   routing generation, setup timestamps, reason and latest diagnostics separately.
   A setup retry is not a scored trial and cannot replace a measured miss.
   The widget calls `request_begin(now)`: it starts immediately if eligible, or
   queues the explicit click for at most two seconds. The next fresh current
   packet is processed once before evaluating the unchanged capture/READY guards.
   That setup packet earns no measurement credit. Timeout, cancellation and new
   preparation clear queued intent. `begin_window(now)` remains the strict API.
7. `capture_release_requested()` means release the worker and remain paused.
   It is emitted once per prepared trial on completion/interruption. On focus
   loss, camera faults or setup changes, call `capture_failed(reason)` or Stop.
   Host shutdown must preserve pending results; `save_error` blocks widget close
   and the host must honor it before destruction/context replacement.
8. `result_ready(PracticeResult)` supplies a frozen result after completion,
   cancellation or expiry. Save locally and present it for review. Restore the
   prior shell context paused, without automatically starting actions. A host
   behavior change prevents current gate eligibility even though historical
   terminal results remain read-only evidence. Call `passed_for` against the
   freshly computed exact revision immediately before considering a gate.

## Result and persistence

`PracticeResult` contains attempt ID, protocol version, exact behavior revision,
profile/model IDs, status/reason, immutable trial records, correct counts for
each pose, negative action count and guidance. Each trial includes intended cue,
timing, observed command/event IDs, simulated outcome, NEUTRAL readiness,
prediction count, rejection counts and coverage. Frame/feature/image data and
configured target paths are not added. Cue text is saved as entered; keep it free
of personal details and paths. Completed and interrupted trials are retained.

`result()` and `save(directory)` are read-only for terminal attempts. They do not
expire a completed/cancelled attempt, pause a later restored router, or relabel
historical evidence after the host changes context. `save(directory)` writes
`practice-<attempt-id>.json` atomically under the supplied private root; repeated
saves replace only this attempt's file. A failed write retains results in memory
for retry. The file is an evidence export, **not an importable readiness
credential**. No API loads JSON into a passed state. Before using a result, the
host must also verify protocol version, `passed_for(current_revision)`, successful
preservation and operator-confirmed real testing. Synthetic tests do not grant
readiness, and this PR does not enable LIVE gestures.

Every measured window requires fresh packets across the full interval, using the
existing 0.2-second gap/age limits. Missing frames cannot count as safe negatives.
Wrong-generation packets do not count; malformed/out-of-order packets cancel.
Otherwise valid stale packets before Begin (preparing or armed) are dropped:
reset to preparing, require fresh neutral arming, retain prior completed windows
and the original 30-second preparation deadline. Record the original phase in
capture diagnostics and advance the packet watermark without measurement credit.
Under `gf-p12-v2`, otherwise valid stale packets captured inside a measured window
are dropped, reset controller arming and advance the packet watermark. They cannot
dispatch an action. The existing five-second timer and receipt deadline continue;
the window is inconclusive and the next prompt can be prepared normally. Per-trial
coverage diagnostics retain `stale_prediction`, late-frame count and maximum age
even after preparing another trial. One inconclusive window prevents a full pass.
A stale packet captured after the scheduled end does not invalidate the preceding
window. Camera faults and revision changes still retain partial evidence and
prevent a pass. These measurement semantics continue in v3; its bounded
diagnostic uses `gf-p12-single-pose-diagnostic-v3`. Historical v1/v2 exports
remain readable without rescoring;
`passed_for` accepts only the current full protocol and behaviour revision.

## LATCHED diagnostic and remaining human checks

`python -m gestureforge.trace_diagnose PATH_TO_PRIVATE_TRACE` validates the
existing label/timing trace and reconstructs states using the current shared
controller. Output goes to ignored `experiments/local/controller-diagnostics/`.
It preserves the input, accepts unannotated recordings for diagnosis and never
computes accuracy or readiness. It reports accepted/rejected NEUTRAL, timing
gaps/ages, reconstructed states and simulated events. Compare separately noted
physical intentions and observed UI states; reconstructed state is not a camera
observation. Use matching code revisions. Scored replay still requires independent
annotations through the existing `scripts/replay_controller.py` workflow.

At preparation time no real reproduction trace was found in the project or the
older temporary Studio mirror. `scripts/check_environment.py --model` successfully
loaded the verified asset and processed a blank image on this Windows laptop
from the Unicode project path. It did not open the camera. The original
intermittent LATCHED symptom remains undiagnosed; no thresholds, data or neutral
policy have changed. The private checklist path
`experiments/local/gf-p07-p12-human-checks-20261003.md` was peer-local at the
time of Hau Jie's component preparation and is not a repository artifact.

GF-P07 still needs current-version human capture: visible invalid feedback,
Stop during an active hold, partial-slot preservation, save/reload, and the
required collection/profile recording. GF-P12 is now attached for host software
review, but it still needs current-version human practice evidence and the
`passed_for(current_revision)` revision-gate check before any readiness decision.
Neither task is marked complete by this component PR.

## Verification on Hau Jie's Windows checkout

Historical component preparation evidence from Hau Jie's Windows checkout, not
current root validation: base `36d8214`; existing Python 3.11.15 environment with this checkout on
`PYTHONPATH`. `python -m pytest -q`: **592 passed, 1 skipped** in 691.66 seconds.
`python -m ruff check gestureforge tests scripts`: passed.
`python -m mypy gestureforge scripts tests`: passed, 75 source files.
Assignment and Studio `--smoke-test`: both exit 0. `git diff --check`: passed.
The 16 focused new tests cover controller-based scoring, no external launch,
rearming, long holds, duplicate/wrong actions, absent/late frames, stale identity,
revision expiry, cancellation, save retry, widget handoff, and trace reconstruction.
These are generated-prediction software tests. The user supplied warning logs
ending at the older temporary-mirror prompt, without a fatal error. Restarting
the synchronized checkout and recording the live reproduction remain pending.

## Selected pose repair handoff on 5 October

Repair now lives in Studio as **Repair pose** via `Window.pose_repair_widget`. It uses the same observation-only capture path as Enrolment, suspends routing during collection and inherits the save-error lifecycle that preserves pending evidence until retry. It does not create a camera, classifier, dispatcher or profile loader.

Operator flow:

- Start from the installed saved personal profile. Guest/manual mode and ad-hoc manifests are disabled; save an ad-hoc TRAIN manifest as a profile before repair.
- After diagnostic review, choose exactly one vocabulary label, including NEUTRAL if that is the diagnosed label, and collect 2-12 TRAIN trials for that label only.
- Save a separate candidate only after reviewing valid-slot and retained-class counts. The candidate replaces the selected label's TRAIN rows, preserves the other TRAIN classes and original-dataset/reviewed-collection hash checks, and excludes VALIDATION, TEST and UNKNOWN rows from fitting.
- `candidate_ready` opens the Profiles review path. Only explicit permission plus **Create and load personal profile** trains and installs the candidate with the existing `ProfileStore.create` and `use_studio_profile` lifecycle. The app returns paused in Preview with readiness expired.
- Rollback uses the original saved profile through **Load selected**. A failed candidate create/load or rollback load retains the current selection and old profile.

This is own-profile targeted repair only after diagnostic need. It does not relax the full Practice gate, grant LIVE eligibility, or justify blanket recollection. Keep original-dataset/reviewed-collection hash checks, operator permission, original task ownership and branch rules with the repair evidence.
