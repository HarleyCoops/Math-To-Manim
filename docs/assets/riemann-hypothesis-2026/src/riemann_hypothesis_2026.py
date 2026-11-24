from manim import *
import numpy as np

BG = "#080c14"
CARD_BG = "#0f172a"
INK = "#faf9f5"
CYAN = "#38bdf8"
CORAL = "#f97316"
GOLD = "#eab308"
EMERALD = "#34d399"
SLATE = "#94a3b8"

ZEROS = [
    14.134725, 21.022040, 25.010858, 30.424876, 32.935062,
    37.586178, 40.918719, 43.327073, 48.005151, 49.773832,
    52.970321, 56.446248, 59.347044, 60.831779, 65.112544,
]


def _zeta_log_mag(sigma: float, t: float, terms: int = 38) -> float:
    """Dirichlet-eta approximation of log(1 + |zeta(sigma + i*t)|)."""
    s = complex(sigma, t)
    n = np.arange(1, terms + 1, dtype=np.float64)
    signs = np.where((n.astype(int) % 2) == 1, 1.0, -1.0)
    eta = np.sum(signs * (n ** (-s)))
    denom = 1.0 - (2.0 ** (1.0 - s))
    if abs(denom) < 1e-6:
        return 2.4
    return float(np.log1p(min(abs(eta / denom), 14.0)))


def _von_mangoldt(n: int) -> float:
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


def _explicit_wave(x: float, num_zeros: int) -> float:
    """Fourier zero-sum approximation to psi(x) - x using first num_zeros on Re(s)=1/2."""
    total = 0.0
    lx = np.log(max(x, 1.01))
    sx = np.sqrt(max(x, 1.01))
    for g in ZEROS[:num_zeros]:
        total += -2.0 * sx * np.cos(g * lx - np.arctan2(g, 0.5)) / np.hypot(0.5, g)
    return float(total)


