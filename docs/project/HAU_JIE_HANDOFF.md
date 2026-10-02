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

GF-P03 was reviewed and merged in [PR #10](https://github.com/Chi944/GestureForge_304/pull/10) on 30 September; PR #13's evaluator and baseline checkpoint are also merged. Your GF-P06 persistence component from [PR #14](https://github.com/Chi944/GestureForge_304/pull/14) is reviewed and integrated, including an integer/float setting canonicalisation fix that preserves model revisions on reload; 49 targeted profile tests passed at that checkpoint. PR #17's [selector](PROFILE_SELECTOR_HANDOFF.md) is attached in Studio's Profiles tab. PR #19 supplies the bounded comparison; continue with the real enrolment walkthrough and longer personal rehearsal without rebuilding storage, the selector or the evaluator. Fetch and merge `origin/main` into your existing branch before the next change, preserving any local work.

Update, 2 October: PR #13's participant-separated evaluator and [checkpoint](STARTER_EVALUATION_CHECKPOINT.md) have been reviewed and merged after correcting the description of private input sidecars. Integration verification passed 346 tests with one platform-specific skip, lint, types, both GUI smoke checks and synthetic evaluation. Your checkpoint reports P01 checksum validation and completed P02/P03 collection. Those participant measurements are attributed to you; integration review did not reproduce them without the private P02/P03 inputs. Do not request blanket recollection. Keep all data and full result files private.

Deston's saved-profile shell adapter is ready: request `window.load_studio_profile(store, id)` and use the existing background lifecycle. A prebuilt candidate can use `window.use_studio_profile(candidate)`. For deletion, follow the synchronous prepare/delete/clear sequence in [PROFILE_PERSISTENCE_HANDOFF.md](PROFILE_PERSISTENCE_HANDOFF.md); never leave a deleted active model or late load installed. Keep the selector embeddable and leave shell edits to Deston. The shared design is frozen in `CONTRACTS.md`; no separate loader or replacement interface is needed.

PR #17's selector is attached in Profiles. Creation/loading stays paused in Preview; cosmetic rename refreshes the label, and busy work blocks competing setup operations. Guest uses `window.use_studio_guest()` for the non-destructive return to manual control, publishing selection only on a true result. Standard gestures remain unavailable; loading does not establish readiness. The [baseline diagnostic](STARTER_FAILURE_ANALYSIS.md) is accepted. PR #19's [bounded comparison](GF_P11_BOUNDED_COMPARISON.md) reports no qualifying candidate; its private findings were not independently rerun during integration. Preserve the baseline, the three-contributor limitation and the distinction from final evaluation/distribution permission. Request repair data only for a diagnosed collection defect. Deston's six-activation check is preliminary; live personal gestures remain blocked until GF-P12 supplies the full protocol and revision-bound result. Explicit LIVE manual controls are attached independently of recognition readiness. Sync main and reuse the shell; do not rebuild its check or dispatcher.

1. **GF-P06 - selector delivered and attached.** Keep the reviewed `ProfileStore` API and shell-owned loading. Preserve unavailable-starter messaging, independent profiles, atomic mutations and old state on failure. Deston owns integrated acceptance; see [PROGRESS.md](PROGRESS.md) for current evidence and status. Profile loading and Guest/manual access do not complete starter readiness.
2. **GF-P11 - comparison supplied in PR #19.** The bounded nested comparison reports no qualifying candidate and disagreement between the inner participants' preferred settings in every fold. Review repairs cover reproducibility and evidence consistency; see [PROGRESS.md](PROGRESS.md) for acceptance. Preserve the private run and fixed baseline. A no-qualifying result does not require shipping a starter or blanket recollection.
3. **GF-P07 by 11 October - complete guided enrolment acceptance.** PR #16's reviewed `EnrolmentSession`/`EnrolmentWidget` is now attached to Studio; read [ENROLMENT_INTERFACE_PROPOSAL.md](ENROLMENT_INTERFACE_PROPOSAL.md). Sync main and use the Enrolment tab for a real capture walkthrough, including invalid feedback, Stop and save/reload evidence. Deston owns the shared observation adapter; do not rebuild it or create another camera thread. The Profiles tab can explicitly create a saved profile from a completed TRAIN manifest. Preserve legacy imports and the implemented three-action-ID-plus-NEUTRAL vocabulary. UNKNOWN remains a rejection result, never a trained positive class.
4. **GF-P12 by 18 October - implement the longer personal rehearsal and readiness handoff.** Count actual would-be actions through the real controller and a recording dispatcher: ten trials per pose and ten five-second negative/transition intervals, with behaviour-version-bound results and guidance for targeted recollection. The proposed pass target is at least nine correct trials per pose and zero negative actions. Supply the measured result and exact behaviour revision for Deston's live-gesture gate; a six-activation preliminary pass is insufficient. Sync main and reuse its shared camera/controller and persistent dispatcher rather than duplicating the shell attachment. Practice remains simulated even though explicit LIVE manual controls are available. Submit the small practice/result interface to Deston before attachment.

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

Your collection/practice widgets receive observations from the shared capture service and report user intentions/results to Deston's shell. They do not launch resources or manipulate the viewer. Enrolment's request/attach/release handshake is implemented and documented in [ENROLMENT_INTERFACE_PROPOSAL.md](ENROLMENT_INTERFACE_PROPOSAL.md). For the remaining rehearsal widget, use `RoutingSession` in REHEARSAL mode to count actual would-be actions and submit its small interface proposal before attachment.

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

## Starter prompt for your coding assistant

Include this branch instruction with the task prompt: **Work only on `codex/hau-jie-profiles`. Before every commit or push, verify the current branch. When asked to publish, push only this branch and open a PR to `main` for Deston; never push or merge directly into `main` or another member's branch.**

> Continue on codex/hau-jie-profiles after syncing main. Read TEAM_GUIDE.md, this brief, CONTRACTS.md and GF_P11_BOUNDED_COMPARISON.md. Reuse the merged evaluator, persistence, selector, shared camera and Deston's persistent dispatcher; do not rebuild the shell. Preserve PR #19's supplied no-qualifying comparison and fixed baseline; do not repeat collection without a diagnosed defect or invent a starter release. Complete GF-P07's real Enrolment walkthrough, including invalid feedback, Stop and save/reload evidence. Implement GF-P12's ten-trials-per-pose personal rehearsal and ten five-second negative/transition intervals through the real controller and recording dispatcher. Supply the measured outcomes and exact behaviour revision for Deston's live-gesture gate, plus targeted recollection guidance. Submit the practice/result interface before attachment. The six-activation check is preliminary; practice must remain simulated despite available explicit LIVE manual controls. Keep unavailable starter choices explicit, private data out of Git and legacy behaviour intact. Do not edit Deston's app/controller/contracts/routing or Javier's modules. Include actual test output and limits, push only my branch, and open a focused PR for Deston without merging it. Do not alter private Word reports/logs.
