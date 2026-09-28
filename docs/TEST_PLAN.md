# GestureForge Test Plan and Requirement Traceability

Status: software verification is recorded in `docs/evidence/verification.json`; live camera, P01 pilot results, real NEXT actions, setup/package checks, and P02 qualitative feedback are consolidated in `docs/evidence/RESULTS.md`. Pause/restart, offline use and guide-only installation remain unverified. Formal twenty-hold runs, live false-action measurement, p95 latency and held-out testing are final-project checks.

## Test Strategy

Testing is split into three levels:

1. Unit tests for contracts, features, classifiers, controller, viewer, profiles, and deck validation.
2. Integration tests for saved data, evaluation replay, and camera-to-controller flow where hardware is available.
3. Release tests on a second Windows computer using the submitted instructions and package.

The assignment only executes tests for implemented prototype parts. The final project executes tests for every subsystem.

## Requirement Traceability

| Requirement | Assignment test evidence | Final project test evidence | Current status |
| --- | --- | --- | --- |
| RQ-001 Local Windows Python 3.11 run | Environment check and launch smoke test | Second-machine release test | Software verified; P02 laptop use reported, remaining release checks pending |
| RQ-002 Work under `code` | File layout review | File layout review | Implemented |
| RQ-003 Labelled collection | CLI collection smoke test and manifest check; P01 TRAIN, VALIDATION and validation-negative sessions collected | GUI enrolment tests | Assignment pilot collected |
| RQ-004 60-feature extraction | Unit test for shape and wrist removal | Same | Software verified |
| RQ-005 Invalid hand rejection | Unit tests for no hand, multiple hands, wrong hand, non-finite values, degenerate scale | Same with UI recovery | Software verified |
| RQ-006 kNN/SVM comparison | Reproducible evaluate command output; aggregate pilot metrics in `docs/evidence/RESULTS.md` | Bounded search evidence | Development validation complete; held-out final pending |
| RQ-007 Hold/rearm controller | State-machine unit tests | Live replay and system tests | Software verified |
| RQ-008 Assignment NEXT only | Viewer/controller integration test; live NEXT event log | Superseded by all-command tests | Verified for assignment live path |
| RQ-009 Exactly-once actions | Duplicate event and long-hold tests; two live deliberate holds advanced once each | Twenty five-second holds per profile | Software verified plus assignment live smoke check; formal run reserved for final project |
| RQ-010 Preview-only PREVIOUS/BOOKMARK | UI smoke check | Replaced by command execution | Software verified |
| RQ-011 Manifest retains invalid detections | Manifest validation test; P01 scheduled pilot samples were all valid | Same | Software verified; no invalid real P01 captures to report |
| RQ-012 Metrics include UNKNOWN | Evaluation unit test with known confusion matrix | Final held-out report | Software verified |
| RQ-013 Profile persistence | Not in assignment scope | Round-trip, reload, delete, corrupt file | Future |
| RQ-014 JSON decks | Not in assignment scope | Valid and malformed deck tests | Future |
| RQ-015 Guide/demo evidence | Assignment install notes | Full guide, video, second-machine evidence | Future |

## Unit Test Scenarios

| Area | Scenario | Expected result |
| --- | --- | --- |
| Feature extraction | Valid 21 world landmarks | 60 finite features |
| Feature extraction | Wrist-to-middle-knuckle distance is zero | Rejected as degenerate scale |
| Feature extraction | Landmark contains NaN or infinity | Rejected as non-finite |
| Hand selection | No hand detected | UNKNOWN or rejected observation |
| Hand selection | Two hands detected | Rejected as multiple hands |
| Hand selection | Handedness does not match profile | Rejected as wrong hand |
| Data split | Frames from one trial kept together | No split leakage |
| Scaling | Scaler fitted on training data only | Validation transform uses training scaler |
| kNN | Saved training input reproduces prediction | Same labels and rejection decisions |
| SVM | Saved training input reproduces prediction | Same labels and rejection decisions |
| Evaluation | Rejected genuine gestures | Count as misses |
| Evaluation | No trial majority | Count as UNKNOWN |
| Controller | Neutral hold reaches READY | Ready after configured duration |
| Controller | Command hold reaches LATCHED | One command event only |
| Controller | Continuous long command | No duplicate actions |
| Controller | Neutral returns after latch | Controller can rearm |
| Controller | Candidate changes mid-hold | Pending hold cancels |
| Controller | Brief classifier rejection after READY or during hold | No action from reject; retry starts a fresh 400 ms hold within 500 ms |
| Controller | Classifier rejection exceeds 500 ms, including first accepted return | Requires fresh NEUTRAL |
| Controller | Classifier-reject jitter while LATCHED | No duplicate action |
| Controller | Tracking loss | Requires neutral before next action |
| Controller | Stale frame | Rejected |
| Controller | Out-of-order timestamp | Rejected |
| Controller | Pause | Pending state invalidated |
| Viewer | NEXT at first card | Moves to second card |
| Viewer | NEXT at last card | Stays at last card |
| Viewer | Duplicate event ID | Ignored |
| Viewer | Keyboard fallback | Moves card with source marked as keyboard |

