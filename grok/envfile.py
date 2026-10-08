"""Load a local .env without overriding the process environment or logging values."""

from __future__ import annotations

import os
from pathlib import Path


def load_local_env(path: Path | None = None) -> None:
    file = path if path is not None else Path.cwd() / ".env"
    if not file.is_file():
        return
    try:
        lines = file.read_text(encoding="utf-8").splitlines()
    except OSError:
        return
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        if stripped.startswith("export "):
            stripped = stripped[len("export ") :]
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        if key and key not in os.environ:
            os.environ[key] = value
