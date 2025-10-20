"""Agent package exports and pipeline helpers."""

# Use absolute imports
try:
    from src.agents.prerequisite_explorer_claude import ConceptAnalyzer, PrerequisiteExplorer, KnowledgeNode
    from src.agents.mathematical_enricher import MathematicalEnricher, MathematicalContent
    from src.agents.visual_designer import VisualDesigner, VisualSpec
    from src.agents.narrative_composer import NarrativeComposer, Narrative
    from src.agents.orchestrator import ReverseKnowledgeTreeOrchestrator, AnimationResult
    from src.agents.video_review_agent import VideoReviewAgent, VideoReviewResult
    from src.agents.nomic_atlas_client import AtlasClient, AtlasConcept, NomicNotInstalledError
except ImportError:
    # Fallback for when running from src/agents directory
    from prerequisite_explorer_claude import ConceptAnalyzer, PrerequisiteExplorer, KnowledgeNode
    from mathematical_enricher import MathematicalEnricher, MathematicalContent
    from visual_designer import VisualDesigner, VisualSpec
    from narrative_composer import NarrativeComposer, Narrative
    from orchestrator import ReverseKnowledgeTreeOrchestrator, AnimationResult
    from video_review_agent import VideoReviewAgent, VideoReviewResult
    from nomic_atlas_client import AtlasClient, AtlasConcept, NomicNotInstalledError

__all__ = [
    # Core agents
    "ConceptAnalyzer",
    "PrerequisiteExplorer",
    "MathematicalEnricher",
    "VisualDesigner",
    "NarrativeComposer",

    # Orchestrator
    "ReverseKnowledgeTreeOrchestrator",

    # Data structures
    "KnowledgeNode",
    "MathematicalContent",
    "VisualSpec",
    "Narrative",
    "AnimationResult",

    # Video review
    "VideoReviewAgent",
    "VideoReviewResult",

    # Atlas integration
    "AtlasClient",
    "AtlasConcept",
    "NomicNotInstalledError",
]

