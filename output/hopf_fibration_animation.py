from manim import *
import numpy as np


class HopfFibrationAnimation(ThreeDScene):
    """
    Hopf Fibration: Stereographic projection of S³ fibers into R³.
    Creates nested toroidal structures where every fiber (Villarceau circle)
    interlocks with every other fiber exactly once.
    """

    # Color palette mapped to latitude (eta)
    FIBER_COLORS = [
        "#4B0082",  # Deep Indigo (innermost)
        "#00CED1",  # Cyan
        "#2E8B57",  # Emerald Green
        "#FF8C00",  # Solar Orange
        "#FF00FF",  # Magenta (outermost)
    ]

    # Eta values for the 5 toroidal layers
    ETA_VALUES = [0.2, 0.5, 0.8, 1.1, 1.4]

    # Number of fibers per layer
    FIBERS_PER_LAYER = 16

    def construct(self):
        # Camera setup
        self.set_camera_orientation(phi=75 * DEGREES, theta=30 * DEGREES)

        # Phase 1: Create the central Z-axis
        self.intro_z_axis()

        # Phase 2: Bloom - expand layers one by one
        self.bloom_layers()

        # Phase 3: Continuous flow animation with camera rotation
        self.flow_animation()

    def hopf_fiber(self, t, eta, phi):
        """
        Parametric equation for a single Hopf fiber.

        Parameters:
            t: Parameter along the fiber (0 to 2*pi)
            eta: Controls radius of torus (0 < eta < pi/2)
            phi: Rotation offset (0 to 2*pi)

        Returns:
            np.array([x, y, z]) - 3D coordinates
        """
        cos_eta = np.cos(eta)
        sin_eta = np.sin(eta)
        cos_t = np.cos(t)
        sin_t = np.sin(t)

        denominator = 1 - cos_eta * sin_t

        # Avoid division by zero
        if np.abs(denominator) < 1e-6:
            denominator = 1e-6

        x = sin_eta * np.cos(t + phi) / denominator
        y = sin_eta * np.sin(t + phi) / denominator
        z = cos_eta * cos_t / denominator

        return np.array([x, y, z])

    def create_fiber_curve(self, eta, phi, color, stroke_width=1.5, stroke_opacity=0.6):
        """Create a single fiber as a ParametricFunction."""
        curve = ParametricFunction(
            lambda t: self.hopf_fiber(t, eta, phi),
            t_range=[0, 2 * PI, 0.05],
            color=color,
            stroke_width=stroke_width,
            stroke_opacity=stroke_opacity,
        )
        return curve

    def create_layer(self, layer_index):
        """Create all fibers for a single toroidal layer."""
        eta = self.ETA_VALUES[layer_index]
        color = self.FIBER_COLORS[layer_index]
        fibers = VGroup()

        for i in range(self.FIBERS_PER_LAYER):
            phi = (2 * PI * i) / self.FIBERS_PER_LAYER
            fiber = self.create_fiber_curve(eta, phi, color)
            fibers.add(fiber)

        return fibers

    def intro_z_axis(self):
        """Phase 1: Start with the central Z-axis line."""
        # Create central axis (represents the fiber at the "North Pole")
        z_axis = Line3D(
            start=np.array([0, 0, -4]),
            end=np.array([0, 0, 4]),
            color=WHITE,
            thickness=0.03,
        )

        # Title
        title = Text("Hopf Fibration", font_size=48).to_edge(UP)
        subtitle = Text(
            "Stereographic Projection of S³ into R³",
            font_size=24
        ).next_to(title, DOWN)

        self.add_fixed_in_frame_mobjects(title, subtitle)

        self.play(
            Create(z_axis),
            FadeIn(title),
            FadeIn(subtitle),
            run_time=2
        )
        self.wait(1)

        self.play(FadeOut(title), FadeOut(subtitle), run_time=1)

        self.z_axis = z_axis

    def bloom_layers(self):
        """Phase 2: Expand toroidal layers one by one (blooming effect)."""
        self.all_layers = VGroup()

        for layer_idx in range(5):
            layer = self.create_layer(layer_idx)
            self.all_layers.add(layer)

            # Animate each layer appearing with a spiral/bloom effect
            self.play(
                LaggedStart(
                    *[Create(fiber) for fiber in layer],
                    lag_ratio=0.05
                ),
                run_time=2
            )
            self.wait(0.5)

        self.wait(1)

    def flow_animation(self):
        """Phase 3: Continuous flow with camera rotation."""
        # Create a ValueTracker for the flow animation
        flow_tracker = ValueTracker(0)

        # Store original fibers and create flowing versions
        def update_all_fibers(mob, dt):
            """Update all fibers to create flowing effect."""
            flow_tracker.increment_value(dt * 0.5)
            offset = flow_tracker.get_value()

            for layer_idx, layer in enumerate(self.all_layers):
                eta = self.ETA_VALUES[layer_idx]
                color = self.FIBER_COLORS[layer_idx]

                for fiber_idx, fiber in enumerate(layer):
                    base_phi = (2 * PI * fiber_idx) / self.FIBERS_PER_LAYER
                    new_phi = base_phi + offset

                    # Recreate fiber with new phi
                    new_points = [
                        self.hopf_fiber(t, eta, new_phi)
                        for t in np.linspace(0, 2 * PI, 100)
                    ]
                    fiber.set_points_smoothly(new_points)

        # Add updater for flowing effect
        self.all_layers.add_updater(update_all_fibers)

        # Begin ambient camera rotation
        self.begin_ambient_camera_rotation(rate=0.15)

        # Let it flow for a while
        self.wait(8)

        # Slow zoom out to show full structure
        self.move_camera(zoom=0.7, run_time=3)

        self.wait(4)

        # Remove updater and stop camera
        self.all_layers.remove_updater(update_all_fibers)
        self.stop_ambient_camera_rotation()

        # Final hold
        self.wait(2)

        # Fade out
        self.play(
            FadeOut(self.all_layers),
            FadeOut(self.z_axis),
            run_time=2
        )


