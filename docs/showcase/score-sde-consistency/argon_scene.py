"""Continuous-Time Score SDEs, Probability Flow ODE, and OpenAI's Consistency Models.

Produced by the Argon Google Agent SDK (`google-adk` + `google-genai`) 6-agent chain.

Mathematical foundations
------------------------
* Data distribution: symmetric bimodal Gaussian mixture
  p_0(x) = 0.5 * N(x; -mu_0, sigma_0^2) + 0.5 * N(x; +mu_0, sigma_0^2)
  with mu_0 = 2.0, sigma_0 = 0.35.
* Karras / Variance-Exploding continuous-time forward SDE on t in [epsilon, T]:
  dx = sqrt(2 t) dw_t, with epsilon = 0.002, T = 2.5, giving exact marginal variance
  v(t) = sigma_0^2 + t^2.
* Exact closed-form score vector field:
  grad_x log p_t(x) = (mu_0 * tanh(mu_0 * x / v(t)) - x) / v(t).
* Tweedie MMSE denoiser:
  D(x, t) = E[x_0 | x_t = x] = x + t^2 * grad_x log p_t(x).
* Deterministic Probability Flow ODE (Song et al., ICLR 2021):
  dx / dt = -t * grad_x log p_t(x), sharing the exact same marginals p_t(x) as the SDE.
* OpenAI Consistency Models (Song, Dhariwal, Chen, & Sutskever, ICML 2023):
  f_theta(x_t, t) = f_theta(x_t', t') = x_epsilon along every Probability Flow ODE trajectory,
  with boundary condition f_theta(x, epsilon) = x enforced via
  f_theta(x, t) = c_skip(t) * x + c_out(t) * F_theta(x, t),
  c_skip(t) = sigma_data^2 / ((t - epsilon)^2 + sigma_data^2),
  c_out(t)  = sigma_data * (t - epsilon) / sqrt(sigma_data^2 + t^2).
"""

from manim import *
import numpy as np

# ---------------------------------------------------------------------------
# Palette & Constants
# ---------------------------------------------------------------------------
INK = "#0c0c0b"
PANEL_BG = "#141619"
IVORY = "#faf9f5"
FOG = "#b0aea5"
CORAL = "#d97757"       # matter: bimodal data, stochastic SDE paths
SKY = "#6a9bcc"         # light: score field grad_x log p_t(x), ODE velocity
OLIVE = "#788c5d"       # structure: density surface p_t(x), c_skip(t)
OLIVE_BRIGHT = "#95b878"
GOLD = "#d4a27f"        # interaction: consistency map f_theta, one-step arcs
GOLD_BRIGHT = "#f2c97d"

MU_0 = 2.0
SIGMA_0 = 0.35
EPSILON = 0.002
T_MAX = 2.5
SIGMA_DATA = 0.5
BIFURCATION_T = float(np.sqrt(MU_0**2 - SIGMA_0**2))  # 1.9691368...


# ---------------------------------------------------------------------------
# Exact Mathematical Functions (tested in tests/test_score_sde_consistency.py)
# ---------------------------------------------------------------------------
def marginal_variance(t):
    """Exact variance v(t) = sigma_0^2 + t^2 under dx = sqrt(2t) dw_t."""
    t_arr = np.asarray(t, dtype=float)
    return SIGMA_0**2 + t_arr**2


def marginal_pdf(x, t):
    """Exact marginal density p_t(x) for the symmetric bimodal Gaussian mixture."""
    x_arr = np.asarray(x, dtype=float)
    v = marginal_variance(t)
    norm = 1.0 / np.sqrt(2.0 * np.pi * v)
    left = np.exp(-0.5 * (x_arr + MU_0) ** 2 / v)
    right = np.exp(-0.5 * (x_arr - MU_0) ** 2 / v)
    return 0.5 * norm * (left + right)


def exact_score(x, t):
    """Exact spatial score grad_x log p_t(x) = (mu_0 tanh(mu_0 x / v(t)) - x) / v(t)."""
    x_arr = np.asarray(x, dtype=float)
    v = marginal_variance(t)
    return (MU_0 * np.tanh(MU_0 * x_arr / v) - x_arr) / v


def tweedie_denoiser(x, t):
    """Tweedie MMSE denoiser D(x, t) = x + t^2 grad_x log p_t(x)."""
    x_arr = np.asarray(x, dtype=float)
    t_arr = np.asarray(t, dtype=float)
    return x_arr + (t_arr**2) * exact_score(x_arr, t_arr)


def prob_flow_velocity(x, t):
    """Probability Flow ODE drift dx/dt = -t * grad_x log p_t(x)."""
    t_arr = np.asarray(t, dtype=float)
    return -t_arr * exact_score(x, t_arr)


