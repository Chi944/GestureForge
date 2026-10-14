"""Checks the single-file packaging boundary without downloading runtime assets."""

from hashlib import sha256
from html.parser import HTMLParser
import json
import sys
import types
from zipfile import ZipFile

import pytest

from scripts import package_participant as package


def _small_assets(tmp_path, monkeypatch, write_collector=True):
    if write_collector:
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
    return model


def _real_collector_root(tmp_path, monkeypatch):
    real_root = package.ROOT
    source = tmp_path / "participant"
    source.mkdir()
    for name in ("collector.html", "collector.mjs", "THIRD_PARTY_NOTICES.txt"):
        source.joinpath(name).write_bytes(real_root.joinpath("participant", name).read_bytes())
    model = _small_assets(tmp_path, monkeypatch, write_collector=False)
    return model


def _ticket(target="P02"):
    return {
        "schema_version": 1,
        "protocol": "gestureforge-browser-test-v1",
        "paired_protocol": "gf-p18-positive-test-v1",
        "target_participant": target,
        "config_fingerprint": "cfg<private",
        "frozen_integrity_sha256": "frozen-private-sha",
        "pose_set_id": "standard-v1",
        "hand": "Right",
    }


class ElementParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.elements = []
        self.stack = []

    def handle_starttag(self, tag, attrs):
        element = {"tag": tag, "attrs": dict(attrs), "text": ""}
        self.elements.append(element)
        self.stack.append(element)

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index]["tag"] == tag:
                del self.stack[index:]
                return

    def handle_data(self, data):
        for element in self.stack:
            element["text"] += data

    def by_id(self, element_id):
        return next(element for element in self.elements if element["attrs"].get("id") == element_id)

    def label_for(self, target):
        return next(
            element for element in self.elements
            if element["tag"] == "label" and element["attrs"].get("for") == target
        )

    def options(self):
        return [element for element in self.elements if element["tag"] == "option"]


def test_embed_verified_assets_and_reject_tampering(tmp_path, monkeypatch):
    model = _small_assets(tmp_path, monkeypatch)
    html = package.assemble_html(tmp_path, model)
    assert "export const checked = true;" in html
    assert "src=" not in html and "BASE64__" not in html
    assert "bW9kZWw=" in html
    model.write_bytes(b"tampered")
    with pytest.raises(ValueError, match="checksum mismatch"):
        package.assemble_html(tmp_path, model)


def test_frozen_test_html_embeds_only_public_ticket_and_locks_visible_form(tmp_path, monkeypatch):
    model = _real_collector_root(tmp_path, monkeypatch)
    frozen = tmp_path / "private-frozen-config.json"
    frozen.write_text("not read by patched ticket helper", encoding="utf-8")
    ticket = _ticket()
    monkeypatch.setattr(package, "browser_test_ticket", lambda path: ticket)

    html = package.assemble_html(tmp_path, model, frozen)
    parser = ElementParser()
    parser.feed(html)

    ticket_tag = parser.by_id("testTicket")
    assert ticket_tag["tag"] == "script"
    assert ticket_tag["attrs"]["type"] == "application/json"
    assert json.loads(ticket_tag["text"]) == ticket
    assert "<private" not in html
    assert "\\u003cprivate" in html
    assert "private-frozen-config" not in html
    assert len([element for element in parser.elements if element["attrs"].get("id") == "testTicket"]) == 1

    assert "Fresh TEST session for the assigned participant only." in html
    participant = parser.by_id("participantId")
    assert participant["attrs"]["value"] == "P02"
    assert "readonly" in participant["attrs"]
    assert parser.label_for("trainConditions")["text"].strip() == (
        "TEST conditions - fill in before TEST"
    )
    assert not any(element["attrs"].get("for") == "validationConditions" for element in parser.elements)
    assert "hidden" in parser.by_id("validationConditions")["attrs"]
    assert parser.by_id("progressText")["text"].strip() == "0 / 48 trials complete"
    assert [(option["attrs"]["value"], option["text"].strip()) for option in parser.options()] == [
        ("test", "TEST - 48 trials, about 5-6 minutes")
    ]
    assert "15-20 minutes" not in html
    assert "UNKNOWN - 8 trials" not in html
    assert "Unknown trials" not in html
    assert "Record only the shown TEST poses" in html


