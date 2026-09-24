"""THE THIRD SIDE — silent 40-second film; render class: TheThirdSide.

Self-contained Manim Community Edition source. All lengths use one scale.
This file deliberately contains no render invocation or external asset access.
"""

from manim import *
import numpy as np


class TheThirdSide(ThreeDScene):
    def construct(self):
        self.camera.background_color = "#080F20"
        teal, gold, lavender = "#42DDD0", "#FFD17A", "#B9A5FF"
        ivory, white, wire_color = "#F7F4E9", "#F0F3FA", "#64758F"
        scale = 0.52
        center = np.array([1.5, 2.0, 3.0])

        def point(xyz):
            return scale * (np.array(xyz, dtype=float) - center)

        raw = {
            "A": (0, 0, 0), "B": (3, 0, 0), "C": (3, 4, 0),
            "E": (0, 4, 0), "F": (0, 0, 6), "G": (3, 0, 6),
            "D": (3, 4, 6), "H": (0, 4, 6),
        }
        p = {key: point(value) for key, value in raw.items()}

        def edge(a, b, color, width, opacity=1.0, layer=2):
            return Line(p[a], p[b], color=color, stroke_width=width,
                        stroke_opacity=opacity).set_z_index(layer)

        def marker(vertices):
            result = VMobject(color=ivory, stroke_width=2.0)
            result.set_points_as_corners([point(v) for v in vertices])
            return result.set_z_index(5)

        def caption(words, y=-2.95, size=34, colors=None):
            obj = Text(words, font="Segoe UI", font_size=size,
                       color=white, t2c=colors or {}, disable_ligatures=True)
            # Uniform glyph fitting, with full bounds inside the safe bands.
            max_height = 0.46 if size <= 24 else 0.60
            obj.scale(min(1.0, 12.0 / max(obj.width, 0.001),
                          max_height / max(obj.height, 0.001)))
            obj.move_to([0, y, 0]).set_z_index(20)
            # Keep camera registration while leaving introduction to FadeIn.
            self.add_fixed_in_frame_mobjects(obj)
            self.remove(obj)
            return obj

        def delayed(delay, animation):
            if delay == 0:
                return animation
            return Succession(Wait(delay), animation, rate_func=linear)

        def timeline(duration, *events):
            # The final Wait fixes group length so gaps never rescale cues.
            return AnimationGroup(
                *(delayed(start, animation) for start, animation in events),
                Wait(duration), lag_ratio=0, run_time=duration,
                rate_func=linear,
            )

        def play_timeline(duration, *events):
            self.play(timeline(duration, *events), run_time=duration,
                      rate_func=linear)

        def stroke(obj, duration, **style):
            # ApplyMethod creates its target when the scheduled cue begins.
            return ApplyMethod(obj.set_stroke, style, run_time=duration)

        def replace(old, new, duration=0.6):
            return Succession(FadeOut(old, run_time=duration / 2),
                              FadeIn(new, run_time=duration / 2),
                              rate_func=linear)

        floor_outline = VGroup(*[
            edge(a, b, wire_color, 1.6, 0.50, -5)
            for a, b in [("A", "B"), ("B", "C"), ("C", "E"), ("E", "A")]
        ])
        box = VGroup(*[
            edge(a, b, wire_color, 1.6, 0.50, -5)
            for a, b in [("A", "F"), ("B", "G"), ("E", "H"),
                         ("F", "G"), ("G", "D"), ("D", "H"), ("H", "F")]
        ])
        ab = edge("A", "B", teal, 3.2)
        bc = edge("B", "C", teal, 3.2)
        ac = edge("A", "C", gold, 4.0)
        cd = edge("C", "D", lavender, 3.5)
        ad = edge("A", "D", gold, 5.0, layer=3)
        floor_plane = Polygon(p["A"], p["B"], p["C"],
                              fill_color=teal, fill_opacity=0.12,
                              stroke_width=0).set_z_index(-10)
        upright_plane = Polygon(p["A"], p["C"], p["D"],
                                fill_color=lavender, fill_opacity=0.10,
                                stroke_width=0).set_z_index(-9)
        floor_marker = marker([(2.8, 0, 0), (2.8, 0.2, 0), (3, 0.2, 0)])
        upright_marker = marker([(2.88, 3.84, 0), (2.88, 3.84, 0.2), (3, 4, 0.2)])
        endpoints = VGroup(*[
            Dot3D(p[k], radius=0.035, color=ivory, resolution=(8, 16))
            .set_z_index(6) for k in ("A", "D")
        ])

        title = caption("THE THIRD SIDE", y=3.13, size=34)
        first_edge = caption("Floor edge: 3", size=27, colors={"3": teal})
        floor_edges = caption("Floor edges: 3 and 4", size=27,
                              colors={"3": teal, "4": teal})
        floor_squared = caption("d² = 3² + 4² = 25",
                                colors={"d": gold, "3²": teal, "4²": teal})
        floor_length = caption("d = √25 = 5", colors={"d": gold, "√25": gold, "[10:11]": gold})
        shared_head = caption("The same 5 becomes a leg", y=3.13, size=29)
        shared = caption("Floor diagonal 5 · Height 6", size=27,
                         colors={"5": gold, "6": lavender})
        interior_head = caption("Through the interior", y=3.13, size=29)
        interior_squared = caption("L² = 5² + 6² = 61",
                                   colors={"L": gold, "5²": gold, "6²": lavender})
        interior_length = caption("L = √61 ≈ 7.81 units",
                                  colors={"L": gold, "√61": gold, "7.81": gold})
        same_head = caption("Same start. Same finish.", y=3.13, size=29)
        edge_sum = caption("Edge walk: 3 + 4 + 6 = 13 units", size=30,
                           colors={"3 + 4": teal, "6": lavender})
        shortest_head = caption("The straight connection is shortest", y=3.13, size=29)
        comparison = caption("Edge walk 13 · Interior ≈ 7.81 units", size=30,
                             colors={"7.81": gold})
        hero_title = caption("THE THIRD SIDE", y=3.13, size=34)
        hero_context = caption("Floor diagonal 5 · Height 6", y=-2.66, size=24,
                               colors={"5": gold, "6": lavender})
        hero_result = caption("L = √61 ≈ 7.81 units", y=-3.23, size=34,
                              colors={"L": gold, "√61": gold, "7.81": gold})

        self.set_camera_orientation(phi=26 * DEGREES, theta=-65 * DEGREES,
                                    gamma=0, zoom=1.65, focal_distance=30,
                                    frame_center=np.array([0, 0, -1.56]))

        # s01 | 0–4: each numeral follows the start of its corresponding edge.
        play_timeline(4.0,
            (0.0, FadeIn(title, floor_outline, run_time=0.4)),
            (0.4, Create(ab, run_time=0.8)),
            (0.7, FadeIn(first_edge, run_time=0.3)),
            (1.2, Create(bc, run_time=0.9)),
            (1.5, replace(first_edge, floor_edges, 0.5)),
            (2.3, Create(ac, run_time=0.7)),
            (3.0, FadeIn(floor_plane, run_time=0.4)),
            (3.0, Create(floor_marker, run_time=0.4)))

        # s02 | 4–8: geometry identifies the terms before the equation.
        play_timeline(4.0,
            (0.0, stroke(ab, 0.45, width=3.8)),
            (0.0, stroke(bc, 0.45, width=3.8)),
            (0.0, stroke(floor_marker, 0.45, width=2.3)),
            (0.45, stroke(ab, 0.45, width=3.2)),
            (0.45, stroke(bc, 0.45, width=3.2)),
            (0.45, stroke(floor_marker, 0.45, width=2.0)),
            (0.45, stroke(ac, 0.45, width=4.6)),
            (0.9, replace(floor_edges, floor_squared, 0.6)))

        # s03 | 8–11: the earned positive length, followed by a 2.4 s hold.
        play_timeline(3.0,
            (0.0, replace(floor_squared, floor_length, 0.6)),
            (0.0, stroke(ac, 0.6, width=4.0)))

        # s04 | 11–16: camera and construction share the SAME three seconds.
        self.play(replace(title, shared_head, 0.5))
        self.move_camera(phi=54 * DEGREES, theta=-54 * DEGREES,
                         gamma=0, zoom=1.0, frame_center=ORIGIN,
                         run_time=3.0, rate_func=smooth,
                         added_anims=[timeline(3.0,
                             (0.0, Create(cd, run_time=2.5)),
                             (0.5, replace(floor_length, shared, 0.6)),
                             (1.1, FadeIn(box, run_time=1.4)),
                             (2.0, FadeIn(endpoints, run_time=0.5)),
                             (2.5, Create(upright_marker, run_time=0.5)))])
        self.wait(1.5)

        # s05 | 16–20: close the interior triangle, then pause before notation.
        self.move_camera(phi=61 * DEGREES, theta=-42 * DEGREES,
                         gamma=0, zoom=1.0, frame_center=ORIGIN,
                         run_time=2.5, rate_func=smooth,
                         added_anims=[timeline(2.5,
                             (0.0, replace(shared_head, interior_head, 0.5)),
                             (0.5, Create(ad, run_time=1.4)),
                             (0.5, stroke(ac, 1.4, width=2.8, opacity=0.85)),
                             (1.9, FadeIn(upright_plane, run_time=0.6)))])
        self.wait(1.5)

        # s06 | 20–23: the second marked right angle earns a second equation.
        play_timeline(3.0,
            (0.0, FadeOut(shared, run_time=0.2)),
            (0.0, stroke(ac, 0.2, width=3.3, opacity=1.0)),
            (0.0, stroke(cd, 0.2, width=4.0)),
            (0.0, stroke(upright_marker, 0.2, width=2.3)),
            (0.2, stroke(ac, 0.2, width=2.8, opacity=0.85)),
            (0.2, stroke(cd, 0.2, width=3.5)),
            (0.2, stroke(upright_marker, 0.2, width=2.0)),
            (0.2, stroke(ad, 0.2, width=5.5)),
            (0.4, FadeIn(interior_squared, run_time=0.2)))

        # s07 | 23–26: exact answer and rounded value remain distinct.
        play_timeline(3.0,
            (0.0, replace(interior_squared, interior_length, 0.6)),
            (0.0, stroke(ad, 0.6, width=5.0)))

        # s08 | 26–32: one walker follows A–B–C–D, never the shared AC.
        walker = Dot3D(p["A"], radius=0.045, color=ivory,
                       resolution=(8, 16)).set_z_index(7)
        self.add(walker)
        route_motion = Succession(
            MoveAlongPath(walker, Line(p["A"], p["B"]), run_time=0.7, rate_func=linear),
            MoveAlongPath(walker, Line(p["B"], p["C"]), run_time=0.92, rate_func=linear),
            MoveAlongPath(walker, Line(p["C"], p["D"]), run_time=1.38, rate_func=linear),
            rate_func=linear)
        play_timeline(3.0,
            (0.0, replace(interior_head, same_head, 0.5)),
            (0.0, FadeOut(interior_length, run_time=0.25)),
            (0.0, stroke(ad, 0.5, opacity=0.4)),
            (0.0, route_motion),
            (0.0, stroke(ab, 0.7, width=4.2)),
            (0.7, stroke(bc, 0.92, width=4.2)),
            (1.62, stroke(cd, 1.38, width=4.3)))
        self.remove(walker)
        self.play(FadeIn(edge_sum, run_time=0.6))
        self.wait(2.4)

        # s09 | 32–36: shortestness is a geometric fact, with a comparison.
        play_timeline(0.6,
            (0.0, replace(same_head, shortest_head, 0.6)),
            (0.0, replace(edge_sum, comparison, 0.6)),
            (0.0, stroke(ad, 0.6, width=5.0, opacity=1.0)),
            (0.0, stroke(ab, 0.6, width=3.2)),
            (0.0, stroke(bc, 0.6, width=3.2)),
            (0.0, stroke(cd, 0.6, width=3.5)))
        self.move_camera(phi=58 * DEGREES, theta=-48 * DEGREES,
                         gamma=0, zoom=1.0, frame_center=ORIGIN,
                         run_time=2.9, rate_func=smooth)
        self.wait(0.5)

        # s10 | 36–40: settled proof, exact answer, no fade to black.
        play_timeline(0.5,
            (0.0, replace(shortest_head, hero_title, 0.5)),
            (0.0, FadeOut(comparison, run_time=0.25)),
            (0.25, FadeIn(hero_context, hero_result, run_time=0.25)))
        self.wait(3.5)
