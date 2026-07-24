from importlib.metadata import version

from m2m2_visual_improvement import ENVIRONMENT_ID, SCHEMA_VERSION


def test_package_contract_is_versioned() -> None:
    assert ENVIRONMENT_ID == "harleycooper/math-to-manim-visual-improvement"
    assert SCHEMA_VERSION == "m2m2.visual_revision.v1"
    assert version("m2m2-visual-improvement") == "0.1.0"
