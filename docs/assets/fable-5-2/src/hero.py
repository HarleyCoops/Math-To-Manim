"""hero.png: "Fable 5.2 Learns Manim" title image, rendered with Manim CE.

A real ThreeDScene. The object is the Hopf fibration: fibers of
h(z1, z2) = (2 z1 conj(z2), |z1|^2 - |z2|^2) on S^3, drawn in R^3 by
stereographic projection. Fibers over one circle of latitude of S^2 lie on
one torus; three latitudes give three nested tori of linked circles. The
fiber over one pole is the unit circle, the fiber over the other is the
vertical axis.

Depth is drawn by hand, as the Charter asks ("lighting by colour and
opacity"): every fiber is cut into short pieces, each piece is coloured and
weighted by its distance from the camera, and pieces are added far to near.

Usage:  .venv\\Scripts\\python.exe docs\\assets\\fable-5-2\\src\\hero.py
Writes: docs/assets/fable-5-2/hero.png  (1600 x 800)
"""

from __future__ import annotations

import sys
from pathlib import Path

import manimpango
import numpy as np
from manim import (
    DEGREES, DOWN, LEFT, RIGHT, UP, CapStyleType, Line, ManimColor, MathTex,
    Polygon, Text, ThreeDScene, VGroup, VMobject, interpolate_color, tempconfig,
)
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import style as S  # noqa: E402

for _font in (S.FONT_BOLD, S.FONT_REGULAR, S.FONT_ITALIC):
    manimpango.register_font(_font)
HEAD = "Poppins" if "Poppins" in S.FONT_BOLD else "Segoe UI"
CAPTION = "Lora" if "Lora" in S.FONT_ITALIC else "Segoe UI"

PHI, THETA = 60 * DEGREES, -58 * DEGREES
SCALE = 1.06                 # world units per unit of the projected S^3
OBJECT_SCREEN_X = 4.5        # where the object's centre sits on screen
OBJECT_SCREEN_Y = 0.2

CAM = np.array([np.sin(PHI) * np.cos(THETA), np.sin(PHI) * np.sin(THETA), np.cos(PHI)])
SCREEN_RIGHT = np.array([-np.sin(THETA), np.cos(THETA), 0.0])
SCREEN_UP = np.cross(CAM, SCREEN_RIGHT)
LIGHT = (0.55 * CAM + 0.75 * SCREEN_UP - 0.45 * SCREEN_RIGHT)
LIGHT /= np.linalg.norm(LIGHT)
# The object is moved in world space, along the screen axes, so that it sits
# right of the title. (ThreeDCamera's frame_center also moves fixed-in-frame
# text, so it is not used.)
OFFSET = OBJECT_SCREEN_X * SCREEN_RIGHT + OBJECT_SCREEN_Y * SCREEN_UP


def fiber(eta: float, xi: float, n: int) -> np.ndarray:
    """n+1 points of the Hopf fiber over (colatitude 2*eta, longitude xi)."""
    t = np.linspace(0, 2 * np.pi, n + 1)
    x1, x2 = np.cos(eta) * np.cos(t + xi), np.cos(eta) * np.sin(t + xi)
    x3, x4 = np.sin(eta) * np.cos(t), np.sin(eta) * np.sin(t)
    return SCALE * np.stack([x1, x2, x3], axis=1) / (1 - x4)[:, None]


def label(text: str, size: float, **kwargs) -> Text:
    """Text set large and scaled down: Pango kerns small sizes badly."""
    return Text(text, font_size=size * 4, **kwargs).scale(0.25)


def torus_point(eta: float, u: float, v: float) -> np.ndarray:
    """The torus |z1| = cos(eta) of S^3, projected the same way."""
    x1, x2 = np.cos(eta) * np.cos(u), np.cos(eta) * np.sin(u)
    x3, x4 = np.sin(eta) * np.cos(v), np.sin(eta) * np.sin(v)
    return SCALE * np.array([x1, x2, x3]) / (1 - x4)


