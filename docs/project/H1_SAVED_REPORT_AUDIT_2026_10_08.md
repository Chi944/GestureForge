# H1 / GF-P17 preparation: saved-report D1 audit

8 October 2026. Hau Jie, with coding-assistant analysis. Reviewer: Deston.
Audit base/source: `9c438137cf4374151e184045bfa231c75f6d1976`.
This is descriptive reconciliation of existing private evidence, not a new fit,
parameter search, collection, final independent evaluation or release approval.

## 14 October: private handoff received and verified

Deston received `PRIVATE_H1_SEND_TO_DESTON_v2.zip` from Hau Jie. The original
archive is 387,438 bytes, SHA256
`3ede6e525cd72fe48d5de887d335c1f9fefd55fc3a53cf9440c548312f7c1003`.
Local receipt checks on `626e5ec` validated CRCs, safe member paths and all 33
file checksums before extracting 3,042,396 bytes into ignored local storage.
No supplied script was executed.

The existing dataset loader validated all nine manifest/NPZ pairs; their hashes
and counts match both result reports and the audit inventory. All 216 trials
and 1,080 scheduled slots remain present: 1,064 valid features and 16 invalid
slots. The existing diagnosis reader reproduces the full saved six-fold content,
and the ten fixed cases match the original collection records and saved
predictions. Each fold's 48 candidate summaries retains the declared grid,
person separation and qualification decision; none qualifies, and no outer
model was selected. The baseline summaries match the original fixed report.

This independently verifies receipt and saved-report consistency, **not a
refit or repeated parameter search**. The historical fitting commit remains
unidentified; recording conditions were not independently observed. Permission
notes support internal team use only and do not establish a new marker, public
package or GitHub distribution grant. The private receipt record is kept with
the extracted packet outside Git.

H1's private handoff is complete. The [current goal and progress table](PROGRESS.md#current-goal-and-handoff-progress--14-october)
now directs H2 diagnosis, eligible participant provenance and reviewed settings
before freeze and untouched TEST. The older H2 recruitment notes inside the
packet are historical; use the current team briefs. GF-P17/GF-P18 and accepted
task weights remain unchanged. The original 8 October audit follows below.

## Inputs and integrity

The private regenerated baseline, saved diagnosis and bounded comparison were
located. The diagnosis's `source_report_sha256` matches the baseline; rebuilding
with the existing `starter_diagnose.diagnose` reader reproduces its full content.
Both result reports declare identical input hashes. All nine original manifests
and their referenced NPZ sidecars match those hashes and load through the existing
dataset reader. Obsolete sidecars/backups and the later P03 version are excluded.
All inputs retain standard legacy IDs, Right hand and feature version 1.

Exact report identities:

| Existing private report | SHA256 |
|---|---|
| Fixed baseline | `5369cb5f45a0c72c993a87178502176323c7ab480c57427de4f13a881a056969` |
| Matching saved diagnosis | `539808a7728c878a8533869b50605af9a280f35d88f4642ed557e9bbb9898157` |
| 48-candidate comparison | `1866f040a9426871f4182e06f9435c26f09ce17185d350f7761c1f15ca33f315` |

Private inventory includes per-file checksums, original manifest/session metadata,
pose/provenance and internal-use permission notes. Each contributor has 320
positive and 40 negative scheduled slots. Invalid positives are 1/4/0 and invalid
negatives 0/1/10 for P01/P02/P03 respectively; these records are retained.
The original fitting runtime records NumPy 2.4.6 and scikit-learn 1.9.1.
The historical evaluator commit is not embedded in saved JSON; the audit source
must not be presented as that original fitting source.

## Six-fold reconciliation

The existing reader checked five-slot voting, 64 positive trials, eight negative
trials, confusion matrices, declared fitting identities and outcome counts for
each of six folds. Held-out people are excluded from fitting. These contributors
previously informed development, so this is not new independent TEST.

| Person/model | Positive sample rejections | Accepted wrong positive samples | Invalid positive slots | UNKNOWN rejected / neutral / action / invalid |
|---|---:|---:|---:|---|
| P01 kNN | 0 | 93 | 1 | 0 / 0 / 40 / 0 |
| P01 SVM | 0 | 82 | 1 | 0 / 1 / 39 / 0 |
| P02 kNN | 165 | 47 | 4 | 20 / 7 / 12 / 1 |
| P02 SVM | 165 | 47 | 4 | 20 / 7 / 12 / 1 |
| P03 kNN | 0 | 31 | 0 | 0 / 0 / 30 / 10 |
| P03 SVM | 0 | 0 | 0 | 0 / 0 / 30 / 10 |

