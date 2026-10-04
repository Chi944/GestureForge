# Practice Begin timing diagnosis — 3 October 2026

## Latest setup timeout and UI repair — 4 October

The follow-up on `aaef21a` ended during setup for the first NEUTRAL window,
after two correct covered actions and one covered BOOKMARK miss. The last Begin
request saw a frame 218 ms old; the unchanged 30-second setup timer then cancelled
the attempt. This differs from the earlier stale-frame failure during measurement.
The BOOKMARK miss remains a measured miss; this diagnosis does not explain it
or justify changing recognition thresholds. The original private export is
preserved unchanged.

Practice v3 waits up to two seconds after an explicit Begin request for a fresh
packet and the required READY state. Setup timeout now releases capture and
offers Retry setup for the same prompt, retaining completed windows and a
separate setup-retry record. It does not retry or replace scored misses.
The four generated 50-window host regressions include the observed Begin age,
setup timeout, earlier stale setup and measured-frame cases. They demonstrate
software continuity, not physical recognition accuracy. Original timing, order,
focus and generation protection remain enforced.

Practice entry and active action controls fit the tested 900x620 workflow pane
at 125% scaling. Negative cues now open in a separate dialog; tab arrows and
scrollbars use the dark palette. Current validation is recorded in
`verification.json`. Physical acceptance of this revision remains unverified;
do not request another long recording until software/review checks pass.

## Deston's P01 follow-up — 4 October

An assisted webcam check on `a738c0a` used the existing P01 pilot recogniser
(right hand, kNN, multiplier 2, margin 1.5, camera 1). In the latest saved attempt,
NEXT and PREVIOUS each completed a covered five-second window with exactly one
intended simulated action. BOOKMARK preparation was interrupted before Begin
with the generic invalid/stale-packet reason. An earlier attempt completed NEXT
and then timed out during preparation. These partial attempts remain saved
locally; they are not a completed rehearsal or a final recognition estimate.

Zero measured frames on the interrupted preparation does not establish a camera
failure: frames are counted only after Begin. The old generic error combines
malformed, late, future and out-of-order input, so the saved record cannot identify
which condition occurred. Do not infer a failed physical pose or change rejection
thresholds from that message. Camera shutdown after a completed five-second
window is intentional; the next preparation opens a new capture session.

The setup display also incorrectly reported no recogniser while the P01 model
was loaded. The entry/status repair adds **Open Practice** and updates availability
from the actual model/loading state while preserving saved diagnostic messages.

The original P02 observations below remain attributed to Hau Jie and separate
from this local P01 check. Full participant acceptance is still incomplete.

Review base: `b44df9a`; physical pilot ran on `ab0305d` with these local changes.
Owner: Hau Jie. Full physical acceptance remains pending.

The former cancellation text, “Action occurred before Begin window”, covered
two different paths: a protected command emitted during preparation, and a
non-NEUTRAL prediction captured before Begin but delivered after it. The latter
can cancel without emitting any command. An existing fixed-latency regression
reproduces that path after a successful Begin. This makes the old message
insufficient evidence that a participant clicked late or that an action occurred.

The component now distinguishes these cases and exports local timing diagnostics
for the latest prepared trial: the latest Begin request, acceptance or rejection,
controller state and last capture timestamp; plus the boundary prediction's
capture/receive times and whether it emitted a command. These are software
timestamps and predicted labels, not physical intent or mouse-press evidence.
The widget explicitly says whether measurement started or Begin was rejected.
It also displays the remaining five-second measurement time, a short finishing
message during the existing late-packet drain, and the next-step instruction.
Reading the countdown does not mutate timing, scoring or controller state.
Qt's `clicked` signal runs on button release; a physical mouse press alone does
not establish the start timestamp. Successful retry replaces the latest Begin
diagnostic. Preparing a new trial resets it; this is not a full event history.

