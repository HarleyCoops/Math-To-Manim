"""
ThreeJS Code Generator Agent - Generates Three.js animation code from verbose prompts

Takes the same narrative/verbose prompt from NarrativeComposer and generates
interactive Three.js WebGL animations instead of Manim video output.

Uses Claude Sonnet 4.5 via the Anthropic Claude Agent SDK.
"""

import os
import json
import asyncio
from dataclasses import dataclass, field
from typing import Optional, List

from anthropic import Anthropic, NotFoundError
from dotenv import load_dotenv

# Import from same package
try:
    from src.agents.claude_agent_runtime import run_query_via_sdk
except ImportError:
    try:
        from claude_agent_runtime import run_query_via_sdk
    except ImportError:
        run_query_via_sdk = None  # type: ignore[assignment]

CLAUDE_MODEL = "claude-sonnet-4-5"
try:
    from src.agents.prerequisite_explorer_claude import CLAUDE_MODEL as _CLAUDE_MODEL
    CLAUDE_MODEL = _CLAUDE_MODEL
except ImportError:
    try:
        from prerequisite_explorer_claude import CLAUDE_MODEL as _CLAUDE_MODEL
        CLAUDE_MODEL = _CLAUDE_MODEL
    except ImportError:
        pass

load_dotenv()

CLI_CLIENT: Optional[Anthropic] = None


def _ensure_client() -> Anthropic:
    global CLI_CLIENT
    if CLI_CLIENT is None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise RuntimeError("ANTHROPIC_API_KEY environment variable not set.")
        CLI_CLIENT = Anthropic(api_key=api_key)
    return CLI_CLIENT


@dataclass
class ThreeJSOutput:
    """Output from the ThreeJS code generator"""
    html_code: str  # Complete HTML file with embedded JS
    js_code: str  # Standalone JS module
    concept: str
    scene_count: int = 0
    has_controls: bool = True
    has_animation: bool = True

    def to_dict(self) -> dict:
        return {
            'html_code': self.html_code,
            'js_code': self.js_code,
            'concept': self.concept,
            'scene_count': self.scene_count,
            'has_controls': self.has_controls,
            'has_animation': self.has_animation
        }

    def save(self, output_dir: str = "."):
        """Save ThreeJS output files"""
        os.makedirs(output_dir, exist_ok=True)
        safe_concept = "".join(c if c.isalnum() else "_" for c in self.concept)

        # Save HTML file
        html_path = os.path.join(output_dir, f"{safe_concept}_threejs.html")
        with open(html_path, 'w') as f:
            f.write(self.html_code)

        # Save standalone JS
        js_path = os.path.join(output_dir, f"{safe_concept}_threejs.js")
        with open(js_path, 'w') as f:
            f.write(self.js_code)

        print(f"✓ ThreeJS files saved:")
        print(f"  - {html_path}")
        print(f"  - {js_path}")

        return html_path, js_path


