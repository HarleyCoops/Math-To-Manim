#!/usr/bin/env python3
"""
Generate Manim animation code from a knowledge tree JSON file.

Uses Kimi K2 to:
1. Generate a narrative/verbose prompt from the knowledge tree
2. Generate Manim code from the prompt
"""

import os
import sys
import asyncio
import json
from typing import Optional
from pathlib import Path
from dotenv import load_dotenv

# Add paths for Kimi K2 imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "KimiK2Thinking"))

load_dotenv()

from kimi_client import KimiClient
from agents.prerequisite_explorer_kimi import KnowledgeNode
from config import KIMI_K2_MODEL


def load_knowledge_tree(json_path: Path) -> KnowledgeNode:
    """Load knowledge tree from JSON file."""
    with open(json_path, 'r', encoding='utf-8') as f:
        tree_dict = json.load(f)
    
    def dict_to_node(d: dict) -> KnowledgeNode:
        """Recursively convert dict to KnowledgeNode."""
        return KnowledgeNode(
            concept=d['concept'],
            depth=d['depth'],
            is_foundation=d['is_foundation'],
            prerequisites=[dict_to_node(p) for p in d.get('prerequisites', [])],
            equations=d.get('equations'),
            definitions=d.get('definitions'),
            visual_spec=d.get('visual_spec'),
            narrative=d.get('narrative')
        )
    
    return dict_to_node(tree_dict)


def walk_tree_for_concepts(node: KnowledgeNode, visited: set = None) -> list:
    """Walk tree and collect all concepts in order (foundations first)."""
    if visited is None:
        visited = set()
    
    concepts = []
    
    # First, add all prerequisites (foundations first)
    foundations = [p for p in node.prerequisites if p.is_foundation]
    non_foundations = [p for p in node.prerequisites if not p.is_foundation]
    
    for prereq in foundations + non_foundations:
        if prereq.concept not in visited:
            visited.add(prereq.concept)
            concepts.extend(walk_tree_for_concepts(prereq, visited))
    
    # Then add this node
    if node.concept not in visited:
        visited.add(node.concept)
        concepts.append(node.concept)
    
    return concepts


async def generate_narrative_from_tree(tree: KnowledgeNode, kimi_client: KimiClient, max_length: int = 4000) -> str:
    """Generate a verbose narrative prompt from the knowledge tree using Kimi K2."""
    
    # Collect all concepts in order
    concepts = walk_tree_for_concepts(tree)
    
    # Build tree structure description
    tree_description = f"""
Target Concept: {tree.concept}
Depth: {tree.depth}
Is Foundation: {tree.is_foundation}

Prerequisites:
"""
    for prereq in tree.prerequisites:
        tree_description += f"  - {prereq.concept} (depth {prereq.depth}, foundation: {prereq.is_foundation})\n"
        for sub_prereq in prereq.prerequisites:
            tree_description += f"    - {sub_prereq.concept} (depth {sub_prereq.depth}, foundation: {sub_prereq.is_foundation})\n"
    
    prompt = f"""You are creating a detailed narrative prompt for a Manim animation that explains the concept: "{tree.concept}"

Knowledge Tree Structure:
{tree_description}

Concept Order (from foundations to target):
{chr(10).join(f"{i+1}. {c}" for i, c in enumerate(concepts))}

Create a comprehensive, detailed narrative prompt (2000+ words) that:
1. Explains each concept in order, building from foundations to the target concept
2. Includes all relevant mathematical equations in LaTeX format
3. Describes visual elements, colors, animations, and transitions
4. Provides specific Manim instructions for each scene
5. Ensures smooth progression from simple to complex concepts
6. Includes timing information for each scene

The narrative should be suitable for generating Manim Community Edition code.

Return the complete narrative prompt, ready to be used for Manim code generation."""

    print("\nGenerating narrative prompt with Kimi K2...")
    
    # Use larger model for narrative generation if available
    model = os.getenv("KIMI_MODEL", KIMI_K2_MODEL)
    if "8k" in model:
        model = model.replace("8k", "32k")
        from kimi_client import KimiClient
        kimi_client = KimiClient(model=model)
    
    response = kimi_client.chat_completion(
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_length,
        temperature=0.7
    )
    
    narrative = kimi_client.get_text_content(response)
    return narrative


