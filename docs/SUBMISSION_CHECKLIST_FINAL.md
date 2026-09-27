# Final Project Submission Checklist

Deadline: 7 November 2026.

Status: future checklist. These November features and formal evaluation gates remain open; they do not expand the [assignment submission checklist](SUBMISSION_CHECKLIST_ASSIGNMENT.md). [P01 development validation and live smoke checks](evidence/PILOT_RESULTS.md), [P02 qualitative assisted use](evidence/P02_LAPTOP_TEST.md) and [same-computer ZIP verification](evidence/WINDOWS_LAPTOP_CHECK.md) do not satisfy the final held-out, full-system or complete physical-laptop acceptance requirements below.

## System Features

- [ ] In-app enrolment works.
- [ ] Practice mode works and cannot dispatch commands.
- [ ] Profiles can be created, reloaded, and deleted.
- [ ] NEXT executes safely.
- [ ] PREVIOUS executes safely.
- [ ] BOOKMARK executes safely and idempotently.
- [ ] User-selected JSON decks load after validation; the assignment's fixed bundled JSON deck does not complete this feature.
- [ ] Malformed decks show clear errors.
- [ ] Deck position and bookmarks reload.
- [ ] Profile and model switching invalidate pending actions.
- [ ] Camera failure recovery is clear.

## Evaluation

- [ ] Two participants consent.
- [ ] Train, validation, and test sessions are collected for both participants.
- [ ] Final configuration is frozen before test results are opened.
- [ ] Macro-F1, precision, recall, and confusion matrix are reported per participant.
- [ ] UNKNOWN predictions are included.
- [ ] Twenty five-second command holds per profile show zero duplicate actions.
- [ ] Ten minutes of non-command activity per profile is measured.
- [ ] Latency is measured from annotated stable-pose onset.
- [ ] Fit and search time are reported.
- [ ] Thirty-minute stability run is recorded.

## Tests and Release

- [ ] Every subsystem has executed tests.
- [ ] Second Windows computer release test passes.
- [ ] Offline operation after setup is checked.
- [ ] Missing camera and missing asset cases are tested.
- [ ] User guide is complete.
- [ ] Developer guide or report instructions are complete.
- [ ] Demo video exists.
- [ ] Slides exist.
- [ ] Ten-minute presentation is rehearsed.

## Administration

- [ ] Contribution record is complete.
- [ ] AI-use appendix is complete and reviewed.
- [ ] Signed declaration is included if required.
- [ ] LMS upload is downloaded and checked.
