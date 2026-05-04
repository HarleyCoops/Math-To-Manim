# Manim Code Patterns

Best practices and patterns for generating high-quality Manim Community Edition code.

## Basic Structure

```python
from manim import *

class ConceptAnimation(Scene):  # or ThreeDScene for 3D
    def construct(self):
        # Setup phase
        self.setup_scene()

        # Scene 1: Foundation concept
        self.scene_foundation()

        # Scene 2: Build up
        self.scene_buildup()

        # Scene 3: Target concept
        self.scene_target()

    def setup_scene(self):
        """Initialize shared elements and colors"""
        self.colors = {
            'primary': BLUE,
            'secondary': YELLOW,
            'highlight': GOLD,
            'axes': WHITE
        }

    def scene_foundation(self):
        """First concept - foundation level"""
        pass

    def scene_buildup(self):
        """Intermediate concepts"""
        pass

    def scene_target(self):
        """Final target concept"""
        pass
```

## LaTeX Handling

### Always Use Raw Strings
```python
# Correct
equation = MathTex(r"E = mc^2")
fraction = MathTex(r"\frac{a}{b}")
integral = MathTex(r"\int_0^\infty f(x) dx")

# Incorrect - will cause errors
equation = MathTex("E = mc^2")  # Works but bad practice
fraction = MathTex("\frac{a}{b}")  # FAILS - backslash issues
```

### Complex Equations
```python
# Multi-line equations
schrodinger = MathTex(
    r"i\hbar\frac{\partial}{\partial t}\Psi",
    r"=",
    r"\hat{H}\Psi"
)

# Color specific parts
schrodinger[0].set_color(BLUE)   # Left side
schrodinger[2].set_color(GREEN)  # Right side
```

### Text with Math
```python
# Use Tex for mixed content
mixed = Tex(r"The energy ", r"$E$", r" equals ", r"$mc^2$")
mixed[1].set_color(BLUE)
mixed[3].set_color(YELLOW)
```

## Animation Patterns

### Sequential Animations
```python
# One after another
self.play(FadeIn(axes))
self.play(Write(equation))
self.play(Create(graph))
self.wait(1)
```

### Simultaneous Animations
```python
# Multiple at once using AnimationGroup
self.play(
    FadeIn(axes),
    Write(title),
    run_time=2
)

# Or comma-separated
self.play(FadeIn(axes), Write(title))
```

### Smooth Transitions
```python
# Transform one object into another
self.play(Transform(old_equation, new_equation))

# Replace without animation artifact
self.play(ReplacementTransform(old, new))

# Fade transition
self.play(FadeOut(old), FadeIn(new))
```

## Positioning Patterns

### Relative Positioning
```python
# Edge positioning
equation.to_edge(UP)
graph.to_edge(LEFT, buff=1)

# Corner positioning
label.to_corner(UR)  # Upper right

# Relative to another object
label.next_to(equation, DOWN, buff=0.5)
arrow.next_to(point, RIGHT)
```

### Grouping and Arrangement
```python
# Vertical arrangement
equations = VGroup(eq1, eq2, eq3)
equations.arrange(DOWN, buff=0.5)
equations.to_edge(LEFT)

# Horizontal arrangement
labels = VGroup(l1, l2, l3)
labels.arrange(RIGHT, buff=1)
```

### Coordinate-Based
```python
# Absolute position
point.move_to(np.array([2, 1, 0]))
point.move_to(2*RIGHT + 1*UP)

# Shift relative
equation.shift(2*LEFT + 0.5*UP)
```

## Color Management

### Consistent Color Palette
```python
class ConceptAnimation(Scene):
    # Define colors as class attributes
    PRIMARY = BLUE
    SECONDARY = YELLOW
    HIGHLIGHT = GOLD
    AXES_COLOR = WHITE
    GRAPH_COLOR = GREEN

    def construct(self):
        equation = MathTex(r"E = mc^2").set_color(self.PRIMARY)
        highlight_box = SurroundingRectangle(equation, color=self.HIGHLIGHT)
```

### Color Transitions
```python
# Animate color change
self.play(equation.animate.set_color(RED))

# Highlight temporarily
self.play(
    equation.animate.set_color(GOLD),
    run_time=0.5
)
self.play(
    equation.animate.set_color(BLUE),
    run_time=0.5
)
```