class HopfFibrationStatic(ThreeDScene):
    """
    Static version for quick preview - no animation, just the structure.
    Useful for testing the geometry before running the full animation.
    """

    FIBER_COLORS = [
        "#4B0082",  # Deep Indigo
        "#00CED1",  # Cyan
        "#2E8B57",  # Emerald Green
        "#FF8C00",  # Solar Orange
        "#FF00FF",  # Magenta
    ]

    ETA_VALUES = [0.2, 0.5, 0.8, 1.1, 1.4]
    FIBERS_PER_LAYER = 12

    def construct(self):
        self.set_camera_orientation(phi=75 * DEGREES, theta=45 * DEGREES)

        # Create all layers at once
        all_fibers = VGroup()

        for layer_idx, eta in enumerate(self.ETA_VALUES):
            color = self.FIBER_COLORS[layer_idx]

            for i in range(self.FIBERS_PER_LAYER):
                phi = (2 * PI * i) / self.FIBERS_PER_LAYER
                fiber = self.create_fiber(eta, phi, color)
                all_fibers.add(fiber)

        # Add Z-axis
        z_axis = Line3D(
            start=np.array([0, 0, -4]),
            end=np.array([0, 0, 4]),
            color=WHITE,
            thickness=0.02,
        )

        self.add(z_axis, all_fibers)
        self.begin_ambient_camera_rotation(rate=0.2)
        self.wait(10)

    def create_fiber(self, eta, phi, color):
        """Create a single Hopf fiber."""
        def hopf_point(t):
            cos_eta = np.cos(eta)
            sin_eta = np.sin(eta)
            denom = 1 - cos_eta * np.sin(t)
            if np.abs(denom) < 1e-6:
                denom = 1e-6

            x = sin_eta * np.cos(t + phi) / denom
            y = sin_eta * np.sin(t + phi) / denom
            z = cos_eta * np.cos(t) / denom
            return np.array([x, y, z])

        return ParametricFunction(
            hopf_point,
            t_range=[0, 2 * PI, 0.05],
            color=color,
            stroke_width=1.5,
            stroke_opacity=0.6,
        )
