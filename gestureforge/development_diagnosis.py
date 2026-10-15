"""Explain fixed-model rejection using development splits, without a search."""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
from typing import Any

import numpy as np

from .dataset import DatasetBundle, dataset_hashes, load_dataset
from .evaluate import (
    _predict_records,
    _validate_assignment_evaluation_bundle,
    classification_metrics,
    trial_majority_predictions,
    validation_negative_metrics,
)
from .models import Algorithm, train_model


def _quantiles(values: list[float]) -> dict[str, float]:
    if not values:
        return {}
    return dict(zip(("p05", "p50", "p95"),
                    map(float, np.quantile(values, [0.05, 0.5, 0.95])), strict=True))


def diagnose_development(
    bundle: DatasetBundle, *, algorithm: Algorithm = "knn",
    multiplier: float = 1.5, margin: float = 1.0,
) -> dict[str, Any]:
    """Fit TRAIN once and explain the existing checks on development observations.

    A bundle containing any other split (including TEST) is refused before fit.
    Outputs are aggregates; no trial IDs, landmarks or feature vectors are emitted.
    """
    if any(r.split not in {"train", "validation", "validation_negative"}
           for r in bundle.records):
        raise ValueError("development diagnosis refuses TEST or unsupported splits")
    _validate_assignment_evaluation_bundle(bundle)
    if not any(r.split == "validation" for r in bundle.records):
        raise ValueError("development diagnosis requires VALIDATION")
    features, labels, train_records = bundle.training_data()
    groups = np.asarray([r.trial_id for r in train_records])
    model = train_model(features, labels, algorithm=algorithm, multiplier=multiplier,
                        margin=margin, vocabulary=bundle.vocabulary, groups=groups)
    scaled = model.train_features_scaled
    geometry: dict[str, Any] = {}
    for label in bundle.vocabulary.labels:
        ratios: list[float] = []
        neighbours: Counter[str] = Counter()
        for i in np.flatnonzero(labels == label):
            distances = np.linalg.norm(scaled - scaled[i], axis=1)
            same = (labels == label) & (groups != groups[i])
            other = labels != label
            nearest_other = int(np.flatnonzero(other)[np.argmin(distances[other])])
            neighbours[str(labels[nearest_other])] += 1
            ratios.append(float(distances[nearest_other] / max(np.min(distances[same]), 1e-12)))
        geometry[label] = {
            "valid_train_samples": int(np.sum(labels == label)),
            "nearest_other_labels": dict(neighbours),
            "other_to_same_distance_excluding_own_trial": _quantiles(ratios),
            "other_closer_than_same_count": sum(r < 1.0 for r in ratios),
            "below_configured_margin_count": sum(r < margin for r in ratios),
        }

    sections: dict[str, Any] = {}
    for split in ("validation", "validation_negative"):
        records = tuple(r for r in bundle.records if r.split == split)
        predictions = _predict_records(model, bundle, records)
        details: dict[str, Any] = {}
        for label in sorted({r.intended_label for r in records}):
            chosen = [(r, p) for r, p in zip(records, predictions, strict=True)
                      if r.intended_label == label]
            margins: list[float] = []
            relative_distances: list[float] = []
            competitors: Counter[str] = Counter()
            for record, prediction in chosen:
                if not record.valid or record.feature_index is None:
                    continue
                row = model.scaler.transform(bundle.features[record.feature_index].reshape(1, -1))[0]
                distances = np.linalg.norm(scaled - row, axis=1)
                predicted = prediction["raw_label"]
                same = float(np.min(distances[labels == predicted]))
                other = labels != predicted
                other_index = int(np.flatnonzero(other)[np.argmin(distances[other])])
                competitors[str(labels[other_index])] += 1
                margins.append(float(distances[other_index] / max(same, 1e-12)))
                relative_distances.append(same / max(model.thresholds[predicted], 1e-12))
            details[label] = {
                "scheduled_slots": len(chosen),
                "valid_slots": sum(r.valid for r, _ in chosen),
                "raw_labels": dict(Counter(p["raw_label"] for _, p in chosen)),
                "outcomes": dict(Counter(p["reason"] or "accepted" for _, p in chosen)),
                "nearest_competing_labels": dict(competitors),
                "other_to_predicted_distance": _quantiles(margins),
                "distance_over_threshold": _quantiles(relative_distances),
            }
        summary = (classification_metrics(trial_majority_predictions(records, predictions),
                                          bundle.vocabulary) if split == "validation"
                   else validation_negative_metrics(predictions, bundle.vocabulary))
        sections[split] = {"by_intended_label": details, "metrics": summary}
    return {
        "purpose": "development diagnosis only; fixed settings; no model selection or TEST",
        "input_hashes": dataset_hashes(bundle),
        "model": model.to_config(),
        "training_geometry": geometry,
        "splits": sections,
        "limits": ["Distance ratios are geometric diagnostics, not calibrated confidence.",
                   "No physical pose or runtime cause is established by numeric records.",
                   "Training geometry excludes the entire query trial; its scaler uses TRAIN.",
                   "Classifier sample predictions are not live controller actions."],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--algorithm", choices=("knn", "svm"), default="knn")
    parser.add_argument("--multiplier", type=float, default=1.5)
    parser.add_argument("--margin", type=float, default=1.0)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.output.exists() or args.output.is_symlink():
        parser.error("output already exists; choose a new private filename")
    result = diagnose_development(load_dataset(args.manifest), algorithm=args.algorithm,
                                  multiplier=args.multiplier, margin=args.margin)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")
    print(f"Private development diagnosis saved: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
