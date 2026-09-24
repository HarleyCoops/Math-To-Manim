"""JSON and scene-source extraction for Grok stage replies.

Grok-native; no Mythos imports. Brace-depth scanning is required because
Grok often wraps nested JSON in fences, and a non-greedy ``{.*?}`` match
stops at the first closing brace.
"""

from __future__ import annotations

import json
import re


def _strip_fence(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```"):
        first_newline = stripped.find("\n")
        if first_newline != -1:
            stripped = stripped[first_newline + 1 :]
        if stripped.rstrip().endswith("```"):
            stripped = stripped.rstrip()[:-3]
    return stripped.strip()


def _first_json_object(text: str) -> dict:
    start = text.find("{")
    if start == -1:
        raise ValueError("model text did not contain a JSON object")
    depth = 0
    in_string = False
    escape = False
    for index, char in enumerate(text[start:], start=start):
        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return json.loads(text[start : index + 1])
    raise ValueError("model text contained an unterminated JSON object")


def extract_json_object(text: str) -> dict:
    if not text or not text.strip():
        raise ValueError("empty model text; expected a JSON object")
    candidates = [_strip_fence(text), text.strip()]
    last_error: Exception | None = None
    for candidate in candidates:
        try:
            return _first_json_object(candidate)
        except (ValueError, json.JSONDecodeError) as exc:
            last_error = exc
    assert last_error is not None
    raise last_error


def extract_python_block(text: str) -> str:
    """Pull a Manim scene out of model output. Never treat a JSON fence as Python."""
    if not text or not text.strip():
        raise ValueError("model text did not contain a Python scene")

    python_fences = re.findall(
        r"```(?:python|py)\s*\n(.*?)```",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )
    for body in reversed(python_fences):
        if _looks_like_scene(body):
            return body.strip() + "\n"
    if python_fences:
        return python_fences[-1].strip() + "\n"

    stripped = _strip_fence(text) if text.strip().startswith("```") else text.strip()
    if stripped.lstrip().startswith("{") and '"source"' not in stripped[:80]:
        raise ValueError("model text did not contain a Python scene")
    if _looks_like_scene(stripped) and not stripped.lstrip().startswith("{"):
        return stripped.strip() + "\n"
    raise ValueError("model text did not contain a Python scene")


def _looks_like_scene(text: str) -> bool:
    return "from manim import" in text or (
        "class " in text and "Scene" in text
    )


def extract_scene_source(
    payload: dict | None,
    text: str = "",
    tool_calls: list[dict] | None = None,
) -> str:
    """Composer may put grok_scene.py in JSON, a python fence, or verify_scene args."""
    candidates: list[str] = []
    if isinstance(payload, dict):
        for key in ("source", "grok_scene.py", "scene_source"):
            value = payload.get(key)
            if isinstance(value, str) and _looks_like_scene(value):
                candidates.append(value)
    if text:
        try:
            candidates.append(extract_python_block(text))
        except ValueError:
            if not candidates:
                try:
                    parsed = extract_json_object(text)
                except (ValueError, json.JSONDecodeError):
                    parsed = None
                if isinstance(parsed, dict):
                    for key in ("source", "grok_scene.py", "scene_source"):
                        value = parsed.get(key)
                        if isinstance(value, str) and _looks_like_scene(value):
                            candidates.append(value)
    for call in tool_calls or []:
        args = call.get("arguments")
        if isinstance(args, str):
            try:
                args = json.loads(args)
            except json.JSONDecodeError:
                args = None
        if isinstance(args, dict):
            value = args.get("source")
            if isinstance(value, str) and _looks_like_scene(value):
                candidates.append(value)
    for source in reversed(candidates):
        if source and source.strip():
            return source if source.endswith("\n") else source + "\n"
    raise ValueError("composer did not return grok_scene.py source")
