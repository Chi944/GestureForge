# P02 missing condition diagnostic 24 October 2026

## Decision

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
