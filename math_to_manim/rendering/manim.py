"""Optional Manim CLI wrapper."""

from __future__ import annotations

from collections.abc import Sequence
import os
from pathlib import Path
import shlex
import subprocess
import sys

from .commands import ToolResult, resolve_binary


QUALITY_FLAGS = {
    "draft": "-ql",
    "l": "-ql",
    "low": "-ql",
    "m": "-qm",
    "medium": "-qm",
    "h": "-qh",
    "high": "-qh",
    "p": "-qp",
    "production": "-qp",
    "k": "-qk",
    "4k": "-qk",
}


def render_manim_scene(
    source_path: str | Path,
    *,
    scene_name: str | None = None,
    output_dir: str | Path | None = None,
    quality: str = "low",
    manim_bin: str = "manim",
    manim_command: Sequence[str] | str | None = None,
    timeout_seconds: float = 120.0,
    working_dir: str | Path | None = None,
    dry_run: bool = False,
) -> ToolResult:
    """Render a Manim scene with the local CLI if it is installed.

    Missing Manim is reported as a skipped result instead of an exception.
    """

    source = Path(source_path).resolve()
    flag = _quality_flag(quality)
    command_prefix = _resolve_manim_command(manim_bin=manim_bin, manim_command=manim_command)
    command = [*command_prefix, flag, str(source)]
    if scene_name:
        command.append(scene_name)
    if output_dir is not None:
        media_dir = Path(output_dir).resolve()
        media_dir.mkdir(parents=True, exist_ok=True)
        command.extend(["--media_dir", str(media_dir)])

    if not command_prefix:
        requested = _format_requested_commands(manim_bin=manim_bin, manim_command=manim_command)
        return ToolResult(False, True, tuple(command), reason=f"Manim command not found: {requested}")
    if dry_run:
        return ToolResult(True, True, tuple(command), reason="dry run", metadata={"quality": quality})
    if not source.exists():
        return ToolResult(False, True, tuple(command), reason=f"Scene source not found: {source}")

    try:
        completed = subprocess.run(
            command,
            cwd=str(working_dir) if working_dir is not None else None,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        return ToolResult(
            False,
            False,
            tuple(command),
            stdout=exc.stdout or "",
            stderr=exc.stderr or "",
            reason=f"Timed out after {timeout_seconds} seconds",
        )

    output_path = _discover_rendered_video(Path(output_dir) if output_dir is not None else None)
    return ToolResult(
        completed.returncode == 0,
        False,
        tuple(command),
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
        output_path=output_path,
    )


def _quality_flag(quality: str) -> str:
    if quality.startswith("-q"):
        return quality
    try:
        return QUALITY_FLAGS[quality]
    except KeyError as exc:
        valid = ", ".join(sorted(QUALITY_FLAGS))
        raise ValueError(f"Unknown Manim quality '{quality}'. Valid values: {valid}") from exc


def _discover_rendered_video(media_dir: Path | None) -> Path | None:
    if media_dir is None or not media_dir.exists():
        return None
    videos = [path for path in media_dir.rglob("*.mp4") if path.is_file()]
    if not videos:
        return None
    return max(videos, key=lambda path: path.stat().st_mtime)


def _resolve_manim_command(*, manim_bin: str, manim_command: Sequence[str] | str | None) -> tuple[str, ...]:
    for command in _candidate_manim_commands(manim_bin=manim_bin, manim_command=manim_command):
        resolved = _resolve_command_prefix(command)
        if resolved:
            return resolved
    return ()


def _candidate_manim_commands(
    *,
    manim_bin: str,
    manim_command: Sequence[str] | str | None,
) -> tuple[tuple[str, ...], ...]:
    if manim_command is not None:
        return (_normalize_command(manim_command),)
    if manim_bin == "manim":
        return ((manim_bin,), (sys.executable, "-m", "manim"))
    return ((manim_bin,),)


def _normalize_command(command: Sequence[str] | str) -> tuple[str, ...]:
    if isinstance(command, str):
        return tuple(shlex.split(command, posix=os.name != "nt"))
    return tuple(command)


def _resolve_command_prefix(command: tuple[str, ...]) -> tuple[str, ...] | None:
    if not command:
        return None
    binary = resolve_binary(command[0])
    if binary is None:
        return None
    return (binary, *command[1:])


def _format_requested_commands(*, manim_bin: str, manim_command: Sequence[str] | str | None) -> str:
    candidates = _candidate_manim_commands(manim_bin=manim_bin, manim_command=manim_command)
    return " or ".join(" ".join(command) for command in candidates)
