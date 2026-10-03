"""Compare Harbor workflow conditions from bounded observer-study records.

This tool validates supplied observer records and exported SessionSummary files.
It does not certify live gesture accuracy, participant consent, commercial demand,
or independent hardware behavior.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import sys
from tempfile import NamedTemporaryFile
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gestureforge.storage import decode_json  # noqa: E402

SCHEMA_VERSION = 1
MAX_INPUT_BYTES = 1024 * 1024
MAX_SUMMARY_BYTES = 16 * 1024 * 1024
CONDITIONS = ("M", "S", "P")
STATUSES = ("completed", "incomplete", "readiness_failed", "withdrawn", "fault", "timeout")
READINESS = ("not_required", "passed", "failed", "unavailable")
HARBOR_WORKSPACE_ID = "harbor-onboarding"
HARBOR_STAGES = ("intro", "budget", "reference", "resources", "discussion", "review")
OBSERVATIONS = (
    "budget_correct",
    "contact_correct",
    "discussion_bookmark",
    "recovery_observed",
    "paused_reload_no_replay",
    "finish_reviewed",
)


def load_study(path: Path) -> tuple[dict[str, Any], str]:
    data = _read_bounded(path, MAX_INPUT_BYTES, "study JSON")
    raw = decode_json(data)
    _require(isinstance(raw, dict), "study must be a JSON object")
    _require(_int(raw.get("schema_version")) == SCHEMA_VERSION, "schema_version must be 1")
    _require(set(raw) == {"schema_version", "study_id", "evidence_kind", "records"}, "invalid study fields")
    study_id = _identifier(raw["study_id"], "study_id")
    evidence_kind = raw["evidence_kind"]
    _require(evidence_kind in {"synthetic", "observed"}, "evidence_kind must be synthetic or observed")
    records_raw = raw["records"]
    _require(isinstance(records_raw, list), "records must be a list")
    _require(1 <= len(records_raw) <= 90, "records must contain 1-90 entries")
    return {
        "schema_version": SCHEMA_VERSION,
        "study_id": study_id,
        "evidence_kind": evidence_kind,
        "records": records_raw,
    }, hashlib.sha256(data).hexdigest()


def compare(input_path: Path) -> dict[str, Any]:
    study, input_hash = load_study(input_path)
    base = input_path.parent
    seen_segments = SeenSegments()
    records = [
        _record_summary(_parse_record(raw, base, seen_segments), study["evidence_kind"])
        for raw in study["records"]
    ]
    _validate_participant_orders(records)
    participants = _participants(records)
    return {
        "schema_version": SCHEMA_VERSION,
        "study": {
            "study_id": study["study_id"],
            "evidence_kind": study["evidence_kind"],
            "input_sha256": input_hash,
            "record_count": len(records),
        },
        "observer_claims": {
            "observer_claims_not_independent_verification": True,
            "tool_does_not_independently_observe_tasks": True,
            "synthetic_input": study["evidence_kind"] == "synthetic",
            "no_accuracy_or_live_gate_certification": True,
        },
        "condition_totals": _condition_totals(records),
        "participants": participants,
        "paired_deltas": _paired_deltas(participants),
        "segment_provenance": {
            "segment_count": seen_segments.count,
            "segment_sha256": sorted(seen_segments.hashes),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        _require(not _same_path_or_file(args.input, args.output), "output must not overwrite input")
        report = compare(args.input)
        _write_json_exclusive(args.output, report)
    except (OSError, ValueError) as exc:
        raise SystemExit(f"compare_workflows: {exc}") from exc
    return 0


class SeenSegments:
    def __init__(self) -> None:
        self.paths: set[str] = set()
        self.hashes: set[str] = set()
        self.revisions: set[str] = set()
        self.event_keys: set[tuple[str, str]] = set()
        self.count = 0


def _parse_record(raw: Any, base: Path, seen: SeenSegments) -> dict[str, Any]:
    _require(isinstance(raw, dict), "record must be an object")
    required = {
        "participant_id", "condition", "order", "planned_order", "source_commit", "workspace_sha256",
        "model_sha256", "config_sha256", "data_sha256", "declared_model_version",
        "environment_id", "setup_seconds", "readiness_seconds", "task_seconds", "readiness", "status",
        "manual_fallback",
        "completed_stages", "observations", "wrong_actions", "retries", "help_requests",
        "comfort", "usefulness", "summary_segments",
    }
    _require(set(raw) == required, "invalid record fields")
    condition = raw["condition"]
    _require(condition in CONDITIONS, "condition must be M, S or P")
    model_hash = _nullable_hash(raw["model_sha256"], "model_sha256")
    config_hash = _nullable_hash(raw["config_sha256"], "config_sha256")
    data_hash = _nullable_hash(raw["data_sha256"], "data_sha256")
    readiness = _enum(raw["readiness"], READINESS, "readiness")
    status = _enum(raw["status"], STATUSES, "status")
    declared_model = _nullable_identifier(raw["declared_model_version"], "declared_model_version")
    full_model = (
        model_hash is not None and config_hash is not None and data_hash is not None
        and declared_model is not None
    )
    null_model = (
        model_hash is None and config_hash is None and data_hash is None and declared_model is None
    )
    if condition == "M":
        _require(null_model, "M model fields must be null")
    else:
        _require(full_model or null_model, "gesture model fields must be complete or all null")
        if null_model:
            _require(
                readiness in {"failed", "unavailable"} or status == "readiness_failed",
                "null gesture model is only valid when recognition was unavailable or failed",
            )
    record = {
        "participant_id": _identifier(raw["participant_id"], "participant_id"),
        "condition": condition,
        "order": _bounded_int(raw["order"], 1, 3, "order"),
        "planned_order": _planned_order(raw["planned_order"]),
        "source_commit": _hex(raw["source_commit"], 40, "source_commit"),
        "workspace_sha256": _hex(raw["workspace_sha256"], 64, "workspace_sha256"),
        "model_sha256": model_hash,
        "config_sha256": config_hash,
        "data_sha256": data_hash,
        "environment_id": _identifier(raw["environment_id"], "environment_id"),
        "declared_model_version": declared_model,
        "setup_seconds": _bounded_number(raw["setup_seconds"], 0.0, 3600.0, "setup_seconds"),
        "readiness_seconds": _bounded_number(raw["readiness_seconds"], 0.0, 3600.0, "readiness_seconds"),
        "task_seconds": _nullable_bounded_number(raw["task_seconds"], 0.0, 3600.0, "task_seconds"),
        "readiness": readiness,
        "status": status,
        "manual_fallback": _bool(raw["manual_fallback"], "manual_fallback"),
        "completed_stages": _stage_list(raw["completed_stages"], "completed_stages"),
        "observations": _observations(raw["observations"]),
        "wrong_actions": _bounded_int(raw["wrong_actions"], 0, 1000, "wrong_actions"),
        "retries": _bounded_int(raw["retries"], 0, 1000, "retries"),
        "help_requests": _bounded_int(raw["help_requests"], 0, 1000, "help_requests"),
        "comfort": _nullable_bounded_int(raw["comfort"], 1, 5, "comfort"),
        "usefulness": _nullable_bounded_int(raw["usefulness"], 1, 5, "usefulness"),
    }
    segments = _segments(raw["summary_segments"], base, record, seen)
    record["summary_segments"] = segments
    return record


def _segments(raw: Any, base: Path, record: dict[str, Any], seen: SeenSegments) -> list[dict[str, Any]]:
    _require(isinstance(raw, list), "summary_segments must be a list")
    raw_segments: list[Any] = raw
    if not raw_segments:
        _require(_zero_segment_allowed(record), "summary_segments must be non-empty after task evidence exists")
        return []
    _require(len(raw_segments) <= 12, "summary_segments limit exceeded")
    result: list[dict[str, Any]] = []
    for item in raw_segments:
        _require(isinstance(item, str), "summary segment must be a relative path")
        relative = Path(item)
        _require(not relative.is_absolute() and ".." not in relative.parts, "summary segment path must stay local")
        path = (base / relative).resolve()
        _require(base.resolve() in (path, *path.parents), "summary segment path must stay local")
        key = str(path)
        _require(key not in seen.paths, "summary segment path reused")
        data = _read_bounded(path, MAX_SUMMARY_BYTES, "summary segment JSON")
        sha = hashlib.sha256(data).hexdigest()
        _require(sha not in seen.hashes, "summary segment hash reused")
        summary = decode_json(data)
        info = _validate_summary(summary, record)
        revision = info["revision_id"]
        _require(revision not in seen.revisions, "summary revision_id reused")
        for event_key in info["event_keys"]:
            _require(event_key not in seen.event_keys, "event identity appears in multiple segments")
        seen.paths.add(key)
        seen.hashes.add(sha)
        seen.revisions.add(revision)
        seen.event_keys.update(info["event_keys"])
        seen.count += 1
        result.append({
            "sha256": sha,
            "revision_id": revision,
            "outcome_count": info["outcome_count"],
            "acknowledged_stages": info["acknowledged_stages"],
            "status_counts": info["status_counts"],
            "gesture_actions": info["gesture_actions"],
            "manual_actions": info["manual_actions"],
        })
    return result


def _validate_summary(summary: Any, record: dict[str, Any]) -> dict[str, Any]:
    _require(isinstance(summary, dict), "summary segment must be an object")
    _require(set(summary) == {"schema_version", "scope", "counts", "outcomes", "trials", "completed_stages"},
             "invalid summary fields")
    _require(_int(summary["schema_version"]) == SCHEMA_VERSION, "summary schema_version must be 1")
    scope = summary["scope"]
    counts = summary["counts"]
    outcomes = summary["outcomes"]
    completed = summary["completed_stages"]
    _require(isinstance(scope, dict), "summary scope must be an object")
    _require(isinstance(counts, dict), "summary counts must be an object")
    _require(isinstance(outcomes, list), "summary outcomes must be a list")
    _require(isinstance(summary["trials"], list), "summary trials must be a list")
    _require(len(outcomes) <= 10000 and len(summary["trials"]) <= 10000, "summary lists exceed limit")
    revision_id = _identifier(scope.get("revision_id"), "scope.revision_id")
    _require(revision_id not in {record["source_commit"], record["workspace_sha256"]},
             "scope revision_id must not be a workspace or source hash")
    _require(scope.get("workspace_id") == HARBOR_WORKSPACE_ID, "summary workspace_id is not Harbor")
    for key in ("participant_id", "condition", "environment_id", "source_commit", "workspace_sha256"):
        if key in scope:
            _require(scope[key] == record[key], f"summary scope {key} does not match record")
    status_counts = {name: 0 for name in (
        "simulated", "launch_requested", "failed", "duplicate", "rejected", "applied", "unchanged"
    )}
    event_keys: set[tuple[str, str]] = set()
    effectful_keys: set[tuple[str, str]] = set()
    gesture_actions = 0
    manual_actions = 0
    for outcome in outcomes:
        _require(isinstance(outcome, dict), "summary outcome must be an object")
        event_id = _identifier(outcome.get("event_id"), "outcome.event_id")
        session_id = _identifier(outcome.get("session_id"), "outcome.session_id")
        source = _enum(outcome.get("source"), ("manual", "gesture"), "outcome.source")
        status = _enum(outcome.get("status"), tuple(status_counts), "outcome.status")
        if source == "gesture" and record["condition"] != "M" and record["declared_model_version"] is None:
            raise ValueError("gesture outcome requires declared_model_version")
        if source == "gesture" and record["condition"] != "M" and record["declared_model_version"] is not None:
            _require(outcome.get("model_version") == record["declared_model_version"],
                     "gesture outcome model_version mismatch")
        if status in {"launch_requested", "applied"}:
            _require((session_id, event_id) not in effectful_keys,
                     "event identity has multiple effectful outcomes")
            effectful_keys.add((session_id, event_id))
            gesture_actions += int(source == "gesture")
            manual_actions += int(source == "manual")
        status_counts[status] += 1
        event_keys.add((session_id, event_id))
    for name, count in status_counts.items():
        _require(_int(counts.get(name)) == count, "summary status count mismatch")
    if "acknowledged_completion" in counts:
        _require(_int(counts["acknowledged_completion"]) == len(completed),
                 "summary acknowledged completion mismatch")
    trial_counts = {"correct": 0, "wrong": 0, "missed": 0, "tracking_lost": 0}
    for trial in summary["trials"]:
        _require(isinstance(trial, dict), "summary trial must be an object")
        expected = trial.get("expected")
        observed = trial.get("observed")
        tracking_lost = _bool(trial.get("tracking_lost", False), "trial.tracking_lost")
        _require(isinstance(expected, str), "trial expected must be a string")
        _require(observed is None or isinstance(observed, str), "trial observed must be null or string")
        trial_counts["correct"] += int(observed == expected)
        trial_counts["wrong"] += int(observed not in {None, "UNKNOWN"} and observed != expected)
        trial_counts["missed"] += int(observed in {None, "UNKNOWN"})
        trial_counts["tracking_lost"] += int(tracking_lost)
    for name, count in trial_counts.items():
        if name in counts:
            _require(_int(counts[name]) == count, f"summary {name} count mismatch")
    for name in ("retries",):
        if name in counts:
            _require(_int(counts[name]) >= 0, f"summary {name} count must be non-negative")
    acknowledged = _stage_list(completed, "summary.completed_stages")
    return {
        "revision_id": revision_id,
        "outcome_count": len(outcomes),
        "acknowledged_stages": acknowledged,
        "status_counts": status_counts,
        "gesture_actions": gesture_actions,
        "manual_actions": manual_actions,
        "event_keys": event_keys,
    }


def _record_summary(record: dict[str, Any], evidence_kind: str) -> dict[str, Any]:
    acknowledged = sorted({
        stage for segment in record["summary_segments"] for stage in segment["acknowledged_stages"]
    })
    all_stages = set(HARBOR_STAGES)
    observed_complete = all(record["observations"].values())
    stage_complete = all_stages <= set(record["completed_stages"]) and all_stages <= set(acknowledged)
    task_time_present = record["task_seconds"] is not None
    task_limit_exceeded = record["task_seconds"] is not None and record["task_seconds"] > 900.0
    actual_completion = (
        record["status"] == "completed" and observed_complete and stage_complete and task_time_present
    )
    readiness_ok = record["readiness"] == ("not_required" if record["condition"] == "M" else "passed")
    simulated = sum(segment["status_counts"]["simulated"] for segment in record["summary_segments"])
    gesture_actions = sum(segment["gesture_actions"] for segment in record["summary_segments"])
    manual_actions = sum(segment["manual_actions"] for segment in record["summary_segments"])
    has_condition_execution = (
        (record["condition"] == "M" and manual_actions > 0 and gesture_actions == 0)
        or (record["condition"] != "M" and gesture_actions > 0)
    )
    condition_success = (
        actual_completion and not record["manual_fallback"] and readiness_ok and simulated == 0
        and has_condition_execution and not task_limit_exceeded
    )
    execution_mismatch = actual_completion and simulated > 0
    return {
        "participant_id": record["participant_id"],
        "condition": record["condition"],
        "order": record["order"],
        "planned_order": record["planned_order"],
        "actual_completion": actual_completion,
        "condition_success": condition_success,
        "manual_fallback": record["manual_fallback"],
        "readiness": record["readiness"],
        "status": record["status"],
        "execution_mismatch": execution_mismatch,
        "task_limit_exceeded": task_limit_exceeded,
        "completed_stage_count": len(set(record["completed_stages"])),
        "acknowledged_stage_count": len(set(acknowledged)),
        "missing_stages": [stage for stage in HARBOR_STAGES if stage not in set(record["completed_stages"])],
        "source_commit": record["source_commit"],
        "workspace_sha256": record["workspace_sha256"],
        "environment_id": record["environment_id"],
        "model_sha256": record["model_sha256"],
        "config_sha256": record["config_sha256"],
        "data_sha256": record["data_sha256"],
        "setup_seconds": record["setup_seconds"],
        "readiness_seconds": record["readiness_seconds"],
        "task_seconds": record["task_seconds"],
        "wrong_actions": record["wrong_actions"],
        "retries": record["retries"],
        "help_requests": record["help_requests"],
        "comfort": record["comfort"],
        "usefulness": record["usefulness"],
        "summary_segment_count": len(record["summary_segments"]),
        "summary_outcome_count": sum(segment["outcome_count"] for segment in record["summary_segments"]),
        "summary_segments": [_segment_output(segment) for segment in record["summary_segments"]],
        "verified_gesture_action_count": gesture_actions,
        "verified_manual_action_count": manual_actions,
        "evidence_kind": evidence_kind,
    }


def _validate_participant_orders(records: list[dict[str, Any]]) -> None:
    by_participant: dict[str, list[dict[str, Any]]] = {}
    for record in records:
        by_participant.setdefault(record["participant_id"], []).append(record)
    for participant_records in by_participant.values():
        planned_orders = {tuple(record["planned_order"]) for record in participant_records}
        _require(len(planned_orders) == 1, "participant planned_order must be consistent")
        orders = [record["order"] for record in participant_records]
        _require(len(orders) == len(set(orders)), "participant actual order values must be unique")
        conditions = [record["condition"] for record in participant_records]
        _require(len(conditions) == len(set(conditions)), "participant condition repeated")


def _participants(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result = []
    for participant_id in sorted({record["participant_id"] for record in records}):
        rows = sorted((record for record in records if record["participant_id"] == participant_id),
                      key=lambda record: record["order"])
        present = {record["condition"] for record in rows}
        result.append({
            "participant_id": participant_id,
            "planned_order": rows[0]["planned_order"],
            "actual_order": [record["condition"] for record in rows],
            "missing_conditions": [condition for condition in CONDITIONS if condition not in present],
            "records": rows,
        })
    return result


def _condition_totals(records: list[dict[str, Any]]) -> dict[str, Any]:
    totals: dict[str, Any] = {}
    for condition in CONDITIONS:
        rows = [record for record in records if record["condition"] == condition]
        statuses = {status: sum(record["status"] == status for record in rows) for status in STATUSES}
        totals[condition] = {
            "records": len(rows),
            "actual_completion": sum(record["actual_completion"] for record in rows),
            "condition_success": sum(record["condition_success"] for record in rows),
            "manual_fallback": sum(record["manual_fallback"] for record in rows),
            "readiness_failed": sum(record["readiness"] == "failed" for record in rows),
            "statuses": statuses,
        }
    return totals


def _paired_deltas(participants: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for participant in participants:
        by_condition = {record["condition"]: record for record in participant["records"]}
        for left, right in (("M", "S"), ("M", "P"), ("S", "P")):
            rows.append(_paired_delta(participant["participant_id"], left, right, by_condition))
    return rows


def _paired_delta(participant_id: str, left: str, right: str,
                  by_condition: dict[str, dict[str, Any]]) -> dict[str, Any]:
    base = {"participant_id": participant_id, "left": left, "right": right}
    if left not in by_condition or right not in by_condition:
        return {**base, "task_seconds_delta": None, "reason": "missing_condition"}
    left_row = by_condition[left]
    right_row = by_condition[right]
    if not left_row["condition_success"] or not right_row["condition_success"]:
        return {**base, "task_seconds_delta": None, "reason": "condition_not_successful"}
    if any(left_row[key] != right_row[key] for key in ("environment_id", "workspace_sha256", "source_commit")):
        return {**base, "task_seconds_delta": None, "reason": "incompatible_source"}
    left_seconds = left_row["task_seconds"]
    right_seconds = right_row["task_seconds"]
    _require(left_seconds is not None and right_seconds is not None, "successful paired rows require task time")
    return {**base, "task_seconds_delta": round(right_seconds - left_seconds, 6), "reason": None}


def _write_json_exclusive(path: Path, data: dict[str, Any]) -> None:
    _require(not path.exists(), "output already exists; choose a new report filename")
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(data, ensure_ascii=False, allow_nan=False, indent=2, sort_keys=True) + "\n"
    with NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        temp = Path(handle.name)
        handle.write(text)
    try:
        os.link(temp, path)
    finally:
        temp.unlink(missing_ok=True)


def _read_bounded(path: Path, limit: int, label: str) -> bytes:
    with path.open("rb") as stream:
        data = stream.read(limit + 1)
    _require(len(data) <= limit, f"{label} exceeds size limit")
    return data


def _same_path_or_file(left: Path, right: Path) -> bool:
    if left.resolve() == right.resolve():
        return True
    try:
        return left.samefile(right)
    except FileNotFoundError:
        return False


def _identifier(value: Any, name: str) -> str:
    _require(isinstance(value, str), f"{name} must be an ID")
    _require(1 <= len(value) <= 64, f"{name} must be 1-64 characters")
    _require(all(char.isascii() and (char.isalnum() or char in "_.:-") for char in value),
             f"{name} must be an opaque ASCII ID")
    return value


def _nullable_identifier(value: Any, name: str) -> str | None:
    if value is None:
        return None
    return _identifier(value, name)


def _hex(value: Any, length: int, name: str) -> str:
    _require(isinstance(value, str) and len(value) == length, f"{name} must be {length} hex chars")
    _require(all(char in "0123456789abcdefABCDEF" for char in value), f"{name} must be hex")
    return value.lower()


def _nullable_hash(value: Any, name: str) -> str | None:
    if value is None:
        return None
    return _hex(value, 64, name)


def _enum(value: Any, allowed: tuple[str, ...], name: str) -> str:
    _require(isinstance(value, str) and value in allowed, f"{name} has unsupported value")
    return value


def _bool(value: Any, name: str) -> bool:
    _require(type(value) is bool, f"{name} must be boolean")
    return value


def _int(value: Any) -> int:
    _require(type(value) is int, "integer required")
    return value


def _bounded_int(value: Any, minimum: int, maximum: int, name: str) -> int:
    _require(type(value) is int and minimum <= value <= maximum, f"{name} must be an integer in range")
    return value


def _nullable_bounded_int(value: Any, minimum: int, maximum: int, name: str) -> int | None:
    if value is None:
        return None
    return _bounded_int(value, minimum, maximum, name)


def _finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _bounded_number(value: Any, minimum: float, maximum: float, name: str) -> float:
    _require(_finite_number(value), f"{name} must be finite")
    result = float(value)
    _require(minimum <= result <= maximum, f"{name} out of range")
    return result


def _nullable_bounded_number(value: Any, minimum: float, maximum: float, name: str) -> float | None:
    if value is None:
        return None
    return _bounded_number(value, minimum, maximum, name)


def _planned_order(value: Any) -> list[str]:
    _require(isinstance(value, list) and len(value) == 3, "planned_order must contain M, S and P")
    result = [_enum(item, CONDITIONS, "planned_order item") for item in value]
    _require(set(result) == set(CONDITIONS), "planned_order must be a complete M/S/P permutation")
    return result


def _stage_list(value: Any, name: str) -> list[str]:
    _require(isinstance(value, list), f"{name} must be a list")
    result = [_enum(item, HARBOR_STAGES, f"{name} item") for item in value]
    _require(len(result) == len(set(result)), f"{name} contains duplicates")
    return result


def _observations(value: Any) -> dict[str, bool]:
    _require(isinstance(value, dict), "invalid observations")
    _require(set(value) == set(OBSERVATIONS), "invalid observations")
    return {key: _bool(value[key], f"observations.{key}") for key in OBSERVATIONS}


def _zero_segment_allowed(record: dict[str, Any]) -> bool:
    no_task_evidence = (
        record["task_seconds"] is None
        and not record["completed_stages"]
        and not any(record["observations"].values())
        and record["wrong_actions"] == 0
    )
    return no_task_evidence and (
        record["status"] in {"withdrawn", "readiness_failed"}
        or record["readiness"] == "unavailable"
    )


def _segment_output(segment: dict[str, Any]) -> dict[str, Any]:
    return {
        "sha256": segment["sha256"],
        "revision_id": segment["revision_id"],
        "outcome_count": segment["outcome_count"],
        "acknowledged_stage_count": len(segment["acknowledged_stages"]),
        "status_counts": segment["status_counts"],
        "gesture_actions": segment["gesture_actions"],
        "manual_actions": segment["manual_actions"],
    }


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


if __name__ == "__main__":
    raise SystemExit(main())
