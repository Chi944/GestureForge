# Javier implementation brief

You own the viewer, workspaces, runbooks and desktop shortcuts for GestureForge Studio. Build and test these product components; Deston owns the common shell, routing safety and final acceptance. Read `TEAM_GUIDE.md` and `CONTRACTS.md` before coding.

## Your branch and delivery rule

Create `codex/javier-shortcuts` from the published `origin/main` before editing. Do not apply the old kickoff patch on top of it. If it already exists, switch to it instead. Commit and push only to this branch; never push to `main` or Hau Jie's branch.

```powershell
git fetch origin
git switch -c codex/javier-shortcuts origin/main
git branch --show-current
# After reviewing your changes, committing and passing the required checks:
git push -u origin codex/javier-shortcuts
```

Before every commit/push, confirm the current branch is `codex/javier-shortcuts`. Open a PR from this branch into `main`, request Deston's review, and leave it unmerged. Only Deston integrates approved work into `main`; do not force-push shared history.

## Start with these tasks

**Current assignment:** finish reproducible software fixes and checks
before requesting new manual evidence. After Deston hands over the reviewed
software checkpoint, you execute the following acceptance work. Deston retains
interface design, integration, acceptance decisions and final review; the existing
backlog owners and weights remain unchanged, and delegation earns no Done credit.