def integrate_prob_flow_ode(x_start: float, t_start: float, t_end: float = EPSILON, steps: int = 160):
    """4th-order Runge-Kutta integration of the exact Probability Flow ODE from t_start to t_end."""
    ts = np.linspace(float(t_start), float(t_end), int(steps) + 1)
    xs = np.empty_like(ts)
    xs[0] = float(x_start)
    for i in range(int(steps)):
        t_cur = ts[i]
        dt = ts[i + 1] - t_cur
        x_cur = xs[i]
        k1 = prob_flow_velocity(x_cur, t_cur)
        k2 = prob_flow_velocity(x_cur + 0.5 * dt * k1, t_cur + 0.5 * dt)
        k3 = prob_flow_velocity(x_cur + 0.5 * dt * k2, t_cur + 0.5 * dt)
        k4 = prob_flow_velocity(x_cur + dt * k3, t_cur + dt)
        xs[i + 1] = x_cur + (dt / 6.0) * (k1 + 2.0 * k2 + 2.0 * k3 + k4)
    return ts, xs


def c_skip(t, epsilon: float = EPSILON, sigma_data: float = SIGMA_DATA):
    """Consistency model skip weight: c_skip(epsilon) == 1.0."""
    t_arr = np.asarray(t, dtype=float)
    return (sigma_data**2) / ((t_arr - epsilon) ** 2 + sigma_data**2)


def c_out(t, epsilon: float = EPSILON, sigma_data: float = SIGMA_DATA):
    """Consistency model output weight: c_out(epsilon) == 0.0."""
    t_arr = np.asarray(t, dtype=float)
    return sigma_data * (t_arr - epsilon) / np.sqrt(sigma_data**2 + t_arr**2)


def consistency_map(x, t, steps: int = 160):
    """Exact consistency function f(x_t, t) = x_epsilon via the ODE flow map + boundary identity."""
    t_val = float(t)
    if abs(t_val - EPSILON) < 1e-12:
        return float(c_skip(EPSILON) * x + c_out(EPSILON) * x)
    _, xs = integrate_prob_flow_ode(float(x), t_val, EPSILON, steps=steps)
    x_eps = float(xs[-1])
    cs = float(c_skip(t_val))
    co = float(c_out(t_val))
    f_net = (x_eps - cs * float(x)) / co
    return float(cs * float(x) + co * f_net)


def forward_sde_path(x0: float, ts: np.ndarray, rng: np.random.Generator) -> np.ndarray:
    """Euler-Maruyama sample path of dx = sqrt(2t) dw_t."""
    xs = np.empty_like(ts, dtype=float)
    xs[0] = float(x0)
    for i in range(len(ts) - 1):
        t_cur = max(float(ts[i]), EPSILON)
        dt = float(ts[i + 1] - ts[i])
        dw = rng.normal(0.0, np.sqrt(abs(dt)))
        xs[i + 1] = xs[i] + np.sqrt(2.0 * t_cur) * dw
    return np.clip(xs, -4.1, 4.1)


def reverse_sde_path(xT: float, ts_desc: np.ndarray, rng: np.random.Generator, noise_scale: float = 0.42) -> np.ndarray:
    """Reverse-time SDE trajectory marching from T down to epsilon with damped Brownian jitter for visual clarity."""
    xs = np.empty_like(ts_desc, dtype=float)
    xs[0] = float(xT)
    for i in range(len(ts_desc) - 1):
        t_cur = max(float(ts_desc[i]), EPSILON)
        dt = float(ts_desc[i + 1] - ts_desc[i])
        drift = -2.0 * t_cur * exact_score(xs[i], t_cur)
        dw = rng.normal(0.0, np.sqrt(abs(dt)))
        xs[i + 1] = xs[i] + drift * dt + noise_scale * np.sqrt(2.0 * t_cur) * dw
    return np.clip(xs, -4.1, 4.1)


# ---------------------------------------------------------------------------
# Coordinate Mapping & Lightweight 3D Vector Primitives
# ---------------------------------------------------------------------------
def world_pt(x, t, z=0.0):
    """Map mathematical (x in [-4.2, 4.2], t in [0, 2.5], z in [0, 0.65]) to 3D Manim world coordinates."""
    wx = 0.82 * float(x)
    wy = -2.05 + 1.52 * float(t)
    wz = -1.25 + 3.60 * float(z)
    return np.array([wx, wy, wz], dtype=float)


def marker_3d(pt, radius=0.065, color=CORAL) -> VGroup:
    """Fast, crisp 3D marker (orthogonal 3D cross-discs without heavy 512-face Sphere meshes)."""
    c1 = Circle(radius=radius, stroke_color=IVORY, stroke_width=1.2, fill_color=color, fill_opacity=0.95)
    c1.move_to(pt)
    c2 = Circle(radius=radius * 1.55, stroke_color=color, stroke_width=1.5, fill_opacity=0.0)
    c2.move_to(pt)
    return VGroup(c2, c1)


