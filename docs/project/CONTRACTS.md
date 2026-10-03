# Shared project routing contract

Project contract version 1 | Design frozen 2 October 2026 | Owner Deston

This is the version-1 integration baseline. Legacy dataset schema 1 and custom-vocabulary schema 2 share `FEATURE_VERSION=1`; legacy labels and the NEXT-only default controller remain compatible. `PROJECT_CONTRACT_VERSION=1` versions the routing types separately. Studio integrates workspace/runbook editing and persistence, session summaries, Quick Actions, shared-camera enrolment and Profiles. One persistent dispatcher handles typed manual requests and gesture simulations. Explicit LIVE mode enables manual actions; LIVE gesture control remains blocked pending measured personal acceptance and the reviewed readiness gate. Standard starter availability remains separate work.

## GF-P02 design freeze - 2 October 2026

Deston's integration baseline adopts the approved [project plan](PROJECT_PLAN.md) and [screen/transition design](TEAM_GUIDE.md#initial-screen-design): Try standard gestures first, optional Personalise, and exactly one typed action per bound stage slot. Reviewed merged PRs #10, #14 and #15 supply the vocabulary, profile and workspace/component interfaces below. Independent acceptance and architecture review reconciled these handoffs with the implementation. This records the approved design and its adoption in reviewed code; it does not claim a separate team meeting or tutor approval.

The final flow is **Try standard gestures -> simulated readiness check -> explicit Start/NEUTRAL -> eligible control**. A failed check offers retry, optional Personalise or manual controls. An unavailable starter shows its reason and preserves manual access. Saved profiles may be loaded without collecting again; loading alone never proves readiness. Preview/Rehearsal can run before readiness. The implemented six-activation check does not satisfy GF-P12's longer personal protocol: LIVE gesture Start and dispatch remain blocked. Manual typed actions simulate in Preview/Rehearsal and execute only after explicit LIVE selection, without requiring a recogniser. This design freeze does not complete starter evaluation, readiness or hardware acceptance.

## Records and responsibilities

| Record | Meaning |
|---|---|
| `Observation` | Existing capture identity, frame/time, hand count/handedness, landmarks and validity |
| `Prediction` | Session/profile/frame/time, canonical gesture label, accepted flag, model version and rejection reason |
| `CommandEvent` | A deliberately held gesture, its identity/time and unique event ID; trailing model_version added with legacy default |
| `Action` | One typed semantic action; only OPEN_SHORTCUT has a shortcut_id |
| `RoutingSnapshot` | Immutable session/profile/model/context identity, copied bindings and mode |
| `RoutingResult` | event_id plus real action, simulated_action, or rejection_reason |

Action types are NEXT, PREVIOUS, BOOKMARK, ADVANCE_STAGE and OPEN_SHORTCUT. Bindings are one to three gesture IDs mapped to `Action` records. IDs are case-sensitive `[A-Z][A-Z0-9_]{0,63}` with NEUTRAL and UNKNOWN reserved. A profile has three action classes plus NEUTRAL, while a context may bind fewer. The current coordinator requires at least one binding; an empty/unbound screen uses manual controls and keeps routing absent/paused.

Other opaque IDs are 1â€“64 ASCII letters/digits and `_ . : -`, beginning with a letter/digit. Display names and target paths are separate values. The shortcut ID is never a URL or executable path. Actual target validation belongs to Javier's local registry/dispatcher.

## Builder handoff records

These are logical handoffs, not a request for four new Python record classes. Hau Jie owns profile/readiness storage and widgets; Javier owns shortcut storage and component widgets; Deston owns the shell handoff and final acceptance. The table names actual counterparts. The short readiness scorer lives in the shared shell; Hau Jie retains ownership of the longer personal rehearsal protocol.

