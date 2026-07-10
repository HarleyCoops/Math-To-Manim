"""One Sol request in, one verified result and deterministic scene out."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from sol.client import SOL_MODEL, calculate_with_sol
from sol.manim import compile_manim
from sol.models import CalculationRequest, CalculationResponse
from sol.offline import calculate_locally


def default_runs_dir() -> Path:
    return Path(os.getenv("M2M2_RUNS_DIR", "runs")) / "sol"


class SolService:
    def __init__(self, *, runs_dir: Path | None = None):
        self.runs_dir = Path(runs_dir) if runs_dir else default_runs_dir()

    def calculate(
        self,
        request: CalculationRequest,
        *,
        safety_identifier: str | None = None,
    ) -> CalculationResponse:
        use_local = request.offline or not os.getenv("OPENAI_API_KEY")
        if use_local:
            result = calculate_locally(request.problem)
            engine = "local-symbolic"
        else:
            result = calculate_with_sol(request, safety_identifier=safety_identifier)
            engine = "gpt-5.6-sol"

        stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-%f")
        slug = re.sub(r"[^a-z0-9]+", "-", request.problem.lower()).strip("-")[:40] or "calculation"
        run_id = f"{stamp}-{slug}"
        run_dir = self.runs_dir / run_id
        run_dir.mkdir(parents=True, exist_ok=False)

        manim_source = compile_manim(result)
        scene_path = run_dir / "sol_scene.py"
        scene_path.write_text(manim_source, encoding="utf-8")
        (run_dir / "result.json").write_text(result.model_dump_json(indent=2), encoding="utf-8")

        video_path = None
        if request.render:
            manim = shutil.which("manim")
            if not manim:
                raise RuntimeError("Manim is not installed; rerun without render or install the render extra")
            completed = subprocess.run(
                [manim, "-ql", str(scene_path), "SolCalculationScene"],
                capture_output=True,
                text=True,
                timeout=300,
                check=False,
            )
            if completed.returncode != 0:
                raise RuntimeError(f"Manim render failed: {(completed.stderr or completed.stdout)[-2000:]}")
            candidates = list((Path("media") / "videos").glob("**/SolCalculationScene.mp4"))
            video_path = str(candidates[-1]) if candidates else None

        response = CalculationResponse(
            run_id=run_id,
            engine=engine,
            model=SOL_MODEL,
            result=result,
            manim_source=manim_source,
            video_path=video_path,
        )
        manifest = {
            "run_id": run_id,
            "created_utc": datetime.now(timezone.utc).isoformat(),
            "engine": engine,
            "model": SOL_MODEL,
            "problem": request.problem,
            "artifacts": ["result.json", "sol_scene.py"],
            "video_path": video_path,
        }
        (run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        return response
