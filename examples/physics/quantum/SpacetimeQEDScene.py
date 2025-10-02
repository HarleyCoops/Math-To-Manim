"""
SpacetimeQEDScene.py
Manim Community v0.19+

Render with (high‑quality, 60 fps example):
    manim -pqh SpacetimeQEDScene.py SpacetimeQEDScene
"""

from __future__ import annotations
from random import uniform, seed
from math import sin, cos, pi

from manim import *

################################################################################
# GLOBAL STYLE CONSTANTS
################################################################################

STAR_COLOR       = GRAY_C
STAR_COUNT       = 2_000                # sprinkle the cosmos!
STAR_SCATTER_RAD = 50

TITLE_GRADIENT = (BLUE_B, TEAL_A)
METRIC_COLORS = {"-c^2 dt^2": RED_B,
                 "+ dx^2":    GREEN_B,
                 "+ dy^2":    YELLOW_B,
                 "+ dz^2":    MAROON_B}

SPINOR_COLOR   = ORANGE
DERIV_COLOR    = GREEN
GAMMA_COLOR    = TEAL
TENSOR_COLOR   = GOLD

E_COLOR        = RED_B
B_COLOR        = BLUE_B
PHOTON_COLOR   = YELLOW_A
ELECTRON_COLOR = BLUE_E


################################################################################
# HELPER OBJECTS
################################################################################

def make_starfield(n: int = STAR_COUNT,
                   radius: float = STAR_SCATTER_RAD) -> VGroup:
    """Return a randomly‑scattered dot cloud that surrounds the origin."""
    seed(42)
    dots = VGroup()
    for _ in range(n):
        x, y, z = (uniform(-1, 1) * radius for _ in range(3))
        dot = Dot3D(point=[x, y, z], radius=0.02, color=STAR_COLOR, stroke_width=0)
        dot.set_opacity(uniform(0.4, 1))
        dots.add(dot)
    return dots


def wavy_photon(start: np.ndarray,
                end: np.ndarray,
                amplitude: float = 0.5,
                waves: int = 14,
                points_per_wave: int = 10,
                color=PHOTON_COLOR) -> VMobject:
    """Create a wavy line (≈ photon propagator) between two 3‑space points."""
    total_points = waves * points_per_wave + 1
    points = []
    for i in range(total_points):
        alpha = i / (total_points - 1)
        pos   = interpolate(start, end, alpha)
        perp  = UP if i % 2 == 0 else RIGHT
        pos  += perp * amplitude * sin(alpha * waves * 2 * pi)
        points.append(pos)
    return VMobject().set_points_as_corners(points).set_stroke(color, 2)


################################################################################
# MAIN SCENE
################################################################################

