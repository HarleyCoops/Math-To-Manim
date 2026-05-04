from manim import *
import numpy as np

# Global Configuration
config.background_color = "#111111"
# config.frame_rate = 60
# config.pixel_width = 1920
# config.pixel_height = 1080

class DissipativeStructures(ThreeDScene):
    def construct(self):
        # --- Helper Variables ---
        self.mu_tracker = ValueTracker(-2)  # For Act IV
        
        # --- Execution Flow ---
        self.act_one_chaos()
        self.act_two_departure()
        self.act_three_linear()
        self.act_four_bifurcation()
        self.act_five_dissipative()

    def act_one_chaos(self):
        """ACT I: The Box of Chaos (The Static World)"""
        
        # 1. Setup Camera and Cube
        self.set_camera_orientation(phi=75 * DEGREES, theta=45 * DEGREES)
        
        cube = Cube(side_length=4, fill_opacity=0, stroke_color=WHITE, stroke_opacity=0.3)
        self.add(cube)
        
        # 2. Particle Generation (Brownian Motion)
        particles = VGroup()
        for _ in range(150):
            dot = Dot3D(radius=0.05, color="#A9A9A9")
            # Random initial position
            dot.move_to(np.array([
                np.random.uniform(-1.8, 1.8),
                np.random.uniform(-1.8, 1.8),
                np.random.uniform(-1.8, 1.8)
            ]))
            particles.add(dot)
        
        # Define Brownian updater
        def brownian_updater(mob, dt):
            speed = 2.0
            shift_vect = np.random.normal(0, speed * dt, 3)
            new_pos = mob.get_center() + shift_vect
            # Simple box clamp
            for i in range(3):
                if abs(new_pos[i]) > 1.9:
                    shift_vect[i] *= -1 
            mob.shift(shift_vect)

        for p in particles:
            p.add_updater(brownian_updater)

        # Sequence 0:00 - 0:10 (The Random Gas)
        title_text = Tex("The Isolated System").to_corner(UL)
        self.add_fixed_in_frame_mobjects(title_text)
        
        self.play(FadeIn(cube), FadeIn(particles), Write(title_text))
        self.begin_ambient_camera_rotation(rate=0.2)
        self.wait(3)

        # Sequence 0:10 - 0:20 (The Mathematical Lens)
        # Using raw strings for latex
        math_grad = MathTex(r"\nabla", color="#4AF626").move_to(LEFT * 3 + UP * 2)
        math_int = MathTex(r"\int", color="#4AF626").move_to(RIGHT * 3 + DOWN * 2)
        math_dist = MathTex(r"P(v) \sim e^{-mv^2/2kT}", color="#4AF626").move_to(UP * 3)
        
        # Ensure math faces camera
        for m in [math_grad, math_int, math_dist]:
            self.add_fixed_in_frame_mobjects(m)

        self.play(
            FadeIn(math_grad, scale=0.5),
            FadeIn(math_int, scale=0.5),
            FadeIn(math_dist, scale=0.5),
            particles.animate.set_color("#4AF626"),
            run_time=2
        )
        self.wait(1)
        self.play(particles.animate.set_color("#A9A9A9"), run_time=1)

        # Sequence 0:20 - 0:30 (Equilibrium Death)
        # Remove updaters to stop motion
        for p in particles:
            p.clear_updaters()
        
        # Animate settling to grid/even distribution
        target_positions = []
        # Create a rough 5x5x6 grid for 150 particles
        for x in np.linspace(-1.5, 1.5, 5):
            for y in np.linspace(-1.5, 1.5, 5):
                for z in np.linspace(-1.5, 1.5, 6):
                    target_positions.append([x,y,z])
        
        animations = []
        for i, p in enumerate(particles):
            if i < len(target_positions):
                animations.append(p.animate.move_to(target_positions[i]).set_color("#555555"))
        
        entropy_eq = MathTex(r"S = k_B \ln \Omega", font_size=70).set_z_index(10)
        self.add_fixed_in_frame_mobjects(entropy_eq)

        entropy_label = Tex(r"Entropy ($S$): ").to_corner(DR)
        entropy_tracker = DecimalNumber(0).next_to(entropy_label, RIGHT)
        self.add_fixed_in_frame_mobjects(entropy_label, entropy_tracker)

        self.play(
            AnimationGroup(*animations, lag_ratio=0.01),
            FadeIn(entropy_eq),
            ChangeDecimalToValue(entropy_tracker, 9999, run_time=3),
            run_time=4
        )
        
        death_text = Tex("Equilibrium = Maximum Entropy = Thermal Death", color=RED).to_edge(DOWN)
        self.add_fixed_in_frame_mobjects(death_text)
        self.wait(2)

        # Cleanup Act I
        self.stop_ambient_camera_rotation()
        self.clear()
        # Reset camera to standard 2D view (top down logic)
        self.set_camera_orientation(phi=0, theta=-90 * DEGREES)

    def act_two_departure(self):
        """ACT II: The Departure (Gears and Gradients)"""
        
        # Sequence 0:30 - 0:40 (Imposing the Gradient)
        # Create 10x6 Grid
        grid = VGroup()
        rows, cols = 6, 10
        for r in range(rows):
            for c in range(cols):
                sq = Square(side_length=0.8)
                sq.move_to(np.array([c - cols/2 + 0.5, r - rows/2 + 0.5, 0]))
                grid.add(sq)
        
        grid.set_stroke(WHITE)
        grid.set_fill(color=GREY, opacity=0.5)
        grid.center()
        
        self.play(Create(grid), run_time=2)
        
        # Apply Gradient
        def get_gradient_color(mob):
            # Map x position to color
            x = mob.get_x()
            alpha = (x + 5) / 10  # Normalize roughly -5 to 5 -> 0 to 1
            return interpolate_color(Color("#FF5733"), Color("#33C1FF"), alpha)

        self.play(
            grid.animate.set_submobject_colors_by_gradient("#FF5733", "#33C1FF"),
            run_time=2
        )

        flux_arrows = VGroup()
        for i in range(15):
            arr = Arrow(LEFT, RIGHT, color="#FFD700").scale(0.8)
            arr.move_to(np.array([np.random.uniform(-4, 4), np.random.uniform(-2, 2), 0]))
            flux_arrows.add(arr)
        
        text_gradient = Tex("Imposing a Gradient implies Flow").to_edge(UP)
        self.play(FadeIn(flux_arrows), Write(text_gradient))
        self.wait(1)

        # Sequence 0:40 - 0:50 (The Local View)
        # We simulate a zoom by scaling everything up and shifting
        target_square = grid[35] # Middle-ish square
        zoom_group = VGroup(grid, flux_arrows)
        
        # Zoom effect
        self.play(
            FadeOut(text_gradient),
            self.camera.animate.set_width(grid[0].width * 4).move_to(target_square.get_center()),
            run_time=2
        )

        # Micro-physics inside the square
        micro_dots = VGroup(*[Dot(radius=0.02, color=WHITE) for _ in range(20)])
        micro_dots.move_to(target_square.get_center())
        
        # Constrain dots to target square
        def local_updater(mob, dt):
            mob.shift(np.random.normal(0, 0.5*dt, 3))
            diff = mob.get_center() - target_square.get_center()
            if abs(diff[0]) > 0.35: mob.shift(np.array([-diff[0]*0.1, 0, 0]))
            if abs(diff[1]) > 0.35: mob.shift(np.array([0, -diff[1]*0.1, 0]))

        for d in micro_dots:
            d.add_updater(local_updater)
        
        self.add(micro_dots)
        
        local_eq = MathTex(r"T ds = du + P dv", color=WHITE).scale(0.3)
        local_eq.move_to(target_square.get_center() + UP*0.2)
        local_eq.set_opacity(0.8)
        
        self.play(FadeIn(local_eq))
        
        # Sequence 0:50 - 1:00 (The Continuity Check)
        balance_eq = MathTex(r"\partial_t \rho + \nabla \cdot \mathbf{J} = 0", color=YELLOW)
        balance_eq.scale(0.3).next_to(target_square, DOWN, buff=0.1)
        
        self.play(
            target_square.animate.set_fill(opacity=0.8, color=YELLOW_E),
            Write(balance_eq)
        )
        self.wait(2)
        
        # Reset Camera for next Act
        self.play(
             self.camera.animate.set_width(config.frame_width).move_to(ORIGIN),
             FadeOut(zoom_group), FadeOut(micro_dots), FadeOut(local_eq), FadeOut(balance_eq)
        )

    def act_three_linear(self):
        """ACT III: The Linear Regime (Coupled Forces)"""
        
        # Sequence 1:00 - 1:15
        
        # Create Helper Function for Gears
        def create_gear(color, radius=1, teeth=8):
            inner = Circle(radius=radius, fill_color=color, fill_opacity=0.5, stroke_color=color)
            teeth_group = VGroup()
            for i in range(teeth):
                angle = i * (TAU / teeth)
                tooth = Square(side_length=radius/3).set_fill(color, 1).set_stroke(width=0)
                tooth.move_to((radius + radius/6) * np.array([np.cos(angle), np.sin(angle), 0]))
                tooth.rotate(angle)
                teeth_group.add(tooth)
            return VGroup(inner, teeth_group)

        gear1 = create_gear(RED, radius=1.5).shift(LEFT * 2)
        gear2 = create_gear(YELLOW, radius=1.5).shift(RIGHT * 0.8) # Meshed roughly
        
        # Labels
        label1 = Tex(r"Thermal Force $X_Q$", font_size=24).next_to(gear1, DOWN)
        label2 = Tex(r"Diffusion $J_D$", font_size=24).next_to(gear2, DOWN)
        
        self.play(DrawBorderThenFill(gear1), DrawBorderThenFill(gear2), Write(label1), Write(label2))

        # Rotate Gears
        # Gear 1 rotates CW (-), Gear 2 rotates CCW (+)
        gear1.add_updater(lambda m, dt: m.rotate(-1 * dt))
        gear2.add_updater(lambda m, dt: m.rotate(1 * dt))
        
        # Onsager Matrix
        onsager = MathTex(
            r"\begin{bmatrix} J_1 \\ J_2 \end{bmatrix} = \begin{bmatrix} L_{11} & L_{12} \\ L_{21} & L_{22} \end{bmatrix} \begin{bmatrix} X_1 \\ X_2 \end{bmatrix}"
        ).to_edge(RIGHT).scale(0.8)
        
        # Highlight Reciprocity
        reciprocity = SurroundingRectangle(onsager[0][13:21], color=BLUE) # Roughly indices for L12, L21
        
        self.play(Write(onsager))
        self.play(Create(reciprocity))
        self.wait(1)
        
        # Entropy Production (Dust)
        contact_point = (gear1.get_center() + gear2.get_center()) / 2
        dust = VGroup()
        
        def dust_updater(mob, dt):
            if len(mob) < 30:
                d = Dot(radius=0.03, color=GREY)
                d.move_to(contact_point)
                d.velocity = np.array([np.random.uniform(-0.5, 0.5), -1, 0])
                mob.add(d)
            for d in mob:
                d.shift(d.velocity * dt)
                d.set_opacity(d.get_opacity() - 0.5 * dt)
                if d.get_opacity() <= 0:
                    mob.remove(d)

        dust.add_updater(dust_updater)
        self.add(dust)
        
        entropy_prod = MathTex(r"\sigma = \sum J_i X_i \geq 0", color=RED).to_edge(UP)
        self.play(Write(entropy_prod))
        self.wait(2)
        
        # Cleanup
        gear1.clear_updaters()
        gear2.clear_updaters()
        dust.clear_updaters()
        self.clear()

    def act_four_bifurcation(self):
        """ACT IV: The Fork in the Road (Bifurcation)"""
        
        # Sequence 1:15 - 1:30
        
        # Reset to 3D View
        self.set_camera_orientation(phi=70 * DEGREES, theta=-90 * DEGREES)
        self.camera.zoom = 1 # Reset zoom just in case
        
        # Axes
        axes = ThreeDAxes(x_range=[-3, 3], y_range=[-3, 3], z_range=[-5, 5], z_length=4)
        
        # Initial Mu
        self.mu_tracker.set_value(-2)
        
        # Parametric Surface: z = x^4 - mu*x^2 (visualized as a ribbon/extruded curve along Y)
        # To optimize, we'll draw a dense series of lines or a low-res surface
        
        def get_surface():
            mu = self.mu_tracker.get_value()
            # Color logic
            c = BLUE if mu < 0 else RED
            
            surf = Surface(
                lambda u, v: axes.c2p(u, v, u**4 - mu * u**2),
                u_range=[-2, 2],
                v_range=[-1, 1], # Short strip in Y
                resolution=(20, 4),
                fill_opacity=0.6
            )
            surf.set_style(fill_color=c, stroke_color=WHITE, stroke_width=0.5)
            return surf

        surface_obj = always_redraw(get_surface)
        self.add(axes, surface_obj)
        
        # The Ball (Sphere)
        sphere = Sphere(radius=0.2, color=YELLOW)
        
        def update_sphere(mob):
            mu = self.mu_tracker.get_value()
            # If mu < 0, stable at x=0
            # If mu > 0, stable at +/- sqrt(mu/2). Let's pick + side
            x_pos = 0
            if mu > 0:
                x_pos = np.sqrt(mu/2)
            
            # Position on surface
            z_pos = x_pos**4 - mu * x_pos**2
            mob.move_to(axes.c2p(x_pos, 0, z_pos) + UP*0.2) # Sit on top

        sphere.add_updater(update_sphere)
        self.add(sphere)
        
        # UI: Flux Slider / Text
        val_text = Tex("Flux $\mu$: ").to_corner(UL)
        val_num = DecimalNumber().next_to(val_text, RIGHT)
        val_num.add_updater(lambda m: m.set_value(self.mu_tracker.get_value()))
        self.add_fixed_in_frame_mobjects(val_text, val_num)
        
        # Animation: Morph
        self.play(
            self.mu_tracker.animate.set_value(5),
            run_time=6,
            rate_func=linear
        )
        
        bif_text = Tex("Symmetry Breaking", color=YELLOW).to_edge(UP)
        self.add_fixed_in_frame_mobjects(bif_text)
        self.play(FadeIn(bif_text))
        self.wait(2)
        
        self.clear()
        sphere.clear_updaters()
        val_num.clear_updaters()
        surface_obj.clear_updaters()

    def act_five_dissipative(self):
        """ACT V: Dissipative Structures (Order out of Chaos)"""
        
        # Sequence 1:30 - End
        self.set_camera_orientation(phi=0, theta=-90*DEGREES)
        
        # Hex Grid
        hex_group = VGroup()
        # Create a honeycomb
        radius = 0.5
        y_step = radius * 1.5
        x_step = radius * np.sqrt(3)
        
        for i in range(-5, 6):
            for j in range(-5, 6):
                # Offset every other row
                x_offset = 0 if i % 2 == 0 else x_step / 2
                pos = np.array([j * x_step + x_offset, i * y_step, 0])
                
                h = RegularPolygon(n=6, radius=radius, start_angle=30*DEGREES)
                h.move_to(pos)
                h.set_fill(color=GREY, opacity=0.5)
                h.set_stroke(color=WHITE, width=1)
                hex_group.add(h)
                
        # Random coloring initially
        for h in hex_group:
            h.set_fill(color=random_color())
            
        self.add(hex_group)
        
        # The Emergence (Transform to Benard Cells)
        # Center Yellow, Edge Blue
        self.play(
            hex_group.animate.set_fill(color="#F1C40F", opacity=0.8)
                     .set_stroke(color="#2C3E50", width=4),
            run_time=3
        )
        
        # Flow Visualization (Loops)
        # We'll create a few sample flow lines in the center hexagon
        center_hex_pos = ORIGIN
        loops = VGroup()
        for i in range(3):
            # Create an ellipse path
            loop = Ellipse(width=0.4, height=0.8, color=RED).move_to(center_hex_pos)
            loops.add(loop)
            
        # Animate scaling out to show global structure
        self.play(
            hex_group.animate.scale(0.6),
            run_time=2
        )
        
        thesis = Tex("Structure maintained by Flow", font_size=60).set_z_index(20)
        thesis_bg = BackgroundRectangle(thesis, color=BLACK, fill_opacity=0.7)
        self.play(FadeIn(thesis_bg), Write(thesis))
        
        # Final Equation
        final_eq = MathTex(r"d_i S > 0, \quad d_e S < 0", font_size=50).next_to(thesis, DOWN)
        subtitle = Tex("Entropy is exported to maintain internal order.", font_size=30).next_to(final_eq, DOWN)
        
        bg_eq = BackgroundRectangle(VGroup(final_eq, subtitle), color=BLACK, fill_opacity=0.7)
        
        self.play(FadeIn(bg_eq), Write(final_eq), Write(subtitle))
        self.wait(3)
        
        # Final Fade
        final_cap = Tex("Dissipative Structures").scale(1.5)
        self.play(
            FadeOut(hex_group), FadeOut(thesis), FadeOut(thesis_bg), 
            FadeOut(final_eq), FadeOut(subtitle), FadeOut(bg_eq),
            FadeIn(final_cap)
        )
        self.wait(2)
        self.play(FadeOut(final_cap))

# Helper color function
def random_color():
    return [
        "#555555", "#666666", "#777777", "#444444"
    ][np.random.randint(0, 4)]