Per D1's larger-category rule, P01 and P03 kNN prioritize accepted wrong
positives; P02 prioritizes genuine-positive rejection. P03 SVM has neither
positive failure category (0/0 tie), but its UNKNOWN action acceptance remains
an unresolved rejection problem. These are sample classifications, not executed
controller actions. NEUTRAL trial outcomes reproduce the published baseline:
P01 1/16 and 0/16 correct, P02 5/16 under both, P03 10/16 and 16/16.

## Fixed cases and notes

All ten preregistered conditions exist. For each person/model/condition the
lexicographically first qualifying trial was selected, retaining its five raw
and scored labels, acceptance, reasons and available distances/thresholds.
Selected trials also match the five records in the checksum-matched manifests.
Exact trial IDs and rows remain only in the private audit.

| Fixed condition | Cases reviewed | Evidence-backed observation |
|---|---:|---|
| P01 NEUTRAL voted PREVIOUS, kNN/SVM | 2 | Accepted wrong-class samples; physical pose compliance unknown. |
| P02 genuine positive voted UNKNOWN, kNN/SVM | 2 | All five slots in each selected case have distance rejection. |
| P03 NEUTRAL voted NEXT, kNN | 1 | Accepted wrong-class samples; physical cause unknown. |
| P01/P03 UNKNOWN with accepted action, kNN/SVM | 4 | Valid features accepted as action labels, not classifier rejection. |
| P03 UNKNOWN with no valid features, kNN | 1 | Five no_hand slots; detection failure, not successful unfamiliar-pose rejection. |

Available general collection notes, session conditions and declared labels were
reviewed. They do not independently establish actual intended pose, orientation,
distance or lighting for the selected slots. P03 import notes attribute the last
two invalid negative trials to attempted pinch detection; this remains an
operator/import note, not proof of classifier rejection. No explicit protocol
contradiction supports a collection-defect finding. All cases retain a physical
cause of unknown. Neither large distance nor misclassification proves a defect.

## Comparison and decision

The comparison's baseline summary equals the six-fold baseline. Its input snapshot
matches, each outer fold contains the saved 48 rows, and all have zero qualifiers
and no selected outer fit. The best worst-person inner F1 values are
0.4542/0.3535/0.4724, with 19/9/36 valid UNKNOWN action accepts for those rows.
Independent inner preferences disagree in all three folds. No search was rerun.

**Return D1 for review with unresolved physical cause; keep starter approval
empty.** No training data, model settings, features or thresholds changed.
A testable hypothesis for a later reviewed versioned development protocol is
orientation sensitivity: the current wrist-relative/scale normalization does not
explicitly align rotation. This is not a causal finding or authorization to
launch another grid. Original records and failures stay unchanged.

H2: Hau Jie reports two willing prospective participants, both using Windows,
with no collection yet. Individual explicit consent and exclusion from prior
fitting/tuning still require confirmation. No development recordings,
configuration freeze or TEST are claimed. Existing
P01/P02/P03 cannot be relabelled as unseen participants. Final distribution
permission is separate from the documented internal-use scope.

## Delivery and checks

Only this aggregate document is intended for Git. The local private packet
contains unchanged report bytes, nine manifest/NPZ pairs, notes, checksums, the
fixed-case audit and its descriptive reader. ZIP CRC and every archived member
SHA256 were verified. Packet reference: `H1-20261008`; prepared locally, not sent
by the assistant. Private archive paths, trial IDs and permission records are
not included in this PR.

Checks on the audit source:

- Audit reader: nine inputs, six folds and ten fixed cases reconciled; saved
  diagnosis reproduced, with no estimator fitting.
- Ruff passed; mypy passed for 100 source files; assignment and Studio offscreen
  startup smoke checks passed; Git whitespace check passed.
- Full suite in a fresh Windows temporary directory: 901 passed, one skipped,
  one warning, 114.26 seconds. The warning is the deliberate duplicate-entry ZIP
  rejection test, not a participant-data validation failure.
- Preserve retry history: sandbox/temp access prevented initial test attempts.
  The first unrestricted full run under a fresh OneDrive temporary path had
  899 passed, two failed and one skipped. Failures were a synthetic Practice
  NEUTRAL-arming timeout and WinError 5 replacing a generated paired manifest.
  Both passed on isolated retry in Windows temp; the full Windows-temp rerun
  above passed. Their intermittent cause is not established and no software
  fix or human Practice pass is claimed.

Data-quality skill guidance informed completeness, cross-file consistency and
provenance checks; no new quality-framework dependency was installed.
