param(
    [string]$PythonExe = ''
)

$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
$env:PIP_CACHE_DIR = Join-Path $PWD '.cache\pip'

function Invoke-Checked {
    param(
        [Parameter(Mandatory = $true)]
        [string]$FailureMessage,
        [Parameter(Mandatory = $true)]
        [string]$FilePath,
        [string[]]$Arguments = @()
    )

    & $FilePath @Arguments
    if ($LASTEXITCODE -ne 0) { throw $FailureMessage }
}

function Assert-Python311 {
    param(
        [Parameter(Mandatory = $true)]
        [string]$PythonPath
    )

    if (-not (Get-Command $PythonPath -ErrorAction SilentlyContinue)) {
        throw "Python executable not found: $PythonPath"
    }
    & $PythonPath -c "import sys; raise SystemExit(0 if sys.version_info[:2] == (3, 11) else 1)"
    if ($LASTEXITCODE -ne 0) {
        throw "GestureForge requires Python 3.11. The selected interpreter is not Python 3.11: $PythonPath"
    }
    & $PythonPath -c "import sys; raise SystemExit(0 if sys.maxsize > 2**32 else 1)"
    if ($LASTEXITCODE -ne 0) {
        throw "GestureForge requires 64-bit Python 3.11 on Windows. The selected interpreter is 32-bit: $PythonPath"
    }
}

if (-not (Test-Path '.venv\Scripts\python.exe')) {
    if ($PythonExe) {
        Assert-Python311 $PythonExe
        Invoke-Checked 'Could not create the virtual environment with the selected Python 3.11 interpreter.' $PythonExe @('-m', 'venv', '.venv')
    } else {
        Invoke-Checked 'Install 64-bit Python 3.11 with the Python launcher first, or rerun setup.cmd with -PythonExe C:\path\to\python.exe.' py @('-3.11', '-m', 'venv', '.venv')
    }
}

$VenvPython = '.\.venv\Scripts\python.exe'
try {
    Assert-Python311 $VenvPython
} catch {
    throw "Existing .venv is incompatible with GestureForge. Rename .venv to .venv-old, then rerun setup.cmd or setup.cmd -PythonExe C:\path\to\python.exe. Details: $($_.Exception.Message)"
}
Invoke-Checked 'Could not initialise pip.' $VenvPython @('-m', 'ensurepip', '--upgrade')
Invoke-Checked 'Dependency installation failed.' $VenvPython @('-m', 'pip', 'install', '-r', 'requirements.lock')
Invoke-Checked 'Application installation failed.' $VenvPython @('-m', 'pip', 'install', '--no-deps', '-e', '.')
Invoke-Checked 'Model asset verification failed.' $VenvPython @('scripts\download_model.py')
Invoke-Checked 'Environment verification failed.' $VenvPython @('scripts\check_environment.py')
Write-Output 'Setup complete. Launch with run.cmd, or use: .\.venv\Scripts\python.exe -m gestureforge'
