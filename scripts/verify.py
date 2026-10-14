"""Run release checks and save their actual output as assessment evidence."""

import argparse
from datetime import datetime, timezone
import importlib.metadata
import json
import math
import os
from pathlib import Path
import platform
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent.parent


def _positive_finite_seconds(value: str) -> float:
    try:
        seconds = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("timeout must be a number of seconds") from exc
    if not math.isfinite(seconds) or seconds <= 0:
        raise argparse.ArgumentTypeError("timeout must be a positive finite number of seconds")
    return seconds


def _text(value) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode(errors="replace")
    return str(value)


def _run_check(command: list[str], environment: dict[str, str], timeout: float) -> dict[str, object]:
    started = time.perf_counter()
    command_text = "python " + " ".join(command)
    try:
        process = subprocess.run([sys.executable, *command], cwd=ROOT, env=environment,
                                 capture_output=True, text=True, timeout=timeout)
        return {"command": command_text,
                "returncode": process.returncode,
                "seconds": round(time.perf_counter() - started, 3),
                "stdout": process.stdout, "stderr": process.stderr}
    except subprocess.TimeoutExpired as exc:
        stdout = getattr(exc, "stdout", None)
        if stdout is None:
            stdout = getattr(exc, "output", None)
        return {"command": command_text,
                "returncode": 124,
                "seconds": round(time.perf_counter() - started, 3),
                "stdout": _text(stdout), "stderr": _text(exc.stderr),
                "timed_out": True}


def main(argv: list[str] | None = None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        help="New JSON file; defaults to a timestamped report in experiments/local.")
    parser.add_argument("--synthetic-output", type=Path,
                        help="Optional new JSON file; otherwise synthetic results stay in the verification report.")
    parser.add_argument("--timeout", type=_positive_finite_seconds, default=600.0,
                        help="Per-command timeout in seconds.")
    args = parser.parse_args(argv)
    output = args.output or (
        ROOT / "experiments/local" /
        f"verification-{datetime.now(timezone.utc):%Y%m%dT%H%M%S%fZ}.json"
    )
    if output.exists() or output.is_symlink():
        parser.error("verification output already exists; choose a new output filename")
    if args.synthetic_output is not None:
        if args.synthetic_output.exists() or args.synthetic_output.is_symlink():
            parser.error("synthetic output already exists; choose a new output filename")
        if args.synthetic_output.resolve() == output.resolve():
            parser.error("synthetic and verification outputs must use different filenames")
    synthetic_command = ["-m", "gestureforge.evaluate", "--config", "experiments/prototype.json"]
    if args.synthetic_output is not None:
        synthetic_command.extend(["--output", str(args.synthetic_output)])
    commands = [
        ["-m", "ruff", "check", "gestureforge", "tests", "scripts"],
        ["-m", "mypy", "gestureforge", "scripts", "tests"],
        ["-m", "pytest", "-q"],
        ["-m", "gestureforge", "--smoke-test"],
        ["-m", "gestureforge", "--studio", "--smoke-test"],
        synthetic_command,
    ]
    results = []
    environment = {**os.environ, "QT_QPA_PLATFORM": "offscreen",
                   "MPLCONFIGDIR": str(ROOT / ".cache" / "matplotlib")}
    for command in commands:
        results.append(_run_check(command, environment, args.timeout))
        print(results[-1]["command"],
              "PASS" if results[-1]["returncode"] == 0 else "FAIL",
              flush=True)
    report = {"timestamp_utc": datetime.now(timezone.utc).isoformat(),
              "python": platform.python_version(), "platform": platform.platform(),
              "versions": {name: importlib.metadata.version(name) for name in
                           ["numpy", "scikit-learn", "mediapipe", "PySide6", "opencv-contrib-python"]},
              "checks": results,
              "limitations": ["Synthetic evaluation is software evidence only.",
                               "This script does not verify live participant performance or a second computer; see docs/evidence/RESULTS.md."]}
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        with output.open("x", encoding="utf-8") as handle:
            handle.write(json.dumps(report, indent=2) + "\n")
    except FileExistsError:
        parser.error("verification output already exists; choose a new output filename")
    print(f"Verification report: {output}", flush=True)
    return int(any(result["returncode"] for result in results))


if __name__ == "__main__":
    raise SystemExit(main())
