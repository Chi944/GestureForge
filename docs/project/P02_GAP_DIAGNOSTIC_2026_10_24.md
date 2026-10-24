# P02 missing condition diagnostic 24 October 2026

## Decision

**Integration review, 24 October:** Deston received the private gap packet and
independently reproduced the results below. PR #36 is reviewed and merged.
The 20-trial collection, private handoff and fixed-model reproduction are complete;
do not repeat them. The bounded TRAIN replacement below is ready for Hau Jie's
separate recording consent and preparation; it is not a completed repair.

The fixed `p02-gap-v1` collection and Original-model scoring substeps are complete,
with operator-confirmed pose order and no reported interruptions. The Original
personal model is not suitable for LIVE on this evidence. No repaired model,
shared-controller defect, Practice pass or whole-task acceptance is claimed.
Standard-starter qualification remains separately unmet; this personal diagnostic
does not repair or qualify the starter. Deston retains review and final direction.

## Fixed method and actual results

Preparation and collection used reviewed source `366a821`, the existing collector,
the Original vocabulary and camera 0. Two new private folders contain positive
VALIDATION and index-only validation-negative records. Numeric recording consent
was confirmed before opening collection. Original profile/data/settings remain
unchanged: Right, distance-weighted kNN k=5, multiplier 1.5, margin 1.0. No TEST
was loaded or tuned. The existing profile/evaluator helpers score the exact saved
Original, and the existing development-diagnosis helper independently agrees on
the section metrics. No alternative evaluator or parameter search was added.

| New positive condition | Correct trials | Valid / scheduled samples | Trial outcome |
|---|---:|---:|---|
| G1 fist | 2/2 | 10/10 | G1 in both trials |
| G2 thumb up | 2/2 | 10/10 | G2 in both trials |
| G3 two fingers | 2/2 | 10/10 | G3 in both trials |
| NEUTRAL open palm | 0/2 | 10/10 | G2 in both trials; all ten samples accepted as G2 |

Positive trial macro-F1 is **0.666667**, with 6/8 correct trials. This is a new
small development condition, separate from the historical Original result
0.936508 and historical margin-1.5 result 0.720879. It is not a before/after repair
comparison, population accuracy estimate or final held-out evaluation.

| Index-only negative condition | Trials | Valid / scheduled samples | Accepted command samples |
|---|---:|---:|---:|
| Centred, palm facing camera | 2 | 10/10 | 10/10 |
| Slightly left | 2 | 6/10 | 6/10 |
| Slightly right | 2 | 10/10 | 10/10 |
| Raised, still in view | 2 | 10/10 | 9/10 |
| Lowered, still in view | 2 | 10/10 | 8/10 |
| Slightly farther, still visible | 2 | 10/10 | 10/10 |
| Total | 12 | 56/60 | **53/60** |

Four negative samples are invalid for a wrong-hand detection and remain in their
original trials/denominators. Of 56 valid negative samples, 53 are accepted as
commands (19 G1, 27 G2, 7 G3) and three as NEUTRAL. None of the valid negative
samples is distance- or margin-rejected. Every negative trial contains at least
one accepted command sample. Two trial-majority outcomes are UNKNOWN, but one
contains invalids and both still contain accepted commands; neither establishes
a clean negative trial. These are classifier samples, **not 53 live actions**.

## Interpretation and acquisition limits

The new intended NEUTRAL samples lie well inside the predicted G2 distance
threshold (median distance/threshold about 0.055); most negative samples also lie
inside command regions. Their acceptance follows the implemented rules at the
unchanged margin 1.0. This supports a recognition discrimination/data-coverage
limitation, not a demonstrated label-remapping or controller defect. Tightening
the already unsuccessful margin is not a justified automatic repair.

The operator confirmed both cue sequences and no interruptions. Conditions are
self-reported, not independently observed. The operator reported a five-metre
distance twice when asked to clarify; actual geometry is not independently
measured, and lighting type/background remain unspecified. Preserve that
uncertainty rather than inventing a half-metre distance, angles or lighting.
This small single-person condition does not cover all negative gestures or
deployment conditions. No raw images/video were recorded for pose verification.

All completed trials, invalid records, private numeric manifests/sidecars and
native logs are retained. Exact process exit codes were not retained by the
background launcher; completed-trial stdout is not a fabricated exit-code receipt.
The initial sandboxed camera preflight failed; corrected source selection and
normal desktop access subsequently read/released five frames. Both changes
occurred, so no single causal explanation is claimed. The older native
`0x8001010d` notice remains unresolved and is not cleared by this collection.

