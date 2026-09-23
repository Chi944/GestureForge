"""Fixed assignment deck viewer."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .contracts import CommandEvent

ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets"
BUILTIN_DECK_PATH = ASSETS_DIR / "demo_deck.json"


@dataclass(frozen=True)
class Card:
    id: str
    title: str
    body: str


@dataclass(frozen=True)
class Deck:
    schema_version: int
    deck_id: str
    title: str
    cards: tuple[Card, ...]


def load_builtin_deck() -> Deck:
    with BUILTIN_DECK_PATH.open("r", encoding="utf-8") as deck_file:
        raw = json.load(deck_file)
    return _parse_deck(raw)


class Viewer:
    """Minimal one-way card viewer for the assignment prototype."""

    def __init__(self, deck: Deck | None = None) -> None:
        self.deck = deck or load_builtin_deck()
        self.position = 0
        self._applied_event_ids: set[str] = set()

    @property
    def current_card(self) -> Card:
        return self.deck.cards[self.position]

    def next_keyboard(self) -> bool:
        return self._advance()

    def apply(self, event: CommandEvent) -> bool:
        if event.event_id in self._applied_event_ids:
            return False
        self._applied_event_ids.add(event.event_id)
        if event.command != "NEXT":
            return False
        return self._advance()

    def _advance(self) -> bool:
        if self.position >= len(self.deck.cards) - 1:
            return False
        self.position += 1
        return True


def _parse_deck(raw: dict[str, Any]) -> Deck:
    cards = tuple(Card(id=str(card["id"]), title=str(card["title"]), body=str(card["body"])) for card in raw["cards"])
    if len(cards) != 10:
        raise ValueError("assignment demo deck must contain exactly 10 cards")
    if len({card.id for card in cards}) != len(cards):
        raise ValueError("assignment demo deck contains duplicate card IDs")
    return Deck(
        schema_version=int(raw["schema_version"]),
        deck_id=str(raw["deck_id"]),
        title=str(raw["title"]),
        cards=cards,
    )
