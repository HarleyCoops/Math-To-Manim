from manim import (
    # Base Scenes
    ThreeDScene,

    # Mobjects
    VGroup, Dot3D, Text, MathTex, Tex, ThreeDAxes, Surface, Circle,
    Arrow3D, Rectangle, Arrow, Line, VMobject, Axes, Dot,

    # Animations
    Write, Create, FadeIn, FadeOut, GrowArrow, LaggedStart, ReplacementTransform,
    TransformMatchingTex, GrowFromCenter, LaggedStartMap, ApplyMethod, AnimationGroup,

    # Constants & Utilities
    ORIGIN, UP, DOWN, RIGHT, LEFT, OUT, IN,
    UL, UR, DL,
    DEGREES, PI, TAU,
    BLACK, WHITE, GRAY_A, GRAY_B, GRAY_C,
    RED, RED_D, BLUE, BLUE_C, BLUE_D, GREEN, GREEN_D,
    ORANGE, YELLOW_A, YELLOW_B, YELLOW_C, YELLOW_D, TEAL, GOLD, PURPLE_D,
    BOLD,
    ValueTracker, always_redraw,
    StealthTip, # For Axes tips

    # Rate functions
    linear, there_and_back_with_pause
)
import numpy as np
import random # For star field positioning

# Define colors for consistency using the imported Manim colors
COLOR_TIME_COMPONENT = RED_D
COLOR_SPATIAL_COMPONENT_X = GREEN_D
COLOR_SPATIAL_COMPONENT_Y = BLUE_D
COLOR_SPATIAL_COMPONENT_Z = PURPLE_D

COLOR_E_FIELD = RED
COLOR_B_FIELD = BLUE

COLOR_PSI = ORANGE
COLOR_D_MU = GREEN
COLOR_GAMMA_MU = TEAL
COLOR_F_MUNU = GOLD

COLOR_ELECTRON = BLUE_C
COLOR_PHOTON = YELLOW_D

# Helper for star field generation
def create_star_field(num_stars=1000, R=50):
    stars = VGroup()
    for _ in range(num_stars):
        phi = random.uniform(0, 2 * PI)
        theta = np.arccos(random.uniform(-1, 1)) # Ensures uniform spherical distribution
        x = R * np.sin(theta) * np.cos(phi)
        y = R * np.sin(theta) * np.sin(phi)
        z = R * np.cos(theta)
        star_pos = np.array([x, y, z])

        star_size = random.uniform(0.005, 0.03)
        star_color = random.choice([GRAY_A, GRAY_B, GRAY_C, WHITE])

        stars.add(Dot3D(point=star_pos, radius=star_size, color=star_color, resolution=(3,3)))
    return stars

