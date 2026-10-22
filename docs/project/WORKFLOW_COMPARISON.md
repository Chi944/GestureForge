# Harbor workflow comparison

This guide prepares GF-P20's manual (M), standard starter (S) and personal (P)
comparison. Follow the participant procedure in [DEMO_SCENARIO.md](DEMO_SCENARIO.md).
The tool combines an observer's record with exported Studio summaries. It does
not observe the participant, certify recognition or enable LIVE gestures.

## Establish the user problem before measuring the solution

Obtain brief, consented accounts from people who have actually delivered training
or product demonstrations. Hau Jie and Javier can each arrange one conversation;
Deston reviews the resulting needs against R07/R13/R16/R20/R21. This is a small
elicitation exercise, not a representative market survey. Do not count the team's
fictional Harbor scenario or camera-data participants as customer interviews.

Ask for a recent example before showing Studio: what resources did the presenter
switch between, when did they return to the keyboard, what went wrong after an
interruption, and what do they already use (keyboard, clicker or other controls)?
Then show the manual and gesture workflow and ask where either would help or make
the task harder, what would stop adoption, and which recovery behaviour matters.
Accept an answer that no new input method is needed.

Keep a private dated note containing consent, pseudonym, relevant experience,
existing workflow, the participant's actual account, priority and proposed
requirement link. Separate direct quotations, paraphrases and the team's
interpretation. Record any resulting requirement decision without fabricating
approval. These notes are a separate qualitative sidecar; do not add unsupported
fields to the study JSON schema below.

The existing M condition is Studio's buttons/keyboard baseline. It is not a
measured clicker comparison. A slide-only clicker is a credible simpler
alternative; this study tests the wider resource/recovery workflow. Compare task
time, errors, help and usefulness only on the recorded conditions; include setup
and readiness cost separately. Report no benefit if the evidence shows none.

## Collect the record

1. Before the study, freeze the source commit, workspace, recognition data and
   configuration. Keep their checksums and the exact model version. Use opaque
   participant and environment IDs; keep consent and identifying notes privately.
2. Record the planned M/S/P order before starting, and the actual position of each
   condition. Record every attempted condition, including failures, withdrawal,
   unavailable recognition and manual fallback. An absent condition stays missing.
3. Time setup, readiness and the task separately. Task timing starts at the first
   instruction and ends after Finish and summary review. Stop after 15 minutes.
   Use observed durations; do not infer them from action timestamps.
4. Retain each disjoint **Export session results** JSON, including both sides of
   a paused reload. Do not include two cumulative snapshots of the same summary.
   Navigation files from **Save session** are not measurement exports.
5. Check the actual calculation, reference answer, discussion bookmark, recovery,
   paused reload and final review. A successful launch request alone does not
   prove any of these. Record errors, retries, help, and optional comfort/usefulness
   ratings. Keep the observer's notes and limitations beside the data.

Before task timing begins, export setup, Practice and familiarisation results,
then use **Restart deck** to archive them and start an empty task summary at
Harbor's first stage. Exporting by itself does not clear the summary. Confirm
the appropriate current-session readiness remains valid; restarting cannot grant
readiness. Preserve preparation exports separately, outside the task record's
`summary_segments`.

During the measured save/reload, observe paused Preview and no automatic replay,
then explicitly select **Live** and **Apply and pause** before the next real
action. Gesture use still needs valid current-session readiness, Start and fresh
NEUTRAL. The development walkthrough's deliberate simulated-action probe is not
part of this measured task. Retain both task segments unchanged. Any simulated
outcome after the task begins remains an execution mismatch and prevents
condition success; do not filter it out or restart the summary to hide it.

Put input records and summary exports under ignored `experiments/local/`, for
example `experiments/local/workflow-study/`. Keep the inputs unchanged after
review. Never commit participant records or private target paths.

## Run the comparison

From the repository root on Windows:

```powershell
.\.venv\Scripts\python.exe scripts/compare_workflows.py --input experiments/local/workflow-study/study.json --output experiments/local/workflow-study/comparison-v1.json
```

On macOS, the command uses `.venv/bin/python`. The comparison itself does not
launch apps or use a webcam. Native Mac application control is outside the current
Windows launch implementation.

Choose a new output name each time. The tool refuses existing output, input
aliases, reused summary segments and overlapping event identities. It publishes
the report with an exclusive local hard link; use a filesystem supporting that
operation, such as the project's Windows NTFS directory. Failure leaves no
partial published report. Keep the input and output checksums with the source
commit used to run the tool.

## Input contract, version 1

The top-level object has exactly `schema_version: 1`, an opaque `study_id`,
`evidence_kind` (`observed` or `synthetic`) and `records`. Use `synthetic` for
generated examples and software checks. Real records remain observer assertions,
even when their attached files pass structural checks.

Each record uses the fields below. The script and its focused tests are the
executable schema; unsupported or misspelled fields are rejected.

