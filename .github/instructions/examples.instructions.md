---
applies_to:
  - "examples/**/*.py"
description: Guidelines for creating and modifying Manim animation examples
---

# Animation Examples Guidelines

## Purpose

This directory contains 55+ working Manim animations demonstrating various mathematical, physical, and computational concepts. Each animation serves as both a working example and educational reference.

## Creating New Animation Examples

### File Organization
- Place animations in the appropriate category directory:
  - `examples/physics/` - Physics concepts (quantum, gravity, nuclear, particle physics)
  - `examples/mathematics/` - Math concepts (geometry, analysis, fractals, statistics)
  - `examples/computer_science/` - CS concepts (ML, algorithms, spatial reasoning)
  - `examples/cosmology/` - Cosmology and astrophysics
  - `examples/finance/` - Financial mathematics
  - `examples/misc/` - Experimental or uncategorized

### Naming Conventions
- Use descriptive, lowercase names with underscores: `schrodinger_equation.py`, not `scene1.py`
- Name should clearly indicate the concept being visualized
- Scene class name should be descriptive and in PascalCase: `SchrodingerEquationScene`

### Required Components

1. **Module Docstring**: Every animation file must start with a comprehensive docstring:
```python
"""
Visualization of the Schrödinger equation in quantum mechanics.

Shows:
- Wave function evolution
- Probability density interpretation
- Energy eigenstates
- Potential well scenarios

Mathematical Concepts:
- Time-independent Schrödinger equation: Hψ = Eψ
- Time-dependent form: iℏ ∂ψ/∂t = Hψ
- Wave function normalization
- Expectation values

Generated using: Claude Sonnet 4.5 / DeepSeek R1 / etc.
"""
```

2. **Import Organization**:
```python
from manim import *
import numpy as np
# Other standard library imports
# Then project-specific imports if needed
```

3. **Scene Class with Docstring**:
```python
class SchrodingerEquationScene(Scene):
    """
    Main scene for Schrödinger equation visualization.
    
    Demonstrates wave function evolution in a potential well.
    """
    def construct(self):
        # Implementation
```

### Mathematical Notation Standards

**LaTeX Formatting**:
- Use `$$...$$` for displayed equations (centered, large)
- Use `$...$` for inline math (smaller, in text)
- Always escape special characters: `\_`, `\{`, `\}`, `\&`, `\%`
- Use raw strings when possible: `r"$E = mc^2$"`

**Common Notation**:
- Vectors: `\vec{E}` or `\mathbf{E}`
- Matrices: `\mathbf{A}` or `\boldsymbol{A}`
- Operators: `\hat{H}` for Hamiltonian operator
- Greek letters: `\alpha`, `\beta`, `\gamma`, etc.
- Script letters: `\mathcal{L}` for Lagrangian
- Fractions: `\frac{numerator}{denominator}`
- Subscripts/superscripts: `E_0`, `x^2`

**LaTeX Best Practices**:
```python
# Good - raw string, proper escaping
equation = r"$\frac{d\psi}{dt} = -\frac{i}{\hbar}\hat{H}\psi$"

# Bad - not escaped, will cause rendering errors
equation = "$\frac{d\psi}{dt} = -\frac{i}{\hbar}\hat{H}\psi$"

# Use Text mobject with LaTeX
eq = MathTex(r"\frac{1}{2}mv^2")
```

### Visual Design Principles

**Color Schemes**:
- Use consistent colors for related concepts
- Common conventions:
  - Blue: Electric field, wave function magnitude
  - Red: Magnetic field, potential energy
  - Green: Velocity, derivatives
  - Yellow/Gold: Energy, important equations
  - White: Text and labels

**Camera and Staging**:
- Start with establishing shots showing full context
- Use camera movements sparingly for emphasis
- Zoom in on important details
- Return to overview before transitioning

**Animation Timing**:
- Allow 2-3 seconds for viewers to read equations
- Use `run_time` parameter to control animation speed
- Add pauses with `self.wait()` between major concepts
- Typical scene: 30-90 seconds total

### Code Organization

Structure your `construct()` method in clear sections:
```python
def construct(self):
    # 1. Setup and title
    title = Text("Schrödinger Equation")
    self.play(Write(title))
    self.wait(2)
    self.play(FadeOut(title))
    
    # 2. Introduce core equation
    equation = MathTex(r"i\hbar\frac{\partial\psi}{\partial t} = \hat{H}\psi")
    self.play(Write(equation))
    self.wait(3)
    
    # 3. Build up visualization
    # ... your visualization code ...
    
    # 4. Demonstrate key concept
    # ... animation code ...
    
    # 5. Conclusion
    self.play(FadeOut(VGroup(*self.mobjects)))
```

### Testing Your Animation

Before committing, verify:
1. **Renders successfully**: `manim -pql examples/path/to/file.py YourScene`
2. **LaTeX renders correctly**: Check all equations appear properly
3. **Timing is appropriate**: Not too fast or too slow
4. **File size is reasonable**: Keep under 50MB for low quality
5. **Follows naming conventions**: Descriptive names

### Common Pitfalls

1. **LaTeX Syntax Errors**:
   - Unescaped underscores: `E_0` → `E\_0` in strings
   - Mismatched braces: `\frac{1{2}` → `\frac{1}{2}`
   - Missing backslashes: `alpha` → `\alpha`

2. **Performance Issues**:
   - Too many objects on screen at once
   - Overly complex 3D scenes
   - Not using `VGroup` for related objects

3. **Visual Clarity**:
   - Text too small to read
   - Colors too similar to background
   - Animations too fast to follow
   - Too much information at once

### Quality Standards

**Good Animation Checklist**:
- [ ] Module docstring explains concept clearly
- [ ] LaTeX equations render correctly
- [ ] Timing allows viewers to absorb information
- [ ] Colors are consistent and meaningful
- [ ] Code is organized with comments
- [ ] Scene name is descriptive
- [ ] File is in correct category directory
- [ ] Animation demonstrates the concept effectively

### Reference Examples

**High Quality Examples to Study**:
- `examples/physics/quantum/QED.py` - Complex physics with multiple concepts
- `examples/mathematics/geometry/pythagorean.py` - Clear visual proof
- `examples/computer_science/machine_learning/AlexNet.py` - Network architecture

### Adding to Documentation

After creating your animation:
1. Test it renders: `manim -pql your_file.py YourScene`
2. Generate preview: `manim -pql --format=gif your_file.py YourScene` (optional)
3. Add entry to `docs/EXAMPLES.md` with description
4. Submit PR with clear description of the concept

### Modifying Existing Animations

When updating existing animations:
- Preserve the original mathematical accuracy
- Don't change working LaTeX unless fixing errors
- Test thoroughly before committing
- Document changes in commit message
- Keep the same visual style unless improving clarity

### Getting Help

- **Manim Documentation**: https://docs.manim.community/
- **LaTeX Reference**: https://oeis.org/wiki/List_of_LaTeX_mathematical_symbols
- **Example Catalog**: See `docs/EXAMPLES.md`
- **Ask Questions**: Open an issue for clarification

## Remember

The goal is educational clarity. Every animation should make a complex concept more understandable through visualization. When in doubt, prioritize clarity over complexity.
