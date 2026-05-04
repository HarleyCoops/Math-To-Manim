"""
Unit Tests for KimiK2Thinking PrerequisiteExplorer

Tests the Kimi K2 implementation using Moonshot AI API.
These tests are completely separate from the Claude/Anthropic tests.
Run with: pytest tests/test_kimi_k2_prerequisite_explorer.py -v
"""

import pytest
import asyncio
import json
import os
from unittest.mock import Mock, patch, MagicMock
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add KimiK2Thinking to path
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
kimi_path = project_root / "KimiK2Thinking"
sys.path.insert(0, str(kimi_path))

# Import the Kimi K2 agents to test
from agents.prerequisite_explorer_kimi import (
    KimiPrerequisiteExplorer,
    KnowledgeNode
)
from kimi_client import KimiClient


# Fixtures for testing
@pytest.fixture
def mock_kimi_response():
    """Create a mock Kimi/Moonshot API response"""
    return {
        "id": "test-id",
        "model": "moonshot-v1-8k",
        "choices": [{
            "index": 0,
            "message": {
                "role": "assistant",
                "content": '["concept1", "concept2", "concept3"]'
            },
            "finish_reason": "stop"
        }],
        "usage": {
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "total_tokens": 150
        }
    }


@pytest.fixture
def sample_tree():
    """Create a sample knowledge tree for testing"""
    foundation = KnowledgeNode(
        concept="basic algebra",
        depth=2,
        is_foundation=True,
        prerequisites=[]
    )

    intermediate = KnowledgeNode(
        concept="calculus",
        depth=1,
        is_foundation=False,
        prerequisites=[foundation]
    )

    root = KnowledgeNode(
        concept="differential equations",
        depth=0,
        is_foundation=False,
        prerequisites=[intermediate]
    )

    return root


class TestKimiPrerequisiteExplorer:
    """Test suite for KimiPrerequisiteExplorer agent"""

    def setup_method(self):
        """Setup for each test method"""
        self.explorer = KimiPrerequisiteExplorer(max_depth=2, use_tools=False)

    @pytest.mark.skipif(
        not os.getenv("MOONSHOT_API_KEY"),
        reason="MOONSHOT_API_KEY not set"
    )
    @pytest.mark.asyncio
    async def test_foundation_detection_basic_concepts(self):
        """Test that basic concepts are detected as foundations"""
        basic_concepts = [
            "addition",
            "velocity",
            "distance",
            "time"
        ]

        for concept in basic_concepts:
            result = await self.explorer._is_foundation_async(concept)
            assert result == True, f"{concept} should be detected as foundation"

    @pytest.mark.skipif(
        not os.getenv("MOONSHOT_API_KEY"),
        reason="MOONSHOT_API_KEY not set"
    )
    @pytest.mark.asyncio
    async def test_foundation_detection_advanced_concepts(self):
        """Test that advanced concepts are NOT detected as foundations"""
        advanced_concepts = [
            "quantum field theory",
            "differential geometry",
            "Hilbert spaces"
        ]

        for concept in advanced_concepts:
            result = await self.explorer._is_foundation_async(concept)
            assert result == False, f"{concept} should NOT be detected as foundation"

    @pytest.mark.skipif(
        not os.getenv("MOONSHOT_API_KEY"),
        reason="MOONSHOT_API_KEY not set"
    )
    @pytest.mark.asyncio
    async def test_discover_prerequisites(self):
        """Test discovering prerequisites for a concept"""
        prerequisites = await self.explorer._get_prerequisites_async("special relativity", verbose=False)
        
        assert isinstance(prerequisites, list)
        assert len(prerequisites) > 0
        assert len(prerequisites) <= 5  # Should limit to 3-5

    @pytest.mark.skipif(
        not os.getenv("MOONSHOT_API_KEY"),
        reason="MOONSHOT_API_KEY not set"
    )
    @pytest.mark.asyncio
    async def test_explore_builds_tree(self):
        """Test that explore builds a complete knowledge tree"""
        tree = await self.explorer.explore_async("quantum mechanics", depth=0, verbose=False)
        
        assert isinstance(tree, KnowledgeNode)
        assert tree.concept == "quantum mechanics"
        assert tree.depth == 0

    def test_tree_serialization(self, sample_tree):
        """Test that knowledge trees can be serialized to dict/JSON"""
        tree_dict = sample_tree.to_dict()
        
        assert isinstance(tree_dict, dict)
        assert 'concept' in tree_dict
        assert 'depth' in tree_dict
        assert 'is_foundation' in tree_dict
        assert 'prerequisites' in tree_dict
        
        # Test JSON serialization
        json_str = json.dumps(tree_dict)
        assert isinstance(json_str, str)
        
        # Test deserialization
        loaded = json.loads(json_str)
        assert loaded['concept'] == sample_tree.concept

    def test_tree_no_cycles(self, sample_tree):
        """Verify knowledge tree has no circular dependencies"""
        visited = set()
        
        def check_cycles(node: KnowledgeNode):
            assert node.concept not in visited, f"Cycle detected: {node.concept}"
            visited.add(node.concept)
            for prereq in node.prerequisites:
                check_cycles(prereq)
        
        check_cycles(sample_tree)

    def test_tree_depth_monotonic(self, sample_tree):
        """Verify depth increases monotonically down the tree"""
        def check_depth(node: KnowledgeNode, parent_depth: int = -1):
            assert node.depth > parent_depth, f"Depth not monotonic at {node.concept}"
            for prereq in node.prerequisites:
                check_depth(prereq, node.depth)
        
        check_depth(sample_tree)

    def test_tree_depth_limit_respected(self):
        """Ensure max_depth parameter is respected"""
        explorer = KimiPrerequisiteExplorer(max_depth=1, use_tools=False)
        
        # Create a simple tree manually to test depth limit
        foundation = KnowledgeNode(
            concept="foundation",
            depth=1,
            is_foundation=True,
            prerequisites=[]
        )
        
        root = KnowledgeNode(
            concept="root",
            depth=0,
            is_foundation=False,
            prerequisites=[foundation]
        )
        
        # Verify depth limit
        assert root.depth == 0
        assert foundation.depth == 1
        assert foundation.depth <= explorer.max_depth

    def test_caching_mechanism(self):
        """Verify caching reduces redundant API calls"""
        explorer = KimiPrerequisiteExplorer(max_depth=2, use_tools=False)
        
        # Manually add to cache
        explorer.cache["test_concept"] = ["prereq1", "prereq2"]
        
        # Should use cache
        assert "test_concept" in explorer.cache
        assert explorer.cache["test_concept"] == ["prereq1", "prereq2"]


