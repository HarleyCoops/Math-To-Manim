"""xAI Responses API client for grok-4.6.

Talks only to ``https://api.x.ai/v1``. Authentication is ``XAI_API_KEY``.
This module never imports Mythos or Sol.
"""

from __future__ import annotations

import base64
import json
import mimetypes
import os
import re
import urllib.error
import urllib.request
from pathlib import Path

from grok.jsonutil import extract_json_object
from grok.models import REASONING_EFFORTS, StageCallResult

DEFAULT_BASE_URL = os.getenv("XAI_BASE_URL", "https://api.x.ai/v1")
DEFAULT_MODEL = os.getenv("XAI_MODEL", "grok-4.6")
DEFAULT_REASONING_EFFORT = os.getenv("XAI_REASONING_EFFORT", "high")
DEFAULT_TIMEOUT = float(os.getenv("XAI_TIMEOUT", "900"))
PING_TIMEOUT = 30.0
PING_PROMPT = "Reply with the single word pong."

_SERVER_TOOL_TYPES = {
    "web_search_call",
    "x_search_call",
    "code_interpreter_call",
    "image_generation_call",
    "function_call",
    "tool_call",
}


class XAIClientError(RuntimeError):
    pass


def redact_secret(text: str, secret: str | None) -> str:
    if not text or not secret or not secret.strip():
        return text
    return text.replace(secret.strip(), "[redacted]")


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
        kind = item.get("type")
        if kind == "message":
            content = item.get("content")
            if isinstance(content, str) and content.strip():
                parts.append(content)
                continue
            for block in content or []:
                if isinstance(block, str) and block.strip():
                    parts.append(block)
                elif isinstance(block, dict) and block.get("type") in {"output_text", "text"}:
                    if block.get("text"):
                        parts.append(str(block["text"]))
        elif kind in {"output_text", "text"} and item.get("text"):
            parts.append(str(item["text"]))
    if parts:
        return "\n".join(parts)
    output_text = payload.get("output_text")
    if isinstance(output_text, str):
        return output_text
    if isinstance(output_text, dict) and output_text.get("text"):
        return str(output_text["text"])
    return ""


def collect_thinking(payload: dict) -> list[str]:
    traces: list[str] = []
    for item in payload.get("output") or []:
        if not isinstance(item, dict):
            continue
        if item.get("type") not in {"reasoning", "reasoning_summary"}:
            continue
        for block in item.get("content") or []:
            if isinstance(block, dict) and block.get("text"):
                traces.append(str(block["text"]))
            elif isinstance(block, str) and block.strip():
                traces.append(block)
        summary = item.get("summary")
        if isinstance(summary, list):
            for block in summary:
                if isinstance(block, dict) and block.get("text"):
                    traces.append(str(block["text"]))
                elif isinstance(block, str) and block.strip():
                    traces.append(block)
        elif summary:
            traces.append(str(summary))
    return traces


def _function_fields(item: dict) -> dict:
    nested = item.get("function") if isinstance(item.get("function"), dict) else {}
    return {
        "type": item.get("type") or "function_call",
        "id": item.get("id") or item.get("call_id"),
        "call_id": item.get("call_id") or item.get("id"),
        "name": item.get("name") or nested.get("name"),
        "arguments": item.get("arguments") if item.get("arguments") is not None else nested.get("arguments"),
        "status": item.get("status"),
    }


def collect_tool_calls(payload: dict) -> list[dict]:
    calls: list[dict] = []
    for item in payload.get("output") or []:
        if not isinstance(item, dict):
            continue
        kind = item.get("type")
        if kind not in _SERVER_TOOL_TYPES:
            continue
        record = _function_fields(item)
        if kind == "image_generation_call":
            record["prompt"] = item.get("prompt")
            record["has_result"] = bool(item.get("result"))
        calls.append(record)
    return calls


def collect_images(payload: dict) -> list[dict]:
    images: list[dict] = []
    for item in payload.get("output") or []:
        if not isinstance(item, dict) or item.get("type") != "image_generation_call":
            continue
        result = item.get("result")
        if not result and isinstance(item.get("image"), dict):
            result = item["image"].get("b64_json") or item["image"].get("result")
        if not result:
            continue
        images.append(
            {
                "id": item.get("id"),
                "prompt": item.get("prompt"),
                "result": result,
            }
        )
    return images


def collect_function_calls(payload: dict) -> list[dict]:
    calls: list[dict] = []
    for item in payload.get("output") or []:
        if not isinstance(item, dict):
            continue
        if item.get("type") in {"function_call", "tool_call"}:
            calls.append(_function_fields(item))
    return calls


