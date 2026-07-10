#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

./scripts/bootstrap-render.sh

if ! command -v npm >/dev/null 2>&1; then
  echo "npm is required to install the pinned Codex CLI from package-lock.json" >&2
  exit 1
fi

npm --cache "$PWD/.npm-cache" ci
ln -sfn "$PWD/node_modules/.bin/codex" .venv/bin/codex

.venv/bin/manim --version
.venv/bin/codex --version

if .venv/bin/codex login status >/dev/null 2>&1; then
  .venv/bin/math-to-manim-sol doctor
else
  echo "Runtime installed. Finish authentication with:"
  echo "  .venv/bin/codex login"
  echo "Then verify with:"
  echo "  .venv/bin/math-to-manim-sol doctor"
fi
