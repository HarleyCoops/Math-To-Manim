"""Offline tests for the MiMo 2.6 tool-calling silo. No model calls.

The live path is exercised through the ``StageClient`` seam with a fake client
that writes artifacts through the real tool dispatcher.
"""

from __future__ import annotations

import json
import threading
from pathlib import Path

import pytest

from mimo.agents import AGENT_STAGES, SCENE_STAGE, STAGE_ARTIFACTS, STAGE_NAMES, build_stage_prompt, stage_by_name, stages_from
from mimo.cli import build_parser, main
from mimo.client import extract_json_object
from mimo.harness import MimoHarness, find_video
from mimo.models import SCENE_FILE, PipelineResult, RunRequest, StageRecord, StageRunResult
from mimo.offline import OFFLINE_SCENE_NAME, write_offline_bundle
from mimo.staged import ToolCallingPipeline
from mimo.tools import TOOLS, ToolContext, dispatch_tool
from mimo.validation import validate_run, validation_from_scene

GOOD_SCENE = (
    "from manim import *\n"
    "class Good(ThreeDScene):\n"
    "    def construct(self):\n"
    "        self.set_camera_orientation(phi=1, theta=2)\n"
    "        self.move_camera(phi=1.2)\n"
)
BAD_SCENE = (
    "from manim import *\n"
    "class Bad(Scene):\n"
    "    def construct(self):\n"
    "        self.play(self.camera.animate.set_euler_angles(1, 2, 3))\n"
)


class FakeClient:
    """Stands in for MimoClient: writes each stage's artifacts through the real tools."""

    model = "fake-mimo"

    def __init__(self, scenes: list[str] | None = None):
        self.calls: list[tuple[str, str]] = []
        self.scenes = list(scenes or [GOOD_SCENE])

    def run_stage(self, *, stage_name, prompt, tools, ctx, reasoning_effort) -> StageRunResult:
        self.calls.append((stage_name, reasoning_effort))
        allowed = {tool["function"]["name"] for tool in tools}
        stage = stage_by_name(stage_name)
        for artifact in stage.artifacts:
            if artifact == SCENE_FILE:
                content = self.scenes.pop(0) if len(self.scenes) > 1 else self.scenes[0]
            else:
                content = json.dumps({"stage": stage_name, "artifact": artifact})
            assert dispatch_tool(ctx, "write_artifact", {"path": artifact, "content": content})["ok"]
        if "record_decision" in allowed:
            dispatch_tool(ctx, "record_decision", {"decision": stage_name, "rationale": "test"})
        return StageRunResult(
            status="completed",
            role=stage_name,
            artifacts=list(stage.artifacts),
            summary=f"{stage_name} done",
            checks=[],
            notes=[],
            tool_calls=[],
        )


# -- stage table -------------------------------------------------------------


def test_agent_stages_cover_chain():
    assert list(STAGE_NAMES) == [
        "intent",
        "cartographer",
        "curriculum",
        "math-director",
        "cinematographer",
        "scene-composer",
    ]
    assert SCENE_STAGE.name == "scene-composer"
    assert STAGE_ARTIFACTS[-1] == SCENE_FILE


def test_stage_tools_exist_and_scene_composer_can_verify():
    for stage in AGENT_STAGES:
        assert set(stage.tools) <= set(TOOLS)
        assert "write_artifact" in stage.tools
    names = {tool["function"]["name"] for tool in stage_by_name("scene-composer").tool_specs}
    assert {"verify_scene", "verify_geometry", "write_artifact"} <= names


def test_charters_load_from_agent_files():
    for stage in AGENT_STAGES:
        assert stage.charter_path.is_file()
        assert "write_artifact" in stage.charter
        assert not stage.charter.startswith("---")


def test_stages_from_follows_dependencies():
    assert stages_from("scene-composer") == {"scene-composer"}
    assert stages_from("cartographer") == {"cartographer", "curriculum", "cinematographer", "scene-composer"}
    assert stages_from("intent") == set(STAGE_NAMES)
    with pytest.raises(ValueError):
        stages_from("director")


def test_cartographer_prompt_requires_reverse_thinking():
    stage = stage_by_name("cartographer")
    prompt = build_stage_prompt(
        stage,
        RunRequest(prompt="explain spinors via a belt"),
        run_dir=Path("runs/mimo/test"),
    )
    assert "reverse" in prompt.lower()
    assert "02_knowledge_map.json" in prompt
    assert "01_intent.json" in prompt


def test_cli_choices_come_from_the_table():
    parser = build_parser()
    resume = next(action for action in parser._subparsers._actions if action.dest == "command").choices["resume"]
    from_action = next(action for action in resume._actions if action.dest == "from_stage")
    assert tuple(from_action.choices) == STAGE_NAMES