def _ping_failure_reason(message: str) -> str:
    match = re.search(r"failed \((\d+)\)", message)
    if match:
        code = match.group(1)
        if code in {"401", "403"}:
            return f"{code}: key rejected"
        return f"HTTP {code}"
    if "unreachable" in message.lower():
        return "unreachable"
    return "request failed"


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
        # Responses API takes the charter in `instructions`. A system-role
        # input item is not the documented delivery path for grok-4.6.
        payload = {
            "model": self.model,
            "instructions": instructions,
            "reasoning": {"effort": self.reasoning_effort},
            "input": [
                {"role": "user", "content": user_content(text, image_path)},
            ],
        }
        if tools:
            payload["tools"] = list(tools)
        if tool_choice is not None:
            payload["tool_choice"] = tool_choice
        return payload

    def ping_payload(self) -> dict:
        return {
            "model": self.model,
            "input": PING_PROMPT,
            "reasoning": {"effort": "low"},
            "max_output_tokens": 16,
        }

    def ping(self) -> tuple[bool, str]:
        """Tiny live Responses call. Never include the key in the returned detail."""
        ok, detail = api_key_status(self.api_key)
        if not ok:
            return False, detail
        previous_timeout = self.timeout
        self.timeout = min(self.timeout, PING_TIMEOUT)
        try:
            response = self.post(self.ping_payload())
        except XAIClientError as exc:
            return False, (
                "XAI_API_KEY is set but the live ping failed "
                f"({_ping_failure_reason(str(exc))})"
            )
        finally:
            self.timeout = previous_timeout
        if not isinstance(response, dict) or not response:
            return False, "XAI_API_KEY is set but the live ping returned an empty response"
        if response.get("error"):
            return False, "XAI_API_KEY is set but the live ping failed (api error)"
        return True, "XAI_API_KEY is set; live ping succeeded"

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
            detail = redact_secret(exc.read().decode("utf-8", errors="replace")[-4000:], self.api_key)
            raise XAIClientError(f"xAI Responses API failed ({exc.code}): {detail}") from exc
        except urllib.error.URLError as exc:
            reason = redact_secret(str(exc.reason), self.api_key)
            raise XAIClientError(f"xAI Responses API was unreachable: {reason}") from exc

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
        tool_calls: list[dict] = []
        thinking: list[str] = []
        images: list[dict] = []
        texts: list[str] = []
        rounds = 0
        nudges = 0

        while True:
            tool_calls.extend(collect_tool_calls(response))
            thinking.extend(collect_thinking(response))
            images.extend(collect_images(response))
            piece = collect_text(response)
            if piece.strip():
                texts.append(piece)

            function_calls = collect_function_calls(response)
            if function_handlers and function_calls and rounds < max_function_rounds:
                rounds += 1
                outputs = self._function_outputs(function_calls, function_handlers)
                if not outputs:
                    break
                response = self.post(
                    {
                        "model": self.model,
                        "reasoning": {"effort": self.reasoning_effort},
                        "input": outputs,
                        "tools": list(tools),
                    },
                    previous_response_id=response.get("id"),
                )
                continue

            status = response.get("status")
            if status in {"incomplete", "in_progress"} and rounds < max_function_rounds:
                rounds += 1
                follow = {
                    "model": self.model,
                    "reasoning": {"effort": self.reasoning_effort},
                    "input": [
                        {
                            "role": "user",
                            "content": "Continue. Return one JSON object with the charter keys.",
                        }
                    ],
                }
                if tools:
                    follow["tools"] = list(tools)
                response = self.post(follow, previous_response_id=response.get("id"))
                continue

            if function_handlers and not texts and nudges < 1 and response.get("id"):
                nudges += 1
                rounds += 1
                response = self.post(
                    {
                        "model": self.model,
                        "reasoning": {"effort": self.reasoning_effort},
                        "input": [
                            {
                                "role": "user",
                                "content": (
                                    "Return one JSON object now. If you wrote grok_scene.py, "
                                    "include it in a source field or a python fence."
                                ),
                            }
                        ],
                        "tools": list(tools),
                    },
                    previous_response_id=response.get("id"),
                )
                continue
            break

        final_text = texts[-1] if texts else ""
        return StageCallResult(
            text=final_text,
            payload=extract_payload_or_empty(final_text),
            tool_calls=tool_calls,
            thinking=thinking,
            images=images,
            raw=response,
        )

    @staticmethod
    def _function_outputs(function_calls: list[dict], function_handlers: dict) -> list[dict]:
        outputs: list[dict] = []
        for call in function_calls:
            name = call.get("name")
            raw_args = call.get("arguments") if call.get("arguments") is not None else "{}"
            try:
                args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
            except json.JSONDecodeError:
                args = {}
            handler = function_handlers.get(name)
            if handler is None:
                result = {"error": f"unknown function {name}"}
            else:
                try:
                    result = handler(**args) if isinstance(args, dict) else handler(args)
                except TypeError as exc:
                    result = {"error": f"function {name} rejected arguments: {exc}"}
            call_id = call.get("call_id") or call.get("id")
            if not call_id:
                continue
            outputs.append(
                {
                    "type": "function_call_output",
                    "call_id": call_id,
                    "output": json.dumps(result),
                }
            )
        return outputs


def extract_payload_or_empty(text: str) -> dict:
    if not text or not text.strip():
        return {}
    try:
        return extract_json_object(text)
    except (ValueError, json.JSONDecodeError):
        return {"raw_text": text}
