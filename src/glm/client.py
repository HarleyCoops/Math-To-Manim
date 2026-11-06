"""Z.ai Coding Plan chat/completions client for glm-5.3-flash.

One endpoint: ``https://api.z.ai/api/coding/paas/v4/chat/completions``.
Thinking is always on (``{"type": "enabled"}``); reasoning effort low|high|max
maps to sampling latitude plus a token budget (see models.py) and is chosen
per call, so one client can serve many runs at once.

The environment is read in exactly one place, ``GlmSettings.from_env``: model
(GLM_MODEL), base URL (GLM_BASE_URL), default effort (GLM_REASONING_EFFORT),
timeout (GLM_TIMEOUT) and the API key, resolved from ZHIPU_API_KEY, then
ZAI_API_KEY, then an OpenCode auth.json entry named ``zai-coding-plan``. A
client built with an explicit ``api_key`` touches neither the environment nor
that file. The key is never printed or logged.

This module never imports Mythos, Sol, or Grok.
"""

from __future__ import annotations

import base64
import json
import mimetypes
import os
import urllib.error
import urllib.request
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path

from glm.models import EFFORT_MAX_TOKENS, EFFORT_TEMPERATURE, REASONING_EFFORTS

DEFAULT_BASE_URL = "https://api.z.ai/api/coding/paas/v4"
DEFAULT_MODEL = "glm-5.3-flash"
DEFAULT_REASONING_EFFORT = "high"
DEFAULT_TIMEOUT = 600.0
PING_TIMEOUT = 45.0
PING_PROMPT = "Reply with the single word pong."
MAX_TOOL_ROUNDS = 6

THINKING_ON = {"type": "enabled"}

_ENV_KEYS = ("ZHIPU_API_KEY", "ZAI_API_KEY")
OPENCODE_PROVIDER = "zai-coding-plan"
NO_KEY_MESSAGE = "no GLM key found; set ZHIPU_API_KEY or ZAI_API_KEY"

# A transport takes (url, headers, body, timeout) and returns the decoded JSON
# object, raising GlmClientError for anything short of that.
Transport = Callable[[str, dict, dict, float], dict]


class GlmClientError(RuntimeError):
    pass


def redact_secret(text: str, secret: str | None) -> str:
    """Replace every trace of the key with [redacted]."""
    if not text or not secret or not secret.strip():
        return text
    return text.replace(secret.strip(), "[redacted]")


# --------------------------------------------------------------------------
# Environment and key resolution
# --------------------------------------------------------------------------


def opencode_auth_path(env: Mapping[str, str] | None = None) -> Path:
    source = os.environ if env is None else env
    override = source.get("OPENCODE_AUTH_JSON")
    if override:
        return Path(override)
    home = source.get("HOME") or str(Path.home())
    return Path(home) / ".local" / "share" / "opencode" / "auth.json"


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


def resolve_api_key(env: Mapping[str, str] | None = None) -> tuple[str | None, str | None]:
    """Return (key, source_name). Values never leave this module except to callers."""
    source = os.environ if env is None else env
    for name in _ENV_KEYS:
        value = source.get(name)
        if value and value.strip():
            return value.strip(), name
    path = opencode_auth_path(source)
    key = _read_opencode_key(path)
    if key:
        return key, f"opencode:{path.name}:{OPENCODE_PROVIDER}"
    return None, None


def api_key_status(env: Mapping[str, str] | None = None) -> tuple[bool, str]:
    """Describe the key situation without ever revealing a value."""
    key, origin = resolve_api_key(env)
    if not key:
        return False, f"{NO_KEY_MESSAGE}, or log in via OpenCode ({OPENCODE_PROVIDER})"
    if len(key) < 8:
        return False, "a GLM key is present but too short to be valid"
    return True, f"a GLM key is set (source: {origin})"


