from manim import *
import numpy as np

class RadiumAtomStructure(Scene):
    def construct(self):
        # Constants and parameters
        SCALE_FACTOR = 0.8  # Scale everything to fit the screen
        NUCLEUS_RADIUS = 0.05
        LAMBDA = 0.7  # Scaling factor for inner orbits
        
        # Setup title and introduction
        self.introduce_topic()
        
        # Create atom components
        nucleus = self.create_nucleus()
        self.play(Create(nucleus))
        
        # Add the primary orbits (red)
        red_orbits = self.create_orbit_family(
            a=5.2, 
            b=3.6, 
            num_orbits=4, 
            color=RED, 
            z_index=1
        )
        self.play(
            *[Create(orbit) for orbit in red_orbits],
            run_time=2
        )
        
        # Add the secondary orbits (black)
        black_orbits = self.create_orbit_family(
            a=4.8, 
            b=3.2, 
            num_orbits=6, 
            color=WHITE, 
            z_index=2
        )
        self.play(
            *[Create(orbit) for orbit in black_orbits],
            run_time=2
        )
        
        # Add inner orbital families with progressively smaller sizes
        all_inner_orbits = []
        for i in range(3, 8):
            a_i = LAMBDA**(i-2) * 4.8
            b_i = LAMBDA**(i-2) * 3.2
            
            # Alternate colors between red and white for inner shells
            color = RED if i % 2 == 1 else WHITE
            
            # Create more orbits for inner shells
            num_orbits = 6 if i % 2 == 0 else 4
            
            inner_orbits = self.create_orbit_family(
                a=a_i, 
                b=b_i, 
                num_orbits=num_orbits, 
                color=color, 
                z_index=i
            )
            
            all_inner_orbits.extend(inner_orbits)
            self.play(
                *[Create(orbit) for orbit in inner_orbits],
                run_time=1.5
            )
        
        # Highlight the nodal points
        self.explain_nodal_points(red_orbits[0], black_orbits[0])
        
        # Fade out all orbits and nucleus after explaining nodal points
        # This will make the mathematical explanations more visible
        all_orbits = VGroup(*red_orbits, *black_orbits, *all_inner_orbits)
        self.play(
            FadeOut(all_orbits),
            FadeOut(nucleus),
            run_time=1.5
        )
        
        # Explain quantization
        self.explain_quantization()
        
        # Fade the orbits back in for electron motion
        self.play(
            FadeIn(all_orbits),
            FadeIn(nucleus),
            run_time=1.5
        )
        
        # Show electron motion
        self.animate_electrons(red_orbits, black_orbits, all_inner_orbits)
        
        # Fade out orbits again for energy levels explanation
        self.play(
            FadeOut(all_orbits),
            FadeOut(nucleus),
            run_time=1.5
        )
        
        # Explain energy levels
        self.explain_energy_levels()
        
        # Conclusion
        self.conclusion()
    
    def introduce_topic(self):
        """Introduction to the radium atom animation"""
        title = Text("Structure of the Radium Atom", font_size=40)
        subtitle = Text("Bohr-Sommerfeld Model", font_size=30, color=BLUE)
        subtitle.next_to(title, DOWN)
        
        # Group the title elements
        title_group = VGroup(title, subtitle)
        
        # Add the atomic number information
        atomic_info = MathTex(r"\text{Radium (Ra)}", r"\quad Z = 88")
        atomic_info.next_to(subtitle, DOWN, buff=0.5)
        
        self.play(Write(title), run_time=1)
        self.play(Write(subtitle), run_time=1)
        self.play(Write(atomic_info), run_time=1)
        self.wait(1)
        
        # Move title to top of screen
        self.play(
            title_group.animate.scale(0.6).to_edge(UP),
            FadeOut(atomic_info),
            run_time=1
        )
    
    def create_nucleus(self):
        """Create the radium nucleus"""
        nucleus = Circle(radius=0.05, color=YELLOW, fill_opacity=1)
        
        # Add a pulsing animation to the nucleus
        nucleus.add_updater(
            lambda m, dt: m.set_opacity(
                0.7 + 0.3 * np.sin(0.5 * self.time)
            )
        )
        
        return nucleus
    
    def create_orbit_family(self, a, b, num_orbits, color, z_index=0):
        """Create a family of elliptical orbits with rotational symmetry"""
        orbits = []
        
        for k in range(num_orbits):
            theta = k * (2 * PI / num_orbits)
            
            # Create the elliptical path
            ellipse = Ellipse(
                width=2*a, 
                height=2*b, 
                color=color,
                stroke_opacity=0.8
            )
            
            # Apply rotation
            ellipse.rotate(theta)
            ellipse.z_index = z_index
            
            orbits.append(ellipse)
            
        return orbits
    
    def explain_nodal_points(self, red_orbit, black_orbit):
        """Explain the nodal points using an example orbit"""
        # Create the explanation text
        nodal_title = Text("Nodal Points", font_size=36)
        nodal_title.to_edge(UP, buff=1.5)
        
        # Define and highlight nodal points
        nodal_eq = MathTex(r"\frac{dr}{dt} = 0", font_size=30)
        nodal_eq.next_to(nodal_title, DOWN)
        
        # Add points to highlight major and minor axis nodes on the red orbit
        major_nodes = [
            Dot(red_orbit.point_from_proportion(0), color=YELLOW, radius=0.05),
            Dot(red_orbit.point_from_proportion(0.5), color=YELLOW, radius=0.05)
        ]
        
        minor_nodes = [
            Dot(red_orbit.point_from_proportion(0.25), color=GREEN, radius=0.05),
            Dot(red_orbit.point_from_proportion(0.75), color=GREEN, radius=0.05)
        ]
        
        # Labels for the nodal points
        alpha = MathTex(r"\alpha", color=YELLOW).next_to(major_nodes[0], UR, buff=0.1)
        beta = MathTex(r"\beta", color=YELLOW).next_to(major_nodes[1], DL, buff=0.1)
        gamma = MathTex(r"\gamma", color=GREEN).next_to(minor_nodes[0], UL, buff=0.1)
        delta = MathTex(r"\delta", color=GREEN).next_to(minor_nodes[1], DR, buff=0.1)
        
        # Create the animations
        self.play(Write(nodal_title), run_time=1)
        self.play(Write(nodal_eq), run_time=1)
        
        # Create major nodes
        self.play(
            *[Create(node) for node in major_nodes],
            Write(alpha), Write(beta),
            run_time=1.5
        )
        
        # Create minor nodes
        self.play(
            *[Create(node) for node in minor_nodes],
            Write(gamma), Write(delta),
            run_time=1.5
        )
        
        # Explain where they occur
        major_axis_formula = MathTex(r"t = \{0, \pi\} \text{ for major axis nodes}")
        minor_axis_formula = MathTex(r"t = \{\frac{\pi}{2}, \frac{3\pi}{2}\} \text{ for minor axis nodes}")
        
        formulas = VGroup(major_axis_formula, minor_axis_formula).arrange(DOWN)
        formulas.next_to(nodal_eq, DOWN, buff=0.5)
        
        self.play(Write(formulas), run_time=2)
        self.wait(1)
        
        # Clean up
        self.play(
            FadeOut(nodal_title), FadeOut(nodal_eq), FadeOut(formulas),
            *[FadeOut(node) for node in major_nodes + minor_nodes],
            FadeOut(alpha), FadeOut(beta), FadeOut(gamma), FadeOut(delta),
            run_time=1
        )
    
    def explain_quantization(self):
        """Explain the quantization rule and its significance"""
        quant_title = Text("Orbital Quantization", font_size=36)
        quant_title.to_edge(UP, buff=1.5)
        
        # Show the Bohr-Sommerfeld quantization rule
        quant_rule = MathTex(r"\oint p_{\phi} d\phi = n h", font_size=36)
        quant_rule.next_to(quant_title, DOWN, buff=0.5)
        
        # Explanation of terms
        explanation = VGroup(
            MathTex(r"p_{\phi} = \text{canonical angular momentum}"),
            MathTex(r"h = \text{Planck's constant}"),
            MathTex(r"n = \text{quantum number}")
        ).arrange(DOWN, aligned_edge=LEFT)
        explanation.next_to(quant_rule, DOWN, buff=0.5)
        
        # Show the animations
        self.play(Write(quant_title), run_time=1)
        self.play(Write(quant_rule), run_time=1)
        self.play(Write(explanation), run_time=2)
        
        # Add the angle pattern equation
        angle_pattern = MathTex(r"\theta_k = \frac{2\pi k}{n}", font_size=36)
        angle_pattern.next_to(explanation, DOWN, buff=0.7)
        
        angle_explanation = VGroup(
            MathTex(r"k = 0, 1, 2, ..., n-1"),
            MathTex(r"n = \text{number of orbits in family}")
        ).arrange(DOWN, aligned_edge=LEFT)
        angle_explanation.next_to(angle_pattern, DOWN, buff=0.5)
        
        self.play(Write(angle_pattern), run_time=1)
        self.play(Write(angle_explanation), run_time=1.5)
        self.wait(2)
        
        # Clean up
        self.play(
            FadeOut(quant_title), FadeOut(quant_rule), FadeOut(explanation),
            FadeOut(angle_pattern), FadeOut(angle_explanation),
            run_time=1
        )
    
    def animate_electrons(self, red_orbits, black_orbits, inner_orbits):
        """Animate electrons moving along the orbits"""
        electron_title = Text("Electron Motion", font_size=36)
        electron_title.to_edge(UP, buff=1.5)
        
        # Formula for electron position
        position_formula = MathTex(
            r"\mathbf{r}(t) = R_{\theta} \begin{pmatrix} a\cos(\omega t + \phi_0) \\ b\sin(\omega t + \phi_0) \end{pmatrix}",
            font_size=30
        )
        position_formula.next_to(electron_title, DOWN, buff=0.5)
        
        # Formula for angular frequency (Kepler's law)
        frequency_formula = MathTex(
            r"\omega \propto \frac{1}{a^{3/2}}",
            font_size=30
        )
        frequency_formula.next_to(position_formula, DOWN, buff=0.5)
        
        # Show the formulas
        self.play(Write(electron_title), run_time=1)
        self.play(Write(position_formula), run_time=1.5)
        self.play(Write(frequency_formula), run_time=1)
        
        # Create electrons for animation
        electrons = []
        
        # Generate 2 electrons for red orbits (slower)
        for orbit in red_orbits[:2]:
            electron = Dot(color=RED_A, radius=0.03)
            # Place at random position on the orbit
            t = np.random.random() * TAU
            electron.move_to(orbit.point_from_proportion(t/TAU))
            electrons.append((electron, orbit, 0.5))  # (electron, orbit, speed)
        
        # Generate 3 electrons for black orbits (medium speed)
        for orbit in black_orbits[:3]:
            electron = Dot(color=WHITE, radius=0.03)
            t = np.random.random() * TAU
            electron.move_to(orbit.point_from_proportion(t/TAU))
            electrons.append((electron, orbit, 0.7))
        
        # Generate 4 electrons for inner orbits (faster)
        for orbit in inner_orbits[:4]:
            electron = Dot(color=BLUE_A, radius=0.03)
            t = np.random.random() * TAU
            electron.move_to(orbit.point_from_proportion(t/TAU))
            electrons.append((electron, orbit, 1.0))
        
        # Add the electrons to the scene
        self.play(*[FadeIn(e[0]) for e in electrons], run_time=1)
        
        # Add the electron updaters
        def electron_updater(electron, orbit, speed, dt):
            # The current proportion along the curve
            curr_t = orbit.proportion_from_point(electron.get_center())
            if curr_t is None:
                curr_t = 0
            # Advance by speed * dt
            new_t = (curr_t + speed * dt) % 1
            # Move to the new position
            electron.move_to(orbit.point_from_proportion(new_t))
        
        # Apply the updaters
        for e, orbit, speed in electrons:
            e.add_updater(lambda m, dt, o=orbit, s=speed: electron_updater(m, o, s, dt))
        
        # Let the animation run for a while
        self.wait(5)
        
        # Remove the updaters and clean up
        for e, _, _ in electrons:
            e.clear_updaters()
        
        self.play(
            FadeOut(electron_title), FadeOut(position_formula), FadeOut(frequency_formula),
            *[FadeOut(e[0]) for e in electrons],
            run_time=1
        )
    
    def explain_energy_levels(self):
        """Explain the energy levels in the Bohr model"""
        energy_title = Text("Energy Levels", font_size=36)
        energy_title.to_edge(UP, buff=1.5)
        
        # Energy formula
        energy_formula = MathTex(
            r"E_n = -\frac{Z^2 e^4 m}{8 \varepsilon_0^2 h^2 n^2} = -\frac{13.6 \, \text{eV} \cdot Z^2}{n^2}",
            font_size=30
        )
        energy_formula.next_to(energy_title, DOWN, buff=0.5)
        
        # Radium ground state energy
        radium_energy = MathTex(
            r"E_1 = -13.6 \, \text{eV} \cdot 88^2 = -105,318.4 \, \text{eV}",
            font_size=30
        )
        radium_energy.next_to(energy_formula, DOWN, buff=0.5)
        
        # Create a visual energy level diagram
        levels = 4
        level_height = 0.5
        level_width = 4
        
        energy_diagram = VGroup()
        
        # Create energy level lines
        for n in range(1, levels+1):
            # Calculate energy proportion for visualization (not to scale)
            energy_prop = 1/n**2
            
            # Create line
            line = Line(
                start=[-level_width/2, -2 - n*level_height, 0],
                end=[level_width/2, -2 - n*level_height, 0],
                color=BLUE
            )
            
            # Add label
            label = MathTex(f"n={n}", font_size=24)
            label.next_to(line, LEFT, buff=0.3)
            
            # Add energy value
            energy_val = MathTex(
                f"E_{n} = {-105318.4/n**2:.1f} \\, \\text{{eV}}",
                font_size=20
            )
            energy_val.next_to(line, RIGHT, buff=0.3)
            
            energy_diagram.add(line, label, energy_val)
        
        # Show the formula and diagram
        self.play(Write(energy_title), run_time=1)
        self.play(Write(energy_formula), run_time=1.5)
        self.play(Write(radium_energy), run_time=1.5)
        self.play(Create(energy_diagram), run_time=2)
        
        self.wait(2)
        
        # Clean up
        self.play(
            FadeOut(energy_title), FadeOut(energy_formula), 
            FadeOut(radium_energy), FadeOut(energy_diagram),
            run_time=1
        )
    
    def conclusion(self):
        """Conclude the animation"""
        conclusion_text = Text("The Bohr-Sommerfeld Model", font_size=36)
        conclusion_text.to_edge(UP, buff=1.5)
        
        points = VGroup(
            Text("• Historical model from early quantum theory", font_size=24),
            Text("• Electrons move in elliptical orbits", font_size=24),
            Text("• Angular momentum is quantized", font_size=24),
            Text("• Predated modern quantum mechanics", font_size=24),
            Text("• Provided foundation for atomic structure understanding", font_size=24)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        points.next_to(conclusion_text, DOWN, buff=0.7)
        
        # Final statement
        final_text = Text(
            "Later replaced by quantum mechanical wave model",
            color=YELLOW,
            font_size=28
        )
        final_text.next_to(points, DOWN, buff=0.7)
        
        # Show conclusion
        self.play(Write(conclusion_text), run_time=1)
        
        for point in points:
            self.play(Write(point), run_time=0.8)
        
        self.play(Write(final_text), run_time=1)
        self.wait(2)
        
        # Final fade out
        self.play(
            FadeOut(conclusion_text),
            FadeOut(points),
            FadeOut(final_text),
            run_time=2
        )


class RotationTransformation(Scene):
    """Demonstrates how rotation matrix transforms elliptical orbits"""
    def construct(self):
        # Create title
        title = Text("Orbital Rotation Transformations", font_size=40)
        title.to_edge(UP)
        self.play(Write(title), run_time=1)
        
        # Create the rotation matrix
        matrix_tex = MathTex(
            r"R_{\theta} = \begin{pmatrix} \cos\theta & -\sin\theta \\ \sin\theta & \cos\theta \end{pmatrix}",
            font_size=36
        )
        matrix_tex.next_to(title, DOWN, buff=0.7)
        self.play(Write(matrix_tex), run_time=1.5)
        
        # Base ellipse
        a, b = 2, 1.2
        base_ellipse = Ellipse(width=2*a, height=2*b, color=BLUE)
        
        # Create multiple rotated ellipses
        num_orbits = 6
        rotated_ellipses = []
        
        for k in range(num_orbits):
            theta = k * (2 * PI / num_orbits)
            rotated = Ellipse(width=2*a, height=2*b, color=RED_A)
            rotated.rotate(theta)
            rotated_ellipses.append(rotated)
        
        # Show base ellipse first
        self.play(Create(base_ellipse), run_time=1)
        self.wait(1)
        
        # Create angle formula
        angle_formula = MathTex(r"\theta_k = \frac{2\pi k}{n}", font_size=36)
        angle_formula.to_edge(DOWN, buff=1)
        self.play(Write(angle_formula), run_time=1)
        
        # Now create all rotated ellipses one by one
        for i, ellipse in enumerate(rotated_ellipses):
            theta_val = MathTex(
                f"\\theta_{i} = \\frac{{2\\pi \\cdot {i}}}{{{num_orbits}}} = {round(i*360/num_orbits)}^\\circ",
                font_size=28
            )
            theta_val.next_to(angle_formula, UP, buff=0.3)
            
            self.play(
                Create(ellipse),
                Write(theta_val),
                run_time=0.8
            )
            
            if i < len(rotated_ellipses) - 1:
                self.play(FadeOut(theta_val), run_time=0.3)
        
        # Final layout with all ellipses
        self.wait(2)
        
        # Clean up and conclusion
        self.play(
            *[FadeOut(mob) for mob in self.mobjects],
            run_time=1.5
        )


class ParametricEllipseScene(Scene):
    """Demonstrates the parametric equation of an ellipse"""
    def construct(self):
        # Title
        title = Text("Parametric Equation of an Ellipse", font_size=40)
        title.to_edge(UP)
        self.play(Write(title), run_time=1)
        
        # Parametric equations
        x_eq = MathTex(r"x(t) = a\cos(t)", font_size=36)
        y_eq = MathTex(r"y(t) = b\sin(t)", font_size=36)
        
        equations = VGroup(x_eq, y_eq).arrange(DOWN, aligned_edge=LEFT)
        equations.next_to(title, DOWN, buff=0.7)
        
        self.play(Write(equations), run_time=1.5)
        
        # Create a coordinate system
        axes = Axes(
            x_range=[-3, 3, 1],
            y_range=[-2, 2, 1],
            axis_config={"include_tip": False}
        )
        
        axes.add_coordinates()
        
        # Label the axes
        x_label = MathTex("x").next_to(axes.x_axis, DOWN)
        y_label = MathTex("y").next_to(axes.y_axis, LEFT)
        
        self.play(
            Create(axes),
            Write(x_label),
            Write(y_label),
            run_time=1.5
        )
        
        # Create an ellipse
        a, b = 2, 1.2
        ellipse = ParametricFunction(
            lambda t: axes.c2p(a*np.cos(t), b*np.sin(t)),
            t_range=[0, TAU],
            color=YELLOW
        )
        
        # Add a moving dot and point
        dot = Dot(color=RED)
        dot.move_to(axes.c2p(a, 0))
        
        # Lines to show a and b values
        a_line = Line(
            start=axes.c2p(0, 0),
            end=axes.c2p(a, 0),
            color=GREEN
        )
        a_label = MathTex("a", font_size=24, color=GREEN)
        a_label.next_to(a_line, DOWN, buff=0.1)
        
        b_line = Line(
            start=axes.c2p(0, 0),
            end=axes.c2p(0, b),
            color=BLUE
        )
        b_label = MathTex("b", font_size=24, color=BLUE)
        b_label.next_to(b_line, RIGHT, buff=0.1)
        
        self.play(
            Create(a_line), Write(a_label),
            Create(b_line), Write(b_label),
            run_time=1.5
        )
        
        # Draw the ellipse and add the dot
        self.play(
            Create(ellipse),
            FadeIn(dot),
            run_time=2
        )
        
        # Animate the dot along the ellipse
        self.play(
            MoveAlongPath(dot, ellipse),
            run_time=4,
            rate_func=linear
        )
        
        # Show the parameter t
        t_tracker = ValueTracker(0)
        
        t_pointer = Vector([1, 0], color=RED)
        t_pointer.move_to(axes.c2p(0, 0))
        
        t_label = MathTex("t", font_size=24, color=RED)
        t_label.add_updater(
            lambda m: m.next_to(
                axes.c2p(1.5*np.cos(t_tracker.get_value()), 
                         1.5*np.sin(t_tracker.get_value())),
                direction=RIGHT if np.cos(t_tracker.get_value()) > 0 else LEFT,
                buff=0.1
            )
        )
        
        def update_pointer(mob):
            angle = t_tracker.get_value()
            mob.set_angle(angle)
            mob.scale(0.5 / mob.get_length())
            mob.next_to(ORIGIN, direction=UP, buff=0)
            mob.shift(axes.c2p(0, 0) - mob.get_start())
        
        t_pointer.add_updater(update_pointer)
        
        # Position updater for the dot
        dot.add_updater(
            lambda m: m.move_to(
                axes.c2p(
                    a*np.cos(t_tracker.get_value()),
                    b*np.sin(t_tracker.get_value())
                )
            )
        )
        
        # Add the pointer and label
        self.play(
            Create(t_pointer),
            Write(t_label),
            run_time=1
        )
        
        # Animate the parameter t
        self.play(
            t_tracker.animate.set_value(TAU),
            run_time=6,
            rate_func=linear
        )
        
        self.wait(1)
        
        # Clean up
        self.play(
            *[FadeOut(mob) for mob in self.mobjects],
            run_time=1.5
        )


# Define a class for a complete showcase of the Radium atom model
class RadiumAtomFullAnimation(Scene):
    def construct(self):
        # Show title sequence
        title = Text("The Radium Atom", font_size=48)
        subtitle = Text("Bohr-Sommerfeld Model Visualization", font_size=32)
        subtitle.next_to(title, DOWN)
        
        title_group = VGroup(title, subtitle)
        self.play(Write(title_group), run_time=2)
        self.wait(1)
        self.play(FadeOut(title_group), run_time=1)
        
        # Instead of trying to reuse other scenes, let's just add a message
        # explaining that we need to render each scene separately
        
        message = Text(
            "To view the full animation, please render each scene separately:",
            font_size=28
        ).to_edge(UP)
        
        scenes = VGroup(
            Text("1. ParametricEllipseScene", font_size=24),
            Text("2. RotationTransformation", font_size=24),
            Text("3. RadiumAtomStructure", font_size=24)
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.5)
        scenes.next_to(message, DOWN, buff=0.7)
        
        command = Text(
            "Command: manim -pqh radium_atom.py SceneName",
            font_size=24,
            color=YELLOW
        ).next_to(scenes, DOWN, buff=0.7)
        
        self.play(Write(message), run_time=1)
        self.play(Write(scenes), run_time=2)
        self.play(Write(command), run_time=1)
        self.wait(2)
        
        # Final credits
        credits = Text("Created with Manim Community Edition", font_size=32)
        credits.to_edge(DOWN, buff=1)
        self.play(Write(credits), run_time=1.5)
        self.wait(2)
        self.play(
            FadeOut(message),
            FadeOut(scenes),
            FadeOut(command),
            FadeOut(credits),
            run_time=1
        )


if __name__ == "__main__":
    # Uncomment the scene you want to render
    # Command to render: manim -pqh radium_atom.py RadiumAtomFullAnimation
    pass