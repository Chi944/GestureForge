# GestureForge Studio team implementation guide

Updated 2 October 2026 Â· Project deadline 7 November 2026

Deston has authorised project implementation. Build the approved Windows corporate training and demonstration product on the submitted assignment. The assignment ZIP is preserved separately. This guide assigns work; it does not claim that future features or participant tests are complete.

## Start here

Read this guide, your individual brief, `CONTRACTS.md`, then `PROJECT_PLAN.md`, `TEAM_BACKLOG.csv` and `PROGRESS.md` in this directory. The full plan is revision 4: contextual AI assistance is removed. There is no chatbot, LLM, provider account or API-key feature. kNN/SVM gesture recognition is the AI subsystem.

The kickoff pack includes the source baseline and Deston's tested routing foundation. It deliberately excludes participant datasets, downloaded model assets, environments, reports, prompt/decision logs and Git metadata. It is a build handoff, not a final release or a ready-trained starter model.

## Responsibilities and editing boundaries

| Member | Owns | Current next step | Reviewer |
|---|---|---|---|
| Deston | Product direction, shared contracts/controller/routing, `app.py`, `__main__.py`, screen design, integration, acceptance and release | Verify explicit LIVE manual dispatch; integrate the longer personal readiness handoff before live gestures | Teammate review; Deston makes final release decision |
| Hau Jie | `collect.py`, `dataset.py`, `models.py`, `evaluate.py`; new profiles/enrolment/practice/starter modules and their tests | GF-P07 real enrolment walkthrough and GF-P12 longer personal rehearsal; preserve PR #19's supplied no-qualifying result | Deston |
| Javier | `viewer.py`; new workspace/runbook/shortcut modules and widgets, session summary, guide and video draft | Verify the attached GF-P13/GF-P34 manual dispatch path, then GF-P19 integrated Windows cases | Deston |

PR #10's vocabulary work, PR #13's evaluator and PR #14's reviewed [profile persistence component](PROFILE_PERSISTENCE_HANDOFF.md) are integrated. Hau Jie's [starter checkpoint](STARTER_EVALUATION_CHECKPOINT.md) reports the three-person collection and baseline comparison; neither classifier is ready for release. Preserve the baseline and private inputs, and request targeted repair collection only for a diagnosed defect. PR #16's [guided enrolment component](ENROLMENT_INTERFACE_PROPOSAL.md) is attached to the shared camera; the real recording walkthrough remains. PR #17's [selector](PROFILE_SELECTOR_HANDOFF.md) is attached in Profiles with Guest/manual fallback. Its [diagnostic slice](STARTER_FAILURE_ANALYSIS.md) is accepted. PR #19's [bounded comparison](GF_P11_BOUNDED_COMPARISON.md) was reviewed and repaired for reproducibility and evidence consistency; its supplied no-qualifying result is unchanged and has not been independently rerun. Explicit LIVE now permits manual actions through one persistent dispatcher; live gestures still require the longer personal readiness handoff. The six-activation check is preliminary only. Javier's [4 October checkpoint](JAVIER_OCT4_CHECKPOINT.md) preserves the historical Linux run. GF-P05 is accepted from PR #18's supplied [laptop-A observations and repair rerun](../evidence/WINDOWS_RESULTS_2026-10-02.md). Teammates should sync main and reuse Deston's attachment: Javier verifies that path for GF-P13/GF-P34, then records GF-P19's integrated Windows cases. Use [TEAM_BACKLOG.csv](TEAM_BACKLOG.csv) for accepted task status and remaining evidence.

Do not rewrite another owner's files to make a demo work. Put a required shared-interface change on the relevant Trello card for Deston to resolve. Own your module's tests and explanations; Deston's final checks do not replace them. Use AI tools to implement and investigate, then read and understand the generated code and report actual assistance.

## Product boundaries everyone must preserve

