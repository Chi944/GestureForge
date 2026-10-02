# Javier — 4 October 2026 checkpoint

Prepared 2 October. Priorities: own P03 contribution, GF-P05 native Windows launches, and demonstrated component defects. Studio shell integration remains Deston's responsibility.

## Current state

- DONE: sync reviewed main `a6fe7b6` into `codex/javier-shortcuts` as `1034089`, preserving branch work and history without reapplying the ZIP.
- DONE: combined Linux/Python 3.12 offscreen checks: 373 tests, Ruff, mypy and four startup smokes pass. Exact output: `oct4-software-checks.json`.
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

## P03 collection and private transfer

Follow `docs/project/STARTER_COLLECTION_GUIDE.md` and `docs/DATA_COLLECTION.md`. Only pass `--consent` after agreeing to numeric feature collection and team-internal evaluation; final/public distribution is separate. Use right hand and the guide's standard poses. No raw video/audio is stored by the collector.

The latest task request asks for your own recording. First preserve any existing P03 data reported in the checkpoint. For an explicitly requested new collection/repair batch, use a separate fresh root, such as `data/local/starter-oct4/P03`; never append a new batch to the old baseline. Record real setup/pose details. From the shared guide, run session 1 (`train`), session 2 (`validation`) and eight `validation_negative` UNKNOWN trials, changing only each output root to the fresh one and the camera index to your verified device. Each positive session has eight trials for each of four labels (32 trials); negatives have eight trials. Five scheduled slots per trial gives 72 trials / 360 scheduled slots. Keep invalid slots.

UNKNOWN sequence: trials 1–3 index finger only; 4–6 index/middle/ring; 7–8 thumb-index pinch. Take a break/reposition between positive sessions; keep the same action poses. Do not fabricate or drop failed slots.

Privately transfer the three manifests and each exact `feature_file` referenced by them to Hau Jie, with internal-use permission and actual setup notes. Verify the ZIP contains all six current files. Do not upload numeric participant features, private consent, detailed evaluation outputs or local probe logs to a PR. No transfer has been sent by this assistant; it requires the actual dataset and a verified private destination.

## Real Windows launches and recovery

Follow `WINDOWS_EVIDENCE.md` (aligned with `docs/evidence/WINDOWS_LAUNCH_PROCEDURE.md`). Use a unique output filename per attempt, since the existing probe writes to its chosen path:

```powershell
.\.venv\Scripts\python.exe -m scripts.windows_launch_probe --laptop-id laptop-A --camera 0 --output ".local\windows-probe-laptop-A-oct4-01.json"
```

1. Record branch revision, winver, Python, camera index, permissions and connectivity in observer notes.
2. Test Calculator, Camera, an allowed local TXT/PDF, a local folder and credential-free HTTPS with explicit buttons. Separately confirm actual visible opening or failure; `launch_requested` alone is not app-ready evidence.
3. For Camera, first receive a real capture frame. Verify shutdown acknowledgement precedes launch; close Camera, return manually, explicitly resume and observe reacquisition.
4. Switch away and return: routing pauses and stays paused until explicit resume. Test missing-target recovery using only a disposable file; retain each failure and fresh retry. Leave unavailable association/timeout checks NOT RUN, with reasons.
5. Preserve the original local JSON and actual notes privately. Submit a pseudonymous summary with PASS/FAIL/NOT RUN per case, actual errors, recovery, source revision and remaining limits. Fix only demonstrated component defects with regressions; escalate shell defects to Deston.

The isolated probe does not establish gesture readiness, LIVE shell dispatch or GF-P19 completion. Both-laptop integrated testing remains a separate gate. Keep the PR unmerged for Deston.
