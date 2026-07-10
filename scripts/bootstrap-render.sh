#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

mapfile -t system_packages < <(sed -e '/^[[:space:]]*#/d' -e '/^[[:space:]]*$/d' requirements-system.txt)

if command -v apt-get >/dev/null 2>&1; then
  privilege=()
  if [ "$(id -u)" -ne 0 ]; then
    if ! command -v sudo >/dev/null 2>&1; then
      echo "sudo is required to install packages from requirements-system.txt" >&2
      exit 1
    fi
    privilege=(sudo)
  fi
  "${privilege[@]}" apt-get update
  "${privilege[@]}" apt-get install -y "${system_packages[@]}"
else
  missing=()
  for command_name in ffmpeg latex dvisvgm pkg-config; do
    command -v "$command_name" >/dev/null 2>&1 || missing+=("$command_name")
  done
  if [ "${#missing[@]}" -gt 0 ]; then
    echo "Missing render tools: ${missing[*]}" >&2
    echo "Install the equivalents listed in requirements-system.txt with your OS package manager." >&2
    exit 1
  fi
fi

if [ ! -x ".venv/bin/python" ]; then
  python3 -m venv .venv
fi

.venv/bin/python -m pip install -U pip
.venv/bin/python -m pip install -r requirements-render.txt

.venv/bin/manim --version
