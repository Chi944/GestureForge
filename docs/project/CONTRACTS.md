# Shared project routing contract

Project contract version 1 Â· 30 September 2026 Â· Owner Deston

This is the implemented first integration boundary. Legacy dataset schema 1 and custom-vocabulary schema 2 share `FEATURE_VERSION=1`; legacy labels and the NEXT-only default controller remain compatible. `PROJECT_CONTRACT_VERSION=1` versions the new routing types separately. Profile/workspace persistence schemas and widget signal adapters are owned by the respective builders and need interface review before integration; they are not claimed implemented here.

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

These records define the integration boundary for GF-P02. They are not implemented persistence modules yet. Hau Jie owns the profile/readiness storage and widgets; Javier owns workspace/runbook/shortcut storage and widgets; Deston owns the shell handoff and final acceptance.

| Handoff | Required fields | Version and loading rule |
|---|---|---|
| `ProfileSelection` | `profile_id`, `display_name`, `selected_hand`, `vocabulary`, `model_version`, `readiness_revision` or empty reason | Profile schema starts at version 1. Load validates the complete record and trained model candidate before replacing the active profile. Invalid, corrupt or incompatible files leave the previous profile/model active and paused. |
| `WorkspaceSelection` | `workspace_id`, `title`, optional `deck`, optional `runbook`, semantic shortcut slots, `workspace_revision` | Workspace schema starts at version 1. Import validates size, schema, IDs, references and excluded fields before replacing active workspace. Failure leaves the previous workspace active and paused. |
| `RunbookContext` | `context_id`, stage title/instruction, optional card ID, zero to three gesture/action slots, continue/finish path | A stage with no gesture slots uses manual controls with routing paused. Other stage changes are context switches. They call `configure_studio(context_id=..., bindings=...)`, cancel pending holds and require NEUTRAL, but they do not invalidate readiness when the profile/model/binding revision is unchanged. |
| `ReadinessStatus` | `profile_id`, `model_version`, `readiness_revision`, `binding_revision`, mode, pass/fail/expired status and short reason | Readiness is valid only for the selected hand, training data hash, feature version, classifier/rejection settings, hold/rearm policy and binding map used during the check. Profile/model changes and mapping edits expire it. Selecting a preconfigured stage only switches context. |

Atomic save means write a new validated file, replace the old file only after the write succeeds, and keep the last working file available after failures. Loading must never partially replace an active profile, workspace, runbook or binding map.

Portable workspace exports include deck text, runbook instructions, semantic shortcut slot IDs/labels and action mappings. They exclude local executable/file/folder paths, URLs, credentials, personal profiles, training samples, model files, raw video, full sensitive target paths, event logs and generated local evidence. Each computer binds and tests its own local targets.

Data limits are shared: one profile vocabulary has exactly three action gesture IDs plus NEUTRAL; an active gesture context binds one to three gestures; a manual-only screen has no active routing; one gesture maps to one `Action`; a runbook has at most twelve stages; a local shortcut library has at most twelve targets; a deck is optional for Quick Actions and optional for a runbook stage unless that stage references a card.

## Widget handoff signals

Use plain PySide signals or direct method calls carrying these records; do not create separate application shells or camera workers.

| Producer | Signal or call | Shell response |
|---|---|---|
| Profile selector | `profile_selected(ProfileSelection)` | Pause, validate model/vocabulary, install with `use_studio_model(...)`, clear old prediction, show selected profile/readiness state. |
| Profile/enrolment widget | `readiness_changed(ReadinessStatus)` | Update the readiness message and enable LIVE only after Deston's final readiness gate exists. Current Studio keeps PREVIEW/REHEARSAL only. |
| Workspace widget | `workspace_selected(WorkspaceSelection)` | Pause, validate full workspace, replace visible deck/runbook state only after success, keep local targets unbound until Javier's registry resolves them. |
| Runbook widget | `stage_selected(RunbookContext)` | Apply the stage context and complete binding map through `configure_studio`; show NEUTRAL-required status. |
| Shortcut registry | `shortcut_binding_changed(binding_revision)` | Pause and expire readiness because action meanings changed. |

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

Checks cover custom IDs, all typed actions, default NEXT-only behaviour, once-per-hold, identity/model/context/map/mode changes, malformed configuration, forged/altered/stale/duplicate events, pause/tracking loss and simulation isolation. These are software checks. An opt-in Studio shell now integrates simulation routing and focus-loss pause. Starter data, profile persistence, the complete GUI workflow, readiness scoring, actual launch handling and human/hardware evaluation remain assigned work; no test here establishes new-user recognition quality or Windows launch success.

## Current shell adapter (Deston)