| Handoff | Required fields | Version and loading rule |
|---|---|---|
| `profiles.ProfileSelection`, from `LoadedProfile.selection` | `profile_id`, `display_name`, `selected_hand`, `vocabulary`, `model_version`, `readiness_revision`, `readiness_reason` | Schema 1. Metadata alone cannot install a recogniser: the shell needs the complete `LoadedProfile` candidate. Validate before replacement; corrupt or incompatible loads leave the previous profile/model active and paused. |
| Workspace selection, implemented by `workspace.Workspace` | `id` (workspace identity), `title`, optional `deck`, semantic `shortcuts`, ordered `stages` | Schema 1. There is no separate `WorkspaceSelection` class or stored `workspace_revision` field. Validate the complete value before replacement. The short readiness revision binds to all authored action meanings; navigation/session revision IDs are not readiness proof. |
| Runbook context, implemented by `workspace.Stage` and `runbook.Runbook` | `id` (stage/context identity), title/instructions, optional `card_id`, zero to three typed `bindings`; runbook owns continue/finish state | `Window.reset_runbook_stage(stage, resume)` applies the complete context. Empty stages stay manual-only. Other transitions clear holds and require NEUTRAL; selecting an already configured stage does not itself change the authored binding revision. |
| `readiness.ReadinessCheck` and shell-held pass revision | `revision`, `status`, `reason`, expected pose, completed count and measured `Trial` records | Session-local; no saved readiness credential. `behavior_revision` hashes profile/model/hand, feature version, controller policy, authored bindings, all workspace stage/Quick Actions mappings and local target meanings. Model revision already binds training data/settings. Behaviour changes expire a pass; cosmetic names and stage position do not. |

Atomic save means write a new validated file, replace the old file only after the write succeeds, and keep the last working file available after failures. Loading must never partially replace an active profile, workspace, runbook or binding map.

Portable workspace exports include deck text, runbook instructions, semantic shortcut slot IDs/labels and action mappings. They exclude local executable/file/folder paths, URLs, credentials, personal profiles, training samples, model files, raw video, full sensitive target paths, event logs and generated local evidence. Each computer binds and tests its own local targets.

Data limits are shared: one profile vocabulary has exactly three action gesture IDs plus NEUTRAL; an active gesture context binds one to three gestures; a manual-only screen has no active routing; one gesture maps to one `Action`; a runbook has at most twelve stages; a local shortcut library has at most twelve targets; a deck is optional for Quick Actions and optional for a runbook stage unless that stage references a card.

## Widget handoff signals

Use plain PySide signals or direct method calls carrying these records; do not create separate application shells or camera workers.

| Producer | Signal or call | Shell response |
|---|---|---|
| `ProfileSelectorWidget` (Profiles tab) | Request load by `ProfileStore` and opaque profile ID; publish selection only after successful installation | Shell owns saved-model reconstruction and installs a complete `LoadedProfile`; creation fits in the component's background worker. Busy notifications serialize competing setup operations. Metadata-only `ProfileSelection` is for display. Deletion clears a matching active or pending selection through the shell; Guest unloads without deleting storage. |
| `EnrolmentWidget` | `capture_requested(plan, request_id)`, `capture_release_requested(request_id)`, `dataset_saved(path)` | Shell pauses actions, retires the previous worker and starts observation-only capture. First matching observation acknowledges readiness to collect. Completion reports a private manifest, never model installation or readiness. See [enrolment handoff](ENROLMENT_INTERFACE_PROPOSAL.md). |
| Studio readiness controls | `start_readiness_check()` / `finish_readiness_check()` | Temporarily route all three poses through simulation with the existing camera/controller, then restore the previous context paused. Only protected simulated gesture events count. Passing this short check does not enable LIVE gestures. |
| `WorkspaceWidget` / `RunbookEditorWidget` | `workspace_changed(Workspace)` | `accept_workspace_widget_change` / `accept_runbook_editor_change` pause and validate before replacing content. Imported targets remain semantic references. |
| `RunbookWidget` / `Runbook` | `action_requested(Action)`, `previous_stage_requested()`, `completion_acknowledged(stage_id)`; runbook callback `(Stage or None, resume)` | `reset_runbook_stage` applies the complete map and invalidates holds; viewing a tab does not activate it. |
| `QuickActionsWidget` | `before_publish() -> bool`, then `bindings_changed(...)` after successful local save | Pause before mutation; failed save preserves the registry. Clear active routing and require explicit Use Quick Actions. Changed action meanings expire the short readiness result. |

