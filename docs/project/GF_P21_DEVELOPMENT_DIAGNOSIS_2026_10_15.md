# GF-P21 development rejection diagnosis — 15 October 2026

Source base: `c021852`. Hau Jie's follow-up uses only the corrected P67/P1543 DEVELOPMENT manifests supplied on 13 October. The selected development settings are held fixed: P67 kNN k=5/distance, multiplier 2.5, margin 1.75; P1543 SVM C=1/gamma=scale, multiplier 2.5, margin 1.25. There is no new candidate search, changed recognition rule, new collection or use of TEST to select settings. GF-P21 remains In Progress and retains GF-P20's acceptance dependency.

## Reproduce the rejection geometry

`gestureforge.development_diagnosis` adds an offline diagnostic. It refuses a dataset with any TEST/unsupported split before fitting, fits valid TRAIN samples once using the existing model, and retains every scheduled VALIDATION/UNKNOWN slot in the existing evaluator's scoring. It outputs aggregate rejection counts, raw-label counts, nearest competing classes and distance-ratio quantiles. TRAIN geometry excludes every sample from the query's own trial when finding its nearest same-class neighbour. The scaler still uses TRAIN; these geometry counts are descriptive rather than independent validation accuracy. Reports contain no trial IDs or landmark arrays, but retain input hashes and should stay private.

With authorised development inputs available:

```powershell
python -m gestureforge.development_diagnosis data/local/participant-handoff-20261013/P67/manifest.json --algorithm knn --multiplier 2.5 --margin 1.75 --output experiments/local/P67-new-diagnosis.json
python -m gestureforge.development_diagnosis data/local/participant-handoff-20261013/P1543/manifest.json --algorithm svm --multiplier 2.5 --margin 1.25 --output experiments/local/P1543-new-diagnosis.json
```

Use a new output filename. Both reports were generated locally on 15 October; no frozen file or historical output was overwritten.

## Findings from development data

| Observation | P67 | P1543 |
| --- | ---: | ---: |
| NEXT valid TRAIN samples | 60 | 59 |
| NEXT TRAIN samples with another class closer than a different NEXT trial | 11 | 13 |
| Nearest other TRAIN class for NEXT | NEUTRAL 55; PREVIOUS 5 | NEUTRAL 59 |
| VALIDATION NEXT raw labels | NEXT 36; BOOKMARK 19; NEUTRAL 5 | NEXT 60 |
| VALIDATION NEXT rejection | 47/60 margin | 41/60 distance |
| VALIDATION NEXT accepted slots | 13/60 | 19/60 |
| VALIDATION trial macro-F1 | 0.789726 | 0.666667 |

P67 NEXT's median distance/threshold ratio is 0.140 while its median competing/predicted-class distance ratio is 1.323, below margin 1.75. Increasing the distance multiplier alone cannot resolve those margin rejections. P1543 NEXT's median distance/threshold ratio is 1.117: the SVM raw label is NEXT for all 60 slots, but many lie outside the current distance threshold. This supports a coverage/rejection diagnosis, not a demonstrated label or importer bug. The existing feature design removes wrist translation and overall scale, but deliberately retains orientation; numeric proximity does not prove a participant made an incorrect pose.

The same fixed reports retain 12/40 negative command samples for P67 and 10/40 for P1543. Removing rejection is not supported by these observations. No production defect was demonstrated in the inspected normalisation, TRAIN-only scaler, grouped distance calibration or prediction rejection implementation.

### Reporting discrepancy for Deston's review

The existing GF-P18 results narrative describes 28/60 P1543 development NEUTRAL slots as margin-rejected for the selected model. The privately supplied candidate report and this rerun show **30/60 for selected SVM**; **28/60 belongs to the alternative kNN** at the same rejection settings. Their aggregate trial macro-F1 ties at 0.666667 and negative commands tie at 10/40. This is a small algorithm-attribution discrepancy; it does not change the published TEST results. Deston owns the results narrative and should reconcile that sentence with his retained SVM report. This PR does not alter his record or rerun TEST.

## Bounded remedy proposed for review

First review the existing NEXT/NEUTRAL trial coverage and intended-pose notes; preserve every difficult trial. Do not request blanket recollection. The available geometry establishes poor separation/coverage, but lacks reliable pose-orientation annotations to establish a physical cause.

If Deston approves further model development, predeclare one paired representation experiment: existing 60 wrist/scale features versus a palm-local rotation-normalised representation with its own feature version. Use TRAIN trial groups for all fitting/calibration and separate DEVELOPMENT validation/negative sessions for comparison. Retain current distance and margin safeguards, fixed estimator/rejection settings, per-class misses, invalid slots and negative-command counts. Accept no claimed improvement based solely on aggregate F1 that hides worse negative acceptance. Preserve the original 0.85 starter/0.90 personal targets; a future deployment decision needs a new freeze and fresh independent evaluation. This experiment is proposed, not run or integrated; it needs contract/version review because existing profiles cannot silently change feature meaning. The already consumed P67/P1543 TEST data cannot guide its design choices or settings.

## Checks and remaining evidence

Six focused tests compare diagnostic metrics with the production evaluator for kNN and SVM, verify whole-trial exclusion, retain invalid slots, refuse TEST before fit and protect existing output files. Both actual development reports also match the retained candidate reports' complete validation and negative metrics exactly.

The fresh `scripts/verify.py --timeout 1200` run passed Ruff, mypy (102 source files), **972 Python tests with one Windows symlink skip**, both offscreen startup checks and synthetic evaluation. The duplicate-ZIP fixture emitted its expected warning. The private report is `experiments/local/verification-20261015T040704082558Z.json`. An earlier sandboxed attempt retained access-denial failures and the then-uncorrected test annotation; the successful run used normal Windows permissions and UTF-8 console output. No production filesystem behavior was relaxed to make tests pass.

Private JSON reports and methods/results remain outside Git. The Word draft has passed structural checks but visual QA is pending because the packaged renderer cannot find LibreOffice on this Windows environment. Laptop-B native/offline/stability checks and GF-P20 physical measurements remain separate work; no camera or live pass is claimed here.
