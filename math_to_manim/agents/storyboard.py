"""Visual storyboard stage."""

from __future__ import annotations

import json

from math_to_manim.agents.base import StageAgent, mark_sdk_metadata, run_structured_sdk_agent
from math_to_manim.schemas import MathPacket, StoryboardScene, VisualStoryboard


class StoryboardAgent(StageAgent[MathPacket, VisualStoryboard]):
    name = "storyboard"

    def run(self, math_packet: MathPacket) -> VisualStoryboard:
        if not self.config.deterministic:
            artifact = run_structured_sdk_agent(
                name="VisualStoryboardAgent",
                instructions=(
                    "Design a visual storyboard before code. Each scene needs concrete visual "
                    "actions, camera notes, timing, concept ids, and metadata such as visual_metaphor, "
                    "objects, color_roles, text_overlays, equation_overlays, transition, and "
                    "manim_primitives. Favor actual educational animation beats over generic title cards."
                ),
                prompt=json.dumps(math_packet.to_public_dict(), indent=2),
                model=self.config.model,
                output_type=VisualStoryboard,
            )
            if artifact is not None:
                return mark_sdk_metadata(artifact, agent_name=self.name, model=self.config.model)

        scenes = []
        scene_titles = ["Foundation", "Visual Model", "Formal Connection", "Takeaway"]
        equations = [equation.latex for equation in math_packet.key_equations]
        for index, title in enumerate(scene_titles, start=1):
            scenes.append(
                StoryboardScene(
                    id=f"scene-{index}",
                    title=title,
                    narration="Build one step of the learner's intuition.",
                    visual_actions=[
                        "introduce visual object",
                        "highlight the changing quantity",
                        "reveal the matching equation",
                    ],
                    concept_ids=[math_packet.concept_id] if math_packet.concept_id else [],
                    duration_seconds=10,
                    camera="static readable frame",
                    metadata={
                        "visual_metaphor": _metaphor(math_packet.definitions[-1] if math_packet.definitions else "concept"),
                        "objects": ["title", "axes or diagram", "highlight labels", "equation overlay"],
                        "color_roles": {"primary": "BLUE", "accent": "YELLOW", "warning": "RED"},
                        "text_overlays": math_packet.definitions[:2],
                        "equation_overlays": equations,
                        "transition": "fade through highlighted takeaway",
                        "manim_primitives": ["Scene", "Text", "MathTex", "VGroup", "FadeIn", "Transform"],
                    },
                )
            )
        return VisualStoryboard(
            title=(math_packet.metadata.get("curriculum_title") or "Math Animation"),
            scenes=scenes,
            target_duration_seconds=sum(scene.duration_seconds or 0 for scene in scenes),
            metadata={"style_notes": "Cinematic but readable: dark background, generous spacing, equations below visuals."},
        )


def _metaphor(concept: str) -> str:
    text = concept.lower()
    if "secant" in text or "derivative" in text or "slope" in text:
        return "a moving secant line tightening into a tangent"
    if "pythagorean" in text or "triangle" in text:
        return "areas rearranging around a right triangle"
    return "an abstract idea becoming a concrete moving diagram"
