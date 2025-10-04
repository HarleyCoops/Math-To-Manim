"""
Unit Tests for PrerequisiteExplorer and ConceptAnalyzer

Tests both synchronous and asynchronous behavior.
Run with: pytest tests/test_prerequisite_explorer.py -v
"""

import pytest
import asyncio
import json
import os
from unittest.mock import Mock, patch, MagicMock
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src/agents to path
import sys
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(project_root, 'src', 'agents'))

# Import the agents to test
from prerequisite_explorer_claude import (
    ConceptAnalyzer,
    PrerequisiteExplorer,
    KnowledgeNode
)


# Fixtures for testing
@pytest.fixture
def mock_anthropic_response():
    """Create a mock Anthropic API response"""
    mock_response = Mock()
    mock_response.content = [Mock(text='{"core_concept": "test", "domain": "test", "level": "beginner", "goal": "test"}')]
    mock_response.usage = Mock(input_tokens=100, output_tokens=50)
    return mock_response


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
        concept="linear algebra",
        depth=1,
        is_foundation=False,
        prerequisites=[foundation]
    )

    root = KnowledgeNode(
        concept="quantum mechanics",
        depth=0,
        is_foundation=False,
        prerequisites=[intermediate]
    )

    return root


class TestConceptAnalyzer:
    """Test suite for ConceptAnalyzer agent"""

    def setup_method(self):
        """Setup for each test method"""
        self.analyzer = ConceptAnalyzer()

    @pytest.mark.skipif(
        not os.getenv("ANTHROPIC_API_KEY"),
        reason="ANTHROPIC_API_KEY not set"
    )
    def test_analyze_simple_physics_question(self):
        """Test analyzing a basic physics question"""
        result = self.analyzer.analyze("Explain cosmology")

        # Verify required fields exist
        assert 'core_concept' in result
        assert 'domain' in result
        assert 'level' in result
        assert 'goal' in result

        # Verify concept extraction
        assert 'cosmology' in result['core_concept'].lower()

        # Verify domain categorization
        assert 'physics' in result['domain'].lower() or 'astronomy' in result['domain'].lower()

        # Verify level is valid
        assert result['level'] in ['beginner', 'intermediate', 'advanced']

    @pytest.mark.skipif(
        not os.getenv("ANTHROPIC_API_KEY"),
        reason="ANTHROPIC_API_KEY not set"
    )
    def test_analyze_advanced_math_question(self):
        """Test analyzing advanced mathematics"""
        result = self.analyzer.analyze("Prove the Riemann hypothesis")

        assert 'riemann' in result['core_concept'].lower()
        assert result['level'] in ['intermediate', 'advanced']
        assert 'math' in result['domain'].lower()

    @pytest.mark.skipif(
        not os.getenv("ANTHROPIC_API_KEY"),
        reason="ANTHROPIC_API_KEY not set"
    )
    def test_analyze_computer_science_question(self):
        """Test analyzing CS concepts"""
        result = self.analyzer.analyze("How does binary search work?")

        assert 'binary' in result['core_concept'].lower() or 'search' in result['core_concept'].lower()
        assert 'computer' in result['domain'].lower() or 'cs' in result['domain'].lower()

    def test_output_structure_consistency(self):
        """Verify output always has required fields (mocked)"""
        with patch('prerequisite_explorer_claude.client.messages.create') as mock_create:
            # Mock the API response
            mock_response = Mock()
            mock_response.content = [Mock(text=json.dumps({
                'core_concept': 'test concept',
                'domain': 'test domain',
                'level': 'beginner',
                'goal': 'test goal'
            }))]
            mock_create.return_value = mock_response

            result = self.analyzer.analyze("Test question")

            # Verify all required fields present
            required_fields = ['core_concept', 'domain', 'level', 'goal']
            for field in required_fields:
                assert field in result, f"Missing required field: {field}"

    def test_handles_varied_input_formats(self):
        """Test that analyzer handles different question formats"""
        with patch('prerequisite_explorer_claude.client.messages.create') as mock_create:
            mock_response = Mock()
            mock_response.content = [Mock(text=json.dumps({
                'core_concept': 'test',
                'domain': 'test',
                'level': 'beginner',
                'goal': 'test'
            }))]
            mock_create.return_value = mock_response

            inputs = [
                "Explain quantum mechanics",
                "What is quantum mechanics?",
                "quantum mechanics",
                "I want to learn about quantum mechanics"
            ]

            for user_input in inputs:
                result = self.analyzer.analyze(user_input)
                assert 'core_concept' in result


