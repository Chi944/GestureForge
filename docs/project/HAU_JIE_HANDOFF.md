# Hau Jie implementation brief

You own recognition and personalisation for GestureForge Studio. Build the reusable AI and profile components; Deston owns integration and final acceptance. Read `TEAM_GUIDE.md` and `CONTRACTS.md` first. Work is assigned for the project due 7 November 2026; the assignment is already submitted.

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

## Start with these tasks

Update, 3 October: [PR #20's camera pilot review](GF_P07_LOCAL_CAMERA_REVIEW_2026_10_03.md) is merged as partial evidence from a personal pilot, not as a new independent evaluation. Keep its completed recordings and results. Its 2/8 accepted NEUTRAL validation trials and kNN/SVM macro-F1 of 0.7209 belong to the same supplied Hau Jie private-pilot evidence stream; do not publish raw data, treat it as diagnostic, and do not lower rejection thresholds or relax neutral-hold/rearm policy on this pilot alone. Sync current main and run `scripts/check_environment.py --model` before the remaining live Enrolment checks: visible invalid feedback, Stop during an active hold, preserved partial slots and save/reload. The shared camera now loads model bytes to avoid a reproduced Windows Unicode model-filename failure. Your original fatal runtime-path error was not reproduced here; use the [Windows recovery instructions](../WINDOWS_LAPTOP.md) if it persists. PR #21 supplies GF-P12's rehearsal component; Deston has attached it as Studio's Practice tab, with a saved historical event review under Session summary. The remaining evidence is a real 50-window rehearsal, not another implementation of the component.

Bounded neutral update, 3 October: Hau Jie reports that open palm sometimes remains LATCHED and some movement can recover it. The screenshot supplied with the report does not show the Prediction field, so do not infer a resolved root cause from it. Deston's shared UI fix now keeps prediction, rejection reason and hold guidance visible in the footer, and accepted fresh packets clear stale errors, but the actual intermittent open-palm report remains unconfirmed. Your next recognition task is evidence capture: after fetching/merging main into your own branch, record a short reproduction using the existing opt-in `EvaluationTrace` in Preview/Rehearsal. `EvaluationTrace` records consumed predictions, acceptance flags, rejection reasons, timestamps and snapshot; it does not store the physical intended pose or controller/readiness state. In local notes, separately mark intended open-palm intervals and the displayed Prediction/hold/rejection/readiness state you observe. Do not capture images or feature vectors. Run `python -m gestureforge.trace_diagnose <localtrace.json>` from the repository root to write a current-controller reconstruction under ignored `experiments/local/controller-diagnostics/`. Compare it with the independently recorded intended-pose/display notes and code revision; the tool cannot infer physical pose or score accuracy/readiness. Compare rejected NEUTRAL samples with accepted continuous 0.3-second/gap behaviour from the actual trace before proposing threshold, dataset or neutral-policy changes. Do not request blanket recollection or automatic dataset publication; ask only for targeted repair data if the trace diagnoses a collection defect.

GF-P03 was reviewed and merged in [PR #10](https://github.com/Chi944/GestureForge_304/pull/10) on 30 September; PR #13's evaluator and baseline checkpoint are also merged. Your GF-P06 persistence component from [PR #14](https://github.com/Chi944/GestureForge_304/pull/14) is reviewed and integrated, including an integer/float setting canonicalisation fix that preserves model revisions on reload; 49 targeted profile tests passed at that checkpoint. PR #17's [selector](PROFILE_SELECTOR_HANDOFF.md) is attached in Studio's Profiles tab. PR #19 supplies the bounded comparison; continue with the real enrolment walkthrough and longer personal rehearsal without rebuilding storage, the selector or the evaluator. Fetch and merge `origin/main` into your existing branch before the next change, preserving any local work.

Update, 2 October: PR #13's participant-separated evaluator and [checkpoint](STARTER_EVALUATION_CHECKPOINT.md) have been reviewed and merged after correcting the description of private input sidecars. Integration verification passed 346 tests with one platform-specific skip, lint, types, both GUI smoke checks and synthetic evaluation. Your checkpoint reports P01 checksum validation and completed P02/P03 collection. Those participant measurements are attributed to you; integration review did not reproduce them without the private P02/P03 inputs. Do not request blanket recollection. Keep all data and full result files private.

Deston's saved-profile shell adapter is ready: request `window.load_studio_profile(store, id)` and use the existing background lifecycle. A prebuilt candidate can use `window.use_studio_profile(candidate)`. For deletion, follow the synchronous prepare/delete/clear sequence in [PROFILE_PERSISTENCE_HANDOFF.md](PROFILE_PERSISTENCE_HANDOFF.md); never leave a deleted active model or late load installed. Keep the selector embeddable and leave shell edits to Deston. The shared design is frozen in `CONTRACTS.md`; no separate loader or replacement interface is needed.

PR #17's selector is attached in Profiles. Creation/loading stays paused in Preview; cosmetic rename refreshes the label, and busy work blocks competing setup operations. Guest uses `window.use_studio_guest()` for the non-destructive return to manual control, publishing selection only on a true result. Standard gestures remain unavailable; loading does not establish readiness. The [baseline diagnostic](STARTER_FAILURE_ANALYSIS.md) is accepted. PR #19's [bounded comparison](GF_P11_BOUNDED_COMPARISON.md) reports no qualifying candidate; its private findings were not independently rerun during integration. Preserve the baseline, the three-contributor limitation and the distinction from final evaluation/distribution permission. Request repair data only for a diagnosed collection defect. Deston's six-activation check remains preliminary. PR #21's longer personal rehearsal uses the same shared camera, controller and persistent dispatcher; its measured result is separate and does not unlock LIVE gestures. Explicit LIVE manual controls are attached independently of recognition readiness. Sync main and reuse the shell; do not rebuild its check or dispatcher.

1. **GF-P06 - selector delivered and attached.** Keep the reviewed `ProfileStore` API and shell-owned loading. Preserve unavailable-starter messaging, independent profiles, atomic mutations and old state on failure. Deston owns integrated acceptance; see [PROGRESS.md](PROGRESS.md) for current evidence and status. Profile loading and Guest/manual access do not complete starter readiness.
2. **GF-P11 - comparison supplied in PR #19.** The bounded nested comparison reports no qualifying candidate and disagreement between the inner participants' preferred settings in every fold. Review repairs cover reproducibility and evidence consistency; see [PROGRESS.md](PROGRESS.md) for acceptance. Preserve the private run and fixed baseline. A no-qualifying result does not require shipping a starter or blanket recollection.
3. **GF-P07 by 11 October - complete guided enrolment acceptance.** PR #16's reviewed `EnrolmentSession`/`EnrolmentWidget` is now attached to Studio; read [ENROLMENT_INTERFACE_PROPOSAL.md](ENROLMENT_INTERFACE_PROPOSAL.md). Sync main and use the Enrolment tab for a real capture walkthrough, including invalid feedback, Stop and save/reload evidence. Deston owns the shared observation adapter; do not rebuild it or create another camera thread. The Profiles tab can explicitly create a saved profile from a completed TRAIN manifest. Preserve legacy imports and the implemented three-action-ID-plus-NEUTRAL vocabulary. UNKNOWN remains a rejection result, never a trained positive class.
4. **GF-P12 by 18 October - collect measured Practice evidence and resolve demonstrated defects.** Sync the reviewed main before testing; PR #21's component is integrated in the embedded **Practice** tab. After saving, inspect Session summary's historical review for completed/recorded windows, coverage and exact event matches; keep the separate full Practice JSON. Do not rebuild it or attach a second camera. Complete fifty five-second windows: ten trials for each of the three enrolled action poses and NEUTRAL, followed by ten negative/transition windows. The prompted actions pass through the shared controller and persistent dispatcher in simulation. Preserve the saved local result, code revision, profile/model/behaviour revision, pose notes and any interruptions. The proposed target is at least nine correct trials per pose and zero negative actions, with coverage checks; an incomplete attempt is not a pass. Inspect the negative instructions against your enrolled poses before starting. A measured pass needs Deston's review and does not enable LIVE gestures. Keep private evidence out of Git; send a permission-appropriate aggregate report and a focused defect PR if needed.

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
- Starter check: two correct simulated activations per action pose with neutral rearming and zero incorrect activations. UNKNOWN-only cannot pass. Personal rehearsal: ten trials per pose and ten five-second negative/transition intervals; target at least nine correct of ten per pose and zero negative actions.
- Readiness revision covers hand, data/feature/model settings, rejection, hold/rearm policy and binding configuration. Cosmetic renames do not invalidate it; changing the mapping does. Selecting a configured stage requires neutral, not full rehearsal again.
- Bound search to kNN k={3,5,7}, uniform/distance; SVM C={0.1,1,10}, gamma={scale,0.1}. Tune rejection on validation positives and negatives. Save numeric examples/configuration, rebuild on load; do not accept arbitrary pickle/joblib files.

## Tests and review evidence

Prove valid and corrupt profile round trips; independent profile deletion; legacy import; wrong/multiple/no hand; custom labels; non-finite/degenerate features; no split leakage; invalid detections counted; caller-visible model revision changes; deterministic reproduction; readiness failure for wrong/UNKNOWN output; and no real actions in practice. Use existing test fixtures and patterns. Synthetic results demonstrate software only.

Run the checks in `TEAM_GUIDE.md` and include their actual output in your handoff. Include a short screen recording for collection/profile workflows and explain what needs camera/participant retesting. Deston reviews the PR and runs independent integration checks.

## Integration follow-up — 4 October

PR #22's timing/countdown and partial-slot Stop handoff are integrated with the
shared-shell footer repair. Keep NEUTRAL through Begin; measurement then displays
the timed cue. New interruption records preserve the host cause. Historical
results provide deterministic next steps after event reconciliation.

Start with one real G1 window to verify Begin/measurement behavior, preserving
its local timing diagnostics. Then run the full Practice attempt. Preserve the
reported partial-slot Stop evidence; the remaining collection/profile workflow
recording is separate. Do not rebuild the footer, add another camera worker,
change thresholds to hide failures or repeat blanket data collection.

## Starter prompt for your coding assistant

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

Include this branch instruction with the task prompt: **Work only on `codex/hau-jie-profiles`. Before every commit or push, verify the current branch. When asked to publish, push only this branch and open a PR to `main` for Deston; never push or merge directly into `main` or another member's branch.**

> Sync reviewed main into `codex/hau-jie-profiles` and read TEAM_GUIDE.md, this brief and CONTRACTS.md. PR #21 supplies the longer rehearsal component and Deston owns its embedded Practice integration: do not rebuild it or add a camera worker. Preserve PR #22's real Stop/invalid-slot evidence and finish GF-P07's short collection/profile workflow recording. Verify one Begin window against the corrected footer, then run Practice's fifty five-second windows using your personal profile: ten per action pose plus NEUTRAL, then ten negative/transition intervals. Keep the saved local result and code/model/behaviour revision; report actual outcomes and interruptions without claiming LIVE permission. Separately reproduce the open-palm/LATCHED issue with the existing opt-in Preview/Rehearsal EvaluationTrace and timestamped intended-pose/display notes. Run `python -m gestureforge.trace_diagnose <localtrace.json>` and compare the current-controller reconstruction with those notes and the code revision; it is not an accuracy/readiness score. Keep raw samples, private results and notes out of Git; do not record images or feature vectors for this diagnosis. Diagnose before changing thresholds, neutral policy or requesting targeted repair collection. Preserve the supplied PR #19 comparison and PR #20 pilot limits. Fix evidenced defects only in your recognition/profile/enrolment/practice modules and tests; send shared-shell issues to Deston. Run the common checks, push only your own branch and open a focused PR for Deston; leave it unmerged. Do not edit private Word reports/logs.
