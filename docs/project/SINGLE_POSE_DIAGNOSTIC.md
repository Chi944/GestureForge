# Single-pose Practice diagnostic

Hau Jie component follow-up, 4 October 2026.

After **Start personal practice**, the embedded Practice widget offers a test
selector before **Prepare next trial**. The default remains the full 50-window
rehearsal. **Test only NEUTRAL**, or another enrolled action ID, selects one
five-second window and displays diagnostic-only scope and a denominator of one.
Selection locks after the first preparation; an existing attempt cannot skip,
replace or discard earlier trials.

The probe uses the host's existing camera handoff, controller, persistent
simulation dispatcher, save/retry and paused context restoration. No shell
attachment changes or new camera worker are needed. For NEUTRAL, wait for fresh
capture, click Begin, then hold the open palm through the timed window. For an
action pose, first earn READY with NEUTRAL, click Begin and show the selected pose.

The recorded trial retains its actual correct/missed/wrong/inconclusive outcome,
coverage and timing diagnostics. Results use the distinct protocol
`gf-p12-single-pose-diagnostic-v1`. Completion closes the existing host attempt
with `status=cancelled` and a diagnostic-complete reason, rather than declaring
a rehearsal pass. The widget displays “diagnostic complete”. The shared host
may still show its generic cancelled/incomplete summary; Deston can refine that
display after review. `passed_for` also requires the full protocol and 50 trials.
This cannot supply full readiness, resume an earlier attempt or combine prior
results into a pass. All result files remain in the existing private output root.

Focused tests cover selected NEUTRAL/action windows, no readiness credit,
selection locking, existing full-protocol behavior, release/result signals and
automatic local saving.

## Physical diagnostic, 4 October

The user selected **Test only NEUTRAL**; this selection did not edit the training
dataset. A saved P02 diagnostic contains one complete five-second NEUTRAL window,
117 consumed frames and adequate capture coverage. Begin was accepted from
WAIT_NEUTRAL with a recent capture; no boundary cancellation was recorded.
The outcome was **missed**, with `neutral_ready=false`, no simulated actions,
57 margin rejections, 2 distance rejections and 7 no-hand observations.
These are observation counts, not separate trials or an accuracy percentage.
The saved result confirms the single-window capture/save path on this laptop.

The user also reported difficulty recognising the pose and a green-progress
display issue after selecting this diagnostic. The aggregate result does not
record the display or the ordered prediction stream, so it cannot establish the
cause of that visual symptom, prove every remaining frame was accepted NEUTRAL,
or diagnose a controller defect. A margin rejection means insufficient class
separation; a distance rejection is feature-space distance, not a measurement
of physical camera distance. Preserve this failure for review before asking for
further targeted evidence or changing data or thresholds.

Deston: review the host's generic cancelled/incomplete presentation for this
distinct diagnostic protocol and the reported green-progress feedback. The
complete window is intentionally saved through the existing terminal lifecycle.
No shared shell/controller code changed. The full 50-window rehearsal remains
incomplete; this diagnostic grants no readiness credit. Earlier GF-P07 Stop and
reload evidence remains in `GF_P07_LOCAL_CAMERA_REVIEW_2026_10_03.md` and need not
be repeated. Private results, traces and datasets are excluded from this handoff.

Local Windows verification: 77 focused tests passed. Full pytest: 676 passed,
1 skipped in 116.18 seconds. Ruff passed; mypy passed for 80 source files.
Both Studio and assignment smoke checks exited 0; diff whitespace checks passed.
