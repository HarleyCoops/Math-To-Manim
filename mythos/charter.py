"""The Mythos Cinematic Charter and shared parsing utilities.

The charter is the visual contract injected into every Mythos generation:
camera-as-narrator grammar, headlines before symbols, term zooms, captions,
and the Mythos palette. Everything in this module is dependency-free and
side-effect-free so the harness, service, API, and MCP server can all share
one source of truth.
"""

from __future__ import annotations

import json
import os
import re
import shutil
from pathlib import Path
from typing import Any

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
   for ensembles; no external assets, file IO, or network. Manim CE 0.19+.
"""

#: Appended to every reasoning-stage prompt so agents return machine-readable JSON.
JSON_CONTRACT = (
    "\n\nOUTPUT CONTRACT: Respond with exactly one JSON object and nothing else — "
    "no Markdown fences, no prose before or after. Be generous and verbose INSIDE "
    "the JSON fields; the next agent in the chain feeds on detail."
)


def load_env_file(path: Path | None = None) -> None:
    """Load simple KEY=VALUE lines from a .env file into os.environ (no override)."""
    env_path = path or Path(".env")
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def resolve_command(command: str) -> str:
    """Resolve a CLI executable, tolerating Windows .cmd shims."""
    found = shutil.which(command)
    if found:
        return found
    if os.name == "nt" and not command.lower().endswith(".cmd"):
        found = shutil.which(command + ".cmd")
        if found:
            return found
    return command


def extract_json_object(text: str) -> dict[str, Any]:
    """Pull the first top-level JSON object out of model output."""
    text = text.strip()
    if text.startswith("```"):
        first_newline = text.find("\n")
        if first_newline != -1:
            text = text[first_newline + 1 :]
        if text.rstrip().endswith("```"):
            text = text.rstrip()[:-3]
    start = text.find("{")
    if start == -1:
        raise RuntimeError(f"Model output contained no JSON object:\n{text[:800]}")
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
    raise RuntimeError("Model output contained an unterminated JSON object")


def extract_python_block(text: str) -> str:
    """Pull one fenced python block (or bare module) out of model output."""
    match = re.search(r"```(?:python|py)?\s*\n(.*?)```", text, flags=re.DOTALL)
    if match:
        return match.group(1).strip() + "\n"
    stripped = text.strip()
    if stripped.startswith(("from manim", "import", '"""', "#")):
        return stripped + "\n"
    raise RuntimeError(f"No python block found in model output:\n{text[:800]}")


def find_scene_class(code: str) -> str:
    """Return the name of the Scene subclass defined in generated code."""
    match = re.search(
        r"class\s+(\w+)\s*\(\s*(?:ThreeDScene|MovingCameraScene|Scene)\b", code
    )
    if not match:
        raise RuntimeError("Generated code defines no Scene subclass")
    return match.group(1)
