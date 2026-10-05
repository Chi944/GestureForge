# GF-P19: Harbor human Windows observations, laptop A

Owner: Javier. Observations: 3-4 October 2026.
Tasks: GF-P13, GF-P34 and partial GF-P19.
Windows 11 Home, version 10.0.26200, build 26200; camera index 0.

## Revision and evidence boundaries

Native observations were performed on ab0305d.
The branch was subsequently fast-forwarded to aaef21a.
Software checks below were run after that sync; native observations do
not establish acceptance of the newly synced shell.

Preserve accepted PR18/GF-P05 evidence separately.
These are guided human observations, supported by supplied screenshots,
user confirmations and exported events. They are not independent replay
or Deston's automated native acceptance evidence.

## Actual targets and outcomes

| Case | Target | Observation |
|---|---|---|
| Calculator | Builtin calculator | User reported application opened; budget completion was acknowledged. Calculation result was not independently captured. |
| Reference | assets/corporate_reference.txt | Text opened; fictional escalation contact was the training coordinator. |
| Folder | assets | User confirmed folder opened and corporate_reference.txt was visible. |
| Missing file | Disposable local harbor-reference-test.txt | Renamed only the disposable copy; launch failed without advancing the stage. |
| Recovery | Restored disposable filename | User confirmed text reopened; export records failure followed by launch_requested. |
| HTTPS | Website https://example.com | Screenshot shows browser loaded the HTTPS page. |
| Camera | Builtin camera | User confirmed Windows Camera showed live webcam video. |
| Focus loss | Active Preview capture, Alt+Tab away/back | User reported live capture beforehand; return screenshot shows Camera off and paused after focus loss. |
| Reacquisition | Close Windows Camera, return to Preview and explicitly Start | User confirmed live webcam video returned inside Studio. |
| Paused restore | Saved Harbor session at discussion/recovery stage | Restored same stage, camera off; user reported no automatic launch. |
| Bookmark | Discussion/recovery stage | BOOKMARK applied event recorded before restore; persistence after restore was not separately inspected. |

## Private summary segments retained

Exports remain under ignored .local; do not commit raw archives or datasets.

- harbor-laptop-A-before-restore-2026-10-03.json:
  8 launch requests, 7 failures, 7 applied actions, 4 acknowledged stages.
  Failures include 3 unbound Calculator requests, 3 missing product-reference
  requests and 1 missing recovery-reference request.
- harbor-laptop-A-after-restore-2026-10-03.json:
  fresh revision; no events and zero launch requests.
- harbor-laptop-A-final-2026-10-03.json:
  2 applied stage advances and acknowledgements for discussion and review.
- harbor-laptop-A-camera-https-2026-10-04.json:
  1 HTTPS and 2 Camera launch requests; 5 simulated Camera requests;
  zero failures. Includes the preceding final-stage events.

The final and Camera/HTTPS exports overlap: do not add their counts.
Together the disjoint pre-restore and later segment record six acknowledged
stages. Launch requests alone do not prove OS task completion.

## Software checks on aaef21a

Commands run in the Windows project virtual environment:

    .\.venv\Scripts\python.exe -m ruff check gestureforge tests scripts
    .\.venv\Scripts\python.exe -m mypy gestureforge scripts tests
    .\.venv\Scripts\python.exe -m pytest -q
    .\run.cmd --smoke-test

Ruff: all checks passed.
mypy: no issues in 81 source files.
pytest: 728 passed, 1 skipped in 476.84 seconds.
Smoke test: passed with exit code 0.

## Remaining limitations

- Laptop B integrated checks have not been run.
- Camera release during a real launch from active capture is unverified:
  Preview simulated requests; switching to manual LIVE paused capture first.
- No live gesture readiness or recognition acceptance is claimed.
- No selected trusted executable or broader invalid-target matrix was tested
  in this walkthrough; preserve earlier GF-P05 evidence separately.
- Missing-target reasons were present in exported events but were not visible
  in the supplied Runbook/footer screenshots. Report this shell feedback
  observation to Deston; no shared-shell fix was attempted.
- No new component code defect was established or repaired.
- Native checks have not been repeated on aaef21a.
- macOS external launches remain unsupported/unverified.

AI assistance guided the steps and inspected supplied screenshots/exports.
Javier operated the Windows applications and supplied the observations.
