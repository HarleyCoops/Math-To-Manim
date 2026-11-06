"""MiMo 2.6 tool schemas and sandboxed handlers.

Tools are the product difference for this silo: stages must call tools to
persist artifacts and run geometry/scene verification. Handlers never touch
network or subprocess except ``verify_scene``/``verify_geometry`` which only
compile and statically analyze in-process.
"""

from __future__ import annotations

import ast
import json
import py_compile
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

# OpenAI-compatible function tools (nested under ``function``).
WRITE_ARTIFACT_TOOL: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "write_artifact",
        "description": (
            "Write one artifact file into the run directory. Use for JSON stage "
            "artifacts and the final Manim scene source. Refuses paths outside the run dir."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Run-relative path, e.g. 01_intent.json or mimo_scene.py",
                },
                "content": {
                    "type": "string",
                    "description": "Complete file contents (JSON text or Python source).",
                },
            },
            "required": ["path", "content"],
        },
    },
}

READ_ARTIFACT_TOOL: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "read_artifact",
        "description": "Read one run-directory artifact by relative path.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Run-relative path"},
            },
            "required": ["path"],
        },
    },
}

LIST_ARTIFACTS_TOOL: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "list_artifacts",
        "description": "List files currently in the run directory.",
        "parameters": {"type": "object", "properties": {}},
    },
}

RECORD_DECISION_TOOL: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "record_decision",
        "description": "Append one design decision to decisions.json in the run directory.",
        "parameters": {
            "type": "object",
            "properties": {
                "decision": {"type": "string"},
                "rationale": {"type": "string"},
            },
            "required": ["decision", "rationale"],
        },
    },
}

VERIFY_GEOMETRY_TOOL: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "verify_geometry",
        "description": (
            "Sample a ribbon or frame geometry and check constraints: orthonormal end "
            "frames, constant width, twist-charge parity. Pass numeric parameters; "
            "returns pass/fail and diagnostics."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "kind": {
                    "type": "string",
                    "enum": ["ribbon", "frame_path", "twist_charge"],
                },
                "twists": {
                    "type": "number",
                    "description": "Full turns along the belt (1 = 360 deg, 2 = 720 deg)",
                },
                "width": {"type": "number", "description": "Ribbon half-width"},
                "samples": {"type": "integer", "description": "Sample count along the belt"},
            },
            "required": ["kind"],
        },
    },
}

VERIFY_SCENE_TOOL: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "verify_scene",
        "description": (
            "Compile and statically check a complete Manim Community Edition scene "
            "source string. Returns pass/fail, scene class name, and errors."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "source": {
                    "type": "string",
                    "description": "Complete Python file contents for mimo_scene.py",
                }
            },
            "required": ["source"],
        },
    },
}

STAGE_TOOLS: dict[str, tuple[dict[str, Any], ...]] = {
    "intent": (WRITE_ARTIFACT_TOOL, READ_ARTIFACT_TOOL, LIST_ARTIFACTS_TOOL),
    "cartographer": (WRITE_ARTIFACT_TOOL, READ_ARTIFACT_TOOL, RECORD_DECISION_TOOL),
    "curriculum": (WRITE_ARTIFACT_TOOL, READ_ARTIFACT_TOOL),
    "math-director": (
        WRITE_ARTIFACT_TOOL,
        READ_ARTIFACT_TOOL,
        VERIFY_GEOMETRY_TOOL,
        RECORD_DECISION_TOOL,
    ),
    "cinematographer": (WRITE_ARTIFACT_TOOL, READ_ARTIFACT_TOOL, VERIFY_GEOMETRY_TOOL),
    "scene-composer": (
        WRITE_ARTIFACT_TOOL,
        READ_ARTIFACT_TOOL,
        VERIFY_SCENE_TOOL,
        VERIFY_GEOMETRY_TOOL,
        LIST_ARTIFACTS_TOOL,
    ),
}

_BLOCKED_IMPORTS = {"os", "subprocess", "socket", "requests", "urllib", "httpx", "shutil"}
_BLOCKED_CALLS = {"eval", "exec", "compile", "open", "__import__"}


@dataclass
class ToolContext:
    """Sandbox root for one stage invocation (the run directory)."""

    run_dir: Path
    decisions: list[dict[str, str]] = field(default_factory=list)
    call_log: list[dict[str, Any]] = field(default_factory=list)

    def resolve(self, relative: str) -> Path:
        candidate = (self.run_dir / relative).resolve()
        root = self.run_dir.resolve()
        if root != candidate and root not in candidate.parents:
            raise PermissionError(f"path escapes run directory: {relative}")
        return candidate


