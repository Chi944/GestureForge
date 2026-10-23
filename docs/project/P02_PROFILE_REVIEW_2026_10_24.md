# Exact P02 profile review — 24 October 2026

## Outcome

The existing P02 Original model and positive development result now reproduce
independently. The earlier **0.936508 is an Original-profile result**, not an
original-versus-repaired improvement. No separate repaired P02 profile or matching
negative-validation data were supplied. Do not request those missing old files
again, substitute the older H1 inputs, or describe their absence as zero errors.

The model is unchanged: Right hand, distance-weighted five-neighbour kNN,
distance multiplier 1.5 and ambiguity margin 1.0. Its exact saved model revision,
thresholds and every supplied sample prediction reproduce. No code defect,
successful recognition repair or LIVE approval follows from this result.

## Receipt and reproduction

Archive SHA256:
`5c7db319319e1783ad5417af9588ee1faee2a1dca2c15afb2fbe95e8ffc059ff`.
All 14 safe ZIP members pass CRC and all 13 payload hashes verify. Original bytes
are preserved. On a separate profile copy, only the dataset path was relocated;
the existing `ProfileStore.load` then verified the saved hashes and rebuilt model
identity. No replacement was installed into Studio.

The sender records source `c1b29a7`, with the later brief reviewed at `eb8ea32`.
Reproduction used `eb8ea32`, matching NumPy, scikit-learn, Qt and MediaPipe
versions. Local Python 3.11.16 reproduces the sender's Python 3.11.15 outputs.
Fit timings differ by execution and are not compared for equality.

| Dataset | Scheduled samples | Valid samples | Trials |
|---|---:|---:|---:|
| Original TRAIN | 160 | 160 | 32: eight per label |
| Existing VALIDATION | 160 | 157 | 32: eight per label |
| Matching validation negatives | Not supplied | Not measured | Not supplied |

The three invalid validation records remain in scoring: multiple hands, wrong
hand and no hand. No exact feature overlap exists between the supplied TRAIN
and VALIDATION arrays. This check does not prove independence of collection
conditions or physical pose correctness. They are historical development sessions.

| Fixed recorded setting | G1 correct | G2 correct | G3 correct | NEUTRAL correct | Macro-F1 |
|---|---:|---:|---:|---:|---:|
| Original margin 1.0 | 8/8 | 8/8 | 8/8 | 6/8 | 0.936508 |
| Historical margin 1.5 | 6/8 | 6/8 | 5/8 | 2/8 | 0.720879 |

Both rows independently reproduce the retained metrics and sample predictions.
The second row reproduces an already recorded setting, not a new search. Its
13 incorrect trials are UNKNOWN; it demonstrates loss of genuine gesture recall.
Neither row has matching negative data and neither measures live false actions.

The Original result misclassifies **two NEUTRAL trials as G1**, with all five
samples in each trial accepted as G1. Across 40 scheduled NEUTRAL samples there
are 27 accepted NEUTRAL, 11 accepted G1, one accepted G3 and one invalid sample.
This is a material control limitation despite the aggregate F1 exceeding 0.90.
It does not establish that every recorded prediction would become an action;
controller state and hold/rearm timing still matter.

## What the numeric geometry establishes

Margin 1.0 disables ambiguity rejection. Across
training data, 17/40 NEUTRAL examples have a different-class neighbour closer
than the nearest NEUTRAL sample outside their own trial. Weighted kNN voting
and the recorded acceptance rules explain these outcomes; no label permutation
was found. Numeric features alone do not prove mislabeled physical poses.

The [23 October trace review](P02_NUMERIC_REVIEW_2026_10_23.md) remains valid:
all 1,479 decisions and 12 Preview events reproduce, while intended-pose timing
is missing. Tightening the margin would reject many NEUTRAL predictions. The
new exact baseline strengthens that conclusion without repairing the live
index-only failure. Keep model/settings/controller safeguards unchanged.

## Smallest next diagnostic — prepared, not yet performed

Hau Jie owns a **development-only missing-condition check**, if he agrees to
record new numeric samples. This is a specified follow-up to the now completed
packet reviews, not another request to find nonexistent old data. It does not
require a stakeholder interview, a full Practice attempt or repeated TEST.

Use the existing command-line collector and the unchanged original TRAIN/model.
Plan two new, separate output folders under `data/local/`; never append to the
original manifests. Export the original profile's `vocabulary` object alone to
a separate JSON file. The collector's `--vocabulary` expects that object, not
the full profile JSON. Confirm the actual camera number and record actual
lighting/background/distance; do not copy assumed conditions from old notes.

