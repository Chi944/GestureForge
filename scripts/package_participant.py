"""Build offline collection-only kits. Build-time PDF tooling is not shipped."""

from __future__ import annotations

import argparse
import base64
from hashlib import sha256
import json
from pathlib import Path
import subprocess
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
ASSETS = {
    "sdk": ("vision_bundle.mjs", "9d5fc9ef74b22329cf9aa88dc543956d192b8c254210b187271614713eb5b10c"),
    "loader": ("vision_wasm_nosimd_internal.js", "510fc70a170eb8b46767a7abab2af89a7a8341fa5b3ebfb8a5de41a79b7fa9df"),
    "wasm": ("vision_wasm_nosimd_internal.wasm", "b802041d105876865d6a0806f2ff7c4419a7f1b80bc01340fe36e759c2030011"),
}
MODEL_SHA = "fbc2a30080c3c557093b5ddfc334698132eb341044ccee322ccf8bcf3607cde1"


def verified_bytes(path: Path, expected: str) -> bytes:
    data = path.read_bytes()
    if sha256(data).hexdigest() != expected:
        raise ValueError(f"Asset checksum mismatch: {path.name}")
    return data


def assemble_html(assets: Path, model: Path) -> str:
    html = (ROOT / "participant/collector.html").read_text(encoding="utf-8")
    module = (ROOT / "participant/collector.mjs").read_text(encoding="utf-8")
    if "</script" in module.lower():
        raise ValueError("Module contains an inline script terminator")
    entrypoint = '<script type="module" src="collector.mjs"></script>'
    if html.count(entrypoint) != 1:
        raise ValueError("Expected one collector entrypoint")
    html = html.replace(entrypoint,
                        f'<script type="module">\n{module}\n</script>')
    for key, (name, digest) in ASSETS.items():
        token = f"__{key.upper()}_BASE64__"
        if html.count(token) != 1:
            raise ValueError(f"Expected one {token}")
        html = html.replace(token, base64.b64encode(verified_bytes(assets / name, digest)).decode())
    if html.count("__MODEL_BASE64__") != 1:
        raise ValueError("Expected one model token")
    return html.replace("__MODEL_BASE64__", base64.b64encode(verified_bytes(model, MODEL_SHA)).decode())


