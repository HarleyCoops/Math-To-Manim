"""Mythos harness: the 6-agent reasoning chain, driven through Claude Fable 5.

The agent charters ship with the package in ``src/mythos/agents/*.md``. This
harness reads them and drives them headlessly through the configured model
backend (see :mod:`mythos.backends`).

Chain (:data:`mythos.stages.STAGES`):
    intent -> cartographer -> curriculum -> math-director
           -> cinematographer -> scene-composer -> [codegen -> verify -> render]

Each reasoning stage receives the prior artifact JSON and must return one
JSON object. Codegen returns a complete Manim CE file inside one fenced
python block. Artifacts land in ``runs/mythos/<timestamp>-<slug>/`` (see
:mod:`mythos.layout`).

The pure pieces an operator may drive by hand are module functions:
``load_charter``, ``stage_prompt``, ``codegen_prompt``, ``repair_prompt``,
``check_scene`` and ``record_check`` (``scripts/operate_mythos_chain.py``).

Usage: ``math-to-manim-mythos run "explain quantum field theory" --render -q m``
"""

from __future__ import annotations

import json
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from mythos import backends
from mythos.backends import BackendAuthError, is_claude_cli_command
from mythos.charter import CINEMATIC_CHARTER, JSON_CONTRACT, extract_json_object, extract_python_block
from mythos.layout import (
    SCENE_FILE,
    VALIDATION_FILE,
    validation_template,
    create_run_dir,
    read_manifest,
    write_json,
    write_manifest,
)
from mythos.lifecycle import enter_stage, mark_run_completed, mark_run_failed, refresh_outcome
from mythos.manifest_schema import manifest_template, migrate_manifest
from mythos.prereq_cache import PrerequisiteCache
from mythos.render import RenderEnvironmentError, render_scene_file
from mythos.scene_checks import find_scene_class, validate_manim_code_report, validation_from_report
from mythos.settings import (
    DEFAULT_COMMAND,
    DEFAULT_MODEL,
    DEFAULT_RENDER_TIMEOUT,
    DEFAULT_TIMEOUT,
    default_runs_dir,
    model_fallbacks_from_env,
)
from mythos.stages import OFFLINE_SCENE, STAGES, Stage, offline_artifact, validate_stage_artifact

AGENT_DIR = Path(__file__).resolve().parent / "agents"

#: ``run_model(prompt, *, system_extra, command, model, timeout) -> str``
ModelRunner = Callable[..., str]
Logger = Callable[[str], None]


def log_to_stderr(message: str) -> None:
    print(f"  [mythos] {message}", file=sys.stderr, flush=True)


class StageValidationError(RuntimeError):
    """A reasoning stage returned a degenerate artifact twice in a row."""


@dataclass(frozen=True)
class RenderOutcome:
    exit_code: int
    output: str
    #: Missing render tool or timeout: model repair cannot help.
    blocked: bool


# ---------------------------------------------------------------------- #
# Pure chain steps                                                        #
# ---------------------------------------------------------------------- #

def load_charter(stage: Stage) -> str:
    """The stage's charter text, without its YAML front matter."""
    path = AGENT_DIR / stage.charter_file
    if not path.exists():
        raise FileNotFoundError(f"No charter {stage.charter_file!r} in {AGENT_DIR}")
    text = path.read_text(encoding="utf-8")
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            text = text[end + 4 :]
    return text.strip()


def stage_prompt(stage: Stage, prior: dict) -> str:
    """The exact prompt a reasoning stage receives (system extra: the Charter)."""
    return (
        f"{load_charter(stage)}\n\nINPUT ARTIFACT JSON:\n"
        f"{json.dumps(prior, indent=2)}{JSON_CONTRACT}"
    )


def retry_prompt(base_prompt: str, problem: str) -> str:
    return (
        f"{base_prompt}\n\nPREVIOUS ATTEMPT REJECTED: your last artifact "
        f"was degenerate ({problem}). The input artifact above contains "
        "real material — mine it. Return a complete, richly populated "
        "JSON object this time; empty lists and placeholder text are "
        "failures."
    )