Scoring, pre-window cancellation, controller hold/rearm policy and classifier
thresholds are unchanged. Original private results are retained unchanged.
Past files contain no Begin-request timestamp, so the historical cause cannot
be resolved from their generic cancellation reason alone.

## Supplied observations and remaining evidence

The private pilot contains successful G1/G2 trials and missed G1 trials with
margin rejections. Rejection counts alone do not establish the cause of a miss;
the saved aggregate does not identify the physical pose or each rejected label.
One earlier attempt was explicitly reported by the participant as following the
prompt one pose late. Keep that observation separate from classifier performance.

In a later saved attempt, the first G1, G2 and G3 windows each produced exactly
one correct simulated command with complete coverage. The NEUTRAL window had
complete coverage but did not reach READY and recorded 56 margin rejections.
A following G1 preparation was interrupted. This is four completed windows,
not a completed 50-window rehearsal or a recognition accuracy estimate.

A separate Preview trace reconstructed NEUTRAL -> READY, one G1 command, and
another NEUTRAL -> READY transition. Hau Jie reported seeing READY and explicitly
confirmed making a fist during that trace. Its G1 event must therefore not be
reported as a false activation. Exact physical-pose intervals were not annotated.
The trace includes both accepted and rejected NEUTRAL predictions; it supports
successful rearming in that run, not uniformly reliable NEUTRAL recognition.

The host cancels on focus loss. Its saved generic Stop/focus-interrupted reason
does not distinguish explicit Stop, hiding the widget and loss of focus.
Hau Jie confirmed switching windows for one attempt; other generic records
must not automatically be attributed to focus loss.

## Shared-shell handoff for Deston

**Historical handoff, resolved in the 4 October integration:** the observations
below describe the shell before integration. The fixed footer now follows the
Practice phase, and new saved interruptions distinguish Stop, camera Pause,
focus loss, hiding the tab, closing Studio and configuration changes. Existing
generic records remain ambiguous. Regression tests establish the changed
software behavior; the targeted physical check below is still required.

During Practice, `app.py` still reaches its ordinary READY footer instruction
to hold a mapped gesture, even when the practice component is waiting for Begin.
Please make that footer follow the Practice phase: keep NEUTRAL before Begin,
then show the prompted pose after measurement starts. This conflicting guidance
may contribute to confusion, but is not a proven cause of any specific attempt.
Please also consider recording distinct host interruption reasons. No shell,
controller or routing files were edited in this change.

## One targeted physical check

Restart the updated Studio, load the existing P02 profile and start Practice.
Prepare G1, keep an open palm until READY, then click and release Begin while
still showing the open palm. Verify “Measurement started”, then show G1 until
the five-second window ends. After that one window, stop and preserve results.
If capture closes early, preserve the displayed message and inspect the new
timing diagnostics. Do not repeat the full 50-window protocol for this probe.

## Local verification

On this Windows checkout, the focused Practice/component-host tests passed
39 tests. The full suite passed 620 tests with one platform-specific skip in
109.53 seconds. Ruff passed for `gestureforge tests scripts`; mypy passed for
`gestureforge scripts tests` (76 files). Both assignment and Studio startup
smoke checks exited 0. Tests reproduce delayed pre-Begin classification after
a successful Begin, unsuccessful Begin and successful retry, and explicit widget
start feedback. These are historical software checks before the final sync and
countdown handoff; final publication checks are recorded below. The physical
pilot above is partial evidence and the full 50-window rehearsal remains pending.

Final publication validation after syncing `b44df9a`, including the countdown:
`python -m pytest -q`: **639 passed, 1 skipped in 109.48 seconds**.
`python -m ruff check gestureforge tests scripts`: passed.
`python -m mypy gestureforge scripts tests`: passed, 78 source files.
`python -m gestureforge --smoke-test` and
`python -m gestureforge --studio --smoke-test`: both exited 0.
`git diff --check`: passed. Only owned source, tests and aggregate handoffs are
included; all participant datasets and full diagnostic/results files stay local.
