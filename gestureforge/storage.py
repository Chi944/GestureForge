"""Bounded JSON reads and durable, atomic private state replacement."""
from __future__ import annotations

import json
import os
from pathlib import Path
import tempfile
from typing import Any

MAX_JSON_BYTES = 1024 * 1024


def read_json(path: Path, limit: int = MAX_JSON_BYTES) -> Any:
    with path.open('rb') as stream:
        data = stream.read(limit + 1)
    if len(data) > limit:
        raise ValueError('JSON exceeds the size limit')
    return decode_json(data)


def decode_json(data: bytes) -> Any:
    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise ValueError(f'duplicate JSON key: {key}')
            result[key] = value
        return result

    def invalid(value: str) -> None:
        raise ValueError(f'non-finite JSON number: {value}')

    try:
        return json.loads(data, object_pairs_hook=pairs, parse_constant=invalid)
    except (UnicodeError, json.JSONDecodeError, RecursionError) as exc:
        raise ValueError('invalid JSON; active state preserved') from exc


def atomic_write_json(path: Path, raw: object, *, limit: int = MAX_JSON_BYTES) -> None:
    data = (json.dumps(raw, ensure_ascii=False, allow_nan=False, indent=2) + '\n').encode()
    if len(data) > limit:
        raise ValueError('JSON exceeds the size limit')
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f'.{path.name}.', dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def fields(raw: object, required: set[str], optional: set[str] | None = None) -> dict[str, Any]:
    if not isinstance(raw, dict) or not required <= raw.keys():
        raise ValueError('missing fields or object required')
    if raw.keys() - required - (optional or set()):
        raise ValueError('unknown fields are not permitted')
    return raw


def text(value: object, maximum: int, *, empty: bool = False) -> str:
    if not isinstance(value, str) or len(value) > maximum or (not empty and not value.strip()):
        raise ValueError(f'text must contain {0 if empty else 1}–{maximum} characters')
    if '\x00' in value:
        raise ValueError('NUL is not permitted')
    return value


def sequence(value: object, minimum: int, maximum: int) -> list[Any]:
    if not isinstance(value, list) or not minimum <= len(value) <= maximum:
        raise ValueError(f'list must contain {minimum}–{maximum} items')
    return value


def version(value: object) -> None:
    if type(value) is not int or value != 1:
        raise ValueError('unsupported schema version')
