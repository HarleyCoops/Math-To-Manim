"""Runtime configuration for the Codex/OpenAI animation pipeline."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path


@dataclass(frozen=True)
class RuntimeConfig:
    """Configuration shared by agents, tools, and pipeline stages."""

    model: str = "gpt-5.5"
    runs_dir: Path = Path("runs")
    default_quality: str = "l"
    max_static_repairs: int = 3
    max_render_repairs: int = 3
    max_visual_repairs: int = 2
    render_timeout_seconds: float = 900.0
    trace_enabled: bool = True
    deterministic: bool = False

    @classmethod
    def from_env(cls) -> "RuntimeConfig":
        """Build config from environment variables with safe defaults."""

        return cls(
            model=os.getenv("M2M2_MODEL", os.getenv("OPENAI_MODEL", "gpt-5.5")),
            runs_dir=Path(os.getenv("M2M2_RUNS_DIR", "runs")),
            default_quality=os.getenv("M2M2_MANIM_QUALITY", "l"),
            max_static_repairs=int(os.getenv("M2M2_MAX_STATIC_REPAIRS", "3")),
            max_render_repairs=int(os.getenv("M2M2_MAX_RENDER_REPAIRS", "3")),
            max_visual_repairs=int(os.getenv("M2M2_MAX_VISUAL_REPAIRS", "2")),
            render_timeout_seconds=float(os.getenv("M2M2_RENDER_TIMEOUT_SECONDS", "900")),
            trace_enabled=os.getenv("M2M2_TRACE", "1") not in {"0", "false", "False"},
            deterministic=os.getenv("M2M2_DETERMINISTIC", "0") in {"1", "true", "True"},
        )
