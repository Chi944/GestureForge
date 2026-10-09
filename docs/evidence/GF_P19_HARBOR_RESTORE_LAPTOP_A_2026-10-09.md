# GF-P19 / J1: Harbor restore retest on laptop A, 9 October 2026

Operator: Javier Ng. Guided human Windows observations, supported by supplied
screenshots, confirmations and six private Session summary exports.

## Source and scope

- Javier synced `origin/codex/javier-shortcuts`, then `origin/main`; the terminal
  records a fast-forward from `781b909` to `a1bb37a` and a clean working tree.
- Studio was started from that checkout with `.\run.cmd --studio`.
- Workspace: `assets/harbor_workspace.json`, Harbor onboarding, 10 cards,
  six stages and six semantic shortcut slots. Guest/manual, no dataset loaded.
- Camera remained off. Earlier device inventory was Windows 11 Home,
  version 10.0.26200/build 26200; no fresh OS/Python inventory was supplied.
  Camera index draft showed 0 initially and 2 in the Restore progress screenshot;
  no capture was started and no camera-device change was verified.
- Preserve accepted PR18/GF-P05, PR24 and PR26 evidence separately. This checks
  the affected restore behavior; it does not repeat the native walkthrough or
  establish full GF-P19/GF-P23/GF-P34 acceptance.

## Restore session

1. Preview navigation initially simulated: the pre-restore export retains
   16 ADVANCE_STAGE requests and one NEXT request in intro. These arose during
   setup before the mode was corrected; they are not failed native launches.
2. After explicit Live selection and Apply and pause, four stage advances
   reached discussion. One BOOKMARK applied at discussion. No task completion
   was acknowledged and no resource action was requested.
3. Javier paused and saved the session at discussion. Screenshot shows Studio
   Live, discussion context, Paused and Camera off before saving.
4. Restore session returned to Preview, with Camera off and a paused context
   change. Javier confirmed nothing opened automatically.
5. Bookmark review screenshot shows card 7/10, Save a discussion point, with one
   `Save a discussion point (discussion)` bookmark still listed.
6. One typed Advance Stage in Preview simulated, left discussion active and
   kept the camera off. The screenshot shows the simulation notice and Preview
   footer; the export records one simulated ADVANCE_STAGE in discussion.
7. Explicit Live selection and Apply and pause followed by Advance Stage moved
   to stage 6, Session review. Camera remained off; export records one applied
   ADVANCE_STAGE in discussion. This was navigation, not task completion.

## Restore progress

1. Previous stage returned from review to discussion. Javier paused and saved
   progress, preserving a summary export before restoration.
2. Restore progress screenshot shows Preview, discussion context, Camera off
   and paused after a Studio context change. Javier confirmed nothing opened
   automatically.
3. One typed Advance Stage left stage 5 active in Preview; the export records
   the additional simulated ADVANCE_STAGE in discussion.
4. Explicit Live selection and Apply and pause followed by Advance Stage moved
   to stage 6, Session review. Screenshot shows Manual LIVE ready and Camera off;
   export records the additional applied ADVANCE_STAGE in discussion.
5. Bookmark persistence was directly inspected after Restore session only;
   it was not separately inspected after Restore progress.

## Private summary reconciliation

Exports remain local and are not committed. Basenames below identify the
private evidence. All six have zero launch requests, failures, duplicate or
rejected events, recognition trials and acknowledged task completions.

| Export basename | Simulated | Applied | Scope |
| --- | ---: | ---: | --- |
| harbor-laptop-A-before-session-restore-2026-10-09.json | 17 | 5 | Original revision; four advances and one bookmark applied. |
| harbor-laptop-A-after-session-restore-2026-10-09.json | 1 | 0 | New summary revision after Restore session; one Preview test. |
| harbor-laptop-A-session-restore-live-recheck-2026-10-09.json | 1 | 1 | Includes the preceding Preview test plus explicit Live advance. |
| harbor-laptop-A-before-progress-restore-2026-10-09.json | 1 | 2 | Includes the preceding two events plus previous-stage navigation. |
| harbor-laptop-A-after-progress-restore-2026-10-09.json | 2 | 2 | Includes the preceding three events plus the progress-restore Preview test. |
| harbor-laptop-A-progress-restore-live-recheck-2026-10-09.json | 2 | 3 | Includes the preceding four events plus explicit Live advance. |

Restore session changed the summary revision. Restore progress retained the
same summary revision and cumulative earlier outcomes; it did not create a
disjoint summary segment. Preserve the before/after exports but do not add
their totals. The five later exports are successive overlapping snapshots.
Their shared event IDs and payloads match exactly, with no repeated event ID
inside an individual export. The disjoint original export plus final later
snapshot contain 17 + 2 = 19 simulated events and 5 + 3 = 8 applied events
(27 unique outcomes). No intermediate snapshot is added.

The two restore Preview tests and subsequent Live advances are distinct event
IDs in the same discussion context. Software parsing of the six supplied JSON
files confirmed counts agree with outcome statuses and overlapping payloads
are unchanged. This parsing is evidence reconciliation, not a native replay.

## Software checks on a1bb37a

Javier supplied screenshots and confirmation of these Windows results:

- Ruff: all checks passed.
- mypy: no issues in 100 source files.
- pytest: 900 passed, 2 skipped, 1 warning in 522.11 seconds.
  The warning concerned a duplicate collection.json ZIP entry in the
  duplicate-entry rejection test.
- Smoke test: exit code 0.

These are operator-supplied results, not an independent AI test run.

## Boundaries and remaining checks

- Both restores reset to Preview and camera-off/paused; manual stage actions
  simulated until explicit Live reactivation. Javier reported no automatic
  external opening for either restore.
- This run had no historical real launch requests and imported slots were
  unbound. It does not independently verify replay prevention after a real
  resource launch. Preserve earlier no-replay evidence with its source identity.
- No code defect was demonstrated or repaired.
- Remaining laptop-A target-association and active-capture shortcut Camera
  handoff/focus recovery cases were not run here. No gesture readiness claimed.
- Hau Jie operates laptop B; Javier coordinates and Deston retains acceptance.
  No laptop-B results, participant-kit check or fresh-install/offline/thirty-minute
  stability/shutdown evidence are added by this retest.

AI assistance guided the commands/UI steps and reconciled supplied evidence.
Javier operated Studio and supplied the actual observations.
