"""Drive the Math-To-Manim MCP server end to end, as a real MCP client.

This is the reference client for headless / scripted use: it spawns
`serve-mcp` over stdio, submits one prompt with m2m_create_animation, polls
m2m_get_job (which reports live per-stage progress), and logs everything as
JSONL so another process can tail the run.

The server is the Grok 4.6 chain. ``m2m_create_animation`` defaults to
model grok-4.6. Claude/Codex ``--command`` values are ignored.

Usage:
    python scripts/drive_mcp_pipeline.py "why does a spinning T-handle flip?" \
        --render -q l --log runs/mcp_drive.log
    python scripts/drive_mcp_pipeline.py @prompt.txt --render --image page.jpg
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

REPO = Path(__file__).resolve().parents[1]
POLL_SECONDS = 30
MAX_WALL_SECONDS = 3.5 * 3600


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prompt",
                        help="the film's prompt, or @path/to/prompt.txt")
    parser.add_argument("--render", action="store_true")
    parser.add_argument("-q", "--quality", default="l",
                        choices=list("lmhpk"))
    parser.add_argument("--model", default="grok-4.6",
                        help="Grok Responses model (default grok-4.6)")
    parser.add_argument("--image", default=None,
                        help="photographed homework page or diagram")
    parser.add_argument("--offline", action="store_true",
                        help="deterministic Grok rehearsal; no xAI calls")
    parser.add_argument("--log", default=None,
                        help="JSONL progress log (default: stdout only)")
    return parser.parse_args()


def make_logger(log_path: Path | None):
    def log(event: str, **payload) -> None:
        record = {"t": time.strftime("%Y-%m-%d %H:%M:%S"),
                  "event": event, **payload}
        line = json.dumps(record, ensure_ascii=False)
        print(line, flush=True)
        if log_path is not None:
            with log_path.open("a", encoding="utf-8") as handle:
                handle.write(line + "\n")
    return log


def text_of(result) -> str:
    return "".join(
        block.text for block in result.content if getattr(block, "text", None)
    )


async def main() -> int:
    args = parse_args()
    prompt = args.prompt
    if prompt.startswith("@"):
        prompt = Path(prompt[1:]).read_text(encoding="utf-8-sig").strip()
    log = make_logger(Path(args.log) if args.log else None)
    log("start", prompt_chars=len(prompt))

    params: dict = {
        "prompt": prompt,
        "render": args.render,
        "quality": args.quality,
        "model": args.model,
        "offline": args.offline,
    }
    if args.image:
        params["image"] = args.image

    server = StdioServerParameters(
        command=sys.executable,
        args=["-m", "mythos.cli", "serve-mcp"],
        cwd=str(REPO),
    )
    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await session.list_tools()
            log("connected", tools=[tool.name for tool in tools.tools])

            created = await session.call_tool(
                "m2m_create_animation", {"params": params})
            job = json.loads(text_of(created))
            if "id" not in job:
                log("create_failed", raw=text_of(created)[:2000])
                return 1
            log("job_created", job_id=job["id"], status=job["status"])

            started = time.time()
            last_stage_count = -1
            while time.time() - started < MAX_WALL_SECONDS:
                await asyncio.sleep(POLL_SECONDS)
                polled = await session.call_tool(
                    "m2m_get_job", {"job_id": job["id"]})
                state = json.loads(text_of(polled))
                stages = (state.get("manifest") or {}).get("stages", [])
                if state["status"] in ("completed", "failed"):
                    log("job_done", status=state["status"],
                        run_id=state.get("run_id"), error=state.get("error"),
                        manifest=state.get("manifest"))
                    return 0 if state["status"] == "completed" else 2
                if len(stages) != last_stage_count:
                    last_stage_count = len(stages)
                    log("progress", status=state["status"],
                        run_id=state.get("run_id"), stages_done=len(stages),
                        latest=stages[-1]["stage"] if stages else None)
            log("timeout", waited_seconds=int(time.time() - started))
            return 3


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
