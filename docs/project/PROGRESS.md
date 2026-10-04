# GestureForge Studio progress

Snapshot: 4 October 2026. This measures the final-project extension, not the already submitted assignment or an expected grade.

## Completion measure

Progress = the original estimated hours of fully completed tasks / the total original estimated hours in [TEAM_BACKLOG.csv](TEAM_BACKLOG.csv). These are task weights, not hours actually worked. In-progress tasks receive no completion credit until their acceptance evidence is complete.

| Owner | Completed task weight / planned | Verified completion |
| :--- | ---: | ---: |
| Deston | 16 / 75 | 21.3% |
| Hau Jie | 23 / 75 | 30.7% |
| Javier | 38 / 73 | 52.1% |
| Team | 77 / 223 | 34.5% |

Eleven of 29 tasks are complete: GF-P31 (saved rehearsal/session review and event reconciliation, 6 hours), GF-P05 (Windows launch probe and reported native recovery evidence, 5 hours), GF-P11 (bounded rejection comparison with an explicit no-qualifying result, 8 hours), GF-P06 (profile lifecycle and Guest/manual selection, 10 hours), GF-P02 (design/interface freeze, 8 hours), GF-P01 (baseline, 2 hours), GF-P32 (scenario/evaluation protocol, 6 hours), GF-P03 (vocabulary/import, 5 hours), GF-P08 (viewer/persistence, 7 hours), GF-P09 (workspace schemas, 8 hours), and GF-P29 (runbook authoring/execution contract, 12 hours). A 2 October independent acceptance audit credited the three Javier software tasks against their own written criteria at `a6fe7b6`: component and Studio integration tests cover commands/boundaries/bookmark reload; validated round-trip and failed imports; stage create/edit/reorder/delete, single-action slots, neutral reset and paused restoration without replay. Earlier progress grouped these software tasks with unrelated native-launch/readiness gates and undercounted their completion. GF-P05 is now separately accepted on Javier's supplied laptop-A observations and repaired-probe rerun; manual LIVE dispatch is now attached; LIVE gesture readiness and GF-P19's two-laptop integrated evidence remain incomplete.

