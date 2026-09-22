"""Tool-calling stage orchestration for the MiMo 2.6 pipeline."""

from __future__ import annotations

import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

from mimo.agents import AGENT_STAGES, AgentStage, build_stage_prompt, stage_by_name, tools_for_stage
from mimo.client import MimoClient
from mimo.models import MimoRunResult, RunRequest, StageRecord
from mimo.tools import ToolContext


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_json_atomic(path: Path, payload: str) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(payload, encoding="utf-8")
    temporary.replace(path)


def _validate_artifacts(run_dir: Path, stage: AgentStage) -> dict[str, str]:
    hashes: dict[str, str] = {}
    for name in stage.artifacts:
        path = run_dir / name
        if not path.is_file() or path.stat().st_size == 0:
            raise RuntimeError(f"{stage.name}: missing or empty artifact {name}")
        if name.endswith(".json"):
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                raise RuntimeError(f"{stage.name}: invalid JSON artifact {name}") from exc
            if not isinstance(payload, dict) or not payload:
                raise RuntimeError(f"{stage.name}: {name} must contain a non-empty object")
        hashes[name] = _sha256(path)
    return hashes


class ToolCallingPipeline:
    def __init__(self, *, client: MimoClient):
        self.client = client

    def _run_stage(
        self,
        stage: AgentStage,
        index: int,
        run_dir: Path,
        request: RunRequest,
        forced: set[str],
        feedback: dict[str, str] | None,
    ) -> dict[str, str]:
        record_path = run_dir / "stages" / f"{index:02d}-{stage.name}.json"
        result_path = run_dir / "stages" / f"{index:02d}-{stage.name}-result.json"
        record_path.parent.mkdir(exist_ok=True)
        prior = None
        if record_path.is_file():
            try:
                prior = StageRecord.model_validate_json(record_path.read_text(encoding="utf-8"))
            except ValueError:
                prior = None
        prompt = build_stage_prompt(
            stage,
            request,
            run_dir=run_dir,
            feedback=(feedback or {}).get(stage.name),
        )
        ctx = ToolContext(run_dir=run_dir)
        started = _now()
        record = StageRecord(
            name=stage.name,
            status="running",
            input_hash=hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
            trace_path=f"stages/{index:02d}-{stage.name}-trace.json",
            result_path=f"stages/{index:02d}-{stage.name}-result.json",
            started_utc=started,
        )
        _write_json_atomic(record_path, record.model_dump_json(indent=2))
        try:
            result = self.client.run_stage(
                stage_name=stage.name,
                prompt=prompt,
                tools=tools_for_stage(stage.name),
                ctx=ctx,
                expected_summary_keys=("summary", "artifacts", "checks", "notes"),
            )
            hashes = _validate_artifacts(run_dir, stage)
            if stage.name not in forced and prior and prior.status == "completed" and prior.artifact_hashes == hashes:
                record.status = "cached"
            else:
                record.status = "completed"
            record.artifact_hashes = hashes
            record.tool_calls = result.tool_calls
            record.completed_utc = _now()
            result_path.write_text(result.model_dump_json(indent=2), encoding="utf-8")
            (run_dir / record.trace_path).write_text(
                json.dumps({"call_log": ctx.call_log, "decisions": ctx.decisions}, indent=2),
                encoding="utf-8",
            )
            _write_json_atomic(record_path, record.model_dump_json(indent=2))
            return hashes
        except Exception as exc:  # noqa: BLE001 - record then re-raise
            record.status = "failed"
            record.error = str(exc)
            record.completed_utc = _now()
            _write_json_atomic(record_path, record.model_dump_json(indent=2))
            raise

    def run(
        self,
        run_dir: Path,
        request: RunRequest,
        *,
        from_stage: str | None = None,
        feedback: dict[str, str] | None = None,
    ) -> MimoRunResult:
        run_dir = Path(run_dir)
        forced: set[str] = set()
        if from_stage:
            stage_by_name(from_stage)
            forced = {from_stage}
            changed = True
            while changed:
                changed = False
                for stage in AGENT_STAGES:
                    if stage.name not in forced and set(stage.dependencies) & forced:
                        forced.add(stage.name)
                        changed = True

        intent = self._run_stage(stage_by_name("intent"), 1, run_dir, request, forced, feedback)

        def curriculum_lane() -> dict[str, str]:
            cartographer = self._run_stage(
                stage_by_name("cartographer"), 2, run_dir, request, forced, feedback
            )
            curriculum = self._run_stage(
                stage_by_name("curriculum"), 3, run_dir, request, forced, feedback
            )
            return {**cartographer, **curriculum}

        with ThreadPoolExecutor(max_workers=2, thread_name_prefix="mimo-stage") as pool:
            curriculum_future = pool.submit(curriculum_lane)
            math_future = pool.submit(
                self._run_stage,
                stage_by_name("math-director"),
                4,
                run_dir,
                request,
                forced,
                feedback,
            )
            curriculum = curriculum_future.result()
            math_dossier = math_future.result()

        cinematographer = self._run_stage(
            stage_by_name("cinematographer"), 5, run_dir, request, forced, feedback
        )
        scene = self._run_stage(
            stage_by_name("scene-composer"), 6, run_dir, request, forced, feedback
        )
        _ = intent, curriculum, math_dossier, cinematographer, scene
        scene_path = run_dir / "mimo_scene.py"
        source = scene_path.read_text(encoding="utf-8") if scene_path.is_file() else ""
        scene_name = "Unknown"
        for line in source.splitlines():
            if line.startswith("class "):
                scene_name = line.split()[1].split("(")[0]
                break
        return MimoRunResult(
            status="completed",
            scene_file="mimo_scene.py",
            scene_name=scene_name,
            artifacts=sorted(
                str(path.relative_to(run_dir)).replace("\\", "/")
                for path in run_dir.glob("*.json")
            )
            + ["mimo_scene.py"],
            rendered=False,
            video_path=None,
            checks=["tool-calling-stages-complete"],
            notes=["MiMo 2.6 tool-calling pipeline finished"],
            tool_calls=[],
        )
