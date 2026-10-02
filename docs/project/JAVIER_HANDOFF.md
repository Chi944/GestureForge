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

Update, 2 October: your delivered components were reviewed, corrected and merged through PR #11; see [the integration review](JAVIER_DELIVERY_REVIEW.md). Do not reapply the ZIP patch or rebuild those components. Sync the reviewed main into your own branch, preserving local work. The viewer, workspace, runbook editor/navigation, session summary and Quick Actions simulation are attached to Studio. The [4 October checkpoint](JAVIER_OCT4_CHECKPOINT.md) preserves your historical 373-test Linux/offscreen run. GF-P05 is now accepted from PR #18's supplied [laptop-A observations and focused repair rerun](../evidence/WINDOWS_RESULTS_2026-10-02.md), including refused failed-dispatch confirmation, recorded missing-target failure and successful recovery. Integration review did not independently repeat those native observations; no further GF-P05 rerun is pending.

Do not recollect P03 unless Hau Jie asks for a repair sample. The merged [PR #13 checkpoint](STARTER_EVALUATION_CHECKPOINT.md) reports P02/P03 collection and validation, with poor recognition/rejection results. Those measurements are supplied by Hau Jie; integration review independently checked the evaluator software. Preserve the accepted GF-P05 report and private probe JSON. Next, use [COMPONENT_INTERFACES.md](COMPONENT_INTERFACES.md) to prepare GF-P13/GF-P34's bounded dispatcher and Quick Actions attachment with Deston: exact routing snapshots, version-bound readiness, duplicate suppression, acknowledged Camera release and explicit manual/simulated/real outcomes. Supply focused contract tests and identify callback gaps; Deston owns shell changes and LIVE attachment. Full GF-P19 testing on both laptops, including isolated focus-loss and integrated error/recovery cases, remains separate work.

1. **GF-P13/GF-P34 by 18 October - prepare bounded dispatch and Quick Actions integration.** Reuse the delivered dispatcher, registry and attached widget. Verify the documented callbacks and target revision handling with focused tests, covering stale/duplicate requests, capture-release refusal and zero OS side effects in Preview/Rehearsal. Resolve interface gaps with Deston before shell attachment; the short simulated readiness check alone does not authorise LIVE. GF-P05 is complete; GF-P19's both-laptop native evidence follows integration.
2. **GF-P08/GF-P09/GF-P29 - maintain the delivered viewer, workspace and runbook.** These components are already implemented. Fix evidenced boundary, bookmark, validation, save-recovery or editor defects with focused regression tests; do not rebuild them. Track each task against its own acceptance criteria in [TEAM_BACKLOG.csv](TEAM_BACKLOG.csv).
3. **GF-P25 - keep the guide and demo draft current.** Document the reviewed Studio controls and actual Windows probe outcomes. Distinguish simulation, real launch requests and acknowledged task completion. Prepare GF-P19's both-laptop checks after readiness and real dispatch are integrated; do not label unrun cases as passed.

## Complete your lane

| Task | Deliverable | Due |
|---|---|---|
| GF-P13 | Validate the delivered dispatcher/target editor with integrated readiness and Windows evidence | 18 Oct |
| GF-P31 | Validate the delivered summary with Hau Jie's measured trials and actual task outcomes | 18 Oct |
| GF-P34 | Validate the attached Quick Actions/library workflow against its task criteria | 18 Oct |
| GF-P19 | Both-laptop shortcut, validation and recovery evidence | 25 Oct |
| GF-P22 | Viewer/storage/shortcut/runbook defects resolved | 1 Nov |
| GF-P25 | Accurate installation/user guide and full demo video draft | 6 Nov |

Estimate 73 base hours, about 88 with contingency. GF-P34's dependency on GF-P10 is the final integration gate; target validation and standalone widget unit tests can start earlier.

## Ownership and shared interfaces

Own `gestureforge/viewer.py`, `workspace.py`, `shortcuts.py`, `runbook.py`, the supplied widgets and their tests. Do not rewrite `app.py`, `__main__.py`, `contracts.py`, `controller.py`, `routing.py` or Hau Jie's recognition/profile modules. Use the implemented interfaces in [COMPONENT_INTERFACES.md](COMPONENT_INTERFACES.md); send any required interface change to Deston before changing the shared shell.

Use the shared `Action` and `ActionType` from `CONTRACTS.md`. OPEN_SHORTCUT carries an opaque shortcut ID. Resolve it through the local registry after current-session routing and immediately before launch. Never accept arbitrary paths from a classifier label or portable workspace. Viewer commands use the same routing path as external actions; the final dispatcher needs one shared duplicate-event gate across all real actions, including manual requests identified as manual.

`RoutingResult.action` is eligible only in LIVE mode after Deston's readiness check. PREVIEW/REHEARSAL return `simulated_action` and must not reach OS launch. Process, route and dispatch synchronously on the UI owner thread; do not queue a result past a context change. OS work requiring asynchronous completion must validate the current session before each side effect. Capture shutdown is an explicit acknowledgement, not a sleep.

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

## Starter prompt for your coding assistant

Include this branch instruction with the task prompt: **Work only on `codex/javier-shortcuts`. Before every commit or push, verify the current branch. When asked to publish, push only this branch and open a PR to `main` for Deston; never push or merge directly into `main` or another member's branch.**

> Continue on codex/javier-shortcuts after syncing the reviewed main. Read TEAM_GUIDE.md, JAVIER_HANDOFF.md, COMPONENT_INTERFACES.md and CONTRACTS.md. Preserve the accepted GF-P05 laptop-A evidence and repair rerun; do not repeat that completed task. Prepare GF-P13/GF-P34's dispatcher and Quick Actions integration contract with focused tests for exact snapshots, readiness revisions, duplicate/stale requests, acknowledged Camera release and zero OS side effects in Preview/Rehearsal. Reuse the delivered components and report callback gaps to Deston before attachment; leave app.py, shared routing and recognition/profile files to their owners. GF-P19's isolated focus-loss, broader errors and both-laptop integrated evidence follow integration. Do not recollect P03 unless Hau Jie asks for repair data. Preserve assignment behaviour and mark unrun cases honestly. Push only my branch and open a focused PR for Deston; do not merge into main or edit private reports/logs.
