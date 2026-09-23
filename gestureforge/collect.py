"""Guided trial collection. Stores features, never raw camera images or audio."""

import argparse
from datetime import datetime, timezone
from pathlib import Path
import time
from uuid import uuid4

import cv2
import numpy as np

from .capture import DEFAULT_ASSET, HandCamera
from .contracts import LABELS
from .dataset import SampleRecord, load_dataset, save_dataset
from .features import extract_feature_vector

SAMPLE_OFFSETS = (0.2, 0.6, 1.0, 1.4, 1.8)


def scheduled_sample(observation, due, chosen_hand):
    """A late/missing sample remains invalid; never substitute a later good frame."""
    delay = observation.timestamp - due
    if delay < 0 or delay > 0.2:
        return None, "missed scheduled timestamp"
    try:
        return extract_feature_vector(observation, chosen_hand), ""
    except ValueError as exc:
        return None, str(exc)


def collect_trials(args):
    output = Path(args.output)
    manifest = output if output.suffix == ".json" else output / "manifest.json"
    records = []
    features = []
    sessions = []
    trial_start_times = {}
    if manifest.exists():
        existing = load_dataset(manifest)
        if any(record.participant_id != args.participant for record in existing.records):
            raise ValueError("Use a separate dataset for each participant.")
        if existing.metadata.get("chosen_hand", args.hand) != args.hand:
            raise ValueError("A dataset must use one chosen hand. Create a new dataset.")
        if any(record.provenance != "human" for record in existing.records):
            raise ValueError("Do not append participant data to a synthetic fixture.")
        records = list(existing.records)
        features = list(existing.features)
        sessions = list(existing.metadata.get("sessions", []))
        trial_start_times = dict(existing.metadata.get("trial_start_times", {}))
    session_id = f"{args.split}-{uuid4().hex[:12]}"
    sessions.append({"session_id": session_id, "split": args.split,
                     "collected_at": datetime.now(timezone.utc).isoformat(),
                     "setup": args.setup, "camera_index": args.camera,
                     "consent_confirmed_by_operator": True})
    labels = ("UNKNOWN",) if args.split == "validation_negative" else LABELS
    metadata = {"provenance": "human", "chosen_hand": args.hand, "sessions": sessions,
                "sampling_offsets_seconds": list(SAMPLE_OFFSETS), "raw_video_recorded": False,
                "trial_start_times": trial_start_times,
                "timestamp_policy": "Capture time when observed; scheduled time for missing slots"}
    completed = 0
    try:
        with HandCamera(args.asset, args.camera, session_id, args.participant) as camera:
            for label in labels:
                for trial in range(args.trials):
                    # Operator confirms the intended pose before the timed interval.
                    while True:
                        frame, _ = camera.read()
                        show(frame, f"{label} | trial {trial + 1}/{args.trials}",
                             "Prepare pose, SPACE begins 2s countdown. Q cancels.")
                        key = cv2.waitKey(1) & 0xFF
                        if key == ord("q"):
                            raise KeyboardInterrupt
                        if key == 32:
                            break
                    start = time.monotonic() + 2.0
                    trial_id = f"{session_id}-{label}-{trial:02d}"
                    trial_start_times[trial_id] = start
                    pending_records = []
                    pending_features: list[np.ndarray] = []
                    sample = 0
                    while time.monotonic() < start + 2.2:
                        frame, observation = camera.read()
                        now = time.monotonic()
                        cue = f"Hold steady: {max(0, start + 2 - now):.1f}s" if now >= start else f"Get ready: {start - now:.1f}s"
                        show(frame, label, cue)
                        if cv2.waitKey(1) & 0xFF == ord("q"):
                            raise KeyboardInterrupt
                        while sample < 5 and observation.timestamp >= start + SAMPLE_OFFSETS[sample]:
                            due = start + SAMPLE_OFFSETS[sample]
                            feature, reason = scheduled_sample(observation, due, args.hand)
                            index = len(features) + len(pending_features) if feature is not None else None
                            if feature is not None:
                                pending_features.append(feature)
                            pending_records.append(SampleRecord(
                                args.participant, session_id, trial_id, label, args.split,
                                sample, observation.timestamp, feature is not None, index, reason,
                                args.hand, "human",
                            ))
                            sample += 1
                    # Preserve all five scheduled slots, including slow/absent camera output.
                    while sample < 5:
                        pending_records.append(SampleRecord(
                            args.participant, session_id, trial_id, label, args.split,
                            sample, start + SAMPLE_OFFSETS[sample], False,
                            validity_reason="missed scheduled timestamp", hand=args.hand,
                        ))
                        sample += 1
                    records.extend(pending_records)
                    features.extend(pending_features)
                    matrix = np.asarray(features, dtype=np.float32).reshape(-1, 60)
                    save_dataset(manifest, records, matrix, metadata)
                    completed += 1
                    print(f"Saved {label} trial {trial + 1}: {len(pending_features)}/5 valid")
                    release_until = time.monotonic() + 1
                    while time.monotonic() < release_until:
                        frame, _ = camera.read()
                        show(frame, "Release pose", "Relax your hand before the next trial.")
                        if cv2.waitKey(1) & 0xFF == ord("q"):
                            raise KeyboardInterrupt
    except KeyboardInterrupt:
        print("Collection stopped; only complete trials were saved.")
    finally:
        cv2.destroyAllWindows()
    print(f"{completed} completed trials saved to {manifest}")


def show(frame, title, instruction):
    preview = cv2.flip(frame, 1)
    cv2.rectangle(preview, (0, 0), (preview.shape[1], 90), (22, 29, 38), -1)
    cv2.putText(preview, title, (16, 32), cv2.FONT_HERSHEY_SIMPLEX, .75, (110, 235, 185), 2)
    cv2.putText(preview, instruction, (16, 64), cv2.FONT_HERSHEY_SIMPLEX, .45, (245, 245, 245), 1)
    cv2.imshow("GestureForge | data collection (commands disabled)", preview)
    cv2.setWindowProperty("GestureForge | data collection (commands disabled)",
                          cv2.WND_PROP_TOPMOST, 1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default="data/local/pilot")
    parser.add_argument("--participant", default="P01", help="Pseudonymous ID, not a name")
    parser.add_argument("--split", choices=["train", "validation", "validation_negative"], required=True)
    parser.add_argument("--hand", choices=["Left", "Right"], default="Right")
    parser.add_argument("--trials", type=int, default=8)
    parser.add_argument("--camera", type=int, default=0)
    parser.add_argument("--asset", type=Path, default=DEFAULT_ASSET)
    parser.add_argument("--setup", required=True, help="Lighting, background and camera arrangement")
    parser.add_argument("--consent", action="store_true", help="Confirm participant permission for feature collection")
    args = parser.parse_args()
    if not args.consent:
        parser.error("Obtain participant permission, then pass --consent. No camera was opened.")
    if not 1 <= args.trials <= 50:
        parser.error("--trials must be between 1 and 50")
    try:
        collect_trials(args)
    except (OSError, ValueError, RuntimeError) as exc:
        parser.exit(1, f"Collection failed: {exc}\nCompleted trials remain in the dataset.\n")


if __name__ == "__main__":
    main()