## Minimal use

```python
from gestureforge.contracts import Action, ActionType, Prediction, RoutingMode
from gestureforge.routing import RoutingSession

session = RoutingSession(
    "trainer", "model-v2", "stage-1",
    {"G1": Action(ActionType.NEXT),
     "G2": Action(ActionType.OPEN_SHORTCUT, "calculator"),
     "G3": Action(ActionType.ADVANCE_STAGE)},
    mode=RoutingMode.PREVIEW,
)
snapshot = session.resume()
# Stamp every capture/prediction with this snapshot's identity and model revision.
prediction = Prediction(
    snapshot.session_id, snapshot.profile_id, 1, 0.0,
    "NEUTRAL", True, snapshot.model_version,
)
event = session.process(prediction, now=0.0)
if event is not None:
    result = session.route(event, now=0.0)
    # Default PREVIEW returns simulated_action, never action.
```

Use monotonic capture timestamps and increasing frame IDs in real operation. The single neutral sample above does not arm the controller. Hold NEUTRAL for 300 ms and then a mapped pose for 400 ms, supplying fresh observations with gaps no greater than 200 ms. Existing rejection grace and tracking-loss behaviour remain in the tested controller.

## Lifecycle and dispatch rules

`RoutingSession(profile_id, model_version, context_id, bindings, mode=PREVIEW)` starts PAUSED. Read `snapshot`, `state`, `progress`, `last_error`; do not access its private controller. Call `fault(reason)` on camera failure to pause and invalidate issued events.

`configure(...)` takes the same complete arguments, validates before replacing state, creates a fresh session and pauses. Any profile, model, workspace, context, mapping or mode change goes through it. Explicit `resume()` creates another fresh session and WAIT_NEUTRAL; `pause()` cancels issued work. Deston's shell must restart or restamp capture against the new snapshot, never relabel an old queued prediction as fresh. Current Studio stage transitions remain paused and require an explicit supported-mode Start followed by NEUTRAL. Profile/model changes and focus loss also require explicit resume.

`process(prediction, now)` emits at most one event per continuous hold. `route(event, now)` accepts only an exact event issued by this coordinator, once, with current identity/model and age no greater than 200 ms. Altered/stale events are consumed; repeating them cannot recover an action. Pause, tracking loss, rearming and generation changes invalidate pending events.

PREVIEW and REHEARSAL populate only `simulated_action`. LIVE populates `action`. Studio attaches Javier's dispatcher for simulations and explicit manual LIVE requests; its gesture readiness callback currently returns false. The longer personal rehearsal is attached in Practice; its measured acceptance and a separate reviewed revision-bound gate are required before enabling LIVE gestures. Construction or passing the short check alone is not permission to execute OS actions.

All coordinator calls and immediate routing/dispatch belong on one owner thread. A RoutingResult is not a durable token: do not queue it for execution after a mode/profile/stage change. The final dispatcher must independently consume event IDs once and record outcomes. Camera release and any asynchronous action preparation require a fresh snapshot check before the side effect.

Manual actions use the same validated target/action handlers, labelled `source=manual`; do not manufacture a prediction or held-gesture event for a button click. Enrolment/practice must have no route to an actual external launcher. Actions are never executed on configuration import or state restoration.

Studio owns one persistent `Dispatcher`; context/profile/workspace changes must not clear its consumed event IDs. Refresh its viewer, runbook and summary references before routing a request. A preservation failure raises `DispatchFailure` before any external launch. Camera handoff interrupts the current worker and requires bounded shutdown acknowledgement; timeout consumes the request, opens nothing and requires a new manual request after release. Returning focus never resumes or replays actions. `launch_requested` records the request only, not completion of the user's external task. External targets use the existing Windows launcher; portable viewer/runbook controls remain available on other platforms.

