# GestureForge Studio team implementation guide

Updated 13 October 2026 · Project deadline 7 November 2026

Deston has authorised project implementation. Build the approved Windows corporate training and demonstration product on the submitted assignment. The assignment ZIP is preserved separately. This guide assigns work; it does not claim that future features or participant tests are complete.

## Current deliveries — 13 October

Deston confirmed sending the private development handoff to Hau Jie. Hau Jie
can now audit the supplied files and return his diagnosis/settings; the existing
H1 audit packet, freeze review and final TEST remain separate deliveries.

**H2 collection update:** two complete development returns and one closed
TRAIN-only contribution have arrived. The newest macOS/Safari return has all
104 trials / 520 scheduled records (497 valid, 23 invalid); the user reports no
collection issues and confirms the supplied poses. Its starter independence and
break before VALIDATION still need confirmation. Its generic condition notes
cannot establish actual recording conditions. Do not ask for more recordings
before reviewing the existing data.

Baseline kNN and SVM (multiplier 2.0, margin 1.5) each scored 0.382 validation macro-F1 for the newest return;
all NEUTRAL trials were rejected and 10/40 negative sample predictions were
accepted commands. Hau Jie should diagnose these development results and propose
bounded settings, not claim a deployment pass. Keep both complete contributors
excluded from starter fitting/tuning if they are the intended independent
evaluation participants. The closed contribution remains 48 TRAIN trials / 240
usable samples with no recovery, further recording or TEST requested. Review
pose/provenance before pooling it. GPT can prepare inputs and configurations;
final TEST still waits for Deston's freeze and a reviewed acquisition route.

GF-P12's current personal LIVE protocol is now `gf-p12-v4`: three five-second
windows for each enrolled action pose plus NEUTRAL, followed by ten negative
windows. This 22-window pass can unlock normal personal LIVE use for the exact
current profile/model/hand/camera/behavior and authored context after saving,
event reconciliation and paused restoration. It is still not final performance
evaluation or native-device acceptance. Historical v1-v3 50-window results
remain old evidence and cannot grant v4 LIVE eligibility. Javier's previous P03
attempt remains failed evidence; his next check is a short PREVIOUS diagnostic
with the correct pose and intended-pose notes, then wrong-action diagnosis before
any fresh 22-window attempt.

Use a fresh Studio source ZIP only for teammates who run from ZIP. Git users
should pull/rebase from `main`; participant browser collection kits are separate.
Extract the new Studio ZIP into a fresh folder and keep old private profiles,
datasets and `.local` evidence outside the replacement folder unless the guide
explicitly tells you to import them.

Software verification passed 918 tests (one platform skip), Ruff, mypy and both
startup modes; the focused Practice/Live suite passed 153 checks. Follow the
Studio archive's matching local verification record for package checks. These
checks do not establish recognition on a participant's hand or native device
acceptance. No additional Trello/backlog task is Done from the protocol change.

Read the **Next delivery** table at the top of your individual brief first.
It supersedes older recording priorities. Return small, reviewable deliveries
as they become available instead of waiting for your entire lane to finish.

| Delivery | Execution | Deston's review / final gate |
|---|---|---|
| H1 / GF-P17 preparation | PR #27's aggregate audit is merged; Hau Jie sends the existing private `H1-20261008` packet, without repeating the search | Verify the actual permitted inputs, reports, hashes and provenance; aggregate review does not approve a deployment starter |
| H2 / GF-P17 → GF-P18 | Hau Jie audits the two complete development returns and the closed TRAIN-only contribution first, checks remaining eligibility facts, and prepares personal settings plus the starter baseline; untouched TEST follows the freeze | Freeze review before TEST; reproduce the paired comparison and accept results, including failed targets. This task does not depend on the GF-P20 live study or a successful deployment starter |
| J1 / GF-P19 | PR #28's restore retest and PR #29's Preview focus/Camera-off launch checks are merged; Javier completes remaining laptop-A native target/recovery and active-capture Camera cases | Preserve PR #24/#26/#28/#29 build boundaries. Active-capture handoff needs a genuine full readiness grant; historical real-launch restore/no-replay and laptop B remain unverified |
| H3 + J2 / GF-P19, GF-P23 | Hau Jie operates laptop B; Javier coordinates and consolidates the two-device matrix, fresh install, offline core and thirty-minute Studio/shutdown evidence | Review evidence and affected retests after GF-P21/GF-P22; no new second-device result is yet claimed |
| J3 / GF-P20 | Javier coordinates observer records, condition order, actual hold/negative/latency sessions and disjoint exports; Hau Jie supplies frozen recognition inputs | Deston analyses/replays measurements and accepts the integrated study after GF-P16/GF-P17. Unavailable standard mode is reported, never silently replaced |
| H4 + J4 / GF-P24, GF-P25 | Hau Jie drafts methods/limitations; Javier drafts the guide and demo storyboard now | Final results, guide-only/native release evidence and complete demo are still required before GF-P26/GF-P27 |

