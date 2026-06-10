"""Manim code generation stage."""

from __future__ import annotations

import json
from pathlib import Path

from math_to_manim.agents.base import StageAgent, mark_sdk_metadata, run_structured_sdk_agent
from math_to_manim.providers import CodexCliProvider, MythosCliProvider
from math_to_manim.schemas import GeneratedCode, ManimSceneSpec


class ManimCodeAgent(StageAgent[ManimSceneSpec, GeneratedCode]):
    name = "codegen"

    def run(self, spec: ManimSceneSpec) -> GeneratedCode:
        if self.config.codegen_provider in {"mythos-cli", "claude-cli"} and not self.config.deterministic:
            return MythosCliProvider(self.config).generate_code(spec)

        if self.config.codegen_provider == "codex-cli" and not self.config.deterministic:
            return CodexCliProvider(self.config).generate_code(spec)

        if not self.config.deterministic:
            artifact = run_structured_sdk_agent(
                name="ManimCodeAgent",
                instructions=(
                    "Generate complete, runnable Manim Community Edition Python code from the scene spec. "
                    "Return only the GeneratedCode artifact. The code must import `from manim import *`, "
                    "define exactly the requested Scene class, avoid network/file IO, avoid custom external "
                    "assets, keep text readable, and implement real educational visuals from the spec. "
                    "Prefer robust Manim CE primitives: Axes, Dot, Line, always_redraw, ValueTracker, "
                    "MathTex, VGroup, Transform, FadeIn, Create. Use raw strings for LaTeX. "
                    "Do not produce a generic title-card scaffold. Keep overlays sparse: no more than "
                    "two equation/text overlays visible in the same region, font sizes generally 24-40, "
                    "and use fixed corners or side panels so labels never overlap the curve, axes, or "
                    "each other. When animating labels, prefer FadeOut/FadeIn or ReplacementTransform "
                    "between compatible MathTex objects; avoid transforms that leave unreadable glyph "
                    "fragments."
                ),
                prompt=json.dumps(spec.to_public_dict(), indent=2),
                model=self.config.model,
                output_type=GeneratedCode,
            )
            if artifact is not None:
                artifact = mark_sdk_metadata(artifact, agent_name=self.name, model=self.config.model)
                if "file_path" not in artifact.metadata:
                    artifact = artifact.model_copy(update={"metadata": {**artifact.metadata, "file_path": "generated_scene.py"}})
                return artifact

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

    def repair(self, spec: ManimSceneSpec, generated: GeneratedCode, failure: str) -> GeneratedCode:
        """Repair generated Manim code after a static/render failure."""

        if self.config.deterministic:
            return generated
        if self.config.codegen_provider in {"mythos-cli", "claude-cli"}:
            return MythosCliProvider(self.config).repair_code(spec, generated, failure)
        if self.config.codegen_provider == "codex-cli":
            return CodexCliProvider(self.config).repair_code(spec, generated, failure)

        artifact = run_structured_sdk_agent(
            name="ManimRepairAgent",
            instructions=(
                "Repair a complete Manim Community Edition Python scene using the traceback. "
                "Return only a GeneratedCode artifact with the complete corrected file. Preserve "
                "the educational visual intent, scene class name, and dependencies. Make surgical "
                "fixes first. Avoid fragile or version-specific methods. In Manim CE 0.19, do not "
                "use add_fixed_in_frame_mobjects in MovingCameraScene; use normal mobjects, camera "
                "frame animation, or a compatible Scene/ThreeDScene choice instead. Also fix visible "
                "layout risks while repairing: remove overlapping labels, reduce crowded text, place "
                "formulas in stable corners/panels, and replace glitchy text transforms with clean "
                "FadeOut/FadeIn or ReplacementTransform. Avoid file IO, network calls, and external assets."
            ),
            prompt=json.dumps(
                {
                    "scene_spec": spec.to_public_dict(),
                    "generated_code": generated.to_public_dict(),
                    "failure": failure[-8000:],
                },
                indent=2,
            ),
            model=self.config.model,
            output_type=GeneratedCode,
        )
        if artifact is None:
            return generated
        artifact = mark_sdk_metadata(artifact, agent_name="repair", model=self.config.model)
        metadata = dict(artifact.metadata)
        metadata.setdefault("file_path", generated.metadata.get("file_path", "generated_scene.py"))
        metadata["repair_of"] = generated.scene_name
        return artifact.model_copy(update={"metadata": metadata})


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
        "        formula = MathTex(r\"f'(a)=\\lim_{h\\to0}\\frac{f(a+h)-f(a)}{h}\", font_size=40)",
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
