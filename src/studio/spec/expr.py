"""Safe arithmetic expressions for surfaces and curves.

A SceneSpec is written by a model, so its expressions are never passed to
``eval``. An expression is parsed once, every node is checked against a short
allow-list, and the result is a function of named variables.

    f = compile_expression("0.4 * x * y", ("x", "y"))
    f(x=1.0, y=2.0)   # 0.8
"""

from __future__ import annotations

import ast
import math
import operator
from typing import Callable

FUNCTIONS: dict[str, Callable[..., float]] = {
    "sin": math.sin, "cos": math.cos, "tan": math.tan, "asin": math.asin,
    "acos": math.acos, "atan": math.atan, "atan2": math.atan2, "sinh": math.sinh,
    "cosh": math.cosh, "tanh": math.tanh, "exp": math.exp, "log": math.log,
    "sqrt": math.sqrt, "abs": abs, "min": min, "max": max, "floor": math.floor,
    "sign": lambda v: (v > 0) - (v < 0),
}
CONSTANTS = {"pi": math.pi, "tau": math.tau, "e": math.e}
_BINARY = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
           ast.Div: operator.truediv, ast.Pow: operator.pow, ast.Mod: operator.mod}
_UNARY = {ast.UAdd: operator.pos, ast.USub: operator.neg}


class ExpressionError(ValueError):
    """The expression uses something that is not allowed, or cannot be parsed."""


def compile_expression(source: str, variables: tuple[str, ...]) -> Callable[..., float]:
    """Check ``source`` and return ``f(**variables) -> float``."""
    if len(source) > 300:
        raise ExpressionError("expression is longer than 300 characters")
    try:
        tree = ast.parse(source.replace("^", "**"), mode="eval")
    except SyntaxError as exc:
        raise ExpressionError(f"cannot parse {source!r}: {exc.msg}") from exc

    def check(node: ast.AST) -> None:
        if isinstance(node, ast.Expression):
            check(node.body)
        elif isinstance(node, ast.Constant):
            if not isinstance(node.value, (int, float)) or isinstance(node.value, bool):
                raise ExpressionError(f"{source!r}: only numbers are allowed as constants")
        elif isinstance(node, ast.Name):
            if node.id not in variables and node.id not in CONSTANTS:
                allowed = ", ".join(variables + tuple(CONSTANTS))
                raise ExpressionError(f"{source!r}: unknown name {node.id!r} (use {allowed})")
        elif isinstance(node, ast.BinOp) and type(node.op) in _BINARY:
            check(node.left)
            check(node.right)
        elif isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY:
            check(node.operand)
        elif (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
              and node.func.id in FUNCTIONS and not node.keywords):
            for arg in node.args:
                check(arg)
        else:
            raise ExpressionError(
                f"{source!r}: only numbers, + - * / ** %, the names "
                f"{', '.join(variables)} and these functions are allowed: "
                f"{', '.join(sorted(FUNCTIONS))}")

    check(tree)

    def evaluate(node: ast.AST, env: dict[str, float]) -> float:
        if isinstance(node, ast.Expression):
            return evaluate(node.body, env)
        if isinstance(node, ast.Constant):
            return float(node.value)
        if isinstance(node, ast.Name):
            return env[node.id] if node.id in env else CONSTANTS[node.id]
        if isinstance(node, ast.BinOp):
            return _BINARY[type(node.op)](evaluate(node.left, env), evaluate(node.right, env))
        if isinstance(node, ast.UnaryOp):
            return _UNARY[type(node.op)](evaluate(node.operand, env))
        call = node  # an allowed ast.Call
        return FUNCTIONS[call.func.id](*(evaluate(arg, env) for arg in call.args))

    def function(**values: float) -> float:
        try:
            result = float(evaluate(tree, values))
        except (ArithmeticError, ValueError, TypeError) as exc:
            raise ExpressionError(f"{source!r} failed at {values}: {exc}") from exc
        if math.isnan(result) or math.isinf(result):
            raise ExpressionError(f"{source!r} is not finite at {values}")
        return result

    return function
