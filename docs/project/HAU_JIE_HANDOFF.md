# Hau Jie implementation brief

You own recognition and personalisation for GestureForge Studio. Build the reusable AI and profile components; Deston owns integration and final acceptance. Read `TEAM_GUIDE.md` and `CONTRACTS.md` first. Work is assigned for the project due 7 November 2026; the assignment is already submitted.

## Next delivery — assigned 7 October

Work through H1–H4 below, returning each useful delivery separately. This order
supersedes the older recording instructions later in this brief. New independent
evaluation participants are needed for GF-P17/GF-P18; this is separate from
repairing or repeating the existing P01/P02/P03 development recordings.

| Priority | Work you execute | Return to Deston | Completion boundary |
|---|---|---|---|
| H1 — saved-report diagnosis | Run D1 in [STARTER_FAILURE_ANALYSIS.md](STARTER_FAILURE_ANALYSIS.md): reconcile the matching baseline and diagnostic, all six folds and the fixed ten cases. Do not repeat the 48-setting search. | A focused aggregate evidence PR with source/configuration/input hashes, reconciled counts, each case or its documented absence, limits and one supported next hypothesis. Keep private inputs separate. | D1 can finish with an unresolved physical cause. Missing notes cannot establish orientation, lighting or pose as the cause. |
| H2 — independent evaluation inputs | Coordinate two new consenting participants excluded from starter fitting **and tuning**. Prepare each person's separate personal TRAIN/VALIDATION sessions using the exact shared standard poses/hand. Disclose all development inputs and selected settings to Deston. | Private numeric manifests/sidecars, permission scope, pose descriptions, split/session provenance, hashes and the proposed [paired configuration](PAIRED_EVALUATION.md). After Deston's freeze review, collect separate untouched TEST sessions, retaining every scheduled invalid/rejected slot. | Freeze before collecting/scoring TEST. Deston reproduces and accepts GF-P18. Poor scores remain valid results; they do not approve a standard starter for deployment. Do not tune on TEST. |
| H3 — operate laptop B | Follow Javier's agreed GF-P19 matrix and the [Windows guide](../WINDOWS_LAPTOP.md) on your physical laptop. Use a fresh setup, local bindings and the same identified build. Run offline core, thirty-minute Studio stability and clean shutdown checks for GF-P23. | Per-case outcomes to Javier: actual operator/device/build/package identity, help or guide deviations, failures/retries, duration, observation rate, peak memory, shutdown and private evidence references. Explicitly identify anything unmeasured or unrun. | Manual cases need no model. Gesture cases use your own profile and full current-session Practice gate. Javier consolidates; Deston accepts after the original defect gates. |
| H4 — report preparation | Draft GF-P24 methods, data protocol, algorithm trade-offs, rejection, attribution and limitations now from the implemented code and saved evidence. Add final results after GF-P18/GF-P21. | Local Word methods/results contribution and verified reference list through the team's existing channel; measured and unmeasured results clearly separated. | Keep Word documents/data/logs out of Git. A methods draft is useful now; GF-P24 is Done only when final results and limits match the evidence. |

**First handoff:** send H1 as a small PR; include the H2 recruitment/input status
without claiming that participants have already been recruited or recorded.
Participant preparation and H3/H4 may proceed while diagnosis is reviewed.
If a file, permission or participant is unavailable, report that exact missing
item and continue the independent work. Do not ask Deston to repeat long trials
or collect the same development data again without a diagnosed need.

**8 October first private handoff to Deston:** provide the existing complete
multi-person consented numeric manifests and NPZ sidecars, or the exact missing
status for any item. Include the fixed default baseline report, the 48-candidate
comparison result reports, the saved diagnostic covering all six folds and the
fixed ten cases, or the exact reason any report is absent. Include configuration,
source/dependency/input hashes, pose descriptions, session provenance and
permission scope, including the standard IDs `NEXT/PREVIOUS/BOOKMARK/NEUTRAL`
and Right hand required by the starter contract. Send private data only through
the team's private folder/archive; never put it in GitHub or Trello. The PR on `codex/hau-jie-profiles`
should contain only sanitized aggregate evidence and stay unmerged for Deston's
review. Do not record new starter data until D1 identifies a diagnosed need.
Preserve the original input labels and report any mismatch; the listed IDs are
the release contract, not permission to relabel existing recordings silently.

