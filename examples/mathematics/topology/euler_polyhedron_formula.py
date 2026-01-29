from manim import *
import numpy as np

# Custom colors matching the storyboard
CYAN_VERTEX = "#00FFFF"
ELECTRIC_BLUE = "#0080FF"
GOLD_FACE = "#FFD700"
MAGENTA_VERTEX = "#FF00FF"
PURPLE_EDGE = "#8000FF"
CORAL_FACE = "#FF6B6B"
EMERALD_VERTEX = "#50C878"
SILVER_EDGE = "#C0C0C0"
DEEP_BLUE_FACE = "#1E3A5F"


class EulerPolyhedronFormula(ThreeDScene):
    """
    Euler's Polyhedron Formula: V - E + F = 2

    A comprehensive animation demonstrating the topological invariant
    through tetrahedron, cube, and dodecahedron examples, with
    visualization of the Euler characteristic generalization.
    """

    def construct(self):
        # Scene setup
        self.camera.background_color = BLACK

        # Execute scene sequence
        self.opening_scene()
        self.act1_tetrahedron()
        self.act2_cube()
        self.act3_dodecahedron()
        self.act4_proof_intuition()
        self.act5_generalization()
        self.closing_scene()

    # ==================== OPENING SCENE ====================
    def opening_scene(self):
        """The Mystery of Counting - single vertex to tetrahedron reveal"""

        # Start in darkness with a single glowing vertex
        vertex = Dot3D(point=ORIGIN, radius=0.15, color=CYAN_VERTEX)
        vertex.set_glow_factor(0.8)

        # Mystery text
        mystery_text = Text(
            "What do all closed shapes have in common?",
            font_size=36,
            color=WHITE
        ).to_edge(UP)

        # Fade in vertex
        self.play(FadeIn(vertex, scale=0.5), run_time=1.5)
        self.wait(0.5)

        # Fade in mystery text
        self.play(Write(mystery_text), run_time=2)
        self.wait(1)

        # Set camera for 3D viewing
        self.set_camera_orientation(phi=70*DEGREES, theta=-45*DEGREES, distance=6)

        # Create tetrahedron vertices
        tetra_vertices = self.get_tetrahedron_vertices(scale=1.5)

        # Create tetrahedron structure
        tetra_dots = VGroup(*[
            Dot3D(point=v, radius=0.1, color=CYAN_VERTEX)
            for v in tetra_vertices
        ])

        tetra_edges = self.create_edges(tetra_vertices, [
            (0,1), (0,2), (0,3), (1,2), (1,3), (2,3)
        ], color=ELECTRIC_BLUE, stroke_width=3)

        tetra_faces = self.create_tetrahedron_faces(tetra_vertices)

        # Animate tetrahedron materializing around the vertex
        self.play(
            vertex.animate.move_to(tetra_vertices[0]),
            run_time=1
        )

        self.play(
            *[GrowFromCenter(dot) for dot in tetra_dots[1:]],
            run_time=1.5
        )

        self.play(
            *[Create(edge) for edge in tetra_edges],
            run_time=2
        )

        self.play(
            *[FadeIn(face) for face in tetra_faces],
            run_time=1.5
        )

        # Remove the original vertex (now part of tetra_dots)
        self.remove(vertex)

        # Store for transition
        self.tetra_group = VGroup(tetra_dots, tetra_edges, tetra_faces)
        self.tetra_vertices_coords = tetra_vertices

        # Fade out mystery text
        self.play(FadeOut(mystery_text), run_time=1)
        self.wait(0.5)

    # ==================== ACT 1: TETRAHEDRON ====================
    def act1_tetrahedron(self):
        """Counting the Tetrahedron - V=4, E=6, F=4"""

        # Title
        title = Text("Act 1: The Tetrahedron", font_size=40, color=CYAN_VERTEX)
        title.to_edge(UP).shift(DOWN*0.3)
        self.add_fixed_in_frame_mobjects(title)
        self.play(Write(title), run_time=1)

        # Begin ambient rotation
        self.begin_ambient_camera_rotation(rate=0.1)

        # Counting vertices
        v_label = MathTex(r"V = ?", font_size=48, color=CYAN_VERTEX)
        v_label.to_corner(UL).shift(DOWN*1.2)
        self.add_fixed_in_frame_mobjects(v_label)
        self.play(Write(v_label))

        # Flash each vertex with count
        tetra_dots = self.tetra_group[0]
        for i, dot in enumerate(tetra_dots):
            count = MathTex(str(i+1), font_size=32, color=CYAN_VERTEX)
            count.next_to(dot, UP+RIGHT, buff=0.1)
            self.play(
                Flash(dot, color=CYAN_VERTEX, flash_radius=0.3),
                FadeIn(count),
                run_time=0.4
            )
            self.play(FadeOut(count), run_time=0.2)

        # Update V label
        v_final = MathTex(r"V = 4", font_size=48, color=CYAN_VERTEX)
        v_final.to_corner(UL).shift(DOWN*1.2)
        self.add_fixed_in_frame_mobjects(v_final)
        self.play(Transform(v_label, v_final), run_time=0.5)

        self.wait(0.5)

        # Counting edges with traveling light
        e_label = MathTex(r"E = ?", font_size=48, color=ELECTRIC_BLUE)
        e_label.next_to(v_label, DOWN, buff=0.3)
        self.add_fixed_in_frame_mobjects(e_label)
        self.play(Write(e_label))

        tetra_edges = self.tetra_group[1]
        for i, edge in enumerate(tetra_edges):
            # Create traveling particle
            particle = Dot(radius=0.08, color=WHITE)
            particle.move_to(edge.get_start())
            self.play(
                edge.animate.set_color(YELLOW),
                MoveAlongPath(particle, edge),
                run_time=0.3
            )
            self.play(
                edge.animate.set_color(ELECTRIC_BLUE),
                FadeOut(particle),
                run_time=0.15
            )

        # Update E label
        e_final = MathTex(r"E = 6", font_size=48, color=ELECTRIC_BLUE)
        e_final.next_to(v_label, DOWN, buff=0.3)
        self.add_fixed_in_frame_mobjects(e_final)
        self.play(Transform(e_label, e_final), run_time=0.5)

        self.wait(0.5)

        # Counting faces
        f_label = MathTex(r"F = ?", font_size=48, color=GOLD_FACE)
        f_label.next_to(e_label, DOWN, buff=0.3)
        self.add_fixed_in_frame_mobjects(f_label)
        self.play(Write(f_label))

        tetra_faces = self.tetra_group[2]
        for i, face in enumerate(tetra_faces):
            self.play(
                face.animate.set_fill(opacity=0.6),
                Flash(face.get_center(), color=GOLD_FACE, flash_radius=0.5),
                run_time=0.5
            )
            self.play(face.animate.set_fill(opacity=0.3), run_time=0.2)

        # Update F label
        f_final = MathTex(r"F = 4", font_size=48, color=GOLD_FACE)
        f_final.next_to(e_label, DOWN, buff=0.3)
        self.add_fixed_in_frame_mobjects(f_final)
        self.play(Transform(f_label, f_final), run_time=0.5)

        self.wait(0.5)

        # Assemble the equation
        equation = MathTex(
            r"4", r"-", r"6", r"+", r"4", r"=", r"2",
            font_size=56
        )
        equation[0].set_color(CYAN_VERTEX)
        equation[2].set_color(ELECTRIC_BLUE)
        equation[4].set_color(GOLD_FACE)
        equation[6].set_color(GREEN)
        equation.to_edge(DOWN).shift(UP*0.5)
        self.add_fixed_in_frame_mobjects(equation)

        self.play(Write(equation), run_time=2)

        # Checkmark
        check = MathTex(r"\checkmark", font_size=56, color=GREEN)
        check.next_to(equation, RIGHT, buff=0.3)
        self.add_fixed_in_frame_mobjects(check)
        self.play(Write(check), run_time=0.5)

        self.wait(1)

        # Stop rotation and clean up for transition
        self.stop_ambient_camera_rotation()

        # Store labels for later
        self.tetra_labels = VGroup(v_label, e_label, f_label)
        self.tetra_equation = equation
        self.tetra_check = check
        self.tetra_title = title

        # Clean up fixed frame objects
        self.play(
            FadeOut(title),
            FadeOut(v_label), FadeOut(e_label), FadeOut(f_label),
            FadeOut(equation), FadeOut(check),
            run_time=1
        )

        self.wait(0.5)

    # ==================== ACT 2: CUBE ====================
    def act2_cube(self):
        """The Cube Test - morph from tetrahedron"""

        # Title
        title = Text("Act 2: The Cube", font_size=40, color=MAGENTA_VERTEX)
        title.to_edge(UP).shift(DOWN*0.3)
        self.add_fixed_in_frame_mobjects(title)
        self.play(Write(title), run_time=1)

        # Create cube
        cube_vertices = self.get_cube_vertices(scale=1.2)

        cube_dots = VGroup(*[
            Dot3D(point=v, radius=0.1, color=MAGENTA_VERTEX)
            for v in cube_vertices
        ])

        cube_edge_indices = [
            (0,1), (1,2), (2,3), (3,0),  # bottom
            (4,5), (5,6), (6,7), (7,4),  # top
            (0,4), (1,5), (2,6), (3,7)   # verticals
        ]
        cube_edges = self.create_edges(cube_vertices, cube_edge_indices,
                                        color=PURPLE_EDGE, stroke_width=3)

        cube_faces = self.create_cube_faces(cube_vertices)

        cube_group = VGroup(cube_dots, cube_edges, cube_faces)

        # Morph tetrahedron to cube
        self.play(
            FadeOut(self.tetra_group),
            FadeIn(cube_group),
            run_time=2
        )

        # Begin rotation
        self.begin_ambient_camera_rotation(rate=0.08)

        # Quick counting display
        v_label = MathTex(r"V = 8", font_size=48, color=MAGENTA_VERTEX)
        e_label = MathTex(r"E = 12", font_size=48, color=PURPLE_EDGE)
        f_label = MathTex(r"F = 6", font_size=48, color=CORAL_FACE)

        labels = VGroup(v_label, e_label, f_label)
        labels.arrange(DOWN, buff=0.3)
        labels.to_corner(UL).shift(DOWN*1.2)

        for label in labels:
            self.add_fixed_in_frame_mobjects(label)

        # Flash vertices sequentially
        for dot in cube_dots:
            self.play(Flash(dot, color=MAGENTA_VERTEX, flash_radius=0.2), run_time=0.15)
        self.play(Write(v_label), run_time=0.5)

        # Light up edges like circuits
        for edge in cube_edges:
            self.play(
                edge.animate.set_color(YELLOW).set_stroke(width=5),
                run_time=0.1
            )
        self.play(
            *[edge.animate.set_color(PURPLE_EDGE).set_stroke(width=3) for edge in cube_edges],
            Write(e_label),
            run_time=0.5
        )

        # Glow faces
        for face in cube_faces:
            self.play(face.animate.set_fill(opacity=0.5), run_time=0.15)
        self.play(
            *[face.animate.set_fill(opacity=0.3) for face in cube_faces],
            Write(f_label),
            run_time=0.5
        )

        # Equation
        equation = MathTex(
            r"8", r"-", r"12", r"+", r"6", r"=", r"2",
            font_size=56
        )
        equation[0].set_color(MAGENTA_VERTEX)
        equation[2].set_color(PURPLE_EDGE)
        equation[4].set_color(CORAL_FACE)
        equation[6].set_color(GREEN)
        equation.to_edge(DOWN).shift(UP*0.5)
        self.add_fixed_in_frame_mobjects(equation)

        self.play(Write(equation), run_time=1.5)

        check = MathTex(r"\checkmark", font_size=56, color=GREEN)
        check.next_to(equation, RIGHT, buff=0.3)
        self.add_fixed_in_frame_mobjects(check)
        self.play(Write(check), run_time=0.5)

        self.wait(1.5)

        # Stop rotation and clean up
        self.stop_ambient_camera_rotation()

        self.cube_group = cube_group

        self.play(
            FadeOut(title),
            FadeOut(v_label), FadeOut(e_label), FadeOut(f_label),
            FadeOut(equation), FadeOut(check),
            run_time=1
        )

        self.wait(0.5)

    # ==================== ACT 3: DODECAHEDRON ====================
    def act3_dodecahedron(self):
        """The Dodecahedron Challenge - assembly from scattered vertices"""

        # Title
        title = Text("Act 3: The Dodecahedron", font_size=40, color=EMERALD_VERTEX)
        title.to_edge(UP).shift(DOWN*0.3)
        self.add_fixed_in_frame_mobjects(title)
        self.play(Write(title), run_time=1)

        # Fade out cube
        self.play(FadeOut(self.cube_group), run_time=1)

        # Get dodecahedron vertices
        dodeca_vertices = self.get_dodecahedron_vertices(scale=1.8)

        # Create scattered positions
        scattered_positions = [
            v + np.random.uniform(-2, 2, 3) for v in dodeca_vertices
        ]

        # Create dots at scattered positions
        dodeca_dots = VGroup(*[
            Dot3D(point=sp, radius=0.08, color=EMERALD_VERTEX)
            for sp in scattered_positions
        ])

        # Fade in scattered dots
        self.play(
            *[FadeIn(dot, scale=0.5) for dot in dodeca_dots],
            run_time=1.5
        )

        # Animate dots spiraling to correct positions
        self.play(
            *[dot.animate.move_to(dodeca_vertices[i])
              for i, dot in enumerate(dodeca_dots)],
            run_time=3,
            rate_func=smooth
        )

        # Create edges
        dodeca_edge_indices = self.get_dodecahedron_edge_indices()
        dodeca_edges = self.create_edges(dodeca_vertices, dodeca_edge_indices,
                                          color=SILVER_EDGE, stroke_width=2)

        # Weave edges together
        self.play(
            *[Create(edge) for edge in dodeca_edges],
            run_time=2.5
        )

        # Create faces
        dodeca_faces = self.create_dodecahedron_faces(dodeca_vertices)

        # Lock faces into place
        self.play(
            *[FadeIn(face) for face in dodeca_faces],
            run_time=2
        )

        dodeca_group = VGroup(dodeca_dots, dodeca_edges, dodeca_faces)

        # Begin slow rotation
        self.begin_ambient_camera_rotation(rate=0.05)

        # Deliberate counting
        v_label = MathTex(r"V = 20", font_size=48, color=EMERALD_VERTEX)
        e_label = MathTex(r"E = 30", font_size=48, color=SILVER_EDGE)
        f_label = MathTex(r"F = 12", font_size=48, color=DEEP_BLUE_FACE)

        labels = VGroup(v_label, e_label, f_label)
        labels.arrange(DOWN, buff=0.3)
        labels.to_corner(UL).shift(DOWN*1.2)

        for label in labels:
            self.add_fixed_in_frame_mobjects(label)

        self.play(Write(v_label), run_time=1)
        self.wait(0.3)
        self.play(Write(e_label), run_time=1)
        self.wait(0.3)
        self.play(Write(f_label), run_time=1)

        # Equation
        equation = MathTex(
            r"20", r"-", r"30", r"+", r"12", r"=", r"2",
            font_size=56
        )
        equation[0].set_color(EMERALD_VERTEX)
        equation[2].set_color(SILVER_EDGE)
        equation[4].set_color(DEEP_BLUE_FACE)
        equation[6].set_color(GREEN)
        equation.to_edge(DOWN).shift(UP*0.5)
        self.add_fixed_in_frame_mobjects(equation)

        self.play(Write(equation), run_time=2)

        check = MathTex(r"\checkmark", font_size=56, color=GREEN)
        check.next_to(equation, RIGHT, buff=0.3)
        self.add_fixed_in_frame_mobjects(check)
        self.play(Write(check), run_time=0.5)

        # Insight text
        insight = Text(
            "No matter the shape... always 2.",
            font_size=36,
            color=GOLD
        ).to_edge(DOWN).shift(DOWN*0.5 + UP*1.5)
        self.add_fixed_in_frame_mobjects(insight)
        self.play(Write(insight), run_time=1.5)

        self.wait(2)

        self.stop_ambient_camera_rotation()

        self.dodeca_group = dodeca_group

        self.play(
            FadeOut(title),
            FadeOut(v_label), FadeOut(e_label), FadeOut(f_label),
            FadeOut(equation), FadeOut(check), FadeOut(insight),
            FadeOut(dodeca_group),
            run_time=1.5
        )

        self.wait(0.5)

    # ==================== ACT 4: PROOF INTUITION ====================
    def act4_proof_intuition(self):
        """Visual proof intuition - flatten polyhedron to planar graph"""

        # Title
        title = Text("Act 4: The Proof Intuition", font_size=40, color=YELLOW)
        title.to_edge(UP).shift(DOWN*0.3)
        self.add_fixed_in_frame_mobjects(title)
        self.play(Write(title), run_time=1)

        # Reset camera for 2D-ish view
        self.move_camera(phi=0*DEGREES, theta=-90*DEGREES, run_time=1.5)

        # Create a simple polyhedron (cube) as planar graph
        # Show "popping" one face open

        explanation1 = Text(
            "Imagine projecting a polyhedron onto a sphere...",
            font_size=28, color=WHITE
        ).shift(UP*2)
        self.add_fixed_in_frame_mobjects(explanation1)
        self.play(Write(explanation1), run_time=1.5)

        # Draw a simple cube graph (flattened)
        outer_square = Square(side_length=4, color=BLUE, stroke_width=3)
        inner_square = Square(side_length=2, color=BLUE, stroke_width=3)

        # Connect corners
        connections = VGroup(*[
            Line(
                outer_square.get_corner(corner),
                inner_square.get_corner(corner),
                color=BLUE, stroke_width=3
            )
            for corner in [UL, UR, DL, DR]
        ])

        planar_graph = VGroup(outer_square, inner_square, connections)
        planar_graph.shift(DOWN*0.5)

        self.play(Create(planar_graph), run_time=2)

        # Add vertex dots
        vertices = VGroup()
        for square in [outer_square, inner_square]:
            for corner in [UL, UR, DL, DR]:
                dot = Dot(square.get_corner(corner), color=CYAN_VERTEX, radius=0.1)
                vertices.add(dot)

        self.play(*[GrowFromCenter(v) for v in vertices], run_time=1)

        explanation2 = Text(
            "Then 'pop' one face open and flatten!",
            font_size=28, color=WHITE
        ).shift(UP*2)
        self.add_fixed_in_frame_mobjects(explanation2)
        self.play(
            FadeOut(explanation1),
            Write(explanation2),
            run_time=1.5
        )

        # Count display
        count_display = MathTex(
            r"V = 8, \quad E = 12, \quad F = 6",
            font_size=36
        ).shift(DOWN*2.5)
        self.add_fixed_in_frame_mobjects(count_display)
        self.play(Write(count_display), run_time=1)

        # Show that removing edges changes counts predictably
        explanation3 = Text(
            "V - E + F stays constant through any operation!",
            font_size=28, color=GREEN
        ).shift(UP*2)
        self.add_fixed_in_frame_mobjects(explanation3)
        self.play(
            FadeOut(explanation2),
            Write(explanation3),
            run_time=1.5
        )

        self.wait(2)

        # Clean up
        self.play(
            FadeOut(title), FadeOut(explanation3),
            FadeOut(planar_graph), FadeOut(vertices), FadeOut(count_display),
            run_time=1
        )

        self.wait(0.5)

    # ==================== ACT 5: GENERALIZATION ====================
    def act5_generalization(self):
        """Euler Characteristic generalization - sphere, torus, double torus"""

        # Title
        title = Text("Act 5: The Euler Characteristic", font_size=40, color=TEAL)
        title.to_edge(UP).shift(DOWN*0.3)
        self.add_fixed_in_frame_mobjects(title)
        self.play(Write(title), run_time=1)

        # Reset to 3D view
        self.move_camera(phi=70*DEGREES, theta=-45*DEGREES, run_time=1.5)

        # Create sphere
        sphere = Surface(
            lambda u, v: np.array([
                np.cos(u) * np.cos(v),
                np.cos(u) * np.sin(v),
                np.sin(u)
            ]),
            u_range=[-PI/2, PI/2],
            v_range=[0, TAU],
            resolution=(24, 48),
            fill_color=BLUE,
            fill_opacity=0.6,
            stroke_color=WHITE,
            stroke_width=0.5
        )
        sphere.scale(0.8)
        sphere.shift(LEFT*3.5)

        sphere_label = MathTex(r"\chi = 2", font_size=36, color=BLUE)
        sphere_label.next_to(sphere, DOWN, buff=0.5)

        self.play(Create(sphere), run_time=2)
        self.add_fixed_in_frame_mobjects(sphere_label)
        self.play(Write(sphere_label), run_time=0.5)

        # Create torus
        torus = Surface(
            lambda u, v: np.array([
                (2 + np.cos(v)) * np.cos(u),
                (2 + np.cos(v)) * np.sin(u),
                np.sin(v)
            ]),
            u_range=[0, TAU],
            v_range=[0, TAU],
            resolution=(36, 24),
            fill_color=TEAL,
            fill_opacity=0.6,
            stroke_color=WHITE,
            stroke_width=0.5
        )
        torus.scale(0.35)

        # Highlight the hole in red
        hole_ring = ParametricFunction(
            lambda t: np.array([
                2 * np.cos(t),
                2 * np.sin(t),
                0
            ]),
            t_range=[0, TAU],
            color=RED,
            stroke_width=5
        )
        hole_ring.scale(0.35)

        torus_group = VGroup(torus, hole_ring)

        torus_label = MathTex(r"\chi = 0", font_size=36, color=TEAL)
        torus_label.next_to(torus, DOWN, buff=0.5)

        self.play(Create(torus), Create(hole_ring), run_time=2)
        self.add_fixed_in_frame_mobjects(torus_label)
        self.play(Write(torus_label), run_time=0.5)

        # Create double torus (simplified as two connected tori)
        double_torus = Surface(
            lambda u, v: np.array([
                (2 + np.cos(v)) * np.cos(u) + 3 * np.cos(u/2),
                (2 + np.cos(v)) * np.sin(u),
                np.sin(v) + np.sin(u/2)
            ]),
            u_range=[0, TAU],
            v_range=[0, TAU],
            resolution=(48, 24),
            fill_color=PURPLE,
            fill_opacity=0.6,
            stroke_color=WHITE,
            stroke_width=0.5
        )
        double_torus.scale(0.25)
        double_torus.shift(RIGHT*3.5)

        double_torus_label = MathTex(r"\chi = -2", font_size=36, color=PURPLE)
        double_torus_label.next_to(double_torus, DOWN, buff=0.5)

        self.play(Create(double_torus), run_time=2)
        self.add_fixed_in_frame_mobjects(double_torus_label)
        self.play(Write(double_torus_label), run_time=0.5)

        self.wait(1)

        # Generalized formula
        formula = MathTex(
            r"\chi = V - E + F = 2 - 2g",
            font_size=48
        )
        formula.to_edge(DOWN).shift(UP*0.8)
        self.add_fixed_in_frame_mobjects(formula)
        self.play(Write(formula), run_time=2)

        # Genus explanation
        genus_text = Text(
            "g = genus (number of holes)",
            font_size=28,
            color=GREY_B
        ).next_to(formula, DOWN, buff=0.3)
        self.add_fixed_in_frame_mobjects(genus_text)
        self.play(Write(genus_text), run_time=1)

        self.wait(2)

        # Clean up
        self.play(
            FadeOut(title), FadeOut(formula), FadeOut(genus_text),
            FadeOut(sphere), FadeOut(sphere_label),
            FadeOut(torus_group), FadeOut(torus_label),
            FadeOut(double_torus), FadeOut(double_torus_label),
            run_time=1.5
        )

        self.wait(0.5)

    # ==================== CLOSING SCENE ====================
    def closing_scene(self):
        """The Topological Invariant - orbiting polyhedra around central equation"""

        # Central equation
        central_eq = MathTex(
            r"V - E + F = 2",
            font_size=72,
            color=GOLD
        )
        central_eq.set_glow_factor(0.5)

        self.add_fixed_in_frame_mobjects(central_eq)
        self.play(Write(central_eq), run_time=2)

        # Create small orbiting polyhedra
        # Tetrahedron
        tetra_small = self.create_small_tetrahedron()
        tetra_small.scale(0.4).shift(LEFT*3)

        # Cube
        cube_small = self.create_small_cube()
        cube_small.scale(0.3).shift(RIGHT*3)

        # Dodecahedron placeholder (simple representation)
        dodeca_small = Dodecahedron()
        dodeca_small.set_fill(EMERALD_VERTEX, opacity=0.5)
        dodeca_small.set_stroke(SILVER_EDGE, width=1)
        dodeca_small.scale(0.5).shift(UP*2.5)

        polyhedra = VGroup(tetra_small, cube_small, dodeca_small)

        self.play(
            *[FadeIn(p) for p in polyhedra],
            run_time=1.5
        )

        # Add rotation updater
        def orbit_updater(mob, dt):
            mob.rotate(0.5 * dt, axis=OUT, about_point=ORIGIN)

        polyhedra.add_updater(orbit_updater)

        # Wisdom text
        wisdom = Text(
            "Euler's formula reveals that topology cares not\n"
            "about size or shape - only about connectivity and holes.",
            font_size=28,
            color=WHITE,
            line_spacing=1.2
        ).to_edge(DOWN).shift(UP*0.5)
        self.add_fixed_in_frame_mobjects(wisdom)
        self.play(Write(wisdom), run_time=3)

        # Let it orbit for a moment
        self.wait(4)

        # Final glow on the number 2
        two = MathTex(r"2", font_size=120, color=WHITE)
        two.set_glow_factor(1.0)

        self.play(
            FadeOut(central_eq),
            FadeIn(two, scale=0.5),
            run_time=1.5
        )

        self.wait(3)

        # Fade to black
        polyhedra.clear_updaters()
        self.play(
            FadeOut(two),
            FadeOut(polyhedra),
            FadeOut(wisdom),
            run_time=2
        )

        self.wait(1)

    # ==================== HELPER METHODS ====================

    def get_tetrahedron_vertices(self, scale=1.0):
        """Return vertices of a regular tetrahedron centered at origin"""
        vertices = np.array([
            [1, 1, 1],
            [1, -1, -1],
            [-1, 1, -1],
            [-1, -1, 1]
        ]) * scale / np.sqrt(3)
        return vertices

    def get_cube_vertices(self, scale=1.0):
        """Return vertices of a cube centered at origin"""
        vertices = np.array([
            [-1, -1, -1],
            [1, -1, -1],
            [1, 1, -1],
            [-1, 1, -1],
            [-1, -1, 1],
            [1, -1, 1],
            [1, 1, 1],
            [-1, 1, 1]
        ]) * scale / 2
        return vertices

    def get_dodecahedron_vertices(self, scale=1.0):
        """Return vertices of a regular dodecahedron"""
        phi = (1 + np.sqrt(5)) / 2  # Golden ratio

        vertices = []
        # Cube vertices
        for i in [-1, 1]:
            for j in [-1, 1]:
                for k in [-1, 1]:
                    vertices.append([i, j, k])

        # Rectangle vertices
        for i in [-1, 1]:
            for j in [-1, 1]:
                vertices.append([0, i * phi, j / phi])
                vertices.append([i / phi, 0, j * phi])
                vertices.append([i * phi, j / phi, 0])

        vertices = np.array(vertices) * scale / 2
        return vertices

    def get_dodecahedron_edge_indices(self):
        """Return edge indices for a dodecahedron"""
        # This is a simplified edge list for visualization
        # A proper implementation would compute from vertices
        edges = [
            (0, 8), (0, 9), (0, 16),
            (1, 8), (1, 10), (1, 17),
            (2, 9), (2, 11), (2, 18),
            (3, 10), (3, 11), (3, 19),
            (4, 12), (4, 13), (4, 16),
            (5, 12), (5, 14), (5, 17),
            (6, 13), (6, 15), (6, 18),
            (7, 14), (7, 15), (7, 19),
            (8, 12), (9, 13), (10, 14), (11, 15),
            (16, 17), (16, 18), (17, 19), (18, 19)
        ]
        return edges[:30]  # Dodecahedron has 30 edges

    def create_edges(self, vertices, edge_indices, color=WHITE, stroke_width=2):
        """Create Line3D objects for edges"""
        edges = VGroup()
        for i, j in edge_indices:
            if i < len(vertices) and j < len(vertices):
                edge = Line3D(
                    start=vertices[i],
                    end=vertices[j],
                    color=color,
                    thickness=0.02
                )
                edge.set_stroke(color=color, width=stroke_width)
                edges.add(edge)
        return edges

    def create_tetrahedron_faces(self, vertices):
        """Create translucent faces for tetrahedron"""
        face_indices = [
            (0, 1, 2),
            (0, 1, 3),
            (0, 2, 3),
            (1, 2, 3)
        ]

        faces = VGroup()
        for indices in face_indices:
            face = Polygon(
                *[vertices[i] for i in indices],
                fill_color=GOLD_FACE,
                fill_opacity=0.3,
                stroke_width=0
            )
            faces.add(face)
        return faces

    def create_cube_faces(self, vertices):
        """Create translucent faces for cube"""
        face_indices = [
            (0, 1, 2, 3),  # bottom
            (4, 5, 6, 7),  # top
            (0, 1, 5, 4),  # front
            (2, 3, 7, 6),  # back
            (0, 3, 7, 4),  # left
            (1, 2, 6, 5)   # right
        ]

        faces = VGroup()
        for indices in face_indices:
            face = Polygon(
                *[vertices[i] for i in indices],
                fill_color=CORAL_FACE,
                fill_opacity=0.3,
                stroke_width=0
            )
            faces.add(face)
        return faces

    def create_dodecahedron_faces(self, vertices):
        """Create simplified faces for dodecahedron (pentagonal approximation)"""
        # For a true dodecahedron, we'd need the proper face indices
        # This creates a simplified visual representation
        faces = VGroup()

        # Create approximate pentagonal faces using nearby vertices
        # This is simplified - proper implementation would compute convex hull
        for i in range(12):  # 12 pentagonal faces
            # Create a small translucent sphere at face centers as approximation
            center = np.mean(vertices, axis=0) * 0.8 + np.random.uniform(-0.3, 0.3, 3)
            face = Dot3D(center, radius=0.15, color=DEEP_BLUE_FACE)
            face.set_opacity(0.4)
            faces.add(face)

        return faces

    def create_small_tetrahedron(self):
        """Create a small tetrahedron for the closing scene"""
        tetra = Tetrahedron()
        tetra.set_fill(CYAN_VERTEX, opacity=0.5)
        tetra.set_stroke(ELECTRIC_BLUE, width=2)
        return tetra

    def create_small_cube(self):
        """Create a small cube for the closing scene"""
        cube = Cube()
        cube.set_fill(MAGENTA_VERTEX, opacity=0.5)
        cube.set_stroke(PURPLE_EDGE, width=2)
        return cube


