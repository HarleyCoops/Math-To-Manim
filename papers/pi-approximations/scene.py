from manim import *
import numpy as np
import math

# Planned duration: 419.7 s (12,591 frames at the host's 30 fps).
# Eight chapters: 0-51.2, 51.2-86.2, 86.2-123.0, 123.0-150.0,
# 150.0-251.3, 251.3-291.9, 291.9-392.7, 392.7-419.7 seconds.
# 27 fully visible holds total 384.4 s. Separately budgeted:
# 16.2 s card transitions + 12.6 s camera setup + 6.5 s diagram animation.
# Reading rule: (title + prose words)/2.5 + 1 s, then 5 s per
# short principal formula or 10 s for a multiline formula/matrix.
# New explanatory diagram words and math labels add separate allowances.
# Unchanged context labels are not charged twice; rescaling equations get 5 s.
# All times are integral frame counts at 30 fps. No motion counts as reading.
PLANNED_DURATION = 419.7
PLANNED_HOLDS = (8.0, 19.0, 20.6, 16.8, 15.2, 17.0, 15.8, 17.0, 7.0, 6.2, 14.0, 16.2, 12.0, 12.8, 12.0, 13.0, 17.2, 10.0, 11.6, 13.8, 14.0, 17.8, 16.2, 15.2, 20.2, 14.8, 11.0)
# No render, complete-proof verification or Lean execution is performed here.
# Research attribution: OpenAI, September 24 2026, family 017.
# Pinned revision: fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb.
# This scene illustrates the argument; it does not independently verify the
# complete research proof or run Lean. The retained Lean scope covers the
# exponent theorem, excluding Flint-Hills convergence. See companion dossier.
# Numerical labels use the retained high-precision computation.
config.renderer = "cairo"
config.frame_width = 128 / 9
config.frame_height = 8
config.background_color = "#F3EFE6"

BONE = "#F3EFE6"
INK = "#202A35"
TEAL = "#176B72"
CORAL = "#C76F51"
GOLD = "#AD8542"