# -- tools --------------------------------------------------------------------


def test_write_artifact_sandbox(tmp_path: Path):
    ctx = ToolContext(run_dir=tmp_path)
    result = dispatch_tool(
        ctx,
        "write_artifact",
        {"path": "01_intent.json", "content": json.dumps({"core_claim": "x"})},
    )
    assert result["ok"] is True
    assert (tmp_path / "01_intent.json").is_file()
    escaped = dispatch_tool(ctx, "write_artifact", {"path": "../escape.json", "content": "{}"})
    assert escaped["ok"] is False
    assert dispatch_tool(ctx, "nope", {})["ok"] is False
    assert dispatch_tool(ctx, "write_artifact", {"path": "x"})["ok"] is False


def test_verify_geometry_twist_parity(tmp_path: Path):
    ctx = ToolContext(run_dir=tmp_path)
    odd = dispatch_tool(ctx, "verify_geometry", {"kind": "ribbon", "twists": 1})
    even = dispatch_tool(ctx, "verify_geometry", {"kind": "ribbon", "twists": 2})
    assert odd["ok"] is True
    assert odd["twist_charge_parity"] == "odd"
    assert odd["untwistable_with_clamped_ends"] is False
    assert even["twist_charge_parity"] == "even"
    assert even["untwistable_with_clamped_ends"] is True
    assert dispatch_tool(ctx, "verify_geometry", {"kind": "ribbon", "twists": 1.5})["ok"] is False


def test_verify_scene_tool_is_the_app_gate(tmp_path: Path):
    ctx = ToolContext(run_dir=tmp_path)
    bad = dispatch_tool(ctx, "verify_scene", {"source": BAD_SCENE})
    assert bad["ok"] is False
    assert bad["errors"] == validation_from_scene(BAD_SCENE)["errors"]
    good = dispatch_tool(ctx, "verify_scene", {"source": GOOD_SCENE})
    assert good["ok"] is True
    assert good["scene_name"] == "Good"
    assert validation_from_scene(GOOD_SCENE)["status"] == "passed"