def test_frozen_test_guide_copy_is_test_only(tmp_path, monkeypatch):
    captured: list[str] = []

    class Style:
        pass

    class Styles(dict):
        def add(self, style):
            self["Lead"] = style

    class Table:
        def __init__(self, rows, **_kwargs):
            self.rows = rows

        def setStyle(self, _style):
            pass

    def paragraph(text, _style):
        captured.append(text)
        return text

    class Document:
        def __init__(self, *_args, **_kwargs):
            pass

        def build(self, content, **_kwargs):
            captured.extend(str(item) for item in content if isinstance(item, str))

    modules = {
        "reportlab": types.ModuleType("reportlab"),
        "reportlab.lib": types.ModuleType("reportlab.lib"),
        "reportlab.lib.colors": types.SimpleNamespace(HexColor=lambda value: value, white="white"),
        "reportlab.lib.styles": types.SimpleNamespace(
            ParagraphStyle=lambda *_args, **_kwargs: Style(),
            getSampleStyleSheet=lambda: Styles({
                "Title": Style(),
                "Lead": Style(),
                "BodyText": Style(),
                "Heading1": Style(),
                "Heading2": Style(),
            }),
        ),
        "reportlab.lib.units": types.SimpleNamespace(inch=1),
        "reportlab.platypus": types.SimpleNamespace(
            PageBreak=lambda: "PAGEBREAK",
            Paragraph=paragraph,
            SimpleDocTemplate=Document,
            Spacer=lambda *_args: "SPACER",
            Table=Table,
            TableStyle=lambda *_args: None,
        ),
    }
    for name, module in modules.items():
        monkeypatch.setitem(sys.modules, name, module)
    frozen = tmp_path / "frozen.json"
    frozen.write_text("not read by patched ticket helper", encoding="utf-8")
    monkeypatch.setattr(package, "browser_test_ticket", lambda path: _ticket())

    package.write_guide(tmp_path / "READ_FIRST.pdf", "Windows", frozen)

    text = "\n".join(captured)
    assert "P02" in text
    assert "one fresh 48-trial TEST session" in text
    assert "5-6 minutes" in text
    assert "EMAIL_THIS_P02_test.zip" in text
    assert "EMAIL_THIS_P02_PARTIAL_test.zip" in text
    assert "same TEST kit" in text
    assert "Do not import old development data" in text
    assert "Start Camera" in text and "Start Selected Session" in text
    assert "chronology evidence" not in text
    assert "manual Windows and macOS webcam checks" not in text
    assert all(label in text for label in ("NEUTRAL", "NEXT", "PREVIOUS", "BOOKMARK"))
    assert "UNKNOWN" not in text
    assert "Development collection" not in text


def test_main_frozen_packages_use_distinct_test_names(tmp_path, monkeypatch):
    model = _real_collector_root(tmp_path, monkeypatch)
    frozen = tmp_path / "private-frozen-config.json"
    frozen.write_text("not read by patched ticket helper", encoding="utf-8")
    out = tmp_path / "out"
    monkeypatch.setattr(package, "browser_test_ticket", lambda path: _ticket("P07"))
    monkeypatch.setattr(package, "write_guide", lambda path, platform, frozen=None: path.write_bytes(b"pdf"))
    monkeypatch.setattr(package.subprocess, "check_output", lambda args, **kwargs: "deadbeef\n")
    monkeypatch.setattr(sys, "argv", [
        "package_participant.py",
        "--assets", str(tmp_path),
        "--model", str(model),
        "--frozen", str(frozen),
        "--output", str(out),
    ])

    package.main()

    expected = {"GestureForge_P07_TEST_Windows.zip", "GestureForge_P07_TEST_macOS.zip"}
    assert {path.name for path in out.glob("*.zip")} == expected
    report = json.loads((out / "verification.json").read_text(encoding="utf-8"))
    assert report["collection_mode"] == "test"
    assert report["test_ticket"]["target_participant"] == "P07"
    with ZipFile(out / "GestureForge_P07_TEST_Windows.zip") as archive:
        html = archive.read("START_HERE.html").decode()
    assert "testTicket" in html
    assert "private-frozen-config" not in html
