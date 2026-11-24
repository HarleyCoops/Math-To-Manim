"""Stages 4-6 runtime: a Claude Agent SDK session that sees its own frames.

The scene coder (stage 4) and its repairs (stage 6) are one
``ClaudeSDKClient`` conversation, so the model keeps its context across
repair loops. Visual QA (stage 5) is a separate, fresh agent: it did not write
the code and is asked to judge frames only.

The agent works in ``<run>/work`` with Read, Write and Edit (confined to that
folder by a PreToolUse hook) and three tools served in process:

- ``render_draft``: renders a 480-line draft of the scene file;
- ``extract_frames``: PNG frames of the latest draft at given times;
- ``probe_video``: size, frame rate and duration of the latest draft.

Every tool call, every edit of the scene file and every turn is written to
the run trace from the SDK's hooks and message stream; nothing is parsed from
logs afterwards.
"""

from __future__ import annotations

import asyncio
import difflib
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from mythos import trace as tr
from mythos.motion import render as mrender
from mythos.scene_checks import find_scene_class

TOOL_SERVER = "motion"
CODER_TOOLS = (
    "Read", "Write", "Edit",
    f"mcp__{TOOL_SERVER}__render_draft",
    f"mcp__{TOOL_SERVER}__extract_frames",
    f"mcp__{TOOL_SERVER}__probe_video",
)
QA_TOOLS = ("Read",)
_PATH_TOOLS = {"Read", "Write", "Edit", "MultiEdit", "NotebookEdit"}
_EDIT_TOOLS = {"Write", "Edit", "MultiEdit"}
_MAX_TEXT = 60_000


def _clip(obj: Any) -> Any:
    """Drop image bytes and cap very long strings before they reach the trace."""
    if isinstance(obj, str):
        return obj if len(obj) <= _MAX_TEXT else obj[:_MAX_TEXT] + f"... <{len(obj)} chars>"
    if isinstance(obj, dict):
        if obj.get("type") == "image" or ("data" in obj and "media_type" in json.dumps(
                {k: v for k, v in obj.items() if k != "data"}, default=str)):
            return {"type": "image", "data": "<image omitted>"}
        return {k: ("<base64 omitted>" if k in {"data", "base64"} and isinstance(v, str)
                    and len(v) > 512 else _clip(v)) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_clip(v) for v in obj]
    if hasattr(obj, "__dict__") and not isinstance(obj, type):
        return _clip({k: v for k, v in vars(obj).items() if not k.startswith("_")})
    return obj


def usage_tokens(usage: dict | None) -> tuple[int | None, int | None]:
    if not usage:
        return None, None
    tokens_in = sum(int(usage.get(k) or 0) for k in (
        "input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"))
    return tokens_in or None, usage.get("output_tokens")


class CodeVersions:
    """Every distinct state of the scene file, saved as code/vNNN.py and traced."""

    def __init__(self, writer: tr.TraceWriter, code_dir: Path, scene_path: Path):
        self.writer = writer
        self.code_dir = Path(code_dir)
        self.scene_path = Path(scene_path)
        self.paths: list[Path] = []
        self.last: str = ""

    def snapshot(self, stage: str, cause: str, parent_seq: int | None = None) -> int | None:
        if not self.scene_path.is_file():
            return None
        code = self.scene_path.read_text(encoding="utf-8")
        if code == self.last:
            return None
        n = len(self.paths) + 1
        self.code_dir.mkdir(parents=True, exist_ok=True)
        path = self.code_dir / f"v{n:03d}.py"
        path.write_text(code, encoding="utf-8")
        diff = "".join(difflib.unified_diff(
            self.last.splitlines(keepends=True), code.splitlines(keepends=True),
            fromfile=f"v{n - 1:03d}.py" if n > 1 else "/dev/null", tofile=path.name))
        seq = self.writer.emit("code_version", stage=stage,
                               input={"version": n, "cause": cause, "file": f"code/{path.name}"},
                               output={"code": code, "diff": diff}, parent_seq=parent_seq,
                               runtime="agent-sdk")
        self.last = code
        self.paths.append(path)
        return seq


