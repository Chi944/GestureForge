# GestureForge Studio progress snapshot

Date: 30 September 2026

This progress record uses the base-hour estimates in `TEAM_BACKLOG.csv`. It counts only implemented or reviewable work with repository evidence. Planned teammate work, Trello card creation, future consented data collection and unmerged branches are not counted as complete.

## Current build status

| Owner | Evidence counted | Earned / planned hours | Progress |
|---|---|---:|---:|
| Deston | Assignment baseline preserved; shared routing/controller contracts; Studio preview shell; fictional scenario/protocol; team handoff docs; local verification | 15 / 75 | 20% |
| Hau Jie | No recognition/profile project branch or PR present on remote yet | 0 / 75 | 0% |
| Javier | No shortcut/viewer/workspace project branch or PR present on remote yet | 0 / 73 | 0% |
| Team total | Published foundation only; feature work remains ahead | 15 / 223 | 7% |

## Verified foundation

- `gestureforge/contracts.py`, `gestureforge/controller.py` and `gestureforge/routing.py` define and test the shared routing boundary.
- `python -m gestureforge --studio --smoke-test` opens a simulation-only Studio shell. It does not yet dispatch desktop shortcuts or replace the assignment viewer.
- `docs/project/TEAM_GUIDE.md`, `HAU_JIE_HANDOFF.md` and `JAVIER_HANDOFF.md` give each member their first tasks and branch rules.
- `docs/project/DEMO_SCENARIO.md`, `assets/corporate_demo_deck.json` and `assets/corporate_reference.txt` provide the fictional corporate training scenario.

## Not complete yet

- Hau Jie's starter recogniser, personal profile lifecycle, guided enrolment, readiness scoring and final recognition evaluation.
- Javier's viewer bookmark/persistence extension, workspace/runbook storage, desktop shortcut dispatcher, Quick Actions and session summary.
- Deston's final integrated Studio workflow, held-out evaluation, stability run, guide/video/report/slides and release packaging.

Fresh local verification passed Ruff, mypy, 116 pytest tests, assignment GUI smoke, Studio GUI smoke and synthetic evaluation. GitHub Actions remains manual-only.
