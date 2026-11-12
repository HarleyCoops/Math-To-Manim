"""Offline unit tests for the Argon Google Agent SDK (google-adk + google-genai) pipeline."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
from google.adk.agents import LlmAgent

from argon import bundle
from argon.client import build_stage_adk_agent
from argon.harness import ArgonHarness
from argon.models import REVIEW_FILE, SCENE_FILE, VALIDATION_FILE, RunRequest
from argon.offline import offline_payloads
from argon.settings import redact_secret
from argon.stages import COMPOSER, STAGES, all_charters
from argon.tools import execute_math_check, verify_scene
from argon.validation import (
    normalize_reverse_tree,
    validate_reverse_tree,
    verify_scene_report,
)

ROOT = Path(__file__).resolve().parents[1]
SHOWCASE = ROOT / "docs" / "showcase" / "score-sde-consistency"
sys.path.insert(0, str(ROOT / "scripts"))

import operate_argon_chain


def test_stage_table_is_the_single_source():
    assert [stage.artifact for stage in STAGES] == [
        "01_intent.json",
        "02_knowledge_map.json",
        "03_curriculum.json",
        "04_math_dossier.json",
        "05_shot_list.json",
        "06_scene_spec.json",
    ]
    assert [stage.name for stage in STAGES if stage.accepts_image] == ["intent"]
    assert COMPOSER.name == "composer" and COMPOSER.tools == (verify_scene,)
    assert COMPOSER.agent_name == "argon_composer"
    assert next(s for s in STAGES if s.name == "math-director").agent_name == "argon_math_director"
    assert set(all_charters()) == {stage.name for stage in STAGES}
    for stage in STAGES:
        assert "tools:" not in stage.charter().split("---")[1]


def test_build_stage_adk_agent_from_table():
    for stage in STAGES:
        agent = build_stage_adk_agent(stage, model="gemini-2.5-pro", reasoning_effort="high")
        assert isinstance(agent, LlmAgent)
        assert agent.name == stage.agent_name
        assert agent.output_key == stage.artifact
        assert list(agent.tools) == list(stage.tools)


def test_tools():
    math_res = execute_math_check("round(sqrt(2.0**2 - 0.35**2), 4)")
    assert math_res["ok"] is True
    assert math_res["value"] == 1.9691

    bad_scene = verify_scene(
        "from manim import *\nclass S(ThreeDScene):\n def construct(self):\n  self.play(self.camera.animate.shift(UP))\n"
    )
    assert bad_scene["passed"] is False
    assert any("never animate self.camera" in e for e in bad_scene["errors"])


def test_offline_argon_run(tmp_path: Path):
    progress: list[str] = []
    harness = ArgonHarness(runs_dir=tmp_path, progress=progress.append)
    manifest = harness.run(
        RunRequest(prompt="Explain Continuous-Time Score SDEs and Consistency Models", offline=True)
    )
    assert manifest["status"] == "completed"
    assert manifest["sdk"] == "google-adk + google-genai"
    assert manifest["scene_name"] == "ArgonOfflineJourney"
    run_dir = tmp_path / manifest["run_id"]
    failures, scene_name = bundle.validate_run(run_dir)
    assert not failures
    assert scene_name == "ArgonOfflineJourney"
    for name in bundle.BUNDLE_FILES:
        assert (run_dir / name).is_file()
    assert manifest["artifacts"] == {name: name for name in bundle.BUNDLE_FILES}
    for stage in STAGES:
        trace = json.loads((run_dir / "traces" / f"{stage.name}.json").read_text(encoding="utf-8"))
        assert trace["tools_requested"] == stage.tool_names
    assert json.loads((run_dir / VALIDATION_FILE).read_text(encoding="utf-8"))["passed"] is True
    review = json.loads((run_dir / REVIEW_FILE).read_text(encoding="utf-8"))
    assert review["offline"] is True and review["rendered"] is False
    assert not list(run_dir.rglob("__pycache__"))
    assert progress == []  # offline runs make no stage calls

    assert bundle.load_manifest(tmp_path, manifest["run_id"]).status == "completed"
    assert [m.run_id for m in bundle.list_manifests(tmp_path)] == [manifest["run_id"]]
    with pytest.raises(ValueError):
        bundle.run_dir_for(tmp_path, "../escape")


def test_offline_payloads_satisfy_stage_checks():
    payloads = offline_payloads(RunRequest(prompt="Explain the Hopf fibration"))
    for stage in STAGES:
        stage.prepare(payloads[stage.name])


def test_validate_run_reports_contract_failures(tmp_path: Path):
    failures, scene_name = bundle.validate_run(tmp_path)
    assert scene_name is None
    assert f"missing required artifact: {SCENE_FILE}" in failures
    assert all(f"missing required artifact: {stage.artifact}" in failures for stage in STAGES)

    bad_tree = {"target": "x", "nodes": [{"id": "a", "depth": 0, "assumed": True}], "edges": [], "spine": []}
    (tmp_path / "02_knowledge_map.json").write_text(json.dumps(bad_tree), encoding="utf-8")
    failures, _ = bundle.validate_run(tmp_path)
    assert any("depth 0 target must not be assumed" in f for f in failures)


def test_showcase_stage_bundle_validates():
    tree = normalize_reverse_tree(json.loads((SHOWCASE / "02_knowledge_map.json").read_text(encoding="utf-8")))
    assert validate_reverse_tree(tree) == []
    scene_report = verify_scene_report((SHOWCASE / "argon_scene.py").read_text(encoding="utf-8"))
    assert scene_report["passed"] is True
    assert scene_report["scene_name"] == "ScoreSDEConsistencyJourney"


def test_operator_script_records_showcase_bundle(tmp_path: Path):
    rc, run_dir = operate_argon_chain.operate(SHOWCASE, runs_dir=tmp_path, model="gemini-4-argon")
    assert rc == 0 and run_dir is not None
    manifest = bundle.load_manifest(tmp_path, run_dir.name)
    assert manifest.status == "completed"
    assert manifest.backend == "argon-operator"
    assert manifest.scene_name == "ScoreSDEConsistencyJourney"
    assert [s["adk_agent"] for s in manifest.stages] == [stage.agent_name for stage in STAGES]
    math_trace = json.loads((run_dir / "traces" / "math-director.json").read_text(encoding="utf-8"))
    assert math_trace["tool_calls"] and all(c["tool"] == "execute_math_check" for c in math_trace["tool_calls"])
    composer_trace = json.loads((run_dir / "traces" / "composer.json").read_text(encoding="utf-8"))
    assert composer_trace["tool_calls"][0]["output"]["passed"] is True
    failures, _ = bundle.validate_run(run_dir)
    assert failures == []


def test_operator_script_asks_for_missing_reply(tmp_path: Path):
    stages = tmp_path / "stages"
    stages.mkdir()
    (stages / "prompt.txt").write_text("Explain the Hopf fibration", encoding="utf-8")
    rc, run_dir = operate_argon_chain.operate(stages, runs_dir=tmp_path / "runs")
    assert rc == operate_argon_chain.NEEDS_REPLY and run_dir is None
    assert (stages / "NEXT_PROMPT.txt").is_file()
    assert not (tmp_path / "runs").exists()


def test_redact_secret_never_leaks():
    assert redact_secret("Error with key AIzaSySecretKey12345", "AIzaSySecretKey12345") == "Error with key [redacted]"


_GOOD_SCENE = (
    "from manim import *\n\nclass FakeJourney(ThreeDScene):\n    def construct(self):\n"
    "        self.set_camera_orientation(phi=60 * DEGREES)\n"
)
_BAD_SCENE = _GOOD_SCENE.replace("set_camera_orientation(phi=60 * DEGREES)", "play(self.camera.animate.shift(UP))")


class FakeClient:
    """Stands in for ArgonClient: one scripted reply per stage, a bad scene first."""

    model = "fake-gemini"

    def __init__(self):
        self.calls: list[tuple[str, str, Path | None]] = []
        self.payloads = offline_payloads(RunRequest(prompt="fake"))
        self.scenes = [_BAD_SCENE, _GOOD_SCENE]

    def require_key(self) -> str:
        return "k" * 16

    def complete(self, stage, *, text, reasoning_effort, instructions=None, image_path=None):
        from argon.models import StageCallResult

        self.calls.append((stage.name, reasoning_effort, image_path))
        payload = dict(self.payloads[stage.name])
        if stage.writes_scene:
            payload["source"] = self.scenes.pop(0)
        return StageCallResult(text=json.dumps(payload), payload=payload)


def test_live_run_with_injected_client_repairs_scene(tmp_path: Path):
    image = tmp_path / "diagram.png"
    image.write_bytes(b"\x89PNG")
    client = FakeClient()
    progress: list[str] = []
    manifest = ArgonHarness(runs_dir=tmp_path, client=client, progress=progress.append).run(
        RunRequest(prompt="Explain the Hopf fibration", image=str(image), reasoning_effort="low")
    )
    assert manifest["status"] == "completed"
    assert manifest["model"] == "fake-gemini"
    assert manifest["scene_name"] == "FakeJourney"
    assert [c[0] for c in client.calls] == [s.name for s in STAGES] + ["composer"]
    assert {c[1] for c in client.calls} == {"low"}
    assert [c[2] for c in client.calls if c[2] is not None] == [image]  # only the intent stage sees the image
    assert [a["mode"] for a in manifest["attempts"]] == ["google-adk", "composer-repair"]
    run_dir = tmp_path / manifest["run_id"]
    assert (run_dir / "traces" / "repair.json").is_file()
    assert (run_dir / "traces" / "intent.raw.json").is_file()
    assert len(progress) == len(STAGES)
    assert bundle.validate_run(run_dir) == ([], "FakeJourney")


def test_live_run_rejects_non_json_stage(tmp_path: Path):
    from argon.models import StageCallResult

    class SilentClient(FakeClient):
        def complete(self, stage, **kwargs):
            return StageCallResult(text="no json here", payload=None)

    with pytest.raises(Exception, match="did not return JSON"):
        ArgonHarness(runs_dir=tmp_path, client=SilentClient()).run(RunRequest(prompt="Explain the Hopf fibration"))
    (run_dir,) = tmp_path.iterdir()
    assert bundle.load_manifest(tmp_path, run_dir.name).status == "failed"
