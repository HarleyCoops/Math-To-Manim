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
CARD = "#FFF8EA"
CARD_SOFT = "#FBF1DA"
BORDER = "#C8BFAE"
GRID = "#D8CCB8"
MONO = "DejaVu Sans Mono"


class Episode01VacuumDipoles(ThreeDScene):
    """Episode 1: transient QED pair fluctuations as a polarizability-density model."""

    def construct(self):
        self.camera.background_color = BG
        self.set_camera_orientation(phi=62 * DEGREES, theta=-48 * DEGREES, zoom=0.95)

        title = Text(
            "Episode 1 — Vacuum Fluctuations as Polarizable Dipoles",
            font=MONO,
            font_size=28,
            color=INK,
            weight=BOLD,
        ).to_edge(UP, buff=0.34)
        subtitle = Text(
            "Every symbol gets a geometry before the Casimir energy equation begins",
            font=MONO,
            font_size=17,
            color=MUTED,
        ).next_to(title, DOWN, buff=0.18)
        self.add_fixed_in_frame_mobjects(title, subtitle)
        self.play(FadeIn(title, shift=0.10 * UP), FadeIn(subtitle), run_time=1.2)
        self.wait(1.2)

        volume = self._vacuum_volume()
        caption = self._caption_lines([
            "Start with empty space: no material medium is being drawn.",
            "The only visible structure is a low-opacity bookkeeping volume for field response.",
        ])
        self.add_fixed_in_frame_mobjects(caption)
        self.play(Create(volume[0]), FadeIn(volume[1]), FadeIn(caption), run_time=1.9)
        self.wait(3.0)
        self.play(FadeOut(caption), run_time=0.45)

        dipoles = self._dipoles()
        pulse_caption = self._caption_lines([
            "Transient pair flashes: red/blue polarity separates briefly.",
            "The line is a dipole moment cue, not a permanent particle track.",
        ])
        self.add_fixed_in_frame_mobjects(pulse_caption)
        self.play(FadeIn(pulse_caption), run_time=0.5)
        for batch in [dipoles[:3], dipoles[3:6], dipoles[6:]]:
            self.play(LaggedStart(*[FadeIn(d, scale=0.65) for d in batch], lag_ratio=0.16), run_time=1.05)
            self.play(LaggedStart(*[d.animate.scale(1.18).set_opacity(0.50) for d in batch], lag_ratio=0.08), run_time=0.7)
            self.play(LaggedStart(*[FadeOut(d, scale=1.45) for d in batch], lag_ratio=0.08), run_time=0.8)
        self.wait(0.8)
        self.play(FadeOut(pulse_caption), run_time=0.45)

        definition = self._definition_card().to_edge(DOWN, buff=0.30)
        self.add_fixed_in_frame_mobjects(definition)
        self.play(FadeIn(definition, shift=0.20 * UP), run_time=1.0)
        self.wait(4.0)

        symbol_steps = [
            (r"\boldsymbol{\mathcal E}(\mathbf r',t')", "FIELD IMPULSE", "A localized electric-field kick enters at source point r' and time t'.", GOLD),
            (r"\boldsymbol{\mathcal P}(\mathbf r,t)", "POLARIZATION RESPONSE", "The vacuum model records a delayed polarization response at r and time t.", TEAL),
            (r"\mathbf r'\rightarrow\mathbf r", "TWO POINTS", "The tensor remembers both source and response locations, not just one local value.", VIOLET),
            (r"t-t'", "RETARDATION", "The response is not instantaneous; the time separation becomes a causal ripple.", RED),
            (r"\delta\boldsymbol{\mathcal P}/\delta\boldsymbol{\mathcal E}", "RESPONSE RATIO", "Polarizability means: how much polarization changes per applied field impulse.", BLUE),
        ]

        source_point = Sphere(radius=0.11, color=GOLD, fill_opacity=0.95).move_to(np.array([-1.35, -0.55, 0.20]))
        response_point = Sphere(radius=0.11, color=TEAL, fill_opacity=0.95).move_to(np.array([1.15, 0.55, 0.70]))
        bridge = Line3D(source_point.get_center(), response_point.get_center(), color=GOLD, thickness=0.018)
        ripple = Torus(major_radius=0.45, minor_radius=0.012, color=TEAL, fill_opacity=0.35).move_to(response_point.get_center())
        delay_ring = Torus(major_radius=0.78, minor_radius=0.010, color=RED, fill_opacity=0.18).move_to(response_point.get_center())
        response_arrow = Arrow3D(
            start=source_point.get_center(),
            end=response_point.get_center(),
            color=GOLD,
            thickness=0.025,
            height=0.15,
            base_radius=0.045,
        )

        for index, (formula, heading, body, accent) in enumerate(symbol_steps):
            card = self._symbol_card(formula, heading, body, accent).to_corner(UL, buff=0.34)
            self.add_fixed_in_frame_mobjects(card)
            self.play(FadeIn(card, shift=0.12 * RIGHT), run_time=0.55)
            if index == 0:
                self.play(FadeIn(source_point), GrowFromCenter(self._field_pulse(source_point.get_center())), run_time=1.0)
            elif index == 1:
                self.play(FadeIn(response_point), GrowFromCenter(ripple), run_time=1.0)
            elif index == 2:
                self.play(Create(bridge), Create(response_arrow), run_time=1.1)
            elif index == 3:
                self.play(GrowFromCenter(delay_ring), delay_ring.animate.scale(1.18).set_opacity(0.20), run_time=1.1)
            else:
                ratio_brace = self._ratio_geometry(source_point.get_center(), response_point.get_center())
                self.play(FadeIn(ratio_brace), run_time=0.9)
                self.play(FadeOut(ratio_brace), run_time=0.5)
            self.wait(2.2)
            self.play(FadeOut(card), run_time=0.35)

        freeze_card = self._wide_card_lines(
            "THE TENSOR IS TOO DETAILED FOR THE NEXT APPROXIMATION",
            ["It tracks source, response, tensor direction, and time.", "The paper then coarse-grains this into a static intrinsic density."],
            BLUE,
        ).to_edge(DOWN, buff=0.30)
        self.add_fixed_in_frame_mobjects(freeze_card)
        self.play(FadeOut(definition), FadeIn(freeze_card), run_time=0.75)
        self.wait(3.4)
        self.play(FadeOut(freeze_card), run_time=0.45)

        model_1 = self._wide_card_lines(
            "MODEL STEP 1 — SPATIAL COARSE GRAINING",
            ["Average over source locations r'.", "The many tiny response bridges become one smooth field texture."],
            GOLD,
        ).to_edge(DOWN, buff=0.30)
        web = self._response_web(source_point.get_center(), response_point.get_center())
        self.add_fixed_in_frame_mobjects(model_1)
        self.play(FadeIn(model_1), FadeIn(web), run_time=1.0)
        self.wait(3.0)

        model_2 = self._wide_card_lines(
            "MODEL STEP 2 — TENSOR TRACE + STATIC LIMIT",
            ["Trace tensor components into a scalar response scale.", "Then take the zero-frequency/static limit for alpha_F(r)."],
            GOLD,
        ).to_edge(DOWN, buff=0.30)
        density = self._density_texture()
        alpha_card = self._formula_card(r"\alpha_{\rm F}(\mathbf r)", "intrinsic polarizability density", TEAL).to_corner(UR, buff=0.34)
        self.add_fixed_in_frame_mobjects(model_2, alpha_card)
        self.play(FadeOut(model_1), FadeIn(model_2), ReplacementTransform(web, density), FadeIn(alpha_card), run_time=1.8)
        self.wait(3.2)

        caveat_1 = self._wide_card_lines(
            "HONEST CAVEAT",
            ["Finite zero-field polarizability density is a working hypothesis.", "The paper uses it as a model assumption, not as settled experimental fact."],
            RED,
        ).to_edge(DOWN, buff=0.30)
        self.add_fixed_in_frame_mobjects(caveat_1)
        self.play(FadeOut(model_2), FadeIn(caveat_1), run_time=0.8)
        self.wait(4.0)

        caveat_2 = self._wide_card_lines(
            "WHAT THE VISUAL MODEL MEANS",
            ["No external field is applied in the final picture.", "Faint zero-point fluctuations average into a soft teal response density."],
            TEAL,
        ).to_edge(DOWN, buff=0.30)
        persistent_dipoles = self._dipoles().set_opacity(0.45)
        self.add_fixed_in_frame_mobjects(caveat_2)
        self.play(FadeOut(caveat_1), FadeIn(caveat_2), LaggedStart(*[FadeIn(d, scale=0.72) for d in persistent_dipoles[:5]], lag_ratio=0.12), run_time=1.4)
        # Hold the final model view without rotating the camera so the caveat and
        # takeaway cards stay perfectly front-facing in the final contact sheet.
        self.wait(5.0)

        final_note = self._wide_card_lines(
            "TAKEAWAY",
            ["A transient dipole picture becomes alpha_F(r).", "Episode 2 plugs this response density into Eq. (1), the Casimir SIE machine."],
            GOLD,
        ).to_edge(DOWN, buff=0.30)
        self.add_fixed_in_frame_mobjects(final_note)
        self.play(FadeOut(caveat_2), FadeIn(final_note), run_time=0.8)
        self.wait(4.0)
        self.play(
            FadeOut(final_note),
            FadeOut(alpha_card),
            FadeOut(density),
            FadeOut(delay_ring),
            FadeOut(ripple),
            FadeOut(bridge),
            FadeOut(response_arrow),
            FadeOut(source_point),
            FadeOut(response_point),
            FadeOut(persistent_dipoles),
            FadeOut(volume),
            FadeOut(title),
            FadeOut(subtitle),
            run_time=1.1,
        )

    def _vacuum_volume(self):
        cube = Cube(side_length=4.4, fill_opacity=0.035, fill_color=TEAL, stroke_color=BLUE, stroke_opacity=0.25)
        grid = VGroup()
        for z in [-2.2, -1.1, 0, 1.1, 2.2]:
            grid.add(Line3D(start=(-2.2, -2.2, z), end=(2.2, -2.2, z), color=GRID, thickness=0.005))
            grid.add(Line3D(start=(-2.2, 2.2, z), end=(2.2, 2.2, z), color=GRID, thickness=0.005))
            grid.add(Line3D(start=(-2.2, z, -2.2), end=(2.2, z, -2.2), color=GRID, thickness=0.005))
        return VGroup(cube, grid)

    def _dipoles(self):
        positions = [
            np.array([-1.45, -0.9, 0.45]), np.array([0.35, -1.1, -0.35]), np.array([1.25, 0.3, 0.85]),
            np.array([-0.25, 1.1, -0.75]), np.array([-1.05, 0.75, 1.15]), np.array([1.05, 1.0, -1.10]),
            np.array([-1.55, -0.05, -1.0]), np.array([0.88, -0.15, 1.05]), np.array([-0.70, -1.3, 1.0]),
        ]
        directions = [RIGHT, RIGHT + 0.25 * UP, LEFT, RIGHT - 0.2 * UP, RIGHT, UP, LEFT + 0.3 * UP, RIGHT, UP + LEFT]
        dipoles = VGroup()
        for pos, direction in zip(positions, directions):
            d = direction / np.linalg.norm(direction)
            e_minus = Sphere(radius=0.075, color=BLUE, fill_opacity=0.92).move_to(pos - 0.18 * d)
            e_plus = Sphere(radius=0.075, color=RED, fill_opacity=0.92).move_to(pos + 0.18 * d)
            link = Line3D(pos - 0.18 * d, pos + 0.18 * d, color=GOLD, thickness=0.018)
            halo = Sphere(radius=0.34, color=TEAL, fill_opacity=0.035, stroke_opacity=0.08).move_to(pos)
            dipoles.add(VGroup(halo, link, e_minus, e_plus))
        return dipoles

    def _field_pulse(self, center):
        rings = VGroup()
        for radius in [0.22, 0.38, 0.56]:
            rings.add(Torus(major_radius=radius, minor_radius=0.008, color=GOLD, fill_opacity=0.22).move_to(center))
        return rings

    def _ratio_geometry(self, a, b):
        numerator = Sphere(radius=0.24, color=TEAL, fill_opacity=0.10, stroke_opacity=0.08).move_to(b)
        denominator = Sphere(radius=0.24, color=GOLD, fill_opacity=0.10, stroke_opacity=0.08).move_to(a)
        slash = Line3D(a + 0.18 * UP, b - 0.18 * UP, color=INK, thickness=0.012)
        return VGroup(numerator, denominator, slash)

    def _response_web(self, a, b):
        web = VGroup()
        bends = [UP, DOWN, OUT, IN, UP + OUT, DOWN + IN, LEFT + OUT, RIGHT + IN]
        for k, bend in enumerate(bends):
            mid = (a + b) / 2 + 0.52 * bend / np.linalg.norm(bend)
            web.add(Line3D(a, mid, color=GOLD if k % 2 == 0 else TEAL, thickness=0.010))
            web.add(Line3D(mid, b, color=TEAL if k % 2 == 0 else GOLD, thickness=0.010))
        return web

    def _density_texture(self):
        shells = VGroup()
        for radius, opacity in [(1.1, 0.050), (1.55, 0.035), (2.0, 0.023)]:
            shells.add(Sphere(radius=radius, color=TEAL, fill_opacity=opacity, stroke_opacity=0.025))
        shells.add(Torus(major_radius=1.85, minor_radius=0.016, color=TEAL, fill_opacity=0.22).rotate(PI / 2, axis=RIGHT))
        shells.add(Torus(major_radius=1.35, minor_radius=0.014, color=GOLD, fill_opacity=0.12).rotate(PI / 2, axis=UP))
        return shells

    def _definition_card(self):
        box = RoundedRectangle(corner_radius=0.18, width=11.2, height=2.12, color=BORDER, fill_color=CARD, fill_opacity=0.98, stroke_width=1.8)
        head = Text("POLARIZABILITY DENSITY-DENSITY TENSOR", font=MONO, font_size=16, color=TEAL, weight=BOLD).move_to(box.get_center() + 0.76 * UP)
        eq = MathTex(
            r"\boldsymbol{\alpha}_{\rm F}(\mathbf r,\mathbf r',t,t')=\frac{\delta\boldsymbol{\mathcal P}(\mathbf r,t)}{\delta\boldsymbol{\mathcal E}(\mathbf r',t')}",
            font_size=35,
            color=INK,
        ).move_to(box.get_center() + 0.06 * UP)
        foot = Text("response polarization divided by applied electric-field impulse", font=MONO, font_size=15, color=MUTED).move_to(box.get_center() - 0.72 * UP)
        return VGroup(box, head, eq, foot)

    def _symbol_card(self, formula, heading, body, accent):
        box = RoundedRectangle(corner_radius=0.18, width=5.35, height=2.05, color=accent, fill_color=CARD, fill_opacity=0.98, stroke_width=2.0)
        head = Text(heading, font=MONO, font_size=15, color=accent, weight=BOLD).move_to(box.get_center() + 0.70 * UP)
        eq = MathTex(formula, font_size=28, color=INK).move_to(box.get_center() + 0.18 * UP)
        body_text = Text(body, font=MONO, font_size=12, color=MUTED, line_spacing=0.82).move_to(box.get_center() - 0.55 * UP)
        if body_text.width > 4.9:
            body_text.scale_to_fit_width(4.9)
        return VGroup(box, head, eq, body_text)

    def _formula_card(self, formula, body, accent):
        box = RoundedRectangle(corner_radius=0.16, width=4.5, height=1.42, color=accent, fill_color=CARD, fill_opacity=0.97, stroke_width=1.8)
        eq = MathTex(formula, font_size=36, color=INK).move_to(box.get_center() + 0.24 * UP)
        text = Text(body, font=MONO, font_size=12, color=MUTED).move_to(box.get_center() - 0.45 * UP)
        return VGroup(box, eq, text)

    def _caption_lines(self, lines):
        box = RoundedRectangle(corner_radius=0.16, width=10.9, height=0.92, color=BORDER, fill_color=CARD_SOFT, fill_opacity=0.95, stroke_width=1.2)
        text = VGroup(*[Text(line, font=MONO, font_size=15, color=INK) for line in lines]).arrange(DOWN, buff=0.08)
        text.move_to(box.get_center())
        return VGroup(box, text).to_edge(DOWN, buff=0.34)

    def _wide_card_lines(self, eyebrow, lines, color):
        box = RoundedRectangle(corner_radius=0.18, width=11.25, height=1.42, color=color, fill_color=CARD, fill_opacity=0.98, stroke_width=1.9)
        head = Text(eyebrow, font=MONO, font_size=16, color=color, weight=BOLD).move_to(box.get_center() + 0.47 * UP)
        text = VGroup(*[Text(line, font=MONO, font_size=15, color=INK) for line in lines]).arrange(DOWN, buff=0.09)
        text.move_to(box.get_center() - 0.18 * UP)
        return VGroup(box, head, text)