| New session | Fixed trial plan | Scheduled samples |
|---|---|---:|
| Positive controls: `--split validation --trials 2` | Two trials of each original G1 fist, G2 thumb-up, G3 two fingers and NEUTRAL open palm | 40 |
| Missing negatives: `--split validation_negative --trials 12` | Six index-only conditions below, two trials each; all intended UNKNOWN | 60 |

Negative trial order: 1–2 centred/palm facing camera; 3–4 hand turned slightly
left; 5–6 slightly right; 7–8 raised within the frame; 9–10 lowered within the
frame; 11–12 slightly farther away while still visible. Keep one right index
finger extended throughout each hold; do not substitute the two-finger G3 pose.
Return to the comfortable centre between conditions. The user chooses comfortable
positions; record actual deviations and uncertainty rather than invent angles.
This targets the reported direction/height/distance sensitivity and is not an
exhaustive negative-gesture test.

Each trial uses the existing two-second measurement with five scheduled slots.
There are 20 trials total: 40 seconds of measured holds, plus preparation,
release, instructions and setup. Allow roughly **5–8 minutes**, depending on
camera setup and operator pace; this is an estimate, not measured completion.
The collector shows trial numbers, not these specific negative cues, so keep
this table visible. Preserve saved invalid trials and record mismatched cues or
interrupted attempts in deviation notes. The collector saves completed trials;
cancelling mid-hold discards that pending trial. Do not silently replace failed
attempts with successful ones. Stop if camera operation is unreliable.

GPT can prepare the two commands and vocabulary file on Hau Jie's laptop:

```text
python -m gestureforge.collect --participant P02 --hand Right --vocabulary <vocabulary.json> --camera <confirmed-index> --split validation --trials 2 --setup "<actual conditions; p02-gap-v1 positive controls>" --output <new-positive-folder> --consent
python -m gestureforge.collect --participant P02 --hand Right --vocabulary <vocabulary.json> --camera <confirmed-index> --split validation_negative --trials 12 --setup "<actual conditions; p02-gap-v1 negative order as declared>" --output <new-negative-folder> --consent
```

These are templates; substitute verified local paths/conditions before use.
Pass `--consent` only after Hau Jie agrees. No raw photos/video are saved. Return
the two new manifests, their referenced NPZ files, actual condition/deviation
notes and checksums privately. No whole environment or repeated original packet.

**Analysis fixed before collection:** fit only the exact original TRAIN with
the original settings; score the new positives and UNKNOWN negatives without
model selection. Preserve the old positive results separately. Use existing
profile/evaluator/diagnosis helpers, retaining invalid denominators, per-class
trial recall and negative command sample counts. No TEST, threshold search or
TRAIN replacement. Negative sample counts are not continuous live action rates.
Any command prediction on a genuine NEUTRAL/negative condition remains a failure
to investigate. Even a clean small diagnostic does not grant Practice/LIVE or
close the final performance targets. After inspecting the labelled failure,
predeclare at most one justified data/representation repair with an unchanged
baseline, recall/safety comparisons and rollback before implementing it.

## Work and acceptance

No stakeholder interviews are assigned or required by this team plan. Published
research supplies the problem/alternatives rationale. Actual software-use timing,
task completion, recovery and safety checks remain separate engineering tests;
research cannot generate those measurements.

The exact-profile handoff, reconstruction and positive-baseline reproduction
substeps are complete. GF-P21 still needs a demonstrated repair/disposition and
the original affected checks/dependencies. GF-P24 must reconcile the final
recognition outcome. Accepted work remains **151/223 (67.7%), 19/29 tasks**:
Deston 34/75, Hau Jie 63/75, Javier 54/73. No weights or criteria changed.
Javier can continue independent native recovery checks while Hau Jie handles
recognition. The earlier native `0x8001010d` cause/termination remains unresolved.

Private reproduction and geometry receipts live under
`.local/p02-profile-20261024/`. Original data, exact identities, full results and
Word documents stay local. Prompt and decision logs are untouched.

Fresh verification: **150 tests passed in 30.62 seconds** across profile loading,
evaluation, collection, development diagnosis, models and trace analysis. The
collector counts and vocabulary contract in the prepared instructions were
independently checked against current code. Ruff passes for application, scripts
and tests; mypy passes for all 43 application source files. No physical trial
ran in this review.
