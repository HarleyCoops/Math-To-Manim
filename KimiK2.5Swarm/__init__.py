"""
KimiK2Thinking - Knowledge tree enrichment pipeline using Kimi K2.5.

This package provides a comprehensive system for:
- Building prerequisite knowledge trees
- Enriching concepts with mathematical content
- Designing visual presentations for Manim
- Composing comprehensive narratives

Key Components:
- KimiClient: Unified API client with mode support
- PrerequisiteExplorer: Builds knowledge trees
- EnrichmentOrchestrator: Parallel swarm orchestration
- KimiEnrichmentPipeline: Legacy-compatible pipeline interface

Example:
    from KimiK2Thinking import (
        KimiClient,
        PrerequisiteExplorer,
        KimiEnrichmentPipeline,
    )

    # Explore prerequisites
    explorer = PrerequisiteExplorer(max_depth=3)
    tree = explorer.explore("quantum field theory")

    # Enrich the tree
    pipeline = KimiEnrichmentPipeline()
    result = pipeline.run(tree)

    print(result.narrative.verbose_prompt)
"""

# Configuration
from .config import (
    KimiMode,
    ModeConfig,
    APIConfig,
    EnrichmentConfig,
    ModelInfo,
    MODE_CONFIGS,
    MODEL_VARIANTS,
    get_mode_config,
    get_model_info,
    # Legacy exports
    MOONSHOT_API_KEY,
    MOONSHOT_BASE_URL,
    KIMI_K2_MODEL,
    DEFAULT_MAX_TOKENS,
    DEFAULT_TEMPERATURE,
    DEFAULT_TOP_P,
    USE_TOOLS,
    TOOLS_ENABLED,
    ENABLE_THINKING,
    FALLBACK_TO_VERBOSE,
)

# Client
from .kimi_client import (
    KimiClient,
    KimiResponse,
    StreamChunk,
    get_kimi_client,
    create_client,
)

# Models
from .models import (
    KnowledgeNode,
    EnrichmentResult,
    Narrative,
)

# Agents
from .agents import (
    BaseAgent,
    AgentRole,
    AgentConfig,
    AgentResult,
    PrerequisiteExplorer,
    MathematicalEnricher,
    VisualDesigner,
    NarrativeComposer,
    # Legacy aliases
    KimiPrerequisiteExplorer,
    KimiMathematicalEnricher,
    KimiVisualDesigner,
    KimiNarrativeComposer,
)

# Swarm orchestration
from .swarm import (
    EnrichmentOrchestrator,
    EnrichmentSwarmConfig,
    EnrichmentSwarmResult,
    ParallelTreeEnricher,
)

# Tools infrastructure
from .tools import (
    ToolRegistry,
    Tool,
    ParallelToolExecutor,
    ToolResult,
    BatchResult,
    get_default_registry,
    ENRICHMENT_TOOLS,
    MATHEMATICAL_CONTENT_TOOL,
    VISUAL_DESIGN_TOOL,
    NARRATIVE_TOOL,
)

# Legacy-compatible pipeline
from .swarm.orchestrator import KimiEnrichmentPipeline

__version__ = "2.5.0"

__all__ = [
    # Version
    "__version__",
    # Configuration
    "KimiMode",
    "ModeConfig",
    "APIConfig",
    "EnrichmentConfig",
    "ModelInfo",
    "MODE_CONFIGS",
    "MODEL_VARIANTS",
    "get_mode_config",
    "get_model_info",
    # Client
    "KimiClient",
    "KimiResponse",
    "StreamChunk",
    "get_kimi_client",
    "create_client",
    # Models
    "KnowledgeNode",
    "EnrichmentResult",
    "Narrative",
    # Agents
    "BaseAgent",
    "AgentRole",
    "AgentConfig",
    "AgentResult",
    "PrerequisiteExplorer",
    "MathematicalEnricher",
    "VisualDesigner",
    "NarrativeComposer",
    # Swarm
    "EnrichmentOrchestrator",
    "EnrichmentSwarmConfig",
    "EnrichmentSwarmResult",
    "ParallelTreeEnricher",
    # Tools
    "ToolRegistry",
    "Tool",
    "ParallelToolExecutor",
    "ToolResult",
    "BatchResult",
    "get_default_registry",
    "ENRICHMENT_TOOLS",
    # Pipeline
    "KimiEnrichmentPipeline",
    # Legacy
    "KimiPrerequisiteExplorer",
    "KimiMathematicalEnricher",
    "KimiVisualDesigner",
    "KimiNarrativeComposer",
    "MOONSHOT_API_KEY",
    "MOONSHOT_BASE_URL",
    "KIMI_K2_MODEL",
    "DEFAULT_MAX_TOKENS",
    "DEFAULT_TEMPERATURE",
    "DEFAULT_TOP_P",
    "USE_TOOLS",
    "TOOLS_ENABLED",
    "ENABLE_THINKING",
    "FALLBACK_TO_VERBOSE",
]
