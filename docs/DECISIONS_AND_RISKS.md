# Decisions and risks

Recorded 23 September 2026. These are implementation decisions, not tutor approvals.

| Decision | Evidence and reason | Consequence |
| --- | --- | --- |
| Keep NEXT as the only assignment action | Approved two-release scope | Profiles, in-app enrolment, PREVIOUS/BOOKMARK execution, custom decks and saved state remain November work |
| Use camera index 1 on this computer and preserve negotiated format | Actual capture and participant collection succeeded; index 0 did not | Recheck the index after reconnecting devices and on the second computer |
| Estimate rejection references across independent training trials | Sample-level references over-rejected real validation gestures; best baseline macro-F1 0.5667 | Model v2 excludes all frames from the originating trial; validation is never used to fit the scaler or reference distances |
| Use provisional kNN with multiplier 2 for the NEXT-only demo | Both classifiers reached development macro-F1 0.9686; kNN is straightforward to explain and both are fast relative to the hold | Preserve the baseline; final selection remains open and needs validation before held-out testing |
| Keep participant features and full outputs local | User authorised local numeric P01 right-hand data, with no raw frames or GitHub publication | Source ZIP and GitHub contain aggregate evidence only; marker sharing and retention still need agreement |

| Risk | Current evidence | Mitigation / exit condition |
| --- | --- | --- |
| Unfamiliar poses accepted as BOOKMARK | 25/40 negative samples at all corrected multipliers | BOOKMARK remains preview-only. Improve development data/rejection and verify the full-command system before final release |
| Small same-person pilot overstates generalisation | 32 validation trials; correction guided by these results | Label results preliminary; final evaluation uses two personal profiles and untouched TEST sessions |
| Deployment differs on the second computer | Development and isolated-environment checks passed locally | Run the release instructions and real camera path on the second Windows computer |
| Assessment rules or administrative gaps | Weight discrepancy; signatures and team details unconfirmed | Use TUTOR_REVIEW.md and submission checklists; do not invent approvals or signatures |
| Schedule pressure expands prototype scope | Final deadline is 7 November | Preserve the two releases and prioritise required evidence over additional features |

Agile status changes are recorded in `sprint_events.jsonl`, with acceptance criteria in `backlog.csv`. Tutor meeting records belong in `TUTOR_REVIEW.md`; no tutor meeting or approval is claimed by this log.
