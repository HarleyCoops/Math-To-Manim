"""Google ADK (`google-adk`) and `google-genai` client for the Argon reasoning chain."""

from __future__ import annotations

import asyncio
import json
import mimetypes
import os
import re
from pathlib import Path
from typing import Callable

from google import genai
from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.runners import InMemoryRunner
from google.genai import types

from argon.charters import STAGES, load_charter
from argon.jsonutil import extract_json_object
from argon.models import REASONING_EFFORTS, StageCallResult
from argon.tools import execute_math_check, verify_scene

DEFAULT_MODEL = os.getenv("ARGON_MODEL", "gemini-2.5-pro")
DEFAULT_REASONING_EFFORT = os.getenv("ARGON_REASONING_EFFORT", "high")
DEFAULT_TIMEOUT = float(os.getenv("ARGON_TIMEOUT", "900"))
PING_PROMPT = "Reply with the single word pong."

_THINKING_BUDGETS = {
    "low": 1024,
    "medium": 4096,
    "high": 8192,
    "xhigh": 16384,
}


class ArgonClientError(RuntimeError):
    pass


def resolve_api_key(explicit: str | None = None) -> tuple[str, str]:
    """Return (key, env_source_name)."""
    if explicit is not None and explicit.strip():
        return explicit.strip(), "explicit"
    for name in ("GEMINI_API_KEY", "GOOGLE_API_KEY", "ARGON_API_KEY"):
        val = os.getenv(name, "").strip()
        if val:
            return val, name
    return "", "GEMINI_API_KEY"


def redact_secret(text: str, secret: str | None) -> str:
    if not text or not secret or not secret.strip():
        return text
    return text.replace(secret.strip(), "[redacted]")


def api_key_status(key: str | None = None) -> tuple[bool, str]:
    """Check whether a Gemini/Google API key is configured without returning its value."""
    value, source = resolve_api_key(key)
    if not value:
        return False, "GEMINI_API_KEY (or GOOGLE_API_KEY) is not set"
    if len(value) < 8:
        return False, f"{source} is present but too short to be valid"
    return True, f"{source} is set"


def extract_payload_or_empty(text: str) -> dict:
    if not text or not text.strip():
        return {}
    try:
        return extract_json_object(text)
    except (ValueError, json.JSONDecodeError):
        return {"raw_text": text}


def _stage_adk_name(stage_name: str) -> str:
    return "argon_" + re.sub(r"[^a-zA-Z0-9_]", "_", stage_name)


def build_stage_adk_agent(
    stage_name: str,
    *,
    instructions: str,
    model: str = DEFAULT_MODEL,
    reasoning_effort: str = DEFAULT_REASONING_EFFORT,
    tools: list[Callable] | tuple[Callable, ...] = (),
    output_key: str | None = None,
) -> LlmAgent:
    """Create a Google ADK LlmAgent for a single reasoning stage."""
    budget = _THINKING_BUDGETS.get(reasoning_effort, 8192)
    gen_config = types.GenerateContentConfig(
        temperature=0.2,
        thinking_config=types.ThinkingConfig(
            include_thoughts=True,
            thinking_budget=budget,
        ),
    )
    return LlmAgent(
        name=_stage_adk_name(stage_name),
        description=f"Argon Math-To-Manim stage agent: {stage_name}",
        model=model,
        instruction=instructions,
        tools=list(tools),
        output_key=output_key or f"{_stage_adk_name(stage_name)}_output",
        generate_content_config=gen_config,
    )


def build_adk_sequential_pipeline(
    *,
    model: str = DEFAULT_MODEL,
    reasoning_effort: str = DEFAULT_REASONING_EFFORT,
) -> SequentialAgent:
    """Build the 6-agent Google ADK SequentialAgent for the Argon reasoning chain."""
    tool_map: dict[str, Callable] = {
        "execute_math_check": execute_math_check,
        "verify_scene": verify_scene,
    }
    sub_agents: list[LlmAgent] = []
    for stage in STAGES:
        charter = load_charter(stage.charter_file)
        stage_tools = [tool_map[t] for t in stage.tools if t in tool_map]
        sub_agents.append(
            build_stage_adk_agent(
                stage.name,
                instructions=charter,
                model=model,
                reasoning_effort=reasoning_effort,
                tools=stage_tools,
                output_key=stage.artifact,
            )
        )
    return SequentialAgent(
        name="argon_math_to_manim_chain",
        description="Six-stage Argon Google ADK mathematical animation reasoning chain.",
        sub_agents=sub_agents,
    )


