"""Backwards-compatible shim — imports from the unified prerequisite_explorer.

All new code should import from:
    src.agents.knowledge_node  (KnowledgeNode)
    src.agents.prerequisite_explorer  (PrerequisiteExplorer, ConceptAnalyzer)
    src.agents.llm_client  (create_client, AnthropicClient, etc.)
"""

# Re-export everything that downstream code expects to find here
from src.agents.knowledge_node import KnowledgeNode  # noqa: F401
from src.agents.prerequisite_explorer import (  # noqa: F401
    ConceptAnalyzer,
    PrerequisiteExplorer,
    CLAUDE_MODEL,
)
from src.agents.llm_client import AnthropicClient, create_client  # noqa: F401