class QEDArtisticRendering(ThreeDScene):
    def construct(self):
        self.camera.background_color = BLACK
        self.set_camera_orientation(phi=75 * DEGREES, theta=30 * DEGREES, zoom=1.0)

        # Containers for elements that might be reused or referred to in the collage
        self.minkowski_layout_group = VGroup() # Axes, non-rotating parts
        self.em_fields_animation_group = VGroup()
        self.lagrangian_display_group = VGroup()
        self.feynman_diagram_group = VGroup()

        self.play_intro_sequence()
        self.play_minkowski_spacetime_sequence()
        self.play_quantum_fields_sequence()
        self.play_maxwell_equations_sequence()
        self.play_qed_lagrangian_sequence()
        self.play_gauge_invariance_sequence()
        self.play_feynman_diagram_sequence()
        self.play_running_coupling_sequence()
        self.play_final_collage_sequence()

    def play_intro_sequence(self):
        self.star_field = create_star_field(num_stars=1500, R=70)
        self.star_field.set_opacity(0)
        self.add(self.star_field)
        self.play(self.star_field.animate.set_opacity(0.8), run_time=4)

        self.play(self.move_camera(phi=60 * DEGREES, theta=-45 * DEGREES, zoom=1.0), run_time=2)

        title_line1 = Text("Quantum Field Theory:", font_size=48, weight=BOLD, color=WHITE)
        title_line2 = Text("A Journey into the Electromagnetic Interaction", font_size=36, weight=BOLD, color=WHITE)
        title = VGroup(title_line1, title_line2).arrange(DOWN, buff=0.3)
        title.move_to(ORIGIN)

        glow_title = title.copy() # Simple glow effect
        glow_title.set_stroke(YELLOW_A, width=10, opacity=0.5)

        self.title_mobject = VGroup(glow_title, title) # Ensure glow is behind
        self.add(self.title_mobject)
        self.play(Write(title), run_time=3) # Main title written on top of glow
        self.wait(1)

        self.play(
            self.title_mobject.animate.scale(0.4).to_corner(UL, buff=0.3),
            run_time=2
        )

    def play_minkowski_spacetime_sequence(self):
        self.axes_minkowski = ThreeDAxes(
            x_range=[-4, 4, 1], y_range=[-4, 4, 1], z_range=[-3, 3, 1], # Z represents 'ct'
            x_length=8, y_length=8, z_length=6,
            axis_config={"include_ticks": False, "include_tip": True, "tip_shape": StealthTip},
            tips=True,
        )
        axes_labels = self.axes_minkowski.get_axis_labels(
            MathTex("x", font_size=30), MathTex("y", font_size=30), MathTex("ct", font_size=30)
        )

        light_cone_res = (15,30)
        light_cone_future = Surface(
            lambda u, v: self.axes_minkowski.c2p(u * np.cos(v), u * np.sin(v), u),
            u_range=[0, 2.9], v_range=[0, TAU], resolution=light_cone_res,
            stroke_color=YELLOW_B, stroke_opacity=0.5, fill_opacity=0.15, fill_color=YELLOW_D,
            checkerboard_colors=False
        )
        light_cone_past = Surface(
            lambda u, v: self.axes_minkowski.c2p(u * np.cos(v), u * np.sin(v), -u),
            u_range=[0, 2.9], v_range=[0, TAU], resolution=light_cone_res,
            stroke_color=YELLOW_B, stroke_opacity=0.5, fill_opacity=0.15, fill_color=YELLOW_D,
            checkerboard_colors=False
        )

        self.light_cone_rotating_parts = VGroup(light_cone_future, light_cone_past)
        for t_val_abs in [1, 2, 2.8]:
            # Convert axis units to world units for circle radius
            origin_on_axis = self.axes_minkowski.x_axis.number_to_point(0)
            val_on_axis = self.axes_minkowski.x_axis.number_to_point(t_val_abs)
            radius_in_world_units = np.linalg.norm(val_on_axis - origin_on_axis)

            circle_future = Circle(radius=radius_in_world_units, color=YELLOW_C, stroke_width=1.5)
            circle_future.rotate(PI/2, RIGHT).move_to(self.axes_minkowski.c2p(0,0,t_val_abs))

            circle_past = Circle(radius=radius_in_world_units, color=YELLOW_C, stroke_width=1.5)
            circle_past.rotate(PI/2, RIGHT).move_to(self.axes_minkowski.c2p(0,0,-t_val_abs))
            self.light_cone_rotating_parts.add(circle_future, circle_past)

        self.light_cone_rotating_parts.add_updater(lambda mob, dt: mob.rotate(0.05 * dt, axis=self.axes_minkowski.z_axis.get_unit_vector()))

        metric_str = r"ds^2 = - (c dt)^2 + dx^2 + dy^2 + dz^2"
        self.metric_eq = MathTex(metric_str, font_size=34)
        self.metric_eq.set_color_by_tex_to_color_map({
            r"(c dt)^2": COLOR_TIME_COMPONENT, r"dx^2": COLOR_SPATIAL_COMPONENT_X,
            r"dy^2": COLOR_SPATIAL_COMPONENT_Y, r"dz^2": COLOR_SPATIAL_COMPONENT_Z
        })
        self.metric_eq.to_corner(UR, buff=0.3)
        self.add_fixed_in_frame_mobjects(self.metric_eq)

        self.minkowski_layout_group.add(self.axes_minkowski, axes_labels)
        self.play(Create(self.axes_minkowski), Write(axes_labels), run_time=2)
        self.add(self.light_cone_rotating_parts) # Add to scene so updater works
        self.play(Create(self.light_cone_rotating_parts), Write(self.metric_eq), run_time=3)

    def play_quantum_fields_sequence(self):
        self.play(self.camera.frame.animate.move_to(ORIGIN).scale(0.4), run_time=3)
        self.play(self.move_camera(phi=80 * DEGREES, theta=-100 * DEGREES), run_time=1.5)

        time_tracker = ValueTracker(0)
        amplitude, k_wave = 0.5, PI

        e_field_wave_func = lambda: Surface(
            lambda u, v: np.array([amplitude * np.sin(k_wave * v - time_tracker.get_value()), u, v]),
            u_range=[-1.5, 1.5], v_range=[-2.5, 2.5], fill_opacity=0.5, resolution=(20, 40),
            color=COLOR_E_FIELD, checkerboard_colors=False
        )
        b_field_wave_func = lambda: Surface(
            lambda u, v: np.array([u, amplitude * np.sin(k_wave * v - time_tracker.get_value()), v]),
            u_range=[-1.5, 1.5], v_range=[-2.5, 2.5], fill_opacity=0.5, resolution=(20, 40),
            color=COLOR_B_FIELD, checkerboard_colors=False
        )
        e_field_wave = always_redraw(e_field_wave_func)
        b_field_wave = always_redraw(b_field_wave_func)

        e_label = MathTex(r"\vec{E}", color=COLOR_E_FIELD, font_size=30).move_to(np.array([amplitude+0.7, -1.5, 0]))
        b_label = MathTex(r"\vec{B}", color=COLOR_B_FIELD, font_size=30).move_to(np.array([-1.5, amplitude+0.7, 0]))

        e_arrow_func = lambda: Arrow3D(ORIGIN, RIGHT * amplitude * np.sin(-time_tracker.get_value()), color=COLOR_E_FIELD, thickness=0.01, base_radius=0.02)
        b_arrow_func = lambda: Arrow3D(ORIGIN, UP * amplitude * np.sin(-time_tracker.get_value()), color=COLOR_B_FIELD, thickness=0.01, base_radius=0.02)
        e_arrow = always_redraw(e_arrow_func)
        b_arrow = always_redraw(b_arrow_func)

        prop_arrow = Arrow3D(OUT * -2.5, OUT * 2.5, color=WHITE, base_radius=0.03)
        prop_label = Tex("Wave Propagation", font_size=20).next_to(prop_arrow.get_end(), RIGHT, buff=0.1)

        self.em_fields_animation_group.add(e_field_wave, b_field_wave, e_label, b_label, e_arrow, b_arrow, prop_arrow, prop_label)
        self.play(LaggedStart(
            Create(e_field_wave), Create(b_field_wave), Write(e_label), Write(b_label),
            GrowArrow(e_arrow), GrowArrow(b_arrow), GrowArrow(prop_arrow), Write(prop_label), lag_ratio=0.3
            ), run_time=4
        )
        self.play(time_tracker.animate.set_value(3*TAU), run_time=6, rate_func=linear)
        time_tracker.set_value(0) # Reset for potential reuse

    def play_maxwell_equations_sequence(self):
        # Ensure metric_eq is removed from fixed_in_frame_mobjects before fading
        if hasattr(self, 'metric_eq') and self.metric_eq in self.fixed_in_frame_mobjects:
            self.remove_fixed_in_frame_mobjects(self.metric_eq)
        self.play(FadeOut(self.metric_eq), run_time=0.5)


        self.play(
            FadeOut(self.em_fields_animation_group),
            self.move_camera(frame_center=ORIGIN + OUT * 1.5, phi=0, theta=-PI/2, gamma=0, zoom=1.5),
            run_time=2
        )

        classical_eqs_tex = VGroup(
            MathTex(r"\nabla \cdot \vec{E} = \frac{\rho}{\epsilon_0}", font_size=36), # Corrected Gauss's Law for E
            MathTex(r"\nabla \cdot \vec{B} = 0", font_size=36),
            MathTex(r"\nabla \times \vec{E} = -\frac{\partial \vec{B}}{\partial t}", font_size=36),
            MathTex(r"\nabla \times \vec{B} = \mu_0 \vec{J} + \mu_0 \epsilon_0 \frac{\partial \vec{E}}{\partial t}", font_size=36) # Corrected Ampere-Maxwell
        ).arrange(DOWN, buff=0.3, aligned_edge=LEFT).move_to(LEFT * 4.5) # Shifted left more for longer equation
        classical_title = Tex("Maxwell's Equations (Classical Form)", font_size=24).next_to(classical_eqs_tex, UP, buff=0.3)

        relativistic_eq_tex = MathTex(r"\partial_\mu F^{\mu\nu} = \mu_0 J^\nu", font_size=48).move_to(RIGHT * 3.5)
        relativistic_title = Tex("Relativistic Compact Form", font_size=24).next_to(relativistic_eq_tex, UP, buff=0.3)

        self.play(Write(classical_eqs_tex), Write(classical_title), run_time=3)
        self.wait(1.5)

        # For a smoother transition, let's transform symbols instead of just copy-fading
        self.play(
            TransformMatchingTex(classical_eqs_tex, relativistic_eq_tex, path_arc=-PI/3), # Use TransformMatchingTex
            FadeOut(classical_title), Write(relativistic_title),
            run_time=3
        )
        self.wait(2)
        self.maxwell_relativistic_display_group = VGroup(relativistic_eq_tex, relativistic_title)


    def play_qed_lagrangian_sequence(self):
        self.play(
            FadeOut(self.maxwell_relativistic_display_group),
            self.move_camera(frame_center=ORIGIN, phi=70 * DEGREES, theta=-70 * DEGREES, zoom=1.0),
            self.star_field.animate.set_opacity(0.5),
            self.title_mobject.animate.set_opacity(0.3),
            run_time=2
        )
        self.minkowski_layout_group.set_opacity(0.6)
        self.light_cone_rotating_parts.set_opacity(0.4)

        qed_lagrangian_str = r"\mathcal{L}_{\text{QED}} = \bar{\psi}(i\gamma^\mu D_\mu - m)\psi - \frac{1}{4}F_{\mu\nu}F^{\mu\nu}"
        lagrangian_math = MathTex(qed_lagrangian_str, font_size=40)
        lagrangian_math.set_color_by_tex_to_color_map({
            r"\psi": COLOR_PSI, r"\bar{\psi}": COLOR_PSI, r"D_\mu": COLOR_D_MU,
            r"\gamma^\mu": COLOR_GAMMA_MU, r"F_{\mu\nu}F^{\mu\nu}": COLOR_F_MUNU # Corrected key for FmunuFmunu
        })

        plane_bg = Rectangle(
            width=lagrangian_math.width + 1, height=lagrangian_math.height + 0.8,
            fill_color=BLACK, fill_opacity=0.7, stroke_color=GRAY_C, stroke_width=2 # Used GRAY_C
        ).move_to(lagrangian_math.get_center())

        self.lagrangian_display_group.add(plane_bg, lagrangian_math)
        self.lagrangian_display_group.move_to(ORIGIN + OUT * 0.5).rotate(15 * DEGREES, axis=RIGHT).rotate(10 * DEGREES, axis=UP)

        self.play(FadeIn(self.lagrangian_display_group, shift=IN*0.5), run_time=2.5)

        # Pulsing effect by targeting sub-mobjects
        psi_terms = lagrangian_math.get_parts_by_tex(r"\psi")
        Dmu_term = lagrangian_math.get_parts_by_tex(r"D_\mu")
        gamma_term = lagrangian_math.get_parts_by_tex(r"\gamma^\mu")
        Fmunu_term = lagrangian_math.get_parts_by_tex(r"F_{\mu\nu}F^{\mu\nu}") # Ensure this selects the Fmunu part


        self.play(
            LaggedStart(
                *[term.animate(rate_func=there_and_back_with_pause, n_cycles=3).scale(1.1) for term_group in [psi_terms, Dmu_term, gamma_term, Fmunu_term] for term in term_group],
                lag_ratio=0.1
            ),
            run_time=3
        )


    def play_gauge_invariance_sequence(self):
        psi_trans_str = r"\psi \rightarrow \psi' = e^{i\alpha(x)}\psi"
        gauge_trans_math = MathTex(psi_trans_str, font_size=30, color=WHITE)
        gauge_trans_math.set_color_by_tex_to_color_map({r"\psi": COLOR_PSI, r"e^{i\alpha(x)}": YELLOW_A})
        gauge_trans_math.to_edge(DL, buff=0.5)
        self.add_fixed_in_frame_mobjects(gauge_trans_math)

        self.play(Write(gauge_trans_math), run_time=2)

        charge_conserv_text = Tex(r"Gauge Invariance $\Rightarrow$ Charge Conservation", font_size=24, color=YELLOW_C)
        charge_conserv_text.next_to(gauge_trans_math, DOWN, buff=0.3, aligned_edge=LEFT)
        self.add_fixed_in_frame_mobjects(charge_conserv_text)

        arrow_explain = Arrow(gauge_trans_math.get_bottom(), charge_conserv_text.get_top(), buff=0.1, color=WHITE, stroke_width=3)
        self.add_fixed_in_frame_mobjects(arrow_explain)

        self.play(Write(charge_conserv_text), Create(arrow_explain), run_time=1.5)
        self.wait(2.5)
        self.gauge_extras_fixed_group = VGroup(gauge_trans_math, charge_conserv_text, arrow_explain)

    def play_feynman_diagram_sequence(self):
        if hasattr(self, 'gauge_extras_fixed_group') and self.gauge_extras_fixed_group:
            for item in self.gauge_extras_fixed_group:
                if item in self.fixed_in_frame_mobjects: self.remove_fixed_in_frame_mobjects(item)
            self.play(FadeOut(self.gauge_extras_fixed_group), run_time=0.5)

        self.play(
            FadeOut(self.lagrangian_display_group),
            self.star_field.animate.set_opacity(0.7),
            self.title_mobject.animate.set_opacity(0.7),
            self.move_camera(frame_center=ORIGIN, phi=0, theta=-PI/2, gamma=0, zoom=1.2),
            run_time=2
        )
        self.play(
            self.minkowski_layout_group.animate.set_opacity(0.1),
            self.light_cone_rotating_parts.animate.set_opacity(0.1),
            run_time=1
        )

        v_sep, h_sep_v, h_sep_ext = 0.6, 0.8, 2.5 # Define vertex separation and line lengths
        v1_pos, v2_pos = LEFT*h_sep_v, RIGHT*h_sep_v # Simplified central vertices for straight photon

        e1_start = LEFT*h_sep_ext + UP*v_sep
        e2_start = LEFT*h_sep_ext + DOWN*v_sep
        e1_end = RIGHT*h_sep_ext + UP*v_sep
        e2_end = RIGHT*h_sep_ext + DOWN*v_sep

        e_line_cfg = {"color": COLOR_ELECTRON, "stroke_width": 6}
        e1_in = Line(e1_start, v1_pos, **e_line_cfg)
        e2_in = Line(e2_start, v1_pos, **e_line_cfg) # Electrons meet at same vertex for this simpler e-e- -> e-e-
        e1_out = Line(v2_pos, e1_end, **e_line_cfg)
        e2_out = Line(v2_pos, e2_end, **e_line_cfg) # Electrons exit from same vertex

        for line in [e1_in, e2_in, e1_out, e2_out]: line.add_tip(tip_length=0.2)

        photon_path_obj = VMobject(color=COLOR_PHOTON, stroke_width=5)
        photon_points = [v1_pos]
        num_wiggles, wiggle_amp = 7, 0.18
        line_vec = v2_pos - v1_pos
        perp_vec = rotate_vector(normalize(line_vec), PI/2) * wiggle_amp

        for i in range(1, num_wiggles * 2 ): # more points for smoothness
            frac = i / (num_wiggles * 2)
            base_pt = v1_pos + frac * line_vec
            wiggle_offset_val = np.sin(frac * num_wiggles * PI) # Smooth sine wave
            photon_points.append(base_pt + perp_vec * wiggle_offset_val)
        photon_points.append(v2_pos)
        photon_line = photon_path_obj.set_points_smoothly(photon_points)


        lbl_e = MathTex("e^-", color=COLOR_ELECTRON, font_size=30)
        lbl_g = MathTex(r"\gamma", color=COLOR_PHOTON, font_size=30)
        labels = VGroup(
            lbl_e.copy().next_to(e1_in.get_start(), LEFT, buff=0.1),
            lbl_e.copy().next_to(e2_in.get_start(), LEFT, buff=0.1),
            lbl_e.copy().next_to(e1_out.get_end(), RIGHT, buff=0.1),
            lbl_e.copy().next_to(e2_out.get_end(), RIGHT, buff=0.1),
            lbl_g.copy().move_to(photon_line.get_center() + UP*0.3) # position label nicely on photon line
        )
        diagram = VGroup(e1_in, e2_in, e1_out, e2_out, photon_line).scale(1.1).center() # Scale after creation
        self.feynman_diagram_group.add(diagram, labels) # Add labels to group

        self.play(
            LaggedStart(Create(e1_in), Create(e2_in), Create(e1_out), Create(e2_out), lag_ratio=0.4),
            Create(photon_line), Write(labels), run_time=4
        )

        fyn_texts = VGroup(
            Tex("Electron-electron scattering", font_size=24),
            Tex("Photon: carrier of the electromagnetic force", font_size=24)
        ).arrange(DOWN, aligned_edge=LEFT).to_corner(UL, buff=0.5)
        self.add_fixed_in_frame_mobjects(fyn_texts)
        self.play(Write(fyn_texts), run_time=2); self.wait(2)

        alpha_approx = MathTex(r"\alpha \approx \frac{1}{137}", font_size=36).next_to(diagram, UP, buff=0.5)
        alpha_symbolic = MathTex(r"\alpha = \frac{e^2}{4\pi\epsilon_0\hbar c}", font_size=36).move_to(alpha_approx)
        self.feynman_diagram_group.add(alpha_symbolic)

        self.play(Write(alpha_approx), run_time=1.5)
        self.play(LaggedStart(*[alpha_approx.animate.set_opacity(val) for _ in range(3) for val in (0.2,1.0)], lag_ratio=0.1), run_time=1.2)
        self.wait(0.5)
        self.play(TransformMatchingTex(alpha_approx, alpha_symbolic, path_arc=-PI/2), run_time=2.5)
        self.wait(2)
        self.feynman_fixed_texts = fyn_texts


    def play_running_coupling_sequence(self):
        # Clean up previous scene elements carefully
        to_fade = VGroup()
        # Remove fixed texts
        if hasattr(self, 'feynman_fixed_texts') and self.feynman_fixed_texts:
            for item in self.feynman_fixed_texts:
                if item in self.fixed_in_frame_mobjects:
                    self.remove_fixed_in_frame_mobjects(item)
            to_fade.add(self.feynman_fixed_texts)

        # Fade main feynman diagram, but keep alpha_symbolic with the group for now.
        alpha_symbolic_temp = None
        if self.feynman_diagram_group and len(self.feynman_diagram_group) > 0 and self.feynman_diagram_group[-1].tex_string == r"\alpha = \frac{e^2}{4\pi\epsilon_0\hbar c}":
             alpha_symbolic_temp = self.feynman_diagram_group.pop()

        to_fade.add(self.feynman_diagram_group)

        self.play(
            FadeOut(to_fade),
            self.move_camera(frame_center=ORIGIN, phi=0, theta=-PI/2, gamma=0, zoom=1.0),
            run_time=1.5
        )
        if alpha_symbolic_temp: # Add it back to the group after fading out the rest
            self.feynman_diagram_group.add(alpha_symbolic_temp)


        axes_cfg = {
            "x_range": [0, 10, 2], "y_range": [0.0072, 0.0080, 0.0002], # Log scale would be more accurate but Q specified this way.
            "x_length": 9, "y_length": 5.5,
            "axis_config": {"include_numbers": True, "decimal_number_config": {"num_decimal_places": 4}},
            "tips": False
        }
        axes = Axes(**axes_cfg).add_coordinates()
        x_lbl = axes.get_x_axis_label(Tex("Energy Scale (e.g., log Q/GeV)"), edge=DOWN, buff=0.4)
        y_lbl = axes.get_y_axis_label(Tex(r"Coupling Strength $\alpha(Q)$").rotate(PI/2), edge=LEFT, buff=0.4)

        graph_ttl = Tex("Running of QED Coupling Constant $\\alpha(Q)$", font_size=28).to_edge(UP, buff=0.3)
        self.play(Create(axes), Write(x_lbl), Write(y_lbl), Write(graph_ttl), run_time=3)

        # More realistic QED running (very slight logarithmic increase)
        # For visualization, we'll exaggerate it slightly within the given y-range.
        def qed_alpha_fn(log_q_scaled): # log_q_scaled from 0 to 10
            # Alpha at Z pole (~91 GeV) is ~1/128. At low energy (Thomson limit) ~1/137.036
            # Let's map x_range (0-10) to a conceptual energy range
            # alpha(Q^2) = alpha(0) / (1 - (alpha(0) / (3*PI)) * log(Q^2/m_e^2))
            # This is just a qualitative increasing curve.
            return 0.007297 + 0.000007 * log_q_scaled**1.2 # Mildly increasing

        curve = axes.plot(qed_alpha_fn, color=YELLOW_D, x_range=[axes_cfg["x_range"][0]+0.1, axes_cfg["x_range"][1]-0.1]) # avoid edges
        self.play(Create(curve), run_time=2.5)

        dots = VGroup(*[Dot(axes.c2p(x, qed_alpha_fn(x)), color=RED_C, radius=0.06) for x in [1.5, 4.5, 7.5, 9.5]])
        self.play(LaggedStartMap(GrowFromCenter, dots, lag_ratio=0.3), run_time=2)

        caption = Tex(
            r"$\alpha$ increases slightly with energy due to vacuum polarization:",
            r"virtual $e^+e^-$ pairs screen the 'bare' charge at larger distances (lower energies).",
            tex_environment="flushleft", font_size=20
        ).set_width(axes.width * 0.9).next_to(axes, DOWN, buff=0.5)
        self.play(Write(caption), run_time=2.5); self.wait(3)
        self.running_graph_display_group = VGroup(axes, x_lbl, y_lbl, graph_ttl, curve, dots, caption)


    def play_final_collage_sequence(self):
        self.play(FadeOut(self.running_graph_display_group), run_time=1)
        if hasattr(self, 'title_mobject') and self.title_mobject:
            if self.title_mobject in self.mobjects : self.play(FadeOut(self.title_mobject), run_time=0.5) # only fade if still on screen

        # Prepare elements for collage - ensure they are correctly positioned and scaled for the final view
        collage_spacetime_elements = VGroup(self.minkowski_layout_group, self.light_cone_rotating_parts)
        # Position these elements before fading them in for the collage
        collage_spacetime_elements.move_to(ORIGIN + DOWN*0.5).scale(0.8)

        # Make EM fields animation visible again - if it was fully faded
        # For always_redraw objects, they should just become visible again if added.
        # Or recreate if easier (but let's try to reuse)
        self.em_fields_animation_group.move_to(LEFT*3.5 + UP*2.2).scale(0.3).set_opacity(0) # Start hidden

        self.lagrangian_display_group.move_to(RIGHT*3.5 + UP*2).scale(0.6).rotate(15*DEGREES,LEFT).set_opacity(0)

        # Feynman diagram group should still have alpha_symbolic. We need just the diagram part.
        # If alpha_symbolic is the last item and you only want the diagram
        feynman_diagram_visuals = self.feynman_diagram_group[0] if self.feynman_diagram_group else VGroup()
        feynman_diagram_visuals.move_to(DOWN*2.5 + RIGHT*0.5).scale(0.5).set_opacity(0)


        self.play(self.star_field.animate.set_opacity(0.8), run_time=1)
        self.play(
            self.move_camera(frame_center=ORIGIN + OUT*1, phi=65*DEGREES, theta=-45*DEGREES, zoom=2.2),
            AnimationGroup(
                 ApplyMethod(collage_spacetime_elements.set_opacity, 1),
                 FadeIn(self.em_fields_animation_group, shift=LEFT*0.2, scale=1.1),
                 FadeIn(self.lagrangian_display_group, shift=RIGHT*0.2, scale=1.1),
                 FadeIn(feynman_diagram_visuals, shift=UP*0.2, scale=1.1),
                 lag_ratio=0.2
            ), run_time=4
        )
        self.wait(1.5)

        summary_txt_str = "QED: Unifying Light and Matter Through Gauge Theory"
        summary_txt = Text(summary_txt_str, font_size=36, weight=BOLD, color=YELLOW_C)
        summary_glow = summary_txt.copy().set_stroke(YELLOW_A, width=8, opacity=0.4)
        final_summary_display = VGroup(summary_glow, summary_txt).move_to(UP*3.2) # Adjusted position
        self.add_fixed_in_frame_mobjects(final_summary_display)

        self.play(Write(final_summary_display), run_time=3); self.wait(2.5)
        self.play(self.camera.frame.animate.scale(1.8).move_to(OUT*10 + UP*1), run_time=5)

        if hasattr(self, 'light_cone_rotating_parts'): self.light_cone_rotating_parts.clear_updaters()
        # Objects with always_redraw (like EM fields) will be handled by FadeOut correctly.
        # Ensure all fixed objects are removed before final fade
        if final_summary_display in self.fixed_in_frame_mobjects:
            self.remove_fixed_in_frame_mobjects(final_summary_display)

        self.play(
            LaggedStart(
                FadeOut(self.em_fields_animation_group), FadeOut(self.lagrangian_display_group),
                FadeOut(feynman_diagram_visuals), # Fade out the visual part shown in collage
                FadeOut(self.minkowski_layout_group),
                FadeOut(self.light_cone_rotating_parts),
                FadeOut(final_summary_display), # The one in the scene, not fixed
                lag_ratio=0.2
            ), run_time=3.5
        )
        self.wait(1)

        finis_txt = Tex("Finis", font_size=48, color=WHITE)
        # self.add_fixed_in_frame_mobjects(finis_txt) # Not needed if just displaying and fading
        self.play(Write(finis_txt), run_time=2); self.wait(2.5)
        self.play(FadeOut(finis_txt), self.star_field.animate.set_opacity(0), run_time=2)
        self.wait(1)