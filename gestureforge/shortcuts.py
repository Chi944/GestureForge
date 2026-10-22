"""Local-only targets and argument-safe Windows opening adapters."""
from __future__ import annotations

import ctypes
from dataclasses import dataclass
from enum import Enum
import ipaddress
import os
from pathlib import Path, PureWindowsPath
import re
from urllib.parse import urlsplit

from .contracts import validate_identifier
from .storage import atomic_write_json, fields, read_json, sequence, text, version


class TargetKind(str, Enum):
    BUILTIN = 'builtin'
    APP = 'app'
    FILE = 'file'
    FOLDER = 'folder'
    WEBSITE = 'website'


@dataclass(frozen=True)
class Target:
    id: str
    label: str
    kind: TargetKind
    value: str
    trusted: bool = False


# Selection is an explicit trust decision, not a malware sandbox. Known launchers
# and interpreters are excluded, including versioned Python names.
DENIED_APPS = frozenset({
    'cmd', 'powershell', 'powershell_ise', 'pwsh', 'wscript', 'cscript', 'mshta', 'rundll32', 'regsvr32',
    'bash', 'sh', 'wsl', 'node', 'nodejs', 'ruby', 'perl', 'java', 'javaw', 'php',
    'msiexec', 'reg', 'schtasks', 'wmic', 'conhost', 'wt', 'hh', 'installutil', 'msbuild',
    'py', 'pyw', 'pypy', 'pypyw',
})
FILE_TYPES = frozenset({'.pdf', '.txt', '.png', '.jpg', '.jpeg'})


def _local_path(value: str) -> Path:
    value = text(value, 4096)
    windows = PureWindowsPath(value)
    if (value.startswith(('\\\\', '//', '\\', '/dev/', '/proc/', '/sys/'))
            or '\x00' in value or '://' in value
            or windows.drive.startswith('\\') or value.startswith(('\\?', '\\.'))):
        raise ValueError('network/device paths are not permitted')
    # Reject alternate data streams and drive-relative paths. Absolute POSIX paths
    # are useful only to exercise fake adapters on the development host.
    if ':' in value and (not re.match(r'^[A-Za-z]:[\\/]', value) or ':' in value[2:]):
        raise ValueError('device, stream or relative-drive path is not permitted')
    path = Path(value)
    if not path.is_absolute():
        raise ValueError('select an absolute local path')
    resolved = path.resolve(strict=True)
    if str(resolved).startswith(('\\\\', '//', '/dev/', '/proc/', '/sys/')):
        raise ValueError('resolved target is not local')
    if os.name == 'nt':
        # A mapped network drive is still remote after Path.resolve().
        root = str(resolved.anchor)
        drive_query = getattr(ctypes, 'windll').kernel32.GetDriveTypeW
        drive_query.argtypes = [ctypes.c_wchar_p]
        drive_query.restype = ctypes.c_uint
        drive_type = drive_query(root)
        if drive_type not in {2, 3, 5, 6}:  # removable, fixed, CD-ROM, RAM disk
            raise ValueError('target must be on an existing local drive')
    return resolved


def validate_https(value: str) -> str:
    text(value, 2048)
    if any(char.isspace() or ord(char) < 32 or ord(char) == 127 for char in value) or '\\' in value:
        raise ValueError('HTTPS URL contains invalid characters')
    try:
        parsed = urlsplit(value)
        host = parsed.hostname
        port = parsed.port
        if parsed.scheme != 'https' or not host or parsed.username is not None or parsed.password is not None:
            raise ValueError('use HTTPS with a host and no embedded credentials')
        if port is not None and not 1 <= port <= 65535:
            raise ValueError('invalid HTTPS port')
        if ':' in host:
            ipaddress.IPv6Address(host)
        else:
            ascii_host = host.encode('idna').decode('ascii')
            if len(ascii_host) > 253 or any(
                not re.fullmatch(r'[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?', label)
                for label in ascii_host.rstrip('.').split('.')
            ):
                raise ValueError('invalid HTTPS host')
    except (ValueError, UnicodeError) as exc:
        raise ValueError('invalid HTTPS URL') from exc
    return value


def validate_target(target: Target) -> str:
    validate_identifier(target.id)
    text(target.label, 80)
    if not isinstance(target.kind, TargetKind) or type(target.trusted) is not bool:
        raise ValueError('invalid local target record')
    if target.kind == TargetKind.BUILTIN:
        if target.value not in {'calculator', 'camera'}:
            raise ValueError('unknown built-in application')
        return target.value
    if target.kind == TargetKind.WEBSITE:
        return validate_https(target.value)
    path = _local_path(target.value)
    if target.kind == TargetKind.FOLDER:
        if not path.is_dir():
            raise ValueError('folder target must be an existing directory')
    else:
        if not path.is_file():
            raise ValueError('target must be an existing file')
        if target.kind == TargetKind.FILE:
            if path.suffix.lower() not in FILE_TYPES or Path(target.value).suffix.lower() not in FILE_TYPES:
                raise ValueError('reference files must be PDF, TXT, PNG or JPEG')
        elif target.kind == TargetKind.APP:
            if not target.trusted:
                raise ValueError('confirm that the selected application is trusted')
            for candidate in (path, Path(target.value)):
                stem = candidate.stem.lower()
                if (candidate.suffix.lower() != '.exe' or stem in DENIED_APPS
                        or re.fullmatch(r'(?:python|pythonw|pypy)[\d.]*', stem)):
                    raise ValueError('scripts, interpreters and shell launchers are not permitted')
        else:
            raise ValueError('unknown target type')
    return str(path)


