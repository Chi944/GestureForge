import json
import subprocess

import pytest

from scripts import verify


def test_verify_records_timeout_and_continues(tmp_path, monkeypatch):
    monkeypatch.setattr(verify, "ROOT", tmp_path)
    monkeypatch.setattr(verify.importlib.metadata, "version", lambda _name: "1.0")
    monkeypatch.setattr(verify.platform, "platform", lambda: "test-platform")
    calls = []

    def run(args, **kwargs):
        calls.append((args, kwargs))
        assert kwargs["timeout"] == 1.5
        if len(calls) == 1:
            raise subprocess.TimeoutExpired(
                args,
                kwargs["timeout"],
                output=b"pytest said passed before hanging",
                stderr=b"still running",
            )
        return subprocess.CompletedProcess(args, 0, stdout="ok", stderr="")

    monkeypatch.setattr(verify.subprocess, "run", run)
    output = tmp_path / "verification.json"
    synthetic = tmp_path / "synthetic.json"

    assert verify.main([
        "--output", str(output),
        "--synthetic-output", str(synthetic),
        "--timeout", "1.5",
    ]) == 1

    report = json.loads(output.read_text(encoding="utf-8"))
    assert len(calls) == 6
    assert report["checks"][0]["returncode"] == 124
    assert report["checks"][0]["timed_out"] is True
    assert report["checks"][0]["stdout"] == "pytest said passed before hanging"
    assert report["checks"][0]["stderr"] == "still running"
    assert report["checks"][1]["returncode"] == 0


def test_successful_check_result_stays_compatible(monkeypatch):
    def run(args, **kwargs):
        assert kwargs["timeout"] == 2.0
        return subprocess.CompletedProcess(args, 0, stdout="ok", stderr="")

    monkeypatch.setattr(verify.subprocess, "run", run)

    result = verify._run_check(["-m", "ruff"], {}, 2.0)

    assert result["returncode"] == 0
    assert result["stdout"] == "ok"
    assert "timed_out" not in result


def test_default_verification_captures_synthetic_stdout(tmp_path, monkeypatch):
    monkeypatch.setattr(verify, "ROOT", tmp_path)
    monkeypatch.setattr(verify.importlib.metadata, "version", lambda _name: "1.0")
    calls = []

    def run(command, _environment, _timeout):
        calls.append(command)
        return {"command": " ".join(command), "returncode": 0, "stdout": "synthetic-result"}

    monkeypatch.setattr(verify, "_run_check", run)
    assert verify.main([]) == 0
    assert calls[-1] == ["-m", "gestureforge.evaluate", "--config", "experiments/prototype.json"]
    report = json.loads((tmp_path / "docs/evidence/verification.json").read_text())
    assert report["checks"][-1]["stdout"] == "synthetic-result"


@pytest.mark.parametrize("existing", [False, True])
def test_conflicting_synthetic_output_refused_before_checks(tmp_path, monkeypatch, existing):
    monkeypatch.setattr(verify, "ROOT", tmp_path)
    monkeypatch.setattr(verify, "_run_check", lambda *_args: pytest.fail("checks must not run"))
    synthetic = tmp_path / "synthetic.json"
    output = tmp_path / "verification.json" if existing else synthetic
    if existing:
        synthetic.write_text("keep the previous result")
    with pytest.raises(SystemExit) as exc:
        verify.main(["--output", str(output), "--synthetic-output", str(synthetic)])
    assert exc.value.code == 2
    if existing:
        assert synthetic.read_text() == "keep the previous result"
    else:
        assert not output.exists()


@pytest.mark.parametrize("value", ["0", "-1", "nan", "inf", "abc"])
def test_timeout_must_be_positive_and_finite(value):
    with pytest.raises(SystemExit) as exc:
        verify.main(["--timeout", value])

    assert exc.value.code == 2