## Verification and remaining work

Run `.\.venv\Scripts\python.exe -m pytest -q tests/test_controller.py tests/test_project_routing.py tests/test_viewer.py`.

Checks cover custom IDs, all typed actions, default NEXT-only behaviour, once-per-hold, identity/model/context/map/mode changes, malformed configuration, forged/altered/stale/duplicate events, pause/tracking loss and simulation isolation. Studio adds shared dispatch, explicit manual LIVE requests and focus-loss pause. Starter release, measured personal acceptance and integrated human/hardware evaluation remain assigned work; generated software checks do not establish new-user recognition quality or native Windows launch success.

## Current shell adapter (Deston)

`Window(..., studio=True, vocabulary=bundle.vocabulary)` exposes `configure_studio(context_id=None, mode=None, bindings=None)`. The default vocabulary preserves legacy labels. The three vocabulary action IDs initially map in order to NEXT, PREVIOUS and BOOKMARK simulations. Omitted configuration values preserve the current snapshot. Supplied bindings replace the whole map (up to three enrolled IDs to typed `Action` objects); an empty map pauses routing and keeps the context manual-only. The complete draft, including membership in the selected vocabulary, is validated before changing active state; invalid inputs raise `ValueError` and leave the current session/capture intact. Startup accepts PREVIEW/REHEARSAL only. Explicit UI configuration may select LIVE for manual controls; it never starts capture.

Successful application pauses capture, clears the old prediction display, creates a fresh routing session, updates the visible legend and records the semantic configuration locally. Interrupted workers and packets with old session/profile/model identities cannot overwrite the new display. Explicit resume still waits for worker shutdown and requires NEUTRAL. The on-screen selectors edit a draft; Apply and pause performs the change. These mappings are in memory only.

`pause()` returns whether an optional evaluation trace was saved successfully. `configure_studio(...)` returns `True` only after applying the configuration. If a trace cannot be saved, configuration/camera changes, dataset loading and deck reset stop while preserving the previous selection and the buffered trace; `use_studio_model(...)` raises `ValueError` before replacement. Integrators must respect these outcomes. The camera is still stopped on save failure; the user can fix storage and press Pause to retry.

The Studio launcher loads schema-1 or schema-2 datasets and passes `bundle.vocabulary` to both `train_model` and `Window`. Explicit vocabulary training produces a data/settings-bound model revision even for legacy IDs. The assignment launcher keeps its existing model-version policy and rejects custom IDs with a request to use `--studio`.

The saved-profile adapter loads a validated `LoadedProfile` with its vocabulary and matching model revision; it does not certify readiness. Hau Jie's selector is attached in Profiles using the shell-owned lifecycle below. `--profile-store PATH` selects the same private store for startup and the tab. Cosmetic rename notifications refresh the shell label without retraining. Explicit Preview-start requests must match the selected profile/model and Preview mode, wait for camera release and require fresh NEUTRAL; installation alone never resumes capture. Workspace/runbook state is saved through the Studio session file path, and stage changes must pass their complete map through the existing context reset path. Software fixtures verify custom classification-to-simulation integration; live recognition of newly enrolled poses remains to be measured.

### Personal dataset selection and model replacement

Studio's **Load personal dataset...** button calls `load_studio_dataset(path)`. The CLI and UI share `load_personal_model`: schema-1/2 numeric manifests, one participant, human provenance, valid hand and train-only fitting. UI loading pauses capture immediately and permits one background training job; start and configuration application are blocked until it finishes. Launch algorithm/rejection settings are reused. No data or model file is rewritten.

`use_studio_model(model, hand, profile, vocabulary)` installs a completed candidate on the UI thread. The classifier must expose `predict`, `train_labels`, `model_version` and the existing `config` fields; its labels must match the vocabulary. Validate the candidate and fresh routing snapshot before replacing state. Successful replacement interrupts old capture, clears the old preview/prediction, resets mode to Preview and remains paused. If the current workspace has an active stage, Studio reapplies that stage's bindings when they match the new vocabulary; mismatched or empty stages stay manual-only. Without an active runbook stage, the startup or standalone deck keeps the default three simulated mappings; an imported manual-only workspace stays manual-only. Start stays disabled until the prior camera worker releases; explicit start requires NEUTRAL. Invalid candidates leave the previous model and mappings intact. Failed asynchronous loads leave that selection paused.

