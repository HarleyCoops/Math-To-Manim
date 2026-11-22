"""Render, probe and frame extraction for motion runs.

Renders use the same pinning as :mod:`mythos.render` (cwd and media inside
the run, no shell, wall-clock timeout) but set the exact pixel size and frame
rate from the BriefSpec on the command line, which ``-q`` presets cannot.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path

from mythos.render import (
    find_final_video,
    resolve_inside,
    resolve_manim,
    validate_scene_name,
)

DRAFT_HEIGHT = 480
DRAFT_FPS = 15.0


@dataclass
class RenderRun:
    command: list[str]
    exit_code: int
    output: str
    seconds: float
    video: Path | None
    timed_out: bool = False

    def tail(self, chars: int = 4000) -> str:
        return self.output[-chars:]


def draft_size(width: int, height: int) -> tuple[int, int]:
    """A 480-line draft with the final aspect ratio (even dimensions)."""
    scale = DRAFT_HEIGHT / min(width, height)
    w, h = round(width * scale / 2) * 2, round(height * scale / 2) * 2
    return int(w), int(h)


def render(work_dir: Path, *, scene_file: str, scene_name: str, width: int,
           height: int, fps: float, media_subdir: str, timeout: float) -> RenderRun:
    root = Path(work_dir).resolve()
    scene_path = resolve_inside(root, scene_file)
    media = resolve_inside(root, root / media_subdir)
    if media.exists():
        shutil.rmtree(media, ignore_errors=True)
    media.mkdir(parents=True, exist_ok=True)
    fps_text = f"{fps:g}"
    command = resolve_manim() + [
        "-r", f"{width},{height}", "--frame_rate", fps_text,
        "--media_dir", str(media), "--progress_bar", "none",
        "--disable_caching",
        scene_path.name, validate_scene_name(scene_name),
    ]
    started = time.perf_counter()
    try:
        completed = subprocess.run(
            command, cwd=str(root), capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=timeout, check=False)
    except subprocess.TimeoutExpired as exc:
        partial = exc.stderr or exc.stdout or ""
        if isinstance(partial, bytes):
            partial = partial.decode("utf-8", errors="replace")
        return RenderRun(command, 124, f"render timed out after {timeout:.0f}s\n{partial}",
                         time.perf_counter() - started, None, timed_out=True)
    output = (completed.stderr or "") + (completed.stdout or "")
    video = find_final_video(media) if completed.returncode == 0 else None
    return RenderRun(command, completed.returncode, output,
                     time.perf_counter() - started, video)


@dataclass
class Probe:
    width: int
    height: int
    fps: float
    duration_s: float
    frames: int | None = None
    raw: dict = field(default_factory=dict)


def probe(video: Path) -> Probe:
    completed = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_packets",
         "-show_entries", "stream=width,height,r_frame_rate,avg_frame_rate,nb_read_packets,duration"
         ":format=duration", "-of", "json", str(video)],
        capture_output=True, text=True, check=True, timeout=120)
    data = json.loads(completed.stdout)
    stream = data["streams"][0]
    num, _, den = stream.get("avg_frame_rate", "0/1").partition("/")
    fps = float(num) / float(den or 1) if float(den or 1) else 0.0
    duration = float(data.get("format", {}).get("duration") or stream.get("duration") or 0)
    frames = stream.get("nb_read_packets")
    return Probe(int(stream["width"]), int(stream["height"]), round(fps, 3),
                 round(duration, 3), int(frames) if frames else None, data)


def extract_frames(video: Path, times: list[float], out_dir: Path, *,
                   width: int | None = None, prefix: str = "t") -> list[tuple[float, Path]]:
    """One PNG per time; ``width`` downscales (keeping aspect)."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    frames = []
    for t in times:
        path = out_dir / f"{prefix}{t:07.3f}s.png"
        command = ["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", str(video),
                   "-frames:v", "1"]
        if width:
            command += ["-vf", f"scale={width}:-2"]
        command.append(str(path))
        subprocess.run(command, capture_output=True, check=False, timeout=120)
        if path.is_file():
            frames.append((t, path))
    return frames
