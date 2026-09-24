"""Z.ai Coding Plan chat/completions client for glm-5.3-flash.

One endpoint: ``https://api.z.ai/api/coding/paas/v4/chat/completions``.
Thinking is always on (``{"type": "enabled"}``); reasoning effort low|high|max
maps to sampling latitude plus a token budget (see models.py). The API key is
resolved from ZHIPU_API_KEY, then ZAI_API_KEY, then an OpenCode auth.json
entry named ``zai-coding-plan`` -- and is never printed or logged.

This module never imports Mythos, Sol, or Grok.
"""

from __future__ import annotations

import base64
import json
import mimetypes
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

from glm.jsonutil import extract_json_object
from glm.models import (
    EFFORT_MAX_TOKENS,
    EFFORT_TEMPERATURE,
    REASONING_EFFORTS,
    StageCallResult,
    tool_record,
)

DEFAULT_BASE_URL = os.getenv("GLM_BASE_URL", "https://api.z.ai/api/coding/paas/v4")
DEFAULT_MODEL = os.getenv("GLM_MODEL", "glm-5.3-flash")
DEFAULT_REASONING_EFFORT = os.getenv("GLM_REASONING_EFFORT", "high")
DEFAULT_TIMEOUT = float(os.getenv("GLM_TIMEOUT", "600"))
PING_TIMEOUT = 45.0
PING_PROMPT = "Reply with the single word pong."
MAX_TOOL_ROUNDS = 6

THINKING_ON = {"type": "enabled"}

_ENV_KEYS = ("ZHIPU_API_KEY", "ZAI_API_KEY")
OPENCODE_PROVIDER = "zai-coding-plan"


class GlmClientError(RuntimeError):
    pass


def redact_secret(text: str, secret: str | None) -> str:
    """Replace every trace of the key with [redacted]."""
    if not text or not secret or not secret.strip():
        return text
    return text.replace(secret.strip(), "[redacted]")


def opencode_auth_path() -> Path:
    home = os.getenv("HOME", str(Path.home()))
    override = os.getenv("OPENCODE_AUTH_JSON")
    base = Path(override) if override else Path(home) / ".local" / "share" / "opencode" / "auth.json"
    return base


