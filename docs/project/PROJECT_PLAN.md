# GestureForge Studio approved project build plan

Revision 4 - 30 September 2026. Submission target: 7 November 2026.
Status: user authorised local implementation and Trello kickoff on 30 September 2026. The user subsequently authorised committing and pushing all current project changes and merging reviewed PRs.
This approval version removes contextual AI assistance at the user's request: no chat/question-answering, prompt templates, note retrieval, hosted provider, API-key setup or answer-generation evaluation. Requirements R09, R10, R17 and R18 are retired; the other IDs remain stable. Gesture recognition remains the AI subsystem. Proposed capabilities are not claims of completed implementation or achieved results. The submitted assignment remains preserved. Current implementation progress is recorded in docs/project/TEAM_BACKLOG.csv and docs/project/PROGRESS.md.

## 1. Product and scope correction

**GestureForge Studio is a gesture-controlled training and demonstration workspace: start with standard gestures, personalise when needed, build a guided demo, and control approved desktop resources through deliberate gestures.**

The earlier scope made every user enrol gestures and treated most capability as isolated shortcuts. This revision adds depth through a complete presenter workflow, optional personalisation and measurable AI behaviour. Overlap with existing products is acceptable; practical value, justified design and verified execution matter more than a worldwide novelty claim.

Commercial scenario: a corporate software trainer prepares a reusable product walkthrough. A colleague opens it, checks camera framing, tries the standard gestures, follows the demo stages, uses desktop shortcuts for demonstration resources, bookmarks discussion points and resumes saved procedures. After rehearsal, the trainer sees missed gestures, retries and incomplete stages. No enterprise cloud platform is required.

One polished supplied scenario is mandatory: a fictional software-product onboarding session with a ten-card deck, six demo stages, Calculator as a demo tool, a local TXT/PDF reference and resource-folder shortcut, an optional HTTPS help link and clear authored instructions. Camera is a separate device-handoff example. All example claims and data must be explicitly fictional or properly sourced.

## 2. What the assessment actually rewards

Sources re-read: `ICT304_Assignment_Project_TS_2026.pdf` (all seven pages) and `Project Feedback Sheet.docx`.

- Page 2: build a fully functioning AI system rather than only a model; explain its place in a workflow; investigate at least two techniques; use the System Engineering Product Life Cycle and report project management/version control/collaboration/communication tools.
- Page 4: extend the same AI system as the assignment. A change of system needs coordinator approval at least four weeks before the deadline. For 7 November, that boundary is 10 October. Discuss this extension promptly; tutor feedback encouraging expansion does not automatically establish approval of this detailed scope.
- Page 4 explicitly says results need not exceed those in literature/websites. The team must understand and justify the steps, measurements, acceptability and limitations.
- Pages 5-6: whole-system design and subsystem interfaces; algorithm steps, preprocessing and parameter justification; reproducible code/data; evaluation/discussion; deployment/integration/maintenance; user/developer guide; demo video; ten-minute presentation; references and assistance prompts.
- Page 7: actual member contributions and group declaration; mandatory tool reporting; runnable code/demo.

| Final feedback criterion | Weight | How the revised scope earns evidence |
|---|---:|---|
| Requirement and report focus | 20% | Named trainer problem, two user journeys, bounded conditions, numbered requirements, acceptance tests and realistic commercial scenario |
| System design | 35% | Starter/personal recognition, session engine, local launch control, rehearsal and recovery, explicit interfaces, alternatives and lifecycle decisions |
| Evaluation and results | 20% | kNN/SVM comparison; unseen-person starter evaluation; personalisation benefit; rejection/controller comparisons; subsystem/recovery tests and workflow comparison |
| User guide and code/model | 15% | Immediate starter experience, clear optional enrolment, install guide, reproducible data/configurations, screenshots and readable source |
| Content and format | 10% | Clear report, figures, references, explained limitations and consistent evidence |

