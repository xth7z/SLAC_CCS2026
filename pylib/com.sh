#!/bin/sh
set -eu

PROJECT_ROOT="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
PYTHON="${PYTHON:-python3}"

# Build the current source for this interpreter in an activated virtual environment.
"$PYTHON" -m pip install --no-cache-dir --force-reinstall "$PROJECT_ROOT"
