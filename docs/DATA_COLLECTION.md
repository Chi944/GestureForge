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

This is separate from the completed assignment pilot. The Studio plan uses the
three team contributors for starter development, then at least two new consenting
participants excluded from starter fitting and tuning. Each new participant's
personal TRAIN/VALIDATION data and standard-pose TEST data remain separate.
See [the paired evaluation guide](project/PAIRED_EVALUATION.md) for freezing
configurations before opening final TEST results. Changed custom poses are a
different experiment and must not be presented as the same-pose comparison.

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

The collector now accepts positive `--split test`. Use a new, TEST-only output
folder and the same `--pose-set-id` recorded in the frozen evaluation. For example,
after consent and protocol/configuration freeze, using the legacy four labels:

```powershell
.\.venv\Scripts\python.exe -m gestureforge.collect --participant P04 --split test --pose-set-id standard-v1 --trials 12 --hand Right --camera 0 --output data/local/P04/test --setup "Replace with actual recording conditions" --consent
```

Replace the participant, camera, hand, pose ID and conditions with actual agreed
values. For G1/G2/G3 or another custom vocabulary, also pass `--vocabulary` with
the same versioned vocabulary JSON used for development. Do not mix label sets.
The command stores numeric features only. Invalid and missing scheduled slots
remain in the manifest. The operator controls each trial; this command is not a
request for Deston to record now.

Use `--pose-set-id` from the first TRAIN collection when starting a new protocol.
Appending to a declared dataset preserves its ID if the option is omitted and
rejects a conflicting ID. Existing legacy development data are not retroactively
tagged by appending; document their pose equivalence explicitly when freezing.
TEST and development records cannot be appended to each other's manifests.
`validation_negative` remains development rejection evidence; it is not an
independent final negative test split.

## Quality Notes

Invalid detections are evidence. Keep them in the manifest and count them as UNKNOWN during scoring. Do not drop difficult samples silently because that would overstate performance.

## Storage Plan

Recommended paths:

- `data/local/pilot/manifest.json` (sessions append to one participant's manifest)
- `data/local/pilot/manifest.features.<hash>.npz` (numeric content-addressed sidecar)
- `experiments/local/<date>-pilot-results.json`
- `experiments/local/final/<date>-heldout-results.json`

Do not commit private or non-consented data.

Keep both the manifest and its referenced `feature_file` together when transferring consented data for marking. Older content-addressed sidecars may remain as recovery copies; only the currently referenced sidecar is needed to reproduce a frozen manifest.
