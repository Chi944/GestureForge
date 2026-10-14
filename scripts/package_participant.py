"""Build offline collection-only kits. Build-time PDF tooling is not shipped."""

from __future__ import annotations

import argparse
import base64
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gestureforge.paired_evaluate import browser_test_ticket  # noqa: E402

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


def _replace_once(text: str, old: str, new: str, label: str) -> str:
    if text.count(old) != 1:
        raise ValueError(f"Expected one {label}")
    return text.replace(old, new)


def _ticket_script(ticket: dict[str, object]) -> str:
    payload = json.dumps(ticket, separators=(",", ":"), sort_keys=True).replace("<", "\\u003c")
    return f'<script type="application/json" id="testTicket">{payload}</script>'


def _apply_frozen_test_html(html: str, ticket: dict[str, object]) -> str:
    target = str(ticket["target_participant"])
    html = _replace_once(
        html,
        '<p class="muted">Collects numeric hand landmarks only. It does not save photos, video or audio.</p>',
        '<p class="muted">Fresh TEST session for the assigned participant only. '
        'It collects numeric hand landmarks only and does not save photos, video or audio.</p>',
        "top collector intro",
    )
    html = _replace_once(
        html,
        '<label for="participantId">Pseudonym</label>\n'
        '        <input id="participantId" placeholder="Example: P04" autocomplete="off">',
        '<label for="participantId">TEST target pseudonym</label>\n'
        f'        <input id="participantId" value="{target}" readonly autocomplete="off">',
        "participant pseudonym field",
    )
    html = _replace_once(
        html,
        '<label for="trainConditions">TRAIN conditions - fill in before TRAIN</label>\n'
        '        <textarea id="trainConditions" placeholder="Lighting, background, seated/standing, approximate hand distance."></textarea>',
        '<label for="trainConditions">TEST conditions - fill in before TEST</label>\n'
        '        <textarea id="trainConditions" placeholder="Lighting, background, seated/standing, approximate hand distance."></textarea>',
        "TRAIN conditions field",
    )
    html = _replace_once(
        html,
        '<label for="validationConditions">VALIDATION conditions - fill in after your break</label>\n'
        '        <textarea id="validationConditions" placeholder="Record any changed lighting, camera or background conditions."></textarea>',
        '        <textarea id="validationConditions" hidden></textarea>',
        "VALIDATION conditions field",
    )
    html = _replace_once(html, '<p id="progressText">0 / 104 trials complete</p>',
                         '<p id="progressText">0 / 48 trials complete</p>', "progress total")
    html = _replace_once(
        html,
        '<option value="train">TRAIN - 48 trials, about 5-6 minutes</option>\n'
        '          <option value="validation">VALIDATION - 48 trials, about 5-6 minutes</option>\n'
        '          <option value="validation_negative">UNKNOWN - 8 trials, about 1 minute</option>',
        '<option value="test">TEST - 48 trials, about 5-6 minutes</option>',
        "session options",
    )
    html = _replace_once(
        html,
        "Allow 15-20 minutes plus a break for all three sections, including setup and saving. Each trial: 3 seconds to get ready, 2 seconds to hold, then 1 second to relax. Keep this tab visible; use Pause before leaving it.",
        "Allow 5-6 minutes for the TEST session, plus setup and saving. Each trial: 3 seconds to get ready, 2 seconds to hold, then 1 second to relax. Keep this tab visible; use Pause before leaving it.",
        "session timing text",
    )
    html = _replace_once(
        html,
        '<p><strong>Unknown trials</strong></p>\n'
        '        <p class="muted">Follow the shown prompt and avoid the enrolled poses.</p>',
        '<p><strong>TEST session</strong></p>\n'
        '        <p class="muted">Record only the shown TEST poses for this assigned kit.</p>',
        "unknown trial instructions",
    )
    entrypoint = '<script type="module" src="collector.mjs"></script>'
    return _replace_once(html, entrypoint, f"{_ticket_script(ticket)}\n{entrypoint}", "collector entrypoint")


