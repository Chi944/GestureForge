"""Read-only next steps from measured Practice trials, never readiness decisions."""
from __future__ import annotations

from collections import Counter
from math import isfinite

from .practice import (
    READABLE_DIAGNOSTIC_PROTOCOL_VERSIONS, READABLE_PROTOCOL_VERSIONS,
    TRIALS_PER_POSE, PracticeResult, PracticeTrial,
)


_REJECTION_GROUPS = {
    "no_hand": "hand tracking",
    "observation has no landmarks": "hand tracking",
    "multiple_hands": "multiple hands",
    "distance_rejection": "distance rejection",
    "margin_rejection": "ambiguous pose",
}
_REJECTION_STEPS = {
    "hand tracking": "Keep the enrolled hand visible in the camera preview, then retry Practice.",
    "multiple hands": "Show only the enrolled hand in the camera preview, then retry Practice.",
    "distance rejection": (
        "Review the enrolled pose and intended-pose notes before deciding on targeted recollection."
    ),
    "ambiguous pose": (
        "Compare the enrolled pose descriptions and saved trial evidence before deciding on recollection."
    ),
    "other reasons": "Review the rejection reason codes in the saved trial export before retrying.",
}


def _command_counts(trials: list[PracticeTrial], expected: str) -> str:
    commands = Counter(command for trial in trials for command in trial.actions if command != expected)
    return ", ".join(f"{command} ({count})" for command, count in sorted(commands.items()))


def _rejection_summary(trials: list[PracticeTrial], label: str) -> str | None:
    rejections: Counter[str] = Counter()
    for trial in trials:
        for reason, count in trial.rejections:
            rejections[_REJECTION_GROUPS.get(reason, "other reasons")] += count
    if not rejections:
        return None
    group, count = min(rejections.items(), key=lambda item: (-item[1], item[0]))
    frames = sum(trial.frames for trial in trials)
    other = sum(rejections.values()) - count
    remainder = f" Another {other} frame(s) had other rejection reasons; see the saved export." if other else ""
    return (
        f"{label}, scored failed windows: {group} in {count}/{frames} frames. "
        f"{_REJECTION_STEPS[group]}{remainder}"
    )


def _diagnostic_next_steps(result: PracticeResult) -> tuple[str, ...]:
    manual = "Use manual controls while reviewing this diagnostic evidence; it does not enable LIVE gestures."
    full_scope = "Full 50-window Practice was not performed; other poses and negative/transition windows were not assessed."
    if not result.trials:
        return (
            "No diagnostic window was recorded. Start Practice and complete the selected single-pose diagnostic before assessing it.",
            full_scope,
            manual,
        )
    trial = result.trials[0]
    correct = 1 if trial.outcome == "correct" and trial.coverage_ok else 0
    steps = [
        f"Single-pose diagnostic recorded {trial.expected}: {trial.outcome}; correct {correct}/1.",
        full_scope,
    ]
    if trial.outcome == "interrupted":
        steps.append(
            "Diagnostic was interrupted. Resolve the recorded stop reason and rerun this one-window diagnostic if more evidence is needed."
        )
    elif not trial.coverage_ok:
        steps.append(
            "Capture coverage was incomplete in this diagnostic window. Check the camera preview and timing before interpreting misses."
        )
        timing = trial.coverage_diagnostics
        if isinstance(timing, dict) and timing.get("schema_version") == 1:
            parts = []
            for key, label in (
                ("first_gap_seconds", "first-frame gap"),
                ("max_interframe_gap_seconds", "largest frame gap"),
                ("last_gap_seconds", "end gap"),
                ("coverage_tolerance_seconds", "allowed gap"),
            ):
                value = timing.get(key)
                if isinstance(value, (int, float)) and not isinstance(value, bool) and 0 <= value <= 60 and isfinite(value):
                    parts.append(f"{label} {value * 1000:.0f} ms")
            if parts:
                steps.append("Recorded capture timing: " + "; ".join(parts) + ".")
    elif trial.outcome in {"missed", "wrong"}:
        commands = _command_counts([trial], trial.expected)
        if commands:
            steps.append(f"Unintended simulated commands: {commands}.")
        rejection = _rejection_summary([trial], trial.expected)
        if rejection is not None:
            steps.append(rejection)
        elif trial.expected == "NEUTRAL" and trial.outcome == "missed":
            steps.append("NEUTRAL did not reach READY in this diagnostic window; review the saved trial export before changing data.")
        elif trial.outcome == "missed":
            steps.append("No simulated command was recorded in this diagnostic window; review the saved trial export before changing data.")
    if result.status == "passed":
        steps.append("Ignore any pass-like status for this diagnostic protocol; it cannot supply readiness credit.")
    steps.append(manual)
    return tuple(steps)


