import json

import numpy as np
import pytest

from gestureforge.dataset import SampleRecord, load_dataset, save_dataset


def _record(trial_id: str, split: str, valid: bool = True) -> SampleRecord:
    return SampleRecord(
        participant_id="P001",
        session_id=f"S-{split}",
        trial_id=trial_id,
        intended_label="NEXT",
        split=split,
        sample_index=0,
        timestamp=1.0,
        valid=valid,
        validity_reason="" if valid else "no_hand",
        hand="Right",
    )


def test_save_and_load_dataset_preserves_invalid_records(tmp_path) -> None:
    features = np.ones((2, 60), dtype=np.float32)
    records = [_record("T1", "train"), _record("T2", "validation", valid=False), _record("T3", "validation")]

    saved = save_dataset(tmp_path / "manifest.json", records, features, {"provenance": "human"})
    loaded = load_dataset(saved.manifest_path)

    assert loaded.metadata["provenance"] == "human"
    assert loaded.features.shape == (2, 60)
    assert len(loaded.records) == 3
    assert loaded.records[1].valid is False
    assert loaded.records[1].feature_index is None
    train_features, train_labels, train_records = loaded.training_data()
    assert train_features.shape == (1, 60)
    assert train_labels.tolist() == ["NEXT"]
    assert train_records[0].trial_id == "T1"


def test_dataset_rejects_trial_split_leakage(tmp_path) -> None:
    records = [_record("T1", "train"), _record("T1", "validation")]
    features = np.ones((2, 60), dtype=np.float32)

    with pytest.raises(ValueError, match="multiple splits"):
        save_dataset(tmp_path / "manifest.json", records, features)


def test_dataset_rejects_hash_mismatch(tmp_path) -> None:
    saved = save_dataset(tmp_path / "manifest.json", [_record("T1", "train")], np.ones((1, 60)))
    assert saved.manifest_path is not None
    manifest = json.loads(saved.manifest_path.read_text(encoding="utf-8"))
    sidecar = saved.manifest_path.with_name(manifest["feature_file"])
    sidecar.write_bytes(b"changed")

    with pytest.raises(ValueError, match="hash mismatch"):
        load_dataset(saved.manifest_path)


def test_dataset_allows_validation_negative_unknown_records(tmp_path) -> None:
    record = SampleRecord(
        participant_id="P001",
        session_id="S-negative",
        trial_id="NEG-1",
        intended_label="UNKNOWN",
        split="validation_negative",
        sample_index=0,
        timestamp=1.0,
        valid=True,
        hand="Right",
    )

    saved = save_dataset(tmp_path / "manifest.json", [record], np.ones((1, 60)))

    assert load_dataset(saved.manifest_path).records[0].intended_label == "UNKNOWN"


def test_dataset_rejects_loose_json_bool(tmp_path) -> None:
    saved = save_dataset(tmp_path / "manifest.json", [_record("T1", "train")], np.ones((1, 60)))
    assert saved.manifest_path is not None
    manifest = json.loads(saved.manifest_path.read_text(encoding="utf-8"))
    manifest["records"][0]["valid"] = "false"
    saved.manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

    with pytest.raises(ValueError, match="valid must be a boolean"):
        load_dataset(saved.manifest_path)


def test_dataset_save_is_recoverable_if_manifest_replace_fails(tmp_path, monkeypatch) -> None:
    path = tmp_path / "manifest.json"
    first = save_dataset(path, [_record("T1", "train")], np.ones((1, 60)))
    assert first.manifest_path is not None
    original_replace = type(path).replace

    def flaky_replace(self, target):
        if str(self).endswith(".tmp"):
            raise RuntimeError("simulated manifest replace failure")
        return original_replace(self, target)

    monkeypatch.setattr(type(path), "replace", flaky_replace)

    with pytest.raises(RuntimeError, match="simulated"):
        save_dataset(path, [_record("T2", "train")], np.full((1, 60), 2.0))

    recovered = load_dataset(path)
    assert recovered.records[0].trial_id == "T1"
    assert float(recovered.features[0, 0]) == 1.0


def test_dataset_rejects_multiple_chosen_hands(tmp_path) -> None:
    left = _record("T1", "train")
    right = SampleRecord(**{**left.__dict__, "trial_id": "T2", "sample_index": 1, "hand": "Left"})

    with pytest.raises(ValueError, match="one chosen hand"):
        save_dataset(tmp_path / "manifest.json", [left, right], np.ones((2, 60)))
