# -*- coding: utf-8 -*-
"""
glm_flash_magnetic_monopole.py   ~   "The Lone Pole"
=====================================================================
Self-contained Manim CE 0.21 (cairo) ThreeDScene film (~70 s):
Dirac's magnetic-monopole argument, drawn geometrically.

Unused-in-the-canon capabilities showcased:
  * StreamLines(three_dimensions=True): a genuine 3D radial field,
    integrated by CE itself over a fixed lattice -- divergence you
    fly through (no prior mythos film uses 3D StreamLines).
  * Composite solid prism arrow: Cylinder shaft + Cone head + Cube
    plinth -- the flux quantum as a physical object.
  * Ink-paper checkered Sphere + hand-built lat/long Circle cage
    (Faraday's engraving rebuilt; TexturedSurface/SurfaceMesh are not
    exported on this install, so the cage is authored by hand).

Camera grammar: set_camera_orientation / move_camera /
begin_ambient_camera_rotation ONLY. Never .animate on self.camera.
Deterministic; no network; no repo imports; no LaTeX needed.
"""

from __future__ import annotations

import numpy as np

from manim import (
    Circle,
    Cone,
    Create,
    Cube,
    Cylinder,
    DEGREES,
    Dot3D,
    DOWN,
    IN,
    ORIGIN,
    OUT,
    PI,
    RIGHT,
    TAU,
    UP,
    FadeIn,
    FadeOut,
    ParametricFunction,
    Sphere,
    StreamLines,
    Text,
    ThreeDScene,
    VGroup,
    Write,
)

# ---------------------------------------------------------------------
# House palette -- iron-gall ink on aged paper (Faraday's notebook)
# ---------------------------------------------------------------------
PAPER     = "#f3ecd8"
INK       = "#241a12"
OXIDE     = "#a24f3d"    # red ochre
VERDIGRIS = "#3f746b"    # oxidized copper
INDIGO    = "#485b7a"    # prussian-leaning blue
OLD_GOLD  = "#a17f35"    # gilded annotation


def _solid(fill_hex, kind, **kw):
    """Build a Cylinder/Cone solid uniform-coloured, tolerating installs
    whose Surface kwargs differ slightly."""
    uni = dict(fill_opacity=1.0, fill_color=fill_hex,
               checkerboard_colors=[fill_hex, fill_hex],
               stroke_color=INK, stroke_width=0.7)
    uni.update(kw)
    try:
        return kind(**uni)
    except TypeError:
        for opt in ("checkerboard_colors",):
            uni.pop(opt, None)
        return kind(**uni)


