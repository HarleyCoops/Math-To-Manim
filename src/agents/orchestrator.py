"""
Reverse Knowledge Tree Orchestrator - Main coordinator for the agent pipeline

Coordinates all agents in the proper sequence:
1. ConceptAnalyzer - Parse user input
2. PrerequisiteExplorer - Build knowledge tree
3. MathematicalEnricher - Add equations and definitions
4. VisualDesigner - Design visual specifications
5. NarrativeComposer - Generate verbose prompt
6. CodeGenerator - Convert to Manim code and/or Three.js code

Supports dual output modes:
- Manim: Traditional video rendering (MP4)
- Three.js: Interactive web-based 3D visualization (HTML/JS)

Uses Claude Sonnet 4.5 via the Anthropic Claude Agent SDK.
"""

import os
import json
import asyncio
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime

from anthropic import Anthropic, NotFoundError
from dotenv import load_dotenv

# Import all agents
try:
    from src.agents.prerequisite_explorer_claude import (
        ConceptAnalyzer,
        PrerequisiteExplorer,
        KnowledgeNode,
        CLAUDE_MODEL
    )
    from src.agents.mathematical_enricher import MathematicalEnricher
    from src.agents.visual_designer import VisualDesigner
    from src.agents.narrative_composer import NarrativeComposer, Narrative
    from src.agents.threejs_code_generator import ThreeJSCodeGenerator, ThreeJSOutput
    from src.agents.claude_agent_runtime import run_query_via_sdk
