# Shared project routing contract

Project contract version 1 | Design frozen 2 October 2026 | Owner Deston

This is the version-1 integration baseline. Legacy dataset schema 1 and custom-vocabulary schema 2 share `FEATURE_VERSION=1`; legacy labels and the NEXT-only default controller remain compatible. `PROJECT_CONTRACT_VERSION=1` versions the routing types separately. Studio integrates manual deck browsing, workspace loading, stage editing, runbook session save/restore, session-summary export and Quick Actions simulation. Profile persistence is implemented; selector/enrolment widgets, readiness and guarded real dispatch remain separate integration work.

## GF-P02 design freeze - 2 October 2026

Deston's integration baseline adopts the approved [project plan](PROJECT_PLAN.md) and [screen/transition design](TEAM_GUIDE.md#initial-screen-design): Try standard gestures first, optional Personalise, and exactly one typed action per bound stage slot. Reviewed merged PRs #10, #14 and #15 supply the vocabulary, profile and workspace/component interfaces below. Independent acceptance and architecture review reconciled these handoffs with the implementation. This records the approved design and its adoption in reviewed code; it does not claim a separate team meeting or tutor approval.

The final flow is **Try standard gestures -> simulated readiness check -> explicit Start/NEUTRAL -> eligible control**. A failed check offers retry, optional Personalise or manual controls. An unavailable starter shows its reason and preserves manual access. Saved profiles may be loaded without collecting again; loading alone never proves readiness. Preview/Rehearsal can run before readiness, but LIVE gesture execution requires the exact current behaviour revision to pass. Current Studio remains simulation-only. This design freeze does not complete starter evaluation, selector/enrolment, readiness or hardware acceptance.

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

These are logical handoffs, not a request for four new Python record classes. Hau Jie owns profile/readiness storage and widgets; Javier owns shortcut storage and component widgets; Deston owns the shell handoff and final acceptance. The table names actual counterparts where they exist; readiness remains a planned interface.

| Handoff | Required fields | Version and loading rule |
|---|---|---|
| `profiles.ProfileSelection`, from `LoadedProfile.selection` | `profile_id`, `display_name`, `selected_hand`, `vocabulary`, `model_version`, `readiness_revision`, `readiness_reason` | Schema 1. Metadata alone cannot install a recogniser: the shell needs the complete `LoadedProfile` candidate. Validate before replacement; corrupt or incompatible loads leave the previous profile/model active and paused. |
| Workspace selection, implemented by `workspace.Workspace` | `id` (workspace identity), `title`, optional `deck`, semantic `shortcuts`, ordered `stages` | Schema 1. There is no separate `WorkspaceSelection` class or stored `workspace_revision` field. Validate the complete value before replacement. The future readiness gate must bind to all authored action meanings; navigation/session revision IDs are not readiness proof. |
| Runbook context, implemented by `workspace.Stage` and `runbook.Runbook` | `id` (stage/context identity), title/instructions, optional `card_id`, zero to three typed `bindings`; runbook owns continue/finish state | `Window.reset_runbook_stage(stage, resume)` applies the complete context. Empty stages stay manual-only. Other transitions clear holds and require NEUTRAL; selecting an already configured stage does not itself change the authored binding revision. |
| Readiness status (planned logical handoff) | `profile_id`, `model_version`, `readiness_revision`, `binding_revision`, mode, pass/fail/expired status and short reason | No `ReadinessStatus` class is implemented yet. Bind to selected hand, training hash, feature version, classifier/rejection settings, hold/rearm policy and the complete authored binding map. Profile/model or mapping changes expire it; stage navigation alone does not. |

Atomic save means write a new validated file, replace the old file only after the write succeeds, and keep the last working file available after failures. Loading must never partially replace an active profile, workspace, runbook or binding map.

Portable workspace exports include deck text, runbook instructions, semantic shortcut slot IDs/labels and action mappings. They exclude local executable/file/folder paths, URLs, credentials, personal profiles, training samples, model files, raw video, full sensitive target paths, event logs and generated local evidence. Each computer binds and tests its own local targets.

