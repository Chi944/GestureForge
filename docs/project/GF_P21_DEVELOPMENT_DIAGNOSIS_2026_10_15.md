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

The example paths use Hau Jie's private handoff layout. On another checkout,
use the corresponding corrected DEVELOPMENT manifest with matching input hashes.

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

### Reporting discrepancy resolved during integration

The earlier GF-P18 results narrative described 28/60 P1543 development NEUTRAL slots as margin-rejected for the selected model. The privately supplied candidate report and this rerun show **30/60 for selected SVM**; **28/60 belongs to the alternative kNN** at the same rejection settings. Their aggregate trial macro-F1 ties at 0.666667 and negative commands tie at 10/40. During integration on 15 October, Deston independently verified the attribution against the retained reports and corrected the GF-P18 development narrative with a dated note. Published TEST results are unchanged; TEST was not rerun for this correction.

## Earlier PR proposal — superseded by the next-delivery specification below

First review the existing NEXT/NEUTRAL trial coverage and intended-pose notes; preserve every difficult trial. Do not request blanket recollection. The available geometry establishes poor separation/coverage, but lacks reliable pose-orientation annotations to establish a physical cause.

If Deston approves further model development, predeclare one paired representation experiment: existing 60 wrist/scale features versus a palm-local rotation-normalised representation with its own feature version. Use TRAIN trial groups for all fitting/calibration and separate DEVELOPMENT validation/negative sessions for comparison. Retain current distance and margin safeguards, fixed estimator/rejection settings, per-class misses, invalid slots and negative-command counts. Accept no claimed improvement based solely on aggregate F1 that hides worse negative acceptance. Preserve the original 0.85 starter/0.90 personal targets; a future deployment decision needs a new freeze and fresh independent evaluation. This experiment is proposed, not run or integrated; it needs contract/version review because existing profiles cannot silently change feature meaning. The already consumed P67/P1543 TEST data cannot guide its design choices or settings.

## Checks and remaining evidence

Six focused tests compare diagnostic metrics with the production evaluator for kNN and SVM, verify whole-trial exclusion, retain invalid slots, refuse TEST before fit and protect existing output files. Both actual development reports also match the retained candidate reports' complete validation and negative metrics exactly.

The fresh `scripts/verify.py --timeout 1200` run passed Ruff, mypy (102 source files), **972 Python tests with one Windows symlink skip**, both offscreen startup checks and synthetic evaluation. The duplicate-ZIP fixture emitted its expected warning. The private report is `experiments/local/verification-20261015T040704082558Z.json`. An earlier sandboxed attempt retained access-denial failures and the then-uncorrected test annotation; the successful run used normal Windows permissions and UTF-8 console output. No production filesystem behavior was relaxed to make tests pass.

Private JSON reports and methods/results remain outside Git. The Word draft has passed structural checks but visual QA is pending because the packaged renderer cannot find LibreOffice on this Windows environment. Laptop-B native/offline/stability checks and GF-P20 physical measurements remain separate work; no camera or live pass is claimed here.

## Integration review and next delivery — 15 October

Deston's independent runs on the retained DEVELOPMENT manifests reproduce the
complete selected-model validation and negative metrics and their input hashes.
They confirm the geometry counts above, including P67 NEXT's 47 margin rejections,
P1543 NEXT's 41 distance rejections and selected SVM NEUTRAL's 30 margin rejections.
The GF-P18 narrative is corrected; its TEST results and both freezes are unchanged.
Private review outputs are under `experiments/local/pr32-review-20261015/`.

**Next delivery for Hau Jie: implement one offline representation comparison.**
This fixes the experiment specification before looking at its results. It is
development work within GF-P21, not a production feature change or a model approval.
The existing 60 values retain landmarks 1–20 wrist-relative and divided by the
wrist-to-middle-knuckle distance, so inserting a zero wrist reconstructs sufficient geometry. No new
participant recording is needed for this experiment.

1. Compare the unchanged wrist/scale baseline with exactly one representation,
   `palm-local-experiment-v1`, on the supplied right-hand standard poses only.
   Reconstruct 21 XYZ points from the v1 feature vector with wrist at zero.
   Use `y = normalise(point[9])`; project `point[5] - point[17]` perpendicular to
   y and normalise it to form x; use `z = cross(x, y)`. Project landmarks 1–20
   onto the x/y/z columns and flatten to 60 values. Do not add mirroring,
   alternative axes, augmentation or a parameter search in this comparison.
2. Compute in float64 and return finite float32 values. Refuse non-finite/wrong
   shapes; treat a y norm or perpendicular x norm at or below `1e-6` as degenerate.
   Keep each newly degenerate scheduled observation as invalid/UNKNOWN, including
   validation negatives. Exclude invalid TRAIN features from fitting; retain
   their records/counts. If calibration has fewer than two valid TRAIN trials for
   any enrolled class, report
   the experimental condition unavailable rather than changing the rule.
3. Refuse any TEST-bearing input before fitting. Use the two existing corrected
   DEVELOPMENT manifests, TRAIN-only scaling and whole-trial calibration.
   Keep P67 kNN k=5/distance, multiplier 2.5/margin 1.75 and P1543 SVM
   C=1/gamma=scale, multiplier 2.5/margin 1.25 fixed in both conditions.
   Re-derive distances from each condition's TRAIN only. Do not select or tune
   using the already consumed TEST sets.
4. Return paired per-person/per-class scores, wrong labels, rejected/invalid
   counts, negative-command sample counts and timing for both conditions.
   Preserve every scheduled slot/trial. A gain in aggregate F1 must not conceal
   worse negative acceptance or class recall. This is exploratory development
   evidence; any later deployment claim needs a new freeze and fresh evaluation.
