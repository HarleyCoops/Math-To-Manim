from manim import *
import numpy as np

class GravitationalWaveVisualization(ThreeDScene):
    def construct(self):
        # --- Scene Setup (as before, but with timing annotations) ---

        # --- Background (0-5 seconds) ---
        num_stars = 200
        star_positions = np.random.uniform(-7, 7, size=(num_stars, 3))
        stars = VGroup(*[Dot(point=pos, radius=0.01 + 0.08*np.random.random(), color=WHITE, fill_opacity=0.2 + 0.8*np.random.random())
                         for pos in star_positions])
        background = Rectangle(width=20, height=20, color = BLACK, fill_opacity =1).set_z_index(-2)
        self.add(background)
        self.add(stars)

        # --- Spacetime Grid (fade in 5-8 seconds) ---
        grid = NumberPlane(
            x_range=(-10, 10, 1),
            y_range=(-10, 10, 1),
            background_line_style={
                "stroke_color": TEAL,
                "stroke_width": 1,
                "stroke_opacity": 0.5
            }
        )
        self.play(FadeIn(grid), run_time=3)  # Slow fade-in
        self.wait(2)  # Pause for a moment (total time: 10 seconds)

        # --- ValueTrackers ---
        time_tracker = ValueTracker(0)
        amplitude_tracker = ValueTracker(0.1)
        frequency_tracker = ValueTracker(1)

        # --- Grid Transformation ---
        def grid_transform(point):
            x, y, z = point
            t = time_tracker.get_value()
            A = amplitude_tracker.get_value()
            f = frequency_tracker.get_value()
            k = 2
            r = np.sqrt(x**2 + y**2)
            if r == 0:
                return np.array([x, y, z])
            displacement_x = A / r * np.cos(2 * PI * f * (r - k * t))
            displacement_y = A / r * np.sin(2 * PI * f * (r - k * t))
            return np.array([x + displacement_x, y + displacement_y, z])

        grid.add_updater(lambda m: m.apply_function(grid_transform))


        # --- Pulse (10-25 seconds) ---
        pulse = Circle(radius=0.1, color=WHITE, fill_opacity=0.5).move_to(grid.c2p(0,0,0))
        self.add(pulse)

        def pulse_updater(mob, dt):
           mob.scale(1 + 0.5 * dt )
           current_opacity = mob.get_fill_opacity()
           if current_opacity - (0.07 * dt) >0:
                mob.set_fill_opacity(current_opacity - (0.5 * dt ))


        pulse.add_updater(pulse_updater)


        # --- Data Overlays (Introduce Gradually) ---
        far_text = MathTex(r"\text{FAR} = 1.267 \times 10^{-9} \, \text{Hz}").to_corner(UL)
        event_time_text = MathTex(r"t_0 = \text{Event Time}").next_to(far_text, DOWN)
        chirp_mass_text = MathTex(r"\mathcal{M} = \text{Chirp Mass}").next_to(event_time_text, DOWN)
        data_group = VGroup(far_text, event_time_text, chirp_mass_text)

        # Fade them in sequentially with delays
        self.play(FadeIn(far_text), run_time=2)        # 10-12 seconds
        self.wait(1)  # (13 seconds)
        self.play(FadeIn(event_time_text), run_time=2) # 13-15 seconds
        self.wait(1)  # (16 seconds)
        self.play(FadeIn(chirp_mass_text), run_time=2)  # 16-18 seconds
        self.wait(7) #  Allow viewing time (total time so far 25 s)



        # --- Sky Projection (25-45 seconds: Setup, 45-90: Animation)---

        self.move_camera(phi=75 * DEGREES, theta=-45 * DEGREES)
        axes = ThreeDAxes()
        self.add(axes)

        def mollweide_projection(theta, phi):
            phi_rad = np.deg2rad(phi) * np.cos(np.deg2rad(theta))
            x = 2 * np.sqrt(2) / PI * phi_rad
            y = np.sqrt(2) * np.sin(np.deg2rad(theta))
            return np.array([x, y, 0])

        gaussian_center_theta = 30
        gaussian_center_phi = 45
        gaussian_sigma_theta = 15
        gaussian_sigma_phi = 20

        def bivariate_gaussian(theta, phi):
            prob = np.exp(-((theta - gaussian_center_theta)**2 / (2 * gaussian_sigma_theta**2) +
                           (phi - gaussian_center_phi)**2 / (2 * gaussian_sigma_phi**2)))
            return prob

        sky_map = Surface(
            lambda u, v: np.array([
                mollweide_projection(u,v)[0],
                mollweide_projection(u,v)[1],
                bivariate_gaussian(u, v)  *0.3
            ]),
            u_range=(0, 180),
            v_range=(-90, 90),
            resolution=(25, 25),
            fill_color=BLUE,
            fill_opacity=0.7,
            stroke_color = BLUE
        )

        sky_map.set_style(fill_opacity=0.7)
        sky_map.set_fill_by_checkerboard(BLUE, YELLOW, opacity=0.7)

        self.play(Create(sky_map), run_time=5)  # 25-30 seconds (longer creation time)
        self.wait(15)  # give adequate time for showing the full-fledged sky_map.

        # --- Detector Locations ---
        detector_locations = {
            "LIGO Hanford": (46.45, -119.4),
            "LIGO Livingston": (30.56, -90.77),
            "Virgo": (43.63, 10.5)
        }
        detector_markers = VGroup()
        for name, (lat, lon) in detector_locations.items():
           marker_position_projected = mollweide_projection( lat,lon )
           marker = Dot(marker_position_projected , color=RED)
           label = Text(name, font_size=14).next_to(marker, UP)
           detector_markers.add(marker, label)

        #  Add Detector Locations (and their Labels) Sequentially
        for marker_label_pair in detector_markers: # 45 - ~60
          self.play(Create(marker_label_pair),run_time=2.5)  # Introduce slowly
          self.wait(2.5)  # Give viewing time


        center_marker_sky_position = mollweide_projection(gaussian_center_theta, gaussian_center_phi)

         # --- Connecting Lines  (~60 - 75 seconds) ---
         # now connect sequentially
        for name, (lat,lon) in detector_locations.items():
            start_line_position = mollweide_projection(lat,lon)
            connecting_line = Line(start_line_position, center_marker_sky_position, color=YELLOW)

            # Show and Leave Up
            self.play(Create(connecting_line), run_time=2)
            self.wait(3) # leave this on the screen a little longer than the locations themselves.


        # --- Combined Animation and Slow Downs (75-120+ seconds) ---
        self.play(
            time_tracker.animate.set_value(50),  # Longer time
            amplitude_tracker.animate.set_value(1.8), #slightly greater amplitude
            frequency_tracker.animate.set_value(3),
            run_time=45,   # Longer combined animation
            rate_func=slow_into,  # slow ramp for clarity.
        )
        self.wait(10)  # Allow final state to be seen

        # --- Fade Out (130-140 seconds) ---
        self.play(*[FadeOut(mob) for mob in self.mobjects], run_time=10)  # Slow fade out
        self.wait(5) # final black

        # Final Time: ~ 145 s