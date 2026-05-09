from __future__ import annotations

import json

from math_to_manim.config import RuntimeConfig
from math_to_manim.pipeline.runner import AnimationPipeline


def test_pipeline_generates_no_render_vertical_slice(tmp_path) -> None:
    pipeline = AnimationPipeline(
        RuntimeConfig(
            runs_dir=tmp_path,
            deterministic=True,
            trace_enabled=True,
        )
    )

    package = pipeline.generate(
        prompt="Explain why derivatives are slopes",
        audience_level="high_school",
        desired_duration=45,
        style="cinematic",
        render=False,
    )

    run_dir = next(tmp_path.iterdir())
    assert package.validation_report is not None
    assert package.validation_report.status == "passed"
    assert package.render_result is not None
    assert package.render_result.metadata["skipped"] is True
    assert (run_dir / "request.json").exists()
    assert (run_dir / "knowledge_graph.json").exists()
    assert (run_dir / "generated_scene.py").exists()
    assert (run_dir / "manifest.json").exists()

    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["render_requested"] is False
    assert "knowledge_graph" in manifest["artifacts"]


def test_pipeline_preserves_long_prompt_for_codegen_with_safe_scene_name(tmp_path) -> None:
    long_prompt = " ".join(["Explain GRPO semantic manifolds with LaTeX zooms"] * 20)
    pipeline = AnimationPipeline(
        RuntimeConfig(
            runs_dir=tmp_path,
            deterministic=True,
            trace_enabled=False,
        )
    )

    pipeline.generate(
        prompt=long_prompt,
        audience_level="advanced",
        desired_duration=240,
        style="cinematic 3D",
        render=False,
    )

    run_dir = next(tmp_path.iterdir())
    scene_spec = json.loads((run_dir / "scene_spec.json").read_text(encoding="utf-8"))
    assert scene_spec["scene_name"].endswith("Scene")
    assert len(scene_spec["scene_name"]) <= 80
    assert scene_spec["metadata"]["original_prompt"] == long_prompt
    assert scene_spec["metadata"]["requested_duration_seconds"] == 240
    assert scene_spec["metadata"]["render_command"].endswith(f"generated_scene.py {scene_spec['scene_name']}")
    assert long_prompt not in scene_spec["metadata"]["render_command"]