def _read_opencode_key(path: Path) -> str | None:
    """Read only the zai-coding-plan entry. The file itself stays closed."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    entry = data.get(OPENCODE_PROVIDER) if isinstance(data, dict) else None
    if not isinstance(entry, dict):
        return None
    key = entry.get("key") or entry.get("api_key") or entry.get("token")
    if isinstance(key, str) and key.strip():
        return key.strip()
    return None


def resolve_api_key(env: dict | None = None) -> tuple[str | None, str | None]:
    """Return (key, source_name). Values never leave this module except to callers."""
    source = env if env is not None else os.environ
    for name in _ENV_KEYS:
        value = source.get(name)
        if value and value.strip():
            return value.strip(), name
    path = opencode_auth_path()
    key = _read_opencode_key(path)
    if key:
        return key, f"opencode:{path.name}:{OPENCODE_PROVIDER}"
    return None, None


def api_key_status(env: dict | None = None) -> tuple[bool, str]:
    """Describe the key situation without ever revealing a value."""
    key, origin = resolve_api_key(env)
    if not key:
        return False, (
            "no GLM key found; set ZHIPU_API_KEY or ZAI_API_KEY, "
            f"or log in via OpenCode ({OPENCODE_PROVIDER})"
        )
    if len(key) < 8:
        return False, "a GLM key is present but too short to be valid"
    return True, f"a GLM key is set (source: {origin})"


def encode_image(path: Path) -> dict:
    raw = path.read_bytes()
    mime, _ = mimetypes.guess_type(str(path))
    if mime not in {"image/png", "image/jpeg", "image/jpg", "image/webp", "image/gif"}:
        mime = "image/png"
    if mime == "image/jpg":
        mime = "image/jpeg"
    encoded = base64.b64encode(raw).decode("ascii")
    return {
        "type": "image_url",
        "image_url": {"url": f"data:{mime};base64,{encoded}"},
    }


def user_content(text: str, image_path: Path | None = None) -> list[dict] | str:
    """chat/completions vision shape: text plus one optional data-URI image."""
    if image_path is None:
        return text
    return [{"type": "text", "text": text}, encode_image(image_path)]


def _thinking_block(message: dict) -> list[str]:
    found: list[str] = []
    for field in ("reasoning_content", "reasoning"):
        value = message.get(field)
        if isinstance(value, str) and value.strip():
            found.append(value)
        elif isinstance(value, list):
            for chunk in value:
                if isinstance(chunk, dict):
                    chunk = chunk.get("text") or chunk.get("content")
                if isinstance(chunk, str) and chunk.strip():
                    found.append(chunk)
    return found


class GlmClient:
    """Thin sync wrapper around Z.ai's OpenAI-compatible chat/completions."""

    def __init__(
        self,
        *,
        model: str = DEFAULT_MODEL,
        base_url: str = DEFAULT_BASE_URL,
        reasoning_effort: str = DEFAULT_REASONING_EFFORT,
        timeout: float = DEFAULT_TIMEOUT,
        api_key: str | None = None,
    ):
        if reasoning_effort not in REASONING_EFFORTS:
            raise GlmClientError(
                f"reasoning_effort must be one of {REASONING_EFFORTS}, got {reasoning_effort!r}"
            )
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
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
        }

    def _post(self, body: dict, timeout: float | None = None) -> dict:
        request = urllib.request.Request(
            self.endpoint,
            data=json.dumps(body).encode("utf-8"),
            headers=self._headers(),
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=timeout or self.timeout) as response:
                raw = response.read().decode("utf-8", errors="replace")
        except urllib.error.HTTPError as exc:
            detail = ""
            try:
                detail = exc.read().decode("utf-8", errors="replace")[:2000]
            except Exception:  # noqa: BLE001 - body best effort
                pass
            raise GlmClientError(
                redact_secret(f"Z.ai returned HTTP {exc.code}: {detail}", self.api_key)
            ) from exc
        except urllib.error.URLError as exc:
            raise GlmClientError(redact_secret(f"could not reach Z.ai: {exc.reason}", self.api_key)) from exc
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise GlmClientError(redact_secret("Z.ai reply was not valid JSON", self.api_key)) from exc
        if not isinstance(payload, dict):
            raise GlmClientError("Z.ai reply was not a JSON object")
        return payload

    def _body(
        self,
        *,
        instructions: str,
        messages_extra: list[dict],
        tools: tuple[dict, ...] | list[dict] | None,
        tool_choice=None,
        max_tokens: int | None = None,
        temperature: float | None = None,
    ) -> dict:
        messages: list[dict] = [{"role": "system", "content": instructions}]
        messages.extend(messages_extra)
        body: dict = {
            "model": self.model,
            "messages": messages,
            # Thinking is always on in this silo; effort tunes latitude only.
            "thinking": dict(THINKING_ON),
            "temperature": temperature
            if temperature is not None
            else EFFORT_TEMPERATURE[self.reasoning_effort],
            "max_tokens": max_tokens
            if max_tokens is not None
            else EFFORT_MAX_TOKENS[self.reasoning_effort],
        }
        if tools:
            body["tools"] = list(tools)
            if tool_choice is not None:
                body["tool_choice"] = tool_choice
        return body

    def complete(
        self,
        *,
        instructions: str,
        text: str,
        image_path: Path | None = None,
        history: list[dict] | None = None,
        tools: tuple[dict, ...] | list[dict] | None = None,
        tool_choice=None,
        function_handlers: dict | None = None,
        max_rounds: int = MAX_TOOL_ROUNDS,
    ) -> StageCallResult:
        """Send one turn, resolving any local function calls until they drain."""
        if not self.api_key:
            raise GlmClientError("no GLM key found; set ZHIPU_API_KEY or ZAI_API_KEY")
        messages_extra: list[dict] = list(history or [])
        messages_extra.append({"role": "user", "content": user_content(text, image_path)})
        handlers = function_handlers or {}
        raw: dict = {}
        final_text = ""
        all_tool_calls: list[dict] = []
        all_thinking: list[str] = []

        for _round in range(max_rounds + 1):
            raw = self._post(
                self._body(
                    instructions=instructions,
                    messages_extra=messages_extra,
                    tools=tools,
                    tool_choice=tool_choice,
                )
            )
            choices = raw.get("choices") or []
            if not choices or not isinstance(choices[0].get("message"), dict):
                raise GlmClientError("Z.ai reply carried no assistant message")
            message = choices[0]["message"]
            final_text = message.get("content") or ""
            all_thinking.extend(_thinking_block(message))

            calls = [tool_record(call) for call in message.get("tool_calls") or []]
            if not calls or not handlers:
                break
            assistant_entry: dict = {"role": "assistant", "content": final_text}
            assistant_entry["tool_calls"] = message.get("tool_calls") or []
            messages_extra.append(assistant_entry)
            pending = False
            for call in calls:
                all_tool_calls.append(call)
                name = call.get("name") or ""
                handler = handlers.get(name)
                arguments = call.get("arguments")
                if isinstance(arguments, str):
                    try:
                        arguments = json.loads(arguments)
                    except json.JSONDecodeError:
                        arguments = {}
                arguments = arguments if isinstance(arguments, dict) else {}
                if handler is None:
                    result_payload = {"error": f"no local handler for {name}"}
                else:
                    try:
                        result_payload = handler(**arguments)
                    except Exception as exc:  # noqa: BLE001 - tool boundary
                        result_payload = {"error": f"{type(exc).__name__}: {exc}"}
                pending = True
                messages_extra.append(
                    {
                        "role": "tool",
                        "tool_call_id": call.get("id"),
                        "name": name,
                        "content": json.dumps(result_payload, ensure_ascii=False),
                    }
                )
            if not pending:
                break

        payload: dict = {}
        if final_text.strip():
            try:
                payload = extract_json_object(final_text)
            except (ValueError, json.JSONDecodeError):
                payload = {}
        return StageCallResult(
            text=final_text,
            payload=payload,
            tool_calls=all_tool_calls,
            thinking=all_thinking,
            raw=raw,
        )

    def ping(self) -> tuple[bool, str]:
        """Live doctor probe: expect pong back from glm-5.3-flash."""
        if not self.api_key:
            return False, "no GLM key found; set ZHIPU_API_KEY or ZAI_API_KEY"
        body = self._body(
            instructions="You are a connectivity probe.",
            messages_extra=[{"role": "user", "content": PING_PROMPT}],
            tools=None,
            # Thinking tokens come out of this budget; 16 was eaten whole.
            max_tokens=1024,
            temperature=0.0,
        )
        for attempt in range(2):
            try:
                raw = self._post(body, timeout=PING_TIMEOUT)
            except GlmClientError as exc:
                if attempt == 0:
                    time.sleep(1.5)
                    continue
                return False, redact_secret(str(exc), self.api_key)
            message = (raw.get("choices") or [{}])[0].get("message") or {}
            said = (message.get("content") or "").strip().lower()
            if "pong" in said:
                return True, f"pong from {self.model}"
            snippet = " ".join(said.split())[:80]
            return False, f"expected pong, got: {snippet!r}"
        return False, "ping did not converge"

    def doctor_line(self) -> str:
        ok, detail = api_key_status()
        return (
            f"endpoint={self.endpoint} model={self.model} "
            f"thinking={'on'} effort={self.reasoning_effort} {detail}"
        ) if ok else (
            f"endpoint={self.endpoint} model={self.model} thinking=on "
            f"effort={self.reasoning_effort} {detail}"
        )
