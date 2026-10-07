from manim import *
import numpy as np
import math

config.renderer = "cairo"
config.frame_width = 128 / 9
config.frame_height = 8
config.background_color = "#080E1C"


class AstraFilm(ThreeDScene):
    # All durations, including transitions, sum to 180 seconds.
    # Display translations/scales are separate from mathematical coordinates.
    CORAL = "#FF806F"
    CYAN = "#4DDBF2"
    GOLD = "#FFD479"
    VIOLET = "#AD94FF"
    INK = "#080E1C"

    def play_for(self, seconds, *animations):
        self.play(*animations, run_time=seconds)
        self.elapsed += seconds

    def fly(self, seconds, **kwargs):
        self.move_camera(run_time=seconds, **kwargs)
        self.elapsed += seconds
        self.phi = kwargs.get("phi", self.phi)
        self.theta = kwargs.get("theta", self.theta)
        self.zoom = kwargs.get("zoom", self.zoom)
        self.focus = np.array(kwargs.get("frame_center", self.focus), dtype=float)

    def until(self, timestamp):
        remainder = timestamp - self.elapsed
        if remainder < -0.001:
            raise ValueError("A film beat exceeded its allocated duration.")
        if remainder > 0.00001:
            self.wait(remainder)
        self.elapsed = float(timestamp)

    def screen_basis(self):
        p, t = self.phi, self.theta
        right = np.array([-math.sin(t), math.cos(t), 0.0])
        up = np.array([-math.cos(p) * math.cos(t),
                       -math.cos(p) * math.sin(t), math.sin(p)])
        return right, up

    def header(self, text, size=20):
        if self.heading is not None:
            self.remove_fixed_in_frame_mobjects(self.heading)
            self.remove(self.heading)
        self.heading = Text(text, font_size=size, color=WHITE)
        if self.heading.width > 12.5:
            self.heading.scale_to_fit_width(12.5)
        self.heading.move_to([0, 3.57, 0]).set_z_index(101)
        self.add_fixed_in_frame_mobjects(self.heading)

    def caption(self, text):
        if self.caption_mob is not None:
            self.remove_fixed_in_frame_mobjects(self.caption_mob)
            self.remove(self.caption_mob)
        self.caption_mob = Text(text, font_size=23, color="#E9EEF8")
        if self.caption_mob.width > 12.7:
            self.caption_mob.scale_to_fit_width(12.7)
        self.caption_mob.move_to([0, -3.48, 0]).set_z_index(101)
        self.add_fixed_in_frame_mobjects(self.caption_mob)

    def clear_equation(self):
        if self.eq is not None:
            self.eq.clear_updaters()
            self.remove(*self.eq.get_family())
            self.eq = None

    def equation(self, *parts, size=36, y=2.42):
        self.clear_equation()
        self.eq = MathTex(*parts, font_size=size, color=WHITE)
        if self.eq.width > 12.1:
            self.eq.scale_to_fit_width(12.1)
        self.eq.move_to(ORIGIN)
        reference = self.eq.copy().scale(1 / self.zoom)
        _, up = self.screen_basis()
        anchor = self.focus + up * y / self.zoom

        def face_camera(mob):
            p, t = self.camera.get_phi(), self.camera.get_theta()
            right = np.array([-math.sin(t), math.cos(t), 0.0])
            up = np.array([-math.cos(p) * math.cos(t),
                           -math.cos(p) * math.sin(t), math.sin(p)])
            basis = np.column_stack((right, up, np.cross(right, up)))
            for target, original in zip(mob.family_members_with_points(),
                                        reference.family_members_with_points()):
                target.set_points(original.get_points() @ basis.T + anchor)

        # Real world-space glyphs: camera zoom magnifies them, while billboarding
        # keeps their plane facing the moving camera. No fixed-orientation override.
        self.eq.add_updater(face_camera)
        face_camera(self.eq)
        self.add(self.eq)
        return self.eq

    def label(self, tex, point, color=WHITE, size=26):
        label = MathTex(tex, font_size=size, color=color).move_to(point)
        self.add_fixed_orientation_mobjects(label)
        self.world_labels.append(label)
        return label

    def clear_labels(self):
        for label in self.world_labels:
            self.remove_fixed_orientation_mobjects(label)
            self.remove(label)
        self.world_labels = []

    def solid(self, vertices, faces, color, opacity=0.22, width=1.5):
        vertices = np.array(vertices, dtype=float)
        panels = VGroup()
        edge_indices = set()
        for i, face in enumerate(faces):
            shade = interpolate_color(ManimColor(color), WHITE, 0.045 * (i % 3))
            panel = Polygon(*[vertices[j] for j in face],
                            fill_color=shade, fill_opacity=opacity,
                            stroke_width=0)
            panel.set_shade_in_3d(True)
            panels.add(panel)
            for j, k in zip(face, face[1:] + face[:1]):
                edge_indices.add(tuple(sorted((j, k))))
        edges = VGroup(*[
            Line(vertices[j], vertices[k], color=color, stroke_width=width)
            for j, k in sorted(edge_indices)
        ])
        return VGroup(panels, edges)

    def cube(self, opacity=0.18):
        vertices = [[-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
                    [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]]
        faces = [[0, 3, 2, 1], [4, 5, 6, 7], [0, 1, 5, 4],
                 [1, 2, 6, 5], [2, 3, 7, 6], [3, 0, 4, 7]]
        return self.solid(vertices, faces, self.CORAL, opacity)

    def octahedron(self, opacity=0.28):
        vertices = [RIGHT, LEFT, UP, DOWN, OUT, IN]
        faces = [[i, j, k] for i in (0, 1) for j in (2, 3) for k in (4, 5)]
        return self.solid(vertices, faces, self.CYAN, opacity)

    def tetrahedron(self, signs, color):
        vertices = [ORIGIN, signs[0] * RIGHT, signs[1] * UP, signs[2] * OUT]
        return self.solid(vertices, [[1, 2, 3], [0, 2, 1],
                                     [0, 1, 3], [0, 3, 2]],
                          color, opacity=0.16, width=1.1)

    def dot3(self, point, color, radius=0.055):
        return Dot3D(point=point, radius=radius, color=color, resolution=(8, 8))

    def supporting_patch(self, normal, scale=1.35, half_size=1.2):
        n = np.array(normal, dtype=float)
        center = n / np.dot(n, n)
        p = np.cross(n, OUT)
        if np.linalg.norm(p) < 0.01:
            p = np.cross(n, UP)
        p /= np.linalg.norm(p)
        q = np.cross(n / np.linalg.norm(n), p)
        points = [scale * (center + half_size * (a * p + b * q))
                  for a, b in [(-1, -1), (1, -1), (1, 1), (-1, 1)]]
        return Polygon(*points, color=self.GOLD, stroke_width=1.2,
                       fill_color=self.GOLD, fill_opacity=0.12)

    def deform(self, mob, reference, diagonal, center=ORIGIN, scale=1.0):
        # Transform every stored control point from the same immutable reference.
        # In the duality act, diagonal and its reciprocal use one shared parameter.
        diagonal = np.array(diagonal)
        center = np.array(center)
        for target, original in zip(mob.family_members_with_points(),
                                    reference.family_members_with_points()):
            target.set_points(original.get_points() * diagonal * scale + center)
        return mob

    def lens_geometry(self):
        # Sample the manuscript series once; no surface rebuilding per frame.
        j = np.arange(1024)
        odd = 2 * j + 1
        coefficients = (8 / math.pi ** 2) * ((-1.0) ** j) / odd ** 2
        self.lens_t = np.linspace(-1.0, 1.0, 257)
        self.lens_w = np.cos(np.outer(self.lens_t, odd) * math.pi / 2) @ coefficients
        self.lens_w = np.maximum(self.lens_w, 0)
        self.lens_w[0] = self.lens_w[-1] = 0
        p = RIGHT
        q = np.array([0, math.cos(PI / 5), math.sin(PI / 5)])
        scale = 1.65

        def width(t):
            return float(np.interp(t, self.lens_t, self.lens_w))

        def embed(v, t):
            return scale * (v * p + t * q)

        surface = Surface(
            lambda r, t: embed(r * width(t), t),
            u_range=[-1, 1], v_range=[-1, 1], resolution=(12, 24),
            fill_opacity=0.35, checkerboard_colors=[self.VIOLET, "#665392"],
            stroke_color=self.VIOLET, stroke_width=0.35)
        contour_points = ([embed(width(t), t) for t in self.lens_t] +
                          [embed(-width(t), t) for t in self.lens_t[::-1]])
        contour = VMobject(color=self.VIOLET, stroke_width=3)
        contour.set_points_as_corners(contour_points + [contour_points[0]])
        axes = VGroup(Line(embed(-1.05, 0), embed(1.05, 0), color=GREY_B,
                           stroke_width=1),
                      Line(embed(0, -1.16), embed(0, 1.16), color=GREY_B,
                           stroke_width=1))
        t = 0.35
        width_line = Line(embed(0, t), embed(width(t), t),
                          color=self.GOLD, stroke_width=4)
        return VGroup(surface, contour, axes), width_line, embed

    def construct(self):
        self.elapsed = 0.0
        self.eq = self.heading = self.caption_mob = None
        self.world_labels = []
        self.phi, self.theta, self.zoom = 65 * DEGREES, -55 * DEGREES, 0.85
        self.focus = np.zeros(3)
        self.set_camera_orientation(phi=self.phi, theta=self.theta, zoom=self.zoom)
        top_rail = Rectangle(width=128 / 9, height=0.72, stroke_width=0,
                             fill_color=self.INK, fill_opacity=0.94).move_to([0, 3.64, 0])
        bottom_rail = Rectangle(width=128 / 9, height=0.86, stroke_width=0,
                                fill_color=self.INK, fill_opacity=0.96).move_to([0, -3.57, 0])
        top_rail.set_z_index(100)
        bottom_rail.set_z_index(100)
        self.add_fixed_in_frame_mobjects(top_rail, bottom_rail)
        stage_right = np.array([math.cos(PI / 6), math.sin(PI / 6), 0])
        left, right = -2.35 * stage_right, 2.35 * stage_right
        signs = [np.array([a, b, c], dtype=float)
                 for a in (-1, 1) for b in (-1, 1) for c in (-1, 1)]
        floor = VGroup()
        for v in np.linspace(-4, 4, 9):
            floor.add(Line([-4, v, -1.42], [4, v, -1.42],
                           color="#263652", stroke_width=0.65),
                      Line([v, -4, -1.42], [v, 4, -1.42],
                           color="#263652", stroke_width=0.65))
        floor.set_stroke(opacity=0.5)

        # ACT 1: constraint before name, 0--27.
        self.header("THE SHAPE AND ITS SHADOW", size=28)
        self.caption("A geometric shadow: a constraint, not an optical projection.")
        self.equation(r"K=[-1,1]^3")[0].set_color(self.CORAL)
        cube = self.cube().scale(1.35)
        self.play_for(2, FadeIn(cube), Create(floor))
        self.fly(3, phi=60 * DEGREES, theta=-35 * DEGREES, zoom=0.93)
        self.header("01  /  CONSTRAINT BEFORE NAME")
        eq = self.equation(r"x", r"\cdot", r"y", r"\leq", r"1", size=46)
        eq[0].set_color(self.CORAL)
        eq[2].set_color(self.GOLD)
        self.caption("x is any point in the cube; y is a testing vector.")
        target_normal = np.array([0.5, 1 / 3, 1 / 6])
        plane = self.supporting_patch(RIGHT)
        normal_line = Line(ORIGIN, 1.35 * RIGHT, color=self.GOLD, stroke_width=4)
        normal_tip = self.dot3(1.35 * RIGHT, self.GOLD)
        self.play_for(2, FadeIn(plane), Create(normal_line), FadeIn(normal_tip))
        self.label(r"y=e_1", 1.6 * RIGHT + 0.2 * OUT, self.GOLD)
        self.until(9)
        self.clear_labels()
        self.caption("The dot product multiplies matching coordinates, then adds; the limit is 1.")

        def turn_support(mob, alpha):
            n = (1 - alpha) * RIGHT + alpha * target_normal
            mob.become(self.supporting_patch(n))

        self.play_for(
            4, UpdateFromAlphaFunc(plane, turn_support),
            UpdateFromAlphaFunc(normal_line, lambda m, a: m.put_start_and_end_on(
                ORIGIN, 1.35 * ((1 - a) * RIGHT + a * target_normal))),
            UpdateFromAlphaFunc(normal_tip, lambda m, a: m.move_to(
                1.35 * ((1 - a) * RIGHT + a * target_normal))))
        vertex = self.dot3(1.35 * np.ones(3), self.GOLD)
        self.add(vertex)
        self.until(14)
        self.clear_equation()
        self.fly(2, zoom=1.05, frame_center=np.array([0.15, 0.15, 0.22]))
        eq = self.equation(r"\max_{x\in K}x\cdot y=",
                           r"|y_1|", r"+|y_2|", r"+|y_3|", size=37)
        self.caption("Choose each cube coordinate with the sign of the matching coordinate of y.")
        self.play_for(1.8, LaggedStart(*[
            Indicate(eq[k], color=self.GOLD, scale_factor=1.08) for k in (1, 2, 3)
        ], lag_ratio=0.35))
        self.until(21)
        self.clear_equation()
        self.clear_labels()
        self.equation(
            r"\begin{aligned}K^\circ&=\{y:x\cdot y\leq1\ \text{for every }x\in K\}\\"
            r"&=\{y:|y_1|+|y_2|+|y_3|\leq1\}\end{aligned}", size=32)
        self.caption("The allowed testing vectors form the polar: a cyan octahedron.")
        polar = self.octahedron().scale(1.35)
        self.play_for(2, FadeOut(plane), FadeOut(normal_line), FadeOut(normal_tip),
                      FadeOut(vertex), cube[0].animate.set_fill(opacity=0.035), FadeIn(polar))
        self.fly(1.5, zoom=0.85, frame_center=ORIGIN)
        self.until(27)

        # ACT 2: an exact volume computation, 27--49.
        self.header("02  /  EIGHT EXACT PIECES")
        self.equation(r"|K|=2^3=8", size=44)[0].set_color(self.CORAL)
        self.caption("Every cube edge has length 2. Bars denote three-dimensional volume.")
        cube_target = self.cube(0.12).scale(0.85).shift(left)
        polar_target = self.octahedron().scale(1.5).shift(right)
        self.play_for(2, Transform(cube, cube_target), Transform(polar, polar_target))
        edge = Line(left + 0.85 * np.array([-1, -1, 1]),
                    left + 0.85 * np.array([1, -1, 1]), color=WHITE, stroke_width=4)
        self.add(edge)
        self.label("2", edge.get_center() + 0.3 * OUT)
        self.until(31)
        self.remove(edge)
        self.clear_labels()
        self.clear_equation()
        pieces = VGroup(*[
            self.tetrahedron(s, interpolate_color(ManimColor(self.CYAN), WHITE, 0.045 * i))
            .scale(1.5, about_point=ORIGIN).shift(right) for i, s in enumerate(signs)
        ])
        self.remove(polar)
        self.add(pieces)
        self.caption("Dissection: eight translated tetrahedra, one from each orthant.")
        self.play_for(2, *[p.animate.shift(0.55 * s) for p, s in zip(pieces, signs)],
                      cube[0].animate.set_fill(opacity=0.025))
        isolated_shift = -(right + 0.55 * np.ones(3))
        self.play_for(1, pieces[7].animate.shift(isolated_shift),
                      *[p[0].animate.set_fill(opacity=0.008) for p in pieces[:7]],
                      *[p[1].animate.set_stroke(opacity=0.05) for p in pieces[:7]],
                      cube[1].animate.set_stroke(opacity=0.1))
        self.fly(1, phi=55 * DEGREES, theta=-35 * DEGREES, zoom=1.6,
                 frame_center=np.array([0.5, 0.5, 0.5]))
        origin = ORIGIN
        base = Polygon(origin, origin + 1.5 * RIGHT, origin + 1.5 * UP,
                       stroke_color=self.GOLD, fill_color=self.GOLD,
                       fill_opacity=0.5, stroke_width=2)
        height = Line(origin, origin + 1.5 * OUT, color=self.GOLD, stroke_width=4)
        eq = self.equation(r"V=\frac13", r"B", r"h",
                           r"=\frac13\cdot\frac12\cdot1=\frac16", size=38)
        eq[1].set_color(self.GOLD)
        eq[2].set_color(self.GOLD)
        self.caption("Base area 1/2; perpendicular height 1.")
        self.label(r"B=1/2", [0.6, 0.6, -0.18], self.GOLD, size=26)
        self.label(r"h=1", [-0.26, 0, 0.9], self.GOLD, size=26)
        self.play_for(0.8, FadeIn(base), Create(height))
        self.play_for(0.8, Indicate(eq[3], color=self.GOLD, scale_factor=1.06))
        self.until(40)
        self.remove(base, height)
        self.clear_labels()
        self.clear_equation()
        self.fly(1.2, phi=55 * DEGREES, theta=-25 * DEGREES,
                 zoom=0.82, frame_center=ORIGIN,
                 added_anims=[pieces[7].animate.shift(-isolated_shift),
                              *[p[0].animate.set_fill(opacity=0.16) for p in pieces[:7]],
                              *[p[1].animate.set_stroke(opacity=1) for p in pieces[:7]],
                              cube[1].animate.set_stroke(opacity=1)])
        self.equation(r"|K^\circ|=8\cdot\frac16=\frac43", size=42)[0].set_color(self.CYAN)
        self.caption("Restored exactly: the eight tetrahedra tile the whole octahedron.")
        self.play_for(2, *[p.animate.shift(-0.55 * s) for p, s in zip(pieces, signs)])
        self.until(44)
        eq = self.equation(r"\mathcal P(K)=", r"|K|", r"|K^\circ|",
                           r"=\frac{32}{3}=\frac{4^3}{3!}", size=40)
        eq[1].set_color(self.CORAL)
        eq[2].set_color(self.CYAN)
        self.caption("The volume product multiplies the volume of a body by the volume of its polar.")
        self.play_for(0.8, Indicate(eq[3], color=self.GOLD, scale_factor=1.08))
        self.until(49)

        # ACT 3: pointwise reciprocal deformation, 49--68.
        self.header("03  /  RECIPROCAL DEFORMATION")
        self.clear_equation()
        self.equation(r"T_\tau=\operatorname{diag}"
                       r"\left(2^\tau,(3/2)^\tau,(1/2)^\tau\right),\quad0\leq\tau\leq1",
                       size=34)
        self.caption("Three coordinate stretches; tau controls their progress. Origins are displayed apart.")
        c_ref, o_ref = self.cube(0.16), self.octahedron(0.26)
        stretched_cube, stretched_polar = c_ref.copy(), o_ref.copy()
        self.deform(stretched_cube, c_ref, [1, 1, 1], left, 0.85)
        self.deform(stretched_polar, o_ref, [1, 1, 1], right, 0.85)
        self.play_for(1, FadeOut(cube), FadeOut(pieces),
                      FadeIn(stretched_cube), FadeIn(stretched_polar))
        self.fly(1, phi=60 * DEGREES, theta=-35 * DEGREES, zoom=0.86)
        self.until(54)
        self.equation(r"(TK)^\circ=", r"T^{-T}K^\circ", size=44)[1].set_color(self.CYAN)
        self.caption("Inverse transpose: each polar coordinate receives the reciprocal stretch.")
        contact_x = self.dot3(left + 0.85 * np.ones(3), self.GOLD)
        contact_y = self.dot3(right + 0.85 * target_normal, self.GOLD)
        self.add(contact_x, contact_y)

        def stretch_animations(start, end):
            def d(alpha):
                return np.array([2.0, 1.5, 0.5]) ** (start + (end - start) * alpha)
            return [
                UpdateFromAlphaFunc(stretched_cube, lambda m, a:
                                    self.deform(m, c_ref, d(a), left, 0.85)),
                UpdateFromAlphaFunc(stretched_polar, lambda m, a:
                                    self.deform(m, o_ref, 1 / d(a), right, 0.85)),
                UpdateFromAlphaFunc(contact_x, lambda m, a:
                                    m.move_to(left + 0.85 * d(a))),
                UpdateFromAlphaFunc(contact_y, lambda m, a:
                                    m.move_to(right + 0.85 * target_normal / d(a)))
            ]

        self.fly(4, phi=65 * DEGREES, theta=-15 * DEGREES, zoom=0.8,
                 added_anims=stretch_animations(0, 1))
        self.equation(r"(Tx)\cdot(T^{-T}y)=x\cdot y=1", size=39)
        self.caption("The highlighted contact pair keeps the same dot product throughout the motion.")
        self.until(61)
        self.equation(r"|\det T|=2\cdot\frac32\cdot\frac12=\frac32", size=40)
        self.caption("Determinants scale volume; polarity takes the reciprocal.")
        self.until(63)
        self.equation(r"|K|:\ 8\longrightarrow12,\qquad"
                       r"|K^\circ|:\ \frac43\longrightarrow\frac89", size=39)
        self.caption("One volume grows by 3/2. The other shrinks by 2/3.")
        self.until(65)
        self.equation(r"\mathcal P(TK)=12\cdot\frac89=\frac{32}{3}=\mathcal P(K)",
                       size=38)
        self.caption("The volume factors cancel, including on the reciprocal journey back.")
        self.play_for(2, *stretch_animations(1, 0))
        self.until(68)

        # ACT 4: the self-polar ball, 68--82.
        self.header("04  /  THE ROUND COMPARISON")
        self.clear_equation()
        self.equation(r"B=\{x:\|x\|_2\leq1\}", size=43, y=2.05)
        sphere = Surface(
            lambda u, v: 1.45 * np.array([math.sin(v) * math.cos(u),
                                          math.sin(v) * math.sin(u), math.cos(v)]),
            u_range=[0, TAU], v_range=[0, PI], resolution=(24, 12),
            checkerboard_colors=["#844B51", "#A65F64"], fill_opacity=0.55,
            stroke_color=self.CYAN, stroke_width=0.55)
        self.caption("The Euclidean unit ball contains precisely the vectors of length at most 1.")
        self.play_for(1, FadeOut(stretched_cube), FadeOut(stretched_polar),
                      FadeOut(contact_x), FadeOut(contact_y), FadeIn(sphere))
        self.fly(2, phi=55 * DEGREES, theta=-25 * DEGREES, zoom=1.02)
        self.until(73)
        n = np.array([0.6, -0.5, math.sqrt(0.39)])
        tangent = self.supporting_patch(n, scale=1.45, half_size=0.65)
        radius = Line(ORIGIN, 1.45 * n, color=self.GOLD, stroke_width=4)
        tip = self.dot3(1.45 * n, self.GOLD)
        self.equation(r"\max_{x\in B}x\cdot y=\|y\|_2", size=42)
        self.caption("An aligned radius attains the largest dot product.")
        self.play_for(1, FadeIn(tangent), Create(radius), FadeIn(tip))
        self.until(75)
        self.equation(r"B^\circ=B", size=52)
        self.caption("The allowed testing vectors form the same ball.")
        self.until(77)
        self.equation(r"|B|=\frac{4\pi}{3}", size=46)
        self.caption("Its volume is four pi over three.")
        self.until(79)
        self.equation(r"\mathcal P(B)=\frac{16\pi^2}{9}\approx17.546"
                       r">\frac{32}{3}\approx10.667", size=35)
        self.caption("The round example has a larger volume product than the cube.")
        self.until(82)

        # ACT 5: hypotheses, attribution, and the analytic lens, 82--106.
        self.header("05  /  MANUSCRIPT CLAIM: ORIGIN-SYMMETRIC CONVEX BODIES")
        self.equation(r"K\subset\mathbb R^n,\qquad K=-K,\qquad n\geq1", size=38)
        self.caption("A convex body is compact and convex, with nonempty interior.")
        self.until(84)
        self.caption("Origin symmetry means x belongs to K exactly when -x does.")
        self.until(87)
        self.equation(r"\mathcal P(K)=|K|\,|K^\circ|\geq\frac{4^n}{n!}", size=42)
        self.caption("Manuscript claim in dimension n; n! means factorial.")
        self.until(89)
        self.caption("The 3D theorem predates this paper: Iriyeh-Shibata.")
        self.until(91)
        self.header("SCHEMATIC OF THE ANALYTIC INPUT", size=21)
        self.clear_equation()
        lens, width_line, embed = self.lens_geometry()
        self.caption("The proof route passes through a complex planar lens.")
        self.play_for(1, FadeOut(sphere), FadeOut(tangent), FadeOut(radius),
                      FadeOut(tip), FadeIn(lens))
        self.fly(2, phi=60 * DEGREES, theta=-40 * DEGREES, zoom=0.95,
                 frame_center=ORIGIN)
        self.equation(r"D=\{v+it:|t|\leq1,\ |v|\leq\lambda(t)\}", size=37)
        self.label("v", embed(1.15, 0), self.VIOLET)
        self.label("t", embed(0, 1.2), self.VIOLET)
        self.play_for(0.8, Create(width_line))
        self.until(97)
        self.caption("v is real; t is the imaginary coordinate.")
        self.until(99)
        self.caption("Gold marks the half-width lambda(t).")
        self.until(101)
        self.clear_labels()
        self.equation(r"S\geq1", size=54)[0].set_color(self.GOLD)
        self.caption("A holomorphic estimate bounds total feasibility: S is at least 1.")
        boundary_dots = VGroup(*[
            self.dot3(embed(float(np.interp(t, self.lens_t, self.lens_w)), t),
                      self.GOLD, 0.035) for t in (-0.72, -0.24, 0.24, 0.72)
        ])
        self.play_for(0.8, FadeIn(boundary_dots))
        self.until(104)
        self.caption("Illustration only: the holomorphic estimate is not proved.")
        self.until(106)

        # ACT 6: exact cube simplices illuminate the attributed proof route, 106--156.
        self.header("06  /  FEASIBILITY TO INTEGRATED VOLUME")
        self.clear_equation()
        self.equation(r"A=\{X:|b_i\cdot X|\leq1\ \text{for every }i\}", size=37)
        cube = self.cube(0.08).scale(0.95).shift(left)
        polar = self.octahedron(0.06).scale(1.35).shift(right)
        self.caption("Each spanning row b_i sets two supporting planes.")
        self.play_for(1, FadeOut(lens), FadeOut(width_line), FadeOut(boundary_dots),
                      FadeIn(cube), FadeIn(polar))
        self.fly(1, phi=60 * DEGREES, theta=-35 * DEGREES, zoom=0.88)
        self.until(109)
        self.equation(r"A^\circ=\operatorname{conv}\{\pm b_i\}", size=42)
        self.caption("The polar is the convex hull of signed rows.")
        self.until(112)
        self.equation(r"L_X=\{Y:|b_i\cdot Y|\leq\lambda(b_i\cdot X)"
                       r"\ \text{for every }i\}", size=34)
        self.caption("Lens widths determine which Y are allowed at X.")
        x0 = np.array([0.2, -0.3, 0.4])
        xdot = self.dot3(left + 0.95 * x0, self.GOLD, 0.07)
        self.add(xdot)
        self.label("X", left + 0.95 * x0 + 0.22 * OUT, self.GOLD)
        self.until(115)
        self.equation(r"b_i\cdot Y=\varepsilon_i\lambda(b_i\cdot X),"
                       r"\quad i\in I,\quad\varepsilon_i=\pm1", size=35)
        self.caption("Independent tight equations determine one candidate Y.")
        self.until(118)
        self.caption("Feasible means Y satisfies every constraint.")
        self.until(121)
        self.clear_equation()
        self.caption("One signed basis gives one tetrahedron.")
        pieces = VGroup(*[
            self.tetrahedron(s, interpolate_color(ManimColor(self.CYAN), WHITE, 0.04 * i))
            .scale(1.35, about_point=ORIGIN).shift(right) for i, s in enumerate(signs)
        ])
        self.play_for(0.7, FadeIn(pieces[7]))
        self.fly(0.8, phi=55 * DEGREES, theta=-25 * DEGREES,
                 zoom=1.25, frame_center=right)
        self.equation(r"\operatorname{conv}(0,e_1,e_2,e_3)", size=38)
        self.until(125)
        self.clear_equation()
        self.caption("Feasible simplices have disjoint interiors almost everywhere.")
        self.play_for(1, LaggedStart(*[FadeIn(pieces[i]) for i in range(7)],
                                    lag_ratio=0.12))
        self.add(pieces)
        self.fly(1, phi=60 * DEGREES, theta=-28 * DEGREES,
                 zoom=0.9, frame_center=ORIGIN)
        self.clear_labels()
        self.until(128)
        self.equation(r"\Sigma_X\subseteq A^\circ", size=48)
        self.caption("Cube tiles; general bodies can leave gaps.")

        def cube_path(alpha):
            return np.array([0.55 * math.cos(TAU * alpha),
                             0.45 * math.sin(TAU * alpha),
                             0.35 * math.sin(2 * TAU * alpha)])

        start = xdot.get_center().copy()
        self.play_for(0.6, UpdateFromAlphaFunc(xdot, lambda m, a:
                      m.move_to((1 - a) * start + a * (left + 0.95 * cube_path(0)))))
        self.play_for(1.4, UpdateFromAlphaFunc(xdot, lambda m, a:
                      m.move_to(left + 0.95 * cube_path(a))))
        self.until(130)
        self.header("MANUSCRIPT PROOF ROUTE  /  ANALYTIC INPUT + GEOMETRY")
        self.equation(r"S=\sum_I P_I", size=49)
        self.caption("I indexes independent sets of n rows.")
        self.until(133)
        self.caption("Each P_I is a feasibility probability under boundary sampling.")
        self.until(136)
        eq = self.equation(r"S=", r"\frac{n!}{4^n}",
                           r"\int_A", r"|\Sigma_X|", r"\,dX", size=46)
        eq[3].set_color(self.CYAN)
        self.caption("|Sigma_X| is the volume of the feasible union.")
        self.fly(0.8, zoom=1.7, frame_center=eq[3].get_center())
        self.until(139)
        self.caption("dX integrates over every position X in A.")
        self.fly(0.8, zoom=1.7, frame_center=eq[4].get_center())
        self.until(142)
        self.caption("n!/4^n normalizes the boundary-sampling volume identity.")
        self.fly(0.8, zoom=1.7, frame_center=eq[1].get_center())
        self.until(144)
        self.fly(1, zoom=0.9, frame_center=ORIGIN)
        eq = self.equation(r"1\leq S=", r"\frac{n!}{4^n}\int_A|\Sigma_X|\,dX",
                           r"\leq", r"\frac{n!}{4^n}|A|\,|A^\circ|", size=35)
        eq[0].set_color(self.GOLD)
        eq[1].set_color(self.CYAN)
        self.caption("Analytic estimate: S is at least 1.")
        self.until(147)
        self.caption("Containment bounds each feasible volume by the polar volume.")
        self.play_for(0.8, Indicate(eq[3], color=self.CYAN, scale_factor=1.06))
        self.until(149)
        self.equation(r"\text{Cube:}\quad S=\frac{6}{64}\cdot8\cdot\frac43=1", size=42)
        self.caption("For the cube, all eight pieces fill the polar at every interior X.")
        self.until(152)
        self.equation(r"1\leq S=\frac{n!}{4^n}\int_A|\Sigma_X|\,dX"
                       r"\leq\frac{n!}{4^n}|A|\,|A^\circ|", size=35)
        self.caption("The manuscript extends the polytope inequality by approximation.")
        self.until(156)

        # ACT 7: Hanner recursion, mixed construction, equality and source, 156--180.
        self.header("07  /  EQUALITY'S RECURSIVE FAMILY")
        self.clear_labels()
        self.equation(r"[-1,1]", size=44)
        self.caption("Start with a centered interval.")
        h_cube_ref, h_oct_ref = self.cube(0.2), self.octahedron(0.27)
        h_cube, h_oct = h_cube_ref.copy(), h_oct_ref.copy()
        self.deform(h_cube, h_cube_ref, [1, 0, 0], left, 1.05)
        self.deform(h_oct, h_oct_ref, [1, 0, 0], right, 1.35)
        self.play_for(1.4, FadeOut(cube), FadeOut(polar), FadeOut(pieces),
                      FadeOut(xdot), FadeIn(h_cube), FadeIn(h_oct))
        self.until(158)
        self.equation(r"H_1\times H_2", size=48)
        self.caption("Construction schematic: product at left; hull at right.")
        self.play_for(1.5,
                      UpdateFromAlphaFunc(h_cube, lambda m, a:
                          self.deform(m, h_cube_ref, [1, a, 0], left, 1.05)),
                      UpdateFromAlphaFunc(h_oct, lambda m, a:
                          self.deform(m, h_oct_ref, [1, a, 0], right, 1.35)))
        self.play_for(1.5, UpdateFromAlphaFunc(h_cube, lambda m, a:
                      self.deform(m, h_cube_ref, [1, 1, a], left, 1.05)))
        self.until(161)
        self.equation(r"\operatorname{conv}\big((H_1,0)\cup(0,H_2)\big)", size=39)
        self.caption("Schematic growth; the completed solids form a polar pair.")
        self.play_for(1.5, UpdateFromAlphaFunc(h_oct, lambda m, a:
                      self.deform(m, h_oct_ref, [1, 1, a], right, 1.35)))
        self.until(164)
        self.equation(r"(H_1\times H_2)^\circ="
                       r"\operatorname{conv}\big((H_1^\circ,0)\cup(0,H_2^\circ)\big)", size=32)
        self.caption("Polarity swaps operations; mixed constructions are Hanner too.")
        mixed = self.solid(
            [[-1, -1, 0], [1, -1, 0], [1, 1, 0], [-1, 1, 0], [0, 0, 1], [0, 0, -1]],
            [[0, 1, 4], [1, 2, 4], [2, 3, 4], [3, 0, 4],
             [1, 0, 5], [2, 1, 5], [3, 2, 5], [0, 3, 5]],
            self.VIOLET, opacity=0.2).scale(0.55).shift(1.6 * DOWN)
        self.play_for(0.7, FadeIn(mixed))
        self.fly(2, phi=55 * DEGREES, theta=-15 * DEGREES, zoom=0.8)
        self.until(168)
        self.header("ORIGIN-SYMMETRIC EQUALITY CLAIM  /  MANUSCRIPT")
        self.equation(r"\mathcal P(K)=\frac{4^n}{n!}"
                       r"\quad\Longleftrightarrow\quad K=TH,\quad H\ \text{Hanner}", size=34)
        self.caption("T is invertible; H is a Hanner body.")
        self.until(171)
        self.caption("The equality classification uses an additional argument.")
        self.until(174)
        self.clear_equation()
        self.remove_fixed_in_frame_mobjects(self.heading, self.caption_mob)
        self.remove(self.heading, self.caption_mob)
        card_a = Text("OpenAI manuscript  |  September 22, 2026  |  family 087",
                      font_size=26, color=WHITE)
        card_b = Text("Formalization reported by the source; not independently checked for this film.",
                      font_size=22, color="#D4DCEE")
        for card in (card_a, card_b):
            if card.width > 12.5:
                card.scale_to_fit_width(12.5)
        card_a.move_to([0, 0.45, 0]).set_z_index(101)
        card_b.move_to([0, -0.28, 0]).set_z_index(101)
        self.add_fixed_in_frame_mobjects(card_a, card_b)
        self.play_for(1, h_cube.animate.set_opacity(0.09),
                      h_oct.animate.set_opacity(0.09), mixed.animate.set_opacity(0.07),
                      floor.animate.set_opacity(0.07), FadeIn(card_a), FadeIn(card_b))
        self.until(180)
