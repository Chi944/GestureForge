# GestureForge

GestureForge is a Python 3.11 Windows desktop prototype for recognising a small personal set of webcam hand gestures and controlling a card viewer.

The assignment release is deliberately scoped: recognise NEXT, PREVIOUS, BOOKMARK, and NEUTRAL, but execute only NEXT in the viewer. PREVIOUS and BOOKMARK are preview-only until the final project release.

## Current Status

The software prototype is ready for pilot preparation: documentation, contracts, package metadata, helper scripts, assets, core modules, command entry points, tests, lint, type checking, GUI smoke, and synthetic evaluation evidence are in place. Live camera control, participant data, second-machine verification, and signed submission materials remain pending.

## Setup

From this folder:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.lock
python -m pip install --no-deps -e .
```

For exact pinned package versions, see `requirements.lock`.

## Environment Checks

```powershell
.\scripts\setup.ps1
python scripts\check_environment.py
python scripts\download_model.py
python scripts\check_environment.py --camera
```

## Commands

```powershell
python -m gestureforge
python -m gestureforge --smoke-test --screenshot docs\evidence\app-smoke.png
python -m gestureforge --dataset data\local\pilot\manifest.json --algorithm knn
python -m gestureforge.collect --split train --participant P01 --hand Right --setup "desk lighting, plain background" --consent --output data/local/pilot
python -m gestureforge.evaluate --config experiments\prototype.json --output experiments\local\prototype-results.json
python -m gestureforge.fixtures data\local\synthetic
python scripts\board.py
python scripts\package_release.py
python -m pytest
```

Do not treat live camera control, participant data, or second-machine operation as verified until evidence is recorded.

Current software verification is recorded in `docs\evidence\verification.json`; fresh-environment source archive results are in `docs\evidence\clean-install-verification.json`.

`scripts\package_release.py` creates a tracked-source archive only. It is not the complete assignment submission until participant results, the report, permitted evidence, and signed declaration are added through the submission process.

## Key Documentation

- `docs/BUILD_PLAN.md`
- `docs/ASSIGNMENT_REPORT.md`
- `docs/TEST_PLAN.md`
- `docs/USER_GUIDE.md`
- `docs/AGILE.md`
- `docs/backlog.csv`

## Scope Guard

Assignment prototype:

- Guided collection.
- Feature extraction.
- kNN and SVM comparison.
- Rejection.
- Live preview.
- Fixed deck.
- Real NEXT action only.

Final project extension:

- In-app enrolment and practice.
- Multiple local profiles.
- PREVIOUS and BOOKMARK execution.
- JSON decks.
- Saved state and bookmarks.
- Held-out evaluation and demo video.
