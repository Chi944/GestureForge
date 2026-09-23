$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
if (-not (Test-Path '.venv\Scripts\python.exe')) {
    py -3.11 -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw 'Install Python 3.11 with the Python launcher first.' }
}
& .\.venv\Scripts\python.exe -m ensurepip --upgrade
if ($LASTEXITCODE -ne 0) { throw 'Could not initialise pip.' }
& .\.venv\Scripts\python.exe -m pip install -r requirements.lock
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
& .\.venv\Scripts\python.exe -m pip install --no-deps -e .
if ($LASTEXITCODE -ne 0) { throw 'Application installation failed.' }
& .\.venv\Scripts\python.exe scripts\download_model.py
if ($LASTEXITCODE -ne 0) { throw 'Model asset verification failed.' }
& .\.venv\Scripts\python.exe scripts\check_environment.py
if ($LASTEXITCODE -ne 0) { throw 'Environment verification failed.' }
Write-Output 'Setup complete. Launch: .\.venv\Scripts\python.exe -m gestureforge'
