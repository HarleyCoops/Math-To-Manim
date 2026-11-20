"""Pluggable Gemini 4 Neon backends: google-genai SDK, gemini-api CLI, and operator."""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from neon.charter import NEON_SYSTEM_CHARTER
from neon.models import PLAN_FILE, SCENE_FILE, NeonPlan, ToolEvent
from neon.settings import default_model, default_thinking_budget, has_gemini_api_cli, redact_secret, resolve_api_key
from neon.tools import check_scene, verify_math


class NeonBackendError(RuntimeError):
    """Raised when a Gemini 4 Neon backend cannot complete a turn."""


@dataclass
class GenerationResult:
    plan: NeonPlan
    source: str
    tool_events: list[ToolEvent] = field(default_factory=list)
    backend_name: str = "operator"
    interaction_id: str | None = None


def _extract_json_block(text: str) -> dict[str, Any]:
    raw = text.strip()
    if raw.startswith("{"):
        return json.loads(raw)
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", raw, flags=re.DOTALL)
    if fenced:
        return json.loads(fenced.group(1))
    start = raw.find("{")
    end = raw.rfind("}")
    if start != -1 and end > start:
        return json.loads(raw[start : end + 1])
    raise ValueError("no JSON object found in model output")


def _extract_python_block(text: str) -> str:
    fenced = re.search(r"```python\s*(.*?)```", text, flags=re.DOTALL)
    if fenced:
        return fenced.group(1).strip() + "\n"
    return text.strip() + "\n"


def _build_user_prompt(prompt: str, slug: str | None) -> str:
    schema_hint = json.dumps(NeonPlan.model_json_schema(), indent=2)
    slug_line = f"Preferred slug: {slug}\n" if slug else ""
    return (
        f"Topic / Production Request:\n{prompt}\n\n"
        f"{slug_line}"
        "Use `verify_math` to verify all key numerical constants and `check_scene` "
        "to validate your Manim ThreeDScene before returning your final JSON object "
        "with top-level keys `plan` (matching the schema below) and `source` (the "
        "complete neon_scene.py Python code).\n\n"
        f"NeonPlan JSON schema:\n{schema_hint}\n"
    )


class GenAINeonBackend:
    """Native google-genai SDK backend running gemini-4-neon with live tool calling."""

    name = "genai"

    def __init__(self, *, model: str | None = None, thinking_budget: int | None = None):
        self.model = model or default_model()
        self.thinking_budget = thinking_budget if thinking_budget is not None else default_thinking_budget()
        self.api_key, self.key_source = resolve_api_key()

    def generate(self, prompt: str, *, slug: str | None = None) -> GenerationResult:
        if not self.api_key:
            raise NeonBackendError("GEMINI_API_KEY is not set")
        try:
            from google import genai
            from google.genai import types
        except ImportError as exc:
            raise NeonBackendError("google-genai is not installed") from exc

        events: list[ToolEvent] = []

        def _tool_verify_math(expression: str) -> dict[str, Any]:
            out = verify_math(expression)
            events.append(ToolEvent(tool="verify_math", ok=bool(out.get("ok")), input={"expression": expression}, output=out))
            return out

        def _tool_check_scene(source: str) -> dict[str, Any]:
            out = check_scene(source)
            events.append(ToolEvent(tool="check_scene", ok=bool(out.get("passed")), input={"line_count": len(source.splitlines())}, output=out))
            return out

        try:
            client = genai.Client(api_key=self.api_key)
            config = types.GenerateContentConfig(
                system_instruction=NEON_SYSTEM_CHARTER,
                temperature=0.2,
                thinking_config=types.ThinkingConfig(include_thoughts=True, thinking_budget=self.thinking_budget),
                tools=[_tool_verify_math, _tool_check_scene],
            )
            response = client.models.generate_content(
                model=self.model,
                contents=_build_user_prompt(prompt, slug),
                config=config,
            )
            payload = _extract_json_block(response.text or "")
            plan = NeonPlan.model_validate(payload["plan"])
            source = str(payload["source"])
            return GenerationResult(plan=plan, source=source, tool_events=events, backend_name=self.name)
        except Exception as exc:  # noqa: BLE001
            raise NeonBackendError(redact_secret(str(exc), self.api_key)) from exc

    def repair(self, source: str, errors: list[str]) -> tuple[str, list[ToolEvent]]:
        from google import genai
        from google.genai import types

        events: list[ToolEvent] = []
        client = genai.Client(api_key=self.api_key)
        response = client.models.generate_content(
            model=self.model,
            contents=(
                "Repair this Manim ThreeDScene so it passes check_scene and renders cleanly. "
                "Return ONLY the complete repaired Python file inside a ```python block.\n\n"
                "ERRORS:\n" + "\n".join(f"- {e}" for e in errors) + "\n\nCURRENT SOURCE:\n```python\n" + source + "\n```"
            ),
            config=types.GenerateContentConfig(
                system_instruction=NEON_SYSTEM_CHARTER,
                temperature=0.1,
                thinking_config=types.ThinkingConfig(thinking_budget=min(4096, self.thinking_budget)),
            ),
        )
        repaired = _extract_python_block(response.text or "")
        check = check_scene(repaired)
        events.append(ToolEvent(tool="check_scene", ok=bool(check.get("passed")), input={"repair": True}, output=check))
        return repaired, events


