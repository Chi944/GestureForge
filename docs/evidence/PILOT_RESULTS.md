# Pilot classifier results

Date: 23 September 2026. This is development validation evidence for the assignment prototype, not a held-out final test.

## Data collected

| Split | Trials | Scheduled samples | Valid samples | Notes |
| --- | ---: | ---: | ---: | --- |
| TRAIN | 32 | 160 | 160 | Eight trials each for NEXT, PREVIOUS, BOOKMARK, and NEUTRAL |
| VALIDATION | 32 | 160 | 160 | Separate recording session using the same right-hand profile |
| VALIDATION_NEGATIVE | 8 | 40 | 40 | Unenrolled poses for open-set rejection development |

The user consented to local numeric P01 right-hand data collection with no raw frames and GitHub exclusion. This file reports aggregate metrics only. It does not publish individual feature rows, trial IDs, model thresholds, raw images, or raw video.

## Why two result sets exist

The original `prototype-v1` threshold calculation used sample-level leave-one-out distances. On this small dataset, neighbouring samples from the same trial made the class reference distances too small. That over-rejected genuine validation gestures.

The corrected `prototype-v2` threshold calculation excludes the whole originating trial when estimating the same-class reference distance for training samples. The evaluation and live-app training path now pass training-record trial IDs into the model so this policy can be reproduced. Regression tests failed before the patch and then 20 targeted regression tests passed after the correction. The correction was guided by development validation results, so the corrected numbers below must not be described as untouched held-out test performance.

## Baseline `prototype-v1` results

| Multiplier | kNN macro-F1 | SVM macro-F1 | Validation-negative accepted commands |
| ---: | ---: | ---: | ---: |
| 1.0 | 0.1919 | 0.1919 | 0/40 |
| 1.5 | 0.3222 | 0.3222 | 0/40 |
| 2.0 | 0.5667 | 0.5667 | 0/40 |

The best baseline macro-F1 was 0.5667 at multiplier 2.0. The zero accepted command count is not enough by itself because most genuine validation gestures were rejected as UNKNOWN.

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

Reproduce the corrected comparison locally with `python -m gestureforge.evaluate --config experiments/pilot.json --output experiments/local/reproduced-pilot.json`. This requires the locally retained participant dataset; it is intentionally absent from GitHub and the source-only ZIP. Initial outputs remain under `experiments/local/pilot-results-m*.json`, and corrected outputs under `experiments/local/pilot-v2-results-m*.json`.

## Provisional assignment choice

Use kNN with multiplier 2.0 provisionally for the assignment NEXT-only demonstration. kNN and SVM have the same aggregate validation metrics in these runs; both have small fit times, and kNN is simpler to explain and persist for the assignment. This is not the frozen final-project model choice.

This choice is acceptable only for the assignment's NEXT-only scope. The validation-negative results show a serious open-set weakness: all corrected settings accept 25 of 40 negative samples as BOOKMARK, although NEXT and PREVIOUS have zero accepted negative samples. BOOKMARK is preview-only in the assignment prototype, but this would be unsafe for the final full-command project until rejection and controller evidence improve.

## Live assignment path

A local live event log records genuine source=`gesture` NEXT events advancing the viewer to positions 1, 2, and 3 after application start. This verifies the assignment path:

`webcam -> MediaPipe landmarks -> personal kNN prototype-v2 multiplier 2.0 -> controller -> viewer`

The participant then repeated the live check with a five-second fist hold that advanced once to card 2, an open-palm rearm, and a second fist hold that advanced once to card 3. The user explicitly confirmed that both holds advanced exactly once. Treat this as a participant-observed smoke check, not the planned formal final-project twenty-hold run.

Both live application instances closed cleanly with exit code 0. The second instance opened the camera successfully. No raw frames were saved. The raw event log remains local. Formal duplicate-action testing, live false-action rate, and latency targets still require measured runs.

## Open gates

- The formal final-project twenty five-second hold run has not been completed.
- Live false-action and latency measurements have not been completed.
- Held-out final testing has not happened.
- Ten-minute live non-command activity testing has not happened.
- Final full-command safety is not met and is not claimed.
- Marker access permission, retention arrangements, signatures, second-machine installation, and LMS verification remain pending.
