"""Agent Orchestrator using Claude Agent SDK.

This orchestrates the full pipeline:
1. ConceptAnalyzer - Parse user intent
2. PrerequisiteExplorer - Build knowledge tree
3. MathematicalEnricher - Add LaTeX (future)
4. VisualDesigner - Design animations (future)
5. NarrativeComposer - Generate verbose prompt (future)
6. CodeGenerator - Create Manim code (future)
7. VideoReview - QA the output (implemented)
"""

from __future__ import annotations

import asyncio
import json
import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    TextBlock,
    create_sdk_mcp_server,
)
from dotenv import load_dotenv

# Import agents
try:
    from src.agents.enhanced_prerequisite_explorer import (
        EnhancedPrerequisiteExplorer,
        KnowledgeNode,
    )
    from src.agents.claude_sdk_tools import ALL_TOOLS
    from src.agents.video_review_agent import VideoReviewAgent, VideoReviewResult
except ImportError:
    try:
        from enhanced_prerequisite_explorer import (
            EnhancedPrerequisiteExplorer,
            KnowledgeNode,
        )
        from claude_sdk_tools import ALL_TOOLS
        from video_review_agent import VideoReviewAgent, VideoReviewResult
    except ImportError:
        print("Warning: Could not import agents")
        EnhancedPrerequisiteExplorer = None  # type: ignore
        ALL_TOOLS = []

load_dotenv()


class PipelineState(Enum):
    """States in the agent pipeline."""
    INIT = "init"
    CONCEPT_ANALYSIS = "concept_analysis"
    PREREQUISITE_DISCOVERY = "prerequisite_discovery"
    MATHEMATICAL_ENRICHMENT = "mathematical_enrichment"
    VISUAL_DESIGN = "visual_design"
    NARRATIVE_COMPOSITION = "narrative_composition"
    CODE_GENERATION = "code_generation"
    VIDEO_REVIEW = "video_review"
    COMPLETE = "complete"
    FAILED = "failed"


