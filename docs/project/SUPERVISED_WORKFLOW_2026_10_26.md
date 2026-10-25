# Supervised Harbor workflow — 26 October 2026

Build: `a8b86f6`. Operator: Deston. Environment: existing Windows demo laptop,
camera 1, saved right-hand personal profile, fixed kNN / distance multiplier 1.5 /
ambiguity margin 1.5. This is an assisted integration walkthrough under the visible
supervised-demo override; it is not a standard Practice qualification pass.

| Check | Evidence and result |
| --- | --- |
| Navigation | Exported gesture NEXT, PREVIOUS and stage transitions across Harbor contexts. Operator reports working functions. |
| Desktop resources | Gesture launch requests for Calculator, reference and resource folder. Actual task results are operator-reported; requests alone do not prove OS task completion. |
| Bookmarks | Discussion bookmark applied, then three gesture bookmark outcomes remained unchanged. Existing bookmarks were retained. |
| Injected failure | Agent temporarily renamed only the disposable recovery reference. Two gesture requests failed with the missing-or-moved target recovery message. |
| Explicit recovery | Agent restored the file with matching SHA256. A fresh gesture requested it; Deston confirmed “reference opened”. No automatic retry was used. |
| Persistence | Agent operated Save / Restore / Save through Studio. Saved JSON content matched exactly: Discussion stage/card and four bookmarks. UI restored paused in Preview; Live was explicitly reapplied. |
| Completion | Deston acknowledged Discussion and gestured to Review. After Deston reported “finished”, the agent acknowledged Review and clicked Finish. Final Finish is manual, not a gesture result. |

Restore archives and resets the summary, so interpret both segments together:
the pre-restore archive has 5 launch requests, 2 intentional failures, 21 applied
and 3 unchanged outcomes; the completed post-restore segment has 2 applied
outcomes (one gesture transition and one manual Finish) and acknowledgements for
Discussion and Review. Earlier stage acknowledgements were not recorded in-app.
The retry counter is zero because the recovery action used a fresh gesture rather
than the dedicated Retry control. Do not combine overlapping interim exports.

Private evidence is indexed by `.local/p01-workflow-20261026/walkthrough-verification.json`.
It references the original pre-restore archive, completed segment, exact session
roundtrip files and retry/restore receipt with checksums. Numeric/profile data and
local machine paths are excluded from the public repository.

Accepted substeps: supervised workflow integration, repeat-bookmark behaviour,
missing-target recovery and session persistence on this machine. GF-P16 is now owner-accepted under the revised criterion documented below;
the original automated qualification was not met and its measured result remains
19/22 correct. No latency, 20-hold, ten-minute-negative, timed manual comparison,
30-minute stability, second-device, macOS Studio or video acceptance is inferred.

Use this walkthrough to prepare genuine demonstration footage and report the
recognition limitation and manual fallback. Reuse these passed recovery checks;
do not repeat the entire walkthrough merely to recreate the same evidence.

## Operator review

Deston reports a frame-by-frame review of the latest session with Claude and manually accepts all 22 trials (22/22 operator acceptance), attributing the three automated failures to autofocus. This is an operator-reported assessment; the review output has not been independently inspected and autofocus causation is unverified. The recorded automated result remains 19/22. No saved outcomes, model settings or runtime qualification gates are changed.

| Assessment | Result | Basis |
| --- | --- | --- |
| Operator acceptance | 22/22 manually accepted | Deston reports reviewing the latest session with Claude. |
| Automated Practice measurement | 19/22 | Saved capture-coverage and prediction outcomes, unchanged. |

Use these labels together when reporting this session; manual acceptance is not
a replacement automated measurement or an independently reproduced adjudication.

## GF-P16 acceptance decision

26 October owner acceptance: Deston explicitly directed that his manual review count in place of the automated qualification criterion for GF-P16. GF-P16 is accepted under this revised owner-approved criterion, using 22/22 operator acceptance and the verified Harbor workflow/recovery. The measured Practice result remains 19/22; this is not a claim of automated qualification, tutor approval, or GF-P20 performance acceptance. Runtime protections and model settings are unchanged.
