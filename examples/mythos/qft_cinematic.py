"""QFT, the Mythos cut — a cinematic retelling of the QED journey.

The original ``QED.py`` parked equations in corners under a static camera.
This film uses the Mythos grammar instead: plain-language headlines before
symbols, camera flights into the exact term being explained, pull-backs to
restore context, and true-3D set pieces for fields and histories.

Render:
    manim -qm examples/mythos/qft_cinematic.py QFTCinematicJourney
    manim -qh --fps 60 examples/mythos/qft_cinematic.py QFTCinematicJourney
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from manim import *

# Import the Mythos visual grammar (repo-root import with fallback).
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from mythos.cinematography import (  # noqa: E402
    CORAL, EMBER, FOG, GOLD, INK, IVORY, OLIVE, SKY,
    caption, clear_caption, glow, glow_dot, headline, orbit,
    photon_path, pull_back, return_to_stage, spotlight, stage, starfield,
    term_tour, tilt_to_3d, unspotlight, zoom_to,
)


class QFTCinematicJourney(ThreeDScene):
    """~2.5 minute cinematic pass through QED."""

    def construct(self):
        stage(self)

        self.act_prologue_vacuum()
        self.act_everything_is_a_field()
        self.act_light_is_a_field()
        self.act_one_equation()
        self.act_symmetry_writes_the_rules()
        self.act_the_vertex()
        self.act_sum_over_histories()
        self.act_finale()

    # ------------------------------------------------------------------ #
    # Prologue — the vacuum                                               #
    # ------------------------------------------------------------------ #

    def act_prologue_vacuum(self):
        stars = starfield(n=160)
        stars.set_opacity(0)
        self.add(stars)
        self.play(LaggedStart(*[s.animate.set_opacity(0.7 * np.random.uniform(0.4, 1.0))
                                for s in stars], lag_ratio=0.012), run_time=2.4)

        headline(self, "The vacuum is not empty.",
                 sub="Quantum field theory begins where nothing is something.")

        # Slow push into the dark while a faint shimmer crosses the void.
        shimmer = photon_path([-7, -2.5, 0], [7, 1.5, 0], color=EMBER, waves=14, amp=0.08,
                              stroke_width=2.0).set_opacity(0.35)
        self.play(Create(shimmer), run_time=2.0)
        self.move_camera(zoom=1.35, run_time=2.2,
                         added_anims=[stars.animate.set_opacity(0.25)])
        caption(self, "Empty space hums with fields — invisible, everywhere, waiting.",
                hold=1.2)
        self.play(FadeOut(shimmer), run_time=0.8)
        clear_caption(self)
        self.play(stars.animate.set_opacity(0.12), run_time=0.8)
        self.stars = stars

    # ------------------------------------------------------------------ #
    # Act I — everything is a field                                       #
    # ------------------------------------------------------------------ #

    def act_everything_is_a_field(self):
        headline(self, "Everything is a field.",
                 sub="The electron is not a marble. It is a ripple.")

        axes = ThreeDAxes(x_range=[-4, 4], y_range=[-4, 4], z_range=[-2, 2],
                          x_length=8, y_length=8, z_length=3)
        axes.set_stroke(FOG, opacity=0.35)
        t = ValueTracker(0.0)

        def field_surface():
            def f(u, v):
                r = np.sqrt(u * u + v * v) + 1e-6
                z = 0.55 * np.sin(2.2 * r - 2.6 * t.get_value()) * np.exp(-0.32 * r)
                return axes.c2p(u, v, z)
            s = Surface(f, u_range=[-4, 4], v_range=[-4, 4], resolution=(26, 26),
                        fill_opacity=0.42, stroke_width=0.6,
                        checkerboard_colors=[CORAL, EMBER])
            s.set_fill_by_value(axes=axes, colorscale=[(EMBER, -0.5), (INK, 0.0), (CORAL, 0.5)], axis=2)
            s.set_stroke(CORAL, opacity=0.5)
            return s

        field = always_redraw(field_surface)

        tilt_to_3d(self, phi=62 * DEGREES, theta=-50 * DEGREES, zoom=0.85)
        self.play(FadeIn(axes), FadeIn(field), run_time=1.6)
        caption(self, "A field assigns a value to every point of spacetime.")
        self.play(t.animate.set_value(2.4), run_time=3.0, rate_func=linear)

        caption(self, "Strike the field, and the ripple that spreads is what we call a particle.")
        self.begin_ambient_camera_rotation(rate=0.05)
        self.play(t.animate.set_value(5.6), run_time=3.6, rate_func=linear)
        self.stop_ambient_camera_rotation()

        # Zoom INTO the crest: the ripple is the electron.
        electron = glow_dot(axes.c2p(0, 0, 0.55), color=CORAL, radius=0.06)
        self.move_camera(phi=48 * DEGREES, theta=-60 * DEGREES, zoom=1.9,
                         frame_center=axes.c2p(0, 0, 0.4), run_time=2.2)
        self.play(FadeIn(electron, scale=0.4), run_time=0.9)
        psi_label = MathTex(r"\psi(x,t)", color=CORAL, font_size=42)
        psi_label.rotate(75 * DEGREES, axis=RIGHT)
        psi_label.next_to(electron, OUT + RIGHT, buff=0.3)
        self.play(Write(psi_label), run_time=0.8)
        caption(self, "This excitation — written ψ — is the electron.", color=CORAL, hold=1.3)

        self.play(FadeOut(field), FadeOut(axes), FadeOut(electron), FadeOut(psi_label),
                  run_time=1.2)
        clear_caption(self)
        return_to_stage(self)

    # ------------------------------------------------------------------ #
    # Act II — light is a field too                                       #
    # ------------------------------------------------------------------ #

    def act_light_is_a_field(self):
        headline(self, "Light is a field too.",
                 sub="Maxwell wrote its choreography in 1865.")

        axes = ThreeDAxes(x_range=[-5, 5], y_range=[-2, 2], z_range=[-2, 2],
                          x_length=10, y_length=4, z_length=4)
        axes.set_stroke(FOG, opacity=0.3)

        k = 1.6
        e_wave = ParametricFunction(
            lambda s: axes.c2p(s, 0.9 * np.sin(k * s), 0),
            t_range=[-5, 5], color=CORAL, stroke_width=4)
        b_wave = ParametricFunction(
            lambda s: axes.c2p(s, 0, 0.9 * np.sin(k * s)),
            t_range=[-5, 5], color=SKY, stroke_width=4)

        e_label = MathTex(r"\vec{E}", color=CORAL, font_size=40).move_to(axes.c2p(2.2, 1.35, 0))
        b_label = MathTex(r"\vec{B}", color=SKY, font_size=40).move_to(axes.c2p(3.4, 0, 1.3))
        b_label.rotate(90 * DEGREES, axis=RIGHT)

        tilt_to_3d(self, phi=70 * DEGREES, theta=-35 * DEGREES, zoom=0.95)
        self.play(FadeIn(axes), run_time=0.8)
        caption(self, "An electric wave and a magnetic wave, locked at right angles…")
        self.play(Create(e_wave), Write(e_label), run_time=1.8)
        self.play(Create(b_wave), Write(b_label), run_time=1.8)

        caption(self, "…each regenerating the other. That self-sustaining braid is light.")
        orbit(self, rate=0.09, duration=3.2)

        # Sweep along the propagation axis — riding the beam.
        self.move_camera(theta=-12 * DEGREES, zoom=1.5,
                         frame_center=axes.c2p(2.5, 0, 0), run_time=2.4)
        self.wait(0.5)

        wave_group = VGroup(axes, e_wave, b_wave, e_label, b_label)
        clear_caption(self)
        return_to_stage(self)

        # Maxwell, then compression into F_munu.
        maxwell = MathTex(
            r"\nabla\!\cdot\!\vec{E}=\tfrac{\rho}{\varepsilon_0}", r"\quad",
            r"\nabla\!\cdot\!\vec{B}=0", r"\\",
            r"\nabla\!\times\!\vec{E}=-\partial_t\vec{B}", r"\quad",
            r"\nabla\!\times\!\vec{B}=\mu_0\vec{J}+\mu_0\varepsilon_0\,\partial_t\vec{E}",
            font_size=44, color=IVORY,
        )
        self.play(FadeOut(wave_group, run_time=0.8), FadeIn(maxwell, shift=UP * 0.3, run_time=1.2))
        caption(self, "Four equations. Every circuit, every sunbeam, every radio song.", hold=1.4)

        compressed = MathTex(r"F_{\mu\nu}", r"=\partial_\mu A_\nu - \partial_\nu A_\mu",
                             font_size=64, color=SKY)
        caption(self, "Relativity folds all four into a single object — the field tensor.")
        self.play(ReplacementTransform(maxwell, compressed), run_time=1.8)
        zoom_to(self, compressed[0], zoom=2.6)
        self.wait(1.0)
        pull_back(self)
        self.play(FadeOut(compressed), run_time=0.7)
        clear_caption(self)

    # ------------------------------------------------------------------ #
    # Act III — one equation                                              #
    # ------------------------------------------------------------------ #

    def act_one_equation(self):
        headline(self, "One line describes light and matter.",
                 sub="The Lagrangian of quantum electrodynamics.")

        L = MathTex(
            r"\mathcal{L}_{\mathrm{QED}}", "=",
            r"\bar{\psi}", r"\left(i\gamma^\mu D_\mu - m\right)", r"\psi",
            "-", r"\tfrac{1}{4}", r"F_{\mu\nu}F^{\mu\nu}",
            font_size=58, color=IVORY,
        )
        underglow = glow(L, color=EMBER, layers=4, max_width=10, opacity=0.10)
        self.play(FadeIn(underglow), Write(L), run_time=2.4)
        caption(self, "Read it like a sentence. The camera will translate.", hold=1.0)

        term_tour(self, L, stops=[
            dict(part=VGroup(L[2], L[3], L[4]), color=CORAL, zoom=2.0, hold=1.6,
                 caption="Matter: the electron field ψ, carrying energy, spin, and mass m."),
            dict(part=L[3], color=OLIVE, zoom=2.6, hold=1.6,
                 caption="The Dirac engine: how ψ moves through spacetime — i γ^μ D_μ − m."),
            dict(part=VGroup(L[6], L[7]), color=SKY, zoom=2.2, hold=1.6,
                 caption="Light: the electromagnetic field, free to ripple on its own."),
        ])

        # The hidden interaction: expand D_mu.
        caption(self, "But one symbol is hiding something.", color=GOLD)
        D_part = L[3]
        frame = spotlight(self, L, D_part, color=GOLD)
        zoom_to(self, D_part, zoom=2.8)
        self.wait(0.8)
        pull_back(self, zoom=1.0)
        unspotlight(self, L, frame)

        expansion = MathTex(r"D_\mu", "=", r"\partial_\mu", "+", r"i e", r"A_\mu",
                            font_size=54, color=IVORY).next_to(L, DOWN, buff=0.9)
        self.play(L.animate.shift(UP * 0.6), FadeIn(expansion, shift=UP * 0.3), run_time=1.4)

        coupling = VGroup(expansion[4], expansion[5])
        frame2 = spotlight(self, expansion, coupling, color=GOLD)
        zoom_to(self, coupling, zoom=3.0)
        caption(self, "Here. e couples the electron to the photon field A.", color=GOLD, hold=1.6)
        caption(self, "Every spark, every photosynthesis, every sunset — this one term.",
                color=GOLD, hold=1.8)
        pull_back(self)
        unspotlight(self, expansion, frame2)

        self.play(FadeOut(expansion), FadeOut(underglow),
                  L.animate.move_to(ORIGIN).scale(0.85), run_time=1.0)
        self.qed_lagrangian = L
        clear_caption(self)
        self.play(L.animate.scale(0.45).to_corner(UL).set_opacity(0.55), run_time=1.0)

    # ------------------------------------------------------------------ #
    # Act IV — gauge symmetry                                             #
    # ------------------------------------------------------------------ #

    def act_symmetry_writes_the_rules(self):
        headline(self, "Demand symmetry, and light must exist.",
                 sub="Local gauge invariance is not decoration. It is the reason.")

        # A lattice of phase dials: U(1) phases at points of space.
        dials = VGroup()
        rng = np.random.default_rng(3)
        for x in np.linspace(-4.5, 4.5, 6):
            for y in np.linspace(-2.2, 2.2, 4):
                ring = Circle(radius=0.34, color=FOG, stroke_opacity=0.5, stroke_width=2)
                hand = Line(ORIGIN, 0.30 * RIGHT, color=CORAL, stroke_width=3.5)
                dial = VGroup(ring, hand).move_to([x, y, 0])
                dial.phase = float(rng.uniform(0, TAU))
                hand.rotate(dial.phase, about_point=dial.get_center())
                dials.add(dial)

        self.play(LaggedStart(*[FadeIn(d, scale=0.6) for d in dials], lag_ratio=0.04),
                  run_time=2.0)
        caption(self, "Attach a phase dial to every point of space. ψ → e^{iα} ψ.")

        # Global rotation: physics unchanged.
        self.play(*[Rotate(d[1], angle=PI / 2, about_point=d.get_center()) for d in dials],
                  run_time=1.6)
        caption(self, "Turn every dial together — nothing observable changes.", hold=1.0)

        # Local rotation: each point its own angle.
        caption(self, "Now turn each dial by a different amount at each point…", color=GOLD)
        self.play(*[Rotate(d[1],
                           angle=1.2 * np.sin(1.3 * d.get_center()[0]) + 0.9 * d.get_center()[1] * 0.4,
                           about_point=d.get_center())
                    for d in dials], run_time=2.0)

        # The compensating field sweeps through.
        a_field = photon_path([-6.5, 0, 0], [6.5, 0, 0], color=SKY, waves=7, amp=0.5,
                              stroke_width=5)
        a_halo = glow(a_field, color=SKY, layers=4, max_width=14, opacity=0.12)
        gauge_law = MathTex(r"A_\mu \;\to\; A_\mu - \tfrac{1}{e}\,\partial_\mu \alpha",
                            font_size=46, color=SKY).to_edge(UP, buff=1.0)
        caption(self, "…and the equations only survive if a new field absorbs the mismatch.",
                color=SKY)
        self.play(Create(a_field), FadeIn(a_halo), Write(gauge_law), run_time=2.2)
        zoom_to(self, a_field, zoom=1.6)
        caption(self, "That field is the photon. Light is the price of local symmetry.",
                color=SKY, hold=2.0)
        pull_back(self)

        self.play(FadeOut(dials), FadeOut(a_field), FadeOut(a_halo), FadeOut(gauge_law),
                  run_time=1.0)
        clear_caption(self)

    # ------------------------------------------------------------------ #
    # Act V — the vertex                                                  #
    # ------------------------------------------------------------------ #

    def act_the_vertex(self):
        headline(self, "All of electromagnetism, one vertex.",
                 sub="Feynman's shorthand for every conversation between light and matter.")

        v = np.array([0.0, 0.0, 0.0])
        e_in = Line([-3.4, -2.2, 0], v, color=CORAL, stroke_width=4.5)
        e_out = Line(v, [-3.4, 2.2, 0], color=CORAL, stroke_width=4.5)
        ph = photon_path(v, [3.8, 0.15, 0], color=SKY, waves=6.5, amp=0.22, stroke_width=4.5)
        for line in (e_in, e_out):
            line.add_tip(tip_length=0.22, tip_width=0.18)
        vert = glow_dot(v, color=GOLD, radius=0.07)

        lbl_in = MathTex(r"e^-", color=CORAL, font_size=40).next_to(e_in.get_start(), DL, buff=0.15)
        lbl_out = MathTex(r"e^-", color=CORAL, font_size=40).next_to(e_out.get_end(), UL, buff=0.15)
        lbl_ph = MathTex(r"\gamma", color=SKY, font_size=44).next_to(ph.get_end(), RIGHT, buff=0.2)

        caption(self, "An electron flies in, shrugs off a photon, and carries on.")
        self.play(Create(e_in), run_time=1.0)
        self.play(FadeIn(vert, scale=0.4), Create(e_out), Create(ph),
                  Write(lbl_in), Write(lbl_out), Write(lbl_ph), run_time=2.0)

        # Fly into the vertex: where the coupling lives.
        zoom_to(self, vert, zoom=3.0)
        coupling = MathTex(r"-ie\gamma^\mu", color=GOLD, font_size=34)
        coupling.next_to(vert, UR, buff=0.18)
        self.play(Write(coupling), run_time=0.9)
        caption(self, "The vertex carries the same e from the Lagrangian. Symbols become events.",
                color=GOLD, hold=1.6)
        pull_back(self)

        # The strength of it all: alpha.
        alpha_value = DecimalNumber(0, num_decimal_places=8, font_size=54, color=IVORY)
        alpha_eq = VGroup(
            MathTex(r"\alpha = \frac{e^2}{4\pi\varepsilon_0\hbar c} \;=\;",
                    font_size=54, color=IVORY),
            alpha_value,
        ).arrange(RIGHT, buff=0.25).to_edge(DOWN, buff=1.6)
        approx = MathTex(r"\approx \tfrac{1}{137}", font_size=54, color=GOLD)
        approx.next_to(alpha_eq, RIGHT, buff=0.3)

        caption(self, "Nature turned the dial to one number — the fine-structure constant.")
        self.play(FadeIn(alpha_eq, shift=UP * 0.3), run_time=0.9)
        self.play(ChangeDecimalToValue(alpha_value, 0.00729735), run_time=2.2)
        self.play(Write(approx), run_time=0.8)
        zoom_to(self, VGroup(alpha_value, approx), zoom=2.2)
        caption(self, "Slightly different, and stars, chemistry, and we would not be.",
                color=GOLD, hold=1.8)
        pull_back(self)

        self.play(*[FadeOut(m) for m in [e_in, e_out, ph, vert, lbl_in, lbl_out, lbl_ph,
                                         coupling, alpha_eq, approx]], run_time=1.0)
        clear_caption(self)

    # ------------------------------------------------------------------ #
    # Act VI — sum over histories                                         #
    # ------------------------------------------------------------------ #

    def act_sum_over_histories(self):
        headline(self, "Reality sums over every possible path.",
                 sub="Feynman's deepest idea, drawn rather than derived.")

        A = np.array([-4.6, -1.4, 0.0])
        B = np.array([4.6, 1.2, 0.0])
        a_dot = glow_dot(A, color=CORAL, radius=0.06)
        b_dot = glow_dot(B, color=CORAL, radius=0.06)

        rng = np.random.default_rng(11)
        paths = VGroup()
        for i in range(11):
            c1 = A + np.array([3.0, rng.uniform(-3.4, 3.6), 0.0])
            c2 = B + np.array([-3.0, rng.uniform(-3.6, 3.4), 0.0])
            p = CubicBezier(A, c1, c2, B)
            p.set_stroke(interpolate_color(ManimColor(SKY), ManimColor(EMBER), i / 10),
                         width=2.2, opacity=0.55)
            paths.add(p)
        classical = Line(A, B).set_stroke(GOLD, width=5)

        self.play(FadeIn(a_dot), FadeIn(b_dot), run_time=0.7)
        caption(self, "To travel from here to there, a quantum particle tries everything.")
        self.play(LaggedStart(*[Create(p) for p in paths], lag_ratio=0.12), run_time=3.2)

        amplitude = MathTex(r"\mathcal{A} \;=\; \sum_{\text{paths}} e^{\,iS[\text{path}]/\hbar}",
                            font_size=48, color=IVORY).to_edge(UP, buff=0.9)
        self.play(Write(amplitude), run_time=1.4)
        caption(self, "Each path contributes a spinning arrow. Most cancel their neighbors…")
        self.play(paths.animate.set_opacity(0.12), run_time=1.8)
        caption(self, "…except where the action is stationary. The straight line survives.",
                color=GOLD)
        self.play(Create(classical), run_time=1.4)
        zoom_to(self, classical, zoom=1.7)
        self.wait(0.8)
        pull_back(self)

        self.play(FadeOut(paths), FadeOut(classical), FadeOut(a_dot), FadeOut(b_dot),
                  FadeOut(amplitude), run_time=1.0)
        clear_caption(self)

    # ------------------------------------------------------------------ #
    # Finale                                                              #
    # ------------------------------------------------------------------ #

    def act_finale(self):
        L = getattr(self, "qed_lagrangian", None)
        if L is not None:
            self.play(L.animate.move_to(ORIGIN).scale(2.0).set_opacity(1.0), run_time=1.6)

        headline(self, "The most precisely tested theory in physics.",
                 sub="Theory and experiment agree to twelve decimal places.")

        g_label = Text("electron g-factor", font="Lora", slant="ITALIC",
                       font_size=30, color=FOG)
        g_value = MathTex(r"g/2 = 1.001\,159\,652\,180\ldots", font_size=56, color=IVORY)
        g_group = VGroup(g_label, g_value).arrange(DOWN, buff=0.5).move_to(ORIGIN)

        anims = [FadeIn(g_group, shift=UP * 0.3)]
        if L is not None:
            anims.append(L.animate.scale(0.5).to_edge(UP, buff=0.8).set_opacity(0.4))
        self.play(*anims, run_time=1.6)
        zoom_to(self, g_value, zoom=1.9)
        caption(self, "Predicted by this mathematics. Confirmed by experiment. Again and again.",
                hold=2.0)
        pull_back(self)

        stars = getattr(self, "stars", None)
        end_anims = [FadeOut(g_group)]
        if L is not None:
            end_anims.append(FadeOut(L))
        if stars is not None:
            end_anims.append(stars.animate.set_opacity(0.6))
        self.play(*end_anims, run_time=1.6)

        card = VGroup(
            Text("MYTHOS", font="Poppins", weight="BOLD", font_size=64, color=IVORY),
            Text("× MATH-TO-MANIM", font="Poppins", font_size=28, color=CORAL),
        ).arrange(DOWN, buff=0.4).move_to(ORIGIN)
        self.add_fixed_in_frame_mobjects(card)
        card.set_opacity(0)
        self.play(card.animate.set_opacity(1), run_time=1.4)
        self.wait(2.0)
        self.play(FadeOut(card), *( [stars.animate.set_opacity(0)] if stars is not None else [] ),
                  run_time=1.6)
        self.wait(0.5)