def assemble_html(assets: Path, model: Path, frozen: Path | None = None) -> str:
    html = (ROOT / "participant/collector.html").read_text(encoding="utf-8")
    module = (ROOT / "participant/collector.mjs").read_text(encoding="utf-8")
    if "</script" in module.lower():
        raise ValueError("Module contains an inline script terminator")
    if frozen is not None:
        html = _apply_frozen_test_html(html, browser_test_ticket(frozen))
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


def write_guide(path: Path, platform: str, frozen: Path | None = None) -> None:
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

    test_ticket = browser_test_ticket(frozen) if frozen is not None else None
    if test_ticket is not None:
        target = str(test_ticket["target_participant"])
        p("GestureForge", "Title")
        p(f"TEST recording guide | {platform}", "Heading1")
        p(f"This kit is assigned to pseudonym <b>{target}</b>. Use it for one fresh "
          "48-trial TEST session only. A webcam, your right hand and an existing browser "
          "are enough; nothing is uploaded automatically.", "Lead")
        p("Read the consent text in the recorder and tick the permission boxes only if you agree. "
          "Record today's TEST conditions before starting: lighting, background, sitting or "
          "standing, and approximate hand-to-camera distance. Do not import old development data "
          "or repeat earlier TRAIN/VALIDATION recordings.")
        step("1  Save, unzip and open", (
            "Save the Windows ZIP from the email. In Downloads, right-click the ZIP, choose "
            "<b>Extract All</b>, then <b>Extract</b>. Open the new folder and double-click "
            "<b>START_HERE.html</b>."
            if platform == "Windows" else
            "Save the macOS ZIP from the email. In Finder, open Downloads and double-click the ZIP. "
            "Open the folder that appears and double-click <b>START_HERE.html</b>."
        ) + " Keep this same extracted kit for backup or resume. Do not run from inside the ZIP.")
        step("2  Check the camera, then start TEST",
             "Click <b>Start Camera</b> and allow camera access. Keep your entire right hand visible, "
             "palm towards the camera, with light on your hand. The preview is mirrored. Check for "
             "<b>Right hand detected</b>, then click <b>Start Selected Session</b>.")
        rows = [[Paragraph("On screen", styles["BodyText"]), Paragraph("Use your RIGHT hand", styles["BodyText"])]]
        for label, pose in [
            ("NEUTRAL", "Open palm towards the camera; fingers extended."),
            ("NEXT", "Closed fist towards the camera."),
            ("PREVIOUS", "Thumb pointing up; other fingers folded."),
            ("BOOKMARK", "Index and middle fingers extended; other fingers folded."),
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
        p("Plan about <b>5-6 minutes</b> once the detector is ready. Each trial gives 3 seconds "
          "to prepare, about 2 seconds to hold the pose, then 1 second to relax. Complete "
          "<b>48 / 48 trials</b> if possible.")
        p("Keep the computer awake and keep this tab visible. If you click <b>Pause</b> or switch "
          "tabs and the camera stops, click <b>Start Camera</b>, wait for <b>Right hand detected</b>, "
          "then click <b>Start Selected Session</b> to continue.")
        step("3  Save and return the ZIP",
             f"Click <b>Export Return ZIP</b> at the end, or after pausing if interrupted. Send "
             f"<b>EMAIL_THIS_{target}_test.zip</b>. If the file is marked "
             f"<b>EMAIL_THIS_{target}_PARTIAL_test.zip</b>, keep it and report the interruption "
             "instead of deleting trials or repeating the session.")
        p("To resume, open <b>START_HERE.html</b> from this same TEST kit and recover the newest "
          "PARTIAL return ZIP. Do not unzip the return ZIP, clear the draft, delete mistakes, "
          "or start again unless the team asks.")

        def test_footer(canvas, doc):
            canvas.setFont("Helvetica", 8)
            canvas.setFillColor(colors.HexColor("#506070"))
            canvas.drawString(42, 24, f"GestureForge | TEST collection | {target}")
            canvas.drawRightString(553, 24, str(doc.page))

        SimpleDocTemplate(str(path), pagesize=(595, 842), leftMargin=42, rightMargin=42,
                          topMargin=36, bottomMargin=42, title=f"GestureForge {platform} TEST guide",
                          author="GestureForge team").build(
                              content, onFirstPage=test_footer, onLaterPages=test_footer)
        return

    p("GestureForge", "Title")
    p(f"Participant recording guide | {platform}", "Heading1")
    p("A webcam, your right hand and an existing browser. No Python, coding tools, "
      "account or installation is needed. The hand detector is included in this download.", "Lead")
    p("<b>This is a data-collection kit, not the full GestureForge Studio app.</b> "
      "It records numeric hand positions and timing, not photographs, video or sound. "
      "Nothing is uploaded automatically. The included detector does not need an internet connection.")
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
         "gave you, not your name. Read the consent text and tick the permission boxes "
         "only if you agree. Your numeric data is for the team and private marker only; "
         "the team will delete it after marking and appeals finish. Contact Deston or "
         "Hau Jie if you have questions before agreeing.")
    p("Fill in <b>TRAIN conditions</b> for your surroundings now: lighting, background, "
      "sitting or standing, and approximate hand-to-camera distance. Describe what is true "
      "for you. <b>Leave VALIDATION conditions until after your break.</b> You do not need "
      "both sets of notes to start TRAIN.")
    step("4  Check the camera, then start TRAIN", "Click <b>Start Camera</b> and select <b>Allow</b> "
         "if the browser asks. "
         "Wait for the hand detector to finish loading. Keep your entire right hand visible, "
         "palm towards the camera, with light on your hand. The preview is mirrored. Check for "
         "<b>Right hand detected</b>. Select <b>TRAIN</b>, then click <b>Start Selected Session</b>.")
    p("<b>If Setup required appears:</b> read the message. The page takes you to the missing "
      "detail. Fill in that field or review the consent item, then click <b>Start Selected "
      "Session</b> again. Camera video alone does not mean a trial has started. You do not "
      "need to restart a working camera.")
    content.append(PageBreak())
    p("Record the three sections", "Heading1")
    p("Plan about 15-20 minutes plus a break. Starting a session takes you to the large "
      "instruction above the camera preview. Follow that instruction and countdown.", "Lead")
    p("Get ready during the <b>3-second countdown</b>, hold the requested pose still for "
      "about <b>2 seconds</b>, then relax for <b>1 second</b>. The trials continue automatically. "
      "The completed count advances after each trial.")
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
    step("5  TRAIN, break, VALIDATION, then UNKNOWN",
         "<b>TRAIN:</b> finish 48 trials (12 per pose; about 5-6 minutes). Export a backup ZIP, "
         "click <b>Pause</b>, then take a break.<br/><br/>"
         "<b>VALIDATION:</b> enter <b>VALIDATION conditions</b> for the current lighting, "
         "background, sitting/standing position and hand distance. The recorder selects "
         "<b>VALIDATION</b> next. Click <b>Start Camera</b>, wait for hand detection, then "
         "<b>Start Selected Session</b> for 48 trials (about 5-6 minutes). Export another backup.<br/><br/>"
         "<b>UNKNOWN:</b> the recorder selects <b>UNKNOWN</b> next. Click <b>Start Selected "
         "Session</b> for its 8 different non-command trials "
         "(about 1 minute). These use your VALIDATION condition notes; keep those conditions "
         "the same. If paused, click <b>Start Camera</b> first. Nothing records until you start it.")
    p("<b>While recording:</b> Start and Export are deliberately unavailable so they cannot "
      "interrupt a trial. <b>Pause</b> remains available. Keep this tab visible; pause before "
      "leaving it. To save during a session, pause first and wait for recording to stop.")
    p("This kit collects <b>development data only</b>. It does not collect final TEST data. "
      "The team will contact you separately after the evaluation settings are frozen.")
    content.append(PageBreak())
    p("Save your data and send it back", "Heading1")
    p("Send the ZIP downloaded by the recorder. You do not need to zip any folders yourself.", "Lead")
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
    step("Resume a PARTIAL ZIP - do not repeat TRAIN",
         "Open <b>START_HERE.html</b> from the newest kit. Under <b>Recover from a previous "
         "return ZIP</b>, choose your original <b>EMAIL_THIS_...PARTIAL_development.zip</b>. "
         "Keep that backup; do not unzip it or clear your draft.<br/>"
         "The recorder selects the first unfinished section. With 48 TRAIN trials saved, "
         "this is <b>VALIDATION</b>. After a break, fill in its actual condition notes, click "
         "<b>Start Camera</b>, wait for hand detection, then <b>Start Selected Session</b>. "
         "Finish VALIDATION and UNKNOWN, then export again. A complete return shows "
         "<b>104 / 104 trials</b> and has no <b>PARTIAL</b> in its filename.")
    p("After the team confirms receipt, <b>Clear Local Draft</b> removes this browser's saved "
      "recording. Keep your emailed ZIP until receipt is confirmed.")
    p("<b>Pause or switching tabs stops the camera.</b> To resume, click <b>Start Camera</b>, "
      "then <b>Start Selected Session</b>. Reopening the same file can also recover a saved "
      "draft. Completed trials are skipped; interrupted slots remain invalid. Do not edit out mistakes.")
    step("If your hand is not detected", "Pause first. Put light on your whole right palm, "
         "keep it unobstructed and move it slightly farther from the camera so all fingers "
         "and the wrist fit in the picture. Face your palm towards the camera, then click "
         "<b>Start Camera</b> to check again. If the message "
         "still does not say <b>Right hand detected</b>, contact the team before continuing.")
    p("<b>If the camera or detector cannot start:</b> close other camera apps and check the "
      "visible browser permission message. Send the exact error and your browser/OS version "
      "to the team if it persists. Do not change browser security settings.")
    p("<b>Coordinator check:</b> verify the extracted kit on both Windows and macOS, including "
      "camera permission, a first trial, pause/recovery and a saved return ZIP. Browser camera "
      "policies vary. Software checks alone do not establish that every laptop works, and "
      "finishing a recording does not establish recognition accuracy.")

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
    parser.add_argument("--frozen", type=Path, help="Frozen paired TEST config for locked TEST kits")
    parser.add_argument("--output", type=Path, default=ROOT / ".local/participant-deliverables")
    args = parser.parse_args()
    test_ticket = browser_test_ticket(args.frozen) if args.frozen is not None else None
    html = assemble_html(args.assets, args.model, args.frozen)
    args.output.mkdir(parents=True, exist_ok=True)
    notices = (ROOT / "participant/THIRD_PARTY_NOTICES.txt").read_bytes()
    packages: list[dict[str, str | int]] = []
    report = {"source_commit": subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "source_dirty": bool(subprocess.check_output(["git", "status", "--porcelain"], cwd=ROOT)),
        "collector_sha256": sha256(html.encode()).hexdigest(),
        "runtime": "MediaPipe Tasks Vision Web 1.1.0, bundled non-SIMD WASM",
        "model_sha256": MODEL_SHA,
        "collection_mode": "test" if test_ticket else "development",
        "device_validation": "Windows/macOS extracted-file camera checks not yet recorded",
        "packages": packages}
    if test_ticket:
        report["test_ticket"] = test_ticket
    for platform in ("Windows", "macOS"):
        guide = args.output / f"READ_FIRST_{platform}.pdf"
        write_guide(guide, platform, args.frozen)
        target = (
            args.output / f"GestureForge_{test_ticket['target_participant']}_TEST_{platform}.zip"
            if test_ticket else args.output / f"GestureForge_Participant_{platform}.zip"
        )
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
