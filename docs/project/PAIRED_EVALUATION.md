# Frozen starter versus personal recognition evaluation

GF-P18 now has an offline tool for comparing both recognisers on the same
positive TEST trials. It prepares Deston's evaluation work while Hau Jie supplies
GF-P17's consented data and selected configurations. Software tests do not satisfy
the participant evaluation criterion or enable LIVE gestures.

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

Follow the [collection protocol](../DATA_COLLECTION.md#split-rules), using a
separate TEST-only manifest. Keep all scheduled slots and failed detections.
After collection, score the frozen comparison:

```powershell
.\.venv\Scripts\python.exe -m gestureforge.paired_evaluate score --frozen experiments/local/P04-frozen.json --test data/local/P04/test/manifest.json --output experiments/local/P04-paired-results.json
```

Both models fit only TRAIN rows. Validation and negative development rows remain
part of the frozen provenance and leakage checks. Both then receive identical TEST
rows. Each five-slot trial needs at least three agreeing predictions; invalid,
missing or rejected samples contribute UNKNOWN. A genuine gesture rejected as
UNKNOWN counts as a miss, not a removed trial. Entirely absent trials cannot be
recovered from a manifest: audit the planned twelve trials per label separately.

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
