"""Launch the prototype, optionally with a personally collected dataset."""

import argparse
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, help="Human collection manifest; omitted for keyboard-only viewer")
    parser.add_argument("--algorithm", choices=["knn", "svm"], default="knn")
    parser.add_argument("--multiplier", type=float, default=1.5)
    parser.add_argument("--margin", type=float, default=1.5)
    parser.add_argument("--camera", type=int, default=0)
    parser.add_argument("--studio", action="store_true", help="Open the project Studio preview shell")
    parser.add_argument(
        "--studio-mode", choices=["preview", "rehearsal"], default="preview",
        help="Studio routing mode; both modes simulate actions only",
    )
    parser.add_argument("--smoke-test", action="store_true", help="Render and close without using the camera")
    parser.add_argument("--screenshot", type=Path, help="Save the app's own window during --smoke-test")
    args = parser.parse_args()
    from .capture import DEFAULT_ASSET
    from .contracts import RoutingMode
    from .features import extract_feature_vector
    from .app import Window
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import QTimer

    model = None
    hand = "Right"
    profile = "pilot"
    note = "Keyboard demo • collect your gestures before enabling camera control. See the User Guide."
    if args.studio:
        note = (
            "Studio preview • camera control needs a starter or personal dataset. "
            "Shortcut dispatch, enrolment and workspace persistence are intentionally not enabled here."
        )
    if args.dataset:
        from .dataset import load_dataset
        from .models import train_model
        try:
            bundle = load_dataset(args.dataset)
            if any(record.provenance != "human" for record in bundle.records):
                raise ValueError("Synthetic fixtures cannot enable live control. Collect personal gestures.")
            participants = {record.participant_id for record in bundle.records}
            if len(participants) != 1:
                raise ValueError("Live control requires exactly one participant's dataset.")
            profile = next(iter(participants))
            hand = bundle.metadata.get("chosen_hand", "Right")
            features, labels, records = bundle.training_data()
            model = train_model(features, labels, args.algorithm, args.multiplier, args.margin,
                                groups=[record.trial_id for record in records])
            note = (
                f"Personal dataset: {profile} • {hand} hand • {args.algorithm.upper()} "
                f"• margin {args.margin:g} • local processing"
            )
        except (OSError, ValueError, KeyError) as exc:
            parser.exit(1, f"Cannot load gesture dataset: {exc}\n")
    app = QApplication(sys.argv[:1])
    window = Window(
        model, extract_feature_vector, hand, args.camera, DEFAULT_ASSET, profile, note,
        studio=args.studio, studio_mode=RoutingMode(args.studio_mode.upper()),
    )
    window.show()
    window.raise_()
    window.activateWindow()
    if args.smoke_test:
        def finish():
            if args.screenshot:
                args.screenshot.parent.mkdir(parents=True, exist_ok=True)
                window.grab().save(str(args.screenshot))
            window.close()
        QTimer.singleShot(500, finish)
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
