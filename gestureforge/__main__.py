"""Launch the prototype, optionally with a personally collected dataset."""

import argparse
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument("--dataset", type=Path, help="Human collection manifest; omitted for keyboard-only viewer")
    parser.add_argument("--profile-id", help="Saved Studio profile ID to load from the private profile store")
    parser.add_argument("--profile-store", type=Path, default=Path(".local/profiles"),
                        help="Private saved-profile folder for --profile-id")
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
    explicit_model_flags = {
        flag for flag in ("--algorithm", "--multiplier", "--margin")
        if any(token == flag or token.startswith(f"{flag}=") for token in sys.argv[1:])
    }
    if args.profile_id:
        if not args.studio:
            parser.exit(1, "--profile-id is available only in --studio mode.\n")
        if args.dataset:
            parser.exit(1, "--profile-id cannot be used with --dataset.\n")
        if explicit_model_flags:
            parser.exit(
                1,
                "Saved profiles use their stored model settings; do not pass "
                "--algorithm, --multiplier or --margin with --profile-id.\n",
            )
    from .capture import DEFAULT_ASSET
    from .contracts import RoutingMode
    from .features import extract_feature_vector
    from .app import Window, load_personal_model
    from .profiles import ProfileStore
    from .vocabulary import LEGACY_VOCABULARY
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import QTimer

    model = None
    vocabulary = LEGACY_VOCABULARY
    hand = "Right"
    profile = "pilot"
    profile_display_name = None
    profile_store = ProfileStore(args.profile_store)
    loaded_profile = None
    note = "Keyboard demo • collect your gestures before enabling camera control. See the User Guide."
    if args.studio:
        note = (
            "Studio preview • camera control needs a starter or personal dataset. "
            "Use Enrolment to collect numeric samples; shortcut dispatch and profile readiness "
            "remain in development. Workspace progress stays local."
        )
    if args.profile_id:
        try:
            loaded = profile_store.load(args.profile_id)
            loaded_profile = loaded
            record = loaded.record
            settings = record.settings
            model, hand, profile, vocabulary = loaded.model, record.selected_hand, record.profile_id, record.vocabulary
            profile_display_name = record.display_name
            args.algorithm, args.multiplier, args.margin = settings.algorithm, settings.multiplier, settings.margin
            note = (
                f"Saved profile: {record.display_name} • ID {record.profile_id} • {hand} hand • "
                "readiness unverified • local processing"
            )
        except (OSError, ValueError, KeyError) as exc:
            parser.exit(1, f"Cannot load saved profile: {exc}\n")
    elif args.dataset:
        try:
            model, hand, profile, vocabulary = load_personal_model(
                args.dataset, args.algorithm, args.multiplier, args.margin, studio=args.studio,
            )
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
        vocabulary=vocabulary,
        model_settings=(args.algorithm, args.multiplier, args.margin),
        profile_display_name=profile_display_name,
        profile_store=profile_store,
        loaded_profile=loaded_profile,
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
