# Javier implementation brief

You own the viewer, workspaces, runbooks and desktop shortcuts for GestureForge Studio. Build and test these product components; Deston owns the common shell, routing safety and final acceptance. Read `TEAM_GUIDE.md` and `CONTRACTS.md` before coding.

## Laptop B assignment confirmed 5 October

**Laptop A is your existing Windows computer; laptop B is Hau Jie's physical Windows laptop.** You coordinate GF-P19 and consolidate the per-device results. Hau Jie installs and operates laptop B; Deston retains final acceptance, including GF-P23. You do not need another laptop. This assignment adds no completed test result.

Give Hau Jie the current source commit/package hash, the Windows setup guide and the cases below. Agree which remaining case runs on which machine so accepted laptop-A observations are preserved. Hau Jie records himself as operator and returns actual observations, failures/retries, source/OS/camera identity and private evidence references. Use his own profile for gesture cases; manual checks need no profile. Review his record without claiming you personally operated laptop B. Submit a focused evidence PR from `codex/javier-shortcuts`; reference Hau Jie's operator record and keep raw/private exports out of Git/Trello. Neither the assignment's older second-laptop test nor a copied environment verifies the current Studio release.

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

**PR #24 reviewed and merged, 5 October:** preserve your [Harbor laptop-A evidence](../evidence/GF_P19_HARBOR_LAPTOP_A_2026-10-04.md). Do not repeat the whole walkthrough. Deston now mirrors dispatch outcomes into the top notice so failures remain visible without scrolling. On your next affected check, verify the message and recovery on current main. Continue the missing laptop-B, target-association and active-capture recovery cases, then GF-P23. This PR does not close GF-P19. The standard starter path is implemented but remains unavailable until a qualifying permitted model is reviewed.

**Current assignment:** you execute the following acceptance work after syncing
the reviewed software checkpoint into your own branch. Fix reproducible software
defects before repeating affected manual checks. Deston retains interface design,
integration and final acceptance; follow these priorities.

**Acceptance update, 5 October:** GF-P13 is Done against its original
dispatcher, no-shell and camera-recovery criteria. The review combines current
software checks with your attributed laptop-A Camera observations; it does not
claim another physical run. Preserve that evidence instead of repeating GF-P13.
GF-P34 still has the original GF-P10 integration dependency. Its standalone
software checks can proceed before a qualifying standard starter exists, but
they cannot close that dependency. The two-laptop integrated cases below remain
GF-P19, and independent installation/stability remains GF-P23.

