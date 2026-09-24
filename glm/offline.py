"""Deterministic GLM chain rehearsal with zero Z.ai calls."""

from __future__ import annotations

import json
from pathlib import Path

from glm.models import ARTIFACT_NAMES, PAPER_STAGE_COLOR, RunRequest
from glm.validation import verify_scene_report

_OFFLINE_SCENE = """from manim import *


class GlmOfflineStory(ThreeDScene):
    \"\"\"Deterministic rehearsal of the complete GLM artifact contract.\"\"\"

    def construct(self):
        # Paper stage, ink text: the GLM house look, no network, no files.
        self.camera.background_color = "#f3ecd8"
        self.set_camera_orientation(phi=0 * DEGREES, theta=-90 * DEGREES)
        ink = "#2b261f"
        title = Text("GLM pipeline: offline rehearsal", color=ink)
        stages = VGroup(*[
            Text(label, font_size=24, color=color)
            for label, color in [
                ("intent", "#3d5a80"),
                ("cartographer", "#9a3b26"),
                ("curriculum", "#7c6a46"),
                ("math director", "#4d6a55"),
                ("composer", "#6b4f8a"),
            ]
        ]).arrange(DOWN, buff=0.25)
        self.play(FadeIn(title))
        title.to_edge(UP, buff=0.5)
        self.play(LaggedStart(*[FadeIn(item) for item in stages]))
        self.move_camera(phi=58 * DEGREES, theta=-42 * DEGREES, run_time=1.5)
        self.wait(0.5)
"""


def reverse_tree_for(prompt: str) -> dict:
    """Offline reverse knowledge tree. Depth 0 is the claim."""
    lowered = prompt.lower()
    if any(
        token in lowered
        for token in ("monopole", "magnet", "pole", "dirac", "flux", "dipole")
    ):
        target = (
            "A magnetic monopole would make Gauss's magnetism law count "
            "sources, and Dirac saw that this packs flux tubes onto a sphere, "
            "quantizing charge itself."
        )
        nodes = [
            {
                "id": "claim",
                "name": "a lone pole would quantize charge",
                "why_needed": "This is the solved insight the film must earn.",
                "depth": 0,
                "assumed": False,
                "visual_seed": "radial rays piercing a closed surface",
            },
            {
                "id": "gauss-divergence",
                "name": "Gauss's law counts net flux through a closed surface",
                "why_needed": "The claim is read off by counting rays.",
                "depth": 1,
                "assumed": False,
                "visual_seed": "rays crossing a translucent shell outward",
            },
            {
                "id": "no-poles-here",
                "name": "every dipole field line is a closed loop",
                "why_needed": "Nothing escapes a dipole; flux in equals flux out.",
                "depth": 2,
                "assumed": False,
                "visual_seed": "figure-eight loops that always come home",
            },
            {
                "id": "pack-quantum",
                "name": "integer packing of flux quanta on a sphere",
                "why_needed": "Dirac's condition is a whole-number statement.",
                "depth": 2,
                "assumed": False,
                "visual_seed": "equal tubes tiled without gaps or overlap",
            },
            {
                "id": "field-lines",
                "name": "how arrows on a page trace a field",
                "why_needed": "The audience already reads drawings of fields.",
                "depth": 3,
                "assumed": True,
                "visual_seed": "compass needles falling along a sketch",
            },
        ]
        edges = [
            ["gauss-divergence", "claim"],
            ["no-poles-here", "gauss-divergence"],
            ["pack-quantum", "claim"],
            ["field-lines", "no-poles-here"],
            ["field-lines", "pack-quantum"],
        ]
        spine = ["field-lines", "gauss-divergence", "claim"]
    elif any(token in lowered for token in ("heat", "fourier", "diffusion")):
        target = (
            "Fourier modes solve the heat equation because each sine is an "
            "eigenvector of curvature-driven smoothing."
        )
        nodes = [
            {
                "id": "claim",
                "name": "sine waves dissolve the heat equation into decay",
                "why_needed": "The claim turns calculus into calm arithmetic.",
                "depth": 0,
                "assumed": False,
                "visual_seed": "a hot bump flattening as clean waves sink",
            },
            {
                "id": "eigen",
                "name": "second derivative flips a sine back at itself",
                "why_needed": "Only then does the PDE become simple decay.",
                "depth": 1,
                "assumed": False,
                "visual_seed": "a wave staying wavy while its height drops",
            },
            {
                "id": "smoothing",
                "name": "heat flow erases sharp differences nearby",
                "why_needed": "The viewer must see what is being solved.",
                "depth": 2,
                "assumed": False,
                "visual_seed": "hot spots leaking into cold neighbors",
            },
            {
                "id": "graphs",
                "name": "slope and curvature of an ordinary graph",
                "why_needed": "Reverse thinking stops where learners nod.",
                "depth": 3,
                "assumed": True,
                "visual_seed": "tangent ticks and a curvature bowl",
            },
        ]
        edges = [
            ["eigen", "claim"],
            ["smoothing", "eigen"],
            ["graphs", "smoothing"],
        ]
        spine = ["graphs", "smoothing", "eigen", "claim"]
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
        "title_options": ["Paper and Ink", "One Claim", "Thinking Out Loud"],
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
                "latex_parts": [r"\Phi", r"=", r"\oint", r"B", r"\cdot", r"dA"],
                "term_glossary": [
                    {
                        "part_index": 2,
                        "plain_words": "Add up every ray piercing the skin.",
                        "identity": "closed-surface integral",
                        "zoom_worthy": True,
                    }
                ],
                "derivation_or_motivation":
                    "Offline rehearsal uses a stand-in identity.",
                "common_misreading": "Reading a dot product as decoration.",
            }
        ],
        "color_identity": {"Phi": "flux count", "B": "field", "A": "surface"},
        "numbers": [
            {
                "name": "rehearsal",
                "value": 1,
                "units": "dimensionless",
                "source": "offline",
            }
        ],
        "checks": ["offline rehearsal; no sandbox call"],
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
                "params": {"phi": 58, "theta": -42},
                "caption_text": "Space when space is the idea.",
                "seconds": 2,
            },
        ],
        "camera_score": "Start flat over the paper stage, then tilt once.",
        "stills": [],
        "visual_seeds": [],
    }


