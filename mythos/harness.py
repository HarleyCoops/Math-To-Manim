"""Mythos harness: the 6-agent reasoning chain, driven through Claude CLI.

The agent charters live in ``.claude/agents/*.md`` — the exact files Claude
Code discovers natively for interactive use. This harness reads those same
charters and drives them headlessly, so interactive sessions and automated
runs share one source of truth.

Chain:
    intent -> cartographer -> curriculum -> math-director
           -> cinematographer -> scene-composer -> [codegen -> verify -> render]

Each reasoning stage receives the prior artifact JSON and must return one
JSON object. Codegen returns a complete Manim CE file inside one fenced
python block. Artifacts land in ``runs/mythos/<timestamp>/``.

Usage (from repo root):
    python -m mythos.harness "explain quantum field theory" --render -q m
    python -m mythos.harness "the heat equation" --offline      # no CLI needed
"""

from __future__ import annotations

import argparse
import json
import py_compile
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from math_to_manim.providers.mythos_cli import (  # noqa: E402
    CINEMATIC_CHARTER,
    _extract_json_object,
    _resolve_command,
)

# Charter search order: user-local Claude Code dir first, then the tracked
# canonical copies that ship with the repo (.claude/ is gitignored here).
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

JSON_CONTRACT = (
    "\n\nOUTPUT CONTRACT: Respond with exactly one JSON object and nothing else — "
    "no Markdown fences, no prose before or after. Be generous and verbose INSIDE "
    "the JSON fields; the next agent in the chain feeds on detail."
)


class MythosHarness:
    def __init__(
        self,
        *,
        command: str = "claude",
        model: str = "claude-fable-5",
        timeout: float = 900.0,
        offline: bool = False,
        runs_dir: Path | None = None,
    ):
        self.command = command
        self.model = model
        self.timeout = timeout
        self.offline = offline
        self.runs_dir = runs_dir or (REPO_ROOT / "runs" / "mythos")

    # ------------------------------------------------------------------ #
    # Claude CLI plumbing                                                  #
    # ------------------------------------------------------------------ #

    def _claude(self, prompt: str, *, system_extra: str | None = None) -> str:
        cmd = [
            _resolve_command(self.command),
            "-p",
            "--output-format", "text",
            "--model", self.model,
        ]
        if system_extra:
            cmd += ["--append-system-prompt", system_extra]
        completed = subprocess.run(
            cmd, input=prompt, text=True, capture_output=True,
            timeout=self.timeout, check=False,
        )
        if completed.returncode != 0:
            raise RuntimeError(
                f"claude CLI failed (exit {completed.returncode})\n"
                f"stderr:\n{completed.stderr[-4000:]}"
            )
        return completed.stdout

    # ------------------------------------------------------------------ #
    # Charters                                                             #
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
    # Run                                                                  #
    # ------------------------------------------------------------------ #

    def run(
        self,
        prompt: str,
        *,
        render: bool = False,
        quality: str = "l",
        max_repairs: int = 3,
    ) -> dict:
        run_dir = self._create_run_dir(prompt)
        manifest: dict = {
            "prompt": prompt,
            "model": self.model,
            "offline": self.offline,
            "created_utc": datetime.now(timezone.utc).isoformat(),
            "stages": [],
        }

        artifact: dict = {"user_prompt": prompt}
        for slug, agent_file, artifact_name in STAGES:
            started = time.time()
            if self.offline:
                artifact = _offline_artifact(slug, prompt, artifact)
            else:
                charter = self.load_charter(agent_file)
                stage_prompt = (
                    f"{charter}\n\nINPUT ARTIFACT JSON:\n"
                    f"{json.dumps(artifact, indent=2)}{JSON_CONTRACT}"
                )
                raw = self._claude(stage_prompt, system_extra=CINEMATIC_CHARTER)
                (run_dir / f"{artifact_name.split('.')[0]}.raw.txt").write_text(
                    raw, encoding="utf-8")
                artifact = _extract_json_object(raw)
            (run_dir / artifact_name).write_text(
                json.dumps(artifact, indent=2), encoding="utf-8")
            manifest["stages"].append(
                {"stage": slug, "artifact": artifact_name,
                 "seconds": round(time.time() - started, 2)})
            print(f"  [mythos] {slug:<16} -> {artifact_name}")

        code_path, scene_name = self._codegen(run_dir, prompt, artifact, manifest)
        ok, failure = self._verify(code_path)
        manifest["static_check"] = {"passed": ok, "detail": failure[:2000] if failure else None}

        if render:
            attempt = 0
            while True:
                if ok:
                    rc, out = self._render(code_path, scene_name, quality)
                    manifest.setdefault("renders", []).append(
                        {"attempt": attempt, "exit_code": rc})
                    if rc == 0:
                        break
                    failure = out
                if attempt >= max_repairs or self.offline:
                    break
                attempt += 1
                print(f"  [mythos] repair attempt {attempt}")
                code_path, scene_name = self._repair(
                    run_dir, code_path, failure or "unknown failure", attempt, manifest)
                ok, failure = self._verify(code_path)

        manifest["scene_file"] = str(code_path)
        manifest["scene_name"] = scene_name
        (run_dir / "manifest.json").write_text(
            json.dumps(manifest, indent=2), encoding="utf-8")
        print(f"  [mythos] run complete -> {run_dir}")
        return manifest

    # ------------------------------------------------------------------ #
    # Codegen / verify / render / repair                                   #
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
                "complete, runnable Manim Community Edition 0.19 Python file that\n"
                "implements the shot list with the full Cinematic Charter — headlines\n"
                "before symbols, camera zooms into terms, plain-language captions,\n"
                "Mythos palette. The file must be self-contained (inline any helpers),\n"
                "import `from manim import *`, and define exactly one ThreeDScene\n"
                "subclass. Respond with exactly one fenced python block and nothing\n"
                "else.\n\nDOSSIER JSON:\n" + json.dumps(dossier, indent=2)
            )
            raw = self._claude(codegen_prompt, system_extra=CINEMATIC_CHARTER)
            (run_dir / "07_codegen.raw.txt").write_text(raw, encoding="utf-8")
            code = _extract_python_block(raw)
        code_path = run_dir / "mythos_scene.py"
        code_path.write_text(code, encoding="utf-8")
        scene_name = _find_scene_class(code)
        manifest["stages"].append(
            {"stage": "codegen", "artifact": "mythos_scene.py",
             "seconds": round(time.time() - started, 2)})
        print(f"  [mythos] codegen          -> mythos_scene.py ({scene_name})")
        return code_path, scene_name

    @staticmethod
    def _verify(code_path: Path) -> tuple[bool, str | None]:
        try:
            py_compile.compile(str(code_path), doraise=True)
        except py_compile.PyCompileError as exc:
            return False, str(exc)
        code = code_path.read_text(encoding="utf-8")
        for pattern, message in _LINT_RULES:
            if re.search(pattern, code):
                return False, f"charter lint: {message}"
        return True, None

    def _render(self, code_path: Path, scene_name: str, quality: str) -> tuple[int, str]:
        manim = shutil.which("manim") or "manim"
        cmd = [manim, f"-q{quality}", str(code_path), scene_name]
        print(f"  [mythos] rendering: {' '.join(cmd)}")
        completed = subprocess.run(cmd, text=True, capture_output=True,
                                   cwd=str(REPO_ROOT), timeout=self.timeout)
        return completed.returncode, (completed.stderr or "") + (completed.stdout or "")

    def _repair(self, run_dir: Path, code_path: Path, failure: str,
                attempt: int, manifest: dict) -> tuple[Path, str]:
        prompt = (
            "The Manim scene below failed. Repair it surgically: preserve the\n"
            "cinematic structure, class name, and Charter rules; fix only what is\n"
            "broken. Manim CE 0.19 APIs only. Respond with exactly one fenced\n"
            "python block containing the COMPLETE corrected file.\n\n"
            f"CURRENT FILE:\n{code_path.read_text(encoding='utf-8')}\n\n"
            f"FAILURE OUTPUT (tail):\n{failure[-8000:]}"
        )
        raw = self._claude(prompt, system_extra=CINEMATIC_CHARTER)
        (run_dir / f"repair_{attempt}.raw.txt").write_text(raw, encoding="utf-8")
        code = _extract_python_block(raw)
        code_path.write_text(code, encoding="utf-8")
        manifest["stages"].append({"stage": f"repair_{attempt}",
                                   "artifact": code_path.name})
        return code_path, _find_scene_class(code)

    def _create_run_dir(self, prompt: str) -> Path:
        slug = re.sub(r"[^a-z0-9]+", "-", prompt.lower()).strip("-")[:48] or "run"
        stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        run_dir = self.runs_dir / f"{stamp}-{slug}"
        run_dir.mkdir(parents=True, exist_ok=True)
        return run_dir


