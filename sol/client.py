"""GPT-5.6 Sol Responses API client using the hosted Python tool."""

from __future__ import annotations

import json
import os
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from sol.models import CalculationRequest, CalculationResult

SOL_MODEL = "gpt-5.6-sol"
RESPONSES_URL = "https://api.openai.com/v1/responses"

SYSTEM_INSTRUCTIONS = """
You are the mathematical core of Math-To-Manim's GPT-5.6 Sol silo.
Solve the user's problem, explain it at the requested audience level, and
design a short visual sequence. Use the python tool for every nontrivial
calculation and verify the final answer numerically or symbolically.

Do not return executable Python or Manim. The application compiles your typed
scene plan into reviewed code. Keep visual beats atomic and in logical order.
Return only the required structured result.
""".strip()


def extract_output_text(payload: dict[str, Any]) -> str:
    chunks: list[str] = []
    for item in payload.get("output", []):
        if not isinstance(item, dict) or item.get("type") != "message":
            continue
        for part in item.get("content", []):
            if isinstance(part, dict) and part.get("type") == "output_text":
                chunks.append(str(part.get("text", "")))
    if not chunks:
        raise RuntimeError("Sol returned no structured output text")
    return "".join(chunks)


def calculate_with_sol(
    request: CalculationRequest,
    *,
    api_key: str | None = None,
    safety_identifier: str | None = None,
    timeout: float = 180.0,
) -> CalculationResult:
    key = api_key or os.getenv("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY is not configured")

    payload: dict[str, Any] = {
        "model": SOL_MODEL,
        "reasoning": {"effort": request.reasoning_effort},
        "instructions": SYSTEM_INSTRUCTIONS,
        "input": f"Audience: {request.audience}\nProblem: {request.problem}",
        "tools": [{
            "type": "code_interpreter",
            "container": {"type": "auto", "memory_limit": "4g"},
        }],
        "tool_choice": "auto",
        "text": {"format": {
            "type": "json_schema",
            "name": "sol_calculation",
            "strict": True,
            "schema": CalculationResult.model_json_schema(),
        }},
        "include": ["code_interpreter_call.outputs"],
        "store": False,
    }
    if safety_identifier:
        payload["safety_identifier"] = safety_identifier

    api_request = Request(
        RESPONSES_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(api_request, timeout=timeout) as response:
            raw = response.read().decode("utf-8")
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[-2000:]
        raise RuntimeError(f"Sol Responses API failed with status {exc.code}: {detail}") from exc
    except URLError as exc:
        raise RuntimeError(f"Sol Responses API could not be reached: {exc.reason}") from exc

    try:
        response_payload = json.loads(raw)
        return CalculationResult.model_validate_json(extract_output_text(response_payload))
    except (json.JSONDecodeError, ValueError) as exc:
        raise RuntimeError("Sol returned an invalid structured calculation") from exc
