from __future__ import annotations

import importlib.util
import shutil
import sys
from pathlib import Path

import pytest

from m2m2_visual_improvement.micro_scenes import BASE_SCENES
from m2m2_visual_improvement.renderer import (
    RenderRequest,
    RenderSettings,
    Renderer,
    SubprocessRunner,
)


RUNTIME_AVAILABLE = (
    importlib.util.find_spec("manim") is not None
    and shutil.which("ffmpeg") is not None
)


@pytest.mark.render
@pytest.mark.skipif(
    not RUNTIME_AVAILABLE,
    reason="Manim and FFmpeg are required for render integration",
)
def test_known_micro_scene_renders_to_video(tmp_path: Path) -> None:
    scene = BASE_SCENES[sorted(BASE_SCENES)[0]]
    renderer = Renderer(
        runner=SubprocessRunner(),
        settings=RenderSettings(
            manim_command=(sys.executable, "-m", "manim"),
            timeout_seconds=180,
        ),
    )

    outcome = renderer.render(
        RenderRequest(
            task_id=scene.base_scene_id,
            source_code=scene.code,
            scene_name=scene.scene_name,
            role="baseline",
            output_dir=tmp_path / "render",
        )
    )

    assert outcome.video_path.stat().st_size > 0
