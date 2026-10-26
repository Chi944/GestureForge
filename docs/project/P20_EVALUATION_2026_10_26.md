# GF-P20 evaluation — 26 October 2026

**Evaluation complete, with measured limitations.** One familiar consenting team
operator used the selected personal right-hand profile on Windows. No settings
were tuned on this evaluation. This closes the evaluation task, not every
performance target or release/device requirement. GF-P21 retains the recognition
review; GF-P19/GF-P23 retain native device and release checks.

## Results

| Check | Observed result | Interpretation |
| --- | --- | --- |
| Earlier twenty-hold capture | 20 matching simulated actions; no extra/wrong commands | No-repeat protection demonstrated in that capture; first action was 0.047 s after its release instruction. Cues were not physical-onset annotations. |
| Ten-minute non-command activity | Zero protected actions; 36 naive per-frame requests | Meets the negative-action target for this recorded profile/run. Not proof of native launch safety or performance for other users. |
| Fresh visual latency capture | 20 cued attempts; 16 matching responses, four misses; zero duplicate/wrong commands | 80% response coverage in this separate recording. Earlier hold results remain separate. |
| Response latency, successful attempts only | Median interval 0.383–0.555 s; nearest-rank p95 interval 0.515–0.718 s | Camera-frame-referenced pose onset to simulated dispatch, including activation hold. Conditional p95 is below one second; the four misses prevent a claim that 95% of all attempts responded within one second. |
| Protected/unprotected replay, fresh capture | 16 protected actions versus 1,463 naive per-frame requests | Same input sequence; replay and runtime action order/kinds agree. Runtime dispatch follows replay receipt/event time by 0–0.016 s. |
| Manual workflow M | 105.094 s task; 129.390 s setup; ten manual outcomes; six stage acknowledgements | Completed walkthrough; operator confirms the prescribed results/recovery. |
| Personal workflow P | 165.844 s task; 160.391 s setup; 15 gesture/four manual outcomes; zero saved stage acknowledgements | Operator confirms all checks and intentional extra launches/navigation. Missing exported acknowledgements remain missing. |

M ran on `a0095b3`; P ran on `0ed7c32` after the camera-start fix. Both used the
same Harbor workspace. The operator confirmed 240 credits, the training
coordinator, missing-file recovery, paused restore without replay, and summary
review. The extra P checks were intentional. These are assisted engineering
walkthroughs, not a controlled speed comparison: builds, action counts and manual
support differ. The strict comparison scorer's success/pairing conditions are not
met; no paired speed advantage is claimed. Setup included assistance.

## Latency annotation and reproducibility

The fresh capture on `ca02e03` saved 2,669 timestamped JPEG frames over 181.016 s.
All archive/index checksums and all individual JPEG hashes verify. Every image
index identity and timestamp matches the consumed-prediction trace. Current
`app.py` and capture-helper source hashes match the recording. The maximum frame
gap is 0.188 s; one input was stale at 0.203 s, after hold 19's successful action.

One Codex visual reviewer inspected original unmirrored images in cue-aligned
contact sheets without classifier labels or dispatch timestamps shown. For each
attempt, the reviewer bracketed the transition from incompletely formed to
clearly formed pose retained in following frames. G1 is a fist, G2 thumb up, G3
index/middle V. Timing bounds preserve visual transition/settling ambiguity; they
are not statistical confidence intervals or an independent human annotation.
Annotations were saved before matching responses. Percentiles use nearest rank
over the 16 responses; misses are reported separately, never as zero latency.

The timestamps follow camera read, not sensor exposure. Unknown camera buffering
and physical external-application response time are not measured. JPEG storage
overhead is included. These are approximate camera-frame-referenced timings,
not a laboratory measurement of complete physical-to-screen latency.

The private `review/reproduce.py` verifies original hashes, index/trace matching,
runtime/replay agreement, missed attempts and the reported interval arithmetic.
Original run metadata remains unchanged; annotations/results are separate files.
Images, traces and profile data stay local and out of GitHub.

| Original private artifact | SHA-256 |
| --- | --- |
| Timestamped image archive | `ec3ed38ca4cd893e00b71e3eb544bc5d52944c11614bc98d5299cbdaf1b44bae` |
| Image index | `60b82741c9e90bbfe0c17f209f607219e743cdc25b785591d9976f290e90e70e` |

## Four missed attempts and remaining recognition work

| Hold | Pose | Observed blocker |
| --- | --- | --- |
| 1 | G1 | Handedness rejection at frame 83 reset READY to WAIT_NEUTRAL. Later accepted G1 predictions could not activate without fresh neutral. |
| 9 | G3 | Sustained ambiguity rejection exceeded the 0.5 s grace at frame 1185; most later G3 inputs were still rejected. |
| 12 | G3 | Sustained classifier rejection exceeded grace at frame 1624; later accepted G3 remained blocked pending neutral. |
| 18 | G3 | Rejection interval exceeded grace at frame 2477, requiring neutral despite the newly accepted G3 input. |

All four had reached READY before the transition. Replay reproduces the runtime;
this demonstrates a recognition/transition limitation with expected protection,
not a controller replay mismatch. Autofocus causation and a threshold repair are
not established. Do not weaken rejection or relabel misses to improve results.

**Hau Jie / GF-P21:** review these four saved transitions and the selected profile,
identify any narrowly affected check needed, and reconcile the recognition report.
Do not restart P02 experiments, collect new participants or repeat the whole
Practice protocol. Deston can proceed with methods/results and demo preparation;
the report/demo must retain this limitation and the manual approval mode used.

See [current progress](PROGRESS.md), [team tasks](TEAM_GUIDE.md) and the
[workflow protocol](WORKFLOW_COMPARISON.md).
