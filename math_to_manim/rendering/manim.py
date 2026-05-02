"""Optional Manim CLI wrapper."""

from __future__ import annotations

from pathlib import Path
import subprocess

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
    timeout_seconds: float = 120.0,
    working_dir: str | Path | None = None,
    dry_run: bool = False,
) -> ToolResult:
    """Render a Manim scene with the local CLI if it is installed.

    Missing Manim is reported as a skipped result instead of an exception.
    """

    source = Path(source_path).resolve()
    binary = resolve_binary(manim_bin)
    flag = _quality_flag(quality)
    command = [binary or manim_bin, flag, str(source)]
    if scene_name:
        command.append(scene_name)
    if output_dir is not None:
        media_dir = Path(output_dir).resolve()
        media_dir.mkdir(parents=True, exist_ok=True)
        command.extend(["--media_dir", str(media_dir)])

    if binary is None:
        return ToolResult(False, True, tuple(command), reason=f"Manim binary not found: {manim_bin}")
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
