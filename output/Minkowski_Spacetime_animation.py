from manim import *

class JourneyThroughSpacetime(Scene):
    def construct(self):
        # Newtonian mechanics
        newtonian_mechanics = Text("Newtonian Mechanics", color=BLUE).to_edge(UP)
        self.play(Write(newtonian_mechanics))
        self.wait(2)

        # Transition to 2D representation
        arrow_2d = Arrow(LEFT, RIGHT).next_to(newtonian_mechanics, DOWN)
        self.play(Write(arrow_2d))
        self.wait(1)

        # Transition to 3D space
        arrow_3d = Arrow(LEFT, RIGHT).next_to(arrow_2d, DOWN)
        self.play(Transform(arrow_2d, arrow_3d))
        self.wait(1)

        # Vectors, calculus, multivariable calculus
        vectors_calculus = VGroup(
            Text("Vectors", color=RED),
            Text("Calculus", color=GREEN),
            Text("Multivariable Calculus", color=YELLOW)
        ).arrange(DOWN, aligned_edge=LEFT).next_to(arrow_3d, DOWN)
        self.play(Write(vectors_calculus))
        self.wait(2)

        # Partial derivatives and vector calculus
        partial_derivatives = Text("Partial Derivatives", color=PURPLE).next_to(vectors_calculus, DOWN)
        vector_calculus = Text("Vector Calculus", color=ORANGE).next_to(partial_derivatives, DOWN)
        self.play(Write(partial_derivatives), Write(vector_calculus))
        self.wait(2)

        # Electrostatics, magnetic fields, magnetostatics
        electrostatics = Text("Electrostatics", color=RED).next_to(partial_derivatives, DOWN)
        magnetic_fields = Text("Magnetic Fields", color=GREEN).next_to(electrostatics, DOWN)
        magnetostatics = Text("MagnetoStatics", color=BLUE).next_to(magnetic_fields, DOWN)
        self.play(Write(electrostatics), Write(magnetic_fields), Write(magnetostatics))
        self.wait(2)

        # Induced electromotive force and Faraday's law of induction
        induced_emf = Text("Induced Electromotive Force", color=PURPLE).next_to(magnetostatics, DOWN)
        faraday_law = Text("Faraday's Law of Induction", color=ORANGE).next_to(induced_emf, DOWN)
        self.play(Write(induced_emf), Write(faraday_law))
        self.wait(2)

        # Maxwell's equations and speed of light
        maxwell_equations = Text("Maxwell's Equations", color=RED).next_to(faraday_law, DOWN)
        speed_of_light = Text("Speed of Light", color=GREEN).next_to(maxwell_equations, DOWN)
        self.play(Write(maxwell_equations), Write(speed_of_light))
        self.wait(2)

        # Special Relativity
        special_relativity = Text("Special Relativity", color=BLUE).next_to(speed_of_light, DOWN)
        self.play(Write(special_relativity))
        self.wait(2)

        # Classical mechanics and electromagnetism
        classical_mechanics = Text("Classical Mechanics", color=PURPLE).next_to(special_relativity, DOWN)
        electromagnetism = Text("Electromagnetism", color=ORANGE).next_to(classical_mechanics, DOWN)
        self.play(Write(classical_mechanics), Write(electromagnetism))
        self.wait(2)

        # Vector spaces, linear algebra, matrix multiplication
        vector_spaces = Text("Vector Spaces", color=RED).next_to(electromagnetism, DOWN)
        linear_algebra = Text("Linear Algebra", color=GREEN).next_to(vector_spaces, DOWN)
        matrix_multiplication = Text("Matrix Multiplication", color=BLUE).next_to(linear_algebra, DOWN)
        self.play(Write(vector_spaces), Write(linear_algebra), Write(matrix_multiplication))
        self.wait(2)

        # Multi-dimensional arrays and tensors
        multi_dimensional_arrays = Text("Multi-Dimensional Arrays", color=PURPLE).next_to(matrix_multiplication, DOWN)
        tensors = Text("Tensors", color=ORANGE).next_to(multi_dimensional_arrays, DOWN)
        self.play(Write(multi_dimensional_arrays), Write(tensors))
        self.wait(2)

        # Minkowski Spacetime
        minkowski_spacetime = Text("Minkowski Spacetime", color=RED).to_edge(DOWN)
        self.play(Write(minkowski_spacetime))
        self.wait(3)

        # Final summary
        final_summary = Text("Final Summary", color=GREEN).to_edge(DOWN)
        self.play(Transform(minkowski_spacetime, final_summary))
        self.wait(2)