Closing stops UI polling; a finishing background load cannot update widgets, start capture or dispatch. `load_studio_profile(store, id)` reconstructs a saved profile through the same worker; `use_studio_profile(candidate)` installs it with its separate display name and stored settings. The selector must request loads by ID rather than train on the GUI thread. For deletion, in one synchronous UI-owner handler call `prepare_studio_profile_delete(id)`; only on true call `store.delete(id)`; only on successful deletion immediately call `clear_studio_profile(id)`. Storage failure retains the old selection. Unrelated pending loads block deletion; matching pending results are invalidated. Clearing an active profile disables camera Start and preserves manual controls. See the [profile handoff](PROFILE_PERSISTENCE_HANDOFF.md) for the full integration sequence.

`use_studio_guest()` is the separate non-destructive switch to manual control. It pauses capture, preserves pending trace/enrolment evidence, clears the in-memory recogniser and invalidates the old capture identity without deleting profile or dataset files. It retains the workspace, deck/bookmarks, runbook, summary and targets. Busy loading, closing or failed preservation returns false; the selector must retain its previous selection until true. A saved profile can be loaded again afterwards. No starter or readiness pass is implied. The Profiles tab exposes this as **Use Guest (manual only)**; unavailable standard gestures remain disabled with a reason.

### Camera selection and recovery

`set_studio_camera(index)` accepts a non-negative signed 32-bit integer (not a boolean), validates before changing state and rejects changes during model loading. A different index uses the existing configuration/pause path to invalidate the capture generation while preserving the active context, mappings and simulation mode. Selecting the same index does nothing. The old capture worker must finish before explicit Start can create a new worker with the selected index and fresh session. Start requires NEUTRAL again. Device indices are local session settings, not portable workspace bindings.

Camera faults and pause clear the displayed preview. Recovery messages do not automatically reopen capture or launch the Windows Camera app. This software path is covered by worker simulations; the user deferred a new live-device check on 30 September.

### Manual deck files and progress

Studio exposes `load_studio_deck(path)`, `save_studio_progress(path)` and `restore_studio_progress(path)`, each returning success/failure. They require an open Studio window with no dataset load in progress. The shared file-control grid pauses before opening dialogs; cancelling leaves control paused. Each direct operation also pauses and honours failed evaluation-trace saving before changing a deck or writing progress.

Deck loading reuses the bounded version-1 parser and replaces the viewer only after complete validation. Progress uses the existing viewer state schema: deck ID, ordered card IDs, current card ID and bookmarks. Restore validates against the loaded deck before changing state. Failure retains the previous deck/position/bookmarks; atomic save failure retains any prior file. Both viewer tabs are refreshed after successful load/restore, imported text is displayed literally, and restart retains the loaded deck while clearing in-memory progress.

File actions never resume capture, replay commands or establish readiness. Queued interrupted-worker packets remain ignored; a later explicit Start creates a fresh session and requires NEUTRAL. The default save location is ignored `.local/studio`; saving is explicit, with no autosave on close. Progress does not include deck text, profile/model data, mappings, local targets or runbook state.

### Studio workspace and runbook session files

Studio exposes `load_studio_workspace(path)`, `save_studio_session(path)` and `restore_studio_session(path)`, each returning success/failure. Workspace load validates the full portable workspace before replacing visible deck/runbook state; failure keeps the prior workspace, viewer, runbook and routing context. Loading a standalone custom deck creates a manual deck workspace and detaches the prior runbook.

