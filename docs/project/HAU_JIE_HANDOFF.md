# Hau Jie implementation brief

You own recognition and personalisation for GestureForge Studio. Build the reusable AI and profile components; Deston owns integration and final acceptance. Read `TEAM_GUIDE.md` and `CONTRACTS.md` first. Work is assigned for the project due 7 November 2026; the assignment is already submitted.

## Active task — personal release, Revision 5, 24 October

**Updated 25 October: the bounded P02 repair is complete and failed. Stop that
experiment.** The [repair disposition](P02_NEUTRAL_REPAIR_2026_10_25.md) preserves
Original and the failed candidate. Independent review verifies all 22 payload
hashes, 520 sample predictions and 104 trial outcomes. Historical NEUTRAL falls
from 6/8 to 0/8; historical macro-F1 falls from 0.936508 to 0.651003; negative
command predictions increase from 53/60 to 54/60. Neither model is LIVE-qualified
by these results. Do not repeat the splice, install the candidate, relax gates,
rerun participant TEST or ask for another twenty-trial diagnostic.

1. **GPT now:** sync reviewed main into `codex/hau-jie-profiles`, preserving
   private work. Retain the explicit failure and limitations in your methods.
   No additional candidate or broad model search is assigned.
2. **Next release option, Deston volunteered:** Deston will enrol a fresh
   complete four-pose profile under consistent demo conditions,
   with separate TRAIN and VALIDATION sessions. Preserve Original. Pin kNN,
   multiplier 1.5 and margin 1.5 before capture using an explicit default launch;
   do not inherit the loaded P02 profile's margin 1.0. Check fixed validation
   before attempting the existing 22-window Practice, and retain failures. This
   is coherent new onboarding, not a proven repair or permission to tune TEST.
   Update: separate new TRAIN has 47 complete trials / 235 valid samples;
   VALIDATION has 48 complete trials / 240 valid samples. Fixed validation is
   48/48 correct (macro-F1 1.00). Saved-profile reload reproduces all 240
   predictions. TRAIN is one NEUTRAL trial short, with its incomplete flag
   retained. Earlier small/interrupted sessions are preserved and excluded.
   No negative-validation or Practice pass is claimed. Next is the existing
   full 22-window Practice, then observed workflow; no model search is assigned.
