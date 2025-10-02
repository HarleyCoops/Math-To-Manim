from manim import *
import math
import numpy as np

class ElectroweakSymmetryScene(ThreeDScene):
    """
    A maximum-complexity Manim 3D scene illustrating key elements of
    electroweak symmetry breaking with dynamic surfaces, text overlays,
    camera movements, parametric updaters, and more.
    """
    def construct(self):
        # ----------------------------------------------------------
        # 1. INITIAL SETUP AND INTRO
        # ----------------------------------------------------------
        # Configure the initial 3D camera orientation and background color
        self.set_camera_orientation(phi=70 * DEGREES, theta=-45 * DEGREES)
        self.camera.background_color = "#000000"  # black background

        # Intro Title
        intro_title = Text(
            "Electroweak Symmetry Breaking", 
            font_size=48, 
            gradient=(BLUE, GREEN)
        ).to_edge(UP)
        
        intro_subtitle = Text(
            "A 3D Manim Visualization", 
            font_size=36
        ).next_to(intro_title, DOWN, buff=0.3)

        # Fade them in
        self.play(Write(intro_title), FadeIn(intro_subtitle))
        self.wait(2)

        # Slide them to top-right corner while shrinking
        self.play(
            intro_title.animate.scale(0.5).to_corner(UR),
            intro_subtitle.animate.scale(0.5).to_corner(UR).shift(DOWN*0.8),
            run_time=2
        )

        # ----------------------------------------------------------
        # 2. LAGRANGIAN DISPLAY (2D Overlay in a 3D Scene)
        # ----------------------------------------------------------
        # We'll present the electroweak Lagrangian in multiple parts, each on the screen briefly.
        lagrangian1 = MathTex(
            r"\mathcal{L}_{\text{EW}} = -\tfrac{1}{4} W_{\mu\nu}^a W^{a\mu\nu}",
            font_size=32
        ).shift(2*UP + 2*LEFT)
        lagrangian2 = MathTex(
            r"- \tfrac{1}{4} B_{\mu\nu} B^{\mu\nu}",
            font_size=32
        ).next_to(lagrangian1, DOWN, buff=0.3)
        lagrangian3 = MathTex(
            r"+ \bar{\psi}_L \gamma^\mu \bigl(i D_\mu\bigr)\psi_L + \dots",
            font_size=32
        ).next_to(lagrangian2, DOWN, buff=0.3)

        # We add them as "fixed in frame" so they don't rotate with the 3D scene
        self.add_fixed_in_frame_mobjects(lagrangian1, lagrangian2, lagrangian3)

        self.play(FadeIn(lagrangian1), run_time=2)
        self.wait(1)
        self.play(FadeIn(lagrangian2), run_time=1.5)
        self.wait(1)
        self.play(FadeIn(lagrangian3), run_time=1.5)
        self.wait(2)

        # ----------------------------------------------------------
        # 3. GAUGE BOSONS (PARTICLES) + SIMPLE 3D GRID
        # ----------------------------------------------------------
        # Create a 3D NumberPlane to represent space
        plane = NumberPlane(
            x_range=[-6, 6, 1],
            y_range=[-6, 6, 1],
            background_line_style={
                "stroke_color": BLUE_E,
                "stroke_width": 1,
                "stroke_opacity": 0.4,
            }
        )
        # Re-orient the plane to look somewhat "floor-like"
        plane.rotate(angle=PI/2, axis=RIGHT)

        self.play(Create(plane), run_time=2)
        self.wait(1)

        # Helper function to create spherical "particles" with labels
        def create_particle(label_tex, color=WHITE, radius=0.3):
            sphere = Sphere(radius=radius).set_color(color).set_opacity(0.8)
            sphere_label = MathTex(label_tex, color=color, font_size=36)
            # We'll position the label above the sphere in 3D
            sphere_label.move_to(sphere.get_center() + UP*(radius+0.2))
            return VGroup(sphere, sphere_label)

        # Example gauge bosons
        w_plus = create_particle(r"W^+", color=YELLOW)
        w_minus = create_particle(r"W^-", color=MAROON)
        z_boson = create_particle(r"Z^0", color=GREEN)
        photon = create_particle(r"\gamma", color=BLUE)

        # Position them around the plane
        w_plus.move_to(3*LEFT + 1*UP)
        w_minus.move_to(3*RIGHT + 1*UP)
        z_boson.move_to(1*LEFT + 2*DOWN)
        photon.move_to(1*RIGHT + 2*DOWN)

        self.play(
            FadeIn(w_plus),
            FadeIn(w_minus),
            FadeIn(z_boson),
            FadeIn(photon),
            run_time=3
        )
        self.wait(1)

        # ----------------------------------------------------------
        # 4. MEXICAN HAT (HIGGS) POTENTIAL SURFACE
        # ----------------------------------------------------------
        # Define the Mexican Hat potential function
        def mexican_hat(x, y):
            r = np.sqrt(x**2 + y**2)
            return 0.2*((r**2 - 1)**2)  # scale factor 0.2 for clarity

        # Create a Surface for the potential
        potential_surface = Surface(
            lambda u, v: np.array([u, v, mexican_hat(u, v)]),
            u_range=[-2.5, 2.5],
            v_range=[-2.5, 2.5],
            resolution=(40, 40),
            fill_opacity=0.7,
            checkerboard_colors=[RED_D, RED_E]
        )
        # Shift it down in the scene
        potential_surface.shift(DOWN*2)

        self.play(Create(potential_surface), run_time=3)
        self.wait(1)

        # ----------------------------------------------------------
        # 5. A "ROLLING SPHERE" TO DEMONSTRATE SYMMETRY BREAKING
        # ----------------------------------------------------------
        # Create a small sphere at the top of the potential
        rolling_sphere = Sphere(radius=0.2, color=YELLOW).set_opacity(1.0)
        rolling_sphere.move_to(np.array([0,0,mexican_hat(0,0)]))
        self.play(FadeIn(rolling_sphere))

        # Path along the "valley" - define a parametric path
        # We'll let it circle around at radius ~1 from the center
        def valley_path(t):
            # t in [0,1]
            angle = 2*PI * t
            x = 1.0 * np.cos(angle)
            y = 1.0 * np.sin(angle)
            z = mexican_hat(x,y)
            return np.array([x, y, z - 0.05])  # shift slightly so it sinks into the valley

        path_function = ParametricFunction(valley_path, t_range=[0,1], color=WHITE)

        # Animate the sphere rolling down from center to the circular valley
        # We'll create an intermediate "down the hill" path
        # Just do a simple param from radius=0..1
        def rolling_down(t):
            # first half of the animation: move from center to radius=1
            # second half: revolve around the valley
            if t < 0.5:
                radius = 2*t  # grows from 0..1 as t goes from 0..0.5
                angle = PI * t  # just a small rotation
                x = radius * np.cos(angle)
                y = radius * np.sin(angle)
                z = mexican_hat(x,y)
                return np.array([x, y, z])
            else:
                # revolve around
                new_t = (t - 0.5)*2  # re-scale 0.5..1 => 0..1
                return valley_path(new_t)

        rolling_path = ParametricFunction(
            rolling_down, 
            t_range=[0,1], 
            color=BLUE_B
        )

        self.play(MoveAlongPath(rolling_sphere, rolling_path), run_time=6)
        self.wait(1)

        # ----------------------------------------------------------
        # 6. AMBIENT CAMERA ROTATION AND A SPHERICAL "HIGGS FIELD" EXPANSION
        # ----------------------------------------------------------
        self.begin_ambient_camera_rotation(rate=0.15)

        # We'll overlay a transparent sphere that grows, symbolizing the 'field' saturating space
        higgs_field = Sphere(radius=0.1, color=PURPLE).set_opacity(0.3)
        self.add(higgs_field)  # add to scene

        def update_higgs_field(mob, alpha):
            # alpha in [0,1]
            # radius from 0.1 to 5
            new_radius = 5 * alpha + 0.1
            mob.become(
                Sphere(radius=new_radius, color=PURPLE).set_opacity(0.15 + 0.15*alpha)
            )
            mob.shift(DOWN*2)  # keep it somewhat aligned with the potential surface

        self.play(
            UpdateFromAlphaFunc(higgs_field, update_higgs_field),
            run_time=5,
            rate_func=there_and_back
        )
        self.stop_ambient_camera_rotation()
        self.wait(1)

        # ----------------------------------------------------------
        # 7. INTRODUCE SHORT TEXT EXPLANATIONS (FIXED IN FRAME)
        # ----------------------------------------------------------
        explanation_text = Text(
            "Gauge Bosons Acquire Mass\nvia Spontaneous Symmetry Breaking",
            font_size=28,
            color=YELLOW
        ).to_edge(DOWN)

        self.add_fixed_in_frame_mobjects(explanation_text)
        self.play(FadeIn(explanation_text), run_time=2)
        self.wait(3)

        # ----------------------------------------------------------
        # 8. FINAL CAMERA TOUR AND OUTRO
        # ----------------------------------------------------------
        # Move the camera around to a new angle
        self.move_camera(phi=60*DEGREES, theta=60*DEGREES, run_time=3)
        self.wait(2)

        outro_box = Rectangle(height=2, width=6, color=WHITE)
        outro_text = Text("Electroweak Unification:\nWhere Mass Emerges", font_size=30)
        outro_group = VGroup(outro_box, outro_text).arrange(DOWN, buff=0.3)
        self.add_fixed_in_frame_mobjects(outro_group)
        outro_group.to_edge(DOWN)

        self.play(FadeIn(outro_group))
        self.wait(3)

        # Fade out everything
        to_fade = [lagrangian1, lagrangian2, lagrangian3, plane, potential_surface,
                   w_plus, w_minus, z_boson, photon, rolling_sphere, higgs_field,
                   explanation_text, outro_group]
        self.play(
            *[FadeOut(m) for m in to_fade],
            FadeOut(intro_title),
            FadeOut(intro_subtitle),
            run_time=3
        )
        self.wait(1)

    # (No special helper functions needed beyond here—just standard Manim methods.)