def codegen_prompt(dossier: dict) -> str:
    """The prompt that turns the six stage artifacts into a Manim file."""
    return (
        "You are the Mythos scene composer's hands: write the film.\n"
        "Using the full dossier below (intent through scene spec), write ONE\n"
        "complete, runnable Manim Community Edition Python file that\n"
        "implements the shot list with the full Cinematic Charter — headlines\n"
        "before symbols, camera zooms into terms, plain-language captions,\n"
        "Mythos palette. The file must be self-contained (inline any helpers),\n"
        "import `from manim import *`, and define exactly one ThreeDScene\n"
        "subclass. Respond with exactly one fenced python block and nothing\n"
        "else.\n\nDOSSIER JSON:\n" + json.dumps(dossier, indent=2)
    )


def repair_prompt(code: str, failure: str) -> str:
    return (
        "The Manim scene below failed. Repair it surgically: preserve the\n"
        "cinematic structure, class name, and Charter rules; fix only what is\n"
        "broken. Manim CE APIs only. Respond with exactly one fenced\n"
        "python block containing the COMPLETE corrected file.\n\n"
        f"CURRENT FILE:\n{code}\n\n"
        f"FAILURE OUTPUT (tail):\n{failure[-8000:]}"
    )


def read_dossier(run_dir: Path) -> dict[str, Any]:
    """Every stage artifact present in ``run_dir``, keyed by file name."""
    return {
        stage.artifact: json.loads((run_dir / stage.artifact).read_text(encoding="utf-8"))
        for stage in STAGES if (run_dir / stage.artifact).exists()
    }


@dataclass(frozen=True)
class SceneCheck:
    """One static pass over a scene file: the verdict and its validation.json."""

    ok: bool
    failure: str | None
    validation: dict[str, Any]


def check_scene(code_path: Path, *, prompt: str | None = None) -> SceneCheck:
    """Static checks (AST, LaTeX fragments, charter and art-direction lint)."""
    source = code_path.read_text(encoding="utf-8")
    report = validate_manim_code_report(source, prompt=prompt)
    return SceneCheck(
        ok=report.valid,
        failure=None if report.valid else "; ".join(report.errors),
        validation=validation_from_report(report, source),
    )


def record_check(run_dir: Path, manifest: dict, check: SceneCheck) -> None:
    """Write ``validation.json`` and the manifest's static-check verdict."""
    write_json(run_dir / VALIDATION_FILE, check.validation)
    manifest["static_check"] = {
        "passed": check.ok,
        "detail": check.failure[:2000] if check.failure else None,
    }
    manifest.setdefault("status", {})["validation"] = "complete" if check.ok else "failed"


def new_manifest(run_dir: Path, *, prompt: str, model: str, command: str,
                 offline: bool) -> dict:
    """A fresh manifest plus the seeded ``validation.json``, both on disk."""
    manifest = manifest_template(
        run_id=run_dir.name, prompt=prompt, model=model, command=command,
        offline=offline, created_utc=datetime.now(timezone.utc).isoformat(),
    )
    write_json(run_dir / VALIDATION_FILE, validation_template())
    write_manifest(run_dir, manifest)
    return manifest


# ---------------------------------------------------------------------- #
# The harness                                                             #
# ---------------------------------------------------------------------- #

