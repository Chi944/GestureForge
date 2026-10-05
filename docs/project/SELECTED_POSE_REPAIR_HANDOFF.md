# GF-P12 selected-pose TRAIN repair

Component owner: Hau Jie. Host integration/review: Deston. 5 October 2026.

## Behavior

After reviewing a diagnostic, choose one positive label from an existing saved
personal profile, including NEUTRAL. `PoseRepairWidget` collects only that label
using the existing EnrolmentSession timings, consent and capture handshake.
The source profile fixes participant, hand, vocabulary and pose descriptions.
The operator supplies diagnostic notes, conditions and 2–12 trials. No camera,
classifier or dispatcher is created by the repair widget.

Completed collection displays valid-slot and retained-class counts. An explicit
count-review checkbox and **Save separate TRAIN candidate** produce a new UUID
directory under the host's private root. The chosen class's old TRAIN records are
replaced; other TRAIN records, invalid evidence and feature values are retained.
VALIDATION, TEST and UNKNOWN records are excluded, and remain in their original
source files. Source and collected-input hashes are checked before publication.

Cancelled/incomplete collections and trials with invalid/missing slots cannot
produce a candidate. Their original evidence remains saved. Pending collection
save failure uses the existing Retry save path; candidate-save failure leaves
the original untouched and allows retry into a new directory. Empty unpublished
directories/sidecars may remain after storage failure; they are never offered as
complete candidates. The original profile is never renamed, deleted or overwritten.

## Host interface

- Embed `PoseRepairWidget(private_root)` and call `set_source(ProfileRecord)`.
  Read the record from the existing selected saved profile. Ad-hoc datasets can
  first be explicitly saved as profiles through the existing selector.
- Its inherited `capture_requested(plan, request_id)`, `attach_capture`,
  `receive_observation`, `capture_failed`, `capture_release_requested`,
  `stop_collection` and save-error lifecycle match EnrolmentWidget.
  `EnrolmentPlan.collection_labels` is optional; ordinary four-label collection
  remains unchanged. A repair plan permits one vocabulary label in TRAIN only.
- Deston must attach this widget to the existing observation-only worker, suspend
  routing and respect capture generations, focus/tab interruption and save retry.
  Current shell code addresses `enrolment_widget` directly; it does not yet attach
  this additional widget. No shell code changes are included in this component PR.
- The inherited `dataset_saved` denotes the one-label collection evidence, which
  is not a complete trainable profile. Do not automatically train it. Instead
  connect `candidate_ready(RepairCandidate)` to
  `ProfileSelectorWidget.offer_repair_candidate(candidate)` after capture release.
- `offer_repair_candidate` populates review fields and preserves source settings,
  hand and names. It requires another explicit permission confirmation and
  **Create and load personal profile** click. Training uses the existing selector
  worker and `ProfileStore.create`; installation uses `use_studio_profile`.
- Keep host busy serialization in place. A new model has a different model
  revision and unverified readiness. Existing installation expires the host's
  previous LIVE eligibility, restores paused Preview and requires fresh NEUTRAL.
- Roll back by selecting `candidate.rollback_profile_id` and using the existing
  Load selected / `load_studio_profile` path. Rollback also clears readiness; it
  does not restore an old LIVE grant. A failed load retains the current selection.

## Generated demonstration and actual limits

Run `python scripts/demo_pose_repair.py` with the repository on PYTHONPATH.
It creates a new ignored `.local/pose-repair-demo/generated-UUID` with four UI
snapshots, a local aggregate workflow JSON and generated fixture data/profiles.
These deliberately use test provenance fields to exercise the real validators,
are prominently labelled GENERATED SOFTWARE DEMO ONLY, and must never be treated
as participant data, recognition accuracy or LIVE readiness. No private input or
webcam is used. No generated output belongs in Git.

Hau Jie separately confirmed P02 loading, open-palm NEUTRAL/READY, camera pause
and reopening without errors on 5 October. That session's exact source revision
was not independently recorded. This qualitative laptop report is not
a new complete Practice pass. Earlier NEUTRAL misses remain preserved. Building
the repair feature does not establish that this user needs further collection;
targeted collection requires diagnostic review. Human repair and shared-shell
integration are pending Deston's review.

## Local verification, 5 October

Base: reviewed main `50e2687`, on `codex/hau-jie-profiles`.

- Final focused collection/profile/repair checks: 116 passed in 23.55 seconds,
  including 22 new repair cases. Generated UI demo exited 0 and readable review
  and candidate/rollback screenshots were inspected.
- Final full pytest: 828 passed, 1 skipped in 239.39 seconds, with
  OMP/OPENBLAS/MKL thread counts set to 1 for this check. An earlier full run
  before the final focused additions passed 822 tests with one skip.
- Ruff: all checks passed. Mypy: no issues in 91 source files.
- Studio and assignment `--smoke-test`: each exited 0. Diff whitespace check passed.

These verify software behavior only. The shared-host attachment and physical
selected-pose repair still require integration and participant testing.
