"""The two writing agents: the Director writes a brief, the Spec Author a SceneSpec.

Each agent answers with one JSON object. Code checks the answer. If the check
fails, the same agent is asked again with the list of problems, up to
``ATTEMPTS`` times. Every call is recorded in ``trace.jsonl`` in the run
folder, with the prompt and the reply saved beside it.
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, TypeVar

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from studio.runtime import AgentRuntime, load_agent_file
from studio.spec.models import SceneSpec

AGENTS_DIR = Path(__file__).resolve().parent / "agents"
ATTEMPTS = 3
T = TypeVar("T")

#: Limits that keep a film inside what this machine renders in minutes.
MAX_FILM_SECONDS = 60.0
MAX_SCENE3D_SHOTS = 4
MAX_SCENE3D_SECONDS = 6.0
MAX_PIXELS = 1280 * 720
MAX_FPS = 30


class AuthoringFailed(RuntimeError):
    """An agent did not produce a valid answer in the allowed attempts."""


class BriefEquation(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    latex: str
    meaning: str = ""


class Beat(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str
    idea: str
    narration: str
    visual: str
    kind: str = "card"
    equations: list[str] = Field(default_factory=list)


class Brief(BaseModel):
    model_config = ConfigDict(extra="ignore")
    title: str
    audience: str = ""
    answer: str
    prerequisites: list[str] = Field(default_factory=list)
    equations: list[BriefEquation] = Field(default_factory=list, max_length=3)
    beats: list[Beat] = Field(min_length=3, max_length=8)
    not_verified: list[str] = Field(default_factory=list)


def extract_json(text: str) -> dict[str, Any]:
    """The first complete JSON object in ``text`` (plain, or inside a code fence)."""
    decoder = json.JSONDecoder()
    position = text.find("{")
    while position != -1:
        try:
            value, _ = decoder.raw_decode(text[position:])
        except ValueError:
            position = text.find("{", position + 1)
            continue
        if isinstance(value, dict):
            return value
        position = text.find("{", position + 1)
    raise ValueError("the reply holds no JSON object")


def check_budget(spec: SceneSpec) -> list[str]:
    """Film rules that the schema cannot express. Returns the problems found."""
    problems = []
    world = spec.world
    if world.width * world.height > MAX_PIXELS or world.fps > MAX_FPS:
        problems.append(f"world must be at most 1280x720 at {MAX_FPS} fps")
    if spec.duration_s() > MAX_FILM_SECONDS:
        problems.append(f"film is {spec.duration_s():.1f} s; the limit is {MAX_FILM_SECONDS:.0f} s")
    scenes = [shot for shot in spec.shots if shot.kind == "scene3d"]
    if len(scenes) > MAX_SCENE3D_SHOTS:
        problems.append(f"{len(scenes)} scene3d shots; the limit is {MAX_SCENE3D_SHOTS}")
    problems += [f"shot {shot.id!r}: a scene3d shot is at most {MAX_SCENE3D_SECONDS:.0f} s"
                 for shot in scenes
                 if spec.frame_count(shot) / world.fps > MAX_SCENE3D_SECONDS]
    if spec.shots[0].kind != "card" or spec.shots[-1].kind != "card":
        problems.append("the first shot and the last shot must be cards")
    problems += [f"shot {shot.id!r}: a card shows at most 2 equations"
                 for shot in spec.shots if shot.kind == "card" and len(shot.equations) > 2]
    return problems


def parse_brief(data: dict[str, Any]) -> Brief:
    return Brief.model_validate(data)


def parse_spec(data: dict[str, Any]) -> SceneSpec:
    spec = SceneSpec.model_validate(data)
    problems = check_budget(spec)
    if problems:
        raise ValueError("; ".join(problems))
    return spec


def _problems(exc: Exception) -> str:
    if isinstance(exc, ValidationError):
        return "\n".join(f"- {'.'.join(str(p) for p in e['loc']) or 'file'}: {e['msg']}"
                         for e in exc.errors()[:25])
    return f"- {exc}"


def ask(runtime: AgentRuntime, agent_file: str, step: str, prompt: str,
        parse: Callable[[dict[str, Any]], T], run_dir: Path,
        log: Callable[[str], None] = print) -> T:
    """Ask one agent for a JSON object until ``parse`` accepts it."""
    spec = load_agent_file(AGENTS_DIR / agent_file)
    folder = run_dir / "agents"
    folder.mkdir(parents=True, exist_ok=True)
    current = prompt
    last_problem = ""
    for attempt in range(1, ATTEMPTS + 1):
        (folder / f"{step}_{attempt}_prompt.txt").write_text(current, encoding="utf-8")
        started = time.perf_counter()
        result = runtime.run(spec, current, cwd=folder)
        reply = result.text or ""
        (folder / f"{step}_{attempt}_reply.txt").write_text(reply, encoding="utf-8")
        record = {
            "utc": datetime.now(timezone.utc).isoformat(), "step": step, "agent": spec.name,
            "runtime": result.runtime, "model": result.model, "attempt": attempt,
            "prompt_chars": len(current), "reply_chars": len(reply),
            "seconds": round(time.perf_counter() - started, 1), "turns": result.turns,
            "cost_usd": result.cost_usd, "session_id": result.session_id,
            "accepted": False, "problem": None,
        }
        try:
            if not result.ok:
                raise AuthoringFailed(f"runtime error: {result.error}")
            value = parse(extract_json(reply))
        except AuthoringFailed as exc:
            record["problem"] = str(exc)
            _trace(run_dir, record)
            raise
        except (ValueError, ValidationError) as exc:
            last_problem = _problems(exc)
            record["problem"] = last_problem[:2000]
            _trace(run_dir, record)
            log(f"  {spec.name}: attempt {attempt} rejected")
            current = (f"{prompt}\n\nYour previous answer was rejected by the checker:\n"
                       f"{last_problem}\n\nYour previous answer:\n{reply[:12000]}\n\n"
                       "Return the corrected JSON object only.")
            continue
        record["accepted"] = True
        _trace(run_dir, record)
        return value
    raise AuthoringFailed(
        f"{spec.name} gave no valid answer in {ATTEMPTS} attempts. Last problems:\n"
        f"{last_problem}")


def _trace(run_dir: Path, record: dict[str, Any]) -> None:
    with (run_dir / "trace.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record) + "\n")


def direct(runtime: AgentRuntime, question: str, run_dir: Path,
           log: Callable[[str], None] = print) -> Brief:
    return ask(runtime, "director.md", "director",
               f"The question the film must answer:\n\n{question}\n", parse_brief, run_dir, log)


def write_spec(runtime: AgentRuntime, question: str, brief: Brief, run_dir: Path,
               log: Callable[[str], None] = print) -> SceneSpec:
    prompt = (f"The question:\n\n{question}\n\nThe Director's brief:\n\n"
              f"{json.dumps(brief.model_dump(), indent=2)}\n\nWrite the SceneSpec.")
    return ask(runtime, "spec-author.md", "spec_author", prompt, parse_spec, run_dir, log)
