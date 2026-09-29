# GestureForge Agile Working Method

Status: assignment submitted; three-member project development in progress.

## Agile Setup

Use short, evidence-focused sprints. Current project acceptance work is tracked in [project/TEAM_BACKLOG.csv](project/TEAM_BACKLOG.csv), with evidence and percentages in [project/PROGRESS.md](project/PROGRESS.md). The live Kanban board is <https://trello.com/b/wDb978u6/gestureforge-assignment-and-project>. `docs/backlog.csv` remains the historical assignment snapshot.

Trello columns:

- Backlog
- To Do
- In Progress
- Review-Test
- Blocked
- Done

Every issue should have:

- Sprint ID.
- Release target.
- Acceptance criteria.
- Evidence path.
- Actual status.

`docs/backlog.csv` is the submission snapshot. `docs/sprint_events.jsonl` records factual status changes made during development. The archived local HTML board and generator are no longer part of the submitted repo.

## Planned Sprint Cadence

| Sprint | Dates | Goal |
| --- | --- | --- |
| A1 | 23-24 Sep | Confirm scope, repo layout, dependencies, camera feasibility |
| A2 | 25-26 Sep | Collect pilot data and produce first classifier results |
| A3 | 27-28 Sep | Connect prediction to viewer NEXT through controller |
| A4 | 29-30 Sep | Tune rejection, run targeted tests, produce measured outputs |
| A5 | 1-3 Oct | Freeze, package, report, second-machine check, submit |
| P1 | 4-11 Oct | Add enrolment, practice, and profile lifecycle |
| P2 | 12-18 Oct | Add all commands, custom decks, saved state, feature freeze |
| P3 | 19-25 Oct | Freeze config and run held-out evaluation |
| P4 | 26 Oct-1 Nov | Fix defects, release candidate, stability and second-machine checks |
| P5 | 2-7 Nov | Final report, guide, video, slides, submission verification |

## Definition of Ready

An issue is ready when:

- The release target is clear.
- Acceptance criteria are testable.
- Required files or modules are known.
- Human gates are identified.
- The issue will not expand assignment scope into final-project scope.

## Definition of Done

An issue is done when:

- Code or document changes are committed or staged for review.
- Relevant tests or checks have fresh evidence.
- Claims in the report and guide match the implemented system.
- Any limitation is recorded.
- No fake measurements, approvals, participants, signatures, or tool usage are present.

## Review Gates

| Gate | Date target | Review question |
| --- | --- | --- |
| Assignment feasibility | 24 Sep | Can the camera, dependencies, and landmark path work? |
| Assignment integration | 28 Sep | Does a live gesture cause exactly one NEXT action? |
| Assignment freeze | 1 Oct | Do code, report, results, and guide say the same thing? |
| Final feature freeze | 18 Oct | Are all final features implemented before evaluation? |
| Final release candidate | 1 Nov | Can another machine run the package from instructions? |
| Final submission | 7 Nov | Are all required artifacts uploaded and downloaded for verification? |

## Board Status

GitHub: <https://github.com/Chi944/GestureForge_304>. Trello sprint board, created on 28 September 2026: <https://trello.com/b/wDb978u6/gestureforge-assignment-and-project>.

The board retains assignment history and 29 project cards split between Deston, Hau Jie and Javier. Each project card names its owner, dependencies, deadline and acceptance criteria. Branch rules and editing boundaries are in [project/TEAM_GUIDE.md](project/TEAM_GUIDE.md): each builder pushes only to their own branch and requests Deston's review; only Deston merges into `main`. Tool setup does not establish completed teammate work or tutor review.

## Status Rules

- `Backlog`: planned work not yet selected; `To Do`: selected and ready to start.
- `In Progress`: active code or documentation work exists.
- `Blocked`: needs human consent, tutor input, hardware, or credentials.
- `Review-Test`: implementation exists and needs final checking or human acceptance.
- `Done`: evidence exists and is referenced.

Do not use `Done` for planned work without evidence.