Data limits are shared: one profile vocabulary has exactly three action gesture IDs plus NEUTRAL; an active gesture context binds one to three gestures; a manual-only screen has no active routing; one gesture maps to one `Action`; a runbook has at most twelve stages; a local shortcut library has at most twelve targets; a deck is optional for Quick Actions and optional for a runbook stage unless that stage references a card.

## Widget handoff signals

Use plain PySide signals or direct method calls carrying these records; do not create separate application shells or camera workers.

| Producer | Signal or call | Shell response |
|---|---|---|
| Profile selector (widget pending) | Request load by `ProfileStore` and opaque profile ID; publish selection only after successful installation | Shell owns background reconstruction and installs a complete `LoadedProfile`. Metadata-only `ProfileSelection` is for display. Deletion must clear a matching active or pending selection through the shell. |
| Profile/enrolment widget (pending) | Version-bound readiness result; concrete widget signal not yet implemented | Show pass/fail/expired reason. LIVE remains unavailable until the exact-revision gate is integrated. Preview/Rehearsal may run the check. |
| `WorkspaceWidget` / `RunbookEditorWidget` | `workspace_changed(Workspace)` | `accept_workspace_widget_change` / `accept_runbook_editor_change` pause and validate before replacing content. Imported targets remain semantic references. |
| `RunbookWidget` / `Runbook` | `action_requested(Action)`, `previous_stage_requested()`, `completion_acknowledged(stage_id)`; runbook callback `(Stage or None, resume)` | `reset_runbook_stage` applies the complete map and invalidates holds; viewing a tab does not activate it. |
| `QuickActionsWidget` | `before_publish() -> bool`, then `bindings_changed(...)` after successful local save | Pause before mutation; failed save preserves the registry. Clear active routing and require explicit Use Quick Actions. The future readiness gate must expire changed action meanings. |

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

`configure(...)` takes the same complete arguments, validates before replacing state, creates a fresh session and pauses. Any profile, model, workspace, context, mapping or mode change goes through it. Explicit `resume()` creates another fresh session and WAIT_NEUTRAL; `pause()` cancels issued work. Deston's shell must restart or restamp capture against the new snapshot, never relabel an old queued prediction as fresh. A stage transition may call configure then resume in the same UI handler, retaining valid readiness but still requiring NEUTRAL. Profile/model changes and focus loss require explicit user resume.

`process(prediction, now)` emits at most one event per continuous hold. `route(event, now)` accepts only an exact event issued by this coordinator, once, with current identity/model and age no greater than 200 ms. Altered/stale events are consumed; repeating them cannot recover an action. Pause, tracking loss, rearming and generation changes invalidate pending events.

PREVIEW and REHEARSAL populate only `simulated_action`. LIVE populates `action`. This foundation does not establish readiness or launch anything. Before wiring LIVE, Deston must integrate Hau Jie's version-bound readiness gate and Javier's final validated dispatcher. Construction alone is not permission to execute OS actions.

All coordinator calls and immediate routing/dispatch belong on one owner thread. A RoutingResult is not a durable token: do not queue it for execution after a mode/profile/stage change. The final dispatcher must independently consume event IDs once and record outcomes. Camera release and any asynchronous action preparation require a fresh snapshot check before the side effect.

Manual actions use the same validated target/action handlers, labelled `source=manual`; do not manufacture a prediction or held-gesture event for a button click. Enrolment/practice must have no route to an actual external launcher. Actions are never executed on configuration import or state restoration.

## Verification and remaining work

Run `.\.venv\Scripts\python.exe -m pytest -q tests/test_controller.py tests/test_project_routing.py tests/test_viewer.py`.

Checks cover custom IDs, all typed actions, default NEXT-only behaviour, once-per-hold, identity/model/context/map/mode changes, malformed configuration, forged/altered/stale/duplicate events, pause/tracking loss and simulation isolation. These are software checks. An opt-in Studio shell now integrates simulation routing and focus-loss pause. Starter release, profile/enrolment widgets, the complete GUI workflow, readiness scoring, actual launch handling and human/hardware evaluation remain assigned work; no test here establishes new-user recognition quality or Windows launch success.

## Current shell adapter (Deston)

