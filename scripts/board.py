"""Local sprint board backed by the same backlog used for GitHub issues."""

import argparse
import csv
from datetime import datetime, timezone
from html import escape
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BACKLOG = ROOT / "docs" / "backlog.csv"
STATUSES = ("Not started", "In progress", "Blocked", "Done", "Future")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--id", help="Backlog ID to update")
    parser.add_argument("--status", choices=STATUSES)
    parser.add_argument("--note", default="")
    args = parser.parse_args()
    with BACKLOG.open(encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        fields = list(reader.fieldnames or [])
        rows = list(reader)
    if args.id:
        if not args.status or not args.note:
            parser.error("Updates require --status and an evidence-based --note")
        matches = [row for row in rows if row["id"] == args.id]
        if len(matches) != 1:
            parser.error("Backlog ID not found or duplicated")
        before = matches[0]["status"]
        matches[0]["status"] = args.status
        matches[0]["notes"] = args.note
        temporary = BACKLOG.with_suffix(".tmp")
        with temporary.open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
        temporary.replace(BACKLOG)
        with (ROOT / "docs" / "sprint_events.jsonl").open("a", encoding="utf-8") as stream:
            stream.write(json.dumps({"time": datetime.now(timezone.utc).isoformat(),
                "id": args.id, "from": before, "to": args.status, "note": args.note,
                "actor": "Codex implementation session"}) + "\n")
    columns = []
    for status in STATUSES:
        cards = []
        for row in rows:
            if row["status"] != status:
                continue
            cards.append(f'<article><small>{escape(row["id"])} / {escape(row["sprint"])}</small>'
                f'<h3>{escape(row["title"])}</h3><p>{escape(row["acceptance_criteria"])}</p>'
                f'<p class="note">{escape(row["notes"])}</p>'
                f'<small>{escape(row["release"])} · {escape(row["evidence_path"])}</small></article>')
        columns.append(f'<section><h2>{status} <span>{len(cards)}</span></h2>{"".join(cards)}</section>')
    html = '''<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>GestureForge sprint board</title>
<style>body{margin:30px;font:15px system-ui;background:#101923;color:#edf2f6}header{max-width:900px}
main{display:grid;grid-template-columns:repeat(5,minmax(200px,1fr));gap:18px}h1{font-size:32px}
h2{font-size:18px}h3{margin:8px 0;font-size:16px}article{background:#213142;padding:16px;border-radius:10px;margin-bottom:12px}
small,.note{color:#b5c7d8}p{line-height:1.45}span{color:#6bd9b3}a{color:#6bd9b3}
@media(max-width:950px){main{grid-template-columns:repeat(2,1fr)}}
@media(max-width:520px){main{grid-template-columns:1fr}}</style>
<header><h1>GestureForge delivery board</h1><p>Assignment: 3 October 2026 · Final project: 7 November 2026</p>
<p>Code completion is separate from participant evidence and submission readiness. Blocked cards identify genuine external requirements.</p>
<p>Source: <a href="backlog.csv">backlog.csv</a>. Update using <code>python scripts/board.py --id ID --status STATUS --note EVIDENCE</code>.</p></header><main>'''
    target = ROOT / "docs" / "SPRINT_BOARD.html"
    target.write_text(html + "".join(columns) + "</main></html>", encoding="utf-8")
    print(f"Updated {target.name}; {len(rows)} tracked work items")


if __name__ == "__main__":
    main()