async def generate_manim_code(narrative: str, kimi_client: KimiClient) -> str:
    """Generate Manim code from the narrative prompt using Kimi K2."""
    
    # Truncate narrative if too long (keep first 6000 chars to leave room for system prompt and response)
    max_narrative_length = 6000
    if len(narrative) > max_narrative_length:
        print(f"  Warning: Narrative too long ({len(narrative)} chars), truncating to {max_narrative_length}")
        narrative = narrative[:max_narrative_length] + "\n\n[... narrative truncated for length ...]"
    
    system_prompt = """You are an expert Manim Community Edition animator.

Generate complete, working Python code that implements the animation described in the prompt.

Requirements:
- Use Manim Community Edition (manim, not manimlib)
- Import: from manim import *
- Create a Scene class with a construct() method
- Use proper LaTeX with raw strings: r"$\\frac{a}{b}$"
- Include all specified visual elements, colors, animations
- Follow the scene sequence exactly
- Ensure code is runnable with: manim -pql file.py SceneName
- Use appropriate colors, positioning, and timing
- Include wait() calls for pacing

Return ONLY the Python code, no explanations or markdown formatting."""

    user_prompt = f"""Generate Manim Community Edition code for this animation:

{narrative}

Return complete Python code that can be run directly with manim."""

    print("\nGenerating Manim code with Kimi K2...")
    
    # Use a larger model if available
    model = os.getenv("KIMI_MODEL", KIMI_K2_MODEL)
    
    # Try 32k model if available for longer contexts
    if "8k" in model:
        model = model.replace("8k", "32k")
        print(f"  Using model: {model} (for longer context)")
        # Create new client with larger model
        from kimi_client import KimiClient
        kimi_client = KimiClient(model=model)
    
    response = kimi_client.chat_completion(
        messages=[{"role": "user", "content": user_prompt}],
        system=system_prompt,
        max_tokens=8000,
        temperature=0.3
    )
    
    code = kimi_client.get_text_content(response)
    
    # Extract code from markdown if needed
    if "```python" in code:
        code = code.split("```python")[1].split("```")[0].strip()
    elif "```" in code:
        code = code.split("```")[1].split("```")[0].strip()
    
    return code


async def main():
    """Main async function"""
    
    # Check for JSON file argument
    if len(sys.argv) > 1:
        json_path = Path(sys.argv[1])
    else:
        # Default to the most recent tree
        json_path = Path("output/Minkowski_Spacetime_kimi_tree.json")
    
    if not json_path.exists():
        print(f"ERROR: Knowledge tree file not found: {json_path}")
        print("\nUsage: python generate_manim_from_tree.py [path_to_tree.json]")
        sys.exit(1)
    
    # Check API key
    if not os.getenv("MOONSHOT_API_KEY"):
        print("[ERROR] MOONSHOT_API_KEY not set!")
        print("\nPlease set it in your .env file:")
        print("  MOONSHOT_API_KEY=your_key_here")
        sys.exit(1)
    
    print("=" * 70)
    print("KNOWLEDGE TREE TO MANIM CODE - KIMI K2")
    print("=" * 70)
    print(f"\nLoading knowledge tree: {json_path}")
    
    # Step 1: Load knowledge tree
    try:
        tree = load_knowledge_tree(json_path)
        print(f"✓ Loaded tree for concept: {tree.concept}")
        print(f"  Depth: {tree.depth}")
        print(f"  Prerequisites: {len(tree.prerequisites)}")
    except Exception as e:
        print(f"\nERROR: Failed to load knowledge tree: {e}")
        sys.exit(1)
    
    # Prepare Kimi client for downstream steps
    try:
        kimi_client = KimiClient()
    except Exception as e:
        print(f"\nERROR: Failed to initialize Kimi client: {e}")
        sys.exit(1)

    # Step 2: Generate or reuse narrative
    print("\n" + "=" * 70)
    print("STEP 1: PREPARING NARRATIVE PROMPT (KIMI K2)")
    print("=" * 70)

    narrative: Optional[str] = None
    if tree.narrative and tree.narrative.strip():
        narrative = tree.narrative
        print(f"\n✓ Using narrative stored on the tree: {len(narrative)} characters")
        print(f"Preview:\n{narrative[:500]}...")
    else:
        print("\nNo stored narrative found. Generating a fresh narrative with Kimi K2...")
        try:
            narrative = await generate_narrative_from_tree(tree, kimi_client)
            print(f"\n✓ Narrative generated: {len(narrative)} characters")
            print(f"Preview:\n{narrative[:500]}...")
        except Exception as e:
            print(f"\nERROR: Failed to generate narrative: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

    # Ensure the tree carries the narrative for downstream use
    tree.narrative = narrative
    
    # Step 3: Generate Manim code
    print("\n" + "=" * 70)
    print("STEP 2: GENERATING MANIM CODE (KIMI K2)")
    print("=" * 70)
    
    try:
        manim_code = await generate_manim_code(narrative, kimi_client)
        
        print(f"\n✓ Manim code generated: {len(manim_code)} characters")
        print(f"  Lines: {len(manim_code.splitlines())}")
        
    except Exception as e:
        print(f"\nERROR: Failed to generate Manim code: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # Step 4: Save outputs
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    safe_name = "".join(c if c.isalnum() else "_" for c in tree.concept[:50])
    
    # Save narrative
    narrative_file = output_dir / f"{safe_name}_narrative.txt"
    with open(narrative_file, 'w', encoding='utf-8') as f:
        f.write(narrative)
    print(f"\nSaved narrative to: {narrative_file}")
    
    # Save Manim code
    code_file = output_dir / f"{safe_name}_animation.py"
    with open(code_file, 'w', encoding='utf-8') as f:
        f.write(manim_code)
    print(f"Saved Manim code to: {code_file}")
    
    print("\n" + "=" * 70)
    print("COMPLETE!")
    print("=" * 70)
    print(f"\nTo render the animation:")
    print(f"  manim -pql {code_file} SceneName")
    print(f"\nOr check the code first:")
    print(f"  python {code_file}")


if __name__ == "__main__":
    asyncio.run(main())

