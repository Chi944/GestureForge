# GF-P19/GF-P22: laptop A recovery observations — 25 October 2026

The original 25 October ZIP and its exports/logs were received and independently
checked in Deston's checkout on 25 October 2026. Receipt integrity, summary
counters and saved-state validation pass. Physical Windows results remain
Javier's guided observations; no screenshots are included in this packet.
This receipt review does not advance whole-task acceptance.

Operator: Javier. Review owner: Deston; independent artifact receipt review
complete. Guided human observations and artifact checks do not constitute
independent native replay or whole-task acceptance.

## Build and private receipt

The supplied post-sync screenshot identifies branch `codex/javier-shortcuts`,
clean tracked status and HEAD `d9c68c651132d1405881966c2fd5445d820201c9`
(reviewed main `19c95233b25c227094c1fbe6ce42202bbb47e2d8` plus documentation).
Windows 11 Home 10.0.26200, build 26200; Python 3.11.9; camera index 0.
The transcript retains sync commands but omits some native command output;
build/Python identification additionally relies on the supplied 073502 screenshot.
No subsequent source edit was reported; this is not an independent runtime attestation.

Private original: `PRIVATE_JAVIER_CHECKS_20261025-203326.zip`, 6,933 bytes,
9 members, SHA256
`2829b372db25d9bce8782833bcca84e521977e0e5346a3031478beb01176123d`.
CRC, size and SHA256 were reproduced on receipt. Actual ZIP member names use
forward slashes; extraction also normalizes backslashes. No absolute or parent
traversal paths, duplicate normalized names or links were found. Original bytes
are preserved in private storage.
The archive root is `javier-check-20261025-153143-857`.
Screenshots and operator confirmations were reported separately in Javier's guided session; screenshots are absent from the received ZIP.

| Case / expected result | Actual observation | Boundary |
| --- | --- | --- |
| Save session without a workspace must explain refusal and leave no file | Visible “Session not saved: load a workspace with a runbook first”; Test-Path returned False | PASS bounded; 074044/074254 screenshots and transcript. |
| Clear two unavailable slots independently without deleting library | Disposable TXT targets bound NEXT/PREVIOUS, copies renamed aside; NEXT cleared while PREVIOUS B still unavailable, then PREVIOUS cleared | PASS bounded; 074940, 075456, 080030 screenshots and rename commands. The intermediate image does not separately prove A was unavailable before clearing; the transcript records both renames. |
| Preserve entries and restore prior setup | Restored TXT filenames; both test entries Configured; NEXT Validation recovery test, PREVIOUS Trusted app test, BOOKMARK Unbound | PASS bounded; 080256 screenshot; original choices at 074508. |
| Save/restore top feedback must replace historical LIVE notice | One manual Live Calculator request established the notice; top message changed to Session saved, then Session restored | PASS bounded; 084604, 084830, 085426 screenshots. |
| Restore must retain budget stage paused without replay | Stage 2 restored in Preview, Camera off; Javier confirmed Calculator stayed closed; new summary revision empty | PASS bounded; independent JSON inspection supports no recorded dispatch, operator confirms OS observation. |
| Same-camera Use camera and pause must stop active Preview | Existing own P03 profile loaded; Quick Actions Preview context; Javier confirmed video appeared, stopped immediately on the control at index 0 before switching windows | PASS by guided operator observation; 113655 precondition/115036 post-state screenshots. Post-state footer mentions later focus loss; causal timing comes from Javier, not the image alone. |
| Explicit Start reacquires capture | Javier confirmed live video returned after Start | PASS by operator report; no independent frame recording. |
| Windows Camera can acquire after Studio closes | After instructed pause/normal closure, Javier reported live video in Windows Camera | PASS by operator report; does not prove active-capture external launch or capture shutdown order. |
| Process exit status retained | WaitForExit returned; process log has PID 36832 and a blank ExitCode | INCOMPLETE numeric exit-status evidence; do not infer zero or a crash. |

Calculator opening was reported by Javier; no calculation result or task
acknowledgement was collected. Preview Quick Actions never establishes a native
launch. The existing profile remains readiness-unverified; no new Practice,
recognition repair, grant, Live gesture or active-capture Camera handoff is claimed.

