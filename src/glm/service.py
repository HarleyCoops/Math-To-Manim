"""Run ledger for the GLM-native pipeline: start runs, read manifests back.

This module never imports Mythos, Sol, or Grok.
"""

from __future__ import annotations

import json
from pathlib import Path

from glm.harness import GlmHarness
from glm.models import MANIFEST_FILE, RunManifest, RunRequest


class GlmService:
    def __init__(self, *, runs_dir: Path | None = None, harness: GlmHarness | None = None):
        self.harness = harness or GlmHarness(runs_dir=runs_dir)
        self.runs_dir = self.harness.runs_dir

    def run(self, request: RunRequest) -> dict:
        return self.harness.run(request)

    def get_run(self, run_id: str) -> RunManifest:
        manifest_path = self._resolve_run_dir(run_id) / MANIFEST_FILE
        if not manifest_path.is_file():
            raise FileNotFoundError(f"unknown GLM run: {run_id}")
        return RunManifest.model_validate(json.loads(manifest_path.read_text(encoding="utf-8")))

    def list_runs(self, *, limit: int = 20) -> list[RunManifest]:
        if not self.runs_dir.exists():
            return []
        manifests: list[RunManifest] = []
        for path in sorted(self.runs_dir.glob(f"*/{MANIFEST_FILE}"), reverse=True):
            try:
                manifests.append(
                    RunManifest.model_validate(json.loads(path.read_text(encoding="utf-8")))
                )
            except (OSError, ValueError):
                continue
            if len(manifests) >= limit:
                break
        return manifests

    def _resolve_run_dir(self, run_id: str) -> Path:
        if Path(run_id).name != run_id:
            raise ValueError("run_id must be a single directory name")
        run_dir = (self.runs_dir / run_id).resolve()
        runs_root = self.runs_dir.resolve()
        if runs_root not in run_dir.parents:
            raise ValueError(f"Invalid run_id: {run_id!r}")
        if not run_dir.is_dir():
            raise FileNotFoundError(f"unknown GLM run: {run_id}")
        return run_dir
