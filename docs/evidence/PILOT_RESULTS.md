# Pilot classifier results

Run date: 23 September 2026. Documentation audited on 26 September 2026. This is development validation evidence for one P01 right-hand profile, not a held-out final test.

## Data collected

| Split | Trials | Scheduled samples | Valid samples | Notes |
| --- | ---: | ---: | ---: | --- |
| TRAIN | 32 | 160 | 160 | Eight trials each for NEXT, PREVIOUS, BOOKMARK, and NEUTRAL |
| VALIDATION | 32 | 160 | 160 | Separate recording session using the same right-hand profile |
| VALIDATION_NEGATIVE | 8 | 40 | 40 | Unenrolled poses for open-set rejection development |

The user consented to local numeric P01 right-hand data collection with no raw frames and GitHub exclusion. This file reports aggregate metrics only. It does not publish individual feature rows, trial IDs, model thresholds, raw images, or raw video.

Collection and split rules are in the [collection protocol](../DATA_COLLECTION.md); camera and live observations are recorded in [HARDWARE_CHECK.md](HARDWARE_CHECK.md). The [assignment checklist](../SUBMISSION_CHECKLIST_ASSIGNMENT.md) now records additional private tutor/marker submission permission granted on 26 September. Retention and the private submission location still need recording; GitHub/public sharing remains excluded.

## Why two result sets exist

The original `prototype-v1` threshold calculation used sample-level leave-one-out distances. On this small dataset, neighbouring samples from the same trial made the class reference distances too small. That over-rejected genuine validation gestures.

The corrected `prototype-v2` threshold calculation excludes the whole originating trial when estimating the same-class reference distance for training samples. The evaluation and live-app training paths pass training-record trial IDs into the model; direct calls without trial IDs retain sample-level exclusion. Calibration regression coverage is in [test_models.py](../../tests/test_models.py), with the follow-up review recorded in [REVIEW.md](REVIEW.md) and the full software run in [verification.json](verification.json). The correction and multiplier choice used development validation feedback, so the corrected numbers below must not be described as untouched held-out test performance.

Validation scores use a majority of at least three of five scheduled slots per trial. Invalid, missing and rejected slots score UNKNOWN. Macro-F1 averages the four enrolled labels on VALIDATION only; the 40 negative samples are measured separately, per sample. In the evaluator, accepted **command labels** are NEXT, PREVIOUS and BOOKMARK (not NEUTRAL); these counts are not controller actions.

## Baseline `prototype-v1` results

| Multiplier | kNN macro-F1 | SVM macro-F1 | Negative samples accepted as command labels |
| ---: | ---: | ---: | ---: |
| 1.0 | 0.1919 | 0.1919 | 0/40 |
| 1.5 | 0.3222 | 0.3222 | 0/40 |
| 2.0 | 0.5667 | 0.5667 | 0/40 |

The best baseline macro-F1 was 0.5667 at multiplier 2.0, where 16 of 32 validation trials scored UNKNOWN. Zero accepted negative command-label predictions is not enough by itself when half the genuine validation trials are UNKNOWN.

## Corrected `prototype-v2` results

| Multiplier | kNN macro-F1 | SVM macro-F1 | Validation trials correct | UNKNOWN validation trials | Validation-negative accepted labels |
| ---: | ---: | ---: | ---: | ---: | --- |
| 1.0 | 0.8443 | 0.8443 | 25/32 | 6 | 25/40 BOOKMARK; 0 NEXT; 0 PREVIOUS |
| 1.5 | 0.9496 | 0.9496 | 30/32 | 1 | 25/40 BOOKMARK and 10/40 NEUTRAL; 0 NEXT; 0 PREVIOUS |
| 2.0 | 0.9686 | 0.9686 | 31/32 | 0 | 25/40 BOOKMARK and 10/40 NEUTRAL; 0 NEXT; 0 PREVIOUS |

At multiplier 2.0, the corrected validation confusion has 31 of 32 trials correct. The one wrong validation trial is a NEUTRAL trial predicted as PREVIOUS. No validation trial is UNKNOWN at this setting.

## Selected-setting detail

Both classifiers have the same trial-level confusion matrix at multiplier 2. Rows are intended labels; columns are predictions. UNKNOWN includes rejected genuine gestures.

| Intended | NEXT | PREVIOUS | BOOKMARK | NEUTRAL | UNKNOWN |
| --- | ---: | ---: | ---: | ---: | ---: |
| NEXT | 8 | 0 | 0 | 0 | 0 |
| PREVIOUS | 0 | 8 | 0 | 0 | 0 |
| BOOKMARK | 0 | 0 | 8 | 0 | 0 |
| NEUTRAL | 0 | 1 | 0 | 7 | 0 |

