# Version Check - Ensure Manim v0.19.x (Community Edition is typical)
# import manim
# print(manim.__version__) # Should output something like 0.19.0.post0

from manim import *
import numpy as np

# Configuration (Optional: can be set via command line)
# config.background_color = BLACK
# config.pixel_height = 1080
# config.pixel_width = 1920
# config.frame_rate = 30

# Color Constants
ELECTRON_COLOR = BLUE
PHOTON_COLOR = YELLOW
CONNECTION_COLOR = BLUE_C
FIELD_E_COLOR = RED
FIELD_B_COLOR = BLUE_D # Using a darker blue for B field for contrast
LAGRANGIAN_TERM_COLORS = {
    r"\psi": ORANGE,
    r"\bar{\psi}": ORANGE,
    r"D_\mu": GREEN,
    r"\gamma^\mu": BLUE_C,
    r"F_{\mu\nu}": YELLOW,
    r"F^{\mu\nu}": YELLOW, # Ensure consistency for upper/lower indices
    r"m": WHITE,
    r"e": WHITE,
    # Placeholder for specific terms if needed later
}


# Helper function for zoom effect
def zoom_animation(scene, target_mobject, zoom_scale=0.4, fade_opacity=0.1):
    """Helper to zoom in on a target, fade others, then zoom out."""

    # Save initial camera state for ThreeDCamera
    original_distance = scene.camera.get_focal_distance()
    original_phi = scene.camera.phi
    original_theta = scene.camera.theta
    
    # Get mobjects to fade (only those that support opacity)
    mobjects_to_fade = []
    original_opacities = {}
    for m in scene.mobjects:
        # Skip the target mobject itself
        if m != target_mobject and isinstance(m, VMobject):
            try:
                # Check if the mobject supports fill opacity
                current_opacity = m.get_fill_opacity()
                mobjects_to_fade.append(m)
                original_opacities[m] = current_opacity
            except AttributeError:
                # Skip if no opacity support
                continue

    # Calculate new distance based on zoom scale
    new_distance = original_distance * zoom_scale

    # Get target position
    target_pos = target_mobject.get_center()

    # Zoom In animation - use move_camera for ThreeDCamera
    scene.move_camera(
        phi=original_phi,
        theta=original_theta,
        frame_center=target_pos,
        focal_distance=new_distance,
        run_time=2
    )
    
    # Fade other objects if we found any that support opacity
    if mobjects_to_fade:
        scene.play(*[m.animate.set_opacity(fade_opacity) for m in mobjects_to_fade])
    
    scene.wait(1) # Pause while zoomed

    # Return a list containing the state and info needed for zoom out
    return [original_distance, original_phi, original_theta, target_pos, mobjects_to_fade, original_opacities]

def zoom_out_animation(scene, zoom_data):
    """Helper to zoom out using data saved by zoom_animation."""
    original_distance, original_phi, original_theta, zoomed_pos, mobjects_to_fade, original_opacities = zoom_data
    
    # Restore camera position for ThreeDCamera using move_camera
    scene.move_camera(
        phi=original_phi,
        theta=original_theta,
        focal_distance=original_distance,
        run_time=2
    )
    
    # Restore opacities if we have objects to restore
    if mobjects_to_fade:
        scene.play(*[m.animate.set_opacity(original_opacities[m]) for m in mobjects_to_fade])
    
    scene.wait(0.5)


class Scene1_SpacetimeContext(ThreeDScene):
    def construct(self):
        # Scene 1: Spacetime Context - The Workspace

        # Background: Star field (Conceptual - Using dark background for now)
        # If using an image:
        # star_field = ImageMobject("path/to/your/starfield_pano.jpg")
        # star_field.set_height(config.frame_height * 1.5) # Make it larger than screen
        # self.add(star_field) # Add early, behind everything
        self.camera.background_color = BLACK # Use black background
        # Note: A panoramic star field that works well with 3D camera moves needs careful setup.

        # Set initial camera orientation
        self.set_camera_orientation(phi=60 * DEGREES, theta=-45 * DEGREES, distance=10)

        # Axes & Title
        axes = ThreeDAxes(
            x_range=[-5, 5, 1],
            y_range=[-5, 5, 1],
            z_range=[-3, 3, 1],
            x_length=10,
            y_length=10,
            z_length=6,
        )
        # axes_labels = axes.get_axis_labels(x_label="x", y_label="y", z_label="z")
        self.play(Create(axes))

        title = Text(
            "Quantum Field Theory:\nA Journey into the Electromagnetic Interaction",
            font_size=48,
            weight=BOLD
        ).to_corner(UL)

        # Make title briefly glow/flash (simpler than continuous glow)
        self.play(Write(title))
        self.play(ShowPassingFlash(title.copy().set_color(YELLOW), time_width=1.0))
        self.play(title.animate.scale(0.5).to_corner(UL))
        self.wait(1)

        # Minkowski Spacetime (Simplified 3D representation)
        light_cone_surface = Surface(
            lambda u, v: axes.c2p(
                u * np.cos(v), u * np.sin(v), u
            ), # Upper cone z = sqrt(x^2+y^2) -> u is radius, z=u
            u_range=[0, 2],
            v_range=[0, TAU],
            resolution=(16, 32),
            fill_opacity=0.2,
            stroke_color=WHITE,
            stroke_width=1,
            checkerboard_colors=[BLUE_E, BLUE_D] # Optional styling
        )
        lower_light_cone = Surface(
             lambda u, v: axes.c2p(
                u * np.cos(v), u * np.sin(v), -u # Lower cone z = -sqrt(x^2+y^2)
            ),
            u_range=[0, 2],
            v_range=[0, TAU],
            resolution=(16, 32),
            fill_opacity=0.2,
            stroke_color=WHITE,
            stroke_width=1,
            checkerboard_colors=[BLUE_E, BLUE_D]
        )

        spacetime_diagram = VGroup(light_cone_surface, lower_light_cone) # Add axes later if needed
        self.play(Create(spacetime_diagram))

        # Rotation Animation (Use ApplyMethod for continuous rotation effect over time)
        # self.play(Rotate(spacetime_diagram, angle=PI, axis=OUT, run_time=8, rate_func=linear))
        # A better way for continuous slow rotation if needed is using an updater:
        spacetime_diagram.add_updater(lambda mob, dt: mob.rotate(0.1 * dt, axis=UP))
        self.add(spacetime_diagram) # Add after Create to apply updater
        self.wait(3) # Let it rotate for a bit

        # Relativistic Metric
        metric_eq = MathTex(
            r"ds^2", "=", r"-c^2 dt^2", "+", r"dx^2", "+", r"dy^2", "+", r"dz^2",
            font_size=36
        ).next_to(title, DOWN, buff=0.5).to_corner(UL, buff=1.0) # Position near corner

        # Color-code terms
        metric_eq.set_color_by_tex_to_color_map({
            r"-c^2 dt^2": RED,
            r"dx^2": GREEN,
            r"dy^2": BLUE,
            r"dz^2": PURPLE,
            "ds^2": WHITE,
        })

        self.play(Write(metric_eq))
        self.wait(0.5)
        # Highlight/pulse the time component
        self.play(Indicate(metric_eq.get_part_by_tex("-c^2 dt^2"), color=RED, scale_factor=1.2), run_time=1.5)
        self.wait(2)

        # Keep metric equation for next scene potentially, store reference
        self.metric_eq = metric_eq
        # Clean up updater if scene ends
        spacetime_diagram.clear_updaters()


