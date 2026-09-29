# Shared project routing contract

Project contract version 1 · 30 September 2026 · Owner Deston

This is the implemented first integration boundary. Existing dataset `SCHEMA_VERSION=1`, `FEATURE_VERSION=1`, legacy labels and NEXT-only default controller remain compatible. `PROJECT_CONTRACT_VERSION=1` versions the new routing types separately. Profile/workspace persistence schemas and widget signal adapters are owned by the respective builders and need interface review before integration; they are not claimed implemented here.

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

Other opaque IDs are 1–64 ASCII letters/digits and `_ . : -`, beginning with a letter/digit. Display names and target paths are separate values. The shortcut ID is never a URL or executable path. Actual target validation belongs to Javier's local registry/dispatcher.

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

`RoutingSession(profile_id, model_version, context_id, bindings, mode=PREVIEW)` starts PAUSED. Read `snapshot`, `state`, `progress`, `last_error`; do not access its private controller.

`configure(...)` takes the same complete arguments, validates before replacing state, creates a fresh session and pauses. Any profile, model, workspace, context, mapping or mode change goes through it. Explicit `resume()` creates another fresh session and WAIT_NEUTRAL; `pause()` cancels issued work. Deston's shell must restart or restamp capture against the new snapshot, never relabel an old queued prediction as fresh. A stage transition may call configure then resume in the same UI handler, retaining valid readiness but still requiring NEUTRAL. Profile/model changes and focus loss require explicit user resume.

`process(prediction, now)` emits at most one event per continuous hold. `route(event, now)` accepts only an exact event issued by this coordinator, once, with current identity/model and age no greater than 200 ms. Altered/stale events are consumed; repeating them cannot recover an action. Pause, tracking loss, rearming and generation changes invalidate pending events.

PREVIEW and REHEARSAL populate only `simulated_action`. LIVE populates `action`. This foundation does not establish readiness or launch anything. Before wiring LIVE, Deston must integrate Hau Jie's version-bound readiness gate and Javier's final validated dispatcher. Construction alone is not permission to execute OS actions.

All coordinator calls and immediate routing/dispatch belong on one owner thread. A RoutingResult is not a durable token: do not queue it for execution after a mode/profile/stage change. The final dispatcher must independently consume event IDs once and record outcomes. Camera release and any asynchronous action preparation require a fresh snapshot check before the side effect.

Manual actions use the same validated target/action handlers, labelled `source=manual`; do not manufacture a prediction or held-gesture event for a button click. Enrolment/practice must have no route to an actual external launcher. Actions are never executed on configuration import or state restoration.

## Verification and remaining work

Run `.\.venv\Scripts\python.exe -m pytest -q tests/test_controller.py tests/test_project_routing.py tests/test_viewer.py`.

Checks cover custom IDs, all typed actions, default NEXT-only behaviour, once-per-hold, identity/model/context/map/mode changes, malformed configuration, forged/altered/stale/duplicate events, pause/tracking loss and simulation isolation. These are software checks. Starter data, profile persistence, GUI integration, readiness scoring, actual launch handling and human/hardware evaluation remain assigned work; no test here establishes new-user recognition quality or Windows launch success.
