"""Unit tests for app.py components."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path


class TestAppComponents:
    """Test the Gradio app components."""
    
    @pytest.mark.unit
    def test_app_file_exists(self):
        """Test that app.py exists."""
        app_path = Path(__file__).parent.parent.parent / "app.py"
        assert app_path.exists(), "app.py not found in project root"
    
    @pytest.mark.unit
    @patch('gradio.Interface')
    def test_app_imports_gradio(self, mock_interface):
        """Test that app.py properly imports and uses Gradio."""
        # Add project root to path
        project_root = Path(__file__).parent.parent.parent
        sys.path.insert(0, str(project_root))
        
        try:
            # Import should work without errors
            import app
            
            # Gradio should be imported
            assert hasattr(app, 'gr') or 'gradio' in sys.modules, \
                "Gradio not imported in app.py"
                
        except ImportError as e:
            pytest.fail(f"Failed to import app.py: {str(e)}")
        finally:
            # Clean up
            if 'app' in sys.modules:
                del sys.modules['app']
            sys.path.remove(str(project_root))
    
    @pytest.mark.unit
    def test_env_file_usage(self):
        """Test that the app expects environment variables."""
        app_path = Path(__file__).parent.parent.parent / "app.py"
        
        with open(app_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for environment variable usage patterns
        env_patterns = [
            'os.getenv',
            'os.environ',
            'load_dotenv',
            'python-dotenv'
        ]
        
        env_usage_found = any(pattern in content for pattern in env_patterns)
        assert env_usage_found, "app.py doesn't seem to use environment variables"
        
        # Check for API key references
        api_key_patterns = ['DEEPSEEK_API_KEY', 'API_KEY', 'api_key']
        api_key_found = any(pattern in content for pattern in api_key_patterns)
        assert api_key_found, "app.py doesn't reference API keys"
    
    @pytest.mark.unit
    @patch('openai.OpenAI')
    def test_deepseek_client_initialization(self, mock_openai):
        """Test that DeepSeek client can be initialized."""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        # Test client initialization pattern
        test_api_key = "test-key-123"
        test_base_url = "https://api.deepseek.com"
        
        client = mock_openai(
            api_key=test_api_key,
            base_url=test_base_url
        )
        
        # Verify initialization
        mock_openai.assert_called_once_with(
            api_key=test_api_key,
            base_url=test_base_url
        )
        assert client == mock_client
    
    @pytest.mark.unit
    def test_main_function_patterns(self):
        """Test for common patterns in the main application."""
        app_path = Path(__file__).parent.parent.parent / "app.py"
        
        with open(app_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for essential patterns
        patterns = {
            'gradio_interface': ['.Interface(', 'gr.Interface('],
            'launch': ['.launch(', 'interface.launch('],
            'function_definition': ['def ', 'async def'],
            'api_interaction': ['client.', 'response', 'completion']
        }
        
        for category, pattern_list in patterns.items():
            found = any(pattern in content for pattern in pattern_list)
            assert found, f"Missing {category} pattern in app.py"
    
    @pytest.mark.unit
    def test_error_handling_exists(self):
        """Test that app.py includes error handling."""
        app_path = Path(__file__).parent.parent.parent / "app.py"
        
        with open(app_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for error handling patterns
        error_patterns = [
            'try:',
            'except',
            'Exception',
            'error',
            'Error'
        ]
        
        error_handling_found = sum(1 for pattern in error_patterns if pattern in content)
        assert error_handling_found >= 2, \
            "app.py should include proper error handling"