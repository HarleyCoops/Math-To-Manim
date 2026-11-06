"""Service facade for the MiMo 2.6 silo."""

from __future__ import annotations

from mimo.harness import MimoHarness
from mimo.models import RunRequest, RunManifest


class MimoService:
    def __init__(self) -> None:
        self.harness = MimoHarness()

    def run(self, request: RunRequest) -> dict:
        return self.harness.run(request)

    def list_runs(self, *, limit: int = 20) -> list[RunManifest]:
        return self.harness.list_runs(limit=limit)

    def get_run(self, run_id: str) -> RunManifest:
        return self.harness.get_run(run_id)

    def resume(self, run_id: str, *, from_stage: str | None = None) -> dict:
        manifest = self.get_run(run_id)
        request = RunRequest(
            prompt=manifest.prompt,
            render=manifest.render_requested,
            quality=manifest.quality,  # type: ignore[arg-type]
            offline=manifest.offline,
        )
        run_dir = self.harness.runs_dir / run_id
        from mimo.staged import ToolCallingPipeline

        result = ToolCallingPipeline(client=self.harness.client).run(
            run_dir, request, from_stage=from_stage
        )
        return result.model_dump()
