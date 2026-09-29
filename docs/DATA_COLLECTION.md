# GestureForge Data Collection Protocol

Status: P01 consented right-hand pilot completed: 32 TRAIN, 32 VALIDATION and eight validation-negative trials, 360/360 valid scheduled samples. Numeric features remain excluded from GitHub and the source-only ZIP. Private tutor/marker submission permission was granted on 26 September. No scheduled deletion has been requested for the local numeric P01 data, and no raw images or video are stored. See [RESULTS.md](evidence/RESULTS.md) for measured results and limitations.

Observed samples store their actual monotonic capture time. Trial start times and the five scheduled offsets are stored in metadata, allowing sampling delay to be audited. A slot with no observed frame keeps its scheduled time as a placeholder and is explicitly invalid; it is never treated as an actual capture.

## Purpose

The dataset supports a personal gesture recogniser for a bounded card-viewer prototype. It is not a general gesture dataset and must not be described as representative of the wider population.

## Consent and Privacy

Before collecting usable data:

- Explain the project purpose.
- Explain what will be recorded.
- The implemented prototype stores numeric features and manifests, not raw video or audio.
- Use participant pseudonyms such as `P01`.
- Agree how long data will be retained.
- Confirm whether data can be included in the submitted package for marking.

Do not collect or submit participant data without consent.

## Assignment Pilot

Participant count:

- One consenting participant.

Sessions:

- TRAIN session.
- VALIDATION session.
- Separate validation-negative trials of ordinary movement and unfamiliar poses. These measure classifier rejection only; final continuous false-action testing remains a project task.

Labels:

- NEXT
- PREVIOUS
- BOOKMARK
- NEUTRAL

Trials:

- Eight trials per label per session.
- Two-second stable pose.
- Release interval between trials.
- Five predetermined samples per trial.

Maximum planned assignment size:

- 64 trials.
- 320 feature vectors.

## Final Project Collection

Participant count:

- Two consenting participants.

Sessions per participant:

- TRAIN.
- VALIDATION.
- TEST.

Trials:

- Twelve trials per label per session.
- Up to five feature vectors per trial.

Maximum planned final size:

- 288 trials.
- 1,440 feature vectors.

## Collection Conditions

Choose four distinct static poses that are comfortable for the participant. For example, start by trying an open palm for NEUTRAL, a fist for NEXT, a thumb-up pose for PREVIOUS and two extended fingers for BOOKMARK. These are suggestions, not built-in recogniser labels. The participant may choose different poses; record the exact mapping in the session `--setup` notes and use the same mapping in later sessions. Collect new development data if validation shows confusion. Never redefine poses based on final test results.

Record these fields in the manifest:

- Participant pseudonym.
- Session ID.
- Split.
- Date and approximate time.
- Selected hand.
- Camera.
- Lighting notes.
- Background notes.
- Seated or standing posture.
- Distance from camera.
- Label.
- Trial ID.
- Scheduled sample timestamps.
- Validity for each sample.
- Rejection reason if invalid.

## Split Rules

- Keep all frames from one trial in one split.
- Do not randomly split neighbouring frames.
- Fit preprocessing only on training data.
- Do not open final TEST results until model and rejection settings are frozen.

## Quality Notes

Invalid detections are evidence. Keep them in the manifest and count them as UNKNOWN during scoring. Do not drop difficult samples silently because that would overstate performance.

## Storage Plan

Recommended paths:

- `data/local/pilot/manifest.json` (sessions append to one participant's manifest)
- `data/local/pilot/manifest.features.<hash>.npz` (numeric content-addressed sidecar)
- `experiments/local/<date>-pilot-results.json`
- `experiments/final/<date>-heldout-results.json`

Do not commit private or non-consented data.

Keep both the manifest and its referenced `feature_file` together when transferring consented data for marking. Older content-addressed sidecars may remain as recovery copies; only the currently referenced sidecar is needed to reproduce a frozen manifest.
