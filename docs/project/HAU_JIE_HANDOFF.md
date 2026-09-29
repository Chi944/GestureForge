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

1. **GF-P03 by 4 October — custom vocabulary and legacy import.** Trace `collect.py`, `dataset.py`, `models.py` and `evaluate.py`. Remove assumptions that action classes must be NEXT/PREVIOUS/BOOKMARK from the project path. Preserve version-1 assignment manifests and commands. Define a versioned vocabulary of exactly three canonical action IDs plus NEUTRAL; names shown to users are separate. UNKNOWN is a rejection result, never a trained positive class. Prove a legacy input loads and custom IDs retain their labels through train, predict and evaluation.
2. **GF-P28 by 4 October — starter feasibility.** Prepare consent and standard-pose collection for the three team members. Use new data; existing P01 permission does not establish public redistribution permission. Run person-separated development folds. Produce a reproducible kNN/SVM comparison and failure analysis before describing the starter as ready for new users. Never train and test on neighbouring frames from the same trial.
3. **GF-P06 and GF-P07 by 11 October — profiles and guided enrolment.** Create independent profiles with selected hand, display names, vocabulary, training-data reference, immutable model revision and configuration. Support create/rename/load/delete; validate malformed/version-incompatible files, write atomically, preserve old state after failure. Build embeddable PySide6 widgets for collection and profile selection; do not create another top-level shell or camera thread.

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

> Work in this GestureForge repository on GF-P03 only first. Read docs/project/TEAM_GUIDE.md, HAU_JIE_HANDOFF.md and CONTRACTS.md, plus the supplied project plan. Preserve legacy dataset support and existing tests. I own recognition/data/profile files; do not edit app.py, contracts.py, controller.py, routing.py, viewer.py or another teammate's files. Implement a versioned custom gesture vocabulary with exactly three action IDs plus NEUTRAL, retaining UNKNOWN as rejection. Add meaningful import/train/evaluation regression tests. Do not claim participant performance from synthetic tests, add an LLM, commit/push main, or alter local reports/logs. Show changed files, actual test results, integration assumptions and the next smallest task for my review.
