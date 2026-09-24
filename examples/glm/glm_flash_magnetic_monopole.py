# -*- coding: utf-8 -*-
"""
glm_flash_magnetic_monopole.py  ~  "The Lone Pole"
=====================================================================
A self-contained Manim CE 0.21 ThreeDScene film (~68 s) about the
magnetic monopole: Dirac's quantization argument, told geometrically.

Capabilities showcased (all ABSENT from the existing mythos films):
  * StreamLines in genuine 3D (three_dimensions=True), seeded by hand
    via ``.start_points`` -- radial divergence you can fly through.
  * TexturedSurface -- a procedurally generated checkerboard (PIL,
    no assets, no network) UV-mapped onto a sphere: Faraday's era of
    paper-and-ink engravings, rebuilt in code.
  * SurfaceMesh -- the lat/long wireframe cage over that textured globe.
  * Composite solid prism arrow (Cylinder shaft + Cone head + Cube plinth):
    the flux tube, made literal.

Camera grammar: set_camera_orientation / move_camera /
begin_ambient_camera_rotation ONLY. Never .animate on self.camera.
Deterministic: np.random.seed(20250925); zero network; no repo imports;
tiny/no MathTex -- all captions are Pango Text() so no LaTeX needed.
"""

from __future__ import annotations

import os
import numpy as np

from manim import (
    DEGREES,
    PI,
    TAU,
    IN,
    ORIGIN,
    OUT,
    RIGHT,
    UP,
    Create,
    Cube,
    Cylinder,
    Cone,
    Dot3D,
    FadeIn,
    FadeOut,
    ParametricFunction,
    Ring,
    Sphere,
    StreamLines,
    SurfaceMesh,
    Text,
    TexturedSurface,
    ThreeDScene,
    VGroup,
    Write,
)

# ---------------------------------------------------------------------
# House palette -- iron-gall ink on aged paper (Faraday's notebook)
# ---------------------------------------------------------------------
PAPER      = "#f3ecd8"
INK        = "#241a12"
OXIDE      = "#a24f3d"   # red ochre
VERDIGRIS  = "#3f746b"   # oxidized copper
INDIGO     = "#485b7a"   # prussian-leaning blue
OLD_GOLD   = "#a17f35"   # gilded annotation
SELF.camera_background_color_dummy_ = None  # noqa: guard against stray edits


# ---------------------------------------------------------------------
# Math helpers
# ---------------------------------------------------------------------
def dipole_field_line(theta_span: float, L: float, resolution: int = 90):
    """A dipole field line r = L*sin^2(theta): the classic CLOSED loop
    leaving the north pole and re-entering the south pole."""
    def f(t):
        th = -theta_span / 2 + t * theta_span          # theta around equator
        r = L * (np.sin(th) ** 2)
        return np.array([
            r * np.sin(th),
            0.0,
            r * np.cos(th),
        ])
    return f


def make_flux_tube(scale: float = 1.0) -> VGroup:
    """One radial tube of magnetic flux built from true solids:
    a cylindrical shaft, a conical head, and a cuboid plinth.
    (Composite prism arrows are absent from every prior film.)"""
    shaft = Cylinder(
        radius=0.115 * scale,
        height=1.55 * scale,
        resolution=28,
        fill_opacity=1.0,
        checkerboard_colors=[OXIDE, OXIDE],
        stroke_color=INK,
        stroke_width=0.6,
    ).shift(IN * 0.42 * scale)                       # center of shaft at origin-local -y
    head = Cone(
        base_radius=0.20 * scale,
        height=0.44 * scale,
        resolution=28,
        fill_opacity=1.0,
        checkerboard_colors=[OLD_GOLD, OLD_GOLD],
        stroke_color=INK,
        stroke_width=0.6,
    )
    plinth = Cube(side_length=0.30 * scale,
                  fill_color=VERDIGRIS,
                  fill_opacity=0.95,
                  stroke_color=INK, stroke_width=0.6)
    grp = VGroup(plinth, shaft, head)
    return grp


