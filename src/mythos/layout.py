"""Run-bundle layout: what one Mythos run directory holds and how it is written.

A run lives at ``<runs_dir>/<UTC stamp>-<slug>/``. Besides the stage
artifacts (see :mod:`mythos.stages`) it holds the generated scene, the
validation report and the manifest. ``<runs_dir>/_cache/`` is the
prerequisite cache, not a run.
"""

from __future__ import annotations

import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

SCENE_FILE = "mythos_scene.py"
VALIDATION_FILE = "validation.json"
MANIFEST_FILE = "manifest.json"
CACHE_DIR = "_cache"



def validation_template() -> dict[str, Any]:
    """The seed written to ``validation.json`` before static checks run."""
    return {
        "latex": None,
        "manim_code": None,
        "complexity": None,
        "ran_at": None,
    }


def create_run_dir(runs_dir: Path, prompt: str) -> Path:
    """Create a fresh, uniquely named run directory for ``prompt``.

    The stamp has one-second precision, so two jobs started in the same
    second would collide; the second one gets a ``-2`` (``-3``, ...) suffix.
    """
    slug = re.sub(r"[^a-z0-9]+", "-", prompt.lower()).strip("-")[:48] or "run"
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    base = Path(runs_dir) / f"{stamp}-{slug}"
    base.parent.mkdir(parents=True, exist_ok=True)
    candidate = base
    for n in range(2, 1000):
        try:
            candidate.mkdir()
            return candidate
        except FileExistsError:
            candidate = base.with_name(f"{base.name}-{n}")
    raise FileExistsError(f"could not find a free run directory name under {runs_dir}")


def iter_run_dirs(runs_dir: Path) -> Iterator[Path]:
    """Run directories under ``runs_dir``, newest first (stamp order)."""
    runs_dir = Path(runs_dir)
    if not runs_dir.is_dir():
        return
    for path in sorted(runs_dir.iterdir(), reverse=True):
        if path.is_dir() and not path.name.startswith(("_", ".")):
            yield path


def write_json(path: Path, payload: dict[str, Any]) -> None:
    """Write JSON atomically: pollers must never read a half-written file.

    (Mid-write parse errors by an MCP client polling ``manifest.json`` were a
    real observed failure.) On Windows, ``os.replace`` onto a file a poller
    currently holds open raises PermissionError: retry briefly, then fall
    back to a direct write rather than killing the run over a progress file.
    """
    path = Path(path)
    text = json.dumps(payload, indent=2)
    tmp = path.with_name(f".{path.name}.tmp")
    tmp.write_text(text, encoding="utf-8")
    for attempt in range(8):
        try:
            os.replace(tmp, path)
            return
        except PermissionError:
            time.sleep(0.02 * (attempt + 1))
    path.write_text(text, encoding="utf-8")
    tmp.unlink(missing_ok=True)


def write_manifest(run_dir: Path, manifest: dict[str, Any]) -> None:
    write_json(Path(run_dir) / MANIFEST_FILE, manifest)


def read_manifest(run_dir: Path) -> dict[str, Any]:
    return json.loads((Path(run_dir) / MANIFEST_FILE).read_text(encoding="utf-8"))