class Scene2_ClassicalEM_to_Relativistic(ThreeDScene):
    def construct(self):
        # Setup elements from Scene 1 (assuming sequential run or recreate)
        self.set_camera_orientation(phi=60 * DEGREES, theta=-45 * DEGREES, distance=10)
        self.camera.background_color = BLACK
        axes = ThreeDAxes(x_range=[-5, 5, 1], y_range=[-5, 5, 1], z_range=[-3, 3, 1], x_length=10, y_length=10, z_length=6)
        title = Text("QFT: Electromagnetic Interaction", font_size=24, weight=BOLD).to_corner(UL) # Smaller title
        metric_eq = MathTex(r"ds^2 = -c^2 dt^2 + dx^2 + dy^2 + dz^2", font_size=30).next_to(title, DOWN, buff=0.2).set_color_by_tex_to_color_map({r"-c^2 dt^2": RED, r"dx^2": GREEN, r"dy^2": BLUE, r"dz^2": PURPLE})

        self.add(axes, title, metric_eq) # Start with these elements present

        # Focus Shift: Zoom towards the origin using move_camera
        self.move_camera(
            frame_center=axes.c2p(0,0,0),
            zoom=1.67,  # Zoom factor (equivalent to distance/new_distance)
            run_time=2
        )
        self.wait(1)

        # Quantum Field Intro: E & B waves
        # Define propagation axis (e.g., z-axis)
        k_vec = axes.c2p(0,0,1) - axes.c2p(0,0,0) # Direction vector
        k_vec_normalized = k_vec / np.linalg.norm(k_vec)

        # E field wave (e.g., along x-axis) oscillating vertically (y-axis in plane)
        E_field_wave = axes.plot_parametric_curve(
            lambda t: axes.c2p(0.2 * np.cos(5*t), 0, t), # x=Amplitude*cos(kz), y=0, z=t (propagation)
            t_range = [-2.5, 2.5, 0.1],
            color = FIELD_E_COLOR,
            stroke_width=3
        ).set_opacity(0.7)

        # B field wave (e.g., along y-axis) oscillating horizontally (x-axis in plane)
        B_field_wave = axes.plot_parametric_curve(
             lambda t: axes.c2p(0, 0.2 * np.sin(5*t + PI/2), t), # y=Amplitude*sin(kz+phase), x=0, z=t
            t_range = [-2.5, 2.5, 0.1],
            color = FIELD_B_COLOR,
            stroke_width=3
        ).set_opacity(0.7) # Note: cos(x+pi/2) = -sin(x), used sin for perpendicular look

        # Propagation direction arrow
        prop_arrow = Arrow3D(start=axes.c2p(0,0,-2.5), end=axes.c2p(0,0,2.5), color=WHITE, thickness=0.02, base_radius=0.05)

        # Labels for E and B fields (use MathTex, position carefully)
        # Positioning 3D labels relative to curves requires care
        e_label = MathTex(r"\vec{E}", color=FIELD_E_COLOR).scale(0.8).move_to(axes.c2p(0.3, 0, 0)).rotate(PI/2, axis=RIGHT) # Adjust position and orientation
        b_label = MathTex(r"\vec{B}", color=FIELD_B_COLOR).scale(0.8).move_to(axes.c2p(0, 0.3, 0)).rotate(PI/2, axis=RIGHT) # Adjust position and orientation

        # Show the fields and labels
        self.play(LaggedStart(
            Create(E_field_wave),
            Create(B_field_wave),
            Create(prop_arrow),  # Changed from GrowArrow to Create for 3D arrow
            Write(e_label),
            Write(b_label),
            lag_ratio=0.5),
            run_time=3
        )
        # Add subtle oscillation animation (can be complex) or just leave static
        # For oscillation: could use updaters changing the phase/amplitude slightly

        self.wait(2)

        # Maxwell's Equations Morph
        classical_maxwell = MathTex(r"\nabla \times \vec{B} - \frac{1}{c^2} \frac{\partial \vec{E}}{\partial t} = \mu_0 \vec{J}", font_size=36)
        relativistic_maxwell = MathTex(r"\partial_\mu F^{\mu \nu}", "=", r"\mu_0 J^\nu", font_size=36)

        # Position initial equation
        classical_maxwell.next_to(axes, RIGHT, buff=1.5).shift(UP*1.5)
        self.play(Write(classical_maxwell))
        self.wait(1)

        # Morph Animation (Need careful alignment for TransformMatchingTex)
        # We'll place the target equation roughly where the source is
        relativistic_maxwell.move_to(classical_maxwell)

        # Create temporary paths or lines for connection (optional visual flair)
        # Could use ShowPassingFlash or custom lines animating between parts

        self.play(
            TransformMatchingTex(classical_maxwell, relativistic_maxwell,
                                 # Key map can help if direct matching fails, but often needs tweaking
                                 # key_map={...}
                                 ),
            run_time=3
        )
        self.wait(1)

        # Make the final equation persistent for next scene / zoom
        self.relativistic_maxwell_eq = relativistic_maxwell # Store reference
        self.fields_group = VGroup(E_field_wave, B_field_wave, prop_arrow, e_label, b_label) # Group fields

        # Zoom Node - Relativistic Maxwell
        self.play(Indicate(self.relativistic_maxwell_eq, color=YELLOW, scale_factor=1.1)) # Trigger
        self.wait(0.5)

        # Perform Zoom In using the corrected helper function
        zoom_data = zoom_animation(self, self.relativistic_maxwell_eq, zoom_scale=0.2, fade_opacity=0.1)

        # Add Annotations during Zoom
        # Note: Positioning annotations relative to zoomed objects can be tricky.
        # Using fix_in_frame() might be necessary if they drift, or calculating positions carefully.
        term_dm = self.relativistic_maxwell_eq.get_part_by_tex(r"\partial_\mu")
        term_F = self.relativistic_maxwell_eq.get_part_by_tex(r"F^{\mu \nu}")
        term_J = self.relativistic_maxwell_eq.get_part_by_tex(r"J^\nu")

        ann_dm = Tex(r"Four-gradient", font_size=24).next_to(term_dm, DOWN, buff=0.5)
        ann_F = Tex(r"EM Tensor", font_size=24).next_to(term_F, DOWN, buff=0.5)
        ann_J = Tex(r"Four-current", font_size=24).next_to(term_J, DOWN, buff=0.5)

        arrow_dm = Arrow(ann_dm.get_top(), term_dm.get_bottom(), buff=0.1, stroke_width=2, max_tip_length_to_length_ratio=0.1)
        arrow_F = Arrow(ann_F.get_top(), term_F.get_bottom(), buff=0.1, stroke_width=2, max_tip_length_to_length_ratio=0.1)
        arrow_J = Arrow(ann_J.get_top(), term_J.get_bottom(), buff=0.1, stroke_width=2, max_tip_length_to_length_ratio=0.1)

        # Group annotations and add .fix_in_frame() if they drift during camera moves
        annotations = VGroup(ann_dm, ann_F, ann_J, arrow_dm, arrow_F, arrow_J)
        # annotations.fix_in_frame() # Uncomment if annotations misbehave

        # Since zoomed, adjust annotation positions/scale if needed
        self.play(LaggedStart(*[FadeIn(m) for m in annotations], lag_ratio=0.3))
        self.wait(3)
        self.play(FadeOut(annotations))

        # Zoom Out using the corrected helper function
        zoom_out_animation(self, zoom_data)

        # Keep the relativistic Maxwell equation visible, move it
        self.play(self.relativistic_maxwell_eq.animate.scale(0.8).to_corner(UR))
        self.wait(1)

        # Store other potentially needed objects from this scene
        self.axes = axes


