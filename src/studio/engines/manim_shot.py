"""Draw a compiled shot with Manim.

``render.py`` writes a three-line scene file per shot that calls
``build_scene`` with the path of the compiled shot. The scene uses the camera
values that ``studio.spec.convert.manim_camera`` computed, so its picture
matches the reference pinhole camera.
"""

from __future__ import annotations

import json
from pathlib import Path

from manim import DEGREES, Arrow3D, Sphere, ThreeDScene


def build_scene(compiled_path: str | Path) -> type[ThreeDScene]:
    compiled = json.loads(Path(compiled_path).read_text(encoding="utf-8"))

    class StudioShot(ThreeDScene):
        def construct(self) -> None:
            self.camera.background_color = compiled["background"]
            cam = compiled["manim_camera"]
            self.set_camera_orientation(
                phi=cam["phi_deg"] * DEGREES,
                theta=cam["theta_deg"] * DEGREES,
                focal_distance=cam["focal_distance"],
                zoom=cam["zoom"],
                frame_center=cam["frame_center"],
            )
            for item in compiled["spheres"]:
                sphere = Sphere(center=item["center"], radius=item["radius"],
                                resolution=(16, 32), checkerboard_colors=False,
                                fill_color=item["color"], fill_opacity=1.0,
                                stroke_width=0)
                self.add(sphere)
            for item in compiled["arrows"]:
                arrow = Arrow3D(start=item["start"], end=item["end"],
                                thickness=item["shaft_radius"],
                                height=item["head_length"],
                                base_radius=item["head_radius"],
                                color=item["color"], resolution=12)
                self.add(arrow)
            self.wait(1 / compiled["fps"])

    return StudioShot
