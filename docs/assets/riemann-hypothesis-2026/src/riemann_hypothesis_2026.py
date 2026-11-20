from manim import *
import numpy as np

BG = "#0b0e14"
INK = "#faf9f5"
CYAN = "#38bdf8"
CORAL = "#d97757"
GOLD = "#eab308"
EMERALD = "#34d399"
SLATE = "#94a3b8"
DIM = "#1e293b"

# First five non-trivial zero heights on the critical line Re(s) = 1/2
ZERO_HEIGHTS = [14.134725, 21.022040, 25.010858, 30.424876, 32.935062]


def _zeta_eta_mag(sigma: float, t: float, terms: int = 45) -> float:
    """Smooth Dirichlet-eta approximation of |zeta(sigma + i*t)| in the critical strip."""
    s = complex(sigma, t)
    n = np.arange(1, terms + 1, dtype=np.float64)
    signs = np.where((n.astype(int) % 2) == 1, 1.0, -1.0)
    eta_val = np.sum(signs * (n ** (-s)))
    denom = 1.0 - (2.0 ** (1.0 - s))
    if abs(denom) < 1e-6:
        return 2.5
    val = abs(eta_val / denom)
    return float(np.log1p(min(val, 14.0)))


def _von_mangoldt(n: int) -> float:
    """Return Lambda(n) = log(p) if n = p^k for prime p, else 0."""
    if n < 2:
        return 0.0
    m = n
    p = 2
    while p * p <= m:
        if m % p == 0:
            while m % p == 0:
                m //= p
            return float(np.log(p)) if m == 1 else 0.0
        p += 1
    return float(np.log(n))


