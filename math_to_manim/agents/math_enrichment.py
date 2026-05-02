"""Mathematical enrichment stage."""

from __future__ import annotations

from math_to_manim.agents.base import StageAgent
from math_to_manim.schemas import CurriculumPlan, MathConceptPacket, MathPacket


class MathAgent(StageAgent[CurriculumPlan, MathPacket]):
    name = "math"

    def run(self, curriculum: CurriculumPlan) -> MathPacket:
        packets = []
        for concept in curriculum.ordered_concepts:
            packets.append(
                MathConceptPacket(
                    concept=concept,
                    definitions=[f"Working definition for {concept}."],
                    equations=_equations_for(concept),
                    variables=_variables_for(concept),
                    assumptions=["Audience knows basic algebraic notation."],
                    examples=[f"A minimal visual example of {concept}."],
                    latex_strings=_equations_for(concept),
                    math_validity_notes="Deterministic seed content; validate with MathTex/SymPy tools before final render.",
                    rendering_risk="low",
                )
            )
        return MathPacket(concepts=packets)


def _equations_for(concept: str) -> list[str]:
    text = concept.lower()
    if "derivative" in text or "slope" in text:
        return [r"m=\frac{y_2-y_1}{x_2-x_1}", r"f'(a)=\lim_{h\to0}\frac{f(a+h)-f(a)}{h}"]
    if "pythagorean" in text:
        return [r"a^2+b^2=c^2"]
    return [r"\text{idea} \rightarrow \text{visual model} \rightarrow \text{formal statement}"]


def _variables_for(concept: str) -> dict[str, str]:
    text = concept.lower()
    if "derivative" in text or "slope" in text:
        return {"h": "horizontal step", "a": "point of tangency", "f": "function"}
    if "pythagorean" in text:
        return {"a": "first leg", "b": "second leg", "c": "hypotenuse"}
    return {"x": "input or position", "y": "output or measured quantity"}