class Scene3_QEDLagrangian(ThreeDScene):
    def construct(self):
        # Setup (recreate or assume persistence)
        self.set_camera_orientation(phi=60 * DEGREES, theta=-45 * DEGREES, distance=8) # Slightly closer
        self.camera.background_color = BLACK
        axes = ThreeDAxes(
            x_range=[-5, 5, 1],
            y_range=[-5, 5, 1],
            z_range=[-3, 3, 1],
            x_length=10,
            y_length=10,
            z_length=6
        )
        title = Text("QFT: EM Interaction", font_size=24, weight=BOLD).to_corner(UL)

        # Create Maxwell equation
        maxwell_eq = VGroup(
            MathTex(r"\partial_\mu", font_size=30),
            MathTex(r"F^{\mu\nu}", font_size=30),
            MathTex("=", font_size=30),
            MathTex(r"\mu_0", font_size=30),
            MathTex(r"J^\nu", font_size=30)
        ).arrange(RIGHT, buff=0.1)
        maxwell_eq[1].set_color(YELLOW)  # Color the F term
        maxwell_eq.to_corner(UR)

        # Add elements to scene
        self.add(axes)
        self.add(title)
        self.add(maxwell_eq)
        self.relativistic_maxwell_eq = maxwell_eq  # Store reference

        # Introduction: QED Lagrangian - create terms separately
        # Use ** to match specific parts in MathTex for easier reference
        qed_terms = MathTex(
            r"\mathcal{L}_{\text{QED}}", "=",
            r"\bar{\psi}", r"(", "i", r"\gamma^\mu", r"D_\mu", "-", "m", r")", r"\psi",
            "-", r"\tfrac{1}{4}", r"F_{\mu\nu}", r"F^{\mu\nu}",
            substrings_to_isolate=[
                r"\mathcal{L}_{\text{QED}}",
                r"\bar{\psi}",
                r"\gamma^\mu",
                r"D_\mu",
                r"m",
                r"\psi",
                r"F_{\mu\nu}",
                r"F^{\mu\nu}"
            ],
            font_size=40
        )

        # Apply colors using substrings_to_isolate map
        qed_terms.set_color_by_tex_to_color_map({
            r"\bar{\psi}": ORANGE,
            r"\psi": ORANGE,
            r"\gamma^\mu": BLUE_C,
            r"D_\mu": GREEN,
            r"m": WHITE,
            r"F_{\mu\nu}": YELLOW,
            r"F^{\mu\nu}": YELLOW,
        })


        # Position the Lagrangian
        qed_terms.move_to(ORIGIN)

        # Create background plane
        padding = 0.5  # Add some padding around the text
        lagrangian_plane = Rectangle(
            width=qed_terms.width + padding,
            height=qed_terms.height + padding,
            fill_color=DARK_GRAY,
            fill_opacity=0.7,
            stroke_width=1,
            stroke_color=WHITE
        ).move_to(qed_terms)

        # Create group
        lagrangian_group = VGroup(lagrangian_plane, qed_terms)

        # Add elements one by one with explicit animations
        self.play(Create(lagrangian_plane))
        self.play(Write(qed_terms))
        self.wait(1)

        # Suggest dynamic fields with pulsing
        # Get indices of specific parts to highlight
        psi_bar_part = qed_terms.get_part_by_tex(r"\bar{\psi}")
        d_mu_part = qed_terms.get_part_by_tex(r"D_\mu")
        f_munu_part = qed_terms.get_part_by_tex(r"F_{\mu\nu}")
        
        self.play(Indicate(psi_bar_part, color=ORANGE), rate_func=there_and_back, run_time=1)
        self.play(Indicate(d_mu_part, color=GREEN), rate_func=there_and_back, run_time=1)
        self.play(Indicate(f_munu_part, color=YELLOW), rate_func=there_and_back, run_time=1)
        self.wait(1)

        # Connection - Fμν Term
        # Draw persistent arrow with explicit positions
        F_maxwell = maxwell_eq[1]  # Get the F term from Maxwell by index
        F_qed = qed_terms.get_part_by_tex(r"F^{\mu\nu}")
        
        connection_F = Arrow(
            start=F_maxwell.get_bottom(),
            end=F_qed.get_top() + LEFT * 0.1,
            stroke_width=4,
            color=CONNECTION_COLOR,
            buff=0.2
        )

        self.play(GrowArrow(connection_F))
        self.wait(1)

        # Store references for later use
        self.qed_lagrangian_group = lagrangian_group
        self.qed_lagrangian = qed_terms
        self.connection_F = connection_F

        # Zoom Node - QED Lagrangian
        self.play(Indicate(self.qed_lagrangian_group, color=YELLOW, scale_factor=1.05)) # Trigger
        self.wait(0.5)

        zoom_data = zoom_animation(self, self.qed_lagrangian_group, zoom_scale=0.25, fade_opacity=0.1)

        # Annotation (During Zoom)
        # Group terms for fermion part manually
        psi_bar_part = self.qed_lagrangian.get_part_by_tex(r"\bar{\psi}")
        psi_part = self.qed_lagrangian.get_part_by_tex(r"\psi")
        fermion_term_group = VGroup()
        fermion_term_group.add(psi_bar_part)
        # Add parts between psi_bar and psi
        for i in range(self.qed_lagrangian.index_of_part(psi_bar_part) + 1, self.qed_lagrangian.index_of_part(psi_part)):
            fermion_term_group.add(self.qed_lagrangian[i])
        fermion_term_group.add(psi_part)

        # Group field terms
        minus_sign_index = self.qed_lagrangian.submobjects.index(self.qed_lagrangian.get_part_by_tex("-", substring=False))
        f_munu_part = self.qed_lagrangian.get_part_by_tex(r"F_{\mu\nu}")
        f_munu_upper_part = self.qed_lagrangian.get_part_by_tex(r"F^{\mu\nu}")
        
        field_term_group = VGroup()
        for i in range(minus_sign_index, self.qed_lagrangian.index_of_part(f_munu_upper_part) + 1):
            field_term_group.add(self.qed_lagrangian[i])

        # Boxes around terms
        box_fermion = SurroundingRectangle(fermion_term_group, color=ORANGE, buff=0.1)
        box_field = SurroundingRectangle(field_term_group, color=GOLD, buff=0.1)

        # Labels for terms
        label_fermion = Tex("Fermion Dynamics + Mass", font_size=24).next_to(box_fermion, DOWN, buff=0.3)
        label_field = Tex("EM Field Dynamics", font_size=24).next_to(box_field, DOWN, buff=0.3)
        
        d_mu_part = self.qed_lagrangian.get_part_by_tex(r"D_\mu")
        label_interaction = Tex(r"Interaction (in $D_\mu = \partial_\mu + ieA_\mu$)", font_size=24).next_to(
            d_mu_part, UP, buff=0.3)

        annotations = VGroup(box_fermion, box_field, label_fermion, label_field, label_interaction)
        self.play(Create(box_fermion), Create(box_field), FadeIn(label_fermion), FadeIn(label_field), FadeIn(label_interaction))
        self.wait(3)

        # Gauge Invariance Animation (Conceptual)
        gauge_psi = MathTex(r"\psi \rightarrow e^{i \alpha(x)}\psi", font_size=28, color=ORANGE).next_to(label_fermion, DOWN, buff=0.5)
        gauge_A = MathTex(r"A_\mu \rightarrow A_\mu - \frac{1}{e}\partial_\mu \alpha(x)", font_size=28, color=GREEN).next_to(gauge_psi, DOWN, buff=0.3)
        
        # Create each line in the gauge text separately and arrange them
        gauge_text1 = Tex("Requires specific $D_\\mu$", font_size=24)
        gauge_text2 = Tex("Ensures $\\mathcal{L}$ unchanged (Invariance)", font_size=24)
        gauge_text3 = Tex("Leads to Charge Conservation", font_size=24)
        
        gauge_text_group = VGroup(gauge_text1, gauge_text2, gauge_text3).arrange(DOWN, aligned_edge=LEFT, buff=0.1).next_to(gauge_A, DOWN, buff=0.3)

        gauge_group = VGroup(gauge_psi, gauge_A, gauge_text_group)
        self.play(FadeIn(gauge_group))
        self.wait(4)
        self.play(FadeOut(annotations), FadeOut(gauge_group))

        # Zoom Out
        zoom_out_animation(self, zoom_data)
        self.wait(1)