- Try standard gestures without collecting a profile first. A simulated readiness check precedes real gesture actions. A consented, evaluated starter dataset must be built; none is supplied in this handoff.
- Personal profiles optionally enrol three action poses plus reserved NEUTRAL. Personalisation is not authentication. Reusing another person's profile is not guaranteed to work.
- Three gesture IDs map to named actions. Names/targets can change without retraining. Always show what each gesture currently does.
- Quick Actions works without a deck or runbook. Up to twelve locally configured app/file/folder/HTTPS shortcuts; three active gesture slots.
- Studio's manual viewer supports NEXT, PREVIOUS and idempotent BOOKMARK in explicit LIVE mode; Preview/Rehearsal simulate typed actions. Live gestures remain blocked; the assignment entry point retains NEXT-only gesture dispatch.
- Optional runbooks contain up to twelve ordered stages, instructions/card reference and up to three single actions. No scripts, loops, chained macros or automatic external launch when entering a stage.
- Preview/enrolment/rehearsal cannot dispatch real actions. Changing a profile/model/workspace/mapping invalidates old work. Stage changes clear a hold and require NEUTRAL. Focus loss pauses; returning requires explicit resume.
- Local core features work offline after setup. Websites and external apps' own online features may require internet. No direct PowerPoint integration is promised.
- Workspace exports contain semantic shortcut slots, never personal samples, local target paths, URL bindings or credentials. Each recipient explicitly binds/tests local targets.

## Initial screen design

Deston owns the shell; teammates provide embeddable PySide6 widgets instead of separate applications. Existing webcam capture remains one worker with one latest-result mailbox. No second camera worker in an enrolment widget.

| Screen | Main content | Persistent or critical controls |
|---|---|---|
| Home and Setup | Try standard gestures; choose/create personal profile; selected hand and camera status | Manual access always available; honest missing-starter/error messages |
| Personalise and Practice | Guided pose collection, progress, rejection guidance and simulated test results | Clearly marked simulation; no OS launch; explicit collect/retrain controls |
| Quick Actions | Three large gesture-to-target tiles; target library editor; local target test button | Current profile/context legend, Start/Pause, unbound targets disabled |
| Demo Studio | Card title/body and distinctive card transition, ordered stages/instructions and bookmarks | Current stage and gesture meanings; manual Next/Previous/Bookmark/Continue; pause |
| Session Review | Correct/wrong/missed trials, would-be actions, retries and acknowledged task completion | Export results; distinguish simulated events from real launch requests |

The current Studio shell includes Profiles, Enrolment, an explicit mode selector, draft gesture mappings, workspace loading, Edit runbook, Runbook, Session summary, runbook session files and Quick Actions. Profiles supports explicit create/load/rename/delete and Guest/manual switching; successful installation stays paused in Preview, and busy profile work blocks competing setup operations. `--profile-store PATH` selects the store for both the tab and startup. Applying a mapping stops capture and requires neutral before gesture simulation resumes; those draft mappings are not persisted. Quick Actions saves its private target library and three slot choices locally; **Use Quick Actions** explicitly validates and activates them, while target edits pause and clear routing until reactivation. Typed action buttons and target tests simulate in Preview/Rehearsal. Explicit LIVE allows manual deck/stage actions without a recogniser and validated Windows launches; macOS reports external launches unsupported. Use `Window.configure_studio` as documented in `CONTRACTS.md` for context/mapping integration. **Start/retry readiness** runs a preliminary six-activation simulated check: two correct protected events per action, NEUTRAL between events and zero wrong activations. UNKNOWN does not complete a trial; **Finish readiness** fails an incomplete check. Its session-local, behaviour-version-bound pass does not enable live gestures. Hau Jie's longer personal protocol and readiness handoff are required for that gate. Guest remains manual-only without a starter.