Copy this first private message to Deston:

> I will send the existing starter audit packet now: consented numeric
> manifests/NPZ sidecars, fixed baseline, 48-candidate reports, saved D1
> diagnostic for all six folds and fixed cases, hashes, legacy vocabulary,
> Right hand, pose/session provenance and permission scope. If anything is
> missing I will state the exact missing item. I will keep raw data private,
> put only sanitized aggregate evidence on `codex/hau-jie-profiles`, and record
> no new starter data unless D1 diagnoses a need.

For H2, follow the existing freeze-and-score commands in
[PAIRED_EVALUATION.md](PAIRED_EVALUATION.md). Preserve the freeze file and hashes
before TEST exists. A qualifying deployment starter is a separate GF-P10 gate;
it is not a prerequisite for reporting an honest failed GF-P18 comparison.
Do not identify existing development contributors as unseen participants. The
existing audit packet supports the D1 decision now; a deployable GF-P10 release
candidate later requires qualifying person-separated independent results and
explicit permission to distribute the bundle. Internal access for review is not
redistribution approval.

Every PR must name the task IDs, base/source commit, changed files, actual check
results, evidence limits and private handoff references. Push only
`codex/hau-jie-profiles`, open a PR to `main` and leave it for Deston's review.
Deston retains shared-shell changes, freeze approval, integration and acceptance;
delegated execution does not change the original task weights or Done status.


**Starter integration update, 5 October:** Deston implemented the approved-release loader and separate standard six-action LIVE gate. No candidate is enabled: the recorded 48-setting comparison found none qualifying. Diagnose the existing starter through the saved private D1 audit; use selected-pose repair only for a diagnosed own-profile need. H2's new independent evaluation and H3/H4 can proceed separately. A later deployment release needs the exact frozen TRAIN manifest/sidecar, all estimator settings, expected rebuilt revision, person-separated evidence and distribution permission for review. See CONTRACTS.md. Keep existing private inputs private.

GF-P16's standard-gesture path remains blocked wherever it depends on a
qualifying GF-P10 starter. Personal LIVE software and manual workflows can
continue under their separate Practice, explicit LIVE and native-evidence gates.

## Laptop B assignment confirmed 5 October

**7 October clarification:** Javier's PR #26 is accepted as partial laptop-A
evidence. Its conflicting operator statement was corrected during review:
you still operate laptop B and Javier coordinates. No laptop-B result was
included. Do not repeat his accepted laptop-A checks or the full starter search;
continue your D1 saved-report diagnosis and your assigned device checks.

For the integrated restore check, sync the current main before testing:
Restore session and Restore progress must return Live mode to paused Preview,
preserve saved stage/card/bookmarks and launch nothing. Explicitly select Live
and Apply and pause again before continuing manual real actions. Record your
own device result; the regression test alone is not native acceptance.

Your physical Windows laptop is **laptop B**. Javier's existing computer remains laptop A; he does not need to obtain another machine. You operate laptop B, Javier coordinates the GF-P19 case matrix and consolidates the evidence, and Deston reviews integration and GF-P23 release acceptance. Device assignment does not mean tests have passed or change the original task weights.

Use a fresh installation of the current Studio source package following `docs/WINDOWS_LAPTOP.md`; do not copy another computer's `.venv`, private targets or profile. Record the exact commit/package hash, Windows/Python versions, camera index, operator and any assistance. Bind your own local targets. Manual Harbor and shortcut checks need no profile. Gesture cases use your own consented profile and the existing current-session Practice gate; retain unrun cases when that gate is unavailable.

