"""The Mythos Cinematic Charter and model-output parsing.

The charter is the visual contract injected into every Mythos generation:
camera-as-narrator grammar, headlines before symbols, term zooms, captions,
and the Mythos palette. Everything in this module is dependency-free and
side-effect-free so the harness, service, API, and MCP server can all share
one source of truth.
"""

from __future__ import annotations

import json
import re
from typing import Any

#: The visual contract injected into every Mythos generation.
CINEMATIC_CHARTER = """\
MYTHOS CINEMATIC CHARTER — the generated scene MUST obey all of it.

1. CAMERA IS THE NARRATOR. Use ThreeDScene. A formula that the camera zooms
   into lies in world space on the floor (z = 0) and is read from straight
   above with the top-down stage pattern:
   set_camera_orientation(phi=0, theta=-90*DEGREES). Between zooms the camera
   may rest at a small tilt (phi <= 25 degrees); tilt fully into 3D for set
   pieces. Move the camera with self.move_camera(...) /
   set_camera_orientation(...); NEVER call .animate on self.camera, and never
   use add_fixed_in_frame_mobjects for formulas you intend to zoom into (keep
   those in world space).
2. HEADLINE BEFORE SYMBOLS. Introduce every major idea with a full-screen
   plain-language statement (font_size >= 64), hold it, fade it, THEN show
   the mathematics.
3. ZOOM INTO TERMS. When explaining part of a formula, dim the rest, color
   the part, and fly the camera into it (zoom 2x-3x via
   move_camera(frame_center=part.get_center(), zoom=...)). Pull back to
   zoom=1 afterward so the part is seen inside the whole.
4. CAPTION EVERYTHING. Every formula on screen gets a one-line plain-English
   lower-third caption (italic, font_size 28-32, at most 14 words). Max ONE
   headline or TWO text blocks visible at once. Replace captions; never
   stack them.
5. PACING. self.wait(0.6-1.6) between beats. A viewer who knows no notation
   must be able to follow from captions and camera motion alone.
6. PALETTE. Default house palette: background #0c0c0b, text #faf9f5,
   accents coral #d97757 (matter), blue #6a9bcc (light/gauge), olive
   #788c5d (mass/structure), gold #d4a27f (interaction), gray #b0aea5
   (secondary). If the user prompt specifies a different art direction,
   background, paper stock, or ink system, that explicit direction wins:
   implement it consistently and choose readable text/geometry colors for it.
   Use color to give each symbol a consistent identity across the whole film.
7. CRAFT. Build formulas from multi-argument MathTex so terms are
   addressable; use glow layers (stroke copies) for emphasis; LaggedStart
   for ensembles; no external assets, file IO, or network. Manim CE 0.19+.
8. SPACE. Build one continuous 3D world, not a sequence of slides. Give each
   idea its own station (a floor deck with its own objects), 15-20 units from
   the next. Fly between stations with ONE move_camera call (frame_center,
   phi, theta and zoom together) and remove the station you leave. Plan at
   least two 3D set pieces; during a set piece the camera is never still
   (a theta sweep, or ambient rotation at rate <= 0.16). Keep every visible
   object within 20 units of the frame center along the view axis (the
   ThreeDCamera focal distance): objects beyond it distort.
9. GEOMETRY IS COMPUTED. Every 3D structure carries the mathematics: compute
   its coordinates in the scene file from the formulas of the dossier, and
   compute every number shown on screen from the same functions. Do not type
   a decimal that the file could calculate.
10. FORMULA ON A CARD. Over a 3D set piece, a formula that is not zoomed sits
    on one fixed-in-frame card at the top of the frame, with a dark plate
    behind it. A new card replaces the old one.
11. HONEST PICTURES. A picture must not claim more than the mathematics. If
    a quantity is small but not zero, show its true size and state the
    number. Label a schematic as a schematic. State what the film does not
    prove.
"""

#: Appended to every reasoning-stage prompt so agents return machine-readable JSON.
JSON_CONTRACT = (
    "\n\nOUTPUT CONTRACT: Respond with exactly one JSON object and nothing else — "
    "no Markdown fences, no prose before or after. Be generous and verbose INSIDE "
    "the JSON fields; the next agent in the chain feeds on detail."
)


_RAW_STRING_JSON = re.compile(r'(?<=[\[\,(:\s])r"((?:[^"\\]|\\.)*)"')


def _coerce_pythonish_json(obj: str) -> str:
    """Rewrite Python raw strings ``r"..."`` into valid JSON strings.

    Models sometimes emit LaTeX fragments as ``r"\\frac{...}"`` -- valid
    Python but invalid JSON. Double the interior backslashes and re-quote.
    """

    def _esc(match: re.Match[str]) -> str:
        body = match.group(1).replace("\\", "\\\\").replace('"', '\\"')
        return '"' + body + '"'

    return _RAW_STRING_JSON.sub(_esc, obj)


def _loads_json_lenient(obj: str) -> dict[str, Any]:
    """json.loads with one fallback for Python-style raw-string fragments."""
    try:
        return json.loads(obj)
    except json.JSONDecodeError:
        return json.loads(_coerce_pythonish_json(obj))


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
                return _loads_json_lenient(text[start : i + 1])
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

