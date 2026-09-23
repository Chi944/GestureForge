# GestureForge Assessment Audit

Status: evidence audit as of 23 September 2026. Software checks pass; the assignment is not yet ready for submission because human and hardware gates remain open.

## Code Coverage Now Present

| Assessment area | Current code or artifact coverage | Evidence status |
| --- | --- | --- |
| Work isolated under `code` | Source, assets, tests, scripts, experiments, and docs are under `code` | Present |
| Agile development tools | Local sprint board and event history; private GitHub repository, nine issues, two milestones and project board | Created and used; see `GITHUB_SETUP.md` and `AGILE.md`; human collaboration records remain pending |
| Local sprint board | `scripts/board.py` renders `docs/SPRINT_BOARD.html` and records evidence-based updates in `docs/sprint_events.jsonl` | Present; root owns status updates |
| AI prototype entry point | `python -m gestureforge` exists via `gestureforge/__main__.py` | Qt startup/render/shutdown smoke passed |
| Guided data collection | `python -m gestureforge.collect --split train|validation|validation_negative --participant P01 --hand Right --setup "..." --consent --output data/local/pilot` | CLI present; P01 right-hand TRAIN, VALIDATION, and validation-negative collection completed |
| Evaluation CLI | `python -m gestureforge.evaluate --config <json>` supports `dataset_path`, `dataset_paths`, `synthetic_fixture`, `algorithm`, `algorithms`, and `rejection_multiplier` | Synthetic reproducibility checks and human pilot metrics recorded; see `docs/evidence/PILOT_RESULTS.md` |
| Synthetic fixtures | `python -m gestureforge.fixtures data/local/synthetic` and `experiments/prototype.json` | Software-only evidence; not participant evidence |
| Environment helpers | `scripts/check_environment.py` and `scripts/download_model.py` | Dependency check, model retrieval/checksum and blank-image inference passed; see evidence/HARDWARE_CHECK.md |
| Locked setup and packaging | `scripts/setup.ps1` installs locked dependencies and asset; `scripts/package_release.py` creates tracked-source ZIP | Present; package is source only |
| Assignment UI boundary | `gestureforge/app.py` labels NEXT active and PREVIOUS/BOOKMARK preview-only | Present |
| Automated checks | Controller, viewer, data, features, classifiers, evaluation, capture, collection and GUI | 55 tests pass, lint/type checks pass; evidence/verification.json records exact output |
| Clean source installation | Extracted source ZIP installed into a new environment using requirements.lock and editable source | Same-computer checks passed; evidence/clean-install-verification.json; not a second-device test |

## Human and Hardware Requirements Still Open

| Requirement | Why it matters | Current status |
| --- | --- | --- |
| Participant consent | Required before real gesture data is collected or submitted | Granted for local numeric P01 right-hand data with no raw frames and GitHub exclusion; marker permission, retention and signatures still pending |
| Pilot train and validation sessions | Required for actual assignment AI results | TRAIN and VALIDATION completed: 32 trials each, eight each for NEXT/PREVIOUS/BOOKMARK/NEUTRAL, 160/160 valid scheduled samples per split |
| Validation-negative sequence | Needed to assess false command acceptance | Completed: 8 trials and 40 valid samples from unenrolled poses |
| Live webcam NEXT action | Required to show integrated prototype behaviour | Verified for assignment path: genuine webcam gesture NEXT events advanced the viewer to positions 1, 2, and 3 |
| Participant-observed hold smoke check | Supports controller behaviour in live use | Two deliberate fist holds advanced exactly once each after open-palm rearm; formal final-project twenty-hold run still pending |
| Connected camera check | Connected-device capture is needed before real collection | Usable non-black capture on camera index 1 verified; device indexes can change after replug |
| Live hand-detection framing | Needed before collecting training and validation examples | Verified by visible/topmost 60-second preview: 1,145 frames processed, one hand detected in 338 frames, clean close; this is detector activity, not recognition accuracy |
| Second Windows computer install | Protects release reproducibility and marking risk | Pending human/hardware gate |
| Tutor scope and marking-weight confirmation | Protects against criteria mismatch | Pending tutor gate |
| Signed group declaration | Required administrative artifact | Pending human gate |
| LMS upload/download verification | Required submission control | Pending human/LMS gate |

## High-Band Protection

The documentation covers requirements, design, algorithm investigation, test planning, lifecycle, agile process, references, contribution tracking, data handling, and submission controls. Automated software evidence is recorded, usable camera-index 1 capture with live hand tracking is verified, P01 right-hand pilot data is complete, pilot metrics are recorded, and a real webcam NEXT path has advanced the viewer. A participant-observed two-hold smoke check advanced exactly once per hold, but the formal final-project twenty-hold run, live false-action/latency measurements, independent installation, human report review and administrative artifacts remain necessary. No grade is guaranteed: the supplied files do not provide detailed highest-band descriptors, and the tutor must resolve the marking-weight discrepancy.
