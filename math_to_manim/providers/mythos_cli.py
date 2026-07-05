"""Mythos generation provider for cinematic Manim code.

By default this routes prompts to Claude Fable 5 through the Claude CLI
(``M2M2_MYTHOS_COMMAND=claude``, ``M2M2_MYTHOS_MODEL=claude-fable-5``).
The Fugu Ultra API path remains available by setting
``M2M2_MYTHOS_COMMAND=fugu-api`` with ``FUGU_API_KEY``.
It drops into the exact same pipeline seam:
scene spec in, ``GeneratedCode`` artifact out — with one addition: every
prompt carries the Mythos Cinematic Charter, so generated scenes use
camera-as-narrator grammar instead of static corner-parked equations.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from collections.abc import Callable
from typing import Any

from pydantic import ValidationError

from math_to_manim.config import RuntimeConfig
from math_to_manim.providers.fugu_api import call_fugu_chat, fugu_base_url_from_env
from math_to_manim.schemas import GeneratedCode, ManimSceneSpec

Runner = Callable[..., subprocess.CompletedProcess[str]]

#: The visual contract injected into every Mythos generation.
CINEMATIC_CHARTER = """\
MYTHOS CINEMATIC CHARTER — the generated scene MUST obey all of it.

1. CAMERA IS THE NARRATOR. Use ThreeDScene with the top-down stage pattern:
   set_camera_orientation(phi=0, theta=-90*DEGREES) so the stage reads as 2D;
   tilt into 3D only for set pieces. Move the camera with
   self.move_camera(...) / set_camera_orientation(...); NEVER call .animate
   on self.camera, and never use add_fixed_in_frame_mobjects for formulas you
   intend to zoom into (keep those in world space).
2. HEADLINE BEFORE SYMBOLS. Introduce every major idea with a full-screen
   plain-language statement (font_size >= 64), hold it, fade it, THEN show
   the mathematics.
3. ZOOM INTO TERMS. When explaining part of a formula, dim the rest, color
   the part, and fly the camera into it (zoom 2x-3x via
   move_camera(frame_center=part.get_center(), zoom=...)). Pull back to
   zoom=1 afterward so the part is seen inside the whole.
4. CAPTION EVERYTHING. Every formula on screen gets a one-line plain-English
   lower-third caption (italic, font_size 28-32). Max ONE headline or TWO
   text blocks visible at once. Replace captions; never stack them.
5. PACING. self.wait(0.6-1.6) between beats. A viewer who knows no notation
   must be able to follow from captions and camera motion alone.
6. PALETTE. Background #0c0c0b. Text #faf9f5. Accents: coral #d97757
   (matter), blue #6a9bcc (light/gauge), olive #788c5d (mass/structure),
   gold #d4a27f (interaction), gray #b0aea5 (secondary). Use color to give
   each symbol a consistent identity across the whole film.
7. CRAFT. Build formulas from multi-argument MathTex so terms are
   addressable; use glow layers (stroke copies) for emphasis; LaggedStart
   for ensembles; no external assets, file IO, or network. Manim CE 0.19.