| Label | Precision | Recall | F1 |
| --- | ---: | ---: | ---: |
| NEXT | 1.0000 | 1.0000 | 1.0000 |
| PREVIOUS | 0.8889 | 1.0000 | 0.9412 |
| BOOKMARK | 1.0000 | 1.0000 | 1.0000 |
| NEUTRAL | 1.0000 | 0.8750 | 0.9333 |

| Classifier | Fit including scaler/rejection (s) | Mean offline prediction per sample (ms) |
| --- | ---: | ---: |
| knn | 0.0121 | 2.730 |
| svm | 0.0080 | 0.548 |

Timing covers this development computer and saved features. It excludes camera processing and the controller hold, so it is not end-to-end action latency.

From the repository root, reproduce the corrected **multiplier 2.0** comparison using [experiments/pilot.json](../../experiments/pilot.json):

```powershell
.\.venv\Scripts\python.exe -m gestureforge.evaluate --config experiments/pilot.json --output experiments/local/reproduced-pilot.json
```

This requires the retained `data/local/pilot/manifest.json` and its referenced feature sidecar; both are intentionally absent from GitHub and the source-only ZIP. New enrolment is a new experiment and will not reproduce these scores. Keep full output JSON local because it includes trial IDs, dataset metadata and thresholds.

Initial outputs remain under `experiments/local/pilot-results-m*.json`, and corrected outputs under `experiments/local/pilot-v2-results-m*.json`. The tables and timings above summarise those saved runs; rerun timings vary. The command reproduces the selected v2 setting, not the complete multiplier sweep or the historical v1 baseline. Other v2 settings require local config copies with multiplier 1.0 or 1.5 and separate output files.

## Provisional assignment choice

Use kNN with multiplier 2.0 provisionally for the assignment NEXT-only demonstration. kNN and SVM have the same aggregate validation metrics in these runs; both have small fit times, and kNN is simpler to explain. Both classifiers are rebuilt from numeric training data, without saved executable model files. The live command must specify `--multiplier 2` because the CLI default remains 1.5. This is not the frozen final-project model choice.

This provisional choice is limited to the assignment's NEXT-only demonstration; it is not a safety approval. All corrected settings accept 25 of 40 negative samples as BOOKMARK, so the evaluator's accepted command-label fraction is 62.5%, even though BOOKMARK is preview-only in this release. At multipliers 1.5 and 2.0 another 10/40 are accepted as NEUTRAL. Zero NEXT or PREVIOUS acceptances in this small offline sample does not establish live false-action safety. Rejection and controller evidence must improve before final full-command performance can be claimed.

## Live assignment path

A local live event log records genuine source=`gesture` NEXT events advancing the viewer to positions 1, 2, and 3 after application start. This verifies the assignment path:

`webcam -> MediaPipe landmarks -> personal kNN prototype-v2 multiplier 2.0 -> controller -> viewer`

The participant then repeated the live check with a five-second fist hold that advanced once to card 2, an open-palm rearm, and a second fist hold that advanced once to card 3. The user explicitly confirmed that both holds advanced exactly once. Treat this as a participant-observed smoke check, not the planned formal final-project twenty-hold run.

Both live application instances closed cleanly with exit code 0. The second instance opened the camera successfully. No raw frames were saved. The raw event log remains local. Formal duplicate-action testing, live false-action rate, and latency targets still require measured runs.

[P02 feedback recorded on 26 September](P02_LAPTOP_TEST.md) separately reports successful assisted ZIP use on another laptop with that participant's own right-hand dataset. It supplies qualitative NEXT/hold/rearm observations, not P02 metrics or a held-out second-participant evaluation. It does not alter the P01 tables above.

## Open gates

- Assignment submission: retention/private packaging details, completion of laptop acceptance, tutor/team review, report export/review, AI-use review, signatures and LMS verification remain open in the [assignment checklist](../SUBMISSION_CHECKLIST_ASSIGNMENT.md). Private P01 tutor/marker permission is recorded as granted; marker access to the private source/agile evidence still needs arranging.
- Final project: the formal twenty five-second hold series, ten-minute non-command activity runs, action latency and held-out testing remain pending in the [final checklist](../SUBMISSION_CHECKLIST_FINAL.md). They are not additional assignment feature requirements. Final full-command safety is not established or claimed.
