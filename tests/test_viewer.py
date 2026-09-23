from gestureforge.contracts import CommandEvent
from gestureforge.viewer import Viewer, load_builtin_deck


def event(event_id: str, command: str = "NEXT") -> CommandEvent:
    return CommandEvent(
        event_id=event_id,
        session_id="s1",
        profile_id="pilot",
        frame_id=1,
        command=command,
        timestamp=1.0,
    )


def test_builtin_deck_has_ten_cards_and_starts_at_first_card() -> None:
    deck = load_builtin_deck()
    viewer = Viewer(deck)

    assert len(deck.cards) == 10
    assert viewer.position == 0
    assert viewer.current_card.id == "card-01"


def test_next_keyboard_advances_without_wrapping() -> None:
    viewer = Viewer()

    for _ in range(9):
        assert viewer.next_keyboard() is True

    assert viewer.position == 9
    assert viewer.current_card.id == "card-10"
    assert viewer.next_keyboard() is False
    assert viewer.position == 9


def test_apply_executes_each_next_event_once() -> None:
    viewer = Viewer()

    assert viewer.apply(event("e1")) is True
    assert viewer.position == 1
    assert viewer.apply(event("e1")) is False
    assert viewer.position == 1


def test_preview_commands_do_not_move_deck() -> None:
    viewer = Viewer()

    assert viewer.apply(event("e1", "PREVIOUS")) is False
    assert viewer.apply(event("e2", "BOOKMARK")) is False
    assert viewer.position == 0