class TargetRegistry:
    """Private machine bindings. Loading does not test or launch targets.

    Stale/moved targets remain visible so the user can repair them; resolve always
    validates again immediately before dispatch. Registry instances are isolated.
    """

    def __init__(self) -> None:
        self._targets: dict[str, Target] = {}
        self.quick_slots: tuple[str | None, str | None, str | None] = (None, None, None)

    @property
    def targets(self) -> tuple[Target, ...]:
        return tuple(self._targets.values())

    def copy(self) -> 'TargetRegistry':
        candidate = TargetRegistry()
        candidate._targets = dict(self._targets)
        candidate.quick_slots = self.quick_slots
        return candidate

    def replace_with(self, candidate: 'TargetRegistry') -> None:
        self._targets = dict(candidate._targets)
        self.quick_slots = candidate.quick_slots

    def configure(self, target: Target) -> None:
        validate_target(target)
        if target.id not in self._targets and len(self._targets) >= 12:
            raise ValueError('the local library supports at most twelve targets')
        self._targets[target.id] = target

    def remove(self, target_id: str) -> None:
        self._targets.pop(target_id, None)
        slots = [None if slot == target_id else slot for slot in self.quick_slots]
        self.quick_slots = (slots[0], slots[1], slots[2])

    def get(self, target_id: str) -> Target:
        if target_id not in self._targets:
            raise ValueError('shortcut is unbound on this machine; bind and test it locally')
        return self._targets[target_id]

    def resolve(self, target_id: str) -> tuple[Target, str]:
        target = self.get(target_id)
        return target, validate_target(target)

    def bind_quick(self, slots: tuple[str | None, str | None, str | None]) -> None:
        if len(slots) != 3:
            raise ValueError('Quick Actions requires three slots')
        for index, slot in enumerate(slots):
            if slot is not None:
                self.get(slot)
                # Keep stale bindings removable one slot at a time.
                if slot != self.quick_slots[index]:
                    self.resolve(slot)
        self.quick_slots = slots

    def save(self, path: Path) -> None:
        atomic_write_json(path, {'schema_version': 1, 'targets': [
            {'id': target.id, 'label': target.label, 'kind': target.kind.value,
             'value': target.value, 'trusted': target.trusted} for target in self.targets],
            'quick_slots': list(self.quick_slots)})

    def restore(self, path: Path) -> None:
        obj = fields(read_json(path), {'schema_version', 'targets', 'quick_slots'})
        version(obj['schema_version'])
        candidate: dict[str, Target] = {}
        for value in sequence(obj['targets'], 0, 12):
            item = fields(value, {'id', 'label', 'kind', 'value', 'trusted'})
            validate_identifier(item['id'])
            text(item['label'], 80)
            text(item['value'], 4096)
            if type(item['trusted']) is not bool or item['id'] in candidate:
                raise ValueError('invalid or duplicate local target')
            try:
                target = Target(item['id'], item['label'], TargetKind(item['kind']), item['value'], item['trusted'])
            except (ValueError, TypeError) as exc:
                raise ValueError('unknown target kind') from exc
            candidate[target.id] = target
        slots = sequence(obj['quick_slots'], 3, 3)
        if any(slot is not None and (not isinstance(slot, str) or slot not in candidate) for slot in slots):
            raise ValueError('Quick Action references a missing target')
        self._targets = candidate
        self.quick_slots = (slots[0], slots[1], slots[2])


class WindowsLauncher:
    """An OS open request is not proof of application readiness or completion."""

    def open(self, target: Target, resolved: str) -> None:
        if os.name != 'nt':
            raise OSError('real desktop opening is supported only on Windows')
        # Revalidate even if an adapter is called without the dispatcher.
        resolved = validate_target(target)
        if target.kind == TargetKind.BUILTIN:
            if resolved == 'camera':
                resolved = 'microsoft.windows.camera:'  # fixed adapter, never workspace supplied
            else:
                buffer = ctypes.create_unicode_buffer(32768)
                system_directory = getattr(ctypes, 'windll').kernel32.GetSystemDirectoryW
                system_directory.argtypes = [ctypes.POINTER(ctypes.c_wchar), ctypes.c_uint]
                system_directory.restype = ctypes.c_uint
                length = system_directory(buffer, len(buffer))
                if not 0 < length < len(buffer):
                    raise OSError('cannot resolve the Windows system directory')
                resolved = str(Path(buffer.value) / 'calc.exe')
        getattr(os, 'startfile')(resolved, 'open')
