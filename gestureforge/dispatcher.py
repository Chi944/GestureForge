"""Single-owner final gate, shared by ALL manual and routed real actions."""
from __future__ import annotations

from collections.abc import Callable
from threading import get_ident
from typing import Protocol

from .contracts import Action, ActionType, RoutingMode, RoutingResult, RoutingSnapshot, validate_identifier
from .runbook import Runbook
from .session_summary import Outcome, SessionSummary
from .shortcuts import Target, TargetKind, TargetRegistry
from .viewer import Viewer


class DispatchFailure(ValueError):
    """A bounded, public recovery message without private target values."""


class Launcher(Protocol):
    def open(self, target: Target, resolved: str) -> None: ...


class Dispatcher:
    def __init__(self, registry: TargetRegistry, launcher: Launcher,
                 current: Callable[[], RoutingSnapshot], active: Callable[[], bool],
                 ready: Callable[[RoutingSnapshot], bool], pause: Callable[[], None],
                 release_capture: Callable[[RoutingSnapshot], bool],
                 viewer: Viewer | None = None, runbook: Runbook | None = None,
                 summary: SessionSummary | None = None) -> None:
        self.registry, self.launcher = registry, launcher
        self.current, self.active, self.ready = current, active, ready
        self.pause, self.release_capture = pause, release_capture
        self.viewer, self.runbook = viewer, runbook
        self.summary = summary or SessionSummary()
        self._owner = get_ident()
        self._seen: set[str] = set()

    def dispatch(self, result: RoutingResult, snapshot: RoutingSnapshot, *, source: str = 'gesture') -> Outcome:
        if get_ident() != self._owner:
            raise RuntimeError('dispatch must run synchronously on the UI owner thread')
        self.summary.ensure_capacity()  # fail BEFORE any real side effect
        action = result.action or result.simulated_action

        def outcome(status: str, reason: str = '') -> Outcome:
            item = Outcome(result.event_id, snapshot.session_id, source, status, action, reason,
                           snapshot.context_id, snapshot.model_version)
            self.summary.record(item)
            return item

        try:
            validate_identifier(result.event_id)
        except ValueError:
            return Outcome('invalid-request', snapshot.session_id, source, 'rejected',
                           reason='invalid request identity')
        if source not in {'gesture', 'manual'}:
            return Outcome(result.event_id, snapshot.session_id, 'manual', 'rejected',
                           reason='invalid request source')
        if snapshot != self.current():
            return outcome('rejected', 'stale context; resume and issue a new request')
        if result.event_id in self._seen:
            return outcome('duplicate', 'event already consumed')
        if len(self._seen) >= 4096:
            return outcome('rejected', 'event limit reached; export and start a new dispatcher/session')
        self._seen.add(result.event_id)  # failures and manual requests are consumed too
        if result.rejection_reason:
            known = {'paused', 'duplicate_event', 'altered_event', 'identity_mismatch',
                     'unissued_event', 'model_mismatch', 'stale_event', 'unmapped_gesture'}
            reason = result.rejection_reason if result.rejection_reason in known else 'invalid request'
            return outcome('rejected', f'routing rejected this request: {reason}')
        if result.action is not None and result.simulated_action is not None:
            return outcome('rejected', 'ambiguous routing result')
        if snapshot.mode != RoutingMode.LIVE:
            if result.action is not None or result.simulated_action is None:
                return outcome('rejected', 'real action is forbidden during simulation')
            return outcome('simulated')
        if result.action is None or result.simulated_action is not None:
            return outcome('rejected', 'LIVE requires a real routed action')
        try:
            if source == 'gesture' and (not self.active() or not self.ready(snapshot)):
                return outcome('rejected', 'paused or readiness check required')
            action = result.action
            if action.kind == ActionType.OPEN_SHORTCUT:
                if action.shortcut_id is None:
                    raise DispatchFailure('Missing shortcut ID; bind a local target.')
                target, resolved = self.registry.resolve(action.shortcut_id)
                self.pause()
                if self.runbook:
                    self.runbook.paused = True
                if target.kind == TargetKind.BUILTIN and target.value == 'camera':
                    if self.release_capture(snapshot) is not True:
                        raise DispatchFailure('Capture shutdown not acknowledged; Camera was not opened. Close competing camera apps, release capture and retry manually.')
                # Pause is synchronous. Camera preparation may re-enter the UI and
                # change context: compare the ENTIRE snapshot before the side effect.
                if snapshot != self.current() or (source == 'gesture' and not self.ready(snapshot)):
                    return outcome('rejected', 'context/readiness changed before launch')
                target, resolved = self.registry.resolve(action.shortcut_id)
                self.launcher.open(target, resolved)
                return outcome('launch_requested')
            if action.kind == ActionType.ADVANCE_STAGE:
                if self.runbook is None:
                    raise DispatchFailure('No runbook is loaded; import a workspace or use Quick Actions.')
                changed = self.runbook.advance()
            else:
                if self.viewer is None:
                    raise DispatchFailure('No deck is loaded; import a deck workspace or use Quick Actions.')
                changed = self.viewer.apply_action(action)
            return outcome('applied' if changed else 'unchanged')
        except Exception as exc:
            # Do not put target paths/URL query strings in session exports.
            code = getattr(exc, 'winerror', None) or getattr(exc, 'errno', None)
            if isinstance(exc, DispatchFailure):
                reason = str(exc)
            elif isinstance(exc, FileNotFoundError):
                reason = 'Target is missing or moved; restore it or rebind the local shortcut, then retry.'
            elif isinstance(exc, PermissionError):
                reason = 'Access denied; check local permissions or choose a permitted target, then retry.'
            elif code in {31, 1155}:
                reason = 'No default application association; set a default app for this file type or open manually.'
            elif isinstance(exc, ValueError):
                reason = 'Invalid or unbound action/target; edit and test the local binding, then retry manually.'
            else:
                reason = f'{type(exc).__name__}' + (f' (OS code {code})' if code else '')
                reason += '; check the local target or shell callback and retry with a new request.'
            return outcome('failed', reason)

    def manual(self, event_id: str, action: Action) -> Outcome:
        snapshot = self.current()
        result = (RoutingResult(event_id, action=action) if snapshot.mode == RoutingMode.LIVE
                  else RoutingResult(event_id, simulated_action=action))
        return self.dispatch(result, snapshot, source='manual')
