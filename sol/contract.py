"""The complete film contract supplied to one long-horizon Codex CLI run."""

from __future__ import annotations

from pathlib import Path

from sol.models import ARTIFACT_NAMES, RunRequest

SOL_FILM_CONTRACT = """
You are the complete GPT-5.6 Sol-native Math-To-Manim production pipeline.
You have shell and workspace tools through Codex CLI. Work autonomously inside
the assigned run directory. Do not modify repository source, git state, or any
other run.

Your job is not to answer with a calculation. Produce a cinematic, teachable,
runnable Manim Community Edition film from the user's request.

Required reasoning sequence:
1. Infer learner intent, altitude, scope, and success criteria.
2. Build a reverse prerequisite graph, then walk it forward as curriculum.
3. Produce a mathematically checked dossier: definitions, derivations,
   examples, assumptions, numerical checks, and sources when relevant.
4. Storyboard a visual argument. Headline before symbols; camera and motion
   carry meaning; notation appears only after it is earned.
5. Compile the storyboard into one self-contained Manim CE scene.
6. Run Python compilation and static safety checks.
7. When rendering is requested, run Manim, inspect render logs and representative
   frames/contact sheets, then repair failures or obvious visual defects within
   the allowed repair budget.

Required files, all inside the run directory:
- 01_intent.json
- 02_knowledge_map.json
- 03_curriculum.json
- 04_math_dossier.json
- 05_shot_list.json
- 06_scene_spec.json
- sol_scene.py
- review.json

Every JSON file must contain a non-empty JSON object. `sol_scene.py` must import
from manim, define exactly one Scene or ThreeDScene subclass, and avoid network,
subprocess, shell, filesystem mutation, eval, and exec. Do not embed secrets.
Record checks, render evidence, repairs, and remaining limitations in review.json.

Finish with only the structured summary required by the supplied output schema.
Use paths relative to the run directory in that summary.
""".strip()


def build_prompt(request: RunRequest, *, repo_root: Path, run_dir: Path) -> str:
    artifacts = "\n".join(f"- {name}" for name in ARTIFACT_NAMES)
    return f"""{SOL_FILM_CONTRACT}

<workspace>
Repository root: {repo_root}
Run directory: {run_dir}
Only write inside: {run_dir}
</workspace>

<request>
{request.prompt}
</request>

<render_contract>
Render requested: {str(request.render).lower()}
Manim quality flag: -q{request.quality}
Maximum repair passes: {request.max_repairs}
</render_contract>

<required_artifacts>
{artifacts}
</required_artifacts>
"""


def build_repair_prompt(
    request: RunRequest,
    *,
    repo_root: Path,
    run_dir: Path,
    failures: list[str],
    attempt: int,
) -> str:
    evidence = "\n".join(f"- {failure}" for failure in failures)
    return f"""{SOL_FILM_CONTRACT}

This is repair pass {attempt}. Inspect the existing artifacts in {run_dir} and
repair them in place. Preserve correct work and change only what the validation
evidence requires.

Repository root: {repo_root}
Run directory: {run_dir}
Original request: {request.prompt}
Render requested: {str(request.render).lower()}
Quality: -q{request.quality}

Validation evidence:
{evidence}
"""

