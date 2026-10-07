# GF-P19: Harbor laptop A follow-up, 5-7 October 2026

Operator: Javier Ng. Guided human observations on laptop A, supported by
user confirmations, screenshots and private Session summary exports.
Device: previously recorded Windows 11 Home, version 10.0.26200/build 26200;
camera index 0. No new OS inventory or Python-version output was supplied.

Preserve PR18/GF-P05 and the accepted PR24 report
`GF_P19_HARBOR_LAPTOP_A_2026-10-04.md` unchanged. This follow-up does not
reopen accepted GF-P13 or claim complete GF-P19/GF-P23 acceptance.

## Source boundaries

- Manual Harbor observations on 5 October and camera checks on 7 October
  preceded the sync and used `9e109a7`.
- On 7 October, `codex/javier-shortcuts` synced `origin/main` to `5595129`;
  the supplied terminal screenshot shows that HEAD and a clean working tree.
- Only the focused Quick Actions missing-target notice/recovery case and the
  software checks below were repeated on `5595129`. Earlier native observations
  do not establish acceptance of all subsequently integrated changes.

## Manual Harbor observations on 9e109a7

| Case | Human observation / evidence boundary |
|---|---|
| Calculator | Calculator opened; screenshot captured the result 240 for 8 x 2 x 15. |
| Reference | Fictional reference text opened; escalation contact was the training coordinator. The screenshot did not independently establish the full file path. |
| Resource folder | Explorer opened and corporate_reference.txt was visible. |
| Missing disposable reference | The disposable recovery TXT was renamed; export records a missing-target failure in discussion, without a stage advance. |
| Explicit recovery | Filename restored; user supplied a screenshot of the reopened text. Export records the subsequent recovery-reference launch request. |
| Restore / no replay | Discussion stage and camera-off state restored; user confirmed no app/file opened automatically. Immediate post-restore export has a new revision, no events and zero launch requests. |
| Bookmark persistence | Post-restore screenshot shows one Save a discussion point (discussion) bookmark. No second bookmark was added during verification. |
| Paused-state boundary | A later screenshot shows Paused after the explicit Pause/camera off step. The first restore screenshot still showed manual LIVE controls active; strict restoration of a fully paused manual state was not established by that screenshot. |
| HTTPS | Harbor HTTPS request recorded; screenshot shows example-domain page content. Browser address bar/HTTPS transport was not captured in that screenshot. |
| Windows Camera | Camera launch request recorded; user reported live webcam video in Windows Camera. |

## Separate camera checks on 9e109a7, 7 October

The original Harbor workspace binds G1/G2/G3, while the supplied P03 manifest
labels are NEXT/PREVIOUS/BOOKMARK/NEUTRAL. Screenshots showed manual-only stages
and disabled camera Start in the original workspace after loading P03.

A local, ignored test copy mapped G1 to NEXT, G2 to PREVIOUS and G3 to BOOKMARK
in quick bindings and all stage bindings. The original shared workspace was
not edited. This is a test configuration, not a recognition acceptance result.

With P03 loaded and this copy in Preview, Javier reported live Studio video.
After Alt+Tab away/back, screenshot shows Camera off and Paused after focus loss.
Explicit Start restored live video. During another live Preview capture, Javier
opened Windows Camera through Windows Start; he reported Windows Camera live
video and Studio camera off on return. After closing Windows Camera, explicit
Studio Start restored video; Javier then paused capture.

This supports focus-loss release and explicit reacquisition on the local test
copy. It does not verify Camera launch through a GestureForge shortcut while
capture is active. No full Practice pass, personal LIVE grant or recognition
performance acceptance is claimed.

## Visible missing-target notice / recovery on 5595129

Guest/manual, no dataset, camera off, explicit LIVE manual controls.
Quick Actions BOOKMARK slot was bound to recovery-reference while the disposable
TXT existed, then Use Quick Actions activated the context.

