"""Visual storyboard stage."""

from __future__ import annotations

from math_to_manim.agents.base import StageAgent
from math_to_manim.schemas import MathPacket, StoryboardScene, VisualStoryboard


class StoryboardAgent(StageAgent[MathPacket, VisualStoryboard]):
    name = "storyboard"

    def run(self, math_packet: MathPacket) -> VisualStoryboard:
        scenes = []
        for index, packet in enumerate(math_packet.concepts[:6], start=1):
            scenes.append(
                StoryboardScene(
                    title=packet.concept.title(),
                    purpose="Build one step of the learner's intuition.",
                    visual_metaphor=_metaphor(packet.concept),
                    objects=["title", "axes or diagram", "highlight labels", "equation overlay"],
                    color_roles={"primary": "BLUE", "accent": "YELLOW", "warning": "RED"},
                    animation_beats=[
                        "introduce visual object",
                        "highlight the changing quantity",
                        "reveal the matching equation",
                    ],
                    camera_plan="static readable frame",
                    timing_seconds=10,
                    text_overlays=[packet.definitions[0]],
                    equation_overlays=packet.latex_strings,
                    transition="fade through highlighted takeaway",
                    manim_primitives=["Scene", "Text", "MathTex", "VGroup", "FadeIn", "Transform"],
                )
            )
        return VisualStoryboard(
            title=math_packet.concepts[-1].concept.title() if math_packet.concepts else "Math Animation",
            scenes=scenes,
            style_notes="Cinematic but readable: dark background, generous spacing, equations below visuals.",
        )


def _metaphor(concept: str) -> str:
    text = concept.lower()
    if "secant" in text or "derivative" in text or "slope" in text:
        return "a moving secant line tightening into a tangent"
    if "pythagorean" in text or "triangle" in text:
        return "areas rearranging around a right triangle"
    return "an abstract idea becoming a concrete moving diagram"
