"""Deterministic Argon Google ADK chain rehearsal with zero network calls."""

from __future__ import annotations

from pathlib import Path

from argon import bundle
from argon.models import RunRequest
from argon.stages import STAGES

OFFLINE_MODEL = "offline"

_OFFLINE_SCENE = '''from manim import *


class ArgonOfflineJourney(ThreeDScene):
    """Deterministic rehearsal of the complete Argon Google ADK artifact contract."""

    def construct(self):
        self.camera.background_color = "#0c0c0b"
        self.set_camera_orientation(phi=0 * DEGREES, theta=-90 * DEGREES)
        title = Text("Argon Google ADK pipeline: offline rehearsal", color="#faf9f5", font_size=34)
        stages = VGroup(*[
            Text(label, font_size=24, color=color)
            for label, color in [
                ("intent", "#6a9bcc"),
                ("cartographer", "#d97757"),
                ("curriculum", "#e5b566"),
                ("math-director", "#788c5d"),
                ("cinematographer", "#b0aea5"),
                ("composer", "#d4a27f"),
            ]
        ]).arrange(DOWN, buff=0.22)
        self.play(FadeIn(title))
        self.play(title.animate.to_edge(UP), LaggedStart(*[FadeIn(item) for item in stages]))
        self.move_camera(phi=60 * DEGREES, theta=-45 * DEGREES, run_time=1.5)
        self.wait(0.5)
'''


def reverse_tree_for(prompt: str) -> dict:
    """Offline reverse knowledge tree. Depth 0 is the target claim."""
    lowered = prompt.lower()
    if any(token in lowered for token in ("diffusion", "score", "sde", "consistency")):
        target = (
            "Continuous-time score SDEs share an exact deterministic Probability Flow ODE "
            "whose trajectories a Consistency Model collapses into a single one-step map "
            "f_theta(x_t, t) = x_epsilon."
        )
        nodes = [
            {
                "id": "consistency-collapse",
                "name": "Consistency map collapses the ODE trajectory to one step",
                "why_needed": "This is the core claim the film must earn.",
                "depth": 0,
                "assumed": False,
                "visual_seed": "Every point along a golden trajectory projecting in one leap onto the clean manifold at t=epsilon.",
            },
            {
                "id": "prob-flow-ode",
                "name": "Probability Flow ODE shares identical marginals p_t(x)",
                "why_needed": "Without a deterministic trajectory through p_t(x), self-consistency along a path cannot be defined.",
                "depth": 1,
                "assumed": False,
                "visual_seed": "Tangled stochastic paths smoothing into a single deterministic golden streamline.",
            },
            {
                "id": "score-field",
                "name": "Score vector field grad_x log p_t(x) points toward high density",
                "why_needed": "Both the reverse SDE and Probability Flow ODE are driven by the score field.",
                "depth": 2,
                "assumed": False,
                "visual_seed": "Sky-blue arrows pointing uphill toward the ridge of probability density.",
            },
            {
                "id": "forward-sde",
                "name": "Forward Brownian diffusion dx = f(x,t)dt + g(t)dw",
                "why_needed": "The learner first sees how structured data dissolves into a Gaussian cloud.",
                "depth": 3,
                "assumed": True,
                "visual_seed": "A bimodal data curve diffusing into a wide Gaussian bell.",
            },
        ]
        edges = [
            ["prob-flow-ode", "consistency-collapse"],
            ["score-field", "prob-flow-ode"],
            ["forward-sde", "score-field"],
        ]
        spine = ["forward-sde", "score-field", "prob-flow-ode", "consistency-collapse"]
    else:
        target = f"The film earns this request: {prompt.strip()[:180]}"
        nodes = [
            {
                "id": "claim",
                "name": "the requested mathematical insight",
                "why_needed": "Depth 0 is always the core claim, not a topic label.",
                "depth": 0,
                "assumed": False,
                "visual_seed": "the final geometric picture the viewer can now read",
            },
            {
                "id": "mechanism",
                "name": "the geometric mechanism that drives the claim",
                "why_needed": "The claim is empty until its engine is visible.",
                "depth": 1,
                "assumed": False,
                "visual_seed": "the moving spatial invariant",
            },
            {
                "id": "quantity",
                "name": "the quantities the mechanism acts on",
                "why_needed": "A mechanism without named quantities cannot be checked.",
                "depth": 2,
                "assumed": False,
                "visual_seed": "labeled magnitudes in 3D space",
            },
            {
                "id": "foundations",
                "name": "notation and ideas the audience already owns",
                "why_needed": "Reverse thinking stops where the learner already is.",
                "depth": 3,
                "assumed": True,
                "visual_seed": "an intuitive starting curve",
            },
        ]
        edges = [
            ["mechanism", "claim"],
            ["quantity", "mechanism"],
            ["foundations", "quantity"],
        ]
        spine = ["foundations", "quantity", "mechanism", "claim"]

    return {
        "offline": True,
        "target": target,
        "nodes": nodes,
        "edges": edges,
        "spine": spine,
        "sources": [],
        "topic": prompt,
    }