class AstraFilm(ThreeDScene):
    def construct(self):
        self.camera.background_color = BONE
        self.set_camera_orientation(phi=65 * DEGREES, theta=-55 * DEGREES, zoom=0.9)
        self.world = VGroup()
        self.card = None
        self.elapsed = 0.0
        self.billboards = []
        self.pending_billboards = []
        self.pending_reading = 0.0
        self.reading_log = []
        bands = VGroup(
            Rectangle(width=14.3, height=2.18, stroke_width=0,
                      fill_color=BONE, fill_opacity=1).move_to([0, 2.91, 0]),
            Rectangle(width=14.3, height=1.70, stroke_width=0,
                      fill_color=BONE, fill_opacity=1).move_to([0, -3.15, 0]),
        ).set_z_index(100)
        self.add_fixed_in_frame_mobjects(bands)

        def txt(s, size=28, color=INK):
            return Text(s, font_size=size, color=color)

        def fit(m, width):
            if m.width > width:
                m.scale_to_fit_width(width)
            return m

        def label(s, p, size=24, color=INK, tex=False, read=None):
            m = MathTex(s, font_size=size, color=color) if tex else txt(s, size, color)
            m.move_to(p)
            self.pending_billboards.append(m)
            # New diagram labels are budgeted once; unchanged labels are context.
            self.pending_reading += (read if read is not None else
                                     (1.0 if tex else max(.4, len(s.split()) / 2.5)))
            return m

        def dot(p, color=CORAL, r=0.047):
            return Dot3D(point=np.array(p), radius=r, color=color, resolution=(6, 10))

        def make_card(title, formula=None, lines=(), fs=37):
            parts = [fit(txt(title, 27, TEAL), 12.7).move_to([0, 3.51, 0])]
            if formula:
                f = MathTex(formula, color=INK, font_size=fs)
                fit(f, 12.65)
                if f.height > 1.28:
                    f.scale_to_fit_height(1.28)
                f.move_to([0, 2.59, 0])
                parts.append(f)
            assert len(lines) <= 2
            for i, s in enumerate(lines):
                parts.append(fit(txt(s, 28), 12.65).move_to([0, -2.78 - 0.51 * i, 0]))
            return VGroup(*parts).set_z_index(110)

        def beat(title, formula=None, lines=(), world=None,
                 view=None, motion=None, motion_time=0, fs=37):
            # Clear first: outgoing and incoming overlay glyphs never coexist.
            # Camera setup and animation are NOT credited as reading holds.
            # Formula allowance: 5 s single-line; 10 s multiline or matrix.
            # New diagram words: 2.5 words/s; isolated math labels: 1 s each.
            # Explicit read= overrides cover nontrivial diagram equations.
            word_count = len((" ".join((title,) + tuple(lines))).split())
            formula_time = (10.0 if formula and
                            ("gathered" in formula or "pmatrix" in formula)
                            else 5.0 if formula else 0.0)
            required = word_count / 2.5 + 1 + formula_time + self.pending_reading
            hold = math.ceil((required - 1e-9) * 5) / 5
            new_labels = self.pending_billboards
            self.pending_billboards = []
            self.pending_reading = 0.0
            outgoing = []
            if self.card is not None:
                outgoing.append(FadeOut(self.card))
            if world is not None and len(self.world):
                outgoing.append(FadeOut(self.world))
            if outgoing:
                self.play(*outgoing, run_time=.2)
            else:
                self.wait(.2)
            if self.card is not None:
                self.remove_fixed_in_frame_mobjects(self.card)
                self.remove(self.card)
            if world is not None:
                # Child animations can promote geometry to top-level scene objects.
                # Retire the entire old family, including those promoted children.
                retired_family = self.world.get_family()
                self.remove(*retired_family)
                assert not set(retired_family).intersection(self.get_mobject_family_members())
                if self.billboards:
                    self.remove_fixed_orientation_mobjects(*self.billboards)
                    self.remove(*self.billboards)
                self.world = world
                self.billboards = []
            if new_labels:
                self.add_fixed_orientation_mobjects(*new_labels)
                self.remove(*new_labels)
                self.billboards.extend(new_labels)
            setup = 0.0
            if view is not None:
                # Reveal the sculpture during the camera move; captions follow.
                extras = [FadeIn(world)] if world is not None and len(world) else []
                self.move_camera(**view, added_anims=extras,
                                 run_time=1.8, rate_func=smooth)
                setup = 1.8
            new_card = make_card(title, formula, lines, fs)
            self.add_fixed_in_frame_mobjects(new_card)
            self.remove(new_card)
            incoming = [FadeIn(new_card)]
            if world is not None and len(world) and view is None:
                incoming.append(FadeIn(world))
            self.play(*incoming, run_time=.4)
            self.card = new_card
            if motion is not None:
                self.play(*motion, run_time=motion_time, rate_func=smooth)
            else:
                assert motion_time == 0
            self.wait(hold)
            assert hold + 1e-8 >= required
            duration = .6 + setup + motion_time + hold
            self.elapsed += duration
            self.reading_log.append((title, word_count, formula_time,
                                     required, hold, duration))

        def error_axis(power, e, fraction):
            def p(v):
                return np.array([-3.7 + 2.05 * v, 0, 0])
            g = VGroup(Line(p(-0.25), p(3.45), color=TEAL, stroke_width=4))
            for k in range(4):
                g.add(Line(p(k) + [0, 0, -0.10], p(k) + [0, 0, 0.10],
                           color=INK, stroke_width=2))
                g.add(label(str(k), p(k) + [0, 0, -0.38], 23))
            g.add(dot(p(0), GOLD, 0.08), dot(p(e), CORAL, 0.075))
            g.add(Line(p(0), p(e), color=CORAL, stroke_width=7))
            g.add(label(r"E=0", p(0) + [0, 0, 0.52], 28, GOLD, True))
            g.add(label(fraction, p(e) + [0, 0, 0.55], 31, CORAL, True))
            g.add(label(r"E=10^{" + str(power) + r"}(x-\pi)",
                        [0, 0, -1.06], 29, INK, True, read=5))
            return g

        # 1. Literal coordinate, followed by two explicitly cut rescalings.
        p0 = np.array([-3.3, 0, 0])
        def literal(x):
            return p0 + np.array([48 * (x - 3.08), 0, 0])
        opening = VGroup(Line(literal(3.08), literal(3.22), color=TEAL, stroke_width=4))
        for x, s in [(3.10, "3.10"), (3.14, "3.14"), (3.18, "3.18")]:
            opening.add(Line(literal(x) + [0, 0, -.09], literal(x) + [0, 0, .09],
                             color=INK, stroke_width=2))
            opening.add(label(s, literal(x) + [0, 0, -.45], 24))
        opening.add(dot(literal(math.pi), GOLD, .08),
                    label(r"\pi", literal(math.pi) + [0, 0, .48], 40, GOLD, True))
        beat("HOW CLOSE CAN FRACTIONS GET TO PI?",
             lines=("Fractions approach an irrational target.",), world=opening)
        beat("22/7",
             r"\frac{22}{7}-\pi=0.001264489\ldots",
             ("Zero error is exact π.",
              "Larger denominators allow closer approximations."),
             world=error_axis(3, 1.264489267349619, r"22/7"),
             view=dict(phi=65 * DEGREES, theta=-70 * DEGREES, zoom=.94))
        beat("355/113",
             r"\frac{355}{113}-\pi=0.000000266764\ldots",
             ("Each unit now means one ten-millionth.",
              "One exceptional fraction cannot settle an infinite pattern."),
             world=error_axis(7, 2.667641890624223, r"355/113"))

        # 2. Computed logarithmic error landscape.
        samples = [
            (7, .8450980400142568, 2.898084852480603),
            (106, 2.025305865264770, 4.079774232335717),
            (113, 2.053078443483420, 6.573872471368807),
            (33102, 4.519854234341384, 9.238154343888931),
            (33215, 4.521334256777568, 9.479349061978999),
            (66317, 4.821624871690065, 9.912372837550457),
            (99532, 4.997962730887820, 10.535460007365110),
        ]
        def lp(u, depth, z):
            return np.array([1.13 * (u - 2.5), depth, .29 * z - 1.35])
        landscape = VGroup()
        for u in range(6):
            landscape.add(Line(lp(u, -.18, 0), lp(u, -.18, 11),
                               color=TEAL, stroke_width=.65, stroke_opacity=.23))
            if u in [0, 2, 4, 5]:
                landscape.add(label(str(u), lp(u, 0, -.8), 21))
        for z in [0, 4, 8]:
            landscape.add(Line(lp(0, -.18, z), lp(5, -.18, z),
                               color=TEAL, stroke_width=.65, stroke_opacity=.23))
            landscape.add(label(str(z), lp(-.32, 0, z), 21))
        ribbon = Surface(lambda u, v: lp(u, v, 2 * u), u_range=[0, 5],
                         v_range=[-.24, .24], resolution=(32, 4),
                         checkerboard_colors=[TEAL, TEAL], fill_opacity=.4,
                         stroke_color=TEAL, stroke_width=.3)
        landscape.add(ribbon, Line(lp(0, 0, 0), lp(5, 0, 10), color=TEAL, stroke_width=3))
        empirical = VGroup()
        for q, u, z in samples:
            empirical.add(Line(lp(u, 0, 2*u), lp(u, 0, z),
                               color=CORAL, stroke_width=2), dot(lp(u, 0, z), CORAL, .05))
        landscape.add(empirical)
        landscape.add(label(r"355/113", lp(samples[2][1], 0, samples[2][2]) + [.32, 0, .4],
                            28, CORAL, True),
                      label(r"Z=2U", lp(4, 0, 8) + [0, 0, -.45], 27, TEAL, True))
        beat("LOGARITHMIC ERRORS",
             r"U=\log_{10}q,\qquad Z=-\log_{10}|\pi-p/q|",
             ("Right one: denominator ×10. Up one: error ÷10.",
              "Continued-fraction examples; depth is decorative."),
             world=landscape,
             view=dict(phi=60*DEGREES, theta=-70*DEGREES, zoom=.82), fs=34)
        beat("INFINITELY MANY APPROXIMATIONS",
             r"0<\left|x-\frac pq\right|<\frac1{q^2}",
             ("Every irrational x has such reduced fractions beyond every denominator cutoff.",
              "This classical theorem is not proved by finite samples."))

        # 3. Finite data disappears before the infinite definition.
        def ep(u, nu):
            return np.array([1.05*(u-2.5), 1.8*(nu-2.5), .235*nu*u-1.32])
        envelope = VGroup(Surface(lambda u, v: ep(u, v),
                           u_range=[0, 5], v_range=[2, 3], resolution=(32, 16),
                           checkerboard_colors=[TEAL, TEAL], fill_opacity=.35,
                           stroke_color=TEAL, stroke_width=.35))
        for nu in [2, 2.25, 2.5, 2.75, 3]:
            envelope.add(ParametricFunction(lambda u, n=nu: ep(u, n),
                                            t_range=[0, 5], color=TEAL, stroke_width=1))
        for u in range(6):
            envelope.add(Line(ep(u, 2), ep(u, 3), color=TEAL, stroke_width=1))
        # Both horizontal coordinates now carry mathematical meaning.
        envelope.add(Line(ep(0,2), ep(5,2), color=INK, stroke_width=2),
                     Line(ep(0,2), ep(0,3), color=INK, stroke_width=2),
                     label("U", ep(2.5,2)+[0,-.28,-.3], 28, INK, True),
                     label(r"\nu", ep(0,3)+[-.25,.12,0], 28, INK, True))
        beat("IRRATIONALITY EXPONENT",
             r"\begin{gathered}\mu(\pi)=\sup\{\nu>0:\ 0<|\pi-p/q|<q^{-\nu}\\"
             r"\text{for infinitely many reduced }p/q,\quad q\ge2\}\end{gathered}",
             ("Reduced: no common factor. Supremum: least upper bound.",),
             world=envelope,
             view=dict(phi=65*DEGREES, theta=-40*DEGREES, zoom=.83), fs=35)
        sections = VGroup()
        for nu, col in [(2, TEAL), (2.25, GOLD), (3, CORAL)]:
            sections.add(ParametricFunction(lambda u, n=nu: ep(u, n), t_range=[0, 5],
                                            color=col, stroke_width=5))
        for nu, col, text_value in [(2,TEAL,"2"),(2.25,GOLD,"2.25"),(3,CORAL,"3")]:
            anchor = ep(5,nu)
            end = anchor + [.7, .15*(nu-2), -.12]
            sections.add(Line(anchor,end,color=col,stroke_width=1.5),
                         label(r"\nu="+text_value, end+[.2,0,.08],25,col,True))
        beat("EXPONENT COORDINATES",
             r"q^{-2}\qquad q^{-2.25}\qquad q^{-3}",
             ("Along: log-denominator U. Across: exponent ν.",
              "Height Z=νU plots the error bound; higher means smaller."),
             motion=[Create(sections)], motion_time=1)
        self.world.add(sections)

        # 4. No invented threshold and no bounded-partial-quotient claim.
        beat("REPORTED RESULT",
             r"\begin{gathered}\forall\varepsilon>0\ \exists Q(\varepsilon):\quad"
             r"\left|\pi-\frac pq\right|\ge q^{-2-\varepsilon}\\"
             r"p\in\mathbb Z,\quad q\in\mathbb Z,\quad q\ge Q(\varepsilon)\end{gathered}",
             ("The manuscript reports μ(π)=2.",
              "Q depends on ε; no computable threshold is supplied."),
             view=dict(phi=15*DEGREES, theta=-90*DEGREES, zoom=.86), fs=36)
        beat("LIMITS",
             lines=("No uniform positive c/q² lower bound is asserted.",
                    "Continued-fraction coefficients need not be bounded."))

        # 5. Explicitly schematic research-proof mechanism.
        markers = VGroup(*[dot([x, 0, 0], CORAL, .08) for x in [-1.2, -.4, .4, 1.2]])
        beat("PROOF SCHEMATIC",
             lines=("Assume infinitely many approximations at fixed ν>2.",
                    "Select widely separated denominators."),
             world=markers, view=dict(phi=65*DEGREES, theta=-35*DEGREES, zoom=.85),
             motion=[markers[0].animate.shift(2*LEFT),
                     markers[3].animate.shift(2*RIGHT)], motion_time=2)
        def sp(x, y, z):
            return np.array([.83*(x-2), .95*(y-1), 1.15*(z-.65)])
        vertices = [sp(0,0,0), sp(6,0,0), sp(0,3,0), sp(0,0,2)]
        simplex = VGroup()
        for face in [(0,1,2), (0,1,3), (0,2,3), (1,2,3)]:
            simplex.add(Polygon(*[vertices[i] for i in face], fill_color=TEAL,
                                fill_opacity=.17, stroke_width=1.2, stroke_color=TEAL))
        for z in [.5, 1, 1.5]:
            b = 6 - 3*z
            simplex.add(Polygon(sp(0,0,z), sp(b,0,z), sp(0,b/2,z),
                                fill_opacity=0, stroke_color=GOLD, stroke_width=2))
        for x in range(7):
            for y in range(4):
                for z in range(3):
                    if x+2*y+3*z <= 6:
                        simplex.add(dot(sp(x,y,z), TEAL, .037))
        simplex.add(label("Illustrative weights; low-dimensional slice",
                          [0, 0, -2.55], 24))
        beat("PROOF SCHEMATIC",
             r"x+2y+3z\le6,\qquad x,y,z\ge0",
             ("Jets are finite Taylor-coefficient packets at separated centers.",
              "The simplex organizes the polynomial budget."),
             world=simplex,
             view=dict(phi=65*DEGREES, theta=-48*DEGREES, zoom=.85))
        beat("PROOF SCHEMATIC · TOY MATRIX",
             r"\det\begin{pmatrix}1&2\\1&2\end{pmatrix}=0",
             ("Equal rows force zero: a determinant detects independence.",))
        beat("PROOF SCHEMATIC",
             r"0\ne\Delta_H\in\mathbb Q(i)",
             ("Interpolation supplies a nonzero square minor.",
              "Entries have rational real and imaginary parts."))
        integer_grid = VGroup()
        for x in range(-3,4):
            integer_grid.add(Line([x*.65,-1.3,0], [x*.65,1.3,0],
                                  color=TEAL, stroke_width=.6, stroke_opacity=.3))
        for y in range(-2,3):
            integer_grid.add(Line([-1.95,y*.65,0], [1.95,y*.65,0],
                                  color=TEAL, stroke_width=.6, stroke_opacity=.3))
        integer_grid.add(Circle(radius=.65, color=GOLD, stroke_width=3))
        for x in range(-3,4):
            for y in range(-2,3):
                if x or y:
                    integer_grid.add(Dot([.65*x,.65*y,0], radius=.035, color=TEAL))
        integer_grid.add(label("0", [.13,-.19,0], 23))
        beat("PROOF SCHEMATIC",
             r"G_H=a+bi\ne0,\quad a,b\in\mathbb Z\quad\Longrightarrow\quad |G_H|\ge1",
             ("Clear denominators: a nonzero Gaussian integer remains.",
              "This floor belongs to the cleared determinant."),
             world=integer_grid,
             view=dict(phi=0, theta=-90*DEGREES, zoom=1), fs=32)
        centers = VGroup()
        moving_centers = VGroup()
        for x in [-3,0,3]:
            centers.add(Dot([x,0,0], radius=.08, color=GOLD))
            moving_centers.add(Dot([x+.5,.6,0], radius=.065, color=CORAL))
        centers.add(moving_centers,
                    label("Exact periods", [0,-.55,0], 25, GOLD),
                    label("Rational centers", [0,1.2,0], 25, CORAL))
        beat("PROOF SCHEMATIC",
             r"2ij\,\frac{p_i}{q_i}\ \approx\ 2\pi i j",
             ("Close fractions put rational centers near exact logarithmic periods.",),
             world=centers,
             motion=[moving_centers.animate.shift([-.38,-.45,0])], motion_time=1.5)
        rails = VGroup()
        floor = Line([-4,-.25,0], [4,-.25,0], color=GOLD, stroke_width=6)
        ceiling = VGroup(Line([-4,1,0], [4,1,0], color=CORAL, stroke_width=6),
                         label("analytic ceiling", [2.6,1.3,0],24,CORAL))
        rails.add(floor, ceiling, label("arithmetic floor", [-2.6,.05,0],24,GOLD),
                  label("Schematic: same normalized quantity", [0,-1.6,0],24))
        rails.add(label("Fix parameters; then increase degree.", [0, 1.65, 0], 24))
        beat("PROOF SCHEMATIC",
             None,
             ("Repeated Taylor degrees give equal rows within groups.",
              "Collision savings or error powers force contradiction."),
             world=rails, motion=[ceiling.animate.shift([0,-1.9,0])], motion_time=2, fs=34)

        # 6. Actual sparse summands; linear scales, no interpolated curve.
        values = [(3,1.859769198533657),(22,1.198717717715873),
                  (333,.000348028891719564),(355,24.59818122070685)]
        def hp(n,a):
            return np.array([-1.3 + n/400*6.1, -1.45+a/25*2.95, 0])
        stems = VGroup(Line(hp(0,0),hp(400,0),color=TEAL,stroke_width=2),
                       Line(hp(0,0),hp(0,26),color=TEAL,stroke_width=2))
        for n in [0,200,400]:
            stems.add(Line(hp(n,0)+[0,-.06,0],hp(n,0)+[0,.06,0],color=INK))
            stems.add(label(str(n),hp(n,0)+[0,-.27,0],20))
        for a in [0,20]:
            stems.add(label(str(a),hp(0,a)+[-.35,0,0],20))
        for n,a in values:
            stems.add(Line(hp(n,0),hp(n,a),color=CORAL,stroke_width=4),
                      Dot(hp(n,a),color=CORAL,radius=.045))
        stems.add(label("n",hp(400,0)+[.32,0,0],24),
                  label("Linear scales", [1.8,1.6,0],23))
        stems.add(label("n       summand",[-4.15,1.2,0],23))
        rows = ["3        1.859769", "22      1.198718", "333    0.000348029", "355    24.598181"]
        for i,s in enumerate(rows):
            stems.add(label(s,[-4.15,.65-.47*i,0],24,CORAL if i==3 else INK))
        spike_ring = Circle(radius=.14,color=GOLD,stroke_width=3).move_to(hp(355,values[-1][1]))
        stems.add(spike_ring)
        beat("FLINT–HILLS SERIES",
             r"\sum_{n\ge1}\frac{1}{n^3\sin^2 n}",
             ("Angles are radians; these four summands are computed.",),
             world=stems)
        beat("WHY 355 SPIKES",
             r"355-113\pi=0.000030144353\ldots",
             ("355 nearly meets 113π, making sine tiny.",))
        beat("WHY SPACING MATTERS",
             r"|\sin n|=|\sin(n-q\pi)|,\qquad q\in\mathbb Z",
             ("Individual bounds need not sum finitely.",
              "Finite plots cannot prove convergence."), fs=35)

        # 7. Circle of actual fractional parts, then symbolic bounds.
        turns = [(8,.1327412287183459),(9,.2743338823081391),
                 (10,.4159265358979324),(11,.5575191894877256),
                 (12,.6991118430775189),(13,.8407044966673121),
                 (14,.9822971502571053),(15,.1238898038468986)]
        center = np.array([-2.55,-.12,0])
        radius = 1.45
        def cp(t,r=radius):
            return center+np.array([r*math.cos(TAU*t),r*math.sin(TAU*t),0])
        def circle_world(seen=False):
            g = VGroup(Circle(radius=radius,color=TEAL,stroke_width=3).move_to(center),
                       Dot(cp(0),radius=.065,color=GOLD))
            for q,t in turns:
                g.add(Dot(cp(t),radius=.025,color=CORAL))
            g.add(label("0",cp(0)+[.25,0,0],26,GOLD,read=0 if seen else .4),
                  label("½",cp(.5)+[-.22,0,0],24,read=0 if seen else .4),
                  label("q = 8, …, 15",center,26,read=0 if seen else 2),
                  label("Distances in turns",[-2.55,-1.99,0],23,read=0 if seen else 1.2))
            return g
        circle = circle_world()
        def inset(t):
            return np.array([.65+4.7*(t-.115)/.025,.15,0])
        circle.add(Line(inset(.115),inset(.140),color=TEAL,stroke_width=2),
                   label("Magnified turns", [3,1.1,0],25),
                   label("0.115",inset(.115)+[0,-.35,0],22),
                   label("0.140",inset(.140)+[0,-.35,0],22))
        for q,t in [turns[-1],turns[0]]:
            circle.add(Dot(inset(t),color=CORAL,radius=.055),
                       label("q="+str(q),inset(t)+[0,.35,0],24,CORAL))
        beat("FRACTIONAL PARTS",
             lines=("Discard the integer part of qπ.",
                    "Wrap the remainder counterclockwise around one circle turn."),
             world=circle)
        beat("DISTANCE TO AN INTEGER",
             r"\|q\pi\|\ge c q^{1-\nu},\qquad c>0,\quad 2<\nu<\frac52,\quad q\ge1",
             ("Double bars: distance to the nearest integer.",
              "Every positive integer q qualifies; finite exceptions enter c."),
             fs=32)
        ordered = circle_world(seen=True)
        for j,(_,t) in enumerate([turns[-1],turns[0],turns[1]],start=1):
            ordered.add(Arc(radius=radius+.08*j, start_angle=0, angle=TAU*t,
                            arc_center=center,color=GOLD,stroke_width=2))
            ordered.add(label(r"\text{distance }"+str(j)+r"\ \ge "+str(j)+r"d",
                              [2.65,1.08-.63*j,0],31,GOLD,True))
        ordered.add(label("Ordered on either half-circle",[2.65,1.15,0],25))
        beat("SPACING",
             r"d=c(2K)^{1-\nu},\qquad K\le q<2K",
             ("Points avoid zero and each other by at least d.",
              "Differences of indices obey the same bound."),
             world=ordered, fs=35)
        beat("BOUND THE BLOCK",
             r"\begin{gathered}\sum_{K\le q<2K}\frac1{q^3\|q\pi\|^2}"
             r"\le\frac{2}{K^3d^2}\sum_{j\ge1}\frac1{j^2}\\"
             r"=O\!\left(K^{2\nu-5}\right)\end{gathered}",
             ("O bounds the sum by a constant times this power.",), fs=36)
        blocks = VGroup(Line([-4.7,-1.4,0],[4.8,-1.4,0],color=TEAL,stroke_width=2))
        for j in range(7):
            h = 2.7*2**(-j/2)
            bar = Rectangle(width=.67,height=h,fill_color=TEAL,fill_opacity=.8,
                            stroke_color=TEAL,stroke_width=1).move_to([-4+j*1.3,-1.4+h/2,0])
            blocks.add(bar, label(str(2**j),[-4+j*1.3,-1.76,0],23))
        blocks.add(label("K",[-4.8,-1.76,0],25),
                   label("Schematic bound; constant unspecified",[0,1.63,0],24))
        beat("SUMMABLE BLOCKS",
             r"\nu=\frac94:\qquad O(K^{-1/2}),\qquad K=1,2,4,\ldots",
             ("Doubling shrinks bounds by 1/√2; their sum is finite.",),
             world=blocks, fs=35)
        grouping = VGroup()
        for x in [-2.25,-.75,.75,2.25]:
            grouping.add(RoundedRectangle(width=.95,height=.68,corner_radius=.12,
                         fill_color=CORAL,fill_opacity=.2,stroke_color=CORAL).move_to([x,.3,0]),
                         Line([x,-.1,0],[0,-.85,0],color=TEAL,stroke_width=1.5))
        grouping.add(label("q=0: a finite group", [3,-.85,0],23),
                     Dot([0,-.85,0],color=GOLD,radius=.08),
                     label(r"q\pi",[0,-1.3,0],30,GOLD,True),
                     label("Schematic: n are integers; q labels groups",[0,1.2,0],25))
        beat("BACK TO SINE",
             r"\sum_{n\ \mathrm{in\ group}\ q}\frac{1}{n^3\sin^2n}"
             r"\le\frac{8}{\pi}\frac{1}{q^3\|q\pi\|^2}\quad(q\ge1)",
             ("Nearest qπ groups contain at most four integers n.",
              "Sine bounds each group by a constant times its q-term."),
             world=grouping, fs=35)

        # 8. Return to both true error scales without conflating them.
        closing = VGroup()
        for yy,scale,e,frac in [(0.68,3,1.264489267349619,r"22/7"),
                                (-.86,7,2.667641890624223,r"355/113")]:
            def p(v,y=yy):
                return np.array([-2.4+1.8*v,y,0])
            closing.add(Line(p(0),p(3.1),color=TEAL,stroke_width=3),
                        Dot(p(0),color=GOLD,radius=.065),
                        Dot(p(e),color=CORAL,radius=.065),
                        label(frac,p(e)+[0,.34,0],27,CORAL,True),
                        label(r"10^{"+str(scale)+r"}(x-\pi)",[-4.7,yy,0],27,INK,True),
                        label("0",p(0)+[0,-.3,0],23,GOLD))
        beat("CLASSICAL ≥2   ·   MANUSCRIPT ≤2", r"\mu(\pi)=2",
             ("Spacing then yields Flint–Hills convergence.",),
             world=closing, fs=47)
        beat("OpenAI · September 24 2026 · family 017",
             lines=("Full proof unchecked here; Lean comparator not run.",
                    "Lean covers μ(π)=2, excluding Flint–Hills. Pinned scope: companion dossier."),
             world=VGroup())
        assert len(self.reading_log) == len(PLANNED_HOLDS) == 27
        assert all(abs(row[4] - expected) < 1e-8
                   for row, expected in zip(self.reading_log, PLANNED_HOLDS))
        assert abs(self.elapsed - PLANNED_DURATION) < 1e-8