Creativity is explicit in the assignment rubric and the final report's abstract/product discussion. The final feedback sheet does not assign it a separate percentage. Adding unrelated features does not substitute for the 35% design and 20% evaluation requirements. No grade or highest-band outcome can be guaranteed.

The feedback sheet identifies deductions for missing video (20%), incomplete subsystem evaluation (15%) and unmet project-sheet requirements (10%). The brief also states consequences for missing declaration/tool reporting and non-working code/demo. These are reasons to reserve verification and documentation time, not to add more features.

## 3. New users, profiles and sharing

### Immediate start

A new user chooses **Try standard gestures**. No account, custom-pose collection or saved personal profile is required. A compact starter recognition model is shipped using the same MediaPipe features and kNN/SVM machinery, trained on explicitly consented multi-person examples of three standard poses plus NEUTRAL. The existing small landmark asset remains; no large local language model is introduced.

A short framing/neutral/action check runs in a simulated preview before real gestures are enabled. This is a readiness check, not training. Target first successful standard action within two minutes after camera setup; measure it rather than claim it achieved. Manual controls work immediately. The user sees the actual startup failure reason and can choose personal training if the starter struggles.

Starter recognition is an engineering deliverable requiring unseen-person tests, not a promise it will work perfectly for every hand, posture or room. Initially support the right hand, matching the current validated collection convention. Offer left-hand personal enrolment through the existing hand-selection contract; do not claim a general left-hand starter until separately tested. State this visibly rather than silently rejecting a left hand.

### Optional personal profile

Choose **Personalise** to use different poses or improve recognition. Guided collection creates a private model for three action poses plus reserved NEUTRAL, along with preferences and bindings. Rehearsal identifies confusing poses and offers targeted recollection. No silent online learning: explicitly reviewed samples and retraining produce a new version that can be reverted.

A returning user selects their saved profile and resumes; they do not repeat full enrolment each launch. A quick check is offered after a camera/lighting change. Switching to another user's personalised model is allowed as an explicit choice but is not recommended as a guaranteed shared model.

### Direct answer about profile transfer

A personalised model does not authenticate the owner. Another person making similar poses may be recognised, may be rejected, or may be confused with another class. The software cannot know that the hand belongs to the profile owner from these gesture features. Therefore personal profiles are neither identity controls nor reliable universal gesture packs.

Keep these separate:

| Object | Contains | Sharing rule |
|---|---|---|
| Starter recogniser | Standard gesture definitions and consented multi-person numeric examples/configuration | Bundled after redistribution permission and evaluation |
| Personal profile | Gesture samples/model settings, selected hand, names and preferences | Local by default; never silently exported with company material |
| Company workspace | Deck, runbook stages, authored instructions and named action slots | Shareable JSON pack; each computer binds its local apps |
| Runtime session | Current stage, bookmarks, outcomes and chosen model revision | Local; pause on switching profile or workspace |

Names and app preferences can be customised without retraining standard gestures. Personal model quality and content portability are separate concerns.

## 4. Creative, commercially coherent core

### A. Demo Studio: editable guided demonstrations

Use a simple workspace with Quick Actions, a deck view and an optional guided session. Quick Actions works without a deck or runbook. A simple form/list editor creates up to twelve ordered stages. Each stage contains an instruction/card reference and up to three named action slots. The three gestures are mapped explicitly to those slots for that stage; a persistent on-screen legend shows their meanings.

Permitted single actions: next/previous card, bookmark card, advance runbook stage, or invoke an approved desktop shortcut. A gesture invokes one typed action. No loops, user code or arbitrary multi-action macros. Activating a stage can display its linked card/instruction, but cannot automatically launch applications or other external targets.

Example stage: show the pricing card; G1 advances to the next stage, G2 opens Calculator, G3 bookmarks the card for later discussion. All stage controls also have buttons. Previous-stage navigation is always available by button. The editor rejects a stage without a visible path to continue/finish.

