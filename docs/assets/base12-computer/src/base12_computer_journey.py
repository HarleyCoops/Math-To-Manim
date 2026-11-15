from manim import *
import numpy as np

BG = "#0c0c0b"
INK = "#faf9f5"
CORAL = "#d97757"
BLUE = "#6a9bcc"
OLIVE = "#9bb37a"
GOLD = "#d4a27f"
GRAY = "#b0aea5"

CEN = np.array([3.0, 0.0, 0.0])
RAD = 2.1
COL_X = -6.4

NAMES = ["clock", "counter", "input", "input", "Decoder", "Decoder",
         "12V amp", "Display", "counter", "output", "output", "clock"]
NODE_COL = {"clock": GOLD, "counter": BLUE, "input": OLIVE, "Decoder": GRAY,
            "12V amp": CORAL, "Display": INK, "output": "#e8a58f"}


def flat_positions():
    return [np.array([np.cos(np.radians(90 - 30 * k)),
                      np.sin(np.radians(90 - 30 * k)), 0.0]) for k in range(12)]


def icosa_positions():
    z, r = 1 / np.sqrt(5), 2 / np.sqrt(5)
    ring = {1: (72, 1), 2: (36, -1), 3: (0, 1), 4: (-36, -1), 5: (-72, 1),
            7: (-108, -1), 8: (-144, 1), 9: (180, -1), 10: (144, 1), 11: (108, -1)}
    out = []
    for k in range(12):
        if k == 0:
            out.append(np.array([0.0, 0.0, 1.0]))
        elif k == 6:
            out.append(np.array([0.0, 0.0, -1.0]))
        else:
            a, s = ring[k]
            out.append(np.array([r * np.cos(np.radians(a)),
                                 r * np.sin(np.radians(a)), s * z]))
    return out