class RiemannThetaLiftCinema(ThreeDScene):
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

        def pill(mob, border_col=SLATE, pad_x=0.22, pad_y=0.12):
            bg = RoundedRectangle(
                corner_radius=0.12,
                width=mob.width + 2 * pad_x,
                height=mob.height + 2 * pad_y,
                fill_color=CARD_BG,
                fill_opacity=0.86,
                stroke_color=border_col,
                stroke_width=1.2,
            ).move_to(mob)
            return VGroup(bg, mob)

        def show_header(title_text: str, eq_tex: str | None = None, color=CYAN):
            anims = []
            if self._hud_header is not None:
                anims.append(FadeOut(self._hud_header, shift=UP * 0.15))
            if self._hud_eq is not None:
                anims.append(FadeOut(self._hud_eq, shift=UP * 0.15))
                self._hud_eq = None

            hdr_txt = Tex(title_text, font_size=30, color=color)
            hdr = pill(hdr_txt, border_col=color).to_corner(UL, buff=0.35)
            fixed(hdr)
            anims.append(FadeIn(hdr, shift=DOWN * 0.12))
            self._hud_header = hdr

            if eq_tex:
                eq_txt = MathTex(eq_tex, font_size=28, color=INK)
                if eq_txt.width > 5.6:
                    eq_txt.scale_to_fit_width(5.6)
                eq = pill(eq_txt, border_col=SLATE).to_corner(UR, buff=0.35)
                fixed(eq)
                anims.append(FadeIn(eq, shift=DOWN * 0.12))
                self._hud_eq = eq
            return anims

        def show_caption(text: str):
            anims = []
            if self._hud_caption is not None:
                anims.append(FadeOut(self._hud_caption, shift=DOWN * 0.1))
            cap_txt = Tex(text, font_size=25, color=INK)
            if cap_txt.width > 12.2:
                cap_txt.scale_to_fit_width(12.2)
            cap = pill(cap_txt, border_col=SLATE, pad_x=0.26, pad_y=0.10).to_edge(DOWN, buff=0.28)
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
        t1 = Tex(r"Chaining Theta Lifts to the Critical Line", font_size=50, color=INK)
        t2 = Tex(
            r"How the November 20, 2026 Riemann Hypothesis Proof Claims Work",
            font_size=27,
            color=CYAN,
        ).next_to(t1, DOWN, buff=0.32)
        rule = Line(LEFT * 4.2, RIGHT * 4.2, color=GOLD, stroke_width=2.0).next_to(t2, DOWN, buff=0.32)
        t3 = Tex(
            r"Gemini 4 Neon · Manim Community 3D Pipeline",
            font_size=22,
            color=SLATE,
        ).next_to(rule, DOWN, buff=0.28)
        opening = VGroup(t1, t2, rule, t3).move_to(ORIGIN)
        fixed(opening)

        self.play(FadeIn(t1, shift=UP * 0.2), run_time=0.9)
        self.play(FadeIn(t2, shift=UP * 0.15), Create(rule), FadeIn(t3), run_time=0.9)
        self.wait(1.4)
        self.play(FadeOut(opening, shift=UP * 0.2), run_time=0.7)

        # =====================================================================
        # ACT 1: HIGH-RES 3D CRITICAL STRIP & TRANSLUCENT CRITICAL PLANE
        # =====================================================================
        self.move_camera(phi=64 * DEGREES, theta=-54 * DEGREES, run_time=1.0)

        axes = ThreeDAxes(
            x_range=[0.0, 1.0, 0.25],
            y_range=[10.0, 35.0, 5.0],
            z_range=[0.0, 2.6, 0.5],
            x_length=5.4,
            y_length=7.6,
            z_length=3.0,
            axis_config={"color": SLATE, "stroke_width": 1.5},
        ).shift(DOWN * 0.15)

        def sp(sigma, t, z):
            return axes.c2p(sigma, t, z)

        zeta_surf = Surface(
            lambda u, v: sp(u, v, _zeta_log_mag(u, v, terms=36)),
            u_range=[0.12, 0.90],
            v_range=[11.0, 34.5],
            resolution=(22, 50),
            fill_opacity=0.84,
            stroke_width=0.35,
            stroke_color=CYAN,
        )
        zeta_surf.set_fill_by_value(
            axes=axes,
            colorscale=[(CORAL, 0.06), (GOLD, 0.55), (CYAN, 1.25), (EMERALD, 2.2)],
            axis=2,
        )

        # Translucent vertical Critical Plane Re(s) = 1/2
        crit_plane = Surface(
            lambda u, v: sp(0.5, u, v),
            u_range=[11.0, 34.5],
            v_range=[0.0, 2.1],
            resolution=(8, 4),
            fill_color=GOLD,
            fill_opacity=0.14,
            stroke_width=0.6,
            stroke_color=GOLD,
        )
        crit_ridge = ParametricFunction(
            lambda t: sp(0.5, t, _zeta_log_mag(0.5, t, terms=36) + 0.03),
            t_range=[11.0, 34.5, 0.18],
            color=GOLD,
            stroke_width=3.4,
        )

        zero_markers = VGroup()
        for t0 in ZEROS[:5]:
            ring = Circle(radius=0.16, color=CORAL, stroke_width=2.8).move_to(sp(0.5, t0, 0.04))
            orb = Sphere(radius=0.10, resolution=(10, 10)).set_color(CORAL).move_to(sp(0.5, t0, 0.05))
            beam = Line3D(sp(0.5, t0, 0.0), sp(0.5, t0, 1.8), color=CORAL, thickness=0.013)
            zero_markers.add(VGroup(ring, orb, beam))

        self.play(
            *show_header(r"Act I: The Critical Strip", r"\zeta(s)=0 \implies \operatorname{Re}(s)=\tfrac{1}{2}", color=CYAN),
            *show_caption(r"The 3D landscape of $\log(1+|\zeta(\sigma+it)|)$ drops to zero along the golden plane $\operatorname{Re}(s)=\tfrac{1}{2}$."),
            Create(axes),
            run_time=1.1,
        )
        self.play(Create(zeta_surf), run_time=2.0)
        self.play(FadeIn(crit_plane), Create(crit_ridge), run_time=1.2)
        self.play(
            LaggedStart(*[FadeIn(m, scale=0.5) for m in zero_markers], lag_ratio=0.16),
            *show_caption(r"First five non-trivial zero wells at $t \approx 14.13,\; 21.02,\; 25.01,\; 30.42,\; 32.94$."),
            run_time=2.0,
        )
        self.move_camera(phi=70 * DEGREES, theta=-28 * DEGREES, run_time=2.6)
        self.play(FadeOut(VGroup(axes, zeta_surf, crit_plane, crit_ridge, zero_markers)), run_time=0.8)

        # =====================================================================
        # ACT 2: WEIL EXPLICIT FORMULA (PRIMES = ZERO HARMONICS)
        # =====================================================================
        self.move_camera(phi=0 * DEGREES, theta=-90 * DEGREES, run_time=0.8)

        ax2 = Axes(
            x_range=[2, 42, 5],
            y_range=[-5.5, 5.5, 2.5],
            x_length=10.6,
            y_length=4.3,
            axis_config={"color": SLATE, "stroke_width": 1.6},
        ).shift(DOWN * 0.15)
        ax2_lbl_x = Tex(r"$X$", font_size=24, color=SLATE).next_to(ax2.x_axis, RIGHT, buff=0.15)
        ax2_lbl_y = MathTex(r"\psi(X) - X", font_size=24, color=CORAL).next_to(ax2.y_axis, UP, buff=0.12)

        # Build true staircase psi(X) - X
        stair_pts = []
        psi_val = 0.0
        for x_int in range(2, 42):
            stair_pts.append(ax2.c2p(x_int, psi_val - x_int))
            psi_val += _von_mangoldt(x_int)
            stair_pts.append(ax2.c2p(x_int, psi_val - x_int))
        stair_curve = VMobject(color=CORAL, stroke_width=3.0).set_points_as_corners(stair_pts)

        # Square-root envelope +/- 0.85 * sqrt(X)
        env_pos = ax2.plot(lambda x: 0.72 * np.sqrt(x), x_range=[2, 41], color=GOLD, stroke_width=1.6)
        env_neg = ax2.plot(lambda x: -0.72 * np.sqrt(x), x_range=[2, 41], color=GOLD, stroke_width=1.6)
        env_pos_d = DashedVMobject(env_pos, num_dashes=26)
        env_neg_d = DashedVMobject(env_neg, num_dashes=26)

        w3 = ax2.plot(lambda x: _explicit_wave(x, 3), x_range=[2, 41, 0.25], color=CYAN, stroke_width=2.6)
        w8 = ax2.plot(lambda x: _explicit_wave(x, 8), x_range=[2, 41, 0.2], color=CYAN, stroke_width=2.8)
        w15 = ax2.plot(lambda x: _explicit_wave(x, 15), x_range=[2, 41, 0.18], color=EMERALD, stroke_width=3.0)

        zero_badge_3 = pill(Tex(r"3 zeta zeros", font_size=24, color=CYAN), border_col=CYAN).move_to(ax2.c2p(35, 4.2))
        zero_badge_8 = pill(Tex(r"8 zeta zeros", font_size=24, color=CYAN), border_col=CYAN).move_to(ax2.c2p(35, 4.2))
        zero_badge_15 = pill(Tex(r"15 zeta zeros", font_size=24, color=EMERALD), border_col=EMERALD).move_to(ax2.c2p(35, 4.2))

        self.play(
            *show_header(r"Act II: Weil Explicit Formula", r"\psi(X) = X - \sum_{\rho}\frac{X^{\rho}}{\rho} - \log 2\pi", color=CORAL),
            *show_caption(r"Prime-power jumps $\psi(X)-X$ (coral) stay trapped inside the golden $\pm O(\sqrt{X})$ envelope."),
            Create(ax2), FadeIn(ax2_lbl_x), FadeIn(ax2_lbl_y),
            Create(env_pos_d), Create(env_neg_d),
            Create(stair_curve),
            run_time=2.2,
        )
        self.play(
            Create(w3), FadeIn(zero_badge_3),
            *show_caption(r"Each zero $\rho=\tfrac{1}{2}+i\gamma$ adds a wave; adding zeros sculpts the exact prime staircase."),
            run_time=1.8,
        )
        self.play(Transform(w3, w8), ReplacementTransform(zero_badge_3, zero_badge_8), run_time=1.5)
        self.play(Transform(w3, w15), ReplacementTransform(zero_badge_8, zero_badge_15), run_time=1.6)
        self.wait(1.0)

        self.play(FadeOut(VGroup(ax2, ax2_lbl_x, ax2_lbl_y, env_pos_d, env_neg_d, stair_curve, w3, zero_badge_15)), run_time=0.8)

        # =====================================================================
        # ACT 3: STEPANOV'S OBSTRUCTION (FUNCTION FIELDS VS. INTEGERS)
        # =====================================================================
        self.move_camera(phi=62 * DEGREES, theta=-76 * DEGREES, run_time=0.9)

        curve = ParametricFunction(
            lambda u: np.array([-3.0 + 1.35 * np.cos(u), 1.35 * np.sin(u), 0.55 * np.sin(2 * u)]),
            t_range=[0, TAU, 0.05],
            color=CYAN,
            stroke_width=4.0,
        )
        mult_rings = VGroup()
        for ang in [0.4, 2.3, 4.2]:
            pt = np.array([-3.0 + 1.35 * np.cos(ang), 1.35 * np.sin(ang), 0.55 * np.sin(2 * ang)])
            for r_i, op in [(0.22, 0.9), (0.38, 0.55), (0.54, 0.3)]:
                ring = Torus(major_radius=r_i, minor_radius=0.018, resolution=(10, 18))
                ring.set_color(EMERALD).set_opacity(op).move_to(pt)
                mult_rings.add(ring)

        prime_bars = VGroup()
        base_line = Line3D(np.array([0.8, -2.0, 0.0]), np.array([5.2, 2.0, 0.0]), color=SLATE, thickness=0.016)
        for idx, n_val in enumerate(range(2, 31)):
            lam = _von_mangoldt(n_val)
            if lam > 0:
                frac = idx / 28.0
                bx = 0.9 + 4.2 * frac
                by = -1.9 + 3.8 * frac
                h = 0.54 * lam
                bar = Prism(dimensions=[0.17, 0.17, h]).move_to(np.array([bx, by, h / 2.0]))
                bar.set_fill(CORAL if n_val in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29) else GOLD, opacity=0.9)
                bar.set_stroke(INK, width=0.45)
                prime_bars.add(bar)

        self.play(
            *show_header(r"Act III: Stepanov's Obstruction", r"\mathbb{F}_q[t]:\;\tfrac{d^k}{dt^k}P=0 \;\text{vs.}\; \mathbb{Z}:\;\Lambda(n)", color=GOLD),
            *show_caption(r"Over function fields $\mathbb{F}_q[t]$, Stepanov used derivatives to force high-order multiplicity."),
            Create(curve),
            LaggedStart(*[FadeIn(r, scale=0.5) for r in mult_rings], lag_ratio=0.07),
            run_time=2.2,
        )
        self.play(
            *show_caption(r"Over the integers $\mathbb{Z}$, prime powers form discrete spikes $\Lambda(n)=\log p$ with no naive derivative."),
            Create(base_line),
            LaggedStart(*[GrowFromPoint(b, b.get_bottom()) for b in prime_bars], lag_ratio=0.05),
            run_time=2.2,
        )
        self.move_camera(phi=68 * DEGREES, theta=-54 * DEGREES, run_time=1.8)
        self.play(FadeOut(VGroup(curve, mult_rings, base_line, prime_bars)), run_time=0.8)

        # =====================================================================
        # ACT 4: CHAINING SQRT(X) AUTOMORPHIC THETA LIFTS (ALPOGE & CLAUDE)
        # =====================================================================
        self.move_camera(phi=66 * DEGREES, theta=-45 * DEGREES, run_time=0.9)

        base_disc = Circle(radius=2.3, color=CORAL, stroke_width=3.0).move_to(np.array([0.0, 0.0, -2.0]))
        base_disc.set_fill(CORAL, opacity=0.12)

        num_lifts = 10
        lift_rings = VGroup()
        lift_filaments = VGroup()
        centers = []
        for k in range(num_lifts):
            zk = -1.6 + 0.42 * k
            rk = 1.90 - 0.11 * k
            ak = 0.25 * k
            ck = np.array([0.10 * np.cos(ak), 0.10 * np.sin(ak), zk])
            centers.append((ck, rk))
            tor = Torus(major_radius=rk, minor_radius=0.048, resolution=(10, 28))
            tor.set_color(CYAN if k % 2 == 0 else GOLD).set_opacity(0.88).move_to(ck)
            lift_rings.add(tor)
            if k > 0:
                pc, pr = centers[k - 1]
                for m in range(4):
                    pm = m * PI / 2 + 0.35 * k
                    p0 = pc + np.array([pr * np.cos(pm), pr * np.sin(pm), 0.0])
                    p1 = ck + np.array([rk * np.cos(pm + 0.35), rk * np.sin(pm + 0.35), 0.0])
                    lift_filaments.add(Line3D(p0, p1, color=EMERALD, thickness=0.016))

        apex = Sphere(radius=0.24, resolution=(14, 14)).set_color(EMERALD).move_to(np.array([0.0, 0.0, 2.68]))

        self.play(
            *show_header(r"Act IV: Chaining Theta Lifts", r"\psi(X)=\sum_{n\le X}\Lambda(n),\quad L_{\theta}(X)\asymp\sqrt{X}", color=EMERALD),
            *show_caption(r"Alp\"oge \& Claude bridge the toy Fourier trick to $\mathbb{Z}$ via chains of automorphic theta lifts."),
            Create(base_disc),
            run_time=1.2,
        )
        self.play(
            LaggedStart(*[FadeIn(r, shift=OUT * 0.22) for r in lift_rings], lag_ratio=0.12),
            LaggedStart(*[Create(f) for f in lift_filaments], lag_ratio=0.025),
            *show_caption(r"For a von Mangoldt sum of length $X=100$, the tower climbs $L=\sqrt{X}=10$ higher-rank lifts."),
            run_time=3.2,
        )
        self.play(
            FadeIn(apex, scale=0.3),
            *show_caption(r"Automorphic structure extends naturally from $\zeta(s)$ to every Dirichlet $L$-function $L(s,\chi)$ (GRH)."),
            run_time=1.4,
        )

        pulse = Sphere(radius=0.15, resolution=(10, 10)).set_color(INK).move_to(np.array([0.0, 0.0, -1.6]))
        self.begin_ambient_camera_rotation(rate=0.22)
        self.play(FadeIn(pulse), run_time=0.3)
        self.play(pulse.animate.move_to(np.array([0.0, 0.0, 2.68])), run_time=2.6, rate_func=smooth)
        self.play(Indicate(apex, color=GOLD, scale_factor=1.35), FadeOut(pulse), run_time=1.0)
        self.stop_ambient_camera_rotation()

        self.play(FadeOut(VGroup(base_disc, lift_rings, lift_filaments, apex)), run_time=0.8)

        # =====================================================================
        # ACT 5: TWIN ANNOUNCEMENTS (NOV 20, 2026) — ZERO-OVERLAP MONUMENTS
        # =====================================================================
        self.move_camera(phi=70 * DEGREES, theta=-90 * DEGREES, run_time=0.9)

        # Elevate both monuments in Z so they stay cleanly above the bottom HUD cards
        lean_lattice = VGroup()
        for layer in range(4):
            box = Cube(side_length=1.15).move_to(np.array([-2.6, 0.0, 0.55 + 0.55 * layer]))
            box.set_fill(CYAN, opacity=0.28).set_stroke(CYAN, width=1.6)
            lean_lattice.add(box)

        human_col = Prism(dimensions=[1.25, 1.25, 2.15]).move_to(np.array([2.6, 0.0, 1.25]))
        human_col.set_fill(GOLD, opacity=0.72).set_stroke(INK, width=1.1)

        bridge = Line3D(np.array([-1.85, 0.0, 1.7]), np.array([1.85, 0.0, 1.7]), color=EMERALD, thickness=0.03)

        left_txt = VGroup(
            Tex(r"Levent Alp\"oge \& Claude", font_size=26, color=CYAN),
            Tex(r"4-page overview + 175,000+ Lean 4 files", font_size=20, color=INK),
            Tex(r"($\sim$250,000 pages equiv., AI-assisted)", font_size=18, color=SLATE),
        ).arrange(DOWN, buff=0.10)
        left_card = pill(left_txt, border_col=CYAN, pad_x=0.24, pad_y=0.14).move_to(np.array([-3.3, -1.95, 0.0]))

        right_txt = VGroup(
            Tex(r"Alessandro Masullo (Stanford)", font_size=26, color=GOLD),
            Tex(r"12-year, $\sim$940-page manuscript", font_size=20, color=INK),
            Tex(r"(All-human, announced by Ravi Vakil)", font_size=18, color=SLATE),
        ).arrange(DOWN, buff=0.10)
        right_card = pill(right_txt, border_col=GOLD, pad_x=0.24, pad_y=0.14).move_to(np.array([3.3, -1.95, 0.0]))

        fixed(left_card)
        fixed(right_card)

        self.play(
            *show_header(r"Act V: Two Claims, One Day", r"L(s,\chi)=0 \implies \operatorname{Re}(s)=\tfrac{1}{2}", color=INK),
            *show_caption(r"November 20, 2026: an AI-formalized Lean archive and a 12-year human proof arrived on the same day."),
            LaggedStart(*[FadeIn(b, shift=OUT * 0.2) for b in lean_lattice], lag_ratio=0.15),
            GrowFromPoint(human_col, np.array([2.6, 0.0, 0.2])),
            run_time=1.8,
        )
        self.play(
            Create(bridge),
            FadeIn(left_card, shift=UP * 0.15),
            FadeIn(right_card, shift=UP * 0.15),
            run_time=1.3,
        )
        self.wait(2.4)

        self.play(
            FadeOut(VGroup(lean_lattice, human_col, bridge)),
            FadeOut(left_card), FadeOut(right_card),
            *clear_hud(),
            run_time=0.9,
        )

        closing = VGroup(
            Tex(r"Neither proof is yet peer-verified.", font_size=42, color=CORAL),
            Tex(r"Mathematicians and Lean kernels now audit the critical line.", font_size=27, color=INK),
            MathTex(r"\operatorname{Re}(s) = \tfrac{1}{2}", font_size=46, color=GOLD),
        ).arrange(DOWN, buff=0.38).move_to(ORIGIN)
        fixed(closing)

        self.play(FadeIn(closing, shift=UP * 0.18), run_time=1.1)
        self.wait(2.2)
        self.play(FadeOut(closing), run_time=0.8)
