# GestureForge Studio team implementation guide

Updated 22 October 2026 · Project deadline 7 November 2026

Deston has authorised project implementation. Build the approved Windows corporate training and demonstration product on the submitted assignment. The assignment ZIP is preserved separately. This guide assigns work; it does not claim that future features or participant tests are complete.

## Current deliveries — 22 October

Hau Jie's methods/results Word contribution and Javier's edited manual video
are now received and reviewed. Their [review record](TEAM_DELIVERABLE_REVIEW_2026_10_22.md)
contains source hashes, bounded findings and exact next returns. GF-P24 is now
In Progress. Laptop-B assisted setup/native observations are reported in the
Word contribution; its referenced logs and the video's restore exports have
not yet arrived. Send those existing files privately before repeating checks.
No new whole task is accepted from these two contributions alone.

The current retained Studio source ZIP is `releases/gestureforge-studio-source.zip`,
source `a480e2e32ea9c3642dbaab922ae3a76ef6801ad1`, SHA256
`840a509dd0a341ca1e206044d9fbec360b143cb82d3cdc672d1167b534103e2f`.
It contains 197 verified members and the PR #35 session-feedback fixes. Source
setup is still required. Hau Jie's reported archive has a different hash; retain
its separate receipt. This documentation update requires no replacement package.
Git users sync main on their own branches; existing physical evidence retains
the build on which it was collected.

### Retained experiment and package history

Deston has received and verified Hau Jie's private H1 starter audit packet as
an internal team handoff. The packet's hashes, saved reports, fixed cases and
trial inventories reconcile with the supplied private files. This closes the H1
handoff substep only: it does not approve a deployment starter, public/marker
redistribution, H2 settings, freeze review or final TEST.

