import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

import numpy as np
import pytest

from gestureforge.contracts import LABELS
from gestureforge.dataset import load_dataset
from gestureforge.features import extract_feature_vector
from gestureforge.import_participant import MODEL_SHA256, RETENTION, import_browser_zip


def _landmarks(scale: float = 1.0) -> list[list[float]]:
    points = [[0.01 * index, 0.02 * index, 0.03 * index] for index in range(21)]
    points[0] = [0.0, 0.0, 0.0]
    points[9] = [0.0, scale, 0.0]
    return points


def _record(
    session: str,
    split: str,
    label: str,
    trial: int,
    sample: int,
    *,
    timestamp: float | None = None,
    frame_id: int | None = None,
    hand_count: int = 1,
    hand: str | None = "Right",
    landmarks: list[list[float]] | None = None,
    reason: str = "",
) -> dict:
    return {
        "session_id": session,
        "trial_id": f"{session}-{label}-{trial:02d}",
        "intended_label": label,
        "split": split,
        "sample_index": sample,
        "timestamp": (10.0 * (trial + 1) + sample if timestamp is None else timestamp),
        "frame_id": (trial * 10 + sample if frame_id is None else frame_id),
        "hand_count": hand_count,
        "hand": hand,
        "landmarks": _landmarks() if landmarks is None else landmarks,
        "validity_reason": reason,
    }


def _payload(*, partial: bool = True) -> dict:
    records = []
    sessions = [
        {
            "session_id": "train-session",
            "split": "train",
            "started_at": "2026-10-08T10:01:00Z",
            "conditions": "software test",
        },
        {
            "session_id": "validation-session",
            "split": "validation",
            "started_at": "2026-10-08T10:02:00Z",
            "conditions": "software test",
        },
    ]
    sessions.append(
        {
            "session_id": "negative-session",
            "split": "validation_negative",
            "started_at": "2026-10-08T10:03:00Z",
            "conditions": "software test",
        }
    )
    labels = ("NEUTRAL", "NEXT") if partial else LABELS
    trials = 1 if partial else 12
    for split, session in (("train", "train-session"), ("validation", "validation-session")):
        for label in labels:
            for trial in range(trials):
                for sample in range(5):
                    records.append(_record(session, split, label, trial, sample))
    if not partial:
        for trial in range(8):
            for sample in range(5):
                records.append(
                    _record(
                        "negative-session",
                        "validation_negative",
                        "UNKNOWN",
                        trial,
                        sample,
                        hand_count=0,
                        hand=None,
                        landmarks=None,
                        reason="no hand detected",
                    )
                )
    return {
        "schema_version": 1,
        "protocol": "gestureforge-browser-development-v1",
        "participant_id": "P99",
        "hand": "Right",
        "source": {
            "runtime": "mediapipe-tasks-vision-web",
            "version": "1.1.0",
            "model_sha256": MODEL_SHA256,
        },
        "consent": {
            "numeric_data": True,
            "team_and_marker_access": True,
            "retention": RETENTION,
            "recorded_at": "2026-10-08T10:00:00Z",
        },
        "sessions": sessions,
        "records": [
            dict(record, timestamp=float(index), frame_id=index)
            for index, record in enumerate(records)
        ],
    }


def _zip(tmp_path, payload: dict, name: str = "collection.json"):
    path = tmp_path / "participant.zip"
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.writestr(name, json.dumps(payload))
    return path


def test_import_browser_zip_round_trips_features_and_partial_status(tmp_path):
    payload = _payload()
    zip_path = _zip(tmp_path, payload)

    imported = import_browser_zip(zip_path, tmp_path / "manifest.json")
    loaded = load_dataset(tmp_path / "manifest.json")

    assert len(imported.records) == len(payload["records"])
    assert len(loaded.features) == len(payload["records"])
    np.testing.assert_allclose(loaded.features[0], extract_feature_vector(_landmarks()))
    assert loaded.metadata["provenance"] == "human"
    assert loaded.metadata["import_source"] == "browser-participant-kit"
    assert loaded.metadata["pose_set_id"] == "standard-v1"
    assert {record.provenance for record in loaded.records} == {"human"}
    assert {record.trial_id for record in loaded.records} == {
        f"P99-{record['trial_id']}" for record in payload["records"]
    }
    browser = loaded.metadata["browser_collection"]
    assert browser["import_status"] == "partial"
    assert browser["complete"] is False
    assert browser["counts"]["train"] == {"NEUTRAL": 1, "NEXT": 1}
    assert browser["consent"]["retention"] == RETENTION