Original task owners, weights, dependencies and acceptance criteria stay fixed.
Delegation shifts execution, not accountability. GF-P17/GF-P24/GF-P25 are selected
for preparation now; their final dependencies do not prevent drafting or recruitment.
Private participant data, full exports, videos and Word deliverables go through
the team's existing private folder/archive, not Git/Trello. Do not update the private
prompt or decision logs as part of this handoff.

### Current manual and GPT-ready work

| Member | Manual / physical work | GPT-assisted work that can continue now |
|---|---|---|
| Deston | Development handoff sent; receive Hau Jie's diagnosis/settings and `H1-20261008`; resolve the newest contributor's unanswered independence/break facts, then review freeze before untouched TEST; later review actual demo/declaration evidence. No new recording is requested now. | Integrate reviewed PRs, verify/use corrected browser imports, maintain evidence and progress, prepare freeze/score/replay and a browser-compatible TEST route once inputs/protocol are reviewed. Keep Word logs and participant data private. |
| Hau Jie | Send the existing private `H1-20261008` packet; review eligibility/session facts for the two complete returns before planning TEST; no further collection from the closed TRAIN-only contributor. Operate laptop B for Javier's GF-P19/GF-P23 matrix. | Audit the new development results, diagnose rejected NEUTRAL versus pose/session differences, propose bounded settings and the paired configurations, use the closed contribution only as TRAIN development after provenance review, and draft GF-P24 methods/limitations on `codex/hau-jie-profiles`. |
| Javier | Complete remaining laptop-A trusted-app/association, failure/retry, real-launch restore/no-replay and active-capture Camera cases; coordinate laptop B and later observer sessions. Do not repeat PR #29's completed Preview focus/reconnect checks. | Consolidate per-device evidence, fix demonstrated viewer/shortcut/runbook defects, prepare GF-P25 guide/storyboard, and update summary/export handling on `codex/javier-shortcuts`. |

GPT or synthetic checks cannot claim participant consent, physical laptop behavior,
camera recovery, real app launches, final TEST independence or marker acceptance.

Hau Jie's 8 October first private handoff is the existing starter audit packet:
complete consented numeric manifests/NPZ sidecars, baseline and 48-candidate
reports, saved all-six-fold/fixed-case diagnostic, hashes, pose/session/source
details, the legacy standard vocabulary, Right hand and permission scope, or
exact missing-status notes. The matching PR on
`codex/hau-jie-profiles` contains only sanitized aggregate evidence; that audit
was merged in PR #27. The private packet still needs delivery and reproduction.
No newer starter recording is requested until D1 diagnoses a need.

Deston's next acceptance opportunity is GF-P18 (10 task-weight hours): the
reviewable frozen packet and actual paired results would take his accepted
total from 16/75 to 26/75 (34.7%) and the team from 115/223 to 125/223 (56.1%).
These are conditional totals, not current completion claims.


