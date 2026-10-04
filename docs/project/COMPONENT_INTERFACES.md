# Component interfaces and dispatch contract

Current integration contract for the reviewed viewer, workspace, runbook,
shortcut and session-summary components. Provenance remains in
`JAVIER_DELIVERY_REVIEW.md`; historical Linux delivery checks are retained in
`../evidence/component-delivery-checks.json`, while current repository
verification is `verification.json`.

## Widgets

| Widget | Input | Requests / output |
|---|---|---|
| `ViewerWidget` | `Viewer(project_actions=True)` | `action_requested(Action)` for NEXT/PREVIOUS/BOOKMARK; `refresh()` after dispatch. Bookmark review and removal are explicit local UI operations. |
| `WorkspaceWidget` | validated `Workspace` | `workspace_changed(Workspace)` stages a fully validated import; `set_workspace()` synchronises authored edits. No target import. |
| `RunbookEditorWidget` | validated `Workspace` | `workspace_changed(Workspace)` after create/edit/reorder/delete; editor mutations never execute an action. |
| `RunbookWidget` | `Runbook` | `action_requested(Action)`, `previous_stage_requested()`, `completion_acknowledged(stage_id)`; `refresh()` after outcomes. |
| `QuickActionsWidget` | private `TargetRegistry`, optional local state path and keyword-only `before_publish() -> bool` | `action_requested(Action)`, `bindings_changed(tuple[(gesture_id, target_id_or_None), ...])`, `focus_lost()`; `set_gesture_ids()` accepts Hau Jie's actual three IDs. |
| `SessionSummaryWidget` | `SessionSummary` | measured counts and explicit JSON export; `refresh()` after outcomes/trials. |

Widget signals do not execute OS work. Studio routes typed manual requests through one persistent `Dispatcher.manual`
with a fresh UUID and `source=manual`, on the UI owner thread. Gesture dispatch must
immediately pass `RoutingSession.route`'s result AND the snapshot captured for that
same process/route call. Never persist/queue a result or look up the latest snapshot
later to restamp old work. All real viewer, stage and external actions share one
dispatcher instance and a bounded event-ID gate, retained across context changes.

## Current Studio Quick Actions attachment

Studio supplies the registry and private `.local/studio/quick-actions-targets.json`
state path. `before_publish` pauses capture before an atomic target/slot save; a
failed pause, active model load or closing shell refuses the change. Failed saves
leave the shared registry unchanged. `bindings_changed` clears active routing and
requires explicit **Use Quick Actions** activation. That button validates nonempty
slots and configures the complete map through `Window.configure_studio`; absent
or invalid targets leave routing paused/manual-only. The current vocabulary
supplies all three gesture IDs, including after a dataset switch.

Slot buttons and **Test selected target** call Studio
`manual_quick_action(Action)` through the persistent dispatcher. Preview/Rehearsal
produce simulated outcomes only; explicit LIVE permits manual validated Windows
launch requests without a recogniser. Unsupported platforms report an external-launch
failure while the manual viewer remains usable. Gesture simulation requires explicit
Start and NEUTRAL and works independently of deck/runbook content. Personal LIVE
uses the current full-Practice grant for the exact authored Quick Actions map,
after explicit Live selection, Apply, Start and fresh NEUTRAL. Selecting an
already configured Quick Actions context preserves that grant; changing target
meanings or slots expires it even if changed back. Tab selection does not activate a context.
Target values stay in the private local registry, outside workspace/session
exports. Reopening restores the library without activating it or replaying work.

## Attached manual dispatcher and personal gesture gate

Studio retains one `Dispatcher` across context changes, with these boundaries:

- `current()`: the current complete `RoutingSnapshot`.
- `active()`: true only while current routing is eligible for gesture dispatch.
- `ready(snapshot)`: the shell-owned personal LIVE gate, checked against the current
  in-memory full-Practice grant, profile/model/hand/camera/behavior revision and exact
  authored context map. The shell also requires current focus and no conflicting
  Practice, Enrolment or profile work. Neither a `RoutingMode.LIVE` snapshot, the
  preliminary six-activation check nor historical/imported results grants readiness.
- `pause()`: synchronously call `RoutingSession.pause()`; synchronise runbook pause
  and shell status. Returning/focus gain must never call resume automatically.
- `release_capture(snapshot)`: request shutdown of the existing capture worker and
  return true ONLY after its completed shutdown acknowledgement. The dispatcher
  revalidates snapshot/readiness and target immediately before opening Camera.
  No second camera worker. No sleeps as acknowledgements. A false result opens
  nothing and requires a new explicit request after release; it never replays.
- Matching optional `Viewer` / `Runbook`, private registry and `WindowsLauncher`.

Manual buttons can work while gesture routing is paused and without recognition
readiness. Preview/rehearsal manual requests still produce only `simulated` results.
Real manual shortcuts require the shell's explicitly chosen LIVE mode; do not
switch it implicitly because a button was clicked. Target tests use the same gate.
Typed manual viewer actions and Continue/ADVANCE_STAGE simulate in Preview/Rehearsal
and execute after explicit LIVE selection. Gesture equivalents require the
current full-Practice grant and normal protected routing. Previous-stage navigation, bookmark
review/removal, restart and restore remain explicit navigation operations outside
typed dispatch; none launches a target. Stage transitions stay paused, with no
deferred automatic resume.

