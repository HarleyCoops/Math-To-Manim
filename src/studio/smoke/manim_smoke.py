"""Studio smoke scene for Manim: the same crystal idea as the Blender scene.

    python -m manim -s -ql --media_dir <dir> manim_smoke.py StudioSmoke

``studio doctor`` renders one still from it and times the render.
"""

from manim import (
    DEGREES,
    UP,
    Arrow3D,
    MathTex,
    Sphere,
    ThreeDScene,
)

PAPER = "#0c0c0b"
CORAL = "#d97757"
BLUE = "#6a9bcc"
IVORY = "#faf9f5"


class StudioSmoke(ThreeDScene):
    def construct(self):
        self.camera.background_color = PAPER
        self.set_camera_orientation(phi=65 * DEGREES, theta=-45 * DEGREES, zoom=0.9)
        for ix in range(3):
            for iy in range(3):
                up = (ix + iy) % 2 == 0
                color = CORAL if up else BLUE
                point = [(ix - 1) * 1.6, (iy - 1) * 1.6, 0.0]
                atom = Sphere(radius=0.3, resolution=(12, 24)).move_to(point)
                atom.set_color(color)
                tip = [point[0], point[1], 0.9 if up else -0.9]
                spin = Arrow3D(start=point, end=tip, color=color, resolution=8)
                self.add(atom, spin)
        label = MathTex(r"E_{\uparrow}(\mathbf{k}) \neq E_{\downarrow}(\mathbf{k})",
                        color=IVORY, font_size=44)
        label.to_edge(UP)
        self.add_fixed_in_frame_mobjects(label)
        self.wait(0.1)