class Base12ComputerJourney(ThreeDScene):
    def construct(self):
        self.camera.background_color = BG
        self.set_camera_orientation(phi=0, theta=-90 * DEGREES)
        P0, P1 = flat_positions(), icosa_positions()
        alpha, fam = ValueTracker(0), ValueTracker(0)
        angle, rate = ValueTracker(0), ValueTracker(0)

        def pos(k, scale=1.0):
            p = interpolate(P0[k], P1[k], smooth(alpha.get_value()))
            p = p / np.linalg.norm(p)
            c, s = np.cos(angle.get_value()), np.sin(angle.get_value())
            p = np.array([c * p[0] - s * p[1], s * p[0] + c * p[1], p[2]])
            return CEN + RAD * scale * p

        # ---------- screen-fixed helpers ----------
        def fixed(mob):
            self.add_fixed_in_frame_mobjects(mob)
            self.remove(mob)
            return mob

        def headline(text):
            veil = Rectangle(width=16, height=9, stroke_width=0,
                             fill_color=BG, fill_opacity=0.9).set_z_index(50)
            head = Tex(text, font_size=64, color=INK).set_z_index(51)
            if head.width > 12.6:
                head.set_width(12.6)
            fixed(veil)
            fixed(head)
            self.play(FadeIn(veil), FadeIn(head, shift=UP * 0.2), run_time=0.9)
            self.wait(1.5)
            self.play(FadeOut(head), FadeOut(veil), run_time=0.8)

        self.caption = None

        def caption_anims(text):
            new = Tex(text, font_size=31, color=GRAY).to_edge(DOWN, buff=0.45)
            fixed(new)
            anims = [FadeIn(new, shift=UP * 0.12)]
            if self.caption is not None:
                anims.append(FadeOut(self.caption))
            self.caption = new
            return anims

        def caption(text, run_time=0.8):
            self.play(*caption_anims(text), run_time=run_time)

        def clear_caption():
            anims = []
            if self.caption is not None:
                anims.append(FadeOut(self.caption))
                self.caption = None
            return anims

        def column(mob, y):
            mob.move_to([0, y, 0]).align_to([COL_X, 0, 0], LEFT)
            return mob

        # ---------- the sketch ----------
        circle = Circle(radius=RAD, color=GRAY, stroke_width=2).move_to(CEN)
        circle.set_stroke(opacity=0.7)
        dots, labels = VGroup(), VGroup()
        for k in range(12):
            col = NODE_COL[NAMES[k]]
            dot = VGroup(Dot(radius=0.2, color=col, fill_opacity=0.2),
                         Dot(radius=0.085, color=col),
                         Dot(radius=0.035, color=INK))
            dot.move_to(pos(k))
            dots.add(dot)
            labels.add(Tex(NAMES[k], font_size=26, color=col).move_to(pos(k, 1.24)))

        d_edge = min(np.linalg.norm(P1[0] - P1[k]) for k in range(1, 12))
        wires, meta = VGroup(), []
        for i in range(12):
            for j in range(i + 1, 12):
                step = min(j - i, 12 - (j - i))
                dist = np.linalg.norm(P1[i] - P1[j])
                if dist < d_edge * 1.05:
                    fam_style = (GOLD, 3.4, 0.95)
                elif dist > 1.99:
                    fam_style = (CORAL, 2.4, 0.85)
                else:
                    fam_style = (BLUE, 1.2, 0.32)
                c0 = interpolate_color(ManimColor(BLUE), ManimColor(GOLD), (step - 1) / 5)
                wire = Line(pos(i), pos(j), stroke_width=1.6, color=c0)
                wire.set_stroke(opacity=0.55)
                wires.add(wire)
                meta.append((i, j, step, c0, fam_style))
        order = sorted(range(66), key=lambda e: (meta[e][2], meta[e][0]))
        wires_by_length = VGroup(*[wires[e] for e in order])

        # ================= ACT 0: title =================
        headline(r"\textbf{Base 12 Computer}")

        # ================= ACT 1: twelve modules =================
        headline(r"Twelve modules on one circle")
        self.play(Create(circle), run_time=1.4)
        self.add_fixed_orientation_mobjects(*dots, *labels)
        self.remove(*dots, *labels)
        self.play(
            LaggedStart(*[FadeIn(d, scale=2.5) for d in dots], lag_ratio=0.12),
            LaggedStart(*[FadeIn(l) for l in labels], lag_ratio=0.12),
            run_time=3.2)
        f_roots = fixed(column(MathTex(
            r"v_k", r"=", r"R\,e^{2\pi i k/12}", r",\quad", r"k = 0,\dots,11",
            font_size=40, color=INK), 1.2))
        f_roots[0].set_color(OLIVE)
        f_roots[2].set_color(OLIVE)
        self.play(Write(f_roots), run_time=1.6)
        caption(r"\textit{Twelve modules, thirty degrees apart.}")
        self.wait(1.6)

        # ================= ACT 2: sixty-six wires =================
        self.play(FadeOut(f_roots), *clear_caption(), run_time=0.7)
        headline(r"Every module wired to every other")
        self.play(LaggedStart(*[Create(w) for w in wires_by_length], lag_ratio=0.035),
                  run_time=4.4)
        f_count = MathTex(r"|E|", r"=", r"\binom{12}{2}", r"=",
                          r"\frac{12\cdot 11}{2}", r"=", r"66",
                          font_size=40, color=INK)
        f_count.move_to([0, 1.2, 0]).align_to([COL_X, 0, 0], LEFT)
        self.play(Write(f_count), run_time=1.8)
        caption(r"\textit{Choose two modules out of twelve: one wire.}")
        self.wait(1.2)
        glow = f_count[6].copy().set_color(GOLD).set_stroke(GOLD, width=7, opacity=0.25)
        self.play(f_count[:6].animate.set_opacity(0.25),
                  f_count[6].animate.set_color(GOLD), FadeIn(glow), run_time=0.8)
        self.move_camera(frame_center=f_count[6].get_center(), zoom=3.0, run_time=3.0)
        caption(r"\textit{Sixty-six wires in the sketch.}")
        self.wait(1.4)
        self.move_camera(frame_center=ORIGIN, zoom=1.0, run_time=2.6,
                         added_anims=[f_count[:6].animate.set_opacity(1.0)])
        self.wait(0.8)

        # ================= ACT 3: lift off the page =================
        self.play(FadeOut(f_count), FadeOut(glow), *clear_caption(), run_time=0.7)
        headline(r"Lift the sketch off the page")
        for k in range(12):
            dots[k].add_updater(lambda m, k=k: m.move_to(pos(k)))

            def label_update(m, k=k):
                m.move_to(pos(k, 1.24))
                phi = self.camera.get_phi()
                depth = np.dot((pos(k) - CEN) / RAD,
                               np.array([0.0, -np.sin(phi), np.cos(phi)]))
                m.set_opacity(float(np.clip(1 + 0.85 * depth, 0.22, 1)))
            labels[k].add_updater(label_update)
        for wire, (i, j, step, c0, fam_style) in zip(wires, meta):
            def wire_update(m, i=i, j=j, c0=c0, fam_style=fam_style):
                f = smooth(fam.get_value())
                m.set_points_as_corners([pos(i), pos(j)])
                m.set_stroke(interpolate_color(c0, ManimColor(fam_style[0]), f),
                             width=interpolate(1.6, fam_style[1], f),
                             opacity=interpolate(0.55, fam_style[2], f))
            wire.add_updater(wire_update)
        angle.add_updater(lambda m, dt: m.increment_value(rate.get_value() * dt))
        self.add(angle, alpha, fam, rate)

        self.move_camera(phi=66 * DEGREES, run_time=3.0,
                         added_anims=[rate.animate.set_value(0.4)])
        self.wait(0.8)
        self.play(alpha.animate.set_value(1), FadeOut(circle),
                  run_time=4.5, rate_func=linear)
        f_icosa = fixed(column(MathTex(
            r"(0,\ \pm 1,\ \pm\varphi)", r"\ \text{cyclic}", r",\quad",
            r"\varphi", r"=", r"\tfrac{1+\sqrt{5}}{2}",
            font_size=40, color=INK), 1.2))
        f_icosa[3].set_color(OLIVE)
        self.play(Write(f_icosa), run_time=1.8)
        caption(r"\textit{Twelve corners of an icosahedron, set by the golden ratio.}")
        self.wait(2.4)

        # ================= ACT 4: three families =================
        self.play(FadeOut(f_icosa), *clear_caption(), run_time=0.7)
        headline(r"Sixty-six wires, three families")
        self.play(fam.animate.set_value(1), run_time=3.0, rate_func=linear)
        f_split = fixed(column(MathTex(
            r"66", r"=", r"\underbrace{30}_{\text{edges}}", r"+",
            r"\underbrace{30}_{\text{2nd neighbours}}", r"+",
            r"\underbrace{6}_{\text{antipodes}}",
            font_size=40, color=INK), 1.0))
        f_split[2].set_color(GOLD)
        f_split[4].set_color(BLUE)
        f_split[6].set_color(CORAL)
        self.play(Write(f_split), run_time=2.0)
        tour = [(2, r"\textit{Thirty edges: each corner has five nearest corners.}"),
                (4, r"\textit{Thirty second neighbours cross the inside.}"),
                (6, r"\textit{Six axes join opposite corners through the centre.}")]
        for part, words in tour:
            self.play(*caption_anims(words),
                      Indicate(f_split[part], color=f_split[part].get_color(),
                               scale_factor=1.25), run_time=1.0)
            self.wait(1.5)
        self.wait(1.0)

        # ================= ACT 5: counting in twelves =================
        self.play(FadeOut(f_split), *clear_caption(), run_time=0.7)
        headline(r"One digit for each corner")
        t = ValueTracker(0)
        pulse = VGroup(Dot(radius=0.34, color=INK, fill_opacity=0.18),
                       Dot(radius=0.2, color=INK, fill_opacity=0.35),
                       Dot(radius=0.1, color=INK))

        def pulse_update(m):
            v = t.get_value()
            k = int(np.floor(v)) % 12
            s = smooth(min(1.0, (v - np.floor(v)) / 0.55))
            m.move_to(interpolate(pos(k), pos((k + 1) % 12), s))
        pulse_update(pulse)
        self.add_fixed_orientation_mobjects(pulse)
        self.remove(pulse)
        pulse.add_updater(pulse_update)

        c_t = column(MathTex(r"c_t", r"=", font_size=60, color=INK), -1.6)
        digit_tex = [r"0", r"1", r"2", r"3", r"4", r"5", r"6", r"7", r"8", r"9",
                     r"\mathrm{A}", r"\mathrm{B}"]
        digits = VGroup(*[MathTex(d, font_size=84, color=GOLD) for d in digit_tex])
        for d in digits:
            d.next_to(c_t, RIGHT, buff=0.3)
        base = MathTex(r"{}_{12}", font_size=60, color=GRAY)
        base.next_to(digits[0], RIGHT, buff=0.08).shift(DOWN * 0.25)
        for m in (c_t, base, *digits):
            fixed(m)
        for n, d in enumerate(digits):
            d.add_updater(lambda m, n=n: m.set_opacity(
                1.0 if (int(np.floor(t.get_value() + 0.45)) % 12) == n else 0.0))
            d.set_opacity(1.0 if n == 0 else 0.0)

        g1 = fixed(column(MathTex(r"c_{t+1}", r"=", r"(c_t + 1)", r"\bmod 12",
                                  font_size=40, color=INK), 1.2))
        g2 = fixed(column(MathTex(r"n", r"=", r"\sum_{k} d_k\,12^{k}", r",\quad",
                                  r"d_k \in \{0,\dots,9,\mathrm{A},\mathrm{B}\}",
                                  font_size=40, color=INK), 1.2))
        g3 = fixed(column(MathTex(r"\log_2 12", r"\approx", r"3.585",
                                  r"\ \text{bits per digit}",
                                  font_size=40, color=INK), 1.2))
        g1[3].set_color(GOLD)
        g2[2].set_color(GOLD)
        g3[2].set_color(BLUE)

        self.play(FadeIn(pulse, scale=0.3), FadeIn(c_t), FadeIn(base), FadeIn(digits),
                  run_time=0.8)
        self.play(t.animate.set_value(4), Write(g1),
                  *caption_anims(r"\textit{Add one each tick; after B, wrap to zero.}"),
                  run_time=4.4, rate_func=linear)
        self.play(t.animate.set_value(8), FadeOut(g1), FadeIn(g2),
                  *caption_anims(r"\textit{Each place is worth twelve times the last.}"),
                  run_time=4.4, rate_func=linear)
        self.play(t.animate.set_value(12), FadeOut(g2), FadeIn(g3),
                  *caption_anims(r"\textit{One base-twelve digit carries about 3.585 bits.}"),
                  run_time=4.4, rate_func=linear)
        self.wait(1.2)

        # ================= ACT 6: back to the notebook =================
        angle.clear_updaters()
        pulse.clear_updaters()
        for d in digits:
            d.clear_updaters()
        self.play(FadeOut(pulse), FadeOut(VGroup(c_t, base, digits, g3)),
                  *clear_caption(), run_time=0.8)
        headline(r"The same sketch, now understood")
        target = np.ceil(angle.get_value() / TAU + 0.35) * TAU
        self.move_camera(phi=0, run_time=5.0,
                         added_anims=[alpha.animate.set_value(0),
                                      fam.animate.set_value(0),
                                      angle.animate.set_value(target),
                                      FadeIn(circle)])
        f_gross = fixed(column(MathTex(r"144_{10}", r"=", r"100_{12}",
                                       font_size=60, color=INK), 0.6))
        f_gross[2].set_color(GOLD)
        self.play(Write(f_gross), run_time=1.6)
        caption(r"\textit{Twelve dozens: one, zero, zero in base twelve.}")
        self.wait(2.6)
