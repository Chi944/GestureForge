"""Synthetic fixtures for software tests, not participant evidence."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

from .contracts import LABELS
from .dataset import DatasetBundle, SampleRecord, save_dataset


def synthetic_dataset(
    trials_per_label_per_split: int = 3,
    samples_per_trial: int = 5,
    seed: int = 304,
) -> DatasetBundle:
    rng = np.random.default_rng(seed)
    centers = {
        label: _class_center(index, rng)
        for index, label in enumerate(LABELS)
    }
    features: list[np.ndarray] = []
    records: list[SampleRecord] = []
    timestamp = 0.0
    for split in ("train", "validation"):
        for label in LABELS:
            for trial_index in range(trials_per_label_per_split):
                trial_id = f"SYN-{split}-{label}-{trial_index:02d}"
                for sample_index in range(samples_per_trial):
                    features.append(
                        centers[label] + rng.normal(0.0, 0.025 if split == "train" else 0.035, 60)
                    )
                    records.append(
                        SampleRecord(
                            participant_id="SYNTHETIC_SOFTWARE_TEST_ONLY",
                            session_id=f"SYN-{split}",
                            trial_id=trial_id,
                            intended_label=label,
                            split=split,
                            sample_index=sample_index,
                            timestamp=timestamp,
                            valid=True,
                            feature_index=len(features) - 1,
                            hand="Right",
                            provenance="synthetic",
                        )
                    )
                    timestamp += 0.2
    return DatasetBundle(
        manifest_path=None,
        records=tuple(records),
        features=np.asarray(features, dtype=np.float32),
        metadata={
            "provenance": "SYNTHETIC",
            "warning": "Generated only for software tests; do not report as participant evidence.",
            "seed": seed,
        },
    )


def save_synthetic_dataset(path: str | Path, seed: int = 304) -> DatasetBundle:
    bundle = synthetic_dataset(seed=seed)
    return save_dataset(path, bundle.records, bundle.features, bundle.metadata)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate a synthetic GestureForge test fixture.")
    parser.add_argument("path", help="Output manifest path or directory.")
    parser.add_argument("--seed", type=int, default=304)
    args = parser.parse_args(argv)
    bundle = save_synthetic_dataset(args.path, seed=args.seed)
    assert bundle.manifest_path is not None
    print(f"wrote synthetic fixture manifest: {bundle.manifest_path}")
    return 0


def _class_center(index: int, rng: np.random.Generator) -> np.ndarray:
    center = rng.normal(0.0, 0.05, 60)
    start = index * 12
    center[start : start + 12] += 1.0 + index * 0.25
    return center.astype(np.float32)


if __name__ == "__main__":
    raise SystemExit(main())
