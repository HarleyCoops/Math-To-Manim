# Verbose Prompt Format

The verbose prompt is the bridge between the knowledge tree and working Manim code. A well-structured verbose prompt produces dramatically better animations than vague descriptions.

## Why Verbose Prompts Work

1. **LaTeX forces precision**: Exact mathematical notation leaves no ambiguity
2. **Detailed cinematography**: Specific colors, positions, and timings guide code generation
3. **Sequential structure**: Clear scene ordering produces organized code
4. **Complete specifications**: Nothing left to guess or infer

## Complete Template

```markdown
# Manim Animation: {TARGET_CONCEPT}

## Overview
This animation builds {TARGET_CONCEPT} from first principles through a carefully
constructed knowledge tree. Each concept is explained with mathematical rigor
and visual clarity, building from foundational ideas to advanced understanding.

**Total Concepts**: {CONCEPT_COUNT}
**Progression**: {CONCEPT_1} -> {CONCEPT_2} -> ... -> {TARGET_CONCEPT}
**Estimated Duration**: {TOTAL_SECONDS} seconds ({MINUTES}:{SECONDS:02d})

## Animation Requirements
- Use Manim Community Edition (manim)
- All LaTeX must be in raw strings: r"$\\frac{a}{b}$"
- Use MathTex() for equations, Text() for labels
- Maintain color consistency throughout
- Ensure smooth transitions between scenes
- Include voiceover-friendly pacing (2-3 seconds per concept introduction)

## Scene Sequence

### Scene 1: {CONCEPT_1}
**Timestamp**: 0:00 - 0:15

Begin by fading in the coordinate axes using FadeIn(axes) with WHITE color.
Position the axes at ORIGIN. Next, display the foundational equation
r"$y = mx + b$" using MathTex() in BLUE color, positioning it at the TOP
of the screen using .to_edge(UP).

Create the equation using Write(equation) animation over 2 seconds. Then,
draw a sample line using Create(line) in YELLOW color, showing a concrete
example of y = 2x + 1. Label the line with Text("slope = 2") in GREEN,
positioned to the RIGHT of the line.

Wait 1 second, then fade all elements to prepare for the next concept using
FadeOut(Group(axes, equation, line, label)).

---

### Scene 2: {CONCEPT_2}
**Timestamp**: 0:15 - 0:30

{SIMILAR DETAILED DESCRIPTION}

---

### Scene N: {TARGET_CONCEPT}
**Timestamp**: {START} - {END}

This is the culminating scene. Transform the previous elements to show how
all concepts connect to {TARGET_CONCEPT}. Display the key equation
r"${MAIN_EQUATION}$" prominently in the center using MathTex() with GOLD color.

Highlight the connection to prerequisites by using Indicate() on relevant
terms. Add a final summary text explaining the core insight.

---

## Final Notes

This animation is designed to be pedagogically sound and mathematically rigorous.
The progression from {FIRST_CONCEPT} to {TARGET_CONCEPT} ensures that viewers
have all necessary prerequisites before encountering advanced concepts.

All visual elements, colors, and transitions have been specified to maintain
consistency and clarity throughout the {TOTAL_SECONDS}-second animation.

Generate complete, working Manim Community Edition Python code that implements
this scene sequence with all specified mathematical notation, visual elements,
colors, and animations.
```

## Scene Segment Structure

Each scene segment should include:

### 1. Timestamp Header
```markdown
### Scene 3: Schrödinger Equation
**Timestamp**: 0:30 - 0:45
```

### 2. Opening Action
Start with a verb describing the first animation:
- "Begin by fading in..."
- "Start with the transformation of..."
- "Open by displaying..."

### 3. Equation Display
Include exact LaTeX with positioning:
```
Display the equation r"$i\hbar\frac{\partial}{\partial t}\Psi = \hat{H}\Psi$"
using MathTex() in BLUE color, centered at ORIGIN.
```

### 4. Visual Elements
Specify all objects with:
- Manim class: `MathTex()`, `Text()`, `Axes()`, `Circle()`
- Color: `BLUE`, `RED`, `YELLOW`, etc.
- Position: `ORIGIN`, `UP`, `LEFT`, `.to_edge()`, `.next_to()`

### 5. Animation Sequence
List animations in order:
```
1. FadeIn(axes) over 1 second
2. Write(equation) over 2 seconds
3. Create(graph) following the equation curve
4. Indicate(key_term) with YELLOW highlight
5. Wait 1 second
6. FadeOut(Group(all_elements))
```

### 6. Transition Hook
End with setup for next scene:
```
The equation remains on screen, shifted to the upper left,
as we introduce the next concept.
```

## Color Palette Guidelines

Maintain consistency across scenes:

| Element Type | Recommended Color |
|--------------|-------------------|
| Primary equations | BLUE |
| Secondary equations | YELLOW |
| Axes/grids | WHITE or GREY |
| Graphs/curves | YELLOW, GREEN |
| Labels | GREEN |
| Highlights | GOLD or ORANGE |
| Warnings/errors | RED |
| Success/completion | GREEN |

## Timing Guidelines

| Content Type | Duration |
|--------------|----------|
| Simple equation display | 2-3 seconds |
| Complex equation with explanation | 4-5 seconds |
| Graph/visualization creation | 3-4 seconds |
| Transition between concepts | 1-2 seconds |
| Pause for comprehension | 1 second |
| Complete scene | 15-30 seconds |

## Example: Complete Scene Segment

```markdown
### Scene 4: Wave-Particle Duality
**Timestamp**: 0:45 - 1:05

Begin by transforming the previous probability wave into a particle
representation using ReplacementTransform(wave, particle). The particle
appears as a Dot() in YELLOW at the center of the screen.

Next, display de Broglie's equation r"$\lambda = \frac{h}{p}$" using
MathTex() in BLUE color, positioned at the TOP using .to_edge(UP).
Write the equation over 2 seconds.

Below the equation, create a Text() label explaining each variable:
- r"$\lambda$" = wavelength (GREEN)
- r"$h$" = Planck's constant (YELLOW)
- r"$p$" = momentum (ORANGE)

Position these labels in a VGroup(), arranged vertically with
.arrange(DOWN, buff=0.3), and place them at the RIGHT side of the screen.

Now demonstrate the wave-particle connection: Create a sinusoidal wave
using ParametricFunction() in PURPLE, with amplitude that varies based
on the particle's momentum. Use Create(wave) animation over 3 seconds.

Show that as momentum increases (particle moving faster), wavelength
decreases. Use ValueTracker to animate momentum from 1 to 5, with the
wave responding in real-time using always_redraw().

Conclude by highlighting the key insight: matter has wave properties.
Use Circumscribe(equation) with GOLD color to emphasize the equation,
then FadeOut all elements except the equation, which shifts to upper-left
corner for the next scene.
```

## Common Pitfalls to Avoid

1. **Vague descriptions**: "Show the equation" -> "Display r'$E=mc^2$' using MathTex() in BLUE at TOP"
2. **Missing positions**: Always specify where elements appear
3. **Unclear timing**: Include duration for each animation
4. **No transitions**: Explicitly describe how scenes connect
5. **Inconsistent colors**: Define palette and stick to it
6. **Missing LaTeX escaping**: Use raw strings with double backslashes
