"""One-command showcase GIFs: `math-to-manim-mythos gif <run_id | scene.mp4>`.

A rendered run keeps its MP4 under ``<run_dir>/media/videos/...``; the
showcase (and the README) wants palette-optimized GIFs. This module turns
one into the other with ffmpeg's two-pass palette pipeline — the same recipe
behind every GIF on the front page.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from mythos.layout import MANIFEST_FILE, read_manifest
from mythos.render import find_final_video
from mythos.settings import default_runs_dir

DEFAULT_FPS = 12
DEFAULT_WIDTH = 640


def resolve_source(target: str, *, runs_dir: Path | None = None) -> tuple[Path, Path]:
    """Map a run id or mp4 path to (mp4_path, default_output_path)."""
    as_path = Path(target)
    if as_path.suffix.lower() == ".mp4":
        if not as_path.exists():
            raise FileNotFoundError(f"No such file: {as_path}")
        return as_path, as_path.with_suffix(".gif")

    runs_dir = Path(runs_dir) if runs_dir else default_runs_dir()
    run_dir = runs_dir / target
    if not (run_dir / MANIFEST_FILE).exists():
        raise FileNotFoundError(
            f"{target!r} is neither an .mp4 path nor a run id under "
            f"{runs_dir} (no {MANIFEST_FILE} found)")
    scene_name = read_manifest(run_dir).get("scene_name")
    if not scene_name:
        raise ValueError(f"Run {target!r} has no scene_name in its manifest "
                         "(did the chain reach codegen?)")
    mp4 = find_final_video(run_dir)
    if mp4 is None:
        raise FileNotFoundError(
            f"No rendered MP4 found in run {target!r} for scene {scene_name!r}. "
            f"Render first: math-to-manim-mythos run ... --render, or "
            f"manim -qm --media_dir {run_dir / 'media'} {run_dir / 'mythos_scene.py'} {scene_name}")
    return mp4, run_dir / f"{scene_name}.gif"


def mp4_to_gif(mp4: Path, out: Path, *, fps: int = DEFAULT_FPS,
               width: int = DEFAULT_WIDTH, max_colors: int = 128) -> Path:
    """Two-pass palette encode (diff-mode palette, bayer dither)."""
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg not found on PATH (required for GIFs)")
    scale = f"fps={fps},scale={width}:-1:flags=lanczos"
    with tempfile.TemporaryDirectory(prefix="m2m-gif-") as tmp:
        palette = Path(tmp) / "palette.png"
        subprocess.run(
            [ffmpeg, "-v", "error", "-i", str(mp4),
             "-vf", f"{scale},palettegen=max_colors={max_colors}:stats_mode=diff",
             "-y", str(palette)],
            check=True)
        subprocess.run(
            [ffmpeg, "-v", "error", "-i", str(mp4), "-i", str(palette),
             "-lavfi",
             f"{scale}[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=5:"
             "diff_mode=rectangle",
             "-y", str(out)],
            check=True)
    return out


def make_gif(target: str, output: str | None = None, *,
             fps: int = DEFAULT_FPS, width: int = DEFAULT_WIDTH) -> Path:
    """The `math-to-manim-mythos gif` entry point. Returns the written GIF path."""
    mp4, default_out = resolve_source(target)
    out = Path(output) if output else default_out
    out.parent.mkdir(parents=True, exist_ok=True)
    mp4_to_gif(mp4, out, fps=fps, width=width)
    size_mb = out.stat().st_size / 1e6
    print(f"  [mythos] {mp4.name} -> {out}  ({size_mb:.1f} MB, "
          f"{fps} fps, {width}px)", file=sys.stderr)
    return out
