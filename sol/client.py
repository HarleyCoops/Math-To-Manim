"""Non-interactive Codex CLI driver using cached ChatGPT authentication."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import threading
from pathlib import Path
from typing import Callable

from sol.models import CodexRunResult

DEFAULT_MODEL = os.getenv("M2M_SOL_MODEL", "gpt-5.6-sol")
DEFAULT_REASONING_EFFORT = os.getenv("M2M_SOL_REASONING", "high")
DEFAULT_TIMEOUT = float(os.getenv("M2M_SOL_TIMEOUT", "3600"))
DEFAULT_COMMAND = os.getenv("M2M_SOL_CODEX", "codex")
FAST_SERVICE_TIER = 'service_tier="fast"'


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

    def build_command(
        self,
        *,
        cwd: Path,
        schema_path: Path,
        output_path: Path,
        session_id: str | None = None,
    ) -> list[str]:
        command = [
            self.resolve(),
            "-c", FAST_SERVICE_TIER,
            "-c", f'model_reasoning_effort="{self.reasoning_effort}"',
            "exec",
        ]
        if session_id:
            command.extend(["resume", session_id])
        command.extend([
            "--model", self.model,
            "--sandbox", "workspace-write",
            "--cd", str(cwd),
            "--json",
            "--output-schema", str(schema_path),
            "--output-last-message", str(output_path),
            "-",
        ])
        return command

    def run(
        self,
        prompt: str,
        *,
        cwd: Path,
        schema_path: Path,
        output_path: Path,
        trace_path: Path,
        event_sink: Callable[[dict], None] | None = None,
        session_id: str | None = None,
    ) -> CodexRunResult:
        command = self.build_command(
            cwd=cwd,
            schema_path=schema_path,
            output_path=output_path,
            session_id=session_id,
        )
        # A stray API key would silently switch billing/auth modes. This silo is
        # deliberately ChatGPT-login-only, so remove it from the child process.
        env = {key: value for key, value in os.environ.items() if key != "OPENAI_API_KEY"}
        process = subprocess.Popen(
            command,
            text=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8",
            errors="replace",
            env=env,
        )
        if process.stdin is None or process.stdout is None or process.stderr is None:
            process.kill()
            raise CodexCliError("Codex CLI did not expose the required process streams")

        stderr_parts: list[str] = []
        reader_errors: list[Exception] = []

        def read_stdout() -> None:
            try:
                with trace_path.open("w", encoding="utf-8") as trace:
                    for line in process.stdout:
                        trace.write(line)
                        trace.flush()
                        if event_sink is None:
                            continue
                        try:
                            event = json.loads(line)
                        except json.JSONDecodeError:
                            continue
                        if isinstance(event, dict):
                            event_sink(event)
            except Exception as exc:  # surfaced after both streams are drained
                reader_errors.append(exc)

        def read_stderr() -> None:
            try:
                stderr_parts.extend(process.stderr)
            except Exception as exc:  # surfaced after both streams are drained
                reader_errors.append(exc)

        stdout_thread = threading.Thread(target=read_stdout, daemon=True)
        stderr_thread = threading.Thread(target=read_stderr, daemon=True)
        stdout_thread.start()
        stderr_thread.start()
        process.stdin.write(prompt)
        process.stdin.close()
        try:
            returncode = process.wait(timeout=self.timeout)
        except subprocess.TimeoutExpired as exc:
            process.kill()
            process.wait()
            stdout_thread.join()
            stderr_thread.join()
            raise CodexCliError(
                f"Codex CLI exceeded the {self.timeout:g}-second timeout"
            ) from exc
        stdout_thread.join()
        stderr_thread.join()
        if reader_errors:
            raise CodexCliError(f"Codex CLI stream reader failed: {reader_errors[0]}")
        if returncode != 0:
            stdout = trace_path.read_text(encoding="utf-8") if trace_path.is_file() else ""
            stderr = "".join(stderr_parts)
            streams = [part.strip() for part in (stderr, stdout) if part.strip()]
            detail = "\n".join(streams)[-6000:]
            raise CodexCliError(
                f"Codex CLI failed with exit {returncode}. "
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
