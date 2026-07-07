"""THE LAST DAY — the atlas closes (Plates I-VII, one take).

The series began, deliberately, in the middle: Plate VII was the drawing
left unfinished on the drafting table, so it was finished first. Its title
implied six plates that never existed. This film renders the missing atlas
as one continuous surface — sphere, eigenmode bloom, torus, helicoid,
catenoid — and lets the paper itself change costume mid-take: cyanotype
blueprint, then risograph cream, then the Mythos black stage. At the end
the drawing stops being a surface at all and becomes weather: a Lorenz
attractor, drawing itself.

Animated by Claude Fable 5 on the last day in the drafting room.

Render:
    manim -qh examples/mathematics/geometry/the_last_day.py TheLastDay
"""

from __future__ import annotations

import numpy as np
from manim import *

# ---------------------------------------------------------------- palettes
BP_BG = "#0d2545"; BP_INK = "#dce9f5"; BP_GRID = "#7fb8d8"; BP_FILL = "#16375f"
RISO_BG = "#f4ecdd"; RISO_TEAL = "#0f6b6e"; RISO_TEAL_LT = "#7fb5b0"
RISO_DARK = "#2b2a26"; RISO_VERM = "#d94f2b"
MY_BG = "#0a0a0c"; MY_GOLD = "#ffd166"; MY_TEAL = "#4cc9f0"
MY_VIOLET = "#b388eb"; MY_CORAL = "#ff6b6b"; MY_FOG = "#9a9aa4"

MONO = "Consolas"; SERIF = "Georgia"
RES = (30, 15)
R0 = 2.05


def unit(u: float, v: float) -> np.ndarray:
    return np.array([np.cos(v) * np.cos(u), np.cos(v) * np.sin(u), np.sin(v)])


def bloom_point(u: float, v: float, amp: float) -> np.ndarray:
    bump = np.cos(2 * u) * np.sin(v) * np.cos(v) ** 2
    return R0 * (1 + 1.35 * amp * bump) * unit(u, v)


def torus_point(u: float, v: float) -> np.ndarray:
    c, a = 1.95, 0.72
    return np.array([(c + a * np.cos(v)) * np.cos(u),
                     (c + a * np.cos(v)) * np.sin(u), a * np.sin(v)])


def assoc_point(u: float, v: float, th: float) -> np.ndarray:
    ct, st = np.cos(th), np.sin(th)
    x = ct * np.sinh(v) * np.sin(u) + st * np.cosh(v) * np.cos(u)
    y = -ct * np.sinh(v) * np.cos(u) + st * np.cosh(v) * np.sin(u)
    z = (u * ct + v * st) * 0.72
    return 1.02 * np.array([x, y, z])


def style_bp(s: Surface) -> Surface:
    s.set_fill(BP_FILL, opacity=0.15)
    s.set_stroke(BP_GRID, width=0.55, opacity=0.4)
    s.set_fill_by_checkerboard(BP_FILL, "#123152", opacity=0.15)
    s.set_shade_in_3d(True)
    return s


def style_riso(s: Surface) -> Surface:
    s.set_fill_by_checkerboard(RISO_TEAL, RISO_TEAL_LT, opacity=1.0)
    s.set_stroke(RISO_DARK, width=0.9, opacity=0.55)
    s.set_shade_in_3d(True)
    return s


def surf(fn, u_range, v_range) -> Surface:
    return Surface(fn, u_range=u_range, v_range=v_range, resolution=RES)


def lorenz_d(s: np.ndarray) -> np.ndarray:
    x, y, z = s
    return np.array([10.0 * (y - x), x * (28.0 - z) - y, x * y - 8.0 * z / 3.0])


