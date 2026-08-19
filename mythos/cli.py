"""The math-to-manim command line.

    math-to-manim run "explain quantum field theory" --render -q m
    math-to-manim run "the heat equation" --offline
    math-to-manim runs                      # list on-disk runs
    math-to-manim doctor --ping             # preflight: config, auth, toolchain
    math-to-manim serve-api                 # REST API on :8642
    math-to-manim serve-mcp                 # Grok MCP server on stdio

Configuration comes from the environment (or a local, gitignored .env):
M2M_MODEL, M2M_COMMAND, M2M_TIMEOUT, M2M_RENDER_TIMEOUT, M2M_RUNS_DIR,
M2M_MANIM.
"""

from __future__ import annotations

import argparse
import json
import sys

from mythos import __version__
from mythos.backends import DEFAULT_COMMAND, DEFAULT_MODEL, DEFAULT_TIMEOUT


def _cmd_run(args: argparse.Namespace) -> int:
    from mythos.harness import DEFAULT_RENDER_TIMEOUT, MythosHarness

    fallbacks = (tuple(m.strip() for m in args.fallbacks.split(",") if m.strip())
                 if args.fallbacks is not None else None)
    harness = MythosHarness(command=args.command, model=args.model,
                            timeout=args.timeout,
                            render_timeout=(args.render_timeout
                                            or DEFAULT_RENDER_TIMEOUT),
                            offline=args.offline,
                            model_fallbacks=fallbacks)
    harness.run(args.prompt, render=args.render, quality=args.quality,
                max_repairs=args.max_repairs)
    return 0


def _cmd_doctor(args: argparse.Namespace) -> int:
    from mythos.doctor import run_doctor

    return run_doctor(command=args.command, model=args.model, ping=args.ping)


def _cmd_gif(args: argparse.Namespace) -> int:
    from mythos.gifs import make_gif

    make_gif(args.target, args.output, fps=args.fps, width=args.width)
    return 0


def _cmd_runs(args: argparse.Namespace) -> int:
    from mythos.service import MythosService

    summaries = MythosService().list_runs(limit=args.limit)
    print(json.dumps(summaries, indent=2))
    return 0


def _cmd_serve_api(args: argparse.Namespace) -> int:
    try:
        import uvicorn
    except ImportError:
        print("The REST API requires the 'api' extra: pip install -e '.[api]'",
              file=sys.stderr)
        return 1
    uvicorn.run("mythos.api:app", host=args.host, port=args.port,
                reload=args.reload)
    return 0


def _cmd_serve_mcp(args: argparse.Namespace) -> int:
    from mythos.mcp_server import main as mcp_main

    mcp_main(transport=args.transport, port=args.port)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="math-to-manim",
        description="Ask a question -> get a freakin' movie.",
    )
    parser.add_argument("--version", action="version",
                        version=f"math-to-manim {__version__}")
    sub = parser.add_subparsers(dest="cmd", required=True)

    run = sub.add_parser("run", help="Run the Mythos 6-agent chain on a prompt")
    run.add_argument("prompt")
    run.add_argument("--render", action="store_true")
    run.add_argument("-q", "--quality", default="l", choices=list("lmhpk"))
    run.add_argument("--model", default=DEFAULT_MODEL)
    run.add_argument("--command", default=DEFAULT_COMMAND)
    run.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)
    run.add_argument("--render-timeout", type=float, default=None,
                     help="render wall-clock budget in seconds "
                          "(default: M2M_RENDER_TIMEOUT or 1800)")
    run.add_argument("--fallbacks", default=None,
                     help="comma-separated Anthropic fallback models via the "
                          "same CLI login (default: M2M_MODEL_FALLBACKS or "
                          "claude-opus-4-8,claude-sonnet-5; '' disables)")
    run.add_argument("--offline", action="store_true")
    run.add_argument("--max-repairs", type=int, default=3)
    run.set_defaults(func=_cmd_run)

    runs = sub.add_parser("runs", help="List on-disk runs, newest first")
    runs.add_argument("--limit", type=int, default=20)
    runs.set_defaults(func=_cmd_runs)

    doctor = sub.add_parser(
        "doctor", help="Preflight: configuration, backend auth, toolchain")
    doctor.add_argument("--command", default=DEFAULT_COMMAND)
    doctor.add_argument("--model", default=DEFAULT_MODEL)
    doctor.add_argument("--ping", action="store_true",
                        help="make one tiny model call to verify login")
    doctor.set_defaults(func=_cmd_doctor)

    gif = sub.add_parser(
        "gif", help="Palette-optimized GIF from a run id or an .mp4 "
                    "(the showcase recipe)")
    gif.add_argument("target", help="run id under runs/mythos/ or a path "
                                    "to a rendered .mp4")
    gif.add_argument("-o", "--output", default=None,
                     help="output path (default: next to the source)")
    gif.add_argument("--fps", type=int, default=12)
    gif.add_argument("--width", type=int, default=640)
    gif.set_defaults(func=_cmd_gif)

    api = sub.add_parser("serve-api", help="Serve the REST API (FastAPI)")
    api.add_argument("--host", default="127.0.0.1")
    api.add_argument("--port", type=int, default=8642)
    api.add_argument("--reload", action="store_true")
    api.set_defaults(func=_cmd_serve_api)

    mcp = sub.add_parser(
        "serve-mcp",
        help="Serve the Grok MCP server (grok-4.6 chain on every tool)",
    )
    mcp.add_argument("--transport", default="stdio",
                     choices=["stdio", "streamable-http"])
    mcp.add_argument("--port", type=int, default=8643)
    mcp.set_defaults(func=_cmd_serve_mcp)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
