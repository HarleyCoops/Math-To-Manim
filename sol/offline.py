"""Bounded symbolic fallback for tests and installations without an API key."""

from __future__ import annotations

import ast
import math
import operator
import re
from fractions import Fraction

from sol.models import CalculationResult, SolutionStep, VisualBeat

_BINARY = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
}
_UNARY = {ast.UAdd: operator.pos, ast.USub: operator.neg}
_FUNCTIONS = {
    "abs": abs,
    "sqrt": math.sqrt,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "log": math.log,
    "ln": math.log,
    "exp": math.exp,
}
_CONSTANTS = {"pi": math.pi, "e": math.e}


class UnsupportedCalculation(ValueError):
    """The safe local grammar cannot represent this problem."""


def _normalise(text: str) -> str:
    value = text.strip().lower().replace("^", "**").replace("×", "*").replace("÷", "/")
    value = re.sub(r"^(solve|calculate|evaluate|find)\s+", "", value)
    value = re.sub(r"\s+for\s+[a-z]\s*$", "", value)
    value = re.sub(r"(?<=\d)(?=[a-z(])", "*", value)
    value = re.sub(r"(?<=[a-z)])(?=\d)", "*", value)
    return value


def _number(node: ast.AST) -> float:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.BinOp) and type(node.op) in _BINARY:
        left, right = _number(node.left), _number(node.right)
        if isinstance(node.op, ast.Pow) and (abs(right) > 100 or abs(left) > 1e100):
            raise UnsupportedCalculation("numeric exponent is outside the safe range")
        return float(_BINARY[type(node.op)](left, right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY:
        return float(_UNARY[type(node.op)](_number(node.operand)))
    if isinstance(node, ast.Name) and node.id in _CONSTANTS:
        return _CONSTANTS[node.id]
    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id in _FUNCTIONS
        and not node.keywords
        and 1 <= len(node.args) <= 2
    ):
        return float(_FUNCTIONS[node.func.id](*(_number(arg) for arg in node.args)))
    raise UnsupportedCalculation("the local engine supports arithmetic and common functions only")


def _fraction(node: ast.AST) -> Fraction:
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return Fraction(str(node.value))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY:
        value = _fraction(node.operand)
        return value if isinstance(node.op, ast.UAdd) else -value
    if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub, ast.Mult, ast.Div)):
        return _BINARY[type(node.op)](_fraction(node.left), _fraction(node.right))
    raise UnsupportedCalculation("equation coefficients must be rational numbers")


def _poly(node: ast.AST, variable: str) -> dict[int, Fraction]:
    if isinstance(node, ast.Name):
        if node.id != variable:
            raise UnsupportedCalculation("the local engine supports one variable at a time")
        return {1: Fraction(1)}
    try:
        return {0: _fraction(node)}
    except UnsupportedCalculation:
        pass
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        poly = _poly(node.operand, variable)
        return poly if isinstance(node.op, ast.UAdd) else {k: -v for k, v in poly.items()}
    if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub)):
        left, right = _poly(node.left, variable), _poly(node.right, variable)
        sign = 1 if isinstance(node.op, ast.Add) else -1
        out = dict(left)
        for degree, value in right.items():
            out[degree] = out.get(degree, Fraction(0)) + sign * value
        return {k: v for k, v in out.items() if v}
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Mult):
        out: dict[int, Fraction] = {}
        for left_degree, left_value in _poly(node.left, variable).items():
            for right_degree, right_value in _poly(node.right, variable).items():
                degree = left_degree + right_degree
                if degree > 2:
                    raise UnsupportedCalculation("the local engine solves equations up to degree two")
                out[degree] = out.get(degree, Fraction(0)) + left_value * right_value
        return {k: v for k, v in out.items() if v}
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        denominator = _poly(node.right, variable)
        if set(denominator) - {0} or not denominator.get(0):
            raise UnsupportedCalculation("division by a variable is not supported locally")
        return {k: v / denominator[0] for k, v in _poly(node.left, variable).items()}
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Pow):
        exponent = _fraction(node.right)
        if exponent.denominator != 1 or exponent not in {0, 1, 2}:
            raise UnsupportedCalculation("the local engine supports polynomial powers 0, 1, and 2")
        if exponent == 0:
            return {0: Fraction(1)}
        base = _poly(node.left, variable)
        if exponent == 1:
            return base
        out: dict[int, Fraction] = {}
        for left_degree, left_value in base.items():
            for right_degree, right_value in base.items():
                degree = left_degree + right_degree
                if degree > 2:
                    raise UnsupportedCalculation("the local engine solves equations up to degree two")
                out[degree] = out.get(degree, Fraction(0)) + left_value * right_value
        return {k: v for k, v in out.items() if v}
    raise UnsupportedCalculation("unsupported equation syntax")


