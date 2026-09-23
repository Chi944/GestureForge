# GestureForge Agile Working Method

Status: active local backlog and live GitHub issue/project tracking.

## Agile Setup

Use short, evidence-focused sprints. Detailed acceptance work is tracked in `docs/backlog.csv`; nine parent issues group that work on the GitHub project board.

Recommended columns:

- Backlog
- Ready
- In progress
- Review
- Done
- Blocked

Every issue should have:

- Sprint ID.
- Release target.
- Acceptance criteria.
- Evidence path.
- Actual status.

The local board generator is:

```powershell
python scripts\board.py
```

It writes `docs/SPRINT_BOARD.html` from `docs/backlog.csv`. Evidence-based status updates use:

```powershell
python scripts\board.py --id GF-A1-002 --status "Done" --note "Evidence path or command result summary"
```

Those updates append records to `docs/sprint_events.jsonl`. The root implementation lane owns backlog status changes after this documentation pass.

## Sprint Cadence

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

## GitHub Status

The private [repository](https://github.com/Chi944/gestureforge-ict304), [nine issues](https://github.com/Chi944/gestureforge-ict304/issues), two dated milestones, and [GestureForge Agile Board](https://github.com/users/Chi944/projects/1) were created on 23 September 2026. See `GITHUB_SETUP.md` for the setup record. Keep GitHub parent issues aligned with the detailed local backlog; a parent remains open until all acceptance evidence exists. Creating these tools is not evidence of human peer review or weekly tutor meetings.

## Status Rules

- `Not started`: no implementation work yet.
- `In progress`: active code or documentation work exists.
- `Blocked`: needs human consent, tutor input, hardware, or credentials.
- `Review`: implementation exists and needs checking.
- `Done`: evidence exists and is referenced.

Do not use `Done` for planned work without evidence.
