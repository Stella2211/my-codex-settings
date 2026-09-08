#!/bin/sh
set -eu

if ! command -v uv >/dev/null 2>&1; then
  echo "error: uv is required; install uv and run this script again" >&2
  exit 127
fi

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
exec uv run --no-project --with 'tomlkit==0.15.1' python "$SCRIPT_DIR/install.py" "$@"
