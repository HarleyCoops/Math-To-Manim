"""SceneSpec: checks, convention conversions, shot compilation and the render commands."""

import json
import math
from pathlib import Path

import pytest

from studio import render
from studio.spec import convert, load_spec
from studio.spec.compile import compile_shot
from studio.spec.models import SceneSpec

EXAMPLE = Path(render.__file__).resolve().parent / "examples" / "lattice.json"


def example_dict() -> dict:
    return json.loads(EXAMPLE.read_text(encoding="utf-8"))


def test_example_spec_loads_and_resolves():
    spec = load_spec(EXAMPLE)
    shot = spec.shot("lattice")
    assert spec.camera(shot.camera).fov_y_deg == 32.0
    assert spec.object("crystal").counts == (3, 3, 2)
    with pytest.raises(KeyError, match="no shot"):
        spec.shot("missing")


def test_spec_rejects_broken_references_and_bad_colours():
    data = example_dict()
    data["shots"][0]["camera"] = "nowhere"
    data["objects"][0]["colors"] = ["coral", "teal"]
    with pytest.raises(ValueError) as error:
        SceneSpec.model_validate(data)
    assert "unknown camera 'nowhere'" in str(error.value)
    assert "unknown palette colour 'teal'" in str(error.value)

    data = example_dict()
    data["palette"]["coral"] = "orange"
    with pytest.raises(ValueError, match="#rrggbb"):
        SceneSpec.model_validate(data)

    data = example_dict()
    data["surprise"] = True
    with pytest.raises(ValueError):
        SceneSpec.model_validate(data)


def test_colour_and_axis_conversions():
    assert convert.srgb_hex_to_linear("#000000") == (0.0, 0.0, 0.0)
    assert convert.srgb_hex_to_linear("#ffffff") == pytest.approx((1.0, 1.0, 1.0))
    assert convert.srgb_hex_to_linear("#808080")[0] == pytest.approx(0.2158, abs=1e-3)
    # Z up to Y up, both right-handed: +Z becomes +Y and +Y becomes -Z.
    assert convert.to_three((1.0, 2.0, 3.0)) == (1.0, 3.0, -2.0)


CAMERA = dict(position=(0.0, -10.0, 0.0), target=(0.0, 0.0, 0.0), up=(0.0, 0.0, 1.0),
              fov_y_deg=40.0, width=1920, height=1080)


def test_reference_camera_projects_the_target_to_the_centre():
    x, y, depth = convert.project((0.0, 0.0, 0.0), **CAMERA)
    assert (x, y, depth) == pytest.approx((960.0, 540.0, 10.0))
    right, _, _ = convert.project((1.0, 0.0, 0.0), **CAMERA)
    _, above, _ = convert.project((0.0, 0.0, 1.0), **CAMERA)
    assert right > 960.0 and above < 540.0
    # The top edge of the frame is at tan(fov / 2) * depth above the target.
    _, edge, _ = convert.project((0.0, 0.0, 10.0 * math.tan(math.radians(20.0))), **CAMERA)
    assert edge == pytest.approx(0.0, abs=1e-6)
    with pytest.raises(ValueError, match="behind"):
        convert.project((0.0, -20.0, 0.0), **CAMERA)


def test_manim_camera_matches_the_reference_pinhole():
    cam = convert.manim_camera(position=(0.0, -10.0, 0.0), target=(0.0, 0.0, 0.0),
                               fov_y_deg=40.0)
    assert cam["phi_deg"] == pytest.approx(90.0)
    assert cam["theta_deg"] == pytest.approx(-90.0)
    assert cam["focal_distance"] == pytest.approx(10.0)
    # Manim shows 8 / zoom units of height at the frame centre; the pinhole
    # shows 2 * d * tan(fov / 2). They must be the same height.
    assert 8.0 / cam["zoom"] == pytest.approx(2 * 10.0 * math.tan(math.radians(20.0)))

    above = convert.manim_camera(position=(0.0, 0.0, 5.0), target=(0.0, 0.0, 0.0),
                                 fov_y_deg=40.0)
    assert above["phi_deg"] == pytest.approx(0.0)


def test_other_engine_cameras_keep_the_vertical_field_of_view():
    blender = convert.blender_camera(position=(1.0, 2.0, 3.0), target=(0.0, 0.0, 0.0),
                                     fov_y_deg=40.0)
    assert blender["sensor_fit"] == "VERTICAL"
    assert blender["angle_y"] == pytest.approx(math.radians(40.0))
    three = convert.three_camera(**CAMERA)
    assert three["fov"] == 40.0 and three["aspect"] == pytest.approx(16 / 9)
    assert three["position"] == [0.0, 0.0, 10.0] and three["up"] == [0.0, 1.0, 0.0]


def test_compile_expands_the_lattice_once_for_every_engine():
    compiled = compile_shot(load_spec(EXAMPLE), "lattice")
    assert len(compiled["spheres"]) == len(compiled["arrows"]) == 18
    assert compiled["background"] == "#0c0c0b"
    assert {s["color"] for s in compiled["spheres"]} == {"#d97757", "#6a9bcc"}
    xs = sorted({s["center"][0] for s in compiled["spheres"]})
    assert xs == pytest.approx([-1.6, 0.0, 1.6])
    for sphere, arrow in zip(compiled["spheres"], compiled["arrows"]):
        up = sphere["color"] == "#d97757"
        direction = arrow["end"][2] - arrow["start"][2]
        assert (direction > 0) == up
        assert abs(direction) == pytest.approx(0.55)
        assert abs(arrow["start"][2] - sphere["center"][2]) == pytest.approx(0.3)
    for key in ("camera", "manim_camera", "blender_camera", "three_camera"):
        assert key in compiled
    json.dumps(compiled)  # every value is JSON-ready


def test_blender_render_command_and_outputs(tmp_path, monkeypatch):
    monkeypatch.setenv("STUDIO_BLENDER", str(tmp_path / "blender.exe"))
    seen = {}

    def runner(command, timeout):
        seen["command"] = command
        frames = Path(command[command.index("--") + 2])
        frames.mkdir(parents=True)
        (frames / "frame_0001.png").write_bytes(b"png")
        return 0, "STUDIO_SHOT_OK"

    result = render.render_shot(EXAMPLE, "lattice", out_root=tmp_path / "shots",
                                runner=runner)
    command = seen["command"]
    assert command[command.index("--gpu-backend") + 1] == "opengl"
    assert command[command.index("--python") + 1].endswith("blender_shot.py")
    compiled = json.loads(Path(result["compiled"]).read_text(encoding="utf-8"))
    assert result["ok"] and result["engine"] == "blender"
    assert compiled["shot"] == "lattice" and compiled["frames"] == 1
    assert Path(result["image"]).is_file()


def test_manim_scene_file_defines_the_scene_in_the_file_manim_reads(tmp_path):
    seen = {}

    def runner(command, timeout):
        seen["command"] = command
        return 1, "no manim here"

    result = render.render_shot(EXAMPLE, "lattice", engine="manim",
                                out_root=tmp_path / "shots", runner=runner)
    scene_file = tmp_path / "shots" / "lattice" / "manim" / "shot_scene.py"
    assert "class StudioShot(build_scene(" in scene_file.read_text(encoding="utf-8")
    assert "1920,1080" in seen["command"]
    assert result["ok"] is False and result["detail"] == "no manim here"


def test_three_engine_is_not_renderable_yet(tmp_path):
    with pytest.raises(ValueError, match="cannot be rendered yet"):
        render.render_shot(EXAMPLE, "lattice", engine="three", out_root=tmp_path)
