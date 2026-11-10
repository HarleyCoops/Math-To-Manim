"""The math-to-manim-studio command line.

    math-to-manim-studio doctor              # check tools, render test shots, write env.lock.json
    math-to-manim-studio doctor --no-render  # check tools only
    math-to-manim-studio agent-check         # run one real agent through the runtime

More commands (run, resume, runs, serve-mcp, train) arrive with later milestones.
"""

from __future__ import annotations

import argparse

from studio import __version__


def _cmd_doctor(args: argparse.Namespace) -> int:
    from studio.doctor import run_doctor

    return run_doctor(render=not args.no_render)


def _cmd_agent_check(args: argparse.Namespace) -> int:
    from studio.agent_check import run_agent_check
    from studio.runtime import RuntimeUnavailable, get_runtime

    try:
        runtime = get_runtime(args.runtime)
    except RuntimeUnavailable as exc:
        print(f"agent-check: {exc}")
        return 1
    return run_agent_check(runtime=runtime)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="math-to-manim-studio",
        description="Studio: one scene description, three engines, a film and a web page.",
    )
    parser.add_argument("--version", action="version",
                        version=f"math-to-manim-studio {__version__}")
    sub = parser.add_subparsers(dest="cmd", required=True)

    doctor = sub.add_parser(
        "doctor", help="Check tools and versions, render one test shot per engine, "
                       "write env.lock.json")
    doctor.add_argument("--no-render", action="store_true",
                        help="check tools and versions only")
    doctor.set_defaults(func=_cmd_doctor)

    check = sub.add_parser(
        "agent-check", help="Run the Studio Doctor agent through the agent runtime")
    check.add_argument("--runtime", default=None,
                       choices=["local-sdk", "managed-agents"],
                       help="default: STUDIO_RUNTIME, else local-sdk")
    check.set_defaults(func=_cmd_agent_check)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
