"""Mythos harness: the 6-agent reasoning chain, driven through Claude Fable 5.

The agent charters live in ``mythos/agents/*.md`` (mirrored to
``.claude/agents/`` for native Claude Code use). This harness reads those
same charters and drives them headlessly through the configured model
backend, so interactive sessions and automated runs share one source of
truth.

Chain:
    intent -> cartographer -> curriculum -> math-director
           -> cinematographer -> scene-composer -> [codegen -> verify -> render]

Each reasoning stage receives the prior artifact JSON and must return one
JSON object. Codegen returns a complete Manim CE file inside one fenced
python block. Artifacts land in ``runs/mythos/<timestamp>-<slug>/``.

Usage (from repo root):
    python -m mythos.harness "explain quantum field theory" --render -q m
    python -m mythos.harness "the heat equation" --offline      # no API needed
"""

from __future__ import annotations

import argparse
import json
import os
import py_compile
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from mythos.backends import (  # noqa: E402
    DEFAULT_COMMAND,
    DEFAULT_MODEL,
    DEFAULT_TIMEOUT,
    BackendAuthError,
    is_claude_cli_command,
    model_fallbacks_from_env,
    run_model,
)
from mythos.charter import (  # noqa: E402
    CINEMATIC_CHARTER,
    JSON_CONTRACT,
    extract_json_object,
    extract_python_block,
    find_scene_class,
    load_env_file,
)
from mythos.manifest_schema import (  # noqa: E402
    manifest_template,
    migrate_manifest,
    validation_template,
)
from mythos.prereq_cache import PrerequisiteCache  # noqa: E402
from mythos.render import (  # noqa: E402
    DEFAULT_RENDER_TIMEOUT,
    render_scene_file,
    resolve_manim,
)
from mythos.scene_checks import (  # noqa: E402
    validate_manim_code_report,
    validation_from_scene,
    write_json,
)

# Charter search order: user-local Claude Code dir first, then the tracked
# canonical copies that ship with the repo.
AGENT_DIRS = [
    REPO_ROOT / ".claude" / "agents",
    REPO_ROOT / "mythos" / "agents",
]

#: (slug, agent definition file, artifact name)
STAGES: list[tuple[str, str, str]] = [
    ("intent", "mythos-intent.md", "01_intent.json"),
    ("cartographer", "mythos-cartographer.md", "02_knowledge_map.json"),
    ("curriculum", "mythos-curriculum.md", "03_curriculum.json"),
    ("math-director", "mythos-math-director.md", "04_math_dossier.json"),
    ("cinematographer", "mythos-cinematographer.md", "05_shot_list.json"),
    ("scene-composer", "mythos-scene-composer.md", "06_scene_spec.json"),
]

_LINT_RULES = [
    (r"self\.camera\.animate",
     "never animate self.camera in a ThreeDScene; use move_camera"),
]

# DEFAULT_RENDER_TIMEOUT and resolve_manim live in mythos.render so the
# sandbox wrapper does not import this harness. Re-exported for callers.


class StageValidationError(RuntimeError):
    """A reasoning stage returned a degenerate artifact twice in a row."""


def validate_stage_artifact(slug: str, artifact: dict) -> str | None:
    """Reject degenerate stage output before it poisons the chain.

    Returns a human-readable problem description, or None when healthy.
    (A real failure mode: the math-director once returned
    ``{"formulas": [], "color_identity": {}, "numbers": []}`` — 48 bytes —
    and every downstream agent faithfully storyboarded an empty film.)
    """
    if not isinstance(artifact, dict) or not artifact:
        return "artifact is not a non-empty JSON object"
    size = len(json.dumps(artifact))
    if slug == "math-director":
        formulas = artifact.get("formulas")
        if isinstance(formulas, list) and not formulas:
            return "math dossier has an empty 'formulas' list"
        if size < 500:
            return f"math dossier is only {size} bytes"
    elif slug == "cinematographer":
        shots = artifact.get("shots")
        if isinstance(shots, list) and len(shots) < 8:
            return f"shot list has only {len(shots)} beats"
        if size < 500:
            return f"shot list is only {size} bytes"
    elif size < 200:
        return f"artifact is only {size} bytes"
    return None


