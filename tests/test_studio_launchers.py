import os
from pathlib import Path
import shutil
import subprocess

import pytest


ROOT = Path(__file__).resolve().parent.parent


@pytest.mark.skipif(os.name != "nt", reason="Windows batch launcher")
def test_windows_studio_launcher_forwards_arguments_and_failure(tmp_path):
    folder = tmp_path / "folder with spaces"
    folder.mkdir()
    launcher = folder / "run-studio.cmd"
    shutil.copyfile(ROOT / launcher.name, launcher)
    (folder / "run.cmd").write_text(
        '@echo off\necho %1\necho %2\necho %~3\nexit /b 23\n'
    )
    result = subprocess.run(
        [os.environ["COMSPEC"], "/d", "/c", "call", str(launcher),
         "--dataset", "data with spaces/manifest.json"],
        capture_output=True, text=True, timeout=10,
    )
    assert result.returncode == 23
    assert result.stdout.splitlines() == [
        "--studio", "--dataset", "data with spaces/manifest.json",
    ]


@pytest.mark.skipif(os.name == "nt", reason="Unix shell launcher")
def test_mac_studio_launcher_forwards_arguments_and_failure(tmp_path):
    folder = tmp_path / "folder with spaces"
    folder.mkdir()
    launcher = folder / "run-studio.command"
    shutil.copyfile(ROOT / launcher.name, launcher)
    (folder / "run.sh").write_text('#!/bin/bash\nprintf "%s\\n" "$@"\nexit 23\n')
    result = subprocess.run(
        ["/bin/bash", str(launcher), "--dataset", "data with spaces/manifest.json"],
        capture_output=True, text=True, timeout=10,
    )
    assert result.returncode == 23
    assert result.stdout.splitlines() == [
        "--studio", "--dataset", "data with spaces/manifest.json",
    ]
