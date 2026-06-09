from manim import *
import numpy as np

BG = "#F4EFE3"
INK = "#1F2933"
MUTED = "#6B6258"
TEAL = "#38A3A5"
BLUE = "#22577A"
GOLD = "#D9A441"
RED = "#C8553D"
VIOLET = "#6D5BD0"
GREEN = "#497D56"
CARD = "#FFF8EA"
CARD_SOFT = "#FBF1DA"
BORDER = "#C8BFAE"
GRID = "#D8CCB8"
MONO = "DejaVu Sans Mono"


class Episode00ArgumentMap(ThreeDScene):
    """Episode 0: a readable 60-90 second roadmap for the full paper explainer."""

    def construct(self):
        self.camera.background_color = BG
        self.set_camera_orientation(phi=62 * DEGREES, theta=-46 * DEGREES, zoom=0.92)

        title = Text(
            "Casimir Self-Interaction Energy Density\nof Quantum Electrodynamic Fields",
            font=MONO,
            font_size=34,
            color=INK,
            weight=BOLD,
            line_spacing=0.88,
        ).to_edge(UP, buff=0.38)
        subtitle = Text(
            "Episode 0 — a roadmap before the equations begin",
            font=MONO,
            font_size=20,
            color=MUTED,
        ).next_to(title, DOWN, buff=0.20)
        source = Text(
            "Phys. Rev. Lett. 130, 041601  •  DOI: 10.1103/PhysRevLett.130.041601",
            font=MONO,
            font_size=15,
            color=MUTED,
        ).to_edge(DOWN, buff=0.28)
        self.add_fixed_in_frame_mobjects(title, subtitle, source)
        self.play(FadeIn(title, shift=0.12 * UP), FadeIn(subtitle), FadeIn(source), run_time=1.6)
        self.wait(1.4)

        caveat = self._wide_card(
            "MODEL WALKTHROUGH",
            "We will visualize the paper's proposed chain of approximations — not treat the result as settled proof of dark energy.",
            eyebrow_color=GOLD,
        ).to_edge(DOWN, buff=0.30)
        self.add_fixed_in_frame_mobjects(caveat)
        self.play(FadeOut(source), FadeIn(caveat, shift=0.18 * UP), run_time=1.1)
        self.wait(2.1)
        self.play(FadeOut(caveat), run_time=0.65)

        # Stage 1: empty field volume.
        volume_group = self._vacuum_volume()
        field_caption = self._caption("Start with empty space: the QED vacuum is not visually blank.")
        self.add_fixed_in_frame_mobjects(field_caption)
        self.play(FadeIn(field_caption), Create(volume_group[0]), FadeIn(volume_group[1]), run_time=2.2)
        self.begin_ambient_camera_rotation(rate=0.018)
        self.wait(2.0)
        self.stop_ambient_camera_rotation()
        self.play(FadeOut(field_caption), run_time=0.5)

        # Stage 2: transient dipoles flash and average into texture.
        dipoles = self._dipoles()
        dipole_caption = self._caption("Transient pair fluctuations become tiny polarizable dipoles — appearing, separating, disappearing.")
        self.add_fixed_in_frame_mobjects(dipole_caption)
        self.play(FadeIn(dipole_caption), run_time=0.4)
        self.play(LaggedStart(*[FadeIn(d, scale=0.65) for d in dipoles], lag_ratio=0.13), run_time=2.5)
        self.wait(0.9)
        self.play(LaggedStart(*[d.animate.scale(1.28).set_opacity(0.58) for d in dipoles], lag_ratio=0.08), run_time=1.3)
        self.play(LaggedStart(*[FadeOut(d, scale=1.55) for d in dipoles], lag_ratio=0.08), FadeOut(dipole_caption), run_time=2.0)

        density_cloud = self._density_cloud()
        density_card = self._formula_card(
            "working object",
            r"\alpha_F(\mathbf r)",
            "a coarse-grained polarizability density for the field",
            accent=TEAL,
        ).to_corner(UL, buff=0.38)
        self.add_fixed_in_frame_mobjects(density_card)
        self.play(FadeIn(density_cloud, scale=0.8), FadeIn(density_card, shift=0.15 * RIGHT), run_time=1.8)
        self.wait(2.1)

        # Stage 3: build the central roadmap as large front-facing cards first.
        roadmap_intro = self._wide_card(
            "THE PAPER'S ARGUMENT CHAIN",
            "Each later episode will open one of these gates, show the equation, then turn the symbols into geometry.",
            eyebrow_color=BLUE,
        ).to_edge(DOWN, buff=0.30)
        self.add_fixed_in_frame_mobjects(roadmap_intro)
        self.play(FadeIn(roadmap_intro, shift=0.18 * UP), run_time=0.9)
        self.wait(1.8)
        self.play(FadeOut(roadmap_intro), run_time=0.55)

        # Clear the dense field volume before the long roadmap section. This keeps
        # the production render fast while preserving the opening 3D field beat.
        self.play(FadeOut(density_card), FadeOut(density_cloud), FadeOut(volume_group), run_time=0.9)

        nodes, connectors = self._roadmap_nodes()
        node_cards = self._roadmap_cards()
        self.play(Create(connectors), LaggedStart(*[GrowFromCenter(n) for n in nodes], lag_ratio=0.13), run_time=2.6)
        self.add_fixed_in_frame_mobjects(node_cards)
        self.play(LaggedStart(*[FadeIn(c, shift=0.10 * UP) for c in node_cards], lag_ratio=0.10), run_time=2.8)
        self.wait(1.0)

        # Stage 4: spotlight every gate, one at a time, with a large readable card.
        gates = [
            ("1", "vacuum fluctuations", "flashes of transient e-/e+ dipoles", BLUE),
            ("2", "polarizability density", "replace microscopic noise by α_F(r)", TEAL),
            ("3", "Casimir self-interaction", "response fields interact with retarded dipole bridges", RED),
            ("4", "pair + lattice model", "count many pairwise interactions with a geometry factor", GOLD),
            ("5", "spherical shell model", "replace lattice uncertainty by isotropic shells", VIOLET),
            ("6", "Λ-scale density", "compare the magnitude with dark-energy-scale density", RED),
        ]
        for i, (number, head, body, color) in enumerate(gates):
            card = self._gate_card(number, head, body, color).to_edge(DOWN, buff=0.26)
            self.add_fixed_in_frame_mobjects(card)
            self.play(nodes[i].animate.scale(1.45), FadeIn(card, shift=0.12 * UP), run_time=0.85)
            self.wait(1.35)
            self.play(nodes[i].animate.scale(1 / 1.45), FadeOut(card), run_time=0.55)

        self.begin_ambient_camera_rotation(rate=0.025)
        orbit_caption = self._caption("The whole route is spatial: local fluctuations → coarse-grained response → accumulated self-interaction.")
        self.add_fixed_in_frame_mobjects(orbit_caption)
        self.play(FadeIn(orbit_caption), run_time=0.5)
        self.wait(4.0)
        self.stop_ambient_camera_rotation()
        self.play(FadeOut(orbit_caption), run_time=0.45)

        # Stage 5: destination formula shown as destination, not a proof.
        destination = self._destination_card().to_edge(DOWN, buff=0.24)
        self.add_fixed_in_frame_mobjects(destination)
        self.play(FadeOut(node_cards), FadeIn(destination, shift=0.25 * UP), run_time=1.2)
        self.wait(3.2)

        caution = self._wide_card(
            "READING RULE FOR THE SERIES",
            "Formula first, geometry second, caveat always visible. Every equation gets a readable card before the camera moves.",
            eyebrow_color=RED,
        ).to_edge(DOWN, buff=0.30)
        self.add_fixed_in_frame_mobjects(caution)
        self.play(FadeOut(destination), FadeIn(caution, shift=0.15 * UP), run_time=0.9)
        self.wait(2.2)
        self.play(FadeOut(caution), run_time=0.55)

        # Stage 6: zoom into first gate for Episode 1.
        next_card = self._wide_card(
            "NEXT: EPISODE 1",
            "We zoom into the first gate: how transient pair fluctuations are represented as a polarizability-density field.",
            eyebrow_color=TEAL,
        ).to_edge(DOWN, buff=0.30)
        self.add_fixed_in_frame_mobjects(next_card)
        self.play(FadeIn(next_card), nodes[0].animate.scale(1.75), nodes[0].animate.set_opacity(1.0), run_time=1.1)
        self.move_camera(phi=66 * DEGREES, theta=-63 * DEGREES, zoom=1.23, run_time=2.4)
        self.wait(2.1)

        self.play(
            FadeOut(next_card),
            FadeOut(nodes),
            FadeOut(connectors),
            FadeOut(volume_group),
            FadeOut(density_cloud),
            FadeOut(title),
            FadeOut(subtitle),
            run_time=1.3,
        )
        end = Text("Episode 1 begins with transient dipoles.", font=MONO, font_size=30, color=INK, weight=BOLD)
        self.add_fixed_in_frame_mobjects(end)
        self.play(FadeIn(end, scale=0.95), run_time=0.8)
        self.wait(1.4)
        self.play(FadeOut(end), run_time=0.6)

    def _vacuum_volume(self):
        cube = Cube(side_length=4.6, fill_opacity=0.035, fill_color=TEAL, stroke_color=BLUE, stroke_opacity=0.26)
        grid = VGroup()
        for z in np.linspace(-2.3, 2.3, 6):
            grid.add(Line3D(start=[-2.3, -2.3, z], end=[2.3, -2.3, z], color=GRID, thickness=0.005))
            grid.add(Line3D(start=[-2.3, 2.3, z], end=[2.3, 2.3, z], color=GRID, thickness=0.005))
            grid.add(Line3D(start=[-2.3, z, -2.3], end=[2.3, z, -2.3], color=GRID, thickness=0.005))
            grid.add(Line3D(start=[-2.3, z, 2.3], end=[2.3, z, 2.3], color=GRID, thickness=0.005))
        axes = VGroup(
            Arrow3D(start=[-2.7, 0, 0], end=[2.7, 0, 0], color=BORDER, thickness=0.01),
            Arrow3D(start=[0, -2.7, 0], end=[0, 2.7, 0], color=BORDER, thickness=0.01),
            Arrow3D(start=[0, 0, -2.7], end=[0, 0, 2.7], color=BORDER, thickness=0.01),
        )
        return VGroup(cube, grid, axes)

    def _dipoles(self):
        dipoles = VGroup()
        positions = [
            np.array([-1.55, -0.95, 0.52]),
            np.array([0.62, -1.20, -0.40]),
            np.array([1.42, 0.42, 0.92]),
            np.array([-0.32, 1.32, -0.82]),
            np.array([-1.20, 0.92, 1.30]),
            np.array([1.00, 1.12, -1.15]),
            np.array([-1.65, -0.05, -1.10]),
        ]
        directions = [RIGHT, 0.75 * RIGHT + 0.20 * UP, LEFT, 0.65 * RIGHT - 0.25 * UP, RIGHT, UP + 0.2 * RIGHT, LEFT + 0.3 * UP]
        for pos, direction in zip(positions, directions):
            d = direction / np.linalg.norm(direction)
            e_minus = Sphere(radius=0.085, color=BLUE, fill_opacity=0.95).move_to(pos - 0.19 * d)
            e_plus = Sphere(radius=0.085, color=RED, fill_opacity=0.95).move_to(pos + 0.19 * d)
            link = Line3D(pos - 0.19 * d, pos + 0.19 * d, color=GOLD, thickness=0.020)
            halo = Sphere(radius=0.42, color=TEAL, fill_opacity=0.045, stroke_opacity=0.10).move_to(pos)
            dipoles.add(VGroup(halo, link, e_minus, e_plus))
        return dipoles

    def _density_cloud(self):
        cloud = VGroup()
        for radius, opacity in [(1.2, 0.040), (1.65, 0.028), (2.05, 0.018)]:
            cloud.add(Sphere(radius=radius, color=TEAL, fill_opacity=opacity, stroke_opacity=0.035))
        shell = Torus(major_radius=1.95, minor_radius=0.018, color=TEAL, fill_opacity=0.22).rotate(PI / 2, axis=RIGHT)
        return VGroup(cloud, shell)

    def _roadmap_nodes(self):
        colors = [BLUE, TEAL, RED, GOLD, VIOLET, RED]
        xs = np.linspace(-5.0, 5.0, len(colors))
        nodes = VGroup()
        for k, (x, color) in enumerate(zip(xs, colors)):
            node = Sphere(radius=0.22, color=color, fill_opacity=0.84).move_to([x, 0.0, 0.32 * np.sin(0.9 * x)])
            ring = Torus(major_radius=0.43, minor_radius=0.012, color=color, fill_opacity=0.52).move_to(node.get_center())
            number = Text(str(k + 1), font=MONO, font_size=18, color=INK, weight=BOLD).move_to(node.get_center() + 0.05 * OUT)
            nodes.add(VGroup(node, ring, number))
        connectors = VGroup()
        for a, b in zip(nodes[:-1], nodes[1:]):
            connectors.add(Line3D(a[0].get_center(), b[0].get_center(), color=MUTED, thickness=0.018))
        return nodes, connectors

    def _roadmap_cards(self):
        labels = [
            ("1  vacuum\nfluctuations", BLUE),
            ("2  polarizability\ndensity", TEAL),
            ("3  Casimir self-\ninteraction", RED),
            ("4  pair + lattice\nmodel", GOLD),
            ("5  spherical shell\nmodel", VIOLET),
            ("6  Lambda-scale\ndensity", RED),
        ]
        x_positions = np.linspace(-5.15, 5.15, len(labels))
        cards = VGroup()
        for x, (label, color) in zip(x_positions, labels):
            box = RoundedRectangle(corner_radius=0.12, width=1.98, height=0.86, color=color, fill_color=CARD, fill_opacity=0.96, stroke_width=1.8)
            txt = Text(label, font=MONO, font_size=15, color=INK, line_spacing=0.82, weight=BOLD)
            cards.add(VGroup(box, txt).move_to([x, -2.92, 0]))
        return cards

    def _caption(self, body):
        box = RoundedRectangle(corner_radius=0.15, width=10.6, height=0.62, color=BORDER, fill_color=CARD_SOFT, fill_opacity=0.94, stroke_width=1.2)
        text = Text(body, font=MONO, font_size=17, color=INK)
        return VGroup(box, text).to_edge(DOWN, buff=0.36)

    def _wide_card(self, eyebrow, body, eyebrow_color=GOLD):
        box = RoundedRectangle(corner_radius=0.18, width=11.15, height=1.20, color=BORDER, fill_color=CARD, fill_opacity=0.97, stroke_width=1.8)
        head = Text(eyebrow, font=MONO, font_size=17, color=eyebrow_color, weight=BOLD).move_to(box.get_center() + 0.34 * UP)
        text = Text(body, font=MONO, font_size=18, color=INK, line_spacing=0.85).move_to(box.get_center() - 0.18 * UP)
        return VGroup(box, head, text)

    def _formula_card(self, eyebrow, formula, body, accent=TEAL):
        box = RoundedRectangle(corner_radius=0.16, width=4.25, height=1.70, color=accent, fill_color=CARD, fill_opacity=0.97, stroke_width=1.8)
        head = Text(eyebrow.upper(), font=MONO, font_size=14, color=accent, weight=BOLD).move_to(box.get_center() + 0.56 * UP)
        eq = MathTex(formula, font_size=34, color=INK).move_to(box.get_center() + 0.04 * UP)
        body_text = Text(body, font=MONO, font_size=12, color=MUTED).move_to(box.get_center() - 0.58 * UP)
        return VGroup(box, head, eq, body_text)

    def _gate_card(self, number, head, body, color):
        box = RoundedRectangle(corner_radius=0.18, width=10.6, height=1.28, color=color, fill_color=CARD, fill_opacity=0.97, stroke_width=2.0)
        badge = Circle(radius=0.34, color=color, fill_color=color, fill_opacity=0.88).move_to(box.get_left() + 0.58 * RIGHT)
        n = Text(number, font=MONO, font_size=22, color=WHITE, weight=BOLD).move_to(badge)
        h = Text(head.upper(), font=MONO, font_size=21, color=color, weight=BOLD).move_to(box.get_center() + 0.26 * UP)
        b = Text(body, font=MONO, font_size=18, color=INK).move_to(box.get_center() - 0.26 * UP)
        return VGroup(box, badge, n, h, b)

    def _destination_card(self):
        box = RoundedRectangle(corner_radius=0.18, width=11.05, height=2.05, color=BORDER, fill_color=CARD, fill_opacity=0.98, stroke_width=1.9)
        head = Text("DESTINATION FORMULA — EARNED LATER", font=MONO, font_size=17, color=GOLD, weight=BOLD).move_to(box.get_center() + 0.70 * UP)
        eq = MathTex(
            r"\bar{E}_{\mathrm{SIE}}=-\frac{1}{4}\alpha_{\mathrm{fsc}}^{31/3}E_h a_0^{-3}",
            font_size=35,
            color=INK,
        ).move_to(box.get_center() + 0.08 * UP)
        val = MathTex(
            r"|\bar{E}_{\mathrm{SIE}}|=2.07\times10^{-23}\ \mathrm{Ha/Bohr^3}",
            font_size=30,
            color=RED,
        ).move_to(box.get_center() - 0.56 * UP)
        return VGroup(box, head, eq, val)
