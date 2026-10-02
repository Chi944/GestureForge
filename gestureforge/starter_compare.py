"""Private, exploratory GF-P11 nested participant-separated model comparison.

This command never promotes a starter model or changes the fixed baseline.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from itertools import product
import json
from pathlib import Path
from typing import Any

import numpy as np

from .dataset import DatasetBundle
from .evaluate import _predict_records, classification_metrics, trial_majority_predictions
from .models import Algorithm, train_model
from .starter_evaluate import evaluate_people, load_validated_people

PEOPLE = ("P01", "P02", "P03")


@dataclass(frozen=True)
class Candidate:
    algorithm: Algorithm
    knn_k: int = 5
    knn_weights: str = "distance"
    svm_c: float = 1.0
    svm_gamma: str | float = "scale"
    multiplier: float = 1.5
    margin: float = 1.0


def candidate_grid() -> tuple[Candidate, ...]:
    """Frozen ordering is the final deterministic tie-break."""
    gammas: tuple[str | float, ...] = ("scale", 0.1)
    return tuple(
        Candidate("knn", knn_k=k, knn_weights=weight, multiplier=multiplier, margin=margin)
        for k, weight, multiplier, margin in product(
            (3, 5, 7), ("uniform", "distance"), (1.0, 1.5), (1.0, 1.2)
        )
    ) + tuple(
        Candidate("svm", svm_c=c, svm_gamma=gamma, multiplier=multiplier, margin=margin)
        for c, gamma, multiplier, margin in product(
            (0.1, 1.0, 10.0), gammas, (1.0, 1.5), (1.0, 1.2)
        )
    )


def _training_data(people: dict[str, DatasetBundle], fit_people: tuple[str, ...]
                   ) -> tuple[np.ndarray, list[str], list[str]]:
    rows: list[np.ndarray] = []
    labels: list[str] = []
    groups: list[str] = []
    for person in fit_people:
        bundle = people[person]
        for record in bundle.valid_records():
            if record.split in ("train", "validation"):
                assert record.feature_index is not None
                rows.append(bundle.features[record.feature_index])
                labels.append(record.intended_label)
                groups.append(record.trial_id)
    return np.asarray(rows, dtype=np.float32), labels, groups


def _score(model: Any, bundle: DatasetBundle) -> dict[str, Any]:
    positives = tuple(r for r in bundle.records if r.split in ("train", "validation"))
    negatives = tuple(r for r in bundle.records if r.split == "validation_negative")
    predictions = _predict_records(model, bundle, positives)
    negative_predictions = _predict_records(model, bundle, negatives)
    trials = trial_majority_predictions(positives, predictions)
    negative_trials = trial_majority_predictions(negatives, negative_predictions)
    valid_negative_predictions = [
        p for record, p in zip(negatives, negative_predictions, strict=True) if record.valid
    ]
    action_ids = set(bundle.vocabulary.action_ids)
    action_accepts = sum(
        p["accepted"] and p["raw_label"] in action_ids for p in valid_negative_predictions
    )
    neutral_accepts = sum(
        p["accepted"] and p["raw_label"] == "NEUTRAL" for p in valid_negative_predictions
    )
    rejected = sum(not p["accepted"] for p in valid_negative_predictions)
    valid_count = len(valid_negative_predictions)
    return {
        "positive_trials": len(trials),
        "positive_metrics": classification_metrics(trials, bundle.vocabulary),
        "unknown_trials": negative_trials,
        "valid_unknown_samples": valid_count,
        "invalid_detection_samples": len(negatives) - valid_count,
        "valid_unknown_rejected": rejected,
        "valid_unknown_neutral_accepted": neutral_accepts,
        "valid_unknown_action_accepted": action_accepts,
        "valid_unknown_rejection_rate": rejected / valid_count if valid_count else None,
    }


def _fit(people: dict[str, DatasetBundle], fit_people: tuple[str, ...],
         candidate: Candidate) -> Any:
    x, labels, groups = _training_data(people, fit_people)
    model = train_model(
        x, labels, algorithm=candidate.algorithm,
        multiplier=candidate.multiplier, margin=candidate.margin,
        groups=groups, vocabulary=people[fit_people[0]].vocabulary,
        knn_k=candidate.knn_k, knn_weights=candidate.knn_weights,  # type: ignore[arg-type]
        svm_c=candidate.svm_c, svm_gamma=candidate.svm_gamma,  # type: ignore[arg-type]
    )
    np.testing.assert_allclose(model.scaler.mean_, x.mean(axis=0, dtype=np.float64))
    return model


def _rank(scores: list[dict[str, Any]], order: int) -> tuple[float, float, int]:
    worst_f1 = min(s["positive_metrics"]["macro_f1"] for s in scores)
    rejection = min(s["valid_unknown_rejection_rate"] or 0.0 for s in scores)
    return (worst_f1, rejection, -order)


def _qualifies(scores: list[dict[str, Any]]) -> bool:
    return all(
        s["positive_metrics"]["macro_f1"] >= 0.85
        and s["valid_unknown_samples"] > 0
        and s["valid_unknown_action_accepted"] == 0
        for s in scores
    )


def compare(root: Path) -> dict[str, Any]:
    # The established evaluator performs strict provenance, slot and leakage checks.
    people, audit, hashes = load_validated_people(root)
    baseline = evaluate_people(people, audit, hashes)
    grid = candidate_grid()
    folds: list[dict[str, Any]] = []
    for held_out in PEOPLE:
        training_people = tuple(p for p in PEOPLE if p != held_out)
        candidates: list[dict[str, Any]] = []
        for order, candidate in enumerate(grid):
            inner_scores = []
            for fit_person, validation_person in (
                (training_people[0], training_people[1]),
                (training_people[1], training_people[0]),
            ):
                model = _fit(people, (fit_person,), candidate)
                score = _score(model, people[validation_person])
                inner_scores.append({"fit_person": fit_person,
                                     "validation_person": validation_person, **score})
            candidates.append({
                "order": order, "configuration": asdict(candidate),
                "inner_scores": inner_scores, "qualifies": _qualifies(inner_scores),
            })
        qualifying = [c for c in candidates if c["qualifies"]]
        chosen = max(qualifying, key=lambda c: _rank(c["inner_scores"], c["order"])) \
            if qualifying else None
        favourites = [
            max(candidates, key=lambda c: (
                c["inner_scores"][index]["positive_metrics"]["macro_f1"],
                c["inner_scores"][index]["valid_unknown_rejection_rate"] or 0.0,
                -c["order"],
            ))["order"]
            for index in (0, 1)
        ]
        outer = None
        if chosen is not None:
            selected = grid[chosen["order"]]
            model = _fit(people, training_people, selected)
            outer = {"model": model.to_config(), "score": _score(model, people[held_out])}
        folds.append({
            "held_out": held_out, "training_people": training_people,
            "candidates": candidates, "qualifying_candidates": len(qualifying),
            "selected_order": None if chosen is None else chosen["order"],
            "independent_inner_favourites": favourites,
            "inner_preferences_disagree": favourites[0] != favourites[1],
            "outer_result": outer,
        })
    return {
        "protocol": "GF-P11 exploratory nested leave-one-person-out; not independent final testing",
        "selection_rule": "Each inner person macro-F1 >=0.85 and zero valid UNKNOWN action accepts; "
                          "tie-break worst macro-F1, worst valid UNKNOWN rejection, fixed grid order",
        "training_policy": "Both positive sessions of fitting people only; train-only scaler and thresholds; "
                           "UNKNOWN excluded from fitting; trial groups preserved",
        "candidate_grid": [asdict(c) for c in grid],
        "library_versions": baseline["folds"][0]["model"]["library_versions"],
        "data_audit": audit, "input_hashes": hashes,
        "baseline_summary": [
            {"held_out": f["held_out"], "algorithm": f["algorithm"],
             "positive_macro_f1": f["metrics"]["macro_f1"],
             "valid_unknown_action_accepted": f["negative_metrics"]["accepted_command_predictions"]}
            for f in baseline["folds"]
        ],
        "folds": folds,
        "limits": ["These three contributors informed the experiment; all results are exploratory",
                   "Classifier outputs are not executed controller actions",
                   "Invalid detections are not classifier rejections",
                   "No starter readiness or distribution permission is established"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("Refusing to replace private comparison evidence")
    report = compare(args.root)
    text = json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as handle:
        handle.write(text)
    for fold in report["folds"]:
        print(f"{fold['held_out']}: {fold['qualifying_candidates']} qualifying; "
              f"selected={fold['selected_order']}; "
              f"inner preferences disagree={fold['inner_preferences_disagree']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
