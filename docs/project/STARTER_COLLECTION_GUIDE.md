# GF-P28 starter collection guide

Owner: Hau Jie. Review/integration: Deston. This guide covers the new three-member
starter feasibility collection. It does not reuse or broaden permission for the
assignment P01/P02 data, and it does not claim starter performance.

## Purpose and responsibility

Each team member records their own right-hand samples on their own computer or a
shared computer. Use a separate pseudonymous participant ID and folder. Hau Jie
checks the transferred datasets and runs the person-separated kNN/SVM comparison.
Deston reviews the evidence and integrates the selected frozen starter configuration.

Suggested IDs:

- Deston: `P01`
- Hau Jie: `P02`
- Javier: `P03`

Before collection, the participant must explicitly agree to numeric feature
collection and team-internal model evaluation. Permission to redistribute or include
the features in the final submission is a separate decision. The collector stores
normalised numeric features and manifests, not raw images, video or audio. Do not commit
participant data to GitHub.

## Windows setup and camera check

Use the latest `main` source in an English-only local path when possible. Use 64-bit
Python 3.11. From PowerShell in the repository root:

```powershell
.\setup.cmd
.\.venv\Scripts\python.exe scripts/check_environment.py --camera --camera-index 0
```

Close Camera, Teams, Zoom and other camera users first. If index 0 fails or selects
the wrong device, check index 1 and consistently substitute the working index below.
Do not copy another computer's `.venv`.

## Standard poses

Use the same right-hand poses in both sessions:

- `NEXT`: closed fist.
- `PREVIOUS`: thumb up, other fingers folded.
- `BOOKMARK`: index and middle fingers raised, other fingers folded.
- `NEUTRAL`: open palm.

For each trial, prepare the displayed pose, press Space, wait for the countdown,
hold still during the two-second sampling interval, and relax only when `Release`
appears. Reposition slightly between trials. Keep invalid scheduled samples; they
are evidence and must not be silently recollected until a score improves. Q stops
collection while preserving complete trials.

Replace `P03` and the camera index below for the actual participant.

Session 1:

```powershell
.\.venv\Scripts\python.exe -m gestureforge.collect `
  --output "data\local\starter\P03\session-1" `
  --participant P03 --split train --hand Right --trials 8 --camera 0 `
  --setup "P03 laptop, camera 0, right hand, starter session 1" --consent
```

Take a short break and reposition before the separate second run.

Session 2:

```powershell
.\.venv\Scripts\python.exe -m gestureforge.collect `
  --output "data\local\starter\P03\session-2" `
  --participant P03 --split validation --hand Right --trials 8 --camera 0 `
  --setup "P03 laptop, camera 0, right hand, separate starter session 2" --consent
```

Each session contains eight trials per four labels and at most five scheduled
vectors per trial: 32 trials and 160 vectors maximum. The split names identify the
two development sessions. The later person-separated evaluator must exclude the
held-out participant completely from model fitting and preprocessing.

## Unfamiliar-pose negatives

Run eight separate `validation_negative` trials:

```powershell
.\.venv\Scripts\python.exe -m gestureforge.collect `
  --output "data\local\starter\P03\negatives" `
  --participant P03 --split validation_negative --hand Right --trials 8 --camera 0 `
  --setup "P03 laptop, camera 0; trials 1-3 index only, 4-6 three fingers, 7-8 pinch" `
  --consent
```

The collector displays `UNKNOWN`; the operator must follow this sequence:

- Trials 1-3: index finger only.
- Trials 4-6: index, middle and ring fingers raised.
- Trials 7-8: thumb-index pinch.

These samples tune/check classifier rejection only. They do not replace later
continuous no-hand, transition and five-second false-action tests.

## Transfer checklist

The participant sends Hau Jie the complete private participant folder containing:

```text
P03/
  session-1/manifest.json
  session-1/manifest.features.<hash>.npz
  session-2/manifest.json
  session-2/manifest.features.<hash>.npz
  negatives/manifest.json
  negatives/manifest.features.<hash>.npz
```

Before sending, open the ZIP and confirm it is not empty and contains all six files.
Keep every manifest beside the exact `feature_file` named inside it. Send the ZIP
privately; do not use a Git commit, PR or repository upload for participant data.

Also send an explicit permission record such as:

> I consent to using my P03 numeric gesture data for internal GestureForge team
> training and evaluation. Permission to include or redistribute my data in the
> final submitted package will be decided separately.

Hau Jie verifies participant identity, selected hand, vocabulary, trial counts,
invalid samples, sidecar hash and split separation before evaluation. A participant
must correct what pose they actually showed if it differed from the setup note.

## Related repository guides

- `docs/WINDOWS_LAPTOP.md`: installation and camera troubleshooting.
- `docs/DATA_COLLECTION.md`: consent, privacy, split and storage rules.
- `docs/project/HAU_JIE_HANDOFF.md`: GF-P28 ownership and acceptance requirements.
- `docs/project/PROJECT_PLAN.md`: three-member starter and person-separated protocol.
