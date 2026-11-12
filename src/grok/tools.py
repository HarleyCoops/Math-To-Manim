"""The local ``verify_scene`` function tool Grok may call during composer.

Schema and handler live together: the Responses API sees the schema, the
client runs the handler on each ``function_call``.
"""

from __future__ import annotations

from grok.models import SCENE_FILE
from grok.validation import verify_scene_report

VERIFY_SCENE_TOOL = {
    "type": "function",
    "name": "verify_scene",
    "description": (
        "Compile and statically check a complete Manim Community Edition "
        "scene source string. Returns pass/fail, scene class name, and errors."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "source": {
                "type": "string",
                "description": f"Complete Python file contents for {SCENE_FILE}",
            }
        },
        "required": ["source"],
    },
}


def verify_scene(*, source: str = "", **_unused) -> dict:
    if not source or not str(source).strip():
        return {"passed": False, "scene_name": None, "errors": ["source was empty"]}
    return verify_scene_report(str(source))


VERIFY_SCENE_HANDLERS = {"verify_scene": verify_scene}
