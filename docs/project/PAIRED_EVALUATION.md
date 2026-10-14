# Frozen starter versus personal recognition evaluation

GF-P18 compares both recognisers on the same positive TEST trials. GF-P17's
development review and two configuration freezes were accepted on 14 October.
The remaining work is real held-out collection, paired scoring and interpretation.
Software tests do not satisfy the participant criterion or enable LIVE gestures.

## Current GF-P18 next steps

**14 October:** no `EMAIL_THIS_*test*.zip` returns were found in the coordinator's
Downloads or Telegram Desktop folders. Neither participant's TEST has been
opened or scored. Do not repeat TRAIN, VALIDATION, the H1/H2 search or the freeze.
P69 remains closed TRAIN-only and is not involved in this task.

1. **Verify the device route.** Before participant distribution, the coordinator
   checks an extracted kit on the intended OS/browser: camera permission and
   correct view, Right-hand detection, first trial, pause/reload/partial recovery,
   an offline trial, export and import. Record the kit hash, OS/browser versions
   and observed outcome. Keep equipment-check attempts isolated from participant
   evidence; a teammate's hand must never be scored as P67 or P1543. Do not clear
   a participant's real draft or replace their interrupted attempts with a
   clean-looking recording. See the [device check](PARTICIPANT_KITS.md).
2. **Send the assigned kit.** P67 receives `GestureForge_P67_TEST_macOS.zip`;
   P1543 receives `GestureForge_P1543_TEST_macOS.zip`. Windows alternatives exist
   for equipment checks, but do not silently change a participant's acquisition
   convention. Use the same computer/browser as development where possible;
   P1543 used Safari and P67's browser was not recorded. Record the actual browser
   rather than guessing. Each ZIP already contains `READ_FIRST.pdf`.
3. **Participant setup.** Save and unzip the kit, open `START_HERE.html` from
   the extracted folder, check the locked pseudonym, read and agree to consent,
   and enter actual TEST conditions: lighting, background, seated/standing and
   approximate hand-to-camera distance. Do not recover old development data.
4. **Record one new TEST session.** Click **Start Camera**, allow camera access,
   wait for **Right hand detected**, then **Start Selected Session**. Use the
   right hand: open palm = NEUTRAL; fist = NEXT; thumb up = PREVIOUS; index and
   middle fingers = BOOKMARK. Follow the on-screen order through **48/48 trials**
   (12 per pose; 240 scheduled slots). Allow about **5–6 minutes plus setup and
   saving**, based on the programmed timing: three seconds to prepare, two to
   hold and one to relax. Keep the tab visible and the computer awake.
5. **Preserve interruptions.** Pause and export a backup if necessary. Reopen
   the same extracted kit and recover the newest partial return with **Recover
   from a previous return ZIP**. Then use **Start Camera** and **Start Selected
   Session** to continue. Keep interrupted/invalid slots; do not clear the draft,
   delete mistakes, repeat completed trials or change settings to improve results.
6. **Return the downloaded data ZIP.** At 48/48 choose **Export Return ZIP**.
   Send the file below privately to Deston, not the program folder. Include the
   actual OS/browser and any help or interruption. If collection cannot finish,
   send the partial ZIP and explanation; preserve it for diagnosis/recovery.

| Participant | Complete return | Interrupted return |
|---|---|---|
| P67 | `EMAIL_THIS_P67_test.zip` | `EMAIL_THIS_P67_PARTIAL_test.zip` |
| P1543 | `EMAIL_THIS_P1543_test.zip` | `EMAIL_THIS_P1543_PARTIAL_test.zip` |

The local prepared kits and guides are under `.local/participant-test-20261014/`,
in one folder per participant. Their reviewed frozen comparisons are under
`experiments/local/paired-20261014/`. Do not edit or send those frozen files.