## 3D Scene Patterns

### Basic 3D Setup
```python
class ThreeDConcept(ThreeDScene):
    def construct(self):
        # Set up 3D axes
        axes = ThreeDAxes()

        # Position camera
        self.set_camera_orientation(phi=75*DEGREES, theta=45*DEGREES)

        # Add ambient rotation
        self.begin_ambient_camera_rotation(rate=0.1)

        self.play(Create(axes))

        # Create 3D surface
        surface = Surface(
            lambda u, v: np.array([u, v, np.sin(u)*np.cos(v)]),
            u_range=[-3, 3],
            v_range=[-3, 3],
            resolution=(30, 30)
        )

        self.play(Create(surface))
        self.wait(5)
```

### Camera Movements
```python
# Move camera smoothly
self.move_camera(phi=60*DEGREES, theta=30*DEGREES, run_time=2)

# Zoom
self.move_camera(zoom=1.5, run_time=1)

# Frame movement
self.play(self.camera.frame.animate.shift(2*RIGHT))
```

## Value Tracking and Updates

### Dynamic Updates
```python
# Create tracker
momentum = ValueTracker(1)

# Create object that depends on tracker
wavelength = always_redraw(
    lambda: MathTex(
        rf"\lambda = {1/momentum.get_value():.2f}"
    ).to_edge(UP)
)

self.add(wavelength)

# Animate the tracker
self.play(momentum.animate.set_value(5), run_time=3)
```

### Updaters for Continuous Animation
```python
# Add updater to object
dot = Dot()
dot.add_updater(lambda m, dt: m.shift(0.5*RIGHT*dt))

self.add(dot)
self.wait(3)  # Dot moves continuously

dot.clear_updaters()  # Stop movement
```

## Error Prevention

### Common Fixes

```python
# Problem: LaTeX rendering fails
# Solution: Use raw strings and double backslashes
eq = MathTex(r"\frac{d}{dx}")  # Correct

# Problem: Object not visible
# Solution: Check z_index for overlapping
foreground.set_z_index(1)
background.set_z_index(0)

# Problem: Animation too fast/slow
# Solution: Specify run_time
self.play(Create(complex_graph), run_time=3)

# Problem: Jerky transitions
# Solution: Use rate functions
self.play(
    Transform(a, b),
    rate_func=smooth,
    run_time=2
)
```

### Defensive Patterns

```python
# Check object exists before animating
if hasattr(self, 'previous_equation'):
    self.play(FadeOut(self.previous_equation))

# Group cleanup
def clear_scene(self):
    self.play(*[FadeOut(mob) for mob in self.mobjects])

# Safe color access
color = getattr(self, 'PRIMARY', BLUE)
```

## Scene Organization

### Breaking Complex Animations into Methods

```python
class QuantumTunneling(ThreeDScene):
    def construct(self):
        self.intro_foundation()
        self.show_wave_function()
        self.demonstrate_barrier()
        self.show_tunneling()
        self.conclusion()

    def intro_foundation(self):
        """Foundation concepts"""
        title = Text("Wave-Particle Duality")
        self.play(Write(title))
        self.wait(2)
        self.play(FadeOut(title))

    def show_wave_function(self):
        """Wave function visualization"""
        # Detailed implementation
        pass

    # ... other methods
```

### Reusable Components

```python
def create_labeled_equation(tex_string, label_text, color=BLUE):
    """Create equation with label below"""
    equation = MathTex(tex_string).set_color(color)
    label = Text(label_text, font_size=24).next_to(equation, DOWN)
    return VGroup(equation, label)

# Usage
energy_eq = create_labeled_equation(r"E = mc^2", "Mass-energy equivalence")
self.play(FadeIn(energy_eq))
```

## Rendering Commands

```bash
# Preview quality (fast)
manim -pql animation.py SceneName

# Medium quality
manim -pqm animation.py SceneName

# High quality (slow)
manim -pqh animation.py SceneName

# 4K quality
manim -pqk animation.py SceneName

# Save as GIF
manim -pql --format=gif animation.py SceneName
```