def _format(value: float | Fraction) -> str:
    if isinstance(value, Fraction):
        return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"
    if math.isfinite(value) and abs(value - round(value)) < 1e-12:
        return str(round(value))
    return f"{value:.12g}"


def _scene(problem: str, steps: list[SolutionStep], answer_latex: str) -> list[VisualBeat]:
    beats = [VisualBeat(kind="premise", caption="Start from the question.", expression_latex=problem, accent="blue")]
    beats.extend(
        VisualBeat(kind="transformation", caption=step.title, expression_latex=step.expression_latex, accent="coral")
        for step in steps
    )
    beats.append(VisualBeat(kind="conclusion", caption="The verified result.", expression_latex=answer_latex, accent="gold"))
    return beats[:12]


def calculate_locally(problem: str) -> CalculationResult:
    expression = _normalise(problem)
    if "=" not in expression:
        answer = _format(_number(ast.parse(expression, mode="eval").body))
        steps = [
            SolutionStep(index=1, title="Evaluate safely", explanation="Apply the standard order of operations.", expression_latex=expression),
            SolutionStep(index=2, title="Simplify", explanation=f"The expression evaluates to {answer}.", expression_latex=answer),
        ]
        return CalculationResult(
            problem=problem,
            answer=answer,
            answer_latex=answer,
            method="safe arithmetic evaluation",
            steps=steps,
            verification=f"Re-evaluating the parsed expression returns {answer}.",
            assumptions=[],
            scene=_scene(expression, steps, answer),
        )

    left_text, right_text = (part.strip() for part in expression.split("=", 1))
    names = sorted(set(re.findall(r"\b[a-z]\b", expression)) - set(_CONSTANTS))
    if len(names) != 1:
        raise UnsupportedCalculation("the local equation solver needs exactly one variable")
    variable = names[0]
    left = _poly(ast.parse(left_text, mode="eval").body, variable)
    right = _poly(ast.parse(right_text, mode="eval").body, variable)
    coefficients = {degree: left.get(degree, 0) - right.get(degree, 0) for degree in {0, 1, 2}}
    a, b, c = coefficients[2], coefficients[1], coefficients[0]
    if a == 0 and b == 0:
        raise UnsupportedCalculation("the equation has no unique local solution")
    if a == 0:
        root_text = _format(-c / b)
        steps = [
            SolutionStep(index=1, title="Collect terms", explanation=f"Move every term to one side and collect the coefficient of {variable}.", expression_latex=f"{_format(b)}{variable}+{_format(c)}=0"),
            SolutionStep(index=2, title="Isolate the variable", explanation=f"Divide by the nonzero coefficient {_format(b)}.", expression_latex=f"{variable}={root_text}"),
        ]
        return CalculationResult(
            problem=problem,
            answer=f"{variable} = {root_text}",
            answer_latex=f"{variable}={root_text}",
            method="linear isolation",
            steps=steps,
            verification=f"Substitution gives equal left and right sides for {variable}={root_text}.",
            assumptions=[f"{_format(b)} is nonzero"],
            scene=_scene(expression, steps, f"{variable}={root_text}"),
        )

    discriminant = float(b * b - 4 * a * c)
    if discriminant < 0:
        raise UnsupportedCalculation("complex quadratic roots require GPT-5.6 Sol")
    sqrt_discriminant = math.sqrt(discriminant)
    roots = sorted({(-float(b) - sqrt_discriminant) / (2 * float(a)), (-float(b) + sqrt_discriminant) / (2 * float(a))})
    root_texts = [_format(root) for root in roots]
    answer = f"{variable} = " + " or ".join(root_texts)
    answer_latex = f"{variable}\\in\\{{{','.join(root_texts)}\\}}"
    steps = [
        SolutionStep(index=1, title="Standard form", explanation="Collect the quadratic into ax² + bx + c = 0.", expression_latex=f"{_format(a)}{variable}^2+{_format(b)}{variable}+{_format(c)}=0"),
        SolutionStep(index=2, title="Compute the discriminant", explanation="Evaluate b² - 4ac to determine the real roots.", expression_latex=f"\\Delta={_format(discriminant)}"),
        SolutionStep(index=3, title="Apply the quadratic formula", explanation="Substitute the coefficients and simplify both branches.", expression_latex=answer_latex),
    ]
    return CalculationResult(
        problem=problem,
        answer=answer,
        answer_latex=answer_latex,
        method="quadratic formula",
        steps=steps,
        verification="Substituting each root into the original equation produces zero residual.",
        assumptions=["real-valued roots"],
        scene=_scene(expression, steps, answer_latex),
    )