Stage changes cancel pending holds and require neutral rearming. Completion is recorded from actual outcomes or explicit user acknowledgement; merely opening an app does not prove the product task was completed. Failed launches leave the stage active. Bookmarks remain idempotent and saved, with a review list and explicit removal.

This is a bounded demo authoring tool built around the existing viewer, not a general desktop automation engine.

### B. Rehearsal and session review

Run the actual recognition/controller/mapping path against a recording dispatcher. Personal readiness uses ten trials per pose and ten five-second negative/transition intervals; proposed pass criteria are at least nine correct trials per pose and zero would-be negative actions. The shorter guest check requires two correct simulated activations of each standard action, successful neutral rearming between them, and zero incorrect would-be actions; UNKNOWN-only output cannot pass; failed checks offer another attempt, personal enrolment or manual control. Count actions that would have fired, including accidental ones, without opening apps. Show recognition misses, false triggers, duplicate events, stage retries and task completion. Use deterministic guidance based on measured issues, such as a frequently confused pose or repeated loss of hand tracking; do not invent a diagnosis about the user's body.

The session summary makes the product useful for training preparation and provides evaluation evidence. Keep it small: one summary view and exportable numeric/event results, not a separate analytics platform.

### C. Customisation that remains usable

Users customise gesture poses, stage bindings, local shortcut slots, deck content and authored stage instructions. Start from a complete supplied workspace instead of an empty editor. Keep three trained action poses plus NEUTRAL; depth comes from what people can build and accomplish, not from collecting a large gesture vocabulary.

### D. Desktop shortcuts: explicitly in scope

Desktop app launching was already R08. R21 adds a usable standalone Quick Actions panel and broadens the approved targets through the same dispatcher, rather than building a second automation system.

| Target type | Included behaviour | Boundary |
|---|---|---|
| Application | Calculator, Camera or a user-selected installed local application | Open only; no arbitrary arguments, scripts, simulated typing or control of its internal UI |
| Reference file | Open a selected PDF, TXT, PNG or JPEG in the registered application | Existing local file; no execution-capable formats, `.lnk` or `.url`; show missing association errors |
| Folder | Open a selected local resource folder in File Explorer | Existing folder; no file modification, deletion or network-share access |
| Website | Open an explicitly configured HTTPS page in the default browser | No custom protocol, embedded credentials or browser automation; page availability depends on internet/site |

A local shortcut library holds up to twelve named targets. Bind three of them to the three gesture slots in Quick Actions; a stage can bind its own slots to library targets. No need to enrol new gestures when changing a target. Show the active bindings continuously. Switching Quick Actions/deck/stage clears the pending gesture and requires NEUTRAL.

Before enabling a binding, show its resolved target and allow a button-based test. Imported workspace packs contain only semantic slot names such as 'Product reference'; each machine must bind and test its own targets, including URLs. Do not silently export local paths, query-string secrets or user-specific settings.

Opening another application/browser/folder normally changes focus: GestureForge pauses and requires explicit resume after returning. This release does not provide global background gesture commands or control applications after opening them. Camera additionally releases capture before launch. A successful Windows open request is logged as 'launch requested', not proof that the application loaded correctly or that the user completed a task. Real-device tests verify visible results.

Use native Windows opening facilities without shell-built command strings; Python's [os.startfile documentation](https://docs.python.org/3.11/library/os.html#os.startfile) describes registered-application opening and its lack of application completion status. Resolve and validate target type immediately before every launch, not just when the shortcut is created.

## 5. Numbered requirements and acceptance evidence

