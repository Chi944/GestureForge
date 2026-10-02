# Javier Windows evidence — 2 October 2026

Initial run source branch: `codex/javier-shortcuts` at `675d693` before the evidence-fix commit.
Raw evidence remains in the ignored local `.local/` directory and is not committed.

## Environment

- Probe laptop: `laptop-A`
- Reported platform: `Windows-10-10.0.26200-SP0`
- Python: 3.11.9
- Camera index: 0
- PySide6: 6.11.2
- opencv-contrib-python: 5.0.0.93
- mediapipe: 1.0.1
- Probe start: 2026-10-02T07:27:38Z

## Observed results

| Check | Result | Evidence and limitation |
|---|---|---|
| Calculator | PASS | Launch requested, Calculator visibly opened, and manual return recorded. |
| Routing pause | Observed | A `paused` row followed the first real frame. The dispatcher also pauses before launches, so this row alone does not establish focus loss as the cause. Probe pause stops routing; capture can continue until Camera handoff or close acknowledges shutdown. |
| Camera handoff | PASS after one refused retry | Capture produced a real frame and shutdown acknowledgement before Camera launch. A premature second request was refused. A later capture produced a real frame, shutdown was acknowledged, and Camera visibly opened. |
| Camera release/reacquisition | PASS | Capture restarted after manual return, produced a new real frame, and completed a second acknowledged handoff. |
| Permitted TXT file | PASS | The disposable reference file visibly opened in its associated application. |
| Existing folder | PASS | The configured `.local` folder visibly opened in File Explorer. |
| HTTPS | PASS | `https://example.com` visibly opened in the default browser. Page rendering/encoding was outside the probe's scope. |
| Missing target and recovery | PASS with evidence defect found | Moving the disposable TXT aside produced a clear pre-dispatch error. Restoring it and making a new request opened it successfully. The original probe did not persist the pre-dispatch failure row. |
| Probe shutdown | PASS | `probe_closed` was saved and the process returned to PowerShell. |

## Demonstrated defects and fixes

1. A failed Camera dispatch could receive an observer `visible=true` confirmation because confirmation always targeted the latest dispatch. The probe now keeps a pending confirmation only for `launch_requested` outcomes and refuses absent, failed, or duplicate confirmations.
2. Quick Actions displayed missing-target validation failures but the probe did not persist them. The widget now emits a validation-failure signal and the probe records `target_validation_failed` with the target ID and reason.

Regression tests cover both paths.

## Post-fix verification rerun

A focused rerun started at `2026-10-02T10:20:58Z` on the same laptop and package versions. It recorded:

- a failed Camera dispatch after `camera_handoff_refused`;
- `observer_confirmation_refused` when a visible confirmation was attempted for that failed dispatch;
- `target_validation_failed` for the moved disposable TXT;
- a new `launch_requested` dispatch after restoration, followed by `visible=true` confirmation and manual-return recovery; and
- clean `probe_closed` shutdown.

Javier reports these corrected JSON evidence paths verified on Windows. Integration review accepted this supplied observer record; it did not independently repeat the native run. The raw rerun remains in ignored `.local/` storage and is not committed.

## Remaining limitations / NOT RUN

- A missing file association was not forced because the procedure forbids changing the user's existing associations merely for a test.
- A camera shutdown timeout did not occur naturally and was not manufactured.
- An isolated focus-loss/explicit-resume check was not established by this record; verify it separately in the integrated shell.
- Windows invalid-input rejection and integrated-shell reload/long-hold/stale-context checks were not manually repeated in this isolated run; fake-adapter regressions remain software-only evidence.
- Only `laptop-A` was tested. GF-P19 still requires the integrated shell on both laptops and Deston's review.
- Observer confirmations are self-reported. This probe does not test gesture recognition quality, P03 accuracy, or application readiness.
