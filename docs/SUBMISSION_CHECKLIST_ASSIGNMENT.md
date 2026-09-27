# Assignment Submission Checklist

Deadline: 3 October 2026.

Status: submission incomplete; documentation and software checks refreshed on 27 September 2026 against the repository and recorded evidence. Checked items establish only the stated scope, not submission readiness. Check off remaining gates only after evidence exists. [Next steps](ASSIGNMENT_NEXT_STEPS.md) gives the priority order; the [final-project checklist](SUBMISSION_CHECKLIST_FINAL.md) keeps November features and formal performance targets separate.

Commands below run from the repository root with the project environment active. The [README](../README.md) shows explicit `.venv` commands and Windows launchers.

## Build and Code

- [x] Source code is under `code`.
- [x] `python -m gestureforge` launches the prototype.
- [x] `python -m gestureforge.collect` works; real TRAIN and VALIDATION sessions completed.
- [x] `python -m gestureforge.evaluate --config experiments\prototype.json --output experiments\local\prototype-results.json` reproduces synthetic classifier comparison.
- [x] The selected multiplier-2.0 comparison is recorded in [PILOT_RESULTS.md](evidence/PILOT_RESULTS.md), with a reproduction command requiring the retained P01 manifest and feature sidecar. New collection is a new experiment; participant data and full outputs are absent from the source ZIP/GitHub.
- [x] Ruff, mypy and 60 tests passed in the recorded [27 September software verification](evidence/verification.json) for implemented assignment parts, including private archive validation.
- [x] Dependencies are pinned or documented with verified versions.
- [x] `requirements.lock` is included and matches the tested environment.
- [x] `.\scripts\setup.ps1` completed in a fresh source folder with a new environment on the development computer; see [SETUP_CHECK.md](evidence/SETUP_CHECK.md). Later source ZIP/launcher checks are in [WINDOWS_LAPTOP_CHECK.md](evidence/WINDOWS_LAPTOP_CHECK.md); neither is a physical second-computer test.
- [x] `scripts/check_environment.py` output is saved in [environment.json](evidence/environment.json); hardware/model observations are in [HARDWARE_CHECK.md](evidence/HARDWARE_CHECK.md).
- [x] `scripts/download_model.py` retrieves the expected MediaPipe model asset.
- [x] Native Windows interface screenshot captured and visually inspected at [prototype.png](images/prototype.png); camera stayed off. Automated offscreen startup/shutdown is a separate check.
- [x] `python -m gestureforge --dataset data\local\pilot\manifest.json --algorithm knn --multiplier 2 --camera 1` launches live control with the pilot dataset.
- [x] PREVIOUS and BOOKMARK are marked recognition preview only.
- [x] Two deliberate NEXT holds each advanced once in the [participant-observed smoke retest](evidence/PILOT_RESULTS.md#live-assignment-path); formal final-project hold testing remains planned.
- [x] Camera releases cleanly after closing; the next live session opened successfully.

## Evidence

- [x] Pilot consent is recorded for local numeric data; private tutor/marker submission permission granted on 26 September; the retention arrangement remains open.
- [ ] Record the retention period and private submission location for P01 artifacts; private tutor/marker permission does not authorise GitHub publication.
- [x] Pilot train and validation manifests exist locally, with distinct sessions and no shared trials.
- [x] Invalid detections are retained by the manifest/software path; the P01 scheduled pilot samples were all valid, so there are no real invalid P01 captures to cite.
- [x] kNN and SVM results are saved locally, preserving the initial baseline and corrected comparison.
- [x] Report includes real metrics and limitations.
- [x] Actual application screenshot shows the interface in manual mode; live recognition is established separately by the pilot event evidence and participant observation.
- [x] P02 reported successful ZIP use on another laptop with their own right-hand dataset and Codex assistance; see [P02_LAPTOP_TEST.md](evidence/P02_LAPTOP_TEST.md). This is qualitative, participant-reported evidence.
- [ ] Complete the [remaining P02 laptop checks](evidence/P02_LAPTOP_TEST.md#short-remaining-laptop-check) and [release acceptance record](WINDOWS_LAPTOP.md#6-physical-laptop-acceptance-record): pause/restart, camera release/reopen, disconnected-network use, guide-only installation, date/environment details and exact ZIP checksum/version. Assisted use and hosted CI do not close these gaps.

## Report

- [x] Problem and user workflow are drafted.
- [x] Requirements are numbered.
- [x] Architecture and contracts are described.
- [x] Technique investigation compares kNN and SVM.
- [x] At least three primary sources are discussed with limitations.
- [x] NASA lifecycle adaptation is described accurately.
- [x] Test plan covers assignment and planned final system.
- [x] AI assistance declaration draft exists.
- [x] Report, README, pilot/package evidence and checklists were reconciled against implemented code and recorded evidence on 27 September; this is not human approval or final-project verification.
- [x] Review PDF exported to [GestureForge_Assignment_Report.pdf](../output/pdf/GestureForge_Assignment_Report.pdf), including the recovered original planning and full implementation-plan prompts for this task. Other Codex conversation coverage remains unconfirmed.
- [ ] Final report human review is complete; regenerate the PDF after any content changes.
- [ ] Unit AI-use guidance is checked against the final declaration and [AI_PROMPTS.md](../AI_PROMPTS.md); confirm required transcript/appendix coverage, review actual AI use and remove private material.

## Administration

- [ ] Team registration and tutorial membership are confirmed.
- [ ] [Contribution record](CONTRIBUTIONS.md) is updated with real names, verified work and required identifiers/percentages; all members have reviewed the submission.
- [x] User confirmed GitHub and WhatsApp use on 27 September; the report names all four required tool categories.
- [ ] Actual team activity summaries and individual contributions are recorded; tool confirmation alone does not establish who performed each task.
- [x] Unchanged official [declaration template](submission/Group_Declaration_TO_COMPLETE.docx) is included for completion.
- [ ] Group declaration sheet is completed and signed by every member.
- [x] Pending questions are recorded in [TUTOR_REVIEW.md](TUTOR_REVIEW.md); tutor approval or reply is not yet recorded.
- [ ] Tutor questions about scope, marking weights, participant evidence, agile evidence and AI-use requirements are resolved and actual replies recorded.
- [x] `python scripts\board.py` has generated the local sprint board.
- [x] GitHub setup/progress is recorded in [GITHUB_SETUP.md](GITHUB_SETUP.md) and [AGILE.md](AGILE.md), with the [local sprint board](SPRINT_BOARD.html). These artifacts do not establish peer review or marker access to the private repository.
- [ ] Marker access to source/agile evidence is confirmed, or permitted exports are included so assessment does not depend on private GitHub links.
- [x] A source archive and SHA256 manifest exist under `releases`; [package instructions](../releases/README.md) describe regeneration. Historical install checks cover their dated snapshots only.
- [x] Source archive is treated as source and draft documentation only, not as the complete submission package.
- [ ] After final edits, regenerate the reviewed source ZIP, verify its checksum/contents, and tie the second-computer acceptance record to that exact package.
- [ ] Assemble and review the complete submission: reviewed report export, source/instructions, privately permitted participant evidence/results, accessible agile evidence, required AI-use material and signed declaration. A source ZIP alone does not reproduce the private P01 results.
- [ ] LMS upload is downloaded and checked.
