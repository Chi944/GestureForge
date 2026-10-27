# Laptop B: remaining release checks — 27 October 2026

Status: preparation only. No new physical case is passed by this checklist.
Deston owns acceptance; Javier reconciles the device matrix. Recognition work
is complete and is not reopened here.

## Pinned source

Reviewed main fetched on 27 October remains
`708e77eadf64d43dfbb477d2ab8955c815f68b1a`. Hau Jie's branch was clean and
fast-forwarded to it, preserving ignored private files. A clean source package
was built before this checklist was added: 222 files, ZIP SHA256
`988e7e38d31e7e6fb705c02a1072f0fa7355431aaf599f097c076286fcb62f3b`.
Use its matching source receipt. This documentation PR is not a different
tested runtime. Packaging and software checks do not establish device acceptance.

## Preparation verification and limits

Archive CRC, safe/unique paths and all 222 checkout member bytes pass. Git clean
filters reconcile Windows line endings with the pinned commit. The focused
monitor, process-launcher and package suite passes **90 tests** with normal local
file access and a fresh absolute temporary folder. Earlier restricted attempts
failed temporary-directory/hard-link access and remain separate private records.

Repository verification is **not all green** on this laptop: Ruff, both smoke
checks and synthetic evaluation pass; mypy reports four existing errors in
`tests/test_app_personal_live.py` (untyped collection/optional grant) and
`tests/test_run_p20.py` (optional decoded image). The full-suite attempt with a
stop-on-first-failure policy records 143 passes then fails
`test_active_practice_actions_fit_half_width_workflow` in `tests/test_app_layout.py`.
Remaining tests were not run in that attempt. Report the layout/type findings
to Deston for ownership and review; no shell change or physical defect is
inferred from the offscreen layout assertion. These baseline failures must not
be hidden by the successful focused tests or package build.

## Before disconnecting networking

1. Keep the ZIP and matching JSON receipt together. Preserve earlier packages.
   Read [Windows setup](../WINDOWS_LAPTOP.md), using its **Studio project
   handoff** and section 2; the assignment prototype and collection instructions
   are historical and do not assign new enrolment.
2. Hau Jie extracts to a separate writable, preferably ASCII-only folder and
   follows the written guide himself. Create that installation's own environment;
   do not copy an old `.venv`, profiles or shortcut paths. Keep networking on
   for dependency/model downloads. Record Python/Windows details, actual folder,
   setup outcome and every help request. Package preparation is agent-assisted;
   only the subsequent installation steps can be observed as guide-only.
3. Confirm `run-studio.cmd` opens Studio and the setup model/dependency checks
   succeed. Rebind only this machine's permitted local app/file/folder targets.
   Read and retain this checklist and the user guide locally before disconnecting.
   If setup fails, stop and retain the error; assistance changes the installation
   disposition to assisted, with the guide problem recorded.

## Offline core: operator checklist

Disconnect all active networking yourself after setup. Record the actual
disconnect/reconnect times, build and observations. Start Studio while offline.

| Check | Expected observation | New result |
| --- | --- | --- |
| Guest/manual navigation | Cards advance/restart; bookmark can be set and revisited | Pending |
| Permitted local app, reference file and folder | Explicit manual LIVE requests open the intended local targets | Pending |
| Save/restore | Keep a before export, save, restore, then keep a separate after export; restore stays paused with no automatic launch replay | Pending |
| Offline limits | HTTPS and other online features are excluded; note any unexpected network dependency | Pending |

Manual LIVE does not require a gesture profile. Select mode explicitly and
check the target before requesting an action; Preview only simulates. These
checks establish the fresh installation's offline behaviour, not new credit
for earlier unchanged online passes. Do not conflate a launch request with
an observed application opening.

## Remaining native and camera cases

Use the [current device matrix](JAVIER_WINDOWS_REMAINING_CASES_2026_10_25.md#reconciled-two-device-case-matrix)
for exact expected behaviour; preserve unchanged bounded passes.

- B1: independently clear two unavailable Quick Actions slots, retain library
  entries/restore choices, and check the affected no-runbook save refusal and
  visible save/restore feedback. Use disposable local fixtures.
- Fill only absent target-validation cells. Distinguish configuration refusal
  from OS launch refusal. Never execute an interpreter/script or alter Windows
  associations to manufacture a failure. No safe mapped-drive/association-free
  fixture means NOT RUN with reason.
- B2: with the existing own profile in Preview, apply the current camera index
  with **Use camera and pause**; observe stop before switching windows, then
  explicitly restart. Separately check focus-loss pause and explicit resume.
- Active-camera external handoff remains separate and conditional on the
  actual current runtime eligibility. Do not import old grants, rerun Practice
  on a failing profile or bypass controls to fill this cell.

## Endurance: prepare, do not start automatically

Previous attempts remain distinct: approximately seven seconds of instrumented
Studio capture, a separate 300.016-second pipeline diagnostic, separate post-close
probe, and an unmeasured operator-reported 30-minute run. None supplies a new
continuous measured Studio pass. The reviewed 26 October run on Deston's device
also retains its five-second gap.

The pinned source includes the persistent gap warning and the parent launcher
that saves actual child-process exit separately from Qt exit. Run affected
monitor/launcher tests before scheduling a justified new physical attempt.
Use [the measurement guide](../USER_GUIDE.md#measure-the-full-studio-stability-run)
with a new output directory, actual camera and independent operator clock.
Do not schedule the 30-minute run until installation and camera setup are ready.

Keep capture uninterrupted and Studio visible; exercise on-screen controls.
Native launches/handoffs that pause capture are separate cases. A visible gap
warning means close normally and retain the failed attempt; waiting longer or
combining restarts cannot repair it. Remaining zero alone is not a pass.
After normal close, retain that same run's measurement, process exit and console
logs, then separately observe another camera app reopening the device and close
it. A software shutdown flag does not prove physical reacquisition.

## Only new evidence to return

Record case ID, expected/actual outcome, operator/date, source/package hash,
assistance, exact new receipt/export filenames, faults/retries and NOT RUN reasons.
Keep before/after exports and distinct attempts separate. New setup/offline/native
observations and the same-run `measurement.json`, `process.json`, `stdout.log`,
`stderr.log` plus camera-reopen observation go privately to Deston. Full logs,
local targets and personal files stay out of GitHub. Give Javier only a sanitized
case summary. The already received 26 October ZIP must not be resent.
