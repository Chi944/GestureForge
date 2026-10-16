"""Generated software fixtures; these do not establish participant recognition."""

from dataclasses import replace
from unittest.mock import Mock

import pytest

from gestureforge.app import load_personal_model
from gestureforge.dataset import load_dataset, save_dataset
from gestureforge.fixtures import synthetic_dataset


def _dataset(tmp_path, hand, chosen_hand):
    bundle = synthetic_dataset(trials_per_label_per_split=2)
    records = [replace(record, participant_id="TEST_PERSON", hand=hand, provenance="human")
               for record in bundle.records]
    for index, invalid_hand in enumerate((None, "Left" if hand == "Right" else "Right")):
        records.append(replace(records[0], trial_id=f"invalid-trial-{index}", valid=False,
                               feature_index=None, hand=invalid_hand))
    return save_dataset(tmp_path, records, bundle.features,
                        {"chosen_hand": chosen_hand, "warning": "GENERATED SOFTWARE TEST ONLY"})


@pytest.mark.parametrize("studio", [False, True])
@pytest.mark.parametrize("hand,chosen_hand", [("Left", "Right"), ("Right", "Left")])
def test_personal_loader_rejects_hand_mismatch_before_fitting(tmp_path, monkeypatch,
                                                           studio, hand, chosen_hand):
    bundle = _dataset(tmp_path, hand, chosen_hand)
    train = Mock(side_effect=AssertionError("Mismatched hands must not reach model fitting"))
    monkeypatch.setattr("gestureforge.models.train_model", train)

    with pytest.raises(ValueError, match="dataset hand does not match the selected hand"):
        load_personal_model(bundle.manifest_path, studio=studio)

    train.assert_not_called()


@pytest.mark.parametrize("hand", ["Left", "Right"])
def test_personal_loader_retains_invalid_detections_without_fitting_them(tmp_path, hand):
    bundle = _dataset(tmp_path, hand, hand)

    model, selected_hand, profile, vocabulary = load_personal_model(bundle.manifest_path, studio=True)

    assert (selected_hand, profile, vocabulary) == (hand, "TEST_PERSON", bundle.vocabulary)
    assert model.config.algorithm == "knn"
    assert (model.config.multiplier, model.config.margin) == (1.5, 1.5)
    assert model.predict(bundle.features[0]) == (bundle.records[0].intended_label, True, "")
    assert len(model.train_features_scaled) == len(bundle.valid_records("train"))
    assert load_dataset(bundle.manifest_path).records == bundle.records
