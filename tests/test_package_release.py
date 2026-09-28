import json
import subprocess
from pathlib import Path
from zipfile import ZipFile

import numpy as np
import pytest

from gestureforge.dataset import SampleRecord, save_dataset
from scripts import package_release


def test_source_package_excludes_untracked_private_data(tmp_path, monkeypatch):
    root = _source_repo(tmp_path)
    _pilot_dataset(root)
    monkeypatch.setattr(package_release, "ROOT", root)

    package_release.main([])

    names = _zip_names(root / "releases" / package_release.SOURCE_ARCHIVE)
    assert "gestureforge/README.md" in names
    assert "gestureforge/experiments/pilot.json" in names
    assert not any(name.startswith("gestureforge/data/local/") for name in names)


@pytest.mark.parametrize("folder", [".local", ".cache"])
def test_source_package_refuses_accidentally_tracked_working_files(tmp_path, folder):
    root = _source_repo(tmp_path)
    local = root / folder / "working-notes.md"
    local.parent.mkdir()
    local.write_text("Not a submission artifact", encoding="utf-8")
    subprocess.run(["git", "add", str(local)], cwd=root, check=True)

    with pytest.raises(SystemExit, match="review before packaging"):
        package_release._tracked_source_files(root)


@pytest.mark.parametrize("filename", ["GestureForge_Technical_Report.docx",
                                      "Prompt_Log.docx", "Decision_Log.docx"])
def test_package_refuses_local_submission_documents(tmp_path, filename):
    root = _source_repo(tmp_path)
    document = root / "docs/submission" / filename
    document.parent.mkdir(parents=True)
    document.write_bytes(b"local document")
    subprocess.run(["git", "add", str(document)], cwd=root, check=True)

    with pytest.raises(SystemExit, match="review before packaging"):
        package_release._tracked_source_files(root)


def test_include_pilot_private_package_adds_only_manifest_and_referenced_features(
    tmp_path, monkeypatch
):
    root = _source_repo(tmp_path)
    feature_file = _pilot_dataset(root)
    monkeypatch.setattr(package_release, "ROOT", root)

    package_release.main(["--include-pilot"])

    names = _zip_names(root / "releases" / package_release.PRIVATE_ARCHIVE)
    assert "gestureforge/README.md" in names
    assert "gestureforge/experiments/pilot.json" in names
    assert "gestureforge/data/local/pilot/manifest.json" in names
    assert f"gestureforge/data/local/pilot/{feature_file}" in names
    assert "gestureforge/data/local/pilot/CONSENT.md" not in names
    assert sum(name.startswith("gestureforge/data/local/pilot/") for name in names) == 2


def test_include_pilot_fails_before_overwriting_existing_private_archive(
    tmp_path, monkeypatch
):
    root = _source_repo(tmp_path)
    feature_file = _pilot_dataset(root)
    (root / "data/local/pilot" / feature_file).write_bytes(b"corrupt")
    target = root / "releases" / package_release.PRIVATE_ARCHIVE
    target.parent.mkdir()
    target.write_bytes(b"old package")
    monkeypatch.setattr(package_release, "ROOT", root)

    with pytest.raises(ValueError):
        package_release.main(["--include-pilot"])

    assert target.read_bytes() == b"old package"


def test_include_pilot_requires_manifest_before_overwriting(tmp_path, monkeypatch):
    root = _source_repo(tmp_path)
    target = root / "releases" / package_release.PRIVATE_ARCHIVE
    target.parent.mkdir()
    target.write_bytes(b"old package")
    monkeypatch.setattr(package_release, "ROOT", root)

    with pytest.raises(FileNotFoundError):
        package_release.main(["--include-pilot"])

    assert target.read_bytes() == b"old package"


def test_archive_rejects_outside_path_before_overwriting(tmp_path):
    root = _source_repo(tmp_path)
    target = root / "releases" / package_release.PRIVATE_ARCHIVE
    target.parent.mkdir()
    target.write_bytes(b"old package")

    with pytest.raises(SystemExit):
        package_release._write_archive(root, target, [Path("../outside.txt")])

    assert target.read_bytes() == b"old package"


def _source_repo(root: Path) -> Path:
    (root / "experiments").mkdir()
    (root / "README.md").write_text("GestureForge\n", encoding="utf-8")
    (root / "experiments/pilot.json").write_text(
        json.dumps({"dataset_path": "data/local/pilot/manifest.json"}) + "\n",
        encoding="utf-8",
    )
    subprocess.run(["git", "init"], cwd=root, check=True, stdout=subprocess.DEVNULL)
    subprocess.run(["git", "add", "README.md", "experiments/pilot.json"], cwd=root, check=True)
    return root


def _pilot_dataset(root: Path):
    records = [
        SampleRecord(
            participant_id="P01",
            session_id="train-session",
            trial_id="train-session-NEXT-00",
            intended_label="NEXT",
            split="train",
            sample_index=0,
            timestamp=1.0,
            valid=True,
            hand="Right",
            provenance="human",
        )
    ]
    save_dataset(
        root / package_release.PILOT_MANIFEST,
        records,
        np.zeros((1, 60), dtype=np.float32),
        {"provenance": "human"},
    )
    manifest = json.loads((root / package_release.PILOT_MANIFEST).read_text(encoding="utf-8"))
    return manifest["feature_file"]


def _zip_names(path: Path) -> set[str]:
    with ZipFile(path) as archive:
        return set(archive.namelist())
