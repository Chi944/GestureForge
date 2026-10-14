# H2 evaluation selection — 14 October 2026

This records Deston's review decision after inspecting development results and
before collecting or opening final TEST. It is not a claim that this ranking was
predeclared before development, that a deployment model qualified, or that LIVE
gestures are approved. The [reproduction review](H2_DEVELOPMENT_DIAGNOSIS_2026_10_14.md)
preserves the unsuccessful baselines and bounded comparisons.

## Selected comparison

Retain Hau Jie's proposed personal settings for the paired offline experiment.
Among the 24 examined development settings per participant, each proposal attains
the highest trial macro-F1 among rows with the lowest observed negative-command
sample count. Both checks remain enabled; no performance target is lowered.

| Role | Algorithm and settings | Development evidence and interpretation |
|---|---|---|
| Fixed starter comparator | kNN, k=5, distance weights; multiplier 1.5, margin 1.0 | Original H1 P01/P02/P03 inputs only. Historical person-separated comparisons found no qualifying starter; retain this as the fixed experimental baseline |
| P67 personal comparator | kNN, k=5, distance weights; multiplier 2.5, margin 1.75 | 36/48 correct trials, macro-F1 0.790, 12/40 negative command samples. Retains the established kNN choice where candidate aggregate outcomes tie |
| P1543 personal comparator | RBF SVM, C=1, gamma=scale; multiplier 2.5, margin 1.25 | 26/48 correct trials, macro-F1 0.667, 10/40 negative command samples. Retains Hau Jie's SVM proposal; equivalent aggregate kNN results and the single-run timing advantage are disclosed below |

At the proposed P1543 settings, kNN and SVM tie on accepted trial and negative
sample counts. The saved SVM prediction time is approximately 0.36 ms/sample
against 4.64 ms/sample for kNN. This is one development timing run, not a robust
hardware benchmark or evidence of superior recognition. Keeping the proposed
SVM supplies a reproducible experimental choice; it does not attribute an
unstated rationale to Hau Jie. Preserve both algorithms' results in the report.

The original targets remain personal macro-F1 >=0.90 and starter >=0.85 per
held-out person under stated conditions. Both personal candidates currently
fall short, and all examined settings accepted some negative command samples.
Those counts are classifier predictions, not measured live false actions.
No historical failed fold becomes a selected qualifying outer model. Final TEST
will report success or failure without further tuning on its results.

## Provenance and acquisition decision

- Starter fitting/tuning excludes P67 and P1543. Personal development uses only
  the respective participant. All nine H1 input manifests and each complete
  personal development manifest are included in the private proposal; only
  TRAIN features fit the classifiers.
- The user confirmed on 14 October that P1543 was excluded from earlier starter
  fitting/tuning and took a break before VALIDATION. P67's corresponding facts
  were already confirmed at intake.
- The user confirmed the original H1 right-hand mappings: open palm NEUTRAL,
  fist NEXT, thumb up PREVIOUS, index/middle fingers BOOKMARK. This is an
  attributed physical-pose assertion for legacy manifests, not something
  established by the landmark arrays alone.
- Retain the personal development acquisition convention for TEST: the same
  pinned browser MediaPipe runtime/model, unmirrored right-hand inference,
  mirrored preview, world landmarks and five scheduled samples per trial.
  Record 12 new trials of each of the four poses in a separate TEST session.
  Both comparators must receive these identical observations.
- A participant-specific browser TEST package must bind its returns to the
  reviewed frozen configuration. No development return may be renamed,
  repartitioned or imported as TEST. Record actual session conditions and retain
  invalid slots and partial attempts.

The mixed native-starter/browser-personal acquisition does not establish
browser/native equivalence. Generic development-condition notes limit causal
interpretation. Record both limitations in the final comparison. P69 remains
closed TRAIN-only and outside this experiment, with no further recording asked.

## Acceptance boundary

The original GF-P17 criterion at project-baseline commit `223c8c3` is
"Person-separated starter development; independent final participants and
frozen personal configs." The original GF-P18 criterion is "Same standard-pose
test trials compare frozen starter and personal models; UNKNOWN included."

The reviewed configuration freezes and browser acquisition route are now
verified, so GF-P17 is accepted as experiment preparation. GF-P18 still requires
both real untouched TEST returns, reproducible scores and interpretation.
GF-P10/R15 deployment and integrated live/release checks remain open. Software
checks and poor experimental results cannot grant a successful starter release.

## Freeze and acceptance receipt

On 14 October Deston created two new private frozen comparison files after the
selection review. Independent checks verified their integrity, settings and all
ten manifest/sidecar pairs per comparison. Starter inputs contain P01/P02/P03;
each personal input contains only its named participant. No pinned manifest
contains TEST. The configuration fingerprints are:

| Participant | Frozen configuration fingerprint |
|---|---|
| P67 | `6d8fed34f03f0ba9f094add9c27f47e42d891903e7ea9a370dc379bbd5c1bf1f` |
| P1543 | `23fb7a3697e2d36a8bae0147c55d1c96c798653b3884940ee0fd6d8f90a4a696` |

The frozen files, complete receipt and four Windows/macOS kits remain local.
Each kit contains only the bundled recorder, PDF instructions and notices; its
public ticket pins the participant and freeze without private input paths,
training data or model settings. All four ZIP hashes/CRCs matched. Each PDF was
rendered and visually checked. A camera-free browser inspection confirmed the
locked target, TEST-only selector and 48-trial total on the extracted P67 page.

The final verification passed 952 Python tests, 30 JavaScript checks, Ruff, mypy,
both application startup checks and synthetic evaluation. One unsupported
Windows symlink fixture was skipped. The browser-generated synthetic return
also passed import and paired scoring, retaining five invalid slots as misses;
it is not participant evidence. Independent source and acceptance reviews found
no blockers. This closes GF-P17's original preparation criterion, adding its
unchanged 12-hour weight to Hau Jie and the team.

Packages were built from the reviewed working tree on `8204c6d`; their private
receipts retain the exact collector/source hashes and dirty-build status.
No kit is claimed distributed. An extracted-file camera, pause/recovery and
return-export check on the intended devices remains before distribution. These
physical checks and honest future TEST chronology cannot be proved by hashes.
No actual TEST has been opened, collected or scored. See [PROGRESS.md](PROGRESS.md)
for current completion and the remaining independent evaluation and LIVE gates.