def write_guide(path: Path, platform: str) -> None:
    from reportlab.lib import colors
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle("Lead", fontName="Helvetica", fontSize=12, leading=17,
                              textColor=colors.HexColor("#21364a"), spaceAfter=14))
    styles["BodyText"].fontSize = 10
    styles["BodyText"].leading = 15
    styles["BodyText"].spaceAfter = 9
    styles["Heading1"].textColor = colors.HexColor("#153f59")
    styles["Heading2"].textColor = colors.HexColor("#153f59")
    content = []

    def p(text: str, style: str = "BodyText") -> None:
        content.append(Paragraph(text, styles[style]))

    def step(title: str, text: str) -> None:
        p(title, "Heading2")
        p(text)

    p("GestureForge", "Title")
    p(f"Participant recording guide | {platform}", "Heading1")
    p("A webcam, your right hand and an existing browser. No Python, coding tools, "
      "account or installation is needed. The hand detector is included in this download.", "Lead")
    p("<b>This is a data-collection kit, not the full GestureForge Studio app.</b> "
      "It records numeric hand positions and timing, not photographs, video or sound. "
      "Nothing is uploaded automatically. It works offline after you receive the ZIP.")
    step("1  Save and unzip", (
        "Save the Windows ZIP from the email. In Downloads, right-click the ZIP, choose "
        "<b>Extract All</b>, then <b>Extract</b>. Open the new folder. Do not run from inside the ZIP."
        if platform == "Windows" else
        "Save the macOS ZIP from the email. In Finder, open Downloads and double-click the ZIP. "
        "Open the folder that appears."
    ))
    step("2  Open the recorder", (
        "Double-click <b>START_HERE.html</b>. If it opens as text, right-click it, choose "
        "<b>Open with</b>, then Microsoft Edge or Google Chrome."
        if platform == "Windows" else
        "Double-click <b>START_HERE.html</b> to open your browser. If it opens as text, "
        "right-click it, choose <b>Open With</b>, then Safari or an already installed Chrome."
    ) + " Keep this same file in the same folder until you finish. Close other camera apps. "
      "Keep your laptop plugged in and awake.")
    step("3  Enter your details and permission", "Use the participant code Deston or Hau Jie "
         "gave you, not your name. Enter your lighting, background, sitting/standing position "
         "and approximate hand distance. Read the consent text and tick the permission boxes "
         "only if you agree. Your numeric data is for the team and private marker only; "
         "the team will delete it after marking and appeals finish. Contact Deston or "
         "Hau Jie if you have questions before agreeing.")
    step("4  Allow the camera", "Start the camera when prompted and select <b>Allow</b>. "
         "Wait for the hand detector to finish loading. Keep your entire right hand visible, "
         "palm towards the camera, with light on your hand. The preview is mirrored like a mirror. "
         "The on-screen hand check should say Right; if it does not, stop and contact the team.")
    p("<b>Before a full recording:</b> the coordinator should verify this extracted kit on "
      "Windows and macOS, including camera permission and a saved return ZIP. These device "
      "checks are separate from the software checks. If your browser cannot start the detector "
      "or camera, stop and send the visible error to the team; do not change security settings.")
    content.append(PageBreak())
    p("Record, save, send", "Heading1")
    p("Follow the large instruction on screen. Get ready during the countdown, hold still "
      "during recording, then relax during the release interval. Plan about 15-20 minutes "
      "plus a break; pause whenever you need to.", "Lead")
    rows = [[Paragraph("On screen", styles["BodyText"]), Paragraph("Use your RIGHT hand", styles["BodyText"])]]
    for label, pose in [
        ("NEUTRAL", "Open palm towards the camera; fingers extended."),
        ("NEXT", "Closed fist towards the camera."),
        ("PREVIOUS", "Thumb pointing up; other fingers folded."),
        ("BOOKMARK", "Index and middle fingers extended; other fingers folded."),
        ("UNKNOWN", "Follow the different non-command instructions on screen. Do not substitute one of the four poses above."),
    ]:
        rows.append([Paragraph(f"<b>{label}</b>", styles["BodyText"]), Paragraph(pose, styles["BodyText"])])
    table = Table(rows, colWidths=[1.15 * inch, 5.25 * inch], hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#dceef2")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f5f8fa"), colors.white]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 9), ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    content += [table, Spacer(1, 12)]
    step("5  Finish the three sections", "Choose <b>TRAIN</b> in the session list, then click "
         "<b>Start Selected Session</b>. Follow 48 short trials automatically (12 per pose; about 5-6 minutes). "
         "Take a break, remove your hand, then explicitly start <b>VALIDATION</b>: another 48 trials, about 5-6 minutes. "
         "Enter the current conditions for each session. Finally complete the 8 <b>UNKNOWN</b> "
         "development trials (about 1 minute). Keep the recorder tab visible. This kit does not collect final TEST data. The team will contact "
         "you separately after the evaluation settings are frozen.")
    step("6  Save your return ZIP", "Click <b>Export Return ZIP</b> after each session "
         "and at the end. If still recording, click <b>Pause</b> first and wait for it to settle. "
         "Your browser saves a ZIP in Downloads, or asks you where to save it. "
         "Keep the newest file. Completed recordings are also saved locally by the browser "
         "when storage is available. The downloaded ZIP is your reliable backup.")
    step("7  Email that ZIP to the team", "Attach the newest file whose name starts with "
         "<b>EMAIL_THIS_</b> and ends in <b>_development.zip</b>. <b>It is already zipped: "
         "do not unzip it or zip the program folder.</b> Include your participant code, Windows "
         "or macOS version, browser name, and any problems or help you needed. A file marked "
         "PARTIAL is incomplete; keep it and report the interruption instead of deleting trials.")
    p("<b>If interrupted:</b> use Pause before leaving the page. Download a backup before "
      "closing. Returning to the same file can recover the locally saved work; the recorder "
      "also lets you load its previous return ZIP. Do not re-record completed trials or "
      "edit the return data to remove mistakes. Camera or tab interruptions preserve missed "
      "samples as invalid. After the team confirms receipt, <b>Clear Local Draft</b> removes "
      "this browser's saved recording; keep your emailed ZIP until receipt is confirmed.")

    def footer(canvas, doc):
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#506070"))
        canvas.drawString(42, 24, "GestureForge | Development collection | No final TEST recording")
        canvas.drawRightString(553, 24, str(doc.page))

    SimpleDocTemplate(str(path), pagesize=(595, 842), leftMargin=42, rightMargin=42,
                      topMargin=36, bottomMargin=42, title=f"GestureForge {platform} participant guide",
                      author="GestureForge team").build(content, onFirstPage=footer, onLaterPages=footer)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assets", type=Path, required=True)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=ROOT / ".local/participant-deliverables")
    args = parser.parse_args()
    html = assemble_html(args.assets, args.model)
    args.output.mkdir(parents=True, exist_ok=True)
    notices = (ROOT / "participant/THIRD_PARTY_NOTICES.txt").read_bytes()
    packages: list[dict[str, str | int]] = []
    report = {"source_commit": subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "source_dirty": bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT)),
        "collector_sha256": sha256(html.encode()).hexdigest(),
        "runtime": "MediaPipe Tasks Vision Web 1.1.0, bundled non-SIMD WASM",
        "model_sha256": MODEL_SHA,
        "device_validation": "Windows/macOS extracted-file camera checks not yet recorded",
        "packages": packages}
    for platform in ("Windows", "macOS"):
        guide = args.output / f"READ_FIRST_{platform}.pdf"
        write_guide(guide, platform)
        target = args.output / f"GestureForge_Participant_{platform}.zip"
        with ZipFile(target, "w", compression=ZIP_DEFLATED, compresslevel=9) as archive:
            archive.writestr("START_HERE.html", html)
            archive.write(guide, "READ_FIRST.pdf")
            archive.writestr("THIRD_PARTY_NOTICES.txt", notices)
        with ZipFile(target) as archive:
            if archive.testzip() is not None:
                raise ValueError("Archive integrity check failed")
        packages.append({"file": target.name, "bytes": target.stat().st_size,
                         "sha256": sha256(target.read_bytes()).hexdigest()})
    (args.output / "verification.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
