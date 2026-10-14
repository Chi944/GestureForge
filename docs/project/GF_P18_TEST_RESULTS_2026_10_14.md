# Frozen paired TEST results — 14 October 2026

**GF-P18 is accepted as a completed experiment. Recognition targets were not
met for both participants.** This does not approve a deployment starter, personal
LIVE use or final system release.

Deston received the genuine P67 and P1543 returns after the reviewed
[14 October freeze](H2_EVALUATION_SELECTION_2026_10_14.md). Each return was imported
against its matching frozen ticket and scored with the unchanged starter and
personal comparators. Independent recomputation and a second complete fit/score
reproduced every prediction, metric, count, input hash and paired difference.
Fit and prediction timings vary between runs and are not equality checks.

## Intake and method

| Check | P67 | P1543 |
|---|---|---|
| Complete TEST trials | 48; 12 per label | 48; 12 per label |
| Scheduled feature slots | 240 | 240 |
| Valid slots | 237 | 240 |
| Invalid slots retained | 1 missed slot; 2 stale observations | 0 |
| Session conditions | Not provided by participant | Not provided by participant |
| Numeric-data and private team/marker permissions in return | Both recorded | Both recorded |

The recorded retention arrangement is deletion after marking and appeals finish,
with access limited to the team and private marker. Original archives, numeric
data, freezes and full reports remain private and excluded from Git/Trello.

Both returns declare the supplied right-hand `standard-v1` poses and the browser
MediaPipe runtime. Identity, complete coverage, matching tickets, schema, hashes
and consent fields pass intake validation. Neither TEST session nor any exact
valid float32 feature vector overlaps its frozen development inputs. The starter
uses only H1 P01/P02/P03; each personal model fits only that participant's TRAIN.
Prior user-confirmed exclusion and pose provenance are preserved in the selection
record. Numeric checks cannot independently establish physical identity or consent.

Recorded sample times are 14:40:54–14:46:19 UTC for P67 and 14:52:36–14:57:56 UTC
for P1543, later than the approximately 07:48 UTC local freeze records. These
client timestamps support the declared sequence; they are not trusted-clock proof.
OS/browser versions, assistance and interruptions were not supplied with these
returns. Earlier development device reports do not establish those TEST details.

Each classifier receives the identical scheduled observations. Each five-slot
trial needs at least three agreeing predictions; otherwise it becomes UNKNOWN.
Invalid and rejected samples stay UNKNOWN. Macro-F1 averages the four enrolled
classes; UNKNOWN predictions count as misses rather than removed trials. There
was no threshold change, candidate search, exclusion of failed trials or model
selection after opening TEST.

## Results

| Participant | Comparator | Trial macro-F1 | Correct / 48 | Wrong enrolled label / 48 | UNKNOWN / 48 | Predeclared target |
|---|---|---:|---:|---:|---:|---|
| P67 | Starter | 0.768651 | 38 | 8 | 2 | Below 0.85 |
| P67 | Personal | 0.718261 | 34 | 1 | 13 | Below 0.90 |
| P1543 | Starter | 0.979130 | 47 | 1 | 0 | Meets 0.85 for this person |
| P1543 | Personal | 0.397059 | 13 | 1 | 34 | Below 0.90 |

Personal minus starter macro-F1 is **−0.050390 for P67** and **−0.582072 for
P1543**. Personalisation did not improve recognition in this experiment. The
starter performed better on both positive sets, but failed the per-person target
for P67. One successful participant does not qualify it as a general starter.

The personal models rejected **all 12 NEXT trials for each participant**. In P67,
the starter recognises only three NEXT trials and confuses seven with other
commands. In P1543, the personal model rejects many other poses and predicts NEXT
for one NEUTRAL trial. These are offline classifier outcomes, not executed actions.

### Confusion counts

Rows are intended poses; columns are predicted labels. Every row contains 12
trials. P/R are per-class precision and recall; the full private reports retain
all sample and trial predictions.

