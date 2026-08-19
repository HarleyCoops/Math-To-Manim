"""JSON extraction for Grok stage replies. Grok-native; no Mythos imports."""

from __future__ import annotations

import json
import re


_FENCE = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL)


def extract_json_object(text: str) -> dict:
    if not text or not text.strip():
        raise ValueError("empty model text; expected a JSON object")
    stripped = text.strip()
    fenced = _FENCE.search(stripped)
    if fenced:
        return json.loads(fenced.group(1))
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start == -1 or end <= start:
        raise ValueError("model text did not contain a JSON object")
    return json.loads(stripped[start : end + 1])


def extract_python_block(text: str) -> str:
    match = re.search(r"```(?:python)?\s*(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip() + "\n"
    if "from manim import" in text or "class " in text:
        return text.strip() + "\n"
    raise ValueError("model text did not contain a Python scene")