`Window(..., studio=True, vocabulary=bundle.vocabulary)` exposes `configure_studio(context_id=None, mode=None, bindings=None)`. The default vocabulary preserves legacy labels. The three vocabulary action IDs initially map in order to NEXT, PREVIOUS and BOOKMARK simulations. Omitted configuration values preserve the current snapshot. Supplied bindings replace the whole map (one to three enrolled IDs to typed `Action` objects). The complete draft, including membership in the selected vocabulary, is validated before changing active state; invalid inputs raise `ValueError` and leave the current session/capture intact. Only PREVIEW and REHEARSAL are accepted by this shell.

Successful application pauses capture, clears the old prediction display, creates a fresh routing session, updates the visible legend and records the semantic configuration locally. Interrupted workers and packets with old session/profile/model identities cannot overwrite the new display. Explicit resume still waits for worker shutdown and requires NEUTRAL. The on-screen selectors edit a draft; Apply and pause performs the change. These mappings are in memory only.

`pause()` returns whether an optional evaluation trace was saved successfully. `configure_studio(...)` returns `True` only after applying the configuration. If a trace cannot be saved, configuration/camera changes, dataset loading and deck reset stop while preserving the previous selection and the buffered trace; `use_studio_model(...)` raises `ValueError` before replacement. Integrators must respect these outcomes. The camera is still stopped on save failure; the user can fix storage and press Pause to retry.

The Studio launcher loads schema-1 or schema-2 datasets and passes `bundle.vocabulary` to both `train_model` and `Window`. Explicit vocabulary training produces a data/settings-bound model revision even for legacy IDs. The assignment launcher keeps its existing model-version policy and rejects custom IDs with a request to use `--studio`.

This adapter does not load saved profiles, certify readiness or save workspace settings. Hau Jie's future profile adapter must supply the selected vocabulary and matching model revision, and Javier's workspace adapter must validate its references before using this entry point. Existing stage changes should pass their complete map. Software fixtures verify custom classification-to-simulation integration; live recognition of newly enrolled poses remains to be measured.

### Personal dataset selection and model replacement

Studio's **Load personal dataset...** button calls `load_studio_dataset(path)`. The CLI and UI share `load_personal_model`: schema-1/2 numeric manifests, one participant, human provenance, valid hand and train-only fitting. UI loading pauses capture immediately and permits one background training job; start and configuration application are blocked until it finishes. Launch algorithm/rejection settings are reused. No data or model file is rewritten.

`use_studio_model(model, hand, profile, vocabulary)` installs a completed candidate on the UI thread. The classifier must expose `predict`, `train_labels`, `model_version` and the existing `config` fields; its labels must match the vocabulary. Validate the candidate and fresh routing snapshot before replacing state. Successful replacement interrupts old capture, clears the old preview/prediction, resets to Preview and the three default simulation mappings, and remains paused. Start stays disabled until the prior camera worker releases; explicit start requires NEUTRAL. Invalid candidates leave the previous model and mappings intact. Failed asynchronous loads leave that selection paused.

Closing stops UI polling; a finishing background load cannot update widgets, start capture or dispatch. This adapter does not create, rename, delete or persist profiles. Hau Jie's profile selector can supply an already trained candidate through this entry point once its lifecycle and readiness contracts are ready.

### Camera selection and recovery

`set_studio_camera(index)` accepts a non-negative signed 32-bit integer (not a boolean), validates before changing state and rejects changes during model loading. A different index uses the existing configuration/pause path to invalidate the capture generation while preserving the active context, mappings and simulation mode. Selecting the same index does nothing. The old capture worker must finish before explicit Start can create a new worker with the selected index and fresh session. Start requires NEUTRAL again. Device indices are local session settings, not portable workspace bindings.

Camera faults and pause clear the displayed preview. Recovery messages do not automatically reopen capture or launch the Windows Camera app. This software path is covered by worker simulations; the user deferred a new live-device check on 30 September.

### Manual deck files and progress

Studio exposes `load_studio_deck(path)`, `save_studio_progress(path)` and `restore_studio_progress(path)`, each returning success/failure. They require an open Studio window with no dataset load in progress. The visible file buttons pause before opening their dialogs; cancelling leaves control paused. Each direct operation also pauses and honours failed evaluation-trace saving before changing a deck or writing progress.

Deck loading reuses the bounded version-1 parser and replaces the viewer only after complete validation. Progress uses the existing viewer state schema: deck ID, ordered card IDs, current card ID and bookmarks. Restore validates against the loaded deck before changing state. Failure retains the previous deck/position/bookmarks; atomic save failure retains any prior file. Both viewer tabs are refreshed after successful load/restore, imported text is displayed literally, and restart retains the loaded deck while clearing in-memory progress.

File actions never resume capture, replay commands or establish readiness. Queued interrupted-worker packets remain ignored; a later explicit Start creates a fresh session and requires NEUTRAL. The default save location is ignored `.local/studio`; saving is explicit, with no autosave on close. Progress does not include deck text, profile/model data, mappings, local targets or runbook state. Full workspace/runbook persistence remains a separate integration boundary.