**5 October integration update:** GF-P10's approved-standard loader and six-action activation route are implemented with generated-fixture verification. No standard model is enabled: the recorded bounded comparison found no qualifying candidate and redistribution permission is unresolved. Personal LIVE still requires full Practice. PR #24 is merged as partial laptop-A evidence; Javier continues the missing native cases. PR #25 delivers GF-P12 selected-pose repair with Deston's shared-camera/Profile integration, explicit candidate create and rollback path; independent review accepts it against the original software criterion. Deston keeps final integration and release acceptance. See current PROGRESS.md; accepted completion is 51.6% (15/29 tasks).

GF-P16's standard path remains blocked wherever it depends on GF-P10. Personal
LIVE software and manual paths may continue through their separate gates.

**Device assignment, 5 October:** laptop A is Javier's Windows laptop and laptop B is Hau Jie's Windows laptop. Hau Jie operates laptop B; Javier coordinates and consolidates GF-P19 evidence; Deston reviews GF-P23 and final integration. Both use the same identified Studio build. No laptop-B test is yet recorded. Original task ownership and weights remain unchanged.

## Start here

Read this guide, your individual brief, `CONTRACTS.md`, then `PROJECT_PLAN.md`, `TEAM_BACKLOG.csv` and `PROGRESS.md` in this directory. The full plan is revision 4: contextual AI assistance is removed. There is no chatbot, LLM, provider account or API-key feature. kNN/SVM gesture recognition is the AI subsystem.

The kickoff pack includes the source baseline and Deston's tested routing foundation. It deliberately excludes participant datasets, downloaded model assets, environments, reports, prompt/decision logs and Git metadata. It is a build handoff, not a final release or a ready-trained starter model.

## Responsibilities and editing boundaries