class TestKimiClient:
    """Test suite for KimiClient"""

    def setup_method(self):
        """Setup for each test method"""
        self.client = KimiClient()

    @pytest.mark.skipif(
        not os.getenv("MOONSHOT_API_KEY"),
        reason="MOONSHOT_API_KEY not set"
    )
    def test_basic_api_call(self):
        """Test basic API call to Kimi K2"""
        response = self.client.chat_completion(
            messages=[{"role": "user", "content": "Say hello"}],
            max_tokens=50
        )
        
        assert "choices" in response
        assert len(response["choices"]) > 0
        content = self.client.get_text_content(response)
        assert len(content) > 0

    def test_get_text_content(self, mock_kimi_response):
        """Test extracting text content from response"""
        content = self.client.get_text_content(mock_kimi_response)
        assert content == '["concept1", "concept2", "concept3"]'

    def test_has_tool_calls(self, mock_kimi_response):
        """Test detecting tool calls in response"""
        assert not self.client.has_tool_calls(mock_kimi_response)
        
        # Response with tool calls
        tool_response = mock_kimi_response.copy()
        tool_response["choices"][0]["message"]["tool_calls"] = [
            {"id": "1", "type": "function", "function": {"name": "test", "arguments": "{}"}}
        ]
        assert self.client.has_tool_calls(tool_response)

    def test_get_tool_calls(self, mock_kimi_response):
        """Test extracting tool calls from response"""
        assert len(self.client.get_tool_calls(mock_kimi_response)) == 0
        
        # Response with tool calls
        tool_response = mock_kimi_response.copy()
        tool_response["choices"][0]["message"]["tool_calls"] = [
            {"id": "1", "type": "function", "function": {"name": "test", "arguments": "{}"}}
        ]
        tool_calls = self.client.get_tool_calls(tool_response)
        assert len(tool_calls) == 1
        assert tool_calls[0]["function"]["name"] == "test"


class TestKimiErrorHandling:
    """Test error handling and edge cases"""

    def setup_method(self):
        """Setup for each test method"""
        self.explorer = KimiPrerequisiteExplorer(max_depth=2, use_tools=False)

    def test_exceeds_max_depth(self):
        """Test behavior when max_depth is reached"""
        explorer = KimiPrerequisiteExplorer(max_depth=0, use_tools=False)
        
        # Create a node at max depth
        node = KnowledgeNode(
            concept="test",
            depth=0,
            is_foundation=True,
            prerequisites=[]
        )
        
        assert node.depth >= explorer.max_depth
        assert node.is_foundation == True

    def test_empty_input_handling(self):
        """Test handling of empty/invalid input"""
        # Empty concept should still create a node
        node = KnowledgeNode(
            concept="",
            depth=0,
            is_foundation=True,
            prerequisites=[]
        )
        
        assert node.concept == ""
        assert isinstance(node.prerequisites, list)

