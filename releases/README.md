# Release packages

The graded source contains the application, tests, guides, Markdown prompt and decision logs, traceability, measured evidence and unsigned declaration template. Participant samples, environments, working drafts and archived checklists stay out of GitHub and the source ZIP.

After staging only reviewed submission files:

```powershell
.\.venv\Scripts\python.exe scripts/package_release.py
.\.venv\Scripts\python.exe scripts/package_release.py --include-pilot
```

| Package | Contents | Use |
| --- | --- | --- |
| `gestureforge-assignment-source.zip` | Tracked submission files; no participant dataset | Source transfer and new personal enrolment |
| `gestureforge-assignment-private-marker.zip` | Source plus authorised P01 numeric manifest and NPZ sidecar | Private tutor or marker reproduction |
| Matching JSON manifest | SHA256, file count and creation time | Verify the exact transferred archive |

The private archive must not be attached to GitHub. P01 private marker sharing was authorised; the retention arrangement remains pending. No raw video or images are included. The downloaded landmark model is verified during online setup rather than redistributed in the archive. Create a new environment on each laptop; do not copy `.venv`.

Submit the three local Word files from `docs/submission/` separately: `GestureForge_Technical_Report.docx`, `Prompt_Log.docx` and `Decision_Log.docx`. They are intentionally excluded from GitHub and both code ZIPs. The official form is an **unsigned template**, not a completed declaration. Complete report review, team details and signatures before submitting. Local package verification does not verify an LMS upload or second-laptop guide-only operation.

To reproduce the saved P01 comparison after extracting the private marker package and running `setup.cmd`:

```powershell
.\.venv\Scripts\python.exe -m gestureforge.evaluate --config experiments/pilot.json --output experiments/local/reproduced-pilot.json
```

Consult the [results and configuration history](../docs/evidence/RESULTS.md) for the expected scores and limits of each model version. Live recognition on another person's hand needs separate enrolment. Keep the retained P01 samples unchanged.

Before upload, verify the exact archive on the second computer using the [Windows guide](../docs/WINDOWS_LAPTOP.md). After upload, download and check the actual LMS files. Required personal details belong in the local report and declaration.
