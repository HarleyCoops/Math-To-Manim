"""Manim code generation stage."""

from __future__ import annotations

from pathlib import Path

from math_to_manim.agents.base import StageAgent
from math_to_manim.schemas import GeneratedCode, ManimSceneSpec


class ManimCodeAgent(StageAgent[ManimSceneSpec, GeneratedCode]):
    name = "codegen"

    def run(self, spec: ManimSceneSpec) -> GeneratedCode:
        code = _deterministic_scene_code(spec)
        return GeneratedCode(
            scene_name=spec.scene_name,
            code=code,
            dependencies=["manim"],
            source_spec_id=spec.storyboard_scene_id,
            metadata={
                "file_path": "generated_scene.py",
                "estimated_runtime_seconds": 30,
                "risk_notes": ["deterministic scaffold; replace with SDK code generation for production quality"],
            },
        )


def _deterministic_scene_code(spec: ManimSceneSpec) -> str:
    title = spec.scene_name.replace("Scene", "")
    lines = [
        "from manim import *",
        "",
        "",
        f"class {spec.scene_name}(Scene):",
        "    def construct(self):",
        "        self.camera.background_color = '#0f172a'",
        f"        title = Text('{title}', font_size=44).to_edge(UP)",
        "        subtitle = Text('Codex/OpenAI typed pipeline scaffold', font_size=24, color=GRAY_B).next_to(title, DOWN)",
        "        card = RoundedRectangle(width=11, height=4.6, corner_radius=0.12, color=BLUE_B)",
        "        formula = MathTex(r\"f'(a)=\\\\lim_{h\\\\to0}\\\\frac{f(a+h)-f(a)}{h}\", font_size=40)",
        "        takeaway = Text('Visual first. Symbols second. Render every claim.', font_size=28, color=YELLOW)",
        "        group = VGroup(card, formula, takeaway).arrange(DOWN, buff=0.45).move_to(ORIGIN)",
        "        self.play(FadeIn(title), FadeIn(subtitle))",
        "        self.play(Create(card), FadeIn(formula))",
        "        self.play(Write(takeaway))",
        "        self.wait(1.5)",
    ]
    return "\n".join(lines) + "\n"


def write_generated_code(generated: GeneratedCode, run_dir: Path) -> Path:
    path = run_dir / str(generated.metadata.get("file_path", "generated_scene.py"))
    path.write_text(generated.code, encoding="utf-8")
    return path
