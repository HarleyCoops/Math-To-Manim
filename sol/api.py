"""Standalone FastAPI application for the GPT-5.6 Sol silo."""

from __future__ import annotations

import hashlib

try:
    from fastapi import FastAPI, HTTPException, Request
except ImportError as exc:  # pragma: no cover
    raise RuntimeError("Install the API extra: pip install -e '.[api]'") from exc

from sol import __version__
from sol.models import CalculationRequest, CalculationResponse
from sol.offline import UnsupportedCalculation
from sol.service import SolService


def create_app(service: SolService | None = None) -> "FastAPI":
    calculator = service or SolService()
    app = FastAPI(
        title="Math-To-Manim: Sol",
        version=__version__,
        description="GPT-5.6 Sol calculates and verifies; deterministic code compiles the Manim scene.",
    )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "silo": "sol", "model": "gpt-5.6-sol", "version": __version__}

    @app.post("/v1/calculate", response_model=CalculationResponse)
    def calculate(payload: CalculationRequest, request: Request) -> CalculationResponse:
        identity = (
            request.headers.get("oai-authenticated-user-email")
            or (request.client.host if request.client else "anonymous")
        )
        safety_identifier = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:32]
        try:
            return calculator.calculate(payload, safety_identifier=safety_identifier)
        except UnsupportedCalculation as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        except RuntimeError as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc

    return app


app = create_app()