class Scene4_FeynmanDiagram(ThreeDScene):
     def construct(self):
        # Setup (Assume persistent elements or recreate needed ones)
        # Look straight down (2D-like view) - use move_camera for smooth transition if needed
        # self.move_camera(phi=0, theta=-90*DEGREES, distance=8, run_time=1.5) # Animate camera change
        self.set_camera_orientation(phi=0, theta=-90*DEGREES, distance=8) # Or set directly if starting fresh
        self.camera.background_color = BLACK # Use black or a clean background

        # Maybe fade out previous complex 3D elements if focusing only on Feynman diagram
        # self.play(*[FadeOut(mob) for mob in self.mobjects]) # Quick clear stage

        # Get references needed for connections later (positions are crucial)
        # Assuming qed_lagrangian_group was positioned at ORIGIN in its scene
        qed_lagrangian_placeholder_pos = ORIGIN + DOWN*3 + LEFT*4 # Conceptual position, out of the way

        # Feynman Diagram: e- e- scattering (t-channel)
        v1 = np.array([-1, -1, 0]) # Vertex 1
        v2 = np.array([1, 1, 0]) # Vertex 2

        e_in1 = Line(v1 + LEFT*2 + DOWN*0.5, v1, color=ELECTRON_COLOR, stroke_width=5).add_tip(tip_length=0.2)
        e_in2 = Line(v2 + LEFT*2 + UP*0.5, v2, color=ELECTRON_COLOR, stroke_width=5).add_tip(tip_length=0.2) # Both coming from left

        # Wiggle line for photon
        photon = ParametricFunction(
             lambda t: v1 + (v2-v1)*t + RIGHT*0.15*np.sin(PI*t*5), # Wiggle perpendicular to v1-v2 line
            t_range = [0, 1],
            color=PHOTON_COLOR,
            stroke_width=4
        )

        e_out1 = Line(v1, v1 + RIGHT*2 + UP*0.5, color=ELECTRON_COLOR, stroke_width=5).add_tip(tip_length=0.2) # Scatter out
        e_out2 = Line(v2, v2 + RIGHT*2 + DOWN*0.5, color=ELECTRON_COLOR, stroke_width=5).add_tip(tip_length=0.2) # Scatter out

        # Labels
        label_e1 = MathTex("e^-", font_size=30, color=ELECTRON_COLOR).next_to(e_in1.get_start(), LEFT)
        label_e2 = MathTex("e^-", font_size=30, color=ELECTRON_COLOR).next_to(e_in2.get_start(), LEFT)
        label_p = MathTex(r"\gamma", font_size=30, color=PHOTON_COLOR).move_to(photon.get_center() + DOWN*0.4)
        label_e3 = MathTex("e^-", font_size=30, color=ELECTRON_COLOR).next_to(e_out1.get_end(), RIGHT)
        label_e4 = MathTex("e^-", font_size=30, color=ELECTRON_COLOR).next_to(e_out2.get_end(), RIGHT)

        diagram = VGroup(e_in1, e_in2, photon, e_out1, e_out2)
        labels = VGroup(label_e1, label_e2, label_p, label_e3, label_e4)

        feynman_group = VGroup(diagram, labels).scale(1.2).move_to(ORIGIN)

        self.play(LaggedStart(
            Create(e_in1), Create(e_in2),  # Changed from GrowArrow to Create
            Create(photon),
            Create(e_out1), Create(e_out2),  # Changed from GrowArrow to Create
            Write(labels),
            lag_ratio=0.4
        ), run_time=4)
        self.wait(1)

        # Explanation Text
        explanation_line1 = Tex("Feynman Diagram: Electron-electron scattering.", font_size=28)
        explanation_line2 = Tex("Lines represent particles, vertices represent interactions.", font_size=28)
        explanation_line3 = Tex(r"Photon ($\gamma$) mediates the electromagnetic force.", font_size=28)
        
        explanation = VGroup(explanation_line1, explanation_line2, explanation_line3)
        explanation.arrange(DOWN, aligned_edge=LEFT, buff=0.2).next_to(feynman_group, DOWN, buff=0.5)
        
        self.play(FadeIn(explanation))
        self.wait(2)

        # Identify vertex area for zoom (e.g., focus on v1)
        vertex_target_for_zoom = Dot(v1, radius=0.01).set_opacity(0)  # Invisible target at vertex v1
        self.add(vertex_target_for_zoom)  # Add temporarily for zoom target

        # Zoom Node - Feynman Vertex (Focus on interaction conceptually, e.g., one vertex v1)
        self.play(Indicate(VGroup(e_in1, e_out1, photon), color=YELLOW, scale_factor=1.1)) # Trigger - Indicate around vertex v1
        self.wait(0.5)

        # Use the invisible dot at v1 as the zoom target
        zoom_data = zoom_animation(self, vertex_target_for_zoom, zoom_scale=0.3, fade_opacity=0.1)

        # Annotation (During Zoom)
        vertex_label = Tex("Interaction Vertex", font_size=24).move_to(v1 + DOWN * 1.5) # Adjust position based on zoom
        vertex_role_e = Tex(r"$e^-$ emits/absorbs $\gamma$", font_size=24).next_to(vertex_label, DOWN, buff=0.2)

        annotations = VGroup(vertex_label, vertex_role_e)
        # annotations.fix_in_frame() # Consider if needed
        self.play(FadeIn(annotations))

        # Coupling Constant α
        alpha_approx = MathTex(r"\alpha \approx \frac{1}{137}", font_size=36).move_to(v1 + UP * 1.5) # Position near vertex
        # alpha_approx.fix_in_frame() # Consider if needed
        self.play(Write(alpha_approx))
        self.play(Flash(alpha_approx, color=RED, line_length=0.3, num_lines=12, time_width=0.3))
        self.wait(1)

        # Store alpha for later
        self.alpha_approx = alpha_approx

        # Connection to Lagrangian Interaction Term
        # Conceptual Position of Interaction term in Lagrangian (based on where it was in Scene 3)
        lagrangian_interaction_pos = qed_lagrangian_placeholder_pos + UP*0.2 # Rough guess

        connection_alpha = Arrow(
            start = alpha_approx.get_bottom(), # From coupling constant
            end = lagrangian_interaction_pos, # To conceptual interaction position
            color = CONNECTION_COLOR, stroke_width=4, buff=0.2
        )
        # Arrow Explanation
        alpha_connect_label = Tex("Interaction Strength", font_size=20, color=CONNECTION_COLOR).next_to(connection_alpha, RIGHT, buff=0.1).shift(DOWN*0.5)
        # alpha_connect_label.fix_in_frame() # Consider if needed

        connection_group = VGroup(connection_alpha, alpha_connect_label)
        self.play(GrowArrow(connection_alpha), FadeIn(alpha_connect_label))
        self.add(connection_group) # Keep persistent
        self.connection_alpha = connection_alpha # Store reference
        self.wait(2)

        # Evolve α to full definition
        alpha_full_tex = r"\alpha = \frac{e^2}{4 \pi \epsilon_0 \hbar c}"
        alpha_full = MathTex(alpha_full_tex, font_size=36).move_to(alpha_approx) # Match position
        alpha_full.set_color_by_tex_to_color_map({"e": YELLOW, r"\hbar": RED, "c": BLUE}) # Highlight constants
        # alpha_full.fix_in_frame() # Consider if needed

        self.play(TransformMatchingTex(alpha_approx, alpha_full, transform_mismatches=True), run_time=2) # Allow mismatches
        self.alpha_full = alpha_full # Store reference to the full version
        self.remove(alpha_approx) # Remove the old tex object explicitly after transform
        self.add(alpha_full) # Ensure the new one is added
        self.wait(2)

        self.play(FadeOut(annotations), FadeOut(connection_group)) # Clean up annotations and connection label before zoom out
        self.remove(connection_group) # Explicit remove

        # Zoom Out
        zoom_out_animation(self, zoom_data)
        self.remove(vertex_target_for_zoom) # Remove the temporary zoom target
        self.play(FadeOut(explanation)) # Remove text explanation now

        # Keep Feynman diagram and alpha visible
        self.feynman_group = feynman_group
        # Reposition alpha if needed after zoom out
        self.play(self.alpha_full.animate.scale(0.8).next_to(feynman_group, UP, buff=0.5))

        self.wait(1)