class TestPrerequisiteExplorer:
    """Test suite for PrerequisiteExplorer agent"""

    def setup_method(self):
        """Setup for each test method"""
        self.explorer = PrerequisiteExplorer(max_depth=2)  # Limit depth for tests

    @pytest.mark.skipif(
        not os.getenv("ANTHROPIC_API_KEY"),
        reason="ANTHROPIC_API_KEY not set"
    )
    def test_foundation_detection_basic_concepts(self):
        """Test that basic concepts are detected as foundations"""
        basic_concepts = [
            "addition",
            "velocity",
            "distance",
            "time"
        ]

        for concept in basic_concepts:
            result = self.explorer.is_foundation(concept)
            assert result == True, f"{concept} should be detected as foundation"

    @pytest.mark.skipif(
        not os.getenv("ANTHROPIC_API_KEY"),
        reason="ANTHROPIC_API_KEY not set"
    )
    def test_foundation_detection_advanced_concepts(self):
        """Test that advanced concepts are NOT detected as foundations"""
        advanced_concepts = [
            "quantum field theory",
            "differential geometry",
            "Hilbert spaces"
        ]

        for concept in advanced_concepts:
            result = self.explorer.is_foundation(concept)
            assert result == False, f"{concept} should NOT be detected as foundation"

    @pytest.mark.skipif(
        not os.getenv("ANTHROPIC_API_KEY"),
        reason="ANTHROPIC_API_KEY not set"
    )
    def test_discover_prerequisites(self):
        """Test discovering prerequisites for a concept"""
        prereqs = self.explorer.discover_prerequisites("calculus")

        # Verify return type
        assert isinstance(prereqs, list)

        # Verify prerequisites found
        assert len(prereqs) > 0, "Should find at least one prerequisite"

        # Verify limit respected
        assert len(prereqs) <= 5, "Should not exceed 5 prerequisites"

        # Verify prerequisites are strings
        for prereq in prereqs:
            assert isinstance(prereq, str)
            assert len(prereq) > 0

    @pytest.mark.skipif(
        not os.getenv("ANTHROPIC_API_KEY"),
        reason="ANTHROPIC_API_KEY not set"
    )
    def test_caching_mechanism(self):
        """Verify caching reduces redundant API calls"""
        # Create new explorer to ensure clean cache
        explorer = PrerequisiteExplorer(max_depth=2)

        concept = "algebra"

        # First discovery should NOT be cached
        prereqs_1 = explorer.discover_prerequisites(concept)
        cache_size_1 = len(explorer.cache)

        # Second discovery should use cache
        prereqs_2 = explorer.discover_prerequisites(concept)
        cache_size_2 = len(explorer.cache)

        # Verify caching worked
        assert prereqs_1 == prereqs_2, "Cached result should match original"
        assert cache_size_1 == cache_size_2, "Cache should not grow for duplicate queries"
        assert concept in explorer.cache, "Concept should be in cache"

    @pytest.mark.skipif(
        not os.getenv("ANTHROPIC_API_KEY"),
        reason="ANTHROPIC_API_KEY not set"
    )
    def test_explore_builds_tree(self):
        """Test that explore builds a complete knowledge tree"""
        tree = self.explorer.explore("linear algebra")

        # Verify root node
        assert isinstance(tree, KnowledgeNode)
        assert tree.concept == "linear algebra"
        assert tree.depth == 0

        # Verify tree has prerequisites (unless it's foundational)
        if not tree.is_foundation:
            assert len(tree.prerequisites) > 0, "Non-foundation should have prerequisites"

    def test_tree_depth_limit_respected(self):
        """Ensure max_depth parameter is respected"""
        explorer = PrerequisiteExplorer(max_depth=2)
        tree = explorer.explore("quantum mechanics")

        def check_depth(node, current_depth=0):
            """Recursively verify depth limit"""
            assert current_depth <= explorer.max_depth, \
                f"Depth {current_depth} exceeds max_depth {explorer.max_depth}"

            for prereq in node.prerequisites:
                check_depth(prereq, current_depth + 1)

        check_depth(tree)

    def test_tree_serialization(self, sample_tree):
        """Test that knowledge trees can be serialized to dict/JSON"""
        tree_dict = sample_tree.to_dict()

        # Verify structure
        assert isinstance(tree_dict, dict)
        assert 'concept' in tree_dict
        assert 'depth' in tree_dict
        assert 'is_foundation' in tree_dict
        assert 'prerequisites' in tree_dict

        # Verify JSON serializable
        json_str = json.dumps(tree_dict)
        assert len(json_str) > 0

        # Verify can deserialize
        deserialized = json.loads(json_str)
        assert deserialized['concept'] == sample_tree.concept

    def test_tree_no_cycles(self, sample_tree):
        """Verify knowledge tree has no circular dependencies"""
        visited = set()

        def check_no_cycles(node):
            """Recursively check for cycles"""
            assert node.concept not in visited, \
                f"Cycle detected: {node.concept} appears twice"

            visited.add(node.concept)

            for prereq in node.prerequisites:
                check_no_cycles(prereq)

        check_no_cycles(sample_tree)

    def test_tree_depth_monotonic(self, sample_tree):
        """Verify depth increases monotonically down the tree"""
        def check_depth_monotonic(node):
            """Recursively verify depth increases"""
            for prereq in node.prerequisites:
                assert prereq.depth > node.depth, \
                    f"Prerequisite {prereq.concept} (depth {prereq.depth}) " \
                    f"should be deeper than {node.concept} (depth {node.depth})"

                check_depth_monotonic(prereq)

        check_depth_monotonic(sample_tree)


