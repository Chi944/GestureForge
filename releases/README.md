# Release packages

Run `python scripts/package_release.py` after staging the reviewed source. It creates a source archive and SHA256 manifest here. Environments and private participant data are excluded.

This source archive is not a complete assignment submission. Add the reviewed report, permitted pilot data/results, and signed declaration only after the submission checklist is complete. Verify the final submitted package on the second computer.

## Private marker archive

The user authorised private tutor/marker inclusion of P01 numeric data on 26 September 2026. From the project root, use the project environment:

```powershell
.\.venv\Scripts\python.exe scripts/package_release.py --include-pilot
```

This creates `gestureforge-assignment-private-marker.zip` and its SHA256 JSON companion. It includes tracked source/documentation plus the validated P01 manifest and its numeric NPZ sidecar. It excludes raw images, video, local event logs, environments and downloaded model assets. Keep this ZIP private; do not attach it to GitHub. The default source ZIP continues to exclude participant data.

The marker can extract it, run `setup.cmd` while online, then reproduce the pilot comparison:

```powershell
.\.venv\Scripts\python.exe -m gestureforge.evaluate --config experiments/pilot.json --output experiments/local/reproduced-pilot.json
```

Expected selected-setting development macro-F1: approximately 0.9686 for both classifiers. Reproduction uses P01's saved samples; a different user's live hand needs separate enrolment. Do not overwrite the retained P01 dataset with new collection. See `docs/evidence/PILOT_RESULTS.md` for limitations and `docs/WINDOWS_LAPTOP.md` for setup and new-enrolment instructions.

Both archives are preparation artifacts until the report is reviewed and the signed declaration and other open submission gates are completed. The private archive contains the draft PDF when it has been staged. Agree and record retention before submission; sharing permission does not establish a retention period.
