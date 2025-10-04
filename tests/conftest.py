"""
Pytest configuration and shared fixtures for Math-To-Manim tests.

This file is automatically loaded by pytest and provides
common fixtures and configuration for all test files.
"""

import pytest
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add project root to path so we can import from src
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "live: marks tests that require API calls"
    )


@pytest.fixture(scope="session")
def api_key():
    """Provide API key for tests"""
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        pytest.skip("ANTHROPIC_API_KEY not set")
    return key


@pytest.fixture
def sample_concepts():
    """Provide sample concepts for testing"""
    return {
        'basic': ['addition', 'velocity', 'distance'],
        'intermediate': ['calculus', 'linear algebra', 'trigonometry'],
        'advanced': ['quantum field theory', 'differential geometry', 'topology']
    }


@pytest.fixture
def mock_analysis_result():
    """Provide a mock concept analysis result"""
    return {
        'core_concept': 'quantum mechanics',
        'domain': 'physics',
        'level': 'intermediate',
        'goal': 'Understand quantum mechanical principles'
    }
