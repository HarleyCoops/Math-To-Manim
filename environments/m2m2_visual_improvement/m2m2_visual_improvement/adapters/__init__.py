"""Filesystem-only provider adapters."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from .common import AdapterError, TaskBundle
from .mythos import export_mythos_run
from .sol import export_sol_run


def detect_provider(run_dir: Path) -> Literal["mythos", "sol"]:
    run_dir = Path(run_dir)
    has_mythos = (run_dir / "mythos_scene.py").is_file()
    has_sol = (run_dir / "sol_scene.py").is_file()
    if has_mythos == has_sol:
        raise AdapterError(
            "run must contain exactly one of mythos_scene.py or sol_scene.py"
        )
    return "mythos" if has_mythos else "sol"


def export_run(run_dir: Path) -> TaskBundle:
    provider = detect_provider(run_dir)
    if provider == "mythos":
        return export_mythos_run(run_dir)
    return export_sol_run(run_dir)


__all__ = [
    "AdapterError",
    "TaskBundle",
    "detect_provider",
    "export_mythos_run",
    "export_run",
    "export_sol_run",
]