class SpacetimeQEDScene(ThreeDScene):
    def construct(self):
        ############### COSMIC OPENING #########################################
        self.set_camera_orientation(phi=75 * DEGREES, theta=-45 * DEGREES)
        stars = make_starfield()
        self.play(FadeIn(stars, run_time=4))

        title = (Text("Quantum Field Theory:",
                      gradient=TITLE_GRADIENT,
                      weight=BOLD, font_size=64)
                 .next_to(ORIGIN, UP*2))
        subtitle = (Text("A Journey into the Electromagnetic Interaction",
                         gradient=TITLE_GRADIENT, font_size=36)
                    .next_to(title, DOWN*0.5))
        big_title = VGroup(title, subtitle)
        self.play(Write(big_title), run_time=3)
        self.wait()

        # shrink & move to upper left
        corner_target = big_title.copy().scale(0.4).to_corner(UL)
        self.play(Transform(big_title, corner_target), run_time=2)

        ############### 3‑D AXIS & MINKOWSKI FRAME #############################
        axes = ThreeDAxes(x_range=[-4, 4], y_range=[-4, 4], z_range=[-4, 4],
                          tips=False, stroke_color=GRAY_D)
        self.play(Create(axes), run_time=3)

        # Light‑cone (double cone made of lines)
        lightcone = VGroup()
        for angle in range(0, 360, 15):
            angle_rad = angle * DEGREES
            line = Line3D(
                start=[0, 0, 0],
                end=[4 * cos(angle_rad), 4 * sin(angle_rad), 4],
                stroke_opacity=0.4
            )
            line2 = Line3D(
                start=[0, 0, 0],
                end=[4 * cos(angle_rad), 4 * sin(angle_rad), -4],
                stroke_opacity=0.4
            )
            lightcone.add(line, line2)

        wireframe = VGroup(axes, lightcone)
        self.play(FadeIn(lightcone, lag_ratio=0.1), run_time=2)
        self.play(Rotate(wireframe, angle=TAU, axis=OUT, run_time=10,
                         rate_func=linear))

        # Metric equation with colored terms
        metric_tex = MathTex(r"\mathrm{d}s^2",
                             "=",
                             r"-c^2\,\mathrm{d}t^2",
                             "+",
                             r"\mathrm{d}x^2",
                             "+",
                             r"\mathrm{d}y^2",
                             "+",
                             r"\mathrm{d}z^2",
                             font_size=48)
        for tex, color in METRIC_COLORS.items():
            metric_tex.set_color_by_tex(tex, color)
        metric_tex.to_corner(UR)
        self.play(Write(metric_tex))
        self.wait(1)

        ############### ZOOM TO ORIGIN – PLANE WAVES ###########################
        self.move_camera(phi=60*DEGREES, theta=-90*DEGREES, zoom=1.4,
                         run_time=2)

        # Electric & magnetic fields (parametric sine waves)
        k = 2 * pi / 3
        E_wave = ParametricFunction(
            lambda t: np.array([t, 0.8 * sin(k*t), 0]),
            t_range=[-7, 7],
            color=E_COLOR, stroke_width=4
        )
        B_wave = ParametricFunction(
            lambda t: np.array([t, 0, 0.8 * sin(k*t + PI/2)]),
            t_range=[-7, 7],
            color=B_COLOR, stroke_width=4
        )
        waves = VGroup(E_wave, B_wave).shift(OUT*1.5)
        self.play(Create(waves, run_time=4))
        self.wait()

        # Labels & 3‑D propagation arrow
        E_label = MathTex(r"\vec{E}", color=E_COLOR).next_to(E_wave, UP)
        B_label = MathTex(r"\vec{B}", color=B_COLOR).next_to(B_wave, RIGHT)
        prop_arrow = Arrow3D(start=[-5, 0, 0], end=[5, 0, 0],
                             color=WHITE).set_opacity(0.6)
        self.play(Write(E_label), Write(B_label), GrowArrow(prop_arrow))
        self.wait()

        ############### MAXWELL EQNS -> RELATIVISTIC FORM ######################
        maxwell_classical = MathTex(
            r"\nabla \cdot \vec{E} = \frac{\rho}{\varepsilon_0}",
            r"\quad \nabla \times \vec{B} - \frac{1}{c^2}\frac{\partial \vec{E}}{\partial t} = \mu_0 \vec{J}",
            font_size=36
        ).to_edge(DOWN)
        maxwell_rel = MathTex(
            r"\partial_\mu F^{\mu \nu} = \mu_0 J^\nu",
            font_size=42
        ).move_to(maxwell_classical)

        self.play(Write(maxwell_classical))
        self.wait()
        self.play(TransformMatchingTex(maxwell_classical, maxwell_rel),
                  run_time=3)
        self.wait()

        ############### QED LAGRANGIAN ########################################
        lagrangian = MathTex(
            r"\mathcal{L}_{\text{QED}} =",
            r"\bar{\psi}", r"(i \gamma^\mu", r"D_\mu", r" - m)", r"\psi",
            r"- \tfrac{1}{4}", r"F_{\mu\nu}F^{\mu\nu}",
            font_size=42
        )
        lagrangian.set_color_by_tex(r"\bar{\psi}", SPINOR_COLOR)
        lagrangian.set_color_by_tex(r"\psi", SPINOR_COLOR)
        lagrangian.set_color_by_tex(r"D_\mu", DERIV_COLOR)
        lagrangian.set_color_by_tex(r"\gamma^\mu", GAMMA_COLOR)
        lagrangian.set_color_by_tex(r"F_{\mu\nu}", TENSOR_COLOR)
        lagrangian.set_color_by_tex(r"F^{\mu\nu}", TENSOR_COLOR)

        plane = Rectangle(width=10, height=3,
                          stroke_opacity=0,
                          fill_opacity=0.2,
                          fill_color=BLACK).shift(OUT*2.5)
        lagrangian.move_to(plane.get_center())

        self.play(FadeIn(plane), Write(lagrangian), run_time=3)
        # gentle pulsing
        self.add_foreground_mobjects(lagrangian)
        self.play(lagrangian.animate.scale(1.05), rate_func=there_and_back,
                  run_time=2)

        ############### GAUGE TRANSFORMATION SIZZLE ###########################
        phase = MathTex(r"e^{i\alpha(x)}", font_size=36).next_to(lagrangian,
                                                                 UP)
        self.play(
            lagrangian[1:6].animate.shift(LEFT*0.2).set_color(SPINOR_COLOR),
            FadeIn(phase), run_time=1.5
        )
        self.play(FadeOut(phase))

        ############### FEYNMAN DIAGRAM #######################################
        self.move_camera(phi=75*DEGREES, theta=-60*DEGREES, zoom=1.6,
                         run_time=2)
        # blank slate
        self.play(*[FadeOut(mob) for mob in self.mobjects if mob != stars],
                  run_time=1)

        # electron lines
        e_left  = Line3D([-4,  0, 0], [0, 0, 0], color=ELECTRON_COLOR,
                         stroke_width=4)
        e_right = Line3D([ 4,  0, 0], [0, 0, 0], color=ELECTRON_COLOR,
                         stroke_width=4)
        photon  = wavy_photon([-0.1, 0, 0], [0.1, 0, 2], amplitude=0.3)

        e_label_L = MathTex(r"e^{-}", color=ELECTRON_COLOR,
                            font_size=36).next_to(e_left, DOWN)
        e_label_R = MathTex(r"e^{-}", color=ELECTRON_COLOR,
                            font_size=36).next_to(e_right, DOWN)
        gamma_lab = MathTex(r"\gamma", color=PHOTON_COLOR,
                            font_size=36).next_to(photon, RIGHT)

        diagram = VGroup(e_left, e_right, photon,
                         e_label_L, e_label_R, gamma_lab)
        diagram.shift(OUT*2)
        self.play(Create(diagram, lag_ratio=0.2), run_time=3)

        # coupling constant animation
        alpha_num = MathTex(r"\alpha \approx \tfrac{1}{137}",
                            font_size=48, color=WHITE).to_corner(UL)
        alpha_full = MathTex(
            r"\alpha = \dfrac{e^2}{4\pi \varepsilon_0 \hbar c}",
            font_size=44, color=WHITE
        ).move_to(alpha_num)

        self.play(Write(alpha_num))
        self.play(TransformMatchingTex(alpha_num, alpha_full), run_time=2)

        ############### RUNNING COUPLING GRAPH ################################
        self.play(*[mob.animate.shift(LEFT*3) for mob in diagram],
                  alpha_full.animate.shift(LEFT*3), run_time=1)

        axes2d = Axes(
            x_range=[0, 12, 2],
            y_range=[0, 1, 0.2],
            x_length=6,
            y_length=4,
            axis_config={"include_tip": False}
        ).shift(RIGHT*3 + DOWN*1 + OUT*2)
        axes2d_labels = axes2d.get_axis_labels(
            Tex("Energy Scale"), Tex("Coupling\nStrength")
        )
        running_curve = axes2d.plot(
            lambda x: 0.0073 + 0.0015*x**0.6,
            x_range=[0, 10],
            use_smoothing=True,
            color=PHOTON_COLOR
        )
        self.play(Create(axes2d), Write(axes2d_labels))
        self.play(Create(running_curve), run_time=3)
        self.wait(1)

        ############### GRAND COLLAGE & OUTRO #################################
        collage = VGroup(diagram, axes2d, axes2d_labels, running_curve,
                         alpha_full)
        summary = (Text("QED: Unifying Light and Matter Through Gauge Theory",
                        font_size=36, gradient=TITLE_GRADIENT)
                   .shift(UP*3 + OUT*2))
        self.play(FadeIn(summary, shift=IN))
        self.wait(2)

        # pull camera back & fade elements
        self.move_camera(phi=75*DEGREES, theta=-45*DEGREES, zoom=0.8,
                         run_time=4)
        self.play(*(FadeOut(mob) for mob in collage), FadeOut(summary),
                  run_time=3)

        finis = (Text("Finis", font_size=48, weight=BOLD,
                      gradient=(WHITE, GRAY_B))
                 .move_to(ORIGIN + OUT*2))
        self.play(Write(finis, run_time=2))
        self.play(FadeOut(finis), FadeOut(stars, run_time=4))
