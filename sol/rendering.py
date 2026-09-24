"""Wrapper-owned Manim rendering and frame-evidence utilities."""

from __future__ import annotations

import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

try:
    import resource
except ImportError:  # pragma: no cover - Windows
    resource = None  # type: ignore[assignment]

_SCENE_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
_QUALITY = re.compile(r"^[lmhpk]$")


class RenderError(RuntimeError):
    pass


def resolve_inside(run_dir: Path, path: Path | str) -> Path:
    root = Path(run_dir).resolve()
    candidate = Path(path)
    resolved = candidate.resolve() if candidate.is_absolute() else (root / candidate).resolve()
    if resolved != root and root not in resolved.parents:
        raise RenderError(f"path escapes run directory: {path}")
    return resolved


def apply_resource_limits() -> None:
    """Best-effort CPU/address-space caps. See docs/security.md for residual risk."""
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


@dataclass(frozen=True)
class RenderOutcome:
    video_path: Path
    stdout_path: Path
    stderr_path: Path
    frame_paths: tuple[Path, ...]
    contact_sheet_path: Path | None


def build_manim_command(
    run_dir: Path,
    *,
    scene_name: str,
    quality: str,
) -> list[str]:
    if not _QUALITY.fullmatch(quality):
        raise RenderError(f"invalid Manim quality flag: {quality!r}")
    if not _SCENE_NAME.fullmatch(scene_name):
        raise RenderError(f"invalid scene class name: {scene_name!r}")
    root = Path(run_dir).resolve()
    media_dir = resolve_inside(root, root / "media")
    resolve_inside(root, root / "sol_scene.py")
    return [
        sys.executable,
        "-m",
        "manim",
        f"-q{quality}",
        "--media_dir",
        str(media_dir),
        "--progress_bar",
        "none",
        "sol_scene.py",
        scene_name,
    ]


def render_environment(
    run_dir: Path,
    base: dict[str, str] | None = None,
) -> dict[str, str]:
    run_dir = Path(run_dir)
    env = dict(os.environ if base is None else base)
    miktex = run_dir / ".miktex"
    paths = {
        "MIKTEX_USERCONFIG": miktex / "config",
        "MIKTEX_USERDATA": miktex / "data",
        "MIKTEX_USERINSTALL": miktex / "install",
    }
    for key, path in paths.items():
        path.mkdir(parents=True, exist_ok=True)
        env[key] = str(path)
    return env


def find_final_video(run_dir: Path) -> Path | None:
    candidates = [
        path
        for path in Path(run_dir).glob("**/*.mp4")
        if "partial_movie_files" not in {
            part.lower() for part in path.parts
        }
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda path: path.stat().st_mtime_ns)


def preflight_render() -> list[str]:
    checks = (
        ([sys.executable, "-c", "import manim; print(manim.__version__)"], "Manim"),
        (["ffmpeg", "-version"], "FFmpeg"),
        (["latex", "--version"], "LaTeX"),
    )
    versions: list[str] = []
    for command, label in checks:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30,
            check=False,
        )
        if completed.returncode:
            detail = (completed.stderr or completed.stdout).strip()[-1000:]
            raise RenderError(f"{label} preflight failed: {detail}")
        first_line = (completed.stdout or completed.stderr).strip().splitlines()
        versions.append(f"{label}: {first_line[0] if first_line else 'ready'}")
    return versions


def render_scene(
    run_dir: Path,
    *,
    scene_name: str,
    quality: str,
    timeout: float = 1200,
) -> RenderOutcome:
    run_dir = Path(run_dir)
    stdout_path = run_dir / "render_stdout.log"
    stderr_path = run_dir / "render_stderr.log"
    completed = subprocess.run(
        build_manim_command(run_dir, scene_name=scene_name, quality=quality),
        cwd=run_dir,
        env=render_environment(run_dir),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        check=False,
        preexec_fn=apply_resource_limits if resource is not None else None,
    )
    stdout_path.write_text(completed.stdout, encoding="utf-8")
    stderr_path.write_text(completed.stderr, encoding="utf-8")
    if completed.returncode:
        detail = "\n".join(
            part.strip()
            for part in (completed.stderr, completed.stdout)
            if part.strip()
        )[-6000:]
        raise RenderError(f"Manim failed with exit {completed.returncode}:\n{detail}")
    video = find_final_video(run_dir)
    if video is None or video.stat().st_size < 1024:
        raise RenderError("Manim completed without a valid final MP4")
    frames, contact_sheet = extract_review_frames(run_dir, video)
    return RenderOutcome(
        video_path=video,
        stdout_path=stdout_path,
        stderr_path=stderr_path,
        frame_paths=tuple(frames),
        contact_sheet_path=contact_sheet,
    )


def extract_review_frames(run_dir: Path, video_path: Path) -> tuple[list[Path], Path | None]:
    review_dir = Path(run_dir) / "review_frames"
    review_dir.mkdir(exist_ok=True)
    duration_result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(video_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    try:
        duration = float(duration_result.stdout.strip())
    except ValueError:
        return [], None
    timestamps = [duration * fraction for fraction in (0.08, 0.25, 0.42, 0.58, 0.75, 0.94)]
    frames: list[Path] = []
    for index, timestamp in enumerate(timestamps, start=1):
        frame = review_dir / f"frame_{index:02d}.png"
        completed = subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-ss",
                f"{timestamp:.3f}",
                "-i",
                str(video_path),
                "-frames:v",
                "1",
                str(frame),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode == 0 and frame.is_file():
            frames.append(frame)
    if not frames:
        return [], None
    contact_sheet = review_dir / "contact_sheet.png"
    completed = subprocess.run(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(video_path),
            "-vf",
            "fps=1/12,scale=480:-1,tile=3x2:padding=8:margin=8",
            "-frames:v",
            "1",
            str(contact_sheet),
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0 or not contact_sheet.is_file():
        contact_sheet = None
    return frames, contact_sheet
