"""xAI Responses API client for grok-4.6.

Talks only to ``https://api.x.ai/v1``. Authentication is ``XAI_API_KEY``.
This module never imports Mythos or Sol.
"""

from __future__ import annotations

import base64
import json
import mimetypes
import os
import urllib.error
import urllib.request
from pathlib import Path

from grok.jsonutil import extract_json_object
from grok.models import REASONING_EFFORTS, StageCallResult

DEFAULT_BASE_URL = os.getenv("XAI_BASE_URL", "https://api.x.ai/v1")
DEFAULT_MODEL = os.getenv("XAI_MODEL", "grok-4.6")
DEFAULT_REASONING_EFFORT = os.getenv("XAI_REASONING_EFFORT", "high")
DEFAULT_TIMEOUT = float(os.getenv("XAI_TIMEOUT", "900"))


class XAIClientError(RuntimeError):
    pass


def api_key_status(key: str | None = None) -> tuple[bool, str]:
    """Check the key without returning its value."""
    value = key if key is not None else os.getenv("XAI_API_KEY", "")
    if not value or not value.strip():
        return False, "XAI_API_KEY is not set"
    if len(value.strip()) < 8:
        return False, "XAI_API_KEY is present but too short to be valid"
    return True, "XAI_API_KEY is set"


def encode_image(path: Path) -> dict:
    raw = path.read_bytes()
    mime, _ = mimetypes.guess_type(str(path))
    if mime not in {"image/png", "image/jpeg", "image/jpg", "image/webp", "image/gif"}:
        mime = "image/png"
    if mime == "image/jpg":
        mime = "image/jpeg"
    encoded = base64.b64encode(raw).decode("ascii")
    return {
        "type": "input_image",
        "image_url": f"data:{mime};base64,{encoded}",
    }


def user_content(text: str, image_path: Path | None = None) -> list[dict] | str:
    if image_path is None:
        return text
    return [
        {"type": "input_text", "text": text},
        encode_image(image_path),
    ]


def collect_text(payload: dict) -> str:
    parts: list[str] = []
    for item in payload.get("output") or []:
        if not isinstance(item, dict):
            continue
        if item.get("type") == "message":
            for block in item.get("content") or []:
                if isinstance(block, dict) and block.get("type") in {"output_text", "text"}:
                    if block.get("text"):
                        parts.append(str(block["text"]))
        elif item.get("type") == "output_text" and item.get("text"):
            parts.append(str(item["text"]))
    if parts:
        return "\n".join(parts)
    if isinstance(payload.get("output_text"), str):
        return payload["output_text"]
    return ""


def collect_thinking(payload: dict) -> list[str]:
    traces: list[str] = []
    for item in payload.get("output") or []:
        if not isinstance(item, dict):
            continue
        if item.get("type") in {"reasoning", "reasoning_summary"}:
            for block in item.get("content") or []:
                if isinstance(block, dict) and block.get("text"):
                    traces.append(str(block["text"]))
            if item.get("summary"):
                traces.append(str(item["summary"]))
    return traces


def collect_tool_calls(payload: dict) -> list[dict]:
    calls: list[dict] = []
    for item in payload.get("output") or []:
        if not isinstance(item, dict):
            continue
        kind = item.get("type")
        if kind in {
            "web_search_call",
            "x_search_call",
            "code_interpreter_call",
            "image_generation_call",
            "function_call",
        }:
            record = {
                "type": kind,
                "id": item.get("id") or item.get("call_id"),
                "name": item.get("name"),
                "arguments": item.get("arguments"),
                "status": item.get("status"),
            }
            if kind == "image_generation_call":
                record["prompt"] = item.get("prompt")
                record["has_result"] = bool(item.get("result"))
            calls.append(record)
    return calls


def collect_images(payload: dict) -> list[dict]:
    images: list[dict] = []
    for item in payload.get("output") or []:
        if isinstance(item, dict) and item.get("type") == "image_generation_call" and item.get("result"):
            images.append(
                {
                    "id": item.get("id"),
                    "prompt": item.get("prompt"),
                    "result": item.get("result"),
                }
            )
    return images


def collect_function_calls(payload: dict) -> list[dict]:
    calls: list[dict] = []
    for item in payload.get("output") or []:
        if isinstance(item, dict) and item.get("type") == "function_call":
            calls.append(item)
    return calls


