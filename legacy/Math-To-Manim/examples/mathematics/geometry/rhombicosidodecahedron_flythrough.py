from manim import *

class CameraJourneyRhombicosidodecahedron(ThreeDScene):
    def construct(self):
        # [Keep all previous vertex/face/polyhedron setup code identical...]
        
        # Remove the automatic rotation updater
        polyhedron.clear_updaters()
        
        # Configure initial camera position INSIDE the polyhedron
        self.set_camera_orientation(
            phi=70 * DEGREES,
            theta=-45 * DEGREES,
            distance=2,  # Start closer
            frame_center=ORIGIN
        )
        
        # Camera path parameters
        start_pos = 4*OUT + 2*UP
        through_pos = ORIGIN
        end_pos = 4*IN + 2*DOWN
        final_pos = 4*OUT + 2*UP  # Return to start view
        
        # Animate camera movement
        camera_path = [
            (0, 3),    # Approach and enter (first 3 seconds)
            (3, 18),   # Travel through and emerge (next 15 seconds)
            (18, 21)   # Pull back to start position (last 3 seconds)
        ]
        
        # Camera motion updater
        def update_camera(mob, dt):
            t = self.time
            if t < 3:  # Entry phase
                self.camera.frame.move_to(
                    interpolate(start_pos, through_pos, t/3)
                )
                self.camera.frame.look_at(ORIGIN)
            elif t < 18:  # Travel through
                progress = (t-3)/15
                self.camera.frame.move_to(
                    interpolate(through_pos, end_pos, progress)
                )
                self.camera.frame.look_at(ORIGIN)
            else:  # Return phase
                progress = (t-18)/3
                self.camera.frame.move_to(
                    interpolate(end_pos, final_pos, progress)
                )
                self.camera.frame.look_at(ORIGIN.lerp(final_pos, progress))
                
            # Update edge opacity based on camera distance
            for edge_group in [pentagons, squares, triangles]:
                for line in edge_group:
                    dist = np.linalg.norm(
                        line.get_center() - self.camera.frame.get_center()
                    )
                    opacity = np.clip(1.5 - dist/6, 0.2, 0.9)
                    line.set_stroke(opacity=opacity)
        
        self.camera.frame.add_updater(update_camera)
        
        # Animation sequence
        self.play(FadeIn(polyhedron), run_time=3)
        self.wait(15)
        self.play(FadeOut(polyhedron), run_time=3)