except ImportError:
    try:
        from prerequisite_explorer_claude import (
            ConceptAnalyzer,
            PrerequisiteExplorer,
            KnowledgeNode,
            CLAUDE_MODEL
        )
        from mathematical_enricher import MathematicalEnricher
        from visual_designer import VisualDesigner
        from narrative_composer import NarrativeComposer, Narrative
        from threejs_code_generator import ThreeJSCodeGenerator, ThreeJSOutput
        from claude_agent_runtime import run_query_via_sdk
    except ImportError:
        raise ImportError("Could not import required agents")

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
class AnimationResult:
    """Complete result from the agent pipeline"""
    user_input: str
    target_concept: str
    knowledge_tree: dict
    verbose_prompt: str
    manim_code: Optional[str] = None
    threejs_html: Optional[str] = None
    threejs_js: Optional[str] = None
    concept_order: list = field(default_factory=list)
    total_duration: int = 0
    scene_count: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'user_input': self.user_input,
            'target_concept': self.target_concept,
            'knowledge_tree': self.knowledge_tree,
            'verbose_prompt': self.verbose_prompt,
            'manim_code': self.manim_code,
            'threejs_html': self.threejs_html,
            'threejs_js': self.threejs_js,
            'concept_order': self.concept_order,
            'total_duration': self.total_duration,
            'scene_count': self.scene_count,
            'timestamp': self.timestamp
        }

    def save(self, output_dir: str = "."):
        """Save all results to files"""
        import os
        os.makedirs(output_dir, exist_ok=True)

        # Sanitize filename
        safe_concept = "".join(c if c.isalnum() else "_" for c in self.target_concept)
        base_path = os.path.join(output_dir, safe_concept)

        # Save verbose prompt
        with open(f"{base_path}_prompt.txt", 'w') as f:
            f.write(self.verbose_prompt)

        # Save knowledge tree
        with open(f"{base_path}_tree.json", 'w') as f:
            json.dump(self.knowledge_tree, f, indent=2)

        # Save Manim code if generated
        if self.manim_code:
            with open(f"{base_path}_animation.py", 'w') as f:
                f.write(self.manim_code)

        # Save Three.js code if generated
        if self.threejs_html:
            with open(f"{base_path}_threejs.html", 'w') as f:
                f.write(self.threejs_html)
        if self.threejs_js:
            with open(f"{base_path}_threejs.js", 'w') as f:
                f.write(self.threejs_js)

        # Save complete result metadata
        with open(f"{base_path}_result.json", 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

        print(f"\n✓ Results saved to {output_dir}/")
        print(f"  - {safe_concept}_prompt.txt")
        print(f"  - {safe_concept}_tree.json")
        if self.manim_code:
            print(f"  - {safe_concept}_animation.py")
        if self.threejs_html:
            print(f"  - {safe_concept}_threejs.html")
        if self.threejs_js:
            print(f"  - {safe_concept}_threejs.js")
        print(f"  - {safe_concept}_result.json")


class ReverseKnowledgeTreeOrchestrator:
    """
    Main orchestrator for the Reverse Knowledge Tree pipeline.

    Coordinates all agents to transform a simple user prompt into
    a complete Manim animation via recursive prerequisite discovery.

    This is the NO-TRAINING-DATA approach: pure reasoning to build
    pedagogically sound animations.
    """

    def __init__(
        self,
        model: str = CLAUDE_MODEL,
        max_tree_depth: int = 4,
        enable_code_generation: bool = True,
        enable_threejs_generation: bool = False,
        enable_atlas: bool = False,
        atlas_dataset: str = "math-to-manim-concepts"
    ):
        """
        Initialize the orchestrator with all agents.

        Args:
            model: Claude model to use
            max_tree_depth: Maximum depth for prerequisite tree
            enable_code_generation: Whether to generate Manim code
            enable_threejs_generation: Whether to generate Three.js code
            enable_atlas: Whether to use Nomic Atlas for caching
            atlas_dataset: Atlas dataset name if enabled
        """
        self.model = model
        self.enable_code_generation = enable_code_generation
        self.enable_threejs_generation = enable_threejs_generation

        # Initialize all agents
        self.concept_analyzer = ConceptAnalyzer(model=model)
        self.prerequisite_explorer = PrerequisiteExplorer(
            model=model,
            max_depth=max_tree_depth
        )
        self.mathematical_enricher = MathematicalEnricher(model=model)
        self.visual_designer = VisualDesigner(model=model)
        self.narrative_composer = NarrativeComposer(model=model)

        # Initialize Three.js generator if enabled
        if enable_threejs_generation:
            self.threejs_generator = ThreeJSCodeGenerator(model=model)
        else:
            self.threejs_generator = None

        # Enable Atlas integration if requested
        if enable_atlas:
            self.prerequisite_explorer.enable_atlas_integration(atlas_dataset)

    def process(self, user_input: str, output_dir: str = ".") -> AnimationResult:
        """
        Process a user input through the complete agent pipeline.

        Args:
            user_input: The user's natural language prompt
            output_dir: Directory to save results

        Returns:
            AnimationResult with all generated content
        """
        return asyncio.run(self.process_async(user_input, output_dir))

    async def process_async(self, user_input: str, output_dir: str = ".") -> AnimationResult:
        """Async version of process"""

        print("""
╔═══════════════════════════════════════════════════════════════════╗
║  REVERSE KNOWLEDGE TREE PIPELINE - Claude Sonnet 4.5             ║
║                                                                   ║
║  Transforming your prompt into a Manim animation...              ║
║  Using recursive prerequisite discovery (no training data!)      ║
╚═══════════════════════════════════════════════════════════════════╝
""")
        print(f"\n📝 USER INPUT: \"{user_input}\"\n")

        # ===================================================================
        # STEP 1: Concept Analysis
        # ===================================================================
        print("=" * 70)
        print("STEP 1: CONCEPT ANALYSIS")
        print("=" * 70)
        analysis = self.concept_analyzer.analyze(user_input)
        print(f"\n✓ Core concept: {analysis['core_concept']}")
        print(f"  Domain: {analysis['domain']}")
        print(f"  Level: {analysis['level']}")
        print(f"  Goal: {analysis['goal']}")

        # ===================================================================
        # STEP 2: Prerequisite Exploration (The Key Innovation!)
        # ===================================================================
        print("\n" + "=" * 70)
        print("STEP 2: PREREQUISITE EXPLORATION (Reverse Knowledge Tree)")
        print("=" * 70)
        print(f"\nRecursively discovering prerequisites for: {analysis['core_concept']}")
        print("Asking: 'What must I understand BEFORE this concept?'\n")

        knowledge_tree = await self.prerequisite_explorer.explore_async(
            analysis['core_concept']
        )

        print("\n✓ Knowledge tree built:")
        knowledge_tree.print_tree()

        # ===================================================================
        # STEP 3: Mathematical Enrichment
        # ===================================================================
        print("\n" + "=" * 70)
        print("STEP 3: MATHEMATICAL ENRICHMENT")
        print("=" * 70)
        print("\nAdding LaTeX equations, definitions, and examples to each node...\n")

        enriched_tree = await self.mathematical_enricher.enrich_node_async(knowledge_tree)

        print("\n✓ Mathematical content added to all nodes")

        # ===================================================================
        # STEP 4: Visual Design
        # ===================================================================
        print("\n" + "=" * 70)
        print("STEP 4: VISUAL DESIGN")
        print("=" * 70)
        print("\nDesigning visual specifications (colors, animations, layout)...\n")

        designed_tree = await self.visual_designer.design_node_async(enriched_tree)

        print("\n✓ Visual specifications added to all nodes")

        # ===================================================================
        # STEP 5: Narrative Composition
        # ===================================================================
        print("\n" + "=" * 70)
        print("STEP 5: NARRATIVE COMPOSITION")
        print("=" * 70)
        print("\nComposing verbose prompt from knowledge tree...")
        print("Walking from foundation concepts → target concept\n")

        narrative = await self.narrative_composer.compose_async(designed_tree)

        print(f"\n✓ Verbose prompt generated:")
        print(f"  Length: {len(narrative.verbose_prompt)} characters")
        print(f"  Words: ~{len(narrative.verbose_prompt.split())}")
        print(f"  Scenes: {narrative.scene_count}")
        print(f"  Duration: {narrative.total_duration} seconds")

        # ===================================================================
        # STEP 6: Code Generation (Optional - Manim and/or Three.js)
        # ===================================================================
        manim_code = None
        threejs_html = None
        threejs_js = None

        if self.enable_code_generation:
            print("\n" + "=" * 70)
            print("STEP 6a: MANIM CODE GENERATION")
            print("=" * 70)
            print("\nGenerating Python code from verbose prompt...\n")

            manim_code = await self._generate_manim_code_async(narrative.verbose_prompt)

            print(f"\n✓ Manim code generated:")
            print(f"  Length: {len(manim_code)} characters")
            print(f"  Lines: {len(manim_code.splitlines())}")

        if self.enable_threejs_generation and self.threejs_generator:
            print("\n" + "=" * 70)
            print("STEP 6b: THREE.JS CODE GENERATION")
            print("=" * 70)
            print("\nGenerating interactive Three.js visualization...\n")

            threejs_output = await self.threejs_generator.generate_async(
                verbose_prompt=narrative.verbose_prompt,
                target_concept=analysis['core_concept'],
                include_controls=True,
                include_gui=True
            )

            threejs_html = threejs_output.html_code
            threejs_js = threejs_output.js_code

            print(f"\n✓ Three.js code generated:")
            print(f"  HTML: {len(threejs_html)} characters")
            print(f"  JS:   {len(threejs_js)} characters")

        # ===================================================================
        # Create result
        # ===================================================================
        result = AnimationResult(
            user_input=user_input,
            target_concept=analysis['core_concept'],
            knowledge_tree=designed_tree.to_dict(),
            verbose_prompt=narrative.verbose_prompt,
            manim_code=manim_code,
            threejs_html=threejs_html,
            threejs_js=threejs_js,
            concept_order=narrative.concept_order,
            total_duration=narrative.total_duration,
            scene_count=narrative.scene_count
        )

        # Save results
        result.save(output_dir)

        print("\n" + "=" * 70)
        print("✅ PIPELINE COMPLETE!")
        print("=" * 70)

        return result

    async def _generate_manim_code_async(self, verbose_prompt: str) -> str:
        """Generate Manim Python code from the verbose prompt"""

        system_prompt = """You are an expert Manim Community Edition animator.

Generate complete, working Python code that implements the animation
described in the prompt.

Requirements:
- Use Manim Community Edition (manim, not manimlib)
- Import: from manim import *
- Create a Scene class
- Use proper LaTeX with raw strings: r"$\\\\frac{a}{b}$"
- Include all specified visual elements, colors, animations
- Follow the scene sequence exactly
- Ensure code is runnable with: manim -pql file.py SceneName

Return ONLY the Python code, no explanations."""

        user_prompt = f"""Generate Manim Community Edition code for this animation:

{verbose_prompt}

Return complete Python code that can be run directly."""

        try:
            response = _ensure_client().messages.create(
                model=self.model,
                max_tokens=8000,
                temperature=0.3,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
            content = response.content[0].text
        except NotFoundError:
            content = run_query_via_sdk(
                user_prompt,
                system_prompt=system_prompt,
                temperature=0.3,
                max_tokens=8000,
            )

        # Extract code from markdown if needed
        if "```python" in content:
            code = content.split("```python")[1].split("```")[0].strip()
        elif "```" in content:
            code = content.split("```")[1].split("```")[0].strip()
        else:
            code = content.strip()

        return code


def demo():
    """Demo the complete orchestrator pipeline"""

    print("""
╔═══════════════════════════════════════════════════════════════════╗
║     COMPLETE AGENT PIPELINE DEMO                                 ║
║                                                                   ║
║  This demonstrates the full Reverse Knowledge Tree approach:     ║
║                                                                   ║
║  Simple prompt → Knowledge tree → Verbose prompt → Code          ║
║                                                                   ║
║  Output options:                                                 ║
║    - Manim: Traditional video rendering (MP4)                    ║
║    - Three.js: Interactive web-based 3D visualization            ║
║                                                                   ║
║  NO TRAINING DATA - Just recursive reasoning!                    ║
╚═══════════════════════════════════════════════════════════════════╝
    """)

    # Ask about output format
    print("Output format options:")
    print("  1. Manim only (traditional video)")
    print("  2. Three.js only (interactive web)")
    print("  3. Both Manim and Three.js")
    output_choice = input("\nChoose output format (1-3) [default: 3]: ").strip() or "3"

    enable_manim = output_choice in ["1", "3"]
    enable_threejs = output_choice in ["2", "3"]

    # Create orchestrator
    orchestrator = ReverseKnowledgeTreeOrchestrator(
        max_tree_depth=3,  # Limit depth for demo
        enable_code_generation=enable_manim,
        enable_threejs_generation=enable_threejs,
        enable_atlas=False  # Set to True if you have Nomic installed
    )

    # Example prompts to try
    examples = [
        "Explain the Pythagorean theorem with a visual proof",
        "Show me how special relativity works",
        "Visualize the gradient descent algorithm"
    ]

    print("\nExample prompts:")
    for i, example in enumerate(examples, 1):
        print(f"  {i}. {example}")

    print("\n" + "=" * 70)
    choice = input("\nChoose an example (1-3) or enter your own prompt: ").strip()

    if choice in ['1', '2', '3']:
        user_input = examples[int(choice) - 1]
    else:
        user_input = choice

    # Process through the pipeline
    result = orchestrator.process(
        user_input=user_input,
        output_dir="output"
    )

    print("\n" + "=" * 70)
    print("PREVIEW OF VERBOSE PROMPT:")
    print("=" * 70)
    print(result.verbose_prompt[:1000])
    print("\n... (truncated)")

    if result.manim_code:
        print("\n" + "=" * 70)
        print("PREVIEW OF MANIM CODE:")
        print("=" * 70)
        print(result.manim_code[:800])
        print("\n... (truncated)")

    if result.threejs_html:
        print("\n" + "=" * 70)
        print("PREVIEW OF THREE.JS HTML:")
        print("=" * 70)
        print(result.threejs_html[:800])
        print("\n... (truncated)")

    print("\n✅ Complete! Check the output/ directory for all files.")
    if result.threejs_html:
        safe_concept = "".join(c if c.isalnum() else "_" for c in result.target_concept)
        print(f"\n🌐 Open the Three.js visualization:")
        print(f"   file://output/{safe_concept}_threejs.html")


if __name__ == "__main__":
    # Verify API key is set
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("[FAIL] Error: ANTHROPIC_API_KEY environment variable not set.")
        print("\nPlease set your Claude API key:")
        print("  1. Create a .env file in the project root")
        print("  2. Add: ANTHROPIC_API_KEY=your_key_here")
        print("\nGet your API key from: https://console.anthropic.com/")
        exit(1)

    demo()
