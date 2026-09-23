# GitHub setup

Created: 2026-09-23

Repository:

- URL: https://github.com/Chi944/gestureforge-ict304
- Visibility: Private
- Local remote: `origin` -> `https://github.com/Chi944/gestureforge-ict304.git`
- Local branch at setup time: `codex/assignment-prototype`

Milestones:

- Assignment prototype, milestone #1, due 2026-10-03
- Final project, milestone #2, due 2026-11-07

Project board:

- GestureForge Agile Board: https://github.com/users/Chi944/projects/1
- Template: GitHub Kanban
- Imported items: 9 open issues from `Chi944/gestureforge-ict304`
- Initial columns shown by GitHub: Backlog, Ready, In progress, In review, Done

Initial issues:

- #1 Set up prototype foundation and reproducible environment
- #2 Implement gesture collection, manifest, and feature pipeline
- #3 Train and compare kNN and SVM prototype classifiers
- #4 Build assignment desktop prototype with NEXT-only viewer control
- #5 Implement activation controller and assignment safety tests
- #6 Collect pilot validation evidence and package assignment release
- #7 Complete assignment report, traceability, and declaration support
- #8 Add final project enrolment, profiles, and full command workflow
- #9 Add final project deck loading, saved state, and evaluation package

Notes:

- GitHub connector issue creation returned 404 for this newly created private repository, so issues and the project board were created through the signed-in GitHub browser session.
- Do not claim GitHub peer review, CI, or project progress until the relevant commits, pushes, reviews, and checks actually happen.

## Tracking update, 2026-09-23

The initial implementation branch was pushed after local verification:

- Branch: `codex/assignment-prototype`
- Commit: `f3451ba`
- Commit message: `Build assignment prototype with guarded NEXT control and assessment evidence`
- GitHub Actions: `Assignment checks` run #1 completed successfully for commit `f3451ba`.

The agile board and issue bodies were updated to reflect the actual state of the prototype work without closing human-gated evidence:

| Issue | Board status | Current gate |
|---|---|---|
| #1 Set up prototype foundation and reproducible environment | Done | Keep post-push install/release evidence attached to release packaging. |
| #2 Implement gesture collection, manifest, and feature pipeline | Done | Consented local TRAIN, VALIDATION and negative collection completed; feature data stays off GitHub. |
| #3 Train and compare kNN and SVM prototype classifiers | In review | Real pilot comparison and limitations recorded in evidence/PILOT_RESULTS.md. |
| #4 Build assignment desktop prototype with NEXT-only viewer control | In review | Genuine NEXT actions verified; participant confirmed hold/rearm smoke behaviour. |
| #5 Implement activation controller and assignment safety tests | Done | Scoped controller and viewer safety tests passed locally. |
| #6 Collect pilot validation evidence and package assignment release | In progress | Pilot and live NEXT evidence complete; second-device installation and submission gates remain open. |
| #7 Complete assignment report, traceability, and declaration support | In progress | Final report wording, evidence reconciliation, and signed declaration remain open. |
| #8 Add final project enrolment, profiles, and full command workflow | Backlog | Reserved for the final project stage after assignment freeze. |
| #9 Add final project deck loading, saved state, and evaluation package | Backlog | Reserved for the final project stage after assignment freeze. |

No GitHub comments or messages were posted during the board update.

The table reflects the subsequent 23 September pilot update: project status fields were changed and verified in GitHub. Source commit `b5aea04` also passed [Assignment checks #4](https://github.com/Chi944/gestureforge-ict304/actions/runs/35832253894). Later commit checks are reported separately.
