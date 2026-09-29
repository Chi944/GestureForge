# GestureForge Assignment Evidence Summary

Status: updated 29 September 2026 from the pilot, hardware, laptop, setup, marker-package and review records, including the user's latest laptop confirmations. This is Assignment 1 evidence for the NEXT-only prototype. It is not final-project held-out testing.

## Current Submission Evidence

| Area | Evidence | Limit |
| --- | --- | --- |
| Environment and dependencies | Python 3.11.16, pinned dependencies, model checksum check, Ruff, mypy, automated tests, offscreen GUI startup and synthetic evaluation are recorded in `verification.json`. | Software checks do not prove live camera performance. |
| Camera and hand tracking | On the development computer, camera index 1 produced usable non-black video. A visible 60-second preview processed 1,145 frames and detected one hand in 338 frames. | Device indexes can change. Camera index 1 is not a universal setting. |
| P01 dataset | P01 consented to local numeric right-hand collection. TRAIN and VALIDATION each have 32 trials and 160 valid scheduled samples; validation-negative has eight trials and 40 valid samples. | No raw frames or video are saved. Feature rows, trial IDs, thresholds and raw event logs stay private. |
| Classifier comparison | Recommended prototype-v3 at multiplier 2.0 and margin 1.5 gives both classifiers macro-F1 0.9667, with 30 of 32 validation trials correct and two UNKNOWN. Historical v2 results remain below. | Development validation only. It is not untouched final-project test performance. |
| Live NEXT path | Local live use verified `webcam -> MediaPipe -> kNN multiplier 2.0 -> controller -> viewer`. The participant confirmed two sustained NEXT holds advanced exactly once each with NEUTRAL rearm between holds. | Smoke evidence only. Formal twenty-hold, false-action and latency runs remain final-project tasks. |
| Fresh setup/package checks | Same-computer extracted-source setup passed in fresh environments. Private marker archive reproduced the selected P01 result from extracted source and included only the authorised P01 manifest plus numeric sidecar. | These are not guide-only second-laptop acceptance checks. |
| P02 laptop feedback | P02 reported assisted ZIP use on another laptop with their own right-hand dataset: NEXT moved Card 1 to Card 10, a five-second hold acted once, NEUTRAL rearm was required, and PREVIOUS/BOOKMARK remained preview-only. On 29 September the user confirmed second-laptop offline operation and camera pause/restart both passed. | Qualitative and user-reported. Exact test date, package checksum, OS, camera index, dataset size and guide-only setup are not recorded. |

## P01 Data Summary

| Split | Trials | Scheduled samples | Valid samples | Notes |
| --- | ---: | ---: | ---: | --- |
| TRAIN | 32 | 160 | 160 | Eight trials each for NEXT, PREVIOUS, BOOKMARK and NEUTRAL |
| VALIDATION | 32 | 160 | 160 | Separate recording session using the same P01 right-hand profile |
| VALIDATION_NEGATIVE | 8 | 40 | 40 | Unenrolled poses for open-set rejection development |

The source repository and source ZIP exclude `data/local`. The private marker package may include the P01 numeric manifest and sidecar because the user allowed private tutor/marker use if needed for submission. On 29 September the participant requested that the samples be retained without a scheduled deletion date. This does not broaden permission beyond local/private marker use. Submit participant data only through the private assessment channel.

## Historical calibration correction

On 23 September, `prototype-v1` used sample-level leave-one-out reference distances. Near-identical frames from the same training trial made those distances too small, rejecting many genuine validation gestures. Version 2 excludes the entire originating training trial. This correction used development-validation feedback; the validation set is not an untouched test set.

| Multiplier | v1 kNN macro-F1 | v1 SVM macro-F1 | Negative command-label accepts |
| ---: | ---: | ---: | ---: |
| 1.0 | 0.1919 | 0.1919 | 0 / 40 |
| 1.5 | 0.3222 | 0.3222 | 0 / 40 |
| 2.0 | 0.5667 | 0.5667 | 0 / 40 |

The v1 multiplier-2 run produced 16 UNKNOWN trials out of 32 genuine validation trials. Rejecting all unfamiliar commands alone is insufficient when genuine gestures are also rejected. The historical outputs remain private under `experiments/local`; their aggregates are retained here for an honest development history.

## Corrected Prototype-v2 Results

