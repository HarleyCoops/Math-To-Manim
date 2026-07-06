from __future__ import annotations

import json
import subprocess
import sys

import pytest

from math_to_manim.rendering import extract_frame, make_contact_sheet, probe_video, render_manim_scene
from math_to_manim.review import (
    EvalCriterion,
    build_eval_prompt,
    parse_eval_score,
    score_video_metadata,
    weighted_score,
)
from math_to_manim.tools import (
    ArtifactStore,
    GraphCycleError,
    discover_scene_classes,
    find_primary_scene_class,
    normalize_graph,
    topological_sort,
    validate_python_source,
)


def test_normalize_graph_closes_dependencies_and_toposorts_deterministically() -> None:
    graph = {
        "render": ["scene", "assets", "scene"],
        "scene": ["plan"],
    }

    assert normalize_graph(graph) == {
        "assets": (),
        "plan": (),
        "render": ("assets", "scene"),
        "scene": ("plan",),
    }
    assert topological_sort(graph) == ["assets", "plan", "scene", "render"]


def test_topological_sort_reports_cycles() -> None:
    with pytest.raises(GraphCycleError) as exc_info:
        topological_sort({"a": ["b"], "b": ["a"]})

    assert exc_info.value.nodes == ("a", "b")


def test_artifact_store_writes_deterministic_manifest(tmp_path) -> None:
    store = ArtifactStore(tmp_path)

    artifact = store.put_text("hello", "../unsafe name.txt", kind="note", metadata={"n": 1})
    same = ArtifactStore(tmp_path).get(artifact.id)

    assert same is not None
    assert artifact.id == same.id
    assert artifact.path.read_text(encoding="utf-8") == "hello"
    assert artifact.path.name.endswith("unsafe_name.txt")
    assert json.loads((tmp_path / "manifest.json").read_text(encoding="utf-8"))[artifact.id]["kind"] == "note"


def test_validate_python_source_accepts_scene_code_and_rejects_dangerous_code() -> None:
    valid = validate_python_source("from manim import Scene\nclass Demo(Scene):\n    def construct(self):\n        pass\n")
    invalid = validate_python_source("import os\nos.system('echo no')\n")
    syntax = validate_python_source("class Broken(:\n    pass\n")

    assert valid.ok
    assert not invalid.ok
    assert {issue.code for issue in invalid.errors} == {"forbidden-import", "forbidden-call"}
    assert not syntax.ok
    assert syntax.errors[0].code == "syntax-error"


def test_scene_discovery_uses_ast_without_importing_manim() -> None:
    source = """
class Helper:
    pass

class Opening(Scene):
    def construct(self):
        pass

class CameraMove(manim.ThreeDScene):
    pass
"""

    scenes = discover_scene_classes(source)

    assert [scene.name for scene in scenes] == ["Opening", "CameraMove"]
    assert scenes[0].has_construct is True
    assert scenes[1].bases == ("manim.ThreeDScene",)
    assert find_primary_scene_class(source).name == "Opening"


def test_optional_rendering_wrappers_skip_missing_binaries(tmp_path) -> None:
    scene_file = tmp_path / "scene.py"
    scene_file.write_text("from manim import Scene\n", encoding="utf-8")

    manim = render_manim_scene(scene_file, manim_bin="definitely-missing-manim-binary")
    probe = probe_video(tmp_path / "missing.mp4", ffprobe_bin="definitely-missing-ffprobe-binary")
    frame = extract_frame(
        tmp_path / "missing.mp4",
        tmp_path / "frame.png",
        ffmpeg_bin="definitely-missing-ffmpeg-binary",
    )
    sheet = make_contact_sheet(
        tmp_path / "missing.mp4",
        tmp_path / "contact_sheet.png",
        ffmpeg_bin="definitely-missing-ffmpeg-binary",
    )

    assert manim.skipped and not manim.ok
    assert probe.skipped and not probe.ok
    assert frame.skipped and not frame.ok
    assert sheet.skipped and not sheet.ok


def test_render_manim_scene_falls_back_to_python_module(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    scene_file = tmp_path / "scene.py"
    scene_file.write_text("from manim import Scene\nclass DemoScene(Scene):\n    def construct(self):\n        pass\n", encoding="utf-8")
    media_dir = tmp_path / "media"
    calls: list[list[str]] = []

    def fake_resolve_binary(binary: str) -> str | None:
        if binary == "manim":
            return None
        if binary == sys.executable:
            return sys.executable
        return None

    def fake_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append(command)
        video_dir = media_dir / "videos" / "scene" / "1080p30"
        video_dir.mkdir(parents=True)
        (video_dir / "DemoScene.mp4").write_bytes(b"video")
        return subprocess.CompletedProcess(command, 0, stdout="ok", stderr="")

    monkeypatch.setattr("math_to_manim.rendering.manim.resolve_binary", fake_resolve_binary)
    monkeypatch.setattr("math_to_manim.rendering.manim.subprocess.run", fake_run)

    result = render_manim_scene(scene_file, scene_name="DemoScene", output_dir=media_dir)

    assert result.ok
    assert result.command[:3] == (sys.executable, "-m", "manim")
    assert calls[0][:3] == [sys.executable, "-m", "manim"]


def test_video_scoring_is_weighted_and_deterministic() -> None:
    good = score_video_metadata(duration_seconds=2.0, width=1280, height=720, file_size_bytes=10)
    weak = score_video_metadata(duration_seconds=0.25, width=320, height=180, file_size_bytes=0)

    assert good.score == pytest.approx(1.0)
    assert good.passed
    assert weak.score < good.score
    assert not weak.passed


def test_eval_prompt_helpers_parse_json_and_weight_scores() -> None:
    prompt = build_eval_prompt(
        criteria=[EvalCriterion("Accuracy", "Matches the requested math.", 2.0), "Visual clarity"],
        reference="Show x^2.",
        candidate="A parabola animation.",
    )
    parsed = parse_eval_score('{"score": 4, "max_score": 5, "explanation": "clear"}')

    assert "Accuracy (weight 2)" in prompt
    assert "Candidate:\n\nA parabola animation." in prompt
    assert parsed.ok
    assert parsed.normalized_score == pytest.approx(0.8)
    assert weighted_score([parsed, 1.0], weights=[1.0, 3.0]) == pytest.approx(0.95)
