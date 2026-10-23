# P02 numeric recognition review — 23 October 2026

**24 October update:** the exact-profile handoff below is now complete. The
[Original model and both recorded development results reproduce](P02_PROFILE_REVIEW_2026_10_24.md).
The 0.936508 result is Original, not a repaired improvement; matching negatives
and a separate repaired profile were not found. Follow the new review's bounded
labelled diagnostic, not the historical request to resend existing files.

## Decision

Hau Jie's requested numeric diagnostic is complete and independently reproduced.
Do not repeat it or change the live profile on the strength of these traces.
The next step is to reproduce the **existing exact P02 profile and development
comparison**, not collect another unannotated recording. No classifier, setting,
controller, readiness gate or consumed TEST result changed in this review.

The reported cross-pose confusion is a recognition limitation. The inspected
training-to-display path carries the estimator's string label unchanged; no
G1/G2/G3 permutation was found. Distance acceptance and controller replay match
their implemented rules. This does not establish that recognition is adequate.

## Verified packet and captures

The supplied archive SHA256 matches Hau Jie's stated value:
`99bf622ad3aef3f2f5a74dde729b56387e0b90e75b53599583a515ef17b7c2de`.
All 13 unique safe members pass CRC; all 12 listed payload hashes match.
The archive was actually attached, despite the copied handoff saying otherwise.
Full traces, identifiers, numeric decisions, logs and receipts remain private
under `.local/p02-numeric-20261023/`; none is added to GitHub or Trello.
The capture receipt identifies source `c1b29a7`; reproduction used the current
reader on `e191fcc`. The later research commit does not change recognition.

| Capture | Span | Frames | Numeric decisions | Preview simulations |
|---|---:|---:|---:|---|
| First | 51.047 s | 1,298 | 887 | Three G2 and five G3 |
| Second | 29.000 s | 691 | 592 | Four G2 |
| Total across separate captures | Not a continuous stability run | 1,989 | 1,479 | 12 |

The current `gestureforge.trace_diagnose` output exactly equals both supplied
analyses. All 1,479 numeric acceptance decisions agree with the saved rule. All
12 reconstructed event labels and timestamps match the runtime simulation log;
no stale or excessive-gap condition was found. These are Preview simulations,
not completed external application actions.

Fresh targeted checks passed **74 tests** across the model, development-only
analysis and trace-reader suites. Independent verification also recalculated
the counterfactual below. No application code changed, so the prior full-suite
result is not presented as a new full run.

Hau Jie reports G1 sometimes showing G2, G2 sometimes showing G3, G3 showing G1,
and index-only predictions changing with hand direction/height. Both records
have incomplete intended-pose annotations and no timed expected holds. Therefore
this review does **not** assign true labels to individual frames, count all 12
events as false activations, calculate accuracy or claim a Practice/LIVE pass.

## Why a higher margin is not an automatic repair

The saved model uses distance-weighted five-neighbour kNN, multiplier 1.5 and
ambiguity margin 1.0. That margin disables ambiguity rejection by design. The
estimator's weighted vote can differ from the closest individual competing
sample. Close competitors therefore explain a possible acceptance weakness,
not a label-remapping or controller defect. The trace does not retain competitor
class identities, full neighbour votes, hand features or timed physical labels.

One fixed **exploratory counterfactual** applies margin 1.5 to the already saved
numeric decisions, retaining the original distance rejects and invalid frames.
Its local plan was saved before calculating these counts. Because the traces
had already been inspected, this is not a preregistered performance evaluation
or model-selection experiment. No search, refit, event replay or profile edit
was performed. Rejections are grouped by recorded prediction, not true pose.

| Capture | Recorded label | Previously accepted | Would additionally reject | Would retain |
|---|---|---:|---:|---:|
| First | G1 | 65 | 57 | 8 |
| First | G2 | 268 | 215 | 53 |
| First | G3 | 227 | 167 | 60 |
| First | NEUTRAL | 327 | 254 | 73 |
| Second | G1 | 64 | 40 | 24 |
| Second | G2 | 311 | 300 | 11 |
| Second | G3 | 0 | 0 | 0 |
| Second | NEUTRAL | 216 | 216 | 0 |

This setting would reject 779/935 previously accepted command predictions and
470/543 previously accepted NEUTRAL predictions. It would leave no accepted
NEUTRAL prediction in the second saved stream. Some rejected predictions could
be wrong and some could be genuine; the absent physical labels prevent that
distinction. These counts demonstrate the potential rearming/recall cost of
blind tightening, **not** improved false-action performance or a safe setting.
Keep the current profile unchanged pending a labelled development comparison.

