"""Unit tests for validating Scene structure and common patterns."""

import pytest
import ast
from pathlib import Path


class TestSceneValidation:
    """Validate that animation scripts follow expected patterns."""
    
    @pytest.fixture
    def scripts_directory(self):
        """Get the Scripts directory path."""
        return Path(__file__).parent.parent.parent / "Scripts"
    
    @pytest.mark.unit
    def test_scripts_import_manim(self, scripts_directory):
        """Test that scripts properly import from manim."""
        script_files = list(scripts_directory.glob("*.py"))[:5]  # Test first 5 files
        
        for script_path in script_files:
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for manim import
            assert 'from manim import' in content or 'import manim' in content, \
                f"{script_path.name} does not import manim"
    
    @pytest.mark.unit
    def test_no_hardcoded_api_keys(self, scripts_directory):
        """Test that scripts don't contain hardcoded API keys."""
        suspicious_patterns = [
            'api_key=',
            'API_KEY=',
            'secret=',
            'SECRET=',
            'token=',
            'TOKEN=',
            'sk-',  # OpenAI key pattern
            'AIza',  # Google API key pattern
        ]
        
        script_files = list(scripts_directory.glob("*.py"))
        
        for script_path in script_files:
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            for pattern in suspicious_patterns:
                if pattern in content:
                    # Check if it's in a comment or docstring
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if pattern in line and not line.strip().startswith('#'):
                            # Could be in docstring, check context
                            if not (i > 0 and '"""' in lines[i-1]):
                                pytest.fail(f"Potential API key found in {script_path.name}: {pattern}")
    
    @pytest.mark.unit
    def test_scene_class_naming_convention(self, scripts_directory):
        """Test that Scene classes follow naming conventions."""
        script_files = list(scripts_directory.glob("*.py"))[:5]
        
        for script_path in script_files:
            with open(script_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check if it's likely a Scene class (basic heuristic)
                    if any(base.id == 'Scene' for base in node.bases if isinstance(base, ast.Name)):
                        # Scene classes should be PascalCase
                        assert node.name[0].isupper(), \
                            f"Scene class {node.name} in {script_path.name} should start with uppercase"
                        
                        # Should not have underscores (PascalCase, not snake_case)
                        if '_' in node.name:
                            pytest.fail(
                                f"Scene class {node.name} in {script_path.name} "
                                "should use PascalCase, not snake_case"
                            )
    
    @pytest.mark.unit
    def test_construct_method_exists_ast(self, scripts_directory):
        """Test construct methods exist using AST parsing."""
        script_files = list(scripts_directory.glob("*.py"))[:5]
        
        for script_path in script_files:
            with open(script_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())
            
            scene_classes = []
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Check if it inherits from Scene
                    for base in node.bases:
                        if isinstance(base, ast.Name) and base.id == 'Scene':
                            scene_classes.append(node)
                            break
            
            # Verify each Scene class has construct method
            for class_node in scene_classes:
                has_construct = any(
                    isinstance(node, ast.FunctionDef) and node.name == 'construct'
                    for node in class_node.body
                )
                assert has_construct, \
                    f"Scene class {class_node.name} in {script_path.name} missing construct method"
    
    @pytest.mark.unit 
    def test_common_manim_patterns(self, scripts_directory):
        """Test for common Manim patterns in scripts."""
        # Sample a few scripts
        script_files = [
            scripts_directory / "QED.py",
            scripts_directory / "pythagorean.py",
            scripts_directory / "fractal_scene.py"
        ]
        
        common_patterns = {
            'animations': ['self.play(', 'self.wait(', 'self.add('],
            'objects': ['Text(', 'MathTex(', 'Circle(', 'Square(', 'Line('],
            'transforms': ['Transform(', 'ReplacementTransform(', 'FadeIn(', 'FadeOut(']
        }
        
        for script_path in script_files:
            if not script_path.exists():
                continue
                
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check that at least some common patterns are used
            patterns_found = []
            for category, patterns in common_patterns.items():
                for pattern in patterns:
                    if pattern in content:
                        patterns_found.append(pattern)
            
            assert len(patterns_found) > 0, \
                f"{script_path.name} doesn't use any common Manim patterns"