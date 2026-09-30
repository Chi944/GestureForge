import subprocess
from pathlib import Path

import pytest

from scripts import setup_macos


@pytest.mark.parametrize("system,machine,version,python,error", [
    ("Darwin", "arm64", "13.0", (3, 11), None),
    ("Darwin", "arm64", "26.0", (3, 11), None),
    ("Windows", "AMD64", "", (3, 11), "Windows"),
    ("Darwin", "x86_64", "14.0", (3, 11), "Rosetta"),
    ("Darwin", "arm64", "", (3, 11), "macOS version"),
    ("Darwin", "arm64", "12.7", (3, 11), "macOS 13"),
    ("Darwin", "arm64", "14.0", (3, 12), "Python 3.11"),
])
def test_runtime_guard(monkeypatch, system, machine, version, python, error):
    monkeypatch.setattr(setup_macos.platform, "system", lambda: system)
    monkeypatch.setattr(setup_macos.platform, "machine", lambda: machine)
    monkeypatch.setattr(setup_macos.platform, "mac_ver", lambda: (version, (), ""))
    monkeypatch.setattr(setup_macos.sys, "version_info", python)
    if error:
        with pytest.raises(SystemExit, match=error):
            setup_macos.validate_runtime()
    else:
        setup_macos.validate_runtime()


def test_setup_stops_before_download_if_install_fails(tmp_path, monkeypatch):
    monkeypatch.setattr(setup_macos, "ROOT", tmp_path / "folder with spaces")
    monkeypatch.setattr(setup_macos, "validate_runtime", lambda: None)
    calls = []

    def run(args, **kwargs):
        calls.append(args)
        assert kwargs["cwd"] == setup_macos.ROOT
        assert kwargs["check"]
        if "requirements.lock" in args:
            raise subprocess.CalledProcessError(1, args)

    monkeypatch.setattr(setup_macos.subprocess, "run", run)
    with pytest.raises(subprocess.CalledProcessError):
        setup_macos.main()
    assert "--only-binary=:all:" in calls[-1]
    assert not any("scripts/download_model.py" in args for args in calls)


def test_setup_preserves_incompatible_environment(tmp_path, monkeypatch):
    monkeypatch.setattr(setup_macos, "ROOT", tmp_path)
    monkeypatch.setattr(setup_macos, "validate_runtime", lambda: None)
    old = tmp_path / ".venv" / "Scripts"
    old.mkdir(parents=True)
    marker = old / "python.exe"
    marker.write_bytes(b"old environment")
    with pytest.raises(SystemExit, match="Rename"):
        setup_macos.main()
    assert marker.read_bytes() == b"old environment"


def test_shell_launcher_has_unix_line_endings():
    launcher = Path(__file__).resolve().parent.parent / "run.sh"
    assert b"\r" not in launcher.read_bytes()


@pytest.mark.parametrize("fail_studio", [False, True])
def test_setup_checks_both_gui_modes_before_reporting_success(
    tmp_path, monkeypatch, capsys, fail_studio
):
    monkeypatch.setattr(setup_macos, "ROOT", tmp_path)
    monkeypatch.setattr(setup_macos, "validate_runtime", lambda: None)
    monkeypatch.setattr(setup_macos.subprocess, "check_output", lambda *a, **k: "ca.pem\n")
    monkeypatch.setenv("QT_QPA_PLATFORM", "offscreen")
    calls = []

    def run(args, **kwargs):
        calls.append(args)
        assert kwargs["env"].get("QT_QPA_PLATFORM") is None
        if fail_studio and "--studio" in args:
            raise subprocess.CalledProcessError(1, args)

    monkeypatch.setattr(setup_macos.subprocess, "run", run)
    if fail_studio:
        with pytest.raises(subprocess.CalledProcessError):
            setup_macos.main()
    else:
        setup_macos.main()
    python = str(tmp_path / ".venv" / "bin" / "python")
    assert calls[-3:] == [
        (python, "scripts/check_environment.py", "--model"),
        (python, "-m", "gestureforge", "--smoke-test"),
        (python, "-m", "gestureforge", "--studio", "--smoke-test"),
    ]
    assert ("Setup complete" in capsys.readouterr().out) is not fail_studio
