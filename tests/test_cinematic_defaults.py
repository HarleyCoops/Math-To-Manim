"""WAR-1534: cinematic-3D defaults match the live Mythos charter, not Hermes."""

from __future__ import annotations

import ast
import re
from pathlib import Path

from mythos.harness import MythosHarness
from mythos.scene_checks import validate_manim_code_report

REPO = Path(__file__).resolve().parents[1]
CINEMATOGRAPHY = REPO / "mythos" / "cinematography.py"
GOLDEN = REPO / "tests" / "fixtures" / "cinematic_geodesic.scene.py"
CHARTER_BG = "#0c0c0b"
RETIRED_HERMES_BG = "#050510"


def _constants(tree: ast.AST) -> dict[str, str]:
    found: dict[str, str] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        if not isinstance(node.value, ast.Constant) or not isinstance(node.value.value, str):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and node.value.value.startswith("#"):
                found[target.id] = node.value.value
    return found


def test_cinematography_library_pins_current_charter_defaults():
    source = CINEMATOGRAPHY.read_text(encoding="utf-8")
    tree = ast.parse(source)
    colors = _constants(tree)
    assert colors["INK"] == CHARTER_BG
    assert colors["INK"] != RETIRED_HERMES_BG
    named = {name for name, value in colors.items() if re.fullmatch(r"#[0-9a-fA-F]{6}", value)}
    assert {"INK", "IVORY", "CORAL", "SKY", "OLIVE"} <= named
    assert "def stage(" in source
    assert "set_camera_orientation" in source
    assert "add_fixed_in_frame_mobjects" in source
    assert "move_camera" in source
    assert "self.camera.animate" not in source


def test_golden_geodesic_scene_honors_mythos_cinematic_contract():
    source = GOLDEN.read_text(encoding="utf-8")
    tree = ast.parse(source)
    report = validate_manim_code_report(source)
    assert report.valid, report.errors
    assert report.scene_names == ["GeodesicFilm"]
    assert report.suggestions == []

    class_def = next(
        node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "GeodesicFilm"
    )
    bases = [base.id for base in class_def.bases if isinstance(base, ast.Name)]
    assert bases == ["ThreeDScene"]
    assert CHARTER_BG in source
    assert RETIRED_HERMES_BG not in source
    assert "set_camera_orientation" in source
    assert "phi=0" in source
    assert "theta=-90" in source
    assert "add_fixed_in_frame_mobjects" in source
    assert "move_camera" in source
    assert "self.camera.animate" not in source
    named_colors = _constants(tree)
    assert len(named_colors) >= 3


def test_offline_codegen_scene_keeps_threedscene_and_raw_mathtex(tmp_path):
    manifest = MythosHarness(offline=True, runs_dir=tmp_path).run(
        "Animate the geodesic equation in cinematic 3D"
    )
    source = Path(manifest["scene_file"]).read_text(encoding="utf-8")
    report = validate_manim_code_report(source)
    assert report.valid, report.errors
    assert "ThreeDScene" in source
    assert report.suggestions == []
    assert CHARTER_BG in source
    assert "set_camera_orientation" in source
    assert "move_camera" in source
    assert "self.camera.animate" not in source
