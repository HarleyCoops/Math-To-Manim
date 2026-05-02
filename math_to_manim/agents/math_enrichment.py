"""Mathematical enrichment stage."""

from __future__ import annotations

import json

from math_to_manim.agents.base import StageAgent, mark_sdk_metadata, run_structured_sdk_agent
from math_to_manim.schemas import CurriculumPlan, Equation, MathPacket


class MathAgent(StageAgent[CurriculumPlan, MathPacket]):
    name = "math"

    def run(self, curriculum: CurriculumPlan) -> MathPacket:
        if not self.config.deterministic:
            artifact = run_structured_sdk_agent(
                name="MathEnrichmentAgent",
                instructions=(
                    "Create the mathematical packet for the curriculum. Include definitions, "
                    "assumptions, key LaTeX equations that are safe for Manim MathTex, worked "
                    "examples, common errors, and notes about rendering risks. Keep notation "
                    "minimal and pedagogically sound."
                ),
                prompt=json.dumps(curriculum.to_public_dict(), indent=2),
                model=self.config.model,
                output_type=MathPacket,
            )
            if artifact is not None:
                return mark_sdk_metadata(artifact, agent_name=self.name, model=self.config.model)

        steps = [step for module in curriculum.modules for step in module.steps]
        target = steps[-1].title if steps else curriculum.title
        equations = [
            Equation(latex=latex, description=f"Equation used for {target}.", variables=_variables_for(target))
            for latex in _equations_for(target)
        ]
        return MathPacket(
            concept_id=(steps[-1].concept_ids[0] if steps and steps[-1].concept_ids else None),
            definitions=[f"Working definition for {step.title}." for step in steps] or [f"Working definition for {target}."],
            assumptions=["Audience knows basic algebraic notation."],
            key_equations=equations,
            worked_examples=[f"A minimal visual example of {target}."],
            common_errors=["Using dense symbolic manipulation before the visual model is established."],
            source_notes=["Deterministic seed content; validate with MathTex/SymPy tools before final render."],
            metadata={"rendering_risk": "low", "curriculum_title": curriculum.title},
        )


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
