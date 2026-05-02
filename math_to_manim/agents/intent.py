"""Concept intent stage."""

from __future__ import annotations

import json

from math_to_manim.agents.base import StageAgent, mark_sdk_metadata, run_structured_sdk_agent
from math_to_manim.schemas import ConceptIntent, UserRequest


class IntentAgent(StageAgent[UserRequest, ConceptIntent]):
    name = "intent"

    def run(self, request: UserRequest) -> ConceptIntent:
        if not self.config.deterministic:
            artifact = run_structured_sdk_agent(
                name="ConceptIntentAgent",
                instructions=(
                    "You identify the educational intent behind a math/science animation request. "
                    "Return a compact ConceptIntent. Include prerequisites, learning objectives, "
                    "likely misconceptions, and target audience. Keep it useful for downstream "
                    "visual storyboarding."
                ),
                prompt=json.dumps(request.to_public_dict(), indent=2),
                model=self.config.model,
                output_type=ConceptIntent,
            )
            if artifact is not None:
                return mark_sdk_metadata(artifact, agent_name=self.name, model=self.config.model)

        prompt = request.prompt.strip()
        core = _derive_core_concept(prompt)
        domain = _guess_domain(core)
        return ConceptIntent(
            primary_concept=core,
            related_concepts=[],
            prerequisites=_default_prerequisites(core),
            learning_objectives=[f"Explain {core} with a concrete visual intuition."],
            misconceptions=[
                "visual approximations are not automatically formal proofs",
                "symbols should not appear before the learner sees what changes",
            ],
            target_audience=request.target_audience,
            metadata={
                "domain": domain,
                "aha_moment": _guess_aha(core),
                "visual_potential": "high",
                "success_criteria": [
                    "target concept appears in the title",
                    "visual metaphor is shown before formal notation",
                    "final scene states the core takeaway",
                ],
            },
        )


def _derive_core_concept(prompt: str) -> str:
    lowered = prompt.lower()
    for prefix in ("explain why ", "explain ", "show why ", "show ", "visualize ", "animate "):
        if lowered.startswith(prefix):
            return prompt[len(prefix) :].strip(" .")
    return prompt.strip(" .")


def _guess_domain(core: str) -> str:
    text = core.lower()
    if any(term in text for term in ("derivative", "limit", "integral", "slope", "series")):
        return "calculus"
    if any(term in text for term in ("vector", "matrix", "eigen", "linear")):
        return "linear_algebra"
    if any(term in text for term in ("gravity", "quantum", "spacetime", "field")):
        return "physics"
    if any(term in text for term in ("gradient", "neural", "policy", "optimization")):
        return "machine_learning"
    return "mathematics"


def _guess_aha(core: str) -> str:
    text = core.lower()
    if "derivative" in text or "slope" in text:
        return "A secant line becomes a tangent line as the interval shrinks."
    if "pythagorean" in text:
        return "The square on the hypotenuse contains the same area as the two leg squares."
    return f"The abstract idea of {core} becomes visible as a sequence of simple transformations."


def _default_prerequisites(core: str) -> list[str]:
    text = core.lower()
    if "derivative" in text or "slope" in text:
        return ["functions and graphs", "slope of a line", "secant lines", "limits"]
    if "pythagorean" in text:
        return ["right triangles", "area of squares", "congruence", "similarity"]
    if "fourier" in text:
        return ["periodic motion", "sine and cosine", "vectors in the plane", "superposition"]
    if "lorenz" in text:
        return ["differential equations", "phase space", "sensitive dependence", "trajectories"]
    return ["basic notation", "visual model", "core definition", "worked example"]
