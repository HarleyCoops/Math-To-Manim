"""Simple demo of Claude Agent SDK query() function.

This demonstrates using the SDK in "query mode" which doesn't require
the Claude Code CLI - it works anywhere with just an API key.
"""

import asyncio
import json
import os
from dotenv import load_dotenv

from claude_agent_sdk import query, ClaudeAgentOptions

load_dotenv()


async def simple_prerequisite_query():
    """Use SDK query() function to discover prerequisites."""

    print("="*70)
    print("SIMPLE SDK DEMO - Using query() function")
    print("="*70)

    concept = "quantum field theory"
    print(f"\nDiscovering prerequisites for: {concept}")

    system_prompt = """You are an expert educator and curriculum designer.

Your task is to identify the ESSENTIAL prerequisite concepts someone must
understand BEFORE they can grasp a given concept.

Rules:
1. Only list concepts that are NECESSARY for understanding (not just helpful)
2. Order from most to least important
3. Assume high school education as baseline
4. Be specific - prefer "special relativity" over "relativity"
5. Limit to 3-5 prerequisites maximum

Return ONLY a JSON array of concept names, nothing else."""

    user_prompt = f'''To understand "{concept}", what are the 3-5 ESSENTIAL prerequisite concepts?

Return format: ["concept1", "concept2", "concept3"]'''

    # Configure options
    options = ClaudeAgentOptions()
    options.system_prompt = system_prompt

    print("\nSending query to Claude Agent SDK...")

    # Use query() - works without CLI
    response_text = ""
    async for message in query(prompt=user_prompt, options=options):
        # Extract text from response
        if hasattr(message, 'content'):
            for block in message.content:
                if hasattr(block, 'text'):
                    response_text += block.text

    print(f"\nReceived response ({len(response_text)} chars)")

    # Parse JSON
    try:
        if "```" in response_text:
            response_text = response_text.split("```")[1]
            if response_text.startswith("json"):
                response_text = response_text[4:]
            response_text = response_text.split("```")[0].strip()

        prerequisites = json.loads(response_text)

        print(f"\nPrerequisites for '{concept}':")
        for i, prereq in enumerate(prerequisites, 1):
            print(f"  {i}. {prereq}")

        return prerequisites

    except json.JSONDecodeError as e:
        print(f"\nFailed to parse JSON: {e}")
        print(f"Raw response: {response_text}")
        return []


async def check_if_foundation():
    """Use SDK to check if a concept is foundational."""

    print("\n" + "="*70)
    print("FOUNDATION CHECK - Multiple concepts")
    print("="*70)

    test_concepts = [
        "velocity",
        "Lorentz transformations",
        "energy",
        "quantum field theory",
        "addition"
    ]

    system_prompt = """You are an expert educator analyzing whether a concept is foundational.

A concept is foundational if a typical high school graduate would understand it
without further mathematical or scientific explanation.

Answer with ONLY "yes" or "no"."""

    results = []

    for concept in test_concepts:
        user_prompt = f'Is "{concept}" a foundational concept?'

        options = ClaudeAgentOptions()
        options.system_prompt = system_prompt

        # Get response
        response_text = ""
        async for message in query(prompt=user_prompt, options=options):
            if hasattr(message, 'content'):
                for block in message.content:
                    if hasattr(block, 'text'):
                        response_text += block.text

        is_foundation = response_text.strip().lower().startswith('yes')
        results.append((concept, is_foundation))

        status = "FOUNDATION" if is_foundation else "advanced"
        print(f"  {concept:30s} -> {status}")

    return results


async def validate_latex_with_claude():
    """Ask Claude to validate LaTeX using the SDK."""

    print("\n" + "="*70)
    print("LATEX VALIDATION - Using Claude's expertise")
    print("="*70)

    test_cases = [
        r"\frac{x}{y}",
        r"\int_0^\infty e^{-x^2} dx = \frac{\sqrt{\pi}}{2}",
        r"E = mc^2",
        r"\nabla \times \vec{E} = -\frac{\partial \vec{B}}{\partial t}",
    ]

    system_prompt = """You are a LaTeX expert. Check if the given LaTeX code is valid.

Return ONLY a JSON object with:
{
  "valid": true/false,
  "issues": ["list", "of", "problems"]
}"""

    for latex_code in test_cases:
        user_prompt = f'Is this LaTeX valid? {latex_code}'

        options = ClaudeAgentOptions()
        options.system_prompt = system_prompt

        response_text = ""
        async for message in query(prompt=user_prompt, options=options):
            if hasattr(message, 'content'):
                for block in message.content:
                    if hasattr(block, 'text'):
                        response_text += block.text

        print(f"\nLaTeX: {latex_code}")
        print(f"Claude says: {response_text.strip()[:100]}...")


async def main():
    """Run all demos."""

    print("""
======================================================================
                    Claude Agent SDK Demo
              Using query() function (no CLI required)
======================================================================

This demonstrates using the SDK with just an API key, without needing
the Claude Code CLI installed.

The query() function is perfect for:
- Simple one-shot questions
- Batch processing
- Scripts and automation
- Any environment with just Python + API key
======================================================================
    """)

    # Check API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("\n[ERROR] ANTHROPIC_API_KEY not set in environment")
        print("Please create a .env file with: ANTHROPIC_API_KEY=your_key_here")
        return

    print("\n[OK] API key found\n")

    try:
        # Demo 1: Prerequisite discovery
        await simple_prerequisite_query()

        # Demo 2: Foundation checking
        await check_if_foundation()

        # Demo 3: LaTeX validation
        await validate_latex_with_claude()

        print("\n" + "="*70)
        print("ALL DEMOS COMPLETED SUCCESSFULLY")
        print("="*70)
        print("\nKey Takeaways:")
        print("  * query() function works without Claude Code CLI")
        print("  * Perfect for automation and scripting")
        print("  * Async streaming for better performance")
        print("  * Can use system prompts and options")
        print("\nNext: Use these patterns in your agents!")
        print("="*70)

    except Exception as e:
        print(f"\n[ERROR] Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