def _requires_light_art_direction(prompt: str) -> bool:
    text = prompt.lower()
    positive = ("off-white", "archival", "paper", "warm paper")
    negative = ("no black", "not black", "never black", "non-black")
    return any(term in text for term in positive) and any(
        term in text for term in negative)


def default_runs_dir() -> Path:
    load_env_file()
    return Path(
        os.getenv("M2M_RUNS_DIR")
        or os.getenv("M2M2_RUNS_DIR")
        or str(REPO_ROOT / "runs")
    ) / "mythos"


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
    ):
        self.command = command
        self.model = model
        self.timeout = timeout
        self.render_timeout = render_timeout
        self.offline = offline
        self.runs_dir = runs_dir or default_runs_dir()
        self.model_fallbacks = (tuple(model_fallbacks)
                                if model_fallbacks is not None
                                else model_fallbacks_from_env())
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
            return run_model(
                prompt,
                system_extra=system_extra,
                command=self.command,
                model=self.model,
                timeout=self.timeout,
            )
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
                print(f"  [mythos] model {failed!r} failed ({reason}); "
                      f"falling back to {fallback!r}")
                try:
                    output = run_model(
                        prompt,
                        system_extra=system_extra,
                        command=self.command,
                        model=fallback,
                        timeout=self.timeout,
                    )
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

    # ------------------------------------------------------------------ #
    # Charters                                                            #
    # ------------------------------------------------------------------ #

    @staticmethod
    def load_charter(agent_file: str) -> str:
        for candidate in AGENT_DIRS:
            if (candidate / agent_file).exists():
                path = candidate / agent_file
                break
        else:
            raise FileNotFoundError(
                f"No charter {agent_file!r} in any of: "
                + ", ".join(str(d) for d in AGENT_DIRS)
            )
        text = path.read_text(encoding="utf-8")
        if text.startswith("---"):
            end = text.find("\n---", 3)
            if end != -1:
                text = text[end + 4 :]
        return text.strip()

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
        run_dir_callback=None,
    ) -> dict:
        prompt = prompt.replace(chr(0xFEFF), "").strip()
        run_dir = self._create_run_dir(prompt)
        if run_dir_callback is not None:
            run_dir_callback(run_dir.name)
        manifest = manifest_template(
            run_id=run_dir.name,
            prompt=prompt,
            model=self.model,
            command=self.command,
            offline=self.offline,
            created_utc=datetime.now(timezone.utc).isoformat(),
        )
        write_json(run_dir / "validation.json", validation_template())
        self._write_manifest(run_dir, manifest)
        prereq_cache = PrerequisiteCache.for_runs_dir(self.runs_dir)

        artifact: dict = {"user_prompt": prompt}
        for slug, agent_file, artifact_name in STAGES:
            started = time.time()
            retried = False
            if self.offline:
                artifact = _offline_artifact(slug, prompt, artifact)
            else:
                artifact, retried = self._run_stage(
                    slug, agent_file, artifact, run_dir, artifact_name)
            (run_dir / artifact_name).write_text(
                json.dumps(artifact, indent=2), encoding="utf-8")
            if slug == "cartographer":
                prereq_cache.ingest_knowledge_map(prompt, artifact)
            stage_record = {"stage": slug, "artifact": artifact_name,
                            "seconds": round(time.time() - started, 2)}
            if retried:
                stage_record["retried"] = True
            manifest["stages"].append(stage_record)
            manifest["model"] = self.model  # may have walked the fallback ladder
            if self.fallbacks_used:
                manifest["model_fallbacks"] = list(self.fallbacks_used)
            self._write_manifest(run_dir, manifest)
            print(f"  [mythos] {slug:<16} -> {artifact_name}")

        code_path, scene_name = self._codegen(run_dir, prompt, artifact, manifest)
        ok, failure = self._verify(code_path, prompt=prompt)
        self._record_validation(run_dir, manifest, code_path, ok, failure)

        if render:
            attempt = 0
            while True:
                if ok:
                    rc, out = self._render(code_path, scene_name, quality)
                    manifest.setdefault("renders", []).append(
                        {"attempt": attempt, "exit_code": rc})
                    if rc == 0:
                        manifest.setdefault("status", {})
                        manifest["status"]["render"] = "complete"
                        break
                    manifest.setdefault("status", {})
                    manifest["status"]["render"] = "failed"
                    failure = out
                    if rc == 124:
                        # A timeout is a budget problem, not a code problem —
                        # don't burn model-repair attempts on it.
                        manifest["render_timed_out"] = True
                        break
                if attempt >= max_repairs or self.offline:
                    break
                attempt += 1
                print(f"  [mythos] repair attempt {attempt}")
                code_path, scene_name = self._repair(
                    run_dir, code_path, failure or "unknown failure",
                    attempt, manifest)
                ok, failure = self._verify(code_path, prompt=prompt)
                self._record_validation(run_dir, manifest, code_path, ok, failure)

        manifest["scene_file"] = str(code_path)
        manifest["scene_name"] = scene_name
        manifest["model"] = self.model  # codegen/repair may have fallen back too
        if self.fallbacks_used:
            manifest["model_fallbacks"] = list(self.fallbacks_used)
        manifest["completed_utc"] = datetime.now(timezone.utc).isoformat()
        self._write_manifest(run_dir, manifest)
        print(f"  [mythos] run complete -> {run_dir}")
        return manifest

    def render_workspace(
        self,
        run_dir: Path,
        scene_name: str,
        quality: str = "l",
    ) -> dict:
        """Render an already-initialized run directory and update its manifest."""
        run_dir = Path(run_dir)
        manifest_path = run_dir / "manifest.json"
        manifest = migrate_manifest(json.loads(manifest_path.read_text(encoding="utf-8")))
        scene_file = run_dir / "mythos_scene.py"
        code, output = self._render(scene_file, scene_name, quality)
        manifest.setdefault("renders", []).append({"exit_code": code})
        manifest.setdefault("status", {})
        manifest["status"]["render"] = "complete" if code == 0 else "failed"
        self._write_manifest(run_dir, manifest)
        return {"exit_code": code, "output": output, "manifest": manifest}

    # ------------------------------------------------------------------ #
    # Stage execution with degenerate-output retry                        #
    # ------------------------------------------------------------------ #

    def _run_stage(self, slug: str, agent_file: str, prior: dict,
                   run_dir: Path, artifact_name: str) -> tuple[dict, bool]:
        """Run one reasoning stage; retry once if the artifact is degenerate."""
        charter = self.load_charter(agent_file)
        base_prompt = (
            f"{charter}\n\nINPUT ARTIFACT JSON:\n"
            f"{json.dumps(prior, indent=2)}{JSON_CONTRACT}"
        )
        raw = self._model(base_prompt, system_extra=CINEMATIC_CHARTER)
        (run_dir / f"{artifact_name.split('.')[0]}.raw.txt").write_text(
            raw, encoding="utf-8")
        artifact = extract_json_object(raw)
        problem = validate_stage_artifact(slug, artifact)
        if problem is None:
            return artifact, False

        print(f"  [mythos] {slug}: degenerate output ({problem}); retrying")
        retry_prompt = (
            f"{base_prompt}\n\nPREVIOUS ATTEMPT REJECTED: your last artifact "
            f"was degenerate ({problem}). The input artifact above contains "
            "real material — mine it. Return a complete, richly populated "
            "JSON object this time; empty lists and placeholder text are "
            "failures."
        )
        raw = self._model(retry_prompt, system_extra=CINEMATIC_CHARTER)
        (run_dir / f"{artifact_name.split('.')[0]}.retry.raw.txt").write_text(
            raw, encoding="utf-8")
        artifact = extract_json_object(raw)
        problem = validate_stage_artifact(slug, artifact)
        if problem is not None:
            raise StageValidationError(
                f"Stage {slug!r} returned a degenerate artifact twice "
                f"({problem}). Aborting instead of filming an empty story. "
                f"Inspect {run_dir / artifact_name} and the .raw.txt traces."
            )
        return artifact, True

    # ------------------------------------------------------------------ #
    # Codegen / verify / render / repair                                  #
    # ------------------------------------------------------------------ #

    def _codegen(self, run_dir: Path, prompt: str, scene_spec: dict,
                 manifest: dict) -> tuple[Path, str]:
        started = time.time()
        if self.offline:
            code = _OFFLINE_SCENE
        else:
            dossier = {
                name: json.loads((run_dir / name).read_text(encoding="utf-8"))
                for _, _, name in STAGES if (run_dir / name).exists()
            }
            codegen_prompt = (
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
            raw = self._model(codegen_prompt, system_extra=CINEMATIC_CHARTER)
            (run_dir / "07_codegen.raw.txt").write_text(raw, encoding="utf-8")
            code = extract_python_block(raw)
        code_path = run_dir / "mythos_scene.py"
        code_path.write_text(code, encoding="utf-8")
        scene_name = find_scene_class(code)
        manifest["stages"].append(
            {"stage": "codegen", "artifact": "mythos_scene.py",
             "seconds": round(time.time() - started, 2)})
        self._write_manifest(run_dir, manifest)
        print(f"  [mythos] codegen          -> mythos_scene.py ({scene_name})")
        return code_path, scene_name

    @staticmethod
    def _verify(code_path: Path, *, prompt: str | None = None) -> tuple[bool, str | None]:
        try:
            py_compile.compile(str(code_path), doraise=True)
        except py_compile.PyCompileError as exc:
            return False, str(exc)
        code = code_path.read_text(encoding="utf-8")
        report = validate_manim_code_report(code)
        if not report.valid:
            return False, "; ".join(report.errors)
        for pattern, message in _LINT_RULES:
            if re.search(pattern, code):
                return False, f"charter lint: {message}"
        if prompt and _requires_light_art_direction(prompt):
            dark_background_patterns = [
                r"background_color\s*=\s*[\"']#0c0c0b[\"']",
                r"background_color\s*=\s*BLACK\b",
                r"\bBG\s*=\s*[\"']#0c0c0b[\"']",
            ]
            for pattern in dark_background_patterns:
                if re.search(pattern, code, flags=re.IGNORECASE):
                    return False, (
                        "prompt art-direction lint: this prompt explicitly "
                        "requires an archival/off-white, non-black background; "
                        "replace the default dark Mythos background with warm "
                        "paper and use dark ink text/geometry."
                    )
        return True, None

    @staticmethod
    def _record_validation(
        run_dir: Path,
        manifest: dict,
        code_path: Path,
        ok: bool,
        failure: str | None,
    ) -> None:
        source = code_path.read_text(encoding="utf-8") if code_path.is_file() else ""
        payload = validation_from_scene(source) if source else validation_template()
        write_json(run_dir / "validation.json", payload)
        manifest["static_check"] = {
            "passed": ok,
            "detail": failure[:2000] if failure else None,
        }
        status = dict(manifest.get("status") or {})
        status["validation"] = "complete" if ok else "failed"
        manifest["status"] = status

    def _render(self, code_path: Path, scene_name: str,
                quality: str) -> tuple[int, str]:
        run_dir = code_path.parent
        command = resolve_manim() + [
            f"-q{quality}", "--media_dir", str(run_dir / "media"),
            code_path.name, scene_name,
        ]
        print(f"  [mythos] rendering: {' '.join(command)}")
        return render_scene_file(
            run_dir,
            scene_file=code_path,
            scene_name=scene_name,
            quality=quality,
            timeout=self.render_timeout,
        )

    def _repair(self, run_dir: Path, code_path: Path, failure: str,
                attempt: int, manifest: dict) -> tuple[Path, str]:
        prompt = (
            "The Manim scene below failed. Repair it surgically: preserve the\n"
            "cinematic structure, class name, and Charter rules; fix only what is\n"
            "broken. Manim CE APIs only. Respond with exactly one fenced\n"
            "python block containing the COMPLETE corrected file.\n\n"
            f"CURRENT FILE:\n{code_path.read_text(encoding='utf-8')}\n\n"
            f"FAILURE OUTPUT (tail):\n{failure[-8000:]}"
        )
        raw = self._model(prompt, system_extra=CINEMATIC_CHARTER)
        (run_dir / f"repair_{attempt}.raw.txt").write_text(raw, encoding="utf-8")
        code = extract_python_block(raw)
        code_path.write_text(code, encoding="utf-8")
        manifest["stages"].append({"stage": f"repair_{attempt}",
                                   "artifact": code_path.name})
        self._write_manifest(run_dir, manifest)
        return code_path, find_scene_class(code)

    # ------------------------------------------------------------------ #
    # Bookkeeping                                                         #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _write_manifest(run_dir: Path, manifest: dict) -> None:
        migrated = migrate_manifest(manifest)
        manifest.clear()
        manifest.update(migrated)
        # Atomic: readers polling the run dir must never see a half-written
        # manifest (mid-write JSON parse errors were a real observed failure).
        # On Windows, os.replace onto a file a poller currently holds open
        # raises PermissionError — retry briefly, then fall back to a direct
        # write rather than killing the run over a progress file.
        payload = json.dumps(manifest, indent=2)
        target = run_dir / "manifest.json"
        tmp = run_dir / ".manifest.json.tmp"
        tmp.write_text(payload, encoding="utf-8")
        for attempt in range(8):
            try:
                os.replace(tmp, target)
                return
            except PermissionError:
                time.sleep(0.02 * (attempt + 1))
        target.write_text(payload, encoding="utf-8")
        tmp.unlink(missing_ok=True)

    def _create_run_dir(self, prompt: str) -> Path:
        slug = re.sub(r"[^a-z0-9]+", "-", prompt.lower()).strip("-")[:48] or "run"
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        run_dir = self.runs_dir / f"{stamp}-{slug}"
        run_dir.mkdir(parents=True, exist_ok=True)
        return run_dir


# ---------------------------------------------------------------------- #
# Offline mode                                                            #
# ---------------------------------------------------------------------- #

def _offline_artifact(slug: str, prompt: str, prior: dict) -> dict:
    """Deterministic stand-ins so the chain runs without a CLI login."""
    base = {"stage": slug, "topic": prompt, "offline": True,
            "prior_keys": sorted(prior)}
    if slug == "cinematographer":
        base["shots"] = [
            {"beat": 1, "move": "HEADLINE", "text": "A deterministic rehearsal."},
            {"beat": 2, "move": "ZOOM_IN", "target": "formula"},
            {"beat": 3, "move": "PULL_BACK"},
        ]
    if slug == "scene-composer":
        base["scene_name"] = "MythosOfflineScene"
    return base


_OFFLINE_SCENE = '''from manim import *


class MythosOfflineScene(ThreeDScene):
    """Offline rehearsal scene: proves the harness plumbing end to end."""

    def construct(self):
        self.camera.background_color = "#0c0c0b"
        self.set_camera_orientation(phi=0 * DEGREES, theta=-90 * DEGREES)
        title = Text("Mythos harness: offline rehearsal", font_size=40, color="#faf9f5")
        formula = MathTex(r"e^{i\\pi} + 1 = 0", font_size=64, color="#d97757")
        self.play(FadeIn(title))
        self.wait(0.6)
        self.play(title.animate.scale(0.5).to_edge(UP), FadeIn(formula))
        self.move_camera(frame_center=formula.get_center(), zoom=2.2, run_time=1.2)
        self.wait(0.6)
        self.move_camera(frame_center=ORIGIN, zoom=1.0, run_time=1.0)
        self.play(FadeOut(formula), FadeOut(title))
'''


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the Mythos 6-agent chain.")
    parser.add_argument("prompt", help="What should the film explain?")
    parser.add_argument("--render", action="store_true", help="Render after codegen")
    parser.add_argument("-q", "--quality", default="l", choices=list("lmhpk"))
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--command", default=DEFAULT_COMMAND,
                        help="Model backend: claude (default), fugu-api, "
                             "or another CLI executable")
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)
    parser.add_argument("--offline", action="store_true",
                        help="Deterministic artifacts; no CLI calls")
    parser.add_argument("--max-repairs", type=int, default=3)
    args = parser.parse_args(argv)

    harness = MythosHarness(command=args.command, model=args.model,
                            timeout=args.timeout, offline=args.offline)
    harness.run(args.prompt, render=args.render, quality=args.quality,
                max_repairs=args.max_repairs)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
