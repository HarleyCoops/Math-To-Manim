"""Sol run-bundle adapter."""

from pathlib import Path

from .common import TaskBundle, build_bundle


def export_sol_run(run_dir: Path) -> TaskBundle:
    return build_bundle(
        run_dir,
        provider="sol",
        default_scene_file="sol_scene.py",
        require_review=True,
    )


__all__ = ["export_sol_run"]
