# GF-P19: laptop-A trusted app and restore observations, 19 October 2026

Operator: Javier. Device: Javier's Windows laptop A.
Runtime source: `d200947692253ede0c264755152e4419530147a3`.
Javier's supplied Git screenshot shows a fast-forward to that commit and clean
tracked status before restarting Studio through `run-studio.cmd`.
The matching 16 October package is a development handoff, not a release pass.
Its ZIP SHA256 is `4c4f4fbc0223229c50fb5a2e7abf9b1fb00057be1c95f9df443236aaaa42839a`.
Later documentation commits do not relabel this native observation's source.

These are guided human observations supported by screenshots, confirmations and
private summary exports. GPT inspected supplied evidence; it did not operate
the laptop or independently inspect native application windows/processes.
No new component-code repair or full GF-P19/GF-P23 acceptance is claimed.
Preserve PR18/GF-P05 and PR24/26/28/29 with their original evidence boundaries.

## Environment and sequence

Earlier laptop-A evidence identifies Windows 11 Home, version 10.0.26200,
build 26200 and Python 3.11.9. Those environment values were not freshly measured
during this check. Camera index 0 and the loaded right-hand personal profile
were visible; capture remained off for these manual checks. A full personal
Practice grant was not available. Manual Live requests do not require one.

Javier configured local shortcut ID `trusted-app-test`, display label
`Trusted app test`, target type App, selected Windows System32 `notepad.exe`,
and checked the installed-application trust confirmation. Screenshots show the
saved target and trust setting. The local absolute executable value is not
reproduced here; it remains on the operator's device.

| Case | Supplied observation | Boundary |
| --- | --- | --- |
| Selected trusted executable | One manual Test selected target request in Demo Studio; export records OPEN_SHORTCUT/trusted-app-test as launch_requested without failure. A subsequent screenshot shows Harbor reference text in the opened text window. | The image omits native window identity; Notepad may restore existing tabs. The record supports an attributed application-opening observation and request, not independent process verification or a completed human task. |
| Restore progress after real request | Saved deck progress after that request. Screenshot shows Progress restored, Preview, camera off and paused; Javier confirmed Notepad stayed closed. | Same summary revision and identical outcomes before/after: no added launch or other event. Saved card position was not separately compared, and there was no Harbor stage/bookmark in this Demo Studio check. |
| Save session without a runbook | In Demo Studio, a Save session attempt produced no usable session file; subsequent restore selection reported file not found. Screenshot retained the older Progress restored message. | Matching source inspection found a silent return when `runbook is None`. This is a shared-shell feedback issue for Deston, not evidence of data loss or an owned-component repair. |
| Save Harbor session | Loaded `assets/harbor_standard_workspace.json`; screenshot confirms Harbor Desk standard gesture onboarding, intro context, paused Preview. Explicit manual Live was reapplied and a fresh trusted-app request recorded. A text-window screenshot was supplied; later Setup shows Session saved with the selected filename. | No standard starter or gesture readiness follows from this workspace's name. This was a local target-library manual request in the intro context, not a completed Harbor task. |
| Restore Harbor session after real request | Restored the saved session after closing the text application. Screenshot shows Session restored, Preview, intro context, camera off/paused. Javier confirmed Notepad stayed closed. | Post-restore export has a new summary revision, zero events and zero launches. No stage advance, bookmark persistence, session restart or active-capture Camera check was performed here. |

## Private exports and overlap

All full exports remain private/local and must not be committed.