1. **Camera-free Harbor first.** Run the [six-stage manual walkthrough](DEMO_SCENARIO.md#manual-walkthrough-available-now)
   in manual LIVE mode without a profile or webcam. **Return:** source revision,
   device/Windows version, observed stage outcomes and acknowledgements, failures
   and retries, missing-target recovery, paused reload/no-replay observations and
   both Session summary segments. A launch request is not a human task outcome.
2. **GF-P19 native recovery.** Follow the [Windows verification procedure](../evidence/WINDOWS_LAUNCH_PROCEDURE.md)
   for the remaining integrated cases on both laptops: app/file/folder/HTTPS
   targets, invalid/missing target or association, focus return, explicit retry,
   and separate Camera release/recovery. Preserve accepted GF-P05 evidence.
   **Return:** a per-device case/result summary with OS/Python/camera details,
   source revision, exact commands, observed launches/errors/recovery and local
   evidence references. Mark inaccessible devices and unrun cases explicitly.
3. **GF-P23 execution for Deston's review.** Use the [Windows setup guide](../WINDOWS_LAPTOP.md)
   for a fresh independent installation on the second Windows laptop; do not
   copy an environment. Verify the
   local workflow offline after dependencies/assets are installed, then record
   the thirty-minute Studio workflow/stability and clean shutdown evidence.
   Keep HTTPS and external apps' online features separate from offline core.
   **Return:** device/source identity, guide steps and any help/deviations,
   installation and offline outcomes, actual run duration, faults/recoveries,
   measured observation rate/peak memory where available, and shutdown result.
   Label unmeasured metrics and unrun cases; a short capture diagnostic does not
   replace the full Studio run or independent-machine acceptance.

4. **Personal LIVE only after your own full Practice pass.** Configure the
   intended workspace, stage maps and Quick Actions targets first. If you run
   gesture cases, use your own consented profile and complete a genuine full
   50-window pass in that app session: every window covered, at least 9/10
   correct for each pose including NEUTRAL, zero wrong activations and all ten
   negatives correct. Wait for save, exact event reconciliation and paused
   restoration; then select **Live**, **Apply and pause**, explicitly Start and
   show fresh NEUTRAL. Record the granted identity/revision, once-per-hold action,
   explicit stage/Quick Actions resume, camera-release refusal/retry and no
   automatic replay. Keep unrun gesture cases explicit if the pass is unavailable;
   manual Harbor and native recovery work can still proceed without a profile.

The personal LIVE grant exists only in memory for the exact profile/model/hand,
camera, behavior revision and authored workspace/stage/Quick Actions maps.
Behavior, mapping, target or camera edits expire it even if changed back;
restarting Studio, Guest and model reload clear it. Cosmetic renames, ordinary
pause and existing context selection preserve it, but resume always requires
Start and fresh NEUTRAL. The short check, diagnostics and historical/imported
JSON never grant it. Native acceptance and human task completion remain separate;
standard starter gestures remain unavailable.

Put a concise outcome summary and exact software check results in a focused PR;
keep raw exports, private paths and participant records local. Fix only your
owned modules and report shared-shell defects to Deston with a reproduction.
You do not need Deston to repeat long trials. Use your own consented profile if
a camera/recognition check needs one, and attribute its results to that profile;
it cannot replace Deston's P01 personal-performance evidence. Existing backlog
owners/weights remain unchanged, including Deston's GF-P23 accountability.
Delegation and software tests alone do not mark native/human acceptance Done.

Update, 2 October: your delivered components were reviewed, corrected and merged through PR #11; see [the integration review](JAVIER_DELIVERY_REVIEW.md). Do not reapply the ZIP patch or rebuild those components. Sync the reviewed main into your own branch, preserving local work. The viewer, workspace, runbook editor/navigation, session summary and Quick Actions simulation are attached to Studio. The [4 October checkpoint](JAVIER_OCT4_CHECKPOINT.md) preserves your historical 373-test Linux/offscreen run. GF-P05 is now accepted from PR #18's supplied [laptop-A observations and focused repair rerun](../evidence/WINDOWS_RESULTS_2026-10-02.md), including refused failed-dispatch confirmation, recorded missing-target failure and successful recovery. Integration review did not independently repeat those native observations; no further GF-P05 rerun is pending.

Bounded update, 3 October: you do not need to wait for a full starter recogniser to continue your lane. On `codex/javier-shortcuts`, verify the integrated manual LIVE path on Windows through the attached six-stage Harbor scenario and preserve the existing PR #18/GF-P05 evidence separately. Record actual targets used, target validation results, missing-target failure, Camera release/recovery, reload behaviour and session-summary entries around reload. Do not promise native Mac external launch support; treat it as unsupported unless separately verified on native macOS. Keep all private reports/logs unchanged and keep fixes inside your owned viewer/workspace/shortcut/runbook components unless Deston requests a shared-shell change.

Do not recollect P03 unless Hau Jie asks for a repair sample. The merged [PR #13 checkpoint](STARTER_EVALUATION_CHECKPOINT.md) reports P02/P03 collection and validation, with poor recognition/rejection results. Those measurements are supplied by Hau Jie; integration review independently checked the evaluator software. Preserve the accepted GF-P05 report and private probe JSON. Sync main and use [COMPONENT_INTERFACES.md](COMPONENT_INTERFACES.md) to preserve accepted GF-P13 and complete GF-P34 integration checks: one persistent dispatcher, exact snapshots, duplicate suppression, acknowledged Camera release and distinct simulated/manual/launch outcomes. Explicit LIVE allows manual actions without a model; Preview/Rehearsal simulate typed actions. PR #21's longer rehearsal component is attached in Practice. Deston's shared-shell review now reconciles its saved event IDs with frozen dispatcher outcomes under Session summary. The short six-event check and historical review cannot grant LIVE permission. A genuine current-session full Practice pass can grant temporary personal LIVE eligibility after save, exact event reconciliation and paused restoration; explicit LIVE selection, Apply, Start and fresh NEUTRAL are still required. Fix evidenced component defects and report shell issues to Deston rather than duplicating the attachment. GF-P19 then records the integrated Windows cases on both laptops, including isolated focus loss and error/recovery behaviour.

1. **GF-P13 accepted; GF-P34 integration remains.** Sync main and reuse the persistent dispatcher, registry and widget. Preserve duplicate suppression, typed target validation, capture-release refusal and simulation isolation. GF-P34's original final gate still depends on GF-P10; standalone software verification is recorded separately in [PROGRESS.md](PROGRESS.md). Previous-stage navigation, bookmark review/removal, restart and restore remain explicit operations outside typed dispatch; stage transitions stay paused. Fix demonstrated component defects with focused regressions and return shared-shell issues to Deston. Record GF-P19's broader integrated Windows cases separately.
2. **GF-P08/GF-P09/GF-P29 - maintain the delivered viewer, workspace and runbook.** These components are already implemented. Fix evidenced boundary, bookmark, validation, save-recovery or editor defects with focused regression tests; do not rebuild them. Track each task against its own acceptance criteria in [TEAM_BACKLOG.csv](TEAM_BACKLOG.csv).
3. **GF-P31 - review the attached historical Practice view.** Deston has added the host reconciliation; do not build a second attachment or change the legacy Trial/export schema. Use Practice's saved local result together with the persistent session-summary outcomes. Match each simulated event ID once; keep per-pose correct/wrong/missed outcomes separate from manual actions, launch requests and acknowledged task completion. Fifty timed windows are not fifty actions: NEUTRAL and negative windows should emit none. Do not relabel simulated counts as successful Windows launches. Report any shared-shell mismatch to Deston and fix summary-component defects in your branch.
4. **GF-P25 - keep the guide and demo draft current.** Document the reviewed Studio controls and actual Windows outcomes. Distinguish Preview/Rehearsal simulations, explicit LIVE manual requests and acknowledged task completion. Record which GF-P19 integrated cases were actually run; live-gesture cases still require the full personal readiness handoff.

## Complete your lane

| Task | Deliverable | Due |
|---|---|---|
| GF-P13 | Accepted bounded dispatcher and target editor; preserve attributed Camera recovery evidence | Accepted 5 Oct |
| GF-P31 | Software complete: saved Practice review and event reconciliation attached; retain real results under GF-P12/GF-P19 | Accepted 3 Oct |
| GF-P34 | Validate the attached Quick Actions/library workflow against its task criteria | 18 Oct |
| GF-P19 | Both-laptop shortcut, validation and recovery evidence | 25 Oct |
| GF-P22 | Viewer/storage/shortcut/runbook defects resolved | 1 Nov |
| GF-P25 | Accurate installation/user guide and full demo video draft | 6 Nov |

Estimate 73 base hours, about 88 with contingency. GF-P34's dependency on GF-P10 is the final integration gate; target validation and standalone widget unit tests can start earlier.

## Ownership and shared interfaces

Own `gestureforge/viewer.py`, `workspace.py`, `shortcuts.py`, `runbook.py`, the supplied widgets and their tests. Do not rewrite `app.py`, `__main__.py`, `contracts.py`, `controller.py`, `routing.py` or Hau Jie's recognition/profile modules. Use the implemented interfaces in [COMPONENT_INTERFACES.md](COMPONENT_INTERFACES.md); send any required interface change to Deston before changing the shared shell.

Use the shared `Action` and `ActionType` from `CONTRACTS.md`. OPEN_SHORTCUT carries an opaque shortcut ID. Resolve it through the local registry after current-session routing and immediately before launch. Never accept arbitrary paths from a classifier label or portable workspace. Viewer commands use the same routing path as external actions; the final dispatcher needs one shared duplicate-event gate across all real actions, including manual requests identified as manual.

`RoutingResult.action` is eligible for personal gestures only in explicitly selected LIVE mode with the current in-memory full-Practice grant and the exact approved context map. PREVIEW/REHEARSAL return `simulated_action` and must not reach OS launch. Explicit LIVE manual requests use the same persistent dispatcher without recognition readiness. Process, route and dispatch synchronously on the UI owner thread; do not queue a result past a context change. OS work requiring asynchronous completion must validate the current session before each side effect. Capture shutdown is an explicit acknowledgement, not a sleep.

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

> Work only on `codex/javier-shortcuts`; sync reviewed main and read TEAM_GUIDE.md, this brief and CONTRACTS.md. Preserve accepted laptop-A observations. Laptop B is Hau Jie's physical Windows laptop: coordinate the remaining GF-P19 case matrix with him as operator, using the same identified build and fresh setup. Collect source/OS/camera/operator identity, actual outcomes, failures/retries, summary segments and private evidence references without claiming you operated laptop B. Check app/file/folder/HTTPS errors, focus return/no replay, actual active-capture Camera handoff and paused restore. Verify the new visible failure notice only in affected cases. Coordinate his GF-P23 fresh-install/offline/thirty-minute Studio/shutdown checks for Deston's review; keep online HTTPS and unrun gesture cases separate. Manual checks need no profile. Gesture cases use the operator's own profile and qualifying current-session Practice gate. Keep private paths/data/full exports local. Fix only your owned modules and report shared-shell defects with a short reproduction. Submit one focused consolidated evidence PR from your branch, leaving it unmerged. Never push/merge into main, invent test outcomes or change original owners/weights/Done status because execution was delegated.
