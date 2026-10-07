from manim import *
import numpy as np
import math

config.renderer = "cairo"
config.background_color = "#F3EFE6"
config.frame_rate = 60
config.pixel_width = 1920
config.pixel_height = 1080

BONE = ManimColor("#F3EFE6")
INK = ManimColor("#202A35")
TEAL = ManimColor("#176B72")
CORAL = ManimColor("#C76F51")
GOLD = ManimColor("#AD8542")
ZERO_T = np.array([14.134725141734693, 21.022039638771555,
                   25.01085758014569, 30.424876125859513])


def zeta_em(s):
    # Analytic continuation by Euler--Maclaurin; never called by an updater.
    s = np.asarray(s, dtype=np.complex128)
    nlog = math.log(64.0)
    value = np.zeros_like(s)
    for n in range(1, 64):
        value += np.exp(-s * math.log(n))
    value += np.exp((1.0-s)*nlog)/(s-1.0) + 0.5*np.exp(-s*nlog)
    bernoulli = (1/6, -1/30, 1/42, -1/30, 5/66,
                 -691/2730, 7/6, -3617/510)
    rising = s.copy()
    for k, b in enumerate(bernoulli, start=1):
        if k > 1:
            rising = rising*(s+2*k-3)*(s+2*k-2)
        value += (b/math.factorial(2*k))*rising*np.exp((1-s-2*k)*nlog)
    return value


def bilinear(x, y, xs, ys, values):
    i = int(np.clip(np.searchsorted(xs, x)-1, 0, len(xs)-2))
    j = int(np.clip(np.searchsorted(ys, y)-1, 0, len(ys)-2))
    a = float(np.clip((x-xs[i])/(xs[i+1]-xs[i]), 0, 1))
    b = float(np.clip((y-ys[j])/(ys[j+1]-ys[j]), 0, 1))
    return float((1-a)*(1-b)*values[i, j] + a*(1-b)*values[i+1, j]
                 + (1-a)*b*values[i, j+1] + a*b*values[i+1, j+1])


def polyline(points, color=TEAL, width=2, opacity=1):
    mob = VMobject()
    mob.set_points_as_corners(np.array(points))
    mob.set_fill(opacity=0)
    mob.set_stroke(color, width=width, opacity=opacity)
    return mob


def bead(point, color=INK, radius=0.075, resolution=(6, 8)):
    return Dot3D(point=np.array(point), radius=radius, color=color,
                 resolution=resolution)


def panel(corners, color=TEAL, opacity=0.12, width=0.8):
    return Polygon(*[np.array(p) for p in corners], color=color,
                   fill_color=color, fill_opacity=opacity,
                   stroke_width=width, shade_in_3d=True)


def skin(func, u_range, v_range, color=TEAL, opacity=0.9,
         resolution=(32, 16), mesh_width=0.35):
    return Surface(func, u_range=u_range, v_range=v_range,
                   resolution=resolution, checkerboard_colors=False,
                   fill_color=color, fill_opacity=opacity,
                   stroke_color=interpolate_color(color, BONE, 0.6),
                   stroke_width=mesh_width, shade_in_3d=True)


def height_color(surface, low, high, color=TEAL):
    for face in surface:
        a = float(np.clip((face.get_center()[2]-low)/(high-low), 0, 1))
        face.set_fill(interpolate_color(color, BONE, 0.10+0.63*a), opacity=0.96)
    return surface


