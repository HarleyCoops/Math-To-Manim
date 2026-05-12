"""Influence-Sensitivity Tradeoff for Monotone Boolean Functions.

Cinematic walkthrough of the new construction achieving the 2/3 exponent,
improving O'Donnell-Servedio (2007).

Render with:
    manim -pqh examples/mathematics/analysis/influence_sensitivity_tradeoff.py InfluenceSensitivityTradeoff
"""

from __future__ import annotations

from itertools import product

import numpy as np
from manim import *

BG_COLOR = "#0b0f1a"
F0_COLOR = "#3b82f6"
F1_COLOR = "#ef4444"
EDGE_COLOR = "#64748b"
ACCENT = "#f59e0b"
ACCENT2 = "#8b5cf6"
GOOD = "#22c55e"


def cube_vertex_coords(n: int, scale: float = 2.0) -> dict[tuple[int, ...], np.ndarray]:
    """Embed {0,1}^n in 3D. For n=3 it's the literal cube; for n=4 we use a tesseract projection."""
    coords: dict[tuple[int, ...], np.ndarray] = {}
    if n == 3:
        for v in product((0, 1), repeat=3):
            coords[v] = np.array([v[0], v[1], v[2]], dtype=float) * scale - scale / 2
    elif n == 4:
        basis = [
            np.array([1.0, 0.0, 0.0]),
            np.array([0.0, 1.0, 0.0]),
            np.array([0.0, 0.0, 1.0]),
            np.array([0.55, 0.55, 0.55]),
        ]
        for v in product((0, 1), repeat=4):
            p = sum(v[i] * basis[i] for i in range(4))
            coords[v] = p * scale - scale * 0.85
    return coords


def monotone_f_n3(v: tuple[int, ...]) -> int:
    """A simple monotone Boolean function on {0,1}^3: f = x1 OR (x2 AND x3)."""
    return int(v[0] or (v[1] and v[2]))


def hamming_neighbors(v: tuple[int, ...]) -> list[tuple[int, ...]]:
    return [tuple(b ^ (1 if i == k else 0) for i, b in enumerate(v)) for k in range(len(v))]


