"""Read-only next steps from measured Practice trials, never readiness decisions."""
from __future__ import annotations

from collections import Counter

from .practice import PROTOCOL_VERSION, TRIALS_PER_POSE, PracticeResult, PracticeTrial


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


def practice_next_steps(result: PracticeResult) -> tuple[str, ...]:
    """Summarize producer-validated trials after the host reconciles their events.

    This does not load files, diagnose a participant, rescore an attempt, or alter
    a model. Uncovered/interrupted windows cannot support recognition advice.
    Unknown rejection strings are counted as data rather than echoed as advice.
    The current protocol bounds output to four pose summaries and four rejection
    summaries, plus capture, completion, negative-action and manual-control notes.
    """
    if result.protocol_version != PROTOCOL_VERSION:
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

        failed = [trial for trial in scored if trial.outcome in {"missed", "wrong"}]
        rejections: Counter[str] = Counter()
        for trial in failed:
            for reason, count in trial.rejections:
                rejections[_REJECTION_GROUPS.get(reason, "other reasons")] += count
        if rejections:
            group, count = min(rejections.items(), key=lambda item: (-item[1], item[0]))
            frames = sum(trial.frames for trial in failed)
            other = sum(rejections.values()) - count
            remainder = f" Another {other} frame(s) had other rejection reasons; see the saved export." if other else ""
            steps.append(
                f"{pose}, scored failed windows: {group} in {count}/{frames} frames. "
                f"{_REJECTION_STEPS[group]}{remainder}"
            )

    negatives = [trial for trial in result.trials if trial.expected == "NEGATIVE" and trial.actions]
    if negatives:
        steps.append(
            f"Negative/transition windows recorded {sum(len(trial.actions) for trial in negatives)} simulated command(s) "
            f"across {len(negatives)} window(s): {_command_counts(negatives, 'NEGATIVE')}. "
            "Review those saved cues and the transition trace before changing data; keep rejection thresholds unchanged."
        )
    steps.append(manual)
    return tuple(steps)
