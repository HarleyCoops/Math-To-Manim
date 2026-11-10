"""The math-to-manim-studio command line.

    math-to-manim-studio doctor              # check tools, render test shots, write env.lock.json
    math-to-manim-studio doctor --no-render  # check tools only
    math-to-manim-studio agent-check         # run one real agent through the runtime
    math-to-manim-studio render-shot SPEC --shot ID [--engine manim|blender]
    math-to-manim-studio compare SPEC --shot ID   # same shot in Manim and Blender

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


def _cmd_render_shot(args: argparse.Namespace) -> int:
    import json

    from studio.render import render_shot

    result = render_shot(args.spec, args.shot, engine=args.engine, samples=args.samples)
    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 1


def _cmd_compare(args: argparse.Namespace) -> int:
    import json

    from studio.render import compare_engines

    report = compare_engines(args.spec, args.shot, args.engines)
    print(json.dumps(report, indent=2))
    return 0 if report["ok"] else 1


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

    shot = sub.add_parser("render-shot", help="Render one shot of a SceneSpec file")
    shot.add_argument("spec", help="path of the SceneSpec JSON file")
    shot.add_argument("--shot", required=True, help="shot id")
    shot.add_argument("--engine", default=None, choices=["manim", "blender"],
                      help="default: the engine named in the shot")
    shot.add_argument("--samples", type=int, default=64, help="EEVEE samples")
    shot.set_defaults(func=_cmd_render_shot)

    compare = sub.add_parser(
        "compare", help="Render one shot with several engines and write comparison images")
    compare.add_argument("spec", help="path of the SceneSpec JSON file")
    compare.add_argument("--shot", required=True, help="shot id")
    compare.add_argument("--engines", nargs=2, default=["manim", "blender"],
                         choices=["manim", "blender"])
    compare.set_defaults(func=_cmd_compare)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
