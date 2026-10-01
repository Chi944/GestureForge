"""Portable semantic workspaces. Imports have no local bindings or side effects."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .contracts import Action, ActionType, validate_gesture_id, validate_identifier
from .storage import atomic_write_json, fields, read_json, sequence, text, version
from .viewer import Deck, deck_json, parse_deck


@dataclass(frozen=True)
class ShortcutSlot:
    id: str
    label: str


@dataclass(frozen=True)
class Binding:
    gesture_id: str
    action: Action


@dataclass(frozen=True)
class Stage:
    id: str
    title: str
    instructions: str
    card_id: str | None
    bindings: tuple[Binding, ...]
    continue_label: str = 'Continue'


@dataclass(frozen=True)
class Workspace:
    id: str
    title: str
    deck: Deck | None = None
    shortcuts: tuple[ShortcutSlot, ...] = ()
    quick_bindings: tuple[Binding, ...] = ()
    stages: tuple[Stage, ...] = ()


def action_json(action: Action) -> dict[str, object]:
    result: dict[str, object] = {'kind': action.kind.value}
    if action.shortcut_id is not None:
        result['shortcut_id'] = action.shortcut_id
    return result


def parse_action(raw: object) -> Action:
    obj = fields(raw, {'kind'}, {'shortcut_id'})
    try:
        kind = ActionType(obj['kind'])
    except (ValueError, TypeError) as exc:
        raise ValueError('unknown action type') from exc
    return Action(kind, obj.get('shortcut_id'))


def binding_json(binding: Binding) -> dict[str, object]:
    return {'gesture_id': binding.gesture_id, 'action': action_json(binding.action)}


def parse_bindings(raw: object) -> tuple[Binding, ...]:
    bindings = []
    for item in sequence(raw, 0, 3):
        obj = fields(item, {'gesture_id', 'action'})
        validate_gesture_id(obj['gesture_id'])
        bindings.append(Binding(obj['gesture_id'], parse_action(obj['action'])))
    if len({binding.gesture_id for binding in bindings}) != len(bindings):
        raise ValueError('duplicate gesture bindings')
    return tuple(bindings)


def workspace_json(workspace: Workspace) -> dict[str, object]:
    return {'schema_version': 1, 'id': workspace.id, 'title': workspace.title,
            'deck': deck_json(workspace.deck) if workspace.deck is not None else None,
            'shortcuts': [vars(slot) for slot in workspace.shortcuts],
            'quick_bindings': [binding_json(binding) for binding in workspace.quick_bindings],
            'stages': [{'id': stage.id, 'title': stage.title, 'instructions': stage.instructions,
                        'card_id': stage.card_id, 'continue_label': stage.continue_label,
                        'bindings': [binding_json(binding) for binding in stage.bindings]}
                       for stage in workspace.stages]}


def parse_workspace(raw: object) -> Workspace:
    obj = fields(raw, {'schema_version', 'id', 'title', 'deck', 'shortcuts', 'quick_bindings', 'stages'})
    version(obj['schema_version'])
    validate_identifier(obj['id'])
    deck = parse_deck(obj['deck']) if obj['deck'] is not None else None
    slots = []
    for value in sequence(obj['shortcuts'], 0, 12):
        slot = fields(value, {'id', 'label'})
        validate_identifier(slot['id'])
        slots.append(ShortcutSlot(slot['id'], text(slot['label'], 80)))
    if len({slot.id for slot in slots}) != len(slots):
        raise ValueError('duplicate shortcut IDs')
    stages = []
    for value in sequence(obj['stages'], 0, 12):
        stage_obj = fields(value, {'id', 'title', 'instructions', 'card_id', 'bindings', 'continue_label'})
        validate_identifier(stage_obj['id'])
        if stage_obj['card_id'] is not None:
            validate_identifier(stage_obj['card_id'])
        stages.append(Stage(stage_obj['id'], text(stage_obj['title'], 120),
                            text(stage_obj['instructions'], 8000), stage_obj['card_id'],
                            parse_bindings(stage_obj['bindings']), text(stage_obj['continue_label'], 80)))
    if len({stage.id for stage in stages}) != len(stages):
        raise ValueError('duplicate stage IDs')
    quick = parse_bindings(obj['quick_bindings'])
    slot_ids = {slot.id for slot in slots}
    card_ids = {card.id for card in deck.cards} if deck else set()

    def validate_actions(bindings: tuple[Binding, ...], *, quick_actions: bool) -> None:
        for binding in bindings:
            action = binding.action
            if action.kind == ActionType.OPEN_SHORTCUT and action.shortcut_id not in slot_ids:
                raise ValueError('missing semantic shortcut slot')
            if quick_actions and action.kind != ActionType.OPEN_SHORTCUT:
                raise ValueError('Quick Actions can only bind shortcuts')
            if action.kind in {ActionType.NEXT, ActionType.PREVIOUS, ActionType.BOOKMARK} and deck is None:
                raise ValueError('viewer actions require a deck')

    validate_actions(quick, quick_actions=True)
    for stage in stages:
        if stage.card_id is not None and stage.card_id not in card_ids:
            raise ValueError('stage references a missing card')
        validate_actions(stage.bindings, quick_actions=False)
    return Workspace(obj['id'], text(obj['title'], 120), deck, tuple(slots), quick, tuple(stages))


def validate_workspace(workspace: Workspace) -> Workspace:
    return parse_workspace(workspace_json(workspace))


class WorkspaceStore:
    def __init__(self, workspace: Workspace) -> None:
        self.active = validate_workspace(workspace)

    def import_file(self, path: Path) -> Workspace:
        candidate = parse_workspace(read_json(path))
        self.active = candidate
        return candidate

    def export_file(self, path: Path) -> None:
        # This serializer never sees personal profiles or a local target registry.
        atomic_write_json(path, workspace_json(validate_workspace(self.active)))
