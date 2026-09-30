"""Versioned gesture identities, independent of display names and actions."""

from dataclasses import dataclass
from typing import Any

from .contracts import LABELS, validate_gesture_id


@dataclass(frozen=True)
class GestureVocabulary:
    action_ids: tuple[str, ...]
    version: int = 1

    def __post_init__(self) -> None:
        if type(self.version) is not int or self.version != 1:
            raise ValueError("unsupported vocabulary version")
        if not isinstance(self.action_ids, tuple) or len(self.action_ids) != 3:
            raise ValueError("vocabulary requires exactly three action IDs")
        for label in self.action_ids:
            validate_gesture_id(label)
        if len(set(self.action_ids)) != 3:
            raise ValueError("action IDs must be unique")

    @property
    def labels(self) -> tuple[str, ...]:
        return (*self.action_ids, "NEUTRAL")

    def to_dict(self) -> dict[str, Any]:
        return {"version": self.version, "action_ids": list(self.action_ids)}

    @classmethod
    def from_mapping(cls, value: Any) -> "GestureVocabulary":
        if not isinstance(value, dict) or set(value) != {"version", "action_ids"}:
            raise ValueError("invalid vocabulary object")
        if not isinstance(value["action_ids"], list):
            raise ValueError("action_ids must be an array")
        return cls(tuple(value["action_ids"]), value["version"])


LEGACY_VOCABULARY = GestureVocabulary(tuple(label for label in LABELS if label != "NEUTRAL"))
