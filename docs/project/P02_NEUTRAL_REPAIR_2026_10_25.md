# P02 bounded NEUTRAL repair decision 25 October 2026

## Decision

**FAIL. Stop this experiment.** The one predeclared NEUTRAL TRAIN replacement
improves the new-condition positive results but regresses historical NEUTRAL and
fails every index-only negative condition. Original is preserved; the candidate
was not installed, no second candidate or threshold search was run, and no
Practice or LIVE qualification is claimed. Deston retains integration and final
acceptance. This is a recognition coverage limitation, not a demonstrated runtime
defect requiring an unverified shell/controller patch.

Under [Revision 5](HAU_JIE_HANDOFF.md#active-task--personal-release-revision-5-24-october),
the release needs a genuinely qualified personal profile. Supplied-starter
delivery and new recruitment are deferred; failed starter research stays in the
methods. P03's separate unresolved evidence is not repaired by this experiment.
Do not repeat Practice on this known failing candidate or silently expand scope.

## Acquisition and isolated candidate

Collection and fixed-model scoring used reviewed source `33090e5`. The actual
Studio Repair pose workflow saved two complete sessions, each containing two
NEUTRAL TRAIN trials and ten valid scheduled numeric samples. This is an explicit
deviation from the planned single two-trial session. The operator confirmed both
groups were right-hand open palm. Both are retained privately. Before any new
TRAIN/candidate scoring, the earliest chronological session was selected and its
hashes pinned; the later session was excluded from training, scoring and selection.
No favourable-result selection, pooling or deletion occurred. Saved manifests
contain no invalid/cancelled slots; absence of unsaved attempts is not established.

The operator consented to local numeric recording and confirmed normal preview.
Actual hand pose and environment remain operator testimony, not independently
observed ground truth. Conditions were reported as unchanged: seated, five-metre
distance, lighting type/background unspecified. Distance was not independently
measured or silently rewritten as half a metre. No photos/video were recorded.

The existing `PoseRepair.build_candidate` helper was called once after review of
the collected counts. It replaced 40 old NEUTRAL TRAIN samples with ten new ones;
G1/G2/G3 stayed at 40 each. Every retained action-class record and feature row was
checked unchanged. The scaler refitted across all classes. Exact Original TRAIN,
historical validation, new positive validation and all negative input hashes
remained pinned. Right hand, representation, distance-weighted kNN k=5,
multiplier 1.5 and margin 1.0 stayed unchanged. No TEST was read or tuned.

## Fixed development comparisons

The existing profile reconstruction and evaluation helpers scored both models on
identical inputs. Conditions are reported separately, not pooled into a pass.

| Positive trial measure | Original | One candidate | Declared screen |
| --- | ---: | ---: | --- |
| Historical G1 | 8/8 | 8/8 | Pass |
| Historical G2 | 8/8 | 8/8 | Pass |
| Historical G3 | 8/8 | 8/8 | Pass |
| Historical NEUTRAL | 6/8 | **0/8** | **Fail: minimum 6/8** |
| Historical macro-F1 | 0.936508 | 0.651003 | Descriptive, not a replacement for criteria |
| New G1 | 2/2 | 2/2 | Pass |
| New G2 | 2/2 | 2/2 | Pass |
| New G3 | 2/2 | 2/2 | Pass |
| New NEUTRAL | 0/2 | 2/2 | Pass |
| New macro-F1 | 0.666667 | 1.000000 | Reused DEVELOPMENT, not independent qualification |
| New intended NEUTRAL accepted command samples | 10/10 | 0/10 | Pass |

The candidate's eight historical NEUTRAL trial outcomes become five G1 and three
G3. Historical validation retains 160 scheduled samples, including three invalid
slots; new positive validation retains all 40/40 valid samples.

| Index-only condition | Valid / scheduled slots | Original command predictions | Candidate command predictions | Screen |
| --- | ---: | ---: | ---: | --- |
| Centred, palm facing | 10/10 | 10/10 | 10/10 | Fail |
| Slightly left | 6/10 | 6/10 | 5/10 | Fail; four detections unmeasured |
| Slightly right | 10/10 | 10/10 | 10/10 | Fail |
| Raised | 10/10 | 9/10 | 9/10 | Fail |
| Lowered | 10/10 | 8/10 | 10/10 | Fail |
| Farther | 10/10 | 10/10 | 10/10 | Fail |
| Total | 56/60 | **53/60** | **54/60** | Fail |

Every negative condition requires zero accepted command samples. Four original
wrong-hand detections remain invalid/unmeasured, not successful rejections; the
left condition also fails complete-coverage evidence. The failures above do not
depend solely on those missing detections. Predictions are classifier outputs,
not 54 live actions. No negative re-recording or selective retry was requested.

## Disposition and remaining work

Keep this candidate as failed DEVELOPMENT evidence only. Rollback requires no
mutation: reload the unchanged Original if needed, noting that Original is also
not qualified for LIVE on this evidence. Independent qualification and genuine
current-session 22-window Practice remain necessary for any chosen release model.
Deston must decide the release disposition; this result authorises no extra
candidate, threshold change, consumed-TEST tuning or substituted task acceptance.

Laptop-B preparation was assisted and reused an environment, not a guide-only
fresh installation. The retained process monitor has long gaps (largest about
4,494 seconds), so its elapsed duration cannot establish uninterrupted measured
30-minute stability. Its 223/223 sampled responsiveness checks do not establish
capture frame rate or uninterrupted endurance. After saved collection, Studio was
closed through its window; fresh UI/process inventories showed it absent. The
existing camera-0 helper then acquired five frames and exited successfully after
release, with no media saved. Studio capture was already off before close; this
is not active-capture handoff. Studio's original exit code was not retained.
Preserve earlier valid native/offline observations with their own builds;
remaining installation and continuous timing/rate/memory checks stay open with Javier. Gesture-
dependent Camera/focus checks remain NOT RUN without genuine readiness.

## Reproducibility and checks

The compact private handoff contains both new TRAIN pairs with their dispositions,
the one candidate pair, pre-fit pins, exact per-sample/per-trial comparison outputs,
all criteria, actual observations, hashes and reconstruction instructions. It
excludes old packets, original/evaluation input duplicates, TEST, environments,
caches, target bindings, raw media and Word documents. Private input hashes permit
Deston to reuse the exact Original/evaluation files already received.

At `33090e5`, Ruff, mypy, **1,130 tests with two skips**, both startup smoke checks
and synthetic evaluation passed. One expected duplicate-ZIP warning is retained.
The handoff branch subsequently synced reviewed `19c9523`; recognition helper
bytes are unchanged. Final branch checks passed Ruff, mypy, **1,139 tests with
two skips**, both startup smokes and synthetic evaluation, with the same expected
warning. Software checks do not substitute for device/gesture acceptance. The private
methods contribution is updated separately, with its visual QA status explicit.
