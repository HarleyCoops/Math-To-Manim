"""Shared subprocess result helpers."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
import shutil


@dataclass(frozen=True)
class ToolResult:
    """Common result for optional local binary wrappers."""

    ok: bool
    skipped: bool
    command: tuple[str, ...]
    returncode: int | None = None
    stdout: str = ""
    stderr: str = ""
    reason: str | None = None
    output_path: Path | None = None
    metadata: Mapping[str, object] = field(default_factory=dict)


def resolve_binary(binary: str) -> str | None:
    """Return an executable path or ``None`` without raising."""

    candidate = Path(binary)
    if candidate.is_absolute() or len(candidate.parts) > 1:
        return str(candidate) if candidate.exists() else None
    return shutil.which(binary)
