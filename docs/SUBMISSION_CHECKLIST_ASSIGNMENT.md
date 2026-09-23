# Assignment Submission Checklist

Deadline: 3 October 2026.

Status: draft. Check off only after evidence exists.

## Build and Code

- [x] Source code is under `code`.
- [x] `python -m gestureforge` launches the prototype.
- [ ] `python -m gestureforge.collect` works or the report clearly states the implemented collection method.
- [x] `python -m gestureforge.evaluate --config experiments\prototype.json --output experiments\local\prototype-results.json` reproduces synthetic classifier comparison.
- [ ] `python -m gestureforge.evaluate --config <human-pilot-config>` reproduces participant classifier comparison after consented collection.
- [x] `python -m pytest` passes for implemented assignment parts.
- [x] Dependencies are pinned or documented with verified versions.
- [x] `requirements.lock` is included and matches the tested environment.
- [ ] `.\scripts\setup.ps1` completes on a clean checkout or release test folder.
- [x] `scripts/check_environment.py` output is saved.
- [x] `scripts/download_model.py` retrieves the expected MediaPipe model asset.
- [ ] `python -m gestureforge --smoke-test --screenshot docs\evidence\app-smoke.png` starts the Qt app.
- [ ] `python -m gestureforge --dataset data\local\pilot\manifest.json --algorithm knn` launches live control after human data exists.
- [x] PREVIOUS and BOOKMARK are marked recognition preview only.
- [ ] NEXT advances the fixed deck once per deliberate hold.
- [ ] Camera releases cleanly after closing.

## Evidence

- [ ] Pilot consent is recorded.
- [ ] Pilot train and validation manifests exist.
- [ ] Invalid detections are retained.
- [ ] kNN and SVM results are saved.
- [ ] Report includes real metrics and limitations.
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
