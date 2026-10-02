# GF-P06 profile persistence: integration handoff

2 October 2026. Hau Jie implementation; Deston review/integration.
Scope: R01 private profile storage and candidate reconstruction. This is a GF-P06
component slice, not completion of the guest starter, profile UI or live readiness.
No other owner's modules have been changed.

## Implemented API

`gestureforge.profiles.ProfileStore(root)` operates on a private local directory,
normally `.local/profiles`. Constructing an empty store or listing it does not
create files, open a camera, load a model or require an account.

| Operation | Result and safety rule |
|---|---|
| `list_ids()` | Sorted opaque IDs; listing is not proof that files/models are valid. |
| `read(id)` | Validated immutable metadata; does not train or change UI state. |
| `create(name, dataset_path, hand, consent=True, ...)` | Validate the dataset, train a candidate, atomically save metadata; return `LoadedProfile`. Explicit consent confirms already obtained internal-use permission, not distribution permission. |
| `load(id)` | Validate metadata and referenced numeric data; rebuild and verify the exact model revision before returning a candidate. |
| `rename(id, name)` | Atomic cosmetic change; returns updated metadata without changing model revision. |
| `delete(id)` | Remove only that profile's JSON settings. Never recursively delete folders or delete the source dataset. |

Two profiles may reference the same source without one deleting the other's data.
IDs are generated UUID hex strings, not names/paths. Duplicate display names are
allowed and do not overwrite another profile. Names allow Unicode, up to 80
characters. Deletion removes settings permanently; original numeric data is kept.
The UI must explain this and confirm deletion before invoking the API.

The caller serializes metadata writes on its owner thread. This is not a
multi-process database or a portable profile export format. Keep the store private
and out of Git; it contains local paths and participant-derived model references.

## Stored schema and reconstruction

Profile schema version 1 stores:

- profile ID, display name and selected Left/Right hand;
- versioned four-label vocabulary and separate per-gesture display names;
- absolute local numeric manifest reference and manifest/sidecar SHA-256 hashes;
- feature version, immutable model revision and validated algorithm/rejection settings.

The named preset `prototype-default-v1` uses existing kNN (k=5, distance weights)
or RBF SVM (C=1, gamma=scale). Multiplier and margin are configurable finite values
with the same limits as the current recogniser. Broader parameter search belongs
to later recognition evaluation; this API does not claim tuned parameters.

No pickle/joblib, saved executable estimator, raw video, binding map or external
action target is accepted. Legacy schema-1 and custom-vocabulary schema-2 datasets
are supported. Only one participant with human provenance and matching hand is
accepted. Invalid detection records with no hand remain legal; valid feature rows
must have the selected hand. Missing classes/trials, non-finite or degenerate
features and conflicting identity/splits are rejected by the profile/data/model
validation chain. Only valid TRAIN records fit the scaler/classifier and calibrate
training-trial-separated rejection; other sessions are never used to fit.

Reconstruction binds the existing data/settings/library-dependent model revision
to selected hand and exact source hashes. The returned model's `model_version` and
`config.model_version` both match the saved profile. A changed/missing dataset,
modified settings or incompatible library/model revision fails rather than silently
retraining the active selection. Preserve the original source files. Explicitly
create a new reviewed profile after intentional data/configuration changes; do not
hand-edit the saved hashes. Cosmetic profile/gesture names are not model identity.

JSON reads reject duplicate keys, unsupported versions, extra fields and files
larger than 16 KiB. Saves use the existing reviewed atomic storage helper (temporary
file, flush/fsync, replace). Failure before replacement retains the previous file;
temporary files are cleaned up. No active shell state is stored in this component.

## Shell integration proposal (no shell edits in this PR)

`LoadedProfile` contains `record`, rebuilt `model` and a `selection` property
returning the shared `ProfileSelection` fields. `readiness_revision` is empty with
an explicit not-verified reason. Loading a profile never certifies readiness.

1. Pause the existing Studio session before selecting/creating/deleting a profile.
   Respect `Window.pause()` returning false if its evaluation trace could not save.
2. Run expensive `store.load(id)`/creation in the existing model-loading workflow,
   off the GUI thread. No second camera or independent application shell is needed.
3. On success, pass the complete candidate on the GUI thread:

   ```python
   candidate = store.load(profile_id)  # worker; candidate only, not UI mutation
   selection = candidate.selection
   window.use_studio_model(candidate.model, selection.selected_hand,
                           selection.profile_id, selection.vocabulary)
   ```

4. Catch storage/validation/training errors and leave the previous selection/model
   paused. Installation can itself fail, including trace-save failure; only update
   the visible selected name after `use_studio_model` succeeds. Ignore stale results
   after close/new selection/deletion using the shell's existing lifecycle rules.
5. Successful installation remains Preview/paused; explicit Start and NEUTRAL are
   required. Rehearsal/behaviour readiness and LIVE authorization remain separate.
6. After deleting an active profile, clear its active selection/model through the
   shell's agreed integration path; do not leave its in-memory model silently active.
   This component deliberately cannot manipulate the shell or camera.

Display `selection.display_name` separately from the opaque ID. Read failures should
identify the unusable entry without hiding other saved profiles. Readiness must
later be bound to hand/model/controller/bindings, not inferred from a successful
load. Cosmetic rename alone must not invalidate a still-matching readiness record.

## Verification and remaining acceptance

The 46 generated-fixture tests cover legacy/custom vocabulary, both algorithms,
both hands, Unicode names, model reconstruction, independent profiles/deletion,
train-only scaling, invalid input/version/hash/identity, missing/changed data,
settings tampering, duplicate/oversized JSON, refused pickle paths, failed atomic
create/rename/delete, generated-ID collision and no-data listing.

A software-only Studio adapter test installs a real rebuilt classifier with custom
labels, then verifies a failed profile load retains the previous model in paused
Preview with no camera worker. Synthetic fixtures demonstrate implementation only;
they do not establish personal accuracy, physical-hand compliance or readiness.

No personal data was modified or copied into Git. No new participant capture,
visible profile workflow recording or fresh-machine test was performed. The
profile/enrolment widgets and GUI integration remain to be built/reviewed. Guest
starter selection remains gated by GF-P28's failed rejection evaluation and
distribution permission; no ready starter is supplied. GF-P06 must not be marked
Done based only on this persistence slice.

Actual local checks on 2 October, using the existing Python 3.11 environment and
`PYTHONPATH` pointing to this checkout:

```text
python -m pytest -q tests/test_profiles.py
46 passed in 9.61s
python -m pytest -q
392 passed, 1 skipped in 80.19s
python -m ruff check gestureforge tests scripts
All checks passed!
python -m mypy gestureforge scripts tests
Success: no issues found in 54 source files
python -m gestureforge --smoke-test
exit 0
python -m gestureforge --studio --smoke-test
exit 0
```
