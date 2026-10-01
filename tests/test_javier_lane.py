"""Acceptance regressions for Javier's owned model/storage/dispatch components."""
from __future__ import annotations

from dataclasses import replace
import json
from pathlib import Path
from threading import Thread
from typing import Any

import pytest

from gestureforge.contracts import Action, ActionType, RoutingMode, RoutingResult
from gestureforge.dispatcher import Dispatcher
from gestureforge.routing import RoutingSession
from gestureforge.runbook import Runbook, RunbookEditor
from gestureforge.session_summary import SessionSummary, Trial
from gestureforge.shortcuts import Target, TargetKind, TargetRegistry, validate_https, validate_target
from gestureforge.storage import atomic_write_json, decode_json
from gestureforge.viewer import Viewer, deck_json, load_builtin_deck, parse_deck
from gestureforge.workspace import (
    Binding, ShortcutSlot, Stage, Workspace, WorkspaceStore, parse_workspace, workspace_json,
)


def workspace() -> Workspace:
    return Workspace('demo', 'Fictional demo', load_builtin_deck(),
                     (ShortcutSlot('calculator', 'Calculator'),),
                     (Binding('G1', Action(ActionType.OPEN_SHORTCUT, 'calculator')),),
                     (Stage('intro', 'Intro', 'Read this fictional example.', 'card-01',
                            (Binding('G1', Action(ActionType.NEXT)),)),
                      Stage('finish', 'Finish', 'Review the results.', 'card-10', (), 'Finish')))


class FakeOS:
    def __init__(self) -> None:
        self.calls: list[str] = []
        self.error: OSError | None = None

    def open(self, target: Target, resolved: str) -> None:
        if self.error:
            raise self.error
        self.calls.append(target.id)


def dispatcher(mode: RoutingMode = RoutingMode.LIVE, *, ready: bool = True):
    registry = TargetRegistry()
    registry.configure(Target('calculator', 'Calculator', TargetKind.BUILTIN, 'calculator'))
    registry.configure(Target('camera', 'Camera', TargetKind.BUILTIN, 'camera'))
    session = RoutingSession('profile', 'model', 'context', {'G1': Action(ActionType.NEXT)}, mode)
    session.resume()
    os = FakeOS()
    viewer = Viewer(project_actions=True)
    acknowledgements: list[str] = []
    def release(snapshot):
        acknowledgements.append('released')
        return True

    gate = Dispatcher(registry, os, lambda: session.snapshot, lambda: session.state != 'PAUSED',
                      lambda snapshot: ready, session.pause,
                      release, viewer=viewer)
    return gate, session, os, viewer, acknowledgements


@pytest.mark.parametrize('size', [1, 10, 100])
def test_custom_deck_limits(size: int) -> None:
    raw = deck_json(load_builtin_deck())
    raw['cards'] = [{'id': f'c{i}', 'title': '<b>Plain text</b>', 'body': 'text'} for i in range(size)]
    assert len(parse_deck(raw).cards) == size


@pytest.mark.parametrize('change', ['duplicate', 'empty', 'oversize', 'long_id', 'long_title', 'long_body', 'coercion', 'version', 'unknown'])
def test_invalid_deck_keeps_existing(change: str) -> None:
    viewer = Viewer()
    raw = deck_json(viewer.deck)
    cards = raw['cards']
    assert isinstance(cards, list)
    if change == 'duplicate':
        cards[1]['id'] = cards[0]['id']
    elif change == 'empty':
        raw['cards'] = []
    elif change == 'oversize':
        raw['cards'] = [{'id': f'c{i}', 'title': 't', 'body': ''} for i in range(101)]
    elif change in {'long_id', 'long_title', 'long_body'}:
        key, size = {'long_id': ('id', 65), 'long_title': ('title', 121), 'long_body': ('body', 8001)}[change]
        cards[0][key] = 'x' * size
    elif change == 'coercion':
        cards[0]['title'] = 12
    elif change == 'version':
        raw['schema_version'] = True
    else:
        raw['script'] = 'evil'
    with pytest.raises(ValueError):
        viewer.replace_deck(parse_deck(raw))
    assert viewer.position == 0 and len(viewer.deck.cards) == 10


