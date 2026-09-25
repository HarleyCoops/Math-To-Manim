"""Every Orbit Is a Great Circle -- a Mythos film.

Hamilton's hodograph, the two hinge points shared by every orbit of one
energy, and the stereographic lift that turns each velocity circle into a
great circle on a glass sphere (Moser 1970; Fock 1935 for hydrogen).

Rendering notes
---------------
* Cairo ThreeDScene with ``camera.should_apply_shading = False``: every
  light in the film is computed here, per frame, from the true camera eye
  position (rebuilt from phi/theta so it is never stale).
* Sphere faces and ring segments set ``shade_in_3d = True`` only so the
  ThreeDCamera depth-sorts them; rings dim when they pass behind the glass.
* Planets move by Kepler's equation; GM = 1 and a = 1 for every orbit shown
  in the family, so all periods are exactly 2*pi of simulation time.
* The starfield is a procedural background pixel array (no files).
"""

from manim import *
import numpy as np

# --------------------------------------------------------------------------
# Palette: the Mythos cast list
# --------------------------------------------------------------------------
INK = "#0c0c0b"
IVORY = "#faf9f5"
FOG = "#b0aea5"
CORAL = "#d97757"   # matter: orbits, planets, e, d
SKY = "#6a9bcc"     # light: velocity, hodograph, R
OLIVE = "#788c5d"   # structure: E, a, p0, equator
GOLD = "#d4a27f"    # interaction: hinge points, alpha, great circles
GLASS = "#1a2a39"
OLIVE_TXT = "#a3b58a"  # olive, lifted for legibility as text

ECCS = [0.0, 0.3, 0.55, 0.75, 0.9]
TINTS = [SKY, "#8fb0c4", GOLD, "#dc8d6b", CORAL]

HEAD_FONT = "Poppins"
CAP_FONT = "Lora"

# Layout (world units)
LEFT_FOCUS = np.array([-2.5, -0.3, 0.0])
PS = 1.7                                   # position scale
VEL_O = np.array([3.5, -1.5, 0.0])          # velocity-plane origin
VS = 1.15                                   # world units per unit speed
OPEN_FOCUS = np.array([0.9, 0.0, 0.0])
OPEN_PS = 1.55
K_LIFT = 1.52
SPH = VS * K_LIFT                           # sphere radius = p0 in world units
LIGHT = np.array([-0.45, -0.55, 0.72])
LIGHT = LIGHT / np.linalg.norm(LIGHT)


# --------------------------------------------------------------------------
# Kepler mechanics (GM = 1, a = 1, mean motion 1, perihelion on +x)
# --------------------------------------------------------------------------
def ecc_anomaly(M, e):
    M = np.mod(np.asarray(M, dtype=float), TAU)
    E = np.full_like(M, np.pi)
    for _ in range(30):
        E = E - (E - e * np.sin(E) - M) / (1.0 - e * np.cos(E))
    return E


def kepler_pos(t, e):
    E = ecc_anomaly(t, e)
    c = np.sqrt(1 - e * e)
    return np.stack([np.cos(E) - e, c * np.sin(E)], axis=-1)


def kepler_vel(t, e):
    E = ecc_anomaly(t, e)
    c = np.sqrt(1 - e * e)
    k = 1.0 / (1.0 - e * np.cos(E))
    return np.stack([-np.sin(E) * k, c * np.cos(E) * k], axis=-1)


def to3(xy):
    xy = np.asarray(xy, dtype=float)
    return np.concatenate([xy, np.zeros(xy.shape[:-1] + (1,))], axis=-1)


def rgb(h):
    return np.array(color_to_rgb(h))


def eye_of(cam):
    R = cam.generate_rotation_matrix()
    return np.array(cam.frame_center) + cam.get_focal_distance() * (R.T @ np.array([0.0, 0.0, 1.0]))


def glow(m, color, width=2.4, halo=9.0, halo_op=0.14, opacity=1.0):
    m.set_stroke(color, width=width, opacity=opacity)
    m.set_stroke(color, width=halo, opacity=halo_op * opacity, background=True)
    return m


def make_sky(w, h, seed=7):
    """Procedural night sky: ink base, faint central lift, vignette, stars."""
    rng = np.random.default_rng(seed)
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    nx = (x - w / 2) / (w / 2)
    ny = (y - h / 2) / (h / 2)
    r2 = nx * nx * 0.75 + ny * ny
    base = np.array([12, 12, 11], np.float32)
    lift = np.array([19, 22, 27], np.float32)
    mix = np.clip(1 - r2 * 0.8, 0, 1)[..., None]
    img = base * (1 - mix) + lift * mix
    band = np.exp(-((ny * 0.9 + nx * 0.45 - 0.1) ** 2) / 0.08)
    ripple = 0.5 + 0.5 * np.sin(nx * 7.1 + 1.3) * np.sin(ny * 5.3 - 0.7) * np.sin((nx + ny) * 3.1)
    img += (band * ripple * 5.0)[..., None] * np.array([0.8, 0.9, 1.0], np.float32)
    img *= (1 - 0.42 * np.clip(r2, 0, 1.6) ** 1.4)[..., None]
    n = int(w * h / 2600)
    xs = rng.integers(2, w - 2, n)
    ys = rng.integers(2, h - 2, n)
    mag = rng.random(n) ** 3.2
    tint = rng.random(n)
    scale = max(w / 1920.0, 0.45)
    for sx, sy, m, tt in zip(xs, ys, mag, tint):
        col = np.array([255, 244, 228], np.float32) if tt < 0.55 else np.array([214, 228, 255], np.float32)
        peak = 40 + 200 * m
        img[sy, sx] += col / 255 * peak
        if m > 0.35:
            rad = int(1 + 2 * m * scale)
            for dy in range(-rad, rad + 1):
                for dx in range(-rad, rad + 1):
                    if dx == 0 and dy == 0:
                        continue
                    d2 = dx * dx + dy * dy
                    img[sy + dy, sx + dx] += col / 255 * peak * 0.28 * np.exp(-d2 / (0.8 + m * scale))
    img = np.clip(img, 0, 255).astype(np.uint8)
    alpha = np.full((h, w, 1), 255, np.uint8)
    return np.concatenate([img, alpha], axis=-1)


# --------------------------------------------------------------------------
# Camera-facing billboards (glows, planets, highlights)
# --------------------------------------------------------------------------
class Billboard(VGroup):
    """Concentric disks rebuilt every frame in the camera plane."""

    def __init__(self, scene, anchor, layers, light_from=None, facing=False, **kw):
        super().__init__(**kw)
        self.cam_fn = (lambda s=scene: s.camera)  # functions deep-copy by reference
        self.anchor = anchor
        self.layers = layers
        self.light_from = light_from
        self.facing = facing
        self.vis = ValueTracker(1.0)
        self.templates = []
        for L in layers:
            disk = Circle(radius=L["r"], num_components=24)
            disk.set_stroke(width=0).set_fill(L["color"], opacity=L["op"])
            self.templates.append(disk.points.copy())
            self.add(disk)
        self.add_updater(lambda m: m.orient())
        self.orient()

    def orient(self):
        cam = self.cam_fn()
        R = cam.generate_rotation_matrix()
        p = self.anchor.get_center()
        vis = self.vis.get_value()
        if self.facing:
            eye = eye_of(self.cam_fn())
            n = p / (np.linalg.norm(p) + 1e-9)
            if np.dot(n, eye - p) < 0:
                vis *= 0.35
        lit = np.zeros(3)
        if self.light_from is not None:
            d = R @ (self.light_from.get_center() - p)
            d[2] = 0
            nd = np.linalg.norm(d)
            if nd > 1e-6:
                lit = d / nd
        for disk, tpl, L in zip(self.submobjects, self.templates, self.layers):
            off = lit * L.get("lit", 0.0)
            disk.points = p + (tpl + off) @ R
            disk.set_fill(opacity=L["op"] * vis)


