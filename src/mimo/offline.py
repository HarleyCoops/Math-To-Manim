"""Deterministic offline bundle for the MiMo tool-calling pipeline (no model calls)."""

from __future__ import annotations

import json
from pathlib import Path

from mimo.models import RunRequest


def write_offline_bundle(run_dir: Path, request: RunRequest) -> dict:
    run_dir = Path(run_dir)
    (run_dir / "01_intent.json").write_text(
        json.dumps(
            {
                "core_claim": request.prompt[:180],
                "audience": "curious technical learners",
                "emotional_arc": ["curiosity", "tension", "revelation"],
                "scope": {"in": [request.prompt], "out": ["live web", "other silos"]},
                "duration_seconds": 90,
                "title_options": ["Offline Rehearsal", "Contract Check", "Dry Run"],
                "the_big_zoom": "dive into the central object and reveal structure",
                "offline": True,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (run_dir / "02_knowledge_map.json").write_text(
        json.dumps(
            {
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
            indent=2,
        ),
        encoding="utf-8",
    )
    (run_dir / "03_curriculum.json").write_text(
        json.dumps(
            {
                "beats": [
                    {
                        "id": "b1",
                        "learning_job": "name the object",
                        "visual_evidence": "object on stage",
                        "notation_budget": "none",
                    }
                ]
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (run_dir / "04_math_dossier.json").write_text(
        json.dumps(
            {
                "statements": ["offline rehearsal does not assert new theorems"],
                "constants": {"samples": 128},
                "checks": ["offline only"],
                "limitations": ["no live model", "no render required"],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (run_dir / "05_shot_list.json").write_text(
        json.dumps(
            {
                "palette": {"ink": "#0b0d10", "bone": "#f2ead8"},
                "shots": [{"id": "S0", "camera": "wide", "seconds": 6}],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (run_dir / "06_scene_spec.json").write_text(
        json.dumps(
            {
                "scene_class": "OfflineRehearsal",
                "engine": "Manim CE",
                "self_contained": True,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    scene = '''"""Offline MiMo rehearsal scene (no model)."""

from __future__ import annotations

from manim import *


class OfflineRehearsal(Scene):
    def construct(self) -> None:
        label = Text("MiMo offline rehearsal")
        self.play(Write(label))
        self.wait(0.2)
'''
    (run_dir / "mimo_scene.py").write_text(scene, encoding="utf-8")
    return {
        "status": "completed",
        "scene_file": "mimo_scene.py",
        "scene_name": "OfflineRehearsal",
        "artifacts": [
            "01_intent.json",
            "02_knowledge_map.json",
            "03_curriculum.json",
            "04_math_dossier.json",
            "05_shot_list.json",
            "06_scene_spec.json",
            "mimo_scene.py",
        ],
        "rendered": False,
        "video_path": None,
        "checks": ["offline-bundle-written"],
        "notes": ["offline mode: zero model calls, zero tool dispatch"],
        "tool_calls": [],
    }