class XAIClient:
    def __init__(
        self,
        *,
        api_key: str | None = None,
        model: str | None = None,
        reasoning_effort: str | None = None,
        base_url: str | None = None,
        timeout: float | None = None,
    ):
        self.api_key = api_key if api_key is not None else os.getenv("XAI_API_KEY", "")
        self.model = model or DEFAULT_MODEL
        effort = reasoning_effort or DEFAULT_REASONING_EFFORT
        if effort not in REASONING_EFFORTS:
            raise XAIClientError(
                f"XAI_REASONING_EFFORT must be one of {', '.join(REASONING_EFFORTS)}"
            )
        self.reasoning_effort = effort
        self.base_url = (base_url or DEFAULT_BASE_URL).rstrip("/")
        self.timeout = DEFAULT_TIMEOUT if timeout is None else timeout

    def require_key(self) -> str:
        ok, detail = api_key_status(self.api_key)
        if not ok:
            raise XAIClientError(detail)
        return self.api_key.strip()

    def build_payload(
        self,
        *,
        instructions: str,
        text: str,
        tools: list[dict] | tuple[dict, ...] = (),
        image_path: Path | None = None,
        tool_choice: str | dict | None = None,
    ) -> dict:
        payload = {
            "model": self.model,
            "reasoning": {"effort": self.reasoning_effort},
            "input": [
                {"role": "system", "content": instructions},
                {"role": "user", "content": user_content(text, image_path)},
            ],
        }
        if tools:
            payload["tools"] = list(tools)
        if tool_choice is not None:
            payload["tool_choice"] = tool_choice
        return payload

    def post(self, payload: dict, *, previous_response_id: str | None = None) -> dict:
        body = dict(payload)
        if previous_response_id:
            body["previous_response_id"] = previous_response_id
        request = urllib.request.Request(
            f"{self.base_url}/responses",
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.require_key()}",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[-4000:]
            raise XAIClientError(f"xAI Responses API failed ({exc.code}): {detail}") from exc
        except urllib.error.URLError as exc:
            raise XAIClientError(f"xAI Responses API was unreachable: {exc.reason}") from exc

    def complete(
        self,
        *,
        instructions: str,
        text: str,
        tools: list[dict] | tuple[dict, ...] = (),
        image_path: Path | None = None,
        tool_choice: str | dict | None = None,
        function_handlers: dict | None = None,
        max_function_rounds: int = 4,
    ) -> StageCallResult:
        payload = self.build_payload(
            instructions=instructions,
            text=text,
            tools=tools,
            image_path=image_path,
            tool_choice=tool_choice,
        )
        response = self.post(payload)
        tool_calls = collect_tool_calls(response)
        thinking = collect_thinking(response)
        images = collect_images(response)
        rounds = 0
        while function_handlers and collect_function_calls(response) and rounds < max_function_rounds:
            rounds += 1
            outputs = []
            for call in collect_function_calls(response):
                name = call.get("name")
                raw_args = call.get("arguments") or "{}"
                try:
                    args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
                except json.JSONDecodeError:
                    args = {}
                handler = function_handlers.get(name)
                if handler is None:
                    result = {"error": f"unknown function {name}"}
                else:
                    result = handler(**args) if isinstance(args, dict) else handler(args)
                outputs.append(
                    {
                        "type": "function_call_output",
                        "call_id": call.get("call_id") or call.get("id"),
                        "output": json.dumps(result),
                    }
                )
            response = self.post(
                {
                    "model": self.model,
                    "reasoning": {"effort": self.reasoning_effort},
                    "input": outputs,
                    "tools": list(tools),
                },
                previous_response_id=response.get("id"),
            )
            tool_calls.extend(collect_tool_calls(response))
            thinking.extend(collect_thinking(response))
            images.extend(collect_images(response))
        return StageCallResult(
            text=collect_text(response),
            payload=extract_payload_or_empty(collect_text(response)),
            tool_calls=tool_calls,
            thinking=thinking,
            images=images,
            raw=response,
        )


def extract_payload_or_empty(text: str) -> dict:
    if not text.strip():
        return {}
    try:
        return extract_json_object(text)
    except (ValueError, json.JSONDecodeError):
        return {"raw_text": text}