def soft_glow(color, r_in, r_out, peak, n=12, power=2.0):
    """Nested translucent disks whose combined opacity follows
    peak * (1 - (r - r_in) / (r_out - r_in)) ** power: a smooth falloff with no
    visible steps."""
    radii = np.linspace(r_out, r_in, n)
    target = peak * np.clip((r_out - radii) / (r_out - r_in), 0, 1) ** power
    layers, prev = [], 0.0
    for r, T in zip(radii, target):
        op = 1 - (1 - T) / (1 - prev) if prev < 1 else 0.0
        if op > 1e-4:
            layers.append({"r": float(r), "color": color, "op": float(op)})
        prev = T
    return layers


def star_layers(core=0.15):
    return (soft_glow(GOLD, core * 1.2, core * 9.0, 0.30, n=14, power=2.4)
            + soft_glow("#fbe6c8", core, core * 2.4, 0.55, n=6, power=1.6)
            + [{"r": core, "color": "#fff6e6", "op": 1.0}])


def planet_layers(tint, r=0.075):
    return (soft_glow(tint, r * 1.05, r * 3.6, 0.42, n=9, power=2.0)
            + [{"r": r, "color": interpolate_color(ManimColor(tint), ManimColor(INK), 0.25), "op": 1.0},
               {"r": r * 0.55, "color": tint, "op": 1.0, "lit": r * 0.28},
               {"r": r * 0.24, "color": IVORY, "op": 0.85, "lit": r * 0.5}])


def point_glow_layers(color, r=0.06):
    return (soft_glow(color, r * 1.05, r * 5.0, 0.62, n=10, power=2.2)
            + [{"r": r, "color": color, "op": 1.0},
               {"r": r * 0.45, "color": IVORY, "op": 0.9}])


class Trail(VMobject):
    """Comet trail: the planet's last stretch of orbit, fading into the ink."""

    def __init__(self, tracker, e, focus, scale, tint, span=0.9, n=36, **kw):
        super().__init__(**kw)
        self.tracker, self.e, self.focus, self.scale = tracker, e, focus, scale
        self.span, self.n, self.tint = span, n, tint
        self.vis = ValueTracker(1.0)
        self.add_updater(lambda m: m.refresh())
        self.refresh()

    def refresh(self):
        t = self.tracker.get_value()
        ts = t - np.linspace(self.span, 0, self.n)
        pts = self.focus.get_center() + self.scale * to3(kepler_pos(ts, self.e))
        self.set_points_smoothly(pts)
        chord = pts[-1] - pts[0]
        if np.linalg.norm(chord) > 1e-6:
            self.set_sheen_direction(chord / np.linalg.norm(chord))
        v = self.vis.get_value()
        self.set_stroke([INK, self.tint], width=3.2, opacity=0.9 * v)
        self.set_stroke([INK, self.tint], width=9, opacity=0.10 * v, background=True)


# --------------------------------------------------------------------------
# The glass sphere and its great circles
# --------------------------------------------------------------------------
class GlassSphere(VGroup):
    def __init__(self, scene, radius, res=(36, 72), **kw):
        super().__init__(**kw)
        self.cam_fn = (lambda s=scene: s.camera)  # functions deep-copy by reference
        self.radius = radius
        self.vis = ValueTracker(0.0)
        nu, nv = res
        us = np.linspace(0, TAU, nv + 1)
        vs = np.linspace(0, PI, nu + 1)
        normals = []
        for i in range(nu):
            for j in range(nv):
                corners = [self._p(us[j], vs[i]), self._p(us[j + 1], vs[i]),
                           self._p(us[j + 1], vs[i + 1]), self._p(us[j], vs[i + 1])]
                face = Polygon(*corners, stroke_width=0)
                face.set_fill(GLASS, opacity=0)
                face.shade_in_3d = True
                c = self._p((us[j] + us[j + 1]) / 2, (vs[i] + vs[i + 1]) / 2)
                normals.append(c / np.linalg.norm(c))
                self.add(face)
        self.normals = np.array(normals)
        self.glass = rgb(GLASS)
        self.rim = rgb(GOLD)
        self.skyc = rgb(SKY)
        self.add_updater(lambda m: m.shade())
        self.shade()

    def _p(self, u, v):
        r = self.radius
        return np.array([r * np.cos(u) * np.sin(v), r * np.sin(u) * np.sin(v), -r * np.cos(v)])

    def shade(self):
        vis = self.vis.get_value()
        if vis <= 1e-3:
            for f in self.submobjects:
                f.set_fill(opacity=0)
            return
        eye = eye_of(self.cam_fn())
        N = self.normals
        P = N * self.radius
        V = eye - P
        V /= np.linalg.norm(V, axis=1)[:, None]
        ndv = np.einsum("ij,ij->i", N, V)
        ndl = np.clip(N @ LIGHT, 0, 1)
        H = V + LIGHT
        H /= np.linalg.norm(H, axis=1)[:, None]
        spec = np.clip(np.einsum("ij,ij->i", N, H), 0, 1) ** 10
        rim = (1 - np.clip(np.abs(ndv), 0, 1)) ** 3.2
        up = np.clip(N[:, 2], 0, 1)
        front = ndv > 0
        col_f = (self.glass[None, :] * (0.45 + 0.55 * ndl[:, None])
                 + self.rim[None, :] * (0.40 * rim)[:, None]
                 + self.skyc[None, :] * (0.10 * up)[:, None]
                 + (0.10 * spec)[:, None])
        col_b = self.glass[None, :] * 0.55 + self.skyc[None, :] * (0.18 * rim)[:, None]
        op_f = 0.10 + 0.22 * rim + 0.08 * spec
        op_b = 0.05 + 0.10 * rim
        cols = np.where(front[:, None], col_f, col_b)
        ops = np.where(front, op_f, op_b) * vis
        cols = np.clip(cols, 0, 1)
        for f, c, o in zip(self.submobjects, cols, ops):
            f.set_fill(rgb_to_color(c), opacity=float(min(o, 0.92)))


class Silhouette(VGroup):
    """Fresnel rim drawn at the sphere's exact perspective silhouette.

    A sharp edge plus two wide, faint inner strokes give a smooth rim glow
    that per-face shading cannot (flat faces step visibly at grazing angles).
    """

    LAYERS = ((1.0, 1.8, 0.60), (0.985, 14, 0.10), (0.955, 36, 0.045))

    def __init__(self, scene, radius, **kw):
        super().__init__(**kw)
        self.cam_fn = (lambda s=scene: s.camera)  # functions deep-copy by reference
        self.radius = radius
        self.vis = ValueTracker(0.0)
        self.tpl = Circle(radius=1.0, num_components=64).points.copy()
        for _ in self.LAYERS:
            self.add(VMobject())
        self.add_updater(lambda m: m.refresh())
        self.refresh()

    def refresh(self):
        eye = eye_of(self.cam_fn())
        d = np.linalg.norm(eye)
        R = self.cam_fn().generate_rotation_matrix()
        r = self.radius
        rp = r * np.sqrt(max(1 - (r / d) ** 2, 0.0))
        ctr = eye / d * (r * r / d)
        v = self.vis.get_value()
        for ring, (k, width, op) in zip(self.submobjects, self.LAYERS):
            ring.points = ctr + (self.tpl * rp * k) @ R
            ring.set_fill(opacity=0)
            ring.set_stroke(GOLD, width=width, opacity=op * v)


