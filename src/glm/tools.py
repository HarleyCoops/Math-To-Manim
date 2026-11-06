"""Local function tools the model may call during composer.

chat/completions returns ``function`` objects; verify_scene compiles and lints
a complete Manim CE scene without importing it.
"""

from __future__ import annotations

from glm.validation import verify_scene_report


def verify_scene(*, source: str = "", **_unused) -> dict:
    if not source or not str(source).strip():
        return {"passed": False, "scene_name": None, "errors": ["source was empty"]}
    return verify_scene_report(str(source))
