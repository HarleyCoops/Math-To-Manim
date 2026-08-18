"""WAR-1533: render wrappers pin cwd, media_dir, and reject path escape."""

from __future__ import annotations

from pathlib import Path

import pytest

from mythos.render import (
    RenderError,
    build_manim_command,
    render_scene_file,
    resolve_inside,
)
from sol.rendering import RenderError as SolRenderError
from sol.rendering import build_manim_command as sol_build_manim_command
from sol.rendering import resolve_inside as sol_resolve_inside


def test_mythos_command_pins_media_dir_and_relative_scene(tmp_path):
    scene = tmp_path / "mythos_scene.py"
    scene.write_text("from manim import *\nclass Demo(Scene):\n    pass\n", encoding="utf-8")
    command = build_manim_command(
        tmp_path,
        scene_file=scene,
        scene_name="Demo",
        quality="l",
    )
    assert "--media_dir" in command
    assert command[command.index("--media_dir") + 1] == str((tmp_path / "media").resolve())
    assert command[-2:] == ["mythos_scene.py", "Demo"]
    assert str(scene) not in command


def test_mythos_rejects_escaped_scene_path(tmp_path):
    outside = tmp_path.parent / "escape.py"
    with pytest.raises(RenderError, match="escapes"):
        resolve_inside(tmp_path, outside)


def test_mythos_rejects_non_identifier_scene_name(tmp_path):
    scene = tmp_path / "mythos_scene.py"
    scene.write_text("pass\n", encoding="utf-8")
    with pytest.raises(RenderError, match="invalid scene class name"):
        build_manim_command(
            tmp_path,
            scene_file=scene,
            scene_name="../Evil",
            quality="l",
        )


def test_sol_command_stays_inside_run_dir(tmp_path):
    (tmp_path / "sol_scene.py").write_text("pass\n", encoding="utf-8")
    command = sol_build_manim_command(tmp_path, scene_name="Demo", quality="l")
    assert command[command.index("--media_dir") + 1] == str((tmp_path / "media").resolve())
    assert command[-2:] == ["sol_scene.py", "Demo"]
    with pytest.raises(SolRenderError, match="escapes"):
        sol_resolve_inside(tmp_path, tmp_path.parent / "nope.mp4")


def test_render_scene_file_uses_run_dir_cwd(tmp_path, monkeypatch):
    scene = tmp_path / "mythos_scene.py"
    scene.write_text("from manim import *\nclass Demo(Scene):\n    pass\n", encoding="utf-8")
    observed: dict[str, object] = {}

    def fake_run(command, **kwargs):
        observed["command"] = command
        observed["cwd"] = kwargs["cwd"]
        observed["shell"] = kwargs.get("shell", False)
        return type("Completed", (), {"returncode": 0, "stdout": "", "stderr": ""})()

    monkeypatch.setattr("mythos.render.subprocess.run", fake_run)
    code, output = render_scene_file(
        tmp_path,
        scene_file=scene,
        scene_name="Demo",
        quality="l",
        timeout=5,
    )
    assert code == 0
    assert output == ""
    assert observed["cwd"] == str(tmp_path.resolve())
    assert observed["shell"] is False
    assert "--media_dir" in observed["command"]
    leaked = [
        path
        for path in Path(tmp_path).parent.glob("media/**/*")
        if tmp_path.resolve() not in path.resolve().parents
    ]
    assert leaked == []