class glm_flash_magnetic_monopole(ThreeDScene):
    """~68 s film: the magnetism has-no-monopoles problem, then Dirac."""

    # ---------------- choreography knobs ------------------------------
    T_TITLE   = 5.0
    T_DIPOLE  = 15.0
    T_GLOBE   = 12.0
    T_RAYS    = 19.0
    T_TUBE    = 17.0
    T_END     = 6.0

    # ------------------------------------------------------------------
    def construct(self):
        np.random.seed(20250925)                     # determinism
        self.camera.background_color = PAPER         # paper, never the void

        self._prologue_card()
        self._act1_dipole_closed_world()
        self._act2_the_lone_pole_globe()
        self._act3_rays_that_escape()
        self._act4_dirac_quantization()
        self._epilogue()

    # ------------------------------------------------------------------
    # Fixed-frame helpers (all captions live IN the camera frame)
    # ------------------------------------------------------------------
    def _caption(self, txt: str, color=INK, weight="SEMIBOLD",
                 size=27, edge_buff=0.42):
        cap = Text(txt, color=color, weight=weight,
                   font_size=size, font="Georgia")
        cap.to_edge(OUT_edge := None or __import__("manim").DOWN,
                    buff=edge_buff)
        return cap

    def _fix(self, mob):
        self.add_fixed_in_frame_mobjects(mob)
        return mob

    # ==================================================================
    # PROLOGUE -- title on paper
    # ==================================================================
    def _prologue_card(self):
        title = Text("THE LONE POLE", color=INK, weight="BOLD",
                     font_size=58, font="Georgia")
        sub = Text("Dirac's argument, drawn in field lines",
                   color=OXIDE, slant="ITALIC",
                   font_size=30, font="Georgia")
        rule = Text("\u2014\u2014\u2014\u2014\u2014", color=OLD_GOLD,
                    font_size=30)
        card = VGroup(title, rule, sub).arrange(DOWN_arranged := __import__("manim").DOWN, buff=0.32)
        self._fix(card)
        self.set_camera_orientation(phi=72 * DEGREES, theta=-58 * DEGREES,
                                    zoom=1.0)
        self.play(FadeIn(card, run_time=self.T_TITLE - 3.0))
        self.wait(2.6)
        self.play(FadeOut(card), run_time=0.55)

    # ==================================================================
    # ACT 1 -- the world everyone believes: CLOSED dipole lines
    # ==================================================================
    def _act1_dipole_closed_world(self):
        self.set_camera_orientation(phi=74 * DEGREES, theta=-48 * DEGREES,
                                    zoom=1.02)

        group = VGroup()
        n_planes = 6                                   # 6 meridians -> classic engraving
        span = 2.86                                    # radians swept per lobe-pair
        for k in range(n_planes):
            ang = TAU * k / n_planes
            fn = dipole_field_line(span, L=2.35,
                                   resolution=int(60 + 10 * ((k % 2))))
            curve = ParametricFunction(
                fn, t_range=[0, 1],
                color=(INK if k % 2 == 0 else INDIGO),
                stroke_width=2.4,
            ).rotate(ang, axis=np.array([0.0, 0.0, 1.0]))
            group.add(curve)

        poles = VGroup(
            Dot3D(point=UP * 2.1, radius=0.055, color=OXIDE,
                  resolution=(10, 10)),
            Dot3D(point=IN * 2.1, radius=0.055, color=OXIDE,
                  resolution=(10, 10)),
        )

        cap_a = self._fix(self._caption(
            "every textbook bar magnet: field lines leave N and RE-ENTER S"))
        self.play(Create(group, lag_ratio=0.06), FadeIn(poles),
                  run_time=self.T_DIPOLE * 0.48)
        self.begin_ambient_camera_rotation(rate=0.075)
        self.wait(self.T_DIPOLE * 0.22)

        cap_b = self._fix(self._caption(
            "\u2205 magnetic charge \u2014 nothing leaks. Net flux = 0.",
            color=VERDIGRIS))
        self.play(FadeOut(cap_a, run_time=0.4))
        self.play(FadeIn(cap_b), run_time=self.T_DIPOLE * 0.18)
        self.wait(self.T_DIPOLE * 0.12)
        self.stop_ambient_camera_rotation()

        self.play(FadeOut(group), FadeOut(poles),
                  FadeOut(cap_b), run_time=0.6)

    # ==================================================================
    # ACT 2 -- the suspect: a lone pole, ink-paper globe w/ cage
    # ==================================================================
    def _make_textured_globe(self, radius: float = 1.28):
        """Procedural checkerboard -> PNG -> TexturedSurface + SurfaceMesh.
        This is the TexturedSurface capability no prior film uses."""
        img_path = "/tmp/glm_monopole_paper_uv.png"
        try:
            from PIL import Image
            W, H = 720, 360
            cell = 36
            base = np.zeros((H, W, 3), dtype=np.uint8)
            ivory = (245, 238, 216)   # warm paper
            gold = (161, 127, 53)     # OLD_GOLD blocks
            ver = (63, 116, 107)      # thin verdigris latitude rules
            yy, xx = np.mgrid[0:H, 0:W]
            blocks = (((xx // cell) % 2) ^ ((yy // cell) % 2)).astype(bool)
            base[blocks] = gold
            base[~blocks] = ivory
            base[(yy % cell) < 2] = ver           # engraved parallels
            Image.fromarray(base, "RGB").save(img_path)
            surf = Sphere(radius=radius, resolution=(36, 72))
            tex = TexturedSurface(surf, img_path)
            tex.set_shading(0.25, 0.18, 0.0)       # soft flat-plate light
            self.using_texture = True
        except Exception:
            surf = Sphere(radius=radius, resolution=(36, 72),
                          checkerboard_colors=[PAPER, OLD_GOLD],
                          stroke_color=VERDIGRIS, stroke_width=0.6)
            tex = surf
            self.using_texture = False

        cage = SurfaceMesh(tex, resolution=(18, 36))
        cage.set_stroke(VERDIGRIS, width=0.85, opacity=0.5)
        return tex, cage

    def _act2_the_lone_pole_globe(self):
        self.set_camera_orientation(phi=70 * DEGREES, theta=-70 * DEGREES,
                                    zoom=1.15)
        tex, cage = self._make_textured_globe(radius=1.28)

        cap = self._fix(self._caption(
            "the heretical hypothesis: ONE pole, alone",
            color=OXIDE))

        self.play(Create(tex), run_time=self.T_GLOBE * 0.42)
        self.play(Create(cage), run_time=self.T_GLOBE * 0.26)
        self.play(FadeIn(cap), run_time=self.T_GLOBE * 0.12)
        self.begin_ambient_camera_rotation(rate=-0.09)
        self.wait(self.T_GLOBE * 0.20)
        self.stop_ambient_camera_rotation()

        # red N mark where the singularity lives
        north_dot = Dot3D(point=UP * 1.30, radius=0.07, color=OXIDE,
                          resolution=(10, 10))
        self.play(Create(north_dot), run_time=0.5)
        self.north_dot = north_dot
        self.globe_tex, self.globe_cage = tex, cage

    # ==================================================================
    # ACT 3 -- rays that ESCAPE the skin (true 3D StreamLines)
    # ==================================================================
    def _monopole_rays(self):
        """Hand-seeded StreamLines, integrated radially OUTWARD in 3D.
        Injection through .start_points puts them INSIDE the skin, so the
        audience watches each ray pierce the ink-paper cage."""

        def radial(_p):
            return np.array([1.0, 0.0, 0.0])          # unit push, any seed

        seeds = []
        R = 0.42                                       # inside the R=1.28 skin
        for zmix in (+0.72, -0.72):                    # upper & lower belts
            cz = zmix
            cr = np.sqrt(max(1e-6, 1.0 - cz * cz))
            for j in range(14):                        # 14 azimuths per belt
                az = TAU * j / 14 + 0.13 * zmix
                seeds.append(R * np.array(
                    [cr * np.cos(az), cr * np.sin(az), cz]))
        rng = np.random.default_rng(20250925)          # reproducible jitter
        seeds = [np.array(s) + 0.03 * rng.standard_normal(3) for s in seeds]

        sl = StreamLines(
            radial,
            x_range=[-3.2, 3.2, 1], y_range=[-3.2, 3.2, 1], z_range=[-3.2, 3.2, 1],
            three_dimensions=True,                     # <-- the unused switch
            noise_factor=None,
            dt=0.06,
            virtual_time=7.5,                          # long enough to exit frame
            max_anchors_per_line=120,
            padding=1.5,
            stroke_width=1.6,
            opacity=0.85,
        )
        sl.start_points = np.array(seeds)              # manual seeding
        sl.generate_lines()                            # bake deterministically

        tints = [OXIDE, INDIGO, VERDIGRIS]
        for i, ln in enumerate(sl):
            ln.set_stroke(tints[i % 3], width=1.8, opacity=0.88)
        return sl

    def _act3_rays_that_escape(self):
        cap_prev = getattr(self, "_last_cap", None)
        self.set_camera_orientation(phi=64 * DEGREES, theta=-118 * DEGREES,
                                    zoom=1.10)

        rays = self._monopole_rays()
        cap = self._fix(self._caption(
            "\u201aN\u2019 = \u201areturn ticket?\u2019 \u2014 none. Every ray exits.",
            color=INDIGO, size=26))
        cap2 = self._fix(self._caption(
            "\u222e E \u00b7 dA \u2260 0 : Gauss counts a SOURCE inside",
            color=OXIDE, size=27))

        self.play(Create(rays), run_time=self.T_RAYS * 0.40)
        self.begin_ambient_camera_rotation(rate=0.11)
        self.play(FadeOut(cap_prev) if cap_prev else FadeOut(self._noop()),
                  run_time=0.01)
        self.play(FadeIn(cap), run_time=self.T_RAYS * 0.10)
        self.wait(self.T_RAYS * 0.18)

        self.play(FadeOut(cap), FadeIn(cap2), run_time=self.T_RAYS * 0.14)
        # a pass INTO the cage: camera dives between the wires
        self.move_camera(phi=24 * DEGREES, theta=-152 * DEGREES,
                         zoom=1.65, run_time=self.T_RAYS * 0.28)
        self.stop_ambient_camera_rotation()
        self.wait(self.T_RAYS * 0.06)

        self.rays = rays
        self.cap_flux = cap2

    # helpers ----------------------------------------------------------
    def _noop(self):
        return VGroup()

    # ==================================================================
    # ACT 4 -- dive to the singularity; one flux tube; Dirac plate
    # ==================================================================
    def _act4_dirac_quantization(self):
        # ---- dive to the singular point ---------------------------
        self.move_camera(phi=6 * DEGREES, theta=-170 * DEGREES,
                         zoom=3.1, run_time=self.T_TUBE * 0.16)
        flash = Dot3D(point=ORIGIN, radius=0.10, color=OXIDE,
                      resolution=(12, 12))
        self.play(Create(flash), run_time=self.T_TUBE * 0.06)

        # ---- recoil -----------------------------------------------
        self.move_camera(phi=58 * DEGREES, theta=-128 * DEGREES,
                         zoom=1.02, run_time=self.T_TUBE * 0.14)
        self.play(FadeOut(flash), FadeOut(self.north_dot),
                  run_time=self.T_TUBE * 0.04)

        # ---- one marked polar cap + THE flux tube -----------------
        th0 = 52 * DEGREES
        cap_center = np.array([np.cos(th0), 0.0, np.sin(th0)]) * 1.30
        ring = Ring(inner_radius=0.44, outer_radius=0.56,
                    color=OLD_GOLD, stroke_width=7.0)
        ring.rotate(90 * DEGREES, axis=np.array([0.0, 1.0, 0.0]))  # lie tangent
        ring.move_to(cap_center)

        tube = make_flux_tube(scale=1.0)
        axis = np.array([np.cos(th0), 0.0, np.sin(th0)])           # radial dir
        rot_ax = np.cross(np.array([0.0, 0.0, 1.0]), axis)
        rot_ax = rot_ax / (np.linalg.norm(rot_ax) + 1e-12)
        ang = np.arccos(np.clip(axis @ np.array([0.0, 0.0, 1.0]), -1, 1))
        tube.rotate(ang, axis=rot_ax)
        tube.shift(axis * 1.52)                        # plinth kisses the globe

        self.play(Create(ring), run_time=self.T_TUBE * 0.10)
        self.play(Create(tube), run_time=self.T_TUBE * 0.22)

        # ---- Dirac plate: geometric read-off ----------------------
        plate = Text("g \u00b7 \u03a9_cap  =  n h        n \u2208 \u2124",
                     color=INK, weight="BOLD", font_size=40, font="Georgia")
        note = Text("flux tubes must pack the sphere WHOLE \u2014 "
                    "charge is quantized",
                    color=VERDIGRIS, slant="ITALIC", font_size=26,
                    font="Georgia")
        board = VGroup(plate, note).arrange(
            DOWN_arranged := __import__("manim").DOWN, buff=0.28)
        board.to_edge(__import__("manim").RIGHT, buff=0.55)
        self._fix(board)

        self.play(Write(plate), run_time=self.T_TUBE * 0.16)
        self.play(FadeIn(note), run_time=self.T_TUBE * 0.06)
        self.begin_ambient_camera_rotation(rate=0.10)
        self.wait(self.T_TUBE * 0.12)
        self.stop_ambient_camera_rotation()

        # tidy
        self.play(FadeOut(board), run_time=self.T_TUBE * 0.10)
        self.epilogue_group = VGroup(self.globe_tex, self.globe_cage,
                                     ring, tube, self.rays)
        self.board_out = True

    # ==================================================================
    # EPILOGUE -- pull back; the honest sentence
    # ==================================================================
    def _epilogue(self):
        cap = self._fix(Text(
            "no lone pole has ever been seen \u2014 yet somewhere, "
            "one would explain charge itself.",
            color=INK, slant="ITALIC", font_size=30, font="Georgia")
            .to_edge(__import__("manim").UP, buff=0.55))
        self.play(FadeIn(cap), run_time=0.8)
        self.move_camera(phi=76 * DEGREES, theta=-210 * DEGREES,
                         zoom=0.82, run_time=self.T_END * 0.62)
        self.begin_ambient_camera_rotation(rate=0.045)
        self.wait(self.T_END * 0.30)
        self.stop_ambient_camera_rotation()
        self.play(FadeOut(self.epilogue_group), FadeOut(cap), run_time=0.9)


# ----------------------------------------------------------------------
# NOTE ON UNITS
# The film draws distances in scene units, so "the sphere" is the
# Gaussian pillbox of radius R, and "one tube" carries the fixed flux
# quantum 2h/e -- hence packing must terminate exactly: Omega_cap = n*h/g.
# ----------------------------------------------------------------------