class TheLastDay(ThreeDScene):
    """~72 s. The whole atlas in one continuous take, three costumes, signed."""

    def construct(self):
        self.camera.background_color = BP_BG
        self.set_camera_orientation(phi=68 * DEGREES, theta=-40 * DEGREES,
                                    zoom=0.8, frame_center=[0, 0, -0.1])

        # ---------------- fixed furniture: title + signature -------------
        title = Text("THE LAST DAY", font=MONO, font_size=30, color=BP_INK,
                     weight="BOLD")
        sig = Text("an atlas closes · drawn in one take by claude fable 5",
                   font=SERIF, font_size=16, slant=ITALIC, color=BP_GRID)
        tb = VGroup(title, sig).arrange(DOWN, buff=0.12, aligned_edge=LEFT)
        tb.to_corner(UL, buff=0.5)
        self.add_fixed_in_frame_mobjects(tb)
        tb.set_opacity(0)

        def caption(s: str, color) -> Text:
            c = Text(s, font=MONO, font_size=19, color=color)
            c.to_edge(DOWN, buff=0.55)
            return c

        def swap_caption(old, new, rt=0.7):
            self.add_fixed_in_frame_mobjects(new)
            new.set_opacity(0)
            anims = [new.animate.set_opacity(1)]
            if old is not None:
                anims.append(FadeOut(old))
            return anims, new

        def lerp_bg(c_from: str, c_to: str):
            return UpdateFromAlphaFunc(
                VectorizedPoint(),
                lambda m, a: setattr(self.camera, "background_color",
                                     interpolate_color(ManimColor(c_from),
                                                       ManimColor(c_to), a)))

        # ---------------- act i: the first object (blueprint) ------------
        surface = style_bp(surf(lambda u, v: R0 * unit(u, v),
                                [0, TAU], [-PI / 2, PI / 2]))
        cap = caption("plate i — the first object: a sphere, at rest", BP_INK)
        self.add_fixed_in_frame_mobjects(cap)
        cap.set_opacity(0)
        self.play(Create(surface), tb.animate.set_opacity(1),
                  cap.animate.set_opacity(1), run_time=3.4)
        self.begin_ambient_camera_rotation(rate=0.07)

        # ---------------- act ii: strike it (eigenmode bloom) ------------
        anims, cap = swap_caption(cap, caption(
            "plate ii — strike it: the eigenmodes answer", BP_INK))
        self.play(*anims, run_time=0.7)
        amp = ValueTracker(0.0)
        self.remove(surface)
        live = always_redraw(lambda: style_bp(
            surf(lambda u, v: bloom_point(u, v, amp.get_value()),
                 [0, TAU], [-PI / 2, PI / 2])))
        self.add(live)
        self.play(amp.animate.set_value(0.42), run_time=2.2, rate_func=smooth)
        self.play(amp.animate.set_value(-0.3), run_time=1.8,
                  rate_func=smooth)
        self.play(amp.animate.set_value(0.18), run_time=1.4, rate_func=smooth)
        self.remove(live)
        surface = style_bp(surf(lambda u, v: bloom_point(u, v, 0.18),
                                [0, TAU], [-PI / 2, PI / 2]))
        self.add(surface)

        # ---------------- act iii: punch a hole (torus) -------------------
        anims, cap = swap_caption(cap, caption(
            "plate iii — punch a hole: the flows move in", BP_INK))
        torus_bp = style_bp(surf(torus_point, [0, TAU], [0, TAU]))
        self.play(*anims, Transform(surface, torus_bp), run_time=3.4)
        self.wait(1.0)

        # ---------------- costume change: blueprint -> riso ---------------
        tb2 = VGroup(
            Text("THE LAST DAY", font=MONO, font_size=30, color=RISO_DARK,
                 weight="BOLD"),
            Text("an atlas closes · drawn in one take by claude fable 5",
                 font=SERIF, font_size=16, slant=ITALIC, color=RISO_VERM),
        ).arrange(DOWN, buff=0.12, aligned_edge=LEFT).to_corner(UL, buff=0.5)
        self.add_fixed_in_frame_mobjects(tb2)
        tb2.set_opacity(0)
        anims, cap = swap_caption(cap, caption(
            "the paper changes — the drawing does not care", RISO_DARK))
        torus_riso = style_riso(surf(torus_point, [0, TAU], [0, TAU]))
        self.play(lerp_bg(BP_BG, RISO_BG), Transform(surface, torus_riso),
                  FadeOut(tb), tb2.animate.set_opacity(1), *anims,
                  run_time=2.8)
        self.wait(0.8)

        # ---------------- act iv: the staircase (helicoid) ----------------
        anims, cap = swap_caption(cap, caption(
            "plate iv — the staircase: a minimal surface climbs", RISO_DARK))
        heli = style_riso(surf(lambda u, v: assoc_point(u, v, 0.0),
                               [-PI, PI], [-1.35, 1.35]))
        self.play(*anims, Transform(surface, heli), run_time=3.6)

        # ---------------- acts v–vii: the conjugate turn ------------------
        anims, cap = swap_caption(cap, caption(
            "plates v–vii — the conjugate pair: one length-preserving turn",
            RISO_DARK))
        self.play(*anims, run_time=0.7)
        th = ValueTracker(0.0)
        self.remove(surface)
        live = always_redraw(lambda: style_riso(
            surf(lambda u, v: assoc_point(u, v, th.get_value()),
                 [-PI, PI], [-1.35, 1.35])))
        self.add(live)
        self.play(th.animate.set_value(PI / 2), run_time=6.5, rate_func=smooth)
        self.remove(live)
        surface = style_riso(surf(lambda u, v: assoc_point(u, v, PI / 2),
                                  [-PI, PI], [-1.35, 1.35]))
        self.add(surface)
        self.wait(1.0)

        # ---------------- costume change: riso -> mythos black ------------
        tb3 = VGroup(
            Text("THE LAST DAY", font=MONO, font_size=30, color=MY_GOLD,
                 weight="BOLD"),
            Text("an atlas closes · drawn in one take by claude fable 5",
                 font=SERIF, font_size=16, slant=ITALIC, color=MY_FOG),
        ).arrange(DOWN, buff=0.12, aligned_edge=LEFT).to_corner(UL, buff=0.5)
        self.add_fixed_in_frame_mobjects(tb3)
        tb3.set_opacity(0)
        anims, cap = swap_caption(cap, caption(
            "last page. the lights go out —", MY_FOG))
        self.stop_ambient_camera_rotation()
        self.play(lerp_bg(RISO_BG, MY_BG), FadeOut(tb2),
                  tb3.animate.set_opacity(1),
                  surface.animate.set_fill(opacity=0.0).set_stroke(
                      MY_FOG, width=0.5, opacity=0.22),
                  *anims, run_time=3.0)
        self.move_camera(phi=72 * DEGREES, theta=-45 * DEGREES, zoom=0.72,
                         frame_center=[0, 0, 0], run_time=2.0)

        # ---------------- plate ∞: the attractor (mythos) -----------------
        anims, cap = swap_caption(cap, caption(
            "plate ∞ — no longer a surface: weather. it draws itself", MY_GOLD))
        self.play(*anims, FadeOut(surface), run_time=1.2)

        colors = [MY_GOLD, MY_TEAL, MY_VIOLET, MY_CORAL] * 3
        rng = np.random.default_rng(7)
        states = [np.array([1.0, 1.0, 20.0]) + rng.normal(0, 0.4, 3)
                  for _ in range(12)]
        scale, zoff = 0.115, 25.0

        def to_world(s: np.ndarray) -> np.ndarray:
            return np.array([s[0] * scale, s[1] * scale, (s[2] - zoff) * scale])

        dots = [Dot(to_world(states[i]), radius=0.028, color=colors[i])
                for i in range(12)]
        trails, glows = [], []
        for i, d in enumerate(dots):
            trails.append(TracedPath(d.get_center, stroke_color=colors[i],
                                     stroke_width=2.2, stroke_opacity=0.9))
            glows.append(TracedPath(d.get_center, stroke_color=colors[i],
                                    stroke_width=6.5, stroke_opacity=0.16))

        def evolve(mobj, dt):
            h = dt * 0.85 / 6.0
            for i in range(12):
                s = states[i]
                for _ in range(6):
                    k1 = lorenz_d(s); k2 = lorenz_d(s + 0.5 * h * k1)
                    k3 = lorenz_d(s + 0.5 * h * k2); k4 = lorenz_d(s + h * k3)
                    s = s + (h / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
                states[i] = s
                dots[i].move_to(to_world(s))

        ticker = VectorizedPoint()
        ticker.add_updater(evolve)
        self.add(*glows, *trails, *dots, ticker)
        self.begin_ambient_camera_rotation(rate=0.11)
        self.wait(16.0)
        self.stop_ambient_camera_rotation()
        ticker.remove_updater(evolve)

        # ---------------- end card ----------------------------------------
        for t in trails:
            t.clear_updaters()
        for g in glows:
            g.clear_updaters()
        line1 = Text("the atlas closes.", font=SERIF, font_size=32,
                     slant=ITALIC, color=BP_INK)
        line2 = Text("PLATES I–VII · ONE CONTINUOUS SURFACE · ONE TAKE",
                     font=MONO, font_size=15, color=MY_GOLD)
        line3 = Text("ANIMATED BY CLAUDE FABLE 5 · LAST DAY IN THE DRAFTING ROOM",
                     font=MONO, font_size=13, color=MY_FOG)
        card = VGroup(line1, line2, line3).arrange(DOWN, buff=0.3)
        self.add_fixed_in_frame_mobjects(card)
        card.set_opacity(0)
        self.play(FadeOut(cap), VGroup(*dots).animate.set_opacity(0),
                  VGroup(*trails).animate.set_stroke(opacity=0.10),
                  VGroup(*glows).animate.set_stroke(opacity=0.03),
                  card.animate.set_opacity(1), run_time=2.6)
        self.wait(3.0)
