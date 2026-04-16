"""Agent package exports and pipeline helpers."""

from __future__ import annotations

# Canonical data structures
from src.agents.knowledge_node import KnowledgeNode

# Unified prerequisite explorer and concept analyzer
from src.agents.prerequisite_explorer import (
    ConceptAnalyzer,
    PrerequisiteExplorer,
    CLAUDE_MODEL,
)

# LLM client interface
from src.agents.llm_client import (
    LLMClient,
    AnthropicClient,
    DeepSeekClient,
    KimiClient,
    create_client,
)

# Enrichment agents
try:
    from src.agents.mathematical_enricher import MathematicalEnricher, MathematicalContent
except ImportError:
    MathematicalEnricher = None  # type: ignore[assignment]
    MathematicalContent = None  # type: ignore[assignment]

try:
    from src.agents.visual_designer import VisualDesigner, VisualSpec
except ImportError:
    VisualDesigner = None  # type: ignore[assignment]
    VisualSpec = None  # type: ignore[assignment]

try:
    from src.agents.narrative_composer import NarrativeComposer, Narrative
except ImportError:
    NarrativeComposer = None  # type: ignore[assignment]
    Narrative = None  # type: ignore[assignment]

try:
    from src.agents.video_review_agent import VideoReviewAgent, VideoReviewResult
except ImportError:
    VideoReviewAgent = None  # type: ignore[assignment]
    VideoReviewResult = None  # type: ignore[assignment]

try:
    from src.agents.threejs_code_generator import ThreeJSCodeGenerator, ThreeJSOutput
except ImportError:
    ThreeJSCodeGenerator = None  # type: ignore[assignment]
    ThreeJSOutput = None  # type: ignore[assignment]

try:
    from src.agents.orchestrator import ReverseKnowledgeTreeOrchestrator, AnimationResult
except ImportError:
    ReverseKnowledgeTreeOrchestrator = None  # type: ignore[assignment]
    AnimationResult = None  # type: ignore[assignment]

__all__ = [
    # Core types
    "KnowledgeNode",
    "CLAUDE_MODEL",
    # LLM clients
    "LLMClient",
    "AnthropicClient",
    "DeepSeekClient",
    "KimiClient",
    "create_client",
    # Core agents
    "ConceptAnalyzer",
    "PrerequisiteExplorer",
    "MathematicalEnricher",
    "VisualDesigner",
    "NarrativeComposer",
    # Code generators
    "ThreeJSCodeGenerator",
    # Orchestrator
    "ReverseKnowledgeTreeOrchestrator",
    # Data structures
    "MathematicalContent",
    "VisualSpec",
    "Narrative",
    "AnimationResult",
    "ThreeJSOutput",
    # Video review
    "VideoReviewAgent",
    "VideoReviewResult",
]