3. **Manual work in parallel:** operate laptop B for the remaining guide-only
   installation, offline core, uninterrupted measured 30-minute full Studio run
   and shutdown/reacquisition checks in the
   [Windows case matrix](JAVIER_WINDOWS_REMAINING_CASES_2026_10_25.md).
   Your camera-off window close and subsequent five-frame camera-0 reacquisition
   are received as bounded evidence. They do not establish active-capture
   handoff, Studio's exit code, fresh guide-only setup or continuous endurance.
   Use the reviewed [full Studio monitor](../USER_GUIDE.md#measure-the-full-studio-stability-run)
   with a new output filename; it records same-run measurements. Do not substitute
   the headless capture diagnostic or earlier gapped responsiveness samples.
4. **Final handoff:** reconcile methods/results once the chosen release profile
   and affected workflow checks are known. Keep Word, data and full logs private;
   send focused code/sanitized-evidence PRs for Deston's review. Aim for complete
   handoff by 29 October; avoid repeated report redrafts before results exist.

Shared-starter delivery, interviews, new recruitment and broad recognition
searches remain deferred. GF-P21 checks the chosen personal release profile and
its affected behaviour; success for every research participant is not required.
Its GF-P20 dependency and GF-P24's final reconciliation remain. No current
LIVE-qualified profile is proven. Your accepted progress remains **63/75 (84.0%)**.
The dated instructions below are historical where they conflict with this section
and [Revision 5](PROJECT_PLAN.md).

## Next delivery — assigned 7 October

**Current next delivery — 24 October, after PR #36 and the new private packet.**
Your 20-trial diagnostic and handoff are complete. Deston independently reproduced
all 100 predictions, section metrics and geometry; see
[the integration decision](P02_GAP_DIAGNOSTIC_2026_10_24.md#independent-integration-and-next-experiment).
Do not repeat that diagnostic or resend either received P02 packet.

- **GPT now:** prepare your existing predeclared proposal for at most one isolated
  selected-label TRAIN candidate. Keep Original, settings and all evaluation input
  hashes fixed. The existing flow replaces 40 NEUTRAL samples with 10, retains
  40 samples in each action class and refits the scaler across all classes.
  Compare all classes on both historical/new validation and each negative
  condition, using your existing strict stop rules. Never train on validation or
  TEST, search thresholds, install automatically or claim a LIVE pass.
- **Your manual part:** if you consent to new numeric recording, check the correct
  webcam view and full intended open-palm pose, record actual conditions, then use
  Repair pose for just two new NEUTRAL TRAIN trials. Preserve invalid/cancelled
  attempts and stop for review if incomplete; do not silently retry or expand.
  Return the new TRAIN pair, candidate receipt and fixed comparison privately.
- **Device work in parallel:** continue laptop-B's remaining guide-only install,
  measured uninterrupted 30-minute stability, shutdown/release and Javier-assigned
  native cases. Do not rerun unchanged successful cases or bypass gesture readiness.
- **Methods:** incorporate the independently verified 0.666667 result, 53/60
  negative command predictions and all limits. Your updated Word draft's visual
  QA was not supplied as passed; send it privately once ready for visual review.
- **Dates:** aim for the recognition disposition by 26 October and final handoff
  by 29 October, supporting Deston's 31 October submission target. The official
  deadline is 7 November; retain failures rather than imply qualification.

Continue on `codex/hau-jie-profiles`; focused PRs go to Deston for review/merge.
No interviews or repeat participant TEST are assigned. GF-P21/GF-P24 retain their
original final checks and dependencies; accepted task weight remains 63/75.

### Historical baseline preparation — superseded by the delivery above

**24 October — exact P02 packet received and Original baseline reproduced.**
Read [the verified result and next diagnostic](P02_PROFILE_REVIEW_2026_10_24.md).
All 13 payload hashes, exact saved model identity and supplied predictions
reproduce. Your file-handoff and baseline-reproduction substeps are complete;
do not resend them or search again for the absent old negatives/repaired profile.

- **Result:** macro-F1 0.936508 belongs to P02 Original, not a repaired model.
  All action trials pass, but two of eight NEUTRAL trials become G1. The recorded
  stricter-margin result also reproduces at 0.720879, losing genuine recognition.
  Matching negative-validation data were not supplied; false-command performance
  is unmeasured. Keep saved settings and TEST unchanged.
- **Next with GPT:** prepare the existing collector for the linked fixed
  `p02-gap-v1` plan: eight positive-control trials and twelve index-only negative
  trials, using the original vocabulary and two new private output folders.
  Verify camera, paths and consent before recording. Afterwards score the new
  inputs against exact Original TRAIN/settings; no search or automatic replacement.
- **Your manual part:** if you agree to new numeric recording, follow those
  twenty trials (roughly 5–8 minutes including setup; estimate only). Record actual
  conditions and deviations, retaining invalid trials and interrupted-attempt
  notes. This fills the labelled negative-condition gap; no full Practice or
  participant TEST repeat is requested. Continue laptop-B remaining checks with Javier.
- **Methods:** incorporate both verified fixed results, the NEUTRAL errors and
  absent negative measurements into your existing private contribution. Deston's
  local report is refreshed; final GF-P21 reconciliation still remains. Native
  `0x8001010d` cause/termination is unresolved; preserve fault evidence if it recurs.
- **No stakeholder interviews:** use the completed secondary research for the
  problem rationale. Actual software/device checks remain engineering tests.
- **Acceptance:** baseline reproduction is complete; GF-P21/GF-P24 retain their
  original affected-check/dependency gates. Deston 34/75 (45.3%), Hau Jie 63/75
  (84.0%), Javier 54/73 (74.0%); total 151/223 (67.7%), 19/29 tasks Done.

**22 October — your methods/results contribution and laptop-B packet are received.**
Both have been reviewed; do not resend reference [10] or redraft completed
sections. GF-P24 remains In Progress pending final GF-P21 reconciliation. See the
[receipt review](TEAM_DELIVERABLE_REVIEW_2026_10_22.md) and
[marker-feedback response](MARKER_FEEDBACK_RESPONSE_2026_10_22.md).

- **Manual:** operate laptop B for remaining guide-only installation, continuous
  thirty-minute rate/memory monitoring and post-close camera release. Coordinate
  unrun association/error and valid-grant active-capture Camera/focus cases with
  Javier. Retain successful unchanged checks, the first camera failure and the
  interrupted 791.605-second monitor; the later reported thirty minutes is separate.
- **Problem research updated 23 October:** Deston chose [secondary research](RESEARCH_POSITIONING_2026_10_23.md)
  instead of trainer interviews; no interview arrangement is assigned. Use its
  fatigue/background-motion limitations in the methods discussion. Continue the
  actual recognition and laptop-B checks; research does not replace them.
- **With GPT:** update the remaining-case matrix from received receipts; continue
  development-only recognition diagnosis and reconcile final methods/results.
  The source-member match remains attributed because the packet omits the source
  ZIP/member listing. No threshold relaxation, TEST tuning or blanket recollection.

Keep Word/data/full exports private. Push sanitized code/evidence only to
`codex/hau-jie-profiles`; leave PRs for Deston's review/merge.
The dated instructions below are historical where this update supersedes them.

**19 October update: the fixed representation experiment is complete.** Deston's
integration track implemented it with GPT assistance and independently reproduced
both conditions on the existing DEVELOPMENT data. You retain recognition ownership;
this is not attributed to a new submission by you. Do not build the same comparison
again. Read [the results and decision](GF_P21_DEVELOPMENT_DIAGNOSIS_2026_10_15.md#executed-comparison-and-next-handoff--19-october).

- **With GPT now:** review the per-class findings and add them, with the failed
  frozen TEST results, to your private GF-P24 methods/results contribution. P67's
  validation macro-F1 changes 0.790 → 0.854 and negative command predictions 12/40
  → 9/40, but PREVIOUS loses one correct trial. P1543 changes 0.667 → 0.655;
  negatives fall 10/40 → 0/40, but NEUTRAL recall falls 6/12 → 1/12 and one
  NEUTRAL sample is accepted as NEXT. Neither experimental personal model meets
  0.90. No new model is approved for Studio.
- **Recognition follow-up:** the [P03 traces are received and reviewed](P03_TRACE_REVIEW_2026_10_19.md).
  Current-controller replay matches four PREVIOUS Preview simulations and two
  additional NEXT simulations during the reported index-finger negative attempt;
  the second summary is cumulative six, not ten. The confirmed saved profile is
  Right/kNN, multiplier 1.5, margin 1.0. Margin 1.0 disables ambiguity rejection
  by design; this does not establish that increasing it fixes the false NEXT.
  The private P03 profile/DEVELOPMENT packet is now received and its exact saved
  model revision reproduced. Read the fixed-setting comparison in the P03 review:
  PREVIOUS improves 2/8 → 5/8 and macro-F1 0.8500 → 0.9423 on the reused original
  validation; negative command samples fall 10/40 → 4/40, all remaining errors
  from older OK-sign samples. Older index samples are all rejected, so they do
  not reproduce the recent live index failure. Coordinate private packet access
  with Deston, not a resend or recreation from Javier. Review this diagnosis and
  distinguish the remaining live-feature gap from the reproduced OK-sign issue.
  No repeat short trace, blanket recollection or threshold change is requested.
  Predeclare any further DEVELOPMENT experiment; do not
  repeat the old search, tune consumed TEST, convert profiles to the experimental
  representation or relax thresholds simply to pass Practice.
- **Manual now:** coordinate with Javier and operate your Windows laptop as
  laptop B for the remaining native, fresh-install, offline, thirty-minute Studio
  and clean-shutdown cases. Use reviewed main or a source ZIP built from it and
  `run-studio.cmd` after setup. The 16 October ZIP predates the new session/status
  feedback fixes; record the actual build and rerun only affected checks.
  Manual cases need no recogniser; gesture cases require your own profile and a
  genuine current-session Practice pass. No new P67/P1543 TEST or P69 recording
  is requested.
- **Return next:** your recognition review/private Word contribution and observed
  laptop-B results to Javier. Submit only demonstrated code fixes or sanitized
  evidence on `codex/hau-jie-profiles`, with a focused PR left unmerged for Deston.
- **Verification:** use `python scripts/verify.py --timeout 1200`; keep its fresh
  ignored output with the exact source version. Existing output files are refused.
  Saved-profile settings stay unchanged; new Studio profiles inherit the current
  multiplier/margin as repaired on 16 October.

GF-P21 remains In Progress with its original GF-P20 dependency. The experiment is
reviewed development evidence, not native or deployment acceptance. At that historical checkpoint progress was
Deston 26/75 (34.7%), Hau Jie 63/75 (84.0%), Javier 48/73 (65.8%), team 137/223
(61.4%); 17/29 tasks Done. Full data/results and Word contributions remain private.
See the [shared task split](TEAM_GUIDE.md#current-manual-and-gpt-ready-work).

**Earlier 14 October H2 review checkpoint (before TEST returns):** [PR #31](https://github.com/Chi944/GestureForge_304/pull/31)
is merged. Deston checked 17 original source-file hashes and independently
reproduced eight evaluator runs and all 48 bounded candidate rows. P67's proposed
kNN settings (2.5 / 1.75) give development macro-F1 0.790 with 12/40 negative
sample predictions accepted as commands; P1543's proposed SVM settings
(2.5 / 1.25) give 0.667 with 10/40. These are sample predictions, not live
actions. Neither candidate qualifies for deployment. Deston retains the H2
proposals under the explicit after-development policy in the independently
reviewed [selection record](H2_EVALUATION_SELECTION_2026_10_14.md). Both private
freezes, their input/settings pins and four participant-specific package hashes
are verified. Full verification passed 952 Python tests, 30 Node checks, lint,
types, both startup modes and synthetic evaluation, with one Windows symlink
skip and the expected duplicate-ZIP test warning. **GF-P17 is accepted:** your
accepted total is 63/75 (84.0%); team acceptance is 127/223 (57.0%), 16/29 tasks.
At that checkpoint GF-P18 still needed actual TEST returns. Those have since
been received and scored; the current instructions and accepted totals above
supersede that waiting step. Windows automation does not establish native Mac
camera/recovery behavior.

**14 October provenance confirmation:** Deston confirmed P1543 was excluded
from earlier starter fitting/tuning and took an actual break before VALIDATION.
He confirmed all four H1 right-hand poses match the browser protocol: open palm
= NEUTRAL, fist = NEXT, thumb up = PREVIOUS, index/middle fingers extended
= BOOKMARK. These user-confirmed facts supersede the unanswered items in the
dated 13 October notes below; they are not evaluator-observed facts.

**13 October newest return:** a third contributor completed all 104 development
trials on macOS/Safari with no reported collection problems. Import retains all
520 scheduled records, including 23 invalid detections (497 usable features).
The user confirmed the supplied poses. Exclusion from earlier starter fitting
and tuning, and the break before VALIDATION, have not yet been confirmed; recorded
condition notes are too general to establish actual lighting, distance or posture.

There are now two complete development returns plus the closed TRAIN-only
contribution below. Audit these existing returns before requesting more
development recordings. The new return's baseline kNN and SVM (multiplier 2.0,
margin 1.5) each scored
validation macro-F1 0.382, with all 12 NEUTRAL trials rejected and 10/40 negative
sample predictions accepted as commands. These are development classifier results,
not live actions or final TEST. Diagnose the saved rejection/pose evidence, then
propose bounded settings for review; do not enable a model or lower targets to
hide these results. The private diagnostic found raw SVM trial labels correct
on 48/48 before rejection (kNN: 43/48); both retained only 15/48 correct trials
after rejection. All ten accepted negative predictions were BOOKMARK. Investigate
this trade-off rather than disabling rejection. Keep both complete contributors out of starter fitting and
tuning if they will serve as the two independent evaluation participants.

Deston confirmed sending `GestureForge_PRIVATE_Development_Handoff_20261013.zip`
to Hau Jie on 13 October. It contains
the original returns, corrected numeric imports, intake notes and the new
baseline/diagnostic. Follow its `READ_FIRST.txt`; it is a data handoff, not the
participant collection app or an approved freeze packet. Pull current `main`
before analysis. Do not merge these corrected imports with earlier copies of
the same collections. The earlier complete contributor's independence, poses
and break are already confirmed; only the newest return's independence and
break still need confirmation. No additional recording is requested now.

**13 October collection decision:** Deston has closed the second contributor's
collection: use the existing 48 TRAIN trials (240 usable samples), with no further
recording requested. The macOS/Safari return remains a partial import because
VALIDATION and UNKNOWN are absent. The reported symptom was that clicking Start
Selected Session for VALIDATION did nothing; its exact cause is unverified.

Use these samples for TRAIN-only development, preserving their original splits
and provenance. Do not request recovery, recollection or TEST from this person.
Before pooling them into a shared starter, audit the available pose/provenance
records; a successful import does not establish physical pose equivalence.
Anyone included in fitting or tuning cannot be an unseen participant for that
model. This closed contribution cannot replace a complete independent evaluation
participant. Review the two complete returns' eligibility before planning TEST.
TEST still follows Deston's reviewed freeze. The private H1 packet is already
received and verified as internal-team evidence, not a deployment approval.

**11 October:** use the [manual/GPT task split](TEAM_GUIDE.md#current-manual-and-gpt-ready-work)
to separate participant and laptop work from coding-assistant preparation.

**8 October PR #27 review, updated 14 October:** your [saved-report D1 audit](H1_SAVED_REPORT_AUDIT_2026_10_08.md)
is reviewed and merged as attributed aggregate evidence. Do not repeat the audit
or the 48-setting search. Deston has received the private H1 packet and verified
hashes, saved reports, fixed cases and trial inventories against the supplied
private files. Starter approval remains empty, and the packet does not grant
public or marker redistribution permission.

Earlier planning identified two willing prospective Windows participants. Review
the received returns first; additional collection needs a specific uncovered gap.
Before any additional collection,
confirm each person's consent and exclusion from earlier starter fitting/tuning,
and complete the extracted Windows kit camera/export/import check. Then use H2:
about 5-6 minutes TRAIN, 5-6 minutes separate VALIDATION and one minute UNKNOWN;
allow 15-20 minutes plus a break in total. This advances preparation, not H2
acceptance or final TEST. The received Mac returns now provide collection
evidence, with P69's interruption retained; they do not establish Windows or
native Studio acceptance.

**8 October participant-kit handoff:** use the collection-only Windows/macOS
ZIPs and PDF guides described in [PARTICIPANT_KITS.md](PARTICIPANT_KITS.md) for
H2's two new independent participants. Allocate pseudonyms; confirm consent,
team/private-marker access and retention individually. Coordinate one extracted
kit camera/export check per OS before broad distribution. Have participants send
the recorder's `EMAIL_THIS_*_development.zip` privately to Deston; do not request
their program folder or any Python installation. Import and audit all scheduled
slots, including invalid/partial ones, before selecting personal settings. These
browser recordings identify their runtime separately from native inputs. Final
TEST is excluded until Deston freezes the development packet. This preparation
does not replace the verified H1 multi-person starter audit packet or earn H2
completion before actual participant data and freeze review exist.

Work through the remaining H3/H4 deliveries and GF-P21 diagnosis separately.
H1/H2 are retained below as completed evidence boundaries. The current guidance
supersedes older recording instructions; no new participant recruitment is
requested for the completed GF-P17/GF-P18 comparison.

| Priority | Work you execute | Return to Deston | Completion boundary |
|---|---|---|---|
| H1 — private audit handoff | The aggregate D1 audit is merged in PR #27. The prepared `H1-20261008` packet was received and verified on 14 October; do not repeat the audit or 48-setting search. | Permitted numeric manifests/sidecars, matching baseline/comparison and all-six-fold/fixed-case reports, hashes, session/source details and permission scope are now fixed internal evidence. | Complete as a handoff substep only. The aggregate audit does not approve a deployment starter or public/marker redistribution. |
| H2 — independent evaluation inputs | GF-P17 and GF-P18 are accepted after verified preparation and independently reproduced scoring of both actual TEST returns. Each has 48 trials / 240 slots, retaining P67's three invalid samples. | Preserve the frozen inputs and failed comparison; no further participant TEST session, repeated collection or unchanged packet resend is requested. | Experiment completion does not qualify deployment. The two TEST sets are consumed and must not guide threshold tuning, model selection or configuration optimisation. |
| H3 — operate laptop B | Follow Javier's agreed GF-P19 matrix and the [Windows guide](../WINDOWS_LAPTOP.md) on your physical laptop. Use a fresh setup, local bindings and the same identified build. Run offline core, thirty-minute Studio stability and clean shutdown checks for GF-P23. | Per-case outcomes to Javier: actual operator/device/build/package identity, help or guide deviations, failures/retries, duration, observation rate, peak memory, shutdown and private evidence references. Explicitly identify anything unmeasured or unrun. | Manual cases need no model. Gesture cases use your own profile and full current-session Practice gate. Javier consolidates; Deston accepts after the original defect gates. |
| H4 — report preparation | Draft GF-P24 methods, data protocol, algorithm trade-offs, rejection, attribution and limitations now from the implemented code and saved evidence. Include the scored GF-P18 results now; reconcile later defect findings after GF-P21. | Local Word methods/results contribution and verified reference list through the team's existing channel; measured and unmeasured results clearly separated. | Keep Word documents/data/logs out of Git. A methods draft is useful now; GF-P24 is Done only when final results and limits match the evidence. |

**Next handoff:** return the GF-P21 development-only diagnosis and private
GF-P24 methods/results contribution; send actual laptop-B outcomes to Javier.
PR #27 and the verified private H1 packet already supply the starter audit;
PR #31 and the reproduced H2 packet supply the development diagnosis. GF-P18's
actual frozen TEST results are now accepted, including the failed targets.
Do not repeat completed audits or ask participants to improve their TEST scores.
If a file or device is unavailable, state the exact gap and continue independent
work. No new collection is justified without a diagnosed development need and
a separate evaluation plan.

**8 October first private handoff to Deston:** provide the existing complete
multi-person consented numeric manifests and NPZ sidecars, or the exact missing
status for any item. Include the fixed default baseline report, the 48-candidate
comparison result reports, the saved diagnostic covering all six folds and the
fixed ten cases, or the exact reason any report is absent. Include configuration,
source/dependency/input hashes, pose descriptions, session provenance and
permission scope, including the standard IDs `NEXT/PREVIOUS/BOOKMARK/NEUTRAL`
and Right hand required by the starter contract. Send private data only through
the team's private folder/archive; never put it in GitHub or Trello. The PR on `codex/hau-jie-profiles`
should contain only sanitized aggregate evidence and stay unmerged for Deston's
review. Do not record new starter data until D1 identifies a diagnosed need.
Preserve the original input labels and report any mismatch; the listed IDs are
the release contract, not permission to relabel existing recordings silently.

Copy this next private message to Deston:

> GF-P18's actual frozen TEST comparison is accepted, with failed targets retained.
> I will continue from the reproduced DEVELOPMENT rejection diagnosis and
> preserve the original settings/results. I will not tune or select on TEST or
> request repeat TEST collection. In parallel I will operate laptop B for Javier's
> agreed native/offline/stability cases and add the scored outcomes and limits to
> the private methods/results contribution. GF-P21's final acceptance still needs
> its original GF-P20 dependency. No unchanged H1/H2 resend is needed.

For H2, follow the existing freeze-and-score commands in
[PAIRED_EVALUATION.md](PAIRED_EVALUATION.md). Preserve the freeze file and hashes
as the historical pre-TEST record. Both TEST comparisons are now complete;
keep the frozen files unchanged. A qualifying deployment starter is a separate
R15 deployment gate, not a prerequisite for reporting an honest failed comparison.
Do not identify existing development contributors as unseen participants. The
existing audit packet supports the D1 decision now; a deployable starter release
candidate still requires qualifying person-separated independent results and
explicit permission to distribute the bundle. Internal access for review is not
redistribution approval.

Every PR must name the task IDs, base/source commit, changed files, actual check
results, evidence limits and private handoff references. Push only
`codex/hau-jie-profiles`, open a PR to `main` and leave it for Deston's review.
Deston retains shared-shell changes, freeze approval, integration and acceptance;
delegated execution does not change the original task weights or Done status.


**Starter integration update, 5 October:** Deston implemented the approved-release loader and separate standard six-action LIVE gate. No candidate is enabled: the recorded 48-setting comparison found none qualifying. Diagnose the existing starter through the saved private D1 audit; use selected-pose repair only for a diagnosed own-profile need. H2's new independent evaluation and H3/H4 can proceed separately. A later deployment release needs the exact frozen TRAIN manifest/sidecar, all estimator settings, expected rebuilt revision, person-separated evidence and distribution permission for review. See CONTRACTS.md. Keep existing private inputs private.

GF-P16's standard-gesture path remains blocked wherever it depends on a
qualifying deployment starter (R15); GF-P10 software is accepted. Personal LIVE software and manual workflows can
continue under their separate Practice, explicit LIVE and native-evidence gates.

## Laptop B assignment confirmed 5 October

**9 October update:** Javier's [PR #28 restore retest](../evidence/GF_P19_HARBOR_RESTORE_LAPTOP_A_2026-10-09.md)
is merged as laptop-A evidence on `a1bb37a`. Both restores returned to Preview;
the camera stayed off. This does not replace your laptop-B checks or cover
active-capture handoff. Coordinate only your remaining device cases with Javier.

**12 October update:** Javier's [PR #29 camera/focus record](../evidence/GF_P19_CAMERA_FOCUS_LAPTOP_A_2026-10-12.md)
is merged as bounded laptop-A evidence on `ffa0af7`. It covers isolated Preview
focus pause/reconnect, Camera Preview simulation, native Camera opening after
capture was already off and later Preview reacquisition. Do not repeat those
laptop-A cases. It does not replace your laptop-B run and does not cover
active-capture native Camera handoff, selected trusted `.exe`, missing
association, native failure/retry or historical real-launch restore/no-replay.

**7 October clarification:** Javier's PR #26 is accepted as partial laptop-A
evidence. Its conflicting operator statement was corrected during review:
you still operate laptop B and Javier coordinates. No laptop-B result was
included. Do not repeat his accepted laptop-A checks or the full starter search;
continue your D1 saved-report diagnosis and your assigned device checks.

For the integrated restore check, sync the current main before testing:
Restore session and Restore progress must return Live mode to paused Preview,
preserve saved stage/card/bookmarks and launch nothing. Explicitly select Live
and Apply and pause again before continuing manual real actions. Record your
own device result; the regression test alone is not native acceptance.

Your physical Windows laptop is **laptop B**. Javier's existing computer remains laptop A; he does not need to obtain another machine. You operate laptop B, Javier coordinates the GF-P19 case matrix and consolidates the evidence, and Deston reviews integration and GF-P23 release acceptance. Device assignment does not mean tests have passed or change the original task weights.

Use a fresh installation of the current Studio source package following `docs/WINDOWS_LAPTOP.md`; do not copy another computer's `.venv`, private targets or profile. Record the exact commit/package hash, Windows/Python versions, camera index, operator and any assistance. Bind your own local targets. Manual Harbor and shortcut checks need no profile. Gesture cases use your own consented profile and the existing current-session Practice gate; retain unrun cases when that gate is unavailable.

Coordinate with Javier using his brief's GF-P19 and GF-P23 procedures: target launch/error/recovery, focus return/no replay, actual active-capture Camera handoff, paused reload, then offline local operation and a thirty-minute Studio workflow with clean shutdown. For active-capture Camera, configure workspace/targets before any genuine same-session full personal Practice grant, then use explicit Live, Apply and pause, Start and fresh NEUTRAL before requesting Camera; if the grant is unavailable, mark that case NOT RUN and complete the manual cases. An HTTPS page itself is not an offline-core check. Preserve failures, retries, source identities and separate summary segments. Keep full traces, private paths and recordings local; send Javier the concise per-case outcomes and private evidence references through the team's existing channel. Attribute every observation to laptop B and you as operator. Do not repeat accepted laptop-A work.

Your next GF-P12 work is operator validation of the integrated **Repair pose** flow, not rebuilding the component. Use the verified private H1 packet as fixed internal evidence before any new starter decision. Do not repeat the D1 audit or 48-setting search unless a missing file or reproduced defect makes it necessary. No blanket data recollection is requested.

## Your branch and delivery rule

Create `codex/hau-jie-profiles` from the published `origin/main` before editing. Do not apply the old kickoff patch on top of it. If it already exists, switch to it instead. Commit and push only to this branch; never push to `main` or Javier's branch.

```powershell
git fetch origin
git switch -c codex/hau-jie-profiles origin/main
git branch --show-current
# After reviewing your changes, committing and passing the required checks:
git push -u origin codex/hau-jie-profiles
```

Before every commit/push, confirm the current branch is `codex/hau-jie-profiles`. Open a PR from this branch into `main`, request Deston's review, and leave it unmerged. Only Deston integrates approved work into `main`; do not force-push shared history.

## Supporting procedures and earlier integration evidence

Use the following recognition/profile procedures when H2 diagnosis identifies a
specific H3 gesture case requires them. They are not prerequisites for the new
H2 participant preparation or H4 methods draft. Fix a reproducible software fault
before repeating an affected recording; preserve earlier failures.

**Acceptance update, 5 October:** GF-P28 is Done as a completed feasibility
investigation with no qualifying starter. Review accepts your supplied
person-separated results and the recorded internal-use permission limits; it
does not claim an independent P02/P03 rerun or permit redistribution. Do not
repeat the spike simply to obtain a successful result. The later final-data and
configuration gate remains GF-P17.

**GF-P12 Repair pose integration:** use the delivered Studio **Repair pose** tab
only after diagnostic review identifies one weak label in your own saved profile.
The source is the installed saved profile; Guest/manual mode and ad-hoc manifests
are disabled. Collect 2-12 trials for the chosen label through shared
observation-only capture, then save a separate TRAIN candidate after reviewing
valid-slot and retained-class counts. Preserve unaffected classes, the original
dataset/profile, original dataset and reviewed collection hashes and permission
notes. Keep
UNKNOWN and held-out TEST samples out of training. `candidate_ready` opens
Profiles review; only explicit permission plus **Create and load personal
profile** trains/loads the candidate, paused in Preview with readiness expired.
Rollback by loading the original saved profile. This targeted-recollection path
is distinct from running another full human Practice attempt.

1. **Compatibility first.** Use your existing consented personal TRAIN manifest
   or saved profile. Check vocabulary, selected hand, feature version and
   model/settings revision; verify load, save/reload and preservation of the
   previous selection on a failed load. **Return:** the source revision,
   pseudonymous profile/data identity, actual settings, each outcome and any
   reproducible error. A workspace/deck selected as a dataset is a file-selection
   error, not a reason to recollect gestures.
2. **Short own-profile diagnostics.** Establish reliable load/start and fresh
   capture, then use individual five-second pose/NEUTRAL diagnostics as needed.
   For a recognition miss, retain coverage, prediction/rejection output and
   independent intended-pose notes; use the existing opt-in trace for the
   open-palm/LATCHED report. **Return:** actual correct/wrong/missed/inconclusive
   outcomes, timing/coverage and a focused reproduction. Stop to diagnose setup
   faults instead of restarting a full Practice run.
3. **GF-P07 accepted; do not repeat the walkthrough.** The reviewed generated
   UI montage closes the original software recording obligation together with
   your attributed PR #20/#22 physical collection/invalid/Stop evidence. Preserve
   those records. No new recognition accuracy or human Practice pass is implied.
   Your next repair task is the integrated selected-pose workflow specified above.
4. **GF-P12 after reliable setup.** Run the current `gf-p12-v4` 22-window protocol on your
   own profile only after the focused checks support it. **Return:** the full
   private Practice JSON reference, code/model/behaviour revisions, per-pose and
   negative-window outcomes, coverage, interruptions and Session summary event
   reconciliation. Retain every miss, inconclusive window and prior attempt;
   an incomplete attempt is evidence, not a pass. Verify all 22 windows are
   covered, every pose including NEUTRAL reaches 3/3 correct, there are no
   wrong or repeated activations and all ten negative windows are correct. Record
   whether saving, event reconciliation and paused restoration completed and
   whether the host granted personal LIVE eligibility. A blocked/failed result
   remains useful evidence; diagnose a software fault with a short reproduction
   before repeating the full run.

Put a concise outcome summary and exact software check results in a focused PR;
keep participant inputs, recordings and full result files private. Fix only your
owned modules and report shared-shell defects to Deston with the reproduction.
Do not ask Deston to repeat long trials for this lane. Your own-profile results
cannot replace or be labelled as Deston's P01 personal-performance evidence.
Request only narrowly targeted repair samples for a diagnosed collection defect.
Original task ownership/weights and acceptance criteria remain unchanged; neither
delegation nor a diagnostic result establishes readiness or LIVE permission.

**Personal LIVE boundary:** only the host's genuine current-session full pass
can grant eligibility, after terminal save, exact event reconciliation and
paused restoration. It is memory-only and pins profile/model/hand/camera,
behavior revision and exact workspace/stage/Quick Actions maps. Behavior, map,
target or camera edits expire it even if changed back; restarting Studio, Guest
and model reload clear it. Cosmetic renames, ordinary pause and existing context
selection retain it, but LIVE selection, Apply, explicit Start and fresh NEUTRAL
remain required. Short checks, diagnostics and historical/imported JSON cannot
grant it. This is software eligibility, not new participant or native acceptance;
standard gestures remain unavailable. Configure intended mappings before the
full run and keep your branch and evidence separate from Javier's.

**GF-P17 preparation, 5 October:** Deston is supplying the
[frozen paired evaluation tool](PAIRED_EVALUATION.md) and positive TEST collector
support. Reuse these rather than building another scorer. Keep all fitting and
tuning manifests, selected settings, hand and exact standard-pose descriptions
ready for review. New TEST data require a separate manifest and matching pose ID;
freeze before inspecting outcomes. Legacy development files stay unchanged.
The 7 October H2 assignment now makes this an immediate preparation task;
it does not request repetition of Deston's development recordings.

Latest integration, 4 October: sync main before recording. Practice v3 queues
Begin for up to two seconds while waiting for fresh capture/READY, and a
30-second setup timeout offers Retry setup without ending the attempt.
Setup retries are saved separately; measured misses/inconclusive windows are not
replaced. Four complete generated host sequences verify continuity, including
the latest P01 setup failure. These are software checks, not participant results.
Review negative cues in the new dialog before starting; keep NEUTRAL until the
measurement countdown begins. Preserve existing P01/P02 outcomes and inspect the
separate recognition misses before requesting repair data or changing thresholds.

Update, 3 October: [PR #20's camera pilot review](GF_P07_LOCAL_CAMERA_REVIEW_2026_10_03.md) is merged as partial evidence from a personal pilot, not as a new independent evaluation. Keep its completed recordings and results. Its 2/8 accepted NEUTRAL validation trials and kNN/SVM macro-F1 of 0.7209 belong to the same supplied Hau Jie private-pilot evidence stream; do not publish raw data, treat it as diagnostic, and do not lower rejection thresholds or relax neutral-hold/rearm policy on this pilot alone. Sync current main and run `scripts/check_environment.py --model` before the remaining live Enrolment checks: visible invalid feedback, Stop during an active hold, preserved partial slots and save/reload. The shared camera now loads model bytes to avoid a reproduced Windows Unicode model-filename failure. Your original fatal runtime-path error was not reproduced here; use the [Windows recovery instructions](../WINDOWS_LAPTOP.md) if it persists. PR #21 supplies GF-P12's rehearsal component; Deston has attached it as Studio's Practice tab, with a saved historical event review under Session summary. At that historical point targeted pose repair was still missing; PR #25 is now integrated and accepted for the selected-pose repair software criterion. Actual own-profile Practice outcomes remain separate evidence.

Bounded neutral update, 3 October: Hau Jie reports that open palm sometimes remains LATCHED and some movement can recover it. The screenshot supplied with the report does not show the Prediction field, so do not infer a resolved root cause from it. Deston's shared UI fix now keeps prediction, rejection reason and hold guidance visible in the footer, and accepted fresh packets clear stale errors, but the actual intermittent open-palm report remains unconfirmed. Your next recognition task is evidence capture: after fetching/merging main into your own branch, record a short reproduction using the existing opt-in `EvaluationTrace` in Preview/Rehearsal. `EvaluationTrace` records consumed predictions, acceptance flags, rejection reasons, timestamps and snapshot; it does not store the physical intended pose or controller/readiness state. In local notes, separately mark intended open-palm intervals and the displayed Prediction/hold/rejection/readiness state you observe. Do not capture images or feature vectors. Run `python -m gestureforge.trace_diagnose <localtrace.json>` from the repository root to write a current-controller reconstruction under ignored `experiments/local/controller-diagnostics/`. Compare it with the independently recorded intended-pose/display notes and code revision; the tool cannot infer physical pose or score accuracy/readiness. Compare rejected NEUTRAL samples with accepted continuous 0.3-second/gap behaviour from the actual trace before proposing threshold, dataset or neutral-policy changes. Do not request blanket recollection or automatic dataset publication; ask only for targeted repair data if the trace diagnoses a collection defect.

GF-P03 was reviewed and merged in [PR #10](https://github.com/Chi944/GestureForge_304/pull/10) on 30 September; PR #13's evaluator and baseline checkpoint are also merged. Your GF-P06 persistence component from [PR #14](https://github.com/Chi944/GestureForge_304/pull/14) is reviewed and integrated, including an integer/float setting canonicalisation fix that preserves model revisions on reload; 49 targeted profile tests passed at that checkpoint. PR #17's [selector](PROFILE_SELECTOR_HANDOFF.md) is attached in Studio's Profiles tab. PR #19 supplies the bounded comparison; preserve accepted enrolment evidence and continue targeted repair plus own-profile Practice without rebuilding storage, the selector or the evaluator. Fetch and merge `origin/main` into your existing branch before the next change, preserving any local work.

Update, 2 October: PR #13's participant-separated evaluator and [checkpoint](STARTER_EVALUATION_CHECKPOINT.md) have been reviewed and merged after correcting the description of private input sidecars. Integration verification passed 346 tests with one platform-specific skip, lint, types, both GUI smoke checks and synthetic evaluation. Your checkpoint reports P01 checksum validation and completed P02/P03 collection. Those participant measurements are attributed to you; integration review did not reproduce them without the private P02/P03 inputs. Do not request blanket recollection. Keep all data and full result files private.

Deston's saved-profile shell adapter is ready: request `window.load_studio_profile(store, id)` and use the existing background lifecycle. A prebuilt candidate can use `window.use_studio_profile(candidate)`. For deletion, follow the synchronous prepare/delete/clear sequence in [PROFILE_PERSISTENCE_HANDOFF.md](PROFILE_PERSISTENCE_HANDOFF.md); never leave a deleted active model or late load installed. Keep the selector embeddable and leave shell edits to Deston. The shared design is frozen in `CONTRACTS.md`; no separate loader or replacement interface is needed.

PR #17's selector is attached in Profiles. Creation/loading stays paused in Preview; cosmetic rename refreshes the label, and busy work blocks competing setup operations. Guest uses `window.use_studio_guest()` for the non-destructive return to manual control, publishing selection only on a true result. Standard gestures remain unavailable; loading does not establish readiness. The [baseline diagnostic](STARTER_FAILURE_ANALYSIS.md) is accepted. PR #19's [bounded comparison](GF_P11_BOUNDED_COMPARISON.md) reports no qualifying candidate; its private findings were not independently rerun during integration. Preserve the baseline, the three-contributor limitation and the distinction from final evaluation/distribution permission. Request repair data only for a diagnosed collection defect. Deston's six-activation check remains preliminary. PR #21's longer personal rehearsal uses the same shared camera, controller and persistent dispatcher; a qualifying full result can grant only current-session personal LIVE eligibility through the shell gate after save/reconciliation/restoration. It cannot start capture or actions automatically. The integrated Repair pose flow also reuses the shared shell and Profiles review path; do not rebuild its capture, profile create/load or dispatcher behavior. Explicit LIVE manual controls are attached independently of recognition readiness.

1. **GF-P06 - selector delivered and attached.** Keep the reviewed `ProfileStore` API and shell-owned loading. Preserve unavailable-starter messaging, independent profiles, atomic mutations and old state on failure. Deston owns integrated acceptance; see [PROGRESS.md](PROGRESS.md) for current evidence and status. Profile loading and Guest/manual access do not complete starter readiness.
2. **GF-P11 - comparison supplied in PR #19.** The bounded nested comparison reports no qualifying candidate and disagreement between the inner participants' preferred settings in every fold. Review repairs cover reproducibility and evidence consistency; see [PROGRESS.md](PROGRESS.md) for acceptance. Preserve the private run and fixed baseline. A no-qualifying result does not require shipping a starter or blanket recollection.
3. **GF-P07 accepted on 5 October.** Preserve the reviewed Enrolment implementation and the existing physical/generated evidence. Fix demonstrated regressions; no repeat recording is required simply to obtain acceptance again.
4. **GF-P12 by 18 October - validate targeted repair and retain actual Practice evidence.** Use the selected-pose workflow described above only after diagnostic need; the current 22-window Practice component and host grant are integrated and should not be rebuilt. Follow compatibility, setup and focused checks before collecting a full own-profile attempt. Preserve the saved Practice JSON, every miss/interruption, source/model/behaviour revisions and exact Session summary reconciliation. The current eligibility rule requires all 22 windows covered, all three trials correct for every pose including NEUTRAL, zero wrong or repeated activations and all ten negative windows correct. Saving, reconciliation and paused restoration must complete before explicit LIVE, Apply, Start and fresh NEUTRAL. Human outcomes remain attributed evidence; they do not replace later GF-P20 study evidence. Historical v1-v3 fifty-window files cannot grant the current v4 pass.

## Complete your lane

| Task | Deliverable | Due |
|---|---|---|
| GF-P11 | Label-aware rejection and evaluator; train-only scaler; both classifiers reproducible | 18 Oct |
| GF-P12 | Personal rehearsal and targeted recollection; version-bound readiness evidence | 18 Oct |
| GF-P17 | Frozen starter/personal configurations and properly partitioned evaluation data | 25 Oct |
| GF-P21 | Recognition/profile/evaluator defects resolved without test-set tuning | 1 Nov |
| GF-P24 | Methods, algorithm comparison, data, measured results and limitations report sections | 6 Nov |

Estimate 75 base hours, about 90 with contingency. Do not fill contingency with new AI features.

## Interfaces and file ownership

Own existing `gestureforge/collect.py`, `dataset.py`, `models.py`, `evaluate.py` and corresponding tests. Add only needed files such as `profiles.py` and `enrolment.py`; names beyond the shared contract are implementation choices. Deston owns `contracts.py`, `controller.py`, `routing.py`, `app.py` and `__main__.py`. Javier owns viewer/workspace/shortcut execution.

Preserve the classifier's `predict(features) -> (label, accepted, rejection_reason)` integration shape. Supply a stable nonempty `model_version` identifier, changed when data, preprocessing, hyperparameters or rejection settings change. Do not invent a confidence percentage from SVM decision values. Preserve 60-feature wrist-relative scale normalisation and input handedness/mirroring conventions unless a separately versioned, evaluated change is agreed.

Your collection/practice widgets receive observations from the shared capture service and report user intentions/results to Deston's shell. They do not launch resources or manipulate the viewer. Enrolment's request/attach/release handshake is implemented and documented in [ENROLMENT_INTERFACE_PROPOSAL.md](ENROLMENT_INTERFACE_PROPOSAL.md). PR #21's rehearsal widget uses the existing `RoutingSession` in REHEARSAL mode and persistent dispatcher to count actual would-be actions. Deston owns its shared-camera attachment and context restoration; report any required shell change rather than replacing the integration.

Legacy dataset import may retain NEXT/PREVIOUS/BOOKMARK as stable gesture IDs; new profiles may use G1/G2/G3 or other valid uppercase IDs. A gesture ID describes the recognised class, not the action it must execute. Validate bindings against the selected profile's vocabulary. Live model changes must reach Deston as a new model revision and trigger a new routing session.

## Data and readiness requirements

- Starter: three consenting team members, two sessions, eight trials per four labels, at most five scheduled samples per trial: 960 vectors maximum. Use participant-separated development folds and separate negatives. Ship only data for which distribution permission exists.
- Final personal comparison: at least two independent consenting participants excluded from starter fitting/tuning; separate TRAIN, VALIDATION and untouched TEST sessions. Twelve trials per label/session and at most five samples per trial: 1,440 vectors maximum across both profiles. Freeze before opening test results.
- Compare starter and personal models on the same standard-pose test trials. Evaluate different custom poses separately. Retain invalid samples and count genuine rejections as UNKNOWN misses; report per-person trial macro-F1 and UNKNOWN confusion.
- Starter check: two correct simulated activations per action pose with neutral rearming and zero incorrect activations. UNKNOWN-only cannot pass. Personal rehearsal: three trials per pose and ten five-second negative/transition intervals; require all windows covered, all three correct per pose including NEUTRAL, zero wrong or repeated activations and all ten negative windows correct.
- Personal LIVE eligibility is held only in memory and pins profile/model/hand/camera/behavior revision and exact authored workspace, stage and Quick Actions maps. Behavior, mapping, target or camera changes expire it even if changed back. Cosmetic renames, ordinary pause and selection of an existing configured stage/Quick Actions context preserve it; resume always needs explicit Start and fresh NEUTRAL. Restarting Studio, Guest and model reload clear it. Historical/imported JSON, the short check and diagnostics cannot grant it.
- Bound search to kNN k={3,5,7}, uniform/distance; SVM C={0.1,1,10}, gamma={scale,0.1}. Tune rejection on validation positives and negatives. Save numeric examples/configuration, rebuild on load; do not accept arbitrary pickle/joblib files.

## Tests and review evidence

Prove valid and corrupt profile round trips; independent profile deletion; legacy import; wrong/multiple/no hand; custom labels; non-finite/degenerate features; no split leakage; invalid detections counted; caller-visible model revision changes; deterministic reproduction; readiness failure for wrong/UNKNOWN output; and no real actions in practice. Use existing test fixtures and patterns. Synthetic results demonstrate software only.

Run the checks in `TEAM_GUIDE.md` and include their actual output in your handoff. Include a short screen recording for collection/profile workflows and explain what needs camera/participant retesting. Deston reviews the PR and runs independent integration checks.

## Integration follow-up — 4 October

PR #22's timing/countdown and partial-slot Stop handoff are integrated with the
shared-shell footer repair. Keep NEUTRAL through Begin; measurement then displays
the timed cue. New interruption records preserve the host cause. Historical
results provide deterministic next steps after event reconciliation.

After the current compatibility/setup checks, use one real G1 window to verify
Begin/measurement behavior and preserve its local timing diagnostics. Proceed
to full Practice only after reliable setup and focused recognition checks. Preserve the
reported partial-slot Stop evidence; the remaining collection/profile workflow
recording is separate. Do not rebuild the footer, add another camera worker,
change thresholds to hide failures or repeat blanket data collection.

## Starter prompt for your coding assistant

Before repeating a long Practice run after a capture-timing problem, use the
shared [capture stability diagnostic](../USER_GUIDE.md#capture-stability-diagnostic)
with the existing personal dataset. It needs no new poses or collection and
keeps only local aggregate measurements. Keep a covered recognition miss separate
from stale-frame or shutdown problems; this diagnostic cannot score poses or
unlock LIVE gestures. Do not change thresholds to hide a capture failure.

**4 October follow-up:** PR #23's single-pose diagnostic is integrated. Use it to
investigate a specific pose without repeating earlier windows; it cannot grant
full rehearsal credit. Deston's P01 partial check recorded correct NEXT and
PREVIOUS, then a pre-Begin capture validation stop. A bounded preparation-only
late-frame recovery and exact timing diagnostics are integrated; do not widen
freshness limits or change model thresholds from the old combined error. Retest
the affected preparation/pose path before requesting a full Practice run.
The subsequent P01 BOOKMARK diagnostic on `d1b68e7` completed five seconds and
recorded one matching simulated BOOKMARK event with 45 frames and no recorded
rejections. Its outcome remains inconclusive because capture coverage failed;
the old export cannot locate the boundary/gap responsible. This does not justify
changing recognition thresholds or recollecting gesture training data. Inspect
the new coverage diagnostics on a targeted retry after the layout update.
Your supplied P02 NEUTRAL miss remains separate evidence and needs its own
intended-pose/trace diagnosis. No additional data collection is justified solely
by the P01 capture interruption.

**Later 4 October check:** bounded P01 BOOKMARK and NEUTRAL diagnostics each
completed correctly with valid capture coverage. A subsequent full attempt
completed five correct, covered windows, then stopped before Begin for window
six because an otherwise valid packet was 203 ms old while armed. Recovery now
also covers READY before Begin: discard the packet, return to preparing, keep
the camera and completed windows, and require fresh NEUTRAL within the original
30-second preparation deadline. Measured-phase timing checks remain strict.
Retain the old cancelled attempt; it cannot be resumed or merged into a new pass.
Sync this correction before the next full run. No new training collection is
indicated by this pre-Begin failure.

**Measured-window follow-up, 4 October:** P01's next full attempt retained eight
covered windows (seven correct, one NEUTRAL miss), then cancelled on a 218 ms-old
frame in window nine. The v2 protocol now drops that frame and completes the
affected window as inconclusive while retaining the same session and earlier
results. It does not extend the timer or allow a full pass with incomplete
coverage. Sync main before repeating the full run; retain the old evidence.
The NEUTRAL miss remains a separate scored result, not proof of a timing cause.
Review its intended-pose evidence before changing the recogniser. Inconclusive
windows and stale-frame counts must be reported even when the session finishes.

Include this branch instruction with the task prompt: **Work only on `codex/hau-jie-profiles`. Before every commit or push, verify the current branch. When asked to publish, push only this branch and open a PR to `main` for Deston; never push or merge directly into `main` or another member's branch.**

> Work only on `codex/hau-jie-profiles`; sync reviewed main, preserving local work. Read TEAM_GUIDE.md, this brief, CONTRACTS.md and the 19 October results in GF_P21_DEVELOPMENT_DIAGNOSIS_2026_10_15.md. Deston's integration track has implemented and independently reproduced the fixed wrist/scale versus palm-local experiment; do not rebuild or retune it. Review its mixed class-level results, including P1543's NEUTRAL regression, and update your private GF-P24 methods/results contribution. Read P03_TRACE_REVIEW_2026_10_19.md: the private profile/DEVELOPMENT packet is received and its exact model reproduced. Review the fixed-setting comparison with Deston: older index negatives are rejected, while four older OK-sign samples are accepted as NEXT after repair. The recent live index failure still lacks numeric features; do not conflate those conditions or request a duplicate packet. Do not repeat the trace or infer a higher-margin fix; propose any further DEVELOPMENT experiment before execution. No model is deployment-approved. Preserve the consumed TEST results, original targets, source data and profiles; do not request repeat TEST from P67/P1543 or more data from P69. GF-P21 retains its GF-P20 dependency. Operate laptop B for Javier's agreed native/fresh-install/offline/thirty-minute/shutdown checks using the identified Studio handoff. Keep full data, exports, Word reports and logs private. Return demonstrated repairs or sanitized evidence in focused PRs from your branch; leave merge and acceptance to Deston. Keep original owners, weights and Done criteria.