def _intent(request: RunRequest) -> dict:
    image_read = None
    if request.image:
        image_read = {
            "path": request.image,
            "note": "offline rehearsal recorded the attachment path without vision",
        }
    return {
        "offline": True,
        "core_claim": f"A spatial visual argument can earn this request: {request.prompt}",
        "audience": "a curious learner who follows 3D geometry before dense symbols",
        "emotional_arc": ["curiosity", "tension", "revelation", "awe"],
        "scope": {"in": [request.prompt], "out": ["unrelated survey material"]},
        "duration_seconds": 120,
        "title_options": ["The Probability Flow", "One Step to the Manifold", "Reverse Then Forward"],
        "the_big_zoom": "the camera dives into the consistency identity f_theta(x_t, t) = f_theta(x_t', t')",
        "image_read": image_read,
    }


def _curriculum(tree: dict) -> dict:
    acts = []
    for index, node_id in enumerate(tree["spine"], start=1):
        node = next(item for item in tree["nodes"] if item["id"] == node_id)
        acts.append(
            {
                "act_number": index,
                "title": node["name"],
                "opening_question": f"What must be true before {node['name']}?",
                "teaches": node_id,
                "narrative": node["why_needed"],
                "headline": node["name"],
                "payoff": node["why_needed"],
                "estimated_seconds": 25,
            }
        )
    return {
        "offline": True,
        "acts": acts,
        "through_line": "The spine walks from assumed foundations to the target claim.",
    }


def _math_dossier(request: RunRequest) -> dict:
    return {
        "offline": True,
        "formulas": [
            {
                "id": "F1",
                "act_number": 2,
                "latex_parts": [r"\mathrm{d}x", r"=", r"-\frac{1}{2}g(t)^2\nabla_x\log p_t(x)\,\mathrm{d}t"],
                "term_glossary": [
                    {
                        "part_index": 2,
                        "plain_words": "Deterministic probability flow drift driven by the score.",
                        "identity": "light",
                        "zoom_worthy": True,
                    }
                ],
                "derivation_or_motivation": "Offline rehearsal uses the zero-drift Probability Flow ODE identity.",
                "common_misreading": "Confusing stochastic SDE paths with deterministic ODE streamlines.",
            }
        ],
        "color_identity": {"x_t": "matter", "score": "light", "p_t": "structure", "f_theta": "interaction"},
        "numbers": [
            {
                "name": "epsilon",
                "value": 0.002,
                "units": "time",
                "source": "offline",
            }
        ],
        "checks": ["offline rehearsal; no live ADK call"],
        "sources": [],
        "topic": request.prompt,
    }


def _shot_list() -> dict:
    return {
        "offline": True,
        "shots": [
            {
                "beat": i,
                "act_number": min(4, (i - 1) // 3 + 1),
                "verb": "HEADLINE" if i % 3 == 1 else ("TILT_3D" if i % 3 == 2 else "SHOW"),
                "target": f"stage_{i}",
                "params": {"phi": 60, "theta": -45},
                "caption_text": "Geometry before symbols.",
                "seconds": 3,
            }
            for i in range(1, 13)
        ],
        "camera_score": "Start flat, tilt into 3D space-time, zoom into the consistency map, and orbit to close.",
        "stills": [],
        "visual_seeds": [],
    }


def _scene_spec() -> dict:
    return {
        "offline": True,
        "scene_name": "ArgonOfflineJourney",
        "scene_class": "ThreeDScene",
        "palette": {"background": "#0c0c0b", "text": "#faf9f5"},
        "objects": [
            {"id": "title", "kind": "Text", "spec": "Argon Google ADK pipeline: offline rehearsal"}
        ],
        "timeline": [{"beat": 1, "verb": "HEADLINE", "target": "title"}],
        "constraints": [
            "Manim CE",
            "move_camera or set_camera_orientation only",
            "never .animate on the camera",
        ],
        "acceptance": ["one ThreeDScene", "camera rule held"],
    }


def offline_payloads(request: RunRequest) -> dict[str, dict]:
    """Deterministic stage payloads keyed by stage name."""
    tree = reverse_tree_for(request.prompt)
    return {
        "intent": _intent(request),
        "cartographer": tree,
        "curriculum": _curriculum(tree),
        "math-director": _math_dossier(request),
        "cinematographer": _shot_list(),
        "composer": _scene_spec(),
    }


def write_offline_bundle(run_dir: Path, request: RunRequest) -> None:
    """Write every stage artifact, its trace and the scene with zero network calls."""
    payloads = offline_payloads(request)
    for stage in STAGES:
        bundle.write_artifact(run_dir, stage, stage.prepare(payloads[stage.name]))
        bundle.write_trace(
            run_dir,
            stage.name,
            {
                "stage": stage.name,
                "offline": True,
                "sdk": "google-adk",
                "adk_agent_name": stage.agent_name,
                "model": OFFLINE_MODEL,
                "tools_requested": stage.tool_names,
                "tool_calls": [],
                "thinking": ["offline rehearsal; no Google ADK network call"],
            },
        )
    bundle.write_scene(run_dir, _OFFLINE_SCENE)