| Fields | Meaning |
|---|---|
| `participant_id`, `environment_id` | Opaque ASCII IDs, not names or device paths |
| `condition`, `order`, `planned_order` | M/S/P, actual position 1–3, and the planned permutation of all three conditions |
| `source_commit`, `workspace_sha256` | 40-character Git commit and 64-character SHA-256 of the frozen workspace bytes |
| `declared_model_version`, `model_sha256`, `config_sha256`, `data_sha256` | Frozen recogniser identity and 64-character hashes. Manual control uses null; gesture records use a complete set or all null if recognition was unavailable/failed. Withdrawal retains known provenance |
| `setup_seconds`, `readiness_seconds`, `task_seconds` | Separate finite durations, each bounded to 0–3,600 seconds; task time may be null before it starts. Task times over the protocol's 900-second limit remain visible with `task_limit_exceeded` and cannot qualify as condition success |
| `readiness` | `not_required`, `passed`, `failed` or `unavailable` |
| `status` | `completed`, `incomplete`, `readiness_failed`, `withdrawn`, `fault` or `timeout` |
| `manual_fallback` | Whether manual controls substituted for the gesture condition |
| `completed_stages` | Observed completed stage IDs from `intro`, `budget`, `reference`, `resources`, `discussion`, `review` (the UI's Welcome and Finish stages use `intro` and `review`) |
| `observations` | Six booleans: `budget_correct`, `contact_correct`, `discussion_bookmark`, `recovery_observed`, `paused_reload_no_replay`, `finish_reviewed` |
| `wrong_actions`, `retries`, `help_requests` | Observer-recorded non-negative counts |
| `comfort`, `usefulness` | Participant rating 1–5, or null when not provided |
| `summary_segments` | Relative paths to disjoint exported summaries under the input directory; no navigation saves. May be empty for withdrawal, readiness failure, a fault or unavailable recognition before task evidence exists. Faults with recorded task time, completed stages, observations or wrong actions still require an export |

Use hashes of the actual frozen files, not placeholder values. These supplied
source/model/config/data/workspace identifiers are provenance claims: the tool
does not possess or independently re-hash those source artifacts. It does hash
the exact input and summary bytes it reads. A summary's generated `revision_id`
identifies a measurement segment; it is not a workspace checksum.

The following is a **synthetic format example**, not a participant record. It
shows an unavailable starter before any task starts; replace every example value
with actual observations and provenance before using `evidence_kind: observed`.
The zero hashes are placeholders and must not appear in actual evidence.

```json
{
  "schema_version": 1,
  "study_id": "format-example-only",
  "evidence_kind": "synthetic",
  "records": [{
    "participant_id": "EXAMPLE", "condition": "S", "order": 2,
    "planned_order": ["M", "S", "P"],
    "source_commit": "0000000000000000000000000000000000000000",
    "workspace_sha256": "0000000000000000000000000000000000000000000000000000000000000000",
    "declared_model_version": null, "model_sha256": null,
    "config_sha256": null, "data_sha256": null,
    "environment_id": "EXAMPLE-WINDOWS",
    "setup_seconds": 0, "readiness_seconds": 0, "task_seconds": null,
    "readiness": "unavailable", "status": "readiness_failed",
    "manual_fallback": false, "completed_stages": [],
    "observations": {
      "budget_correct": false, "contact_correct": false,
      "discussion_bookmark": false, "recovery_observed": false,
      "paused_reload_no_replay": false, "finish_reviewed": false
    },
    "wrong_actions": 0, "retries": 0, "help_requests": 0,
    "comfort": null, "usefulness": null, "summary_segments": []
  }]
}
```

## Read the result

The report retains individual conditions, actual order, missing conditions,
fallbacks, failures and observed completion separately. Completion needs all
required observer checks, all six observed and acknowledged stages and a task
time; an application opening cannot supply those facts. Gesture-condition
success also requires passed readiness, no fallback and actual gesture outcomes,
without simulated outcomes being presented as real execution.

Paired task-time differences are reported only for successful conditions from
the same participant, environment, source commit and workspace checksum. The
value is **right condition minus left condition**; a negative value means the
right condition took less time. Missing or incompatible comparisons stay null
with a reason. There is no imputation, best-run selection, significance test or
claim of commercial demand.

Repeated dispatcher records marked `duplicate` are retained within their original
segment. Multiple effectful records (`applied` or `launch_requested`) for the same
session/event identity are rejected. The same identity appearing across segments is rejected
to prevent cumulative exports being counted twice. The output omits raw paths,
target values, freeform reasons and document contents; retain originals privately
for a reviewer to inspect.

Passing this tool validates record structure and consistency, not participant
honesty, consent, actual desktop behavior or recognition accuracy. Software
fixtures cannot complete GF-P20. Deston reviews real observations alongside these
results; Hau Jie owns frozen recognition inputs and Javier owns native Windows
action/recovery evidence.
