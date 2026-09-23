"""Package tracked source only; never accidentally include private participant data."""

from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parent.parent


def main():
    files = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode().split("\0")
    files = [name for name in files if name and (ROOT / name).is_file()]
    if not files:
        raise SystemExit("Stage the reviewed release files before packaging.")
    forbidden = (".venv/", ".tools/", ".python/", "data/local/", "experiments/local/")
    if any(name.startswith(forbidden) for name in files):
        raise SystemExit("Private data or environment files are tracked; review before packaging.")
    target = ROOT / "releases" / "gestureforge-assignment-source.zip"
    target.parent.mkdir(exist_ok=True)
    with ZipFile(target, "w", ZIP_DEFLATED) as archive:
        for name in sorted(files):
            archive.write(ROOT / name, f"gestureforge/{name}")
    manifest = {"archive": target.name, "sha256": sha256(target.read_bytes()).hexdigest(),
                "files": len(files), "created_utc": datetime.now(timezone.utc).isoformat(),
                "note": "Source package. Participant evidence and signed declaration remain separate pending items."}
    target.with_suffix(".json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
