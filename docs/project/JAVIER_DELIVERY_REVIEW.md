# Javier component delivery review

Reviewed 1 October 2026 by Deston's integration track using Codex. That checkpoint established software acceptance for reusable components, not Windows-device or end-to-end product acceptance.

Current update, 2 October: GF-P05 is accepted from PR #18's supplied [laptop-A observations and repair rerun](../evidence/WINDOWS_RESULTS_2026-10-02.md). The rerun covers the corrected confirmation and missing-target/recovery evidence paths. Native observations remain attributed to Javier; integration review did not independently reproduce them. GF-P13/GF-P34 attachment and GF-P19's broader both-laptop evidence remain separate.

## Source and accepted boundary

Source: `releases/GestureForge_Javier.zip` from Javier's published `codex/javier-shortcuts` commit `3237cae33d32a0347ac257f11a53ee2547d64bc4`. Its focused patch applies to current main. The delivered synthetic repository history and the ZIP itself are not merged. The source implementation is preserved with the integration corrections below; original Linux checks remain attributed in `docs/evidence/component-delivery-checks.json`.

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

At the original review, Windows/Python 3.11 verification covered tests, Ruff, mypy, assignment/Studio smoke tests and synthetic classifier evaluation. Launch adapters in automated tests were mocked; the probe had not yet been run against hardware. Current repository verification is recorded in `docs/project/verification.json`; the later supplied native evidence is linked above.

## Remaining integration gates

- **Hau Jie:** profile selection/lifecycle is attached. Complete the real enrolment walkthrough and GF-P12's longer personal rehearsal with revision-bound results. Hau Jie owns protocol and quality checks; private participant measurements are not independently reproduced here. Do not ask Javier to recollect P03 unless Hau Jie requests repair data.
- **Javier:** prepare GF-P13/GF-P34's bounded dispatcher and Quick Actions integration contract and focused tests with Deston, using [COMPONENT_INTERFACES.md](COMPONENT_INTERFACES.md). GF-P05 is complete. Later GF-P19 verifies integrated target, focus, Camera and error/recovery behaviour on both laptops using the Windows launch procedure.
- **Deston:** the manual viewer, workspace/runbook, Profiles, Enrolment and Quick Actions are attached. Complete guarded dispatch integration; respect pause/save failures, stage reset, empty bindings and local target revisions. The short simulated readiness check does not enable LIVE or replace the longer personal rehearsal. The six-stage scenario and live evaluation remain separate gates.

Keep teammate branches separate and submit subsequent work through PRs. At the original review, component preparation alone left the relevant tasks In Progress. Current task acceptance and completed-task progress are recorded in [PROGRESS.md](PROGRESS.md).

The original delivery's PR/video drafts remain local. No private samples, reports, prompt logs or decision logs are included in this change.
