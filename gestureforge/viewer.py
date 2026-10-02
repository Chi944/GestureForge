"""Assignment-compatible viewer with opt-in Studio actions and private progress."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .contracts import Action, ActionType, CommandEvent, validate_identifier
from .storage import atomic_write_json, fields, read_json, sequence, text, version

ASSETS_DIR = Path(__file__).resolve().parent.parent / 'assets'
BUILTIN_DECK_PATH = ASSETS_DIR / 'demo_deck.json'


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


def deck_json(deck: Deck) -> dict[str, object]:
    return {'schema_version': deck.schema_version, 'deck_id': deck.deck_id,
            'title': deck.title, 'cards': [vars(card) for card in deck.cards]}


def parse_deck(raw: object) -> Deck:
    obj = fields(raw, {'schema_version', 'deck_id', 'title', 'cards'})
    version(obj['schema_version'])
    validate_identifier(obj['deck_id'])
    cards = []
    for value in sequence(obj['cards'], 1, 100):
        card = fields(value, {'id', 'title', 'body'})
        validate_identifier(card['id'])
        cards.append(Card(card['id'], text(card['title'], 120), text(card['body'], 8000, empty=True)))
    if len({card.id for card in cards}) != len(cards):
        raise ValueError('duplicate card IDs')
    return Deck(1, obj['deck_id'], text(obj['title'], 120), tuple(cards))


def load_deck(path: Path) -> Deck:
    return parse_deck(read_json(path))


def load_builtin_deck() -> Deck:
    deck = load_deck(BUILTIN_DECK_PATH)
    if len(deck.cards) != 10:
        raise ValueError('assignment demo deck must contain exactly 10 cards')
    return deck


# Retained for callers of the former parser.
_parse_deck = parse_deck


class Viewer:
    def __init__(self, deck: Deck | None = None, *, project_actions: bool = False) -> None:
        self.deck = parse_deck(deck_json(deck or load_builtin_deck()))
        self.position = 0
        self.project_actions = project_actions
        self._bookmarks: set[str] = set()
        self._applied_event_ids: set[str] = set()

    @property
    def current_card(self) -> Card:
        return self.deck.cards[self.position]

    @property
    def bookmarks(self) -> tuple[Card, ...]:
        return tuple(card for card in self.deck.cards if card.id in self._bookmarks)

    def replace_deck(self, deck: Deck) -> None:
        validated = parse_deck(deck_json(deck))
        self.deck = validated
        self.position = 0
        self._bookmarks.clear()
        self._applied_event_ids.clear()

    def next_keyboard(self) -> bool:
        return self.apply_action(Action(ActionType.NEXT))

    def previous_keyboard(self) -> bool:
        return self.apply_action(Action(ActionType.PREVIOUS))

    def bookmark(self) -> bool:
        return self.apply_action(Action(ActionType.BOOKMARK))

    def remove_bookmark(self, card_id: str) -> bool:
        if card_id not in self._bookmarks:
            return False
        self._bookmarks.remove(card_id)
        return True

    def select_card(self, card_id: str) -> None:
        for index, card in enumerate(self.deck.cards):
            if card.id == card_id:
                self.position = index
                return
        raise ValueError('unknown card')

    def apply_action(self, action: Action) -> bool:
        if action.kind == ActionType.NEXT:
            if self.position == len(self.deck.cards) - 1:
                return False
            self.position += 1
            return True
        if action.kind == ActionType.PREVIOUS:
            if self.position == 0:
                return False
            self.position -= 1
            return True
        if action.kind == ActionType.BOOKMARK:
            card_id = self.current_card.id
            if card_id in self._bookmarks:
                return False
            self._bookmarks.add(card_id)
            return True
        raise ValueError('viewer does not handle this action')

    def apply(self, event: CommandEvent) -> bool:
        # Preserve assignment NEXT-only defaults. Studio uses the typed dispatcher.
        if event.event_id in self._applied_event_ids or len(self._applied_event_ids) >= 4096:
            return False
        self._applied_event_ids.add(event.event_id)
        if event.command != 'NEXT' and not self.project_actions:
            return False
        if event.command not in {'NEXT', 'PREVIOUS', 'BOOKMARK'}:
            return False
        return self.apply_action(Action(ActionType(event.command)))

    def state_json(self) -> dict[str, object]:
        return {'schema_version': 1, 'deck_id': self.deck.deck_id,
                'card_ids': [card.id for card in self.deck.cards],
                'card_id': self.current_card.id, 'bookmarks': [card.id for card in self.bookmarks]}

    def validate_state(self, raw: object) -> tuple[int, set[str]]:
        obj = fields(raw, {'schema_version', 'deck_id', 'card_ids', 'card_id', 'bookmarks'})
        version(obj['schema_version'])
        ids = [card.id for card in self.deck.cards]
        if obj['deck_id'] != self.deck.deck_id or obj['card_ids'] != ids or obj['card_id'] not in ids:
            raise ValueError('saved state belongs to a different deck')
        bookmarks = sequence(obj['bookmarks'], 0, len(ids))
        if any(not isinstance(value, str) or value not in ids for value in bookmarks):
            raise ValueError('unknown bookmark')
        if len(set(bookmarks)) != len(bookmarks):
            raise ValueError('duplicate bookmarks')
        return ids.index(obj['card_id']), set(bookmarks)

    def restore_state(self, raw: object) -> None:
        position, bookmarks = self.validate_state(raw)
        self.position, self._bookmarks = position, bookmarks
        self._applied_event_ids.clear()

    def save(self, path: Path) -> None:
        atomic_write_json(path, self.state_json())

    def restore(self, path: Path) -> None:
        self.restore_state(read_json(path))
