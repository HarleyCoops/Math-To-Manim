"""JSON and Manim-scene extraction from GLM chat/completions replies.

GLM-native; no Mythos, Sol, or Grok imports. GLM wraps nested JSON in
fences often enough that brace-depth scanning beats any regex: a lazy
``{.*?}`` match stops at the first closing brace.
"""

from __future__ import annotations

import json
import re

SCENE_KEYS = ("source", "glm_scene.py", "scene_source")


def strip_fence(text: str) -> str:
    stripped = text.strip()
    if stripped.startswith("```"):
        newline = stripped.find("\n")
        if newline != -1:
            stripped = stripped[newline + 1 :]
        if stripped.rstrip().endswith("```"):
            stripped = stripped.rstrip()[:-3]
    return stripped.strip()


def first_json_object(text: str) -> dict:
    start = text.find("{")
    if start == -1:
        raise ValueError("model text did not contain a JSON object")
    depth = 0
    in_string = False
    escaped = False
    for index, char in enumerate(text[start:], start=start):
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
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
    last_error: Exception | None = None
    for candidate in (strip_fence(text), text.strip()):
        try:
            return first_json_object(candidate)
        except (ValueError, json.JSONDecodeError) as exc:
            last_error = exc
    assert last_error is not None
    raise last_error


def looks_like_scene(text: str) -> bool:
    return "from manim import" in text or ("class " in text and "Scene" in text)


def extract_python_block(text: str) -> str:
    """Pull a Manim scene out of a reply. Never mistake a JSON fence for code."""
    if not text or not text.strip():
        raise ValueError("model text did not contain a Python scene")
    fences = re.findall(
        r"```(?:python|py)\s*\n(.*?)```",
        text,
        flags=re.DOTALL | re.IGNORECASE,
    )
    for body in reversed(fences):
        if looks_like_scene(body):
            return body.strip() + "\n"
    if fences:
        return fences[-1].strip() + "\n"
    stripped = strip_fence(text) if text.strip().startswith("```") else text.strip()
    if stripped.lstrip().startswith("{") and '"source"' not in stripped[:80]:
        raise ValueError("model text did not contain a Python scene")
    if looks_like_scene(stripped) and not stripped.lstrip().startswith("{"):
        return stripped.strip() + "\n"
    raise ValueError("model text did not contain a Python scene")


def sources_in_payload(payload: dict | None) -> list[str]:
    found: list[str] = []
    if isinstance(payload, dict):
        for key in SCENE_KEYS:
            value = payload.get(key)
            if isinstance(value, str) and looks_like_scene(value):
                found.append(value)
    return found


def extract_scene_source(
    payload: dict | None,
    text: str = "",
    tool_calls: list[dict] | None = None,
) -> str:
    """The composer may put glm_scene.py in JSON, a fence, or verify_scene args."""
    candidates: list[str] = sources_in_payload(payload)
    if text:
        try:
            candidates.append(extract_python_block(text))
        except ValueError:
            try:
                parsed = extract_json_object(text)
            except (ValueError, json.JSONDecodeError):
                parsed = None
            candidates.extend(sources_in_payload(parsed))
    for call in tool_calls or []:
        arguments = call.get("arguments")
        if isinstance(arguments, str):
            try:
                arguments = json.loads(arguments)
            except json.JSONDecodeError:
                arguments = None
        if isinstance(arguments, dict):
            value = arguments.get("source")
            if isinstance(value, str) and looks_like_scene(value):
                candidates.append(value)
    for source in reversed(candidates):
        if source and source.strip():
            return source if source.endswith("\n") else source + "\n"
    raise ValueError("composer did not return glm_scene.py source")