@dataclass
class PipelineContext:
    """Shared context across all agents in the pipeline."""
    user_input: str
    concept_analysis: Optional[Dict[str, Any]] = None
    knowledge_tree: Optional[KnowledgeNode] = None
    enriched_tree: Optional[Dict[str, Any]] = None
    visual_design: Optional[Dict[str, Any]] = None
    narrative: Optional[str] = None
    manim_code: Optional[str] = None
    video_path: Optional[Path] = None
    video_review: Optional[VideoReviewResult] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class AgentOrchestrator:
    """
    Orchestrates the full Math-To-Manim agent pipeline.

    Uses Claude Agent SDK for:
    - Stateful conversations
    - Custom MCP tools
    - Error handling
    - Streaming updates
    """

    def __init__(
        self,
        max_depth: int = 4,
        use_tools: bool = True,
        verbose: bool = True
    ):
        self.max_depth = max_depth
        self.use_tools = use_tools
        self.verbose = verbose
        self.state = PipelineState.INIT
        self.context: Optional[PipelineContext] = None

        # Initialize MCP server with tools
        self.mcp_server = None
        if use_tools and ALL_TOOLS:
            self.mcp_server = create_sdk_mcp_server(
                name="math-to-manim-orchestrator",
                tools=ALL_TOOLS
            )

        # Initialize agents
        if EnhancedPrerequisiteExplorer is not None:
            self.prerequisite_explorer = EnhancedPrerequisiteExplorer(
                max_depth=max_depth,
                use_tools=use_tools
            )
        else:
            self.prerequisite_explorer = None

        self.video_review_agent = VideoReviewAgent()

    async def process_async(self, user_input: str) -> Dict[str, Any]:
        """
        Process a user request through the full agent pipeline.

        Args:
            user_input: The user's natural language request

        Returns:
            Dict containing results from all pipeline stages
        """
        self.context = PipelineContext(user_input=user_input)

        try:
            # Stage 1: Concept Analysis
            self.state = PipelineState.CONCEPT_ANALYSIS
            await self._analyze_concept()

            # Stage 2: Prerequisite Discovery
            self.state = PipelineState.PREREQUISITE_DISCOVERY
            await self._discover_prerequisites()

            # Stage 3: Mathematical Enrichment (TODO)
            self.state = PipelineState.MATHEMATICAL_ENRICHMENT
            await self._enrich_mathematics()

            # Stage 4: Visual Design (TODO)
            self.state = PipelineState.VISUAL_DESIGN
            await self._design_visuals()

            # Stage 5: Narrative Composition (TODO)
            self.state = PipelineState.NARRATIVE_COMPOSITION
            await self._compose_narrative()

            # Stage 6: Code Generation (TODO)
            self.state = PipelineState.CODE_GENERATION
            await self._generate_code()

            # Stage 7: Video Review (if video exists)
            self.state = PipelineState.VIDEO_REVIEW
            if self.context.video_path and self.context.video_path.exists():
                await self._review_video()

            self.state = PipelineState.COMPLETE
            return self._build_result()

        except Exception as e:
            self.state = PipelineState.FAILED
            self.context.errors.append(str(e))
            return self._build_result()

    async def _analyze_concept(self):
        """Stage 1: Analyze user input to extract core concept and metadata."""
        if self.verbose:
            print(f"\n[Stage 1] Analyzing concept from: '{self.context.user_input}'")

        system_prompt = """You are an expert at analyzing educational requests.

Analyze the user's question and extract:
1. The MAIN concept they want to understand (be specific)
2. The scientific/mathematical domain
3. The appropriate complexity level
4. Their learning goal

Return ONLY valid JSON with these exact keys:
- core_concept
- domain
- level (must be: "beginner", "intermediate", or "advanced")
- goal"""

        user_prompt = f'''User asked: "{self.context.user_input}"

Return JSON analysis with: core_concept, domain, level, goal

Example:
{{
  "core_concept": "quantum entanglement",
  "domain": "physics/quantum mechanics",
  "level": "intermediate",
  "goal": "Understand how entangled particles maintain correlation across distances"
}}'''

        options = ClaudeAgentOptions()
        options.system_prompt = system_prompt
        if self.use_tools and self.mcp_server:
            options.mcp_servers = [self.mcp_server]

        async with ClaudeSDKClient(options=options) as client:
            await client.connect(prompt=user_prompt)

            response_text = ""
            async for message in client.messages():
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock):
                            response_text += block.text

            # Parse JSON response
            try:
                analysis = json.loads(response_text)
            except json.JSONDecodeError:
                # Try to extract from code blocks
                if "```" in response_text:
                    response_text = response_text.split("```")[1]
                    if response_text.startswith("json"):
                        response_text = response_text[4:]
                    analysis = json.loads(response_text.strip())
                else:
                    import re
                    match = re.search(r'\{.*?\}', response_text, re.DOTALL)
                    if match:
                        analysis = json.loads(match.group(0))
                    else:
                        raise ValueError(f"Could not parse analysis from: {response_text}")

            self.context.concept_analysis = analysis

            if self.verbose:
                print(f"  ✓ Core concept: {analysis.get('core_concept')}")
                print(f"  ✓ Domain: {analysis.get('domain')}")
                print(f"  ✓ Level: {analysis.get('level')}")

    async def _discover_prerequisites(self):
        """Stage 2: Build knowledge tree of prerequisites."""
        if self.verbose:
            print(f"\n[Stage 2] Discovering prerequisites...")

        if self.prerequisite_explorer is None:
            self.context.warnings.append("Prerequisite explorer not available")
            return

        core_concept = self.context.concept_analysis.get('core_concept')
        if not core_concept:
            self.context.errors.append("No core concept identified")
            return

        tree = await self.prerequisite_explorer.explore_async(
            core_concept,
            verbose=self.verbose
        )

        self.context.knowledge_tree = tree

        if self.verbose:
            print(f"\n  ✓ Knowledge tree built with {self._count_nodes(tree)} nodes")

    async def _enrich_mathematics(self):
        """Stage 3: Add LaTeX equations and definitions (TODO)."""
        if self.verbose:
            print(f"\n[Stage 3] Mathematical enrichment (TODO)")

        self.context.warnings.append("Mathematical enrichment not yet implemented")
        # TODO: Implement MathematicalEnricher agent

    async def _design_visuals(self):
        """Stage 4: Design visual specifications (TODO)."""
        if self.verbose:
            print(f"\n[Stage 4] Visual design (TODO)")

        self.context.warnings.append("Visual design not yet implemented")
        # TODO: Implement VisualDesigner agent

    async def _compose_narrative(self):
        """Stage 5: Generate verbose narrative prompt (TODO)."""
        if self.verbose:
            print(f"\n[Stage 5] Narrative composition (TODO)")

        self.context.warnings.append("Narrative composition not yet implemented")
        # TODO: Implement NarrativeComposer agent

    async def _generate_code(self):
        """Stage 6: Generate Manim code (TODO)."""
        if self.verbose:
            print(f"\n[Stage 6] Code generation (TODO)")

        self.context.warnings.append("Code generation not yet implemented")
        # TODO: Implement CodeGenerator agent

    async def _review_video(self):
        """Stage 7: Review rendered video."""
        if self.verbose:
            print(f"\n[Stage 7] Video review")

        try:
            result = self.video_review_agent.review(self.context.video_path)
            self.context.video_review = result

            if self.verbose:
                print(f"  ✓ Video reviewed: {result.video_path}")
                print(f"  ✓ Frames extracted: {result.frames_dir}")
        except Exception as e:
            self.context.warnings.append(f"Video review failed: {e}")

    def _count_nodes(self, node: KnowledgeNode) -> int:
        """Count total nodes in the tree."""
        count = 1
        for prereq in node.prerequisites:
            count += self._count_nodes(prereq)
        return count

    def _build_result(self) -> Dict[str, Any]:
        """Build the final result dictionary."""
        return {
            "status": "success" if self.state == PipelineState.COMPLETE else "failed",
            "state": self.state.value,
            "user_input": self.context.user_input,
            "concept_analysis": self.context.concept_analysis,
            "knowledge_tree": (
                self.context.knowledge_tree.to_dict()
                if self.context.knowledge_tree else None
            ),
            "manim_code": self.context.manim_code,
            "video_path": str(self.context.video_path) if self.context.video_path else None,
            "video_review": (
                self.context.video_review.to_dict()
                if self.context.video_review else None
            ),
            "errors": self.context.errors,
            "warnings": self.context.warnings,
        }

    # Synchronous wrapper
    def process(self, user_input: str) -> Dict[str, Any]:
        """Synchronous wrapper around process_async."""
        return asyncio.run(self.process_async(user_input))


