"""Launch a Studio measurement and retain its actual process exit and console logs."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import subprocess
import sys

from gestureforge.traces import _write_json_exclusive


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--seconds", type=float, default=1800)
    parser.add_argument("--camera", type=int, default=0)
    args = parser.parse_args(argv)
    if not math.isfinite(args.seconds) or args.seconds <= 0 or not 0 <= args.camera <= 2147483647:
        parser.error("seconds must be finite and positive; camera must be a nonnegative 32-bit integer")
    # A new directory keeps every receipt and log tied to this invocation.
    args.output_dir.mkdir(parents=True, exist_ok=False)
    measurement = args.output_dir / "measurement.json"
    command = [sys.executable, "-u", "-m", "scripts.monitor_studio", "--output",
               str(measurement), "--seconds", str(args.seconds), "--camera", str(args.camera)]
    exit_code = None
    launch_error = None
    print(f"Studio measurement starting. Receipts: {args.output_dir}", flush=True)
    with (args.output_dir / "stdout.log").open("xb") as stdout, \
            (args.output_dir / "stderr.log").open("xb") as stderr:
        try:
            exit_code = subprocess.run(command, stdout=stdout, stderr=stderr, check=False).returncode
        except OSError as exc:
            launch_error = str(exc)
    status = "missing"
    measurement_pass = False
    try:
        report = json.loads(measurement.read_text(encoding="utf-8"))
        if isinstance(report, dict):
            status = str(report.get("status", "invalid"))
            measurement_pass = (status == "final" and
                                report.get("measurement_criteria_met") is True)
        else:
            status = "invalid"
    except FileNotFoundError:
        pass
    except (OSError, ValueError):
        status = "unreadable"
    passed = exit_code == 0 and measurement_pass
    _write_json_exclusive(args.output_dir / "process.json", {
        "schema_version": 1,
        "kind": "studio_process_receipt",
        "child_process_exit_code": exit_code,
        "launch_error": launch_error,
        "measurement_status": status,
        "measurement_criteria_met": measurement_pass,
        "same_run_measurement_and_process_pass": passed,
        "limitations": ["Not workflow acceptance or physical camera reopen evidence.",
                        "A terminated launcher cannot certify subsequent child exit."],
    })
    print(f"Child process exit: {exit_code}; measurement: {status}; same-run pass: {passed}")
    return exit_code if exit_code else (0 if passed else 1)


if __name__ == "__main__":
    raise SystemExit(main())
