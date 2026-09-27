# GestureForge assignment submission inventory

Prepared 27 September 2026 for the **3 October 2026 assignment**. The documentation and prototype are assembled for review. Submission is not signed off: the user has explicitly left team identifiers/contributions, tutor matters, data retention and remaining laptop checks pending. The final project remains due 7 November 2026.

## Read in this order

1. [Assignment report PDF](../output/pdf/GestureForge_Assignment_Report.pdf) and [editable report source](ASSIGNMENT_REPORT.md). The PDF includes AI-use and prompt appendices; it is marked for review while human facts remain pending.
2. [User guide](USER_GUIDE.md) and [Windows installation guide](WINDOWS_LAPTOP.md) for setup, demo operation and another laptop.
3. [Pilot results](evidence/PILOT_RESULTS.md), [software verification](evidence/verification.json), [P02 qualitative evidence](evidence/P02_LAPTOP_TEST.md) and [private package reproduction check](evidence/MARKER_PACKAGE_CHECK.md).
4. [Decision/risk log](DECISIONS_AND_RISKS.md), [requirement/test traceability](TEST_PLAN.md), [agile record](AGILE.md) and [local sprint board](SPRINT_BOARD.html).
5. [AI declaration/index](../AI_PROMPTS.md), [preserved user prompts](AI_PROMPT_APPENDIX.md), [source/dependency attribution](../LICENSES.md) and [team contribution record](CONTRIBUTIONS.md).
6. Complete and sign the official [group declaration template](submission/Group_Declaration_TO_COMPLETE.docx). The supplied copy is unchanged and unsigned; it does not satisfy the declaration requirement until completed by the team.

## Assessment coverage

The source is `ICT304_Assignment_Project_TS_2026.pdf`, pages 1-4, and `Assignment Feedback sheet.docx`, retained in the parent assignment folder. This table records coverage, not a predicted grade or tutor approval.

| Requirement | Supplied evidence | Remaining completion |
| --- | --- | --- |
| Product title, problem, requirements and data needs | Report; numbered RQ-001 to RQ-015; data collection protocol | Team/tutor review of requirements |
| Applied systems engineering lifecycle | Report lifecycle and milestones; decision/risk log; agile records | Actual weekly tutor feedback and reviews |
| System/subsystem design, workflow and full-system test plan | Report contracts/pipeline/controller; TEST_PLAN.md | Final-project subsystem execution remains November work |
| Investigation of at least two AI techniques and justified choice | kNN/SVM comparison, common scaler/rejection, confusion matrix, timing and limitations | Human understanding and report approval |
| Working prototype and initial results | Source, NEXT-only live observations, P01 metrics, P02 report and release checks | Remaining laptop acceptance and exact submitted-copy check |
| Innovation and comparison with common approaches | Report innovation and related-work discussion | Human review of claims and references |
| Project management, version control, collaboration, communication | GitHub Issues/Projects, Git, GitHub collaboration, WhatsApp confirmed by user | Concrete team activity summaries and contribution evidence |
| Sources, tools and AI disclosure | LICENSES.md, lockfile/model manifest, AI index and full recovered task prompts | Other Codex conversation coverage and unit-specific AI guidance |
| Group declaration | Official blank template and contribution preparation record | Full identifiers, actual work, agreed percentages and all signatures |
| LMS report/code/relevant files and backup | Separate source/private ZIPs, SHA256 companions, review PDF and guides | Final assembly, backup confirmation, upload/download and run |

The course PDF weights requirements/prototype 35%/15%; the feedback sheet uses 30%/20%. This discrepancy remains a tutor question. Both require reporting all four tool categories and including the group declaration; the course PDF also states a deduction for non-working code/demo. No grade or exemption is assumed.

## Choose the correct package

| Artifact | Contents | Intended use |
| --- | --- | --- |
| `releases/gestureforge-assignment-source.zip` | Tracked source, guides, report, logs and unsigned declaration template; no participant data | Source transfer; cannot alone reproduce the P01 results |
| `releases/gestureforge-assignment-private-marker.zip` | Source package plus only the authorised P01 manifest and numeric feature sidecar | Private tutor/marker reproduction; keep out of GitHub/public distribution |
| Matching `.json` files in `releases` | SHA256, file count and build time | Check the exact transferred ZIP |
| `output/pdf/GestureForge_Assignment_Report.pdf` | Report with AI-use/prompt appendices | Review and eventual report submission |
| Completed signed declaration | To be supplied by the team | Required final private submission attachment; currently absent |

Both ZIPs remain preparation artifacts. The private P01-sharing permission is recorded; retention is explicitly pending. The original assessment files remain unchanged. Do not replace the official signed declaration with an unsigned template, an AI-written attestation or a checklist.

## Reproduce and demonstrate

Extract the private marker ZIP, open its `gestureforge` folder and run `setup.cmd` while online. From PowerShell in that folder:

```powershell
.\.venv\Scripts\python.exe -m gestureforge.evaluate --config experiments/pilot.json --output experiments/local/reproduced-pilot.json
.\run.cmd
```

The first command uses saved P01 data; expected development macro-F1 is 0.9686 for both classifiers. The second opens the manual viewer. For the enrolled P01 person, close other camera apps, verify the camera index and launch:

```powershell
.\run.cmd --dataset data/local/pilot/manifest.json --algorithm knn --multiplier 2 --camera 1
```

Camera index 1 is the development computer's verified index, not a universal value. Start camera control, hold enrolled NEUTRAL until READY, then hold enrolled NEXT for one advance. Hold continuously to demonstrate no repeated advance, then return to NEUTRAL before another command. PREVIOUS/BOOKMARK display labels only. Pause to disable gestures. The app controls its own ten-card deck, not PowerPoint.

P01 is a personal dataset. Another demonstrator must follow the separate enrolment instructions and save their data separately; do not append their examples to the submitted P01 dataset or claim they reproduce the P01 experiment. First-time setup needs internet; disconnected-network webcam acceptance remains pending.

## Final assembly controls

- Resolve the open [submission checklist](SUBMISSION_CHECKLIST_ASSIGNMENT.md) items and update the report from confirmed facts only.
- Re-export the report after edits. Regenerate both ZIPs using [release instructions](../releases/README.md); verify the current SHA256, included files and reproduced scores.
- Keep the signed declaration and identifying details private. Include them in the final LMS submission according to the actual LMS fields; no specific upload structure has been supplied here.
- Retain a backup. Download the actual LMS submission and check the report/declaration open and the extracted code runs. Record the exact filename, checksum, date, tester and result; do not mark this complete from a local build.

Current unanswered facts are intentionally pending, not assumptions: full names/IDs/emails, group name, tutorial/registration, actual contributions and percentages, tutor responses, unit AI-use instructions/other prompt history, retention, remaining laptop tests, final signatures and LMS confirmation.

See the [documentation verification and changed-file record](evidence/DOCUMENTATION_CHECK.md) for this preparation pass.
