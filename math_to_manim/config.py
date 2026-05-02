"""Runtime configuration for the Codex/OpenAI animation pipeline."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path


def load_env_file(path: Path = Path(".env")) -> None:
    """Load simple KEY=VALUE entries from a local .env without overwriting env."""

    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


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
    codegen_provider: str = "openai-agents"
    codex_command: str = "codex"
    codex_full_auto: bool = False
    codex_timeout_seconds: float = 900.0
    codex_workdir: Path | None = None

    @classmethod
    def from_env(cls) -> "RuntimeConfig":
        """Build config from environment variables with safe defaults."""

        load_env_file()
        codex_workdir = os.getenv("M2M2_CODEX_WORKDIR")
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
            codegen_provider=os.getenv("M2M2_CODEGEN_PROVIDER", os.getenv("M2M2_PROVIDER", "openai-agents")),
            codex_command=os.getenv("M2M2_CODEX_COMMAND", "codex"),
            codex_full_auto=os.getenv("M2M2_CODEX_FULL_AUTO", "0") in {"1", "true", "True"},
            codex_timeout_seconds=float(os.getenv("M2M2_CODEX_TIMEOUT_SECONDS", "900")),
            codex_workdir=Path(codex_workdir) if codex_workdir else None,
        )
