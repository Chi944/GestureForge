"""Package tracked source, with an explicit private pilot-data option."""

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
from tempfile import NamedTemporaryFile
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parent.parent
SOURCE_ARCHIVE = "gestureforge-assignment-source.zip"
PRIVATE_ARCHIVE = "gestureforge-assignment-private-marker.zip"
PILOT_MANIFEST = Path("data/local/pilot/manifest.json")


def main(argv: list[str] | None = None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--include-pilot",
        action="store_true",
        help="Create a separate private marker ZIP with P01 numeric pilot data.",
    )
    args = parser.parse_args(argv)

    files = _tracked_source_files(ROOT)
    pilot_files = _pilot_files(ROOT) if args.include_pilot else []
    target_name = PRIVATE_ARCHIVE if args.include_pilot else SOURCE_ARCHIVE
    target = ROOT / "releases" / target_name
    archive_files = files + pilot_files

    _write_archive(ROOT, target, archive_files)
    manifest = {
        "archive": target.name,
        "sha256": sha256(target.read_bytes()).hexdigest(),
        "files": len(archive_files),
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "note": (
            "Private marker package. Includes tracked source plus P01 numeric pilot manifest "
            "and referenced feature sidecar only; no raw images or video."
            if args.include_pilot
            else "Source package. Participant evidence and signed declaration remain separate pending items."
        ),
    }
    target.with_suffix(".json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


def _tracked_source_files(root: Path) -> list[Path]:
    files = subprocess.check_output(["git", "ls-files", "-z"], cwd=root).decode().split("\0")
    files = [name for name in files if name and (root / name).is_file()]
    if not files:
        raise SystemExit("Stage the reviewed release files before packaging.")
    forbidden = (".venv/", ".tools/", ".python/", ".cache/", ".local/",
                 "data/local/", "experiments/local/")
    local_documents = {"docs/submission/GestureForge_Technical_Report.docx",
                       "docs/submission/Prompt_Log.docx", "docs/submission/Decision_Log.docx"}
    if any(name.startswith(forbidden) or name in local_documents for name in files):
        raise SystemExit("Private data or environment files are tracked; review before packaging.")
    return [Path(name) for name in sorted(files)]


def _pilot_files(root: Path) -> list[Path]:
    from gestureforge.dataset import load_dataset

    manifest_path = root / PILOT_MANIFEST
    bundle = load_dataset(manifest_path)
    participants = {record.participant_id for record in bundle.records}
    provenances = {record.provenance for record in bundle.records}
    if (
        participants != {"P01"}
        or provenances != {"human"}
        or bundle.metadata.get("provenance") != "human"
    ):
        raise SystemExit("Pilot package requires exact P01 human numeric records.")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    feature_path = manifest_path.with_name(str(manifest["feature_file"]))
    return [_relative_to_root(root, manifest_path), _relative_to_root(root, feature_path)]


def _write_archive(root: Path, target: Path, files: list[Path]) -> None:
    target.parent.mkdir(exist_ok=True)
    archive_entries = [(name, _project_path(root, name)) for name in files]
    with NamedTemporaryFile(dir=target.parent, suffix=".zip", delete=False) as handle:
        temp_target = Path(handle.name)
    try:
        with ZipFile(temp_target, "w", ZIP_DEFLATED) as archive:
            for name, source_path in archive_entries:
                archive.write(source_path, f"gestureforge/{name.as_posix()}")
        temp_target.replace(target)
    finally:
        if temp_target.exists():
            temp_target.unlink()


def _relative_to_root(root: Path, path: Path) -> Path:
    try:
        return path.resolve().relative_to(root.resolve())
    except ValueError as exc:
        raise SystemExit(f"Refusing to package path outside project: {path}") from exc


def _project_path(root: Path, name: Path) -> Path:
    if name.is_absolute() or ".." in name.parts:
        raise SystemExit(f"Refusing to package path outside project: {name}")
    path = (root / name).resolve()
    _relative_to_root(root, path)
    return path


if __name__ == "__main__":
    main()
