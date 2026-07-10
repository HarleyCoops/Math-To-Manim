"""THE TRAITOR AXIS — why a spinning T-handle flips itself in zero gravity.

One concrete question, computed live:

    Spin a T-handle about each of its three principal axes.
    Two spins are steady forever. The third somersaults on a clock.
    Why — and can we predict the clock?

Everything in this film is calculated, not keyframed:

- The moments of inertia (I_y < I_x < I_z) come from the cylinder geometry.
- The tumbling is RK4 integration of Euler's rigid-body equations,
  with the orientation matrix advanced by the exponential map.
- The polhode curves on the angular-momentum sphere are integrated
  trajectories; the separatrix is the analytic pair of great circles
  through the intermediate axis.
- The flip countdown ln(2*omega/epsilon)/lambda = 3.4 s is compared
  against the simulation's measured first flip (3.5 s) and cadence (8.2 s).

House style: Mythos Cinematic Charter (headlines before symbols, captions
under every idea, camera as narrator, ink-black palette).

Render:  manim -qm examples/physics/classical_mechanics/dzhanibekov_traitor_axis.py TraitorAxis
"""

from __future__ import annotations

import numpy as np
from manim import *

# ----------------------------------------------------------------------- #
# Palette (Mythos house)                                                   #
# ----------------------------------------------------------------------- #
BG = "#0c0c0b"
CREAM = "#faf9f5"
CORAL = "#d97757"   # the intermediate axis — the traitor
BLUE = "#6a9bcc"    # the smallest axis
GOLD = "#d4a27f"    # the largest axis
OLIVE = "#788c5d"
GRAY = "#b0aea5"
STEEL = "#8f8c82"   # handle metal

# ----------------------------------------------------------------------- #
# Physics: geometry -> inertia tensor -> Euler's equations                 #
# ----------------------------------------------------------------------- #
CROSS_M, CROSS_R, CROSS_L = 1.6, 0.16, 2.6   # crossbar: cylinder along y
STEM_M, STEM_R, STEM_L = 1.0, 0.16, 1.2      # stem: cylinder along +x
SIM_FS = 240                                  # integration steps per second


def principal_moments():
    """Composite-cylinder inertia about the COM. Axes: x=stem, y=crossbar."""
    x_s = CROSS_R + STEM_L / 2
    xbar = STEM_M * x_s / (CROSS_M + STEM_M)
    c_ax = 0.5 * CROSS_M * CROSS_R**2
    c_pp = CROSS_M * (3 * CROSS_R**2 + CROSS_L**2) / 12
    s_ax = 0.5 * STEM_M * STEM_R**2
    s_pp = STEM_M * (3 * STEM_R**2 + STEM_L**2) / 12
    d_c, d_s = xbar, x_s - xbar
    ix = c_pp + s_ax
    iy = c_ax + CROSS_M * d_c**2 + s_pp + STEM_M * d_s**2
    iz = c_pp + CROSS_M * d_c**2 + s_pp + STEM_M * d_s**2
    return np.array([ix, iy, iz]), xbar, x_s


I_VEC, XBAR, X_STEM = principal_moments()          # [0.924, 0.502, 1.393]
I_X, I_Y, I_Z = I_VEC
LAMBDA_PER_W = np.sqrt((I_X - I_Y) * (I_Z - I_X) / (I_Y * I_Z))   # 0.532


def euler_rhs(w):
    return np.array([
        (I_Y - I_Z) / I_X * w[1] * w[2],
        (I_Z - I_X) / I_Y * w[2] * w[0],
        (I_X - I_Y) / I_Z * w[0] * w[1],
    ])


def _skew_exp(w, dt):
    theta = np.linalg.norm(w) * dt
    if theta < 1e-12:
        return np.eye(3)
    ax = w / np.linalg.norm(w)
    k = np.array([[0, -ax[2], ax[1]], [ax[2], 0, -ax[0]], [-ax[1], ax[0], 0]])
    return np.eye(3) + np.sin(theta) * k + (1 - np.cos(theta)) * (k @ k)


def simulate(w0, duration):
    """RK4 for omega(t) in the body frame; exponential map for R(t)."""
    n = int(duration * SIM_FS) + 1
    ws = np.zeros((n, 3))
    rs = np.zeros((n, 3, 3))
    w = np.array(w0, dtype=float)
    r = np.eye(3)
    dt = 1.0 / SIM_FS
    for i in range(n):
        ws[i], rs[i] = w, r
        k1 = euler_rhs(w)
        k2 = euler_rhs(w + dt / 2 * k1)
        k3 = euler_rhs(w + dt / 2 * k2)
        k4 = euler_rhs(w + dt * k3)
        w = w + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        r = r @ _skew_exp(w, dt)
    return ws, rs


