# Release packages

The graded source contains the application, tests, guides, traceability and measured evidence. Reports, declaration, prompt and decision logs, participant samples, environments, working drafts and archived checklists stay out of GitHub and the source ZIP.

## Studio development handoff

For the current project work, run this from the reviewed project checkout:

```powershell
.\.venv\Scripts\python.exe scripts/package_release.py --project
```

This writes `releases/gestureforge-studio-source.zip` and a matching JSON manifest with archive checksum, source commit and working-tree state. It includes tracked Studio source, guides, tests and corporate assets; no participant data, profiles, local target paths, Word reports or environments. A dirty checkout is labelled as uncommitted work based on the reported commit. Commit reviewed files before creating a reproducible handoff.

The Studio ZIP is a development source handoff, not final release acceptance. It does not replace either assignment archive. On another Windows laptop, extract it, open `gestureforge`, run `setup.cmd` with internet for the initial dependencies/model download, then `run.cmd --studio`. Rebind local targets on that machine and follow the [manual walkthrough](../docs/project/DEMO_SCENARIO.md#manual-walkthrough-available-now). Test offline use after setup separately. macOS uses the [Apple Silicon setup](../README.md#apple-silicon-mac); Windows external shortcuts remain unsupported there. Do not combine `--project` with `--include-pilot`.

## Retained assignment packages

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

The private archive must not be attached to GitHub. P01 private marker sharing was authorised. On 29 September the participant requested retention without a scheduled deletion date; the existing local/private marker access restriction still applies. No raw video or images are included. The downloaded landmark model is verified during online setup rather than redistributed in the archive. Create a new environment on each laptop; do not copy `.venv`.

Submit the reviewed local Word files from the assignment's separate `submission/` folder: `GestureForge_TechnicalReport_Updated.docx`, `Prompt_Log.docx`, `Decision_Log.docx` and `groupDeclarationSheet.docx`. These are excluded from GitHub and both code ZIPs. The prompt and decision logs remain unchanged by the current refresh; check their coverage and obtain tutor acceptance for supplying prompts separately because the brief requests them in the report. Local package verification does not verify an LMS upload or second-laptop guide-only operation.

To reproduce the saved P01 comparison after extracting the private marker package and running `setup.cmd`:

```powershell
.\.venv\Scripts\python.exe -m gestureforge.evaluate --config experiments/pilot-rejection.json --output experiments/local/reproduced-pilot-v3.json
```

Consult the [results and configuration history](../docs/evidence/RESULTS.md) for the expected scores and limits of each model version. Live recognition on another person's hand needs separate enrolment. Keep the retained P01 samples unchanged.

Before upload, verify the exact archive on the second computer using the [Windows guide](../docs/WINDOWS_LAPTOP.md). After upload, download and check the actual LMS files. Required personal details belong in the local report and declaration.
