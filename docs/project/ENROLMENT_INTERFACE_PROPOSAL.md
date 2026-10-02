# GF-P07 guided enrolment interface proposal

Local component delivery, 2 October 2026. Owner: Hau Jie. Integration: Deston.
PR #14 profile persistence is still a separate review dependency. This work stays
local while that PR is open so its review diff remains unchanged. It is not yet
connected to Studio and does not establish GF-P07 live acceptance.

## Components

`EnrolmentSession` in `gestureforge/enrolment.py` consumes timestamped shared
`Observation` objects. `EnrolmentWidget` is an embeddable PySide6 widget providing
consent, participant ID, selected hand, three editable pose descriptions plus
NEUTRAL, TRAIN/VALIDATION choice, trial count, instructions, countdown, progress,
invalid-sample feedback, stop and save retry. It does not create an application,
camera worker, classifier or action dispatcher. The existing shell owns the video
preview. Default canonical IDs are G1/G2/G3/NEUTRAL; descriptions are separate.

Each session gets its own generated directory and schema-2 manifest beneath the
private output root supplied by the shell. The suggested root is
`data/local/enrolment`. Numeric features and trial records use existing dataset
persistence; raw camera frames/video are never written. Do not export or commit
these directories. Consent is for numeric collection/internal evaluation only.

## Proposed host interface

| API / signal | Host responsibility |
|---|---|
| `EnrolmentWidget(output_root, parent)` | Embed under the existing shell. Keep the component alive while a save needs retry. |
| `capture_requested(plan, request_id)` | Pause the current routing session and honour trace-save failure. Suspend action dispatch; arrange collection observations using the existing capture service. |
| `attach_capture(request_id, capture_session, capture_profile)` | Call only after routing is suspended and capture is ready. A cancelled/old request returns false. Creates a new local collection session, not a camera. |
| `receive_observation(observation)` | Deliver on the widget's owner thread. The capture session/profile must match the acknowledged generation; timestamps share the monotonic clock used by the widget. |
| `capture_failed(request_id, reason)` | Report camera interruption. Preserve completed/partial trial evidence and release collection capture. |
| `capture_release_requested(request_id)` | Stop forwarding/release that collection generation. Keep action routing paused; do not automatically resume live gestures. Ignore releases for old generations. |
| `dataset_saved(manifest_path)` | One notification after full session completion. Show saved counts, then offer the later profile/training step; this is not a trained model or readiness signal. |

The current capture worker exposes predictions for the existing UI; this proposal
requires Deston's reviewed observation-delivery adapter. Do not start a second
camera thread or route enrolment observations through action dispatch. Host methods
must reject stale requests/results after screen changes and shutdown. The widget
cannot enforce the state of an external dispatcher; the host handshake is a
required integration condition, not proof supplied by a checkbox or signal.

Before closing the parent shell, call `stop_collection()` and check whether
`widget.session.state == 'save_error'`. If so, keep the widget and pending trial
alive for retry. Closing the widget directly refuses while a save is pending;
hiding it stops collection. A parent forcibly destroying the widget cannot be
made durable by the child alone. Pause/focus loss must invoke `stop_collection()`
through the same host lifecycle path.

## Trial timing and evidence

The operator presses Begin trial after preparing the named pose. A two-second
countdown precedes a two-second hold; five samples are scheduled at 0.2, 0.6, 1.0,
1.4 and 1.8 seconds into the hold. Capture timestamps must be within 200 ms after
their slot, and delivery must be at most 200 ms old. No frame fills two slots.
Wrong generation/profile, duplicate frame IDs, non-increasing timestamps and
future/stale observations cannot contribute valid features. Timer ticks mark
absent samples invalid even when the camera stops delivering frames.

Wrong/multiple/no hand, malformed landmarks and degenerate/non-finite features
retain their error reason as invalid slots. Invalid slots are not silently
replaced with later good frames. Completed trials save automatically and require
a one-second release before the next Begin trial. Default twelve trials per
label matches the personal collection plan; two through twelve are supported for
software/pilot workflows and the configured count is reflected in the records.

Stopping during the countdown before sampling starts saves no new trial. Stopping
during a hold retains captured slots and records remaining slots as invalid with
the interruption reason, then saves that trial. Previously saved trials remain.
Saving failure retains the pending trial in memory and disables further trials.
Retry saves the same trial once. Stopping while a save is pending keeps that
evidence for retry, then ends the session. Crash/power-loss recovery of unsaved
in-memory data is not implemented; previous successful saves remain available.

## Review and next integration

The numeric session format can be passed to the PR #14 profile store after
successful TRAIN collection and user confirmation. An all-invalid completed
session is still evidence, but cannot be trained into a usable profile. No
automatic profile creation, training, overwrite/recollection, UNKNOWN collection,
readiness pass or action dispatch is introduced here. Separate validation creates
a new session directory; any later evaluation must retain the actual split.

Tests use generated observations to exercise all poses, valid/invalid slots,
missing camera output, generation and frame filtering, independent validation,
fault/stop preservation, save-failure retry and the widget's consent/capture
handshake. An offscreen preview was inspected for readable labels and controls.
No new personal data was collected, and no physical-camera workflow recording
was produced. The host adapter, profile selector, camera retest and short workflow
recording remain necessary before integrated acceptance. GF-P28's rejection
limitations are unchanged.

Local verification (2 October, existing Python 3.11 environment, this checkout on
PYTHONPATH): `python -m pytest -q tests/test_enrolment.py` reports 17 passed;
`python -m pytest -q` reports 409 passed, 1 skipped in 37.50s. Ruff passes for
`gestureforge tests scripts`; mypy passes for `gestureforge scripts tests` (57
source files). The preview renderer explicitly loaded the Windows Segoe UI font
because the offscreen platform initially lacked a usable default font; this does
not change application font settings. These are local software checks.