| Private export filename | Revision and contents | Counting rule |
| --- | --- | --- |
| `laptop-A-trusted-app-2026-10-19.json` | Demo Studio revision `a18e4a0b-cb68-4f6d-829e-0c65950d79e9`: six prior gesture simulations, one manual trusted-app launch request, zero failures. | The six simulations belong to earlier Preview diagnostics, not native launch success. |
| `laptop-A-after-app-restore-2026-10-19.json` | Same revision and exactly the same seven outcome objects after Restore progress. | Fully overlaps the preceding export; add no counts. |
| `laptop-A-before-session-restore-2026-10-19.json` | Harbor revision `2011d990-a38a-4ac6-a433-9a0c848156d0`: one manual trusted-app launch request in intro, no simulations or failures. | Disjoint from the Demo Studio request. |
| `laptop-A-after-session-restore-2026-10-19.json` | Harbor revision `a9e529dd-6f3f-4c62-adbf-7c2a4e31facc`: empty outcomes, all counts zero. | New post-restore segment; no request replay recorded. |

The deduplicated record contains six historical simulations and two distinct
manual launch requests across the Demo Studio and Harbor segments, with zero
recorded failures and zero task acknowledgements. These are not eight successful
Windows tasks. Summary `failed: 0` does not erase the separate silent-save UI
observation, which is outside dispatcher launch outcomes.

The progress filename and saved Harbor session filename are state files, not
summary exports. They were created through separate Save progress / Save session
controls. The save/restore confirmations and no-reopen observations were supplied;
the state JSON contents were not independently provided for inspection.

## Shared-shell feedback reproduction for Deston

1. On the identified runtime, open Demo Studio without loading a runbook.
2. Click Setup's Save session and choose a new JSON destination.
3. Observe that no session-save confirmation is provided and no usable file is
   found for Restore session; the old file-status message can remain visible.
4. Load a workspace containing stages, then Save session again: the supplied
   Harbor follow-up displays Session saved and restores successfully.

In the matched source, `Window.save_studio_session` in `gestureforge/app.py`
returns False when `self.runbook is None` before setting an explanatory message.
The dialog caller does not turn that return into visible guidance. This explains
the supplied sequence; no independent native reproduction was performed by GPT.
Ask the shell owner to show a no-runbook reason or disable the operation with
guidance, preserving all existing save/evidence checks. No shared-shell edit was
made from Javier's branch.

The supplied restore screenshots also retain an earlier top notice about a LIVE
manual request while the footer correctly shows Preview. Treat that notice as
historical launch feedback, not the current mode or a new launch. Its clarity is
for Deston's review; the exports record no replay.

## Verification and remaining cases

Checks performed for this report: parsed all four exports, compared revision IDs,
verified unique event IDs and aggregate counts, compared the two progress
snapshots object-for-object, and checked the empty post-session-restore segment.
Compared the configured target and mode/restore screenshots with those records.
Inspected the save-session guard in the matching source archive. No production
code changed and no new Ruff/mypy/pytest, camera timing or software-suite run is
claimed for this documentation-only delivery.

| Remaining work | Status / responsible operator |
| --- | --- |
| Missing association | NOT RUN in this check; no isolated association-free setup supplied. Do not change existing associations merely to obtain a failure. |
| Further native failure/retry matrix | Not newly run here; preserve accepted earlier missing-target evidence and execute only outstanding/affected cases under the shared procedure. |
| Active-capture Camera handoff | NOT RUN: Javier's full personal Practice remains failed. Earlier off-capture Camera evidence is not substituted. |
| Laptop B | Awaiting Hau Jie's attributed observations on the matching identified package; Javier coordinates, Deston accepts. |
| Fresh installation, offline core, thirty-minute Studio workflow and shutdown | No new GF-P23 acceptance supplied. The short capture diagnostic and software verification cannot replace them. |
| P03 recognition diagnosis | Private trace/settings handoff prepared separately; index-finger checks produced unintended simulated NEXT actions. No tuning, full recollection or combined-attempt pass is claimed. |
| Guide/demo | GF-P25 guide draft merged through PR33 with Deston's neutral-window clarification. Storyboard remains a private draft; final video is not recorded. |

AI assistance guided the steps and inspected the supplied material. Javier
operated Windows and supplied the outcomes. Deston retains defect assignment,
integration review and final task acceptance.