1. The bound action opened the fictional reference text (supplied screenshot).
2. Only the disposable TXT was renamed to harbor-reference-test.txt.missing.
3. After explicit manual LIVE reactivation, the bound action failed. Screenshot
   shows the top notice: Action failed, target missing or moved, with restore or
   rebind and retry guidance.
4. The filename was restored, manual controls explicitly reactivated and the
   same bound action retried. Javier confirmed the text reopened.

The final export records launch_requested, failed, launch_requested in the same
Quick Actions context. Five preceding Test selected target failures are separate
validation attempts in intro; they are not five failed native launches.

Exact rename commands from the project directory:

```powershell
Rename-Item -LiteralPath ".local\harbor-reference-test.txt" -NewName "harbor-reference-test.txt.missing" -ErrorAction Stop
Rename-Item -LiteralPath ".local\harbor-reference-test.txt.missing" -NewName "harbor-reference-test.txt" -ErrorAction Stop
```

## Private export reconciliation

Raw exports, datasets, local target paths and test workspaces remain under
ignored local storage; do not commit them.

| Export basename | Counts / scope |
|---|---|
| harbor-laptop-A-before-restore-2026-10-05.json | 5 launch requests, 1 failure, 6 applied events, 4 acknowledged stages. |
| harbor-laptop-A-after-restore-2026-10-05.json | Fresh revision; zero events and all counts zero. |
| harbor-laptop-A-final-2026-10-05.json | 2 applied advances; discussion/review acknowledged; no launches or failures. |
| harbor-laptop-A-camera-https-2026-10-07.json | Includes the final export's events; 2 launch requests (HTTPS and Camera), 2 simulated PREVIOUS requests, 7 applied events, 2 acknowledgements, zero failures. |
| harbor-laptop-A-notice-check-2026-10-07.json | On the new revision: 5 target-test failures, zero launch requests. |
| harbor-laptop-A-notice-recovery-2026-10-07.json | Includes notice-check events; 2 launch requests, 6 failures (5 target-test failures plus 1 missing-target dispatch failure), zero stage acknowledgements. |

Do not add overlapping final/Camera-HTTPS or notice-check/notice-recovery counts.
The disjoint before-restore and later segment record six acknowledged stages.
Launch requests alone do not prove OS launch or human task completion.

## Software checks on 5595129

Commands run by Javier in the Windows project virtual environment:

```powershell
.\.venv\Scripts\python.exe -m ruff check gestureforge tests scripts
.\.venv\Scripts\python.exe -m mypy gestureforge scripts tests
.\.venv\Scripts\python.exe -m pytest -q
.\run.cmd --smoke-test
$LASTEXITCODE
```

- Ruff: all checks passed (supplied terminal screenshot).
- mypy: no issues in 95 source files (supplied terminal screenshot).
- pytest: 862 passed, 1 skipped in 497.64 seconds (supplied terminal screenshot).
- Smoke test: exit code 0 (Javier's confirmation).

## Remaining work and limitations

- Laptop B remains Hau Jie's Windows laptop, operated by Hau Jie, with Javier
  coordinating and Deston reviewing acceptance, as assigned by Deston on
  5 October. The supplied follow-up's different operator statement does not
  change that assignment. No laptop-B operator record/results were supplied.
- Laptop B integrated cases and fresh independent installation, offline core,
  thirty-minute Studio stability, measured rates/memory and clean shutdown
  evidence remain unverified in this follow-up. Deston retains final acceptance.
- Missing file association, selected trusted executable and the broader
  invalid-target matrix were not run in this follow-up. Preserve earlier GF-P05.
- Strict paused manual-state restoration and shortcut-triggered Camera handoff
  during active capture remain unverified as described above.
- No whole native walkthrough was repeated on 5595129; no macOS launch evidence.
- No owned component code defect was demonstrated or repaired. The G1/P03
  mismatch was addressed only in a local test configuration. The visible
  dispatch failure notice was verified on the integrated shell.

AI assistance guided commands and reviewed supplied screenshots/exports.
Javier operated the Windows applications and supplied the observations.
