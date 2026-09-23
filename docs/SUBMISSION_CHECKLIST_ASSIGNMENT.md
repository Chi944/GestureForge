# Assignment Submission Checklist

Deadline: 3 October 2026.

Status: draft. Check off only after evidence exists.

## Build and Code

- [x] Source code is under `code`.
- [x] `python -m gestureforge` launches the prototype.
- [x] `python -m gestureforge.collect` works; real TRAIN and VALIDATION sessions completed.
- [x] `python -m gestureforge.evaluate --config experiments\prototype.json --output experiments\local\prototype-results.json` reproduces synthetic classifier comparison.
- [x] `python -m gestureforge.evaluate --config experiments/pilot.json` reproduces participant classifier comparison after consented collection.
- [x] `python -m pytest` passes for implemented assignment parts.
- [x] Dependencies are pinned or documented with verified versions.
- [x] `requirements.lock` is included and matches the tested environment.
- [x] `.\scripts\setup.ps1` completes in a fresh source folder with a new environment on this computer; see `evidence/SETUP_CHECK.md`.
- [x] `scripts/check_environment.py` output is saved.
- [x] `scripts/download_model.py` retrieves the expected MediaPipe model asset.
- [x] Native Windows Qt smoke screenshot captured and visually inspected at `docs/images/prototype.png`; camera stayed off.
- [x] `python -m gestureforge --dataset data\local\pilot\manifest.json --algorithm knn --multiplier 2 --camera 1` launches live control with the pilot dataset.
- [x] PREVIOUS and BOOKMARK are marked recognition preview only.
- [x] NEXT advances once per deliberate hold in the participant-observed smoke retest; formal final-project hold testing remains planned.
- [x] Camera releases cleanly after closing; the next live session opened successfully.

## Evidence

- [x] Pilot consent is recorded for local numeric data; submission permission and retention agreement remain open.
- [x] Pilot train and validation manifests exist locally, with distinct sessions and no shared trials.
- [x] Invalid detections are retained by the manifest/software path; the P01 scheduled pilot samples were all valid, so there are no real invalid P01 captures to cite.
- [x] kNN and SVM results are saved locally, preserving the initial baseline and corrected comparison.
- [x] Report includes real metrics and limitations.
- [x] Actual application screenshot shows the interface in manual mode; live recognition is established separately by the pilot event evidence and participant observation.
- [ ] Second Windows computer installation is tested.

## Report

- [x] Problem and user workflow are drafted.
- [x] Requirements are numbered.
- [x] Architecture and contracts are described.
- [x] Technique investigation compares kNN and SVM.
- [x] At least three primary sources are discussed with limitations.
- [x] NASA lifecycle adaptation is described accurately.
- [x] Test plan covers assignment and planned final system.
- [x] AI assistance declaration draft exists.
- [x] Claims are reconciled against implemented code and current evidence.
- [ ] Final report export and human review are complete.
- [ ] Unit AI-use guidance is checked against the final declaration.

## Administration

- [ ] Team registration and tutorial membership are confirmed.
- [ ] Contribution record is updated with real names and work.
- [ ] Group declaration sheet is signed.
- [x] Pending tutor questions are recorded; tutor approval or reply is not yet recorded.
- [x] `python scripts\board.py` has generated the local sprint board.
- [x] GitHub Issues/Projects evidence is included if the private repo setup is complete.
- [x] Release archive is created under `releases`.
- [x] Source archive is treated as source only, not as the full submission package.
- [ ] LMS upload is downloaded and checked.
