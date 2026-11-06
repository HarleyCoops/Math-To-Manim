"""Run-ledger facade for the Codex CLI-native Sol pipeline."""

from __future__ import annotations

import json
from pathlib import Path

from sol.harness import SolHarness, default_runs_dir
from sol.manifest_schema import migrate_manifest
from sol.models import RunManifest, RunRequest


class SolService:
    def __init__(self, *, runs_dir: Path | None = None, harness: SolHarness | None = None):
        resolved = Path(runs_dir) if runs_dir else default_runs_dir()
        self.harness = harness or SolHarness(runs_dir=resolved)
        self.runs_dir = self.harness.runs_dir

    def run(self, request: RunRequest) -> dict:
        return self.harness.run(request)

    def resume(self, run_id: str, *, from_stage: str | None = None) -> dict:
        return self.harness.resume(run_id, from_stage=from_stage)

    def get_run(self, run_id: str) -> RunManifest:
        if Path(run_id).name != run_id:
            raise ValueError("run_id must be a single directory name")
        manifest_path = self.runs_dir / run_id / "manifest.json"
        if not manifest_path.is_file():
            raise FileNotFoundError(f"unknown Sol run: {run_id}")
        payload = migrate_manifest(json.loads(manifest_path.read_text(encoding="utf-8")))
        return RunManifest.model_validate(payload)

    def list_runs(self, *, limit: int = 20) -> list[RunManifest]:
        if not self.runs_dir.exists():
            return []
        manifests: list[RunManifest] = []
        for path in sorted(self.runs_dir.glob("*/manifest.json"), reverse=True):
            try:
                payload = migrate_manifest(json.loads(path.read_text(encoding="utf-8")))
                manifests.append(RunManifest.model_validate(payload))
            except (OSError, ValueError, json.JSONDecodeError):
                continue
            if len(manifests) >= limit:
                break
        return manifests
