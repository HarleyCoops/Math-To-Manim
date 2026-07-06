"""Math-To-Manim REST API: a thin FastAPI wrapper over MythosService.

Run it:
    math-to-manim serve-api                # http://127.0.0.1:8642
    uvicorn mythos.api:app --reload

Endpoints:
    GET  /health                             liveness + version
    POST /v1/runs                            submit a prompt (async job)
    GET  /v1/runs                            on-disk run ledger
    GET  /v1/runs/{run_id}                   manifest + artifact list
    GET  /v1/runs/{run_id}/artifacts/{name}  one artifact's content
    GET  /v1/jobs                            in-memory job list
    GET  /v1/jobs/{job_id}                   job status (poll this)
"""

from __future__ import annotations

from typing import Any, Literal

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import PlainTextResponse
    from pydantic import BaseModel, Field
except ImportError as exc:  # pragma: no cover
    raise RuntimeError(
        "The REST API requires the 'api' extra: pip install -e '.[api]'"
    ) from exc

from mythos import __version__
from mythos.backends import DEFAULT_COMMAND, DEFAULT_MODEL
from mythos.service import MythosService


class RunRequest(BaseModel):
    """Body for POST /v1/runs."""

    prompt: str = Field(..., min_length=3, max_length=4000,
                        description="What should the film explain?")
    render: bool = Field(default=False,
                         description="Render the scene after codegen")
    quality: Literal["l", "m", "h", "p", "k"] = Field(
        default="l", description="Manim quality flag")
    offline: bool = Field(default=False,
                          description="Deterministic rehearsal, no model calls")
    model: str = Field(default=DEFAULT_MODEL, description="Baseline model")
    command: str = Field(default=DEFAULT_COMMAND,
                         description="Backend: claude, codex, or fugu-api")
    max_repairs: int = Field(default=3, ge=0, le=10)


def create_app(service: MythosService | None = None) -> "FastAPI":
    svc = service or MythosService()
    app = FastAPI(
        title="Math-To-Manim API",
        version=__version__,
        description="One sentence in, a cinematic Manim film out — "
                    "driven by the Mythos 6-agent chain on Claude Fable 5.",
    )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "version": __version__}

    @app.post("/v1/runs", status_code=202)
    def create_run(request: RunRequest) -> dict[str, Any]:
        job = svc.submit(
            request.prompt,
            render=request.render,
            quality=request.quality,
            offline=request.offline,
            model=request.model,
            command=request.command,
            max_repairs=request.max_repairs,
        )
        return job.to_dict()

    @app.get("/v1/jobs")
    def list_jobs() -> list[dict[str, Any]]:
        return [job.to_dict() for job in svc.list_jobs()]

    @app.get("/v1/jobs/{job_id}")
    def get_job(job_id: str) -> dict[str, Any]:
        job = svc.get_job(job_id)
        if job is None:
            raise HTTPException(status_code=404, detail=f"No job {job_id!r}")
        return job.to_dict()

    @app.get("/v1/runs")
    def list_runs(limit: int = 50) -> list[dict[str, Any]]:
        return svc.list_runs(limit=max(1, min(limit, 500)))

    @app.get("/v1/runs/{run_id}")
    def get_run(run_id: str) -> dict[str, Any]:
        try:
            return svc.get_run(run_id)
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    @app.get("/v1/runs/{run_id}/artifacts/{artifact_name}",
             response_class=PlainTextResponse)
    def get_artifact(run_id: str, artifact_name: str) -> str:
        try:
            return svc.read_artifact(run_id, artifact_name)
        except FileNotFoundError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    return app


app = create_app()
