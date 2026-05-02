"""Manim scene specification stage."""

from __future__ import annotations

from math_to_manim.agents.base import StageAgent
from math_to_manim.schemas import ManimAnimationSpec, ManimObjectSpec, ManimSceneSpec, VisualStoryboard


class SceneSpecAgent(StageAgent[VisualStoryboard, ManimSceneSpec]):
    name = "scene_spec"

    def run(self, storyboard: VisualStoryboard) -> ManimSceneSpec:
        class_name = "".join(part for part in storyboard.title.title() if part.isalnum()) or "GeneratedScene"
        if not class_name.endswith("Scene"):
            class_name += "Scene"
        timeline = []
        current = 0.0
        for scene in storyboard.scenes:
            duration = scene.duration_seconds or 0.0
            timeline.append(
                {
                    "start": current,
                    "duration": duration,
                    "title": scene.title,
                    "beats": scene.visual_actions,
                }
            )
            current += duration
        return ManimSceneSpec(
            scene_name=class_name,
            storyboard_scene_id=(storyboard.scenes[0].id if storyboard.scenes else None),
            imports=["from manim import *"],
            objects=[
                ManimObjectSpec(id="title", type="Text", properties={"font_size": 44}),
                ManimObjectSpec(id="formula", type="MathTex", properties={"font_size": 40}),
                ManimObjectSpec(id="takeaway", type="Text", properties={"font_size": 28}),
            ],
            animations=[
                ManimAnimationSpec(action="FadeIn", target="title", start_time=0, duration_seconds=1),
                ManimAnimationSpec(action="Write", target="formula", start_time=1, duration_seconds=2),
                ManimAnimationSpec(action="Write", target="takeaway", start_time=3, duration_seconds=2),
            ],
            camera={"plan": "static readable frame"},
            config={"background_color": "#0f172a", "quality_target": "low"},
            code_requirements=[
                "Use Manim Community Edition.",
                "Keep text readable and inside frame.",
                "Show a visual metaphor before formal notation.",
            ],
            metadata={
                "timeline": timeline,
                "render_command": f"python -m manim -ql generated_scene.py {class_name}",
            },
        )
