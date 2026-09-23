# Setup Check

Date: 2026-09-23

Result: PASS on the current Windows computer. This is not the required second-computer installation check.

## What changed

- `scripts/setup.ps1` accepts an optional `-PythonExe` argument.
- `setup.cmd` launches the PowerShell setup script with process-scoped execution bypass for easier Windows handoff.
- `run.cmd` launches the installed app from the repository's own `.venv`.
- The script still defaults to `py -3.11` when `-PythonExe` is not provided.
- The selected interpreter and resulting `.venv` interpreter are validated as 64-bit Python 3.11 before dependency installation.
- Pip cache is kept under the checkout at `.cache\pip`.
- Command failures are checked through a shared PowerShell helper with actionable error messages.

## Evidence

Fresh source snapshot:

`C:\Users\Desto\Desktop\Murdoch\ICT304\Assignment\code\.cache\setup-smoke-20260923-162702\source`

Command:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\setup.ps1 -PythonExe C:\Users\Desto\Desktop\Murdoch\ICT304\Assignment\code\.python\cpython-3.11.16-windows-x86_64-none\python.exe
```

Result file:

`C:\Users\Desto\Desktop\Murdoch\ICT304\Assignment\code\.cache\setup-smoke-20260923-162702\result.json`

Log file:

`C:\Users\Desto\Desktop\Murdoch\ICT304\Assignment\code\.cache\setup-smoke-20260923-162702\setup.log`

Actual result:

- Exit code: 0
- Virtual environment Python: 3.11.16
- Model asset present: true
- `hand_landmarker.task` SHA256 verified: `fbc2a30080c3c557093b5ddfc334698132eb341044ccee322ccf8bcf3607cde1`
- Environment check reported:
  - Python: 3.11.16
  - NumPy: 2.4.6
  - scikit-learn: 1.9.1
  - MediaPipe: 1.0.1
  - OpenCV contrib: 5.0.0.93
  - PySide6: 6.11.2

An earlier smoke run at `.cache\setup-smoke-20260923-162235` failed because PowerShell parsed pip's `-e` editable-install flag as an ambiguous function parameter. The current script fixes that by passing command arguments as explicit arrays.

## Limits

- This check did not open a webcam.
- This check did not collect participant data.
- This check did not prove the required independent second-computer installation.