| Member | Owns | Current next step | Reviewer |
|---|---|---|---|
| Deston | Product direction, shared contracts/controller/routing, `app.py`, `__main__.py`, screen design, integration, acceptance and release | GF-P12 software integration accepted; seven open integration/evaluation/release tasks still need real inputs, hardware or final deliverables, so Deston's task percentage is unchanged | Teammate review; Deston makes final release decision |
| Hau Jie | `collect.py`, `dataset.py`, `models.py`, `evaluate.py`; new profiles/enrolment/practice/starter modules and their tests | H1 private packet delivery; H2 independent data/freeze packet; H3 laptop-B checks; H4 methods draft, in [your brief](HAU_JIE_HANDOFF.md#next-delivery--assigned-7-october) | Deston |
| Javier | `viewer.py`; new workspace/runbook/shortcut modules and widgets, session summary, guide and video draft | J1 remaining target-association, failure/retry, historical real-launch restore/no-replay and active-capture Camera handoff cases; J2 device/release evidence; J3 observer-study coordination; J4 guide/storyboard, in [your brief](JAVIER_HANDOFF.md#next-delivery--assigned-7-october) | Deston |

Manual execution is delegated to Hau Jie and Javier in the priorities above;
each follows their own brief after syncing the reviewed software checkpoint.
Return a concise evidence summary with the source revision, actual device and
conditions, observed outcomes, private evidence references and unrun cases.
Keep raw participant data and private result files out of Git/Trello. Deston can
continue independent software and integration work while these checks run;
repeated long trials by Deston are not a prerequisite for either lane.

Teammates may use their own consented profiles and must identify whose data and
performance were measured. Their results cannot replace or be relabelled as
Deston's P01 personal-performance evidence. Existing P01 failures and gaps remain
attributed to P01. Delegation does not change original task owners, weights or
Done status; GF-P23 acceptance and final integration/release review remain with
Deston. The priority sequence in the briefs supersedes older repeat-run advice.

PR #10's vocabulary work, PR #13's evaluator and PR #14's reviewed [profile persistence component](PROFILE_PERSISTENCE_HANDOFF.md) are integrated. Hau Jie's [starter checkpoint](STARTER_EVALUATION_CHECKPOINT.md) reports the three-person collection and baseline comparison; neither classifier is ready for release. Preserve the baseline and private inputs, and request targeted repair collection only for a diagnosed defect. PR #16's [guided enrolment component](ENROLMENT_INTERFACE_PROPOSAL.md) is attached to the shared camera; GF-P07 is accepted from reviewed generated UI workflow evidence combined with attributed P02 physical observations. PR #17's [selector](PROFILE_SELECTOR_HANDOFF.md) is attached in Profiles with Guest/manual fallback. Its [diagnostic slice](STARTER_FAILURE_ANALYSIS.md) is accepted. PR #19's [bounded comparison](GF_P11_BOUNDED_COMPARISON.md) was reviewed and repaired for reproducibility and evidence consistency; its supplied no-qualifying result is unchanged and has not been independently rerun. PR #20's local camera pilot is partial personal-pilot evidence only: 2/8 accepted NEUTRAL validation trials and kNN/SVM macro-F1 0.7209 remain attributed to Hau Jie's private pilot, not a new independent evaluation. Existing model/rejection thresholds and neutral hold/rearm policy are not relaxed from that result. PR #25 completes GF-P12's selected-pose repair software: the Repair pose tab uses Deston's shared observation-only camera path, starts from the installed saved personal profile, routes the candidate through Profiles for explicit create/load, preserves rollback to the original profile and expires readiness. Independent review accepts GF-P12 against that original software criterion using the integrated generated workflow and eight host tests. Explicit LIVE still permits manual actions through one persistent dispatcher; personal LIVE gestures require the saved, reconciled full Practice gate and explicit activation; native acceptance remains separate. The six-activation check is preliminary only. A new Hau Jie observation reports open palm sometimes remains LATCHED and movement can recover it, but the supplied screenshot does not show Prediction; do not claim the root cause resolved. Deston's reviewed feedback fix keeps prediction/rejection/rearm guidance in the fixed footer and clears stale errors on fresh accepted packets; accepted NEUTRAL rearming passes software regression checks. The physical intermittent report still needs Hau Jie's trace and intended-pose notes. Javier's [4 October checkpoint](JAVIER_OCT4_CHECKPOINT.md) preserves the historical Linux run. GF-P05 is accepted from PR #18's supplied [laptop-A observations and repair rerun](../evidence/WINDOWS_RESULTS_2026-10-02.md). PR #29 adds bounded laptop-A GF-P19 evidence for isolated Preview focus pause/reconnect, Camera Preview simulation, native Camera after capture was already off and later Preview reacquisition; it does not close active-capture native Camera handoff, failure/retry, selected trusted `.exe`, missing association, historical real-launch restore/no-replay, laptop B or GF-P23. Teammates should sync main and reuse Deston's attachment: Hau Jie sends the existing private H1 packet for byte/provenance verification, then targeted own-profile physical repair only if diagnosed, while Javier preserves accepted GF-P13 dispatcher evidence and records GF-P19's remaining Windows cases; GF-P34 still depends on the GF-P10 standard entry integration. Use [TEAM_BACKLOG.csv](TEAM_BACKLOG.csv) for accepted task status and remaining evidence.

Do not rewrite another owner's files to make a demo work. Put a required shared-interface change on the relevant Trello card for Deston to resolve. Own your module's tests and explanations; Deston's final checks do not replace them. Use AI tools to implement and investigate, then read and understand the generated code and report actual assistance.

## Product boundaries everyone must preserve

- Standard starter gestures remain unavailable, with a visible reason and manual access. A future starter needs consented data, evaluation and its own acceptance; a personal Practice grant does not approve a starter.
- Personal profiles optionally enrol three action poses plus reserved NEUTRAL. Personalisation is not authentication. Reusing another person's profile is not guaranteed to work.
- Three gesture IDs map to named actions. Names/targets can change without retraining. Always show what each gesture currently does.
- Quick Actions works without a deck or runbook. Up to twelve locally configured app/file/folder/HTTPS shortcuts; three active gesture slots.
- Studio's manual viewer supports NEXT, PREVIOUS and idempotent BOOKMARK in explicit LIVE mode; Preview/Rehearsal simulate typed actions. Personal LIVE gestures require a current full-Practice grant and explicit activation; the assignment entry point retains NEXT-only gesture dispatch.
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

The current integration adds an embedded Practice tab from PR #21 alongside Profiles, Enrolment, Repair pose, an explicit mode selector, draft gesture mappings, workspace loading, Edit runbook, Runbook, Session summary, runbook session files and Quick Actions. Profiles supports explicit create/load/rename/delete and Guest/manual switching; successful installation stays paused in Preview, and busy profile work blocks competing setup operations. `--profile-store PATH` selects the store for both the tab and startup. Repair pose starts from the installed saved personal profile, disables Guest/ad-hoc sources, uses shared observation-only capture, opens candidate review in Profiles and supports explicit rollback by loading the original profile. Applying a mapping stops capture and requires neutral before gesture simulation resumes; those draft mappings are not persisted. Quick Actions saves its private target library and three slot choices locally; **Use Quick Actions** explicitly validates and activates them, while target edits pause and clear routing until reactivation. Typed action buttons and target tests simulate in Preview/Rehearsal. Explicit LIVE allows manual deck/stage actions without a recogniser and validated Windows launches; macOS reports external launches unsupported. Use `Window.configure_studio` as documented in `CONTRACTS.md` for context/mapping integration. **Start/retry readiness** runs a preliminary six-activation simulated check: two correct protected events per action, NEUTRAL between events and zero wrong activations. UNKNOWN does not complete a trial; **Finish readiness** fails an incomplete check. For personal models its short pass cannot enable LIVE. For a reviewed standard release the six-action check can grant session-local eligibility; no such release is currently supplied. The separate `gf-p12-v4` Practice protocol measures twenty-two five-second windows: three for each action pose and NEUTRAL, followed by ten negative/transition intervals. It uses the existing capture/controller/dispatcher and saves local per-trial evidence. Only a genuine full Practice pass completed in the current app session, saved and reconciled before paused restoration, can grant temporary personal LIVE eligibility. That grant never starts capture or actions; final acceptance remains Deston's responsibility. GF-P12 software is accepted, but physical repair, native Practice and later evaluation remain separate. Guest remains manual-only without a starter.

The personal LIVE grant is held only in memory. It requires a genuine active
full Practice attempt in the current app session: all 22 windows covered, all
3/3 trials correct for every pose including NEUTRAL, no wrong or repeated
activations and all ten negative windows correct. Saving, exact summary-event reconciliation
and restoration of the previous context paused must all succeed first. The
grant pins profile/model/hand/camera/behavior revision and exact authored
workspace, stage and Quick Actions maps. Behavior, mapping, target or camera
edits expire it even if changed back; restarting Studio, Guest and model reload
clear it. Historical/imported JSON, diagnostics and the short check cannot grant
it. Cosmetic renames, ordinary pause and existing stage/Quick Actions selection
retain eligibility, but every resume needs explicit Start and fresh NEUTRAL.
Historical/imported v1-v3 fifty-window results cannot grant a v4 pass.
LIVE selection and **Apply and pause** remain explicit. The grant does not mark
physical repair, participant evaluation or native Windows acceptance complete.

Use **Edit runbook** for authored stage edits and **Session summary** / **Export session results** for local measurement archives. Session summary also shows the latest saved Practice result as a separate historical review with window counts and exact event reconciliation; its full per-trial JSON stays separate. Use [WORKFLOW_COMPARISON.md](WORKFLOW_COMPARISON.md) for observer records and disjoint Harbor summary exports in the later M/S/P study. These exports are separate from Studio's explicit saved runbook navigation/session files; navigation position is not autosaved. Before deck/workspace replacement, session restore, restart or close would leave a non-empty summary behind, Studio archives it under ignored `.local/studio`; archive failure blocks the operation and keeps counts visible. Successful restore/restart starts a fresh review summary. Do not commit those archives.

Screen transitions use the same small rule set:

| Trigger | Required transition |
|---|---|
| Open Studio with no starter/personal model | Show Home and Setup with Start disabled, manual deck controls available and the message "No starter or personal recogniser loaded." |
| Select a saved profile or load a personal dataset | Pause camera, train/validate candidate off the UI thread, then either install the complete model/vocabulary and remain paused or keep the old selection with an error. |
| Request Preview start from Profiles | Require the currently loaded profile/model and Preview mode, finish busy work and camera release, then use the normal Start/NEUTRAL path. |
| Use Guest (manual only) | Pause and unload the recogniser without deleting saved profiles or datasets; preserve manual workspace state. Unavailable standard gestures remain disabled with a reason. |
| Finish the short personal readiness check | Show pass/fail/expired readiness and the reason; incomplete or wrong activation fails. A pass remains simulation-only and does not substitute for Practice's 22-window protocol. |
| Start personal Practice | Use the loaded recogniser and shared capture/controller in REHEARSAL; all would-be actions go through the persistent dispatcher as simulations. Preserve the previous context for paused restoration. |
| Complete qualifying full Practice | Save the terminal result, reconcile every simulated event and restore the previous context paused before issuing an in-memory personal LIVE grant. Never auto-select LIVE or start capture. |
| Stop Practice, leave its tab or lose focus | Stop capture and preserve local evidence; restore the prior context paused only after evidence is saved. Failed storage retains the result for retry and blocks replacement. No automatic resume or LIVE permission. |
| Explicitly select LIVE | Permit manual typed actions without a recogniser. Personal gesture capture requires the current full-Practice grant, Apply and pause, explicit Start and fresh NEUTRAL. Windows targets validate before a launch request; unsupported platforms report a reason. |
| View Quick Actions, Demo Studio or another content tab | Tab selection does not activate routing. Leaving active Enrolment or Practice first stops its capture and preserves its evidence. |
| Open Enrolment; request collection | Pause recognition. An explicit consented request opens observation-only capture after the old worker releases. A first matching observation enables trials; collection never installs a model. |
| Leave Enrolment, Pause or stop collection | Cancel collection and release capture; preserve partial-trial evidence. A failed save keeps the widget alive for retry and blocks close/model replacement. Never resume automatically. |
| Use Repair pose | Require the installed saved personal profile, diagnostic reason, explicit consent and one selected label. Collect through observation-only capture, route the candidate to Profiles for explicit create/load, and keep rollback to the original profile. |
| Explicit Use Quick Actions or runbook stage activation | Apply that context's complete one-to-three gesture/action map, clear pending holds, update the legend and require NEUTRAL on resume. An empty map is manual-only with routing paused. |
| Edit shortcut target, action slot, profile model or gesture mapping | Pause and permanently expire personal LIVE eligibility because the behavior or target changed, even if changed back. Cosmetic renames do not expire it. |
| Import workspace or restore saved state | Validate everything first; on success replace visible content and stay paused. Never launch apps, open files/URLs, replay events or mark tasks complete from loading. |
| Focus loss, Camera launch or capture fault | Pause, cancel pending events and require explicit resume. Camera launch also waits for capture release before Javier's adapter opens the Camera app. |

Builder widgets should emit the records named in `CONTRACTS.md` and leave these messages to the shell: current profile/model/context, current gesture meanings, readiness state, disabled-control reason, simulated versus real action, launch requested, launch failed, target unbound, workspace import failed and neutral required. Keep local module messages factual; do not claim hardware evidence or teammate acceptance from synthetic checks.

Keyboard and button controls remain usable when recognition fails. Use readable contrast, labelled inputs, visible focus, sensible tab order and actionable errors. A disabled control must explain what enables it. Do not display a target as completed merely because Windows accepted an open request.

## Development workflow

1. Use Windows with 64-bit Python 3.11. Extract the source from the kickoff pack and run `setup.cmd`; it installs the pinned dependencies and downloads the small landmark asset. Initial setup needs internet. Never copy someone else's virtual environment.
2. Run `.\.venv\Scripts\python.exe -m pytest -q` and `.\run.cmd --smoke-test`. Normal `.\run.cmd` opens the assignment UI. `.\run.cmd --studio` starts in Preview; explicit LIVE permits manual actions, while personal gestures require a current full-Practice grant, Apply, Start and fresh NEUTRAL.
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
