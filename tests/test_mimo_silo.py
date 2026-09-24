"""Offline tests for the MiMo 2.6 tool-calling silo. No model calls."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from mimo.agents import AGENT_STAGES, build_stage_prompt, tools_for_stage
from mimo.models import RunRequest
from mimo.offline import write_offline_bundle
from mimo.tools import ToolContext, dispatch_tool
from mimo.validation import validate_run, validation_from_scene


def test_agent_stages_cover_chain():
    names = [stage.name for stage in AGENT_STAGES]
    assert names == [
        "intent",
        "cartographer",
        "curriculum",
        "math-director",
        "cinematographer",
        "scene-composer",
    ]


def test_scene_composer_has_verify_tools():
    names = {tool["function"]["name"] for tool in tools_for_stage("scene-composer")}
    assert {"verify_scene", "verify_geometry", "write_artifact"} <= names


def test_cartographer_prompt_requires_reverse_thinking():
    stage = next(s for s in AGENT_STAGES if s.name == "cartographer")
    prompt = build_stage_prompt(
        stage,
        RunRequest(prompt="explain spinors via a belt"),
        run_dir=Path("runs/mimo/test"),
    )
    assert "reverse" in prompt.lower()
    assert "02_knowledge_map.json" in prompt


def test_write_artifact_sandbox(tmp_path: Path):
    ctx = ToolContext(run_dir=tmp_path)
    result = dispatch_tool(
        ctx,
        "write_artifact",
        {"path": "01_intent.json", "content": json.dumps({"core_claim": "x"})},
    )
    assert result["ok"] is True
    assert (tmp_path / "01_intent.json").is_file()
    escaped = dispatch_tool(
        ctx,
        "write_artifact",
        {"path": "../escape.json", "content": "{}"},
    )
    assert escaped["ok"] is False


def test_verify_geometry_twist_parity(tmp_path: Path):
    ctx = ToolContext(run_dir=tmp_path)
    odd = dispatch_tool(ctx, "verify_geometry", {"kind": "ribbon", "twists": 1})
    even = dispatch_tool(ctx, "verify_geometry", {"kind": "ribbon", "twists": 2})
    assert odd["ok"] is True
    assert odd["twist_charge_parity"] == "odd"
    assert odd["untwistable_with_clamped_ends"] is False
    assert even["twist_charge_parity"] == "even"
    assert even["untwistable_with_clamped_ends"] is True


def test_verify_scene_camera_rule(tmp_path: Path):
    ctx = ToolContext(run_dir=tmp_path)
    bad = dispatch_tool(
        ctx,
        "verify_scene",
        {
            "source": (
                "from manim import *\n"
                "class Bad(Scene):\n"
                "    def construct(self):\n"
                "        self.play(self.camera.animate.set_euler_angles(1, 2, 3))\n"
            )
        },
    )
    assert bad["ok"] is False
    good_src = (
        "from manim import *\n"
        "class Good(ThreeDScene):\n"
        "    def construct(self):\n"
        "        self.set_camera_orientation(phi=1, theta=2)\n"
        "        self.move_camera(phi=1.2)\n"
    )
    good = dispatch_tool(ctx, "verify_scene", {"source": good_src})
    assert good["ok"] is True
    assert good["scene_name"] == "Good"


def test_offline_bundle_and_validate(tmp_path: Path):
    request = RunRequest(prompt="rehearse the MiMo tool pipeline", offline=True)
    write_offline_bundle(tmp_path, request)
    (tmp_path / "validation.json").write_text("{}", encoding="utf-8")
    failures, scene_name, _ = validate_run(tmp_path, require_video=False)
    # review.json is auto-spliced as skipped; offline scene must pass
    assert failures == []
    assert scene_name == "OfflineRehearsal"


def test_validation_blocks_imports():
    report = validation_from_scene(
        "import os\nfrom manim import *\nclass S(Scene):\n    def construct(self):\n        pass\n"
    )
    assert report["status"] == "failed"
    assert any("blocked import" in error for error in report["errors"])


def test_flagship_scene_is_3d_single_class():
    root = Path(__file__).resolve().parents[1]
    source = (root / "examples/mimo/the_second_turn.py").read_text(encoding="utf-8")
    report = validation_from_scene(source)
    assert report["errors"] == []
    assert report["scene_name"] == "TheSecondTurn"
    assert "set_camera_orientation" in source
    assert "720" in source
