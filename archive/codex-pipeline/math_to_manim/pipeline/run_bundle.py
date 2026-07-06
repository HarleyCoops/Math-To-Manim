"""Helpers for rerendering and reviewing existing run bundles."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, TypeVar

from math_to_manim.schemas import GeneratedCode
from math_to_manim.schemas.base import ArtifactModel
from math_to_manim.tools import discover_scene_classes_in_file


ArtifactT = TypeVar("ArtifactT", bound=ArtifactModel)


class RunBundle:
    """Small typed facade over a generated ``runs/<id>`` directory."""

    def __init__(self, run_dir: str | Path):
        self.run_dir = Path(run_dir)
        if not self.run_dir.exists():
            raise FileNotFoundError(f"Run directory does not exist: {self.run_dir}")
        if not self.run_dir.is_dir():
            raise NotADirectoryError(f"Run path is not a directory: {self.run_dir}")

    @property
    def manifest_path(self) -> Path:
        return self.run_dir / "manifest.json"

    @property
    def generated_scene_path(self) -> Path:
        return self.run_dir / "generated_scene.py"

    def require_file(self, relative_path: str) -> Path:
        path = self.run_dir / relative_path
        if not path.exists():
            raise FileNotFoundError(f"Required run artifact is missing: {path}")
        return path

    def load_artifact(self, name: str, artifact_type: type[ArtifactT]) -> ArtifactT:
        path = self.require_file(f"{name}.json")
        return artifact_type.model_validate(json.loads(path.read_text(encoding="utf-8")))

    def save_artifact(self, name: str, artifact: ArtifactModel) -> Path:
        path = self.run_dir / f"{name}.json"
        path.write_text(
            json.dumps(artifact.to_public_dict(), indent=2, sort_keys=True, default=str) + "\n",
            encoding="utf-8",
        )
        self.update_manifest(name)
        return path

    def load_current_generated_code(self) -> GeneratedCode:
        generated = self.load_artifact("generated_code", GeneratedCode)
        scene_path = self.require_file("generated_scene.py")
        code = scene_path.read_text(encoding="utf-8")
        scene_name = _resolve_scene_name(scene_path, fallback=generated.scene_name)
        metadata = dict(generated.metadata)
        metadata.update({"source_code_path": str(scene_path), "source": "run_bundle_current_file"})
        return generated.model_copy(update={"code": code, "scene_name": scene_name, "metadata": metadata})

    def update_manifest(self, artifact_name: str) -> None:
        manifest = self._load_manifest()
        artifacts = set(manifest.get("artifacts") or [])
        artifacts.add(artifact_name)
        manifest["artifacts"] = sorted(artifacts)
        manifest.setdefault("run_dir", str(self.run_dir))
        self.manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def _load_manifest(self) -> dict[str, Any]:
        if not self.manifest_path.exists():
            return {"run_dir": str(self.run_dir), "artifacts": []}
        return json.loads(self.manifest_path.read_text(encoding="utf-8"))


def _resolve_scene_name(scene_path: Path, *, fallback: str) -> str:
    scenes = discover_scene_classes_in_file(scene_path, require_construct=True)
    if any(scene.name == fallback for scene in scenes):
        return fallback
    if scenes:
        return scenes[0].name
    return fallback