class InfluenceSensitivityTradeoff(ThreeDScene):
    def construct(self):
        self.camera.background_color = BG_COLOR
        self.scene1_boolean_cube()
        self.scene2_sensitivity()
        self.scene3_influence()
        self.scene4_tradeoff_question()
        self.scene5_polynomial_dnf()
        self.scene6_two_gadget_composition()
        self.scene7_the_limit()
        self.scene8_title_card()

    # ------------------------------------------------------------------ Scene 1
    def scene1_boolean_cube(self):
        self.set_camera_orientation(phi=65 * DEGREES, theta=-50 * DEGREES, zoom=0.95)

        header = Text("The Boolean Cube", font_size=40, color=ACCENT).to_corner(UL)
        subtitle = MathTex(r"\{0,1\}^3 \;\text{with monotone}\; f", font_size=32).next_to(
            header, DOWN, aligned_edge=LEFT, buff=0.15
        )
        self.add_fixed_in_frame_mobjects(header, subtitle)
        self.play(Write(header), FadeIn(subtitle))

        coords = cube_vertex_coords(3, scale=2.2)
        verts = {v: Sphere(radius=0.12).move_to(coords[v]) for v in coords}
        for v, sph in verts.items():
            color = F1_COLOR if monotone_f_n3(v) == 1 else F0_COLOR
            sph.set_color(color).set_opacity(0.95)

        edges = VGroup()
        for v in coords:
            for w in hamming_neighbors(v):
                if v < w:
                    edges.add(
                        Line3D(coords[v], coords[w], color=EDGE_COLOR, thickness=0.012)
                    )

        labels = VGroup()
        for v in coords:
            txt = Text("".join(str(b) for b in v), font_size=22, color=WHITE)
            txt.move_to(coords[v] + np.array([0.0, 0.0, 0.32]))
            labels.add(txt)

        self.play(Create(edges), run_time=1.6)
        self.play(*[GrowFromCenter(s) for s in verts.values()], run_time=1.2)
        self.add_fixed_orientation_mobjects(*labels)
        self.play(FadeIn(labels), run_time=0.8)
        self.begin_ambient_camera_rotation(rate=0.18)

        legend = VGroup(
            Dot(color=F0_COLOR, radius=0.12),
            Text("f(x) = 0", font_size=26, color=WHITE),
            Dot(color=F1_COLOR, radius=0.12),
            Text("f(x) = 1", font_size=26, color=WHITE),
        ).arrange(RIGHT, buff=0.25).to_corner(UR)
        self.add_fixed_in_frame_mobjects(legend)
        self.play(FadeIn(legend))

        # Monotone chain: 000 -> 100 -> 110 -> 111
        chain = [(0, 0, 0), (1, 0, 0), (1, 1, 0), (1, 1, 1)]
        arrows = VGroup()
        for a, b in zip(chain, chain[1:]):
            arrows.add(
                Arrow3D(coords[a], coords[b], color=ACCENT2, thickness=0.025)
            )
        mono_caption = MathTex(
            r"x \le y \;\Rightarrow\; f(x) \le f(y)", font_size=34, color=GOOD
        ).to_edge(DOWN)
        self.add_fixed_in_frame_mobjects(mono_caption)
        self.play(LaggedStartMap(Create, arrows, lag_ratio=0.5), Write(mono_caption))
        self.wait(2.4)
        self.stop_ambient_camera_rotation()
        self.play(
            FadeOut(arrows),
            FadeOut(mono_caption),
            FadeOut(legend),
            FadeOut(header),
            FadeOut(subtitle),
        )
        self.cube_state = dict(coords=coords, verts=verts, edges=edges, labels=labels)

    # ------------------------------------------------------------------ Scene 2
    def scene2_sensitivity(self):
        coords = self.cube_state["coords"]
        verts = self.cube_state["verts"]
        edges = self.cube_state["edges"]

        header = Text("Sensitivity", font_size=40, color=ACCENT).to_corner(UL)
        self.add_fixed_in_frame_mobjects(header)
        self.play(Write(header))

        x = (1, 0, 0)
        marker = Sphere(radius=0.2, color=ACCENT).move_to(coords[x]).set_opacity(0.7)
        self.play(FadeIn(marker, scale=1.4))

        neighbor_lines = VGroup()
        sensitive_flags = []
        for nbr in hamming_neighbors(x):
            flips = monotone_f_n3(nbr) != monotone_f_n3(x)
            ln = Line3D(coords[x], coords[nbr], color=ACCENT if flips else GREY, thickness=0.03)
            neighbor_lines.add(ln)
            sensitive_flags.append(flips)
        self.play(LaggedStartMap(Create, neighbor_lines, lag_ratio=0.3))

        flashes = []
        for ln, flips in zip(neighbor_lines, sensitive_flags):
            if flips:
                flashes.append(ShowPassingFlash(ln.copy().set_color(YELLOW), time_width=0.6))
        if flashes:
            self.play(*flashes, run_time=1.4)

        formula = MathTex(
            r"s(f) \;=\; \max_{x}\,\bigl|\{i : f(x)\neq f(x\oplus e_i)\}\bigr|",
            font_size=34,
        ).to_edge(DOWN)
        count = sum(sensitive_flags)
        count_text = MathTex(
            rf"\text{{sensitivity at }} x=100 \;=\; {count}", font_size=32, color=ACCENT
        ).next_to(formula, UP, buff=0.2)
        self.add_fixed_in_frame_mobjects(formula, count_text)
        self.play(Write(count_text), Write(formula))
        self.wait(2.5)
        self.play(
            FadeOut(marker),
            FadeOut(neighbor_lines),
            FadeOut(count_text),
            FadeOut(formula),
            FadeOut(header),
        )

    # ------------------------------------------------------------------ Scene 3
    def scene3_influence(self):
        coords = self.cube_state["coords"]
        edges = self.cube_state["edges"]

        header = Text("Influence", font_size=40, color=ACCENT).to_corner(UL)
        self.add_fixed_in_frame_mobjects(header)
        self.play(Write(header))

        axis_colors = [F1_COLOR, ACCENT, ACCENT2]
        axis_groups = []
        for i in range(3):
            group = VGroup()
            for v in coords:
                w = tuple(b ^ (1 if k == i else 0) for k, b in enumerate(v))
                if v < w:
                    flips = monotone_f_n3(v) != monotone_f_n3(w)
                    ln = Line3D(
                        coords[v], coords[w],
                        color=axis_colors[i] if flips else EDGE_COLOR,
                        thickness=0.03 if flips else 0.012,
                    )
                    group.add(ln)
            axis_groups.append(group)

        flip_counts = []
        for i in range(3):
            cnt = 0
            for v in coords:
                w = tuple(b ^ (1 if k == i else 0) for k, b in enumerate(v))
                if v < w and monotone_f_n3(v) != monotone_f_n3(w):
                    cnt += 1
            flip_counts.append(cnt)

        for i, group in enumerate(axis_groups):
            self.play(Create(group), run_time=0.9)

        formula = MathTex(
            r"\mathrm{Inf}(f) \;=\; \sum_{i=1}^{n}\Pr_{x\sim U}\!\bigl[f(x)\neq f(x\oplus e_i)\bigr]",
            font_size=32,
        ).to_edge(DOWN)
        total = sum(flip_counts) / 4.0
        per_axis = MathTex(
            rf"\mathrm{{Inf}}_1 + \mathrm{{Inf}}_2 + \mathrm{{Inf}}_3 \;=\; "
            rf"{flip_counts[0]/4:.2f}+{flip_counts[1]/4:.2f}+{flip_counts[2]/4:.2f} \;=\; {total:.2f}",
            font_size=30,
            color=GOOD,
        ).next_to(formula, UP, buff=0.2)
        self.add_fixed_in_frame_mobjects(formula, per_axis)
        self.play(Write(per_axis), Write(formula))
        self.wait(2.5)

        vert_group = VGroup(*self.cube_state["verts"].values())
        self.play(
            *[FadeOut(g) for g in axis_groups],
            FadeOut(vert_group),
            FadeOut(self.cube_state["edges"]),
            FadeOut(self.cube_state["labels"]),
            FadeOut(formula),
            FadeOut(per_axis),
            FadeOut(header),
        )

    # ------------------------------------------------------------------ Scene 4
    def scene4_tradeoff_question(self):
        self.set_camera_orientation(phi=0, theta=-90 * DEGREES, zoom=1.0)

        header = Text("The Tradeoff Question", font_size=40, color=ACCENT).to_edge(UP)
        question = MathTex(
            r"\text{For monotone } f, \;\;\mathrm{Inf}(f) \;\ge\; s(f)^{\alpha}.\;\;",
            r"\text{What is the largest } \alpha?",
            font_size=36,
        ).next_to(header, DOWN, buff=0.4)
        self.add_fixed_in_frame_mobjects(header, question)
        self.play(Write(header), Write(question))

        axes = Axes(
            x_range=[0, 6, 1], y_range=[0, 6, 1], x_length=6.2, y_length=4.2,
            tips=False, axis_config={"color": EDGE_COLOR},
        ).shift(DOWN * 0.6)
        x_lab = MathTex(r"\log s(f)", font_size=28).next_to(axes.x_axis, RIGHT, buff=0.15)
        y_lab = MathTex(r"\log \mathrm{Inf}(f)", font_size=28).next_to(axes.y_axis, UP, buff=0.15)

        trivial = axes.plot(lambda x: x, x_range=[0.1, 5.9], color=GREY)
        trivial_lab = MathTex(r"\alpha=1\;\text{(trivial)}", font_size=24, color=GREY).next_to(
            axes.c2p(5.4, 5.4), UR, buff=0.05
        )
        os_line = axes.plot(lambda x: 0.6115 * x + 0.2, x_range=[0.1, 5.9], color=ACCENT2)
        os_lab = MathTex(
            r"\alpha\approx 0.6115\;\text{O'Donnell--Servedio (2007)}",
            font_size=22, color=ACCENT2,
        ).next_to(axes.c2p(5.5, 0.6115 * 5.5 + 0.2), RIGHT, buff=0.05)
        new_line = axes.plot(lambda x: (2 / 3) * x + 0.1, x_range=[0.1, 5.9], color=GOOD)
        new_lab = MathTex(r"\alpha = \tfrac{2}{3}\;\text{NEW}", font_size=26, color=GOOD).next_to(
            axes.c2p(5.5, (2 / 3) * 5.5 + 0.1), RIGHT, buff=0.05
        )

        self.add_fixed_in_frame_mobjects(axes, x_lab, y_lab)
        self.play(Create(axes), Write(x_lab), Write(y_lab))
        self.add_fixed_in_frame_mobjects(trivial, trivial_lab)
        self.play(Create(trivial), FadeIn(trivial_lab))
        self.add_fixed_in_frame_mobjects(os_line, os_lab)
        self.play(Create(os_line), FadeIn(os_lab))
        self.add_fixed_in_frame_mobjects(new_line, new_lab)
        self.play(Create(new_line), FadeIn(new_lab))
        self.wait(2.0)
        self.play(
            FadeOut(VGroup(header, question, axes, x_lab, y_lab, trivial, trivial_lab,
                           os_line, os_lab, new_line, new_lab))
        )

    # ------------------------------------------------------------------ Scene 5
    def scene5_polynomial_dnf(self):
        header = Text("Construction: Polynomial-Graph DNFs", font_size=38, color=ACCENT).to_edge(UP)
        self.add_fixed_in_frame_mobjects(header)
        self.play(Write(header))

        p = 7
        circle = Circle(radius=1.4, color=EDGE_COLOR).shift(LEFT * 4.0)
        field_dots = VGroup()
        for k in range(p):
            ang = 2 * PI * k / p + PI / 2
            d = Dot(circle.point_at_angle(ang), color=ACCENT, radius=0.07)
            lab = MathTex(str(k), font_size=22).next_to(d, OUT * 0 + UP * 0.0, buff=0.12)
            lab.move_to(circle.point_at_angle(ang) * 1.18)
            field_dots.add(VGroup(d, lab))
        field_label = MathTex(r"\mathbb{F}=\mathbb{Z}/7\mathbb{Z}", font_size=30).next_to(circle, DOWN)
        self.add_fixed_in_frame_mobjects(circle, field_dots, field_label)
        self.play(Create(circle), FadeIn(field_dots), Write(field_label))

        grid_origin = RIGHT * 1.6 + DOWN * 0.4
        cell = 0.42
        grid = VGroup()
        for i in range(p):
            for j in range(p):
                sq = Square(side_length=cell, color=EDGE_COLOR, stroke_width=1)
                sq.move_to(grid_origin + np.array([i * cell, j * cell, 0]) - np.array([3 * cell, 3 * cell, 0]))
                grid.add(sq)
        x_axis_lab = MathTex(r"t", font_size=26).next_to(grid, RIGHT, buff=0.2)
        y_axis_lab = MathTex(r"P(t)", font_size=26).next_to(grid, UP, buff=0.2)
        self.add_fixed_in_frame_mobjects(grid, x_axis_lab, y_axis_lab)
        self.play(Create(grid), Write(x_axis_lab), Write(y_axis_lab))

        def poly_dots(coeffs, color):
            g = VGroup()
            for t in range(p):
                val = sum(c * (t ** k) for k, c in enumerate(coeffs)) % p
                pt = grid_origin + np.array([t * cell, val * cell, 0]) - np.array([3 * cell, 3 * cell, 0])
                g.add(Dot(pt, color=color, radius=0.09))
            return g

        polys = [
            ([1, 2], F1_COLOR),
            ([3, 1, 1], ACCENT2),
            ([0, 4, 2], GOOD),
        ]
        clause_text = MathTex(
            r"C_P \;=\; \bigwedge_{t\in\mathbb{F}} x_{(t,\,P(t))}",
            font_size=30,
        ).to_edge(DOWN, buff=1.2)
        dnf_text = MathTex(
            r"H \;=\; \bigvee_{P\in\mathcal{P}_{<d}} C_P",
            font_size=30, color=GOOD,
        ).next_to(clause_text, DOWN, buff=0.2)
        self.add_fixed_in_frame_mobjects(clause_text, dnf_text)

        for coeffs, color in polys:
            d = poly_dots(coeffs, color)
            self.add_fixed_in_frame_mobjects(d)
            self.play(LaggedStartMap(FadeIn, d, lag_ratio=0.08, run_time=1.0))
        self.play(Write(clause_text))
        self.play(Write(dnf_text))
        self.wait(2.0)
        self.play(*[FadeOut(m) for m in self.mobjects])

    # ------------------------------------------------------------------ Scene 6
    def scene6_two_gadget_composition(self):
        header = Text("Two-Gadget Composition", font_size=40, color=ACCENT).to_edge(UP)
        self.add_fixed_in_frame_mobjects(header)
        self.play(Write(header))

        boxB = RoundedRectangle(width=2.6, height=1.4, corner_radius=0.15, color=ACCENT2).shift(DOWN * 1.4)
        lblB = MathTex(r"B^{*}\;\text{(dualized)}", font_size=30, color=ACCENT2).move_to(boxB)
        boxT = RoundedRectangle(width=2.6, height=1.4, corner_radius=0.15, color=F1_COLOR).shift(UP * 1.0)
        lblT = MathTex(r"T", font_size=34, color=F1_COLOR).move_to(boxT)

        inputs = VGroup(*[
            Arrow(start=DOWN * 3.2 + LEFT * (1.0 - 0.5 * k), end=boxB.get_bottom() + LEFT * (0.6 - 0.3 * k),
                  buff=0.05, color=GREY)
            for k in range(5)
        ])
        connector = Arrow(boxB.get_top(), boxT.get_bottom(), buff=0.05, color=WHITE)
        out = Arrow(boxT.get_top(), boxT.get_top() + UP * 0.7, buff=0.05, color=GOOD)

        self.add_fixed_in_frame_mobjects(boxB, lblB, boxT, lblT, inputs, connector, out)
        self.play(LaggedStartMap(Create, inputs, lag_ratio=0.1))
        self.play(Create(boxB), Write(lblB))
        self.play(Create(connector))
        self.play(Create(boxT), Write(lblT))
        self.play(Create(out))

        bounds = VGroup(
            MathTex(r"\mathrm{Inf}(H) \;\ge\; c\cdot Q^{2}", font_size=32, color=GOOD),
            MathTex(r"s(H) \;\le\; Q^{3}", font_size=32, color=ACCENT),
            MathTex(
                r"\frac{\log \mathrm{Inf}(H)}{\log s(H)} \;\ge\; \frac{\log Q^{2}}{\log Q^{3}} \;=\; \tfrac{2}{3}",
                font_size=34, color=WHITE,
            ),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.25).to_edge(RIGHT, buff=0.4)
        self.add_fixed_in_frame_mobjects(bounds)
        self.play(LaggedStartMap(Write, bounds, lag_ratio=0.4))
        self.wait(2.5)
        self.play(*[FadeOut(m) for m in self.mobjects])

    # ------------------------------------------------------------------ Scene 7
    def scene7_the_limit(self):
        header = Text("The Limit: Q_k → ∞", font_size=40, color=ACCENT).to_edge(UP)
        self.add_fixed_in_frame_mobjects(header)
        self.play(Write(header))

        axes = Axes(
            x_range=[0, 6, 1], y_range=[0, 4.5, 1], x_length=7.2, y_length=4.2,
            tips=False, axis_config={"color": EDGE_COLOR},
        ).shift(DOWN * 0.4)
        x_lab = MathTex(r"\log s(H_k)", font_size=28).next_to(axes.x_axis, RIGHT, buff=0.15)
        y_lab = MathTex(r"\log \mathrm{Inf}(H_k)", font_size=28).next_to(axes.y_axis, UP, buff=0.15)
        target = axes.plot(lambda x: (2 / 3) * x, x_range=[0.1, 5.9], color=GOOD)
        target_lab = MathTex(r"y = \tfrac{2}{3}\,x", font_size=26, color=GOOD).next_to(
            axes.c2p(5.5, (2 / 3) * 5.5), UP, buff=0.1
        )
        self.add_fixed_in_frame_mobjects(axes, x_lab, y_lab, target, target_lab)
        self.play(Create(axes), Write(x_lab), Write(y_lab))
        self.play(Create(target), FadeIn(target_lab))

        primes = [3, 5, 7, 11, 13, 17, 23]
        dots = VGroup()
        for i, q in enumerate(primes):
            sx = 1.0 + i * 0.7
            offset = 0.6 / (i + 1.0)
            sy = (2 / 3) * sx + offset
            d = Dot(axes.c2p(sx, sy), color=ACCENT, radius=0.08)
            lab = MathTex(f"Q={q}", font_size=20, color=ACCENT).next_to(d, UR, buff=0.05)
            dots.add(VGroup(d, lab))
        self.add_fixed_in_frame_mobjects(dots)
        self.play(LaggedStartMap(FadeIn, dots, lag_ratio=0.25, run_time=2.0))

        final = MathTex(
            r"\liminf_{k\to\infty}\;\frac{\log \mathrm{Inf}(H_k)}{\log s(H_k)} \;\ge\; \tfrac{2}{3}",
            font_size=38, color=GOOD,
        ).to_edge(DOWN, buff=0.8)
        verified = Text(
            "Fully verified in Lean 4  -  no sorry, no custom axioms",
            font_size=26, color=ACCENT,
        ).next_to(final, DOWN, buff=0.2)
        self.add_fixed_in_frame_mobjects(final, verified)
        self.play(Write(final))
        self.play(FadeIn(verified, shift=UP * 0.2))
        for _ in range(2):
            self.play(Indicate(verified, color=GOOD, scale_factor=1.05), run_time=0.6)
        self.wait(1.5)
        self.play(*[FadeOut(m) for m in self.mobjects])

    # ------------------------------------------------------------------ Scene 8
    def scene8_title_card(self):
        title = Text(
            "Influence-Sensitivity Tradeoff",
            font_size=52, color=WHITE,
        )
        subtitle1 = Text(
            "for Monotone Boolean Functions",
            font_size=40, color=WHITE,
        ).next_to(title, DOWN, buff=0.25)
        subtitle2 = Text(
            "Achieving the 2/3 Exponent",
            font_size=36, color=ACCENT,
        ).next_to(subtitle1, DOWN, buff=0.6)
        credit = Text(
            "improving O'Donnell-Servedio (2007)   .   verified in Lean 4",
            font_size=22, color=EDGE_COLOR,
        ).next_to(subtitle2, DOWN, buff=0.7)
        group = VGroup(title, subtitle1, subtitle2, credit).move_to(ORIGIN)
        self.add_fixed_in_frame_mobjects(group)
        self.play(FadeIn(title, shift=UP * 0.2))
        self.play(FadeIn(subtitle1))
        self.play(Write(subtitle2))
        self.play(FadeIn(credit))
        self.wait(2.5)
        self.play(FadeOut(group))