1. Run the [camera-free six-stage Harbor walkthrough](DEMO_SCENARIO.md#manual-walkthrough-available-now)
   using manual LIVE controls. No profile, webcam or gesture recording is needed.
   Record actual task outcomes and failures, missing-target recovery, paused
   save/reload with no replay, and both Session summary segments. A launch request
   is not a human task acknowledgement.
2. Record GF-P19's remaining Windows device/launch/recovery cases on both laptops,
   including target validation, trusted app/HTTPS selection, focus return and the
   separate Camera release/recovery check. Preserve accepted GF-P05 evidence.
3. Execute the Windows installation/offline evidence slice for Deston's GF-P23
   review: identify the device and source revision, use the documented setup,
   and observe the local workflow after setup without internet. Keep HTTPS and
   external apps' online features separate. Mark unavailable/unrun cases honestly;
   software tests do not establish native or human acceptance.

Update, 2 October: your delivered components were reviewed, corrected and merged through PR #11; see [the integration review](JAVIER_DELIVERY_REVIEW.md). Do not reapply the ZIP patch or rebuild those components. Sync the reviewed main into your own branch, preserving local work. The viewer, workspace, runbook editor/navigation, session summary and Quick Actions simulation are attached to Studio. The [4 October checkpoint](JAVIER_OCT4_CHECKPOINT.md) preserves your historical 373-test Linux/offscreen run. GF-P05 is now accepted from PR #18's supplied [laptop-A observations and focused repair rerun](../evidence/WINDOWS_RESULTS_2026-10-02.md), including refused failed-dispatch confirmation, recorded missing-target failure and successful recovery. Integration review did not independently repeat those native observations; no further GF-P05 rerun is pending.

Bounded update, 3 October: you do not need to wait for a full starter recogniser to continue your lane. On `codex/javier-shortcuts`, verify the integrated manual LIVE path on Windows through the attached six-stage Harbor scenario and preserve the existing PR #18/GF-P05 evidence separately. Record actual targets used, target validation results, missing-target failure, Camera release/recovery, reload behaviour and session-summary entries around reload. Do not promise native Mac external launch support; treat it as unsupported unless separately verified on native macOS. Keep all private reports/logs unchanged and keep fixes inside your owned viewer/workspace/shortcut/runbook components unless Deston requests a shared-shell change.

Do not recollect P03 unless Hau Jie asks for a repair sample. The merged [PR #13 checkpoint](STARTER_EVALUATION_CHECKPOINT.md) reports P02/P03 collection and validation, with poor recognition/rejection results. Those measurements are supplied by Hau Jie; integration review independently checked the evaluator software. Preserve the accepted GF-P05 report and private probe JSON. Sync main and use [COMPONENT_INTERFACES.md](COMPONENT_INTERFACES.md) to verify Deston's attached GF-P13/GF-P34 manual dispatch path: one persistent dispatcher, exact snapshots, duplicate suppression, acknowledged Camera release and distinct simulated/manual/launch outcomes. Explicit LIVE allows manual actions without a model; Preview/Rehearsal simulate typed actions. PR #21's longer rehearsal component is attached in Practice. Deston's shared-shell review now reconciles its saved event IDs with frozen dispatcher outcomes under Session summary. Both that measured result and the short six-event check remain separate from LIVE permission; live gestures are still blocked. Fix evidenced component defects and report shell issues to Deston rather than duplicating the attachment. GF-P19 then records the integrated Windows cases on both laptops, including isolated focus loss and error/recovery behaviour.

1. **GF-P13/GF-P34 by 18 October - verify the attached manual dispatch and Quick Actions path.** Sync main and reuse the persistent dispatcher, registry and widget. Verify callbacks and target revision handling, stale/duplicate requests, capture-release refusal and simulation isolation against the attached shell. Previous-stage navigation, bookmark review/removal, restart and restore remain explicit operations outside typed dispatch; stage transitions stay paused. Report shell defects to Deston and fix owned component defects with focused regressions. GF-P05 is complete; preserve that evidence and record GF-P19's broader integrated Windows cases separately.
2. **GF-P08/GF-P09/GF-P29 - maintain the delivered viewer, workspace and runbook.** These components are already implemented. Fix evidenced boundary, bookmark, validation, save-recovery or editor defects with focused regression tests; do not rebuild them. Track each task against its own acceptance criteria in [TEAM_BACKLOG.csv](TEAM_BACKLOG.csv).
3. **GF-P31 - review the attached historical Practice view.** Deston has added the host reconciliation; do not build a second attachment or change the legacy Trial/export schema. Use Practice's saved local result together with the persistent session-summary outcomes. Match each simulated event ID once; keep per-pose correct/wrong/missed outcomes separate from manual actions, launch requests and acknowledged task completion. Fifty timed windows are not fifty actions: NEUTRAL and negative windows should emit none. Do not relabel simulated counts as successful Windows launches. Report any shared-shell mismatch to Deston and fix summary-component defects in your branch.
4. **GF-P25 - keep the guide and demo draft current.** Document the reviewed Studio controls and actual Windows outcomes. Distinguish Preview/Rehearsal simulations, explicit LIVE manual requests and acknowledged task completion. Record which GF-P19 integrated cases were actually run; live-gesture cases still require the full personal readiness handoff.

## Complete your lane

| Task | Deliverable | Due |
|---|---|---|
| GF-P13 | Validate the delivered dispatcher/target editor with integrated readiness and Windows evidence | 18 Oct |
| GF-P31 | Software complete: saved Practice review and event reconciliation attached; retain real results under GF-P12/GF-P19 | Accepted 3 Oct |
| GF-P34 | Validate the attached Quick Actions/library workflow against its task criteria | 18 Oct |
| GF-P19 | Both-laptop shortcut, validation and recovery evidence | 25 Oct |
| GF-P22 | Viewer/storage/shortcut/runbook defects resolved | 1 Nov |
| GF-P25 | Accurate installation/user guide and full demo video draft | 6 Nov |

Estimate 73 base hours, about 88 with contingency. GF-P34's dependency on GF-P10 is the final integration gate; target validation and standalone widget unit tests can start earlier.

## Ownership and shared interfaces

Own `gestureforge/viewer.py`, `workspace.py`, `shortcuts.py`, `runbook.py`, the supplied widgets and their tests. Do not rewrite `app.py`, `__main__.py`, `contracts.py`, `controller.py`, `routing.py` or Hau Jie's recognition/profile modules. Use the implemented interfaces in [COMPONENT_INTERFACES.md](COMPONENT_INTERFACES.md); send any required interface change to Deston before changing the shared shell.

Use the shared `Action` and `ActionType` from `CONTRACTS.md`. OPEN_SHORTCUT carries an opaque shortcut ID. Resolve it through the local registry after current-session routing and immediately before launch. Never accept arbitrary paths from a classifier label or portable workspace. Viewer commands use the same routing path as external actions; the final dispatcher needs one shared duplicate-event gate across all real actions, including manual requests identified as manual.

`RoutingResult.action` is eligible only in LIVE mode after full revision-bound personal readiness; the shell currently refuses live gestures. PREVIEW/REHEARSAL return `simulated_action` and must not reach OS launch. Explicit LIVE manual requests use the same persistent dispatcher without recognition readiness. Process, route and dispatch synchronously on the UI owner thread; do not queue a result past a context change. OS work requiring asynchronous completion must validate the current session before each side effect. Capture shutdown is an explicit acknowledgement, not a sleep.

## Bounded product behaviour

- Deck: optional for Quick Actions; if supplied, 1–100 cards, unique IDs up to 64 characters, titles up to 120, body up to 8,000. Keep plain text. Validate before replacing the active deck.
- Runbook: optional, 1–12 ordered stages, up to three single actions per stage, valid card/shortcut references and visible continue/finish path. Always provide previous-stage and other manual buttons. No executable code, loops or action chains.
- Workspace import: supported version and maximum 1 MiB; reject unknown actions, duplicate IDs, broken references and executable/credential fields. Entire import succeeds before active state changes. Export semantic slots only, never local targets or personal profiles/data. Each machine rebinds and tests targets.
- Local library: at most twelve named targets with labels up to 80 characters. Quick Actions can start and reload without a deck/runbook and exposes three active gesture bindings.
- App: built-in Calculator/Camera adapters or user-selected existing trusted local `.exe`. No shell/interpreter, arbitrary arguments, scripts, network share, device path, `.lnk` or `.url` target.
- Reference file: existing local PDF/TXT/PNG/JPEG only. Folder: existing resolved local directory. Validate at configuration and dispatch, reject remote/device paths and handle missing targets/associations clearly.
- Website: parsed HTTPS, nonempty host, no embedded credentials, maximum 2,048 characters. No custom protocol or browser automation. URL bindings remain local; site access may require internet.
- Launch using argument-safe native facilities, not constructed shell commands. Focus loss pauses GestureForge; explicit resume on returning. Opening Camera first pauses, releases capture and confirms shutdown. Failed launch leaves the stage active and shows a retry/manual path.
- Save state atomically. Reload restores card/stage/bookmarks but remains paused and never replays past launches. Bookmarks set once; removal is an explicit separate UI action.
- Session summary distinguishes simulated triggers, real launch requests, failures and user-acknowledged completion. Opening Calculator does not prove the user completed a calculation.

## Tests and review evidence

Automate viewer boundaries and deduplication, bookmark round trips, corrupt/incompatible/oversized workspace import, unknown action types, missing references, export privacy, independent target bindings, invalid path/scheme/file types, missing association/target, repeated event IDs, no side effects during simulation, no launch on state restore, and empty-content Quick Actions.

Use fake OS adapters for automated tests; real Windows probes separately verify all target types, focus loss, Camera handoff and recovery on both laptops. Do not claim the fake proves the real application opens. Include exact commands/results, actual OS information and limitations with the PR. Run the common lint/type/full-test checks in `TEAM_GUIDE.md`.

## Integration follow-up — 4 October

Deston's automated native Harbor dispatch run now covers Calculator, fictional
TXT/folder requests, missing-target recovery, bookmark persistence, paused reload
and no replay, with 124 passing assertions and matching OS window metadata.
It records zero human task acknowledgements and no gesture trials. Preserve this
as automated native evidence; do not relabel it as human acceptance. The remaining
work is actual task outcomes, HTTPS/app selection, Camera/focus recovery and the
required integrated checks on both laptops. Practice timing and saved next-step
guidance are integrated; do not implement a second version.

## Starter prompt for your coding assistant

For GF-P19/GF-P23 camera timing or shutdown problems, use the shared
[capture stability diagnostic](../USER_GUIDE.md#capture-stability-diagnostic)
before another long recording. It requires no pose sequence and saves a compact
private JSON. Include the existing personal dataset to time classification too.
Keep native launch observations and Studio UI acceptance separate: a successful
pipeline diagnostic does not prove either. Do not build a second capture logger.

Include this branch instruction with the task prompt: **Work only on `codex/javier-shortcuts`. Before every commit or push, verify the current branch. When asked to publish, push only this branch and open a PR to `main` for Deston; never push or merge directly into `main` or another member's branch.**

> Work only on `codex/javier-shortcuts`; sync the reviewed fix commit and read TEAM_GUIDE.md, this brief and CONTRACTS.md. Complete reproducible software fixes/checks first. Then execute the camera-free manual Harbor walkthrough, recording actual task outcomes, recovery and both summary segments around paused reload. Separately gather the remaining Windows device/launch/focus/Camera recovery evidence on both laptops and the fresh-install/offline local-workflow evidence for Deston's review. Preserve accepted GF-P05 results; distinguish simulated actions, launch requests and human acknowledgements, and mark unrun cases honestly. Fix only your viewer/workspace/runbook/shortcut/summary modules and tests; report shell issues to Deston. Verify the branch before every commit/push; push only this branch and open a focused PR for Deston's integration and final review, leaving it unmerged. Do not push or merge into `main`, change task weights/status to claim delegated work is done, or publish private data/logs.
