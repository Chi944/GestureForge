# Laptop B native recovery observations — 28 October 2026

These are new assisted Windows UI observations on Hau Jie's laptop B, not
whole-task acceptance. Runtime source was
`708e77eadf64d43dfbb477d2ab8955c815f68b1a`, source ZIP SHA256
`988e7e38d31e7e6fb705c02a1072f0fa7355431aaf599f097c076286fcb62f3b`,
with the separately installed Python 3.11.15 environment. The repository was
subsequently synchronized to reviewed main `96d367c`; that does not change the
identity of the tested installation.

## Observed cases

| Case | Expected | Actual bounded result |
| --- | --- | --- |
| Save without a runbook | Refuse with a specific explanation | “Session not saved: load a workspace with a runbook first.” No save dialog appeared. |
| Viewer controls | Navigate, bookmark and return to a saved card | Harbor card 2 was bookmarked; Next displayed card 3; selecting the bookmark returned to card 2. |
| Real manual launch before restore | Explicit request opens the local target | In manual LIVE mode, the explicit Calculator test produced a new native Calculator window. Request feedback did not claim task completion. Calculator was closed normally before restore. |
| Save feedback | Show the actual file operation | Both notices identified the saved session file. |
| Restore feedback and state | Return paused in Preview, preserve navigation, do not replay launches | Both notices identified the restored session. Preview and paused state were visible; card 2 and its bookmark were retained. No Calculator window reopened. |
| Separate exports | Preserve before and after summaries independently | Before: one launch request and three applied viewer events. After restore: a different revision with zero outcomes/counters. No completion acknowledgement was inferred. |
| Two unavailable slots | Clear each independently without deleting targets | With both disposable TXT files absent, slot 1 cleared while slot 2 remained bound and unavailable. Slot 2 then cleared separately. All four library entries remained. |
| Restore fixtures and bindings | Preserve file contents and previous slot settings | Both files were restored with matching SHA256 values. The reference target could be rebound; both files showed Configured. Final slots matched their original three Unbound values. |
| Normal shutdown | Retain the actual process result | Studio closed normally; its launcher recorded numeric child exit 0. Camera remained off throughout these recovery operations. |

## Evidence and limits

Original before/after summary exports, saved session, native observations,
registry checkpoints, fixture hashes, final raw session log, source receipt and
same-process launch/exit records are retained in a new indexed private packet.
No profiles, participant samples, environments or media are published here.
The new private archive is `PRIVATE_LAPTOP_B_NATIVE_RECOVERY_20261028.zip`
(34 indexed payloads, 26,583 bytes), SHA256
`d2d7e71b6b3ceda35d7026e78a13fbb3977eb5393f4d8d0b266d9a4d86926731`.
CRC, unique safe member names and all indexed payload hashes were checked.

The process started with both physical network adapters disconnected. An earlier
attempt with Wi-Fi up was refused by the receipt launcher and retained. However,
the assisting agent's recovery operations above occurred after Wi-Fi was back
up, and the final network snapshot also showed Wi-Fi up. This is a mixed-network
process, **not a verified complete offline-core pass**. Earlier operator reports
are preserved separately and are not substituted for these online observations.

Installation was assisted, not guide-only. Same-camera pause/reacquisition and
focus/resume were not exercised in that recovery session; the separate short
camera session below supplies new bounded observations.
Active-capture external Camera handoff remains separate. No existing mapped
network drive was available; no isolated broken-association fixture was supplied.
Those fixture-dependent cases remain NOT RUN, without changing the OS.

No production defect was demonstrated and no production code changed. Evidence
validation reconciled the original JSON exports, restored bindings/file hashes,
numeric process result and private archive CRC/index hashes. This documentation
does not claim a new software test-suite run, gesture readiness or release approval.
Reuse the separately accepted passive-duration receipts; no further thirty-minute
run is assigned by this result.

## Separate short camera recovery session

The same identified `708e77e` installation was launched in a new process with
new receipts. Saved P02 Original was loaded unchanged (profile byte hash checked),
with camera 0, Right hand and Preview. No collection, Practice, threshold change,
manual approval or LIVE dispatch was performed.

- Start produced the preview image accessibility control and updated prediction
  text, with Start disabled.
- **Use camera and pause**, still selecting index 0, produced “Camera off / Start
  explicitly to reconnect” and “Paused • camera released”, with Start enabled.