def _scene_spec() -> dict:
    return {
        "offline": True,
        "scene_name": "GlmOfflineStory",
        "scene_class": "ThreeDScene",
        "palette": {"background": PAPER_STAGE_COLOR, "text": "#2b261f"},
        "objects": [
            {"id": "title", "kind": "Text", "spec": "GLM pipeline: offline rehearsal"}
        ],
        "timeline": [{"beat": 1, "verb": "HEADLINE", "target": "title"}],
        "constraints": [
            "Manim CE",
            "set_camera_orientation or move_camera only",
            "never .animate on the camera",
            "paper stage #f3ecd8",
        ],
        "acceptance": ["one ThreeDScene", "camera rule held", "paper palette"],
    }


def _trace(stage: str, tools: list[str]) -> dict:
    return {
        "stage": stage,
        "offline": True,
        "model": "offline",
        "thinking_enabled": False,
        "tools_requested": tools,
        "tool_calls": [],
        "thinking": ["offline rehearsal; no Z.ai call"],
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
            "limitations": ["deterministic rehearsal; no Z.ai call"],
        },
        "validation.json": verify_scene_report(_OFFLINE_SCENE),
    }
    for name, payload in artifacts.items():
        (run_dir / name).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    (run_dir / "glm_scene.py").write_text(_OFFLINE_SCENE, encoding="utf-8")

    traces = run_dir / "traces"
    traces.mkdir(exist_ok=True)
    stage_tools = {
        "intent": [],
        "cartographer": ["web_search"],
        "curriculum": [],
        "math-director": ["code_interpreter", "web_search"],
        "cinematographer": ["web_search"],
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
        "scene_file": "glm_scene.py",
        "scene_name": "GlmOfflineStory",
        "artifacts": list(ARTIFACT_NAMES),
    }
