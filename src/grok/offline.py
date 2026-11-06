"""Deterministic Grok chain rehearsal with zero xAI calls."""

from __future__ import annotations

import json
from pathlib import Path

from grok.models import ARTIFACT_NAMES, RunRequest
from grok.validation import verify_scene_report

_OFFLINE_SCENE = '''from manim import *


class GrokOfflineStory(ThreeDScene):
    """Deterministic rehearsal of the complete Grok artifact contract."""

    def construct(self):
        self.camera.background_color = "#0c0c0b"
        self.set_camera_orientation(phi=0 * DEGREES, theta=-90 * DEGREES)
        title = Text("Grok pipeline: offline rehearsal", color="#faf9f5")
        stages = VGroup(*[
            Text(label, font_size=24, color=color)
            for label, color in [
                ("intent", "#6a9bcc"),
                ("cartographer", "#d97757"),
                ("curriculum", "#e5b566"),
                ("math director", "#788c5d"),
                ("composer", "#d4a27f"),
            ]
        ]).arrange(DOWN, buff=0.25)
        self.play(FadeIn(title))
        self.play(title.animate.to_edge(UP), LaggedStart(*[FadeIn(item) for item in stages]))
        self.move_camera(phi=60 * DEGREES, theta=-45 * DEGREES, run_time=1.5)
        self.wait(0.5)
'''


def reverse_tree_for(prompt: str) -> dict:
    """Offline reverse knowledge tree. Depth 0 is the claim."""
    lowered = prompt.lower()
    if any(token in lowered for token in ("spring", "cart", "compress", "n/m", "kg")):
        target = (
            "A moving cart stores kinetic energy that a spring returns as "
            "compression distance once the energy balance is solved."
        )
        nodes = [
            {
                "id": "claim",
                "name": "energy balance to compression",
                "why_needed": "This is the solved insight the film must earn.",
                "depth": 0,
                "assumed": False,
                "visual_seed": "a cart kissing a coil and the coil shortening",
            },
            {
                "id": "energy",
                "name": "kinetic energy equals spring energy",
                "why_needed": "The claim is an equality of two stored energies.",
                "depth": 1,
                "assumed": False,
                "visual_seed": "two bars of equal height, motion and stretch",
            },
            {
                "id": "spring-law",
                "name": "Hooke energy one half k x squared",
                "why_needed": "Compression is the unknown inside spring energy.",
                "depth": 2,
                "assumed": False,
                "visual_seed": "a coil whose stored energy rises with stretch",
            },
            {
                "id": "motion-energy",
                "name": "kinetic energy one half m v squared",
                "why_needed": "The cart arrives with a known mass and speed.",
                "depth": 2,
                "assumed": False,
                "visual_seed": "a mass with a speed arrow turning into a glow",
            },
            {
                "id": "symbols",
                "name": "mass, speed, and stiffness as given quantities",
                "why_needed": "The audience already reads m, v, and k on a worksheet.",
                "depth": 3,
                "assumed": True,
                "visual_seed": "three labeled givens on a page",
            },
        ]
        edges = [
            ["energy", "claim"],
            ["spring-law", "energy"],
            ["motion-energy", "energy"],
            ["symbols", "spring-law"],
            ["symbols", "motion-energy"],
        ]
        spine = ["symbols", "motion-energy", "energy", "claim"]
    elif any(token in lowered for token in ("heat", "fourier", "diffusion")):
        target = (
            "Fourier modes solve the heat equation because each sine wave "
            "is an eigenvector of the second derivative."
        )
        nodes = [
            {
                "id": "claim",
                "name": "Fourier modes solve the heat equation",
                "why_needed": "This is the core claim the film must make visible.",
                "depth": 0,
                "assumed": False,
                "visual_seed": "a hot bump flattening as clean waves decay",
            },
            {
                "id": "eigen",
                "name": "sines are eigenvectors of the second derivative",
                "why_needed": "The PDE becomes a simple decay law only then.",
                "depth": 1,
                "assumed": False,
                "visual_seed": "a sine staying a sine while its height drops",
            },
            {
                "id": "heat-law",
                "name": "the heat equation as a local smoothing law",
                "why_needed": "The viewer must see what is being solved.",
                "depth": 2,
                "assumed": False,
                "visual_seed": "hot spots leaking into cooler neighbors",
            },
            {
                "id": "waves",
                "name": "sines as standing waves on an interval",
                "why_needed": "Modes are the vocabulary of the solution.",
                "depth": 2,
                "assumed": False,
                "visual_seed": "a string with one, then two, then three humps",
            },
            {
                "id": "derivatives",
                "name": "first and second derivatives of a graph",
                "why_needed": "The audience already reads slope and curvature.",
                "depth": 3,
                "assumed": True,
                "visual_seed": "a curve with slope ticks and a curvature bowl",
            },
        ]
        edges = [
            ["eigen", "claim"],
            ["heat-law", "eigen"],
            ["waves", "eigen"],
            ["derivatives", "heat-law"],
            ["derivatives", "waves"],
        ]
        spine = ["derivatives", "heat-law", "eigen", "claim"]
    else:
        target = f"The film earns this request: {prompt.strip()[:180]}"
        nodes = [
            {
                "id": "claim",
                "name": "the requested insight",
                "why_needed": "Depth 0 is always the core claim, not a topic label.",
                "depth": 0,
                "assumed": False,
                "visual_seed": "the final picture the viewer can now see",
            },
            {
                "id": "mechanism",
                "name": "the mechanism that makes the claim true",
                "why_needed": "The claim is empty until its engine is visible.",
                "depth": 1,
                "assumed": False,
                "visual_seed": "the moving part that carries the argument",
            },
            {
                "id": "quantity",
                "name": "the quantities the mechanism acts on",
                "why_needed": "A mechanism without named quantities cannot be checked.",
                "depth": 2,
                "assumed": False,
                "visual_seed": "labeled magnitudes waiting to move",
            },
            {
                "id": "foundations",
                "name": "notation and ideas the audience already owns",
                "why_needed": "Reverse thinking stops where the learner already is.",
                "depth": 3,
                "assumed": True,
                "visual_seed": "a nod, not a lesson",
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
        "core_claim": f"A visual argument can earn this request: {request.prompt}",
        "audience": "a curious learner who can read the given symbols",
        "emotional_arc": ["curiosity", "tension", "revelation", "awe"],
        "scope": {"in": [request.prompt], "out": ["unrelated survey material"]},
        "duration_seconds": 120,
        "title_options": ["The Earned Picture", "One Claim", "Reverse Then Forward"],
        "the_big_zoom": "the camera enters the symbol that carries the claim",
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
                "estimated_seconds": 20,
            }
        )
    return {
        "offline": True,
        "acts": acts,
        "through_line": "The spine walks from assumed foundations to the claim.",
    }