GF-P02 is now accepted against its original design criteria: the approved Try Now / optional Personalise flow, one typed action per stage slot and the screen transitions are fixed in [CONTRACTS.md](CONTRACTS.md#gf-p02-design-freeze---2-october-2026). Independent acceptance and architecture reviews reconciled the logical handoffs with reviewed merged profile/workspace code, explicit tab activation and LIVE-only readiness gating. This is an owner design freeze supported by approved scope and code adoption, not a claim of a new team meeting or completed runtime/hardware tests. GF-P10/P12 remain separate from the completed GF-P06 profile workflow.

Hau Jie's [PR #10](https://github.com/Chi944/GestureForge_304/pull/10) and Javier's reviewed component delivery are integrated; see [delivery review](JAVIER_DELIVERY_REVIEW.md). Native Windows launch evidence, readiness integration and the final live workflow remain separate tasks.

## Built, but broader tasks still in progress

- **GF-P07 - Hau Jie:** reviewed [PR #16](https://github.com/Chi944/GestureForge_304/pull/16) supplies timed observation-fed collection and an embeddable consent/pose/countdown widget. Review repaired delayed-frame expiry and camera release during failed-save cancellation, retaining trial evidence for retry. Deston's shared-camera adapter now attaches the widget to Studio with model-free observation capture and cancellation/save protection. [PR #20](https://github.com/Chi944/GestureForge_304/pull/20) adds partial P02 recording evidence. PR #22's supplied physical follow-up closes the invalid-feedback/partial-slot Stop gap: retained invalid and cancelled slots reload successfully. The short current-version collection/profile workflow recording remains; the task stays In Progress with no Done credit.
- **GF-P28 - Hau Jie:** [PR #13](https://github.com/Chi944/GestureForge_304/pull/13) is merged with the participant-separated evaluator and [checkpoint](STARTER_EVALUATION_CHECKPOINT.md). Independent code and architecture review accepted the code after clarifying private input/output evidence. Integration checks passed 346 tests with one platform-specific skip, lint, types, both GUI startup checks and synthetic evaluation. Hau Jie reports P01 checksum validation and completed P02/P03 collection; their measurements were not rerun here without those private inputs. The baseline has poor NEUTRAL recognition and UNKNOWN rejection, so neither model is ready for release. GF-P28 is Review-Test while the private evidence/permission record is reconciled; GF-P06 profile lifecycle can proceed now.
- **P01 starter contribution - 1 October:** new right-hand data was collected in two separate positive sessions and a separate UNKNOWN session. Session 1 contains 32 trials with 159/160 valid samples; session 2 contains 32 trials with 160/160; negatives contain eight trials with 40/40. The one missed scheduled timestamp is retained. All manifests and numeric sidecars passed loader/hash, trial-count and session-separation checks; the private handoff archive was extracted and reloaded successfully. This is 72 trials and 359 valid feature vectors, not a recognition-accuracy result. Data, collection notes and the handoff archive remain excluded from GitHub. Deston forwarded the private archive on 1 October. Hau Jie reports matching its checksums and evaluating all three contributors in PR #13; integration review distinguishes those supplied results from local software verification.
- **GF-P10 - Deston:** the opt-in Studio preview opens, simulates held gesture actions, pauses on focus loss, and invalidates old context events. Its Preview/Rehearsal selector and gesture-to-action draft editor apply changes through a validated pause/reset; interrupted and stale identity packets cannot replace the active display. The launcher now passes the selected vocabulary into training and Studio, renders the enrolled IDs, binds predictions to a data/settings-derived model revision and rejects mappings to absent IDs before stopping capture. Studio now loads or switches an existing personal manifest in the background without restarting. A successful switch clears old predictions, reapplies compatible current-stage mappings in Preview (or keeps the workspace manual-only) and requires explicit start after camera release; failed loads preserve the previous selection while paused. Closing during training cannot install the result. Camera selection now pauses and invalidates old capture, waits for release before restart, and preserves the active context/mappings. Recovery clears stale previews; Ctrl+O/Ctrl+Enter/Esc, focus outlines and the training indicator improve keyboard use and feedback. Start/Pause, manual controls, state, hold progress and the active context/gesture legend now remain fixed while setup/deck content scrolls. Camera selection and ad-hoc mapping edits are in memory only. Studio loads portable workspace JSON, offers manual runbook navigation and saves/restores matching runbook sessions. Saved-profile startup and the background shell adapter are implemented; the visible Profiles selector is attached with unavailable-starter messaging; the short six-activation readiness check is implemented for loaded recognisers. Standard Guest recognition and LIVE gesture execution remain unavailable. Explicit LIVE mode supports typed manual controls through the shared dispatcher; Preview/Rehearsal requests simulate.
- **GF-P12 - Hau Jie:** [PR #21](https://github.com/Chi944/GestureForge_304/pull/21) supplies the fifty-window personal rehearsal component; Deston has integrated its embedded Practice attachment to shared capture, routing and the persistent dispatcher. The protocol measures ten five-second windows per action pose plus NEUTRAL, then ten negative intervals. Real participant evidence and final acceptance remain, so GF-P12 is In Progress with no Done credit. It does not enable LIVE gestures.
- **GF-P20 - Deston:** the offline replay tool now compares the actual rehearsal controller against a naive per-frame baseline using identical supplied predictions. It validates annotations/timing, protects the input file and reports reproducible counts, latency, checksum and controller settings. The new workflow comparison CLI also combines observer records and disjoint SessionSummary exports, retains failed/fallback/withdrawn conditions and reports individual paired times only for compatible successful conditions. These tools prepare evaluation; recorded participant traces, hold/negative live trials and the counterbalanced workflow study still depend on GF-P16/GF-P17. No completed-task credit is added.
- **GF-P13/P34 - Javier:** reviewed shortcut/summary components and a manual Windows probe are available. Manual viewer/workspace/runbook, stage-editor and session-summary attachment is implemented; GF-P08/P09/P29 are Done on their software acceptance evidence and GF-P05 on supplied native probe evidence. The shared dispatcher and manual LIVE actions are now attached. Integrated native launch/recovery and remaining Quick Actions/dispatch acceptance keep those tasks In Progress. GF-P31 is now separately accepted on software evidence after Deston's historical Practice review integration; real GF-P12/GF-P19 execution remains separate.

Software checks are recorded in [verification.json](verification.json). Automated simulation is not live-camera, Windows launch, starter-recognition or second-laptop evidence. The submitted assignment archive remains unchanged. GitHub Actions is manual-only; these checks ran locally.

The earlier dataset-loading slice passed 162 tests plus lint, type checks, both GUI smoke modes and synthetic evaluation. A native-window check loaded the existing local P01 dataset, enabled Start and retained a paused controller with no camera worker. The isolated check took 13.23 seconds including loading/imports (classifier fit 0.046 seconds); an earlier concurrent-check attempt exceeded its 30-second smoke timeout. This is one development-machine observation, not a recognition or cross-machine performance result. The updated interface was visually inspected.

The earlier camera-selection slice passed 169 tests, Ruff, mypy (34 files), both GUI smoke modes and synthetic evaluation. Tests cover selecting a different camera during capture, old-packet rejection, explicit restart after release, invalid indices, busy-loading controls and camera-failure recovery with manual fallback. A Windows-native screenshot at the minimum window size was inspected; vertical scrolling is available. The first verification run found a missing test-double attribute declaration; it was fixed before the clean rerun. Independent code review found no actionable issues; its focused UI suite passed 37 tests. No open PRs were available at the final GitHub check. The user chose to defer live webcam checks.

The persistent-controls and replay slice passes 183 tests, Ruff, mypy (36 files), both GUI smoke modes and synthetic evaluation. Native Windows screenshots at 900x620 logical pixels were inspected at both scroll positions; capture controls and the legend remained visible. A clearly synthetic five-second NEXT hold with 56 total frames produced one protected action with no duplicates, versus 51 baseline requests with 50 duplicates; this is tool validation only. Its trace/report remain local. Independent review identified possible replacement of an existing report; the writer now rejects existing output and publishes exclusively, with regression checks for repeat CLI use and a competing writer. Independent re-review approved the fix with no remaining findings. No new participant, webcam or Windows-launch acceptance is claimed.

The Mac compatibility slice passes 187 tests, Ruff, mypy (36 files), both GUI smoke modes and synthetic evaluation on Windows. Apple Silicon/Python 3.11 wheel resolution was refreshed for all 41 pins; [macos-compatibility.json](macos-compatibility.json) records the target, lock checksum and limitations. Mac setup now runs both GUI smoke modes before reporting success and gives an actionable message if its OS version cannot be read. Studio displays native shortcut labels. The updated Mac guide covers Studio and writes destination checks into ignored local outputs, preserving historical evidence. Actual Mac setup, Cocoa rendering, camera permissions, live transitions and responsiveness remain unverified. The Windows shortcut implementation remains outside the Mac compatibility target. No additional completed-task credit is claimed.

The evaluation-recording slice adds opt-in Studio capture of controller-consumed predictions under ignored `experiments/local/controller-traces/`. It records only labels, acceptance state and monotonic timing, marks new traces `annotation_complete: false`, and preserves buffered evidence if saving fails. Replay now refuses unannotated generated traces before scoring while retaining support for legacy hand-authored traces. This advances GF-P20 tooling only: actual P01/P02/new-participant recordings, independent hold annotations and workflow comparison runs are still future work. No additional completed-task credit is claimed.

The recovery follow-up passed 193 tests, lint, type checks, both GUI smoke modes and synthetic evaluation. Independent review found and then approved a fix for state changes continuing after a trace save failure. Camera/configuration changes, dataset/model replacement and deck reset now preserve the previous selection until saving succeeds. The regression checks failed storage, preserved state and successful retry. These are software checks without new webcam or participant evidence.

The manual-browser integration adds a Studio-only tab for Previous/Next, idempotent bookmarking, bookmark review and explicit removal without loading a recogniser. It reuses Javier's `ViewerWidget`, shares the existing deck and resynchronises after restart. Gesture Preview/Rehearsal still cannot mutate the deck or launch applications; assignment behaviour is unchanged. Independent code/spec and architecture review found no remaining issue. Local verification passes 328 tests with one unsupported symlink fixture skipped, Ruff, mypy, both GUI smoke modes and synthetic evaluation. The first focused run exposed a test that attempted removal after refresh had cleared selection; the corrected test exercises explicit selection and the widget's public controls. Native visual inspection also caught low-contrast default widget colours, which were corrected with scoped dark and focus styles. This advances GF-P10 integration; it does not complete profile/readiness, persistence or Windows-launch acceptance.

The deck-file integration now adds explicit Studio Load deck, Save progress and Restore progress controls using Javier's validated viewer/storage APIs. Position and bookmarks survive an explicit save/reopen/restore for the same deck; restart keeps the loaded deck. Invalid or mismatched inputs, failed trace preservation and failed atomic writes retain the previous content. File operations stay paused, interrupted capture packets are ignored, and imported text remains literal. Independent code review approved the slice and architecture review returned CLEAR after improving recovery when the default save folder is unwritable. Local verification passes 336 tests with one unsupported Windows symlink fixture skipped, Ruff, mypy, both GUI smoke modes and synthetic evaluation. A native Windows check loaded the corporate deck, advanced a card and added a bookmark with capture off. This completes another GF-P10 software slice; full workspace/runbook state, profiles/readiness, actual dispatch and live acceptance remain outstanding. Task completion weights are unchanged.

The workspace/runbook integration adds validated workspace loading, manual Previous/Continue/Finish and stage actions, plus explicit save/restore of matching runbook sessions. Deckless or incompatible-vocabulary contexts stay manual-only; compatible model switches reapply the current stage, and restart returns to the first stage with matching routing. Shared file controls remain available without a deck. Review found and corrected stale restart mappings, empty-workspace model reloads, rejected-import state/status drift and horizontal overflow. A native Windows check at 900x620 logical pixels verified the shared toolbar, persistent footer and manual Continue/Previous while capture stayed off. Gesture Preview/Rehearsal still cannot launch applications or change content. Independent code review approved the repaired slice and architecture review returned CLEAR. Final local verification passed 354 tests with one platform-specific skip, Ruff, mypy (52 files), both GUI smoke modes and synthetic evaluation. At that checkpoint, stage authoring, session summaries, profiles/readiness, guarded dispatch and live acceptance remained integration work. Task completion weights were unchanged.

The runbook-editor and session-summary slice attaches Javier's existing components to Studio. Users can create, edit, delete and reorder stages; accepted changes pause and invalidate gesture routing. Rejected changes preserve the selected stage and typed draft for retry. Manual outcomes, gesture simulations/rejections and explicit stage-completion acknowledgements appear in the summary, with originating context retained across stage changes. Nonempty summaries are archived locally before replacement, restore, restart or normal close; failed preservation blocks the change and retains the current state. Gesture routing also checks summary capacity before consuming an event. The summary scope uses a review UUID, not a content hash or readiness proof; correct/wrong/missed counts remain unmeasured without annotated trials. Independent code review approved the repaired slice and architecture review returned CLEAR. Local verification passed 364 tests with one unsupported Windows symlink fixture skipped, Ruff, mypy (52 files), both GUI smoke modes and synthetic evaluation. A native Windows check at 900x620 verified readable fields, scrolling, the summary and a manual Next outcome with the camera off. README, user guide and integration contracts are updated. Shortcut attachment, profiles/readiness, guarded dispatch and live acceptance remain. Task completion weights are unchanged.

The profile/Quick Actions integration adds reviewed [PR #14](https://github.com/Chi944/GestureForge_304/pull/14) persistence and resolves [PR #15](https://github.com/Chi944/GestureForge_304/pull/15) against current main. Studio now attaches the existing twelve-target library and three gesture slots, persists them privately, and requires explicit **Use Quick Actions** followed by Start/NEUTRAL. Merely opening the tab or reloading targets does not activate routing. Target edits pause before publishing; storage failures retain previous bindings. Manual target tests and gesture requests remain simulations. At that checkpoint, profile selector/enrolment, readiness and real dispatch remained separate work.

PR #15's imported Action selection and preview workspace-replacement fixes are retained. The existing candidate/save/replace transaction is reused; duplicate delivery drafts and the old ZIP are not restored. Javier's updated [4 October checkpoint](JAVIER_OCT4_CHECKPOINT.md) and historical Linux evidence are preserved in canonical documentation locations. Review caught and corrected integer profile-setting hash drift, private-store test leakage, post-close callbacks and type-check failures. Independent code and architecture review accepted the repaired runtime. That checkpoint passed **425 tests with one unsupported Windows symlink fixture skipped**, Ruff, mypy (54 files), both GUI startup modes and synthetic evaluation. The close-event assertion was also strengthened and rerun independently. A native Windows check at 900x620 logical pixels verified reachable target controls, explicit activation and a Calculator preview recorded as **Simulated: 1 / Launch Requested: 0**; the window closed cleanly. No real launch, live-camera performance or native Mac acceptance is claimed.

The saved-profile slice now connects `ProfileStore` to Studio startup and the existing background loader. `--profile-id` uses stored settings; profile names remain separate from IDs. Successful switches stay paused in Preview; failed or deleted-profile retries pause capture and preserve the previous selection. A synchronous prepare/delete/clear handoff removes active or pending deleted profiles without late model resurrection and keeps manual controls available. Hau Jie's selector can reuse these APIs without another worker. Independent review repaired a deleted-profile retry that previously reported pause before actually interrupting capture, then approved the final code and architecture.

PR #16 is merged as `0b55200` after repairs to delayed enrolment samples and capture release during failed-save cancellation. The component's 26 generated-observation tests include both already-failed saves and cancellation-triggered first write failures. At that checkpoint, shared-camera attachment and live recording remained separate acceptance work. Combined local verification passes **460 tests with one unsupported Windows symlink fixture skipped**, Ruff, mypy (57 files), assignment/Studio GUI startup and synthetic evaluation. Documentation links and whitespace checks pass. No real launch, new participant recording or native Mac acceptance is claimed. GF-P02's completed design freeze adds eight original task-weight hours: Deston **21.3%**, team **21.5%**; GF-P06/P07/P10 remain In Progress.

The shared-camera enrolment slice connects Hau Jie's existing widget to Studio without another camera worker or a preloaded classifier. Consent and collection choices are explicit; the first matching observation enables trials after the previous capture releases. Numeric samples stay under ignored `data/local/enrolment`. Collection bypasses classifiers, action routing and prediction traces. Pause, tab changes, focus loss, faults and close retire collection; failed writes retain the trial, block replacement/close and permit retry. Completed manifests are shown in Enrolment without automatic model installation. At 900x620, the compact active form and bottom-aligned preview keep the frame and trial controls visible together. Generated tests and a synthetic preview establish software behaviour only; real recording, profile selection, readiness and native Mac acceptance remain. GF-P07/GF-P10 stay In Progress, so accepted-task percentages are unchanged.

Final local verification of the shared-camera slice passed **478 tests with one unsupported Windows symlink fixture skipped**, Ruff, mypy (58 files), both GUI startup modes and synthetic evaluation. Independent code review approved the implementation and architecture review returned CLEAR. Review repairs include preserving cancellation after failed-save retry, ignoring stale capture requests before pausing, and preventing delayed scroll callbacks from changing a later tab/request. Documentation links and whitespace checks pass. These results do not replace live recording acceptance.

The non-destructive Guest-switch API is implemented as `Window.use_studio_guest()`: it unloads the recogniser, pauses and invalidates capture and preserves saved profiles, datasets and manual workspace state. Failed trace/enrolment preservation and busy model loading refuse the switch. Six focused regressions include real generated profile files remaining byte-identical and reloading through the background API after Guest. Full local verification passes **484 tests with one unsupported Windows symlink fixture skipped**, Ruff, mypy (59 files), both GUI startup modes and synthetic evaluation; independent code and architecture reviews approve the slice. At that checkpoint these were Windows software checks without a visible selector walkthrough: the selector was absent from published branch `57d6f5f`, and publication was needed for attachment. The following PR #17 slice supersedes that blocker.

The profile-selector slice attaches Hau Jie's [PR #17](https://github.com/Chi944/GestureForge_304/pull/17) to Studio's **Profiles** tab using the existing profile store and background loader. Creation, load, cosmetic rename, confirmed metadata deletion and non-destructive Guest selection share the paused shell lifecycle. The configured `--profile-store` is honoured. Profile loading does not start the camera or grant readiness; Preview requires an explicit start and matching installed profile/model. Concurrent profile work blocks conflicting changes before publication, and owned installation can restore the active runbook or Quick Actions context.

A native Windows workflow at 900x620 logical pixels used generated data to create separate kNN/SVM profiles, rename without replacing the model, switch to Guest without changing saved files, close/reopen and independently reload both profiles, delete one while preserving the other and source data, and reload the survivor. The compact form and wrapped permission text were visually inspected. This completes GF-P06's software acceptance with Guest/manual fallback; no approved starter is supplied. Live recognition, recording and readiness remain separate. GF-P06 adds ten original task-weight hours: Hau Jie **20.0%**, team **26.0%**; Deston **21.3%** and Javier **37.0%** are unchanged.

PR #17 also adds descriptive saved-baseline diagnostics for GF-P11: invalid detections, accepted/rejected positives, wrong labels and accepted UNKNOWN poses are reported separately. Review repaired overflow in finite ratio summaries and prevents serialization errors from leaving a partial output. This does not fit, tune or improve a model. GF-P11 is In Progress until a bounded train-only rejection comparison records baseline/candidate results and a selected configuration or explicit no-qualifying result.

Final local checks for the selector integration pass **522 tests with one unsupported Windows symlink fixture skipped**, Ruff, mypy (64 source files), assignment/Studio startup and synthetic evaluation. Independent code review approves the combined changes and architecture review returns CLEAR. Immediate and queued enrolment starts are blocked during profile work, with both pending widget and host state cleared for retry. Documentation links and whitespace checks pass. These checks do not establish new participant recognition, native Mac or desktop-launch acceptance.

## Current integration â€” short readiness and PRs #18/#19

Studio now scores two protected simulated activations for each enrolled action pose, with neutral rearming and zero wrong actions. UNKNOWN-only/incomplete attempts fail. Its session-local behaviour revision expires after model/profile/mapping/target changes; stage selection and cosmetic names preserve a completed result. It uses the existing capture/controller path, restores the previous context paused and records measured trial outcomes separately from manual actions. This is the short check, not GF-P12's longer personal rehearsal or final recognition evaluation. GF-P10 remains In Progress because the original standard Guest/Try Now entry still lacks an approved starter.

[PR #18](https://github.com/Chi944/GestureForge_304/pull/18) adds Javier's [reported laptop-A observations](../evidence/WINDOWS_RESULTS_2026-10-02.md) and fixes pending launch confirmation and missing-target evidence. Review corrected routing-pause versus camera-shutdown wording and a Windows escaped-path assertion. The additional `e111942` rerun records refused failed-launch confirmation, persisted missing-target failure and successful restored-target confirmation/recovery. Independent acceptance review credits GF-P05 against its original target-type, error and camera-handoff criteria using this supplied observer evidence; the native run was not independently repeated here. This adds five task-weight hours: Javier 43.8%, team 31.8%. Isolated focus-loss and broader two-laptop integrated checks remain in GF-P19.

[PR #19](https://github.com/Chi944/GestureForge_304/pull/19) completes [GF-P11's bounded comparison](GF_P11_BOUNDED_COMPARISON.md). Hau Jie reports zero qualifying configurations in all three folds. Local software review verifies the selection protocol; private experimental measurements were supplied by Hau Jie and not rerun here. Review repaired shared input-snapshot provenance, preserved pre-existing SVM profile revisions, and prevents serialization errors leaving a new partial report. Library versions remain recorded even when no candidate qualifies. This completes the experiment, not a starter release: Hau Jie 30.7%. Together with GF-P05, team completion is 31.8%, ten tasks Done.

## Previous verification checkpoint

The short-readiness integration passes **551 tests with one unsupported Windows symlink fixture skipped**, Ruff, mypy (68 source files), both GUI startup modes and synthetic evaluation. Independent code and architecture reviews cleared recovery, cosmetic revision preservation and Enrolment interruption. A native Windows layout check at 900x620 confirmed the expected-pose prompt stays visible while the content scrolls. Command event IDs now use bounded UUIDs so saved-profile identities cannot exceed dispatcher/summary identifier limits. These are software and layout checks; live readiness and native Mac acceptance remain separate.

## Current integration â€” shared dispatcher and manual LIVE

Studio reuses Javier's existing dispatcher for typed manual viewer, runbook and Quick Actions requests, and for gesture simulations. Preview/Rehearsal simulate every typed request. Explicit **Live (manual controls)** enables manual deck changes, stage advancement and validated Windows targets without a recogniser. One persistent event ledger survives profile, workspace and summary changes. Camera launch requires acknowledged capture release; preservation or release failures open nothing and require a fresh manual request. Stage transitions remain paused with no deferred replay.

This advances **GF-P16 to In Progress**. It deliberately keeps LIVE camera Start and gesture dispatch blocked: GF-P12 requires ten trials per pose plus ten negative/transition intervals, and the short six-activation check cannot substitute for that protocol. No full task is newly accepted, so the percentages above remain unchanged. Windows launch observation, live recognition and native Mac acceptance are separate from automated software checks.

Final local verification passes **564 tests with one unsupported Windows symlink fixture skipped**, Ruff, mypy (69 source files), assignment/Studio startup and synthetic evaluation. Independent code review approves the final slice and architecture review returns CLEAR. Review repaired shortcut-label lookup, the footer's bypass of simulation, stage pause state and misleading mode/log messages. Regression checks cover acknowledgement failure/retry, retained duplicate IDs, capacity/preservation guards and the longer-readiness boundary. A native Windows UI check at 900x620 confirmed Preview leaves the deck unchanged, manual LIVE advances and bookmarks with capture off, and the layout has no horizontal overflow. External-launch tests use fake adapters; no new native target or webcam acceptance is claimed.

## Current integration â€” runbook recovery and Studio handoff

The latest integration fixes preserve the active deck/runbook context when a local resource is repaired; explicit standalone Quick Actions still requires reactivation after edits. Failed **Test selected target** validation now enters the session summary with a bounded reason and no private path/form text. LIVE instructions describe manual launches correctly. The six-stage Harbor regression covers Guest/manual actions, missing-target recovery, context attribution, bookmarks, paused save/reload and no replay through a fake launcher. Follow the [manual Windows walkthrough](DEMO_SCENARIO.md#manual-walkthrough-available-now) for actual opening and task observations.

`scripts/package_release.py --project` prepares a separate development Studio ZIP and checksum/source-state manifest, preserving the assignment archive names. It carries tracked source and assets without private samples/profiles or Word documents. This advances handoff preparation, not GF-P23's fresh-machine/stability acceptance or GF-P27's final submission. No additional full task is accepted; percentages above are unchanged.

Local verification passed **570 tests with one unsupported Windows symlink fixture skipped**, Ruff, mypy (69 source files), both startup modes and synthetic evaluation. Review then corrected an unavailable Git-status result being reported as clean: the final packaging check passes **13 tests**, including that new regression, and full-repository lint/types pass again. Both independent review lanes approved the final change. These checks use fake launch adapters and generated fixtures, not new native launches, webcam observations or participant measurements.

## Current integration â€” PR #20 camera handoff

[PR #20](https://github.com/Chi944/GestureForge_304/pull/20) is merged at `494e904`. It records partial Hau P02 physical evidence from older `878b1ff`, including completed recordings/reload, while Stop during mid-hold, invalid feedback and current-head hardware recording remain unverified. The shared-camera fix now loads MediaPipe model bytes through `model_asset_buffer`; native Windows MediaPipe 1.0.1 failed on a model filename containing Chinese characters through the old filename API, while the same bytes succeeded through the buffer path. `check_environment.py --model` also succeeded from a copied Chinese project folder, so the earlier `get_runfiles_dir_helper.cc` fatal is still not reproduced or resolved as a current-main defect.

Windows setup now requires a blank-image native model check before success. For the reported fatal, the documented recovery is a fresh source copy under an ASCII-only writable destination such as `C:\GestureForge`, fresh setup and no copied `.venv`, keeping the original folder and private files intact. No new camera/device acceptance or Mac claim is added. Percentages above are unchanged. This checkpoint preceded PR #21's GF-P12 delivery; the remaining Enrolment observations are still needed independently of the rehearsal component.

Local verification of this fix passes **573 tests with one unsupported Windows symlink fixture skipped**, Ruff, mypy (70 source files), both startup modes and synthetic evaluation. Real blank-image inference also passes with the model and check script beneath a Chinese project folder. Independent code and architecture reviews approve the runtime change; [verification.json](verification.json) records the bounded checks. The original fatal runtime error still needs a retest on Hau Jie's laptop.

## Current integration â€” NEUTRAL rearming feedback

Hau Jie reported intermittent open-palm/LATCHED behaviour. Inspection and controlled prediction replay show accepted fresh NEUTRAL immediately leaves LATCHED and reaches READY after the existing continuous 300 ms hold. Classifier rejection deliberately keeps LATCHED to prevent repeat actions. A screenshot without the current prediction cannot identify the physical report's cause; it remains open for a short current-version trace plus independent intended-pose notes.

Two feedback defects are fixed: the prediction and rejection explanation now remain in Studio's fixed footer, and fresh accepted packets clear stale controller error text. LATCHED shows the neutral-rearm instruction and an empty bar; accepted NEUTRAL displays hold progress and READY displays the next step. Pause/restart clears the old prediction. These changes preserve rejection settings, hold durations, identity/timing guards and the LIVE-gesture gate. Regression tests reproduce rejected-to-neutral recovery without duplicate actions and verify feedback stays visible while scrolling. The updated member briefs separate Hau Jie's recognition/rehearsal work from Javier's integrated Windows action checks; both can continue on their own branches.

Local verification passes **576 tests with one unsupported Windows symlink fixture skipped**, Ruff, mypy (70 source files), both startup modes and synthetic evaluation. The full check caught and repaired a generic pause message overwriting Enrolment guidance; 23 focused Enrolment/rearm/packet checks passed before the final rerun. Independent code review approves and architecture review is CLEAR. A generated-prediction Qt render at 900x620 verifies visible feedback and no horizontal overflow; it is not a live camera test.

No additional task is fully accepted by this bounded fix, so completion percentages remain unchanged. Live reproduction and native Mac validation remain separate from software verification.

## Current integration â€” PR #21 personal Practice

PR #21 supplies the longer measured rehearsal, reviewed and attached as an embedded Practice tab. It reuses the existing camera worker, routing controller and persistent dispatcher; fifty prompted five-second windows record actual protected simulated actions and capture coverage. The sequence includes ten trials for each enrolled action pose and NEUTRAL, followed by ten negative/transition intervals. It preserves local results, restores the previous context paused and keeps storage failures recoverable. The short six-activation check remains separate; no Practice result enables LIVE gestures.

Local verification passes **615 tests with 1 unsupported Windows symlink fixture skipped**, Ruff, mypy (76 source files), both GUI startup modes and synthetic evaluation. Independent code and architecture reviews approve the repaired component and host integration. Generated Qt renders at 900x620 and 1100x850 were inspected for prompt/control visibility and horizontal overflow. No new physical participant run or native-platform acceptance is claimed. GF-P12 moves to In Progress; all completion weights and percentages remain unchanged.

## Current integration â€” historical Practice review and workflow comparison

Deston's shared-shell work closes GF-P31's remaining software gap: Session summary
now retains the latest saved Practice result, its original behavior/scope and a
frozen set of dispatcher outcomes. It distinguishes recorded and completed
windows, per-pose and negative outcomes, unattempted windows and coverage gaps.
Exact session/event/model/context/action matches reconcile simulated requests;
missing, duplicate, mismatched and unexpected events remain visible. Save failure
does not publish a saved review. Reset/profile changes retain explicitly
historical evidence. The existing summary export and separate private Practice
JSON retain their own formats; no LIVE permission is granted.

Independent acceptance review accepts GF-P31 against its original software
criterion, after independent code APPROVE and architecture CLEAR. The original
6-hour task weight stays with Javier; this completion includes Deston's host
integration and does not attribute all work to one member. Team completion rises
from 31.8% to 34.5%. GF-P12 participant evidence and GF-P19 native Windows evidence
remain separate. Deston's percentage is unchanged because GF-P20 includes real
study execution, not only building its tools.

`scripts/compare_workflows.py` validates bounded observer input and actual Harbor
SessionSummary exports, hashes their exact bytes and preserves per-condition
segment provenance. Unavailable recognition, withdrawal, manual fallback, help
and late timeouts remain reportable. Readiness, simulation and source mismatch
prevent an unsupported condition-success claim; paired times require the same
participant, source, workspace and environment. Duplicate exports or competing
output writes cannot silently overwrite or double-count evidence. See
[WORKFLOW_COMPARISON.md](WORKFLOW_COMPARISON.md) for the exact fields and a clearly
synthetic example. No participant outcomes were collected by this change.

The full local verifier passes **634 tests with one unsupported Windows symlink
fixture skipped**, Ruff, mypy (78 files), both GUI startup modes and synthetic
evaluation. The guide's synthetic example also passes a real CLI invocation with
zero invented success and exact input hashing. Generated Qt review renders were
checked at 900x620 and 1100x850. A final wrapped-text sizing fix passed **169
affected/adjacent tests**, full lint/types and both startup checks; final verification is recorded in
[verification.json](verification.json). Local checks remain separate from webcam,
native external launch, independent installation and native Mac acceptance.

## Current integration â€” Practice timing, guidance and native dispatch (4 October)

PR #22 adds Hau Jie's countdown, latest-trial Begin diagnostics and attributed
physical partial-slot Stop evidence. It closes that specific Stop evidence gap;
the short collection/profile workflow recording and full fifty-window Practice
remain separate. The integration fixes conflicting READY footer instructions,
preserves explicit interruption reasons, and protects saving after an invalid
Begin timestamp. Recorded Practice guidance now separates missed/wrong/repeated
commands, rejection-frame evidence, incomplete capture and unattempted windows.
Reconciliation anomalies block pose advice until the evidence is resolved.

An automated native Windows Harbor run at `b44df9a` passed 124 assertions with
zero failures. Four real OS open calls were accepted (Calculator, fictional TXT,
resource folder and recovered disposable TXT), with matching visible-window
metadata. Missing-target failure, an explicit retry, idempotent bookmark, paused
save/restore without launch replay and terminal navigation were exercised.
The ignored `experiments/local/harbor-automated-20261003T160810Z/` holds the own-app
screenshots, raw exports and detailed method. All task acknowledgements and
measured-trial counts remained zero: this is automated native dispatch evidence,
not presenter task completion, gesture performance, independent installation,
Camera handoff or Mac verification. No saved real Practice result was found on
Deston's machine. No additional complete-task weight is claimed.

Final local verification passes **672 tests with one unsupported Windows symlink
fixture skipped**, Ruff, mypy (80 source files), both GUI startup modes and
synthetic evaluation. Independent code review approves and architecture review
is CLEAR. An intermediate Qt teardown failure was reproduced and repaired by
preserving the existing no-argument pause callback; its failed run remains only
in local diagnostics. Generated Practice renders at 900x620 and 1100x850 passed
six checks for instructions, review text height and horizontal scrolling. These
are software/layout results; the physical Practice trial is deferred at Deston's
request.

## Practice follow-up â€” P01 live check and one-pose diagnostics (4 October)

Deston completed an assisted P01 check on `a738c0a` using the existing pilot
recogniser. The latest attempt recorded correct, covered NEXT and PREVIOUS
windows with exactly one simulated event each. BOOKMARK preparation stopped
before Begin with the old combined invalid/stale-packet message. Earlier
attempts also include a successful NEXT and a preparation timeout. Private
results are retained unchanged. These are partial familiarisation results, not
a completed fifty-window rehearsal, held-out accuracy or LIVE permission.

PR #23 adds a separately labelled single-pose diagnostic using the existing
capture, controller and simulated dispatcher. Host review now distinguishes its
one-window scope from a full rehearsal and leaves other poses/negatives not
assessed. The setup repair adds Open Practice, fixes initial/loading/Guest status,
and preserves diagnostic messages. Late but otherwise valid packets during
preparation reset neutral arming without extending the 30-second deadline or
receiving score. Armed/measured, malformed and out-of-order packets still fail;
the 200 ms freshness limit is unchanged. New local timing diagnostics identify
the validation condition. This repair addresses a reproduced software path;
the old generic P01 record does not establish which condition caused its stop.

Local verification passed 704 tests with one unsupported Windows symlink fixture
skipped. After annotation/test-fixture corrections, all 105 affected Practice
tests, Ruff, mypy (80 source files) and both startup modes passed again. Synthetic
evaluation and eight generated layout checks also passed. These generated checks
do not establish physical webcam acceptance. Evidence is in `verification.json`. Physical
retesting of BOOKMARK/NEUTRAL and the complete rehearsal remain. No additional
task is Done: Deston 21.3%, Hau Jie 30.7%, Javier 52.1%, team 34.5%.

## P01 BOOKMARK diagnostic follow-up (4 October)

On `d1b68e7`, the assisted P01 pilot diagnostic completed a five-second BOOKMARK
window with 45 measured frames, no recorded rejections and exactly one simulated
BOOKMARK action. Begin was accepted from READY. The result is **inconclusive**:
capture failed the existing 200 ms boundary/gap coverage requirement. The old
export does not retain individual boundary/gap values, so it cannot identify
which part of coverage failed. A recovered 219 ms late preparation packet
occurred before Begin and does not establish the measured-window failure cause.
The separate stopped attempt had no Begin and no recorded trials. Preserve both
results; neither is a full rehearsal pass or LIVE-gesture acceptance.

Normal Studio close archived the matching Session summary. Reconciliation found
one expected and one matching simulated event, with zero missing, duplicate,
mismatched or unexpected events and zero launch requests. The BOOKMARK event
occurred 1.000 seconds after Begin. This confirms the simulated command record,
not capture coverage or a measured stable-pose latency target.

The user reported excessive black preview space and awkward scrolling. The
camera shared a scrolling container with tall workflow content, allowing the
preview to grow beyond the visible area. This follow-up addresses layout and
capture diagnostics; it does not change recognition thresholds or coverage rules.
No additional complete-task weight is claimed.

Studio now keeps the preview and capture controls outside the right workflow
scroller. Setup uses narrow-panel rows, while the active tab determines scroll
height. Resizing preserves every camera-frame corner; long saved results grow
and shrink with their text and remain reachable at the bottom. The separate
assignment window retains its existing layout. New Practice trial exports record
first-frame, largest interframe and end gaps; diagnostic guidance displays those
measurements without rescoring older results or weakening the 200 ms limit.

The full suite passed **716 tests with one unsupported Windows symlink skip**
before the final layout refinements. The final revision passed **225 affected
UI/Practice tests**, Ruff, mypy (81 source files) and both GUI startup modes;
synthetic evaluation also passed. Review caught and corrected long-result
clipping, stale text-height sizing and narrow Setup rows. Test fixtures now load
the existing Windows font for offscreen text measurements and avoid assuming
the old three-column file grid. Sixty generated camera/workflow checks and a
final 42-control Setup text-fit check passed at 900x620 and 1150x740. Independent
code review approves; capture-diagnostic review is clear. These are software and
layout checks, not another physical webcam trial. Actions remains manual-only.

## 4 October - recovery while waiting for Begin

On `965edb8`, bounded P01 BOOKMARK and NEUTRAL diagnostics completed correctly
with valid capture coverage. A later full attempt completed five correct,
covered windows (NEXT, PREVIOUS, BOOKMARK, NEUTRAL, NEXT), then cancelled in
the sixth window's armed phase before Begin. Its saved capture diagnostic
records an otherwise valid 203 ms-old frame against the 200 ms freshness limit;
there were no measured frames or commands in that interrupted window. This
identifies a premeasurement lifecycle problem, not a recognised-gesture miss.
The original result remains local and unchanged. An earlier separate NEUTRAL
diagnostic stopped during measurement on a 218 ms-old frame; that remains a
capture-timing limitation and is not resolved by pre-Begin recovery.

Recovery now treats preparing and armed-before-Begin consistently. It discards
the stale input, returns to preparing with a fresh NEUTRAL requirement, keeps
the same camera and completed results, and preserves the original 30-second
deadline. It records the original armed phase and advances ordering checks
without counting the dropped packet as measured evidence. Malformed/out-of-order
packets and measured-phase stale input still cancel. No thresholds, scoring,
readiness permissions or historical participant results were relaxed. A cancelled
old attempt cannot be resumed under this revision or combined into a new pass.

The host regression reproduced this exact failure after five completed windows
before the correction; the normal control case passed. Final verification passed
**723 tests with 1 unsupported Windows symlink skip**, Ruff, mypy,
both GUI startup modes and synthetic evaluation. Both normal and recovered
50-window host regressions pass; independent code review approves. Raw check
outputs, source hashes and review scope are recorded in `verification.json`.
Physical acceptance of the updated full protocol remains open; no completed-task
weight is added.

## Measured-window interruption correction â€” 4 October 2026

The next P01 attempt on `39b260c` recorded eight covered windows: seven correct
and one NEUTRAL miss. It then cancelled in window nine when an otherwise valid
frame arrived 218 ms after capture. The old result is retained locally unchanged;
the source of that processing delay is not established by the saved packet age.

The v2 Practice protocol drops stale measured packets without dispatching an
action, preserves all earlier results and finishes the current five-second
window as inconclusive. The same attempt can then continue through all 50
windows. Any inconclusive window prevents a full pass. Timing/order guards,
the original timer and safety interruptions remain; no recognition thresholds
or historical scores are changed. Saved per-window diagnostics retain the stale
count and maximum age after later windows. Historical v1 exports remain readable.

The full-host regression reproduced the ninth-window cancellation before the
correction; the normal and pre-Begin recovery controls passed. Final verification
passed **728 tests with 1 unsupported Windows symlink skip**, Ruff,
mypy, both GUI startup modes and synthetic evaluation. Independent review
found no blockers. Check outputs, source hashes and regression scope
are recorded in `verification.json`. Physical acceptance of this revision
still requires a fresh run. Accepted-task weights are unchanged.

## Practice setup continuity and compact controls â€” 4 October 2026

The latest P01 attempt on `aaef21a` completed NEXT and PREVIOUS correctly,
recorded a covered BOOKMARK miss, then hit the 30-second setup timeout before
the first NEUTRAL window. The latest Begin request was rejected at 218 ms frame
age. Its private result is unchanged; the BOOKMARK miss is separate from the
setup defect and no recognition threshold was changed.

Practice v3 queues an explicit Begin click for at most two seconds, retaining
all capture/READY guards. A setup timeout pauses capture and offers Retry setup
on the same prompt; separate saved setup-retry records earn no trial credit.
The existing v2 measured-frame policy continues: late frames make that window
inconclusive while the attempt continues. Four complete generated host runs
cover normal operation, stale setup, late measurement, and the combined latest
setup/Begin problem. The compact controls and dark tab arrows/scrollbars were
rendered and tested at 900x620 and 125% scaling. Cues open in a separate dialog.
Final verification passed **734 tests with one unsupported Windows symlink skip**,
Ruff, mypy (81 files), both GUI startup checks and synthetic evaluation. Independent
review approved; source hashes and regression scope are in `verification.json`.
Physical acceptance is not established by these checks. Task weights remain
unchanged; no additional participant recording is requested during software repair.

## Next deliverables

GF-P23 has moved from Backlog to In Progress for release-test tooling. The
new bounded capture diagnostic reuses the existing worker and optional personal
classifier, reports aggregate timing/memory/shutdown, and saves one private JSON
without frames or prediction history. It requires no new environment, model or
participant collection. The [guide](../USER_GUIDE.md#capture-stability-diagnostic)
separates this pipeline check from full Studio, thirty-minute and second-machine
acceptance. The original task weight and Done criteria are unchanged.

On 4 October, an unattended native Windows run used the existing P01 classifier
and camera index 1 for 60.016 seconds. It delivered 1,040 packets (17.329 Hz),
observed two packets older than 200 ms (maximum 219 ms), skipped one frame ID in
the latest-only mailbox, and shut down cleanly without a capture-worker error.
Peak process working set was 360,407,040 bytes; the private JSON was 3,145 bytes.
This confirms a short pipeline run with timing warnings, not a clean timing
qualification, gesture accuracy, completed Practice or thirty-minute Studio
acceptance. The raw result remains local and unchanged. No new training samples
or images were stored, and no additional participant rehearsal was requested.

The previous local verification checkpoint passed **752 tests with one unsupported Windows symlink
skip**, Ruff, mypy (83 files), both GUI startup modes and synthetic evaluation.
The new diagnostic has 18 focused regressions; independent review approved after
fixing receive-time sampling and duration-boundary fault detection. Exact
software outputs and the separately labelled native summary are retained in
`verification.json`. No completed-task weight is added by these preparatory checks.

**Current software repair checkpoint:** Studio action mode and Apply now appear
at the top of Setup, before dataset/camera/readiness controls. The dataset loader
rejects non-dataset JSON with workspace/deck loading guidance and separately
reports a dataset with no valid TRAIN samples. Existing P01 pilot and session-1
data both loaded in compatibility checks; the primary open Studio application
also loaded P01 pilot successfully. This confirms loading only, not recognition
quality or readiness. The wrong-file defect does not require new gesture data.
Full verification passed **772 tests with one unsupported Windows symlink skip**,
Ruff, mypy (83 files), both GUI startup modes and synthetic evaluation. Independent
review found no code blockers; its stale walkthrough direction was corrected.
Exact outputs and source hashes are in `verification.json`. No completion
percentage changes.

**Delegated acceptance after software verification:** Javier executes the
[camera-free Harbor walkthrough](DEMO_SCENARIO.md#manual-walkthrough-available-now)
and Windows device/launch/recovery/offline evidence. Hau Jie checks existing
personal data/profile compatibility and short focused recognition before a full
Practice attempt. Deston keeps interface design, integration and final review.
This delegates execution within existing tasks; it does not transfer backlog
accountability, change original weights, mark work Done or request new recordings
from Deston. Automated launch/window observations cannot supply human task
acknowledgements.

- **Hau Jie:** sync the reviewed fixes into `codex/hau-jie-profiles` and follow the [individual handoff](HAU_JIE_HANDOFF.md). Preserve GF-P11's no-selection result, PR #22's partial-slot evidence and all private inputs/results. Check existing personal manifest/profile compatibility, reliable load/start and fresh capture; then use short pose/NEUTRAL diagnostics with intended-pose notes. Attempt full GF-P12 Practice only after setup is reliable, keeping misses and inconclusive windows. Diagnose before changing thresholds or requesting narrowly targeted repair data; no blanket rerecording.
- **Javier:** sync the reviewed fixes into `codex/javier-shortcuts` and follow the [individual handoff](JAVIER_HANDOFF.md). Execute camera-free Harbor, retain both summary segments around reload, then gather remaining GF-P19 Windows launch/focus/Camera recovery evidence on both laptops and GF-P23's fresh-install/offline evidence for Deston's review. Preserve accepted GF-P05 results. Report actual outcomes and unrun cases separately; do not duplicate the shared shell or Practice reconciliation.
- **Deston:** complete software integration and verification, then review the evidence supplied by Javier and Hau Jie against the existing acceptance criteria. Retain design, routing safety, final acceptance and release decisions. A successful load, simulated result or delegated task is not LIVE-gesture permission or a completed acceptance gate.

Use [TEAM_GUIDE.md](TEAM_GUIDE.md) and the individual briefs for file ownership, test expectations and PR rules. Teammates push their own branches; Deston reviews and merges into main. Move cards to Done only with linked acceptance evidence.