class AstraFilm(ThreeDScene):
    def refresh_cairo_translation(self):
        # CE 0.19 caches a Cairo matrix containing the old frame-center offset.
        # Invalidate that drawing cache when panning; no geometry is rebuilt.
        center = self.camera.frame_center
        if self._cairo_center is None or not np.array_equal(center, self._cairo_center):
            self.camera.pixel_array_to_cairo_context.clear()
            self._cairo_center = center.copy()

    def screen_anchor(self, mob, position):
        # Fixed-in-frame points still pass through Cairo's frame translation.
        base = np.array(position, dtype=float)
        def follow(m, base=base):
            self.refresh_cairo_translation()
            m.move_to(base+self.camera.frame_center)
        mob.add_updater(follow)
        mob.update(0)
        return mob

    def overlay(self, formula=None, lines=(), title=None, color=INK, size=40):
        group = VGroup()
        if title:
            main = Text(title, font="DejaVu Sans", font_size=41,
                        color=INK, weight="MEDIUM")
        elif formula:
            main = MathTex(formula, font_size=size, color=color)
        else:
            main = None
        if main is not None:
            if main.width > 12.9:
                main.scale_to_fit_width(12.9)
            if main.height > 1.22:
                main.scale_to_fit_height(1.22)
            self.screen_anchor(main, [0, 3.23, 0])
            group.add(main)
        for j, line in enumerate(lines):
            text = Text(line, font="DejaVu Sans", font_size=30, color=INK)
            if text.width > 13.0:
                text.scale_to_fit_width(13.0)
            self.screen_anchor(text, [0, -3.13-0.48*j, 0])
            group.add(text)
        group.set_z_index(1100)
        return group

    def beat(self, seconds, formula=None, lines=(), title=None,
             color=INK, size=40, camera=None, anims=()):
        # Each beat includes 0.6 s of nonoverlapping caption replacement.
        next_hud = self.overlay(formula, lines, title, color, size)
        if self.hud is None:
            self.wait(0.25)
        else:
            old = self.hud
            self.play(FadeOut(old, suspend_mobject_updating=False), run_time=0.25)
            self.remove_fixed_in_frame_mobjects(old)
            self.remove(old)
        self.add_fixed_in_frame_mobjects(next_hud)
        self.play(FadeIn(next_hud, suspend_mobject_updating=False), run_time=0.35)
        self.hud = next_hud
        remaining = seconds-0.6
        if camera is not None:
            self.move_camera(**camera, added_anims=list(anims),
                             run_time=remaining, rate_func=smooth)
        elif anims:
            self.play(*anims, run_time=remaining, rate_func=smooth)
        else:
            self.wait(remaining)
        self.film_seconds += seconds

    def pose(self, phi, theta, zoom, center=(0, 0, 0)):
        return dict(phi=phi*DEGREES, theta=theta*DEGREES,
                    zoom=zoom, frame_center=np.array(center, dtype=float))

    def world_labels(self, specs):
        # Small projected callouts stay inside the uncovered world band.
        # Leaders retain their geometric anchors during close camera pans.
        labels = VGroup()
        for spec in specs:
            tex, point, color = spec[:3]
            nominal = np.array(point, dtype=float)
            anchor = np.array(spec[3] if len(spec) > 3 else point, dtype=float)
            label = MathTex(tex, font_size=26, color=color)
            if label.width > 1.85:
                label.scale_to_fit_width(1.85)
            if label.height > 0.48:
                label.scale_to_fit_height(0.48)
            label.set_stroke(BONE, width=3, opacity=1, background=True)
            label.set_z_index(900)
            hw, hh = label.width/2, label.height/2
            leader = polyline([ORIGIN, 0.001*RIGHT], color, 0.9, 0.6)
            leader.set_z_index(850)

            def placement(nominal=nominal, anchor=anchor, hw=hw, hh=hh):
                # Refresh from the current trackers before the render capture.
                self.camera.reset_rotation_matrix()
                center = self.camera.frame_center
                projected = self.camera.project_points(np.array([anchor, nominal]))
                screen = projected[1]-center
                x_limit = config.frame_width/2-0.30-hw
                safe = np.array([
                    np.clip(screen[0], -x_limit, x_limit),
                    np.clip(screen[1], -2.40+hh, 2.36-hh),
                    0.0])
                target = safe+center
                start = np.array([projected[0, 0], projected[0, 1], center[2]])
                return start, target

            label.add_updater(lambda m, place=placement: m.move_to(place()[1]))

            def update_leader(m, place=placement, hw=hw, hh=hh):
                start, target = place()
                delta = target-start
                box_distance = max(abs(delta[0])/(hw+0.08),
                                   abs(delta[1])/(hh+0.08))
                end = target-delta/box_distance if box_distance > 1 else start
                m.set_points_as_corners([start, end])

            leader.add_updater(update_leader)
            label.update(0)
            leader.update(0)
            labels.add(VGroup(leader, label))
        self.camera.add_fixed_in_frame_mobjects(labels)
        return labels

    def forget_labels(self, labels):
        self.camera.remove_fixed_in_frame_mobjects(labels)

    def landscape(self, close=False):
        if close:
            xs = np.unique(np.r_[np.linspace(0.0, 1.2, 49), 0.5])
            ys = np.unique(np.r_[np.linspace(12.65, 15.65, 73), ZERO_T[0]])
            xs_draw = np.linspace(0, 1.2, 33)
            ys_draw = np.linspace(12.65, 15.65, 25)
            xs_draw[np.argmin(abs(xs_draw-0.5))] = 0.5
            ys_draw[np.argmin(abs(ys_draw-ZERO_T[0]))] = ZERO_T[0]
            def embedding(sigma, t, h):
                return np.array([8*(sigma-0.5), 2.7*(t-ZERO_T[0]), 2*h-1.6])
            ranges = [(0, 24)]
        else:
            xs = np.unique(np.r_[np.linspace(0, 1.2, 33),
                                  0.125, 0.5, 0.875, 11/12, 1.0])
            ys = np.unique(np.r_[np.linspace(12, 32, 97), ZERO_T])
            xs_draw = np.linspace(0, 1.2, 33)
            ys_draw = np.linspace(12, 32, 33)
            for a in [0.125, 0.5, 0.875, 11/12, 1.0]:
                xs_draw[np.argmin(abs(xs_draw-a))] = a
            for t in ZERO_T:
                ys_draw[np.argmin(abs(ys_draw-t))] = t
            def embedding(sigma, t, h):
                return np.array([8*(sigma-0.6), 0.45*(t-22), 2*h-1.6])
            ranges = [(0, 16), (16, 32)]
        heights = np.log1p(np.abs(zeta_em(xs[:, None]+1j*ys[None, :])))
        def graph(sigma, t):
            return embedding(sigma, t, bilinear(sigma, t, xs, ys, heights))
        def sampled(u, v):
            sigma = float(np.interp(u, np.arange(len(xs_draw)), xs_draw))
            t = float(np.interp(v, np.arange(len(ys_draw)), ys_draw))
            return graph(sigma, t)
        surfaces = VGroup()
        for start, end in ranges:
            surf = skin(sampled, [0, 32], [start, end],
                        resolution=(32, end-start))
            surfaces.add(height_color(surf, -1.6, 2.25))
        mesh = VGroup()
        for sigma in [0, 0.125, 0.5, 0.875, 1.2]:
            mesh.add(polyline([graph(sigma, t)+0.012*OUT for t in ys],
                              GOLD if sigma == 0.5 else TEAL,
                              2.5 if sigma == 0.5 else 0.9, 0.9))
        for t in (ZERO_T[:1] if close else ZERO_T):
            mesh.add(polyline([graph(sigma, t)+0.015*OUT for sigma in xs],
                              TEAL, 1.4, 0.85))
        return VGroup(surfaces, mesh), graph

    def strip_point(self, sigma, t, z=-1.6):
        return np.array([8*(sigma-0.6), 0.45*(t-22), z])

    def curtain(self, sigma, color=CORAL, opacity=0.13):
        x = 8*(sigma-0.6)
        surface = skin(lambda u, v: np.array([x, u, v]),
                       [-4.5, 4.5], [-1.6, 2.35],
                       color, opacity, (16, 3), 0.3)
        edges = VGroup(
            Line([x, -4.5, -1.6], [x, 4.5, -1.6], color=color, stroke_width=2.4),
            Line([x, -4.5, 2.35], [x, 4.5, 2.35], color=color, stroke_width=1.5),
            Line([x, -4.5, -1.6], [x, -4.5, 2.35], color=color, stroke_width=2),
            Line([x, 4.5, -1.6], [x, 4.5, 2.35], color=color, stroke_width=1.4))
        return VGroup(surface, edges)

    def critical_strip(self):
        p = self.strip_point
        floor = panel([p(0, 12, -1.64), p(1.2, 12, -1.64),
                       p(1.2, 32, -1.64), p(0, 32, -1.64)], TEAL, 0.055)
        grid = VGroup()
        for sigma in [0, 0.125, 0.25, 0.5, 0.75, 0.875, 1.0, 1.2]:
            grid.add(Line(p(sigma, 12), p(sigma, 32),
                          color=TEAL, stroke_width=0.7, stroke_opacity=0.25))
        for t in [12, 16, 20, 24, 28, 32]:
            grid.add(Line(p(0, t), p(1.2, t), color=TEAL,
                          stroke_width=0.7, stroke_opacity=0.23))
        side0 = self.curtain(0, TEAL, 0.035)
        side1 = self.curtain(1, TEAL, 0.035)
        spine = Line(p(0.5, 12), p(0.5, 32), color=GOLD, stroke_width=4)
        zeros = VGroup(*[bead(p(0.5, t), INK, 0.095) for t in ZERO_T])
        rings = VGroup(*[
            polyline([p(0.5, t)+np.array([0.15*math.cos(a),
                       0.15*math.sin(a), 0.01]) for a in np.linspace(0, TAU, 49)],
                     GOLD, 1.5) for t in ZERO_T])
        labels = self.world_labels([
            (r"0", p(0, 15, 0.3), INK, p(0, 15)),
            (r"\tfrac12", p(0.5, 14.8, 0.3), GOLD, p(0.5, 14.8)),
            (r"1", p(1, 15, 0.3), INK, p(1, 15)),
            (r"\sigma", p(1.2, 18.2, 0.3), INK, p(1.2, 18.2)),
            (r"t", p(-0.06, 30, -0.8), INK, p(-0.06, 30))])
        core = VGroup(floor, grid, side0, side1, spine, zeros, rings, labels)
        middle = panel([p(0.125, 12, -1.62), p(0.875, 12, -1.62),
                        p(0.875, 32, -1.62), p(0.125, 32, -1.62)], GOLD, 0.12)
        return core, middle, labels

    def prime_ribs(self):
        ribs, floors, specs = VGroup(), VGroup(), []
        ts = np.linspace(-4, 4, 129)
        for j, prime in enumerate([2, 3, 5]):
            x = 3.2*(j-1)
            hs = np.log1p(np.abs(1/(1-np.exp(-(1.25+1j*ts)*math.log(prime)))))
            points = np.array([[x, 0.85*t, 3.2*h-2.35] for t, h in zip(ts, hs)])
            rib = polyline(points, [TEAL, CORAL, GOLD][j], 3.8)
            sheet = skin(lambda u, v, xx=x, hh=hs:
                         np.array([xx+0.38*v, 0.85*u,
                                   -2.35+3.2*float(np.interp(u, ts, hh))]),
                         [-4, 4], [-1, 1], [TEAL, CORAL, GOLD][j],
                         0.55, (32, 2), 0.3)
            ribs.add(VGroup(sheet, rib))
            floors.add(polyline([[x, 0.85*t, -1.6] for t in ts],
                                [TEAL, CORAL, GOLD][j], 2))
            specs.append(("p="+str(prime), [x, -3.0, -0.4],
                          [TEAL, CORAL, GOLD][j], points[0]))
        labels = self.world_labels(specs)
        return ribs, floors, labels

    def winding_world(self):
        rho = 0.5+1j*ZERO_T[0]
        angles = np.linspace(0, TAU, 513)
        q = 0.1*np.exp(1j*angles)
        w = zeta_em(rho+q)
        if float(np.max(np.abs(zeta_em(0.5+1j*ZERO_T)))) > 1e-10:
            raise ValueError("Zeta zero residual check failed")
        winding = float(np.sum(np.angle(w[1:]/w[:-1]))/TAU)
        if abs(winding-1) > 1e-8:
            raise ValueError("Zeta image winding check failed")
        origins = [np.array([-3.0, 0, -0.25]), np.array([3.0, 0, -0.25])]
        bases = []
        plates = VGroup()
        for j, a in enumerate([-12*DEGREES, 12*DEGREES]):
            e, f = np.array([math.cos(a), 0, math.sin(a)]), UP.copy()
            bases.append((e, f))
            o = origins[j]
            plates.add(panel([o-2.1*e-2.1*f, o+2.1*e-2.1*f,
                              o+2.1*e+2.1*f, o-2.1*e+2.1*f], TEAL, 0.07))
            for b in [-1, 0, 1]:
                plates.add(Line(o-2*e+b*f, o+2*e+b*f,
                                color=TEAL, stroke_width=0.7, stroke_opacity=0.35))
                plates.add(Line(o+b*e-2*f, o+b*e+2*f,
                                color=TEAL, stroke_width=0.7, stroke_opacity=0.35))
            plates.add(bead(o, INK, 0.055))
        def embed(values, j, scale):
            e, f = bases[j]
            return origins[j]+scale*(values.real[:, None]*e+values.imag[:, None]*f)
        input_points, image_points = embed(q, 0, 16), embed(w, 1, 20)
        loops = VGroup(polyline(input_points, TEAL, 3.7),
                       polyline(image_points, CORAL, 3.7))
        labels = self.world_labels([
            (r"s-\rho", origins[0]+np.array([0, -2.48, 0]), TEAL),
            (r"w=\zeta(s)", origins[1]+np.array([0, -2.48, 0]), CORAL),
            (r"0", origins[1]+np.array([0.3, -0.3, 0]), INK)])
        tracker = ValueTracker(0)
        def along(points):
            phase = float(np.clip(tracker.get_value(), 0, 1))*512
            k = min(int(phase), 511)
            fraction = phase-k
            return (1-fraction)*points[k]+fraction*points[k+1]
        a = bead(input_points[0], TEAL, 0.105)
        b = bead(image_points[0], CORAL, 0.105)
        a.add_updater(lambda m: m.move_to(along(input_points)))
        b.add_updater(lambda m: m.move_to(along(image_points)))
        link = Line(input_points[0], image_points[0], color=GOLD,
                    stroke_width=1.3, stroke_opacity=0.55)
        link.add_updater(lambda m: m.put_start_and_end_on(
            along(input_points), along(image_points)))
        mobile = VGroup(link, a, b)
        derivative = (zeta_em(rho+1e-5)-zeta_em(rho-1e-5))/(2e-5)
        model = polyline(embed(derivative*q, 1, 20), GOLD, 1.5, 0.85)
        return VGroup(plates, loops, labels, mobile), tracker, mobile, model, labels

    def reciprocal(self):
        radii = np.r_[0, 0.007, 0.014, 0.025, np.linspace(0.04, 0.26, 18)]
        angles = np.linspace(0, TAU, 65)
        values = zeta_em(0.5+1j*ZERO_T[0]+radii[:, None]*np.exp(1j*angles[None, :]))
        inverse = 1/np.maximum(np.abs(values), 1e-14)
        heights = np.log1p(np.minimum(80, inverse))
        def pole(u, v):
            r = float(np.interp(u, np.arange(len(radii)), radii))
            q = bilinear(r, v, radii, angles, heights)
            return np.array([10*r*math.cos(v), 10*r*math.sin(v), -1.6+0.8*q])
        surf = skin(pole, [0, len(radii)-1], [0, TAU], CORAL, 0.9, (24, 32))
        for face in surf:
            a = float(np.clip((face.get_center()[2]+0.2)/2.3, 0, 1))
            face.set_fill(interpolate_color(BONE, CORAL, 0.3+0.65*a), opacity=0.93)
        mesh = VGroup()
        for angle in np.linspace(0, TAU, 13)[:-1]:
            mesh.add(polyline([pole(u, angle) for u in np.linspace(0, len(radii)-1, 65)],
                              CORAL, 1.15))
        return VGroup(surf, mesh)

    def eisenstein(self):
        locations = {}
        for m in range(-5, 6):
            for n in range(-5, 6):
                norm = m*m-m*n+n*n
                if norm <= 25:
                    locations[(m, n)] = np.array([m-n/2, math.sqrt(3)*n/2,
                                                  0.08*norm-1.5])
        edges, beads = VGroup(), VGroup()
        for (m, n), point in locations.items():
            for dm, dn in [(1, 0), (0, 1), (1, 1)]:
                if (m+dm, n+dn) in locations:
                    edges.add(Line(point, locations[(m+dm, n+dn)],
                                   color=TEAL, stroke_width=1.05, stroke_opacity=0.5))
            beads.add(bead(point, TEAL, 0.047, (3, 6)))
        unit = polyline([locations[k]+0.025*OUT for k in [(0, 0), (1, 0), (1, 1), (0, 0)]],
                        GOLD, 4)
        return VGroup(edges, beads, unit)

    def arithmetic_map(self):
        def reflected(u, v):
            return np.array([-4.7*u, 1.65*v*(0.2+0.8*u),
                             -0.45+1.55*math.sin(PI*u)+0.22*v*v])
        def transformed(u, v):
            return np.array([4.7*u, 1.65*v*(0.2+0.8*u),
                             -0.45+1.20*math.sin(PI*u)-0.22*v*v])
        reflection = skin(reflected, [0, 1], [-1, 1], TEAL, 0.85)
        poisson = skin(transformed, [0, 1], [-1, 1], TEAL, 0.38)
        rows = VGroup()
        for j in [-2, -1, 1, 2]:
            rows.add(skin(lambda u, v, j=j: np.array([
                4.7*u, j*(0.15+0.85*u)+0.11*v,
                -0.36+1.15*math.sin(PI*u)+0.07*j]),
                [0, 1], [-1, 1], TEAL, 0.65, (24, 2), 0.35))
        signal = skin(lambda u, v: np.array([
            4.7*u, 0.20*v, -0.29+1.15*math.sin(PI*u)]),
            [0, 1], [-1, 1], GOLD, 0.96, (32, 3), 0.3)
        seams = VGroup(
            polyline([reflected(u, 0)+0.025*OUT for u in np.linspace(0, 1, 100)],
                     TEAL, 3),
            bead([0, 0, -0.4], GOLD, 0.13))
        return reflection, poisson, rows, signal, seams

    def proof_geometry(self):
        floor = panel([[-5.2, -3.1, -1.6], [5.2, -3.1, -1.6],
                       [5.2, 3.1, -1.6], [-5.2, 3.1, -1.6]], TEAL, 0.06)
        # Horizontal distances are a conditional schematic, not numeric proof data.
        sigma_x, beta_x, edge_x = -4.0, 1.7, 0.4
        sigma_wall = panel([[sigma_x, -3, -1.6], [sigma_x, 3, -1.6],
                            [sigma_x, 3, 1.55], [sigma_x, -3, 1.55]], CORAL, 0.06)
        supremum = VGroup()
        for y in np.linspace(-3, 3, 9):
            supremum.add(DashedLine([beta_x, y, -1.6], [beta_x, y, 1.6],
                                    dash_length=0.13, color=INK, stroke_width=1.1))
        supremum.add(DashedLine([beta_x, -3, 1.6], [beta_x, 3, 1.6],
                                dash_length=0.15, color=INK, stroke_width=1.6))
        labels = self.world_labels([
            (r"\sigma_0=\tfrac78", [sigma_x, -1.3, -0.3], CORAL,
             [sigma_x, -1.3, -1.6]),
            (r"\beta_*", [beta_x, 1.2, 0.5], INK, [beta_x, 1.2, 1.6]),
            (r"1", [4.0, -1.3, -0.3], INK, [4.0, -1.3, -1.55])])
        def region(left):
            bottom = panel([[left, -3, -1.55], [5.15, -3, -1.55],
                            [5.15, 3, -1.55], [left, 3, -1.55]], TEAL, 0.16)
            roof = panel([[left, -3, 1.55], [5.15, -3, 1.55],
                          [5.15, 3, 1.55], [left, 3, 1.55]], TEAL, 0.045)
            front = panel([[left, -3, -1.55], [left, 3, -1.55],
                           [left, 3, 1.55], [left, -3, 1.55]], TEAL, 0.12)
            edge = Line([left, -3, -1.55], [left, 3, -1.55],
                        color=TEAL, stroke_width=3)
            return VGroup(bottom, roof, front, edge)
        old_region, new_region = region(4.0), region(edge_x)
        low = skin(lambda u, v: np.array([-3.6+3.7*u, -1.05+0.40*v, 0.12]),
                   [0, 1], [-1, 1], TEAL, 0.8, (16, 2))
        high = skin(lambda u, v: np.array([-3.6+3.7*u, 1.05+0.40*v, 0.72]),
                    [0, 1], [-1, 1], CORAL, 0.75, (16, 2))
        ceiling = polyline([[-3.6, 0, 1.4], [0.1, 0, 1.4]], GOLD, 2.7)
        common = skin(lambda u, v: np.array([-3.6+3.7*u, 0.28*v, 0.72]),
                      [0, 1], [-1, 1], GOLD, 0.88, (16, 2))
        gap = VGroup(*[Line([x, 0, 0.72], [x, 0, 1.4],
                            color=GOLD, stroke_width=2.3) for x in [-3.6, 0.1]])
        new_label = self.world_labels([
            (r"\beta_*-\epsilon_*", [edge_x, -1.6, -0.15], TEAL,
             [edge_x, -1.6, -1.55])])
        x0, y0 = 1.07, -0.25
        hypothetical = polyline([[x0+0.13*math.cos(a), y0+0.13*math.sin(a), -1.5]
                                 for a in np.linspace(0, TAU, 65)], CORAL, 3.5)
        zero_label = self.world_labels([
            (r"\rho", [x0-0.22, y0-0.45, -1.32], CORAL, [x0, y0, -1.5])])
        spike = skin(lambda r, a: np.array([
            x0+r*math.cos(a), y0+r*math.sin(a),
            -1.6+0.9*math.log1p(1/max(r, 0.028))]),
            [0, 0.65], [0, TAU], CORAL, 0.85, (24, 24), 0.32)
        return dict(base=VGroup(floor, sigma_wall, supremum, labels),
                    labels=labels, region=old_region, extension=new_region,
                    low=low, high=high, ceiling=ceiling, common=common, gap=gap,
                    edge_label=new_label, zero=hypothetical,
                    zero_label=zero_label, spike=spike)

    def construct(self):
        self.camera.background_color = BONE
        self.camera.light_source.move_to(np.array([-7, -8, 11]))
        self.hud = None
        self.film_seconds = 0.0
        self._cairo_center = None
        # Opaque gallery margins reserve space for one formula and two lines.
        margins = VGroup(
            Rectangle(width=14.24, height=1.43, stroke_width=0,
                      fill_color=BONE, fill_opacity=1).move_to([0, 3.305, 0]),
            Rectangle(width=14.24, height=1.39, stroke_width=0,
                      fill_color=BONE, fill_opacity=1).move_to([0, -3.325, 0]))
        for margin, pos in zip(margins, [np.array([0, 3.305, 0]), np.array([0, -3.325, 0])]):
            self.screen_anchor(margin, pos)
        margins.set_z_index(1000)
        self.add_fixed_in_frame_mobjects(margins)

        # ACT I / 0--24. A magnified chart of the first zero; no pole in this domain.
        local_land, local_graph = self.landscape(close=True)
        first_zero = bead(local_graph(0.5, ZERO_T[0]), INK, 0.10)
        self.set_camera_orientation(**self.pose(70, -95, 1.12, (0.1, -1.4, -0.1)))
        self.add(local_land)
        self.beat(4, title="A FRONTIER FOR THE ZEROS",
                  lines=("OpenAI Mathematics in 3D  /  Family 003",),
                  camera=self.pose(66, -88, 1.0, (0, -0.75, -0.15)))
        self.beat(6, r"s=\sigma+it",
                  ("Two real coordinates locate one complex number.",
                   "Sampled analytic continuation near the first known zero."),
                  camera=self.pose(61, -78, 0.92, (0, 0, -0.2)))
        self.beat(8, r"h=\log\!\left(1+|\zeta(s)|\right)",
                  ("Height records the magnitude of the continued function.",
                   "A function-value visualization, not a physical surface or proof."),
                  color=TEAL, camera=self.pose(57, -65, 1.07, (0, 0, -0.45)))
        self.beat(6, r"\zeta(\rho)=0,\qquad \rho\approx\tfrac12+14.134725\,i",
                  ("A zero is a complex input where the function vanishes.",
                   "The valley reaches height zero at this sampled zero."),
                  size=39, color=TEAL,
                  camera=self.pose(59, -60, 1.30, (0, 0, -0.95)),
                  anims=(FadeIn(first_zero, suspend_mobject_updating=False),))

        # ACT II / 24--46. Each rib is an actual individual Euler-factor magnitude.
        ribs, rib_floors, prime_labels = self.prime_ribs()
        prime_world = VGroup(ribs, prime_labels)
        self.beat(8,
                  r"\zeta(s)=\sum_{n\ge1}n^{-s}=\prod_{p\ {\rm prime}}(1-p^{-s})^{-1}"
                  r",\qquad \Re s>1",
                  ("One function joins sums over integers to products over primes.",
                   "Both expressions converge in the region shown in the formula."),
                  size=38, camera=self.pose(58, -105, 0.9, (0, 0, -0.3)),
                  anims=(FadeOut(local_land, suspend_mobject_updating=False),
                         FadeOut(first_zero, suspend_mobject_updating=False),
                         FadeIn(prime_world, suspend_mobject_updating=False)))
        self.beat(7,
                  r"h_p(t)=\log\!\left(1+\left|(1-p^{-1.25-it})^{-1}\right|\right)",
                  ("Three ribs: the individual factors for primes 2, 3 and 5.",
                   "Their product connects prime arithmetic to zeta."),
                  color=TEAL, size=38,
                  camera=self.pose(52, -80, 0.91, (0, 0, -0.35)))
        continuation_floor = panel(
            [[-5, -3.6, -1.62], [5, -3.6, -1.62],
             [5, 3.6, -1.62], [-5, 3.6, -1.62]], TEAL, 0.065)
        self.beat(7, r"\zeta:\mathbb C\setminus\{1\}\longrightarrow\mathbb C",
                  ("Analytic continuation extends the same complex function.",
                   "The excluded point is a pole, not a zero."),
                  color=TEAL,
                  camera=self.pose(63, -47, 0.77, (0, 0, -0.25)),
                  anims=(Transform(ribs, rib_floors),
                         FadeOut(prime_labels, suspend_mobject_updating=False),
                         FadeIn(continuation_floor, suspend_mobject_updating=False)))
        self.forget_labels(prime_labels)

        # ACT III / 46--76. The four numerical markers never move in this chart.
        strip, middle, strip_labels = self.critical_strip()
        right = self.curtain(11/12)
        left = self.curtain(1/8)
        self.beat(6,
                  r"(t_1,t_2,t_3,t_4)\approx(14.1347,\ 21.0220,\ 25.0109,\ 30.4249)",
                  ("The critical strip: real part between zero and one.",
                   "Sampled known zeros; their positions stay fixed."),
                  size=36, camera=self.pose(63, -45, 0.73, (-0.5, 0, -0.1)),
                  anims=(FadeOut(ribs, suspend_mobject_updating=False),
                         FadeOut(continuation_floor, suspend_mobject_updating=False),
                         FadeIn(strip, suspend_mobject_updating=False)))
        self.beat(6, r"\mathrm{RH}:\qquad \Re\rho=\tfrac12",
                  ("Full RH would put every nontrivial zero on the gold line.",
                   "Four samples cannot settle an assertion at every height."),
                  color=GOLD, camera=self.pose(58, -60, 0.82, (-0.6, 0, -0.35)))
        self.beat(6,
                  r"\exists\,\theta<1:\quad\zeta(s)\ne0\quad(\Re s>\theta,\ s\ne1)",
                  ("Quasi-RH asks for one fixed frontier at every height.",
                   "The principal pole at one is allowed."),
                  size=39, camera=self.pose(60, -62, 0.86, (0.2, 0, 0)),
                  anims=(FadeIn(right, suspend_mobject_updating=False),))
        self.beat(6, r"\theta:\quad \frac{11}{12}\longrightarrow\frac78",
                  ("The manuscript advances the frontier to the left.",
                   "Only the strict half-plane to its right is zero-free."),
                  color=CORAL,
                  camera=self.pose(67, -66, 1.32, (2.30, 0.1, 0.35)),
                  anims=(right.animate.shift(np.array([-1/3, 0, 0])),))
        boundary_labels = self.world_labels([
            (r"\tfrac18", self.strip_point(1/8, 12, 2.62), CORAL,
             self.strip_point(1/8, 12, 2.35)),
            (r"\tfrac78", self.strip_point(7/8, 12, 2.62), CORAL,
             self.strip_point(7/8, 12, 2.35))])
        self.beat(6, r"\frac18\le\Re\rho\le\frac78",
                  ("Zeta symmetry gives the other boundary; the middle is unresolved.",
                   "Finite window; the manuscript's assertion is at every height."),
                  color=CORAL, camera=self.pose(59, -61, 0.72, (-0.4, 0, 0.15)),
                  anims=(FadeIn(left, suspend_mobject_updating=False),
                         FadeIn(middle, suspend_mobject_updating=False),
                         FadeIn(boundary_labels, suspend_mobject_updating=False)))
        strip_tableau = VGroup(strip, right, left, middle, boundary_labels)

        # ACT IV / 76--108. Equal parameter, not independent arc-length motion.
        loop_world, phase, mobile, linear_model, loop_labels = self.winding_world()
        self.beat(5,
                  r"s(\alpha)=\rho+0.1e^{i\alpha},\qquad w(\alpha)=\zeta(s(\alpha))",
                  ("One positive circuit around the first sampled zero.",
                   "Input and image use separate magnifications: 16 and 20."),
                  size=38, camera=self.pose(55, -60, 0.98, (0, 0, -0.1)),
                  anims=(FadeOut(strip_tableau, suspend_mobject_updating=False),
                         FadeIn(loop_world, suspend_mobject_updating=False)))
        self.forget_labels(strip_labels)
        self.forget_labels(boundary_labels)
        # The image is evaluated from zeta, not from the linear model.
        self.move_camera(**self.pose(55, -105, 1.03, (0, 0, -0.1)),
                         added_anims=[phase.animate.set_value(1)],
                         run_time=13, rate_func=linear)
        self.film_seconds += 13
        mobile.clear_updaters()
        self.beat(7, r"\zeta(s)\approx\zeta'(\rho)(s-\rho)",
                  ("The computed image winds once around the origin.",
                   "This sampled zero is simple; gold shows the local approximation."),
                  color=TEAL, camera=self.pose(51, -90, 1.14, (1.1, 0, -0.15)),
                  anims=(Create(linear_model),))
        reciprocal = self.reciprocal()
        self.beat(7,
                  r"q(s)=\log\!\left(1+\min\{80,\ |\zeta(s)|^{-1}\}\right)",
                  ("Reciprocal magnitude capped at 80 for this sculpture.",
                   "An L-zero forces a pole of its reciprocal."),
                  color=CORAL, size=39,
                  camera=self.pose(60, -63, 1.17, (0, 0, 0.25)),
                  anims=(FadeOut(loop_world, suspend_mobject_updating=False),
                         FadeOut(linear_model, suspend_mobject_updating=False),
                         FadeIn(reciprocal, suspend_mobject_updating=False)))
        self.forget_labels(loop_labels)

        # ACT V / 108--134. Geometry of the arithmetic, then an explicitly schematic map.
        lattice = self.eisenstein()
        self.beat(8,
                  r"\mathcal O_F=\mathbb Z[\tau],\quad"
                  r"\tau=\frac{-1+i\sqrt3}{2},\quad F=\mathbb Q(\sqrt{-3})",
                  ("The Eisenstein integers form a triangular lattice.",
                   "Height shows a norm lift, not character values."),
                  size=38, color=TEAL,
                  camera=self.pose(67, -55, 1.10, (0.2, -0.5, -0.65)),
                  anims=(FadeOut(reciprocal, suspend_mobject_updating=False),
                         FadeIn(lattice, suspend_mobject_updating=False)))
        self.beat(6, r"\eta(\mathfrak a\mathfrak b)=\eta(\mathfrak a)\eta(\mathfrak b)",
                  ("Characters are multiplicative arithmetic weights.",
                   "Here finite-order Hecke characters weight ideals."),
                  color=TEAL, camera=self.pose(49, -83, 0.83, (0, 0, -0.2)))
        reflection, poisson, rows, signal, seams = self.arithmetic_map()
        self.beat(6, r"\mathrm{Reflection}\quad\longleftrightarrow\quad\mathrm{Poisson}",
                  ("Two exact views of one completed cubic-theta sum.",
                   "Proof schematic: reflection supplies a direct bound."),
                  camera=self.pose(51, -83, 0.9, (0, 0, 0)),
                  anims=(FadeOut(lattice, suspend_mobject_updating=False),
                         FadeIn(reflection, suspend_mobject_updating=False),
                         FadeIn(poisson, suspend_mobject_updating=False),
                         FadeIn(seams, suspend_mobject_updating=False)))
        self.beat(6, r"\frac{1}{L_F(s,\eta)}",
                  ("Poisson proof map: principal signal plus character rows.",
                   "The Hecke family is needed even for zeta."),
                  color=GOLD, size=47,
                  camera=self.pose(52, -75, 1.01, (0.7, 0, 0.2)),
                  anims=(FadeOut(poisson, suspend_mobject_updating=False),
                         FadeIn(rows, suspend_mobject_updating=False),
                         FadeIn(signal, suspend_mobject_updating=False)))

        # ACT VI / 134--156. Changed normalization and two different moment controls.
        compensation = VGroup()
        for x in [1.0, 2.0, 3.0]:
            compensation.add(polyline([
                [x, 0.4*math.cos(a), 0.60+0.4*math.sin(a)]
                for a in np.linspace(0, TAU, 65)], CORAL, 2.0))
        self.beat(7, r"\text{Part II: a new normalized sum}",
                  ("Prime compensation modifies the arithmetic sum.",
                   "Unequal scales change the comparison."),
                  camera=self.pose(52, -68, 0.96, (0.25, 0, 0.1)),
                  anims=(reflection.animate.stretch(1.08, 0),
                         rows.animate.stretch(0.86, 0),
                         signal.animate.stretch(0.86, 0),
                         FadeIn(compensation, suspend_mobject_updating=False)))
        moment_frames = VGroup()
        for x, count, color in [(-2.7, 2, TEAL), (2.5, 4, CORAL)]:
            for j in range(count):
                moment_frames.add(polyline([
                    [x+0.16*j, 1.2*math.cos(a), 0.25+1.2*math.sin(a)]
                    for a in np.linspace(0, PI, 65)], color, 1.8, 0.85))
        self.beat(7,
                  r"\text{inverse: second moment}\qquad\text{plain: fourth moment}",
                  ("Two different estimates control the remaining rows.",
                   "Proof schematic; the shapes are not numerical proof data."),
                  size=35, camera=self.pose(49, -62, 0.99, (0, 0, 0.3)),
                  anims=(FadeOut(compensation, suspend_mobject_updating=False),
                         Create(moment_frames)))
        self.beat(8, r"C(s)=s-\frac{11}{16},\qquad C\!\left(\frac78\right)=\frac3{16}",
                  ("J: normalized sum. f: reciprocal-L Mellin signal.",
                   "Target character: eta. Positive scale: Z."),
                  color=GOLD, size=42,
                  camera=self.pose(51, -65, 1.05, (0, 0, 0.25)))
        arithmetic = VGroup(reflection, rows, signal, seams, moment_frames)

        # ACT VII / 156--202. Conditional geometry; no known zero enters this chart.
        proof = self.proof_geometry()
        self.beat(6, r"\text{Assume }\quad\beta_*>\sigma_0=\frac78",
                  ("Supremum of 1/2 and family-zero real parts in [1/2, 1]; no poles.",
                   "Primitive Hecke family; this supremum need not be attained."),
                  color=CORAL, size=41,
                  camera=self.pose(62, -58, 0.9, (0, 0, 0.1)),
                  anims=(FadeOut(arithmetic, suspend_mobject_updating=False),
                         FadeIn(proof["base"], suspend_mobject_updating=False),
                         FadeIn(proof["region"], suspend_mobject_updating=False)))
        self.beat(5, r"|f_\eta|\le |J_\eta|+|J_\eta-f_\eta|",
                  ("Small sum + small difference gives a small signal.",
                   "Conditional proof schematic."),
                  camera=self.pose(57, -67, 0.92, (-0.4, 0, 0)),
                  anims=(FadeIn(proof["low"], suspend_mobject_updating=False),
                         FadeIn(proof["high"], suspend_mobject_updating=False),
                         Create(proof["ceiling"])))
        self.beat(8,
                  r"\begin{aligned}|J_\eta(Z)|&\ll_\eta Z^{C(\sigma_0)+\omega}\\"
                  r"|J_\eta(Z)-f_\eta(Z)|&\ll_\eta Z^{C(\beta_*)-\sigma}\end{aligned}",
                  ("Positive omega is below the gap; sigma is a saving exponent.",
                   "Common positive exponents; constants may depend on eta."),
                  size=38, camera=self.pose(55, -71, 0.97, (-0.3, -0.7, -0.25)))
        self.beat(7,
                  r"\begin{gathered}"
                  r"\epsilon_*=\min\{\beta_*-\sigma_0-\omega,\ \sigma\}>0\\"
                  r"|f_\eta(Z)|\ll_\eta Z^{C(\beta_*)-\epsilon_*}"
                  r"\end{gathered}",
                  ("The smaller of the two savings is still positive.",
                   "This common margin is the key to the contradiction."),
                  color=GOLD, size=38,
                  camera=self.pose(53, -75, 1.00, (-0.25, 0, 0.2)),
                  anims=(FadeOut(proof["low"], suspend_mobject_updating=False),
                         FadeOut(proof["high"], suspend_mobject_updating=False),
                         FadeIn(proof["common"], suspend_mobject_updating=False),
                         Create(proof["gap"])))
        self.beat(8, r"\Re s>\beta_*-\epsilon_*>\sigma_0",
                  ("Power saving at infinity and rapid decay at zero",
                   "make the Mellin transform F holomorphic: complex analytic."),
                  color=TEAL, size=44,
                  camera=self.pose(54, -78, 0.95, (0.55, 0, 0.15)),
                  anims=(Transform(proof["region"], proof["extension"]),
                         FadeIn(proof["edge_label"], suspend_mobject_updating=False),
                         FadeOut(proof["common"], suspend_mobject_updating=False),
                         FadeOut(proof["ceiling"], suspend_mobject_updating=False),
                         FadeOut(proof["gap"], suspend_mobject_updating=False)))
        self.beat(6,
                  r"\frac{1}{L_F^{\mathcal S}(s,\eta)}"
                  r"=e^{-(s-5/6)^2}\frac{F_\eta(s)}{H_\eta(s)},"
                  r"\qquad |H_\eta(s)|\ge\frac12",
                  ("Fourier inversion identifies F in the half-plane Re s > 1.",
                   "Identity extends the reciprocal; deleted Euler factors are nonzero."),
                  color=TEAL, size=37,
                  camera=self.pose(53, -82, 1.00, (0.7, 0, 0.15)))
        self.beat(6,
                  r"L_F^{\mathcal S}(\rho,\eta)=0"
                  r"\quad\Longrightarrow\quad 1/L_F^{\mathcal S}\text{ has a pole at }\rho",
                  ("The supremum supplies a hypothetical zero inside the extension.",
                   "A pole contradicts holomorphic continuation."),
                  color=CORAL, size=37,
                  camera=self.pose(55, -76, 1.10, (1.0, -0.1, 0.1)),
                  anims=(Create(proof["zero"]),
                         FadeIn(proof["zero_label"], suspend_mobject_updating=False),
                         FadeIn(proof["spike"], suspend_mobject_updating=False)))

        # ACT VIII / 202--220. Cut to the original chart; never cancel or erase the pole.
        self.remove(proof["base"], proof["region"], proof["edge_label"],
                    proof["zero"], proof["zero_label"], proof["spike"])
        self.forget_labels(proof["labels"])
        self.forget_labels(proof["edge_label"])
        self.forget_labels(proof["zero_label"])
        main_land, unused_graph = self.landscape(close=False)
        self.camera.add_fixed_in_frame_mobjects(strip_labels, boundary_labels)
        # FadeOut cleanup leaves the saved objects at their original geometry and style.
        self.add(main_land, middle, strip, right, left, boundary_labels)
        self.set_camera_orientation(**self.pose(58, -65, 0.72, (-0.3, -0.7, -0.25)))
        self.beat(8,
                  r"\begin{gathered}\Re s>\frac78:\quad L(s)\ne0,"
                  r"\qquad F=\mathbb Q(\sqrt{-3})\\"
                  r"\text{principal pole at }s=1\text{ allowed}\end{gathered}",
                  ("Manuscript: zeta, all Dirichlet L, finite-order Hecke L over F.",
                   "Uniform in character, conductor and imaginary height."),
                  color=CORAL, size=36,
                  camera=self.pose(54, -73, 0.74, (-0.3, -0.7, -0.25)))
        self.beat(4, r"\frac18\le\Re\rho\le\frac78",
                  ("Full RH remains open.",
                   "The central strip is unresolved by this assertion."),
                  color=CORAL, camera=self.pose(51, -78, 0.75, (-0.3, -0.7, -0.25)))
        self.beat(6, r"\Re s>\frac78",
                  ("OpenAI manuscript / 30 September 2026 / family 003",
                   "Full proof and Lean build not independently checked."),
                  color=CORAL, size=47,
                  camera=self.pose(50, -80, 0.76, (-0.3, -0.7, -0.25)))
        self.update_mobjects(0)
        if abs(self.film_seconds-220) > 1e-8:
            raise ValueError("Film timing must total 220 seconds")
