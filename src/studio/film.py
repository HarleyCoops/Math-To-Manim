"""Build a film from a SceneSpec: render every shot, check it, join the shots.

    build_film(spec, run_dir) -> {"film": ..., "shots": {...}, "outcome": ...}

Per shot:

- ``scene3d``: Blender renders the frames; Manim renders one transparent
  overlay (caption and equation); ffmpeg lays the overlay over the frames.
- ``card``: Manim renders the animated card.

Every shot becomes one H.264 segment of the same size and frame rate, and the
segments are joined without re-encoding. A shot that fails is recorded and
left out; the film is still built from the shots that passed.

Each shot has a state: ``queued``, ``rendering``, ``measuring``, then
``accepted`` or ``failed``. ``on_shot`` is called at every change.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any, Callable

from studio.doctor import Runner, run_command
from studio.settings import BLENDER_GPU_BACKEND, find_blender
from studio.spec.compile import compile_shot
from studio.spec.models import SceneSpec

ENGINES_DIR = Path(__file__).resolve().parent / "engines"
SRC_DIR = Path(__file__).resolve().parents[1]
OnShot = Callable[[str, dict[str, Any]], None]


class ShotFailed(RuntimeError):
    """One shot could not be rendered or did not pass its checks."""


def _scene_file(builder: str, class_name: str, compiled_path: Path) -> str:
    return (
        "import sys\n"
        f"sys.path.insert(0, {str(SRC_DIR)!r})\n"
        f"from studio.engines.manim_card import {builder}\n"
        # Manim lists only the scenes that are defined in the file it is given.
        f"class {class_name}({builder}({str(compiled_path)!r})):\n"
        "    pass\n"
    )


def _manim(work: Path, builder: str, class_name: str, compiled: dict, compiled_path: Path,
           extra: list[str], pattern: str, runner: Runner) -> Path:
    scene_file = work / f"{class_name.lower()}_scene.py"
    scene_file.write_text(_scene_file(builder, class_name, compiled_path), encoding="utf-8")
    media = work / f"media_{class_name.lower()}"
    code, output = runner([
        sys.executable, "-m", "manim", "--disable_caching",
        "--resolution", f"{compiled['width']},{compiled['height']}",
        "--fps", str(compiled["fps"]), "--media_dir", str(media), *extra,
        str(scene_file), class_name], 1800.0)
    found = [p for p in sorted(media.rglob(pattern)) if "partial_movie_files" not in p.parts]
    if code != 0 or not found:
        raise ShotFailed(f"manim {class_name} failed (exit {code}): {output[-1500:]}")
    return found[-1]


def _ffmpeg(arguments: list[str], output: Path, runner: Runner) -> None:
    code, text = runner(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                         *arguments, str(output)], 1800.0)
    if code != 0 or not output.is_file() or output.stat().st_size == 0:
        raise ShotFailed(f"ffmpeg failed for {output.name} (exit {code}): {text[-1500:]}")


_ENCODE = ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
           "-an", "-movflags", "+faststart"]


def check_frames(frames_dir: Path, expected: int) -> list[str]:
    """Measured checks on a frame sequence. Returns the problems found."""
    from PIL import Image

    frames = sorted(frames_dir.glob("frame_*.png"))
    problems = []
    if len(frames) != expected:
        problems.append(f"expected {expected} frames, found {len(frames)}")
    for path in frames[:: max(1, len(frames) // 3)][:4]:
        with Image.open(path) as image:
            low, high = image.convert("L").getextrema()
        if high - low < 12:
            problems.append(f"{path.name} is empty: one flat colour")
    return problems


def render_scene3d(compiled: dict, compiled_path: Path, work: Path, samples: int,
                   runner: Runner) -> tuple[Path, dict[str, Any]]:
    blender = find_blender()
    if blender is None:
        raise ShotFailed("blender not found")
    frames_dir = work / "frames"
    for stale in frames_dir.glob("frame_*.png"):
        stale.unlink()
    code, output = runner([
        str(blender), "--background", "--factory-startup",
        "--gpu-backend", BLENDER_GPU_BACKEND,
        "--python", str(ENGINES_DIR / "blender_shot.py"),
        "--", str(compiled_path), str(frames_dir), str(samples)], 7200.0)
    if code != 0:
        raise ShotFailed(f"blender failed (exit {code}): {output[-1500:]}")
    problems = check_frames(frames_dir, compiled["frames"])
    if problems:
        raise ShotFailed("; ".join(problems))

    notes: dict[str, Any] = {}
    overlay = None
    if compiled.get("caption") or compiled["equations"]:
        try:
            overlay = _manim(work, "build_overlay", "StudioOverlay", compiled, compiled_path,
                             ["-s", "-t"], "StudioOverlay*.png", runner)
        except ShotFailed as exc:
            # The picture is still correct without its caption; record the loss.
            notes["overlay_dropped"] = str(exc)[:300]
    segment = work / "segment.mp4"
    source = ["-framerate", str(compiled["fps"]), "-i", str(frames_dir / "frame_%04d.png")]
    if overlay is not None:
        _ffmpeg([*source, "-i", str(overlay), "-filter_complex",
                 "[0:v][1:v]overlay=0:0:format=auto", *_ENCODE], segment, runner)
    else:
        _ffmpeg([*source, *_ENCODE], segment, runner)
    return segment, notes


def render_card(compiled: dict, compiled_path: Path, work: Path,
                runner: Runner) -> tuple[Path, dict[str, Any]]:
    notes: dict[str, Any] = {}
    try:
        movie = _manim(work, "build_card", "StudioCard", compiled, compiled_path,
                       ["--format", "mp4"], "StudioCard*.mp4", runner)
    except ShotFailed as exc:
        if not compiled["equations"]:
            raise
        # A LaTeX error is the usual cause. The card is still useful without
        # its equations, so render it again without them and record the loss.
        notes["equations_dropped"] = str(exc)[:300]
        plain = dict(compiled, equations=[])
        compiled_path.write_text(json.dumps(plain, indent=2), encoding="utf-8")
        movie = _manim(work, "build_card", "StudioCard", plain, compiled_path,
                       ["--format", "mp4"], "StudioCard*.mp4", runner)
    segment = work / "segment.mp4"
    _ffmpeg(["-i", str(movie), "-vf",
             f"scale={compiled['width']}:{compiled['height']},fps={compiled['fps']}",
             *_ENCODE], segment, runner)
    return segment, notes


def probe_seconds(path: Path, runner: Runner) -> float | None:
    code, output = runner(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                           "-of", "default=noprint_wrappers=1:nokey=1", str(path)], 120.0)
    try:
        return float(output.strip().splitlines()[0]) if code == 0 else None
    except (ValueError, IndexError):
        return None


def contact_sheet(spec: SceneSpec, shots_dir: Path, accepted: list[str], out: Path,
                  runner: Runner) -> Path | None:
    """One middle frame per accepted shot, on a grid, with the shot id under it."""
    from PIL import Image, ImageDraw

    thumbs = []
    for shot_id in accepted:
        frame = shots_dir / shot_id / "contact.png"
        shot = spec.shot(shot_id)
        middle = spec.frame_count(shot) / spec.world.fps / 2
        code, _ = runner(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                          "-ss", f"{middle:.3f}", "-i", str(shots_dir / shot_id / "segment.mp4"),
                          "-frames:v", "1", str(frame)], 300.0)
        if code == 0 and frame.is_file():
            thumbs.append((shot_id, frame))
    if not thumbs:
        return None
    columns = min(3, len(thumbs))
    tile_w, tile_h, label_h = 640, 360, 36
    rows = (len(thumbs) + columns - 1) // columns
    sheet = Image.new("RGB", (columns * tile_w, rows * (tile_h + label_h)), "#0c0c0b")
    draw = ImageDraw.Draw(sheet)
    for index, (shot_id, frame) in enumerate(thumbs):
        x, y = (index % columns) * tile_w, (index // columns) * (tile_h + label_h)
        with Image.open(frame) as image:
            sheet.paste(image.convert("RGB").resize((tile_w, tile_h)), (x, y))
        draw.text((x + 12, y + tile_h + 10), f"{index + 1}. {shot_id}", fill="#faf9f5")
    sheet.save(out)
    return out


def build_film(spec: SceneSpec, run_dir: Path, *, samples: int = 32,
               runner: Runner = run_command, on_shot: OnShot | None = None,
               log: Callable[[str], None] = print) -> dict[str, Any]:
    """Render, check and join every shot of ``spec`` into ``run_dir/film.mp4``."""
    shots_dir = run_dir / "shots"
    states: dict[str, dict[str, Any]] = {
        shot.id: {"state": "queued", "kind": shot.kind, "engine": shot.engine}
        for shot in spec.shots}

    def update(shot_id: str, **changes: Any) -> None:
        states[shot_id].update(changes)
        if on_shot is not None:
            on_shot(shot_id, dict(states[shot_id]))

    accepted: list[str] = []
    for shot in spec.shots:
        work = shots_dir / shot.id
        work.mkdir(parents=True, exist_ok=True)
        compiled = compile_shot(spec, shot.id)
        compiled_path = work / "compiled.json"
        compiled_path.write_text(json.dumps(compiled), encoding="utf-8")
        update(shot.id, state="rendering", frames=compiled["frames"])
        log(f"shot {shot.id}: {shot.kind}, {compiled['frames']} frames ...")
        started = time.perf_counter()
        try:
            if shot.kind == "scene3d":
                segment, notes = render_scene3d(compiled, compiled_path, work, samples, runner)
            else:
                segment, notes = render_card(compiled, compiled_path, work, runner)
            update(shot.id, state="measuring")
            seconds = probe_seconds(segment, runner)
            expected = compiled["duration_s"]
            if seconds is not None and abs(seconds - expected) > 0.25:
                raise ShotFailed(f"segment is {seconds:.2f} s, expected {expected:.2f} s")
        except ShotFailed as exc:
            update(shot.id, state="failed", error=str(exc)[:1500],
                   seconds=round(time.perf_counter() - started, 1))
            log(f"  [FAILED] {shot.id}: {str(exc)[:300]}")
            continue
        update(shot.id, state="accepted", segment=str(segment), **notes,
               seconds=round(time.perf_counter() - started, 1))
        accepted.append(shot.id)
        log(f"  [ok] {shot.id} in {states[shot.id]['seconds']} s")

    result: dict[str, Any] = {"shots": states, "film": None, "contact_sheet": None,
                              "outcome": "failed", "seconds": None}
    if not accepted:
        return result
    listing = run_dir / "segments.txt"
    listing.write_text("".join(
        f"file '{(shots_dir / shot_id / 'segment.mp4').as_posix()}'\n" for shot_id in accepted),
        encoding="utf-8")
    film = run_dir / "film.mp4"
    try:
        _ffmpeg(["-f", "concat", "-safe", "0", "-i", str(listing), "-c", "copy"], film, runner)
    except ShotFailed as exc:
        result["error"] = str(exc)[:1500]
        return result
    sheet = contact_sheet(spec, shots_dir, accepted, run_dir / "contact_sheet.png", runner)
    result.update(
        film=str(film),
        contact_sheet=str(sheet) if sheet else None,
        seconds=probe_seconds(film, runner),
        outcome="film_ready" if len(accepted) == len(spec.shots) else "film_partial")
    return result