class Scene5_Renormalization(ThreeDScene):
    def construct(self):
        # Similar setup for continuity
        self.set_camera_orientation(phi=60 * DEGREES, theta=-45 * DEGREES, distance=7.5)
        self.camera.background_color = BLACK
        axes = ThreeDAxes(x_range=[-3, 3, 1], y_range=[-3, 3, 1], z_range=[-2, 2, 1],
                          x_length=6, y_length=6, z_length=4)
        title = Text("Renormalization: Charge and Energy Scale", font_size=24, weight=BOLD).to_corner(UL)

        self.add(axes, title)

        # Create a simple log scale function with safety checks
        def qed_alpha_running(energy_scale):
            """QED running coupling function with safety bounds to prevent overflow."""
            # Fine structure constant at rest
            alpha_0 = 1/137
            # Reference energy scale (electron mass in GeV)
            m_e = 0.000511
            # Energy scale normalized to electron mass, with bounds to prevent overflow
            safe_scale = np.clip(np.abs(energy_scale) / m_e, 1e-5, 1e10)
            # Log term with safety check to prevent extreme values
            log_term = np.log(safe_scale) / (2 * np.pi)
            # Limit the maximum correction to prevent overflow
            correction = np.clip(alpha_0 * log_term / 3, -0.5, 10)
            # Return the running coupling with a floor to prevent division by zero
            return alpha_0 / (1 - correction)
        
        # Create a more stable plot using a limited range
        energy_scale_min, energy_scale_max = 1e-2, 1e5
        
        # Create a numerically stable log scale
        def safe_log10(x):
            """Compute log10 with safety checks."""
            # Use np.log10 for calculation but clip input to prevent errors
            return np.log10(np.clip(x, 1e-10, 1e20))
        
        # Create axis values using log spacing for better stability
        x_values_plot = np.logspace(
            np.log10(energy_scale_min), 
            np.log10(energy_scale_max),
            100
        )
        
        # Compute the coupling values with safety checks
        y_values_plot = np.array([qed_alpha_running(x) for x in x_values_plot])
        
        # Scale the values for plotting to avoid extreme ranges
        # Map log scales to reasonable coordinate ranges
        x_range_plot = [-2, 5]  # Represents log10 of energy from 0.01 to 100,000
        y_range_plot = [0, 0.2]  # Coupling strength range
        
        # Compute scaled coordinates for plotting
        scaled_x = [(safe_log10(x) - safe_log10(energy_scale_min)) / 
                    (safe_log10(energy_scale_max) - safe_log10(energy_scale_min)) * 
                    (x_range_plot[1] - x_range_plot[0]) + x_range_plot[0] 
                    for x in x_values_plot]
        
        scaled_y = [min(y_range_plot[1], max(y_range_plot[0], y)) for y in y_values_plot]
        
        # Create plot points with the scaled values
        running_plot_points = [axes.coords_to_point(x, 0, y) for x, y in zip(scaled_x, scaled_y)]
        
        # Create the curve
        running_coupling_graph = VMobject()
        running_coupling_graph.set_points_smoothly(running_plot_points)
        running_coupling_graph.set_color(BLUE)
        running_coupling_graph.set_stroke(width=4)
        
        # Axis labels (simplified)
        x_label = MathTex("\\log_{10}(E/m_e)", font_size=24).next_to(axes.x_axis, RIGHT)
        y_label = MathTex("\\alpha(E)", font_size=24).next_to(axes.z_axis, UP)
        
        # Highlight points at different energy scales
        e_scales = [1, 100, 10000]  # Three scales to highlight
        
        # Compute and display points of interest with safety checks
        highlight_points = []
        for e in e_scales:
            alpha_val = qed_alpha_running(e)
            # Compute the log position with safety
            log_e = safe_log10(e)
            scaled_log_e = ((log_e - safe_log10(energy_scale_min)) / 
                          (safe_log10(energy_scale_max) - safe_log10(energy_scale_min)) * 
                          (x_range_plot[1] - x_range_plot[0]) + x_range_plot[0])
            
            # Use clipped alpha value to prevent overflow
            safe_alpha = min(y_range_plot[1], max(y_range_plot[0], alpha_val))
            
            # Create a point on the graph
            point = Dot3D(
                axes.coords_to_point(scaled_log_e, 0, safe_alpha),
                color=RED, radius=0.1
            )
            highlight_points.append(point)
        
        # Animate everything together
        self.play(Create(axes), Write(title))
        self.play(Create(x_label), Create(y_label))
        
        self.play(Create(running_coupling_graph), run_time=2)
        
        # Add highlight points one by one
        self.play(LaggedStart(*[Create(p) for p in highlight_points], lag_ratio=0.5))
        
        # Scale labels at highlighted points
        scale_labels = []
        for i, e in enumerate(e_scales):
            # Calculate the coupling at this scale with safety checks
            alpha_val = qed_alpha_running(e)
            scaled_alpha = min(0.2, max(0, alpha_val))  # Clamp to reasonable range
            
            # Create the label
            label = MathTex(f"E_{{{i+1}}} = {e}m_e", f"\\alpha = {scaled_alpha:.4f}", font_size=20)
            
            # Position label with a small offset from the highlight point
            label.next_to(highlight_points[i], RIGHT + UP, buff=0.2)
            scale_labels.append(label)
        
        # Add the labels with a staggered animation
        self.play(LaggedStart(*[Write(l) for l in scale_labels], lag_ratio=0.5))
        
        # Explanatory text about renormalization
        explanation1 = Tex("Quantum corrections cause coupling", "strength to change with energy scale.", font_size=24)
        explanation1.arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        explanation1.to_corner(UR)
        
        explanation2 = Tex("$\\alpha(E)$ increases at higher energies", "as virtual particles screen charge.", font_size=24)
        explanation2.arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        explanation2.next_to(explanation1, DOWN, buff=0.5)
        
        self.play(FadeIn(explanation1), run_time=1)
        self.play(FadeIn(explanation2), run_time=1)
        
        self.wait(3)
        
        # Fade everything except graph for transition
        items_to_keep = [running_coupling_graph]
        items_to_fade = [item for item in self.mobjects if item not in items_to_keep]
        
        self.play(
            *[FadeOut(item) for item in items_to_fade],
            running_coupling_graph.animate.scale(0.7).to_corner(DR)
        )
        
        # Keep a simplified version of the running coupling
        running_graph_simple = running_coupling_graph.copy().scale(0.7).set_stroke(width=3)
        self.add(running_graph_simple)
        self.remove(running_coupling_graph)
        
        # Label for the graph to refer back to it
        alpha_label_graph = MathTex("\\alpha(E)", font_size=24).next_to(running_graph_simple, UP)
        self.play(FadeIn(alpha_label_graph))
        
        self.wait(1)


