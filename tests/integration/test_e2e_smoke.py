"""WAR-1535: init workspace, drop a canned scene, render at quality l."""

from __future__ import annotations

import importlib.util
import json
import shutil
import time
from pathlib import Path

import pytest

from mythos.harness import MythosHarness
from mythos.render import find_final_video

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "smoke_scene.py"


def _render_ready() -> bool:
    return (
        importlib.util.find_spec("manim") is not None
        and shutil.which("ffmpeg") is not None
    )


pytestmark = pytest.mark.skipif(
    not _render_ready(),
    reason="manim and ffmpeg must be on PATH for the init-to-render smoke test",
)


def test_init_overwrite_scene_and_render_stays_in_run_dir(tmp_path):
    harness = MythosHarness(offline=True, runs_dir=tmp_path)
    manifest = harness.run("smoke square")
    run_dir = tmp_path / manifest["run_id"]
    scene_path = run_dir / "mythos_scene.py"
    scene_path.write_text(FIXTURE.read_text(encoding="utf-8"), encoding="utf-8")

    started = time.monotonic()
    result = harness.render_workspace(run_dir, "SmokeScene", quality="l")
    elapsed = time.monotonic() - started
    assert result["exit_code"] == 0, result["output"][-4000:]
    assert elapsed < 60

    video = find_final_video(run_dir)
    assert video is not None
    assert run_dir.resolve() in video.resolve().parents
    assert video.stat().st_size > 0

    outside = [
        path
        for path in tmp_path.glob("**/*.mp4")
        if run_dir.resolve() not in path.resolve().parents
        and path.resolve() != run_dir.resolve()
    ]
    assert outside == []

    written = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    assert written["status"]["render"] == "complete"
