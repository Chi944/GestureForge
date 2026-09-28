import json
import subprocess
import sys
from dataclasses import replace

import pytest

from gestureforge.dataset import DatasetBundle
from gestureforge.evaluate import (
    UNKNOWN,
    classification_metrics,
    evaluate_algorithm,
    evaluate_config,
    trial_majority_predictions,
    validation_negative_metrics,
)
from gestureforge.fixtures import synthetic_dataset


def test_evaluate_config_reports_both_algorithms_for_synthetic_fixture() -> None:
    result = evaluate_config(
        {
            "algorithms": ["knn", "svm"],
            "rejection_multiplier": 1.5,
            "rejection_margin": 1.2,
            "synthetic_fixture": {
                "trials_per_label_per_split": 2,
                "samples_per_trial": 5,
                "seed": 304,
            },
        }
    )

    assert result["dataset"]["metadata"]["provenance"] == "SYNTHETIC"
    assert [entry["algorithm"] for entry in result["results"]] == ["knn", "svm"]
    assert all(entry["model"]["margin"] == 1.2 for entry in result["results"])
    assert all(entry["metrics"]["macro_f1"] == 1.0 for entry in result["results"])


def test_validation_changes_cannot_change_fitted_rejection_thresholds():
    bundle = synthetic_dataset(trials_per_label_per_split=2)
    baseline = evaluate_algorithm(bundle)
    changed_features = bundle.features.copy()
    for record in bundle.records:
        if record.split != "train" and record.feature_index is not None:
            changed_features[record.feature_index] += 100
    changed = evaluate_algorithm(replace(bundle, features=changed_features))
    assert baseline["model"]["rejection_reference"] == "leave_one_trial_out"
    assert baseline["model"]["thresholds"] == changed["model"]["thresholds"]
    assert changed["metrics"]["macro_f1"] == 0


def test_trial_majority_marks_ties_unknown() -> None:
    records = []
    predictions = []
    for index, scored_label in enumerate(["NEXT", "PREVIOUS", "NEXT", "PREVIOUS"]):
        records.append(
            type(
                "Record",
                (),
                {
                    "trial_id": "T1",
                    "intended_label": "NEXT",
                    "sample_index": index,
                },
            )()
        )
        predictions.append({"scored_label": scored_label})

    trial_predictions = trial_majority_predictions(tuple(records), predictions)

    assert trial_predictions == [{"trial_id": "T1", "true_label": "NEXT", "predicted_label": UNKNOWN}]


def test_classification_metrics_counts_unknown_as_miss() -> None:
    metrics = classification_metrics(
        [
            {"trial_id": "T1", "true_label": "NEXT", "predicted_label": "NEXT"},
            {"trial_id": "T2", "true_label": "NEXT", "predicted_label": UNKNOWN},
        ]
    )

    assert metrics["confusion"]["NEXT"]["NEXT"] == 1
    assert metrics["confusion"]["NEXT"][UNKNOWN] == 1
    assert metrics["per_class"]["NEXT"]["recall"] == 0.5


def test_validation_negative_metrics_reports_accepted_command_fraction() -> None:
    metrics = validation_negative_metrics(
        [
            {"accepted": True, "raw_label": "NEXT"},
            {"accepted": True, "raw_label": "NEUTRAL"},
            {"accepted": False, "raw_label": "BOOKMARK"},
        ]
    )

    assert metrics["accepted_command_predictions"] == 1
    assert metrics["accepted_command_predictions_fraction"] == 1 / 3


def test_evaluate_cli_writes_json(tmp_path) -> None:
    config_path = tmp_path / "config.json"
    output_path = tmp_path / "result.json"
    config_path.write_text(
        json.dumps(
            {
                "algorithm": "knn",
                "synthetic_fixture": {
                    "trials_per_label_per_split": 2,
                    "samples_per_trial": 5,
                    "seed": 304,
                },
            }
        ),
        encoding="utf-8",
    )

    completed = subprocess.run(
        [sys.executable, "-m", "gestureforge.evaluate", "--config", str(config_path), "--output", str(output_path)],
        check=True,
        capture_output=True,
        text=True,
    )

    assert completed.stdout == ""
    loaded = json.loads(output_path.read_text(encoding="utf-8"))
    assert loaded["results"][0]["algorithm"] == "knn"


def test_evaluate_rejects_synthetic_human_mixing() -> None:
    bundle = synthetic_dataset(trials_per_label_per_split=2)
    records = list(bundle.records)
    records[0] = replace(records[0], provenance="human", participant_id="P001")
    mixed = DatasetBundle(
        manifest_path=None,
        records=tuple(records),
        features=bundle.features,
        metadata={"provenance": "mixed"},
    )

    with pytest.raises(ValueError, match="cannot mix synthetic and human"):
        evaluate_algorithm(mixed)