def test_viewer_full_actions_boundaries_and_bookmark_roundtrip(tmp_path: Path) -> None:
    viewer = Viewer(project_actions=True)
    assert not viewer.previous_keyboard()
    assert viewer.bookmark()
    assert not viewer.bookmark()
    for _ in range(9):
        assert viewer.next_keyboard()
    assert not viewer.next_keyboard()
    assert viewer.bookmark()
    path = tmp_path / 'state.json'
    viewer.save(path)
    restored = Viewer(project_actions=True)
    restored.restore(path)
    assert restored.position == 9
    assert [card.id for card in restored.bookmarks] == ['card-01', 'card-10']
    assert restored.remove_bookmark('card-01')
    assert not restored.remove_bookmark('card-01')
    assert restored.previous_keyboard()


@pytest.mark.parametrize('bad', ['json', 'version', 'position', 'bookmark', 'duplicates', 'deck'])
def test_corrupt_viewer_restore_preserves_state(tmp_path: Path, bad: str) -> None:
    viewer = Viewer()
    viewer.next_keyboard()
    viewer.bookmark()
    before = viewer.state_json()
    raw = viewer.state_json()
    if bad == 'version':
        raw['schema_version'] = 2
    elif bad == 'position':
        raw['card_id'] = 'missing'
    elif bad == 'bookmark':
        raw['bookmarks'] = ['missing']
    elif bad == 'duplicates':
        raw['bookmarks'] = ['card-02', 'card-02']
    elif bad == 'deck':
        raw['deck_id'] = 'other'
    path = tmp_path / 'state.json'
    path.write_text('{' if bad == 'json' else json.dumps(raw))
    with pytest.raises(ValueError):
        viewer.restore(path)
    assert viewer.state_json() == before


def test_atomic_failure_leaves_previous_file_and_cleans_temp(tmp_path: Path, monkeypatch) -> None:
    path = tmp_path / 'state.json'
    atomic_write_json(path, {'before': True})
    original = path.read_bytes()

    def fail(*args):
        raise OSError('injected replace failure')

    monkeypatch.setattr('gestureforge.storage.os.replace', fail)
    with pytest.raises(OSError):
        atomic_write_json(path, {'after': True})
    assert path.read_bytes() == original
    assert list(tmp_path.iterdir()) == [path]


@pytest.mark.parametrize('bad', [b'{"x":1,"x":2}', b'{"x":NaN}', b'\xff', b'[' * 2000])
def test_json_rejects_duplicate_keys_invalid_encoding_and_recursion(bad: bytes) -> None:
    with pytest.raises(ValueError):
        decode_json(bad)


def test_workspace_roundtrip_and_export_privacy(tmp_path: Path) -> None:
    original = workspace()
    store = WorkspaceStore(original)
    path = tmp_path / 'workspace.json'
    store.export_file(path)
    assert WorkspaceStore(Workspace('empty', 'Quick only')).import_file(path) == original
    data = path.read_text()
    for private in ['value', 'trusted', 'https://', 'password', '"profiles"', '"samples"', 'C:\\']:
        assert private not in data


@pytest.mark.parametrize('bad', ['version', 'unknown_action', 'missing_shortcut', 'missing_card', 'duplicate_stage', 'duplicate_slot', 'duplicate_gesture', 'credentials', 'target', 'script', 'slots', 'stages', 'continue', 'quick_viewer'])
def test_invalid_workspace_is_transactional(tmp_path: Path, bad: str) -> None:
    original = workspace()
    store = WorkspaceStore(original)
    raw: Any = workspace_json(original)
    if bad == 'version':
        raw['schema_version'] = 2
    elif bad == 'unknown_action':
        raw['stages'][0]['bindings'][0]['action']['kind'] = 'SHELL'
    elif bad == 'missing_shortcut':
        raw['quick_bindings'][0]['action']['shortcut_id'] = 'missing'
    elif bad == 'missing_card':
        raw['stages'][0]['card_id'] = 'missing'
    elif bad == 'duplicate_stage':
        raw['stages'][1]['id'] = 'intro'
    elif bad == 'duplicate_slot':
        raw['shortcuts'].append(raw['shortcuts'][0])
    elif bad == 'duplicate_gesture':
        raw['stages'][0]['bindings'] *= 2
    elif bad == 'credentials':
        raw['password'] = 'secret'
    elif bad == 'target':
        raw['shortcuts'][0]['value'] = 'C:\\sensitive.txt'
    elif bad == 'script':
        raw['stages'][0]['script'] = 'run()'
    elif bad == 'slots':
        raw['quick_bindings'] *= 4
    elif bad == 'stages':
        raw['stages'] *= 7
    elif bad == 'continue':
        raw['stages'][0]['continue_label'] = ''
    else:
        raw['quick_bindings'][0]['action'] = {'kind': 'NEXT'}
    path = tmp_path / 'invalid.json'
    path.write_text(json.dumps(raw))
    with pytest.raises(ValueError):
        store.import_file(path)
    assert store.active == original