class glm_flash_magnetic_monopole(ThreeDScene):
    """~70 s: why 'no lone pole', and how Dirac turned one into q = n h."""

    # ---------------- choreography beats ------------------------------
    T_TITLE  = 5.0
    T_DIPOLE = 15.0
    T_GLOBE  = 12.0
    T_RAYS   = 19.0
    T_TUBE   = 17.0
    T_END    = 6.0

    def construct(self):
        np.random.seed(20250925)              # determinism insurance
        self.camera.background_color = PAPER  # paper ground, never void

        self._prologue()
        self._act1_closed_world()
        self.globe, self.cage = self._act2_lone_pole()
        self.rays = self._act3_rays_escape()
        self.tube_stage = self._act4_dirac_quantization()
        self._epilogue()

    # ---------------- fixed-frame caption helper ----------------------
    def _cap(self, txt, color=INK, size=27, weight="SEMIBOLD"):
        cap = Text(txt, color=color, weight=weight,
                   font_size=size, font="Georgia")
        cap.to_edge(DOWN, buff=0.42)
        self.add_fixed_in_frame_mobjects(cap)
        return cap

    # ==================================================================
    # PROLOGUE
    # ==================================================================
    def _prologue(self):
        title = Text("THE LONE POLE", weight="BOLD", font_size=58,
                     color=INK, font="Georgia")
        rule = Text("\u2014\u2014\u2014\u2014\u2014\u2014", color=OLD_GOLD,
                    font_size=26)
        sub = Text("Dirac's argument, drawn in field lines",
                   slant="ITALIC", font_size=30, color=OXIDE, font="Georgia")
        card = VGroup(title, rule, sub).arrange(DOWN, buff=0.30)
        self.add_fixed_in_frame_mobjects(card)
        self.set_camera_orientation(phi=74 * DEGREES, theta=-60 * DEGREES,
                                    zoom=1.0)
        self.play(FadeIn(card), run_time=self.T_TITLE - 3.0)
        self.wait(2.6)
        self.play(FadeOut(card), run_time=0.55)

    # ==================================================================
    # ACT 1 -- the belief: CLOSED dipole loops (r = L sin^2 theta)
    # ==================================================================
    @staticmethod
    def _dipole_fn(span, L):
        def fn(t):
            th = -span / 2 + t * span
            r = L * np.sin(th) ** 2
            return np.array([r * np.sin(th), 0.0, r * np.cos(th)])
        return fn

    def _act1_closed_world(self):
        self.set_camera_orientation(phi=76 * DEGREES, theta=-48 * DEGREES,
                                    zoom=1.02)
        loops = VGroup()
        planes = 6                       # six meridians: classic engraving
        for k in range(planes):
            f = self._dipole_fn(2.86, 2.35)
            c = ParametricFunction(f, t_range=[0, 1], stroke_width=2.5,
                                   color=(INK if k % 2 == 0 else INDIGO))
            c.rotate(TAU * k / planes, axis=OUT)
            loops.add(c)
        dots = VGroup(
            Dot3D(point=UP * 2.05, radius=0.055, color=OXIDE),
            Dot3D(point=DOWN * 2.05, radius=0.055, color=OXIDE),
        )
        cap1 = self._cap(
            "textbook bar magnet: leave N \u00b7 re-enter S \u00b7 always CLOSED")
        self.play(Create(loops, lag_ratio=0.08), FadeIn(dots),
                  run_time=self.T_DIPOLE * 0.46)
        self.begin_ambient_camera_rotation(rate=0.07)
        self.wait(self.T_DIPOLE * 0.20)
        cap2 = self._cap("\u2205 magnetic charge \u2014 net flux 0",
                         color=VERDIGRIS)
        self.remove(cap1)
        self.play(FadeIn(cap2), run_time=self.T_DIPOLE * 0.16)
        self.wait(self.T_DIPOLE * 0.18)
        self.stop_ambient_camera_rotation()
        self.remove(cap2)
        self.play(FadeOut(loops), FadeOut(dots), run_time=0.6)

    # ==================================================================
    # ACT 2 -- the heresy: ONE pole, ink-paper globe + hand-built cage
    # ==================================================================
    def _paper_globe(self, R=1.28):
        """Checkered paper sphere (Surface checkerboard shading) with a
        hand-authored lat/long wire cage of Stroked Circles."""
        globe = Sphere(
            radius=R, resolution=(36, 64),
            checkerboard_colors=[PAPER, OLD_GOLD],
            fill_opacity=0.96,
            stroke_color=VERDIGRIS, stroke_width=0.4,
        )
        cage = VGroup()

        # --- meridians: 8 great circles threading the +-UP poles ---
        for k in range(8):
            m = Circle(radius=R, stroke_color=VERDIGRIS,
                       stroke_width=1.0, stroke_opacity=0.55)
            m.rotate(PI / 2, axis=RIGHT)            # lift into XZ plane
            m.rotate(TAU * k / 8, axis=UP)          # fan around polar axis
            cage.add(m)

        # --- parallels: engraved circles stacked on the axis --------
        for deg in (24, 48, 66, 114, 132, 156):
            th = deg * DEGREES
            pr = R * np.sin(th)
            ph = R * np.cos(th)
            p = Circle(radius=pr, stroke_color=VERDIGRIS,
                       stroke_width=0.9, stroke_opacity=0.45)
            p.rotate(PI / 2, axis=RIGHT)            # lie horizontally
            p.shift(UP * ph)
            cage.add(p)

        eq = Circle(radius=R, stroke_color=OLD_GOLD,
                    stroke_width=1.6, stroke_opacity=0.65)
        eq.rotate(PI / 2, axis=RIGHT)
        cage.add(eq)
        return globe, cage

    def _act2_lone_pole(self):
        self.set_camera_orientation(phi=70 * DEGREES, theta=-70 * DEGREES,
                                    zoom=1.14)
        globe, cage = self._paper_globe()
        cap = self._cap("the heretical hypothesis: ONE pole, alone",
                        color=OXIDE)
        self.play(Create(globe), run_time=self.T_GLOBE * 0.42)
        self.play(Create(cage), run_time=self.T_GLOBE * 0.26)
        self.begin_ambient_camera_rotation(rate=-0.09)
        self.wait(self.T_GLOBE * 0.16)
        self.stop_ambient_camera_rotation()
        mark = Dot3D(point=UP * 1.30, radius=0.07, color=OXIDE)
        self.play(Create(mark), run_time=self.T_GLOBE * 0.16)
        self.wait(0.4)
        # NOTE: returns a 2-tuple on purpose -- construct() unpacks:
        #   self.globe, self.cage = self._act2_lone_pole()
        return VGroup(globe), VGroup(cage, mark)

    # ==================================================================
    # ACT 3 -- rays ESCAPE the skin (true-3D StreamLines, radial field)
    # ==================================================================
    def _monopole_rays(self):
        def radial(p):
            n = np.linalg.norm(p)
            return p / (n + 0.22)          # outward push, softened core

        return StreamLines(
            radial,
            x_range=[-3.0, 3.0, 1.0],
            y_range=[-3.0, 3.0, 1.0],
            z_range=[-3.0, 3.0, 1.0],
            three_dimensions=True,         # <-- the unused switch
            virtual_time=6.0,
            dt=0.05,
            max_anchors_per_line=80,
            padding=1.2,
            color=INDIGO,                  # single-colour bake (safe path)
            stroke_width=1.5,
            opacity=0.82,
        )

    def _restyle_rays(self, rays):
        tints = [OXIDE, INDIGO, VERDIGRIS]
        lines = list(rays)
        for i, ln in enumerate(lines):
            ln.set_stroke(tints[i % 3], width=1.8, opacity=0.88)

    def _act3_rays_escape(self):
        self.set_camera_orientation(phi=62 * DEGREES, theta=-118 * DEGREES,
                                    zoom=1.10)
        rays = self._monopole_rays()
        cap1 = self._cap("no return ticket: EVERY ray exits",
                         color=INDIGO, size=26)
        self.play(Create(rays), run_time=self.T_RAYS * 0.38)
        self._restyle_rays(rays)
        self.begin_ambient_camera_rotation(rate=0.11)
        self.wait(self.T_RAYS * 0.14)
        cap2 = self._cap(
            "\u222e B \u00b7 dA \u2260 0  \u2014 Gauss counts a SOURCE",
            color=OXIDE)
        self.remove(cap1)
        self.play(FadeIn(cap2), run_time=self.T_RAYS * 0.10)
        self.move_camera(phi=26 * DEGREES, theta=-150 * DEGREES,
                         zoom=1.62, run_time=self.T_RAYS * 0.24)
        self.wait(self.T_RAYS * 0.14)
        self.stop_ambient_camera_rotation()
        self.remove(cap2)
        return rays

    # ==================================================================
    # ACT 4 -- dive to the singularity; one solid flux tube; Dirac plate
    # ==================================================================
    def _flux_tube(self, axis, R_globe=1.28):
        """Radial tube from solids: cube plinth -> cylinder -> cone tip,
        authored along local +Z then aimed along `axis`."""
        plinth = _solid(VERDIGRIS, Cube, side_length=0.30)
        shaft = _solid(OXIDE, Cylinder,
                       radius=0.115, height=1.55,
                       direction=OUT, resolution=(12, 26))
        shaft.shift(OUT * 0.92)                       # 0.145 .. 1.695
        head = _solid(OLD_GOLD, Cone,
                      base_radius=0.20, height=0.46,
                      direction=OUT, resolution=(12, 26))
        head.shift(OUT * 1.69 + OUT * 0.23)           # base meets shaft top
        tube = VGroup(plinth, shaft, head)
        zhat = np.array([0.0, 0.0, 1.0])
        ax = np.asarray(axis, dtype=float)
        ax /= np.linalg.norm(ax)
        rot_ax = np.cross(zhat, ax)
        nrm = np.linalg.norm(rot_ax)
        if nrm > 1e-9:
            rot_ax /= nrm
            ang = np.arccos(np.clip(np.dot(zhat, ax), -1.0, 1.0))
            tube.rotate(ang, axis=rot_ax)
        tube.shift(ax * (R_globe - 0.02))             # plinth kisses skin
        return tube

    def _dirac_plate(self):
        plate = Text("g \u00b7 \u03a9_cap  =  n h          n \u2208 \u2124",
                     weight="BOLD", font_size=40, color=INK, font="Georgia")
        note = Text("flux tubes must tile the sphere WHOLE \u2014 "
                    "electric charge is quantized",
                    slant="ITALIC", font_size=25, color=VERDIGRIS,
                    font="Georgia")
        board = VGroup(plate, note).arrange(DOWN, buff=0.26)
        board.to_edge(RIGHT, buff=0.5)
        self.add_fixed_in_frame_mobjects(board)
        return board

    def _act4_dirac_quantization(self):
        # ---- dive through the cage to the singularity --------------
        self.move_camera(phi=8 * DEGREES, theta=-168 * DEGREES,
                         zoom=3.0, run_time=self.T_TUBE * 0.16)
        flash = Dot3D(point=ORIGIN, radius=0.10, color=OXIDE)
        self.play(Create(flash), run_time=self.T_TUBE * 0.06)
        # ---- recoil -------------------------------------------------
        self.move_camera(phi=58 * DEGREES, theta=-128 * DEGREES,
                         zoom=1.02, run_time=self.T_TUBE * 0.13)
        self.play(FadeOut(flash), run_time=self.T_TUBE * 0.04)

        # ---- marked polar cap + THE tube ----------------------------
        th0 = 52 * DEGREES
        axis = np.array([np.sin(th0), 0.0, np.cos(th0)])   # +Z-polar family
        caprings = VGroup(
            Circle(radius=0.52, stroke_color=OLD_GOLD, stroke_width=6.0),
            Circle(radius=0.40, stroke_color=OXIDE, stroke_width=3.5),
        ).rotate(PI / 2, axis=RIGHT)                       # plane normal +Y?
        # aim ring normals along `axis`
        zhat = np.array([0.0, 0.0, 1.0])
        rot_ax = np.cross(zhat, axis)
        rot_ax /= (np.linalg.norm(rot_ax) + 1e-12)
        ang = np.arccos(np.clip(np.dot(zhat, axis), -1.0, 1.0))
        caprings.rotate(ang, axis=rot_ax)
        caprings.move_to(axis * 1.29)

        tube = self._flux_tube(axis)

        capT = self._cap("ONE flux tube \u03a6\u2080 = 2h/e, made solid",
                         color=OLD_GOLD, size=26)
        self.play(Create(caprings), run_time=self.T_TUBE * 0.09)
        self.play(Create(tube), run_time=self.T_TUBE * 0.22)

        board = self._dirac_plate()
        self.play(Write(plate_group := board[0]),
                  run_time=self.T_TUBE * 0.14)
        self.play(FadeIn(note_lab := board[1]),
                  run_time=self.T_TUBE * 0.05)
        self.begin_ambient_camera_rotation(rate=0.10)
        self.wait(self.T_TUBE * 0.12)
        self.stop_ambient_camera_rotation()
        self.remove(capT, board)
        return VGroup(caprings, tube)

    # ==================================================================
    # EPILOGUE
    # ==================================================================
    def _epilogue(self):
        final = Text(
            "no lone pole has ever been seen \u2014 yet one "
            "would explain charge itself.",
            slant="ITALIC", font_size=29, color=INK, font="Georgia")
        final.to_edge(UP, buff=0.5)
        self.add_fixed_in_frame_mobjects(final)
        self.move_camera(phi=78 * DEGREES, theta=-205 * DEGREES,
                         zoom=0.84, run_time=self.T_END * 0.58)
        self.begin_ambient_camera_rotation(rate=0.045)
        self.wait(self.T_END * 0.28)
        self.stop_ambient_camera_rotation()
        group_out = VGroup(self.globe, self.cage, self.rays,
                           self.tube_stage, final)
        self.play(FadeOut(group_out), run_time=0.9)


# ----------------------------------------------------------------------
# UNITS NOTE: distances are scene units. The paper sphere is the Gaussian
# pillbox; the solid tube carries one flux quantum Phi_0 = 2h/e (in SI via
# g_dirac = h/e pairing), hence Omega_cap must close WHOLE: Omega = n h / g.
# ----------------------------------------------------------------------
