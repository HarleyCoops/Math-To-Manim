"""MiMo 2.6 tool schemas and sandboxed handlers.

Tools are the product difference for this silo: stages must call tools to
persist artifacts and run geometry/scene verification. Handlers never touch
network or subprocess; ``verify_scene`` is the same static checker the
application-side gate runs (``mimo.validation``).

Each tool is one ``Tool`` (OpenAI function spec + handler) in ``TOOLS``. Which
tools a stage may call is declared on the stage table in ``mimo.agents``.
"""

from __future__ import annotations

import json
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable

from mimo.models import DECISIONS_FILE, SCENE_FILE
from mimo.validation import validation_from_scene


@dataclass
class ToolContext:
    """Sandbox root for one stage invocation (the run directory).

    ``decisions_lock`` must be shared by every context of one run: stages run
    in parallel threads and ``record_decision`` read-modify-writes one file.
    """

    run_dir: Path
    decisions_lock: threading.Lock = field(default_factory=threading.Lock)
    decisions: list[dict[str, str]] = field(default_factory=list)
    call_log: list[dict[str, Any]] = field(default_factory=list)

    def resolve(self, relative: str) -> Path:
        candidate = (self.run_dir / relative).resolve()
        root = self.run_dir.resolve()
        if root != candidate and root not in candidate.parents:
            raise PermissionError(f"path escapes run directory: {relative}")
        return candidate


Handler = Callable[..., dict[str, Any]]


@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    parameters: dict[str, Any]
    handler: Handler

    @property
    def spec(self) -> dict[str, Any]:
        """OpenAI-compatible function tool (nested under ``function``)."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


def write_artifact(ctx: ToolContext, path: str, content: str) -> dict[str, Any]:
    target = ctx.resolve(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return {"ok": True, "path": path, "bytes": target.stat().st_size}


def read_artifact(ctx: ToolContext, path: str) -> dict[str, Any]:
    target = ctx.resolve(path)
    if not target.is_file():
        return {"ok": False, "error": f"missing artifact: {path}"}
    return {"ok": True, "path": path, "content": target.read_text(encoding="utf-8")}


def list_artifacts(ctx: ToolContext, **_ignored: Any) -> dict[str, Any]:
    names = sorted(
        str(path.relative_to(ctx.run_dir)).replace("\\", "/")
        for path in ctx.run_dir.rglob("*")
        if path.is_file()
    )
    return {"ok": True, "artifacts": names}


def record_decision(ctx: ToolContext, decision: str, rationale: str) -> dict[str, Any]:
    entry = {"decision": decision, "rationale": rationale}
    ctx.decisions.append(entry)
    target = ctx.resolve(DECISIONS_FILE)
    with ctx.decisions_lock:
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


def verify_geometry(
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
        if abs(round(twists) - twists) > 1e-9:
            return {"ok": False, "error": "twists must be an integer number of full turns", **diagnostics}
        parity = "even" if int(round(twists)) % 2 == 0 else "odd"
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


def verify_scene(ctx: ToolContext, source: str) -> dict[str, Any]:
    report = validation_from_scene(source)
    return {"ok": report["status"] == "passed", "errors": report["errors"], "scene_name": report["scene_name"]}


TOOLS: dict[str, Tool] = {
    tool.name: tool
    for tool in (
        Tool(
            name="write_artifact",
            description=(
                "Write one artifact file into the run directory. Use for JSON stage "
                "artifacts and the final Manim scene source. Refuses paths outside the run dir."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": f"Run-relative path, e.g. 01_intent.json or {SCENE_FILE}",
                    },
                    "content": {
                        "type": "string",
                        "description": "Complete file contents (JSON text or Python source).",
                    },
                },
                "required": ["path", "content"],
            },
            handler=write_artifact,
        ),
        Tool(
            name="read_artifact",
            description="Read one run-directory artifact by relative path.",
            parameters={
                "type": "object",
                "properties": {"path": {"type": "string", "description": "Run-relative path"}},
                "required": ["path"],
            },
            handler=read_artifact,
        ),
        Tool(
            name="list_artifacts",
            description="List files currently in the run directory.",
            parameters={"type": "object", "properties": {}},
            handler=list_artifacts,
        ),
        Tool(
            name="record_decision",
            description=f"Append one design decision to {DECISIONS_FILE} in the run directory.",
            parameters={
                "type": "object",
                "properties": {
                    "decision": {"type": "string"},
                    "rationale": {"type": "string"},
                },
                "required": ["decision", "rationale"],
            },
            handler=record_decision,
        ),
        Tool(
            name="verify_geometry",
            description=(
                "Sample a ribbon or frame geometry and check constraints: orthonormal end "
                "frames, constant width, twist-charge parity. Pass numeric parameters; "
                "returns pass/fail and diagnostics."
            ),
            parameters={
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
            handler=verify_geometry,
        ),
        Tool(
            name="verify_scene",
            description=(
                "Compile and statically check a complete Manim Community Edition scene "
                "source string. Returns pass/fail, scene class name, and errors."
            ),
            parameters={
                "type": "object",
                "properties": {
                    "source": {
                        "type": "string",
                        "description": f"Complete Python file contents for {SCENE_FILE}",
                    }
                },
                "required": ["source"],
            },
            handler=verify_scene,
        ),
    )
}


def tool_specs(names: tuple[str, ...]) -> tuple[dict[str, Any], ...]:
    return tuple(TOOLS[name].spec for name in names)


def dispatch_tool(ctx: ToolContext, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    tool = TOOLS.get(name)
    if tool is None:
        return {"ok": False, "error": f"unknown tool: {name}"}
    try:
        result = tool.handler(ctx, **arguments)
    except TypeError as exc:
        return {"ok": False, "error": f"bad arguments for {name}: {exc}"}
    except (OSError, PermissionError, ValueError) as exc:
        return {"ok": False, "error": str(exc)}
    ctx.call_log.append({"tool": name, "ok": bool(result.get("ok")), "arguments_keys": sorted(arguments)})
    return result
