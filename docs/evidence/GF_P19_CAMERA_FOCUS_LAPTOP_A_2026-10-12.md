# GF-P19 / J1: Laptop A Camera and focus observations, 12 October 2026

Operator: Javier Ng. Guided human Windows checks, supported by supplied
screenshots, confirmations and a private Session summary export.

## Source and device

- Branch: `codex/javier-shortcuts`; sync fast-forwarded from `a7ccc17` to
  `ffa0af7`, with a clean working tree before observations.
- Exact source: `ffa0af741166da25175141f3dc99474a42d7b02f`.
- Microsoft Windows 11 Home, version 10.0.26200, build 26200.
- Project virtual environment: Python 3.11.9.
- Selected camera index: 0. Existing personal dataset P03, Right hand,
  KNN, rejection 1.5, margin 1.5. No dataset recollection was performed.
- Demo Studio with Quick Actions; NEXT bound to the existing local
  `harbor-camera` target, display name Harbor Camera test.
- Preserve PR18/GF-P05 and PR24/26/28 evidence with their original boundaries.
  The accepted short restore retest was not repeated.

## Actual observations

| Case | Mode and starting state | Result and evidence boundary |
| --- | --- | --- |
| Initial capture | Preview, P03, camera 0 | Javier reported live webcam video in Studio after explicit Start. |
| Isolated focus loss | Preview, capture reported live; Alt+Tab to PowerShell and back | Return screenshot shows Camera off, camera paused and camera released. Capture did not restart automatically. |
| Explicit focus recovery | Preview, camera off | Javier reported live video returned after clicking Start. |
| Camera request simulation | Preview, Quick Actions capture reported live | One manual NEXT Camera request simulated; Javier confirmed Studio video stayed live. No separate Windows Camera opening was reported for this request. |
| Native Camera launch | Explicit Live and Apply and pause; capture already off | One manual NEXT Camera request; Javier confirmed separate Windows Camera opened and showed live video. This was not an active-capture handoff. |
| Return after native Camera | Windows Camera closed, return to Studio without Start | Screenshot shows Camera off and Paused after focus loss. Start was disabled in Live; footer explicitly required a full personal Practice pass for gesture launch. |
| Reacquisition after native Camera | Changed to Preview, Apply and pause, explicit Start | Javier reported Studio live webcam video returned. This is Preview reacquisition after mode change, not a Live gesture resume. |

Screenshots were supplied for loaded configuration, pause/release and return
states. Actual moving video and the separate Windows Camera result are Javier's
confirmations; the assistant did not independently operate the native device.
The later screenshot-upload steps can also cause focus loss, so the screenshot
alone does not establish which focus transition produced the final pause text.

## Private summary reconciliation

Private export: `harbor-laptop-A-camera-focus-2026-10-12.json`, retained under
ignored `.local`. Do not commit the raw export or personal dataset.

- Schema 1; workspace scope Demo Studio, `demo-studio`.
- Summary revision: `revision-f4283b2d-e380-4f2c-8b5f-961bad308f34`.
- Exactly two unique manual event IDs, both OPEN_SHORTCUT for `harbor-camera`
  in Quick Actions context `quick-actions:8217c335`.
- One simulated outcome followed by one `launch_requested` outcome.
- Zero failed, duplicate, rejected, applied, unchanged, recognition-outcome,
  retry or acknowledged-completion counts. Trials and completed stages are empty.
- Parsing confirmed event statuses match the reported counts. The JSON records
  requests, not OS window readiness, capture shutdown ordering or focus telemetry.
  Native outcomes and recovery observations above come from Javier.

This is one cumulative snapshot. Do not add it to any later overlapping snapshot
from the same summary revision. Keep earlier dated summaries separate.

## Software checks on ffa0af7

Commands run by Javier in the Windows project virtual environment:

```powershell
.\.venv\Scripts\python.exe -m ruff check gestureforge tests scripts
.\.venv\Scripts\python.exe -m mypy gestureforge scripts tests
.\.venv\Scripts\python.exe -m pytest -q
.\run.cmd --smoke-test
$LASTEXITCODE
```

- Ruff: all checks passed.
- mypy: no issues in 100 source files.
- pytest: 900 passed, 2 skipped, 1 warning in 550.60 seconds.
  Warning: duplicate `collection.json` ZIP entry emitted by the duplicate-entry
  rejection test.
- Smoke test: Javier reported exit code 0.

These are supplied Windows results, not an independent assistant test run.

## Remaining limitations

- Active-capture native Camera handoff remains NOT RUN. Preview simulated the
  request; explicit manual Live selection paused capture before the real request.
  No shutdown-acknowledgement ordering during an active native launch is claimed.
- No full personal Practice pass or Live gesture readiness was established.
  Disabled Start in manual Live was consistent with the visible readiness gate;
  no bypass was attempted.
- Missing association, selected trusted executable, broader invalid-target matrix,
  native failure/retry, and no-replay after a historical real launch were not
  tested in this focused run. No file associations were changed.
- No component defect was demonstrated or repaired.
- Hau Jie operates laptop B; Javier coordinates its evidence; Deston retains
  final acceptance. No laptop-B results are included.
- No fresh independent install, offline or thirty-minute Studio stability,
  measured throughput/peak memory, or GF-P23 shutdown acceptance is claimed.
- This is bounded GF-P19 evidence; it does not close GF-P19/GF-P23/GF-P34.

AI assistance guided steps and reconciled the supplied export. Javier operated
Studio and Windows Camera and supplied the actual observations.