Coordinate with Javier using his brief's GF-P19 and GF-P23 procedures: target launch/error/recovery, focus return/no replay, actual active-capture Camera handoff, paused reload, then offline local operation and a thirty-minute Studio workflow with clean shutdown. An HTTPS page itself is not an offline-core check. Preserve failures, retries, source identities and separate summary segments. Keep full traces, private paths and recordings local; send Javier the concise per-case outcomes and private evidence references through the team's existing channel. Attribute every observation to laptop B and you as operator. Do not repeat accepted laptop-A work.

Your next GF-P12 work is operator validation of the integrated **Repair pose** flow, not rebuilding the component. Complete the saved-report D1 diagnostic in `STARTER_FAILURE_ANALYSIS.md` before proposing new training or feature changes. No blanket data recollection is requested.

## Your branch and delivery rule

Create `codex/hau-jie-profiles` from the published `origin/main` before editing. Do not apply the old kickoff patch on top of it. If it already exists, switch to it instead. Commit and push only to this branch; never push to `main` or Javier's branch.

```powershell
git fetch origin
git switch -c codex/hau-jie-profiles origin/main
git branch --show-current
# After reviewing your changes, committing and passing the required checks:
git push -u origin codex/hau-jie-profiles
```

Before every commit/push, confirm the current branch is `codex/hau-jie-profiles`. Open a PR from this branch into `main`, request Deston's review, and leave it unmerged. Only Deston integrates approved work into `main`; do not force-push shared history.

## Supporting procedures and earlier integration evidence

Use the following recognition/profile procedures when H1 diagnoses a need or a
specific H3 gesture case requires them. They are not prerequisites for the new
H2 participant preparation or H4 methods draft. Fix a reproducible software fault
before repeating an affected recording; preserve earlier failures.

**Acceptance update, 5 October:** GF-P28 is Done as a completed feasibility
investigation with no qualifying starter. Review accepts your supplied
person-separated results and the recorded internal-use permission limits; it
does not claim an independent P02/P03 rerun or permit redistribution. Do not
repeat the spike simply to obtain a successful result. The later final-data and
configuration gate remains GF-P17.

**GF-P12 Repair pose integration:** use the delivered Studio **Repair pose** tab
only after diagnostic review identifies one weak label in your own saved profile.
The source is the installed saved profile; Guest/manual mode and ad-hoc manifests
are disabled. Collect 2-12 trials for the chosen label through shared
observation-only capture, then save a separate TRAIN candidate after reviewing
valid-slot and retained-class counts. Preserve unaffected classes, the original
dataset/profile, original dataset and reviewed collection hashes and permission
notes. Keep
UNKNOWN and held-out TEST samples out of training. `candidate_ready` opens
Profiles review; only explicit permission plus **Create and load personal
profile** trains/loads the candidate, paused in Preview with readiness expired.
Rollback by loading the original saved profile. This targeted-recollection path
is distinct from running another full human Practice attempt.

1. **Compatibility first.** Use your existing consented personal TRAIN manifest
   or saved profile. Check vocabulary, selected hand, feature version and
   model/settings revision; verify load, save/reload and preservation of the
   previous selection on a failed load. **Return:** the source revision,
   pseudonymous profile/data identity, actual settings, each outcome and any
   reproducible error. A workspace/deck selected as a dataset is a file-selection
   error, not a reason to recollect gestures.
2. **Short own-profile diagnostics.** Establish reliable load/start and fresh
   capture, then use individual five-second pose/NEUTRAL diagnostics as needed.
   For a recognition miss, retain coverage, prediction/rejection output and
   independent intended-pose notes; use the existing opt-in trace for the
   open-palm/LATCHED report. **Return:** actual correct/wrong/missed/inconclusive
   outcomes, timing/coverage and a focused reproduction. Stop to diagnose setup
   faults instead of restarting a full Practice run.
3. **GF-P07 accepted; do not repeat the walkthrough.** The reviewed generated
   UI montage closes the original software recording obligation together with
   your attributed PR #20/#22 physical collection/invalid/Stop evidence. Preserve
   those records. No new recognition accuracy or human Practice pass is implied.
   Your next repair task is the integrated selected-pose workflow specified above.