def test_workspace_rejects_oversized_input_and_empty_quick_only_works(tmp_path: Path) -> None:
    empty = Workspace('quick-only', 'Quick Actions')
    assert parse_workspace(workspace_json(empty)) == empty
    store = WorkspaceStore(empty)
    path = tmp_path / 'huge.json'
    path.write_bytes(b' ' * (1024 * 1024 + 1))
    with pytest.raises(ValueError):
        store.import_file(path)
    assert store.active == empty


def test_runbook_editor_create_update_reorder_delete() -> None:
    editor = RunbookEditor(workspace())
    extra = Stage('extra', 'Extra', 'Read and continue.', None, ())
    editor.add(extra)
    editor.move(2, 0)
    assert editor.workspace.stages[0] == extra
    editor.update(0, replace(extra, title='Changed'))
    editor.delete(0)
    assert editor.workspace == workspace()
    with pytest.raises(ValueError):
        editor.add(editor.workspace.stages[0])
    assert editor.workspace == workspace()


def test_runbook_routes_stage_change_no_wrap_and_restore_paused(tmp_path: Path) -> None:
    ws = workspace()
    viewer = Viewer(ws.deck)
    session = RoutingSession('profile', 'model', 'intro', {'G1': Action(ActionType.NEXT)})
    session.resume()

    def reset(stage, resume):
        session.configure('profile', 'model', stage.id, {'G1': Action(ActionType.NEXT)})
        if resume:
            session.resume()
        return True

    runbook = Runbook(ws, reset, viewer)
    initial = session.snapshot
    runbook.activate(resume=True)
    assert runbook.advance()
    assert session.snapshot != initial and session.state == 'WAIT_NEUTRAL'
    assert viewer.current_card.id == 'card-10'
    path = tmp_path / 'session.json'
    viewer.bookmark()
    runbook.save(path)
    runbook.previous()
    runbook.restore(path)
    assert runbook.position == 1 and runbook.paused and session.state == 'PAUSED'
    assert viewer.current_card.id == 'card-10' and len(viewer.bookmarks) == 1
    assert runbook.advance() and runbook.finished
    assert not runbook.advance()
    assert runbook.previous() and not runbook.finished


def test_runbook_reset_failure_preserves_stage() -> None:
    ws = workspace()
    runbook = Runbook(ws, lambda stage, resume: False, Viewer(ws.deck))
    with pytest.raises(ValueError):
        runbook.advance()
    assert runbook.position == 0


def test_runbook_corrupt_restore_preserves_stage_and_viewer(tmp_path: Path) -> None:
    ws = workspace()
    viewer = Viewer(ws.deck)
    resets: list[str] = []
    def reset(stage, resume):
        assert stage is not None
        resets.append(stage.id)
        return True
    runbook = Runbook(ws, reset, viewer)
    path = tmp_path / 'session.json'
    runbook.save(path)
    raw = json.loads(path.read_text())
    raw['viewer']['bookmarks'] = ['missing']
    path.write_text(json.dumps(raw))
    with pytest.raises(ValueError):
        runbook.restore(path)
    assert runbook.position == 0 and viewer.position == 0 and resets == []


@pytest.mark.parametrize('url', ['http://example.com', 'file:///tmp/a', 'javascript:alert(1)', 'https://',
                                  'https://name:pass@example.com', 'https://@example.com',
                                  'https://example.com:99999', 'https://bad host.com',
                                  'https://example.com\n', 'https://example.com\\evil',
                                  'https://.example.com', 'https://example.com/' + 'x' * 2048])
def test_invalid_https(url: str) -> None:
    with pytest.raises(ValueError):
        validate_https(url)


@pytest.mark.parametrize('url', ['https://example.com', 'https://example.com:443/path?q=1#x', 'https://[::1]/'])
def test_valid_https(url: str) -> None:
    assert validate_https(url) == url


