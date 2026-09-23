"""Versioned records shared by collection, inference and the application."""

from dataclasses import dataclass

LABELS = ("NEXT", "PREVIOUS", "BOOKMARK", "NEUTRAL")
FEATURE_VERSION = 1
SCHEMA_VERSION = 1


@dataclass(frozen=True)
class Observation:
    session_id: str
    profile_id: str
    frame_id: int
    timestamp: float
    hand_count: int
    handedness: str | None
    landmarks: object | None
    validity_reason: str = ""


@dataclass(frozen=True)
class Prediction:
    session_id: str
    profile_id: str
    frame_id: int
    timestamp: float
    label: str
    accepted: bool
    model_version: str = "prototype-v1"
    rejection_reason: str = ""


@dataclass(frozen=True)
class CommandEvent:
    event_id: str
    session_id: str
    profile_id: str
    frame_id: int
    command: str
    timestamp: float
    resulting_position: int | None = None