4. **GF-P12 after reliable setup.** Run the full fifty-window protocol on your
   own profile only after the focused checks support it. **Return:** the full
   private Practice JSON reference, code/model/behaviour revisions, per-pose and
   negative-window outcomes, coverage, interruptions and Session summary event
   reconciliation. Retain every miss, inconclusive window and prior attempt;
   an incomplete attempt is evidence, not a pass. Verify all 50 windows are
   covered, every pose including NEUTRAL reaches at least 9/10 correct, there
   are no wrong activations and all ten negative windows are correct. Record
   whether saving, event reconciliation and paused restoration completed and
   whether the host granted personal LIVE eligibility. A blocked/failed result
   remains useful evidence; diagnose a software fault with a short reproduction
   before repeating the full run.

Put a concise outcome summary and exact software check results in a focused PR;
keep participant inputs, recordings and full result files private. Fix only your
owned modules and report shared-shell defects to Deston with the reproduction.
Do not ask Deston to repeat long trials for this lane. Your own-profile results
cannot replace or be labelled as Deston's P01 personal-performance evidence.
Request only narrowly targeted repair samples for a diagnosed collection defect.
Original task ownership/weights and acceptance criteria remain unchanged; neither
delegation nor a diagnostic result establishes readiness or LIVE permission.

**Personal LIVE boundary:** only the host's genuine current-session full pass
can grant eligibility, after terminal save, exact event reconciliation and
paused restoration. It is memory-only and pins profile/model/hand/camera,
behavior revision and exact workspace/stage/Quick Actions maps. Behavior, map,
target or camera edits expire it even if changed back; restarting Studio, Guest
and model reload clear it. Cosmetic renames, ordinary pause and existing context
selection retain it, but LIVE selection, Apply, explicit Start and fresh NEUTRAL
remain required. Short checks, diagnostics and historical/imported JSON cannot
grant it. This is software eligibility, not new participant or native acceptance;
standard gestures remain unavailable. Configure intended mappings before the
full run and keep your branch and evidence separate from Javier's.

**GF-P17 preparation, 5 October:** Deston is supplying the
[frozen paired evaluation tool](PAIRED_EVALUATION.md) and positive TEST collector
support. Reuse these rather than building another scorer. Keep all fitting and
tuning manifests, selected settings, hand and exact standard-pose descriptions
ready for review. New TEST data require a separate manifest and matching pose ID;
freeze before inspecting outcomes. Legacy development files stay unchanged.
The 7 October H2 assignment now makes this an immediate preparation task;
it does not request repetition of Deston's development recordings.

Latest integration, 4 October: sync main before recording. Practice v3 queues
Begin for up to two seconds while waiting for fresh capture/READY, and a
30-second setup timeout offers Retry setup without ending the 50-window attempt.
Setup retries are saved separately; measured misses/inconclusive windows are not
replaced. Four complete generated host sequences verify continuity, including
the latest P01 setup failure. These are software checks, not participant results.
Review negative cues in the new dialog before starting; keep NEUTRAL until the
measurement countdown begins. Preserve existing P01/P02 outcomes and inspect the
separate recognition misses before requesting repair data or changing thresholds.

