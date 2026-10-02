# GF-P06 profile selector component

2 October 2026. Hau Jie component; Deston owns shell placement and acceptance.
Updated against reviewed main `b542e33`, including enrolment integration and Guest switching.

Publication verification on this base: **512 passed, 1 skipped** (63.97s), Ruff
passed, mypy passed for 63 files, and assignment/Studio startup smoke checks both
exited 0. This includes 16 selector tests and the separate GF-P11 diagnostics.
The Guest round trip and refused/failed switch use the real Studio host with
generated fixtures; no participant or camera evidence is claimed.

## Local behaviour

`gestureforge.profile_widget.ProfileSelectorWidget(store, parent=None, host=None)`
is an embeddable PySide6 widget using the existing `ProfileStore`. It creates a
personal profile from a local numeric manifest with explicit internal-use
permission, selected hand and kNN/SVM settings; lists, loads, renames and deletes
profiles; and provides non-destructive return to manual Guest. New capture belongs to
the separate enrolment component. Private participant datasets were not used.

**Try standard gestures** stays disabled with a visible missing-approved-starter
reason. Successful personal loading does not certify rehearsal or enable LIVE.
Broken metadata remains visible without hiding good entries. Failed personal
loading retains the prior selection and displays the shell/storage error.

Creation fits in a single background worker and saves through `ProfileStore`.
The selector blocks overlapping operations while it is busy. Changing the dataset
path clears the permission checkbox. Cosmetic renaming preserves model revision.
Deletion requires confirmation, preserves numeric source data and other profiles,
and clears a matching active selection only after storage deletion succeeds.

With no host, the widget supports local persistence/candidate testing, including
loading through its local worker. Preview start stays disabled. With a Studio
host, saved-profile loading uses the **existing shell worker**, not a second
reconstruction pipeline. Neither mode opens a camera or dispatches actions.

## Existing shell boundary

Deston can embed the widget during no-model setup:

```python
selector = ProfileSelectorWidget(store, parent=container, host=window)
```

No edits to `app.py`, `__main__.py`, contracts, routing or camera were made for this
component. The supplied host is the current Studio `Window`:

- Saved loading calls `load_studio_profile(store, id)`. The selector observes the
  retained worker result and the host's installed identity/model. It publishes
  the selection only when that exact candidate was installed, not merely because
  a prior profile with the same ID is still selected after a failed reload.
- New creation calls `pause()` before background fitting, then
  `use_studio_profile(candidate)` on the GUI thread. Installation refusal keeps
  the previous selection. The newly saved metadata remains listed for retry.
- Confirmed deletion calls `prepare_studio_profile_delete(id)`, `store.delete(id)`
  and `clear_studio_profile(id)` synchronously, in that order, with no event-loop
  yield. Failed preparation or storage deletion does not clear the current model.
- `profile_selected(ProfileSelection)` is a post-installation notification; do
  not install or resume again from this signal.
- `profile_renamed(ProfileRecord)` lets Deston refresh cosmetic shell labels.
  The current shell has no public cosmetic-rename method; attachment must handle
  this notification without retraining or expiring otherwise matching readiness.
- `profile_deleted(str)` reports an opaque ID after successful removal/clear.
- `busy_changed(bool)` lets the shell disable competing load/start/edit controls
  for the duration of creation or a requested load. On widget teardown the host
  also reconciles its controls; a closing widget cannot publish another result.
- Guest switching calls `use_studio_guest()` and publishes `guest_selected()` only
  on success. False/exception retains the previous selector state. No saved
  metadata or source data is deleted, and the same profile can be loaded again.
- `start_requested(ProfileSelection)` asks the host owner to start Preview.
  Deston connects this to the existing start path after checking the selection,
  model, mode, focus and camera lifecycle; it must require fresh NEUTRAL. This is
  a request, not proof of camera availability or permission for LIVE.

The shell's timer owns its load completion; this widget never calls the shell's
polling function or writes its loader/state internals. A shell-accepted load stays
owned by that shell if only the selector is hidden/closed. Closing Studio remains
the shell's cancellation boundary. Local-only work and newly created candidates
are discarded for installation if the selector hides/closes; a completed save is
retained. Closing the widget stops its timer and does not interrupt a file save.
Create a new widget instance after closing. The shell must serialize external
profile edits/model changes with the selector and refresh it when ownership changes.

## Remaining integration

Guest now uses Deston's non-deleting reset API. `clear_studio_profile` remains
reserved for actual deletion. Starter recognition remains unavailable.

Deston still needs to place the screen in Studio, handle cosmetic rename and
Preview-start notifications, coordinate other loading controls while creation is
pending, and run integrated camera and participant checks. Guided enrolment is
already attached to Studio on main; its human walkthrough and starter readiness
remain separate acceptance gates. GF-P06 is not marked fully complete by this component.

## Verification

Tests use generated numeric fixtures in temporary directories, not participant
data. They cover persistence, background creation and GUI-thread installation,
real Studio saved loading/deletion, failed reload of the same ID, consent and
pause refusal, corrupt entries, write failures, confirmation, independent deletion,
Guest round trips/failure handling and local worker completion after hide/close. Studio test stores
and working directories are temporary so existing private settings are not read.

Publication is from `codex/hau-jie-profiles` for Deston's review. PR #16 and
Deston's shell changes were brought in by fast-forwarding Hau Jie's branch to
reviewed main. The local `main` branch was not changed. Only source, generated-fixture
tests and handoff documentation are included; datasets and local screenshots stay private.

Historical local results after adapting to `a933052` (Python 3.11, `PYTHONPATH` set to
this checkout; automated GUI suite uses Qt offscreen):

```text
python -m pytest -q tests/test_profile_widget.py
13 passed in 17.19s
python -m pytest -q
473 passed, 1 skipped in 57.48s
python -m ruff check gestureforge tests scripts
All checks passed!
python -m mypy gestureforge scripts tests
Success: no issues found in 59 source files
python -m gestureforge --smoke-test
exit 0
python -m gestureforge --studio --smoke-test
exit 0
```

The native Windows render check passed separately (`QT_QPA_PLATFORM=windows`):
`tests/test_profile_widget.py::test_visible_component_evidence`, 1 passed in
5.93s. Its generated-data screenshot is local and ignored at
`.local/profile-selector.png`. Offscreen rendering initially lacked system fonts;
the native Windows capture was used for visual inspection. This is a rendered
component check, not a recording of human interaction or camera recognition.
