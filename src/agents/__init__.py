"""Agent package exports and pipeline helpers."""

# Use absolute imports
try:
    from src.agents.prerequisite_explorer_claude import ConceptAnalyzer, PrerequisiteExplorer
    from src.agents.video_review_agent import VideoReviewAgent, VideoReviewResult
    from src.agents.nomic_atlas_client import AtlasClient, AtlasConcept, NomicNotInstalledError
except ImportError:
    # Fallback for when running from src/agents directory
    from prerequisite_explorer_claude import ConceptAnalyzer, PrerequisiteExplorer
    from video_review_agent import VideoReviewAgent, VideoReviewResult
    from nomic_atlas_client import AtlasClient, AtlasConcept, NomicNotInstalledError

__all__ = [
    "ConceptAnalyzer",
    "PrerequisiteExplorer",
    "VideoReviewAgent",
    "VideoReviewResult",
    "AtlasClient",
    "AtlasConcept",
    "NomicNotInstalledError",
]

