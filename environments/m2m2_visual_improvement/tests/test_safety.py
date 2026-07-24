from __future__ import annotations

import pytest

from m2m2_visual_improvement.micro_scenes import BASE_SCENES
from m2m2_visual_improvement.safety import (
    CandidateSafetyError,
    assert_safe_candidate,
    validate_candidate_source,
)


SAFE_SCENE = """
from manim import *

class Lesson(Scene):
    def construct(self):
        title = Text("Visible lesson")
        self.play(Write(title))
"""


def violation_codes(code: str, scene_name: str = "Lesson", **limits: int) -> set[str]:
    return {
        violation.code
        for violation in validate_candidate_source(
            code,
            expected_scene_name=scene_name,
            **limits,
        ).violations
    }


def test_rejects_syntax_errors() -> None:
    assert "syntax_error" in violation_codes("class Lesson(:\n")


@pytest.mark.parametrize(
    ("source", "expected_code"),
    [
        ("import os\n" + SAFE_SCENE, "unsafe_import"),
        ("import subprocess\n" + SAFE_SCENE, "unsafe_import"),
        ("import socket\n" + SAFE_SCENE, "unsafe_import"),
        ("import pickle\n" + SAFE_SCENE, "unsafe_import"),
        (SAFE_SCENE.replace('title = Text("Visible lesson")', 'title = open("x")'), "unsafe_call"),
        (SAFE_SCENE.replace('title = Text("Visible lesson")', 'title = eval("1+1")'), "unsafe_call"),
        (SAFE_SCENE.replace('title = Text("Visible lesson")', 'title = exec("pass")'), "unsafe_call"),
        (
            SAFE_SCENE.replace(
                'title = Text("Visible lesson")',
                'title = __import__("os")',
            ),
            "unsafe_call",
        ),
    ],
)
def test_rejects_unsafe_imports_and_calls(
    source: str,
    expected_code: str,
) -> None:
    assert expected_code in violation_codes(source)


def test_rejects_missing_expected_scene_or_construct() -> None:
    assert "missing_scene" in violation_codes(
        "from manim import *\nclass Other(Scene):\n    pass\n"
    )
    assert "missing_construct" in violation_codes(
        "from manim import *\nclass Lesson(Scene):\n    pass\n"
    )


def test_rejects_camera_animate_in_three_d_scene() -> None:
    source = """
from manim import *

class Lesson(ThreeDScene):
    def construct(self):
        self.play(self.camera.animate.set_phi(1))
"""
    assert "three_d_camera_animate" in violation_codes(source)


def test_rejects_source_and_ast_over_limits() -> None:
    assert "source_too_large" in violation_codes(
        SAFE_SCENE,
        max_bytes=10,
    )
    many_nodes = SAFE_SCENE.replace(
        'title = Text("Visible lesson")',
        "\n        ".join(f"value_{index} = {index}" for index in range(100)),
    )
    assert "ast_too_large" in violation_codes(many_nodes, max_nodes=20)


def test_accepts_normal_manim_and_all_committed_micro_scenes() -> None:
    assert validate_candidate_source(
        SAFE_SCENE,
        expected_scene_name="Lesson",
    ).valid
    for scene in BASE_SCENES.values():
        report = validate_candidate_source(
            scene.code,
            expected_scene_name=scene.scene_name,
        )
        assert report.valid, (scene.base_scene_id, report.violations)


def test_assertion_api_returns_source_or_raises_typed_error() -> None:
    assert assert_safe_candidate(
        SAFE_SCENE,
        expected_scene_name="Lesson",
    ) == SAFE_SCENE
    with pytest.raises(CandidateSafetyError, match="unsafe_import"):
        assert_safe_candidate(
            "import os\n" + SAFE_SCENE,
            expected_scene_name="Lesson",
        )
