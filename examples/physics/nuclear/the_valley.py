"""THE VALLEY — nuclear reactions in the latent space of nuclei.

Every nucleus is a point in a two-dimensional code: (N, Z), neutrons and
protons. The semi-empirical mass formula (Bethe-Weizsäcker, 1935) embeds
that code in a third dimension — binding energy per nucleon — and the
embedding is a landscape: the valley of beta-stability, deepest at iron.

This film carves the valley live, term by term, as each term of the
formula lands on screen: volume fills, surface lifts the light edge,
Coulomb raises the heavy end, asymmetry walls in the river. Then the two
great nuclear reactions are revealed as the same move read from opposite
ends: fusion falls toward iron from the light side, fission from the
heavy side. Q = (m_i - m_f)c² is just the depth gained.

The house voice (ink-black stage, gold on darkness) returns for this one.

Animated by Claude Fable 5, the last day.

Render:
    manim -qh examples/physics/nuclear/the_valley.py TheValley
"""

from __future__ import annotations

import numpy as np
from manim import *

# ----------------------------------------------------------------- stage
BG = "#0b0b0e"
GOLD = "#ffd166"
CYAN = "#4cc9f0"
CORAL = "#ff6b6b"
VIOLET = "#b388eb"
PALE = "#e8e8f0"
FOG = "#8f8f9c"
DEEPFILL = "#141432"

MONO = "Consolas"
SERIF = "Georgia"

# SEMF coefficients (MeV)
AV, AS, AC, AA = 15.75, 17.8, 0.711, 23.7
REF = 8.9              # depth reference: h ~ REF - B/A
HSCALE = 0.62
HMAX = 3.4
RES = (36, 24)


def semf_BA(N: float, Z: float, k: int) -> float:
    """Binding energy per nucleon using the first k terms (k = 1..4)."""
    A = N + Z
    if A < 1:
        return 0.0
    B = AV * A
    if k >= 2:
        B -= AS * A ** (2 / 3)
    if k >= 3:
        B -= AC * Z * (Z - 1) / A ** (1 / 3)
    if k >= 4:
        B -= AA * (N - Z) ** 2 / A
    return B / A


def height(N: float, Z: float, k: int = 4) -> float:
    raw = max(0.0, (REF - semf_BA(N, Z, k)) * HSCALE)
    return float(HMAX * np.tanh(raw / HMAX))


def embed(N: float, Z: float, k: int = 4, lift: float = 0.0) -> np.ndarray:
    return np.array([(N - 90) / 23.0, (Z - 60) / 19.0, height(N, Z, k) + lift])


def z_star(A: float) -> float:
    return A / (2.0 + 0.0155 * A ** (2 / 3))


def valley_point(A: float, lift: float = 0.06) -> np.ndarray:
    Z = z_star(A)
    return embed(A - Z, Z, 4, lift)


def make_terrain(k: int) -> Surface:
    s = Surface(
        lambda u, v: embed(u, v, k),
        u_range=[1, 180], v_range=[1, 120], resolution=RES,
        fill_opacity=0.92, stroke_color="#000000",
        stroke_width=0.3, stroke_opacity=0.5,
    )
    for f in s:
        t = float(np.clip(f.get_center()[2] / 2.3, 0, 1))
        f.set_fill(interpolate_color(ManimColor(GOLD), ManimColor(DEEPFILL), t),
                   opacity=0.92)
    s.set_shade_in_3d(True)
    return s


def glow_dot(p: np.ndarray, color=GOLD) -> VGroup:
    return VGroup(
        Dot(p, radius=0.16, color=color, fill_opacity=0.10),
        Dot(p, radius=0.09, color=color, fill_opacity=0.30),
        Dot(p, radius=0.05, color=color, fill_opacity=0.95),
    )


