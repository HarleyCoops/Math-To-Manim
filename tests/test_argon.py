"""Offline unit tests for the Argon Google Agent SDK (google-adk + google-genai) pipeline."""

from __future__ import annotations

from pathlib import Path

from google.adk.agents import LlmAgent, SequentialAgent

from argon.charters import STAGES, all_charters, cinematic_charter
from argon.client import build_adk_sequential_pipeline, build_stage_adk_agent, redact_secret
from argon.models import ARTIFACT_NAMES, RunRequest
from argon.service import ArgonService
from argon.tools import execute_math_check, verify_scene
from argon.validation import normalize_reverse_tree, validate_reverse_tree, validate_run, verify_scene_report

ROOT = Path(__file__).resolve().parents[1]


def test_adk_sequential_pipeline_builds_six_llm_agents():
    pipeline = build_adk_sequential_pipeline(model="gemini-2.5-pro", reasoning_effort="high")
    assert isinstance(pipeline, SequentialAgent)
    assert len(pipeline.sub_agents) == 6
    for stage, agent in zip(STAGES, pipeline.sub_agents):
        assert isinstance(agent, LlmAgent)
        assert agent.output_key == stage.artifact


def test_charters_and_tools():
    charters = all_charters()
    assert set(charters.keys()) == {s.name for s in STAGES}
    assert "ThreeDScene" in cinematic_charter()

    math_res = execute_math_check("round(sqrt(2.0**2 - 0.35**2), 4)")
    assert math_res["ok"] is True
    assert math_res["value"] == 1.9691

    bad_scene = verify_scene("from manim import *\nclass S(ThreeDScene):\n def construct(self):\n  self.play(self.camera.animate.shift(UP))\n")
    assert bad_scene["passed"] is False
    assert any("never animate self.camera" in e for e in bad_scene["errors"])


def test_offline_argon_run(tmp_path: Path):
    service = ArgonService(runs_dir=tmp_path)
    manifest = service.run(
        RunRequest(
            prompt="Explain Continuous-Time Score SDEs and Consistency Models",
            offline=True,
        )
    )
    assert manifest["status"] == "completed"
    assert manifest["sdk"] == "google-adk + google-genai"
    run_dir = tmp_path / manifest["run_id"]
    failures, scene_name, _ = validate_run(run_dir, require_video=False)
    assert not failures
    assert scene_name == "ArgonOfflineJourney"
    for name in ARTIFACT_NAMES:
        assert (run_dir / name).is_file()


def test_showcase_stage_bundle_validates():
    showcase_dir = ROOT / "docs" / "showcase" / "score-sde-consistency"
    tree = normalize_reverse_tree(
        __import__("json").loads((showcase_dir / "02_knowledge_map.json").read_text(encoding="utf-8"))
    )
    assert validate_reverse_tree(tree) == []
    scene_report = verify_scene_report((showcase_dir / "argon_scene.py").read_text(encoding="utf-8"))
    assert scene_report["passed"] is True
    assert scene_report["scene_name"] == "ScoreSDEConsistencyJourney"


def test_redact_secret_never_leaks():
    assert redact_secret("Error with key AIzaSySecretKey12345", "AIzaSySecretKey12345") == "Error with key [redacted]"