class GeminiApiCliBackend:
    """Shells out to the official `gemini-api` CLI targeting `gemini-4-neon`."""

    name = "gemini-api"

    def __init__(self, *, model: str | None = None):
        self.model = model or default_model()

    def generate(self, prompt: str, *, slug: str | None = None) -> GenerationResult:
        if not has_gemini_api_cli():
            raise NeonBackendError("`gemini-api` CLI is not installed on PATH")
        user_prompt = _build_user_prompt(prompt, slug)
        proc = subprocess.run(
            [
                "gemini-api",
                "generate",
                "-m",
                self.model,
                "--system",
                NEON_SYSTEM_CHARTER,
                "--stream=false",
                "-o",
                "json",
                "--stdin",
            ],
            input=user_prompt,
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode != 0:
            raise NeonBackendError(f"gemini-api failed (exit {proc.returncode}): {proc.stderr[:300]}")
        data = json.loads(proc.stdout)
        interaction_id = data.get("id")
        chunks: list[str] = []
        for step in data.get("steps", []):
            if step.get("type") == "model_output":
                for part in step.get("content", []):
                    if part.get("type") == "text":
                        chunks.append(part.get("text", ""))
        payload = _extract_json_block("\n".join(chunks))
        plan = NeonPlan.model_validate(payload["plan"])
        source = str(payload["source"])
        events = self._replay_tools(plan, source)
        return GenerationResult(
            plan=plan,
            source=source,
            tool_events=events,
            backend_name=self.name,
            interaction_id=interaction_id,
        )

    @staticmethod
    def _replay_tools(plan: NeonPlan, source: str) -> list[ToolEvent]:
        events: list[ToolEvent] = []
        for chk in plan.math_checks:
            out = verify_math(chk.expression)
            events.append(ToolEvent(tool="verify_math", ok=bool(out.get("ok")), input={"label": chk.label, "expression": chk.expression}, output=out))
        sc = check_scene(source)
        events.append(ToolEvent(tool="check_scene", ok=bool(sc.get("passed")), input={"line_count": len(source.splitlines())}, output=sc))
        return events


class OperatorNeonBackend:
    """Session-driven Gemini 4 Neon operator backend.

    Consumes ``01_neon_plan.json`` and ``neon_scene.py`` from a workspace directory
    authored by an active Gemini 4 Neon session, replays every ``verify_math``
    and ``check_scene`` tool call live, and feeds the validated artifacts directly
    into Manim rendering and showcase publishing.
    """

    name = "operator"

    def __init__(self, workspace: Path):
        self.workspace = Path(workspace).resolve()

    def generate(self, prompt: str, *, slug: str | None = None) -> GenerationResult:
        self.workspace.mkdir(parents=True, exist_ok=True)
        plan_path = self.workspace / PLAN_FILE
        scene_path = self.workspace / SCENE_FILE
        if not plan_path.is_file() or not scene_path.is_file():
            next_prompt = self.workspace / "NEXT_PROMPT.txt"
            next_prompt.write_text(
                "SYSTEM CHARTER:\n" + NEON_SYSTEM_CHARTER + "\n\nUSER PROMPT:\n" + _build_user_prompt(prompt, slug),
                encoding="utf-8",
            )
            raise NeonBackendError(
                f"operator workspace needs {PLAN_FILE} and {SCENE_FILE}; wrote prompt to {next_prompt}"
            )

        plan = NeonPlan.model_validate(json.loads(plan_path.read_text(encoding="utf-8")))
        source = scene_path.read_text(encoding="utf-8")
        events: list[ToolEvent] = []
        for chk in plan.math_checks:
            out = verify_math(chk.expression)
            events.append(
                ToolEvent(
                    tool="verify_math",
                    ok=bool(out.get("ok")),
                    input={"label": chk.label, "expression": chk.expression},
                    output=out,
                )
            )
        sc = check_scene(source)
        events.append(
            ToolEvent(
                tool="check_scene",
                ok=bool(sc.get("passed")),
                input={"line_count": len(source.splitlines())},
                output=sc,
            )
        )
        return GenerationResult(plan=plan, source=source, tool_events=events, backend_name=self.name)


def select_backend(
    backend: str,
    *,
    model: str,
    thinking_budget: int,
    workspace: Path | None = None,
) -> GenAINeonBackend | GeminiApiCliBackend | OperatorNeonBackend:
    if backend == "operator":
        if workspace is None:
            raise NeonBackendError("--workspace is required when --backend operator is selected")
        return OperatorNeonBackend(workspace)
    if backend == "gemini-api":
        return GeminiApiCliBackend(model=model)
    if backend == "genai":
        return GenAINeonBackend(model=model, thinking_budget=thinking_budget)
    # auto resolution: operator workspace if supplied -> gemini-api CLI -> google-genai SDK
    if workspace is not None:
        return OperatorNeonBackend(workspace)
    if has_gemini_api_cli():
        return GeminiApiCliBackend(model=model)
    key, _ = resolve_api_key()
    if key:
        return GenAINeonBackend(model=model, thinking_budget=thinking_budget)
    raise NeonBackendError(
        "no Neon backend available: pass --workspace <dir> for operator mode, "
        "install `gemini-api`, or set GEMINI_API_KEY"
    )
