"""WAR-1533: Sol render wrapper pins media_dir and rejects path escape."""

from __future__ import annotations

import pytest

from sol.rendering import RenderError as SolRenderError
from sol.rendering import build_manim_command as sol_build_manim_command
from sol.rendering import resolve_inside as sol_resolve_inside


def test_sol_command_stays_inside_run_dir(tmp_path):
    (tmp_path / "sol_scene.py").write_text("pass\n", encoding="utf-8")
    command = sol_build_manim_command(tmp_path, scene_name="Demo", quality="l")
    assert command[command.index("--media_dir") + 1] == str((tmp_path / "media").resolve())
    assert command[-2:] == ["sol_scene.py", "Demo"]
    with pytest.raises(SolRenderError, match="escapes"):
        sol_resolve_inside(tmp_path, tmp_path.parent / "nope.mp4")