Validation scores use a trial majority over the five scheduled samples. Invalid, missing and rejected slots count as UNKNOWN. Macro-F1 averages the four enrolled labels on VALIDATION only. Validation-negative samples are measured separately per sample.

| Multiplier | kNN macro-F1 | SVM macro-F1 | Validation trials correct | UNKNOWN validation trials | Validation-negative accepted labels |
| ---: | ---: | ---: | ---: | ---: | --- |
| 1.0 | 0.8443 | 0.8443 | 25/32 | 6 | 25/40 BOOKMARK; 0 NEXT; 0 PREVIOUS |
| 1.5 | 0.9496 | 0.9496 | 30/32 | 1 | 25/40 BOOKMARK and 10/40 NEUTRAL; 0 NEXT; 0 PREVIOUS |
| 2.0 | 0.9686 | 0.9686 | 31/32 | 0 | 25/40 BOOKMARK and 10/40 NEUTRAL; 0 NEXT; 0 PREVIOUS |

The historical provisional assignment setting was kNN with multiplier 2.0 because kNN and SVM produced the same aggregate metrics and kNN is easier to explain. This is a provisional assignment choice, not the frozen final-project model choice.

Rows are intended labels; columns are predictions for both classifiers at multiplier 2.0.

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
| kNN | 0.0121 | 2.730 |
| SVM | 0.0080 | 0.548 |

Reproduce the selected comparison from the repository root when the private P01 data is present:

```powershell
.\.venv\Scripts\python.exe -m gestureforge.evaluate --config experiments/pilot.json --output experiments/local/reproduced-pilot.json
```

## Revised ambiguity rejection on 28 September 2026

The original rule measures only distance from the predicted class. An unfamiliar pose can fall within that class's broad radius while also resembling another class. Prototype-v3 additionally requires the nearest other-class distance divided by the nearest predicted-class distance to be at least the configured margin. Both distances use the same scaler and TRAIN examples. Validation negatives are used to compare settings, never fitted as training examples.

| Setting at multiplier 2 | kNN macro-F1 | SVM macro-F1 | Genuine correct trials | Genuine UNKNOWN trials | Negative BOOKMARK | Negative NEUTRAL | Negative UNKNOWN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| v2 distance only, margin 1 | 0.9686 | 0.9686 | 31 / 32 | 0 | 25 | 10 | 5 |
| v3 balanced margin 1.5 | 0.9667 | 0.9667 | 30 / 32 | 2 | 5 | 10 | 25 |
| v3 strict margin 2 | 0.8846 | 0.8846 | 26 / 32 | 6 | 0 | 0 | 40 |

The balanced margin 1.5 is the revised live default. One NEXT trial and one NEUTRAL trial become UNKNOWN; no trial is mislabelled as another known gesture. The 20 fewer negative command-label accepts are an offline development improvement, not a measured reduction in live false actions. Margin 2 rejects all saved negatives but misses too many genuine trials, so it is not the recommended setting. Margin 1 explicitly reproduces historical v2; omitted margins in old evaluation configurations preserve v2.

| Intended label | NEXT | PREVIOUS | BOOKMARK | NEUTRAL | UNKNOWN |
| --- | ---: | ---: | ---: | ---: | ---: |
| NEXT | 7 | 0 | 0 | 0 | 1 |
| PREVIOUS | 0 | 8 | 0 | 0 | 0 |
| BOOKMARK | 0 | 0 | 8 | 0 | 0 |
| NEUTRAL | 0 | 0 | 0 | 7 | 1 |

Reproduce the revised result with the authorised private dataset:

```powershell
.\.venv\Scripts\python.exe -m gestureforge.evaluate --config experiments/pilot-rejection.json --output experiments/local/reproduced-pilot-v3.json
```

The historical and revised runs use the same saved development recordings. No new participant recording is claimed. The user subsequently confirmed live v3 transition smoke success, as recorded below. Full outputs, thresholds and individual prediction records stay in ignored `experiments/local`; the source configuration contains only reproducible settings. Broader, independently collected positive and negative data are still needed before claiming reliable unknown rejection.

## Rejection Limitation

Unrecognisable gestures should be rejected as UNKNOWN. The current classifier sometimes accepts unfamiliar validation-negative poses as known labels, especially BOOKMARK. This is a measured limitation, not intended fallback behaviour. For Assignment 1, BOOKMARK and PREVIOUS remain preview-only and do not dispatch viewer actions. Before the final project enables all commands, the team must improve rejection, collect broader development data and run held-out tests.

