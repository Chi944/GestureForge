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

GF-P03 was reviewed and merged in [PR #10](https://github.com/Chi944/GestureForge_304/pull/10) on 30 September; PR #13's evaluator and baseline checkpoint are also merged. Your GF-P06 persistence component from [PR #14](https://github.com/Chi944/GestureForge_304/pull/14) is reviewed and integrated, including an integer/float setting canonicalisation fix that preserves model revisions on reload; 49 targeted profile tests passed. Use the [profile persistence API and integration handoff](PROFILE_PERSISTENCE_HANDOFF.md), then continue the selector and baseline failure analysis without rebuilding storage or the evaluator. Fetch and merge `origin/main` into your existing branch before the next change, preserving any local work.

Update, 2 October: PR #13's participant-separated evaluator and [checkpoint](STARTER_EVALUATION_CHECKPOINT.md) have been reviewed and merged after correcting the description of private input sidecars. Integration verification passed 346 tests with one platform-specific skip, lint, types, both GUI smoke checks and synthetic evaluation. Your checkpoint reports P01 checksum validation and completed P02/P03 collection. Those participant measurements are attributed to you; integration review did not reproduce them without the private P02/P03 inputs. Do not request blanket recollection. Keep all data and full result files private.

Next complete GF-P06's profile selector widget for create/rename/load/delete and the Guest/start selection path, with a small interface proposal for Deston. Keep the Guest path explicit about the unavailable starter; storage alone does not establish recognition readiness. In parallel, inspect the failed NEUTRAL and UNKNOWN cases from the saved baseline and propose a bounded rejection/calibration improvement. Neither baseline model is ready to ship. Keep tuning inside the outer fold's training participants, preserve this baseline, and explain the limits of only three contributors. Request targeted repair data only after identifying a concrete collection defect. These development folds do not replace independent final evaluation or establish distribution permission. Do not change Deston's shell or enable a starter before its readiness gate passes.

1. **GF-P06 by 11 October - finish the profile workflow.** Reuse the reviewed `ProfileStore` API to deliver a create/rename/load/delete selector widget and the Guest/start selection interface. Keep unavailable starter choices disabled with a clear reason. Keep atomic create/rename/load/delete, malformed/version-incompatible input checks and immutable model revisions covered by tests; preserve old state on failure. Deston owns attachment to the shared shell.
2. **GF-P28/GF-P11 - baseline failure analysis and bounded repair.** Inspect NEUTRAL confusion and UNKNOWN acceptance using the saved person-separated comparison. Preserve the baseline; tune only inside each outer fold's training participants and report selection instability. Request targeted repair data only for a diagnosed collection defect. The evaluator and collection protocol already exist; development results do not establish starter readiness or redistribution permission.
3. **GF-P07 by 11 October - guided enrolment after the profile boundary is agreed.** Build embeddable PySide6 collection widgets using the shared capture service; do not create another top-level shell or camera thread. Preserve legacy imports and the implemented three-action-ID-plus-NEUTRAL vocabulary. UNKNOWN remains a rejection result, never a trained positive class.

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

Your collection/practice widgets receive observations from the shared capture service and report user intentions/results to Deston's shell. They do not launch resources or manipulate the viewer. Use `RoutingSession` in REHEARSAL mode to count actual would-be actions. The callback/signal signatures for attaching widgets to `Window` will be agreed with Deston before GF-P10; they are not yet implemented APIs. Submit that small interface proposal with your first widget.

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

> Continue on codex/hau-jie-profiles after syncing main. Read TEAM_GUIDE.md, this brief, CONTRACTS.md and STARTER_EVALUATION_CHECKPOINT.md. PR #13's evaluator is merged; P01/P02/P03 collection is reported complete, so do not rebuild the evaluator or repeat collection without a diagnosed defect. PR #14 persistence is reviewed and integrated; read PROFILE_PERSISTENCE_HANDOFF.md and reuse ProfileStore. Deliver the GF-P06 create/rename/load/delete selector widget and Guest/start interface proposal for Deston, then GF-P07 observation-fed collection without a second camera. Keep unavailable starter choices explicit; do not recreate storage or claim live readiness. Preserve the failed starter baseline and investigate NEUTRAL/UNKNOWN errors with tuning confined to each outer fold's development participants. Keep private data out of Git, preserve legacy behaviour, and do not claim starter readiness. Do not edit Deston's app/controller/contracts/routing or Javier's modules. Include real test output and limits, push only my branch, and open a focused PR for Deston without merging it. Do not alter private Word reports/logs.