def arrow_vec_3d(start_pt, end_pt, color=SKY, stroke_width=2.6, tip_len=0.11) -> VGroup:
    """Fast 3D vector arrow with V-chevron tip in the (x, y) tangent plane."""
    p0 = np.asarray(start_pt, dtype=float)
    p1 = np.asarray(end_pt, dtype=float)
    shaft = Line(p0, p1, stroke_color=color, stroke_width=stroke_width)
    vec = p1 - p0
    norm = float(np.linalg.norm(vec))
    if norm < 1e-6:
        return VGroup(shaft)
    u = vec / norm
    perp = np.array([-u[1], u[0], 0.0], dtype=float)
    p_norm = float(np.linalg.norm(perp))
    if p_norm > 1e-6:
        perp = perp / p_norm
    else:
        perp = np.array([1.0, 0.0, 0.0], dtype=float)
    left_wing = p1 - tip_len * u + 0.52 * tip_len * perp
    right_wing = p1 - tip_len * u - 0.52 * tip_len * perp
    tip = VMobject(stroke_color=color, stroke_width=stroke_width)
    tip.set_points_as_corners([left_wing, p1, right_wing])
    return VGroup(shaft, tip)


# ---------------------------------------------------------------------------
# Main ThreeDScene
# ---------------------------------------------------------------------------
class ScoreSDEConsistencyJourney(ThreeDScene):
    """Five-act 3D visualization of Continuous-Time Score SDEs, Probability Flow ODE, and Consistency Models."""

    def _make_hud_header(self, act_tag: str, headline_str: str, formula_tex: str | None = None) -> VGroup:
        tag = Text(act_tag, font="Consolas", font_size=16, color=GOLD_BRIGHT)
        head = Text(headline_str, font="Arial", font_size=22, color=IVORY, weight=BOLD)
        top_row = VGroup(tag, head).arrange(RIGHT, buff=0.32, aligned_edge=DOWN)
        if top_row.width > 12.6:
            top_row.scale_to_fit_width(12.6)
        items = [top_row]
        if formula_tex:
            eq = MathTex(formula_tex, font_size=26, color=IVORY)
            if eq.width > 12.6:
                eq.scale_to_fit_width(12.6)
            items.append(eq)
        content = VGroup(*items).arrange(DOWN, buff=0.10)
        box = RoundedRectangle(
            corner_radius=0.12,
            width=min(max(content.width + 0.55, 8.8), 13.4),
            height=content.height + 0.28,
            fill_color=PANEL_BG,
            fill_opacity=0.90,
            stroke_color=GOLD,
            stroke_width=1.2,
            stroke_opacity=0.55,
        )
        group = VGroup(box, content)
        content.move_to(box.get_center())
        group.to_edge(UP, buff=0.14)
        return group

    def _make_hud_caption(self, caption_str: str, accent_color=SKY) -> VGroup:
        txt = Text(caption_str, font="Arial", font_size=18, color=IVORY)
        if txt.width > 12.6:
            txt.scale_to_fit_width(12.6)
        box = RoundedRectangle(
            corner_radius=0.10,
            width=txt.width + 0.50,
            height=txt.height + 0.24,
            fill_color=PANEL_BG,
            fill_opacity=0.88,
            stroke_color=accent_color,
            stroke_width=1.1,
            stroke_opacity=0.5,
        )
        group = VGroup(box, txt)
        txt.move_to(box.get_center())
        group.to_edge(DOWN, buff=0.14)
        return group

    def _swap_hud(self, old_header, old_caption, new_header, new_caption, run_time=0.8):
        self.add_fixed_in_frame_mobjects(new_header, new_caption)
        anims = [FadeIn(new_header), FadeIn(new_caption)]
        if old_header is not None:
            anims.append(FadeOut(old_header))
        if old_caption is not None:
            anims.append(FadeOut(old_caption))
        self.play(*anims, run_time=run_time)
        if old_header is not None:
            self.remove(old_header)
        if old_caption is not None:
            self.remove(old_caption)
        return new_header, new_caption

    def _update_caption(self, old_caption, new_caption_str: str, accent_color=SKY, run_time=0.6):
        new_cap = self._make_hud_caption(new_caption_str, accent_color=accent_color)
        self.add_fixed_in_frame_mobjects(new_cap)
        if old_caption is not None:
            self.play(FadeOut(old_caption), FadeIn(new_cap), run_time=run_time)
            self.remove(old_caption)
        else:
            self.play(FadeIn(new_cap), run_time=run_time)
        return new_cap

    def _build_spacetime_floor(self) -> VGroup:
        floor = VGroup()
        for xv in np.linspace(-4.0, 4.0, 9):
            p0 = world_pt(xv, 0.0, 0.0)
            p1 = world_pt(xv, T_MAX, 0.0)
            col = GOLD if abs(xv) < 1e-6 else "#2b3038"
            op = 0.45 if abs(xv) < 1e-6 else 0.28
            floor.add(Line(p0, p1, stroke_color=col, stroke_width=1.2, stroke_opacity=op))
        for tv in np.linspace(0.0, T_MAX, 6):
            p0 = world_pt(-4.2, tv, 0.0)
            p1 = world_pt(4.2, tv, 0.0)
            floor.add(Line(p0, p1, stroke_color="#2b3038", stroke_width=1.2, stroke_opacity=0.30))

        x_axis = arrow_vec_3d(world_pt(-4.3, 0.0, 0.0), world_pt(4.5, 0.0, 0.0), color=CORAL, stroke_width=3.2, tip_len=0.16)
        t_axis = arrow_vec_3d(world_pt(-4.2, 0.0, 0.0), world_pt(-4.2, T_MAX + 0.22, 0.0), color=OLIVE_BRIGHT, stroke_width=3.2, tip_len=0.16)
        z_axis = Line(world_pt(-4.2, 0.0, 0.0), world_pt(-4.2, 0.0, 0.68), stroke_color=SKY, stroke_width=3.2)
        mode_neg = marker_3d(world_pt(-MU_0, EPSILON, 0.0), radius=0.075, color=CORAL)
        mode_pos = marker_3d(world_pt(+MU_0, EPSILON, 0.0), radius=0.075, color=CORAL)
        floor.add(x_axis, t_axis, z_axis, mode_neg, mode_pos)
        return floor

    def _build_density_surface(self) -> tuple[VGroup, VGroup, VMobject, VMobject]:
        xs = np.linspace(-4.1, 4.1, 120)
        t_slices = np.linspace(EPSILON, T_MAX, 14)

        slices_group = VGroup()
        for idx, tv in enumerate(t_slices):
            zs = marginal_pdf(xs, tv)
            pts = [world_pt(xv, tv, zv) for xv, zv in zip(xs, zs)]
            curve = VMobject()
            curve.set_points_smoothly(pts)
            frac = idx / max(len(t_slices) - 1, 1)
            col = interpolate_color(ManimColor(CORAL), ManimColor(OLIVE_BRIGHT), frac)
            width = 3.6 if idx in (0, len(t_slices) - 1) else 2.0
            op = 0.95 if idx in (0, len(t_slices) - 1) else 0.58
            curve.set_stroke(col, width=width, opacity=op)
            slices_group.add(curve)

        filaments = VGroup()
        ts_dense = np.linspace(EPSILON, T_MAX, 60)
        for xv in np.linspace(-3.6, 3.6, 17):
            zs = marginal_pdf(xv, ts_dense)
            pts = [world_pt(xv, tv, zv) for tv, zv in zip(ts_dense, zs)]
            fil = VMobject()
            fil.set_points_smoothly(pts)
            is_ridge = abs(abs(xv) - MU_0) < 0.25
            fil.set_stroke(
                GOLD_BRIGHT if is_ridge else OLIVE,
                width=2.3 if is_ridge else 1.1,
                opacity=0.75 if is_ridge else 0.32,
            )
            filaments.add(fil)

        p0_curve = slices_group[0].copy().set_stroke(CORAL, width=4.2, opacity=1.0)
        pT_curve = slices_group[-1].copy().set_stroke(OLIVE_BRIGHT, width=3.8, opacity=0.95)
        return slices_group, filaments, p0_curve, pT_curve

    def construct(self):
        self.camera.background_color = INK
        self.camera.should_apply_shading = False
        self.set_camera_orientation(phi=62 * DEGREES, theta=-52 * DEGREES)

        # -------------------------------------------------------------------
        # Cold Open & Act I: Forward Diffusion SDE dx = sqrt(2t) dw_t
        # -------------------------------------------------------------------
        header, caption = self._swap_hud(
            None,
            None,
            self._make_hud_header(
                "ACT I · FORWARD DIFFUSION SDE",
                "Sharp Bimodal Data Melts into a Gaussian Horizon",
                r"\mathrm{d}x = \sqrt{2t}\,\mathrm{d}w_t,\qquad p_t(x) = \tfrac{1}{2}\mathcal{N}(-\mu_0,\sigma_0^2+t^2) + \tfrac{1}{2}\mathcal{N}(+\mu_0,\sigma_0^2+t^2)",
            ),
            self._make_hud_caption(
                "At t = epsilon = 0.002, p_0(x) has two sharp modes at x = -2.0 and x = +2.0 (sigma_0 = 0.35).",
                accent_color=CORAL,
            ),
            run_time=1.0,
        )

        floor = self._build_spacetime_floor()
        slices_group, filaments, p0_curve, pT_curve = self._build_density_surface()

        self.play(Create(floor), Create(p0_curve), run_time=2.2)
        self.wait(0.6)

        caption = self._update_caption(
            caption,
            "As time runs to T = 2.5, variance v(t) = sigma_0^2 + t^2 carves the 3D surface p_t(x); peaks merge at t* = 1.97.",
            accent_color=OLIVE_BRIGHT,
        )
        self.play(
            LaggedStart(*[Create(c) for c in slices_group], lag_ratio=0.10),
            FadeIn(filaments),
            Create(pT_curve),
            run_time=4.0,
        )
        self.move_camera(phi=60 * DEGREES, theta=-38 * DEGREES, run_time=2.5)

        caption = self._update_caption(
            caption,
            "Eight stochastic Itô sample paths wander outward from x = +/- 2.0 into the noisy Gaussian bell at t = 2.5.",
            accent_color=CORAL,
        )
        rng = np.random.default_rng(42)
        ts_path = np.linspace(EPSILON, T_MAX, 80)
        starts = [-2.15, -2.0, -1.85, -1.95, 1.85, 1.95, 2.0, 2.15]
        fwd_paths = VGroup()
        fwd_dots = VGroup()
        for x0 in starts:
            xs_p = forward_sde_path(x0, ts_path, rng)
            pts = [world_pt(xv, tv, 0.015) for xv, tv in zip(xs_p, ts_path)]
            path_mob = VMobject()
            path_mob.set_points_as_corners(pts)
            path_mob.set_stroke(CORAL, width=2.1, opacity=0.82)
            fwd_paths.add(path_mob)
            fwd_dots.add(marker_3d(pts[-1], radius=0.055, color=CORAL))

        self.play(
            LaggedStart(*[Create(p) for p in fwd_paths], lag_ratio=0.08),
            FadeIn(fwd_dots),
            run_time=3.8,
        )
        self.wait(0.8)

        # -------------------------------------------------------------------
        # Act II: The Score Vector Field grad_x log p_t(x)
        # -------------------------------------------------------------------
        header, caption = self._swap_hud(
            header,
            caption,
            self._make_hud_header(
                "ACT II · THE SCORE VECTOR FIELD",
                "The Compass in the Fog Points Uphill to the Data Modes",
                r"\nabla_x \log p_t(x) = \frac{\mu_0 \tanh\!\left(\frac{\mu_0 x}{\sigma_0^2 + t^2}\right) - x}{\sigma_0^2 + t^2},\qquad D(x,t) = x + t^2\nabla_x \log p_t(x)",
            ),
            self._make_hud_caption(
                "Sky-blue arrows show grad_x log p_t(x): vanishing on the x = 0 watershed and pointing toward x = +/- 2.0.",
                accent_color=SKY,
            ),
            run_time=0.9,
        )

        self.play(
            fwd_paths.animate.set_stroke(opacity=0.18),
            FadeOut(fwd_dots),
            slices_group.animate.set_stroke(opacity=0.28),
            filaments.animate.set_stroke(opacity=0.18),
            run_time=1.3,
        )
        self.move_camera(phi=50 * DEGREES, theta=-72 * DEGREES, run_time=2.4)

        score_arrows = VGroup()
        watershed_line = Line(
            world_pt(0.0, EPSILON, 0.02),
            world_pt(0.0, T_MAX, 0.02),
            stroke_color=GOLD_BRIGHT,
            stroke_width=2.8,
            stroke_opacity=0.85,
        )
        x_grid = [-3.4, -2.6, -1.8, -1.1, -0.45, 0.45, 1.1, 1.8, 2.6, 3.4]
        t_grid = [0.22, 0.65, 1.15, 1.70, 2.25]
        for tv in t_grid:
            for xv in x_grid:
                sc = float(exact_score(xv, tv))
                dx = np.clip(0.32 * sc, -0.58, 0.58)
                start_p = world_pt(xv, tv, 0.02)
                end_p = world_pt(xv + dx, max(tv - 0.14, EPSILON), 0.02)
                score_arrows.add(arrow_vec_3d(start_p, end_p, color=SKY, stroke_width=2.4, tip_len=0.09))

        self.play(
            Create(watershed_line),
            LaggedStart(*[FadeIn(vec) for vec in score_arrows], lag_ratio=0.02),
            run_time=3.2,
        )
        self.wait(0.7)

        caption = self._update_caption(
            caption,
            "Tweedie's formula D(x, t) = x + t^2 grad_x log p_t(x) jumps straight to the conditional expectation E[x_0 | x_t].",
            accent_color=GOLD_BRIGHT,
        )
        tweedie_group = VGroup()
        for xv in [-3.1, -1.1, 1.1, 3.1]:
            tv = 1.55
            x_hat = float(tweedie_denoiser(xv, tv))
            p_from = world_pt(xv, tv, 0.04)
            p_to = world_pt(x_hat, EPSILON, 0.04)
            arc = CubicBezier(
                p_from,
                p_from + np.array([0.0, -0.6, 0.45]),
                p_to + np.array([0.0, 0.6, 0.45]),
                p_to,
                stroke_color=GOLD_BRIGHT,
                stroke_width=2.8,
                stroke_opacity=0.90,
            )
            tweedie_group.add(arc, marker_3d(p_to, radius=0.055, color=GOLD_BRIGHT))

        self.play(Create(tweedie_group), run_time=2.6)
        self.wait(0.8)
        self.play(FadeOut(tweedie_group), FadeOut(fwd_paths), run_time=0.9)

        # -------------------------------------------------------------------
        # Act III: Reverse-Time SDE vs. Deterministic Probability Flow ODE
        # -------------------------------------------------------------------
        header, caption = self._swap_hud(
            header,
            caption,
            self._make_hud_header(
                "ACT III · PROBABILITY FLOW ODE",
                "Strip Out the Randomness, Keep the Exact Same Marginals p_t(x)",
                r"\frac{\mathrm{d}x}{\mathrm{d}t} = f(x,t) - \frac{1}{2}g(t)^2\nabla_x \log p_t(x) = -t\,\nabla_x \log p_t(x)",
            ),
            self._make_hud_caption(
                "Reverse-time SDE trajectories (coral) guided by -2t grad_x log p_t(x) dt + sqrt(2t) dw_bar_t still jitter.",
                accent_color=CORAL,
            ),
            run_time=0.9,
        )
        self.move_camera(phi=60 * DEGREES, theta=-42 * DEGREES, run_time=2.2)

        xT_samples = [-3.3, -2.3, -1.4, -0.65, 0.65, 1.4, 2.3, 3.3]
        ts_desc = np.linspace(T_MAX, EPSILON, 100)
        rev_sde_curves = VGroup()
        ode_surface_curves = VGroup()
        ode_floor_curves = VGroup()
        ode_endpoints = VGroup()

        for xT in xT_samples:
            xs_rev = reverse_sde_path(xT, ts_desc, rng)
            rev_pts = [world_pt(xv, tv, float(marginal_pdf(xv, tv)) + 0.015) for xv, tv in zip(xs_rev, ts_desc)]
            rev_mob = VMobject()
            rev_mob.set_points_as_corners(rev_pts)
            rev_mob.set_stroke(CORAL, width=2.2, opacity=0.88)
            rev_sde_curves.add(rev_mob)

            ts_ode, xs_ode = integrate_prob_flow_ode(xT, T_MAX, EPSILON, steps=99)
            surf_pts = [world_pt(xv, tv, float(marginal_pdf(xv, tv)) + 0.018) for xv, tv in zip(xs_ode, ts_ode)]
            floor_pts = [world_pt(xv, tv, 0.015) for xv, tv in zip(xs_ode, ts_ode)]

            surf_mob = VMobject()
            surf_mob.set_points_smoothly(surf_pts)
            surf_mob.set_stroke(GOLD_BRIGHT, width=3.4, opacity=0.96)
            ode_surface_curves.add(surf_mob)

            fl_mob = VMobject()
            fl_mob.set_points_smoothly(floor_pts)
            fl_mob.set_stroke(SKY, width=1.8, opacity=0.55)
            ode_floor_curves.add(fl_mob)

            ode_endpoints.add(marker_3d(surf_pts[-1], radius=0.06, color=GOLD_BRIGHT))

        self.play(
            LaggedStart(*[Create(c) for c in rev_sde_curves], lag_ratio=0.08),
            run_time=3.2,
        )
        self.wait(0.6)

        caption = self._update_caption(
            caption,
            "Halving the score drift (1/2 g(t)^2) removes Brownian noise: smooth ODE streamlines ride the exact same p_t(x)!",
            accent_color=GOLD_BRIGHT,
        )
        self.play(
            ReplacementTransform(rev_sde_curves, ode_surface_curves),
            FadeIn(ode_floor_curves),
            FadeIn(ode_endpoints),
            slices_group.animate.set_stroke(opacity=0.45),
            score_arrows.animate.set_stroke(opacity=0.30),
            run_time=3.2,
        )
        self.wait(1.0)

        # -------------------------------------------------------------------
        # Act IV: The Big Zoom — OpenAI's Consistency Map f_theta(x_t, t) = x_epsilon
        # -------------------------------------------------------------------
        header, caption = self._swap_hud(
            header,
            caption,
            self._make_hud_header(
                "ACT IV · THE BIG ZOOM: CONSISTENCY MODELS (OPENAI, 2023)",
                "Every Point Along an ODE Trajectory Maps to the Same Clean Endpoint x_epsilon",
                r"f_\theta(x_t, t) = f_\theta(x_{t'}, t') = x_\epsilon,\qquad f_\theta(x, t) = c_{\text{skip}}(t)\,x + c_{\text{out}}(t)\,F_\theta(x, t)",
            ),
            self._make_hud_caption(
                "Zooming into one Probability Flow ODE trajectory starting at x_T = +2.30 and landing at x_epsilon = +2.04.",
                accent_color=GOLD_BRIGHT,
            ),
            run_time=0.9,
        )

        hero_idx = 6
        hero_curve = ode_surface_curves[hero_idx]
        other_curves = VGroup(*[c for idx, c in enumerate(ode_surface_curves) if idx != hero_idx])

        self.play(
            other_curves.animate.set_stroke(opacity=0.16),
            ode_floor_curves.animate.set_stroke(opacity=0.15),
            hero_curve.animate.set_stroke(GOLD_BRIGHT, width=5.2, opacity=1.0),
            run_time=1.4,
        )
        self.move_camera(phi=52 * DEGREES, theta=-76 * DEGREES, run_time=2.5)

        ts_hero, xs_hero = integrate_prob_flow_ode(2.3, T_MAX, EPSILON, steps=240)
        x_eps_val = float(xs_hero[-1])
        p_eps = world_pt(x_eps_val, EPSILON, float(marginal_pdf(x_eps_val, EPSILON)) + 0.025)
        eps_star = marker_3d(p_eps, radius=0.095, color=CORAL)

        sample_times = [2.20, 1.25, 0.50]
        sample_colors = [CORAL, SKY, OLIVE_BRIGHT]
        beads = VGroup()
        consistency_arcs = VGroup()

        for tv, bcol in zip(sample_times, sample_colors):
            idx_t = int(np.argmin(np.abs(ts_hero - tv)))
            xv = float(xs_hero[idx_t])
            zv = float(marginal_pdf(xv, tv)) + 0.025
            pt_start = world_pt(xv, tv, zv)
            bead = marker_3d(pt_start, radius=0.08, color=bcol)
            beads.add(bead)

            ctrl1 = pt_start + np.array([0.15, -0.35 * tv, 0.75 + 0.18 * tv])
            ctrl2 = p_eps + np.array([0.10, 0.30 * tv, 0.65 + 0.15 * tv])
            jump_arc = CubicBezier(
                pt_start,
                ctrl1,
                ctrl2,
                p_eps,
                stroke_color=GOLD_BRIGHT,
                stroke_width=3.8,
                stroke_opacity=0.96,
            )
            consistency_arcs.add(jump_arc)

        caption = self._update_caption(
            caption,
            "Three points at t = 2.20, t' = 1.25, t'' = 0.50 on the same ODE trajectory fire 1-step arcs to the exact same x_epsilon!",
            accent_color=GOLD_BRIGHT,
        )
        self.play(FadeIn(beads), FadeIn(eps_star), run_time=1.2)
        self.play(
            LaggedStart(*[Create(arc) for arc in consistency_arcs], lag_ratio=0.18),
            run_time=3.2,
        )
        self.wait(1.0)

        caption = self._update_caption(
            caption,
            "Skip weights c_skip(t) and c_out(t) enforce c_skip(epsilon) = 1, c_out(epsilon) = 0 so f_theta(x, epsilon) = x holds identically.",
            accent_color=OLIVE_BRIGHT,
        )
        card_bg = RoundedRectangle(
            corner_radius=0.12,
            width=4.6,
            height=2.7,
            fill_color=PANEL_BG,
            fill_opacity=0.92,
            stroke_color=GOLD,
            stroke_width=1.3,
        )
        card_title = Text("Boundary Weights (sigma_data = 0.5)", font="Consolas", font_size=14, color=GOLD_BRIGHT)
        eq_skip = MathTex(
            r"c_{\text{skip}}(\epsilon)=1,\quad c_{\text{out}}(\epsilon)=0",
            font_size=22,
            color=IVORY,
        )
        ax_origin = np.array([-1.7, -0.85, 0.0])
        ax_w, ax_h = 3.4, 1.25
        x_ax_line = Line(ax_origin, ax_origin + np.array([ax_w, 0.0, 0.0]), stroke_color=FOG, stroke_width=1.4)
        y_ax_line = Line(ax_origin, ax_origin + np.array([0.0, ax_h, 0.0]), stroke_color=FOG, stroke_width=1.4)
        ts_plot = np.linspace(EPSILON, T_MAX, 80)
        skip_pts = [
            ax_origin + np.array([(tv / T_MAX) * ax_w, float(c_skip(tv)) * ax_h, 0.0])
            for tv in ts_plot
        ]
        out_pts = [
            ax_origin + np.array([(tv / T_MAX) * ax_w, float(c_out(tv)) * ax_h, 0.0])
            for tv in ts_plot
        ]
        skip_curve = VMobject().set_points_smoothly(skip_pts).set_stroke(OLIVE_BRIGHT, width=2.8)
        out_curve = VMobject().set_points_smoothly(out_pts).set_stroke(GOLD_BRIGHT, width=2.8)
        lbl_skip = Text("c_skip(t)", font="Consolas", font_size=13, color=OLIVE_BRIGHT).next_to(skip_pts[10], RIGHT, buff=0.08)
        lbl_out = Text("c_out(t)", font="Consolas", font_size=13, color=GOLD_BRIGHT).next_to(out_pts[-1], LEFT, buff=0.08)
        plot_grp = VGroup(x_ax_line, y_ax_line, skip_curve, out_curve, lbl_skip, lbl_out)
        card_inner = VGroup(card_title, eq_skip, plot_grp).arrange(DOWN, buff=0.14)
        skip_card = VGroup(card_bg, card_inner)
        card_inner.move_to(card_bg.get_center())
        skip_card.to_edge(RIGHT, buff=0.25).shift(0.2 * DOWN)

        self.add_fixed_in_frame_mobjects(skip_card)
        self.play(FadeIn(skip_card, shift=0.2 * LEFT), run_time=1.8)
        self.wait(1.4)
        self.play(FadeOut(skip_card), run_time=0.8)
        self.remove(skip_card)

        # -------------------------------------------------------------------
        # Act V: Multi-Step ODE (50 NFE) vs. One-Step Consistency Leap (1 NFE)
        # -------------------------------------------------------------------
        header, caption = self._swap_hud(
            header,
            caption,
            self._make_hud_header(
                "ACT V · ONE LEAP TO THE MANIFOLD",
                "Fifty Sequential ODE Steps Collapse into One Consistency Evaluation (NFE = 1)",
                r"x_\epsilon = f_\theta(x_T, T) = c_{\text{skip}}(T)\,x_T + c_{\text{out}}(T)\,F_\theta(x_T, T)",
            ),
            self._make_hud_caption(
                "All eight prior samples at t = T = 2.5 leap in a single golden Consistency evaluation onto the bimodal peaks at t = epsilon.",
                accent_color=GOLD_BRIGHT,
            ),
            run_time=0.9,
        )

        self.move_camera(phi=62 * DEGREES, theta=-46 * DEGREES, run_time=2.2)
        self.play(
            other_curves.animate.set_stroke(opacity=0.65),
            hero_curve.animate.set_stroke(width=3.4, opacity=0.85),
            FadeOut(beads),
            FadeOut(consistency_arcs),
            FadeOut(eps_star),
            run_time=1.2,
        )

        all_jump_arcs = VGroup()
        start_dots = VGroup()
        for xT in xT_samples:
            ts_o, xs_o = integrate_prob_flow_ode(xT, T_MAX, EPSILON, steps=100)
            x_end = float(xs_o[-1])
            p_s = world_pt(xT, T_MAX, float(marginal_pdf(xT, T_MAX)) + 0.02)
            p_e = world_pt(x_end, EPSILON, float(marginal_pdf(x_end, EPSILON)) + 0.02)
            start_dots.add(marker_3d(p_s, radius=0.06, color=CORAL))
            c1 = p_s + np.array([0.0, -1.1, 0.95])
            c2 = p_e + np.array([0.0, 1.1, 0.85])
            arc = CubicBezier(
                p_s,
                c1,
                c2,
                p_e,
                stroke_color=GOLD_BRIGHT,
                stroke_width=3.2,
                stroke_opacity=0.92,
            )
            all_jump_arcs.add(arc)

        self.play(FadeIn(start_dots), run_time=0.7)
        self.play(
            LaggedStart(*[Create(arc) for arc in all_jump_arcs], lag_ratio=0.08),
            p0_curve.animate.set_stroke(CORAL, width=5.0, opacity=1.0),
            run_time=3.2,
        )

        caption = self._update_caption(
            caption,
            "Score SDEs sculpt the density surface; the Probability Flow ODE straightens the path; Consistency crosses it in one step.",
            accent_color=GOLD_BRIGHT,
        )
        self.move_camera(phi=56 * DEGREES, theta=-24 * DEGREES, run_time=3.8)
        self.wait(1.2)
