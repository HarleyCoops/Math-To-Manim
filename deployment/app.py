"""Base44 preview: a curated lesson, never an unauthenticated agent runner."""
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

ROOT = Path(__file__).resolve().parents[1]
app = FastAPI(title="The Third Side · Math To Manim", docs_url=None, redoc_url=None)


@app.get("/health")
def health():
    return {"status": "ok", "lesson": "the-third-side"}


@app.get("/")
def index():
    return FileResponse(ROOT / "web" / "index.html")


app.mount("/web", StaticFiles(directory=ROOT / "web"), name="web")
app.mount("/films", StaticFiles(directory=ROOT / "docs/showcase/assets"), name="films")
