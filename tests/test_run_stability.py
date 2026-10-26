import json
import subprocess
import sys

import pytest

from scripts.run_stability import main


@pytest.mark.parametrize("status,measurement_pass,child_exit,expected", [
    ("final", True, 0, 0),
    ("final", True, 7, 7),
    ("final", False, 0, 1),
    ("incomplete_checkpoint", True, 0, 1),
    ("incomplete_checkpoint", False, 7, 7),
    (None, False, 0, 1),
    ("invalid_json", False, 9, 9),
])
def test_real_child_exit_and_logs(tmp_path, monkeypatch, status, measurement_pass,
                                  child_exit, expected):
    output = tmp_path / "run"
    real_run = subprocess.run

    def child(command, **kwargs):
        assert command[:4] == [sys.executable, "-u", "-m", "scripts.monitor_studio"]
        assert command[4:6] == ["--output", str(output / "measurement.json")]
        if status is not None:
            content = "broken" if status == "invalid_json" else json.dumps({
                "status": status, "measurement_criteria_met": measurement_pass,
            })
            (output / "measurement.json").write_text(content, encoding="utf-8")
        return real_run([sys.executable, "-c",
                         f"import sys; print('stdout marker'); print('stderr marker', "
                         f"file=sys.stderr); sys.exit({child_exit})"], **kwargs)

    monkeypatch.setattr("scripts.run_stability.subprocess.run", child)
    assert main(["--output-dir", str(output), "--seconds", "1"]) == expected
    receipt = json.loads((output / "process.json").read_text())
    assert receipt["child_process_exit_code"] == child_exit
    assert receipt["same_run_measurement_and_process_pass"] == (expected == 0)
    assert receipt["measurement_criteria_met"] == (status == "final" and measurement_pass)
    assert "stdout marker" in (output / "stdout.log").read_text()
    assert "stderr marker" in (output / "stderr.log").read_text()
    if status == "incomplete_checkpoint":
        assert json.loads((output / "measurement.json").read_text())["status"] == status


def test_existing_output_refused_before_launch(tmp_path, monkeypatch):
    sentinel = tmp_path / "stdout.log"
    sentinel.write_text("previous evidence")
    def unexpected(*args, **kwargs):
        pytest.fail("must not launch into existing directory")
    monkeypatch.setattr("scripts.run_stability.subprocess.run", unexpected)
    with pytest.raises(FileExistsError):
        main(["--output-dir", str(tmp_path)])
    assert sentinel.read_text() == "previous evidence"


def test_launch_error_receipt(tmp_path, monkeypatch):
    output = tmp_path / "run"
    def fail(*args, **kwargs):
        raise OSError("launch unavailable")
    monkeypatch.setattr("scripts.run_stability.subprocess.run", fail)
    assert main(["--output-dir", str(output)]) == 1
    receipt = json.loads((output / "process.json").read_text())
    assert receipt["child_process_exit_code"] is None
    assert receipt["measurement_status"] == "missing"
    assert not receipt["same_run_measurement_and_process_pass"]


@pytest.mark.parametrize("option,value", [("--seconds", "nan"), ("--seconds", "0"),
                                         ("--camera", "-1"), ("--camera", "2147483648")])
def test_bad_arguments_do_not_create_output(tmp_path, option, value):
    output = tmp_path / "run"
    with pytest.raises(SystemExit) as result:
        main(["--output-dir", str(output), option, value])
    assert result.value.code == 2
    assert not output.exists()