`Window(..., studio=True, vocabulary=bundle.vocabulary)` exposes `configure_studio(context_id=None, mode=None, bindings=None)`. The default vocabulary preserves legacy labels. The three vocabulary action IDs initially map in order to NEXT, PREVIOUS and BOOKMARK simulations. Omitted configuration values preserve the current snapshot. Supplied bindings replace the whole map (up to three enrolled IDs to typed `Action` objects); an empty map pauses routing and keeps the context manual-only. The complete draft, including membership in the selected vocabulary, is validated before changing active state; invalid inputs raise `ValueError` and leave the current session/capture intact. Only PREVIEW and REHEARSAL are accepted by this shell.

Successful application pauses capture, clears the old prediction display, creates a fresh routing session, updates the visible legend and records the semantic configuration locally. Interrupted workers and packets with old session/profile/model identities cannot overwrite the new display. Explicit resume still waits for worker shutdown and requires NEUTRAL. The on-screen selectors edit a draft; Apply and pause performs the change. These mappings are in memory only.

`pause()` returns whether an optional evaluation trace was saved successfully. `configure_studio(...)` returns `True` only after applying the configuration. If a trace cannot be saved, configuration/camera changes, dataset loading and deck reset stop while preserving the previous selection and the buffered trace; `use_studio_model(...)` raises `ValueError` before replacement. Integrators must respect these outcomes. The camera is still stopped on save failure; the user can fix storage and press Pause to retry.

The Studio launcher loads schema-1 or schema-2 datasets and passes `bundle.vocabulary` to both `train_model` and `Window`. Explicit vocabulary training produces a data/settings-bound model revision even for legacy IDs. The assignment launcher keeps its existing model-version policy and rejects custom IDs with a request to use `--studio`.

The saved-profile adapter loads a validated `LoadedProfile` with its vocabulary and matching model revision; it does not certify readiness. Hau Jie's selector widget must use the shell-owned lifecycle below. Workspace/runbook state is saved through the Studio session file path, and stage changes must pass their complete map through the existing context reset path. Software fixtures verify custom classification-to-simulation integration; live recognition of newly enrolled poses remains to be measured.

### Personal dataset selection and model replacement

Studio's **Load personal dataset...** button calls `load_studio_dataset(path)`. The CLI and UI share `load_personal_model`: schema-1/2 numeric manifests, one participant, human provenance, valid hand and train-only fitting. UI loading pauses capture immediately and permits one background training job; start and configuration application are blocked until it finishes. Launch algorithm/rejection settings are reused. No data or model file is rewritten.

`use_studio_model(model, hand, profile, vocabulary)` installs a completed candidate on the UI thread. The classifier must expose `predict`, `train_labels`, `model_version` and the existing `config` fields; its labels must match the vocabulary. Validate the candidate and fresh routing snapshot before replacing state. Successful replacement interrupts old capture, clears the old preview/prediction, resets mode to Preview and remains paused. If the current workspace has an active stage, Studio reapplies that stage's bindings when they match the new vocabulary; mismatched or empty stages stay manual-only. Without an active runbook stage, the startup or standalone deck keeps the default three simulated mappings; an imported manual-only workspace stays manual-only. Start stays disabled until the prior camera worker releases; explicit start requires NEUTRAL. Invalid candidates leave the previous model and mappings intact. Failed asynchronous loads leave that selection paused.

Closing stops UI polling; a finishing background load cannot update widgets, start capture or dispatch. `load_studio_profile(store, id)` reconstructs a saved profile through the same worker; `use_studio_profile(candidate)` installs it with its separate display name and stored settings. The selector must request loads by ID rather than train on the GUI thread. For deletion, in one synchronous UI-owner handler call `prepare_studio_profile_delete(id)`; only on true call `store.delete(id)`; only on successful deletion immediately call `clear_studio_profile(id)`. Storage failure retains the old selection. Unrelated pending loads block deletion; matching pending results are invalidated. Clearing an active profile disables camera Start and preserves manual controls. See the [profile handoff](PROFILE_PERSISTENCE_HANDOFF.md) for the full integration sequence.

### Camera selection and recovery

