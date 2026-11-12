"""Deterministic offline bundle for the MiMo tool-calling pipeline (no model calls).

Writes exactly the stage artifacts the stage table declares, so the offline
rehearsal exercises the same validation and manifest path as a live run.
"""

from __future__ import annotations

import json
from pathlib import Path

from mimo.agents import STAGE_ARTIFACTS
from mimo.models import SCENE_FILE, PipelineResult, RunRequest

OFFLINE_SCENE_NAME = "OfflineRehearsal"

OFFLINE_SCENE = f'''"""Offline MiMo rehearsal scene (no model)."""

from __future__ import annotations

from manim import *


class {OFFLINE_SCENE_NAME}(Scene):
    def construct(self) -> None:
        label = Text("MiMo offline rehearsal")
        self.play(Write(label))
        self.wait(0.2)
'''


def offline_artifacts(request: RunRequest) -> dict[str, dict]:
    """JSON payload per stage artifact, in stage order."""
    return {
        "01_intent.json": {
            "core_claim": request.prompt[:180],
            "audience": "curious technical learners",
            "emotional_arc": ["curiosity", "tension", "revelation"],
            "scope": {"in": [request.prompt], "out": ["live web", "other silos"]},
            "duration_seconds": 90,
            "title_options": ["Offline Rehearsal", "Contract Check", "Dry Run"],
            "the_big_zoom": "dive into the central object and reveal structure",
            "offline": True,
        },
        "02_knowledge_map.json": {
            "method": "reverse-knowledge-tree",
            "root": request.prompt,
            "nodes": [
                {"concept": request.prompt, "depth": 0, "is_foundation": False},
                {"concept": "3D space and arrows", "depth": 1, "is_foundation": True},
                {"concept": "continuous motion", "depth": 1, "is_foundation": True},
            ],
            "edges": [
                {"from": request.prompt, "to": "3D space and arrows"},
                {"from": request.prompt, "to": "continuous motion"},
            ],
        },
        "03_curriculum.json": {
            "beats": [
                {
                    "id": "b1",
                    "learning_job": "name the object",
                    "visual_evidence": "object on stage",
                    "notation_budget": "none",
                }
            ]
        },
        "04_math_dossier.json": {
            "statements": ["offline rehearsal does not assert new theorems"],
            "constants": {"samples": 128},
            "checks": ["offline only"],
            "limitations": ["no live model", "no render required"],
        },
        "05_shot_list.json": {
            "palette": {"ink": "#0b0d10", "bone": "#f2ead8"},
            "shots": [{"id": "S0", "camera": "wide", "seconds": 6}],
        },
        "06_scene_spec.json": {
            "scene_class": OFFLINE_SCENE_NAME,
            "engine": "Manim CE",
            "self_contained": True,
        },
    }


def write_offline_bundle(run_dir: Path, request: RunRequest) -> PipelineResult:
    run_dir = Path(run_dir)
    payloads = offline_artifacts(request)
    written = tuple(payloads) + (SCENE_FILE,)
    if written != STAGE_ARTIFACTS:
        raise RuntimeError(f"offline bundle {written} does not match stage artifacts {STAGE_ARTIFACTS}")
    for name, payload in payloads.items():
        (run_dir / name).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    (run_dir / SCENE_FILE).write_text(OFFLINE_SCENE, encoding="utf-8")
    return PipelineResult(
        artifacts=list(written),
        checks=["offline-bundle-written"],
        notes=["offline mode: zero model calls, zero tool dispatch"],
    )
