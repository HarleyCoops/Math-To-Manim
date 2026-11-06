"""Local function tools the model may call over chat/completions.

The composer gets exactly one: ``verify_scene`` compiles and lints a complete
Manim CE scene without importing it. Schema and handler live together so the
wire name and the dispatch name cannot drift apart.
"""

from __future__ import annotations

from glm.client import FunctionTool
from glm.models import SCENE_FILE
from glm.validation import verify_scene_report


def verify_scene(*, source: str = "", **_unused) -> dict:
    if not source or not str(source).strip():
        return {"passed": False, "scene_name": None, "errors": ["source was empty"]}
    return verify_scene_report(str(source))


VERIFY_SCENE = FunctionTool(
    name="verify_scene",
    description=(
        "Compile and statically check a complete Manim Community Edition "
        "scene source string. Returns pass/fail, scene class name, and errors."
    ),
    parameters={
        "type": "object",
        "properties": {
            "source": {
                "type": "string",
                "description": f"Complete Python file contents for {SCENE_FILE}",
            }
        },
        "required": ["source"],
    },
    handler=verify_scene,
)