## Existing files needed next — no new collection requested

Hau Jie should send a private `PRIVATE_P02_PROFILE_DEVELOPMENT.zip` containing:

1. The original saved **P02 Original** profile JSON used for these captures,
   copied without editing, plus its referenced numeric dataset manifest and
   feature `.npz` sidecar. Include a source-to-archive path map so relocation can
   be performed on a copy while preserving original bytes and input hashes.
2. Existing P02 DEVELOPMENT validation-positive and validation-negative manifests
   and their sidecars, including invalid records and trial/session identity.
   Exclude all TEST. Identify any missing or differently collected condition.
3. If available, the existing repaired profile/TRAIN inputs, fixed configuration
   and result behind the earlier reported P02 macro-F1 0.936508. That result is
   still attributed until its exact inputs reproduce; no new tuning is requested.
4. Existing pose-to-label notes, internal-use permission, source/dependency
   versions and SHA256 inventory. State whether index-only negatives and hand
   orientations from the live report are represented in the old development set.

GPT can gather these **existing** files on Hau Jie's laptop. Hau Jie checks that
the chosen original profile is the one actually used and authorises the private
handoff within its consent. Do not send the whole environment, camera recordings,
unrelated profiles, personal target bindings or credentials. Keep the originals.

Deston can then verify hashes, reconstruct the exact original model revision,
inspect trial coverage and reproduce the already reported fixed comparison.
Use the existing `development_diagnosis`, dataset and profile helpers; do not
build another evaluator. A bundle containing TEST must be rejected before fitting.
Report all four classes, UNKNOWN misses, negative command counts and acquisition
limits. The older H1 starter packet does contain P02 data, but it is **not proven
to be this saved personal model's input** and must not be substituted silently.

Only after that baseline is identified should a new repair be predeclared. Its
written plan must fix input hashes, one change, development splits, metrics and
stop criteria before execution; retain original profiles and results. No parameter
relaxation, TEST tuning, invented annotations or release approval from reused
validation. If new collection is actually needed, first specify the missing
condition and obtain consent rather than request another full Practice run.

## Native diagnostic remains unresolved

The retained stderr includes `0x8001010d`. Microsoft identifies this as
`RPC_E_CANTCALLOUT_ININPUTSYNCCALL`, an outgoing COM-call restriction during an
input-synchronous call. The Python frame at `app.exec()` identifies the GUI event
loop, not the responsible native component.
[Microsoft COM error reference](https://learn.microsoft.com/en-us/windows/win32/com/com-error-codes-3).

Later MediaPipe messages and successful captures exist, but the log lacks the
process/time boundaries and exit evidence needed to establish whether that exact
process terminated. Do not call this a confirmed crash, a resolved issue or a
clean stability pass. Javier and Hau Jie retain it with the native recovery work.
If it recurs during an already planned check, keep separate launch stdout/stderr,
PID, start/end times, actual exit code and triggering action; if Studio exits,
retain the matching Windows Application Error/WER faulting-module record. No
speculative exception suppression, camera-backend or font workaround is applied.

## Acceptance and ownership

The diagnostic collection, packet verification and numeric review substeps are
complete. GF-P21 still requires a demonstrated repair/defect disposition and its
original GF-P20 affected checks; GF-P24 requires the resulting methods/results
reconciliation. No whole task gained acceptance from this packet alone.

| Member | Accepted weight | Next manual action | Next GPT action |
|---|---:|---|---|
| Deston | 34/75 — 45.3% | Review integrated workflow/release evidence when prerequisites pass | Rebuild exact P02 baseline when its existing input packet arrives; review PRs and integrate demonstrated fixes |
| Hau Jie | 63/75 — 84.0% | Confirm exact P02 profile/files for private handoff; continue assigned laptop-B cases | Package existing original/repaired development inputs; reconcile methods with this review |
| Javier | 54/73 — 74.0% | Finish native target/recovery cases; record process evidence if the native fault recurs | Consolidate both laptops' records, fix reproduced defects and update the guide/video evidence |
| Total | 151/223 — 67.7% | 19/29 tasks accepted | Original weights, dependencies and acceptance criteria retained |

Both teammates continue on their own branches and open focused PRs for Deston.
Prompt/decision logs are untouched. Frozen TEST outcomes are preserved. This
review records a recognition limitation honestly rather than claiming a fix
from unavailable labels or increasing progress for an unfinished whole task.