`set_studio_camera(index)` accepts a non-negative signed 32-bit integer (not a boolean), validates before changing state and rejects changes during model loading. A different index uses the existing configuration/pause path to invalidate the capture generation while preserving the active context, mappings and simulation mode. Selecting the same index does nothing. The old capture worker must finish before explicit Start can create a new worker with the selected index and fresh session. Start requires NEUTRAL again. Device indices are local session settings, not portable workspace bindings.

Camera faults and pause clear the displayed preview. Recovery messages do not automatically reopen capture or launch the Windows Camera app. This software path is covered by worker simulations; the user deferred a new live-device check on 30 September.

### Manual deck files and progress

Studio exposes `load_studio_deck(path)`, `save_studio_progress(path)` and `restore_studio_progress(path)`, each returning success/failure. They require an open Studio window with no dataset load in progress. The shared file-control grid pauses before opening dialogs; cancelling leaves control paused. Each direct operation also pauses and honours failed evaluation-trace saving before changing a deck or writing progress.

Deck loading reuses the bounded version-1 parser and replaces the viewer only after complete validation. Progress uses the existing viewer state schema: deck ID, ordered card IDs, current card ID and bookmarks. Restore validates against the loaded deck before changing state. Failure retains the previous deck/position/bookmarks; atomic save failure retains any prior file. Both viewer tabs are refreshed after successful load/restore, imported text is displayed literally, and restart retains the loaded deck while clearing in-memory progress.

File actions never resume capture, replay commands or establish readiness. Queued interrupted-worker packets remain ignored; a later explicit Start creates a fresh session and requires NEUTRAL. The default save location is ignored `.local/studio`; saving is explicit, with no autosave on close. Progress does not include deck text, profile/model data, mappings, local targets or runbook state.

### Studio workspace and runbook session files

Studio exposes `load_studio_workspace(path)`, `save_studio_session(path)` and `restore_studio_session(path)`, each returning success/failure. Workspace load validates the full portable workspace before replacing visible deck/runbook state; failure keeps the prior workspace, viewer, runbook and routing context. Loading a standalone custom deck creates a manual deck workspace and detaches the prior runbook.

Runbook stage changes call the same context reset path as routing configuration. Stages with no bindings, or bindings outside the loaded vocabulary, are manual-only with routing paused. A compatible `use_studio_model(...)` call reapplies the current stage bindings and keeps actions in Preview/Rehearsal simulation. Runbook buttons for Previous, Continue/Finish and stage actions operate on the local runbook or produce simulated requests only.

Session save writes schema version, the current workspace JSON, current stage ID/finished state and matching viewer state. Restore requires that same workspace to be loaded first, then validates the session's embedded workspace JSON and saved stage before changing state; it restores paused and never replays actions. Restart clears in-memory viewer progress and reactivates the first stage for the current deck/workspace.

### Stage editing and session summaries

Studio's **Edit runbook** tab wraps `RunbookEditorWidget`: New, Save stage, Delete, Move up and Move down emit a fully validated workspace and never execute actions. Accepted edits call the same workspace activation path as imports. If the deck is unchanged, Studio preserves deck review state; otherwise it replaces the workspace, resets routing and stays paused. Local target bindings and personal profiles are never written into portable workspace content.

Studio's **Session summary** tab wraps `SessionSummaryWidget`. Refresh shows current counts, and **Export session results** writes scope, counts, outcomes, trials and acknowledged stage completions to local JSON. The scope carries workspace identity plus a generated review `revision_id`; it is a review marker, not a deterministic content hash or readiness proof. Counts cover Studio manual card/runbook actions plus gesture simulation/rejection events; bookmark list review/removal and live OS dispatch are outside this summary. Correct/wrong/missed are zero until measured `Trial` records are supplied, so zero is unmeasured, not a passed evaluation, and manual actions do not create automatic readiness evidence. Navigation saves use **Save session...** / **Restore session...** and are separate from measurement exports. Before deck/workspace replacement, session restore, restart or close would leave a non-empty summary behind, Studio archives it under ignored `.local/studio`; archive failure blocks the change or close and retains the current counts. Successful restore/restart starts a fresh review summary. When record limits are reached, export and start a fresh review session rather than evicting old event IDs.