| ID | Requirement | Acceptance evidence | Owner |
|---|---|---|---|
| R01 | Local profile create/rename/load/delete and atomic save | Two independent profiles round-trip; corrupt data rejected; prior data preserved | Hau Jie |
| R02 | Guided optional enrolment of three custom poses plus NEUTRAL | No CLI needed; collector saves valid/invalid trials; no real actions during enrolment | Hau Jie |
| R03 | Train-only feature/scaling/rejection policy; kNN/SVM comparison | Reproducible splits/configurations; UNKNOWN counts as miss; legacy assignment data imports | Hau Jie |
| R04 | Rehearsal and readiness tied to behaviour revision | Real controller with simulated dispatch; negative would-be actions measured; changed settings invalidate result | Hau Jie |
| R05 | NEXT/PREVIOUS/BOOKMARK, custom deck, saved position/bookmarks | Boundaries do not wrap; bookmarks idempotent; reload restores state | Javier |
| R06 | Workspace import/export with content and runbook | Valid round-trip; malformed/version-incompatible input leaves current workspace intact | Javier |
| R07 | Deck/session context with persistent gesture legend | Stage changes and context switching invalidate old actions; no hidden automatic mode changes | Deston |
| R08 | Calculator, Camera and locally selected app bindings | Actual Windows launches; unavailable app errors; clean Camera handoff; no shell/arguments | Javier |
| R11 | Hold/rearm, pause/recovery and global exactly-once dispatch | Long holds, stale IDs, stage/model/profile changes and failed callbacks cannot duplicate actions | Deston |
| R12 | Atomic private storage and portable semantic app slots | No samples/keys/executable paths in exported workspace; local rebinding required | Javier |
| R13 | Accessible status, manual fallback and clear card changes | Profile/model/context visible; readable card titles and action feedback; keyboard controls | Deston |
| R14 | Complete release and assessment evidence | Two Windows installs, offline core, stability, full subsystem matrix, guide/video/slides/declaration | Deston |
| R15 | Try Now using supplied multi-person standard recogniser | No enrolment/account required; unseen-person results recorded; clear fallback on failure | Hau Jie |
| R16 | Simple runbook editor and explicit stage execution | Build/edit/reorder/delete stages; one gesture one action; failed stage recoverable | Javier |
| R19 | Rehearsal/session summary | Counts reproduce event trace; no false completion; no raw video/key leakage | Javier |
| R20 | Complete supplied corporate scenario and usability comparison | Unfamiliar presenter can attempt workflow; button/starter/personalised comparisons recorded | Deston |
| R21 | Standalone desktop shortcut library and three-slot Quick Actions | App/file/folder/HTTPS targets open through validated bindings; no deck required; missing targets and association errors visible; no duplicate launches | Javier |

## 6. Implementation boundaries and safety

Retain Python 3.11, PySide6 Widgets, OpenCV, MediaPipe, NumPy, scikit-learn and existing tests/tools. Keep 21 world landmarks -> wrist-relative/scaled 60 features and the existing latest-frame worker architecture. Gesture classification and data processing remain local. No hosted AI client, text-retrieval subsystem, new framework or database service is required.

Pipeline: camera -> validated observation -> selected starter/personal classifier -> rejection -> controller -> versioned binding -> deduplicating dispatcher -> viewer/runbook/desktop shortcut. Exactly-once control and outcome logging apply to every action type.

Deston owns shared `contracts.py`, `controller.py`, `app.py`, `__main__.py` and integration acceptance. Hau Jie owns collection/dataset/models/evaluation and new profile/enrolment modules. Javier owns viewer/workspace/runbook/shortcut widgets and session-summary modules. Builders own their module tests and guide/report sections. Shared changes require an agreed handoff, not parallel edits to the application shell.

### State transitions

| Event | Required behaviour |
|---|---|
| Start/resume | WAIT_NEUTRAL then deliberate hold; no remembered candidate |
| Accepted held gesture | Exactly one action under the current stage/profile/model snapshot |
| Stage/profile/model/workspace change | Cancel old generation and callbacks, clear candidate; require neutral |
| Pause/tracking loss/focus loss | Cancel pending actions and pause or reset to neutral requirement; explicit resume after app focus loss |
| Launch Camera | Pause, release capture and wait for shutdown before launch; return manually and resume |
| Close/reopen saved session | Restore content position/bookmarks but remain paused; do not replay past app launches |

