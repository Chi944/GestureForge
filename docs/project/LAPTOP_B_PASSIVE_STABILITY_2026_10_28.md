# Laptop B passive Studio measurement — 28 October 2026

Hau Jie's new full-Studio aggregate run satisfies its monitor duration/gap,
worker-release and actual child-exit checks. **It was a passive run:** the
operator explicitly reported no clicks or scrolling. It does not complete
the required interactive workflow, independent guide-only installation,
offline core, remaining native recovery, recognition or whole-release acceptance.
Deston decides the disposition of the remaining interaction coverage.

## Exact tested identity

- Runtime source: `708e77eadf64d43dfbb477d2ab8955c815f68b1a`.
- Source ZIP SHA256: `988e7e38d31e7e6fb705c02a1072f0fa7355431aaf599f097c076286fcb62f3b`.
- Fresh separate environment, agent-assisted installation; Python 3.11.15,
  Windows platform API `10.0.26300`, AMD64, camera index 0.
- Existing P02 Original was copied byte-identically for Preview capture.
  No model/settings change, new collection, Practice or LIVE grant.
- Existing reviewed `scripts.run_stability` / `scripts.monitor_studio` were
  used without private runtime instrumentation edits.

After this run, the branch was fast-forwarded to reviewed main
`1e12dfe7d30ab2c7184044dbe9df74d747ed651f`. **That revision was not the measured
runtime.** Its newer checkpoint-write timing fields are absent from this run
and cannot be backfilled. No new run is implied by synchronizing the branch.

## Same-run original receipts inspected

| Observation | Result |
| --- | --- |
| Longest continuous delivered interval | 1,835.532 s = 30 min 35.532 s |
| Delivered observations | 44,378 |
| Delivered observations per sampled camera-active second | 24.100887 |
| Peak process working set | 458,452,992 bytes = 437.214844 MiB |
| Maximum active GUI heartbeat gap | 0.125 s |
| Maximum delivered-observation gap within generation | 0.296 s |
| Worker errors / unexpected stops | 0 / 0 |
| Final status / normal close | final / observed normal window close |
| Qt exit / actual child-process exit | 0 / 0 |
| Workers released / same-run monitor+process criteria | true / true |

The agent normally closed Studio after the requested duration. The original
launcher returned 0. Original `measurement.json` and `process.json` agree;
no final receipt or prior run was substituted. The 0.296-second value is within
this monitor's two-second gap limit, not evidence of Practice's capture coverage.
The rate is delivered UI observations, not a raw camera-driver frame-rate claim.
Setup/paused time is excluded from the continuous interval.

After actual Studio exit and worker release, Windows Camera was opened. Hau Jie
confirmed real-time video and reported closing it. A subsequent native window
inventory contained neither Studio nor Camera. This is attributed operator
reacquisition evidence; no camera screenshot, photo or video was retained.

## Boundaries and remaining work

- The operator left Studio running without interacting. Timer/observation
  responsiveness cannot establish actual clicking, scrolling or task completion.
- Independent operator start/end times were not supplied. Exact measured duration
  comes from the monitor, not an invented human clock record.
- The run was assisted and no deliberate network disconnection was recorded.
- Full logs, profile and numerical data stay private. Only NEW same-run receipts,
  identity, observations, hashes and an English contents index are packaged.
- Do not concatenate this with earlier interrupted, pipeline-only or reported
  runs. Do not automatically repeat thirty minutes to fill missing interaction.
- Next physical checks are the [current Laptop-B recovery/offline route](JAVIER_WINDOWS_REMAINING_CASES_2026_10_25.md#destons-shortest-closure-route--28-october).
  Retain guide-only assistance and fixture availability as separate limitations.

Validation for this documentation: original JSON consistency, recorded metrics,
actual launcher output/exit, safe unique packet members and indexed payload
hashes. No new production change, new main software-suite pass or task acceptance
is claimed. The 90 focused tests and baseline software failures belong to the
earlier [708e77e preparation](LAPTOP_B_RELEASE_CHECKLIST_2026_10_27.md), not this
later main revision. Subsequent reviewed source fixes do not rewrite that record.