## Assignment Integration Checks

| Check | Command or method | Evidence to save |
| --- | --- | --- |
| Environment check | `python scripts/check_environment.py` | Terminal output or evidence note |
| Locked setup | `.\scripts\setup.ps1` | Terminal output from a clean or release setup |
| Camera check | `python scripts/check_environment.py --camera --camera-index 1` on current machine; index may vary elsewhere | Terminal output and camera notes |
| Model asset download | `python scripts/download_model.py` | Asset path and checksum note |
| App launch | `python -m gestureforge --smoke-test --screenshot docs/evidence/app-smoke.png` | Screenshot or terminal output |
| Live app with human dataset | `python -m gestureforge --dataset data/local/pilot/manifest.json --algorithm knn --multiplier 2 --margin 1.5 --camera 1` | Screenshot, local event log, and camera notes; do not publish raw event log if it contains local identifiers |
| Collection path | `python -m gestureforge.collect --camera 1 --split train --participant P01 --hand Right --setup "desk lighting, plain background" --consent --output data/local/pilot` | Manifest and aggregate data summary; do not publish feature rows |
| Evaluation path | `python -m gestureforge.evaluate --config <path>` | JSON or CSV result |
| UI launch | `python -m gestureforge` | Screenshot and notes |
| Live NEXT | Webcam NEXT advances fixed deck; P01 deliberate holds and P02 reported five-second hold advance once after rearm | Short screen recording, participant-observed note, or local event log |
| Tests | `python -m pytest` | Test output |
| Agile board | Read the private Trello board linked in `docs/AGILE.md` | Verified board URL, `docs/backlog.csv` snapshot and `docs/sprint_events.jsonl` |
| Source package | `python scripts/package_release.py` | ZIP manifest JSON and note that it is source only |

The latest software verification summary is stored in `docs/evidence/verification.json`. Consolidated human, package and limitation evidence is stored in `docs/evidence/RESULTS.md`. Use those files instead of manually copying counts into the final submission.

## Final Project Integration Checks

| Check | Evidence |
| --- | --- |
| Profile create/reload/delete | Test logs and screenshots |
| In-app enrolment disabled command dispatch | Event log showing no commands |
| PREVIOUS and BOOKMARK execution | Viewer event log |
| JSON deck validation | Valid and malformed deck test output |
| Saved state reload | Position and bookmarks restored |
| Profile switch protection | No stale command after switch |
| Offline operation after setup | Second-machine notes |
| Missing camera | User-facing recovery message |
| Missing model asset | User-facing recovery message |
| Stability run | 30-minute log, rate, memory, shutdown note |

## Evidence Naming

Use the implemented local/private paths:

- `data/local/<dataset>/manifest.json` and its referenced numeric `.npz` sidecar: participant samples, excluded from Git.
- `experiments/local/<comparison>.json`: full outputs, excluded from Git.
- `docs/evidence/<check>.md` or `.json`: reviewed aggregate verification suitable for source distribution.
- `releases/`: generated ZIPs and checksum companions, excluded from Git.

Keep the retained P01 dataset unchanged; collect new people or experiments into separate folders. Camera index 1 is verified only on the development machine. Final held-out artifacts will use the same privacy boundary, with names recorded when collected.

Synthetic fixtures, including `experiments/prototype.json`, may be used for software tests. They must be labelled separately from participant pilot or held-out results.

## Evaluation Config Examples

Synthetic fixture config with no participant data prerequisite:

```json
{
  "algorithms": ["knn", "svm"],
  "rejection_multiplier": 1.5,
  "synthetic_fixture": {
    "seed": 304,
    "samples_per_trial": 5,
    "trials_per_label_per_split": 3
  }
}
```

Data-local fixture prerequisite:

```powershell
python -m gestureforge.fixtures data/local/synthetic
```

Config for a data-local manifest:

```json
{
  "dataset_path": "data/local/synthetic/manifest.json",
  "algorithms": ["knn", "svm"],
  "rejection_multiplier": 1.5
}
```

Historical distance-only P01 configuration (v2):

```json
{
  "dataset_path": "data/local/pilot/manifest.json",
  "algorithms": ["knn", "svm"],
  "rejection_multiplier": 2.0
}
```

Supported keys are `dataset_path`, `dataset_paths`, `synthetic_fixture`, `algorithm`, `algorithms`, `rejection_multiplier`, and `rejection_margin`.

Do not create participant records before consent exists.

The revised P01 configuration is `experiments/pilot-rejection.json`, with multiplier 2.0 and margin 1.5. Regressions cover ambiguous-pose rejection, invalid margin settings, evaluator propagation, and GUI rejection feedback without viewer action. Live v3 recognition/rearm must be retested before treating prior v2 live observations as evidence for the revised model. Historical configurations without a margin retain margin 1.0 for reproducibility; live launches default to margin 1.5.


The 28 September live defect report (NEXT displayed with WAIT NEUTRAL after a pose transition) is recorded in the results. Regression tests cover the repaired controller and UI polling path. The user subsequently confirmed both transitions advance once after restart. This is live smoke evidence only; broader final-project testing remains planned.
