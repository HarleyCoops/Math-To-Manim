from manim import *
import numpy as np

# --- AESTHETIC CONFIG ---
C_BG = "#FAF9F6"  # Off-white
C_FG_1 = "#FF0055" # Vibrant Red/Pink
C_FG_2 = "#00CCAA" # Vibrant Teal
C_FG_3 = "#FFCC00" # Vibrant Yellow
C_FG_4 = "#6600FF" # Vibrant Purple
C_TEXT = "#333333" # Dark Grey for text

config.background_color = C_BG

class Machinarium(ThreeDScene):
    def construct(self):
        # Setup Camera
        self.set_camera_orientation(phi=60 * DEGREES, theta=-45 * DEGREES)
        self.begin_ambient_camera_rotation(rate=0.1)

        # 1. The Puzzle in 3D
        self.next_section("Puzzle Setup")
        self.scene_puzzle_3d()

        # 2. Transitivity (Graph)
        self.next_section("Transitivity")
        self.scene_transitivity_3d()

        # 3. Primitivity (Shattering Blocks)
        self.next_section("Primitivity")
        self.scene_primitivity_3d()

        # 4. Commutators (3D Arrows)
        self.next_section("Commutators")
        self.scene_commutators_3d()

        # 5. Jordan's Theorem (3D Bridge)
        self.next_section("Jordan Theorem")
        self.scene_jordan_3d()

        self.wait(2)

    def scene_puzzle_3d(self):
        # Create 3 Rings
        radius = 2.0
        
        # Positions for the 3 circles (Triangle formation)
        # Center: Origin
        # A: Left, B: Right, C: Top
        # Overlap logic is complex, let's just place them nicely in 3D
        
        c1_pos = LEFT * 1.5 + DOWN * 1
        c2_pos = RIGHT * 1.5 + DOWN * 1
        c3_pos = UP * 1.5
        
        ring1 = Torus(major_radius=radius, minor_radius=0.1, color=C_FG_1).move_to(c1_pos)
        ring2 = Torus(major_radius=radius, minor_radius=0.1, color=C_FG_2).move_to(c2_pos)
        ring3 = Torus(major_radius=radius, minor_radius=0.1, color=C_FG_3).move_to(c3_pos)
        
        rings = VGroup(ring1, ring2, ring3)
        
        # Add spheres for positions (6 per ring, simplified intersection)
        # Just placing 12 spheres in a circle layout for the group S12
        
        spheres = VGroup()
        for i in range(12):
            angle = i * 30 * DEGREES
            pos = np.array([3.5 * np.cos(angle), 3.5 * np.sin(angle), 0])
            s = Sphere(radius=0.2, resolution=(15, 15)).move_to(pos)
            # Color gradient
            s.set_color(interpolate_color(ManimColor(C_FG_1), ManimColor(C_FG_4), i/11))
            spheres.add(s)
            
        # Labels
        labels = VGroup()
        for i, s in enumerate(spheres):
            l = Text(str(i+1), font_size=24, color=C_TEXT).next_to(s, OUT)
            # Rotate label to face camera roughly
            l.rotate(90*DEGREES, axis=RIGHT) 
            labels.add(l)

        self.play(Create(rings), run_time=2)
        self.play(FadeIn(spheres), Write(labels))
        
        # Rotate the whole group
        self.play(Rotate(spheres, angle=PI/2, axis=OUT), Rotate(labels, angle=PI/2, axis=OUT, about_point=ORIGIN), run_time=2)
        
        # Swap animation (1 and 2)
        s1 = spheres[0]
        s2 = spheres[1]
        
        arc = ArcBetweenPoints(s1.get_center(), s2.get_center(), angle=PI/2, color=C_TEXT)
        self.play(MoveAlongPath(s1, arc), MoveAlongPath(s2, arc.copy().reverse_direction()), run_time=1)
        
        self.wait(1)
        self.play(FadeOut(rings), FadeOut(spheres), FadeOut(labels))

    def scene_transitivity_3d(self):
        # 3D Graph
        nodes = [Sphere(radius=0.15, color=C_TEXT).move_to(np.array([
            3 * np.cos(i*30*DEGREES), 
            3 * np.sin(i*30*DEGREES), 
            np.sin(i*60*DEGREES) # Wavy z-axis
        ])) for i in range(12)]
        
        node_group = VGroup(*nodes)
        
        edges = VGroup()
        for i in range(12):
            e = Line3D(nodes[i].get_center(), nodes[(i+1)%12].get_center(), color=C_FG_2)
            edges.add(e)
            
        self.play(Create(node_group), Create(edges))
        
        # Flood fill effect
        self.play(nodes[0].animate.set_color(C_FG_1))
        self.play(LaggedStart(*[n.animate.set_color(C_FG_1) for n in nodes[1:]], lag_ratio=0.1))
        
        check = Text("Transitive", color=C_TEXT).rotate(90*DEGREES, axis=RIGHT).move_to(OUT*2)
        self.play(Write(check))
        self.wait(1)
        self.play(FadeOut(node_group), FadeOut(edges), FadeOut(check))

    def scene_primitivity_3d(self):
        # Blocks as Cubes
        cubes = VGroup()
        for i in range(4):
            # Block of 3
            block = VGroup()
            for j in range(3):
                c = Cube(side_length=0.8, fill_opacity=0.8, fill_color=C_FG_4)
                c.move_to(RIGHT * (i*3 + j - 6) + UP * np.sin(i))
                block.add(c)
            cubes.add(block)
            
        self.play(DrawBorderThenFill(cubes))
        
        # Shatter one block
        target_block = cubes[1]
        self.play(target_block.animate.arrange_in_grid(rows=3, cols=1, buff=0.5).shift(UP*2))
        
        # Explode
        self.play(
            *[c.animate.shift(np.random.random(3)*2 - 1).rotate(np.random.random()*PI) for c in target_block],
            run_time=1
        )
        
        lbl = Text("Primitive", color=C_TEXT).rotate(90*DEGREES, axis=RIGHT).move_to(DOWN*2)
        self.play(Write(lbl))
        self.wait(1)
        self.play(FadeOut(cubes), FadeOut(lbl))

    def scene_commutators_3d(self):
        # Commutator [g, h]
        # Visualized as vectors in 3D
        
        origin = ORIGIN
        v1 = Arrow3D(origin, UP*2 + RIGHT, color=C_FG_1)
        v2 = Arrow3D(origin, UP*2 + LEFT, color=C_FG_2)
        
        self.play(Create(v1), Create(v2))
        
        # Commutator result
        v_res = Arrow3D(origin, OUT*2, color=C_FG_3)
        self.play(Transform(v1, v_res), FadeOut(v2))
        
        lbl = Text("3-Cycle", color=C_FG_3).rotate(90*DEGREES, axis=RIGHT).next_to(v_res, OUT)
        self.play(Write(lbl))
        self.wait(1)
        self.play(FadeOut(v1), FadeOut(lbl))

    def scene_jordan_3d(self):
        # Jordan's Theorem as a Monolith
        
        monolith = Prism(dimensions=[2, 4, 1], fill_color=C_FG_2, fill_opacity=0.9)
        monolith.rotate(45*DEGREES, axis=UP)
        
        text_j = Text("Jordan", color=WHITE).rotate(90*DEGREES, axis=RIGHT).rotate(45*DEGREES, axis=UP).move_to(monolith.get_center() + OUT*0.6)
        
        self.play(Create(monolith))
        self.play(Write(text_j))
        
        # Final result S12
        final_text = Text("G = S12", font_size=72, color=C_FG_1).rotate(90*DEGREES, axis=RIGHT).move_to(UP*3)
        self.play(Transform(monolith, final_text), FadeOut(text_j))
        
        # Celebration particles
        particles = VGroup(*[
            Dot3D(color=np.random.choice([C_FG_1, C_FG_2, C_FG_3, C_FG_4]))
            .move_to(np.random.random(3)*6 - 3)
            for _ in range(50)
        ])
        
        self.play(Create(particles), run_time=2)
        self.play(
            *[p.animate.shift(np.random.random(3)*2 - 1) for p in particles],
            run_time=2
        )
        
        self.wait(2)
