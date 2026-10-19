# P03 Preview trace review — 19 October 2026

Deston's integration review, with AI assistance, of Javier's supplied PREVIOUS
and index-negative diagnostic traces and cumulative session summaries. These
are short development checks, not scored trials or a personal Live grant.

## What the evidence establishes

Both traces identify the same saved profile and model. The supplied settings
screenshot reports Right hand, kNN, distance multiplier **1.5**, ambiguity margin
**1.0**. Settings are user-supplied evidence, not embedded trace metadata.
Javier's [PR #33](https://github.com/Chi944/GestureForge_304/pull/33) identifies
the runtime as the 16 October `d200947` Studio handoff and describes four thumb-up
holds and an index-finger-only check. Exact physical-pose intervals were not
independently annotated.

| Recorded/reconstructed measure | PREVIOUS check | Index-negative check |
|---|---:|---:|
| Recorded frames | 890 | 213 |
| First-to-last receipt span | 58.359 s | 17.532 s |
| Accepted PREVIOUS predictions | 198 | 0 |
| Accepted NEXT predictions | 0 | 54 |
| Accepted NEUTRAL predictions | 148 | 38 |
| Distance-rejected predictions | 41 | 36 |
| No-hand observations | 502 | 85 |
| Wrong-hand observations | 1 | 0 |
| Reconstructed / recorded simulated commands | 4 / 4 PREVIOUS | 2 / 2 NEXT |

The current controller exactly matches the packaged controller source. Replaying
the consumed predictions reproduces the recorded command order and count; summary
timestamps match receipt times or follow within 16 ms. One continuous accepted
PREVIOUS run spans **10.781 seconds / 100 frames** and emits once. Accepted NEUTRAL
subsequently rearms. No controller or dispatcher mismatch is demonstrated.

The later summary contains the first four PREVIOUS event IDs plus two new NEXT
IDs. The combined evidence therefore contains **six unique simulated actions**,
not ten. No application launch or real card movement is established by Preview.

Each trace includes one stale packet (312 ms / 234 ms old) and a following
capture gap (296 ms / 219 ms). All occur before the commands and are followed by
successful rearming. They remain timing observations, not an established cause
of the unwanted NEXT activations.

## Interpretation and next work

PREVIOUS activates in this recording; that does not resolve every earlier
intermittent rejection. The remaining actionable finding is **two unwanted NEXT activations during the
reported index-only negative check**. Those arise from accepted NEXT predictions;
the controller applies its existing hold/rearm policy to them correctly.

Margin 1.0 bypasses the optional ambiguity-ratio test by design. Distance rejection
remains active. It is not evidence that raising the margin will fix this pose:
these privacy-preserving traces contain no landmarks, feature vectors, distances
or class thresholds. Do not change the saved settings, weaken rejection, alter
controller timing or install the unsuccessful palm-local experiment from this
evidence alone. Do not repeat the supplied PREVIOUS check merely to obtain another
successful recording.

- **Hau Jie / GPT:** inspect the same saved P03 profile and existing DEVELOPMENT
  feature data when supplied privately. Reproduce its current settings and audit
  class separation and negative examples before predeclaring any repair. Consumed
  TEST data remain excluded from tuning. If existing data do not contain the
  failing index pose, explain the minimum missing evidence before requesting it.
- **Javier:** retain the current profile/data unchanged and provide their existing
  private numeric files if available, together with intended-pose notes. Continue
  camera-free laptop-A recovery checks and coordinate Hau Jie's laptop-B checks.
  A new full Practice attempt is premature while the negative action is unresolved.
- **Deston:** integrate demonstrated repairs and reconcile the resulting evidence;
  retain the current Live gate and original task acceptance criteria.

## Guide repair and verification

PR #33's Windows guide initially asked users to wait for READY before every
Practice window. That is impossible for a NEUTRAL preparation phase: its rearm
transition is deliberately measured inside the window. The reviewed correction
separates action/negative windows (READY before Begin) from NEUTRAL windows
(fresh capture, Begin, then NEUTRAL). See [the corrected guide](GF_P25_WINDOWS_GUIDE_DRAFT.md).

Fresh targeted verification: **95 tests passed** across trace validation,
trace diagnosis, controller and Practice. Independent review checked the guide's
relative links/assets/launchers against the identified source ZIP and approved the
correction. Runtime code is unchanged; the earlier full 1,010-test run remains a
dated separate result, not a new run. No replacement Studio ZIP is required.

Private review receipt: `experiments/local/p03-trace-review-20261019/review.json`.
It records original-file hashes, source parity, counts and event reconciliation.
Original trace/summary bytes are unchanged; raw files and identifiers stay local.

GF-P25 moves from To Do to In Progress because its guide draft is now reviewed and
merged. Its demo, guide-only release checks and GF-P23 dependency remain open.
GF-P16/GF-P20/GF-P21 retain their original integration and physical-test gates.
Accepted totals remain **137/223 (61.4%), 17/29 tasks**; these diagnostics are not
accuracy, latency, ten-minute negative testing, full Practice or device acceptance.
