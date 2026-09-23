@echo off
setlocal
cd /d "%~dp0"

powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\setup.ps1" %*
set "status=%ERRORLEVEL%"
if not "%status%"=="0" (
    echo.
    echo GestureForge setup failed with exit code %status%.
    echo Install 64-bit Python 3.11, then run setup.cmd again.
    if /I not "%CI%"=="true" pause
    exit /b %status%
)

echo.
echo GestureForge setup complete. Launch with run.cmd.
exit /b 0
