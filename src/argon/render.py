"""Render an Argon run bundle's scene with Manim."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

from argon.models import SCENE_FILE
from argon.settings import SCRUBBED_ENV_VARS


def resolve_manim_cmd() -> list[str]:
    override = os.getenv("M2M_MANIM")
    if override:
        return [override]
    manim_bin = shutil.which("manim")
    if manim_bin:
        return [manim_bin]
    return [sys.executable, "-m", "manim"]


def find_video(media_dir: Path) -> Path | None:
    """The final mp4 Manim wrote under ``media_dir`` (never a partial segment)."""
    videos = [p for p in sorted(media_dir.rglob("*.mp4")) if "partial_movie_files" not in p.parts]
    return videos[-1] if videos else None


WINDOWS_MIKTEX_BIN = r"C:\Program Files\MiKTeX\miktex\bin\x64"


def render_scene(run_dir: Path, scene_name: str, quality: str) -> str:
    """Render ``run_dir/argon_scene.py`` into ``run_dir/media`` and return the mp4 path.

    Model-written code runs here, so every API key is removed from its environment.
    """
    media = run_dir / "media"
    command = [
        *resolve_manim_cmd(),
        f"-q{quality}",
        "--media_dir",
        str(media),
        str(run_dir / SCENE_FILE),
        scene_name,
    ]
    env = {name: value for name, value in os.environ.items() if name not in SCRUBBED_ENV_VARS}
    # A system MiKTeX install on Windows is often not on PATH for this process.
    if os.path.isdir(WINDOWS_MIKTEX_BIN) and WINDOWS_MIKTEX_BIN.lower() not in env.get("PATH", "").lower():
        env["PATH"] = env.get("PATH", "") + os.pathsep + WINDOWS_MIKTEX_BIN
    completed = subprocess.run(command, cwd=run_dir, env=env, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        raise RuntimeError((completed.stderr or completed.stdout)[-4000:])
    video = find_video(media)
    if video is None:
        raise RuntimeError("manim exited 0 but wrote no final mp4")
    return str(video)
