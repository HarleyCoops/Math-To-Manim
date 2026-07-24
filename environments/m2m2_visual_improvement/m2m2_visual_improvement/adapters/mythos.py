"""Mythos run-bundle adapter."""

from pathlib import Path

from .common import TaskBundle, build_bundle


def export_mythos_run(run_dir: Path) -> TaskBundle:
    return build_bundle(
        run_dir,
        provider="mythos",
        default_scene_file="mythos_scene.py",
        require_review=False,
    )


__all__ = ["export_mythos_run"]
