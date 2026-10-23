# Recognition review and acceptance reconciliation — 22 October 2026

**24 October update:** both the numeric diagnostic and exact P02 profile packet
are received and independently reproduced. Use [the current result and bounded
next check](P02_PROFILE_REVIEW_2026_10_24.md). Requests below for those files or the
old recording are historical. No stakeholder interviews are assigned; published
research replaces those earlier suggestions. Actual engineering tests remain.

## Received evidence

Hau Jie's private recognition supplement is received. Its SHA256 is
`5f7272c1a971127d044354e9c8ca71154f7744f160cff4404b48d4501d5c694c`.
All 17 unique safe ZIP members pass CRC and all 16 payload hashes match. The
attached reproduction script was read, not executed. Raw traces, logs and numeric
inputs remain private. The integration receipt is
`.local/recognition-review-20261022/independent-audit.json`.

Fresh replay through the current controller exactly reproduces both supplied
reconstructions and all seven event labels/timestamps in the actual simulation
log. The earlier segment includes enrolled-pose checks; its three actions must
not be added to the later negative-pose result.

| Latest P02 segment | Verified result |
|---|---|
| Recorded controller inputs / span | 1,086 / 40.578 seconds |
| Preview actions | Three PREVIOUS and one NEXT simulation |
| Accepted NEUTRAL predictions | 253 |
| Stale packets / excessive frame gaps | Zero / zero |
| Intended physical pose | Hau Jie reports index-only throughout, with direction changes |

The physical description is attributed to Hau Jie, not inferred from labels or
independently verified by video. Accepted false NEUTRAL predictions explain how
the controller could rearm. No discrepancy between its rules, replay and event
log is demonstrated. These were simulations, not external app launches or a
passed Practice session. Direction sensitivity does not establish a particular
feature-normalisation defect or a safe parameter change.

P03's six retained input-file hashes match. Independent fixed-model refitting
reproduces the original versus repaired TRAIN comparison on the same old
development validation: macro-F1 **0.850000 → 0.942308**, PREVIOUS **2/8 → 5/8**,
and negative command predictions **10/40 → 4/40**. Thresholds match too. These
are not new independent observations; the remaining older OK-sign errors do not
reproduce the newer live index condition. P02's reported numeric macro-F1
**0.936508** remains attributed because this supplement omits its numeric inputs.

## Decision and next development check

Keep the existing model, feature version, rejection thresholds, controller and
Practice gates unchanged. Label-only traces cannot identify the live distance
geometry; repeating the same trace or a full Practice trial would not close that
gap. The shared capture path gains an explicitly optional, bounded numeric
recognition diagnostic for Preview/rehearsal. It is off by default and records
decisions, distance/threshold and competing-distance ratio with exact model,
camera/hand and timing identity. It does not save frames, landmarks, feature
vectors or training examples, and cannot grant readiness or enable LIVE.

After software verification, Hau Jie can make **one short, consented DEVELOPMENT
diagnostic** using the unchanged P02 profile, with separate notes identifying
the intended pose and changes. Record an enrolled comparison pose, NEUTRAL and
the reported index-only condition; preserve misses, false commands and any
interruption. Do not fabricate annotations from predicted labels. No blanket
recollection, new participant TEST, parameter sweep or model replacement is
requested. Deston owns integration; Hau Jie reviews the numeric boundary evidence.

The diagnostic records why a prediction passed the current checks; it is not a
recognition fix. Only a demonstrated defect warrants a targeted repair and
regression test. A model-development change requires its own declared comparison,
freeze and independent evaluation. Consumed TEST remains untouched.

## Software verification

The implemented diagnostic passed independent review and software checks:
**1,076 full-suite tests passed, two platform skips**, both startup checks and
synthetic evaluation. Test-only typing errors from the initial run were repaired;
the four affected files passed 142 overlapping tests, and full Ruff/mypy passed
(106 files). Original failure and recheck receipts are preserved privately.
No new physical diagnostic or improved recognition score is claimed.

## Why accepted progress was stuck

The metric credits whole tasks at their original estimated weights. It does not
award partial points for packet arrivals, tests or report drafting. There was
also an avoidable tracking error: later evidence notes added production-starter
and native-first-use conditions to GF-P10, then held GF-P34 behind them.

The original backlog at commit `223c8c3` defines GF-P10 as six correct **simulated**
Guest actions with neutral rearming, zero wrong actions, UNKNOWN-only failure and
snapshot invalidation. GF-P34 defines twelve targets, three slots, deckless
startup/reload, dispatch validation, local rebinding and focus-loss pause.
Neither task's original software criterion is a successful production model or
two-laptop gesture trial. The wider product still promises those capabilities.

Independent review freshly passed **236 tests, one Windows symlink-permission
skip**, mapping every original clause and confirming prerequisite tasks already
Done. Generated predictions and patched model/OS adapters establish software
behaviour only. GF-P10 and GF-P34 are therefore accepted for their original
software scope. Weights, owners, dependency columns and runtime safeguards are
unchanged. Receipt:
`.local/recognition-review-20261022/original-gate-verification.json`.

**R15 production starter performance/permission remains unmet. GF-P16's real
starter and personal six-stage scenario remains unpassed.** Accepting the shell
does not approve a starter, create a Practice grant or complete the product.

| Member | Accepted task weight | Percentage |
|---|---:|---:|
| Deston | 34/75 | 45.3% |
| Hau Jie | 63/75 | 84.0% |
| Javier | 54/73 | 74.0% |
| Total | 151/223 | 67.7% |

Nineteen of 29 tasks are accepted. This is a transparent correction to task
classification, not a measured recognition improvement.

## Closest remaining acceptance steps

1. **Javier / GF-P19 (5):** finish only outstanding target/association/scheme
   error paths on the required Windows devices and genuine active-capture Camera
   handoff/recovery after readiness. Hau Jie operates laptop B. Existing passing
   manual requests/restore checks and supplied packets need no repetition.
2. **Recognition → Deston / GF-P16 (10):** diagnose the negative-pose failure,
   validate any justified repair, then run the actual standard and personal
   six-stage scenario and recovery. The unavailable qualifying starter remains
   a real product gap; manual-only evidence cannot replace this criterion.
3. **Deston / GF-P20 (10):** after scenario readiness, run the prescribed observed
   manual/starter/personal comparison, hold/negative checks and replay. Record
   actual failures and outcomes. Genuine presenter feedback can be collected now.
4. **Hau Jie / GF-P21 then GF-P24 (6 each):** resolve affected recognition checks
   and reconcile final methods/results. Low scores must be reported honestly;
   the report criterion does not require inventing successful target attainment.

Dependencies order final acceptance, not all development work. Recognition fixes,
manual native checks, report editing and stakeholder discussions can proceed in
parallel. The three-member declaration, final demonstration/rehearsal and actual
LMS package verification remain later human deliverables.