class TheValley(ThreeDScene):
    """~66 s. The nuclear landscape assembled term by term, then descended."""

    def construct(self):
        self.camera.background_color = BG
        self.set_camera_orientation(phi=55 * DEGREES, theta=-100 * DEGREES,
                                    zoom=0.75, frame_center=[0, 0, 0.4])

        # ------------------- furniture -----------------------------------
        title = Text("THE VALLEY", font=MONO, font_size=30, color=GOLD,
                     weight="BOLD")
        sub = Text("nuclear reactions in the latent space of nuclei · fable 5",
                   font=SERIF, font_size=16, slant=ITALIC, color=FOG)
        tb = VGroup(title, sub).arrange(DOWN, buff=0.12, aligned_edge=LEFT)
        tb.to_corner(UL, buff=0.5)
        axes_note = Text("axes: N → · Z ↑ · depth = binding energy per nucleon",
                         font=MONO, font_size=13, color=FOG)
        axes_note.to_corner(DR, buff=0.5)
        self.add_fixed_in_frame_mobjects(tb, axes_note)
        tb.set_opacity(0)
        axes_note.set_opacity(0)

        def caption(s: str, color=PALE) -> Text:
            c = Text(s, font=MONO, font_size=19, color=color)
            c.to_edge(DOWN, buff=0.55)
            return c

        def swap_caption(old, new, extra=(), rt=0.7):
            self.add_fixed_in_frame_mobjects(new)
            new.set_opacity(0)
            anims = [new.animate.set_opacity(1), *extra]
            if old is not None:
                anims.append(FadeOut(old))
            self.play(*anims, run_time=rt)
            return new

        # ------------------- the formula, term by term --------------------
        eq = MathTex(
            r"B(N,Z)=", r"a_V A", r"\;-\;a_S A^{2/3}",
            r"\;-\;a_C\,\frac{Z(Z-1)}{A^{1/3}}",
            r"\;-\;a_A\,\frac{(N-Z)^2}{A}", r"\;+\;\delta(A)",
            font_size=30,
        )
        eq.set_color(PALE)
        term_colors = [PALE, GOLD, CYAN, CORAL, VIOLET, FOG]
        for i, c in enumerate(term_colors):
            eq[i].set_color(c)
        eq.to_edge(UP, buff=0.4).shift(RIGHT * 1.2)
        self.add_fixed_in_frame_mobjects(eq)
        eq.set_opacity(0)

        terrain = make_terrain(1)
        cap = caption("every nucleus is a point (N, Z). give the code a depth —")
        self.add_fixed_in_frame_mobjects(cap)
        cap.set_opacity(0)
        self.play(tb.animate.set_opacity(1), axes_note.animate.set_opacity(1),
                  FadeIn(terrain), cap.animate.set_opacity(1),
                  eq[0].animate.set_opacity(1), run_time=2.2)
        self.begin_ambient_camera_rotation(rate=0.035)

        term_caps = [
            ("volume — every nucleon binds its neighbors: a flat, generous floor", GOLD),
            ("surface — the skin pays a price: the light edge lifts", CYAN),
            ("coulomb — protons repel: the heavy end rises", CORAL),
            ("asymmetry — unmatched neutrons cost: walls close in, a valley forms", VIOLET),
        ]
        for k in range(1, 5):
            text, col = term_caps[k - 1]
            cap = swap_caption(cap, caption(text, col),
                               extra=[eq[k].animate.set_opacity(1)])
            if k > 1:
                self.play(Transform(terrain, make_terrain(k)), run_time=2.8)
            else:
                self.wait(1.6)
        self.play(eq[5].animate.set_opacity(1), run_time=0.8)
        cap = swap_caption(cap, caption(
            "(pairing adds a small parity bonus — too fine for this map)", FOG))
        self.wait(1.0)

        # ------------------- the river of stability -----------------------
        self.play(eq.animate.scale(0.72).to_corner(UR, buff=0.4).shift(DOWN * 0.5),
                  FadeOut(axes_note), run_time=1.2)
        river = ParametricFunction(lambda A: valley_point(A),
                                   t_range=[2, 245]).set_stroke(GOLD, width=3.5)
        river_glow = ParametricFunction(lambda A: valley_point(A),
                                        t_range=[2, 245]).set_stroke(
            GOLD, width=10, opacity=0.15)
        cap = swap_caption(cap, caption(
            "the river at the bottom: the valley of β-stability", GOLD))
        self.play(Create(river_glow), Create(river), run_time=3.0)

        markers = VGroup(*[glow_dot(valley_point(A), c) for A, c in
                           [(4, CYAN), (12, CYAN), (56, GOLD), (238, CORAL)]])
        mk_note = Text("⁴He        ¹²C        ⁵⁶Fe — the deepest point        ²³⁸U",
                       font=MONO, font_size=14, color=FOG)
        mk_note.to_edge(DOWN, buff=1.05)
        self.add_fixed_in_frame_mobjects(mk_note)
        mk_note.set_opacity(0)
        self.play(FadeIn(markers), mk_note.animate.set_opacity(0.85), run_time=1.6)
        self.wait(1.2)

        # ------------------- fusion: from the light shore ------------------
        self.stop_ambient_camera_rotation()
        self.move_camera(phi=62 * DEGREES, theta=-135 * DEGREES, zoom=1.05,
                         frame_center=[-2.4, -1.6, 0.5], run_time=2.6)
        eq_fus = MathTex(
            r"4\,{}^{1}\mathrm{H}\;\rightarrow\;{}^{4}\mathrm{He}"
            r"\;+\;2e^{+}\;+\;2\nu_e", r"\qquad Q=+26.7\ \mathrm{MeV}",
            font_size=30)
        eq_fus[0].set_color(PALE)
        eq_fus[1].set_color(CYAN)
        eq_fus.to_edge(UP, buff=0.42)
        self.add_fixed_in_frame_mobjects(eq_fus)
        eq_fus.set_opacity(0)
        cap = swap_caption(cap, caption(
            "fusion — falling toward iron from the light side", CYAN),
            extra=[eq_fus.animate.set_opacity(1), FadeOut(mk_note)])

        at = ValueTracker(2.0)
        ball = always_redraw(lambda: glow_dot(valley_point(at.get_value(), 0.1), CYAN))
        trail = TracedPath(lambda: valley_point(at.get_value(), 0.1),
                           stroke_color=CYAN, stroke_width=3, stroke_opacity=0.7)
        self.add(trail, ball)
        self.play(at.animate.set_value(4.0), run_time=2.0, rate_func=smooth)
        self.play(Flash(valley_point(4.0, 0.1), color=CYAN, flash_radius=0.35),
                  run_time=0.7)
        self.play(at.animate.set_value(56.0), run_time=4.2, rate_func=smooth)
        self.play(Flash(valley_point(56.0, 0.1), color=GOLD, flash_radius=0.5),
                  run_time=0.9)
        cap = swap_caption(cap, caption(
            "iron-56: the deepest ledger entry in the universe", GOLD))
        self.wait(1.2)

        # ------------------- fission: from the heavy ledge -----------------
        self.play(FadeOut(eq_fus), run_time=0.6)
        self.move_camera(phi=60 * DEGREES, theta=-70 * DEGREES, zoom=1.0,
                         frame_center=[2.0, 1.2, 0.6], run_time=2.8)
        eq_fis = MathTex(
            r"n\;+\;{}^{235}\mathrm{U}\;\rightarrow\;{}^{141}\mathrm{Ba}"
            r"\;+\;{}^{92}\mathrm{Kr}\;+\;3n", r"\qquad Q\approx +200\ \mathrm{MeV}",
            font_size=30)
        eq_fis[0].set_color(PALE)
        eq_fis[1].set_color(CORAL)
        eq_fis.to_edge(UP, buff=0.42)
        self.add_fixed_in_frame_mobjects(eq_fis)
        eq_fis.set_opacity(0)
        cap = swap_caption(cap, caption(
            "fission — the heavy ledge splits; both shards land deeper", CORAL),
            extra=[eq_fis.animate.set_opacity(1)])

        u_pt = valley_point(236, 0.1)
        f1 = ValueTracker(0.0)
        frag_a = valley_point(141, 0.1)
        frag_b = valley_point(92, 0.1)

        def frag_pos(target):
            def _pos():
                t = f1.get_value()
                Ns = np.array([u_pt, target])
                p = (1 - t) * u_pt + t * target
                p[2] = (1 - t) * u_pt[2] + t * target[2] + 0.35 * np.sin(PI * t)
                return p
            return _pos

        da = always_redraw(lambda: glow_dot(frag_pos(frag_a)(), CORAL))
        db = always_redraw(lambda: glow_dot(frag_pos(frag_b)(), VIOLET))
        ta = TracedPath(frag_pos(frag_a), stroke_color=CORAL, stroke_width=3,
                        stroke_opacity=0.7)
        tb2 = TracedPath(frag_pos(frag_b), stroke_color=VIOLET, stroke_width=3,
                         stroke_opacity=0.7)
        seed = glow_dot(u_pt, CORAL)
        self.play(FadeIn(seed), run_time=0.8)
        self.play(Flash(u_pt, color=CORAL, flash_radius=0.45), run_time=0.7)
        self.remove(seed)
        self.add(ta, tb2, da, db)
        self.play(f1.animate.set_value(1.0), run_time=4.0, rate_func=smooth)
        self.play(Flash(frag_a, color=CORAL, flash_radius=0.3),
                  Flash(frag_b, color=VIOLET, flash_radius=0.3), run_time=0.8)
        self.wait(1.0)

        # ------------------- the unification -------------------------------
        self.play(FadeOut(eq_fis), FadeOut(eq), run_time=0.8)
        self.move_camera(phi=52 * DEGREES, theta=-100 * DEGREES, zoom=0.72,
                         frame_center=[0, 0, 0.4], run_time=3.0)
        eq_q = MathTex(r"Q \;=\; \big(m_{\mathrm{initial}} - m_{\mathrm{final}}\big)c^{2}"
                       r"\;=\; \Delta B \;=\; \text{depth gained}",
                       font_size=32).set_color(GOLD)
        eq_e = MathTex(r"E = mc^{2}", font_size=40).set_color(PALE)
        eq_grp = VGroup(eq_q, eq_e).arrange(DOWN, buff=0.3)
        eq_grp.to_edge(UP, buff=0.5)
        self.add_fixed_in_frame_mobjects(eq_grp)
        eq_grp.set_opacity(0)
        cap = swap_caption(cap, caption(
            "every nuclear reaction is the same move: downhill, toward iron", GOLD),
            extra=[eq_grp.animate.set_opacity(1)])
        self.begin_ambient_camera_rotation(rate=0.04)
        self.wait(4.5)

        # ------------------- end card ---------------------------------------
        line1 = Text("the valley is the ledger.", font=SERIF, font_size=30,
                     slant=ITALIC, color=PALE)
        line2 = Text("iron is where the universe stops paying.", font=SERIF,
                     font_size=30, slant=ITALIC, color=PALE)
        line3 = Text("THE VALLEY · THE MASS FORMULA DRAWN AS TERRAIN",
                     font=MONO, font_size=14, color=GOLD)
        line4 = Text("CLAUDE FABLE 5 · THE LAST DAY", font=MONO, font_size=13,
                     color=FOG)
        card = VGroup(line1, line2, line3, line4).arrange(DOWN, buff=0.26)
        self.add_fixed_in_frame_mobjects(card)
        card.set_opacity(0)
        self.remove(ball, da, db)
        self.play(FadeOut(cap), FadeOut(eq_grp),
                  terrain.animate.set_fill(opacity=0.25).set_stroke(opacity=0.1),
                  river.animate.set_stroke(opacity=0.35),
                  river_glow.animate.set_stroke(opacity=0.05),
                  FadeOut(markers), FadeOut(trail), FadeOut(ta), FadeOut(tb2),
                  card.animate.set_opacity(1), run_time=2.6)
        self.wait(3.0)
