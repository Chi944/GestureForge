# GF-P11 baseline failure analysis and next experiment

2 October 2026. Hau Jie. This is a descriptive checkpoint and experiment proposal,
not a changed model or a new measured result. Private participant data and private
reports were not opened for this work. Findings below come from the already
committed [GF-P28 checkpoint](STARTER_EVALUATION_CHECKPOINT.md) and model code.

This preserves the original diagnostic and experiment proposal. PR #19 now
supplies the [bounded comparison](GF_P11_BOUNDED_COMPARISON.md), reporting no
qualifying candidate. Integration review repaired reproducibility and evidence
consistency; the private measurements are unchanged and have not been rerun here.
The [5 October decision](#5-october-2026-decision-and-next-investigation) below
supersedes the historical next-delivery wording without changing those results.

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

## Original bounded experiment proposal

The proposal below led to PR #19's bounded development comparison. It preserves
the fixed-default baseline and does not improve its historical reported results:

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

The supplied comparison found no qualifying setting in this grid. Request
targeted capture repair only after a specific collection defect is evidenced;
low accuracy alone does not establish a defect. Standard feature normalization
and the prediction API remain unchanged. The next delivery work is GF-P07's real
enrolment walkthrough and GF-P12's longer personal rehearsal, not starter release.

The profile selector is a separate component in this delivery. Shared-camera
enrolment is now integrated on main and awaits a human walkthrough. No starter
release, LIVE readiness or public-data permission is claimed. The diagnostic
code and documentation are submitted for review without participant inputs or outputs.

## 5 October 2026 decision and next investigation

**Keep the starter blocked; review saved failures with Hau Jie before changing
training, thresholds or features.** GF-P07 is now accepted in
[PROGRESS.md](PROGRESS.md); its walkthrough is no longer the next starter task.
GF-P12's selected-pose repair and GF-P10's starter integration are separate work.
Completed feasibility/comparison work does not establish a qualifying starter.

The [bounded comparison](GF_P11_BOUNDED_COMPARISON.md) exhausted the frozen
48-candidate grid with zero qualifiers in every outer fold. Even the best
worst-person inner macro-F1 was only 0.4542, 0.3535 and 0.4724, with respectively
19, 9 and 36 valid UNKNOWN action accepts across the two inner people. The only
two zero-action-acceptance candidates, in P02's development pair, scored
0.2961/0.0294. Both inner people preferred different settings in all three folds.
Thus this grid did not preserve genuine recognition while rejecting unfamiliar
poses; choosing its least-bad row or repeating it cannot satisfy the fixed rule.
This establishes failure of the tested grid, not the physical cause or failure
of every possible method.

The baseline gives different failure patterns: P01/P03 accept unfamiliar poses
as actions while P02 rejects 38/64 genuine trials. Tightening a global cutoff
cannot be assumed to repair both. Rejection is already class-conditional, and
both classifiers share the same scaled 60-feature distances. The existing
wrist translation and scale normalization do not explicitly align hand
orientation; orientation is a hypothesis only, not a diagnosed collection
defect. The original [project plan](PROJECT_PLAN.md#8-evaluation-that-adds-technical-depth)
keeps starter macro-F1 at least 0.85 per held-out person, first action within two
minutes, and a frozen candidate tested on at least two new consenting people.
No target or feature policy changes in this decision.

### D1: preregistered saved-failure audit (not yet executed)

**Owner:** Hau Jie, for the private evidence and case review. **Reviewer:** Deston,
for protocol compliance and the next-method decision. Freeze this D1 procedure
before opening the private cases; retain the source commit, report SHA-256 and
review date with the private findings. This is one descriptive investigation,
with no fitting, parameter sweep, new dependency or candidate promotion.

1. Obtain the regenerated six-fold baseline and its saved diagnostic referenced
   by the bounded comparison, plus the original input-hash record and internal-use
   permission confirmation. Reuse the diagnostic only when its
   `source_report_sha256` matches that baseline. Otherwise run the existing reader
   once to a new ignored output. Do not feed it the comparison JSON or patch the
   older incompatible baseline to make it pass. Missing records, schema refusal,
   a hash mismatch or inconsistent votes stop D1 for evidence repair, not retraining.
2. Reconcile all six folds, each with 320 positive and 40 negative scheduled
   slots, against the published counts. Tabulate each person's/model's NEUTRAL
   trial confusion, positive sample outcomes/rejection reasons and valid UNKNOWN
   rejection/NEUTRAL/action counts. Retain invalid detections separately. Use the
   existing distance/threshold summaries descriptively; their ratios are neither
   calibrated confidence nor evidence of a physical cause.
3. Review the following fixed cases from the saved baseline's trial/sample rows.
   Within each listed person/model, choose the lexicographically first trial ID
   meeting the condition, inspect all five slots and record raw/scored labels,
   acceptance, reason and available distance/threshold. Record an absent condition
   explicitly; do not substitute a more persuasive example. This is at most ten
   model/trial cases, not a sample for estimating a new performance rate.

   | Case condition | Person/model |
   |---|---|
   | NEUTRAL trial scored PREVIOUS | P01, kNN and SVM |
   | Genuine positive trial scored UNKNOWN | P02, kNN and SVM |
   | NEUTRAL trial scored NEXT | P03, kNN |
   | UNKNOWN trial containing an accepted action sample | P01 and P03, kNN and SVM |
   | UNKNOWN trial with no valid features | P03, kNN (same detection input under SVM) |

4. Hau Jie checks any available contemporaneous collection notes for these exact
   IDs: intended pose, hand, session and recorded conditions. Missing pose or
   camera evidence is reported as unknown. A collection-defect finding requires
   an explicit contradiction with the collection protocol in those records;
   confusion, a large distance or an invalid slot alone is insufficient. Record
   the evidence and affected IDs before proposing any targeted repair. Preserve
   the original data and results; do not silently relabel, remove or replace trials.
5. **Decision/stop rule:** D1 is complete only when all six fold summaries reconcile
   and every selected case has an evidence-backed finding or an explicit unknown.
   For each person/model, record separate totals for valid positive classifier
   rejections and accepted wrong positives; investigate its larger category first
   (ties retain both), without treating that as a cause. If a collection defect is
   evidenced, propose only its bounded repair. Otherwise record the unresolved
   recognition/rejection problem and one testable method hypothesis for a new
   versioned protocol; do not launch another grid from D1. Stop after that reviewed
   decision, even if no cause can be established. Starter approval remains empty.

From the repository root after normal setup, substitute Hau Jie's actual private
baseline path; the placeholder below is not an assertion that a report exists:

```powershell
$env:PYTHONPATH = (Get-Location).Path
.\.venv\Scripts\python.exe -m gestureforge.starter_diagnose `
  --report "<private-regenerated-baseline.json>" `
  --output "experiments/local/starter-diagnosis-2026-10-05-v1.json"
```

If that output already exists, validate/reuse its source hash or choose a new
filename; never overwrite evidence. Keep reports, case IDs, notes and hashes
private. Publish only a permission-checked aggregate decision. No matching
starter/diagnosis report filename was found under the primary checkout's
`experiments/local` during this filename-only review; no private report content
was opened. Hau Jie's actual report location and matching evidence are therefore
the execution input still needed, not a reason to regenerate training here.

D1 cannot create an independent test: P01/P02/P03 already informed development.
Any later method comparison must keep complete trials and people separated,
fit scaling/calibration only on fitting people, and select inside each outer
fold's development people. UNKNOWN never becomes a fitted positive class;
invalid slots remain in five-slot votes, and UNKNOWN-as-NEUTRAL is not a rejection.
Keep the existing per-inner-person 0.85/zero-valid-UNKNOWN-action screen. Freeze
before new independent participants; obtain separate redistribution permission
and controller/readiness/first-use evidence before release. This update runs no
private experiment and claims no model improvement or LIVE readiness.

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