## Software Verification

The current verification summary lives in `verification.json`. On 29 September, 82 tests, Ruff, mypy across 30 files, GUI smoke and synthetic evaluation passed. The refreshed private archive was extracted and its own source reproduced both v3 macro-F1 values of 0.9667 and passed GUI smoke using the existing verified Windows environment; this was not a new dependency installation. Archive integrity and privacy boundaries were checked locally. Earlier package checks recorded:

GitHub Actions run `36413668556` did not start its test job: GitHub reported an account payment/spending-limit block. This is not a remote test pass or a code-test failure. The user requested local CI instead. Hosted runs are now disabled; quota-blocked runs were removed after their metadata was retained locally. Fresh local verification remains available in `verification.json`; no remote pass is claimed.

- Fresh extracted source setup on the development computer passed with Python 3.11.16 and the expected `hand_landmarker.task` SHA256 `fbc2a30080c3c557093b5ddfc334698132eb341044ccee322ccf8bcf3607cde1`.
- Same-computer source archive verification passed pip checks, model checks, launcher smoke and synthetic verification from an extracted folder with spaces in its path.
- Private marker archive integrity passed and reproduced macro-F1 0.9686274509803923 for kNN and SVM from extracted source with authorised P01 numeric data.

These archive checks support reproducibility. They do not replace recording the exact second-laptop package checksum and environment.

## P02 Qualitative Feedback

P02 reported that recognition worked best when the hand faced the camera, stayed still, remained at a similar distance and position to the training samples, and stayed well lit. Recognition became unreliable with motion, tilt, back-of-hand orientation, lateral shift and distance changes. Recovery usually involved returning to NEUTRAL before repeating the command.

This supports the assignment claim that a separately enrolled user could operate the NEXT path on another laptop. On 29 September the user additionally confirmed that offline operation and camera pause/restart both passed. These confirmations establish user-reported checks, not recorded P02 accuracy, an exact-release acceptance record, guide-only installation or full-system final evaluation.

## Open Gates

- Team names, IDs and a 60/40 contribution split are present in the private declaration; the user confirmed both members' agreement on 29 September. Review its confirmation boxes and add specific report/code responsibility evidence before submission.
- Confirm course administration requirements: same-tutorial membership and team registration have not been established here; the user reports no tutor feedback. Do not claim tutor requirements approval.
- Review prompt-log coverage and obtain tutor acceptance for the requested separate prompt document: page 1 of the brief specifies prompts in the report. The user requested no log edits during this refresh.
- Record guide-only second-laptop setup and exact package/version and Windows/Python/camera details. Offline and pause/restart checks were confirmed passed by the user; no independent event log or exact test date is supplied.
- Use the rebuilt source/private archives and their SHA256 companions; rebuild again if any submitted source changes after verification.
- Download the LMS upload and check it before the deadline.
- For the November project, run two-participant held-out evaluation, full command execution checks, twenty-hold duplicate-action runs, false-action measurement, latency measurement and stability testing.


## NEUTRAL-to-NEXT transition correction — 28 September 2026

The user reported repeated failed advances while the display showed NEXT + WAIT NEUTRAL. Code inspection identified that every rejected prediction, including a valid tracked hand between enrolled poses, immediately disarmed the controller. This explains why a subsequent recognised NEXT could not execute.

The update distinguishes classifier-only distance/margin rejection from invalid tracking. After READY, up to 500 ms of classifier rejection cancels a partial hold without disarming; accepted NEXT must then complete a fresh 400 ms hold. Longer rejection requires NEUTRAL again. Tracking loss, stale/out-of-order data, wrong/multiple hands, pause and camera faults retain their reset protection. LATCHED stays latched through classifier rejection. Classifier thresholds and retained P01 recordings are unchanged.

Controller and app regression tests exercise the transition, timeout, retry and duplicate prevention. See `verification.json` for fresh automated results. After receiving the corrected launch command (kNN, multiplier 2, margin 1.5, camera 1), the user confirmed: “Yes, both transitions work once”. This is a successful participant-observed live smoke retest of the corrected transition, not a quantified accuracy, latency, false-action or twenty-hold result.
