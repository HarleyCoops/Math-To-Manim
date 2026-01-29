"""
Models layer for KimiK2Thinking.

Provides data structures used throughout the enrichment pipeline.
"""

from .knowledge_node import KnowledgeNode
from .enrichment_result import EnrichmentResult, Narrative

__all__ = ["KnowledgeNode", "EnrichmentResult", "Narrative"]
