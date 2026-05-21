"""Codex CLI provider for subscription-authenticated code generation."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from collections.abc import Callable
from typing import Any

from pydantic import ValidationError

from math_to_manim.config import RuntimeConfig
from math_to_manim.schemas import GeneratedCode, ManimSceneSpec

Runner = Callable[..., subprocess.CompletedProcess[str]]


class CodexCliProvider:
    """Generate Manim artifacts through the locally authenticated Codex CLI.

    This provider intentionally talks to `codex exec` instead of the OpenAI API,
    so it can use a user's Codex subscription/OAuth login when that CLI is ready.
    """

    def __init__(self, config: RuntimeConfig | None = None, runner: Runner | None = None):
        self.config = config or RuntimeConfig.from_env()
        self._runner = runner or subprocess.run

    def generate_code(self, spec: ManimSceneSpec) -> GeneratedCode:
        """Generate a complete `GeneratedCode` artifact from a scene spec."""

        prompt = self._build_codegen_prompt(spec)
        raw = self._run_codex(prompt)
        generated = self._parse_generated_code(raw)
        metadata = dict(generated.metadata or {})
        metadata.update(
            {
                "runtime": "codex_cli",
                "provider": "codex-cli",
                "codex_command": self.config.codex_command,
                "source_agent": "codegen",
            }
        )
        metadata.setdefault("file_path", "generated_scene.py")
        return generated.model_copy(update={"metadata": metadata})

    def repair_code(self, spec: ManimSceneSpec, generated: GeneratedCode, failure: str) -> GeneratedCode:
        """Repair generated Manim code using Codex CLI."""

        prompt = self._build_repair_prompt(spec, generated, failure)
        raw = self._run_codex(prompt)
        repaired = self._parse_generated_code(raw)
        metadata = dict(repaired.metadata or {})
        metadata.update(
            {
                "runtime": "codex_cli",
                "provider": "codex-cli",
                "codex_command": self.config.codex_command,
                "source_agent": "repair",
                "repair_of": generated.scene_name,
            }
        )
        metadata.setdefault("file_path", generated.metadata.get("file_path", "generated_scene.py"))
        return repaired.model_copy(update={"metadata": metadata})

    def _run_codex(self, prompt: str) -> str:
        command = (
            _resolve_codex_command(self.config.codex_command)
            if self._runner is subprocess.run
            else self.config.codex_command
        )
        cmd = [command, "exec"]
        if self.config.codex_full_auto:
            cmd.append("--full-auto")
        cmd.append("-")
        try:
            completed = self._runner(
                cmd,
                input=prompt,
                cwd=str(self.config.codex_workdir) if self.config.codex_workdir else None,
                text=True,
                capture_output=True,
                timeout=self.config.codex_timeout_seconds,
                check=False,
            )
        except FileNotFoundError as exc:
            raise RuntimeError(
                f"Codex CLI command not found: {self.config.codex_command!r}. Install/login with Codex first."
            ) from exc
        if completed.returncode != 0:
            raise RuntimeError(
                "Codex CLI generation failed\n"
                f"command: {' '.join(cmd[:3])}\n"
                f"exit_code: {completed.returncode}\n"
                f"stderr:\n{completed.stderr[-4000:]}\n"
                f"stdout:\n{completed.stdout[-2000:]}"
            )
        return completed.stdout

    def _parse_generated_code(self, text: str) -> GeneratedCode:
        payload = _extract_json_object(text)
        try:
            return GeneratedCode.model_validate(payload)
        except ValidationError as exc:
            raise RuntimeError(f"Codex CLI returned JSON that did not match GeneratedCode: {exc}") from exc

    def _build_codegen_prompt(self, spec: ManimSceneSpec) -> str:
        return (
            "You are the M2M2 Manim code generation provider running through Codex CLI.\n"
            "Return only valid JSON matching the GeneratedCode artifact shape. No Markdown fences.\n"
            "Required JSON keys: scene_name, code, dependencies, metadata.\n"
            "The code must be complete runnable Manim Community Edition Python.\n"
            "It must import `from manim import *`, define exactly the requested scene class, avoid network/file IO, "
            "avoid external assets, and preserve the educational visual intent.\n"
            "For Manim CE camera changes, use self.move_camera(...), self.set_camera_orientation(...), "
            "or begin_ambient_camera_rotation(...); do not call .animate on self.camera.\n"
            "Scene spec JSON:\n"
            f"{json.dumps(spec.to_public_dict(), indent=2)}"
        )

    def _build_repair_prompt(self, spec: ManimSceneSpec, generated: GeneratedCode, failure: str) -> str:
        return (
            "You are the M2M2 Manim repair provider running through Codex CLI.\n"
            "Return only valid JSON matching the GeneratedCode artifact shape. No Markdown fences.\n"
            "Repair the complete code file while preserving scene intent and scene class name.\n"
            "Make surgical fixes for the traceback first; avoid network/file IO and external assets.\n"
            "For Manim CE camera changes, use self.move_camera(...), self.set_camera_orientation(...), "
            "or begin_ambient_camera_rotation(...); do not call .animate on self.camera.\n"
            "Repair input JSON:\n"
            f"{json.dumps({'scene_spec': spec.to_public_dict(), 'generated_code': generated.to_public_dict(), 'failure': failure[-8000:]}, indent=2)}"
        )


def _extract_json_object(text: str) -> dict[str, Any]:
    """Extract the first complete JSON object from Codex stdout."""

    stripped = text.strip()
    if stripped.startswith("```"):
        stripped = stripped.strip("`").strip()
        if stripped.startswith("json"):
            stripped = stripped[4:].strip()
    try:
        parsed = json.loads(stripped)
    except json.JSONDecodeError:
        start = stripped.find("{")
        end = stripped.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise RuntimeError(f"Codex CLI did not return a JSON object. Output tail:\n{stripped[-2000:]}")
        parsed = json.loads(stripped[start : end + 1])
    if not isinstance(parsed, dict):
        raise RuntimeError("Codex CLI returned JSON, but it was not an object")
    return parsed


def _resolve_codex_command(command: str) -> str:
    """Resolve Windows npm shims to an executable subprocess can launch."""

    if os.name != "nt":
        return command
    if any(command.lower().endswith(suffix) for suffix in (".exe", ".cmd", ".bat", ".ps1")):
        return command
    return shutil.which(f"{command}.cmd") or shutil.which(f"{command}.exe") or shutil.which(command) or command
