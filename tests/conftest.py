import os
import sys
import tempfile
import shutil
from pathlib import Path
from typing import Generator, Any
from unittest.mock import Mock, patch

import pytest
from manim import config as manim_config


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test files."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def temp_media_dir(temp_dir: Path) -> Path:
    """Create a temporary media directory for Manim outputs."""
    media_dir = temp_dir / "media"
    media_dir.mkdir(exist_ok=True)
    return media_dir


@pytest.fixture
def mock_manim_config(temp_media_dir: Path) -> Generator[None, None, None]:
    """Mock Manim configuration for testing."""
    original_config = {
        "media_dir": manim_config.media_dir,
        "video_dir": manim_config.video_dir,
        "images_dir": manim_config.images_dir,
        "tex_dir": manim_config.tex_dir,
        "log_dir": manim_config.log_dir,
    }
    
    manim_config.media_dir = str(temp_media_dir)
    manim_config.video_dir = str(temp_media_dir / "videos")
    manim_config.images_dir = str(temp_media_dir / "images")
    manim_config.tex_dir = str(temp_media_dir / "tex")
    manim_config.log_dir = str(temp_media_dir / "logs")
    
    yield
    
    for key, value in original_config.items():
        setattr(manim_config, key, value)


@pytest.fixture
def mock_openai_client() -> Mock:
    """Mock OpenAI client for testing AI integrations."""
    mock_client = Mock()
    mock_response = Mock()
    mock_response.choices = [Mock(message=Mock(content="Test response"))]
    mock_client.chat.completions.create.return_value = mock_response
    return mock_client


@pytest.fixture
def mock_gradio_interface() -> Mock:
    """Mock Gradio interface for testing web UI."""
    mock_interface = Mock()
    mock_interface.launch.return_value = None
    return mock_interface


@pytest.fixture
def sample_math_expression() -> str:
    """Sample mathematical expression for testing."""
    return "f(x) = x^2 + 2x + 1"


@pytest.fixture
def sample_manim_code() -> str:
    """Sample Manim code for testing."""
    return '''
from manim import *

class TestScene(Scene):
    def construct(self):
        text = Text("Hello, Manim!")
        self.play(Write(text))
        self.wait()
'''


@pytest.fixture
def mock_env_vars() -> Generator[None, None, None]:
    """Mock environment variables for testing."""
    env_vars = {
        "OPENAI_API_KEY": "test-api-key",
        "DEEPSEEK_API_KEY": "test-deepseek-key",
        "GEMINI_API_KEY": "test-gemini-key",
    }
    
    with patch.dict(os.environ, env_vars):
        yield


@pytest.fixture
def capture_logs(caplog: pytest.LogCaptureFixture) -> pytest.LogCaptureFixture:
    """Capture log messages during tests."""
    caplog.set_level("DEBUG")
    return caplog


@pytest.fixture(autouse=True)
def reset_matplotlib():
    """Reset matplotlib state between tests."""
    import matplotlib.pyplot as plt
    plt.close('all')
    yield
    plt.close('all')


@pytest.fixture
def mock_torch_cuda() -> Generator[None, None, None]:
    """Mock torch CUDA availability for testing."""
    with patch("torch.cuda.is_available", return_value=False):
        yield


@pytest.fixture
def sample_config_dict() -> dict[str, Any]:
    """Sample configuration dictionary for testing."""
    return {
        "model": "gpt-4",
        "temperature": 0.7,
        "max_tokens": 1000,
        "animation_quality": "high",
        "output_format": "mp4",
    }


@pytest.fixture
def mock_file_system(tmp_path: Path) -> Path:
    """Create a mock file system structure for testing."""
    scripts_dir = tmp_path / "Scripts"
    scripts_dir.mkdir()
    
    (scripts_dir / "__init__.py").touch()
    (scripts_dir / "example.py").write_text("# Example script")
    
    examples_dir = scripts_dir / "examples"
    examples_dir.mkdir()
    (examples_dir / "basic.py").write_text("# Basic example")
    
    return tmp_path


@pytest.fixture(scope="session")
def pytest_config() -> dict[str, Any]:
    """Pytest configuration for the session."""
    return {
        "markers": {
            "unit": "Unit tests",
            "integration": "Integration tests",
            "slow": "Slow running tests",
        },
        "test_timeout": 300,
        "asyncio_mode": "auto",
    }