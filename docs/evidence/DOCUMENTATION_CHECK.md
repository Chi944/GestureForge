# Documentation and submission preparation check

Recorded 27 September 2026. This pass changes documentation, attribution and submission artifacts only. Application source, datasets and assignment scope are unchanged.

## Verified in this pass

- Checked 203 local Markdown file links/anchors before adding this evidence record; none were broken. Historical paths inside preserved quoted prompts were excluded from repository-link validation.
- Prompt appendix has 30 unique ordered IDs and 30 original-message SHA256 values. Original planning and the full implementation-plan prompt are retained. Other Codex conversations remain unconfirmed.
- Report PDF regenerated to 27 pages, all pages rendered and visually inspected. AI-use and all recovered user-prompt entries are included. The Markdown log also retains the navigation register omitted from the PDF's duplicate index.
- Official blank declaration copied unchanged; SHA256 `50f20dc01cdc9666b3ce80cd84a0837c2c0abc649352e0f701aa8d57c96ca768` matches the supplied original. It remains unsigned.
- Dependency attribution snapshot covers all 41 lockfile packages and installed metadata. Model source/checksum is recorded; a separate asset-specific licence has not been established from local evidence.
- Updated source/private archives passed ZIP integrity, checksum and byte-for-byte comparison with their corresponding files. Source contains no participant data; private adds exactly the P01 manifest and numeric feature sidecar.
- The private package was extracted into `.cache/Documentation Release 20260927/gestureforge`. Import resolved to that extracted source. Evaluation with `experiments/pilot.json` reproduced macro-F1 **0.9686274509803923** for kNN and SVM using the existing development environment. This is not a new installation, hardware test or held-out evaluation.
- Existing software verification remains in [verification.json](verification.json): 60 tests, Ruff, mypy, GUI smoke and synthetic evaluation. Those checks were not rerun for this documentation-only pass; no new live-camera result is claimed.

Release archive checksums are in their generated `releases/*.json` companions. Rebuilding after this record is staged updates archive contents/checksums; final byte comparisons are retained locally in `releases/final-package-verification.json`. Neither archive is a signed complete submission.

## Pending facts and human signoffs

Jameson and Deston, GitHub, WhatsApp and Codex are confirmed as supplied. Full names/IDs/emails, individual contributions/percentages, group/tutorial registration, tutor replies, retention, remaining laptop checks, unit AI guidance/other Codex prompt coverage, report review, signatures, marker access and LMS verification remain pending. No participant-to-team-name mapping is inferred.

## Files changed in this pass

- `AI_PROMPTS.md`
- `LICENSES.md`
- `README.md`
- `docs/AGILE.md`
- `docs/AI_PROMPT_APPENDIX.md`
- `docs/ASSESSMENT_AUDIT.md`
- `docs/ASSIGNMENT_NEXT_STEPS.md`
- `docs/ASSIGNMENT_REPORT.md`
- `docs/CONTRIBUTIONS.md`
- `docs/DECISIONS_AND_RISKS.md`
- `docs/GITHUB_SETUP.md`
- `docs/SPRINT_BOARD.html`
- `docs/SUBMISSION_CHECKLIST_ASSIGNMENT.md`
- `docs/SUBMISSION_README.md`
- `docs/TEST_PLAN.md`
- `docs/USER_GUIDE.md`
- `docs/backlog.csv`
- `docs/evidence/DOCUMENTATION_CHECK.md`
- `docs/evidence/MARKER_PACKAGE_CHECK.md`
- `docs/evidence/dependency-attribution.json`
- `docs/sprint_events.jsonl`
- `docs/submission/Group_Declaration_TO_COMPLETE.docx`
- `output/pdf/GestureForge_Assignment_Report.pdf`
- `releases/README.md`

## Later cleanup - 28 September 2026

The temporary extracted source was removed after its unique reproduction output was retained under `.cache/retained-evidence/Documentation Release 20260927/experiments/local`. The dated checks above describe the 27 September pass. Current software verification and archive metadata have since been refreshed; see [CLEANUP_AUDIT.md](CLEANUP_AUDIT.md). The prior archive verification JSON is retained locally under `.cache/retained-evidence/final-package-verification-b91765b.json`.