class ThreeJSCodeGenerator:
    """
    Agent that generates Three.js animation code from verbose prompts.

    Takes the same narrative prompt used for Manim generation and produces
    interactive WebGL visualizations using Three.js.

    Key differences from Manim output:
    - Interactive (zoom, rotate, pan)
    - Runs in browser
    - Real-time rendering
    - Can include UI controls

    Powered by Claude Sonnet 4.5.
    """

    THREEJS_SYSTEM_PROMPT = """You are an expert Three.js developer who creates stunning
mathematical and scientific visualizations for the web.

Generate complete, working Three.js code that implements interactive 3D animations.

Requirements:
- Use Three.js r150+ (modern ES6 imports via CDN or importmap)
- Include OrbitControls for camera interaction
- Use proper lighting (ambient + directional)
- Implement smooth animations with requestAnimationFrame
- Add responsive canvas sizing
- Include mathematical accuracy for all visualizations
- Use shaders or custom geometry where appropriate for complex math

For mathematical content:
- Use THREE.BufferGeometry for parametric surfaces
- Implement proper coordinate systems
- Add axis helpers and labels where appropriate
- Use color gradients to represent values
- Include LaTeX labels using CSS2DRenderer or sprite text

Animation principles:
- Smooth easing functions
- Clear visual progression
- Interactive timeline controls where helpful
- Pause/play functionality

Return ONLY the code, no explanations. Generate two outputs:
1. Complete HTML file with embedded JavaScript
2. Standalone ES6 JavaScript module"""

    def __init__(self, model: str = CLAUDE_MODEL):
        self.model = model

    async def generate_async(
        self,
        verbose_prompt: str,
        target_concept: str,
        include_controls: bool = True,
        include_gui: bool = True
    ) -> ThreeJSOutput:
        """
        Generate Three.js code from a verbose prompt.

        Args:
            verbose_prompt: The narrative prompt from NarrativeComposer
            target_concept: The main concept being visualized
            include_controls: Include OrbitControls for camera
            include_gui: Include dat.GUI for parameter tweaking

        Returns:
            ThreeJSOutput with HTML and JS code
        """
        print(f"\n{'='*70}")
        print("THREEJS CODE GENERATION")
        print(f"{'='*70}")
        print(f"Generating Three.js visualization for: {target_concept}")

        # Adapt the Manim-focused prompt for Three.js
        adapted_prompt = self._adapt_prompt_for_threejs(
            verbose_prompt,
            include_controls,
            include_gui
        )

        # Generate the HTML version
        print("\n  Generating HTML with embedded Three.js...")
        html_code = await self._generate_html_async(adapted_prompt, target_concept)

        # Generate the standalone JS module
        print("  Generating standalone JS module...")
        js_code = await self._generate_js_module_async(adapted_prompt, target_concept)

        # Count scenes from the prompt
        scene_count = verbose_prompt.count("### Scene")

        output = ThreeJSOutput(
            html_code=html_code,
            js_code=js_code,
            concept=target_concept,
            scene_count=scene_count,
            has_controls=include_controls,
            has_animation=True
        )

        print(f"\n✓ Three.js code generated:")
        print(f"  HTML: {len(html_code)} characters")
        print(f"  JS:   {len(js_code)} characters")

        return output

    def generate(
        self,
        verbose_prompt: str,
        target_concept: str,
        include_controls: bool = True,
        include_gui: bool = True
    ) -> ThreeJSOutput:
        """Synchronous wrapper for generate_async"""
        return asyncio.run(self.generate_async(
            verbose_prompt, target_concept, include_controls, include_gui
        ))

    def _adapt_prompt_for_threejs(
        self,
        manim_prompt: str,
        include_controls: bool,
        include_gui: bool
    ) -> str:
        """Adapt a Manim-focused prompt for Three.js generation"""

        # Add Three.js specific instructions
        threejs_additions = f"""
## Three.js Specific Requirements

Convert the above Manim animation specification to an interactive Three.js visualization.

**Technical Requirements:**
- Use Three.js via CDN: https://unpkg.com/three@0.150.0/build/three.module.js
- Import OrbitControls: https://unpkg.com/three@0.150.0/examples/jsm/controls/OrbitControls.js
{"- Include dat.GUI for parameter controls: https://unpkg.com/dat.gui@0.7.9/build/dat.gui.module.js" if include_gui else ""}
- Responsive canvas that fills the viewport
- Anti-aliased renderer with proper pixel ratio

**Animation Mapping:**
- Manim "FadeIn" → Three.js opacity animation (0 → 1)
- Manim "Transform" → Three.js morph targets or geometry lerp
- Manim "Write" → Progressive line drawing or text reveal
- Manim "Create" → Scale animation (0 → 1)
- Manim "Indicate" → Pulse/glow effect
- Manim "Rotate" → Quaternion/euler rotation tween
- Manim camera movements → OrbitControls + GSAP/tween.js

**Mathematical Rendering:**
- Use BufferGeometry for parametric surfaces
- Use Line2/LineMaterial for thick mathematical curves
- Use TextGeometry or CSS2DRenderer for labels
- Use custom shaders for color mapping

**Color Mapping (Manim → Three.js hex):**
- BLUE → 0x3b82f6
- RED → 0xef4444
- GREEN → 0x22c55e
- YELLOW → 0xeab308
- PURPLE → 0xa855f7
- ORANGE → 0xf97316
- TEAL → 0x14b8a6
- GOLD → 0xfbbf24
- WHITE → 0xffffff
- GRAY → 0x6b7280

{"**Interactive Controls:**" if include_controls else ""}
{"- OrbitControls: rotate (left-click), zoom (scroll), pan (right-click)" if include_controls else ""}
{"- Play/pause button for animation timeline" if include_controls else ""}
{"- Slider to scrub through animation" if include_controls else ""}

{"**GUI Parameters:**" if include_gui else ""}
{"- Expose key mathematical parameters (e.g., coefficients, frequencies)" if include_gui else ""}
{"- Animation speed control" if include_gui else ""}
{"- Toggle visibility of elements" if include_gui else ""}
"""

        return manim_prompt + threejs_additions

    async def _generate_html_async(self, prompt: str, concept: str) -> str:
        """Generate complete HTML file with embedded Three.js"""

        user_prompt = f"""Generate a complete, self-contained HTML file for this visualization:

{prompt}

The HTML should:
1. Include all necessary CDN imports (Three.js, OrbitControls, etc.)
2. Have a dark background (#1a1a2e or similar)
3. Include a title overlay showing: "{concept}"
4. Be fully responsive
5. Include animation controls (play/pause/restart)
6. Work when opened directly in a browser (file://)

Return ONLY the complete HTML code starting with <!DOCTYPE html>."""

        try:
            response = _ensure_client().messages.create(
                model=self.model,
                max_tokens=12000,
                temperature=0.3,
                system=self.THREEJS_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_prompt}],
            )
            content = response.content[0].text
        except NotFoundError:
            content = run_query_via_sdk(
                user_prompt,
                system_prompt=self.THREEJS_SYSTEM_PROMPT,
                temperature=0.3,
                max_tokens=12000,
            )

        # Extract HTML from markdown if needed
        if "```html" in content:
            code = content.split("```html")[1].split("```")[0].strip()
        elif "```" in content:
            code = content.split("```")[1].split("```")[0].strip()
        else:
            code = content.strip()

        return code

    async def _generate_js_module_async(self, prompt: str, concept: str) -> str:
        """Generate standalone ES6 JavaScript module"""

        user_prompt = f"""Generate a standalone ES6 JavaScript module for this visualization:

{prompt}

The module should:
1. Export a main class named after the concept (e.g., `export class {concept.replace(' ', '')}Visualization`)
2. Accept a container element in the constructor
3. Have init(), animate(), dispose() methods
4. Be importable and reusable
5. Not include HTML - just the JS logic
6. Use ES6 imports for Three.js dependencies

Example structure:
```javascript
import * as THREE from 'three';
import {{ OrbitControls }} from 'three/examples/jsm/controls/OrbitControls.js';

export class ConceptVisualization {{
    constructor(container) {{ ... }}
    init() {{ ... }}
    animate() {{ ... }}
    dispose() {{ ... }}
}}
```

Return ONLY the JavaScript code."""

        try:
            response = _ensure_client().messages.create(
                model=self.model,
                max_tokens=10000,
                temperature=0.3,
                system=self.THREEJS_SYSTEM_PROMPT,
                messages=[{"role": "user", "content": user_prompt}],
            )
            content = response.content[0].text
        except NotFoundError:
            content = run_query_via_sdk(
                user_prompt,
                system_prompt=self.THREEJS_SYSTEM_PROMPT,
                temperature=0.3,
                max_tokens=10000,
            )

        # Extract JS from markdown if needed
        if "```javascript" in content:
            code = content.split("```javascript")[1].split("```")[0].strip()
        elif "```js" in content:
            code = content.split("```js")[1].split("```")[0].strip()
        elif "```" in content:
            code = content.split("```")[1].split("```")[0].strip()
        else:
            code = content.strip()

        return code