@pytest.mark.parametrize('name', ['cmd.exe', 'powershell.exe', 'python.exe', 'python3.11.exe',
                                   'powershell_ise.exe', 'node.exe', 'wscript.exe', 'rundll32.exe',
                                   'test.bat', 'test.lnk'])
def test_shell_interpreter_script_apps_rejected(tmp_path: Path, name: str) -> None:
    path = tmp_path / name
    path.write_text('fake fixture only')
    with pytest.raises(ValueError):
        validate_target(Target('app', 'App', TargetKind.APP, str(path), True))


@pytest.mark.parametrize('value', ['\\\\server\\share\\file.txt', '//server/share/file.txt',
                                    '\\\\?\\C:\\file.txt', '\\\\.\\device', 'C:file.txt',
                                    'C:\\file.txt:stream', 'file:///a', 'relative.txt'])
def test_remote_device_relative_paths_rejected(value: str) -> None:
    with pytest.raises(ValueError):
        validate_target(Target('file', 'File', TargetKind.FILE, value))


@pytest.mark.parametrize('suffix', ['.pdf', '.txt', '.png', '.jpg', '.jpeg'])
def test_allowed_reference_files(tmp_path: Path, suffix: str) -> None:
    path = tmp_path / f'file{suffix}'
    path.write_text('fixture')
    assert validate_target(Target('file', 'File', TargetKind.FILE, str(path))) == str(path)


@pytest.mark.parametrize('suffix', ['.exe', '.cmd', '.py', '.lnk', '.url', '.svg', '.docx'])
def test_disallowed_reference_files(tmp_path: Path, suffix: str) -> None:
    path = tmp_path / f'file{suffix}'
    path.write_text('fixture')
    with pytest.raises(ValueError):
        validate_target(Target('file', 'File', TargetKind.FILE, str(path)))


def test_untrusted_app_rejected_and_symlink_to_disallowed_file(tmp_path: Path) -> None:
    exe = tmp_path / 'editor.exe'
    exe.write_text('fixture')
    with pytest.raises(ValueError):
        validate_target(Target('app', 'App', TargetKind.APP, str(exe)))
    link = tmp_path / 'file.txt'
    try:
        link.symlink_to(exe)
    except OSError:
        pytest.skip('symlinks not permitted on this host')
    with pytest.raises(ValueError):
        validate_target(Target('file', 'File', TargetKind.FILE, str(link)))


def test_registry_twelve_targets_three_slots_and_independent_rebinding(tmp_path: Path) -> None:
    registry = TargetRegistry()
    for index in range(12):
        registry.configure(Target(f't{index}', f'Target {index}', TargetKind.BUILTIN, 'calculator'))
    with pytest.raises(ValueError):
        registry.configure(Target('overflow', 'Overflow', TargetKind.BUILTIN, 'calculator'))
    registry.bind_quick(('t1', 't2', 't3'))
    path = tmp_path / 'registry.json'
    registry.save(path)
    other = TargetRegistry()
    other.restore(path)
    other.configure(Target('t1', 'Different machine', TargetKind.BUILTIN, 'camera'))
    assert other.get('t1') != registry.get('t1')
    assert other.quick_slots == registry.quick_slots
    other.remove('t1')
    assert other.quick_slots == (None, 't2', 't3')


def test_registry_missing_target_after_configuration_and_restore_without_launch(tmp_path: Path) -> None:
    path = tmp_path / 'reference.txt'
    path.write_text('fixture')
    registry = TargetRegistry()
    registry.configure(Target('ref', 'Reference', TargetKind.FILE, str(path)))
    state = tmp_path / 'registry.json'
    registry.save(state)
    path.unlink()
    restored = TargetRegistry()
    restored.restore(state)
    assert restored.get('ref').label == 'Reference'
    with pytest.raises(OSError):
        restored.resolve('ref')


def test_dispatch_all_real_actions_share_once_gate_even_manual() -> None:
    gate, session, os, viewer, _ = dispatcher()
    snapshot = session.snapshot
    assert gate.manual('same', Action(ActionType.NEXT)).status == 'applied'
    assert gate.dispatch(RoutingResult('same', action=Action(ActionType.OPEN_SHORTCUT, 'calculator')), snapshot).status == 'duplicate'
    assert viewer.position == 1 and os.calls == []


