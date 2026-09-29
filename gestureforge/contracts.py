"""Versioned records shared by collection, inference and the application."""

from dataclasses import dataclass
from enum import Enum
import re

LABELS = ("NEXT", "PREVIOUS", "BOOKMARK", "NEUTRAL")
FEATURE_VERSION = 1
SCHEMA_VERSION = 1
# Project routing contracts; independent of the legacy dataset/feature schemas.
PROJECT_CONTRACT_VERSION = 1


def validate_identifier(value: str) -> None:
    """Validate a bounded opaque ID, never a path or executable target."""
    if not isinstance(value, str) or re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,63}", value) is None:
        raise ValueError("IDs must be 1-64 ASCII letters, digits, underscores, dots, colons or hyphens")


def validate_gesture_id(value: str) -> None:
    """Action gesture IDs are canonical uppercase; NEUTRAL/UNKNOWN are reserved."""
    if (
        not isinstance(value, str)
        or re.fullmatch(r"[A-Z][A-Z0-9_]{0,63}", value) is None
        or value in {"NEUTRAL", "UNKNOWN"}
    ):
        raise ValueError("action gesture IDs must be uppercase ASCII IDs excluding NEUTRAL/UNKNOWN")


class ActionType(str, Enum):
    NEXT = "NEXT"
    PREVIOUS = "PREVIOUS"
    BOOKMARK = "BOOKMARK"
    ADVANCE_STAGE = "ADVANCE_STAGE"
    OPEN_SHORTCUT = "OPEN_SHORTCUT"


class RoutingMode(str, Enum):
    PREVIEW = "PREVIEW"
    REHEARSAL = "REHEARSAL"
    LIVE = "LIVE"


@dataclass(frozen=True)
class Action:
    """One semantic action; shortcuts refer to local IDs, never target paths."""

    kind: ActionType
    shortcut_id: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.kind, ActionType):
            raise ValueError("kind must be an ActionType")
        if self.kind == ActionType.OPEN_SHORTCUT:
            if self.shortcut_id is None:
                raise ValueError("OPEN_SHORTCUT requires shortcut_id")
            validate_identifier(self.shortcut_id)
        elif self.shortcut_id is not None:
            raise ValueError("only OPEN_SHORTCUT accepts shortcut_id")


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
    model_version: str = "prototype-v1"


@dataclass(frozen=True)
class RoutingSnapshot:
    """A single immutable routing generation, detached from mutable caller maps."""

    session_id: str
    profile_id: str
    model_version: str
    context_id: str
    bindings: tuple[tuple[str, Action], ...]
    mode: RoutingMode = RoutingMode.PREVIEW

    def __post_init__(self) -> None:
        for value in (self.session_id, self.profile_id, self.model_version, self.context_id):
            validate_identifier(value)
        if not isinstance(self.mode, RoutingMode):
            raise ValueError("mode must be a RoutingMode")
        bindings = tuple((gesture_id, action) for gesture_id, action in self.bindings)
        if not 1 <= len(bindings) <= 3:
            raise ValueError("a context requires one to three gesture bindings")
        seen: set[str] = set()
        for gesture_id, action in bindings:
            validate_gesture_id(gesture_id)
            if gesture_id in seen or not isinstance(action, Action):
                raise ValueError("bindings require unique gesture IDs and typed actions")
            seen.add(gesture_id)
        object.__setattr__(self, "bindings", bindings)


@dataclass(frozen=True)
class RoutingResult:
    event_id: str
    action: Action | None = None
    simulated_action: Action | None = None
    rejection_reason: str = ""
