"""Agent package exports and pipeline helpers."""

from __future__ import annotations

# Import core agents with graceful fallbacks so test environments without the
# Claude Agent SDK still work.
try:
    from src.agents.prerequisite_explorer_claude import ConceptAnalyzer, PrerequisiteExplorer, KnowledgeNode
except ImportError:
    from prerequisite_explorer_claude import ConceptAnalyzer, PrerequisiteExplorer, KnowledgeNode  # type: ignore

try:
    from src.agents.mathematical_enricher import MathematicalEnricher, MathematicalContent
except ImportError:
    from mathematical_enricher import MathematicalEnricher, MathematicalContent  # type: ignore

try:
    from src.agents.visual_designer import VisualDesigner, VisualSpec
except ImportError:
    from visual_designer import VisualDesigner, VisualSpec  # type: ignore

try:
    from src.agents.narrative_composer import NarrativeComposer, Narrative
except ImportError:
    from narrative_composer import NarrativeComposer, Narrative  # type: ignore

try:
    from src.agents.video_review_agent import VideoReviewAgent, VideoReviewResult
except ImportError:
    from video_review_agent import VideoReviewAgent, VideoReviewResult  # type: ignore

try:
    from src.agents.threejs_code_generator import ThreeJSCodeGenerator, ThreeJSOutput
except ImportError:
    try:
        from threejs_code_generator import ThreeJSCodeGenerator, ThreeJSOutput  # type: ignore
    except ImportError:
        ThreeJSCodeGenerator = None  # type: ignore[assignment]
        ThreeJSOutput = None  # type: ignore[assignment]

try:
    from src.agents.nomic_atlas_client import AtlasClient, AtlasConcept, NomicNotInstalledError
except ImportError:
    from nomic_atlas_client import AtlasClient, AtlasConcept, NomicNotInstalledError  # type: ignore

try:
    from src.agents.orchestrator import ReverseKnowledgeTreeOrchestrator, AnimationResult
except ImportError:
    ReverseKnowledgeTreeOrchestrator = None  # type: ignore[assignment]
    AnimationResult = None  # type: ignore[assignment]

__all__ = [
    # Core agents
    "ConceptAnalyzer",
    "PrerequisiteExplorer",
    "MathematicalEnricher",
    "VisualDesigner",
    "NarrativeComposer",

    # Code generators
    "ThreeJSCodeGenerator",

    # Orchestrator (optional)
    "ReverseKnowledgeTreeOrchestrator",

    # Data structures
    "KnowledgeNode",
    "MathematicalContent",
    "VisualSpec",
    "Narrative",
    "AnimationResult",
    "ThreeJSOutput",

    # Video review
    "VideoReviewAgent",
    "VideoReviewResult",

    # Atlas integration
    "AtlasClient",
    "AtlasConcept",
    "NomicNotInstalledError",
]