@pytest.mark.parametrize('mode', [RoutingMode.PREVIEW, RoutingMode.REHEARSAL])
def test_simulation_cannot_open_or_move_or_pause(mode: RoutingMode) -> None:
    gate, session, os, viewer, acknowledgements = dispatcher(mode)
    action = Action(ActionType.OPEN_SHORTCUT, 'camera')
    assert gate.manual('manual', action).status == 'simulated'
    assert gate.dispatch(RoutingResult('real', action=action), session.snapshot).status == 'rejected'
    assert gate.manual('viewer', Action(ActionType.NEXT)).status == 'simulated'
    assert os.calls == [] and viewer.position == 0 and acknowledgements == []
    assert session.state != 'PAUSED'


def test_readiness_gate_and_manual_fallback() -> None:
    gate, session, os, viewer, _ = dispatcher(ready=False)
    action = Action(ActionType.NEXT)
    assert gate.dispatch(RoutingResult('gesture', action=action), session.snapshot).status == 'rejected'
    session.pause()
    assert gate.manual('manual', action).status == 'applied'
    assert viewer.position == 1


def test_camera_release_ack_and_context_change_before_os_side_effect() -> None:
    gate, session, os, _, acknowledgements = dispatcher()
    assert gate.manual('camera1', Action(ActionType.OPEN_SHORTCUT, 'camera')).status == 'launch_requested'
    assert os.calls == ['camera'] and acknowledgements == ['released'] and session.state == 'PAUSED'
    gate.release_capture = lambda snapshot: False
    assert gate.manual('camera2', Action(ActionType.OPEN_SHORTCUT, 'camera')).status == 'failed'
    assert os.calls == ['camera']

    def change(snapshot):
        session.configure('profile', 'model-v2', 'other', {'G1': Action(ActionType.NEXT)}, RoutingMode.LIVE)
        return True

    gate.release_capture = change
    assert gate.manual('camera3', Action(ActionType.OPEN_SHORTCUT, 'camera')).status == 'rejected'
    assert os.calls == ['camera']


def test_target_revalidated_after_capture_shutdown(tmp_path: Path) -> None:
    gate, session, os, _, _ = dispatcher()
    def remove(snapshot):
        gate.registry.remove('camera')
        return True
    gate.release_capture = remove
    assert gate.manual('camera', Action(ActionType.OPEN_SHORTCUT, 'camera')).status == 'failed'
    assert os.calls == []


def test_association_failure_not_completion_not_retryable_with_same_event() -> None:
    gate, session, os, viewer, _ = dispatcher()
    os.error = OSError(1155, 'no association (sensitive target path)')
    action = Action(ActionType.OPEN_SHORTCUT, 'calculator')
    assert gate.manual('test1', action).status == 'failed'
    os.error = None
    assert gate.manual('test1', action).status == 'duplicate'
    assert gate.manual('test2', action).status == 'launch_requested'
    assert gate.summary.counts()['acknowledged_completion'] == 0
    assert all('sensitive' not in item.reason for item in gate.summary.outcomes)


def test_stale_snapshot_and_dedup_generation_and_owner_thread() -> None:
    gate, session, os, viewer, _ = dispatcher()
    old = session.snapshot
    assert gate.manual('e1', Action(ActionType.NEXT)).status == 'applied'
    session.resume()
    assert gate.dispatch(RoutingResult('old', action=Action(ActionType.NEXT)), old).status == 'rejected'
    assert gate.manual('e1', Action(ActionType.NEXT)).status == 'duplicate'
    errors: list[str] = []
    def wrong_thread():
        try:
            gate.manual('thread', Action(ActionType.NEXT))
        except RuntimeError as exc:
            errors.append(str(exc))
    thread = Thread(target=wrong_thread)
    thread.start()
    thread.join()
    assert len(errors) == 1 and viewer.position == 1


@pytest.mark.parametrize('changed', ['context', 'pause'])
def test_readiness_context_change_blocks_viewer_side_effect(changed: str) -> None:
    gate, session, os, viewer, _ = dispatcher()
    snapshot = session.snapshot

    def change(snapshot):
        if changed == 'context':
            session.configure('profile', 'model', 'other', {'G1': Action(ActionType.PREVIOUS)}, RoutingMode.LIVE)
        else:
            session.pause()
        return True

    gate.ready = change
    outcome = gate.dispatch(RoutingResult('stale-viewer', action=Action(ActionType.NEXT)), snapshot)
    assert outcome.status == 'rejected' and 'readiness changed' in outcome.reason
    assert viewer.position == 0 and os.calls == []


