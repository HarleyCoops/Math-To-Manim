"""Concept intent stage."""

from __future__ import annotations

from math_to_manim.agents.base import StageAgent
from math_to_manim.schemas import ConceptIntent, UserRequest


class IntentAgent(StageAgent[UserRequest, ConceptIntent]):
    name = "intent"

    def run(self, request: UserRequest) -> ConceptIntent:
        prompt = request.prompt.strip()
        core = _derive_core_concept(prompt)
        domain = _guess_domain(core)
        return ConceptIntent(
            core_concept=core,
            domain=domain,
            audience_level=request.audience_level,
            learning_goal=f"Explain {core} with a concrete visual intuition.",
            aha_moment=_guess_aha(core),
            visual_potential="high",
            forbidden_complexity=[
                "unintroduced notation",
                "dense text blocks",
                "symbolic manipulation before geometric intuition",
            ],
            success_criteria=[
                "target concept appears in the title",
                "visual metaphor is shown before formal notation",
                "final scene states the core takeaway",
            ],
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
