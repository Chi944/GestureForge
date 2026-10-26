# Selected personal profile recognition disposition

26 October 2026. **GF-P21 assessment complete with limitations.** The selected
P01 profile remains unchanged for the disclosed, manually approved demonstration.
This closes the bounded recognition assessment and affected checks defined in
[Revision 5](PROJECT_PLAN.md); it does not award automated Practice qualification
or accept the native-device release. GF-P18 and GF-P20 are complete.

## Evidence reviewed

- The selected right-hand kNN profile uses distance multiplier **1.5** and
  ambiguity margin **1.5**. Its identity matches the saved Practice and GF-P20
  captures. The existing validation/reload receipt records **48/48 validation
  trials** and **240 reproduced predictions**. TRAIN contains **47 trials**;
  its missing NEUTRAL trial and incomplete flag remain disclosed.
- Actual automated Practice remains **19/22**: two inconclusive capture windows,
  one complete-coverage G3 miss and zero negative actions. Deston's separate
  manual acceptance of 22/22 changes GF-P16's project criterion only. Original
  outcomes and runtime readiness gates remain unchanged.
- The [GF-P20 evaluation](P20_EVALUATION_2026_10_26.md) retains separate hold,
  negative, workflow and visual-latency recordings. Fresh reproduction verified
  all **2,669 JPEG frames**, replay/runtime agreement, **16/20 responses**, four
  misses and the conditional successful-response p95 **0.515–0.718 s**.
- Fresh affected checks: **57 tests passed** across `test_controller.py`,
  `test_replay_controller.py`, `test_features.py` and `test_app_personal_live.py`.
  No new physical recording or model search was performed.

## Four missed attempts

Direct replay through the current controller establishes the following transitions:

| Hold | Frame | Observation and resulting protection |
| --- | --- | --- |
| 1 | 83 | A Left-handed detection for the Right profile immediately resets READY to WAIT_NEUTRAL. |
| 9 | 1185 | Classifier rejection lasts 0.547 s, exceeding the 0.5 s grace; READY resets to WAIT_NEUTRAL. |
| 12 | 1624 | Classifier rejection lasts 0.515 s, exceeding the grace; READY resets to WAIT_NEUTRAL. |
| 18 | 2477 | An accepted G3 arrives after 0.547 s of rejection. The expired grace is checked first, requiring fresh NEUTRAL. |

At frames 1185 and 1624 the literal reset reason is `margin_rejection`;
grace expiry explains why that rejection resets readiness. The existing private
diagnosis describes the mechanism. Original traces are not rewritten.

`Controller.process` deliberately resets non-classifier invalid observations
immediately and requires rearming after sustained classifier rejection. The
recorded outcomes agree with these rules. There is no demonstrated controller
defect to fix, no established autofocus cause and no evidence that relaxing
thresholds would improve safety. Requiring fresh NEUTRAL remains intentional.

## Decision and remaining boundaries

Retain the selected profile and protections, document intermittent rejection,
and provide manual fallback. Do not restart the failed P02 replacement experiment,
tune consumed TEST, change settings, or repeat the whole Practice merely to seek
a better score. Failed frozen TEST and development candidates remain in the
methods/results record. A new investigation needs a specific reproduced defect.

GF-P21 is accepted as completion of this bounded assessment, with the recognition
limits explicitly dispositioned. It is not a claim of universal reliability,
95% all-attempt sub-second response, automated qualification or native Mac support.
Hau Jie's original recognition work remains credited; Deston's integration review
with Codex supplied this final saved-evidence reconciliation. No new Hau Jie
physical test or sign-off is implied.

This closes the recognition dependency for GF-P24. GF-P19/GF-P22 native checks,
GF-P23 Windows installation/stability, GF-P25 genuine video, GF-P26 final submission
review and GF-P27 upload/download verification remain separate gates.

Private original recordings, numeric inputs, review scripts and hashes remain
local. The earlier validation receipt was inspected rather than refitted in this
review; the visual onset annotations were reproduced, not independently reannotated.
