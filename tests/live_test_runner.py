"""
Live Test Runner for Math-To-Manim Agents

Runs real-time tests against the actual Claude API and provides
detailed reports on agent behavior, performance, and correctness.

Usage:
    python tests/live_test_runner.py
    python tests/live_test_runner.py --concept "cosmology"
    python tests/live_test_runner.py --suite performance
"""

import sys
import os
import time
import json
import asyncio
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from dotenv import load_dotenv

# Add src/agents directory to path for imports
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(project_root, 'src', 'agents'))

from prerequisite_explorer_claude import (
    ConceptAnalyzer,
    PrerequisiteExplorer,
    KnowledgeNode
)

load_dotenv()


@dataclass
class TestResult:
    """Result of a single test"""
    test_name: str
    status: str  # 'PASS', 'FAIL', 'SKIP', 'ERROR'
    duration_ms: float
    message: str
    details: Optional[Dict] = None


@dataclass
class TestSuite:
    """Collection of test results"""
    suite_name: str
    start_time: str
    end_time: str
    total_duration_ms: float
    results: List[TestResult]

    @property
    def passed(self):
        return sum(1 for r in self.results if r.status == 'PASS')

    @property
    def failed(self):
        return sum(1 for r in self.results if r.status == 'FAIL')

    @property
    def skipped(self):
        return sum(1 for r in self.results if r.status == 'SKIP')

    @property
    def errors(self):
        return sum(1 for r in self.results if r.status == 'ERROR')


class LiveTestRunner:
    """
    Runs live tests against the agents and reports results.
    """

    def __init__(self, verbose=True):
        self.verbose = verbose
        self.results: List[TestResult] = []

    def run_test(self, test_name: str, test_func, *args, **kwargs) -> TestResult:
        """
        Run a single test and record the result.
        """
        if self.verbose:
            print(f"\n{'='*80}")
            print(f"Running: {test_name}")
            print(f"{'='*80}")

        start_time = time.time()

        try:
            # Run the test
            result = test_func(*args, **kwargs)
            duration = (time.time() - start_time) * 1000

            # Determine status
            if result is True:
                status = 'PASS'
                message = "Test passed"
            elif result is False:
                status = 'FAIL'
                message = "Test failed"
            elif isinstance(result, dict):
                status = result.get('status', 'PASS')
                message = result.get('message', 'Test completed')
                details = result.get('details')
            else:
                status = 'PASS'
                message = f"Test completed: {result}"
                details = None

            test_result = TestResult(
                test_name=test_name,
                status=status,
                duration_ms=duration,
                message=message,
                details=details if isinstance(result, dict) else None
            )

        except Exception as e:
            duration = (time.time() - start_time) * 1000
            test_result = TestResult(
                test_name=test_name,
                status='ERROR',
                duration_ms=duration,
                message=f"Exception: {str(e)}",
                details={'exception_type': type(e).__name__}
            )

        # Print result
        if self.verbose:
            self._print_result(test_result)

        self.results.append(test_result)
        return test_result

    def _print_result(self, result: TestResult):
        """Pretty print a test result"""
        # Use simple text symbols for Windows compatibility
        status_symbol = {
            'PASS': '[PASS]',
            'FAIL': '[FAIL]',
            'SKIP': '[SKIP]',
            'ERROR': '[ERROR]'
        }

        symbol = status_symbol.get(result.status, '[?]')
        print(f"\n{symbol} {result.test_name}")
        print(f"   Duration: {result.duration_ms:.2f}ms")
        print(f"   Message: {result.message}")

        if result.details:
            print(f"   Details: {json.dumps(result.details, indent=6)}")

    def print_summary(self):
        """Print summary of all test results"""
        if not self.results:
            print("\nNo tests run.")
            return

        passed = sum(1 for r in self.results if r.status == 'PASS')
        failed = sum(1 for r in self.results if r.status == 'FAIL')
        skipped = sum(1 for r in self.results if r.status == 'SKIP')
        errors = sum(1 for r in self.results if r.status == 'ERROR')
        total_time = sum(r.duration_ms for r in self.results)

        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        print(f"Total Tests: {len(self.results)}")
        print(f"Passed:  {passed}")
        print(f"Failed:  {failed}")
        print(f"Skipped: {skipped}")
        print(f"Errors:  {errors}")
        print(f"Total Time: {total_time:.2f}ms ({total_time/1000:.2f}s)")
        print("="*80)

        # List failures/errors
        failures = [r for r in self.results if r.status in ['FAIL', 'ERROR']]
        if failures:
            print("\nFailed/Error Tests:")
            for result in failures:
                print(f"  - {result.test_name}: {result.message}")


