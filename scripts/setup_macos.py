"""Set up native Apple Silicon Python 3.11 without modifying system packages."""

import os
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parent.parent


def validate_runtime() -> None:
    if platform.system() != "Darwin":
        raise SystemExit("This setup is for macOS. On Windows, use setup.cmd.")
    if platform.machine() != "arm64":
        raise SystemExit("Use native Apple Silicon Python, not Intel Python or Rosetta.")
    try:
        major = int(platform.mac_ver()[0].split(".")[0])
    except (IndexError, ValueError):
        raise SystemExit("Could not read the macOS version. Confirm macOS 13+ with sw_vers.") from None
    if major < 13:
        raise SystemExit("The pinned dependencies require macOS 13 Ventura or newer.")
    if sys.version_info[:2] != (3, 11):
        raise SystemExit("Run this script with Python 3.11: python3.11 scripts/setup_macos.py")


def main() -> None:
    validate_runtime()
    environment = {**os.environ, "PIP_CACHE_DIR": str(ROOT / ".cache" / "pip")}
    environment.pop("QT_QPA_PLATFORM", None)

    def run(*args: str) -> None:
        subprocess.run(args, cwd=ROOT, env=environment, check=True)

    venv = ROOT / ".venv"
    python = venv / "bin" / "python"
    if venv.exists() and not python.is_file():
        raise SystemExit("Existing .venv is incompatible. Rename it, then rerun setup.")
    if not venv.exists():
        run(sys.executable, "-m", "venv", str(venv))
    # Check an existing environment before installing anything into it.
    run(str(python), "-c", "from scripts.setup_macos import validate_runtime; validate_runtime()")
    run(str(python), "-m", "ensurepip", "--upgrade")
    run(str(python), "-m", "pip", "install", "--only-binary=:all:", "-r", "requirements.lock")
    run(str(python), "-m", "pip", "install", "--no-deps", "-e", ".")
    run(str(python), "-m", "pip", "check")
    # python.org installations may not yet have run Install Certificates.command.
    # Use the already-pinned CA bundle; never disable HTTPS verification.
    environment["SSL_CERT_FILE"] = subprocess.check_output(
        [str(python), "-c", "import certifi; print(certifi.where())"],
        cwd=ROOT, text=True,
    ).strip()
    run(str(python), "scripts/download_model.py")
    run(str(python), "scripts/check_environment.py", "--model")
    # Exercise the native Qt window too; neither smoke mode starts a camera.
    run(str(python), "-m", "gestureforge", "--smoke-test")
    run(str(python), "-m", "gestureforge", "--studio", "--smoke-test")
    print("Setup complete. Launch from Terminal with: bash run.sh")


if __name__ == "__main__":
    try:
        main()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise SystemExit(f"Setup failed: {exc}. Fix the reported error, then rerun setup.") from exc