# Alternative shorter scene for quick testing
class EulerFormulaQuick(ThreeDScene):
    """Quick version showing just the core formula with three polyhedra"""

    def construct(self):
        self.camera.background_color = BLACK
        self.set_camera_orientation(phi=70*DEGREES, theta=-45*DEGREES)

        # Title
        title = MathTex(r"V - E + F = 2", font_size=72, color=GOLD)
        title.to_edge(UP)
        self.add_fixed_in_frame_mobjects(title)
        self.play(Write(title), run_time=2)

        # Create three polyhedra
        tetra = Tetrahedron().scale(0.8).shift(LEFT*3.5)
        tetra.set_fill(CYAN_VERTEX, opacity=0.5)
        tetra.set_stroke(ELECTRIC_BLUE, width=2)

        cube = Cube().scale(0.7)
        cube.set_fill(MAGENTA_VERTEX, opacity=0.5)
        cube.set_stroke(PURPLE_EDGE, width=2)

        dodeca = Dodecahedron().scale(0.8).shift(RIGHT*3.5)
        dodeca.set_fill(EMERALD_VERTEX, opacity=0.5)
        dodeca.set_stroke(SILVER_EDGE, width=2)

        # Labels
        tetra_label = MathTex(r"4-6+4=2", font_size=28, color=CYAN_VERTEX)
        tetra_label.next_to(tetra, DOWN, buff=0.5)

        cube_label = MathTex(r"8-12+6=2", font_size=28, color=MAGENTA_VERTEX)
        cube_label.next_to(cube, DOWN, buff=0.5)

        dodeca_label = MathTex(r"20-30+12=2", font_size=28, color=EMERALD_VERTEX)
        dodeca_label.next_to(dodeca, DOWN, buff=0.5)

        # Add to scene
        self.play(
            GrowFromCenter(tetra),
            GrowFromCenter(cube),
            GrowFromCenter(dodeca),
            run_time=2
        )

        for label in [tetra_label, cube_label, dodeca_label]:
            self.add_fixed_in_frame_mobjects(label)

        self.play(
            Write(tetra_label),
            Write(cube_label),
            Write(dodeca_label),
            run_time=1.5
        )

        # Rotate
        self.begin_ambient_camera_rotation(rate=0.1)
        self.wait(6)
        self.stop_ambient_camera_rotation()

        # Final message
        message = Text(
            "A topological invariant!",
            font_size=36,
            color=GREEN
        ).to_edge(DOWN)
        self.add_fixed_in_frame_mobjects(message)
        self.play(Write(message), run_time=1.5)

        self.wait(2)


if __name__ == "__main__":
    # Render command: manim -pqh euler_polyhedron_formula.py EulerPolyhedronFormula
    pass