class RiemannThetaLiftJourney(ThreeDScene):
    def construct(self):
        self.camera.background_color = BG
        self.set_camera_orientation(phi=0 * DEGREES, theta=-90 * DEGREES)

        self._hud_header = None
        self._hud_eq = None
        self._hud_caption = None

        def fixed(mob):
            self.add_fixed_in_frame_mobjects(mob)
            self.remove(mob)
            return mob

        def show_header(title_text: str, eq_tex: str | None = None, color=CYAN):
            anims = []
            if self._hud_header is not None:
                anims.append(FadeOut(self._hud_header, shift=UP * 0.15))
            if self._hud_eq is not None:
                anims.append(FadeOut(self._hud_eq, shift=UP * 0.15))
                self._hud_eq = None

            hdr = Tex(title_text, font_size=34, color=color).to_corner(UL, buff=0.42)
            fixed(hdr)
            anims.append(FadeIn(hdr, shift=DOWN * 0.12))
            self._hud_header = hdr

            if eq_tex:
                eq = MathTex(eq_tex, font_size=32, color=INK).to_corner(UR, buff=0.42)
                if eq.width > 5.8:
                    eq.scale_to_fit_width(5.8)
                fixed(eq)
                anims.append(FadeIn(eq, shift=DOWN * 0.12))
                self._hud_eq = eq
            return anims

        def show_caption(text: str):
            anims = []
            if self._hud_caption is not None:
                anims.append(FadeOut(self._hud_caption, shift=DOWN * 0.1))
            cap = Tex(text, font_size=28, color=SLATE).to_edge(DOWN, buff=0.38)
            if cap.width > 12.8:
                cap.scale_to_fit_width(12.8)
            fixed(cap)
            anims.append(FadeIn(cap, shift=UP * 0.1))
            self._hud_caption = cap
            return anims

        def clear_hud():
            anims = []
            for mob in (self._hud_header, self._hud_eq, self._hud_caption):
                if mob is not None:
                    anims.append(FadeOut(mob))
            self._hud_header = None
            self._hud_eq = None
            self._hud_caption = None
            return anims

        # =====================================================================
        # OPENING TITLE CARD
        # =====================================================================
        title = Tex(r"Chaining Theta Lifts to the Critical Line", font_size=52, color=INK)
        subtitle = Tex(
            r"The November 20, 2026 Riemann Hypothesis Proof Announcements",
            font_size=29,
            color=CYAN,
        ).next_to(title, DOWN, buff=0.35)
        badge = Tex(
            r"Rendered by the Gemini 4 Neon Math-To-Manim Pipeline",
            font_size=22,
            color=GOLD,
        ).next_to(subtitle, DOWN, buff=0.55)
        opening = VGroup(title, subtitle, badge).move_to(ORIGIN)
        fixed(opening)

        self.play(FadeIn(title, shift=UP * 0.2), run_time=1.0)
        self.play(FadeIn(subtitle, shift=UP * 0.15), FadeIn(badge), run_time=0.9)
        self.wait(1.6)
        self.play(FadeOut(opening, shift=UP * 0.2), run_time=0.8)

        # =====================================================================
        # ACT 1: THE CRITICAL STRIP & FIRST FIVE ZEROS OF ZETA(s)
        # =====================================================================
        self.move_camera(phi=64 * DEGREES, theta=-55 * DEGREES, run_time=1.2)

        axes = ThreeDAxes(
            x_range=[0.0, 1.0, 0.25],
            y_range=[10.0, 35.0, 5.0],
            z_range=[0.0, 2.6, 0.5],
            x_length=5.2,
            y_length=7.4,
            z_length=3.0,
            axis_config={"color": SLATE, "stroke_width": 1.6},
        ).shift(DOWN * 0.2)

        def strip_point(sigma: float, t: float, z: float) -> np.ndarray:
            return axes.c2p(sigma, t, z)

        zeta_surface = Surface(
            lambda u, v: strip_point(u, v, _zeta_eta_mag(u, v, terms=36)),
            u_range=[0.12, 0.90],
            v_range=[11.0, 34.5],
            resolution=(18, 42),
            fill_opacity=0.82,
            stroke_width=0.45,
            stroke_color=CYAN,
        )
        zeta_surface.set_fill_by_value(
            axes=axes,
            colorscale=[(CORAL, 0.05), (GOLD, 0.55), (CYAN, 1.25), (EMERALD, 2.2)],
            axis=2,
        )

        # Critical line Re(s) = 1/2 projected on z=0 and along the surface valley
        crit_base = Line3D(
            start=strip_point(0.5, 11.0, 0.0),
            end=strip_point(0.5, 34.5, 0.0),
            color=GOLD,
            thickness=0.025,
        )
        crit_ridge = ParametricFunction(
            lambda t: strip_point(0.5, t, _zeta_eta_mag(0.5, t, terms=36) + 0.03),
            t_range=[11.0, 34.5, 0.2],
            color=GOLD,
            stroke_width=3.2,
        )

        zero_spheres = VGroup()
        zero_stems = VGroup()
        for t0 in ZERO_HEIGHTS:
            sp = Sphere(radius=0.11, resolution=(12, 12)).set_color(CORAL)
            sp.move_to(strip_point(0.5, t0, 0.05))
            stem = Line3D(
                start=strip_point(0.5, t0, 0.0),
                end=strip_point(0.5, t0, 1.65),
                color=CORAL,
                thickness=0.012,
            )
            zero_spheres.add(sp)
            zero_stems.add(stem)

        self.play(
            *show_header(r"Act I: The Critical Strip", r"\zeta(s) = 0 \implies \operatorname{Re}(s) = \tfrac{1}{2}", color=CYAN),
            *show_caption(r"For 167 years, every known non-trivial zero of $\zeta(s)$ has lain on $\operatorname{Re}(s)=\tfrac{1}{2}$."),
            Create(axes),
            run_time=1.3,
        )
        self.play(Create(zeta_surface), run_time=2.2)
        self.play(Create(crit_base), Create(crit_ridge), run_time=1.4)
        self.play(
            LaggedStart(*[FadeIn(s, scale=0.4) for s in zero_spheres], lag_ratio=0.18),
            LaggedStart(*[Create(st) for st in zero_stems], lag_ratio=0.18),
            *show_caption(r"First five zero wells at $t \approx 14.13,\; 21.02,\; 25.01,\; 30.42,\; 32.94$."),
            run_time=2.2,
        )
        self.begin_ambient_camera_rotation(rate=0.14)
        self.wait(3.2)
        self.stop_ambient_camera_rotation()

        act1_group = VGroup(axes, zeta_surface, crit_base, crit_ridge, zero_spheres, zero_stems)
        self.play(FadeOut(act1_group), run_time=1.0)

        # =====================================================================
        # ACT 2: FUNCTION FIELDS (STEPANOV) VS. THE INTEGERS (NO DERIVATIVE)
        # =====================================================================
        self.move_camera(phi=62 * DEGREES, theta=-78 * DEGREES, run_time=1.0)

        # Left world: Smooth algebraic curve over F_q[t] with tangent multiplicity rings
        curve = ParametricFunction(
            lambda u: np.array([-3.2 + 1.35 * np.cos(u), 1.35 * np.sin(u), 0.55 * np.sin(2 * u)]),
            t_range=[0, TAU, 0.05],
            color=CYAN,
            stroke_width=4.0,
        )
        mult_rings = VGroup()
        for ang in [0.4, 2.2, 4.1]:
            pt = np.array([-3.2 + 1.35 * np.cos(ang), 1.35 * np.sin(ang), 0.55 * np.sin(2 * ang)])
            for r_i, op in [(0.22, 0.9), (0.38, 0.55), (0.54, 0.3)]:
                ring = Torus(major_radius=r_i, minor_radius=0.018, resolution=(10, 18))
                ring.set_color(EMERALD).set_opacity(op).move_to(pt)
                mult_rings.add(ring)

        # Right world: Discrete von Mangoldt prime-power towers Lambda(n) over Z
        prime_bars = VGroup()
        base_line = Line3D(
            start=np.array([0.8, -2.0, 0.0]),
            end=np.array([5.4, 2.0, 0.0]),
            color=SLATE,
            thickness=0.015,
        )
        for idx, n_val in enumerate(range(2, 31)):
            lam = _von_mangoldt(n_val)
            if lam > 0:
                frac = idx / 28.0
                bx = 0.9 + 4.4 * frac
                by = -1.9 + 3.8 * frac
                h = 0.52 * lam
                bar = Prism(dimensions=[0.16, 0.16, h]).move_to(np.array([bx, by, h / 2.0]))
                bar.set_fill(CORAL if n_val in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29) else GOLD, opacity=0.88)
                bar.set_stroke(INK, width=0.4)
                prime_bars.add(bar)

        self.play(
            *show_header(
                r"Act II: Stepanov's Obstruction",
                r"\mathbb{F}_q[t]:\;\tfrac{d}{dt} \quad\text{vs.}\quad \mathbb{Z}:\;\Lambda(n)=\log p",
                color=GOLD,
            ),
            *show_caption(r"Over function fields $\mathbb{F}_q[t]$, differentiation builds multiplicity to trap zeros."),
            Create(curve),
            run_time=1.6,
        )
        self.play(
            LaggedStart(*[FadeIn(r, scale=0.5) for r in mult_rings], lag_ratio=0.08),
            run_time=1.5,
        )
        self.play(
            *show_caption(r"Over the integers $\mathbb{Z}$, primes form discrete spikes $\Lambda(n)$ with no naive derivative."),
            Create(base_line),
            LaggedStart(*[GrowFromPoint(b, b.get_bottom()) for b in prime_bars], lag_ratio=0.06),
            run_time=2.3,
        )
        self.move_camera(phi=68 * DEGREES, theta=-58 * DEGREES, run_time=2.2)
        self.wait(1.0)

        act2_group = VGroup(curve, mult_rings, base_line, prime_bars)
        self.play(FadeOut(act2_group), run_time=0.9)

        # =====================================================================
        # ACT 3: CHAINING THETA LIFTS (ALPOGE & CLAUDE, NOV 20, 2026)
        # =====================================================================
        self.move_camera(phi=66 * DEGREES, theta=-45 * DEGREES, run_time=1.0)

        # Base von Mangoldt ring representing sum of length X = 100
        base_disc = Circle(radius=2.2, color=CORAL, stroke_width=3.0).move_to(np.array([0.0, 0.0, -2.0]))
        base_disc.set_fill(CORAL, opacity=0.10)

        # Chain of L = sqrt(100) = 10 automorphic theta-lift rings climbing in 3D
        num_lifts = 10
        lift_rings = VGroup()
        lift_filaments = VGroup()
        ring_centers = []

        for k in range(num_lifts):
            z_k = -1.6 + 0.42 * k
            rad_k = 1.85 - 0.11 * k
            ang_k = 0.25 * k
            center_k = np.array([0.12 * np.cos(ang_k), 0.12 * np.sin(ang_k), z_k])
            ring_centers.append((center_k, rad_k, ang_k))
            col = CYAN if k % 2 == 0 else GOLD
            tor = Torus(major_radius=rad_k, minor_radius=0.045, resolution=(10, 28))
            tor.set_color(col).set_opacity(0.86).move_to(center_k)
            lift_rings.add(tor)

            if k > 0:
                prev_c, prev_r, prev_a = ring_centers[k - 1]
                for m in range(4):
                    phi_m = m * PI / 2 + 0.35 * k
                    p0 = prev_c + np.array([prev_r * np.cos(phi_m), prev_r * np.sin(phi_m), 0.0])
                    p1 = center_k + np.array([rad_k * np.cos(phi_m + 0.35), rad_k * np.sin(phi_m + 0.35), 0.0])
                    fil = Line3D(start=p0, end=p1, color=EMERALD, thickness=0.015)
                    lift_filaments.add(fil)

        # Apex beacon representing GRH cancellation across Dirichlet L-functions
        apex = Sphere(radius=0.22, resolution=(14, 14)).set_color(EMERALD).move_to(np.array([0.0, 0.0, 2.65]))

        self.play(
            *show_header(
                r"Act III: Chaining Theta Lifts",
                r"\psi(X)=\sum_{n\le X}\Lambda(n),\quad L_{\theta}\asymp\sqrt{X}",
                color=EMERALD,
            ),
            *show_caption(r"Alp\"oge \& Claude replace differentiation with Fourier-analytic chains of theta lifts."),
            Create(base_disc),
            run_time=1.3,
        )
        self.play(
            LaggedStart(*[FadeIn(r, shift=OUT * 0.25) for r in lift_rings], lag_ratio=0.14),
            LaggedStart(*[Create(f) for f in lift_filaments], lag_ratio=0.03),
            *show_caption(r"For a von Mangoldt sum of length $X=100$, the automorphic tower climbs $L=\sqrt{X}=10$ lifts."),
            run_time=3.4,
        )
        self.play(
            FadeIn(apex, scale=0.3),
            *show_caption(r"Automorphic structure extends naturally from $\zeta(s)$ to all Dirichlet $L$-functions $L(s,\chi)$."),
            run_time=1.5,
        )

        # Pulse climbing the tower while camera orbits
        pulse = Sphere(radius=0.14, resolution=(10, 10)).set_color(INK).move_to(np.array([0.0, 0.0, -1.6]))
        self.begin_ambient_camera_rotation(rate=0.22)
        self.play(FadeIn(pulse), run_time=0.4)
        self.play(pulse.animate.move_to(np.array([0.0, 0.0, 2.65])), run_time=3.0, rate_func=smooth)
        self.play(Indicate(apex, color=GOLD, scale_factor=1.35), FadeOut(pulse), run_time=1.1)
        self.stop_ambient_camera_rotation()

        act3_group = VGroup(base_disc, lift_rings, lift_filaments, apex)
        self.play(FadeOut(act3_group), run_time=0.9)

        # =====================================================================
        # ACT 4: TWIN ANNOUNCEMENTS (NOV 20, 2026) & VERIFICATION FRONTIER
        # =====================================================================
        self.move_camera(phi=70 * DEGREES, theta=-90 * DEGREES, run_time=1.0)

        # Left monument: Levent Alpoge + Claude (175,000+ Lean 4 files)
        lean_pillar = Prism(dimensions=[1.5, 1.5, 3.2]).move_to(np.array([-2.6, 0.0, 0.2]))
        lean_pillar.set_fill(CYAN, opacity=0.75).set_stroke(INK, width=1.0)

        # Right monument: Alessandro Masullo (12-year, 940-page human manuscript)
        human_pillar = Prism(dimensions=[1.5, 1.5, 2.2]).move_to(np.array([2.6, 0.0, -0.3]))
        human_pillar.set_fill(GOLD, opacity=0.78).set_stroke(INK, width=1.0)

        # Glowing critical-line bridge connecting both monuments
        bridge = Line3D(
            start=np.array([-1.8, 0.0, 1.2]),
            end=np.array([1.8, 0.0, 1.2]),
            color=EMERALD,
            thickness=0.03,
        )

        left_card = VGroup(
            Tex(r"Levent Alp\"oge \& Claude", font_size=28, color=CYAN),
            Tex(r"4-page overview + 175,000+ Lean 4 files", font_size=22, color=INK),
            Tex(r"($\sim$250,000 pages equiv., AI-assisted)", font_size=20, color=SLATE),
        ).arrange(DOWN, buff=0.14).move_to(np.array([-3.3, -2.0, 0.0]))

        right_card = VGroup(
            Tex(r"Alessandro Masullo (Stanford)", font_size=28, color=GOLD),
            Tex(r"12-year, $\sim$940-page manuscript", font_size=22, color=INK),
            Tex(r"(All-human, announced by Ravi Vakil)", font_size=20, color=SLATE),
        ).arrange(DOWN, buff=0.14).move_to(np.array([3.3, -2.0, 0.0]))

        fixed(left_card)
        fixed(right_card)

        self.play(
            *show_header(
                r"Act IV: Two Claims, One Day",
                r"L(s,\chi)=0 \implies \operatorname{Re}(s)=\tfrac{1}{2}",
                color=INK,
            ),
            *show_caption(r"November 20, 2026: both an AI-formalized Lean archive and a 12-year human proof arrived."),
            GrowFromPoint(lean_pillar, np.array([-2.6, 0.0, -1.4])),
            GrowFromPoint(human_pillar, np.array([2.6, 0.0, -1.4])),
            run_time=1.8,
        )
        self.play(
            Create(bridge),
            FadeIn(left_card, shift=UP * 0.15),
            FadeIn(right_card, shift=UP * 0.15),
            run_time=1.4,
        )
        self.wait(2.8)

        # Closing epilogue
        self.play(
            FadeOut(VGroup(lean_pillar, human_pillar, bridge)),
            FadeOut(left_card),
            FadeOut(right_card),
            *clear_hud(),
            run_time=1.0,
        )

        closing = VGroup(
            Tex(r"Neither proof is yet peer-verified.", font_size=42, color=CORAL),
            Tex(
                r"Independent mathematicians and Lean kernels now audit the critical line.",
                font_size=28,
                color=INK,
            ),
            MathTex(r"\operatorname{Re}(s) = \tfrac{1}{2}", font_size=44, color=GOLD),
        ).arrange(DOWN, buff=0.4).move_to(ORIGIN)
        fixed(closing)

        self.play(FadeIn(closing, shift=UP * 0.18), run_time=1.2)
        self.wait(2.4)
        self.play(FadeOut(closing), run_time=0.9)
