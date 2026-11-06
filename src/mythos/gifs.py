"""One-command showcase GIFs: `math-to-manim gif <run_id | scene.mp4>`.

Manim leaves rendered MP4s under ``media/videos/<module>/<quality>/``; the
showcase (and the README) wants palette-optimized GIFs. This module turns
one into the other with ffmpeg's two-pass palette pipeline — the same recipe
behind every GIF on the front page.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path

from mythos.harness import REPO_ROOT, default_runs_dir

DEFAULT_FPS = 12
DEFAULT_WIDTH = 640


def find_scene_mp4(scene_name: str, media_root: Path | None = None) -> Path | None:
    """Newest rendered MP4 for a scene, searching media/videos recursively."""
    root = media_root or (REPO_ROOT / "media" / "videos")
    if not root.exists():
        return None
    candidates = sorted(
        root.rglob(f"{scene_name}.mp4"),
        key=lambda p: (p.stat().st_mtime_ns, p.as_posix()),
        reverse=True,
    )
    for candidate in candidates:
        if "partial_movie_files" not in candidate.parts:
            return candidate
    return None


def resolve_source(target: str) -> tuple[Path, Path]:
    """Map a run id or mp4 path to (mp4_path, default_output_path)."""
    as_path = Path(target)
    if as_path.suffix.lower() == ".mp4":
        if not as_path.exists():
            raise FileNotFoundError(f"No such file: {as_path}")
        return as_path, as_path.with_suffix(".gif")

    run_dir = default_runs_dir() / target
    manifest_path = run_dir / "manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError(
            f"{target!r} is neither an .mp4 path nor a run id under "
            f"{default_runs_dir()} (no manifest.json found)")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    scene_name = manifest.get("scene_name")
    if not scene_name:
        raise ValueError(f"Run {target!r} has no scene_name in its manifest "
                         "(did the chain reach codegen?)")
    local = run_dir / f"{scene_name}.mp4"
    mp4 = local if local.exists() else find_scene_mp4(scene_name)
    if mp4 is None:
        raise FileNotFoundError(
            f"No rendered MP4 found for scene {scene_name!r}. "
            "Render first: manim -qm <scene file> " + scene_name)
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
    """The `math-to-manim gif` entry point. Returns the written GIF path."""
    mp4, default_out = resolve_source(target)
    out = Path(output) if output else default_out
    out.parent.mkdir(parents=True, exist_ok=True)
    mp4_to_gif(mp4, out, fps=fps, width=width)
    size_mb = out.stat().st_size / 1e6
    print(f"  [mythos] {mp4.name} -> {out}  ({size_mb:.1f} MB, "
          f"{fps} fps, {width}px)")
    return out
