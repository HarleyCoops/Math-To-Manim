"""Local Manim rendering for the Grok silo.

Static screening is not an OS or container sandbox. It only refuses
imports and calls outside a small allowlist. Child processes receive a
clean environment so API keys, secrets, and tokens never reach Manim.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

from grok.validation import validate_scene_source

DEFAULT_RENDER_TIMEOUT = 7200
PROBE_TIMEOUT = 600
TOOL_TIMEOUT = 120
DEFAULT_MIN_DURATION = 20.0
DEFAULT_MAX_DURATION = 240.0

# Delivery profiles. p and k match the Grok CLI quality flags.
PROFILES = {
    "l": (854, 480, 15),
    "m": (1280, 720, 30),
    "h": (1920, 1080, 60),
    "p": (2560, 1440, 60),
    "k": (3840, 2160, 60),
}

_SECRET_MARKERS = ("API_KEY", "SECRET", "TOKEN", "PASSWORD")


def clean_environment(source: dict[str, str] | None = None) -> dict[str, str]:
    env = os.environ if source is None else source
    return {
        key: value
        for key, value in env.items()
        if not any(marker in key.upper() for marker in _SECRET_MARKERS)
    }


def assert_duration(duration: float, minimum: float, maximum: float) -> None:
    if not minimum <= duration <= maximum:
        raise RuntimeError(f"Unexpected film duration: {duration}")


def duration_of(metadata: dict) -> float:
    return float(metadata["format"]["duration"])


def _run(args, *, cwd, timeout, runner=None):
    run = runner or subprocess.run
    try:
        return run(
            list(args),
            cwd=str(cwd),
            env=clean_environment(),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"command timed out after {timeout}s") from exc


def _check(result, label: str) -> str:
    if result.returncode:
        detail = (result.stderr or result.stdout or "")[-5000:]
        raise RuntimeError(f"{label} failed: {detail}")
    return result.stdout or ""


def _screen(source: str) -> str:
    failures, scene_name = validate_scene_source(source)
    if failures or not scene_name:
        raise RuntimeError("Scene failed static screening: " + "; ".join(failures))
    return scene_name


def _worker_args(scene_path: Path, media_dir: Path, quality: str, mode: str, scene_name: str) -> list[str]:
    worker = Path(__file__).with_name("render_worker.py")
    return [
        sys.executable,
        str(worker),
        str(scene_path),
        str(media_dir),
        quality,
        mode,
        scene_name,
    ]


def write_contact_sheet(folder: Path, frames: list[Path], duration: float) -> Path:
    # Pillow ships with Manim. Importing it here keeps `import grok` usable
    # in offline CI images that have not installed the render extra.
    from PIL import Image, ImageDraw, ImageOps

    sheet = Image.new("RGB", (1280, 4 * 204), (12, 18, 30))
    for index, frame in enumerate(frames):
        with Image.open(frame) as image:
            thumb = ImageOps.contain(image.convert("RGB"), (426, 180))
            sheet.paste(thumb, ((index % 3) * 426, (index // 3) * 204))
        ImageDraw.Draw(sheet).text(
            ((index % 3) * 426 + 8, (index // 3) * 204 + 182),
            f"{duration * (index + 0.5) / 12:.1f}s",
            fill="white",
        )
    target = folder / "contact_sheet.png"
    sheet.save(target)
    return target


def probe(run_dir, source, attempt, *, quality="l", timeout=PROBE_TIMEOUT, runner=None):
    """Render one final still. A still is not evidence of continuous motion."""
    scene_name = _screen(source)
    folder = Path(run_dir) / f"probes/{int(attempt):03d}"
    folder.mkdir(parents=True, exist_ok=False)
    scene = folder / "scene.py"
    scene.write_text(source, encoding="utf-8")
    media = folder / "media"
    result = _run(
        _worker_args(scene, media, quality, "still", scene_name),
        cwd=folder,
        timeout=timeout,
        runner=runner,
    )
    (folder / "stdout.log").write_text(result.stdout or "", encoding="utf-8")
    (folder / "stderr.log").write_text(result.stderr or "", encoding="utf-8")
    _check(result, "Scene execution probe")
    frames = list((media / "images").rglob(f"{scene_name}*.png")) if (media / "images").is_dir() else []
    if not frames:
        frames = [path for path in media.rglob("*.png") if "partial_movie_files" not in path.parts]
    if len(frames) != 1:
        raise RuntimeError("Scene probe did not produce exactly one image")
    record = folder / "execution.json"
    record.write_text(
        json.dumps(
            {
                "kind": "actual_manim_final_frame_probe",
                "source_sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
                "delivery_quality": quality,
                "exit_code": result.returncode,
                "image": frames[0].relative_to(run_dir).as_posix(),
                "scene_name": scene_name,
                "limitations": ["Final still only; no continuous movie rendered or inspected."],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return record, frames[0]


def render(
    run_dir,
    source,
    quality,
    attempt,
    *,
    timeout=DEFAULT_RENDER_TIMEOUT,
    min_duration=DEFAULT_MIN_DURATION,
    max_duration=DEFAULT_MAX_DURATION,
    runner=None,
    contact_sheet=write_contact_sheet,
):
    scene_name = _screen(source)
    folder = Path(run_dir) / f"renders/{int(attempt):03d}"
    folder.mkdir(parents=True, exist_ok=False)
    scene = folder / "scene.py"
    scene.write_text(source, encoding="utf-8")
    media = folder / "media"
    proc = _run(
        _worker_args(scene, media, quality, "movie", scene_name),
        cwd=folder,
        timeout=timeout,
        runner=runner,
    )
    (folder / "stdout.log").write_text(proc.stdout or "", encoding="utf-8")
    (folder / "stderr.log").write_text(proc.stderr or "", encoding="utf-8")
    _check(proc, "Manim render")
    videos = [
        path
        for path in media.rglob(f"{scene_name}.mp4")
        if "partial_movie_files" not in path.parts
    ]
    if len(videos) != 1 or videos[0].stat().st_size < 1024:
        raise RuntimeError("Render did not produce a unique final MP4")
    video = videos[0]
    probe_text = _run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration:stream=width,height,r_frame_rate",
            "-of",
            "json",
            str(video),
        ],
        cwd=folder,
        timeout=TOOL_TIMEOUT,
        runner=runner,
    )
    metadata = json.loads(_check(probe_text, "ffprobe"))
    duration = duration_of(metadata)
    assert_duration(duration, min_duration, max_duration)
    frames: list[Path] = []
    for index in range(12):
        frame = folder / f"frame_{index:02d}.png"
        stamp = duration * (index + 0.5) / 12
        extracted = _run(
            [
                "ffmpeg",
                "-v",
                "error",
                "-y",
                "-ss",
                str(stamp),
                "-i",
                str(video),
                "-frames:v",
                "1",
                str(frame),
            ],
            cwd=folder,
            timeout=TOOL_TIMEOUT,
            runner=runner,
        )
        _check(extracted, f"frame {index:02d}")
        if not frame.is_file():
            raise RuntimeError("Frame extraction produced no image")
        frames.append(frame)
    sheet = contact_sheet(folder, frames, duration)
    (folder / "metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return video, frames, sheet