# Test implementations
class ConceptAnalyzerTests:
    """Live tests for ConceptAnalyzer"""

    @staticmethod
    def test_analyze_physics_concept():
        """Test analyzing a physics concept"""
        analyzer = ConceptAnalyzer()
        result = analyzer.analyze("Explain special relativity")

        # Validate
        assert 'core_concept' in result
        assert 'relativity' in result['core_concept'].lower()
        assert result['level'] in ['beginner', 'intermediate', 'advanced']

        return {
            'status': 'PASS',
            'message': 'Successfully analyzed physics concept',
            'details': result
        }

    @staticmethod
    def test_analyze_math_concept():
        """Test analyzing a math concept"""
        analyzer = ConceptAnalyzer()
        result = analyzer.analyze("Teach me about calculus")

        assert 'core_concept' in result
        assert 'calculus' in result['core_concept'].lower()

        return {
            'status': 'PASS',
            'message': 'Successfully analyzed math concept',
            'details': result
        }

    @staticmethod
    def test_analyze_cs_concept():
        """Test analyzing a computer science concept"""
        analyzer = ConceptAnalyzer()
        result = analyzer.analyze("How do neural networks work?")

        assert 'core_concept' in result
        assert 'neural' in result['core_concept'].lower() or 'network' in result['core_concept'].lower()

        return {
            'status': 'PASS',
            'message': 'Successfully analyzed CS concept',
            'details': result
        }


class PrerequisiteExplorerTests:
    """Live tests for PrerequisiteExplorer"""

    @staticmethod
    def test_foundation_detection():
        """Test foundation concept detection"""
        explorer = PrerequisiteExplorer()

        # Test basic concepts
        basic_results = []
        for concept in ["addition", "velocity", "distance"]:
            is_found = explorer.is_foundation(concept)
            basic_results.append((concept, is_found))

        # Test advanced concepts
        advanced_results = []
        for concept in ["quantum field theory", "differential geometry"]:
            is_found = explorer.is_foundation(concept)
            advanced_results.append((concept, is_found))

        # Validate
        basic_correct = all(is_found for _, is_found in basic_results)
        advanced_correct = all(not is_found for _, is_found in advanced_results)

        if basic_correct and advanced_correct:
            return {
                'status': 'PASS',
                'message': 'Foundation detection working correctly',
                'details': {
                    'basic_concepts': basic_results,
                    'advanced_concepts': advanced_results
                }
            }
        else:
            return {
                'status': 'FAIL',
                'message': 'Foundation detection has errors',
                'details': {
                    'basic_concepts': basic_results,
                    'advanced_concepts': advanced_results
                }
            }

    @staticmethod
    def test_prerequisite_discovery():
        """Test prerequisite discovery"""
        explorer = PrerequisiteExplorer()
        prereqs = explorer.discover_prerequisites("calculus")

        # Validate
        assert isinstance(prereqs, list)
        assert len(prereqs) > 0
        assert len(prereqs) <= 5
        assert all(isinstance(p, str) for p in prereqs)

        return {
            'status': 'PASS',
            'message': f'Found {len(prereqs)} prerequisites',
            'details': {'prerequisites': prereqs}
        }

    @staticmethod
    def test_tree_building():
        """Test building a complete knowledge tree"""
        explorer = PrerequisiteExplorer(max_depth=2)
        tree = explorer.explore("linear algebra")

        # Validate structure
        assert isinstance(tree, KnowledgeNode)
        assert tree.depth == 0

        # Count nodes
        def count_nodes(node):
            return 1 + sum(count_nodes(p) for p in node.prerequisites)

        total_nodes = count_nodes(tree)

        return {
            'status': 'PASS',
            'message': f'Built tree with {total_nodes} nodes',
            'details': {
                'root_concept': tree.concept,
                'total_nodes': total_nodes,
                'max_depth': explorer.max_depth,
                'is_foundation': tree.is_foundation
            }
        }

    @staticmethod
    def test_caching():
        """Test caching mechanism"""
        explorer = PrerequisiteExplorer(max_depth=2)

        # First call
        start1 = time.time()
        prereqs1 = explorer.discover_prerequisites("algebra")
        time1 = (time.time() - start1) * 1000

        # Second call (should be cached)
        start2 = time.time()
        prereqs2 = explorer.discover_prerequisites("algebra")
        time2 = (time.time() - start2) * 1000

        # Validate
        assert prereqs1 == prereqs2
        assert "algebra" in explorer.cache

        # Second call should be much faster (cached)
        speedup = time1 / max(time2, 0.001)  # Avoid division by zero

        return {
            'status': 'PASS',
            'message': f'Caching working (speedup: {speedup:.1f}x)',
            'details': {
                'first_call_ms': time1,
                'second_call_ms': time2,
                'speedup': speedup,
                'cache_size': len(explorer.cache)
            }
        }


