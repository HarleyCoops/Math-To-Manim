"""End-to-end offline chain: no model calls, real artifacts on disk."""

import json
import py_compile

from mythos.harness import STAGES, MythosHarness


def test_offline_chain_writes_all_artifacts(tmp_path):
    harness = MythosHarness(offline=True, runs_dir=tmp_path)
    manifest = harness.run("the pythagorean theorem")

    run_dir = tmp_path / manifest["run_id"]
    assert run_dir.is_dir()

    for _, _, artifact_name in STAGES:
        artifact_path = run_dir / artifact_name
        assert artifact_path.exists(), artifact_name
        payload = json.loads(artifact_path.read_text(encoding="utf-8"))
        assert payload["offline"] is True

    assert manifest["static_check"]["passed"] is True
    assert manifest["scene_name"] == "MythosOfflineScene"
    assert (run_dir / "manifest.json").exists()
    assert (run_dir / "mythos_scene.py").exists()


def test_offline_scene_compiles(tmp_path):
    harness = MythosHarness(offline=True, runs_dir=tmp_path)
    manifest = harness.run("compile check")
    py_compile.compile(manifest["scene_file"], doraise=True)


def test_stage_artifacts_chain_prior_keys(tmp_path):
    harness = MythosHarness(offline=True, runs_dir=tmp_path)
    manifest = harness.run("chaining")
    run_dir = tmp_path / manifest["run_id"]
    shot_list = json.loads(
        (run_dir / "05_shot_list.json").read_text(encoding="utf-8"))
    assert shot_list["shots"][0]["move"] == "HEADLINE"


def test_charters_ship_with_repo():
    for _, agent_file, _ in STAGES:
        text = MythosHarness.load_charter(agent_file)
        assert len(text) > 100, agent_file


def test_offwhite_prompt_rejects_default_dark_background(tmp_path):
    code_path = tmp_path / "scene.py"
    code_path.write_text(
        "from manim import *\n"
        "class BadPaperScene(ThreeDScene):\n"
        "    BG = \"#0c0c0b\"\n"
        "    def construct(self):\n"
        "        self.camera.background_color = self.BG\n",
        encoding="utf-8",
    )

    ok, failure = MythosHarness._verify(
        code_path,
        prompt="Use archival off-white paper, never black.",
    )

    assert ok is False
    assert "archival/off-white" in failure
