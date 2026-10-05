# GF-P12 selected-pose TRAIN repair

Component owner: Hau Jie. Host integration/review: Deston. Updated 5 October 2026.

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
source files. Original-dataset and reviewed-collection hash checks are performed
before publication. Studio separately checks the installed source profile and
model identity.

Cancelled/incomplete collections and trials with invalid/missing slots cannot
produce a candidate. Their original evidence remains saved. Pending collection
save failure uses the existing Retry save path; candidate-save failure leaves
the original untouched and allows retry into a new directory. Empty unpublished
directories/sidecars may remain after storage failure; they are never offered as
complete candidates. SaveError handling retains the collected evidence for retry.
The original profile is never renamed, deleted or overwritten.

## Integrated host flow

- Studio embeds `PoseRepairWidget(private_root)` as the **Repair pose** tab on
  `Window.pose_repair_widget`. The source is the installed saved personal
  profile selected through Profiles. Guest/manual mode and ad-hoc manifests are
  disabled for repair; save an ad-hoc TRAIN manifest as a profile first.
- The widget uses the existing observation-only capture worker and inherited
  `capture_requested(plan, request_id)`, `attach_capture`, `receive_observation`,
  `capture_failed`, `capture_release_requested`, `stop_collection` and
  save-error lifecycle. Routing is suspended during repair and no action can
  dispatch. `EnrolmentPlan.collection_labels` remains optional; ordinary
  four-label Enrolment is unchanged.
- The inherited `dataset_saved` records one-label collection evidence only.
  It is not a complete trainable profile and is never auto-trained.
  `candidate_ready(RepairCandidate)` opens
  `ProfileSelectorWidget.offer_repair_candidate(candidate)` after capture
  release.
- `offer_repair_candidate` populates Profiles review fields and preserves source
  settings, hand, names and permission notes. It requires explicit permission and
  **Create and load personal profile**. Training uses the existing selector
  worker and `ProfileStore.create`; installation uses `use_studio_profile`,
  paused in Preview with readiness expired.
- Roll back with **Load selected** on `candidate.rollback_profile_id`, the
  unchanged original profile. Rollback also clears readiness and cannot restore
  an old LIVE grant. A failed create/load or rollback load retains the current
  selection.

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
a new complete Practice pass. Earlier NEUTRAL misses remain preserved. The
repair feature does not establish that this user needs further collection;
targeted collection requires diagnostic review. Human repair evidence remains
separate from generated workflow evidence and final participant testing.

## Local verification, 5 October

Historical component base: `50e2687`, on `codex/hau-jie-profiles`.
Final integrated check: main `19fec08` plus PR #25 head `0ddc757` and
Deston's reviewed host integration. Exact source hashes are in `verification.json`.

Historical component checks covered selected-label collection, retained classes,
invalid/cancelled repair, candidate-save retry, profile review, candidate load
and rollback screenshots. Final verification passed 862 tests with one
unsupported Windows symlink skip in 300.38 seconds. Ruff, mypy across 95 files,
both GUI startup modes and synthetic evaluation all passed. Final independent
review found no issues.

The offscreen five-snapshot generated workflow was inspected: actual collection
recorded 10 NEUTRAL slots, proceeded through count review, created a candidate
profile and rolled back to the original. The check left two profiles, preserved
the original unchanged and did not record outcomes or grant LIVE eligibility.
GF-P12 is Done against the original selected-pose repair software criterion.

These verify software behavior only. Physical selected-pose repair and later
participant evaluation remain separate evidence.
