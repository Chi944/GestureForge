# GF-P28: 4 October checkpoint

Prepared 1 October 2026. Owner: Hau Jie. Reviewer: Deston.
Status: reproducible feasibility comparison for review, **not a ready starter**.
This PR continues the merged vocabulary and collection guide; it does not change
the shell, controller, routing, viewer or other builders' modules.

## Private data audit

Each participant contributed 32 positive trials in each of two sessions and eight
separate UNKNOWN trials: 72 trials and 360 scheduled slots per participant.

| Participant | Session 1 valid | Session 2 valid | UNKNOWN valid | Total valid |
|---|---:|---:|---:|---:|
| P01 | 159/160 | 160/160 | 40/40 | 359/360 |
| P02 | 158/160 | 158/160 | 39/40 | 355/360 |
| P03 | 160/160 | 160/160 | 30/40 | 350/360 |

P01's three manifest and sidecar checksums match the sender's verification record.
Its missed scheduled timestamp remains an invalid slot. All participants' invalid
slots remain in scoring. P03's last two negative trials contain no valid features;
these are detection failures, not proof of classifier rejection. No silent
replacement, relabelling or score-driven removal was performed.

The evaluator checks manifest/sidecar validity through the existing loader,
participant IDs, right hand, human provenance, standard vocabulary, split names,
session separation, eight trials per label and five scheduled slots per trial.
It rejects exact feature duplicates across sessions/participants. These checks
cannot verify physical pose compliance or prove independence of near-duplicate
frames; physical conditions and consent remain documented separately.

Archives, features, consent records, input hashes, sample predictions and full
reports remain private. Permission covers internal team training/evaluation only;
final-package/public distribution still needs separate permission. Do not upload
the CLI output to GitHub: it contains detailed participant evaluation records.

## Reproducible development protocol

Run from the repository root, after normal setup. Arrange the private data root as
`P01`, `P02`, `P03`, each containing `session-1`, `session-2`, `negatives` with a
manifest and its referenced numeric sidecar. Ignore historical sidecars/backups.
Confirm all three participants' internal-use consent before running.

```powershell
$env:PYTHONPATH = (Get-Location).Path
.\.venv\Scripts\python.exe -m gestureforge.starter_evaluate `
  --root "data/local/starter" `
  --output "experiments/local/starter-checkpoint.json"
```

Choose a new output filename to repeat; existing evidence is never overwritten.
The root may instead point to a private folder outside the repository. Do not
commit that folder or copy another computer's environment.

For each held-out participant, fit on both positive sessions of the other two
participants. The original train/validation names identify collection sessions;
they are regrouped by person for this development comparison. Fit the scaler and
classifier only on those two training people. Calibrate distance thresholds using
training-only leave-one-trial-out distances. No UNKNOWN samples enter fitting.
Score all 64 positive trials of the held-out person plus their eight negative
trials. All five scheduled slots vote; invalid/rejected slots vote UNKNOWN and
fewer than three matching votes yields UNKNOWN. Genuine UNKNOWN outputs count as
misses in positive-trial macro-F1.

Fixed existing defaults, chosen for the baseline before inspecting fold results:
kNN k=5, distance weights; RBF SVM C=1, gamma=scale; distance multiplier=1.5,
margin=1.0. No parameter search, winner selection or held-out threshold tuning was
performed. Numeric features, model revisions, input hashes and fitted scaler
statistics are recorded in the private output for reproduction.

## Measured results

Each row scores 64 positive trials. Negative acceptance counts are **sample-level
accepted action-class predictions**, not executed controller actions. An accepted
NEUTRAL prediction is reported separately, not counted as a successful rejection.

| Held out | Model | Correct trials | Macro-F1 | Negative action acceptance / valid features |
|---|---|---:|---:|---:|
| P01 | kNN | 45/64 | 0.6335 | 40/40 |
| P01 | SVM | 48/64 | 0.6563 | 39/40 |
| P02 | kNN | 21/64 | 0.4509 | 12/39 |
| P02 | SVM | 21/64 | 0.4509 | 12/39 |
| P03 | kNN | 58/64 | 0.9028 | 30/30 |
| P03 | SVM | 64/64 | 1.0000 | 30/30 |

- P01: NEUTRAL succeeds in only 1/16 kNN and 0/16 SVM trials; most are
  confused with PREVIOUS. Neither classifier rejects any valid negative feature;
  SVM accepts one as NEUTRAL and 39 as action classes.
- P02: both classifiers correctly score NEXT 8/16, PREVIOUS 2/16, BOOKMARK 6/16,
  NEUTRAL 5/16. Across positive trials, 38/64 are rejected as UNKNOWN. For valid
  negatives, 20/39 are rejected, seven accepted as NEUTRAL and twelve as actions.
- P03: kNN mistakes six NEUTRAL trials for NEXT. SVM scores all positive trials
  correctly, but both accept every valid negative sample as an action class.
  The ten invalid negative slots cannot improve the valid-feature rejection rate.

**Neither model is ready for release.** Positive accuracy alone hides poor
unknown-pose rejection. P01/P02 also miss the proposed per-person starter
macro-F1 target of 0.85. Three contributors and limited poses/conditions do not
establish generalisation. Distance/orientation were not measured; observed
confusions do not prove their physical cause. No controller false-action rate,
first-use time, readiness pass, live-camera retest or independent final test is
claimed by this batch evaluation.

## Next handoff

Review the failed rejection/NEUTRAL cases before choosing a model. Any bounded
kNN/SVM parameter or rejection search must keep selection inside each outer
fold's training participants (for example, an inner person split), never use the
held-out person's results to tune its model. With only two inner people, report
selection instability. Preserve this baseline and separately label later
development choices. Freeze before independent final evaluation on new people.

GF-P06 profile persistence is the next separate implementation slice. GF-P07
widgets, live readiness, final model selection and public dataset permission are
not delivered here. No collection/profile video was created by an offline run;
the required human workflow recording remains outstanding. Deston reviews this
checkpoint and decides acceptance; this document does not mark GF-P28 Done.

## Software verification

Tests cover participant isolation, train-only scaling and calibration, invalid
slot accounting, deterministic predictions/model revisions, malformed identity,
wrong hand/provenance/split, missing slots, duplicate sessions/features and refusal
to overwrite an existing report. Synthetic tests demonstrate software only.
Actual local verification on 1 October, using the existing local Python 3.11
environment with `PYTHONPATH` set to this checkout:

```text
python -m pytest -q
346 passed, 1 skipped in 35.03s
python -m ruff check gestureforge tests scripts
All checks passed!
python -m mypy gestureforge scripts tests
Success: no issues found in 52 source files
python -m gestureforge --smoke-test
exit 0
python -m gestureforge --studio --smoke-test
exit 0
```

The ten new evaluator tests pass. Two real-data runs produced identical positive
trial predictions and model revisions for all six folds, matching the previous
private baseline. Fit timings are not expected to be identical. Smoke checks do
not constitute camera/gesture or fresh-install acceptance.
