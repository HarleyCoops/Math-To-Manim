from manim import *
import numpy as np
from math import sqrt

class ArtisticRhombicosidodecahedron(ThreeDScene):
    def construct(self):
        # Configuration
        self.camera.background_color = BLACK
        
        # Constants from McCooey's data
        C0 = (1 + sqrt(5)) / 4
        C1 = (3 + sqrt(5)) / 4
        C2 = (1 + sqrt(5)) / 2
        C3 = (5 + sqrt(5)) / 4
        C4 = (2 + sqrt(5)) / 2

        # Vertex data (same as original)
        vertices = [
            np.array([ 0.5,  0.5,   C4]),  # V0
            np.array([ 0.5,  0.5,  -C4]),  # V1
            np.array([ 0.5, -0.5,   C4]),  # V2
            np.array([ 0.5, -0.5,  -C4]),  # V3
            np.array([-0.5,  0.5,   C4]),  # V4
            np.array([-0.5,  0.5,  -C4]),  # V5
            np.array([-0.5, -0.5,   C4]),  # V6
            np.array([-0.5, -0.5,  -C4]),  # V7
            np.array([  C4,  0.5,  0.5]),  # V8
            np.array([  C4,  0.5, -0.5]),  # V9
            np.array([  C4, -0.5,  0.5]),  # V10
            np.array([  C4, -0.5, -0.5]),  # V11
            np.array([ -C4,  0.5,  0.5]),  # V12
            np.array([ -C4,  0.5, -0.5]),  # V13
            np.array([ -C4, -0.5,  0.5]),  # V14
            np.array([ -C4, -0.5, -0.5]),  # V15
            np.array([ 0.5,   C4,  0.5]),  # V16
            np.array([ 0.5,   C4, -0.5]),  # V17
            np.array([ 0.5,  -C4,  0.5]),  # V18
            np.array([ 0.5,  -C4, -0.5]),  # V19
            np.array([-0.5,   C4,  0.5]),  # V20
            np.array([-0.5,   C4, -0.5]),  # V21
            np.array([-0.5,  -C4,  0.5]),  # V22
            np.array([-0.5,  -C4, -0.5]),  # V23
            np.array([ 0.0,   C1,   C3]),  # V24
            np.array([ 0.0,   C1,  -C3]),  # V25
            np.array([ 0.0,  -C1,   C3]),  # V26
            np.array([ 0.0,  -C1,  -C3]),  # V27
            np.array([  C3,  0.0,   C1]),  # V28
            np.array([  C3,  0.0,  -C1]),  # V29
            np.array([ -C3,  0.0,   C1]),  # V30
            np.array([ -C3,  0.0,  -C1]),  # V31
            np.array([  C1,   C3,  0.0]),  # V32
            np.array([  C1,  -C3,  0.0]),  # V33
            np.array([ -C1,   C3,  0.0]),  # V34
            np.array([ -C1,  -C3,  0.0]),  # V35
            np.array([  C1,   C0,   C2]),  # V36
            np.array([  C1,   C0,  -C2]),  # V37
            np.array([  C1,  -C0,   C2]),  # V38
            np.array([  C1,  -C0,  -C2]),  # V39
            np.array([ -C1,   C0,   C2]),  # V40
            np.array([ -C1,   C0,  -C2]),  # V41
            np.array([ -C1,  -C0,   C2]),  # V42
            np.array([ -C1,  -C0,  -C2]),  # V43
            np.array([  C2,   C1,   C0]),  # V44
            np.array([  C2,   C1,  -C0]),  # V45
            np.array([  C2,  -C1,   C0]),  # V46
            np.array([  C2,  -C1,  -C0]),  # V47
            np.array([ -C2,   C1,   C0]),  # V48
            np.array([ -C2,   C1,  -C0]),  # V49
            np.array([ -C2,  -C1,   C0]),  # V50
            np.array([ -C2,  -C1,  -C0]),  # V51
            np.array([  C0,   C2,   C1]),  # V52
            np.array([  C0,   C2,  -C1]),  # V53
            np.array([  C0,  -C2,   C1]),  # V54
            np.array([  C0,  -C2,  -C1]),  # V55
            np.array([ -C0,   C2,   C1]),  # V56
            np.array([ -C0,   C2,  -C1]),  # V57
            np.array([ -C0,  -C2,   C1]),  # V58
            np.array([ -C0,  -C2,  -C1]),  # V59
        ]

        # Face data (same structure as original)
        faces = [
            # Pentagons (first 12 faces)
            [24, 52, 16, 20, 56],
            [25, 57, 21, 17, 53],
            [26, 58, 22, 18, 54],
            [27, 55, 19, 23, 59],
            [28, 36,  0,  2, 38],
            [29, 39,  3,  1, 37],
            [30, 42,  6,  4, 40],
            [31, 41,  5,  7, 43],
            [32, 44,  8,  9, 45],
            [33, 47, 11, 10, 46],
            [34, 49, 13, 12, 48],
            [35, 50, 14, 15, 51],
            # Squares (next 30 faces)
            [ 0, 36, 52, 24],
            [ 1, 25, 53, 37],
            [ 2, 26, 54, 38],
            [ 3, 39, 55, 27],
            [ 4, 24, 56, 40],
            [ 5, 41, 57, 25],
            [ 6, 42, 58, 26],
            [ 7, 27, 59, 43],
            [ 8, 44, 36, 28],
            [ 9, 29, 37, 45],
            [10, 28, 38, 46],
            [11, 47, 39, 29],
            [12, 30, 40, 48],
            [13, 49, 41, 31],
            [14, 50, 42, 30],
            [15, 31, 43, 51],
            [16, 52, 44, 32],
            [17, 32, 45, 53],
            [18, 33, 46, 54],
            [19, 55, 47, 33],
            [20, 34, 48, 56],
            [21, 57, 49, 34],
            [22, 58, 50, 35],
            [23, 35, 51, 59],
            [ 0,  4,  6,  2],
            [ 1,  3,  7,  5],
            [ 8, 10, 11,  9],
            [12, 13, 15, 14],
            [16, 17, 21, 20],
            [18, 22, 23, 19],
            # Triangles (last 20 faces)
            [24,  4,  0],
            [25,  1,  5],
            [26,  2,  6],
            [27,  7,  3],
            [28, 10,  8],
            [29,  9, 11],
            [30, 12, 14],
            [31, 15, 13],
            [32, 17, 16],
            [33, 18, 19],
            [34, 20, 21],
            [35, 23, 22],
            [36, 44, 52],
            [37, 53, 45],
            [38, 54, 46],
            [39, 47, 55],
            [40, 56, 48],
            [41, 49, 57],
            [42, 50, 58],
            [43, 59, 51]
        ]

        # Create edge groups with different styles
        pentagon_edges = set()
        square_edges = set()
        triangle_edges = set()
        all_edges = set()

        # Process faces by type
        for i, face in enumerate(faces):
            n = len(face)
            face_type = "pentagon" if i < 12 else "square" if i < 42 else "triangle"
            
            for j in range(n):
                v1, v2 = sorted([face[j], face[(j+1)%n]])
                edge = (v1, v2)
                
                if edge not in all_edges:
                    all_edges.add(edge)
                    if face_type == "pentagon":
                        pentagon_edges.add(edge)
                    elif face_type == "square":
                        square_edges.add(edge)
                    else:
                        triangle_edges.add(edge)

        # Create edge meshes with different styles
        def create_edges(edges, color, stroke_width):
            group = VGroup()
            for (v1, v2) in edges:
                line = Line3D(
                    start=vertices[v1],
                    end=vertices[v2],
                    color=color,
                    stroke_width=stroke_width,
                    stroke_opacity=0.9
                )
                group.add(line)
            return group

        pentagons = create_edges(pentagon_edges, GOLD_E, 2.5)
        squares = create_edges(square_edges, BLUE_E, 2.0)
        triangles = create_edges(triangle_edges, RED_E, 1.5)

        # Create glowing vertices
        vertex_group = VGroup()
        for v in vertices:
            core = Sphere(radius=0.06, color=WHITE, resolution=(10, 10)).move_to(v)
            halo = Sphere(
                radius=0.15, 
                color=WHITE,
                resolution=(10, 10)
            ).set_opacity(0.15).move_to(v)
            vertex_group.add(halo, core)

        # Build final object
        polyhedron = VGroup(pentagons, squares, triangles, vertex_group)
        polyhedron.scale(2).move_to(ORIGIN)

        # Camera setup
        self.set_camera_orientation(
            phi=60 * DEGREES,
            theta=-45 * DEGREES,
            distance=8,
            frame_center=ORIGIN
        )
        self.camera.set_zoom(1.5)

        # Animated rotation with multiple axes
        polyhedron.add_updater(lambda m, dt: m.rotate(
            0.6 * dt, 
            axis=normalize(np.sin(self.time*0.5)*UP + np.cos(self.time*0.3)*RIGHT + OUT)
        ))

        # Background gradient
        bg = FullScreenRectangle()
        bg.set_color([BLACK, "#002233", "#001122"])
        bg.set_opacity(1)
        self.add(bg, polyhedron)

        # Animation sequence
        self.play(Write(polyhedron), run_time=3)
        self.wait(15)
        self.play(FadeOut(polyhedron), run_time=3)

def normalize(v):
    return v / np.linalg.norm(v)