class Ring(VGroup):
    """A velocity circle that can be lifted onto the sphere and tilted.

    tilt = arcsin(e). mode 'theta' samples by true anomaly (needed while the
    plane circle is being lifted); mode 'E' samples by eccentric anomaly,
    which stays regular all the way to the collision orbit at tilt = 90 deg.
    """

    def __init__(self, scene, e, color, nseg=150, width=3.0, **kw):
        super().__init__(**kw)
        self.cam_fn = (lambda s=scene: s.camera)  # functions deep-copy by reference
        self.color = color
        self.width = width
        self.nseg = nseg
        self.tilt = ValueTracker(float(np.arcsin(e)))
        self.lam = ValueTracker(0.0)
        self.vis = ValueTracker(1.0)
        self.mode = "theta"
        # Continuous paths, split into runs facing toward / away from the camera.
        # Front runs sit on the near side of the glass and draw on top. Back
        # runs are depth-sorted at the sphere's centre, so the near half of the
        # glass veils them. (Per-segment strokes left antialiasing seams.)
        self.centre_ref = VectorizedPoint(ORIGIN)
        self.front = VMobject()
        self.back = VMobject()
        self.halo_front = VMobject()
        self.halo_back = VMobject()
        for m in (self.back, self.halo_back):
            m.shade_in_3d = True
            m.z_index_group = self.centre_ref
        self.add(self.halo_back, self.back, self.halo_front, self.front)
        self.add_updater(lambda m: m.refresh())
        self.refresh()

    def samples(self):
        a = self.tilt.get_value()
        e, c = np.sin(a), np.cos(a)
        s = np.linspace(0, TAU, 3 * self.nseg + 1)
        if self.mode == "theta":
            v = np.stack([-np.sin(s), e + np.cos(s)], axis=-1) / max(c, 1e-6)
            u2 = (v ** 2).sum(-1)
            lifted = np.column_stack([2 * v / (u2 + 1)[:, None], (u2 - 1) / (u2 + 1)]) * SPH
            planar = to3(v) * SPH
            lam = self.lam.get_value()
            return (1 - lam) * planar + lam * lifted * 1.004, lam
        pts = np.column_stack([-np.sin(s), c * np.cos(s), e * np.cos(s)]) * SPH * 1.004
        return pts, 1.0

    def refresh(self):
        pts, lam = self.samples()
        eye = eye_of(self.cam_fn())
        vis = self.vis.get_value()
        mids = pts[1::3][: self.nseg]
        nrm = mids / (np.linalg.norm(mids, axis=1)[:, None] + 1e-9)
        backs = np.einsum("ij,ij->i", nrm, eye - mids) < 0
        if lam < 0.5:
            backs[:] = False  # still in the plane: no glass to hide behind
        back_op = vis * (1 - 0.76 * lam)
        plan = ((self.front, False, self.width, vis), (self.back, True, self.width, back_op),
                (self.halo_front, False, 11, 0.13 * vis), (self.halo_back, True, 11, 0.035 * vis))
        for path, want, width, op in plan:
            path.clear_points()
            k = 0
            while k < self.nseg:
                if backs[k] == want:
                    j = k
                    while j < self.nseg and backs[j] == want:
                        j += 1
                    run = pts[3 * k: 3 * j + 1]
                    path.start_new_path(run[0])
                    path.add_points_as_corners(run[1:])
                    k = j
                else:
                    k += 1
            path.set_fill(opacity=0)
            path.set_stroke(self.color, width=width, opacity=op)


class Plate(VGroup):
    """Astrolabe plate in the velocity plane, outside the sphere.

    Built from short depth-sorted segments so the glass occludes it correctly.
    """

    def __init__(self, radii=(1.22, 1.55, 2.0, 2.6), **kw):
        super().__init__(**kw)
        self.vis = ValueTracker(0.0)
        self.last = None
        self.base = []
        for i, rr in enumerate(radii):
            n = 96
            ang = np.linspace(0, TAU, n + 1)
            for k in range(n):
                a0, a1 = ang[k], ang[k + 1]
                seg = Line(SPH * rr * np.array([np.cos(a0), np.sin(a0), 0]),
                           SPH * rr * np.array([np.cos(a1), np.sin(a1), 0]))
                seg.shade_in_3d = True
                self.add(seg)
                self.base.append(0.20 - 0.035 * i)
        for k in range(36):
            a = k * TAU / 36
            d = np.array([np.cos(a), np.sin(a), 0])
            r0, r1 = (1.08, 1.22) if k % 3 else (1.08, 2.6)
            steps = np.linspace(r0, r1, 5 if k % 3 == 0 else 2)
            for q in range(len(steps) - 1):
                seg = Line(SPH * steps[q] * d, SPH * steps[q + 1] * d)
                seg.shade_in_3d = True
                self.add(seg)
                self.base.append(0.16 if k % 3 == 0 else 0.22)
        self.add_updater(lambda m: m.refresh())
        self.refresh()

    def refresh(self):
        v = round(self.vis.get_value(), 4)
        if v == self.last:
            return
        self.last = v
        for seg, b in zip(self.submobjects, self.base):
            seg.set_stroke(GOLD if b > 0.21 else FOG, width=1.1, opacity=b * v)


