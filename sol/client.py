"""Non-interactive Codex CLI driver using cached ChatGPT authentication."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

from sol.models import CodexRunResult

DEFAULT_MODEL = os.getenv("M2M_SOL_MODEL", "gpt-5.6-sol")
DEFAULT_REASONING_EFFORT = os.getenv("M2M_SOL_REASONING", "high")
DEFAULT_TIMEOUT = float(os.getenv("M2M_SOL_TIMEOUT", "3600"))
DEFAULT_COMMAND = os.getenv("M2M_SOL_CODEX", "codex")


class CodexCliError(RuntimeError):
    pass


class CodexCli:
    def __init__(
        self,
        *,
        command: str = DEFAULT_COMMAND,
        model: str = DEFAULT_MODEL,
        reasoning_effort: str = DEFAULT_REASONING_EFFORT,
        timeout: float = DEFAULT_TIMEOUT,
    ):
        self.command = command
        self.model = model
        self.reasoning_effort = reasoning_effort
        self.timeout = timeout

    def resolve(self) -> str:
        resolved = shutil.which(self.command)
        if not resolved:
            raise CodexCliError(
                f"Codex CLI command {self.command!r} was not found. Install Codex, "
                "run `codex login`, and retry."
            )
        return resolved

    def build_command(self, *, cwd: Path, schema_path: Path, output_path: Path) -> list[str]:
        return [
            self.resolve(),
            "-c", f'model_reasoning_effort="{self.reasoning_effort}"',
            "exec",
            "--model", self.model,
            "--sandbox", "workspace-write",
            "--cd", str(cwd),
            "--json",
            "--output-schema", str(schema_path),
            "--output-last-message", str(output_path),
            "-",
        ]

    def run(
        self,
        prompt: str,
        *,
        cwd: Path,
        schema_path: Path,
        output_path: Path,
        trace_path: Path,
    ) -> CodexRunResult:
        command = self.build_command(cwd=cwd, schema_path=schema_path, output_path=output_path)
        # A stray API key would silently switch billing/auth modes. This silo is
        # deliberately ChatGPT-login-only, so remove it from the child process.
        env = {key: value for key, value in os.environ.items() if key != "OPENAI_API_KEY"}
        completed = subprocess.run(
            command,
            input=prompt,
            text=True,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            env=env,
            timeout=self.timeout,
            check=False,
        )
        trace_path.write_text(completed.stdout, encoding="utf-8")
        if completed.returncode != 0:
            streams = [part.strip() for part in (completed.stderr, completed.stdout) if part.strip()]
            detail = "\n".join(streams)[-6000:]
            raise CodexCliError(
                f"Codex CLI failed with exit {completed.returncode}. "
                "Inspect the preserved trace and diagnostics below; run `codex login` "
                "only if they identify an authentication failure.\n"
                f"{detail}"
            )
        if not output_path.is_file():
            raise CodexCliError("Codex CLI completed without writing its structured final message")
        try:
            return CodexRunResult.model_validate_json(output_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, ValueError) as exc:
            raise CodexCliError("Codex CLI returned an invalid final result") from exc
