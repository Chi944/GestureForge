# GestureForge AI assistance declaration and prompt index

Updated 27 September 2026. This record describes actual AI assistance and verification. It does not claim human signoff or compliance with unit-specific guidance that has not been supplied. The user confirmed **Codex** as the AI tool used so far.

## Declaration for human review

OpenAI Codex was used substantially for scope planning, implementation, automated tests, troubleshooting, documentation, repository/agile setup and review. AI-generated work includes prototype source code, helper scripts, tests and report text. MediaPipe supplies the pretrained hand detector and landmarks; scikit-learn supplies the classifier implementations. These are third-party components, not team-authored algorithms. GestureForge fits the supplied classifiers to the personal numeric training data.

The team remains responsible for understanding and checking the submitted work, attribution, participant permissions and accurate reporting. Human names, contributions and signoff must be recorded in [CONTRIBUTIONS.md](docs/CONTRIBUTIONS.md). AI assistance is not a student team member and must not be assigned a student contribution percentage.

This is a factual draft for team review. The unit information guide and required AI citation format remain to be checked. No specific model/version has been inferred from the model selected today.

## Prompt record

The [user prompt log](docs/AI_PROMPT_APPENDIX.md) replaces the earlier representative excerpts. It preserves stable prompt IDs, recorded UTC timestamps where available, original wording, the full implementation-plan prompt, and clarification questions with the user's answers. Original-message hashes support checking against the retained source. Images, internal system instructions, hidden reasoning and tool outputs are not part of this user-prompt export.

| Prompt IDs | Request or clarification | Related work and evidence |
| --- | --- | --- |
| PR-001 to PR-006 | Assignment/final split, implementation, agile tools and repository | [Build plan](docs/BUILD_PLAN.md), [agile record](docs/AGILE.md), source and tests |
| PR-007 to PR-017 | Camera troubleshooting, P01 consent and live hold/rearm observations | [Hardware record](docs/evidence/HARDWARE_CHECK.md), [pilot results](docs/evidence/PILOT_RESULTS.md) |
| PR-018 to PR-020 | Main branch, README and another Windows laptop | [GitHub record](docs/GITHUB_SETUP.md), [Windows guide](docs/WINDOWS_LAPTOP.md) |
| PR-021 to PR-025 | P02 feedback, private P01 sharing, local operation and gesture scope | [P02 evidence](docs/evidence/P02_LAPTOP_TEST.md), [user guide](docs/USER_GUIDE.md), [private package check](docs/evidence/MARKER_PACKAGE_CHECK.md) |
| PR-026 to PR-027 | Continue packaging and tighten records without assumptions | Report, [decision log](docs/DECISIONS_AND_RISKS.md), [submission inventory](docs/SUBMISSION_README.md) |
| PR-028 to PR-030 | Confirm names/tools and pending team, retention and laptop facts | [Contributions](docs/CONTRIBUTIONS.md), [checklist](docs/SUBMISSION_CHECKLIST_ASSIGNMENT.md) |

This index identifies related artifacts, not proof that every requested result is complete. Each artifact states its evidence status.

## Verification of AI assisted work

| Work | Verification recorded | Limit |
| --- | --- | --- |
| Source and tests | 27 September verification: 60 tests, Ruff, mypy, GUI smoke and synthetic comparison passed | Automated checks do not replace human understanding or live hardware tests |
| AI comparison | Private archive reproduced P01 kNN/SVM macro-F1 0.9686 | Development validation, not held-out generalisation; 25/40 negative samples accepted as BOOKMARK |
| Live prototype | P01 participant-observed hold/rearm check and P02 assisted laptop report | Qualitative smoke evidence; final-project performance targets remain untested |
| Documentation | Checked against assessment files, code and recorded evidence | Human approval, administrative facts and external AI-history coverage remain pending |

## Coverage and remaining review

Original planning and implementation messages have now been recovered for this task. That closes the earlier missing-plan gap; it does not establish completeness across all Codex chats. Other conversations, including P02's assisted setup, have not been supplied or confirmed complete. The user's statement “codex so far” identifies the tool, not the number of conversations or transcript coverage.

Before submission, confirm all AI conversations used are represented, check unit-specific declaration/citation guidance, review privacy and attribution, and have both team members approve the text. The course specification requires prompts in the report; the report PDF includes this record and the recovered prompt appendix. Do not mark external-history coverage complete until confirmed.
