# GestureForge Studio progress

Snapshot: 30 September 2026. This measures the final-project extension, not the already submitted assignment or an expected grade.

## Completion measure

Progress = the original estimated hours of fully completed tasks / the total original estimated hours in [TEAM_BACKLOG.csv](TEAM_BACKLOG.csv). These are task weights, not hours actually worked. In-progress tasks receive no completion credit until their acceptance evidence is complete.

| Owner | Completed task weight / planned | Verified completion |
| :--- | ---: | ---: |
| Deston | 8 / 75 | 10.7% |
| Hau Jie | 0 / 75 | 0% verified |
| Javier | 0 / 73 | 0% verified |
| Team | 8 / 223 | 3.6% |

Two of 29 tasks are complete: GF-P01 (preserve/review the assignment baseline, 2 hours) and GF-P32 (author the fictional scenario and evaluation protocol, 6 hours). GF-P32 is content/protocol authoring; this does not claim an implemented runbook or completed user study. No teammate feature branches or open PRs were available during this snapshot. Zero verified completion does not mean a teammate has done no work locally.

## Built, but broader tasks still in progress

- **GF-P02 â€” Deston:** shared typed actions, immutable routing snapshots, controller integration, invalidation and simulation routing are implemented and tested. The complete profile/workspace schemas and screen contracts still need integration review with the builders.
- **GF-P10 â€” Deston:** the opt-in Studio preview opens, simulates held gesture actions, pauses on focus loss, and invalidates old context events. An on-screen Preview/Rehearsal selector and gesture-to-action draft editor now apply changes through a validated pause/reset; interrupted and stale identity packets cannot replace the active display. Mappings are in memory only. Starter/profile selection, readiness checks and the final integrated session workflow remain to be built. The preview cannot dispatch desktop actions.
- **GF-P05 â€” Javier:** Windows launch and camera-handoff probe is selected as the first task; no completion evidence has been received.

Software checks are recorded in [verification.json](verification.json). Automated simulation is not live-camera, Windows launch, starter-recognition or second-laptop evidence. The submitted assignment archive remains unchanged. GitHub Actions is manual-only; these checks ran locally.

## Next deliverables

- **Hau Jie:** GF-P03 custom vocabulary/legacy import and GF-P28 consented starter feasibility spike, on `codex/hau-jie-profiles`.
- **Javier:** GF-P05 Windows target/camera probe, followed by GF-P08 viewer actions and GF-P09 validated storage, on `codex/javier-shortcuts`.
- **Deston:** review the first deliverables, finalise shared schemas/screens, integrate readiness and session UI, and own verification, design and release decisions.

Use [TEAM_GUIDE.md](TEAM_GUIDE.md) and the individual briefs for file ownership, test expectations and PR rules. Teammates push their own branches; Deston reviews and merges into main. Move cards to Done only with linked acceptance evidence.
