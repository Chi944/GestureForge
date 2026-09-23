@echo off
setlocal
cd /d "%~dp0"

if not exist "%~dp0.venv\Scripts\python.exe" (
    echo GestureForge is not set up yet.
    echo Run setup.cmd first, then run this file again.
    if /I not "%CI%"=="true" pause
    exit /b 1
)

"%~dp0.venv\Scripts\python.exe" -m gestureforge %*
set "status=%ERRORLEVEL%"
if not "%status%"=="0" (
    echo.
    echo GestureForge exited with code %status%.
    if /I not "%CI%"=="true" pause
    exit /b %status%
)

exit /b 0
