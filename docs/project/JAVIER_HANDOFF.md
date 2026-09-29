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

1. **GF-P05 by 4 October — Windows launch probes.** In a small local probe, verify Calculator, Camera, a permitted reference file, a folder and HTTPS opening. Record actual launch/error behaviour on Windows. Camera must wait for GestureForge's capture worker to release the device before opening; return/resume is manual. A successful OS request means `launch requested`, not application ready. Do not wire gesture launches into the current assignment window.
2. **GF-P08 by 11 October — complete viewer.** Extend `viewer.py` with NEXT/PREVIOUS and idempotent BOOKMARK, explicit bookmark removal/review, no wrap at boundaries, validated custom decks and saved position/bookmarks. Keep the built-in assignment deck usable. Preserve assignment controller defaults until Deston enables the project path. Test duplicate IDs, boundaries, corrupt state and atomic recovery.
3. **GF-P09 then GF-P29 by 11 October — workspace and runbook.** Build a validated portable JSON workspace and an embeddable list/form editor for ordered stages. Provide clear authored instructions and action mappings; changing stages must go through Deston's routing reset. No external actions execute merely from loading a workspace, restoring state or entering a stage.

## Complete your lane

| Task | Deliverable | Due |
|---|---|---|
| GF-P13 | Bounded dispatcher and local target editor | 18 Oct |
| GF-P31 | Rehearsal/session summary using Hau Jie's measured events and actual task outcomes | 18 Oct |
| GF-P34 | Standalone Quick Actions, twelve-target library and three active gesture slots | 18 Oct |
| GF-P19 | Both-laptop shortcut, validation and recovery evidence | 25 Oct |
| GF-P22 | Viewer/storage/shortcut/runbook defects resolved | 1 Nov |
| GF-P25 | Accurate installation/user guide and full demo video draft | 6 Nov |

Estimate 73 base hours, about 88 with contingency. GF-P34's dependency on GF-P10 is the final integration gate; target validation and standalone widget unit tests can start earlier.

## Ownership and shared interfaces

Own `gestureforge/viewer.py`, its tests and new modules such as `workspace.py`, `shortcuts.py` and `runbook.py` only where needed. Supply embeddable PySide6 widgets. Do not rewrite `app.py`, `__main__.py`, `contracts.py`, `controller.py`, `routing.py` or Hau Jie's recognition/profile modules. Send Deston a short widget signal/function proposal before attaching it to the shell; those attachment interfaces are not yet implemented.

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

> Work on my GestureForge project lane. Read docs/project/TEAM_GUIDE.md, JAVIER_HANDOFF.md and CONTRACTS.md plus the supplied project plan. Start with GF-P05 as an isolated Windows launch probe and GF-P08 viewer tests. I own viewer/workspace/runbook/shortcut modules; do not edit app.py, contracts.py, controller.py, routing.py or recognition/profile files. Use existing dependencies and argument-safe native launch operations; no shell macros or background global controls. Keep real launches out of practice, validate local targets and never replay launches on restore. Preserve the assignment entry point and tests. Do not commit/push main or edit reports/logs. Return focused changes, runnable tests, actual probe evidence and a small interface proposal for Deston's integration.
