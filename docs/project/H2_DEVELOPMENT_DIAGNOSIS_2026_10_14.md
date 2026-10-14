# H2 development diagnosis — 14 October 2026

Hau Jie reviewed Deston's 13 October private development handoff on `codex/hau-jie-profiles` after syncing `main` at `626e5ec`. This is attributed aggregate evidence, not a freeze, TEST result, Studio live-action result, or model-release approval. The participant files, full per-trial outputs and proposed configs remain local for private review.

The corrected complete returns each contain 48 TRAIN, 48 VALIDATION and 8 UNKNOWN trials. P67 retains 505/520 valid sample slots; P1543 retains 497/520. P69 is closed at TRAIN only (48 trials, 240 valid samples), so is neither a complete evaluation participant nor part of the proposed starter. A separate failed P06 return was not used. P67's pose, prior-fit/tuning exclusion and break were confirmed in Deston's intake. P1543's prior-fit/tuning exclusion and actual break before VALIDATION still require confirmation; session timestamps and generic condition notes cannot establish them.

P1543's saved baseline was reproduced with the supplied config and fresh output. For both kNN and SVM, confusion matrices, all sample predictions, thresholds, macro-F1 and negative acceptance matched the supplied report. At multiplier 2.0 and margin 1.5, each had 15/48 correctly accepted validation trials, macro-F1 0.382, 0/12 correctly accepted NEUTRAL trials and 10/40 UNKNOWN sample slots accepted as BOOKMARK. These are classifier predictions, not observed physical poses or live actions. Before rejection, SVM's raw trial labels were 48/48 correct and kNN's 43/48. NEUTRAL was mainly rejected on margin (kNN 56/60 slots, SVM 58/60), which accounts for an important part of the validation miss.

At the same baseline settings, P67 had 35/48 correctly accepted trials, macro-F1 0.778, only 2/12 NEXT trials correct and 14/40 negative sample slots accepted as commands. NEXT had 16/60 accepted sample slots under each algorithm; kNN rejected 28/60 on margin and 16/60 on distance, while SVM rejected 36/60 on margin and 8/60 on distance. Numeric records alone cannot establish a physical pose cause.

A bounded development comparison kept both rejection checks enabled, using default kNN/SVM estimators, multipliers 1.5/2.0/2.5 and margins 1.1/1.25/1.5/1.75 (24 settings per person). Illustrative candidates for Deston's review—not final settings—were P67 kNN at 2.5/1.75 (36/48 correct, macro-F1 0.790, NEXT 2/12, 12/40 negative command slots) and P1543 SVM at 2.5/1.25 (26/48 correct, macro-F1 0.667, NEUTRAL 6/12, 10/40 negative command slots). Exact evaluator reruns agreed with the bounded reader's aggregate counts. No examined setting eliminated negative command acceptance. The figures are development-selection results and do not establish independent performance or safety.

The private paired-comparison proposals retain the original fixed H1 P01/P02/P03 starter inputs and baseline settings, while keeping P67 and P1543 entirely out of starter fitting and tuning. They have not been frozen. The old H1 manifests lack a `pose_set_id`, so the standard-pose declaration still needs physical review. Deston must confirm P1543 eligibility and the matching browser TEST acquisition route, reproduce and review the private configs, then decide whether to freeze before any untouched TEST. No TEST was opened or scored. Deston received and verified the separate H1 private archive on 14 October; this H2 record does not replace it.

## Deston's receipt and reproduction review — 14 October

The received H2 archive passed safe-path, duplicate-name and CRC checks. The
original development handoff's 17 file checksums were verified, and the two
manifest/feature pairs matched those used in the supplied reports. Eight fresh
evaluator runs reproduced sample predictions, trial confusion, macro-F1,
rejection thresholds and reference distances. All 48 bounded comparison rows
were independently refitted and reproduced, including rejection reasons and
negative-command counts. Timing and generated model identifiers were not treated
as deterministic comparison fields.

[PR #31](https://github.com/Chi944/GestureForge_304/pull/31) was reviewed and
merged with no blocking findings in its evidence-only change. Receipt details,
archive digest, remapped **unfrozen** proposals and full reproduced outputs stay
local. The archive supplied no member-checksum manifest of its own; the locally
recorded ZIP hash identifies the received bytes, not sender authentication.

This completes the H2 diagnosis receipt/reproduction substep. It does not select
settings, freeze either comparison, approve LIVE use or complete GF-P17/GF-P18.
Negative command sample counts are classifier results, not measured live false
actions. No TEST was opened or scored.

**Subsequent user confirmation, 14 October:** P1543 was excluded from earlier
starter training/tuning and took a break before VALIDATION. The user also
confirmed all four original H1 right-hand poses match the browser protocol:
open palm = NEUTRAL, fist = NEXT, thumb up = PREVIOUS, index/middle fingers
extended = BOOKMARK. These resolve the two eligibility facts and the physical
mapping question raised above. They are attributed confirmations, not facts
inferred from numeric samples. Setting selection and the reviewed acquisition
route still precede a freeze and any new TEST recording.

**Later 14 October acceptance:** the independently reviewed
[selection and freeze record](H2_EVALUATION_SELECTION_2026_10_14.md) now pins both
comparisons and records software verification of the TEST route. GF-P17 is Done
against its original preparation criterion. The earlier unfrozen status above
describes the received proposal; it is preserved as history. GF-P18 still needs
real untouched TEST, and no deployment or LIVE approval is granted.
