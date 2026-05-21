from __future__ import annotations

import hashlib
import json
from pathlib import Path

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
    assert package.render_result.status == "skipped"
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


def test_pipeline_copies_reference_images_into_run_bundle(tmp_path) -> None:
    image_path = tmp_path / "reference plot.png"
    image_bytes = b"not a real png, but stable test bytes"
    image_path.write_bytes(image_bytes)
    pipeline = AnimationPipeline(
        RuntimeConfig(
            runs_dir=tmp_path / "runs",
            deterministic=True,
            trace_enabled=False,
        )
    )

    package = pipeline.generate(
        prompt="Explain unit distance lattices",
        render=False,
        reference_images=[image_path],
    )

    run_dir = next((tmp_path / "runs").iterdir())
    reference_assets = json.loads((run_dir / "reference_assets.json").read_text(encoding="utf-8"))
    request = json.loads((run_dir / "request.json").read_text(encoding="utf-8"))
    scene_spec = json.loads((run_dir / "scene_spec.json").read_text(encoding="utf-8"))
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))

    asset = reference_assets["assets"][0]
    copied_path = asset["bundle_path"]
    digest = hashlib.sha256(image_bytes).hexdigest()
    assert asset["source_path"] == str(image_path.resolve())
    assert asset["sha256"] == digest
    assert asset["size_bytes"] == len(image_bytes)
    assert asset["media_type"] == "image/png"
    assert copied_path.endswith(f"{digest[:12]}.png")
    assert (run_dir / "reference_assets").exists()
    assert image_bytes == (run_dir / "reference_assets" / Path(copied_path).name).read_bytes()
    assert request["metadata"]["reference_assets"]["assets"][0]["sha256"] == digest
    assert scene_spec["metadata"]["reference_assets"]["assets"][0]["sha256"] == digest
    assert package.reference_assets is not None
    assert package.reference_assets.assets[0].sha256 == digest
    assert "reference_assets" in manifest["artifacts"]