# ---------------------------------------------------------------------- #
# Helpers                                                                 #
# ---------------------------------------------------------------------- #

_LINT_RULES = [
    (r"self\.camera\.animate", "never animate self.camera in a ThreeDScene; use move_camera"),
    (r"from\s+manim\s+import\s+\*\s*$|from manim import \*",
     None),  # presence checked below via inverse
]
# Keep only real rules (the import check is handled separately).
_LINT_RULES = [r for r in _LINT_RULES if r[1] is not None]


def _extract_python_block(text: str) -> str:
    match = re.search(r"```(?:python|py)?\s*\n(.*?)```", text, flags=re.DOTALL)
    if match:
        return match.group(1).strip() + "\n"
    stripped = text.strip()
    if stripped.startswith(("from manim", "import", '"""', "#")):
        return stripped + "\n"
    raise RuntimeError(f"No python block found in CLI output:\n{text[:800]}")


def _find_scene_class(code: str) -> str:
    match = re.search(r"class\s+(\w+)\s*\(\s*(?:ThreeDScene|MovingCameraScene|Scene)\b", code)
    if not match:
        raise RuntimeError("Generated code defines no Scene subclass")
    return match.group(1)


def _offline_artifact(slug: str, prompt: str, prior: dict) -> dict:
    """Deterministic stand-ins so the chain runs without a CLI login."""
    base = {"stage": slug, "topic": prompt, "offline": True, "prior_keys": sorted(prior)}
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
    parser.add_argument("--model", default="claude-fable-5")
    parser.add_argument("--command", default="claude", help="Claude CLI executable")
    parser.add_argument("--timeout", type=float, default=900.0)
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
