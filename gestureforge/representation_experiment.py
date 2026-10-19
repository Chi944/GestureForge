"""Fixed development-only wrist/scale versus palm-local comparison; no model export."""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import replace
import json
from pathlib import Path
from time import perf_counter
from typing import Any

import numpy as np

from .dataset import DatasetBundle, dataset_hashes, load_dataset
from .evaluate import _validate_assignment_evaluation_bundle, evaluate_algorithm
from .vocabulary import LEGACY_VOCABULARY

EXPERIMENT = "palm-local-experiment-v1"
SETTINGS = {"P67": ("knn", 2.5, 1.75), "P1543": ("svm", 2.5, 1.25)}


def palm_local(feature: np.ndarray) -> np.ndarray:
    """Project a v1 wrist-relative row onto the predeclared right-palm frame."""
    row = np.asarray(feature, dtype=np.float64)
    if row.shape != (60,) or not np.isfinite(row).all():
        raise ValueError("expected a finite 60-value feature row")
    points = np.vstack((np.zeros((1, 3)), row.reshape(20, 3)))
    y = points[9].copy()
    length = np.linalg.norm(y)
    if not np.isfinite(length) or length <= 1e-6:
        raise ValueError("degenerate_palm")
    y /= length
    x = points[5] - points[17]
    x -= np.dot(x, y) * y
    length = np.linalg.norm(x)
    if not np.isfinite(length) or length <= 1e-6:
        raise ValueError("degenerate_palm")
    x /= length
    projected = (points[1:] @ np.column_stack((x, y, np.cross(x, y)))).ravel()
    if not np.isfinite(projected).all() or np.any(np.abs(projected) > np.finfo(np.float32).max):
        raise ValueError("non-finite projected feature")
    return projected.astype(np.float32)


def _transformed(bundle: DatasetBundle) -> DatasetBundle:
    features: list[np.ndarray] = []
    records = []
    for record in bundle.records:
        if not record.valid or record.feature_index is None:
            records.append(record)
            continue
        try:
            row = palm_local(bundle.features[record.feature_index])
        except ValueError as exc:
            if str(exc) != "degenerate_palm":
                raise
            records.append(replace(record, valid=False, feature_index=None,
                                   validity_reason="degenerate_palm"))
            continue
        records.append(replace(record, feature_index=len(features)))
        features.append(row)
    # This in-memory bundle is never passed to dataset/profile persistence.
    return replace(bundle, manifest_path=None, records=tuple(records),
                   features=np.asarray(features, dtype=np.float32).reshape(-1, 60))


def _condition(bundle: DatasetBundle, representation: str, settings: tuple[str, float, float],
               transform_seconds: float) -> dict[str, Any]:
    splits: dict[str, Any] = {}
    for split in ("train", "validation", "validation_negative"):
        records = tuple(r for r in bundle.records if r.split == split)
        splits[split] = {
            "scheduled_slots": len(records), "trials": len({r.trial_id for r in records}),
            "invalid_slots": sum(not r.valid or r.feature_index is None for r in records),
        }
    sparse = [label for label in bundle.vocabulary.labels if len({
        r.trial_id for r in bundle.valid_records("train") if r.intended_label == label
    }) < 2]
    result: dict[str, Any] = {"representation": representation, "splits": splits,
                              "transform_seconds": transform_seconds}
    if sparse:
        return {**result, "status": "unavailable", "reason": "fewer than two valid TRAIN trials",
                "classes": sparse}
    evaluated = evaluate_algorithm(bundle, *settings)
    for split, key in (("validation", "sample_predictions"),
                       ("validation_negative", "validation_negative_predictions")):
        records = tuple(r for r in bundle.records if r.split == split)
        predictions = evaluated[key]
        details = {}
        for label in sorted({r.intended_label for r in records}):
            chosen = [(r, p) for r, p in zip(records, predictions, strict=True)
                      if r.intended_label == label]
            details[label] = {
                "scheduled_slots": len(chosen),
                "invalid_slots": sum(not r.valid or r.feature_index is None for r, _ in chosen),
                "rejected_valid_slots": sum(r.valid and not p["accepted"] for r, p in chosen),
                "wrong_accepted_slots": sum(p["accepted"] and p["scored_label"] != label
                                            for _, p in chosen),
                "scored_labels": dict(Counter(p["scored_label"] for _, p in chosen)),
                "reasons": dict(Counter(p["reason"] or "accepted" for _, p in chosen)),
            }
        splits[split]["by_intended_label"] = details
    return {**result, "status": "available", "metrics": evaluated["metrics"],
            "timing": evaluated["timing"],
            "estimator_params": evaluated["model"]["estimator_params"],
            "rejection_reference": evaluated["model"]["rejection_reference"],
            "library_versions": evaluated["model"]["library_versions"]}


def compare_representations(bundle: DatasetBundle) -> dict[str, Any]:
    """Preserve every development slot; neither select settings nor use TEST."""
    if any(r.split not in {"train", "validation", "validation_negative"} for r in bundle.records):
        raise ValueError("representation experiment refuses TEST or unsupported splits")
    participants = {r.participant_id for r in bundle.records}
    if len(participants) != 1 or next(iter(participants)) not in SETTINGS:
        raise ValueError("requires one predeclared participant: P67 or P1543")
    if bundle.vocabulary != LEGACY_VOCABULARY or any(
        r.intended_label != "UNKNOWN" if r.split == "validation_negative"
        else r.intended_label not in LEGACY_VOCABULARY.labels for r in bundle.records
    ):
        raise ValueError("requires standard pose labels")
    if any(r.valid and r.hand != "Right" for r in bundle.records):
        raise ValueError("requires right-hand valid observations")
    if bundle.features.ndim != 2 or bundle.features.shape[1] != 60 or not np.isfinite(bundle.features).all():
        raise ValueError("expected finite 60-column input features")
    _validate_assignment_evaluation_bundle(bundle)
    participant = next(iter(participants))
    settings = SETTINGS[participant]
    start = perf_counter()
    transformed = _transformed(bundle)
    transform_seconds = perf_counter() - start
    return {
        "purpose": "exploratory DEVELOPMENT only; no production change or model approval",
        "participant": participant, "input_hashes": dataset_hashes(bundle),
        "settings": dict(zip(("algorithm", "multiplier", "margin"), settings, strict=True)),
        "conditions": [_condition(bundle, "wrist-scale-v1", settings, 0.0),
                       _condition(transformed, EXPERIMENT, settings, transform_seconds)],
        "limits": ["Negative-command counts are predictions, not live actions.",
                   "Inspect per-class recall and negative acceptance alongside aggregate F1.",
                   "Deployment requires a new freeze and fresh independent evaluation.",
                   "Orientation can distinguish custom poses; do not apply this to all profiles."],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.output.exists() or args.output.is_symlink():
        parser.error("output already exists; choose a new private filename")
    result = compare_representations(load_dataset(args.manifest))
    text = json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as handle:
        handle.write(text)
    print(f"Private representation comparison saved: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
