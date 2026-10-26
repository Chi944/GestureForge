# GF-P19: Deston desktop and camera checks — 26 October 2026

Source checked: `3cdfe99f0a648ac04609d31dacf89cbe75d43ed6`.
Device: Deston's Windows laptop; operator: Codex using native desktop controls.
Deston confirmed the webcam was connected. This is additional integration evidence,
separate from Javier's laptop A and Hau Jie's laptop B.

## Results

| Check | Observed result | Evidence boundary |
| --- | --- | --- |
| Affected automated tests | 142 passed, 1 skipped in 27.96 s | Symlink test skipped because this host lacks creation permission. Fake camera/OS tests do not prove physical behavior. |
| Native target-validation API | 19/19 expected results: 14 refusals and 5 positive controls | Real Windows paths and drive classification; no mocks, UI save claim or OS execution in this test. Refused registry changes left state unchanged. |
| Manual LIVE Calculator | Actual Calculator window opened | Guest/manual, capture off; launch request and native observation are separate evidence. |
| Missing reference and explicit retry | Missing file refused with recovery message; restoring it did not launch anything; explicit shortcut retry opened the expected text in Notepad | Disposable local file moved and restored. Summary records two launch requests, one deliberate failure, zero duplicate events. Dedicated retry counter and completion acknowledgements remain zero. |
| Same-camera pause | Camera index 1 showed live frames; Use camera and pause stopped capture with the index unchanged | Preview; explicit Start reacquired the camera. |
| Focus loss and resume | Activating blank Notepad paused/released capture; returning to Studio left it off; explicit Start reacquired it | Preview focus behavior, not gesture LIVE dispatch or a Windows Camera shortcut handoff. |
| Close during capture | Normal-close event and QApplication return 0; separate subprocess subsequently read five fresh 640 x 480 frames and exited 0 | Short lifecycle/reacquisition check; not a full Studio endurance or independently measured Studio OS-exit result. |

The existing personal profile and recognition settings were unchanged. No new
training samples, camera recording, association edits or user trust settings were
saved. The disposable launch and camera harnesses isolated output folders and
added measurement only; application dispatch/controller behavior was unchanged.

Camera instrumentation used Python object IDs, which were reused across starts.
Three starts produced two frame-count buckets. Do not infer continuous duration,
per-session frame rates or stability acceptance from those aggregates.

## Remaining work

GF-P19 stays **In Progress** under its existing two-device criterion. Reuse the
unchanged A/B passes in the [case matrix](JAVIER_WINDOWS_REMAINING_CASES_2026_10_25.md).
This additional device must not be silently relabelled as either laptop.

- Javier consolidates the remaining A native input/association cases and both
  devices' receipts. Mapped-drive refusal needs an actual mapped-drive fixture;
  none exists here. A packaged-image association lookup was inconclusive, so no
  native missing-association/recovery pass is claimed.
- Hau Jie completes B's outstanding unavailable-slot, same-camera pause and
  focus/resume cases, preserving exact build and actual outcomes.
- Active-capture Windows Camera shortcut handoff remains unrun where runtime
  eligibility is unavailable. Do not weaken the gate or restart failed Practice
  searches merely for this check.
- Fresh installation and measured full-Studio endurance/exit remain GF-P23
  release work; these short checks do not replace them.

No production defect was reproduced in these checks, so no application code was
changed. Whole-task accepted progress remains **183/223 (82.1%), 23/29 tasks**.

## Reproduction and private receipts

```powershell
$env:QT_QPA_PLATFORM = 'offscreen'
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider tests/test_javier_lane.py tests/test_app_dispatch.py tests/test_quick_actions_acceptance.py tests/test_app_studio_recovery.py
```

Original numeric logs, isolated fixtures/harnesses and a checksummed receipt remain
under the ignored `.local/p19-deston-20261026` folder. Its `receipt.json` SHA256 is
`abcbfb3c754b484e137c679d9e2cb9f27e3e6c3a09d7b88fddfc65aaef1cc973`. The receipt hashes the original software, API, UI and camera evidence.
No private profile/data/log contents are published.