## Repair disposition before any new experiment

No runtime patch is justified by the evidence inspected so far. Do not reuse the
new VALIDATION positives/negatives as TRAIN, label UNKNOWN as a positive gesture,
edit the Original or silently install an experimental representation.

One bounded **proposal, not executed**, is a NEUTRAL-only TRAIN coverage repair
using the existing selected-pose repair flow. It requires two separately consented
new TRAIN trials; no such TRAIN inputs exist in this diagnostic. The current
development records remain evaluation-only. A private predeclared plan pins the
baseline/input hashes, selected-label replacement strategy, unchanged settings,
recall/safety criteria and rollback before any candidate is built. Deston should
review whether to proceed; no additional physical capture has been requested or
performed for that proposal. If the candidate does not meet the fixed comparison
criteria, retain failure and stop rather than search more settings. Even a good
reused-development result would require independent qualification, not immediate
LIVE installation. Personal viability is therefore blocked pending a justified
repair and affected checks; starter viability remains a separate blocked scope.

## Software verification and private handoff

At source `366a821`, the repository verification runner passes Ruff, mypy (107
source files), **1,129 tests with two skips and one warning**, both startup smoke
checks and synthetic evaluation. The earlier sandboxed run retained 337 passes,
one skip and 793 temporary-directory setup errors; its failed report is not
discarded or described as a product regression. The normal-permissions rerun
used a new short temporary directory. These checks verify software, not native
device stability, fresh-install independence or recognition qualification.

The compact private handoff contains only new numeric input pairs, fixed results,
geometry, actual operator/deviation notes, versions, hashes and relevant checks.
It excludes TEST, environments/caches, old packets, original input duplicates and
private target bindings. Full private data/logs/Word remain out of GitHub/Trello.
This public note is aggregate evidence only. Remaining laptop-B cases and final
methods/results reconciliation retain their original gates. No interviews are
assigned and no acceptance totals are changed.

## Independent integration and next experiment

The received ZIP has 24 safe members, passes CRC, and matches all 23 payload
hashes and the source-to-archive map. Reconstructing exact P02 Original matches
all 100 new sample predictions, both section metrics, per-trial outcomes and
geometry (apart from execution-dependent fit time). No trial/session overlap or
identical feature rows were found across Original TRAIN, historical validation,
new positive validation and new negatives. Original bytes remain unchanged.
Private receipts are retained under `.local/p02-gap-20261024/independent/`.
This confirms the numeric calculation; physical cue adherence, distance and camera
identity remain operator-reported. No numeric integrity or shared runtime defect
was found that explains the physical confusion.

The private predeclared repair proposal is reviewed. Proceed with **at most one
isolated DEVELOPMENT candidate**, after Hau Jie consents and verifies the correct
webcam view and complete intended open-palm pose. Record actual conditions and any
deviation; do not rewrite the earlier five-metre report. Use the existing Repair
pose flow for two new NEUTRAL TRAIN trials, five valid slots each. No other
collection, search or automatic LIVE installation is authorised by this step.

This is a **replacement**, not an addition: 40 old NEUTRAL TRAIN samples become
10 new ones, leaving G1/G2/G3/NEUTRAL counts **40/40/40/10**. The scaler refits on
the whole candidate, so every class prediction can change even when its TRAIN
samples are retained. Preserve Original for rollback and keep all validation,
negative and TEST data out of TRAIN. Pin the new TRAIN hashes before fitting.

Use the proposal's unchanged settings and comparisons on both old and new
development conditions, reported separately. Historical action recall must remain
8/8 per class and NEUTRAL at least 6/8; new action controls must remain 2/2 per
class and NEUTRAL reach 2/2 with no command predictions. Each negative condition
must have zero accepted command samples. Retain all 60 scheduled slots, including
the four invalid detections: those four are unmeasured recognition, not successful
rejections. Any failure/incomplete coverage stops the experiment for review.
No second candidate or selective retry belongs to this plan. Passing this reused
development screen would still require separate qualification and genuine current
Practice before LIVE; it does not qualify the starter.

The repair review screen now shows the selected-label before/after counts,
retained class counts and the all-pose retraining warning. Generated regressions
cover both 10-to-10 and 40-to-10 replacement with mandatory review and no automatic
training/profile creation. This improves review clarity; it does not fix recognition.

Accepted progress remains **151/223 (67.7%), 19/29 tasks**. GF-P21 still needs
affected recognition checks and its original GF-P20 dependency; diagnosis alone
cannot close it. Target delivery remains 31 October, with official deadline
7 November. Failed outcomes remain visible if that target cannot be met.
