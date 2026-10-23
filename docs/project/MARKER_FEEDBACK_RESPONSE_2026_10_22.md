# Marker feedback and project response — 22 October 2026

Source: the two-page `ICT304_A1_Feedback_Group_GestureForge_Wong.pdf` supplied
by Deston. Both pages were read and visually reviewed. The marker awarded
**83/100**: lifecycle 9/10, requirements 26/30, techniques 17/20, prototype 14/20,
innovation 8/10 and writing 9/10. Those are the earlier assessment's results,
not a forecast of the project's mark. Preserve the original submission and
feedback unchanged. The project rubric remains the one in [the plan](PROJECT_PLAN.md).
Feedback SHA256: `b4f76c7fcc13bfa04c6a954a4e3289b3140e22dfd91a4bcd7c95d8d37a3e6cd4`.

## The problem and the proposed product

A trainer presenting a mixed-resource demonstration repeatedly returns to the
keyboard to find reference material, open tools and recover their place after
interruptions. GestureForge proposes a reusable runbook that keeps the current
step and action meanings visible, offers personal gestures alongside manual
controls, and restores progress without replaying launches. The presenter is the
primary user; the walkthrough author is the secondary user.

This is a testable problem statement. Existing team experience and the fictional
Harbor scenario do not establish customer demand. On 23 October Deston chose
[published secondary research](RESEARCH_POSITIONING_2026_10_23.md) instead of
the suggested trainer interviews. This strengthens problem justification while
leaving direct stakeholder elicitation unperformed. A clicker
is a sensible simpler alternative for slide-only work. The proposed distinction
is the combination of authored stages, personal input, local resources, rehearsal
and recoverable execution; it is not a claim to have invented gesture control.

## Changes against the feedback

| Marker finding | Change now | Evidence still needed |
|---|---|---|
| Requirements lacked measurable pass/fail conditions; quantitative goals largely deferred | All 17 active requirements now have operational checks in [plan section 5](PROJECT_PLAN.md#operational-passfail-rules--clarified-22-october), tied to existing tests and physical records. Existing recognition/latency/false-action targets are retained. | Execute every requirement's physical cases on the identified release. Tests passing does not establish usability or device operation. |
| One presenter persona/participant, little stakeholder elicitation | The [secondary-research review](RESEARCH_POSITIONING_2026_10_23.md) examines six research papers and seven official alternatives pages and maps needs to requirements. It replaces the proposed interviews at Deston's request on 23 October. | Direct elicitation was not conducted. Keep this limitation visible; actual workflow observations still determine product usefulness. Published findings do not prove customer demand. |
| Report claimed P01 data was included, but submitted ZIP lacked it | Read-only inspection confirms the 83-member submitted ZIP lacks the P01 manifest/sidecar. The existing packaging tool now checks declared evaluation inputs **inside the finished ZIP**, including CRC, safe paths and feature hashes. | Build the permitted project evidence package, check every claimed configuration, then reproduce the reported outputs from its extracted contents. Input integrity alone is insufficient. |
| Live evidence was a participant-reported smoke check, with no measured latency/false-action run | Keep software, offline recognition and physical results separate. The frozen comparison and failed targets remain visible; new teammate exports are reconciled with their actual build and source limits. | Genuine full Practice, timed holds/negative activity, same-stream replay and the observed six-stage workflow under the existing protocol. |
| No measured advantage over a clicker; integration of existing components | Explain where a clicker/manual control is preferable. Evaluate manual versus gesture operation of the **same** mixed-resource task, counting setup cost, time, errors, retries and help. | Recorded comparison and honest interpretation, including a result of no advantage. The manual baseline is not an actual clicker trial. |
| Hosted CI had not run and private repository limited access | Continue local verification with retained command output, versions and source/package hashes. Supply runnable source/evidence privately to the marker; the repository is not the only access route. | Fresh guide-only install and evaluation from the selected package. Do not label manual/local checks as successful GitHub Actions runs. |
| Report was dense, table-heavy, and packaging statement inaccurate | Put the problem, rationale and conclusions in prose; reserve tables for requirements and results. Keep detailed receipts in the evidence matrix and correct packaging claims. Refresh the local Word report and matrix. | Final page-by-page review, citation/figure checks and reconciliation against the actual package. |
| Declaration had six unchecked confirmations and generic member roles | Keep actual PR/module/report contributions for Deston, Hau Jie and Javier. Do not reuse the two-person 60/40 allocation or tick declarations on their behalf. | The three members complete the current declaration and agreed contribution details truthfully before submission. |

The marker credited the lifecycle, stable interfaces, leakage-aware comparison
and explanation of pretrained landmarks. Preserve those strengths. More unrelated
features would not remedy these evidence gaps.

## Finished-package check

Use the existing tool with the exact ZIP intended for handoff, and repeat
`--require-config` for every evaluation configuration whose results the report
claims can be reproduced. Paths are relative to the project folder inside the ZIP.
For example, the already-permitted private P01 package can be checked with:

```powershell
.\.venv\Scripts\python.exe scripts/package_release.py --verify-archive releases/gestureforge-assignment-private-marker.zip --require-config experiments/pilot-rejection.json
```

The preserved submitted archive uses the prefix `ICT304_Assignment/gestureforge/`;
checking it with `--archive-root ICT304_Assignment/gestureforge/` correctly reports
the missing P01 manifest. The source-only Studio ZIP is a development handoff,
not a complete private evaluation submission. Do not rename it and claim that
private datasets are included.

On 22 October the retained private P01 archive passed both `experiments/pilot.json`
and `experiments/pilot-rejection.json`; its SHA256 is
`75bb42adc310ee4d3fb48eba56b475b58e520e4a669130da9f8e00fed5064727`.
This successful check does not alter the fact that a different, incomplete ZIP
was submitted earlier. Neither archive was changed by the check.

This check reads files without extracting or executing archived code. It verifies
declared numeric input presence, archive CRC and feature-sidecar hashes; it does
not run evaluation, validate every dataset record, infer consent or check report,
video and declaration completeness. Run the existing evaluator after safe
extraction in the release verification environment and compare all non-timing
results. Retain the package hash and output, then repeat the checks on the LMS
download. Keep participant files out of GitHub. H1's internal-team handoff is
not permission to redistribute that data to a marker or to bundle a starter.

## What the new private receipts establish

The [22 October deliverable review](TEAM_DELIVERABLE_REVIEW_2026_10_22.md) now
includes both supporting packets. Javier's 42 payload hashes and laptop B's 25
payload hashes match. The supplied before/after exports validate separate result
revisions and empty post-restore counters. They are manual demonstration evidence,
not an eligible gesture workflow or proof of external task completion.

Laptop B's assisted install, native target requests and explicit missing-file
retry are supported. Its 791.605-second monitor and later human-reported
30-minute interval are different runs; do not combine them. Current gaps are
native association handling, eligible active-capture Camera/focus recovery,
guide-only installation, continuous measured stability and post-close release.
There is no need to resend the received exports or repeat unchanged passing cases.

No remaining whole task meets all original criteria through these receipts alone.
Accepted work stays **137/223 (61.4%), 17/29 tasks**. The release decision must
remain separate from experimental completion: the frozen TEST comparison is
complete, but failed recognition targets do not approve a deployment model.