def test_full_development_packet_reports_complete_and_keeps_unknown_invalid(tmp_path):
    payload = _payload(partial=False)
    zip_path = _zip(tmp_path, payload)

    imported = import_browser_zip(zip_path, tmp_path / "full" / "manifest.json")

    assert imported.metadata["browser_collection"]["complete"] is True
    assert imported.metadata["browser_collection"]["counts"]["validation_negative"] == {"UNKNOWN": 8}
    invalid = [record for record in imported.records if record.split == "validation_negative"]
    assert invalid
    assert all(not record.valid and record.validity_reason == "no hand detected" for record in invalid)


def test_invalid_observations_are_retained_without_feature_rows(tmp_path):
    payload = _payload()
    payload["records"][0] = _record(
        "train-session", "train", "NEUTRAL", 0, 0,
        timestamp=0.0, frame_id=0, hand_count=2, landmarks=_landmarks(), reason="multiple hands",
    )
    zip_path = _zip(tmp_path, payload)

    imported = import_browser_zip(zip_path, tmp_path / "manifest.json")

    assert imported.records[0].valid is False
    assert imported.records[0].feature_index is None
    assert imported.records[0].validity_reason == "multiple hands"
    assert len(imported.features) == len(payload["records"]) - 1


@pytest.mark.parametrize("mutate, error", [
    (lambda payload: payload.__setitem__("schema_version", True), "schema_version"),
    (lambda payload: payload.__setitem__("protocol", "other"), "protocol"),
    (lambda payload: payload.__setitem__("hand", "Left"), "Right-hand"),
    (lambda payload: payload["source"].__setitem__("version", "9"), "runtime"),
    (lambda payload: payload["consent"].__setitem__("numeric_data", False), "consent"),
    (lambda payload: payload["consent"].__setitem__("retention", "Keep until deleted."), "retention"),
    (lambda payload: payload["records"][0].__setitem__("split", "test"), "session"),
    (lambda payload: payload["records"][0].__setitem__("intended_label", "UNKNOWN"), "label"),
    (lambda payload: payload["records"][0].__setitem__("sample_index", 5), "sample_index"),
    (lambda payload: payload["records"][0].__setitem__("landmarks", [[0.0, 0.0, 0.0]]), "21x3"),
    (lambda payload: payload["records"][0].__setitem__("timestamp", -0.1), "timestamp"),
    (lambda payload: payload["records"][0].__setitem__("frame_id", -1), "frame_id"),
    (lambda payload: payload["records"][0].__setitem__("frame_id", None), "frame_id"),
    (lambda payload: payload["records"][0].__setitem__("hand_count", 3), "hand_count"),
    (lambda payload: payload["records"][0].__setitem__("hand", {"side": "Right"}), "hand"),
    (lambda payload: payload.__setitem__("records", payload["records"] * 27), "520"),
])
def test_structural_validation_rejects_bad_packets(tmp_path, mutate, error):
    payload = _payload()
    mutate(payload)

    with pytest.raises(ValueError, match=error):
        import_browser_zip(_zip(tmp_path, payload), tmp_path / "manifest.json")


@pytest.mark.parametrize("edit, error", [
    (lambda records: records.append(dict(copy.deepcopy(records[-1]), frame_id=999)), "duplicate sample_index"),
    (lambda records: records.pop(), "exactly five"),
    (lambda records: records[6].__setitem__("timestamp", records[5]["timestamp"] - 0.5), "timestamps"),
    (lambda records: records[1].__setitem__("frame_id", records[0]["frame_id"]), "reused"),
    (lambda records: records[0].__setitem__("session_id", "missing-session"), "unknown session"),
])
def test_record_consistency_rejects_ambiguous_collections(tmp_path, edit, error):
    payload = _payload()
    edit(payload["records"])

    with pytest.raises(ValueError, match=error):
        import_browser_zip(_zip(tmp_path, payload), tmp_path / "manifest.json")


def test_safe_zip_rules_reject_extra_duplicate_and_oversized_entries(tmp_path):
    payload = _payload()
    extra = tmp_path / "extra.zip"
    with zipfile.ZipFile(extra, "w") as archive:
        archive.writestr("collection.json", json.dumps(payload))
        archive.writestr("../collection.json", "{}")
    duplicate = tmp_path / "duplicate.zip"
    with zipfile.ZipFile(duplicate, "w") as archive:
        archive.writestr("collection.json", json.dumps(payload))
        archive.writestr("collection.json", json.dumps(payload))
    large = tmp_path / "large.zip"
    with zipfile.ZipFile(large, "w") as archive:
        archive.writestr("collection.json", " " * (10 * 1024 * 1024 + 1))

    for path in (extra, duplicate, large):
        with pytest.raises(ValueError, match="only collection.json|larger than 10 MB"):
            import_browser_zip(path, tmp_path / f"{path.stem}.json")