class PerformanceTests:
    """Performance and efficiency tests"""

    @staticmethod
    def test_analysis_performance():
        """Measure analysis performance"""
        analyzer = ConceptAnalyzer()

        concepts = [
            "quantum mechanics",
            "calculus",
            "machine learning"
        ]

        times = []
        for concept in concepts:
            start = time.time()
            analyzer.analyze(f"Explain {concept}")
            duration = (time.time() - start) * 1000
            times.append(duration)

        avg_time = sum(times) / len(times)

        return {
            'status': 'PASS',
            'message': f'Average analysis time: {avg_time:.2f}ms',
            'details': {
                'times_ms': times,
                'average_ms': avg_time,
                'min_ms': min(times),
                'max_ms': max(times)
            }
        }

    @staticmethod
    def test_exploration_depth_scaling():
        """Test how performance scales with depth"""
        depths = [1, 2, 3]
        results = []

        for depth in depths:
            explorer = PrerequisiteExplorer(max_depth=depth)

            start = time.time()
            tree = explorer.explore("calculus")
            duration = (time.time() - start) * 1000

            # Count nodes
            def count_nodes(node):
                return 1 + sum(count_nodes(p) for p in node.prerequisites)

            node_count = count_nodes(tree)

            results.append({
                'depth': depth,
                'duration_ms': duration,
                'nodes': node_count,
                'ms_per_node': duration / max(node_count, 1)
            })

        return {
            'status': 'PASS',
            'message': 'Depth scaling test completed',
            'details': {'results_by_depth': results}
        }


def run_test_suite(suite_name: str, test_class):
    """Run all tests in a test class"""
    runner = LiveTestRunner(verbose=True)

    start_time = datetime.now()

    # Get all test methods
    test_methods = [
        getattr(test_class, method)
        for method in dir(test_class)
        if method.startswith('test_')
    ]

    # Run each test
    for test_method in test_methods:
        runner.run_test(
            test_name=f"{test_class.__name__}.{test_method.__name__}",
            test_func=test_method
        )

    end_time = datetime.now()

    # Print summary
    runner.print_summary()

    # Create test suite object
    suite = TestSuite(
        suite_name=suite_name,
        start_time=start_time.isoformat(),
        end_time=end_time.isoformat(),
        total_duration_ms=(end_time - start_time).total_seconds() * 1000,
        results=runner.results
    )

    return suite