## Disjoint restore segments

Javier's earlier review reports byte identity with separately uploaded originals.
Receipt review reproduces the published hashes below; separate standalone
originals were not available for an independent byte comparison here.

| Export | Revision | Contents | SHA256 |
| --- | --- | --- | --- |
| harbor-before-restore-2026-10-25.json | revision-5cd443ea-9477-4593-ba2a-0fc118ded1c2 | 1 applied manual ADVANCE_STAGE from intro, 1 manual Calculator launch_requested in budget; no failures, simulations or acknowledged stages | `8f4a87ddf0a7fa412f66a346c1a176780cb15b7404d6471dab132b00be0e9157` |
| harbor-after-restore-2026-10-25.json | revision-96fd9b79-9462-47a7-9e16-61be17a934cf | All counts zero; empty outcomes/trials/completed_stages; no session ID to invent | `df618eb92ee2c197c25bd8e590e426d5c3049116c99be69c642a18e5b882b7f8` |

This new manual check used workspace ID `harbor-onboarding`; the historical
22 October manual pair used `harbor-onboarding-standard`. Neither is measured
workflow-study evidence merely because of a workspace identifier.
Saved session JSON independently contains stage_id/card_id `budget`,
finished false and no bookmarks. It does not contain or prove a readiness grant.
Post-restore Preview/pause is established by the screenshot, not an invented
resume field in that JSON. Before contains two outcomes; after contributes none.

## Logs and important limits

The transcript records two Start-Process invocations using the same stdout,
stderr and process filenames, including a repeated Out-File. Only the final
process identity/log set survives; do not present this as a complete per-launch
record or assign the earlier no-workspace attempt to PID 36832.

Final process record: PID 36832, start UTC 2026-10-25T07:44:25.5952223Z.
The EndedUTC line is the logging/check time 2026-10-25T12:30:45.7526508Z,
not a measured exact OS termination timestamp. ExitCode is blank.
The elapsed wall interval includes long gaps between guided actions and is
not a measured stability run. No observation-rate, responsiveness or memory
series was collected.

stdout is empty. Retained stderr contains Qt font and MediaPipe/TFLite warnings;
no traceback or 0x8001010d occurs in that retained file. This does not recover
overwritten earlier stderr or establish an error-free full session.
No Windows fault log or complete automatic diagnostic/gesture trace was supplied.
Optional trace checkboxes were off. Full logs remain private.

For future launches, use a new output directory per invocation, never reuse
these files, and record an unavailable exit code explicitly. Do not repeat
successful UI checks solely to replace missing logging metadata.

## Validation and remaining work

Independent receipt assertions pass for archive CRC/safe paths, nine-member
inventory, SHA256, summary counters recomputed from events, unique event IDs,
distinct revision identities and saved budget stage/card. Current workspace,
viewer and Runbook validators accept the saved session; a stub routing callback
receives budget with resume=False, leaving the restored runbook paused. No OS
action was executed. This verifies artifact compatibility, not Javier's physical
UI state or camera behavior. Private intake, audit and review files are retained
under `.local/javier-checks-20261025/` and excluded from Git.

Receipt/integrity and JSON review substeps are closed. Standalone/packet byte
equality remains attributed to the earlier review. No production code change,
Ruff/mypy/pytest, full build or native hardware run is claimed by this update.

A association/input cases not exercised here remain unrun. Laptop B's remaining
affected fixes, guide-only installation, offline checks, continuous measured
30-minute full-Studio workflow and post-close camera/exit evidence still need
Hau Jie's new receipts. Preserve his already-reviewed packet unchanged.
Genuine readiness, eligible active-capture handoff, actual personal scenario,
M/P comparison, holds/negative/latency and final verified video remain outstanding.
No task weights, acceptance or prompt/decision logs were changed.

AI assistance guided the session, inspected screenshots/exports/logs and drafted
this sanitized note. Javier performed and reported the physical Windows actions.
See the [two-device matrix](../project/JAVIER_WINDOWS_REMAINING_CASES_2026_10_25.md).