Use **Edit runbook** for authored stage edits and **Session summary** / **Export session results** for local measurement archives. These exports are separate from Studio's explicit saved runbook navigation/session files; navigation position is not autosaved. Before deck/workspace replacement, session restore, restart or close would leave a non-empty summary behind, Studio archives it under ignored `.local/studio`; archive failure blocks the operation and keeps counts visible. Successful restore/restart starts a fresh review summary. Do not commit those archives.

Screen transitions use the same small rule set:

| Trigger | Required transition |
|---|---|
| Open Studio with no starter/personal model | Show Home and Setup with Start disabled, manual deck controls available and the message "No starter or personal recogniser loaded." |
| Select a saved profile or load a personal dataset | Pause camera, train/validate candidate off the UI thread, then either install the complete model/vocabulary and remain paused or keep the old selection with an error. |
| Request Preview start from Profiles | Require the currently loaded profile/model and Preview mode, finish busy work and camera release, then use the normal Start/NEUTRAL path. |
| Use Guest (manual only) | Pause and unload the recogniser without deleting saved profiles or datasets; preserve manual workspace state. Unavailable standard gestures remain disabled with a reason. |
| Finish the short personal readiness check | Show pass/fail/expired readiness and the reason; incomplete or wrong activation fails. A pass remains simulation-only. Standard-gesture checks and the longer personal rehearsal remain separate work. |
| Explicitly select LIVE | Permit manual typed actions without a recogniser; keep gesture capture/dispatch blocked pending full personal readiness. Windows targets validate before a launch request; unsupported platforms report a reason. |
| View Quick Actions, Demo Studio or another content tab | Change the visible view only; tab selection does not activate routing. |
| Open Enrolment; request collection | Pause recognition. An explicit consented request opens observation-only capture after the old worker releases. A first matching observation enables trials; collection never installs a model. |
| Leave Enrolment, Pause or stop collection | Cancel collection and release capture; preserve partial-trial evidence. A failed save keeps the widget alive for retry and blocks close/model replacement. Never resume automatically. |
| Explicit Use Quick Actions or runbook stage activation | Apply that context's complete one-to-three gesture/action map, clear pending holds, update the legend and require NEUTRAL on resume. An empty map is manual-only with routing paused. |
| Edit shortcut target, action slot, profile model or gesture mapping | Pause and expire readiness because the behaviour revision changed. Cosmetic label edits do not expire readiness. |
| Import workspace or restore saved state | Validate everything first; on success replace visible content and stay paused. Never launch apps, open files/URLs, replay events or mark tasks complete from loading. |
| Focus loss, Camera launch or capture fault | Pause, cancel pending events and require explicit resume. Camera launch also waits for capture release before Javier's adapter opens the Camera app. |

Builder widgets should emit the records named in `CONTRACTS.md` and leave these messages to the shell: current profile/model/context, current gesture meanings, readiness state, disabled-control reason, simulated versus real action, launch requested, launch failed, target unbound, workspace import failed and neutral required. Keep local module messages factual; do not claim hardware evidence or teammate acceptance from synthetic checks.

Keyboard and button controls remain usable when recognition fails. Use readable contrast, labelled inputs, visible focus, sensible tab order and actionable errors. A disabled control must explain what enables it. Do not display a target as completed merely because Windows accepted an open request.

## Development workflow

