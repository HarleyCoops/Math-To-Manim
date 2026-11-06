"""Local ADK function tools for Argon math-director and composer agents."""

from __future__ import annotations

import ast
import math
import operator
import numpy as np

from argon.validation import verify_scene_report

_SAFE_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

_SAFE_NAMES = {
    "pi": math.pi,
    "e": math.e,
    "tau": math.tau,
    "sqrt": math.sqrt,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "asin": math.asin,
    "acos": math.acos,
    "atan": math.atan,
    "exp": math.exp,
    "log": math.log,
    "log10": math.log10,
    "abs": abs,
    "round": round,
    "min": min,
    "max": max,
    "np": np,
    "math": math,
}


def _eval_node(node: ast.AST):
    if isinstance(node, ast.Expression):
        return _eval_node(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.Name) and node.id in _SAFE_NAMES:
        return _SAFE_NAMES[node.id]
    if isinstance(node, ast.UnaryOp) and type(node.op) in _SAFE_OPS:
        return _SAFE_OPS[type(node.op)](_eval_node(node.operand))
    if isinstance(node, ast.BinOp) and type(node.op) in _SAFE_OPS:
        return _SAFE_OPS[type(node.op)](_eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.Attribute):
        base = _eval_node(node.value)
        if base in (np, math) and not node.attr.startswith("_"):
            return getattr(base, node.attr)
        raise ValueError(f"disallowed attribute access: {node.attr}")
    if isinstance(node, ast.Call):
        func = _eval_node(node.func)
        args = [_eval_node(arg) for arg in node.args]
        kwargs = {kw.arg: _eval_node(kw.value) for kw in node.keywords if kw.arg}
        return func(*args, **kwargs)
    if isinstance(node, (ast.List, ast.Tuple)):
        return [_eval_node(elt) for elt in node.elts]
    raise ValueError(f"unsupported AST node in math check: {type(node).__name__}")


def execute_math_check(expression: str) -> dict:
    """Evaluate a safe mathematical expression using numpy/math and return the numerical result."""
    if not expression or not str(expression).strip():
        return {"ok": False, "error": "expression was empty"}
    try:
        tree = ast.parse(str(expression).strip(), mode="eval")
        val = _eval_node(tree)
        if isinstance(val, np.ndarray):
            val = val.tolist()
        elif isinstance(val, (np.floating, np.integer)):
            val = val.item()
        return {"ok": True, "expression": str(expression).strip(), "value": val}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "expression": str(expression).strip(), "error": str(exc)}


def verify_scene(source: str = "") -> dict:
    """Compile and statically check a complete Manim Community Edition scene source string."""
    if not source or not str(source).strip():
        return {"passed": False, "scene_name": None, "errors": ["source was empty"]}
    return verify_scene_report(str(source))