class FableHero(ThreeDScene):
    def construct(self):
        self.camera.background_color = S.INK
        self.set_camera_orientation(phi=PHI, theta=THETA, zoom=1.0)
        # A long lens: the object sits off-centre and a short one would skew it.
        self.camera.set_focal_distance(80.0)
        ink, ivory = ManimColor(S.INK), ManimColor(S.IVORY)
        pieces: list[tuple[float, VMobject]] = []

        def depth_of(points: np.ndarray) -> float:
            return float(np.mean(points, axis=0) @ CAM)

        d_near, d_far = 3.1 * SCALE, -3.1 * SCALE

        def nearness(depth: float) -> float:
            return float(np.clip((depth - d_far) / (d_near - d_far), 0, 1))

        def add_curve(points: np.ndarray, color: str, width: float, step: int = 2,
                      halo: bool = True, fade: np.ndarray | None = None) -> None:
            base = ManimColor(color)
            for i in range(0, len(points) - 1, step):
                seg = points[i:i + step + 1]
                depth = depth_of(seg)
                k = nearness(depth)
                tone = 0.26 + 0.74 * k ** 1.5
                if fade is not None:
                    tone *= float(fade[i])
                shade = interpolate_color(ink, base, tone)
                if k > 0.8:  # nearest pieces catch the light
                    shade = interpolate_color(shade, ivory, 0.9 * (k - 0.8))
                core = VMobject().set_points_as_corners(seg + OFFSET)
                core.set_stroke(shade, width=width * (0.45 + 0.95 * k), opacity=1.0)
                core.set_cap_style(CapStyleType.ROUND)
                pieces.append((depth, core))
                if halo and k > 0.35:
                    glow = VMobject().set_points_as_corners(seg + OFFSET)
                    glow.set_stroke(base, width=width * 4.2 * k, opacity=0.10 * k * tone)
                    glow.set_cap_style(CapStyleType.ROUND)
                    pieces.append((depth - 0.02, glow))

        # --- glass torus for the inner latitude: faces lit by hand ---------
        eta_glass = 0.30
        nu, nv = 56, 30
        us = np.linspace(0, 2 * np.pi, nu + 1)
        vs = np.linspace(0, 2 * np.pi, nv + 1)
        grid = np.array([[torus_point(eta_glass, u, v) for v in vs] for u in us])
        ember = ManimColor(S.EMBER)
        for i in range(nu):
            for j in range(nv):
                quad = np.array([grid[i, j], grid[i + 1, j], grid[i + 1, j + 1], grid[i, j + 1]])
                normal = np.cross(quad[1] - quad[0], quad[3] - quad[0])
                norm = np.linalg.norm(normal)
                if norm < 1e-9:
                    continue
                normal /= norm
                lambert = abs(float(normal @ LIGHT))
                facing = abs(float(normal @ CAM))
                face = Polygon(*(quad + OFFSET), stroke_width=0)
                face.set_fill(interpolate_color(ink, ember, 0.25 + 0.75 * lambert),
                              opacity=0.10 + 0.30 * lambert ** 2 + 0.16 * (1 - facing) ** 2)
                pieces.append((depth_of(quad) - 0.05, face))

        # --- fibers: three latitudes, three nested tori ---------------------
        for eta, color, count, width in (
            (0.30, S.CORAL, 12, 3.6),
            (0.62, S.SKY, 14, 3.2),
            (0.90, S.GOLD, 16, 2.8),
        ):
            for xi in np.linspace(0, 2 * np.pi, count, endpoint=False):
                add_curve(fiber(eta, xi, 120), color, width)

        # --- the two special fibers ----------------------------------------
        add_curve(fiber(0.0, 0.0, 120), S.IVORY, 4.2)                 # unit circle
        zs = np.linspace(-3.6, 3.6, 121)
        axis = np.stack([0 * zs, 0 * zs, zs], axis=1) * SCALE
        add_curve(axis, S.OLIVE, 3.6, fade=np.clip(1.6 - np.abs(zs) / 2.6, 0, 1),
                  halo=False)

        for _, mob in sorted(pieces, key=lambda item: item[0]):
            self.add(mob)

        # --- narration layer (fixed in frame) --------------------------------
        left = -7.1
        rule = Line(LEFT * 0.33, RIGHT * 0.33, stroke_width=5, color=S.CORAL)
        kicker = label("MATH-TO-MANIM   /   THE MYTHOS CHAIN", 20, font=HEAD, color=S.FOG)
        kicker_row = VGroup(rule, kicker).arrange(RIGHT, buff=0.28)
        kicker_row.move_to([left, 2.95, 0], aligned_edge=LEFT)

        line1 = Text("Fable 5.2", font=HEAD, weight="BOLD", font_size=76, color=S.IVORY)
        line2 = Text("Learns Manim", font=HEAD, weight="BOLD", font_size=76, color=S.CORAL)
        line1.move_to([left, 1.62, 0], aligned_edge=LEFT)
        line2.move_to([left, 0.5, 0], aligned_edge=LEFT)

        note = label("Six reasoning stages, then codegen, verify, render, repair.",
                     19, font=HEAD, color=S.IVORY)
        note.move_to([left, -0.62, 0], aligned_edge=LEFT)

        formula = MathTex(
            r"h(", r"z_1", r",", r"z_2", r")", r"=",
            r"\bigl(\,2", r"z_1", r"\bar{z}_2", r",\;", r"|z_1|^2", r"-", r"|z_2|^2", r"\bigr)",
            r"\qquad", r"h\colon S^3 \to S^2",
            font_size=34, color=S.IVORY,
        )
        for index in (1, 7, 10):
            formula[index].set_color(S.CORAL)
        for index in (3, 8, 12):
            formula[index].set_color(S.SKY)
        formula[15].set_color(S.GOLD)
        formula.move_to([left, -2.42, 0], aligned_edge=LEFT)

        caption = label(
            "The Hopf map. Each circle is the fiber over one point of the sphere.",
            20, font=CAPTION, slant="ITALIC", color=S.FOG)
        caption.move_to([left, -3.18, 0], aligned_edge=LEFT)

        credit = label("Still from a Manim CE ThreeDScene", 16, font=HEAD, color=S.MUTED)
        credit.move_to([7.1, -3.42, 0], aligned_edge=RIGHT)

        self.add_fixed_in_frame_mobjects(kicker_row, line1, line2, note, formula,
                                         caption, credit)


def main() -> None:
    scale = 2  # render at 2x, then downsample for clean edges
    with tempconfig({
        "pixel_width": 1600 * scale, "pixel_height": 800 * scale,
        "frame_width": 16.0, "frame_height": 8.0,
        "save_last_frame": True, "write_to_movie": False, "disable_caching": True,
        "media_dir": str(Path(__file__).resolve().parent / "media"),
        "verbosity": "WARNING",
    }):
        scene = FableHero()
        scene.render()
        frame = scene.renderer.get_frame()
    image = Image.fromarray(frame).convert("RGB")
    image = image.resize((1600, 800), Image.LANCZOS)
    out = S.OUT_DIR / "hero.png"
    image.save(out, optimize=True)
    print(out, image.size, out.stat().st_size)


if __name__ == "__main__":
    main()