| Comparator | Intended | NEXT | PREVIOUS | BOOKMARK | NEUTRAL | UNKNOWN | P | R |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| P67 starter | NEXT | 3 | 2 | 5 | 0 | 2 | 1.000 | 0.250 |
| P67 starter | PREVIOUS | 0 | 12 | 0 | 0 | 0 | 0.800 | 1.000 |
| P67 starter | BOOKMARK | 0 | 1 | 11 | 0 | 0 | 0.688 | 0.917 |
| P67 starter | NEUTRAL | 0 | 0 | 0 | 12 | 0 | 1.000 | 1.000 |
| P67 personal | NEXT | 0 | 0 | 0 | 0 | 12 | 0.000 | 0.000 |
| P67 personal | PREVIOUS | 0 | 12 | 0 | 0 | 0 | 0.923 | 1.000 |
| P67 personal | BOOKMARK | 0 | 1 | 11 | 0 | 0 | 1.000 | 0.917 |
| P67 personal | NEUTRAL | 0 | 0 | 0 | 11 | 1 | 1.000 | 0.917 |
| P1543 starter | NEXT | 11 | 0 | 0 | 1 | 0 | 1.000 | 0.917 |
| P1543 starter | PREVIOUS | 0 | 12 | 0 | 0 | 0 | 1.000 | 1.000 |
| P1543 starter | BOOKMARK | 0 | 0 | 12 | 0 | 0 | 1.000 | 1.000 |
| P1543 starter | NEUTRAL | 0 | 0 | 0 | 12 | 0 | 0.923 | 1.000 |
| P1543 personal | NEXT | 0 | 0 | 0 | 0 | 12 | 0.000 | 0.000 |
| P1543 personal | PREVIOUS | 0 | 5 | 0 | 0 | 7 | 1.000 | 0.417 |
| P1543 personal | BOOKMARK | 0 | 0 | 4 | 0 | 8 | 1.000 | 0.333 |
| P1543 personal | NEUTRAL | 1 | 0 | 0 | 4 | 7 | 1.000 | 0.333 |

Sample-level UNKNOWN counts are 4/240 (P67 starter), 64/240 (P67 personal),
0/240 (P1543 starter) and 168/240 (P1543 personal). P67's counts include the three
invalid slots. Sample counts and majority trial counts are different units.

First-run fit times range from 0.028 to 0.244 seconds, below the 60-second target.
Batch prediction averages range from 2.67 to 4.84 milliseconds per scheduled
sample on the coordinator's machine. These are single-run offline timings, not
camera/controller action latency or a participant-device benchmark.

## Reproduction and integrity

Scoring source: `7ac187c570df1de5a778b829da070c1c3bdfd0ac`. The private intake receipt
records dependencies, exact paths, all input/output hashes and timing metadata.
The original Downloads files are untouched; their preserved copies match:

| Return | SHA-256 |
|---|---|
| `EMAIL_THIS_P67_test.zip` | `5918fbccfb777b538d009bffa1b9c622cc138b433e972a857763e5c30e4eb349` |
| `EMAIL_THIS_P1543_test.zip` | `98909df1d38145b45684cec648b0ddbfc596f9248e3b27e9917192f8432b521c` |

Private inputs live in `data/local/participant-test-20261014/<participant>/`;
freezes in `experiments/local/paired-20261014/`; original score reports, independent repeat
reports and `intake-receipt.json` in `experiments/local/paired-test-20261014/`.
No private inputs are bundled with this public aggregate record.

With authorised private inputs present, reproduce into a new output name:

```powershell
$env:OPENBLAS_NUM_THREADS='1'
$env:OMP_NUM_THREADS='1'
.\.venv\Scripts\python.exe -m gestureforge.paired_evaluate score --frozen experiments/local/paired-20261014/P67-frozen.json --test data/local/participant-test-20261014/P67/manifest.json --output experiments/local/paired-test-20261014/P67-another-review.json
.\.venv\Scripts\python.exe -m gestureforge.paired_evaluate score --frozen experiments/local/paired-20261014/P1543-frozen.json --test data/local/participant-test-20261014/P1543/manifest.json --output experiments/local/paired-test-20261014/P1543-another-review.json
```

Existing outputs must not be overwritten. Use the [import/scoring protocol](PAIRED_EVALUATION.md)
for a clean reconstruction from the preserved original archives.

## Development-only diagnosis and software verification

A bounded read-only check found no definite label, feature-version or runtime
mismatch between either personal development set and its TEST return. The fitted
class-distance thresholds equal those in the already reproduced selected
DEVELOPMENT models. This does not establish physical pose consistency.

The selected P67 development model already recognised only 2/12 NEXT trials,
with one classified NEUTRAL and nine UNKNOWN; 47/60 NEXT sample slots were margin
rejected. Its 12/40 negative command samples were predicted NEXT. P1543's selected
development model recognised 4/12 NEXT, 4/12 PREVIOUS, 6/12 NEUTRAL and 12/12
BOOKMARK trials. NEXT had 41/60 distance-rejected slots; NEUTRAL had 28/60
margin-rejected slots; 10/40 negative samples were accepted as BOOKMARK.

These saved DEVELOPMENT findings establish a rejection/separation trade-off that
predates TEST. They do not prove a software bug or identify a physical cause.
No new candidates were fitted or thresholds changed for this diagnosis. GF-P21
has started with this diagnosis, but remains unaccepted: Hau Jie must investigate
and address supported defects using development inputs, with GF-P20's later
findings also retained in its acceptance gate.

Fresh verification: **66 importer/paired-evaluator tests passed** on 14 October.
The duplicate-ZIP fixture generated its expected warning. The two independent
real-data re-fits also reproduced the original reports. No runtime source changed
in this evidence update; a new full GUI, lint/type or hardware pass was not needed
for the documentation-only diff.

## Acceptance and next work

GF-P18's original criterion at `223c8c3` is: “Same standard-pose test trials
compare frozen starter and personal models; UNKNOWN included.” Two complete
held-out participants, repeated scores and reviewed interpretation satisfy that
criterion, including the unsuccessful results. Its original 10-hour task weight
is credited to Deston; no task has been reweighted or threshold lowered.

Accepted totals: Deston **26/75 (34.7%)**, Hau Jie **63/75 (84.0%)**, Javier
**48/73 (65.8%)**, team **137/223 (61.4%)**; **17/29 tasks Done**.

- **Hau Jie / GF-P21:** diagnose rejection and pose coverage using DEVELOPMENT
  inputs only. Establish whether there is a reproducible code defect before
  changing implementation. Preserve these TEST baselines. Any revised model
  needs a new freeze and fresh held-out evaluation; these two returns cannot
  become a new untouched TEST or a threshold-selection set.
- **Hau Jie / GF-P24:** use these negative findings, per-class results and limits
  in the private methods/results contribution. No new TEST recording is requested
  from P67/P1543 simply to replace poor scores; P69 remains closed TRAIN-only.
- **Javier + Hau Jie:** continue the remaining native Windows checks and laptop-B
  fresh setup/offline/stability evidence on an identified build.
- **Deston:** retain model/release decisions, review the development diagnosis and
  integrate demonstrated fixes. GF-P20 still needs physical hold, negative,
  latency and workflow evidence after its integration prerequisites.

These two positive TEST sets do not measure unseen unfamiliar poses, live false
actions, duplicate holds, readiness, actual action latency or task completion.
H1 native acquisition versus browser personal acquisition is a limitation, not
proven equivalence. Two people and missing TEST conditions do not establish broad
generalisation. None of those outstanding gates is closed by GF-P18 acceptance.
