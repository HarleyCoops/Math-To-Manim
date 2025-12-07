from manim import *
import numpy as np

# Aesthethic Configuration
config.background_color = "#F5F5F0"  # Off-white gallery look

class HopfFibrationEpic(ThreeDScene):
    def construct(self):
        # 1. Set up Camera and Lighting Feel
        self.set_camera_orientation(phi=75 * DEGREES, theta=45 * DEGREES, zoom=0.6)
        self.begin_ambient_camera_rotation(rate=0.1)

        # 2. The Reflection Plane (Simulating the floor)
        floor_level = -3
        
        # 3. Mathematical Helper: Stereographic Projection of S3 fibers
        def get_fiber_points(eta, n_points=100):
            # Generates points for a fiber (circle in 4D) projected to 3D
            # eta: varies from 0 to pi/2 to select the torus 'shell'
            # phi: varies 0 to 2pi to trace the circle fiber
            # xi_2: varies 0 to 2pi (base circle rotation)
            points = []
            # We lock one angle for the specific fiber, sweep the other
            xi1_range = np.linspace(0, TAU, n_points)
            xi2_fixed = 0 # This defines 'which' fiber on the torus we draw
            
            # To create a bundle, we iterate fibers
            path_points = []
            for phi in xi1_range:
                # Coordinates on S3
                p0 = np.cos(eta) * np.exp(1j * phi)
                p1 = np.sin(eta) * np.exp(1j * (phi + xi2_fixed * 2.0))
                
                # Split into R4 coordinates (x1, y1, x2, y2)
                x1, y1 = p0.real, p0.imag
                x2, y2 = p1.real, p1.imag
                
                # Stereographic projection S3 -> R3
                # Project from (0,0,0,1) to w=0 hyperplane
                denom = 1 - y2
                if abs(denom) < 0.001: denom = 0.001
                
                SX = x1 / denom
                SY = y1 / denom
                SZ = x2 / denom
                
                path_points.append([SX, SY, SZ])
            return np.array(path_points)

        # 4. Generate the Bundle
        fibers = VGroup()
        reflections = VGroup()
        
        # Colors representing the gradient map
        colors = [TEAL_E, BLUE, PURPLE, MAROON_E, GOLD_E]
        
        self.stop_ambient_camera_rotation()
        
        # Create nested tori fibers
        for i, eta in enumerate(np.linspace(0.2, 1.4, 5)):
            c = colors[i % len(colors)]
            # Create a ring of fibers for this torus shell
            for tilt in np.linspace(0, TAU, 8, endpoint=False):
                # We rotate the path points to populate the torus surface
                raw_points = get_fiber_points(eta)
                
                # Manual rotation hack to distribute fibers on the torus
                # (Simplification for visual impact over pure strict math fidelity)
                rot_matrix = rotation_matrix(tilt, OUT)
                rotated_points = np.dot(raw_points, rot_matrix[:3,:3].T)
                
                # Create the Fiber Object
                fiber = VMobject()
                fiber.set_points_smoothly(rotated_points)
                fiber.set_stroke(c, width=3, opacity=0.9)
                
                # Create the Reflection (Ghost Object)
                reflection = fiber.copy()
                # Flip across Z and shift down twice the distance to floor
                reflection.apply_function(lambda p: np.array([p[0], p[1], -p[2] + 2*floor_level]))
                reflection.set_stroke(color=GRAY, width=1, opacity=0.1)
                reflection.set_shade_in_3d(False)

                fibers.add(fiber)
                reflections.add(reflection)

        # 5. Animation Sequence
        title = Text("The Hopf Fibration", font_size=64).to_edge(UP).set_color(BLACK)
        self.add_fixed_in_frame_mobjects(title)
        self.play(Write(title))
        
        # Spin in fibers
        self.move_camera(phi=60 * DEGREES, theta=-45 * DEGREES, run_time=2)
        self.play(
            Create(fibers, lag_ratio=0.01, run_time=4),
            FadeIn(reflections, run_time=4)
        )
        
        # Continuous rotation phase
        self.begin_ambient_camera_rotation(rate=0.15)
        self.wait(6)