@dataclass(frozen=True)
class GlmSettings:
    """Everything the environment decides, read once at call time."""

    model: str = DEFAULT_MODEL
    base_url: str = DEFAULT_BASE_URL
    reasoning_effort: str = DEFAULT_REASONING_EFFORT
    timeout: float = DEFAULT_TIMEOUT
    api_key: str | None = None
    key_source: str | None = None

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> GlmSettings:
        source = os.environ if env is None else env
        effort = source.get("GLM_REASONING_EFFORT") or DEFAULT_REASONING_EFFORT
        if effort not in REASONING_EFFORTS:
            raise GlmClientError(
                f"GLM_REASONING_EFFORT must be one of {REASONING_EFFORTS}, got {effort!r}"
            )
        key, origin = resolve_api_key(source)
        return cls(
            model=source.get("GLM_MODEL") or DEFAULT_MODEL,
            base_url=source.get("GLM_BASE_URL") or DEFAULT_BASE_URL,
            reasoning_effort=effort,
            timeout=float(source.get("GLM_TIMEOUT") or DEFAULT_TIMEOUT),
            api_key=key,
            key_source=origin,
        )


# --------------------------------------------------------------------------
# Wire shapes
# --------------------------------------------------------------------------


@dataclass(frozen=True)
class FunctionTool:
    """A local function the model may call; schema and handler travel together."""

    name: str
    description: str
    parameters: dict
    handler: Callable[..., dict]

    def schema(self) -> dict:
        # Z.ai chat/completions tool shape: nested under "function".
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


@dataclass
class StageReply:
    """One finished chat/completions exchange, tool rounds included."""

    text: str
    tool_calls: list[dict] = field(default_factory=list)
    thinking: list[str] = field(default_factory=list)
    raw: dict = field(default_factory=dict)


def tool_record(tool_call: dict) -> dict:
    """Normalize one OpenAI-style tool_call into {id, name, arguments}."""
    nested = tool_call.get("function") if isinstance(tool_call.get("function"), dict) else {}
    return {
        "id": tool_call.get("id"),
        "name": tool_call.get("name") or nested.get("name"),
        "arguments": (
            tool_call.get("arguments")
            if tool_call.get("arguments") is not None
            else nested.get("arguments")
        ),
    }


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
    for name in ("reasoning_content", "reasoning"):
        value = message.get(name)
        if isinstance(value, str) and value.strip():
            found.append(value)
        elif isinstance(value, list):
            for chunk in value:
                if isinstance(chunk, dict):
                    chunk = chunk.get("text") or chunk.get("content")
                if isinstance(chunk, str) and chunk.strip():
                    found.append(chunk)
    return found


def _call_arguments(call: dict) -> dict:
    arguments = call.get("arguments")
    if isinstance(arguments, str):
        try:
            arguments = json.loads(arguments)
        except json.JSONDecodeError:
            arguments = {}
    return arguments if isinstance(arguments, dict) else {}