def demo():
    """Demo the ThreeJS code generator with a sample prompt"""

    print("""
╔═══════════════════════════════════════════════════════════════════╗
║     THREEJS CODE GENERATOR - Claude Sonnet 4.5                    ║
║                                                                    ║
║  Generates interactive Three.js visualizations from prompts       ║
║  Same input as Manim, but outputs web-based 3D animations         ║
╚═══════════════════════════════════════════════════════════════════╝
    """)

    # Sample verbose prompt (simplified for demo)
    sample_prompt = """# Manim Animation: Pythagorean Theorem

## Overview
This animation builds the Pythagorean Theorem from first principles.

### Scene 1: Right Triangle
Begin by displaying a right triangle with sides labeled a, b, and c.
The triangle should be centered, with the right angle at the bottom left.
Use BLUE for side a (vertical), GREEN for side b (horizontal), and RED for
the hypotenuse c. Fade in the triangle, then write the side labels.

### Scene 2: Square Construction
Transform the scene to show squares constructed on each side.
The square on side a (BLUE) has area a².
The square on side b (GREEN) has area b².
The square on side c (RED) has area c².
Animate the squares growing from each side of the triangle.

### Scene 3: The Equation
Display the equation: a² + b² = c²
Show visually how the areas of the smaller squares equal the area of the large square.
Use animation to "pour" the smaller squares into the larger one.

### Scene 4: Interactive Proof
Allow the user to drag vertices of the triangle and see the equation update.
The relationship a² + b² = c² should always hold for any right triangle.
"""

    generator = ThreeJSCodeGenerator()

    output = generator.generate(
        verbose_prompt=sample_prompt,
        target_concept="Pythagorean Theorem",
        include_controls=True,
        include_gui=True
    )

    # Save output
    output.save("output")

    print("\n" + "=" * 70)
    print("HTML Preview (first 500 chars):")
    print("=" * 70)
    print(output.html_code[:500])
    print("\n...")


if __name__ == "__main__":
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("[FAIL] Error: ANTHROPIC_API_KEY environment variable not set.")
        exit(1)

    demo()
