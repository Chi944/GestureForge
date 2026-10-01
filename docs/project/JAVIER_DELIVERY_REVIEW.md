# Javier component delivery review

Reviewed 1 October 2026 by Deston's integration track using Codex. This is software acceptance for reusable components, not final task, Windows-device or end-to-end product acceptance.

## Source and accepted boundary

Source: `releases/GestureForge_Javier.zip` from Javier's published `codex/javier-shortcuts` commit `3237cae33d32a0347ac257f11a53ee2547d64bc4`. Its focused patch applies to current main. The delivered synthetic repository history and the ZIP itself are not merged. The source implementation is preserved with the integration corrections below; original Linux checks remain attributed in `docs/javier/software-checks.json`.

Accepted components: validated decks and bookmarks; atomic JSON storage; portable semantic workspaces; explicit runbooks/stage editor; a twelve-target local registry; a bounded dispatcher; measured session summaries; embeddable widgets; simulation-only review harness; and a manual Windows acceptance probe. The assignment launcher retains NEXT-only gesture behaviour. The Studio camera shell remains Preview/Rehearsal with no real desktop dispatch.

## Review corrections

| Finding | Correction and evidence |
|---|---|
| Readiness callbacks could change context before a viewer action or Camera launch | Recheck active state and the complete snapshot after callbacks; mocked regressions prove no side effects |
| Target edits could update memory before a failed save | Stage changes in a candidate registry, save first, then publish while retaining the registry object shared by the dispatcher; failed create/bind/delete preserve state |
| Closed Quick Actions widgets still received app focus events | Remove the event filter on close and reinstall on show; same-widget reopen regression |
| Known interpreter exclusion omitted PowerShell ISE | Add the executable name to the existing exclusion and test it; trusted executable selection is not a malware sandbox |
| Probe could close while its capture thread was still running | Ignore close until capture shutdown is acknowledged; fake-worker timeout/retry regression |
| A Windows adapter test hard-coded POSIX separators | Use the native Path representation in the assertion |

Windows/Python 3.11 verification: 325 tests pass, one symlink test skips because this host does not permit its fixture; Ruff, mypy, assignment/Studio smoke tests and synthetic classifier evaluation pass. Launch adapters in automated tests are mocked. The probe was not run against hardware. The common verification output is `docs/project/verification.json`.

## Remaining integration gates

- **Hau Jie:** deliver profile selection/lifecycle and revision-bound readiness plus GF-P28 starter feasibility data. Each person performs their own gestures; Hau Jie owns protocol and quality checks. Deston's new P01 two-session/UNKNOWN recording remains to be performed.
- **Javier:** run GF-P05 on Windows and later GF-P19 on both laptops. Demonstrate visible Calculator, Camera, permitted file/folder/HTTPS opening, camera release, focus pause, manual recovery and error paths. Use `docs/javier/WINDOWS_EVIDENCE.md`; do not replace these with unit tests.
- **Deston:** attach these components to the one Studio session after the readiness/profile contract is available, respecting pause/save failures, stage reset, empty bindings and local target revisions. Then run the six-stage scenario and live evaluation. No LIVE bypass is added to compensate for missing readiness.

Keep teammate branches separate and submit subsequent work through PRs. Component preparation moves Javier's relevant cards to In Progress, not Done. This preserves the original completed-task progress calculation.

The original delivery's PR/video drafts remain local. No private samples, reports, prompt logs or decision logs are included in this change.
