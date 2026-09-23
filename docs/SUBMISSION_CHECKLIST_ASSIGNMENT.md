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
- [ ] `.\scripts\setup.ps1` completes on a clean checkout or release test folder.
- [x] `scripts/check_environment.py` output is saved.
- [x] `scripts/download_model.py` retrieves the expected MediaPipe model asset.
- [ ] `python -m gestureforge --smoke-test --screenshot docs\evidence\app-smoke.png` starts the Qt app.
- [x] `python -m gestureforge --dataset data\local\pilot\manifest.json --algorithm knn --multiplier 2 --camera 1` launches live control with the pilot dataset.
- [x] PREVIOUS and BOOKMARK are marked recognition preview only.
- [x] NEXT advances once per deliberate hold in the participant-observed smoke retest; formal final-system hold testing remains planned.
- [x] Camera releases cleanly after closing; the next live session opened successfully.

## Evidence

- [x] Pilot consent is recorded for local numeric data; submission permission and retention agreement remain open.
- [x] Pilot train and validation manifests exist locally, with distinct sessions and no shared trials.
- [ ] Invalid detections are retained.
- [x] kNN and SVM results are saved locally, preserving the initial baseline and corrected comparison.
- [x] Report includes real metrics and limitations.
- [ ] Screenshot or recording shows the working prototype.
- [ ] Second Windows computer installation is tested.

## Report

- [ ] Problem and user workflow are explained.
- [ ] Requirements are numbered.
- [ ] Architecture and contracts are described.
- [ ] Technique investigation compares kNN and SVM.
- [ ] At least three primary sources are discussed with limitations.
- [ ] NASA lifecycle adaptation is described accurately.
- [ ] Test plan covers assignment and planned final system.
- [ ] AI assistance is declared accurately.
- [ ] Claims match implemented code and real evidence.

## Administration

- [ ] Team registration and tutorial membership are confirmed.
- [ ] Contribution record is updated with real names and work.
- [ ] Group declaration sheet is signed.
- [ ] Tutor feedback or pending tutor questions are recorded.
- [x] `python scripts\board.py` has generated the local sprint board.
- [x] GitHub Issues/Projects evidence is included if the private repo setup is complete.
- [x] Release archive is created under `releases`.
- [x] Source archive is treated as source only, not as the full submission package.
- [ ] LMS upload is downloaded and checked.