Update, 3 October: [PR #20's camera pilot review](GF_P07_LOCAL_CAMERA_REVIEW_2026_10_03.md) is merged as partial evidence from a personal pilot, not as a new independent evaluation. Keep its completed recordings and results. Its 2/8 accepted NEUTRAL validation trials and kNN/SVM macro-F1 of 0.7209 belong to the same supplied Hau Jie private-pilot evidence stream; do not publish raw data, treat it as diagnostic, and do not lower rejection thresholds or relax neutral-hold/rearm policy on this pilot alone. Sync current main and run `scripts/check_environment.py --model` before the remaining live Enrolment checks: visible invalid feedback, Stop during an active hold, preserved partial slots and save/reload. The shared camera now loads model bytes to avoid a reproduced Windows Unicode model-filename failure. Your original fatal runtime-path error was not reproduced here; use the [Windows recovery instructions](../WINDOWS_LAPTOP.md) if it persists. PR #21 supplies GF-P12's rehearsal component; Deston has attached it as Studio's Practice tab, with a saved historical event review under Session summary. At that historical point targeted pose repair was still missing; PR #25 is now integrated and accepted for the selected-pose repair software criterion. Actual own-profile Practice outcomes remain separate evidence.

Bounded neutral update, 3 October: Hau Jie reports that open palm sometimes remains LATCHED and some movement can recover it. The screenshot supplied with the report does not show the Prediction field, so do not infer a resolved root cause from it. Deston's shared UI fix now keeps prediction, rejection reason and hold guidance visible in the footer, and accepted fresh packets clear stale errors, but the actual intermittent open-palm report remains unconfirmed. Your next recognition task is evidence capture: after fetching/merging main into your own branch, record a short reproduction using the existing opt-in `EvaluationTrace` in Preview/Rehearsal. `EvaluationTrace` records consumed predictions, acceptance flags, rejection reasons, timestamps and snapshot; it does not store the physical intended pose or controller/readiness state. In local notes, separately mark intended open-palm intervals and the displayed Prediction/hold/rejection/readiness state you observe. Do not capture images or feature vectors. Run `python -m gestureforge.trace_diagnose <localtrace.json>` from the repository root to write a current-controller reconstruction under ignored `experiments/local/controller-diagnostics/`. Compare it with the independently recorded intended-pose/display notes and code revision; the tool cannot infer physical pose or score accuracy/readiness. Compare rejected NEUTRAL samples with accepted continuous 0.3-second/gap behaviour from the actual trace before proposing threshold, dataset or neutral-policy changes. Do not request blanket recollection or automatic dataset publication; ask only for targeted repair data if the trace diagnoses a collection defect.

GF-P03 was reviewed and merged in [PR #10](https://github.com/Chi944/GestureForge_304/pull/10) on 30 September; PR #13's evaluator and baseline checkpoint are also merged. Your GF-P06 persistence component from [PR #14](https://github.com/Chi944/GestureForge_304/pull/14) is reviewed and integrated, including an integer/float setting canonicalisation fix that preserves model revisions on reload; 49 targeted profile tests passed at that checkpoint. PR #17's [selector](PROFILE_SELECTOR_HANDOFF.md) is attached in Studio's Profiles tab. PR #19 supplies the bounded comparison; preserve accepted enrolment evidence and continue targeted repair plus own-profile Practice without rebuilding storage, the selector or the evaluator. Fetch and merge `origin/main` into your existing branch before the next change, preserving any local work.

Update, 2 October: PR #13's participant-separated evaluator and [checkpoint](STARTER_EVALUATION_CHECKPOINT.md) have been reviewed and merged after correcting the description of private input sidecars. Integration verification passed 346 tests with one platform-specific skip, lint, types, both GUI smoke checks and synthetic evaluation. Your checkpoint reports P01 checksum validation and completed P02/P03 collection. Those participant measurements are attributed to you; integration review did not reproduce them without the private P02/P03 inputs. Do not request blanket recollection. Keep all data and full result files private.

Deston's saved-profile shell adapter is ready: request `window.load_studio_profile(store, id)` and use the existing background lifecycle. A prebuilt candidate can use `window.use_studio_profile(candidate)`. For deletion, follow the synchronous prepare/delete/clear sequence in [PROFILE_PERSISTENCE_HANDOFF.md](PROFILE_PERSISTENCE_HANDOFF.md); never leave a deleted active model or late load installed. Keep the selector embeddable and leave shell edits to Deston. The shared design is frozen in `CONTRACTS.md`; no separate loader or replacement interface is needed.

PR #17's selector is attached in Profiles. Creation/loading stays paused in Preview; cosmetic rename refreshes the label, and busy work blocks competing setup operations. Guest uses `window.use_studio_guest()` for the non-destructive return to manual control, publishing selection only on a true result. Standard gestures remain unavailable; loading does not establish readiness. The [baseline diagnostic](STARTER_FAILURE_ANALYSIS.md) is accepted. PR #19's [bounded comparison](GF_P11_BOUNDED_COMPARISON.md) reports no qualifying candidate; its private findings were not independently rerun during integration. Preserve the baseline, the three-contributor limitation and the distinction from final evaluation/distribution permission. Request repair data only for a diagnosed collection defect. Deston's six-activation check remains preliminary. PR #21's longer personal rehearsal uses the same shared camera, controller and persistent dispatcher; a qualifying full result can grant only current-session personal LIVE eligibility through the shell gate after save/reconciliation/restoration. It cannot start capture or actions automatically. The integrated Repair pose flow also reuses the shared shell and Profiles review path; do not rebuild its capture, profile create/load or dispatcher behavior. Explicit LIVE manual controls are attached independently of recognition readiness.

1. **GF-P06 - selector delivered and attached.** Keep the reviewed `ProfileStore` API and shell-owned loading. Preserve unavailable-starter messaging, independent profiles, atomic mutations and old state on failure. Deston owns integrated acceptance; see [PROGRESS.md](PROGRESS.md) for current evidence and status. Profile loading and Guest/manual access do not complete starter readiness.
2. **GF-P11 - comparison supplied in PR #19.** The bounded nested comparison reports no qualifying candidate and disagreement between the inner participants' preferred settings in every fold. Review repairs cover reproducibility and evidence consistency; see [PROGRESS.md](PROGRESS.md) for acceptance. Preserve the private run and fixed baseline. A no-qualifying result does not require shipping a starter or blanket recollection.
3. **GF-P07 accepted on 5 October.** Preserve the reviewed Enrolment implementation and the existing physical/generated evidence. Fix demonstrated regressions; no repeat recording is required simply to obtain acceptance again.
4. **GF-P12 by 18 October - validate targeted repair and retain actual Practice evidence.** Use the selected-pose workflow described above only after diagnostic need; the existing fifty-window component and host grant are already integrated and should not be rebuilt. Follow compatibility, setup and focused checks before collecting a full own-profile attempt. Preserve the saved Practice JSON, every miss/interruption, source/model/behaviour revisions and exact Session summary reconciliation. The existing eligibility rule still requires all fifty windows covered, at least nine correct out of ten for every pose including NEUTRAL, zero wrong activations and all ten negative windows correct. Saving, reconciliation and paused restoration must complete before explicit LIVE, Apply, Start and fresh NEUTRAL. Human outcomes remain attributed evidence; they do not replace later GF-P20 study evidence.

## Complete your lane

| Task | Deliverable | Due |
|---|---|---|
| GF-P11 | Label-aware rejection and evaluator; train-only scaler; both classifiers reproducible | 18 Oct |
| GF-P12 | Personal rehearsal and targeted recollection; version-bound readiness evidence | 18 Oct |
| GF-P17 | Frozen starter/personal configurations and properly partitioned evaluation data | 25 Oct |
| GF-P21 | Recognition/profile/evaluator defects resolved without test-set tuning | 1 Nov |
| GF-P24 | Methods, algorithm comparison, data, measured results and limitations report sections | 6 Nov |

Estimate 75 base hours, about 90 with contingency. Do not fill contingency with new AI features.

## Interfaces and file ownership

Own existing `gestureforge/collect.py`, `dataset.py`, `models.py`, `evaluate.py` and corresponding tests. Add only needed files such as `profiles.py` and `enrolment.py`; names beyond the shared contract are implementation choices. Deston owns `contracts.py`, `controller.py`, `routing.py`, `app.py` and `__main__.py`. Javier owns viewer/workspace/shortcut execution.

Preserve the classifier's `predict(features) -> (label, accepted, rejection_reason)` integration shape. Supply a stable nonempty `model_version` identifier, changed when data, preprocessing, hyperparameters or rejection settings change. Do not invent a confidence percentage from SVM decision values. Preserve 60-feature wrist-relative scale normalisation and input handedness/mirroring conventions unless a separately versioned, evaluated change is agreed.

Your collection/practice widgets receive observations from the shared capture service and report user intentions/results to Deston's shell. They do not launch resources or manipulate the viewer. Enrolment's request/attach/release handshake is implemented and documented in [ENROLMENT_INTERFACE_PROPOSAL.md](ENROLMENT_INTERFACE_PROPOSAL.md). PR #21's rehearsal widget uses the existing `RoutingSession` in REHEARSAL mode and persistent dispatcher to count actual would-be actions. Deston owns its shared-camera attachment and context restoration; report any required shell change rather than replacing the integration.

Legacy dataset import may retain NEXT/PREVIOUS/BOOKMARK as stable gesture IDs; new profiles may use G1/G2/G3 or other valid uppercase IDs. A gesture ID describes the recognised class, not the action it must execute. Validate bindings against the selected profile's vocabulary. Live model changes must reach Deston as a new model revision and trigger a new routing session.

## Data and readiness requirements

- Starter: three consenting team members, two sessions, eight trials per four labels, at most five scheduled samples per trial: 960 vectors maximum. Use participant-separated development folds and separate negatives. Ship only data for which distribution permission exists.
- Final personal comparison: at least two independent consenting participants excluded from starter fitting/tuning; separate TRAIN, VALIDATION and untouched TEST sessions. Twelve trials per label/session and at most five samples per trial: 1,440 vectors maximum across both profiles. Freeze before opening test results.
- Compare starter and personal models on the same standard-pose test trials. Evaluate different custom poses separately. Retain invalid samples and count genuine rejections as UNKNOWN misses; report per-person trial macro-F1 and UNKNOWN confusion.
- Starter check: two correct simulated activations per action pose with neutral rearming and zero incorrect activations. UNKNOWN-only cannot pass. Personal rehearsal: ten trials per pose and ten five-second negative/transition intervals; require all windows covered, at least nine correct of ten per pose including NEUTRAL, zero wrong activations and all ten negative windows correct.
- Personal LIVE eligibility is held only in memory and pins profile/model/hand/camera/behavior revision and exact authored workspace, stage and Quick Actions maps. Behavior, mapping, target or camera changes expire it even if changed back. Cosmetic renames, ordinary pause and selection of an existing configured stage/Quick Actions context preserve it; resume always needs explicit Start and fresh NEUTRAL. Restarting Studio, Guest and model reload clear it. Historical/imported JSON, the short check and diagnostics cannot grant it.
- Bound search to kNN k={3,5,7}, uniform/distance; SVM C={0.1,1,10}, gamma={scale,0.1}. Tune rejection on validation positives and negatives. Save numeric examples/configuration, rebuild on load; do not accept arbitrary pickle/joblib files.

## Tests and review evidence

Prove valid and corrupt profile round trips; independent profile deletion; legacy import; wrong/multiple/no hand; custom labels; non-finite/degenerate features; no split leakage; invalid detections counted; caller-visible model revision changes; deterministic reproduction; readiness failure for wrong/UNKNOWN output; and no real actions in practice. Use existing test fixtures and patterns. Synthetic results demonstrate software only.

Run the checks in `TEAM_GUIDE.md` and include their actual output in your handoff. Include a short screen recording for collection/profile workflows and explain what needs camera/participant retesting. Deston reviews the PR and runs independent integration checks.

## Integration follow-up — 4 October

PR #22's timing/countdown and partial-slot Stop handoff are integrated with the
shared-shell footer repair. Keep NEUTRAL through Begin; measurement then displays
the timed cue. New interruption records preserve the host cause. Historical
results provide deterministic next steps after event reconciliation.

After the current compatibility/setup checks, use one real G1 window to verify
Begin/measurement behavior and preserve its local timing diagnostics. Proceed
to full Practice only after reliable setup and focused recognition checks. Preserve the
reported partial-slot Stop evidence; the remaining collection/profile workflow
recording is separate. Do not rebuild the footer, add another camera worker,
change thresholds to hide failures or repeat blanket data collection.

## Starter prompt for your coding assistant

Before repeating a long Practice run after a capture-timing problem, use the
shared [capture stability diagnostic](../USER_GUIDE.md#capture-stability-diagnostic)
with the existing personal dataset. It needs no new poses or collection and
keeps only local aggregate measurements. Keep a covered recognition miss separate
from stale-frame or shutdown problems; this diagnostic cannot score poses or
unlock LIVE gestures. Do not change thresholds to hide a capture failure.

**4 October follow-up:** PR #23's single-pose diagnostic is integrated. Use it to
investigate a specific pose without repeating earlier windows; it cannot grant
full rehearsal credit. Deston's P01 partial check recorded correct NEXT and
PREVIOUS, then a pre-Begin capture validation stop. A bounded preparation-only
late-frame recovery and exact timing diagnostics are integrated; do not widen
freshness limits or change model thresholds from the old combined error. Retest
the affected preparation/pose path before requesting a full 50-window run.
The subsequent P01 BOOKMARK diagnostic on `d1b68e7` completed five seconds and
recorded one matching simulated BOOKMARK event with 45 frames and no recorded
rejections. Its outcome remains inconclusive because capture coverage failed;
the old export cannot locate the boundary/gap responsible. This does not justify
changing recognition thresholds or recollecting gesture training data. Inspect
the new coverage diagnostics on a targeted retry after the layout update.
Your supplied P02 NEUTRAL miss remains separate evidence and needs its own
intended-pose/trace diagnosis. No additional data collection is justified solely
by the P01 capture interruption.

**Later 4 October check:** bounded P01 BOOKMARK and NEUTRAL diagnostics each
completed correctly with valid capture coverage. A subsequent full attempt
completed five correct, covered windows, then stopped before Begin for window
six because an otherwise valid packet was 203 ms old while armed. Recovery now
also covers READY before Begin: discard the packet, return to preparing, keep
the camera and completed windows, and require fresh NEUTRAL within the original
30-second preparation deadline. Measured-phase timing checks remain strict.
Retain the old cancelled attempt; it cannot be resumed or merged into a new pass.
Sync this correction before the next full run. No new training collection is
indicated by this pre-Begin failure.

**Measured-window follow-up, 4 October:** P01's next full attempt retained eight
covered windows (seven correct, one NEUTRAL miss), then cancelled on a 218 ms-old
frame in window nine. The v2 protocol now drops that frame and completes the
affected window as inconclusive while retaining the same session and earlier
results. It does not extend the timer or allow a full pass with incomplete
coverage. Sync main before repeating the full run; retain the old evidence.
The NEUTRAL miss remains a separate scored result, not proof of a timing cause.
Review its intended-pose evidence before changing the recogniser. Inconclusive
windows and stale-frame counts must be reported even when the session finishes.

Include this branch instruction with the task prompt: **Work only on `codex/hau-jie-profiles`. Before every commit or push, verify the current branch. When asked to publish, push only this branch and open a PR to `main` for Deston; never push or merge directly into `main` or another member's branch.**

> Work only on `codex/hau-jie-profiles`; sync reviewed main, preserving local work. Read TEAM_GUIDE.md, this brief, CONTRACTS.md, STARTER_FAILURE_ANALYSIS.md and PAIRED_EVALUATION.md. Follow H1–H4: return the saved-report D1 audit first; prepare two genuinely new consenting participants and all personal/starter development inputs for Deston's configuration freeze; collect untouched TEST only after that freeze. Preserve failures and UNKNOWN slots; poor scores are reportable results, not a reason to tune TEST or enable a failed starter. Operate your laptop as laptop B for Javier's native matrix and GF-P23 fresh-install/offline/thirty-minute checks. Draft GF-P24 methods now and send Word files privately. Reuse existing collection/evaluation tools; repair only evidenced defects in your modules. Keep data, full exports, Word reports and logs local. Return one focused PR at a time with actual checks and limits; push only your branch and leave PRs to main unmerged for Deston. Do not change original owners, weights or acceptance status.
