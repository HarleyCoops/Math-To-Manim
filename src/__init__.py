"""Top-level package for the Math-To-Manim agent system."""

# Use absolute imports
try:
    from src.agents import (
        AtlasClient,
        AtlasConcept,
        ConceptAnalyzer,
        NomicNotInstalledError,
        PrerequisiteExplorer,
        VideoReviewAgent,
        VideoReviewResult,
    )
except ImportError:
    # This allows importing from the src directory directly
    try:
        from agents import (
            AtlasClient,
            AtlasConcept,
            ConceptAnalyzer,
            NomicNotInstalledError,
            PrerequisiteExplorer,
            VideoReviewAgent,
            VideoReviewResult,
        )
    except ImportError:
        # Direct imports as last resort
        from src.agents.prerequisite_explorer_claude import ConceptAnalyzer, PrerequisiteExplorer
        from src.agents.video_review_agent import VideoReviewAgent, VideoReviewResult
        from src.agents.nomic_atlas_client import AtlasClient, AtlasConcept, NomicNotInstalledError

__all__ = [
    "AtlasClient",
    "AtlasConcept",
    "ConceptAnalyzer",
    "NomicNotInstalledError",
    "PrerequisiteExplorer",
    "VideoReviewAgent",
    "VideoReviewResult",
]