**Deston with GPT, after receiving both returns:** validate identity, consent,
acquisition notes, frozen tickets, coverage and chronology; import each against
its matching freeze; reproduce starter/personal scores on identical observations;
review each person's macro-F1, per-class scores, UNKNOWN-inclusive confusion,
paired differences and timings. Preserve poor results without tuning on TEST.
Hau Jie supports provenance/methods; Javier continues the separate device and
workflow checks. Full data and reports remain private.

Acceptance requires both genuine complete TEST returns and reviewed reproducible
results. Failing a recognition target is still a reportable evaluation outcome,
not permission to deploy. GF-P18 adds its original 10-hour weight only after
acceptance: Deston **21.3% → 34.7%**, team **57.0% → 61.4%**. It remains open now.

## Responsibilities and prerequisites

- **Hau Jie:** supply consented development manifests and numeric sidecars,
  chosen hand, exact pose descriptions and settings selected on development data.
  Include every fitting and tuning session, including validation negatives.
- **Deston:** review participant/split separation, freeze each comparison, then
  score each new participant's untouched standard-pose TEST data and review results.
- Keep files beneath `data/local/` and `experiments/local/`. Full reports contain
  local paths and participant trial identities; share them privately.

The starter must exclude the evaluated participant from both fitting and tuning.
Personal development contains only that participant. Both use the same hand,
feature version, vocabulary and declared physical poses. Use one frozen file per
evaluated person. At least two new people are required by the final evaluation
plan; a tool accepting one person's file does not reduce that requirement.

A contributor who stops after TRAIN can still supply development training data.
Preserve the partial import and original split labels; do not divide neighbouring
frames into invented VALIDATION or TEST sessions. Review consent, physical pose
mapping and provenance before pooling data. A fitting-only check establishes
numerical compatibility, not recognition accuracy or rejection performance.
Anyone used in starter fitting or tuning is excluded from that model's unseen-user
evaluation. A closed TRAIN-only contribution does not count as a completed paired
evaluation participant, and no further recording is requested from that person.

Do not tune after inspecting TEST. If a defect forces a development change,
preserve the original result, document the change and arrange fresh held-out
evaluation. Freeze files record input integrity; they cannot prove when a human
first inspected results, consent, omitted tuning data or physical pose equivalence.

## 1. Declare the selected development configuration

For inexperienced remote participants, [PARTICIPANT_KITS.md](PARTICIPANT_KITS.md)
describes offline browser development recording and strict import to the existing
numeric format. Record the browser/runtime/model provenance and collection
conditions. Shared model/feature hashes alone do not establish native/browser
equivalence. Preserve the declared acquisition protocol for the later separate
TEST session; review any runtime change before freezing. Browser kit completion
does not complete the paired evaluation or approve a starter.

Create a local JSON file, for example `experiments/local/P04-paired.json`.
The example below uses the legacy NEXT/PREVIOUS/BOOKMARK/NEUTRAL vocabulary.
Paths, participant, descriptions and settings are **illustrative**, not an approved
starter or measured participant configuration. Replace them with reviewed facts;
add all development manifest paths if sessions are stored separately.

```json
{
  "target_participant": "P04",
  "hand": "Right",
  "pose_set": {
    "id": "standard-v1",
    "descriptions": {
      "NEXT": "Closed fist facing camera",
      "PREVIOUS": "Thumb up facing camera",
      "BOOKMARK": "Index and middle fingers extended",
      "NEUTRAL": "Open palm facing camera"
    }
  },
  "starter": {
    "manifests": ["../../data/local/starter-development/manifest.json"],
    "settings": {
      "algorithm": "knn", "knn_k": 5, "knn_weights": "distance",
      "svm_c": 1.0, "svm_gamma": "scale", "multiplier": 2.0, "margin": 1.5
    }
  },
  "personal": {
    "manifests": ["../../data/local/P04/development/manifest.json"],
    "settings": {
      "algorithm": "knn", "knn_k": 5, "knn_weights": "distance",
      "svm_c": 1.0, "svm_gamma": "scale", "multiplier": 2.0, "margin": 1.5
    }
  }
}
```