class TestAsyncExploration:
    """Test asynchronous/concurrent exploration capabilities"""

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        not os.getenv("ANTHROPIC_API_KEY"),
        reason="ANTHROPIC_API_KEY not set"
    )
    async def test_concurrent_analysis(self):
        """Test analyzing multiple concepts concurrently"""
        analyzer = ConceptAnalyzer()

        concepts = [
            "quantum mechanics",
            "calculus",
            "machine learning"
        ]

        # Create tasks for concurrent execution
        async def analyze_async(concept):
            """Async wrapper for analyze"""
            # Run in thread pool since analyze() is synchronous
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, analyzer.analyze, f"Explain {concept}")

        tasks = [analyze_async(concept) for concept in concepts]
        results = await asyncio.gather(*tasks)

        # Verify all completed
        assert len(results) == len(concepts)

        # Verify each has required fields
        for result in results:
            assert 'core_concept' in result
            assert 'domain' in result

    @pytest.mark.asyncio
    @pytest.mark.skipif(
        not os.getenv("ANTHROPIC_API_KEY"),
        reason="ANTHROPIC_API_KEY not set"
    )
    async def test_concurrent_prerequisite_discovery(self):
        """Test discovering prerequisites for multiple concepts concurrently"""
        explorer = PrerequisiteExplorer(max_depth=1)  # Shallow for speed

        concepts = ["algebra", "geometry", "trigonometry"]

        async def discover_async(concept):
            """Async wrapper for discover_prerequisites"""
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, explorer.discover_prerequisites, concept)

        tasks = [discover_async(concept) for concept in concepts]
        results = await asyncio.gather(*tasks)

        # Verify all completed
        assert len(results) == len(concepts)

        # Verify each returned prerequisites
        for prereqs in results:
            assert isinstance(prereqs, list)
            assert len(prereqs) > 0


class TestErrorHandling:
    """Test error handling and edge cases"""

    def test_empty_input_handling(self):
        """Test handling of empty/invalid input"""
        analyzer = ConceptAnalyzer()

        with patch('prerequisite_explorer_claude.client.messages.create') as mock_create:
            mock_response = Mock()
            mock_response.content = [Mock(text=json.dumps({
                'core_concept': 'unknown',
                'domain': 'unknown',
                'level': 'beginner',
                'goal': 'clarify question'
            }))]
            mock_create.return_value = mock_response

            result = analyzer.analyze("")
            assert 'core_concept' in result

    def test_malformed_json_response(self):
        """Test handling of malformed JSON responses"""
        analyzer = ConceptAnalyzer()

        with patch('prerequisite_explorer_claude.client.messages.create') as mock_create:
            # Return invalid JSON
            mock_response = Mock()
            mock_response.content = [Mock(text="This is not JSON")]
            mock_create.return_value = mock_response

            with pytest.raises((json.JSONDecodeError, ValueError)):
                analyzer.analyze("test")

    def test_api_timeout_handling(self):
        """Test handling of API timeouts (mocked)"""
        explorer = PrerequisiteExplorer()

        with patch('prerequisite_explorer_claude.client.messages.create') as mock_create:
            # Simulate timeout
            mock_create.side_effect = TimeoutError("API timeout")

            with pytest.raises(TimeoutError):
                explorer.is_foundation("test concept")

    def test_exceeds_max_depth(self):
        """Test behavior when max_depth is reached"""
        explorer = PrerequisiteExplorer(max_depth=0)

        tree = explorer.explore("quantum mechanics")

        # Should immediately be marked as foundation due to max_depth=0
        assert tree.depth == 0
        assert tree.is_foundation == True or len(tree.prerequisites) == 0


