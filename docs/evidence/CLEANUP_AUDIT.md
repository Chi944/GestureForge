# Repository cleanup audit

Date: 28 September 2026. Scope: the GestureForge `code` repository and its generated local artifacts. Original assessment files outside `code` are preserved.

## Cleanup plan

1. Inventory tracked source, tests, scripts, configuration, documentation and ignored local artifacts; trace callers and document references before selecting deletions.
2. Run the existing regression suite before code changes. Preserve assignment behaviour, safety checks, numeric participant data, provenance, assessment evidence and the November extension plan.
3. Remove only proven dead code or redundant generated artifacts. Keep the active interpreter/environment and original evidence; retain unique logs when removing temporary installations or extracted copies.
4. Run targeted regression tests, lint, type checks, the full suite, GUI smoke and synthetic evaluation; check document links and regenerate source/private packages.

## Results

The tracked repository was reviewed by separate source/tooling and documentation audit passes, with findings checked before editing. No complete tracked module, test, guide, assessment record or experiment file was unrelated enough to justify deletion. The cleanup removes 27 lines of unused/unreachable Python and one repeated guide paragraph.

| Removed code/prose | Evidence for removal | Retained behaviour |
| --- | --- | --- |
| `DatasetBundle.labels` | No callers; `split_data()` already returns aligned labels | Training and validation labels continue through `split_data()` |
| `append_dataset()` | No callers; collection already loads, extends and saves complete trials | Existing collection append/resume path and dataset persistence remain tested |
| Second `LATCHED` guard in `Controller.process()` | Earlier guard returns for that state, with no reachable intervening transition into it | Exactly-once hold/rearm behaviour is unchanged |
| Repeated synthetic-fixture warning in USER_GUIDE | Same warning already appears immediately above | Human versus synthetic evidence distinction retained |

No new runtime dependencies or abstractions were added. Existing regression tests covered the retained behaviours, so duplicate tests were not added.

## Generated artifacts removed

Removed **99,759 generated files**, totalling **9,829,121,605 logical bytes** (about 9.8 GB / 9.15 GiB). Logical size is not a measurement of physical disk space reclaimed, because caches can use hard links.

The exact paths, file counts and byte totals are retained locally in `.cache/cleanup-audit.json`. Removed groups:


- `.cache/assessment-review`
- `.cache/Bad Venv Message 20260923-165441`
- `.cache/Bad Venv Message 20260923-165508`
- `.cache/camera-opencv4`
- `.cache/doc-review`
- `.cache/doc-review-final`
- `.cache/report-preview`
- `.cache/pip`
- `.cache/references`
- `.cache/uv`
- `.cache/release-env`
- `.cache/release-smoke/gestureforge`
- `.cache/setup-smoke-20260923-162235/source`
- `.cache/setup-smoke-20260923-162702/source`
- `.cache/Windows Laptop Smoke 20260923/gestureforge`
- `.cache/Windows Laptop Smoke 20260923-164822/gestureforge`
- `.cache/Documentation Release 20260927/gestureforge`
- `.cache/Marker Final 20260927/gestureforge`
- `.cache/Marker Package Check 20260927/gestureforge`
- `.cache/marker-package-check-20260927165849/gestureforge`
- `.cache/marker-package-check-20260927165908/gestureforge`

## Evidence and working files preserved

- All original participant files under `data/local` were hashed before cleanup and checked unchanged afterwards. Private copies in deleted extracted trees were removed only after matching the originals.
- 27 unique run-output files were copied and hash-verified under `.cache/retained-evidence/<run-name>/`. Private evaluation outputs and raw session logs remain excluded from GitHub and source ZIPs.
- Original setup logs/results remain at `.cache/setup-smoke-20260923-162235/`, `.cache/setup-smoke-20260923-162702/`, and `.cache/Windows Laptop Smoke 20260923/setup.log`.
- The active `.python` interpreter, `.venv`, editable-install metadata, model asset and current source/private release outputs were preserved.
- Existing tests, CI, synthetic fixtures, research/attribution, prompt history, report, official declaration, agile records and November extension plans remain relevant to assessment and were retained.
- Automatic approval review rejected the optional follow-up removal of `.tools` and remaining Python/test caches with only “blocked by policy”. Those folders and the one-off local cleanup script were left intact; no alternative deletion route was attempted.

## Verification

- Before editing: **60 tests passed**.
- After editing: `scripts/verify.py` passed Ruff, mypy (29 source files), **60 tests**, offscreen GUI startup/shutdown and synthetic evaluation. Fresh exact output is in [verification.json](verification.json).
- After removing temporary installations/caches: `python -m pip check` reported no broken requirements; `run.cmd --smoke-test` exited 0.
- P01 evaluation with `experiments/pilot.json` reproduced macro-F1 **0.9686274509803923** for kNN and SVM, unchanged confusion matrices and the known 25/40 negative command-label acceptance limitation. Full private output is `experiments/local/cleanup-reproduced-pilot.json`. This is development evidence, not new live-camera or held-out testing.
- AI-use log includes the exact cleanup request as PR-031. The 27-page report PDF was regenerated and visually inspected with that prompt included.
- Release and document checks are completed before handoff; exact current package hashes and source revision are recorded locally in `releases/final-package-verification.json`.

This cleanup does not close remaining human submission gates: team identifiers/contributions, tutor/AI guidance, other conversation coverage, retention, laptop acceptance, report approval, signatures, marker access and LMS verification remain pending.

## Changed tracked files

- `AI_PROMPTS.md`
- `docs/AI_PROMPT_APPENDIX.md`
- `docs/SUBMISSION_README.md`
- `docs/USER_GUIDE.md`
- `docs/evidence/CLEANUP_AUDIT.md`
- `docs/evidence/DOCUMENTATION_CHECK.md`
- `docs/evidence/MARKER_PACKAGE_CHECK.md`
- `docs/evidence/verification.json`
- `experiments/synthetic-software-check.json`
- `gestureforge/controller.py`
- `gestureforge/dataset.py`
- `output/pdf/GestureForge_Assignment_Report.pdf`
