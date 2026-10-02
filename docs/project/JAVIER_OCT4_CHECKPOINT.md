# Javier — 4 October 2026 checkpoint

Prepared 2 October. Current priorities: GF-P05 native Windows launch evidence and demonstrated component defects. Studio shell integration remains Deston's responsibility. This checkpoint preserves Javier's PR #15 handoff and its historical Linux software results; it does not replace current integration verification or add hardware evidence.

## Recorded checkpoint state

- DONE: sync reviewed main `a6fe7b6` into `codex/javier-shortcuts` as `1034089`, preserving branch work and history without reapplying the ZIP.
- DONE: combined Linux/Python 3.12 offscreen checks: 373 tests, Ruff, mypy and four startup smokes pass. Exact output: [historical software checks](../evidence/javier-oct4-software-checks.json).
- NOT RUN HERE: new human P03 sessions/UNKNOWN trials, private dataset transfer, Windows native opening, actual focus/camera/failure recovery and both-laptop acceptance. This environment has no Windows laptop or participant camera.
- Existing shared checkpoint reports P03's two sessions plus UNKNOWN: 350/360 valid slots, including ten invalid UNKNOWN slots. This is Hau Jie's prior supplied evidence, not new collection performed here. Preserve that dataset and its baseline; do not silently replace detection failures or tune against the held-out participant.

## Windows checkout

Use your real Git checkout, not an old ZIP extraction. Save uncommitted local changes before updating; do not discard them. In PowerShell at the repository root:

```powershell
git status --short
git fetch origin
git switch codex/javier-shortcuts
git pull --ff-only origin codex/javier-shortcuts
git branch --show-current
git rev-parse HEAD
.\.venv\Scripts\python.exe --version
```

If Git reports local changes or diverged history, stop before overwriting anything and retain the error for review. Use `setup.cmd` for a missing environment (64-bit Python 3.11); do not copy another person's `.venv`.

## Preserve P03; collect repair data only for a diagnosed defect

If Hau Jie identifies a concrete defect requiring repair data, follow the [starter collection guide](STARTER_COLLECTION_GUIDE.md) and [collection reference](../DATA_COLLECTION.md). Only pass `--consent` after agreeing to numeric feature collection and team-internal evaluation; final/public distribution is separate. Use right hand and the guide's standard poses. No raw video/audio is stored by the collector.

P03 collection is already reported complete in Hau Jie's [starter checkpoint](STARTER_EVALUATION_CHECKPOINT.md). Preserve those inputs and the failed baseline; there is no blanket recollection task. Only after Hau Jie diagnoses a collection defect and specifies a repair batch, use a separate fresh root, such as `data/local/starter-oct4/P03`; never append a new batch to the old baseline. Record real setup/pose details and collect only the repair scope agreed with Hau Jie. For reference, a complete standard batch uses session 1 (`train`), session 2 (`validation`) and eight `validation_negative` UNKNOWN trials; use a fresh output root and verified camera index if that complete batch is specifically required. Each positive session has eight trials for each of four labels (32 trials); negatives have eight trials. Five scheduled slots per trial gives 72 trials / 360 scheduled slots. Keep invalid slots.

Standard UNKNOWN sequence for reference: trials 1–3 index finger only; 4–6 index/middle/ring; 7–8 thumb-index pinch. Take a break/reposition between positive sessions; keep the same action poses. Do not fabricate or drop failed slots.

For an agreed repair batch, privately transfer its manifests and each exact `feature_file` referenced by them to Hau Jie, with internal-use permission and actual setup notes. A complete three-part batch contains six current files; verify any transfer includes all files referenced by the supplied manifests. Do not upload numeric participant features, private consent, detailed evaluation outputs or local probe logs to a PR. No transfer has been sent by this assistant; it requires the actual dataset and a verified private destination.

## Real Windows launches and recovery

Follow the canonical [Windows launch procedure](../evidence/WINDOWS_LAUNCH_PROCEDURE.md). Use a unique output filename per attempt, since the existing probe writes to its chosen path:

```powershell
.\.venv\Scripts\python.exe -m scripts.windows_launch_probe --laptop-id laptop-A --camera 0 --output ".local\windows-probe-laptop-A-oct4-01.json"
```

1. Record branch revision, winver, Python, camera index, permissions and connectivity in observer notes.
2. Test Calculator, Camera, an allowed local TXT/PDF, a local folder and credential-free HTTPS with explicit buttons. Separately confirm actual visible opening or failure; `launch_requested` alone is not app-ready evidence.
3. For Camera, first receive a real capture frame. Verify shutdown acknowledgement precedes launch; close Camera, return manually, explicitly resume and observe reacquisition.
4. Switch away and return: routing pauses and stays paused until explicit resume. Test missing-target recovery using only a disposable file; retain each failure and fresh retry. Leave unavailable association/timeout checks NOT RUN, with reasons.
5. Preserve the original local JSON and actual notes privately. Submit a pseudonymous summary with PASS/FAIL/NOT RUN per case, actual errors, recovery, source revision and remaining limits. Fix only demonstrated component defects with regressions; escalate shell defects to Deston.

The isolated probe does not establish gesture readiness, LIVE shell dispatch or GF-P19 completion. Both-laptop integrated testing remains a separate gate. Submit subsequent fixes on `codex/javier-shortcuts`, with a focused PR to `main` left unmerged for Deston.
