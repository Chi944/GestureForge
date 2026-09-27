# P02 second laptop test

Recorded 26 September 2026 from the friend's written report supplied by the project lead. This is participant-reported qualitative evidence, not a directly observed or instrumented evaluation. The exact test date, Windows version, camera model/index, source commit, dataset size and algorithm settings were not supplied.

The project lead confirmed that the friend used the ZIP with Codex assistance. This establishes successful use on another laptop, but does not establish unaided installation using only the supplied guide. The friend used their own P02 right-hand dataset and laptop camera. P02 feature files and measured classification results have not been supplied.

| Scenario | Reported observation | Evidence status |
| --- | --- | --- |
| Personal enrolment and webcam recognition | Worked using P02's own right-hand examples and laptop camera | Reported pass |
| Full fixed deck navigation | NEXT advanced from Card 1 through Card 10 | Reported pass |
| Sustained NEXT | A five-second hold produced one action | Reported pass; repetition count not provided |
| Rearming | NEUTRAL was required before another NEXT command | Reported pass |
| PREVIOUS and BOOKMARK | Labels appeared without changing cards | Expected assignment behaviour |
| Pose changes | Motion, tilt, back of hand, lateral position and excessive distance reduced reliability | Reported limitation |
| Recovery | Friend usually removed the hand, showed NEUTRAL, then repeated the command | Reported workaround, not a software requirement |
| Pause and camera restart | Not tested, confirmed by project lead | Pending |
| Network disconnected | Not tested, confirmed by project lead | Pending |
| Exact ZIP version and guide-only setup | Version not provided; Codex assisted setup/use | Not established |

## Interpretation and action

The report supports a limited assignment outcome: a separately enrolled person reported advancing the demo deck on another laptop, and the reported five-second hold produced one action. The repetition count is unknown. It does not provide P02 macro-F1, false-action frequency, action latency, a formal twenty-hold result or performance on users who have not enrolled.

The prototype uses static poses and preserves pose orientation. Wrist-relative scaling reduces translation and scale variation in valid landmarks; it does not make hand tracking immune to camera framing, occlusion, perspective, blur or distance. These are plausible explanations, not root causes isolated by this qualitative test.

For the assignment demo, keep the whole enrolled hand visible, use the same palm orientation and similar camera framing as enrolment, settle before holding a command, and return to a stable NEUTRAL pose after a rejected observation. Removing the hand is not required by the controller. Do not loosen rejection or shorten hold timing simply to hide failed recognition.

For the final project, collect bounded variations in position, distance and orientation in development sessions; evaluate unfamiliar poses and rejection; freeze configuration before separate held-out tests. Dynamic gestures and PowerPoint integration remain outside scope.

## Short remaining laptop check

1. Record Windows/Python versions, camera index, source ZIP SHA256 or commit, test date and pseudonymous tester ID.
2. Start control with the personal dataset. Pause during a pending command and confirm no gesture action occurs while paused.
3. Restart camera control, show stable NEUTRAL, then NEXT; confirm recovery and one action. Close and reopen the app to check camera release.
4. After setup, disconnect Wi-Fi/network and repeat launch, model check and the live NEXT sequence. Do not rerun online dependency installation while disconnected.
5. Record whether any Codex assistance was needed and the exact missing instruction/error. Preserve this as assisted-test evidence until an instructions-only installation is actually demonstrated.
