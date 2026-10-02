# GF-P11 baseline failure analysis and next experiment

2 October 2026. Hau Jie. This is a descriptive checkpoint and experiment proposal,
not a changed model or a new measured result. Private participant data and private
reports were not opened for this work. Findings below come from the already
committed [GF-P28 checkpoint](STARTER_EVALUATION_CHECKPOINT.md) and model code.

## What the baseline already establishes

| Held-out participant | NEUTRAL result | UNKNOWN valid-feature result | Implication |
|---|---|---|---|
| P01 | kNN 1/16 correct; SVM 0/16; most confused with PREVIOUS | kNN 40/40 action accepts; SVM 39/40 actions and one NEUTRAL; zero classifier rejections | Positive recognition and unfamiliar-pose rejection both need work. |
| P02 | Both 5/16 correct; across all positive classes 38/64 trials rejected | Both 20/39 rejected, 7/39 NEUTRAL, 12/39 action accepts | A globally tighter threshold may reject even more genuine poses. |
| P03 | kNN mistakes six NEUTRAL trials for NEXT; SVM all positives correct | Both accept all 30/30 valid negatives as actions | Perfect positive accuracy does not imply safe unfamiliar-pose rejection. |

P03 also has ten invalid negative slots. These remain detection failures, not
successful classifier rejections. None of these batch counts is an executed
controller action, false-activation rate or five-second-hold result.

## What the implementation explains, and what it does not

`models.py` already uses a separate distance threshold for each predicted label.
It compares a sample with the nearest training example of the classifier's
predicted class. Training calibration excludes the query's own trial, uses the
95th percentile within that class and multiplies it by 1.5 in the saved baseline.
The scaler is trained only on fitting data.

The optional cross-class distance margin runs only when `margin > 1.0`; the
baseline uses 1.0, so that check is inactive. A wrong label can still pass a
distance threshold when its features resemble that class. This is a plausible
mechanism for acceptance, not proof that changing the margin will solve it.

UNKNOWN is not a trained positive label. Baseline calibration uses positive
training trials, not validation negatives. Changing classifier family alone did
not fix the observed rejection problem. Physical pose compliance, camera angle,
distance and handedness/mirroring errors cannot be diagnosed from these published
aggregate counts. No blanket recollection or physical-cause claim is justified.

## Saved-report diagnostic tool

`python -m gestureforge.starter_diagnose` reads a previously saved baseline JSON;
it never loads numeric dataset sidecars, fits a model or chooses parameters. It:

- checks the six person/model folds and declared training/held-out identities;
- requires all 320 positive and 40 negative scheduled slots per fold;
- rebuilds five-slot majority votes and checks them against saved trial results,
  confusion matrices and counts, refusing inconsistent reports;
- separates invalid detections, valid classifier rejections, accepted wrong
  positives, accepted UNKNOWN-as-NEUTRAL and accepted UNKNOWN-as-action outcomes;
- reports NEUTRAL trial confusion and descriptive distance/threshold ratios;
- records the input report's SHA-256 and refuses to overwrite input/output evidence.

This validates consistency of the saved report, not authenticity or physical
independence of the original collection. Raw UNKNOWN without distances is the
existing baseline's invalid-detection encoding; other report formats are refused.
If no valid negative features exist, valid-feature rates are null, not 100%.
Distance ratios are not confidence probabilities, and zero thresholds have no
defined ratio. Aggregate output still contains participant results and stays private.

When internal-use access to the saved report is in scope, run from the repository
root with the existing environment and a new output filename, for example:

```powershell
python -m gestureforge.starter_diagnose `
  --report "experiments/local/starter-checkpoint.json" `
  --output "experiments/local/starter-diagnosis-v1.json"
```

These example paths do not assert that those exact local files exist. No private
diagnostic run was performed in this implementation session. Software tests use
generated prediction records and a generated-data run of the existing evaluator.

## Bounded next experiment, before any new final testing

Keep the fixed-default baseline intact. Treat the following as a later development
experiment rather than a retroactive improvement to its reported results:

1. For each outer held-out person, select settings using only the other two people.
   In inner folds, fit scaler/classifier on one person and validate positives and
   UNKNOWN trials on the other, then swap. Keep trials intact; UNKNOWN never
   enters positive-class fitting. No outer held-out examples select thresholds.
2. Stay within the brief's existing classifier grid: kNN k={3,5,7},
   uniform/distance weights; SVM C={0.1,1,10}, gamma={scale,0.1}. A proposed small
   rejection comparison is multiplier={1.0,1.5}, margin={1.0,1.2}. Those added
   rejection candidates are a proposal, not tuned winners or approved defaults.
3. Specify the selection rule before running: reject candidate promotion unless
   each inner person's positive-trial macro-F1 meets the brief's 0.85 target and
   no valid negative sample is accepted as an action. Report NEUTRAL acceptance
   separately. If none qualifies, report that none qualifies; do not silently
   choose a model for release. This conservative screen does not replace the
   controller-based readiness requirement.
4. If candidates qualify, use a fixed tie-break (worst-person positive macro-F1,
   then valid-feature UNKNOWN rejection, then an explicitly frozen candidate order).
   Report both inner-person scores and whether independently preferred settings
   disagree. Two inner people provide weak and potentially unstable selection.
5. Fit the selected configuration only on the two outer training people and score
   the held-out person once. Record data/configuration/model revisions in a new
   private experiment. Preserve the original baseline and report failures.
6. This proposal itself was informed by the three-person baseline. All later runs
   on these people remain exploratory development, even with correct nested
   splitting. Freeze the final configuration before evaluation on the independent
   new participants required by the brief.

Before implementation, inspect permitted saved-case diagnostics to decide whether
this bounded experiment is worthwhile. If feature overlap prevents useful
separation, document the limitation; request targeted capture repair only after a
specific collection defect is evidenced. Do not infer a defect simply from low
accuracy. Standard feature normalization and the prediction API remain unchanged.

The profile selector is a separate component in this delivery. Shared-camera
enrolment is now integrated on main and awaits a human walkthrough. No starter
release, LIVE readiness or public-data permission is claimed. The diagnostic
code and documentation are submitted for review without participant inputs or outputs.

## Local verification

Publication check after syncing main `b542e33` and connecting the profile selector
to the Guest API: **512 passed, 1 skipped** in 63.97s; Ruff, mypy (63 files), and
both startup smoke checks passed. The earlier component checkpoint below is retained
as historical evidence.

Using the existing Python 3.11 environment with this checkout on `PYTHONPATH`:

```text
python -m pytest -q tests/test_starter_diagnose.py tests/test_starter_evaluate.py
22 passed in 36.22s
python -m pytest -q
485 passed, 1 skipped in 1119.18s (0:18:39)
python -m ruff check gestureforge tests scripts
All checks passed!
python -m mypy gestureforge scripts tests
Success: no issues found in 61 source files
python -m gestureforge --smoke-test
exit 0
python -m gestureforge --studio --smoke-test
exit 0
```

The full-suite duration is elapsed wall time from this run, not an inference about
recognition latency. These are software checks only. The diagnostic workflow follows
the ML Pipeline Workflow skill's reproducibility principles by retaining the
baseline, checking saved evidence and recording its source hash; it adds no cloud
pipeline or deployment dependency.
