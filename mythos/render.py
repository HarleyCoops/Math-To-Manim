"""Sandboxed Manim render for a Mythos run directory.

The previous harness invoked Manim with ``cwd`` at the repository root and no
``--media_dir``, so generated media leaked into ``media/`` at the checkout
root. Render outputs now stay inside the run directory.

Threat model (see ``docs/security.md``): ``mythos_scene.py`` is
trusted-with-caveats agent output. This wrapper pins paths, cwd, argument
vector, and a wall-clock timeout. It does not give Manim a full OS sandbox.
"""

from __future__ import annotations

import importlib.util
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import resource
except ImportError:  # pragma: no cover - Windows
    resource = None  # type: ignore[assignment]

DEFAULT_RENDER_TIMEOUT = float(os.getenv("M2M_RENDER_TIMEOUT", "1800"))

_SCENE_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_QUALITY = re.compile(r"^[lmhpk]$")


def resolve_manim() -> list[str]:
    """Find the manim entry point, preferring the active interpreter's env."""
    override = os.getenv("M2M_MANIM")
    if override:
        return [override]
    if importlib.util.find_spec("manim") is not None:
        return [sys.executable, "-m", "manim"]
    return [shutil.which("manim") or "manim"]


class RenderError(RuntimeError):
    pass


def resolve_inside(run_dir: Path, path: Path | str) -> Path:
    """Resolve ``path`` and reject anything that escapes ``run_dir``."""
    root = Path(run_dir).resolve()
    candidate = Path(path)
    resolved = candidate.resolve() if candidate.is_absolute() else (root / candidate).resolve()
    if resolved != root and root not in resolved.parents:
        raise RenderError(f"path escapes run directory: {path}")
    return resolved


def validate_scene_name(scene_name: str) -> str:
    if not _SCENE_NAME.fullmatch(scene_name):
        raise RenderError(f"invalid scene class name: {scene_name!r}")
    return scene_name


def apply_resource_limits() -> None:
    """Best-effort CPU and address-space caps for the Manim child.

    Residual risk: ``resource`` is unavailable on Windows; even on Linux these
    limits do not stop a scene from opening sockets or writing through Manim
    itself. Follow-up: a user-namespace / bubblewrap jail.
    """
    if resource is None:
        return
    try:
        resource.setrlimit(resource.RLIMIT_CPU, (600, 600))
    except (ValueError, OSError):
        pass
    try:
        resource.setrlimit(resource.RLIMIT_AS, (4 * 1024 ** 3, 4 * 1024 ** 3))
    except (ValueError, OSError):
        pass


def build_manim_command(
    run_dir: Path,
    *,
    scene_file: Path,
    scene_name: str,
    quality: str,
) -> list[str]:
    if not _QUALITY.fullmatch(quality):
        raise RenderError(f"invalid Manim quality flag: {quality!r}")
    root = Path(run_dir).resolve()
    scene_path = resolve_inside(root, scene_file)
    media_dir = resolve_inside(root, root / "media")
    return resolve_manim() + [
        f"-q{quality}",
        "--media_dir",
        str(media_dir),
        "--progress_bar",
        "none",
        str(scene_path.name),
        validate_scene_name(scene_name),
    ]


def find_final_video(run_dir: Path) -> Path | None:
    candidates = [
        path
        for path in Path(run_dir).glob("**/*.mp4")
        if "partial_movie_files" not in {part.lower() for part in path.parts}
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda path: path.stat().st_mtime_ns)


def render_scene_file(
    run_dir: Path,
    *,
    scene_file: Path,
    scene_name: str,
    quality: str,
    timeout: float = DEFAULT_RENDER_TIMEOUT,
) -> tuple[int, str]:
    """Run Manim with cwd and media pinned to ``run_dir``. Never uses shell=True."""
    root = Path(run_dir).resolve()
    root.mkdir(parents=True, exist_ok=True)
    (root / "media").mkdir(exist_ok=True)
    command = build_manim_command(
        root,
        scene_file=scene_file,
        scene_name=scene_name,
        quality=quality,
    )
    try:
        completed = subprocess.run(
            command,
            cwd=str(root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
            preexec_fn=apply_resource_limits if resource is not None else None,
        )
    except subprocess.TimeoutExpired as exc:
        partial = exc.stderr or exc.stdout or b""
        if isinstance(partial, bytes):
            partial = partial.decode("utf-8", errors="replace")
        return 124, (
            f"render timed out after {timeout:.0f}s "
            "(raise M2M_RENDER_TIMEOUT or lower the quality)\n" + partial
        )
    return completed.returncode, (completed.stderr or "") + (completed.stdout or "")
