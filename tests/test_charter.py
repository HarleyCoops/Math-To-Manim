"""Unit tests for mythos.charter parsing utilities."""

import pytest

from mythos.charter import (
    CINEMATIC_CHARTER,
    extract_json_object,
    extract_python_block,
    find_scene_class,
)


def test_charter_mentions_core_rules():
    assert "CAMERA IS THE NARRATOR" in CINEMATIC_CHARTER
    assert "HEADLINE BEFORE SYMBOLS" in CINEMATIC_CHARTER
    assert "#0c0c0b" in CINEMATIC_CHARTER


def test_extract_json_object_plain():
    assert extract_json_object('{"a": 1}') == {"a": 1}


def test_extract_json_object_with_prose_and_fences():
    text = 'Here you go:\n```json\n{"a": {"b": [1, 2]}, "s": "x{y}"}\n```'
    assert extract_json_object(text) == {"a": {"b": [1, 2]}, "s": "x{y}"}


def test_extract_json_object_nested_braces_in_strings():
    text = '{"latex": "\\\\frac{a}{b}", "n": 2}'
    assert extract_json_object(text)["n"] == 2


def test_extract_json_object_no_json_raises():
    with pytest.raises(RuntimeError):
        extract_json_object("no json here")


def test_extract_python_block_fenced():
    code = extract_python_block("```python\nfrom manim import *\n```")
    assert code.startswith("from manim import *")


def test_extract_python_block_bare_module():
    code = extract_python_block("from manim import *\nx = 1")
    assert "x = 1" in code


def test_extract_python_block_missing_raises():
    with pytest.raises(RuntimeError):
        extract_python_block("just prose, no code")


def test_find_scene_class():
    code = "from manim import *\nclass MyFilm(ThreeDScene):\n    pass\n"
    assert find_scene_class(code) == "MyFilm"


def test_find_scene_class_missing_raises():
    with pytest.raises(RuntimeError):
        find_scene_class("x = 1")
