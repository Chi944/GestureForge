"""Checks the single-file packaging boundary without downloading runtime assets."""

from hashlib import sha256

import pytest

from scripts import package_participant as package


def test_embed_verified_assets_and_reject_tampering(tmp_path, monkeypatch):
    source = tmp_path / "participant"
    source.mkdir()
    (source / "collector.html").write_text(
        '__SDK_BASE64__ __LOADER_BASE64__ __WASM_BASE64__ __MODEL_BASE64__ '
        '<script type="module" src="collector.mjs"></script>', encoding="utf-8"
    )
    (source / "collector.mjs").write_text("export const checked = true;", encoding="utf-8")
    assets = {}
    for key in ("sdk", "loader", "wasm"):
        name = f"{key}.bin"
        (tmp_path / name).write_bytes(key.encode())
        assets[key] = (name, sha256(key.encode()).hexdigest())
    model = tmp_path / "model.task"
    model.write_bytes(b"model")
    monkeypatch.setattr(package, "ROOT", tmp_path)
    monkeypatch.setattr(package, "ASSETS", assets)
    monkeypatch.setattr(package, "MODEL_SHA", sha256(b"model").hexdigest())
    html = package.assemble_html(tmp_path, model)
    assert "export const checked = true;" in html
    assert "src=" not in html and "BASE64__" not in html
    assert "bW9kZWw=" in html
    model.write_bytes(b"tampered")
    with pytest.raises(ValueError, match="checksum mismatch"):
        package.assemble_html(tmp_path, model)
