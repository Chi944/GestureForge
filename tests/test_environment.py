"""The setup model check must verify the same bytes it gives to MediaPipe."""

from contextlib import contextmanager
import hashlib
import json
from types import SimpleNamespace
import sys

import pytest

from scripts import check_environment


@pytest.mark.parametrize("corrupt", [False, True])
def test_unicode_model_check_verifies_before_native_start(tmp_path, monkeypatch, capsys, corrupt):
    root = tmp_path / "\u4e2d\u6587 project"
    assets = root / "assets"
    assets.mkdir(parents=True)
    model_bytes = b"model data"
    digest = hashlib.sha256(model_bytes).hexdigest()
    (assets / "hand_landmarker.task").write_bytes(b"bad data" if corrupt else model_bytes)
    (assets / "model_manifest.json").write_text(json.dumps({"sha256": digest}))
    monkeypatch.setattr(check_environment, "__file__", str(root / "scripts/check_environment.py"))
    monkeypatch.setattr(sys, "argv", ["check_environment.py", "--model"])
    calls = []

    def detect(image, timestamp):
        assert not image.data.any() and image.data.shape == (256, 256, 3)
        assert timestamp == 1
        calls.append("inference")
        return SimpleNamespace(hand_landmarks=[])

    @contextmanager
    def create(options):
        assert vars(options.base_options) == {"model_asset_buffer": model_bytes}
        calls.append("create")
        try:
            yield SimpleNamespace(detect_for_video=detect)
        finally:
            calls.append("close")

    fake_mp = SimpleNamespace(
        tasks=SimpleNamespace(
            BaseOptions=lambda **kwargs: SimpleNamespace(**kwargs),
            vision=SimpleNamespace(
                HandLandmarkerOptions=lambda **kwargs: SimpleNamespace(**kwargs),
                RunningMode=SimpleNamespace(VIDEO="VIDEO"),
                HandLandmarker=SimpleNamespace(create_from_options=create),
            ),
        ),
        ImageFormat=SimpleNamespace(SRGB="SRGB"),
        Image=lambda **kwargs: SimpleNamespace(**kwargs),
    )
    monkeypatch.setitem(sys.modules, "mediapipe", fake_mp)
    if corrupt:
        with pytest.raises(SystemExit, match="checksum mismatch"):
            check_environment.main()
        assert calls == []
    else:
        check_environment.main()
        report = json.loads(capsys.readouterr().out)
        assert report["model"] == {"sha256": digest, "blank_image_hands": 0, "camera_opened": False}
        assert calls == ["create", "inference", "close"]
