#!/usr/bin/env bash
set -euo pipefail

if [[ "${1:-}" == "--help" ]]; then
  echo 'Usage: ./setup-computer-use.sh'
  echo 'Installs Computer Use plugins for the current Codex home on macOS.'
  exit 0
fi
if [[ $# -ne 0 ]]; then
  echo 'Unexpected argument. Use --help.' >&2
  exit 2
fi
if [[ "$(uname -s)" != Darwin ]]; then
  echo 'This Computer Use setup requires macOS and the desktop app.' >&2
  exit 1
fi
if ! command -v codex >/dev/null 2>&1; then
  echo 'Install Codex and sign in before setting up Computer Use.' >&2
  exit 1
fi
if [[ ! -d /Applications/ChatGPT.app ]]; then
  echo 'Install the ChatGPT desktop app before setting up its Computer Use plugins.' >&2
  exit 1
fi
codex plugin add computer-use@openai-bundled
codex plugin add unified-computer-use@openai-bundled
printf '%s\n' 'Restart the desktop app and complete its Computer Use permission prompts.'
