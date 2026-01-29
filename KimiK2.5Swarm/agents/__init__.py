"""
Agents layer for KimiK2Thinking.

Provides specialized agents for knowledge tree building and enrichment:
- PrerequisiteExplorer: Builds prerequisite knowledge trees
- MathematicalEnricher: Adds equations, definitions, interpretations
- VisualDesigner: Designs Manim visual presentations
- NarrativeComposer: Composes comprehensive animation narratives
"""

# Base agent infrastructure
from .base_agent import (
    BaseAgent,
    AgentRole,
    AgentConfig,
    AgentResult,
    ROLE_PROMPTS,
    create_mathematical_agent,
    create_visual_agent,
    create_narrative_agent,
)

# Enrichment agents
from .enrichment_agents import (
    MathematicalEnricher,
    VisualDesigner,
    NarrativeComposer,
    MathematicalContent,
    VisualSpec,
    # Legacy aliases
    KimiMathematicalEnricher,
    KimiVisualDesigner,
    KimiNarrativeComposer,
)

# Prerequisite explorer
from .prerequisite_explorer import (
    PrerequisiteExplorer,
    TTLCache,
    # Legacy alias
    KimiPrerequisiteExplorer,
)

__all__ = [
    # Base agent
    "BaseAgent",
    "AgentRole",
    "AgentConfig",
    "AgentResult",
    "ROLE_PROMPTS",
    "create_mathematical_agent",
    "create_visual_agent",
    "create_narrative_agent",
    # Enrichment agents
    "MathematicalEnricher",
    "VisualDesigner",
    "NarrativeComposer",
    "MathematicalContent",
    "VisualSpec",
    # Prerequisite explorer
    "PrerequisiteExplorer",
    "TTLCache",
    # Legacy aliases
    "KimiMathematicalEnricher",
    "KimiVisualDesigner",
    "KimiNarrativeComposer",
    "KimiPrerequisiteExplorer",
]