Readiness revision includes selected hand, training data hash, feature version, classifier/rejection settings, hold/rearm settings and the configured binding-map revision. Selecting an existing stage/context does not edit that revision or repeat rehearsal; it only cancels the pending hold and requires NEUTRAL. Editing a mapping invalidates readiness. Cosmetic renames do not invalidate it. Returning users do not repeat full training. Guest checks are session-local, since there is no identity authentication.

### Validation and data limits

- JSON workspace: supported schema only, maximum 1 MiB; reject unknown action types, duplicate IDs and executable/credential fields.
- Deck is optional for Quick Actions; when present: 1-100 cards; IDs <=64 characters, title <=120, body <=8,000.
- Runbook is optional; when present: 1-12 stages, <=3 single-action slots per stage; valid card/shortcut references; no cycles or scripting.
- Executable binding: user-selected existing local `.exe`; no network path, script, interpreter/shell or argument field. Built-in app adapters have their own allowlist. Selection is a local trust decision, not a malware sandbox.
- File/folder binding: existing resolved local path; reject network/device paths and disallowed file types at setup and dispatch. HTTPS binding: parsed HTTPS URL with non-empty host and no embedded credentials; reject every other scheme. Limits: twelve local targets, labels <=80 characters, URL <=2,048 characters.
- Imported packs never install executable, file, folder or URL bindings. Validate the entire pack before replacing active state.
- Raw video stays off. Action records contain limited IDs/outcomes/timings, without raw video, document contents or full sensitive target paths by default.

## 7. AI contribution, marks and operating costs

Removing contextual AI assistance does not remove the core AI system. MediaPipe supplies pretrained landmarks; the team's contribution remains the trained kNN/SVM gesture classifiers, preprocessing, unknown-pose rejection, starter-versus-personal recognition, activation controller and integration into a complete usable workflow.

The brief requires investigation of at least two techniques, not two different AI subsystems or a language model. A fair kNN-versus-SVM comparison with a justified selection satisfies the technique-count requirement; quality of the investigation and results still determines the marks. The final feedback sheet has no criterion requiring a chatbot or generative AI. Removing one proposed feature does not cause an automatic deduction, but the remaining system must meet its agreed requirements and all assessment deliverables. Record this scope revision with the tutor if the assistant had been separately approved as a requirement; do not invent that approval.

Retain technical depth through (1) kNN versus SVM, (2) frozen starter versus personalised recognition on the same test trials, (3) rejection and controller replay comparisons, and (4) end-to-end task completion/recovery and all-subsystem testing. Creativity comes from custom personal gestures controlling shareable, authored procedures and desktop resources, supported by rehearsal and clear feedback. More subsystems are not automatically worth more marks; unfinished or weakly evaluated ones create delivery risk.

All GestureForge recognition, profiles, rehearsal, procedures, local file/folder/application shortcuts and saved state run offline after setup. Opening an HTTPS website still needs the browser/site connection for its content; opening an external application does not make that application's own online features work offline. No AI provider account, API key, paid inference or large local language-model download is needed.