5. Add focused checks for rotation invariance on a nondegenerate synthetic hand,
   shape/finiteness, degenerate palms, unchanged inputs, TEST refusal and retained
   invalid denominators. Keep original features, source files and reports intact;
   write new private aggregate reports and submit a small code/test PR.
6. Keep the transform isolated from Studio and profile/dataset persistence.
   Do not change production `FEATURE_VERSION=1`, save transformed arrays through
   the v1 dataset writer, or export an experimental model as a deployable v1
   profile. Label experimental identities explicitly in reports. Orientation may
   distinguish custom poses, so this result cannot justify changing all profiles.

Hau Jie owns recognition review on `codex/hau-jie-profiles`; Deston reviews any
later contract change. The implementation assistance and results below supersede
the request to build this experiment again. Keep GF-P21 In Progress with its
original GF-P20 dependency. Laptop-B checks and the private methods/results
contribution can continue in parallel.

## Executed comparison and next handoff — 19 October

Deston's integration track implemented the fixed experiment with GPT assistance
in `gestureforge.representation_experiment`. Hau Jie retains recognition ownership;
this is not attributed to a new teammate submission. No open PR or new GestureForge
return was found in the checked repository and Downloads locations on 19 October.

The command accepts only the two specified participants and right-hand standard
poses. Settings stay P67 kNN k=5/distance, multiplier 2.5/margin 1.75; P1543 SVM
C=1/gamma=scale, multiplier 2.5/margin 1.25. Both conditions use TRAIN-only scaling
and whole-trial distance calibration. TEST is refused before fitting. The transform
and its temporary arrays are isolated from Studio, profiles and dataset writers.
No deployable model is exported and production feature version 1 is unchanged.

```powershell
python -m gestureforge.representation_experiment data/local/P67/browser-development-identity-v1-20261013/manifest.json --output experiments/local/P67-representation-new.json
python -m gestureforge.representation_experiment data/local/P1543/browser-development-identity-v1-20261013/manifest.json --output experiments/local/P1543-representation-new.json
```

Use new private output filenames and the corrected manifests whose hashes match
the earlier diagnosis. The actual reports are retained under
`experiments/local/representation-review-20261019/`. Both baseline metric dictionaries
exactly reproduce the reviewed PR #32 outputs, and the input hashes are unchanged.

Independent review separately recomputed the axes and repeated both conditions,
matching every non-timing report field. The 19 focused tests pass; full verification
passes 1,010 tests (two platform skips), Ruff, mypy, both startup modes and synthetic
evaluation. Source/report hashes are in the private `review-receipt.json` beside
the two comparisons; full verification is
`experiments/local/verification-20261019T004955135994Z.json`.

| Participant / condition | Validation trial macro-F1 | NEXT correct / 12 | PREVIOUS correct / 12 | BOOKMARK correct / 12 | NEUTRAL correct / 12 | Negative command predictions / 40 |
|---|---:|---:|---:|---:|---:|---:|
| P67 wrist/scale | 0.789726 | 2 | 12 | 11 | 11 | 12 |
| P67 palm-local | 0.854130 | 4 | 11 | 12 | 12 | 9 |
| P1543 wrist/scale | 0.666667 | 4 | 4 | 12 | 6 | 10 |
| P1543 palm-local | 0.655128 | 8 | 6 | 12 | 1 | 0 |

Each condition retains 240 TRAIN slots, 240 VALIDATION slots and 40 negative slots
per participant: 48/48/8 trials. Existing invalid counts remain P67 6/0/9 and
P1543 11/2/10 respectively; these inputs produce no newly degenerate palm slots.
Invalid observations remain in denominators and score UNKNOWN. Synthetic regression
cases separately verify newly degenerate positives/negatives and an unavailable
condition when a class has fewer than two valid TRAIN trials.

The aggregate F1 gain for P67 is 0.064405, with fewer negative command predictions,
but PREVIOUS recall loses one trial. For P1543, NEXT/PREVIOUS improve while NEUTRAL
falls from 6/12 to 1/12 and macro-F1 falls by 0.011538. At sample level the palm-local
condition also accepts one NEUTRAL slot as NEXT; the baseline has none. P67 retains
five NEXT slots accepted as NEUTRAL in both conditions. The private reports preserve
all per-class accepted/wrong/rejected/invalid counts and confusion matrices.

All four fits took less than 0.05 seconds on this run. Prediction over the 280
scheduled validation/negative slots took 0.55–2.27 seconds per condition, and each
whole-dataset transformation took less than 0.18 seconds. These single-run offline
timings include no camera, UI, controller hold or live latency measurement.

**Decision: keep this representation experimental.** Neither person's experimental
personal score meets 0.90. Reduced negative sample acceptance does not establish
safe live actions, and the NEUTRAL regression is particularly relevant to arming.
No starter is approved, no profile is converted, no threshold is relaxed, and no
consumed TEST result is changed. A future deployment candidate requires a separate
reviewed feature contract, new freeze and fresh independent evaluation.

**Hau Jie next:** review these results and explain the class-level trade-offs in
the private GF-P24 methods/results contribution. Do not reimplement the comparison
or repeat the old search. Diagnose Javier's same-profile PREVIOUS trace when it
arrives; predeclare any further model experiment before running it. Continue laptop-B
checks with Javier. **Deston next:** integrate any demonstrated repair, review
actual scenario/release evidence and preserve all existing acceptance gates.