`Runbook(reset_routing=...)` calls its callback BEFORE activation/restoration:
`reset_routing(stage_or_None, resume_requested) -> bool`. Deston must configure the
full profile/model/context/binding/mode map via `RoutingSession.configure`. LIVE
gesture execution requires the current full-Practice grant and the exact approved
authored map. Preview/Rehearsal can run the simulated check without prior readiness. Stage transitions and restoration stay paused. Return true only when the reset is
acknowledged. Exceptions/false preserve stage content. Configure an empty context
as paused/manual-only; the current coordinator requires a nonempty map, so do not
invent an enabled gesture binding to fill an empty map. The inspection harness
uses a visibly simulated placeholder solely to satisfy that API.

Behavior, map, target or camera changes pause/reset routing and permanently
expire the personal LIVE grant, even if changed back. Guest, model reload and
app restart clear it. Cosmetic renames, ordinary pause and selecting an existing
authored stage/Quick Actions context preserve eligibility; context changes still
reset holds and require explicit Start and fresh NEUTRAL. Retain assignment
controller defaults and its entry point. This gate does not establish participant
performance or native readiness/capture/focus acceptance.

SessionSummary accepts `Trial` records of Hau Jie's MEASURED expected/observed
canonical labels (UNKNOWN/None are misses). It does not predict trial scores or
create readiness evidence. Record retries explicitly. A launch request is never
converted to task completion; connect the current stage's acknowledgement button
separately. Exported outcomes include event/session/context/model IDs, monotonic
receipt time, source, typed action and bounded recovery reason, with no target
values. These receipt times are not gesture-onset latency measurements.

In Studio, **Edit runbook** mutates only validated workspace content. New, Save
stage, Delete, Move up and Move down never execute stage actions; accepted edits
must reset routing before activation. **Session summary** is a measured-results
surface: Refresh shows counts, and Export session results writes local JSON for
review. It is separate from saved runbook navigation, which uses the current
workspace plus stage/viewer state and is explicit rather than autosaved. The
summary scope uses workspace identity plus a generated review revision ID, not a
deterministic content hash. Correct/wrong/missed remain zero until measured
`Trial` records are supplied; zero is unmeasured, not evidence that the workflow
passed, and manual actions do not create automatic readiness evidence. Before a
deck/workspace replacement, session restore, restart or close would leave a
non-empty summary behind, Studio archives it under ignored `.local/studio`;
archive failure blocks the operation and keeps the current counts visible.

Event capacity is fail-closed: after 4,096 unique requests, export and start a new
application session/dispatcher under a fresh routing identity. Outcome recording
is separately bounded at 10,000 rows and checked before side effects. Never evict
consumed IDs within a session. `Dispatcher` is not a security boundary against a
caller constructing forged Python records; only route-issued gesture results and
fresh manual requests belong at this trusted shell boundary.

## Profile persistence handoff

The reviewed `ProfileStore` component returns a rebuilt `LoadedProfile` candidate;
see [PROFILE_PERSISTENCE_HANDOFF.md](PROFILE_PERSISTENCE_HANDOFF.md). Hau Jie owns
the create/rename/load/delete selector widget attached in Studio's Profiles tab. Deston owns
background candidate loading, shell installation and clearing an active deleted
profile. These shell APIs are now implemented: `load_studio_profile`,
`use_studio_profile`, `use_studio_guest`, `prepare_studio_profile_delete` and `clear_studio_profile`.
Use the documented synchronous prepare/delete/clear sequence and retain state on
storage failure. Guest unloads the model without deleting saved files. The shell
handles cosmetic rename and explicit Preview-start notifications and blocks competing
setup operations while the selector is busy. Successful reconstruction stays paused
and does not establish readiness; loading or reloading clears any personal LIVE
grant. Only the host's genuine current-session full Practice attempt can grant
eligibility after all 50 covered windows, at least 9/10 correct for every pose
including NEUTRAL, zero wrong activations and all ten negative windows correct,
followed by terminal save, exact event reconciliation and paused restoration.
The memory-only grant never selects LIVE or starts capture automatically. Saved
loading reuses the existing model worker. See [the selector handoff](PROFILE_SELECTOR_HANDOFF.md).

## Remaining gates

GF-P05 is accepted from PR #18's supplied [laptop-A observations and repair rerun](../evidence/WINDOWS_RESULTS_2026-10-02.md); no further GF-P05 rerun is pending. Javier should sync main and verify the attached GF-P13/GF-P34 manual path, including exact snapshots, duplicate/stale requests, capture-release refusal and simulation-only outcomes, then record GF-P19's integrated Windows cases. Hau Jie supplies actual full Practice evidence and short software-defect reproductions; Deston owns the integrated shell gate and acceptance review. Javier runs personal LIVE cases only after his own qualifying current-session full pass. The short six-activation result is preliminary and cannot authorise live gestures. Standard starter availability, full personal readiness and broader both-laptop evidence remain separate. Keep shared shell,
contracts/controller/routing, capture and recognition/profile changes in their
owned lanes.
