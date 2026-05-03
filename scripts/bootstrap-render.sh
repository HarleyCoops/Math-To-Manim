#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

missing=()
for command_name in ffmpeg latex dvisvgm; do
  if ! command -v "$command_name" >/dev/null 2>&1; then
    missing+=("$command_name")
  fi
done

if [ "${#missing[@]}" -gt 0 ]; then
  if ! command -v apt-get >/dev/null 2>&1; then
    echo "Missing render tools: ${missing[*]}" >&2
    echo "apt-get not found. Install packages from requirements-system.txt with your OS package manager." >&2
    exit 1
  fi

  sudo apt-get update
  sudo xargs -a requirements-system.txt apt-get install -y
fi

if [ ! -x ".venv/bin/python" ]; then
  python3 -m venv .venv
fi

.venv/bin/python -m pip install -U pip
.venv/bin/python -m pip install -e ".[dev,render]"

.venv/bin/manim --version