def test_import_refuses_to_overwrite_existing_manifest(tmp_path):
    output = tmp_path / "manifest.json"
    output.write_text("{}", encoding="utf-8")

    with pytest.raises(ValueError, match="already exists"):
        import_browser_zip(_zip(tmp_path, _payload()), output)


def test_import_refuses_to_overwrite_normalised_output_directory(tmp_path):
    output = tmp_path / "existing"
    output.mkdir()
    (output / "manifest.json").write_text("{}", encoding="utf-8")

    with pytest.raises(ValueError, match="already exists"):
        import_browser_zip(_zip(tmp_path, _payload()), output)


def test_actual_collector_zip_imports_through_cli(tmp_path):
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node.js is required for the browser collector interoperability check")
    script = tmp_path / "make-collector-zip.mjs"
    zip_path = tmp_path / "EMAIL_THIS_P98_PARTIAL_development.zip"
    manifest = tmp_path / "manifest.json"
    collector = (Path(__file__).resolve().parents[1] / "participant" / "collector.mjs").as_uri()
    script.write_text(
        f"""
import {{
  LABELS,
  makeCollection,
  makeStoredZip,
  makeTrialPlan,
  readOwnCollectionZip,
  sessionId,
}} from {json.dumps(collector)};
import {{ writeFileSync }} from "node:fs";

function landmarks() {{
  return Array.from({{ length: 21 }}, (_, index) => {{
    if (index === 0) return [0, 0, 0];
    if (index === 9) return [0, 1, 0];
    return [index / 100, index / 50, index / 25];
  }});
}}

const participantId = "P98";
const started = {{
  train: "2026-10-08T10:00:00.000Z",
  validation: "2026-10-08T10:20:00.000Z",
  validation_negative: "2026-10-08T10:40:00.000Z",
}};
const records = [];
let timestamp = 1;
let frame = 1;
for (const label of LABELS) {{
  const trial = makeTrialPlan().find((row) => row.split === "train" && row.label === label);
  for (let sample = 0; sample < 5; sample += 1) {{
    records.push({{
      session_id: sessionId(participantId, "train"),
      trial_id: trial.trial_id,
      intended_label: trial.label,
      split: trial.split,
      sample_index: sample,
      timestamp: timestamp++,
      frame_id: frame++,
      hand_count: 1,
      hand: "Right",
      landmarks: landmarks(),
      validity_reason: "",
    }});
  }}
}}
const negative = makeTrialPlan().find((row) => row.split === "validation_negative");
for (let sample = 0; sample < 5; sample += 1) {{
  records.push({{
    session_id: sessionId(participantId, "validation_negative"),
    trial_id: negative.trial_id,
    intended_label: "UNKNOWN",
    split: "validation_negative",
    sample_index: sample,
    timestamp: timestamp++,
    frame_id: null,
    hand_count: 0,
    hand: null,
    landmarks: null,
    validity_reason: "paused_before_sample",
  }});
}}
const collection = makeCollection({{
  participantId,
  trainConditions: "synthetic interoperability fixture, not participant evidence",
  validationConditions: "synthetic interoperability fixture, not participant evidence",
  recordedAt: "2026-10-08T10:50:00.000Z",
  sessionStartedAt: started,
  records,
}});
const zip = makeStoredZip({{ "collection.json": JSON.stringify(collection) }});
readOwnCollectionZip(zip);
writeFileSync(process.argv[2], zip);
""",
        encoding="utf-8",
    )
    subprocess.run([node, str(script), str(zip_path)], check=True)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "gestureforge.import_participant",
            str(zip_path),
            "--output",
            str(manifest),
        ],
        check=True,
        text=True,
        capture_output=True,
    )
    assert "Imported 25 records (20 valid features), status=partial" in result.stdout
    bundle = load_dataset(manifest)
    assert bundle.features.shape == (20, 60)
    invalid = [record for record in bundle.records if not record.valid]
    assert len(invalid) == 5
    assert {record.validity_reason for record in invalid} == {"paused_before_sample"}
