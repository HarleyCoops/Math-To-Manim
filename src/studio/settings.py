"""Where Studio keeps its runs and finds its pinned tools.

Environment variables, all optional and all read at call time:

    M2M_RUNS_DIR     parent of every silo's run ledger   default <checkout>/runs
    STUDIO_BLENDER   path of the Blender executable      default newest tools/blender-*
    STUDIO_ANT       path of the ``ant`` CLI             default tools/ant, then PATH
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path

#: Blender must use this GPU backend. Vulkan has open crash reports on the
#: Adreno GPUs of Windows ARM machines; OpenGL is the measured, working path.
BLENDER_GPU_BACKEND = "opengl"


def checkout_root() -> Path:
    """The source checkout this package runs from, else the current directory."""
    checkout = Path(__file__).resolve().parents[2]
    return checkout if (checkout / "pyproject.toml").is_file() else Path.cwd()


def default_runs_dir() -> Path:
    """``$M2M_RUNS_DIR/studio``; else ``runs/studio`` in the checkout. Resolved at call time."""
    if os.getenv("M2M_RUNS_DIR"):
        return Path(os.environ["M2M_RUNS_DIR"]) / "studio"
    return checkout_root() / "runs" / "studio"


def _executable(name: str) -> str:
    return f"{name}.exe" if os.name == "nt" else name


def find_blender() -> Path | None:
    """``STUDIO_BLENDER``, else the newest pinned build in ``tools/``, else PATH."""
    override = os.getenv("STUDIO_BLENDER")
    if override:
        return Path(override)
    pinned = sorted((checkout_root() / "tools").glob(f"blender-*/{_executable('blender')}"))
    if pinned:
        return pinned[-1]
    found = shutil.which("blender")
    return Path(found) if found else None


def find_ant() -> Path | None:
    """``STUDIO_ANT``, else ``tools/ant``, else PATH."""
    override = os.getenv("STUDIO_ANT")
    if override:
        return Path(override)
    pinned = checkout_root() / "tools" / "ant" / _executable("ant")
    if pinned.is_file():
        return pinned
    found = shutil.which("ant")
    return Path(found) if found else None
