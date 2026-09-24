"""Bounded Manim subprocess rendering with typed failure attribution."""

from __future__ import annotations

import json
import os
import re
import subprocess
from pathlib import Path
from typing import Literal, Protocol

from pydantic import Field

from .schemas import NonEmpty, Sha256, StrictFrozenModel

RenderRole = Literal["baseline", "candidate"]


class ProcessResult(StrictFrozenModel):
    returncode: int | None
    stdout: str
    stderr: str
    timed_out: bool


class ProcessRunner(Protocol):
    def run(
        self,
        args: tuple[str, ...],
        *,
        cwd: Path,
        timeout_seconds: float,
        env: dict[str, str],
    ) -> ProcessResult: ...


class SubprocessRunner:
    """Production process boundary; tests replace only this external edge."""

    def run(
        self,
        args: tuple[str, ...],
        *,
        cwd: Path,
        timeout_seconds: float,
        env: dict[str, str],
    ) -> ProcessResult:
        process_env = os.environ.copy()
        process_env.update(env)
        try:
            completed = subprocess.run(
                list(args),
                cwd=cwd,
                env=process_env,
                text=True,
                capture_output=True,
                timeout=timeout_seconds,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            return ProcessResult(
                returncode=None,
                stdout=_coerce_output(exc.stdout),
                stderr=_coerce_output(exc.stderr),
                timed_out=True,
            )
        return ProcessResult(
            returncode=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
            timed_out=False,
        )


def _coerce_output(value: str | bytes | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


class RenderSettings(StrictFrozenModel):
    manim_command: tuple[NonEmpty, ...] = ("python", "-m", "manim")
    width: int = Field(default=854, gt=0)
    height: int = Field(default=480, gt=0)
    fps: int = Field(default=15, gt=0)
    quality: Literal["l", "m", "h", "p", "k"] = "l"
    timeout_seconds: float = Field(default=180.0, gt=0)
    max_log_chars: int = Field(default=8_000, gt=0)
    environment: dict[str, str] = {}


class RenderRequest(StrictFrozenModel):
    task_id: NonEmpty
    source_code: str = Field(min_length=1)
    scene_name: NonEmpty
    role: RenderRole
    output_dir: Path


class RenderOutcome(StrictFrozenModel):
    status: Literal["completed"]
    task_id: NonEmpty
    role: RenderRole
    video_path: Path
    command: tuple[str, ...]
    source_sha256: Sha256
    stdout: str
    stderr: str


class CandidateRenderError(ValueError):
    """Candidate code caused a zero-reward render outcome."""


class InfrastructureRenderError(RuntimeError):
    """The render platform failed independently of candidate quality."""


_SECRET_PATTERN = re.compile(
    r"(?i)\b([a-z0-9_-]*(?:api[_-]?key|authorization|password|secret|token)"
    r"[a-z0-9_-]*)(\s*[:=]\s*)([^\r\n]+)"
)


def redact_and_truncate_log(value: str, *, max_chars: int) -> str:
    redacted = _SECRET_PATTERN.sub(
        lambda match: f"{match.group(1)}{match.group(2)}[REDACTED]",
        value,
    )
    if len(redacted) <= max_chars:
        return redacted
    return redacted[:max_chars] + "\n...[truncated]"


def write_json_atomic(path: Path, payload: object) -> None:
    """Atomically replace a JSON artifact with deterministic formatting."""

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def _write_source_atomic(path: Path, source: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(source, encoding="utf-8")
    temporary.replace(path)


def parse_ffprobe_duration(output: str) -> float:
    try:
        payload = json.loads(output)
        duration = float(payload["format"]["duration"])
    except (KeyError, TypeError, ValueError, json.JSONDecodeError):
        raise InfrastructureRenderError("ffprobe returned an invalid duration") from None
    if duration < 0:
        raise InfrastructureRenderError("ffprobe returned an invalid duration")
    return duration


class Renderer:
    def __init__(
        self,
        *,
        runner: ProcessRunner,
        settings: RenderSettings | None = None,
    ):
        self.runner = runner
        self.settings = settings or RenderSettings()

    def _command(self, request: RenderRequest, source_path: Path) -> tuple[str, ...]:
        media_dir = request.output_dir / "media"
        return (
            *self.settings.manim_command,
            f"-q{self.settings.quality}",
            "-r",
            f"{self.settings.width},{self.settings.height}",
            "--fps",
            str(self.settings.fps),
            "--format",
            "mp4",
            "--media_dir",
            str(media_dir),
            str(source_path),
            request.scene_name,
        )

    def render(self, request: RenderRequest) -> RenderOutcome:
        output_dir = request.output_dir.resolve()
        output_dir.mkdir(parents=True, exist_ok=True)
        source_path = output_dir / "scene.py"
        _write_source_atomic(source_path, request.source_code)
        command = self._command(request, source_path)
        try:
            result = self.runner.run(
                command,
                cwd=output_dir,
                timeout_seconds=self.settings.timeout_seconds,
                env=dict(self.settings.environment),
            )
        except FileNotFoundError as exc:
            raise InfrastructureRenderError(
                f"render executable is unavailable: {exc}"
            ) from None
        except OSError as exc:
            raise InfrastructureRenderError(
                f"render process could not start: {exc}"
            ) from None

        stdout = redact_and_truncate_log(
            result.stdout,
            max_chars=self.settings.max_log_chars,
        )
        stderr = redact_and_truncate_log(
            result.stderr,
            max_chars=self.settings.max_log_chars,
        )
        if result.timed_out:
            message = (
                f"{request.role} render timed out after "
                f"{self.settings.timeout_seconds:g}s"
            )
            if request.role == "candidate":
                raise CandidateRenderError(message)
            raise InfrastructureRenderError(message)
        if result.returncode != 0:
            message = (
                f"{request.role} render failed with exit code "
                f"{result.returncode}: {stderr or stdout}"
            )
            if request.role == "candidate":
                raise CandidateRenderError(message)
            raise InfrastructureRenderError(message)

        videos = sorted((output_dir / "media").rglob("*.mp4"))
        if len(videos) != 1:
            raise InfrastructureRenderError(
                "successful render did not produce exactly one MP4"
            )
        digest = __import__("hashlib").sha256(
            request.source_code.encode("utf-8")
        ).hexdigest()
        return RenderOutcome(
            status="completed",
            task_id=request.task_id,
            role=request.role,
            video_path=videos[0].resolve(),
            command=command,
            source_sha256=digest,
            stdout=stdout,
            stderr=stderr,
        )


__all__ = [
    "CandidateRenderError",
    "InfrastructureRenderError",
    "ProcessResult",
    "RenderOutcome",
    "RenderRequest",
    "RenderSettings",
    "Renderer",
    "SubprocessRunner",
    "parse_ffprobe_duration",
    "redact_and_truncate_log",
    "write_json_atomic",
]
