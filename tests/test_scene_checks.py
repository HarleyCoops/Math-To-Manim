"""WAR-1527 / WAR-1528 / WAR-1529: real LaTeX parser and AST scene checks."""

from __future__ import annotations

import pytest

from mythos.charter import find_scene_class
from mythos.scene_checks import (
    iter_known_scene_bases,
    validate_latex_report,
    validate_manim_code_report,
)

GOOD_LATEX = [
    r"x^2 + y^2 = z^2",
    r"\frac{a}{b}",
    r"\sqrt{x+1}",
    r"\begin{pmatrix} a \\ b \end{pmatrix}",
    r"\sum_{n=1}^{\infty} \frac{1}{n^2}",
    r"e^{i\pi}+1=0",
    r"\int_0^1 x\,dx",
    r"\mathbf{F} = m\mathbf{a}",
    r"\frac{\partial u}{\partial t} = \kappa \frac{\partial^2 u}{\partial x^2}",
    r"\alpha,\beta,\gamma \in \mathbb{R}",
    r"\nabla_{\dot\gamma}\dot\gamma = 0",
]

BAD_LATEX = [
    r"\frac{a",
    r"\frac{}{b}",
    r"\begin{align} x \end{pmatrix}",
    r"\begin{align} x",
    r"a^{b",
    r"\frac{a}{b}}",
    r"\end{align}",
    r"{a",
    r"\sqrt",
    r"\binom{n}",
]


def _scene(body: str, base: str = "ThreeDScene") -> str:
    return (
        "from manim import *\n\n"
        f"class Demo({base}):\n"
        "    def construct(self):\n"
        f"{body}"
    )


def test_latex_accepts_known_good_mathtex_subset():
    for sample in GOOD_LATEX:
        report = validate_latex_report(sample)
        assert report.valid, (sample, report.errors)


def test_latex_rejects_known_bad_samples_with_line_numbers():
    for sample in BAD_LATEX:
        report = validate_latex_report(sample)
        assert report.valid is False, sample
        assert report.errors
        assert all(": " in item for item in report.errors)


def test_latex_report_keeps_legacy_json_shape():
    report = validate_latex_report(r"\frac{a}{b}").to_dict()
    assert set(report) >= {"valid", "errors", "warnings"}
    assert report["valid"] is True
    assert report["errors"] == []


@pytest.mark.parametrize("base", list(iter_known_scene_bases()))
def test_scene_base_is_accepted(base: str):
    source = _scene("        self.wait(0.1)\n", base=base)
    report = validate_manim_code_report(source)
    assert report.valid, (base, report.errors)
    assert report.scene_names == ["Demo"]
    assert find_scene_class(source) == "Demo"


def test_attribute_scene_base_is_accepted():
    source = (
        "import manim\n"
        "class Orbit(manim.ThreeDScene):\n"
        "    def construct(self):\n"
        "        self.wait(0.1)\n"
    )
    assert validate_manim_code_report(source).valid is True
    assert find_scene_class(source) == "Orbit"


def test_no_scene_subclass_is_an_error():
    report = validate_manim_code_report("from manim import *\nclass Helper:\n    pass\n")
    assert report.valid is False
    assert any("Scene subclass" in item for item in report.errors)


def test_raw_mathtex_does_not_suggest_raw_strings():
    source = _scene('        eq = MathTex(r"\\frac{a}{b}")\n        self.play(FadeIn(eq))\n')
    report = validate_manim_code_report(source)
    assert report.valid is True
    assert report.suggestions == []


def test_non_raw_mathtex_suggests_raw_string_with_line_number():
    source = _scene('        eq = MathTex("a^2")\n        other = MathTex(r"b^2")\n')
    report = validate_manim_code_report(source)
    assert any("Prefer raw strings for MathTex content." in item for item in report.suggestions)
    assert any(item.startswith("L") for item in report.suggestions)


def test_fstring_mathtex_is_not_flagged():
    source = _scene("        piece = r'x'\n        eq = MathTex(f'{piece}^2')\n")
    report = validate_manim_code_report(source)
    assert report.suggestions == []


def test_lualatex_fallback_stays_quiet_unless_enabled(monkeypatch):
    monkeypatch.delenv("M2M_LATEX_DEEP_CHECK", raising=False)
    report = validate_latex_report(r"\frac{a}{b}")
    assert report.valid is True
    assert not any("lualatex" in item for item in report.warnings)


def test_lualatex_fallback_records_compile_failure(monkeypatch):
    from types import SimpleNamespace

    from mythos import scene_checks

    monkeypatch.setenv("M2M_LATEX_DEEP_CHECK", "1")
    monkeypatch.setattr(scene_checks.shutil, "which", lambda name: "/usr/bin/lualatex")

    def fake_run(*args, **kwargs):
        return SimpleNamespace(returncode=1, stdout="! Missing $ inserted.\n", stderr="")

    monkeypatch.setattr(scene_checks.subprocess, "run", fake_run)
    report = validate_latex_report(r"\frac{a}{b}")
    assert any("lualatex" in item for item in report.warnings)
