"""Bounded authoring and explicit stage execution through shell routing reset."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace
from pathlib import Path

from .storage import atomic_write_json, fields, read_json, version
from .viewer import Viewer
from .workspace import Stage, Workspace, validate_workspace, workspace_json


class RunbookEditor:
    def __init__(self, workspace: Workspace) -> None:
        self.workspace = validate_workspace(workspace)

    def _replace(self, stages: list[Stage]) -> Workspace:
        candidate = validate_workspace(replace(self.workspace, stages=tuple(stages)))
        self.workspace = candidate
        return candidate

    def add(self, stage: Stage) -> Workspace:
        return self._replace([*self.workspace.stages, stage])

    def update(self, index: int, stage: Stage) -> Workspace:
        stages = list(self.workspace.stages)
        if not 0 <= index < len(stages):
            raise ValueError('invalid stage index')
        stages[index] = stage
        return self._replace(stages)

    def delete(self, index: int) -> Workspace:
        stages = list(self.workspace.stages)
        if not 0 <= index < len(stages):
            raise ValueError('invalid stage index')
        del stages[index]
        return self._replace(stages)

    def move(self, index: int, destination: int) -> Workspace:
        stages = list(self.workspace.stages)
        if not 0 <= index < len(stages) or not 0 <= destination < len(stages):
            raise ValueError('invalid stage index')
        stages.insert(destination, stages.pop(index))
        return self._replace(stages)


class Runbook:
    """No launch callbacks. reset_routing must call Deston's configure/pause path.

    The shell receives a stage BEFORE it is activated, resets the context, and
    confirms success. A false acknowledgement or exception preserves progress.
    Restoration invokes reset with resume=False and never calls an action.
    """

    def __init__(self, workspace: Workspace, reset_routing: Callable[[Stage | None, bool], bool],
                 viewer: Viewer | None = None) -> None:
        self.workspace = validate_workspace(workspace)
        self.reset_routing = reset_routing
        self.viewer = viewer
        if self.workspace.deck is not None and (viewer is None or viewer.deck != self.workspace.deck):
            raise ValueError('runbook requires the matching viewer')
        self.position = 0
        self.finished = False
        self.paused = True

    @property
    def current_stage(self) -> Stage | None:
        return self.workspace.stages[self.position] if self.workspace.stages else None

    def _change(self, position: int, finished: bool, resume: bool) -> bool:
        stage = self.workspace.stages[position] if self.workspace.stages else None
        if self.reset_routing(stage, resume) is not True:
            raise ValueError('routing reset was not acknowledged; stage preserved')
        self.position, self.finished, self.paused = position, finished, not resume
        if stage and stage.card_id and self.viewer:
            self.viewer.select_card(stage.card_id)
        return True

    def activate(self, *, resume: bool = False) -> bool:
        return self._change(self.position, self.finished, resume)

    def advance(self) -> bool:
        if not self.workspace.stages or self.finished:
            return False
        if self.position == len(self.workspace.stages) - 1:
            return self._change(self.position, True, False)
        return self._change(self.position + 1, False, not self.paused)

    def previous(self) -> bool:
        if not self.workspace.stages:
            return False
        if self.finished:
            return self._change(self.position, False, False)
        if self.position == 0:
            return False
        return self._change(self.position - 1, False, not self.paused)

    def save(self, path: Path) -> None:
        stage = self.current_stage
        atomic_write_json(path, {'schema_version': 1, 'workspace': workspace_json(self.workspace),
                                'stage_id': stage.id if stage else None, 'finished': self.finished,
                                'viewer': self.viewer.state_json() if self.viewer else None})

    def restore(self, path: Path) -> None:
        obj = fields(read_json(path), {'schema_version', 'workspace', 'stage_id', 'finished', 'viewer'})
        version(obj['schema_version'])
        if obj['workspace'] != workspace_json(self.workspace) or type(obj['finished']) is not bool:
            raise ValueError('incompatible session state')
        ids = [stage.id for stage in self.workspace.stages]
        if ids:
            if obj['stage_id'] not in ids:
                raise ValueError('missing saved stage')
            position = ids.index(obj['stage_id'])
            if obj['finished'] and position != len(ids) - 1:
                raise ValueError('only the final stage can be finished')
        else:
            if obj['stage_id'] is not None or obj['finished']:
                raise ValueError('invalid empty runbook state')
            position = 0
        if self.viewer:
            self.viewer.validate_state(obj['viewer'])
        elif obj['viewer'] is not None:
            raise ValueError('unexpected viewer state')
        self._change(position, obj['finished'], False)
        if self.viewer:
            self.viewer.restore_state(obj['viewer'])
