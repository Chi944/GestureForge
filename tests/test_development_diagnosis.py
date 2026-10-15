from dataclasses import replace
import json

import numpy as np
import pytest

from gestureforge.development_diagnosis import diagnose_development, main
from gestureforge.evaluate import evaluate_algorithm
from gestureforge.fixtures import synthetic_dataset


@pytest.mark.parametrize("algorithm", ["knn", "svm"])
def test_diagnosis_matches_production_evaluation_and_does_not_mutate(algorithm):
    bundle = synthetic_dataset(trials_per_label_per_split=2)
    before = bundle.features.copy()
    result = diagnose_development(bundle, algorithm=algorithm, multiplier=2.0, margin=1.5)
    expected = evaluate_algorithm(bundle, algorithm=algorithm, multiplier=2.0, margin=1.5)
    assert result["splits"]["validation"]["metrics"] == {
        k: v for k, v in expected["metrics"].items() if k != "validation_negative"
    }
    assert result["splits"]["validation_negative"]["metrics"] == expected["metrics"]["validation_negative"]
    assert np.array_equal(before, bundle.features)
    assert '"trial_id"' not in json.dumps(result)
    json.dumps(result, allow_nan=False)


def test_test_data_is_refused_before_any_fit(monkeypatch):
    from gestureforge import development_diagnosis

    bundle = synthetic_dataset(trials_per_label_per_split=2)
    changed = replace(bundle, records=(*bundle.records, replace(bundle.records[0], split="test")))
    monkeypatch.setattr(development_diagnosis, "train_model", lambda *a, **kw: pytest.fail("fit occurred"))
    with pytest.raises(ValueError, match="refuses TEST"):
        diagnose_development(changed)


def test_own_trial_is_excluded_from_geometry():
    bundle = synthetic_dataset(trials_per_label_per_split=2)
    # Give each trial identical internal samples. Cross-trial distances must
    # still be nonzero; counting its own duplicate rows would hide overlap.
    features = bundle.features.copy()
    by_trial: dict[str, np.ndarray] = {}
    for record in bundle.records:
        if record.split == "train" and record.feature_index is not None:
            reference = by_trial.setdefault(record.trial_id, features[record.feature_index].copy())
            features[record.feature_index] = reference
    result = diagnose_development(replace(bundle, features=features))
    for row in result["training_geometry"].values():
        assert row["other_to_same_distance_excluding_own_trial"]["p95"] < 1e10


def test_invalid_validation_slots_are_retained():
    bundle = synthetic_dataset(trials_per_label_per_split=2)
    trial = next(r.trial_id for r in bundle.records if r.split == "validation")
    records = tuple(replace(r, valid=False, feature_index=None, validity_reason="no_hand")
                    if r.trial_id == trial else r for r in bundle.records)
    result = diagnose_development(replace(bundle, records=records))
    row = next(r for r in records if r.trial_id == trial)
    assert result["splits"]["validation"]["by_intended_label"][row.intended_label]["outcomes"]["no_hand"] == 5
    assert result["splits"]["validation"]["metrics"]["confusion"][row.intended_label]["UNKNOWN"] >= 1


def test_existing_output_is_rejected_before_input_load(tmp_path):
    output = tmp_path / "keep.json"
    output.write_text("preserve", encoding="utf-8")
    with pytest.raises(SystemExit):
        main([str(tmp_path / "missing.json"), "--output", str(output)])
    assert output.read_text(encoding="utf-8") == "preserve"