def test_post_camera_readiness_context_change_blocks_launch() -> None:
    gate, session, os, _, acknowledgements = dispatcher()
    calls = 0

    def change_on_second_ready(snapshot):
        nonlocal calls
        calls += 1
        if calls == 2:
            session.configure('profile', 'model', 'other', {'G1': Action(ActionType.NEXT)}, RoutingMode.LIVE)
        return True

    gate.ready = change_on_second_ready
    outcome = gate.dispatch(
        RoutingResult('stale-launch', action=Action(ActionType.OPEN_SHORTCUT, 'camera')),
        session.snapshot,
    )
    assert outcome.status == 'rejected' and 'before launch' in outcome.reason
    assert os.calls == [] and acknowledgements == ['released']


def test_failed_launch_preserves_runbook_stage() -> None:
    gate, session, os, viewer, _ = dispatcher()
    gate.runbook = Runbook(workspace(), lambda stage, resume: True, viewer)
    os.error = OSError('unavailable')
    assert gate.manual('launch', Action(ActionType.OPEN_SHORTCUT, 'calculator')).status == 'failed'
    assert gate.runbook.position == 0 and not gate.runbook.finished


def test_summary_counts_are_measured_and_completion_explicit(tmp_path: Path) -> None:
    gate, _, _, _, _ = dispatcher(RoutingMode.REHEARSAL)
    summary = gate.summary
    summary.record_trial(Trial('correct', 'G1', 'G1'))
    summary.record_trial(Trial('wrong', 'G1', 'G2'))
    summary.record_trial(Trial('missed', 'G1', None, True))
    gate.manual('simulation', Action(ActionType.OPEN_SHORTCUT, 'calculator'))
    summary.acknowledge_completion('intro')
    summary.acknowledge_completion('intro')
    summary.retry()
    counts = summary.counts()
    assert [counts[key] for key in ['correct', 'wrong', 'missed', 'tracking_lost', 'simulated', 'acknowledged_completion', 'retries']] == [1] * 7
    path = tmp_path / 'summary.json'
    summary.export(path)
    assert json.loads(path.read_text())['counts'] == counts
    with pytest.raises(ValueError):
        summary.record_trial(Trial('correct', 'G1', 'G1'))
    assert SessionSummary().counts()['correct'] == 0


def test_duplicate_gate_survives_stage_context_changes_and_is_bounded() -> None:
    gate, session, os, viewer, _ = dispatcher()
    assert gate.manual('once', Action(ActionType.NEXT)).status == 'applied'
    session.configure('profile', 'model', 'new-stage', {'G1': Action(ActionType.NEXT)}, RoutingMode.LIVE)
    assert gate.manual('once', Action(ActionType.OPEN_SHORTCUT, 'calculator')).status == 'duplicate'
    gate._seen = {str(index) for index in range(4096)}
    assert gate.manual('limit', Action(ActionType.NEXT)).status == 'rejected'
    assert viewer.position == 1 and not os.calls


def test_callback_failure_is_consumed_before_retry() -> None:
    gate, _, os, _, _ = dispatcher()
    def fail():
        raise RuntimeError('private target details from an integration error')
    gate.pause = fail
    action = Action(ActionType.OPEN_SHORTCUT, 'calculator')
    outcome = gate.manual('same', action)
    assert outcome.status == 'failed' and 'private' not in outcome.reason
    assert gate.manual('same', action).status == 'duplicate' and not os.calls


def test_unknown_prediction_counts_as_measured_miss() -> None:
    summary = SessionSummary()
    summary.record_trial(Trial('unknown', 'G1', 'UNKNOWN'))
    assert summary.counts()['missed'] == 1 and summary.counts()['wrong'] == 0


def test_windows_adapter_uses_fixed_builtin_targets_and_safe_native_request(monkeypatch) -> None:
    from types import SimpleNamespace
    from gestureforge import shortcuts
    calls = []
    def system_directory(buffer, size):
        buffer.value = '/Windows/System32'
        return len(buffer.value)
    monkeypatch.setattr(shortcuts, 'os', SimpleNamespace(name='nt', startfile=lambda *args: calls.append(args)))
    monkeypatch.setattr(shortcuts.ctypes, 'windll', SimpleNamespace(kernel32=SimpleNamespace(GetSystemDirectoryW=system_directory)), raising=False)
    launcher = shortcuts.WindowsLauncher()
    launcher.open(Target('calc', 'Calculator', TargetKind.BUILTIN, 'calculator'), 'ignored')
    launcher.open(Target('cam', 'Camera', TargetKind.BUILTIN, 'camera'), 'ignored')
    assert calls == [(str(Path('/Windows/System32') / 'calc.exe'), 'open'), ('microsoft.windows.camera:', 'open')]


