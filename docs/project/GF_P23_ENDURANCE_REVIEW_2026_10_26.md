# Studio endurance and laptop-B receipt review — 26 October 2026

## Deston's completed run

Source: `922ced4a22d9a49fb12160f4febc4e3e09f45bbb`. Deston's Windows laptop,
camera 1, existing P01 fixed-validation profile, Studio Preview. Codex launched
the monitor and loaded the unchanged profile; Deston kept the session running
and reported completion. This was an assisted existing installation, not the
fresh guide-only laptop-B installation.

| Measurement | Saved result |
| --- | --- |
| Delivered observations | 54,396 in one camera generation |
| Longest continuous interval | 1,940.578 s (32 min 20.578 s); duration target reached |
| Camera-active estimate | 2,043.594 s; 26.618 delivered observations/s |
| Peak process memory | 426,065,920 bytes (406.328 MiB) |
| Maximum active GUI / delivered-frame gaps | 5.062 / 5.094 s; both exceed the existing 2-second limit |
| Worker errors / unexpected stops | 0 / 0 |
| Shutdown | Normal window close, Qt event loop 0, all workers released |
| Monitor child exit | 1: measurement criteria failed; not evidence of an application crash |
| Separate post-close camera check | Camera 1 acquired five 640 × 480 frames, released, process exit 0 |

Deston reports no visible interruption, app switching, screen lock or system
prompt. This operator observation is retained alongside the measured gaps.
The old aggregate report does not timestamp the gap, so its location and cause
remain unknown. It cannot be attributed to focus loss, autofocus, or a particular
application defect from these files.

**Accepted substeps:** duration reached, measured resource/observation evidence,
normal Qt close, worker release, and independent post-close reacquisition.
**Not passed:** the complete strict stability check. The earlier gap remains
part of this run even though a later continuous interval exceeded 30 minutes.
No original measurement, threshold, model setting or qualification record changed.

Private originals: `experiments/local/studio-soak-deston-20261026/`, containing
`measurement.json`, `process.json`, stdout/stderr and `camera-reopen.json`.
No raw images, video, hand features or labels were saved by this monitor/probe.

## Laptop-B originals now independently inspected

`PRIVATE_LAPTOP_B_NEW_RECEIPTS_20261026.zip` is 20,559 bytes, SHA256
`f18d6dbd2a3caac62c9d6843d06215a2f395d8a03eef523dc758862aaa510c0f`.
All 12 member paths are safe and unique; CRC and all 11 indexed payload hashes
pass. The ZIP was inspected without executing or extracting attached content.
It confirms the existing PR #40 inventory in the [device matrix](JAVIER_WINDOWS_REMAINING_CASES_2026_10_25.md).

- The interrupted Studio run has 6.922 s and 168 packets. Its 842 JSONL rows
  contain 835 waiting rows and 7 measuring rows, with a 1,034.595167 s maximum
  adjacent UTC gap. Event-loop exit 0 does not supply the missing OS exit receipt.
- The separate pipeline diagnostic has 300.016 s, 8,147 packets and process
  exit 0. Its rate/memory/exit cannot be combined with another Studio run.
- The separate post-close five-frame probe passed. Setup was assisted with a
  reused environment; the additional reported 30-minute attempt has no retained
  measurements. These are not new fresh-install or full-Studio passes.

The packet has arrived; neither teammate needs to resend it. Private originals
stay outside Git. This review verifies artifacts and arithmetic, not a replay
of Hau Jie's physical laptop.

## Monitor correction and next steps

The old timer could show remaining zero despite an earlier failed gap. The
monitor now displays a persistent gap warning and records the first GUI/frame
gap detection time in future reports. These bounded timestamps indicate when
a gap was detected, not its onset or cause. They add no per-frame storage.
35 monitor/launcher tests, Ruff and mypy passed. Existing pass/fail criteria
and the completed run are unchanged.

Do not ask Deston to repeat enrolment, Practice or this entire run blindly.
Review a future occurrence using the new warning/timestamps before prescribing
another full-duration attempt. Active-camera shortcut handoff is a separate
check, because transferring the camera intentionally interrupts capture.
Hau Jie still supplies the remaining fresh guide-only/offline laptop-B cases;
Javier consolidates the remaining native/recovery cells. Deston's additional
device does not replace those machine-specific results.

GF-P23 remains In Progress, including its GF-P22 dependency. Whole-task accepted
progress remains **183/223 (82.1%), 23/29 tasks**; the newly completed substeps
are recorded without awarding the whole eight-point release task prematurely.

## 27 October bounded camera diagnostic

A separate real Studio Preview run on Deston's camera 1 and unchanged saved P01
profile delivered 2,435 observations over 120.079 continuous seconds. Maximum
active GUI and delivered-observation gaps were 0.125 and 0.172 seconds. The
two-minute criteria passed, with normal closure, released workers and child
process exit 0. A separate post-close camera-1 probe read five frames and exited
normally. No raw frames or features were saved. This is a diagnostic,
not another 30-minute release test or recognition qualification.

The monitor now records the maximum duration of checkpoint generation and
saving, plus its completion time. This run's maximum was 0.062 seconds. It did
not reproduce or explain the historical five-second gap; neither the threshold
nor the earlier result changed. The two timing fields use bounded storage and
appear in a subsequent checkpoint/final report. Existing write failures still
propagate and prevent a pass.

Private aggregate: `experiments/local/studio-diagnostic-20261027/aggregate.json`.
The independent process receipt is retained with the local presentation-build
diagnostic records. PRs #41 and #42 now provide the reconciled device matrix and
[laptop-B checklist](LAPTOP_B_RELEASE_CHECKLIST_2026_10_27.md). Complete the missing
device cases and a qualifying measured endurance run before closing GF-P23.

Integrated verification after the Practice layout and monitor changes: 86 tests
across the five affected test files passed offscreen; Ruff and mypy passed the
six changed Python files. This is focused regression coverage, not a rerun of
every repository test or either teammate's physical device checks.