For a G1/G2/G3 vocabulary, use those exact description keys and matching schema-2
manifests throughout. The tool does not remap gesture names or reinterpret poses.
Development manifest `pose_set_id`, where present, must match. For older files
without it, the frozen declaration explicitly relies on the operator's assertion;
preserve those original files. New TEST manifests must carry the matching ID.

## 2. Freeze before final testing

```powershell
.\.venv\Scripts\python.exe -m gestureforge.paired_evaluate freeze --config experiments/local/P04-paired.json --output experiments/local/P04-frozen.json
```

Freeze validates development inputs, participant roles, labels and settings, and
pins manifest/sidecar checksums. It does not open final TEST files or select a
better model. Do not edit the frozen file or append to its pinned development
manifests. Existing outputs are never overwritten; choose distinct filenames for
explicitly documented new experiments.

## 3. Collect and score positive TEST

For browser participants, build a **new participant-specific TEST kit** with
`scripts/package_participant.py --frozen experiments/local/P04-frozen.json`,
alongside the usual verified `--assets`, `--model` and separate `--output`
arguments. See [participant kits](PARTICIPANT_KITS.md#separate-frozen-test-kits).
The kit carries a small collection ticket, not the frozen file's private input
paths, training data or model settings. It supports only the Right-hand
`standard-v1` legacy vocabulary, with the four physical poses declared above.

Collect 48 new positive trials (12 per pose, five scheduled slots each). Keep the
same browser runtime/model and physical conventions as development. Use the TEST
guide and a fresh session after freeze; do not relabel any earlier return. Import
the new ZIP with its matching freeze:

```powershell
.\.venv\Scripts\python.exe -m gestureforge.import_participant EMAIL_THIS_P04_test.zip --frozen experiments/local/P04-frozen.json --output data/local/P04/test/manifest.json
```

The importer retains invalid detections and partial attempts. A partial return is
evidence to preserve and recover, not a complete final comparison. Browser TEST
scoring requires the matching ticket and all 48 trials. Drafts and recovery are
isolated from development and other freezes. Ticket hashes guard accidental
mix-ups and altered metadata; they cannot prove consent, honest labels or when a
person first recorded or inspected data.

The native [collection protocol](../DATA_COLLECTION.md#split-rules) remains
available with a separate TEST-only manifest and matching pose ID. Its acquisition
convention must be reviewed separately; do not silently substitute native
collection for a browser-frozen experiment. Keep every scheduled slot and failed
detection. After collection, score the frozen comparison:

```powershell
.\.venv\Scripts\python.exe -m gestureforge.paired_evaluate score --frozen experiments/local/P04-frozen.json --test data/local/P04/test/manifest.json --output experiments/local/P04-paired-results.json
```

Both models fit only TRAIN rows. Validation and negative development rows remain
part of the frozen provenance and leakage checks. Both then receive identical TEST
rows. Each five-slot trial needs at least three agreeing predictions; invalid,
missing or rejected samples contribute UNKNOWN. A genuine gesture rejected as
UNKNOWN counts as a miss, not a removed trial. Entirely absent native trials
cannot be recovered from a manifest: audit the planned twelve trials per label
separately. The browser TEST route checks this prescribed coverage explicitly.

## 4. Review and report

Report each participant separately: trial macro-F1, per-class precision/recall,
confusion including UNKNOWN predictions, paired trial outcomes, personal-minus-
starter macro-F1, model/input revisions, fit and prediction timing. Report failure
to meet the predeclared targets; do not present these scores as general accuracy
on arbitrary people, poses or operating conditions.

This tool evaluates positive recognition only. `validation_negative` cannot stand
in for unseen final unfamiliar poses. It does not measure live false actions,
hold duplicates, action latency, workflow completion, full Practice readiness or
thirty-minute stability. Those remain separate recorded protocols and acceptance
criteria. Synthetic fixture reports are marked as software evidence.
