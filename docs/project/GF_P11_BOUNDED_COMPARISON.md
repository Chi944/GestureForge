# GF-P11 bounded starter comparison — exploratory checkpoint

2 October 2026. Hau Jie. This is an internal development comparison, not a
released starter, final independent test, or measurement of executed actions.
The original fixed-default GF-P28 baseline remains unchanged.

PR #19 supplies this checkpoint. Review repairs reuse one validated input
snapshot for the baseline and candidate fits, preserve unchanged SVM model
revisions, serialize the report before opening its output file, and record
runtime library versions. The private results below remain Hau Jie's reported
measurements; they have not been independently rerun in Deston's checkout.
Current acceptance is tracked in [PROGRESS.md](PROGRESS.md).

## Protocol and reproducibility

`python -m gestureforge.starter_compare --root <private-participant-root>
--output experiments/local/<new-name>.json` validates the same P01/P02/P03
manifests as the baseline evaluator, then runs three outer leave-one-person-out
folds. In each outer fold, the two development people alternate as the sole
fitting person and inner validation person. Both positive sessions of the
fitting person enter the fit; their UNKNOWN trials do not. Scaling and
class-conditional, leave-one-trial-out distance thresholds use fitting samples
only. All five scheduled slots, including invalid detections, remain in trial
votes; invalid detections are not counted as classifier rejections.

The frozen 48-candidate grid is kNN k=3/5/7 with uniform/distance weighting, or
RBF SVM C=0.1/1/10 with gamma=scale/0.1, crossed with rejection multiplier
1.0/1.5 and margin 1.0/1.2. A candidate qualifies only if **each** inner
person has positive-trial macro-F1 at least 0.85 and **zero** valid UNKNOWN
samples accepted as an action. Accepted UNKNOWN-as-NEUTRAL is reported
separately. If several qualify, the fixed ranking is worst inner macro-F1,
then worst valid-UNKNOWN rejection rate, then frozen grid order. Only a
qualifying candidate is refitted on the two development people and scored on
the outer held-out person. No nonqualifying candidate is promoted or scored as
a selected outer model.

The private JSON records the complete grid, per-person inner positive confusion
and UNKNOWN outcomes, selected model settings/revision if any, independent
inner-person preferences, source hashes and the prior baseline summary. The
CLI refuses to overwrite an existing report. It does not save participant
vectors or enable the starter in Studio. Keep the input sidecars and complete
result JSON in ignored local directories; do not attach them to a PR without
separate distribution permission.

## Supplied private internal run

The run on the three consented team datasets completed with **zero qualifying
candidates in all three outer folds**. The two inner people's independently
preferred settings disagreed in all three folds. Consequently no selected
outer model was fitted or scored. These are honest no-selection outcomes, not
three zero-accuracy results.

| Outer person | Candidates qualifying | Best worst-person inner macro-F1 (any candidate) | UNKNOWN action accepts for that candidate, both inner people |
|---|---:|---:|---:|
| P01 | 0/48 | 0.4542 | 19 |
| P02 | 0/48 | 0.3535 | 9 |
| P03 | 0/48 | 0.4724 | 36 |

Only two candidates in P02's development pair accepted zero valid UNKNOWN
samples as actions; their inner macro-F1 pairs were 0.2961/0.0294, far below
0.85. In P01's and P03's development pairs, no candidate achieved zero such
acceptances. The comparison therefore shows a strong recognition/rejection
trade-off in this bounded grid; it does not establish that all other possible
methods would fail.

The fixed-default baseline was regenerated with the current evaluator and
matched the published six-fold counts: P01 kNN/SVM macro-F1 0.6335/0.6563,
P02 0.4509/0.4509, P03 0.9028/1.0000, with valid UNKNOWN action accepts
40/40 and 39/40 for P01, 12/39 for P02, and 30/30 for P03 under both models.
An older saved baseline JSON lacked later-added UNKNOWN trial details and was
not accepted by the strict diagnostic reader; the old file was preserved.
The regenerated report and its diagnostic stay private.

## Interpretation and next gate

The same three contributors' earlier baseline informed this experiment, so
even nested splitting here is exploratory. Two inner people are too few for a
stable universal-starter selection, and this run found no qualifying setting.
Do not load any candidate as a ready starter, claim improved live recognition,
or count these classifier outputs as actual controller actions. A collection
defect has not been established, so blanket recollection is not requested.
The next decision should review specific pose/collection evidence or revise
the method under a new versioned protocol; freeze a candidate before testing
on new independent participants, with controller-based readiness checks still
required. Hau Jie's next delivery work is GF-P07's real enrolment walkthrough
and GF-P12's longer personal rehearsal with negative intervals and targeted
recollection. The shell's short simulated check does not replace that rehearsal
or establish starter readiness.

## Software verification

Hau Jie's publication checkpoint used the existing Windows Python 3.11
environment and his checkout on
`PYTHONPATH`: full pytest **527 passed, 1 skipped**; after the final
model-version guard, focused model/starter tests **27 passed**; Ruff passed;
mypy passed on 65 files; assignment and Studio startup smoke checks returned
exit 0; `git diff --check` passed. Synthetic tests verify split isolation,
invalid-slot accounting, no selection when no candidate qualifies, the frozen
grid and model revision changes. They do not replace the private internal run
or real camera acceptance. The private run completed without errors and its
output was confirmed ignored by Git.
