# GF-P03: custom vocabulary and legacy import

Hau Jie implementation handoff, 30 September 2026. Base: `cfbe5cbdcc90e68287629aaa4e22d2cdcb829e92`.
Status: implemented locally and awaiting Deston's review. This is not completion of the recognition/profile lane.

## Delivered

- `GestureVocabulary` version 1 validates exactly three distinct canonical action IDs; NEUTRAL is implicit and UNKNOWN cannot be a positive class. It reuses the shared gesture-ID validator.
- Dataset schema 1 remains readable and is still the default write format for existing commands. Explicit vocabulary writes schema 2 with the versioned vocabulary and matching label list. No assignment file is migrated in place.
- Collection accepts `--vocabulary PATH`, preserves an existing schema-2 vocabulary when appending, and rejects a conflicting vocabulary before camera acquisition.
- Training accepts keyword `vocabulary=...`; kNN and SVM retain custom labels and the existing `(label, accepted, reason)` prediction interface. Feature extraction and mirroring/hand conventions are unchanged.
- Project vocabulary-aware training generates a deterministic model revision from training vectors, labels, trial grouping, feature version, classifier settings, rejection settings and library versions. Direct legacy calls without vocabulary retain their previous prototype version strings for compatibility. Integrators must pass the vocabulary even for a legacy-ID project profile to obtain a content-bound revision.
- Evaluation uses the dataset vocabulary for per-class metrics, UNKNOWN misses and negative accepted-command counts. Unexpected metric labels raise errors instead of silently disappearing. Different vocabularies cannot be merged implicitly.

## Integration example

Vocabulary JSON (canonical IDs only; display names belong to the future profile layer):

```json
{"version": 1, "action_ids": ["G1", "CUSTOM_2", "POSE3"]}
```

```python
from gestureforge.dataset import load_dataset
from gestureforge.models import train_model

bundle = load_dataset("data/local/personal")
x, y, records = bundle.training_data()
model = train_model(x, y, vocabulary=bundle.vocabulary,
                    groups=[record.trial_id for record in records])
# Supply model.model_version to a NEW routing session after a model change.
```

Collection retains the existing arguments, with optional `--vocabulary vocabulary.json`.
The evaluator still accepts `python -m gestureforge.evaluate --config CONFIG.json`.
Gesture IDs do not imply NEXT/PREVIOUS/BOOKMARK actions; Deston's shell must validate bindings against the selected vocabulary. No shell, controller, routing, shared contracts or viewer source was edited.

## Actual verification

Executed from the new checkout using Hau Jie's already installed Python 3.11 environment:

```powershell
$testPython = 'C:\Users\hauji\Downloads\GestureForge_304-main\GestureForge_304-main\.venv\Scripts\python.exe'
& $testPython -m ruff check gestureforge tests scripts
# All checks passed!
& $testPython -m mypy gestureforge scripts tests
# Success: no issues found in 34 source files
& $testPython -m pytest -q
# 151 passed in 10.11s
& $testPython -m gestureforge --smoke-test
# Exit 0, no output
& $testPython -m gestureforge --studio --smoke-test
# Exit 0, no output
```

The existing 129 tests passed before adding 22 vocabulary regressions. Regression coverage includes schema-1 import, schema-2 round trip, both classifiers, custom metrics/negatives, malformed/reserved IDs, version mismatch, unknown-positive rejection, split leakage, non-finite data, invalid detection misses, model revision reproduction/invalidation and a mocked collection cue/cancel path. Synthetic data establishes software behaviour only.

No new environment was copied or installed. This does not establish a fresh installation. No camera was opened, no participant performance was measured, and no collection/profile screen recording was produced. The mock collection test is not a physical camera test. The existing one-participant evaluator restriction remains; person-separated starter folds are GF-P28 work.

## Next smallest task

GF-P28: agree explicit collection and redistribution permission with all three members, collect new standard-pose sessions, then implement/run person-separated development evaluation. Existing personal data is not included in this change. Profiles, enrolment widgets and readiness checks remain subsequent tasks, not completed features.