def practice_next_steps(result: PracticeResult) -> tuple[str, ...]:
    """Summarize producer-validated trials after the host reconciles their events.

    This does not load files, diagnose a participant, rescore an attempt, or alter
    a model. Uncovered/interrupted windows cannot support recognition advice.
    Unknown rejection strings are counted as data rather than echoed as advice.
    The current protocol bounds output to four pose summaries and four rejection
    summaries, plus capture, completion, negative-action and manual-control notes.
    """
    if result.protocol_version in READABLE_DIAGNOSTIC_PROTOCOL_VERSIONS:
        return _diagnostic_next_steps(result)
    if result.protocol_version not in READABLE_PROTOCOL_VERSIONS:
        return ("This Practice protocol is unsupported for guidance. Review its original trial export.",)

    manual = "Use manual controls while reviewing this simulation evidence; it does not enable LIVE gestures."
    if not result.trials:
        return (
            "No Practice windows were recorded. Start Practice and complete the prompted windows before assessing poses.",
            manual,
        )

    steps: list[str] = []
    interrupted = sum(trial.outcome == "interrupted" for trial in result.trials)
    uncovered = sum(not trial.coverage_ok and trial.outcome != "interrupted" for trial in result.trials)
    if uncovered:
        steps.append(
            f"Capture coverage was incomplete in {uncovered} measured window(s). Check the camera preview "
            "and capture timing, then retry Practice before interpreting misses or recollecting data."
        )
    poses = tuple(label for label, _count in result.correct_per_pose)
    unattempted = max(0, (len(poses) + 1) * TRIALS_PER_POSE - len(result.trials))
    if unattempted or interrupted:
        steps.append(
            f"Incomplete attempt: {unattempted} window(s) unattempted; {interrupted} interrupted. "
            "Resolve the recorded stop reason and start a fresh Practice attempt. Unattempted windows are not misses."
        )

    for pose in poses:
        scored = [trial for trial in result.trials if trial.expected == pose
                  and trial.coverage_ok and trial.outcome != "interrupted"]
        missed = sum(trial.outcome == "missed" for trial in scored)
        wrong = sum(trial.outcome == "wrong" for trial in scored)
        if not missed and not wrong:
            continue
        correct = sum(trial.outcome == "correct" for trial in scored)
        details = [f"{pose}: {correct}/{TRIALS_PER_POSE} correct; {missed} missed; {wrong} wrong."]
        commands = _command_counts(scored, pose)
        repeated = sum(any(count > 1 for count in Counter(trial.actions).values()) for trial in scored)
        if commands:
            details.append(f"Unintended simulated commands: {commands}.")
        if repeated:
            details.append(f"Repeated commands occurred in {repeated} window(s); inspect the transition/rearm trace.")
        if pose == "NEUTRAL":
            details.append("Show enrolled NEUTRAL until READY; review accepted/rejected NEUTRAL in the controller trace.")
        elif commands:
            details.append("Compare these enrolled poses with intended-pose notes before deciding on targeted recollection.")
        elif not repeated:
            details.append("Return to NEUTRAL until READY, then retry the prompted pose for the full five-second window.")
        steps.append(" ".join(details))

        rejection = _rejection_summary([trial for trial in scored if trial.outcome in {"missed", "wrong"}], pose)
        if rejection is not None:
            steps.append(rejection)

    negatives = [trial for trial in result.trials if trial.expected == "NEGATIVE" and trial.actions]
    if negatives:
        steps.append(
            f"Negative/transition windows recorded {sum(len(trial.actions) for trial in negatives)} simulated command(s) "
            f"across {len(negatives)} window(s): {_command_counts(negatives, 'NEGATIVE')}. "
            "Review those saved cues and the transition trace before changing data; keep rejection thresholds unchanged."
        )
    steps.append(manual)
    return tuple(steps)
