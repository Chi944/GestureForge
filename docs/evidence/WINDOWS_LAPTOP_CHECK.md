# Windows laptop package verification

Run date: 23 September 2026. Documentation audited on 26 September 2026. This was a same-computer source-package test. Later [P02 feedback](P02_LAPTOP_TEST.md) reports assisted ZIP use and personal gesture control on another laptop. Its exact package/environment, guide-only installation, pause/restart and disconnected-network checks remain open in the [remaining P02 checks](P02_LAPTOP_TEST.md#short-remaining-laptop-check) and [laptop acceptance record](../WINDOWS_LAPTOP.md#6-physical-laptop-acceptance-record).

The source ZIP was extracted into `.cache/Windows Laptop Smoke 20260923/gestureforge`, which had no environment, model or participant dataset. From the original repository folder, `setup.cmd -PythonExe` was invoked using the extracted launcher's absolute path and a 64-bit Python 3.11.16 executable. Setup created a fresh environment under the extracted folder, installed the pinned requirements and application, downloaded the model, verified its checksum and exited 0. The complete local log is `.cache/Windows Laptop Smoke 20260923/setup.log`.

From the extracted folder, the following passed:

- `python -m pip check`: no broken requirements.
- `python scripts/check_environment.py --model`: expected SHA256, real MediaPipe video-mode inference on a blank image, zero detected hands, no camera opened.
- `python scripts/verify.py`: Ruff, mypy, 55 automated tests, GUI startup/shutdown and synthetic evaluation.
- `run.cmd --smoke-test`: launcher exit code 0.
- The imported application path was inside the extracted folder, not the development checkout.

The exact output of the five `verify.py` checks is in [laptop-archive-verification.json](laptop-archive-verification.json). It records Ruff, mypy, 55 tests, offscreen GUI startup/shutdown without a camera, and synthetic evaluation; it does not contain the separate pip, model, launcher or import-path commands. Those checks are described in this run note, with setup output in the local log above. Together they support fresh setup and native runtime loading on the development computer, not physical second-laptop compatibility or performance. See also [CLEAN_INSTALL.md](CLEAN_INSTALL.md) and [SETUP_CHECK.md](SETUP_CHECK.md) for the earlier same-computer checks.

The local archive test preceded the recovery-message change for an incompatible existing `.venv`. The [Windows CI workflow](../../.github/workflows/checks.yml) is configured to build and test an extracted source ZIP. Its normal fresh-install path does not exercise incompatible-environment recovery, and this note records no hosted run result for that later change. A configured workflow or badge is not physical-laptop acceptance evidence.

These are dated results for the tested snapshot, not a claim that every later archive was installed. Regenerate the source archive after final edits, verify its manifest/checksum and contents, and record acceptance against the actual package to be submitted. The [assignment checklist](../SUBMISSION_CHECKLIST_ASSIGNMENT.md) keeps that release check and human submission gates open.
