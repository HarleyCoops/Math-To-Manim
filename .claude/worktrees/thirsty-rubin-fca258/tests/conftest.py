"""Pytest configuration and shared fixtures for Math-To-Manim tests."""

import os
import sys

import pytest
from dotenv import load_dotenv

load_dotenv()

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "slow: marks tests as slow")
    config.addinivalue_line("markers", "integration: integration tests")
    config.addinivalue_line("markers", "live: tests requiring live API calls")
    config.addinivalue_line("markers", "unit: unit tests with mocks")


@pytest.fixture(scope="session")
def api_key():
    """Provide API key, skip if not set."""
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        pytest.skip("ANTHROPIC_API_KEY not set")
    return key


@pytest.fixture
def sample_concepts():
    """Sample concepts organized by difficulty."""
    return {
        "basic": ["addition", "velocity", "distance"],
        "intermediate": ["calculus", "linear algebra", "trigonometry"],
        "advanced": ["quantum field theory", "differential geometry", "topology"],
    }


@pytest.fixture
def mock_analysis_result():
    """Mock concept analysis output."""
    return {
        "core_concept": "quantum mechanics",
        "domain": "physics",
        "level": "intermediate",
        "goal": "Understand quantum mechanical principles",
    }
