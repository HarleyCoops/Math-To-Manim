from manim import *
import numpy as np

class EpicBlackHoleAdventure(Scene):
    def construct(self):
        # Set a pure black background for the cosmic void
        self.camera.background_color = BLACK

        # **1) Subtle Gradient Background**
        # Create a large rectangle to cover the frame, with a faint radial gradient for depth
        gradient_rect = Rectangle(
            width=config.frame_width * 2,
            height=config.frame_height * 2
        )
        gradient_rect.set_fill(
            color=[BLACK, "#111111"],  # Subtle gray gradient
            opacity=1
        )
        gradient_rect.set_stroke(width=0)
        gradient_rect.move_to(ORIGIN)
        self.add(gradient_rect)

        # **2) Enhanced Twinkling Star Field with Parallax**
        num_stars = 300
        star_field = VGroup()
        for _ in range(num_stars):
            x = np.random.uniform(-10, 10)
            y = np.random.uniform(-6, 6)
            star = Dot(
                point=[x, y, 0],
                radius=0.015,
                color=WHITE,
                fill_opacity=np.random.uniform(0.2, 0.9)
            )
            # Store initial position and "depth" for parallax
            star.depth = np.random.uniform(0.5, 2.0)  # Depth factor
            star.initial_pos = star.get_center()
            star_field.add(star)
        self.add(star_field)

        # Twinkle updater with smooth pulsation
        def twinkle_updater(star, dt):
            new_radius = 0.015 + 0.01 * np.sin(4 * self.time + star.initial_pos[0])
            star.set_radius(abs(new_radius))

        # Parallax updater for depth effect during camera motion
        def parallax_updater(star, dt):
            # Simulate camera movement toward the black hole
            camera_shift = np.sin(self.time * 0.1) * 0.05
            new_pos = star.initial_pos / star.depth + [camera_shift, 0, 0]
            star.move_to(new_pos)

        for star in star_field:
            star.add_updater(twinkle_updater)
            star.add_updater(parallax_updater)

        # **3) Black Hole Core (Event Horizon)**
        black_hole_core = Circle(radius=1.5, color=BLACK, fill_opacity=1).move_to(ORIGIN)
        glow_ring = Circle(radius=1.52, color=GRAY, fill_opacity=0, stroke_width=2)
        self.add(black_hole_core, glow_ring)

        # **4) Enhanced Gravitational Lensing Ring with Distortion**
        lensing_ring = Annulus(
            inner_radius=1.6,
            outer_radius=1.65,
            fill_opacity=0.7,
            color=RED_E
        )
        lensing_ring.set_color_by_radial_gradient(
            inner_color=BLUE_E, outer_color=RED_E
        )
        self.add(lensing_ring)

        # Add distortion effect to simulate light bending
        def lensing_distortion(mob, dt):
            t = self.time
            mob.stretch(1 + 0.05 * np.sin(2 * t), dim=0)  # Horizontal distortion
            mob.stretch(1 - 0.05 * np.sin(2 * t), dim=1)  # Vertical distortion
            mob.rotate(0.02 * dt)  # Subtle shimmering rotation

        lensing_ring.add_updater(lensing_distortion)

        # **5) Advanced Accretion Disk with Orbital Mechanics**
        disk = VGroup()
        disk_particle_count = 150
        for i in range(disk_particle_count):
            angle = np.random.uniform(0, 2 * PI)
            r = np.random.uniform(1.8, 4.0)
            x = r * np.cos(angle)
            y = r * np.sin(angle)

            # Enhanced Doppler shift based on angular position
            color_val = interpolate_color(
                BLUE, RED, (angle % PI) / PI
            )
            particle = Dot(
                point=[x, y, 0],
                radius=0.025,
                color=color_val,
                fill_opacity=0.8
            )
            particle.orbit_radius = r
            particle.orbit_angle = angle
            particle.orbit_speed = 0.5 / np.sqrt(r)  # Keplerian orbital speed
            disk.add(particle)
        self.add(disk)

        # Orbital motion updater for the accretion disk
        def orbital_disk(mob, dt):
            for d in mob:
                d.orbit_angle += d.orbit_speed * dt
                new_x = d.orbit_radius * np.cos(d.orbit_angle)
                new_y = d.orbit_radius * np.sin(d.orbit_angle)
                d.move_to([new_x, new_y, 0])

        disk.add_updater(orbital_disk)

        # **6) Enhanced Swirling Light Streaks with Parametric Curves**
        swirl_streaks = VGroup()
        swirl_count = 25
        for _ in range(swirl_count):
            start_angle = np.random.uniform(0, 2 * PI)
            arc_radius = np.random.uniform(2.5, 4.5)
            arc_length = 0.5
            arc = Arc(
                arc_center=ORIGIN,
                radius=arc_radius,
                start_angle=start_angle,
                angle=arc_length,
                color=WHITE,
                stroke_width=1.5,
            )
            arc.set_opacity(np.random.uniform(0.2, 0.6))
            arc.orbit_speed = np.random.uniform(0.05, 0.15)
            swirl_streaks.add(arc)
        self.add(swirl_streaks)

        # Parametric rotation for swirling streaks
        def swirl_streaks_updater(mob, dt):
            for arc in mob:
                arc.rotate(arc.orbit_speed * dt, about_point=ORIGIN)
                # Add subtle pulsation to opacity
                arc.set_opacity(0.3 + 0.2 * np.sin(3 * self.time))

        swirl_streaks.add_updater(swirl_streaks_updater)

        # **7) Pulsing Glow Ring with Color Shift**
        def glow_updater(mob, dt):
            t = self.time
            mob.set_stroke(width=2 + 1.8 * np.sin(2.5 * t))
            color_val = interpolate_color(GRAY, YELLOW, (1 + np.sin(t * 0.8)) / 2)
            mob.set_stroke(color=color_val)

        glow_ring.add_updater(glow_updater)

        # **8) Camera Motion for Immersive Journey**
        # Simulate a slow zoom toward the black hole
        self.play(
            self.camera.frame.animate.scale(0.7).shift(DOWN * 0.5),
            run_time=10,
            rate_func=linear
        )

        # Let the animations run for a while
        self.wait(10)

        # **9) Fade Out with Smooth Transition**
        self.play(
            FadeOut(VGroup(
                star_field, black_hole_core, glow_ring,
                lensing_ring, disk, swirl_streaks, gradient_rect
            )),
            run_time=3
        )
        self.wait()