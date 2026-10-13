from manim import *
import numpy as np
import math

config.renderer = "cairo"
config.pixel_width = 1280
config.pixel_height = 720
config.frame_rate = 30
config.frame_width = 128 / 9
config.frame_height = 8
config.background_color = "#080E1B"


class AstraFilm(ThreeDScene):
    """The third rhythm. 94 seconds; silent; all teaching geometry is spatial.

    Snapshot: eumemic/exoplanets ec8311b19a61092ad5eae3d34e947b14485d363e.
    Data read 2026-10-12. Review status: not_reviewed.
    Primary-paper provenance: Tey 2023, arXiv:2301.01370;
    ESPRESSO 2026, arXiv:2601.22115; TRICERATOPS, arXiv:2002.00691.
    The distinct 47.5-day RV candidate is deliberately not depicted.
    No rendered or continuous-motion verification is claimed.
    """

    def construct(self):
        ivory = "#F4DCAC"
        cyan = "#52D6EF"
        violet = "#B59AFF"
        amber = "#FFBE58"
        muted = "#7F91AC"
        white = "#EDF3FF"
        gray = "#586679"
        self.hud = None

        periods = np.array([5.5382498, 10.688716, 18.908204403493546])
        a_au = (0.63 * (periods / 365.25) ** 2) ** (1 / 3)
        orbit_radii = 1.8 * a_au / a_au[0]
        # Original b/c radii from Tey 2023, not later revised radii.
        radii_earth = np.array([2.266, 2.415, 2.2071478365538053])
        k = 0.033789403644782876
        impact = 0.7468945703333496
        fit_duration_hours = 2.4555907437510087
        fpp_mean = 0.11134977664133187
        nfpp_max = 1.1854257918475973e-5
        sector_ids = [13, 27, 66, 67, 93, 101, 102, 103]
        self.source_metadata = dict(
            stellar_mass_solar=0.63, stellar_radius_solar=0.60,
            temperature_K=3900, distance_pc=61.54,
            periods_days=periods.tolist(), semimajor_axes_AU=a_au.tolist(),
            radii_earth=radii_earth.tolist(), k=k, impact_parameter=impact,
            fitted_T14_hours=fit_duration_hours,
            radius_errors_earth=[-0.10835866990546572, 0.1122872646124562],
            area_model_depth_ppm=k * k * 1e6, FPP_mean=fpp_mean,
            NFPP_max=nfpp_max, FPP_runs=10,
            sectors=sector_ids, LEO_N_transit=9,
            snr_old=11.339307872309764, snr_new=7.390052000596899,
            centroid_offsets_arcsec=[7.1, 15.5, 9.5],
            nearest_listed_capable_neighbor_arcsec=38.24799745122992,
        )

        def ball(radius, color, center=ORIGIN, resolution=(12, 8), mesh=False):
            return Sphere(
                radius=radius, resolution=resolution,
                fill_color=color, fill_opacity=1,
                checkerboard_colors=False,
                stroke_color="#A18C6D" if mesh else color,
                stroke_width=0.38 if mesh else 0,
            ).move_to(center)

        def curve_piece(func, lo, hi, color, width=1.5, opacity=1):
            curve = ParametricFunction(
                func, t_range=[lo, hi, (hi - lo) / 5],
                use_smoothing=False, color=color, stroke_width=width,
            )
            curve.set_stroke(opacity=opacity)
            curve.set_shade_in_3d(True)
            return curve

        def spatial_curve(func, color, dashed=False, width=1.6, opacity=1):
            # Separate short pieces allow Cairo to depth-sort the path.
            count = 64 if dashed else 72
            portion = 0.60 if dashed else 1.0
            return VGroup(*[
                curve_piece(func, TAU * j / count,
                            TAU * (j + portion) / count,
                            color, width, opacity)
                for j in range(count)
            ])

        def rod(start, end, color=muted, width=1.3, opacity=1):
            start, end = np.array(start, dtype=float), np.array(end, dtype=float)
            return VGroup(*[
                Line(start + (end - start) * j / 6,
                     start + (end - start) * (j + 1) / 6,
                     color=color, stroke_width=width,
                     stroke_opacity=opacity).set_shade_in_3d(True)
                for j in range(6)
            ])

        def overlay(line1, line2="", formula=None, color=white, title=False):
            group = VGroup()
            for text, y, size in [
                (line1, -2.94, 38 if title else 32),
                (line2, -3.48, 30 if title else 32),
            ]:
                if text:
                    text = text.replace("\u00b7", "|").replace("11.3393", "11.3").replace("7.39005", "7.4")
                    item = Text(text, font_size=size, color=white)
                    if item.width > 12.9:
                        item.scale_to_fit_width(12.9)
                    item.move_to([0, y, 0])
                    group.add(item)
            if formula:
                eq = MathTex(formula, font_size=42, color=color)
                if eq.width > 12.7:
                    eq.scale_to_fit_width(12.7)
                eq.move_to([0, 3.24, 0])
                group.add(eq)
            group.set_z_index(100)
            return group

        def beat(seconds, line1, line2="", formula=None, color=white,
                 animations=(), camera=None, title=False):
            # Remove the previous caption before fading the new one in.
            # This keeps the two-line limit even during transitions.
            if self.hud is not None:
                self.remove(self.hud)
                self.remove_fixed_in_frame_mobjects(self.hud)
            self.hud = overlay(line1, line2, formula, color, title)
            self.add_fixed_in_frame_mobjects(self.hud)
            self.remove(self.hud)
            caption_anim = Succession(
                FadeIn(self.hud, run_time=0.24),
                Wait(seconds - 0.24),
            )
            actions = [caption_anim, *animations]
            if camera is None:
                self.play(*actions, run_time=seconds)
            else:
                self.move_camera(**camera, added_anims=actions, run_time=seconds)

        # A virtually orthographic explanatory camera preserves silhouette ratios.
        self.set_camera_orientation(
            phi=65 * DEGREES, theta=-55 * DEGREES,
            zoom=0.75, focal_distance=1e9, frame_center=ORIGIN,
        )
        star = ball(1, ivory, resolution=(32, 16), mesh=True)

        # 0--12: walk BACKWARD through the prerequisite constellation.
        positions = [
            np.array([0.0, 0.0, 3.1]),
            np.array([-3.2, -0.5, 1.4]),
            np.array([0.2, 2.1, 1.1]),
            np.array([3.2, 0.1, 1.2]),
            np.array([-2.6, -1.5, -0.7]),
            np.array([0.0, -1.0, -1.3]),
            np.array([2.7, 1.6, -0.9]),
        ]
        node_colors = [amber, amber, cyan, violet, ivory, amber, cyan]
        nodes = VGroup(*[
            ball(0.11 if j == 0 else 0.078, node_colors[j], point,
                 resolution=(8, 6))
            for j, point in enumerate(positions)
        ])
        pairs = [(0, 1), (0, 2), (0, 3),
                 (1, 4), (1, 5), (2, 5), (2, 6), (3, 4), (3, 6)]
        edges = VGroup(*[
            rod(positions[a], positions[b], muted, 1.15, 0.52)
            for a, b in pairs
        ])
        beat(2, "The third rhythm", "TOI-4342 · TIC 354944123",
             animations=[FadeIn(star)], title=True)
        beat(1.5, "A third planet?", animations=[FadeIn(nodes[0])])
        beat(2, "Repeated dimming", "Orbit + sightline",
             animations=[FadeIn(VGroup(nodes[1], nodes[2], edges[0], edges[1]))],
             camera=dict(theta=-45 * DEGREES))
        beat(1.5, "Rule out impostors", "Connections show prerequisites, not proof",
             animations=[FadeIn(VGroup(nodes[3], edges[2]))])
        beat(2.5, "Light + blocked area", "Period + phase",
             animations=[FadeIn(VGroup(nodes[4], nodes[5], edges[3],
                                       edges[4], edges[5], edges[7]))],
             camera=dict(theta=-35 * DEGREES))
        beat(2.5, "Projection + inclination", "Now build forward from light",
             animations=[FadeIn(VGroup(nodes[6], edges[6], edges[8])),
                         Indicate(nodes[4], color=ivory, scale_factor=1.35)])

        # 12--26: an accurately scaled planet blocks projected stellar area.
        # Only orbital distance is compressed in this local geometry model.
        # This inclination is constructed, NOT an observed orbital normal.
        demo_radius = 3.2
        inclination = math.acos(impact / demo_radius)
        ci, si = math.cos(inclination), math.sin(inclination)

        def orbit_point(radius, theta):
            return radius * np.array([
                math.sin(theta), ci * math.cos(theta), si * math.cos(theta)
            ])

        phase = ValueTracker(-0.37)
        candidate = ball(k, "#51371B", resolution=(16, 12))
        candidate.move_to(orbit_point(demo_radius, phase.get_value()))
        candidate.add_updater(
            lambda m: m.move_to(orbit_point(demo_radius, phase.get_value()))
        )
        stellar_outline = Circle(
            radius=1, color=ivory, stroke_width=1.1
        )
        planet_outline = Circle(radius=k, color=amber, stroke_width=1.1)
        planet_outline.add_updater(
            lambda m: m.move_to(candidate.get_center() + OUT * (k + 0.001))
        )
        beat(2, "Transit: a planet overlaps the star along our sightline",
             "A foreground body blocks some received light",
             animations=[FadeOut(VGroup(nodes, edges)),
                         FadeIn(candidate), FadeIn(stellar_outline),
                         FadeIn(planet_outline)],
             camera=dict(phi=0, theta=-90 * DEGREES, zoom=2.05))
        beat(4, "Depth: the fraction of received light blocked",
             "Planet-to-star radius ratio: 0.0337894",
             animations=[phase.animate.set_value(0)])
        beat(5, "Uniform-disk illustration", "About 1142 parts per million",
             formula=r"\delta\approx\left(R_p/R_\star\right)^2\approx0.001142",
             color=amber)
        beat(3, "Fitted duration: 2.45559 h",
             "Impact parameter: 0.746895 stellar radii",
             formula=r"R_p=2.207^{+0.112}_{-0.108}\,R_\oplus",
             color=amber, animations=[phase.animate.set_value(0.37)])

        # 26--39: observer-dependent overlap, normal, and projection.
        planet_outline.clear_updaters()
        demo_orbit = spatial_curve(
            lambda t: orbit_point(demo_radius, t), amber, dashed=True
        )
        observer_position = np.array([0.0, 0.0, 4.7])
        observer = VGroup(
            ball(0.075, white, observer_position, resolution=(8, 6)),
            spatial_curve(
                lambda t: observer_position + 0.20 * np.array(
                    [math.cos(t), math.sin(t), 0]),
                white, width=1.1
            )
        )
        sightline = rod([0, 0, 1.04], observer_position, white, 1.8, 0.8)
        projection_z = -1.24
        projection = spatial_curve(
            lambda t: np.array([demo_radius * math.sin(t),
                                impact * math.cos(t), projection_z]),
            muted, width=1.0, opacity=0.65,
        )
        projection_rays = VGroup(*[
            rod(orbit_point(demo_radius, t),
                [demo_radius * math.sin(t), impact * math.cos(t), projection_z],
                muted, 0.9, 0.35)
            for t in [0.5, 2.3, 3.9, 5.5]
        ])
        normal = np.array([0.0, -si, ci])
        normal_rod = rod(ORIGIN, 1.85 * normal, cyan, 2.0)
        normal_tip = ball(0.055, cyan, 1.85 * normal, resolution=(8, 4))
        inclination_arc = curve_piece(
            lambda t: 1.5 * np.array([0, -math.sin(t), math.cos(t)]),
            0, inclination, cyan, 2.0,
        )
        beat(4, "Sightline: direction toward the white observer",
             "Projection: depth collapsed along that direction",
             animations=[FadeOut(stellar_outline), FadeOut(planet_outline),
                         FadeIn(demo_orbit), FadeIn(observer), FadeIn(sightline),
                         FadeIn(projection), FadeIn(projection_rays),
                         candidate.animate.set_color(amber)],
             camera=dict(phi=65 * DEGREES, theta=15 * DEGREES, zoom=0.64))
        beat(4, "Inclination: angle between orbit normal and sightline",
             "90° is edge-on; this normal is illustrative",
             animations=[FadeIn(normal_rod), FadeIn(normal_tip),
                         Create(inclination_arc), phase.animate.set_value(PI)])
        beat(2.5, "Behind the star, the same planet still exists",
             "Distance compressed; explanatory camera off the sightline",
             camera=dict(theta=-5 * DEGREES))
        beat(2.5, "The orbit is circular in space",
             "Its projection along this sightline is an ellipse",
             animations=[projection.animate.set_stroke(color=white, opacity=0.9)])

        # 39--54: three clocks with exact relative distances and angular speeds.
        candidate.clear_updaters()
        colors = [cyan, violet, amber]
        rings = VGroup(*[
            spatial_curve(lambda t, r=r: orbit_point(r, t),
                          colors[j], dashed=(j == 2), width=1.8)
            for j, r in enumerate(orbit_radii)
        ])
        phases = [-0.7, 1.7, PI]
        overview_sizes = 0.11 * radii_earth / radii_earth[2]
        planet_b = ball(overview_sizes[0], cyan,
                        orbit_point(orbit_radii[0], phases[0]))
        planet_c = ball(overview_sizes[1], violet,
                        orbit_point(orbit_radii[1], phases[1]))
        geometry_aids = VGroup(
            demo_orbit, observer, sightline, projection, projection_rays,
            normal_rod, normal_tip, inclination_arc,
        )
        beat(3, "Circular orbits, phases and coplanarity illustrative",
             "Overview body sizes exaggerated",
             animations=[FadeOut(geometry_aids), FadeIn(rings),
                         star.animate.scale(0.45),
                         candidate.animate.scale(overview_sizes[2] / k).move_to(
                             orbit_point(orbit_radii[2], phases[2])),
                         FadeIn(planet_b), FadeIn(planet_c)],
             camera=dict(phi=58 * DEGREES, theta=-45 * DEGREES, zoom=0.60))
        clock = ValueTracker(0)
        clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(clock)
        planets = [planet_b, planet_c, candidate]
        for j, body in enumerate(planets):
            body.add_updater(
                lambda m, j=j: m.move_to(orbit_point(
                    orbit_radii[j], phases[j] + TAU * clock.get_value() / periods[j]
                ))
            )
        beat(2, "Period: time for one circuit", "Phase: position within that cycle")
        beat(2.5, "b · confirmed transiting planet",
             "Original radius: 2.266 Earth radii",
             formula=r"P_b=5.5382498\,\mathrm{d}", color=cyan,
             animations=[rings[0].animate.set_stroke(width=2.7)])
        beat(2.5, "c · confirmed transiting planet",
             "Original radius: 2.415 Earth radii",
             formula=r"P_c=10.688716\,\mathrm{d}", color=violet,
             animations=[rings[0].animate.set_stroke(width=1.8),
                         rings[1].animate.set_stroke(width=2.7)])
        beat(2.5, "candidate · residual transit signal",
             "Dashed orbit: a hypothesis",
             formula=r"P_{\rm candidate}=18.9082044035\,\mathrm{d}", color=amber,
             animations=[rings[1].animate.set_stroke(width=1.8),
                         rings[2].animate.set_stroke(width=2.7)])
        beat(2.5, "Model-derived distances (AU), in b / c / candidate order",
             "0.05252 / 0.08141 / 0.11907 · stellar mass: 0.63 solar",
             animations=[rings[2].animate.set_stroke(width=1.8)])

        # 54--64: schematic time samples, followed by exclusion, never subtraction.
        # Times, depths and mask widths below are explicitly illustrative.
        end_time = 3 * periods[2]
        event_times = [9.8 + j * periods[2] for j in range(3)]
        b_centers = np.arange(2.0, end_time, periods[0])
        c_centers = np.arange(4.0, end_time, periods[1])
        sample_times = sorted(set(
            [round(float(t), 8) for t in np.arange(0, end_time, 2.5)]
            + [round(float(t), 8) for t in b_centers]
            + [round(float(t), 8) for t in c_centers]
            + [round(float(t), 8) for t in event_times]
        ))

        def sample_position(t, dim=False):
            return np.array([3.4 + 0.090 * t, -1.05 + 0.20 * math.sin(t / 10),
                             0.2 + 0.024 * t - (0.36 if dim else 0)])

        beads, masked, retained, recurrence = VGroup(), [], [], []
        for t in sample_times:
            in_b = min(abs(t - q) for q in b_centers) < 0.45
            in_c = min(abs(t - q) for q in c_centers) < 0.55
            is_event = min(abs(t - q) for q in event_times) < 1e-6
            bead = ball(0.058, white, sample_position(t, in_b or in_c or is_event),
                        resolution=(8, 4))
            beads.add(bead)
            if in_b or in_c:
                masked.append((bead, cyan if in_b else violet))
            else:
                retained.append(bead)
            if is_event and not (in_b or in_c):
                recurrence.append(bead)

        brackets = VGroup()
        for t, color in [(b_centers[0], cyan), (c_centers[0], violet),
                         (b_centers[3], cyan), (c_centers[2], violet)]:
            p, q = sample_position(t - 0.7), sample_position(t + 0.7)
            lift = np.array([0.0, 0.0, 0.24])
            brackets.add(VGroup(
                rod(p, p + lift, color, 2),
                rod(p + lift, q + lift, color, 2),
                rod(q + lift, q, color, 2),
            ))
        beat(3, "Schematic brightness samples along time",
             "Lower beads illustrate dimming; no measured light curve",
             animations=[FadeIn(beads)],
             camera=dict(theta=-65 * DEGREES, zoom=0.66,
                         frame_center=[2.6, 0, 0]))
        beat(3, "Mask known b/c transit windows before searching",
             "Window widths are schematic",
             animations=[FadeIn(brackets)] + [
                 bead.animate.set_color(color) for bead, color in masked
             ])
        beat(4, "Excluded samples leave gaps",
             "Search only the retained samples",
             animations=[FadeOut(brackets)] + [
                 bead.animate.shift([0, -1.05, -0.58]).set_color(gray).set_opacity(0.42)
                 for bead, color in masked
             ])

        # 64--72: three illustrative cycles align; their count is not data.
        e1 = RIGHT
        e2 = np.array([0, 0.6, 0.8])
        cycle_normal = np.array([0, -0.8, 0.6])
        cycle_center = np.array([6.2, 0, 0.65])
        cycle_centers = [cycle_center + (j - 1) * (2.0 * e1 + 0.8 * cycle_normal)
                         for j in range(3)]
        cycles = VGroup(*[
            spatial_curve(
                lambda t, p=p: p + 0.73 * (
                    math.cos(t) * e1 + math.sin(t) * e2),
                amber, width=1.4, opacity=0.65,
            ) for p in cycle_centers
        ])
        other_beads = VGroup(*[bead for bead in beads if bead not in recurrence])
        beat(2, "Schematic phase folding: three illustrative cycles",
             "Not the observed transit count",
             animations=[FadeIn(cycles), other_beads.animate.set_opacity(0.17)] + [
                 bead.animate.set_color(amber).scale(1.3).move_to(p + 0.73 * e1)
                 for bead, p in zip(recurrence, cycle_centers)
             ])
        beat(3, "Repeated dimming aligns at one phase",
             "Equal time intervals suggest an orbital clock",
             formula=r"P_{\rm candidate}\approx18.9082\,\mathrm{d}", color=amber,
             animations=[
                 cycles[j].animate.shift(cycle_center - cycle_centers[j])
                 for j in range(3)
             ] + [
                 bead.animate.move_to(cycle_center + 0.73 * e1)
                 for bead in recurrence
             ])
        beat(3, "A separate TOI-host search recovers this rhythm",
             "Another search of existing data",
             formula=r"P_{\rm candidate}\approx18.9082\,\mathrm{d}", color=amber,
             animations=[rings[2].animate.set_stroke(width=3.0)])

        # 72--86: sector count, signal strength, contamination, model limits.
        evidence_positions = [
            [2.6, -0.7, 0.6], [3.3, -0.3, 1.2], [4.0, -0.8, 0.8],
            [4.7, -0.1, 1.6], [2.8, 0.7, 1.5], [3.5, 1.0, 0.4],
            [4.2, 0.7, 1.1], [4.9, 1.0, 0.5],
        ]
        evidence = VGroup(*[
            ball(0.085, amber, p, resolution=(8, 6))
            for p in evidence_positions
        ])
        beat(4, "Sector = observing interval; 8 sectors, 9 LEO transits",
             "13, 27, 66, 67, 93, 101, 102, 103",
             animations=[FadeOut(beads), FadeOut(cycles), FadeIn(evidence),
                         rings[2].animate.set_stroke(width=1.8),
                         FadeIn(VGroup(nodes[0], nodes[3], edges[2]))],
             camera=dict(theta=0, zoom=0.66, frame_center=[1.4, 0, 0.3]))
        beat(2, "Signal-to-noise: old 11.3393 · new 7.39005",
             "Repetition alone cannot rule out an impostor")

        neighbor_position = np.array([5.2, 2.0, 0.2])
        neighbor = ball(0.09, muted, neighbor_position, resolution=(8, 6))
        blend_ray = rod(neighbor_position, observer_position, muted, 1.3, 0.6)
        beat(3, "Nearest listed capable neighbor: 38.248 arcsec",
             "Schematic ray; centroids do not fully localize the signal",
             animations=[FadeIn(neighbor), FadeIn(blend_ray), FadeIn(observer)])
        beat(5, "False-positive probability under tested models",
             "Gaia-constrained mean; above the validation threshold",
             formula=r"\mathrm{FPP}=0.11135>0.015", color=amber,
             animations=[FadeOut(neighbor), FadeOut(blend_ray), FadeOut(observer)])

        # 86--94: return to the unresolved root. The final three seconds are still.
        clock.clear_updaters()
        for body in planets:
            body.clear_updaters()
        beat(2, "A candidate. Confirmation still needed.",
             animations=[FadeOut(evidence),
                         FadeOut(VGroup(nodes[0], nodes[3], edges[2]))],
             camera=dict(phi=65 * DEGREES, theta=-35 * DEGREES,
                         zoom=0.63, frame_center=[0.6, 0, 0.3]))
        beat(3, "A candidate. Confirmation still needed.",
             "Follow-up: ground photometry · high-resolution imaging · RVs")
        self.wait(3)
