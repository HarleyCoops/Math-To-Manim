"""Non-interactive Codex CLI driver using cached ChatGPT authentication.

Everything about how Codex is invoked lives here: executable discovery, the
service-tier override, the OPENAI_API_KEY scrub, structured output flags.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import threading
from pathlib import Path
from typing import Callable

from pydantic import BaseModel

FAST_SERVICE_TIER = 'service_tier="fast"'
SANDBOXES = ("read-only", "workspace-write")


def default_codex_command() -> str:
    """M2M_SOL_CODEX, else the npm-pinned Codex under the current checkout, else PATH."""
    configured = os.getenv("M2M_SOL_CODEX")
    if configured:
        return configured
    local = Path.cwd() / "node_modules" / ".bin" / ("codex.cmd" if os.name == "nt" else "codex")
    return str(local) if local.is_file() else "codex"


def default_model() -> str:
    return os.getenv("M2M_SOL_MODEL", "gpt-6-astra")


def default_timeout() -> float:
    return float(os.getenv("M2M_SOL_TIMEOUT", "3600"))


def codex_env() -> dict[str, str]:
    # A stray API key would silently switch billing/auth modes. This silo is
    # deliberately ChatGPT-login-only, so remove it from the child process.
    return {key: value for key, value in os.environ.items() if key != "OPENAI_API_KEY"}


class CodexCliError(RuntimeError):
    pass


class CodexCli:
    def __init__(
        self,
        *,
        command: str | None = None,
        model: str | None = None,
        timeout: float | None = None,
        sandbox: str = "workspace-write",
    ):
        self.command = command or default_codex_command()
        self.model = model or default_model()
        self.timeout = default_timeout() if timeout is None else timeout
        if sandbox not in SANDBOXES:
            raise ValueError("unsupported Codex sandbox")
        self.sandbox = sandbox

    def resolve(self) -> str:
        resolved = shutil.which(self.command)
        if not resolved:
            raise CodexCliError(
                f"Codex CLI command {self.command!r} was not found. Install Codex, "
                "run `codex login`, and retry."
            )
        return resolved

    def _base_command(self) -> list[str]:
        # The fast tier override also shadows an invalid global service_tier
        # setting that would otherwise stop Codex before any subcommand runs.
        return [self.resolve(), "-c", FAST_SERVICE_TIER]

    def check_login(self) -> tuple[bool, list[str]]:
        """Whether Codex runs and holds a ChatGPT login, plus the two status lines.

        Raises CodexCliError when the executable cannot be found at all.
        """
        version = subprocess.run(
            [self.resolve(), "--version"],
            capture_output=True, text=True, env=codex_env(), check=False,
        )
        login = subprocess.run(
            [*self._base_command(), "login", "status"],
            capture_output=True, text=True, env=codex_env(), check=False,
        )
        lines = [(version.stdout or version.stderr).strip(), (login.stdout or login.stderr).strip()]
        return not (version.returncode or login.returncode), lines

    def build_command(
        self,
        *,
        cwd: Path,
        schema_path: Path,
        output_path: Path,
        reasoning_effort: str,
        session_id: str | None = None,
        image_paths: list[Path] | None = None,
    ) -> list[str]:
        command = [
            *self._base_command(),
            "-c", f'model_reasoning_effort="{reasoning_effort}"',
            "exec",
            "--sandbox", self.sandbox,
            "--cd", str(cwd),
        ]
        if session_id:
            command.extend(["resume", session_id])
        command.extend(["--model", self.model, "--json", "--output-schema", str(schema_path),
                        "--output-last-message", str(output_path)])
        for path in image_paths or []:
            command.extend(["--image", str(path)])
        command.append("-")
        return command

    def run(
        self,
        prompt: str,
        *,
        cwd: Path,
        schema_path: Path,
        output_path: Path,
        trace_path: Path,
        reasoning_effort: str,
        result_model: type[BaseModel],
        event_sink: Callable[[dict], None] | None = None,
        session_id: str | None = None,
        image_paths: list[Path] | None = None,
    ) -> BaseModel:
        command = self.build_command(
            cwd=cwd,
            schema_path=schema_path,
            output_path=output_path,
            reasoning_effort=reasoning_effort,
            session_id=session_id,
            image_paths=image_paths,
        )
        process = subprocess.Popen(
            command,
            text=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8",
            errors="replace",
            env=codex_env(),
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
            return result_model.model_validate_json(output_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, ValueError) as exc:
            raise CodexCliError("Codex CLI returned an invalid final result") from exc