class ArgonClient:
    """Executes Argon reasoning stages via Google ADK InMemoryRunner and google-genai."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str | None = None,
        reasoning_effort: str | None = None,
        timeout: float | None = None,
    ):
        key, source = resolve_api_key(api_key)
        self.api_key = key
        self.key_source = source
        self.model = model or DEFAULT_MODEL
        effort = reasoning_effort or DEFAULT_REASONING_EFFORT
        if effort not in REASONING_EFFORTS:
            raise ArgonClientError(
                f"ARGON_REASONING_EFFORT must be one of {', '.join(REASONING_EFFORTS)}"
            )
        self.reasoning_effort = effort
        self.timeout = DEFAULT_TIMEOUT if timeout is None else timeout

    def require_key(self) -> str:
        ok, detail = api_key_status(self.api_key)
        if not ok:
            raise ArgonClientError(detail)
        return self.api_key

    def ping(self) -> tuple[bool, str]:
        """Run a lightweight google-genai ping without exposing the key."""
        ok, detail = api_key_status(self.api_key)
        if not ok:
            return False, detail
        try:
            client = genai.Client(api_key=self.require_key())
            response = client.models.generate_content(
                model=self.model,
                contents=PING_PROMPT,
                config=types.GenerateContentConfig(max_output_tokens=16),
            )
            text = (response.text or "").strip()
            if not text:
                return False, f"{self.key_source} is set but the live ping returned empty text"
            return True, f"{self.key_source} is set; live ping succeeded"
        except Exception as exc:  # noqa: BLE001
            safe_msg = redact_secret(str(exc), self.api_key)
            return False, f"{self.key_source} is set but live ping failed ({safe_msg[:180]})"

    async def _run_adk_stage_async(
        self,
        *,
        stage_name: str,
        instructions: str,
        text: str,
        tools: list[Callable] | tuple[Callable, ...] = (),
        image_path: Path | None = None,
    ) -> StageCallResult:
        key = self.require_key()
        os.environ["GEMINI_API_KEY"] = key
        os.environ["GOOGLE_API_KEY"] = key

        agent = build_stage_adk_agent(
            stage_name,
            instructions=instructions,
            model=self.model,
            reasoning_effort=self.reasoning_effort,
            tools=tools,
        )
        runner = InMemoryRunner(agent=agent, app_name="math-to-manim-argon")
        session = await runner.session_service.create_session(
            app_name="math-to-manim-argon",
            user_id="argon-operator",
        )

        parts: list[types.Part] = [types.Part.from_text(text=text)]
        if image_path is not None:
            mime, _ = mimetypes.guess_type(str(image_path))
            if mime not in {"image/png", "image/jpeg", "image/webp", "image/gif"}:
                mime = "image/png"
            parts.append(types.Part.from_bytes(data=image_path.read_bytes(), mime_type=mime))
        user_msg = types.Content(role="user", parts=parts)

        texts: list[str] = []
        thinking: list[str] = []
        tool_calls: list[dict] = []
        raw_events: list[dict] = []

        async for event in runner.run_async(
            user_id="argon-operator",
            session_id=session.id,
            new_message=user_msg,
        ):
            content = getattr(event, "content", None)
            if content and getattr(content, "parts", None):
                for part in content.parts:
                    if getattr(part, "thought", False) and getattr(part, "text", None):
                        thinking.append(str(part.text))
                    elif getattr(part, "text", None):
                        texts.append(str(part.text))
                    fn_call = getattr(part, "function_call", None)
                    if fn_call is not None:
                        tool_calls.append(
                            {
                                "type": "function_call",
                                "id": getattr(fn_call, "id", None),
                                "name": getattr(fn_call, "name", None),
                                "arguments": dict(getattr(fn_call, "args", {}) or {}),
                            }
                        )
            raw_events.append(
                {
                    "author": getattr(event, "author", None),
                    "has_content": bool(content),
                }
            )

        final_text = "\n".join(t for t in texts if t.strip()).strip()
        return StageCallResult(
            text=final_text,
            payload=extract_payload_or_empty(final_text),
            tool_calls=tool_calls,
            thinking=thinking,
            raw={"sdk": "google-adk", "model": self.model, "events": raw_events},
        )

    def complete(
        self,
        *,
        stage_name: str = "stage",
        instructions: str,
        text: str,
        tools: list[Callable] | tuple[Callable, ...] = (),
        image_path: Path | None = None,
    ) -> StageCallResult:
        try:
            return asyncio.run(
                self._run_adk_stage_async(
                    stage_name=stage_name,
                    instructions=instructions,
                    text=text,
                    tools=tools,
                    image_path=image_path,
                )
            )
        except Exception as exc:
            safe = redact_secret(str(exc), self.api_key)
            raise ArgonClientError(f"Google ADK stage {stage_name!r} failed: {safe}") from exc