class MythosHarness:
    """Runs the full chain: six reasoning stages, codegen, verify, render, repair."""

    def __init__(
        self,
        *,
        command: str = DEFAULT_COMMAND,
        model: str = DEFAULT_MODEL,
        timeout: float = DEFAULT_TIMEOUT,
        render_timeout: float = DEFAULT_RENDER_TIMEOUT,
        offline: bool = False,
        runs_dir: Path | None = None,
        model_fallbacks: tuple[str, ...] | None = None,
        run_model: ModelRunner = backends.run_model,
        log: Logger = log_to_stderr,
    ):
        self.command = command
        self.model = model
        self.timeout = timeout
        self.render_timeout = render_timeout
        self.offline = offline
        self.runs_dir = Path(runs_dir) if runs_dir else default_runs_dir()
        self.model_fallbacks = (tuple(model_fallbacks)
                                if model_fallbacks is not None
                                else model_fallbacks_from_env())
        self.run_model = run_model
        self.log = log
        self.fallbacks_used: list[dict] = []

    # ------------------------------------------------------------------ #
    # Model plumbing                                                      #
    # ------------------------------------------------------------------ #

    def _model(self, prompt: str, *, system_extra: str | None = None) -> str:
        """One model call, with an Anthropic fallback ladder on the Claude CLI.

        Auth failures raise immediately (a broken login is broken for every
        model). Model-specific failures walk M2M_MODEL_FALLBACKS through the
        same CLI subscription login; the first model that answers becomes the
        baseline for the rest of the run and the switch is recorded in the
        manifest.
        """
        try:
            return self._call(prompt, system_extra, self.model)
        except BackendAuthError:
            raise
        except RuntimeError as primary_exc:
            if not is_claude_cli_command(self.command):
                raise
            candidates = [m for m in self.model_fallbacks if m != self.model]
            if not candidates:
                raise
            last_exc: RuntimeError = primary_exc
            failed = self.model
            for fallback in candidates:
                reason = str(last_exc).splitlines()[0][:200]
                self.log(f"model {failed!r} failed ({reason}); falling back to {fallback!r}")
                try:
                    output = self._call(prompt, system_extra, fallback)
                except BackendAuthError:
                    raise
                except RuntimeError as exc:
                    last_exc = exc
                    failed = fallback
                    continue
                self.fallbacks_used.append({
                    "from": self.model,
                    "to": fallback,
                    "reason": str(primary_exc).splitlines()[0][:300],
                })
                self.model = fallback  # sticky for the rest of the run
                return output
            tried = [self.model, *candidates]
            raise RuntimeError(
                "All Anthropic models failed via the Claude CLI "
                f"(tried, in order: {', '.join(tried)}). Last error:\n"
                f"{last_exc}"
            ) from last_exc

    def _call(self, prompt: str, system_extra: str | None, model: str) -> str:
        return self.run_model(prompt, system_extra=system_extra, command=self.command,
                              model=model, timeout=self.timeout)

    # ------------------------------------------------------------------ #
    # Run                                                                 #
    # ------------------------------------------------------------------ #

    def run(
        self,
        prompt: str,
        *,
        render: bool = False,
        quality: str = "l",
        max_repairs: int = 3,
        run_dir_callback: Callable[[str], None] | None = None,
    ) -> dict:
        prompt = prompt.replace(chr(0xFEFF), "").strip()
        run_dir = create_run_dir(self.runs_dir, prompt)
        if run_dir_callback is not None:
            run_dir_callback(run_dir.name)
        manifest = new_manifest(run_dir, prompt=prompt, model=self.model,
                                command=self.command, offline=self.offline)
        enter_stage(manifest, STAGES[0].slug)
        self._save(run_dir, manifest)
        try:
            return self._run_chain(prompt, run_dir, manifest, render=render,
                                   quality=quality, max_repairs=max_repairs)
        except BaseException as exc:
            # Without this record a crashed run is the same on disk as a run
            # in progress. status.stage keeps the step that failed.
            mark_run_failed(manifest, exc)
            try:
                self._save(run_dir, manifest)
            except Exception:  # noqa: BLE001 - never mask the original error
                pass
            raise

    def _run_chain(self, prompt: str, run_dir: Path, manifest: dict, *,
                   render: bool, quality: str, max_repairs: int) -> dict:
        prereq_cache = PrerequisiteCache.for_runs_dir(self.runs_dir)

        artifact: dict = {"user_prompt": prompt}
        for index, stage in enumerate(STAGES):
            started = time.time()
            retried = False
            if self.offline:
                artifact = offline_artifact(stage, prompt, artifact)
            else:
                artifact, retried = self._run_stage(stage, artifact, run_dir)
            (run_dir / stage.artifact).write_text(
                json.dumps(artifact, indent=2), encoding="utf-8")
            if stage.caches_prerequisites:
                prereq_cache.ingest_knowledge_map(prompt, artifact)
            stage_record = {"stage": stage.slug, "artifact": stage.artifact,
                            "seconds": round(time.time() - started, 2)}
            if retried:
                stage_record["retried"] = True
            manifest["stages"].append(stage_record)
            enter_stage(manifest, STAGES[index + 1].slug
                        if index + 1 < len(STAGES) else "codegen")
            self._save(run_dir, manifest)
            self.log(f"{stage.slug:<16} -> {stage.artifact}")

        code_path, scene_name = self._codegen(run_dir, prompt, artifact, manifest)
        check = check_scene(code_path, prompt=prompt)
        record_check(run_dir, manifest, check)

        if render:
            attempt = 0
            while True:
                failure = check.failure
                if check.ok:
                    enter_stage(manifest, "render")
                    self._save(run_dir, manifest)
                    outcome = self._render_and_record(
                        run_dir, manifest, code_path, scene_name, quality,
                        log_name=f"render_{attempt}.log", attempt=attempt)
                    self._save(run_dir, manifest)
                    if outcome.exit_code == 0 or outcome.blocked:
                        break
                    failure = outcome.output
                if attempt >= max_repairs or self.offline:
                    break
                attempt += 1
                self.log(f"repair attempt {attempt}")
                enter_stage(manifest, "repair")
                self._save(run_dir, manifest)
                code_path, scene_name = self._repair(
                    run_dir, code_path, failure or "unknown failure", attempt, manifest)
                check = check_scene(code_path, prompt=prompt)
                record_check(run_dir, manifest, check)

        manifest["scene_file"] = str(code_path)
        manifest["scene_name"] = scene_name
        manifest["completed_utc"] = datetime.now(timezone.utc).isoformat()
        mark_run_completed(manifest)
        self._save(run_dir, manifest)
        outcome = "render blocked" if manifest.get("render_error") else "run complete"
        self.log(f"{outcome} -> {run_dir}")
        return manifest

    def render_workspace(
        self,
        run_dir: Path,
        scene_name: str,
        quality: str = "l",
    ) -> dict:
        """Render an already-initialized run directory and update its manifest."""
        run_dir = Path(run_dir)
        manifest = migrate_manifest(read_manifest(run_dir))
        outcome = self._render_and_record(
            run_dir, manifest, run_dir / SCENE_FILE, scene_name, quality,
            log_name=f"render_workspace_{len(manifest.get('renders', []))}.log")
        refresh_outcome(manifest)
        write_manifest(run_dir, manifest)
        return {"exit_code": outcome.exit_code, "output": outcome.output,
                "manifest": manifest}

    # ------------------------------------------------------------------ #
    # Stage execution with degenerate-output retry                        #
    # ------------------------------------------------------------------ #

    def _run_stage(self, stage: Stage, prior: dict, run_dir: Path) -> tuple[dict, bool]:
        """Run one reasoning stage; retry once if the artifact is degenerate."""
        base_prompt = stage_prompt(stage, prior)
        raw = self._model(base_prompt, system_extra=CINEMATIC_CHARTER)
        (run_dir / f"{stage.stem}.raw.txt").write_text(raw, encoding="utf-8")
        artifact = extract_json_object(raw)
        problem = validate_stage_artifact(stage.slug, artifact)
        if problem is None:
            return artifact, False

        self.log(f"{stage.slug}: degenerate output ({problem}); retrying")
        raw = self._model(retry_prompt(base_prompt, problem), system_extra=CINEMATIC_CHARTER)
        (run_dir / f"{stage.stem}.retry.raw.txt").write_text(raw, encoding="utf-8")
        artifact = extract_json_object(raw)
        problem = validate_stage_artifact(stage.slug, artifact)
        if problem is not None:
            raise StageValidationError(
                f"Stage {stage.slug!r} returned a degenerate artifact twice "
                f"({problem}). Aborting instead of filming an empty story. "
                f"Inspect {run_dir / stage.artifact} and the .raw.txt traces."
            )
        return artifact, True

    # ------------------------------------------------------------------ #
    # Codegen / render / repair                                           #
    # ------------------------------------------------------------------ #

    def _codegen(self, run_dir: Path, prompt: str, scene_spec: dict,
                 manifest: dict) -> tuple[Path, str]:
        started = time.time()
        if self.offline:
            code = OFFLINE_SCENE
        else:
            raw = self._model(codegen_prompt(read_dossier(run_dir)),
                              system_extra=CINEMATIC_CHARTER)
            (run_dir / "07_codegen.raw.txt").write_text(raw, encoding="utf-8")
            code = extract_python_block(raw)
        code_path = run_dir / SCENE_FILE
        code_path.write_text(code, encoding="utf-8")
        scene_name = find_scene_class(code)
        manifest["stages"].append(
            {"stage": "codegen", "artifact": SCENE_FILE,
             "seconds": round(time.time() - started, 2)})
        enter_stage(manifest, "verify")
        self._save(run_dir, manifest)
        self.log(f"{'codegen':<16} -> {SCENE_FILE} ({scene_name})")
        return code_path, scene_name

    def _render_and_record(self, run_dir: Path, manifest: dict, code_path: Path,
                           scene_name: str, quality: str, *, log_name: str,
                           attempt: int | None = None) -> RenderOutcome:
        """One render; the log file, render record and status land in the manifest.

        The caller persists the manifest.
        """
        self.log(f"rendering {scene_name} -q{quality} in {run_dir}")
        manifest.pop("render_error", None)
        environment_error = None
        timed_out = False
        try:
            result = render_scene_file(
                run_dir, scene_file=code_path, scene_name=scene_name,
                quality=quality, timeout=self.render_timeout)
            exit_code, output, timed_out = result.exit_code, result.output, result.timed_out
        except RenderEnvironmentError as exc:
            environment_error = exc.to_dict()
            exit_code, output = exc.exit_code, exc.output + "\n" + str(exc)
        (run_dir / log_name).write_text(output, encoding="utf-8")
        record: dict[str, Any] = {"exit_code": exit_code, "log": log_name}
        if attempt is not None:
            record = {"attempt": attempt, **record}
        if environment_error:
            record["error"] = environment_error
            manifest["render_error"] = environment_error
            self.log(environment_error["detail"])
        if timed_out:
            # A timeout is a budget problem, not a code problem — don't burn
            # model-repair attempts on it.
            manifest["render_timed_out"] = True
        manifest.setdefault("renders", []).append(record)
        manifest.setdefault("status", {})["render"] = "complete" if exit_code == 0 else "failed"
        return RenderOutcome(exit_code, output, bool(environment_error) or timed_out)

    def _repair(self, run_dir: Path, code_path: Path, failure: str,
                attempt: int, manifest: dict) -> tuple[Path, str]:
        raw = self._model(repair_prompt(code_path.read_text(encoding="utf-8"), failure),
                          system_extra=CINEMATIC_CHARTER)
        (run_dir / f"repair_{attempt}.raw.txt").write_text(raw, encoding="utf-8")
        code = extract_python_block(raw)
        code_path.write_text(code, encoding="utf-8")
        manifest["stages"].append({"stage": f"repair_{attempt}",
                                   "artifact": code_path.name})
        enter_stage(manifest, "verify")
        self._save(run_dir, manifest)
        return code_path, find_scene_class(code)

    # ------------------------------------------------------------------ #
    # Bookkeeping                                                         #
    # ------------------------------------------------------------------ #

    def _save(self, run_dir: Path, manifest: dict) -> None:
        """Persist the manifest, stamping the model actually in use."""
        manifest["model"] = self.model  # may have walked the fallback ladder
        if self.fallbacks_used:
            manifest["model_fallbacks"] = list(self.fallbacks_used)
        write_manifest(run_dir, manifest)
