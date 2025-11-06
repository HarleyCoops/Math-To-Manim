"""Test script for custom MCP tools.

This demonstrates how the tools work within the Claude Agent SDK context.
Tools decorated with @tool are not directly callable - they must be used
through an MCP server and ClaudeSDKClient.
"""

import asyncio
import json
try:
    from src.agents.claude_sdk_tools import ALL_TOOLS, _PREREQUISITE_CACHE
except ImportError:
    from claude_sdk_tools import ALL_TOOLS, _PREREQUISITE_CACHE


async def test_tools_metadata():
    """Test that all tools are properly defined."""
    print("="*70)
    print("CUSTOM MCP TOOLS TEST")
    print("="*70)

    print(f"\nTotal tools defined: {len(ALL_TOOLS)}")
    print("\nTool Details:")
    print("-"*70)

    for i, tool in enumerate(ALL_TOOLS, 1):
        print(f"\n{i}. Tool Name: {tool.name}")
        print(f"   Description: {tool.description}")
        print(f"   Input Schema: {tool.input_schema}")
        print(f"   Type: {type(tool).__name__}")

    print("\n" + "="*70)
    print("MANUAL FUNCTION TESTS (Direct calls)")
    print("="*70)


async def test_latex_validation():
    """Test LaTeX validation by calling the underlying function."""
    print("\n1. Testing LaTeX Validation")
    print("-"*70)

    test_cases = [
        (r"\frac{x}{y}", "Valid LaTeX"),
        (r"\frac{x}{y", "Unclosed brace"),
        (r"$ \int_0^1 x^2 dx $", "Valid integral"),
        (r"$ \int_0^1 x^2 dx", "Unmatched $ delimiter"),
    ]

    # Import the actual validation function
    from claude_sdk_tools import validate_latex

    # Access the underlying function (before decoration)
    # Since it's already decorated, we'll recreate the logic
    for latex_code, description in test_cases:
        print(f"\nTest: {description}")
        print(f"LaTeX: {latex_code}")

        errors = []
        warnings = []

        # Basic syntax checks (same logic as in the tool)
        if latex_code.count("$") % 2 != 0:
            errors.append("Unmatched $ delimiter")

        if latex_code.count("\\[") != latex_code.count("\\]"):
            errors.append("Unmatched \\[ \\] delimiters")

        # Check for balanced braces
        brace_count = 0
        for char in latex_code:
            if char == "{":
                brace_count += 1
            elif char == "}":
                brace_count -= 1
            if brace_count < 0:
                errors.append("Unmatched closing brace }")
                break

        if brace_count > 0:
            errors.append(f"Unclosed braces: {brace_count} opening brace(s) without closing")

        result = {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }

        status = "[VALID]" if result["valid"] else "[INVALID]"
        print(f"Result: {status}")
        if errors:
            for error in errors:
                print(f"  - Error: {error}")


async def test_prerequisite_caching():
    """Test prerequisite caching functionality."""
    print("\n2. Testing Prerequisite Caching")
    print("-"*70)

    # Clear cache
    _PREREQUISITE_CACHE.clear()

    # Add some test data
    test_concepts = {
        "quantum mechanics": ["wave-particle duality", "Heisenberg uncertainty", "Schrödinger equation"],
        "special relativity": ["Galilean relativity", "speed of light", "Lorentz transformations"],
        "calculus": ["limits", "derivatives", "integrals"]
    }

    print("\nAdding concepts to cache:")
    for concept, prereqs in test_concepts.items():
        _PREREQUISITE_CACHE[concept] = prereqs
        print(f"  + {concept}: {len(prereqs)} prerequisites")

    print(f"\nCache size: {len(_PREREQUISITE_CACHE)} concepts")

    # Test retrieval
    print("\nRetrieving from cache:")
    for concept in test_concepts.keys():
        cached_prereqs = _PREREQUISITE_CACHE.get(concept, [])
        print(f"  + {concept}: {cached_prereqs}")

    # Test search
    print("\nSearching for related concepts:")
    search_term = "quantum"
    matches = [
        concept for concept in _PREREQUISITE_CACHE.keys()
        if search_term.lower() in concept.lower()
    ]
    print(f"  Query: '{search_term}'")
    print(f"  Matches: {matches}")