- Explicit Start restored the preview/prediction state.
- Activating the existing Notepad window produced pause events. Returning to
  Studio without a Start command remained paused, with the camera-off/released
  messages. Explicit Ctrl+Return then restored the preview/prediction state.
- Escape paused capture again. Normal Alt+F4 removed the Studio window, and the
  same launch's original process receipt recorded child exit **0**.

All three original start events identify camera 0, Preview and the same model
version/settings. Accessibility snapshots sometimes lagged; refreshed return
state and the original event log were reconciled. No active-camera screenshot
was taken, and frame rate/count, preview pixel quality and exact focus-to-pause
latency were not measured. No new physical gesture pass is inferred.

Two preceding startup failures are retained separately: a private parent
launcher's Unicode console-output error (child exit unknown), and a restricted
startup with no visible window, whose identified child was explicitly stopped
before any camera/UI case (exit 4294967295). Neither is normal shutdown or a pass.
The private launcher was corrected; production source was not changed.

The new private archive is `PRIVATE_LAPTOP_B_CAMERA_RECOVERY_20261028.zip`
(20 indexed payloads, 13,642 bytes), SHA256
`15b41af08b37755f48dd25353855c2fe715d145b87e3341893fad7b4beb1d1cb`.
CRC and all payload hashes pass. It contains only this short case's originals,
observations and separate failed startups, not the received passive-stability
packet. Guide-only setup, verified complete offline core and any separately
assigned eligible external Camera handoff remain outside these observations.

## Later operator-run offline attempt: partial, not accepted as fully offline

A new human-operated run used the same identified `708e77e` installation.
The launcher recorded disconnected physical adapters at startup and actual
child exit 0 after normal closure. Its 183 sampled link observations contain
four disconnected samples followed by 179 Wi-Fi-Up samples. Physical link Up
does not prove Internet traffic, but these records do not establish the assigned
fully disconnected workflow. Hau Jie subsequently stated that the computer's
Wi-Fi stayed disconnected throughout. Preserve both accounts for owner review;
do not infer operator error or change the originals to resolve the discrepancy.

The user reported successful bookmark return, actual Calculator/reference/folder
opening, and paused Preview restoration without automatic reopening. Original
pre-restore summary state reconciles three manual launch requests, nine applied
viewer outcomes and two unchanged outcomes. The original after export has a
different revision and zero outcomes/counters. The actual saved workspace is
Demo Studio, not the planned Harbor workspace; it saves card 10 and no bookmarks.
The existing pre-restore summary and its identical archive are retained as found;
an exact separate export named `sessionsummary` was not located in the reviewed
folders. These limits are preserved rather than upgrading the run to a full pass.

Only this attempt's originals and observations were indexed in
`PRIVATE_LAPTOP_B_OFFLINE_REVIEW_20261028.zip` (30 payloads), SHA256
`56bfacaaa19061ec6613d275210bf4bb206d7a9fe8e7227ffde43cdb9f98ec18`.
The later operator clarification is a separate private addendum. No automatic
rerun or whole offline-core acceptance is assigned by this review.

## Fresh installation: assisted completion, not guide-only

The user extracted the identified source package and created a new Python
3.11.15 environment before requesting agent help. Dependencies/application and
the hand model were not yet installed. The agent preserved that environment,
verified all 222 extracted source files against the ZIP, and completed the
original setup script with the existing Python base interpreter. No old
environment, profile, participant samples or target registry was copied.

Setup, dependency consistency, Studio smoke and viewer smoke each returned 0.
Setup also passed the blank-image native model check without a webcam. The new
native Studio showed Guest/manual, Preview and Camera off. Normal Alt+F4 then
produced actual child exit 0 in that same launch's original process receipt.
This is **AI-assisted installation**, regardless of the proposed folder name;
the independent guide-only criterion remains unmet. No offline, physical camera,
Practice or endurance check was performed on this new installation.

The final private packet is
`PRIVATE_LAPTOP_B_ASSISTED_INSTALL_FINAL_20261028.zip` (22 indexed payloads), SHA256
`bfa9d8683ef7a42b5cd48d4ff3de1ea80d4d074211a38239dfe707db6cb7c1f9`.
It resolves the earlier installation packet's pending visible-process exit;
the earlier immutable snapshot remains preserved. CRC and every indexed payload
hash pass. Only sanitized findings are committed; original logs, saved states,
network observations and local paths remain private. These additions change no
qualification, acceptance points or production source.