def post_json(url: str, headers: dict, body: dict, timeout: float) -> dict:
    """Default transport: one HTTPS POST, JSON in, JSON object out."""
    request = urllib.request.Request(
        url, data=json.dumps(body).encode("utf-8"), headers=headers, method="POST"
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        detail = ""
        try:
            detail = exc.read().decode("utf-8", errors="replace")[:2000]
        except Exception:  # noqa: BLE001 - body best effort
            pass
        raise GlmClientError(f"Z.ai returned HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise GlmClientError(f"could not reach Z.ai: {exc.reason}") from exc
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise GlmClientError("Z.ai reply was not valid JSON") from exc
    if not isinstance(payload, dict):
        raise GlmClientError("Z.ai reply was not a JSON object")
    return payload


class GlmClient:
    """Thin sync wrapper around Z.ai's OpenAI-compatible chat/completions."""

    def __init__(
        self,
        *,
        api_key: str | None,
        model: str = DEFAULT_MODEL,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        key_source: str | None = "explicit",
        transport: Transport | None = None,
    ):
        self.api_key = api_key.strip() if api_key and api_key.strip() else None
        self.key_source = key_source if self.api_key else None
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._transport = transport or post_json

    @classmethod
    def from_env(
        cls, env: Mapping[str, str] | None = None, *, transport: Transport | None = None
    ) -> GlmClient:
        settings = GlmSettings.from_env(env)
        return cls(
            api_key=settings.api_key,
            key_source=settings.key_source,
            model=settings.model,
            base_url=settings.base_url,
            timeout=settings.timeout,
            transport=transport,
        )

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
        try:
            return self._transport(self.endpoint, self._headers(), body, timeout or self.timeout)
        except GlmClientError as exc:
            raise GlmClientError(redact_secret(str(exc), self.api_key)) from exc

    def _body(
        self,
        *,
        instructions: str,
        messages_extra: list[dict],
        tools: Sequence[FunctionTool] = (),
        max_tokens: int,
        temperature: float,
    ) -> dict:
        body: dict = {
            "model": self.model,
            "messages": [{"role": "system", "content": instructions}, *messages_extra],
            # Thinking is always on in this silo; effort tunes latitude only.
            "thinking": dict(THINKING_ON),
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if tools:
            body["tools"] = [tool.schema() for tool in tools]
        return body

    def complete(
        self,
        *,
        instructions: str,
        text: str,
        reasoning_effort: str = DEFAULT_REASONING_EFFORT,
        image_path: Path | None = None,
        tools: Sequence[FunctionTool] = (),
    ) -> StageReply:
        """Send one turn, resolving local function calls until they drain."""
        if not self.api_key:
            raise GlmClientError(NO_KEY_MESSAGE)
        handlers = {tool.name: tool.handler for tool in tools}
        messages_extra: list[dict] = [{"role": "user", "content": user_content(text, image_path)}]
        reply = StageReply(text="")

        for _round in range(MAX_TOOL_ROUNDS + 1):
            reply.raw = self._post(
                self._body(
                    instructions=instructions,
                    messages_extra=messages_extra,
                    tools=tools,
                    max_tokens=EFFORT_MAX_TOKENS[reasoning_effort],
                    temperature=EFFORT_TEMPERATURE[reasoning_effort],
                )
            )
            choices = reply.raw.get("choices") or []
            if not choices or not isinstance(choices[0].get("message"), dict):
                raise GlmClientError("Z.ai reply carried no assistant message")
            message = choices[0]["message"]
            reply.text = message.get("content") or ""
            reply.thinking.extend(_thinking_block(message))

            calls = [tool_record(call) for call in message.get("tool_calls") or []]
            if not calls or not handlers:
                break
            messages_extra.append(
                {
                    "role": "assistant",
                    "content": reply.text,
                    "tool_calls": message.get("tool_calls") or [],
                }
            )
            for call in calls:
                reply.tool_calls.append(call)
                name = call.get("name") or ""
                handler = handlers.get(name)
                if handler is None:
                    result_payload = {"error": f"no local handler for {name}"}
                else:
                    try:
                        result_payload = handler(**_call_arguments(call))
                    except Exception as exc:  # noqa: BLE001 - tool boundary
                        result_payload = {"error": f"{type(exc).__name__}: {exc}"}
                messages_extra.append(
                    {
                        "role": "tool",
                        "tool_call_id": call.get("id"),
                        "name": name,
                        "content": json.dumps(result_payload, ensure_ascii=False),
                    }
                )
        return reply

    def ping(self) -> tuple[bool, str]:
        """Live doctor probe, one attempt: expect pong back from the model."""
        if not self.api_key:
            return False, NO_KEY_MESSAGE
        body = self._body(
            instructions="You are a connectivity probe.",
            messages_extra=[{"role": "user", "content": PING_PROMPT}],
            # Thinking tokens come out of this budget; 16 was eaten whole.
            max_tokens=1024,
            temperature=0.0,
        )
        try:
            raw = self._post(body, timeout=PING_TIMEOUT)
        except GlmClientError as exc:
            return False, str(exc)
        message = (raw.get("choices") or [{}])[0].get("message") or {}
        said = (message.get("content") or "").strip().lower()
        if "pong" in said:
            return True, f"pong from {self.model}"
        snippet = " ".join(said.split())[:80]
        return False, f"expected pong, got: {snippet!r}"
