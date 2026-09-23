# Windows laptop package verification

Date: 23 September 2026. The second Intel/AMD Windows laptop is not available yet. Its webcam and disconnected-network acceptance checks are pending in `../WINDOWS_LAPTOP.md`.

The source ZIP was extracted into `.cache/Windows Laptop Smoke 20260923/gestureforge`, which had no environment, model or participant dataset. From the original repository folder, `setup.cmd -PythonExe` was invoked using the extracted launcher's absolute path and a 64-bit Python 3.11.16 executable. Setup created a fresh environment under the extracted folder, installed the pinned requirements and application, downloaded the model, verified its checksum and exited 0. The complete local log is `.cache/Windows Laptop Smoke 20260923/setup.log`.

From the extracted folder, the following passed:

- `python -m pip check`: no broken requirements.
- `python scripts/check_environment.py --model`: expected SHA256, real MediaPipe video-mode inference on a blank image, zero detected hands, no camera opened.
- `python scripts/verify.py`: Ruff, mypy, 55 automated tests, GUI startup/shutdown and synthetic evaluation.
- `run.cmd --smoke-test`: launcher exit code 0.
- The imported application path was inside the extracted folder, not the development checkout.

The exact verification output is in `laptop-archive-verification.json`. This verifies fresh setup, native runtime loading and source portability on this computer. It does not establish the absent laptop's hardware compatibility or physical performance.

The initial archive test preceded the final wording for recovery from an incompatible existing `.venv`. That error-path-only change is included in the hosted Windows archive workflow. No app, dependency or success-path change was made after the local archive test.
