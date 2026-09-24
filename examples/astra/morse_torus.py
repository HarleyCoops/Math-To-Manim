from manim import *
import numpy as np

config.renderer = "cairo"
config.pixel_width = 1280
config.pixel_height = 720
config.frame_rate = 30
config.frame_height = 8
config.frame_width = 128 / 9
config.background_color = "#071426"


class AstraFilm(ThreeDScene):
    def construct(self):
        BG = "#071426"
        TEAL = "#21CDBA"
        CYAN = "#75E8FF"
        DIM = "#396A87"
        GOLD = "#FFC766"
        CORAL = "#FF8078"
        VIOLET = "#B58AFF"
        INK = "#EAF6FF"
        R, r = 2.0, 0.8

        # The major circle lies in the vertical xz-plane.
        # Orthogonal tangent lengths are rho > 0 and r > 0.
        # h_u = rho*cos(u), h_v = -r*sin(v)*sin(u).
        # Criticality forces cos(u)=0 and sin(v)=0: exactly four points.
        # Milnor, Morse Theory, sections 2--3 and 6 supplies the theorems.
        def torus(u, v):
            rho = R + r * np.cos(v)
            return np.array([rho * np.cos(u), r * np.sin(v), rho * np.sin(u)])

        critical_uv = [(-PI / 2, 0), (-PI / 2, PI), (PI / 2, PI), (PI / 2, 0)]
        critical_heights = [float(torus(u, v)[2]) for u, v in critical_uv]
        critical_indices = []
        critical_determinants = []
        for u, v in critical_uv:
            rho = R + r * np.cos(v)
            gradient = np.array([rho * np.cos(u), -r * np.sin(v) * np.sin(u)])
            hessian = np.array([
                [-rho * np.sin(u), -r * np.sin(v) * np.cos(u)],
                [-r * np.sin(v) * np.cos(u), -r * np.cos(v) * np.sin(u)],
            ])
            assert np.linalg.norm(gradient) < 1e-12
            critical_determinants.append(float(np.linalg.det(hessian)))
            critical_indices.append(int(np.count_nonzero(np.linalg.eigvalsh(hessian) < 0)))
        assert np.allclose(critical_heights, [-2.8, -1.2, 1.2, 2.8])
        assert np.allclose(critical_determinants, [2.24, -0.96, -0.96, 2.24])
        assert critical_indices == [0, 1, 1, 2]
        assert sum((-1) ** k for k in critical_indices) == 0

        def analytic_normals(points):
            rho = np.sqrt(points[:, 0] ** 2 + points[:, 2] ** 2)
            radial = (rho - R) / np.maximum(rho, 1e-12)
            normals = np.column_stack((
                radial * points[:, 0], points[:, 1], radial * points[:, 2],
            ))
            return normals / np.maximum(np.linalg.norm(normals, axis=1, keepdims=True), 1e-12)

        for u in np.linspace(-PI, PI, 9):
            for v in np.linspace(-PI, PI, 9):
                normal = analytic_normals(torus(u, v)[None, :])[0]
                tangent_u = np.array([-np.sin(u), 0, np.cos(u)])
                tangent_v = np.array([
                    -np.sin(v) * np.cos(u), np.cos(v), -np.sin(v) * np.sin(u),
                ])
                assert abs(np.linalg.norm(normal) - 1) < 1e-12
                assert abs(np.dot(normal, tangent_u)) < 1e-12
                assert abs(np.dot(normal, tangent_v)) < 1e-12

        def sublevel_points(a, w, q):
            # h = -rho*cos(theta), theta = u + pi/2.
            # Adaptive v knots resolve cap seams above the upper saddle.
            # Periodic seams and collapsed chart edges are not boundaries.
            extent = np.arccos(np.clip((-a - R) / r, -1, 1)) if a < -(R - r) else PI
            split = np.arccos(np.clip((a - R) / r, -1, 1)) if a > R - r else extent
            knots = np.concatenate([
                np.linspace(-extent, -split, 7)[:-1],
                np.linspace(-split, 0, 7)[:-1],
                np.linspace(0, split, 7)[:-1],
                np.linspace(split, extent, 7),
            ])
            interval = np.minimum(np.floor(q).astype(int), 23)
            fraction = q - interval
            v = (1 - fraction) * knots[interval] + fraction * knots[interval + 1]
            rho = R + r * np.cos(v)
            alpha = np.arccos(np.clip(-a / rho, -1, 1))
            u = -PI / 2 + w * alpha
            return np.stack((rho * np.cos(u), r * np.sin(v), rho * np.sin(u)), axis=-1)

        branch_parameter = np.linspace(-1.0, 1.0, 193)

        def boundary_points(a):
            # Exact level branches, joined according to their topology.
            # At a saddle the joined curve has a singular crossing.
            if abs(a) >= R + r:
                return []
            beta = np.arccos(np.clip((abs(a) - R) / r, -1, 1))
            v = beta * np.sin(PI * branch_parameter / 2)
            rho = R + r * np.cos(v)
            x = np.sqrt(np.maximum(0.0, rho * rho - a * a))
            y = r * np.sin(v)
            if abs(a) >= R - r:
                x[[0, -1]] = 0.0
            plus = np.column_stack((x, y, np.full_like(x, a)))
            minus = np.column_stack((-x, y, np.full_like(x, a)))
            if abs(a) < R - r:
                plus[-1] = plus[0]
                minus[-1] = minus[0]
                return [plus, minus]
            joined = np.vstack((plus, minus[-2::-1]))
            joined[-1] = joined[0]
            return [joined]

        # Runtime guards verify analytic samples, not continuous-video quality.
        test_w, test_q = np.meshgrid(np.linspace(-1, 1, 65), np.linspace(0, 24, 49))
        for a in [-2.799, -2.4, -1.38, -1.20001, -1.2, -1.19999,
                  -1.02, 0.0, 0.99, 1.19999, 1.2, 1.20001, 1.41, 2.4, 2.799, 3.0]:
            p = sublevel_points(a, test_w, test_q).reshape(-1, 3)
            residual = (np.hypot(p[:, 0], p[:, 2]) - R) ** 2 + p[:, 1] ** 2 - r * r
            assert np.max(np.abs(residual)) < 1e-11
            assert np.max(p[:, 2] - a) < 1e-11
            for curve in boundary_points(a):
                residual = (np.hypot(curve[:, 0], curve[:, 2]) - R) ** 2 + curve[:, 1] ** 2 - r * r
                assert np.max(np.abs(residual)) < 1e-11
                assert np.max(np.abs(curve[:, 2] - a)) < 1e-11
                assert np.linalg.norm(curve[0] - curve[-1]) < 1e-11
        assert [len(boundary_points(a)) for a in [-3, -2.4, 0, 2.4, 3]] == [0, 1, 2, 1, 0]

        def hold_to(seconds):
            remaining = seconds - self.time
            if remaining > 1 / config.frame_rate:
                self.wait(remaining)

        def fixed(mob, layer=60):
            mob.set_shade_in_3d(False)
            mob.set_z_index(layer)
            self.add_fixed_in_frame_mobjects(mob)
            return mob

        top_band = Rectangle(width=config.frame_width, height=1.24)
        top_band.set_fill(BG, opacity=1).set_stroke(width=0).move_to([0, 3.38, 0])
        bottom_band = Rectangle(width=config.frame_width, height=1.20)
        bottom_band.set_fill(BG, opacity=1).set_stroke(width=0).move_to([0, -3.40, 0])
        fixed(VGroup(top_band, bottom_band), 50)
        overlay = None

        def cue(formula, lines=(), duration=0.4):
            nonlocal overlay
            assert len(lines) <= 2
            if overlay is not None:
                self.play(FadeOut(overlay), run_time=duration / 2)
                self.remove_fixed_in_frame_mobjects(overlay)
            else:
                self.wait(duration / 2)
            parts = []
            if formula:
                tex = MathTex(formula, font_size=38, color=INK)
                if tex.width > 12.4:
                    tex.scale_to_fit_width(12.4)
                if tex.height > 0.57:
                    tex.scale_to_fit_height(0.57)
                tex.move_to([0, 3.38, 0])
                parts.append(tex)
            for i, line in enumerate(lines):
                text = Text(line, font_size=26, color=INK)
                if text.height > 0.30:
                    text.scale_to_fit_height(0.30)
                if text.width > 12.3:
                    text.scale_to_fit_width(12.3)
                y = -3.40 if len(lines) == 1 else -3.17 - 0.47 * i
                text.move_to([0, y, 0])
                parts.append(text)
            overlay = fixed(VGroup(*parts))
            self.play(FadeIn(overlay), run_time=duration / 2)

        def camera_to(phi, theta, zoom, center, duration, animations=()):
            self.move_camera(
                phi=phi * DEGREES, theta=theta * DEGREES, gamma=0,
                zoom=zoom, frame_center=np.array(center, dtype=float),
                added_anims=list(animations), run_time=duration, rate_func=smooth,
            )

        self.set_camera_orientation(
            phi=78 * DEGREES, theta=-115 * DEGREES,
            gamma=0, zoom=0.80, focal_distance=20,
        )
        self.camera.light_source.move_to([-4, -7, 7])

        # Analytic normals prevent unstable shading on curved clipped patches.
        # Untagged objects retain native Cairo shading and depth sorting.
        native_modified_rgbas = self.camera.modified_rgbas

        def torus_modified_rgbas(vmobject, rgbas):
            try:
                torus_patch = vmobject._astra_torus_patch
            except AttributeError:
                return native_modified_rgbas(vmobject, rgbas)
            if not torus_patch:
                return native_modified_rgbas(vmobject, rgbas)
            if (not self.camera.should_apply_shading
                    or not vmobject.shade_in_3d
                    or vmobject.get_num_points() == 0):
                return rgbas
            end_index = ((len(vmobject.points) - 1) // 6) * 3
            anchors = vmobject.points[[0, end_index]]
            normals = analytic_normals(anchors)
            to_light = self.camera.light_source.points[0] - anchors
            to_light /= np.maximum(np.linalg.norm(to_light, axis=1, keepdims=True), 1e-12)
            light = 0.5 * np.sum(normals * to_light, axis=1) ** 3
            light = np.where(light < 0, 0.5 * light, light)
            if len(rgbas) < 2:
                shaded = np.array(rgbas, dtype=float).repeat(2, axis=0)
            else:
                shaded = np.array(rgbas[:2], dtype=float, copy=True)
            shaded[:, :3] = np.clip(shaded[:, :3] + light[:, None], 0, 1)
            return shaded

        self.camera.modified_rgbas = torus_modified_rgbas

        shell = Surface(
            torus, u_range=(-PI, PI), v_range=(-PI, PI),
            resolution=(32, 16), checkerboard_colors=False,
            fill_color="#124B5B", fill_opacity=0.28,
            stroke_color=CYAN, stroke_width=0.45,
        )
        shell.set_stroke(opacity=0.55)
        level = ValueTracker(-3.2)
        self.add(level)

        # Allocate once; update points of 768 reusable patches during sweeps.
        skin = Surface(
            lambda w, q: np.array([w, q, 0.0]),
            u_range=(-1, 1), v_range=(0, 24), resolution=(32, 24),
            checkerboard_colors=False, fill_color=TEAL, fill_opacity=0,
            stroke_color=CYAN, stroke_width=0.24,
        )
        faces = list(skin.submobjects)
        parameters = []
        for face in faces:
            face._astra_torus_patch = True
            face.set_shade_in_3d(True)
            corners = np.array([
                [face.u1, face.v1], [face.u2, face.v1],
                [face.u2, face.v2], [face.u1, face.v2],
                [face.u1, face.v1],
            ])
            samples = []
            for k in range(4):
                for fraction in (0.0, 1 / 3, 2 / 3):
                    samples.append((1 - fraction) * corners[k] + fraction * corners[k + 1])
            samples.append(corners[0])
            parameters.append(samples)
        parameters = np.array(parameters)
        w_samples = parameters[:, :, 0]
        q_samples = parameters[:, :, 1]
        palette = [
            interpolate_color(ManimColor(TEAL), ManimColor(CYAN), t)
            for t in np.linspace(0.0, 0.36, 12)
        ]

        plane = Polygon(
            [-3.2, -1.2, -3.2], [3.2, -1.2, -3.2],
            [3.2, 1.2, -3.2], [-3.2, 1.2, -3.2],
            fill_color=GOLD, fill_opacity=0.055,
            stroke_color=GOLD, stroke_width=0.85,
        )
        plane.set_stroke(opacity=0.38).set_shade_in_3d(True)
        rims = VGroup(*[
            VMobject(stroke_color=GOLD, stroke_width=3.0, fill_opacity=0)
            .set_points_as_corners([ORIGIN, ORIGIN])
            for _ in range(2)
        ])
        rims.set_shade_in_3d(False).set_z_index(3)
        state = {"last": None, "curves": []}

        def refresh_geometry(mob):
            a = float(level.get_value())
            if state["last"] is not None and abs(a - state["last"]) < 1e-10:
                return
            state["last"] = a
            plane.set_points_as_corners([
                [-3.2, -1.2, a], [3.2, -1.2, a],
                [3.2, 1.2, a], [-3.2, 1.2, a], [-3.2, -1.2, a],
            ])
            curves = boundary_points(a)
            state["curves"] = curves
            for i, path in enumerate(rims):
                if i < len(curves):
                    path.set_points_as_corners(curves[i])
                    path.set_stroke(opacity=1)
                else:
                    path.set_stroke(opacity=0)
            if a <= -(R + r):
                mob.set_opacity(0)
                return
            points = sublevel_points(a, w_samples, q_samples)
            centers = np.mean(points[:, :-1], axis=1)
            color_indices = np.clip(((1 - centers[:, 1] / r) * 5.5).astype(int), 0, 11)
            p0, p3, p6, p9 = (points[:, k] for k in (0, 3, 6, 9))
            areas = 0.5 * (
                np.linalg.norm(np.cross(p3 - p0, p6 - p0), axis=1)
                + np.linalg.norm(np.cross(p6 - p0, p9 - p0), axis=1)
            )
            saddle = -1.2 if a < 0 else 1.2
            crossing_strength = max(0.0, 1 - abs(a - saddle) / 0.36)
            for i, face in enumerate(faces):
                face.set_points_as_corners(points[i])
                if areas[i] < 1e-14:
                    face.set_fill(opacity=0).set_stroke(opacity=0)
                    continue
                color = palette[color_indices[i]]
                if crossing_strength > 0:
                    d = centers[i] - np.array([0.0, 0.0, saddle])
                    proximity = np.exp(-(
                        (d[0] / 0.62) ** 2 + (d[1] / 0.43) ** 2 + (d[2] / 0.45) ** 2
                    ))
                    weight = crossing_strength * proximity
                    if weight > 0.025:
                        color = interpolate_color(color, ManimColor(VIOLET), 0.85 * weight)
                face.set_fill(color, opacity=0.94)
                face.set_stroke(CYAN, width=0.24, opacity=0.34)

        refresh_geometry(skin)
        skin.add_updater(refresh_geometry)
        self.add(skin, rims)

        def sweep(a, duration):
            self.play(level.animate.set_value(a), run_time=duration, rate_func=smooth)

        def direction_arcs(u, v, colors):
            return VGroup(
                ParametricFunction(
                    lambda t: torus(u + t, v), t_range=[-0.35, 0.35, 0.01],
                    color=colors[0], stroke_width=4.5, use_smoothing=False,
                ),
                ParametricFunction(
                    lambda t: torus(u, v + t), t_range=[-0.35, 0.35, 0.01],
                    color=colors[1], stroke_width=4.5, use_smoothing=False,
                ),
            ).set_shade_in_3d(False).set_z_index(4)

        def trace_arcs(arcs, duration=1.0):
            self.play(Create(arcs[0]), Create(arcs[1]), run_time=duration)

        markers = VGroup(*[
            Dot3D(point=[0, 0, h], radius=0.075, color=color, resolution=(8, 4))
            .set_stroke(width=0)
            for h, color in zip(critical_heights, [CORAL, VIOLET, VIOLET, CORAL])
        ])

        # 0--7: orientation.
        cue(r"T^2\colon\ \text{the torus surface}", [
            "Topology: properties unchanged by continuous deformation",
            "without cutting or gluing.",
        ])
        self.play(FadeIn(shell), run_time=1.6)
        camera_to(76, -70, 0.85, ORIGIN, 4.0)
        hold_to(7)

        # 7--16: height and surface sublevel sets.
        guide = VGroup(
            Line([-3.5, 0, -3.05], [-3.5, 0, 3.05], color=DIM, stroke_width=1.3),
            Line([-3.5, 0, 3.05], [-3.62, 0, 2.83], color=GOLD, stroke_width=2),
            Line([-3.5, 0, 3.05], [-3.38, 0, 2.83], color=GOLD, stroke_width=2),
        )
        cue(r"h(x,y,z)=z", ["Height is the vertical coordinate."])
        self.play(
            FadeIn(plane), FadeIn(guide),
            shell.animate.set_fill(opacity=0.10).set_stroke(color=DIM, opacity=0.42),
            run_time=0.6,
        )
        sweep(-3.0, 1.0)
        hold_to(10)
        cue(r"M_a=\{p\in T^2:h(p)\leq a\}", [
            "Include surface points at or below height a.",
            "At this height, the included surface is empty.",
        ])
        hold_to(13)
        cue(r"M_a=\{p\in T^2:h(p)\leq a\}", [
            "Teal will mark a two-dimensional surface subset.",
            "We track the torus skin, not a liquid volume.",
        ])
        hold_to(16)

        # 16--34: definitions before the first attachment.
        cue(r"dh_p=0", [
            "Critical point: height has zero derivative",
            "in every tangent direction.",
        ])
        camera_to(78, -78, 1.10, [0, 0, -1.8], 2.0,
                  [FadeIn(markers[0]), FadeOut(guide)])
        minimum_arcs = direction_arcs(-PI / 2, 0, [CORAL, CYAN])
        trace_arcs(minimum_arcs, 1.2)
        hold_to(21)
        cue(r"\det H_p\ne 0", [
            "H is the matrix of second derivatives in local coordinates.",
            "Morse: every critical point is nondegenerate.",
        ])
        hold_to(25)
        cue(r"\operatorname{index}(p)=\#\{\text{negative eigenvalues of }H_p\}", [
            "Count independent downward-bending directions.",
        ])
        self.play(*[
            ShowPassingFlash(arc.copy().set_stroke(width=7), time_width=0.4)
            for arc in minimum_arcs
        ], run_time=1.2)
        hold_to(28)
        cue(r"h(p)=-2.8,\qquad\operatorname{index}(p)=0", [
            "Minimum: index 0. Both directions bend upward.",
        ])
        hold_to(30)
        cue(r"M_a=\{p\in T^2:h(p)\leq a\}", [
            "Crossing the minimum adds a disk.",
        ])
        sweep(-2.4, 2.0)
        cue(r"a=-2.4", [
            "Disk: one boundary curve.",
            "Gold traces the one-dimensional boundary.",
        ])
        self.play(
            ShowPassingFlash(rims[0].copy().set_stroke(width=6), time_width=0.35),
            run_time=0.8,
        )
        self.play(FadeOut(minimum_arcs), run_time=0.4)
        hold_to(34)

        # 34--50: a band attaches to one boundary component.
        cue(r"M_a=\{p\in T^2:h(p)\leq a\}", [
            "Morse attachment theorem:",
            "Topology stays unchanged between critical levels.",
        ])
        camera_to(76, -65, 0.85, ORIGIN, 2.2, [level.animate.set_value(-1.38)])
        cue(r"h(p)=-1.2,\qquad\operatorname{index}(p)=1", [
            "A saddle: one direction rises; one falls.",
        ])
        camera_to(80, -62, 1.18, [0, 0, -1.2], 2.0, [FadeIn(markers[1])])
        lower_arcs = direction_arcs(-PI / 2, PI, [CYAN, VIOLET])
        trace_arcs(lower_arcs)
        hold_to(41)
        cue(r"h(p)=-1.2,\qquad\operatorname{index}(p)=1", [
            "Crossing this saddle attaches a band",
            "to two arcs of the same boundary curve.",
        ])
        sweep(-1.02, 2.8)
        self.play(FadeOut(lower_arcs), run_time=0.4)
        camera_to(76, -65, 0.85, ORIGIN, 2.4, [level.animate.set_value(0.0)])
        cue(r"a=0", ["Cylinder (annulus): two boundary curves."])
        for path in rims:
            self.play(
                ShowPassingFlash(path.copy().set_stroke(width=6), time_width=0.35),
                run_time=0.8,
            )
        hold_to(50)

        # 50--66: a band joins two different boundary components.
        cue(r"M_a=\{p\in T^2:h(p)\leq a\}", [
            "Between the saddles, the surface remains a cylinder.",
        ])
        camera_to(74, -110, 0.85, ORIGIN, 2.2, [level.animate.set_value(0.99)])
        cue(r"h(p)=1.2,\qquad\operatorname{index}(p)=1", [
            "Again: one direction rises; one falls.",
        ])
        camera_to(80, -108, 1.18, [0, 0, 1.2], 2.0, [FadeIn(markers[2])])
        upper_arcs = direction_arcs(PI / 2, PI, [VIOLET, CYAN])
        trace_arcs(upper_arcs)
        cue(r"h(p)=1.2,\qquad\operatorname{index}(p)=1", [
            "This band joins the two boundary curves.",
        ])
        sweep(1.41, 2.6)
        self.play(FadeOut(upper_arcs), run_time=0.4)
        camera_to(76, -85, 0.85, ORIGIN, 2.2, [level.animate.set_value(2.4)])
        cue(r"a=2.4", [
            "Punctured torus: one boundary curve.",
            "A torus with one open disk removed.",
        ])
        hold_to(64)
        cue(r"a=2.4", [
            "Disk and punctured torus each have one boundary.",
            "Their topology differs.",
        ])
        hold_to(66)

        # 66--76: cap the remaining boundary at the maximum.
        cue(r"h(p)=2.8,\qquad\operatorname{index}(p)=2", [
            "Maximum: both independent directions bend downward.",
        ])
        camera_to(76, -72, 0.95, [0, 0, 0.3], 1.6,
                  [level.animate.set_value(2.65), FadeIn(markers[3])])
        maximum_arcs = direction_arcs(PI / 2, 0, [CORAL, VIOLET])
        trace_arcs(maximum_arcs)
        hold_to(70)
        cue(r"h(p)=2.8,\qquad\operatorname{index}(p)=2", [
            "Crossing the maximum caps the remaining boundary.",
        ])
        sweep(3.0, 2.2)
        cue(r"a=3", ["Closed torus: no boundary."])
        skin.clear_updaters()
        self.remove(level)

        # A uniform chart provides the closing complete sculpture.
        finished_skin = Surface(
            torus, u_range=(-PI, PI), v_range=(-PI, PI),
            resolution=(32, 24), checkerboard_colors=False,
            fill_color=TEAL, fill_opacity=0.94,
            stroke_color=CYAN, stroke_width=0.24,
        )
        for face in finished_skin:
            v_mid = (face.v1 + face.v2) / 2
            face.set_fill(interpolate_color(
                ManimColor(TEAL), ManimColor(CYAN),
                0.18 * (1 - np.sin(v_mid)),
            ), opacity=0.94)
            face.set_stroke(CYAN, width=0.24, opacity=0.28)
        self.play(
            FadeOut(plane), FadeOut(shell), FadeOut(maximum_arcs),
            FadeOut(skin), FadeIn(finished_skin), run_time=0.6,
        )
        skin = finished_skin
        camera_to(76, -75, 0.85, ORIGIN, 1.8)
        hold_to(76)

        # 76--88: definition, subdivision, then theorem-based counting.
        cue(r"\chi=V-E+F", [
            "Euler characteristic: vertices minus edges plus faces.",
            "The count is independent of triangulation.",
        ])
        camera_to(76, -75, 0.72, [-2.7, 0, 0], 1.1, [FadeOut(markers)])
        A = np.array([-4.85, -0.80, 0.0])
        B = np.array([-2.75, -0.80, 0.0])
        C = np.array([-3.80, 1.05, 0.0])
        D = (A + B) / 2
        triangle_face = fixed(Polygon(
            A, B, C, stroke_width=0, fill_color=TEAL, fill_opacity=0.25,
        ), 30)
        triangle_edges = fixed(VGroup(*[
            Line(p, q, color=GOLD, stroke_width=3)
            for p, q in [(A, B), (B, C), (C, A)]
        ]), 32)
        triangle_vertices = fixed(VGroup(*[
            Dot(p, radius=0.06, color=CORAL) for p in (A, B, C)
        ]), 34)
        self.remove(triangle_face, triangle_edges, triangle_vertices)
        self.play(FadeIn(triangle_vertices), run_time=0.35)
        self.play(Create(triangle_edges), run_time=0.35)
        self.play(FadeIn(triangle_face), run_time=0.30)
        cue(r"3-3+1=1", ["Three vertices, three edges, one triangular face."])
        hold_to(80)
        split_faces = fixed(VGroup(
            Polygon(A, D, C, stroke_width=0, fill_color=TEAL, fill_opacity=0.30),
            Polygon(D, B, C, stroke_width=0, fill_color=CYAN, fill_opacity=0.22),
        ), 30)
        split_edges = fixed(VGroup(*[
            Line(p, q, color=GOLD, stroke_width=3)
            for p, q in [(A, D), (D, B), (B, C), (C, A), (D, C)]
        ]), 32)
        new_vertex = fixed(Dot(D, radius=0.06, color=CORAL), 34)
        self.play(
            FadeOut(triangle_face), FadeOut(triangle_edges),
            FadeIn(split_faces), FadeIn(split_edges), FadeIn(new_vertex),
            run_time=0.6,
        )
        cue(r"4-5+2=1", ["Subdivision preserves the count."])
        hold_to(82)
        inset = VGroup(triangle_vertices, new_vertex, split_faces, split_edges)
        self.play(FadeOut(inset), run_time=0.3)
        self.remove_fixed_in_frame_mobjects(
            triangle_face, triangle_edges, triangle_vertices,
            new_vertex, split_faces, split_edges,
        )
        cue(r"\Delta\chi=(-1)^k", [
            "Morse attachment theorem: an index-k attachment",
            "changes Euler characteristic by this amount.",
        ])
        hold_to(84)
        disk_icon = Ellipse(width=1.65, height=1.10, color=CORAL, fill_opacity=0.22)
        band_one = RoundedRectangle(
            width=1.80, height=0.64, corner_radius=0.14,
            color=VIOLET, fill_opacity=0.24,
        ).rotate(0.18)
        band_two = RoundedRectangle(
            width=1.80, height=0.64, corner_radius=0.14,
            color=VIOLET, fill_opacity=0.24,
        ).rotate(-0.18)
        cap_icon = VGroup(
            Arc(radius=0.82, start_angle=0, angle=PI, color=CORAL, stroke_width=3),
            Line([-0.82, 0, 0], [0.82, 0, 0], color=CORAL, stroke_width=2),
        )
        for icon, contribution in zip(
            [disk_icon, band_one, band_two, cap_icon], ["+1", "-1", "-1", "+1"],
        ):
            icon.move_to([-3.8, 0.2, 0])
            number = Text(contribution, font_size=34, color=INK).move_to([-3.8, -0.95, 0])
            glyph = fixed(VGroup(icon, number), 35)
            self.play(FadeIn(glyph), run_time=0.2)
            self.wait(0.4)
            self.play(FadeOut(glyph), run_time=0.2)
            self.remove_fixed_in_frame_mobjects(glyph)
        hold_to(88)

        # 88--98: critical-point counts and five-second final hold.
        cue(r"m_k=\#\{\text{critical points of index }k\}", [
            "disk  →  cylinder  →  punctured torus  →  closed torus",
        ])
        camera_to(76, -75, 0.85, ORIGIN, 1.2, [FadeIn(markers)])
        self.camera.reset_rotation_matrix()
        projected_points = [
            self.camera.project_point(np.array([0.0, 0.0, h]))
            for h in critical_heights
        ]
        projected_y = [float(point[1]) for point in projected_points]
        critical_callouts = VGroup()
        for point, color in zip(projected_points, [CORAL, VIOLET, VIOLET, CORAL]):
            anchor = np.array([point[0], point[1], 0.0])
            critical_callouts.add(
                Circle(radius=0.10, color=color, stroke_width=2.2,
                       fill_opacity=0).move_to(anchor),
                Dot(anchor, radius=0.025, color=color),
            )
        fixed(critical_callouts, 36)
        rail = VGroup(Line(
            [4.35, projected_y[0], 0], [4.35, projected_y[-1], 0],
            color=DIM, stroke_width=1.3,
        ))
        rail.add(Text("index", font_size=20, color=INK).move_to([4.77, 2.63, 0]))
        for y, index, color in zip(
            projected_y, critical_indices, [CORAL, VIOLET, VIOLET, CORAL],
        ):
            rail.add(Line([4.20, y, 0], [4.50, y, 0], color=color, stroke_width=2))
            rail.add(Dot([4.35, y, 0], radius=0.045, color=color))
            rail.add(Text(str(index), font_size=26, color=color).move_to([4.84, y, 0]))
        fixed(rail, 35)
        self.play(FadeIn(rail), FadeIn(critical_callouts), run_time=0.4)
        hold_to(92.6)
        self.play(FadeOut(rail), run_time=0.2)
        self.remove_fixed_in_frame_mobjects(rail)
        cue(r"\chi(T^2)=m_0-m_1+m_2=1-2+1=0", duration=0.2)
        hold_to(98)