@dataclass
class TurnResult:
    text: str = ""
    assistant_text: list[str] = field(default_factory=list)
    structured: dict | None = None
    tokens_in: int | None = None
    tokens_out: int | None = None
    cost_usd: float | None = None
    turns: int | None = None
    session_id: str | None = None
    error: str | None = None
    seq: int | None = None


class MotionAgents:
    """The SDK session for stages 4 and 6 and the stage-5 visual QA agent."""

    def __init__(self, *, writer: tr.TraceWriter, work_dir: Path, scene_file: str,
                 width: int, height: int, fps: float, model: str,
                 coder_system: str, qa_system: str, versions: CodeVersions,
                 render_timeout: float, config_dir: str | None = None,
                 max_turns: int = 80, log=print):
        self.writer = writer
        self.work = Path(work_dir).resolve()
        self.scene_file = scene_file
        self.width, self.height, self.fps = width, height, fps
        self.model = model
        self.coder_system = coder_system
        self.qa_system = qa_system
        self.versions = versions
        self.render_timeout = render_timeout
        self.config_dir = config_dir
        self.max_turns = max_turns
        self.log = log
        self.stage = "scene_coder"
        self.last_draft: Path | None = None
        self.draft_count = 0
        self._starts: dict[str, float] = {}

    # ------------------------------------------------------------------ #
    # Hooks                                                               #
    # ------------------------------------------------------------------ #

    def _inside(self, raw: str, root: Path) -> bool:
        path = Path(raw)
        path = path if path.is_absolute() else root / path
        try:
            path.resolve().relative_to(root.resolve())
            return True
        except ValueError:
            return False

    def hooks(self, root: Path) -> dict:
        from claude_agent_sdk import HookMatcher

        async def pre(data: dict, tool_use_id: str | None, context: Any) -> dict:
            self._starts[tool_use_id or ""] = time.perf_counter()
            name = data.get("tool_name", "")
            args = data.get("tool_input") or {}
            target = args.get("file_path") or args.get("notebook_path") or args.get("path")
            if name in _PATH_TOOLS and target and not self._inside(str(target), root):
                return {"hookSpecificOutput": {
                    "hookEventName": "PreToolUse", "permissionDecision": "deny",
                    "permissionDecisionReason": f"{name} is limited to {root.name}/"}}
            return {}

        async def post(data: dict, tool_use_id: str | None, context: Any) -> dict:
            started = self._starts.pop(tool_use_id or "", None)
            name = data.get("tool_name", "")
            args = data.get("tool_input") or {}
            seq = self.writer.emit(
                "tool_call", stage=self.stage, runtime="agent-sdk",
                input={"tool": name, "tool_use_id": tool_use_id, "args": _clip(args)},
                output=_clip(data.get("tool_response")),
                latency_ms=(time.perf_counter() - started) * 1000 if started else None)
            target = str(args.get("file_path") or "")
            if name in _EDIT_TOOLS and Path(target).name == self.scene_file:
                self.versions.snapshot(self.stage, cause=f"{name} by agent", parent_seq=seq)
            return {}

        async def post_failure(data: dict, tool_use_id: str | None, context: Any) -> dict:
            started = self._starts.pop(tool_use_id or "", None)
            self.writer.emit(
                "tool_call", stage=self.stage, runtime="agent-sdk",
                input={"tool": data.get("tool_name"), "tool_use_id": tool_use_id,
                       "args": _clip(data.get("tool_input") or {})},
                output={"error": _clip(data.get("error"))},
                latency_ms=(time.perf_counter() - started) * 1000 if started else None)
            return {}

        return {
            "PreToolUse": [HookMatcher(matcher=None, hooks=[pre])],
            "PostToolUse": [HookMatcher(matcher=None, hooks=[post])],
            "PostToolUseFailure": [HookMatcher(matcher=None, hooks=[post_failure])],
        }

    # ------------------------------------------------------------------ #
    # In-process tools                                                    #
    # ------------------------------------------------------------------ #

    def scene_name(self) -> str:
        return find_scene_class((self.work / self.scene_file).read_text(encoding="utf-8"))

    def tool_server(self):
        from claude_agent_sdk import create_sdk_mcp_server, tool

        dw, dh = mrender.draft_size(self.width, self.height)

        def text(value: str) -> dict:
            return {"content": [{"type": "text", "text": value}]}

        @tool("render_draft",
              f"Render {self.scene_file} as a {dw}x{dh} {mrender.DRAFT_FPS:g} fps draft. "
              "Returns the exit code, the error tail on failure, and the draft's duration.",
              {"type": "object", "properties": {}})
        async def render_draft(args: dict) -> dict:
            try:
                scene_name = self.scene_name()
            except Exception as exc:  # noqa: BLE001 - reported to the agent
                return text(f"Cannot render: {exc}")
            self.draft_count += 1
            run = await asyncio.to_thread(
                mrender.render, self.work, scene_file=self.scene_file, scene_name=scene_name,
                width=dw, height=dh, fps=mrender.DRAFT_FPS, media_subdir="draft_media",
                timeout=self.render_timeout)
            self.last_draft = run.video
            duration = None
            if run.video:
                duration = (await asyncio.to_thread(mrender.probe, run.video)).duration_s
            self.writer.emit(
                "render_attempt", stage=self.stage, runtime="agent-sdk",
                input={"kind": "draft", "n": self.draft_count, "command": run.command,
                       "scene": scene_name},
                output={"exit_code": run.exit_code, "seconds": round(run.seconds, 2),
                        "timed_out": run.timed_out, "stderr_tail": run.tail(3000),
                        "duration_s": duration,
                        "video_sha256": tr.sha256_file(run.video) if run.video else None},
                latency_ms=run.seconds * 1000)
            if run.exit_code != 0:
                return text(f"Draft render FAILED (exit {run.exit_code}).\n{run.tail(6000)}")
            return text(f"Draft rendered: {dw}x{dh}, {duration:.3f}s "
                        f"(target {self.target_duration:.3f}s). Use extract_frames to look at it.")

        @tool("extract_frames",
              "Extract PNG frames of the latest draft at the given times (seconds). "
              "Returns the file paths; open them with Read.",
              {"type": "object", "properties": {"times": {"type": "array",
                                                          "items": {"type": "number"}}},
               "required": ["times"]})
        async def extract_frames(args: dict) -> dict:
            if not self.last_draft:
                return text("No draft yet: call render_draft first.")
            times = [float(t) for t in (args.get("times") or [])][:24]
            out = self.work / "draft_frames" / f"d{self.draft_count:02d}"
            frames = await asyncio.to_thread(mrender.extract_frames, self.last_draft, times, out)
            listing = "\n".join(f"{t:.3f}s -> {p.relative_to(self.work).as_posix()}"
                                for t, p in frames)
            return text(listing or "No frames extracted (times past the end?).")

        @tool("probe_video", "Width, height, frame rate and duration of the latest draft.",
              {"type": "object", "properties": {}})
        async def probe_video(args: dict) -> dict:
            if not self.last_draft:
                return text("No draft yet: call render_draft first.")
            info = await asyncio.to_thread(mrender.probe, self.last_draft)
            return text(json.dumps({"width": info.width, "height": info.height,
                                    "fps": info.fps, "duration_s": info.duration_s,
                                    "frames": info.frames,
                                    "target_duration_s": self.target_duration}))

        return create_sdk_mcp_server(TOOL_SERVER, tools=[render_draft, extract_frames,
                                                         probe_video])

    target_duration: float = 0.0

    # ------------------------------------------------------------------ #
    # Options and turns                                                   #
    # ------------------------------------------------------------------ #

    def _env(self) -> dict[str, str]:
        # The CLI login is the credential. Callers remove a stray
        # ANTHROPIC_API_KEY from the process environment before a live run.
        env: dict[str, str] = {}
        if self.config_dir:
            env["CLAUDE_CONFIG_DIR"] = self.config_dir
        return env

    def coder_options(self):
        from claude_agent_sdk import ClaudeAgentOptions

        return ClaudeAgentOptions(
            system_prompt=self.coder_system, model=self.model, cwd=str(self.work),
            allowed_tools=list(CODER_TOOLS), permission_mode="dontAsk",
            setting_sources=[], max_turns=self.max_turns,
            mcp_servers={TOOL_SERVER: self.tool_server()},
            hooks=self.hooks(self.work), env=self._env())

    async def ask(self, client: Any, prompt: str, stage: str) -> TurnResult:
        from claude_agent_sdk import AssistantMessage, ResultMessage, TextBlock

        self.stage = stage
        watch = tr.Stopwatch()
        result = TurnResult()
        await client.query(prompt)
        final = None
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock) and block.text.strip():
                        result.assistant_text.append(block.text)
            elif isinstance(message, ResultMessage):
                final = message
        return self._close_turn(result, final, prompt, stage, watch)

    def _close_turn(self, result: TurnResult, final: Any, prompt: str, stage: str,
                    watch: tr.Stopwatch, system: str | None = None) -> TurnResult:
        if final is None:
            result.error = "no result message"
        else:
            result.text = final.result or ""
            result.structured = getattr(final, "structured_output", None)
            result.tokens_in, result.tokens_out = usage_tokens(final.usage)
            result.cost_usd = final.total_cost_usd
            result.turns = final.num_turns
            result.session_id = final.session_id
            if final.is_error:
                result.error = str(getattr(final, "errors", None) or final.subtype)
        result.seq = self.writer.emit(
            "agent_call", stage=stage, runtime="agent-sdk", prompt=prompt,
            input={"prompt": prompt, "system": system},
            output={"result": result.text, "assistant_text": result.assistant_text,
                    "structured_output": result.structured, "num_turns": result.turns,
                    "cost_usd": result.cost_usd, "session_id": result.session_id,
                    "error": result.error},
            tokens_in=result.tokens_in, tokens_out=result.tokens_out, latency_ms=watch.ms)
        return result

    async def visual_qa(self, prompt: str, frames_dir: Path, schema: dict) -> TurnResult:
        """One fresh QA agent: Read-only, structured answer, judged from frames."""
        from claude_agent_sdk import (AssistantMessage, ClaudeAgentOptions, ResultMessage,
                                      TextBlock, query)

        root = Path(frames_dir).resolve()
        options = ClaudeAgentOptions(
            system_prompt=self.qa_system, model=self.model, cwd=str(root),
            allowed_tools=list(QA_TOOLS), permission_mode="dontAsk", setting_sources=[],
            max_turns=60, hooks=self.hooks(root), env=self._env(),
            output_format={"type": "json_schema", "schema": schema})
        previous, self.stage = self.stage, "visual_qa"
        watch = tr.Stopwatch()
        result = TurnResult()
        final = None
        try:
            async for message in query(prompt=prompt, options=options):
                if isinstance(message, AssistantMessage):
                    for block in message.content:
                        if isinstance(block, TextBlock) and block.text.strip():
                            result.assistant_text.append(block.text)
                elif isinstance(message, ResultMessage):
                    final = message
        finally:
            self.stage = previous
        return self._close_turn(result, final, prompt, "visual_qa", watch, system=None)


def client_class():
    from claude_agent_sdk import ClaudeSDKClient

    return ClaudeSDKClient