class Scene6_Synthesis(ThreeDScene): # Back to 3D scene for final overview
    def construct(self):
        self.set_camera_orientation(phi=45 * DEGREES, theta=-60 * DEGREES, distance=20) # Start zoomed out
        self.camera.background_color = BLACK

        # Recreate or Place Persistent Elements for Final View
        # Need to position them nicely. Scales might need adjustment.

        # 1. Spacetime Grid (Simplified representation)
        axes = ThreeDAxes(x_range=[-3, 3, 1], y_range=[-3, 3, 1], z_range=[-2, 2, 1], x_length=6, y_length=6, z_length=4).shift(LEFT * 6 + DOWN * 3).set_opacity(0.3)

        # 2. Relativistic Maxwell Eq
        relativistic_maxwell_eq = MathTex(r"\partial_\mu F^{\mu \nu} = \mu_0 J^\nu", font_size=28).move_to(UP*3 + LEFT*4)
        relativistic_maxwell_eq.set_color_by_tex(r"F^{\mu \nu}", YELLOW)

        # 3. QED Lagrangian
        qed_lagrangian_tex = r"\mathcal{L}_{\text{QED}} = \bar{\psi}(i \gamma^\mu D_\mu - m)\psi - \tfrac{1}{4}F_{\mu\nu}F^{\mu\nu}"
        qed_lagrangian = MathTex(qed_lagrangian_tex, font_size=32).move_to(ORIGIN + UP*1)
        qed_lagrangian.set_color_by_tex_to_color_map(LAGRANGIAN_TERM_COLORS)

        # 4. Feynman Diagram (Simplified recreation)
        v1 = np.array([-0.5, -0.5, 0])
        v2 = np.array([0.5, 0.5, 0])
        e_in1 = Line(v1 + LEFT*1, v1, color=ELECTRON_COLOR, stroke_width=3).add_tip(tip_length=0.1)
        e_in2 = Line(v2 + LEFT*1, v2, color=ELECTRON_COLOR, stroke_width=3).add_tip(tip_length=0.1)
        photon = ParametricFunction(lambda t: v1 + (v2-v1)*t + RIGHT*0.1*np.sin(PI*t*5), t_range=[0, 1], color=PHOTON_COLOR, stroke_width=2.5)
        e_out1 = Line(v1, v1 + RIGHT*1, color=ELECTRON_COLOR, stroke_width=3).add_tip(tip_length=0.1)
        e_out2 = Line(v2, v2 + RIGHT*1, color=ELECTRON_COLOR, stroke_width=3).add_tip(tip_length=0.1)
        diagram = VGroup(e_in1, e_in2, photon, e_out1, e_out2)
        alpha_full = MathTex(r"\alpha \approx \frac{1}{137}", font_size=28).next_to(diagram.get_center()+RIGHT*0.5, UP, buff=0.1) # Simplified text near vertex
        feynman_group = VGroup(diagram, alpha_full).scale(1.0).move_to(DOWN*2.5 + RIGHT*4)

        # 5. Running Coupling Graph (Simplified view - 2D element in 3D scene)
        graph_axes_simple = Axes(x_range=[0,10], y_range=[0,1], x_length=3, y_length=2, tips=False, axis_config={"include_tip": False, "stroke_width": 1})
        graph_curve_simple = graph_axes_simple.plot(lambda x: 0.1 + 0.05*x, color=YELLOW, x_range=[0,10]) # Simple increasing line
        alpha_label_graph = MathTex(r"\alpha", font_size=20).next_to(graph_axes_simple.get_y_axis(), UP, buff=0.05)
        energy_label = MathTex("E", font_size=20).next_to(graph_axes_simple.get_x_axis(), RIGHT, buff=0.05)
        running_graph_simple = VGroup(graph_axes_simple, graph_curve_simple, alpha_label_graph, energy_label).scale(0.8).move_to(DOWN * 3 + LEFT * 4)
        # Position it flat on the XY plane by default, then maybe rotate slightly?
        running_graph_simple.rotate(5*DEGREES, axis=RIGHT) # Slight tilt for 3D view

        # Add all elements to the scene (start faded)
        elements = VGroup(axes, relativistic_maxwell_eq, qed_lagrangian, feynman_group, running_graph_simple).set_opacity(0)
        self.play(elements.animate.set_opacity(1), run_time=1.5)
        self.wait(1)

        # Ensure Connections are Visible
        # Recreate or update connection arrows using final positions

        # Connection F (Maxwell Fmunu to Lagrangian Fmunu)
        # Extract Maxwell F term - needs special handling since it's a substring
        maxwell_f_term_pos = relativistic_maxwell_eq.get_center() + RIGHT * 0.5 + DOWN * 0.1
        
        # Extract Lagrangian F term - again special handling for substrings in LaTeX
        f_munu_pos = qed_lagrangian.get_center() + RIGHT * 1 + UP * 0.1
        
        conn_F = Arrow(
            maxwell_f_term_pos,
            f_munu_pos,
            color=CONNECTION_COLOR, stroke_width=3, buff=0.2, max_tip_length_to_length_ratio=0.05
        )

        # Connection Alpha (Feynman Alpha to Lagrangian Interaction Dmu)
        # Need to extract D_mu position in Lagrangian
        d_mu_pos = qed_lagrangian.get_center() + LEFT * 0.5 + DOWN * 0.1
        
        conn_Alpha = Arrow(
            alpha_full.get_bottom(), # From alpha symbol near Feynman diagram
            d_mu_pos, # To interaction term D_mu
            color=CONNECTION_COLOR, stroke_width=3, buff=0.2, max_tip_length_to_length_ratio=0.05
        )

        # Connection Graph Alpha (Graph Alpha label to Feynman Alpha label)
        # Get the position directly
        graph_alpha_pos = alpha_label_graph.get_center() + running_graph_simple.get_center()
        conn_GraphAlpha = Arrow(
            graph_alpha_pos + RIGHT*0.1, # From alpha on graph (adjust start point slightly)
            alpha_full.get_left(), # To alpha near Feynman diagram
            color=CONNECTION_COLOR, stroke_width=3, buff=0.2, max_tip_length_to_length_ratio=0.05
        )

        connections = VGroup(conn_F, conn_Alpha, conn_GraphAlpha)
        self.play(LaggedStart(*[GrowArrow(c) for c in connections]), lag_ratio=0.5, run_time=2)
        self.wait(2)

        # Summary Text
        summary_title = Text(
            "QED: Unifying Light and Matter Through Gauge Theory",
            font_size=36,
            weight=BOLD
        ).to_edge(UP)
        summary_subtitle = Text(
            "A cornerstone of particle physics.",
            font_size=24
        ).next_to(summary_title, DOWN)

        self.play(Write(summary_title))
        self.play(FadeIn(summary_subtitle, shift=DOWN))
        self.wait(4)

        # Fade Out sequence
        self.play(
            FadeOut(summary_title),
            FadeOut(summary_subtitle),
            # Fade out connections first
            *[FadeOut(c) for c in connections],
            run_time=1.5
        )
        # Fade out conceptual elements
        self.play(LaggedStart(
            FadeOut(feynman_group),
            FadeOut(running_graph_simple),
            FadeOut(qed_lagrangian),
            FadeOut(relativistic_maxwell_eq),
            FadeOut(axes),
            lag_ratio=0.2
            ),
            run_time=3
        )

        # Optional: Pull camera back further
        self.move_camera(
            focal_distance=self.camera.get_focal_distance() * 1.5,
            run_time=2
        )  # Less extreme zoom out

        # Finale
        finis_text = Tex("Finis.", font_size=48, color=WHITE)
        self.play(FadeIn(finis_text))
        self.wait(3)
        self.play(FadeOut(finis_text))
        self.wait(1)


# To render scenes sequentially if this file is `qed_animation.py`:
# manim -pql qed_animation.py Scene1_SpacetimeContext Scene2_ClassicalEM_to_Relativistic Scene3_QEDLagrangian Scene4_FeynmanDiagram Scene5_Renormalization Scene6_Synthesis

# Notes for potential improvements:
# - Add actual starfield background ImageMobject.
# - Smoother 3D field oscillations using updaters.
# - More sophisticated glow/highlight effects.
# - Check compatibility with specific Manim v0.19 features (e.g., LogBase setup, Wiggle).
# - Refine positioning and scaling for visual balance, especially in Scene 6.
# - Consider adding sound effects or narration timings in comments.
# - Using a single scene class and controlling visibility/position is another structural option, potentially better for persistent connections across "scenes".
# - Ensure fix_in_frame() is used appropriately for text added during zooms if needed.