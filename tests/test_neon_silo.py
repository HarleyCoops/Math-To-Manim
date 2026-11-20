"""Unit tests for the Gemini 4 Neon-first silo."""

from __future__ import annotations

import json
from pathlib import Path

from neon import DEFAULT_MODEL
from neon.harness import NeonHarness
from neon.models import PLAN_FILE, SCENE_FILE, NeonPlan, NeonRequest
from neon.tools import check_scene, verify_math


VALID_SCENE = '''from manim import *
import numpy as np

class TinyNeonScene(ThreeDScene):
    def construct(self):
        self.set_camera_orientation(phi=65 * DEGREES, theta=-45 * DEGREES)
        title = Tex(r"Neon Test")
        self.add_fixed_in_frame_mobjects(title)
        self.play(FadeIn(title))
        self.wait(0.5)
'''


def test_default_model_is_gemini_4_neon():
    assert DEFAULT_MODEL == "gemini-4-neon"


def test_verify_math_supports_real_and_complex():
    r1 = verify_math("sqrt(100)")
    assert r1["ok"] is True
    assert r1["value"] == 10.0

    r2 = verify_math("abs(complex(0.5, 14.134725))")
    assert r2["ok"] is True
    assert r2["value"] > 14.1

    r3 = verify_math("__import__('os').system('echo nope')")
    assert r3["ok"] is False


def test_check_scene_accepts_valid_and_rejects_banned():
    ok = check_scene(VALID_SCENE)
    assert ok["passed"] is True
    assert ok["scene_class"] == "TinyNeonScene"

    bad = check_scene("import os\nclass Bad(ThreeDScene):\n    def construct(self): pass\n")
    assert bad["passed"] is False
    assert any("banned import" in e for e in bad["errors"])


def test_operator_harness_runs_without_render(tmp_path: Path):
    ws = tmp_path / "ws"
    ws.mkdir()
    plan = NeonPlan(
        title="Tiny Test",
        slug="tiny-test",
        subtitle="Unit test",
        core_thesis="Check operator harness.",
        math_checks=[{"label": "sqrt100", "expression": "sqrt(100)", "expected_note": "10"}],
        scene_class="TinyNeonScene",
    )
    (ws / PLAN_FILE).write_text(plan.model_dump_json(indent=2), encoding="utf-8")
    (ws / SCENE_FILE).write_text(VALID_SCENE, encoding="utf-8")

    harness = NeonHarness(runs_dir=tmp_path / "runs", repo_root=tmp_path)
    manifest = harness.run(
        NeonRequest(
            prompt="Tiny test",
            backend="operator",
            workspace=str(ws),
            render=False,
        )
    )
    assert manifest["status"]["run"] == "completed"
    assert manifest["status"]["outcome"] == "scene_ready"
    assert manifest["scene_class"] == "TinyNeonScene"
    assert manifest["tool_calls_count"] == 2