1. Use Windows with 64-bit Python 3.11. Extract the source from the kickoff pack and run `setup.cmd`; it installs the pinned dependencies and downloads the small landmark asset. Initial setup needs internet. Never copy someone else's virtual environment.
2. Run `.\.venv\Scripts\python.exe -m pytest -q` and `.\run.cmd --smoke-test`. Normal `.\run.cmd` opens the assignment UI. `.\run.cmd --studio` starts in Preview; explicit LIVE permits manual actions, while live gestures remain blocked.
3. For Git collaboration, clone `https://github.com/Chi944/GestureForge_304.git`, fetch `origin`, and create your own branch from the published `origin/main`. The shared foundation is now supplied through Git. Do not apply an old kickoff patch on top of the published foundation. If you already have local work based on the old pack, preserve it on your branch and ask Deston to review the diff before rebasing or merging. A ZIP extraction is an alternative read/run workspace, not a substitute for Git history.
4. **Commit and push only to your own branch: Hau Jie uses `codex/hau-jie-profiles`; Javier uses `codex/javier-shortcuts`. Never commit, push, force-push or merge directly to `main`, and never push to another teammate's branch.** Create your branch before editing. Shared starting work is not your authorship.
5. Limit each change to your owned modules and related tests. Push your branch, then open a PR **from your branch into `main` for Deston's review; leave it unmerged**. Include the Trello ID, files, commands/results, screenshot or short recording where useful, and known limits. Only Deston integrates approved changes into `main`. If GitHub access is not available, send the patch to Deston with the exact base commit.
6. Run targeted tests while developing. Before handoff run Ruff, mypy and the complete pytest suite using the commands below. GitHub Actions remains manual; do not depend on Actions credit for testing.

```powershell
.\.venv\Scripts\python.exe -m ruff check gestureforge tests scripts
.\.venv\Scripts\python.exe -m mypy gestureforge scripts tests
.\.venv\Scripts\python.exe -m pytest -q
.\run.cmd --smoke-test
```

Keep numeric samples in `data/local/`, private experiments in `experiments/local/` and temporary work under `.local/`. No pickled model import, secrets, raw webcam recordings, `.venv`, local Word reports/logs or bulky generated checklists in a PR.

## Board and completion rules

Board: https://trello.com/b/wDb978u6/gestureforge-assignment-and-project

Project cards use `GF-Pxx | Owner | Task`. Owner text identifies the responsible person; it does not claim a Trello member-account assignment or that they have received this pack. Earlier assignment cards are retained as history. New project cards replace the earlier, narrower project backlog.

Backlog means planned; To Do means ready to start; In Progress means actual work started; Review-Test means implementation/evidence awaits review; Done requires evidence and acceptance. Put missing data, hardware or cross-module dependencies in Blocked when they genuinely prevent progress. Never mark a task done because an AI tool says it is finished. Dependencies are completion gates; independent probes and contract tests may start earlier.

Each review must include: requirement/task IDs; what works; exact tests and results; invalid-input/recovery cases; whether hardware checks were run; no-data/no-model startup; and instructions another teammate can follow. Failed targets remain visible. Do not tune using the final held-out test set.

## Milestones and delivery evidence

| Dates | Gate |
|---|---|
| 30 Sepâ€“4 Oct | Shared foundation, [starter evaluation checkpoint](STARTER_EVALUATION_CHECKPOINT.md), GF-P06 profile selection/readiness, Windows launch probes, capacity and participant recruitment |
| 5â€“11 Oct | Profiles/enrolment, viewer/workspaces and first integration |
| 12â€“18 Oct | Shortcuts, runbooks, rehearsal and summaries integrated; feature freeze |
| 19â€“25 Oct | Frozen-data evaluation, system tasks and replay |
| 26 Octâ€“1 Nov | Defects, independent Windows installation and stability; release candidate |
| 2â€“6 Nov | Report, guide, video, slides, actual contribution declaration and presentation rehearsal |
| 7 Nov | Deadline buffer |

Base estimates: Deston 75h, Hau Jie 75h, Javier 73h; reserve about 20% contingency. These are estimates, not verified availability. Hau Jie owns methods/results sections; Javier owns user-guide/video drafts; Deston integrates the report, rubric/test matrix and ten-minute presentation. Every member must explain their own work. Register/report the new three-person team using actual identities and contributions; do not reuse the assignment's two-person split.

No participant performance, commercial demand, universal accessibility or world-first novelty is claimed. The final project needs measured recognition, complete subsystem testing, a working demo/video and clear operating limits. Existing reports and prompt/decision logs are not edited by this kickoff.
