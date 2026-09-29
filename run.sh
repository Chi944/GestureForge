#!/bin/bash
set -eu
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
if [ ! -x .venv/bin/python ]; then
    echo 'Run python3.11 scripts/setup_macos.py first.' >&2
    exit 1
fi
exec .venv/bin/python -m gestureforge "$@"
