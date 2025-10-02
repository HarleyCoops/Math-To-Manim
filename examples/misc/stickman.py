from manim import *

class InscribedShapes(ThreeDScene):
    def construct(self):
        # -- Camera setup with better initial angle --
        self.set_camera_orientation(phi=75 * DEGREES, theta=30 * DEGREES, distance=10)
        
        # Add dramatic lighting
        self.renderer.camera.light_source.move_to(3*IN + 7*OUT + 4*RIGHT)
        
        # Create a title that stays fixed to the camera frame
        title = Text("Nested Geometric Shapes", font_size=48, color=BLUE_A)
        subtitle = Text("From Human to Pyramid", font_size=32, color=BLUE_C)
        title_group = VGroup(title, subtitle).arrange(DOWN).to_corner(UL)
        self.add_fixed_in_frame_mobjects(title_group)
        self.play(Write(title), FadeIn(subtitle, shift=DOWN), run_time=2)
        
        # ------------------------------------------------------------------
        # 1) Create a small "human" figure inside a house
        # ------------------------------------------------------------------
        # For simplicity, treat the "human" as a small cylinder or a simple 2D "stick figure".
        # Let's do a 3D small cylinder to represent a person standing.
        human_height = 0.2
        human = Cylinder(radius=0.05, height=human_height, resolution=16).set_color(YELLOW)
        human.move_to(ORIGIN)  # center at origin
        
        # Animate the human appearing
        self.play(FadeIn(human, scale=1.5), run_time=1)
        
        # Add a tracker for the human's position for later animations
        human_tracker = ValueTracker(0)
        
        # ------------------------------------------------------------------
        # 2) Build a "house" by combining:
        #    - A rectangular prism (walls)
        #    - A triangular prism (roof)
        # ------------------------------------------------------------------
        house_width  = 1.0
        house_depth  = 1.0
        house_height = 0.6
        roof_height  = 0.4

        # Rectangular prism for walls (centered at origin)
        # Prism has dimensions: width x depth x height
        walls = Prism(dimensions=[house_width, house_depth, house_height])
        walls.set_color(RED)
        walls.shift(UP * (house_height / 2))  # so its bottom sits at z=0
        
        # Animate the walls appearing around the human
        self.play(
            Create(walls, run_time=1.5),
            human.animate.shift(UP * (human_height/2)),  # Move human up to stand on floor
        )

        # We'll do it more simply by creating a 3D VGroup of faces:
        roof_faces = VGroup()
        
        # Calculate roof points
        apex_z = house_height + roof_height
        
        # Face 1 (front slope): triangle with points: front-left, front-right, apex front
        front_left  = np.array([ -house_width/2, -house_depth/2, house_height])
        front_right = np.array([  house_width/2, -house_depth/2, house_height])
        apex_front  = np.array([ 0, -house_depth/2, apex_z])
        face_front = Polygon(front_left, front_right, apex_front)
        face_front.set_fill(ORANGE, opacity=0.7).set_stroke(ORANGE, opacity=0.9)

        # Face 2 (back slope): triangle with points: back-left, back-right, apex back
        back_left  = np.array([ -house_width/2, house_depth/2, house_height])
        back_right = np.array([  house_width/2, house_depth/2, house_height])
        apex_back  = np.array([ 0, house_depth/2, apex_z])
        face_back = Polygon(back_left, back_right, apex_back)
        face_back.set_fill(ORANGE, opacity=0.7).set_stroke(ORANGE, opacity=0.9)

        # Face 3 (left roof plane): quad with points: front_left, apex_front, apex_back, back_left
        face_left = Polygon(front_left, apex_front, apex_back, back_left)
        face_left.set_fill(ORANGE, opacity=0.7).set_stroke(ORANGE, opacity=0.9)

        # Face 4 (right roof plane): quad with points: front_right, apex_front, apex_back, back_right
        face_right = Polygon(front_right, apex_front, apex_back, back_right)
        face_right.set_fill(ORANGE, opacity=0.7).set_stroke(ORANGE, opacity=0.9)

        roof_faces.add(face_front, face_back, face_left, face_right)
        
        # Animate the roof appearing
        self.play(Create(roof_faces, run_time=1.5))

        # Combine the house (walls + roof) into one group
        house = VGroup(walls, roof_faces)
        house_and_human = VGroup(house, human)

        # ------------------------------------------------------------------
        # 3) House bounding box to find radius for the inscribing sphere
        # ------------------------------------------------------------------
        house_total_height = house_height + roof_height
        center_shift_z = -(house_total_height / 2)
        
        # Animate centering the house at origin
        self.play(
            house_and_human.animate.shift(UP * center_shift_z),
            run_time=1.5
        )

        # Calculate sphere radius
        hx = house_width / 2
        hy = house_depth / 2
        hz = house_total_height / 2
        R_sphere = np.sqrt(hx**2 + hy**2 + hz**2)

        # Create the sphere with radius = R_sphere
        sphere = Sphere(radius=R_sphere, resolution=(32,32)).set_color(BLUE)
        sphere.set_opacity(0.2)
        sphere.set_stroke(color=BLUE, width=1.5, opacity=0.5)
        
        # Add a label for the sphere
        sphere_label = Text("Sphere", color=BLUE).scale(0.5)
        sphere_label.next_to(sphere, UP+RIGHT)
        self.add_fixed_in_frame_mobjects(sphere_label)
        
        # Animate the sphere appearing
        self.play(
            Create(sphere, run_time=2),
            FadeIn(sphere_label)
        )
        
        # Add a formula for the sphere radius
        radius_formula = MathTex(r"R = \sqrt{(\frac{w}{2})^2 + (\frac{d}{2})^2 + (\frac{h}{2})^2}", font_size=30)
        self.add_fixed_in_frame_mobjects(radius_formula)
        radius_formula.to_corner(UR)
        self.play(Write(radius_formula), run_time=1.5)
        self.wait(1)
        self.play(FadeOut(radius_formula), run_time=1)

        # ------------------------------------------------------------------
        # 4) Sphere inscribed in a cube
        #    => the diameter of the sphere = side of the cube
        # ------------------------------------------------------------------
        side_cube = 2 * R_sphere
        cube = Cube(side_length=side_cube).set_color(GREEN)
        cube.set_opacity(0.15).set_stroke(color=GREEN, width=1.5, opacity=0.6)
        
        # Add a label for the cube
        cube_label = Text("Cube", color=GREEN).scale(0.5)
        cube_label.next_to(cube, DOWN+RIGHT)
        self.add_fixed_in_frame_mobjects(cube_label)
        
        # Animate the cube appearing
        self.play(
            Create(cube, run_time=2),
            FadeIn(cube_label)
        )
        
        # Add a formula for the cube side length
        cube_formula = MathTex(r"s_{cube} = 2R", font_size=30)
        self.add_fixed_in_frame_mobjects(cube_formula)
        cube_formula.to_corner(UR)
        self.play(Write(cube_formula), run_time=1.5)
        self.wait(1)
        self.play(FadeOut(cube_formula), run_time=1)

        # ------------------------------------------------------------------
        # 5) Cube inscribed in a cylinder
        # ------------------------------------------------------------------
        base_radius = side_cube / np.sqrt(2)
        cylinder_height = side_cube
        cylinder = Cylinder(radius=base_radius, height=cylinder_height, resolution=32)
        cylinder.set_color(PURPLE)
        cylinder.set_opacity(0.15)
        cylinder.set_stroke(color=PURPLE, width=1.5, opacity=0.6)
        
        # Add a label for the cylinder
        cylinder_label = Text("Cylinder", color=PURPLE).scale(0.5)
        cylinder_label.next_to(cylinder, LEFT+UP)
        self.add_fixed_in_frame_mobjects(cylinder_label)
        
        # Animate the cylinder appearing
        self.play(
            Create(cylinder, run_time=2),
            FadeIn(cylinder_label)
        )
        
        # Add a formula for the cylinder dimensions
        cylinder_formula = MathTex(r"r_{cyl} = \frac{s_{cube}}{\sqrt{2}}, h_{cyl} = s_{cube}", font_size=30)
        self.add_fixed_in_frame_mobjects(cylinder_formula)
        cylinder_formula.to_corner(UR)
        self.play(Write(cylinder_formula), run_time=1.5)
        self.wait(1)
        self.play(FadeOut(cylinder_formula), run_time=1)

        # ------------------------------------------------------------------
        # 6) Cylinder inscribed in a square pyramid
        # ------------------------------------------------------------------
        pyramid_base_side = 2 * base_radius
        pyramid_height = side_cube  # enough to fully contain the cylinder

        # Build a simple square pyramid as a VGroup of Polygon faces:
        half_side = pyramid_base_side / 2
        base_BL = np.array([-half_side, -half_side, -pyramid_height/2])
        base_BR = np.array([ half_side, -half_side, -pyramid_height/2])
        base_TR = np.array([ half_side,  half_side, -pyramid_height/2])
        base_TL = np.array([-half_side,  half_side, -pyramid_height/2])
        apex = np.array([0, 0, pyramid_height/2])

        base_square = Polygon(base_BL, base_BR, base_TR, base_TL)
        base_square.set_fill(WHITE, opacity=0.1).set_stroke(WHITE, opacity=0.3)

        # Four triangular faces
        face_1 = Polygon(base_BL, base_BR, apex)
        face_2 = Polygon(base_BR, base_TR, apex)
        face_3 = Polygon(base_TR, base_TL, apex)
        face_4 = Polygon(base_TL, base_BL, apex)

        pyramid_faces = VGroup(face_1, face_2, face_3, face_4)
        pyramid_faces.set_fill(WHITE, opacity=0.15).set_stroke(WHITE, opacity=0.4)
        pyramid = VGroup(base_square, pyramid_faces)
        
        # Add a label for the pyramid
        pyramid_label = Text("Pyramid", color=WHITE).scale(0.5)
        pyramid_label.next_to(pyramid, RIGHT+DOWN)
        self.add_fixed_in_frame_mobjects(pyramid_label)
        
        # Animate the pyramid appearing
        self.play(
            Create(pyramid, run_time=2),
            FadeIn(pyramid_label)
        )
        
        # Add a formula for the pyramid dimensions
        pyramid_formula = MathTex(r"s_{base} = 2r_{cyl}, h_{pyr} = h_{cyl}", font_size=30)
        self.add_fixed_in_frame_mobjects(pyramid_formula)
        pyramid_formula.to_corner(UR)
        self.play(Write(pyramid_formula), run_time=1.5)
        self.wait(1)
        self.play(FadeOut(pyramid_formula), run_time=1)

        # ------------------------------------------------------------------
        # Add a summary of the nesting relationship
        # ------------------------------------------------------------------
        nesting_text = Text("Nesting Relationship:", color=YELLOW).scale(0.7)
        nesting_formula = MathTex(r"\text{Human} \subset \text{House} \subset \text{Sphere} \subset \text{Cube} \subset \text{Cylinder} \subset \text{Pyramid}", font_size=28)
        nesting_group = VGroup(nesting_text, nesting_formula).arrange(DOWN).to_edge(DOWN)
        self.add_fixed_in_frame_mobjects(nesting_group)
        self.play(Write(nesting_group), run_time=2)
        
        # ------------------------------------------------------------------
        # Camera movement and highlighting
        # ------------------------------------------------------------------
        # First do a partial rotation to show the 3D structure
        self.begin_ambient_camera_rotation(rate=TAU/16)
        self.wait(4)
        
        # Highlight each shape in sequence
        self.play(
            Flash(human, color=YELLOW, flash_radius=0.3),
            run_time=1
        )
        self.wait(0.5)
        
        self.play(
            house.animate.set_color(RED_A).set_opacity(0.9),
            run_time=1
        )
        self.wait(0.5)
        self.play(
            house.animate.set_color(RED).set_opacity(0.7),
            run_time=1
        )
        
        self.play(
            sphere.animate.set_color(BLUE_A).set_opacity(0.4),
            run_time=1
        )
        self.wait(0.5)
        self.play(
            sphere.animate.set_color(BLUE).set_opacity(0.2),
            run_time=1
        )
        
        self.play(
            cube.animate.set_color(GREEN_A).set_opacity(0.3),
            run_time=1
        )
        self.wait(0.5)
        self.play(
            cube.animate.set_color(GREEN).set_opacity(0.15),
            run_time=1
        )
        
        self.play(
            cylinder.animate.set_color(PURPLE_A).set_opacity(0.3),
            run_time=1
        )
        self.wait(0.5)
        self.play(
            cylinder.animate.set_color(PURPLE).set_opacity(0.15),
            run_time=1
        )
        
        self.play(
            pyramid.animate.set_color(WHITE).set_opacity(0.3),
            run_time=1
        )
        self.wait(0.5)
        self.play(
            pyramid.animate.set_color(WHITE).set_opacity(0.15),
            run_time=1
        )
        
        # Continue rotation for a full view
        self.wait(4)
        self.stop_ambient_camera_rotation()
        
        # Final dramatic camera movement
        self.move_camera(phi=45 * DEGREES, theta=60 * DEGREES, distance=8, run_time=3)
        self.wait(2)
        
        # Fade out all labels for a clean final view
        self.play(
            FadeOut(sphere_label),
            FadeOut(cube_label),
            FadeOut(cylinder_label),
            FadeOut(pyramid_label),
            FadeOut(nesting_group),
            run_time=1.5
        )
        
        # Final rotation to appreciate the full structure
        self.begin_ambient_camera_rotation(rate=TAU/12)
        self.wait(6)
        self.stop_ambient_camera_rotation()
        
        # Fade to black
        self.play(
            FadeOut(title_group),
            FadeOut(house_and_human),
            FadeOut(sphere),
            FadeOut(cube),
            FadeOut(cylinder),
            FadeOut(pyramid),
            run_time=2
        )
        self.wait(1)
