# GF-P07 local enrolment and recognition review

Owner: Hau Jie. Reviewer: Deston. Date: 3 October 2026.
Status: partial hardware evidence; acceptance and recognition readiness pending.

## Scope and evidence

Hau Jie performed the physical tests on his Windows laptop using his own P02
right hand and camera index 0. Observations below are attributed to him;
the assistant inspected saved numeric manifests and evaluation output, not the
physical poses directly. The running Studio used an ASCII-path mirror of the
earlier `878b1ff` checkout. These observations are not a hardware retest of the
newer main synchronized for this documentation PR.

The camera opened after an ASCII-path workaround. Completed collection persisted
locally, and a saved TRAIN manifest was loaded after restarting the computer.
The supplied Studio screenshot showed P02, Right hand, KNN and rejection
multiplier/margin 1.5. Hau Jie reported that live recognition worked but depended
on keeping the hand straight, facing the camera and at an appropriate position.
Distance and orientation were not measured. This is not a readiness pass.

## Saved collection inspected locally

| Session | Trials | Scheduled samples | Valid samples | Purpose |
|---|---:|---:|---:|---|
| TRAIN | 8 per label / 32 total | 160 | 160 | Exploratory personal fitting |
| VALIDATION | 8 per label / 32 total | 160 | 157 | Separate exploratory evaluation |
| Later TRAIN | 2 per label / 8 total | 40 | 40 | Separate completed pilot; excluded from comparison |

Labels: G1 closed fist; G2 thumb up; G3 index and middle fingers raised;
NEUTRAL open palm. Validation retains three invalid slots: one multiple-hand
detection, one wrong-hand detection and one no-hand detection. Invalid samples
were not silently discarded from the trial records.

Hau Jie reported pressing Stop and confirmed that the displayed message was
**Session saved**. The later TRAIN record contains a complete session. Therefore
completed-session saving is evidenced, but cancellation during an active hold
and preservation of interrupted slots are **not verified by this attempt**.
Do not mark the Stop/partial-save acceptance item passed.

## Saved validation comparison

The existing evaluator fitted only the eight-trial TRAIN session and scored the
separate eight-trial VALIDATION session. Both algorithms used rejection
multiplier 1.5 and margin 1.5, without tuning these settings on validation results.

| Intended label | kNN correct trials | SVM correct trials | Rejected trials (each model) |
|---|---:|---:|---:|
| G1 | 6/8 | 6/8 | 2/8 |
| G2 | 6/8 | 6/8 | 2/8 |
| G3 | 5/8 | 5/8 | 3/8 |
| NEUTRAL | 2/8 | 2/8 | 6/8 |

Both models: **19/32 correct trials (59.4%)**, trial macro-F1 **0.7209**.
The other 13 trial-level outputs were UNKNOWN. No other positive label was
returned at the aggregated trial level; this does not mean every individual
sample was classified correctly. Margin rejection was a frequent sample-level
reason. Weak NEUTRAL recognition may hinder rearming, but this causal explanation
has not been established by a controlled live test.

No unfamiliar-pose/negative session was included in this comparison. Positive
rejections do not demonstrate safe negative rejection and do not justify simply
lowering the thresholds. These are same-person pilot results, not the separate
participant starter comparison and not final independent personal evaluation.
The formal personal protocol requires 12 trials per label/session and an
untouched TEST session with independent participants.

## Camera-path problem and workaround

MediaPipe terminated with a fatal `get_runfiles_dir_helper.cc` accessibility
check; its reported runfiles path contained `??` in place of the Chinese folder
name. The QFont point-size warning was separate from that fatal error.
Launching the code/model from an ASCII-only temporary directory allowed the user
to open the camera. An enrolment-directory junction kept numeric data in the
original private storage. No camera/shell source was changed for this workaround.
This is a local workaround, not a portable fix or a reproduced root-cause proof.
Deston should review non-ASCII Windows startup handling in his integration lane.

## Review requested and remaining evidence

- Review the saved-collection counts and honest acceptance status.
- Retest against the current integrated main; the running mirror predates it.
- Confirm visible invalid-sample feedback, not only stored invalid reasons.
- Demonstrate Stop during an active hold and inspect preserved interrupted slots.
- Produce the short collection/profile workflow recording required by the brief.
- Investigate NEUTRAL and margin rejection before claiming reliable rehearsal.
- Collect/evaluate separate unfamiliar-pose intervals before threshold changes.

Loading numeric data is not the same as creating/reloading a saved ProfileStore
profile. The physical profile-create/Guest/reload workflow is not established by
this dataset-loading evidence. No claim of GF-P07 completion, GF-P12 readiness,
starter release or real gesture action dispatch is made.

## Privacy and reproducibility

Numeric datasets, manifests, full result JSON, absolute local paths and screenshots
remain private. This review contains only aggregate measurements and observations;
it grants no final-package redistribution permission. No raw video was saved.
Local input locations and the reproducible evaluator command are recorded in the
ignored `experiments/local/p02-gf07-review-20261003.md` file. Deston can request
consented private internal review separately; no participant archive is in this PR.

## Publication verification

On synchronized main `caeabbb`, with this documentation-only addition:

- `python -m pytest -q`: 571 passed, 1 skipped in 122.19 seconds.
- `python -m ruff check gestureforge tests scripts`: passed.
- `python -m mypy gestureforge scripts tests`: passed, 69 source files.
- Assignment and Studio `--smoke-test`: both exit 0.
- `git diff --check`: passed; private evidence index is Git-ignored.

These are software/publication checks, not a new physical-camera acceptance test.