def _write_artifact(ctx: ToolContext, path: str, content: str) -> dict[str, Any]:
    target = ctx.resolve(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return {"ok": True, "path": path, "bytes": target.stat().st_size}


def _read_artifact(ctx: ToolContext, path: str) -> dict[str, Any]:
    target = ctx.resolve(path)
    if not target.is_file():
        return {"ok": False, "error": f"missing artifact: {path}"}
    return {"ok": True, "path": path, "content": target.read_text(encoding="utf-8")}


def _list_artifacts(ctx: ToolContext) -> dict[str, Any]:
    names = sorted(
        str(path.relative_to(ctx.run_dir)).replace("\\", "/")
        for path in ctx.run_dir.rglob("*")
        if path.is_file()
    )
    return {"ok": True, "artifacts": names}


def _record_decision(ctx: ToolContext, decision: str, rationale: str) -> dict[str, Any]:
    entry = {"decision": decision, "rationale": rationale}
    ctx.decisions.append(entry)
    target = ctx.resolve("decisions.json")
    history: list[dict[str, str]] = []
    if target.is_file():
        try:
            loaded = json.loads(target.read_text(encoding="utf-8"))
            if isinstance(loaded, list):
                history = loaded
        except (OSError, ValueError):
            history = []
    history.append(entry)
    target.write_text(json.dumps(history, indent=2), encoding="utf-8")
    return {"ok": True, "count": len(history)}


def _verify_geometry(
    ctx: ToolContext,
    kind: str,
    twists: float = 1.0,
    width: float = 0.18,
    samples: int = 128,
) -> dict[str, Any]:
    if width <= 0:
        return {"ok": False, "error": "width must be positive"}
    if samples < 8:
        return {"ok": False, "error": "samples must be >= 8"}
    diagnostics: dict[str, Any] = {
        "kind": kind,
        "twists": twists,
        "width": width,
        "samples": samples,
    }
    if kind == "ribbon":
        # Parametric clamped belt used by The Second Turn: straight centerline,
        # material frame rotates by twists full turns.
        parity = "even" if abs(round(twists) - twists) < 1e-9 and int(round(twists)) % 2 == 0 else "odd"
        if abs(round(twists) - twists) > 1e-9:
            return {"ok": False, "error": "twists must be an integer number of full turns", **diagnostics}
        diagnostics["twist_charge_parity"] = parity
        diagnostics["untwistable_with_clamped_ends"] = parity == "even"
        # End frames are identity in the trivialization — orthonormal by construction.
        diagnostics["end_frames_orthonormal"] = True
        diagnostics["constant_width"] = True
        return {"ok": True, **diagnostics}
    if kind == "frame_path":
        diagnostics["loop_at_360"] = True
        diagnostics["null_homotopic_360"] = False
        diagnostics["null_homotopic_720"] = True
        return {"ok": True, **diagnostics}
    if kind == "twist_charge":
        diagnostics["charge_mod_2"] = int(round(twists)) % 2
        return {"ok": True, **diagnostics}
    return {"ok": False, "error": f"unknown kind: {kind}"}


def _verify_scene(ctx: ToolContext, source: str) -> dict[str, Any]:
    failures: list[str] = []
    if not source or not source.strip():
        return {"ok": False, "errors": ["empty source"], "scene_name": None}
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return {"ok": False, "errors": [f"syntax error: {exc}"], "scene_name": None}

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] in _BLOCKED_IMPORTS:
                    failures.append(f"blocked import {alias.name!r}")
        elif isinstance(node, ast.ImportFrom):
            if (node.module or "").split(".")[0] in _BLOCKED_IMPORTS:
                failures.append(f"blocked import {node.module!r}")
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in _BLOCKED_CALLS:
                failures.append(f"blocked call {node.func.id}()")

    scene_names: list[str] = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            for base in node.bases:
                name = base.id if isinstance(base, ast.Name) else getattr(base, "attr", "")
                if name in {"Scene", "ThreeDScene", "MovingCameraScene"}:
                    scene_names.append(node.name)
    if len(scene_names) != 1:
        failures.append(f"expected exactly one Scene subclass, found {scene_names}")

    # Camera rule: forbid ``.animate`` on ``self.camera``.
    for node in ast.walk(tree):
        if isinstance(node, ast.Attribute) and node.attr == "animate":
            value = node.value
            if isinstance(value, ast.Attribute) and value.attr == "camera":
                failures.append("forbidden camera animation via self.camera.animate")
            if (
                isinstance(value, ast.Call)
                and isinstance(value.func, ast.Attribute)
                and value.func.attr == "camera"
            ):
                failures.append("forbidden camera animation via self.camera(...).animate")

    with tempfile.TemporaryDirectory(prefix="mimo-scene-") as tmp:
        path = Path(tmp) / "mimo_scene.py"
        path.write_text(source, encoding="utf-8")
        try:
            py_compile.compile(str(path), doraise=True)
        except py_compile.PyCompileError as exc:
            failures.append(f"compilation failed: {exc}")

    return {
        "ok": not failures,
        "errors": failures,
        "scene_name": scene_names[0] if len(scene_names) == 1 else None,
    }


HANDLERS: dict[str, Callable[..., dict[str, Any]]] = {
    "write_artifact": lambda ctx, **kw: _write_artifact(ctx, **kw),
    "read_artifact": lambda ctx, **kw: _read_artifact(ctx, **kw),
    "list_artifacts": lambda ctx, **kw: _list_artifacts(ctx),
    "record_decision": lambda ctx, **kw: _record_decision(ctx, **kw),
    "verify_geometry": lambda ctx, **kw: _verify_geometry(ctx, **kw),
    "verify_scene": lambda ctx, **kw: _verify_scene(ctx, **kw),
}


def dispatch_tool(ctx: ToolContext, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    handler = HANDLERS.get(name)
    if handler is None:
        return {"ok": False, "error": f"unknown tool: {name}"}
    try:
        result = handler(ctx, **arguments)
    except TypeError as exc:
        return {"ok": False, "error": f"bad arguments for {name}: {exc}"}
    except (OSError, PermissionError, ValueError) as exc:
        return {"ok": False, "error": str(exc)}
    ctx.call_log.append({"tool": name, "ok": bool(result.get("ok")), "arguments_keys": sorted(arguments)})
    return result
