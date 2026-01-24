#!/usr/bin/env python3
"""
Quick test of the Three.js code generator with a trigonometric integral visualization.
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not required if ANTHROPIC_API_KEY is already set

from agents.threejs_code_generator import ThreeJSCodeGenerator

# The integral from the image - a sophisticated trigonometric integral
VERBOSE_PROMPT = r"""# Three.js Animation: Trigonometric Integral Visualization

## Overview
Visualize the integral:
$$\int_0^{\pi/2} \frac{x \sin(2x)}{(1 + a\sin^2 x)(1 + b\cos^2 x)} dx$$

This animation shows how the integrand behaves for different values of parameters a and b,
and demonstrates the beautiful closed-form solution.

### Scene 1: The Integrand Surface
Create a 3D surface plot showing f(x, a) where:
- x-axis: x from 0 to π/2 (use parametric range 0 to 1.57)
- y-axis: parameter a from 0.1 to 2
- z-axis: the integrand value

Use a color gradient from BLUE (low values) to RED (high values) to show intensity.
The surface should be smooth with proper lighting.

Key equations to display:
- f(x) = \frac{x \sin(2x)}{(1 + a\sin^2 x)(1 + b\cos^2 x)}
- Note: sin(2x) = 2sin(x)cos(x)

### Scene 2: Integration Path Animation
Animate a glowing line that traces the integration path from x=0 to x=π/2.
Show the "area under curve" filling in as the integration progresses.
Use GREEN for the integration path and semi-transparent TEAL for the filled region.

### Scene 3: The Closed Form Result
Display the elegant final result:
$$\frac{\pi}{a+b+ab} \log\left(\frac{\sqrt{1+a}(1+\sqrt{1+b})}{1+\sqrt{1+a}}\right)$$

Animate each component appearing:
1. First show π/(a+b+ab) in GOLD
2. Then the logarithm appears in PURPLE
3. The square root terms materialize in TEAL

### Scene 4: Interactive Parameter Explorer
Allow users to adjust parameters a and b with sliders.
Show real-time updates of:
- The integrand curve
- The numerical integral value
- The closed-form result

Both values should match (within numerical precision), demonstrating the identity.

## Visual Style
- Dark background (#1a1a2e)
- Glowing mathematical text
- Smooth camera orbiting
- Grid helpers for orientation
- LaTeX-style equation rendering
"""

def main():
    print("""
+===================================================================+
|  THREE.JS GENERATOR TEST - Trigonometric Integral                 |
+===================================================================+
    """)

    if not os.getenv("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY not set")
        return

    generator = ThreeJSCodeGenerator()

    print("Generating Three.js visualization...")
    print("This may take a minute...\n")

    output = generator.generate(
        verbose_prompt=VERBOSE_PROMPT,
        target_concept="Trigonometric Integral",
        include_controls=True,
        include_gui=True
    )

    # Save to output directory
    os.makedirs("output", exist_ok=True)
    output.save("output")

    print("\n" + "=" * 70)
    print("TEST COMPLETE!")
    print("=" * 70)
    print(f"\nOpen in browser: file://{os.path.abspath('output/Trigonometric_Integral_threejs.html')}")


if __name__ == "__main__":
    main()
