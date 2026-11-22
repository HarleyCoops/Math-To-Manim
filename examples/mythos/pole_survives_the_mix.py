"""The Mix That Cannot Kill a Pole -- a Mythos film (Cinematic Charter, rules 1-11).

Three copies of a curve g, two of them delayed by log 2 and log 4, are added
with weights -1, 3, -2:

    D(u) = -g(u) + 3 g(u - log 2) - 2 g(u - log 4).

On the Laplace side the mix is multiplication by

    m(s) = -1 + 3*2^(-s) - 2*4^(-s) = (1 - q)(2q - 1),   q = 2^(-s).

For 0 < Re s < 1 the number q lies strictly between the circles |q| = 1/2 and
|q| = 1, and the two zeros q = 1, q = 1/2 lie on those circles. So m has no
zero inside the strip and a pole there survives, with residue times m(rho).

Source of the mathematics: L. Crossley, DelayedPole.lean
(github.com/leecrossley/prime-window-rh-criterion, dirichlet-window-transfer).

Rendering notes
---------------
* One continuous 3D world with five stations 18 units apart along x. The
  camera flies between them; formulas that are zoomed lie on the floor
  (z = 0) and are read top-down, 3D structures rise out of the same floor.
* Cairo ThreeDScene, ``should_apply_shading = False``: surface colours are
  computed here from the mathematics (height, radius).
* Every number on screen is computed in this file from RHO, the first zero
  of the Riemann zeta function: q = 2^(-RHO), m(RHO), |m(RHO)| = 3.984.
* The night sky is a procedural background pixel array (no files).
"""

from manim import *
import numpy as np

# --------------------------------------------------------------------------
# Palette: the cast list
# --------------------------------------------------------------------------
INK = "#0c0c0b"
IVORY = "#faf9f5"     # the sum D, the pole
FOG = "#b0aea5"
CORAL = "#d97757"     # copy one, weight -1
GOLD = "#d4a27f"      # copy two, delay log 2, weight 3
SKY = "#6a9bcc"       # copy three, delay log 4, weight -2
OLIVE = "#788c5d"     # q, the strip, the ribbon
OLIVE_TXT = "#a3b58a"
EMBER = "#e8623c"     # the kill points: zeros of m
DECK = "#191b20"

HEAD_FONT = "Poppins"
CAP_FONT = "Lora"

# --------------------------------------------------------------------------
# Mathematics (all on-screen numbers come from here)
# --------------------------------------------------------------------------
LOG2 = float(np.log(2.0))
GAMMA1 = 14.134725141734693          # first zeta zero: rho = 1/2 + i*GAMMA1
RHO = complex(0.5, GAMMA1)
PERIOD = 2 * np.pi / LOG2            # 9.0647: spacing of the zeros of m on a wall


def q_of(s):
    return np.exp(-np.asarray(s, dtype=complex) * LOG2)


def m_of(s):
    q = q_of(s)
    return (1 - q) * (2 * q - 1)


Q_RHO = complex(q_of(RHO))           # -0.6586 + 0.2575i, radius 0.7071
M_RHO = complex(m_of(RHO))           # -3.7106 + 1.4506i, modulus 3.9840


def floor_of(sigma):
    r = 2.0 ** (-sigma)
    return (1 - r) * (2 * r - 1)


def g_fun(u):
    """The demonstration curve: a chord of two growing tones, g(0) = 0."""
    return 0.20 * np.exp(0.16 * u) * np.sin(2.9 * u) + 0.09 * np.exp(0.10 * u) * np.sin(6.1 * u)


def g_delayed(u, a):
    return np.where(u > a, g_fun(np.maximum(u - a, 0.0)), 0.0)


# --------------------------------------------------------------------------
# World layout: five stations along x
# --------------------------------------------------------------------------
P = [np.array([18.0 * k, 0.0, 0.0]) for k in range(5)]

U_MAX, LX0, LXS = 6.6, -5.2, 1.55            # lanes: u in [0, U_MAX], x = LX0 + LXS*u
LANE_Y = (2.6, 0.0, -2.6)

HU, HX0, HXS, HA, HZ = 3.0, -4.8, 3.2, 0.15, 2.9   # helix station
U0 = 2 * np.pi * 5 / GAMMA1                          # tone has phase 0 here

QR, QH = 2.4, 1.5                            # q-station: radius of |q|=1, height per turn
SX, SY, ZS, T_LO, T_HI = 4.2, 0.36, 0.42, -1.0, 21.0   # landscape station


def glow(m, color, width=3.0, halo=10.0, halo_op=0.16, opacity=1.0):
    m.set_fill(opacity=0)
    m.set_stroke(color, width=width, opacity=opacity)
    m.set_stroke(color, width=halo, opacity=halo_op * opacity, background=True)
    return m


def polyline(points, color, width=3.0, halo=10.0, halo_op=0.16):
    m = VMobject()
    m.set_points_as_corners(np.asarray(points, dtype=float))
    return glow(m, color, width=width, halo=halo, halo_op=halo_op)


def glow_dot(point, color, radius=0.09):
    core = Dot(point=point, radius=radius * 0.55, color=IVORY)
    halo = VGroup(*[
        Dot(point=point, radius=radius * (1 + 0.9 * i), color=color).set_fill(color, opacity=0.5 / (i + 1.0))
        for i in range(1, 5)
    ])
    return VGroup(halo, core)


def bead(point, color=IVORY, radius=0.10):
    core = Dot3D(point=point, radius=radius, color=color, resolution=(6, 6))
    halo = Dot3D(point=point, radius=radius * 2.3, color=color, resolution=(6, 6)).set_opacity(0.16)
    return VGroup(halo, core)


def stand(mob):
    """Stand a flat mobject upright in the xz-plane, facing the -y side."""
    return mob.rotate(PI / 2, axis=RIGHT)


def deck(center, w=14.0, h=8.0, op=0.10):
    lines = VGroup()
    for x in np.arange(-w / 2, w / 2 + 1e-6, 1.0):
        lines.add(Line([x, -h / 2, 0], [x, h / 2, 0]))
    for y in np.arange(-h / 2, h / 2 + 1e-6, 1.0):
        lines.add(Line([-w / 2, y, 0], [w / 2, y, 0]))
    lines.set_stroke(FOG, width=1, opacity=op)
    plate = Rectangle(width=w, height=h).set_stroke(GOLD, width=1.6, opacity=0.34)
    plate.set_fill(DECK, opacity=0.55)
    return VGroup(plate, lines).shift(center)


