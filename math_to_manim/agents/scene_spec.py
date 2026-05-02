"""Manim scene specification stage."""

from __future__ import annotations

from math_to_manim.agents.base import StageAgent
from math_to_manim.schemas import ManimSceneSpec, VisualStoryboard


class SceneSpecAgent(StageAgent[VisualStoryboard, ManimSceneSpec]):
    name = "scene_spec"

    def run(self, storyboard: VisualStoryboard) -> ManimSceneSpec:
        class_name = "".join(part for part in storyboard.title.title() if part.isalnum()) or "GeneratedScene"
        if not class_name.endswith("Scene"):
            class_name += "Scene"
        timeline = []
        current = 0.0
        for scene in storyboard.scenes:
            timeline.append(
                {
                    "start": current,
                    "duration": scene.timing_seconds,
                    "title": scene.title,
                    "beats": scene.animation_beats,
                }
            )
            current += scene.timing_seconds
        return ManimSceneSpec(
            scene_class_name=class_name,
            imports=["from manim import *"],
            helper_functions=[],
            mobjects=["Text", "MathTex", "VGroup"],
            timeline=timeline,
            constants={"background_color": "#0f172a"},
            assets=[],
            quality_target="l",
            render_command=f"python -m manim -ql generated_scene.py {class_name}",
            expected_output_path=None,
        )
