"""Run release checks and save their actual output as assessment evidence."""

from datetime import datetime, timezone
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent.parent


def main():
    commands = [
        ["-m", "ruff", "check", "gestureforge", "tests", "scripts"],
        ["-m", "mypy", "gestureforge", "scripts"],
        ["-m", "pytest", "-q"],
        ["-m", "gestureforge", "--smoke-test"],
        ["-m", "gestureforge.evaluate", "--config", "experiments/prototype.json",
         "--output", "experiments/synthetic-software-check.json"],
    ]
    results = []
    environment = {**os.environ, "QT_QPA_PLATFORM": "offscreen",
                   "MPLCONFIGDIR": str(ROOT / ".cache" / "matplotlib")}
    for command in commands:
        started = time.perf_counter()
        process = subprocess.run([sys.executable, *command], cwd=ROOT, env=environment,
                                 capture_output=True, text=True, timeout=180)
        results.append({"command": "python " + " ".join(command),
                        "returncode": process.returncode,
                        "seconds": round(time.perf_counter() - started, 3),
                        "stdout": process.stdout, "stderr": process.stderr})
        print(results[-1]["command"], "PASS" if process.returncode == 0 else "FAIL", flush=True)
    report = {"timestamp_utc": datetime.now(timezone.utc).isoformat(),
              "python": platform.python_version(), "platform": platform.platform(),
              "versions": {name: importlib.metadata.version(name) for name in
                           ["numpy", "scikit-learn", "mediapipe", "PySide6", "opencv-contrib-python"]},
              "checks": results,
              "limitations": ["Synthetic evaluation is software evidence only.",
                               "This script does not verify live participant performance or a second computer; see the assessment audit."]}
    output = ROOT / "docs" / "evidence" / "verification.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return int(any(result["returncode"] for result in results))


if __name__ == "__main__":
    raise SystemExit(main())
