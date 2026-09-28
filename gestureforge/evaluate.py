"""Reproducible prototype evaluation CLI."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import asdict
import json
from pathlib import Path
from time import perf_counter
from typing import Any

import numpy as np

from .contracts import LABELS
from .dataset import DatasetBundle, SampleRecord, dataset_hashes, load_dataset, merge_datasets
from .fixtures import synthetic_dataset
from .models import train_model

UNKNOWN = "UNKNOWN"
COMMAND_LABELS = {"NEXT", "PREVIOUS", "BOOKMARK"}


def evaluate_config(config: dict[str, Any]) -> dict[str, Any]:
    bundle = _load_config_dataset(config)
    algorithms = config.get("algorithms") or [config.get("algorithm", "knn")]
    multiplier = float(config.get("rejection_multiplier", 1.5))
    margin = float(config.get("rejection_margin", 1.0))
    results = []
    for algorithm in algorithms:
        results.append(evaluate_algorithm(bundle, str(algorithm), multiplier, margin))
    return {
        "dataset": {
            "manifest_path": None if bundle.manifest_path is None else str(bundle.manifest_path),
            "metadata": bundle.metadata,
            "hashes": dataset_hashes(bundle),
        },
        "results": results,
    }


def evaluate_algorithm(
    bundle: DatasetBundle, algorithm: str = "knn", multiplier: float = 1.5, margin: float = 1.0
) -> dict[str, Any]:
    train_features, train_labels, train_records = bundle.training_data()
    _validate_assignment_evaluation_bundle(bundle)
    if len(train_features) == 0:
        raise ValueError("dataset has no valid training samples")
    model = train_model(train_features, train_labels, algorithm=algorithm, multiplier=multiplier,  # type: ignore[arg-type]
                        margin=margin,
                        groups=[record.trial_id for record in train_records])

    validation_records = tuple(record for record in bundle.records if record.split == "validation")
    if not validation_records:
        raise ValueError("dataset has no validation samples")
    validation_negative_records = tuple(
        record for record in bundle.records if record.split == "validation_negative"
    )
    start = perf_counter()
    sample_predictions = _predict_records(model, bundle, validation_records)
    negative_predictions = _predict_records(model, bundle, validation_negative_records)
    predict_seconds = perf_counter() - start
    trial_predictions = trial_majority_predictions(validation_records, sample_predictions)
    metrics = classification_metrics(trial_predictions)
    metrics["validation_negative"] = validation_negative_metrics(negative_predictions)
    return {
        "algorithm": algorithm,
        "model": model.to_config(),
        "train_samples": len(train_records),
        "validation_samples": len(validation_records),
        "validation_negative_samples": len(validation_negative_records),
        "validation_trials": len(trial_predictions),
        "timing": {
            "fit_seconds": model.fit_seconds,
            "predict_seconds": predict_seconds,
            "predict_seconds_per_sample": predict_seconds / max(
                1, len(validation_records) + len(validation_negative_records)
            ),
        },
        "metrics": metrics,
        "sample_predictions": sample_predictions,
        "validation_negative_predictions": negative_predictions,
        "trial_predictions": trial_predictions,
    }


def trial_majority_predictions(
    records: tuple[SampleRecord, ...], sample_predictions: list[dict[str, Any]]
) -> list[dict[str, str]]:
    by_trial: dict[str, dict[int, str]] = defaultdict(dict)
    labels_by_trial: dict[str, str] = {}
    for record, prediction in zip(records, sample_predictions, strict=True):
        by_trial[record.trial_id][record.sample_index] = str(prediction["scored_label"])
        labels_by_trial[record.trial_id] = record.intended_label

    results: list[dict[str, str]] = []
    for trial_id in sorted(by_trial):
        five_slots = [by_trial[trial_id].get(index, UNKNOWN) for index in range(5)]
        counts = Counter(five_slots)
        [(top_label, top_count), *rest] = counts.most_common()
        if top_count < 3 or (rest and rest[0][1] == top_count):
            top_label = UNKNOWN
        results.append(
            {
                "trial_id": trial_id,
                "true_label": labels_by_trial[trial_id],
                "predicted_label": top_label,
            }
        )
    return results


def classification_metrics(trial_predictions: list[dict[str, str]]) -> dict[str, Any]:
    columns = [*LABELS, UNKNOWN]
    confusion = {label: {column: 0 for column in columns} for label in LABELS}
    for prediction in trial_predictions:
        true_label = prediction["true_label"]
        predicted_label = prediction["predicted_label"]
        if true_label in confusion and predicted_label in columns:
            confusion[true_label][predicted_label] += 1

    per_class: dict[str, dict[str, float]] = {}
    f1_values: list[float] = []
    for label in LABELS:
        tp = confusion[label][label]
        fp = sum(confusion[other][label] for other in LABELS if other != label)
        fn = sum(confusion[label][column] for column in columns if column != label)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        f1_values.append(f1)
        per_class[label] = {"precision": precision, "recall": recall, "f1": f1}
    return {
        "macro_f1": float(np.mean(f1_values)) if f1_values else 0.0,
        "per_class": per_class,
        "confusion": confusion,
        "columns": columns,
    }


def validation_negative_metrics(predictions: list[dict[str, Any]]) -> dict[str, Any]:
    accepted_commands = sum(
        1
        for prediction in predictions
        if prediction["accepted"] and prediction["raw_label"] in COMMAND_LABELS
    )
    total = len(predictions)
    return {
        "samples": total,
        "accepted_command_predictions": accepted_commands,
        "accepted_command_predictions_fraction": accepted_commands / total if total else None,
        "measurement": "classifier predictions only, not live controller actions",
    }


def _predict_records(
    model: Any, bundle: DatasetBundle, records: tuple[SampleRecord, ...]
) -> list[dict[str, Any]]:
    predictions: list[dict[str, Any]] = []
    for record in records:
        if not record.valid or record.feature_index is None:
            predictions.append(
                {
                    "trial_id": record.trial_id,
                    "sample_index": record.sample_index,
                    "true_label": record.intended_label,
                    "raw_label": UNKNOWN,
                    "accepted": False,
                    "reason": record.validity_reason or "invalid_sample",
                    "scored_label": UNKNOWN,
                }
            )
            continue
        result = model.predict_one(bundle.features[record.feature_index])
        predictions.append(
            {
                "trial_id": record.trial_id,
                "sample_index": record.sample_index,
                "true_label": record.intended_label,
                "raw_label": result.label,
                "accepted": result.accepted,
                "reason": result.reason,
                "distance": result.distance,
                "threshold": result.threshold,
                "scored_label": result.label if result.accepted else UNKNOWN,
            }
        )
    return predictions


def _load_config_dataset(config: dict[str, Any]) -> DatasetBundle:
    if "dataset_path" in config:
        dataset_path = config["dataset_path"]
        if isinstance(dataset_path, list):
            return merge_datasets([load_dataset(path) for path in dataset_path])
        return load_dataset(dataset_path)
    if "dataset_paths" in config:
        return merge_datasets([load_dataset(path) for path in config["dataset_paths"]])
    fixture = config.get("synthetic_fixture")
    if fixture:
        seed = int(fixture.get("seed", 304))
        return synthetic_dataset(
            trials_per_label_per_split=int(fixture.get("trials_per_label_per_split", 3)),
            samples_per_trial=int(fixture.get("samples_per_trial", 5)),
            seed=seed,
        )
    raise ValueError("config must define dataset_path or synthetic_fixture")


def _validate_assignment_evaluation_bundle(bundle: DatasetBundle) -> None:
    provenances = {record.provenance for record in bundle.records}
    if "synthetic" in provenances and len(provenances) > 1:
        raise ValueError("evaluation cannot mix synthetic and human records")
    participants = {record.participant_id for record in bundle.records if record.provenance != "synthetic"}
    if len(participants) > 1:
        raise ValueError("assignment evaluation supports one participant/profile per run")
    train_provenances = {record.provenance for record in bundle.records if record.split == "train"}
    if "synthetic" in train_provenances and len(train_provenances) > 1:
        raise ValueError("training cannot mix synthetic and human records")
    hands = {record.hand for record in bundle.records if record.valid and record.hand is not None}
    if len(hands) > 1:
        raise ValueError("assignment evaluation supports one chosen hand per run")
    split_counts = Counter(record.split for record in bundle.records)
    if split_counts["train"] == 0:
        raise ValueError("dataset has no training samples")
    if split_counts["validation"] == 0:
        raise ValueError("dataset has no validation samples")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate GestureForge prototype classifiers.")
    parser.add_argument("--config", required=True, help="Evaluation JSON config.")
    parser.add_argument("--output", help="Optional JSON output path.")
    args = parser.parse_args(argv)

    config_path = Path(args.config)
    config = json.loads(config_path.read_text(encoding="utf-8"))
    result = evaluate_config(config)
    text = json.dumps(result, indent=2, sort_keys=True, default=_json_default) + "\n"
    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


def _json_default(value: Any) -> Any:
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, SampleRecord):
        return asdict(value)
    raise TypeError(f"object of type {type(value).__name__} is not JSON serialisable")


if __name__ == "__main__":
    raise SystemExit(main())