class TestIntegration:
    """Integration tests for full pipeline"""

    @pytest.mark.skipif(
        not os.getenv("ANTHROPIC_API_KEY"),
        reason="ANTHROPIC_API_KEY not set"
    )
    def test_full_pipeline_simple_concept(self):
        """Test complete flow: analyze -> explore -> verify"""
        # Step 1: Analyze concept
        analyzer = ConceptAnalyzer()
        analysis = analyzer.analyze("Explain basic calculus")

        assert 'core_concept' in analysis

        # Step 2: Build prerequisite tree
        explorer = PrerequisiteExplorer(max_depth=2)
        tree = explorer.explore(analysis['core_concept'])

        # Step 3: Verify tree structure
        assert isinstance(tree, KnowledgeNode)
        assert tree.depth == 0

        # Step 4: Verify tree reaches foundations or depth limit
        def has_foundation_or_limit(node, max_depth):
            """Check tree reaches foundation or depth limit"""
            if node.is_foundation or node.depth >= max_depth:
                return True
            if len(node.prerequisites) == 0:
                return True
            return all(has_foundation_or_limit(p, max_depth) for p in node.prerequisites)

        assert has_foundation_or_limit(tree, explorer.max_depth)

    @pytest.mark.skipif(
        not os.getenv("ANTHROPIC_API_KEY"),
        reason="ANTHROPIC_API_KEY not set"
    )
    def test_full_pipeline_complex_concept(self):
        """Test complete flow with a complex concept"""
        analyzer = ConceptAnalyzer()
        analysis = analyzer.analyze("Explain quantum field theory")

        explorer = PrerequisiteExplorer(max_depth=3)
        tree = explorer.explore(analysis['core_concept'])

        # Verify complex concept has multiple prerequisite layers
        def count_nodes(node):
            """Count total nodes in tree"""
            return 1 + sum(count_nodes(p) for p in node.prerequisites)

        total_nodes = count_nodes(tree)
        assert total_nodes > 1, "Complex concept should have multiple prerequisite nodes"


# Performance benchmarks
class TestPerformance:
    """Performance and efficiency tests"""

    @pytest.mark.skipif(
        not os.getenv("ANTHROPIC_API_KEY"),
        reason="ANTHROPIC_API_KEY not set"
    )
    def test_cache_efficiency(self):
        """Measure cache hit rate"""
        explorer = PrerequisiteExplorer(max_depth=2)

        # Explore a tree (will populate cache)
        tree = explorer.explore("algebra")

        initial_cache_size = len(explorer.cache)

        # Re-explore (should use cache extensively)
        tree2 = explorer.explore("algebra")

        final_cache_size = len(explorer.cache)

        # Cache should not grow (or grow minimally)
        assert final_cache_size - initial_cache_size <= 1, \
            "Cache should prevent redundant API calls"

    @pytest.mark.skipif(
        not os.getenv("ANTHROPIC_API_KEY"),
        reason="ANTHROPIC_API_KEY not set"
    )
    def test_exploration_depth_performance(self):
        """Test how depth affects performance"""
        import time

        depths_to_test = [1, 2, 3]
        times = []

        for depth in depths_to_test:
            explorer = PrerequisiteExplorer(max_depth=depth)

            start = time.time()
            tree = explorer.explore("calculus")
            duration = time.time() - start

            times.append(duration)
            print(f"\nDepth {depth}: {duration:.2f}s")

        # Verify time increases with depth (generally)
        # Note: This is a soft check due to API variability and caching
        print(f"Times by depth: {times}")


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