class HiddenSphereJourney(ThreeDScene):
    # ------------------------------------------------------------------ #
    # Narration layer                                                     #
    # ------------------------------------------------------------------ #
    def setup_layers(self):
        self.cap_mob = None
        self.dead_caps = []

    def cap(self, text):
        """Swap the lower-third caption. Fades run on their own clock, so a
        caption never stretches across a long shot's run_time."""
        for m in self.dead_caps:
            m.clear_updaters()
            self.remove(m)
        self.dead_caps = []
        if self.cap_mob is not None:
            self.cap_mob.fading = True
            self.dead_caps.append(self.cap_mob)
        if text is None:
            self.cap_mob = None
            return []
        new = Text(text, font=CAP_FONT, slant=ITALIC, font_size=30, color=IVORY)
        if new.width > 12.4:
            new.scale_to_fit_width(12.4)
        new.to_edge(DOWN, buff=0.42)
        new.base = new.get_center().copy()
        new.clock = -0.35 if self.dead_caps else 0.0
        new.fclock, new.fading = 0.0, False

        def tick(m, dt):
            if m.fading:
                m.fclock += dt
                op = max(0.0, 1.0 - m.fclock / 0.35) * min(1.0, max(m.clock, 0.0) / 0.5)
            else:
                m.clock += dt
                op = min(1.0, max(m.clock, 0.0) / 0.5)
            m.set_opacity(op)
            m.move_to(m.base + DOWN * 0.08 * (1 - min(1.0, max(m.clock, 0.0) / 0.5)))

        new.add_updater(tick)
        new.set_opacity(0)
        self.add_fixed_in_frame_mobjects(new)
        self.cap_mob = new
        return []

    def headline(self, text, font_size=72, hold=1.3, dim_op=0.8):
        title = Text(text, font=HEAD_FONT, weight=BOLD, font_size=font_size, color=IVORY,
                     line_spacing=0.85)
        if title.width > 11.6:
            title.scale_to_fit_width(11.6)
        rule = Line(LEFT * 0.45, RIGHT * 0.45).set_stroke(GOLD, width=3)
        rule.next_to(title, UP, buff=0.5)
        group = VGroup(rule, title).move_to(ORIGIN)
        dim = Rectangle(width=16.5, height=9.6).set_stroke(width=0).set_fill(INK, opacity=dim_op)
        self.add_fixed_in_frame_mobjects(dim, group)
        self.play(FadeIn(dim), FadeIn(group, shift=UP * 0.15), *self.cap(None), run_time=0.9)
        self.wait(hold)
        self.play(FadeOut(group, shift=UP * 0.3), FadeOut(dim), run_time=0.75)
        self.remove_fixed_in_frame_mobjects(dim, group)
        self.remove(dim, group)

    def formula(self, parts, colors, pos, font_size=48):
        f = MathTex(*parts, font_size=font_size, color=IVORY)
        for i, col in colors.items():
            f[i].set_color(col)
        f.move_to(pos)
        return f

    def zoom_to(self, formula, idx, zoom, caption, run_time=1.2):
        dims = [m.animate.set_opacity(0.28) for i, m in enumerate(formula) if i != idx and len(m) > 0]
        self.move_camera(frame_center=formula[idx].get_center(), zoom=zoom, run_time=run_time,
                         added_anims=[formula[idx].animate.set_opacity(1), *dims, *self.cap(caption)])

    # ------------------------------------------------------------------ #
    # Film                                                                #
    # ------------------------------------------------------------------ #
    def construct(self):
        self.setup_layers()
        cam = self.camera
        cam.should_apply_shading = False
        cam.set_background(make_sky(cam.pixel_width, cam.pixel_height))
        self.t = ValueTracker(0.0)

        self.act_orrery()
        self.act_hodograph()
        self.act_energy()
        self.act_hinges()
        self.act_lift()
        self.act_angle()
        self.act_rotation()

    # ACT 1a: cold open ------------------------------------------------- #
    def act_orrery(self):
        self.set_camera_orientation(phi=58 * DEGREES, theta=-72 * DEGREES, zoom=1.45)
        self.star_anchor = VectorizedPoint(OPEN_FOCUS)
        self.add(self.star_anchor)
        focus = self.star_anchor
        orbits = VGroup()
        for e, tint in zip(ECCS, TINTS):
            orb = ParametricFunction(
                lambda E, e=e: OPEN_FOCUS + OPEN_PS * np.array([np.cos(E) - e, np.sqrt(1 - e * e) * np.sin(E), 0]),
                t_range=[0, TAU, TAU / 160])
            glow(orb, tint, width=1.6, halo=7, halo_op=0.10, opacity=0.55)
            orbits.add(orb)
        trails, planets = [], []
        for e, tint in zip(ECCS, TINTS):
            tr = Trail(self.t, e, focus, OPEN_PS, tint)
            trails.append(tr)
        for e, tint in zip(ECCS, TINTS):
            anchor = VectorizedPoint()
            anchor.add_updater(lambda m, e=e: m.move_to(focus.get_center() + OPEN_PS * to3(kepler_pos(self.t.get_value(), e))))
            anchor.update()
            pl = Billboard(self, anchor, planet_layers(tint), light_from=focus)
            planets.append((anchor, pl))
        self.star = Billboard(self, self.star_anchor, star_layers(0.17))
        self.add(orbits, *trails)
        for anchor, pl in planets:
            self.add(anchor, pl)
        self.add(self.star)
        for tr in trails:
            tr.vis.set_value(0)
        for _, pl in planets:
            pl.vis.set_value(0)
        self.star.vis.set_value(0)
        orbits.set_opacity(0)

        self.begin_ambient_camera_rotation(rate=0.05)
        self.play(self.star.vis.animate.set_value(1),
                  orbits.animate.set_stroke(opacity=0.55).set_stroke(opacity=0.055, background=True),
                  *[pl.vis.animate.set_value(1) for _, pl in planets],
                  *[tr.vis.animate.set_value(1) for tr in trails],
                  run_time=1.2)
        self.play(self.t.animate.set_value(TAU), *self.cap("Five orbits around one star. Watch them come home together."),
                  run_time=8.6, rate_func=linear)
        self.wait(0.4)
        self.stop_ambient_camera_rotation()
        self.headline("Where it is draws an ellipse.\nHow fast it goes draws a circle.", font_size=66, hold=1.6)

        # RETURN_2D: flatten onto the drafting table
        self.velocity_grid = self.make_velocity_grid()
        self.move_camera(phi=0, theta=-90 * DEGREES, zoom=1.0, run_time=2.0,
                         added_anims=[orbits.animate.set_stroke(opacity=0).set_stroke(opacity=0, background=True),
                                      *[pl.vis.animate.set_value(0) for _, pl in planets],
                                      *[tr.vis.animate.set_value(0) for tr in trails],
                                      self.star_anchor.animate.move_to(LEFT_FOCUS),
                                      FadeIn(self.velocity_grid)])
        for anchor, pl in planets:
            pl.clear_updaters()
            anchor.clear_updaters()
            self.remove(anchor, pl)
        for tr in trails:
            tr.clear_updaters()
            self.remove(tr)
        self.remove(orbits)
        self.t.set_value(0)

    def make_velocity_grid(self):
        g = VGroup()
        for r in [0.5, 1.0, 1.5, 2.0, 2.5]:
            c = Circle(radius=r * VS).move_to(VEL_O).set_stroke(FOG, width=0.8, opacity=0.10 + 0.02 * (r == 1.0))
            g.add(c)
        for k in range(12):
            ang = k * TAU / 12
            d = np.array([np.cos(ang), np.sin(ang), 0])
            g.add(Line(VEL_O + d * 0.35 * VS, VEL_O + d * 2.6 * VS).set_stroke(FOG, width=0.6, opacity=0.07))
        g.add(Line(VEL_O + LEFT * 2.8 * VS, VEL_O + RIGHT * 2.8 * VS).set_stroke(FOG, width=0.9, opacity=0.18))
        g.add(Line(VEL_O + DOWN * 1.2 * VS, VEL_O + UP * 4.3 * VS).set_stroke(FOG, width=0.9, opacity=0.18))
        g.add(Dot(VEL_O, radius=0.035, color=IVORY))
        return g

    # ACT 1b: the hodograph -------------------------------------------- #
    def act_hodograph(self):
        e = 0.6
        focus = self.star_anchor
        orbit = ParametricFunction(
            lambda E: LEFT_FOCUS + PS * np.array([np.cos(E) - e, np.sqrt(1 - e * e) * np.sin(E), 0]),
            t_range=[0, TAU, TAU / 160])
        glow(orbit, CORAL, width=2.2, halo=9, halo_op=0.12)
        p_anchor = VectorizedPoint()
        p_anchor.add_updater(lambda m: m.move_to(LEFT_FOCUS + PS * to3(kepler_pos(self.t.get_value(), e))))
        p_anchor.update()
        planet = Billboard(self, p_anchor, planet_layers(CORAL, 0.085), light_from=focus)
        trail = Trail(self.t, e, focus, PS, CORAL)

        def vel_arrow():
            p = p_anchor.get_center()
            v = to3(kepler_vel(self.t.get_value(), e)) * VS
            return Arrow(p, p + v, buff=0, stroke_width=4.5, tip_length=0.16,
                         max_tip_length_to_length_ratio=0.3, color=SKY)

        arrow = always_redraw(vel_arrow)
        self.play(Create(orbit), run_time=1.4)
        self.add(trail, p_anchor, planet)
        planet.vis.set_value(0)
        trail.vis.set_value(0)
        self.play(planet.vis.animate.set_value(1), trail.vis.animate.set_value(1), run_time=0.5)
        self.add(arrow)
        self.play(self.t.animate.set_value(3.2), *self.cap("The blue arrow is the velocity: which way, and how fast."),
                  run_time=4.0, rate_func=linear)

        # Stamp twelve arrows at equal time steps
        stamps, slid = VGroup(), VGroup()
        for k in range(12):
            tk = k * TAU / 12
            p = LEFT_FOCUS + PS * to3(kepler_pos(tk, e))
            v = to3(kepler_vel(tk, e)) * VS
            a0 = Arrow(p, p + v, buff=0, stroke_width=3.2, tip_length=0.13,
                       max_tip_length_to_length_ratio=0.3, color=SKY).set_opacity(0.9)
            a1 = Arrow(VEL_O, VEL_O + v, buff=0, stroke_width=3.2, tip_length=0.13,
                       max_tip_length_to_length_ratio=0.3, color=SKY).set_opacity(0.9)
            stamps.add(a0)
            slid.add(a1)
        self.play(LaggedStart(*[GrowArrow(a) for a in stamps], lag_ratio=0.14),
                  *self.cap("Stamp it at twelve equal moments of the year."), run_time=3.0)
        self.play(LaggedStart(*[Transform(a, b) for a, b in zip(stamps, slid)], lag_ratio=0.05),
                  *self.cap("Now slide every arrow so all the tails meet."), run_time=2.6)
        hodo = Circle(radius=VS * 1.25).move_to(VEL_O + UP * VS * 0.75)
        glow(hodo, SKY, width=2.6, halo=12, halo_op=0.16)
        tips = VGroup(*[Dot(b.get_end(), radius=0.04, color=IVORY) for b in slid])
        self.play(Create(hodo), FadeIn(tips, lag_ratio=0.1),
                  *self.cap("The tips sit on a perfect circle. Hamilton, 1846."), run_time=1.8)
        self.wait(1.0)

        def live():
            v = to3(kepler_vel(self.t.get_value(), e)) * VS
            return Arrow(VEL_O, VEL_O + v, buff=0, stroke_width=5, tip_length=0.17,
                         max_tip_length_to_length_ratio=0.3, color=SKY)

        live_arrow = always_redraw(live)
        tip_anchor = VectorizedPoint()
        tip_anchor.add_updater(lambda m: m.move_to(VEL_O + to3(kepler_vel(self.t.get_value(), e)) * VS))
        tip_anchor.update()
        tip_glow = Billboard(self, tip_anchor, point_glow_layers(IVORY, 0.045))
        self.add(live_arrow, tip_anchor, tip_glow)
        self.play(stamps.animate.set_opacity(0.22), tips.animate.set_opacity(0.3),
                  self.t.animate.set_value(3.2 + TAU),
                  *self.cap("The orbit is an ellipse. The velocity runs around a circle."),
                  run_time=6.0, rate_func=linear)

        f = self.formula([r"\vec v", r"=", r"\frac{GM}{h}", r"\big(", r"-\sin\theta", r",\;", r"e",
                          r"+", r"\cos\theta", r"\big)"],
                         {0: SKY, 2: SKY, 6: CORAL}, np.array([3.5, 2.6, 0]))
        self.play(Write(f), *self.cap("The velocity circle, written out."), run_time=1.4)
        self.wait(0.8)
        self.zoom_to(f, 2, 2.4, "GM over h sets the size: the circle's radius.", run_time=1.4)
        self.wait(1.1)
        self.zoom_to(f, 6, 2.4, "The eccentricity e only slides the circle's center upward.", run_time=1.0)
        self.wait(1.5)
        self.move_camera(frame_center=ORIGIN, zoom=1.0, run_time=1.2,
                         added_anims=[f.animate.set_opacity(1)])
        self.wait(0.2)

        self.headline("Same energy, same year.", font_size=74, hold=1.2)
        for m in (arrow, live_arrow):
            m.clear_updaters()
        self.play(*[FadeOut(m) for m in (orbit, arrow, live_arrow, stamps, tips, hodo, f)],
                  planet.vis.animate.set_value(0), trail.vis.animate.set_value(0),
                  tip_glow.vis.animate.set_value(0), run_time=0.8)
        tip_glow.clear_updaters()
        for m in (planet, trail, p_anchor, tip_anchor):
            m.clear_updaters()
        self.remove(planet, trail, p_anchor, tip_anchor, tip_glow)

    # ACT 2: same energy, same year ------------------------------------ #
    def act_energy(self):
        self.t.set_value(0)
        focus = self.star_anchor
        self.family = VGroup()
        for e, tint in zip(ECCS, TINTS):
            orb = ParametricFunction(
                lambda E, e=e: LEFT_FOCUS + PS * np.array([np.cos(E) - e, np.sqrt(1 - e * e) * np.sin(E), 0]),
                t_range=[0, TAU, TAU / 160])
            glow(orb, tint, width=2.0, halo=8, halo_op=0.11)
            self.family.add(orb)
        self.fam_planets, self.fam_trails = [], []
        for e, tint in zip(ECCS, TINTS):
            anchor = VectorizedPoint()
            anchor.add_updater(lambda m, e=e: m.move_to(LEFT_FOCUS + PS * to3(kepler_pos(self.t.get_value(), e))))
            anchor.update()
            pl = Billboard(self, anchor, planet_layers(tint, 0.07), light_from=focus)
            pl.vis.set_value(0)
            tr = Trail(self.t, e, focus, PS, tint, span=0.7)
            tr.vis.set_value(0)
            self.fam_planets.append((anchor, pl))
            self.fam_trails.append(tr)
        self.play(LaggedStart(*[Create(o) for o in self.family], lag_ratio=0.18),
                  *self.cap("Five orbits, stretched differently, with the same long axis."), run_time=2.4)
        for tr in self.fam_trails:
            self.add(tr)
        for anchor, pl in self.fam_planets:
            self.add(anchor, pl)
        self.play(*[pl.vis.animate.set_value(1) for _, pl in self.fam_planets], run_time=0.6)

        bars = VGroup()
        for k, (e, tint) in enumerate(zip(ECCS, TINTS)):
            y = -2.25 - 0.14 * k
            bars.add(Line([LEFT_FOCUS[0] - PS * (1 + e), y, 0], [LEFT_FOCUS[0] + PS * (1 - e), y, 0])
                     .set_stroke(tint, width=3.2))
        ticks = VGroup(Line([LEFT_FOCUS[0], -2.12, 0], [LEFT_FOCUS[0], -2.95, 0]).set_stroke(FOG, 1, 0.5))
        label = MathTex(r"2a", font_size=40, color=OLIVE_TXT).next_to(bars, LEFT, buff=0.22)
        self.play(LaggedStart(*[Create(b) for b in bars], lag_ratio=0.12), FadeIn(ticks), FadeIn(label),
                  *self.cap("Each long axis has the same length, 2a. Only its position shifts."), run_time=1.6)
        self.wait(1.0)

        f = self.formula([r"E", r"=", r"-\frac{GM}{2a}", r"\qquad", r"T", r"=", r"2\pi\sqrt{a^{3}/GM}"],
                         {0: OLIVE_TXT, 2: OLIVE_TXT, 6: OLIVE_TXT}, np.array([-3.05, 2.75, 0]))
        self.play(Write(f), run_time=1.2)
        self.zoom_to(f, 2, 2.2, "The energy depends only on a, never on the shape.", run_time=1.2)
        self.wait(1.4)
        self.move_camera(frame_center=ORIGIN, zoom=1.0, run_time=1.0, added_anims=[f.animate.set_opacity(1)])
        self.play(*[tr.vis.animate.set_value(1) for tr in self.fam_trails], run_time=0.4)
        self.play(self.t.animate.set_value(TAU), *self.cap("Same a, same period: all five come home together."),
                  run_time=6.0, rate_func=linear)
        self.wait(0.4)
        self.energy_formula = f
        self.bars = VGroup(bars, ticks, label)

    # ACT 3: the two hinge points -------------------------------------- #
    def act_hinges(self):
        self.headline("Every circle passes\nthrough the same two points.", font_size=66, hold=1.4)
        self.play(FadeOut(self.bars), *[tr.vis.animate.set_value(0) for tr in self.fam_trails], run_time=0.5)
        self.hodos = VGroup()
        for e, tint in zip(ECCS, TINTS):
            c = np.sqrt(1 - e * e)
            circ = Circle(radius=VS / c, num_components=48).move_to(VEL_O + UP * VS * e / c)
            glow(circ, tint, width=2.4, halo=10, halo_op=0.13)
            self.hodos.add(circ)
        self.play(LaggedStart(*[Create(h) for h in self.hodos], lag_ratio=0.2),
                  *self.cap("Their velocity circles come in every size and height."), run_time=2.4)
        self.wait(0.6)

        self.hinge_anchors = VGroup(VectorizedPoint(VEL_O + RIGHT * VS), VectorizedPoint(VEL_O + LEFT * VS))
        self.hinges = [Billboard(self, a, point_glow_layers(GOLD, 0.085), facing=False) for a in self.hinge_anchors]
        for h in self.hinges:
            h.vis.set_value(0)
        self.add(self.hinge_anchors, *self.hinges)
        pings = VGroup(*[Circle(radius=0.05).move_to(a.get_center()).set_stroke(GOLD, 3) for a in self.hinge_anchors])
        self.play(*[h.vis.animate.set_value(1) for h in self.hinges],
                  *[p.animate.scale(9).set_stroke(opacity=0) for p in pings],
                  *self.cap("Yet all five pass through the same two gold points."), run_time=1.2)
        self.remove(pings)
        self.wait(1.4)

        p0c = DashedVMobject(Circle(radius=VS, num_components=64).move_to(VEL_O), num_dashes=56)
        p0c.set_stroke(OLIVE_TXT, width=4.2)
        dim_others = [h.animate.set_stroke(opacity=0.28).set_stroke(opacity=0.03, background=True)
                      for h in self.hodos[1:]]
        self.play(Create(p0c), *dim_others,
                  *self.cap("The circular orbit's circle has radius p0, fixed by the energy."),
                  run_time=1.2)
        self.wait(1.2)

        # Pythagoras on the e = 0.75 circle
        e = 0.75
        c = np.sqrt(1 - e * e)
        ctr = VEL_O + UP * VS * e / c
        hp = VEL_O + RIGHT * VS
        leg_d = Line(VEL_O, ctr).set_stroke(CORAL, width=4)
        leg_p = Line(VEL_O, hp).set_stroke(OLIVE, width=4)
        hyp = Line(ctr, hp).set_stroke(SKY, width=4)
        corner = VGroup(Line(VEL_O + RIGHT * 0.16, VEL_O + RIGHT * 0.16 + UP * 0.16),
                        Line(VEL_O + UP * 0.16, VEL_O + RIGHT * 0.16 + UP * 0.16)).set_stroke(IVORY, 1.6, 0.8)
        lab_d = MathTex(r"d", font_size=44, color=CORAL).next_to(leg_d, LEFT, buff=0.14)
        lab_p = MathTex(r"p_0", font_size=44, color=OLIVE_TXT).next_to(leg_p, DOWN, buff=0.16)
        lab_r = MathTex(r"R", font_size=44, color=SKY).move_to((ctr + hp) / 2 + np.array([0.3, 0.2, 0]))
        tri = VGroup(leg_d, leg_p, hyp, corner, lab_d, lab_p, lab_r)
        self.play(self.hodos[3].animate.set_stroke(width=3.4, opacity=1).set_stroke(opacity=0.13, background=True),
                  Create(leg_d), Create(leg_p), Create(hyp),
                  FadeIn(corner), FadeIn(lab_d), FadeIn(lab_p), FadeIn(lab_r),
                  *self.cap("A right triangle: legs d and p0, hypotenuse R."), run_time=1.6)
        self.wait(0.8)

        f = self.formula([r"R^{2}", r"=", r"d^{2}", r"+", r"p_0^{2}", r",\qquad", r"p_0", r"=", r"\sqrt{-2E}"],
                         {0: SKY, 2: CORAL, 4: OLIVE_TXT, 6: OLIVE_TXT, 8: OLIVE_TXT}, np.array([-3.05, 2.75, 0]))
        self.play(FadeOut(self.energy_formula), Write(f), run_time=1.2)
        self.zoom_to(f, 0, 2.2, "R: the radius of a velocity circle.", run_time=1.2)
        self.wait(1.0)
        self.zoom_to(f, 2, 2.2, "d: how far its center sits above the origin.", run_time=0.9)
        self.wait(1.1)
        self.zoom_to(f, 4, 2.2, "p0: the same for every orbit of this energy.", run_time=0.9)
        self.wait(1.3)
        self.move_camera(frame_center=ORIGIN, zoom=1.0, run_time=1.2, added_anims=[
            f.animate.set_opacity(1),
            *[h.animate.set_stroke(opacity=1).set_stroke(opacity=0.13, background=True) for h in self.hodos]])
        self.wait(0.3)
        self.hinge_formula = f
        self.p0c = p0c
        self.tri = tri

    # ACT 4: lift the plane onto a sphere ------------------------------ #
    def act_lift(self):
        self.headline("Lift the plane onto a sphere.", font_size=74, hold=1.2)
        left_stuff = [self.family, self.hinge_formula, self.tri, self.p0c]
        movers = VGroup(self.hodos, self.hinge_anchors)
        self.play(*[FadeOut(m) for m in left_stuff],
                  *[pl.vis.animate.set_value(0) for _, pl in self.fam_planets],
                  self.star.vis.animate.set_value(0),
                  FadeOut(self.velocity_grid),
                  movers.animate.scale(K_LIFT, about_point=VEL_O).shift(-VEL_O),
                  run_time=1.8)
        for anchor, pl in self.fam_planets:
            anchor.clear_updaters()
            pl.clear_updaters()
            self.remove(anchor, pl)
        for tr in self.fam_trails:
            tr.clear_updaters()
            self.remove(tr)
        self.star.clear_updaters()
        self.remove(self.star)

        self.move_camera(phi=64 * DEGREES, theta=-62 * DEGREES, zoom=0.85, run_time=2.6)

        # Swap the flat circles for liftable rings (identical at lam = 0)
        self.rings = [Ring(self, e, tint) for e, tint in zip(ECCS, TINTS)]
        self.remove(self.hodos)
        self.add(*self.rings)
        for h in self.hinges:
            h.facing = True

        self.sphere = GlassSphere(self, SPH)
        self.sil = Silhouette(self, SPH)
        self.spec_anchor = VectorizedPoint()

        def place_spec(m):
            eye = eye_of(self.camera)
            v = eye / np.linalg.norm(eye)
            h = v + LIGHT
            h /= np.linalg.norm(h)
            m.move_to(h * SPH * 1.01)

        self.spec_anchor.add_updater(place_spec)
        place_spec(self.spec_anchor)
        self.spec = Billboard(self, self.spec_anchor,
                              soft_glow(IVORY, 0.03, 0.42, 0.75, n=12, power=2.6)
                              + [{"r": 0.024, "color": "#ffffff", "op": 0.92}])
        self.spec.vis.set_value(0)
        self.plate = Plate()
        self.add(self.plate, self.sphere, self.sil, self.spec_anchor, self.spec)
        # hinge glows drawn above the glass
        for h in self.hinges:
            self.remove(h)
            self.add(h)
        self.play(self.sphere.vis.animate.set_value(1), self.sil.vis.animate.set_value(1),
                  self.spec.vis.animate.set_value(1), self.plate.vis.animate.set_value(1),
                  *self.cap("A glass sphere of radius p0. Its equator is the p0 circle."), run_time=2.0)
        self.wait(0.6)

        # Projection rays through the e = 0.55 circle
        ring = self.rings[2]
        e = 0.55
        c = np.sqrt(1 - e * e)
        north = np.array([0, 0, SPH])
        rays = VGroup()
        for k in range(24):
            s = k * TAU / 24
            v = np.array([-np.sin(s), e + np.cos(s)]) / c
            q = to3(v) * SPH
            rays.add(Line(north, north + 1.1 * (q - north)).set_stroke(GOLD, width=1.5, opacity=0.55))
        pole = Billboard(self, VectorizedPoint(north), point_glow_layers(IVORY, 0.05))
        self.add(pole)
        pole.vis.set_value(0)
        self.play(LaggedStart(*[Create(r) for r in rays], lag_ratio=0.04), pole.vis.animate.set_value(1),
                  *self.cap("From the north pole, draw a line through each point."), run_time=1.6)
        self.play(ring.lam.animate.set_value(1), run_time=1.8, rate_func=smooth)
        self.move_camera(zoom=1.4, run_time=3.2, rate_func=smooth, added_anims=[
            *[r.lam.animate.set_value(1) for i, r in enumerate(self.rings) if i != 2],
            rays.animate.set_stroke(opacity=0), pole.vis.animate.set_value(0),
            *self.cap("Every circle lands as a great circle, hinged on the gold points.")])
        self.remove(rays, pole)
        self.wait(0.4)

        f = MathTex(r"\vec u", r"\;\longmapsto\;", r"\frac{1}{|\vec u|^{2}+p_0^{2}}", r"\big(",
                    r"2p_0^{2}\,\vec u", r",\;", r"p_0\,(|\vec u|^{2}-p_0^{2})", r"\big)",
                    font_size=40, color=IVORY)
        f[0].set_color(SKY)
        f.to_edge(UP, buff=0.3)
        self.add_fixed_in_frame_mobjects(f)
        self.begin_ambient_camera_rotation(rate=0.09)
        self.play(FadeIn(f), *self.cap("Stereographic projection: circles stay circles."), run_time=0.8)
        self.wait(4.2)
        self.stop_ambient_camera_rotation()
        self.play(FadeOut(f), run_time=0.5)
        self.remove_fixed_in_frame_mobjects(f)

    # ACT 5: eccentricity is an angle (the big zoom) ------------------- #
    def act_angle(self):
        self.headline("Eccentricity is an angle.", font_size=74, hold=1.2)
        for r in self.rings:
            r.mode = "E"
        self.move_camera(phi=90 * DEGREES, theta=0, zoom=1.3, run_time=3.0,
                         added_anims=[self.plate.vis.animate.set_value(0.35),
                                      *self.cap("Look straight down the hinge: every ring becomes a line.")])
        self.wait(0.6)
        feat = self.rings[2]
        arc = always_redraw(lambda: ParametricFunction(
            lambda s: 0.62 * SPH * np.array([0.02, np.cos(s), np.sin(s)]),
            t_range=[0, max(feat.tilt.get_value(), 1e-3), max(feat.tilt.get_value(), 1e-3) / 40])
            .set_stroke(GOLD, width=3.2))
        card = MathTex(r"e", r"=", r"\sin", r"\alpha", font_size=64, color=IVORY)
        card[0].set_color(CORAL)
        card[3].set_color(GOLD)
        card.rotate(90 * DEGREES, RIGHT, about_point=ORIGIN).rotate(90 * DEGREES, OUT, about_point=ORIGIN)
        card.move_to(np.array([0.3, 3.25, 1.35]))
        a_lab = MathTex(r"\alpha", font_size=40, color=GOLD)
        a_lab.rotate(90 * DEGREES, RIGHT, about_point=ORIGIN).rotate(90 * DEGREES, OUT, about_point=ORIGIN)
        a_lab.move_to(0.62 * SPH * np.array([0.03, np.cos(0.29), np.sin(0.29)]) + np.array([0, 0.28, 0.02]))
        self.play(Create(arc), FadeIn(a_lab), Write(card), *[r.vis.animate.set_value(0.45) for i, r in enumerate(self.rings) if i not in (0, 2)],
                  run_time=1.6)
        self.wait(0.4)
        # THE BIG ZOOM
        self.move_camera(frame_center=card[3].get_center(), zoom=3.9, run_time=2.2,
                         added_anims=[card[0].animate.set_opacity(0.3), card[1].animate.set_opacity(0.3),
                                      card[2].animate.set_opacity(0.3),
                                      *self.cap("Alpha, the ring's tilt, is the whole shape of the orbit.")])
        self.wait(2.4)
        self.move_camera(frame_center=ORIGIN, zoom=1.3, run_time=2.0,
                         added_anims=[card.animate.set_opacity(1)])
        self.wait(0.3)
        self.play(FadeOut(a_lab), *[r.vis.animate.set_value(0.3) for i, r in enumerate(self.rings) if i != 2],
                  run_time=0.4)
        self.play(feat.tilt.animate.set_value(PI / 2),
                  *self.cap("Push e toward 1 and the ring stands up through the north pole."),
                  run_time=4.5, rate_func=smooth)
        north = Billboard(self, VectorizedPoint(np.array([0, 0, SPH * 1.004])), point_glow_layers(IVORY, 0.07))
        north.vis.set_value(0)
        self.add(north)
        ping = Circle(radius=0.06).rotate(90 * DEGREES, UP).move_to(np.array([0.05, 0, SPH])).set_stroke(IVORY, 3)
        self.play(north.vis.animate.set_value(1), ping.animate.scale(8).set_stroke(opacity=0),
                  *self.cap("A head-on fall reaches infinite speed. Here it is one point."), run_time=0.8)
        self.remove(ping)
        self.wait(2.2)
        self.north = north
        self.arc = arc
        self.card = card

    # ACT 6: rotate the sphere, change the orbit ----------------------- #
    def act_rotation(self):
        self.arc.clear_updaters()
        self.play(FadeOut(self.arc), FadeOut(self.card), run_time=0.5)
        self.headline("Rotate the sphere,\nchange the orbit.", font_size=68, hold=1.2)
        feat = self.rings[2]
        self.move_camera(phi=66 * DEGREES, theta=-60 * DEGREES, zoom=1.45, run_time=2.4,
                         added_anims=[self.north.vis.animate.set_value(0), self.plate.vis.animate.set_value(1)])
        self.north.clear_updaters()
        self.remove(self.north)

        # Inset: the orbit that belongs to the featured ring (same energy, a = 1)
        panel_c = np.array([-4.9, -1.5, 0])
        s_i = 0.78
        foc = panel_c + np.array([0.55, 0.0, 0])
        panel = RoundedRectangle(width=3.5, height=2.45, corner_radius=0.14)
        panel.set_stroke(FOG, width=1, opacity=0.45).set_fill(INK, opacity=0.62).move_to(panel_c)
        star_dot = VGroup(Dot(foc, radius=0.11, color=GOLD).set_opacity(0.25), Dot(foc, radius=0.05, color="#fff1dc"))

        ell = VMobject()

        def upd_ell(m):
            a = feat.tilt.get_value()
            ee, cc = np.sin(a), np.cos(a)
            E = np.linspace(0, TAU, 121)
            pts = foc + s_i * np.column_stack([np.cos(E) - ee, cc * np.sin(E), np.zeros_like(E)])
            m.set_points_smoothly(pts)
            glow(m, CORAL, width=2.4, halo=8, halo_op=0.14)

        upd_ell(ell)
        ell.add_updater(upd_ell)
        axis = VMobject()

        def upd_axis(m):
            ee = np.sin(feat.tilt.get_value())
            m.set_points_as_corners([foc + s_i * np.array([-(1 + ee), -0.0, 0]) + DOWN * 0.95,
                                     foc + s_i * np.array([1 - ee, 0, 0]) + DOWN * 0.95])
            m.set_stroke(OLIVE, width=3)

        upd_axis(axis)
        axis.add_updater(upd_axis)
        inset = VGroup(panel, star_dot, ell, axis)
        self.add_fixed_in_frame_mobjects(inset)
        for i, r in enumerate(self.rings):
            if i != 2:
                r.vis.set_value(0.3)
        self.begin_ambient_camera_rotation(rate=0.05)
        self.play(FadeIn(inset), feat.tilt.animate.set_value(0.0),
                  *self.cap("Rotate a ring about the hinge: the orbit stretches, same energy."),
                  run_time=2.6, rate_func=smooth)
        self.wait(0.4)
        halley = float(np.arcsin(0.96714))
        earth = float(np.arcsin(0.0167086))
        lab_h = MathTex(r"\text{Halley:}\;\; e=0.967,\;\; \alpha=75.3^{\circ}", font_size=34, color=IVORY)
        lab_h.next_to(panel, UP, buff=0.2, aligned_edge=LEFT)
        lab_e = MathTex(r"\text{Earth:}\;\; e=0.0167,\;\; \alpha=0.96^{\circ}", font_size=34, color=IVORY)
        lab_e.next_to(panel, UP, buff=0.2, aligned_edge=LEFT)
        self.play(feat.tilt.animate.set_value(halley), run_time=2.8, rate_func=smooth)
        self.add_fixed_in_frame_mobjects(lab_h)
        self.play(FadeIn(lab_h), *self.cap("Halley's comet, e = 0.967: its ring tilts 75.3 degrees."), run_time=0.6)
        self.wait(1.4)
        self.play(feat.tilt.animate.set_value(earth), FadeOut(lab_h), run_time=2.2, rate_func=smooth)
        self.add_fixed_in_frame_mobjects(lab_e)
        self.play(FadeIn(lab_e), *self.cap("Earth, e = 0.0167: its ring tilts less than one degree."), run_time=0.6)
        self.wait(1.4)

        hyd = MathTex(r"E_n", r"=", r"-\frac{13.6\ \mathrm{eV}}{n^{2}}", r",\qquad", r"n^{2}",
                      r"\ \text{states per level}", font_size=44, color=IVORY)
        hyd[0].set_color(OLIVE_TXT)
        hyd[2].set_color(OLIVE_TXT)
        hyd[4].set_color(GOLD)
        hyd.to_edge(UP, buff=0.45)
        self.add_fixed_in_frame_mobjects(hyd)
        self.play(FadeIn(hyd), FadeOut(lab_e), FadeOut(inset),
                  feat.tilt.animate.set_value(float(np.arcsin(0.55))),
                  *[r.vis.animate.set_value(1) for r in self.rings],
                  *self.cap("Fock, 1935: the same sphere, in four dimensions, organizes hydrogen."),
                  run_time=1.2)
        ell.clear_updaters()
        axis.clear_updaters()
        self.wait(3.2)

        # Finale: planets running along their rings (true Kepler timing)
        self.t.set_value(0)
        runners = []
        for r, e, tint in zip(self.rings, ECCS, TINTS):
            anchor = VectorizedPoint()

            def mv(m, e=e):
                E = float(ecc_anomaly(self.t.get_value(), e))
                c = np.sqrt(1 - e * e)
                m.move_to(SPH * 1.006 * np.array([-np.sin(E), c * np.cos(E), e * np.cos(E)]))

            anchor.add_updater(mv)
            mv(anchor)
            bb = Billboard(self, anchor, planet_layers(tint, 0.07), facing=True)
            bb.vis.set_value(0)
            self.add(anchor, bb)
            runners.append(bb)
        self.play(FadeOut(hyd), *self.cap(None), *[b.vis.animate.set_value(1) for b in runners], run_time=0.8)
        self.play(self.t.animate.set_value(4.4), run_time=4.4, rate_func=linear)
        # End title over the running armillary
        title = Text("Every orbit is a great circle.", font=HEAD_FONT, weight=BOLD, font_size=64, color=IVORY)
        if title.width > 12.4:
            title.scale_to_fit_width(12.4)
        rule = Line(LEFT * 0.45, RIGHT * 0.45).set_stroke(GOLD, width=3).next_to(title, UP, buff=0.45)
        sub = Text("Hamilton 1846  ·  Fock 1935  ·  Moser 1970", font=CAP_FONT, slant=ITALIC,
                   font_size=26, color=FOG).next_to(title, DOWN, buff=0.4)
        endcard = VGroup(rule, title, sub).to_edge(DOWN, buff=0.7)
        shade = Rectangle(width=16.5, height=3.2).set_stroke(width=0).set_fill(INK, opacity=0.72).to_edge(DOWN, buff=0)
        self.add_fixed_in_frame_mobjects(shade, endcard)
        self.play(FadeIn(shade), FadeIn(endcard, shift=UP * 0.15),
                  self.t.animate.set_value(5.6), run_time=1.2, rate_func=linear)
        self.play(self.t.animate.set_value(8.4), run_time=2.8, rate_func=linear)
        self.stop_ambient_camera_rotation()
        fade = Rectangle(width=16.5, height=9.6).set_stroke(width=0).set_fill(BLACK, opacity=1)
        self.add_fixed_in_frame_mobjects(fade)
        self.play(FadeIn(fade), self.t.animate.set_value(9.6), run_time=1.2, rate_func=linear)
