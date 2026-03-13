"""Unit tests for the unified PrerequisiteExplorer (with mock LLM client)."""

import pytest

from src.agents.knowledge_node import KnowledgeNode
from src.agents.llm_client import LLMClient
from src.agents.prerequisite_explorer import PrerequisiteExplorer, ConceptAnalyzer


class MockClient(LLMClient):
    """Mock LLM client with configurable responses."""

    def __init__(self):
        self.calls = []
        self._responses = {}

    def add_response(self, contains: str, response: str):
        """Add a response keyed by a substring in the prompt."""
        self._responses[contains] = response

    def query(self, user_prompt, system_prompt="", max_tokens=500, temperature=0.3):
        self.calls.append({"user": user_prompt, "system": system_prompt})
        for key, response in self._responses.items():
            if key in user_prompt:
                return response
        # Default: foundation=yes for any concept, empty prereqs
        if "foundational" in system_prompt.lower():
            return "yes"
        return '[]'

    @property
    def model_name(self):
        return "mock"


class TestPrerequisiteExplorer:
    """Tests for PrerequisiteExplorer with mocked LLM."""

    def test_explore_foundation_concept(self):
        client = MockClient()
        client.add_response("velocity", "yes")
        explorer = PrerequisiteExplorer(client, max_depth=3)

        tree = explorer.explore("velocity")
        assert tree.concept == "velocity"
        assert tree.is_foundation is True
        assert tree.prerequisites == []

    def test_explore_with_prerequisites(self):
        client = MockClient()
        # "momentum" is NOT a foundation
        client.add_response('"momentum"', "no")
        # Return prerequisites for momentum
        client.add_response('"momentum"', '["velocity", "mass"]')
        # "velocity" and "mass" ARE foundations
        client.add_response('"velocity"', "yes")
        client.add_response('"mass"', "yes")

        explorer = PrerequisiteExplorer(client, max_depth=3)
        tree = explorer.explore("momentum")

        assert tree.concept == "momentum"
        assert tree.is_foundation is False
        assert len(tree.prerequisites) == 2

    def test_max_depth_stops_recursion(self):
        client = MockClient()
        # "deep concept" is not a foundation, but children are forced by depth
        client.add_response('"deep concept" a foundational', "no")
        client.add_response('"child" a foundational', "no")
        client.add_response('To understand "deep concept"', '["child"]')
        client.add_response('To understand "child"', '["grandchild"]')

        explorer = PrerequisiteExplorer(client, max_depth=1)
        tree = explorer.explore("deep concept")

        # depth 0 is "deep concept" (not foundation, has prereqs)
        assert tree.depth == 0
        assert tree.is_foundation is False
        # depth 1 children are forced to foundation by max_depth
        assert len(tree.prerequisites) == 1
        assert tree.prerequisites[0].is_foundation is True

    def test_caching(self):
        client = MockClient()
        client.add_response("foundational", "no")
        client.add_response("prerequisites", '["A", "B"]')

        explorer = PrerequisiteExplorer(client, max_depth=1)

        # First call discovers
        prereqs1 = explorer.lookup_prerequisites("test")
        # Second call should use cache
        prereqs2 = explorer.lookup_prerequisites("test")

        assert prereqs1 == prereqs2
        assert explorer.stats["cache_hits"] == 1

    def test_stats_tracking(self):
        client = MockClient()
        client.add_response("", "yes")  # everything is foundation
        explorer = PrerequisiteExplorer(client, max_depth=3)

        explorer.explore("test concept")

        assert explorer.stats["concepts"] >= 1
        assert explorer.stats["api_calls"] >= 1

    def test_discover_prerequisites_limits_to_5(self):
        client = MockClient()
        client.add_response("", '["a", "b", "c", "d", "e", "f", "g"]')
        explorer = PrerequisiteExplorer(client, max_depth=1)

        prereqs = explorer.discover_prerequisites("test")
        assert len(prereqs) <= 5


class TestConceptAnalyzer:
    """Tests for ConceptAnalyzer with mocked LLM."""

    def test_analyze_returns_dict(self):
        client = MockClient()
        client.add_response("", '{"core_concept": "QFT", "domain": "physics", "level": "advanced", "goal": "understand"}')
        analyzer = ConceptAnalyzer(client)

        result = analyzer.analyze("Explain quantum field theory")
        assert result["core_concept"] == "QFT"
        assert result["domain"] == "physics"
        assert result["level"] == "advanced"

    def test_analyze_handles_code_fence(self):
        client = MockClient()
        client.add_response("", '```json\n{"core_concept": "calculus", "domain": "math", "level": "intermediate", "goal": "learn"}\n```')
        analyzer = ConceptAnalyzer(client)

        result = analyzer.analyze("Teach me calculus")
        assert result["core_concept"] == "calculus"
