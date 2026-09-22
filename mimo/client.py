"""MiMo 2.6 tool-calling client (OpenAI-compatible chat/completions).

Endpoint defaults to the MiMoCode OpenAI-compatible /v1 surface. The API key
is resolved from MIMO_API_KEY / MIMO_CODE_API_KEY and is never printed.
This module never imports Mythos, Sol, Grok, or GLM.
"""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from mimo.jsonutil import extract_json_object
from mimo.models import StageRunResult, ToolCallRecord
from mimo.tools import ToolContext, dispatch_tool

DEFAULT_BASE_URL = os.getenv("MIMO_BASE_URL", "http://127.0.0.1:8642/v1")
DEFAULT_MODEL = os.getenv("MIMO_MODEL", "mimo-2.6")
DEFAULT_REASONING_EFFORT = os.getenv("MIMO_REASONING_EFFORT", "high")
DEFAULT_TIMEOUT = float(os.getenv("MIMO_TIMEOUT", "600"))
PING_TIMEOUT = 20.0
MAX_TOOL_ROUNDS = int(os.getenv("MIMO_MAX_TOOL_ROUNDS", "8"))

_EFFORT_TOKENS = {
    "low": 2_000,
    "medium": 4_000,
    "high": 8_000,
    "xhigh": 12_000,
    "max": 16_000,
}


class MimoClientError(RuntimeError):
    pass


def redact_secret(text: str, secret: str | None) -> str:
    if not text or not secret or not secret.strip():
        return text
    return text.replace(secret.strip(), "[redacted]")


def resolve_api_key(env: dict | None = None) -> tuple[str | None, str | None]:
    source = env if env is not None else os.environ
    for name in ("MIMO_API_KEY", "MIMO_CODE_API_KEY"):
        value = source.get(name)
        if value and value.strip():
            return value.strip(), name
    return None, None


def api_key_status(env: dict | None = None) -> tuple[bool, str]:
    key, origin = resolve_api_key(env)
    if not key:
        return False, (
            "no MiMo key found; set MIMO_API_KEY. Offline mode works without a key."
        )
    return True, f"a MiMo key is set (source: {origin})"


class MimoClient:
    """Sync OpenAI-compatible chat/completions client with a tool loop."""

    def __init__(
        self,
        *,
        model: str = DEFAULT_MODEL,
        base_url: str = DEFAULT_BASE_URL,
        reasoning_effort: str = DEFAULT_REASONING_EFFORT,
        timeout: float = DEFAULT_TIMEOUT,
        api_key: str | None = None,
    ):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.reasoning_effort = reasoning_effort
        self.timeout = timeout
        resolved, origin = resolve_api_key()
        if api_key is not None and api_key.strip():
            resolved, origin = api_key.strip(), "explicit"
        self.api_key = resolved
        self.key_source = origin

    @property
    def endpoint(self) -> str:
        return f"{self.base_url}/chat/completions"

    def _headers(self) -> dict:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _post(self, body: dict, timeout: float | None = None) -> dict:
        request = urllib.request.Request(
            self.endpoint,
            data=json.dumps(body).encode("utf-8"),
            headers=self._headers(),
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout or self.timeout) as response:
                raw = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise MimoClientError(
                f"MiMo HTTP {exc.code}: {redact_secret(detail, self.api_key)}"
            ) from exc
        except urllib.error.URLError as exc:
            raise MimoClientError(f"MiMo unreachable: {exc.reason}") from exc
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            raise MimoClientError("MiMo returned non-JSON") from exc

    def ping(self) -> str:
        body = {
            "model": self.model,
            "messages": [{"role": "user", "content": "Reply with the single word pong."}],
            "max_tokens": 8,
            "temperature": 0,
        }
        payload = self._post(body, timeout=PING_TIMEOUT)
        try:
            return payload["choices"][0]["message"]["content"] or ""
        except (KeyError, IndexError, TypeError) as exc:
            raise MimoClientError("unexpected ping shape") from exc

    def run_stage(
        self,
        *,
        stage_name: str,
        prompt: str,
        tools: tuple[dict, ...],
        ctx: ToolContext,
        expected_summary_keys: tuple[str, ...],
    ) -> StageRunResult:
        """Drive one specialist with a bounded tool-calling loop."""
        messages: list[dict[str, Any]] = [
            {
                "role": "system",
                "content": (
                    f"MiMo 2.6 Math-To-Manim specialist: {stage_name}. "
                    "Use tools to write artifacts. Finish with one JSON object "
                    f"containing keys: {', '.join(expected_summary_keys)}."
                ),
            },
            {"role": "user", "content": prompt},
        ]
        tool_records: list[ToolCallRecord] = []
        body_base: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.4,
            "max_tokens": _EFFORT_TOKENS.get(self.reasoning_effort, 8_000),
            "tools": list(tools),
            "tool_choice": "auto",
        }

        final_text = ""
        for round_index in range(MAX_TOOL_ROUNDS + 1):
            payload = self._post(dict(body_base))
            try:
                message = payload["choices"][0]["message"]
            except (KeyError, IndexError, TypeError) as exc:
                raise MimoClientError("unexpected chat/completions shape") from exc
            tool_calls = message.get("tool_calls") or []
            content = message.get("content") or ""
            if content:
                final_text = content
            messages.append(
                {
                    "role": "assistant",
                    "content": content,
                    "tool_calls": tool_calls or None,
                }
            )
            if not tool_calls:
                break
            for call in tool_calls:
                function = call.get("function") or {}
                name = function.get("name") or ""
                raw_args = function.get("arguments") or "{}"
                try:
                    arguments = json.loads(raw_args) if isinstance(raw_args, str) else dict(raw_args)
                except json.JSONDecodeError:
                    arguments = {}
                result = dispatch_tool(ctx, name, arguments)
                tool_records.append(
                    ToolCallRecord(
                        tool=name,
                        ok=bool(result.get("ok")),
                        summary=str(result.get("error") or result.get("path") or result.get("kind") or "ok")[:200],
                        round_index=round_index,
                    )
                )
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": call.get("id") or name,
                        "name": name,
                        "content": json.dumps(result)[:8_000],
                    }
                )

        try:
            summary = extract_json_object(final_text)
        except ValueError:
            summary = {"summary": final_text[:500] or "no final text"}

        artifacts = []
        for key in expected_summary_keys:
            if key == "artifacts" and isinstance(summary.get("artifacts"), list):
                artifacts = [str(item) for item in summary["artifacts"]]
        if not artifacts:
            artifacts = [
                str(path.relative_to(ctx.run_dir)).replace("\\", "/")
                for path in sorted(ctx.run_dir.glob("*"))
                if path.is_file()
            ]
        notes = summary.get("notes")
        if not isinstance(notes, list):
            notes = [str(summary.get("summary") or "ok")]
        checks = summary.get("checks")
        if not isinstance(checks, list):
            checks = []
        return StageRunResult(
            status="completed" if all(r.ok for r in tool_records) or not tool_records else "completed",
            role=stage_name,
            artifacts=artifacts,
            summary=str(summary.get("summary") or "stage complete"),
            checks=[str(item) for item in checks],
            notes=[str(item) for item in notes],
            tool_calls=tool_records,
        )
