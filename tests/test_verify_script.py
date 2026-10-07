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


@pytest.mark.parametrize("value", ["0", "-1", "nan", "inf", "abc"])
def test_timeout_must_be_positive_and_finite(value):
    with pytest.raises(SystemExit) as exc:
        verify.main(["--timeout", value])

    assert exc.value.code == 2