def test_record_decision_is_safe_across_threads(tmp_path: Path):
    lock = threading.Lock()
    contexts = [ToolContext(run_dir=tmp_path, decisions_lock=lock) for _ in range(4)]

    def record(ctx: ToolContext, lane: int) -> None:
        for i in range(25):
            dispatch_tool(ctx, "record_decision", {"decision": f"{lane}-{i}", "rationale": "r"})

    threads = [threading.Thread(target=record, args=(ctx, lane)) for lane, ctx in enumerate(contexts)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    history = json.loads((tmp_path / "decisions.json").read_text(encoding="utf-8"))
    assert len(history) == 100
    assert len({entry["decision"] for entry in history}) == 100


# -- client helpers -------------------------------------------------------------


def test_extract_json_object_handles_nesting_fences_and_prose():
    nested = {"summary": "ok", "artifacts": ["a"], "checks": {"inner": {"deep": [1, {"x": 2}]}}}
    fenced = "Here you go:\n```json\n" + json.dumps(nested, indent=2) + "\n```\nDone {not json}."
    assert extract_json_object(fenced) == nested
    bare = "Result: " + json.dumps(nested) + " and a stray } brace { later"
    assert extract_json_object(bare) == nested
    assert extract_json_object("```\n{\"a\": {\"b\": 1}}\n```") == {"a": {"b": 1}}
    with pytest.raises(ValueError):
        extract_json_object("no object here")
    with pytest.raises(ValueError):
        extract_json_object("   ")


# -- validation -----------------------------------------------------------------


def test_offline_bundle_matches_stage_table_and_validates(tmp_path: Path):
    request = RunRequest(prompt="rehearse the MiMo tool pipeline", offline=True)
    result = write_offline_bundle(tmp_path, request)
    assert isinstance(result, PipelineResult)
    assert tuple(result.artifacts) == STAGE_ARTIFACTS
    validation = validate_run(tmp_path, STAGE_ARTIFACTS)
    assert validation.ok
    assert validation.scene_name == OFFLINE_SCENE_NAME
    assert validation.report["status"] == "passed"
    assert not (tmp_path / "validation.json").exists()  # validate_run is read-only


def test_validate_run_reports_missing_and_malformed(tmp_path: Path):
    (tmp_path / "01_intent.json").write_text("[]", encoding="utf-8")
    (tmp_path / SCENE_FILE).write_text(BAD_SCENE, encoding="utf-8")
    validation = validate_run(tmp_path, STAGE_ARTIFACTS)
    assert not validation.ok
    assert "01_intent.json: expected a non-empty JSON object" in validation.failures
    assert "missing required artifact: 02_knowledge_map.json" in validation.failures
    assert any(f.startswith(f"{SCENE_FILE}: forbidden camera animation") for f in validation.failures)


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


# -- pipeline and harness (live path through the StageClient seam) ----------------


def test_live_run_completes_through_harness(tmp_path: Path):
    client = FakeClient()
    harness = MimoHarness(runs_dir=tmp_path, client=client)
    response = harness.run(RunRequest(prompt="show the belt trick", reasoning_effort="max"))

    assert response["status"] == "completed"
    assert response["scene_name"] == "Good"
    assert response["video_path"] is None
    run_dir = Path(response["run_dir"])
    assert [name for name, _ in client.calls][0] == "intent"
    assert {name for name, _ in client.calls} == set(STAGE_NAMES)
    assert {effort for _, effort in client.calls} == {"max"}

    manifest = harness.get_run(run_dir.name)
    assert manifest.status == "completed"
    assert manifest.scene_name == "Good"
    assert manifest.model == "fake-mimo"
    assert len(manifest.stage_records) == len(STAGE_NAMES)
    for record_path in manifest.stage_records:
        record = StageRecord.model_validate_json((run_dir / record_path).read_text(encoding="utf-8"))
        assert record.status == "completed"
        assert (run_dir / record.result_path).is_file()
        assert (run_dir / record.trace_path).is_file()
    assert json.loads((run_dir / "validation.json").read_text(encoding="utf-8"))["status"] == "passed"
    assert json.loads((run_dir / "review.json").read_text(encoding="utf-8")) == {"status": "skipped"}
    assert json.loads((run_dir / "request.json").read_text(encoding="utf-8"))["reasoning_effort"] == "max"
    decisions = json.loads((run_dir / "decisions.json").read_text(encoding="utf-8"))
    assert {entry["decision"] for entry in decisions} == {"cartographer", "math-director"}


def test_pipeline_skips_cached_stages(tmp_path: Path):
    client = FakeClient()
    pipeline = ToolCallingPipeline(client=client)
    request = RunRequest(prompt="cache me")
    first = pipeline.run(tmp_path, request)
    assert first.checks == [f"{name}:completed" for name in STAGE_NAMES]
    assert len(client.calls) == len(STAGE_NAMES)

    second = pipeline.run(tmp_path, request)
    assert len(client.calls) == len(STAGE_NAMES), "unchanged stages must not call the model"
    assert second.checks == [f"{name}:cached" for name in STAGE_NAMES]

    pipeline.run(tmp_path, request, from_stage="cinematographer")
    assert [name for name, _ in client.calls[len(STAGE_NAMES):]] == ["cinematographer", "scene-composer"]

    (tmp_path / "01_intent.json").write_text(json.dumps({"edited": True}), encoding="utf-8")
    before = len(client.calls)
    third = pipeline.run(tmp_path, request)
    assert third.checks[0] == "intent:completed", "a changed artifact invalidates its stage"
    assert third.checks[1:] == [f"{name}:cached" for name in STAGE_NAMES[1:]], "re-run produced identical inputs"


def test_changed_upstream_output_invalidates_dependants(tmp_path: Path):
    class Counting(FakeClient):
        """Intent writes different content every time it runs; other stages are deterministic."""

        def run_stage(self, *, stage_name, ctx, **kwargs):
            result = super().run_stage(stage_name=stage_name, ctx=ctx, **kwargs)
            if stage_name == "intent":
                n = sum(1 for name, _ in self.calls if name == "intent")
                dispatch_tool(ctx, "write_artifact", {"path": "01_intent.json", "content": json.dumps({"v": n})})
            return result

    client = Counting()
    pipeline = ToolCallingPipeline(client=client)
    request = RunRequest(prompt="upstream changes")
    pipeline.run(tmp_path, request)
    (tmp_path / "01_intent.json").write_text(json.dumps({"edited": True}), encoding="utf-8")
    result = pipeline.run(tmp_path, request)
    assert result.checks == [
        "intent:completed",  # its artifact changed under it
        "cartographer:completed",  # reads the new 01_intent.json
        "curriculum:cached",  # cartographer rewrote identical content
        "math-director:completed",  # reads the new 01_intent.json
        "cinematographer:cached",
        "scene-composer:cached",
    ]


def test_failed_stage_is_recorded_and_dependants_do_not_run(tmp_path: Path):
    class Failing(FakeClient):
        def run_stage(self, *, stage_name, **kwargs):
            if stage_name == "curriculum":
                raise RuntimeError("boom")
            return super().run_stage(stage_name=stage_name, **kwargs)

    client = Failing()
    with pytest.raises(RuntimeError, match="boom"):
        ToolCallingPipeline(client=client).run(tmp_path, RunRequest(prompt="fail in the middle"))
    record = StageRecord.model_validate_json((tmp_path / "stages/03-curriculum.json").read_text(encoding="utf-8"))
    assert record.status == "failed" and record.error == "boom"
    assert "math-director" in {name for name, _ in client.calls}  # the independent lane still ran
    assert not (tmp_path / "stages/05-cinematographer.json").exists()
    assert not (tmp_path / "stages/06-scene-composer.json").exists()


def test_repair_reruns_only_the_scene_stage(tmp_path: Path):
    client = FakeClient(scenes=[BAD_SCENE, GOOD_SCENE])
    harness = MimoHarness(runs_dir=tmp_path, client=client)
    response = harness.run(RunRequest(prompt="needs one repair", max_repairs=2))
    assert response["status"] == "completed"
    names = [name for name, _ in client.calls]
    assert names.count("scene-composer") == 2
    assert names.count("intent") == 1
    manifest = harness.get_run(response["run_id"])
    assert [attempt["mode"] for attempt in manifest.attempts] == ["mimo-tool-calling", "scene-composer-static-repair"]
    assert manifest.attempts[1]["input_failures"]


def test_repair_budget_exhausted_fails_the_manifest(tmp_path: Path):
    client = FakeClient(scenes=[BAD_SCENE])
    harness = MimoHarness(runs_dir=tmp_path, client=client)
    with pytest.raises(RuntimeError, match="validation failed"):
        harness.run(RunRequest(prompt="never repairs", max_repairs=1))
    manifest = harness.list_runs()[0]
    assert manifest.status == "failed"
    assert "forbidden camera animation" in (manifest.error or "")
    assert json.loads((tmp_path / manifest.run_id / "validation.json").read_text(encoding="utf-8"))["status"] == "failed"


def test_resume_keeps_cached_stages_and_finishes_manifest(tmp_path: Path):
    class FailsOnce(FakeClient):
        def __init__(self):
            super().__init__()
            self.failed = False

        def run_stage(self, *, stage_name, **kwargs):
            if stage_name == "cinematographer" and not self.failed:
                self.failed = True
                raise RuntimeError("transient")
            return super().run_stage(stage_name=stage_name, **kwargs)

    client = FailsOnce()
    harness = MimoHarness(runs_dir=tmp_path, client=client)
    with pytest.raises(RuntimeError, match="transient"):
        harness.run(RunRequest(prompt="resume me", reasoning_effort="low"))
    failed = harness.list_runs()[0]
    assert failed.status == "failed"
    calls_before = len(client.calls)

    response = harness.resume(failed.run_id)
    assert response["status"] == "completed"
    resumed = [name for name, effort in client.calls[calls_before:]]
    assert resumed == ["cinematographer", "scene-composer"]
    assert {effort for _, effort in client.calls} == {"low"}, "resume reuses the stored request"
    manifest = harness.get_run(failed.run_id)
    assert manifest.status == "completed" and manifest.error is None
    assert manifest.scene_name == "Good"

    harness.resume(failed.run_id, from_stage="math-director")
    assert [name for name, _ in client.calls[calls_before + 2:]] == ["math-director", "cinematographer", "scene-composer"]


def test_run_dir_rejects_traversal(tmp_path: Path):
    harness = MimoHarness(runs_dir=tmp_path, client=FakeClient())
    for bad in ("../x", "a/b", "..", ""):
        with pytest.raises(ValueError):
            harness.run_dir(bad)
    with pytest.raises(FileNotFoundError):
        harness.run_dir("missing")


def test_find_video_ignores_partial_movie_files(tmp_path: Path):
    partial = tmp_path / "videos/mimo_scene/480p15/partial_movie_files/Good/x.mp4"
    partial.parent.mkdir(parents=True)
    partial.write_bytes(b"")
    assert find_video(tmp_path) is None
    final = tmp_path / "videos/mimo_scene/480p15/Good.mp4"
    final.write_bytes(b"")
    assert find_video(tmp_path) == final
    assert find_video(tmp_path / "nope") is None


def test_cli_offline_run_uses_cwd_runs_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys):
    monkeypatch.chdir(tmp_path)
    assert main(["run", "offline rehearsal via the CLI", "--offline"]) == 0
    response = json.loads(capsys.readouterr().out)
    assert response["status"] == "completed"
    assert response["scene_name"] == OFFLINE_SCENE_NAME
    assert Path(response["run_dir"]).parent == tmp_path / "runs" / "mimo"
    assert main(["status", response["run_id"]]) == 0
    assert json.loads(capsys.readouterr().out)["offline"] is True
    assert main(["runs"]) == 0
    assert response["run_id"] in capsys.readouterr().out
