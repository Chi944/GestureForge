# Release packages

The graded source contains the application, tests, guides, traceability and measured evidence. Reports, declaration, prompt and decision logs, participant samples, environments, working drafts and archived checklists stay out of GitHub and the source ZIP.

## Studio development handoff

For the current project work, run this from the reviewed project checkout:

```powershell
.\.venv\Scripts\python.exe scripts/package_release.py --project
```

This writes `releases/gestureforge-studio-source.zip` and a matching JSON manifest with archive checksum, source commit and working-tree state. It includes tracked Studio source, guides, tests and corporate assets; no participant data, profiles, local target paths, Word reports or environments. A dirty checkout is labelled as uncommitted work based on the reported commit. Commit reviewed files before creating a reproducible handoff.

Packaging stops if a tracked source file is missing and preserves the previous
ZIP and checksum receipt. Restore the missing file, or review and stage its
intentional removal, before packaging again; files are never silently omitted.

The Studio ZIP is a source handoff; creating it does not establish release
acceptance. On another Windows laptop, extract it into a fresh folder, open
`gestureforge`, run `setup.cmd` with internet for the initial dependencies/model
download, then double-click `run-studio.cmd`. Python 3.11 is required. Rebind local
targets and follow the [manual walkthrough](../docs/project/DEMO_SCENARIO.md#manual-walkthrough-available-now).

Keep private profiles, datasets and `.local` evidence outside the replacement
folder unless intentionally importing them through the app. Git users update
their checkout; ZIP users compare the package manifest's source commit and hash
with the reviewed handoff. Rebuild only when a new package is needed, and identify
the exact package in device receipts. Do not reuse results from an unidentified
older ZIP. Participant browser collection kits are separate, require no Python,
and are not replaced by a Studio handoff.

Test offline use after setup separately. The Mac `.command` launcher requires
the [Apple Silicon setup](../README.md#apple-silicon-mac); full native verification
is outstanding and Windows external shortcuts are unavailable there. Do not
combine `--project` with `--include-pilot`.

## Current release gates

Follow [accepted progress](../docs/project/PROGRESS.md) and the
[team handoff](../docs/project/TEAM_GUIDE.md) before assembling the final delivery.
The 26 October run met continuous-duration and close/reopen substeps but exceeded
the responsiveness limits; see the [endurance review](../docs/project/GF_P23_ENDURANCE_REVIEW_2026_10_26.md).
Laptop-B receipts have been received and checked. Remaining native, installation
and offline coverage must be reconciled; neither a successful archive build nor
the monitor's countdown completes GF-P23.

After release verification, match the genuine demo video and guide to that build,
then reconcile the report, presentation and declaration. Keep Word deliverables,
prompt/decision logs and permitted private evidence outside the public source
archive. GF-P27 covers the final source/assets, required documents, guide, slides,
video and permitted reproduction data, followed by checking the actual LMS
download. No new package is created by this documentation refresh.

<details>
<summary>First-release packages and instructions (historical reference)</summary>

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

</details>