async def demo():
    """Demo the agent orchestrator."""
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║              Agent Orchestrator - Full Pipeline Demo             ║
║                                                                   ║
║  Pipeline Stages:                                                ║
║  1. Concept Analysis                                             ║
║  2. Prerequisite Discovery                                       ║
║  3. Mathematical Enrichment (TODO)                               ║
║  4. Visual Design (TODO)                                         ║
║  5. Narrative Composition (TODO)                                 ║
║  6. Code Generation (TODO)                                       ║
║  7. Video Review                                                 ║
║                                                                   ║
║  Powered by: Claude Agent SDK + Custom MCP Tools                 ║
╚═══════════════════════════════════════════════════════════════════╝
    """)

    orchestrator = AgentOrchestrator(max_depth=3, use_tools=True, verbose=True)

    user_input = "Explain quantum mechanics to me"

    print(f"\n{'='*70}")
    print(f"USER REQUEST: {user_input}")
    print('='*70)

    result = await orchestrator.process_async(user_input)

    print(f"\n{'='*70}")
    print("PIPELINE RESULT")
    print('='*70)
    print(f"Status: {result['status']}")
    print(f"Final State: {result['state']}")

    if result.get('errors'):
        print(f"\nErrors: {len(result['errors'])}")
        for error in result['errors']:
            print(f"  - {error}")

    if result.get('warnings'):
        print(f"\nWarnings: {len(result['warnings'])}")
        for warning in result['warnings']:
            print(f"  - {warning}")

    # Save result
    output_file = "orchestrator_result.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    print(f"\nSaved result to: {output_file}")


if __name__ == "__main__":
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("[FAIL] Error: ANTHROPIC_API_KEY environment variable not set.")
        exit(1)

    asyncio.run(demo())