def test_project_viewer_event_bookmarks_and_previous_are_idempotent() -> None:
    from gestureforge.contracts import CommandEvent
    viewer = Viewer(project_actions=True)
    def event(id, command):
        return CommandEvent(id, 'session', 'profile', 1, command, 1.0)
    assert viewer.apply(event('bookmark', 'BOOKMARK'))
    assert not viewer.apply(event('bookmark', 'BOOKMARK'))
    assert viewer.apply(event('next', 'NEXT'))
    assert viewer.apply(event('previous', 'PREVIOUS'))
    assert not viewer.apply(event('previous', 'PREVIOUS'))
    assert viewer.position == 0 and len(viewer.bookmarks) == 1


@pytest.mark.parametrize('bad', ['json', 'unknown', 'duplicates', 'slots', 'oversized'])
def test_registry_corrupt_restore_keeps_valid_active_bindings(tmp_path: Path, bad: str) -> None:
    registry = TargetRegistry()
    registry.configure(Target('calculator', 'Calculator', TargetKind.BUILTIN, 'calculator'))
    registry.bind_quick(('calculator', None, None))
    path = tmp_path / 'targets.json'
    registry.save(path)
    raw = json.loads(path.read_text())
    if bad == 'unknown':
        raw['targets'][0]['arguments'] = ['unsafe']
    elif bad == 'duplicates':
        raw['targets'] *= 2
    elif bad == 'slots':
        raw['quick_slots'][0] = 'missing'
    path.write_text('{' if bad == 'json' else ' ' * (1024 * 1024 + 1) if bad == 'oversized' else json.dumps(raw))
    with pytest.raises(ValueError):
        registry.restore(path)
    assert len(registry.targets) == 1 and registry.quick_slots == ('calculator', None, None)


def test_mapped_network_drive_is_rejected_at_native_configuration(tmp_path: Path, monkeypatch) -> None:
    from types import SimpleNamespace
    from gestureforge import shortcuts
    path = tmp_path / 'reference.txt'
    path.write_text('fixture')
    monkeypatch.setattr(shortcuts, 'os', SimpleNamespace(name='nt'))
    monkeypatch.setattr(shortcuts.ctypes, 'windll', SimpleNamespace(kernel32=SimpleNamespace(GetDriveTypeW=lambda root: 4)), raising=False)
    with pytest.raises(ValueError, match='local drive'):
        validate_target(Target('ref', 'Reference', TargetKind.FILE, str(path)))


def test_dispatcher_record_limit_blocks_side_effect_before_os_call() -> None:
    gate, session, os, viewer, _ = dispatcher()
    outcome = gate.manual('initial', Action(ActionType.NEXT))
    gate.summary.outcomes = [outcome] * 10000
    with pytest.raises(ValueError, match='record limit'):
        gate.manual('over-limit', Action(ActionType.OPEN_SHORTCUT, 'calculator'))
    assert not os.calls


def test_no_launch_replay_on_runbook_restore(tmp_path: Path) -> None:
    gate, session, os, viewer, _ = dispatcher()
    gate.runbook = Runbook(workspace(), lambda stage, resume: not session.pause(), viewer)
    assert gate.manual('calculator', Action(ActionType.OPEN_SHORTCUT, 'calculator')).status == 'launch_requested'
    path = tmp_path / 'progress.json'
    gate.runbook.save(path)
    gate.runbook.restore(path)
    assert os.calls == ['calculator'] and gate.runbook.paused and session.state == 'PAUSED'


def test_launch_failure_has_specific_missing_and_association_recovery_messages() -> None:
    gate, _, os, _, _ = dispatcher()
    action = Action(ActionType.OPEN_SHORTCUT, 'calculator')
    os.error = FileNotFoundError('sensitive path')
    missing = gate.manual('missing', action)
    assert missing.status == 'failed' and 'missing or moved' in missing.reason
    os.error = OSError(1155, 'sensitive association target')
    association = gate.manual('association', action)
    assert 'default application association' in association.reason
    assert 'sensitive' not in missing.reason + association.reason