**H2 diagnosis reviewed:** [PR #31](https://github.com/Chi944/GestureForge_304/pull/31)
is merged. Deston's independent reproduction checked 17 original source-file
hashes, eight evaluator runs and all 48 bounded candidate rows against Hau Jie's
private packet. P67's proposed kNN settings (multiplier 2.5 / margin 1.75) give
development macro-F1 0.790 with 12/40 negative sample predictions accepted as
commands. P1543's proposed SVM settings (2.5 / 1.25) give 0.667 with 10/40.
These are classifier samples, not live actions; neither proposal qualifies for
deployment. No examined setting eliminates negative command predictions.
On 14 October Deston confirmed P1543 was excluded from earlier starter fitting
and tuning and took a break before VALIDATION. He also confirmed H1's four
right-hand poses match the browser protocol. These are user-confirmed provenance
facts, not observations made by the evaluator. Keep P67 and P1543 excluded from
starter fitting/tuning for the independent comparison. Deston retains these
settings under the explicit after-development policy in the independently
reviewed [selection record](H2_EVALUATION_SELECTION_2026_10_14.md). Both private
freezes, their input/settings pins and four participant-specific ZIP hashes are
verified. **GF-P17 is accepted as experiment preparation. GF-P18 is now accepted**
after both real TEST returns were imported and independently scored twice against
those unchanged freezes. Each contains 48 trials and 240 scheduled samples;
P67's three invalid samples remain misses, and P1543 has none. See the
[paired TEST results](GF_P18_TEST_RESULTS_2026_10_14.md).

Trial macro-F1 is 0.769 starter / 0.718 personal for P67 and 0.979 / 0.397
for P1543. Both personal models reject all 12 NEXT trials. The starter misses
its 0.85 per-person target on P67; both personal models miss 0.90. Experiment
completion does not approve deployment or LIVE use. Preserve these failed
results and their freezes. No further TEST session or repeat is requested from
these participants. Their returned numeric files do not establish the current
OS/browser, assistance or camera-recovery experience.

GF-P12's current personal LIVE protocol is now `gf-p12-v4`: three five-second
windows for each enrolled action pose plus NEUTRAL, followed by ten negative
windows. This 22-window pass can unlock normal personal LIVE use for the exact
current profile/model/hand/camera/behavior and authored context after saving,
event reconciliation and paused restoration. It is still not final performance
evaluation or native-device acceptance. Historical v1-v3 50-window results
remain old evidence and cannot grant v4 LIVE eligibility. Javier's previous P03 attempt remains failed evidence. His short PREVIOUS and
index-finger negative traces are now received and reviewed in the
[P03 trace review](P03_TRACE_REVIEW_2026_10_19.md). Investigate the negative
false NEXT before any fresh 22-window attempt; do not repeat the short trace.

Use a fresh Studio source ZIP only for teammates who run from ZIP. Git users
should pull/rebase from `main`; participant browser collection kits are separate.
Extract the new Studio ZIP into a fresh folder and keep old private profiles,
datasets and `.local` evidence outside the replacement folder unless the guide
explicitly tells you to import them.

Historical source verification on 16 October passed 991 tests (two platform skips
and the expected duplicate-ZIP test warning), Ruff, mypy (104 source files),
both startup modes and synthetic evaluation. See
[the progress record](PROGRESS.md) for its private verification report.
The earlier 14 October collector run passed 30 Node checks; the collector is
unchanged by this diagnostic. The earlier extracted
Practice/Live suite passed 153 checks on its recorded package. Follow each
Studio archive's matching verification record; those checks do not verify a newer archive. These
checks do not establish recognition on a participant's hand or native device
acceptance. GF-P17 acceptance also requires the verified private freezes and
reviewed provenance/selection decision; test counts alone do not close it.

The refreshed handoff identifies clean source **`d200947`**. Its 191 archive
members match source, and extracted-source model loading, both startup modes
and 31 focused tests pass (one platform skip), using the existing Windows
dependencies. See [the progress record](PROGRESS.md#studio-recognition-and-package-audit--16-october)
for its SHA256 and verification limits. Deston's Downloads folder
`GestureForge/Studio/Current/GestureForge_Studio_Handoff_20261016` contains the ZIP, matching receipts and
`READ_FIRST.txt`. Later documentation-only updates do not change this ZIP's build.

Read the **Next delivery** table at the top of your individual brief first.
It supersedes older recording priorities. Return small, reviewable deliveries
as they become available instead of waiting for your entire lane to finish.

| Delivery | Execution | Deston's review / final gate |
|---|---|---|
| H1 / GF-P17 preparation | PR #27's aggregate audit is merged; Hau Jie's private H1 packet is received and verified for hashes, saved reports and inventories | H1 remains internal-team evidence only; it does not approve a deployment starter or public/marker redistribution |
| H2 / GF-P17 → GF-P18 | Both tasks are accepted: P67/P1543's actual TEST returns were audited and the same frozen comparisons reproduced independently | Retain failed targets and invalid slots in the results. No deployment model is qualified; no TEST recollection, threshold tuning or model selection on these results |
| J1 / GF-P19 | Earlier native evidence is retained. Javier's manual video now shows bounded request/validation/post-restore views; send its existing restore exports and filmed build identity. | Remaining association/failure/retry and valid-grant active-capture Camera cases are still required. Recheck only affected session feedback on updated source. |
| H3 + J2 / GF-P19, GF-P23 | Hau Jie's report supplies attributed laptop-B assisted setup/native checks and reported offline/endurance/closure observations; send reference [10] files for Javier's consolidation. | Guide-only setup, measured stability/release evidence and remaining device/defect gates are not closed. Keep interrupted monitor and later reported thirty minutes separate. |
| J3 / GF-P20 | Javier coordinates observer records, condition order, actual hold/negative/latency sessions and disjoint exports; Hau Jie supplies frozen recognition inputs | Deston analyses/replays measurements and accepts the integrated study after GF-P16/GF-P17. Unavailable standard mode is reported, never silently replaced |
| H4 + J4 / GF-P24, GF-P25 | Hau Jie's Word contribution is reviewed against current results; Javier's labelled manual video draft and earlier guide are received. | Final GF-P21 reconciliation, guide-only/native release evidence and complete gesture/scenario/recovery demo remain before GF-P26/GF-P27. Do not redraft already delivered sections. |

Original task owners, weights, dependencies and acceptance criteria stay fixed.
Accepted task weights are Deston 26/75 (34.7%), Hau Jie 63/75 (84.0%),
Javier 48/73 (65.8%), and team 137/223 (61.4%): 17/29 tasks Done.
GF-P17 and GF-P18 are accepted against their original criteria. Delegation shifts execution, not
accountability. GF-P24/GF-P25 drafting can proceed before their final dependencies.
Private participant data, full exports, videos and Word deliverables go through
the team's existing private folder/archive, not Git/Trello. Do not update the private
prompt or decision logs as part of this handoff.

### Current manual and GPT-ready work

Current as of 22 October, after the [team deliverable review](TEAM_DELIVERABLE_REVIEW_2026_10_22.md). All three
members have work available now; the later acceptance gates below still apply.

| Member | Manual / physical work now | GPT-assisted work now |
|---|---|---|
| Deston | Retain final direction and review the integrated demonstration, release evidence and final report/presentation when prerequisites pass. No repeat participant TEST is requested. | Verify the supporting packets when received, reconcile report sections and disjoint exports, integrate demonstrated fixes and analyse actual workflow evidence. |
| Hau Jie | Send the existing reference [10] laptop-B packet privately. Agree only remaining guide-only/native/stability/release checks with Javier; retain successful reported checks and original failures. | Reconcile receipts with the Word contribution, continue the development-only recognition investigation and update final methods/results after GF-P21. No duplicate experiment, TEST tuning or speculative threshold change. |
| Javier | Send the video's existing before/after restore exports and exact filmed build identity; consolidate Hau Jie's laptop-B evidence. Finish unrun native cases and affected feedback checks; gesture-dependent cases need genuine readiness. | Reconcile the two-device matrix and non-overlapping exports, fix demonstrated defects and plan remaining real gesture/scenario/recovery footage. Preserve the received manual video draft and accepted unchanged checks. |

**Next returns:** Hau Jie sends the existing private reference [10] packet;
Javier sends existing restore exports, filmed build identity and the remaining-case
matrix. Their Word contribution and manual video are already received. The representation implementation
was completed with GPT assistance in Deston's integration track; it is not a new
teammate-authored submission and does not qualify a deployment model.
Javier's short P03 traces are received: replay agrees with four PREVIOUS Preview
simulations and two additional NEXT simulations during the reported index-finger
negative attempt. The second summary is cumulative six, not ten. The saved
profile is Right/kNN with multiplier 1.5 and margin 1.0; that margin disables
ambiguity rejection by design, but a higher margin is not a demonstrated fix.
The received private profile and numeric DEVELOPMENT packet reproduce the exact
saved model. PREVIOUS improves 2/8 → 5/8 on the reused original validation, and
negative command samples fall 10/40 → 4/40. Older index samples are rejected;
the remaining four errors are older OK-sign samples accepted as NEXT. The recent
live index failure still lacks numeric features and is not reproduced by those
older samples. See the [numeric comparison](P03_TRACE_REVIEW_2026_10_19.md#private-numeric-packet-received-and-reproduced--19-october).
No duplicate packet or blanket recollection is requested. These results do not
prove final accuracy, a runtime defect or a Practice/Live pass. Next return a
focused remaining-case evidence PR and attributed laptop-B matrix; the reviewed
GF-P25 guide draft does not close the video or final release requirements. GPT prepares and checks
evidence; people supply observed device outcomes and final review decisions.
PR #34 is reviewed and merged: its trusted-app, restore/no-replay and target-save
checks retain their original `d200947` build attribution. Current source also
fixes missing-runbook feedback and the stale top LIVE notice; the 16 October ZIP
predates those UI fixes. Sync reviewed main or use a source ZIP built from it
before checking the affected feedback. Participant collection packages are
unchanged. A source update does not establish a new physical device pass.

**Use the repaired verification command:** `python scripts/verify.py --timeout 1200`
now writes and prints a fresh timestamped report under ignored `experiments/local/`.
Both optional output filenames must be new; existing reports or data cannot be
replaced by a verification run. Keep each result with its tested source version.

**Before a measured workflow:** export preparation/Practice results, then
**Restart deck** to begin an empty task summary before timing starts. Confirm
the appropriate readiness remains valid. Follow [the measured reload procedure](WORKFLOW_COMPARISON.md)
instead of the development walkthrough's simulation probe. Keep all task
segments and failed attempts; these instructions do not relax the scoring rules.

**Then:** GF-P20's measured live study retains its GF-P16 integration gate;
accepted GF-P17/GF-P18 do not grant deployment or live readiness. GF-P21 is In
Progress from the reproduced development diagnosis but is not Done before its
original GF-P20 dependency and defect checks. Final GF-P23 release acceptance follows
defect closure and affected retests; Windows checks can begin now. The two TEST
sets have been consumed: any later model changes need a new predeclared,
independent evaluation rather than a better score on these returns. P69 stays
closed TRAIN-only with no further collection.

**Working copies:** sync reviewed `main` while preserving local changes. Hau Jie
pushes only `codex/hau-jie-profiles`; Javier pushes only `codex/javier-shortcuts`.
Open focused PRs and leave merging to Deston. Git users can continue from the
identified source commit. For a fresh-install ZIP test, use the Studio source
archive with its matching commit/hash receipt and extracted-source verification.
Do not treat the older 13 October verification as proof for a newer archive.

After setup, **run-studio.cmd** opens Studio on Windows and **run-studio.command**
is the corresponding Mac launcher. The legacy `run.cmd`/`run.sh` defaults stay
unchanged. New profile creation shows and retains the host's rejection settings;
existing saved profiles retain their own settings. The audit does not establish
that Javier's physical PREVIOUS pose is now recognised. Follow the
[P03 findings](P03_TRACE_REVIEW_2026_10_19.md) before requesting another long trial.
For Practice action and negative windows, wait for READY before Begin; for a
NEUTRAL window, wait for capture, press Begin, then establish READY inside it. Participant browser kits are unchanged.
Participant kits and the private data handoff serve different purposes; neither
is a Studio installation. Follow [release instructions](../../releases/README.md).

GPT or synthetic checks cannot claim participant consent, physical laptop behavior,
camera recovery, real app launches, final TEST independence or marker acceptance.

Hau Jie's 8 October first private handoff is the existing starter audit packet:
complete consented numeric manifests/NPZ sidecars, baseline and 48-candidate
reports, saved all-six-fold/fixed-case diagnostic, hashes, pose/session/source
details, the legacy standard vocabulary, Right hand and permission scope, or
exact missing-status notes. The matching PR on
`codex/hau-jie-profiles` contains only sanitized aggregate evidence; that audit
was merged in PR #27. On 14 October the private packet was received and verified
for hash/report/inventory consistency as internal-team evidence.
No newer starter recording is requested until D1 diagnoses a need.

GF-P18's original 10 task-weight hours are now accepted for the reproducible
paired experiment, including its failed targets. Current accepted totals are
26/75 for Deston and 137/223 for the team; model performance and physical LIVE
acceptance remain separate gates.


**Historical 5 October integration update:** GF-P10's approved-standard loader and six-action activation route are implemented with generated-fixture verification. No standard model is enabled: the recorded bounded comparison found no qualifying candidate and redistribution permission is unresolved. Personal LIVE still requires full Practice. PR #24 is merged as partial laptop-A evidence; Javier continues the missing native cases. PR #25 delivers GF-P12 selected-pose repair with Deston's shared-camera/Profile integration, explicit candidate create and rollback path; independent review accepts it against the original software criterion. Deston keeps final integration and release acceptance. Accepted completion at that checkpoint was 51.6% (15/29 tasks); use the current totals above and PROGRESS.md.

GF-P16's standard path remains blocked wherever it depends on GF-P10. Personal
LIVE software and manual paths may continue through their separate gates.

**Device assignment, 5 October:** laptop A is Javier's Windows laptop and laptop B is Hau Jie's Windows laptop. Hau Jie operates laptop B; Javier coordinates and consolidates GF-P19 evidence; Deston reviews GF-P23 and final integration. Both use the same identified Studio build. No laptop-B test is yet recorded. Original task ownership and weights remain unchanged.

## Start here

Read this guide, your individual brief, `CONTRACTS.md`, then `PROJECT_PLAN.md`, `TEAM_BACKLOG.csv` and `PROGRESS.md` in this directory. The full plan is revision 4: contextual AI assistance is removed. There is no chatbot, LLM, provider account or API-key feature. kNN/SVM gesture recognition is the AI subsystem.

The kickoff pack includes the source baseline and Deston's tested routing foundation. It deliberately excludes participant datasets, downloaded model assets, environments, reports, prompt/decision logs and Git metadata. It is a build handoff, not a final release or a ready-trained starter model.

## Responsibilities and editing boundaries

| Member | Owns | Current next step | Reviewer |
|---|---|---|---|
| Deston | Product direction, shared contracts/controller/routing, `app.py`, `__main__.py`, screen design, integration, acceptance and release | GF-P18 paired evaluation accepted; review development-only defect work and complete the remaining integration, physical evaluation and release gates | Teammate review; Deston makes final release decision |
| Hau Jie | `collect.py`, `dataset.py`, `models.py`, `evaluate.py`; new profiles/enrolment/practice/starter modules and their tests | GF-P21 development-only diagnosis; H3 laptop-B checks; H4 methods/results contribution, in [your brief](HAU_JIE_HANDOFF.md#next-delivery--assigned-7-october) | Deston |
| Javier | `viewer.py`; new workspace/runbook/shortcut modules and widgets, session summary, guide and video draft | J1 remaining target-association, failure/retry and active-capture Camera handoff cases plus affected session-feedback checks on updated source; preserve PR #34 bounded evidence; J2 device/release evidence; J3 observer-study coordination; J4 guide/storyboard, in [your brief](JAVIER_HANDOFF.md#next-delivery--assigned-7-october) | Deston |

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

PR #10's vocabulary work, PR #13's evaluator and PR #14's reviewed [profile persistence component](PROFILE_PERSISTENCE_HANDOFF.md) are integrated. Hau Jie's [starter checkpoint](STARTER_EVALUATION_CHECKPOINT.md) reports the three-person collection and baseline comparison; neither classifier is ready for release. Preserve the baseline and private inputs, and request targeted repair collection only for a diagnosed defect. PR #16's [guided enrolment component](ENROLMENT_INTERFACE_PROPOSAL.md) is attached to the shared camera; GF-P07 is accepted from reviewed generated UI workflow evidence combined with attributed P02 physical observations. PR #17's [selector](PROFILE_SELECTOR_HANDOFF.md) is attached in Profiles with Guest/manual fallback. Its [diagnostic slice](STARTER_FAILURE_ANALYSIS.md) is accepted. PR #19's [bounded comparison](GF_P11_BOUNDED_COMPARISON.md) was reviewed and repaired for reproducibility and evidence consistency; its supplied no-qualifying result is unchanged and has not been independently rerun. PR #20's local camera pilot is partial personal-pilot evidence only: 2/8 accepted NEUTRAL validation trials and kNN/SVM macro-F1 0.7209 remain attributed to Hau Jie's private pilot, not a new independent evaluation. Existing model/rejection thresholds and neutral hold/rearm policy are not relaxed from that result. PR #25 completes GF-P12's selected-pose repair software: the Repair pose tab uses Deston's shared observation-only camera path, starts from the installed saved personal profile, routes the candidate through Profiles for explicit create/load, preserves rollback to the original profile and expires readiness. Independent review accepts GF-P12 against that original software criterion using the integrated generated workflow and eight host tests. Explicit LIVE still permits manual actions through one persistent dispatcher; personal LIVE gestures require the saved, reconciled full Practice gate and explicit activation; native acceptance remains separate. The six-activation check is preliminary only. A new Hau Jie observation reports open palm sometimes remains LATCHED and movement can recover it, but the supplied screenshot does not show Prediction; do not claim the root cause resolved. Deston's reviewed feedback fix keeps prediction/rejection/rearm guidance in the fixed footer and clears stale errors on fresh accepted packets; accepted NEUTRAL rearming passes software regression checks. The physical intermittent report still needs Hau Jie's trace and intended-pose notes. Javier's [4 October checkpoint](JAVIER_OCT4_CHECKPOINT.md) preserves the historical Linux run. GF-P05 is accepted from PR #18's supplied [laptop-A observations and repair rerun](../evidence/WINDOWS_RESULTS_2026-10-02.md). PR #29 adds bounded laptop-A GF-P19 evidence for isolated Preview focus pause/reconnect, Camera Preview simulation, native Camera after capture was already off and later Preview reacquisition. PR #34 adds attributed trusted Notepad requests, historical-launch restore/no-replay and target-save validation on its identified build. Neither closes the remaining active-capture native Camera, failure/retry, missing-association, laptop-B or GF-P23 criteria; the latest session-feedback repairs still need affected native checks. Teammates should sync main and reuse Deston's attachment: Hau Jie uses the verified private H1 packet as fixed internal evidence, then targeted own-profile physical repair only if diagnosed, while Javier preserves accepted GF-P13 dispatcher evidence and records GF-P19's remaining Windows cases; GF-P34 still depends on the GF-P10 standard entry integration. Use [TEAM_BACKLOG.csv](TEAM_BACKLOG.csv) for accepted task status and remaining evidence.

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
