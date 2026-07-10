import json
import py_compile

import pytest

from sol.client import extract_output_text
from sol.manim import sanitize_latex
from sol.models import CalculationRequest
from sol.offline import UnsupportedCalculation, calculate_locally
from sol.service import SolService


def test_local_arithmetic():
    result = calculate_locally("calculate (12 + 3) * 4")
    assert result.answer == "60"
    assert result.method == "safe arithmetic evaluation"


def test_local_linear_equation():
    result = calculate_locally("solve 3x + 11 = 14")
    assert result.answer == "x = 1"
    assert result.answer_latex == "x=1"


def test_local_quadratic_equation():
    result = calculate_locally("x^2 - 5x + 6 = 0")
    assert result.answer == "x = 2 or 3"


def test_local_engine_rejects_code_execution():
    with pytest.raises(UnsupportedCalculation):
        calculate_locally("__import__('os').system('id')")


def test_scene_compiler_rejects_dangerous_latex():
    with pytest.raises(ValueError):
        sanitize_latex(r"\input{/etc/passwd}")


def test_service_writes_typed_bundle(tmp_path):
    response = SolService(runs_dir=tmp_path).calculate(
        CalculationRequest(problem="solve 3x + 11 = 14", offline=True)
    )
    run_dir = tmp_path / response.run_id
    assert response.engine == "local-symbolic"
    assert json.loads((run_dir / "result.json").read_text())["answer"] == "x = 1"
    py_compile.compile(str(run_dir / "sol_scene.py"), doraise=True)


def test_extract_responses_output_text():
    payload = {"output": [{"type": "message", "content": [{"type": "output_text", "text": "{\"ok\":true}"}]}]}
    assert extract_output_text(payload) == '{"ok":true}'
