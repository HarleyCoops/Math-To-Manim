"""Optional ffprobe and ffmpeg wrappers."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path
import subprocess
from typing import Any

from .commands import ToolResult, resolve_binary


@dataclass(frozen=True)
class VideoProbe:
    """Parsed ffprobe metadata for a video file."""

    ok: bool
    skipped: bool
    path: Path
    command: tuple[str, ...]
    returncode: int | None = None
    stdout: str = ""
    stderr: str = ""
    reason: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)
    duration_seconds: float | None = None
    width: int | None = None
    height: int | None = None
    frame_rate: float | None = None
    frame_count: int | None = None


def probe_video(
    video_path: str | Path,
    *,
    ffprobe_bin: str = "ffprobe",
    timeout_seconds: float = 30.0,
) -> VideoProbe:
    """Run ffprobe if available and return parsed metadata."""

    path = Path(video_path)
    binary = resolve_binary(ffprobe_bin)
    command = (
        binary or ffprobe_bin,
        "-v",
        "error",
        "-show_format",
        "-show_streams",
        "-of",
        "json",
        str(path),
    )

    if binary is None:
        return VideoProbe(False, True, path, command, reason=f"ffprobe binary not found: {ffprobe_bin}")
    if not path.exists():
        return VideoProbe(False, True, path, command, reason=f"Video file not found: {path}")

    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        return VideoProbe(
            False,
            False,
            path,
            command,
            stdout=exc.stdout or "",
            stderr=exc.stderr or "",
            reason=f"Timed out after {timeout_seconds} seconds",
        )

    if completed.returncode != 0:
        return VideoProbe(
            False,
            False,
            path,
            command,
            returncode=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
            reason="ffprobe failed",
        )

    try:
        raw = json.loads(completed.stdout or "{}")
    except json.JSONDecodeError:
        return VideoProbe(
            False,
            False,
            path,
            command,
            returncode=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
            reason="ffprobe returned invalid JSON",
        )

    parsed = _parse_video_probe(raw)
    return VideoProbe(
        True,
        False,
        path,
        command,
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
        raw=raw,
        **parsed,
    )


def extract_frame(
    video_path: str | Path,
    output_path: str | Path,
    *,
    timestamp_seconds: float = 0.0,
    ffmpeg_bin: str = "ffmpeg",
    timeout_seconds: float = 30.0,
    overwrite: bool = True,
) -> ToolResult:
    """Extract one frame from a video if ffmpeg is available."""

    video = Path(video_path)
    output = Path(output_path)
    binary = resolve_binary(ffmpeg_bin)
    command = [
        binary or ffmpeg_bin,
        "-y" if overwrite else "-n",
        "-ss",
        f"{timestamp_seconds:.3f}",
        "-i",
        str(video),
        "-frames:v",
        "1",
        str(output),
    ]

    if binary is None:
        return ToolResult(False, True, tuple(command), output_path=output, reason=f"ffmpeg binary not found: {ffmpeg_bin}")
    if not video.exists():
        return ToolResult(False, True, tuple(command), output_path=output, reason=f"Video file not found: {video}")

    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        completed = subprocess.run(
            command,
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
            output_path=output,
        )

    return ToolResult(
        completed.returncode == 0 and output.exists(),
        False,
        tuple(command),
        returncode=completed.returncode,
        stdout=completed.stdout,
        stderr=completed.stderr,
        output_path=output,
        reason=None if completed.returncode == 0 else "ffmpeg failed",
    )


def _parse_video_probe(raw: dict[str, Any]) -> dict[str, Any]:
    streams = raw.get("streams") if isinstance(raw.get("streams"), list) else []
    video_stream = next((stream for stream in streams if stream.get("codec_type") == "video"), {})
    format_info = raw.get("format") if isinstance(raw.get("format"), dict) else {}

    duration = _float_or_none(video_stream.get("duration")) or _float_or_none(format_info.get("duration"))
    return {
        "duration_seconds": duration,
        "width": _int_or_none(video_stream.get("width")),
        "height": _int_or_none(video_stream.get("height")),
        "frame_rate": _parse_frame_rate(video_stream.get("avg_frame_rate") or video_stream.get("r_frame_rate")),
        "frame_count": _int_or_none(video_stream.get("nb_frames")),
    }


def _parse_frame_rate(value: Any) -> float | None:
    if value in (None, "0/0"):
        return None
    if isinstance(value, str) and "/" in value:
        numerator, denominator = value.split("/", 1)
        denominator_value = _float_or_none(denominator)
        if not denominator_value:
            return None
        numerator_value = _float_or_none(numerator)
        return None if numerator_value is None else numerator_value / denominator_value
    return _float_or_none(value)


def _float_or_none(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _int_or_none(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