def _math_dossier(request: RunRequest) -> dict:
    return {
        "offline": True,
        "formulas": [
            {
                "id": "F1",
                "act_number": 2,
                "latex_parts": [r"E", r"=", r"\\tfrac{1}{2}", r"mv^2"],
                "term_glossary": [
                    {
                        "part_index": 0,
                        "plain_words": "Energy stored in the motion.",
                        "identity": "mass",
                        "zoom_worthy": True,
                    }
                ],
                "derivation_or_motivation": "Offline rehearsal uses a stand-in identity.",
                "common_misreading": "Treating symbols as decoration instead of quantities.",
            }
        ],
        "color_identity": {"E": "mass", "m": "matter", "v": "interaction"},
        "numbers": [
            {
                "name": "rehearsal",
                "value": 1,
                "units": "dimensionless",
                "source": "offline",
            }
        ],
        "checks": ["offline rehearsal; no code_interpreter call"],
        "sources": [],
        "topic": request.prompt,
    }


def _shot_list() -> dict:
    return {
        "offline": True,
        "shots": [
            {
                "beat": 1,
                "act_number": 1,
                "verb": "HEADLINE",
                "target": "title",
                "params": {},
                "caption_text": None,
                "seconds": 2,
            },
            {
                "beat": 2,
                "act_number": 2,
                "verb": "TILT_3D",
                "target": "stage",
                "params": {"phi": 60, "theta": -45},
                "caption_text": "Space when space is the idea.",
                "seconds": 2,
            },
        ],
        "camera_score": "Start flat, then tilt once the claim needs space.",
        "stills": [],
        "visual_seeds": [],
    }


def _scene_spec() -> dict:
    return {
        "offline": True,
        "scene_name": "GrokOfflineStory",
        "scene_class": "ThreeDScene",
        "palette": {"background": "#0c0c0b", "text": "#faf9f5"},
        "objects": [
            {"id": "title", "kind": "Text", "spec": "Grok pipeline: offline rehearsal"}
        ],
        "timeline": [{"beat": 1, "verb": "HEADLINE", "target": "title"}],
        "constraints": [
            "Manim CE",
            "move_camera or set_camera_orientation only",
            "never .animate on the camera",
        ],
        "acceptance": ["one ThreeDScene", "camera rule held"],
    }


def _trace(stage: str, tools: list[str]) -> dict:
    return {
        "stage": stage,
        "offline": True,
        "model": "offline",
        "tools_requested": tools,
        "tool_calls": [],
        "thinking": ["offline rehearsal; no xAI call"],
    }


def write_offline_bundle(run_dir: Path, request: RunRequest) -> dict:
    tree = reverse_tree_for(request.prompt)
    artifacts = {
        "01_intent.json": _intent(request),
        "02_knowledge_map.json": tree,
        "03_curriculum.json": _curriculum(tree),
        "04_math_dossier.json": _math_dossier(request),
        "05_shot_list.json": _shot_list(),
        "06_scene_spec.json": _scene_spec(),
        "review.json": {
            "offline": True,
            "checks": ["artifact contract", "reverse tree", "python compilation"],
            "rendered": False,
            "limitations": ["deterministic rehearsal; no xAI call"],
        },
        "validation.json": verify_scene_report(_OFFLINE_SCENE),
    }
    for name, payload in artifacts.items():
        (run_dir / name).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    (run_dir / "grok_scene.py").write_text(_OFFLINE_SCENE, encoding="utf-8")

    traces = run_dir / "traces"
    traces.mkdir(exist_ok=True)
    stage_tools = {
        "intent": [],
        "cartographer": ["web_search"],
        "curriculum": [],
        "math-director": ["code_interpreter", "web_search"],
        "cinematographer": ["image_generation", "x_search"],
        "composer": ["verify_scene"],
    }
    for stage, tools in stage_tools.items():
        (traces / f"{stage}.json").write_text(
            json.dumps(_trace(stage, tools), indent=2),
            encoding="utf-8",
        )
    assert all((run_dir / name).is_file() for name in ARTIFACT_NAMES)
    return {
        "status": "completed",
        "scene_file": "grok_scene.py",
        "scene_name": "GrokOfflineStory",
        "artifacts": list(ARTIFACT_NAMES),
    }