def run_all_suites():
    """Run all test suites"""
    print("""
╔═══════════════════════════════════════════════════════════════════════════╗
║                    LIVE TEST RUNNER - Math-To-Manim                       ║
║                                                                           ║
║  Running real-time tests against Claude API                              ║
║  This will make actual API calls and may incur costs                     ║
╚═══════════════════════════════════════════════════════════════════════════╝
    """)

    suites = []

    # Run ConceptAnalyzer tests
    print("\n" + ">"*40)
    print("SUITE 1: ConceptAnalyzer Tests")
    print(">"*40)
    suite1 = run_test_suite("ConceptAnalyzer", ConceptAnalyzerTests)
    suites.append(suite1)

    # Run PrerequisiteExplorer tests
    print("\n" + ">"*40)
    print("SUITE 2: PrerequisiteExplorer Tests")
    print(">"*40)
    suite2 = run_test_suite("PrerequisiteExplorer", PrerequisiteExplorerTests)
    suites.append(suite2)

    # Run Performance tests
    print("\n" + ">"*40)
    print("SUITE 3: Performance Tests")
    print(">"*40)
    suite3 = run_test_suite("Performance", PerformanceTests)
    suites.append(suite3)

    # Overall summary
    print("\n" + "="*80)
    print("OVERALL SUMMARY")
    print("="*80)

    total_tests = sum(len(s.results) for s in suites)
    total_passed = sum(s.passed for s in suites)
    total_failed = sum(s.failed for s in suites)
    total_errors = sum(s.errors for s in suites)

    print(f"Total Suites: {len(suites)}")
    print(f"Total Tests: {total_tests}")
    print(f"[DONE] Passed: {total_passed}")
    print(f"[FAIL] Failed: {total_failed}")
    print(f"[ERROR] Errors: {total_errors}")

    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"test_results_{timestamp}.json"

    with open(output_file, 'w') as f:
        json.dump([asdict(s) for s in suites], f, indent=2)

    print(f"\n[OK] Results saved to: {output_file}")
    print("="*80)

    return suites


def test_specific_concept(concept: str):
    """Test the system with a specific concept"""
    print(f"\n{'='*80}")
    print(f"TESTING CONCEPT: {concept}")
    print(f"{'='*80}\n")

    runner = LiveTestRunner(verbose=True)

    # Test 1: Analyze
    def analyze_test():
        analyzer = ConceptAnalyzer()
        result = analyzer.analyze(f"Explain {concept}")
        return {'status': 'PASS', 'message': 'Analysis complete', 'details': result}

    runner.run_test(f"Analyze: {concept}", analyze_test)

    # Test 2: Build tree
    def tree_test():
        explorer = PrerequisiteExplorer(max_depth=3)
        tree = explorer.explore(concept)

        def count_nodes(node):
            return 1 + sum(count_nodes(p) for p in node.prerequisites)

        return {
            'status': 'PASS',
            'message': f'Tree built with {count_nodes(tree)} nodes',
            'details': tree.to_dict()
        }

    runner.run_test(f"Build Tree: {concept}", tree_test)

    runner.print_summary()


if __name__ == "__main__":
    # Check API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("[FAIL] Error: ANTHROPIC_API_KEY not set")
        print("\nSet your API key in .env file:")
        print("  ANTHROPIC_API_KEY=your_key_here")
        sys.exit(1)

    # Parse command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--concept":
            concept = sys.argv[2] if len(sys.argv) > 2 else "quantum mechanics"
            test_specific_concept(concept)
        elif sys.argv[1] == "--suite":
            suite_name = sys.argv[2] if len(sys.argv) > 2 else "all"
            if suite_name == "analyzer":
                run_test_suite("ConceptAnalyzer", ConceptAnalyzerTests)
            elif suite_name == "explorer":
                run_test_suite("PrerequisiteExplorer", PrerequisiteExplorerTests)
            elif suite_name == "performance":
                run_test_suite("Performance", PerformanceTests)
            else:
                run_all_suites()
        else:
            print("Usage:")
            print("  python tests/live_test_runner.py")
            print("  python tests/live_test_runner.py --concept 'cosmology'")
            print("  python tests/live_test_runner.py --suite [analyzer|explorer|performance|all]")
    else:
        run_all_suites()