def make_sky(w, h, seed=11):
    """Procedural night sky: ink base, two faint palette nebulae, vignette, stars."""
    rng = np.random.default_rng(seed)
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    nx = (x - w / 2) / (w / 2)
    ny = (y - h / 2) / (h / 2)
    r2 = nx * nx * 0.8 + ny * ny
    base = np.array([12, 12, 11], np.float32)
    lift = np.array([20, 23, 31], np.float32)
    mixv = np.clip(1 - r2 * 0.75, 0, 1)[..., None]
    img = base * (1 - mixv) + lift * mixv
    band1 = np.exp(-((ny * 1.1 + nx * 0.5 - 0.15) ** 2) / 0.06)
    band2 = np.exp(-((ny * 0.9 - nx * 0.6 + 0.4) ** 2) / 0.10)
    ripple = 0.55 + 0.45 * np.sin(nx * 6.3 + 0.9) * np.sin(ny * 4.7 - 0.4)
    img += (band1 * ripple * 7.0)[..., None] * np.array([0.55, 0.75, 1.0], np.float32)
    img += (band2 * ripple * 5.0)[..., None] * np.array([1.0, 0.62, 0.45], np.float32)
    img *= (1 - 0.45 * np.clip(r2, 0, 1.6) ** 1.4)[..., None]
    n = int(w * h / 2300)
    xs = rng.integers(2, w - 2, n)
    ys = rng.integers(2, h - 2, n)
    mag = rng.random(n) ** 3.4
    tint = rng.random(n)
    for sx, sy, mg, tt in zip(xs, ys, mag, tint):
        col = np.array([255, 244, 228], np.float32) if tt < 0.6 else np.array([214, 228, 255], np.float32)
        peak = 30 + 190 * mg
        img[sy, sx] += col / 255 * peak
        if mg > 0.45:
            for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
                img[sy + dy, sx + dx] += col / 255 * peak * 0.3
    img = np.clip(img, 0, 255).astype(np.uint8)
    return np.concatenate([img, np.full((h, w, 1), 255, np.uint8)], axis=-1)


# --------------------------------------------------------------------------
# Geometry builders
# --------------------------------------------------------------------------
def lane_points(a, w, y, n=240):
    us = np.linspace(0, U_MAX, n)
    return np.stack([LX0 + LXS * us, np.full(n, y), w * g_delayed(us, a)], axis=1)


def lane_curve(a, w, y, color, width=3.2):
    return polyline(lane_points(a, w, y), color, width=width)


def mix_points(y=0.0, n=320):
    us = np.linspace(0, U_MAX, n)
    vals = -g_delayed(us, 0.0) + 3 * g_delayed(us, LOG2) - 2 * g_delayed(us, 2 * LOG2)
    return np.stack([LX0 + LXS * us, np.full(n, y), vals], axis=1)


def helix_points(center, a, weight, n=620):
    """weight * e^(RHO (u - a)) for u > a, drawn as (x, Re, Im) around the axis."""
    us = np.linspace(0, HU, n)
    val = np.where(us > a, np.exp(RHO * np.maximum(us - a, 0.0)), 0.0) * weight * HA
    pts = np.stack([HX0 + HXS * us, val.real, val.imag + HZ], axis=1)
    return pts + center


def ribbon_point(center, r, th, lift):
    return center + np.array([QR * r * np.cos(th), -QR * r * np.sin(th), lift * QH * th / TAU])


def strip_xy(center, sigma, t):
    return center + np.array([SX * (sigma - 0.5), SY * (t - 10.0), 0.0])


def height_color(v):
    """Colour of the landscape at height |m| = v (0 ... 6)."""
    stops = [(0.0, "#2a1d1a"), (0.25, EMBER), (1.2, OLIVE), (2.8, SKY), (4.4, GOLD), (6.0, IVORY)]
    for (v0, c0), (v1, c1) in zip(stops, stops[1:]):
        if v <= v1:
            return interpolate_color(ManimColor(c0), ManimColor(c1), (v - v0) / (v1 - v0))
    return ManimColor(IVORY)


