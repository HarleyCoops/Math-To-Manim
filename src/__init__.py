"""Top-level package for the Math-To-Manim agent system."""

__version__ = "0.1.0"

from src.agents.knowledge_node import KnowledgeNode
from src.agents.prerequisite_explorer import ConceptAnalyzer, PrerequisiteExplorer
from src.agents.llm_client import create_client, LLMClient

__all__ = [
    "ConceptAnalyzer",
    "KnowledgeNode",
    "LLMClient",
    "PrerequisiteExplorer",
    "create_client",
]
