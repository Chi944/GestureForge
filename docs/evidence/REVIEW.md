# Independent code review

Reviewed on 23 September 2026: capture, application, controller, collection, data and evaluation flows, with relevant automated tests.

One confirmed finding was corrected: observed collection records now store actual capture timestamps rather than their scheduled times. Trial start times and offsets remain in metadata; missing slots are explicitly invalid. The simulated collection regression checks saved times against the camera's actual observations and audits delay against the schedule.

A proposed handedness swap was withdrawn after checking the API actually used. MediaPipe Tasks maps tensor index 0 to Right and index 1 to Left; legacy Hands uses the opposite label ordering. Applying legacy selfie guidance without checking Tasks would introduce an unsupported change. Source: [Tasks detector graph](https://raw.githubusercontent.com/google-ai-edge/mediapipe/master/mediapipe/tasks/cc/vision/hand_landmarker/hand_landmarks_detector_graph.cc). Subsequent physical-camera collection with the participant's stated right hand produced 160/160 valid training samples under the Right-hand check.

No confirmed high or critical software issue remained in this bounded review. This is not proof of live performance or of absence of defects. Static type checking covers application source and scripts, not the test suite; the tests are executed by pytest.

The subsequent model-v2 review found no confirmed high/medium blocker in trial-group rejection calibration, its evaluation/live call sites, or model-version propagation. The reviewer independently ran 22 targeted tests, lint and type checks. An additional regression verifies that changing validation features cannot alter fitted rejection thresholds. Unfamiliar-pose BOOKMARK acceptance remains a measured limitation, not a closed defect; see PILOT_RESULTS.md.

The later assignment-readiness review found three documentation/evidence issues: collection examples omitted the known working camera index, an actual interface screenshot was missing, and the local agile board still described negative collection as unfinished. All three were corrected. Fresh-source setup testing also exposed PowerShell interpreting pip's `-e` argument as a function parameter; explicit argument arrays fixed it and the complete setup script then passed. See `SETUP_CHECK.md`. Second-computer testing, participant submission permission and human submission signoffs remain open.