Runbook stage changes call the same context reset path as routing configuration and remain paused. Stages with no bindings, or bindings outside the loaded vocabulary, are manual-only. A compatible `use_studio_model(...)` call reapplies the current stage bindings and resets mode to Preview. Typed Continue/Finish and stage actions simulate in Preview/Rehearsal and execute manually in LIVE. Previous-stage navigation, bookmark review/removal, restart and restore remain explicit navigation operations; they do not generate gesture or readiness evidence.

Session save writes schema version, the current workspace JSON, current stage ID/finished state and matching viewer state. Restore requires that same workspace to be loaded first, then validates the session's embedded workspace JSON and saved stage before changing state; it restores paused and never replays actions. Restart clears in-memory viewer progress and reactivates the first stage for the current deck/workspace.

### Stage editing and session summaries

Studio's **Edit runbook** tab wraps `RunbookEditorWidget`: New, Save stage, Delete, Move up and Move down emit a fully validated workspace and never execute actions. Accepted edits call the same workspace activation path as imports. If the deck is unchanged, Studio preserves deck review state; otherwise it replaces the workspace, resets routing and stays paused. Local target bindings and personal profiles are never written into portable workspace content.

Studio's **Session summary** tab wraps `SessionSummaryWidget`. Refresh shows current counts, and **Export session results** writes scope, counts, outcomes, trials and acknowledged stage completions to local JSON. The scope carries workspace identity plus a generated review `revision_id`; it is a review marker, not a deterministic content hash or readiness proof. Counts cover typed manual requests, gesture simulations/rejections and external launch requests/failures from the shared dispatcher. Bookmark list review/removal remains outside this summary; a launch request is never counted as task completion. Correct/wrong/missed are zero until measured `Trial` records are supplied, so zero is unmeasured, not a passed evaluation, and manual actions do not create automatic readiness evidence. Navigation saves use **Save session...** / **Restore session...** and are separate from measurement exports. Before deck/workspace replacement, session restore, restart or close would leave a non-empty summary behind, Studio archives it under ignored `.local/studio`; archive failure blocks the change or close and retains the current counts. Successful restore/restart starts a fresh review summary. When the summary record limit is reached, export and start a fresh review session. If the separate 4,096-event dispatcher limit is reached, export and close/reopen Studio; resetting a summary does not clear consumed action IDs.

### Short readiness check

With a loaded recogniser, Studio prompts each of its three action IDs twice. The existing neutral/hold controller supplies the only scored events; manual controls and raw predictions cannot earn credit. A wrong activation fails the attempt. Finishing an incomplete or UNKNOWN-only attempt fails it. Capture interruption cancels the attempt and requires a new check. The previous context is restored paused; failed trace preservation retains recovery state.

The result is a session-local six-activation check, not accuracy evaluation, identity authentication, an approved starter or permission to execute desktop actions. GF-P12's longer personal rehearsal is a separate workflow and result. Guest stays manual-only while no approved starter is available.

### Measured personal rehearsal (GF-P12)

The embedded **Practice** tab uses `PersonalRehearsal` and the existing persistent `Dispatcher` in REHEARSAL mode. It records ten five-second windows per enrolled pose (three commands plus NEUTRAL), then ten negative/transition windows. Users review the negative instructions against their custom vocabulary and consent to local outcome recording before starting. The protocol, capture-generation handshake, bounded late-frame handling and result format are defined in [PERSONAL_REHEARSAL_INTERFACE.md](PERSONAL_REHEARSAL_INTERFACE.md).

The component processes each observation exactly once through the shared router. The shell supplies one camera worker stamped with the prepared snapshot, waits for the preceding worker to retire, and does not process those predictions a second time. Practice never launches applications or changes the viewer. Terminal results remain historical evidence after the previous context is restored; their applicability is checked against the current semantic behavior revision.

Changing context, losing focus, pausing or a camera fault interrupts an active attempt. Local save failure retains evidence and blocks replacement or close until retry succeeds. The previous context restores paused after preservation. A measured pass neither sets the preliminary check's pass field nor enables LIVE gestures. Native measured acceptance and the reviewed live-readiness gate remain separate work.