class PoleSurvivesTheMixJourney(ThreeDScene):
    # ------------------------------------------------------------------ #
    # Narration layer (fixed in frame)                                    #
    # ------------------------------------------------------------------ #
    def setup_layers(self):
        self.cap_mob = None
        self.hud_mob = None
        self.gallery = []

    def _swap(self, attr, new, run_time, shift):
        old = getattr(self, attr)
        anims = []
        if old is not None:
            anims.append(FadeOut(old))
        if new is not None:
            self.add_fixed_in_frame_mobjects(new)
            anims.append(FadeIn(new, shift=shift))
        setattr(self, attr, new)
        if anims:
            self.play(*anims, run_time=run_time)
        if old is not None:
            self.remove_fixed_in_frame_mobjects(old)
            self.remove(old)

    def say(self, text, run_time=0.5, hold=0.0):
        """Lower-third caption; replaces the previous one."""
        new = None
        if text:
            line = Text(text, font=CAP_FONT, slant=ITALIC, font_size=30, color=IVORY)
            if line.width > 12.2:
                line.scale_to_fit_width(12.2)
            plate = RoundedRectangle(corner_radius=0.16, width=line.width + 0.7, height=line.height + 0.44)
            plate.set_stroke(width=0).set_fill(INK, opacity=0.66)
            new = VGroup(plate, line).to_edge(DOWN, buff=0.34)
        self._swap("cap_mob", new, run_time, UP * 0.08)
        if hold:
            self.wait(hold)

    def hud(self, formula, run_time=0.7):
        """Formula card at the top of the frame, used over 3D set pieces."""
        new = None
        if formula is not None:
            if formula.width > 11.6:
                formula.scale_to_fit_width(11.6)
            plate = RoundedRectangle(corner_radius=0.2, width=formula.width + 0.9, height=formula.height + 0.55)
            plate.set_stroke(GOLD, width=1.2, opacity=0.4).set_fill(INK, opacity=0.72)
            formula.move_to(plate)
            new = VGroup(plate, formula).to_edge(UP, buff=0.38)
        self._swap("hud_mob", new, run_time, DOWN * 0.08)

    def headline(self, text, sub=None, hold=1.5, font_size=66):
        self.say(None, run_time=0.3)
        self.hud(None, run_time=0.3)
        title = VGroup(*[Text(line, font=HEAD_FONT, weight=BOLD, font_size=font_size, color=IVORY)
                         for line in text.split("\n")]).arrange(DOWN, buff=0.28)
        if title.width > 11.8:
            title.scale_to_fit_width(11.8)
        rule = Line(LEFT * 0.5, RIGHT * 0.5).set_stroke(GOLD, width=3)
        group = VGroup(rule, title).arrange(DOWN, buff=0.45)
        if sub:
            subline = Text(sub, font=CAP_FONT, slant=ITALIC, font_size=30, color=GOLD)
            if subline.width > 11.0:
                subline.scale_to_fit_width(11.0)
            group.add(subline)
            group.arrange(DOWN, buff=0.45)
        group.move_to(ORIGIN)
        dim = Rectangle(width=16.5, height=9.6).set_stroke(width=0).set_fill(INK, opacity=0.84)
        self.add_fixed_in_frame_mobjects(dim, group)
        self.play(FadeIn(dim), FadeIn(group, shift=UP * 0.15), run_time=0.9)
        self.wait(hold)
        self.play(FadeOut(group, shift=UP * 0.3), FadeOut(dim), run_time=0.75)
        self.remove_fixed_in_frame_mobjects(dim, group)
        self.remove(dim, group)

    # ------------------------------------------------------------------ #
    # Camera grammar                                                      #
    # ------------------------------------------------------------------ #
    def fly(self, center, phi, theta, zoom, run_time=3.0, out=(), into=()):
        self.say(None, run_time=0.3)
        self.hud(None, run_time=0.3)
        anims = [FadeOut(m) for m in out] + [FadeIn(m) for m in into]
        self.move_camera(frame_center=center, phi=phi, theta=theta, zoom=zoom,
                         run_time=run_time, added_anims=anims)
        for m in out:
            self.remove(m)

    def zoom_part(self, formula, ids, zoom, text, color=IVORY, hold=1.7, run_time=1.5):
        """Dim the formula, frame one part, fly straight above it. Returns the frame."""
        target = VGroup(*[formula[i] for i in ids])
        frame = SurroundingRectangle(target, color=color, buff=0.14, stroke_width=2.5, corner_radius=0.08)
        dims = [m.animate.set_opacity(0.22) for i, m in enumerate(formula) if i not in ids]
        self.say(text)
        self.move_camera(frame_center=target.get_center(), zoom=zoom, phi=0, theta=-90 * DEGREES,
                         run_time=run_time, added_anims=[*dims, Create(frame)])
        self.wait(hold)
        return frame

    def pull_back(self, formula, frame, center, zoom=1.0, run_time=1.3, phi=0.0):
        self.move_camera(frame_center=center, zoom=zoom, phi=phi, theta=-90 * DEGREES, run_time=run_time,
                         added_anims=[formula.animate.set_opacity(1), FadeOut(frame)])
        self.remove(frame)

    # ------------------------------------------------------------------ #
    # Film                                                                #
    # ------------------------------------------------------------------ #
    def construct(self):
        self.setup_layers()
        cam = self.camera
        cam.should_apply_shading = False
        cam.set_background(make_sky(cam.pixel_width, cam.pixel_height))
        self.act_lanes()
        self.act_tone()
        self.act_symbol()
        self.act_ribbon()
        self.act_landscape()
        self.act_gallery()

    # ACT 1: three copies, two delays, three weights -------------------- #
    def act_lanes(self):
        C = P[0]
        self.set_camera_orientation(phi=64 * DEGREES, theta=-106 * DEGREES, zoom=0.84,
                                    frame_center=C + OUT * 0.5 + LEFT * 0.5)
        deck1 = deck(C)
        y1, y2, y3 = LANE_Y
        x_end = LX0 + LXS * U_MAX
        base = lane_curve(0.0, 1.0, y2, IVORY).shift(C)
        self.play(FadeIn(deck1), run_time=1.0)
        self.play(Create(base), run_time=2.6, rate_func=linear)
        self.headline("The Mix That\nCannot Kill a Pole",
                      sub="three copies of one curve, weights −1, 3, −2", hold=2.0)

        axis_u = Arrow(C + np.array([LX0, y2 - 3.55, 0]), C + np.array([x_end, y2 - 3.55, 0]),
                       buff=0, stroke_width=2, max_tip_length_to_length_ratio=0.02).set_color(FOG)
        lab_u = stand(MathTex("u", font_size=44, color=FOG)).move_to(C + np.array([x_end + 0.35, y2 - 3.55, 0.25]))
        lab_g = stand(MathTex("g(u)", font_size=46, color=IVORY)).move_to(C + np.array([LX0 - 0.95, y2, 0.45]))
        self.say("Start with one curve, g. Its height changes as u moves to the right.")
        self.play(FadeIn(axis_u), FadeIn(lab_u), FadeIn(lab_g), run_time=0.8)
        self.wait(1.4)

        # three copies
        lanes = VGroup(*[Line(C + np.array([LX0, y, 0]), C + np.array([x_end, y, 0])) for y in LANE_Y])
        lanes.set_stroke(FOG, width=1.5, opacity=0.4)
        c1 = lane_curve(0.0, 1.0, y1, CORAL).shift(C)
        c2 = lane_curve(0.0, 1.0, y2, GOLD).shift(C)
        c3 = lane_curve(0.0, 1.0, y3, SKY).shift(C)
        self.say("Make three copies of it.")
        self.play(ReplacementTransform(base.copy(), c1), ReplacementTransform(base.copy(), c3),
                  ReplacementTransform(base, c2), FadeIn(lanes), FadeOut(lab_g), run_time=1.8)
        self.wait(0.6)

        # two delays
        a2, a3 = ValueTracker(0.0), ValueTracker(0.0)
        w1, w2, w3 = ValueTracker(1.0), ValueTracker(1.0), ValueTracker(1.0)
        self.remove(c1, c2, c3)
        c1 = always_redraw(lambda: lane_curve(0.0, w1.get_value(), y1, CORAL).shift(C))
        c2 = always_redraw(lambda: lane_curve(a2.get_value(), w2.get_value(), y2, GOLD).shift(C))
        c3 = always_redraw(lambda: lane_curve(a3.get_value(), w3.get_value(), y3, SKY).shift(C))
        self.add(c1, c2, c3)

        def bracket(y, a, color, tex):
            p0 = C + np.array([LX0, y - 0.62, 0])
            p1 = C + np.array([LX0 + LXS * a, y - 0.62, 0])
            bar = VGroup(Line(p0, p1), Line(p0 + DOWN * 0.12, p0 + UP * 0.12), Line(p1 + DOWN * 0.12, p1 + UP * 0.12))
            bar.set_stroke(color, width=3)
            lab = stand(MathTex(tex, font_size=40, color=color)).move_to((p0 + p1) / 2 + np.array([0, -0.08, 0.34]))
            return VGroup(bar, lab)

        br2 = bracket(y2, LOG2, GOLD, r"\log 2")
        br3 = bracket(y3, 2 * LOG2, SKY, r"\log 4")
        self.say("Delay the second copy by log 2, and the third by log 4.")
        self.play(a2.animate.set_value(LOG2), a3.animate.set_value(2 * LOG2),
                  FadeIn(br2), FadeIn(br3), run_time=2.8)
        self.wait(1.2)

        # three weights
        wl = VGroup(
            stand(MathTex(r"\times(-1)", font_size=46, color=CORAL)).move_to(C + np.array([LX0 - 1.0, y1, 0.45])),
            stand(MathTex(r"\times 3", font_size=46, color=GOLD)).move_to(C + np.array([LX0 - 0.8, y2, 0.45])),
            stand(MathTex(r"\times(-2)", font_size=46, color=SKY)).move_to(C + np.array([LX0 - 1.0, y3, 0.45])),
        )
        self.say("Now weight the copies: minus one, three, and minus two.")
        self.play(w1.animate.set_value(-1.0), w2.animate.set_value(3.0), w3.animate.set_value(-2.0),
                  FadeIn(wl), run_time=2.8)
        self.wait(1.2)

        # the sum
        for c in (c1, c2, c3):
            c.clear_updaters()
        f_mix = MathTex("D(u)", "=", "-g(u)", "+", r"3\,g(u-\log 2)", "-", r"2\,g(u-\log 4)", font_size=46, color=IVORY)
        f_mix[2].set_color(CORAL)
        f_mix[4].set_color(GOLD)
        f_mix[6].set_color(SKY)
        self.hud(f_mix)
        mix = polyline(mix_points(y2), IVORY, width=4.0, halo=14.0, halo_op=0.2).shift(C)
        self.say("Add the three heights at every u. The sum D is the mix.")
        self.play(Transform(c1, mix.copy()), Transform(c3, mix.copy()), Transform(c2, mix),
                  FadeOut(br2), FadeOut(br3), FadeOut(wl),
                  lanes[0].animate.set_stroke(opacity=0.12), lanes[2].animate.set_stroke(opacity=0.12),
                  run_time=2.8)
        self.remove(c1, c3)
        self.move_camera(theta=-82 * DEGREES, zoom=0.95, run_time=3.2, rate_func=smooth)
        self.wait(0.6)
        self.headline("The transform of g has poles.\nDoes any pole survive the mix?", hold=2.0, font_size=64)
        self.st1 = VGroup(deck1, lanes, axis_u, lab_u, c2)
        self.gallery.append(self.st1)

    # ACT 2: a pole is one pure tone ------------------------------------ #
    def act_tone(self):
        C = P[1]
        deck2 = deck(C)
        mid = C + OUT * (HZ - 0.5)
        self.fly(mid, 72 * DEGREES, -42 * DEGREES, 0.95, run_time=3.4,
                 out=list(self.st1), into=[deck2])
        self.headline("A pole is one pure tone.")

        x0, x1 = HX0, HX0 + HXS * HU
        axis = Line(C + np.array([x0 - 0.3, 0, HZ]), C + np.array([x1 + 0.4, 0, HZ])).set_stroke(FOG, width=1.6, opacity=0.6)
        tone = polyline(helix_points(C, 0.0, 1.0), CORAL, width=3.2)
        self.say("A pure tone is a spiral along u. It turns, and it grows.")
        self.play(Create(axis), run_time=0.6)
        self.play(Create(tone), run_time=3.4, rate_func=linear)
        f_tone = MathTex(r"e^{\rho u}", r"\qquad", r"\rho", "=", r"\tfrac{1}{2}", "+", r"14.1347\,i", font_size=48, color=IVORY)
        f_tone[0].set_color(CORAL)
        self.hud(f_tone)
        self.say("This one is the tone of the first zero of the zeta function.", hold=1.2)

        us = np.linspace(0, HU, 420)
        sh = np.exp(RHO * us) * HA
        shadow = polyline(np.stack([HX0 + HXS * us, sh.real, np.zeros_like(us)], axis=1) + C,
                          CORAL, width=2.4, halo=7.0, halo_op=0.1)
        shadow.set_stroke(opacity=0.6)
        drops = VGroup(*[
            DashedLine(C + np.array([HX0 + HXS * u, (np.exp(RHO * u) * HA).real, HZ + (np.exp(RHO * u) * HA).imag]),
                       C + np.array([HX0 + HXS * u, (np.exp(RHO * u) * HA).real, 0]), dash_length=0.08)
            for u in np.linspace(0.6, HU, 7)
        ]).set_stroke(FOG, width=1, opacity=0.4)
        self.say("Its shadow on the floor is a growing wave.")
        self.move_camera(theta=-78 * DEGREES, phi=66 * DEGREES, run_time=3.0,
                         added_anims=[Create(shadow), FadeIn(drops)])
        self.say("The curve g is a chord of such waves, one for each pole.", hold=2.0)

        f_pole = MathTex(r"\int_0^\infty", r"e^{\rho u}", r"e^{-su}\,du", "=", r"\frac{1}{s-\rho}", font_size=48, color=IVORY)
        f_pole[1].set_color(CORAL)
        self.hud(f_pole)
        self.say("In the transform, this single tone is a pole at s = ρ.", hold=2.6)

        # delay the tone
        a = ValueTracker(0.0)
        copy = always_redraw(lambda: polyline(helix_points(C, a.get_value(), 1.0), GOLD, width=3.0))
        self.add(copy)
        self.say("Delay the tone by log 2. The spiral slides along its axis.")
        self.move_camera(theta=-40 * DEGREES, phi=72 * DEGREES, run_time=3.2,
                         added_anims=[a.animate.set_value(LOG2), FadeOut(shadow), FadeOut(drops),
                                      tone.animate.set_stroke(opacity=0.45)])
        copy.clear_updaters()
        f_shift = MathTex(r"e^{\rho(u-\log 2)}", "=", r"2^{-\rho}", r"\,e^{\rho u}", font_size=52, color=IVORY)
        f_shift[0].set_color(GOLD)
        f_shift[2].set_color(OLIVE_TXT)
        f_shift[3].set_color(CORAL)
        self.hud(f_shift)
        self.say("A slid spiral is the old spiral times one number, q.", hold=2.0)

        # face the phasor plane at u = U0
        A0 = C + np.array([HX0 + HXS * U0, 0, HZ])
        r0 = HA * np.exp(0.5 * U0)

        def tip(z):
            return A0 + np.array([0, z.real, z.imag]) * r0

        def face_x(mob, z, dz=0j):
            """Label in the phasor plane, readable from the +x side."""
            mob.rotate(PI / 2, axis=RIGHT).rotate(PI / 2, axis=OUT)
            return mob.move_to(tip(z + dz))

        ring = Circle(radius=r0).rotate(PI / 2, axis=UP).move_to(A0).set_stroke(FOG, width=1.5, opacity=0.6)
        v_old = Line(A0, tip(1)).set_stroke(CORAL, width=6)
        v_new = Line(A0, tip(Q_RHO)).set_stroke(GOLD, width=6)
        l_old = face_x(MathTex("1", font_size=22, color=CORAL), 1, 0.2 - 0.18j)
        l_new = face_x(MathTex("q", font_size=22, color=GOLD), Q_RHO, -0.12 + 0.2j)
        look = A0 + np.array([0, -0.62, 0.16])
        self.move_camera(phi=86 * DEGREES, theta=-7 * DEGREES, frame_center=look, zoom=3.0, run_time=3.6,
                         added_anims=[FadeIn(ring), Create(v_old), Create(v_new), FadeIn(l_old), FadeIn(l_new),
                                      FadeOut(deck2),
                                      tone.animate.set_stroke(opacity=0.10).set_stroke(opacity=0.0, background=True),
                                      copy.animate.set_stroke(opacity=0.10).set_stroke(opacity=0.0, background=True)])
        self.say("Along the axis: q turns the tone 159 degrees and shrinks it to 0.707.", hold=2.6)

        # the three weighted arrows, head to tail
        z1 = -1 + 0j
        z2 = z1 + 3 * Q_RHO
        z3 = z2 - 2 * Q_RHO ** 2
        s1 = Line(A0, tip(z1)).set_stroke(CORAL, width=7)
        s2 = Line(tip(z1), tip(z2)).set_stroke(GOLD, width=7)
        s3 = Line(tip(z2), tip(z3)).set_stroke(SKY, width=7)
        total = Line(A0, tip(z3)).set_stroke(IVORY, width=7)
        total.set_stroke(IVORY, width=20, opacity=0.2, background=True)
        end = bead(tip(z3), IVORY, radius=0.035)
        t1 = face_x(MathTex("-1", font_size=22, color=CORAL), z1 / 2, -0.22j)
        t2 = face_x(MathTex("3q", font_size=22, color=GOLD), (z1 + z2) / 2, -0.24j)
        t3 = face_x(MathTex("-2q^{2}", font_size=22, color=SKY), (z2 + z3) / 2, -0.78 - 0.14j)
        t4 = face_x(MathTex(r"m(\rho)", font_size=24, color=IVORY), z3 / 2, 0.12 + 0.34j)
        f_sum = MathTex("-1", "+", "3q", "-", "2q^{2}", "=", r"m(\rho)", font_size=52, color=IVORY)
        f_sum[0].set_color(CORAL)
        f_sum[2].set_color(GOLD)
        f_sum[4].set_color(SKY)
        self.hud(f_sum)
        self.say("Now the mix. Three arrows, head to tail.")
        self.play(FadeOut(v_new), FadeOut(l_new), FadeOut(l_old), ReplacementTransform(v_old, s1), FadeIn(t1), run_time=1.1)
        self.play(Create(s2), FadeIn(t2), run_time=1.2)
        self.play(Create(s3), FadeIn(t3), run_time=1.2)
        self.say("Minus one, then three q, then minus two q squared.", hold=1.6)
        self.say("They do not close up. The gap is the number m(ρ), 3.98 units long.")
        self.play(Create(total), FadeIn(end), FadeIn(t4), run_time=1.5)
        self.wait(2.2)

        # the mix returns the same tone, louder
        f_eig = MathTex(r"-e^{\rho u}", "+", r"3e^{\rho(u-\log 2)}", "-", r"2e^{\rho(u-\log 4)}", "=",
                        r"m(\rho)", r"\,e^{\rho u}", font_size=44, color=IVORY)
        f_eig[0].set_color(CORAL)
        f_eig[2].set_color(GOLD)
        f_eig[4].set_color(SKY)
        f_eig[7].set_color(CORAL)
        big = polyline(helix_points(C, 0.0, M_RHO), IVORY, width=3.2, halo=12.0, halo_op=0.18)
        self.hud(f_eig)
        self.move_camera(phi=70 * DEGREES, theta=-50 * DEGREES, frame_center=C + OUT * (HZ - 1.0) + RIGHT * 0.2, zoom=0.72,
                         run_time=3.4,
                         added_anims=[FadeOut(copy), FadeOut(ring), FadeIn(deck2), FadeOut(VGroup(t1, t2, t3, t4)),
                                      tone.animate.set_stroke(opacity=1.0).set_stroke(opacity=0.16, background=True)])
        self.say("So the mix gives back the same tone, 3.98 times larger.")
        self.play(Create(big), run_time=3.4, rate_func=linear)
        self.wait(1.2)
        self.say("A tone dies only if its own number m(ρ) is zero.", hold=2.4)
        self.st2 = VGroup(deck2, axis, tone, big, s1, s2, s3, total, end)
        self.gallery.append(self.st2)

    # ACT 3: the symbol and its two factors ----------------------------- #
    def act_symbol(self):
        C = P[2]
        deck3 = deck(C)
        tilt = 24 * DEGREES
        self.fly(C, tilt, -90 * DEGREES, 1.0, run_time=3.4, out=list(self.st2), into=[deck3])
        self.headline("A delay becomes\na multiplication.")

        f_m = MathTex("m(s)", "=", "-1", "+", r"3\cdot 2^{-s}", "-", r"2\cdot 4^{-s}", font_size=88, color=IVORY)
        f_m[2].set_color(CORAL)
        f_m[4].set_color(GOLD)
        f_m[6].set_color(SKY)
        f_m.move_to(C + UP * 1.55)
        self.say("On the transform side, the whole mix is multiplication by one function, m.")
        self.play(Write(f_m), run_time=2.2)
        self.wait(1.2)
        for ids, col, text in (
            ((2,), CORAL, "Copy one: no delay, weight minus one."),
            ((4,), GOLD, "Copy two: the delay log 2 becomes the factor 2 to the minus s."),
            ((6,), SKY, "Copy three: the delay log 4 becomes 4 to the minus s."),
        ):
            frame = self.zoom_part(f_m, ids, 2.3, text, color=col, hold=1.7)
            self.pull_back(f_m, frame, C, phi=tilt)

        f_q = MathTex("-1+3q-2q^{2}", "=", "(1-q)", "(2q-1)", font_size=78, color=IVORY)
        f_q[2].set_color(EMBER)
        f_q[3].set_color(EMBER)
        f_q.move_to(C + DOWN * 0.65)
        f_def = MathTex("q", "=", "2^{-s}", font_size=60, color=OLIVE_TXT).move_to(C + DOWN * 2.35)
        self.say("Write q for 2 to the minus s. The quadratic in q factors.")
        self.play(FadeIn(f_def, shift=UP * 0.1), run_time=0.8)
        self.play(TransformFromCopy(VGroup(f_m[2], f_m[3], f_m[4], f_m[5], f_m[6]), f_q[0]), run_time=1.6)
        self.play(Write(VGroup(f_q[1], f_q[2], f_q[3])), run_time=1.6)
        self.wait(1.0)
        frame = self.zoom_part(f_q, (2,), 2.4, "This factor is zero only when q is 1.", color=EMBER, hold=1.9)
        self.pull_back(f_q, frame, C, phi=tilt)
        frame = self.zoom_part(f_q, (3,), 2.4, "This factor is zero only when q is one half.", color=EMBER, hold=1.9)
        self.pull_back(f_q, frame, C, phi=tilt)
        self.say("The mix can kill a tone only when q is 1 or 1/2.", hold=2.4)
        self.st3 = VGroup(deck3, f_m, f_q, f_def)
        self.gallery.append(self.st3)

    # ACT 4: where q lives; the strip winds into a ribbon --------------- #
    def act_ribbon(self):
        C = P[3]
        deck4 = deck(C)
        AC = C + RIGHT * 2.9
        self.fly(C, 0, -90 * DEGREES, 1.0, run_time=3.0, out=list(self.st3), into=[deck4])
        self.headline("Where can q be?")

        outer = Circle(radius=QR).move_to(AC).set_stroke(OLIVE_TXT, width=3)
        inner = Circle(radius=QR / 2).move_to(AC).set_stroke(OLIVE_TXT, width=3)
        annulus = Annulus(inner_radius=QR / 2, outer_radius=QR).move_to(AC)
        annulus.set_fill(OLIVE, opacity=0.24).set_stroke(width=0)
        cross = VGroup(Line(AC + LEFT * (QR + 0.3), AC + RIGHT * (QR + 0.3)),
                       Line(AC + DOWN * (QR + 0.3), AC + UP * (QR + 0.3))).set_stroke(FOG, width=1, opacity=0.4)
        f_abs = MathTex("|q|", "=", r"2^{-\mathrm{Re}\,s}", font_size=60, color=IVORY).move_to(C + LEFT * 3.7 + UP * 2.2)
        f_abs[0].set_color(OLIVE_TXT)
        self.say("The size of q depends on one thing only: the real part of s.")
        self.play(Create(outer), Create(inner), FadeIn(cross), Write(f_abs), run_time=2.0)

        sig = ValueTracker(0.0)
        ring = always_redraw(lambda: Circle(radius=QR * 2.0 ** (-sig.get_value())).move_to(AC)
                             .set_stroke(GOLD, width=4).set_stroke(GOLD, width=12, opacity=0.2, background=True))
        read_l = MathTex(r"\mathrm{Re}\,s=", font_size=44, color=GOLD)
        read_n = DecimalNumber(0.0, num_decimal_places=2, font_size=44, color=GOLD)
        read_n.add_updater(lambda d: d.set_value(sig.get_value()))
        read = VGroup(read_l, read_n).arrange(RIGHT, buff=0.15).move_to(C + LEFT * 3.7 + UP * 0.95)
        read_n.add_updater(lambda d: d.next_to(read_l, RIGHT, buff=0.15))
        self.play(FadeIn(ring), FadeIn(read), run_time=0.6)
        self.say("As the real part goes from 0 to 1, the circle shrinks to 1/2.")
        self.play(sig.animate.set_value(1.0), run_time=3.2)
        self.play(sig.animate.set_value(0.5), FadeIn(annulus), run_time=1.6)
        ring.clear_updaters()
        read_n.clear_updaters()

        f_strip = MathTex(r"0<\mathrm{Re}\,s<1", r"\Longrightarrow", r"\tfrac{1}{2}", "<", "|q|", "<", "1",
                          font_size=50, color=IVORY)
        f_strip[4].set_color(OLIVE_TXT)
        f_strip[2].set_color(EMBER)
        f_strip[6].set_color(EMBER)
        if f_strip.width > 5.7:
            f_strip.scale_to_fit_width(5.7)
        f_strip.move_to(C + LEFT * 3.75 + DOWN * 0.6)
        self.say("Inside the critical strip, the real part is strictly between 0 and 1.")
        self.play(Write(f_strip), FadeOut(read), run_time=1.8)
        # THE BIG ZOOM
        frame = self.zoom_part(f_strip, (2, 3, 4, 5, 6), 3.0,
                               "So q is strictly between the two circles. It is never on them.",
                               color=OLIVE_TXT, hold=2.6, run_time=2.4)
        self.pull_back(f_strip, frame, C, run_time=1.8)

        k1 = glow_dot(AC + RIGHT * QR, EMBER, radius=0.11)
        k2 = glow_dot(AC + RIGHT * QR / 2, EMBER, radius=0.11)
        l1 = MathTex("q=1", font_size=40, color=EMBER).next_to(k1[1], UL, buff=0.2)
        l2 = MathTex(r"q=\tfrac{1}{2}", font_size=40, color=EMBER).next_to(k2[1], DL, buff=0.2)
        self.say("And the two kill points? They sit exactly on the circles.")
        self.play(FadeIn(k1, scale=2.5), FadeIn(k2, scale=2.5), FadeIn(l1), FadeIn(l2), run_time=1.2)
        self.play(Flash(k1[1], color=EMBER, flash_radius=0.35), Flash(k2[1], color=EMBER, flash_radius=0.35), run_time=1.0)
        self.wait(1.2)

        # tilt: height is Im s
        n_turn = 3
        th_max = n_turn * TAU

        def ribbon(lift):
            surf = Surface(lambda r, th: ribbon_point(AC, r, th, lift), u_range=[0.5, 1.0], v_range=[0, th_max],
                           resolution=(3, 28 * n_turn), fill_opacity=0.5, checkerboard_colors=False,
                           stroke_color=IVORY, stroke_width=0.5, stroke_opacity=0.35)
            for face in surf:
                rr = 0.5 * (face.u1 + face.u2)
                face.set_fill(interpolate_color(ManimColor(GOLD), ManimColor(OLIVE), (rr - 0.5) / 0.5), opacity=0.5)
            return surf

        def edge(rad, lift, color):
            ths = np.linspace(0, th_max, 360)
            return polyline([ribbon_point(AC, rad, th, lift) for th in ths], color, width=3.0)

        flat, rib = ribbon(0.0), ribbon(1.0)
        e_out, e_in = edge(1.0, 0.0, OLIVE_TXT), edge(0.5, 0.0, OLIVE_TXT)
        self.say(None, run_time=0.3)
        self.move_camera(phi=64 * DEGREES, theta=-56 * DEGREES, frame_center=AC + OUT * 1.9 + LEFT * 0.6, zoom=0.88,
                         run_time=3.2, added_anims=[FadeOut(f_abs), FadeOut(f_strip), FadeOut(ring),
                                                    FadeOut(l1), FadeOut(l2), FadeIn(flat)])
        self.remove(outer, inner)
        self.add(e_out, e_in)
        self.say("Let the imaginary part of s be height. The strip winds into a ribbon.")
        self.play(Transform(flat, rib), Transform(e_out, edge(1.0, 1.0, OLIVE_TXT)),
                  Transform(e_in, edge(0.5, 1.0, OLIVE_TXT)), run_time=4.0)
        H = n_turn * QH
        rod1 = Line(AC + RIGHT * QR, AC + RIGHT * QR + OUT * (H + 0.4))
        rod2 = Line(AC + RIGHT * QR / 2, AC + RIGHT * QR / 2 + OUT * (H + 0.4))
        for rod in (rod1, rod2):
            rod.set_stroke(EMBER, width=4).set_stroke(EMBER, width=14, opacity=0.22, background=True)
        hits = VGroup(*[bead(AC + RIGHT * rad + OUT * QH * k, EMBER, radius=0.07)
                        for rad in (QR, QR / 2) for k in range(n_turn + 1)])
        self.say("Each kill point becomes a rod. It meets the ribbon only at an edge.")
        self.play(Create(rod1), Create(rod2), run_time=1.8)
        self.play(FadeIn(hits, lag_ratio=0.1), run_time=1.2)
        self.begin_ambient_camera_rotation(rate=0.16)
        self.wait(4.6)
        f_turn = MathTex(r"\text{one turn}", "=", r"\frac{2\pi}{\log 2}", r"\approx", "9.06", font_size=46, color=IVORY)
        f_turn[2].set_color(OLIVE_TXT)
        f_turn[4].set_color(OLIVE_TXT)
        self.hud(f_turn)
        self.say("One turn of the ribbon is 9.06 units of height in the strip.")
        self.wait(2.6)
        self.stop_ambient_camera_rotation()

        th1 = GAMMA1 * LOG2
        p_rho = ribbon_point(AC, abs(Q_RHO), th1, 1.0)
        zero = bead(p_rho, IVORY, radius=0.12)
        ruler = Line(ribbon_point(AC, 0.5, th1, 1.0), ribbon_point(AC, 1.0, th1, 1.0)).set_stroke(IVORY, width=3)
        f_rho = MathTex(r"\rho=\tfrac{1}{2}+14.1347\,i", r"\qquad", r"|q|", "=", r"2^{-1/2}", r"\approx", "0.707",
                        font_size=44, color=IVORY)
        f_rho[2].set_color(OLIVE_TXT)
        self.hud(f_rho)
        self.say("The first zeta zero rides here, in the middle of the ribbon.")
        self.play(FadeIn(zero, scale=2.0), Create(ruler), run_time=1.4)
        self.move_camera(frame_center=p_rho, zoom=1.7, theta=self.camera.get_theta() + 50 * DEGREES, run_time=3.4)
        self.say("Every pole in the strip rides between the edges. No rod can reach it.", hold=2.8)
        self.st4 = VGroup(deck4, annulus, cross, flat, e_out, e_in, rod1, rod2, hits, zero, ruler, k1, k2)
        self.gallery.append(self.st4)

    # ACT 5: how much of the tone gets through -------------------------- #
    def act_landscape(self):
        C = P[4]
        deck5 = deck(C)
        self.fly(C + OUT * 0.7 + DOWN * 0.4, 62 * DEGREES, -128 * DEGREES, 0.86, run_time=3.6,
                 out=list(self.st4), into=[deck5])
        self.headline("How much of the tone\ngets through?")

        def land(scale):
            surf = Surface(
                lambda sg, t: strip_xy(C, sg, t) + OUT * scale * ZS * abs(complex(m_of(complex(sg, t)))),
                u_range=[0.0, 1.0], v_range=[T_LO, T_HI], resolution=(6, 60), fill_opacity=0.9,
                checkerboard_colors=False, stroke_color=INK, stroke_width=0.6, stroke_opacity=0.5)
            for face in surf:
                v = abs(complex(m_of(complex(0.5 * (face.u1 + face.u2), 0.5 * (face.v1 + face.v2)))))
                face.set_fill(height_color(v), opacity=0.9)
            return surf

        walls = VGroup(*[Line(strip_xy(C, sg, T_LO), strip_xy(C, sg, T_HI)) for sg in (0.0, 1.0)])
        walls.set_stroke(OLIVE_TXT, width=3)
        w_lab = VGroup(
            stand(MathTex(r"\mathrm{Re}\,s=0", font_size=38, color=OLIVE_TXT)).move_to(strip_xy(C, 0.0, T_HI) + np.array([-1.0, 0.0, 0.3])),
            stand(MathTex(r"\mathrm{Re}\,s=1", font_size=38, color=OLIVE_TXT)).move_to(strip_xy(C, 1.0, T_LO) + np.array([1.35, 0.1, 0.3])),
        )
        t_axis = Arrow(strip_xy(C, 1.0, T_LO) + RIGHT * 0.5, strip_xy(C, 1.0, T_HI) + RIGHT * 0.5, buff=0,
                       stroke_width=2, max_tip_length_to_length_ratio=0.03).set_color(FOG)
        t_lab = stand(MathTex(r"\mathrm{Im}\,s", font_size=38, color=FOG)).move_to(strip_xy(C, 1.0, T_HI) + np.array([1.2, 0, 0.3]))
        flat, surf = land(0.0), land(1.0)
        self.say("This floor is the strip. Its walls are real part 0 and 1.")
        self.play(Create(walls), FadeIn(w_lab), FadeIn(t_axis), FadeIn(t_lab), FadeIn(flat), run_time=1.8)
        self.wait(1.0)
        f_h = MathTex(r"\text{height}", "=", "|m(s)|", font_size=48, color=IVORY)
        self.hud(f_h)
        self.say("Raise each point to the height |m(s)|: how much of that tone passes.")
        self.play(Transform(flat, surf), run_time=3.6)
        self.move_camera(theta=-70 * DEGREES, run_time=4.4, rate_func=smooth)

        zeros = VGroup(*[glow_dot(strip_xy(C, sg, k * PERIOD), EMBER, radius=0.10)
                         for sg in (0.0, 1.0) for k in range(3)])
        self.say("It touches the floor only on the walls, once every 9.06.")
        self.play(FadeIn(zeros, lag_ratio=0.12, scale=2.0), run_time=1.6)
        self.wait(1.6)

        # the floor function, as an inset graph
        f_floor = MathTex("|m(s)|", r"\ge", r"(1-2^{-\sigma})", r"(2^{1-\sigma}-1)", ">", "0", font_size=46, color=IVORY)
        f_floor[2].set_color(EMBER)
        f_floor[3].set_color(EMBER)
        self.hud(f_floor)
        ax = Axes(x_range=[0, 1, 0.5], y_range=[0, 0.15, 0.05], x_length=3.6, y_length=1.8,
                  axis_config={"color": FOG, "stroke_width": 1.5, "include_tip": False})
        curve = ax.plot(floor_of, x_range=[0, 1], color=EMBER, stroke_width=3)
        mark = Dot(ax.c2p(0.5, floor_of(0.5)), radius=0.06, color=IVORY)
        note = MathTex(r"\sigma=\tfrac{1}{2}:\ 0.121", font_size=30, color=IVORY).next_to(mark, UP, buff=0.12)
        xl = MathTex(r"\sigma", font_size=30, color=FOG).next_to(ax, RIGHT, buff=0.1).shift(DOWN * 0.7)
        plate = RoundedRectangle(corner_radius=0.15, width=4.8, height=3.0).set_stroke(GOLD, width=1, opacity=0.4)
        plate.set_fill(INK, opacity=0.92)
        inset = VGroup(plate, ax, curve, mark, note, xl)
        plate.move_to(VGroup(ax, note, xl))
        inset.to_corner(UR, buff=0.4).shift(DOWN * 1.35)
        self.add_fixed_in_frame_mobjects(inset)
        self.say("Inside, the valleys are low but never zero. Their height has a positive floor.")
        self.play(FadeIn(inset), run_time=1.0)
        self.wait(2.8)

        p0 = strip_xy(C, 0.5, GAMMA1)
        top = p0 + OUT * ZS * abs(M_RHO)
        pillar = Line(p0, top + OUT * 0.9).set_stroke(IVORY, width=4)
        pillar.set_stroke(IVORY, width=16, opacity=0.22, background=True)
        cap = bead(top, IVORY, radius=0.11)
        f_at = MathTex(r"|m(\rho)|", "=", "3.984", r"\qquad", r"\rho=\tfrac{1}{2}+14.1347\,i", font_size=46, color=IVORY)
        f_at[2].set_color(GOLD)
        self.play(FadeOut(inset), run_time=0.5)
        self.remove_fixed_in_frame_mobjects(inset)
        self.remove(inset)
        self.hud(f_at)
        self.say("The first zeta zero stands on a ridge. Its tone passes 3.98 times larger.")
        self.play(Create(pillar), FadeIn(cap, scale=2.0), run_time=1.6)
        self.move_camera(theta=-104 * DEGREES, phi=58 * DEGREES, zoom=1.15, frame_center=p0 + OUT * 0.9,
                         run_time=3.6)
        self.wait(1.0)

        # top-down: the residue formula on the floor
        f_res = MathTex(r"\frac{r}{s-\rho}", r"\longmapsto", r"\frac{m(\rho)\,r}{s-\rho}", font_size=56, color=IVORY)
        if f_res.width > 4.2:
            f_res.scale_to_fit_width(4.2)
        f_res.move_to(C + LEFT * 4.6 + UP * 1.25)
        self.say(None, run_time=0.3)
        self.hud(None, run_time=0.3)
        self.move_camera(phi=0, theta=-90 * DEGREES, frame_center=C + LEFT * 1.4, zoom=1.0, run_time=3.4,
                         added_anims=[FadeOut(w_lab), FadeOut(t_lab), FadeIn(f_res)])
        self.say("Near a pole the transform is r over s minus ρ, plus smooth terms.")
        self.wait(2.2)
        frame = self.zoom_part(f_res, (2,), 2.5, "The pole stays. Its residue becomes m(ρ) times r, and m(ρ) is not zero.",
                               color=GOLD, hold=3.0, run_time=2.0)
        self.pull_back(f_res, frame, C + LEFT * 1.4)
        self.st5 = VGroup(deck5, walls, t_axis, flat, zeros, pillar, cap, f_res)

    # ACT 6: the whole journey in one frame ----------------------------- #
    def act_gallery(self):
        self.headline("The mix is blind\nonly on the walls.", hold=1.8)
        back = [m for group in self.gallery for m in group]
        self.move_camera(phi=56 * DEGREES, theta=-90 * DEGREES, frame_center=P[2] + DOWN * 11.0, zoom=0.152,
                         run_time=5.0, added_anims=[FadeIn(m) for m in back])
        l_a = Tex(r"$s=0$\ \ (constants):\quad removed", font_size=40, color=IVORY)
        l_b = Tex(r"$s=1$\ \ (the growth $e^{u}$):\quad removed", font_size=40, color=IVORY)
        l_c = Tex(r"$0<\mathrm{Re}\,s<1$:\quad every pole survives", font_size=40, color=GOLD)
        lines = VGroup(l_a, l_b, l_c).arrange(DOWN, buff=0.3, aligned_edge=LEFT)
        credit = Text("Lean-checked: compactDifference_poleData, L. Crossley (2026).\n"
                      "One step of a window criterion. Not a proof of the Riemann hypothesis.",
                      font=CAP_FONT, slant=ITALIC, font_size=22, color=FOG, line_spacing=0.9)
        card = VGroup(lines, credit).arrange(DOWN, buff=0.5)
        plate = RoundedRectangle(corner_radius=0.22, width=card.width + 1.1, height=card.height + 0.9)
        plate.set_stroke(GOLD, width=1.2, opacity=0.45).set_fill(INK, opacity=0.8)
        end = VGroup(plate, card).move_to(DOWN * 1.75)
        self.add_fixed_in_frame_mobjects(end)
        self.play(FadeIn(end, shift=UP * 0.15), run_time=1.2)
        self.begin_ambient_camera_rotation(rate=0.02)
        self.wait(6.0)
        self.stop_ambient_camera_rotation()
        fade = Rectangle(width=16.5, height=9.6).set_stroke(width=0).set_fill(INK, opacity=1.0)
        self.add_fixed_in_frame_mobjects(fade)
        self.play(FadeIn(fade), run_time=1.6)
        self.wait(0.4)
