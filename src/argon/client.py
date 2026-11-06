"""Google ADK (`google-adk`) and `google-genai` client for the Argon reasoning chain.

Importing this module requires the ``argon`` extra (google-adk, google-genai);
offline runs and the run ledger never import it.
"""

from __future__ import annotations

import asyncio
import json
import mimetypes
from pathlib import Path

from google import genai
from google.adk.agents import LlmAgent
from google.adk.models.google_llm import Gemini
from google.adk.runners import InMemoryRunner
from google.genai import types

from argon.jsonutil import extract_json_object
from argon.models import StageCallResult
from argon.settings import api_key_status, default_model, redact_secret, resolve_api_key
from argon.stages import Stage

APP_NAME = "math-to-manim-argon"
USER_ID = "argon-operator"
PING_PROMPT = "Reply with the single word pong."

_THINKING_BUDGETS = {
    "low": 1024,
    "medium": 4096,
    "high": 8192,
    "xhigh": 16384,
}
_IMAGE_MIME_TYPES = {"image/png", "image/jpeg", "image/webp", "image/gif"}


class ArgonClientError(RuntimeError):
    pass


def _parse_payload(text: str) -> dict | None:
    """The JSON object in a model reply, or None when there is none."""
    if not text.strip():
        return None
    try:
        return extract_json_object(text)
    except (ValueError, json.JSONDecodeError):
        return None


def build_stage_adk_agent(
    stage: Stage,
    *,
    instructions: str | None = None,
    model: str | Gemini | None = None,
    reasoning_effort: str = "high",
) -> LlmAgent:
    """Create the Google ADK LlmAgent for one stage of the table."""
    budget = _THINKING_BUDGETS.get(reasoning_effort, _THINKING_BUDGETS["high"])
    gen_config = types.GenerateContentConfig(
        temperature=0.2,
        thinking_config=types.ThinkingConfig(include_thoughts=True, thinking_budget=budget),
    )
    return LlmAgent(
        name=stage.agent_name,
        description=f"Argon Math-To-Manim stage agent: {stage.name}",
        model=model or default_model(),
        instruction=instructions if instructions is not None else stage.charter(),
        tools=list(stage.tools),
        output_key=stage.artifact,
        generate_content_config=gen_config,
    )


def _image_part(image_path: Path) -> types.Part:
    mime, _ = mimetypes.guess_type(str(image_path))
    if mime not in _IMAGE_MIME_TYPES:
        mime = "image/png"
    return types.Part.from_bytes(data=image_path.read_bytes(), mime_type=mime)


class ArgonClient:
    """Executes Argon reasoning stages via Google ADK InMemoryRunner and google-genai.

    The API key is handed to the SDK explicitly; it is never written into the
    process environment. Per-run settings (reasoning effort) are passed per call,
    so one client can serve concurrent runs.
    """

    def __init__(self, *, api_key: str | None = None, model: str | None = None):
        key, source = resolve_api_key(api_key)
        self.api_key = key
        self.key_source = source
        self.model = model or default_model()

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
            client = genai.Client(api_key=self.api_key)
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

    async def _run_stage_async(
        self,
        stage: Stage,
        *,
        instructions: str,
        text: str,
        reasoning_effort: str,
        image_path: Path | None,
    ) -> StageCallResult:
        llm = Gemini(model=self.model, client_kwargs={"api_key": self.require_key()})
        agent = build_stage_adk_agent(
            stage,
            instructions=instructions,
            model=llm,
            reasoning_effort=reasoning_effort,
        )
        runner = InMemoryRunner(agent=agent, app_name=APP_NAME)
        session = await runner.session_service.create_session(app_name=APP_NAME, user_id=USER_ID)

        parts: list[types.Part] = [types.Part.from_text(text=text)]
        if image_path is not None:
            parts.append(_image_part(image_path))
        user_msg = types.Content(role="user", parts=parts)

        texts: list[str] = []
        thinking: list[str] = []
        tool_calls: list[dict] = []
        raw_events: list[dict] = []

        async for event in runner.run_async(user_id=USER_ID, session_id=session.id, new_message=user_msg):
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
            raw_events.append({"author": getattr(event, "author", None), "has_content": bool(content)})

        final_text = "\n".join(t for t in texts if t.strip()).strip()
        return StageCallResult(
            text=final_text,
            payload=_parse_payload(final_text),
            tool_calls=tool_calls,
            thinking=thinking,
            raw={"sdk": "google-adk", "model": self.model, "events": raw_events},
        )

    def complete(
        self,
        stage: Stage,
        *,
        text: str,
        reasoning_effort: str,
        instructions: str | None = None,
        image_path: Path | None = None,
    ) -> StageCallResult:
        """Run one stage turn. ``instructions`` defaults to the stage charter."""
        try:
            return asyncio.run(
                self._run_stage_async(
                    stage,
                    instructions=instructions if instructions is not None else stage.charter(),
                    text=text,
                    reasoning_effort=reasoning_effort,
                    image_path=image_path,
                )
            )
        except Exception as exc:
            safe = redact_secret(str(exc), self.api_key)
            raise ArgonClientError(f"Google ADK stage {stage.name!r} failed: {safe}") from exc