Useful prior-art comparisons remain [Pawvis](https://pawvis.app/), [CyberGesture](https://github.com/irolyuk/CyberGesture) and [Stream Deck profiles](https://docs.elgato.com/stream-deck/profiles/getting-started/). Compare workflow, setup and control choices, not a world-first claim. [Grouped cross-validation](https://scikit-learn.org/stable/modules/cross_validation.html#leave-one-group-out) supports separating people in recognition evaluation; it does not guarantee generalisation.

## 8. Evaluation that adds technical depth

### Starter recognition versus personalisation

Collect a new consented starter dataset from the three team members using the same standard poses in separate sessions. Budget two sessions x eight trials x four labels x five scheduled vectors per member: at most 960 starter vectors across the three members, plus negatives. This is separate from the personal evaluation data. Do not reuse P01 samples for public starter redistribution without specific permission. Use person-separated development folds to compare kNN and SVM and tune thresholds; fit transforms only on each fold's training people. Then freeze the starter and evaluate it on at least two new consenting participants excluded from training and tuning. Their availability is a project dependency, not an established fact.

For those same participants, collect separate optional personal training and validation sessions, freeze personal configurations, then test starter and personalised systems on the same untouched standard-gesture test trials. This paired comparison isolates personalisation benefit. Evaluate changed custom poses separately; do not directly compare different pose sets and attribute the whole difference to personalisation.

If independent participants cannot be recruited, report team leave-one-person-out evidence honestly and narrow the claim. A starter trained/tested only on its own contributors is not evidence of new-user reliability. If starter quality is weak, improve development data/conditions and use a fresh held-out evaluation; do not silently make full enrolment mandatory while claiming zero-training success.

Personal evaluation retains the original target of two profiles, separate TRAIN/VALIDATION/TEST sessions, twelve trials per four labels per session and up to five scheduled vectors per trial: 288 trials / 1,440 maximum vectors for those two profiles, plus the separately budgeted starter dataset and negative activity. Keep entire trials in a split. Retain invalid samples and count rejected genuine gestures as misses. No test-data retraining.

Report per-person trial macro-F1, per-class precision/recall, UNKNOWN confusion, false actions and first-use completion time. Proposed targets: personal macro-F1 >=0.90; starter >=0.85 per held-out person under stated conditions; first standard action within two minutes after camera setup. These targets are not achieved results and must be fixed before the final test.

Bound the comparison to kNN k={3,5,7}, uniform/distance weights and RBF SVM C={0.1,1,10}, gamma={scale,0.1}; select rejection on validation positives/negatives. Explain orientation/distance limitations and any preprocessing changes. The assignment's BOOKMARK false acceptances need new negative tests before the action is enabled.

### Complete system and product value

| Area | Required evidence |
|---|---|
| Features/capture | Wrong/multiple/no hand, invalid scale, lighting/framing failures and clean shutdown |
| Profiles/data | Legacy import, guest vs personal selection, version errors, split integrity, atomic writes and deletion |
| Controller/dispatcher | Long holds, neutral rearm, stale/duplicate events, all stage/profile/model changes, no side effects during practice |
| Runbook/viewer | Stage editing/reordering, bindings, saved progress, boundaries, bookmarks, failed app action, restart without replay |
| Workspace | Malformed/oversized import, duplicate IDs, missing references, no exported secrets/data/paths |
| Apps/shortcuts | Both Windows machines; all four target types; empty-content Quick Actions startup/reload; missing/moved targets, missing file association, disallowed path/scheme, duplicate events, import rebinding, launch-request outcome, Camera release/recovery and focus loss |
| UI/session review | Always-visible action meanings, manual alternatives, readable errors, event counts match displayed summary |
| Release | Fresh guide-only install on second Windows laptop; offline core; thirty-minute stability/memory/observation rate; source/config hashes |

Twenty five-second holds per profile distributed across enabled action types: zero duplicates. Ten minutes of non-command activity per profile: target <=1 unintended viewer action and zero unintended external launches of any shortcut type. Action latency p95 target <1 second includes hold time; application startup time is recorded separately from dispatch latency. Replay controller protection on/off against the same predictions with simulated dispatch only.

Product task: a presenter unfamiliar with the supplied scenario completes the six-stage demonstration, launches a tool, opens a local reference/folder, bookmarks a discussion point, reloads saved progress, and recovers from one injected failure. Compare manual controls, starter gestures and personal gestures with counterbalanced order; record time, action errors, retries, help requests and brief comfort/usefulness ratings. Report the small sample and practice effects. Do not call this proven commercial demand or universal accessibility.

## 9. Team ownership, capacity and delivery

| Member | Main build/review ownership | Required evidence |
|---|---|---|
| Deston | Product direction, scope/contracts, screen designs, shared shell/controller integration, independent acceptance tests, report coherence and release decisions | Design decisions, reviewed PRs, integration evidence, final demonstration and release checks |
| Hau Jie | Starter/personal models, profiles/enrolment/rehearsal, data/evaluation and recognition robustness | Tested modules, reproducible comparisons, data/source documentation, AI-methods report sections |
| Javier | Viewer, workspace/runbook editor/execution, desktop shortcuts, session summary, guide and video draft | Tested action/storage/UI paths, scenario package, install guide and complete demo recording |

Builders use their AI tools for the substantial implementation and repetitive documentation work, but own tests and explanations. Deston controls direction and final acceptance; he does not replace their unit testing. Do not carry over the assignment's two-person contribution percentages or invent registration/signature approvals for Javier.

The 29-item CSV estimates 75 base hours for Deston, 75 for Hau Jie and 73 for Javier (223 team hours). Reserve 20% contingency: approximately 90 / 90 / 88 hours respectively. These are planning estimates, not confirmed availability. This is 45 fewer base hours than revision 3; do not fill the saving with replacement features. Keep the existing release dates and use the headroom for recognition quality, verification and delivery contingency.

Before the 18 October feature freeze, the backlog allocates 34 / 51 / 54 base hours respectively. Confirm actual availability at the 4 October capacity gate. Deston integrates modules as they arrive; GF-P16 dependencies are completion prerequisites, not a reason to postpone all integration checks. Feature freeze remains a target; testing, report work and release checks retain their scheduled time.

| Dates | Exit gate |
|---|---|
| 30 Sep-4 Oct | Preserve assignment; agree extension/contracts; demonstrate shortcut opening and Camera handoff; starter leave-one-person-out spike; minimal runbook path; assess capacity/recruitment |
| 5-11 Oct | Working starter and personal onboarding; all viewer actions; workspace/runbook creation; first integrated corporate scenario |
| 12-18 Oct | Desktop shortcuts, app recovery, rehearsal/summary; all 17 active requirement paths integrated; feature freeze |
| 19-25 Oct | Freeze data/configs; held-out-person/personalisation and rejection tests; full workflow and controller tests |
| 26 Oct-1 Nov | Defect fixes and affected regressions; fresh Windows install; stability; release candidate |
| 2-6 Nov | Final report/figures, guide, video, slides, declaration and ten-minute presentation; package/upload/download verification |
| 7 Nov | Deadline buffer only |

Use Trello project-release cards, Git/GitHub PRs and WhatsApp. One active implementation item per builder, twice-weekly integration reviews and genuine weekly tutor updates. Local verification is required; GitHub Actions remains manual. Cards move to Done only with criterion-specific evidence. All 29 project cards were verified on Trello during kickoff; the Trello board and handoff record their links. Owner names identify responsibilities, not confirmed member-account assignments.

Handoffs: Hau Jie and Javier may add owned modules/widgets and tests but must coordinate shared-contract changes with Deston. Do not revert others' work or rewrite the whole UI independently. Each PR includes commands actually run, results, limitations and the author’s explanation. Deston reviews and merges only after local checks and relevant workflow verification.

## 10. Exclusions and submission gates

Do not build direct PowerPoint control, a virtual mouse, arbitrary OS scripting, background control of other applications, speech recognition, sign-language translation, dynamic/two-hand gestures, PDF ingestion, web crawling, embedding downloads, local LLMs, contextual AI assistance, chatbot integration, AI prompt composition, hosted AI clients, autonomous AI actions, cloud accounts, billing, enterprise RBAC or an executable installer. Preserve existing macOS code where feasible; the expanded release is verified on Windows.

The distinctive contribution is the complete trainer workflow and the evaluation of immediate start versus personalisation, not inventing a new general-purpose model. A small authored runbook, reusable desktop shortcuts, personalisation and rehearsal provide depth without a plugin engine or a second AI subsystem. Playback/media keys, meeting controls and keyboard-macro recording remain outside the approved release; opening a reference file does not imply controlling its viewer.

Final report follows the brief: title/abstract, domain/workflow, critical prior work, lifecycle, whole-system/subsystem design, AI methods and preprocessing, evaluation protocol/results, discussion/limits, deployment/integration/maintenance, references and appendices. Guide records dependency versions and reproducible steps. Include source/permitted datasets/configs, demo video, slides, contribution/declaration and mandatory tool use. Update all three members' assistance evidence prospectively.

The brief expressly requires assistance prompts in the report/appendix (pages 1 and 6). Existing separate Word logs remain untouched now; confirm an acceptable final reporting arrangement rather than silently omitting a requirement or combining files against the user's instruction.

Release gate: every agreed requirement has recorded verification; independent install and offline recovery pass; starter distribution permissions are recorded; offline and external-application limitations clear; no secrets in packages; all members explain their work; required documents/video included and downloaded submission inspected. Do not guarantee a grade, fabricate results, or mark an untested capability complete.

Kickoff outputs: revised plan and backlog, team handoffs, shared routing/controller foundation and tests, and updated Trello project cards. Existing Word logs and the submitted assignment archive remain unchanged. Source publication is authorised; the progress record identifies the published implementation and remaining work.

### Deployment and maintenance plan

Deliver a source release with pinned tested dependencies, the existing Windows setup/run scripts, necessary licensed assets and permitted reproducible data/configurations. Record version/checksums and guide-only installation evidence. No executable installer is promised. Use versioned JSON schemas, atomic writes and a backup before migrations; unsupported schema versions produce recovery guidance rather than partial loading. Keep the previous working profile/configuration available for rollback after retraining. Regression-test model/data/schema changes against frozen cases, and rerun affected held-out evaluation when the recognition feature policy changes, clearly separating prior and new results. Provide a troubleshooting section for camera permissions, missing associations, missing assets, unavailable shortcut targets and restoring saved state. Dataset retention/distribution follows actual participant permissions; no new consent is inferred.

## 11. Approval boundary and build acceptance

Approval covers the 17 active requirements in section 5 and the deliverables in this version. It starts local implementation, automated checks and integration in the existing `code` repository, preserving the submitted assignment archive. It is not permission to publish personal datasets or submit to LMS. The subsequent user request authorises committing, pushing and merging reviewed project changes. Existing Word reports and prompt/decision logs remain local and unchanged. Trello project tasks have been migrated to this revision. Use TEAM_BACKLOG.csv and PROGRESS.md for current status; original estimates remain the progress denominator. The first foundation slice passed 116 automated tests. The next slice adds a simulation-only Studio shell; current checks and uncompleted acceptance gates are recorded in PROGRESS.md. Readiness scoring and OS dispatch remain to be integrated.

Retain `python -m gestureforge`, `python -m gestureforge.collect`, `python -m gestureforge.evaluate --config ...` and `python -m pytest`; the UI makes collection optional for standard users but the CLI remains useful for reproducible evaluation. Existing Windows launch/setup scripts remain the supported install path. Run targeted tests, then the existing local lint/type/test verification before a release; Actions stays manual.

First build gate, by 4 October: preserve/hash submitted baseline; review pre-existing uncommitted changes; freeze contracts and initial screens; verify starter feasibility, Camera handoff and app/file/folder/HTTPS opening. Confirm real team availability and arrange two independent evaluation participants. These are unresolved execution dependencies, not invented approvals or completed checks. If a core gate fails, propose and document a scope revision before replacing a promised feature.

The plan avoids conditional 'stretch' features. Do not drop tests, reproduction data, video, guide or old final-project promises to recover schedule. Reduce decorative styling and extra example content first. Any capability change after approval requires an explicit requirement/backlog update and user review, plus tutor discussion when it changes the approved academic scope.

At feature freeze, one complete supplied six-stage scenario must work with standard gestures, saved personal profiles and manual controls. It must demonstrate desktop shortcuts, rehearsal, saved state and recovery. At release, every numbered requirement must have a recorded result and every shortfall must be visible. Performance targets are test objectives; do not fabricate results or retrospectively lower targets to declare success.
