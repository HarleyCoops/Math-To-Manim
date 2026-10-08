"""Headless Grok Build CLI backend.

This wraps the installed `grok` command and a cached `grok login` session.
It does not implement an OAuth client. When no session file is present, the
CLI's own precedence can still use XAI_API_KEY from the environment. The key
is never placed on the command line and never printed.

The CLI flags below are the headless flags documented for Grok Build. Exact
acceptance of each flag was not verified in this offline change.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

from grok.client import XAIClientError, api_key_status, redact_secret
from grok.jsonutil import extract_json_object
from grok.models import StageCallResult

DEFAULT_MAX_TURNS = 4


def auth_file() -> Path:
    override = os.getenv("GROK_AUTH_FILE", "").strip()
    if override:
        return Path(override)
    return Path.home() / ".grok" / "auth.json"


def cached_login_present(path: Path | None = None) -> bool:
    """True when a login file exists. The file contents are never read."""
    target = path or auth_file()
    try:
        return target.is_file() and target.stat().st_size > 2
    except OSError:
        return False


def auth_source_for(backend: str) -> str:
    login = cached_login_present()
    key_ok, _detail = api_key_status()
    if backend == "grok-build":
        if login:
            return "grok-login"
        if key_ok:
            return "xai-api-key"
        return "none"
    if key_ok:
        return "xai-api-key"
    return "none"


def describe_auth(backend: str) -> dict[str, str]:
    key_ok, key_detail = api_key_status()
    return {
        "backend": backend,
        "auth_source": auth_source_for(backend),
        "grok_login": "cached" if cached_login_present() else "absent",
        "xai_api_key": "set" if key_ok else "absent",
        "key_detail": "XAI_API_KEY is set" if key_ok else key_detail,
    }


def grok_binary() -> str | None:
    return shutil.which("grok")


def login_command(*, device_auth: bool = False, binary: str | None = None) -> list[str]:
    executable = binary or grok_binary()
    if not executable:
        raise XAIClientError("grok CLI is not installed")
    command = [executable, "login"]
    if device_auth:
        command.append("--device-auth")
    return command


def build_grok_argv(
    *,
    binary: str,
    prompt: str,
    model: str,
    effort: str,
    system_prompt: str,
    cwd: str,
    max_turns: int = DEFAULT_MAX_TURNS,
) -> list[str]:
    return [
        binary,
        "-p",
        prompt,
        "-m",
        model,
        "--effort",
        effort,
        "--output-format",
        "json",
        "--no-auto-update",
        "--max-turns",
        str(max_turns),
        "--system-prompt-override",
        system_prompt,
        "--cwd",
        cwd,
        "--sandbox",
        "read-only",
        "--no-subagents",
        "--always-approve",
        "--disable-web-search",
    ]


def parse_cli_output(stdout: str) -> str:
    text = (stdout or "").strip()
    if not text:
        raise XAIClientError("grok CLI returned empty output")
    candidates = [text]
    lines = [line for line in text.splitlines() if line.strip()]
    if len(lines) > 1:
        candidates.append(lines[-1])
    for candidate in candidates:
        try:
            data = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        if isinstance(data, str) and data.strip():
            return data
        if isinstance(data, dict):
            for key in ("response", "content", "text", "message", "output_text"):
                value = data.get(key)
                if isinstance(value, str) and value.strip():
                    return value
            return json.dumps(data)
    return text


class GrokBuildBackend:
    """Subprocess backend. Schema enforcement is validate-and-retry in the harness."""

    name = "grok-build"

    def __init__(
        self,
        *,
        model: str,
        reasoning_effort: str = "high",
        binary: str | None = None,
        runner=None,
        timeout: float | None = None,
        api_key: str | None = None,
    ):
        self.model = model
        self.reasoning_effort = reasoning_effort
        self.binary = binary or grok_binary() or "grok"
        self.runner = runner or subprocess.run
        self.timeout = float(os.getenv("XAI_TIMEOUT", "900")) if timeout is None else timeout
        self.api_key = api_key if api_key is not None else os.getenv("XAI_API_KEY", "")
        self.capability_warnings: list[str] = []

    def require_auth(self) -> str:
        source = auth_source_for("grok-build")
        if source == "none":
            raise XAIClientError("grok login session and XAI_API_KEY are both missing")
        return source

    def complete(
        self,
        *,
        instructions: str,
        text: str,
        tools: list[dict] | tuple[dict, ...] = (),
        image_path: Path | None = None,
        image_paths: list[Path] | tuple[Path, ...] | None = None,
        tool_choice: str | dict | None = None,
        function_handlers: dict | None = None,
        schema: dict | None = None,
        schema_name: str | None = None,
        prompt_cache_key: str | None = None,
        max_function_rounds: int = 4,
        cwd: Path | None = None,
    ) -> StageCallResult:
        del tool_choice, function_handlers, max_function_rounds
        source = self.require_auth()
        work = Path(cwd or Path.cwd())
        prompt = _prompt(
            text,
            tools=tools,
            schema=schema,
            image_path=image_path,
            image_paths=image_paths,
            prompt_cache_key=prompt_cache_key,
        )
        command = build_grok_argv(
            binary=self.binary,
            prompt=prompt,
            model=self.model,
            effort=self.reasoning_effort,
            system_prompt=instructions,
            cwd=str(work),
        )
        result = self.runner(
            command,
            cwd=str(work),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=self.timeout,
            env=os.environ.copy(),
        )
        stdout = redact_secret(getattr(result, "stdout", "") or "", self.api_key)
        stderr = redact_secret(getattr(result, "stderr", "") or "", self.api_key)
        if getattr(result, "returncode", 1) != 0:
            raise XAIClientError(f"grok CLI failed ({result.returncode}): {stderr[-2000:]}")
        final_text = parse_cli_output(stdout)
        try:
            payload = extract_json_object(final_text)
        except (ValueError, json.JSONDecodeError):
            payload = {"raw_text": final_text}
        warnings = [f"grok-build auth_source={source}"]
        if tools:
            warnings.append("grok-build backend does not attach xAI server tools; JSON is validated locally")
        self.capability_warnings = warnings
        return StageCallResult(
            text=final_text,
            payload=payload,
            warnings=warnings,
            raw={"auth_source": source, "returncode": 0},
        )


def _prompt(
    text: str,
    *,
    tools,
    schema,
    image_path,
    image_paths,
    prompt_cache_key,
) -> str:
    parts = [text]
    if prompt_cache_key:
        parts.append(f"\nCache key: {prompt_cache_key}")
    if tools:
        kinds = [tool.get("type") or tool.get("name") for tool in tools]
        parts.append(
            "\nThis headless login session cannot call xAI server tools "
            f"({', '.join(str(kind) for kind in kinds)}). "
            "Return one JSON object for the charter."
        )
    images = []
    if image_path is not None:
        images.append(image_path)
    images.extend(image_paths or [])
    if images:
        listed = "\n".join(str(path) for path in images)
        parts.append(
            "\nImage paths (CLI image attachment is not used; cite these filenames):\n" + listed
        )
    if schema is not None:
        parts.append(
            "\nReturn one JSON object matching this JSON schema:\n" + json.dumps(schema)
        )
    return "\n".join(parts)
