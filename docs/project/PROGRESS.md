# GestureForge Studio progress

Snapshot: 30 September 2026. This measures the final-project extension, not the already submitted assignment or an expected grade.

## Completion measure

Progress = the original estimated hours of fully completed tasks / the total original estimated hours in [TEAM_BACKLOG.csv](TEAM_BACKLOG.csv). These are task weights, not hours actually worked. In-progress tasks receive no completion credit until their acceptance evidence is complete.

| Owner | Completed task weight / planned | Verified completion |
| :--- | ---: | ---: |
| Deston | 8 / 75 | 10.7% |
| Hau Jie | 5 / 75 | 6.7% |
| Javier | 0 / 73 | 0% verified |
| Team | 13 / 223 | 5.8% |

Three of 29 tasks are complete: GF-P01 (preserve/review the assignment baseline, 2 hours), GF-P32 (author the fictional scenario and evaluation protocol, 6 hours), and GF-P03 (custom vocabulary and legacy import, 5 hours). GF-P32 is content/protocol authoring; this does not claim an implemented runbook or completed user study. Hau Jie's [PR #10](https://github.com/Chi944/GestureForge_304/pull/10) passed independent review and 151 tests at its submitted head and was merged. No Javier feature branch or PR was available during this snapshot. Zero verified completion does not mean a teammate has done no work locally.

## Built, but broader tasks still in progress

- **GF-P02 â€” Deston:** shared typed actions, immutable routing snapshots, controller integration, invalidation and simulation routing are implemented and tested. The complete profile/workspace schemas and screen contracts still need integration review with the builders.
- **GF-P10 - Deston:** the opt-in Studio preview opens, simulates held gesture actions, pauses on focus loss, and invalidates old context events. Its Preview/Rehearsal selector and gesture-to-action draft editor apply changes through a validated pause/reset; interrupted and stale identity packets cannot replace the active display. The launcher now passes the selected vocabulary into training and Studio, renders the enrolled IDs, binds predictions to a data/settings-derived model revision and rejects mappings to absent IDs before stopping capture. Mappings are in memory only. Starter/profile selection, readiness checks and the final integrated session workflow remain to be built. The preview cannot dispatch desktop actions.
- **GF-P05 â€” Javier:** Windows launch and camera-handoff probe is selected as the first task; no completion evidence has been received.

Software checks are recorded in [verification.json](verification.json). Automated simulation is not live-camera, Windows launch, starter-recognition or second-laptop evidence. The submitted assignment archive remains unchanged. GitHub Actions is manual-only; these checks ran locally.

## Next deliverables

- **Hau Jie:** GF-P03 is accepted; next is GF-P28 consented starter feasibility, then profile lifecycle/enrolment, on `codex/hau-jie-profiles`. Sync the merged main before starting the next PR.
- **Javier:** GF-P05 Windows target/camera probe, followed by GF-P08 viewer actions and GF-P09 validated storage, on `codex/javier-shortcuts`.
- **Deston:** review the first deliverables, finalise shared schemas/screens, integrate readiness and session UI, and own verification, design and release decisions.

Use [TEAM_GUIDE.md](TEAM_GUIDE.md) and the individual briefs for file ownership, test expectations and PR rules. Teammates push their own branches; Deston reviews and merges into main. Move cards to Done only with linked acceptance evidence.