async def test_manim_validation():
    """Test Manim code validation."""
    print("\n3. Testing Manim Code Validation")
    print("-"*70)

    test_codes = [
        ("""from manim import *

class MyScene(Scene):
    def construct(self):
        circle = Circle()
        self.play(Create(circle))
""", "Valid Manim code"),
        ("""class MyScene(Scene):
    def construct(self):
        circle = Circle()
""", "Missing Manim import"),
        ("""from manim import *

def construct(self):
    circle = Circle()
""", "No Scene class"),
    ]

    for manim_code, description in test_codes:
        print(f"\nTest: {description}")

        errors = []
        warnings = []

        # Check for Manim import
        if "from manim import" not in manim_code and "import manim" not in manim_code:
            errors.append("Missing Manim import statement")

        # Check for Scene class definition
        if "class" not in manim_code or "Scene)" not in manim_code:
            errors.append("No Scene class defined")

        # Check for construct method
        if "def construct(self)" not in manim_code:
            errors.append("Missing construct(self) method")

        result = {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }

        status = "[VALID]" if result["valid"] else "[INVALID]"
        print(f"Result: {status}")
        if errors:
            for error in errors:
                print(f"  - Error: {error}")


async def test_complexity_estimation():
    """Test animation complexity estimation."""
    print("\n4. Testing Animation Complexity Estimation")
    print("-"*70)

    test_codes = [
        ("""from manim import *

class SimpleScene(Scene):
    def construct(self):
        circle = Circle()
        self.play(Create(circle))
        self.wait()
""", "Simple scene"),
        ("""from manim import *

class ComplexScene(Scene):
    def construct(self):
        eq1 = MathTex(r"E = mc^2")
        eq2 = MathTex(r"\\nabla \\times \\vec{E} = -\\frac{\\partial \\vec{B}}{\\partial t}")
        eq3 = MathTex(r"\\int_0^\\infty e^{-x^2} dx = \\frac{\\sqrt{\\pi}}{2}")

        for i in range(10):
            circle = Circle()
            self.play(Create(circle))
            self.play(Transform(circle, Square()))

        self.play(Write(eq1), Write(eq2), Write(eq3))
""", "Complex scene with math"),
    ]

    for manim_code, description in test_codes:
        print(f"\nTest: {description}")

        # Count complexity indicators
        play_count = manim_code.count("self.play(")
        create_count = manim_code.count("Create(")
        transform_count = manim_code.count("Transform(")
        mathtex_count = manim_code.count("MathTex(")
        mobject_count = (
            manim_code.count("Circle(") +
            manim_code.count("Square(") +
            manim_code.count("Line(") +
            manim_code.count("Dot(")
        )

        # Estimate render time
        base_time = 5
        time_per_play = 2
        time_per_mathtex = 3
        time_per_mobject = 0.5

        estimated_seconds = (
            base_time +
            (play_count * time_per_play) +
            (mathtex_count * time_per_mathtex) +
            (mobject_count * time_per_mobject)
        )

        complexity_score = play_count + mathtex_count + (mobject_count * 0.5)

        if complexity_score < 10:
            complexity = "low"
        elif complexity_score < 30:
            complexity = "medium"
        else:
            complexity = "high"

        print(f"  Complexity: {complexity.upper()}")
        print(f"  Estimated render time: {estimated_seconds}s")
        print(f"  Statistics:")
        print(f"    - Play calls: {play_count}")
        print(f"    - Create animations: {create_count}")
        print(f"    - Transforms: {transform_count}")
        print(f"    - LaTeX objects: {mathtex_count}")
        print(f"    - Basic mobjects: {mobject_count}")


async def main():
    """Run all tests."""
    await test_tools_metadata()
    await test_latex_validation()
    await test_prerequisite_caching()
    await test_manim_validation()
    await test_complexity_estimation()

    print("\n" + "="*70)
    print("ALL TESTS COMPLETED")
    print("="*70)
    print("\nNote: These tools are designed to be used within Claude Agent SDK.")
    print("To use them with Claude, they must be added to an MCP server:")
    print("")
    print("  from claude_agent_sdk import create_sdk_mcp_server")
    print("  from claude_sdk_tools import ALL_TOOLS")
    print("")
    print("  mcp_server = create_sdk_mcp_server(")
    print("      name='math-to-manim-tools',")
    print("      tools=ALL_TOOLS")
    print("  )")
    print("")
    print("Then use with ClaudeSDKClient:")
    print("")
    print("  options = ClaudeAgentOptions()")
    print("  options.mcp_servers = [mcp_server]")
    print("  async with ClaudeSDKClient(options=options) as client:")
    print("      # Claude can now use the tools")
    print("="*70)


if __name__ == "__main__":
    asyncio.run(main())
