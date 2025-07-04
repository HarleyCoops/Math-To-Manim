"""Unit tests for verifying Script imports and basic structure."""

import pytest
import importlib.util
import inspect
from pathlib import Path
import sys


class TestSceneImports:
    """Test that animation scripts can be imported successfully."""
    
    @pytest.fixture
    def scripts_directory(self):
        """Get the Scripts directory path."""
        return Path(__file__).parent.parent.parent / "Scripts"
    
    @pytest.fixture
    def sample_script_files(self, scripts_directory):
        """Get a sample of script files for testing."""
        all_scripts = list(scripts_directory.glob("*.py"))
        # Test a subset to keep tests fast, but ensure we test variety
        sample_scripts = [
            "QED.py",
            "ElectroweakSymmetryScene.py",
            "CosmicProbabilityScene.py",
            "fractal_scene.py",
            "pythagorean.py"
        ]
        return [scripts_directory / script for script in sample_scripts if (scripts_directory / script).exists()]
    
    @pytest.mark.unit
    def test_scripts_directory_exists(self, scripts_directory):
        """Test that the Scripts directory exists."""
        assert scripts_directory.exists(), "Scripts directory not found"
        assert scripts_directory.is_dir(), "Scripts is not a directory"
    
    @pytest.mark.unit
    def test_scripts_directory_has_files(self, scripts_directory):
        """Test that Scripts directory contains Python files."""
        py_files = list(scripts_directory.glob("*.py"))
        assert len(py_files) > 0, "No Python files found in Scripts directory"
    
    @pytest.mark.unit
    @pytest.mark.parametrize("script_name", [
        "QED.py",
        "ElectroweakSymmetryScene.py",
        "CosmicProbabilityScene.py",
        "fractal_scene.py",
        "pythagorean.py"
    ])
    def test_individual_script_imports(self, scripts_directory, script_name):
        """Test that individual scripts can be imported without errors."""
        script_path = scripts_directory / script_name
        
        if not script_path.exists():
            pytest.skip(f"Script {script_name} not found")
        
        # Create module spec and load the module
        spec = importlib.util.spec_from_file_location(
            f"test_script_{script_name.replace('.py', '')}", 
            script_path
        )
        module = importlib.util.module_from_spec(spec)
        
        # Add to sys.modules temporarily
        sys.modules[spec.name] = module
        
        try:
            # This will raise ImportError if there are syntax errors or missing imports
            spec.loader.exec_module(module)
        except Exception as e:
            pytest.fail(f"Failed to import {script_name}: {str(e)}")
        finally:
            # Clean up
            if spec.name in sys.modules:
                del sys.modules[spec.name]
    
    @pytest.mark.unit
    def test_scripts_contain_scene_classes(self, sample_script_files):
        """Test that scripts contain at least one Scene class."""
        from manim import Scene
        
        for script_path in sample_script_files:
            spec = importlib.util.spec_from_file_location(
                f"test_script_{script_path.stem}", 
                script_path
            )
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            
            try:
                spec.loader.exec_module(module)
                
                # Find all classes that inherit from Scene
                scene_classes = []
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, Scene) and obj is not Scene:
                        scene_classes.append(name)
                
                assert len(scene_classes) > 0, f"No Scene classes found in {script_path.name}"
                
            except Exception as e:
                pytest.fail(f"Error analyzing {script_path.name}: {str(e)}")
            finally:
                if spec.name in sys.modules:
                    del sys.modules[spec.name]
    
    @pytest.mark.unit
    def test_scripts_have_construct_method(self, sample_script_files):
        """Test that Scene classes have a construct method."""
        from manim import Scene
        
        for script_path in sample_script_files:
            spec = importlib.util.spec_from_file_location(
                f"test_script_{script_path.stem}", 
                script_path
            )
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            
            try:
                spec.loader.exec_module(module)
                
                # Check each Scene class has construct method
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, Scene) and obj is not Scene:
                        assert hasattr(obj, 'construct'), \
                            f"Scene class {name} in {script_path.name} missing construct method"
                        
                        # Verify construct is a method
                        construct = getattr(obj, 'construct')
                        assert callable(construct), \
                            f"construct in {name} ({script_path.name}) is not callable"
                
            except Exception as e:
                pytest.fail(f"Error checking construct methods in {script_path.name}: {str(e)}")
            finally:
                if spec.name in sys.modules:
                    del sys.modules[spec.name]