def flip_times(ws):
    """Zero crossings of the intermediate-axis spin component."""
    sign = np.sign(ws[:, 0])
    idx = np.where(np.diff(sign) != 0)[0]
    return idx / SIM_FS


def rotation_to_z(axis):
    """Rotation matrix taking `axis` to +z (Rodrigues), safe for parallel vectors."""
    a = axis / np.linalg.norm(axis)
    z = np.array([0.0, 0.0, 1.0])
    if np.allclose(a, z):
        return np.eye(3)
    if np.allclose(a, -z):
        return np.diag([1.0, -1.0, -1.0])
    v = np.cross(a, z)
    s = np.linalg.norm(v)
    c = float(np.dot(a, z))
    k = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    return np.eye(3) + k + k @ k * ((1 - c) / s**2)


# ----------------------------------------------------------------------- #
# The film                                                                 #
# ----------------------------------------------------------------------- #
class TraitorAxis(ThreeDScene):
    S = 1.5  # visual scale of the handle

    def construct(self):
        self.camera.background_color = BG
        self.caption_mob = None

        # ---- precompute every trajectory the film needs ---------------- #
        seed = np.hypot(0.02, 0.015)                       # 0.025 rad/s
        self.sim_mid = simulate((3.0, 0.02, 0.015), 32.0)  # the traitor
        self.sim_min = simulate((0.03, 3.0, 0.02), 14.0)   # crossbar axis
        self.sim_max = simulate((0.03, 0.02, 3.0), 14.0)   # perpendicular
        self.flips = flip_times(self.sim_mid[0])           # 3.47 11.66 19.85 27.9
        lam = 3.0 * LAMBDA_PER_W                           # 1.60 s^-1
        t_pred = np.log(2 * 3.0 / seed) / lam              # 3.43 s

        # ---- 0. the question ------------------------------------------- #
        self.set_camera_orientation(phi=0, theta=-90 * DEGREES, zoom=1.0)
        self.headline("Why does a spinning\nT-handle flip itself?", hold=1.6)

        # ---- 1. the object and its three axes --------------------------- #
        self.set_camera_orientation(phi=62 * DEGREES, theta=-125 * DEGREES, zoom=1.05)
        stars = self.starfield()
        self.add(stars)

        handle = self.build_handle()
        axes3d = self.axis_triad()
        rig = VGroup(handle, axes3d)
        self.play(FadeIn(handle, scale=1.06), run_time=1.2)
        self.play(LaggedStart(*[GrowFromCenter(a) for a in axes3d], lag_ratio=0.2),
                  run_time=1.2)
        self.caption("A crossbar and a stem: two cylinders, three principal axes.",
                     hold=1.2)
        self.caption(
            f"Computed from the geometry:  I_min = {I_Y:.2f}   "
            f"I_mid = {I_X:.2f}   I_max = {I_Z:.2f}",
            hold=1.6)
        self.play(FadeOut(rig), run_time=0.5)

        # ---- 2. two loyal axes ------------------------------------------ #
        self.caption("Spin it about the smallest axis. Steady, forever.", hold=0.4)
        self.spin_segment(self.sim_min, pre_axis=np.array([0.0, 1.0, 0.0]),
                          film_time=6.0, sim_time=6.0, axis_color=BLUE)
        self.caption("The largest axis: just as loyal.", hold=0.4)
        self.spin_segment(self.sim_max, pre_axis=np.array([0.0, 0.0, 1.0]),
                          film_time=5.0, sim_time=5.0, axis_color=GOLD)

        # ---- 3. the traitor --------------------------------------------- #
        self.caption("Now the middle axis. Same handle. Nobody touches it.",
                     hold=0.4)
        warp = self.make_warp(
            film_knots=[0.0, 2.9, 7.1, 14.4],
            sim_knots=[0.0, 2.9, 4.4, 14.0])
        self.spin_segment(self.sim_mid, pre_axis=np.array([1.0, 0.0, 0.0]),
                          film_time=14.4, sim_time=14.0, axis_color=CORAL,
                          rate=warp,
                          mid_caption=(4.5, "It flips. And it will flip again on schedule."))
        self.clear_caption()

        # ---- 4. why: the momentum sphere -------------------------------- #
        self.headline("Two conservation laws\nshare one surface.", hold=1.5)
        self.polhode_segment()

        # ---- 5. the countdown: prediction vs simulation ------------------ #
        self.headline("The flip is not random.\nIt is a countdown.", hold=1.4)
        self.chart_segment(t_pred, lam, seed)

        # ---- 6. finale: triptych ----------------------------------------- #
        self.triptych_segment()

        # ---- 7. end card -------------------------------------------------- #
        self.set_camera_orientation(phi=0, theta=-90 * DEGREES, zoom=1.0)
        title = Text("Stable.  Stable.  Saddle.", font_size=68, color=CREAM,
                     weight=BOLD)
        sub = Text("the intermediate axis theorem — Euler 1765, Dzhanibekov 1985",
                   font_size=26, color=GRAY, slant=ITALIC).next_to(title, DOWN, buff=0.5)
        self.add_fixed_in_frame_mobjects(title, sub)
        self.play(FadeIn(title, shift=0.1 * UP), FadeIn(sub), run_time=1.0)
        self.wait(1.8)
        self.play(FadeOut(title), FadeOut(sub), FadeOut(stars), run_time=1.0)

    # ------------------------------------------------------------------ #
    # Charter helpers                                                     #
    # ------------------------------------------------------------------ #
    def headline(self, text, hold=1.3):
        self.clear_caption()
        h = Text(text, font_size=64, color=CREAM, weight=BOLD,
                 line_spacing=0.9)
        self.add_fixed_in_frame_mobjects(h)
        self.play(FadeIn(h, shift=0.12 * UP), run_time=0.8)
        self.wait(hold)
        self.play(FadeOut(h), run_time=0.5)
        self.remove(h)

    def caption(self, text, hold=0.9):
        c = Text(text, font_size=30, color=CREAM, slant=ITALIC)
        if c.width > config.frame_width - 1.0:
            c.scale((config.frame_width - 1.0) / c.width)
        c.to_edge(DOWN, buff=0.5)
        c.set_stroke(BG, width=5, background=True)
        self.add_fixed_in_frame_mobjects(c)
        if self.caption_mob is None:
            self.play(FadeIn(c, shift=0.08 * UP), run_time=0.35)
        else:
            old = self.caption_mob
            self.play(FadeOut(old), FadeIn(c, shift=0.08 * UP), run_time=0.35)
            self.remove(old)
        self.caption_mob = c
        if hold:
            self.wait(hold)

    def clear_caption(self):
        if self.caption_mob is not None:
            self.play(FadeOut(self.caption_mob), run_time=0.3)
            self.remove(self.caption_mob)
            self.caption_mob = None

    # ------------------------------------------------------------------ #
    # Mobjects                                                            #
    # ------------------------------------------------------------------ #
    def starfield(self):
        rng = np.random.default_rng(7)
        stars = VGroup()
        for _ in range(46):
            v = rng.normal(size=3)
            v = 8.5 * v / np.linalg.norm(v)
            d = Dot3D(point=v, radius=0.014 + 0.012 * rng.random(),
                      color=CREAM, resolution=(4, 2))
            d.set_opacity(0.10 + 0.25 * rng.random())
            stars.add(d)
        return stars

    def build_handle(self, scale=None):
        s = scale or self.S
        cross = Cylinder(radius=CROSS_R * s, height=CROSS_L * s,
                         direction=np.array([0.0, 1.0, 0.0]),
                         fill_opacity=1.0, checkerboard_colors=[STEEL, STEEL],
                         resolution=(18, 24))
        cross.set_stroke(CREAM, width=0.4, opacity=0.25)
        cross.shift(LEFT * XBAR * s)
        stem = Cylinder(radius=STEM_R * s, height=STEM_L * s,
                        direction=np.array([1.0, 0.0, 0.0]),
                        fill_opacity=1.0, checkerboard_colors=[CORAL, CORAL],
                        resolution=(18, 24))
        stem.set_stroke("#e8956f", width=0.4, opacity=0.35)
        stem.shift(RIGHT * (X_STEM - XBAR) * s)
        return VGroup(cross, stem)

    def axis_triad(self):
        s = self.S
        return VGroup(
            Arrow3D(start=ORIGIN, end=np.array([1.5, 0, 0]) * s, color=CORAL,
                    thickness=0.014, base_radius=0.05),
            Arrow3D(start=ORIGIN, end=np.array([0, 1.7, 0]) * s, color=BLUE,
                    thickness=0.014, base_radius=0.05),
            Arrow3D(start=ORIGIN, end=np.array([0, 0, 1.5]) * s, color=GOLD,
                    thickness=0.014, base_radius=0.05),
        )

    # ------------------------------------------------------------------ #
    # Spinning segments                                                   #
    # ------------------------------------------------------------------ #
    @staticmethod
    def make_warp(film_knots, sim_knots):
        film = np.array(film_knots)
        sim = np.array(sim_knots)

        def rate(alpha):
            t_film = alpha * film[-1]
            return float(np.interp(t_film, film, sim) / sim[-1])

        return rate

    def spin_segment(self, sim, pre_axis, film_time, sim_time, axis_color,
                     rate=None, mid_caption=None):
        """One spin test: the handle tumbles under R(t); L stays vertical."""
        ws, rs = sim
        pre = rotation_to_z(pre_axis)

        handle = self.build_handle()
        base = [m.points.copy() for m in handle.family_members_with_points()]
        tracker = ValueTracker(0.0)
        n_max = len(rs) - 1

        def update(group):
            k = min(int(tracker.get_value() * SIM_FS), n_max)
            r = pre @ rs[k]
            for sub, b in zip(group.family_members_with_points(), base):
                sub.points = b @ r.T

        handle.add_updater(update)
        update(handle)

        # the conserved angular momentum, pinned in space
        l_arrow = Arrow3D(start=np.array([0, 0, -2.1]), end=np.array([0, 0, 2.1]),
                          color=axis_color, thickness=0.012, base_radius=0.045)
        l_arrow.set_opacity(0.55)
        self.play(FadeIn(handle), FadeIn(l_arrow), run_time=0.6)

        if mid_caption is None:
            self.begin_ambient_camera_rotation(rate=0.055)
            self.play(tracker.animate.set_value(sim_time),
                      run_time=film_time, rate_func=rate or linear)
            self.stop_ambient_camera_rotation()
        else:
            t_cap, cap_text = mid_caption
            self.begin_ambient_camera_rotation(rate=0.045)
            self.play(tracker.animate.set_value(t_cap),
                      run_time=film_time * t_cap / sim_time,
                      rate_func=rate or linear)
            self.stop_ambient_camera_rotation()
            self.caption(cap_text, hold=0)
            remaining_sim = sim_time - t_cap
            self.begin_ambient_camera_rotation(rate=0.045)
            self.play(tracker.animate.set_value(sim_time),
                      run_time=film_time * remaining_sim / sim_time,
                      rate_func=linear)
            self.stop_ambient_camera_rotation()

        handle.remove_updater(update)
        self.play(FadeOut(handle), FadeOut(l_arrow), run_time=0.5)

    # ------------------------------------------------------------------ #
    # The momentum sphere                                                 #
    # ------------------------------------------------------------------ #
    def polhode_segment(self):
        self.set_camera_orientation(phi=64 * DEGREES, theta=-120 * DEGREES,
                                    zoom=1.1)
        rad = 2.35
        sphere = Sphere(radius=rad, resolution=(30, 15), fill_opacity=0.05,
                        checkerboard_colors=[GRAY, GRAY], stroke_width=0)
        sphere.set_stroke(CREAM, width=0.3, opacity=0.10)

        group = VGroup(sphere)

        # polhode families: integrated trajectories around the two loyal axes
        def polhode(w0, color, opacity, width=1.6, duration=9.0):
            ws, _ = simulate(w0, duration)
            l_hat = ws * I_VEC
            l_hat = l_hat / np.linalg.norm(l_hat, axis=1, keepdims=True)
            curve = VMobject()
            curve.set_points_smoothly([rad * p for p in l_hat[::10]])
            curve.set_stroke(color, width=width, opacity=opacity)
            return curve

        for tilt in (0.25, 0.55, 0.95):
            for sgn in (1, -1):
                group.add(polhode((3 * np.sin(tilt), sgn * 3 * np.cos(tilt), 0.0),
                                  BLUE, 0.45))
                group.add(polhode((3 * np.sin(tilt), 0.0, sgn * 3 * np.cos(tilt)),
                                  GOLD, 0.45))

        # separatrix: the analytic pair of great circles through the mid axis
        a = 1 / I_Y - 1 / I_X
        b = 1 / I_X - 1 / I_Z
        c = np.sqrt(b / a)
        for sgn in (1, -1):
            u2 = np.array([0.0, sgn * c, 1.0])
            u2 = u2 / np.linalg.norm(u2)
            pts = [rad * (np.cos(th) * np.array([1.0, 0, 0]) + np.sin(th) * u2)
                   for th in np.linspace(0, TAU, 120)]
            sep = VMobject()
            sep.set_points_smoothly(pts)
            sep.set_stroke(CORAL, width=2.6, opacity=0.85)
            group.add(sep)

        # the three axes, marked
        marks = VGroup(
            Dot3D(point=np.array([rad, 0, 0]), radius=0.075, color=CORAL),
            Dot3D(point=np.array([-rad, 0, 0]), radius=0.075, color=CORAL),
            Dot3D(point=np.array([0, rad, 0]), radius=0.06, color=BLUE),
            Dot3D(point=np.array([0, 0, rad]), radius=0.06, color=GOLD),
        )
        group.add(marks)

        self.play(FadeIn(sphere), run_time=0.9)
        self.caption("Energy pins the spin to an ellipsoid; momentum pins it to this sphere.",
                     hold=0.6)
        self.play(LaggedStart(*[Create(m) for m in group[1:-1]], lag_ratio=0.06),
                  FadeIn(marks), run_time=2.6)
        self.caption("The spin must ride an intersection curve. Blue and gold: closed loops.",
                     hold=1.2)

        # the actual simulated trajectory, traced live
        ws, _ = self.sim_mid
        l_hat = ws * I_VEC
        l_hat = l_hat / np.linalg.norm(l_hat, axis=1, keepdims=True)
        n_max = len(l_hat) - 1
        tracker = ValueTracker(0.0)
        dot = Dot3D(point=rad * l_hat[0], radius=0.085, color=CORAL)
        glow = Dot3D(point=rad * l_hat[0], radius=0.16, color=CORAL)
        glow.set_opacity(0.25)

        def move(m):
            k = min(int(tracker.get_value() * SIM_FS), n_max)
            m.move_to(rad * l_hat[k])

        dot.add_updater(move)
        glow.add_updater(move)
        trail = TracedPath(dot.get_center, stroke_color=CORAL, stroke_width=3.4)
        self.add(trail, glow, dot)

        self.caption("Coral is a saddle: the simulated spin creeps, then sprints.",
                     hold=0)
        self.begin_ambient_camera_rotation(rate=0.06)
        self.play(tracker.animate.set_value(19.0), run_time=13.0,
                  rate_func=linear)
        self.stop_ambient_camera_rotation()
        self.caption("Every sprint around the sphere is one somersault of the handle.",
                     hold=1.4)

        dot.remove_updater(move)
        glow.remove_updater(move)
        self.clear_caption()
        self.play(FadeOut(group), FadeOut(dot), FadeOut(glow), FadeOut(trail),
                  run_time=0.8)

    # ------------------------------------------------------------------ #
    # The countdown chart                                                 #
    # ------------------------------------------------------------------ #
    def chart_segment(self, t_pred, lam, seed):
        self.set_camera_orientation(phi=0, theta=-90 * DEGREES, zoom=1.0)

        axes = Axes(x_range=[0, 30, 5], y_range=[-3.6, 3.6, 3],
                    x_length=10.6, y_length=4.4, tips=False,
                    axis_config={"color": GRAY, "stroke_width": 2,
                                 "include_ticks": True})
        axes.shift(0.4 * UP)
        x_label = Text("time  (s)", font_size=24, color=GRAY)
        x_label.next_to(axes.x_axis, DOWN, buff=0.25).align_to(axes, RIGHT)
        y_label = Text("spin about the middle axis", font_size=24, color=CORAL)
        y_label.next_to(axes.y_axis, UP, buff=0.2).align_to(axes, LEFT)

        ws, _ = self.sim_mid
        t = np.arange(len(ws)) / SIM_FS
        keep = t <= 30.0
        pts = [axes.c2p(tt, ww) for tt, ww in
               zip(t[keep][::14], ws[keep, 0][::14])]
        curve = VMobject().set_points_smoothly(pts)
        curve.set_stroke(CORAL, width=3.6)

        self.play(Create(axes), FadeIn(x_label), FadeIn(y_label), run_time=1.0)
        self.caption("The middle-axis spin, straight from the integrator.", hold=0)
        self.play(Create(curve), run_time=4.0, rate_func=linear)

        # measured flips
        marks = VGroup()
        for ft in self.flips[self.flips <= 29.5]:
            marks.add(DashedLine(axes.c2p(ft, -3.4), axes.c2p(ft, 3.4),
                                 color=GRAY, stroke_width=1.6,
                                 dash_length=0.08).set_opacity(0.7))
        gap = VGroup()
        f0, f1 = self.flips[0], self.flips[1]
        arrow = DoubleArrow(axes.c2p(f0, 2.9), axes.c2p(f1, 2.9),
                            color=CREAM, stroke_width=2.5, tip_length=0.14,
                            buff=0.02)
        gap_label = Text(f"{f1 - f0:.1f} s, like clockwork", font_size=26,
                         color=CREAM).next_to(arrow, UP, buff=0.12)
        gap.add(arrow, gap_label)
        self.play(LaggedStart(*[Create(m) for m in marks], lag_ratio=0.15),
                  run_time=1.2)
        self.caption(f"Measured flips at t = "
                     f"{', '.join(f'{ft:.1f}' for ft in self.flips[:3])} s.",
                     hold=0.4)
        self.play(FadeIn(gap), run_time=0.8)
        self.wait(0.8)

        # the prediction
        pred = DashedLine(axes.c2p(t_pred, -3.4), axes.c2p(t_pred, 3.4),
                          color=BLUE, stroke_width=3, dash_length=0.1)
        pred_tag = Text(f"predicted: {t_pred:.1f} s", font_size=26, color=BLUE)
        pred_tag.next_to(axes.c2p(t_pred, -3.4), DOWN, buff=0.18)
        formula = MathTex(
            r"\lambda", "=", r"\omega\sqrt{\tfrac{(I_x-I_y)(I_z-I_x)}{I_y I_z}}",
            "=", f"{lam:.2f}", r"\ \mathrm{s}^{-1}",
            color=CREAM, font_size=40)
        formula[0].set_color(CORAL)
        formula[4].set_color(CORAL)
        formula.to_edge(UP, buff=0.45)
        self.add_fixed_in_frame_mobjects(formula)
        self.play(FadeIn(formula, shift=0.1 * DOWN), Create(pred),
                  FadeIn(pred_tag), run_time=1.2)
        self.caption(
            f"A wobble seed of {seed:.3f} rad/s doubles every "
            f"{np.log(2)/lam:.2f} s — the countdown hits at {t_pred:.1f} s. "
            f"The simulation says {self.flips[0]:.1f} s.",
            hold=2.4)

        self.clear_caption()
        self.play(FadeOut(axes), FadeOut(curve), FadeOut(marks), FadeOut(gap),
                  FadeOut(pred), FadeOut(pred_tag), FadeOut(formula),
                  FadeOut(x_label), FadeOut(y_label), run_time=0.7)
        self.remove(formula)

    # ------------------------------------------------------------------ #
    # Finale                                                              #
    # ------------------------------------------------------------------ #
    def triptych_segment(self):
        self.set_camera_orientation(phi=64 * DEGREES, theta=-115 * DEGREES,
                                    zoom=0.82)
        specs = [
            (self.sim_min, np.array([0.0, 1.0, 0.0]), np.array([-4.4, 0, 0])),
            (self.sim_max, np.array([0.0, 0.0, 1.0]), np.array([0.0, 0, 0])),
            (self.sim_mid, np.array([1.0, 0.0, 0.0]), np.array([4.4, 0, 0])),
        ]
        tracker = ValueTracker(0.0)
        handles, updaters = [], []
        for sim, axis, offset in specs:
            ws, rs = sim
            pre = rotation_to_z(axis)
            h = self.build_handle(scale=1.05)
            base = [m.points.copy() for m in h.family_members_with_points()]
            n_max = len(rs) - 1

            def make(bb, rr, pp, nn, off):
                def upd(group):
                    k = min(int(tracker.get_value() * SIM_FS), nn)
                    r = pp @ rr[k]
                    for sub, b in zip(group.family_members_with_points(), bb):
                        sub.points = (b @ r.T) + off
                return upd

            upd = make(base, rs, pre, n_max, offset.copy())
            h.add_updater(upd)
            upd(h)
            handles.append(h)
            updaters.append(upd)

        self.play(*[FadeIn(h) for h in handles], run_time=0.8)
        self.caption("Smallest: steady.   Largest: steady.   Middle: the traitor.",
                     hold=0)
        self.play(tracker.animate.set_value(12.5), run_time=11.0,
                  rate_func=linear)
        for h, u in zip(handles, updaters):
            h.remove_updater(u)
        self.clear_caption()
        self.play(*[FadeOut(h) for h in handles], run_time=0.7)