"""


FUGU_API_COMMANDS = {"fugu-api", "sakana-api", "sakaa-api"}


class MythosCliProvider:
    """Generate Manim artifacts through Fugu Ultra or the legacy Mythos CLI."""

    def __init__(self, config: RuntimeConfig | None = None, runner: Runner | None = None):
        self.config = config or RuntimeConfig.from_env()
        self._runner = runner or subprocess.run

    # -- public seam (identical shape to CodexCliProvider) ----------------

    def generate_code(self, spec: ManimSceneSpec) -> GeneratedCode:
        prompt = self._build_codegen_prompt(spec)
        raw = self._run_model(prompt)
        generated = self._parse_generated_code(raw)
        return self._stamp(generated, source_agent="codegen")

    def repair_code(self, spec: ManimSceneSpec, generated: GeneratedCode, failure: str) -> GeneratedCode:
        prompt = self._build_repair_prompt(spec, generated, failure)
        raw = self._run_model(prompt)
        repaired = self._parse_generated_code(raw)
        stamped = self._stamp(repaired, source_agent="repair")
        metadata = dict(stamped.metadata)
        metadata.setdefault("file_path", generated.metadata.get("file_path", "generated_scene.py"))
        metadata["repair_of"] = generated.scene_name
        return stamped.model_copy(update={"metadata": metadata})

    # -- internals ---------------------------------------------------------

    def _stamp(self, generated: GeneratedCode, *, source_agent: str) -> GeneratedCode:
        metadata = dict(generated.metadata or {})
        is_fugu_api = self.config.mythos_command in FUGU_API_COMMANDS
        metadata.update(
            {
                "runtime": "fugu_api" if is_fugu_api else "mythos_cli",
                "provider": "mythos-fugu-api" if is_fugu_api else "mythos-cli",
                "mythos_command": self.config.mythos_command,
                "model": self.config.mythos_model,
                "source_agent": source_agent,
                "charter": "cinematic-v1",
            }
        )
        metadata.setdefault("file_path", "generated_scene.py")
        return generated.model_copy(update={"metadata": metadata})

    def _run_model(self, prompt: str) -> str:
        if self.config.mythos_command in FUGU_API_COMMANDS:
            return call_fugu_chat(
                prompt,
                system_prompt=CINEMATIC_CHARTER,
                model=self.config.mythos_model,
                base_url=fugu_base_url_from_env(),
                timeout=self.config.mythos_timeout_seconds,
            )
        return self._run_cli(prompt)

    def _run_cli(self, prompt: str) -> str:
        command = _resolve_command(self.config.mythos_command)
        cmd = [
            command,
            "-p",
            "--output-format", "text",
            "--model", self.config.mythos_model,
            "--append-system-prompt", CINEMATIC_CHARTER,
        ]
        try:
            completed = self._runner(
                cmd,
                input=prompt,
                text=True,
                capture_output=True,
                timeout=self.config.mythos_timeout_seconds,
                check=False,
            )
        except FileNotFoundError as exc:
            raise RuntimeError(
                f"Mythos CLI not found: {self.config.mythos_command!r}. "
                "Install the requested CLI or use M2M2_MYTHOS_COMMAND=fugu-api."
            ) from exc
        if completed.returncode != 0:
            raise RuntimeError(
                "Mythos CLI generation failed\n"
                f"command: {' '.join(cmd[:4])}\n"
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
            raise RuntimeError(
                f"Mythos CLI returned JSON that did not match GeneratedCode: {exc}"
            ) from exc

    def _build_codegen_prompt(self, spec: ManimSceneSpec) -> str:
        return (
            "You are the Math-To-Manim code generation provider running on the Mythos baseline model.\n"
            "Return only valid JSON matching the GeneratedCode artifact shape. No Markdown fences.\n"
            "Required JSON keys: scene_name, code, dependencies, metadata.\n"
            "The code must be complete, runnable Manim Community Edition 0.19 Python that\n"
            "imports `from manim import *`, defines exactly the requested scene class, and\n"
            "implements the scene spec with the full Mythos Cinematic Charter (headlines,\n"
            "term zooms, captions, palette). Verbose, gorgeous, narration-grade output is\n"
            "the goal — but every line must execute.\n"
            "Scene spec JSON:\n"
            f"{json.dumps(spec.to_public_dict(), indent=2)}"
        )

    def _build_repair_prompt(self, spec: ManimSceneSpec, generated: GeneratedCode, failure: str) -> str:
        return (
            "You are the Math-To-Manim repair provider running on the Mythos baseline model.\n"
            "Return only valid JSON matching the GeneratedCode artifact shape (keys: \n"
            "scene_name, code, dependencies, metadata). Repair the scene below using the\n"
            "failure output. Make surgical fixes; preserve the cinematic structure, the\n"
            "scene class name, and the Charter rules. Manim CE 0.19 APIs only.\n"
            f"Scene spec JSON:\n{json.dumps(spec.to_public_dict(), indent=2)}\n"
            f"Current code:\n{generated.code}\n"
            f"Failure (tail):\n{failure[-8000:]}"
        )


def _resolve_command(command: str) -> str:
    found = shutil.which(command)
    if found:
        return found
    if os.name == "nt" and not command.lower().endswith(".cmd"):
        found = shutil.which(command + ".cmd")
        if found:
            return found
    return command


def _extract_json_object(text: str) -> dict[str, Any]:
    """Pull the first top-level JSON object out of CLI stdout."""
    text = text.strip()
    if text.startswith("```"):
        first_newline = text.find("\n")
        if first_newline != -1:
            text = text[first_newline + 1 :]
        if text.rstrip().endswith("```"):
            text = text.rstrip()[:-3]
    start = text.find("{")
    if start == -1:
        raise RuntimeError(f"Mythos CLI output contained no JSON object:\n{text[:800]}")
    depth = 0
    in_string = False
    escape = False
    for i, ch in enumerate(text[start:], start=start):
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return json.loads(text[start : i + 1])
    raise RuntimeError("Mythos CLI output contained an unterminated JSON object")
